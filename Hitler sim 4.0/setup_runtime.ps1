param(
    [string]$PythonVersion = "3.11.8",
    [string]$RuntimeDir = "runtime",
    [string]$PythonSha256 = ""
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path $RuntimeDir)) {
    New-Item -ItemType Directory -Path $RuntimeDir | Out-Null
}

$pythonExe = Join-Path $RuntimeDir 'python.exe'
$needsRuntime = $true
if (Test-Path $pythonExe) {
    try {
        $versionOutput = & $pythonExe --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $versionOutput) {
            $installedVersion = ($versionOutput -replace '^Python\s+', '').Trim()
            if ($installedVersion -eq $PythonVersion) {
                $needsRuntime = $false
            } else {
                Write-Host "Existing runtime version $installedVersion does not match requested $PythonVersion. Reinstalling..."
            }
        } else {
            Write-Host "Unable to determine current Python runtime version. Reinstalling..."
        }
    } catch {
        Write-Host "Failed to query python.exe for version. Reinstalling..."
    }
}

if ($needsRuntime) {
    if (Test-Path $RuntimeDir) {
        Get-ChildItem -Path $RuntimeDir -Force | Remove-Item -Recurse -Force
    } else {
        New-Item -ItemType Directory -Path $RuntimeDir | Out-Null
    }

    $zipName = "python-$PythonVersion-embed-amd64.zip"
    $zipPath = Join-Path $RuntimeDir $zipName
    $pythonUrl = "https://www.python.org/ftp/python/$PythonVersion/$zipName"

    Write-Host "Downloading embeddable Python $PythonVersion..."
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $zipPath -UseBasicParsing -ErrorAction Stop
    } catch {
        throw "Failed to download Python runtime from $pythonUrl. $_"
    }

    if ($PythonSha256) {
        $downloadHash = (Get-FileHash $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($downloadHash -ne $PythonSha256.ToLowerInvariant()) {
            Remove-Item $zipPath -Force
            throw "SHA256 mismatch for Python runtime. Expected $PythonSha256 but got $downloadHash."
        }
    }

    Write-Host "Extracting runtime..."
    Expand-Archive -LiteralPath $zipPath -DestinationPath $RuntimeDir -Force
    Remove-Item $zipPath

    if (-not (Test-Path $pythonExe)) {
        $nested = Get-ChildItem $RuntimeDir -Directory | Select-Object -First 1
        if ($nested) {
            Get-ChildItem $nested.FullName | Move-Item -Destination $RuntimeDir -Force
            Remove-Item $nested.FullName -Recurse -Force
        }
    }
} else {
    Write-Host "Python runtime already present."
}

$pthFile = Get-ChildItem $RuntimeDir -Filter "python*._pth" | Select-Object -First 1
if (-not $pthFile) {
    throw "Could not find python._pth file in runtime."
}

$content = Get-Content $pthFile.FullName
if ($content -notcontains "import site") {
    $content = $content | ForEach-Object {
        if ($_ -match '#import site') { 'import site' } else { $_ }
    }
    if ($content -notcontains 'import site') {
        $content += 'import site'
    }
    Set-Content $pthFile.FullName $content -Encoding ASCII
}

$python = Join-Path $RuntimeDir 'python.exe'
$requirements = Join-Path $root 'requirements.txt'
$requirementsHashPath = Join-Path $RuntimeDir 'requirements.sha256'
if (-not (Test-Path $requirements)) {
    throw "Missing requirements file at $requirements. Create it or provide the correct path."
}
$currentHash = (Get-FileHash $requirements -Algorithm SHA256).Hash
$storedHash = $null
if (Test-Path $requirementsHashPath) {
    $storedHash = (Get-Content $requirementsHashPath).Trim()
}

function Ensure-Pip {
    param($PythonExe)

    $pipAvailable = $false
    try {
        & $PythonExe -m pip --version *> $null
        if ($LASTEXITCODE -eq 0) {
            $pipAvailable = $true
        }
    } catch {
        $pipAvailable = $false
    }

    if ($pipAvailable) {
        return
    }

    $getPip = Join-Path (Split-Path $PythonExe -Parent) 'get-pip.py'
    Write-Host "Installing pip..."
    try {
        Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile $getPip -UseBasicParsing -ErrorAction Stop
    } catch {
        throw "Failed to download get-pip.py. $_"
    }

    & $PythonExe $getPip
    if ($LASTEXITCODE -ne 0) {
        throw "pip bootstrap script failed."
    }
    Remove-Item $getPip -Force
}

Ensure-Pip -PythonExe $python

$needsDeps = $needsRuntime -or ($storedHash -ne $currentHash)
if ($needsDeps) {
    Write-Host "Installing Python dependencies..."
    & $python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade pip inside runtime."
    }

    & $python -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies listed in requirements.txt."
    }

    Set-Content $requirementsHashPath $currentHash -Encoding ASCII
} else {
    Write-Host "Python dependencies already up to date."
}

Write-Host "Runtime ready."

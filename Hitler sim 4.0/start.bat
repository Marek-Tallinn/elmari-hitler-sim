@echo off
setlocal
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "PYTHON_EXE=%RUNTIME%\python.exe"
set "LAUNCHER=%ROOT%launch_game.py"

powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%setup_runtime.ps1"
if errorlevel 1 (
    echo Failed to set up the runtime. See messages above.
    exit /b 1
)

"%PYTHON_EXE%" "%LAUNCHER%"
endlocal

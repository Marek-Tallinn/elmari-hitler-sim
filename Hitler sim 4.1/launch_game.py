import os
import runpy
import sys


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)
    target = os.path.join(root, "game.py")
    runpy.run_path(target, run_name="__main__")


if __name__ == "__main__":
    main()


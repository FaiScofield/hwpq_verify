#!/usr/bin/env python3
"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : build_verify_csc_ui.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-04
Description : Build script for the verify_csc_ui Windows package
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Build the CSC UI executable with PyInstaller."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    entry_script = script_dir / "run_csc_ui.py"
    font_path = repo_root / "data" / "fonts" / "NotoSans-Regular.ttf"
    pyinstaller_work_dir = repo_root / "output" / "pyinstaller"
    separator = ";" if sys.platform.startswith("win") else ":"
    add_data_arg = f"{font_path}{separator}assets/fonts"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name",
        "verify_csc_ui",
        "--specpath",
        str(pyinstaller_work_dir),
        "--add-data",
        add_data_arg,
        str(entry_script),
    ]

    subprocess.run(cmd, check=True, cwd=repo_root)


if __name__ == "__main__":
    main()

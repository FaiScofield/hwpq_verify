#!/usr/bin/env python3
"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : run_csc_ui.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-04
Description : GUI-only launcher for the CSC tool
"""

import sys

from run_csc import main


def ensure_ui_flag(argv):
    """Ensure the CSC UI launcher always starts the GUI mode."""
    if "--ui" not in argv:
        argv.append("--ui")
    return argv


if __name__ == "__main__":
    ensure_ui_flag(sys.argv)
    main()
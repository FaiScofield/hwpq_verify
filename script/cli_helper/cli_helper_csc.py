'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_csc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-22
Description :
LastEditTime: 2025-08-14
'''

import os
import sys
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper import ModuleHelperCore
from config_def import ModuleConfigCore, CscConfig
from reg_def import ModuleRegisterCore, CscRegister


class CscHelper(ModuleHelperCore):
    def __init__(self, name: str = "CSC", platform: str = 'RK3572', parent: Optional[ModuleHelperCore] = None):
        super().__init__(name, platform, parent)

    ## =============== overwrite methods  ===============
    def update_attributes(self, platform: str) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        self.platform = platform.upper()
        self.config = CscConfig(self.name, self.platform)
        self.register = CscRegister(self.name, self.platform)
        return self.config, self.register


if __name__ == "__main__":
    platform = "RK3572"
    if len(sys.argv) > 1:
        platform = sys.argv[1].upper()
    runner = CscHelper(platform=platform)
    runner.run()

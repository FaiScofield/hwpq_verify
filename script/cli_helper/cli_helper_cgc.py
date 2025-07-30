'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_cgc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-30
Description :
LastEditTime: 2025-07-30
'''

import os
import sys
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper import ModuleHelperCore
from config_def import ModuleConfigCore, CgcConfig
from reg_def import ModuleRegisterCore, CgcRegister


class CgcHelper(ModuleHelperCore):
    def __init__(self, name: str = "CGC", platform: str = 'RK3572', parent: Optional[ModuleHelperCore] = None):
        super().__init__(name, platform, parent)

    ## =============== overwrite methods  ===============
    def define_config_and_regs(self) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        self.config = CgcConfig(self.name)
        self.register = CgcRegister(self.name, self.platform)
        return self.config, self.register


if __name__ == "__main__":
    runner = CgcHelper()
    runner.run()

'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_acm.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-25
'''

import os
import sys
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper import ModuleHelperCore
from config_def import ModuleConfigCore, AcmConfig
from reg_def import ModuleRegisterCore, AcmRegister


class AcmHelper(ModuleHelperCore):
    def __init__(self, name: str = "ACM", platform: str = 'RK3572', parent: Optional[ModuleHelperCore] = None):
        super().__init__(name, platform, parent)

    ## =============== overwrite methods  ===============
    def define_config_and_regs(self) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        self.config = AcmConfig(self.name)
        self.register = AcmRegister(self.name, self.platform)
        return self.config, self.register


if __name__ == "__main__":
    runner = AcmHelper()
    runner.run()

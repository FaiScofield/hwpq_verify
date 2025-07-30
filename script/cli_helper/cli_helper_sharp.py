'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_sharp.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-25
'''

import os
import sys
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper.cli_helper_core import ModuleHelperCore
from config_def import ModuleConfigCore, SharpLiteConfig
from reg_def import ModuleRegisterCore, SharpRegister


class SharpHelper(ModuleHelperCore):
    def __init__(self, name: str = "SHARP", platform: str = 'RK3572', parent: Optional[ModuleHelperCore] = None):
        if platform.upper() == 'RK3572':
            name = 'SHARP_LITE'
        super().__init__(name, platform, parent)

    ## =============== overwrite methods  ===============
    def define_config_and_regs(self) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        # if self.platform == 'RK3572':
        self.config = SharpLiteConfig(self.name)
        self.register = SharpRegister(self.name, self.platform)
        return self.config, self.register


if __name__ == "__main__":
    runner = SharpHelper()
    runner.run()

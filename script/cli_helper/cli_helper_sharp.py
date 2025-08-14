'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_sharp.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-08-14
'''

import os
import sys
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper.cli_helper_core import ModuleHelperCore
from config_def import ModuleConfigCore, SharpLiteConfig, SharpConfig
from reg_def import ModuleRegisterCore, SharpRegister


class SharpHelper(ModuleHelperCore):
    def __init__(self, name: str = "SHARP", platform: str = 'RK3572', parent: Optional[ModuleHelperCore] = None):
        if platform.upper() == 'RK3572':
            name = 'SHARP_LITE'
        super().__init__(name, platform, parent)

    ## =============== overwrite methods  ===============
    def update_attributes(self, platform: str) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        self.platform = platform.upper()
        self.name = 'SHARP_LITE' if platform.upper() == 'RK3572' else 'SHARP'
        if self.platform == 'RK3572':
            self.config = SharpLiteConfig(self.name, self.platform)
            self.register = SharpRegister(self.name, self.platform)
        else:
            self.config = SharpConfig(self.name, self.platform)
            self.register = SharpRegister(self.name, self.platform)
        return self.config, self.register


if __name__ == "__main__":
    platform = "RK3572"
    if len(sys.argv) > 1:
        platform = sys.argv[1].upper()
    runner = SharpHelper(platform=platform)
    runner.run()

'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_sharp.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-11
'''

import os
import sys
from typing import Optional, Dict, Any, List, Type
from ctypes import Structure, c_uint

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper.cli_helper_core import ModuleHelper
from config_def.module_config_sharp_lite import SharpLiteConfig
from reg_def.module_reg_sharp_lite import SharpLiteRegisters


class SharpHelper(ModuleHelper):
    def __init__(self, name: str = "SHARP", platform: str = 'RK3572', parent: Optional['ModuleHelper'] = None):
        if platform.upper() == 'RK3572':
            name = 'SHARP_LITE'
        super().__init__(name, platform, parent)
        # self.define_config_and_regs()

    ## =============== overwrite methods  ===============
    def define_config_and_regs(self):
        # if self.platform == 'RK3572':
        self.config = SharpLiteConfig(self.name)
        self.register = SharpLiteRegisters(self.name, self.platform)
        return self.config, self.register

if __name__ == "__main__":
    runner = SharpHelper()
    runner.run()
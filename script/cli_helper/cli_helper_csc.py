'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_csc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-22
Description :
LastEditTime: 2025-07-22
'''

import os
import sys
from typing import Optional, Dict, Any, List, Type

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper import ModuleHelperCore
from config_def import CscConfig
from reg_def import CscRegister


class CscHelper(ModuleHelperCore):
    def __init__(self, name: str = "CSC", platform: str = 'RK3572', parent: Optional['ModuleHelperCore'] = None):
        super().__init__(name, platform, parent)
        # self.define_config_and_regs()

        ## 增加额外的命令
        # self.add_command('opt', self.do_optimize, "<level>", "执行图像优化处理")

    ## =============== overwrite methods  ===============
    def define_config_and_regs(self):
        self.config = CscConfig(self.name)
        self.register = CscRegister(self.name, self.platform)
        return self.config, self.register


if __name__ == "__main__":
    runner = CscHelper()
    runner.run()

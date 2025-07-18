'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_acm.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description : 
LastEditTime: 2025-07-18
'''

import os
import sys
from typing import Optional, Dict, Any, List, Type

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper.cli_helper_core import ModuleHelper
# from config_def.module_config_acm import AcmConfig

class AcmHelper(ModuleHelper):
    def __init__(self, name: str = "ACM", platform: str = 'RK3572', parent: Optional['ModuleHelper'] = None):
        super().__init__(name, platform, parent)
        # self.define_config_and_regs()

        ## 增加额外的命令
        # self.add_command('opt', self.do_optimize, "<level>", "执行图像优化处理")


    ## =============== overwrite methods  ===============
    def define_config_and_regs(self):
        self.config = None
        self.register = None
        return self.config, self.register


if __name__ == "__main__":
    runner = AcmHelper()
    runner.run()
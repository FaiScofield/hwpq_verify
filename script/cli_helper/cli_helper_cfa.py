"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_cfa.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description : 
LastEditTime: 2025-07-07
"""

import os
import sys
from tqdm import tqdm
from typing import Optional, Dict, Any, List, Type

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper.cli_helper_core import ModuleHelper
from config_def.module_config_cfa import CfaConfig


class CfaHelper(ModuleHelper):
    def __init__(
        self,
        name: str = "CFA",
        platform: str = "RK3572",
        parent: Optional["ModuleHelper"] = None,
    ):
        super().__init__(name, platform, parent)
        self.config = self.define_config()

        ## 增加额外的命令
        # self.add_command('opt', self.do_optimize, "<level>", "执行图像优化处理")

    ## =============== overwrite methods  ===============
    def define_config(self):
        return CfaConfig(self.name)

    def config_to_registers(self) -> int:
        # TODO
        pass

    def get_param(self, param_name: str) -> Any:
        # TODO
        pass

    def set_param(self, param_name: str, value: Any) -> bool:
        # TODO
        pass


if __name__ == "__main__":
    runner = CfaHelper()
    runner.run()

"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_cfa.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description :
LastEditTime: 2025-07-11
"""

import os
import sys
from tqdm import tqdm
from typing import Optional, Dict, Any, List, Type

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper.cli_helper_core import ModuleHelperCore
from config_def.module_config_cfa import CfaConfig


class CfaHelper(ModuleHelperCore):
    def __init__(
        self,
        name: str = "CFA",
        platform: str = "RK3572",
        parent: Optional["ModuleHelperCore"] = None,
    ):
        super().__init__(name, platform, parent)
        # self.define_config_and_regs()

    ## =============== overwrite methods  ===============
    def define_config_and_regs(self):
        self.config = CfaConfig(self.name)
        self.register = None
        return self.config, self.register


if __name__ == "__main__":
    runner = CfaHelper()
    runner.run()

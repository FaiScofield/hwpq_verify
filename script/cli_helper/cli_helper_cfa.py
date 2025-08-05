"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_cfa.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description :
LastEditTime: 2025-08-05
"""

import os
import sys
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper.cli_helper_core import ModuleHelperCore
from config_def import ModuleConfigCore, CfaConfig
from reg_def import ModuleRegisterCore  # ,CfaRegister


class CfaHelper(ModuleHelperCore):
    def __init__(self, name: str = "CFA", platform: str = "RK3572", parent: Optional[ModuleHelperCore] = None):
        super().__init__(name, platform, parent)

    ## =============== overwrite methods  ===============
    def update_attributes(self, platform: str) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        self.platform = platform.upper()
        self.config = CfaConfig(self.name)
        self.register = None
        return self.config, self.register


if __name__ == "__main__":
    runner = CfaHelper()
    runner.run()

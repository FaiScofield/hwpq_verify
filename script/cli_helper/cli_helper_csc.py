'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_csc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-22
Description :
LastEditTime: 2025-10-14
'''

import os
import sys
import copy
import numpy as np
from ast import literal_eval
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from cli_helper import ModuleHelperCore
from config_def import ModuleConfigCore, CscConfig
from reg_def import ModuleRegisterCore, CscRegister


class CscHelper(ModuleHelperCore):
    def __init__(self, name: str = "CSC", platform: str = 'RK3572', parent: Optional[ModuleHelperCore] = None):
        super().__init__(name, platform, parent)

    ## =============== overwrite methods  ===============
    def update_attributes(self, platform: str) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        self.platform = platform.upper()
        self.config = CscConfig(self.name, self.platform)
        self.register = CscRegister(self.name, self.platform)
        return self.config, self.register

    def do_set(self, args: list[str]) -> bool:
        if not args:
            print(f"[{self.name}] 错误: 参数设置格式应为 <param1>=<value1> [param2=<value2> ...]")
            return False  # 不退出

        valid_args = args.copy()
        for part in args:
            if not self.check_attr_str_validate(part, True):
                print(f"[{self.name}] 忽略错误的参数格式: {part}")
                valid_args.remove(part)
        if len(valid_args) == 0:
            print(f"[{self.name}] 错误: 参数设置格式应为 <param1>=<value1> [param2=<value2> ...]")
            return False  # 不退出

        if self.register is not None:
            self.register.config = copy.deepcopy(self.config)
            self.register.config2regs()
            old_regs = copy.deepcopy(self.register.regs)  # list[Reg]
            # self.register.dump()

        for part in valid_args:
            full_key, value = part.split('=')
            obj = self.config

            ## 检查嵌套属性是否存在
            if '.' in full_key:
                keys = full_key.split('.')
                b_valid_key = True
                for key in keys[0:-1]:
                    if not hasattr(obj, key):
                        print(f"[{self.name}] invalid param name: \'{full_key}\'! use \'dump\' to check all params.")
                        b_valid_key = False
                        break
                    obj = getattr(obj, key)  # 最内层子配置
                if b_valid_key:
                    key = keys[-1]
                else:
                    continue
            else:
                key = full_key

            ## 对最内层子配置的属性设置值
            if hasattr(obj, key):
                if type(getattr(obj, key)) not in (bool, int, float, str, list[int], np.ndarray):
                    print(f"[{self.name}] ignore to set param \'{part}\' since it is an object!")
                    continue

                if self.config.cscPassthrough and key not in ['cscPassthrough', 'cscMatrix', 'cscVector']:
                    print(f"[{self.name}] param \'{full_key}\' no changed since cscPassthrough = 1!")
                    continue
                elif not self.config.cscPassthrough and key in ['cscPassthrough', 'cscMatrix', 'cscVector']:
                    print(f"[{self.name}] param \'{full_key}\' no changed since cscPassthrough = 0!")
                    continue

                value = value.strip()
                if value.startswith('[') and value.endswith(']'):
                    try:
                        value = literal_eval(value)  # 安全转换为Python对象
                    except:
                        value = [x.strip() for x in value[1:-1].split(',')]
                    array_obj = getattr(obj, key)
                    for i, x in enumerate(value):
                        array_obj[i] = x
                else:
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    setattr(obj, key, value)

                print(f"[{self.name}] set param \'{full_key}\' value: {value}")
            else:
                print(f"[{self.name}] invalid param name: \'{full_key}\'! use \'dump\' to check all params.")

        ## update csc coefs
        self.config.update_csc_coefs()

        ## update registers
        if self.register is not None:
            self.register.config = copy.deepcopy(self.config)
            self.register.config2regs()
            new_regs = copy.deepcopy(self.register.regs)
            # self.register.dump()
            cnt_changed = 0
            for old, new in zip(old_regs, new_regs):
                assert old.name == new.name and old.offset == new.offset
                if old.value != new.value:
                    print(
                        "[%s] register 0x%08X changed: 0x%08X ==> 0x%08X"
                        % (self.name, old.offset, old.value.astype(np.uint32), new.value.astype(np.uint32))
                    )
                    cnt_changed += 1
            if cnt_changed == 0:
                print(f"[{self.name}] the value of no register has changed!")

        return False  # 不退出


if __name__ == "__main__":
    platform = "RK3572"
    if len(sys.argv) > 1:
        platform = sys.argv[1].upper()
    runner = CscHelper(platform=platform)
    runner.run()

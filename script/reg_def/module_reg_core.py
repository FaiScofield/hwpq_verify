"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_reg_core.py
Description : 
Author      : vance.wu@rock-chips.com
Date        : 2025-07-11
LastEditTime: 2025-07-17
"""

from abc import ABC, abstractmethod


class ModuleRegisterCore(ABC):
    def __init__(self, name: str, platform: str = "RK3572"):
        self.name = name.upper()
        self.platform = platform
        self.valid = False

    @abstractmethod
    def dump(self, filename: str = "", align: int = 4, **kwargs):
        return False

    @abstractmethod
    def load(self, filename, **kwargs):
        return False

    @abstractmethod
    def check(self, **kwargs):
        return False

    def format_regs_dict(
        self, regs: dict[str:[hex, hex]], align: int = 4, address_offset: int = 0, joint_lines: bool = True
    ):
        """
        format string for regs = {name: [offset, value]} with number align registers, like:
        0x00000000: 0x00000001 0x000000FF 0x0FCD0008 0x00000000
        0x00000004: 0x00000000 0x00000000 ---------- 0x00000000
        """
        if align < 1 or len(regs) == 0:
            return None

        offset_value_list = regs.values()
        offset_value_dict = {k: v for k, v in offset_value_list}

        key_st = min(offset_value_dict.keys())
        key_ed = max(offset_value_dict.keys())
        lines = []

        while key_st <= key_ed:
            valid_line = False
            line = "0x%08X:" % (key_st + address_offset)
            for j in range(align):
                key = key_st + j * 4
                if key in offset_value_dict:
                    line += " 0x%08X" % offset_value_dict[key]
                    valid_line = True
                else:
                    line += " ----------"
            if valid_line:
                lines.append(line)
            key_st += align * 4

        return "\n".join(lines) if joint_lines else lines

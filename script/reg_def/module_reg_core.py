"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_reg_core.py
Description :
Author      : vance.wu@rock-chips.com
Date        : 2025-07-11
LastEditTime: 2025-07-17
"""

from abc import ABC, abstractmethod


class Reg:
    def __init__(self, offset: int, value: int, name: str = ""):
        self.offset = offset
        self.value = value
        self.name = name

    def __iter__(self):
        return iter((self.offset, self.value, self.name))


class ModuleRegisterCore(ABC):
    def __init__(self, name: str, platform: str = "RK3572"):
        self.name = name.upper()
        self.platform = platform
        self.regs = [Reg(0, 0)]

    @abstractmethod
    def dump(self, filename: str = "", align: int = 4, **kwargs) -> bool:
        return False

    @abstractmethod
    def load(self, filename, **kwargs) -> bool:
        return False

    @abstractmethod
    def update(self, **kwargs) -> bool:
        return False

    def set(self, value: int, index: int = None, name: str = None, offset: int = None) -> bool:
        ret = False
        for i in range(len(self.regs)):
            if (
                (index is not None and i == index)
                or (name is not None and self.regs[i].name == name)
                or (offset is not None and self.regs[i].offset == offset)
            ):
                self.regs[i].value = value
                ret = True
                break
            else:
                continue
        return ret

    def get(self, index: int = None, name: str = None, offset: int = None) -> int or None:
        if index is not None:
            if index >=0 and index < len(self.regs):
                return self.regs[index].value
        else:
            for reg in self.regs:
                if name is not None and name == reg.name:
                    return reg.value
                if offset is not None and offset == reg.offset:
                    return reg.value
        return None

    def format_regs_dict(
        self, regs: list[Reg], align: int = 4, base_address: int = 0, joint_lines: bool = True
    ) -> str or list[str]:
        """
        format string for regs with number align registers, like:
        0x00000000: 0x00000001 0x000000FF 0x0FCD0008 0x00000000
        0x00000004: 0x00000000 0x00000000 ---------- 0x00000000
        """
        if align < 1 or len(regs) == 0:
            return None

        offsets = [o for o, v, n in regs]
        offset_value_dict = {o: v for o, v, _ in regs}

        key_st = min(offsets)
        key_ed = max(offsets)
        lines = []

        while key_st <= key_ed:
            valid_line = False
            line = "0x%08X:" % (key_st + base_address)
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

"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_reg_core.py
Description :
Author      : vance.wu@rock-chips.com
Date        : 2025-07-11
LastEditTime: 2025-08-06
"""

import os
import sys
import re
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Union
from enum import Enum

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def import ModuleConfigCore
from utils import setup_logger

# class RegMask(Enum):
RM1 = 0x01
RM2 = 0x03
RM3 = 0x07
RM4 = 0x0F
RM5 = 0x1F
RM6 = 0x3F
RM7 = 0x7F
RM8 = 0xFF
RM9 = 0x1FF
RM10 = 0x3FF
RM11 = 0x7FF
RM12 = 0xFFF
RM13 = 0x1FFF
RM14 = 0x3FFF
RM15 = 0x7FFF
RM16 = 0xFFFF
RM20 = 0xFFFFF
RM24 = 0xFFFFFF
RM32 = 0xFFFFFFFF


class Reg:
    def __init__(self, offset: int, value: int, name: str = ""):
        self.offset = offset
        self.value = np.uint32(value) if value >= 0 else np.uint32(2**32 + value)
        self.name = name

        self.base_addr = 0x0

    def __iter__(self):
        return iter((self.offset, self.value, self.name))


class ModuleRegisterCore(ABC):
    def __init__(self, name: str, platform: str = "RK3572"):
        self.name = name.upper()
        self.platform = platform
        self.logger = setup_logger(self.name)

        # below attributes should be set by subclass
        self.base_addr = 0x0
        self.regs = []
        self.nb_regs = 0
        self.config: Optional[ModuleConfigCore] = None

    ## =============== abstract methods  ===============
    @abstractmethod
    def update(self, **kwargs) -> bool:
        return self.check_regs()

    @abstractmethod
    def config2regs(self) -> bool:
        return False

    @abstractmethod
    def regs2config(self) -> bool:
        return False

    ## =============== common methods  ===============
    def dump(self, filename: str = "", align: int = 4, pretty_lines_stdout: int = 16, **kwargs) -> bool:
        """
        @param: filename - 输出文件名，如果为空则输出到控制台
        @param: align - 格式化输出每行的对齐寄存器数
        @param: pretty_lines_stdout - 当输出到控制台时的最大行数，省略中间部分行输出，<=0时表示不限制
        """
        if "regs" in kwargs:
            regs = kwargs["regs"]
        else:
            regs = self.regs

        if filename == None or filename == "":
            self.logger.info(f"dump {self.platform} registers below:")
            data = self.format_str_regs_array(regs, align, self.base_addr, False, pretty_lines_stdout)
            if data == "":
                return False
            for line in data:
                self.logger.info(line)
            return True

        self.logger.info(f"dump {self.platform} registers (nb={len(regs)}) to {filename} ...")

        if filename.endswith(".txt") or filename.endswith(".dat"):
            with open(filename, "w") as f:
                data = self.format_str_regs_array(regs, align, self.base_addr, True, 0)
                if data != "":
                    f.write(data)
                    return True
        elif filename.endswith(".bin"):
            data = np.array([val for _, val, _ in regs], dtype=np.uint32)
            data.tofile(filename)
            return True
        return False

    def load(self, filename, **kwargs) -> bool:
        self.logger.info(f"loading {self.platform} registers from {filename} ...")
        if filename.endswith(".txt") or filename.endswith(".dat"):
            valid_regs_val_pairs = []  # [offset, value]
            with open(filename, "rt") as f:
                for _, line in enumerate(f):
                    pair = self.parse_str_regs_array(line)
                    if pair is not None:
                        valid_regs_val_pairs += pair
                    else:
                        continue
            for pos, val in valid_regs_val_pairs:
                pos_ok = False
                for i in range(len(self.regs)):
                    if pos == self.regs[i].offset or pos == self.regs[i].offset + self.base_addr:
                        self.regs[i].value = val
                        pos_ok = True
                        break
                if not pos_ok:
                    self.logger.warning("offset=0x%08X is not a valid register!" % pos)
            return self.dump()
        elif filename.endswith(".bin"):
            data = np.fromfile(filename, dtype=np.uint32)
            if len(data) < len(self.regs):
                self.logger.error(
                    f"not enough register data in {filename}! require {len(self.regs)} registers, but only get {len(data)}!"
                )
                return False
            for i in range(len(self.regs)):
                self.regs[i].value = np.uint32(data[i])
            # if self.config is not None:
            #     self.regs2config()
            #     self.config.dump()
            return self.dump(**kwargs)
        elif filename.endswith(".json"):
            if self.config is not None:
                ok = self.config.load(filename)
                ok |= self.config2regs()
                # self.config.dump()
                ok |= self.dump(**kwargs)
                return ok
            else:
                self.logger.error(f"{filename} is not supported since the config handler is not set!")
        else:
            self.logger.error(f"{filename} is not supported!")

        return False

    def gen(self, seed=114514, **kwargs) -> bool:
        if self.config is not None:
            ok = self.config.gen(seed, **kwargs)
            # self.config.dump()
            ok &= self.config2regs()
            return ok
        else:
            self.logger.error(f"failed to run gen(), since the config handler is not set!")
            return False

    def set(self, value, index: Optional[int] = None, name: Optional[str] = None, offset: Optional[int] = None) -> bool:
        ret = False
        # if type is None:
        #     type = np.uint32
        for i in range(len(self.regs)):
            if (
                (index is not None and i == index)
                or (name is not None and self.regs[i].name == name)
                or (offset is not None and self.regs[i].offset == offset)
            ):
                self.regs[i].value = np.uint32(value) if value >= 0 else np.uint32(2**32 + value)
                ret = True
                break
            else:
                continue
        return ret

    def get(
        self, index: Optional[int] = None, name: Optional[str] = None, offset: Optional[int] = None
    ) -> Optional[np.uint32]:
        if index is not None:
            if index >= 0 and index < len(self.regs):
                return self.regs[index].value
        else:
            for reg in self.regs:
                if name is not None and name == reg.name:
                    return reg.value
                if offset is not None and offset == reg.offset:
                    return reg.value
        return None

    def format_str_regs_array(
        self,
        regs: list[Reg],
        align: int = 4,
        base_address: int = 0,
        joint_lines: bool = True,
        pretty_lines_stdout: int = 16,
    ) -> Union[str, list[str]]:
        """
        format string for regs with number align registers, like:
            0x00000000: 0x00000001 0x000000FF 0x0FCD0008 0x00000000
            0x00000004: 0x00000000 0x00000000 ---------- 0x00000000
        return joined string or list[string]
        """
        if align < 1 or len(regs) == 0:
            self.logger.warning(f"invalid align={align} or regs={regs}!")
            return ""

        offsets = [o for o, v, n in regs]
        offset_value_dict = {o: v for o, v, n in regs}

        key_st = np.uint32(min(offsets))
        key_ed = np.uint32(max(offsets))
        lines = []

        while key_st <= key_ed:
            valid_line = False
            line = "0x%08X:" % (key_st + np.uint32(base_address))
            for j in range(align):
                key = key_st + j * 4
                if key in offset_value_dict:
                    line += " 0x%08X" % np.uint32(offset_value_dict[key])
                    valid_line = True
                else:
                    line += " ----------"
            if valid_line:  # skip empty line
                lines.append(line)
            key_st += align * 4

        if pretty_lines_stdout >= 4 and len(lines) > pretty_lines_stdout:
            half_lines = (pretty_lines_stdout + 1) // 2
            new_lines = lines[:half_lines]
            new_lines.append(
                f"...omit middle {len(lines)-pretty_lines_stdout} lines since `max_lines_stdout={pretty_lines_stdout}`..."
            )
            new_lines += lines[-half_lines:]
            lines = new_lines

        return "\n".join(lines) if joint_lines else lines

    def parse_str_regs_array(self, line_str: str) -> Optional[list[int]]:
        """
        parse regs array from a string like:
            0x00000000: 0x00000001 0x000000FF 0x0FCD0008 0x00000000
            0x00000004: 0x00000000 0x00000000 ---------- 0x00000000
        return list[offset, value] or None
        """
        if line_str.strip() == "" or line_str.startswith("#"):
            return None
        parts = re.split(r"[: \t]+", line_str.strip())
        hex_pattern = re.compile(r"^0[xX][0-9a-fA-F]{1,8}$")

        if hex_pattern.match(parts[0]):
            start_pos = int(parts[0], 16)
        else:
            self.logger.error(f"the first column data '{parts[0]}' is not a valid address!")
            return None

        valid_regs_val_pairs = []
        invalid_cnt = 0
        for idx, part in enumerate(parts[1:]):
            if hex_pattern.match(part):
                valid_regs_val_pairs.append([start_pos + idx * 4, int(part, 16)])
            else:
                invalid_cnt += 1
        if invalid_cnt > 0:
            self.logger.warning(f"count {invalid_cnt} invalid value(s) in this line str: {line_str}")
        return valid_regs_val_pairs

    def check_regs(self) -> bool:
        unq_names = set()
        unq_offsets = set()
        dup_names = set()
        dup_offsets = set()

        for reg in self.regs:
            if reg.name in unq_names:
                dup_names.add(reg.name)
            else:
                unq_names.add(reg.name)
            if reg.offset in unq_offsets:
                dup_offsets.add(reg.offset)
            else:
                unq_offsets.add(reg.offset)

        if len(dup_names) > 0:
            self.logger.error(f"duplicate register name found: {dup_names}!")
            return False
        if len(dup_offsets) > 0:
            self.logger.error(f"duplicate register offset found: {dup_offsets}!")
            return False
        if len(self.regs) != self.nb_regs:
            self.logger.error(
                f"the real number of registers({len(self.regs)}) is not equal to manul defined nb_regs({self.nb_regs})!"
            )
            return False
        return True

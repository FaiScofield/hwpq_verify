"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_reg_csc.py
Description : 
Author      : vance.wu@rock-chips.com
Date        : 2025-07-17
LastEditTime: 2025-07-17
"""
import os
import sys
import re
import numpy as np
from enum import Enum


sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def.module_reg_core import ModuleRegisterCore

# from config_def.module_config_csc import CscConfig
from utils import setup_logger


class CscModuleIndex(Enum):
    # enum = (name, offset)
    CLUSTER0_DCI_CSC = (("CLUSTER0_DCI_CSC", 0x00001140),)
    CLUSTER0_WIN0_CSC = (("CLUSTER0_WIN0_CSC", 0x00001180),)
    CLUSTER0_WIN1_CSC = (("CLUSTER0_WIN1_CSC", 0x000011A0),)
    CLUSTER1_WIN0_CSC = (("CLUSTER1_WIN0_CSC", 0x00001380),)
    CLUSTER1_WIN1_CSC = (("CLUSTER1_WIN1_CSC", 0x000013A0),)
    POST0_ACM_R2Y = (("POST0_ACM_R2Y", 0x00000C70),)
    POST0_ACM_Y2R = (("POST0_ACM_Y2R", 0x00000CD0),)
    MSMART0_CSC = (("MSMART0_CSC", 0x00001830),)
    MSMART1_CSC = (("MSMART1_CSC", 0x00001A30),)
    ESMART0_CSC = (("ESMART0_CSC", 0x00001D00),)
    ESMART1_CSC = (("ESMART1_CSC", 0x00001F00),)
    VIVID_SDR_CSC = (("VIVID_SDR_CSC", 0x0000201C),)
    VIVID_HDR_CSC = (("VIVID_HDR_CSC", 0x00002054),)
    HWC0_CSC = (("HWC0_CSC", 0x00003830),)
    HWC1_CSC = (("HWC1_CSC", 0x00003900),)


class CscRegister(ModuleRegisterCore):
    def __init__(
        self, name: str = "CSC", platform: str = "RK3572", index: CscModuleIndex = CscModuleIndex.POST0_ACM_Y2R
    ):
        super().__init__(name, platform)
        self.index = index
        self.regs = {}  # register dict: {name: (offset, value)}
        self.base_addr = 0x0
        self.logger = setup_logger(self.name)

        if platform.lower() == "rk3572":
            self.base_addr = 0xF9000000
            self.regs[CscModuleIndex.POST0_ACM_Y2R] = {
                "POST_ACM_CTRL": [0x00000CD0, 0x0],
                "POST_ACM_Y2R_COE0102": [0x00000CD4, 0x0],
                "POST_ACM_Y2R_COE1011": [0x00000CD8, 0x0],
                "POST_ACM_Y2R_COE1220": [0x00000CDC, 0x0],
                "POST_ACM_Y2R_COE2122": [0x00000CE0, 0x0],
                "POST_ACM_Y2R_OFFSET0": [0x00000CE4, 0x0],
                "POST_ACM_Y2R_OFFSET1": [0x00000CE8, 0x0],
                "POST_ACM_Y2R_OFFSET2": [0x00000CEC, 0x0],
            }
            self.regs[CscModuleIndex.POST0_ACM_R2Y] = {
                "POST_ACM_R2Y_CTRL": [0x00000C70, 0x0],
                "POST_ACM_R2Y_COE0102": [0x00000C74, 0x0],
                "POST_ACM_R2Y_COE1011": [0x00000C78, 0x0],
                "POST_ACM_R2Y_COE1220": [0x00000C7C, 0x0],
                "POST_ACM_R2Y_COE2122": [0x00000C80, 0x0],
                "POST_ACM_R2Y_OFFSET0": [0x00000C84, 0x0],
                "POST_ACM_R2Y_OFFSET1": [0x00000C88, 0x0],
                "POST_ACM_R2Y_OFFSET2": [0x00000C8C, 0x0],
            }
        else:
            self.logger.error(f"Platform {platform} is not supported!")

    def dump(self, filename: str = "", align: int = 4, **kwargs):
        index = self.index
        if "index" in kwargs:
            arg_idx = CscModuleIndex[kwargs["index"]]
            if arg_idx in self.regs:
                index = arg_idx
            else:
                self.logger.error(f"{arg_idx} is invalid on {self.platform} now!")
        reg = self.regs[index]  # {name: [offset, value]}

        if filename == None or filename == "":
            self.logger.info(f"dump {self.platform} - {index.name} registers below:")
            data = self.format_regs_dict(reg, align, self.base_addr, False)
            for line in data:
                self.logger.info(line)
            return True

        data = self.format_regs_dict(reg, align, self.base_addr, True)
        if filename.endswith(".txt") or filename.endswith(".dat"):
            self.logger.info(f"dump {self.platform} - {index.name} registers to {filename} ...")
            with open(filename, "w") as f:
                f.write(data)
                return True
        elif filename.endswith(".bin"):
            self.logger.info(f"dump {self.platform} - {index.name} registers to {filename} ...")
            data = np.array([val for _, val in reg.values()], dtype=np.uint32)
            data.tofile(filename)
            return True

        return False

    def load(self, filename, **kwargs):
        index = self.index
        if "index" in kwargs:
            arg_idx = CscModuleIndex[kwargs["index"]]
            if arg_idx in self.regs:
                index = arg_idx
            else:
                self.logger.error(f"{arg_idx} is invalid on {self.platform} now!")
        reg = self.regs[index]  # {name: [offset, value]}

        self.logger.info(f"loading {self.platform} - {index.name} registers from {filename} ...")
        if filename.endswith(".txt") or filename.endswith(".dat"):
            valid_regs_val_pairs = []
            with open(filename, "rt") as f:
                for nb_line, line in enumerate(f, 1):
                    if line.strip() == "" or line.startswith("#"):
                        continue
                    # line = f.readline()
                    parts = re.split(r"[: \t]+", line.strip())
                    hex_pattern = re.compile(r"^0[xX][0-9a-fA-F]{1,8}$")

                    if hex_pattern.match(parts[0]):
                        start_pos = int(parts[0], 16)
                    else:
                        self.logger.error(f"{parts[0]} is not a valid offset!")
                        continue

                    invalid_cnt = 0
                    for idx, part in enumerate(parts[1:]):
                        if hex_pattern.match(part):
                            valid_regs_val_pairs.append([start_pos + idx * 4, int(part, 16)])
                        else:
                            invalid_cnt += 1
                    if invalid_cnt > 0:
                        self.logger.warning(f"count {invalid_cnt} invalid value(s) in line #{nb_line}: {line.strip()}")

            # reg_keys = [l[0] for l in reg.values()]
            for pos, val in valid_regs_val_pairs:
                pos_ok = False
                for _key, _val in reg.items():
                    if pos == _val[0] or pos == _val[0] + self.base_addr:
                        reg[_key][1] = val
                        pos_ok = True
                        continue
                if not pos_ok:
                    self.logger.warning(f"offset={pos} is not a valid register!")
            return self.dump()

        elif filename.endswith(".bin"):
            data = np.fromfile(filename, dtype=np.uint32)
            cnt = 0
            for pos in reg:
                reg[pos][1] = data[cnt]
                cnt += 1
            return self.dump()
        else:
            self.logger.error(f"{filename} is not supported!")

        return False

    def check(self, **kwargs):
        return False


if __name__ == "__main__":
    reg = CscRegister()
    reg.regs[CscModuleIndex.POST0_ACM_Y2R]["POST_ACM_CTRL"][1] = 0x04000002
    reg.regs[CscModuleIndex.POST0_ACM_Y2R]["POST_ACM_Y2R_COE0102"][1] = 0x064D0000
    reg.regs[CscModuleIndex.POST0_ACM_Y2R]["POST_ACM_Y2R_COE1011"][1] = 0xFF400400
    reg.regs[CscModuleIndex.POST0_ACM_Y2R]["POST_ACM_Y2R_COE1220"][1] = 0x0400FE21
    reg.regs[CscModuleIndex.POST0_ACM_Y2R]["POST_ACM_Y2R_COE2122"][1] = 0x0000076C
    reg.regs[CscModuleIndex.POST0_ACM_Y2R]["POST_ACM_Y2R_OFFSET0"][1] = 0xFFF36600
    reg.regs[CscModuleIndex.POST0_ACM_Y2R]["POST_ACM_Y2R_OFFSET1"][1] = 0x00053E00
    reg.regs[CscModuleIndex.POST0_ACM_Y2R]["POST_ACM_Y2R_OFFSET2"][1] = 0xFFF12800

    # reg.dump(filename="csc_regs.txt", index="CLUSTER0_DCI_CSC")
    reg.load(filename="csc_regs.txt")

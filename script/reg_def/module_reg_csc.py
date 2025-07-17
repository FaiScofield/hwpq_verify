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
import argparse
import numpy as np
from enum import Enum


sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def.module_reg_core import ModuleRegisterCore, Reg
from config_def.module_config_csc import CscConfig
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

        self.config = CscConfig(name)
        self.reg_dicts = {  # CscModuleIndex : list[Reg]
            CscModuleIndex.POST0_ACM_R2Y: [],
            CscModuleIndex.POST0_ACM_Y2R: [],
        }
        self.base_addr = 0x0
        self.logger = setup_logger(self.name)
        self.update(platform=platform, index=index)

    def update(self, **kwargs) -> bool:
        if "platform" in kwargs:
            self.platform = kwargs["platform"]
        if "index" in kwargs:
            index = kwargs["index"]
            self.index = index if isinstance(index, CscModuleIndex) else CscModuleIndex[index]

        if self.platform.lower() == "rk3572":
            self.base_addr = 0xF9000000
            self.reg_dicts[CscModuleIndex.POST0_ACM_Y2R] = [
                Reg(0x00000CD0, 0x0, "POST_ACM_CTRL"),
                Reg(0x00000CD4, 0x0, "POST_ACM_Y2R_COE0102"),
                Reg(0x00000CD8, 0x0, "POST_ACM_Y2R_COE1011"),
                Reg(0x00000CDC, 0x0, "POST_ACM_Y2R_COE1220"),
                Reg(0x00000CE0, 0x0, "POST_ACM_Y2R_COE2122"),
                Reg(0x00000CE4, 0x0, "POST_ACM_Y2R_OFFSET0"),
                Reg(0x00000CE8, 0x0, "POST_ACM_Y2R_OFFSET1"),
                Reg(0x00000CEC, 0x0, "POST_ACM_Y2R_OFFSET2"),
            ]
            self.reg_dicts[CscModuleIndex.POST0_ACM_R2Y] = [
                Reg(0x00000C70, 0x0, "POST_ACM_R2Y_CTRL"),
                Reg(0x00000C74, 0x0, "POST_ACM_R2Y_COE0102"),
                Reg(0x00000C78, 0x0, "POST_ACM_R2Y_COE1011"),
                Reg(0x00000C7C, 0x0, "POST_ACM_R2Y_COE1220"),
                Reg(0x00000C80, 0x0, "POST_ACM_R2Y_COE2122"),
                Reg(0x00000C84, 0x0, "POST_ACM_R2Y_OFFSET0"),
                Reg(0x00000C88, 0x0, "POST_ACM_R2Y_OFFSET1"),
                Reg(0x00000C8C, 0x0, "POST_ACM_R2Y_OFFSET2"),
            ]
            if self.index in self.reg_dicts:
                self.regs = self.reg_dicts[self.index]
                return True
            else:
                self.logger.error(f"HW module {self.index} is invalid on {self.platform} now!")
        else:
            self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def dump(self, filename: str = "", align: int = 4, **kwargs) -> bool:
        index = self.index
        if "index" in kwargs:
            arg_idx = CscModuleIndex[kwargs["index"]]
            if arg_idx in self.reg_dicts:
                index = arg_idx
            else:
                self.logger.error(f"{arg_idx} is invalid on {self.platform} now!")
        regs = self.reg_dicts[index]  # [offset, value, name]

        if filename == None or filename == "":
            self.logger.info(f"dump {self.platform} - {index.name} registers below:")
            data = self.format_regs_dict(regs, align, self.base_addr, False)
            for line in data:
                self.logger.info(line)
            return True

        data = self.format_regs_dict(regs, align, self.base_addr, True)
        if filename.endswith(".txt") or filename.endswith(".dat"):
            self.logger.info(f"dump {self.platform} - {index.name} registers to {filename} ...")
            with open(filename, "w") as f:
                f.write(data)
                return True
        elif filename.endswith(".bin"):
            self.logger.info(f"dump {self.platform} - {index.name} registers to {filename} ...")
            data = np.array([val for _, val, _ in regs], dtype=np.uint32)
            data.tofile(filename)
            return True

        return False

    def load(self, filename, **kwargs) -> bool:
        index = self.index
        if "index" in kwargs:
            arg_idx = CscModuleIndex[kwargs["index"]]
            if arg_idx in self.reg_dicts:
                index = arg_idx
            else:
                self.logger.error(f"{arg_idx} is invalid on {self.platform} now!")
        regs = self.reg_dicts[index]  # [offset, value, name]

        self.logger.info(f"loading {self.platform} - {index.name} registers from {filename} ...")
        if filename.endswith(".txt") or filename.endswith(".dat"):
            valid_regs_val_pairs = []  # [offset, value]
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
                for i in range(len(regs)):
                    if pos == regs[i].offset or pos == regs[i].offset + self.base_addr:
                        regs[i].value = val
                        pos_ok = True
                        break
                if not pos_ok:
                    self.logger.warning(f"offset={pos} is not a valid register!")
            return self.dump()
        elif filename.endswith(".bin"):
            data = np.fromfile(filename, dtype=np.uint32)
            if len(data) < len(regs):
                self.logger.error(
                    f"not enough register data in {filename}! require {len(regs)} registers, but only get {len(data)}!"
                )
                return False
            for i in range(len(regs)):
                regs[i].value = data[i]
            return self.dump()
        elif filename.endswith(".json"):
            ok = self.config.load(filename)
            # self.config.dump()
            ok |= self.config2regs()
            ok |= self.dump()
            return ok
        else:
            self.logger.error(f"{filename} is not supported!")

        return False

    def config2regs(self) -> bool:
        regs = self.reg_dicts[self.index]  # [offset, value, name]
        if self.index == CscModuleIndex.POST0_ACM_Y2R or self.index == CscModuleIndex.POST0_ACM_R2Y:
            regs[0].value = 0x2 | ((self.config.cscMatrix[0, 0] & 0x3FF) << 16)
            regs[1].value = (self.config.cscMatrix[0, 1] & 0x3FF) | ((self.config.cscMatrix[0, 2] & 0x3FF) << 16)
            regs[2].value = (self.config.cscMatrix[1, 0] & 0x3FF) | ((self.config.cscMatrix[1, 1] & 0x3FF) << 16)
            regs[3].value = (self.config.cscMatrix[1, 2] & 0x3FF) | ((self.config.cscMatrix[2, 0] & 0x3FF) << 16)
            regs[4].value = (self.config.cscMatrix[2, 1] & 0x3FF) | ((self.config.cscMatrix[2, 2] & 0x3FF) << 16)
            regs[5].value = self.config.cscVector[0]
            regs[6].value = self.config.cscVector[1]
            regs[7].value = self.config.cscVector[2]
            return True

        return False

    def regs2config(self) -> bool:
        # TODO
        return False

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument(
        "-m",
        "--module",
        type=str,
        default="POST0_ACM_Y2R",
        help=f"设置硬件所处模块: {CscModuleIndex.__members__.keys()}",
    )
    parser.print_usage()
    args = parser.parse_args()

    module = CscModuleIndex[args.module]
    register = CscRegister(args.platform, index=module)
    register.set(index=0, value=0x04000002)
    register.set(index=1, value=0x064D0000)
    register.set(index=2, value=0xFF400400)
    register.set(index=3, value=0x0400FE21)
    register.set(index=4, value=0x0000076C)
    register.set(index=5, value=0xFFF36600)
    register.set(index=6, value=0x00053E00)
    register.set(index=7, value=0xFFF12800)

    val = register.get(index=8)
    if val is not None:
        print("register #8: 0x%08X" % val)
    else:
        print("None of register #8 exist!")

    if args.interface == "load":
        register.load(args.file)
    elif args.interface == "dump":
        register.dump(args.file)
    else:
        print(f"interface {args.interface} is not supported!")
        args.print_help()

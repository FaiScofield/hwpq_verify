"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_reg_csc.py
Description :
Author      : vance.wu@rock-chips.com
Date        : 2025-07-17
LastEditTime: 2025-07-22
"""

import os
import sys
import argparse
import numpy as np
from enum import Enum


sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def.module_reg_core import ModuleRegisterCore, Reg
from config_def.module_config_csc import CscConfig


class CscModuleIndex(Enum):
    """enum = (name, offset)"""

    ## start with (xxx; coef00)
    POST0_ACM_R2Y = ("POST0_ACM_R2Y", 0x00000C70)  # (bypass, en; coef00)
    POST0_ACM_Y2R = ("POST0_ACM_Y2R", 0x00000CD0)  # (bypass, en; coef00)
    POST1_BCSH_Y2R = ("POST1_BCSH_Y2R", 0x00000DD0)  # (xxx; coef00)
    ## start with (coef00; coef01)
    CLUSTER0_DCI_CSC = ("CLUSTER0_DCI_CSC", 0x00001140)
    CLUSTER0_WIN0_CSC = ("CLUSTER0_WIN0_CSC", 0x00001180)
    CLUSTER0_WIN1_CSC = ("CLUSTER0_WIN1_CSC", 0x000011A0)
    CLUSTER1_WIN0_CSC = ("CLUSTER1_WIN0_CSC", 0x00001380)
    CLUSTER1_WIN1_CSC = ("CLUSTER1_WIN1_CSC", 0x000013A0)
    ESMART0_CSC = ("ESMART0_CSC", 0x00001900)
    ESMART1_CSC = ("ESMART1_CSC", 0x00001B00)
    MSMART0_CSC = ("MSMART0_CSC", 0x00001C30)
    MSMART1_CSC = ("MSMART1_CSC", 0x00001E30)
    VIVID_SDR_CSC = ("VIVID_SDR_CSC", 0x0000201C)
    VIVID_HDR_CSC = ("VIVID_HDR_CSC", 0x00002054)
    HWC0_CSC = ("HWC0_CSC", 0x00003830)
    HWC1_CSC = ("HWC1_CSC", 0x00003930)


g_csc_new_reg_arrange = [CscModuleIndex.POST0_ACM_R2Y, CscModuleIndex.POST0_ACM_Y2R, CscModuleIndex.POST1_BCSH_Y2R]


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
            CscModuleIndex.POST1_BCSH_Y2R: [],
            CscModuleIndex.CLUSTER0_DCI_CSC: [],
            # CscModuleIndex.CLUSTER0_WIN0_CSC: [],
            # CscModuleIndex.CLUSTER0_WIN1_CSC: [],
            # CscModuleIndex.CLUSTER1_WIN0_CSC: [],
            # CscModuleIndex.CLUSTER1_WIN1_CSC: [],
        }
        self.base_addr = 0x0
        self.update(platform=platform, index=index)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if "platform" in kwargs:
            self.platform = kwargs["platform"]
        if "index" in kwargs:
            index = kwargs["index"]
            self.index = index if isinstance(index, CscModuleIndex) else CscModuleIndex[index]

        if self.platform.lower() == "rk3572":
            self.base_addr = 0xF9000000
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
            self.reg_dicts[CscModuleIndex.POST1_BCSH_Y2R] = [
                Reg(0x00000DD0, 0x0, "POST_BCSH_R2Y_COE00"),
                Reg(0x00000DD4, 0x0, "POST_BCSH_R2Y_COE02_01"),
                Reg(0x00000DD8, 0x0, "POST_BCSH_R2Y_COE11_10"),
                Reg(0x00000DDC, 0x0, "POST_BCSH_R2Y_COE20_12"),
                Reg(0x00000DE0, 0x0, "POST_BCSH_R2Y_COE22_21"),
                Reg(0x00000DE4, 0x0, "POST_BCSH_R2Y_OFFSET0"),
                Reg(0x00000DE8, 0x0, "POST_BCSH_R2Y_OFFSET1"),
                Reg(0x00000DEC, 0x0, "POST_BCSH_R2Y_OFFSET2"),
            ]
            self.reg_dicts[CscModuleIndex.CLUSTER0_DCI_CSC] = [
                Reg(0x00001140, 0x0, "DCI_CSC_COE01_00"),
                Reg(0x00001144, 0x0, "DCI_CSC_COE10_02"),
                Reg(0x00001148, 0x0, "DCI_CSC_COE12_11"),
                Reg(0x0000114C, 0x0, "DCI_CSC_COE21_20"),
                Reg(0x00001150, 0x0, "DCI_CSC_COE22"),
                Reg(0x00001154, 0x0, "DCI_CSC_OFFSET0"),
                Reg(0x00001158, 0x0, "DCI_CSC_OFFSET1"),
                Reg(0x0000115C, 0x0, "DCI_CSC_OFFSET2"),
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
                self.logger.info(f"about to dump regs of {index.name}, self.index={self.index.name}")
            else:
                self.logger.error(f"{arg_idx} is invalid on {self.platform} now!")
        if index in self.reg_dicts:
            regs = self.reg_dicts[index]  # [offset, value, name]
        else:
            self.logger.error(f"HW module {index} is invalid on {self.platform} now!")
            return False

        self.logger.info(f"dump {self.platform} - {index.name} registers...")
        return super().dump(filename, align, regs=regs)

    def load(self, filename, **kwargs) -> bool:
        index = self.index
        if "index" in kwargs:
            arg_idx = CscModuleIndex[kwargs["index"]]
            if arg_idx in self.reg_dicts:
                index = arg_idx
                self.logger.info(f"about to load regs of {index.name}, self.index={self.index.name}")
            else:
                self.logger.error(f"{arg_idx} is invalid on {self.platform} now!")
        if index in self.reg_dicts:
            self.regs = self.reg_dicts[index]  # [offset, value, name]
        else:
            self.logger.error(f"HW module {index} is invalid on {self.platform} now!")
            return False

        self.logger.info(f"loading {self.platform} - {index.name} registers from {filename} ...")
        return super().load(filename, **kwargs)

    def gen(self, seed=114514, **kwargs) -> bool:
        if self.index in [
            CscModuleIndex.CLUSTER0_DCI_CSC,
            CscModuleIndex.CLUSTER0_WIN0_CSC,
            CscModuleIndex.CLUSTER0_WIN1_CSC,
            CscModuleIndex.CLUSTER1_WIN0_CSC,
            CscModuleIndex.CLUSTER1_WIN1_CSC,
        ]:
            precision = 13
        else:
            precision = 10
        return super().gen(seed, precision=precision, **kwargs)

    def config2regs(self) -> bool:
        if self.index not in self.reg_dicts:
            self.logger.error(f"HW module {self.index} is invalid on {self.platform} now!")
            return False

        self.regs = self.reg_dicts[self.index]  # [offset, value, name]
        CM = np.uint16(0xFFFF)  # coef mask = 0x3FF or 0xFFFF
        self.config.cscMatrix = np.clip(self.config.cscMatrix, -(2**12), 2**12 - 1)  # s13
        self.config.cscVector = np.clip(self.config.cscVector, -(2**22), 2**22 - 1)  # s23
        if self.index in g_csc_new_reg_arrange:
            self.regs[0].value = 0x3 | ((self.config.cscMatrix[0, 0] & CM) << 16)
            self.regs[1].value = (self.config.cscMatrix[0, 1] & CM) | ((self.config.cscMatrix[0, 2] & CM) << 16)
            self.regs[2].value = (self.config.cscMatrix[1, 0] & CM) | ((self.config.cscMatrix[1, 1] & CM) << 16)
            self.regs[3].value = (self.config.cscMatrix[1, 2] & CM) | ((self.config.cscMatrix[2, 0] & CM) << 16)
            self.regs[4].value = (self.config.cscMatrix[2, 1] & CM) | ((self.config.cscMatrix[2, 2] & CM) << 16)
        else:
            self.regs[0].value = (self.config.cscMatrix[0, 0] & CM) | ((self.config.cscMatrix[0, 1] & CM) << 16)
            self.regs[1].value = (self.config.cscMatrix[0, 2] & CM) | ((self.config.cscMatrix[1, 0] & CM) << 16)
            self.regs[2].value = (self.config.cscMatrix[1, 1] & CM) | ((self.config.cscMatrix[1, 2] & CM) << 16)
            self.regs[3].value = (self.config.cscMatrix[2, 0] & CM) | ((self.config.cscMatrix[2, 1] & CM) << 16)
            self.regs[4].value = self.config.cscMatrix[2, 2] & CM
        self.regs[5].value = self.config.cscVector[0]
        self.regs[6].value = self.config.cscVector[1]
        self.regs[7].value = self.config.cscVector[2]
        return True

    def regs2config(self) -> bool:
        if self.index not in self.reg_dicts:
            self.logger.error(f"HW module {self.index} is invalid on {self.platform} now!")
            return False

        self.regs = self.reg_dicts[self.index]  # [offset, value, name]
        CM = np.uint32(0xFFFF)  # coef mask = 0x3FF or 0xFFFF
        if self.index in g_csc_new_reg_arrange:
            self.config.cscEnable = (self.regs[0].value >> 1) & 0x1
            self.config.cscMatrix[0, 0] = np.int16(np.uint16(self.regs[0].value >> 16) & CM)
            self.config.cscMatrix[0, 1] = np.int16(np.uint16(self.regs[1].value & CM))
            self.config.cscMatrix[0, 2] = np.int16(np.uint16(self.regs[1].value >> 16) & CM)
            self.config.cscMatrix[1, 0] = np.int16(np.uint16(self.regs[2].value & CM))
            self.config.cscMatrix[1, 1] = np.int16(np.uint16(self.regs[2].value >> 16) & CM)
            self.config.cscMatrix[1, 2] = np.int16(np.uint16(self.regs[3].value & CM))
            self.config.cscMatrix[2, 0] = np.int16(np.uint16(self.regs[3].value >> 16) & CM)
            self.config.cscMatrix[2, 1] = np.int16(np.uint16(self.regs[4].value & CM))
            self.config.cscMatrix[2, 2] = np.int16(np.uint16(self.regs[4].value >> 16) & CM)
        else:
            self.config.cscMatrix[0, 0] = np.int16(np.uint16(self.regs[0].value & CM))
            self.config.cscMatrix[0, 1] = np.int16(np.uint16(self.regs[0].value >> 16) & CM)
            self.config.cscMatrix[0, 2] = np.int16(np.uint16(self.regs[1].value & CM))
            self.config.cscMatrix[1, 0] = np.int16(np.uint16(self.regs[1].value >> 16) & CM)
            self.config.cscMatrix[1, 1] = np.int16(np.uint16(self.regs[2].value & CM))
            self.config.cscMatrix[1, 2] = np.int16(np.uint16(self.regs[2].value >> 16) & CM)
            self.config.cscMatrix[2, 0] = np.int16(np.uint16(self.regs[3].value & CM))
            self.config.cscMatrix[2, 1] = np.int16(np.uint16(self.regs[3].value >> 16) & CM)
            self.config.cscMatrix[2, 2] = np.int16(np.uint16(self.regs[4].value & CM))
        self.config.cscVector[0] = self.regs[5].value
        self.config.cscVector[1] = self.regs[6].value
        self.config.cscVector[2] = self.regs[7].value
        self.config.cscMatrix = np.clip(self.config.cscMatrix, -(2**12), 2**12 - 1)  # s13
        self.config.cscVector = np.clip(self.config.cscVector, -(2**22), 2**22 - 1)  # s23
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/config2regs/regs2config"
    )
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
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
    register = CscRegister(platform=args.platform, index=module)
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
        register.logger.info("register #8: 0x%08X" % val)
    else:
        register.logger.error("None of register #8 exist!")

    if args.interface == "load":
        register.load(args.file, index=args.module)
    elif args.interface == "dump":
        register.dump(args.file, index=args.module)
    elif args.interface == "gen":
        register.gen(args.seed)
        register.dump(args.file)
    else:
        register.logger.error(f"interface {args.interface} is not supported!")
        args.print_help()

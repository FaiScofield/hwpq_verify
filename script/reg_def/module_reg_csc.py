"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_reg_csc.py
Description :
Author      : vance.wu@rock-chips.com
Date        : 2025-07-17
LastEditTime: 2025-09-01
"""

import os
import sys
import argparse
import numpy as np
from enum import Enum


sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def.module_reg_core import ModuleRegisterCore, Reg
from config_def.module_config_csc import CscConfig
from utils import enum_with_index


@enum_with_index
class CscModuleIndex(Enum):
    """enum = (name, offset)"""

    ## start with (xxx; coef00)
    POST0_ACM_R2Y = ("POST0_ACM_R2Y", 0x00000C70)  # (bypass, en; coef00)
    POST0_ACM_Y2R = ("POST0_ACM_Y2R", 0x00000CD0)  # (bypass, en; coef00)
    POST1_BCSH_Y2R = ("POST1_BCSH_Y2R", 0x00000DD0)  # (xxx; coef00)
    ## start with (coef00; coef01)
    CLUSTER0_WIN0_CSC = ("CLUSTER0_WIN0_CSC", 0x00001180)  # 13bit coefs
    CLUSTER0_WIN1_CSC = ("CLUSTER0_WIN1_CSC", 0x000011A0)
    CLUSTER1_WIN0_CSC = ("CLUSTER1_WIN0_CSC", 0x00001380)
    CLUSTER1_WIN1_CSC = ("CLUSTER1_WIN1_CSC", 0x000013A0)
    ESMART0_CSC = ("ESMART0_CSC", 0x00001900)  # 13bit coefs
    ESMART1_CSC = ("ESMART1_CSC", 0x00001B00)
    MSMART0_CSC = ("MSMART0_CSC", 0x00001C30)
    MSMART1_CSC = ("MSMART1_CSC", 0x00001E30)
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
            CscModuleIndex.CLUSTER0_WIN0_CSC: [],
            CscModuleIndex.CLUSTER0_WIN1_CSC: [],
            CscModuleIndex.CLUSTER1_WIN0_CSC: [],
            CscModuleIndex.CLUSTER1_WIN1_CSC: [],
        }
        self.base_addr = 0x0
        self.update(platform=platform, index=index)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if "platform" in kwargs:
            self.platform = kwargs["platform"].upper()
        if "index" in kwargs:
            index = kwargs["index"]
            try:
                self.index = CscModuleIndex.from_index(index)
            except:
                self.logger.error(f"failed to change index to {index}!")

        if self.platform.lower() == "rk3572":
            self.base_addr = 0xF9000000
            self.reg_dicts[CscModuleIndex.POST0_ACM_R2Y] = [
                Reg(0x00, 0x0, "POST_ACM_R2Y_CTRL"),
                Reg(0x04, 0x0, "POST_ACM_R2Y_COE0102"),
                Reg(0x08, 0x0, "POST_ACM_R2Y_COE1011"),
                Reg(0x0C, 0x0, "POST_ACM_R2Y_COE1220"),
                Reg(0x10, 0x0, "POST_ACM_R2Y_COE2122"),
                Reg(0x14, 0x0, "POST_ACM_R2Y_OFFSET0"),
                Reg(0x18, 0x0, "POST_ACM_R2Y_OFFSET1"),
                Reg(0x1C, 0x0, "POST_ACM_R2Y_OFFSET2"),
            ]
            self.reg_dicts[CscModuleIndex.POST0_ACM_Y2R] = [
                Reg(0x00, 0x0, "POST_ACM_CTRL"),
                Reg(0x04, 0x0, "POST_ACM_Y2R_COE0102"),
                Reg(0x08, 0x0, "POST_ACM_Y2R_COE1011"),
                Reg(0x0C, 0x0, "POST_ACM_Y2R_COE1220"),
                Reg(0x10, 0x0, "POST_ACM_Y2R_COE2122"),
                Reg(0x14, 0x0, "POST_ACM_Y2R_OFFSET0"),
                Reg(0x18, 0x0, "POST_ACM_Y2R_OFFSET1"),
                Reg(0x1C, 0x0, "POST_ACM_Y2R_OFFSET2"),
            ]
            self.reg_dicts[CscModuleIndex.POST1_BCSH_Y2R] = [
                Reg(0x00, 0x0, "POST_BCSH_R2Y_COE00"),
                Reg(0x04, 0x0, "POST_BCSH_R2Y_COE02_01"),
                Reg(0x08, 0x0, "POST_BCSH_R2Y_COE11_10"),
                Reg(0x0C, 0x0, "POST_BCSH_R2Y_COE20_12"),
                Reg(0x10, 0x0, "POST_BCSH_R2Y_COE22_21"),
                Reg(0x14, 0x0, "POST_BCSH_R2Y_OFFSET0"),
                Reg(0x18, 0x0, "POST_BCSH_R2Y_OFFSET1"),
                Reg(0x1C, 0x0, "POST_BCSH_R2Y_OFFSET2"),
            ]
            self.reg_dicts[CscModuleIndex.CLUSTER0_DCI_CSC] = [
                Reg(0x00, 0x0, "CSC_COE01_00"),
                Reg(0x04, 0x0, "CSC_COE10_02"),
                Reg(0x08, 0x0, "CSC_COE12_11"),
                Reg(0x0C, 0x0, "CSC_COE21_20"),
                Reg(0x10, 0x0, "CSC_COE22"),
                Reg(0x14, 0x0, "CSC_OFFSET0"),
                Reg(0x18, 0x0, "CSC_OFFSET1"),
                Reg(0x1C, 0x0, "CSC_OFFSET2"),
            ]
            self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_DCI_CSC].copy()
            self.reg_dicts[CscModuleIndex.CLUSTER0_WIN1_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_DCI_CSC].copy()
            self.reg_dicts[CscModuleIndex.CLUSTER1_WIN0_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_DCI_CSC].copy()
            self.reg_dicts[CscModuleIndex.CLUSTER1_WIN1_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_DCI_CSC].copy()
            if self.index in self.reg_dicts:
                self.regs = self.reg_dicts[self.index]
                self.nb_regs = len(self.regs)
                return self.check_regs()
            else:
                self.logger.error(f"HW module {self.index} is invalid on {self.platform} now!")
        else:
            self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def config2regs(self) -> bool:
        if self.index not in self.reg_dicts:
            self.logger.error(f"HW module {self.index} is invalid on {self.platform} now!")
            return False

        self.regs = self.reg_dicts[self.index]  # [offset, value, name]
        CM = np.uint16(0xFFFF)  # coef mask = 0x3FF or 0xFFFF
        self.config.cscMatrix = np.clip(self.config.cscMatrix, -(2**12), 2**12 - 1)  # s13
        self.config.cscVector = np.clip(self.config.cscVector, -(2**22), 2**22 - 1)  # s23
        cscMatrix = self.config.cscMatrix.astype(np.int32)  # s16->s32 first
        cscVector = self.config.cscVector.astype(np.int32)  # s32->s32 first
        if self.index in g_csc_new_reg_arrange:
            self.regs[0].value = 0x1 | ((self.config.cscEnable * 0x1) << 1) | ((cscMatrix[0, 0] & CM) << 16)
            self.regs[1].value = (cscMatrix[0, 1] & CM) | ((cscMatrix[0, 2] & CM) << 16)
            self.regs[2].value = (cscMatrix[1, 0] & CM) | ((cscMatrix[1, 1] & CM) << 16)
            self.regs[3].value = (cscMatrix[1, 2] & CM) | ((cscMatrix[2, 0] & CM) << 16)
            self.regs[4].value = (cscMatrix[2, 1] & CM) | ((cscMatrix[2, 2] & CM) << 16)
        else:
            self.regs[0].value = (cscMatrix[0, 0] & CM) | ((cscMatrix[0, 1] & CM) << 16)
            self.regs[1].value = (cscMatrix[0, 2] & CM) | ((cscMatrix[1, 0] & CM) << 16)
            self.regs[2].value = (cscMatrix[1, 1] & CM) | ((cscMatrix[1, 2] & CM) << 16)
            self.regs[3].value = (cscMatrix[2, 0] & CM) | ((cscMatrix[2, 1] & CM) << 16)
            self.regs[4].value = cscMatrix[2, 2] & CM
        self.regs[5].value = cscVector[0]
        self.regs[6].value = cscVector[1]
        self.regs[7].value = cscVector[2]
        return True

    def regs2config(self) -> bool:
        if self.index not in self.reg_dicts:
            self.logger.error(f"HW module {self.index} is invalid on {self.platform} now!")
            return False

        self.regs = self.reg_dicts[self.index]  # [offset, value, name]
        CM = np.uint32(0xFFFF)  # coef mask = 0x3FF or 0xFFFF
        if self.index in g_csc_new_reg_arrange:
            self.config.cscEnable = (self.regs[0].value >> 1) & 0x1
            self.config.cscMatrix[0, 0] = ((self.regs[0].value >> 16) & CM).astype(np.int16)
            self.config.cscMatrix[0, 1] = ((self.regs[1].value & CM)).astype(np.int16)
            self.config.cscMatrix[0, 2] = ((self.regs[1].value >> 16) & CM).astype(np.int16)
            self.config.cscMatrix[1, 0] = ((self.regs[2].value & CM)).astype(np.int16)
            self.config.cscMatrix[1, 1] = ((self.regs[2].value >> 16) & CM).astype(np.int16)
            self.config.cscMatrix[1, 2] = ((self.regs[3].value & CM)).astype(np.int16)
            self.config.cscMatrix[2, 0] = ((self.regs[3].value >> 16) & CM).astype(np.int16)
            self.config.cscMatrix[2, 1] = ((self.regs[4].value & CM)).astype(np.int16)
            self.config.cscMatrix[2, 2] = ((self.regs[4].value >> 16) & CM).astype(np.int16)
        else:
            self.config.cscMatrix[0, 0] = ((self.regs[0].value & CM)).astype(np.int16)
            self.config.cscMatrix[0, 1] = ((self.regs[0].value >> 16) & CM).astype(np.int16)
            self.config.cscMatrix[0, 2] = ((self.regs[1].value & CM)).astype(np.int16)
            self.config.cscMatrix[1, 0] = ((self.regs[1].value >> 16) & CM).astype(np.int16)
            self.config.cscMatrix[1, 1] = ((self.regs[2].value & CM)).astype(np.int16)
            self.config.cscMatrix[1, 2] = ((self.regs[2].value >> 16) & CM).astype(np.int16)
            self.config.cscMatrix[2, 0] = ((self.regs[3].value & CM)).astype(np.int16)
            self.config.cscMatrix[2, 1] = ((self.regs[3].value >> 16) & CM).astype(np.int16)
            self.config.cscMatrix[2, 2] = ((self.regs[4].value & CM)).astype(np.int16)
        self.config.cscVector[0] = self.regs[5].value.astype(np.int32)
        self.config.cscVector[1] = self.regs[6].value.astype(np.int32)
        self.config.cscVector[2] = self.regs[7].value.astype(np.int32)
        # self.config.cscMatrix = np.clip(self.config.cscMatrix, -(2**12), 2**12 - 1)  # s13
        # self.config.cscVector = np.clip(self.config.cscVector, -(2**22), 2**22 - 1)  # s23
        # self.config.cscVecB4Mul = np.linalg.solve(self.config.cscMatrix, self.config.cscVector).astype(np.int32)
        return True

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3538...")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.add_argument(
        "-m", "--module", type=str, default="POST0_ACM_Y2R", help=f"设置硬件所处模块: {CscModuleIndex.__members__.keys()}"
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
        if register.gen(args.seed):
            register.dump(args.file)
    elif args.interface in ["c2r", "config2regs"]:
        register.config.gen(args.seed)
        register.config.dump()
        if register.config2regs():
            register.dump()
    elif args.interface in ["r2c", "regs2config"]:
        register.gen(args.seed)
        register.dump()
        if register.regs2config():
            register.config.dump()
    else:
        register.logger.error(f"interface {args.interface} is not supported!")
        parser.print_help()

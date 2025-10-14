"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_reg_csc.py
Description :
Author      : vance.wu@rock-chips.com
Date        : 2025-07-17
LastEditTime: 2025-09-03
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
import tool.get_csc_coefs as csc_core


@enum_with_index
class CscModuleIndex(Enum):
    """enum = (name, offset, coef_precision)"""

    ## start with (xxx; coef00)
    POST0_ACM_R2Y = ("POST0_ACM_R2Y", 0x00000C70, 10)  # (bypass, en; coef00)
    POST0_ACM_Y2R = ("POST0_ACM_Y2R", 0x00000CD0, 10)  # (bypass, en; coef00)
    POST1_BCSH_Y2R = ("POST1_BCSH_Y2R", 0x00000DD0, 10)  # (xxx; coef00)
    ## start with (coef00; coef01)
    CLUSTER0_WIN0_CSC = ("CLUSTER0_WIN0_CSC", 0x00001180, 13)  # 13bit coefs
    CLUSTER0_WIN1_CSC = ("CLUSTER0_WIN1_CSC", 0x000011A0, 10)
    CLUSTER1_WIN0_CSC = ("CLUSTER1_WIN0_CSC", 0x00001380, 10)
    CLUSTER1_WIN1_CSC = ("CLUSTER1_WIN1_CSC", 0x000013A0, 10)
    ESMART0_CSC = ("ESMART0_CSC", 0x00001900, 13)  # 13bit coefs
    ESMART1_CSC = ("ESMART1_CSC", 0x00001B00, 10)
    MSMART0_CSC = ("MSMART0_CSC", 0x00001C30, 10)
    MSMART1_CSC = ("MSMART1_CSC", 0x00001E30, 10)
    HWC0_CSC = ("HWC0_CSC", 0x00003830, 10)
    HWC1_CSC = ("HWC1_CSC", 0x00003930, 10)


g_post_csc = [CscModuleIndex.POST0_ACM_R2Y, CscModuleIndex.POST0_ACM_Y2R, CscModuleIndex.POST1_BCSH_Y2R]


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
            CscModuleIndex.CLUSTER0_WIN0_CSC: [],
            CscModuleIndex.CLUSTER0_WIN1_CSC: [],
            CscModuleIndex.CLUSTER1_WIN0_CSC: [],
            CscModuleIndex.CLUSTER1_WIN1_CSC: [],
            CscModuleIndex.ESMART0_CSC: [],
            CscModuleIndex.ESMART1_CSC: [],
            CscModuleIndex.MSMART0_CSC: [],
            CscModuleIndex.MSMART1_CSC: [],
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
            self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC] = [
                Reg(0x00, 0x0, "CSC_COE01_00"),
                Reg(0x04, 0x0, "CSC_COE10_02"),
                Reg(0x08, 0x0, "CSC_COE12_11"),
                Reg(0x0C, 0x0, "CSC_COE21_20"),
                Reg(0x10, 0x0, "CSC_COE22"),
                Reg(0x14, 0x0, "CSC_OFFSET0"),
                Reg(0x18, 0x0, "CSC_OFFSET1"),
                Reg(0x1C, 0x0, "CSC_OFFSET2"),
            ]
            self.reg_dicts[CscModuleIndex.CLUSTER0_WIN1_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC].copy()
            self.reg_dicts[CscModuleIndex.CLUSTER1_WIN0_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC].copy()
            self.reg_dicts[CscModuleIndex.CLUSTER1_WIN1_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC].copy()
            self.reg_dicts[CscModuleIndex.ESMART0_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC].copy()
            self.reg_dicts[CscModuleIndex.ESMART1_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC].copy()
            self.reg_dicts[CscModuleIndex.MSMART0_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC].copy()
            self.reg_dicts[CscModuleIndex.MSMART1_CSC] = self.reg_dicts[CscModuleIndex.CLUSTER0_WIN0_CSC].copy()
            if self.index in self.reg_dicts:
                self.regs = self.reg_dicts[self.index]
                self.nb_regs = len(self.regs)
                self.logger.info(
                    f"reg index set to: {self.index.name}, len={self.nb_regs}, precision={self.index.value[2]}"
                )
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
        if self.config.cscPassthrough:
            cscMatrix = self.config.cscMatrix.astype(np.int32)  # s16->s32 first
            cscVector = self.config.cscVector.astype(np.int32)  # s32->s32 first
        else:
            ## generate csc matrix and vector with CscCoefConfig
            csc_config = csc_core.CscCoefConfig()
            csc_config.platform = self.platform
            csc_config.pixel_depth = self.config.cscPixelDepth
            csc_config.coef_precision = self.config.cscCoefPrecision
            if self.config.cscConvertMode in range(0, 41):
                mode_key = list(csc_core.g_supported_standard_convert_modes.keys())[self.config.cscConvertMode]
                csc_config.csc_mode = csc_core.g_supported_standard_convert_modes[mode_key]
            else:
                self.logger.error(f"Invalid cscConvertMode {self.config.cscConvertMode}! Valid range: [0, 40]!")
                return False

            ## adjust csc matri with BCSH config
            bcsh_config = csc_core.CscBcshConfig()
            bcsh_config.hue = self.config.cscHue
            bcsh_config.saturation = self.config.cscSaturation
            bcsh_config.contrast = self.config.cscContrast
            bcsh_config.brightness = self.config.cscBrightness
            bcsh_config.r_gain = self.config.cscRGain
            bcsh_config.g_gain = self.config.cscGGain
            bcsh_config.b_gain = self.config.cscBGain
            bcsh_config.r_offset = self.config.cscROffset
            bcsh_config.g_offset = self.config.cscGOffset
            bcsh_config.b_offset = self.config.cscBOffset
            cscMatrix, cscVector = csc_core.get_csc_coefs(csc_config, bcsh_config)

        if self.index in g_post_csc:
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
        if self.index in g_post_csc:
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
        return True

    def dump(self, filename: str = "", align: int = 4, pretty_lines_stdout: int = 16, **kwargs) -> bool:
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
        return super().dump(filename, align, pretty_lines_stdout, regs=regs)

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
        precision = self.index.value[2]
        return super().gen(seed, precision=precision, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3538...")
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

"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_cfa.py
Author      : vance.wu@rock-chips.com
Date        : 2025-08-11
Description :
LastEditTime: 2025-08-13
"""

import os
import sys
import argparse
import traceback
import numpy as np
from enum import Enum

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def import *
from config_def import CfaConfig


class CfaC2pInfo(Enum):
    ## eCfaPattern_value, c2p_id, c2p_apattern, dither_coef05, dither_coef6B, name
    RKCFA_PATTERN_GRAY = (0x0000, 3, 0x0, 0x0, 0x0, "PtnGray")
    RKCFA_PATTERN_3X3_RGBGBRBRG = (0x1000, 0, 0x12264, 0x0, 0x0, "Ptn3x3RGBGBRBRG")
    RKCFA_PATTERN_3X3_GBRBRGRGB = (0x1001, 0, 0x24489, 0x0, 0x0, "Ptn3x3GBRBRGRGB")
    RKCFA_PATTERN_3x3_RBGGRBBGR = (0x1002, 0, 0x06858, 0x0, 0x0, "Ptn3x3RBGGRBBGR")
    RKCFA_PATTERN_2x2_BWGR = (0x2000, 2, 0x1E, 0x0, 0x0, "Ptn2x2BWGR")
    RKCFA_PATTERN_2x2_RGWB = (0x2001, 2, 0xB4, 0x0, 0x0, "Ptn2x2RGWB")
    RKCFA_PATTERN_2x6_GBBRRGRRGGBB = (0x3000, 1, 0xA50429, 0x0, 0x0, "Ptn2x6GBBRRGRRGGBB")
    RKCFA_PATTERN_UNKNOWN = (-1, 3, 0x0, 0x0, "PtnUnknown")


class CfaRegister(ModuleRegisterCore):
    def __init__(self, name: str = "CFA", platform: str = 'RK3572'):
        super().__init__(name, platform)

        self.config = CfaConfig(self.name)
        self.base_addr = 0x0
        self.update(platform=platform)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if "platform" in kwargs:
            self.platform = kwargs["platform"].upper()

        if self.platform.lower() == "rk3572":
            self.base_addr = 0x0
            self.nb_regs = 77  # 5 + 72
            self.regs = [Reg(0x00 + i * 4, 0x0, f"BCSH_LUT{i}") for i in range(72)] # 64/72 valid
            self.regs += [
                Reg(0x120, 0x0, "RKCFA_CTRL0"),
                Reg(0x124, 0x0, "APATTERN"),
                Reg(0x128, 0x0, "EDCOEF05"),
                Reg(0x12C, 0x0, "EDCOEF6B"),
                Reg(0x130, 0x0, "RKCFA_CTRL1"),
            ]
            return self.check_regs()
        else:
            self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def config2regs(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False
        cfg = self.config  # CfaConfig

        sw_cfa_bcsh_lut_en = int(
            cfg.nContrastGain != 64
            or cfg.nSaturationGain != 64
            or cfg.nLuminanceGain != 64
            or cfg.nStretchBlack != 0
            or cfg.nStretchWhite != 255
        )
        sw_cfa_midflt_en = cfg.bDeFalseColor4Gray & RM1
        sw_cfa_highpass_en = int(cfg.nSharpenGain != 64)
        sw_cfa_panel_mode = int(cfg.eCfaPattern > 0)  # if cfg.eCfaPattern >= 0 else int(cfg.ePlatform > 0)
        c2p_info = CfaC2pInfo(cfg.eCfaPattern)
        sw_cfa_c2p_id = c2p_info.value[1]
        sw_cfa_c2p_apattern = c2p_info.value[2]
        sw_cfa_dither_coef05 = c2p_info.value[3]
        sw_cfa_dither_coef6B = c2p_info.value[4]
        sw_cfa_r2y_mode = 1
        sw_cfa_r2y_clip = 0
        sw_cfa_sat_gain = min(cfg.nSaturationGain, 128)
        val = (
            0x1
            | (sw_cfa_bcsh_lut_en << 1)
            | (sw_cfa_midflt_en << 2)
            | (sw_cfa_highpass_en << 3)
            | (sw_cfa_panel_mode << 4)
            | (sw_cfa_c2p_id << 5)
            | (sw_cfa_r2y_mode << 8)
            | (sw_cfa_r2y_clip << 10)
            | (sw_cfa_sat_gain << 12)
        )
        self.set(name="RKCFA_CTRL0", value=val)
        sw_cfa_dither_en = int(cfg.bDither == 2)
        sw_cfa_modulate_lps_en = int(cfg.bA2Modulate >> 0) & RM1
        sw_cfa_modulate_hps_en = int(cfg.bA2Modulate >> 1) & RM1
        sw_cfa_modulate_err_en = int(cfg.bA2Modulate >> 2) & RM1
        sw_cfa_cfa_mode = cfg.eAlgoType & RM2
        if cfg.bClearLow4bits >= 0:
            sw_cfa_clr_low4bit_en = cfg.bClearLow4bits & RM1
        else:
            sw_cfa_clr_low4bit_en = int(cfg.eAlgoType != 1 and cfg.bDither != 1)
        sw_cfa_comps_en = int(cfg.nA2CompLevel > 0)
        sw_cfa_out_fmt = (cfg.eOutFormat - 10) & RM2
        sw_cfa_pat_out_en = 1
        sw_cfa_sharp_level = min(cfg.nSharpenGain, 128)
        sw_cfa_comps_level = min(cfg.nA2CompLevel, 128)
        val = (
            (sw_cfa_dither_en << 0)
            | (sw_cfa_modulate_lps_en << 1)
            | (sw_cfa_modulate_hps_en << 2)
            | (sw_cfa_modulate_err_en << 3)
            | (sw_cfa_cfa_mode << 4)
            | (sw_cfa_clr_low4bit_en << 6)
            | (sw_cfa_comps_en << 7)
            | (sw_cfa_out_fmt << 8)
            | (sw_cfa_pat_out_en << 10)
            | (sw_cfa_sharp_level << 16)
            | (sw_cfa_comps_level << 24)
        )
        self.set(name="RKCFA_CTRL1", value=val)
        self.set(name="APATTERN", value=sw_cfa_c2p_apattern)
        self.set(name="EDCOEF05", value=sw_cfa_dither_coef05)
        self.set(name="EDCOEF6B", value=sw_cfa_dither_coef6B)

        if sw_cfa_bcsh_lut_en:
            bcsh_lut = self.gen_lut()
        else:
            bcsh_lut = [i for i in range(256)]
        for i in range(64):
            j = i * 4
            val = bcsh_lut[j] | (bcsh_lut[j + 1] << 8) | (bcsh_lut[j + 2] << 16) | (bcsh_lut[j + 3] << 24)
            self.set(name=f"BCSH_LUT{i}", value=val)

        return True

    def regs2config(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False

        try:
            ## TODO: read regs and update config
            val = self.get(offset=0x00)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]  # get last erro stack
            self.logger.error(f"regs2config error in '{os.path.basename(tb.filename)}'-{tb.lineno}: {e}")
            return False
        return True

    def gen_lut(self) -> list[int]:
        ## TODO
        return [i for i in range(256)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    register = CfaRegister(platform=args.platform)

    if args.interface == "load":
        register.load(args.file)
    elif args.interface == "dump":
        register.dump(args.file)
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
        print(f"interface {args.interface} is not supported!")
        parser.print_help()

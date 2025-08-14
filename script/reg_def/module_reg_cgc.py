"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_cgc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-30
Description :
LastEditTime: 2025-08-12
"""

import os
import sys
import argparse
import traceback
import numpy as np
from enum import Enum

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def import *
from config_def import CgcConfig


class CgcModuleIndex(Enum):
    """enum = (name, ip_address, offset, nb_regs)"""

    VOP_HDRVIVID_S2H = ("VOP_HDRVIVID_S2H", 0xF9000000, 0x00002010, 253)  # 8 + 245
    VOP_HDRVIVID_CGC = ("VOP_HDRVIVID_CGC", 0xF9000000, 0x000020C0, 253)  # 8 + 245


class CgcRegister(ModuleRegisterCore):
    def __init__(
        self, name: str = "CGC", platform: str = 'RK3572', index: CgcModuleIndex = CgcModuleIndex.VOP_HDRVIVID_CGC
    ):
        super().__init__(name, platform)

        self.index = index
        self.config = CgcConfig(self.name)
        self.reg_dicts = {
            CgcModuleIndex.VOP_HDRVIVID_S2H: [],
            CgcModuleIndex.VOP_HDRVIVID_CGC: [],
        }  # CgcModuleIndex : list[Reg]
        self.base_addr = 0x0
        self.update(platform=platform)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if "platform" in kwargs:
            self.platform = kwargs["platform"].upper()
        if "index" in kwargs:
            index = kwargs["index"]
            self.index = index if isinstance(index, CgcModuleIndex) else CgcModuleIndex[index]

        if self.platform.lower() == "rk3572":
            self.ip_addr = self.index.value[1]
            self.base_addr = self.ip_addr + self.index.value[2] # 0xF9002010/0xF90020C0
            self.nb_regs = self.index.value[3]  # 253 = 8 + 245(69+3|6+2|6+42|117)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] = [
                Reg(0x00, 0x0, "SDR2HDR_CTRL"),
                Reg(0x04, 0x0, "SDR_CFG_COE0"),
                Reg(0x08, 0x0, "SDR_CFG_COE1"),
                Reg(0x0C, 0x0, "SDR_CSC_COE00_01"),
                Reg(0x10, 0x0, "SDR_CSC_COE02_10"),
                Reg(0x14, 0x0, "SDR_CSC_COE11_12"),
                Reg(0x18, 0x0, "SDR_CSC_COE20_21"),
                Reg(0x1C, 0x0, "SDR_CSC_COE22"),
            ]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] = [
                Reg(0x00, 0x0, "CGC_CTRL"),
                Reg(0x04, 0x0, "CGC_CFG_COE0"),
                Reg(0x08, 0x0, "CGC_CFG_COE1"),
                Reg(0x0C, 0x0, "CGC_CSC_COE00_01"),
                Reg(0x10, 0x0, "CGC_CSC_COE02_10"),
                Reg(0x14, 0x0, "CGC_CSC_COE11_12"),
                Reg(0x18, 0x0, "CGC_CSC_COE20_21"),
                Reg(0x1C, 0x0, "CGC_CSC_COE22"),
            ]
            # shift_tab, u13. total elements/regs: 137/69+3 (0xb00 - 0xc10)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] += [
                Reg(0x0A40 + idx * 4, 0x0, f"CGCINVGAMMA_CURVE{idx}") for idx in range(72)
            ]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] += [
                Reg(0x06F0 + idx * 4, 0x0, f"SDRINVGAMMA_CURVE{idx}") for idx in range(72)
            ]
            # start_idx, u11. total elements/regs: 11/6+2 (0xc20 - 0xc34)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] += [
                Reg(0x0B60 + idx * 4, 0x0, f"CGCINVGAMMA_STARTIDX{idx}") for idx in range(8)
            ]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] += [
                Reg(0x0810 + idx * 4, 0x0, f"SDRINVGAMMA_STARTIDX{idx}") for idx in range(8)
            ]
            # change_idx, u10. total elements/regs: 11/6+42 (0xc40 - 0xc54)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] += [
                Reg(0x0B80 + idx * 4, 0x0, f"CGCINVGAMMA_CHANGEIDX{idx}") for idx in range(48)
            ]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] += [
                Reg(0x0830 + idx * 4, 0x0, f"SDRINVGAMMA_CHANGEIDX{idx}") for idx in range(48)
            ]
            # oetf_tab, u32. total elements/regs: 117/117 (0xd00 - 0xed0)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] += [
                Reg(0x0C40 + idx * 4, 0x0, f"CGCOEFT_CURVE{idx}") for idx in range(117)
            ]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] += [
                Reg(0x08F0 + idx * 4, 0x0, f"SDROEFT_CURVE{idx}") for idx in range(117)
            ]

            self.regs = self.reg_dicts[self.index]
            return self.check_regs()
        else:
            self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def config2regs(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False
        cfg, param = self.config, self.config.cgc_params
        val = ((cfg.cgc_en & RM1) << 0)
        self.set(offset=0x00, value=val)
        val = ((param.log10_s_fix & RM12) << 0) | ((param.log10_r_ootf_fix & RM12) << 16)
        self.set(offset=0x04, value=val)
        val = (param.log10_t_fix_params & RM14) << 0
        self.set(offset=0x08, value=val)
        mat = param.Mat_R2R.flatten().astype(np.uint32)  # s16->u32 first
        val = ((mat[0] & RM16) << 0) | ((mat[1] & RM16) << 16)
        self.set(offset=0x0C, value=val)
        val = ((mat[2] & RM16) << 0) | ((mat[3] & RM16) << 16)
        self.set(offset=0x10, value=val)
        val = ((mat[4] & RM16) << 0) | ((mat[5] & RM16) << 16)
        self.set(offset=0x14, value=val)
        val = ((mat[6] & RM16) << 0) | ((mat[7] & RM16) << 16)
        self.set(offset=0x18, value=val)
        val = (mat[8] & RM16) << 0
        self.set(offset=0x1C, value=val)

        tab_offset = 0x0A40 if self.index == CgcModuleIndex.VOP_HDRVIVID_CGC else 0x06F0
        tab_u32 = param.eotf_diff_shift_tab.astype(np.uint32)  # u13->u32 first
        for i in range(137 // 2):  # [0,135]=>[0,67]
            j = i * 2
            val = (tab_u32[j] & RM13) | ((tab_u32[j + 1] & RM13) << 16)
            self.set(offset=tab_offset + i * 4, value=val)
        self.set(offset=tab_offset + 68 * 4, value=tab_u32[136] & RM13)  # 68th

        tab_offset = 0x0B60 if self.index == CgcModuleIndex.VOP_HDRVIVID_CGC else 0x0810
        tab_u32 = param.eotf_start_idx_tab.astype(np.uint32)  # u11->u32 first
        for i in range(11 // 2):  # [0,9]=>[0,4]
            j = i * 2
            val = (tab_u32[j] & RM11) | ((tab_u32[j + 1] & RM11) << 16)
            self.set(offset=tab_offset + i * 4, value=val)
        self.set(offset=tab_offset + 5 * 4, value=tab_u32[10] & RM11)  # 5th

        tab_offset = 0x0B80 if self.index == CgcModuleIndex.VOP_HDRVIVID_CGC else 0x0830
        tab_u32 = param.eotf_attbits_change_idx_tab.astype(np.uint32)  # u8->u32 first
        for i in range(11 // 2):  # [0,9]=>[0,4]
            j = i * 2
            val = (tab_u32[j] & RM8) | ((tab_u32[j + 1] & RM8) << 16)
            self.set(offset=tab_offset + i * 4, value=val)
        self.set(offset=tab_offset + 5 * 4, value=tab_u32[10] & RM8)  # 5th

        tab_offset = 0x0C40 if self.index == CgcModuleIndex.VOP_HDRVIVID_CGC else 0x08F0
        tab_u32 = param.cgc_oetf_tab.astype(np.uint32)  # u32->u32 first
        for i in range(117):  # [0,117]=>[0,117]
            self.set(offset=tab_offset + i * 4, value=tab_u32[i])
        return True

    def regs2config(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False

        try:
            val = self.get(offset=0x00)
            self.config.cgc_en = val & RM1
            self.config.sdr2hdr_enable = 0
            val = self.get(offset=0x04)
            self.config.cgc_params.log10_s_fix = (val >> 0) & RM12
            self.config.cgc_params.log10_r_ootf_fix = (val.astype(np.int32) >> 16) & RM12
            val = self.get(offset=0x08)
            self.config.cgc_params.log10_t_fix_params = (val >> 0) & RM14
            val = self.get(offset=0x0C)
            self.config.cgc_params.Mat_R2R[0][0] = ((val >> 0) & RM16).astype(np.int16)
            self.config.cgc_params.Mat_R2R[0][1] = ((val >> 16) & RM16).astype(np.int16)
            val = self.get(offset=0x10)
            self.config.cgc_params.Mat_R2R[0][2] = ((val >> 0) & RM16).astype(np.int16)
            self.config.cgc_params.Mat_R2R[1][0] = ((val >> 16) & RM16).astype(np.int16)
            val = self.get(offset=0x14)
            self.config.cgc_params.Mat_R2R[1][1] = ((val >> 0) & RM16).astype(np.int16)
            self.config.cgc_params.Mat_R2R[1][2] = ((val >> 16) & RM16).astype(np.int16)
            val = self.get(offset=0x18)
            self.config.cgc_params.Mat_R2R[2][0] = ((val >> 0) & RM16).astype(np.int16)
            self.config.cgc_params.Mat_R2R[2][1] = ((val >> 16) & RM16).astype(np.int16)
            val = self.get(offset=0x1C)
            self.config.cgc_params.Mat_R2R[2][2] = ((val >> 0) & RM16).astype(np.int16)

            tab_offset = 0x0A40 if self.index == CgcModuleIndex.VOP_HDRVIVID_CGC else 0x06F0
            for i in range(137 // 2):  # [0,135]=>[0,67]
                j = i * 2
                val = self.get(index=tab_offset + i * 4)
                self.config.cgc_params.eotf_diff_shift_tab[j] = (val >> 0) & RM13
                self.config.cgc_params.eotf_diff_shift_tab[j + 1] = (val >> 16) & RM13
            val = self.get(index=tab_offset + 68 * 4)
            self.config.cgc_params.eotf_diff_shift_tab[136] = (val >> 0) & RM13

            tab_offset = 0x0B60 if self.index == CgcModuleIndex.VOP_HDRVIVID_CGC else 0x0810
            for i in range(11 // 2):  # [0,9]=>[0,4]
                j = i * 2
                val = self.get(index=tab_offset + i * 4)
                self.config.cgc_params.eotf_start_idx_tab[j] = (val >> 0) & RM11
                self.config.cgc_params.eotf_start_idx_tab[j + 1] = (val >> 16) & RM11
            val = self.get(index=tab_offset + 5 * 4)
            self.config.cgc_params.eotf_start_idx_tab[10] = (val >> 0) & RM11

            tab_offset = 0x0B80 if self.index == CgcModuleIndex.VOP_HDRVIVID_CGC else 0x0830
            for i in range(11 // 2):  # [0,9]=>[0,4]
                val = self.get(index=tab_offset + i * 4)
                self.config.cgc_params.eotf_attbits_change_idx_tab[j] = (val >> 0) & RM8
                self.config.cgc_params.eotf_attbits_change_idx_tab[j + 1] = (val >> 16) & RM8
            val = self.get(index=tab_offset + 5 * 4)
            self.config.cgc_params.eotf_attbits_change_idx_tab[10] = (val >> 0) & RM8

            tab_offset = 0x0C40 if self.index == CgcModuleIndex.VOP_HDRVIVID_CGC else 0x08F0
            for i in range(117):  # [0,117]=>[0,117]
                self.config.cgc_params.cgc_oetf_tab[i] = self.get(index=tab_offset + i * 4)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]  # get last erro stack
            self.logger.error(f"regs2config error in '{os.path.basename(tb.filename)}'-{tb.lineno}: {e}")
            return False
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3538...")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    register = CgcRegister(platform=args.platform)

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

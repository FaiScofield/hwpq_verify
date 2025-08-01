"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_cgc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-30
Description :
LastEditTime: 2025-07-30
"""

import os
import sys
import argparse
import traceback
import numpy as np
from enum import Enum

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def import ModuleRegisterCore, Reg
from config_def import CgcConfig


class CgcModuleIndex(Enum):
    """enum = (name, ip_address, offset, nb_regs)"""

    VOP_HDRVIVID_S2H = ("VOP_HDRVIVID_S2H", 0xF90000000, 0x00002010, 206)
    VOP_HDRVIVID_CGC = ("VOP_HDRVIVID_CGC", 0xF90000000, 0x000020C0, 206)


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
            self.platform = kwargs["platform"]
        if "index" in kwargs:
            index = kwargs["index"]
            self.index = index if isinstance(index, CgcModuleIndex) else CgcModuleIndex[index]

        if self.platform.lower() == "rk3572":
            self.ip_addr = self.index.value[1]
            self.base_addr = self.index.value[2]
            self.nb_regs = self.index.value[3] # 206 = 8 + (69) + (6) + (6) + (117)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] = [
                Reg(0x00002010, 0x0, "SDR2HDR_CTRL"),
                Reg(0x00002014, 0x0, "SDR_CFG_COE0"),
                Reg(0x00002018, 0x0, "SDR_CFG_COE1"),
                Reg(0x0000201C, 0x0, "SDR_CSC_COE00_01"),
                Reg(0x00002020, 0x0, "SDR_CSC_COE02_10"),
                Reg(0x00002024, 0x0, "SDR_CSC_COE11_12"),
                Reg(0x00002028, 0x0, "SDR_CSC_COE20_21"),
                Reg(0x0000202C, 0x0, "SDR_CSC_COE22"),
            ]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] = [
                Reg(0x000020C0, 0x0, "CGC_CTRL"),
                Reg(0x000020C4, 0x0, "CGC_CFG_COE0"),
                Reg(0x000020C8, 0x0, "CGC_CFG_COE1"),
                Reg(0x000020CC, 0x0, "CGC_CSC_COE00_01"),
                Reg(0x000020D0, 0x0, "CGC_CSC_COE02_10"),
                Reg(0x000020D4, 0x0, "CGC_CSC_COE11_12"),
                Reg(0x000020D8, 0x0, "CGC_CSC_COE20_21"),
                Reg(0x000020DC, 0x0, "CGC_CSC_COE22"),
            ]
            # shift_tab, u13. total elements/regs: 137/69 (0xb00 - 0xc10)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] += [Reg(0x00002B00 + idx * 4, 0x0, f"CGCINVGAMMA_CURVE{idx}") for idx in range(69)]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] += [Reg(0x00002700 + idx * 4, 0x0, f"SDRINVGAMMA_CURVE{idx}") for idx in range(69)]
            # start_idx, u11. total elements/regs: 11/6 (0xc20 - 0xc34)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] += [Reg(0x00002C20 + idx * 4, 0x0, f"CGCINVGAMMA_STARTIDX{idx}") for idx in range(6)]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] += [Reg(0x00002820 + idx * 4, 0x0, f"SDRINVGAMMA_STARTIDX{idx}") for idx in range(6)]
            # change_idx, u10. total elements/regs: 11/6 (0xc40 - 0xc54)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] += [Reg(0x00002C40 + idx * 4, 0x0, f"CGCINVGAMMA_CHANGEIDX{idx}") for idx in range(6)]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] += [Reg(0x00002840 + idx * 4, 0x0, f"SDRINVGAMMA_CHANGEIDX{idx}") for idx in range(6)]
            # oetf_tab, u32. total elements/regs: 117/117 (0xd00 - 0xed0)
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_CGC] += [Reg(0x00002D00 + idx * 4, 0x0, f"CGCOEFT_CURVE{idx}") for idx in range(117)]
            self.reg_dicts[CgcModuleIndex.VOP_HDRVIVID_S2H] += [Reg(0x00002900 + idx * 4, 0x0, f"SDROEFT_CURVE{idx}") for idx in range(117)]

            self.regs = self.reg_dicts[self.index]
            assert len(self.regs) == self.nb_regs
            return True
        else:
            self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def config2regs(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False
        cfg, param = self.config, self.config.cgc_params
        val = (cfg.cgc_en & 0x1) << 0
        self.set(name="CGC_CTRL", value=val)
        val = ((param.log10_s_fix & 0xFFF) << 0) | ((param.log10_r_ootf_fix & 0xFFF) << 16)
        self.set(name="CGC_CFG_COE0", value=val)
        val = (param.log10_t_fix_params & 0x3FFF) << 0
        self.set(name="CGC_CFG_COE1", value=val)
        mat = param.Mat_R2R.flatten().astype(np.uint32)
        val = ((mat[0] & 0xFFFF) << 0) | ((mat[1] & 0xFFFF) << 16)
        self.set(name="CGC_CSC_COE00_01", value=val)
        val = ((mat[2] & 0xFFFF) << 0) | ((mat[3] & 0xFFFF) << 16)
        self.set(name="CGC_CSC_COE02_10", value=val)
        val = ((mat[4] & 0xFFFF) << 0) | ((mat[5] & 0xFFFF) << 16)
        self.set(name="CGC_CSC_COE11_12", value=val)
        val = ((mat[6] & 0xFFFF) << 0) | ((mat[7] & 0xFFFF) << 16)
        self.set(name="CGC_CSC_COE20_21", value=val)
        val = (mat[8] & 0xFFFF) << 0
        self.set(name="CGC_CSC_COE22", value=val)
        for i in range(137 // 2):  # [0,135]=>[0,67]
            j = i * 2
            val = (param.eotf_diff_shift_tab[j] & 0x1FFF) | ((param.eotf_diff_shift_tab[j + 1] & 0x1FFF) << 16)
            self.set(name=f"CGCINVGAMMA_CURVE{i}", value=val)
        val = param.eotf_diff_shift_tab[136] & 0x1FFF
        self.set(name="CGCINVGAMMA_CURVE68", value=val)  # 68th
        for i in range(11 // 2):  # [0,9]=>[0,4]
            j = i * 2
            val = (param.eotf_start_idx_tab[j] & 0x7FF) | ((param.eotf_start_idx_tab[j + 1] & 0x7FF) << 16)
            self.set(name=f"CGCINVGAMMA_STARTIDX{i}", value=val)
            val = (param.eotf_attbits_change_idx_tab[j] & 0x3FF) | (
                (param.eotf_attbits_change_idx_tab[j + 1] & 0x3FF) << 16
            )
            self.set(name=f"CGCINVGAMMA_CHANGEIDX{i}", value=val)
        val = param.eotf_start_idx_tab[10] & 0x7FF
        self.set(name="CGCINVGAMMA_STARTIDX5", value=val)  # 5th
        val = param.eotf_attbits_change_idx_tab[10] & 0x3FF
        self.set(name="CGCINVGAMMA_CHANGEIDX5", value=val)  # 5th
        for i in range(117):  # [0,117]=>[0,117]
            self.set(name=f"CGCOEFT_CURVE{i}", value=param.cgc_oetf_tab[i])
        return True

    def regs2config(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False

        try:
            val = self.get(name="CGC_CTRL")
            self.config.cgc_en = val & 0x1
            self.config.sdr2hdr_enable = 0
            val = self.get(name="CGC_CFG_COE0")
            self.config.cgc_params.log10_s_fix = (val >> 0) & 0xFFF
            self.config.cgc_params.log10_r_ootf_fix = (val.astype(np.int32) >> 16) & 0xFFF
            val = self.get(name="CGC_CFG_COE1")
            self.config.cgc_params.log10_t_fix_params = (val >> 0) & 0x3FFF
            val = self.get(name="CGC_CSC_COE00_01")
            self.config.cgc_params.Mat_R2R[0][0] = ((val >> 0) & 0xFFFF).astype(np.int16)
            self.config.cgc_params.Mat_R2R[0][1] = ((val >> 16) & 0xFFFF).astype(np.int16)
            val = self.get(name="CGC_CSC_COE02_10")
            self.config.cgc_params.Mat_R2R[0][2] = ((val >> 0) & 0xFFFF).astype(np.int16)
            self.config.cgc_params.Mat_R2R[1][0] = ((val >> 16) & 0xFFFF).astype(np.int16)
            val = self.get(name="CGC_CSC_COE11_12")
            self.config.cgc_params.Mat_R2R[1][1] = ((val >> 0) & 0xFFFF).astype(np.int16)
            self.config.cgc_params.Mat_R2R[1][2] = ((val >> 16) & 0xFFFF).astype(np.int16)
            val = self.get(name="CGC_CSC_COE20_21")
            self.config.cgc_params.Mat_R2R[2][0] = ((val >> 0) & 0xFFFF).astype(np.int16)
            self.config.cgc_params.Mat_R2R[2][1] = ((val >> 16) & 0xFFFF).astype(np.int16)
            val = self.get(name="CGC_CSC_COE22")
            self.config.cgc_params.Mat_R2R[2][2] = ((val >> 0) & 0xFFFF).astype(np.int16)
            for i in range(137 // 2):  # [0,135]=>[0,67]
                j = i * 2
                val = self.get(name=f"CGCINVGAMMA_CURVE{i}")
                self.config.cgc_params.eotf_diff_shift_tab[j] = (val >> 0) & 0x1FFF
                self.config.cgc_params.eotf_diff_shift_tab[j + 1] = (val >> 16) & 0x1FFF
            val = self.get(name=f"CGCINVGAMMA_CURVE68")
            self.config.cgc_params.eotf_diff_shift_tab[136] = (val >> 0) & 0x1FFF
            for i in range(11 // 2):  # [0,9]=>[0,4]
                j = i * 2
                val = self.get(name=f"CGCINVGAMMA_STARTIDX{i}")
                self.config.cgc_params.eotf_start_idx_tab[j] = (val >> 0) & 0x7FF
                self.config.cgc_params.eotf_start_idx_tab[j + 1] = (val >> 16) & 0x7FF
                val = self.get(name=f"CGCINVGAMMA_CHANGEIDX{i}")
                self.config.cgc_params.eotf_attbits_change_idx_tab[j] = (val >> 0) & 0x3FF
                self.config.cgc_params.eotf_attbits_change_idx_tab[j + 1] = (val >> 16) & 0x3FF
            val = self.get(name="CGCINVGAMMA_STARTIDX5")
            self.config.cgc_params.eotf_start_idx_tab[10] = (val >> 0) & 0x7FF
            val = self.get(name="CGCINVGAMMA_CHANGEIDX5")
            self.config.cgc_params.eotf_attbits_change_idx_tab[10] = (val >> 0) & 0x3FF
            for i in range(117):  # [0,117]=>[0,117]
                self.config.cgc_params.cgc_oetf_tab[i] = self.get(name=f"CGCOEFT_CURVE{i}")
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]  # get last erro stack
            lineno = tb.lineno
            filename = os.path.basename(tb.filename)
            self.logger.error(f"regs2config error in {filename}:{lineno}: {e}")
            return False
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    register = CgcRegister()

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

"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_sharp_lite.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-08-05
"""

import os
import sys
import argparse
import numpy as np

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def.module_reg_core import ModuleRegisterCore, Reg
from config_def.module_config_sharp_lite import SharpLiteConfig


class SharpRegister(ModuleRegisterCore):
    def __init__(self, name: str = "SHARP", platform: str = 'RK3572'):
        super().__init__(name, platform)

        self.config = SharpLiteConfig(self.name)
        self.base_addr = 0x0
        self.update(platform=platform)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if self.platform.lower() == "rk3572":
            self.base_addr = 0xF9000000
            self.nb_regs = 14
            self.regs = [
                Reg(0x00006C00, 0x0, "ENABLE_CTRL"),
                Reg(0x00006C04, 0x0, "GATING_CTRL"),
                Reg(0x00006C08, 0x0, "RESERVED_08"),
                Reg(0x00006C0C, 0x0, "RESERVED_0C"),
                Reg(0x00006C10, 0x0, "USM_CTRL"),
                Reg(0x00006C14, 0x0, "USM_COEF"),
                Reg(0x00006C18, 0x0, "RESERVED_18"),
                Reg(0x00006C1C, 0x0, "RESERVED_1C"),
                Reg(0x00006C20, 0x0, "SHOOT_CTRL_REG0"),
                Reg(0x00006C24, 0x0, "SHOOT_CTRL_REG1"),
                Reg(0x00006C28, 0x0, "SHOOT_CTRL_REG2"),
                Reg(0x00006C2C, 0x0, "ROI_CTRL0"),
                Reg(0x00006C30, 0x0, "ROI_CTRL1"),
                Reg(0x00006C34, 0x0, "INK_CTRL"),
            ]
            assert len(self.regs) == self.nb_regs
            return True
        else:  # RK3576, RK3538
            self.base_addr = 0x27D06C00
            self.nb_regs = 172
            self.regs = [Reg(0x27D06C00, 0x0, "CTRL"), Reg(0x27D06C04, 0x000007FE, "AUTO_GATING_IMD")]  # 2
            self.regs += [Reg(0x27D06C04 + i * 4, 0x0, f"PEAKING_FILTER_COE{i}") for i in range(10)]  # 10
            self.regs += [
                Reg(0x27D06C30 + i * 4, 0x0, f"PEAKING{i}_CTRL_COE{j}") for i in range(8) for j in range(11)
            ]  # 8x11==88
            self.regs += [Reg(0x27D06D90 + i * 4, 0x0, f"PEAKING_CTRL{i}") for i in range(10)]  # 10
            self.regs += [Reg(0x27D06DB8 + i * 4, 0x0, f"SHOOT_CTRL{i}") for i in range(2)]  # 2
            self.regs += [Reg(0x27D06DC0 + i * 4, 0x0, f"GAIN_CTRL{i}") for i in range(16)]  # 16
            self.regs += [Reg(0x27D06E30 + i * 4, 0x0, f"COLORADJ_CTRL{i}") for i in range(16)]  # 16
            self.regs += [Reg(0x27D06E70 + i * 4, 0x0, f"TEXTURE_CTRL{i}") for i in range(6)]  # 6
            self.regs += [Reg(0x27D06E88 + i * 4, 0x0, f"LTI_CTRL{i}") for i in range(4)]  # 4
            self.regs += [Reg(0x27D06E98 + i * 4, 0x0, f"CTI_CTRL{i}") for i in range(4)]  # 4
            self.regs += [
                Reg(0x27D06EA8, 0x0, f"INK_CTRL0"),
                Reg(0x27D06EAC, 0x0, f"ROI_CTRL0"),
                Reg(0x27D06EB0, 0x0, f"ROI_CTRL1"),
            ]  # 3
            assert len(self.regs) == self.nb_regs
            return True
        # else:
        #     self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def config2regs_lite(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False
        cfg = self.config
        self.set(name="ENABLE_CTRL", value=(cfg.i_sharp_lite_en & 0x1) | ((cfg.i_shoot_ctrl_en & 0x1) << 1))
        self.set(name="GATING_CTRL", value=0x0)
        self.set(name="RESERVED_08", value=0x0)
        self.set(name="RESERVED_0C", value=0x0)
        self.set(name="USM_CTRL", value=(cfg.i_sharp_usm_gain & 0x3FF) | ((cfg.f_usm_coring_thr & 0x7F) << 16))
        self.set(
            name="USM_COEF",
            value=(cfg.i_sharp_core_A & 0xFF)
            | ((cfg.i_sharp_core_B & 0xFF) << 8)
            | ((cfg.i_sharp_core_C & 0xFF) << 16),
        )
        self.set(name="RESERVED_18", value=0x0)
        self.set(name="RESERVED_1C", value=0x0)
        self.set(name="SHOOT_CTRL_REG0", value=(cfg.i_shoot_ctrl_delta_offset & 0xFF))
        self.set(
            name="SHOOT_CTRL_REG1", value=(cfg.i_shoot_ctrl_pos & 0x7F) | ((cfg.i_shoot_ctrl_pos_unlimit & 0x7F) << 16)
        )
        self.set(
            name="SHOOT_CTRL_REG2", value=(cfg.i_shoot_ctrl_neg & 0x7F) | ((cfg.i_shoot_ctrl_neg_unlimit & 0x7F) << 16)
        )
        self.set(
            name="ROI_CTRL0",
            value=(cfg.i_sharp_roi_xstart & 0xFFF)
            | ((cfg.i_sharp_roi_ystart & 0xFFF) << 16)
            | ((cfg.i_sharp_roi_enable & 0x1) << 31),
        )
        self.set(name="ROI_CTRL1", value=(cfg.i_sharp_roi_xend & 0xFFF) | ((cfg.i_sharp_roi_yend & 0xFFF) << 16))
        self.set(name="INK_CTRL", value=(cfg.i_ink_mode & 0xF) | ((cfg.i_ink_enable & 0x1) << 31))
        return True

    def regs2config_lite(self) -> bool:
        val = self.get(name="ENABLE_CTRL")
        self.config.i_sharp_lite_en = (val >> 0) & 0x1
        self.config.i_shoot_ctrl_en = (val >> 1) & 0x1
        val = self.get(name="USM_CTRL")
        self.config.i_sharp_usm_gain = (val >> 0) & 0x3FF
        self.config.f_usm_coring_thr = (val >> 16) & 0x7F
        val = self.get(name="USM_COEF")
        self.config.i_sharp_core_A = int(val >> 0) & 0xFF
        self.config.i_sharp_core_B = int(val >> 8) & 0xFF
        self.config.i_sharp_core_C = int(val >> 16) & 0xFF
        val = self.get(name="SHOOT_CTRL_REG0")
        self.config.i_shoot_ctrl_delta_offset = val & 0x7F
        val = self.get(name="SHOOT_CTRL_REG1")
        self.config.i_shoot_ctrl_pos = (val >> 0) & 0x7F
        self.config.i_shoot_ctrl_pos_unlimit = (val >> 16) & 0x7F
        val = self.get(name="SHOOT_CTRL_REG2")
        self.config.i_shoot_ctrl_neg = (val >> 0) & 0x7F
        self.config.i_shoot_ctrl_neg_unlimit = (val >> 16) & 0x7F
        val = self.get(name="ROI_CTRL0")
        self.config.i_sharp_roi_xstart = (val >> 0) & 0xFFF
        self.config.i_sharp_roi_xend = (val >> 16) & 0xFFF
        self.config.i_sharp_roi_enable = (val >> 31) & 0x1
        val = self.get(name="ROI_CTRL1")
        self.config.i_sharp_roi_xend = (val >> 0) & 0xFFF
        self.config.i_sharp_roi_yend = (val >> 16) & 0xFFF
        # TODO: parse INK_CTRL register
        val = self.get(name="INK_CTRL")
        self.config.i_ink_mode = (val >> 0) & 0xF
        self.config.i_ink_enable = (val >> 31) & 0x1
        return True

    def config2regs_full(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False
        cfg = self.config.s_sharp_en_ctrl
        val = (
            (self.config.i_EnabledSharpen & 0x1)
            | (((cfg.i_lti_h_en | cfg.i_lti_v_en) & 0x1) << 1)
            | (((cfg.i_cti_h_en | cfg.i_cti_v_en) & 0x1) << 2)
            | ((cfg.i_peaking_en & 0x1) << 3)
            | (((cfg.i_peaking_gain_en | cfg.i_peaking_coring_en | cfg.i_peaking_limit_ctrl_en) & 0x1) << 4)
            | ((cfg.i_peaking_shoot_ctrl_en & 0x1) << 5)
            | ((cfg.i_peaking_edge_ctrl_en & 0x1) << 6)
            # | ((cfg.i_peaking_edge_shoot_ctr & 0x1) << 1)
            | ((cfg.i_shoot_ctrl_en & 0x1) << 7)
            | ((cfg.i_global_gain_en & 0x1) << 8)
            | ((cfg.i_color_adj_en & 0x1) << 9)
            | ((cfg.i_texture_adj_en & 0x1) << 10)
        )
        self.set(name="CTRL", value=val)

        cfg = self.config.s_sharp_hw_config
        val = (
            ((cfg.lti_gating_en & 0x1) << 1)
            | ((cfg.cti_gating_en & 0x1) << 2)
            | ((cfg.peaking_gating_en & 0x1) << 3)
            | ((cfg.peaking_ctrl_gating_en & 0x1) << 4)
            | ((cfg.peaking_shoot_ctrl_gating_en & 0x1) << 5)
            | ((cfg.edge_proc_gating_en & 0x1) << 6)
            | ((cfg.shoot_ctrl_gating_en & 0x1) << 7)
            | ((cfg.gain_ctrl_gating_en & 0x1) << 8)
            | ((cfg.color_adj_gating_en & 0x1) << 9)
            | ((cfg.texture_adj_gating_en & 0x1) << 10)
        )
        self.set(name="AUTO_GATING_IMD", value=val)

        cfg = self.config.s_peaking
        val = (
            ((cgc.t_filt_core_V0[0] & 0xF) << 0)
            | ((cgc.t_filt_core_V0[1] & 0xF) << 4)
            | ((cgc.t_filt_core_V0[2] & 0xF) << 8)
            | ((cgc.t_filt_core_V1[0] & 0xF) << 12)
            | ((cgc.t_filt_core_V1[1] & 0xF) << 16)
            | ((cgc.t_filt_core_V1[2] & 0xF) << 20)
        )
        self.set(name=f"PEAKING_FILTER_COE0", value=val)
        val = (
            ((cgc.t_filt_core_V2[0] & 0xF) << 0)
            | ((cgc.t_filt_core_V2[1] & 0xF) << 4)
            | ((cgc.t_filt_core_V2[2] & 0xF) << 8)
            | ((cgc.t_filt_core_USM[0] & 0xF) << 12)
            | ((cgc.t_filt_core_USM[1] & 0xF) << 16)
            | ((cgc.t_filt_core_USM[2] & 0xF) << 20)
            | ((cgc.i_diag_enh_coef & 0x7) << 24)
        )
        self.set(name=f"PEAKING_FILTER_COE1", value=val)
        tab = cgc.t_filt_core_H0 + cgc.t_filt_core_H1 + cgc.t_filt_core_H2 + cfg.t_filt_core_H3
        for i in range(2, 10, 2):
            j = i * 6
            val = ((tab[j] & 0x1F) << 0) | ((tab[j + 1] & 0x7F) << 8) | ((tab[j + 2] & 0x1FF) << 16)
            self.set(name=f"PEAKING_FILTER_COE{i}", value=val)
            val = ((tab[j + 3] & 0x3FF) << 0) | ((tab[j + 4] & 0x7FF) << 10) | ((tab[j + 5] & 0x3FF) << 21)
            self.set(name=f"PEAKING_FILTER_COE{i+1}", value=val)

        # tab = cgc.t_filt_core_H0 + cgc.t_filt_core_H1 + cgc.t_filt_core_H2 + cfg.t_filt_core_H3
        for i in range(8):
            if self.config.s_sharp_en_ctrl.i_peaking_coring_en:
                coring_ratio = cfg.t_CoringRatio[i]
                coring_zero = cfg.t_CoringZero[i]
                coring_thr = cfg.t_CoringThreshold[i]
            else:
                coring_ratio = 1024
                coring_zero = 0
                coring_thr = 0
            if self.config.s_sharp_en_ctrl.i_peaking_gain_en:
                gain_ctrl_pos 	= cfg.t_GainPos[i]
                gain_ctrl_neg 	= cfg.t_GainNeg[i]
            else:
                gain_ctrl_pos 	= 1024
                gain_ctrl_neg 	= 1024
            if self.config.s_sharp_en_ctrl.i_peaking_limit_ctrl_en:
                limit_ctrl_p0 		= cfg.t_LimitPos0[i]
                limit_ctrl_p1 		= cfg.t_LimitPos1[i]
                limit_ctrl_n0 		= cfg.t_LimitNeg0[i]
                limit_ctrl_n1 		= cfg.t_LimitNeg1[i]
                limit_ctrl_ratio 	= cfg.t_LimitRatio[i]
            else:
                limit_ctrl_p0 		= 1023
                limit_ctrl_p1 		= 1023
                limit_ctrl_n0 		= 1023
                limit_ctrl_n1 		= 1023
                limit_ctrl_ratio 	= 1024

            peaking_ctrl_idx_P0[i] =  coring_zero
            peaking_ctrl_idx_N0[i] = -coring_zero
            peaking_ctrl_idx_P1[i] =  coring_thr
            peaking_ctrl_idx_N1[i] = -coring_thr
            peaking_ctrl_idx_P2[i] =  limit_ctrl_p0
            peaking_ctrl_idx_N2[i] = -limit_ctrl_n0
            peaking_ctrl_idx_P3[i] =  limit_ctrl_p1
            peaking_ctrl_idx_N3[i] = -limit_ctrl_n1

            ratio_pos_tmp = (coring_ratio * gain_ctrl_pos + 512) >> 10
            ratio_neg_tmp = (coring_ratio * gain_ctrl_neg + 512) >> 10
            peaking_ctrl_value_P1[i] =  ((ratio_pos_tmp * (coring_thr - coring_zero) + 512) >> 10)
            peaking_ctrl_value_N1[i] = -((ratio_neg_tmp * (coring_thr - coring_zero) + 512) >> 10)
            peaking_ctrl_ratio_P01[i] = ratio_pos_tmp
            peaking_ctrl_ratio_N01[i] = ratio_neg_tmp
            peaking_ctrl_ratio_P12[i] = gain_ctrl_pos
            peaking_ctrl_ratio_N12[i] = gain_ctrl_neg

            peaking_ctrl_add_tmp = (gain_ctrl_pos * (limit_ctrl_p0 - coring_thr) + 512) >> 10
            peaking_ctrl_value_P2[i] = peaking_ctrl_value_P1[i] + peaking_ctrl_add_tmp
            peaking_ctrl_add_tmp = (gain_ctrl_neg * (limit_ctrl_n0 - coring_thr) + 512) >> 10
            peaking_ctrl_value_N2[i] = peaking_ctrl_value_N1[i] - peaking_ctrl_add_tmp

            ratio_pos_tmp = (limit_ctrl_ratio * gain_ctrl_pos + 512) >> 10
            ratio_neg_tmp = (limit_ctrl_ratio * gain_ctrl_neg + 512) >> 10

            peaking_ctrl_add_tmp = (ratio_pos_tmp * (limit_ctrl_p1 - limit_ctrl_p0) + 512) >> 10
            peaking_ctrl_value_P3[i] = peaking_ctrl_value_P2[i] + peaking_ctrl_add_tmp
            peaking_ctrl_add_tmp = (ratio_neg_tmp * (limit_ctrl_n1 - limit_ctrl_n0) + 512) >> 10
            peaking_ctrl_value_N3[i] = peaking_ctrl_value_N2[i] - peaking_ctrl_add_tmp
            peaking_ctrl_ratio_P23[i] = ratio_pos_tmp
            peaking_ctrl_ratio_N23[i] = ratio_neg_tmp

            peaking_ctrl_idx_N0[i] = clamp(peaking_ctrl_idx_N0[i], -1024, 1023)
            peaking_ctrl_idx_N1[i] = clamp(peaking_ctrl_idx_N1[i], -1024, 1023)
            peaking_ctrl_idx_N2[i] = clamp(peaking_ctrl_idx_N2[i], -1024, 1023)
            peaking_ctrl_idx_N3[i] = clamp(peaking_ctrl_idx_N3[i], -1024, 1023)
            peaking_ctrl_idx_P0[i] = clamp(peaking_ctrl_idx_P0[i], -1024, 1023)
            peaking_ctrl_idx_P1[i] = clamp(peaking_ctrl_idx_P1[i], -1024, 1023)
            peaking_ctrl_idx_P2[i] = clamp(peaking_ctrl_idx_P2[i], -1024, 1023)
            peaking_ctrl_idx_P3[i] = clamp(peaking_ctrl_idx_P3[i], -1024, 1023)

            peaking_ctrl_value_N1[i] = clamp(peaking_ctrl_value_N1[i], -1024, 1023)
            peaking_ctrl_value_N2[i] = clamp(peaking_ctrl_value_N2[i], -1024, 1023)
            peaking_ctrl_value_N3[i] = clamp(peaking_ctrl_value_N3[i], -1024, 1023)
            peaking_ctrl_value_P1[i] = clamp(peaking_ctrl_value_P1[i], -1024, 1023)
            peaking_ctrl_value_P2[i] = clamp(peaking_ctrl_value_P2[i], -1024, 1023)
            peaking_ctrl_value_P3[i] = clamp(peaking_ctrl_value_P3[i], -1024, 1023)

            peaking_ctrl_ratio_P01[i] = clamp(peaking_ctrl_ratio_P01[i], 0, 4095)
            peaking_ctrl_ratio_P12[i] = clamp(peaking_ctrl_ratio_P12[i], 0, 4095)
            peaking_ctrl_ratio_P23[i] = clamp(peaking_ctrl_ratio_P23[i], 0, 4095)
            peaking_ctrl_ratio_N01[i] = clamp(peaking_ctrl_ratio_N01[i], 0, 4095)
            peaking_ctrl_ratio_N12[i] = clamp(peaking_ctrl_ratio_N12[i], 0, 4095)
            peaking_ctrl_ratio_N23[i] = clamp(peaking_ctrl_ratio_N23[i], 0, 4095)

            for j in range(11):
                val = 0x0
                self.set(name=f"PEAKING{i}_CTRL_COE{j}", value=val)
        for i in range(10):
            val = 0x0
            self.set(name=f"PEAKING_CTRL{i}", value=val)
        val = 0x0
        self.set(name=f"SHOOT_CTRL0", value=val)
        self.set(name=f"SHOOT_CTRL1", value=val)
        for i in range(16):
            val = 0x0
            self.set(name=f"GAIN_CTRL{i}", value=val)
            self.set(name=f"COLORADJ_CTRL{i}", value=val)
        for i in range(6):
            val = 0x0
            self.set(name=f"TEXTURE_CTRL{i}", value=val)
        for i in range(4):
            val = 0x0
            self.set(name=f"LTI_CTRL{i}", value=val)
            self.set(name=f"CTI_CTRL{i}", value=val)

        self.set(name="INK_CTRL0", value=(cfg.i_ink_mode & 0xF) | ((cfg.i_ink_enable & 0x1) << 31))
        self.set(
            name="ROI_CTRL0",
            value=(cfg.i_sharp_roi_xstart & 0xFFF)
            | ((cfg.i_sharp_roi_ystart & 0xFFF) << 16)
            | ((cfg.i_sharp_roi_enable & 0x1) << 31),
        )
        self.set(name="ROI_CTRL1", value=(cfg.i_sharp_roi_xend & 0xFFF) | ((cfg.i_sharp_roi_yend & 0xFFF) << 16))
        return True

    def regs2config_full(self) -> bool:
        # TODO:
        return False

    def config2regs(self) -> bool:
        if self.platform.lower() == "rk3572":
            return self.config2regs_lite()
        return self.config2regs_full()

    def regs2config(self) -> bool:
        if self.platform.lower() == "rk3572":
            return self.regs2config_lite()
        return self.regs2config_full()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    register = SharpRegister()
    register.set(name="ENABLE_CTRL", value=0x1)
    register.set(name="USM_CTRL", value=0x300)
    register.set(name="USM_COEF", value=0x10 | (0x20 << 8) | (0x30 << 16))

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
        print(f"interface '{args.interface}' is not supported!")
        parser.print_help()

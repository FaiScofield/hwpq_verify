"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_sharp_lite.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-08-06
"""

import os
import sys
import argparse
import traceback
import numpy as np

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def.module_reg_core import *
from config_def import SharpLiteConfig, SharpConfig
from utils import clamp


class SharpRegister(ModuleRegisterCore):
    def __init__(self, name: str = "SHARP", platform: str = 'RK3572'):
        super().__init__(name, platform)

        self.config = SharpLiteConfig(self.name)
        self.base_addr = 0x0
        self.update(platform=platform)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if "platform" in kwargs:
            self.platform = kwargs["platform"].upper()
        self.logger.info(f"updating register type with platform: {self.platform}")
        if self.platform == "RK3572":
            self.config = SharpLiteConfig(self.name)
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
            return self.check_regs()
        else:  # RK3576, RK3538
            self.config = SharpConfig(self.name)
            self.base_addr = 0x27D00000
            self.nb_regs = 173
            self.regs = [Reg(0x00006C00, 0x0, "CTRL"), Reg(0x00006C04, 0x000007FE, "AUTO_GATING_IMD")]  # 2
            self.regs += [Reg(0x00006C08 + i * 4, 0x0, f"PEAKING_FILTER_COE{i}") for i in range(10)]  # 10
            self.regs += [
                Reg(0x00006C30 + i * 11 * 4 + j * 4, 0x0, f"PEAKING{i}_CTRL_COE{j}") for i in range(8) for j in range(11)
            ]  # 8x11==88
            self.regs += [Reg(0x00006D90 + i * 4, 0x0, f"PEAKING_CTRL{i}") for i in range(10)]  # 10
            self.regs += [Reg(0x00006DB8 + i * 4, 0x0, f"SHOOT_CTRL{i}") for i in range(2)]  # 2
            self.regs += [Reg(0x00006DC0 + i * 4, 0x0, f"GAIN_CTRL{i}") for i in range(4)]  # 4
            self.regs += [Reg(0x00006DD0 + i * 4, 0x0, f"RESERVED{i}") for i in range(12)]  # 12 reserved regs
            self.regs += [Reg(0x00006E00 + i * 4, 0x0, f"GAIN_CTRL{i+4}") for i in range(12)]  # 12
            self.regs += [Reg(0x00006E30 + i * 4, 0x0, f"COLORADJ_CTRL{i}") for i in range(16)]  # 16
            self.regs += [Reg(0x00006E70 + i * 4, 0x0, f"TEXTURE_CTRL{i}") for i in range(6)]  # 6
            self.regs += [Reg(0x00006E88 + i * 4, 0x0, f"LTI_CTRL{i}") for i in range(4)]  # 4
            self.regs += [Reg(0x00006E98 + i * 4, 0x0, f"CTI_CTRL{i}") for i in range(4)]  # 4
            self.regs += [
                Reg(0x00006EA8, 0x0, f"INK_CTRL0"),
                Reg(0x00006EAC, 0x0, f"ROI_CTRL0"),
                Reg(0x00006EB0, 0x0, f"ROI_CTRL1"),
            ]  # 3
            return self.check_regs()
        # else:
        #     self.logger.error(f"Platform {self.platform} is not supported now!")
        # return False

    def config2regs_lite(self) -> bool:
        if self.platform not in ["RK3572"]:
            self.logger.error(f"current registers type is not fit for platform {self.platform}!")
            return False
        cfg = self.config
        self.set(name="ENABLE_CTRL", value=(cfg.i_sharp_lite_en & RM1) | ((cfg.i_shoot_ctrl_en & RM1) << 1))
        self.set(name="GATING_CTRL", value=0x0)
        self.set(name="RESERVED_08", value=0x0)
        self.set(name="RESERVED_0C", value=0x0)
        self.set(name="USM_CTRL", value=(cfg.i_sharp_usm_gain & RM10) | ((cfg.f_usm_coring_thr & RM7) << 16))
        val = (cfg.i_sharp_core_A & RM8) | ((cfg.i_sharp_core_B & RM8) << 8) | ((cfg.i_sharp_core_C & RM8) << 16)
        self.set(name="USM_COEF", value=val)
        self.set(name="RESERVED_18", value=0x0)
        self.set(name="RESERVED_1C", value=0x0)
        self.set(name="SHOOT_CTRL_REG0", value=(cfg.i_shoot_ctrl_delta_offset & RM8))
        val = (cfg.i_shoot_ctrl_pos & RM7) | ((cfg.i_shoot_ctrl_pos_unlimit & RM7) << 16)
        self.set(name="SHOOT_CTRL_REG1", value=val)
        val = (cfg.i_shoot_ctrl_neg & RM7) | ((cfg.i_shoot_ctrl_neg_unlimit & RM7) << 16)
        self.set(name="SHOOT_CTRL_REG2", value=val)
        val = (
            (cfg.i_sharp_roi_xstart & RM12)
            | ((cfg.i_sharp_roi_ystart & RM12) << 16)
            | ((cfg.i_sharp_roi_enable & RM1) << 31)
        )
        self.set(name="ROI_CTRL0", value=val)
        self.set(name="ROI_CTRL1", value=(cfg.i_sharp_roi_xend & RM12) | ((cfg.i_sharp_roi_yend & RM12) << 16))
        self.set(name="INK_CTRL", value=(cfg.i_ink_mode & RM4) | ((cfg.i_ink_enable & RM1) << 31))
        return True

    def regs2config_lite(self) -> bool:
        if self.platform not in ["RK3572"]:
            self.logger.error(f"current registers type is not fit for platform {self.platform}!")
            return False
        val = self.get(name="ENABLE_CTRL")
        self.config.i_sharp_lite_en = (val >> 0) & RM1
        self.config.i_shoot_ctrl_en = (val >> 1) & RM1
        val = self.get(name="USM_CTRL")
        self.config.i_sharp_usm_gain = (val >> 0) & RM10
        self.config.f_usm_coring_thr = (val >> 16) & RM7
        val = self.get(name="USM_COEF")
        self.config.i_sharp_core_A = int(val >> 0) & RM8
        self.config.i_sharp_core_B = int(val >> 8) & RM8
        self.config.i_sharp_core_C = int(val >> 16) & RM8
        val = self.get(name="SHOOT_CTRL_REG0")
        self.config.i_shoot_ctrl_delta_offset = val & RM7
        val = self.get(name="SHOOT_CTRL_REG1")
        self.config.i_shoot_ctrl_pos = (val >> 0) & RM7
        self.config.i_shoot_ctrl_pos_unlimit = (val >> 16) & RM7
        val = self.get(name="SHOOT_CTRL_REG2")
        self.config.i_shoot_ctrl_neg = (val >> 0) & RM7
        self.config.i_shoot_ctrl_neg_unlimit = (val >> 16) & RM7
        val = self.get(name="ROI_CTRL0")
        self.config.i_sharp_roi_xstart = (val >> 0) & RM12
        self.config.i_sharp_roi_xend = (val >> 16) & RM12
        self.config.i_sharp_roi_enable = (val >> 31) & RM1
        val = self.get(name="ROI_CTRL1")
        self.config.i_sharp_roi_xend = (val >> 0) & RM12
        self.config.i_sharp_roi_yend = (val >> 16) & RM12
        # TODO: parse INK_CTRL register
        val = self.get(name="INK_CTRL")
        self.config.i_ink_mode = (val >> 0) & RM4
        self.config.i_ink_enable = (val >> 31) & RM1
        return True

    def config2regs_full(self) -> bool:
        if self.platform in ["RK3572"]:
            self.logger.error(f"current registers type is not fit for platform {self.platform}!")
            return False

        try:
            ## s_sharp_en_ctrl
            cfg = self.config.s_sharp_en_ctrl
            val = (
                (self.config.i_EnabledSharpen & RM1)
                | (((cfg.i_lti_h_en | cfg.i_lti_v_en) & RM1) << 1)
                | (((cfg.i_cti_h_en | cfg.i_cti_v_en) & RM1) << 2)
                | ((cfg.i_peaking_en & RM1) << 3)
                | (((cfg.i_peaking_gain_en | cfg.i_peaking_coring_en | cfg.i_peaking_limit_ctrl_en) & RM1) << 4)
                | ((cfg.i_peaking_shoot_ctrl_en & RM1) << 5)
                | ((cfg.i_peaking_edge_ctrl_en & RM1) << 6)
                # | ((cfg.i_peaking_edge_shoot_ctr & RM1) << 1)
                | ((cfg.i_shoot_ctrl_en & RM1) << 7)
                | ((cfg.i_global_gain_en & RM1) << 8)
                | ((cfg.i_color_adj_en & RM1) << 9)
                | ((cfg.i_texture_adj_en & RM1) << 10)
            )
            self.set(name="CTRL", value=val)
            ## s_sharp_hw_config
            cfg = self.config.s_sharp_hw_config
            val = (
                ((cfg.lti_gating_en & RM1) << 1)
                | ((cfg.cti_gating_en & RM1) << 2)
                | ((cfg.peaking_gating_en & RM1) << 3)
                | ((cfg.peaking_ctrl_gating_en & RM1) << 4)
                | ((cfg.peaking_shoot_ctrl_gating_en & RM1) << 5)
                | ((cfg.edge_proc_gating_en & RM1) << 6)
                | ((cfg.shoot_ctrl_gating_en & RM1) << 7)
                | ((cfg.gain_ctrl_gating_en & RM1) << 8)
                | ((cfg.color_adj_gating_en & RM1) << 9)
                | ((cfg.texture_adj_gating_en & RM1) << 10)
            )
            self.set(name="AUTO_GATING_IMD", value=val)
            ## s_peaking
            cfg = self.config.s_peaking
            val = (
                ((cfg.t_filt_core_V0[0] & RM4) << 0)
                | ((cfg.t_filt_core_V0[1] & RM4) << 4)
                | ((cfg.t_filt_core_V0[2] & RM4) << 8)
                | ((cfg.t_filt_core_V1[0] & RM4) << 12)
                | ((cfg.t_filt_core_V1[1] & RM4) << 16)
                | ((cfg.t_filt_core_V1[2] & RM4) << 20)
            )
            self.set(name="PEAKING_FILTER_COE0", value=val)
            val = (
                ((cfg.t_filt_core_V2[0] & RM4) << 0)
                | ((cfg.t_filt_core_V2[1] & RM4) << 4)
                | ((cfg.t_filt_core_V2[2] & RM4) << 8)
                | ((cfg.t_filt_core_USM[0] & RM4) << 12)
                | ((cfg.t_filt_core_USM[1] & RM4) << 16)
                | ((cfg.t_filt_core_USM[2] & RM4) << 20)
                | ((cfg.i_diag_enh_coef & RM3) << 24)
            )
            self.set(name="PEAKING_FILTER_COE1", value=val)
            tab = cfg.t_filt_core_H0 + cfg.t_filt_core_H1 + cfg.t_filt_core_H2 + cfg.t_filt_core_H3 # len=4x6
            j = 0
            for i in range(2, 10, 2):
                val = ((tab[j] & RM5) << 0) | ((tab[j + 1] & RM7) << 8) | ((tab[j + 2] & RM9) << 16)
                self.set(name=f"PEAKING_FILTER_COE{i}", value=val)
                val = ((tab[j + 3] & RM10) << 0) | ((tab[j + 4] & RM11) << 10) | ((tab[j + 5] & RM10) << 21)
                self.set(name=f"PEAKING_FILTER_COE{i+1}", value=val)
                j += 6

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
                    gain_ctrl_pos = cfg.t_GainPos[i]
                    gain_ctrl_neg = cfg.t_GainNeg[i]
                else:
                    gain_ctrl_pos = 1024
                    gain_ctrl_neg = 1024
                if self.config.s_sharp_en_ctrl.i_peaking_limit_ctrl_en:
                    limit_ctrl_p0 = cfg.t_LimitPos0[i]
                    limit_ctrl_p1 = cfg.t_LimitPos1[i]
                    limit_ctrl_n0 = cfg.t_LimitNeg0[i]
                    limit_ctrl_n1 = cfg.t_LimitNeg1[i]
                    limit_ctrl_ratio = cfg.t_LimitRatio[i]
                else:
                    limit_ctrl_p0 = 1023
                    limit_ctrl_p1 = 1023
                    limit_ctrl_n0 = 1023
                    limit_ctrl_n1 = 1023
                    limit_ctrl_ratio = 1024

                peaking_ctrl_idx_P0 = coring_zero
                peaking_ctrl_idx_N0 = -coring_zero
                peaking_ctrl_idx_P1 = coring_thr
                peaking_ctrl_idx_N1 = -coring_thr
                peaking_ctrl_idx_P2 = limit_ctrl_p0
                peaking_ctrl_idx_N2 = -limit_ctrl_n0
                peaking_ctrl_idx_P3 = limit_ctrl_p1
                peaking_ctrl_idx_N3 = -limit_ctrl_n1

                ratio_pos_tmp = (coring_ratio * gain_ctrl_pos + 512) >> 10
                ratio_neg_tmp = (coring_ratio * gain_ctrl_neg + 512) >> 10
                peaking_ctrl_value_P1 = (ratio_pos_tmp * (coring_thr - coring_zero) + 512) >> 10
                peaking_ctrl_value_N1 = -((ratio_neg_tmp * (coring_thr - coring_zero) + 512) >> 10)
                peaking_ctrl_ratio_P01 = ratio_pos_tmp
                peaking_ctrl_ratio_N01 = ratio_neg_tmp
                peaking_ctrl_ratio_P12 = gain_ctrl_pos
                peaking_ctrl_ratio_N12 = gain_ctrl_neg

                peaking_ctrl_add_tmp = (gain_ctrl_pos * (limit_ctrl_p0 - coring_thr) + 512) >> 10
                peaking_ctrl_value_P2 = peaking_ctrl_value_P1 + peaking_ctrl_add_tmp
                peaking_ctrl_add_tmp = (gain_ctrl_neg * (limit_ctrl_n0 - coring_thr) + 512) >> 10
                peaking_ctrl_value_N2 = peaking_ctrl_value_N1 - peaking_ctrl_add_tmp

                ratio_pos_tmp = (limit_ctrl_ratio * gain_ctrl_pos + 512) >> 10
                ratio_neg_tmp = (limit_ctrl_ratio * gain_ctrl_neg + 512) >> 10

                peaking_ctrl_add_tmp = (ratio_pos_tmp * (limit_ctrl_p1 - limit_ctrl_p0) + 512) >> 10
                peaking_ctrl_value_P3 = peaking_ctrl_value_P2 + peaking_ctrl_add_tmp
                peaking_ctrl_add_tmp = (ratio_neg_tmp * (limit_ctrl_n1 - limit_ctrl_n0) + 512) >> 10
                peaking_ctrl_value_N3 = peaking_ctrl_value_N2 - peaking_ctrl_add_tmp
                peaking_ctrl_ratio_P23 = ratio_pos_tmp
                peaking_ctrl_ratio_N23 = ratio_neg_tmp

                peaking_ctrl_idx_N0 = clamp(peaking_ctrl_idx_N0, -1024, 1023)
                peaking_ctrl_idx_N1 = clamp(peaking_ctrl_idx_N1, -1024, 1023)
                peaking_ctrl_idx_N2 = clamp(peaking_ctrl_idx_N2, -1024, 1023)
                peaking_ctrl_idx_N3 = clamp(peaking_ctrl_idx_N3, -1024, 1023)
                peaking_ctrl_idx_P0 = clamp(peaking_ctrl_idx_P0, -1024, 1023)
                peaking_ctrl_idx_P1 = clamp(peaking_ctrl_idx_P1, -1024, 1023)
                peaking_ctrl_idx_P2 = clamp(peaking_ctrl_idx_P2, -1024, 1023)
                peaking_ctrl_idx_P3 = clamp(peaking_ctrl_idx_P3, -1024, 1023)
                peaking_ctrl_value_N1 = clamp(peaking_ctrl_value_N1, -1024, 1023)
                peaking_ctrl_value_N2 = clamp(peaking_ctrl_value_N2, -1024, 1023)
                peaking_ctrl_value_N3 = clamp(peaking_ctrl_value_N3, -1024, 1023)
                peaking_ctrl_value_P1 = clamp(peaking_ctrl_value_P1, -1024, 1023)
                peaking_ctrl_value_P2 = clamp(peaking_ctrl_value_P2, -1024, 1023)
                peaking_ctrl_value_P3 = clamp(peaking_ctrl_value_P3, -1024, 1023)
                peaking_ctrl_ratio_N01 = clamp(peaking_ctrl_ratio_N01, 0, 4095)
                peaking_ctrl_ratio_N12 = clamp(peaking_ctrl_ratio_N12, 0, 4095)
                peaking_ctrl_ratio_N23 = clamp(peaking_ctrl_ratio_N23, 0, 4095)
                peaking_ctrl_ratio_P01 = clamp(peaking_ctrl_ratio_P01, 0, 4095)
                peaking_ctrl_ratio_P12 = clamp(peaking_ctrl_ratio_P12, 0, 4095)
                peaking_ctrl_ratio_P23 = clamp(peaking_ctrl_ratio_P23, 0, 4095)

                val = ((peaking_ctrl_idx_N0 & RM11) << 0) | ((peaking_ctrl_idx_N1 & RM11) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE0", value=val)
                val = ((peaking_ctrl_idx_N2 & RM11) << 0) | ((peaking_ctrl_idx_N3 & RM11) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE1", value=val)
                val = ((peaking_ctrl_idx_P0 & RM11) << 0) | ((peaking_ctrl_idx_P1 & RM11) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE2", value=val)
                val = ((peaking_ctrl_idx_P2 & RM11) << 0) | ((peaking_ctrl_idx_P3 & RM11) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE3", value=val)
                val = ((peaking_ctrl_value_N1 & RM11) << 0) | ((peaking_ctrl_value_N2 & RM11) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE4", value=val)
                val = ((peaking_ctrl_value_N3 & RM11) << 0) | ((peaking_ctrl_value_P1 & RM11) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE5", value=val)
                val = ((peaking_ctrl_value_P2 & RM11) << 0) | ((peaking_ctrl_value_P3 & RM11) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE6", value=val)
                val = ((peaking_ctrl_ratio_N01 & RM12) << 0) | ((peaking_ctrl_ratio_N12 & RM12) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE7", value=val)
                val = ((peaking_ctrl_ratio_N23 & RM12) << 0) | ((peaking_ctrl_ratio_P01 & RM12) << 16)
                self.set(name=f"PEAKING{i}_CTRL_COE8", value=val)
                val = (
                    ((peaking_ctrl_ratio_P12 & RM12) << 0)
                    | ((peaking_ctrl_ratio_P23 & RM12) << 12)
                    | ((cfg.t_ShootAdjDeltaOffset[i] & RM8) << 24)
                )
                self.set(name=f"PEAKING{i}_CTRL_COE9", value=val)
                val = (
                    ((cfg.t_ShootAdjAlphaOver[i] & RM7) << 0)
                    | ((cfg.t_ShootAdjAlphaUnder[i] & RM7) << 8)
                    | ((cfg.t_ShootAdjAlphaOverUnlimit[i] & RM7) << 16)
                    | ((cfg.t_ShootAdjAlphaUnderUnlimit[i] & RM7) << 24)
                )
                self.set(name=f"PEAKING{i}_CTRL_COE10", value=val)

            val = (
                ((cfg.i_peakingGain & RM10) << 0)
                | ((cfg.edge_ctrl_i_non_dir_thr & RM7) << 12)
                | ((cfg.edge_ctrl_i_dir_cmp_ratio & RM4) << 20)
                | ((cfg.edge_ctrl_i_non_dir_wgt_ratio & RM5) << 24)
            )
            self.set(name="PEAKING_CTRL0", value=val)
            val = (
                ((cfg.edge_ctrl_i_non_dir_wgt_offset & RM8) << 0)
                | ((cfg.edge_ctrl_i_dir_cnt_thr & RM4) << 8)
                | ((cfg.edge_ctrl_i_dir_cnt_avg & RM3) << 12)
                | ((cfg.edge_ctrl_i_dir_cnt_offset & RM4) << 16)
                | ((cfg.edge_ctrl_i_diag_dir_thr & RM7) << 20)
            )
            self.set(name="PEAKING_CTRL1", value=val)
            val = 0
            for i in range(8):
                val |= (cfg.edge_ctrl_t_diag_adj_gain_tab[i] & RM4) << i * 4
            self.set(name="PEAKING_CTRL2", value=val)
            val = (
                ((cfg.edge_shoot_s_direct_non.i_alpha_over & RM7) << 0)
                | ((cfg.edge_shoot_s_direct_non.i_alpha_under & RM7) << 8)
                | ((cfg.edge_shoot_s_direct_non.i_alpha_over_unlimit & RM7) << 16)
                | ((cfg.edge_shoot_s_direct_non.i_alpha_under_unlimit & RM7) << 24)
            )
            self.set(name="PEAKING_CTRL3", value=val)
            val = (
                ((cfg.edge_shoot_s_direct_v.i_alpha_over & RM7) << 0)
                | ((cfg.edge_shoot_s_direct_v.i_alpha_under & RM7) << 8)
                | ((cfg.edge_shoot_s_direct_v.i_alpha_over_unlimit & RM7) << 16)
                | ((cfg.edge_shoot_s_direct_v.i_alpha_under_unlimit & RM7) << 24)
            )
            self.set(name="PEAKING_CTRL4", value=val)
            val = (
                ((cfg.edge_shoot_s_direct_h.i_alpha_over & RM7) << 0)
                | ((cfg.edge_shoot_s_direct_h.i_alpha_under & RM7) << 8)
                | ((cfg.edge_shoot_s_direct_h.i_alpha_over_unlimit & RM7) << 16)
                | ((cfg.edge_shoot_s_direct_h.i_alpha_under_unlimit & RM7) << 24)
            )
            self.set(name="PEAKING_CTRL5", value=val)
            val = (
                ((cfg.edge_shoot_s_direct_d0.i_alpha_over & RM7) << 0)
                | ((cfg.edge_shoot_s_direct_d0.i_alpha_under & RM7) << 8)
                | ((cfg.edge_shoot_s_direct_d0.i_alpha_over_unlimit & RM7) << 16)
                | ((cfg.edge_shoot_s_direct_d0.i_alpha_under_unlimit & RM7) << 24)
            )
            self.set(name="PEAKING_CTRL6", value=val)
            val = (
                ((cfg.edge_shoot_s_direct_d1.i_alpha_over & RM7) << 0)
                | ((cfg.edge_shoot_s_direct_d1.i_alpha_under & RM7) << 8)
                | ((cfg.edge_shoot_s_direct_d1.i_alpha_over_unlimit & RM7) << 16)
                | ((cfg.edge_shoot_s_direct_d1.i_alpha_under_unlimit & RM7) << 24)
            )
            self.set(name="PEAKING_CTRL7", value=val)
            val = (
                ((cfg.edge_shoot_s_direct_non.i_delta_offset & RM8) << 0)
                | ((cfg.edge_shoot_s_direct_v.i_delta_offset & RM8) << 8)
                | ((cfg.edge_shoot_s_direct_h.i_delta_offset & RM8) << 16)
            )
            self.set(name="PEAKING_CTRL8", value=val)
            val = ((cfg.edge_shoot_s_direct_d0.i_delta_offset & RM8) << 0) | (
                (cfg.edge_shoot_s_direct_d1.i_delta_offset & RM8) << 8
            )
            self.set(name="PEAKING_CTRL9", value=val)
            ## s_shootCtrl
            cfg = self.config.s_shootCtrl
            val = (
                ((cfg.i_FilterRadius & RM1) << 0)
                | ((cfg.i_Delta_offset & RM8) << 4)
                | ((cfg.i_Alpha_over & RM7) << 12)
                | ((cfg.i_Alpha_under & RM7) << 20)
            )
            self.set(name="SHOOT_CTRL0", value=val)
            val = ((cfg.i_Alpha_over_unlimit & RM7) << 0) | ((cfg.i_Alpha_under_unlimit & RM7) << 8)
            self.set(name="SHOOT_CTRL1", value=val)
            ## s_globalGain
            cfg = self.config.s_globalGain
            val = ((cfg.t_adp_grd[1] & RM10) << 0) | ((cfg.t_adp_grd[2] & RM10) << 10) | ((cfg.t_adp_grd[3] & RM10) << 20)
            self.set(name="GAIN_CTRL0", value=val)
            val = ((cfg.t_adp_grd[4] & RM10) << 0) | ((cfg.t_adp_val[0] & RM7) << 12) | ((cfg.t_adp_val[1] & RM7) << 20)
            self.set(name="GAIN_CTRL1", value=val)
            val = ((cfg.t_adp_val[2] & RM10) << 0) | ((cfg.t_adp_val[3] & RM7) << 12) | ((cfg.t_adp_val[4] & RM7) << 20)
            self.set(name="GAIN_CTRL2", value=val)
            adp_slp01 = round(128 * (cfg.t_adp_val[1] - cfg.t_adp_val[0]) / max(cfg.t_adp_grd[1] - 0, 1))
            adp_slp12 = round(128 * (cfg.t_adp_val[2] - cfg.t_adp_val[1]) / max(cfg.t_adp_grd[2] - cfg.t_adp_grd[1], 1))
            adp_slp23 = round(128 * (cfg.t_adp_val[3] - cfg.t_adp_val[2]) / max(cfg.t_adp_grd[3] - cfg.t_adp_grd[2], 1))
            adp_slp34 = round(128 * (cfg.t_adp_val[4] - cfg.t_adp_val[3]) / max(cfg.t_adp_grd[4] - cfg.t_adp_grd[3], 1))
            adp_slp45 = round(128 * (cfg.t_adp_val[5] - cfg.t_adp_val[4]) / max(1023 - cfg.t_adp_grd[4], 1))
            adp_slp01 = clamp(adp_slp01, -1024, 1023)
            adp_slp12 = clamp(adp_slp12, -1024, 1023)
            adp_slp23 = clamp(adp_slp23, -1024, 1023)
            adp_slp34 = clamp(adp_slp34, -1024, 1023)
            adp_slp45 = clamp(adp_slp45, -1024, 1023)
            val = ((adp_slp01 & RM11) << 0) | ((adp_slp12 & RM11) << 12)
            self.set(name="GAIN_CTRL3", value=val)
            val = ((adp_slp23 & RM11) << 0) | ((adp_slp34 & RM11) << 12)
            self.set(name="GAIN_CTRL4", value=val)
            val = ((adp_slp45 & RM11) << 0) | ((cfg.t_var_grd[1] & RM10) << 11) | ((cfg.t_var_grd[2] & RM10) << 21)
            self.set(name="GAIN_CTRL5", value=val)
            val = ((cfg.t_var_grd[3] & RM10) << 0) | ((cfg.t_var_grd[4] & RM10) << 12) | ((cfg.t_var_val[0] & RM7) << 24)
            self.set(name="GAIN_CTRL6", value=val)
            val = (
                ((cfg.t_var_val[1] & RM10) << 0)
                | ((cfg.t_var_val[2] & RM7) << 12)
                | ((cfg.t_var_val[3] & RM7) << 20)
                | ((cfg.t_var_val[4] & RM7) << 24)
            )
            self.set(name="GAIN_CTRL7", value=val)
            var_slp01 = round(128 * (cfg.t_var_val[1] - cfg.t_var_val[0]) / max(cfg.t_var_grd[1] - 0, 1))
            var_slp12 = round(128 * (cfg.t_var_val[2] - cfg.t_var_val[1]) / max(cfg.t_var_grd[2] - cfg.t_var_grd[1], 1))
            var_slp23 = round(128 * (cfg.t_var_val[3] - cfg.t_var_val[2]) / max(cfg.t_var_grd[3] - cfg.t_var_grd[2], 1))
            var_slp34 = round(128 * (cfg.t_var_val[4] - cfg.t_var_val[3]) / max(cfg.t_var_grd[4] - cfg.t_var_grd[3], 1))
            var_slp45 = round(128 * (cfg.t_var_val[5] - cfg.t_var_val[4]) / max(1023 - cfg.t_var_grd[4], 1))
            var_slp01 = clamp(var_slp01, -1024, 1023)
            var_slp12 = clamp(var_slp12, -1024, 1023)
            var_slp23 = clamp(var_slp23, -1024, 1023)
            var_slp34 = clamp(var_slp34, -1024, 1023)
            var_slp45 = clamp(var_slp45, -1024, 1023)
            val = ((var_slp01 & RM11) << 0) | ((var_slp12 & RM11) << 12)
            self.set(name="GAIN_CTRL8", value=val)
            val = ((var_slp23 & RM11) << 0) | ((var_slp34 & RM11) << 12)
            self.set(name="GAIN_CTRL9", value=val)
            val = ((var_slp45 & RM11) << 0) | ((cfg.i_lum_mode & RM2) << 16) | ((cfg.t_lum_grd[1] & RM10) << 20)
            self.set(name="GAIN_CTRL10", value=val)
            val = ((cfg.t_lum_grd[2] & RM10) << 0) | ((cfg.t_lum_grd[3] & RM10) << 10) | ((cfg.t_lum_grd[4] & RM10) << 20)
            self.set(name="GAIN_CTRL11", value=val)
            val = (
                ((cfg.t_lum_val[0] & RM10) << 0)
                | ((cfg.t_lum_val[1] & RM7) << 12)
                | ((cfg.t_lum_val[2] & RM7) << 20)
                | ((cfg.t_lum_val[3] & RM7) << 24)
            )
            self.set(name="GAIN_CTRL12", value=val)
            lum_slp01 = round(128 * (cfg.t_lum_val[1] - cfg.t_lum_val[0]) / max(cfg.t_lum_grd[1] - 0, 1))
            lum_slp12 = round(128 * (cfg.t_lum_val[2] - cfg.t_lum_val[1]) / max(cfg.t_lum_grd[2] - cfg.t_lum_grd[1], 1))
            lum_slp23 = round(128 * (cfg.t_lum_val[3] - cfg.t_lum_val[2]) / max(cfg.t_lum_grd[3] - cfg.t_lum_grd[2], 1))
            lum_slp34 = round(128 * (cfg.t_lum_val[4] - cfg.t_lum_val[3]) / max(cfg.t_lum_grd[4] - cfg.t_lum_grd[3], 1))
            lum_slp45 = round(128 * (cfg.t_lum_val[5] - cfg.t_lum_val[4]) / max(1023 - cfg.t_lum_grd[4], 1))
            lum_slp01 = clamp(lum_slp01, -1024, 1023)
            lum_slp12 = clamp(lum_slp12, -1024, 1023)
            lum_slp23 = clamp(lum_slp23, -1024, 1023)
            lum_slp34 = clamp(lum_slp34, -1024, 1023)
            lum_slp45 = clamp(lum_slp45, -1024, 1023)
            val = ((cfg.t_lum_val[4] & RM7) << 0) | ((lum_slp01 & RM11) << 8) | ((lum_slp12 & RM11) << 20)
            self.set(name="GAIN_CTRL13", value=val)
            val = ((lum_slp23 & RM11) << 0) | ((lum_slp34 & RM11) << 12)
            self.set(name="GAIN_CTRL14", value=val)
            val = (lum_slp45 & RM11) << 0
            self.set(name="GAIN_CTRL15", value=val)
            ## s_colorCtrl
            cfg = self.config.s_colorCtrl
            val = (
                ((cfg.s_ctrl_point_3.t_ctrl_point[0] & RM10) << 0)
                | ((cfg.s_ctrl_point_3.t_ctrl_point[1] & RM10) << 12)
                | ((cfg.s_ctrl_point_3.i_ctrl_scaling & RM3) << 24)
            )
            self.set(name="COLORADJ_CTRL0", value=val)
            val = (
                ((cfg.s_ctrl_point_3.t_ctrl_rolltab[0] & RM5) << 0)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[1] & RM5) << 5)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[2] & RM5) << 10)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[3] & RM5) << 15)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[4] & RM5) << 20)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[5] & RM5) << 25)
            )
            self.set(name="COLORADJ_CTRL1", value=val)
            val = (
                ((cfg.s_ctrl_point_3.t_ctrl_rolltab[6] & RM5) << 0)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[7] & RM5) << 5)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[8] & RM5) << 10)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[9] & RM5) << 15)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[10] & RM5) << 20)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[11] & RM5) << 25)
            )
            self.set(name="COLORADJ_CTRL2", value=val)
            val = (
                ((cfg.s_ctrl_point_3.t_ctrl_rolltab[12] & RM5) << 0)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[13] & RM5) << 5)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[14] & RM5) << 10)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[15] & RM5) << 15)
            )
            self.set(name="COLORADJ_CTRL3", value=val)
            val = (
                ((cfg.s_ctrl_point_3.t_ctrl_point[0] & RM10) << 0)
                | ((cfg.s_ctrl_point_3.t_ctrl_point[1] & RM10) << 12)
                | ((cfg.s_ctrl_point_3.i_ctrl_scaling & RM3) << 24)
            )
            self.set(name="COLORADJ_CTRL4", value=val)
            val = (
                ((cfg.s_ctrl_point_1.t_ctrl_rolltab[0] & RM5) << 0)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[1] & RM5) << 5)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[2] & RM5) << 10)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[3] & RM5) << 15)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[4] & RM5) << 20)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[5] & RM5) << 25)
            )
            self.set(name="COLORADJ_CTRL5", value=val)
            val = (
                ((cfg.s_ctrl_point_1.t_ctrl_rolltab[6] & RM5) << 0)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[7] & RM5) << 5)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[8] & RM5) << 10)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[9] & RM5) << 15)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[10] & RM5) << 20)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[11] & RM5) << 25)
            )
            self.set(name="COLORADJ_CTRL6", value=val)
            val = (
                ((cfg.s_ctrl_point_1.t_ctrl_rolltab[12] & RM5) << 0)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[13] & RM5) << 5)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[14] & RM5) << 10)
                | ((cfg.s_ctrl_point_1.t_ctrl_rolltab[15] & RM5) << 15)
            )
            self.set(name="COLORADJ_CTRL7", value=val)
            val = (
                ((cfg.s_ctrl_point_1.t_ctrl_point[0] & RM10) << 0)
                | ((cfg.s_ctrl_point_1.t_ctrl_point[1] & RM10) << 12)
                | ((cfg.s_ctrl_point_1.i_ctrl_scaling & RM3) << 24)
            )
            self.set(name="COLORADJ_CTRL8", value=val)
            val = (
                ((cfg.s_ctrl_point_2.t_ctrl_rolltab[0] & RM5) << 0)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[1] & RM5) << 5)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[2] & RM5) << 10)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[3] & RM5) << 15)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[4] & RM5) << 20)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[5] & RM5) << 25)
            )
            self.set(name="COLORADJ_CTRL9", value=val)
            val = (
                ((cfg.s_ctrl_point_2.t_ctrl_rolltab[6] & RM5) << 0)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[7] & RM5) << 5)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[8] & RM5) << 10)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[9] & RM5) << 15)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[10] & RM5) << 20)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[11] & RM5) << 25)
            )
            self.set(name="COLORADJ_CTRL10", value=val)
            val = (
                ((cfg.s_ctrl_point_2.t_ctrl_rolltab[12] & RM5) << 0)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[13] & RM5) << 5)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[14] & RM5) << 10)
                | ((cfg.s_ctrl_point_2.t_ctrl_rolltab[15] & RM5) << 15)
            )
            self.set(name="COLORADJ_CTRL11", value=val)
            val = (
                ((cfg.s_ctrl_point_2.t_ctrl_point[0] & RM10) << 0)
                | ((cfg.s_ctrl_point_2.t_ctrl_point[1] & RM10) << 12)
                | ((cfg.s_ctrl_point_2.i_ctrl_scaling & RM3) << 24)
            )
            self.set(name="COLORADJ_CTRL12", value=val)
            val = (
                ((cfg.s_ctrl_point_3.t_ctrl_rolltab[0] & RM5) << 0)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[1] & RM5) << 5)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[2] & RM5) << 10)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[3] & RM5) << 15)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[4] & RM5) << 20)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[5] & RM5) << 25)
            )
            self.set(name="COLORADJ_CTRL13", value=val)
            val = (
                ((cfg.s_ctrl_point_3.t_ctrl_rolltab[6] & RM5) << 0)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[7] & RM5) << 5)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[8] & RM5) << 10)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[9] & RM5) << 15)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[10] & RM5) << 20)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[11] & RM5) << 25)
            )
            self.set(name="COLORADJ_CTRL14", value=val)
            val = (
                ((cfg.s_ctrl_point_3.t_ctrl_rolltab[12] & RM5) << 0)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[13] & RM5) << 5)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[14] & RM5) << 10)
                | ((cfg.s_ctrl_point_3.t_ctrl_rolltab[15] & RM5) << 15)
            )
            self.set(name="COLORADJ_CTRL15", value=val)
            ## s_textureAdj
            cfg = self.config.s_textureAdj
            val = (
                ((cfg.i_idx_mode_select & RM1) << 0)
                | ((cfg.i_y_mode_select & RM2) << 1)
                | ((cfg.t_texture_grd[1] & RM10) << 4)
                | ((cfg.t_texture_grd[2] & RM10) << 16)
            )
            self.set(name="TEXTURE_CTRL0", value=val)
            val = (
                ((cfg.t_texture_grd[3] & RM10) << 0)
                | ((cfg.t_texture_grd[4] & RM10) << 12)
                | ((cfg.t_texture_val[0] & RM7) << 24)
            )
            self.set(name="TEXTURE_CTRL1", value=val)
            val = (
                ((cfg.t_texture_val[1] & RM7) << 0)
                | ((cfg.t_texture_val[2] & RM7) << 8)
                | ((cfg.t_texture_val[3] & RM7) << 16)
                | ((cfg.t_texture_val[4] & RM7) << 24)
            )
            self.set(name="TEXTURE_CTRL2", value=val)
            tex_slp01 = round(128 * (cfg.t_texture_val[1] - cfg.t_texture_val[0]) / max(cfg.t_texture_grd[1] - 0, 1))
            tex_slp12 = round(
                128 * (cfg.t_texture_val[2] - cfg.t_texture_val[1]) / max(cfg.t_texture_grd[2] - cfg.t_texture_grd[1], 1)
            )
            tex_slp23 = round(
                128 * (cfg.t_texture_val[3] - cfg.t_texture_val[2]) / max(cfg.t_texture_grd[3] - cfg.t_texture_grd[2], 1)
            )
            tex_slp34 = round(
                128 * (cfg.t_texture_val[4] - cfg.t_texture_val[3]) / max(cfg.t_texture_grd[4] - cfg.t_texture_grd[3], 1)
            )
            tex_slp45 = round(128 * (cfg.t_texture_val[5] - cfg.t_texture_val[4]) / max(1023 - cfg.t_texture_grd[4], 1))
            tex_slp01 = clamp(tex_slp01, -1024, 1023)
            tex_slp12 = clamp(tex_slp12, -1024, 1023)
            tex_slp23 = clamp(tex_slp23, -1024, 1023)
            tex_slp34 = clamp(tex_slp34, -1024, 1023)
            tex_slp45 = clamp(tex_slp45, -1024, 1023)
            val = ((lum_slp01 & RM11) << 0) | ((lum_slp12 & RM11) << 12)
            self.set(name="TEXTURE_CTRL3", value=val)
            val = ((lum_slp23 & RM11) << 0) | ((lum_slp34 & RM11) << 12)
            self.set(name="TEXTURE_CTRL4", value=val)
            val = (lum_slp45 & RM11) << 0
            self.set(name="TEXTURE_CTRL5", value=val)
            ## s_lti_h
            cfg = self.config.s_lti_h
            val = ((cfg.i_Radius & RM1) << 0) | ((cfg.i_Slope & RM9) << 4) | ((cfg.i_Thresold & RM9) << 16)
            self.set(name="LTI_CTRL0", value=val)
            val = ((cfg.i_noiseThrNeg & RM10) << 0) | ((cfg.i_noiseThrPos & RM10) << 12) | ((cfg.i_Gain & RM5) << 24)
            self.set(name="LTI_CTRL1", value=val)
            ## s_lti_v
            cfg = self.config.s_lti_v
            val = ((cfg.i_Radius & RM1) << 0) | ((cfg.i_Slope & RM9) << 4) | ((cfg.i_Thresold & RM9) << 16)
            self.set(name="LTI_CTRL2", value=val)
            val = ((cfg.i_noiseThrNeg & RM10) << 0) | ((cfg.i_noiseThrPos & RM10) << 12) | ((cfg.i_Gain & RM5) << 24)
            self.set(name="LTI_CTRL3", value=val)
            ## s_cti_h
            cfg = self.config.s_cti_h
            val = ((cfg.i_Radius & RM1) << 0) | ((cfg.i_Slope & RM9) << 4) | ((cfg.i_Thresold & RM9) << 16)
            self.set(name="CTI_CTRL0", value=val)
            val = ((cfg.i_noiseThrNeg & RM10) << 0) | ((cfg.i_noiseThrPos & RM10) << 12) | ((cfg.i_Gain & RM5) << 24)
            self.set(name="CTI_CTRL1", value=val)
            ## s_cti_v
            cfg = self.config.s_cti_v
            val = ((cfg.i_Radius & RM1) << 0) | ((cfg.i_Slope & RM9) << 4) | ((cfg.i_Thresold & RM9) << 16)
            self.set(name="CTI_CTRL2", value=val)
            val = ((cfg.i_noiseThrNeg & RM10) << 0) | ((cfg.i_noiseThrPos & RM10) << 12) | ((cfg.i_Gain & RM5) << 24)
            self.set(name="CTI_CTRL3", value=val)
            ## s_sharpRoiCfg
            cfg = self.config.s_sharpRoiCfg
            self.set(name="DBG_CTRL0", value=0x0)
            val = ((cfg.i_roi_xstart & RM12) << 0) | ((cfg.i_roi_ystart & RM12) << 16) | ((cfg.i_roi_enable & RM1) << 31)
            self.set(name="ROI_CTRL0", value=val)
            val = (cfg.i_roi_xend & RM12) | ((cfg.i_roi_yend & RM12) << 16)
            self.set(name="ROI_CTRL1", value=val)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]  # get last erro stack
            self.logger.error(f"config2regs error in '{os.path.basename(tb.filename)}'-{tb.lineno}: {e}")
            return False
        return True

    def regs2config_full(self) -> bool:
        if self.platform in ["RK3572"]:
            self.logger.error(f"current registers type is not fit for platform {self.platform}!")
            return False
        # TODO:
        self.logger.error(f"TODO: invalid 'regs2config_full' method for now in platform '{self.platform}'!")
        return False

    def config2regs(self) -> bool:
        if self.platform == "RK3572":
            return self.config2regs_lite()
        return self.config2regs_full()

    def regs2config(self) -> bool:
        if self.platform == "RK3572":
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

    register = SharpRegister(platform=args.platform)
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

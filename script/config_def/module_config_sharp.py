"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_sharp_lite.py
Author      : vance.wu@rock-chips.com
Date        : 2025-08-05
Description :
LastEditTime: 2025-08-15
"""

import os
import sys
import json
import random
import argparse
import traceback

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *
from utils import NoIndent, CompactArrayEncoder


class s_sharp_hw_config:
    lti_gating_en = 0
    cti_gating_en = 0
    peaking_gating_en = 0
    peaking_ctrl_gating_en = 0
    peaking_shoot_ctrl_gating_en = 0
    edge_proc_gating_en = 0
    shoot_ctrl_gating_en = 0
    gain_ctrl_gating_en = 0
    color_adj_gating_en = 0
    texture_adj_gating_en = 0


class s_sharp_en_ctrl:
    i_lti_h_en = 0  # invalid on RK3538
    i_lti_v_en = 0  # invalid on RK3538
    i_cti_h_en = 0  # invalid on RK3538
    i_cti_v_en = 0  # invalid on RK3538
    i_peaking_en = 1
    i_peaking_gain_en = 1
    i_peaking_coring_en = 1
    i_peaking_limit_ctrl_en = 1
    i_peaking_shoot_ctrl_en = 0  # invalid on RK3538
    i_peaking_edge_ctrl_en = 1
    i_peaking_edge_shoot_ctrl_en = 1
    i_shoot_ctrl_en = 1
    i_global_gain_en = 0
    i_color_adj_en = 0  # invalid on RK3538
    i_texture_adj_en = 1


class s_lcti_hv:
    i_Radius = 1
    i_Slope = 100
    i_Thresold = 21
    i_Gain = 8
    i_noiseThrPos = 1023
    i_noiseThrNeg = 1023


class s_peaking:
    # s_gain
    t_GainPos = [128, 512, 1024, 512, 1024, 800, 800, 1024]
    t_GainNeg = [128, 512, 1024, 512, 1024, 800, 800, 1024]
    # s_coring
    t_CoringThreshold = [40, 40, 40, 24, 26, 30, 26, 26]
    t_CoringRatio = [1479, 1188, 1024, 1422, 1024, 1024, 1024, 1024]
    t_CoringZero = [5, 5, 8, 5, 8, 5, 5, 7]
    # s_limitCtrl
    t_LimitPos0 = [64, 64, 64, 64, 64, 64, 64, 64]
    t_LimitPos1 = [120, 120, 120, 120, 120, 120, 120, 120]
    t_LimitNeg0 = [64, 64, 64, 64, 64, 64, 64, 64]
    t_LimitNeg1 = [120, 120, 120, 120, 120, 120, 120, 120]
    t_LimitRatio = [128, 128, 128, 128, 128, 128, 128, 128]
    t_LimitboundPos = [81, 131, 63, 81, 63, 63, 63, 63]
    t_LimitboundNeg = [81, 131, 63, 81, 63, 63, 63, 63]
    # s_shootAdj
    t_ShootAdjDeltaOffset = [32, 32, 32, 32, 32, 32, 32, 32]
    t_ShootAdjAlphaOver = [8, 8, 8, 8, 8, 8, 8, 8]
    t_ShootAdjAlphaUnder = [64, 64, 64, 64, 64, 64, 64, 64]
    t_ShootAdjAlphaOverUnlimit = [96, 96, 96, 96, 96, 96, 96, 96]
    t_ShootAdjAlphaUnderUnlimit = [96, 96, 96, 96, 96, 96, 96, 96]
    # s_edgeCtrl
    edge_ctrl_i_non_dir_thr = 64
    edge_ctrl_i_dir_cmp_ratio = 4
    edge_ctrl_i_non_dir_wgt_offset = 64
    edge_ctrl_i_non_dir_wgt_ratio = 16
    edge_ctrl_i_dir_cnt_thr = 2
    edge_ctrl_i_dir_cnt_avg = 3
    edge_ctrl_i_dir_cnt_offset = 2
    edge_ctrl_i_diag_dir_thr = 64
    edge_ctrl_t_diag_adj_gain_tab = [6, 7, 8, 9, 10, 11, 12, 13]

    # s_edge_shoot_ctrl_param
    class s_direct:
        i_delta_offset = 4
        i_alpha_over = 16
        i_alpha_under = 16
        i_alpha_over_unlimit = 96
        i_alpha_under_unlimit = 96

    edge_shoot_s_direct_h = s_direct()
    edge_shoot_s_direct_v = s_direct()
    edge_shoot_s_direct_d0 = s_direct()
    edge_shoot_s_direct_d1 = s_direct()
    edge_shoot_s_direct_non = s_direct()
    # s_filter_cfg
    i_diag_enh_coef = 6
    t_filt_core_H0 = [1, 10, 45, 120, 210, 252]
    t_filt_core_H1 = [-9, -55, -119, -73, 128, 256]
    t_filt_core_H2 = [0, 0, 0, -256, 0, 512]
    t_filt_core_H3 = [0, 0, 0, 0, -256, 512]
    t_filt_core_V0 = [1, 4, 6]
    t_filt_core_V1 = [-4, 0, 8]
    t_filt_core_V2 = [0, -4, 8]
    t_filt_core_USM = [1, 4, 6]
    # peakingGain
    i_peakingGain = 160


class s_shootCtrl:
    i_FilterRadius = 1
    i_Delta_offset = 32
    i_Alpha_over = 8
    i_Alpha_under = 8
    i_Alpha_over_unlimit = 64
    i_Alpha_under_unlimit = 112


class s_globalGain:
    i_lum_mode = 0
    t_lum_grd = [0, 200, 300, 860, 960, 1023]  # u10, [0, 1023]
    t_lum_val = [40, 50, 64, 70, 80, 90]  # u7, [0, 127]
    t_adp_grd = [0, 4, 60, 200, 300, 1023]  # u10, [0, 1023]
    t_adp_val = [64, 64, 64, 64, 64, 64]  # u7, [0, 127]
    t_var_grd = [0, 39, 102, 209, 500, 1023]  # u10, [0, 1023]
    t_var_val = [36, 54, 64, 64, 64, 64]  # u7, [0, 127]


class s_colorCtrl:
    class s_ctrl_point:
        i_ctrl_scaling = 2
        t_ctrl_point = [468, 584]
        t_ctrl_rolltab = [0, 0, 0, 1, 2, 3, 4, 6, 8, 10, 11, 12, 13, 14, 15, 15]

    s_ctrl_point_0 = s_ctrl_point()
    s_ctrl_point_1 = s_ctrl_point()
    s_ctrl_point_2 = s_ctrl_point()
    s_ctrl_point_3 = s_ctrl_point()


class s_textureAdj:
    i_y_mode_select = 1
    i_idx_mode_select = 0
    t_texture_grd = [0, 128, 256, 400, 600, 1023]
    t_texture_val = [40, 60, 80, 80, 50, 10]


class s_ink_config:
    class ink_set:
        i_ink_idx_h = 128
        i_ink_idx_v = 157
        i_ink_mode = 4
        i_ink_result = 0

    i_EnableInk = 0
    s_ink_set0 = ink_set()
    s_ink_set1 = ink_set()
    s_ink_set2 = ink_set()
    s_ink_set3 = ink_set()


class s_sharpRoiCfg:
    i_roi_enable = 1
    i_roi_xstart = 100
    i_roi_ystart = 60
    i_roi_xend = 1763
    i_roi_yend = 925


class SharpConfig(ModuleConfigCore):
    def __init__(self, name: str = "SharpLite", platform: str = "RK3572"):
        super().__init__(name, platform)

        ## RK3576-VOP3-Heron / RK3538-VOP3-SHARK
        self.i_EnabledSharpen = 1
        self.i_SharpSimMode = 0
        self.s_sharp_hw_config = s_sharp_hw_config()
        self.s_sharp_en_ctrl = s_sharp_en_ctrl()
        self.s_lti_h = s_lcti_hv()
        self.s_cti_h = s_lcti_hv()
        self.s_lti_v = s_lcti_hv()
        self.s_cti_v = s_lcti_hv()
        self.s_peaking = s_peaking()
        self.s_shootCtrl = s_shootCtrl()
        self.s_globalGain = s_globalGain()
        self.s_colorCtrl = s_colorCtrl()
        self.s_textureAdj = s_textureAdj()
        self.s_ink_config = s_ink_config()
        self.s_sharpRoiCfg = s_sharpRoiCfg()

    ## =============== overwrite methods  ===============
    def dump(self, filename: str = "", pretty_array_stdout: int = 32) -> bool:
        ## keep list data in one line by using NoIndent & CompactArrayEncoder
        data = {
            "version": self.version,
            "randSeed": self.randSeed,
            "i_EnabledSharpen": self.i_EnabledSharpen,
            "i_SharpSimMode": self.i_SharpSimMode,
            "s_sharp_hw_config": {
                "lti_gating_en": self.s_sharp_hw_config.lti_gating_en,
                "cti_gating_en": self.s_sharp_hw_config.cti_gating_en,
                "peaking_gating_en": self.s_sharp_hw_config.peaking_gating_en,
                "peaking_ctrl_gating_en": self.s_sharp_hw_config.peaking_ctrl_gating_en,
                "peaking_shoot_ctrl_gating_en": self.s_sharp_hw_config.peaking_shoot_ctrl_gating_en,
                "edge_proc_gating_en": self.s_sharp_hw_config.edge_proc_gating_en,
                "shoot_ctrl_gating_en": self.s_sharp_hw_config.shoot_ctrl_gating_en,
                "gain_ctrl_gating_en": self.s_sharp_hw_config.gain_ctrl_gating_en,
                "color_adj_gating_en": self.s_sharp_hw_config.color_adj_gating_en,
                "texture_adj_gating_en": self.s_sharp_hw_config.texture_adj_gating_en,
            },
            "s_sharp_en_ctrl": {
                "i_lti_h_en": self.s_sharp_en_ctrl.i_lti_h_en,
                "i_lti_v_en": self.s_sharp_en_ctrl.i_lti_v_en,
                "i_cti_h_en": self.s_sharp_en_ctrl.i_cti_h_en,
                "i_cti_v_en": self.s_sharp_en_ctrl.i_cti_v_en,
                "i_peaking_en": self.s_sharp_en_ctrl.i_peaking_en,
                "i_peaking_gain_en": self.s_sharp_en_ctrl.i_peaking_gain_en,
                "i_peaking_coring_en": self.s_sharp_en_ctrl.i_peaking_coring_en,
                "i_peaking_limit_ctrl_en": self.s_sharp_en_ctrl.i_peaking_limit_ctrl_en,
                "i_peaking_shoot_ctrl_en": self.s_sharp_en_ctrl.i_peaking_shoot_ctrl_en,
                "i_peaking_edge_ctrl_en": self.s_sharp_en_ctrl.i_peaking_edge_ctrl_en,
                "i_peaking_edge_shoot_ctrl_en": self.s_sharp_en_ctrl.i_peaking_edge_shoot_ctrl_en,
                "i_shoot_ctrl_en": self.s_sharp_en_ctrl.i_shoot_ctrl_en,
                "i_global_gain_en": self.s_sharp_en_ctrl.i_global_gain_en,
                "i_color_adj_en": self.s_sharp_en_ctrl.i_color_adj_en,
                "i_texture_adj_en": self.s_sharp_en_ctrl.i_texture_adj_en,
            },
            "s_lti_h": {
                "i_Radius": self.s_lti_h.i_Radius,
                "i_Slope": self.s_lti_h.i_Slope,
                "i_Thresold": self.s_lti_h.i_Thresold,
                "i_Gain": self.s_lti_h.i_Gain,
                "i_noiseThrPos": self.s_lti_h.i_noiseThrPos,
                "i_noiseThrNeg": self.s_lti_h.i_noiseThrNeg,
            },
            "s_cti_h": {
                "i_Radius": self.s_cti_h.i_Radius,
                "i_Slope": self.s_cti_h.i_Slope,
                "i_Thresold": self.s_cti_h.i_Thresold,
                "i_Gain": self.s_cti_h.i_Gain,
                "i_noiseThrPos": self.s_cti_h.i_noiseThrPos,
                "i_noiseThrNeg": self.s_cti_h.i_noiseThrNeg,
            },
            "s_lti_v": {
                "i_Radius": self.s_lti_v.i_Radius,
                "i_Slope": self.s_lti_v.i_Slope,
                "i_Thresold": self.s_lti_v.i_Thresold,
                "i_Gain": self.s_lti_v.i_Gain,
                "i_noiseThrPos": self.s_lti_v.i_noiseThrPos,
                "i_noiseThrNeg": self.s_lti_v.i_noiseThrNeg,
            },
            "s_cti_v": {
                "i_Radius": self.s_cti_v.i_Radius,
                "i_Slope": self.s_cti_v.i_Slope,
                "i_Thresold": self.s_cti_v.i_Thresold,
                "i_Gain": self.s_cti_v.i_Gain,
                "i_noiseThrPos": self.s_cti_v.i_noiseThrPos,
                "i_noiseThrNeg": self.s_cti_v.i_noiseThrNeg,
            },
            "s_peaking": {
                "s_gain": {
                    "t_GainPos": NoIndent(self.s_peaking.t_GainPos),
                    "t_GainNeg": NoIndent(self.s_peaking.t_GainNeg),
                },
                "s_coring": {
                    "t_CoringThreshold": NoIndent(self.s_peaking.t_CoringThreshold),
                    "t_CoringRatio": NoIndent(self.s_peaking.t_CoringRatio),
                    "t_CoringZero": NoIndent(self.s_peaking.t_CoringZero),
                },
                "s_limitCtrl": {
                    "t_LimitPos0": NoIndent(self.s_peaking.t_LimitPos0),
                    "t_LimitPos1": NoIndent(self.s_peaking.t_LimitPos1),
                    "t_LimitNeg0": NoIndent(self.s_peaking.t_LimitNeg0),
                    "t_LimitNeg1": NoIndent(self.s_peaking.t_LimitNeg1),
                    "t_LimitRatio": NoIndent(self.s_peaking.t_LimitRatio),
                    "t_LimitboundPos": NoIndent(self.s_peaking.t_LimitboundPos),
                    "t_LimitboundNeg": NoIndent(self.s_peaking.t_LimitboundNeg),
                },
                "s_shootAdj": {
                    "t_ShootAdjDeltaOffset": NoIndent(self.s_peaking.t_ShootAdjDeltaOffset),
                    "t_ShootAdjAlphaOver": NoIndent(self.s_peaking.t_ShootAdjAlphaOver),
                    "t_ShootAdjAlphaUnder": NoIndent(self.s_peaking.t_ShootAdjAlphaUnder),
                    "t_ShootAdjAlphaOverUnlimit": NoIndent(self.s_peaking.t_ShootAdjAlphaOverUnlimit),
                    "t_ShootAdjAlphaUnderUnlimit": NoIndent(self.s_peaking.t_ShootAdjAlphaUnderUnlimit),
                },
                "s_edgeCtrl": {
                    "s_edge_ctrl_param": {
                        "i_non_dir_thr": self.s_peaking.edge_ctrl_i_non_dir_thr,
                        "i_dir_cmp_ratio": self.s_peaking.edge_ctrl_i_dir_cmp_ratio,
                        "i_non_dir_wgt_offset": self.s_peaking.edge_ctrl_i_non_dir_wgt_offset,
                        "i_non_dir_wgt_ratio": self.s_peaking.edge_ctrl_i_non_dir_wgt_ratio,
                        "i_dir_cnt_thr": self.s_peaking.edge_ctrl_i_dir_cnt_thr,
                        "i_dir_cnt_avg": self.s_peaking.edge_ctrl_i_dir_cnt_avg,
                        "i_dir_cnt_offset": self.s_peaking.edge_ctrl_i_dir_cnt_offset,
                        "i_diag_dir_thr": self.s_peaking.edge_ctrl_i_diag_dir_thr,
                        "t_diag_adj_gain_tab": NoIndent(self.s_peaking.edge_ctrl_t_diag_adj_gain_tab),
                    },
                    "s_edge_shoot_ctrl_param": {
                        "s_direct_h": {
                            "i_delta_offset": self.s_peaking.edge_shoot_s_direct_h.i_delta_offset,
                            "i_alpha_over": self.s_peaking.edge_shoot_s_direct_h.i_alpha_over,
                            "i_alpha_under": self.s_peaking.edge_shoot_s_direct_h.i_alpha_under,
                            "i_alpha_over_unlimit": self.s_peaking.edge_shoot_s_direct_h.i_alpha_over_unlimit,
                            "i_alpha_under_unlimit": self.s_peaking.edge_shoot_s_direct_h.i_alpha_under_unlimit,
                        },
                        "s_direct_v": {
                            "i_delta_offset": self.s_peaking.edge_shoot_s_direct_v.i_delta_offset,
                            "i_alpha_over": self.s_peaking.edge_shoot_s_direct_v.i_alpha_over,
                            "i_alpha_under": self.s_peaking.edge_shoot_s_direct_v.i_alpha_under,
                            "i_alpha_over_unlimit": self.s_peaking.edge_shoot_s_direct_v.i_alpha_over_unlimit,
                            "i_alpha_under_unlimit": self.s_peaking.edge_shoot_s_direct_v.i_alpha_under_unlimit,
                        },
                        "s_direct_d0": {
                            "i_delta_offset": self.s_peaking.edge_shoot_s_direct_d0.i_delta_offset,
                            "i_alpha_over": self.s_peaking.edge_shoot_s_direct_d0.i_alpha_over,
                            "i_alpha_under": self.s_peaking.edge_shoot_s_direct_d0.i_alpha_under,
                            "i_alpha_over_unlimit": self.s_peaking.edge_shoot_s_direct_d0.i_alpha_over_unlimit,
                            "i_alpha_under_unlimit": self.s_peaking.edge_shoot_s_direct_d0.i_alpha_under_unlimit,
                        },
                        "s_direct_d1": {
                            "i_delta_offset": self.s_peaking.edge_shoot_s_direct_d1.i_delta_offset,
                            "i_alpha_over": self.s_peaking.edge_shoot_s_direct_d1.i_alpha_over,
                            "i_alpha_under": self.s_peaking.edge_shoot_s_direct_d1.i_alpha_under,
                            "i_alpha_over_unlimit": self.s_peaking.edge_shoot_s_direct_d1.i_alpha_over_unlimit,
                            "i_alpha_under_unlimit": self.s_peaking.edge_shoot_s_direct_d1.i_alpha_under_unlimit,
                        },
                        "s_direct_non": {
                            "i_delta_offset": self.s_peaking.edge_shoot_s_direct_non.i_delta_offset,
                            "i_alpha_over": self.s_peaking.edge_shoot_s_direct_non.i_alpha_over,
                            "i_alpha_under": self.s_peaking.edge_shoot_s_direct_non.i_alpha_under,
                            "i_alpha_over_unlimit": self.s_peaking.edge_shoot_s_direct_non.i_alpha_over_unlimit,
                            "i_alpha_under_unlimit": self.s_peaking.edge_shoot_s_direct_non.i_alpha_under_unlimit,
                        },
                    },
                },
                "s_filter_cfg": {
                    "i_diag_enh_coef": self.s_peaking.i_diag_enh_coef,
                    "t_filt_core_H0": NoIndent(self.s_peaking.t_filt_core_H0),
                    "t_filt_core_H1": NoIndent(self.s_peaking.t_filt_core_H1),
                    "t_filt_core_H2": NoIndent(self.s_peaking.t_filt_core_H2),
                    "t_filt_core_H3": NoIndent(self.s_peaking.t_filt_core_H3),
                    "t_filt_core_V0": NoIndent(self.s_peaking.t_filt_core_V0),
                    "t_filt_core_V1": NoIndent(self.s_peaking.t_filt_core_V1),
                    "t_filt_core_V2": NoIndent(self.s_peaking.t_filt_core_V2),
                    "t_filt_core_USM": NoIndent(self.s_peaking.t_filt_core_USM),
                },
                "i_peakingGain": self.s_peaking.i_peakingGain,
            },
            "s_shootCtrl": {
                "i_FilterRadius": self.s_shootCtrl.i_FilterRadius,
                "i_Delta_offset": self.s_shootCtrl.i_Delta_offset,
                "i_Alpha_over": self.s_shootCtrl.i_Alpha_over,
                "i_Alpha_under": self.s_shootCtrl.i_Alpha_under,
                "i_Alpha_over_unlimit": self.s_shootCtrl.i_Alpha_over_unlimit,
                "i_Alpha_under_unlimit": self.s_shootCtrl.i_Alpha_under_unlimit,
            },
            "s_globalGain": {
                "s_lum_gain": {
                    "i_lum_mode": self.s_globalGain.i_lum_mode,
                    "t_lum_grd": NoIndent(self.s_globalGain.t_lum_grd),
                    "t_lum_val": NoIndent(self.s_globalGain.t_lum_val),
                },
                "s_adp_gain": {
                    "t_adp_grd": NoIndent(self.s_globalGain.t_adp_grd),
                    "t_adp_val": NoIndent(self.s_globalGain.t_adp_val),
                },
                "s_var_gain": {
                    "t_var_grd": NoIndent(self.s_globalGain.t_var_grd),
                    "t_var_val": NoIndent(self.s_globalGain.t_var_val),
                },
            },
            "s_colorCtrl": {
                "s_ctrl_point_0": {
                    "i_ctrl_scaling": self.s_colorCtrl.s_ctrl_point_0.i_ctrl_scaling,
                    "t_ctrl_point": NoIndent(self.s_colorCtrl.s_ctrl_point_0.t_ctrl_point),
                    "t_ctrl_rolltab": NoIndent(self.s_colorCtrl.s_ctrl_point_0.t_ctrl_rolltab),
                },
                "s_ctrl_point_1": {
                    "i_ctrl_scaling": self.s_colorCtrl.s_ctrl_point_1.i_ctrl_scaling,
                    "t_ctrl_point": NoIndent(self.s_colorCtrl.s_ctrl_point_1.t_ctrl_point),
                    "t_ctrl_rolltab": NoIndent(self.s_colorCtrl.s_ctrl_point_1.t_ctrl_rolltab),
                },
                "s_ctrl_point_2": {
                    "i_ctrl_scaling": self.s_colorCtrl.s_ctrl_point_2.i_ctrl_scaling,
                    "t_ctrl_point": NoIndent(self.s_colorCtrl.s_ctrl_point_2.t_ctrl_point),
                    "t_ctrl_rolltab": NoIndent(self.s_colorCtrl.s_ctrl_point_2.t_ctrl_rolltab),
                },
                "s_ctrl_point_3": {
                    "i_ctrl_scaling": self.s_colorCtrl.s_ctrl_point_3.i_ctrl_scaling,
                    "t_ctrl_point": NoIndent(self.s_colorCtrl.s_ctrl_point_3.t_ctrl_point),
                    "t_ctrl_rolltab": NoIndent(self.s_colorCtrl.s_ctrl_point_3.t_ctrl_rolltab),
                },
            },
            "s_textureAdj": {
                "i_y_mode_select": self.s_textureAdj.i_y_mode_select,
                "i_idx_mode_select": self.s_textureAdj.i_idx_mode_select,
                "t_texture_grd": NoIndent(self.s_textureAdj.t_texture_grd),
                "t_texture_val": NoIndent(self.s_textureAdj.t_texture_val),
            },
            "s_ink_config": {
                "i_EnableInk": self.s_ink_config.i_EnableInk,
                "s_ink_set0": {
                    "i_ink_idx_h": self.s_ink_config.s_ink_set0.i_ink_idx_h,
                    "i_ink_idx_v": self.s_ink_config.s_ink_set0.i_ink_idx_v,
                    "i_ink_mode": self.s_ink_config.s_ink_set0.i_ink_mode,
                    "i_ink_result": self.s_ink_config.s_ink_set0.i_ink_result,
                },
                "s_ink_set1": {
                    "i_ink_idx_h": self.s_ink_config.s_ink_set1.i_ink_idx_h,
                    "i_ink_idx_v": self.s_ink_config.s_ink_set1.i_ink_idx_v,
                    "i_ink_mode": self.s_ink_config.s_ink_set1.i_ink_mode,
                    "i_ink_result": self.s_ink_config.s_ink_set1.i_ink_result,
                },
                "s_ink_set2": {
                    "i_ink_idx_h": self.s_ink_config.s_ink_set2.i_ink_idx_h,
                    "i_ink_idx_v": self.s_ink_config.s_ink_set2.i_ink_idx_v,
                    "i_ink_mode": self.s_ink_config.s_ink_set2.i_ink_mode,
                    "i_ink_result": self.s_ink_config.s_ink_set2.i_ink_result,
                },
                "s_ink_set3": {
                    "i_ink_idx_h": self.s_ink_config.s_ink_set3.i_ink_idx_h,
                    "i_ink_idx_v": self.s_ink_config.s_ink_set3.i_ink_idx_v,
                    "i_ink_mode": self.s_ink_config.s_ink_set3.i_ink_mode,
                    "i_ink_result": self.s_ink_config.s_ink_set3.i_ink_result,
                },
            },
            "s_sharpRoiCfg": {
                "i_roi_enable": self.s_sharpRoiCfg.i_roi_enable,
                "i_roi_xstart": self.s_sharpRoiCfg.i_roi_xstart,
                "i_roi_ystart": self.s_sharpRoiCfg.i_roi_ystart,
                "i_roi_xend": self.s_sharpRoiCfg.i_roi_xend,
                "i_roi_yend": self.s_sharpRoiCfg.i_roi_yend,
            },
        }
        if filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.pretty_print_dict(k, v, 2, pretty_array_stdout)
            return True

        with open(filename, "w") as f:
            nest_data = {"pq_tuning_param": {"SHARPNESS": data}}
            json_data = json.dumps(nest_data, indent=4, ensure_ascii=False, cls=CompactArrayEncoder)
            f.write(json_data)
            self.logger.info(f"Config parameters saved to file '{filename}'")
            return True

        return False

    def load(self, filename) -> bool:
        # check config file validity
        if not os.path.exists(filename):
            self.logger.error(f"config file '{filename}' doesn't exist!")
            return False
        if not filename.endswith(".json"):
            self.logger.error(f"config file '{filename}' is not a json file!")
            return False

        try:
            with open(filename, "r") as f:
                data = json.load(f)
                if "pq_tuning_param" in data:
                    self.logger.info(f"load config from pq_tuning_param.SHARPNESS ...")
                    data = data["pq_tuning_param"]["SHARPNESS"]

                subdata = data["s_sharp_hw_config"]
                self.s_sharp_hw_config.lti_gating_en = subdata["lti_gating_en"]
                self.s_sharp_hw_config.cti_gating_en = subdata["cti_gating_en"]
                self.s_sharp_hw_config.peaking_gating_en = subdata["peaking_gating_en"]
                self.s_sharp_hw_config.peaking_ctrl_gating_en = subdata["peaking_ctrl_gating_en"]
                self.s_sharp_hw_config.peaking_shoot_ctrl_gating_en = subdata["peaking_shoot_ctrl_gating_en"]
                self.s_sharp_hw_config.edge_proc_gating_en = subdata["edge_proc_gating_en"]
                self.s_sharp_hw_config.shoot_ctrl_gating_en = subdata["shoot_ctrl_gating_en"]
                self.s_sharp_hw_config.gain_ctrl_gating_en = subdata["gain_ctrl_gating_en"]
                self.s_sharp_hw_config.color_adj_gating_en = subdata["color_adj_gating_en"]
                self.s_sharp_hw_config.texture_adj_gating_en = subdata["texture_adj_gating_en"]

                subdata = data["s_sharp_en_ctrl"]
                self.s_sharp_en_ctrl.i_lti_h_en = subdata["i_lti_h_en"]
                self.s_sharp_en_ctrl.i_lti_v_en = subdata["i_lti_v_en"]
                self.s_sharp_en_ctrl.i_cti_h_en = subdata["i_cti_h_en"]
                self.s_sharp_en_ctrl.i_cti_v_en = subdata["i_cti_v_en"]
                self.s_sharp_en_ctrl.i_peaking_en = subdata["i_peaking_en"]
                self.s_sharp_en_ctrl.i_peaking_gain_en = subdata["i_peaking_gain_en"]
                self.s_sharp_en_ctrl.i_peaking_coring_en = subdata["i_peaking_coring_en"]
                self.s_sharp_en_ctrl.i_peaking_limit_ctrl_en = subdata["i_peaking_limit_ctrl_en"]
                self.s_sharp_en_ctrl.i_peaking_shoot_ctrl_en = subdata["i_peaking_shoot_ctrl_en"]
                self.s_sharp_en_ctrl.i_peaking_edge_ctrl_en = subdata["i_peaking_edge_ctrl_en"]
                self.s_sharp_en_ctrl.i_peaking_edge_shoot_ctrl_en = subdata["i_peaking_edge_shoot_ctrl_en"]
                self.s_sharp_en_ctrl.i_shoot_ctrl_en = subdata["i_shoot_ctrl_en"]
                self.s_sharp_en_ctrl.i_global_gain_en = subdata["i_global_gain_en"]
                self.s_sharp_en_ctrl.i_color_adj_en = subdata["i_color_adj_en"]
                self.s_sharp_en_ctrl.i_texture_adj_en = subdata["i_texture_adj_en"]
                if self.platform in ["RK3538"]:
                    self.s_sharp_en_ctrl.i_lti_h_en = 0
                    self.s_sharp_en_ctrl.i_lti_v_en = 0
                    self.s_sharp_en_ctrl.i_cti_h_en = 0
                    self.s_sharp_en_ctrl.i_cti_v_en = 0
                    self.s_sharp_en_ctrl.i_peaking_shoot_ctrl_en = 0
                    self.s_sharp_en_ctrl.i_color_adj_en = 0
                    self.logger.warning(
                        f"LTI/CTI/PeakingShoot/ColorAdj are not supported on {self.platform}, force disabled!"
                    )

                self.s_lti_h.i_Radius = data["s_lti_h"]["i_Radius"]
                self.s_lti_h.i_Slope = data["s_lti_h"]["i_Slope"]
                self.s_lti_h.i_Thresold = data["s_lti_h"]["i_Thresold"]
                self.s_lti_h.i_Gain = data["s_lti_h"]["i_Gain"]
                self.s_lti_h.i_noiseThrPos = data["s_lti_h"]["i_noiseThrPos"]
                self.s_lti_h.i_noiseThrNeg = data["s_lti_h"]["i_noiseThrNeg"]
                self.s_cti_h.i_Radius = data["s_cti_h"]["i_Radius"]
                self.s_cti_h.i_Slope = data["s_cti_h"]["i_Slope"]
                self.s_cti_h.i_Thresold = data["s_cti_h"]["i_Thresold"]
                self.s_cti_h.i_Gain = data["s_cti_h"]["i_Gain"]
                self.s_cti_h.i_noiseThrPos = data["s_cti_h"]["i_noiseThrPos"]
                self.s_cti_h.i_noiseThrNeg = data["s_cti_h"]["i_noiseThrNeg"]
                self.s_lti_v.i_Radius = data["s_lti_v"]["i_Radius"]
                self.s_lti_v.i_Slope = data["s_lti_v"]["i_Slope"]
                self.s_lti_v.i_Thresold = data["s_lti_v"]["i_Thresold"]
                self.s_lti_v.i_Gain = data["s_lti_v"]["i_Gain"]
                self.s_lti_v.i_noiseThrPos = data["s_lti_v"]["i_noiseThrPos"]
                self.s_lti_v.i_noiseThrNeg = data["s_lti_v"]["i_noiseThrNeg"]
                self.s_cti_v.i_Radius = data["s_cti_v"]["i_Radius"]
                self.s_cti_v.i_Slope = data["s_cti_v"]["i_Slope"]
                self.s_cti_v.i_Thresold = data["s_cti_v"]["i_Thresold"]
                self.s_cti_v.i_Gain = data["s_cti_v"]["i_Gain"]
                self.s_cti_v.i_noiseThrPos = data["s_cti_v"]["i_noiseThrPos"]
                self.s_cti_v.i_noiseThrNeg = data["s_cti_v"]["i_noiseThrNeg"]

                subdata = data["s_peaking"]
                self.s_peaking.t_GainPos = subdata["s_gain"]["t_GainPos"]
                self.s_peaking.t_GainNeg = subdata["s_gain"]["t_GainNeg"]
                self.s_peaking.t_CoringThreshold = subdata["s_coring"]["t_CoringThreshold"]
                self.s_peaking.t_CoringRatio = subdata["s_coring"]["t_CoringRatio"]
                self.s_peaking.t_CoringZero = subdata["s_coring"]["t_CoringZero"]
                self.s_peaking.t_LimitPos0 = subdata["s_limitCtrl"]["t_LimitPos0"]
                self.s_peaking.t_LimitPos1 = subdata["s_limitCtrl"]["t_LimitPos1"]
                self.s_peaking.t_LimitNeg0 = subdata["s_limitCtrl"]["t_LimitNeg0"]
                self.s_peaking.t_LimitNeg1 = subdata["s_limitCtrl"]["t_LimitNeg1"]
                self.s_peaking.t_LimitRatio = subdata["s_limitCtrl"]["t_LimitRatio"]
                self.s_peaking.t_LimitboundPos = subdata["s_limitCtrl"]["t_LimitboundPos"]
                self.s_peaking.t_LimitboundNeg = subdata["s_limitCtrl"]["t_LimitboundNeg"]

                subdata = data["s_peaking"]["s_shootAdj"]
                self.s_peaking.t_ShootAdjDeltaOffset = subdata["t_ShootAdjDeltaOffset"]
                self.s_peaking.t_ShootAdjAlphaOver = subdata["t_ShootAdjAlphaOver"]
                self.s_peaking.t_ShootAdjAlphaUnder = subdata["t_ShootAdjAlphaUnder"]
                self.s_peaking.t_ShootAdjAlphaOverUnlimit = subdata["t_ShootAdjAlphaOverUnlimit"]
                self.s_peaking.t_ShootAdjAlphaUnderUnlimit = subdata["t_ShootAdjAlphaUnderUnlimit"]

                subdata = data["s_peaking"]["s_edgeCtrl"]["s_edge_ctrl_param"]
                self.s_peaking.edge_ctrl_i_non_dir_thr = subdata["i_non_dir_thr"]
                self.s_peaking.edge_ctrl_i_dir_cmp_ratio = subdata["i_dir_cmp_ratio"]
                self.s_peaking.edge_ctrl_i_non_dir_wgt_offset = subdata["i_non_dir_wgt_offset"]
                self.s_peaking.edge_ctrl_i_non_dir_wgt_ratio = subdata["i_non_dir_wgt_ratio"]
                self.s_peaking.edge_ctrl_i_dir_cnt_thr = subdata["i_dir_cnt_thr"]
                self.s_peaking.edge_ctrl_i_dir_cnt_avg = subdata["i_dir_cnt_avg"]
                self.s_peaking.edge_ctrl_i_dir_cnt_offset = subdata["i_dir_cnt_offset"]
                self.s_peaking.edge_ctrl_i_diag_dir_thr = subdata["i_diag_dir_thr"]
                self.s_peaking.edge_ctrl_t_diag_adj_gain_tab = subdata["t_diag_adj_gain_tab"]

                subdata = data["s_peaking"]["s_edgeCtrl"]["s_edge_shoot_ctrl_param"]["s_direct_h"]
                self.s_peaking.edge_shoot_s_direct_h.i_delta_offset = subdata["i_delta_offset"]
                self.s_peaking.edge_shoot_s_direct_h.i_alpha_over = subdata["i_alpha_over"]
                self.s_peaking.edge_shoot_s_direct_h.i_alpha_under = subdata["i_alpha_under"]
                self.s_peaking.edge_shoot_s_direct_h.i_alpha_over_unlimit = subdata["i_alpha_over_unlimit"]
                self.s_peaking.edge_shoot_s_direct_h.i_alpha_under_unlimit = subdata["i_alpha_under_unlimit"]
                subdata = data["s_peaking"]["s_edgeCtrl"]["s_edge_shoot_ctrl_param"]["s_direct_v"]
                self.s_peaking.edge_shoot_s_direct_v.i_delta_offset = subdata["i_delta_offset"]
                self.s_peaking.edge_shoot_s_direct_v.i_alpha_over = subdata["i_alpha_over"]
                self.s_peaking.edge_shoot_s_direct_v.i_alpha_under = subdata["i_alpha_under"]
                self.s_peaking.edge_shoot_s_direct_v.i_alpha_over_unlimit = subdata["i_alpha_over_unlimit"]
                self.s_peaking.edge_shoot_s_direct_v.i_alpha_under_unlimit = subdata["i_alpha_under_unlimit"]
                subdata = data["s_peaking"]["s_edgeCtrl"]["s_edge_shoot_ctrl_param"]["s_direct_d0"]
                self.s_peaking.edge_shoot_s_direct_d0.i_delta_offset = subdata["i_delta_offset"]
                self.s_peaking.edge_shoot_s_direct_d0.i_alpha_over = subdata["i_alpha_over"]
                self.s_peaking.edge_shoot_s_direct_d0.i_alpha_under = subdata["i_alpha_under"]
                self.s_peaking.edge_shoot_s_direct_d0.i_alpha_over_unlimit = subdata["i_alpha_over_unlimit"]
                self.s_peaking.edge_shoot_s_direct_d0.i_alpha_under_unlimit = subdata["i_alpha_under_unlimit"]
                subdata = data["s_peaking"]["s_edgeCtrl"]["s_edge_shoot_ctrl_param"]["s_direct_d1"]
                self.s_peaking.edge_shoot_s_direct_d1.i_delta_offset = subdata["i_delta_offset"]
                self.s_peaking.edge_shoot_s_direct_d1.i_alpha_over = subdata["i_alpha_over"]
                self.s_peaking.edge_shoot_s_direct_d1.i_alpha_under = subdata["i_alpha_under"]
                self.s_peaking.edge_shoot_s_direct_d1.i_alpha_over_unlimit = subdata["i_alpha_over_unlimit"]
                self.s_peaking.edge_shoot_s_direct_d1.i_alpha_under_unlimit = subdata["i_alpha_under_unlimit"]
                subdata = data["s_peaking"]["s_edgeCtrl"]["s_edge_shoot_ctrl_param"]["s_direct_non"]
                self.s_peaking.edge_shoot_s_direct_non.i_delta_offset = subdata["i_delta_offset"]
                self.s_peaking.edge_shoot_s_direct_non.i_alpha_over = subdata["i_alpha_over"]
                self.s_peaking.edge_shoot_s_direct_non.i_alpha_under = subdata["i_alpha_under"]
                self.s_peaking.edge_shoot_s_direct_non.i_alpha_over_unlimit = subdata["i_alpha_over_unlimit"]
                self.s_peaking.edge_shoot_s_direct_non.i_alpha_under_unlimit = subdata["i_alpha_under_unlimit"]

                subdata = data["s_peaking"]
                self.s_peaking.i_diag_enh_coef = subdata["s_filter_cfg"]["i_diag_enh_coef"]
                self.s_peaking.t_filt_core_H0 = subdata["s_filter_cfg"]["t_filt_core_H0"]
                self.s_peaking.t_filt_core_H1 = subdata["s_filter_cfg"]["t_filt_core_H1"]
                self.s_peaking.t_filt_core_H2 = subdata["s_filter_cfg"]["t_filt_core_H2"]
                self.s_peaking.t_filt_core_H3 = subdata["s_filter_cfg"]["t_filt_core_H3"]
                self.s_peaking.t_filt_core_V0 = subdata["s_filter_cfg"]["t_filt_core_V0"]
                self.s_peaking.t_filt_core_V1 = subdata["s_filter_cfg"]["t_filt_core_V1"]
                self.s_peaking.t_filt_core_V2 = subdata["s_filter_cfg"]["t_filt_core_V2"]
                self.s_peaking.t_filt_core_USM = subdata["s_filter_cfg"]["t_filt_core_USM"]
                self.s_peaking.i_peakingGain = subdata["i_peakingGain"]

                self.s_shootCtrl.i_FilterRadius = data["s_shootCtrl"]["i_FilterRadius"]
                self.s_shootCtrl.i_Delta_offset = data["s_shootCtrl"]["i_Delta_offset"]
                self.s_shootCtrl.i_Alpha_over = data["s_shootCtrl"]["i_Alpha_over"]
                self.s_shootCtrl.i_Alpha_under = data["s_shootCtrl"]["i_Alpha_under"]
                self.s_shootCtrl.i_Alpha_over_unlimit = data["s_shootCtrl"]["i_Alpha_over_unlimit"]
                self.s_shootCtrl.i_Alpha_under_unlimit = data["s_shootCtrl"]["i_Alpha_under_unlimit"]

                self.s_globalGain.i_lum_mode = data["s_globalGain"]["s_lum_gain"]["i_lum_mode"]
                self.s_globalGain.t_lum_grd = data["s_globalGain"]["s_lum_gain"]["t_lum_grd"]
                self.s_globalGain.t_lum_val = data["s_globalGain"]["s_lum_gain"]["t_lum_val"]
                self.s_globalGain.t_adp_grd = data["s_globalGain"]["s_adp_gain"]["t_adp_grd"]
                self.s_globalGain.t_adp_val = data["s_globalGain"]["s_adp_gain"]["t_adp_val"]
                self.s_globalGain.t_var_grd = data["s_globalGain"]["s_var_gain"]["t_var_grd"]
                self.s_globalGain.t_var_val = data["s_globalGain"]["s_var_gain"]["t_var_val"]

                self.s_colorCtrl.s_ctrl_point_0.i_ctrl_scaling = data["s_colorCtrl"]["s_ctrl_point_0"]["i_ctrl_scaling"]
                self.s_colorCtrl.s_ctrl_point_0.t_ctrl_point = data["s_colorCtrl"]["s_ctrl_point_0"]["t_ctrl_point"]
                self.s_colorCtrl.s_ctrl_point_0.t_ctrl_rolltab = data["s_colorCtrl"]["s_ctrl_point_0"]["t_ctrl_rolltab"]
                self.s_colorCtrl.s_ctrl_point_1.i_ctrl_scaling = data["s_colorCtrl"]["s_ctrl_point_1"]["i_ctrl_scaling"]
                self.s_colorCtrl.s_ctrl_point_1.t_ctrl_point = data["s_colorCtrl"]["s_ctrl_point_1"]["t_ctrl_point"]
                self.s_colorCtrl.s_ctrl_point_1.t_ctrl_rolltab = data["s_colorCtrl"]["s_ctrl_point_1"]["t_ctrl_rolltab"]
                self.s_colorCtrl.s_ctrl_point_2.i_ctrl_scaling = data["s_colorCtrl"]["s_ctrl_point_2"]["i_ctrl_scaling"]
                self.s_colorCtrl.s_ctrl_point_2.t_ctrl_point = data["s_colorCtrl"]["s_ctrl_point_2"]["t_ctrl_point"]
                self.s_colorCtrl.s_ctrl_point_2.t_ctrl_rolltab = data["s_colorCtrl"]["s_ctrl_point_2"]["t_ctrl_rolltab"]
                self.s_colorCtrl.s_ctrl_point_3.i_ctrl_scaling = data["s_colorCtrl"]["s_ctrl_point_3"]["i_ctrl_scaling"]
                self.s_colorCtrl.s_ctrl_point_3.t_ctrl_point = data["s_colorCtrl"]["s_ctrl_point_3"]["t_ctrl_point"]
                self.s_colorCtrl.s_ctrl_point_3.t_ctrl_rolltab = data["s_colorCtrl"]["s_ctrl_point_3"]["t_ctrl_rolltab"]

                self.s_textureAdj.i_y_mode_select = data["s_textureAdj"]["i_y_mode_select"]
                self.s_textureAdj.i_idx_mode_select = data["s_textureAdj"]["i_idx_mode_select"]
                self.s_textureAdj.t_texture_grd = data["s_textureAdj"]["t_texture_grd"]
                self.s_textureAdj.t_texture_val = data["s_textureAdj"]["t_texture_val"]

                subdata = data["s_ink_config"]
                self.s_ink_config.i_EnableInk = subdata["i_EnableInk"]
                self.s_ink_config.s_ink_set0.i_ink_idx_h = subdata["s_ink_set0"]["i_ink_idx_h"]
                self.s_ink_config.s_ink_set0.i_ink_idx_v = subdata["s_ink_set0"]["i_ink_idx_v"]
                self.s_ink_config.s_ink_set0.i_ink_mode = subdata["s_ink_set0"]["i_ink_mode"]
                self.s_ink_config.s_ink_set0.i_ink_result = subdata["s_ink_set0"]["i_ink_result"]
                self.s_ink_config.s_ink_set1.i_ink_idx_h = subdata["s_ink_set1"]["i_ink_idx_h"]
                self.s_ink_config.s_ink_set1.i_ink_idx_v = subdata["s_ink_set1"]["i_ink_idx_v"]
                self.s_ink_config.s_ink_set1.i_ink_mode = subdata["s_ink_set1"]["i_ink_mode"]
                self.s_ink_config.s_ink_set1.i_ink_result = subdata["s_ink_set1"]["i_ink_result"]
                self.s_ink_config.s_ink_set2.i_ink_idx_h = subdata["s_ink_set2"]["i_ink_idx_h"]
                self.s_ink_config.s_ink_set2.i_ink_idx_v = subdata["s_ink_set2"]["i_ink_idx_v"]
                self.s_ink_config.s_ink_set2.i_ink_mode = subdata["s_ink_set2"]["i_ink_mode"]
                self.s_ink_config.s_ink_set2.i_ink_result = subdata["s_ink_set2"]["i_ink_result"]
                self.s_ink_config.s_ink_set3.i_ink_idx_h = subdata["s_ink_set3"]["i_ink_idx_h"]
                self.s_ink_config.s_ink_set3.i_ink_idx_v = subdata["s_ink_set3"]["i_ink_idx_v"]
                self.s_ink_config.s_ink_set3.i_ink_mode = subdata["s_ink_set3"]["i_ink_mode"]
                self.s_ink_config.s_ink_set3.i_ink_result = subdata["s_ink_set3"]["i_ink_result"]

                self.s_sharpRoiCfg.i_roi_enable = data["s_sharpRoiCfg"]["i_roi_enable"]
                self.s_sharpRoiCfg.i_roi_xstart = data["s_sharpRoiCfg"]["i_roi_xstart"]
                self.s_sharpRoiCfg.i_roi_ystart = data["s_sharpRoiCfg"]["i_roi_ystart"]
                self.s_sharpRoiCfg.i_roi_xend = data["s_sharpRoiCfg"]["i_roi_xend"]
                self.s_sharpRoiCfg.i_roi_yend = data["s_sharpRoiCfg"]["i_roi_yend"]

                self.i_EnabledSharpen = data["i_EnabledSharpen"] if "i_EnabledSharpen" in data else 1
                self.i_SharpSimMode = data["i_SharpSimMode"] if "i_SharpSimMode" in data else 0
                self.version = data["version"] if "version" in data else "unknown"
                self.randSeed = data["randSeed"] if "randSeed" in data else -1
                return True
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]  # get last erro stack
            self.logger.error(f"load config '{filename}' failed in '{os.path.basename(tb.filename)}'-{tb.lineno}: {e}")
            return False

    def check(self) -> bool:
        # TODO
        self.valid = True
        return self.valid

    def gen(self, seed: int = 114514, **kwargs) -> bool:
        ## set random seed
        if seed == None:
            seed = self.randSeed
        random.seed(seed)
        np.random.seed(seed)

        self.randSeed = seed
        self.version = f"{self.name.lower()}_config_{self.platform.lower()}_random_seed_{seed}"

        self.i_EnabledSharpen = int(random.randint(0, 99) < 99)  # 99% be ON
        self.i_SharpSimMode = 0

        self.s_sharp_hw_config.lti_gating_en = 1
        self.s_sharp_hw_config.cti_gating_en = 1
        self.s_sharp_hw_config.peaking_gating_en = 1
        self.s_sharp_hw_config.peaking_ctrl_gating_en = 1
        self.s_sharp_hw_config.peaking_shoot_ctrl_gating_en = 1
        self.s_sharp_hw_config.edge_proc_gating_en = 1
        self.s_sharp_hw_config.shoot_ctrl_gating_en = 1
        self.s_sharp_hw_config.gain_ctrl_gating_en = 1
        self.s_sharp_hw_config.color_adj_gating_en = 1
        self.s_sharp_hw_config.texture_adj_gating_en = 1

        self.s_sharp_en_ctrl.i_lti_h_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_lti_v_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_cti_h_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_cti_v_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_peaking_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_peaking_gain_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_peaking_coring_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_peaking_limit_ctrl_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_peaking_shoot_ctrl_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_peaking_edge_ctrl_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_peaking_edge_shoot_ctrl_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_shoot_ctrl_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_global_gain_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_color_adj_en = int(random.randint(0, 99) < 75)  # 75%
        self.s_sharp_en_ctrl.i_texture_adj_en = int(random.randint(0, 99) < 75)  # 75%
        if self.platform in ["RK3538"]:
            self.s_sharp_en_ctrl.i_lti_h_en = 0
            self.s_sharp_en_ctrl.i_lti_v_en = 0
            self.s_sharp_en_ctrl.i_cti_h_en = 0
            self.s_sharp_en_ctrl.i_cti_v_en = 0
            self.s_sharp_en_ctrl.i_peaking_shoot_ctrl_en = 0
            self.s_sharp_en_ctrl.i_color_adj_en = 0

        self.s_lti_h.i_Radius = random.randint(0, 1)
        self.s_lti_h.i_Slope = random.randint(0, 511)
        self.s_lti_h.i_Thresold = random.randint(0, 511)
        self.s_lti_h.i_Gain = random.randint(0, 31)
        self.s_lti_h.i_noiseThrPos = random.randint(0, 1023)
        self.s_lti_h.i_noiseThrNeg = random.randint(0, 1023)
        self.s_cti_h.i_Radius = random.randint(0, 1)
        self.s_cti_h.i_Slope = random.randint(0, 511)
        self.s_cti_h.i_Thresold = random.randint(0, 511)
        self.s_cti_h.i_Gain = random.randint(0, 31)
        self.s_cti_h.i_noiseThrPos = random.randint(0, 1023)
        self.s_cti_h.i_noiseThrNeg = random.randint(0, 1023)
        self.s_lti_v.i_Radius = random.randint(0, 1)
        self.s_lti_v.i_Slope = random.randint(0, 511)
        self.s_lti_v.i_Thresold = random.randint(0, 511)
        self.s_lti_v.i_Gain = random.randint(0, 31)
        self.s_lti_v.i_noiseThrPos = random.randint(0, 1023)
        self.s_lti_v.i_noiseThrNeg = random.randint(0, 1023)
        self.s_cti_v.i_Radius = random.randint(0, 1)
        self.s_cti_v.i_Slope = random.randint(0, 511)
        self.s_cti_v.i_Thresold = random.randint(0, 511)
        self.s_cti_v.i_Gain = random.randint(0, 31)
        self.s_cti_v.i_noiseThrPos = random.randint(0, 1023)
        self.s_cti_v.i_noiseThrNeg = random.randint(0, 1023)

        self.s_peaking.t_GainPos = np.random.randint(0, 2047, 8).tolist()
        self.s_peaking.t_GainNeg = np.random.randint(0, 2047, 8).tolist()
        self.s_peaking.t_CoringRatio = np.random.randint(0, 2047, 8).tolist()
        self.s_peaking.t_CoringZero = np.random.randint(0, 1023, 8).tolist()
        # self.s_peaking.t_CoringThreshold = np.random.randint(0, 1023, 8).tolist()
        # self.s_peaking.t_LimitPos0 = np.random.randint(0, 1023, 8).tolist()
        # self.s_peaking.t_LimitPos1 = np.random.randint(0, 1023, 8).tolist()
        # self.s_peaking.t_LimitNeg0 = np.random.randint(0, 1023, 8).tolist()
        # self.s_peaking.t_LimitNeg1 = np.random.randint(0, 1023, 8).tolist()
        for i in range(8):
            self.s_peaking.t_CoringThreshold[i] = random.randint(self.s_peaking.t_CoringZero[i], 1023)
            self.s_peaking.t_LimitPos0[i] = random.randint(self.s_peaking.t_CoringThreshold[i], 1023)
            self.s_peaking.t_LimitPos1[i] = random.randint(self.s_peaking.t_LimitPos0[i], 1023)
            self.s_peaking.t_LimitNeg0[i] = random.randint(self.s_peaking.t_CoringThreshold[i], 1023)
            self.s_peaking.t_LimitNeg1[i] = random.randint(self.s_peaking.t_LimitNeg0[i], 1023)
        self.s_peaking.t_LimitRatio = np.random.randint(0, 1024, 8).tolist()
        self.s_peaking.t_LimitboundPos = np.random.randint(0, 1023, 8).tolist()
        self.s_peaking.t_LimitboundNeg = np.random.randint(0, 1023, 8).tolist()
        self.s_peaking.t_ShootAdjDeltaOffset = np.random.randint(0, 255, 8).tolist()
        self.s_peaking.t_ShootAdjAlphaOver = np.random.randint(0, 127, 8).tolist()
        self.s_peaking.t_ShootAdjAlphaUnder = np.random.randint(0, 127, 8).tolist()
        self.s_peaking.t_ShootAdjAlphaOverUnlimit = np.random.randint(0, 127, 8).tolist()
        self.s_peaking.t_ShootAdjAlphaUnderUnlimit = np.random.randint(0, 127, 8).tolist()
        self.s_peaking.edge_ctrl_i_non_dir_thr = random.randint(0, 127)
        self.s_peaking.edge_ctrl_i_dir_cmp_ratio = random.randint(0, 15)
        self.s_peaking.edge_ctrl_i_non_dir_wgt_offset = random.randint(0, 255)
        self.s_peaking.edge_ctrl_i_non_dir_wgt_ratio = random.randint(0, 31)
        self.s_peaking.edge_ctrl_i_dir_cnt_thr = random.randint(0, 12)
        self.s_peaking.edge_ctrl_i_dir_cnt_avg = random.randint(0, 7)
        self.s_peaking.edge_ctrl_i_dir_cnt_offset = random.randint(0, 15)
        self.s_peaking.edge_ctrl_i_diag_dir_thr = random.randint(0, 127)
        self.s_peaking.edge_ctrl_t_diag_adj_gain_tab = np.random.randint(0, 15, 8).tolist()

        self.s_peaking.edge_shoot_s_direct_h.i_delta_offset = random.randint(0, 255)
        self.s_peaking.edge_shoot_s_direct_h.i_alpha_over = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_h.i_alpha_under = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_h.i_alpha_over_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_h.i_alpha_under_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_v.i_delta_offset = random.randint(0, 255)
        self.s_peaking.edge_shoot_s_direct_v.i_alpha_over = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_v.i_alpha_under = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_v.i_alpha_over_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_v.i_alpha_under_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_d0.i_delta_offset = random.randint(0, 255)
        self.s_peaking.edge_shoot_s_direct_d0.i_alpha_over = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_d0.i_alpha_under = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_d0.i_alpha_over_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_d0.i_alpha_under_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_d1.i_delta_offset = random.randint(0, 255)
        self.s_peaking.edge_shoot_s_direct_d1.i_alpha_over = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_d1.i_alpha_under = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_d1.i_alpha_over_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_d1.i_alpha_under_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_non.i_delta_offset = random.randint(0, 255)
        self.s_peaking.edge_shoot_s_direct_non.i_alpha_over = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_non.i_alpha_under = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_non.i_alpha_over_unlimit = random.randint(0, 127)
        self.s_peaking.edge_shoot_s_direct_non.i_alpha_under_unlimit = random.randint(0, 127)

        gen_filter_core_hx6 = lambda: [
            random.randint(-15, 15),
            random.randint(-63, 63),
            random.randint(-255, 255),
            random.randint(-511, 511),
            random.randint(-1023, 1023),
            random.randint(0, 1023),
        ]
        gen_filter_core_vx3 = lambda: [random.randint(-8, 7), random.randint(-8, 7), random.randint(0, 15)]
        self.s_peaking.i_diag_enh_coef = random.randint(0, 7)
        self.s_peaking.t_filt_core_H0 = gen_filter_core_hx6()
        self.s_peaking.t_filt_core_H1 = gen_filter_core_hx6()
        self.s_peaking.t_filt_core_H2 = gen_filter_core_hx6()
        self.s_peaking.t_filt_core_H3 = gen_filter_core_hx6()
        self.s_peaking.t_filt_core_V0 = gen_filter_core_vx3()
        self.s_peaking.t_filt_core_V1 = gen_filter_core_vx3()
        self.s_peaking.t_filt_core_V2 = gen_filter_core_vx3()
        self.s_peaking.t_filt_core_USM = np.random.randint(-7, 7, 3).tolist()
        self.s_peaking.i_peakingGain = random.randint(0, 1023)

        self.s_shootCtrl.i_FilterRadius = random.randint(0, 1)
        self.s_shootCtrl.i_Delta_offset = random.randint(0, 255)
        self.s_shootCtrl.i_Alpha_over = random.randint(0, 127)
        self.s_shootCtrl.i_Alpha_under = random.randint(0, 127)
        self.s_shootCtrl.i_Alpha_over_unlimit = random.randint(0, 127)
        self.s_shootCtrl.i_Alpha_under_unlimit = random.randint(0, 127)
        self.s_globalGain.i_lum_mode = random.randint(0, 2)
        self.s_globalGain.t_lum_grd = np.random.randint(0, 1023, 6).tolist()
        self.s_globalGain.t_lum_val = np.random.randint(0, 127, 6).tolist()
        self.s_globalGain.t_adp_grd = np.random.randint(0, 1023, 6).tolist()
        self.s_globalGain.t_adp_val = np.random.randint(0, 127, 6).tolist()
        self.s_globalGain.t_var_grd = np.random.randint(0, 1023, 6).tolist()
        self.s_globalGain.t_var_val = np.random.randint(0, 127, 6).tolist()
        self.s_globalGain.t_lum_grd.sort()  # ascending order
        self.s_globalGain.t_adp_grd.sort()  # ascending order
        self.s_globalGain.t_var_grd.sort()  # ascending order

        self.s_colorCtrl.s_ctrl_point_0.i_ctrl_scaling = random.randint(0, 6)
        self.s_colorCtrl.s_ctrl_point_0.t_ctrl_point = np.random.randint(0, 1023, 2).tolist()
        self.s_colorCtrl.s_ctrl_point_0.t_ctrl_rolltab = np.random.randint(0, 31, 16).tolist()
        self.s_colorCtrl.s_ctrl_point_1.i_ctrl_scaling = random.randint(0, 6)
        self.s_colorCtrl.s_ctrl_point_1.t_ctrl_point = np.random.randint(0, 1023, 2).tolist()
        self.s_colorCtrl.s_ctrl_point_1.t_ctrl_rolltab = np.random.randint(0, 31, 16).tolist()
        self.s_colorCtrl.s_ctrl_point_2.i_ctrl_scaling = random.randint(0, 6)
        self.s_colorCtrl.s_ctrl_point_2.t_ctrl_point = np.random.randint(0, 1023, 2).tolist()
        self.s_colorCtrl.s_ctrl_point_2.t_ctrl_rolltab = np.random.randint(0, 31, 16).tolist()
        self.s_colorCtrl.s_ctrl_point_3.i_ctrl_scaling = random.randint(0, 6)
        self.s_colorCtrl.s_ctrl_point_3.t_ctrl_point = np.random.randint(0, 1023, 2).tolist()
        self.s_colorCtrl.s_ctrl_point_3.t_ctrl_rolltab = np.random.randint(0, 31, 16).tolist()

        self.s_textureAdj.i_y_mode_select = random.randint(0, 3)
        self.s_textureAdj.i_idx_mode_select = random.randint(0, 1)
        self.s_textureAdj.t_texture_grd = np.random.randint(0, 1023, 6).tolist()
        self.s_textureAdj.t_texture_val = np.random.randint(0, 127, 6).tolist()
        self.s_textureAdj.t_texture_grd.sort()  # ascending order

        self.s_ink_config.i_EnableInk = int(random.randint(0, 99) < 75)  # 75%

        self.s_sharpRoiCfg.i_roi_enable = int(random.randint(0, 99) < 20)  # 20%
        self.s_sharpRoiCfg.i_roi_xstart = random.randint(0, 4095)
        self.s_sharpRoiCfg.i_roi_ystart = random.randint(0, 4095)
        self.s_sharpRoiCfg.i_roi_xend = random.randint(self.s_sharpRoiCfg.i_roi_xstart, 4095)
        self.s_sharpRoiCfg.i_roi_yend = random.randint(self.s_sharpRoiCfg.i_roi_ystart, 4095)

        self.logger.info(f"generated a random config with seed={seed}")
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3538...")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.add_argument("-ps", "--passthrough", action="store_true", help="设置相关参数直通寄存器")
    parser.print_usage()
    args = parser.parse_args()

    config = SharpConfig(platform=args.platform)
    if args.interface == "gen":
        seed = config.gen(args.seed)
        config.dump(args.file)
        load_ok = True
    elif args.interface == "load":
        load_ok = config.load(args.file)
        config.dump()
    elif args.interface == "dump":
        load_ok = config.dump(args.file)
    else:
        config.logger.error(f"unknown interface '{args.interface}'!")
        load_ok = False

    check_ok = config.check()
    config.logger.info("load_ok: %s, check_ok: %s" % (load_ok, check_ok))

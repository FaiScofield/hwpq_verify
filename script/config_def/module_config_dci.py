"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_dci.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-08-07
"""

import os
import sys
import json
import random
import argparse
import math
import traceback
import numpy as np

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *
from utils import NoIndent, CompactArrayEncoder, clamp


class DciHWParam_VDPP:
    def __init__(self, platform: str = "RK3572"):
        self.platform = platform

        self.working_mode = 3  # [u2] 0-IDLE, 1-IEP2(deinterlace), 2-VEP(VDPP缩放模式,针对1080p以下的视频), 3-DCI(仅HistCalc)
        self.dci_data_format = 0  # [u3] 0-RGB888, 1-ARGB8888, 4-YSP8bit, 5-YSP10bit
        self.dci_csc_range = 0  # [u1] 0-limited, 1-full
        self.dci_vsd_mode = 0  # [u2] vertical scale down mode select: 0-Disable, 1-x2, 2-x4
        self.dci_hsd_mode = 0  # [u1] horizontal scale down mode select: 0-Disable, 1-x2
        self.dci_alpha_swap = 0  # [u1] 0-ARGB, 1-RGBA
        self.dci_rb_swap = 0  # [u1] 0-RGB, 1-BGR
        self.dci_blk_hsize = 0  # [u8] horizonal block size
        self.dci_blk_vsize = 0  # [u8] vertical block size


class DciHWParam_VOP:
    def __init__(self, platform: str = "RK3572"):
        self.platform = platform

        self.dci_enable = 1
        self.blk_size_fix = 0  # u20
        self.act_width = 0
        self.act_height = 0
        self.act_start_h_idx = 0  # u5
        self.act_start_v_idx = 0  # u5
        self.act_start_h_offset = 0  # u9
        self.act_start_v_offset = 0  # u9
        self.act_blk_size_h = 0  # u9
        self.act_blk_size_v = 0  # u9
        self.ca_enable = 0
        self.sat_w = 0  # u7
        self.luma_sat_adj_zero = 0  # u16
        self.luma_sat_adj_thrd = 0  # u16
        self.luma_sat_adj_k = 0  # u16
        self.dci_local_lut = np.zeros(16 * 16 * 16, np.uint16)
        self.dci_locat_ratio = np.zeros(16 * 16, np.uint8)
        self.dci_global_lut = np.zeros(256, np.uint16)


class DciConfig(ModuleConfigCore):
    def __init__(self, name: str = "DCI", platform: str = "unknown"):
        super().__init__(name, platform)

        # self.user_config = DciUserConfig()

        ## for RK3572 VOP HW regs config
        self.vdpp_config = DciHWParam_VDPP(self.platform)
        self.vop_config = DciHWParam_VOP(self.platform)

    ## =============== overwrite methods  ===============
    def dump(self, filename: str = "", pretty_array_stdout: int = 32) -> bool:
        data = {
            "version": self.version,
            "randSeed": self.randSeed,
            "vdpp_config": {
                "working_mode": self.vdpp_config.working_mode,
                "dci_csc_range": self.vdpp_config.dci_csc_range,
                "dci_vsd_mode": self.vdpp_config.dci_vsd_mode,
                "dci_hsd_mode": self.vdpp_config.dci_hsd_mode,
                "dci_alpha_swap": self.vdpp_config.dci_alpha_swap,
                "dci_rb_swap": self.vdpp_config.dci_rb_swap,
                "dci_blk_hsize": self.vdpp_config.dci_blk_hsize,
                "dci_blk_vsize": self.vdpp_config.dci_blk_vsize,
            },
            "vop_config": {
                "dci_enable": self.vop_config.dci_enable,
                "blk_size_fix": self.vop_config.blk_size_fix,
                "act_width": self.vop_config.act_width,
                "act_height": self.vop_config.act_height,
                "act_start_h_idx": self.vop_config.act_start_h_idx,
                "act_start_v_idx": self.vop_config.act_start_v_idx,
                "act_start_h_offset": self.vop_config.act_start_h_offset,
                "act_start_v_offset": self.vop_config.act_start_v_offset,
                "act_blk_size_h": self.vop_config.act_blk_size_h,
                "act_blk_size_v": self.vop_config.act_blk_size_v,
                "ca_enable": self.vop_config.ca_enable,
                "sat_w": self.vop_config.sat_w,
                "luma_sat_adj_zero": self.vop_config.luma_sat_adj_zero,
                "luma_sat_adj_thrd": self.vop_config.luma_sat_adj_thrd,
                "luma_sat_adj_k": self.vop_config.luma_sat_adj_k,
                ## keep list data in one line by using NoIndent & CompactArrayEncoder
                "dci_local_lut": NoIndent(self.vop_config.dci_local_lut.flatten().tolist()),
                "dci_locat_ratio": NoIndent(self.vop_config.dci_locat_ratio.flatten().tolist()),
                "dci_global_lut": NoIndent(self.vop_config.dci_global_lut.flatten().tolist()),
            },
        }
        if filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.pretty_print_dict(k, v, 2, pretty_array_stdout)
            return True

        with open(filename, "w") as f:
            json_data = json.dumps(data, indent=4, ensure_ascii=False, cls=CompactArrayEncoder)
            f.write(json_data)
            self.logger.info(f"Config parameters saved to file '{filename}'")
            return True

        return False

    def load(self, filename: str) -> bool:
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
                    self.logger.info(f"load config from pq_tuning_param.dci ...")
                    data = data["pq_tuning_param"]["dci"]
                self.version = data["version"] if "version" in data else "unknown"
                self.randSeed = data["randSeed"] if "randSeed" in data else -1

                if "s_vdpp_hist_cnt" in data:
                    vdpp_data = data["s_vdpp_hist_cnt"]
                    self.vdpp_config.dci_vsd_mode = vdpp_data["dci_vsd_mode"]
                    self.vdpp_config.dci_hsd_mode = vdpp_data["dci_hsd_mode"]
                elif "vdpp_config" in data:
                    vdpp_data = data["vdpp_config"]
                    self.vdpp_config.working_mode = vdpp_data["working_mode"]
                    self.vdpp_config.dci_data_format = vdpp_data["dci_data_format"]
                    self.vdpp_config.dci_csc_range = vdpp_data["dci_csc_range"]
                    self.vdpp_config.dci_vsd_mode = vdpp_data["dci_vsd_mode"]
                    self.vdpp_config.dci_hsd_mode = vdpp_data["dci_hsd_mode"]
                    self.vdpp_config.dci_alpha_swap = vdpp_data["dci_alpha_swap"]
                    self.vdpp_config.dci_rb_swap = vdpp_data["dci_rb_swap"]
                    self.vdpp_config.dci_blk_hsize = vdpp_data["dci_blk_hsize"]
                    self.vdpp_config.dci_blk_vsize = vdpp_data["dci_blk_vsize"]
                else:
                    return False

                if "vop_config" in data:
                    vop_data = data["vop_config"]
                    self.vop_config.dci_enable = vop_data["dci_enable"]
                    self.vop_config.blk_size_fix = vop_data["blk_size_fix"]
                    self.vop_config.act_width = vop_data["act_width"]
                    self.vop_config.act_height = vop_data["act_height"]
                    self.vop_config.act_start_h_idx = vop_data["act_start_h_idx"]
                    self.vop_config.act_start_v_idx = vop_data["act_start_v_idx"]
                    self.vop_config.act_start_h_offset = vop_data["act_start_h_offset"]
                    self.vop_config.act_start_v_offset = vop_data["act_start_v_offset"]
                    self.vop_config.act_blk_size_h = vop_data["act_blk_size_h"]
                    self.vop_config.act_blk_size_v = vop_data["act_blk_size_v"]
                    self.vop_config.ca_enable = vop_data["ca_enable"]
                    self.vop_config.sat_w = vop_data["sat_w"]
                    self.vop_config.luma_sat_adj_zero = vop_data["luma_sat_adj_zero"]
                    self.vop_config.luma_sat_adj_thrd = vop_data["luma_sat_adj_thrd"]
                    self.vop_config.luma_sat_adj_k = vop_data["luma_sat_adj_k"]
                    self.vop_config.dci_local_lut = np.array(vop_data["dci_local_lut"], dtype=np.uint16)
                    self.vop_config.dci_locat_ratio = np.array(vop_data["dci_locat_ratio"], dtype=np.uint8)
                    self.vop_config.dci_global_lut = np.array(vop_data["dci_global_lut"], dtype=np.uint16)
                elif "s_vop_dci_interp_params" in data:
                    vop_data = data["s_vop_dci_interp_params"]
                    vop_dci_ctrl = vop_data['s_vop_dci_ctrl']
                    cf_params = vop_data["s_curve_fitting_params"]
                    he_params = vop_data["s_he_params"]
                    bs_params = vop_data["s_bs_params"]
                    ws_params = vop_data["s_ws_params"]
                    clahe_params = vop_data["s_clahe_params"]
                    abld_params = vop_data["s_time_abld_params"]
                    ca_params = vop_data["s_color_adjust_params"]
                    ## TODO: parse other params. need resolution info
                    self.vop_config.dci_enable = vop_dci_ctrl['i_dciEnable']
                else:
                    return False
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
            seed = self.randSeed + 1  # increase rand seed if no argument in
        random.seed(seed)
        np.random.seed(seed)
        self.randSeed = seed
        self.version = f"{self.name.lower()}_config_{self.platform.lower()}_random_seed_{seed}"

        ## parse dependent arguments
        img_wid = kwargs["width"] if "width" in kwargs else 1920
        img_hgt = kwargs["height"] if "height" in kwargs else 1080
        blk_size_hor = img_wid + (0 if img_wid < 1080 else 15) >> 4
        blk_size_ver = img_hgt + (0 if img_hgt < 1080 else 15) >> 4
        blk_size_hor_half = (blk_size_hor + 1) >> 1
        blk_size_ver_half = (blk_size_ver + 1) >> 1
        lum_zero = random.randint(0, 255)
        lum_thr = lum_zero + random.randint(-40, 40)
        while lum_thr == lum_zero:
            lum_thr = lum_zero + random.randint(-40, 40)
        if lum_zero > lum_thr:
            lum_zero, lum_thr = lum_thr, lum_zero
        lum_zero *= 4
        lum_thr *= 4

        ## random config for vdpp
        self.vdpp_config.working_mode = 2 if (img_wid <= 1920 and img_hgt <= 2048) else 3
        self.vdpp_config.dci_data_format = 4
        self.vdpp_config.dci_csc_range = int(random.randint(0, 99) < 50)  # 50%
        self.vdpp_config.dci_vsd_mode = random.randint(0, 2) if self.vdpp_config.working_mode == 3 else 0
        self.vdpp_config.dci_hsd_mode = random.randint(0, 1) if self.vdpp_config.working_mode == 3 else 0
        hsd_sample_num = 2 ** (self.vdpp_config.dci_hsd_mode + 1)  # 2,4
        vsd_sample_num = 2**self.vdpp_config.dci_vsd_mode  # 1,2,4
        self.vdpp_config.dci_alpha_swap = 0
        self.vdpp_config.dci_rb_swap = 0
        self.vdpp_config.dci_blk_hsize = img_wid / hsd_sample_num / 16
        self.vdpp_config.dci_blk_vsize = img_hgt / vsd_sample_num / 16
        self.vdpp_config.dci_blk_hsize = (
            math.floor(self.vdpp_config.dci_blk_hsize) if img_wid < 1080 else math.ceil(self.vdpp_config.dci_blk_hsize)
        )
        self.vdpp_config.dci_blk_vsize = (
            math.floor(self.vdpp_config.dci_blk_vsize) if img_hgt < 1080 else math.ceil(self.vdpp_config.dci_blk_vsize)
        )

        ## random config for vop
        self.vop_config.dci_enable = int(random.randint(0, 99) < 95)  # 95% enable
        self.vop_config.blk_size_fix = round(2**25 / ((blk_size_hor - 1) * (blk_size_ver - 1)))
        self.vop_config.act_width = img_wid  # TODO: could be smaller than img_wid
        self.vop_config.act_height = img_hgt  # TODO: could be smaller than img_hgt
        self.vop_config.act_start_h_idx = 0
        self.vop_config.act_start_v_idx = 0
        self.vop_config.act_start_h_offset = clamp(
            0 - blk_size_hor_half - (self.vop_config.act_start_h_idx - 1) * blk_size_hor, 0, img_wid
        )
        self.vop_config.act_start_v_offset = clamp(
            0 - blk_size_ver_half - (self.vop_config.act_start_v_idx - 1) * blk_size_ver, 0, img_hgt
        )
        self.vop_config.act_blk_size_h = blk_size_hor
        self.vop_config.act_blk_size_v = blk_size_ver
        self.vop_config.ca_enable = int(random.randint(0, 99) < 50)  # 50% enable
        self.vop_config.sat_w = random.randint(0, 64)  # u7
        self.vop_config.luma_sat_adj_zero = lum_zero
        self.vop_config.luma_sat_adj_thrd = lum_thr
        self.vop_config.luma_sat_adj_k = round(2**10 / max(1.0, lum_thr - lum_zero))
        self.vop_config.dci_local_lut = np.random.randint(0, 1023, size=16 * 16 * 16, dtype=np.uint16)
        self.vop_config.dci_locat_ratio = np.random.randint(0, 32, size=16 * 16, dtype=np.uint8)
        self.vop_config.dci_global_lut = np.random.randint(0, 1023, size=256, dtype=np.uint16)
        self.logger.info(f"generated a random config with seed={seed}")
        return True

class DciUserConfig(ModuleConfigCore):
    def __init__(self, name: str = "DCI", platform: str = "unknown"):
        super().__init__(name, platform)

        ## for vdpp_hist_cnt
        self.hist_pre_vhsd_mode = 0  # 0-MANUAL_CONFIG, 1-AUTO_CONFIG
        self.hist_hsd_mode = 0  # 0-disable, 1-x2
        self.hist_vsd_mode = 0  # 0-disable, 1-x2, 2-x4

        ## for vop_dci_interp
        self.ctrl_enable = 1
        self.ctrl_vopIn_csc_range = 1  # 0-LIMIT, 1-FULL
        self.ctrl_vop_srand_seed = -1
        self.ctrl_dci_CF_HE_ratio = 64
        self.ctrl_dci_ACT_area_l = 0
        self.ctrl_dci_ACT_area_r = 0
        self.ctrl_dci_ACT_area_u = 0
        self.ctrl_dci_ACT_area_d = 0
        self.ctrl_reg_ctrl_mode = 0
        self.ctrl_reg_file_path = ""
        self.ctrl_lut_file_path = ""

        self.cf_dciWgtCoef_low = np.zeros(33, dtype=np.uint16)
        self.cf_dciWgtCoef_mid = np.zeros(33, dtype=np.uint16)
        self.cf_dciWgtCoef_high = np.zeros(33, dtype=np.uint16)
        self.cf_dciWeight_low = np.zeros(32, dtype=np.uint16)
        self.cf_dciWeight_mid = np.zeros(32, dtype=np.uint16)
        self.cf_dciWeight_high = np.zeros(32, dtype=np.uint16)
        self.cf_gain_low = 32
        self.cf_gain_mid = 32
        self.cf_gain_high = 32
        self.cf_hist_cor_thr0 = 0
        self.cf_hist_cor_thr1 = 0
        self.cf_hist_cor_thr2 = 0

        self.he_split_point = 125
        self.he_left_clip = 1.0
        self.he_right_clip = 1.0
        self.he_overlap = 16

        self.bs_enable = 0
        self.bs_set_point = 80
        self.bs_ratio = 64
        self.bs_overlap = 0

        self.ws_enable = 0
        self.ws_set_point = 80
        self.ws_ratio = 64
        self.ws_overlap = 8

        self.clahe_en = 1
        self.clahe_clip_value = 1.0
        self.clahe_local_ratio = 19
        self.clahe_left_alpha = 3.0
        self.clahe_left_ThrLmin = 0.5
        self.clahe_left_ThrLmax = 2.3
        self.clahe_left_lumRatio = 0.7
        self.clahe_right_alpha = 1.5
        self.clahe_right_ThrRmin = 0.7
        self.clahe_right_ThrRmax = 3.0

        self.abld_hist_abld_ratio = 8
        self.abld_clahe_abld_ratio = 0.93
        self.abld_hist_wgt_high = 0
        self.abld_hist_wgt_mid = 0
        self.abld_hist_wgt_low = 0
        self.abld_metricAbldCoef0 = 8
        self.abld_metricAbldCoef1 = 8
        self.abld_metricAbldCoef2 = 8
        self.abld_minLuma = 0
        self.abld_maxLuma = 1023
        self.abld_minLuma_abld_ratio = 26
        self.abld_maxLuma_abld_ratio = 26
        self.abld_scd_flag = 1
        self.abld_scd_thr = 896
        self.abld_clahe_scd_thr_max = 896
        self.abld_clahe_scd_thr_min = 38

        self.ca_enable = 1
        self.ca_saturation_w = 56
        self.ca_adj_luma_coring_zero = 8
        self.ca_adj_luma_coring_thrd = 16

    # ------------------------------------------------------------------ #
    # dump / load — JSON I/O                                             #
    # ------------------------------------------------------------------ #

    def _to_dict(self, add_pqtuning_header: bool = False) -> dict:
        """Serialize to the nested dict matching dci_config JSON structure."""
        dic = {
            "s_vdpp_hist_cnt": {
                "i_pre_vhsd_mode_auto_config": self.hist_pre_vhsd_mode,
                "dci_hsd_mode": self.hist_hsd_mode,
                "dci_vsd_mode": self.hist_vsd_mode,
            },
            "s_vop_dci_interp_params": {
                "s_vop_dci_ctrl": {
                    "i_dciEnable": int(self.ctrl_enable),
                    "i_vopIn_csc_range": self.ctrl_vopIn_csc_range,
                    "i_vop_srand_seed": self.ctrl_vop_srand_seed,
                    "i_dci_CF_HE_ratio": self.ctrl_dci_CF_HE_ratio,
                    "i_dci_ACT_area_l": self.ctrl_dci_ACT_area_l,
                    "i_dci_ACT_area_r": self.ctrl_dci_ACT_area_r,
                    "i_dci_ACT_area_u": self.ctrl_dci_ACT_area_u,
                    "i_dci_ACT_area_d": self.ctrl_dci_ACT_area_d,
                },
                "s_curve_fitting_params": {
                    "t_dciWgtCoef_low": NoIndent(self.cf_dciWgtCoef_low.tolist()),
                    "t_dciWgtCoef_mid": NoIndent(self.cf_dciWgtCoef_mid.tolist()),
                    "t_dciWgtCoef_high": NoIndent(self.cf_dciWgtCoef_high.tolist()),
                    "t_dciWeight_low": NoIndent(self.cf_dciWeight_low.tolist()),
                    "t_dciWeight_mid": NoIndent(self.cf_dciWeight_mid.tolist()),
                    "t_dciWeight_high": NoIndent(self.cf_dciWeight_high.tolist()),
                    "i_gain_low": self.cf_gain_low,
                    "i_gain_mid": self.cf_gain_mid,
                    "i_gain_high": self.cf_gain_high,
                    "i_hist_cor_thr0": self.cf_hist_cor_thr0,
                    "i_hist_cor_thr1": self.cf_hist_cor_thr1,
                    "i_hist_cor_thr2": self.cf_hist_cor_thr2,
                },
                "s_he_params": {
                    "i_dci_HE_splitPoint": self.he_split_point,
                    "i_dci_HE_leftClip": self.he_left_clip,
                    "i_dci_HE_rightClip": self.he_right_clip,
                    "i_dci_HE_overLap": self.he_overlap,
                },
                "s_bs_params": {
                    "i_dci_BS_enable": int(self.bs_enable),
                    "i_dci_BS_set_point": self.bs_set_point,
                    "i_dci_BS_ratio": self.bs_ratio,
                    "i_dci_BS_overlap": self.bs_overlap,
                },
                "s_ws_params": {
                    "i_dci_WS_enable": self.ws_enable,
                    "i_dci_WS_set_point": self.ws_set_point,
                    "i_dci_WS_ratio": self.ws_ratio,
                    "i_dci_WS_overlap": self.ws_overlap,
                },
                "s_clahe_params": {
                    "i_dci_CLAHE_en": int(self.clahe_en),
                    "i_dci_CLAHE_clip_value": self.clahe_clip_value,
                    "i_dci_CLAHE_LocalRatio": self.clahe_local_ratio,
                    "i_left_alpha": self.clahe_left_alpha,
                    "i_left_ThrLmin": self.clahe_left_ThrLmin,
                    "i_left_ThrLmax": self.clahe_left_ThrLmax,
                    "i_left_lumRatio": self.clahe_left_lumRatio,
                    "i_right_alpha": self.clahe_right_alpha,
                    "i_right_ThrRmin": self.clahe_right_ThrRmin,
                    "i_right_ThrRmax": self.clahe_right_ThrRmax,
                },
                "s_time_abld_params": {
                    "i_dci_hist_abld_ratio": self.abld_hist_abld_ratio,
                    "i_dci_clahe_abld_ratio": self.abld_clahe_abld_ratio,
                    "i_dci_hist_wgt_high": self.abld_hist_wgt_high,
                    "i_dci_hist_wgt_mid": self.abld_hist_wgt_mid,
                    "i_dci_hist_wgt_low": self.abld_hist_wgt_low,
                    "i_dci_metricAbldCoef0": self.abld_metricAbldCoef0,
                    "i_dci_metricAbldCoef1": self.abld_metricAbldCoef1,
                    "i_dci_metricAbldCoef2": self.abld_metricAbldCoef2,
                    "i_dci_minLuma": self.abld_minLuma,
                    "i_dci_maxLuma": self.abld_maxLuma,
                    "i_dci_minLuma_abld_ratio": self.abld_minLuma_abld_ratio,
                    "i_dci_maxLuma_abld_ratio": self.abld_maxLuma_abld_ratio,
                    "i_scd_flag": self.abld_scd_flag,
                    "i_dci_scd_thr": self.abld_scd_thr,
                    "i_dci_clahe_scd_thr_max": self.abld_clahe_scd_thr_max,
                    "i_dci_clahe_scd_thr_min": self.abld_clahe_scd_thr_min,
                },
                "s_color_adjust_params": {
                    "i_dci_CA_enable": int(self.ca_enable),
                    "i_dci_CA_saturation_w": self.ca_saturation_w,
                    "i_dci_CA_adj_luma_coring_zero": self.ca_adj_luma_coring_zero,
                    "i_dci_CA_adj_luma_coring_thrd": self.ca_adj_luma_coring_thrd,
                },
            },
        }
        data = {"pq_tuning_param": {"dci": dic}} if add_pqtuning_header else dic
        return data

    def dump(self, filename: str = "", pretty_array_stdout: int = 32) -> bool:
        """Write config to a JSON file or print to stdout."""
        data = self._to_dict(add_pqtuning_header=True)
        if not filename:
            self.pretty_print_dict("dci", data, indent=2, pretty_array_stdout=pretty_array_stdout)
            return True
        try:
            json_data = json.dumps(data, indent=4, ensure_ascii=False, cls=CompactArrayEncoder)
            with open(filename, "w") as f:
                f.write(json_data)
            self.logger.info(f"User config saved to '{filename}'")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False

    def load(self, filename: str) -> bool:
        """Load config from a JSON file.

        Accepts both full config files (with global_param / pq_tuning_param)
        and standalone DCI section dumps.
        """
        if not os.path.exists(filename):
            self.logger.error(f"Config file '{filename}' not found")
            return False

        try:
            with open(filename, "r") as f:
                root = json.load(f)

            # Unwrap from pq_tuning_param -> dci if present
            data = root
            if "pq_tuning_param" in root and "dci" in root["pq_tuning_param"]:
                data = root["pq_tuning_param"]["dci"]
            elif "s_vdpp_hist_cnt" not in data and "s_vop_dci_interp_params" not in data:
                self.logger.error(f"No DCI config section found in '{filename}'")
                return False

            # s_vdpp_hist_cnt
            vdpp = data.get("s_vdpp_hist_cnt", {})
            self.hist_pre_vhsd_mode = vdpp.get("i_pre_vhsd_mode_auto_config", self.hist_pre_vhsd_mode)
            self.hist_hsd_mode = vdpp.get("dci_hsd_mode", self.hist_hsd_mode)
            self.hist_vsd_mode = vdpp.get("dci_vsd_mode", self.hist_vsd_mode)

            # s_vop_dci_interp_params
            interp = data.get("s_vop_dci_interp_params", {})

            ctrl = interp.get("s_vop_dci_ctrl", {})
            self.ctrl_enable = int(ctrl.get("i_dciEnable", self.ctrl_enable))
            self.ctrl_vopIn_csc_range = ctrl.get("i_vopIn_csc_range", self.ctrl_vopIn_csc_range)
            self.ctrl_vop_srand_seed = ctrl.get("i_vop_srand_seed", self.ctrl_vop_srand_seed)
            self.ctrl_dci_CF_HE_ratio = ctrl.get("i_dci_CF_HE_ratio", self.ctrl_dci_CF_HE_ratio)
            self.ctrl_dci_ACT_area_l = ctrl.get("i_dci_ACT_area_l", self.ctrl_dci_ACT_area_l)
            self.ctrl_dci_ACT_area_r = ctrl.get("i_dci_ACT_area_r", self.ctrl_dci_ACT_area_r)
            self.ctrl_dci_ACT_area_u = ctrl.get("i_dci_ACT_area_u", self.ctrl_dci_ACT_area_u)
            self.ctrl_dci_ACT_area_d = ctrl.get("i_dci_ACT_area_d", self.ctrl_dci_ACT_area_d)

            cf = interp.get("s_curve_fitting_params", {})
            self._load_array(cf, "t_dciWgtCoef_low", self.cf_dciWgtCoef_low)
            self._load_array(cf, "t_dciWgtCoef_mid", self.cf_dciWgtCoef_mid)
            self._load_array(cf, "t_dciWgtCoef_high", self.cf_dciWgtCoef_high)
            self._load_array(cf, "t_dciWeight_low", self.cf_dciWeight_low)
            self._load_array(cf, "t_dciWeight_mid", self.cf_dciWeight_mid)
            self._load_array(cf, "t_dciWeight_high", self.cf_dciWeight_high)
            self.cf_gain_low = cf.get("i_gain_low", self.cf_gain_low)
            self.cf_gain_mid = cf.get("i_gain_mid", self.cf_gain_mid)
            self.cf_gain_high = cf.get("i_gain_high", self.cf_gain_high)
            self.cf_hist_cor_thr0 = cf.get("i_hist_cor_thr0", self.cf_hist_cor_thr0)
            self.cf_hist_cor_thr1 = cf.get("i_hist_cor_thr1", self.cf_hist_cor_thr1)
            self.cf_hist_cor_thr2 = cf.get("i_hist_cor_thr2", self.cf_hist_cor_thr2)

            he = interp.get("s_he_params", {})
            self.he_split_point = he.get("i_dci_HE_splitPoint", self.he_split_point)
            self.he_left_clip = he.get("i_dci_HE_leftClip", self.he_left_clip)
            self.he_right_clip = he.get("i_dci_HE_rightClip", self.he_right_clip)
            self.he_overlap = he.get("i_dci_HE_overLap", self.he_overlap)

            bs = interp.get("s_bs_params", {})
            self.bs_enable = int(bs.get("i_dci_BS_enable", self.bs_enable))
            self.bs_set_point = bs.get("i_dci_BS_set_point", self.bs_set_point)
            self.bs_ratio = bs.get("i_dci_BS_ratio", self.bs_ratio)
            self.bs_overlap = bs.get("i_dci_BS_overlap", self.bs_overlap)

            ws = interp.get("s_ws_params", {})
            self.ws_enable = int(ws.get("i_dci_WS_enable", self.ws_enable))
            self.ws_set_point = ws.get("i_dci_WS_set_point", self.ws_set_point)
            self.ws_ratio = ws.get("i_dci_WS_ratio", self.ws_ratio)
            self.ws_overlap = ws.get("i_dci_WS_overlap", self.ws_overlap)

            clahe = interp.get("s_clahe_params", {})
            self.clahe_en = int(clahe.get("i_dci_CLAHE_en", self.clahe_en))
            self.clahe_clip_value = clahe.get("i_dci_CLAHE_clip_value", self.clahe_clip_value)
            self.clahe_local_ratio = clahe.get("i_dci_CLAHE_LocalRatio", self.clahe_local_ratio)
            self.clahe_left_alpha = clahe.get("i_left_alpha", self.clahe_left_alpha)
            self.clahe_left_ThrLmin = clahe.get("i_left_ThrLmin", self.clahe_left_ThrLmin)
            self.clahe_left_ThrLmax = clahe.get("i_left_ThrLmax", self.clahe_left_ThrLmax)
            self.clahe_left_lumRatio = clahe.get("i_left_lumRatio", self.clahe_left_lumRatio)
            self.clahe_right_alpha = clahe.get("i_right_alpha", self.clahe_right_alpha)
            self.clahe_right_ThrRmin = clahe.get("i_right_ThrRmin", self.clahe_right_ThrRmin)
            self.clahe_right_ThrRmax = clahe.get("i_right_ThrRmax", self.clahe_right_ThrRmax)

            abld = interp.get("s_time_abld_params", {})
            self.abld_hist_abld_ratio = abld.get("i_dci_hist_abld_ratio", self.abld_hist_abld_ratio)
            self.abld_clahe_abld_ratio = abld.get("i_dci_clahe_abld_ratio", self.abld_clahe_abld_ratio)
            self.abld_hist_wgt_high = abld.get("i_dci_hist_wgt_high", self.abld_hist_wgt_high)
            self.abld_hist_wgt_mid = abld.get("i_dci_hist_wgt_mid", self.abld_hist_wgt_mid)
            self.abld_hist_wgt_low = abld.get("i_dci_hist_wgt_low", self.abld_hist_wgt_low)
            self.abld_metricAbldCoef0 = abld.get("i_dci_metricAbldCoef0", self.abld_metricAbldCoef0)
            self.abld_metricAbldCoef1 = abld.get("i_dci_metricAbldCoef1", self.abld_metricAbldCoef1)
            self.abld_metricAbldCoef2 = abld.get("i_dci_metricAbldCoef2", self.abld_metricAbldCoef2)
            self.abld_minLuma = abld.get("i_dci_minLuma", self.abld_minLuma)
            self.abld_maxLuma = abld.get("i_dci_maxLuma", self.abld_maxLuma)
            self.abld_minLuma_abld_ratio = abld.get("i_dci_minLuma_abld_ratio", self.abld_minLuma_abld_ratio)
            self.abld_maxLuma_abld_ratio = abld.get("i_dci_maxLuma_abld_ratio", self.abld_maxLuma_abld_ratio)
            self.abld_scd_flag = abld.get("i_scd_flag", self.abld_scd_flag)
            self.abld_scd_thr = abld.get("i_dci_scd_thr", self.abld_scd_thr)
            self.abld_clahe_scd_thr_max = abld.get("i_dci_clahe_scd_thr_max", self.abld_clahe_scd_thr_max)
            self.abld_clahe_scd_thr_min = abld.get("i_dci_clahe_scd_thr_min", self.abld_clahe_scd_thr_min)

            ca = interp.get("s_color_adjust_params", {})
            self.ca_enable = int(ca.get("i_dci_CA_enable", self.ca_enable))
            self.ca_saturation_w = ca.get("i_dci_CA_saturation_w", self.ca_saturation_w)
            self.ca_adj_luma_coring_zero = ca.get("i_dci_CA_adj_luma_coring_zero", self.ca_adj_luma_coring_zero)
            self.ca_adj_luma_coring_thrd = ca.get("i_dci_CA_adj_luma_coring_thrd", self.ca_adj_luma_coring_thrd)

            self.version = f"loaded_{os.path.basename(filename)}"
            self.logger.info(f"Config loaded from '{filename}'")
            return True
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            self.logger.error(f"Load config failed in {os.path.basename(tb.filename)}-{tb.lineno}: {e}")
            return False

    @staticmethod
    def _load_array(src: dict, key: str, dst: np.ndarray):
        """Load a JSON array into an existing NumPy array placeholder."""
        if key in src:
            arr = np.asarray(src[key], dtype=dst.dtype)
            dst[: len(arr)] = arr

    # ------------------------------------------------------------------ #
    # Abstract method stubs                                              #
    # ------------------------------------------------------------------ #

    def check(self) -> bool:
        # Validate curve fitting array lengths
        expected_sizes = [
            (self.cf_dciWgtCoef_low, 33, "cf_dciWgtCoef_low"),
            (self.cf_dciWgtCoef_mid, 33, "cf_dciWgtCoef_mid"),
            (self.cf_dciWgtCoef_high, 33, "cf_dciWgtCoef_high"),
            (self.cf_dciWeight_low, 32, "cf_dciWeight_low"),
            (self.cf_dciWeight_mid, 32, "cf_dciWeight_mid"),
            (self.cf_dciWeight_high, 32, "cf_dciWeight_high"),
        ]
        for arr, expected_len, name in expected_sizes:
            if len(arr) != expected_len:
                self.logger.error(f"check failed: {name} length={len(arr)}, expected={expected_len}")
                self.valid = False
                return False
        self.valid = True
        return True

    def gen(self, seed: int = 114514, **kwargs) -> bool:
        self.randSeed = seed
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3538...")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    config = DciConfig(platform=args.platform)
    if args.interface == "gen":
        load_ok = config.gen(args.seed)
        if load_ok:
            config.dump(args.file)
    elif args.interface == "load":
        load_ok = config.load(args.file)
        if load_ok:
            config.dump()
    elif args.interface == "dump":
        load_ok = config.dump(args.file)
    else:
        config.logger.error(f"unknown interface '{args.interface}'!")
        load_ok = False

    check_ok = config.check()
    config.logger.info("load_ok: %s, check_ok: %s" % (load_ok, check_ok))

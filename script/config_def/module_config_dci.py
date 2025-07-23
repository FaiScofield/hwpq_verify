"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_dci.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-07-23
"""

import os
import sys
import json
import random
import argparse
from matplotlib.pylab import rand
import numpy as np

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *
from utils import NoIndent, CompactArrayEncoder


class DciConfig(ModuleConfigCore):
    def __init__(self, name: str = "DCI", version: str = "unknown"):
        super().__init__(name, version)

        # ## for vdpp_hist_cnt
        # self.hist_pre_vhsd_mode = 0  # 0-MANUAL_CONFIG, 1-AUTO_CONFIG
        # self.hist_hsd_mode = 0  # 0-disable, 1-x2
        # self.hist_vsd_mode = 0  # 0-disable, 1-x2, 2-x4

        # ## for vop_dci_interp
        # self.ctrl_enable = 1
        # self.ctrl_vopIn_csc_range = 1  # 0-LIMIT, 1-FULL
        # self.ctrl_vop_srand_seed = -1
        # self.ctrl_dci_CF_HE_ratio = 64
        # self.ctrl_dci_ACT_area_l = 0
        # self.ctrl_dci_ACT_area_r = 0
        # self.ctrl_dci_ACT_area_u = 0
        # self.ctrl_dci_ACT_area_d = 0
        # self.ctrl_reg_ctrl_mode = 0
        # self.ctrl_reg_file_path = ""
        # self.ctrl_lut_file_path = ""

        # self.cf_dciWgtCoef_low = np.zeros(33, dtype=np.uint16)
        # self.cf_dciWgtCoef_mid = np.zeros(33, dtype=np.uint16)
        # self.cf_dciWgtCoef_high = np.zeros(33, dtype=np.uint16)
        # self.cf_dciWeight_low = np.zeros(32, dtype=np.uint16)
        # self.cf_dciWeight_mid = np.zeros(32, dtype=np.uint16)
        # self.cf_dciWeight_high = np.zeros(32, dtype=np.uint16)
        # self.cf_gain_low = 32
        # self.cf_gain_mid = 32
        # self.cf_gain_high = 32
        # self.cf_hist_cor_thr0 = 0
        # self.cf_hist_cor_thr1 = 0
        # self.cf_hist_cor_thr2 = 0

        # self.he_split_point = 125
        # self.he_left_clip = 1.0
        # self.he_right_clip = 1.0
        # self.he_overlap = 16

        # self.bs_enable = 0
        # self.bs_set_point = 80
        # self.bs_ratio = 64
        # self.bs_overlap = 0

        # self.ws_enable = 0
        # self.ws_set_point = 80
        # self.ws_ratio = 64
        # self.ws_overlap = 8

        # self.clahe_en = 1
        # self.clahe_clip_value = 1.0
        # self.clahe_local_ratio = 19
        # self.clahe_left_alpha = 3.0
        # self.clahe_left_ThrLmin = 0.5
        # self.clahe_left_ThrLmax = 2.3
        # self.clahe_left_lumRatio = 0.7
        # self.clahe_right_alpha = 1.5
        # self.clahe_right_ThrRmin = 0.7
        # self.clahe_right_ThrRmax = 3.0

        # self.abld_hist_abld_ratio = 8
        # self.abld_clahe_abld_ratio = 0.93
        # self.abld_hist_wgt_high = 0
        # self.abld_hist_wgt_mid = 0
        # self.abld_hist_wgt_low = 0
        # self.abld_metricAbldCoef0 = 8
        # self.abld_metricAbldCoef1 = 8
        # self.abld_metricAbldCoef2 = 8
        # self.abld_minLuma = 0
        # self.abld_maxLuma = 1023
        # self.abld_minLuma_abld_ratio = 26
        # self.abld_maxLuma_abld_ratio = 26
        # self.abld_scd_flag = 1
        # self.abld_scd_thr = 896
        # self.abld_clahe_scd_thr_max = 896
        # self.abld_clahe_scd_thr_min = 38

        # self.ca_enable = 1
        # self.ca_saturation_w = 56
        # self.ca_adj_luma_coring_zero = 8
        # self.ca_adj_luma_coring_thrd = 16

        ## for RK3572 HW regs config
        self.hw_dci_enable = 1
        self.hw_blk_size_fix = 0  # u20
        self.hw_act_width = 0
        self.hw_act_height = 0
        self.hw_act_start_h_idx = 0  # u5
        self.hw_act_start_v_idx = 0  # u5
        self.hw_act_start_h_offset = 0  # u9
        self.hw_act_start_v_offset = 0  # u9
        self.hw_act_blk_size_h = 0  # u9
        self.hw_act_blk_size_v = 0  # u9
        self.hw_ca_enable = 0
        self.hw_sat_w = 0  # u7
        self.hw_luma_sat_adj_zero = 0  # u16
        self.hw_luma_sat_adj_thrd = 0  # u16
        self.hw_luma_sat_adj_k = 0  # u16
        self.hw_dci_local_lut = np.zeros(16 * 16 * 16, np.uint16)
        self.hw_dci_locat_ratio = np.zeros(16 * 16, np.uint8)
        self.hw_dci_global_lut = np.zeros(256, np.uint16)

    ## =============== overwrite methods  ===============
    def dump(self, filename=None) -> bool:
        data = {
            "version": self.version,
            "rand_seed": self.randSeed,
            "dci_enable": self.hw_dci_enable,
            "blk_size_fix": self.hw_blk_size_fix,
            "act_width": self.hw_act_width,
            "act_height": self.hw_act_height,
            "act_start_h_idx": self.hw_act_start_h_idx,
            "act_start_v_idx": self.hw_act_start_v_idx,
            "act_start_h_offset": self.hw_act_start_h_offset,
            "act_start_v_offset": self.hw_act_start_v_offset,
            "act_blk_size_h": self.hw_act_blk_size_h,
            "act_blk_size_v": self.hw_act_blk_size_v,
            "ca_enable": self.hw_ca_enable,
            "sat_w": self.hw_sat_w,
            "luma_sat_adj_zero": self.hw_luma_sat_adj_zero,
            "luma_sat_adj_thrd": self.hw_luma_sat_adj_thrd,
            "luma_sat_adj_k": self.hw_luma_sat_adj_k,
            "dci_local_lut": self.hw_dci_local_lut.flatten().tolist(),
            "dci_locat_ratio": self.hw_dci_locat_ratio.flatten().tolist(),
            "dci_global_lut": self.hw_dci_global_lut.flatten().tolist(),
            # "s_vdpp_hist_cnt": {
            #     "i_pre_vhsd_mode_auto_config": self.hist_pre_vhsd_mode,
            #     "dci_hsd_mode": self.hist_hsd_mode,
            #     "dci_vsd_mode": self.hist_vsd_mode,
            # },
            # "s_vop_dci_interp_params": {
            #     "s_vop_dci_ctrl": {
            #         "i_dciEnable": self.ctrl_enable,
            #         # TODO
            #     },
            #     "s_curve_fitting_params": {
            #         "t_dciWgtCoef_low": self.cf_dciWgtCoef_low.flatten().tolist(),
            #         "t_dciWgtCoef_mid": self.cf_dciWgtCoef_mid.flatten().tolist(),
            #         "t_dciWgtCoef_high": self.cf_dciWgtCoef_high.flatten().tolist(),
            #         "t_dciWeight_low": self.cf_dciWeight_low.flatten().tolist(),
            #         "t_dciWeight_mid": self.cf_dciWeight_mid.flatten().tolist(),
            #         "t_dciWeight_high": self.cf_dciWeight_high.flatten().tolist(),
            #         "i_gain_low": self.cf_gain_low,
            #         "i_gain_mid": self.cf_gain_mid,
            #         "i_gain_high": self.cf_gain_high,
            #         "i_hist_cor_thr0": self.cf_hist_cor_thr0,
            #         "i_hist_cor_thr1": self.cf_hist_cor_thr1,
            #         "i_hist_cor_thr2": self.cf_hist_cor_thr2,
            #     }
            #     # TODO
            # },
        }
        if filename == None or filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.pretty_print_dict(k, v)
            return True

        with open(filename, "w") as f:
            ## keep list data in one line by using NoIndent & CompactArrayEncoder
            # for k, v in data["s_vop_dci_interp_params"]["s_curve_fitting_params"].items():
            #     if k in [
            #         "t_dciWgtCoef_low",
            #         "t_dciWgtCoef_mid",
            #         "t_dciWgtCoef_high",
            #         "t_dciWeight_low",
            #         "t_dciWeight_mid",
            #         "t_dciWeight_high",
            #     ]:
            #         data["s_vop_dci_interp_params"]["s_curve_fitting_params"][k] = NoIndent(v)
            # nest_data = {"pq_tuning_param": {"dci": data}}
            for k, v in data.items():
                if k in [
                    "dci_local_lut",
                    "dci_locat_ratio",
                    "dci_global_lut",
                ]:
                    data[k] = NoIndent(v)
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
                # hist_data = data["s_vdpp_hist_cnt"]
                # param_data = data["s_vop_dci_interp_params"]
                # self.hist_pre_vhsd_mode = hist_data["i_pre_vhsd_mode_auto_config"]  # 0-MANUAL_CONFIG, 1-AUTO_CONFIG
                # self.hist_hsd_mode = hist_data["dci_hsd_mode"]  # 0-disable, 1-x2
                # self.hist_vsd_mode = hist_data["dci_vsd_mode"]  # 0-disable, 1-x2, 2-x4
                # self.ctrl_enable = param_data["s_vop_dci_ctrl"]["i_dciEnable"]
                # self.cf_dciWgtCoef_low = np.array(
                #     param_data["s_curve_fitting_params"]["t_dciWgtCoef_low"], dtype=np.uint16
                # )
                # self.cf_dciWgtCoef_mid = np.array(
                #     param_data["s_curve_fitting_params"]["t_dciWgtCoef_mid"], dtype=np.uint16
                # )
                # self.cf_dciWgtCoef_high = np.array(
                #     param_data["s_curve_fitting_params"]["t_dciWgtCoef_high"], dtype=np.uint16
                # )
                # self.cf_dciWeight_low = np.array(
                #     param_data["s_curve_fitting_params"]["t_dciWeight_low"], dtype=np.uint16
                # )
                # self.cf_dciWeight_mid = np.array(
                #     param_data["s_curve_fitting_params"]["t_dciWeight_mid"], dtype=np.uint16
                # )
                # self.cf_dciWeight_high = np.array(
                #     param_data["s_curve_fitting_params"]["t_dciWeight_high"], dtype=np.uint16
                # )
                # self.cf_gain_low = param_data["s_curve_fitting_params"]["i_gain_low"]
                # self.cf_gain_mid = param_data["s_curve_fitting_params"]["i_gain_mid"]
                # self.cf_gain_high = param_data["s_curve_fitting_params"]["i_gain_high"]
                # self.cf_hist_cor_thr0 = param_data["s_curve_fitting_params"]["i_hist_cor_thr0"]
                # self.cf_hist_cor_thr1 = param_data["s_curve_fitting_params"]["i_hist_cor_thr1"]
                # self.cf_hist_cor_thr2 = param_data["s_curve_fitting_params"]["i_hist_cor_thr2"]
                self.hw_dci_enable = data["dci_enable"]
                self.hw_blk_size_fix = data["blk_size_fix"]
                self.hw_act_width = data["act_width"]
                self.hw_act_height = data["act_height"]
                self.hw_act_start_h_idx = data["act_start_h_idx"]
                self.hw_act_start_v_idx = data["act_start_v_idx"]
                self.hw_act_start_h_offset = data["act_start_h_offset"]
                self.hw_act_start_v_offset = data["act_start_v_offset"]
                self.hw_act_blk_size_h = data["act_blk_size_h"]
                self.hw_act_blk_size_v = data["act_blk_size_v"]
                self.hw_ca_enable = data["ca_enable"]
                self.hw_sat_w = data["sat_w"]
                self.hw_luma_sat_adj_zero = data["luma_sat_adj_zero"]
                self.hw_luma_sat_adj_thrd = data["luma_sat_adj_thrd"]
                self.hw_luma_sat_adj_k = data["luma_sat_adj_k"]
                self.hw_dci_local_lut = np.array(data["dci_local_lut"], dtype=np.uint16)
                self.hw_dci_locat_ratio = np.array(data["dci_locat_ratio"], dtype=np.uint8)
                self.hw_dci_global_lut = np.array(data["dci_global_lut"], dtype=np.uint16)

                self.version = data["version"] if "version" in data else "unknown"
                self.randSeed = data["rand_seed"] if "rand_seed" in data else -1
                return True
        except Exception as e:
            self.logger.error(f"load config file '{filename}' failed: {e}")
            return False

    def check(self) -> bool:
        # TODO
        self.valid = True
        return self.valid

    def gen(self, seed: int = 114514, **kwargs) -> int:
        ## set random seed
        if seed == None:
            seed = self.randSeed + 1  # increase rand seed if no argument in
        random.seed(seed)
        np.random.seed(seed)

        ## parse dependent arguments
        img_wid = kwargs["width"] if "width" in kwargs else 1920
        img_hgt = kwargs["height"] if "height" in kwargs else 1080
        blk_size_hor = img_wid >> 4
        blk_size_ver = img_hgt >> 4
        blk_size_hor_half = (blk_size_hor + 1) >> 1
        blk_size_ver_half = (blk_size_ver + 1) >> 1
        lum_zero = random.randint(0, 255)
        lum_thr = lum_zero + random.randint(-40, 40)
        while (lum_thr == lum_zero):
            lum_thr = lum_zero + random.randint(-40, 40)
        if (lum_zero > lum_thr):
            lum_zero, lum_thr = lum_thr, lum_zero
        lum_zero *= 4
        lum_thr *= 4

        self.randSeed = seed
        self.version = f"{self.name.lower()}_config_rk3572_random_seed_{seed}"
        self.hw_dci_enable = int(random.randint(0, 95) > 0)  # 95% enable
        self.hw_blk_size_fix = round(2**25 / ((blk_size_hor - 1) * (blk_size_ver - 1)))
        self.hw_act_width = img_wid
        self.hw_act_height = img_hgt
        self.hw_act_start_h_idx = 0
        self.hw_act_start_v_idx = 0
        self.hw_act_start_h_offset = np.clip(
            0 - blk_size_hor_half - (self.hw_act_start_h_idx - 1) * blk_size_hor, 0, img_wid
        )
        self.hw_act_start_v_offset = np.clip(
            0 - blk_size_ver_half - (self.hw_act_start_v_idx - 1) * blk_size_ver, 0, img_hgt
        )
        self.hw_act_blk_size_h = blk_size_hor
        self.hw_act_blk_size_v = blk_size_ver
        self.hw_ca_enable = int(random.randint(0, 1) > 0)  # 50% enable
        self.hw_sat_w = random.randint(0, 64) # u7
        self.hw_luma_sat_adj_zero = lum_zero
        self.hw_luma_sat_adj_thrd = lum_thr
        self.hw_luma_sat_adj_k = round(2**10 / max(1.0, lum_thr - lum_zero))
        self.hw_dci_local_lut = np.random.randint(0, 1023, size=16*16*16, dtype=np.uint16)
        self.hw_dci_locat_ratio = np.random.randint(0, 32, size=16*16, dtype=np.uint8)
        self.hw_dci_global_lut = np.random.randint(0, 1023, size=256, dtype=np.uint16)
        self.logger.info(f"generated a random config with seed={seed}, passthrough={1}")
        return seed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    config = DciConfig()
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

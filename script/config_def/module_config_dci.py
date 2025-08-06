"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_dci.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-08-06
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

        ## for RK3572 VOP HW regs config
        self.vdpp_config = DciHWParam_VDPP("RK3572")
        self.vop_config = DciHWParam_VOP("RK3572")

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
                "dci_local_lut": self.vop_config.dci_local_lut.flatten().tolist(),
                "dci_locat_ratio": self.vop_config.dci_locat_ratio.flatten().tolist(),
                "dci_global_lut": self.vop_config.dci_global_lut.flatten().tolist(),
            },
        }
        if filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.pretty_print_dict(k, v, 2, pretty_array_stdout)
            return True

        with open(filename, "w") as f:
            ## keep list data in one line by using NoIndent & CompactArrayEncoder
            for k, v in data["vop_config"].items():
                if k in ["dci_local_lut", "dci_locat_ratio", "dci_global_lut"]:
                    data["vop_config"][k] = NoIndent(v)
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
        self.version = f"{self.name.lower()}_config_rk3572_random_seed_{seed}"

        ## parse dependent arguments
        img_wid = kwargs["width"] if "width" in kwargs else 1920
        img_hgt = kwargs["height"] if "height" in kwargs else 1080
        blk_size_hor = img_wid >> 4
        blk_size_ver = img_hgt >> 4
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

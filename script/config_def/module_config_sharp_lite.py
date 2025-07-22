"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_sharp_lite.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-10
Description :
LastEditTime: 2025-07-22
"""

import os
import sys
import json
import random
import argparse

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *


class SharpLiteConfig(ModuleConfigCore):
    def __init__(self, name: str = "SharpLite", version: str = "unknown"):
        super().__init__(name, version)
        self.sharp_lite_en = 1  # u1
        self.usm_sigma_0 = 0.7  # for gaussian 2D kernel0
        self.usm_sigma_1 = 0.7  # for gaussian 2D kernel1
        self.usm_gain_0 = 3.1  # gain of kernel0
        self.usm_gain_1 = 3.2  # gain of kernel1
        self.usm_coring_thr = 16  # u7, range: [0, 127]
        self.shoot_ctrl_en = 0  # u1
        self.shoot_ctrl_delta_offset = 16  # u8
        self.shoot_ctrl_pos = 16  # u7
        self.shoot_ctrl_neg = 16  # u7
        self.shoot_ctrl_pos_unlimit = 32  # u7
        self.shoot_ctrl_neg_unlimit = 32  # u7
        self.sharp_roi_enable = 0  # u1
        self.sharp_roi_xstart = 0  # u12
        self.sharp_roi_xend = 0  # u12
        self.sharp_roi_ystart = 0  # u12
        self.sharp_roi_yend = 0  # u12
        self.sharp_force_core_mode = 1  # enbale this if using below parameters directly to generate registers
        self.sharp_core_A = 16  # 3x3 gaussian kernel corner (0,2,6,8), s8 fixed, range: [-128, 127]
        self.sharp_core_B = 32  # 3x3 gaussian kernel edge   (1,3,5,7), s8 fixed, range: [-128, 127]
        self.sharp_core_C = 64  # 3x3 gaussian kernel center (4),       s8 fixed, range: [-128, 127]
        self.sharp_usm_gain = 303  # u7 fixed, range: [0, 1023]
        self.ink_enable = 0  # u1
        self.ink_mode = 0  # u2
        self.ink_idx_h = 0
        self.ink_idx_v = 0

    ## =============== overwrite methods  ===============
    def dump(self, filename=None) -> bool:
        data = {
            "version": self.version,
            "rand_seed": self.randSeed,
            "i_sharp_lite_en": self.sharp_lite_en,
            "f_usm_sigma_0": self.usm_sigma_0,
            "f_usm_sigma_1": self.usm_sigma_1,
            "f_usm_gain_0": self.usm_gain_0,
            "f_usm_gain_1": self.usm_gain_1,
            "f_usm_coring_thr": self.usm_coring_thr,
            "i_shoot_ctrl_en": self.shoot_ctrl_en,
            "i_shoot_ctrl_delta_offset": self.shoot_ctrl_delta_offset,
            "i_shoot_ctrl_pos": self.shoot_ctrl_pos,
            "i_shoot_ctrl_neg": self.shoot_ctrl_neg,
            "i_shoot_ctrl_pos_unlimit": self.shoot_ctrl_pos_unlimit,
            "i_shoot_ctrl_neg_unlimit": self.shoot_ctrl_neg_unlimit,
            "i_sharp_roi_enable": self.sharp_roi_enable,
            "i_sharp_roi_xstart": self.sharp_roi_xstart,
            "i_sharp_roi_xend": self.sharp_roi_xend,
            "i_sharp_roi_ystart": self.sharp_roi_ystart,
            "i_sharp_roi_yend": self.sharp_roi_yend,
            "i_sharp_force_core_mode": self.sharp_force_core_mode,
            "i_sharp_core_A": self.sharp_core_A,
            "i_sharp_core_B": self.sharp_core_B,
            "i_sharp_core_C": self.sharp_core_C,
            "i_sharp_usm_gain": self.sharp_usm_gain,
            "i_ink_enable": self.ink_enable,
            "i_ink_mode": self.ink_mode,
            "i_ink_idx_h": self.ink_idx_h,
            "i_ink_idx_v": self.ink_idx_v,
        }
        if filename == None or filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.logger.info(f"  - {k}: {v}")
            return True

        with open(filename, "w") as f:
            nest_data = {"pq_tuning_param": {"SHARPNESS_lite": data}}
            json.dump(nest_data, f, indent=4, ensure_ascii=False)
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
                    self.logger.info(f"load config from pq_tuning_param.SHARPNESS_lite ...")
                    data = data["pq_tuning_param"]["SHARPNESS_lite"]

                self.sharp_lite_en = data["i_sharp_lite_en"]
                self.usm_sigma_0 = data["f_usm_sigma_0"]
                self.usm_sigma_1 = data["f_usm_sigma_1"]
                self.usm_gain_0 = data["f_usm_gain_0"]
                self.usm_gain_1 = data["f_usm_gain_1"]
                self.usm_coring_thr = data["f_usm_coring_thr"]
                self.shoot_ctrl_en = data["i_shoot_ctrl_en"]
                self.shoot_ctrl_delta_offset = data["i_shoot_ctrl_delta_offset"]
                self.shoot_ctrl_pos = data["i_shoot_ctrl_pos"]
                self.shoot_ctrl_neg = data["i_shoot_ctrl_neg"]
                self.shoot_ctrl_pos_unlimit = data["i_shoot_ctrl_pos_unlimit"]
                self.shoot_ctrl_neg_unlimit = data["i_shoot_ctrl_neg_unlimit"]
                self.sharp_roi_enable = data["i_sharp_roi_enable"]
                self.sharp_roi_xstart = data["i_sharp_roi_xstart"]
                self.sharp_roi_xend = data["i_sharp_roi_xend"]
                self.sharp_roi_ystart = data["i_sharp_roi_ystart"]
                self.sharp_roi_yend = data["i_sharp_roi_yend"]
                self.sharp_force_core_mode = data["i_sharp_force_core_mode"]
                self.sharp_core_A = data["i_sharp_core_A"]
                self.sharp_core_B = data["i_sharp_core_B"]
                self.sharp_core_C = data["i_sharp_core_C"]
                self.sharp_usm_gain = data["i_sharp_usm_gain"]
                self.ink_enable = data["i_ink_enable"]
                self.ink_mode = data["i_ink_mode"]
                self.ink_idx_h = data["i_ink_idx_h"]
                self.ink_idx_v = data["i_ink_idx_v"]
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

        self.randSeed = seed
        self.version = f"{self.name.lower()}_config_rk3572_random_seed_{seed}"

        self.sharp_lite_en = int(random.randint(0, 9) > 0)  # %90 be ON
        self.usm_sigma_0 = random.random() * 3 + 1e-3  # [1e-3, 3]
        self.usm_sigma_1 = random.random() * 3 + 1e-3  # [1e-3, 3]
        self.usm_gain_0 = random.random() * 5 + 1e-3  # [1e-3, 5]
        self.usm_gain_1 = random.random() * 5 + 1e-3  # [1e-3, 5]
        self.usm_coring_thr = random.randint(0, 127)
        self.shoot_ctrl_en = random.randint(0, 1)
        self.shoot_ctrl_delta_offset = random.randint(0, 255)
        self.shoot_ctrl_pos = random.randint(0, 127)
        self.shoot_ctrl_neg = random.randint(0, 127)
        self.shoot_ctrl_pos_unlimit = max(random.randint(0, 127), self.shoot_ctrl_pos)
        self.shoot_ctrl_neg_unlimit = max(random.randint(0, 127), self.shoot_ctrl_neg)
        self.sharp_roi_enable = int(random.randint(0, 9) > 6)  # %30 be ON
        self.sharp_roi_xstart = random.randint(0, 1000)
        self.sharp_roi_xend = random.randint(4, 1200)
        self.sharp_roi_ystart = random.randint(0, 600)
        self.sharp_roi_yend = random.randint(4, 800)
        self.sharp_force_core_mode = random.randint(0, 1)  # %50 be ON
        self.sharp_core_A = random.randint(-128, 127)
        self.sharp_core_B = random.randint(-128, 127)
        self.sharp_core_C = random.randint(-128, 127)
        # coefSum = (self.sharp_core_A + self.sharp_core_B) * 4 + self.sharp_core_C
        # while coefSum > 255: # sum nedd to be <= 255!
        #     delta = (coefSum - 255 + 9) // 9
        #     self.sharp_core_A = max(self.sharp_core_A - delta * 4, 0)
        #     self.sharp_core_B = max(self.sharp_core_B - delta * 4, 0)
        #     self.sharp_core_C = max(self.sharp_core_C - delta * 1, 0)
        #     coefSum = (self.sharp_core_A + self.sharp_core_B) * 4 + self.sharp_core_C
        self.sharp_usm_gain = random.randint(0, 1023)
        self.ink_enable = 0
        self.ink_mode = 0
        self.ink_idx_h = 0
        self.ink_idx_v = 0

        ## check if passthrough mode
        passthrough = None
        if "passthrough" in kwargs:
            passthrough = int(kwargs["passthrough"])
            self.sharp_force_core_mode = passthrough

        self.logger.info(f"generated a random config with seed={seed}, passthrough={passthrough}")
        return seed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.add_argument("-s", "--passthrough", type=bool, default=True, help="设置寄存器直通")
    parser.print_usage()
    args = parser.parse_args()

    config = SharpLiteConfig()
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

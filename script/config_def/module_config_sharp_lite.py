"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_sharp_lite.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-10
Description :
LastEditTime: 2025-07-10
"""

import os
import sys
import json
import random

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
    def dump(self, filename=None):
        if filename == None or filename == "":
            print(f"[{self.name}] Config parameters shown below:")
            dumpdata = "".join([f"  - %s: %s\n" % item for item in self.__dict__.items()])
            print(dumpdata)
            return True

        with open(filename, "w") as f:
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
            nest_data = {"pq_tuning_param": {"SHARPNESS_lite": data}}
            json.dump(nest_data, f, indent=4, ensure_ascii=False)
            return True

        return False

    def load(self, filename):
        # check config file validity
        if not os.path.exists(filename):
            print(f"[{self.name}] config file '{filename}' doesn't exist!")
            return False
        if not filename.endswith(".json"):
            print(f"[{self.name}] config file '{filename}' is not a json file!")
            return False

        try:
            with open(filename, "r") as f:
                data = json.load(f)
                if "pq_tuning_param" in data:
                    print(f"[{self.name}] load config from pq_tuning_param.SHARPNESS_lite ...")
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
            print(f"[{self.name}] load config file '{filename}' failed: {e}")
            return False

    def check(self):
        # TODO
        self.valid = True
        return self.valid

    def gen(self, seed: int = 114514):
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

        return seed


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: %s load <config_json_file>" % sys.argv[0])
        print("Usage: %s gen <rand_seed>" % sys.argv[0])
        exit(-1)

    config = SharpLiteConfig()
    if sys.argv[1] == "gen":
        seed = config.gen(int(sys.argv[2]))
        load_ok = True
    elif sys.argv[1] == "load":
        load_ok = config.load(sys.argv[2])
        if not load_ok:
            exit(-1)
    else:
        print("Usage: %s load <config_json_file>" % sys.argv[0])
        print("Usage: %s gen <config_json_file>" % sys.argv[0])
        exit(-1)

    check_ok = config.check()
    print("load_ok: %s, check_ok: %s" % (load_ok, check_ok))
    config.dump()

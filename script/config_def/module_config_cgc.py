"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_cgc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-29
Description :
LastEditTime: 2025-08-06
"""

import os
import sys
import json
import random
import argparse
import traceback
import numpy as np

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *
from utils import NoIndent, CompactArrayEncoder


class CgcHWParam_VOP:
    def __init__(self, platform: str = "RK3572"):
        self.platform = platform

        self.log10_s_fix = 0  # u12, [0, 4080]
        self.log10_r_ootf_fix = 0  # s12, [-512, 1024]
        self.log10_t_fix_params = 0  # u14, [0, 9826]
        self.Mat_R2R = np.zeros((3, 3), dtype=np.int16)  # s16
        self.eotf_diff_shift_tab = np.zeros(137, dtype=np.uint16)  # u13
        self.eotf_start_idx_tab = np.zeros(11, dtype=np.uint16)  # u11
        self.eotf_attbits_change_idx_tab = np.zeros(11, dtype=np.uint16)  # u10
        self.cgc_oetf_tab = np.zeros(117, dtype=np.uint32)  # u32: [31:0]=[value:bits:seg=16:4:12]


class CgcConfig(ModuleConfigCore):
    def __init__(self, name: str = "CGC", platform: str = "RK3572"):
        super().__init__(name, platform)

        self.cgc_en = 1
        self.sdr2hdr_enable = 0
        self.cgc_params = CgcHWParam_VOP(self.platform)

    ## =============== overwrite methods  ===============
    def dump(self, filename: str = "", pretty_array_stdout: int = 32) -> bool:
        data = {
            "version": self.version,
            "randSeed": self.randSeed,
            "sdr2hdr_enable": self.sdr2hdr_enable,
            "cgc_en": self.cgc_en,
            "HDRvivid": {
                "cgc_params": {
                    "log10_s_fix": self.cgc_params.log10_s_fix,
                    "log10_r_ootf_fix": self.cgc_params.log10_r_ootf_fix,
                    "log10_t_fix_params": self.cgc_params.log10_t_fix_params,
                    "Mat_R2R": self.cgc_params.Mat_R2R.flatten().tolist(),
                    "eotf_diff_shift_tab": self.cgc_params.eotf_diff_shift_tab.flatten().tolist(),
                    "eotf_start_idx_tab": self.cgc_params.eotf_start_idx_tab.flatten().tolist(),
                    "eotf_attbits_change_idx_tab": self.cgc_params.eotf_attbits_change_idx_tab.flatten().tolist(),
                    "cgc_oetf_tab": self.cgc_params.cgc_oetf_tab.flatten().tolist(),
                }
            },
        }
        if filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.pretty_print_dict(k, v, 2, pretty_array_stdout)
            return True

        with open(filename, "w") as f:
            ## keep list data in one line by using NoIndent & CompactArrayEncoder
            for k, v in data["HDRvivid"]["cgc_params"].items():
                if k in [
                    "Mat_R2R",
                    "eotf_attbits_change_idx_tab",
                    "eotf_start_idx_tab",
                    "eotf_diff_shift_tab",
                    "cgc_oetf_tab",
                ]:
                    data["HDRvivid"]["cgc_params"][k] = NoIndent(v)
            nest_data = {"HDR": data}
            json_data = json.dumps(nest_data, indent=4, ensure_ascii=False, cls=CompactArrayEncoder)
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
                if "HDR" in data:
                    self.logger.info(f"load config from HDR.HDRvivid ...")
                    data = data["HDR"]
                self.cgc_en = data["cgc_en"]
                self.sdr2hdr_enable = data["sdr2hdr_enable"]
                if "HDRvivid" in data:
                    data = data["HDRvivid"]
                data = data["cgc_params"]
                self.cgc_params.log10_s_fix = data["log10_s_fix"]
                self.cgc_params.log10_r_ootf_fix = data["log10_r_ootf_fix"]
                self.cgc_params.log10_t_fix_params = data["log10_t_fix_params"]
                self.cgc_params.Mat_R2R = np.array(data["Mat_R2R"], dtype=np.int16)
                self.cgc_params.eotf_attbits_change_idx_tab = np.array(
                    data["eotf_attbits_change_idx_tab"], dtype=np.uint16
                )
                self.cgc_params.eotf_start_idx_tab = np.array(data["eotf_start_idx_tab"], dtype=np.uint16)
                self.cgc_params.eotf_diff_shift_tab = np.array(data["eotf_diff_shift_tab"], dtype=np.uint16)
                self.cgc_params.cgc_oetf_tab = np.array(data["cgc_oetf_tab"], dtype=np.uint32)

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
            seed = self.randSeed + 1  # increase rand seed if no argument in
        random.seed(seed)
        np.random.seed(seed)

        self.randSeed = seed
        self.version = f"{self.name.lower()}_config_{self.platform.lower()}_random_seed_{seed}"

        self.cgc_en = int(random.randint(0, 99) < 95)  # 95% be ON
        self.sdr2hdr_enable = 0  # aways be 0
        self.cgc_params.log10_s_fix = random.randint(0, 4080)
        self.cgc_params.log10_r_ootf_fix = random.randint(-512, 1024)
        self.cgc_params.log10_t_fix_params = random.randint(0, 9826)
        self.cgc_params.Mat_R2R = np.random.randint(-(2**15), 2**15 - 1, size=(3, 3), dtype=np.int16)  # s16
        self.cgc_params.eotf_diff_shift_tab = np.random.randint(0, 2**13 - 1, size=137, dtype=np.uint16)  # u13
        self.cgc_params.eotf_start_idx_tab = np.random.randint(0, 2**11 - 1, size=11, dtype=np.uint16)  # u11
        self.cgc_params.eotf_attbits_change_idx_tab = np.random.randint(0, 2**10 - 1, size=11, dtype=np.uint16)  # u10
        self.cgc_params.cgc_oetf_tab = np.random.randint(0, 2**32 - 1, size=117, dtype=np.uint32)  # u32

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

    config = CgcConfig(platform=args.platform)
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

"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_acm.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-07-29
"""

import os
import sys
import json
import random
import argparse
import numpy as np

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *
from utils import NoIndent, CompactArrayEncoder


class AcmConfig(ModuleConfigCore):
    def __init__(self, name: str = "ACM", version: str = "unknown"):
        super().__init__(name, version)

        self.acmEnable = 1
        self.acmTableDeltaYbyH = np.zeros(65, dtype=np.int16)  # [-255, 255]
        self.acmTableDeltaHbyH = np.zeros(65, dtype=np.int8)  # [- 64,  64]
        self.acmTableDeltaSbyH = np.zeros(65, dtype=np.int16)  # [-255, 255]
        self.acmTableGainYbyY = np.zeros(17 * 9, dtype=np.int8)  # [-127, 127]
        self.acmTableGainHbyY = np.zeros(17 * 9, dtype=np.int8)  # [-127, 127]
        self.acmTableGainSbyY = np.zeros(17 * 9, dtype=np.int8)  # [-127, 127]
        self.acmTableGainYbyS = np.zeros(17 * 13, dtype=np.int8)  # [-127, 127]
        self.acmTableGainHbyS = np.zeros(17 * 13, dtype=np.int8)  # [-127, 127]
        self.acmTableGainSbyS = np.zeros(17 * 13, dtype=np.int8)  # [-127, 127]
        self.lumGain = 256  # [0, (256), 1023]
        self.hueGain = 256  # [0, (256), 1023]
        self.satGain = 256  # [0, (256), 1023]

    ## =============== overwrite methods  ===============
    def dump(self, filename: str = "", pretty_array_stdout: int = 32) -> bool:
        data = {
            "version": self.version,
            "randSeed": self.randSeed,
            "acmEnable": self.acmEnable,
            "acmTableDeltaYbyH": self.acmTableDeltaYbyH.flatten().tolist(),
            "acmTableDeltaHbyH": self.acmTableDeltaHbyH.flatten().tolist(),
            "acmTableDeltaSbyH": self.acmTableDeltaSbyH.flatten().tolist(),
            "acmTableGainYbyY": self.acmTableGainYbyY.flatten().tolist(),
            "acmTableGainHbyY": self.acmTableGainHbyY.flatten().tolist(),
            "acmTableGainSbyY": self.acmTableGainSbyY.flatten().tolist(),
            "acmTableGainYbyS": self.acmTableGainYbyS.flatten().tolist(),
            "acmTableGainHbyS": self.acmTableGainHbyS.flatten().tolist(),
            "acmTableGainSbyS": self.acmTableGainSbyS.flatten().tolist(),
            "lumGain": self.lumGain,
            "hueGain": self.hueGain,
            "satGain": self.satGain,
        }
        if filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.pretty_print_dict(k, v, 2, pretty_array_stdout)
            return True

        with open(filename, "w") as f:
            ## keep list data in one line by using NoIndent & CompactArrayEncoder
            for k, v in data.items():
                if k in [
                    "acmTableDeltaYbyH",
                    "acmTableDeltaHbyH",
                    "acmTableDeltaSbyH",
                    "acmTableGainYbyY",
                    "acmTableGainHbyY",
                    "acmTableGainSbyY",
                    "acmTableGainYbyS",
                    "acmTableGainHbyS",
                    "acmTableGainSbyS",
                ]:
                    data[k] = NoIndent(v)
            nest_data = {"pq_tuning_param": {"acm": data}}
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
                if "pq_tuning_param" in data:
                    self.logger.info(f"load config from pq_tuning_param.acm ...")
                    data = data["pq_tuning_param"]["acm"]
                self.acmEnable = data["acmEnable"]
                self.acmTableDeltaYbyH = np.array(data["acmTableDeltaYbyH"], dtype=np.int16)
                self.acmTableDeltaHbyH = np.array(data["acmTableDeltaHbyH"], dtype=np.int8)
                self.acmTableDeltaSbyH = np.array(data["acmTableDeltaSbyH"], dtype=np.int16)
                self.acmTableGainYbyY = np.array(data["acmTableGainYbyY"], dtype=np.int8)
                self.acmTableGainHbyY = np.array(data["acmTableGainHbyY"], dtype=np.int8)
                self.acmTableGainSbyY = np.array(data["acmTableGainSbyY"], dtype=np.int8)
                self.acmTableGainYbyS = np.array(data["acmTableGainYbyS"], dtype=np.int8)
                self.acmTableGainHbyS = np.array(data["acmTableGainHbyS"], dtype=np.int8)
                self.acmTableGainSbyS = np.array(data["acmTableGainSbyS"], dtype=np.int8)
                self.lumGain = data["lumGain"]
                self.hueGain = data["hueGain"]
                self.satGain = data["satGain"]
                self.version = data["version"] if "version" in data else "unknown"
                self.randSeed = data["randSeed"] if "randSeed" in data else -1
                return True
        except Exception as e:
            self.logger.error(f"load config file '{filename}' failed: {e}")
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

        self.acmEnable = int(random.randint(0, 95) > 0)  # %95 be ON
        self.lumGain = random.randint(0, 1023)
        self.hueGain = random.randint(0, 1023)
        self.satGain = random.randint(0, 1023)
        self.acmTableDeltaYbyH = np.random.randint(-256, 255, size=65, dtype=np.int16)
        self.acmTableDeltaHbyH = np.random.randint(-64, 63, size=65, dtype=np.int8)
        self.acmTableDeltaSbyH = np.random.randint(-256, 255, size=65, dtype=np.int16)
        self.acmTableGainYbyY = np.random.randint(-128, 127, size=17 * 9, dtype=np.int8)
        self.acmTableGainHbyY = np.random.randint(-128, 127, size=17 * 9, dtype=np.int8)
        self.acmTableGainSbyY = np.random.randint(-128, 127, size=17 * 9, dtype=np.int8)
        self.acmTableGainYbyS = np.random.randint(-128, 127, size=17 * 13, dtype=np.int8)
        self.acmTableGainHbyS = np.random.randint(-128, 127, size=17 * 13, dtype=np.int8)
        self.acmTableGainSbyS = np.random.randint(-128, 127, size=17 * 13, dtype=np.int8)
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

    config = AcmConfig()
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

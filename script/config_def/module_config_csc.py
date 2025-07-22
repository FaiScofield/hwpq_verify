"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_csc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-16
Description :
LastEditTime: 2025-07-22
"""

import os
import sys
import json
import random
import argparse
import numpy as np

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *


class CscConfig(ModuleConfigCore):
    def __init__(self, name: str = "CSC", version: str = "unknown"):
        super().__init__(name, version)

        self.cscEnable = 1
        self.cscCctCtrlEn = 0
        self.cscBrightness = 256
        self.cscHue = 256
        self.cscContrast = 256
        self.cscSaturation = 256
        self.cscRGain = 256
        self.cscGGain = 256
        self.cscBGain = 256
        self.cscROffset = 256
        self.cscGOffset = 256
        self.cscBOffset = 256
        self.cscMatrix = np.identity(3, dtype=np.int16)
        self.cscVector = np.zeros(3, dtype=np.int32)
        self.cscPassthrough = 0  # use matrix & vector directly

    ## =============== overwrite methods  ===============
    def dump(self, filename=None) -> bool:
        data = {
            "version": self.version,
            "rand_seed": self.randSeed,
            "cscEnable": self.cscEnable,
            "cscCctCtrlEn": self.cscCctCtrlEn,
            "cscBrightness": self.cscBrightness,
            "cscHue": self.cscHue,
            "cscContrast": self.cscContrast,
            "cscSaturation": self.cscSaturation,
            "cscRGain": self.cscRGain,
            "cscGGain": self.cscGGain,
            "cscBGain": self.cscBGain,
            "cscROffset": self.cscROffset,
            "cscGOffset": self.cscGOffset,
            "cscBOffset": self.cscBOffset,
            "cscMatrix": self.cscMatrix.flatten().tolist(),
            "cscVector": self.cscVector.flatten().tolist(),
            "cscPassthrough": self.cscPassthrough,
        }
        if filename == None or filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.logger.info(f"  - {k}: {v}")
            return True

        with open(filename, "w") as f:
            nest_data = {"pq_tuning_param": {"csc": data}}
            json.dump(nest_data, f, indent=4, ensure_ascii=False)
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
                    self.logger.info(f"load config from pq_tuning_param.csc ...")
                    data = data["pq_tuning_param"]["csc"]
                self.cscEnable = data["cscEnable"]
                self.cscCctCtrlEn = data["cscCctCtrlEn"] if "cscCctCtrlEn" in data else 0
                self.cscBrightness = data["cscBrightness"]
                self.cscHue = data["cscHue"]
                self.cscContrast = data["cscContrast"]
                self.cscSaturation = data["cscSaturation"]
                self.cscRGain = data["cscRGain"]
                self.cscGGain = data["cscGGain"]
                self.cscBGain = data["cscBGain"]
                self.cscROffset = data["cscROffset"]
                self.cscGOffset = data["cscGOffset"]
                self.cscBOffset = data["cscBOffset"]
                self.cscMatrix = (
                    np.array(data["cscMatrix"], dtype=np.int16).reshape(3, 3)
                    if "cscMatrix" in data
                    else np.identity(3, dtype=np.int16)
                )
                self.cscVector = (
                    np.array(data["cscVector"], dtype=np.int32) if "cscVector" in data else np.zeros(3, dtype=np.int32)
                )
                self.cscPassthrough = data["cscPassthrough"] if "cscPassthrough" in data else 0
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

        self.randSeed = seed
        self.version = f"{self.name.lower()}_config_rk3572_random_seed_{seed}"

        self.cscEnable = int(random.randint(0, 9) > 0)  # %90 be ON
        self.cscCctCtrlEn = 0  # always 0 for now
        self.cscBrightness = random.randint(0, 511)
        self.cscHue = random.randint(0, 511)
        self.cscContrast = random.randint(0, 511)
        self.cscSaturation = random.randint(0, 511)
        self.cscRGain = random.randint(0, 511)
        self.cscGGain = random.randint(0, 511)
        self.cscBGain = random.randint(0, 511)
        self.cscROffset = random.randint(0, 511)
        self.cscGOffset = random.randint(0, 511)
        self.cscBOffset = random.randint(0, 511)
        self.cscMatrix = np.random.randint(-(2**12), 2**12 - 1, size=(3, 3), dtype=np.int16)  # s13 in s16
        self.cscVector = np.random.randint(-(2**10), 2**10 - 1, size=3, dtype=np.int32)  # s10
        self.cscVector = np.dot(self.cscMatrix, self.cscVector)  # s13*s11->s23 in s32
        self.cscPassthrough = 1  # 100% use matrix & vector directly for now!

        ## check if passthrough mode
        # passthrough = None
        # if "passthrough" in kwargs:
        #     passthrough = kwargs["passthrough"]
        #     self.cscPassthrough = passthrough

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

    config = CscConfig()
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

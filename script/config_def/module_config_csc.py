"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_csc.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-16
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
from enum import Enum

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *
from utils import NoIndent, CompactArrayEncoder


class CscColorSpace(Enum):
    """(enum_val, offset_r/y, offset_g/u, offset_b/v)"""

    RGBL = (0x00, 16, 16, 16)
    RGBF = (0x01, 0, 0, 0)
    YUV601L = (0x02, 16, 128, 128)
    YUV601F = (0x03, 0, 128, 128)
    YUV709L = (0x04, 16, 128, 128)
    YUV709F = (0x05, 0, 128, 128)
    YUV2020L = (0x08, 16, 128, 128)
    YUV2020F = (0x09, 0, 128, 128)


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
        self.cscMatrix = np.identity(3, dtype=np.int16) * 1024  # s13
        self.cscVector = np.zeros(3, dtype=np.int32)  # s23
        self.cscSrcOffset = np.zeros(3, dtype=np.int32)
        self.cscDstOffset = np.zeros(3, dtype=np.int32)
        self.cscPassthrough = 0  # use matrix & vector directly

    ## =============== overwrite methods  ===============
    def dump(self, filename: str = "", pretty_array_stdout: int = 32) -> bool:
        data = {
            "version": self.version,
            "randSeed": self.randSeed,
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
            "cscSrcOffset": self.cscSrcOffset.flatten().tolist(),
            "cscDstOffset": self.cscDstOffset.flatten().tolist(),
            "cscPassthrough": self.cscPassthrough,
        }
        if filename == "":
            self.logger.info(f"Config parameters shown below:")
            for k, v in data.items():
                self.pretty_print_dict(k, v, 2, pretty_array_stdout)
            return True

        with open(filename, "w") as f:
            ## keep list data in one line by using NoIndent & CompactArrayEncoder
            for k, v in data.items():
                if k in ["cscMatrix", "cscVector", "cscSrcOffset", "cscDstOffset"]:
                    data[k] = NoIndent(v)
            nest_data = {"pq_tuning_param": {"csc": data}}
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
                self.cscSrcOffset = (
                    np.array(data["cscSrcOffset"], dtype=np.int32)
                    if "cscSrcOffset" in data
                    else np.zeros(3, dtype=np.int32)
                )
                self.cscDstOffset = (
                    np.array(data["cscDstOffset"], dtype=np.int32)
                    if "cscDstOffset" in data
                    else np.zeros(3, dtype=np.int32)
                )
                self.cscPassthrough = data["cscPassthrough"] if "cscPassthrough" in data else 0
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

        ## parse other arguments
        precision = kwargs["precision"] if "precision" in kwargs else 10
        assert precision in [10, 13]

        self.randSeed = seed
        self.version = f"{self.name.lower()}_config_rk3572_random_seed_{seed}"

        self.cscEnable = 1  # int(random.randint(0, 99) > 95)  # 95% be ON
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

        ## check if passthrough mode.
        if False:  # "passthrough" in kwargs:
            self.cscPassthrough = int(kwargs["passthrough"])
        else:
            self.cscPassthrough = 1  # 100% use matrix & vector directly for now!

        if self.cscPassthrough:
            src_clr = random.choice(list(CscColorSpace))
            dst_clr = random.choice(list(CscColorSpace))
            self.cscSrcOffset = -np.array(src_clr.value[1:], dtype=np.int32) << (precision - 8)
            self.cscDstOffset = +np.array(dst_clr.value[1:], dtype=np.int32) << (precision - 8)
            if precision == 13:
                self.cscMatrix = np.random.randint(-(2**15), 2**15 - 1, size=(3, 3), dtype=np.int16)  # s16
                self.cscVector = (
                    np.identity(3, dtype=np.int32) << precision
                ) @ self.cscDstOffset + self.cscMatrix @ self.cscSrcOffset  # s16*s11->s26
                self.cscVector = np.clip(self.cscVector, -(2**25), 2**25 - 1 - 4096)  # -4096 for hw + offset
                # self.cscVector = np.clip(self.cscVector, -(2**25), 2**25 - 1 - 4096)
            else:  # precision == 10:
                self.cscMatrix = np.random.randint(-(2**12), 2**12 - 1, size=(3, 3), dtype=np.int16)  # s13
                self.cscVector = (
                    np.identity(3, dtype=np.int32) << precision
                ) @ self.cscDstOffset + self.cscMatrix @ self.cscSrcOffset  # s13*s11->s23
                # self.cscVector = np.clip(self.cscVector, -(2**22), 2**22 - 1 - 512)  # -512 for hw + offset
                self.cscVector = np.random.randint(-(2**22), 2**22 - 1 - 512, size=3, dtype=np.int32)
        else:
            self.gen_coef_from_param()

        self.logger.info(f"generated a random config with seed={seed}, passthrough={self.cscPassthrough}")
        return True

    def gen_coef_from_param(self):
        # TODO
        self.logger.error("TODO: 'gen_coef_from_param' not implemented yet!")
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.add_argument("-ps", "--passthrough", action="store_true", help="设置相关参数直通寄存器")
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

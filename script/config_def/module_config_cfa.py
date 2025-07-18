"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_cfa.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description :
LastEditTime: 2025-07-11
"""

import os
import sys
import json
import random
import argparse

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *


class CfaConfig(ModuleConfigCore):
    def __init__(self, name: str = "CFA", version: str = "unknown"):
        super().__init__(name, version)
        self.nCallCnt = 0
        self.nFrameIdx = 0
        self.nImgWid = 0
        self.nImgHgt = 0
        self.nSrcWidStride = 0
        self.nSrcHgtStride = 0
        self.nDstWidStride = 0
        self.nDstHgtStride = 0
        self.nCurrC2pWidStride = 0
        self.nCurrC2pHgtStride = 0
        self.ePlatform = 0
        self.eCfaPattern = 0
        self.eAlgoType = 0
        self.eImgFormat = 0
        self.eOutFormat = 0
        self.eDisplayMode = 0
        self.nColorDepth = 0
        self.nContrastGain = 0
        self.nSaturationGain = 0
        self.nLuminanceGain = 0
        self.nSharpenGain = 0
        self.nStretchBlack = 0
        self.nStretchWhite = 0
        self.bDither = 0
        self.bDeFalseColor4Gray = 0
        self.bContrastEqual = 0
        self.bForceRunWithCpu = 0
        self.nRegalType = 0
        self.nA2AlgoType = 0
        self.nA2CompLevel = 0
        self.bA2Modulate = 0
        self.bClearLow4bits = 0
        self.sRoiInfo = [0, 0, 0, 0, 0, 0]  # x6
        self.aReserved = [0, 0, 0, 0, 0, 0, 0, 0]  # x8

    ## =============== overwrite methods  ===============
    def dump(self, filename=None) -> bool:
        if filename == None or filename == "":
            print(f"[{self.name}] Config parameters shown below:")
            dumpdata = "".join([f"  - %s: %s\n" % item for item in self.__dict__.items()])
            print(dumpdata)
            return True

        with open(filename, "w") as f:
            data = {
                "Version": self.version,
                "nCallCnt": self.nCallCnt,
                "nFrameIdx": self.nFrameIdx,
                "nImgWid": self.nImgWid,
                "nImgHgt": self.nImgHgt,
                "nSrcWidStride": self.nSrcWidStride,
                "nSrcHgtStride": self.nSrcHgtStride,
                "nDstWidStride": self.nDstWidStride,
                "nDstHgtStride": self.nDstHgtStride,
                "nCurrC2pWidStride": self.nCurrC2pWidStride,
                "nCurrC2pHgtStride": self.nCurrC2pHgtStride,
                "ePlatform": self.ePlatform,
                "eCfaPattern": self.eCfaPattern,
                "eAlgoType": self.eAlgoType,
                "eImgFormat": self.eImgFormat,
                "eOutFormat": self.eOutFormat,
                "eDisplayMode": self.eDisplayMode,
                "nColorDepth": self.nColorDepth,
                "nContrastGain": self.nContrastGain,
                "nSaturationGain": self.nSaturationGain,
                "nLuminanceGain": self.nLuminanceGain,
                "nSharpenGain": self.nSharpenGain,
                "nStretchBlack": self.nStretchBlack,
                "nStretchWhite": self.nStretchWhite,
                "bDither": self.bDither,
                "bDeFalseColor4Gray": self.bDeFalseColor4Gray,
                "bContrastEqual": self.bContrastEqual,
                "bForceRunWithCpu": self.bForceRunWithCpu,
                "nRegalType": self.nRegalType,
                "nA2AlgoType": self.nA2AlgoType,
                "nA2CompLevel": self.nA2CompLevel,
                "bA2Modulate": self.bA2Modulate,
                "bClearLow4bits": self.bClearLow4bits,
                "randSeed": self.randSeed,
                "sRoiInfo": self.sRoiInfo,
                "aReserved": self.aReserved,
            }
            json.dump(data, f, indent=4, ensure_ascii=False)
            return True

        return False

    def load(self, filename) -> bool:
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

                self.version = data["Version"]
                self.nCallCnt = data["nCallCnt"]
                self.nFrameIdx = data["nFrameIdx"]
                self.nImgWid = data["nImgWid"]
                self.nImgHgt = data["nImgHgt"]
                self.nSrcWidStride = data["nSrcWidStride"]
                self.nSrcHgtStride = data["nSrcHgtStride"]
                self.nDstWidStride = data["nDstWidStride"]
                self.nDstHgtStride = data["nDstHgtStride"]
                self.nCurrC2pWidStride = data["nCurrC2pWidStride"]
                self.nCurrC2pHgtStride = data["nCurrC2pHgtStride"]
                self.ePlatform = data["ePlatform"]
                self.eCfaPattern = data["eCfaPattern"]
                self.eAlgoType = data["eAlgoType"]
                self.eImgFormat = data["eImgFormat"]
                self.eOutFormat = data["eOutFormat"]
                self.eDisplayMode = data["eDisplayMode"]
                self.nColorDepth = data["nColorDepth"]
                self.nContrastGain = data["nContrastGain"]
                self.nSaturationGain = data["nSaturationGain"]
                self.nLuminanceGain = data["nLuminanceGain"]
                self.nSharpenGain = data["nSharpenGain"]
                self.nStretchBlack = data["nStretchBlack"]
                self.nStretchWhite = data["nStretchWhite"]
                self.bDither = data["bDither"]
                self.bDeFalseColor4Gray = data["bDeFalseColor4Gray"]
                self.bContrastEqual = data["bContrastEqual"]
                self.bForceRunWithCpu = data["bForceRunWithCpu"]
                self.nRegalType = data["nRegalType"]
                self.nA2AlgoType = data["nA2AlgoType"]
                self.nA2CompLevel = data["nA2CompLevel"]
                self.bA2Modulate = data["bA2Modulate"]
                self.bClearLow4bits = data["bClearLow4bits"]
                self.sRoiInfo = data["sRoiInfo"]
                self.aReserved = data["aReserved"]
                self.randSeed = data["randSeed"]
                return True
        except Exception as e:
            print(f"[{self.name}] load config file '{filename}' failed: {e}")
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

        self.version = f"{self.name.lower()}_config_rk3572_random_seed_{seed}"
        self.nCallCnt = 0
        self.nFrameIdx = 0
        self.nImgWid = random.randint(4, 4000) // 4 * 4  # align to 4
        self.nImgHgt = random.randint(2, 4000)  # no align
        self.nSrcWidStride = self.nImgWid * 4  # x4 for RGBA format
        self.nSrcHgtStride = self.nImgHgt
        self.nDstWidStride = self.nImgWid
        self.nDstHgtStride = self.nImgHgt
        self.nCurrC2pWidStride = self.nImgWid
        self.nCurrC2pHgtStride = self.nImgHgt
        self.ePlatform = random.randint(0, 10)  # but not 8
        self.ePlatform = 7 if self.ePlatform == 8 else self.ePlatform  # 8 is not supported
        self.eCfaPattern = 0
        self.eAlgoType = random.randint(0, 2)
        self.eImgFormat = 0
        self.eOutFormat = 11  # random.randint(11, 13)
        self.eDisplayMode = 0
        self.nColorDepth = 64
        self.nContrastGain = random.randint(0, 200)  # [0, 128]
        self.nSaturationGain = random.randint(0, 200)  # [0, 128]
        self.nLuminanceGain = random.randint(0, 200)  # [0, 128]s
        self.nSharpenGain = random.randint(0, 200)  # [0, 128]
        self.nStretchBlack = random.randint(0, 120)  # [0, 96]
        self.nStretchWhite = random.randint(120, 300)  # [160, 255]
        self.bDither = (random.randint(0, 3) > 0) * 2  # 0 or 2, 75% ON
        self.bDeFalseColor4Gray = int(random.randint(0, 3) > 0)  # 75% ON
        self.bContrastEqual = 0
        self.bForceRunWithCpu = random.randint(0, 1)
        self.nRegalType = 0
        self.nA2AlgoType = 0  # always 0 for hardware mode
        self.nA2CompLevel = random.randint(0, 80)  # [0, 64]
        self.bA2Modulate = random.randint(0, 10)  # [0, 7]
        self.bClearLow4bits = 1  # random.randint(0, 1)  # [0, 1]
        self.sRoiInfo = [0, 0, 0, 0, 0, 0]  # x6
        self.aReserved = [0, 0, 0, 0, 0, 0, 0, 0]  # x8

        self.randSeed = seed
        return seed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    config = CfaConfig()
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
        print(f"unknown interface '{args.interface}'!")
        load_ok = False

    check_ok = config.check()
    print("load_ok: %s, check_ok: %s" % (load_ok, check_ok))

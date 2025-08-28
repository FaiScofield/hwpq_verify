"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_cfa.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description :
LastEditTime: 2025-08-14
"""

import os
import sys
import json
import random
import argparse
import traceback

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *
from utils import NoIndent, CompactArrayEncoder


class CfaConfig(ModuleConfigCore):
    def __init__(self, name: str = "CFA", platform: str = "RK3572"):
        super().__init__(name, platform)

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
    def dump(self, filename: str = "", pretty_array_stdout: int = 32) -> bool:
        data = {
            "version": self.version,
            "randSeed": self.randSeed,
            "nCallCnt": self.nCallCnt,
            "ePlatform": self.ePlatform,
            "eCfaPattern": self.eCfaPattern,
            "eDisplayMode": self.eDisplayMode,
            "bClearLow4bits": self.bClearLow4bits,
            "sFrameInfo": {
                "nFrameIdx": self.nFrameIdx,
                "nImgWid": self.nImgWid,
                "nImgHgt": self.nImgHgt,
                "nSrcWidStride": self.nSrcWidStride,
                "nSrcHgtStride": self.nSrcHgtStride,
                "nDstWidStride": self.nDstWidStride,
                "nDstHgtStride": self.nDstHgtStride,
                "nCurrC2pWidStride": self.nCurrC2pWidStride,
                "nCurrC2pHgtStride": self.nCurrC2pHgtStride,
                "eImgFormat": self.eImgFormat,
                "eOutFormat": self.eOutFormat,
            },
            "sProcParam": {
                "nColorDepth": self.nColorDepth,
                "nContrastGain": self.nContrastGain,
                "nSaturationGain": self.nSaturationGain,
                "nLuminanceGain": self.nLuminanceGain,
                "nSharpenGain": self.nSharpenGain,
                "nStretchBlack": self.nStretchBlack,
                "nStretchWhite": self.nStretchWhite,
                "bDeFalseColor4Gray": self.bDeFalseColor4Gray,
                "bContrastEqual": self.bContrastEqual,
                "bDither": self.bDither,
                "eAlgoType": self.eAlgoType,
                "nRegalType": self.nRegalType,
                "nA2AlgoType": self.nA2AlgoType,
                "nA2CompLevel": self.nA2CompLevel,
                "bA2Modulate": self.bA2Modulate,
                "bForceRunWithCpu": self.bForceRunWithCpu,
                ## keep list data in one line by using NoIndent & CompactArrayEncoder
                "sRoiInfo": NoIndent(self.sRoiInfo),
                "aReserved": NoIndent(self.aReserved),
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
                dataRoot = json.load(f)
                data = dataRoot

                self.version = data["version"]
                self.randSeed = data["randSeed"] if "randSeed" in data else -1
                self.nCallCnt = data["nCallCnt"]
                self.ePlatform = data["ePlatform"]
                self.eCfaPattern = data["eCfaPattern"]
                self.eDisplayMode = data["eDisplayMode"]
                self.bClearLow4bits = data["bClearLow4bits"] if "bClearLow4bits" in data else -1
                if "sFrameInfo" in dataRoot:
                    data = dataRoot["sFrameInfo"]
                self.nFrameIdx = data["nFrameIdx"]
                self.nImgWid = data["nImgWid"]
                self.nImgHgt = data["nImgHgt"]
                self.nSrcWidStride = data["nSrcWidStride"]
                self.nSrcHgtStride = data["nSrcHgtStride"]
                self.nDstWidStride = data["nDstWidStride"]
                self.nDstHgtStride = data["nDstHgtStride"]
                self.nCurrC2pWidStride = data["nCurrC2pWidStride"]
                self.nCurrC2pHgtStride = data["nCurrC2pHgtStride"]
                self.eImgFormat = data["eImgFormat"]
                self.eOutFormat = data["eOutFormat"]
                if "sProcParam" in dataRoot:
                    data = dataRoot["sProcParam"]
                self.eAlgoType = data["eAlgoType"]
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
                self.sRoiInfo = data["sRoiInfo"]
                self.aReserved = data["aReserved"]
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

        support_pattern_values = [0x0, 0x1000, 0x1001, 0x1002, 0x2000, 0x2001]

        self.version = f"{self.name.lower()}_config_{self.platform.lower()}_random_seed_{seed}"
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
        # self.ePlatform = random.randint(0, 10)  # but not 8
        # self.ePlatform = 7 if self.ePlatform == 8 else self.ePlatform  # 8 is not supported
        self.ePlatform = 0
        self.eCfaPattern = support_pattern_values[random.randint(0, len(support_pattern_values) - 1)]
        self.eAlgoType = random.randint(0, 2)
        self.eImgFormat = 0
        self.eOutFormat = 11  # random.randint(11, 13)
        self.eDisplayMode = 4
        self.nColorDepth = 64
        self.nContrastGain = random.randint(0, 128)  # [0, 128]
        self.nSaturationGain = random.randint(0, 128)  # [0, 128]
        self.nLuminanceGain = random.randint(0, 128)  # [0, 128]
        self.nSharpenGain = random.randint(0, 128)  # [0, 128]
        self.nStretchBlack = random.randint(0, 96)  # [0, 96]
        self.nStretchWhite = random.randint(160, 255)  # [160, 255]
        self.bDither = int(random.randint(0, 99) < 75) * 2  # 0 or 2, 75% ON
        self.bDeFalseColor4Gray = int(random.randint(0, 99) < 75)  # 75% ON
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
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3538...")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    config = CfaConfig(platform=args.platform)
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

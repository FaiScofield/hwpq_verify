"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_cfa.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description : 
LastEditTime: 2025-07-08
"""

import os
import sys
import json
import random

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import *

class CfaConfig(ModuleConfigCore):
    def __init__(self, name: str, version: str = "unknown"):
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

    def dump(self, filename=None):
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

    def load(self, filename):
        # check config file validity
        if not os.path.exists(filename):
            print(f"[{self.name}] config file '%s' doesn't exist!" % filename)
            return False
        if not filename.endswith(".json"):
            print(f"[{self.name}] config file '%s' is not a json file!" % filename)
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
            print(f"[{self.name}] load config file '%s' failed: %s" % (filename, e))
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

        self.version = f"RKCFA_0.13.0.4721.random_seed_{seed}"
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
        self.ePlatform = random.randint(0, 10)
        self.eCfaPattern = 0
        self.eAlgoType = random.randint(0, 2)
        self.eImgFormat = 0
        self.eOutFormat = random.randint(11, 13)
        self.eDisplayMode = 0
        self.nColorDepth = 64
        self.nContrastGain = random.randint(0, 200)  # [0, 128]
        self.nSaturationGain = random.randint(0, 200)  # [0, 128]
        self.nLuminanceGain = random.randint(0, 200)  # [0, 128]
        self.nSharpenGain = random.randint(0, 200)  # [0, 128]
        self.nStretchBlack = random.randint(0, 120)  # [0, 96]
        self.nStretchWhite = random.randint(120, 300)  # [160, 255]
        self.bDither = random.randint(0, 1) * 2 # 0 or 2
        self.bDeFalseColor4Gray = random.randint(0, 1)
        self.bContrastEqual = 0
        self.bForceRunWithCpu = random.randint(0, 1)
        self.nRegalType = 0
        self.nA2AlgoType = 2
        self.nA2CompLevel = random.randint(0, 80)  # [0, 64]
        self.bA2Modulate = random.randint(0, 8)  # [0, 7]
        self.bClearLow4bits = 1 #random.randint(0, 1)  # [0, 1]
        self.sRoiInfo = [0, 0, 0, 0, 0, 0]  # x6
        self.aReserved = [0, 0, 0, 0, 0, 0, 0, 0]  # x8

        self.randSeed = seed
        return seed


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: %s load <config_json_file>" % sys.argv[0])
        print("Usage: %s gen <rand_seed>" % sys.argv[0])
        exit(-1)

    config = CfaConfig()
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

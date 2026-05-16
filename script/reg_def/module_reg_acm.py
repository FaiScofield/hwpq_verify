"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_acm.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-08-06
"""

import os
import sys
import argparse

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def import *
from config_def import *


class AcmRegister(ModuleRegisterCore):
    def __init__(self, name: str = "ACM", platform: str = 'RK3572'):
        super().__init__(name, platform)

        self.config = AcmConfig(self.name)
        self.base_addr = 0x0
        self.update(platform=platform)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if "platform" in kwargs:
            self.platform = kwargs["platform"].upper()
        if self.platform.lower() == "rk3572":
            self.base_addr = 0xF9000000
            # self.nb_regs = 441 # 1764 bytes, nb_regs=2+153+221+65=441
            self.nb_regs = 503 # 2012 bytes, nb_regs=12+16+36+153+221+65=503
            self.regs = [
                Reg(0x00006400, 0x0, "ACM_CTRL"),
                Reg(0x00006404, 0x0, "DELTA_RANGE"),
                Reg(0x00006408, 0x0, "FETCH_START"),
                Reg(0x0000640C, 0x0, "DEMO_CTRL"), # after RK3572
                Reg(0x00006410, 0x0, "DEBUG_POINT0_CFG"),
                Reg(0x00006414, 0x0, "DEBUG_POINT1_CFG"),
                Reg(0x00006418, 0x0, "DEBUG_POINT2_CFG"),
                Reg(0x0000641C, 0x0, "DEBUG_POINT3_CFG"),
                Reg(0x00006420, 0x0, "FETCH_DONE"),
                Reg(0x00006424, 0x0, "ReservedA0"),
                Reg(0x00006428, 0x0, "ReservedA1"),
                Reg(0x0000642C, 0x0, "ReservedA2"),
            ]
            self.regs += [Reg(0x00006430 + idx * 4, 0x0, f"DEBUG{idx//4}_POINT{idx%4}") for idx in range(16)] # 6430~646C, 16 regs
            self.regs += [Reg(0x00006470 + idx * 4, 0x0, f"ReservedB{idx}") for idx in range(36)] # 6470~64FC, 36 regs
            self.regs += [Reg(0x00006500 + idx * 4, 0x0, f"YHS_GAIN_BY_Y_SEG{idx}") for idx in range(153)]  # 6500~6760 17*9=153 regs
            self.regs += [Reg(0x00006764 + idx * 4, 0x0, f"YHS_GAIN_BY_S_SEG{idx}") for idx in range(221)]  # 6764~6AD4 17*13=221 regs
            self.regs += [Reg(0x00006AD8 + idx * 4, 0x0, f"YHS_DEL_BY_H_SEG{idx}") for idx in range(65)] # 6AD8~6BD8 65*1=65 regs
            return self.check_regs()
        else:
            self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def config2regs(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False
        cfg = self.config
        self.set(name="ACM_CTRL", value=(cfg.acmEnable & 0x1))
        self.set(
            name="DELTA_RANGE",
            value=(cfg.lumGain & 0x3FF) | ((cfg.hueGain & 0x3FF) << 10) | ((cfg.satGain & 0x3FF) << 20),
        )
        tabY = cfg.acmTableGainYbyY.astype(np.int32)
        tabH = cfg.acmTableGainHbyY.astype(np.int32)
        tabS = cfg.acmTableGainSbyY.astype(np.int32)
        for i in range(153):
            self.set(
                name=f"YHS_GAIN_BY_Y_SEG{i}",
                value=((tabY[i] & 0xFF) << 0) | ((tabH[i] & 0xFF) << 8) | ((tabS[i] & 0xFF) << 16),
            )
        tabY = cfg.acmTableGainYbyS.astype(np.int32)
        tabH = cfg.acmTableGainHbyS.astype(np.int32)
        tabS = cfg.acmTableGainSbyS.astype(np.int32)
        for i in range(221):
            self.set(
                name=f"YHS_GAIN_BY_S_SEG{i}",
                value=((tabY[i] & 0xFF) << 0) | ((tabH[i] & 0xFF) << 8) | ((tabS[i] & 0xFF) << 16),
            )
        tabY = cfg.acmTableDeltaYbyH.astype(np.int32)
        tabH = cfg.acmTableDeltaHbyH.astype(np.int32)
        tabS = cfg.acmTableDeltaSbyH.astype(np.int32)
        for i in range(65):
            self.set(
                name=f"YHS_DEL_BY_H_SEG{i}",
                value=((tabY[i] & 0x3FF) << 0) | ((tabH[i] & 0xFF) << 12) | ((tabS[i] & 0x3FF) << 20),
            )
        return True

    def regs2config(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False

        self.config.acmEnable = self.regs[0].value & 0x1
        self.config.lumGain = (self.regs[1].value >> 0) & 0x3FF
        self.config.hueGain = (self.regs[1].value >> 10) & 0x3FF
        self.config.satGain = (self.regs[1].value >> 20) & 0x3FF
        for i in range(153):
            reg = self.regs[2 + i]
            self.config.acmTableGainYbyY[i] = (reg.value.astype(np.int32) >> 0) & 0xFF
            self.config.acmTableGainHbyY[i] = (reg.value.astype(np.int32) >> 8) & 0xFF
            self.config.acmTableGainSbyY[i] = (reg.value.astype(np.int32) >> 16) & 0xFF
        for i in range(221):
            reg = self.regs[2 + 153 + i]
            self.config.acmTableGainYbyS[i] = (reg.value.astype(np.int32) >> 0) & 0xFF
            self.config.acmTableGainHbyS[i] = (reg.value.astype(np.int32) >> 8) & 0xFF
            self.config.acmTableGainSbyS[i] = (reg.value.astype(np.int32) >> 16) & 0xFF
        for i in range(65):
            reg = self.regs[2 + 153 + 221 + i]
            self.config.acmTableDeltaYbyH[i] = (reg.value.astype(np.int32) >> 0) & 0x3FF
            self.config.acmTableDeltaHbyH[i] = (reg.value.astype(np.int32) >> 12) & 0xFF
            self.config.acmTableDeltaSbyH[i] = (reg.value.astype(np.int32) >> 20) & 0x3FF
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3538...")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    register = AcmRegister(platform=args.platform)

    if args.interface == "load":
        register.load(args.file)
    elif args.interface == "dump":
        register.dump(args.file)
    elif args.interface == "gen":
        if register.gen(args.seed):
            register.dump(args.file)
    elif args.interface in ["c2r", "config2regs"]:
        register.config.gen(args.seed)
        register.config.dump()
        if register.config2regs():
            register.dump()
    elif args.interface in ["r2c", "regs2config"]:
        register.gen(args.seed)
        register.dump()
        if register.regs2config():
            register.config.dump()
    else:
        print(f"interface {args.interface} is not supported!")
        parser.print_help()

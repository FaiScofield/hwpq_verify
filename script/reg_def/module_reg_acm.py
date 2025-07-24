"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_acm.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-07-24
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
        if self.platform.lower() == "rk3572":
            self.base_addr = 0xF9000000
            self.nb_regs = 441
            self.regs = [
                Reg(0x00006400, 0x0, "ACM_CTRL"),
                Reg(0x00006404, 0x0, "DELTA_RANGE"),
                # Reg(0x00006408, 0x0, "FETCH_START"),
                # Reg(0x00006420, 0x0, "FETCH_DONE"),
            ]
            self.regs += [Reg(0x00006500 + idx * 4, 0x0, f"YHS_GAIN_BY_Y_SEG{idx}") for idx in range(153)]
            self.regs += [Reg(0x00006764 + idx * 4, 0x0, f"YHS_GAIN_BY_S_SEG{idx}") for idx in range(221)]
            self.regs += [Reg(0x00006AD8 + idx * 4, 0x0, f"YHS_DEL_BY_H_SEG{idx}") for idx in range(65)]
            assert len(self.regs) == self.nb_regs
            return True
        else:
            self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def config2regs(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False
        cfg = self.config
        self.logger.error("TODO: config2regs() is not implement yet!")
        # self.set(name="ENABLE_CTRL", value=(cfg.acm_en & 0x1) | ((cfg.shoot_ctrl_en & 0x1) << 1))
        # self.set(name="USM_CTRL", value=(cfg.sharp_usm_gain & 0x3FF) | ((cfg.usm_coring_thr & 0x7F) << 16))
        # self.set(
        #     name="USM_COEF",
        #     value=(cfg.sharp_core_A & 0xFF) | ((cfg.sharp_core_B & 0xFF) << 8) | ((cfg.sharp_core_C & 0xFF) << 16),
        # )
        # self.set(name="SHOOT_CTRL_REG0", value=(cfg.shoot_ctrl_delta_offset & 0xFF))
        # self.set(

        #     name="SHOOT_CTRL_REG1", value=(cfg.shoot_ctrl_pos & 0x7F) | ((cfg.shoot_ctrl_pos_unlimit & 0x7F) << 16)
        # )
        # self.set(
        #     name="SHOOT_CTRL_REG2", value=(cfg.shoot_ctrl_neg & 0x7F) | ((cfg.shoot_ctrl_neg_unlimit & 0x7F) << 16)
        # )
        # self.set(
        #     name="ROI_CTRL0",
        #     value=(cfg.sharp_roi_xstart & 0xFFF)
        #     | ((cfg.sharp_roi_ystart & 0xFFF) << 16)
        #     | ((cfg.sharp_roi_enable & 0x1) << 31),
        # )
        # self.set(name="ROI_CTRL1", value=(cfg.sharp_roi_xend & 0xFFF) | ((cfg.sharp_roi_yend & 0xFFF) << 16))
        return False

    def regs2config(self) -> bool:
        self.logger.error("TODO: regs2config() is not implement yet!")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    register = AcmRegister()
    register.set(name="ENABLE_CTRL", value=0x1)
    register.set(name="USM_CTRL", value=0x300)
    register.set(name="USM_COEF", value=0x10 | (0x20 << 8) | (0x30 << 16))

    if args.interface == "load":
        register.load(args.file)
    elif args.interface == "dump":
        register.dump(args.file)
    elif args.interface == "gen":
        if register.gen(args.seed):
            register.dump(args.file)
    elif args.interface in ["c2r", "config2regs"]:
        if register.config2regs():
            register.dump()
    elif args.interface in ["r2c", "regs2config"]:
        if register.regs2config():
            register.config.dump()
    else:
        print(f"interface {args.interface} is not supported!")
        parser.print_help()

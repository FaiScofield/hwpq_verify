"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_sharp_lite.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-27
"""

import os
import sys
import argparse
import numpy as np

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def.module_reg_core import ModuleRegisterCore, Reg
from config_def.module_config_sharp_lite import SharpLiteConfig


class SharpLiteRegister(ModuleRegisterCore):
    def __init__(self, name: str = "SHARP", platform: str = 'RK3572'):
        super().__init__(name, platform)

        self.config = SharpLiteConfig(self.name)
        self.base_addr = 0x0
        self.update(platform=platform)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if self.platform.lower() == "rk3572":
            self.base_addr = 0xF9000000
            self.nb_regs = 14
            self.regs = [
                Reg(0x00006C00, 0x0, "ENABLE_CTRL"),
                Reg(0x00006C04, 0x0, "GATING_CTRL"),
                Reg(0x00006C08, 0x0, "RESERVED_08"),
                Reg(0x00006C0C, 0x0, "RESERVED_0C"),
                Reg(0x00006C10, 0x0, "USM_CTRL"),
                Reg(0x00006C14, 0x0, "USM_COEF"),
                Reg(0x00006C18, 0x0, "RESERVED_18"),
                Reg(0x00006C1C, 0x0, "RESERVED_1C"),
                Reg(0x00006C20, 0x0, "SHOOT_CTRL_REG0"),
                Reg(0x00006C24, 0x0, "SHOOT_CTRL_REG1"),
                Reg(0x00006C28, 0x0, "SHOOT_CTRL_REG2"),
                Reg(0x00006C2C, 0x0, "ROI_CTRL0"),
                Reg(0x00006C30, 0x0, "ROI_CTRL1"),
                Reg(0x00006C34, 0x0, "INK_CTRL"),
            ]
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
        self.set(name="ENABLE_CTRL", value=(cfg.i_sharp_lite_en & 0x1) | ((cfg.i_shoot_ctrl_en & 0x1) << 1))
        self.set(name="GATING_CTRL", value=0x0)
        self.set(name="RESERVED_08", value=0x0)
        self.set(name="RESERVED_0C", value=0x0)
        self.set(name="USM_CTRL", value=(cfg.i_sharp_usm_gain & 0x3FF) | ((cfg.f_usm_coring_thr & 0x7F) << 16))
        self.set(
            name="USM_COEF",
            value=(cfg.i_sharp_core_A & 0xFF)
            | ((cfg.i_sharp_core_B & 0xFF) << 8)
            | ((cfg.i_sharp_core_C & 0xFF) << 16),
        )
        self.set(name="RESERVED_18", value=0x0)
        self.set(name="RESERVED_1C", value=0x0)
        self.set(name="SHOOT_CTRL_REG0", value=(cfg.i_shoot_ctrl_delta_offset & 0xFF))
        self.set(
            name="SHOOT_CTRL_REG1", value=(cfg.i_shoot_ctrl_pos & 0x7F) | ((cfg.i_shoot_ctrl_pos_unlimit & 0x7F) << 16)
        )
        self.set(
            name="SHOOT_CTRL_REG2", value=(cfg.i_shoot_ctrl_neg & 0x7F) | ((cfg.i_shoot_ctrl_neg_unlimit & 0x7F) << 16)
        )
        self.set(
            name="ROI_CTRL0",
            value=(cfg.i_sharp_roi_xstart & 0xFFF)
            | ((cfg.i_sharp_roi_ystart & 0xFFF) << 16)
            | ((cfg.i_sharp_roi_enable & 0x1) << 31),
        )
        self.set(name="ROI_CTRL1", value=(cfg.i_sharp_roi_xend & 0xFFF) | ((cfg.i_sharp_roi_yend & 0xFFF) << 16))
        return True

    def regs2config(self) -> bool:
        val = self.get(name="ENABLE_CTRL")
        self.config.i_sharp_lite_en = (val >> 0) & 0x1
        self.config.i_shoot_ctrl_en = (val >> 1) & 0x1
        val = self.get(name="USM_CTRL")
        self.config.i_sharp_usm_gain = (val >> 0) & 0x3FF
        self.config.f_usm_coring_thr = (val >> 16) & 0x7F
        val = self.get(name="USM_COEF")
        self.config.i_sharp_core_A = int(val >> 0) & 0xFF
        self.config.i_sharp_core_B = int(val >> 8) & 0xFF
        self.config.i_sharp_core_C = int(val >> 16) & 0xFF
        val = self.get(name="SHOOT_CTRL_REG0")
        self.config.i_shoot_ctrl_delta_offset = val & 0x7F
        val = self.get(name="SHOOT_CTRL_REG1")
        self.config.i_shoot_ctrl_pos = (val >> 0) & 0x7F
        self.config.i_shoot_ctrl_pos_unlimit = (val >> 16) & 0x7F
        val = self.get(name="SHOOT_CTRL_REG2")
        self.config.i_shoot_ctrl_neg = (val >> 0) & 0x7F
        self.config.i_shoot_ctrl_neg_unlimit = (val >> 16) & 0x7F
        val = self.get(name="ROI_CTRL0")
        self.config.i_sharp_roi_xstart = (val >> 0) & 0xFFF
        self.config.i_sharp_roi_xend = (val >> 16) & 0xFFF
        self.config.i_sharp_roi_enable = (val >> 31) & 0x1
        val = self.get(name="ROI_CTRL1")
        self.config.i_sharp_roi_xend = (val >> 0) & 0xFFF
        self.config.i_sharp_roi_yend = (val >> 16) & 0xFFF
        # TODO: parse INK_CTRL register
        # val = self.get(name="INK_CTRL")
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    register = SharpLiteRegister()
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
        print(f"interface '{args.interface}' is not supported!")
        parser.print_help()

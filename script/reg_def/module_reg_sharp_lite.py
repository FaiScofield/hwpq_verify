"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_sharp_lite.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-11
"""
import os
import sys
import argparse

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
    '''
    def load(self, filename, **kwargs) -> bool:
        try:
            if filename.endswith(".bin"):
                data = np.fromfile(filename, dtype=np.uint32)
                if len(data) < len(self.regs):
                    self.logger.error(
                        f"not enough register data in {filename}! require {len(self.regs)} registers, but only get {len(data)}!"
                    )
                    return False
                for i in range(len(self.regs)):
                    self.regs[i].value = data[i]
                return self.dump()
            elif filename.endswith(".txt") or filename.endswith(".dat"):
                valid_regs_val_pairs = []  # [offset, value]
                with open(filename, "rt") as f:
                    for _, line in enumerate(f):
                        pair = self.parse_str_regs_array(line)
                        if pair is not None:
                            valid_regs_val_pairs.append(pair)
                        else:
                            continue
                for pos, val in valid_regs_val_pairs:
                    pos_ok = False
                    for i in range(len(self.regs)):
                        if pos == self.regs[i].offset or pos == self.regs[i].offset + self.base_addr:
                            self.regs[i].value = val
                            pos_ok = True
                            break
                    if not pos_ok:
                        self.logger.warning(f"offset={pos} is not a valid register!")
                return self.dump()
            elif filename.endswith(".json") and self.config is not None:
                ok = self.config.load(filename)
                ok |= self.config2regs()
                ok |= self.dump()
                return ok
            else:
                self.logger.errorint(f"{filename} is not supported!")
        except Exception as e:
            self.logger.error(f"failed to load {filename}! {str(e)}")
        return False
    '''

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
        self.set(name="ENABLE_CTRL", value=(cfg.sharp_lite_en & 0x1) | ((cfg.shoot_ctrl_en & 0x1) << 1))
        self.set(name="USM_CTRL", value=(cfg.sharp_usm_gain & 0x3FF) | ((cfg.usm_coring_thr & 0x7F) << 16))
        self.set(
            name="USM_COEF",
            value=(cfg.sharp_core_A & 0xFF) | ((cfg.sharp_core_B & 0xFF) << 8) | ((cfg.sharp_core_C & 0xFF) << 16),
        )
        self.set(name="SHOOT_CTRL_REG0", value=(cfg.shoot_ctrl_delta_offset & 0xFF))
        self.set(

            name="SHOOT_CTRL_REG1", value=(cfg.shoot_ctrl_pos & 0x7F) | ((cfg.shoot_ctrl_pos_unlimit & 0x7F) << 16)
        )
        self.set(
            name="SHOOT_CTRL_REG2", value=(cfg.shoot_ctrl_neg & 0x7F) | ((cfg.shoot_ctrl_neg_unlimit & 0x7F) << 16)
        )
        self.set(
            name="ROI_CTRL0",
            value=(cfg.sharp_roi_xstart & 0xFFF)
            | ((cfg.sharp_roi_ystart & 0xFFF) << 16)
            | ((cfg.sharp_roi_enable & 0x1) << 31),
        )
        self.set(name="ROI_CTRL1", value=(cfg.sharp_roi_xend & 0xFFF) | ((cfg.sharp_roi_yend & 0xFFF) << 16))
        return True

    def regs2config(self) -> bool:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/config2regs/regs2config")
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
        register.gen(args.seed)
        register.dump(args.file)
    else:
        print(f"interface {args.interface} is not supported!")
        args.print_help()

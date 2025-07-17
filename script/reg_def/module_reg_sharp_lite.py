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
from ctypes import *
from typing import TypeVar, Type

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def.module_reg_core import ModuleRegisterCore


class RK3572_SharpLiteReg_0x00(Structure):
    _fields_ = [
        ("sharp_en", c_uint32, 1),  # bit 0
        ("shoot_ctrl_en", c_uint32, 1),  # bits 1
        ("reserved2", c_uint32, 30),  # bits 2-31
    ]
    _pack_ = 1


class RK3572_SharpLiteReg_0x04(Structure):
    _fields_ = [
        ("shoot_ctrl_gating_en", c_uint32, 1),  # bit 0
        ("reserved1", c_uint32, 31),  # bits 1-31
    ]
    _pack_ = 1


class RK3572_SharpLiteReg_0x10(Structure):
    _fields_ = [
        ("peaking_gain", c_uint32, 10),  # bit 0-9
        ("reserved10", c_uint32, 6),  # bits 10-15
        ("coring_thr", c_uint32, 7),  # bits 16-22
        ("reserved23", c_uint32, 15),  # bits 23-31
    ]
    _pack_ = 1


class RK3572_SharpLiteReg_0x14(Structure):
    _fields_ = [
        ("coef_A", c_uint32, 8),
        ("coef_B", c_uint32, 8),
        ("coef_C", c_uint32, 8),
        ("reserved24", c_uint32, 8),
    ]
    _pack_ = 1


class RK3572_SharpLiteReg_0x20(Structure):
    _fields_ = [
        ("delta_offset", c_uint32, 8),
        ("reserved8", c_uint32, 24),
    ]
    _pack_ = 1


class RK3572_SharpLiteReg_0x24(Structure):
    _fields_ = [
        ("alpha_pos", c_uint32, 7),
        ("reserved7", c_uint32, 9),
        ("alpha_pos_unlimit", c_uint32, 7),
        ("reserved23", c_uint32, 9),
    ]
    _pack_ = 1


class RK3572_SharpLiteReg_0x28(Structure):
    _fields_ = [
        ("alpha_neg", c_uint32, 7),
        ("reserved7", c_uint32, 9),
        ("alpha_neg_unlimit", c_uint32, 7),
        ("reserved23", c_uint32, 9),
    ]
    _pack_ = 1


class RK3572_SharpLiteReg_0x2c(Structure):
    _fields_ = [
        ("sw_roi_xstart", c_uint32, 12),
        ("reserved12", c_uint32, 4),
        ("sw_roi_ystart", c_uint32, 12),
        ("reserved28", c_uint32, 3),
        ("sw_roi_en", c_uint32, 1),
    ]
    _pack_ = 1


class RK3572_SharpLiteReg_0x30(Structure):
    _fields_ = [
        ("sw_roi_xend", c_uint32, 12),
        ("reserved12", c_uint32, 4),
        ("sw_roi_yend", c_uint32, 12),
        ("reserved28", c_uint32, 4),
    ]
    _pack_ = 1

class RK3572_SharpLiteReg_0x34(Structure):
    _fields_ = [
        ("sw_ink_mode", c_uint32, 2),
        ("reserved3", c_uint32, 29),
        ("sw_ink_en", c_uint32, 1),
    ]
    _pack_ = 1


class SharpLiteRegisters_RK3572(ModuleRegisterCore):
    def __init__(self, name: str = "SHARP", platform: str = 'RK3572'):
        super().__init__(name, platform)

        self.ENABLE_CTRL = RK3572_SharpLiteReg_0x00()  # Address Offset: 0x0000
        self.GATING_CTRL = RK3572_SharpLiteReg_0x04()  # Address Offset: 0x0004
        self.RESERVED0008 = [c_uint32(0), c_uint32(0)]  # Address Offset: 0x0008
        self.USM_CTRL = RK3572_SharpLiteReg_0x10()  # Address Offset: 0x0010
        self.USM_COEF = RK3572_SharpLiteReg_0x14()  # Address Offset: 0x0014
        self.RESERVED0018 = [c_uint32(0), c_uint32(0)]  # Address Offset: 0x0018
        self.SHOOT_CTRL_REG0 = RK3572_SharpLiteReg_0x20()  # Address Offset: 0x0020
        self.SHOOT_CTRL_REG1 = RK3572_SharpLiteReg_0x24()  # Address Offset: 0x0024
        self.SHOOT_CTRL_REG2 = RK3572_SharpLiteReg_0x28()  # Address Offset: 0x0028
        self.ROI_CTRL0 = RK3572_SharpLiteReg_0x2c()  # Address Offset: 0x002C
        self.ROI_CTRL1 = RK3572_SharpLiteReg_0x30()  # Address Offset: 0x0030
        self.INK_CTRL = RK3572_SharpLiteReg_0x34()  # Address Offset: 0x0034

        self.sharp_en = 0  # 1bit unsigned
        self.sharp_usm_coef_A = 0  # s8bit Fix
        self.sharp_usm_coef_B = 0  # s8bit Fix
        self.sharp_usm_coef_C = 0  # s8bit Fix
        self.sharp_usm_coring_thr = 0  # No Fix, 7bit unsigned
        self.sharp_usm_gain = 0  # 10bit Fix
        self.sharp_shoot_ctrl_en = 0  # 1bit unsigned
        self.sharp_shoot_ctrl_delta_offset = 0  # 8bit unsigned
        self.sharp_shoot_ctrl_alpha_pos = 0  # 7bit unsigned
        self.sharp_shoot_ctrl_alpha_pos_unlimit = 0  # 7bit unsigned
        self.sharp_shoot_ctrl_alpha_neg = 0  # 7bit unsigned
        self.sharp_shoot_ctrl_alpha_neg_unlimit = 0  # 7bit unsigned
        self.sharp_roi_en = 0  # 1bit unsigned
        self.sharp_roi_xstart = 0  # 12bit unsigned
        self.sharp_roi_ystart = 0  # 12bit unsigned
        self.sharp_roi_xend = 0  # 12bit unsigned
        self.sharp_roi_yend = 0  # 12bit unsigned
        self.sharp_ink_enable = 0  # 1bit unsigned
        self.sharp_ink_mode = 0  # 4bit unsigned

    ## =============== overwrite methods  ===============
    def dump(self, filename):
        return False

    def load(self, filename):
        try:
            if filename.endswith(".bin"):
                with open(filename, "rt") as f:
                    data = f.read()
                    # TODO: parse data

            elif filename.endswith(".dat"):
                with open(filename, "rt") as f:
                    data = f.read().strip()
                    # TODO: parse data
            else:
                print(f"[{self.name}] 文件类型不支持!")
        except Exception as e:
            print(f"[{self.name}] 错误: 加载文件\'{filename}\'失败: {str(e)}")
        return False

    def check(self):
        return True


if __name__ == "__main__":
    reg = SharpLiteRegisters_RK3572()
    reg.ENABLE_CTRL.sharp_en = 1
    reg.USM_CTRL.peaking_gain = 0x300
    reg.USM_COEF.coef_A = 0x10
    reg.USM_COEF.coef_B = 0x20
    reg.USM_COEF.coef_C = 0x30

    print("checking SharpLiteRegisters_RK3572:")

    print(read_reg(reg.USM_COEF), reg.USM_COEF.coef_A, reg.USM_COEF.coef_B, reg.USM_COEF.coef_C)
    print(read_reg(reg.USM_CTRL), reg.USM_CTRL.peaking_gain)

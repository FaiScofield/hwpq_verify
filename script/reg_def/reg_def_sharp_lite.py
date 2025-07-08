"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_sharp_lite.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-03 17:35:32
"""

from ctypes import *
from typing import TypeVar, Type


def read_reg(reg: Structure):
    val = 0
    bit = 0
    for i in range(0, reg._fields_.__len__()):
        name, _, len = reg._fields_[i]
        bit += len
        val |= getattr(reg, name) << bit
    return hex(val)


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


# class RK3572_SharpLiteReg_0x34(Structure):
#     _fields_ = [
#         ("sharp_ink_enable", c_uint32, 1),
#         ("sharp_ink_mode", c_uint32, 4),
#         ("i_ink_idx_h":  c_uint32, 4),
#         ("i_ink_idx_v", c_uint32, 4),
#     ]
#     _pack_ = 1


class SharpLiteRegisters_RK3572():
    platform = "RK3572"
    ENABLE_CTRL = RK3572_SharpLiteReg_0x00()  # Address Offset: 0x0000
    GATING_CTRL = RK3572_SharpLiteReg_0x04()  # Address Offset: 0x0004
    RESERVED0008 = [c_uint32(), c_uint32()]  # Address Offset: 0x0008
    USM_CTRL = RK3572_SharpLiteReg_0x10()  # Address Offset: 0x0010
    USM_COEF = RK3572_SharpLiteReg_0x14()  # Address Offset: 0x0014
    RESERVED0018 = [c_uint32(), c_uint32()]  # Address Offset: 0x0018
    SHOOT_CTRL_REG0 = RK3572_SharpLiteReg_0x20()  # Address Offset: 0x0020
    SHOOT_CTRL_REG1 = RK3572_SharpLiteReg_0x24()  # Address Offset: 0x0024
    SHOOT_CTRL_REG2 = RK3572_SharpLiteReg_0x28()  # Address Offset: 0x0028
    ROI_CTRL0 = RK3572_SharpLiteReg_0x2c()  # Address Offset: 0x002C
    ROI_CTRL1 = RK3572_SharpLiteReg_0x30()  # Address Offset: 0x0030
    # INK_CTRL = RK3572_SharpLiteReg_0x34()  # Address Offset: 0x0034



if __name__ == "__main__":
    reg = SharpLiteRegisters_RK3572()
    reg.ENABLE_CTRL.sharp_en = 1
    reg.USM_CTRL.peaking_gain = 0x300
    reg.USM_COEF.coef_A = 0x10
    reg.USM_COEF.coef_B = 0x20
    reg.USM_COEF.coef_C = 0x30

    print("checking SharpLiteRegisters_RK3572:")
    # for name, field, len in reg._fields_:
    #     print(f"{name}: {getattr(reg, name)} {field.__name__}, {len}")
    #     total_sub_len = 0
    #     for sub_name, sub_field, sub_len in field._fields_:
    #         print(f"{name}: {getattr(reg, name)} {field.__name__}, {len}")
    #         total_sub_len += sub_len
    #     if total_sub_len != 32:
    #         print(f"error: total_sub_len != 32 for reg {name} !")

    print(read_reg(reg.USM_COEF), reg.USM_COEF.coef_A, reg.USM_COEF.coef_B, reg.USM_COEF.coef_C)
    print(read_reg(reg.USM_CTRL), reg.USM_CTRL.peaking_gain)
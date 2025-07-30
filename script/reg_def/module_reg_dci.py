"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : reg_def_dci.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-23
Description :
LastEditTime: 2025-07-30
"""

import os
import sys
import argparse

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from reg_def import *
from config_def import *


class DciModuleIndex(Enum):
    """enum = (name, ip_address, offset, nb_regs)"""

    VDPP_VEP = ("VDPP_VEP", 0x0, 0x00001004, 7)
    VOP_CLUSTER0 = ("VOP_CLUSTER0", 0xF90000000, 0x00001104, 6 + 1408)  # 1408=5632/4


class DciRegister(ModuleRegisterCore):
    def __init__(
        self, name: str = "DCI", platform: str = 'RK3572', index: DciModuleIndex = DciModuleIndex.VOP_CLUSTER0
    ):
        super().__init__(name, platform)

        self.index = index
        self.config = DciConfig(self.name)
        self.reg_dicts = {DciModuleIndex.VDPP_VEP: [], DciModuleIndex.VOP_CLUSTER0: []}  # DciModuleIndex : list[Reg]
        self.base_addr = 0x0
        self.update(platform=platform)

    ## =============== overwrite methods  ===============
    def update(self, **kwargs) -> bool:
        if "platform" in kwargs:
            self.platform = kwargs["platform"]
        if "index" in kwargs:
            index = kwargs["index"]
            self.index = index if isinstance(index, DciModuleIndex) else DciModuleIndex[index]

        if self.platform.lower() == "rk3572":
            self.ip_addr = self.index.value[1]
            self.base_addr = self.index.value[2]
            self.nb_regs = self.index.value[3]
            self.reg_dicts[DciModuleIndex.VDPP_VEP] = [
                Reg(0x00001004, 0x0, "CONFIG0"),
                Reg(0x00001008, 0x0, "WORKING_MODE"),
                Reg(0x000010E0, 0x0, "DCI_YRGB_ADDR"),
                Reg(0x000010E4, 0x0, "DCI_YRGB_VIR_STRIDE"),
                Reg(0x000010E8, 0x0, "DCI_IMG_SIZE"),
                Reg(0x000010EC, 0x0, "DCI_CTRL"),
                Reg(0x000010F0, 0x0, "DCI_HIST_ADDR"),
            ]
            self.reg_dicts[DciModuleIndex.VOP_CLUSTER0] = [
                Reg(0x00001104, 0x0, "DCI_BLK_SIZE"),
                Reg(0x00001108, 0x0, "DCI_BLK_OFFSET"),
                Reg(0x0000110C, 0x0, "DCI_PIX_REGION"),
                Reg(0x00001110, 0x0, "DCI_LUMA_SAT_ADJ_0"),
                Reg(0x00001114, 0x0, "DCI_LUMA_SAT_ADJ_1"),
                Reg(0x00001118, 0x0, "DCI_CTRL"),
                # Reg(0x0000111C, 0x0, "DCI_LUT_MST"),
            ]
            self.reg_dicts[DciModuleIndex.VOP_CLUSTER0] += [
                Reg(0x0001124 + idx * 4, 0x0, f"DCI_LUT_DATA{idx}") for idx in range(1408)
            ]
            self.packed_lut = np.zeros(5632, dtype=np.uint8)
            self.regs = self.reg_dicts[self.index]

            assert len(self.regs) == self.nb_regs
            assert self.regs[0].offset == self.base_addr
            return True
        else:
            self.logger.error(f"Platform {self.platform} is not supported now!")
        return False

    def config2regs(self) -> bool:
        if len(self.regs) < self.nb_regs:
            self.logger.error(f"current registers num={len(self.regs)} is not equal to required={self.nb_regs}!")
            return False
        cfg = self.config
        self.set(
            name="DCI_BLK_SIZE",
            value=(cfg.vop_config.act_blk_size_h & 0x1FF) | ((cfg.vop_config.act_blk_size_v & 0x1FF) << 16),
        )
        self.set(
            name="DCI_BLK_OFFSET",
            value=(cfg.vop_config.act_start_h_offset & 0x1FF) | ((cfg.vop_config.act_start_v_offset & 0x1FF) << 16),
        )
        self.set(
            name="DCI_PIX_REGION",
            value=(cfg.vop_config.blk_size_fix & 0xFFFFF)
            | ((cfg.vop_config.act_start_h_idx & 0x1F) << 20)
            | ((cfg.vop_config.act_start_v_idx & 0x1F) << 26),
        )
        self.set(
            name="DCI_LUMA_SAT_ADJ_0",
            value=(cfg.vop_config.luma_sat_adj_zero & 0xFFFF) | ((cfg.vop_config.luma_sat_adj_thrd & 0xFFFF) << 16),
        )
        self.set(
            name="DCI_LUMA_SAT_ADJ_1", value=(cfg.vop_config.luma_sat_adj_k & 0xFFFF) | ((cfg.vop_config.sat_w & 0x7F) << 16)
        )
        self.set(
            name="DCI_CTRL", value=(cfg.vop_config.dci_enable & 0x1) | ((cfg.vop_config.ca_enable & 0x1) << 1) | (1 << 2)
        )
        # self.set(name="DCI_LUT_MST", value=0x0)

        self.packed_lut = self.pack_lut(
            cfg.vop_config.dci_global_lut, cfg.vop_config.dci_locat_ratio, cfg.vop_config.dci_local_lut
        )
        for i in range(1408):
            self.set(
                name=f"DCI_LUT_DATA{i}",
                value=self.packed_lut[i * 4 + 0].astype(np.uint32)
                | (self.packed_lut[i * 4 + 1].astype(np.uint32) << 8)
                | (self.packed_lut[i * 4 + 2].astype(np.uint32) << 16)
                | (self.packed_lut[i * 4 + 3].astype(np.uint32) << 24),
            )
        return True

    def regs2config(self) -> bool:
        try:
            val = self.get(name="DCI_BLK_SIZE")
            self.config.vop_config.act_blk_size_h = (val >> 0) & 0x1FF
            self.config.vop_config.act_blk_size_v = (val >> 16) & 0x1FF
            val = self.get(name="DCI_BLK_OFFSET")
            self.config.vop_config.act_start_h_offset = (val >> 0) & 0x1FF
            self.config.vop_config.act_start_v_offset = (val >> 16) & 0x1FF
            val = self.get(name="DCI_PIX_REGION")
            self.config.vop_config.blk_size_fix = (val >> 0) & 0xFFFFF
            self.config.vop_config.act_start_h_idx = (val >> 20) & 0x1F
            self.config.vop_config.act_start_v_idx = (val >> 26) & 0x1F
            val = self.get(name="DCI_LUMA_SAT_ADJ_0")
            self.config.vop_config.luma_sat_adj_zero = (val >> 0) & 0xFFFF
            self.config.vop_config.luma_sat_adj_thrd = (val >> 16) & 0xFFFF
            val = self.get(name="DCI_LUMA_SAT_ADJ_1")
            self.config.vop_config.luma_sat_adj_k = (val >> 0) & 0xFFFF
            self.config.vop_config.sat_w = (val >> 16) & 0x7F
            val = self.get(name="DCI_CTRL")
            self.config.vop_config.dci_enable = (val >> 0) & 0x1
            self.config.vop_config.ca_enable = (val >> 1) & 0x1
        except Exception as e:
            self.logger.error(f"get register value error: {e}")
            return False

        ## get self.packed_lut then unpack it to global_lut_x256, locat_ratio_x256, local_lut_x4096
        for i in range(1408):
            val = self.get(name=f"DCI_LUT_DATA{i}")
            self.packed_lut[i * 4 + 0] = (val >> 0) & 0xFF
            self.packed_lut[i * 4 + 1] = (val >> 8) & 0xFF
            self.packed_lut[i * 4 + 2] = (val >> 16) & 0xFF
            self.packed_lut[i * 4 + 3] = (val >> 24) & 0xFF
        (self.config.vop_config.dci_global_lut, self.config.vop_config.dci_locat_ratio, self.config.vop_config.dci_local_lut) = (
            self.unpack_lut(self.packed_lut)
        )
        return True

    ## =============== adiitional auxiliary methods  ===============
    def pack_lut(
        self, global_lut_x256: np.ndarray, locat_ratio_x256: np.ndarray, local_lut_x4096: np.ndarray
    ) -> np.ndarray:
        packed_lut = np.zeros(5632, np.uint8)
        idx = 0
        for i in range(len(global_lut_x256) // 4):  # u10_x256 => u8_x320
            tmp0_u10 = global_lut_x256[i * 4 + 0]
            tmp1_u10 = global_lut_x256[i * 4 + 1]
            tmp2_u10 = global_lut_x256[i * 4 + 2]
            tmp3_u10 = global_lut_x256[i * 4 + 3]
            packed_lut[idx + 0] = tmp0_u10 & ((1 << 8) - 1)
            packed_lut[idx + 1] = ((tmp1_u10 & ((1 << 6) - 1)) << 2) + (tmp0_u10 >> 8)
            packed_lut[idx + 2] = ((tmp2_u10 & ((1 << 4) - 1)) << 4) + (tmp1_u10 >> 6)
            packed_lut[idx + 3] = ((tmp3_u10 & ((1 << 2) - 1)) << 6) + (tmp2_u10 >> 4)
            packed_lut[idx + 4] = tmp3_u10 >> 2
            idx += 5
        assert idx == 320

        for i in range(len(locat_ratio_x256) // 4):  # u6_x256 => u8_x192
            tmp0_u6 = locat_ratio_x256[4 * i + 0]
            tmp1_u6 = locat_ratio_x256[4 * i + 1]
            tmp2_u6 = locat_ratio_x256[4 * i + 2]
            tmp3_u6 = locat_ratio_x256[4 * i + 3]
            packed_lut[idx + 0] = ((tmp1_u6 & ((1 << 2) - 1)) << 6) + (tmp0_u6 >> 0)
            packed_lut[idx + 1] = ((tmp2_u6 & ((1 << 4) - 1)) << 4) + (tmp1_u6 >> 2)
            packed_lut[idx + 2] = ((tmp3_u6 & ((1 << 6) - 1)) << 2) + (tmp2_u6 >> 4)
            idx += 3
        assert idx == 320 + 192

        for i in range(len(local_lut_x4096) // 4):  # u10_x4096 => u8_x5120
            tmp0_u10 = local_lut_x4096[4 * i + 0]
            tmp1_u10 = local_lut_x4096[4 * i + 1]
            tmp2_u10 = local_lut_x4096[4 * i + 2]
            tmp3_u10 = local_lut_x4096[4 * i + 3]
            packed_lut[idx + 0] = tmp0_u10 & ((1 << 8) - 1)
            packed_lut[idx + 1] = ((tmp1_u10 & ((1 << 6) - 1)) << 2) + (tmp0_u10 >> 8)
            packed_lut[idx + 2] = ((tmp2_u10 & ((1 << 4) - 1)) << 4) + (tmp1_u10 >> 6)
            packed_lut[idx + 3] = ((tmp3_u10 & ((1 << 2) - 1)) << 6) + (tmp2_u10 >> 4)
            packed_lut[idx + 4] = tmp3_u10 >> 2
            idx += 5
        assert idx == 5632
        return packed_lut

    def unpack_lut(self, packed_lut: np.ndarray) -> tuple:
        global_lut_x256 = np.zeros(256, dtype=np.uint16)
        locat_ratio_x256 = np.zeros(256, dtype=np.uint8)
        local_lut_x4096 = np.zeros(4096, dtype=np.uint16)

        idx = 0
        for i in range(64):  # 256/4=64
            byte0 = packed_lut[idx + 0]
            byte1 = packed_lut[idx + 1]
            byte2 = packed_lut[idx + 2]
            byte3 = packed_lut[idx + 3]
            byte4 = packed_lut[idx + 4]
            global_lut_x256[4 * i + 0] = (byte0 & 0xFF) | ((byte1 & 0x03) << 8)
            global_lut_x256[4 * i + 1] = ((byte1 >> 2) & 0x3F) | ((byte2 & 0x0F) << 6)
            global_lut_x256[4 * i + 2] = ((byte2 >> 4) & 0x0F) | ((byte3 & 0x3F) << 4)
            global_lut_x256[4 * i + 3] = ((byte3 >> 6) & 0x03) | (byte4 << 2)
            idx += 5
        assert idx == 320

        for i in range(64):  # 256/4=64
            byte0 = packed_lut[idx + 0]
            byte1 = packed_lut[idx + 1]
            byte2 = packed_lut[idx + 2]
            locat_ratio_x256[4 * i + 0] = byte0 & 0x3F
            locat_ratio_x256[4 * i + 1] = ((byte0 >> 6) & 0x03) | ((byte1 & 0x0F) << 2)
            locat_ratio_x256[4 * i + 2] = ((byte1 >> 4) & 0x0F) | ((byte2 & 0x03) << 4)
            locat_ratio_x256[4 * i + 3] = (byte2 >> 2) & 0x3F
            idx += 3
        assert idx == 320 + 192

        for i in range(1024):  # 4096/4=1024
            byte0 = packed_lut[idx + 0]
            byte1 = packed_lut[idx + 1]
            byte2 = packed_lut[idx + 2]
            byte3 = packed_lut[idx + 3]
            byte4 = packed_lut[idx + 4]
            local_lut_x4096[4 * i + 0] = (byte0 & 0xFF) | ((byte1 & 0x03) << 8)
            local_lut_x4096[4 * i + 1] = ((byte1 >> 2) & 0x3F) | ((byte2 & 0x0F) << 6)
            local_lut_x4096[4 * i + 2] = ((byte2 >> 4) & 0x0F) | ((byte3 & 0x3F) << 4)
            local_lut_x4096[4 * i + 3] = ((byte3 >> 6) & 0x03) | (byte4 << 2)
            idx += 5
        assert idx == 5632
        return global_lut_x256, locat_ratio_x256, local_lut_x4096


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", type=str, default="dump", help="选择测试接口: dump/load/gen/c2r/r2c")
    parser.add_argument("-f", "--file", type=str, default="", help="读写文件名")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="设置平台: RK3572/RK3576")
    parser.add_argument("-s", "--seed", type=int, default=114514, help="设置随机种子")
    parser.print_usage()
    args = parser.parse_args()

    register = DciRegister()

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

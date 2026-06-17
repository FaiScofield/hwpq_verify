"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : acm_impls.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-14
Description : Concrete ACM implementation subclasses.

    * AcmImplHwRk       - hardware ACM, 4 LUTs at (9, 13, 65, 17)
    * AcmImplSwRk       - software ACM matching RK semantics, (9, 13, 65, 65)
    * AcmImplSwEvideo   - evideo ACM, (9, 13, 65, 65) with wider delta range
    * AcmImplSwVariant  - any (y, s, h, h2) with h2 <= h
LastEditTime: 2026-06-14
"""

import os
import sys
import argparse
import numpy as np

if __package__:
    from .acm_impl_base import AcmImplBase, linear_resize_array_1d
    from .. import utils as utl
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from acm_impl_base import AcmImplBase, linear_resize_array_1d
    import utils as utl


# ---------------------------------------------------------------------------
# AcmImplHwRk
# ---------------------------------------------------------------------------
class AcmImplHwRk(AcmImplBase):
    """ACM implementation for RK VOP hardware. len_h2 = 17."""

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_h2: int = 17,
        delta_range: tuple = (0.25, 0.25, 64),
        use_cordic: bool = True,
    ):
        super().__init__(
            len_y=len_y, len_s=len_s, len_h=len_h, len_hd=len_h2, delta_range=delta_range, use_cordic=use_cordic
        )
        print("[ACM] created AcmImplHwRk.")

    ## override
    def _do_acm(
        self,
        y: np.ndarray,
        cb: np.ndarray,
        cr: np.ndarray,
        s: np.ndarray,
        h_deg: np.ndarray,
        h_rad: np.ndarray,
        depth_uv: int,
        y_range: int,
        cbcr_center: int,
        use_cordic: bool,
    ) -> np.ndarray:
        # TODO: implement hardware ACM
        return super()._do_acm_yuv(y, cb, cr, s, h_deg, h_rad, depth_uv, y_range, cbcr_center, use_cordic)


# ---------------------------------------------------------------------------
# AcmImplSwRk
# ---------------------------------------------------------------------------
class AcmImplSwRk(AcmImplBase):
    """ACM implementation matching RK software semantics. len_h2 = 65."""

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_h2: int = 65,
        delta_range: tuple = (0.25, 0.25, 64),
        use_cordic: bool = False,
    ):
        super().__init__(
            len_y=len_y, len_s=len_s, len_h=len_h, len_hd=len_h2, delta_range=delta_range, use_cordic=use_cordic
        )
        print("[ACM] created AcmImplSwRk.")


# ---------------------------------------------------------------------------
# AcmImplSwEvideo
# ---------------------------------------------------------------------------
class AcmImplSwEvideo(AcmImplBase):
    """EVideo-style ACM with wider delta mapping range.

    Default delta_range is (1.0, 1.0, 64) (delta_y/s in [-1, 1] of full range, h in [-64, 64] deg).
    Can be switched to 0.25 via set_delta_range(0.25) to match the rk semantics.
    """

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_h2: int = 65,
        delta_range: tuple = (1.0, 1.0, 64),
        use_cordic: bool = False,
    ):
        super().__init__(
            len_y=len_y, len_s=len_s, len_h=len_h, len_hd=len_h2, delta_range=delta_range, use_cordic=use_cordic
        )
        print("[ACM] created AcmImplSwEvideo.")


# ---------------------------------------------------------------------------
# AcmImplSwVariant
# ---------------------------------------------------------------------------
class AcmImplSwVariant(AcmImplBase):
    """ACM with arbitrary LUT lengths (only constraint: len_h2 <= len_h).

    The 4 len arguments can be changed at runtime via set_len / set_step.
    The current LUT is always re-sampled (bicubic) from the default LUT
    when the length changes; call sync_to_default() to push runtime edits
    back into the default set (bicubic).
    """

    def __init__(
        self,
        len_y: int = 9,
        len_s: int = 13,
        len_h: int = 65,
        len_h2: int = 65,
        delta_range: tuple = (1.0, 1.0, 64),
        use_cordic: bool = False,
    ):
        super().__init__(
            len_y=len_y, len_s=len_s, len_h=len_h, len_hd=len_h2, delta_range=delta_range, use_cordic=use_cordic
        )
        self.source_algo = None
        self.source_config = None
        print("[ACM] created AcmImplSwVariant.")

    # ------------------------------------------------------------------
    # extra helper specific to the variant class
    # ------------------------------------------------------------------
    def interpolate_from(self, source_acm: AcmImplBase, kernel: np.ndarray = None) -> bool:
        """Interpolate LUT data from another ACM instance.

        Resamples all 9 LUT tables from source_acm to match self's dimensions.
        Both default and current sets are populated.
        """
        if not source_acm.b_lut_ready:
            print("[ACM] Source ACM LUT is not ready!")
            return False

        print(
            f"[ACM] Interpolating LUTs from source: "
            f"y={source_acm.len_y}x{self.len_y}, s={source_acm.len_s}x{self.len_s}, "
            f"h={source_acm.len_h}x{self.len_h}, h2={source_acm.len_hd}x{self.len_hd}"
        )

        # 1D delta LUTs
        if source_acm.len_h != self._default_len_h:
            self._default_lut_delta_ybyh = linear_resize_array_1d(source_acm.lut_delta_ybyh, self._default_len_h)
            self._default_lut_delta_sbyh = linear_resize_array_1d(source_acm.lut_delta_sbyh, self._default_len_h)
            self._default_lut_delta_hbyh = linear_resize_array_1d(source_acm.lut_delta_hbyh, self._default_len_h)
            print(f"[ACM] Updated delta LUT size: {source_acm.len_h} => {self._default_len_h}")
        else:
            self._default_lut_delta_ybyh = source_acm.lut_delta_ybyh.copy()
            self._default_lut_delta_sbyh = source_acm.lut_delta_sbyh.copy()
            self._default_lut_delta_hbyh = source_acm.lut_delta_hbyh.copy()

        # 2D gain LUTs (Y axis)
        self._default_lut_gain_ybyy = _resize_2d_lut(
            source_acm.lut_gain_ybyy,
            source_acm.len_hd,
            source_acm.len_y,
            self._default_len_hd,
            self._default_len_y,
            kernel,
        )
        self._default_lut_gain_sbyy = _resize_2d_lut(
            source_acm.lut_gain_sbyy,
            source_acm.len_hd,
            source_acm.len_y,
            self._default_len_hd,
            self._default_len_y,
            kernel,
        )
        self._default_lut_gain_hbyy = _resize_2d_lut(
            source_acm.lut_gain_hbyy,
            source_acm.len_hd,
            source_acm.len_y,
            self._default_len_hd,
            self._default_len_y,
            kernel,
        )

        # 2D gain LUTs (S axis)
        self._default_lut_gain_ybys = _resize_2d_lut(
            source_acm.lut_gain_ybys,
            source_acm.len_hd,
            source_acm.len_s,
            self._default_len_hd,
            self._default_len_s,
            kernel,
        )
        self._default_lut_gain_sbys = _resize_2d_lut(
            source_acm.lut_gain_sbys,
            source_acm.len_hd,
            source_acm.len_s,
            self._default_len_hd,
            self._default_len_s,
            kernel,
        )
        self._default_lut_gain_hbys = _resize_2d_lut(
            source_acm.lut_gain_hbys,
            source_acm.len_hd,
            source_acm.len_s,
            self._default_len_hd,
            self._default_len_s,
            kernel,
        )

        # Copy gains
        self.gain_y = source_acm.gain_y
        self.gain_s = source_acm.gain_s
        self.gain_h = source_acm.gain_h

        # Save source info
        self.source_algo = type(source_acm).__name__
        self.source_config = getattr(source_acm, 'source_config', None)

        # Propagate default -> current
        self._resample_default_to_current(method="bicubic")
        self.b_lut_ready = True
        print("[ACM] Interpolation completed successfully.")
        return True


# ---------------------------------------------------------------------------
# private helper for AcmImplSwVariant.interpolate_from
# ---------------------------------------------------------------------------
def _resize_2d_lut(
    src_lut: np.ndarray, src_h2: int, src_dim: int, dst_h2: int, dst_dim: int, kernel: np.ndarray
) -> np.ndarray:
    """Resize a 2D LUT from (src_h2, src_dim) to (dst_h2, dst_dim) in two passes."""
    if src_lut.shape == (dst_h2, dst_dim):
        return src_lut.copy()

    if src_h2 != dst_h2:
        tmp = np.zeros((dst_h2, src_dim), dtype=src_lut.dtype)
        for i in range(src_dim):
            tmp[:, i] = linear_resize_array_1d(src_lut[:, i], dst_h2)
    else:
        tmp = src_lut.copy()

    if src_dim != dst_dim:
        result = np.zeros((dst_h2, dst_dim), dtype=src_lut.dtype)
        for i in range(dst_h2):
            result[i, :] = linear_resize_array_1d(tmp[i, :], dst_dim)
        return result
    return tmp


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------
def main() -> None:
    """Command-line entry for ACM LUT verify / dump.

    Reads a YUV444 planar image, loads (or generates) a LUT, applies ACM
    and writes the result back as a planar YUV file, then dumps the
    effective config and LUT preview.
    """
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("-i", "--input", default="", type=str, help="输入图像文件，yuv444p格式")
    parser.add_argument("-o", "--output", default="", type=str, help="输出图像文件")
    parser.add_argument("-c", "--config", default="", type=str, help=".json 配置文件")
    parser.add_argument("-w", "--width", default=1920, type=int, help="图像宽度, 默认 1920")
    parser.add_argument("-g", "--height", default=1080, type=int, help="图像高度, 默认 1080")
    parser.add_argument("-s", "--step", type=float, nargs='+', help="LUT step 数组, 4 个元素")
    parser.add_argument("-l", "--len", type=int, nargs='+', help="LUT len 数组, 4 个元素")
    parser.add_argument("-G", "--gain", type=int, nargs='+', help="LUT gain 数组, 3 个元素")
    parser.add_argument("-n", "--iter_num", default=13, type=int, help="Cordic 迭代次数, 默认: 13")
    parser.add_argument("-b", "--increase_bits", default=3, type=int, help="Cordic S 定点提示精度, 默认: 3")
    parser.add_argument("-uv", "--uv", type=int, nargs='+', help="传入U/V数值测试Cordic结果")
    parser.add_argument("-hs", "--hs", type=int, nargs='+', help="传入H/S数值测试Cordic结果")
    args, _ = parser.parse_known_args()

    # DEF_OUT_DIR = "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/test_var_lut"
    DEF_OUT_DIR = "D:/RkDefaultDumpData"
    H = args.height
    W = args.width
    infile = (
        "V:/hwpq_verify_data/vop_robin_fpga_verify_acm/input_1920x1080_yuv444p_601F.yuv"
        if args.input == ""
        else args.input
    )
    outfile = f"{DEF_OUT_DIR}/out_acm_1920x1080_yuv444p_601F.yuv" if args.output == "" else args.output
    cfgfile = "G:/Codes/gerrit_projects/hwpq_verify/data/vdpp_vop_config_3576.json" if args.config == "" else args.config

    ## read YUV444 planar (Y | Cb | Cr)
    data = np.fromfile(infile, np.uint8)
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:, :, 0] = data[0 : H * W * 1].reshape(H, W)
    img[:, :, 1] = data[H * W * 1 : H * W * 2].reshape(H, W)
    img[:, :, 2] = data[H * W * 2 : H * W * 3].reshape(H, W)

    acm = AcmImplSwRk()

    if cfgfile != "":
        ret = acm.load_json(cfgfile)
        if not ret:
            print("[ACM] load config failed.")
            exit(ret)
    else:
        acm.set_len(9, 13, 65, 17)
        acm.gen_test_config(False)

    if args.step:
        acm.set_step(args.step[0], args.step[1], args.step[2], args.step[3])
    elif args.len:
        acm.set_len(args.len[0], args.len[1], args.len[2], args.len[3])
    if args.gain:
        acm.set_global_gains(args.gain[0], args.gain[1], args.gain[2])

    out = acm.do_acm_u8(img)

    ## write planar Y then Cb then Cr (same layout as input file)
    out.tofile(outfile)  # shape is already [C,H,W] (planar)
    print(f"[ACM] done. write output file to {outfile}")

    acm.dump_json(f"{DEF_OUT_DIR}/acm_var_config_len_y{acm.len_y}_s{acm.len_s}" f"_h{acm.len_h}_{acm.len_hd}.json")
    acm.dump_lut(DEF_OUT_DIR)
    utl.run_cmd(f"cp {infile} {DEF_OUT_DIR}")


if __name__ == '__main__':
    main()

    # b_strict = True
    # seed = 114517
    # acm = AcmImplSwRk(9, 13, 65, 65)
    # acm.gen_test_config(b_strict, seed)

    # kernel = np.array([1, 4, 6, 4, 1])
    # kernel = np.outer(kernel, kernel)
    # kernel = kernel / kernel.sum()
    # print("kernel: \n", kernel)

    # acm.set_len(9, 13, 65, 17, kernel)
    # if b_strict:
    #     acm.dump_json(
    #         f"acm_var_config_len_y{acm.len_y}_s{acm.len_s}_h{acm.len_h}"
    #         f"_hd{acm.len_hd}_strict_rand{seed}_kernel.json"
    #     )
    # else:
    #     acm.dump_json(f"acm_var_config_len_y{acm.len_y}_s{acm.len_s}_h{acm.len_h}" f"_hd{acm.len_hd}_rand{seed}.json")

"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cordic.py
Author      : vance.wu@rock-chips.com
Date        : 2025-11-27
Description :
LastEditTime: 2025-11-27
"""

import os
import sys
import argparse
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import utils as utl

CORDIC_S_FIX_BITS = 3
CORDIC_XY_FIX_BITS = 6
## u14 max, 8bit fixed: angle [45, 26.565, 14.036, ..., 0.006994, 0.003497] * 256
CORDIC_ATAN_LUT_FIX8 = [11520, 6801, 3593, 1824, 916, 458, 229, 115, 57, 29, 14, 7, 4, 2, 1]
CORDIC_COEF_K_FIX10 = 622  # 10bit fixed: 0.607252935 * 1024, (from K4 to K15 are all the same)
CORDIC_MIN_ITER_NUM = 7
CORDIC_MAX_ITER_NUM = 15
CORDIC_DEG180_FIX8 = 180 << 8


def cordic_cbcr2hs(cb, cr, depth_uv: int, iter_num: int = 13, increase_bits_for_s: int = 0, keep_fix_out: bool = False):
    """
    depth_uv: 8 or 10
    input cb range: [-128, 127] in S8 / [-512, 511] in S10
    input cr range: [-128, 127] in S8 / [-512, 511] in S10
    output h range: [-180, 180] in S9, add more 8 bits fixed if not keep_fix_out
    output s range: [  0,  181] in U8 / [   0, 724] in U10, add more 'increase_bits_for_s' fixed if not keep_fix_out
    """
    assert depth_uv >= 8

    ## at leat 7 times iterations make sure the error of the output angle is less than 1 degree
    iter_num = utl.clamp(iter_num, CORDIC_MIN_ITER_NUM, CORDIC_MAX_ITER_NUM)

    ## the depth of x & y should be > iter_num, otherwise, the remain (depth - iter_num) iterations will be useless!
    increase_bits_for_h = 8
    increase_bits_for_s = utl.clamp(increase_bits_for_s, 0, 8)
    precision_s = increase_bits_for_s + depth_uv
    if precision_s < iter_num:
        print(
            f"Warning: increase_bits_for_s({increase_bits_for_s}) + depth_uv({depth_uv}) < iter_num({iter_num}), some iterations will be useless!"
        )

    ## swap to the first coordinate quadrant
    x = abs(cb) << CORDIC_XY_FIX_BITS#increase_bits_for_s  # s20
    y = abs(cr) << CORDIC_XY_FIX_BITS#increase_bits_for_s  # s20
    z = 0  # [0, 90] << 8

    # mx = 0
    # my = 0
    # mz = 0

    ## cordic iteration
    for i in range(iter_num):
        d = (y < 0) * 2 - 1  # +y => -1 -y => +1
        xp = x - d * (y >> i)
        yp = y + d * (x >> i)
        zp = z - d * CORDIC_ATAN_LUT_FIX8[i]
        x = xp
        y = yp
        z = zp

        # mx = max(mx, abs(x))
        # my = max(my, abs(y))
        # mz = max(mz, abs(z))

    # s = (CORDIC_COEF_K_FIX10 * x + (1 << 9)) >> 10  # x=s/K, K=0.607252935
    s = CORDIC_COEF_K_FIX10 * x  # x=s/K, K=0.607252935
    if type(cb) == np.ndarray:
        h = np.where(s == 0, np.zeros_like(cb), np.maximum(z, 0))
    else:
        h = 0 if s == 0 else np.maximum(z, 0)  # z might be a little negative after cordic iteration

    '''
      return H value to four quadrants by input sign of UV
        | quadrant | x_y_in       | h_out   | s_out |
        | -------- | ------------ | ------- | ----- |
        |    1     | x0=+x, y0=+y | +z      | Kx    |
        |    2     | x0=-x, y0=+y | -(z-pi) | Kx    |
        |    3     | x0=-x, y0=-y | +(z-pi) | Kx    |
        |    4     | x0=+x, y0=-y | -z      | Kx    |
    '''
    cb_mask = cb >= 0
    cr_mask = cr >= 0
    cb_mask_pi = cb < 0  # +cb => 0, -cb => 1
    cb_mask_H = 2 * cb_mask - 1  # +cb => 1, -cb => -1
    cr_mask_H = 2 * cr_mask - 1  # +cr => 1, -cr => -1
    h = (CORDIC_DEG180_FIX8 * cb_mask_pi + h * cb_mask_H) * cr_mask_H

    if not keep_fix_out:
        h = np.int32(h)
        h = (h + (1 << increase_bits_for_h - 1) + (h >> 31)) >> increase_bits_for_h
        depth_h = 8
        s_shift = increase_bits_for_s + 10
        s = (s + (1 << s_shift - 1)) >> s_shift
        depth_s = depth_uv
    else:
        depth_h = 8 + increase_bits_for_h
        depth_s = depth_uv + increase_bits_for_s

        s_shift = 10 + CORDIC_XY_FIX_BITS - increase_bits_for_s
        s = (s + (1 << s_shift - 1)) >> s_shift

    return h, s, depth_h, depth_s


def cordic_hs2cbcr(
    h, s, depth_h: int, depth_s: int, out_depth_s: int, iter_num: int = 13, increase_bits_for_s: int = 5
):
    """
    depth_h: 8(+8)
    depth_s: [8,16] or [10,18]
    input   h range: [-180, 180] in S9 / ([-180, 180]<<8) in S17
    input   s range: [  0,  181](<<[0,8]) / [   0, 724] in U10
    output cb range: [-128, 127] in S8 / [-512, 511] in S10
    output cr range: [-128, 127] in S8 / [-512, 511] in S10
    """
    assert depth_s >= 8

    ## at leat 7 times iterations make sure the error of the output angle is less than 1 degree
    iter_num = utl.clamp(iter_num, CORDIC_MIN_ITER_NUM, CORDIC_MAX_ITER_NUM)

    ## the depth of x & y should be > iter_num, otherwise, the remain (depth - iter_num) iterations will be useless!
    increase_bits_for_h = 8
    increase_bits_for_s = utl.clamp(increase_bits_for_s, 0, 8)
    precision_s = increase_bits_for_s + depth_s
    if precision_s < iter_num:
        print(
            f"Warning: increase_bits_for_s({increase_bits_for_s}) + depth_s({depth_s}) < iter_num({iter_num}), some iterations will be useless!"
        )

    ## change H to the first/fourth quadrant
    scale_h = 256 if depth_h == 16 else 1
    H_flag = ((h >= -90 * scale_h) & (h <= 90 * scale_h)) * 2 - 1  # 1: q1/q4; -1: q2/q3
    H_cordicPiFlag = np.int32(h > 90 * scale_h) - np.int32(h < -90 * scale_h)  # 0: q1/q4; 1: q2; -1: q3
    h0 = H_cordicPiFlag * 180 * scale_h + H_flag * h

    x = s << increase_bits_for_s
    y = 0
    z = h0 << (16 - depth_h)

    ## cordic iteration
    for i in range(iter_num):
        d = (z > 0) * 2 - 1
        xp = x - d * (y >> i)
        yp = y + d * (x >> i)
        zp = z - d * CORDIC_ATAN_LUT_FIX8[i]
        x = xp
        y = yp
        z = zp

    fix_bits = 10 + precision_s - out_depth_s
    cb = (CORDIC_COEF_K_FIX10 * x + (1 << fix_bits - 1)) >> fix_bits
    cr = (CORDIC_COEF_K_FIX10 * y + (1 << fix_bits - 1)) >> fix_bits

    ## get the sign of U by the H value
    cb = cb * H_flag

    return cb, cr


def test_cordic_cbcr2hs(depth: int, iter_num: int, increase_bits: int, uv):
    assert depth in [8, 10]
    if depth == 10:
        uv_half = 512
        uv_range = 1024
    else:
        uv_half = 128
        uv_range = 256

    ## at leat 7 times iterations make sure the error of the output angle is less than 1 degree
    iter_num = utl.clamp(iter_num, CORDIC_MIN_ITER_NUM, CORDIC_MAX_ITER_NUM)

    if (uv is not None) and len(uv) >= 2:
        u, v = uv[0], uv[1]
    else:
        u, v = np.indices((uv_range, uv_range))
    cb, cr = u - uv_half, v - uv_half

    increase_bits = utl.clamp(increase_bits, 0, 8)
    res = cordic_cbcr2hs(cb, cr, depth, iter_num, increase_bits, False)
    h = res[0]  # [-180, +180]
    s = res[1]  # [0, 181] << increase_bits
    # s = np.int32(res[1])
    # s = (s + 4 + (s >> 31)) >> 3

    hp = np.degrees(np.arctan2(cr, cb))  # [-180, +180]
    sp = np.sqrt(cb**2 + cr**2)  # [0, 181]
    hp = (hp + 0.5 * np.sign(hp)).astype(np.int32)
    sp = (sp + 0.5).astype(np.int32)

    dh = hp - h
    ds = sp - s

    if type(u) != np.ndarray:
        print(f"input  uv=({u}, {v}) => cb/cr=({cb}, {cr})")
        print(f"output hs=({h}, {s}) / hp/sp=({hp}, {sp})")
    else:
        h.astype(np.int16).tofile(f"out_h_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        s.astype(np.int16).tofile(f"out_s_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        hp.astype(np.int16).tofile(f"out_hp_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        sp.astype(np.int16).tofile(f"out_sp_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        # dh.astype(np.int8).tofile(f"diff_h_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        # ds.astype(np.int8).tofile(f"diff_s_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        print(f"Max absolute error: dh={np.max(np.abs(dh))}, ds={np.max(np.abs(ds))}")
    print(
        f"sum error for {depth}bit uv->hs: eh={np.abs(dh).sum()}, es={np.abs(ds).sum()} (iter={iter_num}, inc_bits={increase_bits})"
    )


def test_cordic_hs2cbcr(depth: int, iter_num: int, increase_bits: int, hs):
    assert depth in [8, 10]
    if depth == 10:
        uv_half = 512
        uv_range = 1024
        s_range = 725
    else:
        uv_half = 128
        uv_range = 256
        s_range = 182

    if (hs is not None) and len(hs) >= 2:
        h, s = hs[0], hs[1]
    else:
        h = np.full((361, s_range), np.arange(-180, 181).reshape(-1, 1))
        _, s = np.indices((361, s_range))

    increase_bits = utl.clamp(increase_bits, 0, 8)
    res = cordic_hs2cbcr(h, s, 8, depth, depth, iter_num, increase_bits)
    u = np.clip(res[0] + uv_half, 0, uv_range - 1)
    v = np.clip(res[1] + uv_half, 0, uv_range - 1)

    up = np.clip(s * np.cos(np.radians(h)) + uv_half, 0, uv_range - 1)
    vp = np.clip(s * np.sin(np.radians(h)) + uv_half, 0, uv_range - 1)
    up = (up + 0.5).astype(np.int32)
    vp = (vp + 0.5).astype(np.int32)

    du = up - u
    dv = vp - v

    if type(h) != np.ndarray:
        print(f"test {depth}bit hs({h}, {s}) -> uv({u}, {v}), target vaule: ({up}, {vp})")
    else:
        u.astype(np.uint16).tofile(f"out_u_{s_range}x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        v.astype(np.uint16).tofile(f"out_v_{s_range}x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        up.astype(np.uint16).tofile(f"out_up_{s_range}x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        vp.astype(np.uint16).tofile(f"out_vp_{s_range}x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        # du.astype(np.int8).tofile(f"diff_u_{s_range}x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        # dv.astype(np.int8).tofile(f"diff_v_{s_range}x361_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        print(f"Max absolute error: du={np.max(np.abs(du))}, dv={np.max(np.abs(dv))}")
    print(
        f"sum error for {depth}bit hs->uv: eu={abs(du).sum()}, ev={abs(dv).sum()} (iter={iter_num}, inc_bits={increase_bits})"
    )


def test_cordic_uv2hs2uv(depth: int, iter_num: int, increase_bits: int, uv):
    assert depth in [8, 10]
    if depth == 10:
        uv_half = 512
        uv_range = 1024
        s_range = 725
    else:
        uv_half = 128
        uv_range = 256
        s_range = 182

    if (uv is not None) and len(uv) >= 2:
        u, v = uv[0], uv[1]
    else:
        u, v = np.indices((uv_range, uv_range))
    cb, cr = u - uv_half, v - uv_half

    increase_bits = utl.clamp(increase_bits, 0, 8)
    res = cordic_cbcr2hs(cb, cr, depth, iter_num, increase_bits, True)
    h = res[0]
    s = res[1]
    depth_h = res[2]  # 8+8=16
    depth_s = res[3]  # depth + increase_bits
    assert depth_h == 8 + 8
    assert depth_s == depth + increase_bits

    res2 = cordic_hs2cbcr(h, s, depth_h, depth_s, depth, iter_num, max(CORDIC_XY_FIX_BITS - increase_bits, 0))
    uo = np.clip(res2[0] + uv_half, 0, uv_range - 1)
    vo = np.clip(res2[1] + uv_half, 0, uv_range - 1)

    du = uo - u
    dv = vo - v
    if type(h) != np.ndarray:
        print(f"cordic_uv2hs2uv: uv=({u}, {v}) => ({uo}, {vo}) (iter={iter_num}, inc_bits={increase_bits})")
    else:
        u.astype(np.uint16).tofile(f"in_u2u_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        v.astype(np.uint16).tofile(f"in_v2v_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        uo.astype(np.uint16).tofile(f"out_u2u_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        vo.astype(np.uint16).tofile(f"out_v2v_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        du.astype(np.int16).tofile(f"diff_u2u_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        dv.astype(np.int16).tofile(f"diff_v2v_{uv_range}x{uv_range}_iter{iter_num}_incbits{increase_bits}_yuv400.yuv")
        print(f"Max absolute error: du={np.max(np.abs(du))}, dv={np.max(np.abs(dv))}")
    print(
        f"sum error for {depth}bit uv->hs->uv: eu={np.abs(du).sum()}, ev={np.abs(dv).sum()} (iter={iter_num}, inc_bits={increase_bits})"
    )


if __name__ == '__main__':
    ## arg parser
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("-m", "--mode", default="", type=str, help="0-uv2hs, 1-hs2uv, 2-uv2uv")
    parser.add_argument("-d", "--depth", default=8, type=int, help="图像深度, 8/10, 默认: 8")
    parser.add_argument("-n", "--iter_num", default=13, type=int, help="Cordic迭代次数, 默认: 13")
    parser.add_argument("-b", "--increase_bits", default=3, type=int, help="Cordic S定点提示精度, 默认: 3")
    parser.add_argument("-p", "--pixel", type=int, nargs='+', help="传入一组UV/HS数值测试Cordic结果")
    args, _ = parser.parse_known_args()

    if args.mode in ["0", "uv2hs"]:
        print("Do test_cordic_cbcr2hs...")
        test_cordic_cbcr2hs(args.depth, args.iter_num, args.increase_bits, args.pixel if args.pixel else None)
    elif args.mode in ["1", "hs2uv"]:
        print("Do test_cordic_hs2cbcr...")
        test_cordic_hs2cbcr(args.depth, args.iter_num, args.increase_bits, args.pixel if args.pixel else None)
    elif args.mode in ["2", "uv2uv", "uv2hs2uv"]:
        print("Do test_cordic_uv2hs2uv...")
        test_cordic_uv2hs2uv(args.depth, args.iter_num, args.increase_bits, args.pixel if args.pixel else None)
    else:
        print(f"Error: unknown mode {args.mode}! Only support 0-uv2hs, 1-hs2uv, 2-uv2uv")
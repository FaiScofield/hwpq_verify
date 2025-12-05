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
CORDIC_XY_FIX_BITS = 8
## u14 max, 8bit fixed: angle [45, 26.565, 14.036, ..., 0.006994, 0.003497] * 256
CORDIC_ATAN_LUT_FIX8 = [11520, 6801, 3593, 1824, 916, 458, 229, 115, 57, 29, 14, 7, 4, 2, 1]
CORDIC_COEF_K_FIX10 = 622  # 10bit fixed: 0.607252935 * 1024, (from K4 to K15 are all the same)
CORDIC_MIN_ITER_NUM = 7
CORDIC_MAX_ITER_NUM = 15
CORDIC_DEG180_FIX8 = 180 << 8


def cordic_cbcr2hs(cb, cr, depth_uv: int, iter_num: int = 13, fix_bits_s: int = 0, keep_bits_s: int = 0):
    """
    depth_uv: 8 or 10
    input cb range: [-128, 127] in S8 / [-512, 511] in S10
    input cr range: [-128, 127] in S8 / [-512, 511] in S10
    output h range: [-180, 180] in S9, add more 8 bits fixed if keep_fix_bits_for_s>0
    output s range: [  0,  181] in U8 / [   0, 724] in U10, add more 'keep_fix_bits_for_s' fixed
    """
    assert depth_uv >= 8

    ## at leat 7 times iterations make sure the error of the output angle is less than 1 degree
    iter_num = utl.clamp(iter_num, CORDIC_MIN_ITER_NUM, CORDIC_MAX_ITER_NUM)

    ## the depth of x & y should be > iter_num, otherwise, the remain (depth - iter_num) iterations will be useless!
    fix_bits_h = 8
    fix_bits_s = utl.clamp(fix_bits_s, 0, 8)
    precision_s = fix_bits_s + depth_uv
    if precision_s < iter_num:
        print(
            f"Warning: fix_bits_for_s({fix_bits_s}) + depth_uv({depth_uv}) < iter_num({iter_num}), some iterations will be useless!"
        )

    ## swap to the 1st/4th coordinate quadrant
    x = abs(cb) << fix_bits_s
    y = cr << fix_bits_s
    z = 0  # might beyond the range ([0, 90]<<8) after iteration

    ## cordic iteration
    for i in range(iter_num):
        d = (y < 0) * 2 - 1  # +y => -1 -y => +1
        xp = x - d * (y >> i)
        yp = y + d * (x >> i)
        zp = z - d * CORDIC_ATAN_LUT_FIX8[i]
        x = xp
        y = yp
        z = zp

    ## x=s/K, K=0.607252935.
    s = CORDIC_COEF_K_FIX10 * x
    h = z

    '''
      return H value to four quadrants by input sign of UV
        | quadrant | x_y_in       | h_out   | s_out |
        | -------- | ------------ | ------- | ----- |
        |    1     | x0=+x, y0=y  | +z      | Kx    |
        |    2     | x0=-x, y0=y  | -z+pi   | Kx    |
        |    3     | x0=-x, y0=y  | -z-pi   | Kx    |
        |    4     | x0=+x, y0=y  | +z      | Kx    |
    '''
    cb_mask = cb >= 0
    cr_mask = cr >= 0
    cb_mask_H = 2 * cb_mask - 1  # +cb => 1, -cb => -1
    cr_mask_H = 2 * cr_mask - 1  # +cr => 1, -cr => -1
    cb_mask_pi = cb < 0  # +cb => 0, -cb => 1
    h = h * cb_mask_H + CORDIC_DEG180_FIX8 * cb_mask_pi * cr_mask_H

    if keep_bits_s > 0:
        keep_bits_s = min(keep_bits_s, fix_bits_s)
        shift_bits_s = 10 + fix_bits_s - keep_bits_s
        s = (s + (1 << shift_bits_s - 1)) >> shift_bits_s
        depth_h = 8 + fix_bits_h
        depth_s = depth_uv + keep_bits_s
    else:
        h = np.int32(h)
        h = (h + (1 << fix_bits_h - 1) + (h >> 31)) >> fix_bits_h
        shift_bits_s = 10 + fix_bits_s
        s = (s + (1 << shift_bits_s - 1)) >> shift_bits_s
        depth_h = 8
        depth_s = depth_uv

    ## set h to if s is 0
    if type(cb) == np.ndarray:
        h = np.where(s == 0, np.zeros_like(cb), h)
    else:
        h = 0 if s == 0 else h

    return h, s, depth_h, depth_s


def cordic_hs2cbcr(h, s, depth_h: int, depth_s: int, out_depth_s: int, iter_num: int = 13, fix_bits_s: int = 5):
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
    fix_bits_h = 8
    fix_bits_s = utl.clamp(fix_bits_s, 0, 8)
    precision_s = fix_bits_s + depth_s
    if precision_s < iter_num:
        print(
            f"Warning: fix_bits_for_s({fix_bits_s}) + depth_s({depth_s}) < iter_num({iter_num}), some iterations will be useless!"
        )

    ## change H to the first/fourth quadrant
    scale_h = 256 if depth_h == 16 else 1
    H_flag = ((h >= -90 * scale_h) & (h <= 90 * scale_h)) * 2 - 1  # 1: q1/q4; -1: q2/q3
    H_cordicPiFlag = np.int32(h > 90 * scale_h) - np.int32(h < -90 * scale_h)  # 0: q1/q4; 1: q2; -1: q3
    h0 = H_cordicPiFlag * 180 * scale_h + H_flag * h

    x = s << fix_bits_s
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

    shift_bits_s = 10 + precision_s - out_depth_s
    cb = (CORDIC_COEF_K_FIX10 * x + (1 << shift_bits_s - 1)) >> shift_bits_s
    cr = (CORDIC_COEF_K_FIX10 * y + (1 << shift_bits_s - 1)) >> shift_bits_s

    ## get the sign of U by the H value
    cb = cb * H_flag

    return cb, cr


def cordic_cbcr2hs_acm(cb, cr, depth_uv: int, iter_num: int = 13, b_fixed_out: bool = True):
    """
    depth_uv: 8 or 10
    input cb range: [-128, 127] in S8 / [-512, 511] in S10
    input cr range: [-128, 127] in S8 / [-512, 511] in S10
    output h range: [-180, 180] in S9, add more 8 bits fixed if not b_fixed_out
    output s range: [  0,  181] in U8 / [   0, 724] in U10, add more 'fix_bits_s' fixed if not b_fixed_out
    """
    assert depth_uv >= 8

    ## at leat 7 times iterations make sure the error of the output angle is less than 1 degree
    iter_num = utl.clamp(iter_num, CORDIC_MIN_ITER_NUM, CORDIC_MAX_ITER_NUM)

    fix_bits_h = 8
    fix_bits_s = 8

    ## swap to the first coordinate quadrant
    x = abs(cb) << CORDIC_XY_FIX_BITS
    y = abs(cr) << CORDIC_XY_FIX_BITS
    z = 0  # [0, 90] << 8

    ## cordic iteration
    for i in range(iter_num):
        d = (y < 0) * 2 - 1  # +y => -1 -y => +1
        xp = x - d * (y >> i)
        yp = y + d * (x >> i)
        zp = z - d * CORDIC_ATAN_LUT_FIX8[i]
        x = xp
        y = yp
        z = zp

    ## x=s/K, K=0.607252935. U8/U10=>U8.8/U10.8=>U8.3/U10.3
    s = (CORDIC_COEF_K_FIX10 * x + (1 << 14)) >> 15

    ## z might be a little negative after cordic iteration
    if type(cb) == np.ndarray:
        h = np.where(s == 0, np.zeros_like(cb), np.maximum(z, 0))
    else:
        h = 0 if s == 0 else np.maximum(z, 0)

    '''
      return H value to four quadrants by input sign of UV
        | quadrant | x_y_in       | h_out   | s_out |
        | -------- | ------------ | ------- | ----- |
        |    1     | x0=+x, y0=+y | +z      | Kx    |
        |    2     | x0=-x, y0=+y | -(z-pi) | Kx    |
        |    3     | x0=-x, y0=-y | +(z-pi) | Kx    |
        |    4     | x0=+x, y0=-y | -z      | Kx    |
    '''
    cb_mask = cb > 0  # WARNING: error when cb==0 & cr==0!  the condition should be 'cb >= 0'
    cr_mask = cr > 0  # WARNING: error when cr==0!  the condition should be 'cr >= 0'
    cb_mask_pi = cb < 0  # +cb => 0, -cb => 1
    cb_mask_H = 2 * cb_mask - 1  # +cb => 1, -cb => -1
    cr_mask_H = 2 * cr_mask - 1  # +cr => 1, -cr => -1
    h = (CORDIC_DEG180_FIX8 * cb_mask_pi + h * cb_mask_H) * cr_mask_H

    if b_fixed_out:
        depth_h = 8 + fix_bits_h
        depth_s = depth_uv + 3
    else:
        h = np.int32(h)
        h = (h + (1 << fix_bits_h - 1) + (h >> 31)) >> fix_bits_h # restore to S9
        s = (s + (1 << 2)) >> 3  # restore to U8/U10
        depth_h = 8
        depth_s = depth_uv

    return h, s, depth_h, depth_s


def cordic_hs2cbcr_acm(h, s, depth_h: int, depth_s: int, out_depth_s: int, iter_num: int = 13):
    fix_bits_s = CORDIC_XY_FIX_BITS - (depth_s - out_depth_s)
    return cordic_hs2cbcr(h, s, depth_h, depth_s, out_depth_s, iter_num, fix_bits_s)


def test_cordic_cbcr2hs(depth: int, iter_num: int, fix_bits_s: int, keep_bits_s: int, b_use_acm_impl: bool, uv):
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

    fix_bits_s = utl.clamp(fix_bits_s, 0, 8)
    if b_use_acm_impl:
        hs_depth = cordic_cbcr2hs_acm(cb, cr, depth, iter_num, keep_bits_s > 0)
    else:
        hs_depth = cordic_cbcr2hs(cb, cr, depth, iter_num, fix_bits_s, keep_bits_s)
    h = hs_depth[0]  # [-180, +180]
    s = hs_depth[1]  # [0, 181] << keep_bits
    keep_bits_h = hs_depth[2] - 8  # 8 or 0
    keep_bits_s = hs_depth[3] - depth  # 3 or 0

    hp = np.degrees(np.arctan2(cr, cb))  # [-180, +180]
    sp = np.sqrt(cb**2 + cr**2)  # [0, 181]
    hp = (hp + 0.5 * np.sign(hp)).astype(np.int32)
    sp = (sp + 0.5).astype(np.int32)

    if keep_bits_s > 0:
        hd = np.abs(hp - (h + (1 << keep_bits_h - 1) + (h >> 31) >> keep_bits_h))
        sd = np.abs(sp - (s + (1 << keep_bits_s - 1) >> keep_bits_s))
    else:
        hd = np.abs(hp - h)
        sd = np.abs(sp - s)

    if type(u) != np.ndarray:
        if keep_bits_s > 0:
            h = (h + (1 << keep_bits_h - 1) + (h >> 31) >> keep_bits_h)
            s = (s + (1 << keep_bits_s - 1) >> keep_bits_s)
        print(
            f"cordic_cbcr2hs: {depth}bit uv=({u}, {v}) => cb/cr=({cb}, {cr}) => hs({h}, {s}), target vaule: ({hp}, {sp})"
        )
    else:
        h.astype(np.int16).tofile(f"cbcr2hs_ho_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_h}_yuv400.yuv")
        s.astype(np.int16).tofile(f"cbcr2hs_so_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        hp.astype(np.int16).tofile(f"cbcr2hs_hp_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_h}_yuv400.yuv")
        sp.astype(np.int16).tofile(f"cbcr2hs_sp_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        hd.astype(np.uint8).tofile(f"cbcr2hs_hd_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_h}_yuv400.yuv")
        sd.astype(np.uint8).tofile(f"cbcr2hs_sd_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        print(f"Max absolute error: hd={np.max(hd)}, sd={np.max(sd)}")
    print(f"sum error for {depth}bit uv->hs: he={hd.sum()}, se={sd.sum()}")
    print(f"final configs: iter_num={iter_num}, fix_bits={fix_bits_s}, inc_bits={keep_bits_s}")


def test_cordic_hs2cbcr(depth: int, iter_num: int, fix_bits_s: int, keep_bits_s: int, b_use_acm_impl: bool, hs):
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

    fix_bits_s = utl.clamp(fix_bits_s, 0, 8)
    if b_use_acm_impl:
        cbcr = cordic_hs2cbcr_acm(h, s, 8, depth, depth + keep_bits_s, iter_num)
        fix_bits_s = CORDIC_XY_FIX_BITS - keep_bits_s
    else:
        cbcr = cordic_hs2cbcr(h, s, 8, depth, depth, iter_num, fix_bits_s)
    cb = cbcr[0]
    cr = cbcr[1]

    up = np.clip(s * np.cos(np.radians(h)) + uv_half, 0, uv_range - 1)
    vp = np.clip(s * np.sin(np.radians(h)) + uv_half, 0, uv_range - 1)
    up = (up + 0.5).astype(np.int32)
    vp = (vp + 0.5).astype(np.int32)

    if keep_bits_s > 0:
        cb = (cb + (1 << keep_bits_s - 1) + (cb >> 31)) >> keep_bits_s
        cr = (cr + (1 << keep_bits_s - 1) + (cr >> 31)) >> keep_bits_s
    u = np.clip(cb + uv_half, 0, uv_range - 1)
    v = np.clip(cr + uv_half, 0, uv_range - 1)
    ud = np.abs(up - u)
    vd = np.abs(vp - v)

    if type(h) != np.ndarray:
        if keep_bits_s > 0:
            u = (u + (1 << keep_bits_s - 1) >> keep_bits_s)
            v = (v + (1 << keep_bits_s - 1) >> keep_bits_s)
        print(
            f"cordic_hs2cbcr: {depth}bit hs({h}, {s}) => cb/cr=({cbcr[0]}, {cbcr[1]}) => uv({u}, {v}), target vaule: ({up}, {vp})"
        )
    else:
        u.astype(np.uint16).tofile(f"hs2cbcr_uo_{s_range}x361_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        v.astype(np.uint16).tofile(f"hs2cbcr_vo_{s_range}x361_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        up.astype(np.uint16).tofile(f"hs2cbcr_up_{s_range}x361_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        vp.astype(np.uint16).tofile(f"hs2cbcr_vp_{s_range}x361_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        ud.astype(np.uint8).tofile(f"hs2cbcr_ud_{s_range}x361_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        vd.astype(np.uint8).tofile(f"hs2cbcr_vd_{s_range}x361_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        print(f"Max absolute error: ud={np.max(ud)}, vd={np.max(vd)}")
    print(f"sum error for {depth}bit hs->uv: ue={ud.sum()}, ve={vd.sum()}")
    print(f"final configs: iter_num={iter_num}, fix_bits={fix_bits_s}, inc_bits={keep_bits_s}")


def test_cordic_uv2hs2uv(depth: int, iter_num: int, fix_bits_s: int, keep_bits_s: int, b_use_acm_impl: bool, uv):
    assert depth in [8, 10]
    assert keep_bits_s >= 0 and keep_bits_s <= fix_bits_s
    if depth == 10:
        uv_half = 512
        uv_range = 1024
        s_range = 725
    else:
        uv_half = 128
        uv_range = 256
        s_range = 182

    ## at leat 7 times iterations make sure the error of the output angle is less than 1 degree
    iter_num = utl.clamp(iter_num, CORDIC_MIN_ITER_NUM, CORDIC_MAX_ITER_NUM)

    if (uv is not None) and len(uv) >= 2:
        u, v = uv[0], uv[1]
    else:
        u, v = np.indices((uv_range, uv_range))
    cb, cr = u - uv_half, v - uv_half

    fix_bits_s = utl.clamp(fix_bits_s, 0, 8)
    if b_use_acm_impl:
        hs_depth = cordic_cbcr2hs_acm(cb, cr, depth, iter_num, keep_bits_s > 0)
        fix_bits_s = 8
        keep_bits_s = hs_depth[3] - depth
    else:
        hs_depth = cordic_cbcr2hs(cb, cr, depth, iter_num, fix_bits_s, keep_bits_s)
    h = hs_depth[0]
    s = hs_depth[1]
    depth_h = hs_depth[2]  # 8+8=16
    depth_s = hs_depth[3]  # depth + increase_bits
    assert depth_h == 16 if keep_bits_s > 0 else 8
    assert depth_s == depth + keep_bits_s

    if b_use_acm_impl:
        cbcr = cordic_hs2cbcr_acm(h, s, depth_h, depth_s, depth, iter_num)
    else:
        cbcr = cordic_hs2cbcr(h, s, depth_h, depth_s, depth, iter_num, max(fix_bits_s - keep_bits_s, 0))
    uo = np.clip(cbcr[0] + uv_half, 0, uv_range - 1)
    vo = np.clip(cbcr[1] + uv_half, 0, uv_range - 1)

    ud = np.abs(uo - u)
    vd = np.abs(vo - v)
    if type(h) != np.ndarray:
        print(f"cordic_uv2hs2uv: {depth}bit uv({u}, {v}) => ({uo}, {vo})")
    else:
        uo.astype(np.uint16).tofile(f"uv2uv_uo_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        vo.astype(np.uint16).tofile(f"uv2uv_vo_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        u.astype(np.uint16).tofile(f"uv2uv_up_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        v.astype(np.uint16).tofile(f"uv2uv_vp_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        ud.astype(np.uint8).tofile(f"uv2uv_ud_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        vd.astype(np.uint8).tofile(f"uv2uv_vd_{uv_range}x{uv_range}_iter{iter_num}_incbits{keep_bits_s}_yuv400.yuv")
        print(f"Max absolute error: ud={np.max(ud)}, vd={np.max(vd)}")
    print(f"sum error for {depth}bit uv->hs->uv: eu={np.abs(ud).sum()}, ev={np.abs(vd).sum()}")
    print(f"final configs: iter_num={iter_num}, fix_bits={fix_bits_s}, inc_bits={keep_bits_s}")


if __name__ == '__main__':
    ## arg parser
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("-m", "--mode", default="", type=str, help="0-uv2hs, 1-hs2uv, 2-uv2uv")
    parser.add_argument("-a", "--acm", action='store_true', help="use pq_acm_impl (-n13 -f8 -k3)")
    parser.add_argument("-d", "--depth", default=8, type=int, help="图像深度, 8/10, 默认: 8")
    parser.add_argument("-n", "--iter_num", default=13, type=int, help="Cordic迭代次数, 默认: 13")
    parser.add_argument("-f", "--fix_bits", default=8, type=int, help="Cordic S定点提升精度, 默认: 8")
    parser.add_argument("-k", "--keep_bits", default=3, type=int, help="Cordic S定点保留精度, 默认: 3")
    parser.add_argument("-p", "--pixel", type=int, nargs='+', help="传入一组UV/HS数值p测试Cordic结果")
    args, _ = parser.parse_known_args()

    pixel = args.pixel if args.pixel else None

    if args.mode in ["0", "uv2hs"]:
        print("Do test_cordic_cbcr2hs...")
        test_cordic_cbcr2hs(args.depth, args.iter_num, args.fix_bits, args.keep_bits, args.acm, pixel)
    elif args.mode in ["1", "hs2uv"]:
        print("Do test_cordic_hs2cbcr...")
        test_cordic_hs2cbcr(args.depth, args.iter_num, args.fix_bits, args.keep_bits, args.acm, pixel)
    elif args.mode in ["2", "uv2uv", "uv2hs2uv"]:
        print("Do test_cordic_uv2hs2uv...")
        test_cordic_uv2hs2uv(args.depth, args.iter_num, args.fix_bits, args.keep_bits, args.acm, pixel)
    else:
        print(f"Error: unknown mode {args.mode}! Only support 0-uv2hs, 1-hs2uv, 2-uv2uv")

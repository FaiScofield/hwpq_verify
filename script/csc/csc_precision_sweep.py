# -*- coding: utf-8 -*-
"""
扫描: 为了让 8bit / 10bit limited YUV 经过 L2F -> F2L 往返完全无差异,
系数定点精度至少要多少 bit。

数据通路:
    out = clip((mat@pix + offset + 2^(p-1)) >> p, 0, 2^depth-1)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "script", "csc"))
from get_csc_coefs import (  # noqa: E402
    CscCoefConfig,
    get_csc_coefs,
    g_supported_standard_convert_modes,
)


def get_fix(mode_key, depth, prec):
    cfg = CscCoefConfig()
    cfg.pixel_depth = depth
    cfg.coef_precision = prec
    cfg.platform = "rk3572"
    cfg.csc_mode = g_supported_standard_convert_modes[mode_key]
    mat, ofs = get_csc_coefs(cfg, None)
    return mat.astype(np.int64), ofs.astype(np.int64)


def stage(pix, mat, ofs, depth, prec):
    t = pix @ mat.T + ofs + (1 << (prec - 1))
    return np.clip(t >> prec, 0, (1 << depth) - 1)


def sweep(depth, prec_list=range(8, 17)):
    maxv = (1 << depth) - 1
    y_lo, y_hi = 16 << (depth - 8), 235 << (depth - 8)
    c_lo, c_hi = 16 << (depth - 8), 240 << (depth - 8)
    y_ratio = (235 - 16) * (1 << (depth - 8)) / maxv
    uv_ratio = (240 - 16) * (1 << (depth - 8)) / maxv

    print("=" * 108)
    print(f"depth={depth}bit  (limited Y {y_lo}..{y_hi}, C {c_lo}..{c_hi})")
    print(f"{'p':>3} | {'c_l2f_Y':>8} {'c_f2l_Y':>8} | {'乘积/2^2p':>12} {'相对误差':>10} {'满幅漂移':>9} "
          f"| {'Y 差异':>12} {'C 差异':>12} | {'max|e|':>6}")
    print("-" * 108)
    first_exact = {}
    for p in prec_list:
        m1, o1 = get_fix("709l_to_709f", depth, p)
        m2, o2 = get_fix("709f_to_709l", depth, p)
        prod = (m1.diagonal() * m2.diagonal()) / 2.0 ** (2 * p)
        drift = prod[0] * (y_hi - y_lo) - (y_hi - y_lo)

        nd, mx = {}, 0
        for name, lo, hi, ch in (("Y", y_lo, y_hi, 0), ("C", c_lo, c_hi, 1)):
            v = np.arange(lo, hi + 1, dtype=np.int64).reshape(-1, 1)
            pix = np.repeat(v, 3, axis=1)
            out = stage(stage(pix, m1, o1, depth, p), m2, o2, depth, p)
            d = out[:, ch] - v[:, 0]
            nd[name] = (int(np.count_nonzero(d)), len(v))
            mx = max(mx, int(np.abs(d).max()))
        ok = nd["Y"][0] == 0 and nd["C"][0] == 0
        if ok and "p" not in first_exact:
            first_exact["p"] = p
        print(f"{p:>3} | {m1[0, 0]:>8} {m2[0, 0]:>8} | {prod[0]:>12.9f} {prod[0] - 1:>+10.2e} {drift:>+9.3f} "
              f"| {nd['Y'][0]:>5}/{nd['Y'][1]:<6} {nd['C'][0]:>5}/{nd['C'][1]:<6} | {mx:>6}")
        _ = (y_ratio, uv_ratio)
    print(f"-> 首个完全无差异的精度: {first_exact.get('p', '未出现(<=16)')}")
    return first_exact.get("p", None)


def theory(depth, prec):
    """解析判据: 系统漂移 + 第一次取整传递误差 < 0.5"""
    maxv = (1 << depth) - 1
    y_ratio = (235 - 16) * (1 << (depth - 8)) / maxv
    span = 219 * (1 << (depth - 8))
    m1, _ = get_fix("709l_to_709f", depth, prec)
    m2, _ = get_fix("709f_to_709l", depth, prec)
    prod = (m1[0, 0] * m2[0, 0]) / 2.0 ** (2 * prec)
    e1 = 0.5 * m2[0, 0] / 2 ** prec
    bound = abs(prod - 1) * span + e1
    print(f"  depth={depth}, p={prec}: |Δgain|*span = {abs(prod - 1) * span:.3f} LSB, "
          f"二次取整传递上界 {e1:.3f} LSB, 合计 {bound:.3f} (判据 < 0.5)")
    return bound


def rk3576_style(depth, prec_list=range(10, 17)):
    """RK3576 风格: offset 寄存器为像素单位(先右移), 再 out=(pix@mat+2^(p-1))>>p + ofs"""
    y_lo, y_hi = 16 << (depth - 8), 235 << (depth - 8)
    c_lo, c_hi = 16 << (depth - 8), 240 << (depth - 8)
    print("\n" + "=" * 108)
    print(f"[RK3576 风格 offset] depth={depth}")

    def st(pix, mat, ofs, p):
        ofs_pix = (ofs + (1 << (p - 1)) + (ofs >> 31)) >> p
        return np.clip(((pix @ mat.T + (1 << (p - 1))) >> p) + ofs_pix, 0, (1 << depth) - 1)

    for p in prec_list:
        m1, o1 = get_fix("709l_to_709f", depth, p)
        m2, o2 = get_fix("709f_to_709l", depth, p)
        out_s = []
        for name, lo, hi, ch in (("Y", y_lo, y_hi, 0), ("C", c_lo, c_hi, 1)):
            v = np.arange(lo, hi + 1, dtype=np.int64).reshape(-1, 1)
            pix = np.repeat(v, 3, axis=1)
            d = st(st(pix, m1, o1, p), m2, o2, p)[:, ch] - v[:, 0]
            out_s.append(f"{name}:{np.count_nonzero(d)}/{len(v)}(max{int(np.abs(d).max())})")
        print(f"  p={p:>2}  " + "  ".join(out_s) + f"   (offset 像素值 L2F={o1[0] / 2**p:.3f} F2L={o2[0] / 2**p:.3f})")


def tuned_pair(depth, prec, span=16):
    """在理想系数附近搜索使乘积最接近 2^2p 的系数对, 检验往返是否 0 差异"""
    maxv = (1 << depth) - 1
    y_ratio = (235 - 16) * (1 << (depth - 8)) / maxv
    y_lo, y_hi = 16 << (depth - 8), 235 << (depth - 8)
    ideal_c1 = 2 ** prec / y_ratio
    ideal_c2 = 2 ** prec * y_ratio
    best = None
    for c1 in range(int(ideal_c1) - span, int(ideal_c1) + span + 1):
        c2 = int(round(2 ** (2 * prec) / c1))
        err = abs(c1 * c2 - 2 ** (2 * prec))
        if best is None or err < best[0]:
            best = (err, c1, c2)
    err, c1, c2 = best
    # 单级最大偏差(相对理想浮点 L2F)
    v = np.arange(y_lo, y_hi + 1, dtype=np.int64)
    a = (c1 * (v - y_lo) + (1 << (prec - 1))) >> prec
    ideal_a = (v - y_lo) / y_ratio
    l2f_dev = float(np.abs(a - ideal_a).max())
    b = (c2 * a + y_lo * 2 ** prec + (1 << (prec - 1))) >> prec
    d = b - v
    print(f"  depth={depth} p={prec}: 最优系数对 c1={c1}, c2={c2}, |c1*c2-2^2p|={err} "
          f"(独立取整为 c1={round(ideal_c1)}, c2={round(ideal_c2)})")
    print(f"    往返不一致 {np.count_nonzero(d)}/{len(v)}, max|e|={int(np.abs(d).max())}; "
          f"但单级 L2F 与理想值最大偏差 = {l2f_dev:.3f} LSB")


if __name__ == "__main__":
    r8 = sweep(8)
    print()
    r10 = sweep(10)
    print("\n##### 解析上界检查(保证对所有码值都无差异的条件) #####")
    for d in (8, 10):
        for p in range(8, 17):
            theory(d, p)
    rk3576_style(8)
    rk3576_style(10)
    print("\n##### 对照: 10bit 精度下通过系数对调优实现 0 往返差异 #####")
    tuned_pair(8, 10)
    tuned_pair(10, 10)
    tuned_pair(10, 11)
    print(f"\n结果: 8bit 需 >= {r8}bit, 10bit 需 >= {r10}bit")

# -*- coding: utf-8 -*-
"""
分析: 8bit/10bit limited YUV 数据源, 用 10bit 定点系数先做 L2F 再做 F2L 的往返误差。

数据通路与 script/csc/csc_bitwidth_analysis.py 中的模型一致:
    fix_mat = round(float_mat * 2^precision)
    offset  = 2^precision * range_ofs_o + fix_mat @ range_ofs_i
    T       = fix_mat @ pix + offset + 2^(precision-1)
    out     = clip(T >> precision, 0, 2^depth - 1)

注意 L2F/F2L 是两个独立 CSC 级, 每级各自把系数定点化到 10bit。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "script", "csc"))
from get_csc_coefs import (  # noqa: E402
    CscCoefConfig,
    CscBcshConfig,
    get_csc_coefs,
    g_supported_standard_convert_modes,
)

PREC = 10  # 10bit 定点系数


def get_fix(mode_key, depth, bcsh=None):
    cfg = CscCoefConfig()
    cfg.pixel_depth = depth
    cfg.coef_precision = PREC
    cfg.platform = "rk3572"
    cfg.csc_mode = g_supported_standard_convert_modes[mode_key]
    mat, ofs = get_csc_coefs(cfg, bcsh)
    return mat.astype(np.int64), ofs.astype(np.int64)


def stage(pix, mat, ofs, depth, prec=PREC, rounding=True):
    """pix: (N,3) int64 -> (N,3) int64; rounding=False 时为截断取整"""
    t = pix @ mat.T + ofs + ((1 << (prec - 1)) if rounding else 0)
    out = t >> prec
    return np.clip(out, 0, (1 << depth) - 1)


def analyze_depth(depth, bcsh=None, tag=""):
    m_l2f, o_l2f = get_fix("709l_to_709f", depth, bcsh)
    m_f2l, o_f2l = get_fix("709f_to_709l", depth, bcsh)
    maxv = (1 << depth) - 1
    y_lo, y_hi = 16 << (depth - 8), 235 << (depth - 8)
    c_lo, c_hi = 16 << (depth - 8), 240 << (depth - 8)

    print("=" * 86)
    print(f"[{tag}] depth={depth}bit, coef precision={PREC}bit, maxv={maxv}")
    print("  L2F(709l_to_709f) mat diag =", m_l2f.diagonal(), " offset =", o_l2f)
    print("  F2L(709f_to_709l) mat diag =", m_f2l.diagonal(), " offset =", o_f2l)
    diag_l2f = np.diag(m_l2f.diagonal())
    diag_f2l = np.diag(m_f2l.diagonal())
    print("  off-diagonal all zero:", bool(np.array_equal(m_l2f, diag_l2f) and np.array_equal(m_f2l, diag_f2l)))

    # 单级缩放比例 (定点值 / 2^PREC) 与理想值比较
    y_ratio = (235 - 16) * (1 << (depth - 8)) / maxv
    uv_ratio = (240 - 16) * (1 << (depth - 8)) / maxv
    ideal = [1.0 / y_ratio, 1.0 / uv_ratio, 1.0 / uv_ratio]
    print(f"  理想 L2F 增益  = {ideal[0]:.9f} (Y), {ideal[1]:.9f} (C)")
    print(f"  定点 L2F 增益  = {m_l2f[0,0] / 2**PREC:.9f} (Y), {m_l2f[1,1] / 2**PREC:.9f} (C)")
    print(f"  理想 F2L 增益  = {y_ratio:.9f} (Y), {uv_ratio:.9f} (C)")
    print(f"  定点 F2L 增益  = {m_f2l[0,0] / 2**PREC:.9f} (Y), {m_f2l[1,1] / 2**PREC:.9f} (C)")
    prod = (m_l2f.diagonal() * m_f2l.diagonal()) / 2.0 ** (2 * PREC)
    print(f"  往返总增益(Y)  = {prod[0]:.9f}  -> 满量程偏差 {prod[0] * maxv - maxv:+.3f} LSB")

    # 逐通道扫描所有合法码值
    def scan(rounding):
        res = {}
        for name, lo, hi, ch in (("Y", y_lo, y_hi, 0), ("U/V", c_lo, c_hi, 1)):
            v = np.arange(lo, hi + 1, dtype=np.int64)
            pix = np.repeat(v.reshape(-1, 1), 3, axis=1)
            a = stage(pix, m_l2f, o_l2f, depth, rounding=rounding)
            b = stage(a, m_f2l, o_f2l, depth, rounding=rounding)
            d = b[:, ch] - v
            res[name] = dict(v=v, d=d, nz=int(np.count_nonzero(d)), n=len(v),
                             mx=int(np.abs(d).max()), mean=float(d.mean()))
        return res

    def show(res, label):
        p_y = res["Y"]["nz"] / res["Y"]["n"]
        p_c = res["U/V"]["nz"] / res["U/V"]["n"]
        p_pix = 1 - (1 - p_y) * (1 - p_c) ** 2
        print(f"  -- {label} --")
        for name in ("Y", "U/V"):
            r = res[name]
            hist = {int(k): int(np.sum(r["d"] == k)) for k in np.unique(r["d"])}
            bad = r["v"][r["d"] != 0]
            extra = f"  差异码值 {bad[:10].tolist()}{'...' if len(bad) > 10 else ''}" if len(bad) else ""
            print(f"    {name:>3}: 不一致 {r['nz']:>4}/{r['n']:<4} = {100.0 * r['nz'] / r['n']:6.2f}%"
                  f" | max|e|={r['mx']} | mean e={r['mean']:+.4f} | 直方图 {hist}{extra}")
        print(f"    任一通道不一致的像素比例(码值均匀分布) = {100.0 * p_pix:.2f}%")
        return p_pix

    show(scan(True), "四舍五入 round-half-up (代码默认模型)")
    show(scan(False), "截断取整 floor (最坏情况)")
    return m_l2f, o_l2f, m_f2l, o_f2l


def real_image_test(depth=8):
    """用真实图像(转成 limited 后)统计像素差异比例"""
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "input_1920x1080_yuv444p_601F_5frames.yuv")
    if not os.path.exists(src):
        print(f"\n(跳过真实图像测试: 未找到 {src})")
        return
    w, h = 1920, 1080
    fsize = w * h * 3
    with open(src, "rb") as fp:
        raw = fp.read(fsize)
    if len(raw) < fsize:
        print("\n(跳过真实图像测试: 文件尺寸不足)")
        return
    img = np.frombuffer(raw, dtype=np.uint8).reshape(3, h, w).astype(np.float64)
    maxv = (1 << depth) - 1
    gain = 1 << (depth - 8)
    # 8bit full -> depth-bit full -> depth-bit limited, 得到"真实内容的 limited 源"
    full = img * maxv / 255.0 if depth != 8 else img.copy()
    y = np.clip(np.round(full[0] * (219 * gain) / maxv + 16 * gain), 16 * gain, 235 * gain)
    u = np.clip(np.round((full[1] - maxv / 2.0) * (224 * gain) / maxv + 128 * gain), 16 * gain, 240 * gain)
    v = np.clip(np.round((full[2] - maxv / 2.0) * (224 * gain) / maxv + 128 * gain), 16 * gain, 240 * gain)
    src_pix = np.stack([y.ravel(), u.ravel(), v.ravel()], axis=1).astype(np.int64)

    m_l2f, o_l2f = get_fix("709l_to_709f", depth)
    m_f2l, o_f2l = get_fix("709f_to_709l", depth)
    out = stage(stage(src_pix, m_l2f, o_l2f, depth), m_f2l, o_f2l, depth)
    diff = out - src_pix
    any_diff = np.any(diff != 0, axis=1)
    per_ch = np.count_nonzero(diff != 0, axis=0)
    n = len(src_pix)
    print("\n" + "=" * 86)
    print(f"[真实图像 1920x1080 yuv444p -> limited {depth}bit] 像素数 {n}")
    print(f"  Y/U/V 单独不一致比例: {100.0 * per_ch[0] / n:.2f}% / {100.0 * per_ch[1] / n:.2f}% / {100.0 * per_ch[2] / n:.2f}%")
    print(f"  任一通道不一致的像素: {int(np.count_nonzero(any_diff))}/{n} = {100.0 * np.count_nonzero(any_diff) / n:.2f}%")
    print(f"  最大绝对偏差: Y={int(np.abs(diff[:, 0]).max())}, U={int(np.abs(diff[:, 1]).max())}, V={int(np.abs(diff[:, 2]).max())}")
    print(f"  平均绝对偏差: Y={np.abs(diff[:, 0]).mean():.4f}, U={np.abs(diff[:, 1]).mean():.4f}, V={np.abs(diff[:, 2]).mean():.4f}")
    hd = {int(k): int(np.sum(diff[:, 0] == k)) for k in np.unique(diff[:, 0])}
    print(f"  Y 通道偏差直方图 {hd}")


def fused_check(depth):
    """对照: L2F+F2L 若融合成单级(CSC 直通), 结果是否精确
    out = (Mf*(Ml*x+ol)/2^p + of) >> p
    """
    m_l2f, o_l2f = get_fix("709l_to_709f", depth)
    m_f2l, o_f2l = get_fix("709f_to_709l", depth)
    p = PREC
    j = np.rint(m_f2l.astype(np.float64) @ m_l2f.astype(np.float64) / 2 ** p).astype(np.int64)
    o = np.rint(m_f2l.astype(np.float64) @ o_l2f / 2 ** p + o_f2l).astype(np.int64)
    print(f"  [fused depth={depth}] 融合矩阵 diag = {j.diagonal()}, offset = {o}")
    y_lo, y_hi = 16 << (depth - 8), 235 << (depth - 8)
    c_lo, c_hi = 16 << (depth - 8), 240 << (depth - 8)
    for name, lo, hi, ch in (("Y", y_lo, y_hi, 0), ("C", c_lo, c_hi, 1)):
        v = np.arange(lo, hi + 1, dtype=np.int64).reshape(-1, 1)
        pix = np.repeat(v, 3, axis=1)
        out = stage(pix, j, o, depth)
        d = out[:, ch] - v[:, 0]
        print(f"    {name}: 不一致 {np.count_nonzero(d)}/{len(v)}, max|e|={int(np.abs(d).max())}")


def stage_3576(pix, mat, ofs, depth, prec=PREC):
    """RK3576 风格: offset 先右移成像素单位, 先移位再加 offset"""
    ofs_pix = (ofs + (1 << (prec - 1)) + (ofs >> 31)) >> prec
    t = pix @ mat.T + (1 << (prec - 1))
    out = (t >> prec) + ofs_pix
    return np.clip(out, 0, (1 << depth) - 1)


def variant_3576(depth):
    m_l2f, o_l2f = get_fix("709l_to_709f", depth)
    m_f2l, o_f2l = get_fix("709f_to_709l", depth)
    y_lo, y_hi = 16 << (depth - 8), 235 << (depth - 8)
    c_lo, c_hi = 16 << (depth - 8), 240 << (depth - 8)
    print(f"  [RK3576 风格 depth={depth}]")
    for name, lo, hi, ch in (("Y", y_lo, y_hi, 0), ("U/V", c_lo, c_hi, 1)):
        v = np.arange(lo, hi + 1, dtype=np.int64)
        pix = np.repeat(v.reshape(-1, 1), 3, axis=1)
        out = stage_3576(stage_3576(pix, m_l2f, o_l2f, depth), m_f2l, o_f2l, depth)
        d = out[:, ch] - v
        hist = {int(k): int(np.sum(d == k)) for k in np.unique(d)}
        print(f"    {name:>3}: 不一致 {np.count_nonzero(d)}/{len(v)} = {100.0 * np.count_nonzero(d) / len(v):.2f}%, "
              f"max|e|={int(np.abs(d).max())}, 直方图 {hist}")


def bit8_in_10bit_path():
    """变体: 8bit limited 源 <<2 进 10bit 通路(10bit 系数), 再四舍五入回 8bit"""
    m_l2f, o_l2f = get_fix("709l_to_709f", 10)
    m_f2l, o_f2l = get_fix("709f_to_709l", 10)
    print("\n" + "=" * 86)
    print("[变体: 8bit 数据 <<2 进 10bit 通路, 出 10bit 再 (v+2)>>2 回 8bit]")
    for name, v8, ch in (("Y", np.arange(16, 236), 0), ("U/V", np.arange(16, 241), 1)):
        v10 = v8 << 2
        pix = np.repeat(v10.reshape(-1, 1), 3, axis=1)
        out10 = stage(stage(pix, m_l2f, o_l2f, 10), m_f2l, o_f2l, 10)
        out8 = (out10[:, ch] + 2) >> 2
        d = out8 - v8
        hist = {int(k): int(np.sum(d == k)) for k in np.unique(d)}
        print(f"  {name:>3}: 10bit 域不一致 {np.count_nonzero(out10[:, ch] - v10):>3}/{len(v8)}, "
              f"回 8bit 后 {np.count_nonzero(d):>3}/{len(v8)} = {100.0 * np.count_nonzero(d) / len(v8):.2f}%"
              f", max|e|={int(np.abs(d).max())}, 直方图 {hist}")


if __name__ == "__main__":
    print("##### 场景1: 8bit limited YUV 源, 10bit 定点系数 #####")
    analyze_depth(8, tag="8bit")
    print("\n##### 场景2: 10bit limited YUV 源, 10bit 定点系数 #####")
    analyze_depth(10, tag="10bit")
    print("\n##### 附加: 默认 BCSH(全 256) 下是否变化 #####")
    analyze_depth(10, bcsh=CscBcshConfig(), tag="10bit+BCSH默认")
    real_image_test(8)
    real_image_test(10)
    print("\n" + "=" * 86)
    print("##### 附加: RK3576 风格的 offset 处理(先移位, 再加像素域 offset) #####")
    variant_3576(8)
    variant_3576(10)
    bit8_in_10bit_path()
    print("\n##### 对照: L2F+F2L 融合成单级矩阵 (无中间量化) #####")
    fused_check(8)
    fused_check(10)

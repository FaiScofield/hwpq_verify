# -*- coding: utf-8 -*-
"""
CSC 定点数据通路位宽分析 (整合版)
=========================================================================
模型与 script/csc/get_csc_coefs.py 完全一致 (RK HW CSC):
    fix_mat  = round(float_mat * 2^precision)          # int32, 系数 Q13 等
    offset   = fix_factor * range_ofs_o + fix_mat @ range_ofs_i
数据通路 (C datapath, V2 型):
    P = mat @ pix                       # Q2: 点积(矩阵乘)结果
    T = P + offset + (1 << (precision-1))   # Q4: 移位前全量(含 round-half)
    out = clip( T >> precision , 0, 2^depth - 1 )

四个问题:
    Q1: mat          元素取值域        -> mat 表达位宽
    Q2: mat @ pix    点积取值域        -> 乘法器/点积累加位宽
    Q3: offset       偏移取值域        -> offset 表达位宽
    Q4: P+offset+2^(precision-1)       -> 移位前加法器位宽

用法示例:
    python script\\csc\\csc_bitwidth_analysis.py               # 全部 Q1-Q4
    python script\\csc\\csc_bitwidth_analysis.py -q 1 -q 4     # 只跑 Q1 与 Q4
    python script\\csc\\csc_bitwidth_analysis.py --s16-only    # 只统计系数<=s16(可写入寄存器)
    python script\\csc\\csc_bitwidth_analysis.py --fast        # 粗网格(快)
    python script\\csc\\csc_bitwidth_analysis.py -p 13 -d 10   # 指定精度/位深
    python script\\csc\\csc_bitwidth_analysis.py -p 0          # 全浮点(只统计取值域, 不分析位宽)
    python script\\csc\\csc_bitwidth_analysis.py --no-bcsh     # 忽略 BCSH, 只用标准转换矩阵
"""
import sys, os, argparse, itertools
import numpy as np

from get_csc_coefs import (
    CscCoefConfig,
    CscBcshConfig,
    get_csc_coefs,
    g_supported_standard_convert_modes,
    get_range_convert_mat,
    get_space_convert_mat,
    adjust_convert_mat,
)

# 与 CscBcshConfig 成员变量定义顺序一致:
# brightness/contrast/saturation/hue/r_gain/g_gain/b_gain/r_offset/g_offset/b_offset
BCSH_FIELD_ORDER = [n for n, v in CscBcshConfig.__dict__.items() if isinstance(v, int)]


# ---------------------------------------------------------------- helpers
def signed_bits(lo, hi):
    """能表示 [lo, hi] 范围内所有整数所需的有符号位数"""
    n = 1
    while not (lo >= -(1 << (n - 1)) and hi <= (1 << (n - 1)) - 1):
        n += 1
    return n


def make_config(mode_key, platform, depth, precision):
    cfg = CscCoefConfig()
    cfg.platform = platform
    cfg.pixel_depth = depth
    cfg.coef_precision = precision
    cfg.algo_type = "RK HW CSC"
    cfg.tune_fix_coefs = 0
    cfg.csc_mode = g_supported_standard_convert_modes[mode_key]
    return cfg


def pixel_corners(mode, depth):
    """输入像素合法范围的角点 (线性函数的最值必在角点)"""
    if mode.is_input_yuv and not mode.is_input_full_range:
        lo = [16 << (depth - 8)] * 3
        hi = [235 << (depth - 8), 240 << (depth - 8), 240 << (depth - 8)]  # limited YUV: Y<=940, C<=960
    else:
        lo = [0] * 3
        hi = [(1 << depth) - 1] * 3
    return lo, hi


def rebuild_mat_offset(mode_key, params, depth, precision):
    """用 mode 与 BCSH 参数重建 fix_mat / offset (与 get_csc_coefs 一致) """
    cfg = make_config(mode_key, "rk3572", depth, precision)
    b = CscBcshConfig()
    for name, val in zip(BCSH_FIELD_ORDER, params):
        setattr(b, name, val)
    M, off = get_csc_coefs(cfg, b)
    if precision == 0:  # 全浮点
        return cfg, b, M.astype(np.float64), off.astype(np.float64)
    return cfg, b, M.astype(np.int64), off.astype(np.int64)


def get_dc_vectors(cfg, b):
    """取与 offset 公式一致的 dc_in / dc_out(含 BCSH 对 dc_out 的调整)"""
    range_mat_i, range_mat_o, range_ofs_i, range_ofs_o = get_range_convert_mat(cfg.csc_mode, cfg.pixel_depth)
    color_convert_mat = get_space_convert_mat(cfg.csc_mode)
    final_mat = range_mat_o @ color_convert_mat @ range_mat_i
    dc_out = range_ofs_o.copy()
    if b is not None and cfg.algo_type in {"RK HW CSC", "RK SW CSC"}:
        _, dc_out, _ = adjust_convert_mat(cfg, b, final_mat, dc_out)
    return range_ofs_i.astype(np.float64), dc_out.astype(np.float64)


# ---------------------------------------------------------------- 主扫描
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--question", type=int, action="append", choices=[1, 2, 3, 4], help="要测试的问题编号(可多次), 缺省=全部")
    ap.add_argument("--s16-only", action="store_true", help="只保留 |mat 元素| <= 32767 (可写入16bit系数寄存器) 的配置")
    ap.add_argument("--fast", action="store_true", help="粗网格快速扫描")
    ap.add_argument("-p", "--precision", type=int, default=13, help="系数定点精度 bit, 0=全浮点(不做位宽分析)")
    ap.add_argument("-d", "--depth", type=int, default=10, help="像素位深 bit")
    ap.add_argument("-m", "--mode", type=str, default="", help="只测某个 mode, 如 2020l_to_rgbf")
    ap.add_argument("--no-bcsh", action="store_true",
                    help="忽略 BCSH 参数影响: 全部固定为中性 256, 只按标准转换矩阵统计")
    args = ap.parse_args()

    questions = args.question or [1, 2, 3, 4]
    depth = args.depth
    precision = args.precision
    float_mode = precision == 0  # precision=0: 全部浮点, 不做位宽分析
    if not float_mode and precision not in range(8, 17):
        print(f"Error: precision({precision}) should be 0 or in range [8, 16]!")
        sys.exit(1)
    if not float_mode and precision < depth:
        print(f"Warning: precision({precision}) < pixel_depth({depth})!")
    fix_half = (1 << (precision - 1)) if not float_mode else 0.0
    val_of = float if float_mode else int

    # 参数网格
    hue_grid = list(range(0, 512, 32 if not args.fast else 128))
    hue_grid.append(511)
    hue_grid = sorted(set(hue_grid))
    sat_grid = [0, 256, 511]
    con_grid = [256, 511]
    gain_grid = [(256, 256, 256), (511, 511, 511), (511, 256, 256), (256, 511, 256), (256, 256, 511)]
    br_grid = [0, 256, 511]
    ofs_grid = [0, 256, 511]

    if args.no_bcsh:
        # 忽略 BCSH 参数影响: 全部固定为中性 256, 不做参数扫描
        bcsh_combos = [(256, 256, 256, (256, 256, 256), 256, 256)]
    else:
        bcsh_combos = list(
            itertools.product(hue_grid, sat_grid, con_grid, gain_grid, br_grid, ofs_grid)
        )

    mode_list = list(g_supported_standard_convert_modes.keys())
    if args.mode:
        key = args.mode.lower()
        if key not in g_supported_standard_convert_modes:
            print(f"Error: unknown mode '{key}'")
            sys.exit(1)
        mode_list = [key]
    n_modes = len(mode_list)

    # 每问题每桶分别记录: 最大值(hi) 与 最小值(lo) 及上下文
    # record = (value, mode_key, params10, extra)
    best = {q: {"all": {"hi": None, "lo": None}, "s16": {"hi": None, "lo": None}} for q in questions}
    cnt = 0
    for key in mode_list:
        cfg = make_config(key, "rk3572", depth, precision)
        mode = cfg.csc_mode
        lo, hi = pixel_corners(mode, depth)
        corners = list(itertools.product(*[[lo[k], hi[k]] for k in range(3)]))

        def upd(q, bkt, val, extra):
            recs = best[q][bkt]
            if recs["hi"] is None or val > recs["hi"][0]:
                recs["hi"] = (val, key, params, extra)
            if recs["lo"] is None or val < recs["lo"][0]:
                recs["lo"] = (val, key, params, extra)

        for hue, sat, con, gains, br, ofs in bcsh_combos:
            b = CscBcshConfig()
            b.brightness = br
            b.contrast = con
            b.saturation = sat
            b.hue = hue
            b.r_gain, b.g_gain, b.b_gain = gains
            b.r_offset = b.g_offset = b.b_offset = ofs
            M, off = get_csc_coefs(cfg, b)
            if float_mode:
                M = M.astype(np.float64)
                off = off.astype(np.float64)
            else:
                M = M.astype(np.int64)
                off = off.astype(np.int64)
            params = tuple(getattr(b, n) for n in BCSH_FIELD_ORDER)
            cnt += 1
            maxc = None if float_mode else int(np.abs(M).max())

            for q in questions:
                if float_mode:
                    buckets = ["all"]
                elif args.no_bcsh or args.s16_only:
                    # --no-bcsh: 只有标准矩阵(必在 s16 内), 无需再测"不限"场景
                    buckets = ["s16"] if maxc <= 32767 else []
                else:
                    buckets = ["all"]
                    if maxc <= 32767:
                        buckets.append("s16")
                if not buckets:
                    continue
                # Q1: mat 元素
                if q == 1:
                    for r in range(3):
                        for c in range(3):
                            val = val_of(M[r, c])
                            for bkt in buckets:
                                upd(q, bkt, val, (r, c))
                # Q2: P = mat@pix
                elif q == 2:
                    for pix in corners:
                        P = M @ np.array(pix, dtype=np.int64)
                        for i in range(3):
                            val = val_of(P[i])
                            for bkt in buckets:
                                upd(q, bkt, val, (pix, i))
                # Q3: offset 元素
                elif q == 3:
                    for i in range(3):
                        val = val_of(off[i])
                        for bkt in buckets:
                            upd(q, bkt, val, i)
                # Q4: T = P + offset (+ 2^(precision-1), 定点时)
                else:
                    for pix in corners:
                        P = M @ np.array(pix, dtype=np.int64)
                        T = P + off + fix_half
                        for i in range(3):
                            val = val_of(T[i])
                            for bkt in buckets:
                                upd(q, bkt, val, (pix, i))

    # ------------------------------------------------------------ 打印
    print(
        f"# 扫描配置: modes={n_modes}, combos={cnt}, precision={precision}"
        f"({'全浮点' if float_mode else '定点'}), depth={depth}, "
        f"BCSH={'忽略(中性256)' if args.no_bcsh else '全参数扫描'}, "
        f"coef<=s16 过滤={'ON' if args.s16_only and not float_mode else 'OFF(同时统计)'}"
    )
    names = {
        1: "Q1 mat 元素",
        2: "Q2 mat@pix 点积",
        3: "Q3 offset",
        4: "Q4 P+offset" + ("" if float_mode else "+2^(p-1)"),
    }

    def fmt_num(v):
        return f"{v:.6f}" if float_mode else f"{v:>7d}"

    def fmt_vec(a):
        if float_mode:
            return "[" + ", ".join(f"{x:.6f}" for x in a) + "]"
        return "[" + ", ".join(f"{int(x):>9d}" for x in a) + "]"

    def fmt_mat(M):
        return "\n".join("      [" + " ".join(fmt_num(v) for v in row) + "]" for row in M)

    def show_extreme(q, tag, rec):
        value, mode_key, params, extra = rec
        cfg, b, M, off = rebuild_mat_offset(mode_key, params, depth, precision)
        if float_mode:
            print(f"\n  [{tag}] value = {value:.6f}")
        else:
            print(f"\n  [{tag}] value = {value}")
        print(f"    csc_mode = {mode_key}")
        print(f"    参数(bcsh,gains,offsets) = {params}")
        print(f"    mat:")
        print(fmt_mat(M))
        if q == 1:
            r, c = extra
            print(f"    -> mat[{r}][{c}] = {fmt_num(M[r, c])}  (mat 元素的最值)")
        elif q == 2:
            pix, ch = extra
            P = M @ np.array(pix, dtype=np.int64)
            print(f"    pixel = {pix}")
            print(f"    P = mat@pixel = {fmt_vec(P)}")
            print(f"    -> 极值通道 ch={ch}: P[{ch}] = {fmt_num(P[ch])}")
        elif q == 3:
            dc_in, dc_out = get_dc_vectors(cfg, b)
            ch = extra
            print(f"    dc_in  = {fmt_vec(dc_in)}")
            print(f"    dc_out = {fmt_vec(dc_out)}")
            if float_mode:
                calc = dc_out + M @ dc_in
                expr = "dc_out + mat@dc_in"
            else:
                calc = (1 << precision) * dc_out + M @ dc_in
                expr = f"2^{precision}*dc_out + mat@dc_in"
            print(f"    offset = {expr}")
            print(f"           = {fmt_vec(calc)}")
            print(f"    (get_csc_coefs 返回 off = {fmt_vec(off)})")
            print(f"    -> 极值通道 ch={ch}: offset[{ch}] = {fmt_num(off[ch])}")
        else:  # q == 4
            pix, ch = extra
            P = M @ np.array(pix, dtype=np.int64)
            T = P + off + fix_half
            if float_mode:
                out_pix = T  # 全浮点: out = mat@pixel + offset, 无移位无 clip
                expr = f"T = P+offset = {fmt_vec(T)}"
            else:
                out_pix = np.clip(T >> precision, 0, (1 << depth) - 1)
                expr = f"T = P+offset+2^{precision - 1} = {fmt_vec(T)}"
            print(f"    pixel  = {pix}")
            print(f"    offset = {fmt_vec(off)}")
            print(f"    P = mat@pixel          = {fmt_vec(P)}")
            print(f"    {expr}")
            if float_mode:
                print(f"    out = {fmt_vec(out_pix)}  (全浮点: 无移位无clip)")
            else:
                print(f"    out = clip(T>>{precision}, 0, {2 ** depth - 1}) = {fmt_vec(out_pix)}")
            print(f"    -> 极值通道 ch={ch}: T[{ch}] = {fmt_num(T[ch])}")

    for q in questions:
        print("\n" + "=" * 78)
        if float_mode:
            print(f"[{names[q]}]  浮点取值域(不做位宽分析)")
        else:
            print(f"[{names[q]}]  取值域与所需有符号位宽(保证不溢出)")
        print("=" * 78)
        if float_mode:
            buckets_out = ["all"]
        elif args.no_bcsh or args.s16_only:
            buckets_out = ["s16"]  # --no-bcsh: 只输出 s16(标准矩阵)场景
        else:
            buckets_out = ["s16", "all"]
        for bkt in buckets_out:
            recs = best[q][bkt]
            if recs["hi"] is None:
                continue
            tag = "全浮点 precision=0" if float_mode else ("系数<=s16(可写寄存器)" if bkt == "s16" else "不限(模型满参数)")
            lo_val = recs["lo"][0]
            hi_val = recs["hi"][0]
            print(f"\n-- 场景[{tag}] --")
            print(f"  取值域: [{fmt_num(lo_val)}, {fmt_num(hi_val)}]")
            if float_mode:
                print(f"  最大绝对值 = {fmt_num(max(abs(lo_val), abs(hi_val)))}  (浮点, 不做位宽分析)")
            else:
                nbits = signed_bits(lo_val, hi_val)
                print(f"  有符号位宽: {nbits} bit  (s{nbits}; 2^({nbits}-1)={1 << (nbits - 1)})")
            show_extreme(q, "最大值时", recs["hi"])
            show_extreme(q, "最小值时", recs["lo"])
    print("\n" + "=" * 78)
    if float_mode:
        print("说明: precision=0, mat/offset/结果均为浮点数, 仅统计取值域与最大绝对值")
    else:
        print("说明: Q13 定点, precision=13 时 2^13=8192; 有符号 N bit 可表示 [-2^(N-1), 2^(N-1)-1]")
    print("=" * 78)


if __name__ == "__main__":
    main()

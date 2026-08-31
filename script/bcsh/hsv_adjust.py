"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : hsv_adjust.py
Author      : vance.wu@rock-chips.com
Date        : 2026-08-05
Description : RGB <=> HSV 转换与 V/S/H 加性/乘性调整（对应 run_csc_note.md "RGB的HSV调整特点总结" 节）
"""

import numpy as np


def _to_rgb(rgb):
    """输入 (r,g,b) / (...,3) -> float32 数组，clamp [0,1]。"""
    arr = np.asarray(rgb, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'rgb 最后一维必须为 3，实际 shape={arr.shape}')
    return np.clip(arr, 0.0, 1.0)


def _is_scalar_rgb(rgb):
    """是否单像素 tuple/list 输入（返回 tuple 而非数组）。"""
    return isinstance(rgb, (tuple, list)) and len(rgb) == 3


def _wrap(orig, out):
    """标量输入返回 tuple，数组输入返回 numpy 数组。"""
    return tuple(out) if _is_scalar_rgb(orig) else out


def rgb_to_hsv(rgb):
    """RGB -> HSV。h∈[0,360)，s/v∈[0,1]。标量或数组 (...,3) 均可。"""
    orig = rgb
    rgb = _to_rgb(rgb)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    c = mx - mn
    v = mx
    s = np.divide(c, mx, out=np.zeros_like(c), where=mx != 0)   # 除0保护
    c_safe = np.where(c == 0, 1.0, c)
    h = np.zeros_like(c)
    h = np.where(mx == r, 60.0 * (((g - b) / c_safe + 6) % 6), h)
    h = np.where(mx == g, 60.0 * ((b - r) / c_safe + 2), h)
    h = np.where(mx == b, 60.0 * ((r - g) / c_safe + 4), h)
    # h = (h + 360.0) % 360.0                                       # h ∈ [0,360)
    if _is_scalar_rgb(orig):
        return float(h), float(s), float(v)
    return h, s, v


def hsv_to_rgb(hsv):
    """HSV -> RGB，参考 hsv2rgb_v4_hexwalk（六边形走表模型：M/m/mid + 6 段 TAB）。
    h∈[0,360)、s/v∈[0,1]；返回 rgb∈[0,1]。标量或数组 (...,3) 均可。
    s<=0（灰/黑）直接返回 v；与 rgb_to_hsv 构成往返（float 下近似恒等）。"""
    orig = hsv
    arr = np.asarray(hsv, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hsv 最后一维必须为 3，实际 shape={arr.shape}')
    h = arr[..., 0] % 360.0
    s = np.clip(arr[..., 1], 0.0, 1.0)
    v = np.clip(arr[..., 2], 0.0, 1.0)
    gray = s <= 0
    # ---- 对应 v4_hexwalk：M=V、C=V*S、m=V-C ----
    M = v
    C = v * s
    m = M - C
    seg = np.floor(h / 60.0).astype(np.int32) % 6      # 60° 扇区 0..5（对应 t>>FIX_BITS_H）
    f = h / 60.0 - seg                                 # 段内位置 0..1（对应 f14/F）
    # mid = (seg&1) ? M - C*f : m + C*f（v4 奇段 M-dm / 偶段 m+dm）
    mid = np.where(seg % 2 == 0, m + C * f, M - C * f)
    seg_tab = np.array([
        [0, 2, 1], [1, 2, 0], [1, 0, 2],
        [2, 0, 1], [2, 1, 0], [0, 1, 2],
    ])                                     # 每段 [M通道, m通道, 变化通道]，0/1/2=R/G/B
    m_idx = seg_tab[seg, 0]
    m2_idx = seg_tab[seg, 1]
    out = np.empty_like(arr)
    for ch in range(3):
        out[..., ch] = np.where(m_idx == ch, M, np.where(m2_idx == ch, m, mid))
    out = np.where(gray[..., None], v[..., None], out)  # 灰色直接返回 v
    return _wrap(orig, out)


def rgb_to_hsi(rgb):
    """RGB -> HSI（Gonzalez 模型）。h∈[0,360)，s/i∈[0,1]。标量或数组 (...,3) 均可。

    I = (R+G+B)/3；S = 1-min/I（I>0，全黑 I=0 时 S=0）；H 用 acos 连续公式
    （B<=G 取 θ，否则 360°-θ），与 HSV 的 60° 扇区色相数值等价。
    """
    orig = rgb
    arr = np.asarray(rgb, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hsi 最后一维必须为 3，实际 shape={arr.shape}')
    rgb_c = np.clip(arr, 0.0, 1.0)
    r, g, b = rgb_c[..., 0], rgb_c[..., 1], rgb_c[..., 2]
    i = (r + g + b) / 3.0
    mn = np.minimum(np.minimum(r, g), b)
    s = np.divide(i - mn, i, out=np.zeros_like(i), where=i > 0)   # S=1-min/I，I=0 全黑 S=0
    # H：acos 连续公式
    denom = np.sqrt((r - g) ** 2 + (r - b) * (g - b))
    safe = denom > 0.0
    num = 0.5 * ((r - g) + (r - b))
    theta = np.zeros_like(i)
    theta = np.where(safe, np.degrees(np.arccos(
        np.clip(num / np.where(safe, denom, 1.0), -1.0, 1.0))), 0.0)
    h = np.where(b <= g, theta, 360.0 - theta) % 360.0
    if _is_scalar_rgb(orig):
        return float(h), float(s), float(i)
    return h, s, i


def hsi_to_rgb(hsi):
    """HSI -> RGB，Gonzalez 三段扇区公式。返回 rgb∈[0,1]。标量或数组 (...,3) 均可。"""
    orig = hsi
    arr = np.asarray(hsi, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hsi 最后一维必须为 3，实际 shape={arr.shape}')
    h = arr[..., 0] % 360.0
    s = np.clip(arr[..., 1], 0.0, 1.0)
    i = np.clip(arr[..., 2], 0.0, 1.0)
    m0 = (h >= 0.0) & (h < 120.0)
    m1 = (h >= 120.0) & (h < 240.0)
    m2 = h >= 240.0
    # 扇区 0：红为主
    h0 = h
    b0 = i * (1.0 - s)
    r0 = i * (1.0 + s * np.cos(np.radians(h0)) / np.cos(np.radians(60.0 - h0)))
    g0 = 3.0 * i - (r0 + b0)
    # 扇区 1：绿为主
    h1 = h - 120.0
    r1 = i * (1.0 - s)
    g1 = i * (1.0 + s * np.cos(np.radians(h1)) / np.cos(np.radians(60.0 - h1)))
    b1 = 3.0 * i - (r1 + g1)
    # 扇区 2：蓝为主
    h2 = h - 240.0
    g2 = i * (1.0 - s)
    b2 = i * (1.0 + s * np.cos(np.radians(h2)) / np.cos(np.radians(60.0 - h2)))
    r2 = 3.0 * i - (g2 + b2)
    r = np.where(m0, r0, np.where(m1, r1, r2))
    g = np.where(m0, g0, np.where(m1, g1, g2))
    b = np.where(m0, b0, np.where(m1, b1, b2))
    out = np.clip(np.stack([r, g, b], axis=-1), 0.0, 1.0)
    return _wrap(orig, out)


def rgb_to_hsl(rgb):
    """RGB -> HSL（双锥模型）。h∈[0,360)，s/l∈[0,1]。标量或数组 (...,3) 均可。

    L=(max+min)/2；S=(max-min)/(1-|2L-1|)（L=0/1 时 S=0）；H 与 HSV 相同 60° 扇区。
    """
    orig = rgb
    arr = np.asarray(rgb, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hsl 最后一维必须为 3，实际 shape={arr.shape}')
    rgb_c = np.clip(arr, 0.0, 1.0)
    r, g, b = rgb_c[..., 0], rgb_c[..., 1], rgb_c[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    l = (mx + mn) / 2.0
    c = mx - mn
    denom = 1.0 - np.abs(2.0 * l - 1.0)
    s = np.divide(c, denom, out=np.zeros_like(c), where=denom != 0)
    c_safe = np.where(c == 0, 1.0, c)
    h = np.zeros_like(c)
    h = np.where(mx == r, 60.0 * (((g - b) / c_safe + 6) % 6), h)
    h = np.where(mx == g, 60.0 * ((b - r) / c_safe + 2), h)
    h = np.where(mx == b, 60.0 * ((r - g) / c_safe + 4), h)
    if _is_scalar_rgb(orig):
        return float(h), float(s), float(l)
    return h, s, l


def hsl_to_rgb(hsl):
    """HSL -> RGB，双锥扇区公式。返回 rgb∈[0,1]。标量或数组 (...,3) 均可。"""
    orig = hsl
    arr = np.asarray(hsl, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hsl 最后一维必须为 3，实际 shape={arr.shape}')
    h = arr[..., 0] % 360.0
    s = np.clip(arr[..., 1], 0.0, 1.0)
    l = np.clip(arr[..., 2], 0.0, 1.0)
    c = (1.0 - np.abs(2.0 * l - 1.0)) * s
    hh = h / 60.0
    x = c * (1.0 - np.abs(hh % 2.0 - 1.0))
    m = l - c / 2.0
    seg = np.floor(hh).astype(np.int32) % 6
    # 每扇区 (r, g, b) 基值：seg0..5 依次取 (c,x,0)/(x,c,0)/(0,c,x)/(0,x,c)/(x,0,c)/(c,0,x)
    r = np.where(seg == 0, c, np.where(seg == 1, x, np.where(seg == 2, 0.0,
        np.where(seg == 3, 0.0, np.where(seg == 4, x, c)))))
    g = np.where(seg == 0, x, np.where(seg == 1, c, np.where(seg == 2, c,
        np.where(seg == 3, x, np.where(seg == 4, 0.0, 0.0)))))
    b = np.where(seg == 0, 0.0, np.where(seg == 1, 0.0, np.where(seg == 2, x,
        np.where(seg == 3, c, np.where(seg == 4, c, x)))))
    out = np.clip(np.stack([r + m, g + m, b + m], axis=-1), 0.0, 1.0)
    return _wrap(orig, out)


# ------------------------------------------------------------------ #
# HCY（Hue/Chroma/Luma，Rec.601 luma，六边形色相）                   #
# 参考 colorjs/color-space spaces/hcy.js（Kuzma Shapran/Chilliant）  #
# ------------------------------------------------------------------ #

_HCY_LUMA_W = (0.299, 0.587, 0.114)   # Rec.601 luma 权重


def _hcy_luma(rgb):
    """Rec.601 luma -> (...,) 灰度。"""
    return (rgb[..., 0] * _HCY_LUMA_W[0] + rgb[..., 1] * _HCY_LUMA_W[1]
            + rgb[..., 2] * _HCY_LUMA_W[2])


def _hcy_hue_ramp(h):
    """纯色相斜坡（V=1 的六边形色相，H∈[0,1)）-> (hr, hg, hb)∈[0,1]。"""
    x = h * 6.0
    hr = np.minimum(1.0, np.maximum(0.0, np.abs(x - 3.0) - 1.0))
    hg = np.minimum(1.0, np.maximum(0.0, 2.0 - np.abs(x - 2.0)))
    hb = np.minimum(1.0, np.maximum(0.0, 2.0 - np.abs(x - 4.0)))
    return hr, hg, hb


def rgb_to_hcy(rgb):
    """RGB -> HCY。h∈[0,360)，c/y∈[0,1]。标量或数组 (...,3) 均可。

    C 为按当前色相可承载的最大色度归一化（Y<Z 时 C*=Z/Y，否则 C*=(1-Z)/(1-Y)，
    Z 为该色相纯色 luma），使同 Y 的颜色视觉亮度一致；接口与 rgb_to_hsv 一致
    （(h, s, 第三通道)，S 通道为色度 C）。
    """
    orig = rgb
    arr = np.asarray(rgb, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hcy 最后一维必须为 3，实际 shape={arr.shape}')
    rgb_c = np.clip(arr, 0.0, 1.0)
    r, g, b = rgb_c[..., 0], rgb_c[..., 1], rgb_c[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    chroma = mx - mn
    c_safe = np.where(chroma == 0, 1.0, chroma)
    h6 = np.zeros_like(chroma)
    h6 = np.where(mx == r, ((g - b) / c_safe % 6.0 + 6.0) % 6.0, h6)
    h6 = np.where(mx == g, (b - r) / c_safe + 2.0, h6)
    h6 = np.where(mx == b, (r - g) / c_safe + 4.0, h6)
    h = h6 / 6.0 * 360.0
    y = _hcy_luma(rgb_c)
    hr, hg, hb = _hcy_hue_ramp(h6 / 6.0)
    z = _hcy_luma(np.stack([hr, hg, hb], axis=-1))
    # 反转色度归一化：还原为该色相/该 Y 可承载的最大色度（∈[0,1]）。
    z_over_y = np.divide(z, y, out=np.ones_like(y), where=y != 0)
    one_minus = np.divide(1.0 - z, 1.0 - y, out=np.ones_like(y), where=(1.0 - y) != 0)
    c_out = np.where(
        chroma != 0,
        np.where(y < z, chroma * z_over_y, chroma * one_minus),
        chroma)
    if _is_scalar_rgb(orig):
        return float(h), float(c_out), float(y)
    return h, c_out, y


def hcy_to_rgb(hcy):
    """HCY -> RGB（Rec.601 luma 圆柱）。返回 rgb∈[0,1]。标量或数组 (...,3) 均可。"""
    orig = hcy
    arr = np.asarray(hcy, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hcy 最后一维必须为 3，实际 shape={arr.shape}')
    h = arr[..., 0] % 360.0
    c = np.clip(arr[..., 1], 0.0, 1.0)
    y = np.clip(arr[..., 2], 0.0, 1.0)
    hr, hg, hb = _hcy_hue_ramp(h / 360.0)
    z = _hcy_luma(np.stack([hr, hg, hb], axis=-1))
    # 色度归一化：把 C 缩放到该 Y 下不越界（保持同 Y 亮度一致）。
    c = np.where(
        y < z,
        np.where(z != 0.0, c * y / z, 0.0),
        np.where(z < 1.0, c * (1.0 - y) / (1.0 - z), c))
    r = (hr - z) * c + y
    g = (hg - z) * c + y
    b = (hb - z) * c + y
    return _wrap(orig, np.clip(np.stack([r, g, b], axis=-1), 0.0, 1.0))


# ------------------------------------------------------------------ #
# HSP（Hue/Saturation/Perceived brightness，六边形色相 + 感知亮度）  #
# 参考 colorjs/color-space spaces/hsp.js（Darel Rex Finley）         #
# ------------------------------------------------------------------ #

_HSP_W = (0.299, 0.587, 0.114)   # 感知亮度权重（Rec.601，作用于通道平方）


def rgb_to_hsp(rgb):
    """RGB -> HSP。h∈[0,360)，s/p∈[0,1]。标量或数组 (...,3) 均可。

    P = sqrt(0.299r²+0.587g²+0.114b²)（感知亮度，通道平方加权）；
    S = 1-min/max（与 HSV 相同）；H 为六边形色相（与 HSV 同角，灰色取 0）。
    """
    orig = rgb
    arr = np.asarray(rgb, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hsp 最后一维必须为 3，实际 shape={arr.shape}')
    rgb_c = np.clip(arr, 0.0, 1.0)
    r, g, b = rgb_c[..., 0], rgb_c[..., 1], rgb_c[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    c = mx - mn
    # P：感知亮度（通道平方加权）
    p = np.sqrt(r * r * _HSP_W[0] + g * g * _HSP_W[1] + b * b * _HSP_W[2])
    # S = 1 - min/max（HSV 饱和度）
    s = np.divide(c, mx, out=np.zeros_like(c), where=mx != 0)
    # 六边形色相（同 HSV/HCY）；灰色（c==0）取 0
    c_safe = np.where(c == 0, 1.0, c)
    h6 = np.zeros_like(c)
    h6 = np.where(mx == r, ((g - b) / c_safe % 6.0 + 6.0) % 6.0, h6)
    h6 = np.where(mx == g, (b - r) / c_safe + 2.0, h6)
    h6 = np.where(mx == b, (r - g) / c_safe + 4.0, h6)
    h = np.where(c == 0, 0.0, h6 / 6.0 * 360.0)
    if _is_scalar_rgb(orig):
        return float(h), float(s), float(p)
    return h, s, p


def hsp_to_rgb(hsp):
    """HSP -> RGB。返回 rgb∈[0,1]。标量或数组 (...,3) 均可。

    6 扇区 × 全饱和/非全饱和共 12 段闭式求解，与 colorjs hsp.js 一致。
    """
    orig = hsp
    arr = np.asarray(hsp, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hsp 最后一维必须为 3，实际 shape={arr.shape}')
    h = arr[..., 0] % 360.0 / 360.0
    s = np.clip(arr[..., 1], 0.0, 1.0)
    p = np.clip(arr[..., 2], 0.0, 1.0)
    Pr, Pg, Pb = _HSP_W
    mm = 1.0 - s                       # min/max 比值
    seg = np.floor(h * 6.0).astype(np.int32) % 6
    k = seg.astype(np.float32)
    # 扇区内位置 h'∈[0,1]：偶扇区递增、奇扇区递减
    hprime = np.where(seg % 2 == 0, 6.0 * (h - k / 6.0), 6.0 * (-h + (k + 1.0) / 6.0))
    # 每扇区 (max,mid,min) 通道权重：0:(R,G,B) 1:(G,R,B) 2:(G,B,R) 3:(B,G,R) 4:(B,R,G) 5:(R,B,G)
    def _wsel(a0, a1, a2, a3, a4, a5):
        return np.where(seg == 0, a0, np.where(seg == 1, a1, np.where(
            seg == 2, a2, np.where(seg == 3, a3, np.where(seg == 4, a4, a5)))))
    wmax = _wsel(Pr, Pg, Pg, Pb, Pb, Pr)
    wmid = _wsel(Pg, Pr, Pb, Pg, Pr, Pb)
    wmin = _wsel(Pb, Pb, Pr, Pr, Pg, Pg)
    full = s >= 1.0
    mm_safe = np.where(full, 1.0, mm)
    # 非全饱和分支（minOverMax>0）：base 为最小通道，r/mid 由 h' 内插
    part = 1.0 + hprime * (1.0 / mm_safe - 1.0)
    base = p / np.sqrt(wmax / (mm_safe * mm_safe) + wmid * part * part + wmin)
    maxv = base / mm_safe
    midv = base + hprime * (maxv - base)
    # 全饱和分支（s==1）：最小通道=0
    bfull = p / np.sqrt(wmax + wmid * hprime * hprime)
    mxv = np.where(full, bfull, maxv)
    mdv = np.where(full, bfull * hprime, midv)
    mnv = np.where(full, 0.0, base)
    # 通道赋值（按扇区 max/mid/min -> R/G/B）
    r = np.where(seg == 0, mxv, np.where(seg == 1, mdv, np.where(seg == 2, mnv,
        np.where(seg == 3, mnv, np.where(seg == 4, mdv, mxv)))))
    g = np.where(seg == 0, mdv, np.where(seg == 1, mxv, np.where(seg == 2, mxv,
        np.where(seg == 3, mdv, np.where(seg == 4, mnv, mnv)))))
    b = np.where(seg == 0, mnv, np.where(seg == 1, mnv, np.where(seg == 2, mdv,
        np.where(seg == 3, mxv, np.where(seg == 4, mxv, mdv)))))
    return _wrap(orig, np.clip(np.stack([r, g, b], axis=-1), 0.0, 1.0))


# ------------------------------------------------------------------ #
# Lch（CIELAB 柱坐标）                                               #
# ------------------------------------------------------------------ #
# sRGB (D65) <-> XYZ 矩阵与 D65 白点（标准值）。
_SRGB_TO_XYZ = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041],
], dtype=np.float32)
_XYZ_TO_SRGB = np.array([
    [3.2404542, -1.5371385, -0.4985314],
    [-0.9692660, 1.8760108, 0.0415560],
    [0.0556434, -0.2040259, 1.0572252],
], dtype=np.float32)
_XYZ_D65 = np.array([0.95047, 1.0, 1.08883], dtype=np.float32)


def _srgb_to_xyz(rgb):
    """归一化 sRGB (...,3) -> XYZ (...,3)（线性化 + D65 矩阵）。"""
    rgb = np.asarray(rgb, dtype=np.float32)
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return lin @ _SRGB_TO_XYZ.T


def _xyz_to_lab(xyz):
    """XYZ (...,3) -> (L, a, b)（各 (...,)）。D65 白点，L∈[0,100]。"""
    xyz = np.asarray(xyz, dtype=np.float32)

    def _f(t):
        eps = (6.0 / 29.0) ** 3
        return np.where(t > eps, t ** (1.0 / 3.0),
                        t / (3.0 * (6.0 / 29.0) ** 2) + 4.0 / 29.0)

    fx = _f(xyz[..., 0] / _XYZ_D65[0])
    fy = _f(xyz[..., 1] / _XYZ_D65[1])
    fz = _f(xyz[..., 2] / _XYZ_D65[2])
    return 116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)


def _lab_to_xyz(L, a, b):
    """(L, a, b) -> XYZ (...,3)。D65 白点。"""
    delta = 6.0 / 29.0
    fy = (L + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0

    def _inv_f(t):
        return np.where(t > delta, t ** 3, 3.0 * delta ** 2 * (t - 4.0 / 29.0))

    return np.stack([_inv_f(fx) * _XYZ_D65[0], _inv_f(fy) * _XYZ_D65[1],
                     _inv_f(fz) * _XYZ_D65[2]], axis=-1)


def _lab_to_srgb(L, a, b):
    """(L, a, b) -> sRGB (...,3)（去线性化，越界钳位 [0,1]）。"""
    xyz = _lab_to_xyz(L, a, b)
    lin = xyz @ _XYZ_TO_SRGB.T
    rgb = np.where(lin <= 0.0031308, 12.92 * lin,
                   1.055 * np.maximum(lin, 0.0) ** (1.0 / 2.4) - 0.055)
    return np.clip(rgb, 0.0, 1.0)


def _compute_lch_cmax(samples: int = 48) -> float:
    """sRGB 色域内最大 LCH 色度 C（S 归一化因子，约 134）。"""
    vals = np.linspace(0.0, 1.0, samples, dtype=np.float32)
    r, g, b = np.meshgrid(vals, vals, vals, indexing="ij")
    rgb = np.stack([r.ravel(), g.ravel(), b.ravel()], axis=-1)
    L, a, b = _xyz_to_lab(_srgb_to_xyz(rgb))
    c = np.sqrt(a * a + b * b)
    return float(c.max())


_LCH_C_MAX = _compute_lch_cmax()


def rgb_to_lch(rgb):
    """RGB -> Lch（CIELAB 柱坐标，D65/sRGB）。h∈[0,360)，s=c/Cmax∈[0,1]，l=L/100∈[0,1]。

    标量或数组 (...,3) 均可；接口与 rgb_to_hsv 一致（(h, s, 第三通道)）。
    """
    orig = rgb
    arr = np.asarray(rgb, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'lch 最后一维必须为 3，实际 shape={arr.shape}')
    L, a, b = _xyz_to_lab(_srgb_to_xyz(np.clip(arr, 0.0, 1.0)))
    c = np.sqrt(a * a + b * b)
    h = (np.degrees(np.arctan2(b, a)) + 360.0) % 360.0
    s = c / _LCH_C_MAX
    l = L / 100.0
    if _is_scalar_rgb(orig):
        return float(h), float(s), float(l)
    return h, s, l


def lch_to_rgb(lch):
    """Lch -> RGB（sRGB D65）。返回 rgb∈[0,1]。标量或数组 (...,3) 均可。"""
    orig = lch
    arr = np.asarray(lch, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'lch 最后一维必须为 3，实际 shape={arr.shape}')
    h = arr[..., 0] % 360.0
    s = np.clip(arr[..., 1], 0.0, 1.0)
    l = np.clip(arr[..., 2], 0.0, 1.0)
    c = s * _LCH_C_MAX
    a = c * np.cos(np.radians(h))
    b = c * np.sin(np.radians(h))
    return _wrap(orig, _lab_to_srgb(l * 100.0, a, b))


# ------------------------------------------------------------------ #
# RGB 域直接调整                                                      #
# ------------------------------------------------------------------ #

def _rgb_luma(rgb, coef='bt709'):
    """luma -> (...,) 灰度（RGB 域 S 灰阶混合用）。coef='bt709'/'bt601'。"""
    if coef == 'bt601':
        w0, w1, w2 = 0.299, 0.587, 0.114
    else:
        w0, w1, w2 = 0.2126, 0.7152, 0.0722
    return rgb[..., 0] * w0 + rgb[..., 1] * w1 + rgb[..., 2] * w2


def _rgb_saturation(rgb):
    """HSV 式饱和度 (max-min)/max，除0保护 -> (...,)。"""
    mx = np.max(rgb, axis=-1)
    mn = np.min(rgb, axis=-1)
    c = mx - mn
    return np.divide(c, mx, out=np.zeros_like(c), where=mx != 0)


def _rotate_hue(rgb, angle_deg):
    """RGB 绕灰色轴 (1,1,1)/√3 旋转 angle_deg（度，标量或数组）。

    灰阶保持不变；等价标准 hue-rotate（圆形色相旋转，与 HSV 六边形色相存在
    模型固有差异，用于 RGB 域 H 通道调整）。
    """
    th = np.radians(angle_deg)
    c = np.cos(th)
    s = np.sin(th)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    gray3 = (r + g + b) / 3.0
    inv = 1.0 / np.sqrt(3.0)
    out0 = c * r + (1.0 - c) * gray3 + s * (b - g) * inv
    out1 = c * g + (1.0 - c) * gray3 + s * (r - b) * inv
    out2 = c * b + (1.0 - c) * gray3 + s * (g - r) * inv
    return np.stack([out0, out1, out2], axis=-1)


def _rgb_hue_add(rgb, angle_deg):
    """RGB 域 ModeAdd：经 HSV 中转做六边形色相加法（h'=(h+angle)%360，S/V 不变）。"""
    h, s, v = rgb_to_hsv(rgb)
    h = (h + np.asarray(angle_deg, dtype=np.float32)) % 360.0
    return hsv_to_rgb(np.stack([h, s, v], axis=-1))


def _rgb_contrast_brightness(rgb, gain_c, db, mode_c, mode_b):
    """RGB 域 C/V：三通道统一 contrast(ch) 后按 mode_b 施加 db。返回 (...,3)。"""
    if gain_c is None:
        gain_c = 1.0
    if db is None:
        db = 0.0
    mode_c = str(mode_c).lower()
    if mode_c == 'tanslant':
        c = np.clip(np.asarray(gain_c, np.float64), -1.0, 1.0)
        g = np.tan((c + 1.0) * (np.pi / 4.0))
        out = np.clip((rgb - 0.5) * g[..., None] + 0.5, 0.0, 1.0).astype(np.float32)
    elif mode_c == 'zero':
        gc = np.clip(np.asarray(gain_c, np.float32), 0.0, 4.0)
        out = np.clip(gc * rgb, 0.0, 1.0)
    elif mode_c == 'both':
        gc = np.clip(np.asarray(gain_c, np.float32), 0.0, 4.0)
        out = np.where(gc < 1.0, gc * rgb, (rgb - 0.5) * gc + 0.5)
        out = np.clip(out, 0.0, 1.0)
    elif mode_c == 'faststone':
        # FastStone Contrast：逐通道 Levels 拉伸 out=clip(k·in+b)（0~255 域，C∈[-1,1] 中性 0）
        # 参数先归一化为 [-100,100] 再代入通用公式（由 FastStone 输出图逐像素提取拟合，见 hsv_note.md）：
        #   C≥0: k=1+0.01651C,        b=-1.1759C+0.338
        #   C<0: k=1+9.11e-3C+1.09e-4C²+5.23e-7C³,  b=-6.50e-1C-7.82e-3C²-3.75e-5C³
        c = np.clip(np.asarray(gain_c, np.float64), -1.0, 1.0) * 100.0
        pos = c >= 0.0
        k = np.where(pos, 1.0 + 0.01651 * c,
                     1.0 + 9.11e-3 * c + 1.09e-4 * c * c + 5.23e-7 * c * c * c)
        b = np.where(pos, -1.1759 * c + 0.338,
                     -6.50e-1 * c - 7.82e-3 * c * c - 3.75e-5 * c * c * c)
        out = np.clip(k[..., None] * rgb + (b / 255.0)[..., None], 0.0, 1.0).astype(np.float32)
    else:   # 'mid'（默认）：过 0.5 中点
        gc = np.clip(np.asarray(gain_c, np.float32), 0.0, 4.0)
        out = np.clip((rgb - 0.5) * gc + 0.5, 0.0, 1.0)
    mode_b = str(mode_b).lower()
    if mode_b in ('mul', 'mulkeepmin'):
        gv = np.clip(np.asarray(db, np.float32), 0.0, 4.0)
        out = np.clip(out * gv[..., None], 0.0, 1.0)
    elif mode_b == 'negmulposrat':
        d = np.clip(np.asarray(db, np.float32), -1.0, 1.0)
        comp = out * (1.0 + d[..., None])         # δB<0：乘法压缩
        white = out + d[..., None] * (1.0 - out)  # δB>0：向白靠拢
        out = np.clip(np.where((d < 0)[..., None], comp, white), 0.0, 1.0)
    else:   # 'add'（默认）：加性
        d = np.clip(np.asarray(db, np.float32), -1.0, 1.0)
        out = np.clip(out + d[..., None], 0.0, 1.0)
    return out


def adjust_rgb(rgb, delta_b=None, delta_s=None, gain_c=1.0, tolerance_s=0.0,
               mode_c='mid', mode_b='add', angle_deg=0.0, gray_coef='bt709',
               h_mode='add'):
    """RGB 域直接 BCSH 调整（不经过 HSV 域转换）。标量或数组 (...,3) 均可。

    - C/V：三通道统一 ch'=contrast(ch) 按 mode_c 参考点（'faststone' 为 FastStone
      兼容逐通道 Levels 拉伸 out=clip(k·in+b)，C∈[-1,1]，再按 mode_b 施加 delta_b
    - S：scale=delta_s（乘性，中性 1.0）；out=scale*in+(1-scale)*gray(in)，
         gray 为 luma——gray_coef='bt709' 用 BT.709、'bt601' 用 BT.601 系数；
         scale>1（增色）时 S<tolerance_s 的像素保持原样。
    - H：按 h_mode 生效，angle_deg 由调用方算好（SameOffset 角度或 SameTarget
         进度*弧长，可逐像素数组）：
           'add' 经 HSV 中转做六边形色相加法 h'=(h+angle)%360；
           'rotategray' 绕灰色轴 (1,1,1)/√3 旋转。
    """
    orig = rgb
    arr = np.asarray(rgb, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'rgb 最后一维必须为 3，实际 shape={arr.shape}')
    rgb_in = np.clip(arr, 0.0, 1.0)
    # ---- V：逐通道 contrast + brightness ----
    rgb_v = _rgb_contrast_brightness(rgb_in, gain_c, delta_b,
                                     str(mode_c).lower(), str(mode_b).lower())
    # ---- S：灰阶混合（scale 语义，始终生效） ----
    scale = np.asarray(
        1.0 if delta_s is None else np.clip(np.asarray(delta_s, np.float32), 0.0, 4.0),
        np.float32)
    gray = _rgb_luma(rgb_v, gray_coef)
    sat = _rgb_saturation(rgb_v)
    apply = (sat >= tolerance_s) | (scale <= 1.0)
    rgb_s = np.where(
        apply[..., None],
        scale[..., None] * rgb_v + (1.0 - scale)[..., None] * gray[..., None],
        rgb_v)
    # ---- H：按 modeH 生效方式 ----
    angle = np.asarray(angle_deg, dtype=np.float32)
    h_mode = str(h_mode).lower()
    if np.all(angle == 0.0):
        rgb_h = rgb_s
    elif h_mode == 'rotategray':
        rgb_h = _rotate_hue(rgb_s, angle)
    else:   # 'add'（默认）：HSV 中转六边形色相加法
        rgb_h = _rgb_hue_add(rgb_s, angle)
    return _wrap(orig, np.clip(rgb_h, 0.0, 1.0))


def adjust_hsv(hsv, delta_b=None, delta_s=None, delta_h=None, gain_c=1.0, mode='add',
               tolerance_s: float = 0.0, mode_c='mid', mode_b='add'):
    """HSV 域 V/S/H 调整（hsv 输入、hsv 输出，不涉及 RGB 重建）。
    按 V -> S -> H 顺序执行：
      V：Contrast 乘性 + delta_b（加性或乘性）；mode_c 选择增益参考点：
           'mid'   v'=clip((v-0.5)*gc + 0.5 [+db])   （过 v=0.5 中点，默认）
           'zero'  v'=clip(gc*v [+db])               （过 v=0.0 原点）
           'both'  gc<1 时等效 'zero'，gc>1 时等效 'mid'（gc==1 恒等）
           'tanslant'  v'=clip((v-0.5)*tan((c+1)π/4)+0.5)（c∈[-1,1]，中性 0；
                   tan 映射增益：c=0->1 恒等，c=-1->0 全压到 0.5，c=1->∞ 极强对比）
         mode_b 决定 delta_b 生效方式：
           'add'   v'=clip(contrast(v)+db)           （db ∈ [-1,1]，默认）
           'mul'   v'=clip(contrast(v)*gv)           （gv 增益 ∈ [0,4]，中性 1.0）
           'negmulposrat'  db∈[-1,1]，中性 0：db<0 乘性压缩 v'=clip(v*(1+db))；
                   db>0 按进度向白靠拢 v'=clip(v+db*(1-v))；db=-1 纯黑、db=1 纯白
           'mulKeepMin'  保底乘性：调小(gv<1)时 V 线性缩小到旧 RGB 最小通道
                   m=v'*(1-s)（v'=m+(v-m)*gv，永不小于 m），S 保持不变（饱和度
                   不变，新最小通道自动 m'=r*v'，r=m/v）；调大(gv>=1)时与 'mul'
                   一致（gv 增益 ∈ [0,4]）
      S：mode='add'  s'=clip(s+ds)；mode='mul'  s'=clip(s*ds)     （ds ∈ [-1,1] 或乘性增益 ∈ [0,4]）
      S：mode='negmulposrat'  ds∈[-1,1]，中性 0：ds<0 乘性压缩 s'=clip(s*(1+ds))；
          ds>0 向全饱和靠拢 s'=clip(s+ds*(1-s))；ds=-1 灰、ds=1 全饱和
      H：始终加性     h'=(h + dh*360) % 360                        （dh ∈ [-0.5,0.5]，0.5=180°）
    语义：S < tolerance_s 的像素不做放大（增色），缩小（减色）始终允许；
          H 统一平移（对灰色无影响）。
    支持单个像素 (h,s,v) 或一帧图像 (...,3) 数组，返回同形状。"""
    orig = hsv
    arr = np.asarray(hsv, dtype=np.float32)
    if arr.shape[-1] != 3:
        raise ValueError(f'hsv 最后一维必须为 3，实际 shape={arr.shape}')
    h = arr[..., 0] % 360.0
    s = np.clip(arr[..., 1], 0.0, 1.0)
    v = np.clip(arr[..., 2], 0.0, 1.0)
    db = 0.0 if delta_b is None else np.clip(np.asarray(delta_b, np.float32), -1.0, 1.0)
    dh = 0.0 if delta_h is None else np.clip(np.asarray(delta_h, np.float32), -0.5, 0.5)
    mode_c = str(mode_c).lower()
    if mode_c == 'tanslant':
        # TanSlant：c∈[-1,1]，tan 映射增益（中性 0 -> tan(π/4)=1）
        gc = 1.0 if gain_c is None else np.clip(np.asarray(gain_c, np.float32), -1.0, 1.0)
    else:
        gc = 1.0 if gain_c is None else np.clip(np.asarray(gain_c, np.float32), 0.0, 4.0)
    mode = str(mode).lower()
    if mode == 'add':
        ds = 0.0 if delta_s is None else np.clip(np.asarray(delta_s, np.float32), -1.0, 1.0)
        # ---- S：S<tolerance_s 的像素不放大（增色），缩小（减色）始终允许 ----
        s_new = np.where((s >= tolerance_s) | (ds <= 0.0), np.clip(s + ds, 0.0, 1.0), s)
    elif mode == 'mul':
        gs = 1.0 if delta_s is None else np.clip(np.asarray(delta_s, np.float32), 0.0, 4.0)
        # ---- S：S<tolerance_s 的像素不放大（增色），缩小（减色）始终允许 ----
        s_new = np.where((s >= tolerance_s) | (gs <= 1.0), np.clip(s * gs, 0.0, 1.0), s)
    elif mode == 'negmulposrat':
        # 负值乘性压缩 / 正值向全饱和靠拢（ds∈[-1,1]，中性 0）
        ds = 0.0 if delta_s is None else np.clip(np.asarray(delta_s, np.float32), -1.0, 1.0)
        s_comp = np.clip(s * (1.0 + ds), 0.0, 1.0)               # δS<0：乘性压缩（减色）
        s_sat = np.clip(s + ds * (1.0 - s), 0.0, 1.0)            # δS>0：向全饱和靠拢（增色）
        s_apply = np.where(ds < 0.0, s_comp, s_sat)
        # ---- S：S<tolerance_s 的像素不放大（增色），缩小（减色）始终允许 ----
        s_new = np.where((s >= tolerance_s) | (ds <= 0.0), s_apply, s)
    else:
        raise ValueError(f"Unsupported adjust_hsv mode: {mode!r}, expect 'add'/'mul'/'negmulposrat'")
    # ---- V：Contrast 乘性 + delta_b 加性 + clamp，mode_c 决定增益参考点 ----
    mode_c = str(mode_c).lower()
    if mode_c == 'zero':
        # 过 v=0.0 原点：v' = gc*v
        v_new = np.clip(gc * v, 0.0, 1.0)
    elif mode_c == 'both':
        # gc<1 等效 GainAtZero>1 等效 GainAtMid==1 恒等
        v_new = np.where(gc < 1.0, gc * v, (v - 0.5) * gc + 0.5)
        v_new = np.clip(v_new, 0.0, 1.0)
    elif mode_c == 'tanslant':
        # TanSlant：增益 = tan((c+1)π/4)，c∈[-1,1]；用 float64 避免 π/2 附近符号翻转
        g = np.tan((np.asarray(gc, np.float64) + 1.0) * (np.pi / 4.0))
        v_new = np.clip((v - 0.5) * g + 0.5, 0.0, 1.0).astype(np.float32)
    else:   # 'mid'（默认）：过 v=0.5 中点
        v_new = np.clip((v - 0.5) * gc + 0.5, 0.0, 1.0)
    # ---- delta_b 生效方式：mode_b='add' 加性 / 'mul' 乘性 / 'mulKeepMin' 保底乘性 ----
    mode_b = str(mode_b).lower()
    if mode_b in ('mul', 'mulkeepmin'):
        gv = 1.0 if delta_b is None else np.clip(np.asarray(delta_b, np.float32), 0.0, 4.0)
        if mode_b == 'mulkeepmin':
            # 保底乘性：乘法增益作用于 V；调小(gv<1)时按量程比例线性缩小到旧
            # RGB 最小通道 m=v_new*(1-s_new)（v'=m+(v-m)*gv，永不小于 m），
            # S 保持不变 -> 饱和度不变，新最小通道自动为 m'=r*v'（r=m/v）。
            m_val = np.clip(v_new * (1.0 - s_new), 0.0, 1.0)
            v_new = np.clip(
                np.where(gv < 1.0, m_val + (v_new - m_val) * gv, v_new * gv),
                0.0, 1.0)
        else:
            v_new = np.clip(v_new * gv, 0.0, 1.0)
    elif mode_b == 'negmulposrat':
        # 负值乘性压缩 / 正值按进度向白靠拢（db∈[-1,1]，中性 0）
        neg = db < 0
        v_comp = np.clip(v_new * (1.0 + db), 0.0, 1.0)          # δB<0：乘法压缩
        v_white = np.clip(v_new + db * (1.0 - v_new), 0.0, 1.0)  # δB>0：向白靠拢
        v_new = np.where(neg, v_comp, v_white)
    else:   # 'add'（默认）：加性
        v_new = np.clip(v_new + db, 0.0, 1.0)
    # ---- H：平移 360° 归一（始终加性） ----
    h_new = (h + dh * 360.0) % 360.0
    out = np.stack([h_new, s_new, v_new], axis=-1)
    return _wrap(orig, out)


if __name__ == '__main__':
    # 冒烟测试：标量 / 数组 / 除0 / clamp 各覆盖一例
    print('标量: adjust_hsv((20.0, 0.75, 0.8), 0.2, 0.3, 0.25) =',
          adjust_hsv((20.0, 0.75, 0.8), 0.2, 0.3, 0.25))
    print('标量: adjust_hsv((0.0, 0.0, 0.5), delta_b=0.3)    =',
          adjust_hsv((0.0, 0.0, 0.5), delta_b=0.3))
    print('数组: adjust_hsv(arr, 0.1, 0.2, 0.15) 形状 =',
          adjust_hsv(np.array([[20.0, 0.75, 0.8], [0.0, 0.0, 0.0],
                               [120.0, 1.0, 1.0], [300.0, 0.5, 0.2]]), 0.1, 0.2, 0.15).shape)
    # Contrast（gain_c）乘性作用于 V，db 仍加性
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, delta_b=0.1) =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, delta_b=0.1))
    # mode_c：三种对比度增益参考点
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c="zero") =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c='zero'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c="mid")   =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c='mid'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=0.5, mode_c="both") =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=0.5, mode_c='both'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c="both") =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c='both'))
    # mode_b：delta_b 乘性增益（默认加性）
    print('标量: adjust_hsv((20.0, 0.5, 0.5), delta_b=1.5, mode_b="mul") =',
          adjust_hsv((20.0, 0.5, 0.5), delta_b=1.5, mode_b='mul'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), delta_b=0.7, mode_b="mul") =',
          adjust_hsv((20.0, 0.5, 0.5), delta_b=0.7, mode_b='mul'))
    # mode_b='mulKeepMin'：调小保底旧 m 且 S 不变（v=0.5,s=0.5 -> m=0.25）
    print('标量: adjust_hsv((20.0, 0.5, 0.5), delta_b=0.5, mode_b="mulKeepMin") =',
          adjust_hsv((20.0, 0.5, 0.5), delta_b=0.5, mode_b='mulKeepMin'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), delta_b=0.0, mode_b="mulKeepMin") =',
          adjust_hsv((20.0, 0.5, 0.5), delta_b=0.0, mode_b='mulKeepMin'))
    # S 乘性模式（仅 S 受 mode 影响）
    print('标量: adjust_hsv((20.0, 0.5, 0.5), delta_s=1.5, mode="mul") =',
          adjust_hsv((20.0, 0.5, 0.5), delta_s=1.5, mode='mul'))
    print('标量: adjust_hsv((0.0, 0.0, 0.5), delta_s=3.0, mode="mul") =',
          adjust_hsv((0.0, 0.0, 0.5), delta_s=3.0, mode='mul'))
    # mode='negmulposrat'：ds<0 乘性压缩 / ds>0 向全饱和靠拢（ds=-1 灰、ds=1 全饱和）
    print('标量: adjust_hsv((20.0, 0.6, 0.5), delta_s=-1.0, mode="negmulposrat") =',
          adjust_hsv((20.0, 0.6, 0.5), delta_s=-1.0, mode='negmulposrat'))
    print('标量: adjust_hsv((20.0, 0.6, 0.5), delta_s=1.0, mode="negmulposrat") =',
          adjust_hsv((20.0, 0.6, 0.5), delta_s=1.0, mode='negmulposrat'))
    print('标量: adjust_hsv((20.0, 0.6, 0.5), delta_s=0.5, mode="negmulposrat") =',
          adjust_hsv((20.0, 0.6, 0.5), delta_s=0.5, mode='negmulposrat'))
    print('标量: adjust_hsv((20.0, 0.6, 0.5), delta_s=-0.5, mode="negmulposrat") =',
          adjust_hsv((20.0, 0.6, 0.5), delta_s=-0.5, mode='negmulposrat'))
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=0.5, mode="negmulposrat", tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=0.5, mode='negmulposrat', tolerance_s=0.05))
    # tolerance_s：S<阈值 的像素不放大（增色），缩小（减色）仍允许
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=0.3, tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=0.3, tolerance_s=0.05))
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=-0.1, tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=-0.1, tolerance_s=0.05))
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=2.0, mode="mul", tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=2.0, mode='mul', tolerance_s=0.05))
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=0.5, mode="mul", tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=0.5, mode='mul', tolerance_s=0.05))
    # mode_c='tanslant'：c∈[-1,1]，tan 映射增益（c=0 恒等 / c=1 极强 / c=-1 压平）
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=1.0, mode_c="tanslant") =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=1.0, mode_c='tanslant'))
    print('标量: adjust_hsv((20.0, 0.5, 0.7), gain_c=1.0, mode_c="tanslant") =',
          adjust_hsv((20.0, 0.5, 0.7), gain_c=1.0, mode_c='tanslant'))
    print('标量: adjust_hsv((20.0, 0.5, 0.3), gain_c=1.0, mode_c="tanslant") =',
          adjust_hsv((20.0, 0.5, 0.3), gain_c=1.0, mode_c='tanslant'))
    print('标量: adjust_hsv((20.0, 0.5, 0.7), gain_c=-1.0, mode_c="tanslant") =',
          adjust_hsv((20.0, 0.5, 0.7), gain_c=-1.0, mode_c='tanslant'))
    # mode_b='negmulposrat'：db<0 乘性压缩 / db>0 向白靠拢（db=-1 纯黑、db=1 纯白）
    print('标量: adjust_hsv((20.0, 0.5, 0.6), delta_b=-1.0, mode_b="negmulposrat") =',
          adjust_hsv((20.0, 0.5, 0.6), delta_b=-1.0, mode_b='negmulposrat'))
    print('标量: adjust_hsv((20.0, 0.5, 0.6), delta_b=1.0, mode_b="negmulposrat") =',
          adjust_hsv((20.0, 0.5, 0.6), delta_b=1.0, mode_b='negmulposrat'))
    print('标量: adjust_hsv((20.0, 0.5, 0.6), delta_b=0.5, mode_b="negmulposrat") =',
          adjust_hsv((20.0, 0.5, 0.6), delta_b=0.5, mode_b='negmulposrat'))
    print('标量: adjust_hsv((20.0, 0.5, 0.6), delta_b=-0.5, mode_b="negmulposrat") =',
          adjust_hsv((20.0, 0.5, 0.6), delta_b=-0.5, mode_b='negmulposrat'))
    # adjust_rgb：中性恒等 / S 灰阶混合 / H 灰色轴旋转 / tanslant / negmulposrat
    _ar = np.array([0.2, 0.5, 0.8], np.float32)
    print('adjust_rgb 中性恒等 =', adjust_rgb(_ar))
    print('adjust_rgb S=0（纯灰） =', adjust_rgb(np.array([1.0, 0.0, 0.0], np.float32), delta_s=0.0))
    print('adjust_rgb H=120（红->绿） =', adjust_rgb(np.array([1.0, 0.0, 0.0], np.float32), angle_deg=120.0))
    print('adjust_rgb TanSlant c=1（v>0.5->1） =', adjust_rgb(np.array([0.7, 0.7, 0.7], np.float32), mode_c='tanslant', gain_c=1.0))
    print('adjust_rgb NegMulPosRat db=-1（纯黑） =', adjust_rgb(np.array([0.6, 0.3, 0.1], np.float32), mode_b='negmulposrat', delta_b=-1.0))
    print('adjust_rgb NegMulPosRat db=1（纯白） =', adjust_rgb(np.array([0.6, 0.3, 0.1], np.float32), mode_b='negmulposrat', delta_b=1.0))
    try:
        adjust_hsv((0.0, 0.0, 0.5), mode='bad')
    except ValueError as exc:
        print('非法 mode 抛 ValueError:', exc)
    # hsv_to_rgb 冒烟：六经典色 / 灰色 / 数组 / 往返
    print('标量: hsv_to_rgb((300.0, 1.0, 1.0))         =', hsv_to_rgb((300.0, 1.0, 1.0)))
    print('标量: hsv_to_rgb((0.0, 0.0, 0.5))           =', hsv_to_rgb((0.0, 0.0, 0.5)))
    print('数组: hsv_to_rgb(arr) 形状 =',
          hsv_to_rgb(np.array([[0.0, 1.0, 1.0], [120.0, 0.5, 1.0],
                               [240.0, 1.0, 0.5], [60.0, 0.0, 0.5]])).shape)
    r0 = (0.8, 0.4, 0.2)
    h0 = rgb_to_hsv(r0)
    r1 = hsv_to_rgb(h0)
    print(f'往返: rgb{r0} -> hsv({h0[0]:.4f},{h0[1]:.4f},{h0[2]:.4f}) -> '
          f'{tuple(round(x, 6) for x in r1)}，max|Δ|={max(abs(a - b) for a, b in zip(r0, r1)):.2e}')

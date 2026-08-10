"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : hsv_adjust.py
Author      : vance.wu@rock-chips.com
Date        : 2026-08-05
Description : RGB <=> HSV 转换与 V/S/H 加性偏置调整（对应 run_csc_note.md "RGB的HSV调整特点总结" 节）
"""

import numpy as np


def _to_rgb(rgb):
    """输入 (r,g,b) / (...,3) -> float64 数组，clamp [0,1]。"""
    arr = np.asarray(rgb, dtype=np.float64)
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
    h = np.where(mx == r, 60.0 * (((g - b) / c_safe) % 6), h)
    h = np.where(mx == g, 60.0 * ((b - r) / c_safe + 2), h)
    h = np.where(mx == b, 60.0 * ((r - g) / c_safe + 4), h)
    h = (h + 360.0) % 360.0                                       # h ∈ [0,360)
    if _is_scalar_rgb(orig):
        return float(h), float(s), float(v)
    return h, s, v


def adjust_hsv(rgb, delta_v=None, delta_s=None, delta_h=None):
    """V/S/H 加性偏置调整（合并单函数，一次 rgb_to_hsv，单次遍历）。
    按 V -> S -> H 顺序执行；delta_v/delta_s ∈ [-1,1]，delta_h ∈ [-0.5,0.5]（0.5=180°）。
    语义：S=0（灰色/黑色）像素 V 直接赋 V'、S/H 保持原样；V/S 调整不改变 H（H 用原始值）。
    只调用一次 rgb_to_hsv；与独立 adjust_v/adjust_s/adjust_h 依次组合结果一致（误差 ~1e-15）。"""
    orig = rgb
    rgb = _to_rgb(rgb)
    dv = 0.0 if delta_v is None else np.clip(np.asarray(delta_v, np.float64), -1.0, 1.0)
    ds = 0.0 if delta_s is None else np.clip(np.asarray(delta_s, np.float64), -1.0, 1.0)
    dh = 0.0 if delta_h is None else np.clip(np.asarray(delta_h, np.float64), -0.5, 0.5)
    h_deg, s, v = rgb_to_hsv(rgb)                     # 一次转换（V/S 不改变 H）
    gray = s == 0
    # ---- V：非灰按 k 缩放；灰/黑直接赋 V' ----
    v_new = np.clip(v + dv, 0.0, 1.0)
    denom = np.where(gray, 1.0, v)                    # 除0保护
    k = (v_new / denom)[..., None]
    v_out = rgb * k
    v_out = np.where(gray[..., None], v_new[..., None], v_out)   # S=0 直接赋 V'
    # ---- S：非灰 S'=clamp(S+ds)；灰色保持 V 步结果（非原始 rgb） ----
    s_new = np.clip(s + ds, 0.0, 1.0)
    s_safe = np.where(gray, 1.0, s)                   # 除0保护
    kk = (s_new / s_safe)[..., None]
    m = (v_new * (1 - s))[..., None]
    m_new = (v_new * (1 - s_new))[..., None]
    s_out = m_new + kk * (v_out - m)
    s_out = np.where(gray[..., None], v_out, s_out)   # 灰色保持 V 步结果
    # ---- H：非灰且 S'>0 才调整；H 用原始 h_deg ----
    active = (~gray) & (s_new > 0)                    # S=0 或 S'=0 跳过 H（灰色无 H）
    h_new = (h_deg + dh * 360.0) % 360.0
    m_h = v_new * (1 - s_new)
    M_h = v_new
    seg = np.floor(h_new / 60.0).astype(np.int64) % 6
    f = (h_new - seg * 60) / 60.0
    mid_val = np.where(seg % 2 == 0, m_h + (M_h - m_h) * f, M_h - (M_h - m_h) * f)
    seg_tab = np.array([
        [0, 2, 1], [1, 2, 0], [1, 0, 2],
        [2, 0, 1], [2, 1, 0], [0, 1, 2],
    ])                                    # 每段 [M通道, m通道, 变化通道]，0/1/2=R/G/B
    m_idx = seg_tab[seg, 0]
    m2_idx = seg_tab[seg, 1]
    h_out = np.empty_like(rgb)
    for ch in range(3):
        h_out[..., ch] = np.where(m_idx == ch, M_h,
                                  np.where(m2_idx == ch, m_h, mid_val))
    out = np.where(active[..., None], h_out, s_out)   # 非 active 用 S 步结果
    return _wrap(orig, out)


if __name__ == '__main__':
    # 冒烟测试：标量 / 数组 / 除0 / clamp 各覆盖一例
    print('标量: adjust_hsv((0.8, 0.4, 0.0), 0.2, 0.3, 0.25) =',
          adjust_hsv((0.8, 0.4, 0.0), 0.2, 0.3, 0.25))
    print('标量: adjust_hsv((0.5, 0.5, 0.5), delta_v=0.3)   =',
          adjust_hsv((0.5, 0.5, 0.5), delta_v=0.3))
    print('数组: adjust_hsv(arr, 0.1, 0.2, 0.15) 形状 =',
          adjust_hsv(np.array([[0.8, 0.4, 0.0], [0.0, 0.0, 0.0],
                               [0.5, 0.5, 0.5], [0.2, 0.6, 0.1]]), 0.1, 0.2, 0.15).shape)

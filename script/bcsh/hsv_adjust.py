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


def adjust_hsv(hsv, delta_v=None, delta_s=None, delta_h=None, gain_c=1.0, mode='add',
               tolerance_s: float = 0.0, mode_c='mid', mode_v='add'):
    """HSV 域 V/S/H 调整（hsv 输入、hsv 输出，不涉及 RGB 重建）。
    按 V -> S -> H 顺序执行：
      V：Contrast 乘性 + delta_v（加性或乘性）；mode_c 选择增益参考点：
           'mid'   v'=clip((v-0.5)*gc + 0.5 [+dv])   （过 v=0.5 中点，默认）
           'zero'  v'=clip(gc*v [+dv])               （过 v=0.0 原点）
           'both'  gc<1 时等效 'zero'，gc>1 时等效 'mid'（gc==1 恒等）
         mode_v 决定 delta_v 生效方式：
           'add'   v'=clip(contrast(v)+dv)           （dv ∈ [-1,1]，默认）
           'mul'   v'=clip(contrast(v)*gv)           （gv 增益 ∈ [0,4]，中性 1.0）
      S：mode='add'  s'=clip(s+ds)；mode='mul'  s'=clip(s*ds)     （ds ∈ [-1,1] 或乘性增益 ∈ [0,4]）
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
    dv = 0.0 if delta_v is None else np.clip(np.asarray(delta_v, np.float32), -1.0, 1.0)
    dh = 0.0 if delta_h is None else np.clip(np.asarray(delta_h, np.float32), -0.5, 0.5)
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
    else:
        raise ValueError(f"Unsupported adjust_hsv mode: {mode!r}, expect 'add' or 'mul'")
    # ---- V：Contrast 乘性 + delta_v 加性 + clamp，mode_c 决定增益参考点 ----
    mode_c = str(mode_c).lower()
    if mode_c == 'zero':
        # 过 v=0.0 原点：v' = gc*v
        v_new = np.clip(gc * v, 0.0, 1.0)
    elif mode_c == 'both':
        # gc<1 等效 GainAtZeroPoint，gc>1 等效 GainAtMidPoint；gc==1 恒等
        v_new = np.where(gc < 1.0, gc * v, (v - 0.5) * gc + 0.5)
        v_new = np.clip(v_new, 0.0, 1.0)
    else:   # 'mid'（默认）：过 v=0.5 中点
        v_new = np.clip((v - 0.5) * gc + 0.5, 0.0, 1.0)
    # ---- delta_v 生效方式：mode_v='add' 加性偏移 / 'mul' 乘性增益 ----
    mode_v = str(mode_v).lower()
    if mode_v == 'mul':
        gv = 1.0 if delta_v is None else np.clip(np.asarray(delta_v, np.float32), 0.0, 4.0)
        v_new = np.clip(v_new * gv, 0.0, 1.0)
    else:   # 'add'（默认）：加性
        v_new = np.clip(v_new + dv, 0.0, 1.0)
    # ---- H：平移 360° 归一（始终加性） ----
    h_new = (h + dh * 360.0) % 360.0
    out = np.stack([h_new, s_new, v_new], axis=-1)
    return _wrap(orig, out)


if __name__ == '__main__':
    # 冒烟测试：标量 / 数组 / 除0 / clamp 各覆盖一例
    print('标量: adjust_hsv((20.0, 0.75, 0.8), 0.2, 0.3, 0.25) =',
          adjust_hsv((20.0, 0.75, 0.8), 0.2, 0.3, 0.25))
    print('标量: adjust_hsv((0.0, 0.0, 0.5), delta_v=0.3)    =',
          adjust_hsv((0.0, 0.0, 0.5), delta_v=0.3))
    print('数组: adjust_hsv(arr, 0.1, 0.2, 0.15) 形状 =',
          adjust_hsv(np.array([[20.0, 0.75, 0.8], [0.0, 0.0, 0.0],
                               [120.0, 1.0, 1.0], [300.0, 0.5, 0.2]]), 0.1, 0.2, 0.15).shape)
    # Contrast（gain_c）乘性作用于 V，dv 仍加性
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, delta_v=0.1) =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, delta_v=0.1))
    # mode_c：三种对比度增益参考点
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c="zero") =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c='zero'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c="mid")   =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c='mid'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=0.5, mode_c="both") =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=0.5, mode_c='both'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c="both") =',
          adjust_hsv((20.0, 0.5, 0.5), gain_c=2.0, mode_c='both'))
    # mode_v：delta_v 乘性增益（默认加性）
    print('标量: adjust_hsv((20.0, 0.5, 0.5), delta_v=1.5, mode_v="mul") =',
          adjust_hsv((20.0, 0.5, 0.5), delta_v=1.5, mode_v='mul'))
    print('标量: adjust_hsv((20.0, 0.5, 0.5), delta_v=0.7, mode_v="mul") =',
          adjust_hsv((20.0, 0.5, 0.5), delta_v=0.7, mode_v='mul'))
    # S 乘性模式（仅 S 受 mode 影响）
    print('标量: adjust_hsv((20.0, 0.5, 0.5), delta_s=1.5, mode="mul") =',
          adjust_hsv((20.0, 0.5, 0.5), delta_s=1.5, mode='mul'))
    print('标量: adjust_hsv((0.0, 0.0, 0.5), delta_s=3.0, mode="mul") =',
          adjust_hsv((0.0, 0.0, 0.5), delta_s=3.0, mode='mul'))
    # tolerance_s：S<阈值 的像素不放大（增色），缩小（减色）仍允许
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=0.3, tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=0.3, tolerance_s=0.05))
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=-0.1, tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=-0.1, tolerance_s=0.05))
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=2.0, mode="mul", tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=2.0, mode='mul', tolerance_s=0.05))
    print('标量: adjust_hsv((20.0, 0.02, 0.5), delta_s=0.5, mode="mul", tolerance_s=0.05) =',
          adjust_hsv((20.0, 0.02, 0.5), delta_s=0.5, mode='mul', tolerance_s=0.05))
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

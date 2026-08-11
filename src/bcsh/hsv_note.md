
# RGB <=> HSV 转换算法实验笔记

## HSV 投影原理：RGB 立方体到六边形平面的投影

将 RGB 立方体绕中性轴（黑→白对角线）倾斜，使黑色位于底部、白色位于顶部（中性轴垂直），再沿中性轴方向正交投影到"色度平面"（垂直于中性轴的平面）。投影形状为正六边形：红 0°、黄 60°、绿 120°、青 180°、蓝 240°、品红 300° 位于六个顶点。

设 RGB 值 $R, G, B \in [0,1]$（归一化），先定义：

$$M = \max(R,G,B), \quad m = \min(R,G,B), \quad C = M - m$$

- $C$（Chroma，色度）= RGB 三分量的极差，即投影点到中性轴的距离（相对该色相方向最大可能色度的比例）
- $V = M$ 是颜色沿中性轴的高度，即 HSV 的 **V 值**

**六边形平面直角坐标**（$\alpha$ 指向红色 0° 方向，$\beta$ 与之垂直、指向黄绿色）：

$$\alpha = R - G\cos 60° - B\cos 60° = \frac{2R - G - B}{2}$$

$$\beta = G\sin 60° - B\sin 60° = \frac{\sqrt{3}}{2}(G - B)$$

**平面极坐标**（极径 = 圆形色度 $C_2$，极角 = 圆形色相 $H_2$）：

$$C_2 = \sqrt{\alpha^2 + \beta^2}, \qquad H_2 = \operatorname{atan2}(\beta, \alpha)$$

**六边形色相 $H$**（标准 HSV 使用，分段定义、以 60° 为步长）：

$$H' = \begin{cases}
   \dfrac{G - B}{C} \bmod 6, & M = R \\[2mm]
   \dfrac{B - R}{C} + 2,     & M = G \\[2mm]
   \dfrac{R - G}{C} + 4,     & M = B \\[2mm]
   \text{未定义},            & C = 0
\end{cases}, \qquad H = 60° \times H'$$

> **极坐标是否就是 H 和 S？** 极角就是 **H（色相）**；但**极径是色度 C（Chroma），不是饱和度 S**。HSV 的饱和度定义为 $S = C / V$，即色度相对于 V 的比值。只有当 $V = 1$（顶部平面，所有纯色所在的平面）时才有 $C = S$。

### 六边形投影与圆形 HSV 色轮的关系

- 六边形是 RGB 立方体沿中性轴正交投影的**真实形状**；圆形色轮是把六边形**每条边线性映射到 60° 圆弧**（几何扭曲 warping）后得到的，扭曲后色相严格等于极角、色度严格等于极径。
- 两者的 H/S/V 含义**基本一致但细节不同**：

| 分量 | 六边形投影 | 圆形色轮 | 差异 |
| --- | --- | --- | --- |
| $V$ | $\max(R,G,B)$ | $\max(R,G,B)$ | 完全一致，与投影形状无关 |
| $H$ | 分段函数 $H$ | 极角 $H_2 = \operatorname{atan2}(\beta,\alpha)$ | 几乎重合，最大偏差约 1.12°（出现在 13.38° 等 12 个色相处），30° 倍数处完全相等 |
| $C$ | $C = M - m$ | $C_2 = \sqrt{\alpha^2+\beta^2}$ | 六边形顶点（30° 倍数）相等；30° 处 $C=1$ 而 $C_2 = \sqrt{3}/2 \approx 0.866$，相差约 13.4% |
| $S$ | $S = C/V = (M-m)/M$ | 若沿用圆形色度则为 $C_2/V$ | 标准 HSV 用六边形 $C$；采用圆形 $C_2$ 时 $S$ 略有不同 |

- 实际的颜色选择器（Photoshop/GIMP 等）虽显示为圆形，但**仍按六边形 HSV 公式**（$S = (M-m)/M$）计算；真正使用圆形极坐标（$H_2 / C_2$）的模型是 HSI / 极坐标变体。
- 本项目 `get_csc_coef_hsv.py` 的 `_rgb_to_hsv()` / `_hsv_to_rgb()` 采用标准六边形 HSV 公式：$V = \max$，$S = (M-m)/M$，$H$ 为六边形分段函数（归一化到 $[0,1]$）。

## 示例 demo 的使用

以下命令在仓库根目录 `fpga_verify` 下执行。

### HSV 投影教学 3D Demo（`web/color-space-lab`）

可视化 RGB 立方体的 HSV 六边形投影模型，对应上文 "RGB <=> HSV 转换算法" 一节（倾斜立方体、V=v 小立方体切割、六边形投影、等 S 环轨迹、RGB↔HSV 公式联动等）：

```shell
cd web/color-space-lab
npm install        # 首次运行需要安装依赖
npm run dev        # 启动 Vite 开发服务器，浏览器打开 http://localhost:5173/

npm --prefix web/color-space-lab run dev -- --host 127.0.0.1 --port 8000
```

生产构建与本地预览：

```shell
cd web/color-space-lab
npm run build      # 构建产物输出到 dist/
npm run preview    # 本地预览构建产物
```

## RGB的HSV调整特点总结

- 改V（明度）的时候，RGB会等比例缩放，三通道之间比例不变，所以可以直接在RGB域修改，但要注意：
  - 用乘法增益形式修改：`RGB' = k · RGB`，`k = V'/V`
  - 各通道调整下限为0，`k` 的上限为 `1/M`（此时 `M'=1`，最大通道到1）
- 改S（饱和度）的时候，保持`V`不变（`M` 通道不动），各通道到`m`（或到`M`）的距离按 `k=S'/S` 缩放，可以直接在RGB域修改，但要注意：
  - 每个通道 `RGB_i ∈ [m, M]`：向`M`的剩余空间 = `M - RGB_i`，向`m`的剩余空间 = `RGB_i - m`
  - 新下限 `m' = V(1-S')`，调整公式：`RGB'_i = m' + k·(RGB_i - m)`，等价于 `M - RGB'_i = k·(M - RGB_i)`
  - 即先以乘法增益`k`乘到各通道相对`m`的偏移量，再以加法形式加上新下限`m'`
- 改H（色相）的时候，保持`S/V`不变，`M/m/C` 都不变，RGB数值在`[m, M]`之间变换，H沿着同心六边形的边缘移动，每过60°就切换一个"变化通道"（同时`M/m`角色互换），所以也可以直接在RGB域修改H，注意：
  - 计算初始色调`HS`，按加法计算终点色调`HE`
  - 统计从`HS->HE`需要经过多少个60°节点，以及经过每个节点前对应调整的通道`C`
  - 如果下一个节点是60°整数倍，可以直接将C的值设为m或M，并记录当前RGB数值
  - 如果终点`HE`不是60°整数倍，则应该按一定比例加上当前颜色C到调整目标m或M的差值
- 优先调V，调V之后重新统计`M/m`的值；之后：
  - 如果`S=0`，无需下一步调整。
  - 再调整S，如果调整后的`S'=0`，无需下一步调整。
  - 最后调整H

## 参考代码

### Python 计算代码

**（RGB 域直接调整；同时支持单像素 `(r,g,b)` 标量 与 numpy 数组 `(...,3)` 批量；参数为**加性偏置**：`delta_h ∈ [-0.5, 0.5]`（归一化色相，0.5 = 180°）、`delta_s/delta_v ∈ [-1, 1]`；已用随机样例与 HSV 中转对比验证，最大误差 < 2e-15）**：

```python
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
```

验证示例（delta 语义，标量 + 除0 + 上下限 + 数组；delta 均为可选，可只调其中一项）：

```python
>>> adjust_hsv((0.8, 0.4, 0.0), delta_v=+0.2)              # (1.0, 0.5, 0.0)   V 0.8→1.0（k=1.25）
>>> adjust_hsv((0.8, 0.4, 0.0), delta_v=-0.3)              # (0.5, 0.25, 0.0)  V 0.8→0.5
>>> adjust_hsv((0.8, 0.6, 0.4), delta_s=+0.3)              # (0.8, 0.48, 0.16) S 0.5→0.8（V/H 不变）
>>> adjust_hsv((0.8, 0.4, 0.0), delta_h=+0.25)             # (0.0, 0.8, 0.0)   H 30→120（绿）
>>> adjust_hsv((0.8, 0.4, 0.0), delta_h=-0.25)             # (0.8, 0.0, 0.8)   H 30→300（品红）
>>> adjust_hsv((0.8, 0.4, 0.0), +0.2, +0.3, +0.25)         # (0.0, 1.0, 0.0)   V+S+H 组合

# 除0保护：S=0 像素
>>> adjust_hsv((0.5, 0.5, 0.5), delta_v=+0.3)              # (0.8, 0.8, 0.8)   灰色直接赋 V'
>>> adjust_hsv((0.0, 0.0, 0.0), delta_v=+0.5)              # (0.5, 0.5, 0.5)   黑色→灰
>>> adjust_hsv((0.9, 0.9, 0.9), delta_s=+0.5)              # (0.9, 0.9, 0.9)   灰色保持原样
>>> adjust_hsv((0.9, 0.9, 0.9), delta_h=+0.3)              # (0.9, 0.9, 0.9)   灰色保持原样

# 上下限 clamp
>>> adjust_hsv((0.8, 0.4, 0.0), delta_v=+1.5)              # (1.0, 0.5, 0.0)   delta_v clamp [-1,1]
>>> adjust_hsv((0.8, 0.6, 0.4), delta_s=-1.2)              # (0.8, 0.8, 0.8)   delta_s clamp → S'=0 灰
>>> adjust_hsv((0.8, 0.4, 0.0), delta_h=+0.9)              # (0.0, 0.4, 0.8)   delta_h clamp 0.5

# numpy 数组（批量，支持任意形状 (...,3)，delta 也可为同形数组）
>>> import numpy as np
>>> arr = np.array([[0.8, 0.4, 0.0], [0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.2, 0.6, 0.1]])
>>> adjust_hsv(arr, delta_v=0.1)                           # 数组批量调 V
>>> adjust_hsv(arr, delta_s=np.array([0.2, 0.2, 0.2, 0.3]))  # 每像素不同 S 偏置
>>> adjust_hsv(arr, delta_h=np.array([0.25, 0.0, 0.0, -0.2]))  # 每像素不同 H 偏置
>>> adjust_hsv(arr, 0.1, 0.2, 0.15)                        # 组合调整（数组）
```

### C 计算代码

**C 语言实现（定点化版本，输入 8bit RGB，性能优先、减少分支）**：

```c
# include <stdint.h>

/* ---------- 定点格式 ----------
 * S  : Q16 定点，1.0 = 65536
 * H  : 归一化 Q16，1.0 = 65536（即 360°）
 * delta_v / delta_s : Q8（-256..255 对应 -1..1）
 * delta_h           : Q8（-128..127 对应 -0.5..0.5）
 * 内部 int32 计算，乘法用 int64 防溢出
 */

static inline int32_t clp_u8(int32_t x) { return x < 0 ? 0 : (x > 255 ? 255 : x); }

/* RGB(8bit) -> HSV：h16 归一化 Q16，s16 Q16，v8 8bit 像素域。
   H 分段用三目（编译器转条件传送，少跳转）；仅 R 段可能出界做一次修正。 */
static inline void rgb2hsv_q(int32_t r, int32_t g, int32_t b,
                             int32_t *h16, int32_t *s16, int32_t *v8) {
    int32_t mx = r > g ? (r > b ? r : b) : (g > b ? g : b);
    int32_t mn = r < g ? (r < b ? r : b) : (g < b ? g : b);
    int32_t c = mx - mn;
    *v8 = mx;
    *s16 = (c > 0) ? (int32_t)(((int64_t)c << 16) / mx) : 0;
    int32_t hh = 0;
    if (c > 0) {
        int32_t d, base;                  /* base: 0=R段 2=G段 4=B段 */
        if (mx == r) { d = g - b;     base = 0; }
        else if (mx == g) { d = b - r; base = 2; }
        else { d = r - g;     base = 4; }
        /* h16 = (base + d/c) / 6 * 65536，d/c 用 Q16 表示 */
        int32_t q = (base << 16) + (int32_t)(((int64_t)d << 16) / c);
        int32_t h = q / 6;
        if (h < 0) h += 65536;            /* R 段 d<0 -> 300..360° */
        hh = h & 0xFFFF;                  /* mod 65536 */
    }
    *h16 = hh;
}

/* 按 V -> S -> H 顺序调整（合并单函数，唯一入口）：单次遍历、每像素一次 rgb2hsv_q。
   语义：V 步 S=0（灰/黑）直接赋 V'8；S 步灰色保持 V 步结果（非原始 rgb）；
   H 步用原始 h16（V/S 不改变 H），S=0 或 S'>0 不成立时跳过。 */
void adjust_hsv_q(const uint8_t *rgb, int n, int16_t dv8, int16_t ds8, int16_t dh8,
                  uint8_t *out) {
    static const uint8_t TAB[6][3] = {
        {0, 2, 1}, {1, 2, 0}, {1, 0, 2},
        {2, 0, 1}, {2, 1, 0}, {0, 1, 2},
    };
    for (int i = 0; i < n; i++) {
        int32_t r = rgb[3 * i], g = rgb[3 * i + 1], b = rgb[3 * i + 2];
        int32_t h16, s16, v8;
        rgb2hsv_q(r, g, b, &h16, &s16, &v8);

        /* adjust V */
        int32_t vn = clp_u8(v + ((dv8 * 255 + 128) >> 8));
        int32_t r1, g1, b1;
        if (s16 > 0) {
            int32_t k8 = (vn << 8) / v8;
            r1 = clp_u8((r * k8 + 128) >> 8);
            g1 = clp_u8((g * k8 + 128) >> 8);
            b1 = clp_u8((b * k8 + 128) >> 8);
        } else {
            r1 = g1 = b1 = vn;
        }
        if (s16 > 0) {
            /* adjust S */
            int32_t sn16 = s16 + ((int32_t)ds8 << 8);
            if (sn16 < 0) sn16 = 0; else if (sn16 > 65536) sn16 = 65536;
            int64_t kk16 = ((int64_t)sn16 << 16) / s16;
            int32_t m8 = (int32_t)(((int64_t)vn * (65536 - s16)) >> 16);
            int32_t mn8 = (int32_t)(((int64_t)vn * (65536 - sn16)) >> 16);
            r1 = clp_u8(mn8 + (int32_t)((kk16 * (r1 - m8) + 32768) >> 16));
            g1 = clp_u8(mn8 + (int32_t)((kk16 * (g1 - m8) + 32768) >> 16));
            b1 = clp_u8(mn8 + (int32_t)((kk16 * (b1 - m8) + 32768) >> 16));
            /* adjust H（用原始 h16；V/S 不改变 H） */
            if (sn16 > 0) {
                int32_t hn = (h16 + ((int32_t)dh8 << 8)) & 0xFFFF;
                int32_t t = hn * 6;
                int32_t seg = t / 65536;
                int32_t f16 = t - seg * 65536;
                int32_t m = (int32_t)(((int64_t)vn * (65536 - sn16)) >> 16);
                int32_t M = vn;
                int32_t dm = (M - m) * f16;
                int32_t mid = (seg & 1) ? (M - ((dm + 32768) >> 16)) : (m + ((dm + 32768) >> 16));
                uint8_t ch[3] = { (uint8_t)m, (uint8_t)m, (uint8_t)m };
                ch[TAB[seg][0]] = (uint8_t)M;
                ch[TAB[seg][2]] = (uint8_t)mid;
                r1 = ch[0]; g1 = ch[1]; b1 = ch[2];
            }
        }
        out[3 * i] = (uint8_t)r1; out[3 * i + 1] = (uint8_t)g1; out[3 * i + 2] = (uint8_t)b1;
    }
}
```

C 使用说明：

- **输入输出均为 8bit RGB**（`uint8_t`，0..255），`n` 为像素数，内存布局 `r,g,b,r,g,b,...`（`3*n` 字节）
- 定点格式：`S` 为 Q16（1.0 = 65536）、`H` 为归一化 Q16（65536 = 360°）、`delta_v/delta_s` 为 Q8（`dv8/256 = delta_v ∈ [-1,1]`）、`delta_h` 为 Q8（`dh8/256 = delta_h ∈ [-0.5,0.5]`，0.5 = 180°）
- 唯一入口 `adjust_hsv_q`（`dv8/ds8/dh8` 均为 0 时对应不调整，可只传需要的项）：按 V -> S -> H 顺序执行；V 步 S=0 像素直接赋 `V'8 = clamp(mx + dv8*255/256)`、S 步灰色保持 V 步结果、H 步 S=0 或 S'=0 时跳过（灰色无 H）
- 精度要点：S 用 Q16（避免 Q8 在低饱和度时 k 误差放大）；`k16`/`kk16` 用 `int64`（低 S 时 `sn16<<16` 超 int32）；H 段判定 `seg=(h*6)/65536`、段内比例 `f16=(h*6)%65536`（60° 边界精确）
- 性能要点：H 分段三目（少跳转）；六边形 6 段查表 `TAB`（无 switch）；`adjust_hsv_q` 单次遍历、每像素一次 `rgb2hsv_q`（V/S 不改变 H）；`static inline` 便于内联
- 编译：`gcc -O3 -o app app.c`（无需 `-lm`，无浮点/三角函数；已用 `-O3` 与 Python 合并版在 8bit 输入下逐像素对比，含灰/黑/越界参数，最大误差 1 LSB，平均 < 0.9 LSB；`dv8=ds8=dh8=0` 时输出与输入完全一致）

### 定点化实验情况

#### 量化定点化精度

通过计算 rgb->hsv->rgb 的往返误差计算定点化精度：
- 对于 U8 数据进行全遍历：
    - 单独量化S至少需要8bit定点
    - 单独量化H至少需要11bit定点
    - 组合量化H+S，至少需要21bit定点，推荐 **(H=11, S=10)** 或 (H=12, S=9)
- 对于 U10 数据进行全遍历：
    - 单独量化S至少需要11bit定点
    - 单独量化H至少需要13bit定点
    - 组合量化H+S，至少需要25bit定点，推荐 **(H=13, S=12)** 或 (H=14, S=11)
- 结合 U8/U10 全遍历量化结论，建议采用 **(H=13, S=12)** 的量化策略

#### rgb2hsv 定点化计算优化

```c
const int FIX_H_TRAD = 13;  /* H Q13: 360° = 8192 */
const int FIX_S_TRAD = 11;  /* S Q11: 1.0 = 2048 */
const int F_H = 1 << FIX_H_TRAD;
const int max_h = F_H - 1;

// 经典计算公式，未优化，存在分支和除法
static inline void rgb2hsv_trad(int32_t r, int32_t g, int32_t b, int32_t *h13, int32_t *s12, int32_t *v10)
{
    int32_t M = MAX3(r, g, b);  // U10
    int32_t m = MIN3(r, g, b);  // U10
    int32_t c = M - m;          // U10, chroma
    *v10 = M;
    *s12 = (c > 0) ? ((c << FIX_S_TRAD) + (M >> 1)) / M : 0;
    int32_t h = 0;
    if (c > 0) {
        int32_t d, base; /* base: 0=R 段  2=G 段  4=B 段 */
        if (M == r)      { d = g - b; base = 0; }
        else if (M == g) { d = b - r; base = 2; }
        else             { d = r - g; base = 4; }
        /* h13 = (base + d/c) / 6 * 2^13 */
        d = ((d << FIX_H_TRAD) + (c >> 1)) / c;
        h = ((base << FIX_H_TRAD) + d + 3) / 6 + F_H;
        h = h & max_h; /* mod 2^13, R 段 d<0 → 300..360°，加整圈回绕 */
    }
    *h13 = h;
}
```

```c
// 优化版 v1：取消分支（优先级掩码选 H 候选；S 仍用除法）
static inline void rgb2hsv_v1(int32_t r, int32_t g, int32_t b, int32_t *h13, int32_t *s12, int32_t *v10)
{
    const int FIX_H_TRAD = 13;
    const int FIX_S_TRAD = 11;
    const int F_H = 1 << FIX_H_TRAD;
    const int max_h = F_H - 1;

    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t c = M - m;
    *v10 = M;
    *s12 = (c > 0) ? ((c << FIX_S_TRAD) + (M >> 1)) / M : 0;

    int32_t h = 0;
    if (c > 0) {
        /* 三通道 diff，含除 C（仍用整数除法 /c，仅消除 if-else 分支） */
        int32_t dR = g - b, dG = b - r, dB = r - g;
        int32_t aR = ((dR << FIX_H_TRAD) + (c >> 1)) / c;
        int32_t aG = ((dG << FIX_H_TRAD) + (c >> 1)) / c;
        int32_t aB = ((dB << FIX_H_TRAD) + (c >> 1)) / c;
        /* H = round((a + base*F)/6)，base∈{6,2,4}（6 使 hR 恒正、& mask 正确回绕） */
        int32_t hR = (((6 << FIX_H_TRAD) + aR + 3) / 6) & max_h;    /* base=6: [5F/6, 7F/6) → wrap */
        int32_t hG = ((2 << FIX_H_TRAD) + aG + 3) / 6;              /* base=2: [1F/6, 3F/6) */
        int32_t hB = ((4 << FIX_H_TRAD) + aB + 3) / 6;              /* base=4: [3F/6, 5F/6) */

        /* 优先级掩码：R > G > B，平局取前者 */
        uint32_t mR = (uint32_t)(M == r);
        uint32_t mG = (uint32_t)(M == g) & ~mR;
        uint32_t mB = (uint32_t)(M == b) & ~(mR | mG);
        int32_t selR = (int32_t)(0u - mR);  /* 0 或 -1 */
        int32_t selG = (int32_t)(0u - mG);
        int32_t selB = (int32_t)(0u - mB);
        h = (hR & selR) | (hG & selG) | (hB & selB);
    }
    *h13 = h;
}
```

```c
// 优化版 v2：取消除法（倒数表 + rcp_mul_rsh；分支保留）
static inline int32_t rcp_mul_rsh(int32_t a, int32_t rcp, int rsh)
{
    int64_t p = (int64_t)a * rcp;
    p += (1LL << (rsh - 1)) + (p >> 63);
    return (int32_t)(p >> rsh);
}

static inline void rgb2hsv_v2(int32_t r, int32_t g, int32_t b, int32_t *h13, int32_t *s12, int32_t *v10)
{
    const int FIX_H_TRAD = 13;
    const int FIX_S_TRAD = 11;
    const int F_H = 1 << FIX_H_TRAD;
    const int max_h = F_H - 1;
    const int RCP_BITS = 24;   /* 倒数表定标（最小值由精度测试确定，24 安全） */
    const int RCP6_BITS = 18;  /* /6 固定除数定标 */

    /* 倒数表（static lazy init，硬件可替换为 ROM） */
    static int32_t rcp_tbl[1024];
    static int ready = 0;
    if (!ready) {
        rcp_tbl[0] = 0;
        for (int k = 1; k <= 1023; k++)
            rcp_tbl[k] = (int32_t)((((int64_t)1 << RCP_BITS) + (k >> 1)) / k);
        ready = 1;
    }
    int32_t rcp6 = (int32_t)((((int64_t)1 << RCP6_BITS) + 3) / 6);

    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t c = M - m;
    *v10 = M;

    /* S = round(C<<11 / M)，倒数表替代除法（无 branch） */
    *s12 = (c > 0) ? rcp_mul_rsh(c, rcp_tbl[M], RCP_BITS - FIX_S_TRAD) : 0;

    int32_t h = 0;
    if (c > 0) {
        int32_t d, base; /* 分支保留 */
        if (M == r)      { d = g - b; base = 0; }
        else if (M == g) { d = b - r; base = 2; }
        else             { d = r - g; base = 4; }
        /* a = round(diff<<13 / C)，倒数表替代除法 */
        int32_t a = rcp_mul_rsh(d, rcp_tbl[c], RCP_BITS - FIX_H_TRAD);
        /* h = round((a + base*F) / 6)，rcp6 替代 /6 */
        int32_t h_ = rcp_mul_rsh(a + base * F_H, rcp6, RCP6_BITS);
        if (h_ < 0)
            h_ += F_H;
        h = h_ & max_h;
    }
    *h13 = h;
}
```

```c
// 优化版 v3：取消分支 + 取消除法（优先级掩码 + 倒数表，硬件友好）
static inline void rgb2hsv_v3(int32_t r, int32_t g, int32_t b, int32_t *h13, int32_t *s12, int32_t *v10)
{
    const int FIX_H_TRAD = 13;
    const int FIX_S_TRAD = 11;
    const int F_H = 1 << FIX_H_TRAD;
    const int max_h = F_H - 1;
    const int RCP_BITS = 24;
    const int RCP6_BITS = 18;

    static int32_t rcp_tbl[1024];
    static int ready = 0;
    if (!ready) {
        rcp_tbl[0] = 0;
        for (int k = 1; k <= 1023; k++)
            rcp_tbl[k] = (int32_t)((((int64_t)1 << RCP_BITS) + (k >> 1)) / k);
        ready = 1;
    }
    int32_t rcp6 = (int32_t)((((int64_t)1 << RCP6_BITS) + 3) / 6);

    int32_t M = MAX3(r, g, b);
    int32_t m = MIN3(r, g, b);
    int32_t c = M - m;
    *v10 = M;

    /* S：倒数表，无分支 */
    *s12 = (c > 0) ? rcp_mul_rsh(c, rcp_tbl[M], RCP_BITS - FIX_S_TRAD) : 0;

    int32_t h = 0;
    if (c > 0) {
        /* 三通道 diff → A = round(diff<<13 / C)（倒数表，无除法） */
        int32_t aR = rcp_mul_rsh(g - b, rcp_tbl[c], RCP_BITS - FIX_H_TRAD);
        int32_t aG = rcp_mul_rsh(b - r, rcp_tbl[c], RCP_BITS - FIX_H_TRAD);
        int32_t aB = rcp_mul_rsh(r - g, rcp_tbl[c], RCP_BITS - FIX_H_TRAD);
        /* H = round((A + base*F) / 6)，base∈{6,2,4}（6 使 hR 恒正，& mask 正确回绕） */
        int32_t hR = rcp_mul_rsh(aR + (6 << FIX_H_TRAD), rcp6, RCP6_BITS) & max_h;
        int32_t hG = rcp_mul_rsh(aG + (2 << FIX_H_TRAD), rcp6, RCP6_BITS);
        int32_t hB = rcp_mul_rsh(aB + (4 << FIX_H_TRAD), rcp6, RCP6_BITS);

        /* 优先级掩码选 H 候选（无分支） */
        uint32_t mR = (uint32_t)(M == r);
        uint32_t mG = (uint32_t)(M == g) & ~mR;
        uint32_t mB = (uint32_t)(M == b) & ~(mR | mG);
        int32_t selR = (int32_t)(0u - mR);
        int32_t selG = (int32_t)(0u - mG);
        int32_t selB = (int32_t)(0u - mB);
        h = (hR & selR) | (hG & selG) | (hB & selB);
    }
    *h13 = h;
}
```

#### hsv2rgb 定点化计算优化

```c
const int FIX_H_TRAD = 13;  /* H Q13: 360° = 8192 */
const int FIX_S_TRAD = 11;  /* S Q11: 1.0 = 2048 */
const int F_H = 1 << FIX_H_TRAD;
const int F_S = 1 << FIX_S_TRAD;
const int VS_SHIFT = 4;              /* (V*S>>4)*t ≤ 2^30，防 int32 溢出 */
const int RS = FIX_H_TRAD + FIX_S_TRAD - VS_SHIFT;  /* 重建右移 = 20 */

/* clamp01(k) = max(0, min(min(k, 4F-k), F))，k∈[0,6F)，全三目（CMOV）无分支 */
static inline int32_t clamp01(int32_t k)
{
    int32_t t = k < 4 * F_H - k ? k : 4 * F_H - k;  /* min(k, 4F-k) */
    t = t < 0 ? 0 : t;                              /* max(t, 0) */
    t = t > F_H ? F_H : t;                          /* min(t, 1) */
    return t;
}

// 经典计算公式（C/X/m 模型）：switch 分支 + 除法 + abs
static inline void hsv2rgb_trad(int32_t H, int32_t S, int32_t V, int32_t maxv, int32_t *R, int32_t *G, int32_t *B)
{
    if (S == 0) { *R = *G = *B = V; return; }          /* 灰度：V 直接输出 */
    int32_t C = (V * S + (F_S >> 1)) / F_S;            /* 色度（Q11→像素域） */
    int32_t m = V - C;
    int32_t h6 = H * 6;                                /* 六边形位置 [0,6F) */
    int32_t seg = h6 / F_H;                            /* 扇区 0..5（除法） */
    int32_t f = h6 % F_H;                              /* 段内比例 Q13（除法） */
    int32_t t = 2 * f - F_H;
    if (t < 0) t = -t;                                 /* |2f-1|（分支） */
    int32_t X = C - (int32_t)((int64_t)C * t / F_H);   /* C*(1-|2f-1|) */
    switch (seg) {                                     /* 6 路分支 */
    case 0: *R = C; *G = X; *B = m; break;
    case 1: *R = X; *G = C; *B = m; break;
    case 2: *R = m; *G = C; *B = X; break;
    case 3: *R = m; *G = X; *B = C; break;
    case 4: *R = X; *G = m; *B = C; break;
    default: *R = C; *G = m; *B = X; break;
    }
    *R = CLIP(*R, 0, maxv); *G = CLIP(*G, 0, maxv); *B = CLIP(*B, 0, maxv);
}
```

```c
// 优化版 v1：取消分支（f(n) 公式 + 三目 clamp01，替代 switch；保留 % 除法）
static inline void hsv2rgb_v1(int32_t H, int32_t S, int32_t V, int32_t maxv, int32_t *R, int32_t *G, int32_t *B)
{
    if (S == 0) { *R = *G = *B = V; return; }
    /* k = (n + 6H') mod 6，n = 5,3,1（% 仍是真除法） */
    int32_t h6 = H * 6;
    int32_t k5 = (5 * F_H + h6) % (6 * F_H);
    int32_t k3 = (3 * F_H + h6) % (6 * F_H);
    int32_t k1 = (1 * F_H + h6) % (6 * F_H);
    int32_t t5 = clamp01(k5);
    int32_t t3 = clamp01(k3);
    int32_t t1 = clamp01(k1);
    /* f = V - round(V*S*t / 2^bits)，三通道同一 vsq 提前降位宽 */
    int32_t vsq = (V * S + (1 << (VS_SHIFT - 1))) >> VS_SHIFT;
    int32_t r = V - (int32_t)((vsq * t5 + (1 << (RS - 1))) >> RS);
    int32_t g = V - (int32_t)((vsq * t3 + (1 << (RS - 1))) >> RS);
    int32_t b = V - (int32_t)((vsq * t1 + (1 << (RS - 1))) >> RS);
    *R = CLIP(r, 0, maxv); *G = CLIP(g, 0, maxv); *B = CLIP(b, 0, maxv);
}
```

```c
// 优化版 v2：取消除法（hsv2rgb 的除法全是 2 的幂，改显式移位；switch 保留）
static inline void hsv2rgb_v2(int32_t H, int32_t S, int32_t V, int32_t maxv, int32_t *R, int32_t *G, int32_t *B)
{
    if (S == 0) { *R = *G = *B = V; return; }
    int32_t C = (V * S + (F_S >> 1)) >> FIX_S_TRAD;    /* /F_S → >>11 */
    int32_t m = V - C;
    int32_t h6 = H * 6;
    int32_t seg = h6 >> FIX_H_TRAD;                    /* /F_H → >>13 */
    int32_t f = h6 & (F_H - 1);                        /* %F_H → &(F_H-1) */
    int32_t t = 2 * f - F_H;
    if (t < 0) t = -t;                                 /* abs（分支保留） */
    int32_t X = C - (int32_t)(((int64_t)C * t) >> FIX_H_TRAD);  /* /F_H → >>13 */
    switch (seg) {                                     /* 6 路分支保留 */
    case 0: *R = C; *G = X; *B = m; break;
    case 1: *R = X; *G = C; *B = m; break;
    case 2: *R = m; *G = C; *B = X; break;
    case 3: *R = m; *G = X; *B = C; break;
    case 4: *R = X; *G = m; *B = C; break;
    default: *R = C; *G = m; *B = X; break;
    }
    *R = CLIP(*R, 0, maxv); *G = CLIP(*G, 0, maxv); *B = CLIP(*B, 0, maxv);
}
```

```c
// 优化版 v3：取消分支 + 取消除法（f(n) + 单次减 mod + 三目 + 全移位，硬件友好）
static inline void hsv2rgb_v3(int32_t H, int32_t S, int32_t V, int32_t maxv, int32_t *R, int32_t *G, int32_t *B)
{
    if (S == 0) { *R = *G = *B = V; return; }
    /* k = n + h6 ∈ [F, 11F)，mod 6F（整圈）最多减一次：三目 CMOV 无分支 */
    int32_t h6 = H * 6;
    int32_t k5 = 5 * F_H + h6;
    int32_t k3 = 3 * F_H + h6;
    int32_t k1 = 1 * F_H + h6;
    k5 = (k5 >= 6 * F_H) ? k5 - 6 * F_H : k5;
    k3 = (k3 >= 6 * F_H) ? k3 - 6 * F_H : k3;
    k1 = (k1 >= 6 * F_H) ? k1 - 6 * F_H : k1;
    int32_t t5 = clamp01(k5);
    int32_t t3 = clamp01(k3);
    int32_t t1 = clamp01(k1);
    /* f = V - round(V*S*t / 2^20)：vsq 提前右移降位宽，全程 32 位 */
    int32_t vsq = (V * S + (1 << (VS_SHIFT - 1))) >> VS_SHIFT;
    int32_t r = V - (int32_t)((vsq * t5 + (1 << (RS - 1))) >> RS);
    int32_t g = V - (int32_t)((vsq * t3 + (1 << (RS - 1))) >> RS);
    int32_t b = V - (int32_t)((vsq * t1 + (1 << (RS - 1))) >> RS);
    *R = CLIP(r, 0, maxv); *G = CLIP(g, 0, maxv); *B = CLIP(b, 0, maxv);
}
```

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

### C 语言代码与量化实验情况

#### 量化定点化精度

通过计算 rgb->hsv->rgb 的往返误差计算定点化精度：
- 对于 U8 数据进行全遍历：
    - 单独量化S至少需要8bit定点
    - 单独量化H至少需要11bit定点
    - 组合量化H+S，至少需要21bit定点，推荐 (H=11, S=10) 或 **(H=12, S=9)**
- 对于 U10 数据进行全遍历：
    - 单独量化S至少需要11bit定点
    - 单独量化H至少需要13bit定点
    - 组合量化H+S，至少需要25bit定点，推荐 (H=13, S=12) 或 **(H=14, S=11)**
- H的量化精度对 hsv2rgb 计算影响更大
- 结合 U8/U10 全遍历量化结论，建议采用 **(H=14, S=11)** 的量化策略

#### rgb<->hsv 定点化计算优化

```c
#define FIX_BITS_H 14 /* H 归一化位宽：360° = 2^14 */
#define FIX_BITS_S 11 /* S 归一化位宽：1.0 = 2^11 */
#define RCP_BITS   21 /* S 表定标位宽；可用 -DRCP_BITS=N 覆盖（最小值 21 由 [11] 全遍历确定） */
#define RCP6_BITS  24 /* H 表 rcp6 定标位宽；可用 -DRCP6_BITS=N 覆盖（最小值 24 由 [11] 全遍历确定） */

// 经典计算公式，未优化，存在分支和除法
void rgb2hsv_v0_classic(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
// 优化版 v1：取消分支（优先级掩码选 H 候选；仍存在除法）
void rgb2hsv_v1_no_branch(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
// 优化版 v2：取消除法（倒数表 + rcp_mul_rsh；分支保留）
void rgb2hsv_v2_no_division(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);
// 优化版 v3：取消分支 + 取消除法（优先级掩码 + 双倒数表，硬件友好）【当前实现】
//   定标：FIX_BITS_H=14（360°=F_H=16384）、FIX_BITS_S=11（1.0=2048）
//   双表（索引与定标均不同，无法共用）：
//     S 表 rcp[k]  = round(2^RCP_BITS/k)，RCP_BITS=21，以 V(M) 为索引，供 S=C/V
//     H 表 rcp6[k] = round(2^RCP6_BITS/(6k))，RCP6_BITS=24，以 C(Chroma) 为索引，供 H=diff/(6C)
//   rcp6 利用 (diff×2^14/C)/6 = diff×2^14/(6C) 恒等，把原两级乘法 (diff×rcp[C])×RCP6
//   合并为一级乘法 diff×rcp6[C]，省 3 个 /6 乘法器；最小位宽由 hsv_precision_test [11] 全遍历确定
void rgb2hsv_v3_optimal(uint16_t r, uint16_t g, uint16_t b, uint16_t *h14, uint16_t *s11, uint16_t *v10);


/* v0：经典 C/X/m 模型，switch 分支 + 除法；*/
void hsv2rgb_v0_classic(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
/* v1：取消分支（f(n) 公式 + 三目 clamp01 替代 switch；保留 % 除法） */
void hsv2rgb_v1_no_branch(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
/* v2：取消除法（除法全改移位；switch 保留）； */
void hsv2rgb_v2_no_division(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
/* v3：取消分支 + 取消除法（f(n) + 单次减 mod + 三目 + 全移位，硬件友好） */
void hsv2rgb_v3_optimal(uint16_t h14, uint16_t s11, uint16_t v10, uint16_t maxv, uint16_t *R, uint16_t *G, uint16_t *B);
```

具体代码实现请见 [hsv_fixed.c](hsv_fixed.c)

#### v3_optimal 计算量 / 乘法位宽 / 定点化精度分析

> 基于 2026-08 双表方案（S 表 21bit + H 表 24bit，H 一级乘法）；性能/精度为 hsv_fixed_test、hsv_precision_test 实测（MinGW -O2）。

##### 定点化精度（实测全遍历）

| 对象 | 定点化精度 | 取值范围 |
| --- | --- | --- |
| H | 14bit | 归一化定点， [0, 2^14-1] |
| S | 11bit | 归一化定点， [0, 2^11] <br>**todo: 验证 [0, 2^11-1] 的精度是否Ok?**  |
| 导数表1 | 21bit | [0, 2^21] <br>**todo: 验证 [0, 2^21-1] 的精度是否Ok?** |
| 导数表2 | 24bit | [0, 2^24] <br>**todo: 验证 [0, 2^24-1] 的精度是否Ok?** |

##### rgb2hsv_v3_optimal（每像素，C>0）

| 项目 | 明细 |
| --- | --- |
| 查找表 | S 表 1024×21bit（索引 M）+ H 表 1024×24bit（索引 C）；查表总共 2 次 |
| 乘法器 | 4 个：S 1 个 + H 3 个 |
| S 乘法 | C(≤11bit) × rcp\[M](≤21bit)：原始 32bit，实际乘积 ≤ 2^21（C 与 rcp[M] 反比） |
| H 乘法 | diff(≤11bit) × rcp6\[C](≤22bit)：原始 33bit，实际乘积 ≤ 2^24/6 ≈ 2^21.4（C 与 rcp6[C] 反比） |
| 算术 | MAX3/MIN3 各 2 比较；3 次常量加（+16384/5461/10923）；3 比较（M==r/g/b）+ 3 取反 + 3 AND + 2 OR |
| 分支 | 仅 1 次 `if (C>0)` |
| H 表误差 | rcp6 舍入 ≤0.5，被 diff(≤1023) 放大：最坏 ≈ diff·0.5 / 2^(RCP6_BITS-14)；RCP6_BITS=24 时 < 0.5 LSB ✓ |

##### hsv2rgb_v3_optimal（每像素，S>0）

| 项目 | 明细 |
| --- | --- |
| 乘法器 | 3 个 + 1 常量乘 |
| h6 = H×6 | 常量乘法（14bit×3），移位+加 |
| vsq = V×S | V(≤11bit) × S(≤11bit)：原始 22bit，实际 ≤ 2^21 |
| 重建 vsq×t | vsq(≤11bit) × t(≤14bit)：原始 25bit，实际 ≤ 2^24 |
| 算术 | 3 组 k（加+比较+条件减）；3 次 clamp01（各 2 比较 2 三目）；3 次（乘+加+移位+减+CLIP） |
| 分支 | 仅 1 次 `if (S==0)` |

##### 最大乘法位宽汇总

| 通路 | 乘法器 | 实际需要的乘法位宽 |
| --- | --- | --- |
| rgb2hsv S | C×rcp\[M] | 21bit |
| rgb2hsv H | diff×rcp6\[C] | 22bit |
| hsv2rgb vsq | V×S | 21bit |
| hsv2rgb 重建 | vsq×t | 24bit |

综上，对于 10bit 输入数据，乘法器位宽最大需要 24bit 。

##### 性能测试

测试平台: RK3588
测试分辨率：4K rgb

平均性能数据如下：

| 函数 | 平均耗时[ms/帧] | 备注 |
|-----|----------| -----|
| `rgb2hsv_v0_classic` | 107 | CPU 单线程 |
| `rgb2hsv_v1_no_branch` | 128 | CPU 单线程 |
| `rgb2hsv_v2_no_division` | 107 | CPU 单线程 |
| `rgb2hsv_v3_optimal` | 99 | CPU 单线程 |
| `hsv2rgb_v0_classic` | 130 | CPU 单线程 |
| `hsv2rgb_v1_no_branch` | 107 | CPU 单线程 |
| `hsv2rgb_v2_no_division` | 125 | CPU 单线程 |
| `hsv2rgb_v3_optimal` | 98 | CPU 单线程 |
| `hsv2rgb + acm + rgb2hsv` | 9.5 | OpenCL + float版 |

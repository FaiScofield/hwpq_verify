# YUV 色域调色补偿方法研究

## 1. 简述

&emsp;&emsp;在 **YUV 域**直接调色（亮度 B / 对比度 C / 饱和度 S / 色调 H），实现简单、贴近硬件语义。Hisi, MTK 以及 RK 等公司的硬件实现均采用了该方案。

但由于 **YUV 色域大于 RGB 色域**——在 YUV 上调色后数据转回 RGB 时常发生越界，逐通道钳位会破坏 RGB 通道比例，从而产生**色相/饱和度偏移**。

&emsp;&emsp;本文整理：

1. YUV 域调色的基本做法；
2. 色相偏移问题的几何根源；
3. 仿真工具中已实现的补偿方案及其取舍。

## 2. YUV 色域调色（BCSH）的基本做法

### 2.1 处理域与坐标

&emsp;&emsp;处理域统一定义为归一化的 YUV444 planar full-range: $Y,U,V\in[0,1] \quad (Cb,Cr\in[-0.5,0.5])$

色度用去中心化后的 UV 平面极坐标（下文统称为 CbCr 坐标系）： $r=\sqrt{Cb^2+Cr^2},\quad \theta=\text{atan2}(Cr, Cb)\ \in [0°,360°]$

- **B/C**：作用于 $Y$ 通道（luma）；
- **S**：作用于色度极径 $r$（$r$ 或其归一化后的值）；
- **H**：直接旋转极角 $\theta'=(\theta+\delta H)\%360$。

### 2.2 BCSH 调整公式

- **C（Contrast）**，主要以乘法作用于 Y，仿真器支持多种模式，只推荐以下两种：
  - `GainAtMid`: $Y'=\mathrm{clip}((Y-0.5)g_c+0.5)$； 对比度缩放斜率 $[0, \max(g_c)]$
  - `TanSlant` $Y'=\mathrm{clip}((Y-0.5)\tan((c+1)\pi/4)+0.5)$； 对比度缩放斜率 $[0, \infty]$
- **B（Brightness）**，主要以加法作用于 Y：$Y'=\mathrm{clip}(Y+\Delta B)$
- **S（Saturation）**，建议以乘法作用于极径：$S'=\mathrm{clip}(S\cdot g_s)$，可保持对比度变化尺度的一致性
- **H（Hue）**：旋转极角 $\theta'=(\theta+\Delta H)\%360$

## 3. YUV 色域调色的问题与核心原因

### 3.1 问题现象

&emsp;&emsp;在 YCbCr 上调整后，$(Y,\theta,r)$ 可能落到 RGB 色域外；转 RGB 后逐通道钳位 $RGB'_i=\mathrm{clip}(RGB_i)$ 会**独立**改动各通道，破坏六边形色相的判定比例 $t=\frac{mid-min}{max-min}$，于是产生**色相偏移**；同时 $V=\max_i RGB_i$ 被压回 1，**饱和度也随之改变**。

> &emsp;&emsp;:warning: 注意，我们在 YUV 色域上定义的 “色相/饱和度/亮度” 这三个维度的概念其实和 **HSV** 色域定义的概念是不一样的。但由于目前硬件对图像呈现都是基于RGB色域表达的，所以这里我们始终以 RGB 色域对应的“色相/饱和度/亮度”来分析。
>
> &emsp;&emsp;RGB 色域的“色相/饱和度/亮度”表达模型最常见的是 **HSV/HSL** 等这类“圆锥”体模型。这几个模型的“色相”概念都是一样的，“亮度和饱和度”概念互有不同。
>
> &emsp;&emsp;下表给出各模型三参数的定义对比（除 YCbCr 之外统一用 RGB 域表达，记 $M=\max(R,G,B)$，$m=\min(R,G,B)$，$C=M-m$）：
>
> | 模型 | 色相 H | 饱和度 S | 亮度轴 | 取值完备性 |
> | --- | --- | --- | --- | --- |
> | **YCbCr** | CbCr 平面极角 $\theta=\mathrm{atan2}(Cr,Cb)$ | 极径 $r=\sqrt{Cb^2+Cr^2}$（或其归一化） | luma $Y=\mathbf w\cdot(R,G,B)$<br>（BT.709/BT.601$） | 不完备 |
> | **HSV** | 六边形扇区式（60°×6，按 max 通道分扇区） | $S=C/M$ | 明度 $V=M$ | 完备 |
> | **HSL** | ^ | $S=C/(1-\lvert 2L-1\rvert)$ | 亮度 $L=(M+m)/2$ | 完备 |
> | **HCY** | ^ | 色度 $C=(M-m)\cdot$归一化因子（按该色相/亮度可承载的最大色度，Rec.601 luma） | luma $Y=0.299R+0.587G+0.114B$ (BT.601) | 完备 |
> | **HSP** | ^ | $S=C/M$（同 HSV） | 感知亮度 $P=\sqrt{0.299R^2+0.587G^2+0.114B^2}$ | 不完备 |
> | **HSI** | acos 连续式（Maxwell 三角连续角，120° 对称）：$H=\theta\ (B\le G)$，否则 $360^\circ-\theta$ | $S=1-m/I=(I-m)/I$ | 强度 $I=(R+G+B)/3$ | 不完备 |
>
> YCbCr 的色相和 HSV 的色相都是连续的，但色相定义不同；在 HSV 旋转 60° 色相，对应在 YCbCr 中大约只有50°。

### 3.2 核心原因：色域失配 + 逐通道钳位

- YUV 全空间是立方体，合法区域只是其中凸多面体，调色很容易越界；
- 越界后的处理（尤其 `HardClip`）是**逐通道独立**的，不保通道比例 → 必偏色；
- 即使不越界，YCbCr 极坐标与六边形锥坐标的“亮度/饱和度”轴也不对齐（见 §3.4）。

### 3.3 几何模型：矩阵形式、色域边界、V/S 等高线

**矩阵形式（与 CSC 系数矩阵的关系）**：

$$\begin{bmatrix} R \\ G \\ B \end{bmatrix} = \begin{bmatrix} 1 & 0 & 1.5748 \\ 1 & -0.1873 & -0.4681 \\ 1 & 1.8556 & 0 \end{bmatrix} \begin{bmatrix} Y \\ Cb \\ Cr \end{bmatrix} = \begin{bmatrix} Y \\ r \cdot \cos(\theta) \\ r \cdot \sin(\theta) \end{bmatrix}$$

$$\mathbf{RGB}=\underbrace{Y\cdot\mathbf{1}}_{\text{Y 系数列}}+r\cdot\underbrace{\mathbf{M}}_{\mathbf M=\mathbf{Y2R}[:,1:]}\begin{bmatrix}\cos\theta\\\sin\theta\end{bmatrix}=Y\cdot\mathbf{1}+r\cdot\mathbf k(\theta)$$

即 $\mathbf k(\theta)=\mathbf M\cdot\mathbf u(\theta)$，$k_i=a_i\cos\theta+b_i\sin\theta$——$\mathbf k$ 是 CSC 色度系数子矩阵 $\mathbf M$ 作用于单位方向的结果，决定 RGB 三通道的色度增量。

**色域边界极径**：

$$r_{\max}(Y,\theta)=\min\!\Big(\min_{k_i>0}\tfrac{1-Y}{k_i},\ \min_{k_i<0}\tfrac{-Y}{k_i}\Big)$$

即沿方向 $\theta$、luma 为 $Y$ 时，三通道中“最先被顶到 0 或 1”的那张面决定最大允许极径。固定 $Y$ 时，$r_{\max}$ 在 (Cb,Cr) 平面围成的多边形就是 **RGB 立方体在 luma 平面上的截面**，其每一条边对应一张立方体面：

- **暗边**（某通道 $=0$，即 $\min=0$）⇔ $S_{hex}=1$，由 $(-Y)/k_i\ (k_i<0)$ 决定；
- **亮边**（某通道 $=1$，即 $\max=1$）⇔ $V=1$，由 $(1-Y)/k_i\ (k_i>0)$ 决定。

**边数取决于 Y**：BT.709 的 luma 权重 $w=[0.2126,0.7152,0.0722]$，通道 $c$ 的“$c=0$ 面”被切当且仅当 $Y<1-w_c$，“$c=1$ 面”当且仅当 $Y>w_c$。因此截面在三角形/四边形/五边形之间变化（BT.709 下 luma 截面**永远不会是六边形**）。

**V/S 等高线**：$V=\max(RGB)$ 的等高线是闭凸多边形（R/B 主导段轴对齐、G 主导段为对角线）；$S_{hex}=\frac{max-min}{max}$ 的等高线是绕灰轴的闭合星形曲线。二者均非圆——这正是“同一极径 $r$ 在不同角度对应不同六边形 S/V”的几何来源。

### 3.4 只调 S / 只调 H / 只调 Y 的行为

- **只调 S**（$r'=g_s r$，$\theta,Y$ 不变）：$\mathbf{RGB}'=Y+g_s(\mathbf{RGB}-Y)$，所有通道差同乘 $g_s$，**六边形色相严格保持**——与 HSV/HSL/HCY/HSP 的 `ModeMul`、RGB 域 `MixGray` 同属“绕灰轴径向缩放”，故色环变化观感一致。
- **只调 H**（固定 $(Y,r)$ 旋转 $\theta$）：$\max_i k_i(\theta)$ 随角度变化 ⇒ $S_{hex}$ 与 $V$ 都变——YCbCr 极坐标与六边形锥坐标的 S/V 轴不对齐。
- **只调 Y**（固定 $(\theta,r)$）：通道差不变 ⇒ 六边形色相**严格保持**；但 $V$ 变 ⇒ $S_{hex}$ 变；且 $Y\to0$ 或 $Y\to1$ 时 $r_{\max}\to0$，固定 $r$ 越界 → 钳位偏色。

## 4. YUV 色域调色的补偿方案

### 4.1 y2yClipType 统一色域处理策略（保色相优先）

- `HardClip`：$Y,Cb,Cr$ 各自硬钳，不保色相；
- `ClipChroma`：保持 $Y$ 与极角，$r'=\min(r,r_{\max})$，保色相、降饱和；
- `ScaleChromaPix`：$s=\dfrac{r}{r_{\max}(Y,\theta)}\in[0,1]$，保证颜色落在 RGB 色域内，$s$ 为“相对当前 $(Y,\theta)$ 边界”的比例
- `ScaleChromaSec`：$S=r/\text{\_CHROMA\_MAX}$ 全局归一化，`ScaleChromaPix`的优化版本；重建可能越界，越界像素按 `HardClip` 兜底；
- `CompLumaOnly`：保色度调亮度，见 §4.2；
- `CompLumaFirst`：调亮度优先、不足缩色度兜底，见 §4.2。

**y2rClipType（YUV→RGB 转换钳位）**：

- `HardClip`：逐通道硬钳（可能偏色）；
- `SoftClip`：zentone 移植，仅高侧保比例软压缩、低侧硬钳 0（保低侧饱和度，欠饱和像素可能偏色）；
- `ConstHue`：负值钳 0 后等比缩放使 $\max=1$，通道比例不变 ⇒ 保色相。

### 4.2 y2yClipType 的亮度补偿（CompLumaOnly / CompLumaFirst）

- 六边形色相由通道差比例 $t$ 决定，YCbCr 下“保持通道差比例”等价于“保持极角 $\theta$”
- 但 **Y、极径 S、极角 θ 三者无法在任意调整中同时保持**，补偿的本质是选择“把代价放在哪个量上”
- 越界时若不想动色度，可把代价放在亮度上。**根本极限：任何调整都无法同时保持 $(Y, r, \theta)$ 三者**，只能选择“代价落在 Y 还是 S”
- **`CompLumaOnly`（保 S 调 Y，原 `ModeAddCompY`）**：色度 $(Cb,Cr)$ 不变（保极角与极径），按 Y2R 通道钳位量补偿亮度：
  $$\Delta Y=\max(0,-\min_i RGB_i)-\max(0,\max_i RGB_i-1),\qquad Y'=\mathrm{clip}(Y_a+\Delta Y,0,1)$$
  色相与极径 S 不变，靠调 Y 把越界的 RGB 拉回色域；**代价**是亮度漂移。**局限**：$r>r^*$ 时（见下）$\Delta Y$ 无法同时消掉两侧越界，残留溢出交给 `HardClip`，色相仍可能偏。

  **设计说明（ΔY 为何 1:1、无需按 luma 权重）**：Y2R 的 Y 系数列为 $[1,1,1]^T$（$\partial RGB_i/\partial Y=1$），平移 $\Delta Y$ 时 R/G/B 三通道**等量平移**，故缺量/超量以 1:1 补偿即可恰好修满；若按 luma 权重 $w_i$ 加权，三通道平移量相同而目标修正量不同，反而修不满。该式等价于 $Y'=\mathrm{clamp}(Y,[Y_{lo},Y_{hi}])$——把 $Y$ 投影到可行区间（**最小亮度扰动**），本质是几何投影而非能量守恒。
- **`CompLumaFirst`（Y 优先、S 兜底，原 `ModeAddCompYS`）**：色度 $\theta'$ 下，$Y$ 的可行区间为 $[rA,\ 1-rB]$（$A=\max_i(-k_i)$，$B=\max_i k_i$，$k_i=a_i\cos\theta'+b_i\sin\theta'$）。先只调 Y：$Y'=\mathrm{clip}(Y,\ rA,\ 1-rB)$——可行时与 `CompLumaOnly` 逐位一致，色度不动；若 $r>r^*=\dfrac{1}{A+B}$（可行区间为空、Y 单独调不够），再调 S：
  $$(Cb',Cr')\leftarrow(Cb,Cr)\cdot\frac{r^*}{r},\qquad Y'=Y^*=\frac{A}{A+B}$$
  此时 $\max_i RGB_i=1$、$\min_i RGB_i=0$——恰好落在色域边界（$V=1,\ S_{hex}=1$ 全饱和），色相严格保持、无残留越界。取舍：Y 优先、S 只缩到恰好够（最小损失），但 $r>r^*$ 时结果必然全饱和且 Y 可能漂移。

**补充：色相由极角决定，与 Y 无关**

- 未钳位 probe 的 luma 加权和恰等于 $Y$：$w\cdot\mathbf M=0\Rightarrow\sum_i w_i\,RGB_i=Y$，故 $\Delta Y$ 正是 luma 加权能量的变化量；但公式取通道极值（$\min_i$/ $\max_i$）而非加权和——保持的是“色域可行性 + 极角/极径”，而非硬钳后的亮度。
- 通道差 $RGB_i-RGB_j=(k_i-k_j)r$ 只依赖 $\theta$，六边形色相 $t=(mid-min)/(max-min)$ 与 $Y$ 无关 ⇒ **保持极角 $\theta$ 即保持“意图色相”，调 Y 不改变色相本身**。因此 `CompLumaOnly` 对色相的贡献不在“保色相”（由固定 $\theta$ 天然保证），而在**把颜色拉回色域**：避免越界像素被逐通道硬钳而破坏通道比例——这才是显示端色相偏移的根源。可行（单侧越界）时补偿后 probe 完全入域 ⇒ 显示色相 = 意图色相；不可行（$r>r^*$，双侧越界）时残留溢出仍会硬钳偏色（即上述局限，由 `CompLumaFirst` 兜底）。

## 5. 附图：固定 luma 切片的色度平面

以下三张图为 BT.709 下固定 $Y=0.2/0.5/0.8$ 的 (Cb,Cr) 色度平面：色域内渲染真实 RGB 颜色，粗彩色线段为按立方体面着色的色域边界（标注 R/G/B + 亮/暗），黑虚线为 V 等高线、橙实线为 S 等高线（`--extended` 模式可跨边界延伸）。

| 图 | 说明 |
| --- | --- |
| ![Y=0.2](../output/ycbcr_gamut_face_colored_Y0.2.png) | $Y=0.2$：靠近黑角，四边形截面（G=0/B=0/B=1/R=0），暗边为主 |
| ![Y=0.5](../output/ycbcr_gamut_face_colored_Y0.5.png) | $Y=0.5$：标准切片，四边形（R=0/B=1/B=0/R=1），暗亮各两条 |
| ![Y=0.8](../output/ycbcr_gamut_face_colored_Y0.8.png) | $Y=0.8$：靠近白角，五边形（多 G=1 亮边），亮边为主 |

**读图要点**：

- 色域边界每段 = 一张立方体面（某通道 $=0$ 暗边 / $=1$ 亮边）；
- $S=1$（橙线）与暗边重合（$\min=0$），$V=1$（黑虚线最外）与亮边重合（$\max=1$）；
- V/S 等高线均为非圆（六边对称），直观说明“同一极径 $r$ 在不同角度对应不同六边形 S/V”。

绘图脚本：`output/plot_ycbcr_gamut_face_colored.py`（支持 `--extended` 延伸等高线）。

## 参考

- 各种色彩空间模块在线调色模拟 <https://color-space.io/>

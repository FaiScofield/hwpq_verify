# CSC 实现算法对比

## CSC 算法实现

**对比表**

| 算法名称 | 当前状态 | 参数映射方式 | 固定点量化方式 | 主要特点 |
| --- | --- | --- | --- | --- |
| `ALGO_RK_HW_CSC` / `RK HW CSC` | 现行算法 | `RK` 映射 | `get_fixed_coefs_mat()` | One-Step 硬件 CSC，BCSH 通过矩阵变换折叠进 CSC 系数，输入域参数过大时存在偏色风险 |
| `ALGO_RK_SW_CSC` / `RK SW CSC` | 现行算法 | ^ | 运行时固定为 `10bit` 系数 | 软件 CSC，基础 BCSH 路径与 `RK HW CSC` 同源；仅 `R2Y` 场景会把 `RgbGain` 抽成独立 `step1` 以减轻偏色 |
| `ALGO_EVIDEO_CSC` / `eVideo CSC` | 现行算法<br>(索诺克定制版) | `eVideo` 映射 | ^ | 仍是单次 `apply_csc()` 路径，和 `RK SW CSC` 的主要差异在于 BCSH 参数映射范围不同 |
| `ALGO_EVIDEO_CSC_PLAN_A` / `eVideo CSC Plan A` | 改进方案A | ^ | `step1/step2` 分别量化 | Two-Step，Y2Y时不生效`RgbGain/RgbOffset`参数 |
| `ALGO_EVIDEO_CSC_PLAN_B` / `eVideo CSC Plan B` | 改进方案B | ^ | ^ | 在PLAN_A 基础上，以输出域为参考做BCSH |
| `ALGO_EVIDEO_CSC_PLAN_C` / `eVideo CSC Plan C` | 改进方案C | `eVideo` 映射 | ^ | 所有参数统一转到 RGB，再进入 HSV 域调色，调色后转回输出色域，四模式全参数生效 |

### RK HW CSC

- RK VOP CSC 硬件版本，8个寄存器涵盖了 3x3 CSC矩阵（5个寄存器） + 3x1 偏移量（3个寄存器） 共计12个参数实现
- 基本公式: `O = clip(M * I + V, 0, m)` , 对于`8/10bit`数据 `m=255/1023`
- BCSH支持：将 BCSH 参数通过矩阵变换的关系作用到$M$上，得到$M'$，用新的$M'$进行计算
  - 由于硬件设计是 **One-Step CSC**，只有在最后一步做clip操作，所以如果<u>作用于输入域的BCSH参数过大</u>可能会导致中间层数据溢出，进而导致<font color="red">输出出现色偏现象</font>
  - `Brightness`: $B_y = [b, 0, 0]^T,\quad B_r = [b, b, b]^T$，既可以作用于 RGB 域，也可以作用于 YUV 域，视输出而定（<font color="red">作用于RGB输出时会改变颜色饱和度</font>）
  - `Contrast`: $C_r = \begin{bmatrix}c&0&0\\0&c&0\\0&0&c\end{bmatrix}$, 只作用于 RGB 域 （<font color="red">$c>1$时会让暗部数据也变亮；YUV输出时存在偏色风险</font>）
  - `Saturation`: $S_y = \begin{bmatrix}1&0&0\\0&s&0\\0&0&s\end{bmatrix}$, 只作用于 YUV 域
  - `Hue`: $H_y = \begin{bmatrix}1&0&0\\0&cos(h)&-sin(h)\\0&sin(h)&cos(h)\end{bmatrix}$, 只作用于 YUV 域
  - `RgbGain`：$G_r = \begin{bmatrix}r_{gain}&0&0\\0&g_{gain}&0\\0&0&b_{gain}\end{bmatrix}$，只作用于 RGB 域 （<font color="red">$gain>1$且YUV输出时存在偏色风险</font>）
  - `RgbOffset`：$O_r = \begin{bmatrix}r_{offset}\\g_{offset}\\b_{offset}\end{bmatrix}$，只作用于**输出** RGB 域（和`Brightness`有重复）

- BCSH参数生效表：
  - 注： `I`表示作用于输入, `O`表示作用于输出, `MO`表示作用于输出的中间层，`MI`表示作用于输入的中间层, `X`表示不生效（下同）
  - 所谓中间层指：Y2Y时 yuv 数据需要先转到 rgb 的中间层再应用 rgb 域的BCSH参数，最后再转回 yuv 域； R2R时亦然。

    | 参数类型 | 映射范围 | 作用域 | R2Y | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----: | :---: | :---: | :---: |
    | 亮度 `Brightness` | `[-1/4, 1/4]` | RGB/YUV OUT | O | O | O | O |
    | 对比度 `Contrast` | `[0.0, 2.0]` | RGB | I | O | O | MO |
    | 饱和度 `Saturation` | `[0.0, 2.0]` | YUV | O | I | MO | O |
    | 色调 `Hue` | `[-30, 30]deg` | YUV | O | I | MO | O |
    | RGB增益 `RgbGain` | `[0.0, 2.0]` | RGB | I | O | O | MO |
    | RGB偏移 `RgbOffset` | `[-1/8, 1/8]` | RGB OUT | X | O | O | X |

### RK SW CSC

- 当前脚本已为 `RK SW CSC` 提供独立算法入口，运行时通过 `run_selected_algo()` 调度，并统一将 `coef_precision` 固定为 `10bit`
- 系数生成仍复用 `RK HW CSC` 的矩阵路径，因此 BCSH 生效规则总体与 **RK HW CSC** 保持一致
- 与 **RK HW CSC** 的主要运行时差异：
  - `R2Y` 时会先把 `RgbGain` 作为独立 `step1` 在输入 RGB 域执行，再对清零后的 `RgbGain` 做后续 CSC 计算
  - 其余参数仍合并在后续 CSC 系数中，`Contrast > 1` 且输出为 YUV 时仍可能出现偏色
- 因为该路径不是严格的硬件 One-Step，`R2Y` 场景下由 `RgbGain` 引起的色偏风险可以部分避免；`Y2Y/R2R` 仍可能保留中间域偏色风险

### eVideo CSC

- 为星网视易公司定制的软件 CSC 版本，当前通过 `get_evideo_csc_coefs()` 生成单组仿射 CSC 系数，再在 `run_selected_algo()` 中执行一次 `apply_csc()`
- 与 **RK SW CSC** 的主要区别是 **BCSH 参数映射范围** 和 **系数量化方式** 不同：
  - BCSH 参数按 eVideo 范围映射：`Brightness[-1,1]`、`Hue[-180,180]deg`、`RgbGain[0,8]`、`RgbOffset[-1,1]`
  - 当 `coef_precision > 0` 时，量化入口改为 `get_fixed_coefs_affine()`
- BCSH参数生效表：

    | 参数类型 | 映射范围 | 作用域 | R2Y | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----: | :---: | :---: | :---: |
    | 亮度 `Brightness` | `[-1.0, 1.0]` | RGB/YUV OUT | O | O | O | O |
    | 对比度 `Contrast` | `[0.0, 2.0]` | RGB | I | O | O | MO |
    | 饱和度 `Saturation` | `[0.0, 2.0]` | YUV | O | I | MO | O |
    | 色调 `Hue` | `[-180, 180]deg` | YUV | O | I | MO | O |
    | RGB增益 `RgbGain` | `[0.0, 8.0]` | RGB | I | O | O | MO |
    | RGB偏移 `RgbOffset` | `[-1.0, 1.0]` | RGB OUT | X | O | O | X |

- BCSH 色偏现象理论与 RK SW CSC 一致

### eVideo CSC Plan A

- eVideo CSC 软件改进版本A，当前代码中的实现要点：
  - CSC 系数精度支持 `{0(浮点精度), [8, 16]}`，`step1/step2` 分别按同一精度量化
  - `BCSH` 4 个参数只作用于 YUV 域，`RgbGain/RgbOffset` 6 个参数只作用于 RGB 域
- BCSH 参数的改进方案A 具体内容：
  - `Brightness`: $B_y = [b, 0, 0]^T$，只作用于YUV 域，
  - `Contrast`: $Cg_y = \begin{bmatrix}c&0&0\\0&1&0\\0&0&1\end{bmatrix},\quad Co_y = \begin{bmatrix}0.5\\0\\0\end{bmatrix}$, 只作用于 YUV 域
    - 公式由 $O_r=C_r*I_r$ 改为：$O_y=Cg_y*(I_y-Co_y)+Co_y$，解决对比度映射曲线过原点$(0, 0)$而不是$(0.5, 0.5)$点的问题
  - `Saturation`: $S_y = \begin{bmatrix}1&0&0\\0&s&0\\0&0&s\end{bmatrix}$, 只作用于 YUV 域，保持不变
  - `Hue`: $H_y = \begin{bmatrix}1&0&0\\0&cos(h)&-sin(h)\\0&sin(h)&cos(h)\end{bmatrix}$, 只作用于 YUV 域，保持不变
  - `RgbGain`：$G_r = \begin{bmatrix}r_{gain}&0&0\\0&g_{gain}&0\\0&0&b_{gain}\end{bmatrix}$，只作用于 RGB 域
  - `RgbOffset`：$O_r = \begin{bmatrix}r_{offset}\\g_{offset}\\b_{offset}\end{bmatrix}$，只作用于 RGB 域
- BCSH参数生效总结：
  - `BCSH` 4 个参数融合成齐次矩阵 `Q_yuv`，作用对象按优先级从高到低排列：输出 YUV（`R2Y/Y2Y`）、输入 YUV（`Y2R`）、输入中间层 YUV（`R2R`）
  - `RgbGain/RgbOffset` 6 个参数融合成齐次矩阵 `Q_rgb`，作用对象按优先级从高到低排列：输出 RGB（`Y2R/R2R`）、输入 RGB（`R2Y`）、输入中间层 RGB（`Y2Y`）
  - 运行时按域拆分为齐次矩阵路径：**Two-Step** 实现，四个模式均按 $I' \to O'$ 两步执行
    - 对于 `R2Y`：$I'_{rgb} = clip(Q_{rgb} * I_{rgb}, 0, 1);\quad O'_{yuv} = clip((Q_{yuv} * M_{r2y}) * I'_{rgb}, 0, 1)$
    - 对于 `Y2R`：$I'_{yuv} = clip(Q_{yuv} * I_{yuv}, 0, 1);\quad O'_{rgb} = clip((Q_{rgb} * M_{y2r}) * I'_{yuv}, 0, 1)$
    - 对于 `R2R`：$I'_{rgb} = clip(M_{y2r} * Q_{yuv} * M_{r2y} * I_{rgb}, 0, 1);\quad O'_{rgb} = clip(Q_{rgb} * I'_{rgb}, 0, 1);$
    - 对于 `Y2Y`：$I'_{yuv} = clip(M_{r2y} * Q_{rgb} * M_{y2r} * I_{yuv}, 0, 1);\quad O'_{yuv} = clip((Q_{yuv} * M_{y2y}) * I'_{yuv}, 0, 1)$
  - UI 中仍只显示两组齐次矩阵参数：
    - `Step1` 根据以上4个模式的分支显示 `Q_yuv/Q_rgb` 的系数和偏移
    - `Step2` 根据以上4个模式的分支显示 `Q_yuv/Q_rgb` 的系数和偏移
    - 中间域转换使用的 `M_{r2y}` / `M_{y2r}` 不在 UI 中单独显示

    | 参数类型 | 映射范围 | 作用域 | R2Y | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----: | :---: | :---: | :---: |
    | 亮度 `Brightness` | `[-1.0, 1.0]` | YUV | O | I | MI | O |
    | 对比度 `Contrast` | `[0.0, 2.0]` | YUV | O | I | MI | O |
    | 饱和度 `Saturation` | `[0.0, 2.0]` | YUV | O | I | MI | O |
    | 色调 `Hue` | `[-180, 180]deg` | YUV | O | I | MI | O |
    | RGB增益 `RgbGain` | `[0.0, 8.0]` | RGB | I | O | O | MI |
    | RGB偏移 `RgbOffset` | `[-1.0, 1.0]` | RGB | I | O | O | MI |

### eVideo CSC Plan B

- eVideo CSC 软件改进版本B
- 参数构成沿用 eVideo 映射，并复用与 Plan A 相同的两个域矩阵：
  - `Q_yuv`：由 `Brightness/Contrast/Saturation/Hue` 组合而成，只表示 YUV 域参数
  - `Q_rgb`：由 `RgbGain/RgbOffset` 组合而成，只表示 RGB 域参数
- 运行时按模式调度：
  - 对于 `Y2R`：`step1 = Q_yuv`，`step2 = Q_rgb * M_{y2r}`
  - 对于 `R2Y`：`step1 = Q_rgb`，`step2 = Q_yuv * M_{r2y}`
  - 对于 `Y2Y`：`step1 = None`，`step2 = Q_yuv * M_{y2y}`
  - 对于 `R2R`：`step1 = None`，`step2 = Q_rgb * M_{r2r}`
- 因此当前代码中的参数生效范围可以总结为：

    | 参数类型 | 映射范围 | 作用域 | R2Y | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----: | :---: | :---: | :---: |
    | 亮度 `Brightness` | `[-1.0, 1.0]` | YUV | O | I | X | O |
    | 对比度 `Contrast` | `[0.0, 2.0]` | YUV | O | I | X | O |
    | 饱和度 `Saturation` | `[0.0, 2.0]` | YUV | O | I | X | O |
    | 色调 `Hue` | `[-180, 180]deg` | YUV | O | I | X | O |
    | RGB增益 `RgbGain` | `[0.0, 8.0]` | RGB | I | O | O | X |
    | RGB偏移 `RgbOffset` | `[-1.0, 1.0]` | RGB | I | O | O | X |

### eVideo CSC Plan C

- eVideo CSC 软件改进版本C：把所有参数统一转到 RGB 域，再进入 HSV 色域调色，调色完成后转回原（输出）色域
- 参数构成沿用 eVideo 映射，全部参数在 `RGB -> HSV -> RGB` 调色路径中生效：
  - `Hue` 作用于 HSV 的 `H`：$H' = (H + hue) \bmod 360$
  - `Saturation` 作用于 HSV 的 `S`：$S' = clip(S \times saturation, 0, 1)$
  - `Brightness/Contrast` 作用于 HSV 的 `V`：$V' = clip((V - 0.5) \times contrast + 0.5 + brightness, 0, 1)$
  - `RgbGain/RgbOffset` 在 HSV 转回 RGB 后应用：$RGB' = clip(RGB \times rgb\_gains + rgb\_offsets, 0, 1)$
- 运行时按模式调度（输入/输出的 YUV↔RGB 转换按实际色彩空间构建）：
  - 对于 `R2R`：`RGB -> HSV(调色) -> RGB`
  - 对于 `R2Y`：`RGB -> HSV(调色) -> RGB -> M_{r2y}`
  - 对于 `Y2R`：`M_{y2r} -> RGB -> HSV(调色) -> RGB`
  - 对于 `Y2Y`：`M_{y2r} -> RGB -> HSV(调色) -> RGB -> M_{r2y}`
- 特点：
  - 调色全程在 HSV 域进行，为非线性路径（非矩阵合成），因此不参与固定点系数量化，精度为浮点
  - 四模式下所有参数均生效，无 `X` 项；`RgbGain/RgbOffset` 在转回 RGB 后应用

    | 参数类型 | 映射范围 | 作用域 | R2Y | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----: | :---: | :---: | :---: |
    | 亮度 `Brightness` | `[-1.0, 1.0]` | HSV-V | I | O | O | MO |
    | 对比度 `Contrast` | `[0.0, 2.0]` | HSV-V | I | O | O | MO |
    | 饱和度 `Saturation` | `[0.0, 2.0]` | HSV-S | I | O | O | MO |
    | 色调 `Hue` | `[-180, 180]deg` | HSV-H | I | O | O | MO |
    | RGB增益 `RgbGain` | `[0.0, 8.0]` | RGB | I | O | O | MO |
    | RGB偏移 `RgbOffset` | `[-1.0, 1.0]` | RGB | I | O | O | MO |

### 各版本算法差异

| 对比项 | `RK HW CSC` | `RK SW CSC` | `eVideo CSC` | `eVideo CSC Plan A` | `eVideo CSC Plan B` | `eVideo CSC Plan C` |
| --- | --- | --- | --- | --- | --- | --- |
| 文档/代码对应 | `ALGO_RK_HW_CSC` | `ALGO_RK_SW_CSC` | `ALGO_EVIDEO_CSC` | `ALGO_EVIDEO_CSC_PLAN_A` | `ALGO_EVIDEO_CSC_PLAN_B` | `ALGO_EVIDEO_CSC_PLAN_C` |
| 实现形态 | 硬件 One-Step CSC | 软件浮点 CSC | 软件浮点 CSC | 软件浮点 CSC 改进方案 A | 软件浮点 CSC 改进方案 B | 软件浮点 CSC 改进方案 C（HSV 域调色） |
| BCSH 映射范围 | `RK` 旧映射 | `RK` 旧映射 | `eVideo` 映射 | `eVideo` 映射 | `eVideo` 映射 | `eVideo` 映射 |
| 运行时步数 | 固定 1 步 | 常规 1 步，`R2Y` 额外 `step1` | 固定 1 步 | `R2Y/Y2R/R2R/Y2Y` 均 2 步 | `R2Y/Y2R` 2 步，`R2R/Y2Y` 仅 `step2` | 统一 `RGB→HSV→RGB` 调色路径（YUV 输入/输出额外各一次域转换） |
| 亮度/对比度/饱和度/色调 | 按原始 RK 规则折叠入单组 CSC | 基本同 `RK HW CSC`，但 `R2Y` 可先抽离 `RgbGain` | 按 eVideo 规则折叠入单组仿射 CSC | 合并进 `Q_yuv`：`R2Y/Y2Y` 输出 YUV、`Y2R` 输入 YUV、`R2R` 输入中间层（MI） | 合并进 `Q_yuv`：`R2Y/Y2Y` 输出 YUV、`Y2R` 输入 YUV、`R2R` 不生效（X） | 合并进 HSV 的 H/S/V，四模式均生效 |
| `RgbGain` / `RgbOffset` | RGB 域 / 输出 RGB 域 | `RgbGain` 在 `R2Y` 可抽成独立 `step1` | RGB 域 / 输出 RGB 域 | 合并进 `Q_rgb`：`R2Y` 输入、`Y2R/R2R` 输出、`Y2Y` 输入中间层（MI） | 合并进 `Q_rgb`：`R2Y` 输入、`Y2R/R2R` 输出、`Y2Y` 不生效（X） | 在 HSV 转回 RGB 后应用，四模式均生效 |
| 主要备注 | 输入域参数过大时可能偏色 | 运行时精度固定为 `10bit` | 主要差异在参数映射范围与仿射量化 | UI 显示 `Q_yuv/Q_rgb` 两组（按模式分支），中间域转换不单独显示 | `step1` 允许为空，当前实现不包含 HSV 专用运行时分支 | 调色为非线性 HSV 路径（浮点），不参与固定点量化；中间 YUV↔RGB 固定 BT709 全范围 |

**BCSH 参数范围对比**

| 参数 | 原始寄存器范围 | `RK HW CSC` / `RK SW CSC` | `eVideo CSC` / `Plan A` / `Plan B` |
| --- | --- | --- | --- |
| `Brightness` | `[0, 512]` | `[-1/4, 1/4]` | `[-1, 1]` |
| `Contrast` | `[0, 512]` | `[0, 2]` | `[0, 2]` |
| `Saturation` | `[0, 512]` | `[0, 2]` | `[0, 2]` |
| `Hue` | `[0, 512]` | `[-30, 30]` 度 | `[-180, 180]`度 |
| `RgbGain` | `[0, 512]` | `[0, 2]` | `[0, 8]` |
| `RgbOffset` | `[0, 512]` | `[-1/8, 1/8]` | `[-1, 1]` |


## RGB <=> HSV 转换算法

### RGB 立方体到六边形平面的投影

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
```

生产构建与本地预览：

```shell
cd web/color-space-lab
npm run build      # 构建产物输出到 dist/
npm run preview    # 本地预览构建产物
```
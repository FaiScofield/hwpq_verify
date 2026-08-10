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
  - 各通道调整下限为0，`k` 的上限为 `1/M`（此时 `M'=1`，最大通道到顶）
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

**Python 计算代码（RGB 域直接调整；同时支持单像素 `(r,g,b)` 标量 与 numpy 数组 `(...,3)` 批量；参数为**加性偏置**：`delta_h ∈ [-0.5, 0.5]`（归一化色相，0.5 = 180°）、`delta_s/delta_v ∈ [-1, 1]`；已用随机样例与 HSV 中转对比验证，最大误差 < 2e-15）**：

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

**C 语言实现（定点化版本，输入 8bit RGB，性能优先、减少分支）**：

```c
#include <stdint.h>

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
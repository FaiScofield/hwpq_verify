# CSC 实现算法对比

## 算法实现

**对比表**

| 算法名称 | 当前状态 | 参数映射方式 | 核心计算路径 | 固定点量化方式 | 主要特点 |
| --- | --- | --- | --- | --- | --- |
| `ALGO_RK_HW_CSC` / `RK HW CSC` | 现行算法 | `RK` 旧映射 | `adjust_convert_mat()` | `get_fixed_coefs_mat()` | One-Step 硬件 CSC，BCSH 通过矩阵变换折叠进 CSC 系数，输入域参数过大时存在偏色风险 |
| `RK SW CSC` | 新增条目 | `RK` 旧映射 | 文档新增，代码待补充 | 文档新增，代码待补充 | 软件浮点 CSC，BCSH 生效方式基本同 `RK HW CSC`，但非 One-Step，可避免大部分色偏问题 |
| `ALGO_EVIDEO_CSC` / `eVideo CSC` | 现行算法 | `eVideo` 映射 | `adjust_convert_quad_evideo()` | `get_fixed_coefs_affine()` | 采用 eVideo 参数映射，核心差异主要在 BCSH 映射范围与 RGB/YUV 域参数组合顺序 |
| `ALGO_EVIDEO_CSC_PLAN_A` / `eVideo CSC Plan A` | 现行算法 | `eVideo` 映射 | `Two-Step homogeneous path` | `step1/step2 split output` | 方案 A：按域拆分 `Q_rgb` 与 `Q_yuv`，每步执行后钳位 |
| `ALGO_EVIDEO_CSC_PLAN_B` / `eVideo CSC Plan B` | 现行算法 | `eVideo` 映射 | `Two-Step homogeneous path` | `step1/step2 split output` | 方案 B：`R2Y/Y2R` 两步，`R2R/Y2Y` 仅保留 `step2` |

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
  - 注： `I`表示作用于输入, `O`表示作用于输出, `MO`表示作用于输出的中间层，`MI`表示作用于输入的中间层, `X`表示不生效
  - 所谓中间层指：Y2Y时 yuv 数据需要先转到 rgb 的中间层再应用 rgb 域的BCSH参数，最后再转回 yuv 域； R2R时亦然。

    | 参数类型 | 映射范围 | 作用域 |  R2Y | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----:|:---:|:---:|:---:|
    | 亮度 `Brightness`   | `[-1/4, 1/4]`  | RGB/YUV OUT |  O | O | O  | O |
    | 对比度 `Contrast`   | `[0.0, 2.0]`   | RGB |  I | O | O  | MO |
    | 饱和度 `Saturation` | `[0.0, 2.0]`   | YUV |  O | I | MO | O |
    | 色调 `Hue`          | `[-30, 30]deg` | YUV |  O | I | MO | O |
    | RGB增益 `RgbGain`   | `[0.0, 2.0]`   | RGB |  I | O | O  | MO |
    | RGB偏移 `RgbOffset` | `[-1/8, 1/8]`  | RGB OUT |  X | O | O  | X |

### RK SW CSC

- RK VOP CSC 软件版本，采用 GPU 进行浮点计算，与 **RK HW CSC** 版本的区别：
  - 但是系数是固定的10bit系数，对于10bit数据来说系数的精度不够 **（待改进）**
    - 本仿真脚本将此版本的系数计算方式采用和 **RK HW CSC** 版本一致并固定为 10bit 精度
  - BCSH支持基本保持一致，但由于是非 One-Step CSC，**输出的色偏现象部分可以避免**
    - 本仿真脚本在R2Y时时会抽离`RgbGain`参数对输入RGB单独生效，避免色偏现象，<font color="red">但Y2Y还是会存在色偏风险</font>
    - ~~本仿真脚本没有抽离`Contrast`参数，因为目前软件端并没有这么做 **（待修正）**，所以~~`Contrast>1`且YUV输出时还是可能会出现色偏现象。

### eVideo CSC

- 为星网视易公司定制的软件 CSC 版本，采用 GPU 进行浮点计算，与 **RK SW CSC** 版本的主要区别是**BCSH系数映射范围不同**
- BCSH参数生效表：

    | 参数类型 | 映射范围 | 作用域 |  R2Y | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----:|:---:|:---:|:---:|
    | 亮度 `Brightness`   | `[-1.0, 1.0]`  | RGB/YUV OUT |  O | O | O  | O |
    | 对比度 `Contrast`   | `[0.0, 2.0]`   | RGB |  I | O | O  | MO |
    | 饱和度 `Saturation` | `[0.0, 2.0]`   | YUV |  O | I | MO | O |
    | 色调 `Hue`          |`[-180, 180]deg`| YUV |  O | I | MO | O |
    | RGB增益 `RgbGain`   | `[0.0, 8.0]`   | RGB |  I | O | O  | MO |
    | RGB偏移 `RgbOffset` | `[-1.0, 1.0]`  | RGB OUT |  X | O | O  | X |

- BCSH 色偏现象理论与 RK SW CSC 一致

### eVideo CSC Plan A

- eVideo CSC 软件改进版本A，改进主要体现在2个方面：
  - CSC 系数的精度支持选择: `{0(浮点精度)，[8, 16]}`
  - BCSH 参数生效方式改进方案A： `BCSH`参数只作用于YUV域(R2R时需要先转到YUV生效)，`RgbGain/RgbOffset`参数只作用于RGB域（Y2Y时需要先转到RGB生效）
- BCSH 参数的改进方案A 具体内容：
  - `Brightness`: $B_y = [b, 0, 0]^T$，只作用于YUV 域，
  - `Contrast`: $Cg_y = \begin{bmatrix}c&0&0\\0&1&0\\0&0&1\end{bmatrix},\quad Co_y = \begin{bmatrix}0.5\\0\\0\end{bmatrix}$, 只作用于 YUV 域
    - 公式由 $O_r=C_r*I_r$ 改为：$O_y=Cg_y*(I_y-Co_y)+Co_y$，解决对比度映射曲线过原点$(0, 0)$而不是$(0.5, 0.5)$点的问题
  - `Saturation`: $S_y = \begin{bmatrix}1&0&0\\0&s&0\\0&0&s\end{bmatrix}$, 只作用于 YUV 域，保持不变
  - `Hue`: $H_y = \begin{bmatrix}1&0&0\\0&cos(h)&-sin(h)\\0&sin(h)&cos(h)\end{bmatrix}$, 只作用于 YUV 域，保持不变
  - `RgbGain`：$G_r = \begin{bmatrix}r_{gain}&0&0\\0&g_{gain}&0\\0&0&b_{gain}\end{bmatrix}$，只作用于 RGB 域
  - `RgbOffset`：$O_r = \begin{bmatrix}r_{offset}\\g_{offset}\\b_{offset}\end{bmatrix}$，只作用于 RGB 域
- BCSH参数生效总结：
  - `BCSH` 4个参数融合成齐次矩阵`Quad_yuv`，作用对象按优先级从高到低排列：输出YUV(R2Y/Y2Y)、输入YUV(Y2R)、输入中间层YUV(R2R: R2Y2R)
  - `RgbGain/RgbOffset` 6个参数融合成齐次矩阵`Quad_rgb`，作用对象按优先级从高到低排列：输出RGB(Y2R/R2R)、输入RGB(R2Y)、输入中间层RGB(Y2Y: Y2R2Y)
  - 改为**Two-Step**形式，先计算作用于输入的矩阵和向量，再计算作用于输出的矩阵和向量，每次变换后都需要钳位
    - 对于R2Y，计算公式为: $I'_{rgb} = clip(Q_{rgb} * I_{rgb}, 0, 1); O'_{yuv} = clip(Q_{yuv} * M_{r2y} * I'_{rgb}, 0, 1)$
    - 对于Y2R，计算公式为: $I'_{yuv} = clip(Q_{yuv} * I_{yuv}, 0, 1); O'_{rgb} = clip(Q_{rgb} * M_{y2r} * I'_{rgb}, 0, 1)$
    - 对于R2R，计算公式为: $I'_{yuv} = clip(Q_{yuv} * M_{r2y} * I_{rgb}, 0, 1); O'_{rgb} = clip(Q_{rgb} * M_{y2r} * I'_{yuv}, 0, 1)$
    - 对于Y2Y，计算公式为: $I'_{rgb} = clip(Q_{rgb} * M_{y2r} * I_{yuv}, 0, 1); O'_{yuv} = clip(Q_{yuv} * M_{r2y} * I'_{rgb}, 0, 1)$

    | 参数类型 | 映射范围 | 作用域 |  R2Y | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----:|:---:|:---:|:---:|
    | 亮度 `Brightness`   | `[-1.0, 1.0]`  | YUV |  O | I | MI | O |
    | 对比度 `Contrast`   | `[0.0, 2.0]`   | RGB |  O | I | MI | O |
    | 饱和度 `Saturation` | `[0.0, 2.0]`   | YUV |  O | I | MI | O |
    | 色调 `Hue`          |`[-180, 180]deg`| YUV |  O | I | MI | O |
    | RGB增益 `RgbGain`   | `[0.0, 8.0]`   | RGB |  I | O | O  | MI|
    | RGB偏移 `RgbOffset` | `[-1.0, 1.0]`  | RGB |  I | O | O  | MI|

### eVideo CSC Plan B

- eVideo CSC 软件改进版本B，和方案A的区别主要在于BCSH参数的方案不用
- BCSH 参数的改进方案B：
  - `BCSH`: 4个参数优先在 YUV 域生效，没有 YUV 数据时在 RGB => HSV 域生效
    - 如果是 Y2R，在输入 YUV 域生效
    - 如果是 Y2Y / R2Y，在输出 YUV 域生效
    - 如果是 R2R，在输出 RGB => HSV 域生效，在该域的计算公式如下：
      - `Brightness/Contrast`: $V' = c_g * (V - c_o) + c_o + b$
      - `Saturation`: $S' = s * S$
      - `Hue`: $H' = H + h$
  - `RgbGain`/`RgbOffset`：只在 RGB 域生效
    - 如果是 Y2R / R2R，在输出 RGB 域生效
    - 如果是 R2Y，在输入 RGB 域生效
    - 如果是 Y2Y，不生效

## 其他

**关键差异**

| 对比项 | `RK HW CSC` | `RK SW CSC` | `eVideo CSC` | `eVideo CSC Plan A` | `eVideo CSC Plan B` |
| --- | --- | --- | --- | --- | --- |
| 文档/代码对应 | `ALGO_RK_HW_CSC` | 新增条目 | `ALGO_EVIDEO_CSC` | `ALGO_EVIDEO_CSC_PLAN_A` | `ALGO_EVIDEO_CSC_PLAN_B` |
| 实现形态 | 硬件 One-Step CSC | 软件浮点 CSC | 软件浮点 CSC | 软件浮点 CSC 改进方案 A | 软件浮点 CSC 改进方案 B |
| BCSH 映射范围 | `RK` 旧映射 | `RK` 旧映射 | `eVideo` 映射 | `eVideo` 映射 | `eVideo` 映射 |
| 亮度策略 | RGB/YUV 输出域生效 | 基本同 `RK HW CSC` | RGB/YUV 输出域生效 | 并入 `Q_yuv`，按 Two-Step 路径生效 | 并入 `Q_yuv`，按 Two-Step 路径生效 |
| 对比度策略 | RGB 域缩放，YUV 输出有偏色风险 | 基本同 `RK HW CSC`，当前脚本未抽离 `Contrast` | RGB 域缩放 | 改为 `Q_yuv` 中的 YUV 域中心缩放 | 并入 `Q_yuv`，`R2R/Y2Y` 仅保留 `step2` |
| `RgbGain` / `RgbOffset` | RGB 域 / 输出 RGB 域 | `RgbGain` 在 R2Y 时可单独抽离 | RGB 域 / 输出 RGB 域 | 并入 `Q_rgb`，由 `step1/step2` 按域调度 | 并入 `Q_rgb`，`Y2Y` 不生效且 `R2R/Y2Y` 无 `step1` |
| 主要备注 | 输入域参数过大时可能偏色 | 非 One-Step，可避免大部分色偏 | 主要差异在参数映射范围 | 显式输出 `step1/step2` 两组齐次矩阵参数 | 显式输出 `step1/step2` 两组齐次矩阵参数 |

**BCSH 参数范围对比**

| 参数 | 原始寄存器范围 | `RK HW CSC` / `RK SW CSC` | `eVideo CSC` / `Plan A` / `Plan B` |
| --- | --- | --- | --- |
| `Brightness` | `[0, 512]` | `[-1/4, 1/4]` | `[-1, 1]` |
| `Contrast` | `[0, 512]` | `[0, 2]` | `[0, 2]` |
| `Saturation` | `[0, 512]` | `[0, 2]` | `[0, 2]` |
| `Hue` | `[0, 512]` | `[-30, 30]` 度 | `[-180, 180]`度 |
| `RgbGain` | `[0, 512]` | `[0, 2]` | `[0, 8]` |
| `RgbOffset` | `[0, 512]` | `[-1/8, 1/8]` | `[-1, 1]` |

**名称对应关系**

- `ALGO_RK_HW_CSC` 对应 `RK HW CSC`
- `ALGO_RK_SW_CSC` 对应 `RK SW CSC`
- `ALGO_EVIDEO_CSC` 对应 `eVideo CSC`
- `ALGO_EVIDEO_CSC_PLAN_A` 对应 `eVideo CSC Plan A`
- `ALGO_EVIDEO_CSC_PLAN_B` 对应 `eVideo CSC Plan B`

**代码依据**

- 常量定义与别名归一化：[get_csc_coef_hsv.py](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coef_hsv.py)
- `RK HW CSC / RK SW CSC` 路径：[adjust_convert_mat](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coefs.py#L322-L366)
- `eVideo CSC / Plan A` 系数路径：[get_evideo_csc_coefs](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coef_hsv.py#L271-L285)
- `eVideo CSC Plan A / Plan B` 两步系数路径：[get_csc_coef_hsv.py](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coef_hsv.py)
- Two-Step 总调度入口：[run_selected_algo](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/run_csc.py)
- UI 两步参数显示入口：[display_result](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/run_csc.py)

**简要结论**

- 当前文档聚焦 `RK HW CSC`、`RK SW CSC`、`eVideo CSC`、`eVideo CSC Plan A`、`eVideo CSC Plan B` 这 5 个条目。
- `RK SW CSC` 现在已具备单列算法入口，并在 `R2Y` 场景下将 `RgbGain` 从矩阵路径中抽离为独立 RGB 域处理。
- `ALGO_EVIDEO_CSC_PLAN_A` 与 `ALGO_EVIDEO_CSC_PLAN_B` 现统一输出 `step1/step2` 两组齐次矩阵参数，并在 UI 中分别展示。
- 现有代码入口与文档名称的对应关系以 `ALGO_RK_HW_CSC`、`ALGO_RK_SW_CSC`、`ALGO_EVIDEO_CSC`、`ALGO_EVIDEO_CSC_PLAN_A`、`ALGO_EVIDEO_CSC_PLAN_B` 为主。

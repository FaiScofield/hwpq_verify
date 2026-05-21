# CSC 实现算法对比

## 算法实现

**对比表**

| 算法名称 | 当前状态 | 参数映射方式 | 核心计算路径 | 固定点量化方式 | 主要特点 |
| --- | --- | --- | --- | --- | --- |
| `RK CSC` | 现行算法 | `RK` 旧映射 | `adjust_convert_mat()` | `get_fixed_coefs_mat()` | 传统 RK CSC 路径，基于 `3x3 matrix + range offset` 做调整 |
| `eVideo CSC` | 现行算法 | `eVideo` 映射 | `adjust_convert_quad_evideo()` | `get_fixed_coefs_affine()` | 把整体看成仿射变换，亮度、HS、RGB gain/offset 的组合顺序更明确 |
| `eVideo CSC fix` | 现行算法 | `eVideo` 映射 | `adjust_convert_quad_evideo_fix()` | `get_fixed_coefs_affine()` | `eVideo CSC` 的修正版，对比度/亮度/色度作用域更严格 |
| `rgbOnHsv_RgbCfg4YuvOff` | 现行名称 | `eVideo` 映射 | 在本文件中最终仍走 `adjust_convert_mat()` | `get_fixed_coefs_mat()` | 名义上是 RGB 配置叠加 HSV 路径的 `YuvOff` 版本，但当前文件里无独立公式 |
| `rgbOnHsv_RgbCfg4YuvOn` | 现行名称 | `eVideo` 映射 | 在本文件中最终仍走 `adjust_convert_mat()` | `get_fixed_coefs_mat()` | 名义上是 `YuvOn` 版本，但当前文件里也没有和 `Off` 分开的计算分支 |

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
  - 注： `I`表示作用于输入, `O`表示作用于输出, `MO`表示作用于输出的中间层，`X`表示不生效
  - 所谓中间层指：Y2Y时 yuv 数据需要先转到 rgb 的中间层再应用 rgb 域的BCSH参数，最后再转回 yuv 域； R2R时亦然。

    | 参数类型 | 映射范围 | 作用域 |  Y2R | Y2R | R2R | Y2Y |
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
  - BCSH支持基本保持一致，但由于是非 One-Step CSC，**输出的色偏现象可以避免**
    - 本仿真脚本在应用BCSH参数时会抽离`RgbGain`参数在R2Y时单独生效，避免色偏现象
    - 本仿真脚本没有抽离`Contrast`参数，因为目前软件端并没有这么做 **（待修正）**，所以`Contrast>1`且YUV输出时还是可能会出现色偏现象。

### eVideo CSC

- 为星网视易公司定制的软件 CSC 版本，采用 GPU 进行浮点计算，与 **RK SW CSC** 版本的主要区别是**BCSH系数映射范围不同**
- BCSH参数生效表：

    | 参数类型 | 映射范围 | 作用域 |  Y2R | Y2R | R2R | Y2Y |
    | ------- | ------- | ------ | :----:|:---:|:---:|:---:|
    | 亮度 `Brightness`   | `[-1.0, 1.0]`  | RGB/YUV OUT |  O | O | O  | O |
    | 对比度 `Contrast`   | `[0.0, 2.0]`   | RGB |  I | O | O  | MO |
    | 饱和度 `Saturation` | `[0.0, 2.0]`   | YUV |  O | I | MO | O |
    | 色调 `Hue`          |`[-180, 180]deg`| YUV |  O | I | MO | O |
    | RGB增益 `RgbGain`   | `[0.0, 8.0]`   | RGB |  I | O | O  | MO |
    | RGB偏移 `RgbOffset` | `[-1.0, 1.0]`  | RGB OUT |  X | O | O  | X |

### eVideo CSC Plan A

- eVideo CSC 软件改进版本A，改进主要体现在2个方面：
  - CSC 系数的精度支持选择: `{0(浮点精度)，[8, 16]}`
  - BCSH 参数生效方式改进方案A
- BCSH 参数的改进方案A：
  - `Brightness`: $B_y = [b, 0, 0]^T$，只作用于**输出** YUV 域，没有YUV输出时参数不生效
    - 取消对输出 RGB 域的支持，避免在 RGB 域生效导致饱和度改变的问题
    - RGB输出的亮度调整可以通过 `RgbOffset` 参数实现
  - `Contrast`: $Cg_y = \begin{bmatrix}c&0&0\\0&1&0\\0&0&1\end{bmatrix},\quad Co_y = \begin{bmatrix}0.5\\0\\0\end{bmatrix} (c>1) 或 \begin{bmatrix}0\\0\\0\end{bmatrix}(c<=1)$, 只作用于 YUV 域
    - 公式由 $O_r=C_r*I_r$ 改为：$O_y=Cg_y*(I_y-Co_y)+Co_y$，解决 $c>1$ 时，暗部数据也会变亮的问题
    - 改为在 YUV 域生效，避免偏色问题
  - `Saturation`: $S_y = \begin{bmatrix}1&0&0\\0&s&0\\0&0&s\end{bmatrix}$, 只作用于 YUV 域，保持不变
  - `Hue`: $H_y = \begin{bmatrix}1&0&0\\0&cos(h)&-sin(h)\\0&sin(h)&cos(h)\end{bmatrix}$, 只作用于 YUV 域，保持不变
  - `RgbGain`：$G_r = \begin{bmatrix}r_{gain}&0&0\\0&g_{gain}&0\\0&0&b_{gain}\end{bmatrix}$，只作用于 RGB 域，保持不变
    - 非 **One-Step** 实现可以确保 $gain>1$ 时不会导致色偏问题
  - `RgbOffset`：$O_r = \begin{bmatrix}r_{offset}\\g_{offset}\\b_{offset}\end{bmatrix}$，只作用于**输出** RGB 域，保持不变

### eVideo CSC Plan B

- eVideo CSC 软件改进版本B，和方案A的区别主要在于BCSH参数的方案不用
- BCSH 参数的改进方案B：
  - `BCSH`: 4个参数优先在 YUV 域生效，没有 YUV 数据时在 RGB => HSV 域生效
    - 如果是 Y2R，在输入 YUV 域生效
    - 如果是 Y2Y / R2Y，在输出 YUV 域生效
    - 如果是 R2R，在输出 RGB => HSV 域生效，在该域的计算公式如下：
      - `Brightness/Contrast`: $V' = c_g * (V - c_o) + C_o + b$
      - `Saturation`: $S' = s * S$
      - `Hue`: $H' = H + h$
  - `RgbGain`/`RgbOffset`：只在 RGB 域生效
    - 如果是 Y2R / R2R，在输出 YUV 域生效
    - 如果是 R2Y，在输入 RGB 域生效
    - 如果是 Y2Y，不生效

## 其他

**关键差异**

| 对比项 | `RK CSC` | `eVideo CSC` | `eVideo CSC fix` | `rgbOnHsv_*` |
| --- | --- | --- | --- | --- |
| `hue` 映射 | 约 `[-30, 30]` 度 | `[-180, 180]` 度 | `[-180, 180]` 度 | `[-180, 180]` 度 |
| `rgb_gain` 归一化 | 除以 `256` | 除以 `64` | 除以 `64` | 除以 `64` |
| `rgb_offset` 解释 | 偏旧式、和位深有换算关系 | 直接按居中单位映射到像素范围 | 同 `eVideo` | 同 `eVideo` |
| 变换建模 | 以矩阵修正为主 | 仿射变换拼装 | 仿射变换拼装，且域划分更严谨 | 名称上偏特化，当前实现里仍复用 `RK` 主路径 |
| 是否有独立实现 | 有 | 有 | 有 | 当前文件中没有 `On/Off` 的独立实现差异 |

**BCSH 参数对比**

| 参数 | 原始寄存器范围 | `RK` 旧映射归一化基准 | `RK` 映射结果范围 | `eVideo` 归一化基准 | `eVideo` 映射结果范围 |
| --- | --- | --- | --- | --- | --- |
| `hue` | `[0, 511]` | 中心化 `256` | `[-30, 30)` 度 | 中心化 `256` | `[-180, 180)` 度 |
| `saturation` | `[0, 511]` | 归一化 `256` | `[0, 2)` | 归一化 `256` | `[0, 2)` |
| `contrast` | `[0, 511]` | 归一化 `256` | `[0, 2)` | 归一化 `256` | `[0, 2)` |
| `brightness` | `[0, 511]` | 中心化 `256` | `[-1/4, 1/4)` | 中心化 `256` |`[-1, 1)` |
| `rgb_gain` | `[0, 511]` | 归一化 `256` | `[0, 2)` | 归一化 `64` | `[0, 8)` |
| `rgb_offset` | `[0, 511]` | 中心化 `256` | `[-1/8, 1/8)` | 中心化 `256` |`[-1, 1)` |

**代码依据**

- 常量和别名归一化：[get_csc_coefs.py:L64-L91](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coefs.py#L64-L91)
- 参数映射逻辑：[get_bcsh_param_pack](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coefs.py#L278-L351)
- `RK CSC` 路径：[adjust_convert_mat](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coefs.py#L402-L450)
- `eVideo CSC` 路径：[adjust_convert_quad_evideo](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coefs.py#L453-L495)
- `eVideo CSC fix` 路径：[adjust_convert_quad_evideo_fix](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coefs.py#L498-L524)
- 总调度入口：[get_csc_coefs](file:///g:/Codes/gerrit_projects/hwpq_verify/script/csc/get_csc_coefs.py#L594-L635)

**简要结论**

- 真正有独立计算实现的，只有 `RK CSC`、`eVideo CSC`、`eVideo CSC fix` 这 3 类。
- `rgbOnHsv_RgbCfg4YuvOff/On` 在这个文件里主要体现为“采用 eVideo 参数映射”的命名分类，当前没有分出两套不同公式。
- 两个 legacy 名称只是兼容入口，不是新的算法分支，因此本文不再单列它们。

**对比表**

| 算法名称 | 当前状态 | 参数映射方式 | 核心计算路径 | 固定点量化方式 | 主要特点 |
| --- | --- | --- | --- | --- | --- |
| `RK CSC` | 现行算法 | `RK` 旧映射 | `adjust_convert_mat()` | `get_fixed_coefs_mat()` | 传统 RK CSC 路径，基于 `3x3 matrix + range offset` 做调整 |
| `eVideo CSC` | 现行算法 | `eVideo` 映射 | `adjust_convert_quad_evideo()` | `get_fixed_coefs_affine()` | 把整体看成仿射变换，亮度、HS、RGB gain/offset 的组合顺序更明确 |
| `eVideo CSC fix` | 现行算法 | `eVideo` 映射 | `adjust_convert_quad_evideo_fix()` | `get_fixed_coefs_affine()` | `eVideo CSC` 的修正版，对比度/亮度/色度作用域更严格 |
| `rgbOnHsv_RgbCfg4YuvOff` | 现行名称 | `eVideo` 映射 | 在本文件中最终仍走 `adjust_convert_mat()` | `get_fixed_coefs_mat()` | 名义上是 RGB 配置叠加 HSV 路径的 `YuvOff` 版本，但当前文件里无独立公式 |
| `rgbOnHsv_RgbCfg4YuvOn` | 现行名称 | `eVideo` 映射 | 在本文件中最终仍走 `adjust_convert_mat()` | `get_fixed_coefs_mat()` | 名义上是 `YuvOn` 版本，但当前文件里也没有和 `Off` 分开的计算分支 |

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

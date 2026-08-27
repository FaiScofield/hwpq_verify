# Verify Tool UI 使用指南

[TOC]

## 文件信息

文件标识：--

发布版本：v1.0

日期：2026-xx-xx

文件密级：□绝密   □秘密   ■内部资料   □公开

**免责声明**

本文档按"现状"提供，瑞芯微电子股份有限公司（"本公司"，下同）不对本文档的任何陈述、信息和内容的准确性、可靠性、完整性、适销性、特定目的性和非侵权性提供任何明示或暗示的声明或保证。本文档仅作为使用指导的参考。

由于产品版本升级或其他原因，本文档将可能在未经任何通知的情况下，不定期进行更新或修改。

**商标声明**

"Rockchip"、"瑞芯微"、"瑞芯"均为本公司的注册商标，归本公司所有。

本文档可能提及的其他所有注册商标或商标，由其各自拥有者所有。

**版权所有 © 2026 瑞芯微电子股份有限公司**

超越合理使用范畴，非经本公司书面许可，任何单位和个人不得擅自摘抄、复制本文档内容的部分或全部，并不得以任何形式传播。

瑞芯微电子股份有限公司

Rockchip Electronics Co., Ltd.

地址：     福建省福州市铜盘路软件园A区18号

网址：     [www.rock-chips.com](http://www.rock-chips.com)

客户服务电话： +86-4007-700-590

客户服务传真： +86-591-83951833

客户服务邮箱： [fae@rock-chips.com](mailto:fae@rock-chips.com)

---

**概述**

本文档主要介绍瑞芯微算法测试工具 **PQVerifyTool** 的使用。

**修订记录**

| **文档版本** | **工具版本** | **作者** | **审核** | **修改日期** | **修改说明** |
| :---------: | :----------: | :------: | :------: | :---------: | :---------- |
| v1.0 | v1.0 | Vance Wu | - | 2026-xx-xx | 初始版本 |


**读者对象**

本文档主要适用于以下工程师：

- PQ算法开发工程师
- 技术支持工程师
- 画质调试工程师

<div STYLE="page-break-after: always;"></div>

---

## 0. 简介

PQVerifyTool 是瑞芯微 PQ 算法测试工具，用于验证 PQ 算法的原理，对比和测试不同方案的效果。它支持多种输入格式，包括文件、纯色和内置测试图，并提供丰富的输出设置和预览功能。

## 1. IO 模块

`IoUiController`（`ui_impl/io_ui_impl.py`）控制 I/O Tab：输入选择（三选一）、输出设置、分量交换、输入参数猜测与自动重载。通过回调与宿主交互：

- `on_input_loaded(frame, status_message)`：输入帧加载完成通知（宿主据此刷新预览/处理）
- `on_load_config(path)`：加载配置 JSON
- `on_output_changed()`：输出设置变化通知
- `status_callback(msg)`：状态栏提示

### 选择输入（三选一）

- **Use File as Input**：文件加载。`Browse` 选择、`Reload` 重载；`_guess_input_params` 按文件名自动猜测参数：
  - **分辨率**：先读图片头（STB 扩展名用 PIL 取尺寸），再正则 `(\d+)x(\d+)` 匹配文件名
  - **格式**：按后缀与 token 映射（`_YUV_SUFFIX_FMT`/`_RGB_SUFFIX_FMT`）——`.yuv` 默认 `0x3`（YUV444P）、`.rgb` 默认 `0x0`（RGB888）、raw `.bin` 先匹配 YUV token 再匹配 RGB token
  - **色彩空间**：RGB → `1`（full），YUV → `5`（BT.709 full）；输出 format/colorspace 默认跟随输入（之后可手动修改）
- **Use Specified Color**：纯色输入，`R G B` 文本（`_parse_color_text` 解析，回车触发 `_on_set_color_return_pressed`）
- **Use Test Pattern**：内置合成测试图（`build_test_pattern_rgb`，7 种图案），`Value`/`Hue` 固定参数 + `Width`/`Height` 分辨率

帧数：`_recalc_frame_num` 按「文件大小 ÷ 单帧大小」计算帧数，帧索引 0-based，范围 `[0, N-1]`。

### 分量交换（Swap）

- RGB 输入：`Swap R/B`；YUV 输入：`Swap U/V`（`_apply_swap`，勾选后自动重载）
- 测试图/纯色输入不可用（`_update_swap_controls` 控制使能）

### 输出设置

- `Output Dir`：结果保存目录（`get_output_dir()` 供保存方查询）
- `Output Format` / `Output Colorspace`：用户可选；色彩空间选项按格式域刷新（`_refresh_output_colorspace_options`：RGB 域只列 `0/1`、YUV 域列 `2-7`），并按域记住上次选择（`_last_clrspc_rgb`/`_last_clrspc_yuv`），格式在 RGB/YUV 域间切换时恢复
- `Browse/Load Config`：加载配置（`on_load_config` 回调）

### 实现细节

- **色彩空间显示**统一为 `n-name`（无空格）；匹配用 `_find_clrspc_item`（兼容有无空格）
- **装载失败弹窗去重**：参数猜测级联（格式/色彩空间/帧号信号触发的中间重载）期间 `_suppress_load_errors=True` 抑制弹窗，只保留最终一次——一次用户操作最多弹 1 次错误框
- **避免二次重载**：输入格式变化重建 colorspace combo 时 `blockSignals`（`_on_input_format_changed`）
- 输入加载链路：`_load_input_image` → `_emit_input_loaded(frame, status)`；纯色走 `_load_set_color_input`、测试图走 `_on_generate_test_pattern`（`_set_test_pattern_input_fmt` 强制格式）

## 2. Preview 预览页面

`PreviewUiController`（`ui_impl/io_preview_ui_impl.py`）控制 Image Preview dock：双 `QGraphicsScene` 视图、像素读数与冻结、图像保存、预览缩放。挂载为可移动/浮动/关闭的 `QDockWidget`（默认底部，`View → Preview` 显示/隐藏）。

### 预览类型

- **BothInLeft**（默认）：单窗口显示，默认显示处理结果，勾选 `Show Left Input` 显示输入
- **SideBySide**：左右并排，左=输入、右=输出（右预览固定显示输出）
- `set_acm_enabled` 可影响 BothInLeft 布局（ACM 处理时切换）

### 预览缩放与工作分辨率

- `slider_preview_scale`（10%-100%）：预览缩放
- `get_work_size(src_w, src_h)`：scale<1 时按 scale 降采样返回预览处理分辨率，保证调参响应速度；源尺寸 ≤ 预览尺寸时逐像素一致
- `set_full_res_output_provider`：预览按降采样运行时，保存动作经该 provider 在源分辨率重算输出，保证保存结果精确

### 像素读数与冻结

- 鼠标移动：`_on_mouse_move_left/right` → `_fill_readout`，信息行显示坐标 + 输入/输出像素 RGB/HSV 读数（`_pixel_readout_provider(x, y, role)` 提供文本）
- **空格冻结**（`handle_key_press`）：冻结后出现十字标记（`_frozen_marker_item`），信息行固定该像素读数；`pixel_selection_callback` 把选中像素通知宿主（HSV 页 `on_preview_pixel_selection` 据此同步读数/处理）
- 视图坐标映射：`_map_view_pos_to_image`（graphicsView → pixmap → 图像像素）

### 图像显示与保存

- 显示链路：`set_input_image`/`set_output_image` → `_frame_to_qimage`（YUV/RGB 帧转 QImage，带 yuv444/rgb444/qimage 缓存）→ 场景 pixmap
- 保存：`Save Left/Right Image` → `_ask_save_target`（确认保存名/扩展名）→ `_save_assets`，默认存到 `Output Dir`；输出帧经 `_get_output_for_save`（全分辨率 provider 优先）

## 3. CSC 模块

### TODO

- [x] 增加CSC系数Swap Combo，只改变显示的系数值，不改变实际使用的系数



## 4. BCSH 模块

### 统一处理流水线（1️⃣~6️⃣）

所有处理域共用同一条流水线（`_process_frame` → `_process_frame_rgb`/`_process_frame_yuv`）：

1️⃣ 原始输入直读 → 2️⃣ 输入 CSC 到处理域 → 3️⃣ 域转换 → 4️⃣ BCSH 调整 → 5️⃣ 回 full-range RGB/YUV → 6️⃣ 输出 CSC 到输出格式/色彩空间

- **步骤 2️⃣（输入 CSC）**：RGB 系处理域转 full-range RGB；YCbCr 处理域转 yuv444p full-range（输入 YUV 不做钳位）。
- **步骤 5️⃣（回处理域）**：RGB 系恒钳 $[0,1]$；YCbCr 按 `y2yClipType` 处理。
- **步骤 6️⃣（输出 CSC）**：YCbCr 处理域 YUV 输出直接编码（不经 RGB）；RGB 输出需 YUV→RGB 桥。

### 处理域（Adjust Field）

- **RGB 系**（HSV/HSI/HSL/HCY/HSP/Lch/RGB）：full-range RGB ↔ 对应域，域内 BCSH 调整（`_process_frame_rgb`）。
- **YCbCr**（YUV 系）：处理域为 yuv444p full-range，$Y$ 通道调 B/C，$Cb/Cr$ 极坐标系调 H(角度)/S(极径)（`_process_frame_yuv`）。

### 输入/输出 CSC 与钳位/归一化控件

| 控件 | 语义 | 档位 |
| ---- | ---- | ---- |
| `y2rClipType` | YUV→RGB 转换钳位（RGB 系输入 YUV→RGB、YCbCr 预览、YCbCr→RGB 输出桥） | HardClip / SoftClip / ConstHue |
| `y2yClipType` | YCbCr 处理域步骤 5️⃣ 的 YUV 数据钳位 | HardClip / ClipChroma / ClipChromaSoft |
| `normYuvChroma` | YCbCr 域 S 归一化方式（仅 YCbCr 域 **且 y2yClipType=HardClip** 时可选） | OFF / NormByPix / NormBySec |

**使能逻辑**（`_update_clip_enables`，在 `_init_state`/`_on_adjust_field_changed`/`_process_frame` 末尾调用）：

- `y2yClipType` / `normYuvChroma`：仅 `adjustField == YCbCr` 启用。
- `y2rClipType`：存在 y2r 节点才启用——`adjustField == YCbCr`（预览 y2r 恒存在，输出 RGB 桥亦然）或（输入为 YUV 且非 YCbCr）（输入 y2r 节点）。
- **互斥**：`y2yClipType` 切到非 HardClip 时，NormBy* 自动回落 OFF（`_on_y2y_clip_changed`），避免"UI 禁用但逻辑仍生效"；NormByPix 会短路 y2y 钳位（见下），NormBySec 视为其简化实现，保持相同互斥行为。
- **互斥**：`normYuvChroma` 切到非 OFF 时，modeH 的 Keep 系列（`ModeAddKeepS`/`ModeAddKeepYH`）禁用并回落 `ModeAdd`（`_on_norm_chroma_changed`）——NormByPix 下重建天然域内、Keep 系列恒等短路；NormBySec 语义同样由归一化接管。`_set_mode_h_items_enabled` 同时按处理域与 norm 状态刷新项使能（Keep* 仅 YCbCr 域 **且 normYuvChroma=OFF** 可选）。

### RGB 系处理域（简述）

- **步骤 2️⃣**：RGB 输入 limited→full 展开后**直接硬钳**（不依赖 `y2rClipType`）；YUV 输入转 RGB 后按 `y2rClipType` 钳位。
- **步骤 4️⃣**：`adjust_rgb`——C/V 逐通道（Contrast + δB）、S 灰阶混合（`MixGray_BT709`/`BT601`）、H 按 modeH 生效（`ModeAdd` 六边形加法 / `RotateOnGray` 绕灰轴 Rodrigues 旋转，严格正交、往返无累积误差）。
- **步骤 6️⃣**：RGB 输出直接编码；YUV 输出经 `rgb_to_yuv`（内部钳位量化）。

### YCbCr 处理域

处理域为 yuv444p full-range（归一化 $(Y, Cb, Cr)$，$Cb/Cr$ 去中心 0.5：$Y\in[0,1]$、$Cb,Cr\in[-0.5,0.5]$）。YCbCr 域下 B 通道即 Y（亮度）。

#### 1. H/S 极坐标与 S 归一化（步骤 3️⃣）

$$\text{radius} = \sqrt{Cb^2+Cr^2},\qquad \theta = \text{atan2}(Cr, Cb)\ \text{（度，[0,360)）}$$

S 按 `normYuvChroma` 归一化：

- **OFF**：$s = \text{radius}$（绝对极径，不归一化）。
- **NormByPix**：$s = \dfrac{\text{radius}}{r_{\max}(Y,\theta)}$，其中该 $(Y,\theta)$ 下的 RGB 色域边界极径为
  $$r_{\max}(Y,\theta)=\min\!\Big(\min_{k_i>0}\tfrac{1-Y}{k_i},\ \min_{k_i<0}\tfrac{-Y}{k_i}\Big),\qquad k_i=a_i\cos\theta+b_i\sin\theta$$
  $s\in[0,1]$ 保证落在色域内 ⇒ **Y/S/H 三参数解耦**，任意调整不越界、色相不变（`_gamut_r_max`/`_gamut_s_norm`）。
- **NormBySec**：$s = \text{radius}/\text{\_CHROMA\_MAX}$，其中 $\text{\_CHROMA\_MAX}=\max_{6\text{ 纯色}}\lVert(Cb,Cr)\rVert$（`_bt_chroma_max`；BT.709=0.5957，在 G/M 方向）。绝对比例，**不保证域内**。

#### 2. BCSH 调整（步骤 4️⃣）

- **H**：直接旋转极角 $\theta_a=(\theta+\delta H)\%360$（`adjust_hsv` 的 dh 即极角加性旋转，不再经 HSV 色相中转）；`hue_sync` 经 LUT（`hue_ycbcr_to_hsv`/`hue_hsv_to_ycbcr`）仅作读数显示（H/H'SY）与指定色相 range。
- **S**：`adjust_hsv` 对 $s$ 做加性/乘性（`ModeAdd` $s'=\mathrm{clip}(s+ds)$ / `ModeMul` $s'=\mathrm{clip}(s\cdot ds)$）。
- **B/C**：Y 通道——Contrast 乘性 + δB（`mode_b`：`ModeAdd` 加性 / `ModeMul` 乘性 / `NegMulPosRat` 负压正白）。

#### 3. 重建与钳位（步骤 5️⃣）

$$\text{radius}_a = \begin{cases} s_a\cdot r_{\max}(Y_a,\theta_a) & \text{NormByPix}\\ s_a\cdot\text{\_CHROMA\_MAX} & \text{NormBySec}\\ s_a & \text{OFF}\end{cases},\qquad (Cb_a,Cr_a)=\text{radius}_a(\cos\theta_a,\ \sin\theta_a)$$

- **NormByPix**：重建天然在域内 ⇒ `yuv_5_disp = yuv_5_raw` 短路（调整结果与输入按 w 的凸组合仍落在 RGB 色域内——RGB 色域为凸集，无需钳位）；5a/5b 补偿在域内自动恒等。
- **NormBySec/OFF**：重建可能越界 ⇒ 由 `y2yClipType` 兜底（`HardClip` YUV 范围硬钳 / `ClipChroma` 色度压缩保色相 / `ClipChromaSoft` 软拐角）。

**5a. H 旋转后补偿（modeH，仅 YCbCr 域）**：

- `ModeAddKeepS`（保 S 调 Y）：色度不变，按 Y2R 通道钳位量补 $\Delta Y$ = 缺量 − 超量（只补回实际被钳掉的部分，不直接顶到可行区间边界）：
  $$\Delta Y=\max(0,-\min_i RGB_i)-\max(0,\max_i RGB_i-1),\qquad Y'=\mathrm{clip}(Y_a+\Delta Y,0,1)$$
- `ModeAddKeepYH`（保 Y 调 S）：Y 不变，把色度极径缩到该 $(Y,\theta)$ 下的色域边界（`_gamut_clip_chroma`），保极角/色相、向灰压缩。

**5b. 亮度超界处理（modeB，仅 YCbCr 域）**：

拉大 δB 抬高亮度后，一旦某通道顶到色域边界（$\max_i RGB_i>1$，如蓝色像素 B 顶满 255），继续增大 δB 的多余亮度只能分给其他通道（等于加白），色相会偏移。`ModeAddKeepHS` 与 `ModeAddKeepH` 在该场景自动保持色相：

- **`ModeAddKeepHS`（Y 双向封顶，保饱和保色相）**：把 Y 钳到该色度下的色域可行区间，色度 $(Cb_a, Cr_a)$ 不变：
  $$Y_{lo}=\max_i(-k_i),\qquad Y_{hi}=\min_i(1-k_i),\qquad Y'=\mathrm{clip}(Y_a,\ Y_{lo},\ Y_{hi})$$
  $Y_a\in[Y_{lo},Y_{hi}]$ 时不处理；高侧 $Y_a>Y_{hi}$ 时封顶（如蓝色 B=255 处，不再变亮），低侧 $Y_a<Y_{lo}$ 时封底（如蓝色 G 触 0 处，不再变暗）。色度不变 ⇒ YCbCr 极角不变、RGB 通道差值不变 ⇒ **色相恒定**，结果停留在色域边界（最饱和），代价是越过边界后继续拉大/拉小 δB 亮度不再变化。

- **`ModeAddKeepH`（等比缩回，双向保色相）**：
  - 高侧（$\max_i RGB_i>1$，即 $Y_a>Y_{hi}$）：负值先钳 0，再按 $\max_i RGB_i$ 等比缩放使最大通道回到 1（等价 ConstHue），随后转回 YUV：
    $$RGB'_i=t\cdot\max(RGB_i,0),\qquad t=\min\!\Big(1,\tfrac{1}{\max_i RGB_i}\Big),\qquad (Y',Cb',Cr')=R2Y\cdot RGB'$$
    通道比例不变 ⇒ **色相恒定**；δB 越大 $t$ 越小、颜色向白去饱和，代价是亮度继续上升但饱和度下降。
  - 低侧（$\min_i RGB_i<0$，即 $Y_a<Y_{lo}$）：保持 $Y_a$，把色度按 $s=\min\!\big(1,\tfrac{Y_a}{Y_{lo}},\tfrac{1-Y_a}{1-Y_{hi}}\big)$ 向 0 缩放使最小通道回到 0，色相恒定、向黑去饱和：
    $$(Y',Cb',Cr')=(Y_a,\ s\cdot Cb_a,\ s\cdot Cr_a)$$

#### 4. 预览与输出

- **预览帧**：`yuv_5_disp` → YUV→RGB → `y2rClipType` 钳位（Hard/Soft/ConstHue）→ RGB 帧显示（`_yuv_to_preview_frame`）。
- **输出**：YUV 输出直接编码（步骤 5️⃣ 已完成色域处理，`_yuv_norm_to_output_frame`）；RGB 输出经 YUV→RGB 桥 + `y2rClipType` 钳位（`_to_output_frame_yuv`）。

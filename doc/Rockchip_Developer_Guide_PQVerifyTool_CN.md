# RK Verify Tool UI 开发指南

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

1️⃣ 原始输入直读 → 2️⃣ 确保 full-range RGB/YUV → 3️⃣ 到处理域的转换（HSV/HSI/HSL/HCY/HSP/Lch/YCbCr等） → 4️⃣ BCSH 调整 → 5️⃣ 回 full-range RGB/YUV → 6️⃣ 输出 CSC 到输出格式/色彩空间

- **步骤 2️⃣（输入 CSC）**：RGB 系处理域转 full-range RGB；YCbCr 处理域转 yuv444p full-range。
- **步骤 5️⃣（回处理域）**：RGB 系恒钳 $[0,1]$；YCbCr 按 `y2yClipType` 处理。
- **步骤 6️⃣（输出 CSC）**：YCbCr 处理域 YUV 输出直接编码（不经 RGB）；RGB 输出需 YUV→RGB 桥。

### 处理域（Adjust Field）

- **RGB 系**（HSV/HSI/HSL/HCY/HSP/Lch/RGB）：full-range RGB ↔ 对应域，域内 BCSH 调整（`_process_frame_rgb`）。
- **YCbCr**（YUV 系）：处理域为 yuv444p full-range，$Y$ 通道调 B/C，$Cb/Cr$ 极坐标系调 H(角度)/S(极径)（`_process_frame_yuv`）。

### 处理色域与 RGB 互转公式（步骤 3️⃣/5️⃣ 的域转换）

统一记号：$\mathrm{clip}(x)=\min(\max(x,0),1)$；$R,G,B\in[0,1]$，色相 $H\in[0,360)$，其余分量 $\in[0,1]$。以下即 `_DOMAIN_CONVERTERS` 各色域的 `to_domain`/`from_domain`（`script/bcsh/hsv_adjust.py`）。

#### HSV（六棱锥）

**RGB→HSV:**

- $M=\max(R,G,B)$，$m=\min(R,G,B)$，$C=M-m$
- $V=M$
- $S=C/V$（$V=0$ 时 $S=0$，除 0 保护）
- $H$ 按最大通道分扇区：
  - $M=R$ 时 $H=60^\circ\cdot((G-B)/C+6) \% 60$；
  - $M=G$ 时 $H=60^\circ\cdot((B-R)/C+2)$；
  - $M=B$ 时 $H=60^\circ\cdot((R-G)/C+4)$

**HSV→RGB:**

- $M=V$，$C=V\cdot S$，$m=M-C$；
- 扇区 $\mathrm{seg}=\lfloor H/60\rfloor\bmod 6$，段内位置 $f=H/60-\mathrm{seg}$，中间通道 $\mathrm{mid}=m+C\cdot f$（seg 偶）或 $M-C\cdot f$（seg 奇）：

  | seg | 0 | 1 | 2 | 3 | 4 | 5 |
  | --- | - | - | - | - | - | - |
  | (R,G,B) | (M,mid,m) | (mid,M,m) | (m,M,mid) | (m,mid,M) | (mid,m,M) | (M,m,mid) |

- $S=0$（灰/黑）直接返回 $V$。

**硬件计算难度: 简单** ✔️

- 常量除法
- 变量除法，需要引入定点导数表

#### HSI（Gonzalez 模型）

**RGB→HSI:**

- $I=(R+G+B)/3$
- $S=1-\min(R,G,B)/I$（$I=0$ 全黑时 $S=0$）
- $\theta=\arccos\dfrac{0.5\big((R-G)+(R-B)\big)}{\sqrt{(R-G)^2+(R-B)(G-B)}}$
- $H=\theta$（$B\le G$）或 $360^\circ-\theta$（$B>G$）

**HSI→RGB：**（120° 三段闭式）

- 扇区 0（$0\le H<120$）：$B=I(1-S)$，$R=I\big(1+S\cos H/\cos(60^\circ-H)\big)$，$G=3I-R-B$
- 扇区 1（$120\le H<240$）：$R=I(1-S)$，$G=I\big(1+S\cos(H-120^\circ)/\cos(60^\circ-(H-120^\circ))\big)$，$B=3I-R-G$
- 扇区 2（$240\le H<360$）：$G=I(1-S)$，$B=I\big(1+S\cos(H-240^\circ)/\cos(60^\circ-(H-240^\circ))\big)$，$R=3I-G-B$

**硬件计算难度: 复杂** ❌

- 常量除法
- 三角函数，存在多处
- 平方根

#### HSL（双锥模型）

**RGB→HSL：**

- $L=(M+m)/2$
- $S=(M-m)/(1-|2L-1|)$（$L=0$ 或 $1$ 时 $S=0$）
- $H$ 与 HSV 相同的六边形扇区公式

**S 的 min/max 展开与病态放大**（把 $C=M-m$、$L=(M+m)/2$ 代入 $S$）：

$$S=\frac{M-m}{1-|M+m-1|}=\begin{cases}\dfrac{M-m}{M+m}, & M+m\le1\ (L\le0.5)\ \text{下半锥}\\[6pt] \dfrac{M-m}{2-(M+m)}, & M+m\ge1\ (L\ge0.5)\ \text{上半锥}\end{cases}$$

- 上半锥（$L\ge0.5$）：$S=1\iff M=1$——**只要最大通道满白（$M=1$），$S$ 恒等于 1**，与色度 $C=M-m$ 大小无关；如 (255,255,253) 的 $C=2/255$ 但 $S=1$。
- 下半锥（$L\le0.5$）：$S=1\iff m=0$——**只要最小通道全黑（$m=0$），$S$ 恒等于 1**；如 (2,0,1) 的 $C=2/255$ 但 $S=1$。
- 两锥顶点（纯白 $(1,1,1)$ / 纯黑 $(0,0,0)$）为 $0/0$，约定 $S=0$。

即"病态放大"（$C$ 极小却 $S=1$）只出现在 $M=1$（近白）或 $m=0$（近黑）的像素。**这正是 HSL 域 S Tolerance 改用色度 $C$ 门控（而非 $S$）的原因**——这两类像素 $S$ 恒为 1，按 $S$ 判断永远高于阈值、保护失效。

**HSL→RGB：**
- $C=(1-|2L-1|)\cdot S$，$H'=H/60$，$X=C\cdot(1-|H'\bmod 2-1|)$，$m=L-C/2$；
- 按扇区取基值（$0:(C,X,0)$、$1:(X,C,0)$、$2:(0,C,X)$、$3:(0,X,C)$、$4:(X,0,C)$、$5:(C,0,X)$）赋给 (R,G,B)，最后各通道 $+m$。

**硬件计算难度: 简单** ✔️

- 常数除法
- 变量除法，需要引入定点导数表

#### HCY（Hue/Chroma/Luma，Rec.601 luma）

**RGB→HCY：**

- $Y=0.299R+0.587G+0.114B$
- $H$ 六边形色相（与 HSV 同角）
- 纯色相斜坡（$h=H/360$）：$h_r=\mathrm{clip}(|6h-3|-1)$，$h_g=\mathrm{clip}(2-|6h-2|)$，$h_b=\mathrm{clip}(2-|6h-4|)$
- 纯色 luma $Z=0.299h_r+0.587h_g+0.114h_b$；
- 色度 $C=(M-m)\cdot\begin{cases}Z/Y,&Y<Z\\(1-Z)/(1-Y),&Y\ge Z\end{cases}$（按该色相/亮度可承载的最大色度归一化，同 Y 视觉亮度一致）

**HCY→RGB：**

- 色度反归一化 $C=\begin{cases}C\cdot Y/Z,&Y<Z\\C\cdot(1-Y)/(1-Z),&Y\ge Z\end{cases}$，
- $R=(h_r-Z)\cdot C+Y$，$G=(h_g-Z)\cdot C+Y$，$B=(h_b-Z)\cdot C+Y$。

**硬件计算难度: 中等** ✔️

- 常数除法
- 变量除法数量较多

#### HSP（Hue/Saturation/Perceived brightness）

**RGB→HSP：**

- $P=\sqrt{0.299R^2+0.587G^2+0.114B^2}$（感知亮度，通道平方加权）
- $S=1-\min/\max$（与 HSV 相同）
- $H$ 六边形色相（灰色取 0）

**HSP→RGB：**

- 6 扇区 × 全饱和/非全饱和共 12 段闭式求解（与 colorjs `hsp.js` 一致）。
- 非全饱和（$s<1$，$\mathrm{mm}=1-s$）：
- 最小通道 $\mathrm{base}$ 由 $P^2=w_{max}\cdot\max^2+w_{mid}\cdot\mathrm{mid}^2+w_{min}\cdot\min^2$ 反解（$\max=\mathrm{base}/\mathrm{mm}$，$\mathrm{mid}=\mathrm{base}+h'\cdot(\max-\mathrm{base})$，$h'$ 为段内位置）；
- 全饱和（$s=1$）：$\min=0$，$\max=P/\sqrt{w_{max}+w_{mid}\,h'^2}$，$\mathrm{mid}=\max\cdot h'$。

**硬件计算难度: 复杂** ❌

- 平方根
- 变量除法

#### Lch（CIELAB 柱坐标，sRGB D65）

**RGB→Lch：**
- sRGB 线性化（$R\le0.04045$ 时 $R/12.92$，否则 $((R+0.055)/1.055)^{2.4}$）→
- D65 矩阵转 XYZ → Lab（$f(t)$ 分段：→
  - $t>\epsilon$ 取 $t^{1/3}$，否则线性段；
  - $L^*=116f(Y/Y_n)-16$
  - $a^*=500(f(X/X_n)-f(Y/Y_n))$
  - $b^*=200(f(Y/Y_n)-f(Z/Z_n))$
- 柱坐标：$L=L^*/100$，$C=\sqrt{a^{*2}+b^{*2}}$，$h=\mathrm{atan2}(b^*,a^*)\bmod 360$，$s=C/C_{max}$（$C_{max}\approx134$，sRGB 域内最大色度）。

**Lch→RGB**：

- $C=s\cdot C_{max}$，$a^*=C\cos h$，$b^*=C\sin h$ →
- Lab → XYZ → sRGB（逆线性化），越界钳 $[0,1]$。

**硬件计算难度: 复杂** ❌

- 常数除法
- 立方根
- 幂运算
- 变量除法
- 三角函数

#### RGB

恒等映射（`_rgb_domain_to`/`_rgb_domain_from`，仅钳位 $[0,1]$），无需转换。

#### YCbCr（yuv444p full-range）

- 处理域为归一化 $(Y,Cb,Cr)$，$Cb/Cr$ 去中心 0.5：$Y\in[0,1]$、$Cb,Cr\in[-0.5,0.5]$。
- RGB↔YUV 用色彩空间矩阵（BT.601/709/2020，`_get_csc_matrices`）：$(Y,Cb,Cr)=\mathbf{R2Y}\cdot(R,G,B)^\top$，$(R,G,B)=\mathbf{Y2R}\cdot(Y,Cb,Cr)^\top$。
- 输入 RGB → YCbCr 处理域用 BT.709（cs=5）；输入 YUV 保持输入矩阵（不做钳位）。
- H/S 极坐标、S 归一化与重建公式见「YCbCr 处理域」§1/§3。

### 输入/输出 CSC 与钳位/归一化控件

| 控件 | 语义 | 档位 |
| ---- | ---- | ---- |
| `y2rClipType` | YUV→RGB 转换钳位（RGB 系输入 YUV→RGB、YCbCr 预览、YCbCr→RGB 输出桥） | HardClip / SoftClip / ConstHue |
| `y2yClipType` | YCbCr 处理域统一色域处理策略（步骤 3️⃣/5️⃣） | HardClip / ClipChroma / ScaleChromaPix / ScaleChromaSec / CompLumaOnly / CompLumaFirst |

#### `y2rClipType` 档位详解（YUV→RGB 转换钳位，`_clip_rgb`）

作用节点：RGB 系输入 YUV→RGB（步骤 2️⃣）、YCbCr 预览、YCbCr→RGB 输出桥。输入为 full-range RGB（可能越界，如 $R<0$ 或 $B>1$），按以下方式钳回 $[0,1]$：

- **HardClip**（逐通道硬钳）：$RGB'_i=\mathrm{clip}(RGB_i)$——实现最简单，但逐通道独立钳位会破坏通道比例，越界/高饱和颜色可能色相偏移。
- **SoftClip**（zentone `soft_clip` 移植，参考 https://docs.rs/zentone/latest/zentone/gamut/fn.soft_clip.html ，色相保持软钳）：负值先钳 0；若 $\max_i RGB_i\le1$ 直接返回；否则按最大/中间/最小通道排序（$hi\ge mid\ge lo$）：
  $$hi'=\min(hi,1),\qquad lo'=\min(lo,1),\qquad t=\frac{mid-lo}{hi-lo},\qquad mid'=lo'+(hi'-lo')\,t$$
  即 $hi$ 钳到 1、$lo$ 钳到 $\min(lo,1)$，$mid$ 按段内比例 $t$ 线性插值；三通道相等时映射到 $\min(hi,1)$。

  - **不对称特点**：与 zentone 参考实现一致（负值在"保色相步骤"之前硬钳 0，$t$ 在钳位后的值上计算）——该算法**只在高侧（$\max_i RGB_i>1$）做保比例的软压缩**，高侧通道比例保持 ⇒ 色相不变；而**低侧（$\min_i RGB_i<0$）是硬钳 0**，负通道在计算 $t$ 前即被丢弃，欠饱和越界像素的通道比例被破坏、可能色相偏移。
  - **保低侧饱和度**：负通道钳到 0 是"最饱和"的边界处理（与 HardClip 低侧一致），**不降低欠饱和像素的饱和度**——这是刻意取舍：若需两侧都保色相，可用对称方案（在原始值上计算 $t=\frac{mid-mn}{mx-mn}$ 再钳两端）或灰轴压缩（`ConstHue` / `ClipChroma`），但会牺牲低侧饱和度。
- **ConstHue**（恒定色相等比例缩放）：负值先钳 0，再按同一比例 $s$ 缩放使最大通道回到 1（$\max_i RGB_i\le1$ 时恒等）：
  $$RGB'_i=s\cdot\max(RGB_i,0),\qquad s=\min\!\Big(1,\tfrac{1}{\max_i RGB_i}\Big)$$
  通道比例不变 ⇒ 色相不变；越界部分被等比压回，颜色不发淡（$s<1$ 时整体降饱和）。

  - **同样存在低侧不对称**：负通道先硬钳 0（缩放前后钳位等价，因为 $\max(RGB,0)\cdot s=\max(RGB\cdot s,0)$，$s>0$）——高侧（$\max_i RGB_i>1$）等比缩放保色相；低侧（$\min_i RGB_i<0$）负通道被硬钳 0，欠饱和越界像素通道比例被破坏、可能色相偏移。低侧要保色相需用灰轴压缩（`ClipChroma`），代价是低侧降饱和。

#### `y2yClipType` 档位详解（YCbCr 域统一色域处理策略，步骤 3️⃣/5️⃣）

合并了原 `y2yClipType`、modeH 的 Comp* 与 modeB 的 Keep*。记 $r=\sqrt{Cb^2+Cr^2}$、$\theta=\mathrm{atan2}(Cr,Cb)$，$k_i=a_i\cos\theta+b_i\sin\theta$（$a_i,b_i$ 为 $\mathbf{Y2R}$ 矩阵的 $Cb/Cr$ 列系数），该 $(Y,\theta)$ 下 RGB 色域边界极径：
$$r_{\max}(Y,\theta)=\min\!\Big(\min_{k_i>0}\tfrac{1-Y}{k_i},\ \min_{k_i<0}\tfrac{-Y}{k_i}\Big)$$

- **HardClip**（YUV 范围硬钳）：$Y'=\mathrm{clip}(Y,0,1)$，$Cb'=\mathrm{clip}(Cb,-0.5,0.5)$，$Cr'=\mathrm{clip}(Cr,-0.5,0.5)$——逐分量独立硬钳，不保色相。
- **ClipChroma**（恒定色相色度压缩，= 原 `ModeAddCompS`）：保持 $Y$ 与极角 $\theta$ 不变，把色度极径缩到色域边界（$r>r_{\max}$ 时，`_gamut_clip_chroma`）：
  $$r'=\min(r,\,r_{\max}),\qquad (Cb',Cr')=\frac{r'}{r}\,(Cb,Cr)$$
  极角不变 ⇒ 色相保持，代价是越界像素降饱和。
- **ScaleChromaPix**（原 `NormByPix`）：$S$ 按像素边界归一化 $s=\dfrac{r}{r_{\max}(Y,\theta)}$（`_gamut_s_norm`）。$s\in[0,1]$ 保证落在 RGB 色域内 ⇒ **Y/S/H 三参数解耦**，任意调整不越界、色相不变；重建 $r'=s'\cdot r_{\max}(Y',\theta')$ 天然域内，硬钳恒等。
- **ScaleChromaSec**（原 `NormBySec`）：$S$ 按全局最大归一化 $s=\dfrac{r}{\text{\_CHROMA\_MAX}}$（$\text{\_CHROMA\_MAX}=\max_{6\text{ 纯色}}\lVert(Cb,Cr)\rVert$，`_bt_chroma_max`；BT.709=0.5957，在 G/M 方向）。绝对比例，**不保证域内**；重建 $r'=s'\cdot\text{\_CHROMA\_MAX}$ 可能越界，越界像素按 `HardClip` 兜底。
- **CompLumaOnly**（原 `ModeAddCompY`，保 S 调 Y）：见「YCbCr 处理域」§3 亮度补偿。
- **CompLumaFirst**（原 `ModeAddCompYS`，Y 优先、S 兜底）：见「YCbCr 处理域」§3 亮度补偿。

> 已删除：`ClipChromaSoft`（软拐角档）、`ModeAddKeepHS`（可行时与 `CompLumaOnly` 等价）、`ModeAddKeepH`（双机制 + RGB 往返，实现最复杂）。

### 步骤 4️⃣ BCSH 调整公式（ModeB/C/S/H）

统一记号：
- $\mathrm{clip}(x)$ 钳位到 $[0,1]$（色相角度域 $[0,360)$）；
- $x$ 为被调整通道——RGB 域为逐通道 $R/G/B$，圆柱色域为亮度/色相/饱和度通道，YCbCr 域为 $Y$（B/C）或极角/极径（H/S）。
- 控件参数：$\delta B$（`deltaB`）、$g_c$（`gainC`）、$\delta S$（`deltaS`）、$\delta H$（`deltaH`）、`tolerance_s`。
- 执行顺序 **C → B → S → H**。

#### C（Contrast，modeC）

$g_c\in[0,4]$ 中性 1；TanSlant/FastStone 参数 $c\in[-1,1]$ 中性 0。

| 模式 | 公式 | 适用域 |
| ---- | ---- | ---- |
| GainAtMid（默认） | $x'=\mathrm{clip}\big((x-0.5)\,g_c+0.5\big)$（过 0.5 中点，最大斜率为$g_c$的最大值） | 所有域 |
| GainAtZero | $x'=\mathrm{clip}(g_c\,x)$（过 0 原点） | 所有域 |
| GainAtBoth | $g_c<1$：$x'=\mathrm{clip}(g_c\,x)$；$g_c\ge1$：$x'=\mathrm{clip}\big((x-0.5)\,g_c+0.5\big)$ | 所有域 |
| TanSlant | $x'=\mathrm{clip}\big((x-0.5)\tan((c+1)\pi/4)+0.5\big)$（过 0.5 中点，最大斜率为♾️） | 所有域 |
| FastStone | 逐通道 Levels 拉伸 $x'=\mathrm{clip}(k\,x+b)$，$c$ 归一化为 $[-1,1]$：$c\ge0$ → $k=1+1.651c$，$b=(0.338-117.59c)/255$；$c<0$ → $k=1+0.911c+1.09c^2+0.523c^3$，$b=(-65c-78.2c^2-37.5c^3)/255$ | 仅 RGB 域 |

#### B（Brightness，modeB）

$\delta B\in[-1,1]$ 中性 0；ModeMul $g_v\in[0,4]$ 中性 1。在 modeC 输出上施加。

| 模式 | 公式 | 适用域 |
| ---- | ---- | ---- |
| ModeAdd（默认） | $x'=\mathrm{clip}(x+\delta B)$ | 所有域 |
| ModeMul | $x'=\mathrm{clip}(x\,g_v)$ | 所有域 |
| NegMulPosRat | $\delta B<0$：$x'=\mathrm{clip}(x(1+\delta B))$；$\delta B>0$：$x'=\mathrm{clip}(x+\delta B(1-x))$ | 所有域 |

#### S（Saturation，modeS）

圆柱色域（HSV/HSI/HSL/HCY/HSP/Lch 的 S 通道、YCbCr 的色度极径 $s$）：

| 模式 | 公式 | 量程 / 中性 |
| ---- | ---- | ---- |
| ModeAdd | $s'=\mathrm{clip}(s+\delta S)$ | $[-1,1]$ / 0 |
| ModeMul（默认） | $s'=\mathrm{clip}(s\,g_s)$ | $[0,4]$ / 1 |
| NegMulPosRat（算法库支持，UI 未开放） | $\delta S<0$：$s'=\mathrm{clip}(s(1+\delta S))$；$\delta S>0$：$s'=\mathrm{clip}(s+\delta S(1-s))$ | $[-1,1]$ / 0 |

RGB 域灰阶混合（仅 RGB 处理域，S 恒为灰阶混合）：

$$x'=\mathrm{clip}\big(\mathrm{scale}\cdot x+(1-\mathrm{scale})\,g\big),\qquad g=\begin{cases}0.2126R+0.7152G+0.0722B&\text{BT.709}\\0.299R+0.587G+0.114B&\text{BT.601}\end{cases}$$

- `MixGray_BT709` / `MixGray_BT601`，$\mathrm{scale}=\delta S\in[0,2]$ 中性 0
- 等价 $g+\mathrm{scale}\,(x-g)$：绕灰轴径向缩放，线性域严格保色相；$\mathrm{scale}>1$ 放大越界后逐通道硬钳可能色相偏移

S Tolerance 门控（所有 S 模式）：$s<\mathrm{tolerance\_s}$（默认 0.0025）的像素不做增色（放大），减色/中性始终允许——即 $\delta S>0$、$g_s>1$、$\mathrm{scale}>1$ 时受保护像素保持原样。**HSL 处理域**下改为对色度 $C=M-m$ 判断（$C<\mathrm{tolerance\_s}$ 即 8bit 的 $(M-m)<\mathrm{tolerance\_s}\times255$），且对受保护像素做**输出色度封顶** $C'=S'\cdot(1-|2L'-1|)\le\mathrm{tolerance\_s}$——规避 L 近黑/白时 HSL 的 $S$ 病态放大在亮度/对比度变动下被“变现”成颜色爆炸（如近白像素变黄）。

#### H（Hue，modeH）

目标角度由 Hue Goal 决定：

- `SameOffset`（默认）：$\mathrm{angle}=\delta H$（加性偏移，$[-180,180]^\circ$ 中性 0）
- `SameTarget`：$\mathrm{progress}=\mathrm{clip}(\delta H/100,0,1)$，$\mathrm{arc}=\big((\mathrm{target}-h+180)\bmod 360\big)-180$（最短有符号弧），$\mathrm{angle}=\mathrm{progress}\cdot\mathrm{arc}$（$\delta H\in[0,100]$ 表示旋转进度 %）

生效方式：

| 模式 | 公式 | 适用域 |
| ---- | ---- | ---- |
| ModeAdd（默认） | 圆柱色域：$h'=(h+\mathrm{angle})\bmod 360$（S/V 不变）；RGB 域：经 HSV 中转六边形加法（$RGB\to HSV\to h'=(h+\mathrm{angle})\bmod 360\to RGB$，S/V 不变）；YCbCr 域：直接旋转极角 $\theta'=(\theta+\mathrm{angle})\bmod 360$ | 所有域 |
| RotateOnGray | 绕灰色轴 $(1,1,1)/\sqrt3$ Rodrigues 旋转（严格正交，灰阶不变，往返无累积误差） | 仅 RGB 域 |

### RGB 系处理域（简述）

- **步骤 2️⃣**：RGB 输入 limited→full 展开后**直接硬钳**（不依赖 `y2rClipType`）；YUV 输入转 RGB 后按 `y2rClipType` 钳位。
- **步骤 4️⃣**：`adjust_rgb`——C/V 逐通道（Contrast + δB）、S 灰阶混合（`MixGray_BT709`/`BT601`）、H 按 modeH 生效（`ModeAdd` 六边形加法 / `RotateOnGray` 绕灰轴 Rodrigues 旋转，严格正交、往返无累积误差）。各 Mode 计算公式见「步骤 4️⃣ BCSH 调整公式」。
- **步骤 6️⃣**：RGB 输出直接编码；YUV 输出经 `rgb_to_yuv`（内部钳位量化）。

### YCbCr 处理域

处理域为 yuv444p full-range（归一化 $(Y, Cb, Cr)$，$Cb/Cr$ 去中心 0.5：$Y\in[0,1]$、$Cb,Cr\in[-0.5,0.5]$）。YCbCr 域下 B 通道即 Y（亮度）。

#### 1. H/S 极坐标与 S 归一化（步骤 3️⃣）

$$\text{radius} = \sqrt{Cb^2+Cr^2},\qquad \theta = \text{atan2}(Cr, Cb)\ \text{（度，[0,360)）}$$

S 按 `y2yClipType` 的 S 语义归一化（`ScaleChromaPix`/`ScaleChromaSec` 之外为绝对极径）：

- **默认（HardClip/ClipChroma/CompLumaOnly/CompLumaFirst）**：$s = \text{radius}$（绝对极径，不归一化）。
- **ScaleChromaPix**：$s = \dfrac{\text{radius}}{r_{\max}(Y,\theta)}$，其中该 $(Y,\theta)$ 下的 RGB 色域边界极径为
  $$r_{\max}(Y,\theta)=\min\!\Big(\min_{k_i>0}\tfrac{1-Y}{k_i},\ \min_{k_i<0}\tfrac{-Y}{k_i}\Big),\qquad k_i=a_i\cos\theta+b_i\sin\theta$$
  $s\in[0,1]$ 保证落在色域内 ⇒ **Y/S/H 三参数解耦**，任意调整不越界、色相不变（`_gamut_r_max`/`_gamut_s_norm`）。
- **ScaleChromaSec**：$s = \text{radius}/\text{\_CHROMA\_MAX}$，其中 $\text{\_CHROMA\_MAX}=\max_{6\text{ 纯色}}\lVert(Cb,Cr)\rVert$（`_bt_chroma_max`；BT.709=0.5957，在 G/M 方向）。绝对比例，**不保证域内**。

#### 2. BCSH 调整（步骤 4️⃣）

- **H**：直接旋转极角 $\theta_a=(\theta+\delta H)\%360$（`adjust_hsv` 的 dh 即极角加性旋转，不再经 HSV 色相中转）；`hue_sync` 经 LUT（`hue_ycbcr_to_hsv`/`hue_hsv_to_ycbcr`）仅作读数显示（H/H'SY）与指定色相 range。
- **S**：`adjust_hsv` 对 $s$ 做加性/乘性（`ModeAdd` $s'=\mathrm{clip}(s+ds)$ / `ModeMul` $s'=\mathrm{clip}(s\cdot ds)$）。
- **B/C**：Y 通道——Contrast 乘性 + δB（`mode_b`：`ModeAdd` 加性 / `ModeMul` 乘性 / `NegMulPosRat` 负压正白）。
- 各 ModeB/C/S/H 的完整计算公式见「步骤 4️⃣ BCSH 调整公式」。

#### 3. 重建与钳位（步骤 5️⃣）

$$\text{radius}_a = \begin{cases} s_a\cdot r_{\max}(Y_a,\theta_a) & \text{ScaleChromaPix}\\ s_a\cdot\text{\_CHROMA\_MAX} & \text{ScaleChromaSec}\\ s_a & \text{其余}\end{cases},\qquad (Cb_a,Cr_a)=\text{radius}_a(\cos\theta_a,\ \sin\theta_a)$$

随后按 `y2yClipType` 统一策略处理（步骤 5️⃣，`_apply_y2y_strategy`）：

- **ScaleChromaPix**：重建天然在域内 ⇒ 硬钳恒等（调整结果与输入按 w 的凸组合仍落在 RGB 色域内——RGB 色域为凸集）。
- **ScaleChromaSec**：重建可能越界 ⇒ 越界像素按 `HardClip` 兜底。
- **ClipChroma**：保 Y、沿色相把极径缩到 $r_{\max}(Y,\theta)$（`_gamut_clip_chroma`）。
- **CompLumaOnly / CompLumaFirst**：见下方「亮度补偿」。

**亮度补偿（y2yClipType=CompLumaOnly / CompLumaFirst）**：

- `CompLumaOnly`（保 S 调 Y，原 `ModeAddCompY`）：色度不变，按 Y2R 通道钳位量补 $\Delta Y$ = 缺量 − 超量（只补回实际被钳掉的部分，不直接顶到可行区间边界）：
  $$\Delta Y=\max(0,-\min_i RGB_i)-\max(0,\max_i RGB_i-1),\qquad Y'=\mathrm{clip}(Y_a+\Delta Y,0,1)$$
- `CompLumaFirst`（Y 优先、S 兜底，原 `ModeAddCompYS`）：先只调 Y——把 $Y$ 钳到该 $(\theta,r)$ 下的可行区间 $[Y_{lo},Y_{hi}]$（$Y_{lo}=\max_i(-k_i)$，$Y_{hi}=\min_i(1-k_i)$，可行时与 `CompLumaOnly` 一致）；若 $r>r^*=\frac{1}{A+B}$（$A=\max_i(-k_i)$，$B=\max_i k_i$，可行区间为空、Y 单独调不够），再调 S：
  $$(Cb',Cr')\leftarrow(Cb,Cr)\cdot\frac{r^*}{r},\qquad Y'=Y^*=\frac{A}{A+B}$$
  此时 $\max_i RGB_i=1$、$\min_i RGB_i=0$——落在色域边界（$V=1$、$S_{hex}=1$ 全饱和），色相严格保持、无残留越界；取舍：Y 优先、S 只缩到恰好够（最小损失），但 $r>r^*$ 时结果必然全饱和。

> 原 modeB 的 `ModeAddKeepHS`/`ModeAddKeepH`（5b 亮度超界处理）已删除：`ModeAddKeepHS` 可行时与 `CompLumaOnly` 等价、不可行时比 `CompLumaFirst` 粗糙；`ModeAddKeepH` 需双向矩阵 + RGB 往返、双机制，实现最复杂。亮度越界统一由 `y2yClipType` 策略处理。

#### 4. 预览与输出

- **预览帧**：`yuv_5_disp` → YUV→RGB → `y2rClipType` 钳位（Hard/Soft/ConstHue）→ RGB 帧显示（`_yuv_to_preview_frame`）。
- **输出**：YUV 输出直接编码（步骤 5️⃣ 已完成色域处理，`_yuv_norm_to_output_frame`）；RGB 输出经 YUV→RGB 桥 + `y2rClipType` 钳位（`_to_output_frame_yuv`）。

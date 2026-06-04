# PQ 模块通用测试工具 设计文档

## 概述

整合 `csc_ui.py` 和 `dci_ui.py`，生成统一的 PQ（Picture Quality）模块测试工具。支持多模块流水线串联、参数实时调整、图像预览。

## 文件

| 文件 | 用途 |
|------|------|
| `script/test_tool_ui/pq_test_tool.py` | 主入口，窗口、事件循环、流水线编排 |
| `script/test_tool_ui/ui_io.py` | CSC 模块（参考 `script/csc/csc_ui.py` 提取 UI 和事件逻辑） |
| `script/test_tool_ui/ui_csc.py` | CSC 模块（参考 `script/csc/csc_ui.py` 提取 UI 和事件逻辑） |
| `script/test_tool_ui/ui_dci.py` | DCI 模块（参考 `script/dci/dci_ui.py` 提取 UI 和事件逻辑） |
| `script/test_tool_ui/ui_shp.py` | SHP 模块（参考 `script/dci/dci_ui.py` 提取 UI 和事件逻辑） |
| `script/csc/` | CSC 原实现（保留不动） |
| `script/dci/` | DCI/SHP 原实现（保留不动） |

子模块文件从源文件中提取 UI 构建和事件处理逻辑，包含独立的 `build_controls()` / 事件处理函数，由 `pq_test_tool.py` 导入并集成到统一窗口。

## 布局

```

┌─ Pipeline ───────────────────────────────────────────┐
│  [☑ CSC ◀ ▶]   [☐ DCI ◀ ▶]   [☑ SHP ◀ ▶]      │  ← 顶部独立 row
└──────────────────────────────────────────────────────┘
┌─ [I/O] [CSC] [DCI] [SHP] ─────────  ← 同一个 TabGroup │
│                                                       │
│  模块参数区域（按当前选中 Tab 显示）                    │
│    - I/O ：公共文件/分辨率/格式/色彩空间                │
│    - CSC / DCI / SHP：各自专属控件                     │
│                                                       │
└───────────────────────────────────────────────────────┘
┌─ Preview ────────── ← 独立的 layout（方案 A：内嵌Frame） │
│  ┌─ Common Info ────────────────────────────────────┐ │
│  │ Display Size │ Position │ Input Pix │ Output Pix │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌─ Left Preview ──┐  ┌─ Right Preview ──────────┐    │
│  │  (输出/输入切换)  │ │  (辅助：直方图等)        │    │
│  └──────────────────┘ └───────────────────────────┘  │
│                                                       │
│  [Status Bar]                                         │
└───────────────────────────────────────────────────────┘
```

### 关键规则

1. I/O、CSC、DCI、SHP 属于同一个 `sg.TabGroup` layout
2. Preview 是独立的 layout，包含 Common Info 栏 + 左右图像预览区
3. Preview 主窗口内嵌为 `sg.Frame`（方案 A）
4. Pipeline bar 固定在窗口顶部独立的 layout row，始终可见
5. 所有 Tab 始终可见（禁用模块不隐藏）
6. 默认流水线：仅 CSC 启用，顺序 `["csc", "dci", "shp"]`

### 浮动预览窗口（方案 B，暂不实现）

- 内嵌 Preview Frame 旁增加「弹出预览」按钮
- 点击后创建独立 `sg.Window("Preview", layout=preview_layout, finalize=True)`
- 关闭浮动窗口后缩回内嵌 Frame
- PySimpleGUI 不原生支持可拖拽停靠面板，此方案为最佳折中

## 流水线细节

### 流水线执行策略

- **无 Run 按钮**：任何参数变化自动触发流水线
- **首次输入**：选文件 → 读入内存 → 按预览区分辨率缩放 → 处理
- **降低处理分辨率**：预览区大小不超过图像原始分辨率，默认保持在400高度，图像缩放要保持宽高比
- **输入文件切换**：清空所有模块缓存快照，全流水线重跑
- **缓存快照**：每个模块入口存一份上一模块输出的 numpy 数组，还要保留格式和色彩空间信息
- **增量执行**：调整模块 X 参数，从 X 起重新计算（利用上游缓存），并刷新下游

```
输入文件 → [RAW BGRA]
             ↓
        CSC → _SNAPSHOTS["csc"]
             ↓
        DCI → _SNAPSHOTS["dci"]
             ↓
        SHP → _SNAPSHOTS["shp"]
             ↓
        最终输出 → 预览区
```

### 流水线数据模型

```python
REGISTERED_MODULES: dict[str, dict[str, Any]]  # 模块注册表

pipeline_order: list[str]        # 当前顺序，如 ["csc", "dci", "shp"]
pipeline_enabled: set[str]       # 启用的模块 tag
_SNAPSHOTS: dict[str, np.ndarray | None]  # 每个模块的缓存 BGRA
```

- 实际执行流水线：`[m for m in pipeline_order if m in pipeline_enabled]`

### 流水线 UI 行为

| 操作 | 行为 |
|------|------|
| ☑ / ☐ 勾选 | 立即重新计算流水线（若该模块在上游系，刷新下游） |
| ◀ / ▶ 排序 | 修改流水线模块顺序，并触发重新执行，快照和缓存也要重置 |
| ◀ 已达顶部 / ▶ 已达底部 | 按钮不变灰但无效果（可后续优化） |

## 模块细节

### 模块协议

每个模块实现以下接口，在 `_register_modules()` 中显式注册：

| 接口 | 签名 | 说明 |
|------|------|------|
| `tag` | `str` | 模块标识 (csc/dci/shp) |
| `label` | `str` | Tab 显示名 |
| `build_controls()` | `→ list[list[sg.Element]]` | 模块专属参数控件 |
| `process(input_data, input_fmt, input_clrspc, params)` | `→ (bool, np.ndarray, int, int | str)` | 处理，返回 (ok, output_data, output_fmt, output_clrspc 或 error_msg) |
| `read_params(values)` | `→ dict` | 从 values 提取模块参数 |
| `get_right_preview_image(snapshot, params)` | `→ np.ndarray \| None` | 可选，返回右侧辅助预览图像，返回 None 则清空 |

### 快照数据结构

每个模块入口缓存使用三元组：`(data: np.ndarray, fmt: int, clrspc: int)`。不是纯数组，附带格式和色彩空间信息供下游模块校验。

DCI/SHP 的 exe 调用通过临时文件桥接：写临时 raw → 调 exe → 读临时 raw 回内存。

### 模块执行引擎

- CSC：Python in-process（`run_csc.py` 的 `read_raw_to_planar` / 转换逻辑）
- DCI：调用外部 `dci_runner` exe
- SHP：调用外部 `sharpen` exe
- 执行失败时在 Status Bar 显示错误，预览区保留上次成功结果

## 预览区细节

### Common Info（参考 csc_ui.py Preview Info 实现）

位于 Preview 布局顶部，显示 4 个只读字段，鼠标悬浮在预览图像上时实时更新：

| 字段 | Key | 说明 |
|------|-----|------|
| Display Size | `-DISPLAY-SIZE-` | 当前显示分辨率 和 缩放比例 |
| Position | `-POSITION-INFO-` | 鼠标在原图中的像素坐标 `(x, y) [Frozen/Unfrozen]` |
| Input Pixel | `-INPUT-PIXEL-INFO-` | 输入图像该位置的像素值 `rgb: (R, G, B)` 或 `yuv: (Y, U, V)`（根据格式）  |
| Output Pixel | `-OUTPUT-PIXEL-INFO-` | 输出图像该位置的像素值 `rgb: (R, G, B)` 或 `yuv: (Y, U, V)`（根据格式） |

实现方式：

- 图像元素 `.bind('<Motion>', '+MOTION')` 绑定鼠标移动
- 事件循环中匹配 `+MOTION`，通过 `window[key].user_bind_event` 获取 tkinter 坐标
- 根据当前缩放因子将 widget 坐标映射回原图坐标
- 用空格键冻结/解冻像素值显示

### 左侧预览

- 默认显示流水线最终输出图像数据，如果是yuv格式，需要转换为rgb数据再显示
- 底部左侧为"Show Input" checkbox, 默认不勾选，勾选后显示对应分辨率的输入图像
- 底部右侧为“Save Image” button, 点击后保存当前显示图像数据为文件，支持".yuv/.rgb"后缀（保存raw数据）或者".png/.bmp"后缀（保存转换为rgb之后的图像）
- ~~可弹出浮动窗口~~

### 右侧预览

- 默认不显示
- 具体显示内容由各模块通过 `get_right_preview_image(snapshot, params) → np.ndarray | None` 实现
- 返回 `None` 时清空右侧预览

## IO tab 细节

### 布局

- 以 `csc/csc_ui.py` 实现为基准，不需要 `Precision`（移动到CSC tab 内）和`Auto Pixel Depth`
- 增加`dci/dci_ui.py`中的 `Output Dir` 和 `Config File`
- 宽高控件右侧增加 `Frame Num` （默认1，输入分辨率和格式变换后根据帧大小自动测算，取整） 和 `Frame Index` （默认0）
- **Frame Num 校验**：当用户调整格式或分辨率后 `Frame Num < 1` 时，Status Bar 输出警告信息 `"File too small for frame size"`
- `Set Color` 改名为 `Use Specified Color as Input:`，`dump` 按钮移动到此处

### 格式与 Colorspace 联动

- `_update_clrspc_for_fmt(window, values, clrspc_key, fmt_str)`：复用现有实现
- `-IN-FMT-` 变化 → 更新 `-IN-CLR-` 选项
- `-OUT-FMT-` 变化 → 更新 `-OUT-CLR-` 选项
- 输入文件选择 → 按扩展名猜测格式 `.yuv`→NV24, `.rgb`→RGB888
- 分辨率从文件名 `(\d+)x(\d+)` 猜测
- 格式切换时校验色彩空间有效性，无效则回退默认

## CSC tab 细节

### 布局

基于 `csc/csc_ui.py` 的实现调整：

- `Precision` 移动到 `Algo Type`右侧
- 增加一行分隔线，再将 `Sat/Hue Test` 功能用 `sg.Frame("Sat/Hue Test", [...])` 整合到分割线下方，控件顺序按以下展开，每小点一行:
    - `Show Color Map` checkbox，`Color Map Type` combo（由 `Input Colorspace` 改名而来）
    - `Luma/Value` slider + spinbox，`Set Src Color` checkbox + input
    - `Hue` 和 `Saturation` slider + spinbox 则由原 BCSH 中的对应控件复用
- 增加一行分隔线，将原 `CSC Steps` 相关控件整合到分割线下方，改名为 `CSC Coef Info`

## 非功能需求

- 单文件 `pq_test_tool.py` 不超过 2000 行（核心逻辑精简）
- 尽量多参考现有 `csc/run_csc.py` 和 `dci/dci_models.py` 的实现
- 模块扩展只需遵循协议并调用 `_register_modules()` 注册

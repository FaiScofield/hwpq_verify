# ui pipeline

## 总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                          1. 用户操作输入                              │
├─────────────────────────────────────────────────────────────────────┤
│  IoUiController._on_browse_input() / _on_reload_input()             │
│  → 选择文件路径，设置 width/height/fmt/frame_idx                      │
└──────────────────────────┬──────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          2. 读取原始文件                              │
├─────────────────────────────────────────────────────────────────────┤
│  IoUiController._load_input_image()                                 │
│  → read_raw_to_planar(filepath, w, h, fmt, repeat_to_444=True)      │
│      输出: tuple(Y, U, V)  各为 2D uint8/uint16 ndarray              │
│  → _convert_to_yuv444(data, fmt)                                    │
│      • YUV 格式: 色度上采样(422/420→444) + 10bit→8bit 降位            │
│      • RGB 格式: BT.709 matrix → YUV444 uint8                       │
│      输出: np.ndarray (H, W, 3) uint8, channels-last YUV444         │
└──────────────────────────┬──────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          3. 分发输入图像                              │
├─────────────────────────────────────────────────────────────────────┤
│  IoUiController._emit_input_loaded(input_yuv444, status)            │
│  → AcmTestAppWindow._on_input_loaded(yuv444, status)                │
│      ├── preview_ctrl.set_input_image(yuv444)  [左预览]              │
│      └── acm_ctrl.request_auto_run()           [触发 ACM 处理]       │
└──────────────────────────┬──────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   4. ACM 自动运行(Timer 防抖)                         │
├─────────────────────────────────────────────────────────────────────┤
│  AcmUiController._schedule_auto_run() → QTimer → _do_auto_run()     │
│  → input_data = self._input_provider()                              │
│      └── PreviewUiController.input_yuv444  (H,W,3) uint8 YUV444     │
│  → _apply_lut_lengths() + _update_acm_gains()                       │
│  → _apply_full_delta_to_acm()                                       │
│      └── 写入 acm.lut_delta_ybyh/sbyh/hbyh (int16)                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        5. ACM 核心处理                                │
├─────────────────────────────────────────────────────────────────────┤
│  acm = self._get_current_acm()  (AcmImplHwRk / SwRk / SwEvideo)    │
│  → acm.do_acm_yhs(input_data)   或  do_acm_10bit(...)               │
│     输入: (H,W,3) uint8 YUV444 channels-last                        │
│     内部:                                                            │
│       • YUV → YHS 色彩空间转换 (trig / cordic)                       │
│       • 查表: LUT delta + gain 应用到 Y/S/H                          │
│       • YHS → YUV 逆转换                                             │
│     输出: (H,W,3) uint8 YUV444 channels-last                        │
│  → 计时 elapsed_ms                                                   │
└──────────────────────────┬──────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        6. 显示输出图像                                │
├─────────────────────────────────────────────────────────────────────┤
│  AcmUiController._do_auto_run()                                     │
│  → self._output_callback(acm_output)                                │
│      └── preview_ctrl.set_output_image(acm_output)  [右预览]         │
│  → self._preview_time_callback(elapsed_ms)                          │
│      └── preview_ctrl.set_time_cost_ms(elapsed_ms)                  │
│  → self._status_callback(f"Processing completed in {elapsed_ms}ms") │
└─────────────────────────────────────────────────────────────────────┘
```

## 组件联动事件

**总览**

- `do_acm` 的直接入口不是某个控件，而是 `_schedule_auto_run()` 启动定时器，随后 `auto_run_timer.timeout -> _do_auto_run()`。
- 不是所有“看起来可编辑”的控件都会触发 `do_acm`。
- `offset` 相关控件当前只做数值联动，没有接入 `_schedule_auto_run()`。
- `delta` 图表不是 `acm_ui.ui` 原生控件，而是运行时挂到 `widget_delta_*_host` 里的 `SingleCurveChartWidget`。

**交互控件联动表**

| UI控件 | 类型 | 触发信号 | 目标槽/联动 | 主要副作用 | 是否会走到 `do_acm` |
| --- | --- | --- | --- | --- | --- |
| `checkBox_enable_acm` | `QCheckBox` | `toggled` | `_schedule_auto_run()` | 请求自动运行；但若取消勾选，调度会被 `_is_acm_enabled()` 短路 | 条件触发 |
| `radioButton_colorspace_yhs` | `QRadioButton` | `toggled` | `_on_acm_colorspace_changed()` | 切换 colorspace，联动启用/禁用 offset 控件，并请求自动运行 | 是 |
| `radioButton_colorspace_hsv` | `QRadioButton` | `toggled` | `_on_acm_colorspace_changed()` | 同上；但 `_do_auto_run()` 里 HSV 路径当前直接返回“未实现” | 是 |
| `comboBox_algo_type` | `QComboBox` | `currentIndexChanged` | `_on_algo_changed()` | 切换算法实例、同步 LUT 长度、迁移 delta/gain/clip 状态、刷新 UI、请求自动运行 | 是 |
| `comboBox_clip_type` | `QComboBox` | `currentTextChanged` | `_on_clip_type_changed()` | 写回 `acm.clip_type`，请求自动运行 | 是 |
| `comboBox_interp_method` | `QComboBox` | `currentTextChanged` | `_on_interp_method_changed()` | 只更新插值方式，供后续 delta 平滑/重建使用 | 否 |
| `checkBox_lut_visualization` | `QCheckBox` | `toggled` | `_on_lut_visualization_toggled()` | 将 LUT 可视化区拆到 dock 或收回 | 否 |
| `groupBox_lut_lengths` | `QGroupBox(checkable)` | `toggled` | `_on_lut_lengths_group_toggled()` | 按勾选状态决定长度来源，应用长度、刷新 delta 控件、请求自动运行 | 是 |
| `slider_ctrl_points` | `QSlider` | `valueChanged` | `_on_ctrl_points_changed()` | 改控制点数量、重算 sample positions、更新 hint | 否 |
| `slider_len_y` | `QSlider` | `valueChanged` | `spinBox_len_y.setValue()` + `_on_lut_lengths_changed()` | 和 `spinBox_len_y` 双向同步；改 2D LUT 长度并请求自动运行 | 是 |
| `spinBox_len_y` | `QSpinBox` | `valueChanged` | `slider_len_y.setValue()` + `_on_lut_lengths_changed()` | 同上 | 是 |
| `slider_len_s` | `QSlider` | `valueChanged` | `spinBox_len_s.setValue()` + `_on_lut_lengths_changed()` | 同上 | 是 |
| `spinBox_len_s` | `QSpinBox` | `valueChanged` | `slider_len_s.setValue()` + `_on_lut_lengths_changed()` | 同上 | 是 |
| `slider_len_h` | `QSlider` | `valueChanged` | `spinBox_len_h.setValue()` + `_on_len_h_changed()` | 和 `spinBox_len_h` 同步；约束 `len_h2` 最大值、应用长度、重建 delta 控件、请求自动运行 | 是 |
| `spinBox_len_h` | `QSpinBox` | `valueChanged` | `slider_len_h.setValue()` + `_on_len_h_changed()` | 同上 | 是 |
| `slider_len_h2` | `QSlider` | `valueChanged` | `spinBox_len_h2.setValue()` + `_on_lut_lengths_changed()` | 和 `spinBox_len_h2` 同步；改 2D LUT 长度并请求自动运行 | 是 |
| `spinBox_len_h2` | `QSpinBox` | `valueChanged` | `slider_len_h2.setValue()` + `_on_lut_lengths_changed()` | 同上 | 是 |
| `button_reset_lut_length` | `QPushButton` | `clicked` | `_on_reset_lut_length()` | 长度恢复当前算法默认值、刷新 delta/sample overlay、请求自动运行 | 是 |
| `slider_gain_y` | `QSlider` | `valueChanged` | `spinBox_gain_y.setValue()` + `_schedule_auto_run()` | 和 `spinBox_gain_y` 同步，请求自动运行 | 是 |
| `spinBox_gain_y` | `QSpinBox` | `valueChanged` | `slider_gain_y.setValue()` | 通过 slider 的 `valueChanged` 间接请求自动运行 | 是 |
| `slider_gain_s` | `QSlider` | `valueChanged` | `spinBox_gain_s.setValue()` + `_schedule_auto_run()` | 同上 | 是 |
| `spinBox_gain_s` | `QSpinBox` | `valueChanged` | `slider_gain_s.setValue()` | 同上 | 是 |
| `slider_gain_h` | `QSlider` | `valueChanged` | `spinBox_gain_h.setValue()` + `_schedule_auto_run()` | 同上 | 是 |
| `spinBox_gain_h` | `QSpinBox` | `valueChanged` | `slider_gain_h.setValue()` | 同上 | 是 |
| `button_reset_gain` | `QPushButton` | `clicked` | `_on_reset_gain()` | 把 3 个 gain spinbox 设为 `256`；因 spinbox->slider 联动，最终会触发自动运行 | 是 |
| `slider_offset_wr` | `QSlider` | `valueChanged` | `spinBox_offset_wr.setValue()` | 只做数值同步 | 否 |
| `spinBox_offset_wr` | `QSpinBox` | `valueChanged` | `slider_offset_wr.setValue()` | 只做数值同步 | 否 |
| `slider_offset_wg` | `QSlider` | `valueChanged` | `spinBox_offset_wg.setValue()` | 只做数值同步 | 否 |
| `spinBox_offset_wg` | `QSpinBox` | `valueChanged` | `slider_offset_wg.setValue()` | 只做数值同步 | 否 |
| `slider_offset_wb` | `QSlider` | `valueChanged` | `spinBox_offset_wb.setValue()` | 只做数值同步 | 否 |
| `spinBox_offset_wb` | `QSpinBox` | `valueChanged` | `slider_offset_wb.setValue()` | 只做数值同步 | 否 |
| `button_reset_offset` | `QPushButton` | `clicked` | `_on_reset_offset()` | 把 3 个 offset spinbox 设为 `256`；当前不会请求自动运行 | 否 |
| `slider_max_delta_y` | `QSlider` | `valueChanged` | `spinBox_max_delta_y.setValue(v/100.0)` + `_schedule_auto_run()` | 数值换算到 double spinbox，并请求自动运行 | 是 |
| `spinBox_max_delta_y` | `QDoubleSpinBox` | `valueChanged` | `slider_max_delta_y.setValue(int(v*100+0.5))` | 通过 slider 的 `valueChanged` 间接请求自动运行 | 是 |
| `slider_max_delta_s` | `QSlider` | `valueChanged` | `spinBox_max_delta_s.setValue(v/100.0)` + `_schedule_auto_run()` | 同上 | 是 |
| `spinBox_max_delta_s` | `QDoubleSpinBox` | `valueChanged` | `slider_max_delta_s.setValue(int(v*100+0.5))` | 同上 | 是 |
| `slider_max_delta_h` | `QSlider` | `valueChanged` | `spinBox_max_delta_h.setValue()` + `_schedule_auto_run()` | 和 `spinBox_max_delta_h` 同步，并请求自动运行 | 是 |
| `spinBox_max_delta_h` | `QSpinBox` | `valueChanged` | `slider_max_delta_h.setValue()` | 通过 slider 的 `valueChanged` 间接请求自动运行 | 是 |
| `button_reset_max_delta` | `QPushButton` | `clicked` | `_on_reset_max_delta()` | 把 max delta 恢复到 `0.25/0.25/64`，请求自动运行 | 是 |
| `pushButton_read_config` | `QPushButton` | `clicked` | `_on_read_config()` | 打开文件对话框，读 JSON；成功后 `load_current_config()` 刷新 UI 并请求自动运行 | 是 |
| `pushButton_save_config` | `QPushButton` | `clicked` | `_on_save_config()` | 打开保存对话框并 `dump_json` | 否 |
| `button_reset_curr` | `QPushButton` | `clicked` | `_on_reset_curr()` | 当前 delta tab 清零，写回 ACM，更新 heatmap，请求自动运行 | 是 |
| `button_smooth_curr` | `QPushButton` | `clicked` | `_on_smooth_curr()` | 按插值/平滑策略处理当前 delta tab，写回 ACM，更新 heatmap，请求自动运行 | 是 |
| `button_reset_all` | `QPushButton` | `clicked` | `_on_reset_all()` | 三条 delta 曲线全清零，并逐条请求自动运行 | 是 |
| `button_smooth_all` | `QPushButton` | `clicked` | `_on_smooth_all()` | 三条 delta 曲线全平滑，并逐条请求自动运行 | 是 |

**Delta 图表宿主与运行时联动**

| UI控件 | 类型 | 运行时挂载 | 触发信号 | 目标槽/联动 | 是否会走到 `do_acm` |
| --- | --- | --- | --- | --- | --- |
| `widget_delta_y_host` | `QWidget` | `delta_chart_y` | `samplePointChanged` | `_on_sample_point_changed("y", ...)` | 是 |
| `widget_delta_s_host` | `QWidget` | `delta_chart_s` | `samplePointChanged` | `_on_sample_point_changed("s", ...)` | 是 |
| `widget_delta_h_host` | `QWidget` | `delta_chart_h` | `samplePointChanged` | `_on_sample_point_changed("h", ...)` | 是 |
| `widget_delta_y_host` | `QWidget` | `delta_chart_y` | `dataChanged` | `_on_delta_chart_changed("y", ...)` | 否，当前实现是 no-op |
| `widget_delta_s_host` | `QWidget` | `delta_chart_s` | `dataChanged` | `_on_delta_chart_changed("s", ...)` | 否 |
| `widget_delta_h_host` | `QWidget` | `delta_chart_h` | `dataChanged` | `_on_delta_chart_changed("h", ...)` | 否 |

**Heatmap 宿主控件**

| UI控件 | 类型 | 运行时挂载 | 事件联动 |
| --- | --- | --- | --- |
| `widget_gain_ybyy_host` | `QWidget` | `HeatmapWidget` | 仅被 `_update_heatmaps()` 刷新，无反向 UI 事件 |
| `widget_gain_sbyy_host` | `QWidget` | `HeatmapWidget` | 同上 |
| `widget_gain_hbyy_host` | `QWidget` | `HeatmapWidget` | 同上 |
| `widget_gain_ybys_host` | `QWidget` | `HeatmapWidget` | 同上 |
| `widget_gain_sbys_host` | `QWidget` | `HeatmapWidget` | 同上 |
| `widget_gain_hbys_host` | `QWidget` | `HeatmapWidget` | 同上 |

**无直接联动的被动控件**

| 控件组 | 包含项 | 当前代码中的直接事件 |
| --- | --- | --- |
| 分隔线 | `line`, `line_2`, `line_3` | 无 |
| 文本标签 | `label_*` 全部 | 无 |
| 容器 GroupBox | `groupBox_delta_editor`, `groupBox_global_gain`, `groupBox_lut_visualization`, `groupBox_gain_*` | 无直接 signal；仅 `groupBox_lut_lengths` 有 `toggled` |
| Tab 容器 | `tabWidget_delta`, `tab_delta_y`, `tab_delta_s`, `tab_delta_h` | 当前未显式连接 `currentChanged` 等信号 |
| 顶层容器 | `AcmUiWidget` | 无 |
| LUT 可视化内容容器 | `groupBox_gain_ybyy` 等 | 仅承载 heatmap，无 direct event |

**自动运行链路表**

| 来源 | 最终是否会进 `_schedule_auto_run()` | 备注 |
| --- | --- | --- |
| 算法切换、长度变更、delta 编辑、delta reset/smooth、gain 变更、max delta 变更、读配置、colorspace 切换 | 会 | 这些是当前主要的 `do_acm` 入口 |
| `checkBox_enable_acm` | 条件 | 勾上时会调度；取消勾选时 `_schedule_auto_run()` 会被 `_is_acm_enabled()` 提前返回 |
| `offset` 相关控件 | 不会 | 当前只同步数值，不触发自动运行 |
| `checkBox_lut_visualization`、保存配置、插值方式切换、控制点数量切换 | 不会 | 只改 UI / 内部状态，不直接跑 ACM |

**我认为最值得你审核的几个点**

- `offset` 三组控件当前没有接入 `_schedule_auto_run()`，这意味着改 offset 不会触发 `do_acm`。
- `comboBox_interp_method` 只改 `self.interp_method`，不会立即刷新现有 delta 曲线。
- `slider_ctrl_points` 只改 sample 点分布，不会立即跑 `do_acm`。
- `groupBox_lut_lengths` 现在有 `toggled -> _on_lut_lengths_group_toggled()`，这是我这次新增的联动。

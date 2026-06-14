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
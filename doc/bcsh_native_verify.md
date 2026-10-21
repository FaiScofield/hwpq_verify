# BCSH Python/C++ 自动比对工具

用于验证 `script/bcsh/hsv_adjust.py`（Python 参考实现）与 RkYuvAlgos 中
`rk_swpq_exe` 的 BCSH 模块（`rkalgo_swpq_bcsh.cpp` / `rkpq_main.cpp`）输出是否一致。

- 核心实现：`script/bcsh/native_compare.py`
- 命令行入口：`script/bcsh/verify_bcsh_native.py`

## 前置条件

1. 编译带 BCSH 的 `rk_swpq_exe`（Release 示例）：

   ```bat
   cd /d <RkYuvAlgos_git>\project\vc\build_ninja_Release
   cmake --build . --target rk_swpq_exe -j 1
   ```

   > 本机 8 并发编译曾触发 `C1060: 编译器的堆空间不足`，内存紧张时请降低 `-j`。

2. 常见产物路径：

   ```
   <RkYuvAlgos_git>/project/vc/build_ninja_Release/rkswpq/rk_swpq_exe.exe
   <RkYuvAlgos_git>/project/vc/build_msvc/rkswpq/Debug/rk_swpq_exe.exe
   ```

   工具会自动查找；也可用 `--exe`、环境变量 `RKPQ_EXE` 或 `RKYUVALGOS_ROOT` 指定。

   > **多个构建产物并存时，工具取修改时间最新的一个。** 旧 exe 与新构建写入的
   > OpenCL kernel 缓存（`D:/RkDefaultDumpData/pq_bcsh_*.bin`）可能不兼容，
   > GPU 通路会**静默输出全黑**。遇到这种情况请改用最新构建的 exe，或删除该
   > 缓存文件（下次运行会重新编译 kernel），或用 `--proc-mode cpu` 走纯 CPU 通路。

   MSVC 多配置构建的 `pthreadVC2.dll` 位于 `<build>/rkswpq/Release/`，工具会自动
   把 exe 同级、上级及其 `Release` 子目录加入子进程 `PATH`。

## 用法

```bat
:: 快速冒烟（约 30 条用例）
python script\bcsh\verify_bcsh_native.py --quick

:: 默认用例集（约 77 条，含 RGB/HSV、各色空间、随机组合）
python script\bcsh\verify_bcsh_native.py

:: 更密集的随机组合
python script\bcsh\verify_bcsh_native.py --full

:: 指定 exe / 只验证 RGB 模型 / 使用真实图片
python script\bcsh\verify_bcsh_native.py --exe <path> --model rgb --image data/photo.png

:: 只列出用例
python script\bcsh\verify_bcsh_native.py --list-cases

:: 输出调试日志（exe 路径/时间、JSON 参数、临时目录、输出统计）
python script\bcsh\verify_bcsh_native.py --quick -v
```

退出码：`0` 全部通过，`1` 存在超差/失败用例，`2` 参数或环境错误。

输出目录默认为 `output/bcsh_native/`：

- `report.csv`：每条用例的参数、max/mean/P99 误差、>1 LSB/>2 LSB 像素数、是否通过。
- 失败用例（默认）或 `--save-all` 时：`input.png`、`ref.png`、`native.png`、`diff_x8.png`。

## 参数映射

工具内部把 C++ 原始参数映射为 `hsv_adjust.py` 的调用：

| Python | C++ `rkpq_bcsh_cfg` |
|---|---|
| `adjust_rgb(delta_b=(B-256)/256, gain_c=C/256, delta_s=S/256, mode_c='zero', mode_b='add', angle_deg=(H-256)*180/256, h_mode='rotategray', gray_coef=...)` | `eColorModel=0`，`nBrightness=B`，`nContrast=C`，`nSaturation=S`，`nHue=H` |
| `adjust_hsv(delta_b=(B-256)/256, delta_s=S/256, mode_b='add', mode_s='mul', delta_h=((H-256)*180/256)/360)` | `eColorModel=1`，`fHueGoal` 在 `[0,360]` 之外（SameOffset） |
| `adjust_hsv(..., delta_h=0)` 后按 `h += (H/511)·shortest_arc(goal-h)` 旋转 | `eColorModel=1`，`fHueGoal=goal`，`nHue=H`（SameTarget） |

`eColorSpace` 与灰度系数的对应关系（与 `bcshClrSpc2GrayCoef()` 一致）：

| eColorSpace | 灰度系数 |
|---|---|
| 0/1 (BT.601) | `bt601` |
| 2/3/6/7 (BT.709 / RGB) | `bt709` |
| 4/5 (BT.2020) | `bt2020` |
| 8 (DCI P3) / 9 (Display P3) | `dci_p3` / `display_p3` |

UI 上可对应选择 `GainAtZero`、`RotateOnGray`、`MixGray_BT709`/`MixGray_BT601`、
`ModeAdd` 这几条 C++ 已实现的路径；`FastStone`/`TanSlant`/`Rate2Limit`/`mid`
等模式 C++ 没有对应实现，不在比对范围内。

## 判定阈值

| 模型 | 默认阈值（最大绝对误差） |
|---|---|
| RGB | 2 LSB |
| HSV | 3 LSB |

实测 RGB 模型通常为 0~1 LSB，HSV 模型为 0~2 LSB（定点 Q11/Q14 与浮点的差异）。
可用 `--threshold-rgb` / `--threshold-hsv` 调整。

## 已规避的 C++ 侧限制

- **使用 RGBA8888（`-sf=1000 -df=1000`）**：本机 OpenCL 驱动不支持 `CL_RGB`，
  RGB888（`-sf=1002`）会报 `CL_INVALID_IMAGE_FORMAT_DESCRIPTOR`。RGBA 还顺带验证 alpha 不被修改。
- **分辨率 >= 128x128**：`rkpq_proc` 的最小尺寸限制；工具默认测试图为 256x256，
  更小的帧由 `NativeBcshRunner` 按边缘复制补齐后处理并裁回（BCSH 为逐像素运算，补齐不影响结果）。
- **纯 CPU 模式**：当前 OpenCL 构建中 `eProcMode=2` 的输出可能被内部 OCL buffer
  回读覆盖为 0（`eProcMode=3` 时只有 GPU 处理的半屏有效）。默认使用 `--proc-mode gpu`；
  若要验证 CPU 实现，请使用 `-DENABLE_RKOCL_SUPPORT=OFF` 的纯 CPU 构建。
- **`bEnableBCSH=0` 直通**：同样受上述 OCL buffer 回读影响，默认用例未包含该场景。
- **SameTarget 对跖色相**：`0 < progress < 1` 时，目标色相 180° 附近的最短弧方向
  对 H 的微小差异敏感（定点/浮点会翻转），这是算法本身的病态点。工具会用
  `masked_px` 标记并排除该 ±1° 色相带，其余像素正常统计。

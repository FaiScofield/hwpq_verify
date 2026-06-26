# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

RK HWPQ (Hardware Picture Quality) IP 验证工程，用于对 VOP (Video Output Processor) 和 VDPP (Video Display Post-Processor) 等相关 IP 模块 — ACM, DCI, CSC, Sharp, CFA, CGC — 进行 FPGA 仿真验证、kernel 驱动验证和 CModel 软件验证。

支持 RK3576、RK3572、RK3538 等平台。

## 开发环境约束

- 操作系统: Windows，默认终端为 `cmd`
- C/C++ 编译请使用 `project/build_win32_mingw.cmd` 脚本
- C/C++ 代码格式化遵循仓库根目录的 `_clang-format`（Microsoft 风格变体）
- C/C++ 代码使用英文注释，python代码用中文注释
- 只修改必要的代码，尽量减少无关代码的变动
- 不要删除已存在的注释，除非代码功能和注释不符
- 不要在文档末尾增加空白行
- 不要编辑 `script/verify_tool_app/ui_gen/` 下的文件，这些文件是自动生成的。如果需要修改 UI 相关设置，应修改 `script/verify_tool_app/ui_impl/` 下的文件

## 构建与运行

### Python 环境

```bash
pip install -r requirements.txt
```

### C/C++ 编译 (CMake, C++11)

Windows (MinGW，推荐):
```bash
project/build_win32_mingw.cmd
```

Windows (MSVC):
```bash
project/build_win32_msvc.cmd
```

Linux/WSL:
```bash
# Debug build，目标平台 RK3572（默认）
bash project/build_linux_host.sh Debug RK3572
# Release build
bash project/build_linux_host.sh Release RK3576
```

编译产物输出到 `output/`。`compile_commands.json` 会自动生成在仓库根目录，供 clangd/IDE 使用。编译时会链接 `prebuilt/` 目录下的预编译静态库。

### 运行 Python 工具

CLI 交互式工具（主入口）:
```bash
python script/cli_helper_main.py [RK3572|RK3576|RK3538]
```

PQ 统一 GUI 验证工具:
```bash
python script/verify_tool_app/pq_verify_tool.py
```

ACM 专用测试应用 (PySide6):
```bash
python script/verify_tool_app/test_app_acm.py
```

## 架构设计

### 模块分层模式

每个 IP 模块遵循相同的分层架构，理解其中一个模块（如 ACM）即可掌握所有模块的结构：

| 分层 | 位置 | 用途 |
|-------|----------|---------|
| Config 参数定义 | `script/config_def/module_config_*.py` | JSON 配置文件的 schema，支持 load/save/gen/dump |
| Register 寄存器定义 | `script/reg_def/module_reg_*.py` | 硬件寄存器布局，config↔register 互转 |
| CLI 交互 | `script/cli_helper/cli_helper_*.py` | 模块的 CLI 子命令交互 |
| 算法实现 (Python) | `script/<module>/` | IP 算法的纯 Python 仿真，也用于测试开发一些新功能 |
| C 验证 | `src/<module>/` | 链接预编译库的 C/C++ 验证 Demo |

### 核心抽象（参见 [script/cli_helper/cli_helper_core.py](script/cli_helper/cli_helper_core.py)）

- **`ModuleHelperCore`** (ABC): CLI 框架基类。各模块继承此类，实现 `update_attributes()` 以绑定 `ModuleConfigCore` + `ModuleRegisterCore`，并注册命令处理函数。主程序 ([cli_helper_main.py](script/cli_helper_main.py)) 通过 `submodules` 字典在不同模块间切换。
- **`ModuleConfigCore`** (ABC): 配置参数管理 — JSON 文件加载/保存、随机生成、格式化打印。各模块以 class 属性的形式定义自己的配置 schema。
- **`ModuleRegisterCore`** (ABC): 硬件寄存器管理 — `.bin`（原始二进制）和 `.dat`（可读文本）寄存器文件的读写，config-to-register (`c2r`) 和 register-to-config (`r2c`) 转换。使用 `Reg(offset, value, name)` 描述单个寄存器字段。

### 各模块实现要点

- **ACM** ([script/acm/](script/acm/)): 自适应色彩管理。YUV→YHS 色彩空间转换（三角函数 或 CORDIC），LUT 管理，delta-Y/delta-S/delta-H 处理，多种 clip 模式（luma_clip, triangle_bt709）。主要 SW 实现类为 `AcmImplSwRk`。

- **CSC** ([script/csc/](script/csc/)): 色彩空间转换。基于矩阵的 RGB↔YUV 变换（BT.601/709/2020），系数调优，基于 HSV 的色彩调整。变换矩阵来自 `get_csc_coefs.py`。

- **DCI** ([script/dci/](script/dci/)): 动态对比度增强。直方图分析，全局 tone-curve LUT 生成，audit/override 机制。Python 层通过 subprocess 调用 native C 可执行文件 (`dci_verify_runner`)，参见 [dci_runner.py](script/dci/dci_runner.py)。

- **Sharp** ([script/sharp/](script/sharp/)): 锐化和色度增强。

### GUI 验证工具

GUI 层统一工具使用 **PySimpleGUI**，ACM 测试应用使用 **PySide6 (Qt)**：

- [pq_verify_tool.py](script/verify_tool_app/pq_verify_tool.py): 多 Tab 流水线工具 (I/O → CSC → DCI → SHP)。模块通过 Tab 模式注册：每个 `ui_*.py` 导出 `TAB_LABEL`、`build_controls()`、`process()` 和事件处理函数。
- [test_app_acm.py](script/verify_tool_app/test_app_acm.py): 独立的 ACM 可视化工具，支持实时 HSV 图表、LUT 曲线图、像素级 H-marker 同步。
- [ui_gen/](script/verify_tool_app/ui_gen/): 从 `.ui` 文件自动生成的 PySide6 UI 类（已在 `.gitignore` 中忽略，不要手动修改）。
- [ui_impl/](script/verify_tool_app/ui_impl/): 手写的 UI 控制器和 widget 实现（当需要修改 UI 行为时，应修改这里的文件）。

### C/C++ 验证代码 ([src/](src/))

`src/` 下每个模块有一个 `*_verify_demo` 可执行程序，链接预编译的 IP 仿真库。`src/utils/` 中的共享工具包括 cJSON、图像 I/O (`verify_img_io`)、CRC32、命令行解析和格式转换。`src/kernel/` 包含 Linux kernel 驱动代码。

编译基于 CMake，支持 ABI 自动检测（x86_64, aarch64, armhf）。通过 `-DRK_SOC=RK3576` 选择目标 SOC 平台。

### 图像格式体系

定义于 [script/img_io.py](script/img_io.py) 和 [script/utils.py](script/utils.py)。图像格式以整数编码标识（`0x0`=RGB888, `0x9`=NV12, `0x13`=YUV444P_10LSB 等），附带元数据：planar/packed、像素深度（字节）、色度子采样。`ImageFrame` 类（y/u/v 平面 + 格式 + 色彩空间）是流水线中标准的数据载体。

## 文件目录说明

- `data/` 和 `output/` 为运行时/测试数据目录 — 不要提交其中生成的文件
- `doc/` 包含验证说明和模块理论文档（中文）
- `rxbb/` 包含寄存器描述文件（`.rxbb` 格式），供寄存器生成工具使用
- `web/color-space-lab/` 是独立的 Vite+Three.js 项目，用于 3D 色彩空间可视化；`dist/` 已预编译
- `graphify-out/` 包含代码知识图谱 — 可用 `graphify query`/`graphify path`/`graphify explain` 进行代码导航

## Git 工作流

- 从 `master` 分支，在 feature 分支上开发（当前分支: `dev`），完成后合回
- Commit 信息规范:
  - 只根据暂存区 (staged) 的更改生成提交信息，不应包含未暂存的文件
  - 类型仅允许使用 `fix`, `feat`, `refactor`, `style`, `test`, `docs`, `perf`, `chore`
  - 影响范围跟在类型后面，用中括号 `[]` 包含，例如: `feat[acm_ui]`, `fix[csc]`
  - 首行为总结性语句，后续隔行开始用 `-` 起始描述具体更改内容，每条一句话
- 禁止提交以下内容: `script/verify_tool_app/ui_gen/`、`build/`、`dist/`、`output/` 下的文件，以及 `*.json` 测试数据文件

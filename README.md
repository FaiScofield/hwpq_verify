# HWPQ 验证工程

本工程用于对 HWPQ 相关 IP 设计进行模块化验证，支持内容有：

1. FPGA 验证
   - VOP: ACM, DCI, CSC, Sharp
   - VDPP: DciHist, Sharp, ZME(TODO)
2. Kernel 驱动验证
3. CModel 软件验证
4. 其他辅助功能

## 目录结构

```shell
├── data        # 测试数据
├── doc         # 相关文档
├── prebuilt    # 预编译的cmodel静态库文件，用于生成cmodel软件程序
├── project     # 编译脚本以及编译生成的临时文件
│   ├── build_linux_host.sh     # Linux主机编译脚本
│   ├── build_win32_mingw.cmd   # Windows主机+MinGW工具编译脚本
│   └── build_win32_msvc.cmd    # Windows主机+MSVC工具编译脚本
├── rxbb        # 寄存器描述文件
├── script      # 脚本，主要包含了CLI工具实现和一些批量仿真的脚本
├── src
│   ├── acm     # TODO
│   ├── cfa     # TODO
│   ├── csc     # CSC模块内核验证程序
│   ├── dci     # TODO
│   ├── include # 寄存器定义相关C头文件
│   ├── kernel  # 内核部分驱动代码
│   ├── sharp   # TODO
│   └── utils   # 仿真工具和一些通用代码
├── CMakeLists.txt
├── README.md
└── requirements.txt
```

## 环境准备

### Python 脚本执行环境

工程内的[requirements.txt](requirements.txt)文件中列出了工程所需的 Python 库，可使用 pip 工具安装：

```shell
pip install -r requirements.txt
```

### C++11 编译环境

TODO

## 使用方法

### 脚本的使用

本工程基于Python实现了CLI(Command Line Interface)工具，即[cli_helper_main.py](script/cli_helper_main.py)，为硬件IP的调试提供便利的即时转换工具。支持：
    - 加载、保存软件仿真所需的配置文件，格式为`.json`.
    - 加载、保存fpga仿真所需的硬件寄存器数据，格式为`.bin`(二进制原始数据文件)/`.dat`(寄存器数据可视化文本)。
    - 在配置文件和寄存器数据之间进行相互转换。
    - 随机生成批量的配置，支持保存为多种格式。
    - 获取/修改配置参数，并立即给出对应的寄存器数值变换情况。
    - 支持RK3576/RK3572/RK3538.

```shell
# 执行CLI工具脚本
python script/cli_helper_main.py

# 输出提示信息如下：
=== 欢迎使用 fpga_verify_helep_cli 工具 ===

[MAIN] 可用命令如下:
        help                             - 显示本条帮助信息
        quit                             - 退出程序
        plat    <name>                   - 设置SOC平台，支持: RK3576, RK3572, RK3538 等等
        sharp                            - 进入子模块 SHARP
        acm                              - 进入子模块 ACM
        dci                              - 进入子模块 DCI
        csc                              - 进入子模块 CSC
        cfa                              - 进入子模块 CFA
[MAIN_RK3572] >> #(等待输入命令)
[MAIN_RK3572] >> csc  # 进入CSC子模块，输出提示信息如下：

=== 进入 CSC 模块 ===

[CSC] 可用命令如下:
        help                             - 显示命令帮助信息
        quit                             - 退出或返回上一级
        plat    <-p name> [-x index]     - 设置平台(RK3572/RK3538)和硬件通路的位置(整数)
        load    <file>                   - 加载 .json 配置文件或 .dat(txt)/.bin 寄存器文件
        gen     [-n num] [-o file/dir] [-s rand_seed]
                                         - 生成 num 个随机配置, 可输出到文件(num=1)或文件夹(num>1)
        dump    [-o files] / [-n align] [-l pretty_lines_stdout] [-a pretty_array_stdout]
                                         - 指定文件名(.json/.dat(txt)/.bin, 可多个)时则导出当前配置到对应文件, 否则打印到控制台(此时支持-n/l/a参数)
        c2r     [-i files/dir] [-o files/dir] [-s suffix] [-c cat_regs] / [-n align] [-l pretty_lines_stdout]
                                         - config2register, 读入配置文件(-i)转到寄存器文件(-o), 或者打印到控制台(此时支持-n/l参数)
        r2c     [-i files/dir] [-o files/dir] / [-a pretty_array_stdout]
                                         - register2config, 读入寄存器文件(-i)转到配置文件(-o), 或者打印到控制台(此时支持-n/l参数)
        get     <name1> [name2 name3 ...]
                                         - 获取配置参数的值
        set     <name1=value1> [name2=value2 name3=value3 ...]
                                         - 设置配置参数的值
[CSC_RK3572] >> #(等待输入命令)
```

1. 随时输入`help`命令，可以查看当前模块的可用命令提示。
2. 在子模块内部可以输出其他子模块的名字，直接切换到对应的子模块内

## 验证方案说明

[HWPQ验证说明.md](doc/HWPQ验证说明.md)
[FPGA验证说明.md](doc/FPGA验证说明.md)

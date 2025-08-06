"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-08-06
"""

import sys
import os
import re
import numpy as np
import argparse
import copy
from ast import literal_eval
from tqdm import tqdm
from abc import ABC, abstractmethod
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
# 配置参数基类，新增模块需要在`config_def`中增加对应的参数定义文件
from config_def.module_config_core import ModuleConfigCore
# 寄存器基类，新增模块需要在`reg_def`中增加对应的寄存器定义文件
from reg_def.module_reg_core import ModuleRegisterCore
from utils import run_cmd


class ModuleHelperCore(ABC):
    """Command-Line Interface Helper base framework CLI基类框架。
    * 有新的模块请继承此类，并在`cli_helper_main.py`文件中加入该新模块。
    * 成员函数说明：
    *   `do_xxx`形式的函数返回值表示执行后是否退出脚本，固除了`do_quit`函数返回True, 其他函数均返回False.
    * 成员变量说明：
    *   `self.parent`: 模块名称，用于提示和命令提示。
    *   `self.config`: 基于`ModuleConfigCore`类的配置参数类，实现了对`.json`格式配置（含软软件/硬件参数）的加载、保存、生成、打印等功能。
    *   `self.register`: 基于`ModuleRegisterCore`类的寄存器参数类，实现了对`.bin/.dat(txt)`格式寄存器配置的加载、保存、生成、打印等功能。
    """

    def __init__(self, name: str, platform: str = "RK3572", parent: Optional["ModuleHelperCore"] = None):
        self.name = name.upper()
        self.platform = platform.upper()
        self.parent = parent  # 无上级窗口则为空
        self.config, self.register = self.update_attributes(self.platform)  # 子类需要复写`define_config_and_regs`的实现
        self.submodules = {}  # 空的子模块，仅供顶层Main模块使用

        ## 常驻命令注册表: name, (handler, param_desc, description)
        self.commands = {
            "help": (self.do_help, "", "显示命令帮助信息"),
            "quit": (self.do_quit, "", "退出或返回上一级"),
            "plat": (self.do_plat, "<-p name> [-x index]", "设置平台: (Only RK3572 for now!) 和硬件通路的位置"),
            "load": (self.do_load, "<file>", "加载 .json 配置文件或 .dat(txt)/.bin 寄存器文件"),
            "gen": (
                self.do_gen,
                "[-n num] [-o file/dir] [-s rand_seed]",
                "生成 num 个随机配置, 可输出到文件(num=1)或文件夹(num>1)",
            ),
            "dump": (
                self.do_dump,
                "[-o files] / [-n align] [-l pretty_lines_stdout] [-a pretty_array_stdout]",
                "指定文件名(.json/.dat(txt)/.bin, 可多个)时则导出当前配置到对应文件, 否则打印到控制台(此时支持-n/l/a参数)",
            ),
            "c2r": (
                self.do_c2r,
                "[-i files/dir] [-o files/dir] [-s suffix] [-c cat_regs] / [-n align] [-l pretty_lines_stdout]",
                "config2register, 读入配置文件(-i)转到寄存器文件(-o), 或者打印到控制台(此时支持-n/l参数)",
            ),
            "r2c": (
                self.do_r2c,
                "[-i files/dir] [-o files/dir] / [-a pretty_array_stdout]",
                "register2config, 读入寄存器文件(-i)转到配置文件(-o), 或者打印到控制台(此时支持-n/l参数)",
            ),
            "get": (self.do_get, "<name1> [name2 name3 ...]", "获取配置参数的值"),
            "set": (self.do_set, "<name1=value1> [name2=value2 name3=value3 ...]", "设置配置参数的值"),
        }

    def run(self) -> str:
        """运行模块的主循环"""
        print(f"\n=== 进入 {self.name.upper()} 模块 ===")
        self.do_help([])  # 显示初始帮助信息

        while True:
            try:
                ## 等待用户输入命令
                user_input = input(f"[{self.name}_{self.platform}] >> ").strip()
                if not user_input:
                    continue

                ## 解析命令和参数
                parts = user_input.split()
                command = parts[0].lower()  # 第一个参数总是被解析为常驻命令
                args = parts[1:] if len(parts) > 1 else []  # 剩下的参数被解析为该常驻命令的子参数

                # 处理命令
                if command in self.commands:
                    cmd_handler = self.commands[command][0]
                    should_exit = cmd_handler(args)
                    if should_exit:
                        return ""  # 返回上一级
                elif command == self.name.lower():
                    print(f"[{self.name}] 正处于当前模块中，无需切换")
                    continue
                elif self.parent is not None and command in self.parent.submodules:
                    return command  # 返回上一级并由上一级切换到另一个模块
                else:
                    print(f"[{self.name}] 无效命令: {command}。输入 'help' 查看帮助")
            except KeyboardInterrupt:
                print(f"[{self.name}] \n操作已取消")
            except Exception as e:
                print(f"[{self.name}] 错误: {str(e)}")

    ## =============== 虚函数，需要派生的子类实现 ===============
    @abstractmethod
    def update_attributes(self, platform: str) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        """定义模块的配置参数(由子类实现)"""
        self.platform = platform.upper()
        self.config: Optional[ModuleConfigCore] = None
        self.register: Optional[ModuleRegisterCore] = None
        return self.config, self.register

    ## =============== 通用命令处理函数，子模块可按需复写 ===============
    def config_to_regs(self) -> bool:
        if self.register is not None:
            self.register.config = self.config
            ok = self.register.config2regs()
            return ok
        else:
            print(f"[{self.name}] self.register not defined!!!")
        return False

    def regs_to_config(self) -> bool:
        if self.register is not None:
            ok = self.register.regs2config()
            self.config = self.register.config
            return ok
        else:
            print(f"[{self.name}] self.register not defined!!!")
        return False

    ## =============== 常驻命令处理函数，子模块一般不用复写 ===============
    def do_help(self, args) -> bool:
        print(f"\n[{self.name}] 可用命令如下:")

        for cmd, (_, param_desc, description) in self.commands.items():
            cmd_args = f"{cmd.ljust(8)}{param_desc.ljust(24)}"
            second_prefix = " "
            if len(cmd_args) > 32:
                print(f"\t{cmd_args}")
                print(f"\t{second_prefix.ljust(32)} - {description}")
            else:
                print(f"\t{cmd_args.ljust(32)} - {description}")

        if not self.platform:
            print(f"[{self.name}] Platform not set!")

        return False  # 总是返回False表示不退出

    def do_dump(self, args) -> bool:
        """导出配置到文件或控制台"""
        ## parse args & check
        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument(
            "-a", "--pretty_array_stdout", default=64, type=int, help="控制台美观输出：限制数组类型参数的输出元素量"
        )
        parser.add_argument(
            "-l", "--pretty_lines_stdout", default=16, type=int, help="控制台美观输出：限制寄存器输出最大行数"
        )
        parser.add_argument(
            "-n", "--align", default=4, type=int, help="控制台与文件美观输出：设置寄存器输出每行的对齐数"
        )
        parser.add_argument("-o", "--output", default="", type=str, nargs='+', help="导出的目标文件，可指定多个")
        args, _ = parser.parse_known_args(args)

        reg_ok = self.config_to_regs()

        if args.output == "":
            ## 控制台显示
            self.config.dump(pretty_array_stdout=args.pretty_array_stdout)
            if reg_ok:
                self.register.dump(align=args.align, pretty_lines_stdout=args.pretty_lines_stdout)
        else:
            ## 导出到文件
            for target in args.output:
                try:
                    if target.endswith(".json"):
                        self.config.dump(target)
                    elif reg_ok and (target.endswith(".dat") or target.endswith(".txt")):
                        self.register.dump(target, align=4)
                    elif reg_ok and target.endswith(".bin"):
                        self.register.dump(target)
                    else:
                        print(f"[{self.name}] 错误: 不支持的输出文件类型: {target}, 仅支持.json/.dat(txt)/.bin")
                        break
                    print(f"[{self.name}] 配置已导出到: {os.path.abspath(target)}")
                except Exception as e:
                    print(f"[{self.name}] 导出配置信息至文件 {os.path.abspath(target)} 失败: {str(e)}")

        return False  # 总是返回False表示不退出

    def do_gen(self, args) -> bool:
        ## parse args & check
        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument("-n", "--num", default=1, type=int, help="生成随机配置的数量")
        parser.add_argument("-s", "--rand_seed", type=int, help="起始随机种子(n>1时随机种子自增1)")
        parser.add_argument("-o", "--output", default="", type=str, help="生成的配置文件或目录(n>1时指定目录)")
        args, _ = parser.parse_known_args(args)

        args.num = max(1, args.num)
        abs_path = os.path.abspath(args.output)
        if args.output == "":
            args.num = 1
            abs_path = dirname = ""
        elif os.path.isdir(abs_path):
            dirname = abs_path
        else:
            dirname = os.path.dirname(abs_path)
        if dirname != "" and not os.path.exists(dirname):
            os.makedirs(dirname, parents=True, exist_ok=True)

        if args.num == 1:
            seed_ret = self.config.gen(args.rand_seed)
            if abs_path != "" and not os.path.isfile(abs_path):
                abs_path = os.path.join(dirname, f"{self.name.lower()}_config_seed_{seed_ret}.json")
                print(f"[{self.name}] num = 1, 指定输出应该为绝对路径的文件名，强制修改为: {abs_path}")
            ok = self.config.dump(abs_path)
            if ok and abs_path != "":
                print(f"[{self.name}] 随机配置已生成并导出到: {abs_path}")
        else:
            if not os.path.isdir(abs_path):
                print(f"[{self.name}] num > 1, 指定输出应该为绝对路径的目录名，强制修改为: {dirname}")
            seed = self.config.get_seed() if args.rand_seed is None else args.rand_seed
            for i in tqdm(range(args.num), desc="生成随机配置"):
                seed_ret = self.config.gen(seed + i)
                abs_path = os.path.join(dirname, f"{self.name.lower()}_config_seed_{seed_ret}.json")
                self.config.dump(abs_path)

        return False  # 不退出

    def do_load(self, args) -> bool:
        if not args:
            print(f"[{self.name}] 错误: 需要一个额外的参数来指定文件路径！")
            return False  # 不退出

        filename = args[0]
        if not os.path.isfile(filename):
            print(f"[{self.name}] 错误: 文件不存在: {filename}")
            return False  # 不退出

        if filename.endswith(".json"):
            # 加载JSON配置文件
            self.config.load(filename)
            self.config_to_regs()
        elif filename.endswith(".dat") or filename.endswith(".txt") or filename.endswith(".bin"):
            # 加载.dat/.bin寄存器配置文件
            self.register.load(filename)
            self.regs_to_config()
        else:
            print(f"[{self.name}] 错误: 不支持的文件类型: {filename}. 仅支持 .json/.dat(txt)/.bin")

        return False  # 不退出

    def do_plat(self, args) -> bool:
        """设置平台属性"""
        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument("-p", "--platform", type=str, default="", help="set RK platform")
        parser.add_argument("-x", "--index", type=int, help="XxxModuleIndex")
        param, _ = parser.parse_known_args(args)

        platform_name = param.platform.upper()
        if True: #platform_name == "RK3572":
            self.platform = platform_name
            print(f"[{self.name}] Set platform to: {platform_name}")
            self.update_attributes(platform_name)  # 重新定义配置参数
            if self.register is not None:
                print(f"[{self.name}] Set index to: {param.index}")
                self.register.update(platform=platform_name, index=param.index)
            ## 给子模块也全部设置新的平台
            for mod in self.submodules:
                self.submodules[mod].do_plat(args)
        else:
            print(f"[{self.name}] Error: 当前仅支持 RK3572 平台！")

        return False  # 不退出

    def do_c2r(self, args) -> bool:
        if self.register is None:
            print(f"[{self.name}] self.register not defined!!!")
            return False  # 不退出

        ## parse args & check
        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument("-i", "--input", default="", type=str, nargs='+', help="指定输入配置文件或文件夹")
        parser.add_argument("-o", "--output", default="", type=str, nargs='+', help="导出的目标文件(可多个)或文件夹")
        parser.add_argument("-s", "--suffix", default="bin", type=str, help="多个导出目标文件的后缀: bin(默认)/dat/txt")
        parser.add_argument("-c", "--cat_regs", action="store_true", help="多个导出.bin文件合并为单个.bin文件")
        parser.add_argument(
            "-n", "--align", default=4, type=int, help="控制台与文件美观输出：设置寄存器输出每行的对齐数"
        )
        parser.add_argument(
            "-l", "--pretty_lines_stdout", default=16, type=int, help="控制台美观输出：限制寄存器输出最大行数"
        )
        args, _ = parser.parse_known_args(args)
        if args.suffix not in ["bin", "dat", "txt"]:
            print(f"[{self.name}] 错误: 不支持的导出文件类型: {args.suffix}. 仅支持 bin/dat/txt")
            return False  # 不退出
        args.suffix = "." + args.suffix

        ## 确定输入/输出数量
        inputs = []
        if args.input != "":
            if os.path.isdir(args.input[0]):
                inputs += [os.path.join(args.input[0], f) for f in os.listdir(args.input[0])]
            else:
                inputs += args.input
            inputs = [f for f in inputs if f.endswith(".json")]  # 只读入json文件
            print(f"[{self.name}] 读取到{len(inputs)}个'.json'配置文件")
        if len(inputs) == 0:
            inputs = [""]
        outputs = []
        output_dir = ""
        if args.output != "":
            if len(inputs) > 1:  # n to n
                if not os.path.isdir(args.output[0]):
                    print(f"[{self.name}] 错误: 多个输入文件时，输出应该为目录！")
                    return False  # 不退出
                output_dir = args.output[0]
                outputs += [os.path.join(output_dir, os.path.basename(f).replace(".json", args.suffix)) for f in inputs]
            else:  # 1 to n
                if os.path.isdir(args.output[0]):
                    print(f"[{self.name}] 错误: 单个输入时，输出应该为文件名！")
                    return False  # 不退出
                outputs += args.output
                outputs = [f for f in outputs if f.endswith(".dat") or f.endswith(".bin") or f.endswith(".txt")]
        if len(outputs) == 0:
            outputs = [""] * len(inputs)
            print(f"[{self.name}] 输出文件(夹)未指定或无效，输出到控制台...")

        ## 转至寄存器并输出
        if len(inputs) == 1:  # 1 to n
            self.register.config = self.config
            if inputs[0] != "":
                self.register.load(inputs[0])
            if self.register.config2regs():
                for output in outputs:
                    self.register.dump(output, args.align, args.pretty_lines_stdout)
            else:
                print(f"[{self.name}] 错误: 寄存器配置转换失败！{inputs[0]}")
        else:  # n to n
            for input, output in zip(inputs, outputs):
                self.register.load(input)
                if self.register.config2regs():
                    self.register.dump(output, args.align, args.pretty_lines_stdout)
                else:
                    print(f"[{self.name}] 错误: 寄存器配置转换失败！{input} => {output}")

        ## 合并寄存器文件
        if args.cat_regs and len(outputs) > 0 and args.suffix == ".bin":
            cat_file = os.path.join(output_dir, f"{self.name.lower()}_cat_regs_num_{len(outputs)}.bin")
            with open(cat_file, "wb") as fp:
                for output in outputs:
                    data = np.fromfile(output, dtype=np.uint32)
                    fp.write(data.tobytes())
                    run_cmd(f"rm {output}")
            print(f"[{self.name}] 合并{len(outputs)}个寄存器文件至: {cat_file}")
        return False  # 不退出

    def do_r2c(self, args) -> bool:
        if self.register is None:
            print(f"[{self.name}] self.register not defined!!!")
            return False  # 不退出

        ## parse args & check
        parser = argparse.ArgumentParser(exit_on_error=False)
        parser.add_argument("-i", "--input", type=str, default="", nargs='+', help="输入配置文件(允许多个)或文件夹")
        parser.add_argument("-o", "--output", type=str, default="", nargs='+', help="输出寄存器文件(允许多个)或文件夹")
        parser.add_argument(
            "-a", "--pretty_array_stdout", default=64, type=int, help="控制台美观输出：限制数组类型参数的输出元素量"
        )
        args, _ = parser.parse_known_args(args)

        ## 确定输入/输出数量
        inputs = []
        if args.input != "":
            if os.path.isdir(args.input[0]):
                ## 按'.bin'/'.dat'/'.txt'优先级读取
                inputs += [os.path.join(args.input[0], f) for f in os.listdir(args.input[0]) if f.endswith(".bin")]
                if len(inputs) == 0:
                    inputs += [os.path.join(args.input[0], f) for f in os.listdir(args.input[0]) if f.endswith(".dat")]
                if len(inputs) == 0:
                    inputs += [os.path.join(args.input[0], f) for f in os.listdir(args.input[0]) if f.endswith(".txt")]
            else:
                inputs += args.input
            inputs = [f for f in inputs if f.endswith(".bin") or f.endswith(".dat") or f.endswith(".txt")]
            print(f"[{self.name}] 读取到{len(inputs)}个'.bin/.dat(txt)'寄存器文件")
        else:
            inputs = [""]
        outputs = []
        output_dir = ""
        if args.output != "":
            if len(inputs) > 1:  # n to n
                if not os.path.isdir(args.output[0]):
                    print(f"[{self.name}] 错误: 多个输入文件时，输出应该为目录！")
                    return False  # 不退出
                output_dir = args.output[0]
                outputs += [os.path.join(output_dir, os.path.basename(f) + ".dat") for f in inputs]
            else:  # 1 to 1
                if os.path.isdir(args.output[0]):
                    print(f"[{self.name}] 错误: 单个输入时，输出应该为文件名！")
                    return False  # 不退出
                outputs.append(args.output[0])
            outputs = [f for f in outputs if f.endswith(".json")]
        if len(outputs) == 0:
            outputs = [""]
        print(f"[{self.name}] 识别到{len(inputs)}个'.json'输出配置文件")

        ## 转至配置结构体并输出
        for input, output in zip(inputs, outputs):
            if input != "":
                self.register.load(input)
            if self.register.regs2config():
                self.register.config.dump(output, args.pretty_array_stdout)
            else:
                print(f"[{self.name}] 错误: 寄存器到配置转换失败！ {input} => {output}")

        return False  # 不退出

    def do_quit(self, args) -> bool:
        if self.parent:
            print(f"[{self.name}] 返回 {self.parent.name.upper()} 模块...")
            return True  # 如果有上层则退出当前模块返回上一层
        else:
            sys.exit(0)  # 直接退出程序

    def do_get(self, args) -> bool:
        """获取一个或多个参数值"""
        if not args:
            print(f"[{self.name}] 错误: 需要至少一个参数名！")
            return False  # 不退出
        for part in args:
            if not self.check_attr_str_validate(part, False):
                print(f"[{self.name}] 忽略错误的参数格式: {part}")
                args.remove(part)
        if len(args) == 0:
            return False  # 不退出

        print(f"[{self.name}] 获取到{len(args)}个有效参数对象，查询结果如下:")
        for param_name in args:
            full_name = param_name
            ## 解析嵌套参数: 'xxx.yyy.zzz'
            var_dict = vars(self.config)
            while '.' in param_name:
                names = param_name.split('.')
                if names[0] in var_dict:
                    var_dict = vars(var_dict[names[0]])
                    param_name = '.'.join(names[1:])  # ['yyy', 'zzz'] to 'yyy.zzz'
                else:
                    print(f"[{self.name}] invalid param name: \'{full_name}\'! use \'dump\' to check all params.")
                    param_name = ""
                    break
            ## 格式化输出参数值
            if param_name in var_dict:
                value = var_dict[param_name]
                if type(value) is np.ndarray:
                    value = np.array2string(value.flatten(), separator=",")
                elif type(value) is list:
                    value = ",".join(str(x) for x in value)
                print(f"[{self.name}] get param \'{full_name}\' value: {value}")
            elif param_name != "":
                print(f"[{self.name}] invalid param name: \'{full_name}\'! use \'dump\' to check all params.")

        return False  # 不退出

    def do_set(self, args: list[str]) -> bool:
        """设置一个或多个参数值"""
        if not args:
            print(f"[{self.name}] 错误: 参数设置格式应为 <param1>=<value1> [param2=<value2> ...]")
            return False  # 不退出

        # arg_str = " ".join(args)
        valid_args = args.copy()
        for part in args:
            if not self.check_attr_str_validate(part, True):
                print(f"[{self.name}] 忽略错误的参数格式: {part}")
                valid_args.remove(part)
        if len(valid_args) == 0:
            print(f"[{self.name}] 错误: 参数设置格式应为 <param1>=<value1> [param2=<value2> ...]")
            return False  # 不退出

        if self.register is not None:
            self.register.config = copy.deepcopy(self.config)
            self.register.config2regs()
            old_regs = copy.deepcopy(self.register.regs)  # list[Reg]
            # self.register.dump()

        for part in valid_args:
            full_key, value = part.split('=')
            obj = self.config

            ## 检查嵌套属性是否存在
            if '.' in full_key:
                keys = full_key.split('.')
                b_valid_key = True
                for key in keys[0:-1]:
                    if not hasattr(obj, key):
                        print(f"[{self.name}] invalid param name: \'{full_key}\'! use \'dump\' to check all params.")
                        b_valid_key = False
                        break
                    obj = getattr(obj, key)
                if b_valid_key:
                    key = keys[-1]
                else:
                    continue
            else:
                key = full_key

            ## 设置值
            if hasattr(obj, key):
                if type(getattr(obj, key)) not in (bool, int, float, str, list[int], np.ndarray):
                    print(f"[{self.name}] ignore to set param \'{part}\' since it is an object!")
                    continue

                value = value.strip()
                if value.startswith('[') and value.endswith(']'):
                    try:
                        value = literal_eval(value)  # 安全转换为Python对象
                    except:
                        value = [x.strip() for x in value[1:-1].split(',')]
                    array_obj = getattr(obj, key)
                    for i, x in enumerate(value):
                        array_obj[i] = x
                else:
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    setattr(obj, key, value)
                print(f"[{self.name}] set param \'{full_key}\' value: {value}")
            else:
                print(f"[{self.name}] invalid param name: \'{full_key}\'! use \'dump\' to check all params.")

        if self.register is not None:
            self.register.config = copy.deepcopy(self.config)
            self.register.config2regs()
            new_regs = copy.deepcopy(self.register.regs)
            # self.register.dump()
            cnt_changed = 0
            for old, new in zip(old_regs, new_regs):
                assert old.name == new.name and old.offset == new.offset
                if old.value != new.value:
                    print(
                        "[%s] register 0x%08X changed: 0x%08X ==> 0x%08X"
                        % (self.name, old.offset, old.value, new.value)
                    )
                    cnt_changed += 1
            if cnt_changed == 0:
                print(f"[{self.name}] the value of no register has changed!")

        return False  # 不退出

    ## =============== 通用辅助方法 ===============
    def add_command(self, name: str, handler, param_desc: str = "", description: str = ""):
        self.commands[name] = (handler, param_desc, description)

    def remove_command(self, name: str):
        if name in self.commands:
            del self.commands[name]

    def check_attr_str_validate(self, kv_str: str, check_equal_mark: bool = False) -> bool:
        """
        @param: check_equal_mark - 用在 set() 函数中，有以下逻辑
        1. 判断字符串中有且仅有一个'='号
        2. '='号左边的子字符串以'.'号分割(如果存在的话)后的子字符串必须不含特殊字符且以字母或下划线开头，多个'.'号不可连续
        3. '='号右边可以是数字，也可以是数字列表；如果是数字列表，元素间必须全部以','或者空白字符间隔。
        """
        if not check_equal_mark:
            if re.search(r'[^a-zA-Z0-9_.]', kv_str):
                return False
            return True

        if kv_str.count('=') != 1:
            return False

        left, right = kv_str.split('=')

        if re.search(r'[^a-zA-Z0-9_.]', left):
            return False
        if '..' in left:
            return False

        part_names = left.split('.') if '.' in left else [left]
        for part_name in part_names:
            if not re.fullmatch(r'^[a-zA-Z_][a-zA-Z0-9_]*$', part_name):
                return False

        if not re.fullmatch(r'^\d+$', right) and not re.fullmatch(r'^\[\s*(\d+(\s*,\s*\d+)*)?\s*\]$', right):
            return False

        return True

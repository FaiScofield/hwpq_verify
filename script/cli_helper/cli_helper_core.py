"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-28
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
from config_def.module_config_core import ModuleConfigCore  # 配置参数基类，新增模块需要在`config_def`中增加对应的参数定义文件
from reg_def.module_reg_core import ModuleRegisterCore  # 寄存器基类，新增模块需要在`reg_def`中增加对应的寄存器定义文件


class ModuleHelperCore(ABC):
    """Command-Line Interface Helper base framework CLI基类框架。
    * 有新的模块请继承此类，并在`cli_helper_main.py`文件中加入该新模块。
    * 成员函数说明：
    *   `do_xxx`形式的函数返回值表示执行后是否退出脚本，固除了`do_quit`函数返回True, 其他函数均返回False.
    * 成员变量说明：
    *   `self.parent`: 模块名称，用于提示和命令提示。
    *   `self.config`: 基于`ModuleConfigCore`类的配置参数类，实现了对`.json`格式配置（含软软件/硬件参数）的加载、保存、生成、打印等功能。
    *   `self.register`: 基于`ModuleRegisterCore`类的寄存器参数类，实现了对`.bin/.txt/.dat`格式寄存器配置的加载、保存、生成、打印等功能。
    """

    def __init__(self, name: str, platform: str = "RK3572", parent: Optional["ModuleHelperCore"] = None):
        self.name = name.upper()
        self.platform = platform.upper()
        self.parent = parent  # 无上级窗口则为空
        self.config, self.register = self.define_config_and_regs()  # 子类需要复写`define_config_and_regs`的实现
        self.submodules = {}  # 空的子模块，仅供顶层Main模块使用

        ## 常驻命令注册表: name, (handler, param_desc, description)
        self.commands = {
            "help": (self.do_help, "", "显示命令帮助信息"),
            "quit": (self.do_quit, "", "退出或返回上一级"),
            "plat": (self.do_plat, "<name>", "设置平台: (Only RK3572 for now!)"),
            "load": (self.do_load, "<file>", "加载 .json 配置文件或 .dat/.bin 寄存器文件"),
            "gen": (
                self.do_gen,
                "[-n num] [-o filename/directory] [-s rand_seed]",
                "生成 num 个随机配置, 可输出到文件(num=1)或文件夹(num>1)",
            ),
            "dump": (self.do_dump, "[filenames]", "指定文件名(.json/.dat/.bin, 可多个)时则导出当前配置到对应文件, 否则打印到控制台"),
            "reg": (self.do_reg, "[target]", "生成寄存器配置值"),
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
    def define_config_and_regs(self) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        """定义模块的配置参数(由子类实现)"""
        config = None
        register = None
        return config, register

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
        config = self.config
        reg_ok = self.config_to_regs()

        if not args:
            ## 控制台显示
            config.dump()
            if reg_ok:
                self.register.dump()
        else:
            ## 导出到文件
            targets = args
            for target in targets:
                try:
                    if target.endswith(".json"):
                        config.dump(target)
                    elif reg_ok and (target.endswith(".dat") or target.endswith(".txt")):
                        self.register.dump(target, align=4)
                    elif reg_ok and target.endswith(".bin"):
                        self.register.dump(target)
                    else:
                        print(f"[{self.name}] 错误: 不支持的输出文件类型: {target}. 仅支持 .json/.dat/.bin")
                    print(f"[{self.name}] 配置已导出到: {os.path.abspath(target)}")
                except Exception as e:
                    print(f"[{self.name}] 导出配置信息至文件 {os.path.abspath(target)} 失败: {str(e)}")

        return False  # 总是返回False表示不退出

    def do_gen(self, args) -> bool:
        ## parse args & check
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-n", "--num", default=1, type=int, help="生成随机配置的数量")
            parser.add_argument("-s", "--rand_seed", type=int, help="起始随机种子(n>1时随机种子自增1)")
            parser.add_argument("-o", "--file_or_dir", default="", type=str, help="生成的配置文件或目录(n>1时指定目录)")
            args = parser.parse_args(args)
        except:
            return False  # 不退出

        args.num = max(1, args.num)
        abs_path = os.path.abspath(args.file_or_dir)
        if args.file_or_dir == "":
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
            print(f"[{self.name}] 错误: 不支持的文件类型: {filename}. 仅支持 .json/.dat/.txt/.bin")

        return False  # 不退出

    def do_plat(self, args) -> bool:
        """设置平台属性"""
        if not args:
            print(f"[{self.name}] Error: 需要一个额外的参数来指定平台名称！")
            return False  # 不退出

        platform_name = args[0].upper()
        self.platform = platform_name
        print(f"[{self.name}] Set platform to: {platform_name}")

        ## 给子模块也全部设置新的平台
        for mod in self.submodules:
            self.submodules[mod].do_plat(args)

        return False  # 不退出

    def do_reg(self, args) -> bool:
        """生成寄存器配置值"""
        if self.config_to_regs():
            self.register.dump()
        else:
            print(f"[{self.name}] 错误: 寄存器配置生成失败！")
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

        print(f"[{self.name}] \n参数值查询结果:")
        for param_name in args:
            # vars(self.config).items()
            if hasattr(self.config, param_name):  # case sensitive
                value = getattr(self.config, param_name)
                if type(value) is np.ndarray:
                    value = np.array2string(value.flatten(), separator=",")
                elif type(value) is list:
                    value = ",".join(str(x) for x in value)
                print(f"[{self.name}] get param \'{param_name}\' value: {value}")
            else:
                print(f"[{self.name}] invalid param name: \'{param_name}\'! use \'dump\' to check all params.")

        return False  # 不退出

    def do_set(self, args) -> bool:
        """设置一个或多个参数值"""
        if not args:
            print(f"[{self.name}] 错误: 参数设置格式应为 <param1>=<value1> [param2=<value2> ...]")
            return False  # 不退出

        arg_str = " ".join(args)
        if "=" not in arg_str:
            print(f"[{self.name}] 错误: 参数设置格式应为 <param1>=<value1> [param2=<value2> ...]")
            return False  # 不退出

        if self.register is not None:
            self.register.config = copy.deepcopy(self.config)
            self.register.config2regs()
            old_regs = copy.deepcopy(self.register.regs)  # list[Reg]
            # self.register.dump()

        items = re.findall(r'(\w+)=([^=]+)(?=\s+\w+=|$)', arg_str.strip())
        for key, value in items:
            if hasattr(self.config, key):
                value = value.strip()
                if value.startswith('[') and value.endswith(']'):
                    try:
                        value = literal_eval(value)  # 安全转换为Python对象
                    except:
                        value = [x.strip() for x in value[1:-1].split(',')]
                else:
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)

                setattr(self.config, key, value)
                print(f"[{self.name}] set param \'{key}\' value: {value}")
            else:
                print(f"[{self.name}] invalid param name: \'{key}\'! use \'dump\' to check all params.")

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

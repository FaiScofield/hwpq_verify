"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-18
"""

import sys
import os
import json
import re
import random
import argparse
import copy
from ast import literal_eval
from tqdm import tqdm
from abc import ABC, abstractmethod
from typing import Optional

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from config_def.module_config_core import ModuleConfigCore
from reg_def.module_reg_core import ModuleRegisterCore

class ModuleHelperCore(ABC):
    """Command-Line Interface Helper base framework"""

    def __init__(self, name: str, platform: str = "RK3572", parent: Optional["ModuleHelperCore"] = None):
        self.name = name.upper()
        self.platform = platform.upper()
        self.parent = parent # 无上级窗口则为空
        self.define_config_and_regs()  # 创建变量 self.config / self.config, 需要复写
        self.modules = {}  # 子模块，空的，暂时仅供顶层使用

        ## 命令注册表: name, (handler, param_desc, description)
        self.commands = {
            "help": (self.do_help, "", "显示命令帮助信息"),
            "quit": (self.do_quit, "", "退出或返回上一级"),
            "plat": (self.do_plat, "<name>", "设置平台: (Only RK3572 for now!)"),
            "load": (self.do_load, "<file>", "加载 .json 配置文件或 .dat/.bin 寄存器文件"),
            "gen": (self.do_gen, "[-n num] [-o filename/directory] [-s rand_seed]", "生成 num 个随机配置, 可输出到文件(num=1)或文件夹(num>1)"),
            "dump": (self.do_dump, "[filenames]", "指定文件名(.json/.dat/.bin, 可多个)时则导出当前配置到对应文件, 否则打印到控制台"),
            "reg": (self.do_reg, "[target]", "生成寄存器配置值 (TODO)"),
            "get": (self.do_get, "<name1> [name2 name3 ...]", "获取配置参数的值"),
            "set": (self.do_set, "<name1=value1> [name2=value2 name3=value3 ...]", "设置配置参数的值"),
        }

    def run(self):
        """运行模块的主循环"""
        print(f"\n=== 进入 {self.name.upper()} 模块 ===")
        self.do_help([])  # 显示初始帮助信息

        while True:
            try:
                user_input = input(f"({self.name}_{self.platform})> ").strip()
                if not user_input:
                    continue

                # 解析命令和参数
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                # 处理命令
                if command in self.commands:
                    handler = self.commands[command][0]
                    should_exit = handler(args)
                    if should_exit:
                        return None  # 返回上一级
                elif command == self.name.lower():
                    print(f"[{self.name}] 正处于当前模块中，无需切换")
                    continue
                elif self.parent is not None and self.parent.is_valid_module(command):
                    return command  # 返回上一级并由上一级切换到另一个模块
                else:
                    print(f"[{self.name}] 无效命令: {command}。输入 'help' 查看帮助")

            except KeyboardInterrupt:
                print(f"[{self.name}] \n操作已取消")
            except Exception as e:
                print(f"[{self.name}] 错误: {str(e)}")
                # 详细的调试信息(调试模式下)
                # import traceback
                # traceback.print_exc()

    ## =============== 虚函数，需要继承实现 ===============
    @abstractmethod
    def define_config_and_regs(self):
        """定义模块的配置参数(由子类实现)"""
        self.config = ModuleConfigCore(self.name)
        self.register = ModuleRegisterCore(self.name, self.platform)
        pass

    # @abstractmethod
    def config_to_regs(self) -> bool:
        if self.register is not None:
            self.register.config = self.config
            return self.register.config2regs()
        return False

    # @abstractmethod
    def regs_to_config(self) -> bool:
        if self.register is not None:
            ok = self.register.regs2config()
            self.config = self.register.config
            return ok
        return False

    ## =============== 通用命令处理函数 ===============
    def do_help(self, args) -> bool:
        print(f"\n[{self.name}] 可用命令如下:")
        # max_desc_len = max(len(pipe[1]) for _, pipe in self.commands)

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

        return False

    def do_dump(self, args) -> bool:
        """导出配置到文件或控制台"""
        config = self.config
        regs = self.config_to_regs()

        if not args:
            ## 控制台显示
            config.dump()
            # regs.dump()
        else:
            ## 导出到文件
            targets = args
            for target in targets:
                try:
                    if target.endswith(".json"):
                        config.dump(target)
                    elif target.endswith(".dat"):
                        regs.dump(target)
                    elif target.endswith(".bin"):
                        regs.dump(target, align=4)
                    else:
                        print(f"[{self.name}] 错误: 不支持的输出文件类型: {target}. 仅支持 .json/.dat/.bin")
                    print(f"[{self.name}] 配置已导出到: {os.path.abspath(target)}")
                except Exception as e:
                    print(f"[{self.name}] 导出配置信息至文件 {os.path.abspath(target)} 失败: {str(e)}")

        return False

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
            return False

        filename = args[0]
        if not os.path.isfile(filename):
            print(f"[{self.name}] 错误: 文件不存在: {filename}")
            return False

        if filename.endswith(".json"):
            # 加载JSON配置文件
            self.config.load(filename)
            self.config_to_regs()
        elif filename.endswith(".dat") or filename.endswith(".bin"):
            # 加载.dat/.bin寄存器配置文件
            self.reg.load(filename)
            self.regs_to_config()
        else:
            print(f"[{self.name}] 错误: 不支持的文件类型: {filename}. 仅支持 .json/.dat/.bin")

        return False

    def do_plat(self, args) -> bool:
        """设置平台属性"""
        if not args:
            print(f"[{self.name}] Error: 需要一个额外的参数来指定平台名称！")
            return False

        platform_name = args[0]
        self.platform = platform_name
        print(f"[{self.name}] Set platform to: {platform_name}")

        # 更新平台相关的配置
        self.apply_platform_config()

        ## 给子模块也全部设置新的平台
        for mod in self.modules:
            self.modules[mod].do_plat(args)

        return False  # 不退出

    def do_reg(self, args) -> bool:
        """生成寄存器配置值"""
        ok = self.config_to_regs()
        if ok:
            self.register.dump()
        else:
            ok = False
            print(f"[{self.name}] 错误: 寄存器配置生成失败！")
        return ok

    def do_quit(self, args) -> bool:
        if self.parent:
            print(f"[{self.name}] 返回 {self.parent.name.upper()} 模块...")
            return True  # 退出当前模块
        else:
            sys.exit(0)

    def do_get(self, args) -> bool:
        """获取一个或多个参数值"""
        if not args:
            print(f"[{self.name}] 错误: 需要至少一个参数名！")
            return False

        print(f"[{self.name}] \n参数值查询结果:")
        for param_name in args:
            if hasattr(self.config, param_name):
                value = getattr(self.config, param_name)
                print(f"[{self.name}] get param \'{param_name}\' value: {value}")
            else:
                print(f"[{self.name}] invalid param name: \'{param_name}\'!")

        # 不退出
        return False

    def do_set(self, args) -> bool:
        """设置一个或多个参数值"""
        if not args:
            print(f"[{self.name}] 错误: 参数设置格式应为 <param1>=<value1> [param2=<value2> ...]")
            return False

        arg_str = " ".join(args)
        if "=" not in arg_str:
            print(f"[{self.name}] 错误: 参数设置格式应为 <param1>=<value1> [param2=<value2> ...]")
            return False

        if self.register is not None:
            self.register.config = copy.deepcopy(self.config)
            self.register.config2regs()
            old_regs = copy.deepcopy(self.register.regs) # list[Reg]
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
                print(f"[{self.name}] set param \'{key}\' to {value}")
            else:
                print(f"[{self.name}] failed to set param \'{key}\' to {value}")

        if self.register is not None:
            self.register.config = copy.deepcopy(self.config)
            self.register.config2regs()
            new_regs = copy.deepcopy(self.register.regs)
            # self.register.dump()
            for old, new in zip(old_regs, new_regs):
                assert(old.name == new.name and old.offset == new.offset)
                if old.value != new.value:
                    print("[%s] register 0x%08X changed: 0x%08X ==> 0x%08X." % (self.name, old.offset, old.value, new.value))

        # 不退出
        return False

    ## =============== 通用辅助方法 ===============
    def is_valid_module(self, module_name: str) -> bool:
        return False  # 只给最顶层APP级使用

    def apply_platform_config(self):
        """应用平台相关的配置(默认实现为空，子类可覆盖)"""
        pass

    def add_command(self, name: str, handler, param_desc: str = "", description: str = ""):
        self.commands[name] = (handler, param_desc, description)

    def remove_command(self, name: str):
        if name in self.commands:
            del self.commands[name]

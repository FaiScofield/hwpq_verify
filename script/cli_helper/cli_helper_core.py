"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-07
"""

import sys
import os
import json
import random
import argparse
from tqdm import tqdm
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Type
from ctypes import Structure, c_uint


class ModuleRegister:
    def __init__(self, platform: str, regs: List[Structure]):
        # super().__init__()
        self.platform = platform.upper()
        self.regs = regs


class ModuleHelper(ABC):
    """Command-Line Interface Helper base framework"""

    def __init__(self, name: str, platform: str = "RK3572", parent: Optional["ModuleHelper"] = None):
        self.name = name.upper()
        self.platform = platform.upper()
        self.parent = parent
        self.config = self.define_config()  # 创建配置参数变量，需要复写
        self.regs = self.config_to_registers()  # 创建寄存器变量，需要复写
        self.modules = {}  # 子模块，空的，顶层使用

        ## 命令注册表: name, (handler, param_desc, description)
        self.commands = {
            "help": (self.do_help, "", "显示命令帮助信息"),
            "quit": (self.do_quit, "", "退出或返回上一级"),
            "plat": (self.do_plat, "<name>", "设置平台属性"),
            "load": (self.do_load, "<file>", "加载.json配置文件或.dat/.bin寄存器文件"),
            "gen": (self.do_gen, "[-n num] [-o filename/directory] [-s rand_seed]", "生成 num 个随机配置, 可输出到文件(num=1)或文件夹(num>1)"),
            "dump": (self.do_dump, "[filenames]", "指定文件名(.json/.dat/.bin, 可多个)时则导出当前配置到对应文件, 否则打印到控制台"),
            "reg": (self.do_reg, "[target]", "生成寄存器配置值 (TODO)"),
            "get": (self.do_get, "<params>(name1 name2 ...)", "获取配置参数值"),
            "set": (self.do_set, "<params>(-name1_short value1  --name2_long=value2 ...)", "设置配置参数值"),
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
                # 详细的调试信息（调试模式下）
                # import traceback
                # traceback.print_exc()

    @abstractmethod
    def define_config(self):
        """定义模块的配置参数（由子类实现）"""
        # 子类应该在此方法中设置self.config属性
        pass

    @abstractmethod
    def config_to_registers(self) -> map:
        """将配置转换为32位寄存器值（由子类实现）"""
        # 返回32位寄存器值
        pass

    @abstractmethod
    def get_param(self, param_name: str) -> Any:
        """获取特定参数值（由子类实现）"""
        pass

    @abstractmethod
    def set_param(self, param_name: str, value: Any) -> bool:
        """设置特定参数值（由子类实现）"""
        # 返回设置是否成功
        return True

    # @abstractmethod
    def is_valid_module(self, module_name: str) -> bool:
        return False  # 只给最顶层APP级使用

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
        regs = self.config_to_registers()

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
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--num", default=1, type=int, help="生成随机配置的数量")
        parser.add_argument("-s", "--rand_seed", type=int, help="起始随机种子(n>1时随机种子自增1)")
        parser.add_argument("-o", "--file_or_dir", default="", type=str, help="生成的配置文件或目录(n>1时指定目录)")
        args = parser.parse_args(args)

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
            if ok:
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
            self.load_config_json(filename)
        elif filename.endswith(".dat"):
            # 加载.dat寄存器配置文件
            self.load_config_reg(filename, True)
        elif filename.endswith(".bin"):
            # 加载.bin寄存器配置文件
            self.load_config_reg(filename, False)
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
        reg_value = self.config_to_registers()

        # 转换为16进制字符串
        reg_hex = f"{reg_value:08x}"

        if args:
            # 导出到文件
            target = args[0]
            try:
                with open(target, "w") as f:
                    f.write(reg_hex)
                print(f"[{self.name}] 寄存器值已导出到: {os.path.abspath(target)}")
            except Exception as e:
                print(f"[{self.name}] 导出失败: {str(e)}")
        else:
            # 控制台显示
            print(f"[{self.name}] \n寄存器值 ({self.platform}平台):")
            print(f"[{self.name}]   32位: {reg_value}")
            print(f"[{self.name}]   16进制: 0x{reg_hex}")
            print(f"[{self.name}]   二进制: {bin(reg_value)}")

        # 不退出
        return False

    def do_quit(self, args) -> bool:
        if self.parent:
            print(f"[{self.name}] 返回 {self.parent.name.upper()} 模块...")
            return True  # 退出当前模块
        else:
            sys.exit(0)

    def do_get(self, args) -> bool:
        """获取多个参数值"""
        if not args:
            print(f"[{self.name}] 错误: 需要至少一个参数名！")
            return False

        print(f"[{self.name}] \n参数值查询结果:")
        for param_name in args:
            value = self.get_param(param_name)
            if value is not None:
                print(f"[{self.name}]   {param_name}: {value}")
            else:
                print(f"[{self.name}]   {param_name}: 无效参数名！")

        # 不退出
        return False

    def do_set(self, args) -> bool:
        """设置多个参数值"""
        if len(args) < 2 or len(args) % 2 != 0:
            print(f"[{self.name}] 错误: 参数格式应为 <param1> <value1> [param2 <value2> ...]")
            return False

        # 成对处理参数
        results = []
        for i in range(0, len(args), 2):
            param_name = args[i]
            value_str = args[i + 1]

            # 尝试类型转换
            try:
                # 尝试整数转换
                value = int(value_str)
            except ValueError:
                try:
                    # 尝试浮点数转换
                    value = float(value_str)
                except ValueError:
                    # 作为字符串处理
                    value = value_str

            success = self.set_param(param_name, value)
            if success:
                current_value = self.get_param(param_name)
                results.append(f"{param_name} = {current_value}")
            else:
                results.append(f"{param_name}: 设置失败")

        # 显示设置结果
        print(f"[{self.name}] \n参数设置结果:")
        for result in results:
            print(f"[{self.name}]   {result}")

        # 不退出
        return False

    ## =============== 通用辅助方法 ===============
    def load_config_json(self, filename: str):
        """加载JSON配置文件"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[{self.name}] 错误: 加载JSON配置文件失败: {str(e)}")
            return False

    def load_config_reg(self, filename: str, is_dat: bool):
        """加载.dat/.bin寄存器配置文件"""
        if is_dat:
            # 加载.dat文件
            try:
                with open(filename, "rt") as f:
                    data = f.read().strip()
            except Exception as e:
                print(f"[{self.name}] 错误: 加载.dat文件失败: {str(e)}")
        else:
            try:
                with open(filename, "rb") as f:
                    data = f.read()
            except Exception as e:
                print(f"[{self.name}] 错误: 加载.bin文件失败: {str(e)}")
                return False

    def get_config_data(self) -> Dict[str, Any]:
        """获取配置数据的字典形式"""
        return {"module": self.name, "platform": self.platform, **self.config}

    def generate_random_config(self):
        """生成随机配置（默认实现，子类可覆盖）"""
        for key, value in self.config.items():
            # 根据值的类型生成随机值
            if isinstance(value, bool):
                self.config[key] = random.choice([True, False])
            elif isinstance(value, int):
                self.config[key] = random.randint(0, 100)
            elif isinstance(value, float):
                self.config[key] = round(random.uniform(0, 1), 3)
            elif isinstance(value, str):
                self.config[key] = f"random-{random.randint(1, 100)}"
            elif isinstance(value, list):
                self.config[key] = [random.randint(1, 10) for _ in range(len(value))]
            elif isinstance(value, dict):
                self.config[key] = {k: random.random() for k in value.keys()}

    def apply_platform_config(self):
        """应用平台相关的配置（默认实现为空，子类可覆盖）"""
        pass

    ## =============== 便捷方法 ===============
    def add_command(self, name: str, handler, param_desc: str = "", description: str = ""):
        self.commands[name] = (handler, param_desc, description)

    def remove_command(self, name: str):
        if name in self.commands:
            del self.commands[name]

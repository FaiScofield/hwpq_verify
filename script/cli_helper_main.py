'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_main.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description : 
LastEditTime: 2025-07-07
'''

from cli_helper.cli_helper_core import *
from cli_helper.cli_helper_sharp import *
from cli_helper.cli_helper_acm import *
from cli_helper.cli_helper_cfa import *
from typing import Any


class MainApp(ModuleHelper):
    def __init__(self, platform: str = 'RK3572'):
        super().__init__("MAIN", platform)

        ## 当前支持的所有模块
        self.modules = {
            "sharp": SharpHelper("sharp", platform, self),
            "acm": AcmHelper("acm", platform, self),
            # "dci": DciHelper("dci", platform, self),
            "cfa": CfaHelper("cfa", platform, self),
        }

        ## 直接覆盖掉基类的命令内容
        self.commands = {
            "help": (self.do_help, "", "show this help message"),
            "quit": (self.do_quit, "", "exit program"),
            "plat": (self.do_plat, "<name>", "set the platform: RK3576, RK3572, RK3538, etc."),
            "sharp": (self.do_sharp, "", "enter module SHARP"),
            "acm": (self.do_acm, "", "enter module ACM"),
            # "dci": (self.do_dci, "", "enter module DCI"),
            # "csc": (self.do_csc, "", "enter module CSC"),
            "cfa": (self.do_cfa, "", "enter module CFA"),
        }

    def run(self) -> bool:
        print(f"\n=== 欢迎使用 fpga_verify_helep_cli 工具 ===")
        self.do_help([])  # 显示初始帮助信息

        while True:
            try:
                user_input = input(f"({self.name}_{self.platform})> ").strip()
                if not user_input:
                    continue

                ## 解析命令和参数
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                ## 处理命令
                if command in self.commands:
                    while True:
                        handler = self.commands[command][0]
                        exit_or_switch = handler(args)
                        ## 是否直接退出
                        if type(exit_or_switch) == bool:
                            if exit_or_switch: # exit
                                exit(0)
                            else:
                                break
                        ## 是否切换到其他模块
                        elif exit_or_switch in self.modules:
                            command = exit_or_switch
                            continue
                        ## 从下一级返回，等待下一个命令输入
                        else:
                            self.do_help([])
                            break
                else:
                    print(f"无效命令: {command}。输入 'help' 查看帮助")
            except KeyboardInterrupt:
                print("\n操作已取消")
            except Exception as e:
                print(f"错误: {str(e)}")
                # 详细的调试信息（调试模式下）
                # import traceback
                # traceback.print_exc()

        return False

    def do_sharp(self, args) -> str:
        return self.modules['sharp'].run()

    def do_acm(self, args) -> str:
        print(f"[{self.name}] TODO: ACM 模块暂未支持")
        return None

    def do_dci(self, args) -> str:
        print(f"[{self.name}] TODO: DCI 模块暂未支持")
        return None

    def do_csc(self, args) -> str:
        print(f"[{self.name}] TODO: CSC 模块暂未支持")
        return None

    def do_cfa(self, args) -> str:
        return self.modules['cfa'].run()

    def is_valid_module(self, module_name: str) -> bool:
        return module_name in self.modules

    ## =============== 主程序不需要实现这些抽象方法 ===============
    def define_config(self):
        return None

    def config_to_registers(self) -> int:
        return 0

    def get_param(self, param_name: str) -> Any:
        return None

    def set_param(self, param_name: str, value: Any) -> bool:
        return None


if __name__ == "__main__":
    app = MainApp()
    app.run()

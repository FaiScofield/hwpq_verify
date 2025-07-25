'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_main.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-25
'''

from cli_helper import *
from typing import Union


class MainApp(ModuleHelperCore):
    def __init__(self, platform: str = 'RK3572'):
        super().__init__("MAIN", platform)

        ## 当前支持的所有模块，新增模块请加在此处
        self.submodules = {
            "sharp": SharpHelper("sharp", platform, self),
            "acm": AcmHelper("acm", platform, self),
            "dci": DciHelper("dci", platform, self),
            "csc": CscHelper("csc", platform, self),
            "cfa": CfaHelper("cfa", platform, self),
        }

        ## 直接覆盖掉基类的常驻命令内容，新增模块请在此处增加一个do_xxx的处理函数，并在后面增加它的实现
        self.commands = {
            "help": (self.do_help, "", "show this help message"),
            "quit": (self.do_quit, "", "exit program"),
            "plat": (self.do_plat, "<name>", "set the platform: RK3576, RK3572, RK3538, etc."),
            "sharp": (self.do_sharp, "", "enter module SHARP"),
            "acm": (self.do_acm, "", "enter module ACM"),
            "dci": (self.do_dci, "", "enter module DCI"),
            "csc": (self.do_csc, "", "enter module CSC"),
            "cfa": (self.do_cfa, "", "enter module CFA"),
        }

    ## =============== 主程序不需要实现该抽象方法 ===============
    def define_config_and_regs(self) -> tuple[Optional[ModuleConfigCore], Optional[ModuleRegisterCore]]:
        return None, None

    ## =============== 主循环函数 ===============
    def run(self):
        print(f"\n=== 欢迎使用 fpga_verify_helep_cli 工具 ===")
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

                ## 处理命令
                if command in self.commands:
                    while True:
                        cmd_handler = self.commands[command][0]
                        exit_or_switch = cmd_handler(args)
                        ## 是否直接退出，基础常驻命令(do_help/do_quit/do_plat)返回bool
                        if type(exit_or_switch) == bool:
                            if exit_or_switch:  # exit
                                exit(0)
                            else:
                                break
                        ## 是否切换到其他模块, do_xxx返回str
                        elif exit_or_switch in self.submodules:
                            command = exit_or_switch
                            continue
                        ## 从下一级返回，等待本级的下一个命令输入
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

    ## =============== 常驻命令处理函数 ===============
    def do_sharp(self, args) -> str:
        return self.submodules['sharp'].run()

    def do_acm(self, args) -> str:
        return self.submodules['acm'].run()

    def do_dci(self, args) -> str:
        return self.submodules['dci'].run()

    def do_csc(self, args) -> str:
        return self.submodules['csc'].run()

    def do_cfa(self, args) -> str:
        return self.submodules['cfa'].run()


if __name__ == "__main__":
    app = MainApp()
    app.run()

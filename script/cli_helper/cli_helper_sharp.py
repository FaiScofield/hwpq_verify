'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : cli_helper_sharp.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-02
Description :
LastEditTime: 2025-07-02 21:13:29
'''

from .cli_helper_core import *
from typing import Optional, Dict, Any, List, Type
from ctypes import Structure, c_uint

class SharpLiteConfig:
    def __init__(self):
        sharp_en = 1
        sharp_config_mode = 1
        sigma0 = 1
        sigma1 = 1
        gain0 = 1
        gain1 = 1
        coring_thr = 1
        shoot_ctrl_en = 1
        shoot_ctrl_delta_offset = 1
        shoot_ctrl_alpha_pos = 1
        shoot_ctrl_alpha_neg = 1
        shoot_ctrl_alpha_pos_unlimit = 1
        shoot_ctrl_alpha_neg_unlimit = 1
        core_direct_config_mode = 1
        core_A = 1
        core_B = 1
        core_C = 1
        fix_gain = 1
        sharp_roi_en = 1
        sharp_roi_xstart = 1
        sharp_roi_xend = 1
        sharp_roi_ystart = 1
        sharp_roi_yend = 1
        sharp_ink_enable = 1
        sharp_ink_mode = 1
        sharp_ink_h = 1
        sharp_ink_v = 1

class SharpHelper(ModuleHelper):
    def __init__(self, name: str = "SHARP", platform: str = 'RK3572', parent: Optional['ModuleHelper'] = None):
        super().__init__(name, platform, parent)
        self.define_config()

        ## 增加额外的命令
        self.add_command('opt', self.do_optimize, "<level>", "执行图像优化处理")


    ## =============== overwrite methods  ===============
    def define_config(self):
        """定义Sharp模块的配置参数"""
        self.config = {
            "enable": True,
            "peaking_gain": 1.5,
            "cores": 4,
            "threshold": 0.8,
            "mode": "balanced",
            "region_weights": [1.0, 0.8, 0.6],
            "tuning_params": {
                "low_freq": 0.2,
                "high_freq": 0.9
            }
        }

    def config_to_registers(self) -> map:
        """将Sharp配置转换为32位寄存器值"""
        # # 简化转换逻辑
        # enable_bit = 0x80000000 if self.config["enable"] else 0
        # gain_int = int(self.config["peaking_gain"] * 10)
        # cores = min(self.config["cores"], 7)  # 限制在3位以内
        # threshold = int(self.config["threshold"] * 100)

        # # 合并为32位值
        # reg_value = (
        #     enable_bit |
        #     (gain_int << 24) |
        #     (cores << 20) |
        #     (threshold << 12)
        # )
        # return reg_value
        pass

    def get_param(self, param_name: str) -> Any:
        """获取特定参数值"""
        # 支持嵌套参数的访问
        parts = param_name.split('.')
        value = self.config

        try:
            for part in parts:
                if isinstance(value, list):
                    index = int(part)
                    if 0 <= index < len(value):
                        value = value[index]
                    else:
                        return None
                elif isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        except (KeyError, IndexError, ValueError):
            return None

    def set_param(self, param_name: str, value: Any) -> bool:
        """设置特定参数值"""
        parts = param_name.split('.')
        current = self.config

        try:
            # 遍历到最后一个位置
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], (dict, list)):
                    # 创建中间结构
                    if part.isdigit():
                        # 列表索引
                        index = int(part)
                        if not isinstance(current, list):
                            current = []
                        # 确保列表长度
                        while index >= len(current):
                            current.append(None)
                        current[index] = {} if not parts[-1].isdigit() else []
                        current = current[index]
                    else:
                        # 字典键
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                else:
                    current = current[part]

            # 设置最终值
            last_part = parts[-1]

            if isinstance(current, list):
                index = int(last_part)
                if 0 <= index < len(current):
                    current[index] = value
                    return True
            elif isinstance(current, dict) and last_part in current:
                # 执行类型检查
                original_type = type(current[last_part])

                # 尝试类型转换
                try:
                    if original_type is bool:
                        if str(value).lower() in ["true", "1", "yes"]:
                            converted = True
                        elif str(value).lower() in ["false", "0", "no"]:
                            converted = False
                        else:
                            print(f"警告: {last_part}需要布尔值 (true/false), 使用默认值")
                            return False
                    else:
                        converted = original_type(value)

                    current[last_part] = converted
                    return True
                except (ValueError, TypeError):
                    print(f"类型错误: {last_part}需要{original_type.__name__}类型")
            return False
        except (KeyError, IndexError, ValueError):
            return False

    ## =============== Sharp 模块特有命令 ===============
    def do_optimize(self, args) -> bool:
        """执行图像优化处理 - Sharp特有的自定义命令"""
        if not args:
            print("错误: 需要指定优化级别")
            return False

        try:
            level = int(args[0])
            print(f"在优化级别 {level} 下执行Sharp图像处理...")
            # 这里添加实际的处理逻辑
            return False
        except ValueError:
            print("错误: 优化级别必须是整数")
            return False


if __name__ == "__main__":
    runner = SharpHelper()
    runner.run()
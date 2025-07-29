'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description :
LastEditTime: 2025-07-29
'''
import os
import sys
import numpy as np
from abc import ABC, abstractmethod

sys.path.append(os.path.normpath(os.path.dirname(__file__) + "/../"))
from utils import setup_logger


class ModuleConfigCore(ABC):
    def __init__(self, name: str, version: str = 'unknown'):
        self.name = name.upper()
        self.valid = False
        self.version = version
        self.randSeed = 114514
        self.logger = setup_logger(self.name)

    @abstractmethod
    def dump(self, filename: str = "", pretty_array_stdout: int = 128) -> bool:
        return False

    @abstractmethod
    def load(self, filename: str) -> bool:
        return False

    @abstractmethod
    def check(self) -> bool:
        return False

    @abstractmethod
    def gen(self, seed: int = 114514, **kwargs) -> bool:
        self.randSeed = seed
        return False

    def get_seed(self) -> int:
        return self.randSeed

    def pretty_print_dict(self, key, val, indent=2, pretty_array_stdout=32):
        if isinstance(val, dict):
            self.logger.info(" " * indent + "- %s: {" % key)
            for k, v in val.items():
                self.pretty_print_dict(k, v, indent + 2, pretty_array_stdout)
            self.logger.info(" " * indent + "} #%s" % key)
        else:
            if isinstance(val, (list, tuple, set, np.ndarray)) and len(val) > pretty_array_stdout:
                half_len = (pretty_array_stdout + 1) // 2
                val_str = f"{val[:half_len]}... (omit items between [{half_len}, {len(val) - half_len}] since `pretty_array_stdout={pretty_array_stdout}`) ...{val[-pretty_array_stdout:]}"
                self.logger.info(" " * indent + f"- {key}: {val_str}")
            else:
                self.logger.info(" " * indent + f"- {key}: {val}")

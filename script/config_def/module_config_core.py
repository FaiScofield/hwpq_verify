'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description :
LastEditTime: 2025-07-25
'''
import os
import sys
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
    def dump(self, filename) -> bool:
        return False

    @abstractmethod
    def load(self, filename) -> bool:
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

    def pretty_print_dict(self, key, val, indent=2):
        if isinstance(val, dict):
            self.logger.info(" " * indent + "- %s: {" % key)
            for k, v in val.items():
                self.pretty_print_dict(k, v, indent + 2)
            self.logger.info(" " * indent + "} #%s" % key)
        else:
            self.logger.info(" " * indent + f"- {key}: {val}")

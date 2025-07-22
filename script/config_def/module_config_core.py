'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description :
LastEditTime: 2025-07-22
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
    def gen(self, seed: int = 114514, **kwargs) -> int:
        self.randSeed = seed
        return seed

    def get_seed(self) -> int:
        return self.randSeed
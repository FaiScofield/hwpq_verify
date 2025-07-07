'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_config_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description : 
LastEditTime: 2025-07-07
'''

from abc import ABC, abstractmethod

class ModuleConfigCore(ABC):
    def __init__(self, name: str, version: str = 'unknown'):
        self.name = name.upper()
        self.valid = False
        self.version = version
        self.randSeed = 114514

    @abstractmethod
    def dump(self, filename):
        return False

    @abstractmethod
    def load(self, filename):
        return False

    @abstractmethod
    def check(self):
        return False

    @abstractmethod
    def gen(self, seed: int = 114514):
        self.randSeed = seed
        return seed

    def get_seed(self):
        return self.randSeed
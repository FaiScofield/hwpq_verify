'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : module_reg_core.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-11
Description : 
LastEditTime: 2025-07-11
'''

from abc import ABC, abstractmethod

class ModuleRegisterCore(ABC):
    def __init__(self, name: str, platform: str = 'RK3572'):
        self.name = name.upper()
        self.platform = platform
        self.valid = False

    @abstractmethod
    def dump(self, filename):
        return False

    @abstractmethod
    def load(self, filename):
        return False

    @abstractmethod
    def check(self):
        return False
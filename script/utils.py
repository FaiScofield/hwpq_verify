"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : setup_logger.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-10
Description :
LastEditTime: 2025-07-31
"""

import os
import sys
import logging
import subprocess
import random
import time
import json
import re
import numpy as np
from enum import Enum
from _ctypes import PyObj_FromPtr


class IMG_FMT(Enum):
    ## idx, name, frame_size_ratio
    RGB = (0, "rgb24", 3)
    RGBA = (1, "rgba32", 4)
    RGB_PLANAR = (2, "rgb_planar", 3)
    YUV444P = (3, "yu24", 3)
    YUV444SP = (4, "nv24", 3)
    YUV444I = (5, "yuv444i", 3)
    YUV422P = (6, "yu16", 2)
    YUV422SP = (7, "nv16", 2)
    YUV420P = (8, "yu12", 1.5)
    YUV420SP = (9, "nv12", 1.5)

    RGB_101010LSB = (10, "rgb101010l", 3 * 2)
    RGB_PLANAR10LSB = (12, "rgb10l_planar", 3 * 2)
    YUV444P_10LSB = (13, "yuv444p10l", 3 * 2)
    YUV444SP_10LSB = (14, "yuv444sp10l", 3 * 2)
    YUV444I_10LSB = (15, "yuv444i10l", 3 * 2)
    YUV422P_10LSB = (16, "yuv422p10l", 2 * 2)
    YUV422SP_10LSB = (17, "yuv422sp10l", 2 * 2)
    YUV420P_10LSB = (18, "yuv420p10l", 1.5 * 2)
    YUV420SP_10LSB = (19, "yuv420sp10l", 1.5 * 2)

    RGB_10PACKED = (20, "rgb10pack", 3 / 4 * 5)
    RGBA_1010102 = (21, "rgba1010102", 4)
    RGB_PLANAR10PACKED = (22, "rgb10pack_planar", 3 / 4 * 5)
    YUV444P_10PACKED = (23, "yuv444p10pack", 3 / 4 * 5)
    YUV444SP_10PACKED = (24, "nv30", 3 / 4 * 5)
    YUV444I_10PACKED = (25, "yuv444i10pack", 3 / 4 * 5)
    YUV422P_10PACKED = (26, "yuv422p10pack", 2 / 4 * 5)
    YUV422SP_10PACKED = (27, "nv20", 2 / 4 * 5)
    YUV420P_10PACKED = (28, "yuv420p10pack", 1.5 / 4 * 5)
    YUV420SP_10PACKED = (29, "nv15", 1.5 / 4 * 5)

    @classmethod
    def _init_cache(cls):
        cls._int_to_enum = {ele.value[0]: ele for ele in cls}
        cls._name_to_enum = {ele.value[1]: ele for ele in cls}

    @classmethod
    def from_int(cls, value: int):
        if not hasattr(cls, '_int_to_enum'):
            cls._init_cache()
        return cls._int_to_enum[value]

    @classmethod
    def from_name(cls, name: str):
        if not hasattr(cls, '_name_to_enum'):
            cls._init_cache()
        return cls._name_to_enum[name]



## set encoding to utf-8 to support ✅ & ❌
if not sys.stdout.encoding or sys.stdout.encoding.upper() != 'UTF-8':
    sys.stdout.reconfigure(encoding='utf-8')

## basic config
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] %(levelname)-8s: %(message)s",
    datefmt="%m/%d %H:%M:%S",
    encoding='utf-8',
)

g_plain_formatter = logging.Formatter("[%(asctime)s] [%(name)s] %(levelname)-8s: %(message)s", datefmt="%m/%d %H:%M:%S")


def add_file_handler(logger, output):
    if output is not None:
        if output.endswith(".txt") or output.endswith(".log"):
            filename = output
        else:
            filename = os.path.join(output, "log.txt")
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler) and handler.name == os.fspath(output):
                return logger

        fh = logging.FileHandler(filename, mode="a", encoding='utf-8')  # set encoding to utf-8 to support ✅ & ❌
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(g_plain_formatter)
        logger.addHandler(fh)


def setup_logger(name: str = None, output: str = None, loglevel: str = "DEBUG"):
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)

    # stdout logging: master only
    # if not logger.hasHandlers():
    #     ch = logging.StreamHandler(stream=sys.stdout)
    #     ch.setFormatter(g_plain_formatter)
    #     logger.addHandler(ch)

    # file logging: all workers
    add_file_handler(logger, output)
    return logger


def run_cmd(cmd, showOutput=True, logger: logging.Logger = None):
    # return os.system(cmd)
    if logger is not None:
        logger.info('cmd to run: %s' % cmd)
    else:
        logging.info('cmd to run: %s' % cmd)

    if showOutput:
        ret = subprocess.call(cmd, shell=True)
    else:
        r = os.popen(cmd)
        text = r.read()
        r.close()
        ret = 0
    return ret


def gen_random_frame(size, seed=None, filename=""):
    if seed is None:
        seed = int(time.time())

    np.random.seed(seed)
    data = np.random.randint(0, 255, (1, size), dtype=np.uint8)

    if filename != "":
        data.tofile(filename)
        logging.info(f'saved random frame data(size={size}) to: {filename}')

    return seed


def clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)

def clip(value, min_value, max_value):
    return min(max(value, min_value), max_value)

## using this by `json.dump(data, fp, cls=CompactArrayEncoder)` to dump json array in a single line
class NoIndent(object):
    """Value wrapper."""

    def __init__(self, value):
        self.value = value


class CompactArrayEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))

    def __init__(self, **kwargs):
        # Save copy of any keyword argument values needed for use here.
        self.__sort_keys = kwargs.get('sort_keys', None)
        super(CompactArrayEncoder, self).__init__(**kwargs)

    def default(self, obj):
        return (
            self.FORMAT_SPEC.format(id(obj))
            if isinstance(obj, NoIndent)
            else super(CompactArrayEncoder, self).default(obj)
        )

    def encode(self, obj):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super(CompactArrayEncoder, self).encode(obj)  # Default JSON.

        # Replace any marked-up object ids in the JSON repr with the
        # value returned from the json.dumps() of the corresponding
        # wrapped Python object.
        for match in self.regex.finditer(json_repr):
            # see https://stackoverflow.com/a/15012814/355230
            id = int(match.group(1))
            no_indent = PyObj_FromPtr(id)
            json_obj_repr = json.dumps(no_indent.value, sort_keys=self.__sort_keys)

            # Replace the matched id string with json formatted representation
            # of the corresponding Python object.
            json_repr = json_repr.replace('"{}"'.format(format_spec.format(id)), json_obj_repr)

        return json_repr

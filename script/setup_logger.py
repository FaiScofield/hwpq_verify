"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : setup_logger.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-10
Description : 
LastEditTime: 2025-07-10
"""

import os
import sys
import logging

## set encoding to utf-8 to support ✅ & ❌
if not sys.stdout.encoding or sys.stdout.encoding.upper() != 'UTF-8':
    sys.stdout.reconfigure(encoding='utf-8')

## basic config
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="[%(asctime)s] [%(name)s] %(levelname)-8s: %(message)s",
    datefmt="%m/%d %H:%M:%S",
    encoding='utf-8'
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

        fh = logging.FileHandler(filename, mode="a", encoding='utf-8') # set encoding to utf-8 to support ✅ & ❌
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

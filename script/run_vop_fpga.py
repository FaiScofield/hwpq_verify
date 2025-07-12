"""
Copyright   : Copyright (c) by Rockchip. All right reserved.
FilePath    : run_vop_fpga.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description :
LastEditTime: 2025-07-11
"""

import os
import json
import argparse
import platform
import sys
import re
import random

# import crcmod
import filecmp
import numpy as np
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.normpath(os.path.dirname(__file__)))
from config_def.module_config_cfa import CfaConfig
from config_def.module_config_sharp_lite import SharpLiteConfig
from utils import *

logger = setup_logger(name="run_vop_fpga")


def parse_common_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--module", required=True, help="module name (sharp, acm, dci, csc, ...)")
    parser.add_argument("-e", "--exe", default="", help="module sim_exe file path")
    parser.add_argument("-r", "--root", default="", help="the root dir for data saving")
    parser.add_argument("-p", "--platform", default="RK3572", help="RK3572/RK3576")
    parser.add_argument("-in", "--input_num", default=0, help="generate random input frame number")
    parser.add_argument(
        "-is", "--input_seed", default=603893, help="random seed for generating input frames, used when input_num > 0"
    )
    parser.add_argument("-if", "--input_fmt", default=0, help="input format, 0: YUV444SP, 1: RGBA")
    parser.add_argument("-iw", "--input_wid", default=0, help="used when input_num > 0")
    parser.add_argument("-ih", "--input_hgt", default=0, help="used when input_num > 0")
    parser.add_argument("-cn", "--config_num", default=0, help="generate random config number")
    parser.add_argument(
        "-cs", "--config_seed", default=114514, help="random seed for generating configs, used when config_num > 0"
    )
    args = parser.parse_args(args)
    return args, parser


def run_sharp_lite(args):
    NB_REG_PER_FRAME = 14

    ## set root dir & exe path
    root_dir = args.root if args.root != "" else "//172.16.4.246/vop/RKCFA/batch_sim/sim_check_fpga_rk3572_sharp_lite/"
    exe = os.path.normpath(
        args.exe if args.exe != "" else "G:/Codes/RkVopAlgos/pub_lib/RkSharpLiteSim/AMD64/bin/sharp_lite_sim_exe.exe"
    )

    ## set log file
    time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = os.path.join(root_dir, f"{time_str}_run_fpga_sharp_lite.log")
    add_file_handler(logger, log_file)

    platform = args.platform
    nb_input = int(args.input_num)
    nb_config = int(args.config_num)
    input_seed = int(args.input_seed)
    config_seed = int(args.config_seed)
    img_fmt = int(args.input_fmt)
    img_wid = int(args.input_wid)
    img_hgt = int(args.input_hgt)
    logger.info(f"Set root_dir: {root_dir}")
    logger.info(f"Set platform: {platform}")
    logger.info(f"Set input_num: {nb_input}, config_num: {nb_config}")
    if nb_input > 0:
        logger.info(f"Set input seed: {input_seed}, image size: {img_wid}x{img_hgt}, format: {img_fmt}")
    if nb_config > 0:
        logger.info(f"Set config seed: {config_seed}")

    ## mkdir
    input_dir = os.path.join(root_dir, "input")
    output_dir = os.path.join(root_dir, "output")
    config_dir = os.path.join(root_dir, "config")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)
    if not os.access(root_dir, os.W_OK):
        logger.error(f"root_dir {root_dir} is not writable, please check!")
        exit(-1)
    if not os.access(exe, os.X_OK):
        logger.error(f"sim_exe {exe} is not executable, please check!")
        exit(-1)

    ## generate input data
    input_list = {}  # basename: (width, height)
    if nb_input > 0:
        logger.warning(
            f"about to generate {nb_config} random input frames from seed {input_seed}, existing frames will be overwritten!"
        )
        file_suffix = "yuv444sp.yuv" if img_fmt == 0 else "rgba.bin"
        for i in range(nb_input):
            wid, hgt = img_wid, img_hgt
            if wid * hgt == 0:
                wid = img_wid if img_wid > 0 else random.randint(100, 1000) * 4  # 4 pixel align
                hgt = img_hgt if img_hgt > 0 else random.randint(200, 2000) * 2  # 2 pixel align
                logger.warning(f"gen a random image size({wid}x{hgt}) instead of the input size({img_wid}x{img_hgt}) !")
            input_file = os.path.join(input_dir, f"sharp_lite_input_{wid}x{hgt}_seed_{config_seed + i}_{file_suffix}")
            frame_size = wid * hgt * 3
            gen_random_frame(frame_size, input_seed + i, input_file)
            input_list[os.path.basename(input_file)] = (wid, hgt)
        logger.info(f"generated {len(input_list)} input frames in {input_dir} ...")
    else:
        for basename in os.listdir(input_dir):
            wxh = re.findall(r"(\d+)x(\d+)", basename)
            if len(wxh) >= 1:
                input_list[basename] = (wxh[0][0], wxh[0][1])
            else:
                logger.warning(
                    f"ignore file {basename} in input_dir, not match the pattern of '<W>x<H>' in the filename!"
                )
        logger.info(f"count {len(input_list)} input frames in {input_dir} ...")
    if len(input_list) == 0:
        logger.error(f"no input frames in {input_dir}, please check!")
        exit(-1)

    ## generate random cfg
    config_list = []  # basename
    config_handler = SharpLiteConfig()
    if nb_config > 0:
        logger.warning(
            f"about to generate {nb_config} random configs from seed {config_seed}, existing configs will be overwritten!"
        )
        for i in range(nb_config):
            config_file = os.path.join(config_dir, f"sharp_lite_cfg_seed_{config_seed + i}.json")
            config_handler.gen(config_seed + i)
            config_handler.dump(config_file)
            config_list.append(os.path.basename(config_file))
        logger.info(f"generated {len(config_list)} config files in {config_dir} ...")
    else:
        config_list = os.listdir(config_dir)
        logger.info(f"count {len(config_list)} config files in {config_dir} ...")
    if len(config_list) == 0:
        logger.error(f"no input configs in {config_dir}, please check!")
        exit(-1)

    ## run command & get CRC/Reg result
    exe_output_reg_file = os.path.join(output_dir, "sharp_lite_regs.bin")
    run_cmd(f"chmod +x {exe}", False, logger)
    for input_name, (wid, hgt) in input_list.items():
        input_path = os.path.join(input_dir, input_name)
        final_reg_file = os.path.join(
            output_dir, f"sharp_lite_reg_from_input_{input_name.split('.')[0]}_config_num_{len(config_list)}.bin"
        )
        final_crc_file = os.path.join(
            output_dir, f"sharp_lite_crc_from_input_{input_name.split('.')[0]}_config_num_{len(config_list)}.dat"
        )

        # removed the old regs binary file for each input frame
        run_cmd(f"rm {exe_output_reg_file}", False, logger)
        logger.warning(f"removed the old regs binary file: {exe_output_reg_file} !")

        for config in config_list:
            config_path = os.path.join(config_dir, config)
            # config_handler.load(config_path)
            # seed = config_handler.randSeed
            # suffix = f"_seed_{seed}"

            try:
                # run command
                cmd_str = (
                    exe
                    + f" -i {input_path} -o {output_dir} -l {output_dir} -c {config_path} -r {final_crc_file} -w {wid} -g {hgt}"
                )
                ret = run_cmd(cmd_str, False, logger)
                if ret != 0:
                    raise Exception("run sim_exe failed for intput={input_name}, config={config}!")
            except:
                logger.error(f"run sim_exe failed for intput={input_name}, config={config}!")
                break

        # move output regs file to output_dir
        exe_reg_file_size = os.path.getsize(exe_output_reg_file)
        theorical_file_size = NB_REG_PER_FRAME * 4 * len(config_list)
        if exe_reg_file_size == theorical_file_size:
            cmd_str = f"cp {exe_output_reg_file} {final_reg_file}"
            run_cmd(cmd_str, False, logger)
            logger.info(f"✅ got a register binary file: {final_reg_file}")
        else:
            logger.error(
                f"❌ register file size = {exe_reg_file_size} != {theorical_file_size} theorical size, please check!"
            )
            exit(-1)

    logger.info(f"run sim_exe done. check output data in {output_dir}")


if __name__ == "__main__":
    args, parser = parse_common_args(sys.argv[1:])
    if len(sys.argv) < 3:
        parser.print_help()
        exit(-1)

    name = args.module.lower()
    if "sharp" in name:
        run_sharp_lite(args)
    else:
        print(f"Unsupported module for now: {name}")
        exit(-1)

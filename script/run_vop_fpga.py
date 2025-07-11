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

# import crcmod
import filecmp
import numpy as np
from datetime import datetime
from typing import Dict, List
from config_def.module_config_cfa import CfaConfig
from config_def.module_config_sharp_lite import SharpLiteConfig
from utils import *

logger = setup_logger(name="run_vop_fpga")


def parse_common_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exe", default="", help="module sim_exe file path")
    parser.add_argument("-r", "--root", default="", help="the root dir for data saving")
    parser.add_argument("-p", "--platform", default="RK3572", help="RK3572/RK3576")
    parser.add_argument("-ni", "--nb_input", default=0, help="generate random input frame number")
    parser.add_argument("-nc", "--nb_config", default=0, help="generate random config number")
    parser.add_argument("-si", "--seed_input", default=603893, help="random seed for generating input frames")
    parser.add_argument("-sc", "--seed_config", default=114514, help="random seed for generating configs")
    parser.add_argument("-w", "--img_w", default=3840)
    parser.add_argument("-g", "--img_h", default=2160)

    parser.add_argument("-ys", "--yuv_seed", default=0)
    parser.add_argument("-yn", "--yuv_num", default=2)
    # parser.add_argument("-rgb_mode", "--rgb_mode", default=0)
    args = parser.parse_args(args)
    return args


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
    nb_input = int(args.nb_input)
    nb_config = int(args.nb_config)
    input_seed = int(args.seed_input)
    config_seed = int(args.seed_config)
    img_w = int(args.img_w)
    img_h = int(args.img_h)
    # rgb_mode = int(args.rgb_mode)
    logger.info(f"Set root_dir: {root_dir}")
    logger.info(f"Set platform: {platform}")
    logger.info(f"Set nb_input: {nb_input}, input_seed: {input_seed}")
    logger.info(f"Set nb_config: {nb_config}, config_seed: {config_seed}")
    logger.info(f"Set image_size: {img_w}x{img_h}")

    ## mkdir
    input_dir = os.path.join(root_dir, "input")
    output_dir = os.path.join(root_dir, "output")
    config_dir = os.path.join(root_dir, "config")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)

    # fpga_dir = "%s/%s_fpga_dir/" % (root_dir, time_str)
    # if not (os.path.exists(fpga_dir)):
    #     os.mkdir(fpga_dir)
    # temp_path = "./temp_dir_%s/" % (time_str)
    # if not (os.path.exists(temp_path)):
    #     os.mkdir(temp_path)

    ## generate input data
    if nb_input > 0:
        logger.warning(
            f"about to generate {nb_config} random configs from seed {config_seed}, existing configs will be overwritten!"
        )
        input_list = {}
        for i in range(nb_input):
            input_file = os.path.join(
                input_dir, f"sharp_lite_input_{img_w}x{img_h}_seed_{config_seed + i}_yuv444sp.yuv"
            )
            # TODO
            input_list[input_file] = (img_w, img_h)
    else:
        input_list = {}
        for basename in os.listdir(input_dir):
            input_list[basename] = (img_w, img_h)
    if len(input_list) == 0:
        logger.error(f"no input frames in {input_dir}, please check!")
        exit(-1)
    else:
        logger.info(f"count {len(input_list)} input frames in {input_dir} ...")

    ## generate random cfg
    config_handler = SharpLiteConfig()
    if nb_config > 0:
        logger.warning(
            f"about to generate {nb_config} random configs from seed {config_seed}, existing configs will be overwritten!"
        )
        for i in range(nb_config):
            config_file = os.path.join(config_dir, f"sharp_lite_cfg_seed_{config_seed + i}.json")
            config_handler.gen(config_seed + i)
            config_handler.dump(config_file)
    config_list = os.listdir(config_dir)
    if len(config_list) == 0:
        logger.error(f"no input configs in {config_dir}, please check!")
        exit(-1)
    else:
        logger.info(f"count {len(config_list)} config files in {config_dir} ...")

    ## run command & get CRC/Reg result
    exe_output_reg_file = os.path.join(output_dir, "sharp_lite_regs.bin")
    run_cmd(f"chmod +x {exe}", False, logger)
    run_cmd(f"rm {exe_output_reg_file}", False, logger)
    logger.warning(f"removed the old regs binary file: {exe_output_reg_file} !")

    for input_name, (wid, hgt) in input_list.items():
        input_path = os.path.join(input_dir, input_name)
        final_reg_file = os.path.join(output_dir, f"sharp_lite_reg_from_input_{input_name}_config_num_{len(config_list)}.bin")
        final_crc_file = os.path.join(output_dir, f"sharp_lite_crc_from_input_{input_name}_config_num_{len(config_list)}.dat")
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
        theorical_file_size =  NB_REG_PER_FRAME * 4 * len(config_list)
        if exe_reg_file_size == theorical_file_size:
            cmd_str = f"cp {exe_output_reg_file} {final_reg_file}"
            run_cmd(cmd_str, False, logger)
        else:
            logger.error(f"register file size = {exe_reg_file_size} != {theorical_file_size} theorical size, please check!")
            exit(-1)

    logger.info(f"run sim_exe done. check output data in {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_vop_fpga.py <module_name> (cfa, sharp_lite, acm, dci, csc ...)")
        exit(1)

    name = sys.argv[1].lower()
    args = parse_common_args(sys.argv[2:])
    if name == "sharp_lite":
        run_sharp_lite(args)
    else:
        print(f"Unsupported module: {name}")
        exit(-1)

"""
Copyright   : Copyright (c) by Rockchip. All right reserved.
FilePath    : run_rga_fpga.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-11
Description :
LastEditTime: 2025-07-11
"""

import os
import sys
# import crcmod
import filecmp
from datetime import datetime
from typing import Dict, List
from config_def.module_config_cfa import CfaConfig
from utils import *

logger = setup_logger(name="check_cfa_dither")


def main(args):
    ## set data root dir & exe path
    root_dir = "//172.16.4.246/vop/RKCFA/batch_sim/sim_check_sdk0.13.1_vs_cmodel1.0"
    os.makedirs(root_dir, exist_ok=True)
    input_dir = os.path.join(root_dir, "input")
    output_dir = os.path.join(root_dir, "output")
    config_dir = os.path.join(root_dir, "config")
    b_output_overwrite = True
    exe0 = os.path.normpath(
        "G:/Codes/RkYuvAlgos_update/project/vc/build/rkcfa/Release/rkcfa_sim_exe.exe"
    )  # exe from librkcfa.so SDK
    exe1 = os.path.normpath(
        "G:/Codes/RkVopAlgos/pub_lib/RkCfaDitherSim/AMD64/bin/cfa_dither_sim_exe.exe"
    )  # exe from IC cmodel

    ## set log file
    time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = os.path.join(root_dir, f"{time_str}_run_fpga_cfa.log")
    add_file_handler(logger, log_file)

    input_list = {
        ## basename, w, h
        "cfa_src_1200x825_rgba.rgb": (1200, 825),
        "cfa_src_2480x1860_rgba.rgb": (2480, 1680),
        "input_720x480_rgba_full_25frames.rgb": (720, 480),
    }
    config_list = os.listdir(config_dir)
    logger.info(f"Set data root dir to: {root_dir}")
    logger.info(f"Read {len(config_list)} config files from {config_dir}")

    config_handler = CfaConfig()
    # crc_handler = crcmod.mkCrcFun(0x104C11DB7, initCrc=0xFFFFFFFF, xorOut=0xFFFFFFFF)

    ## run command & get CRC result
    check_pass = 0
    fail_map: Dict[int, List[str]] = {}
    run_cmd(f"chmod +x {exe0}")
    run_cmd(f"chmod +x {exe1}")
    for input_name, (wid, hgt) in input_list.items():
        input_path = os.path.join(input_dir, input_name)
        for config in config_list:
            ret0, ret1 = 0, 0
            config_path = os.path.join(config_dir, config)
            config_handler.load(config_path)

            seed = config_handler.randSeed
            suffix = "" if b_output_overwrite else f"_seed_{seed}"
            output_file0 = os.path.join(output_dir, f"rkcfa_test_out_Y8{suffix}.yuv")
            output_file1 = os.path.join(output_dir, f"cfa_dither_test_out_Y8{suffix}.yuv")

            cmd0 = exe0 + f" -i={input_path} -o={output_file0} -j={config_path} -sw={wid} -sh={hgt}"
            ret0 = run_cmd(cmd0, False)

            cmd1 = exe1 + f" -i {input_path} -o {output_file1} -j {config_path} -w {wid} -g {hgt}"
            ret1 = run_cmd(cmd1, False)
            if ret0 != 0 or ret1 != 0:
                logger.error(f"Error happend! ret of cmd0/cmd1: {ret0}/{ret1}")
                logger.error(f"Error input: {input_path}")
                logger.error(f"Error config: {config}")
                fail_map.setdefault(seed, []).append(input_name)
                return
            if filecmp.cmp(output_file0, output_file1, shallow=False):
                check_pass += 1
                logger.info(
                    f"✅ Binary equal when seed = {seed}, input = {input_name} ... pass/fail num total: {check_pass}/{len(fail_map)}"
                )
            else:
                logger.error(
                    f"❌ Binary not equal when seed = {seed}, input = {input_name}! pass/fail num total: {check_pass}/{len(fail_map)}"
                )
                fail_map.setdefault(seed, []).append(input_name)
                # return

    logger.info(f"Check done. pass/fail num total: {check_pass} ✅ / {len(fail_map)} ❌")
    for seed, input_names in fail_map:
        logger.error(f"Failed seed-inputs case seed {seed}: {input_names}")


if __name__ == "__main__":
    main(sys.argv)

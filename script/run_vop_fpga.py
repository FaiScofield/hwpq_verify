'''
Copyright   : Copyright (c) by Rockchip. All right reserved.
FilePath    : run_vop_fpga.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description : 
LastEditTime: 2025-07-10
'''

import os
import json
import argparse
import sys
import time
# import crcmod
import filecmp
import subprocess
import numpy as np
from datetime import datetime
from typing import Dict, List
from config_def.module_config_cfa import CfaConfig
from setup_logger import setup_logger, add_file_handler

logger = setup_logger(name='run_vop_fpga')

def main(args):
    ## set data root dir & exe path
    root_dir = "//172.16.4.246/vop/RKCFA/batch_sim/sim_check_sdk0.13.1_vs_cmodel1.0"
    input_dir  = os.path.join(root_dir, 'input')
    output_dir = os.path.join(root_dir, 'output')
    config_dir = os.path.join(root_dir, 'config')
    b_output_overwrite = True
    exe0 = os.path.normpath('G:/Codes/RkYuvAlgos_update/project/vc/build/rkcfa/Release/rkcfa_sim_exe.exe')  # exe from librkcfa.so SDK
    exe1 = os.path.normpath('G:/Codes/RkVopAlgos/pub_lib/RkCfaDitherSim/AMD64/bin/cfa_dither_sim_exe.exe') # exe from IC cmodel

    ## set log file
    time_str = datetime.now().strftime('%Y%m%d%H%M%S')
    log_file = os.path.join(output_dir, f'{time_str}_run_vop_fpga.log')
    add_file_handler(logger, log_file)

    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-exe", "--exe_path", default="./exe/RkVopSimExe_dci_rand_run_v2771.exe")
    parser.add_argument("-dir", "--proc_dir", default="./dst_dir/")
    parser.add_argument("-js", "--cfg_seed", default=0)
    parser.add_argument("-jn", "--cfg_num", default=5)
    parser.add_argument("-ys", "--yuv_seed", default=0)
    parser.add_argument("-yn", "--yuv_num", default=2)
    parser.add_argument("-iw", "--img_w", default=3840)
    parser.add_argument("-ih", "--img_h", default=2160)
    # parser.add_argument("-rgb_mode", "--rgb_mode", default=0)
    args = parser.parse_args()

    exe_path        = args.exe_path
    proc_dir        = args.proc_dir
    cfg_seed        = int(args.cfg_seed)
    cfg_num         = int(args.cfg_num)
    yuv_seed        = int(args.yuv_seed)
    yuv_num         = int(args.yuv_num)
    img_w           = int(args.img_w)
    img_h           = int(args.img_h)
    # rgb_mode        = int(args.rgb_mode)

    timestamp = time.time()
    time_tuple = time.localtime(timestamp)
    time_str = time.strftime("%Y%m%d%H%M%S", time_tuple)

    if not(os.path.exists(proc_dir)):
        os.mkdir(proc_dir)

    fpga_dir = "%s/%s_fpga_dir/" % (proc_dir, time_str)
    if not(os.path.exists(fpga_dir)):
        os.mkdir(fpga_dir)
    yuv_path        = "%s/%s_yuv_dir/" % (proc_dir, time_str)
    if not(os.path.exists(yuv_path)):
        os.makedirs(yuv_path)
    cfg_path        = "%s/%s_cfg_dir/" % (proc_dir, time_str)
    if not(os.path.exists(cfg_path)):
        os.makedirs(cfg_path)
    temp_path       = "./temp_dir_%s/" % (time_str)
    if not(os.path.exists(temp_path)):
        os.mkdir(temp_path)

    json_ref_path = "./dci_interp_ref.json"
    with open(json_ref_path, "r") as f_in:
        json_ref_root = json.load(f_in)

    play_list_ref_path = "./dci_interp_fpga_cfg.json"
    with open(play_list_ref_path, "r") as f_in:
        play_list_ref_root = json.load(f_in)

    play_list_ref_root["dci_hw_lut_path"]   = "/dci_interp/dci_hw_lut_s%d_n%d.dat" % (cfg_seed, cfg_num)
    play_list_ref_root["dci_reg_path"]      = "/dci_interp/dci_reg_list_s%d_n%d.dat" % (cfg_seed, cfg_num)
    play_list_ref_root["dci_crc_path"]      = "/dci_interp/dci_crc_list_s%d_n%d.dat" % (cfg_seed, cfg_num)
    play_list_ref_root["yuv_seed"]  = yuv_seed
    play_list_ref_root["cfg_seed"]  = cfg_seed
    play_list_ref_root["yuv_num"]   = yuv_num
    play_list_ref_root["cfg_num"]   = cfg_num
    # play_list_ref_root["rgb_mode"]   = rgb_mode

    play_list_dst_path = "%s/dci_interp_fpga_cfg.json" % (fpga_dir)
    with open(play_list_dst_path, "w") as f_out:
        json.dump(play_list_ref_root, f_out, indent=4, separators=(", ", ": "))

    w_i = img_w
    h_i = img_h
    w_o = img_w
    h_o = img_h

    ## generate yuv
    for yuv_idx in range(yuv_seed, yuv_seed + yuv_num, 1):
        yuv_name_pack = "rand_seed_%08d_%dx%d_%dx%d_yuv444p10le.yuv" % (yuv_idx, w_i, h_i, w_o, h_o)
        yuv_name = "rand_seed_%08d_%dx%d_%dx%d_yuv444p10le_unpack.yuv" % (yuv_idx, w_i, h_i, w_o, h_o)
        cmd = "./exe/generate_vop_rand.exe %s %d %d %d 0 0" % (fpga_dir, yuv_idx, w_i, h_i)
        run_cmd(cmd)
        cmd = "./exe/convert_10bit_pack_to_10bit_unpack.exe %s/%s %s/%s %d %d 3" % (fpga_dir, yuv_name_pack, yuv_path, yuv_name, w_i, h_i)
        run_cmd(cmd)

    ## generate rand cfg
    for cfg_idx in range(cfg_seed, cfg_seed + cfg_num, 1):
        logger.info("yuv_idx: %d, cfg_idx: %d" % (yuv_idx, cfg_idx))

        json_ref_root["pq_tuning_param"]["dci"]["s_vop_dci_interp_params"]["s_vop_dci_ctrl"]["i_vop_srand_seed"] = cfg_idx
        rand_json_name = "%s/rand_cfg_%d.json" % (cfg_path, cfg_idx)
        # run_cmd(rand_json_name)
        with open(rand_json_name, "w") as f_out:
            json.dump(json_ref_root, f_out, indent=4, separators=(", ", ": "))
    '''


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
    run_cmd(f'chmod +x {exe0}')
    run_cmd(f'chmod +x {exe1}')
    for input_name, (wid, hgt) in input_list.items():
        input_path = os.path.join(input_dir, input_name)
        for config in config_list:
            ret0, ret1 = 0, 0
            config_path = os.path.join(config_dir, config)
            config_handler.load(config_path)

            seed = config_handler.randSeed
            suffix = '' if b_output_overwrite else f'_seed_{seed}'
            output_file0 = os.path.join(output_dir, f'rkcfa_test_out_Y8{suffix}.yuv')
            output_file1 = os.path.join(output_dir, f'cfa_dither_test_out_Y8{suffix}.yuv')

            cmd0 = exe0 + f' -i={input_path} -o={output_file0} -j={config_path} -sw={wid} -sh={hgt}'
            ret0 = run_cmd(cmd0, False)

            cmd1 = exe1 + f' -i {input_path} -o {output_file1} -j {config_path} -w {wid} -g {hgt}'
            ret1 = run_cmd(cmd1, False)
            if ret0 != 0 or ret1 != 0:
                logger.error(f"Error happend! ret of cmd0/cmd1: {ret0}/{ret1}")
                logger.error(f"Error input: {input_path}")
                logger.error(f"Error config: {config}")
                fail_map.setdefault(seed, []).append(input_name)
                return
            if filecmp.cmp(output_file0, output_file1, shallow=False):
                logger.info(f"✅ Binary equal when seed = {seed}, input = {input_name} ...")
                check_pass += 1
            else:
                logger.error(f"❌ Binary not equal when seed = {seed}, input = {input_name}!")
                fail_map.setdefault(seed, []).append(input_name)
                # return
    logger.info(f"Check done. ✅ pass num: {check_pass}, ❌ fail num: {len(fail_map)}")
    for seed, input_names in fail_map:
        logger.error(f"Failed seed-inputs case seed {seed}: {input_names}")


def run_cmd(cmd, showOutput=True):
    # return os.system(cmd)
    logger.info('cmd to run: %s' % cmd)
    if showOutput:
        ret = subprocess.call(cmd, shell=True)
    else:
        r = os.popen(cmd)
        text = r.read()
        r.close()
        ret = 0
    return ret


if __name__ == "__main__":
    main(sys.argv)
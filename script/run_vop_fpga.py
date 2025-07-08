'''
Copyright   : Copyright (c) by Rockchip. All right reserved.
FilePath    : run_vop_fpga.py
Author      : vance.wu@rock-chips.com
Date        : 2025-07-07
Description : 
LastEditTime: 2025-07-08
'''

import os
import json
import argparse
import sys
import time
from config_def.module_config_cfa import CfaConfig

def main(args):
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
        print("yuv_idx: %d, cfg_idx: %d" % (yuv_idx, cfg_idx))

        json_ref_root["pq_tuning_param"]["dci"]["s_vop_dci_interp_params"]["s_vop_dci_ctrl"]["i_vop_srand_seed"] = cfg_idx
        rand_json_name = "%s/rand_cfg_%d.json" % (cfg_path, cfg_idx)
        # run_cmd(rand_json_name)
        with open(rand_json_name, "w") as f_out:
            json.dump(json_ref_root, f_out, indent=4, separators=(", ", ": "))
    '''

    script_dir = os.path.dirname(os.path.realpath(__file__))
    exe0 = os.path.normpath(os.path.join(script_dir, '../bin/rkcfa_sim_exe.exe'))  # exe from librkcfa.so SDK
    exe1 = os.path.normpath(os.path.join(script_dir, '../bin/cfa_dither_sim_exe.exe')) # exe from IC cmodel
    run_cmd(f'chmod +x {exe0}')
    run_cmd(f'chmod +x {exe1}')

    input_dir = 'V:/RKCFA/batch_sim/sim_check_crc_v0.13.0.4736_vs_v0.7/input/'
    output_dir = 'V:/RKCFA/batch_sim/sim_check_crc_v0.13.0.4736_vs_v0.7/output/'
    config_dir = 'V:/RKCFA/batch_sim/sim_check_crc_v0.13.0.4736_vs_v0.7/config/'
    input_list = {
        ## basename, w, h
        "cfa_src_1200x825_rgba.rgb": (1200, 825),
        "cfa_src_2480x1860_rgba.rgb": (2480, 1680),
        "input_720x480_rgba_full_25frames.rgb": (720, 480),
        }
    config_list = os.listdir(config_dir)

    ## run command & get CRC result
    for input_name, (wid, hgt) in input_list.items():
        input_path = os.path.join(input_dir, input_name)
        for config in config_list:
            config_path = os.path.join(config_dir, config)
            cmd0 = exe0 + f' -i={input_path} -o={output_dir} -j={config_path} -sw={wid} -sh={hgt}'
            cmd1 = exe1 + f' -i {input_path} -o {output_dir} -j {config_path} -w {wid} -g {hgt}'
            # print(f"cmd0: {cmd0}")
            # print(f"cmd0: {cmd1}")
            ret0 = run_cmd(cmd0)
            ret1 = run_cmd(cmd1)
            if ret0 != 0 or ret1 != 0:
                print(f"Error happend! ret of cmd0/cmd1: {ret0}/{ret1}")
                print(f"Error input_path: {input_path}")
                print(f"Error config_path: {config_path}")
                break

def run_cmd(cmd):
    return os.system(cmd)

if __name__ == "__main__":
    main(sys.argv)
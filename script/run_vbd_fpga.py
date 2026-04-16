"""
Copyright   : Copyright (c) by Rockchip. All right reserved.
FilePath    : run_vbd_fpga.py
Author      : vance.wu@rock-chips.com
Date        : 2026-04-15
Description :
LastEditTime: 2026-04-15
"""

import os
import sys
import zlib # crc32
import utils as utl

data_root = "V:/RK_186X/vbd/20260415/"
seq_names = ["099"] # ~250, ~550 group inputs
exe = "G:/Codes/RkVopAlgos/pub_lib/ModelVerify/AMD64/bin/fusion_verify_demo.exe"
version = 5405
pick_step = 30
pick_offset = 1
pick_num = 20

def main(args):

    for seq_name in seq_names:
        input_folder = f"{data_root}/{seq_name}_mesh8x8/"
        otuput_folder = f"{data_root}/group0_3840x2160_yuv420/"
        output_crcfile = f"{otuput_folder}/vbd_group0_3840x2160_yuv420_crc.txt"
        os.makedirs(otuput_folder, exist_ok=True)

        for idx in range(pick_num):
            frm_id = idx * pick_step + pick_offset
            input_file0 = f"{input_folder}/{seq_name}_vbd_input_{frm_id:05d}_0_3840x2160.nv12"
            input_file1 = f"{input_folder}/{seq_name}_vbd_input_{frm_id:05d}_1_3840x2160.nv12"
            input_filem = f"{input_folder}/{seq_name}_vbd_mask_{frm_id:05d}_3840x2160_yuv400.yuv"
            output_file = f"{otuput_folder}/{seq_name}_vbd_out_{frm_id:05d}_3840x2160.nv12"
            if not os.path.exists(input_file0) or not os.path.exists(input_file1) or not os.path.exists(input_filem):
                print(f"Warning: Input files not found for frame {frm_id}, skipping...")
                continue

            # run vbd
            utl.run_cmd(f"{exe} -i {input_file0} -I {input_file1} -m {input_filem} -o {output_file} -O {otuput_folder} --save_tile")

            # copy input tiles & mask file to output folder
            utl.run_cmd(f"mv {otuput_folder}/fusion_input0_3840x2160_yuv420sp-8bit.tile4x4 {otuput_folder}/{seq_name}_vbd_input_{frm_id:05d}_0_3840x2160.tile4x4")
            utl.run_cmd(f"mv {otuput_folder}/fusion_input1_3840x2160_yuv420sp-8bit.tile4x4 {otuput_folder}/{seq_name}_vbd_input_{frm_id:05d}_1_3840x2160.tile4x4")
            utl.run_cmd(f"cp {input_filem} {otuput_folder}/")

            # append crc_val to output_crcfile
            crc_val = utl.calc_crc32(open(output_file,'rb').read())
            with open(output_crcfile, 'a') as f:
                f.write(f"idx_{idx:03d}: frame_{frm_id:05d}, output_crc: 0x{crc_val:08x}\n")

if __name__ == "__main__":
    main(sys.argv)
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
import utils as utl

data_root = "V:/RK_186X/vbd/20260415/"
seq_names = ["098"]  # ~250, ~550 group inputs
vbd_exe = "G:/Codes/RkVopAlgos/pub_lib/ModelVerify/AMD64/bin/fusion_verify_demo.exe"
version = 5435
pick_step = 25
pick_offset = 5
pick_num = 30

# scaling & conversion
zme_exe = "G:/Codes/RkYuvAlgos_update/pub_lib/rkswpq_0.26.0.5423/bin/Windows/amd64/rk_swpq_exe.exe"
org_wid = 3840
org_hgt = 2160
target_wid = 3840
target_hgt = 2160
# target_wid = 1920
# target_hgt = 1088

org_fmt_zme = 2  # 0-nv24, 1-nv16, 2-nv12
tar_fmt_zme = 0  # 0-nv24, 1-nv16, 2-nv12
org_fmt_vbd = 0x9  # 0x4-nv24, 0x7-nv16, 0x9-nv12
tar_fmt_vbd = 0x4  # 0x4-nv24, 0x7-nv16, 0x9-nv12
tar_fmt_name = "nv24"
tile_fmt_name = "yuv444sp-8bit"


def main(args):
    for seq_name in seq_names:
        input_folder = f"{data_root}/{seq_name}_mesh8x8/"

        otuput_folder = f"{data_root}/group3_{target_wid}x{target_hgt}_yuv444/"
        # otuput_folder = f"{data_root}/{seq_name}_mesh8x8_test_out_v{version}/"
        output_crcfile = f"{otuput_folder}/vbd_test_{target_wid}x{target_hgt}_yuv444_crc.txt"
        os.makedirs(otuput_folder, exist_ok=True)

        for idx in range(pick_num):
            frm_id = idx * pick_step + pick_offset
            input_file0 = f"{input_folder}/{seq_name}_vbd_input_{frm_id:05d}_0_3840x2160.nv12"
            input_file1 = f"{input_folder}/{seq_name}_vbd_input_{frm_id:05d}_1_3840x2160.nv12"
            input_filem = f"{input_folder}/{seq_name}_vbd_mask_{frm_id:05d}_3840x2160_yuv400.yuv"
            output_file = f"{otuput_folder}/{seq_name}_vbd_out_{frm_id:05d}_3840x2160.nv12"
            if not os.path.exists(input_file0) or not os.path.exists(input_file1) or not os.path.exists(input_filem):
                print(
                    f"Warning: Input files not found ({os.path.exists(input_file0)}, {os.path.exists(input_file1)}, {os.path.exists(input_filem)}) for frame {frm_id}, skipping"
                )
                continue

            # run zme if necessary
            if org_wid != target_wid or org_hgt != target_hgt or org_fmt_zme != tar_fmt_zme:
                tmp_file0 = f"{otuput_folder}/{seq_name}_vbd_input_{frm_id:05d}_0_{target_wid}x{target_hgt}.{tar_fmt_name}"
                tmp_file1 = f"{otuput_folder}/{seq_name}_vbd_input_{frm_id:05d}_1_{target_wid}x{target_hgt}.{tar_fmt_name}"
                tmp_filem = f"{otuput_folder}/{seq_name}_vbd_mask_{frm_id:05d}_{target_wid}x{target_hgt}_yuv400.yuv"
                output_file = f"{otuput_folder}/{seq_name}_vbd_out_{frm_id:05d}_{target_wid}x{target_hgt}.{tar_fmt_name}"

                com_cmd = f"-f=sim -m=5 -sw={org_wid} -sh={org_hgt} -sc=3 -dw={target_wid} -dh={target_hgt}"
                utl.run_cmd(f"{zme_exe} {com_cmd} -i={input_file0} -sf={org_fmt_zme} -o={tmp_file0} -df={tar_fmt_zme}")
                utl.run_cmd(f"{zme_exe} {com_cmd} -i={input_file1} -sf={org_fmt_zme} -o={tmp_file1} -df={tar_fmt_zme}")
                if org_wid != target_wid or org_hgt != target_hgt:
                    utl.run_cmd(f"{zme_exe} {com_cmd} -i={input_filem} -sf=12 -o={tmp_filem} -df=12")
                else:
                    utl.run_cmd(f"cp {input_filem} {tmp_filem}")

                input_file0 = tmp_file0
                input_file1 = tmp_file1
                input_filem = tmp_filem

            # run vbd
            utl.run_cmd(
                f"{vbd_exe} -i {input_file0} -I {input_file1} -m {input_filem} -o {output_file} -O {otuput_folder} -w {target_wid} -g {target_hgt} -f {tar_fmt_vbd} -F {tar_fmt_vbd} --save_tile"
            )

            # copy input tiles & mask file to output folder
            utl.run_cmd(
                f"mv {otuput_folder}/fusion_input0_{target_wid}x{target_hgt}_{tile_fmt_name}.tile4x4 {otuput_folder}/{seq_name}_vbd_input_{frm_id:05d}_0_{target_wid}x{target_hgt}_{tile_fmt_name}.tile4x4"
            )
            utl.run_cmd(
                f"mv {otuput_folder}/fusion_input1_{target_wid}x{target_hgt}_{tile_fmt_name}.tile4x4 {otuput_folder}/{seq_name}_vbd_input_{frm_id:05d}_1_{target_wid}x{target_hgt}_{tile_fmt_name}.tile4x4"
            )
            utl.run_cmd(f"cp {input_filem} {otuput_folder}/")

            # append crc_val to output_crcfile
            crc_val = utl.calc_crc32(open(output_file, 'rb').read())
            with open(output_crcfile, 'a') as f:
                f.write(f"idx_{idx:03d}: frame_{frm_id:05d}, output_crc: 0x{crc_val:08x}\n")


if __name__ == "__main__":
    main(sys.argv)

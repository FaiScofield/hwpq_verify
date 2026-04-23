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
version = 5449
pick_step = 25
pick_offset = 2
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
tar_fmt_zme = 1  # 0-nv24, 1-nv16, 2-nv12
src_fmt_vbd = 0x7  # 0x4-nv24, 0x7-nv16, 0x9-nv12 (+0x30 for tile)
dst_fmt_vbd = 0x7  # 0x4-nv24, 0x7-nv16, 0x9-nv12
org_fmt_name = "nv12"
tar_fmt_name = "nv16"
tile_fmt_name = "yuv422sp-8bit"


def main(args):
    for seq_name in seq_names:
        input_folder = f"{data_root}/{seq_name}_mesh8x8/"

        output_folder = f"{data_root}/group6_{target_wid}x{target_hgt}_yuv422_fix/"
        output_crcfile = f"{output_folder}/vbd_test_{target_wid}x{target_hgt}_yuv422_crc.txt"
        output_crcfile2 = f"{output_folder}/vbd_test_{target_wid}x{target_hgt}_yuv422_crc_cmodel.txt"
        os.makedirs(output_folder, exist_ok=True)

        for idx in range(pick_num):
            frm_id = idx * pick_step + pick_offset
            input_file0 = f"{input_folder}/{seq_name}_vbd_input_{frm_id:05d}_0_3840x2160.{org_fmt_name}"
            input_file1 = f"{input_folder}/{seq_name}_vbd_input_{frm_id:05d}_1_3840x2160.{org_fmt_name}"
            input_filem = f"{input_folder}/{seq_name}_vbd_mask_{frm_id:05d}_3840x2160_yuv400.yuv"
            output_file = f"{output_folder}/{seq_name}_vbd_out_{frm_id:05d}_3840x2160.{tar_fmt_name}"
            if not os.path.exists(input_file0) or not os.path.exists(input_file1) or not os.path.exists(input_filem):
                print(
                    f"Warning: Input files not found ({os.path.exists(input_file0)}, {os.path.exists(input_file1)}, {os.path.exists(input_filem)}) for frame {frm_id}, skipping"
                )
                continue

            # run zme if necessary
            if org_wid != target_wid or org_hgt != target_hgt or org_fmt_zme != tar_fmt_zme:
                tmp_file0 = (
                    f"{output_folder}/{seq_name}_vbd_input_{frm_id:05d}_0_{target_wid}x{target_hgt}.{tar_fmt_name}"
                )
                tmp_file1 = (
                    f"{output_folder}/{seq_name}_vbd_input_{frm_id:05d}_1_{target_wid}x{target_hgt}.{tar_fmt_name}"
                )
                tmp_filem = f"{output_folder}/{seq_name}_vbd_mask_{frm_id:05d}_{target_wid}x{target_hgt}_yuv400.yuv"
                output_file = (
                    f"{output_folder}/{seq_name}_vbd_out_{frm_id:05d}_{target_wid}x{target_hgt}.{tar_fmt_name}"
                )

                com_cmd = f"-f=sim -m=5 -sw={org_wid} -sh={org_hgt} -sc=3 -dw={target_wid} -dh={target_hgt}"
                utl.run_cmd(f"{zme_exe} {com_cmd} -i={input_file0} -sf={org_fmt_zme} -o={tmp_file0} -df={tar_fmt_zme}", False)
                utl.run_cmd(f"{zme_exe} {com_cmd} -i={input_file1} -sf={org_fmt_zme} -o={tmp_file1} -df={tar_fmt_zme}", False)
                if org_wid != target_wid or org_hgt != target_hgt:
                    utl.run_cmd(f"{zme_exe} {com_cmd} -i={input_filem} -sf=12 -o={tmp_filem} -df=12", False)
                else:
                    utl.run_cmd(f"cp {input_filem} {tmp_filem}", False)

                input_file0 = tmp_file0
                input_file1 = tmp_file1
                input_filem = tmp_filem

            # run vbd
            utl.run_cmd(
                f"{vbd_exe} -i {input_file0} -I {input_file1} -m {input_filem} -o {output_file} -O {output_folder} -w {target_wid} -g {target_hgt} -f {src_fmt_vbd:x} -F {dst_fmt_vbd:x} -c {output_crcfile2} --save_tile", False
            )

            # copy input tiles & mask file to output folder
            utl.run_cmd(
                f"mv {output_folder}/fusion_input0_{target_wid}x{target_hgt}_{tile_fmt_name}.tile4x4 {output_folder}/{seq_name}_vbd_input_{frm_id:05d}_0_{target_wid}x{target_hgt}_{tile_fmt_name}.tile4x4", False
            )
            utl.run_cmd(
                f"mv {output_folder}/fusion_input1_{target_wid}x{target_hgt}_{tile_fmt_name}.tile4x4 {output_folder}/{seq_name}_vbd_input_{frm_id:05d}_1_{target_wid}x{target_hgt}_{tile_fmt_name}.tile4x4", False
            )
            utl.run_cmd(f"cp {input_filem} {output_folder}/", False)

            # append crc_val to output_crcfile
            crc_src0 = utl.calc_crc32(open(input_file0, 'rb').read())
            crc_src1 = utl.calc_crc32(open(input_file1, 'rb').read())
            crc_mask = utl.calc_crc32(open(input_filem, 'rb').read())
            crc_dst = utl.calc_crc32(open(output_file, 'rb').read())
            with open(output_crcfile, 'a') as f:
                f.write(
                    f"idx_{idx:03d}: frame_{frm_id:05d}, {'raster' if src_fmt_vbd < 0x30 else 'tile'} input crc: 0x{crc_src0:08x}, 0x{crc_src1:08x}, 0x{crc_mask:08x}; {'raster' if dst_fmt_vbd < 0x30 else 'tile'} output crc: 0x{crc_dst:08x}\n"
                )


if __name__ == "__main__":
    main(sys.argv)

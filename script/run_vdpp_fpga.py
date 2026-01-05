"""
Copyright   : Copyright (c) by Rockchip. All right reserved.
FilePath    : run_vdpp_fpga.py
Author      : vance.wu@rock-chips.com
Date        : 2026-01-05
Description :
LastEditTime: 2025-01-05
"""

import os
import sys
import utils as utl

b_test_vdpp = True
b_test_hwpq = False
dev_data_path = "/data/vdpp/"
dev_output_folder = f"{dev_data_path}/rk3538_0105"
host_root_dir = "//172.16.4.246/vop/hwpq_verify_data/vdpp_robin_fpga_verify_pyr/output/"

def main(args):
    ## set data root dir
    os.makedirs(host_root_dir, exist_ok=True)

    utl.run_cmd(f"adb shell rm -r {dev_output_folder}")
    utl.run_cmd(f"adb shell mkdir -p {dev_output_folder}")

    ## run command
    if b_test_vdpp:
        ## 1080p nv12 limited in. VEP PATH: hist + pyr + bbd (bbd result: top=0, btm=0, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test_out_vep_1080p"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/input_1920x1080_601l_nv12.yuv -w 1920 -g 1080 -f 0 -r 0 -o {sub_dir}/out_1920x1080_nv12_601l.yuv -F yuv420 -m 2 -d {sub_dir}")

        ## 1088p nv12 limited in. VEP PATH: hist + pyr + bbd. (bbd result: top=130, btm=125, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test_out_vep_1088p"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_1920x1088_709l_nv12.yuv -w 1920 -g 1088 -f 0 -r 0 -o {sub_dir}/out_1920x1088_nv12_709l.yuv -F yuv420 -m 2 -d {sub_dir}")

        ## 1088p nv12 limited in. DCI PATH: hist + bbd. (bbd result: top=130, btm=125->124, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test_out_dci_1088p_nv12"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_1920x1088_709l_nv12.yuv -w 1920 -g 1088 -f 0 -r 0 -o {sub_dir}/out_1920x1088_nv12_709l.yuv -F yuv420 -m 3 -d {sub_dir}")

        ## 4k nv12 in. DCI PATH: hist + bbd. (bbd result: top=22, btm=434, left=351->352, right=1784)
        sub_dir = f"{dev_output_folder}/vdpp_test_out_dci_4k_nv12"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_3840x2160_709f_nv12.yuv -w 3840 -g 2160 -f 0 -r 1 -o {sub_dir}/out_3840x2160_nv12.yuv -F yuv420 -m 3 -d {sub_dir}")

        ## 4k rgb in. DCI PATH: hist + bbd. (bbd result: top=22->20, btm=434->430, left=351->348, right=1784)
        sub_dir = f"{dev_output_folder}/vdpp_test_out_dci_4k_rgb"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_3840x2160_full_rgb.rgb -w 3840 -g 2160 -f 65542 -r 1 -m 3 -o {sub_dir}/out_3840x2160_nv24.yuv -F yuv444 -d {sub_dir}")

        ## 4k rgb in. DCI PATH: hist + bbd. (bbd result: top=0, btm=0, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test_out_dci_4k_rg24"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/input_4k_resolution_test_3840x2160_rg24_full.rgb -w 3840 -g 2160 -f 65542 -r 1 -m 3 -o {sub_dir}/out_3840x2160_nv24.yuv -F yuv444 -d {sub_dir}")

    if b_test_hwpq:
        ## 1080p nv12 limited in. VEP PATH: hist + pyr + bbd (bbd result: top=0, btm=0, left=0, right=0)
        sub_dir = f"{dev_output_folder}/hwpq_test_out_vep_1080p"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/input_1920x1080_601l_nv12.yuv -w 1920 -g 1080 -f 2 -r 0 -o {sub_dir}/out_1920x1080_nv12_601l.yuv -F 2 -m 2 -d {sub_dir}")

        ## 1088p nv12 limited in. VEP PATH: hist + pyr + bbd. (bbd result: top=130, btm=125, left=0, right=0)
        sub_dir = f"{dev_output_folder}/hwpq_test_out_vep_1088p"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_1920x1088_709l_nv12.yuv -w 1920 -g 1088 -f 2 -r 0 -o {sub_dir}/out_1920x1088_nv12_709l.yuv -F 2 -m 2 -d{sub_dir}")

        ## 1088p nv12 limited in. DCI PATH: hist + bbd. (bbd result: top=130, btm=125->124, left=0, right=0)
        sub_dir = f"{dev_output_folder}/hwpq_test_out_dci_1088p_nv12"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_1920x1088_709l_nv12.yuv -w 1920 -g 1088 -f 2 -r 0 -o {sub_dir}/out_1920x1088_nv12_709l.yuv -F 2 -m 3 -d {sub_dir}")

        ## 4k nv12 in. DCI PATH: hist + bbd. (bbd result: top=22, btm=434, left=351->352, right=1784)
        sub_dir = f"{dev_output_folder}/hwpq_test_out_dci_4k_nv12"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_3840x2160_709f_nv12.yuv -w 3840 -g 2160 -f 2 -r 1 -o {sub_dir}/out_3840x2160_nv12.yuv -F 2 -m 3 -d {sub_dir}")

        ## 4k rgb in. DCI PATH: hist + bbd. (bbd result: top=22->20, btm=434->430, left=351->348, right=1784)
        sub_dir = f"{dev_output_folder}/hwpq_test_out_dci_4k_rgb"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_3840x2160_full_rgb.rgb -w 3840 -g 2160 -f 1001 -r 1 -m 3 -o {sub_dir}/out_3840x2160_nv24.yuv -F yuv444 -d {sub_dir}")

        ## 4k rgb in. DCI PATH: hist + bbd. (bbd result: top=0, btm=0, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test_out_dci_4k_rg24"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/input_4k_resolution_test_3840x2160_rg24_full.rgb -w 3840 -g 2160 -f 65542 -r 1 -m 3 -o {sub_dir}/out_3840x2160_nv24.yuv -F yuv444 -d {sub_dir}")

    ## pull data
    utl.run_cmd(f"adb pull {dev_output_folder} {host_root_dir}")


if __name__ == "__main__":
    main(sys.argv)

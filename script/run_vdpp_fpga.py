"""
Copyright   : Copyright (c) by Rockchip. All right reserved.
FilePath    : run_vdpp_fpga.py
Author      : vance.wu@rock-chips.com
Date        : 2026-01-05
Description :
LastEditTime: 2025-01-22
"""

import os
import sys
import utils as utl

b_test_vdpp = True
b_test_hwpq = True
b_test_zme = True
plat_name = "rk3576"

dev_data_path = "/data/vdpp/"
dev_output_folder = f"{dev_data_path}/{plat_name}_0803_v1.4.3"
host_root_dir = "//172.16.4.246/vop/hwpq_verify_data/vdpp_robin_fpga_verify_pyr/output/"

def main(args):
    ## set data root dir
    os.makedirs(host_root_dir, exist_ok=True)

    utl.run_cmd(f"adb shell rm -r {dev_output_folder}")
    utl.run_cmd(f"adb shell mkdir -p {dev_output_folder}/vdpp_test/")
    utl.run_cmd(f"adb shell mkdir -p {dev_output_folder}/hwpq_test/")

    utl.run_cmd("adb shell setprop vendor.hwpq_debug 0x3F")
    utl.run_cmd("adb shell setprop vendor.vdpp_debug 0x3F")
    utl.run_cmd("adb shell setprop vendor.vdpp2_debug 0x3F")
    utl.run_cmd("adb shell setprop vendor.vdpp3_debug 0x3F")
    utl.run_cmd("adb shell \"echo 0x104 > /sys/module/rk_vcodec/parameters/mpp_dev_debug\"")

    ## run command
    if b_test_vdpp:
        ## 1080p nv12 limited in. VEP PATH: hist + pyr + bbd + diff_uv (bbd result: top=0, btm=0, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test/out_vep_1080p"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/input_1920x1080_601l_nv12.yuv -w 1920 -g 1080 -f 0 -r 0 -o {sub_dir}/out_1920x1080_nv12_601l.yuv --outc {sub_dir}/out_960x540_nv12_601l_chroma.yuv -F 2 -m 2 -d {sub_dir}")

        ## 1088p nv12 limited in. VEP PATH: hist + pyr + bbd + diff_uv. (bbd result: top=130, btm=125, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test/out_vep_1088p"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_1920x1088_709l_nv12.yuv -w 1920 -g 1088 -f 0 -r 0 -o {sub_dir}/out_1920x1088_nv24_709l.yuv --outc {sub_dir}/out_1920x1088_nv24_709l_chroma.yuv -F 0 -m 2 -d {sub_dir}")

        ## 1088p nv12 limited in. DCI PATH: hist + bbd. (bbd result: top=130, btm=125->124, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test/out_dci_1088p_nv12"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_1920x1088_709l_nv12.yuv -w 1920 -g 1088 -f 0 -r 0 -m 3 -d {sub_dir}")

        ## 4k nv12 in. DCI PATH: hist + bbd. (bbd result: top=22, btm=434, left=351->352, right=1784)
        sub_dir = f"{dev_output_folder}/vdpp_test/out_dci_4k_nv12"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_3840x2160_709f_nv12.yuv -w 3840 -g 2160 -f 0 -r 1 -m 3 -d {sub_dir}")

        ## 4k rgb in. DCI PATH: hist + bbd. (bbd result: top=22->20, btm=434->430, left=351->348, right=1784)
        sub_dir = f"{dev_output_folder}/vdpp_test/out_dci_4k_rgb"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_3840x2160_full_rgb.rgb -w 3840 -g 2160 -f 65542 -r 1 -m 3 -d {sub_dir}")

        ## 4k rgb in. DCI PATH: hist + bbd. (bbd result: top=0, btm=0, left=0, right=0)
        sub_dir = f"{dev_output_folder}/vdpp_test/out_dci_4k_rg24"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/input_4k_resolution_test_3840x2160_rg24_full.rgb -w 3840 -g 2160 -f 65542 -r 1 -m 3 -d {sub_dir}")

        ## other format for DCI PATH
        sub_dir = f"{dev_output_folder}/vdpp_test/out_dci_4k_rgba"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_3840x2160_full_rgba.rgb -w 3840 -g 2160 -f 65549 -r 1 -m 3 -d {sub_dir}")
        sub_dir = f"{dev_output_folder}/vdpp_test/out_dci_4k_nv15"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test -i {dev_data_path}/input/black_bar_3840x2160_709f_nv15.yuv -w 3840 -g 2160 -f 1 -r 1 -m 3 -d {sub_dir}")

        ## other module results
        sub_dir = f"{dev_output_folder}/vdpp_test/out_vep_1080p_com"
        com_arg = f"-i {dev_data_path}/input/input_960x540_601l_nv12.yuv -w 960 -g 540 -f 0 -r 0 -m 2"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell vdpp_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x1.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=1 --en_es=0 --en_shp=0")
        utl.run_cmd(f"adb shell vdpp_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x2.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=0 --en_es=1 --en_shp=0")
        utl.run_cmd(f"adb shell vdpp_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x3.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=1 --en_es=1 --en_shp=0")
        utl.run_cmd(f"adb shell vdpp_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x4.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=0 --en_es=0 --en_shp=1")
        utl.run_cmd(f"adb shell vdpp_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x5.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=1 --en_es=0 --en_shp=1")
        utl.run_cmd(f"adb shell vdpp_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x6.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=0 --en_es=1 --en_shp=1")
        utl.run_cmd(f"adb shell vdpp_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x7.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=1 --en_es=1 --en_shp=1")
        utl.run_cmd(f"adb shell vdpp_test {com_arg} -o {sub_dir}/out_1920x1080_nv24_601l_zme.yuv -F 0 -W 1920 -G 1080 --en_hist=1 --en_pyr=1 --en_bbd=1 --en_dmsr=1 --en_es=1 --en_shp=1")

    if b_test_hwpq:
        ## 1080p nv12 limited in. VEP PATH: hist + pyr + bbd + diff_uv (bbd result: top=0, btm=0, left=0, right=0)
        sub_dir = f"{dev_output_folder}/hwpq_test/out_vep_1080p"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/input_1920x1080_601l_nv12.yuv -w 1920 -g 1080 -f 2 -r 0 -o {sub_dir}/out_1920x1080_nv12_601l.yuv --outc {sub_dir}/out_960x540_nv12_601l_chroma.yuv -F 2 -m 2 -d {sub_dir}")

        ## 1088p nv12 limited in. VEP PATH: hist + pyr + bbd + diff_uv. (bbd result: top=130, btm=125, left=0, right=0)
        sub_dir = f"{dev_output_folder}/hwpq_test/out_vep_1088p"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_1920x1088_709l_nv12.yuv -w 1920 -g 1088 -f 2 -r 0 -o {sub_dir}/out_1920x1088_nv24_709l.yuv --outc {sub_dir}/out_1920x1088_nv24_709l_chroma.yuv -F 0 -m 2 -d {sub_dir}")

        ## 1088p nv12 limited in. DCI PATH: hist + bbd. (bbd result: top=130, btm=125->124, left=0, right=0)
        sub_dir = f"{dev_output_folder}/hwpq_test/out_dci_1088p_nv12"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_1920x1088_709l_nv12.yuv -w 1920 -g 1088 -f 2 -r 0 -m 3 -d {sub_dir}")

        ## 4k nv12 in. DCI PATH: hist + bbd. (bbd result: top=22, btm=434, left=351->352, right=1784)
        sub_dir = f"{dev_output_folder}/hwpq_test/out_dci_4k_nv12"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_3840x2160_709f_nv12.yuv -w 3840 -g 2160 -f 2 -r 1 -m 3 -d {sub_dir}")

        ## 4k rgb in. DCI PATH: hist + bbd. (bbd result: top=22->20, btm=434->430, left=351->348, right=1784)
        sub_dir = f"{dev_output_folder}/hwpq_test/out_dci_4k_rgb"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_3840x2160_full_rgb.rgb -w 3840 -g 2160 -f 1001 -r 1 -m 3 -d {sub_dir}")

        ## 4k rgb in. DCI PATH: hist + bbd. (bbd result: top=0, btm=0, left=0, right=0)
        sub_dir = f"{dev_output_folder}/hwpq_test/out_dci_4k_rg24"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/input_4k_resolution_test_3840x2160_rg24_full.rgb -w 3840 -g 2160 -f 1001 -r 1 -m 3 -d {sub_dir}")

        ## other format for DCI PATH
        sub_dir = f"{dev_output_folder}/hwpq_test/out_dci_4k_rgba"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_3840x2160_full_rgba.rgb -w 3840 -g 2160 -f 1000 -r 1 -m 3 -d {sub_dir}")
        sub_dir = f"{dev_output_folder}/hwpq_test/out_dci_4k_nv15"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test -i {dev_data_path}/input/black_bar_3840x2160_709f_nv15.yuv -w 3840 -g 2160 -f 3 -r 1 -m 3 -d {sub_dir}")

        ## other module results
        sub_dir = f"{dev_output_folder}/hwpq_test/out_vep_1080p_com"
        com_arg = f"-i {dev_data_path}/input/input_960x540_601l_nv12.yuv -w 960 -g 540 -f 2 -r 0 -m 2"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x1.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=1 --en_es=0 --en_shp=0")
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x2.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=0 --en_es=1 --en_shp=0")
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x3.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=1 --en_es=1 --en_shp=0")
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x4.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=0 --en_es=0 --en_shp=1")
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x5.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=1 --en_es=0 --en_shp=1")
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x6.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=0 --en_es=1 --en_shp=1")
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x540_nv12_601l_0x7.yuv -F 2 --en_hist=0 --en_pyr=0 --en_bbd=0 --en_dmsr=1 --en_es=1 --en_shp=1")
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_1920x1080_nv24_601l_zme.yuv -F 0 -W 1920 -G 1080 --en_hist=1 --en_pyr=1 --en_bbd=1 --en_dmsr=1 --en_es=1 --en_shp=1")

    if b_test_zme:
        sub_dir = f"{dev_output_folder}/zme_test/out_vep_1080p_zme"
        utl.run_cmd(f"adb shell mkdir -p {sub_dir}")

        com_arg = f"-i {dev_data_path}/input/input_1920x1080_601l_nv12.yuv -w 1920 -g 1080 -f 2 -r 0 -m 2 --en_pyr=0 --en_bbd=0 --en_es=0 --en_dmsr=0 --en_shp=0 --en_hist=0"
        # x1 == 1.0
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_1920x1080_nv24_601l.yuv -F 0")
        # x0.85 > 0.833
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_1632x912_nv12_601l.yuv -F 2 -W 1632 -G 912")
        # x0.75 >= 0.7
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_1440x816_nv12_601l.yuv -F 2 -W 1440 -G 816")
        # x0.5  >= 0.5
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x540_nv24_601l.yuv -F 0 -W 960 -G 540")
        # x0.4  >= 0.33
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_768x432_nv12_601l.yuv -F 2 -W 768 -G 432")
        # x0.25 >= 0.25
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_480x272_nv12_601l.yuv -F 2 -W 480 -G 272")

        com_arg = f"-i {dev_data_path}/input/input_480x272_601l_nv12.yuv -w 480 -g 272 -f 2 -r 0 -m 2 --en_pyr=0 --en_bbd=0 --en_es=0 --en_dmsr=0 --en_shp=0 --en_hist=0"
        # x1.2  >  1
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_576x328_nv12_601l.yuv -F 2 -W 576 -G 328")
        # x1.5  >= 1.5
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_720x408_nv12_601l.yuv -F 2 -W 720 -G 408")
        # x2    >= 2.0
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_960x544_nv12_601l.yuv -F 2 -W 960 -G 544")
        # x3    >= 2.667
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_1440x816_nv12_601l.yuv -F 2 -W 1440 -G 816")
        # x4    else
        utl.run_cmd(f"adb shell hwpq_test {com_arg} -o {sub_dir}/out_1920x1080_nv12_601l.yuv -F 2 -W 1920 -G 1080")

    ## pull data
    utl.run_cmd(f"adb pull {dev_output_folder} {host_root_dir}")


if __name__ == "__main__":
    main(sys.argv)

# cd /data/vdpp/output/
# hwpq_test -i ../input/input_1920x1080_601l_nv12.yuv -w 1920 -g 1080 -f 2 -r 0 -o out_1920x1080_nv24_601l.yuv -F 2 -m 2 --en_hist=0 --en_dmsr=1
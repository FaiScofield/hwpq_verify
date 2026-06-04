"""
DCI Layer 1 Runner UI launcher.

Use this script as the entry point for the interactive DCI UI.
The original batch helpers (do_png_to_yuv444p10l, do_yuv444p10l_to_png,
do_dci_sim) are kept below for backward-compatible CLI usage.
"""

import glob
import os
import sys

import utils as utl

data_dir = "V:/ai-contrast/9681Aicontrast/"


def do_png_to_yuv444p10l(data_dir):
    output_dir = os.path.join(data_dir, "dci_sim")

    # 获取 data_dir 下所有 xxx_off.png 文件
    png_files = glob.glob(os.path.join(data_dir, "*_off.png"))

    if not png_files:
        print(f"在 {data_dir} 目录下没有找到 *_off.png 文件")
        sys.exit(1)

    print(f"找到 {len(png_files)} 个 PNG 文件，开始转换...")

    for png_file in png_files:
        # 获取文件名（不含路径和扩展名）
        file_name = os.path.basename(png_file)
        base_name = file_name.split('.')[0]

        # 生成输出文件路径
        out_file = os.path.join(output_dir, f"{base_name}_1920x1080_yuv444p10le.yuv")

        # 执行 ffmpeg 转换（full-range yuv444p10le）
        # -color_range 2 指定为 full-range (0-1023 for 10bit) （只是标记了流的属性）
        # 默认是 limited-range (64-940 for 10bit)
        # 真正改变数据的是 'scale=out_range=pc'
        cmd = f'ffmpeg -i "{png_file}" -pix_fmt yuv444p10le -color_range 2 -vf "scale=out_range=pc" "{out_file}" -y'
        print(f"转换：{file_name} -> {base_name}_1920x1080_yuv444p10le.yuv")
        utl.run_cmd(cmd, showOutput=False, showCmd=True)

    print("所有文件转换完成！")


def do_yuv444p10l_to_png(data_dir):
    output_dir = data_dir

    # 获取 data_dir 下所有 xxx_yuv444p10le.yuv 文件
    yuv_files = glob.glob(os.path.join(data_dir, "*_yuv444p10le.yuv"))

    if not yuv_files:
        print(f"在 {data_dir} 目录下没有找到 *_yuv444p10le.yuv 文件")
        sys.exit(1)

    print(f"找到 {len(yuv_files)} 个 YUV 文件，开始转换...")

    for yuv_file in yuv_files:
        # 获取文件名（不含路径和扩展名）
        file_name = os.path.basename(yuv_file)
        # 去掉 _yuv444p10le 后缀
        base_name = file_name.replace('_yuv444p10le.yuv', '')

        # 生成输出文件路径
        out_file = os.path.join(output_dir, f"{base_name}.png")

        # 执行 ffmpeg 转换（yuv444p10le 转 png）
        # -color_range 2 指定输入为 full-range
        cmd = f'ffmpeg -y -color_range 2 -f rawvideo -pixel_format yuv444p10le -s 1920x1080 -i "{yuv_file}" -frames:v 1 -vf "format=rgb48be,format=rgb24" "{out_file}"'
        print(f"转换：{file_name} -> {base_name}.png")
        utl.run_cmd(cmd, showOutput=False, showCmd=True)

    print("所有文件转换完成！")


def do_dci_sim(data_dir, lce=25):
    output_dir = os.path.join(data_dir, "dci_sim")

    # 获取 data_dir 下所有 xxx_yuv444p10le.yuv 文件
    yuv_files = glob.glob(os.path.join(data_dir, "*_yuv444p10le.yuv"))

    if not yuv_files:
        print(f"在 {data_dir} 目录下没有找到 *_yuv444p10le.yuv 文件")
        sys.exit(1)

    print(f"找到 {len(yuv_files)} 个 YUV 文件，开始转换...")

    for yuv_file in yuv_files:
        # 获取文件名（不含路径和扩展名）
        file_name = os.path.basename(yuv_file)
        base_name = file_name.split('_')[0]

        # 生成输出文件路径
        out_file = os.path.join(output_dir, f"{base_name}_lce{lce}_1920x1080_yuv444p10le.yuv")

        # 执行 dci_sim_exe 转换
        cmd = f'G:/Codes/RkVopAlgos/pub_lib/ModelVerify/AMD64/bin/dci_sim_exe.exe -i "{yuv_file}" -f 0x13 -F 0x13 -o "{out_file}" -c G:/Codes/bucket_projects/hwpq_verify/data/vdpp_vop_config_3576.json -m 5'
        print(f"转换：{file_name} -> {base_name}_lce{lce}_1920x1080_yuv444p10le.yuv")
        utl.run_cmd(cmd, showOutput=False, showCmd=True)


if __name__ == "__main__":
    from dci.dci_ui import main
    main()

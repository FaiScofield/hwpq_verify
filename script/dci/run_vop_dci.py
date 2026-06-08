import argparse
import os
import glob
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import utils as utl
import draw_global_lut as dgl

data_dir = "V:/ai-contrast/9681Aicontrast/"
dci_exe = "G:/Codes/gerrit_projects/hwpq_verify/output/bin/dci_verify_demo.exe"
# config_file = "G:/Codes/gerrit_projects/hwpq_verify/data/vdpp_vop_config_3572.json"
# dci_exe = "G:/Codes/RkVopAlgos_git/pub_lib/ModelVerify/AMD64/bin/dci_sim_exe.exe"
config_file = "G:/Codes/gerrit_projects/hwpq_verify/data/dci_config_3572.json"
do_single_img_sim = "pdf2"
suffix = ""
draw_curve=False

def parse_args():
    """Parse command line arguments for the VOP DCI batch script."""
    parser = argparse.ArgumentParser(description="Run DCI simulation for *_off.png images.")
    parser.add_argument("--clahe_clip", type=float, default=1.0, help="CLAHE clip value.")
    parser.add_argument("--clahe_lce", type=int, default=19, help="CLAHE LCE value, recommended range [0, 32].")
    parser.add_argument("--peaking_gain", type=int, default=150, help="Peaking gain, recommended range [0, 1023].")
    return parser.parse_args()


def do_dci_sim(data_dir, clahe_clip=1.0, clahe_lce=19, peaking_gain=150):
    """Run DCI simulation for all matching PNG files in the target directory."""
    output_dir = os.path.join(data_dir, "dci_sim6_again")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 获取 data_dir 下所有 xxx_off.png 文件
    png_files = glob.glob(os.path.join(data_dir, "*_off.png"))

    if not png_files:
        print(f"在 {data_dir} 目录下没有找到 *_off.png 文件")
        sys.exit(1)

    print(f"找到 {len(png_files)} 个 PNG 文件，开始做DCI仿真...")

    for png_file in png_files:
        # 获取文件名（不含路径和扩展名）
        file_name = os.path.basename(png_file)
        base_name = file_name.split('_')[0]

        if do_single_img_sim != "" and base_name != do_single_img_sim:
            continue

        # 生成输出文件路径
        out_file = os.path.join(output_dir, f"{base_name}_rk_peaking{peaking_gain}_clip{clahe_clip}_lce{clahe_lce}.png")

        # 执行 dci_sim_exe 转换
        cmd = (
            f'{dci_exe} -i "{png_file}" -o "{out_file}" -c "{config_file}" -m 0 '
            f'--clahe_clip_value {clahe_clip} --clahe_local_ratio {clahe_lce} --shp_type 1 --shp_peaking_gain {peaking_gain} --dump 0xf0'
        )

        # input_file = f'{output_dir}/pdf2_input_1920x1080_yuv444p10l.yuv'
        # out_file = os.path.join(output_dir, f"{base_name}_rk_yuv44410pl_{suffix}.yuv")
        # cmd = f'{dci_exe} -i "{input_file}" -o "{out_file}" -c "{config_file}" -m 0 -f 0x13 --dump 0xf0'
        # print(f"转换：{file_name} -> {base_name}_lce{lce}.png")
        utl.run_cmd(cmd, showOutput=True, showCmd=True)

        # 画直方图和全局Lut曲线
        if draw_curve:
            global_lut_path = f'{output_dir}/VOP_pos1_DCI_Global_LUT_frame0.txt'
            local_lut_path = f'{output_dir}/VOP_pos3_DCI_Local_LUT_frame0.txt'
            global_hist_path = f'{output_dir}/vdpp_hist_data_global_unpacked.bin'
            local_hist_path = f'{output_dir}/vdpp_hist_data_local_unpacked.bin'
            pic_global_out = f'{output_dir}/{base_name}_hist_and_global_lut_{suffix}.png'
            pic_local_out = f'{output_dir}/{base_name}_hist_and_local_lut_{suffix}.png'
            multi_lut_specs = [
                (f'{output_dir}/VOP_pos1_DCI_CF_LUT_frm0.txt', "CF LUT"),
                (f'{output_dir}/VOP_pos2_DCI_HE_LUT_frm0.txt', "HE LUT"),
                (f'{output_dir}/VOP_pos3_DCI_Global_LUT_CFHE_frm0.txt', "Global LUT CFHE"),
                (f'{output_dir}/VOP_pos4_DCI_Global_LUT_WS_frm0.txt', "Global LUT WS"),
            ]
            multi_lut_output_path = f'{output_dir}/{base_name}_he_bs_global_lut_{suffix}.png'
            dgl.draw_combined_plot(global_lut_path, global_hist_path, pic_global_out)
            dgl.draw_local_combined_plot(local_lut_path, local_hist_path, pic_local_out)
            dgl.draw_multi_lut_plot(multi_lut_specs, multi_lut_output_path, f"{base_name} CF/HE/CF+HE/BS LUTs")
            utl.run_cmd(f'cp {png_file} {output_dir}/', showOutput=False, showCmd=False)

        print(f"proc done for {file_name}")
        if do_single_img_sim:
            return


if __name__ == "__main__":
    args = parse_args()
    args.clahe_lce = utl.clip(args.clahe_lce, 0, 32)
    args.peaking_gain = utl.clip(args.peaking_gain, 0, 1023)
    do_dci_sim(data_dir, args.clahe_clip, args.clahe_lce, args.peaking_gain)
    print("done.")

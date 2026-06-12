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
# dci_exe = "G:/Codes/RkVopAlgos/pub_lib/ModelVerify/AMD64/bin/dci_sim_exe.exe"
config_file = f"{data_dir}/dci_sim_to_cvte_0611/vop_base_config_rk3576_b.json"
do_single_img_sim = ""
suffix = "_CfgB"
# custum_args = "--cf_gain_low 0 --cf_gain_mid 0 --cf_gain_high 0 --cf_he_ratio 64"
custum_args = ""
draw_curve=True

def do_dci_sim(data_dir):
    """Run DCI simulation for all matching PNG files in the target directory."""
    output_dir = os.path.join(data_dir, "dci_sim_to_cvte_0611")
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
        out_file = os.path.join(output_dir, f"{base_name}_rk{suffix}.png")

        # 执行 dci_sim_exe 转换
        cmd = f'{dci_exe} -i "{png_file}" -o "{out_file}" -c "{config_file}" -m 0 --shp_type 1 --dump 0xf0 {custum_args}'


        # input_file = f'{output_dir}/pdf2_input_1920x1080_yuv444p10l.yuv'
        # out_file = os.path.join(output_dir, f"{base_name}_rk_yuv444p10l{suffix}.yuv")
        # cmd = f'{dci_exe} -i "{input_file}" -o "{out_file}" -c "{config_file}" -m 0 -f 0x13 --dump 0xf0 --clahe_clip_value {clahe_clip} --clahe_local_ratio {clahe_lce} --shp_type 1 --dump 0xf0 --cf_gain_low 0 --cf_gain_mid 0 --cf_gain_high 0 --cf_he_ratio 64'
        # print(f"转换：{file_name} -> {base_name}_lce{lce}.png")
        utl.run_cmd(cmd, showOutput=True, showCmd=True)

        # 画直方图和全局Lut曲线
        if draw_curve:
            pic_global_out = f'{output_dir}/{base_name}_rk_global_hist_luts{suffix}.png'
            global_hist_path = f'{output_dir}/vdpp_hist_data_global_unpacked.bin'
            global_luts_specs = [
                (f'{output_dir}/dci_glb1_cf_lut_frm0.txt', "Global CF"),
                (f'{output_dir}/dci_glb2_he_lut_frm0.txt', "Global HE"),
                (f'{output_dir}/dci_glb3_cfhe_lut_frm0.txt', "Global CFHE"),
                (f'{output_dir}/dci_glb4_cfhebws_lut_frm0.txt', "Global WS(Final)"),
            ]
            pic_local_out = f'{output_dir}/{base_name}_rk_local_hist_luts{suffix}.png'
            local_lut_path = f'{output_dir}/dci_local_clahe_lut_frm0.txt'
            local_hist_path = f'{output_dir}/vdpp_hist_data_local_unpacked.bin'
            print("正在绘制global/local 直方图和LUT曲线...")
            dgl.draw_global_hist_luts(global_luts_specs, global_hist_path, pic_global_out)
            # dgl.draw_local_hist_luts(local_lut_path, local_hist_path, pic_local_out)
            # utl.run_cmd(f'cp {png_file} {output_dir}/', showOutput=False, showCmd=False)

        print(f"proc done for {file_name}")
        if do_single_img_sim:
            return


if __name__ == "__main__":
    do_dci_sim(data_dir)
    print("done.")

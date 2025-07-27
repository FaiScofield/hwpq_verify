import os
import json
import argparse
import sys
import time
import numpy as np
import shutil
import struct
from utils import vop_py_tools as vt

max_exceed_value = (1 + 16)
min_exceed_value = (0 + 16)

vop_max_img_w = 4096
vop_max_img_h = 2400
vop_min_img_w = 128
vop_min_img_h = 128

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-ys", "--yseed", default=0)
    parser.add_argument("-js", "--jseed", default=0)
    parser.add_argument("-yn", "--yuv_cnt", default=10)
    parser.add_argument("-jn", "--cfg_cnt", default=10)

    parser.add_argument("-exe", "--exe_path", default="./exe/RkVopSimExe_v2633_debug_info_print_off")
    parser.add_argument("-odir", "--dst_dir", default="./dst_dir/")

    args = parser.parse_args()

    timestamp = time.time()
    time_tuple = time.localtime(timestamp)
    time_str = time.strftime("%Y%m%d%H%M%S", time_tuple)

    dst_dir     = args.dst_dir
    exe_path    = args.exe_path
    yseed       = int(args.yseed)
    jseed       = int(args.jseed)
    cfg_cnt     = int(args.cfg_cnt)
    yuv_cnt     = int(args.yuv_cnt)

    ## generate folders
    yuv_path, json_path, fpga_path, fpga_cfg_path, fpga_result_path, fpga_yuv_path, temp_path = generate_folders(dst_dir, time_str)

    ## compile .c tools
    exe_temp = "./temp_exe/"
    vt.check_exist(exe_temp)
    compile_tools(exe_temp)

    # generate fpga result parser
    cmd = "cp ./c_src/parse_fpga_result.exe %sparse_fpga_result.exe" % (fpga_result_path)
    vt.run_cmd(cmd)

    bat_info = "parse_fpga_result.exe ./crc_fpga_result.bin ./crc_fpga_result_%s.dat %d %d 2" % (time_str, yuv_cnt, cfg_cnt)
    cmd = "echo %s >> %s/parse_fpga_result.bat" % (bat_info, fpga_result_path)
    vt.run_cmd(cmd)


    # generate config
    generate_guide_config(fpga_path, yseed, jseed, yuv_cnt, cfg_cnt)

    for yuv_idx in range(0, yuv_cnt, 1):
        yuv_name = "rand_seed_%08d_yuv444p10le.yuv" % (yseed + yuv_idx)
        cmd = "%sgen_rand_yuv %s %d %d %d 0 0" % (exe_temp, yuv_path, yseed + yuv_idx, vop_max_img_w, vop_max_img_h)
        vt.run_cmd(cmd)

        cmd = "%scvt_unpack_2_pack %s/%s %s/%s %d %d 3 0" % (exe_temp, yuv_path, yuv_name, fpga_yuv_path, yuv_name, vop_max_img_w, vop_max_img_h)
        vt.run_cmd(cmd)

    cnt = 0
    for cfg_idx in range(0, cfg_cnt, 1):
        generate_cfg(jseed + cfg_idx, json_path, exe_temp)

        # generate random bin
        rand_json_name = "%s/rand_json_seed_%08d.json" % (json_path, jseed + cfg_idx)
        cmd0 = "%s -m -i=./default.yuv -o=%stmp.yuv -l=%s -cfg=%s" % (exe_path, temp_path, temp_path, rand_json_name)
        cmd1 = "-iwvir=%d -iwrel=%d -iwvld=%d -ihvir=%d -ihrel=%d -ihvld=%d -owvir=%d -owrel=%d -owvld=%d -ohrel=%d -ohvld=%d" % (
            64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64
        )
        cmd2 = "-fmt=4 -ofmt=0 -f=1 -s=0 -is=0 -os=0 -itype=1 -di=0"

        cmd = "%s %s %s >> %s/run_log" % (cmd0, cmd1, cmd2, temp_path)
        vt.run_cmd(cmd)

        dst_dir_list = os.listdir(temp_path)
        for file in dst_dir_list:
            if (file == "sharp_reg_.bin"):
                dst_bin_name = "sharp_config_seed_%d_idx_%d.bin" % (jseed, cnt)
                shutil.move(temp_path+file, fpga_cfg_path+dst_bin_name)
            elif (file == "acm_hw_config.dat"):
                dst_bin_name = "acm_config_seed_%d_idx_%d.bin" % (jseed, cnt)
                shutil.move(temp_path+file, fpga_cfg_path+dst_bin_name)
            else:
                os.remove(temp_path+file)

        cnt = cnt + 1
    for ii in range(0, cnt, 1):
        bin_temp = "%s/sharp_config_seed_%d_idx_%d.bin" % (fpga_cfg_path, jseed, ii)
        cmd = "cat %s >> %s/sharp_config_seed_%d.bin" % (bin_temp, fpga_cfg_path, jseed)
        vt.run_cmd(cmd)
        cmd = "rm %s" % (bin_temp)
        vt.run_cmd(cmd)

        bin_temp = "%s/acm_config_seed_%d_idx_%d.bin" % (fpga_cfg_path, jseed, ii)
        cmd = "cat %s >> %s/acm_config_seed_%d.bin" % (bin_temp, fpga_cfg_path, jseed)
        vt.run_cmd(cmd)
        cmd = "rm %s" % (bin_temp)
        vt.run_cmd(cmd)

        bin_temp = "%s/dither_cfg_%08d.bin" % (json_path, jseed + ii)
        cmd = "cat %s >> %s/dither_cfg_%d.bin" % (bin_temp, fpga_cfg_path, jseed)
        vt.run_cmd(cmd)
        cmd = "rm %s" % (bin_temp)
        vt.run_cmd(cmd)

        bin_temp = "%s/dci_hw_lut_%08d.dat" % (json_path, jseed + ii)
        cmd = "cat %s >> %s/dci_hw_lut_%d.bin" % (bin_temp, fpga_cfg_path, jseed)
        vt.run_cmd(cmd)
        cmd = "rm %s" % (bin_temp)
        vt.run_cmd(cmd)

        bin_temp = "%s/dci_reg_list_%08d.dat" % (json_path, jseed + ii)
        cmd = "cat %s >> %s/dci_reg_list_%d.bin" % (bin_temp, fpga_cfg_path, jseed)
        vt.run_cmd(cmd)
        cmd = "rm %s" % (bin_temp)
        vt.run_cmd(cmd)

    vt.rm_dir(exe_temp)
    cmd = "rm PQ_ALGORITHM_PRE_debug.*"
    vt.run_cmd(cmd)
    print("finish generate(%s)" % (time_str))
    return

def generate_guide_config(fpga_path, yseed, jseed, yuv_cnt, cfg_cnt):
    json_ref_path = "./cfg_mask/vop_fpga_cfg.json"
    with open(json_ref_path, "r") as f_in:
        json_ref_root = json.load(f_in)
    json_dst_root = json_ref_root
    json_dst_path = "%s/vop_rand_dir/vop_rand_cfg.json" % (fpga_path)

    json_dst_root["yuv_seed"]       = yseed
    json_dst_root["cfg_seed"]       = jseed
    json_dst_root["yuv_cnt"]        = yuv_cnt
    json_dst_root["cfg_cnt"]        = cfg_cnt

    json_dst_root["cfg_bin_path"]           = "vop_rand_dir/sharp_config_seed_%d.bin" % (jseed)
    json_dst_root["dither_cfg_bin_path"]    = "vop_rand_dir/dither_cfg_%d.bin" % (jseed)
    json_dst_root["dci_cfg_lut_path"]    = "vop_rand_dir/dci_hw_lut_%d.bin" % (jseed)
    json_dst_root["dci_cfg_reg_path"]    = "vop_rand_dir/dci_reg_list_%d.bin" % (jseed)
    json_dst_root["acm_cfg_lut_path"]    = "vop_rand_dir/acm_config_seed_%d.bin" % (jseed)

    with open(json_dst_path, "w") as f_out:
        json.dump(json_dst_root, f_out, indent=4, separators=(', ', ': '))

def compile_tools(temp_path):
    # print(temp_path)
    vt.run_cmd("gcc ./c_src/convert_10bit_pack_to_10bit_unpack.c -o cvt_pack2unpack")
    vt.run_cmd("mv cvt_pack2unpack %scvt_pack_2_unpack" % (temp_path))
    vt.run_cmd("gcc ./c_src/cvt_10bit_unpack_2_10bit_pack.c -o cvt_unpack2pack")
    vt.run_cmd("mv cvt_unpack2pack %scvt_unpack_2_pack" % (temp_path))
    vt.run_cmd("gcc ./c_src/gen_dci_config.c -o gen_dci_cfg")
    vt.run_cmd("mv gen_dci_cfg %sgen_dci_cfg" % (temp_path))
    vt.run_cmd("gcc ./c_src/generate_vop_rand.c -o gen_rand_yuv")
    vt.run_cmd("mv gen_rand_yuv %sgen_rand_yuv" % (temp_path))

def generate_folders(dst_dir, time_str):
    vt.check_exist(dst_dir)
    yuv_path    = "%s/%s_yuv_dir/" % (dst_dir, time_str)
    vt.check_exist(yuv_path)
    json_path    = "%s/%s_json_dir/" % (dst_dir, time_str)
    vt.check_exist(json_path)
    fpga_path    = "%s/%s_fpga_dir/" % (dst_dir, time_str)
    vt.check_exist(fpga_path)
    fpga_cfg_path = "%s/vop_rand_dir/" % (fpga_path)
    vt.check_exist(fpga_cfg_path)
    fpga_result_path = "%s/vop_rand_result/" % (fpga_path)
    vt.check_exist(fpga_result_path)
    fpga_yuv_path = "%s/vop_rand_yuv/" % (fpga_path)
    vt.check_exist(fpga_yuv_path)

    temp_path       = "/run/shm/temp_dir_%s/" % (time_str)
    vt.check_exist(temp_path)

    return yuv_path, json_path, fpga_path, fpga_cfg_path, fpga_result_path, fpga_yuv_path, temp_path

def generate_cfg(jseed, json_path, temp_path):
    np.random.seed(jseed)
    json_mask_path = "./cfg_mask/sharp_cfg_mask_sharp.json"
    with open(json_mask_path, "r") as f_in:
        json_root = json.load(f_in)
        sharp_mask = json_root["sharp_mask"]
    ref_json_path = "./cfg_mask/vop_config_sharp_ref.json"
    with open(ref_json_path, "r") as f_in:
        json_ref = json.load(f_in)
    rand_json_name = "%s/rand_json_seed_%08d.json" % (json_path, jseed)
    rand_json_tmp = generate_rand_cfg(sharp_mask, "sharp_mask")
    json_ref["pq_tuning_param"]["SHARPNESS"] = rand_json_tmp
    json_ref = sharp_cfg_check(json_ref)

    ## resolusion config
    img_w = generate_rand_int(vop_min_img_w, vop_max_img_w)
    img_h = generate_rand_int(vop_min_img_h, vop_max_img_h)
    img_w = (img_w >> 1) << 1
    img_h = (img_h >> 1) << 1
    json_ref["global_param"]["inwidvirtual"]    = img_w
    json_ref["global_param"]["inwidreal"]       = img_w
    json_ref["global_param"]["inwidvalid"]      = img_w
    json_ref["global_param"]["inhgtvirtual"]    = img_h
    json_ref["global_param"]["inhgtreal"]       = img_h
    json_ref["global_param"]["inhgtvalid"]      = img_h
    json_ref["global_param"]["outwidreal"]      = img_w
    json_ref["global_param"]["outwidvalid"]     = img_w
    json_ref["global_param"]["outwidvirtual"]   = img_w
    json_ref["global_param"]["outhgtreal"]      = img_h
    json_ref["global_param"]["outhgtvalid"]     = img_h

    ## dci config
    dci_en = 1#generate_rand_int(0, 1)
    global max_exceed_value
    global min_exceed_value
    max_exceed_value = 2
    min_exceed_value = 1
    csc_range = generate_rand_int(0, 1)
    ca_en = generate_rand_int(0, 1)
    hsd_mode = generate_rand_int(0, 1)
    vsd_mode = generate_rand_int(0, 2)
    json_ref["pq_tuning_param"]["dci"]["s_vop_dci_interp_params"]["s_vop_dci_ctrl"]["i_dciEnable"] = dci_en
    json_ref["pq_tuning_param"]["dci"]["s_vop_dci_interp_params"]["s_vop_dci_ctrl"]["i_vopIn_csc_range"] = csc_range
    json_ref["pq_tuning_param"]["dci"]["s_vop_dci_interp_params"]["s_vop_dci_ctrl"]["i_vop_srand_seed"] = jseed
    json_ref["pq_tuning_param"]["dci"]["s_vop_dci_interp_params"]["s_color_adjust_params"]["i_dci_CA_enable"] = ca_en
    json_ref["pq_tuning_param"]["dci"]["s_vdpp_hist_cnt"]["dci_hsd_mode"] = hsd_mode
    json_ref["pq_tuning_param"]["dci"]["s_vdpp_hist_cnt"]["dci_vsd_mode"] = vsd_mode

    cmd = "%sgen_dci_cfg %s/ %d %d %d %d %d %d %d %d" % (temp_path, json_path, jseed, img_w, img_h, dci_en, csc_range, ca_en, hsd_mode, vsd_mode)
    vt.run_cmd(cmd)

    ## dither config
    dither_cfg = generate_dither_cfg(jseed)
    # print(dither_cfg["dither_cfg"])
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["i_dither_auto_idx_en"] = 0
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["i_dither_mode"]        = dither_cfg["dither_cfg"][0]
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["t_dither_DA_index"][0] = dither_cfg["dither_cfg"][1]
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["t_dither_DA_index"][1] = dither_cfg["dither_cfg"][2]
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["t_dither_DA_index"][2] = dither_cfg["dither_cfg"][3]
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["t_dither_dither_strength"][0] = dither_cfg["dither_cfg"][4]
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["t_dither_dither_strength"][1] = dither_cfg["dither_cfg"][5]
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["t_dither_dither_strength"][2] = dither_cfg["dither_cfg"][6]
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["i_dither_range_sca"] = dither_cfg["dither_cfg"][7]
    json_ref["pq_tuning_param"]["dither"]["s_dither_params"]["i_dither_frame_idx"] = dither_cfg["dither_cfg"][8]

    ## acm config
    acm_cfg = generate_acm_cfg()

    json_ref["pq_tuning_param"]["acm"]["acmEnable"]         = acm_cfg["acmEnable"]
    json_ref["pq_tuning_param"]["acm"]["acmTableDeltaYbyH"] = acm_cfg["acmTableDeltaYbyH"]
    json_ref["pq_tuning_param"]["acm"]["acmTableDeltaHbyH"] = acm_cfg["acmTableDeltaHbyH"]
    json_ref["pq_tuning_param"]["acm"]["acmTableDeltaSbyH"] = acm_cfg["acmTableDeltaSbyH"]
    json_ref["pq_tuning_param"]["acm"]["acmTableGainYbyY"]  = acm_cfg["acmTableGainYbyY"]
    json_ref["pq_tuning_param"]["acm"]["acmTableGainHbyY"]  = acm_cfg["acmTableGainHbyY"]
    json_ref["pq_tuning_param"]["acm"]["acmTableGainSbyY"]  = acm_cfg["acmTableGainSbyY"]
    json_ref["pq_tuning_param"]["acm"]["acmTableGainYbyS"]  = acm_cfg["acmTableGainYbyS"]
    json_ref["pq_tuning_param"]["acm"]["acmTableGainHbyS"]  = acm_cfg["acmTableGainHbyS"]
    json_ref["pq_tuning_param"]["acm"]["acmTableGainSbyS"]  = acm_cfg["acmTableGainSbyS"]
    json_ref["pq_tuning_param"]["acm"]["lumGain"]           = acm_cfg["lumGain"]
    json_ref["pq_tuning_param"]["acm"]["hueGain"]           = acm_cfg["hueGain"]
    json_ref["pq_tuning_param"]["acm"]["satGain"]           = acm_cfg["satGain"]

    dither_cfg_name = "%s/dither_cfg_%08d.bin" % (json_path, jseed)
    if os.path.exists(dither_cfg_name):
        cmd = "rm %s" % (dither_cfg_name)
        vt.run_cmd(cmd)

    with open(dither_cfg_name, 'wb') as f:
        vt.write_records(dither_cfg["dither_cfg"], 'i', f)
        f.close()

    # print(rand_json_name)
    with open(rand_json_name, "w") as f_out:
        json.dump(json_ref, f_out, indent=4, separators=(', ', ': '))
    return

def sharp_cfg_check(root):
    # peaking_ctrl_cfg check
    peaking_subroot = root["pq_tuning_param"]["SHARPNESS"]["s_peaking"]
    for band_idx in range(0, 8, 1):
        coring_zero = peaking_subroot["s_coring"]["t_CoringZero"][band_idx]
        coring_thrd = peaking_subroot["s_coring"]["t_CoringThreshold"][band_idx]
        limit_pos0  = peaking_subroot["s_limitCtrl"]["t_LimitPos0"][band_idx]
        limit_pos1  = peaking_subroot["s_limitCtrl"]["t_LimitPos1"][band_idx]
        limit_neg0  = peaking_subroot["s_limitCtrl"]["t_LimitNeg0"][band_idx]
        limit_neg1  = peaking_subroot["s_limitCtrl"]["t_LimitNeg1"][band_idx]

        coring_thrd = value_recheck(coring_zero, coring_thrd, 1023)
        limit_pos0  = value_recheck(coring_thrd, limit_pos0, 1023)
        limit_pos1  = value_recheck(limit_pos0, limit_pos1, 1023)

        coring_thrd = value_recheck(coring_zero, coring_thrd, 1023)
        limit_neg0  = value_recheck(coring_thrd, limit_neg0, 1023)
        limit_neg1  = value_recheck(limit_neg0, limit_neg1, 1023)

        peaking_subroot["s_coring"]["t_CoringZero"][band_idx] = coring_zero
        peaking_subroot["s_coring"]["t_CoringThreshold"][band_idx] = coring_thrd
        peaking_subroot["s_limitCtrl"]["t_LimitPos0"][band_idx] = limit_pos0
        peaking_subroot["s_limitCtrl"]["t_LimitPos1"][band_idx] = limit_pos1
        peaking_subroot["s_limitCtrl"]["t_LimitNeg0"][band_idx] = limit_neg0
        peaking_subroot["s_limitCtrl"]["t_LimitNeg1"][band_idx] = limit_neg1
    root["pq_tuning_param"]["SHARPNESS"]["s_peaking"] = peaking_subroot

    # var/adp/lum/texture_grd check
    gain_ctrl_subroot = root["pq_tuning_param"]["SHARPNESS"]["s_globalGain"]
    texture_adj_subroot = root["pq_tuning_param"]["SHARPNESS"]["s_textureAdj"]
    adp_grd0 = gain_ctrl_subroot["s_adp_gain"]["t_adp_grd"][0]
    var_grd0 = gain_ctrl_subroot["s_var_gain"]["t_var_grd"][0]
    lum_grd0 = gain_ctrl_subroot["s_lum_gain"]["t_lum_grd"][0]
    tex_grd0 = texture_adj_subroot["t_texture_grd"][0]
    for grd_idx in range(1, 6, 1):
        adp_grd1 = gain_ctrl_subroot["s_adp_gain"]["t_adp_grd"][grd_idx]
        var_grd1 = gain_ctrl_subroot["s_var_gain"]["t_var_grd"][grd_idx]
        lum_grd1 = gain_ctrl_subroot["s_lum_gain"]["t_lum_grd"][grd_idx]
        tex_grd1 = texture_adj_subroot["t_texture_grd"][grd_idx]

        adp_grd1 = value_recheck(adp_grd0, adp_grd1, 1023)
        var_grd1 = value_recheck(var_grd0, var_grd1, 1023)
        lum_grd1 = value_recheck(lum_grd0, lum_grd1, 1023)
        tex_grd1 = value_recheck(tex_grd0, tex_grd1, 1023)

        gain_ctrl_subroot["s_adp_gain"]["t_adp_grd"][grd_idx] = adp_grd1
        gain_ctrl_subroot["s_var_gain"]["t_var_grd"][grd_idx] = var_grd1
        gain_ctrl_subroot["s_lum_gain"]["t_lum_grd"][grd_idx] = lum_grd1
        texture_adj_subroot["t_texture_grd"][grd_idx] = tex_grd1

        adp_grd0 = adp_grd1
        var_grd0 = var_grd1
        lum_grd0 = lum_grd1
        tex_grd0 = tex_grd1
    root["pq_tuning_param"]["SHARPNESS"]["s_globalGain"] = gain_ctrl_subroot
    root["pq_tuning_param"]["SHARPNESS"]["s_textureAdj"] = texture_adj_subroot

    roi_x_s = root["pq_tuning_param"]["SHARPNESS"]["s_sharpRoiCfg"]["i_roi_xstart"]
    roi_x_e = root["pq_tuning_param"]["SHARPNESS"]["s_sharpRoiCfg"]["i_roi_xend"]
    roi_y_s = root["pq_tuning_param"]["SHARPNESS"]["s_sharpRoiCfg"]["i_roi_ystart"]
    roi_y_e = root["pq_tuning_param"]["SHARPNESS"]["s_sharpRoiCfg"]["i_roi_yend"]
    roi_x_s = max(min(3838, roi_x_s), 0)
    roi_x_e = max(min(3838, roi_x_e), 0)
    roi_y_s = max(min(2158, roi_y_s), 0)
    roi_y_e = max(min(2158, roi_y_e), 0)
    roi_x_e = value_recheck(roi_x_s, roi_x_e, 3839)
    roi_y_e = value_recheck(roi_y_s, roi_y_e, 2159)
    root["pq_tuning_param"]["SHARPNESS"]["s_sharpRoiCfg"]["i_roi_xstart"]   = roi_x_s
    root["pq_tuning_param"]["SHARPNESS"]["s_sharpRoiCfg"]["i_roi_xend"]     = roi_x_e
    root["pq_tuning_param"]["SHARPNESS"]["s_sharpRoiCfg"]["i_roi_ystart"]   = roi_y_s
    root["pq_tuning_param"]["SHARPNESS"]["s_sharpRoiCfg"]["i_roi_yend"]     = roi_y_e

    # filter_core check
    filter_core_subroot = root["pq_tuning_param"]["SHARPNESS"]["s_peaking"]["s_filter_cfg"]
    filter_core_subroot["t_filt_core_H0"][0] = generate_rand_int(-15, 15)
    filter_core_subroot["t_filt_core_H1"][0] = generate_rand_int(-15, 15)
    filter_core_subroot["t_filt_core_H2"][0] = generate_rand_int(-15, 15)
    filter_core_subroot["t_filt_core_H3"][0] = generate_rand_int(-15, 15)

    filter_core_subroot["t_filt_core_H0"][1] = generate_rand_int(-63, 63)
    filter_core_subroot["t_filt_core_H1"][1] = generate_rand_int(-63, 63)
    filter_core_subroot["t_filt_core_H2"][1] = generate_rand_int(-63, 63)
    filter_core_subroot["t_filt_core_H3"][1] = generate_rand_int(-63, 63)

    filter_core_subroot["t_filt_core_H0"][2] = generate_rand_int(-255, 255)
    filter_core_subroot["t_filt_core_H1"][2] = generate_rand_int(-255, 255)
    filter_core_subroot["t_filt_core_H2"][2] = generate_rand_int(-255, 255)
    filter_core_subroot["t_filt_core_H3"][2] = generate_rand_int(-255, 255)

    filter_core_subroot["t_filt_core_H0"][3] = generate_rand_int(-511, 511)
    filter_core_subroot["t_filt_core_H1"][3] = generate_rand_int(-511, 511)
    filter_core_subroot["t_filt_core_H2"][3] = generate_rand_int(-511, 511)
    filter_core_subroot["t_filt_core_H3"][3] = generate_rand_int(-511, 511)

    filter_core_subroot["t_filt_core_H0"][4] = generate_rand_int(-1023, 1023)
    filter_core_subroot["t_filt_core_H1"][4] = generate_rand_int(-1023, 1023)
    filter_core_subroot["t_filt_core_H2"][4] = generate_rand_int(-1023, 1023)
    filter_core_subroot["t_filt_core_H3"][4] = generate_rand_int(-1023, 1023)

    filter_core_subroot["t_filt_core_H0"][5] = generate_rand_int(0, 1023)
    filter_core_subroot["t_filt_core_H1"][5] = generate_rand_int(0, 1023)
    filter_core_subroot["t_filt_core_H2"][5] = generate_rand_int(0, 1023)
    filter_core_subroot["t_filt_core_H3"][5] = generate_rand_int(0, 1023)

    filter_core_subroot["t_filt_core_V0"][0] = generate_rand_int(-8, 7)
    filter_core_subroot["t_filt_core_V1"][0] = generate_rand_int(-8, 7)
    filter_core_subroot["t_filt_core_V2"][0] = generate_rand_int(-8, 7)

    filter_core_subroot["t_filt_core_V0"][1] = generate_rand_int(-8, 7)
    filter_core_subroot["t_filt_core_V1"][1] = generate_rand_int(-8, 7)
    filter_core_subroot["t_filt_core_V2"][1] = generate_rand_int(-8, 7)

    filter_core_subroot["t_filt_core_V0"][2] = generate_rand_int(0, 15)
    filter_core_subroot["t_filt_core_V1"][2] = generate_rand_int(0, 15)
    filter_core_subroot["t_filt_core_V2"][2] = generate_rand_int(0, 15)

    root["pq_tuning_param"]["SHARPNESS"]["s_peaking"]["s_filter_cfg"] = filter_core_subroot
    return root

def value_recheck(pos0, pos1, max_range):
    if (pos1 < pos0):
        pos1 = generate_rand_int(pos0, max_range)
    return pos1

def generate_rand_int(min_value, max_value):
    global max_exceed_value
    global min_exceed_value
    max_min_range = (max_value - min_value) * 2
    max_exceed = max_min_range
    min_exceed = max_min_range+1
    tmp = np.random.randint(low=min_value - min_exceed, high=max_value + max_exceed, size=1)
    tmp = tmp.tolist()
    result = tmp[0]
    result = min(max_value, max(min_value, result))
    return result

def generate_rand_cfg(root, root_name):
    tab_tmp = []
    tab_dict_tmp = {}
    global max_exceed_value
    global min_exceed_value
    max_exceed_value = 16
    min_exceed_value = 8
    for sub_root in root:
        if sub_root[0:2] == "s_":
            sub_tab_form = generate_rand_cfg(root[sub_root], sub_root)
            tab_dict_tmp[sub_root] = sub_tab_form
        else:
            tab_value = root[sub_root]
            if tab_value[0] == 0: # generate int value
                min_value = tab_value[1]
                max_value = tab_value[2]
                rand_length = tab_value[3]
                if rand_length == 1:
                    if (max_value == min_value):
                        rand_value = max_value
                        # value_tmp = rand_value
                    else:
                        value_list_tmp = np.random.randint(low=min_value - min_exceed_value, high=max_value+max_exceed_value, size=rand_length)
                        value_list_tmp = value_list_tmp.tolist()
                        rand_value = min(max_value, max(min_value, value_list_tmp[0]))
                        # print(type(rand_value).__name__)
                    tab_dict_tmp[sub_root] = rand_value
                else:
                    rand_value = np.random.randint(low=min_value - min_exceed_value, high=max_value+max_exceed_value, size=rand_length)
                    rand_value = np.clip(rand_value, min_value, max_value)
                    tab_dict_tmp[sub_root] = rand_value.tolist()

            elif tab_value[0] == 1: # str
                root[sub_root]
                tab_dict_tmp[sub_root] = tab_value[4]

    return tab_dict_tmp

def generate_dither_cfg(seed):
    np.random.seed(seed)
    global max_exceed_value
    global min_exceed_value
    max_exceed_value = 2
    min_exceed_value = 1
    DB_cfg = []
    DB_cfg.append(generate_rand_int(0, 3))
    DB_cfg.append(generate_rand_int(0, 2))
    DB_cfg.append(generate_rand_int(0, 2))
    DB_cfg.append(generate_rand_int(0, 2))

    max_exceed_value = 256
    min_exceed_value = 256
    DB_cfg.append(generate_rand_int(0, 1023))
    DB_cfg.append(generate_rand_int(0, 1023))
    DB_cfg.append(generate_rand_int(0, 1023))
    if (DB_cfg[0] < 2):
        ## Mode 0, 1: 10bit Input
        DB_cfg.append(generate_rand_int(0, 2017))
    else:
        ## Mode 1, 2: 8bit Input
        DB_cfg.append(generate_rand_int(0, 4110))

    max_exceed_value = 1
    min_exceed_value = 1
    DB_cfg.append(generate_rand_int(0, 7))

    dither_cfg = {}
    dither_cfg["dither_cfg"] = DB_cfg
    return dither_cfg

def generate_acm_cfg():
    acm_en = np.maximum(0, np.minimum(1, np.random.randint(low=0, high=3, size=1)))
    acm_tab_ydelta = np.maximum(-256, np.minimum(255, np.random.randint(low=-512, high=512, size=65)))
    acm_tab_hdelta = np.maximum(-64, np.minimum(63, np.random.randint(low=-64, high=64, size=65)))
    acm_tab_sdelta = np.maximum(-256, np.minimum(255, np.random.randint(low=-512, high=512, size=65)))
    acm_tab_ygain_by_y = np.maximum(-128, np.minimum(127, np.random.randint(low=-256, high=256, size=9*17)))
    acm_tab_hgain_by_y = np.maximum(-128, np.minimum(127, np.random.randint(low=-256, high=256, size=9*17)))
    acm_tab_sgain_by_y = np.maximum(-128, np.minimum(127, np.random.randint(low=-256, high=256, size=9*17)))
    acm_tab_ygain_by_s = np.maximum(-128, np.minimum(127, np.random.randint(low=-256, high=256, size=13*17)))
    acm_tab_hgain_by_s = np.maximum(-128, np.minimum(127, np.random.randint(low=-256, high=256, size=13*17)))
    acm_tab_sgain_by_s = np.maximum(-128, np.minimum(127, np.random.randint(low=-256, high=256, size=13*17)))
    acm_y_gain = np.maximum(0, np.minimum(1023, np.random.randint(low=-512, high=1535, size=1)))
    acm_h_gain = np.maximum(0, np.minimum(1023, np.random.randint(low=-512, high=1535, size=1)))
    acm_s_gain = np.maximum(0, np.minimum(1023, np.random.randint(low=-512, high=1535, size=1)))
    acm_cfg = dict()
    acm_en_tmp = acm_en.tolist()
    acm_y_gain_tmp = acm_y_gain.tolist()
    acm_h_gain_tmp = acm_h_gain.tolist()
    acm_s_gain_tmp = acm_s_gain.tolist()
    acm_cfg["acmEnable"] = acm_en_tmp[0]
    acm_cfg["lumGain"] = acm_y_gain_tmp[0]
    acm_cfg["hueGain"] = acm_h_gain_tmp[0]
    acm_cfg["satGain"] = acm_s_gain_tmp[0]
    acm_cfg["acmTableDeltaYbyH"] = acm_tab_ydelta.tolist()
    acm_cfg["acmTableDeltaHbyH"] = acm_tab_hdelta.tolist()
    acm_cfg["acmTableDeltaSbyH"] = acm_tab_sdelta.tolist()
    acm_cfg["acmTableGainYbyY"] = acm_tab_ygain_by_y.tolist()
    acm_cfg["acmTableGainHbyY"] = acm_tab_hgain_by_y.tolist()
    acm_cfg["acmTableGainSbyY"] = acm_tab_sgain_by_y.tolist()
    acm_cfg["acmTableGainYbyS"] = acm_tab_ygain_by_s.tolist()
    acm_cfg["acmTableGainHbyS"] = acm_tab_hgain_by_s.tolist()
    acm_cfg["acmTableGainSbyS"] = acm_tab_sgain_by_s.tolist()

    return acm_cfg

def generate_yuv(img_w, img_h, pip_num, seed, dst_file_name):
    np.random.seed(seed)
    yuv_rand = np.random.randint(low=0, high=255, size=(1, img_w * img_h * pip_num * 1))
    yuv_rand = yuv_rand.astype('uint8')

    binfile = open(dst_file_name, 'wb')
    binfile.write(yuv_rand)
    binfile.close()

if __name__ == "__main__":
    args = sys.argv
    main(args)

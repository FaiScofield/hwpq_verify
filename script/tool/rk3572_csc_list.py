import argparse
from typing import Optional
import numpy as np
from rkvop_csc import *

g_supported_colorspace_list = [
    ## colorspace, range
    ["rgb", "L"],
    ["rgb", "F"],
    ["bt601", "L"],
    ["bt601", "F"],
    ["bt709", "L"],
    ["bt709", "F"],
    ["bt2020", "L"],
    ["bt2020", "F"],
]

def get_mat(color_space_i, range_i, color_space_o, range_o, pix_bits=10, coef_fix_bits=10, fine_tuning=False):
    bypass_mat = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    # get input range mat
    if (range_i == "F"):
        input_range_mat = bypass_mat
    elif ((range_i == "L") and (color_space_i == "rgb")): # RGBL
        input_range_mat = getRGBL2FMat(is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    else: # YUVL
        input_range_mat = getYUVL2FMat(is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)

    # get output range mat
    if (range_o == "F"):
        output_range_mat = bypass_mat
    elif ((range_o == "L") and (color_space_o == "rgb")): # RGBL
        output_range_mat = getRGBF2LMat(is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    else: # YUVL
        output_range_mat = getYUVF2LMat(is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)

    # get color space mat
    check_case = ""
    if (color_space_i == color_space_o):
        color_space_mat = bypass_mat
    elif (color_space_i == "rgb"): # R2Y
        color_space_mat = getR2YMat(color_space_o, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
        check_case = "r2y"
    elif (color_space_o == "rgb"): # Y2R
        color_space_mat = getY2RMat(color_space_i, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
        check_case = "y2r"
    else: # Y2Y
        mat0 = getY2RMat(color_space_i, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
        mat1 = getR2YMat(color_space_o, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
        color_space_mat = mat1 @ mat0

    # get final mat
    final_mat = output_range_mat @ color_space_mat @ input_range_mat
    if coef_fix_bits > 0:
        final_mat_float = final_mat.copy()
        final_mat = getFixMat(final_mat, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
        if fine_tuning:
            final_mat = checkFixMat(final_mat_float, final_mat, coef_fix_bits, check_case, range_i, range_o)
    return final_mat

def get_offset(color_space_i, range_i, color_space_o, range_o, csc_mat, pix_bits=10, coef_fix_bits=10):
    yuv_limit_offset = np.array([[16*(2**(pix_bits-8))], [128*(2**(pix_bits-8))], [128*(2**(pix_bits-8))]])
    yuv_full_offset = np.array([[0], [128*(2**(pix_bits-8))], [128*(2**(pix_bits-8))]])
    bypass_offset = np.array([[0], [0], [0]])
    rgb_limit_offset = np.array([[16*(2**(pix_bits-8))], [16*(2**(pix_bits-8))], [16*(2**(pix_bits-8))]])
    rgb_full_offset = np.array([[0], [0], [0]])

    is_input_yuv = ((color_space_i == "bt601") or (color_space_i == "bt709") or (color_space_i == "bt2020"))
    is_output_yuv = ((color_space_o == "bt601") or (color_space_o == "bt709") or (color_space_o == "bt2020"))
    is_input_rgb = (color_space_i == "rgb")
    is_output_rgb = (color_space_o == "rgb")

    if (range_i == "F") and (is_input_yuv):
        input_range_offset = -yuv_full_offset
    elif (range_i == "L") and (is_input_yuv):
        input_range_offset = -yuv_limit_offset
    elif (range_i == "F") and (is_input_rgb):
        input_range_offset = -rgb_full_offset
    elif (range_i == "L") and (is_input_rgb):
        input_range_offset = -rgb_limit_offset
    else:
        input_range_offset = bypass_offset

    if (range_o == "F") and (is_output_yuv):
        output_range_offset = yuv_full_offset
    elif (range_o == "L") and (is_output_yuv):
        output_range_offset = yuv_limit_offset
    elif (range_o == "F") and (is_output_rgb):
        output_range_offset = rgb_full_offset
    elif (range_o == "L") and (is_output_rgb):
        output_range_offset = rgb_limit_offset
    else:
        output_range_offset = bypass_offset

    fix_mat = np.array([[2**coef_fix_bits, 0, 0], [0, 2**coef_fix_bits, 0], [0, 0, 2**coef_fix_bits]])
    final_offset = fix_mat @ output_range_offset + csc_mat @ input_range_offset
    # print(f"input_range_offset={input_range_offset.flatten()}, output_range_offset={output_range_offset.flatten()}, final_offset={final_offset.flatten()}")
    if coef_fix_bits > 0:
        return final_offset.astype(np.int32) # all integers, no need to round
    return final_offset / 2**pix_bits

def check_valid_csc_mode(color_space_i: Optional[str], color_space_o: Optional[str]):
    if color_space_i == None or color_space_o == None:
        return False
    if ((color_space_i == "bt2020") and ((color_space_o == "bt601") or (color_space_o == "bt709"))):
        return False
    if ((color_space_o == "bt2020") and ((color_space_i == "bt601") or (color_space_i == "bt709"))):
        return False
    return True

def parse_csc_mode_str(csc_mode_str):
    ## csc_mode_str: 709l_to_rgbl
    substrs = csc_mode_str.split("_to_")
    if len(substrs) != 2:
        print(f"Error: invalid csc mode string: {csc_mode_str}. use 'xxxf/l_to_xxxf/l' format ...")
        return None, None, None, None

    color_space_i = substrs[0].lower()
    color_space_o = substrs[1].lower()
    range_i = color_space_i[-1].upper()
    range_o = color_space_o[-1].upper()
    if range_i not in ["L", "F"] or range_o not in ["L", "F"]:
        print(f"Error: invalid csc mode string: {csc_mode_str}. use 'xxxf/l_to_xxxf/l' format ...")
        return None, None, None, None

    color_space_i = color_space_i[0:-1]
    color_space_o = color_space_o[0:-1]
    if color_space_i.startswith("601") or color_space_i.startswith("709") or color_space_i.startswith("2020"):
        color_space_i = "bt" + color_space_i
    if color_space_o.startswith("601") or color_space_o.startswith("709") or color_space_o.startswith("2020"):
        color_space_o = "bt" + color_space_o
    if color_space_i not in ["rgb", "bt601", "bt709", "bt2020"] or color_space_o not in ["rgb", "bt601", "bt709", "bt2020"]:
        print(f"Error: invalid csc mode string: {csc_mode_str}. input({color_space_i}) or output({color_space_o}) color space is not supported!")
        return None, None, None, None
    return color_space_i, range_i, color_space_o, range_o

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--print_all", action="store_true", help="print all csc mode coefs")
    parser.add_argument("-c", "--fix_check", action="store_true", help="check and do fine tuning for the fixed matrix output")
    parser.add_argument("-f", "--out_file", type=str, default="", help="dump all csc mode coefs to a file when '-a' is set")
    parser.add_argument("-p", "--platform", type=str, default="RK3572", help="RK3572/RK3576")
    parser.add_argument("-m", "--mode", type=str, default="", help="a single csc mode, like: '601f_to_rgbl/rgbf_to_2020f' ...)")
    parser.add_argument("-b", "--fix_bits", type=int, default=10, help="the precision bits (8/10/13)")
    parser.add_argument("-d", "--depth", type=int, default=10, help="the pixel depth bits (8/10)")
    parser.print_usage()
    args, _  = parser.parse_known_args()

    pix_bits = args.depth
    coef_fix_bits = args.fix_bits
    if coef_fix_bits > 0 and coef_fix_bits < pix_bits:
        print(f"Error: precision bits({coef_fix_bits}) should >= pixel_depth({pix_bits})!")
        exit(-1)
    if args.mode:
        csc_mode = args.mode.lower()
    else:
        csc_mode = "print_all"
        args.print_all = True
    platform = args.platform.lower()
    out_file = args.out_file if args.out_file else f"{platform}_csc_coef_for_%dbit_pix_%dbits_coef.txt" % (pix_bits, coef_fix_bits)
    print(f" - get platform: {platform}")
    print(f" - get pixel_bits: {pix_bits}, coefs_bits: {coef_fix_bits}, fix_check: {args.fix_check}")
    print(f" - get out_file: {out_file}")
    print(f" - get csc_mode: {csc_mode}")
    if coef_fix_bits not in [0, 8, 10, 13]:
        print(f"Warning: precision bits = {coef_fix_bits} is not a standard value ([0, 8, 10, 13])!")

    float_fmt = {'float_kind': lambda x: f"{x:.6f}"} # fsor float data format-string
    if csc_mode == "print_all":
        max_abs_coef = 0
        max_abs_offset = 0
        max_coef_idx = (0, 0)
        max_offset_idx = (0, 0)
        count = 0
        fp = open(out_file, "w")
        for idx_i in range(len(g_supported_colorspace_list)):
            for idx_o in range(len(g_supported_colorspace_list)):
                if idx_i == idx_o:
                    continue

                color_space_i = g_supported_colorspace_list[idx_i][0]
                color_space_o = g_supported_colorspace_list[idx_o][0]
                range_i = g_supported_colorspace_list[idx_i][1]
                range_o = g_supported_colorspace_list[idx_o][1]
                is_valid_mode = check_valid_csc_mode(color_space_i, color_space_o)
                if not is_valid_mode:
                    continue

                mat = get_mat(color_space_i, range_i, color_space_o, range_o, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, fine_tuning=args.fix_check)
                offset = get_offset(color_space_i, range_i, color_space_o, range_o, mat, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
                print(f"matrix_{color_space_i}{range_i}_to_{color_space_o}{range_o} = {np.array2string(mat.flatten(), separator=', ', formatter=float_fmt)}")
                print(f"offset_{color_space_i}{range_i}_to_{color_space_o}{range_o} = {np.array2string(offset.flatten(), separator=', ', formatter=float_fmt)}")
                fp.write(f"matrix_{color_space_i}{range_i}_to_{color_space_o}{range_o} = {np.array2string(mat.flatten(), separator=', ', formatter=float_fmt)}\n")
                fp.write(f"offset_{color_space_i}{range_i}_to_{color_space_o}{range_o} = {np.array2string(offset.flatten(), separator=', ', formatter=float_fmt)}\n")
                fp.write("\n")

                count += 1
                max_coef = max(abs(mat.max()), abs(mat.min()))
                max_offset = max(abs(offset.max()), abs(offset.min()))
                max_abs_coef = max(max_abs_coef, max_coef)
                max_abs_offset = max(max_abs_offset, max_offset)
                max_coef_idx = (idx_i, idx_o) if max_coef == max_abs_coef else max_coef_idx
                max_offset_idx = (idx_i, idx_o) if max_offset == max_abs_offset else max_offset_idx

        fp.close()
        print(f"write {count} group of csc coefs to: {out_file}")
        print(f"max_abs_coef = {max_abs_coef} ({g_supported_colorspace_list[max_coef_idx[0]][0]}{g_supported_colorspace_list[max_coef_idx[0]][1]}_to_{g_supported_colorspace_list[max_coef_idx[1]][0]}{g_supported_colorspace_list[max_coef_idx[1]][1]})")
        print(f"max_abs_offset = {max_abs_offset} ({g_supported_colorspace_list[max_offset_idx[0]][0]}{g_supported_colorspace_list[max_offset_idx[0]][1]}_to_{g_supported_colorspace_list[max_offset_idx[1]][0]}{g_supported_colorspace_list[max_offset_idx[1]][1]})")
    else:
        color_space_i, range_i, color_space_o, range_o = parse_csc_mode_str(csc_mode)
        is_valid_mode = check_valid_csc_mode(color_space_i, color_space_o)
        if is_valid_mode:
            mat = get_mat(color_space_i, range_i, color_space_o, range_o, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, fine_tuning=args.fix_check)
            offset = get_offset(color_space_i, range_i, color_space_o, range_o, mat, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
            print(f"matrix_{color_space_i}{range_i}_to_{color_space_o}{range_o} = {np.array2string(mat.flatten(), separator=', ', formatter=float_fmt)}")
            print(f"offset_{color_space_i}{range_i}_to_{color_space_o}{range_o} = {np.array2string(offset.flatten(), separator=', ', formatter=float_fmt)}")
            print(f"matrix_sum: {np.sum(mat[0,:])} / {np.sum(mat)}")
        else:
            print(f"invalid csc mode: {color_space_i}_to_{color_space_o}!")

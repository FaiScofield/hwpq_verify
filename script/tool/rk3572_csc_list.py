import sys
import os
import numpy as np
from rkvop_csc import *

def get_mat(color_space_i, range_i, color_space_o, range_o, pix_bits=10, coef_fix_bits=10):
    bypass_mat = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    # get input range mat
    if (range_i == "F"):
        input_range_mat = bypass_mat
    elif ((range_i == "L") and (color_space_i == "RGB")):
        input_range_mat = getRGBL2FMat(is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    else:
        input_range_mat = getYUVL2FMat(is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)

    # get output range mat
    if (range_o == "F"):
        output_range_mat = bypass_mat
    elif ((range_o == "L") and (color_space_o == "RGB")):
        output_range_mat = getRGBF2LMat(is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    else:
        output_range_mat = getYUVF2LMat(is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)

    # get color space mat
    if (color_space_i == color_space_o):
        color_space_mat = bypass_mat
    elif (color_space_i == "RGB"):
        color_space_mat = getR2YMat(color_space_o, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
    elif (color_space_o == "RGB"):
        color_space_mat = getY2RMat(color_space_i, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
    else:
        mat0 = getY2RMat(color_space_i, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
        mat1 = getR2YMat(color_space_o, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
        color_space_mat = mat1 @ mat0

    # get final mat
    final_mat = output_range_mat @ color_space_mat @ input_range_mat
    final_mat_fix = getFixMat(final_mat, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)

    return final_mat_fix

def get_offset(color_space_i, range_i, color_space_o, range_o, csc_mat, pix_bits=10, coef_fix_bits=10):
    yuv_limit_offset = np.array([[16*(2**(pix_bits-8))], [128*(2**(pix_bits-8))], [128*(2**(pix_bits-8))]])
    yuv_full_offset = np.array([[0], [128*(2**(pix_bits-8))], [128*(2**(pix_bits-8))]])
    bypass_offset = np.array([[0], [0], [0]])
    rgb_limit_offset = np.array([[16*(2**(pix_bits-8))], [16*(2**(pix_bits-8))], [16*(2**(pix_bits-8))]])
    rgb_full_offset = np.array([[0], [0], [0]])

    is_input_yuv = ((color_space_i == "bt601") or (color_space_i == "bt709") or (color_space_i == "bt2020"))
    is_output_yuv = ((color_space_o == "bt601") or (color_space_o == "bt709") or (color_space_o == "bt2020"))
    is_input_rgb = (color_space_i == "RGB")
    is_output_rgb = (color_space_o == "RGB")

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
    return final_offset.astype(np.int32)

if __name__ == '__main__':
    supported_list = [
        ["RGB", "L"],
        ["RGB", "F"],
        ["bt601", "L"],
        ["bt601", "F"],
        ["bt709", "L"],
        ["bt709", "F"],
        ["bt2020", "L"],
        ["bt2020", "F"],
    ]
    pix_bits = 10
    coef_fix_bits = 10 if len(sys.argv) < 2 else int(sys.argv[1]) # 10 / 13
    platform = "rk3572" if len(sys.argv) < 3 else sys.argv[2].lower() # rk3572 / rk3576
    assert(coef_fix_bits == 10 or coef_fix_bits == 13)
    print(f" - get coef_fix_bits: {coef_fix_bits}")
    print(f" - get platform: {platform}")

    max_abs_coef = 0
    max_abs_offset = 0
    max_coef_idx = (0, 0)
    max_offset_idx = (0, 0)

    out_file = f"{platform}_csc_coef_for_%dbit_pix_%dbits_coef.txt" % (pix_bits, coef_fix_bits)
    fp = open(out_file, "w")
    for idx_i in range(len(supported_list)):
        for idx_o in range(len(supported_list)):
            if idx_i == idx_o:
                continue

            color_space_i = supported_list[idx_i][0]
            color_space_o = supported_list[idx_o][0]
            range_i = supported_list[idx_i][1]
            range_o = supported_list[idx_o][1]

            if ((color_space_i == "bt2020") and ((color_space_o == "bt601") or (color_space_o == "bt709"))):
                continue
            if ((color_space_o == "bt2020") and ((color_space_i == "bt601") or (color_space_i == "bt709"))):
                continue

            mat = get_mat(color_space_i, range_i, color_space_o, range_o, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
            offset = get_offset(color_space_i, range_i, color_space_o, range_o, mat, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
            print(f"matrix_{color_space_i}_{range_i}_{color_space_o}_{range_o} = {np.array2string(mat.flatten(), separator=', ')}")
            print(f"offset_{color_space_i}_{range_i}_{color_space_o}_{range_o} = {np.array2string(offset.flatten(), separator=', ')}")

            fp.write(f"matrix_{color_space_i}_{range_i}_{color_space_o}_{range_o} = {np.array2string(mat.flatten(), separator=', ')}\n")
            fp.write(f"offset_{color_space_i}_{range_i}_{color_space_o}_{range_o} = {np.array2string(offset.flatten(), separator=', ')}\n")
            fp.write("\n")

            max_coef = max(abs(mat.max()), abs(mat.min()))
            max_offset = max(abs(offset.max()), abs(offset.min()))
            max_abs_coef = max(max_abs_coef, max_coef)
            max_abs_offset = max(max_abs_offset, max_offset)
            max_coef_idx = (idx_i, idx_o) if max_coef == max_abs_coef else max_coef_idx
            max_offset_idx = (idx_i, idx_o) if max_offset == max_abs_offset else max_offset_idx

    fp.close()
    print(f"csc coef list written to: {out_file}")
    print(f"max_abs_coef = {max_abs_coef} ({supported_list[max_coef_idx[0]][0]}_{supported_list[max_coef_idx[0]][1]}_{supported_list[max_coef_idx[1]][0]}_{supported_list[max_coef_idx[1]][1]})")
    print(f"max_abs_offset = {max_abs_offset} ({supported_list[max_offset_idx[0]][0]}_{supported_list[max_offset_idx[0]][1]}_{supported_list[max_offset_idx[1]][0]}_{supported_list[max_offset_idx[1]][1]})")

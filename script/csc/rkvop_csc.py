import numpy as np
import os
import sys
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Get csc matrix')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='input color space, e.g. bt601L / bt709F / 2020 (suffix L: limited range, F: full range, default: F)')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='output color space, e.g. bt601F; if not set, print the y2r / r2y coefs of the input color space')
    parser.add_argument('-b', '--fix_bits', type=int, default=10,
                        help='the fixed-point precision bits of the coefs (8/10/13), default: 10')
    args = parser.parse_args()
    return args

def getM_rgb2XYZ(pri_xyz):
    pri_xyz = np.array(pri_xyz).T
    z = 1 - np.sum(pri_xyz, axis=0)
    pri_xyz = np.vstack([pri_xyz, z])
    w = pri_xyz[:, 3]
    w = w / w[1]
    rgb = pri_xyz[:3, :3]
    gain = np.linalg.inv(rgb) @ w
    M_rgb2XYZ = rgb @ np.diag(gain)
    return M_rgb2XYZ

def getMatByCoord(rgbw_coord):
    pri_xyz = list(rgbw_coord)
    M_rgb2XYZ = getM_rgb2XYZ(pri_xyz)

    Y_coef = M_rgb2XYZ[1, :]
    cb_coef = (1 - Y_coef[2]) * 2
    cr_coef = (1 - Y_coef[0]) * 2
    cb_line_coef = np.array([-Y_coef[0], -Y_coef[1], 1 - Y_coef[2]]) / cb_coef
    cr_line_coef = np.array([1 - Y_coef[0], -Y_coef[1], -Y_coef[2]]) / cr_coef

    Mat_r2y = np.vstack([Y_coef, cb_line_coef, cr_line_coef])
    Mat_y2r = np.linalg.inv(Mat_r2y)

    return Mat_r2y, Mat_y2r


def getXYbyColorSpace(color_space):
    if color_space == 'bt709' or color_space == 'srgb':
        r_xy = [0.6400, 0.3300]  # z=0.03
        g_xy = [0.3000, 0.6000]  # z=0.10
        b_xy = [0.1500, 0.0600]  # z=0.79
        w_xy = [0.3127, 0.3290]  # z=0.3582. why [0.95047， 1.0， 1.08883] ?
    elif color_space == 'bt2020' or color_space == 'bt2100':
        r_xy = [0.7080, 0.2920]
        g_xy = [0.1700, 0.7970]
        b_xy = [0.1310, 0.0460]
        w_xy = [0.3127, 0.3290]  # D65
    elif color_space == 'bt601':  # or color_space == 'ntsc':
        r_xy = [0.6700, 0.3300]
        g_xy = [0.2100, 0.7100]
        b_xy = [0.1400, 0.0800]
        w_xy = [0.3101, 0.3162]  # illuminant C
    # elif color_space == 'bt601-625':
    #     r_xy = [0.640, 0.330]
    #     g_xy = [0.290, 0.600]
    #     b_xy = [0.150, 0.060]
    #     w_xy = [0.3127, 0.3290]  # D65
    # elif color_space == 'bt601-525':
    #     r_xy = [0.630, 0.340]
    #     g_xy = [0.310, 0.595]
    #     b_xy = [0.155, 0.070]
    #     w_xy = [0.3127, 0.3290]  # D65
    # elif color_space == 'adobergb':
    #     r_xy = [0.640, 0.330]
    #     g_xy = [0.210, 0.710]
    #     b_xy = [0.150, 0.060]
    #     w_xy = [0.3127, 0.3290] # D65
    elif color_space == 'dci-p3' or color_space == 'dci-p3-theater':
        r_xy = [0.6800, 0.3200]
        g_xy = [0.2650, 0.6900]
        b_xy = [0.1500, 0.0600]
        # w_xy = [0.32168, 0.33767] # Cinema, p3-D60(K=6000)
        w_xy = [0.3140, 0.3510] # Theater, p3-DCI(K=6300)
        # w_xy = [0.3127, 0.3290] # Display, p3-D65(K=6504)
    elif color_space == 'display-p3' or color_space == 'dci-p3-d65':
        r_xy = [0.6800, 0.3200]
        g_xy = [0.2650, 0.6900]
        b_xy = [0.1500, 0.0600]
        # w_xy = [0.32168, 0.33767] # Cinema, p3-D60(K=6000)
        # w_xy = [0.3140, 0.3510] # Theater, p3-DCI(K=6300)
        w_xy = [0.3127, 0.3290] # Display, p3-D65(K=6504)
    # elif color_space == 'dci-p3+':
    #     r_xy = [0.7400, 0.2700]
    #     g_xy = [0.2200, 0.2700]
    #     b_xy = [0.0900, -0.0900]
    #     w_xy = [0.3140, 0.3510]
    else:
        print("Error: color space not supported")
        r_xy = [0, 0]
        g_xy = [0, 0]
        b_xy = [0, 0]
        w_xy = [0, 0]

    return r_xy, g_xy, b_xy, w_xy


def getFixMat(mat, pix_bits=10, coef_fix_bits=10):
    # mat_fix = np.round(mat * (2**coef_fix_bits)).astype(np.int32) # round to nearest even integer
    mat_fix = (mat * (2**coef_fix_bits) + np.sign(mat) * 0.5).astype(np.int32)  # round to nearest integer
    return mat_fix


def checkFixMat(
    mat_float: np.ndarray,
    mat_fix: np.ndarray,
    coef_fix_bits: int,
    check_case: str = "",
    range_i: str = "F",
    range_o: str = "F",
):
    assert coef_fix_bits > 0

    target_denorms = np.ones(3) * 2**coef_fix_bits
    if range_i == "F" and range_o == "L":
        target_denorms[0] = 220/255 * (2**coef_fix_bits - 1)
        target_denorms[1] = 225/255 * (2**coef_fix_bits - 1)
    elif range_i == "L" and range_o == "F":
        target_denorms[0] = 255/220 * (2**coef_fix_bits - 1)
        target_denorms[1] = 255/225 * (2**coef_fix_bits - 1)
    target_denorms = (target_denorms + 0.5).astype(np.int32)
    target_denorms[2] = target_denorms[1]

    org_mat_fix = mat_fix.copy()
    mat_float = mat_float * (2**coef_fix_bits)
    check_case = check_case.lower()

    if check_case == "r2y":
        target_denorms[1] = target_denorms[2] = 0
        denorms = np.sum(mat_fix, axis=1)
        updated = False

        for i in range(3):
            if denorms[i] != target_denorms[i]:
                print(f"Warning: denorms[{i}] = {denorms[i]} != {target_denorms[i]}")
                delta = target_denorms[i] - denorms[i]
                j = np.argmin(np.abs(mat_fix[i, :] + delta - mat_float[i, :]))
                mat_fix[i, j] += delta
                updated = True
        if updated:
            print(f"fine-tunig for R2Y, original mat: {np.array2string(org_mat_fix.flatten(), separator=', ')}")
            print(f"fine-tunig for R2Y, updated  mat: {np.array2string(mat_fix.flatten(), separator=', ')}")
    elif check_case == "y2r":
        if mat_fix[0, 0] != target_denorms[0]:
            print(f"NOTE: Update coef[0,0] = {mat_fix[0, 0]} => {target_denorms[0]}, since RY2 case!")
            mat_fix[0, 0] = target_denorms[0]
        if mat_fix[1, 0] != target_denorms[0]:
            print(f"NOTE: Update coef[1,0] = {mat_fix[1, 0]} => {target_denorms[0]}, since RY2 case!")
            mat_fix[1, 0] = target_denorms[0]
        if mat_fix[2, 0] != target_denorms[0]:
            print(f"NOTE: Update coef[2,0] = {mat_fix[2, 0]} => {target_denorms[0]}, since RY2 case!")
            mat_fix[2, 0] = target_denorms[0]
        if mat_fix[0, 1] != 0:
            print(f"NOTE: Update coef[0,1] = {mat_fix[0, 1]} => 0, since RY2 case!")
            mat_fix[0, 1] = 0
        if mat_fix[2, 2] != 0:
            print(f"NOTE: Update coef[1,0] = {mat_fix[2, 2]} => 0, since RY2 case!")
            mat_fix[2, 2] = 0

    return mat_fix

def getY2RMat(color_space, is_float=True, pix_bits=10, coef_fix_bits=10, range="F"):
    rgbw_coord = getXYbyColorSpace(color_space)
    Mat_r2y, Mat_y2r = getMatByCoord(rgbw_coord)
    if is_float:
        Mat_y2r = Mat_y2r.astype(np.float32)

    if (range == "L"):
        y_ratio = (235-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
        uv_ratio = (240-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
        mat_l2f = np.array([[1/y_ratio, 0, 0], [0, 1/uv_ratio, 0], [0, 0, 1/uv_ratio]])
        Mat_y2r = Mat_y2r @ mat_l2f

    if (is_float == False):
        Mat_y2r = getFixMat(Mat_y2r, pix_bits, coef_fix_bits)

    return Mat_y2r

def getR2YMat(color_space, is_float=True, pix_bits=10, coef_fix_bits=10, range="F"):
    rgbw_coord = getXYbyColorSpace(color_space)
    Mat_r2y, Mat_y2r = getMatByCoord(rgbw_coord)
    if is_float:
        Mat_r2y = Mat_r2y.astype(np.float32)

    if (range == "L"):
        y_ratio = (235-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
        uv_ratio = (240-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
        mat_f2l = np.array([[y_ratio, 0, 0], [0, uv_ratio, 0], [0, 0, uv_ratio]])
        Mat_r2y = mat_f2l @ Mat_r2y

    if (is_float == False):
        Mat_r2y = getFixMat(Mat_r2y, pix_bits, coef_fix_bits)

    return Mat_r2y

def getRGBL2FMat(is_float=True, pix_bits=10, coef_fix_bits=10):
    rgb_ratio = (235-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
    mat_rgb_l2f = np.array([[1/rgb_ratio, 0, 0], [0, 1/rgb_ratio, 0], [0, 0, 1/rgb_ratio]])

    if (is_float == False):
        mat_rgb_l2f = getFixMat(mat_rgb_l2f, pix_bits, coef_fix_bits)

    return mat_rgb_l2f

def getRGBF2LMat(is_float=True, pix_bits=10, coef_fix_bits=10):
    rgb_ratio = (235-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
    mat_rgb_f2l = np.array([[rgb_ratio, 0, 0], [0, rgb_ratio, 0], [0, 0, rgb_ratio]])

    if (is_float == False):
        mat_rgb_f2l = getFixMat(mat_rgb_f2l, pix_bits, coef_fix_bits)

    return mat_rgb_f2l

def getYUVL2FMat(is_float=True, pix_bits=10, coef_fix_bits=10):
    y_ratio = (235-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
    uv_ratio = (240-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
    mat_yuv_l2f = np.array([[1/y_ratio, 0, 0], [0, 1/uv_ratio, 0], [0, 0, 1/uv_ratio]])

    if (is_float == False):
        mat_yuv_l2f = getFixMat(mat_yuv_l2f, pix_bits, coef_fix_bits)

    return mat_yuv_l2f

def getYUVF2LMat(is_float=True, pix_bits=10, coef_fix_bits=10):
    y_ratio = (235-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
    uv_ratio = (240-16) * (2**(pix_bits-8)) / (2**pix_bits - 1)
    mat_yuv_f2l = np.array([[y_ratio, 0, 0], [0, uv_ratio, 0], [0, 0, uv_ratio]])

    if (is_float == False):
        mat_yuv_f2l = getFixMat(mat_yuv_f2l, pix_bits, coef_fix_bits)

    return mat_yuv_f2l


# 解析色域参数：<色域名>[L|F]，L 表示 limited range，F 表示 full range，未指定时默认为 F
def parseColorSpace(spec):
    spec = spec.strip().lower()
    if spec and spec[-1] in ("l", "f"):
        range_ = spec[-1].upper()
        name = spec[:-1]
    else:
        range_ = "F"
        name = spec

    # 兼容 601 / 709 / 2020 等简写，以及 rec* / bt2100 等别名
    alias = {
        "601": "bt601",
        "709": "bt709",
        "2020": "bt2020",
        "2100": "bt2020",
        "bt2100": "bt2020",
        "rec601": "bt601",
        "rec709": "bt709",
        "rec2020": "bt2020",
    }
    name = alias.get(name, name)

    supported = ("bt601", "bt709", "srgb", "bt2020", "dci-p3", "dci-p3-theater", "display-p3", "dci-p3-d65")
    if name not in supported:
        print(f"Error: color space '{spec}' is not supported!")
        print(f"supported: {', '.join(supported)}, e.g. bt709L / 601F")
        sys.exit(1)

    return name, range_


if __name__ == '__main__':
    args = get_args()

    pix_bits = 10
    coef_fix_bits = args.fix_bits
    if coef_fix_bits <= 0:
        print(f"Error: invalid fix_bits({coef_fix_bits}), should be > 0!")
        sys.exit(1)

    cs_in, range_in = parseColorSpace(args.input)
    tag_in = (cs_in[2:] if cs_in.startswith("bt") else cs_in) + range_in

    if args.output:
        cs_out, range_out = parseColorSpace(args.output)

        # 601 与 2020 之间的转换是非法的
        if {cs_in, cs_out} == {"bt601", "bt2020"}:
            print(f"Error: csc between {cs_in} and {cs_out} is illegal!")
            sys.exit(1)

        tag_out = (cs_out[2:] if cs_out.startswith("bt") else cs_out) + range_out

        # 计算输入色域到输出色域的转换矩阵与 offset
        mat_cvt = getFixMat(
            getR2YMat(cs_out, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range=range_out)
            @ getY2RMat(cs_in, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range=range_in),
            pix_bits=pix_bits,
            coef_fix_bits=coef_fix_bits,
        )
        offset_in = np.array([[-64], [-512], [-512]]) if range_in == "L" else np.array([[0], [-512], [-512]])
        offset_out = np.array([[64], [512], [512]]) if range_out == "L" else np.array([[0], [512], [512]])
        offset_cvt = mat_cvt @ offset_in + offset_out * (2**coef_fix_bits)

        print(f"mat_{tag_in}_2_{tag_out}:\n\t", mat_cvt.flatten(), "\n\t", offset_cvt.flatten())
    else:
        # 只指定输入色域时，打印该色域的 y2r / r2y 转换系数
        mat_y2r = getY2RMat(cs_in, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range=range_in)
        mat_r2y = getR2YMat(cs_in, is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range=range_in)
        print(f"mat_y2r_{tag_in} (float):\n\t", mat_y2r.flatten())
        print(f"mat_y2r_{tag_in} (fix {coef_fix_bits} bits):\n\t",
              getFixMat(mat_y2r, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits).flatten())
        print(f"mat_r2y_{tag_in} (float):\n\t", mat_r2y.flatten())
        print(f"mat_r2y_{tag_in} (fix {coef_fix_bits} bits):\n\t",
              getFixMat(mat_r2y, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits).flatten())

    # read yuv from file
    if False:
        yuv_path = "F://log_dir//plane_csc//Moutain_3840x2160_yuv444p.yuv"
        print("read yuv from file ", yuv_path)
        yuv_file = open(yuv_path, "rb")
        yuv_data = yuv_file.read()
        yuv_file.close()
        img_w = 3840
        img_h = 2160

        y_ = np.frombuffer(yuv_data[0:img_w*img_h], dtype=np.uint8).reshape(1, img_w*img_h)
        u_ = np.frombuffer(yuv_data[img_w*img_h:img_w*img_h+img_w*img_h], dtype=np.uint8).reshape(1, img_w*img_h)
        v_ = np.frombuffer(yuv_data[img_w*img_h+img_w*img_h:img_w*img_h+2*img_w*img_h], dtype=np.uint8).reshape(1, img_w*img_h)
        yuv_vec = np.concatenate((y_, u_, v_), axis=0).astype(np.int32)
        yuv_vec = yuv_vec * 4

        # 使用 -i / -o 指定的输入色域到输出色域的转换系数（需要指定 -o）
        yuv_601F = mat_cvt @ yuv_vec + offset_cvt @ np.ones([1, img_w*img_h])
        yuv_601F = np.clip(yuv_601F / (2**coef_fix_bits) / 4, 0, 255)
        print("coef:")
        print(mat_cvt)
        print("offset:")
        print(offset_cvt)

        dst_y_ = yuv_601F[0, 0:img_w*img_h].astype(np.uint8)
        dst_u_ = yuv_601F[1, 0:img_w*img_h].astype(np.uint8)
        dst_v_ = yuv_601F[2, 0:img_w*img_h].astype(np.uint8)
        dst_yuv_data = np.concatenate((dst_y_, dst_u_, dst_v_), axis=0)

        dst_yuv_path = "F://log_dir//plane_csc//Moutain_3840x2160_yuv444p_bt601F.yuv"
        dst_yuv_file = open(dst_yuv_path, "wb")
        dst_yuv_file.write(dst_yuv_data)
        dst_yuv_file.close()

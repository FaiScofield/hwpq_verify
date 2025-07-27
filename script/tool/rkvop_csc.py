import numpy as np
import os
import sys
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Get csc matrix')
    parser.add_argument('-c', '--color_space', type=str, default='bt709', help='color space')
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

def getMat(r_xy, g_xy, b_xy, w_xy):

    pri_xyz = [r_xy, g_xy, b_xy, w_xy]
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
    if color_space == 'bt709':
        r_xy = [0.640, 0.330]
        g_xy = [0.300, 0.600]
        b_xy = [0.150, 0.060]
        w_xy = [0.3127, 0.3290]
    elif color_space == 'bt2020':
        r_xy = [0.708, 0.292]
        g_xy = [0.170, 0.797]
        b_xy = [0.131, 0.046]
        w_xy = [0.3127, 0.3290]
    elif color_space == 'bt601':
        r_xy = [0.670, 0.330]
        g_xy = [0.210, 0.710]
        b_xy = [0.140, 0.080]
        w_xy = [0.3101, 0.3162]
    else:
        print("Error: color space not supported")
        r_xy = [0, 0]
        g_xy = [0, 0]
        b_xy = [0, 0]
        w_xy = [0, 0]

    return r_xy, g_xy, b_xy, w_xy

def getFixMat(mat, pix_bits=10, coef_fix_bits=10):
    mat_fix = np.round(mat * (2**coef_fix_bits)).astype(np.int32)
    return mat_fix

def getY2RMat(color_space, is_float=True, pix_bits=10, coef_fix_bits=10, range="F"):
    r_xy, g_xy, b_xy, w_xy = getXYbyColorSpace(color_space)
    Mat_r2y, Mat_y2r = getMat(r_xy, g_xy, b_xy, w_xy)
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

def getR2YMat(color_space, is_float=True, pix_bits=10, coef_fix_bits=10, range="F"):
    r_xy, g_xy, b_xy, w_xy = getXYbyColorSpace(color_space)
    Mat_r2y, Mat_y2r = getMat(r_xy, g_xy, b_xy, w_xy)
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

if __name__ == '__main__':
    r_xy_bt709, g_xy_bt709, b_xy_bt709, w_xy_bt709 = getXYbyColorSpace("bt709")
    r_xy_bt2020, g_xy_bt2020, b_xy_bt2020, w_xy_bt2020 = getXYbyColorSpace("bt2020")
    r_xy_bt601, g_xy_bt601, b_xy_bt601, w_xy_bt601 = getXYbyColorSpace("bt601")

    pix_bits = 10
    coef_fix_bits = 10

    Mat_r2y_bt601F = getR2YMat("bt601", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
    Mat_r2y_bt601L = getR2YMat("bt601", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="L")
    Mat_y2r_bt601F = getY2RMat("bt601", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
    Mat_y2r_bt601L = getY2RMat("bt601", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="L")

    Mat_r2y_bt709F = getR2YMat("bt709", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
    Mat_r2y_bt709L = getR2YMat("bt709", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="L")
    Mat_y2r_bt709F = getY2RMat("bt709", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
    Mat_y2r_bt709L = getY2RMat("bt709", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="L")

    Mat_r2y_bt2020F = getR2YMat("bt2020", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
    Mat_r2y_bt2020L = getR2YMat("bt2020", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="L")
    Mat_y2r_bt2020F = getY2RMat("bt2020", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="F")
    Mat_y2r_bt2020L = getY2RMat("bt2020", is_float=True, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits, range="L")

    Mat_601L_2_601F  = getFixMat(Mat_r2y_bt601F @ Mat_y2r_bt601L, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    Mat_601F_2_601F  = getFixMat(Mat_r2y_bt601F @ Mat_y2r_bt601F, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    Mat_709L_2_601F  = getFixMat(Mat_r2y_bt601F @ Mat_y2r_bt709L, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    Mat_709F_2_601F  = getFixMat(Mat_r2y_bt601F @ Mat_y2r_bt709F, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    Mat_2020L_2_601F = getFixMat(Mat_r2y_bt601F @ Mat_y2r_bt2020L, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    Mat_2020F_2_601F = getFixMat(Mat_r2y_bt601F @ Mat_y2r_bt2020F, pix_bits=pix_bits, coef_fix_bits=coef_fix_bits)
    offset_601L_2_601F = Mat_601L_2_601F @ np.array([[-64], [-512], [-512]]) + np.array([[0], [512], [512]])*(2**10)
    offset_601F_2_601F = Mat_601F_2_601F @ np.array([[0], [-512], [-512]]) + np.array([[0], [512], [512]])*(2**10)
    offset_709L_2_601F = Mat_709L_2_601F @ np.array([[-64], [-512], [-512]]) + np.array([[0], [512], [512]])*(2**10)
    offset_709F_2_601F = Mat_709F_2_601F @ np.array([[0], [-512], [-512]]) + np.array([[0], [512], [512]])*(2**10)
    offset_2020L_2_601F = Mat_2020L_2_601F @ np.array([[-64], [-512], [-512]]) + np.array([[0], [512], [512]])*(2**10)
    offset_2020F_2_601F = Mat_2020F_2_601F @ np.array([[0], [-512], [-512]]) + np.array([[0], [512], [512]])*(2**10)
    print("mat_601L_2_601F\n", Mat_601L_2_601F, "\n", offset_601L_2_601F)
    print("mat_601F_2_601F\n", Mat_601F_2_601F, "\n", offset_601F_2_601F)
    print("mat_709L_2_601F\n", Mat_709L_2_601F, "\n", offset_709L_2_601F)
    print("mat_709F_2_601F\n", Mat_709F_2_601F, "\n", offset_709F_2_601F)
    print("mat_2020L_2_601F\n", Mat_2020L_2_601F, "\n", offset_2020L_2_601F)
    print("mat_2020F_2_601F\n", Mat_2020F_2_601F, "\n", offset_2020F_2_601F)

    # read yuv from file
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

    # convert from bt709L to bt601F
    mat_cvt = Mat_709L_2_601F
    offset_cvt = offset_709L_2_601F
    yuv_601F = mat_cvt @ yuv_vec + offset_cvt @ np.ones([1, img_w*img_h])
    yuv_601F = np.clip(yuv_601F / 1024 / 4, 0, 255)
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

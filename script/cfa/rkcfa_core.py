'''
Copyright    : Copyright (c) 2024 by Rockchip. All right reserved.
Filename     : rkcfa_core.py
Creacted By  : vance.wu@rock-chips.com
Creacted Date: 2025-01-17
Description  : 
Modify Date  : 2026-03-09
'''

import os
import sys
import argparse
import numpy as np
import cv2
from PIL import Image, ImageFilter

##### platform info #####
class RkCfaPlatformInfo:
    def __init__(self, name, enum_idx, pattern, ed_coefs=[[0, 0, 7], [2, 4, 1]], ed_factor=16):
        self.name = name
        self.enum_idx = enum_idx
        self.pattern = np.array(pattern, dtype=np.uint8)
        self.ed_coefs = np.array(ed_coefs, dtype=np.int8)
        self.ed_factor = ed_factor

    def get_norm_ed_coefs(self, reshape21D=False):
        norm_coefs = self.ed_coefs.astype(np.float32) / self.ed_factor
        if reshape21D:
            pad = self.ed_coefs.shape[1] // 2
            norm_coefs = norm_coefs.reshape(-1)[pad+1:]
        return norm_coefs


g_cfa_support_platforms = {
    # name, enum_idx(same to 'rkcfa_platform'), cfa_pattern(2D array, 0=R/1=G/2=B/3=W/4=Gray), ed_coefs(2D array), ed_factor
    'common':   RkCfaPlatformInfo('COMMON',    0, [[4]],                            [[0,0,0,14,0], [0,6,10,2,0]], 32),
    'ec060kc1': RkCfaPlatformInfo('EC060KC1',  1, [[0,1,2], [1,2,0], [2,0,1]],      [[0,0,0, 5,3], [1,13,3,4,3]], 32),
    'ec060kh3': RkCfaPlatformInfo('EC060KH3',  2, [[1,2,2,0,0,1], [0,0,1,1,2,2]],   [[0,0,0,11,0], [0,5,11,5,0]], 32),
    'ec060kh4': RkCfaPlatformInfo('EC060KH4',  3, [[1,2,2,0,0,1], [0,0,1,1,2,2]],   [[0,0,0,11,0], [0,5,11,5,0]], 32),
    'ec070kc1': RkCfaPlatformInfo('EC070KC1',  4, [[1,2,0], [2,0,1], [0,1,2]],      [[0,0,0,5,3],  [1,13,3,4,3]], 32),
    'ec078kh3': RkCfaPlatformInfo('EC078KH3',  5, [[1,2,2,0,0,1], [0,0,1,1,2,2]],   [[0,0,0,11,0], [0,5,11,5,0]], 32),
    'ec078kh6': RkCfaPlatformInfo('EC078KH6',  6, [[1,2,0], [2,0,1], [0,1,2]],      [[0,0,0,5,3],  [1,13,3,4,3]], 32),
    'ec103kh3': RkCfaPlatformInfo('EC103KH3',  7, [[0,2,1], [1,0,2], [2,1,0]],      [[0,0,0,5,2],  [3,2,6,13,1]], 32),
    'ec103th2': RkCfaPlatformInfo('EC103TH2',  8, [[0,2,1], [1,0,2], [2,1,0]],      [[0,0,0,5,2],  [3,2,6,13,1]], 32),
    'opm103e5': RkCfaPlatformInfo('OPM103E5',  9, [[2,3],[1,0]],                    [[0,0,0,5,16], [1,3,3,3,1]],  32),
    'opm133c1': RkCfaPlatformInfo('OPM133C1', 10, [[2,3],[1,0]],                    [[0,0,0,5,16], [1,3,3,3,1]],  32),
    }

##### global LUTs #####
def load_rkcfa_dither_matrix_256x256(filename):
    matrix = np.zeros((256, 256), dtype=np.uint8)
    with open(filename, 'rt') as f:
        lines = f.readlines()
        i = 0
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('},'):
                data = line.strip('{').strip('},').split(',')
                matrix[i, :] = data
                i += 1
    if i == 256:
        return matrix
    else:
        print(f"load 256x256 dither matrix error with file {filename} !")
        return None

## range: [1, 255]
## usage 1(for halftone): dst[y][x] = image[y][x] < g_ODMatrix_256x256_8bit[i][j] ? 0 : 255
## usage 2(for ditherdown): image[y][x] += g_ODMatrix_256x256_8bit[i][j] >> shiftbit
g_ODMatrix_256x256_8bit = load_rkcfa_dither_matrix_256x256(f'{os.path.dirname(__file__)}/rkcfa_DitherMatrix256x256_8bit.dat')

## ZhouFang error diffusion coefficients, direction: right, donw-left, down, sum to 256. 128x3
g_EdCoefs_ZhouFang_8bit = np.array([
    [185,   0,  71], [185,   0,  71], [175,   0,  81], [163,   0,  93], [159,   0,  97], [154,  10,  92], [151,  20,  85], [148,  29,  79],
    [145,  39,  72], [141,  49,  66], [138,  58,  60], [137,  61,  58], [136,  64,  56], [135,  66,  55], [134,  68,  54], [134,  70,  52],
    [133,  72,  51], [132,  74,  50], [131,  77,  48], [130,  79,  47], [130,  81,  45], [129,  83,  44], [119,  82,  55], [126,  82,  48],
    [123,  79,  54], [121,  75,  60], [119,  72,  65], [116,  69,  71], [114,  65,  77], [112,  62,  82], [109,  59,  88], [107,  55,  94],
    [122,  78,  56], [105,  55,  96], [106,  57,  93], [107,  59,  90], [108,  61,  87], [109,  63,  84], [110,  65,  81], [111,  67,  78],
    [112,  70,  74], [113,  72,  71], [114,  74,  68], [115,  76,  65], [110, 108,  38], [116,  81,  59], [117,  83,  56], [118,  85,  53],
    [119,  87,  50], [120,  89,  47], [121,  92,  43], [122,  94,  40], [123,  96,  37], [124,  98,  34], [125, 100,  31], [126, 102,  28],
    [127, 104,  25], [127, 107,  22], [128, 109,  19], [129, 111,  16], [130, 113,  13], [131, 116,   9], [132, 118,   6], [133, 120,   3],
    [ 93, 111,  52], [130, 124,   2], [125, 126,   5], [121, 128,   7], [116, 130,  10], [112, 132,  12], [107, 134,  15], [103, 136,  17],
    [ 98, 138,  20], [113, 119,  24], [127, 100,  29], [142,  81,  33], [156,  62,  38], [104, 132,  20], [170,  43,  43], [170,  43,  43],
    [170,  43,  43], [170,  43,  43], [170,  43,  43], [170,  43,  43], [170,  43,  43], [ 92,  87,  77], [166,  46,  44], [162,  50,  44],
    [158,  53,  45], [154,  56,  46], [149,  60,  47], [145,  63,  48], [141,  66,  49], [137,  70,  49], [132,  74,  50], [ 87,  95,  74],
    [128,  77,  51], [128,  77,  51], [128,  77,  51], [128,  77,  51], [128,  77,  51], [128,  77,  51], [ 91,  90,  75], [128,  77,  51],
    [128,  77,  51], [128,  77,  51], [128,  77,  51], [ 85,  96,  75], [130,  75,  51], [132,  74,  50], [134,  72,  50], [137,  70,  49],
    [ 85,  97,  74], [141,  66,  49], [143,  65,  48], [145,  63,  48], [146,  63,  47], [149,  60,  47], [151,  58,  47], [154,  56,  46],
    [156,  54,  46], [158,  53,  45], [160,  51,  45], [162,  50,  44], [164,  48,  44], [166,  46,  44], [169,  44,  43], [ 90,  92,  74],
])
## ZhouFang threshold modulation strength, normalized to 128 (7bit). 128x1
g_ThresholdModulationStrength_ZhouFang_7bit = np.array([
    0, 0, 1, 3, 4, 4, 5, 6, 8, 8, 9, 10, 12, 12, 13, 14, 15, 15, 17, 18, 19, 19, 20, 22, 23, 23, 24, 26, 27, 27, 28, 29,
    31, 31, 32, 33, 35, 35, 36, 37, 38, 40, 41, 42, 44, 44, 45, 46, 47, 49, 49, 50, 51, 52, 54, 54, 55, 56, 58, 59, 59,
    60, 61, 63, 64, 68, 72, 76, 79, 83, 87, 91, 96, 100, 104, 108, 111, 115, 119, 123, 128, 128, 128, 128, 128, 128, 116,
    106, 96, 84, 74, 64, 52, 42, 32, 22, 27, 33, 40, 45, 51, 58, 64, 69, 74, 79, 84, 90, 91, 93, 96, 99, 101, 102, 104,
    106, 108, 110, 111, 113, 115, 116, 119, 120, 122, 124, 125, 128
])

## Hermann halftone temporal compensation
g_HermannDeltaLut_8bit = np.array([
    38, 37, 35, 33, 32, 30, 29, 27, 25, 24, 22, 21, 19, 18, 16, 14, 13, 13, 13, 13, 13, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10,
    10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
    9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6,
    6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
], dtype=np.int8)

## @see Yen, etc., 'Chip Design of Video Halftoning for Color Electronic Paper'. National Taiwan Normal University, 2023. */
g_BayerOrderMatrix_8bit = np.array([
    0,64,16,80,4,68,20,84,          128,192,144,208,132,196,148,212,
    96,32,112,48,100,36,116,52,     224,160,240,176,228,164,244,180,
    24,88,8,72,28,92,12,76,         152,216,136,200,156,220,140,204,
    120,56,104,40,124,60,108,44,    248,184,232,168,252,188,236,172,
    6,70,22,86,2,66,18,82,          134,198,150,214,130,194,146,210,
    102,38,118,54,98,34,114,50,     230,166,246,182,226,162,242,178,
    30,94,14,78,26,90,10,74,        158,222,142,206,154,218,138,202,
    126,62,110,46,122,58,106,42,    254,190,238,174,250,186,234,170,

    129,193,145,209,133,197,149,213, 1,65,17,81,5,69,21,85,
    225,161,241,177,229,165,245,181, 97,33,113,49,101,37,117,53,
    153,217,137,201,157,221,141,205, 25,89,9,73,29,93,13,77,
    249,185,233,169,253,189,237,173, 121,57,105,41,125,61,109,45,
    135,199,151,215,131,195,147,211, 7,71,23,87,3,67,19,83,
    231,167,247,183,227,163,243,179, 103,39,119,55,99,35,115,51,
    159,223,143,207,155,219,139,203, 31,95,15,79,27,91,11,75,
    255,191,239,175,251,187,235,171, 127,63,111,47,123,59,107,43,
], dtype=np.uint8)

##### dithering functions #####
def dither_od(img: np.ndarray, src_depth=8, dst_depth=4, od_matrix_8bit: np.ndarray = g_ODMatrix_256x256_8bit):
    assert(1 <= dst_depth <= 8 and src_depth > dst_depth)

    H, W = img.shape[0], img.shape[1]
    mask = (2**dst_depth - 1) << (8 - dst_depth)

    if dst_depth == 1:
        src_lshift_bit = 8 - src_depth if src_depth < 8 else 0
        err_lshift_bit = src_depth - 8 if src_depth > 8 else 0 # [0, 5]

        # use as threshold
        err = np.tile(od_matrix_8bit, ((H + 255)//256, (W + 255)//256)).astype(np.uint8) # range: [1, 255]
        err = err[:H, :W]
        dst = np.where((img << src_lshift_bit) < (err << err_lshift_bit), 0, 255)
        dst = (dst & mask).astype(np.uint8)
    else:
        assert(dst_depth <= 8)
        src_rshift_bit = src_depth - dst_depth # [2, 6]
        err_rshift_bit = 7 - src_rshift_bit;    # [1, 5]

        # use as niose pattern
        err = np.tile(od_matrix_8bit, ((H + 255)//256, (W + 255)//256)).astype(np.int8) # range: [-128, 127]
        err = err[:H, :W]
        err = (err + (1 << (err_rshift_bit - 1)) + (err >> 7)) >> err_rshift_bit
        assert(np.max(err[:]) == 2**src_rshift_bit - 1)
        assert(np.min(err[:]) == -2**src_rshift_bit)
        dst = (img.astype(np.int16) + err.astype(np.int16)) >> src_rshift_bit
        dst = np.clip(dst, 0, 255).astype(np.uint8)
        dst = (dst & mask) # MSB valid
    return dst

def dither_ec(img: np.ndarray, pf_info: RkCfaPlatformInfo, target_bit=4, clip_old_val=False):
    assert(1 <= target_bit <= 7)
    mask = 2**target_bit - 1

    step = 255 / ((1 << target_bit) - 1)
    rnd = step // 2

    ed_coefs = pf_info.ed_coefs
    ed_factor = pf_info.ed_factor
    H, W = img.shape[0], img.shape[1]
    CH, CW = ed_coefs.shape[0], ed_coefs.shape[1]
    assert(CW <= 5 and CH == 2)
    pad = CW // 2

    ed_coefs = ed_coefs.astype(np.float32) / ed_factor
    ed_coefs = ed_coefs.reshape(-1)[pad+1:]
    error_buf = np.zeros((CH, W + 2 * pad), dtype=np.int16)

    ## define the lambda function for counting error
    if CH == 2 and CW == 3: # ED area: 2x3
        count_err = lambda er0, er1, er2, coefs, j: er0[j - 1] * coefs[3] + er0[j] * coefs[2] + er0[j + 1] * coefs[1] + er1[j - 1] * coefs[0]
    elif CH == 2 and CW == 5: # ED area: 2x5
        count_err = lambda er0, er1, er2, coefs, j: er0[j - 2] * coefs[6] + er0[j - 1] * coefs[5] + er0[j] * coefs[4] + \
            er0[j + 1] * coefs[3] + er0[j + 2] * coefs[2] + er1[j - 2] * coefs[1] + er1[j - 1] * coefs[0]
    elif CH == 3 and CW == 5: # ED area: 3x5
        count_err = lambda er0, er1, er2, coefs, j: er0[j - 2] * coefs[11] + er0[j - 1] * coefs[10] + er0[j] * coefs[9] + \
            er0[j + 1] * coefs[8] + er0[j + 2] * coefs[7] + er1[j - 2] * coefs[6] + er1[j - 1] * coefs[5] + er1[j] * coefs[4] + \
            er1[j + 1] * coefs[3] + er1[j + 2] * coefs[2] + er2[j - 2] * coefs[1] + er2[j - 1] * coefs[0]
    else:
        raise TypeError(f'Unsupported ED area size: {CH}x{CW}!')
    old_val_clip = lambda r: np.clip(r, 0, 255) if clip_old_val else r

    for y in range(H):
        error_row0 = error_buf[y%CH, :].view()
        error_row1 = error_buf[(y+1)%CH, :].view()
        error_row2 = error_buf[(y+2)%CH, :].view() if CH == 3 else error_row1.view()
        for x in range(W):
            j = pad + x
            err_val = count_err(error_row0, error_row1, error_row2, ed_coefs, j)
            old_val = img[y, x] + np.floor(err_val)
            # old_val = old_val_clip(old_val)
            new_val = (old_val + rnd) // step * step
            new_val = np.clip(new_val, 0, 255)
            img[y, x] = new_val
            error_row2[j] = old_val - new_val
        error_row0[:] = 0 # reset to 0 for next row

    img[:] = np.bitwise_and(img, mask)
    return img

##### pattern to color conversion #####
def cfa_pattern2color(img: np.ndarray, pf_info: RkCfaPlatformInfo, norm_to_8bit=True):
    '''
    @brief: 从pattern图案反向推算rgb色彩图像，即demosaic过程，模拟了人眼的低通显示效果。
        默认采用'const_chroma'约束，即色差恒定假设。效果更好的方法有：
        - 边缘判别插值: Adam-Hamilton / AHD / GBTF 效果比较好
        - 残差插值法: RI / MLRI / IRI / ARI 效果更好
    @see: [从bayer到rgb:ISP中的demosaic技术](https://zhuanlan.zhihu.com/p/682733226)
    '''

    img = img.squeeze() # HWC to HW
    if norm_to_8bit:
        img += img >> 4

    H, W = img.shape[0], img.shape[1]
    PH, PW = pf_info.pattern.shape[0], pf_info.pattern.shape[1]
    pattern = np.tile(pf_info.pattern, ((H + PH - 1)//PH, (W + PW - 1)//PW)).astype(np.uint8)
    pattern = pattern[:H, :W]

    ## 1st: fill rgb known color values
    r = np.where(pattern == 0, img, np.zeros_like(img, dtype=np.uint8)) # fill r in pattern-r pixels
    g = np.where(pattern == 1, img, np.zeros_like(img, dtype=np.uint8)) # fill g in pattern-g pixels
    b = np.where(pattern == 2, img, np.zeros_like(img, dtype=np.uint8)) # fill b in pattern-b pixels

    ## get kernel
    gausian_kernel = cv2.getGaussianKernel(5, 1.0, cv2.CV_32F)
    gausian_kernel = gausian_kernel * gausian_kernel.T
    if pf_info.name in ['EC060KC1', 'EC070KC1', 'EC078KH6', 'EC103KH3']:
        if pf_info.name in ['EC103KH3']:
            ## 3x3 rgb pattern 135 degree
            mask_g4r = np.array([[0, 0, 1, 0, 0], [1, 0, 0, 1, 0], [0, 1, 0, 0, 1], [0, 0, 1, 0, 0], [0, 1, 0, 0, 1]], dtype=np.float32)
            mask_g4b = np.array([[0, 1, 0, 0, 1], [0, 0, 1, 0, 0], [1, 0, 0, 1, 0], [1, 0, 0, 1, 0], [0, 0, 1, 0, 0]], dtype=np.float32)
        else:
            ## 3x3 rgb pattern 45 degree
            mask_g4r = np.array([[0, 0, 1, 0, 0], [0, 1, 0, 0, 1], [1, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 1, 0, 0, 1]], dtype=np.float32)
            mask_g4b = np.array([[1, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 1, 0, 0, 1], [1, 0, 0, 1, 0], [0, 0, 1, 0, 0]], dtype=np.float32)
        # kernel_g4rb = np.ones((5, 5), dtype=np.float32) / 8.0 # 8 g-pixels around r/b-pixels on 5x5 area
        kernel_g4r = gausian_kernel * mask_g4r
        kernel_g4b = gausian_kernel * mask_g4b
        kernel_g4r /= np.sum(kernel_g4r[:])
        kernel_g4b /= np.sum(kernel_g4b[:])
        kernel_r4b = kernel_b4g = kernel_g4r
        kernel_b4r = kernel_r4g = kernel_g4b

    elif pf_info.name in ['OPM103E5', 'OPM133C1']:
        mask_g4r = np.array([[0, 1, 0, 1, 0], [0, 0, 0, 0, 0], [0, 1, 0, 1, 0], [0, 0, 0, 0, 0], [0, 1, 0, 1, 0]], dtype=np.float32)
        mask_g4b = np.array([[0, 0, 0, 0, 0], [1, 0, 1, 0, 1], [0, 0, 0, 0, 0], [1, 0, 1, 0, 1], [0, 0, 0, 0, 0]], dtype=np.float32)
        mask_r4b = np.array([[0, 0, 0, 0, 0], [0, 1, 0, 1, 0], [0, 0, 0, 0, 0], [0, 1, 0, 1, 0], [0, 0, 0, 0, 0]], dtype=np.float32)
        kernel_g4r = gausian_kernel * mask_g4r
        kernel_g4b = gausian_kernel * mask_g4b
        kernel_r4b = gausian_kernel * mask_r4b
        kernel_g4r /= np.sum(kernel_g4r[:])
        kernel_g4b /= np.sum(kernel_g4b[:])
        kernel_r4b /= np.sum(kernel_r4b[:])
        kernel_r4g = kernel_b4w = kernel_g4r
        kernel_b4g = kernel_r4w = kernel_g4b
        kernel_b4r = kernel_r4b

        kernel_g4w = np.array([[-0.5, 0, -1.5, 0, -0.5], [0, 2, 0, 2, 0], [-1.5, 0, 8, 0, -1.5], [0, 2, 0, 2, 0], [-0.5, 0, -1.5, 0, -0.5]], dtype=np.float32) / 8.0
        covw = cv2.filter2D(img, cv2.CV_8UC1, kernel_g4w, borderType=cv2.BORDER_REPLICATE)
        g[pattern == 3] = covw[pattern == 3] # fill g in pattern-w pixels from covw

    elif pf_info.name in ['EC060KH3', 'EC060KH4', 'EC078KH3']:
        ## even row: g,b,b,r,r;
        ## old  row: r,r,g,g,b;
        mask_g4r_L = np.array([[0, 0, 0, 0, 1], [0, 1, 1, 0, 0], [0, 0, 0, 0, 1], [0, 1, 1, 0, 0], [0, 0, 0, 0, 1]], dtype=np.float32)
        mask_g4r_R = np.array([[0, 0, 0, 1, 1], [1, 1, 0, 0, 0], [0, 0, 0, 1, 1], [1, 1, 0, 0, 0], [0, 0, 0, 1, 1]], dtype=np.float32)
        mask_g4b_L = np.array([[1, 1, 0, 0, 0], [0, 0, 0, 1, 1], [1, 1, 0, 0, 0], [0, 0, 0, 1, 1], [1, 1, 0, 0, 0]], dtype=np.float32)
        mask_g4b_R = np.array([[1, 0, 0, 0, 0], [0, 0, 1, 1, 0], [1, 0, 0, 0, 0], [0, 0, 1, 1, 0], [1, 0, 0, 0, 0]], dtype=np.float32)
        kernel_g4r_L = gausian_kernel * mask_g4r_L
        kernel_g4r_R = gausian_kernel * mask_g4r_R
        kernel_g4b_L = gausian_kernel * mask_g4b_L
        kernel_g4b_R = gausian_kernel * mask_g4b_R
        kernel_g4r_L /= np.sum(kernel_g4r_L[:])
        kernel_g4r_R /= np.sum(kernel_g4r_R[:])
        kernel_g4b_L /= np.sum(kernel_g4b_L[:])
        kernel_g4b_R /= np.sum(kernel_g4b_R[:])
        kernel_r4g_L = kernel_b4r_L = kernel_g4b_L
        kernel_r4g_R = kernel_b4r_R = kernel_g4b_R
        kernel_b4g_L = kernel_r4b_L = kernel_g4r_L
        kernel_b4g_R = kernel_r4b_R = kernel_g4r_R

        ## 2nd: fill green color values. All grean color pixels are filled after this step.
        covg_L = cv2.filter2D(g, cv2.CV_8UC1, kernel_g4r_L, borderType=cv2.BORDER_REPLICATE)
        covg_R = cv2.filter2D(g, cv2.CV_8UC1, kernel_g4r_R, borderType=cv2.BORDER_REPLICATE)
        covg_L[0::2, 0::2] = 0 # for  Left-red-pixel on even row, just keep the old  column pixels
        covg_L[1::2, 1::2] = 0 # for  Left-red-pixel on old  row, just keep the even column pixels
        covg_R[0::2, 1::2] = 0 # for Right-red-pixel on even row, just keep the even column pixels
        covg_R[1::2, 0::2] = 0 # for Right-red-pixel on old  row, just keep the old  column pixels
        g[pattern == 0] += covg_L[pattern == 0] # fill g in pattern-r pixels from covg4r
        g[pattern == 0] += covg_R[pattern == 0] # fill g in pattern-r pixels from covg4r
        covg_L = cv2.filter2D(g, cv2.CV_8UC1, kernel_g4b_L, borderType=cv2.BORDER_REPLICATE)
        covg_R = cv2.filter2D(g, cv2.CV_8UC1, kernel_g4b_R, borderType=cv2.BORDER_REPLICATE)
        covg_L[0::2, 0::2] = 0 # for  Left-blur-pixel on even row, just keep the old  column pixels
        covg_L[1::2, 1::2] = 0 # for  Left-blur-pixel on old  row, just keep the even column pixels
        covg_R[0::2, 1::2] = 0 # for Right-blur-pixel on even row, just keep the even column pixels
        covg_R[1::2, 0::2] = 0 # for Right-blur-pixel on old  row, just keep the old  column pixels
        g[pattern == 2] += covg_L[pattern == 2] # fill g in pattern-b pixels from covg4b
        g[pattern == 2] += covg_R[pattern == 2] # fill g in pattern-b pixels from covg4b

        ## 3rd: fill red and blue color values with 'const chroma principle'
        cr = r.astype(np.int16)
        cb = b.astype(np.int16)
        cr[pattern == 0] -= g[pattern == 0] # cr = r - g, g/b pixels are 0
        cb[pattern == 2] -= g[pattern == 2] # cb = b - g, r/g pixels are 0
        retr = cr
        retb = cb
        # fill r in pattern-g pixels from covr
        covr_L = cv2.filter2D(cr, -1, kernel_r4g_L, borderType=cv2.BORDER_REPLICATE)
        covr_R = cv2.filter2D(cr, -1, kernel_r4g_R, borderType=cv2.BORDER_REPLICATE)
        covr_L[0::2, 0::2] = 0
        covr_L[1::2, 1::2] = 0
        covr_R[0::2, 1::2] = 0
        covr_R[1::2, 0::2] = 0
        retr[pattern == 1] += covr_L[pattern == 1]
        retr[pattern == 1] += covr_R[pattern == 1]
        # fill b in pattern-g pixels from covb
        covb_L = cv2.filter2D(cb, -1, kernel_b4g_L, borderType=cv2.BORDER_REPLICATE)
        covb_R = cv2.filter2D(cb, -1, kernel_b4g_R, borderType=cv2.BORDER_REPLICATE)
        covb_L[0::2, 0::2] = 0
        covb_L[1::2, 1::2] = 0
        covb_R[0::2, 1::2] = 0
        covb_R[1::2, 0::2] = 0
        retb[pattern == 1] += covb_L[pattern == 1]
        retb[pattern == 1] += covb_R[pattern == 1]
        # fill r in pattern-b pixels from covr
        covr_L = cv2.filter2D(cr, -1, kernel_r4b_L, borderType=cv2.BORDER_REPLICATE)
        covr_R = cv2.filter2D(cr, -1, kernel_r4b_R, borderType=cv2.BORDER_REPLICATE)
        covb_L[0::2, 0::2] = 0
        covb_L[1::2, 1::2] = 0
        covb_R[0::2, 1::2] = 0
        covb_R[1::2, 0::2] = 0
        retr[pattern == 2] += covr_L[pattern == 2]
        retr[pattern == 2] += covr_R[pattern == 2]
        # fill b in pattern-r pixels from covb
        covb_L = cv2.filter2D(cb, -1, kernel_b4r_L, borderType=cv2.BORDER_REPLICATE)
        covb_R = cv2.filter2D(cb, -1, kernel_b4r_R, borderType=cv2.BORDER_REPLICATE)
        covb_L[0::2, 0::2] = 0
        covb_L[1::2, 1::2] = 0
        covb_R[0::2, 1::2] = 0
        covb_R[1::2, 0::2] = 0
        retb[pattern == 0] += covb_L[pattern == 0]
        retb[pattern == 0] += covb_R[pattern == 0]

        r = np.clip(retr + g, 0, 255).astype(np.uint8)
        b = np.clip(retb + g, 0, 255).astype(np.uint8)
        rgb = np.stack([r, g, b], axis=2)
        return rgb

    else:
        print(f'Error: unsupported platform {pf_info.name}!')
        exit(-1)

    ## 2nd: fill green color values. All grean color pixels are filled after this step.
    covg = cv2.filter2D(g, cv2.CV_8UC1, kernel_g4r, borderType=cv2.BORDER_REPLICATE)
    g[pattern == 0] = covg[pattern == 0] # fill g in pattern-r pixels from covg4r
    covg = cv2.filter2D(g, cv2.CV_8UC1, kernel_g4b, borderType=cv2.BORDER_REPLICATE)
    g[pattern == 2] = covg[pattern == 2] # fill g in pattern-b pixels from covg4b

    ## 3rd: fill red and blue color values with 'const chroma principle'
    cr = r.astype(np.int16)
    cb = b.astype(np.int16)
    cr[pattern == 0] -= g[pattern == 0] # cr = r - g, g/b pixels are 0
    cb[pattern == 2] -= g[pattern == 2] # cb = b - g, r/g pixels are 0
    retr = cr
    retb = cb
    covr = cv2.filter2D(cr, -1, kernel_r4g, borderType=cv2.BORDER_REPLICATE)
    covb = cv2.filter2D(cb, -1, kernel_b4g, borderType=cv2.BORDER_REPLICATE)
    retr[pattern == 1] = covr[pattern == 1] # fill r in pattern-g pixels from covr
    retb[pattern == 1] = covb[pattern == 1] # fill b in pattern-g pixels from covb
    covr = cv2.filter2D(cr, -1, kernel_r4b, borderType=cv2.BORDER_REPLICATE)
    covb = cv2.filter2D(cb, -1, kernel_b4r, borderType=cv2.BORDER_REPLICATE)
    retr[pattern == 2] = covr[pattern == 2] # fill r in pattern-b pixels from covr
    retb[pattern == 0] = covb[pattern == 0] # fill b in pattern-r pixels from covb
    if pf_info.name in ['OPM103E5', 'OPM133C1']:
        covr = cv2.filter2D(cr, -1, kernel_r4w, borderType=cv2.BORDER_REPLICATE)
        covb = cv2.filter2D(cb, -1, kernel_b4w, borderType=cv2.BORDER_REPLICATE)
        retr[pattern == 3] = covr[pattern == 3]
        retb[pattern == 3] = covg[pattern == 3]

    r = np.clip(retr + g, 0, 255).astype(np.uint8)
    b = np.clip(retb + g, 0, 255).astype(np.uint8)

    rgb = np.stack([r, g, b], axis=2)
    return rgb

##### (same to libcfa) color to pattern conversion for all mode #####
def c2p_input2pattern(img: np.ndarray, pf_info: RkCfaPlatformInfo):
    '''
    color/gray image to pattern image
    support image format: rgba(U8C4), rgb(U8C3), gray(U8C1)
    return pattern image(U8C1) with the low 4bits cleared
    '''


    H, W = img.shape[0], img.shape[1]
    C = img.shape[2] if len(img.shape) >= 3 else 1
    PH, PW = pf_info.pattern.shape[0], pf_info.pattern.shape[1]

    if C == 1:
        gray = img.copy()
    elif C >= 3:
        gray = np.round(img[:,:,0] * 0.299 + img[:,:,1] * 0.587 + img[:,:,2] * 0.114).astype(np.uint8)

    # COMMON(grayscale) platform
    if pf_info.name == 'COMMON':
        dst = gray.copy()

    # 2x2 RGBW CFA pattern
    elif pf_info.name in ['OPM103E5', 'OPM133C1']:
        assert(PH == 2 and PW == 2)
        assert(np.max(pf_info.pattern) <= 3)
        # white = np.min(img, axis=2)
        white = np.right_shift(np.sum(img.astype(np.uint16), axis=2) - np.max(img.astype(np.uint16), axis=2), 1).astype(np.uint8)
        pidx0, pidx1, pidx2, pidx3 = np.ravel(pf_info.pattern) # flattern pattern to 1D array
        dst = np.zeros((H, W), dtype=np.uint8)
        dst[0:H:2, 0:W:2] = img[0:H:2, 0:W:2, pidx0] if pidx0 != 3 else white[0:H:2, 0:W:2]
        dst[0:H:2, 1:W:2] = img[0:H:2, 1:W:2, pidx1] if pidx1 != 3 else white[0:H:2, 1:W:2]
        dst[1:H:2, 0:W:2] = img[1:H:2, 0:W:2, pidx2] if pidx2 != 3 else white[1:H:2, 0:W:2]
        dst[1:H:2, 1:W:2] = img[1:H:2, 1:W:2, pidx3] if pidx3 != 3 else white[1:H:2, 1:W:2]

    # 3x3 or 2x6 RGB CFA pattern
    else:
        assert(np.max(pf_info.pattern) <= 2)
        full_pattern = np.tile(pf_info.pattern, ((H + PH - 1)//PH, (W + PW - 1)//PW)).astype(np.uint8)
        full_pattern = full_pattern[:H, :W]
        dst = np.zeros((H, W), dtype=np.uint8)
        dst += np.where(full_pattern == 0, img[:,:,0], 0)
        dst += np.where(full_pattern == 1, img[:,:,1], 0)
        dst += np.where(full_pattern == 2, img[:,:,2], 0)

    return dst, gray

##### (same to libcfa) deshadow processing for mode 'regal' #####
def regal_process(curr_pt: np.ndarray, prev_pt: np.ndarray, curr_rgb: np.ndarray, clear_low_bits=True):
    H, W = curr_pt.shape[0], curr_pt.shape[1]
    dst = curr_pt.copy()
    th = 0xE8

    curr_mask_pt = curr_pt >= th
    prev_mask_pt = prev_pt >= th
    if curr_rgb is not None:
        curr_mask_rgb = curr_rgb[:,:,:3] == [255, 255, 255]
    else:
        curr_mask_rgb = np.ones((H, W), dtype=np.bool)

    kernel = np.ones((3, 3), dtype=np.uint8)
    box_filter  = ImageFilter.Kernel((3, 3), kernel.ravel(), scale=None, offset=0)
    curr_cnt = (1 - curr_mask_pt).filter(box_filter)
    prev_cnt = (1 - prev_mask_pt).filter(box_filter)

    ## common regal
    mask = curr_mask_rgb & curr_mask_pt & prev_mask_pt & (curr_cnt == 0) & (prev_cnt > 0)
    mask1 = mask.copy()
    dst[mask] = 0xF8

    mask = curr_mask_rgb & curr_mask_pt & prev_mask_pt & (curr_cnt >= 3)
    mask1 |= mask
    dst[mask] = 0xE8

    ## rgba regal
    if curr_rgb is not None:
        mask = (1 - curr_mask_rgb) & curr_mask_pt & (prev_pt == 0)
        mask1 |= mask
        dst[mask] = 0xE8
        prev_pt[mask] = 0x08

        mask = (1 - curr_mask_rgb) & curr_mask_pt & prev_mask_pt
        mask1 |= mask
        dst[mask] = 0xE8

    ## clear low 4 bits for the pixels not in the mask
    if clear_low_bits:
        dst[1 - mask1] = np.bitwise_and(dst[1 - mask1], 0xF0)
    return dst, prev_pt

##### (same to libcfa) halftone processing for mode 'A2' #####
def a2_process(src_pt: np.ndarray, compensation: np.ndarray, diff_mask: np.ndarray, pf_info: RkCfaPlatformInfo, comp_level=64, clip_old_val=False):
    '''
    Hermann video halftone algorithm
    '''
    ed_coefs = pf_info.ed_coefs
    ed_factor = pf_info.ed_factor
    ed_rnd = np.int16(ed_factor//2)

    MIN_VAL = 0
    MAX_VAL = 255
    MID_VAL = 127
    H, W = src_pt.shape[0], src_pt.shape[1]
    CH, CW = ed_coefs.shape[0], ed_coefs.shape[1]
    assert(CW <= 5 and CH == 2)
    pad = CW // 2

    # ed_coefs = ed_coefs.astype(np.float32) / ed_factor
    ed_coefs = ed_coefs.reshape(-1)[pad+1:]
    error_buf = np.zeros((CH, W + 2 * pad), dtype=np.int16)
    dst_pt = np.zeros((H, W), dtype=np.uint8)

    ## define the lambda function for counting error
    if CH == 2 and CW == 3: # ED area: 2x3
        count_err = lambda er0, er1, er2, coefs, j: er0[j - 1] * coefs[3] + er0[j] * coefs[2] + er0[j + 1] * coefs[1] + er1[j - 1] * coefs[0]
    elif CH == 2 and CW == 5: # ED area: 2x5
        count_err = lambda er0, er1, er2, coefs, j: er0[j - 2] * coefs[6] + er0[j - 1] * coefs[5] + er0[j] * coefs[4] + \
            er0[j + 1] * coefs[3] + er0[j + 2] * coefs[2] + er1[j - 2] * coefs[1] + er1[j - 1] * coefs[0]
    elif CH == 3 and CW == 5: # ED area: 3x5
        count_err = lambda er0, er1, er2, coefs, j: er0[j - 2] * coefs[11] + er0[j - 1] * coefs[10] + er0[j] * coefs[9] + \
            er0[j + 1] * coefs[8] + er0[j + 2] * coefs[7] + er1[j - 2] * coefs[6] + er1[j - 1] * coefs[5] + er1[j] * coefs[4] + \
            er1[j + 1] * coefs[3] + er1[j + 2] * coefs[2] + er2[j - 2] * coefs[1] + er2[j - 1] * coefs[0]
    else:
        raise TypeError(f'Unsupported ED area size: {CH}x{CW}!')
    old_val_clip = lambda r: np.clip(r, 0, 255) if clip_old_val else r

    for y in range(H):
        error_row0 = error_buf[y%CH, :].view()
        error_row1 = error_buf[(y+1)%CH, :].view()
        error_row2 = error_buf[(y+2)%CH, :].view() if CH == 3 else error_row1.view()
        for x in range(W):
            j = pad + x
            err_val = count_err(error_row0, error_row1, error_row2, ed_coefs, j)
            err_rnd = ((err_val >> 15) & 0x1) * ed_rnd # RTZ
            old_val = src_pt[y, x] + ((err_val + err_rnd) >> 4) # ed_coefs are all 4bit for now
            # old_val = old_val_clip(old_val)
            new_val = MAX_VAL if old_val + compensation[y,x] > MID_VAL else MIN_VAL
            dst_pt[y,x] = new_val
            error_row2[j] = old_val - new_val
        error_row0[:] = 0 # reset to 0 for next row

    # comp_level = comp_level / 64.0
    # compensation = np.round(g_HermannDeltaLut_8bit[diff_mask] * comp_level).astype(np.int8)
    compensation = np.floor(comp_level / 2)
    compensation[dst_pt == MIN_VAL] = -compensation[dst_pt == MIN_VAL]
    dst_pt[:] = np.bitwise_and(dst_pt, 0xF0)

    return dst_pt, compensation



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='input file')
    parser.add_argument('-o', '--output', type=str, help='output file or output directory')
    parser.add_argument('-p', '--platform', type=str, default='common', help='support list: common, 060kc1, 070kc1, 078kh6, 103kh3, 103e5')
    parser.add_argument('-t', '--type', type=str, default='c2p', help='support list: c2p, od, ed')
    parser.add_argument('-f', '--format', type=str, default='gray', help='support list: rgba, rgb, gray, pattern')
    parser.add_argument('-w', '--width', type=int, default=2480)
    parser.add_argument('-g', '--height', type=int, default=1860)
    parser.add_argument('-d', '--src_depth', type=int, default=8)
    parser.add_argument('-D', '--dst_depth', type=int, default=4)
    parser.add_argument('-n', '--frames', type=int, default=1, help='only valid when input number of files is 1')
    args = parser.parse_args()

    # check options
    if args.input is None:
        print(f'Error: input file is not specified!')
        exit(-1)

    output_filename = f'output_{args.width}x{args.height}.png'
    if args.output is None:
        args.output = os.path.join(os.path.dirname(args.input), output_filename)
    elif os.path.isdir(args.output):
        args.output = os.path.join(args.output, output_filename)

    # read input image
    W = args.width
    H = args.height
    is_normal_img = False
    normal_img_ext = ['png', 'bmp', 'jpg', 'jpeg', 'tif']
    for ext in normal_img_ext:
        if args.input.endswith(ext):
            is_normal_img = True
            img = Image.open(args.input).resize((W, H))
            args.src_depth = 8
            break

    is_yuv_planar = False
    imgY = None
    if not is_normal_img:
        if args.format == 'gray':
            data = np.fromfile(args.input, dtype=np.uint8 if args.src_depth <= 8 else np.uint16)
            img = data.reshape(H, W)
            imgY = np.expand_dims(img, axis=2)
        elif args.format == 'yuv420p' or args.format == 'yu12':
            data = np.fromfile(args.input, dtype=np.uint8)
            imgY = data[0:H*W].reshape(H, W)
            imgU = data[H*W:H*W*5//4].reshape(H//2, W//2)
            imgV = data[H*W*5//4:H*W*6//4].reshape(H//2, W//2)
            is_yuv_planar = True
        elif args.format == 'yuv420p10l':
            data = np.fromfile(args.input, dtype=np.uint16)
            imgY = data[0:H*W].reshape(H, W)
            imgU = data[H*W:H*W*5//4].reshape(H//2, W//2)
            imgV = data[H*W*5//4:H*W*6//4].reshape(H//2, W//2)
            is_yuv_planar = True



    # run test
    platform = args.platform.lower()
    if platform in g_cfa_support_platforms:
        pf_info = g_cfa_support_platforms[platform]
    else:
        print(f'Error: platform {platform} is not supported!')
        exit(-1)

    ## do color2pattern
    if args.type == 'c2p':
        dst, _ = c2p_input2pattern(np.array(imgY), pf_info)
    elif args.type == 'od':
        dst = dither_od(np.array(imgY), src_depth=args.src_depth, dst_depth=args.dst_depth)
    elif args.type == 'ec' or args.type == 'ed':
        dst = dither_ec(np.array(imgY), pf_info, target_bit=args.dst_depth)

    if is_normal_img:
        Image.fromarray(dst, mode='L').save(args.output)
    elif is_yuv_planar:
        if args.dst_depth <= 8:
            data = np.zeros(H*W*6//4, dtype=np.uint8)
            data[0:H*W] = dst.flatten()
            data[H*W:H*W*5//4] = imgU.flatten() >> (args.src_depth - 8)
            data[H*W*5//4:H*W*6//4] = imgV.flatten() >> (args.src_depth - 8)
            data.tofile(args.output)
        else:
            print(f'Error: dst_depth {args.dst_depth} is not supported for yuv planar format!')
            exit(-1)
    else:
        data.tofile(args.output)

    print(f'save result to {args.output}.')

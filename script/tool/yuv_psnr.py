'''
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : yuv_psnr.py
Author      : vance.wu@rock-chips.com
Date        : 2025-12-11
Description :
LastEditTime: 2025-12-11
'''

import os
import sys
import argparse
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import utils as utl


def get_yuv_psnr(yuv_chw1: np.ndarray, yuv_chw2: np.ndarray, depth: int = 8) -> float:
    assert yuv_chw1.shape[2] == yuv_chw2.shape[2] and yuv_chw1.shape[1] == yuv_chw2.shape[1]
    assert yuv_chw1.shape[0] == 3 and yuv_chw2.shape[0] == 3

    max_val = (1 << depth) - 1
    mses = np.mean((yuv_chw1 - yuv_chw2) ** 2, axis=(1, 2))

    psnrs = 20 * np.log10(max_val) - 10 * np.log10(mses)
    psnrs = np.where(mses == 0, np.ones_like(mses) * 100, psnrs)

    return psnrs


def main():
    parser = argparse.ArgumentParser(description='Calculate the PSNR between two YUV planar images.')
    parser.add_argument("-r", "--ref_file", type=str, help='The reference YUV planar image file path.')
    parser.add_argument("-t", "--tar_file", type=str, help='The target YUV planar image file path.')
    parser.add_argument("-d", "--depth", type=int, default=8, help='The bit depth of the YUV image.')
    parser.add_argument("-w", "--width", type=int, default=1920, help='The width of the YUV image.')
    parser.add_argument("-g", "--height", type=int, default=1080, help='The height of the YUV image.')
    args = parser.parse_args()

    frame_size = args.width * args.height * 3  # YUV444 planar format
    data_type = np.uint8
    if args.depth == 10:
        frame_size *= 2  # yuv444p10l
        data_type = np.uint16
    yuv1 = np.fromfile(args.ref_file, dtype=data_type, count=frame_size)
    yuv2 = np.fromfile(args.tar_file, dtype=data_type, count=frame_size)
    yuv1 = yuv1.reshape((3, args.height, args.width)) # planar in, CHW
    yuv2 = yuv2.reshape((3, args.height, args.width))

    psnrs = get_yuv_psnr(yuv1, yuv2, args.depth)
    wpsnr = (psnrs[0] * 4 + psnrs[1] + psnrs[2]) / 6
    print(f'PSNR: Y/U/V={psnrs.flatten().tolist()} dB. weighted(4/1/1) PSNR: {wpsnr: .2f}')


if __name__ == '__main__':
    main()
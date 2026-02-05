'''
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : cvt_png.py
Author      : vance.wu@rock-chips.com
Date        : 2026-01-01
Description :
LastEditTime: 2026-01-01
'''

import os
import sys
import cv2
import argparse
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import utils as utl


# BT.709 YUV to RGB conversion (Y in [0,255], U/V in [-128,127])
def yuvf_to_rgbf_bt709(y, u, v):
    y = np.float64(y)
    cb = np.float64(u) - 128
    cr = np.float64(v) - 128
    r = y + 1.5748 * cr
    g = y - 0.1873 * cb - 0.4681 * cr
    b = y + 1.8556 * cb
    return np.stack([r, g, b], axis=2)  # shape: (H, W, 3)


def rgbf_to_yuvf_bt709(r, g, b):
    r = np.float64(r)
    g = np.float64(g)
    b = np.float64(b)
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    u = -0.114572 * r - 0.385428 * g + 0.5 * b + 128
    v = 0.5 * r - 0.454153 * g - 0.045847 * b + 128
    return np.stack([y, u, v], axis=2)  # shape: (H, W, 3)


def convertRawImg2Png(file: str, imgWid: int, imgHgt: int, pitch: int, fmt: str, outdir: str = None):
    sizeY = imgHgt * pitch
    outdir = os.path.dirname(file) if outdir is None else outdir

    name = os.path.basename(file).split(".")[0]
    outfile = os.path.join(outdir, name + '.png')

    try:
        data = np.fromfile(file, dtype=np.uint8, count=-1)
        if fmt == "nv12":
            y = data[0:sizeY].reshape(imgHgt, pitch)
            u = data[sizeY : len(data) : 2].reshape(imgHgt // 2, pitch // 2)
            v = data[sizeY + 1 : len(data) : 2].reshape(imgHgt // 2, pitch // 2)
            u = cv2.resize(u, (pitch, imgHgt), interpolation=cv2.INTER_LINEAR)
            v = cv2.resize(v, (pitch, imgHgt), interpolation=cv2.INTER_LINEAR)
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt == "nv16":
            y = data[0:sizeY].reshape(imgHgt, pitch)
            u = data[sizeY : len(data) : 2].reshape(imgHgt, pitch // 2)
            v = data[sizeY + 1 : len(data) : 2].reshape(imgHgt, pitch // 2)
            u = cv2.resize(u, (pitch, imgHgt), interpolation=cv2.INTER_LINEAR)
            v = cv2.resize(v, (pitch, imgHgt), interpolation=cv2.INTER_LINEAR)
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt == "nv24":
            y = data[0:sizeY].reshape(imgHgt, pitch)
            u = data[sizeY : len(data) : 2].reshape(imgHgt, pitch)
            v = data[sizeY + 1 : len(data) : 2].reshape(imgHgt, pitch)
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt == "yu24":
            y = data[0:sizeY].reshape(imgHgt, pitch)
            u = data[sizeY : sizeY * 2].reshape(imgHgt, pitch)
            v = data[sizeY * 2 : sizeY * 3].reshape(imgHgt, pitch)
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt == 'nv15':
            data = pfc.unpackData_10bit(data, imgHgt * 3 // 2, imgWid, pitch)
            data_u8 = np.around(data / 1023 * 255).astype(np.uint8)
            sizeY = imgHgt * imgWid
            y = data_u8[0:sizeY].reshape(imgHgt, imgWid)
            u = data_u8[sizeY : len(data) : 2].reshape(imgHgt // 2, imgWid // 2)
            v = data_u8[sizeY + 1 : len(data) : 2].reshape(imgHgt // 2, imgWid // 2)
            u = cv2.resize(u, (imgWid, imgHgt), interpolation=cv2.INTER_LINEAR)
            v = cv2.resize(v, (imgWid, imgHgt), interpolation=cv2.INTER_LINEAR)
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt == 'nv20':
            data = pfc.unpackData_10bit(data, imgHgt * 2, imgWid, pitch)
            data_u8 = np.around(data / 1023 * 255).astype(np.uint8)
            sizeY = imgHgt * imgWid
            y = data_u8[0:sizeY].reshape(imgHgt, imgWid)
            u = data_u8[sizeY : len(data) : 2].reshape(imgHgt, imgWid // 2)
            v = data_u8[sizeY + 1 : len(data) : 2].reshape(imgHgt, imgWid // 2)
            u = cv2.resize(u, (imgWid, imgHgt), interpolation=cv2.INTER_LINEAR)
            v = cv2.resize(v, (imgWid, imgHgt), interpolation=cv2.INTER_LINEAR)
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt == 'nv30':
            data = pfc.unpackData_10bit(data, imgHgt * 3, imgWid, pitch)
            data_u8 = np.around(data / 1023 * 255).astype(np.uint8)
            sizeY = imgHgt * imgWid
            y = data_u8[0:sizeY].reshape(imgHgt, imgWid)
            u = data_u8[sizeY : len(data) : 2].reshape(imgHgt, imgWid)
            v = data_u8[sizeY + 1 : len(data) : 2].reshape(imgHgt, imgWid)
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt == 'vu30':
            data = pfc.unpackData_vu30(data, imgHgt, imgWid, pitch)
            data_u8 = np.around(data / 1023 * 255).astype(np.uint8)
            data_u8 = data_u8.reshape(imgHgt, imgWid, 3)
            y = data_u8[:, :, 0]
            u = data_u8[:, :, 1]
            v = data_u8[:, :, 2]
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt in ['vu24', 'yuv444i']:
            data = data.reshape(imgHgt, imgWid, 3)
            y = data[:, :, 0]
            u = data[:, :, 1]
            v = data[:, :, 2]
            rgb = yuvf_to_rgbf_bt709(y, u, v)
            rgb = np.clip(rgb + 0.5, 0, 255).astype(np.uint8)
        elif fmt in ['rgba', 'rgba32', 'rgba8888']:
            data = data.reshape(imgHgt, pitch // 4, 4)
            rgb = data[:, :, :3]
        elif fmt == 'bgra':
            data = data.reshape(imgHgt, pitch // 4, 4)
            rgb = data[:, :, [2, 1, 0]]
        elif fmt in ['rgb', 'rg24', 'rgb24', 'rgb888']:
            rgb = data.reshape(imgHgt, pitch // 3, 3)
        elif fmt in ['bgr', 'bg24', 'bgr24', 'bgr888']:
            data = data.reshape(imgHgt, pitch // 3, 3)
            rgb = data[:, :, ::-1]
        # elif fmt == 'rgb565':
        #     data = pfc.rgb565_to_rgb888(data)
        #     img = data.reshape(imgHgt, pitch // 2, 3)
        #     img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # elif fmt == 'bgr565':
        #     data = pfc.rgb565_to_rgb888(data)
        #     img = data.reshape(imgHgt, pitch // 2, 3)
        else:
            raise ValueError('unsupported format: {} for file {}'.format(fmt, file))

        bgr = rgb[:, :, ::-1]
        cv2.imwrite(outfile, bgr)
    except Exception as e:
        print('Exception with file: {}, error: {}'.format(file, e))


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Convert raw image to png format')
    # parser.add_argument('file', type=str, help='raw image file')
    # parser.add_argument('--width', type=int, help='image width')
    # parser.add_argument('--height', type=int, help='image height')

    folder = "V:/hwpq_verify_data/vop_verify_data_from_wfy_20251230/csc/r2y/"
    files = os.listdir(folder)
    for file in files:
        suffix = file.split(".")[-1]
        if suffix.lower() in ['png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff']:
            continue

        print(f"converting '{file}' to png...")
        filename = os.path.join(folder, file)
        # convertRawImg2Png(filename, 512, 428, 512 * 3, "rgb")
        convertRawImg2Png(filename, 512, 428, 512, "yu24")

    print("Done.")

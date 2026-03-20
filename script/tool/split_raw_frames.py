#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@copyright: Copyright (c) Rockchip Electronics Co., Ltd. 2025-. All rights reserved.
@brief:     split_raw_frames.py - 分离 RAW 图像帧
@author:    vance.wu@rock-chips.com
@create:    2026-03-20
@modifier:  vance.wu@rock-chips.com
@modify:    2026-03-20
"""

import argparse
import os
import sys


def split_raw_frames(input_path, output_dir, prefix, frame_size, total_frames):
    """
    分离 RAW 图像帧
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        prefix: 文件名前缀
        frame_size: 每帧大小（字节）
        total_frames: 总帧数
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误：找不到输入文件 {input_path}")
        return False

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"开始分离 {total_frames} 帧，每帧 {frame_size} 字节...")

    try:
        with open(input_path, 'rb') as stream:
            cnt = 0
            for i in range(total_frames):
                # 生成文件名，格式为 _001, _002...
                file_name = f"{prefix}{i:03d}.yuv"
                full_path = os.path.join(output_dir, file_name)

                # 读取一帧的数据
                buffer = stream.read(frame_size)
                bytes_read = len(buffer)

                if bytes_read == frame_size:
                    # 写入新文件
                    with open(full_path, 'wb') as out_file:
                        out_file.write(buffer)
                    cnt += 1
                    print(f"成功生成: {file_name} (大小: {bytes_read} 字节)")
                else:
                    print(f"警告：第 {i} 帧读取不完整 (只读取了 {bytes_read} 字节)，文件可能已结束。")
                    break

        print("----------------------------------------")
        print(f"完成！共生成 {cnt} 个文件。")
        return True

    except IOError as e:
        print(f"发生错误: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='分离 RAW 图像帧')
    parser.add_argument('-i', '--input', type=str, default=None,
                        help='输入文件路径')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='输出目录')
    parser.add_argument('-p', '--prefix', type=str, default=None,
                        help='文件名前缀')
    parser.add_argument('-s', '--size', type=int, default=None,
                        help='每帧大小（字节）')
    parser.add_argument('-n', '--frames', type=int, default=None,
                        help='总帧数')

    args = parser.parse_args()

    # 配置路径和参数
    input_path = args.input if args.input else r"V:\hwpq_verify_data\vop_robin_fpga_verify_acm\input\testcombine_1920x1080_acm_fullrange_nv30_32frms.yuv"
    output_dir = args.output if args.output else r"V:\hwpq_verify_data\vop_robin_fpga_verify_acm\input\testcombine_32frms"
    prefix = args.prefix if args.prefix else "testcombine_1920x1080_acm_fullrange_nv30_frame_"
    frame_size = args.size if args.size else 7776000
    total_frames = args.frames if args.frames else 32

    # 执行分离
    split_raw_frames(input_path, output_dir, prefix, frame_size, total_frames)


if __name__ == '__main__':
    main()

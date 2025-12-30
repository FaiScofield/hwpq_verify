"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : sharp_chroma_boost.py
Author      : zxy@rock-chips.com
Date        : 2025-12-15
Description :
LastEditTime: 2025-12-15
"""

import os
import cv2
import numpy as np
from pathlib import Path

import numpy as np

# # BT.709 RGB -> YUV 线性变换矩阵（无偏移，仅线性部分）
# # Y = Kr*R + Kg*G + Kb*B
# # U = (B - Y) / (1 - Kb)   → 线性组合
# # V = (R - Y) / (1 - Kr)
# # Full-range BT.709 coefficients:
# Kr, Kg, Kb = 0.2126, 0.7152, 0.0722

# # 构建 RGB -> YUV 线性变换矩阵（不包含 128 偏移）
# M_RGB2YUV_linear = np.array([
#     [Kr,      Kg,      Kb     ],      # Y
#     [-Kr/(2*(1-Kb)), -Kg/(2*(1-Kb)), 0.5 ],  # U (scaled to [-0.5, 0.5])
#     [0.5, -Kg/(2*(1-Kr)), -Kb/(2*(1-Kr)) ]   # V
# ], dtype=np.float32)

# 但更常用的是直接使用标准 full-range 矩阵（简化版）：
# 参考 ITU-R BT.709 full range (0-255):
M_RGB2YUV = np.array([
    [ 0.2126,  0.7152,  0.0722],   # Y
    [-0.1146, -0.3854,  0.5000],   # U (already scaled for [-128,127] → +128 → [0,255])
    [ 0.5000, -0.4542, -0.0458]    # V
], dtype=np.float32)

# 计算逆矩阵：YUV (去偏移后) -> RGB
# 注意：YUV 输入需先减去 [0, 128, 128] 才能应用逆矩阵
# M_YUV2RGB = np.linalg.inv(M_RGB2YUV)

M_YUV2RGB = np.array([
    [1.0000,  0.0000,  1.5748],   # R = Y + 0*U' + 1.5748*V'
    [1.0000, -0.1873, -0.4681],   # G = Y -0.1873*U' -0.4681*V'
    [1.0000,  1.8556,  0.0000]    # B = Y + 1.8556*U' + 0*V'
], dtype=np.float32)


def rgb_yuv_transform(img, flag="rgb2yuv"):
    """
    使用 BT.709 full-range 矩阵进行 RGB ↔ YUV 转换。
    
    Args:
        img (np.ndarray): shape (H, W, 3), dtype uint8, range [0, 255]
        flag (str): "rgb2yuv" 或 "yuv2rgb"
    
    Returns:
        np.ndarray: 转换后的图像，same shape and dtype
    """
    if img.dtype != np.uint8:
        raise ValueError("Input must be uint8 in [0, 255]")

    img_f = img.astype(np.float32)
    H, W = img.shape[:2]

    if flag == "rgb2yuv":
        # Reshape from (H,W,3) to (H*W, 3)
        pixels = img_f.reshape(-1, 3)
        # Apply matrix: (N,3) @ (3,3).T → (N,3)
        yuv_linear = pixels @ M_RGB2YUV.T
        # Add offset to U and V
        yuv_linear[:, 1] += 128  # U
        yuv_linear[:, 2] += 128  # V
        out = yuv_linear.reshape(H, W, 3)

    elif flag == "yuv2rgb":
        # Remove offset from U and V
        img_f[:, :, 1] -= 128  # U
        img_f[:, :, 2] -= 128  # V
        pixels = img_f.reshape(-1, 3)
        # Apply inverse matrix
        rgb_linear = pixels @ M_YUV2RGB.T
        out = rgb_linear.reshape(H, W, 3)

    else:
        raise ValueError('flag must be "rgb2yuv" or "yuv2rgb"')

    # Clip and convert back
    out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    return out

def usm_sharpen(y_channel, strength=1.0, radius=3, threshold=10):
    """
    USM（Unsharp Mask）锐化算法处理Y通道
    Args:
        y_channel: Y通道数据
        strength: 锐化强度
        radius: 高斯模糊半径
        threshold: 锐化阈值，只有差异大于阈值时才进行锐化
    """
    # 高斯模糊
    blurred = cv2.GaussianBlur(y_channel, (0, 0), radius)

    # 计算差异
    diff = y_channel.astype(np.float32) - blurred.astype(np.float32)

    # 只对差异大于阈值的区域进行锐化
    mask = np.abs(diff) > threshold
    sharpened = y_channel.astype(np.float32) + strength * diff * mask

    # 钳位到合法范围并返回
    return np.clip(sharpened + 0.5, 0, 255).astype(np.uint8)

def chroma_boost_preserve_saturation(y_in, cb_in, cr_in, y_out, saturation_scale=1.0):
    """
    方案二：饱和度保持算法处理Cb、Cr通道
    通过控制色度向量的模长（饱和度）来避免失真
    """
    # 转换为float32进行计算
    y_in = y_in.astype(np.float32)
    cb_in = cb_in.astype(np.float32)
    cr_in = cr_in.astype(np.float32)
    y_out = y_out.astype(np.float32)

    # 计算原始饱和度（Cb, Cr构成的向量的模长）
    original_saturation = np.sqrt(cb_in**2 + cr_in**2)
    # 避免除零，给一个最小饱和度
    original_saturation = np.maximum(original_saturation, 1e-6)

    # 计算原始色度的方向（单位向量）
    cb_unit = cb_in / original_saturation
    cr_unit = cr_in / original_saturation

    # 计算目标饱和度：保持原始饱和度不变
    target_saturation = original_saturation * saturation_scale

    # 用新的饱和度和原始的方向，重构新的Cb, Cr
    cb_out = cb_unit * target_saturation
    cr_out = cr_unit * target_saturation

    # 钳位到YUV色度的合法范围（假设是8bit，Cb/Cr范围通常是16-240）
    cb_out = np.clip(cb_in + 0.5, 0, 255)
    cr_out = np.clip(cr_in + 0.5, 0, 255)

    return cb_out.astype(np.uint8), cr_out.astype(np.uint8)

def process_single_image(image_path, output_dir, usm_strength=1.5, usm_radius=2.0, usm_threshold=5):
    """处理单张图片"""
    try:
        # 读取图片
        original_rgb = cv2.imread(image_path)

        def imread_chinese(path):
            # 读取二进制数据
            with open(path, 'rb') as f:
                data = f.read()
            # 转为 numpy array
            nparr = np.frombuffer(data, np.uint8)
            # 解码图像
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img

        if original_rgb is None:
            original_rgb = imread_chinese(image_path)

        # both error
        if original_rgb is None and imread_chinese(image_path) is None:
            print(f"无法读取图片: {image_path}")
            return

        # 转换为RGB（OpenCV默认读取为BGR）, HWC
        original_rgb = cv2.cvtColor(original_rgb, cv2.COLOR_BGR2RGB)

        # RGB转YUV
        yuv_img = rgb_yuv_transform(original_rgb, flag="rgb2yuv")
        rgb_img = rgb_yuv_transform(yuv_img, flag="yuv2rgb")
        # 分离YUV通道
        y_in = yuv_img[:, :, 0]  # Y通道
        cb_in = yuv_img[:, :, 1]  # Cb通道
        cr_in = yuv_img[:, :, 2]  # Cr通道

        # 对Y通道进行USM锐化
        y_out = usm_sharpen(y_in, strength=usm_strength, radius=usm_radius, threshold=usm_threshold)

        # 计算saturation_scale = Y_out / Y_in，并限制在0.5-1.25之间
        ratio = y_out.astype(np.float32) / (y_in.astype(np.float32) + 1e-6)  # 避免除零
        saturation_scale = np.clip(ratio, 0.5, 1.25)

        # 使用方案二处理Cb、Cr通道
        cb_out, cr_out = chroma_boost_preserve_saturation(y_in, cb_in, cr_in, y_out, saturation_scale)

        # 合并YUV通道
        yuv_output = np.stack([y_out, cb_out, cr_out], axis=2)

        # YUV转回RGB
        result_rgb = rgb_yuv_transform(yuv_output, flag="yuv2rgb")

        # 生成输出文件名
        input_path = Path(image_path)
        output_filename = f"{input_path.stem}_chroma_boost2{input_path.suffix}"
        output_path = str(Path(output_dir) / output_filename)

        # 保存图片（转换回BGR格式用于保存）
        result_bgr = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR)
        ok = cv2.imwrite(output_path, result_bgr)
        print(f"处理完成: {input_path.name} -> {output_filename}, ok={ok}")

    except Exception as e:
        print(f"处理图片 {image_path} 时出错: {str(e)}")

def process_all_images(input_folder, output_folder, usm_strength=1.5, usm_radius=2.0, usm_threshold=5):
    """处理文件夹中的所有图片"""
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 支持的图片格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # filename = "00-fundation_(3)1.bmp"
        file_path = os.path.join(input_folder, filename)

        # 检查是否为支持的图片格式
        if os.path.isfile(file_path) and Path(filename).suffix.lower() in supported_formats:
            process_single_image(
                os.path.normpath(file_path),
                output_folder,
                usm_strength=usm_strength,
                usm_radius=usm_radius,
                usm_threshold=usm_threshold
            )

# 使用示例
if __name__ == "__main__":
    # 配置参数
    input_directory = "V:/CVTEPQ素材/第一轮评审素材"  # 输入图片文件夹路径
    output_directory = "G:/Project/pq/exp/chroma_boost"  # 输出图片文件夹路径

    # USM锐化参数调整（可根据需要调整）
    usm_params = {
        "usm_strength": 1.2,    # 锐化强度（建议0.5-2.0）
        "usm_radius": 1.5,      # 高斯模糊半径（建议1.0-3.0）
        "usm_threshold": 8      # 锐化阈值（建议5-15）
    }

    print("开始处理图片...")
    process_all_images(input_directory, output_directory, **usm_params)
    print("所有图片处理完成！")
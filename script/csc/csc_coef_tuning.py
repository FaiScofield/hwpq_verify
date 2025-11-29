"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : csc_coef_tuning.py
Author      : vance.wu@rock-chips.com
Date        : 2025-11-28
Description :
LastEditTime: 2025-11-29
"""

import sys
import argparse
import numpy as np
import get_csc_coefs as csc


def float_to_fixed_matrix(matF: np.ndarray, fix_bits: int = 8):
    scale = 1 << fix_bits
    # return np.round(F * scale).astype(np.int32)
    return (matF * scale + np.sign(matF) * 0.5).astype(np.int32)


def compute_rmse_for_matrix(matF: np.ndarray, matI: np.ndarray, depth: int = 8, fix_bits: int = 8):
    """
    计算给定整数矩阵M相对于浮点矩阵F的均方根误差
    遍历所有可能的RGB值(0-255)
    """
    src_range = 1 << depth  # 256/1024
    total_error = 0.0
    n_pixels = 0

    for r in range(src_range):
        for g in range(src_range):
            for b in range(src_range):
                rgb = np.array([r, g, b], dtype=np.int32)

                yuv_float = matF @ rgb.astype(np.float64)
                yuv_fixed = matI @ rgb
                yuv_fixed = (yuv_fixed + (1 << fix_bits - 1) + np.sign(yuv_fixed)) >> fix_bits

                # 累积误差
                error = yuv_float - yuv_fixed
                total_error += np.sum(error**2)
                n_pixels += 1

                # 每100万像素打印一次进度
                if n_pixels % 1000000 == 0:
                    print(f"已处理 {n_pixels // 1000000} 百万个像素, 进度: {n_pixels*100/src_range**3:.6f}%")

    rmse = np.sqrt(total_error / n_pixels)
    return rmse


def optimize_matrix_full(matF: np.ndarray, depth: int = 8, fix_bits: int = 8):
    """
    在初始矩阵M0的邻域内搜索更优的整数矩阵
    通过小范围遍历优化
    """
    M0 = float_to_fixed_matrix(matF, fix_bits)
    print(f"初始矩阵M0 ({fix_bits}bit定点):\n{M0}")

    print(f"计算初始矩阵RMSE...")
    initial_rmse = compute_rmse_for_matrix(matF, M0, depth, fix_bits)
    print(f"初始矩阵RMSE: {initial_rmse}")

    best_M = M0.copy()
    best_rmse = initial_rmse

    # 对每个矩阵元素进行小范围搜索
    print("开始局部优化搜索...")

    # 迭代 todo: 用 Mx3矩阵 x M, 加快计算。 引入最小二乘？ 可以根据R2Y/Y2R矩阵特性来限制要微调的位置？
    for i in range(3):
        for j in range(3):
            print(f"正在计算像素 [{i}, {j}]...")
            for delta in [-1, +1]:
                TM = M0.copy()
                TM[i, j] = M0[i, j] + delta

                # 计算当前矩阵的MSE（这里为了效率可以使用采样）
                # 但为了精确比较, 我们仍使用全遍历
                current_rmse = compute_rmse_for_matrix(matF, TM, depth, fix_bits)

                if current_rmse < best_rmse:
                    print(f"找到更优矩阵: 元素({i},{j})由{best_M[i, j]}调整为{TM[i, j]}, RMSE: {current_rmse}")
                    best_rmse = current_rmse
                    best_M = TM.copy()

    return best_M, best_rmse, initial_rmse


def optimize_matrix_random(matF: np.ndarray, depth: int = 8, fix_bits: int = 8):
    M0 = float_to_fixed_matrix(matF, fix_bits)
    print(f"初始矩阵M0:\n{M0}")

    # 由于全遍历计算量巨大, 我们只演示一个小范围的优化
    # 实际应用中, 全遍历所有RGB组合(16M)是不现实的
    # 所以我们改为验证方法对比

    # 为了效率, 我们使用采样方法验证
    sample_size = 10000  # 使用1万个随机采样点
    total_error = 0.0
    np.random.seed(42)  # 固定随机种子以便复现
    print(f"\n计算M0的MSE... (使用随机采样验证, 采样深度: {depth}bit, 采样点数: {sample_size})")

    MF = np.array(matF, dtype=np.float64)
    MI = np.array(M0, dtype=np.int32)
    src_range = 1 << depth  # 256/1024

    for _ in range(sample_size):
        rgb = np.random.randint(0, src_range, size=3).astype(np.int32)

        yuv_float = MF @ rgb.astype(np.float64)
        yuv_fixed = MI @ rgb
        yuv_fixed = (yuv_fixed + (1 << fix_bits - 1) + np.sign(yuv_fixed)) >> fix_bits

        error = yuv_float - yuv_fixed
        total_error += np.sum(error**2)

    sampled_rmse = np.sqrt(total_error / sample_size)
    print(f"采样RMSE (M0): {sampled_rmse}")

    # 现在我们尝试一个小规模的邻域搜索优化
    print("\n尝试邻域优化 (只对单个元素进行+1/-1调整):")

    # 为了演示, 我们手动尝试一些微小调整
    best_M = M0.copy()
    best_rmse = sampled_rmse

    print("尝试对每个元素进行+1/-1调整...")

    for i in range(3):
        for j in range(3):
            for delta in [-1, 1]:
                TM = M0.copy()
                TM[i, j] = M0[i, j] + delta

                # 计算采样MSE
                total_error = 0.0
                MTI = np.array(TM, dtype=np.int32)

                for _ in range(sample_size):
                    rgb = np.random.randint(0, src_range, size=3).astype(np.int32)

                    yuv_float = MF @ rgb.astype(np.float64)
                    yuv_fixed = MTI @ rgb
                    yuv_fixed = (yuv_fixed + (1 << fix_bits - 1) + np.sign(yuv_fixed)) >> fix_bits

                    error = yuv_float - yuv_fixed
                    total_error += np.sum(error**2)

                current_rmse = np.sqrt(total_error / sample_size)
                if current_rmse < best_rmse:
                    print(f"找到改进: 元素({i},{j})由{best_M[i, j]}调整为{TM[i, j]}, MSE: {current_rmse}")
                    best_rmse = current_rmse
                    best_M = TM.copy()

    return best_M, best_rmse, sampled_rmse


def test_csc_coef_tuning(depth: int, fix_bits: int, mode_str: str):

    if mode_str in csc.g_supported_standard_convert_modes:
        csc_config = csc.CscCoefConfig()
        csc_config.pixel_depth = depth
        csc_config.coef_precision = 0
        csc_config.tune_fix_coefs = False
        csc_config.platform = "RK3572"  # RK3576/RK3572/RK3538
        csc_config.csc_mode = csc.g_supported_standard_convert_modes[mode_str]
        matF, _ = csc.get_csc_coefs(csc_config, None)
        print(f"使用系数: {mode_str}:")
    else:
        # ITU-R BT.601 R2Y_L2L
        matF = np.array([[0.299, 0.587, 0.114], [-0.172588, -0.338827, 0.511416], [0.511416, -0.428247, -0.083169]])
        print("使用系数: ITU-R BT.601 R2Y_L2L:")
    print(matF)

    # 方法1: 直接round(F*256)
    M0 = float_to_fixed_matrix(matF, fix_bits)
    # print(f"\n初始定点化矩阵 (定点精度{fix_bits}bit): ")
    # print(M0)

    best_M, best_rmse, initial_rmse = optimize_matrix_random(matF, depth, fix_bits)
    # best_M, best_rmse, initial_rmse = optimize_matrix_full(matF, depth, fix_bits)

    if np.all(best_M == M0):
        print("\n无需改进。")
    else:
        print(f"\n最终优化后的矩阵:")
        print(best_M)
        print(f"优化后RMSE: {best_rmse}")
        print(f"相对改进: {(initial_rmse - best_rmse) / initial_rmse * 100:.6f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--mode", type=str, default="", help="a single csc mode string, like: '601f_to_rgbl/rgbf_to_2020f' ...)"
    )
    parser.add_argument("-p", "--precision", type=int, default=8, help="the fixed coef precision bits 0 or [8, 16]")
    parser.add_argument("-d", "--depth", type=int, default=8, help="the pixel depth bits [8, 16]")
    parser.print_usage()
    args, _ = parser.parse_known_args()

    test_csc_coef_tuning(args.depth, args.precision, args.mode)

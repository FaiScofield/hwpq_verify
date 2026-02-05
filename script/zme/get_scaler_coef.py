"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : get_scaler_coef.py
Author      : vance.wu@rock-chips.com
Date        : 2026-01-23
Description : 计算图像插值系数 (Bicubic/Lanczos)
LastEditTime: 2026-01-23
"""

import numpy as np
import argparse
from math import sin, pi


def lanczos_weight(x, a=3):
    """
    计算 Lanczos 插值权重系数
    参数:
        x: 距离，通常为浮点数或数组
        a: 窗口半径参数，默认为 3（常用值）
    返回:
        对应的权重系数
    """
    x = abs(x)
    if x == 0:
        return 1.0
    elif x < a:
        return a * sin(pi * x) * sin(pi * x / a) / (pi * pi * x * x)
    else:
        return 0.0


def compute_lanczos_weights(dx, dy, a=3):
    """
    计算二维 Lanczos 插值所需的 2a x 2a 权重矩阵
    参数:
        dx: 水平方向的小数偏移量
        dy: 垂直方向的小数偏移量
        a: 窗口半径参数
    返回:
        2ax2a 权重矩阵
    """
    # 根据参数 a 确定邻域大小
    x_idx = np.arange(-a, a)
    y_idx = np.arange(-a, a)
    wx = np.array([lanczos_weight(x - dx, a) for x in x_idx])
    wy = np.array([lanczos_weight(y - dy, a) for y in y_idx])
    # 外积得到二维权重
    w = np.outer(wy, wx)
    return w


def bicubic_weight(x, a=-0.5):
    """
    计算 Bicubic 插值权重系数
    参数:
        x: 距离，通常为浮点数或数组
        a: 锐化参数，默认 -0.5（常用值）
    返回:
        对应的权重系数
    """
    x = np.abs(x)

    res = np.zeros_like(x)
    res_le1 = (a + 2) * x**3 - (a + 3) * x**2 + 1
    res_le2 = a * x**3 - 5 * a * x**2 + 8 * a * x - 4 * a

    res[x <= 1] = res_le1[x <= 1]
    res[(x > 1) & (x <= 2)] = res_le2[(x > 1) & (x <= 2)]

    return res


def compute_bicubic_weights(dx, dy, a=-0.5):
    """
    计算二维 Bicubic 插值所需的 4x4 权重矩阵
    参数:
        dx: 水平方向的小数偏移量
        dy: 垂直方向的小数偏移量
        a: 锐化参数
    返回:
        4x4 权重矩阵（如果 dx 是列表，则返回多个权重矩阵）
    """

    # 周围 4x4 邻域的相对坐标
    x_idx = np.arange(-1, 3)
    y_idx = np.arange(-1, 3)

    if dy == 0:
        w = np.zeros((len(dx), 4))
        for i in range(len(dx)):
            wx = np.array([bicubic_weight(x - dx[i], a) for x in x_idx])
            w[i, :] = wx
    else:
        wy = np.array([bicubic_weight(y - dy, a) for y in y_idx])
        w = np.zeros((len(dx), 4, 4))
        for i in range(len(dx)):
            wx = np.array([bicubic_weight(x - dx[i], a) for x in x_idx])
            w[i, :, :] = np.outer(wy, wx)

    return w


def inverse_bicubic_weight(weight, a=-0.5, tolerance=1e-6):
    """
    已知 bicubic 权重和系数 a，求解 x 值
    参数:
        weight: 已知的权重值
        a: 锐化参数
        tolerance: 数值求解的容差
    返回:
        满足条件的 x 值（可能有多个解，返回第一个找到的）
    """
    import numpy as np

    # 定义误差函数，我们需要找到使此函数接近零的 x 值
    def error_func(x):
        return bicubic_weight(x, a) - weight

    # 根据分段函数定义，在不同的区间内搜索解
    solutions = []

    # 在区间 [0, 1] 内搜索，即 x <= 1 的情况
    # 这里我们使用数值方法求解: (a + 2) * x^3 - (a + 3) * x^2 + 1 = weight
    # 即 (a + 2) * x^3 - (a + 3) * x^2 + (1 - weight) = 0
    # 使用numpy的roots函数求解多项式根
    coeffs_case1 = [a + 2, -(a + 3), 0, 1 - weight]  # [x^3, x^2, x^1, x^0]
    roots_case1 = np.roots(coeffs_case1)

    for root in roots_case1:
        if np.isreal(root):
            x_real = np.real(root)
            if -tolerance <= x_real <= 1 + tolerance and abs(error_func(x_real)) < tolerance:
                solutions.append(x_real)

    # 在区间 (1, 2] 内搜索，即 1 < x <= 2 的情况
    # 这里我们求解: a * x^3 - 5 * a * x^2 + 8 * a * x - 4 * a = weight
    # 即 a * x^3 - 5 * a * x^2 + 8 * a * x - 4 * a - weight = 0
    coeffs_case2 = [a, -5 * a, 8 * a, -4 * a - weight]
    roots_case2 = np.roots(coeffs_case2)

    for root in roots_case2:
        if np.isreal(root):
            x_real = np.real(root)
            if 1 - tolerance < x_real <= 2 + tolerance and abs(error_func(x_real)) < tolerance:
                solutions.append(x_real)

    # 如果在正区间没有找到解，检查负区间（因为abs(x)函数的原因）
    # 对于负数，bicubic_weight使用的是abs(x)，所以负数的解与正数相同
    if len(solutions) == 0:
        # 尝试更广泛的搜索范围
        for x in np.linspace(-2, 2, 1000):
            if abs(error_func(x)) < tolerance:
                solutions.append(x)

    # 返回第一个有效解，优先返回正值
    if solutions:
        positive_solutions = [s for s in solutions if s >= 0]
        if positive_solutions:
            return min(positive_solutions, key=lambda x: abs(error_func(x)))
        else:
            return min(solutions, key=lambda x: abs(error_func(x)))
    else:
        return None  # 没有找到解


def demo_weights():
    """
    演示不同参数下的 Bicubic 权重计算
    """
    print("不同锐化参数 a 下的 Bicubic 权重（距离 0.5）:")
    for a in [-1, -0.75, -0.5, -0.25, 0]:
        print(f"a={a:4.2f}: weight={bicubic_weight(0.5, a):7.4f}")

    print("\n二维 Bicubic 权重矩阵示例 (dx=0.3, dy=0.7, a=-0.5):")
    w = compute_bicubic_weights([0.3], 0.7, a=-0.5)
    print(np.round(w, 4))

    print("\nLanczos 权重（距离 0.5, a=3）:")
    print(f"Lanczos weight: {lanczos_weight(0.5, 3):7.4f}")

    print("\n二维 Lanczos 权重矩阵示例 (dx=0.3, dy=0.7, a=3):")
    w = compute_lanczos_weights(0.3, 0.7, a=3)
    print(np.round(w, 4))

    print("\nBicubic 反向计算示例 (从权重值求解 x):")
    test_weight = bicubic_weight(0.5, -0.5)
    calculated_x = inverse_bicubic_weight(test_weight, -0.5)
    print(f"原始 x=0.5, 对应权重={test_weight:.4f}, 反向计算的 x={calculated_x:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="计算图像插值系数 (Bicubic/Lanczos)")
    parser.add_argument("-m", "--method", type=str, choices=['bicubic', 'lanczos'], default='bicubic',
                        help="插值方法: bicubic 或 lanczos")
    parser.add_argument("-x", "--dx", type=float, nargs='+',
                        help="水平方向小数偏移量 (支持向量)")
    parser.add_argument("-y", "--dy", type=float, default=0,
                        help="垂直方向小数偏移量 (标量，默认: 0)")
    parser.add_argument("-X", "--dx_num", type=int, default=0,
                        help="水平方向小数偏移总量 (默认: 0)")
    parser.add_argument("-a", type=float, default=None,
                        help="插值参数: 对于bicubic是锐化参数(默认-0.5)，对于lanczos是窗口半径(默认3)")
    parser.add_argument("-p", "--precision", type=int, default=0,
                        help="定点化精度位数，(默认: 0, 不进行定点化)")
    parser.add_argument("-w", "--weight", type=float,
                        help="设置权重，反向求取dx")
    parser.add_argument("--norm", action="store_true", help="系数归一化")
    parser.add_argument("--demo", action="store_true",
                        help="运行演示模式，展示各种权重计算")

    args = parser.parse_args()

    if args.demo:
        demo_weights()
    else:
        if args.method == 'bicubic':
            if args.a is None:
                args.a = -0.5  # 默认bicubic参数

            if args.weight is not None:
                res = inverse_bicubic_weight(args.weight, args.a)
                print(f"get dx from inverse_bicubic_weight: {res:.6f}")
                exit(0)

            if args.dx_num > 0:
                dx = np.linspace(0, 1, args.dx_num)
                print(f"dx: {dx}, len: {len(dx)}")
            else:
                dx = args.dx
            dy = args.dy
            weights = compute_bicubic_weights(dx, dy, args.a)
            print(f"Bicubic weights (dx={dx}, dy={dy}, a={args.a}):")
        else:  # lanczos
            if args.a is None:
                args.a = 3  # 默认lanczos参数
            weights = compute_lanczos_weights(args.dx, args.dy, int(args.a))
            print(f"Lanczos weights (dx={args.dx}, dy={args.dy}, a={int(args.a)}):")

        # 归一化
        if args.norm:
            if weights.ndim > 2:
                # 对多维权重逐层归一化
                for i in range(weights.shape[0]):
                    weights[i] /= np.sum(weights[i])
            elif args.dy == 0:
                # 对单维权重归一化 - 每行单独归一化
                row_sums = np.sum(weights, axis=1, keepdims=True)
                # 避免除以零的情况
                row_sums[row_sums == 0] = 1
                weights /= row_sums
            else:
                weights /= np.sum(weights)

        # 如果指定了精度，则进行定点化处理
        if args.precision > 0:
            scale_factor = 2 ** args.precision
            weights = (weights * scale_factor + 0.5 * np.sign(weights)).astype(int)
            print(f"Fixed-point coefficients (Q.{args.precision}):")
        else:
            # 浮点系数，保留4位小数，禁用科学计数法
            np.set_printoptions(precision=6, suppress=True)
        print(weights)

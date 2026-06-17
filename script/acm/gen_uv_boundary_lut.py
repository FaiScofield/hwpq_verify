import numpy as np
import matplotlib.pyplot as plt

# ====== 解决 matplotlib 中文显示问题 ======
# Windows 系统常用中文字体：Microsoft YaHei (微软雅黑), SimHei (黑体)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
# 解决保存图像时负号 '-' 显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False
# ==============================


# YCbCr -> RGB conversion coefficients for boundary computation.
# (R_cr, G_cb, G_cr, B_cb) = coefficients for:
#   R = Y + R_cr * Cr
#   G = Y - G_cb * Cb - G_cr * Cr
#   B = Y + B_cb * Cb
_COEFFS = {
    "bt601": (1.402, 0.344, 0.714, 1.772),
    "bt709": (1.5748, 0.187324, 0.468124, 1.8556),
}


def compute_max_radius(Y, H, standard: str = "bt709"):
    """
    Compute the maximum legal radius r in the UV plane for a given
    normalised luma Y in [0, 1] and hue angle H in radians.

    Parameters
    ----------
    standard : str
        "bt601" or "bt709" (default).  Selects the YCbCr->RGB matrix
        coefficients used for the gamut boundary inequalities.
    """
    if standard not in _COEFFS:
        raise ValueError(f"unknown standard: {standard!r}, must be bt601 or bt709")
    rc, gc, gc2, bc = _COEFFS[standard]

    cos_h = np.cos(H)
    sin_h = np.sin(H)

    # 初始设为极大值（相当于无约束）
    max_r = 10.0
    eps = 1e-12  # 防止除零

    # ----- 约束 1: 0 <= R <= 1 -----
    # R = Y + rc * r * sin(H)
    # R <= 1  =>  rc * sin * r <= 1 - Y
    if sin_h > eps:
        max_r = min(max_r, (1.0 - Y) / (rc * sin_h))
    # R >= 0  =>  -rc * sin * r <= Y  (当 sin < 0 时左侧为正)
    if sin_h < -eps:
        max_r = min(max_r, Y / (-rc * sin_h))

    # ----- 约束 2: 0 <= G <= 1 -----
    # G = Y - gc * r * cos(H) - gc2 * r * sin(H)
    # 合并系数: coeff_G = -gc*cos - gc2*sin
    coeff_g = -gc * cos_h - gc2 * sin_h
    # G <= 1  =>  coeff_g * r <= 1 - Y
    if coeff_g > eps:
        max_r = min(max_r, (1.0 - Y) / coeff_g)
    # G >= 0  =>  -coeff_g * r <= Y  =>  (gc*cos + gc2*sin) * r <= Y
    coeff_g_neg = -coeff_g  # 即 gc*cos + gc2*sin
    if coeff_g_neg > eps:
        max_r = min(max_r, Y / coeff_g_neg)

    # ----- 约束 3: 0 <= B <= 1 -----
    # B = Y + bc * r * cos(H)
    # B <= 1  =>  bc * cos * r <= 1 - Y
    if cos_h > eps:
        max_r = min(max_r, (1.0 - Y) / (bc * cos_h))
    # B >= 0  =>  -bc * cos * r <= Y  (当 cos < 0 时左侧为正)
    if cos_h < -eps:
        max_r = min(max_r, Y / (-bc * cos_h))

    # 安全保护：归一化 UV 空间的理论最大半径不会超过 0.5（实际六边形内切于圆）
    # 如果因为数值原因 max_r 仍为 10，强制设为 0.5
    # if max_r > 0.5:
    #     max_r = 0.5

    # 防止数值下溢为负数
    return max(0.0, max_r)


def generate_uv_boundary_lut(y_bins=256, h_bins=360, standard: str = "bt709"):
    """
    Generate a UV boundary look-up table.

    Args:
        y_bins: Y quantization levels (default 256, for 8-bit Y 0~255)
        h_bins: H quantization levels (default 360, for angle 0~359°)
        standard: "bt601" or "bt709" (default).  YCbCr->RGB matrix.

    Returns:
        lut: (y_bins, h_bins) uint8 array, radius in 8-bit UV pixel offset (0~127).
    """
    lut = np.zeros((y_bins, h_bins), dtype=np.uint8)

    for y_idx in range(y_bins):
        # Y 归一化到 [0, 1]
        Y = y_idx / (y_bins - 1) if y_bins > 1 else 0.0

        for h_idx in range(h_bins):
            # 角度转为弧度
            H = np.radians(h_idx)

            # 计算归一化半径
            r_norm = compute_max_radius(Y, H, standard=standard)

            # 映射回 8-bit UV 偏移值 (U-128 或 V-128 的范围)
            # 归一化 r 对应的是 u = r*cos, v = r*sin，其中 u,v 范围约 [-0.5, 0.5]
            # 所以 U_pixel = u * 255，最大半径约为 0.5 * 255 = 127.5
            r_pixel = r_norm * 255.0

            lut[y_idx, h_idx] = int(round(np.clip(r_pixel, 0, 127)))

    return lut


def plot_boundary_for_y(Y_values, standard: str = "bt709"):
    angles_deg = np.linspace(0, 360, 360)
    fig, axes = plt.subplots(1, len(Y_values), figsize=(15, 4))

    for idx, Y in enumerate(Y_values):
        radii = []
        for deg in angles_deg:
            r = compute_max_radius(Y, np.radians(deg), standard=standard)
            radii.append(r)

        # 转成直角坐标 u = r*cos, v = r*sin
        u = np.array(radii) * np.cos(np.radians(angles_deg))
        v = np.array(radii) * np.sin(np.radians(angles_deg))

        axes[idx].plot(u, v, 'b-', linewidth=2)
        axes[idx].set_title(f'Y = {Y:.1f}')
        axes[idx].set_aspect('equal')
        axes[idx].grid(True)
        axes[idx].set_xlim(-0.6, 0.6)
        axes[idx].set_ylim(-0.6, 0.6)

    plt.tight_layout()
    plt.show()


# ============================================
# 主程序：生成 LUT 并可视化
# ============================================
if __name__ == "__main__":
    # # 1. 生成 LUT (256x360)
    # print("正在生成 UV Boundary LUT (256x360)...")
    # lut = generate_uv_boundary_lut(y_bins=256, h_bins=360)

    # # 2. 打印 LUT 的统计信息
    # print(f"LUT 形状: {lut.shape}")
    # print(f"LUT 数据类型: {lut.dtype}")
    # print(f"有效半径最小值: {np.min(lut)}")
    # print(f"有效半径最大值: {np.max(lut)}")
    # print(f"有效半径平均值: {np.mean(lut):.2f}")

    # # 3. 可视化 LUT（热力图）
    # plt.figure(figsize=(12, 6))

    # # 横轴为色相角度 H (0~360°)，纵轴为亮度 Y (0~255)
    # plt.imshow(lut, aspect='auto', cmap='jet', extent=[0, 360, 255, 0], interpolation='nearest')  # 让 Y=0 在顶部
    # plt.colorbar(label='最大 UV 半径 (像素偏移值)')
    # plt.xlabel('色相角度 H (度)')
    # plt.ylabel('亮度 Y (0~255)')
    # plt.title('YUV 六棱柱 UV 平面边界最大半径 LUT')

    # # 标注关键亮度线 (Y=16 黑, Y=128 中灰, Y=235 白 对应 limited range)
    # plt.axhline(y=16, color='white', linestyle='--', linewidth=0.8, alpha=0.5)
    # plt.axhline(y=128, color='white', linestyle='--', linewidth=0.8, alpha=0.5)
    # plt.axhline(y=235, color='white', linestyle='--', linewidth=0.8, alpha=0.5)
    # plt.text(362, 16, 'Y=16', color='white', fontsize=8)
    # plt.text(362, 128, 'Y=128', color='white', fontsize=8)
    # plt.text(362, 235, 'Y=235', color='white', fontsize=8)

    # plt.tight_layout()
    # plt.savefig('uv_boundary_lut.png', dpi=150)
    # plt.show()

    # # 4. （可选）保存 LUT 为二进制文件，供硬件加载
    # # lut.tofile('uv_boundary_lut.bin')
    # # print("LUT 已保存为 uv_boundary_lut.bin")

    # # 5. 打印几个典型值供验证
    # print("\n典型值验证（归一化半径 r，乘以255后为像素值）：")
    # # Y=0.5 (idx=128), H=45° (idx=45)
    # r = compute_max_radius(0.5, np.radians(45))
    # print(f"Y=0.5, H=45° -> 归一化 r={r:.4f}, 像素半径={r*255:.1f}")
    # # Y=0.0 (纯黑), H=任意
    # r = compute_max_radius(0.0, np.radians(45))
    # print(f"Y=0.0, H=45° -> 归一化 r={r:.4f}, 像素半径={r*255:.1f}")
    # # Y=1.0 (纯白), H=任意
    # r = compute_max_radius(1.0, np.radians(45))
    # print(f"Y=1.0, H=45° -> 归一化 r={r:.4f}, 像素半径={r*255:.1f}")

    # 测试典型的 5 个亮度层
    plot_boundary_for_y([0.1, 0.3, 0.5, 0.7, 0.9])

import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

g_r2y_mat_bt709 = np.array(
    [[0.2126, 0.7152, 0.0722], [-0.114572, -0.385428, 0.5], [0.5, -0.454153, -0.045847]], dtype=np.float32
)

g_y2r_mat_bt709 = np.array([
    [1.0,  0.0,      1.5748],
    [1.0, -0.187324,  -0.468124],
    [1.0,  1.8556,   0.0   ]
], dtype=np.float32)

def ycbcr2rgb(y, cb, cr):
    """
    将 YCbCr 转换到 RGB，输入为标量或数组，返回 0~255 的 uint8 RGB
    ITU-R BT.709 标准，使用矩阵乘法
    """
    y = np.asarray(y, dtype=np.float32)
    cb = np.asarray(cb, dtype=np.float32)
    cr = np.asarray(cr, dtype=np.float32)

    # 组合 YCbCr 分量为 (..., 3) 形状
    ycbcr_stacked = np.stack([y, cb, cr], axis=-1)

    # 保存原始形状用于后续恢复
    original_shape = ycbcr_stacked.shape

    # 将输入重塑为二维矩阵，便于矩阵乘法
    ycbcr_flat = ycbcr_stacked.reshape(-1, 3)  # (N, 3)

    # 执行矩阵乘法: (N, 3) x (3, 3) -> (N, 3)
    rgb_flat = np.dot(ycbcr_flat, g_y2r_mat_bt709.T)  # 注意转置以实现正确的矩阵乘法

    # 恢复原始形状
    rgb = rgb_flat.reshape(original_shape)

    # 分离R、G、B通道
    r = rgb[..., 0] + 0.5
    g = rgb[..., 1] + 0.5
    b = rgb[..., 2] + 0.5

    # 裁剪并转 uint8
    r = np.clip(r, 0, 255).astype(np.uint8)
    g = np.clip(g, 0, 255).astype(np.uint8)
    b = np.clip(b, 0, 255).astype(np.uint8)
    return r, g, b


def hsv2rgb(h, s, v):
    """
    将 HSV 转换到 RGB，输入为标量或数组，返回 0~255 的 uint8 RGB
    h: 0~360, s: 0~1, v: 0~1
    """
    h = np.asarray(h, dtype=np.float32) % 360
    s = np.asarray(s, dtype=np.float32)
    v = np.asarray(v, dtype=np.float32)

    c = v * s
    x = c * (1 - np.abs((h / 60) % 2 - 1))
    m = v - c

    r = np.zeros_like(h)
    g = np.zeros_like(h)
    b = np.zeros_like(h)

    cond = (h >= 0) & (h < 60)
    r[cond] = c[cond]; g[cond] = x[cond]; b[cond] = 0

    cond = (h >= 60) & (h < 120)
    r[cond] = x[cond]; g[cond] = c[cond]; b[cond] = 0

    cond = (h >= 120) & (h < 180)
    r[cond] = 0; g[cond] = c[cond]; b[cond] = x[cond]

    cond = (h >= 180) & (h < 240)
    r[cond] = 0; g[cond] = x[cond]; b[cond] = c[cond]

    cond = (h >= 240) & (h < 300)
    r[cond] = x[cond]; g[cond] = 0; b[cond] = c[cond]

    cond = (h >= 300) & (h < 360)
    r[cond] = c[cond]; g[cond] = 0; b[cond] = x[cond]

    r = ((r + m) * 255).astype(np.uint8)
    g = ((g + m) * 255).astype(np.uint8)
    b = ((b + m) * 255).astype(np.uint8)
    return r, g, b


# ---------- 画图通用工具 ----------
def draw_axis(img_draw, W, H, margin, x0, y0, x_range, y_range, xlabel, ylabel, font=None):
    """
    在 PIL ImageDraw 上画坐标轴与刻度
    x0,y0: 原点像素坐标
    x_range: (xmin, xmax) 数据范围
    y_range: (ymin, ymax) 数据范围
    """
    # 轴颜色
    axis_color = (0, 0, 0)
    # 刻度颜色
    tick_color = (64, 64, 64)

    hm = margin // 4

    # X 轴 - 从左到右穿过中心点
    img_draw.line([(margin - hm, y0 + margin), (W + margin + hm, y0 + margin)], fill=axis_color, width=2)
    # Y 轴 - 从上到下穿过中心点
    img_draw.line([(x0 + margin, H + margin + hm), (x0 + margin, margin - hm)], fill=axis_color, width=2)

    # 刻度
    nx, ny = 9, 9
    for i in range(nx):
        x_data = x_range[0] + i * (x_range[1] - x_range[0]) / (nx - 1)
        x_pix = int(i * (W - 1) / (nx - 1))
        img_draw.line([(x_pix + margin, y0 + margin - 3), (x_pix + margin, y0 + margin + 3)], fill=tick_color, width=1)
        if font:
            img_draw.text((x_pix + margin - 5, y0 + margin + 5), f"{int(x_data)}", fill=tick_color, font=font)

    for j in range(ny):
        y_data = y_range[0] + j * (y_range[1] - y_range[0]) / (ny - 1)
        y_pix = int((H - 1) - j * (H - 1) / (ny - 1))
        img_draw.line([(x0 + margin - 3, y_pix + margin), (x0 + margin + 3, y_pix + margin)], fill=tick_color, width=1)
        if font:
            img_draw.text((x0 + margin + 5, y_pix + margin - 5), f"{int(y_data)}", fill=tick_color, font=font)

    # 标签
    if font:
        img_draw.text((W + margin + hm, y0 - 15 + margin), xlabel, fill=axis_color, font=font)
        img_draw.text((x0 + margin - 20, margin - hm), ylabel, fill=axis_color, font=font)


# ---------- 四个生成函数 ----------
def gen_img_ycbcr2rgb_coor(y=128, scale=2.0, out_path=None):
    """
    横坐标 Cb∈[-128,127]，纵坐标 Cr∈[-128,127]，固定亮度 y
    """
    if out_path is None:
        out_path = f"ycbcr2rgb_coor_y{y}.png"
    base = 256
    # 修复坐标轴方向问题：图像中 y 轴向下为正，但我们需要 y 轴（Cr）向上为正
    cb_grid, cr_grid = np.meshgrid(np.arange(-128, 128), np.arange(127, -129, -1), indexing='xy')
    y = np.ones_like(cb_grid) * y
    r, g, b = ycbcr2rgb(y, cb_grid, cr_grid)
    rgb = np.stack([r, g, b], axis=-1)  # (256,256,3)

    img = Image.fromarray(rgb, mode="RGB")
    img = img.resize((int(scale * base), int(scale * base)), Image.BICUBIC)

    # 添加边距的图像
    margin = 64
    padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
    padded_img.paste(img, (margin, margin))

    # 画坐标轴
    draw = ImageDraw.Draw(padded_img)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = None
    # 坐标轴中心点在图像中心
    x0 = int(img.width / 2)  # 图像中心x坐标
    y0 = int(img.height / 2)  # 图像中心y坐标
    draw_axis(draw, img.width, img.height, margin, x0, y0,
              (-128, 127), (-128, 127), "Cb", "Cr", font)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_ybyh_coor(s=1.0, scale=2.0, out_path=None):
    """
    横坐标 H∈[-180,179]，纵坐标 dy∈[-255,255]，固定饱和度 s
    实际 y = 128 + dy
    """
    if out_path is None:
        out_path = "ybyh_coor.png"
    base = 256
    h_grid, dy_grid = np.meshgrid(np.linspace(-180, 179, base),
                                  np.linspace(-255, 255, base))
    y_val = 128 + dy_grid
    # 将 y 限制在 [0, 255] 范围内，并归一化到 [0, 1]
    y_val = np.clip(y_val, 0, 255)
    v = y_val / 255.0
    r, g, b = hsv2rgb(h_grid, s, v)
    rgb = np.stack([r, g, b], axis=-1)

    img = Image.fromarray(rgb, mode="RGB")
    img = img.resize((int(scale * base), int(scale * base)), Image.NEAREST)

    # 添加边距的图像
    margin = 64
    padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
    padded_img.paste(img, (margin, margin))

    draw = ImageDraw.Draw(padded_img)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = None
    x0 = int(margin + scale * (180 / 360 * base))  # H 轴原点，加上左边距
    y0 = int(margin + scale * (255 / 510 * base))  # dy 轴原点 (dy=0 时 y=128 的位置)，加上上边距
    draw_axis(draw, padded_img.width, padded_img.height, x0, y0,
              (-180, 179), (-255, 255), "H", "dy", font)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_sbyh_coor(y=128, scale=2.0, out_path=None):
    """
    横坐标 H∈[-180,179]，纵坐标为 ds 值，范围[-1, 1]，固定亮度 y
    s 对应为 0.5+ds，画出坐标轴
    """
    if out_path is None:
        out_path = "sbyh_coor.png"
    base = 256
    h_grid, ds_grid = np.meshgrid(np.linspace(-180, 179, base),
                                  np.linspace(-1, 1, base))
    s_val = 0.5 + ds_grid
    # 将 s 限制在 [0, 1] 范围内
    s_val = np.clip(s_val, 0, 1)
    # 将 y 归一化到 0~1，色相已在正确范围内
    v = y / 255.0
    r, g, b = hsv2rgb(h_grid, s_val, v)
    rgb = np.stack([r, g, b], axis=-1)

    img = Image.fromarray(rgb, mode="RGB")
    img = img.resize((int(scale * base), int(scale * base)), Image.NEAREST)

    # 添加边距的图像
    margin = 64
    padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
    padded_img.paste(img, (margin, margin))

    draw = ImageDraw.Draw(padded_img)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = None
    x0 = int(margin + scale * (180 / 360 * base))  # H 轴原点，加上左边距
    y0 = int(margin + scale * base / 2)  # ds 轴原点 (ds=0 时的位置)，加上上边距
    draw_axis(draw, padded_img.width, padded_img.height, x0, y0,
              (-180, 179), (-1, 1), "H", "ds", font)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_hbyh_coor(y=128, s=0.5, scale=2.0, out_path=None):
    """
    横坐标 H 值，范围[-180, 179]，纵坐标为 dh 值，范围[-180, 180]
    给定亮度 y 和饱和度 s，画出坐标轴
    """
    if out_path is None:
        out_path = "hbyh_coor.png"
    base = 256
    h_base = np.linspace(-180, 179, base)
    dh_grid, h_grid = np.meshgrid(np.linspace(-180, 180, base),
                                  h_base)
    # 计算实际的 H 值为 h + dh
    actual_h = (h_grid + dh_grid) % 360
    # 将 y 归一化到 0~1
    v = y / 255.0
    r, g, b = hsv2rgb(actual_h, s, v)
    rgb = np.stack([r, g, b], axis=-1)

    img = Image.fromarray(rgb, mode="RGB")
    img = img.resize((int(scale * base), int(scale * base)), Image.NEAREST)

    # 添加边距的图像
    margin = 64
    padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
    padded_img.paste(img, (margin, margin))

    draw = ImageDraw.Draw(padded_img)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = None
    x0 = int(margin + scale * (180 / 360 * base))  # H 轴原点，加上左边距
    y0 = int(margin + scale * (180 / 360 * base))  # dh 轴原点 (dh=0 时的位置)，加上上边距
    draw_axis(draw, padded_img.width, padded_img.height, x0, y0,
              (-180, 179), (-180, 180), "H", "dh", font)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    ## arg parser
    parser = argparse.ArgumentParser(exit_on_error=False)
    # parser.add_argument("-i", "--input", default="", type=str, help="输入图像文件, yuv444p格式")
    # parser.add_argument("-o", "--output", default="", type=str, help="输出图像文件")
    parser.add_argument("-y", "--yval", type=int, default=128, help="y value")
    parser.add_argument("-s", "--sval", type=int, default=128, help="y value")
    args, _ = parser.parse_known_args()

    gen_img_ycbcr2rgb_coor(args.yval)
    # gen_img_ybyh_coor()
    # gen_img_sbyh_coor()
    # gen_img_hbyh_coor()
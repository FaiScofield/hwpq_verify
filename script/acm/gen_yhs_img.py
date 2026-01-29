import os
import sys
import argparse
from matplotlib.pyplot import ylabel
import numpy as np
from PIL import Image, ImageDraw, ImageFont

g_r2y_mat_bt709 = np.array(
    [[0.2126, 0.7152, 0.0722], [-0.114572, -0.385428, 0.5], [0.5, -0.454153, -0.045847]], dtype=np.float32
)

g_y2r_mat_bt709 = np.array([[1.0, 0.0, 1.5748], [1.0, -0.187324, -0.468124], [1.0, 1.8556, 0.0]], dtype=np.float32)


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
    r[cond] = c[cond]
    g[cond] = x[cond]
    b[cond] = 0

    cond = (h >= 60) & (h < 120)
    r[cond] = x[cond]
    g[cond] = c[cond]
    b[cond] = 0

    cond = (h >= 120) & (h < 180)
    r[cond] = 0
    g[cond] = c[cond]
    b[cond] = x[cond]

    cond = (h >= 180) & (h < 240)
    r[cond] = 0
    g[cond] = x[cond]
    b[cond] = c[cond]

    cond = (h >= 240) & (h < 300)
    r[cond] = x[cond]
    g[cond] = 0
    b[cond] = c[cond]

    cond = (h >= 300) & (h < 360)
    r[cond] = c[cond]
    g[cond] = 0
    b[cond] = x[cond]

    r = ((r + m) * 255).astype(np.uint8)
    g = ((g + m) * 255).astype(np.uint8)
    b = ((b + m) * 255).astype(np.uint8)
    return r, g, b


# ---------- 画图通用工具 ----------
def draw_axis(img_draw, W, H, margin, x0, y0, x_range, y_range, xlabel, ylabel, font=None, x_center=None, y_center=None, title=None):
    # 辅助函数：判断数值是否为整数
    def is_integer(value):
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            return value.is_integer()
        return False

    # 辅助函数：格式化数字显示
    def format_number(value):
        if is_integer(value):
            return f"{int(value)}"
        else:
            return f"{value:.1f}"

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
    if len(x_range) == 2:
        nx = 9
        for i in range(nx):
            x_data = x_range[0] + i * (x_range[1] - x_range[0]) / (nx - 1)
            x_pix = int(i * (W - 1) / (nx - 1))
            img_draw.line([(x_pix + margin, y0 + margin - 3), (x_pix + margin, y0 + margin + 3)], fill=tick_color, width=1)
            if font:
                img_draw.text((x_pix + margin + 5, y0 + margin + 5), format_number(x_data), fill=tick_color, font=font)
    elif len(x_range) > 2:
        # 按 x_range 绘制刻度，x轴正负半轴的间隔应该分开计算
        # 使用 x_center 对齐到 x 轴的零点位置
        x_center = x_center if x_center is not None else 0  # 默认 x_center 为 0

        # 将刻度分为小于 x_center 和大于等于 x_center 两部分
        left_ticks = [val for val in x_range if val < x_center]
        right_ticks = [val for val in x_range if val >= x_center]

        # 计算正半轴和负半轴在像素空间的范围
        # 从原点(x0)到图像左侧和右侧的距离
        left_width = x0  # 原点到图像左侧的像素数
        right_width = W - x0  # 原点到图像右侧的像素数

        # 分别计算左右半轴的映射比例
        if right_ticks:
            max_right = max(right_ticks)
            if max_right > x_center:
                right_scale = right_width / (max_right - x_center)  # 每单位数据值对应的像素数
            else:
                right_scale = 0
        if left_ticks:
            min_left = min(left_ticks)
            if min_left < x_center:
                left_scale = left_width / (x_center - min_left)  # 每单位数据值对应的像素数
            else:
                left_scale = 0

        # 绘制右半轴刻度 (x >= x_center)
        for x_data in right_ticks:
            if x_data == x_center:
                # 对于x=x_center点，只绘制刻度线，不绘制文本标签（避免重复）
                x_offset = 0
            else:
                x_offset = int((x_data - x_center) * right_scale)
            x_pix = x0 + x_offset  # 正值向右（像素值增大）
            img_draw.line([(x_pix + margin, y0 + margin - 3), (x_pix + margin, y0 + margin + 3)], fill=tick_color, width=1)
            if font and x_data != x_center:  # 不为x_center时才绘制标签
                img_draw.text((x_pix + margin + 5, y0 + margin + 5), format_number(x_data), fill=tick_color, font=font)

        # 绘制左半轴刻度 (x < x_center)
        for x_data in left_ticks:
            x_offset = int((x_center - x_data) * left_scale)
            x_pix = x0 - x_offset  # 负值向左（像素值减小）
            img_draw.line([(x_pix + margin, y0 + margin - 3), (x_pix + margin, y0 + margin + 3)], fill=tick_color, width=1)
            if font:
                img_draw.text((x_pix + margin + 5, y0 + margin + 5), format_number(x_data), fill=tick_color, font=font)
    else:
        raise ValueError("x_range must be a tuple of two elements")

    if len(y_range) == 2:
        ny = 9
        for j in range(ny):
            y_data = y_range[0] + j * (y_range[1] - y_range[0]) / (ny - 1)
            y_pix = int((H - 1) - j * (H - 1) / (ny - 1))
            img_draw.line([(x0 + margin - 3, y_pix + margin), (x0 + margin + 3, y_pix + margin)], fill=tick_color, width=1)
            if font and y_data != 0:
                img_draw.text((x0 + margin + 5, y_pix + margin - 5), format_number(y_data), fill=tick_color, font=font)
    elif len(y_range) > 2:
        # 按 y_range 绘制刻度，y轴正负半轴的间隔应该分开计算
        # 使用 y_center 对齐到 y 轴的零点位置
        y_center = y_center if y_center is not None else 0  # 默认 y_center 为 0

        # 将刻度分为小于 y_center 和大于等于 y_center 两部分
        lower_ticks = [val for val in y_range if val < y_center]
        upper_ticks = [val for val in y_range if val >= y_center]

        # 计算正半轴和负半轴在像素空间的范围
        # 从原点(y0)到图像顶部和底部的距离
        upper_height = y0  # 原点到图像顶部的像素数
        lower_height = H - y0  # 原点到图像底部的像素数

        # 分别计算上下半轴的映射比例
        if upper_ticks:
            max_upper = max(upper_ticks)
            if max_upper > y_center:
                upper_scale = upper_height / (max_upper - y_center)  # 每单位数据值对应的像素数
            else:
                upper_scale = 0
        if lower_ticks:
            min_lower = min(lower_ticks)
            if min_lower < y_center:
                lower_scale = lower_height / (y_center - min_lower)  # 每单位数据值对应的像素数
            else:
                lower_scale = 0

        # 绘制上半轴刻度 (y >= y_center)
        for y_data in upper_ticks:
            if y_data == y_center:
                # 对于y=y_center点，只绘制刻度线，不绘制文本标签（避免与x轴0点重复）
                y_offset = 0
            else:
                y_offset = int((y_data - y_center) * upper_scale)
            y_pix = y0 - y_offset  # 正值向上（像素值减小）
            img_draw.line([(x0 + margin - 3, y_pix + margin), (x0 + margin + 3, y_pix + margin)], fill=tick_color, width=1)
            if font and y_data != y_center:  # 不为y_center时才绘制标签
                img_draw.text((x0 + margin + 5, y_pix + margin - 5), format_number(y_data), fill=tick_color, font=font)

        # 绘制下半轴刻度 (y < y_center)
        for y_data in lower_ticks:
            y_offset = int((y_center - y_data) * lower_scale)
            y_pix = y0 + y_offset  # 负值向下（像素值增大）
            img_draw.line([(x0 + margin - 3, y_pix + margin), (x0 + margin + 3, y_pix + margin)], fill=tick_color, width=1)
            if font:
                img_draw.text((x0 + margin + 5, y_pix + margin - 5), format_number(y_data), fill=tick_color, font=font)
    else:
        raise ValueError("y_range must be a tuple of two elements")

    # 标签
    if font:
        img_draw.text((W + margin + hm, y0 - 15 + margin), xlabel, fill=axis_color, font=font)
        img_draw.text((x0 + margin + 5, margin - hm - 5), ylabel, fill=axis_color, font=font)
        if title:
            # 获取文本的边界框以准确计算宽度，实现居中
            bbox = img_draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            center_x = x0 + margin - text_width // 2
            img_draw.text((center_x, margin//3), title, fill=axis_color, font=font)


# ---------- 四个生成函数 ----------
def gen_img_ycbcr2rgb_coor(y=128, scale=2.0, out_path=None):
    """
    横坐标 Cb∈[-128,127]，纵坐标 Cr∈[-128,127]，固定亮度 y
    """
    if out_path is None:
        out_path = f"colormap_ycbcr2rgb_y{y}.png"
    base = 256
    # 修复坐标轴方向问题：图像中 y 轴向下为正，但我们需要 y 轴（Cr）向上为正
    cb_grid, cr_grid = np.meshgrid(np.arange(-128, 128), np.arange(127, -129, -1), indexing='xy')
    y_grid = np.ones_like(cb_grid) * y
    r, g, b = ycbcr2rgb(y_grid, cb_grid, cr_grid)
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
    title = f"Color Map of YUV2RGB (y={y})"
    draw_axis(draw, img.width, img.height, margin, x0, y0, (-128, 128), (-128, 128), "Cb", "Cr", title=title, font=font)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_dybyh_coor(y=128, s=1.0, range=64, out_path=None):
    """
    横坐标 H∈[-180,179]，纵坐标 dy∈[-255,255]，固定饱和度 s
    实际 y = 128 + dy
    """
    if out_path is None:
        out_path = f"colormap_dybyh_y{y}_s{s}_range{range}.png"

    title = f"Color Map of DeltaY-by-H (y={y}, s={s}, ΔY=±{range})"
    if range > 0:
        h_grid, dy_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-1, -1), indexing='xy')
        y = np.clip(y + dy_grid, 0, 255) # 360x512
    else:
        range = 64
        h_grid, dy_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-1, -1), indexing='xy')
        y = np.ones_like(h_grid) * y
    s = np.ones_like(h_grid) * s * 181

    h_rad = np.radians(h_grid)
    cb = np.clip(s * np.cos(h_rad), -128, 127)
    cr = np.clip(s * np.sin(h_rad), -128, 127)
    r, g, b = ycbcr2rgb(y, cb, cr)
    rgb = np.stack([r, g, b], axis=-1)
    img = Image.fromarray(rgb, mode="RGB")

    scale = 128 / range
    new_hgt = int(scale * img.height)
    new_wid = 3 * new_hgt
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    # 添加边距的图像
    margin = 64
    padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
    padded_img.paste(img, (margin, margin))

    draw = ImageDraw.Draw(padded_img)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = None
    x0 = int(img.width / 2)  # 图像中心x坐标
    y0 = int(img.height / 2)  # 图像中心y坐标
    draw_axis(draw, img.width, img.height, margin, x0, y0, (-180, 180), (-range, range), "H", "ΔY", title=title, font=font)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_dsbyh_coor(y=128, s=0.5, range=0.5, out_path=None):
    """
    横坐标 H∈[-180,179]，纵坐标为 ds 值，范围[-range, range]，固定亮度 y
    s 对应为 s+ds，画出坐标轴
    """
    if out_path is None:
        out_path = f"colormap_dsbyh_y{y}_s{s}_range{range}.png"

    title = f"Color Map of DeltaS-by-H (y={y}, s={s}, ΔS=±{range})"
    if range > 0:
        h_grid, ds_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-0.01, -range/64), indexing='xy')
        s = np.clip(s + ds_grid, 0, 1) * 181
    else:
        range = 0.5
        h_grid, ds_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-0.01, -range/64), indexing='xy')
        s = np.ones_like(h_grid) * s * 181
    y = np.ones_like(h_grid) * y

    h_rad = np.radians(h_grid)
    cb = np.clip(s * np.cos(h_rad), -128, 127)
    cr = np.clip(s * np.sin(h_rad), -128, 127)
    r, g, b = ycbcr2rgb(y, cb, cr)
    rgb = np.stack([r, g, b], axis=-1)
    img = Image.fromarray(rgb, mode="RGB")

    scale = 2
    new_hgt = int(scale * img.height)
    new_wid = 3 * new_hgt
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    # 添加边距的图像
    margin = 64
    padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
    padded_img.paste(img, (margin, margin))

    draw = ImageDraw.Draw(padded_img)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = None
    x0 = int(img.width / 2)  # 图像中心x坐标
    y0 = int(img.height / 2)  # 图像中心y坐标
    draw_axis(draw, img.width, img.height, margin, x0, y0, (-180, 180), (-range, range), "H", "ΔS", title=title, font=font)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_dhbyh_coor(y=128, s=0.5, range=180, out_path=None):
    """
    横坐标 H 值，范围[-180, 179]，纵坐标为 dh 值，范围[-range, range]
    给定亮度 y 和饱和度 s，画出坐标轴
    """
    if out_path is None:
        out_path = f"colormap_dhbyh_y{y}_s{s}_range{range}.png"

    title = f"Color Map of DeltaH-by-H (y={y}, s={s}, ΔH=±{range})"
    if range > 0:
        h_grid, dh_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-1, -1), indexing='xy')
        h = h_grid + dh_grid
    else:
        range = 180
        h_grid, dh_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-1, -1), indexing='xy')
        h = h_grid
    y = np.ones_like(h_grid) * y
    s = np.ones_like(h_grid) * s * 181

    h_rad = np.radians(h)
    cb = np.clip(s * np.cos(h_rad), -128, 127)
    cr = np.clip(s * np.sin(h_rad), -128, 127)
    r, g, b = ycbcr2rgb(y, cb, cr)
    rgb = np.stack([r, g, b], axis=-1)
    img = Image.fromarray(rgb, mode="RGB")

    scale = 180 / range
    new_hgt = int(scale * img.height)
    new_wid = 3 * new_hgt
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    # 添加边距的图像
    margin = 64
    padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
    padded_img.paste(img, (margin, margin))

    draw = ImageDraw.Draw(padded_img)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = None
    x0 = int(img.width / 2)  # 图像中心x坐标
    y0 = int(img.height / 2)  # 图像中心y坐标
    draw_axis(draw, img.width, img.height, margin, x0, y0, (-180, 180), (-range, range), "H", "ΔH", title=title, font=font)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_rgbgainbyh_coor(y=128, s=0.5, scale=2.0, out_path=None, rgain=None, ggain=None, bgain=None):
    # 仅允许 rgain/ggain/bgain 中至多一个有效；若三者均为 None，则直接返回
    if rgain is None and ggain is None and bgain is None:
        return
    # 若同时指定了多个增益，也直接返回
    if sum(x is not None for x in (rgain, ggain, bgain)) > 1:
        return

    range_yaxis = 1.0
    if rgain is not None:
        out_path = f"colormap_rgbgainbyh_y{y}_s{s}_rgain{rgain}.png" if out_path is None else out_path
        range_yaxis = rgain
        ylabel = "rgain"
    elif ggain is not None:
        out_path = f"colormap_rgbgainbyh_y{y}_s{s}_ggain{ggain}.png" if out_path is None else out_path
        range_yaxis = ggain
        ylabel = "ggain"
    elif bgain is not None:
        out_path = f"colormap_rgbgainbyh_y{y}_s{s}_bgain{bgain}.png" if out_path is None else out_path
        range_yaxis = bgain
        ylabel = "bgain"
    else:
        raise ValueError("one of r/g/bgain must be specified!")

    range_str = f"{range_yaxis}"
    color_gain = None
    if range_yaxis == 0:
        range_yaxis = 1.0
        color_gain = 1.0

    gain_range = np.arange(range_yaxis, -1.0, -(range_yaxis+1)/128)
    h_grid, _ = np.meshgrid(np.arange(-180, 180), gain_range, indexing='xy')

    y = np.ones_like(h_grid) * y
    s = np.ones_like(h_grid) * s * 181
    h_rad = np.radians(h_grid)
    cb = np.clip(s * np.cos(h_rad), -128, 127)
    cr = np.clip(s * np.sin(h_rad), -128, 127)
    r, g, b = ycbcr2rgb(y, cb, cr)

    if color_gain is None:
        color_gain = np.maximum(gain_range + 1.0, 0)
        color_gain = np.repeat(color_gain[:, None], r.shape[1], axis=1)
    if rgain:
        r = np.clip(r * color_gain, 0, 255).astype(np.uint8)
    elif ggain:
        g = np.clip(g * color_gain, 0, 255).astype(np.uint8)
    elif bgain:
        b = np.clip(b * color_gain, 0, 255).astype(np.uint8)

    rgb = np.stack([r, g, b], axis=-1)
    img = Image.fromarray(rgb, mode="RGB")

    new_hgt = int(scale * img.height)
    new_wid = 3 * new_hgt
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    # 添加边距的图像
    margin = 64
    padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
    padded_img.paste(img, (margin, margin))

    draw = ImageDraw.Draw(padded_img)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = None
    x0 = int(img.width / 2)  # 图像中心x坐标
    y0 = int(img.height - img.height / (range_yaxis + 1))  # 图像中心y坐标

    x_rane = np.arange(-180, 180+45, 45)
    y_rane = np.arange(0, range_yaxis+1+0.5, 0.5)
    y_cent = 1.0
    title = f"Color Map of {ylabel} (y={y}, s={s}, {ylabel}=±{range_str})"
    draw_axis(draw, img.width, img.height, margin, x0, y0, x_rane, y_rane, "H", ylabel, title=title, font=font, y_center=y_cent)

    padded_img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    ## arg parser
    parser = argparse.ArgumentParser(exit_on_error=False)
    # parser.add_argument("-i", "--input", default="", type=str, help="输入图像文件, yuv444p格式")
    # parser.add_argument("-o", "--output", default="", type=str, help="输出图像文件")
    parser.add_argument("-y", "--yval", type=int, help="y value, draw ycbcr2rgb")
    parser.add_argument("-s", "--sval", type=float, default=0.5, help="s value")
    parser.add_argument("-Y", "--dy", type=int, help="delta y range, draw dybyh")
    parser.add_argument("-S", "--ds", type=float, help="delta s range, draw dsbyh")
    parser.add_argument("-H", "--dh", type=int, help="delta h range, draw dhbyh")
    parser.add_argument("-r", "--rgain", type=float, help="red gain range, draw rgainbyh")
    parser.add_argument("-g", "--ggain", type=float, help="green gain range, draw ggainbyh")
    parser.add_argument("-b", "--bgain", type=float, help="blue gain range, draw bgainbyh")
    args, _ = parser.parse_known_args()

    if args.yval is not None and args.yval >= 0:
        gen_img_ycbcr2rgb_coor(y=args.yval)

    yval = args.yval if args.yval is not None else 128
    if args.dy is not None and args.dy >= 0:
        gen_img_dybyh_coor(y=yval, s=args.sval, range=args.dy)
    if args.ds is not None and args.ds >= 0:
        gen_img_dsbyh_coor(y=yval, s=args.sval, range=args.ds)
    if args.dh is not None and args.dh >= 0:
        gen_img_dhbyh_coor(y=yval, s=args.sval, range=args.dh)

    if args.rgain is not None and args.rgain >= 0:
        gen_img_rgbgainbyh_coor(y=yval, s=args.sval, rgain=args.rgain)
    if args.ggain is not None and args.ggain >= 0:
        gen_img_rgbgainbyh_coor(y=yval, s=args.sval, ggain=args.ggain)
    if args.bgain is not None and args.bgain >= 0:
        gen_img_rgbgainbyh_coor(y=yval, s=args.sval, bgain=args.bgain)

    # gen_img_sbyh_coor()
    # gen_img_hbyh_coor()

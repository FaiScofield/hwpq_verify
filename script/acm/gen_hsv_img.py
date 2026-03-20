import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

g_r2y_mat_bt709 = np.array(
    [[0.2126, 0.7152, 0.0722], [-0.114572, -0.385428, 0.5], [0.5, -0.454153, -0.045847]], dtype=np.float32
)

g_y2r_mat_bt709 = np.array([[1.0, 0.0, 1.5748], [1.0, -0.187324, -0.468124], [1.0, 1.8556, 0.0]], dtype=np.float32)

def rgb2hsv(r, g, b):
    """
    将 RGB 转换到 HSV，输入为 0~255 的 uint8 或浮点，返回 (h, s, v)
    h: 0~360, s: 0~1, v: 0~1
    """
    r = np.asarray(r, dtype=np.float32) / 255.0
    g = np.asarray(g, dtype=np.float32) / 255.0
    b = np.asarray(b, dtype=np.float32) / 255.0

    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    delta = maxc - minc

    # 计算色相 H
    h = np.zeros_like(maxc)
    cond = delta != 0
    rc = (maxc - r) / delta
    gc = (maxc - g) / delta
    bc = (maxc - b) / delta

    h = np.where(cond,
                 np.where(maxc == r, (bc - gc),
                          np.where(maxc == g, 2.0 + rc - bc,
                                   4.0 + gc - rc)),
                 h)
    h = (h / 6.0) % 1.0
    h = h * 360.0

    # 计算饱和度 S
    s = np.where(maxc != 0, delta / maxc, 0.0)

    # 计算明度 V
    v = maxc

    return h, s, v

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
def draw_axis_coor(img_draw, W, H, margin, x0, y0, x_range, y_range, xlabel, ylabel, font=None, x_center=None, y_center=None, title=None):
    # 辅助函数：判断数值是否为整数
    def is_integer(value):
        if int(value) - value == 0:
            return True
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
                img_draw.text((x0 + margin - 25, y_pix + margin - 5), format_number(y_data), fill=tick_color, font=font)
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
                img_draw.text((x0 + margin - 25, y_pix + margin - 5), format_number(y_data), fill=tick_color, font=font)

        # 绘制下半轴刻度 (y < y_center)
        for y_data in lower_ticks:
            y_offset = int((y_center - y_data) * lower_scale)
            y_pix = y0 + y_offset  # 负值向下（像素值增大）
            img_draw.line([(x0 + margin - 3, y_pix + margin), (x0 + margin + 3, y_pix + margin)], fill=tick_color, width=1)
            if font:
                img_draw.text((x0 + margin - 25, y_pix + margin - 5), format_number(y_data), fill=tick_color, font=font)
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
            center_x = W//2 + margin - text_width // 2
            img_draw.text((center_x, margin//3), title, fill=axis_color, font=font)


def gen_img_hsv2rgb_coor(vval=128, draw_axis=True, out_path=None):
    vval = np.clip(vval, 0, 255)
    if out_path is None:
        out_path = f"colormap_hsv2rgb_v{vval}.png"

    # 修复坐标轴方向问题：图像中 y 轴向下为正，但我们需要 y 轴（Cr）向上为正
    radius = 256
    x_grid, y_grid = np.meshgrid(np.arange(-radius, radius+1), np.arange(radius, -radius-1, -1), indexing='xy')
    x_grid = x_grid.astype(np.float32) / radius
    y_grid = y_grid.astype(np.float32) / radius
    h = np.arctan2(y_grid, x_grid) * 180 / np.pi + 360 # to positive angle
    s = np.sqrt(x_grid**2 + y_grid**2)
    v = np.ones_like(x_grid) * vval / 255

    r, g, b = hsv2rgb(h, s, v)
    r[s > 1] = 255
    g[s > 1] = 255
    b[s > 1] = 255
    rgb = np.stack([r, g, b], axis=-1)  # (H,W,3)

    img = Image.fromarray(rgb, mode="RGB")
    if draw_axis:
        margin = 64 # 添加边距的图像
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
        title = f"Color Map of HSV2RGB (v={vval})"
        draw_axis_coor(draw, img.width, img.height, margin, x0, y0, (-1, 1), (-1, 1), "S", "S", title=title, font=font)
        img = padded_img

    img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_dvbyh_coor(vval=128, sval=1.0, range=64, draw_axis=True, out_path=None):
    vval = np.clip(vval, 0, 255)
    sval = np.clip(sval, 0, 1.0)
    range = np.clip(range, 0, 255)
    if out_path is None:
        out_path = f"colormap_dvbyh_v{vval}_s{sval}_range{range}.png"

    title = f"Color Map of DeltaV-by-H (v={vval}, s={sval}, ΔV=±{range})"
    if range > 0:
        h_grid, dv_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-1, -1), indexing='xy')
        v = np.clip(vval + dv_grid, 0, 255) / 255 # 360x512
    else:
        range = 64
        h_grid, dv_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-1, -1), indexing='xy')
        v = np.ones_like(h_grid) * vval / 255
    h = h_grid + 360 # make sure h is positive
    s = np.ones_like(h_grid) * sval

    r, g, b = hsv2rgb(h, s, v)
    rgb = np.stack([r, g, b], axis=-1)

    img = Image.fromarray(rgb, mode="RGB")
    new_hgt = 256 # ~ 256
    new_wid = 2 * img.width # ~ 720
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    if draw_axis:
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
        step = (range + 2) // 4
        y_rane = np.arange(-range, range + step // 2, step)
        y_rane = np.clip(y_rane, -range, range)
        draw_axis_coor(draw, img.width, img.height, margin, x0, y0, (-180, 180), y_rane, "H", "ΔV", title=title, font=font)
        img = padded_img

    img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_dsbyh_coor(vval=128, sval=0.5, range=0.5, draw_axis=True, out_path=None):
    vval = np.clip(vval, 0, 255)
    sval = np.clip(sval, 0, 1.0)
    range = np.clip(range, 0, 1.0)
    if out_path is None:
        out_path = f"colormap_dsbyh_v{vval}_s{sval}_range{range}.png"

    title = f"Color Map of DeltaS-by-H (v={vval}, s={sval}, ΔS=±{range})"
    if range > 0:
        h_grid, ds_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-0.01, -range/64), indexing='xy')
        s = np.clip(sval + ds_grid, 0, 1)
    else:
        range = 0.5
        h_grid, ds_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-0.01, -range/64), indexing='xy')
        s = np.ones_like(h_grid) * sval
    h = h_grid + 360 # make sure h is positive
    v = np.ones_like(h_grid) * vval / 255

    r, g, b = hsv2rgb(h, s, v)
    rgb = np.stack([r, g, b], axis=-1)

    img = Image.fromarray(rgb, mode="RGB")
    new_hgt = 256 # ~ 256
    new_wid = 2 * img.width # ~ 720
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    if draw_axis:
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
        draw_axis_coor(draw, img.width, img.height, margin, x0, y0, (-180, 180), (-range, range), "H", "ΔS", title=title, font=font)
        img = padded_img

    img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_dhbyh_coor(vval=128, sval=0.5, range=180, draw_axis=True, out_path=None):
    vval = np.clip(vval, 0, 255)
    sval = np.clip(sval, 0, 1.0)
    range = np.clip(range, 0, 360)
    if out_path is None:
        out_path = f"colormap_dhbyh_v{vval}_s{sval}_range{range}.png"

    title = f"Color Map of DeltaH-by-H (v={vval}, s={sval}, ΔH=±{range})"
    if range > 0:
        h_grid, dh_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-1, -1), indexing='xy')
        h = h_grid + dh_grid + 360
    else:
        range = 180
        h_grid, dh_grid = np.meshgrid(np.arange(-180, 180), np.arange(range, -range-1, -1), indexing='xy')
        h = h_grid + 360
    v = np.ones_like(h_grid) * vval / 255
    s = np.ones_like(h_grid) * sval
    r, g, b = hsv2rgb(h, s, v)
    rgb = np.stack([r, g, b], axis=-1)

    img = Image.fromarray(rgb, mode="RGB")
    new_hgt = 256 # ~ 256
    new_wid = 2 * img.width # ~ 720
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    if draw_axis:
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
        draw_axis_coor(draw, img.width, img.height, margin, x0, y0, (-180, 180), (-range, range), "H", "ΔH", title=title, font=font)
        img = padded_img

    img.save(out_path)
    print(f"Saved: {out_path}")


def gen_img_rgbgainbyh_coor(vval=128, sval=0.5, rgain=None, ggain=None, bgain=None, draw_axis=True, out_path=None):
    vval = np.clip(vval, 0, 255)
    # 仅允许 rgain/ggain/bgain 中至多一个有效；若三者均为 None，则直接返回
    if rgain is None and ggain is None and bgain is None:
        return
    # 若同时指定了多个增益，也直接返回
    if sum(x is not None for x in (rgain, ggain, bgain)) > 1:
        return

    if rgain is not None:
        out_path = f"colormap_rgbgainbyh_v{vval}_s{sval}_rgain{rgain}.png" if out_path is None else out_path
        ylabel = "rgain"
        range = rgain
    elif ggain is not None:
        out_path = f"colormap_rgbgainbyh_v{vval}_s{sval}_ggain{ggain}.png" if out_path is None else out_path
        ylabel = "ggain"
        range = ggain
    elif bgain is not None:
        out_path = f"colormap_rgbgainbyh_v{vval}_s{sval}_bgain{bgain}.png" if out_path is None else out_path
        ylabel = "bgain"
        range = bgain
    else:
        raise ValueError("one of r/g/bgain must be specified!")

    zero_gain = False
    if range == 0:
        range = 1.0
        zero_gain = True

    max_gain = 1 + range
    min_gain = max(1 - range, 0)
    h_grid, gain_grid = np.meshgrid(np.arange(-180, 180), np.arange(max_gain, min_gain-0.01, -range/64), indexing='xy')
    h = h_grid + 360
    s = np.ones_like(h_grid) * sval
    v = np.ones_like(h_grid) * vval / 255
    r, g, b = hsv2rgb(h, s, v)

    gain_grid = 1 if zero_gain else gain_grid
    if rgain is not None:
        r = np.clip(r * gain_grid, 0, 255).astype(np.uint8)
    elif ggain is not None:
        g = np.clip(g * gain_grid, 0, 255).astype(np.uint8)
    elif bgain is not None:
        b = np.clip(b * gain_grid, 0, 255).astype(np.uint8)
    rgb = np.stack([r, g, b], axis=-1)

    img = Image.fromarray(rgb, mode="RGB")
    new_hgt = 256 # ~ 256
    new_wid = 2 * img.width # ~ 720
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    if draw_axis:
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
        y0 = int(img.height * range / (range + 1 - min_gain))  # 图像中心y坐标

        x_rane = np.arange(-180, 180+45, 45)
        y_rane = np.arange(min_gain, max_gain+0.5, 0.5)
        if zero_gain:
            title = f"Color Map of {ylabel}-by-H (v={vval}, s={sval}, {ylabel}=OFF)"
        else:
            title = f"Color Map of {ylabel}-by-H (v={vval}, s={sval}, {ylabel}=[{min_gain}, {max_gain}])"
        draw_axis_coor(draw, img.width, img.height, margin, x0, y0, x_rane, y_rane, "H", ylabel, title=title, font=font, y_center=1)
        img = padded_img

    img.save(out_path)
    print(f"Saved: {out_path}")

def gen_img_rgbgain2w_coor(rgain=None, ggain=None, bgain=None, draw_axis=True, out_path=None):
    # 仅允许 rgain/ggain/bgain 中至多一个有效；若三者均为 None，则直接返回
    if rgain is None and ggain is None and bgain is None:
        return
    # 若同时指定了多个增益，也直接返回
    if sum(x is not None for x in (rgain, ggain, bgain)) > 1:
        return

    if rgain is not None:
        out_path = f"colormap_rgbgain2w_rgain{rgain}.png" if out_path is None else out_path
        ylabel = "rgain"
        range = rgain
    elif ggain is not None:
        out_path = f"colormap_rgbgain2w_ggain{ggain}.png" if out_path is None else out_path
        ylabel = "ggain"
        range = ggain
    elif bgain is not None:
        out_path = f"colormap_rgbgain2w_bgain{bgain}.png" if out_path is None else out_path
        ylabel = "bgain"
        range = bgain
    else:
        raise ValueError("one of r/g/bgain must be specified!")

    zero_gain = False
    if range == 0:
        range = 1.0
        zero_gain = True

    max_gain = 1 + range
    min_gain = max(1 - range, 0)
    w_grid, gain_grid = np.meshgrid(np.arange(0, 256), np.arange(max_gain, min_gain-0.01, -range/64), indexing='xy')
    r = w_grid.astype(np.uint8)
    g = w_grid.astype(np.uint8)
    b = w_grid.astype(np.uint8)
    gain_grid = 1 if zero_gain else gain_grid
    if rgain is not None:
        r = np.clip(r * gain_grid, 0, 255).astype(np.uint8)
    elif ggain is not None:
        g = np.clip(g * gain_grid, 0, 255).astype(np.uint8)
    elif bgain is not None:
        b = np.clip(b * gain_grid, 0, 255).astype(np.uint8)
    rgb = np.stack([r, g, b], axis=-1)

    img = Image.fromarray(rgb, mode="RGB")
    new_hgt = 300 # ~ 300
    new_wid = 2 * img.width # ~ 512
    img = img.resize((new_wid, new_hgt), Image.BICUBIC)

    if draw_axis:
        # 添加边距的图像
        margin = 64
        padded_img = Image.new("RGB", (img.width + 2 * margin, img.height + 2 * margin), (255, 255, 255))
        padded_img.paste(img, (margin, margin))

        draw = ImageDraw.Draw(padded_img)
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = None
        x0 = 0
        y0 = int(img.height * range / (range + 1 - min_gain))

        x_rane = np.arange(0, 256 + 16, 32)
        y_rane = np.arange(min_gain, max_gain+0.5, 0.5)
        y_cent = 1
        if zero_gain:
            title = f"Color Map of {ylabel}-on-gray ({ylabel}=OFF)"
        else:
            title = f"Color Map of {ylabel}-on-gray ({ylabel}=[{min_gain}, {max_gain}])"
        draw_axis_coor(draw, img.width, img.height, margin, x0, y0, x_rane, y_rane, "Gray", ylabel, title=title, font=font, y_center=y_cent)
        img = padded_img

    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    ## arg parser
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("--rgb2hsv", nargs="+", type=int, help="input rgb value(r, g, b), do rgb2hsv")
    parser.add_argument("--hsv2rgb", nargs="+", type=float, help="input hsv value(h, s, v), do hsv2rgb")
    parser.add_argument("-v", "--vval", type=int, help="v value, range: [0, 255], draw hsv2rgb")
    parser.add_argument("-s", "--sval", type=float, default=0.5, help="s value, range: [0.0, 1.0]")
    parser.add_argument("-V", "--dv", type=int, help="delta v range, draw dvbyh, range: [0, 255]")
    parser.add_argument("-S", "--ds", type=float, help="delta s range, draw dsbyh, range: [0.0, 1.0]")
    parser.add_argument("-H", "--dh", type=int, help="delta h range, draw dhbyh, range: [0, 360]")
    parser.add_argument("-r", "--rgain", type=float, help="red gain range, draw rgainbyh")
    parser.add_argument("-g", "--ggain", type=float, help="green gain range, draw ggainbyh")
    parser.add_argument("-b", "--bgain", type=float, help="blue gain range, draw bgainbyh")
    parser.add_argument("--white", action="store_true", help="apply white color")
    parser.add_argument("--no_draw_axis", action="store_false", dest="draw_axis", help="draw axis")
    parser.set_defaults(draw_axis=True)
    args, _ = parser.parse_known_args()

    if args.rgb2hsv is not None and len(args.rgb2hsv) == 3:
        h, s, v = rgb2hsv(args.rgb2hsv[0], args.rgb2hsv[1], args.rgb2hsv[2])
        print(f"rgb2hsv: {args.rgb2hsv} -> {float(h), float(s), float(v)}")
        exit(0)

    if args.hsv2rgb is not None and len(args.hsv2rgb) == 3:
        r, g, b = hsv2rgb(args.hsv2rgb[0], args.hsv2rgb[1], args.hsv2rgb[2])
        print(f"hsv2rgb: {args.hsv2rgb} -> {r, g, b}")
        exit(0)

    if args.vval is not None and args.vval >= 0:
        gen_img_hsv2rgb_coor(vval=args.vval)

    vval = args.vval if args.vval is not None else 128
    if args.dv is not None and args.dv >= 0:
        gen_img_dvbyh_coor(vval=vval, sval=args.sval, range=args.dv, draw_axis=args.draw_axis)
    if args.ds is not None and args.ds >= 0:
        gen_img_dsbyh_coor(vval=vval, sval=args.sval, range=args.ds, draw_axis=args.draw_axis)
    if args.dh is not None and args.dh >= 0:
        gen_img_dhbyh_coor(vval=vval, sval=args.sval, range=args.dh, draw_axis=args.draw_axis)

    if args.white:
        gen_img_rgbgain2w_coor(rgain=args.rgain, ggain=args.ggain, bgain=args.bgain, draw_axis=args.draw_axis)
    else:
        if args.rgain is not None and args.rgain >= 0:
            gen_img_rgbgainbyh_coor(vval=vval, sval=args.sval, rgain=args.rgain, draw_axis=args.draw_axis)
        if args.ggain is not None and args.ggain >= 0:
            gen_img_rgbgainbyh_coor(vval=vval, sval=args.sval, ggain=args.ggain, draw_axis=args.draw_axis)
        if args.bgain is not None and args.bgain >= 0:
            gen_img_rgbgainbyh_coor(vval=vval, sval=args.sval, bgain=args.bgain, draw_axis=args.draw_axis)

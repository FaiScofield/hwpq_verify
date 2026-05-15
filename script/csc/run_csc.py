#!/usr/bin/env python3
"""
Copyright   : Copyright (c) 2025 by Rockchip. All right reserved.
FilePath    : run_csc.py
Author      : vance.wu@rock-chips.com
Date        : 2026-05-14
Description : CSC image conversion tool with optional UI
"""

import argparse
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from get_csc_coefs import (
    CscCoefConfig,
    CscBcshConfig,
    CscMode,
    get_csc_coefs,
    parse_csc_mode_str,
    ColorSpace,
)
from get_csc_coef_hsv import apply_bcsh_hsv

FORMAT_NAMES = {
    0x0: "RGB888",
    0x1: "RGBA8888",
    0x2: "RGB_Planar",
    0x3: "YUV444P_YU24",
    0x4: "YUV444SP_NV24",
    0x5: "YUV444I_VU24",
    0x6: "YUV422P_YU16",
    0x7: "YUV422SP_NV16",
    0x8: "YUV420P_YU12",
    0x9: "YUV420SP_NV12",
    0xA: "YUV400_Gray",
    0x10: "RGB_10LSB",
    0x11: "RGBA_10LSB",
    0x12: "RGB_Planar_10LSB",
    0x13: "YUV444P_10LSB",
    0x14: "YUV444SP_10LSB",
    0x15: "YUV444I_10LSB",
    0x16: "YUV422P_10LSB",
    0x17: "YUV422SP_10LSB",
    0x18: "YUV420P_10LSB",
    0x19: "YUV420SP_10LSB",
    0x1A: "YUV400_10LSB",
    0x20: "RGB_10Packed",
    0x21: "RGBA_1010102",
    0x22: "RGB_Planar_10Packed",
    0x23: "YUV444P_10Packed",
    0x24: "YUV444SP_10Packed_NV30",
    0x25: "YUV444I_10Packed",
    0x26: "YUV422P_10Packed",
    0x27: "YUV422SP_10Packed_NV20",
    0x28: "YUV420P_10Packed",
    0x29: "YUV420SP_10Packed_NV15",
    0x2A: "YUV400_10Packed",
}

CLRSPC_NAMES = {
    0: "RGB_Limited",
    1: "RGB_Full",
    2: "BT601_Limited",
    3: "BT601_Full",
    4: "BT709_Limited",
    5: "BT709_Full",
    8: "BT2020_Limited",
    9: "BT2020_Full",
}

CLRSPC_TO_PARAMS = {
    0: ("rgb", "L"),
    1: ("rgb", "F"),
    2: ("bt601", "L"),
    3: ("bt601", "F"),
    4: ("bt709", "L"),
    5: ("bt709", "F"),
    8: ("bt2020", "L"),
    9: ("bt2020", "F"),
}

CLRSPC_OPTIONS = [0, 1, 2, 3, 4, 5, 8, 9]

FMT_OPTIONS_8BIT = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA]
FMT_OPTIONS_10BIT = [0x10, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A]


def clrspc_to_mode_params(clrspc):
    """Convert clrspc integer to (color_space_name, range_flag) tuple"""
    if clrspc not in CLRSPC_TO_PARAMS:
        raise ValueError(f"Unsupported colorspace: {clrspc}, supported: {list(CLRSPC_TO_PARAMS.keys())}")
    return CLRSPC_TO_PARAMS[clrspc]


def build_csc_mode_str(input_clrspc, output_clrspc):
    """Build a CSC mode string from input and output colorspace integers"""
    ics, irange = clrspc_to_mode_params(input_clrspc)
    ocs, orange = clrspc_to_mode_params(output_clrspc)
    mode_str = f"{ics}{irange.lower()}_to_{ocs}{orange.lower()}"
    return mode_str


def is_yuv_format(fmt):
    """Check if format code represents a YUV format"""
    base = fmt & 0xF
    return base >= 0x3


def is_rgb_format(fmt):
    """Check if format code represents an RGB format"""
    base = fmt & 0xF
    return base <= 0x2


def get_pixel_depth(fmt):
    """Get pixel bit depth from format code"""
    modifier = fmt & 0xF0
    if modifier >= 0x10:
        return 10
    return 8


def get_bytes_per_element(fmt):
    """Get bytes per pixel element from format code"""
    modifier = fmt & 0xF0
    if modifier >= 0x10:
        return 2
    return 1


def _resample_horizontal(channel, target_w):
    """Resample a channel to target width by duplicating each column"""
    h, w = channel.shape
    if w == target_w:
        return channel
    ratio = target_w // w
    return np.repeat(channel, ratio, axis=1)


def _resample_hv(channel, target_h, target_w):
    """Resample a channel to target height and width by duplicating"""
    h, w = channel.shape
    if h == target_h and w == target_w:
        return channel
    h_ratio = target_h // h
    w_ratio = target_w // w
    result = np.repeat(channel, h_ratio, axis=0)
    result = np.repeat(result, w_ratio, axis=1)
    return result


def get_frame_size(width, height, fmt):
    """Calculate the expected frame size in bytes based on resolution and format"""
    base = fmt & 0xF
    bpe = get_bytes_per_element(fmt)

    # Base number of elements (pixels)
    if base == 0x0 or base == 0x2 or base == 0x3 or base == 0x5: # RGB888, RGB_Planar, YUV444P, YUV444I
        elements = width * height * 3
    elif base == 0x1: # RGBA8888
        elements = width * height * 4
    elif base == 0x4: # YUV444SP
        elements = width * height * 3
    elif base == 0x6 or base == 0x7: # YUV422P, YUV422SP
        elements = width * height * 2
    elif base == 0x8 or base == 0x9: # YUV420P, YUV420SP
        elements = width * height * 3 // 2
    elif base == 0xA: # YUV400_Gray
        elements = width * height
    else:
        elements = width * height * 3

    return elements * bpe


def read_raw_to_planar(filepath, width, height, fmt):
    """Read raw image file and return planar numpy array (3, H, W)"""
    base = fmt & 0xF
    bpe = get_bytes_per_element(fmt)
    dtype = np.uint16 if bpe == 2 else np.uint8
    depth = get_pixel_depth(fmt)

    raw = np.fromfile(filepath, dtype=dtype)
    planar = np.zeros((3, height, width), dtype=dtype)
    max_val = (1 << depth) - 1

    if base == 0x0:
        rgb = raw[: height * width * 3].reshape(height, width, 3)
        planar[0] = rgb[:, :, 0]
        planar[1] = rgb[:, :, 1]
        planar[2] = rgb[:, :, 2]
    elif base == 0x1:
        rgba = raw[: height * width * 4].reshape(height, width, 4)
        planar[0] = rgba[:, :, 0]
        planar[1] = rgba[:, :, 1]
        planar[2] = rgba[:, :, 2]
    elif base == 0x2:
        planar = raw[: 3 * height * width].reshape(3, height, width)
    elif base == 0x3:
        planar = raw[: 3 * height * width].reshape(3, height, width)
    elif base == 0x4:
        y_size = height * width
        y = raw[:y_size].reshape(height, width)
        uv = raw[y_size : y_size + y_size * 2].reshape(height, width, 2)
        planar[0] = y
        planar[1] = uv[:, :, 0]
        planar[2] = uv[:, :, 1]
    elif base == 0x5:
        vuy = raw[: height * width * 3].reshape(height, width, 3)
        planar[0] = vuy[:, :, 2]
        planar[1] = vuy[:, :, 1]
        planar[2] = vuy[:, :, 0]
    elif base == 0x6:
        y_size = height * width
        uv_size = height * (width // 2)
        y = raw[:y_size].reshape(height, width)
        u = raw[y_size : y_size + uv_size].reshape(height, width // 2)
        v = raw[y_size + uv_size : y_size + 2 * uv_size].reshape(height, width // 2)
        planar[0] = y
        planar[1] = _resample_horizontal(u, width)
        planar[2] = _resample_horizontal(v, width)
    elif base == 0x7:
        y_size = height * width
        y = raw[:y_size].reshape(height, width)
        uv = raw[y_size : y_size + y_size].reshape(height, width // 2, 2)
        planar[0] = y
        planar[1] = _resample_horizontal(uv[:, :, 0], width)
        planar[2] = _resample_horizontal(uv[:, :, 1], width)
    elif base == 0x8:
        y_size = height * width
        uv_size = (height // 2) * (width // 2)
        y = raw[:y_size].reshape(height, width)
        u = raw[y_size : y_size + uv_size].reshape(height // 2, width // 2)
        v = raw[y_size + uv_size : y_size + 2 * uv_size].reshape(height // 2, width // 2)
        planar[0] = y
        planar[1] = _resample_hv(u, height, width)
        planar[2] = _resample_hv(v, height, width)
    elif base == 0x9:
        y_size = height * width
        y = raw[:y_size].reshape(height, width)
        uv = raw[y_size : y_size + (height // 2) * width].reshape(height // 2, width // 2, 2)
        planar[0] = y
        planar[1] = _resample_hv(uv[:, :, 0], height, width)
        planar[2] = _resample_hv(uv[:, :, 1], height, width)
    elif base == 0xA:
        y = raw[: height * width].reshape(height, width)
        planar[0] = y
        planar[1] = max_val if is_yuv_format(fmt) else 0
        planar[2] = planar[1].copy()
    else:
        raise ValueError(f"Unsupported base format: 0x{base:X}")

    if bpe == 2:
        planar = planar.astype(np.uint16)

    return planar


def write_planar_to_raw(planar, filepath, width, height, fmt):
    """Write planar numpy array (3, H, W) to raw file in specified format"""
    base = fmt & 0xF
    bpe = get_bytes_per_element(fmt)
    dtype = planar.dtype

    if base == 0x0:
        out = np.stack([planar[0], planar[1], planar[2]], axis=-1).ravel()
    elif base == 0x1:
        alpha = np.full((height, width), 255, dtype=dtype)
        out = np.stack([planar[0], planar[1], planar[2], alpha], axis=-1).ravel()
    elif base == 0x2:
        out = planar.ravel()
    elif base == 0x3:
        out = planar.ravel()
    elif base == 0x4:
        uv = np.stack([planar[1], planar[2]], axis=-1).ravel()
        out = np.concatenate([planar[0].ravel(), uv])
    elif base == 0x5:
        vuy = np.stack([planar[2], planar[1], planar[0]], axis=-1).ravel()
        out = vuy
    elif base == 0x6:
        y_out = planar[0].ravel()
        u_out = planar[1][:, 0::2].ravel()
        v_out = planar[2][:, 0::2].ravel()
        out = np.concatenate([y_out, u_out, v_out])
    elif base == 0x7:
        y_out = planar[0].ravel()
        uv_ch = np.stack([planar[1][:, 0::2], planar[2][:, 0::2]], axis=-1).ravel()
        out = np.concatenate([y_out, uv_ch])
    elif base == 0x8:
        y_out = planar[0].ravel()
        u_out = planar[1][0::2, 0::2].ravel()
        v_out = planar[2][0::2, 0::2].ravel()
        out = np.concatenate([y_out, u_out, v_out])
    elif base == 0x9:
        y_out = planar[0].ravel()
        uv_ch = np.stack([planar[1][0::2, 0::2], planar[2][0::2, 0::2]], axis=-1).ravel()
        out = np.concatenate([y_out, uv_ch])
    elif base == 0xA:
        out = planar[0].ravel()
    else:
        raise ValueError(f"Unsupported base format: 0x{base:X}")

    out.tofile(filepath)


def apply_csc(planar_in, csc_coefs, csc_offset, coef_precision, pixel_depth):
    """Apply CSC transformation to planar image, return output planar (3, H, W)"""
    h, w = planar_in.shape[1], planar_in.shape[2]
    pixels = planar_in.reshape(3, -1).astype(np.float64)
    out = csc_coefs.astype(np.float64) @ pixels + csc_offset.reshape(3, 1).astype(np.float64)

    if coef_precision > 0:
        rnd = 1 << (coef_precision - 1)
        out = (out.astype(np.int64) + rnd) >> coef_precision

    max_val = (1 << pixel_depth) - 1
    out = np.clip(out, 0, max_val).astype(planar_in.dtype)
    return out.reshape(3, h, w)


def _get_default_output_path(input_path):
    """Generate default output path: dirname(input)/custom_output_basename"""
    dirname = os.path.dirname(input_path)
    basename = os.path.splitext(os.path.basename(input_path))[0]
    if not dirname:
        dirname = "."
    return os.path.join(dirname, f"{basename}_csc_output.raw")


def run_cli(args):
    """Run CSC conversion in command-line mode"""
    if not args.input:
        print("Error: input file (-i/--input) is required in CLI mode")
        sys.exit(-1)

    input_file = args.input
    width = args.width
    height = args.height
    input_fmt = args.format
    input_clrspc = args.clrspc
    output_fmt = args.outfmt
    output_clrspc = args.outclr
    coef_precision = args.precision
    pixel_depth = args.depth

    if output_fmt is None:
        output_fmt = (input_fmt & 0xF) + 0x10
    if output_clrspc is None:
        output_clrspc = input_clrspc

    output_file = args.output
    if output_file is None:
        output_file = _get_default_output_path(input_file)

    if not os.path.isfile(input_file):
        print(f"Error: input file not found: {input_file}")
        sys.exit(-1)

    print(f"Input:  {input_file} ({FORMAT_NAMES.get(input_fmt, f'0x{input_fmt:X}')}, "
          f"{CLRSPC_NAMES.get(input_clrspc, str(input_clrspc))}, {width}x{height})")
    print(f"Output: {output_file} ({FORMAT_NAMES.get(output_fmt, f'0x{output_fmt:X}')}, "
          f"{CLRSPC_NAMES.get(output_clrspc, str(output_clrspc))}, {args.outwid}x{args.outhgt})")
    print(f"CSC config: precision={coef_precision}, depth={pixel_depth}")

    mode_str = build_csc_mode_str(input_clrspc, output_clrspc)
    print(f"CSC mode: {mode_str}")

    planar_in = read_raw_to_planar(input_file, width, height, input_fmt)

    csc_config = CscCoefConfig()
    csc_config.pixel_depth = pixel_depth
    csc_config.coef_precision = coef_precision
    csc_config.algo_type = args.algo_type
    csc_config.csc_mode = parse_csc_mode_str(mode_str)

    bcsh = CscBcshConfig()
    if args.hue is not None:
        bcsh.hue = args.hue
    if args.saturation is not None:
        bcsh.saturation = args.saturation
    if args.contrast is not None:
        bcsh.contrast = args.contrast
    if args.brightness is not None:
        bcsh.brightness = args.brightness
    if args.r_gain is not None:
        bcsh.r_gain = args.r_gain
    if args.g_gain is not None:
        bcsh.g_gain = args.g_gain
    if args.b_gain is not None:
        bcsh.b_gain = args.b_gain
    if args.r_offset is not None:
        bcsh.r_offset = args.r_offset
    if args.g_offset is not None:
        bcsh.g_offset = args.g_offset
    if args.b_offset is not None:
        bcsh.b_offset = args.b_offset

    if args.algo_type == 'RGB_on_HSV':
        output_is_rgb = is_rgb_format(output_fmt)
        input_is_rgb = is_rgb_format(input_fmt)
        if output_is_rgb:
            coefs, offset = get_csc_coefs(csc_config, None)
            planar_out = apply_csc(planar_in, coefs, offset, coef_precision, pixel_depth)
            planar_out = apply_bcsh_hsv(planar_out, bcsh, pixel_depth)
        elif input_is_rgb:
            planar_in = apply_bcsh_hsv(planar_in, bcsh, pixel_depth)
            coefs, offset = get_csc_coefs(csc_config, None)
            planar_out = apply_csc(planar_in, coefs, offset, coef_precision, pixel_depth)
        else:
            coefs, offset = get_csc_coefs(csc_config, bcsh)
            planar_out = apply_csc(planar_in, coefs, offset, coef_precision, pixel_depth)
    else:
        coefs, offset = get_csc_coefs(csc_config, bcsh)
        planar_out = apply_csc(planar_in, coefs, offset, coef_precision, pixel_depth)

    print(f"CSC matrix:\n{coefs}")
    print(f"CSC offset: {offset}")

    out_width = args.outwid if args.outwid is not None else width
    out_height = args.outhgt if args.outhgt is not None else height
    if out_width != width or out_height != height:
        if out_width == width:
            planar_out_resized = planar_out.copy()
        else:
            planar_out_resized = np.zeros((3, out_height, out_width), dtype=planar_out.dtype)
            for c in range(3):
                h_ratio = out_height / height
                w_ratio = out_width / width
                y_src = (np.arange(out_height) / h_ratio).astype(np.int32)
                x_src = (np.arange(out_width) / w_ratio).astype(np.int32)
                y_src = np.clip(y_src, 0, height - 1)
                x_src = np.clip(x_src, 0, width - 1)
                planar_out_resized[c] = planar_out[c][y_src[:, None], x_src[None, :]]
    else:
        planar_out_resized = planar_out

    write_planar_to_raw(planar_out_resized, output_file, out_width, out_height, output_fmt)
    print(f"Conversion done, output written to: {output_file}")


def open_csc_ui(args):
    """Open PySimpleGUI UI for interactive CSC conversion"""
    import io
    import PySimpleGUI as sg
    from PIL import Image

    sg.theme('SystemDefault')

    fmt_options = FMT_OPTIONS_8BIT + FMT_OPTIONS_10BIT
    fmt_display = [f"0x{f:X} - {FORMAT_NAMES.get(f, 'Unknown')}" for f in fmt_options]
    clrspc_display = [f"{c} - {CLRSPC_NAMES[c]}" for c in CLRSPC_OPTIONS]
    precision_values = [0] + list(range(8, 17))

    def get_fmt_from_display(display_str):
        return int(display_str.split(" ")[0], 16)

    def get_clrspc_from_display(display_str):
        return int(display_str.split(" ")[0])

    bcsh_names = [
        ('Brightness:', 'bright', 'Contrast:', 'contrast'),
        ('Saturation:', 'sat', 'Hue:', 'hue'),
        ('R Gain:', 'r_gain', 'R Offset:', 'r_offset'),
        ('G Gain:', 'g_gain', 'G Offset:', 'g_offset'),
        ('B Gain:', 'b_gain', 'B Offset:', 'b_offset'),
    ]

    bcsh_layout = []
    for n1, k1, n2, k2 in bcsh_names:
        bcsh_layout.append([
            sg.Text(n1, size=(10, 1)),
            sg.Slider(range=(0, 511), default_value=256, orientation='h',
                      size=(20, 15), key=f'-BCSH-{k1}-', enable_events=True, disable_number_display=True),
            sg.Text('256', key=f'-BCSH-{k1}-VAL-', size=(4, 1)),
            sg.Text(n2, size=(10, 1)),
            sg.Slider(range=(0, 511), default_value=256, orientation='h',
                      size=(20, 15), key=f'-BCSH-{k2}-', enable_events=True, disable_number_display=True),
            sg.Text('256', key=f'-BCSH-{k2}-VAL-', size=(4, 1)),
        ])

    algo_type_options = ['RK CSC', 'RK CSC (fix contrast)', 'RGB_on_HSV']
    bcsh_tab_layout = [
        *bcsh_layout,
        [sg.Text('AlgoType:', size=(8, 1)),
         sg.Combo(algo_type_options, default_value='RK CSC', key='-BCSH-ALGO-TYPE-',
                  readonly=True, size=(22, 1), enable_events=True),
         sg.Push(),
         sg.Button('Reset BCSH', key='-RESET-BCSH-')]
    ]

    input_output_layout = [
        [sg.Text('Input File:', size=(12, 1)),
         sg.Input(key='-INPUT-FILE-', size=(52, 1), enable_events=True, readonly=True),
         sg.FileBrowse('Browse...')],
        [sg.Text('Width:', size=(6, 1)), sg.Input('1920', key='-WIDTH-', size=(8, 1), enable_events=True),
         sg.Text('Height:', size=(6, 1)), sg.Input('1080', key='-HEIGHT-', size=(8, 1), enable_events=True)],
        [sg.Text('Input Format:', size=(12, 1)),
         sg.Combo(fmt_display, default_value=fmt_display[0], key='-IN-FMT-',
                  readonly=True, size=(28, 1), enable_events=True),
         sg.Text('Input Colorspace:', size=(14, 1)),
         sg.Combo(clrspc_display, default_value=clrspc_display[1], key='-IN-CLR-',
                  readonly=True, size=(22, 1), enable_events=True)],
        [sg.Text('Output Format:', size=(12, 1)),
         sg.Combo(fmt_display, default_value=fmt_display[0], key='-OUT-FMT-',
                  readonly=True, size=(28, 1), enable_events=True),
         sg.Text('Output Colorspace:', size=(14, 1)),
         sg.Combo(clrspc_display, default_value=clrspc_display[1], key='-OUT-CLR-',
                  readonly=True, size=(22, 1), enable_events=True)],
        [sg.Text('Precision (0=float):', size=(16, 1)),
         sg.Combo([str(v) for v in precision_values], default_value='10',
                  key='-PRECISION-', readonly=True, size=(6, 1), enable_events=True),
         sg.Text('Auto Pixel Depth:', size=(14, 1)),
         sg.Text('8', key='-DISP-DEPTH-', size=(4, 1), font=('_', 10, 'bold'))]
    ]

    layout = [
        [sg.Column([
            [sg.TabGroup([
                [sg.Tab('I/O Config', input_output_layout),
                 sg.Tab('BCSH Configuration', bcsh_tab_layout)]
            ])]
        ]),
         sg.Column([
             [sg.Button('Save Output', key='-SAVE-OUT-', size=(12, 2))],
             [sg.Radio('Show Input', 'RADIO1', key='-SHOW-IN-', enable_events=True, size=(12, 1))],
             [sg.Radio('Show Output', 'RADIO1', default=True, key='-SHOW-OUT-', enable_events=True, size=(12, 1))]
         ], element_justification='l', vertical_alignment='top', pad=(10, 30))],
        [sg.HorizontalSeparator()],
        [sg.Input('Display Size: ...\tCoefs: ...\tOffset: ...', key='-PREVIEW-LABEL-', expand_x=True, font=('Consolas', 10), readonly=True, border_width=0, disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color())],
        [sg.Input('Position: ... Input Pixel: ... Output Pixel: ... [Press Space to freeze]', key='-PIXEL-INFO-', expand_x=True, font=('Consolas', 10), readonly=True, border_width=0, disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color())],
        [sg.Column([[sg.Image(key='-IMAGE-', background_color='gray')]], key='-IMAGE-COL-', expand_x=True, expand_y=True, element_justification='l', vertical_alignment='top')]
    ]

    window = sg.Window('CSC Image Converter', layout, resizable=True, finalize=True, return_keyboard_events=True)

    window.bind('<Configure>', '-WINDOW-RESIZE-')
    window['-IMAGE-'].bind('<Motion>', '+MOTION')
    window['-IMAGE-'].bind('<Enter>', '+ENTER')
    window['-IMAGE-'].bind('<Leave>', '+LEAVE')

    current_planar_in = None
    current_planar_out = None
    current_output_pixel_depth = 10
    current_input_pixel_depth = 10
    current_output_is_yuv = False
    current_input_is_yuv = False
    current_output_full_range = True
    current_input_full_range = True
    current_output_color = ColorSpace.BT709
    current_input_color = ColorSpace.BT709
    current_csc_coefs = None
    current_csc_offset = None
    current_scale_factor = 1.0
    current_mouse_pos = None
    is_pixel_info_frozen = False
    is_mouse_in_image = False

    planar_in_full = None
    current_input_file_params = None  # (input_file, w, h, ifmt)

    def do_conversion(planar_in, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt):
        csc_config = CscCoefConfig()
        csc_config.pixel_depth = depth
        csc_config.coef_precision = precision
        csc_config.algo_type = algo_type
        mode_str = build_csc_mode_str(iclr, oclr)
        csc_config.csc_mode = parse_csc_mode_str(mode_str)

        bcsh = CscBcshConfig()
        bcsh.hue = int(values['-BCSH-hue-'])
        bcsh.saturation = int(values['-BCSH-sat-'])
        bcsh.contrast = int(values['-BCSH-contrast-'])
        bcsh.brightness = int(values['-BCSH-bright-'])
        bcsh.r_gain = int(values['-BCSH-r_gain-'])
        bcsh.g_gain = int(values['-BCSH-g_gain-'])
        bcsh.b_gain = int(values['-BCSH-b_gain-'])
        bcsh.r_offset = int(values['-BCSH-r_offset-'])
        bcsh.g_offset = int(values['-BCSH-g_offset-'])
        bcsh.b_offset = int(values['-BCSH-b_offset-'])

        if algo_type == 'RGB_on_HSV':
            output_is_rgb = is_rgb_format(ofmt)
            input_is_rgb = is_rgb_format(ifmt)

            if output_is_rgb:
                coefs, offset = get_csc_coefs(csc_config, None)
                planar_out = apply_csc(planar_in, coefs, offset, precision, depth)
                planar_out = apply_bcsh_hsv(planar_out, bcsh, depth)
            elif input_is_rgb:
                planar_in_proc = apply_bcsh_hsv(planar_in, bcsh, depth)
                coefs, offset = get_csc_coefs(csc_config, None)
                planar_out = apply_csc(planar_in_proc, coefs, offset, precision, depth)
            else:
                coefs, offset = get_csc_coefs(csc_config, bcsh)
                planar_out = apply_csc(planar_in, coefs, offset, precision, depth)
        else:
            coefs, offset = get_csc_coefs(csc_config, bcsh)
            planar_out = apply_csc(planar_in, coefs, offset, precision, depth)

        return planar_out, coefs, offset

    def update_pixel_info(window, orig_x, orig_y):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_input_is_yuv, current_output_is_yuv
        nonlocal current_scale_factor

        if current_planar_in is not None:
            # Map original coordinates to downsampled array coordinates
            ds_x = int(orig_x * current_scale_factor)
            ds_y = int(orig_y * current_scale_factor)

            h, w = current_planar_in.shape[1], current_planar_in.shape[2]

            if 0 <= ds_x < w and 0 <= ds_y < h:
                in_p0 = current_planar_in[0, ds_y, ds_x]
                in_p1 = current_planar_in[1, ds_y, ds_x]
                in_p2 = current_planar_in[2, ds_y, ds_x]
                in_str = f"({in_p0:04d}, {in_p1:04d}, {in_p2:04d})"
            else:
                in_str = "(----, ----, ----)"

            out_str = "(----, ----, ----)"
            if current_planar_out is not None:
                out_h, out_w = current_planar_out.shape[1], current_planar_out.shape[2]
                if 0 <= ds_x < out_w and 0 <= ds_y < out_h:
                    out_p0 = current_planar_out[0, ds_y, ds_x]
                    out_p1 = current_planar_out[1, ds_y, ds_x]
                    out_p2 = current_planar_out[2, ds_y, ds_x]
                    out_str = f"({out_p0:04d}, {out_p1:04d}, {out_p2:04d})"

            in_format = "yuv" if current_input_is_yuv else "rgb"
            out_format = "yuv" if current_output_is_yuv else "rgb"

            freeze_status = "[Frozen]" if is_pixel_info_frozen else "[Press Space to freeze]"
            info_text = f"Position: ({orig_x:04d},{orig_y:04d}) Input Pixel ({in_format}): {in_str} Output Pixel ({out_format}): {out_str} {freeze_status}"
            window['-PIXEL-INFO-'].update(info_text)

    def update_multiline_readonly(window, key, value):
        widget = window[key].Widget
        widget.configure(state='normal')
        window[key].update(value=value)
        # We don't set it back to 'disabled' because we handle readonly via binding '<Key>' to 'break'

    def trigger_convert(values, update_display=True):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_output_pixel_depth, current_input_pixel_depth
        nonlocal current_output_is_yuv, current_input_is_yuv
        nonlocal current_output_full_range, current_input_full_range
        nonlocal current_output_color, current_input_color
        nonlocal current_csc_coefs, current_csc_offset
        nonlocal planar_in_full, current_input_file_params
        nonlocal current_scale_factor

        input_file = values['-INPUT-FILE-']
        if not input_file or not os.path.isfile(input_file):
            return

        try:
            w = int(values['-WIDTH-'])
            h = int(values['-HEIGHT-'])
            ifmt = get_fmt_from_display(values['-IN-FMT-'])
            iclr = get_clrspc_from_display(values['-IN-CLR-'])
            ofmt = get_fmt_from_display(values['-OUT-FMT-'])
            oclr = get_clrspc_from_display(values['-OUT-CLR-'])
            precision = int(values['-PRECISION-'])

            in_depth = get_pixel_depth(ifmt)
            out_depth = get_pixel_depth(ofmt)
            depth = max(in_depth, out_depth)

            # Update the displayed pixel depth on UI
            window['-DISP-DEPTH-'].update(str(depth))
        except (ValueError, IndexError):
            return

        if h <= 0 or w <= 0:
            return

        expected_size = get_frame_size(w, h, ifmt)
        actual_size = os.path.getsize(input_file)
        if actual_size < expected_size:
            window['-PREVIEW-LABEL-'].update(value=f"Error: Input file size ({actual_size} bytes) is smaller than the expected frame size ({expected_size} bytes)!")
            window['-IMAGE-'].update(data=b'')
            return

        try:
            file_params = (input_file, w, h, ifmt)
            if planar_in_full is None or current_input_file_params != file_params:
                planar_in_full = read_raw_to_planar(input_file, w, h, ifmt)
                current_input_file_params = file_params

            # Calculate downsampling factors
            col_widget = window['-IMAGE-COL-'].Widget
            # Provide some default size before window is fully rendered
            max_display_w = max(col_widget.winfo_width() - 20, 640)
            max_display_h = max(col_widget.winfo_height() - 20, 360)

            scale_factor = min(max_display_w / w, max_display_h / h, 1.0)
            current_scale_factor = scale_factor
            disp_w = max(int(w * scale_factor), 1)
            disp_h = max(int(h * scale_factor), 1)

            # Downsample the full resolution input
            y_indices = np.linspace(0, h - 1, disp_h).astype(int)
            x_indices = np.linspace(0, w - 1, disp_w).astype(int)
            planar_in = planar_in_full[:, y_indices[:, None], x_indices]

            algo_type = values.get('-BCSH-ALGO-TYPE-', 'RK CSC')

            planar_out, coefs, offset = do_conversion(
                planar_in, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt
            )

            current_planar_in = planar_in
            current_planar_out = planar_out
            current_csc_coefs = coefs
            current_csc_offset = offset
            current_output_pixel_depth = out_depth
            current_input_pixel_depth = in_depth
            current_output_is_yuv = is_yuv_format(ofmt)
            current_input_is_yuv = is_yuv_format(ifmt)

            _, orange = clrspc_to_mode_params(oclr)
            current_output_full_range = (orange == "F")
            ocs, _ = clrspc_to_mode_params(oclr)
            if ocs.startswith("bt"):
                current_output_color = ColorSpace[ocs.upper()]
            else:
                current_output_color = ColorSpace.BT709

            _, irange = clrspc_to_mode_params(iclr)
            current_input_full_range = (irange == "F")
            ics, _ = clrspc_to_mode_params(iclr)
            if ics.startswith("bt"):
                current_input_color = ColorSpace[ics.upper()]
            else:
                current_input_color = ColorSpace.BT709

            if update_display:
                display_result(window, values)
                if current_mouse_pos is not None:
                    update_pixel_info(window, current_mouse_pos[0], current_mouse_pos[1])
        except Exception as e:
            window['-PREVIEW-LABEL-'].update(value=f"Error: {e}")
            window['-IMAGE-'].update(data=b'')

    def display_result(window, values):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_csc_coefs, current_csc_offset
        nonlocal current_scale_factor

        show_output = values.get('-SHOW-OUT-', False)

        target_planar = current_planar_out if show_output else current_planar_in
        if target_planar is None:
            window['-PREVIEW-LABEL-'].update(value="No conversion result")
            return

        target_is_yuv = current_output_is_yuv if show_output else current_input_is_yuv
        target_pixel_depth = current_output_pixel_depth if show_output else current_input_pixel_depth
        target_full_range = current_output_full_range if show_output else current_input_full_range
        target_color = current_output_color if show_output else current_input_color

        try:
            if target_is_yuv:
                y2r_config = CscCoefConfig()
                y2r_config.pixel_depth = target_pixel_depth
                y2r_config.coef_precision = 0
                y2r_mode = CscMode()
                y2r_mode.is_input_yuv = True
                y2r_mode.is_output_yuv = False
                y2r_mode.is_input_full_range = target_full_range
                y2r_mode.is_output_full_range = True
                y2r_mode.input_color_encoding = target_color
                y2r_mode.output_color_encoding = ColorSpace.BT709
                y2r_config.csc_mode = y2r_mode

                y2r_coefs, y2r_offset = get_csc_coefs(y2r_config, None)
                rgb_planar = apply_csc(target_planar, y2r_coefs, y2r_offset, 0, target_pixel_depth)
            else:
                rgb_planar = target_planar.copy()
                max_val = (1 << target_pixel_depth) - 1
                rgb_planar = np.clip(rgb_planar, 0, max_val)

            h, w = rgb_planar.shape[1], rgb_planar.shape[2]
            if target_pixel_depth > 8:
                rgb_8bit = (rgb_planar >> (target_pixel_depth - 8)).astype(np.uint8)
            else:
                rgb_8bit = rgb_planar.astype(np.uint8)

            rgb_interleaved = np.stack([rgb_8bit[0], rgb_8bit[1], rgb_8bit[2]], axis=-1)

            # target_planar is already downsampled to disp_w x disp_h
            img = Image.fromarray(rgb_interleaved, 'RGB')

            bio = io.BytesIO()
            img.save(bio, format='PNG')
            window['-IMAGE-'].update(data=bio.getvalue(), size=(w, h))

            iclr_disp = values['-IN-CLR-']
            oclr_disp = values['-OUT-CLR-']
            mode_desc = build_csc_mode_str(
                get_clrspc_from_display(iclr_disp),
                get_clrspc_from_display(oclr_disp),
            )
            coef_str = str(current_csc_coefs).replace('\n', ' ') if current_csc_coefs is not None else "None"
            offset_str = str(current_csc_offset) if current_csc_offset is not None else "None"
            preview_text = f"Display Size: {w}x{h}\tCoefs: {coef_str}\tOffset: {offset_str}"
            window['-PREVIEW-LABEL-'].update(value=preview_text)
        except Exception as e:
            window['-PREVIEW-LABEL-'].update(value=f"Display error: {e}")

    bcsh_keys = {f'-BCSH-{k}-' for _, k, _, _ in bcsh_names}.union({f'-BCSH-{k}-' for _, _, _, k in bcsh_names})
    convert_keys = {'-IN-FMT-', '-OUT-FMT-', '-IN-CLR-', '-OUT-CLR-',
                    '-PRECISION-', '-WIDTH-', '-HEIGHT-', '-BCSH-ALGO-TYPE-'}

    last_window_size = window.size

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, None):
            break

        if event == '-WINDOW-RESIZE-':
            # Only redraw if the size actually changed significantly to prevent infinite loop
            if last_window_size != window.size:
                last_window_size = window.size
                if current_planar_in is not None:
                    # Delay slightly to allow the UI layout to settle before re-calculating dimensions
                    # We call trigger_convert to re-downsample the image with the new size
                    window.perform_long_operation(lambda: None, '-REDRAW-IMAGE-')
            continue
        elif event == '-REDRAW-IMAGE-':
            trigger_convert(values)
            continue

        if event in bcsh_keys:
            val_label_key = event + 'VAL-'
            window[val_label_key].update(str(int(values[event])))
            trigger_convert(values)
        elif event == '-RESET-BCSH-':
            for _, k1, _, k2 in bcsh_names:
                window[f'-BCSH-{k1}-'].update(value=256)
                window[f'-BCSH-{k1}-VAL-'].update('256')
                values[f'-BCSH-{k1}-'] = 256
                window[f'-BCSH-{k2}-'].update(value=256)
                window[f'-BCSH-{k2}-VAL-'].update('256')
                values[f'-BCSH-{k2}-'] = 256
            trigger_convert(values)
        elif event == '-SAVE-OUT-':
            try:
                input_file = values['-INPUT-FILE-']
                w = int(values['-WIDTH-'])
                h = int(values['-HEIGHT-'])
                ifmt = get_fmt_from_display(values['-IN-FMT-'])
                iclr = get_clrspc_from_display(values['-IN-CLR-'])
                ofmt = get_fmt_from_display(values['-OUT-FMT-'])
                oclr = get_clrspc_from_display(values['-OUT-CLR-'])
                precision = int(values['-PRECISION-'])
                if not input_file or not os.path.isfile(input_file):
                    sg.popup_error("Please select a valid input file first!")
                    continue

                if current_planar_out is None or planar_in_full is None:
                    sg.popup_error("No output image generated yet. Check parameters.")
                    continue

                default_output = _get_default_output_path(input_file)
                save_path = sg.popup_get_file('Save output image as', save_as=True, default_path=default_output)
                if save_path:
                    # Calculate full resolution output
                    algo_type = values.get('-BCSH-ALGO-TYPE-', 'RK CSC')
                    in_depth = get_pixel_depth(ifmt)
                    out_depth = get_pixel_depth(ofmt)
                    depth = max(in_depth, out_depth)

                    full_planar_out, _, _ = do_conversion(
                        planar_in_full, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt
                    )

                    write_planar_to_raw(full_planar_out, save_path, w, h, ofmt)
                    sg.popup(f"Saved successfully to:\n{save_path}", title="Success")
            except Exception as e:
                sg.popup_error(f"Failed to save output:\n{e}")
        elif event in convert_keys:
            trigger_convert(values)
        elif event in ['-SHOW-IN-', '-SHOW-OUT-']:
            display_result(window, values)
        elif event == '-INPUT-FILE-':
            if values['-INPUT-FILE-'] and os.path.isfile(values['-INPUT-FILE-']):
                import re
                filepath = values['-INPUT-FILE-']
                basename = os.path.basename(filepath).lower()
                ext = os.path.splitext(basename)[1]

                updates = False
                # 1. Guess by extension
                if ext == '.yuv':
                    # YUV420SP_NV12 is 0x9. fmt_display has format: "0x9 - YUV420SP_NV12"
                    # BT709_Limited is 4. clrspc_display has format: "4 - BT709_Limited"
                    yuv_fmt = next((f for f in fmt_display if f.startswith('0x9 ')), None)
                    if yuv_fmt:
                        window['-IN-FMT-'].update(value=yuv_fmt)
                        values['-IN-FMT-'] = yuv_fmt
                        updates = True
                    bt709_l = next((c for c in clrspc_display if c.startswith('4 ')), None)
                    if bt709_l:
                        window['-IN-CLR-'].update(value=bt709_l)
                        values['-IN-CLR-'] = bt709_l
                        updates = True
                elif ext == '.rgb':
                    # RGB888 is 0x0. fmt_display has format: "0x0 - RGB888"
                    # RGB_Full is 1. clrspc_display has format: "1 - RGB_Full"
                    rgb_fmt = next((f for f in fmt_display if f.startswith('0x0 ')), None)
                    if rgb_fmt:
                        window['-IN-FMT-'].update(value=rgb_fmt)
                        values['-IN-FMT-'] = rgb_fmt
                        updates = True
                    rgb_f = next((c for c in clrspc_display if c.startswith('1 ')), None)
                    if rgb_f:
                        window['-IN-CLR-'].update(value=rgb_f)
                        values['-IN-CLR-'] = rgb_f
                        updates = True

                # 2. Guess by resolution in basename
                m_res = re.search(r'(\d+)x(\d+)', basename)
                if m_res:
                    w_str, h_str = m_res.group(1), m_res.group(2)
                    window['-WIDTH-'].update(value=w_str)
                    values['-WIDTH-'] = w_str
                    window['-HEIGHT-'].update(value=h_str)
                    values['-HEIGHT-'] = h_str
                    updates = True

                trigger_convert(values)
        elif event == '-IMAGE-+ENTER':
            is_mouse_in_image = True
        elif event == '-IMAGE-+LEAVE':
            is_mouse_in_image = False
        elif event == '-IMAGE-+MOTION':
            if current_planar_in is not None and not is_pixel_info_frozen:
                e = window['-IMAGE-'].user_bind_event
                # tkinter event coordinates are relative to the widget
                widget_x, widget_y = e.x, e.y

                # Image widget padding/border is small but we use coordinates directly
                # Map to original image coordinates using current_scale_factor
                orig_x = int(widget_x / current_scale_factor)
                orig_y = int(widget_y / current_scale_factor)

                current_mouse_pos = (orig_x, orig_y)
                update_pixel_info(window, orig_x, orig_y)

        elif event == ' ':  # Space key
            if is_mouse_in_image:
                is_pixel_info_frozen = not is_pixel_info_frozen
                if current_mouse_pos is not None:
                    update_pixel_info(window, current_mouse_pos[0], current_mouse_pos[1])

    window.close()


def main():
    parser = argparse.ArgumentParser(description="CSC image conversion tool")
    parser.add_argument("--ui", action="store_true", help="open UI interface for interactive CSC conversion")

    parser.add_argument("-i", "--input", type=str, default=None, help="input filename")
    parser.add_argument("-w", "--width", type=int, default=1920, help="input image width, default: 1920")
    parser.add_argument("-g", "--height", type=int, default=1080, help="input image height, default: 1080")
    parser.add_argument("-f", "--format", type=lambda x: int(x, 0), default=0x0,
                        help="input image format, default: 0x0, support: "
                             "rgb(0)[a(1)|planar(2)]; "
                             "yuv[444p(3)|444sp(4)|444i(5)|422p(6)|422sp(7)|420p(8)|420sp(9)|400(a)]"
                             "(+0x10 for 10bit unpacked(LSB); +0x20 for 10bit packed)")
    parser.add_argument("-r", "--clrspc", type=int, default=1,
                        help="input image colorspace, default: 1-RGBF/5-709F, "
                             "support: {0/1(RGBL/F), 2/3(601L/F), 4/5(709L/F), 8/9(2020L/F)}")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="output filename, default: 'dirname(input)/custom_output_basename'")
    parser.add_argument("-W", "--outwid", type=int, default=None, help="output image width, default: same to 'width'")
    parser.add_argument("-G", "--outhgt", type=int, default=None, help="output image height, default: same to 'height'")
    parser.add_argument("-F", "--outfmt", type=lambda x: int(x, 0), default=None,
                        help="output image format, default: mod('format',16)+0x10")
    parser.add_argument("-R", "--outclr", type=int, default=None,
                        help="output image colorspace, default: same to 'clrspc'")
    parser.add_argument("-P", "--precision", type=int, default=10,
                        help="the fixed coef precision bits 0 or [8, 16]")
    parser.add_argument("-D", "--depth", type=int, default=10,
                        help="the pixel depth bits [8, 16]")

    parser.add_argument("--hue", type=int, default=None, help="BCSH hue [0, 511], default: 256")
    parser.add_argument("--saturation", type=int, default=None, help="BCSH saturation [0, 511], default: 256")
    parser.add_argument("--contrast", type=int, default=None, help="BCSH contrast [0, 511], default: 256")
    parser.add_argument("--brightness", type=int, default=None, help="BCSH brightness [0, 511], default: 256")
    parser.add_argument("--r_gain", type=int, default=None, help="BCSH R gain [0, 511], default: 256")
    parser.add_argument("--g_gain", type=int, default=None, help="BCSH G gain [0, 511], default: 256")
    parser.add_argument("--b_gain", type=int, default=None, help="BCSH B gain [0, 511], default: 256")
    parser.add_argument("--r_offset", type=int, default=None, help="BCSH R offset [0, 511], default: 256")
    parser.add_argument("--g_offset", type=int, default=None, help="BCSH G offset [0, 511], default: 256")
    parser.add_argument("--b_offset", type=int, default=None, help="BCSH B offset [0, 511], default: 256")
    parser.add_argument("--algo-type", type=str, default="RK CSC",
                        help="BCSH algorithm type: 'RK CSC', 'RK CSC (fix contrast)', 'RGB_on_HSV'")

    args, _ = parser.parse_known_args()

    if args.depth not in [8, 10]:
        print(f"Error: pixel_depth({args.depth}) should be 8 or 10!")
        sys.exit(-1)
    if args.precision not in range(8, 17) and args.precision != 0:
        print(f"Error: coef_precision({args.precision}) should be 0 or [8, 16]!")
        sys.exit(-1)

    if args.outwid is None:
        args.outwid = args.width
    if args.outhgt is None:
        args.outhgt = args.height

    if args.ui:
        open_csc_ui(args)
    else:
        run_cli(args)


if __name__ == "__main__":
    main()
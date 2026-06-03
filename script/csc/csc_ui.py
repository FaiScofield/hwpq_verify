"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : csc_ui.py
Author      : vance.wu@rock-chips.com
Date        : 2026-06-03
Description : PySimpleGUI-based UI for interactive CSC image conversion
"""

import io
import os
import re
import numpy as np
import PySimpleGUI as sg
from PIL import Image

from get_csc_coefs import (
    CscCoefConfig,
    CscMode,
    ColorSpace,
    get_csc_coefs,
    parse_csc_mode_str,
)
from get_csc_coef_hsv import (
    ALGO_RK_HW_CSC,
    ALGO_RK_SW_CSC,
    ALGO_EVIDEO_CSC,
    ALGO_EVIDEO_CSC_PLAN_A,
    ALGO_EVIDEO_CSC_PLAN_B,
    normalize_algo_type,
    get_evideo_plan_a_steps,
    get_evideo_plan_a_runtime_steps,
    get_evideo_plan_b_steps,
)
from run_csc import (
    FORMAT_NAMES,
    CLRSPC_NAMES,
    CLRSPC_TO_PARAMS,
    FMT_OPTIONS_8BIT,
    FMT_OPTIONS_10BIT,
    CLRSPC_OPTIONS,
    clrspc_to_mode_params,
    build_csc_mode_str,
    is_yuv_format,
    is_rgb_format,
    get_pixel_depth,
    read_raw_to_planar,
    write_planar_to_raw,
    apply_csc,
    build_csc_config,
    build_bcsh_config_from_dict,
    get_default_bcsh_raw_values,
    get_rgb_gain_default_value,
    run_selected_algo,
    _get_default_output_path,
    DEBUG_DUMP_PATH,
)

RGB_GAIN_KEYS = ("r_gain", "g_gain", "b_gain")
UI_BCSH_KEY_TO_CONFIG_KEY = {
    "bright": "brightness",
    "sat": "saturation",
}


def ui_bcsh_key_to_config_key(ui_key):
    """Convert a UI BCSH key to the matching config field name."""
    return UI_BCSH_KEY_TO_CONFIG_KEY.get(ui_key, ui_key)


def get_bcsh_spin_key(slider_key):
    """Return the paired spinbox key for a BCSH slider key."""
    if not slider_key.startswith("-BCSH-") or not slider_key.endswith("-"):
        raise ValueError(f"Invalid BCSH slider key: {slider_key}")
    return slider_key[:-1] + "-SPIN-"


def normalize_bcsh_spin_value(raw_value, fallback_value):
    """Normalize a spinbox commit to an in-range integer."""
    try:
        value = int(str(raw_value).strip())
    except (TypeError, ValueError):
        return int(fallback_value)
    return max(0, min(511, value))


def step_bcsh_value(current_value, delta):
    """Step a BCSH value by delta while clamping to the valid range."""
    return max(0, min(511, int(current_value) + int(delta)))


def get_bcsh_norm_value(param_key, raw_value, algo_type):
    """
    Compute the normalized display value for a BCSH parameter.
    Returns a formatted string according to the algorithm's mapping range.
    """
    evideo_algos = {ALGO_EVIDEO_CSC, ALGO_EVIDEO_CSC_PLAN_A, ALGO_EVIDEO_CSC_PLAN_B}
    is_evideo = algo_type in evideo_algos

    if param_key in ("r_gain", "g_gain", "b_gain"):
        if is_evideo:
            norm = raw_value / 64.0
        else:
            norm = raw_value / 256.0
        return f"{norm:.2f}"
    elif param_key in ("r_offset", "g_offset", "b_offset"):
        if is_evideo:
            norm = (raw_value - 256) / 256.0
        else:
            norm = (raw_value - 256) / 2048.0
        return f"{norm:.2f}"
    elif param_key == "bright":
        if is_evideo:
            norm = (raw_value - 256) / 256.0
        else:
            norm = (raw_value - 256) / 1024.0
        return f"{norm:.2f}"
    elif param_key == "contrast":
        norm = raw_value / 256.0
        return f"{norm:.2f}"
    elif param_key == "sat":
        norm = raw_value / 256.0
        return f"{norm:.2f}"
    elif param_key == "hue":
        if is_evideo:
            norm = (raw_value - 256) * 180.0 / 256.0
        else:
            norm = (raw_value - 256) * 30.0 / 256.0
        return f"{norm:.2f}"
    return ""


def remap_rgb_gain_value_for_algo_switch(value, old_algo_type, new_algo_type):
    """Remap raw RGB gain when switching between RK-family and eVideo CSC."""
    if old_algo_type == new_algo_type:
        return int(value)

    remapped = float(value)
    rk_algo_types = {ALGO_RK_HW_CSC, ALGO_RK_SW_CSC}
    evideo_algo_types = {ALGO_EVIDEO_CSC, ALGO_EVIDEO_CSC_PLAN_A, ALGO_EVIDEO_CSC_PLAN_B}
    if old_algo_type in rk_algo_types and new_algo_type in evideo_algo_types:
        remapped /= 4.0
    elif old_algo_type in evideo_algo_types and new_algo_type in rk_algo_types:
        remapped *= 4.0

    return int(np.clip(round(remapped), 0, 511))


def open_csc_ui(args=None):
    """Open PySimpleGUI UI for interactive CSC conversion"""
    sg.theme('SystemDefault')

    fmt_options = FMT_OPTIONS_8BIT + FMT_OPTIONS_10BIT
    fmt_display = [f"0x{f:X} - {FORMAT_NAMES.get(f, 'Unknown')}" for f in fmt_options]
    clrspc_display_all = [f"{c} - {CLRSPC_NAMES[c]}" for c in CLRSPC_OPTIONS]
    clrspc_rgb = [s for s in clrspc_display_all if int(s.split(" ")[0]) in (0, 1)]
    clrspc_yuv = [s for s in clrspc_display_all if int(s.split(" ")[0]) in range(2, 8)]
    precision_values = [0] + list(range(8, 17))

    def get_fmt_from_display(display_str):
        return int(display_str.split(" ")[0], 16)

    def get_clrspc_from_display(display_str):
        return int(display_str.split(" ")[0])

    def _update_fmt_for_clrspc(window, values, fmts, iclr):
        """Auto-select input format based on colorspace when Set Color is active."""
        iclr_int = int(iclr)
        if iclr_int in (0, 1):
            # RGB full/limited -> RGB888 (0x0)
            target_fmt = next((f for f in fmts if f.startswith('0x0 ')), None)
        else:
            # YUV -> YU24 (0x3)
            target_fmt = next((f for f in fmts if f.startswith('0x3 ')), None)
        if target_fmt:
            window['-IN-FMT-'].update(value=target_fmt)
            values['-IN-FMT-'] = target_fmt

    def _update_clrspc_for_fmt(window, values, clrspc_key, fmt_str, default_clrspc=None):
        """Update a colorspace combo options to match the selected format domain."""
        fmt_code = int(fmt_str.split(" ")[0], 16)
        base = fmt_code & 0xF
        if base <= 0x2:
            options = clrspc_rgb
            default = default_clrspc or clrspc_rgb[1]  # RGB_Full
        else:
            options = clrspc_yuv
            default = default_clrspc or clrspc_yuv[3]  # BT709_Full
        window[clrspc_key].update(values=options)
        # Reset to default if current value is not in the new options
        current_val = values.get(clrspc_key, '')
        if current_val not in options:
            window[clrspc_key].update(value=default)
            values[clrspc_key] = default

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
            sg.Spin([str(i) for i in range(512)], initial_value='256', key=f'-BCSH-{k1}-SPIN-', size=(5, 1)),
            sg.Text('', size=(8, 1), key=f'-BCSH-{k1}-NORM-', justification='left'),
            sg.Text(n2, size=(10, 1)),
            sg.Slider(range=(0, 511), default_value=256, orientation='h',
                      size=(20, 15), key=f'-BCSH-{k2}-', enable_events=True, disable_number_display=True),
            sg.Spin([str(i) for i in range(512)], initial_value='256', key=f'-BCSH-{k2}-SPIN-', size=(5, 1)),
            sg.Text('', size=(8, 1), key=f'-BCSH-{k2}-NORM-', justification='left'),
        ])

    algo_type_options = [
        ALGO_RK_HW_CSC,
        ALGO_RK_SW_CSC,
        ALGO_EVIDEO_CSC,
        ALGO_EVIDEO_CSC_PLAN_A,
        ALGO_EVIDEO_CSC_PLAN_B,
    ]
    bcsh_tab_layout = [
        *bcsh_layout,
        [sg.Text('AlgoType:', size=(8, 1)),
         sg.Combo(algo_type_options, default_value=ALGO_RK_HW_CSC, key='-BCSH-ALGO-TYPE-',
                  readonly=True, size=(22, 1), enable_events=True),
         sg.Push(),
         sg.Button('Reset BCSH', key='-RESET-BCSH-')]
    ]

    input_output_layout = [
        [sg.Text('Input File:', size=(12, 1)),
         sg.Input(key='-INPUT-FILE-', size=(52, 1), enable_events=True, readonly=True),
         sg.FileBrowse('Browse...')],
        [sg.Text('Width:', size=(6, 1)), sg.Input('1920', key='-WIDTH-', size=(8, 1), enable_events=True),
         sg.Text('Height:', size=(6, 1)), sg.Input('1080', key='-HEIGHT-', size=(8, 1), enable_events=True),
         sg.Checkbox('Set Color', key='-SET-COLOR-', default=False, enable_events=True),
         sg.Input('128, 128, 128', key='-COLOR-INPUT-', size=(28, 1), enable_events=False,
                  disabled=True, disabled_readonly_background_color=sg.theme_background_color())],
        [sg.Text('Input Format:', size=(12, 1)),
         sg.Combo(fmt_display, default_value=fmt_display[0], key='-IN-FMT-',
                  readonly=True, size=(28, 1), enable_events=True),
         sg.Text('Input Colorspace:', size=(14, 1)),
         sg.Combo(clrspc_rgb, default_value=clrspc_rgb[1], key='-IN-CLR-',
                  readonly=True, size=(22, 1), enable_events=True)],
        [sg.Text('Output Format:', size=(12, 1)),
         sg.Combo(fmt_display, default_value=fmt_display[0], key='-OUT-FMT-',
                  readonly=True, size=(28, 1), enable_events=True),
         sg.Text('Output Colorspace:', size=(14, 1)),
         sg.Combo(clrspc_rgb, default_value=clrspc_rgb[1], key='-OUT-CLR-',
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
                 sg.Tab('BCSH Config', bcsh_tab_layout)]
            ])]
        ]),
        sg.Column([
             [sg.Button('Save Output', key='-SAVE-OUT-', size=(12, 2))],
             [sg.Radio('Show Input', 'RADIO1', key='-SHOW-IN-', enable_events=True, size=(12, 1))],
             [sg.Radio('Show Output', 'RADIO1', default=True, key='-SHOW-OUT-', enable_events=True, size=(12, 1))],
             [sg.Checkbox('dump', key='-DUMP-', default=False, enable_events=True, size=(12, 1))]
         ], element_justification='l', vertical_alignment='top', pad=(10, 30))],
        [sg.HorizontalSeparator()],
        [sg.Frame('Preview Info', [
            [
                sg.Text('Display Size:', size=(12, 1)),
                sg.Input('', key='-DISPLAY-SIZE-', size=(36, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
                sg.Text('Position:', size=(10, 1)),
                sg.Input('', key='-POSITION-INFO-', size=(36, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
            ],
            [
                sg.Text('Input Pixel:', size=(12, 1)),
                sg.Input('', key='-INPUT-PIXEL-INFO-', size=(36, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
                sg.Text('Output Pixel:', size=(10, 1)),
                sg.Input('', key='-OUTPUT-PIXEL-INFO-', size=(36, 1), readonly=True, border_width=0,
                         disabled_readonly_background_color=sg.theme_background_color(), disabled_readonly_text_color=sg.theme_text_color()),
            ],
        ], expand_x=True)],
        [sg.Frame('CSC Steps', [
            [
                sg.Text('Step1 Coefs:', size=(12, 1)),
                sg.Multiline('', size=(58, 1), key='-STEP1-COEFS-', disabled=True, no_scrollbar=True),
                sg.Text('Step1 Offset:', size=(12, 1)),
                sg.Multiline('', size=(28, 1), key='-STEP1-OFFSET-', disabled=True, no_scrollbar=True),
            ],
            [
                sg.Text('Step2 Coefs:', size=(12, 1)),
                sg.Multiline('', size=(58, 1), key='-STEP2-COEFS-', disabled=True, no_scrollbar=True),
                sg.Text('Step2 Offset:', size=(12, 1)),
                sg.Multiline('', size=(28, 1), key='-STEP2-OFFSET-', disabled=True, no_scrollbar=True),
            ],
        ], expand_x=True)],
        [sg.Column([[sg.Image(key='-IMAGE-', background_color='gray')]], key='-IMAGE-COL-', expand_x=True, expand_y=True, element_justification='l', vertical_alignment='top')]
    ]

    window = sg.Window('CSC Image Converter', layout, resizable=True, finalize=True, return_keyboard_events=True)
    window.TKroot.attributes('-topmost', True)
    window.TKroot.lift()
    window.TKroot.focus_force()
    window.TKroot.after(100, lambda: window.TKroot.attributes('-topmost', False))

    window.bind('<Configure>', '-WINDOW-RESIZE-')
    window['-IMAGE-'].bind('<Motion>', '+MOTION')
    window['-IMAGE-'].bind('<Enter>', '+ENTER')
    window['-IMAGE-'].bind('<Leave>', '+LEAVE')
    window['-COLOR-INPUT-'].bind('<Return>', '+ENTER')
    window['-COLOR-INPUT-'].bind('<KP_Enter>', '+ENTER')

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
    current_step1_coefs = None
    current_step1_offset = None
    current_step2_coefs = None
    current_step2_offset = None
    current_scale_factor = 1.0
    current_mouse_pos = None
    is_pixel_info_frozen = False
    is_mouse_in_image = False
    current_algo_type = ALGO_RK_HW_CSC

    planar_in_full = None
    current_input_file_params = None  # (input_file, w, h, ifmt)

    def parse_color_input(text):
        """Parse color input text into a list of 3 integers. Returns None on failure."""
        if not text or not text.strip():
            return None
        text = text.strip().replace(',', ' ')
        parts = text.split()
        nums = []
        for p in parts:
            try:
                nums.append(int(float(p)))
            except ValueError:
                continue
        if len(nums) < 3:
            sg.popup_error(f"Need 3 integer values, got {len(nums)}. Input: '{text}'")
            return None
        return nums[:3]

    def do_conversion(planar_in, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, dump_enabled=False):
        bcsh = build_bcsh_config_from_dict(
            {
                'hue': values['-BCSH-hue-'],
                'saturation': values['-BCSH-sat-'],
                'contrast': values['-BCSH-contrast-'],
                'brightness': values['-BCSH-bright-'],
                'r_gain': values['-BCSH-r_gain-'],
                'g_gain': values['-BCSH-g_gain-'],
                'b_gain': values['-BCSH-b_gain-'],
                'r_offset': values['-BCSH-r_offset-'],
                'g_offset': values['-BCSH-g_offset-'],
                'b_offset': values['-BCSH-b_offset-'],
            },
            algo_type,
        )
        return run_selected_algo(planar_in, bcsh, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, dump_enabled)

    def update_bcsh_norm_labels(window, values, algo_type):
        """Update all BCSH normalized value labels based on current slider values and algo type."""
        for _, k1, _, k2 in bcsh_names:
            for k in (k1, k2):
                raw_val = int(values[f'-BCSH-{k}-'])
                norm_str = get_bcsh_norm_value(k, raw_val, algo_type)
                window[f'-BCSH-{k}-NORM-'].update(norm_str)

    def set_bcsh_pair_value(window, values, slider_key, committed_value):
        """Synchronize one BCSH slider and its paired spinbox."""
        spin_key = get_bcsh_spin_key(slider_key)
        committed_value = int(committed_value)
        window[slider_key].update(value=committed_value)
        window[spin_key].update(value=str(committed_value))
        values[slider_key] = committed_value
        values[spin_key] = str(committed_value)

    def commit_bcsh_spin_value(window, values, spin_key):
        """Commit an edited BCSH spinbox value back to the paired slider."""
        slider_key = spin_key.replace("-SPIN-", "-")
        fallback_value = int(values[slider_key])
        committed_value = normalize_bcsh_spin_value(values.get(spin_key), fallback_value)
        set_bcsh_pair_value(window, values, slider_key, committed_value)
        return committed_value

    def emit_bcsh_ui_event(event_key, stop_default=False):
        """Build a Tk callback that forwards a custom UI event to the window."""
        def _handler(event=None):
            window.write_event_value(event_key, None)
            if stop_default:
                return "break"
            return None

        return _handler

    def update_rgb_gain_controls_for_algo_switch(window, values, old_algo_type, new_algo_type):
        """Update RGB gain sliders when switching between RK-family and eVideo CSC."""
        for gain_key in RGB_GAIN_KEYS:
            slider_key = f'-BCSH-{gain_key}-'
            current_value = int(values[slider_key])
            remapped_value = remap_rgb_gain_value_for_algo_switch(current_value, old_algo_type, new_algo_type)
            set_bcsh_pair_value(window, values, slider_key, remapped_value)

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
                in_str = f"({in_p0:4d}, {in_p1:4d}, {in_p2:4d})"
            else:
                in_str = "(----, ----, ----)"

            out_str = "(----, ----, ----)"
            if current_planar_out is not None:
                out_h, out_w = current_planar_out.shape[1], current_planar_out.shape[2]
                if 0 <= ds_x < out_w and 0 <= ds_y < out_h:
                    out_p0 = current_planar_out[0, ds_y, ds_x]
                    out_p1 = current_planar_out[1, ds_y, ds_x]
                    out_p2 = current_planar_out[2, ds_y, ds_x]
                    out_str = f"({out_p0:4d}, {out_p1:4d}, {out_p2:4d})"

            in_format = "yuv" if current_input_is_yuv else "rgb"
            out_format = "yuv" if current_output_is_yuv else "rgb"

            freeze_status = "[Frozen]" if is_pixel_info_frozen else "[Press Space to freeze]"
            window['-POSITION-INFO-'].update(f"({orig_x:4d},{orig_y:4d}) {freeze_status}")
            window['-INPUT-PIXEL-INFO-'].update(f"{in_format}: {in_str}")
            window['-OUTPUT-PIXEL-INFO-'].update(f"{out_format}: {out_str}")

    for _, k1, _, k2 in bcsh_names:
        for bcsh_key in (k1, k2):
            slider_key = f'-BCSH-{bcsh_key}-'
            spin_key = get_bcsh_spin_key(slider_key)
            window[spin_key].bind('<Return>', '+ENTER')
            window[spin_key].bind('<KP_Enter>', '+ENTER')
            window[spin_key].Widget.configure(command=emit_bcsh_ui_event(f'{spin_key}+STEP'))
            slider_widget = window[slider_key].Widget
            slider_widget.configure(takefocus=1)
            slider_widget.bind('<Button-1>', lambda event, widget=slider_widget: widget.focus_set(), add='+')
            slider_widget.bind('<Left>', emit_bcsh_ui_event(f'{slider_key}+LEFT', stop_default=True))
            slider_widget.bind('<Right>', emit_bcsh_ui_event(f'{slider_key}+RIGHT', stop_default=True))

    def update_multiline_readonly(window, key, value):
        widget = window[key].Widget
        widget.configure(state='normal')
        window[key].update(value=value)

    def trigger_convert(values, update_display=True):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_output_pixel_depth, current_input_pixel_depth
        nonlocal current_output_is_yuv, current_input_is_yuv
        nonlocal current_output_full_range, current_input_full_range
        nonlocal current_output_color, current_input_color
        nonlocal current_step1_coefs, current_step1_offset
        nonlocal current_step2_coefs, current_step2_offset
        nonlocal planar_in_full, current_input_file_params
        nonlocal current_scale_factor

        set_color = values.get('-SET-COLOR-', False)

        if set_color:
            # Use the parsed color as a flat input image
            color_vals = parse_color_input(values.get('-COLOR-INPUT-', ''))
            if color_vals is None:
                return

            try:
                w = int(values['-WIDTH-']) if values['-WIDTH-'] else 256
                h = int(values['-HEIGHT-']) if values['-HEIGHT-'] else 256
                if w <= 0:
                    w = 256
                if h <= 0:
                    h = 256
                ifmt = get_fmt_from_display(values['-IN-FMT-'])
                iclr = get_clrspc_from_display(values['-IN-CLR-'])
                ofmt = get_fmt_from_display(values['-OUT-FMT-'])
                oclr = get_clrspc_from_display(values['-OUT-CLR-'])
                precision = int(values['-PRECISION-'])

                in_depth = get_pixel_depth(ifmt)
                out_depth = get_pixel_depth(ofmt)
                depth = max(in_depth, out_depth)

                window['-DISP-DEPTH-'].update(str(depth))
            except (ValueError, IndexError):
                return

            if h <= 0 or w <= 0:
                return

            # Build flat planar from color values
            max_val = (1 << depth) - 1
            planar_in_full = np.zeros((3, h, w), dtype=np.uint16 if depth > 8 else np.uint8)
            for i in range(3):
                planar_in_full[i, :, :] = int(np.clip(color_vals[i], 0, max_val))
            current_input_file_params = None

            # Downsample for display
            scale_factor = 1.0
            disp_w, disp_h = w, h
            if w > 640 or h > 360:
                col_widget = window['-IMAGE-COL-'].Widget
                max_display_w = max(col_widget.winfo_width() - 20, 640)
                max_display_h = max(col_widget.winfo_height() - 20, 360)
                scale_factor = min(max_display_w / w, max_display_h / h, 1.0)
                current_scale_factor = scale_factor
                disp_w = max(int(w * scale_factor), 1)
                disp_h = max(int(h * scale_factor), 1)
                y_indices = np.linspace(0, h - 1, disp_h).astype(int)
                x_indices = np.linspace(0, w - 1, disp_w).astype(int)
                planar_in = planar_in_full[:, y_indices[:, None], x_indices]
            else:
                current_scale_factor = 1.0
                planar_in = planar_in_full

            algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)

            planar_out, step1_coefs, step1_offset, step2_coefs, step2_offset = do_conversion(
                planar_in, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, False
            )

            current_planar_in = planar_in
            current_planar_out = planar_out
            current_step1_coefs = step1_coefs
            current_step1_offset = step1_offset
            current_step2_coefs = step2_coefs
            current_step2_offset = step2_offset
            current_output_pixel_depth = out_depth
            current_input_pixel_depth = in_depth
            current_output_is_yuv = is_yuv_format(ofmt)
            current_input_is_yuv = is_yuv_format(ifmt)

            _, orange = clrspc_to_mode_params(oclr)
            current_output_full_range = (orange == "F")
            ocs, _ = clrspc_to_mode_params(oclr)
            current_output_color = ColorSpace[ocs.upper()] if ocs.startswith("bt") else ColorSpace.BT709

            _, irange = clrspc_to_mode_params(iclr)
            current_input_full_range = (irange == "F")
            ics, _ = clrspc_to_mode_params(iclr)
            current_input_color = ColorSpace[ics.upper()] if ics.startswith("bt") else ColorSpace.BT709

            if update_display:
                display_result(window, values)
            return

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

        from run_csc import get_frame_size

        expected_size = get_frame_size(w, h, ifmt)
        actual_size = os.path.getsize(input_file)
        if actual_size < expected_size:
            window['-DISPLAY-SIZE-'].update(value=f"Error: file too small ({actual_size} < {expected_size})")
            window['-POSITION-INFO-'].update(value='')
            window['-INPUT-PIXEL-INFO-'].update(value='')
            window['-OUTPUT-PIXEL-INFO-'].update(value='')
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

            algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)

            planar_out, step1_coefs, step1_offset, step2_coefs, step2_offset = do_conversion(
                planar_in, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, False
            )

            if values.get('-DUMP-', False):
                do_conversion(planar_in_full, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt, True)

            current_planar_in = planar_in
            current_planar_out = planar_out
            current_step1_coefs = step1_coefs
            current_step1_offset = step1_offset
            current_step2_coefs = step2_coefs
            current_step2_offset = step2_offset
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
            window['-DISPLAY-SIZE-'].update(value=f"Error: {e}")
            window['-POSITION-INFO-'].update(value='')
            window['-INPUT-PIXEL-INFO-'].update(value='')
            window['-OUTPUT-PIXEL-INFO-'].update(value='')
            window['-IMAGE-'].update(data=b'')

    def display_result(window, values):
        nonlocal current_planar_in, current_planar_out
        nonlocal current_step1_coefs, current_step1_offset
        nonlocal current_step2_coefs, current_step2_offset
        nonlocal current_scale_factor

        show_output = values.get('-SHOW-OUT-', False)

        target_planar = current_planar_out if show_output else current_planar_in
        if target_planar is None:
            window['-DISPLAY-SIZE-'].update(value="No conversion result")
            window['-POSITION-INFO-'].update(value='')
            window['-INPUT-PIXEL-INFO-'].update(value='')
            window['-OUTPUT-PIXEL-INFO-'].update(value='')
            update_multiline_readonly(window, '-STEP1-COEFS-', 'None')
            update_multiline_readonly(window, '-STEP1-OFFSET-', 'None')
            update_multiline_readonly(window, '-STEP2-COEFS-', 'None')
            update_multiline_readonly(window, '-STEP2-OFFSET-', 'None')
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
            step1_coef_str = str(current_step1_coefs).replace('\n', ' ') if current_step1_coefs is not None else "None"
            step1_offset_str = str(current_step1_offset) if current_step1_offset is not None else "None"
            step2_coef_str = str(current_step2_coefs).replace('\n', ' ') if current_step2_coefs is not None else "None"
            step2_offset_str = str(current_step2_offset) if current_step2_offset is not None else "None"
            window['-DISPLAY-SIZE-'].update(value=f"{w}x{h} ({mode_desc})")
            update_multiline_readonly(window, '-STEP1-COEFS-', step1_coef_str)
            update_multiline_readonly(window, '-STEP1-OFFSET-', step1_offset_str)
            update_multiline_readonly(window, '-STEP2-COEFS-', step2_coef_str)
            update_multiline_readonly(window, '-STEP2-OFFSET-', step2_offset_str)
        except Exception as e:
            window['-DISPLAY-SIZE-'].update(value=f"Display error: {e}")

    bcsh_keys = {f'-BCSH-{k}-' for _, k, _, _ in bcsh_names}.union({f'-BCSH-{k}-' for _, _, _, k in bcsh_names})
    bcsh_spin_keys = {get_bcsh_spin_key(key) for key in bcsh_keys}
    convert_keys = {'-IN-FMT-', '-OUT-FMT-', '-IN-CLR-', '-OUT-CLR-',
                    '-PRECISION-', '-WIDTH-', '-HEIGHT-', '-BCSH-ALGO-TYPE-'}
    convert_keys.add('-DUMP-')

    last_window_size = window.size

    # Initialize normalized value labels with default values
    default_bcsh_vals = {f'-BCSH-{k}-': 256 for _, k1, _, k2 in bcsh_names for k in (k1, k2)}
    update_bcsh_norm_labels(window, default_bcsh_vals, ALGO_RK_HW_CSC)

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
        elif event == '-SET-COLOR-':
            set_color = values.get('-SET-COLOR-', False)
            if set_color:
                window['-COLOR-INPUT-'].update(disabled=False)
            else:
                window['-COLOR-INPUT-'].update(disabled=True)
            trigger_convert(values)
            continue

        event_key, _, event_suffix = event.rpartition('+')

        if event in bcsh_keys:
            set_bcsh_pair_value(window, values, event, int(values[event]))
            update_bcsh_norm_labels(window, values, current_algo_type)
            trigger_convert(values)
        elif event_key in bcsh_spin_keys and event_suffix == 'STEP':
            commit_bcsh_spin_value(window, values, event_key)
            update_bcsh_norm_labels(window, values, current_algo_type)
            trigger_convert(values)
        elif event_key in bcsh_spin_keys and event_suffix == 'ENTER':
            commit_bcsh_spin_value(window, values, event_key)
            update_bcsh_norm_labels(window, values, current_algo_type)
            trigger_convert(values)
        elif event_key in bcsh_keys and event_suffix in {'LEFT', 'RIGHT'}:
            delta = -1 if event_suffix == 'LEFT' else 1
            stepped_value = step_bcsh_value(values[event_key], delta)
            set_bcsh_pair_value(window, values, event_key, stepped_value)
            update_bcsh_norm_labels(window, values, current_algo_type)
            trigger_convert(values)
        elif event == '-BCSH-ALGO-TYPE-':
            new_algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)
            update_rgb_gain_controls_for_algo_switch(window, values, current_algo_type, new_algo_type)
            current_algo_type = new_algo_type
            update_bcsh_norm_labels(window, values, current_algo_type)
            print(f"algo_type switch to: {new_algo_type}")
            trigger_convert(values)
        elif event == '-RESET-BCSH-':
            algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)
            default_values = get_default_bcsh_raw_values(algo_type)
            for _, k1, _, k2 in bcsh_names:
                value1 = default_values[ui_bcsh_key_to_config_key(k1)]
                value2 = default_values[ui_bcsh_key_to_config_key(k2)]
                set_bcsh_pair_value(window, values, f'-BCSH-{k1}-', value1)
                set_bcsh_pair_value(window, values, f'-BCSH-{k2}-', value2)
            update_bcsh_norm_labels(window, values, algo_type)
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
                    algo_type = values.get('-BCSH-ALGO-TYPE-', ALGO_RK_HW_CSC)
                    in_depth = get_pixel_depth(ifmt)
                    out_depth = get_pixel_depth(ofmt)
                    depth = max(in_depth, out_depth)

                    full_planar_out, _, _, _, _ = do_conversion(
                        planar_in_full, values, depth, precision, algo_type, iclr, oclr, ifmt, ofmt
                    )

                    write_planar_to_raw(full_planar_out, save_path, w, h, ofmt)
                    sg.popup(f"Saved successfully to:\n{save_path}", title="Success")
            except Exception as e:
                sg.popup_error(f"Failed to save output:\n{e}")
        elif event == '-COLOR-INPUT-+ENTER':
            trigger_convert(values)
        elif event == '-IN-CLR-' and values.get('-SET-COLOR-', False):
            _update_fmt_for_clrspc(window, values, fmt_display, get_clrspc_from_display(values['-IN-CLR-']))
            trigger_convert(values)
        elif event == '-IN-FMT-':
            _update_clrspc_for_fmt(window, values, '-IN-CLR-', values['-IN-FMT-'])
            trigger_convert(values)
        elif event == '-OUT-FMT-':
            _update_clrspc_for_fmt(window, values, '-OUT-CLR-', values['-OUT-FMT-'])
            trigger_convert(values)
        elif event in convert_keys:
            trigger_convert(values)
        elif event in ['-SHOW-IN-', '-SHOW-OUT-']:
            display_result(window, values)
        elif event == '-INPUT-FILE-':
            if values['-INPUT-FILE-'] and os.path.isfile(values['-INPUT-FILE-']):
                filepath = values['-INPUT-FILE-']
                basename = os.path.basename(filepath).lower()
                ext = os.path.splitext(basename)[1]

                # 1. Guess by extension
                if ext == '.yuv':
                    # YUV420SP_NV12 is 0x9, BT709_Limited is 4
                    yuv_fmt = next((f for f in fmt_display if f.startswith('0x9 ')), None)
                    if yuv_fmt:
                        window['-IN-FMT-'].update(value=yuv_fmt)
                        values['-IN-FMT-'] = yuv_fmt
                    bt709_l = next((c for c in clrspc_yuv if c.startswith('4 ')), None)
                    if bt709_l:
                        window['-IN-CLR-'].update(value=bt709_l)
                        values['-IN-CLR-'] = bt709_l
                    elif yuv_fmt:
                        _update_clrspc_for_fmt(window, values, '-IN-CLR-', yuv_fmt, clrspc_yuv[0])
                elif ext == '.rgb':
                    # RGB888 is 0x0, RGB_Full is 1
                    rgb_fmt = next((f for f in fmt_display if f.startswith('0x0 ')), None)
                    if rgb_fmt:
                        window['-IN-FMT-'].update(value=rgb_fmt)
                        values['-IN-FMT-'] = rgb_fmt
                    rgb_f = next((c for c in clrspc_rgb if c.startswith('1 ')), None)
                    if rgb_f:
                        window['-IN-CLR-'].update(value=rgb_f)
                        values['-IN-CLR-'] = rgb_f
                    elif rgb_fmt:
                        _update_clrspc_for_fmt(window, values, '-IN-CLR-', rgb_fmt, clrspc_rgb[1])

                # 2. Guess by resolution in basename
                m_res = re.search(r'(\d+)x(\d+)', basename)
                if m_res:
                    w_str, h_str = m_res.group(1), m_res.group(2)
                    window['-WIDTH-'].update(value=w_str)
                    values['-WIDTH-'] = w_str
                    window['-HEIGHT-'].update(value=h_str)
                    values['-HEIGHT-'] = h_str

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

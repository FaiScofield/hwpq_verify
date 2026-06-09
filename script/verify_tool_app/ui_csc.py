"""
CSC module tab for PQ Test Tool.

Provides colorspace conversion controls (BCSH, Algo Type, Precision),
Sat/Hue test panel, and CSC processing logic.
References csc/csc_ui.py and csc/run_csc.py implementations.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Ensure the parent script/ package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"csc"))

import numpy as np
from PIL import Image, ImageDraw
import PySimpleGUI as sg

from verify_tool_app.ui_helpers import (
    SliderSpinConfig,
    LINE,
    STATUS_ERROR,
    STATUS_OK,
    update_status as update_status,
    bind_keyboard_events as _bind_kb_shared,
    handle_keyboard_event,
    sync_slider_to_spin,
    sync_spin_to_slider,
    sync_all_norms,
)

TAB_LABEL = "CSC"

from csc.get_csc_coef_hsv import (
    ALGO_RK_HW_CSC,
    ALGO_RK_SW_CSC,
    ALGO_EVIDEO_CSC,
    ALGO_EVIDEO_CSC_PLAN_A,
    ALGO_EVIDEO_CSC_PLAN_B,
    normalize_algo_type,
)
from csc.run_csc import (
    build_bcsh_config_from_dict,
    run_selected_algo,
    get_pixel_depth,
    get_default_bcsh_raw_values,
)

from csc.csc_ui import (
    get_bcsh_norm_value,
    remap_rgb_gain_value_for_algo_switch,
    RGB_GAIN_KEYS,
)


# CSC Support image formats
CSC_SUPPORT_IO_FORMATS = defaultdict(list, {
    0x0: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13],
    0x1: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13],
    0x2: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13],
    0x3: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13],
    0x4: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x4, 0x14],
    0x5: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x5, 0x15],
    0x6: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x6, 0x16],
    0x7: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x7, 0x17],
    0x8: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x8, 0x18],
    0x9: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x9, 0x19],
    0xA: [0xA, 0x1A],
    0x10: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13],
    0x11: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13],
    0x12: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13],
    0x13: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13],
    0x14: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x4, 0x14],
    0x15: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x5, 0x15],
    0x16: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x6, 0x16],
    0x17: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x7, 0x17],
    0x18: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x8, 0x18],
    0x19: [0x0, 0x1, 0x2, 0x3, 0x10, 0x11, 0x12, 0x13, 0x9, 0x19],
    0x1A: [0xA, 0x1A],
})

# ------------------------------------------------------------------ #
# Data model                                                         #
# ------------------------------------------------------------------ #

BCSH_KEYS = ["bright", "contrast", "sat", "hue",
             "r_gain", "r_offset", "g_gain", "g_offset", "b_gain", "b_offset"]

BCSH_DEFAULT = {
    "bright": 256, "contrast": 256, "sat": 256, "hue": 256,
    "r_gain": 256, "r_offset": 256,
    "g_gain": 256, "g_offset": 256,
    "b_gain": 256, "b_offset": 256,
}

CHANNEL_SWAP_TYPES = ["None", "V1_SWAP", "V2_Y2R_R2R", "V2_R2Y_R2R", "V2_Y2R_Y2Y"]

PRECISION_VALUES = [0] + list(range(8, 17))

ALGO_TYPE_OPTIONS = [
    ALGO_RK_HW_CSC,
    ALGO_RK_SW_CSC,
    ALGO_EVIDEO_CSC,
    ALGO_EVIDEO_CSC_PLAN_A,
    ALGO_EVIDEO_CSC_PLAN_B,
]

BCSH_NAMES = [
    ("Brightness", "bright", "Contrast", "contrast"),
    ("Saturation", "sat", "Hue", "hue"),
    ("R Gain", "r_gain", "R Offset", "r_offset"),
    ("G Gain", "g_gain", "G Offset", "g_offset"),
    ("B Gain", "b_gain", "B Offset", "b_offset"),
]

# SliderSpinConfig pairs generated from BCSH_NAMES
CSC_SLIDER_SPIN_PAIRS: list[SliderSpinConfig] = []
for _label1, _key1, _label2, _key2 in BCSH_NAMES:
    for _k in (_key1, _key2):
        pair = SliderSpinConfig(
            spin_key=f"-BCSH-{_k}-SPIN-",
            slider_key=f"-BCSH-{_k}-",
            min_val=0, max_val=511, def_val=256,
            norm_key=f"-BCSH-{_k}-NORM-",
            norm_func=lambda v, vals, k=_k: _bcsh_norm_func(k, v, vals),
        )
        CSC_SLIDER_SPIN_PAIRS.append(pair)


def _bcsh_norm_func(key: str, raw_val: float, values: dict) -> str:
    """Compute normalized BCSH display string from raw slider value."""
    algo_type = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    return get_bcsh_norm_value(key, int(raw_val), algo_type)


# ------------------------------------------------------------------ #
# Colormap helpers (referenced from csc_ui.py)                       #
# ------------------------------------------------------------------ #

SAT_COLORMAP_SIZE = 416  # effective image area size (px)
SAT_MARGIN = 48          # border margin for axes/labels
_DATA_RANGE_MAX = 128    # max data value, range is [-128, 127] or [-128, 128]
_DATA_SIZE = 256         # total data range size


def _load_font(size):
    """Load a font for colormap axis labels."""
    font_path = Path(__file__).resolve().parents[2] / "data" / "fonts" / "NotoSans-Regular.ttf"
    try:
        from PIL import ImageFont
        return ImageFont.truetype(str(font_path), size)
    except Exception:
        return None


def _data_to_pix(val):
    """Map a float data value in [-128, 128] to pixel coordinate [0, SAT_COLORMAP_SIZE-1]."""
    return int(round((val + _DATA_RANGE_MAX) * SAT_COLORMAP_SIZE / _DATA_SIZE))


def _pix_to_data(pix):
    """Map pixel [0, SIZE-1] to continuous float data value in [-128, 127.5]."""
    return pix * _DATA_SIZE / SAT_COLORMAP_SIZE - _DATA_RANGE_MAX


def _ycbcr2rgb(y, cb, cr):
    """Convert YCbCr to RGB (BT.709), returns 0-255 uint8 arrays."""
    ycbcr = np.stack([np.asarray(y, dtype=np.float32),
                       np.asarray(cb, dtype=np.float32),
                       np.asarray(cr, dtype=np.float32)], axis=-1)
    g_y2r = np.array([[1.0, 0.0, 1.5748], [1.0, -0.187324, -0.468124], [1.0, 1.8556, 0.0]], dtype=np.float32)
    rgb = np.dot(ycbcr.reshape(-1, 3), g_y2r.T).reshape(ycbcr.shape)
    r = np.clip(rgb[..., 0] + 0.5, 0, 255).astype(np.uint8)
    g = np.clip(rgb[..., 1] + 0.5, 0, 255).astype(np.uint8)
    b = np.clip(rgb[..., 2] + 0.5, 0, 255).astype(np.uint8)
    return r, g, b


def _rgb2hsv(r, g, b):
    """Convert RGB (0-255) to HSV, returns h(0-360), s(0-1), v(0-1)."""
    r = np.asarray(r, dtype=np.float32) / 255.0
    g = np.asarray(g, dtype=np.float32) / 255.0
    b = np.asarray(b, dtype=np.float32) / 255.0
    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    delta = maxc - minc
    h = np.zeros_like(maxc)
    cond = delta != 0
    rc = np.where(cond, (maxc - r) / delta, 0)
    gc = np.where(cond, (maxc - g) / delta, 0)
    bc = np.where(cond, (maxc - b) / delta, 0)
    h = np.where(cond & (maxc == r), bc - gc, h)
    h = np.where(cond & (maxc == g), 2.0 + rc - bc, h)
    h = np.where(cond & (maxc == b), 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0 * 360.0
    s = np.where(maxc != 0, delta / maxc, 0.0)
    v = maxc
    return h, s, v


def _hsv2rgb(h, s, v):
    """Convert HSV to RGB, returns 0-255 uint8 arrays."""
    h = np.asarray(h, dtype=np.float32) % 360
    s = np.asarray(s, dtype=np.float32)
    v = np.asarray(v, dtype=np.float32)
    c = v * s
    x = c * (1 - np.abs((h / 60) % 2 - 1))
    m = v - c
    r = np.zeros_like(h)
    g = np.zeros_like(h)
    b = np.zeros_like(h)
    for lo, hi, rc, gc, bc in [(0, 60, c, x, 0), (60, 120, x, c, 0), (120, 180, 0, c, x),
                                (180, 240, 0, x, c), (240, 300, x, 0, c), (300, 360, c, 0, x)]:
        mask = (h >= lo) & (h < hi)
        r[mask] = rc[mask] if isinstance(rc, np.ndarray) else rc
        g[mask] = gc[mask] if isinstance(gc, np.ndarray) else gc
        b[mask] = bc[mask] if isinstance(bc, np.ndarray) else bc
    r = np.clip((r + m) * 255 + 0.5, 0, 255).astype(np.uint8)
    g = np.clip((g + m) * 255 + 0.5, 0, 255).astype(np.uint8)
    b = np.clip((b + m) * 255 + 0.5, 0, 255).astype(np.uint8)
    return r, g, b


def _build_colormap_yuv(luma_val):
    """Build YCbCr->RGB colormap for a fixed luma value. Returns PIL Image."""
    w, h_img = SAT_COLORMAP_SIZE, SAT_COLORMAP_SIZE
    cb_grid = _pix_to_data(np.tile(np.arange(w, dtype=np.float32), (h_img, 1)))
    cr_grid = _pix_to_data(np.tile(np.arange(h_img - 1, -1, -1, dtype=np.float32).reshape(-1, 1), (1, w)))
    y = np.full((h_img, w), float(luma_val), dtype=np.float32)
    r, g, b = _ycbcr2rgb(y, cb_grid, cr_grid)
    return Image.fromarray(np.stack([r, g, b], axis=-1), 'RGB')


def _build_colormap_rgb(value_val):
    """Build HSV->RGB colormap for a fixed V value. Returns PIL Image."""
    w, h_img = SAT_COLORMAP_SIZE, SAT_COLORMAP_SIZE
    pix_x = np.tile(np.arange(w, dtype=np.float32), (h_img, 1))
    pix_y = np.tile(np.arange(h_img - 1, -1, -1, dtype=np.float32).reshape(-1, 1), (1, w))
    cx = _pix_to_data(pix_x) / _DATA_RANGE_MAX
    cy = _pix_to_data(pix_y) / _DATA_RANGE_MAX
    h = (np.arctan2(cy, cx) * 180.0 / np.pi + 360.0) % 360.0
    s = np.sqrt(cx ** 2 + cy ** 2)
    v = np.full((h_img, w), float(value_val) / 255.0, dtype=np.float32)
    r, g, b = _hsv2rgb(h, s, v)
    mask = s > 1.0
    r[mask], g[mask], b[mask] = 220, 220, 220
    return Image.fromarray(np.stack([r, g, b], axis=-1), 'RGB')


def _build_colormap_with_axis(img_eff, title, xlabel, ylabel):
    """Add margin and axes to a colormap PIL Image. Returns (padded_img, margin_size)."""
    margin = SAT_MARGIN
    w, h_img = img_eff.size
    total_w, total_h = w + 2 * margin, h_img + 2 * margin
    padded = Image.new('RGB', (total_w, total_h), (255, 255, 255))
    padded.paste(img_eff, (margin, margin))
    draw = ImageDraw.Draw(padded)
    font = _load_font(16)
    axis_color = (0, 0, 0)
    tick_color = (64, 64, 64)
    # Origin at center of effective area
    cx0 = _data_to_pix(0)
    cy0 = _data_to_pix(0)
    x0 = margin + cx0
    y0 = margin + (SAT_COLORMAP_SIZE - 1) - cy0
    # Axes
    draw.line([(margin, y0), (total_w - margin, y0)], fill=axis_color, width=2)
    draw.line([(x0, margin), (x0, total_h - margin)], fill=axis_color, width=2)
    # Ticks
    tick_data_vals = [-128, -96, -64, -32, 0, 32, 64, 96]
    for dv in tick_data_vals:
        x = margin + _data_to_pix(dv)
        draw.line([(x, y0 - 4), (x, y0 + 4)], fill=tick_color, width=1)
        if font and dv != 0:
            draw.text((x + 3, y0 + 5), str(dv), fill=tick_color, font=font)
        y = margin + (SAT_COLORMAP_SIZE - 1) - _data_to_pix(dv)
        draw.line([(x0 - 4, y), (x0 + 4, y)], fill=tick_color, width=1)
        if font and dv != 0:
            draw.text((x0 - 30, y - 8), str(dv), fill=tick_color, font=font)
    # Labels
    if font:
        draw.text((total_w - margin + 8, y0 - 10), xlabel, fill=axis_color, font=font)
        draw.text((x0 + 5, margin - 22), ylabel, fill=axis_color, font=font)
        bbox = draw.textbbox((0, 0), title, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((total_w // 2 - tw // 2, 4), title, fill=axis_color, font=font)
    return padded, margin


# ------------------------------------------------------------------ #
# Layout                                                             #
# ------------------------------------------------------------------ #

def _build_bcsh_layout() -> list:
    """Build the BCSH parameter control rows."""
    tooltips = {
        "bright": "亮度调整（0~511，256为原始值）",
        "contrast": "对比度调整（0~511，256为原始值）",
        "sat": "饱和度调整（0~511，256为原始值）",
        "hue": "色相调整（0~511，256为原始值，对应0度）",
        "r_gain": "红色通道增益（0~511，256为原始值）",
        "r_offset": "红色通道偏移（0~511，256为零偏移）",
        "g_gain": "绿色通道增益（0~511，256为原始值）",
        "g_offset": "绿色通道偏移（0~511，256为零偏移）",
        "b_gain": "蓝色通道增益（0~511，256为原始值）",
        "b_offset": "蓝色通道偏移（0~511，256为零偏移）",
    }
    rows = []
    for n1, k1, n2, k2 in BCSH_NAMES:
        rows.append([
            sg.Text(n1, size=(10, 1)),
            sg.Slider(
                range=(0, 511), default_value=256, orientation="h",
                size=(15, 15), key=f"-BCSH-{k1}-", enable_events=True,
                disable_number_display=True,
                tooltip=tooltips.get(k1, f"调整{k1}参数（0~511）"),
            ),
            sg.Spin(
                [str(i) for i in range(512)], initial_value="256",
                key=f"-BCSH-{k1}-SPIN-", size=(5, 1),
                tooltip=tooltips.get(k1, f"直接输入{k1}数值（0~511）"),
            ),
            sg.Text("", size=(8, 1), key=f"-BCSH-{k1}-NORM-", justification="left"),
            sg.Text(n2, size=(10, 1)),
            sg.Slider(
                range=(0, 511), default_value=256, orientation="h",
                size=(15, 15), key=f"-BCSH-{k2}-", enable_events=True,
                disable_number_display=True,
                tooltip=tooltips.get(k2, f"调整{k2}参数（0~511）"),
            ),
            sg.Spin(
                [str(i) for i in range(512)], initial_value="256",
                key=f"-BCSH-{k2}-SPIN-", size=(5, 1),
                tooltip=tooltips.get(k2, f"直接输入{k2}数值（0~511）"),
            ),
            sg.Text("", size=(8, 1), key=f"-BCSH-{k2}-NORM-", justification="left"),
        ])
    return rows


def _build_sathue_frame() -> list:
    """Build the Sat/Hue test Frame layout."""
    return [
        [
            sg.Frame(
                "Sat/Hue Test",
                [
                    [
                        sg.Checkbox(
                            "Show Color Map", key="-SAT-SHOW-MAP-", size=(12, 1), default=False, enable_events=True,
                            tooltip="启用后右预览区显示饱和度/色相色度图"
                        ),
                        sg.Combo(
                            ["YUV", "RGB"],
                            default_value="YUV",
                            key="-SAT-CLRSPC-",
                            readonly=True,
                            size=(12, 1),
                            enable_events=True,
                            tooltip="色度图色彩空间：YUV模式或RGB模式",
                        ),
                    ],
                    [
                        sg.Checkbox(
                            "Set Src Color", key="-SAT-SET-COLOR-", size=(12, 1), default=False, enable_events=True,
                            tooltip="启用在色度图上点击选色，将所选色值设为CSC输入颜色"
                        ),
                        sg.Input(
                            "",
                            key="-SAT-COLOR-INPUT-",
                            size=(12, 1),
                            disabled=True,
                            disabled_readonly_background_color=sg.theme_background_color(),
                            tooltip="当前色度图选中色值（Y,U,V 或 R,G,B）",
                        ),
                    ],
                    [
                        sg.Text("Luma/Value:", size=(10, 1)),
                        sg.Slider(
                            range=(0, 255),
                            default_value=204,
                            orientation="h",
                            size=(10, 15),
                            key="-SAT-LUMA-",
                            enable_events=True,
                            disable_number_display=True,
                            tooltip="色度图的亮度/明度值（0~255）",
                        ),
                        sg.Spin([str(i) for i in range(256)], initial_value="204", key="-SAT-LUMA-SPIN-", size=(5, 1),
                                tooltip="直接输入亮度/明度值（0~255）"),
                    ],
                ],
                expand_x=True,
            )
        ]
    ]


def _build_coef_info_layout() -> list:
    """Build the CSC Coef Info display section."""
    return [
        [sg.Frame("CSC Coef Info", [
            [
                sg.Text("Step1 Coefs", size=(12, 1)),
                sg.Multiline("", size=(50, 1), key="-STEP1-COEFS-", disabled=True, no_scrollbar=True),
                sg.Text("Step1 Offset", size=(12, 1)),
                sg.Multiline("", size=(25, 1), key="-STEP1-OFFSET-", disabled=True, no_scrollbar=True),
            ],
            [
                sg.Text("Step2 Coefs", size=(12, 1)),
                sg.Multiline("", size=(50, 1), key="-STEP2-COEFS-", disabled=True, no_scrollbar=True),
                sg.Text("Step2 Offset", size=(12, 1)),
                sg.Multiline("", size=(25, 1), key="-STEP2-OFFSET-", disabled=True, no_scrollbar=True),
            ],
        ])],
    ]


def build_controls() -> list:
    """Build the CSC module tab layout.

    Left column: CSC Config Frame (Algo Type + BCSH sliders).
    Right column: Sat/Hue Test Frame.
    Below both: CSC Coef Info.
    """
    csc_config_rows = [
        [
            sg.Text("Algo Type"),
            sg.Combo(
                ALGO_TYPE_OPTIONS, default_value=ALGO_RK_HW_CSC,
                key="-BCSH-ALGO-TYPE-", readonly=True,
                enable_events=True,
                tooltip="CSC算法实现方法",
            ),
            sg.Text("Precision"),
            sg.Combo(
                [str(v) for v in PRECISION_VALUES], default_value="10",
                key="-PRECISION-", readonly=True,
                enable_events=True,
                tooltip="CSC计算精度",
            ),
            sg.Text("Channel Swap (VOP)"),
            sg.Combo(
                CHANNEL_SWAP_TYPES, default_value="None",
                key="-CHANNEL-SWAP-", readonly=True,
                enable_events=True,
                tooltip="VOP通道交换模式",
            ),
            sg.Button("Reset BCSH", key="-RESET-BCSH-",
                      tooltip="将所有BCSH参数重置为默认值256"),
            sg.Button("Save Config", key="-CSC-SAVE-CFG-",
                      tooltip="保存配置参数到json配置文件"),
        ],
    ]
    csc_config_rows.extend(_build_bcsh_layout())

    layout = [
        [
            sg.Column([
                [sg.Frame("CSC Config", csc_config_rows, expand_x=True, expand_y=True)]
            ], expand_x=True, expand_y=True, vertical_alignment="top"),
            sg.Column(
                _build_sathue_frame(),
                expand_y=True,
                vertical_alignment="top",
            ),
        ],
    ]
    layout.extend(_build_coef_info_layout())
    return layout


# ------------------------------------------------------------------ #
# Event handling                                                     #
# ------------------------------------------------------------------ #

def handle_csc_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle CSC-specific events. Returns True if consumed."""
    # Keyboard suffix events + reset button clicks via shared handler
    if handle_keyboard_event(event, values, window, CSC_SLIDER_SPIN_PAIRS):
        return True

    # SAT-LUMA keyboard events (single special pair)
    sat_luma_handled = handle_keyboard_event(
        event, values, window,
        [SliderSpinConfig("-SAT-LUMA-SPIN-", "-SAT-LUMA-", 0, 255, 128)]
    )
    if sat_luma_handled:
        return True

    # BCSH slider/spin direct sync
    for pair in CSC_SLIDER_SPIN_PAIRS:
        if event == pair.slider_key:
            sync_slider_to_spin(window, values, pair.slider_key, pair.spin_key, pair.step, pair)
            return True
        if event == pair.spin_key:
            sync_spin_to_slider(window, values, pair.spin_key, pair.slider_key, pair)
            return True

    if event == "-RESET-BCSH-":
        _reset_bcsh(window, values)
        return True

    # Save Config button — write UI values to CONFIG-PATH json file
    if event == "-CSC-SAVE-CFG-":
        config_path = values.get("-CONFIG-PATH-", "").strip()
        if not config_path:
            update_status(window, "CSC", LINE(), "No config file path specified", level=STATUS_ERROR)
            return True
        try:
            _save_csc_config_from_ui(values, config_path)
            update_status(window, "CSC", LINE(), f"Config saved to {config_path}", level=STATUS_OK)
        except Exception as e:
            update_status(window, "CSC", LINE(), str(e), level=STATUS_ERROR)
        return True

    # Algo type switch with RGB gain remap
    if event == "-BCSH-ALGO-TYPE-":
        _handle_algo_type_switch(window, values)
        return True

    # Sat/Hue events
    if event == "-SAT-SET-COLOR-":
        enabled = values["-SAT-SET-COLOR-"]
        window["-SAT-COLOR-INPUT-"].update(disabled=not enabled)
        return True

    if event == "-SAT-SHOW-MAP-":
        return True

    if event == "-SAT-CLRSPC-":
        return True

    if event in ("-SAT-LUMA-", "-SAT-LUMA-SPIN-"):
        _sync_sathue_slider_spin(window, values, "LUMA", 0, 255, int)
        return True

    return False


# Track algo type for RGB gain remap
_current_algo_type = ALGO_RK_HW_CSC


def _handle_algo_type_switch(window: sg.Window, values: dict):
    """Handle algo type switch and remap RGB gain values."""
    global _current_algo_type
    new_algo_type = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    old_algo_type = _current_algo_type
    for gain_key in RGB_GAIN_KEYS:
        slider_key = f"-BCSH-{gain_key}-"
        current_value = int(values[slider_key])
        remapped = remap_rgb_gain_value_for_algo_switch(current_value, old_algo_type, new_algo_type)
        window[slider_key].update(value=remapped)
        window[f"-BCSH-{gain_key}-SPIN-"].update(value=str(remapped))
        values[slider_key] = remapped
        values[f"-BCSH-{gain_key}-SPIN-"] = str(remapped)
    _current_algo_type = new_algo_type
    # Refresh all norm labels for the new algo type
    sync_all_norms(window, values, CSC_SLIDER_SPIN_PAIRS)


def _sync_sathue_slider_spin(window: sg.Window, values: dict, suffix: str,
                              min_val: int, max_val: int, spin_fmt):
    """Sync Sat/Hue Slider and Spin bidirectionally."""
    slider_key = f"-SAT-{suffix}-"
    spin_key = f"-SAT-{suffix}-SPIN-"
    slider_val = int(values[slider_key])
    spin_val = values[spin_key]

    if values.get(slider_key) is not None:
        window[spin_key].update(value=str(spin_fmt(slider_val)))
    try:
        sv = int(spin_val)
        sv = max(min_val, min(max_val, sv))
        window[slider_key].update(value=sv)
    except (ValueError, TypeError):
        pass


def _reset_bcsh(window: sg.Window, values: dict = None):
    """Reset all BCSH controls to algorithm-specific defaults."""
    algo_type = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC) if values else ALGO_RK_HW_CSC
    defaults = get_default_bcsh_raw_values(algo_type)
    key_map = {
        "brightness": "bright", "contrast": "contrast",
        "saturation": "sat", "hue": "hue",
        "r_gain": "r_gain", "r_offset": "r_offset",
        "g_gain": "g_gain", "g_offset": "g_offset",
        "b_gain": "b_gain", "b_offset": "b_offset",
    }
    for config_key, ui_key in key_map.items():
        default_val = defaults.get(config_key, 256)
        window[f"-BCSH-{ui_key}-"].update(value=default_val)
        window[f"-BCSH-{ui_key}-SPIN-"].update(value=str(default_val))
    # Refresh all norm labels
    sync_all_norms(window, values, CSC_SLIDER_SPIN_PAIRS)


# ------------------------------------------------------------------ #
# Module protocol                                                    #
# ------------------------------------------------------------------ #

def read_params(values: dict) -> dict:
    """Extract CSC module parameters from window values."""
    params = {}
    for _, k1, _, k2 in BCSH_NAMES:
        for k in (k1, k2):
            slider_key = f"-BCSH-{k}-"
            try:
                params[k] = int(values.get(slider_key, 256))
            except (ValueError, TypeError):
                params[k] = BCSH_DEFAULT.get(k, 256)
    params["algo_type"] = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    try:
        params["precision"] = int(values.get("-PRECISION-", "10"))
    except ValueError:
        params["precision"] = 10

    # Sat/Hue params (hue/sat from BCSH)
    params["sat_luma"] = int(float(values.get("-SAT-LUMA-", "204")))
    params["sat_show_map"] = values.get("-SAT-SHOW-MAP-", False)
    params["bcsh_hue"] = params.get("hue", 256)
    params["bcsh_sat"] = params.get("sat", 256)
    params["sat_clrspc"] = values.get("-SAT-CLRSPC-", "Input Colorspace")

    return params


def process(src_frame, io_info: dict):
    """Run CSC processing.

    Args:
        src_frame: ImageFrame with input data, fmt, clrspc.
        io_info: dict with "out_fmt", "out_clrspc", "elements",
                 and common I/O metadata.

    Returns:
        (ok: bool, dst_frame: ImageFrame | str)
        On success: (True, dst_frame)
        On failure: (False, error_message)
    """
    from verify_tool_app.pq_verify_tool import ImageFrame

    try:
        input_fmt = src_frame.fmt
        input_clrspc = src_frame.clrspc
        output_fmt = io_info["out_fmt"]
        output_clrspc = io_info["out_clrspc"]
        params = read_params(io_info["elements"])

        in_depth = get_pixel_depth(input_fmt)
        out_depth = get_pixel_depth(output_fmt)
        pixel_depth = max(in_depth, out_depth)

        algo_type = normalize_algo_type(params.get("algo_type", ALGO_RK_HW_CSC))
        precision = params.get("precision", 10)

        bcsh_config = build_bcsh_config_from_dict({
            "brightness": params.get("bright", 256),
            "contrast": params.get("contrast", 256),
            "saturation": params.get("sat", 256),
            "hue": params.get("hue", 256),
            "r_gain": params.get("r_gain", 256),
            "r_offset": params.get("r_offset", 256),
            "g_gain": params.get("g_gain", 256),
            "g_offset": params.get("g_offset", 256),
            "b_gain": params.get("b_gain", 256),
            "b_offset": params.get("b_offset", 256),
        }, algo_type)

        input_data = np.stack([src_frame.pyr, src_frame.pug, src_frame.pvb], axis=0)

        output_data, step1_coefs, step1_offset, step2_coefs, step2_offset = run_selected_algo(
            input_data, bcsh_config, pixel_depth, precision,
            algo_type, input_clrspc, output_clrspc,
            input_fmt, output_fmt,
        )

        dst_frame = ImageFrame(output_data[0], output_data[1], output_data[2],
                               output_fmt, output_clrspc)

        # Update CSC Coef Info UI
        _update_coef_info(io_info, step1_coefs, step1_offset, step2_coefs, step2_offset)

        return True, dst_frame
    except Exception as e:
        return False, str(e)


def _update_coef_info(io_info: dict, step1_coefs, step1_offset, step2_coefs, step2_offset):
    """Update the CSC Coef Info display on the UI."""
    window = io_info.get("window")
    if window is None:
        return
    try:
        window["-STEP1-COEFS-"].update(_format_coef_array(step1_coefs))
        window["-STEP1-OFFSET-"].update(_format_coef_array(step1_offset))
        window["-STEP2-COEFS-"].update(_format_coef_array(step2_coefs))
        window["-STEP2-OFFSET-"].update(_format_coef_array(step2_offset))
    except Exception:
        pass


def _format_coef_array(arr) -> str:
    """Format a numpy array or list as compact numeric string."""
    if arr is None:
        return "N/A"
    if hasattr(arr, "flatten"):
        arr = arr.flatten()
    is_int = arr.dtype.kind in ("i", "u") if hasattr(arr, "dtype") else all(
        isinstance(v, (int, np.integer)) for v in arr)
    if is_int:
        vals = [str(int(v)) for v in arr[:9]]
    else:
        vals = [f"{float(v):.3f}" for v in arr[:9]]
    if len(arr) > 9:
        vals.append("...")
    return "[" + ", ".join(vals) + "]"


def get_right_preview_image(snapshot, params: dict):
    """Return Sat/Hue color map for right preview, or None if disabled."""
    if not params.get("sat_show_map", False):
        return None

    clrspc = params.get("sat_clrspc", "Input Colorspace")
    luma = params.get("sat_luma", 204)

    if clrspc == "RGB":
        img_eff = _build_colormap_rgb(luma)
        title = f"HSV->RGB  (V={luma})"
        xlabel, ylabel = "S*cos(H)", "S*sin(H)"
    else:
        # Default: YUV mode (also for "Input Colorspace")
        img_eff = _build_colormap_yuv(luma)
        title = f"YCbCr->RGB  (Y={luma})"
        xlabel, ylabel = "Cb", "Cr"

    full_img, _ = _build_colormap_with_axis(img_eff, title, xlabel, ylabel)
    return np.array(full_img)

def right_preview_mouse_motion():
    # todo
    return None


# ------------------------------------------------------------------ #
# Save Config                                                        #
# ------------------------------------------------------------------ #

# Map UI BCSH keys to CscConfig attribute names
_CSC_UI_KEY_TO_ATTR = {
    "bright":     "cscBrightness",
    "contrast":   "cscContrast",
    "sat":        "cscSaturation",
    "hue":        "cscHue",
    "r_gain":     "cscRGain",
    "r_offset":   "cscROffset",
    "g_gain":     "cscGGain",
    "g_offset":   "cscGOffset",
    "b_gain":     "cscBGain",
    "b_offset":   "cscBOffset",
}


def _save_csc_config_from_ui(values: dict, config_path: str):
    """Save current CSC UI control values to a JSON config file via CscConfig."""
    from config_def.module_config_csc import CscConfig

    cfg = CscConfig()

    # Populate BCSH params from UI slider values
    for ui_key, attr_name in _CSC_UI_KEY_TO_ATTR.items():
        slider_key = f"-BCSH-{ui_key}-"
        val = int(values.get(slider_key, 256))
        setattr(cfg, attr_name, val)

    # Algo type → convert mode index
    algo_type = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    import csc.get_csc_coefs as csc_core
    mode_map = {v: k for k, v in csc_core.g_supported_standard_convert_modes.items()}
    for i, key in enumerate(csc_core.g_supported_standard_convert_modes.keys()):
        if csc_core.g_supported_standard_convert_modes[key] == algo_type:
            cfg.cscConvertMode = i
            break

    # Precision
    try:
        cfg.cscCoefPrecision = int(values.get("-PRECISION-", "10"))
    except ValueError:
        cfg.cscCoefPrecision = 10

    # Update computed coefficients
    cfg.update_csc_coefs()

    # Save to file
    cfg.dump(config_path)


# ------------------------------------------------------------------ #
# Keyboard bindings                                                  #
# ------------------------------------------------------------------ #

def bind_keyboard_events(window: sg.Window):
    """Bind keyboard events on all CSC sliders and spins."""
    _bind_kb_shared(window, CSC_SLIDER_SPIN_PAIRS)
    # SAT-LUMA: bind individually (single special pair)
    _bind_kb_shared(
        window,
        [SliderSpinConfig("-SAT-LUMA-SPIN-", "-SAT-LUMA-", 0, 255, 128)]
    )

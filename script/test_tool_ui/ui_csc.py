"""
CSC module tab for PQ Test Tool.

Provides colorspace conversion controls (BCSH, Algo Type, Precision),
Sat/Hue test panel, and CSC processing logic.
References csc/csc_ui.py and csc/run_csc.py implementations.
"""

import numpy as np
import PySimpleGUI as sg

from get_csc_coefs import (
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
)
from csc.run_csc import (
    clrspc_to_mode_params,
    build_csc_mode_str,
    is_yuv_format,
    read_raw_to_planar,
    apply_csc,
    build_csc_config,
    build_bcsh_config_from_dict,
    get_default_bcsh_raw_values,
    get_rgb_gain_default_value,
    run_selected_algo,
)

from .ui_io import get_fmt_from_display, get_clrspc_from_display

TAB_LABEL = "CSC"

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

PRECISION_VALUES = [0] + list(range(8, 17))

ALGO_TYPE_OPTIONS = [
    ALGO_RK_HW_CSC,
    ALGO_RK_SW_CSC,
    ALGO_EVIDEO_CSC,
    ALGO_EVIDEO_CSC_PLAN_A,
    ALGO_EVIDEO_CSC_PLAN_B,
]

BCSH_NAMES = [
    ("Brightness:", "bright", "Contrast:", "contrast"),
    ("Saturation:", "sat", "Hue:", "hue"),
    ("R Gain:", "r_gain", "R Offset:", "r_offset"),
    ("G Gain:", "g_gain", "G Offset:", "g_offset"),
    ("B Gain:", "b_gain", "B Offset:", "b_offset"),
]


# ------------------------------------------------------------------ #
# Layout                                                             #
# ------------------------------------------------------------------ #

def _build_bcsh_layout() -> list:
    """Build the BCSH parameter control rows."""
    rows = []
    for n1, k1, n2, k2 in BCSH_NAMES:
        rows.append([
            sg.Text(n1, size=(10, 1)),
            sg.Slider(
                range=(0, 511), default_value=256, orientation="h",
                size=(20, 15), key=f"-BCSH-{k1}-", enable_events=True,
                disable_number_display=True,
            ),
            sg.Spin(
                [str(i) for i in range(512)], initial_value="256",
                key=f"-BCSH-{k1}-SPIN-", size=(5, 1),
            ),
            sg.Text("", size=(8, 1), key=f"-BCSH-{k1}-NORM-", justification="left"),
            sg.Text(n2, size=(10, 1)),
            sg.Slider(
                range=(0, 511), default_value=256, orientation="h",
                size=(20, 15), key=f"-BCSH-{k2}-", enable_events=True,
                disable_number_display=True,
            ),
            sg.Spin(
                [str(i) for i in range(512)], initial_value="256",
                key=f"-BCSH-{k2}-SPIN-", size=(5, 1),
            ),
            sg.Text("", size=(8, 1), key=f"-BCSH-{k2}-NORM-", justification="left"),
        ])
    return rows


def _build_sathue_frame() -> list:
    """Build the Sat/Hue test Frame layout."""
    return [
        [sg.Frame("Sat/Hue Test", [
            [
                sg.Checkbox("Show Color Map", key="-SAT-SHOW-MAP-", default=False, enable_events=True),
                sg.Combo(
                    ["Input Colorspace", "YUV", "RGB"],
                    default_value="Input Colorspace",
                    key="-SAT-CLRSPC-",
                    readonly=True,
                    size=(16, 1),
                    enable_events=True,
                ),
            ],
            [
                sg.Text("Luma/Value:", size=(14, 1)),
                sg.Slider(
                    range=(0, 255), default_value=204, orientation="h",
                    size=(20, 15), key="-SAT-LUMA-", enable_events=True,
                    disable_number_display=True,
                ),
                sg.Spin(
                    [str(i) for i in range(256)], initial_value="204",
                    key="-SAT-LUMA-SPIN-", size=(5, 1),
                ),
                sg.Checkbox("Set Src Color", key="-SAT-SET-COLOR-", default=False, enable_events=True),
                sg.Input(
                    "", key="-SAT-COLOR-INPUT-", size=(28, 1), disabled=True,
                    disabled_readonly_background_color=sg.theme_background_color(),
                ),
            ],
            [
                sg.Text("Hue:", size=(14, 1)),
                sg.Slider(
                    range=(-180, 180), default_value=0, resolution=1, orientation="h",
                    size=(20, 15), key="-SAT-HUE-", enable_events=True,
                    disable_number_display=True,
                ),
                sg.Spin(
                    [str(i) for i in range(-180, 181)], initial_value="0",
                    key="-SAT-HUE-SPIN-", size=(5, 1),
                ),
                sg.Button("Reset", key="-SAT-HUE-RESET-", size=(5, 1)),
            ],
            [
                sg.Text("Saturation:", size=(14, 1)),
                sg.Slider(
                    range=(0, 360), default_value=180, resolution=1, orientation="h",
                    size=(20, 15), key="-SAT-SAT-", enable_events=True,
                    disable_number_display=True,
                ),
                sg.Spin(
                    [f"{i / 180:.2f}" for i in range(361)], initial_value="1.00",
                    key="-SAT-SAT-SPIN-", size=(5, 1),
                ),
                sg.Button("Reset", key="-SAT-SAT-RESET-", size=(5, 1)),
            ],
        ], expand_x=True)]
    ]


def _build_coef_info_layout() -> list:
    """Build the CSC Coef Info display section."""
    return [
        [sg.HorizontalSeparator()],
        [sg.Frame("CSC Coef Info", [
            [
                sg.Text("Step1 Coefs:", size=(12, 1)),
                sg.Multiline("", size=(58, 1), key="-STEP1-COEFS-", disabled=True, no_scrollbar=True),
                sg.Text("Step1 Offset:", size=(12, 1)),
                sg.Multiline("", size=(28, 1), key="-STEP1-OFFSET-", disabled=True, no_scrollbar=True),
            ],
            [
                sg.Text("Step2 Coefs:", size=(12, 1)),
                sg.Multiline("", size=(58, 1), key="-STEP2-COEFS-", disabled=True, no_scrollbar=True),
                sg.Text("Step2 Offset:", size=(12, 1)),
                sg.Multiline("", size=(28, 1), key="-STEP2-OFFSET-", disabled=True, no_scrollbar=True),
            ],
        ], expand_x=True)],
    ]


def build_controls() -> list:
    """Build the CSC module tab layout."""
    layout = [
        [
            sg.Text("Algo Type:", size=(10, 1)),
            sg.Combo(
                ALGO_TYPE_OPTIONS, default_value=ALGO_RK_HW_CSC,
                key="-BCSH-ALGO-TYPE-", readonly=True, size=(22, 1),
                enable_events=True,
            ),
            sg.Text("Precision (0=float):", size=(16, 1)),
            sg.Combo(
                [str(v) for v in PRECISION_VALUES], default_value="10",
                key="-PRECISION-", readonly=True, size=(6, 1),
                enable_events=True,
            ),
            sg.Push(),
            sg.Button("Reset BCSH", key="-RESET-BCSH-"),
        ],
    ]
    layout.extend(_build_bcsh_layout())
    layout.append([sg.HorizontalSeparator()])
    layout.extend(_build_sathue_frame())
    layout.extend(_build_coef_info_layout())
    return layout


# ------------------------------------------------------------------ #
# Event handling                                                     #
# ------------------------------------------------------------------ #

def handle_csc_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle CSC-specific events. Returns True if consumed."""
    # BCSH slider/spin sync
    for _, k1, _, k2 in BCSH_NAMES:
        for k in (k1, k2):
            slider_key = f"-BCSH-{k}-"
            spin_key = f"-BCSH-{k}-SPIN-"
            if event == slider_key:
                _sync_bcsh_slider(window, values, k)
                return True
            if event == spin_key:
                _sync_bcsh_spin(window, values, k)
                return True

    if event == "-RESET-BCSH-":
        _reset_bcsh(window)
        return True

    # Sat/Hue events
    if event == "-SAT-SET-COLOR-":
        enabled = values["-SAT-SET-COLOR-"]
        window["-SAT-COLOR-INPUT-"].update(disabled=not enabled)
        return True

    if event in ("-SAT-LUMA-", "-SAT-LUMA-SPIN-"):
        _sync_sathue_slider_spin(window, values, "LUMA", 0, 255, int)
        return True

    if event in ("-SAT-HUE-", "-SAT-HUE-SPIN-"):
        _sync_sathue_slider_spin(window, values, "HUE", -180, 180, int)
        return True

    if event == "-SAT-HUE-RESET-":
        window["-SAT-HUE-"].update(value=0)
        window["-SAT-HUE-SPIN-"].update(value="0")
        return True

    if event in ("-SAT-SAT-", "-SAT-SAT-SPIN-"):
        _sync_sathue_slider_spin(window, values, "SAT", 0, 360, lambda v: f"{v / 180:.2f}")
        return True

    if event == "-SAT-SAT-RESET-":
        window["-SAT-SAT-"].update(value=180)
        window["-SAT-SAT-SPIN-"].update(value="1.00")
        return True

    return False


def _sync_bcsh_slider(window: sg.Window, values: dict, key: str):
    """Sync Spin to Slider value on BCSH Slider change."""
    val = int(values[f"-BCSH-{key}-"])
    window[f"-BCSH-{key}-SPIN-"].update(value=str(val))
    norm = (val - 256) / 256.0
    window[f"-BCSH-{key}-NORM-"].update(value=f"({norm:+.2f})")


def _sync_bcsh_spin(window: sg.Window, values: dict, key: str):
    """Sync Slider to Spin value on BCSH Spin change."""
    try:
        val = int(values[f"-BCSH-{key}-SPIN-"])
    except ValueError:
        return
    val = max(0, min(511, val))
    window[f"-BCSH-{key}-"].update(value=val)
    norm = (val - 256) / 256.0
    window[f"-BCSH-{key}-NORM-"].update(value=f"({norm:+.2f})")


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
        if suffix == "SAT":
            pv = float(spin_val)
            sv = int(round(pv * 180))
            sv = max(min_val, min(max_val, sv))
            window[slider_key].update(value=sv)
        else:
            sv = int(spin_val)
            sv = max(min_val, min(max_val, sv))
            window[slider_key].update(value=sv)
    except (ValueError, TypeError):
        pass


def _reset_bcsh(window: sg.Window):
    """Reset all BCSH controls to defaults."""
    for _, k1, _, k2 in BCSH_NAMES:
        for k in (k1, k2):
            default = BCSH_DEFAULT.get(k, 256)
            window[f"-BCSH-{k}-"].update(value=default)
            window[f"-BCSH-{k}-SPIN-"].update(value=str(default))
            window[f"-BCSH-{k}-NORM-"].update(value="")


# ------------------------------------------------------------------ #
# Module protocol                                                    #
# ------------------------------------------------------------------ #

def read_params(values: dict) -> dict:
    """Extract CSC module parameters from window values."""
    params = {}
    for _, k1, _, k2 in BCSH_NAMES:
        for k in (k1, k2):
            try:
                params[k] = int(values.get(f"-BCSH-{k}-SPIN-", "256"))
            except ValueError:
                params[k] = BCSH_DEFAULT.get(k, 256)
    params["algo_type"] = values.get("-BCSH-ALGO-TYPE-", ALGO_RK_HW_CSC)
    try:
        params["precision"] = int(values.get("-PRECISION-", "10"))
    except ValueError:
        params["precision"] = 10

    # Sat/Hue params
    params["sat_luma"] = int(values.get("-SAT-LUMA-", "204"))
    params["sat_hue"] = int(values.get("-SAT-HUE-", "0"))
    params["sat_sat"] = int(values.get("-SAT-SAT-", "180"))
    params["sat_show_map"] = values.get("-SAT-SHOW-MAP-", False)
    params["sat_set_color"] = values.get("-SAT-SET-COLOR-", False)
    params["sat_color_input"] = values.get("-SAT-COLOR-INPUT-", "")
    params["sat_clrspc"] = values.get("-SAT-CLRSPC-", "Input Colorspace")

    return params


def process(input_data: np.ndarray, input_fmt: int, input_clrspc: int,
            output_fmt: int, output_clrspc: int, params: dict):
    """Run CSC processing.

    Args:
        input_data: Input planar numpy array (3, H, W).
        input_fmt: Input pixel format code.
        input_clrspc: Input colorspace code.
        output_fmt: Output pixel format code.
        output_clrspc: Output colorspace code.
        params: CSC module parameters from read_params().

    Returns:
        (ok: bool, output_data: np.ndarray | str)
        On success: (True, output_planar)
        On failure: (False, error_message)
    """
    try:
        in_cs, in_range = clrspc_to_mode_params(input_clrspc)
        out_cs, out_range = clrspc_to_mode_params(output_clrspc)
        mode_str = build_csc_mode_str(input_clrspc, output_clrspc)
        mode = parse_csc_mode_str(mode_str)

        csc_config = build_csc_config(mode, input_clrspc, output_clrspc)

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
        })

        algo_type = normalize_algo_type(params.get("algo_type", ALGO_RK_HW_CSC))
        precision = params.get("precision", 10)

        output_data = run_selected_algo(
            input_data, csc_config, bcsh_config,
            algo_type, precision,
            input_fmt, output_fmt,
        )

        return True, output_data
    except Exception as e:
        return False, str(e)


def get_right_preview_image(snapshot, params: dict):
    """Return Sat/Hue color map or None."""
    # Sat/Hue color map rendering is complex; defer to future implementation.
    return None

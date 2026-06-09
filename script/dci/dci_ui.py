"""
PySimpleGUI-based DCI_SHP Runner UI.

Provides five panels:
  1. Input panel       -- file paths, geometry, format
  2. Audit control     -- enable, node/export masks, override knobs
  3. Preview panel     -- input/output preview, simulated preview
  4. Data panel        -- histogram plots, global curve plots, metrics text
  5. Action panel      -- Run, Refresh, Save Config & Result, Open Output Dir
"""

import io
import json
import os
import re
import sys
from dataclasses import dataclass

# Ensure the parent script/ package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import PySimpleGUI as sg
from PIL import Image

from csc.run_csc import get_frame_size, get_pixel_depth, is_yuv_format, read_raw_to_planar

from dci.dci_models import (
    DciAuditConfig,
    DciAuditOverride,
    DciRunnerRequest,
    write_runner_request,
)
from dci.dci_runner import load_runner_result, run_dci_request
from dci.dci_workspace import (
    check_working_set_ready,
    load_working_set,
    resolve_preview_paths,
    save_snapshot,
)
from dci.dci_plot import (
    build_curve_series,
    render_curve_figure,
    render_histogram_figure,
)


DEFAULT_OUTPUT_DIR = "D:\\RkDefaultDumpData\\"
DEFAULT_CONFIG_PATH = r"D:\RkDefaultDumpData\dci_config.json"

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
    6: "BT2020_Limited",
    7: "BT2020_Full",
}

FMT_OPTIONS = [
    0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A,
    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A,
]
CLRSPC_OPTIONS = [0, 1, 2, 3, 4, 5, 6, 7]
FMT_DISPLAY = [f"0x{fmt:x} - {FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]
CLRSPC_DISPLAY = [f"{clr} - {CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
DEFAULT_FMT_DISPLAY = next(item for item in FMT_DISPLAY if item.startswith("0x0 "))
DEFAULT_CLRSPC_DISPLAY = next(item for item in CLRSPC_DISPLAY if item.startswith("1 "))
CLRSPC_DISPLAY_RGB = [s for s in CLRSPC_DISPLAY if int(s.split(" ")[0]) in (0, 1)]
CLRSPC_DISPLAY_YUV = [s for s in CLRSPC_DISPLAY if int(s.split(" ")[0]) in range(2, 8)]


# ------------------------------------------------------------------ #
# UI State                                                           #
# ------------------------------------------------------------------ #


@dataclass
class DciUiState:
    """Mutable UI state that survives between event loop iterations."""

    exe_path: str = ""
    request_path: str = ""
    result_path: str = ""
    workspace: dict | None = None
    last_runner_result: dict | None = None


# ------------------------------------------------------------------ #
# Layout builders                                                    #
# ------------------------------------------------------------------ #


IO_LABEL_SIZE = (14, 1)
IO_PATH_INPUT_SIZE = (52, 1)
IO_FMT_LABEL_SIZE = (14, 1)
IO_CLR_LABEL_SIZE = (16, 1)
IO_FMT_COMBO_SIZE = (24, 1)
IO_CLR_COMBO_SIZE = (20, 1)
IO_BROWSE_BUTTON_SIZE = (8, 1)
IO_PAIR_LEFT_LABEL_SIZE = (10, 1)
IO_PAIR_RIGHT_LABEL_SIZE = (10, 1)


def _update_clrspc_for_fmt(window: sg.Window, values: dict, clrspc_key: str, fmt_str: str):
    """Update a colorspace combo options to match the selected format domain."""
    fmt_code = int(fmt_str.split(" ")[0], 16)
    base = fmt_code & 0xF
    if base <= 0x2:
        options = CLRSPC_DISPLAY_RGB
        default = CLRSPC_DISPLAY_RGB[1]  # RGB_Full
    else:
        options = CLRSPC_DISPLAY_YUV
        default = CLRSPC_DISPLAY_YUV[3]  # BT709_Full
    current_val = values.get(clrspc_key, "")
    new_val = current_val if current_val in options else default
    window[clrspc_key].update(values=options, value=new_val)
    _enforce_combo_width(window, clrspc_key, IO_CLR_COMBO_SIZE[0])
    values[clrspc_key] = new_val


def _enforce_combo_width(window: sg.Window, key: str, width_chars: int):
    """Keep combo widget width stable after runtime value list updates."""
    try:
        window[key].Widget.configure(width=width_chars)
    except Exception:
        pass


def _show_native_raw_preview(window: sg.Window, values: dict):
    """Read raw input file and show native preview image."""
    input_file = values.get("-INPUT-", "").strip()
    if not input_file or not os.path.isfile(input_file):
        return

    try:
        w = int(values.get("-WIDTH-", "1920"))
        h = int(values.get("-HEIGHT-", "1080"))
    except ValueError:
        w, h = 1920, 1080

    fmt_str = values.get("-IN-FMT-", DEFAULT_FMT_DISPLAY)
    fmt = int(fmt_str.split(" ")[0], 16)

    expected_size = get_frame_size(w, h, fmt)
    actual_size = os.path.getsize(input_file)
    if actual_size < expected_size:
        return

    try:
        planar, fmt = read_raw_to_planar(input_file, w, h, fmt, True)
    except Exception:
        return

    depth = get_pixel_depth(fmt)
    max_val = (1 << depth) - 1

    if is_yuv_format(fmt):
        # Simple BT.709 YCbCr to RGB for preview
        y = planar[0].astype(np.float32)
        cb = planar[1].astype(np.float32) - (max_val // 2)
        cr = planar[2].astype(np.float32) - (max_val // 2)
        r = np.clip(y + 1.5748 * cr, 0, max_val)
        g = np.clip(y - 0.187324 * cb - 0.468124 * cr, 0, max_val)
        b = np.clip(y + 1.8556 * cb, 0, max_val)
        rgb_planar = np.stack([r, g, b]).astype(planar.dtype)
    else:
        rgb_planar = planar

    if depth > 8:
        rgb_8bit = (rgb_planar >> (depth - 8)).astype(np.uint8)
    else:
        rgb_8bit = rgb_planar.astype(np.uint8)

    rgb_interleaved = np.stack([rgb_8bit[0], rgb_8bit[1], rgb_8bit[2]], axis=-1)
    img = Image.fromarray(rgb_interleaved, "RGB")

    # Downscale if too large for preview
    max_preview = 640
    if max(img.size) > max_preview:
        ratio = max_preview / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.Resampling.LANCZOS)

    bio = io.BytesIO()
    img.save(bio, format="PNG")
    window["-NATIVE-PREVIEW-"].update(data=bio.getvalue())


def _build_input_output_layout() -> list:
    """Build the input and output configuration tab."""
    return [
        [
            sg.Text("Runner EXE", size=IO_LABEL_SIZE),
            sg.Input(key="-EXE-", size=IO_PATH_INPUT_SIZE),
            sg.FileBrowse(
                file_types=(("Executable", "*.exe"),),
                size=IO_BROWSE_BUTTON_SIZE,
            ),
        ],
        [
            sg.Text("Output Dir", size=IO_LABEL_SIZE),
            sg.Input(DEFAULT_OUTPUT_DIR, key="-OUTPUT-DIR-", size=IO_PATH_INPUT_SIZE),
            sg.FolderBrowse(size=IO_BROWSE_BUTTON_SIZE),
            sg.Button("Explor", size=IO_BROWSE_BUTTON_SIZE, key="-OPEN-DIR-"),
        ],
        [
            sg.Text("Snapshot Root", size=IO_LABEL_SIZE),
            sg.Input(DEFAULT_OUTPUT_DIR, key="-SNAPROOT-", size=IO_PATH_INPUT_SIZE),
            sg.FolderBrowse(size=IO_BROWSE_BUTTON_SIZE),
            sg.Button("Explor", size=IO_BROWSE_BUTTON_SIZE, key="-OPEN-SNAPROOT-"),
        ],
        [
            sg.Text("Config Path", size=IO_LABEL_SIZE),
            sg.Input(DEFAULT_CONFIG_PATH, key="-CONFIG-", size=IO_PATH_INPUT_SIZE),
            sg.FileBrowse(size=IO_BROWSE_BUTTON_SIZE),
            sg.Button("Load", key="-LOAD-CONFIG-", size=IO_BROWSE_BUTTON_SIZE),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Input File", size=IO_LABEL_SIZE),
            sg.Input(key="-INPUT-", size=IO_PATH_INPUT_SIZE, enable_events=True),
            sg.FileBrowse(size=IO_BROWSE_BUTTON_SIZE),
        ],
        [
            sg.Text("Width", size=IO_PAIR_LEFT_LABEL_SIZE),
            sg.Input("1920", size=(8, 1), key="-WIDTH-"),
            sg.Text("Height", size=IO_PAIR_RIGHT_LABEL_SIZE),
            sg.Input("1080", size=(8, 1), key="-HEIGHT-"),
            sg.Text("Frame Idx", size=IO_PAIR_LEFT_LABEL_SIZE),
            sg.Input("0", size=(8, 1), key="-FRAMEIDX-"),
            sg.Text("Frame Num", size=IO_PAIR_RIGHT_LABEL_SIZE),
            sg.Input("1", size=(8, 1), key="-FRAMENUM-"),
        ],
        [
            sg.Text("Input Format", size=IO_FMT_LABEL_SIZE),
            sg.Combo(
                FMT_DISPLAY,
                default_value=DEFAULT_FMT_DISPLAY,
                key="-IN-FMT-",
                readonly=True,
                size=IO_FMT_COMBO_SIZE,
                enable_events=True,
            ),
            sg.Text("Input Colorspace", size=IO_CLR_LABEL_SIZE),
            sg.Combo(
                CLRSPC_DISPLAY_RGB,
                default_value=CLRSPC_DISPLAY_RGB[1],  # RGB_Full
                key="-IN-CLR-",
                readonly=True,
                size=IO_CLR_COMBO_SIZE,
            ),
        ],
        [
            sg.Text("Output Format", size=IO_FMT_LABEL_SIZE),
            sg.Combo(
                FMT_DISPLAY,
                default_value=DEFAULT_FMT_DISPLAY,
                key="-OUT-FMT-",
                readonly=True,
                size=IO_FMT_COMBO_SIZE,
                enable_events=True,
            ),
            sg.Text("Output Colorspace", size=IO_CLR_LABEL_SIZE),
            sg.Combo(
                CLRSPC_DISPLAY_RGB,
                default_value=CLRSPC_DISPLAY_RGB[1],  # RGB_Full
                key="-OUT-CLR-",
                readonly=True,
                size=IO_CLR_COMBO_SIZE,
            ),
        ],
    ]

def _build_dci_config_layout() -> list:
    """Build the DCI configuration tab with merged audit controls."""
    return [
        [
            sg.Checkbox("Enable Audit", default=False, key="-AUDIT-ENABLE-"),
            sg.Text("Tag", size=(4, 1)),
            sg.Input("ui_live", size=(20, 1), key="-TAG-"),
        ],
        [
            sg.Text("Node Mask", size=(10, 1)),
            sg.Input("0", size=(8, 1), key="-NODEMASK-"),
            sg.Text("Export Mask", size=(11, 1)),
            sg.Input("0", size=(8, 1), key="-EXPORTMASK-"),
            sg.Text("Debug Dump Mask", size=(14, 1)),
            sg.Input("0", size=(8, 1), key="-DUMPMASK-"),
        ],
        [sg.HorizontalSeparator()],
        _build_numeric_control_row(
            "CF/HE Ratio",
            "-CFHE-",
            "-CFHE-SLIDER-",
            32,
            0,
            64,
        ),
        _build_numeric_control_row(
            "BS Set Point",
            "-BS-",
            "-BS-SLIDER-",
            80,
            0,
            255,
        ),
        _build_numeric_control_row(
            "WS Set Point",
            "-WS-",
            "-WS-SLIDER-",
            80,
            0,
            255,
        ),
        _build_numeric_control_row(
            "CLAHE Local Ratio",
            "-CLAHE-R-",
            "-CLAHE-R-SLIDER-",
            19,
            0,
            32,
        ),
        _build_numeric_control_row(
            "CLAHE Clip Value",
            "-CLAHE-C-",
            "-CLAHE-C-SLIDER-",
            1.0,
            0.0,
            8.0,
            resolution=0.1,
        ),
    ]




def _build_numeric_control_row(
    label: str,
    spin_key: str,
    slider_key: str,
    default_value: int | float,
    min_value: int | float,
    max_value: int | float,
    resolution: float = 1.0,
    label_size: tuple = (22, 1),
) -> list:
    """Build one numeric control row with a synchronized spinbox and slider."""
    steps = int(round((max_value - min_value) / resolution))
    spin_values = [
        round(min_value + index * resolution, 1 if resolution < 1 else 0)
        for index in range(steps + 1)
    ]
    if resolution >= 1:
        spin_values = [int(value) for value in spin_values]

    return [
        sg.Text(label, size=label_size),
        sg.Slider(
            range=(min_value, max_value),
            default_value=default_value,
            resolution=resolution,
            orientation="h",
            size=(28, 15),
            key=slider_key,
            enable_events=True,
            disable_number_display=True,
        ),
        sg.Spin(
            spin_values,
            initial_value=default_value,
            size=(8, 1),
            key=spin_key,
            enable_events=True,
        ),
    ]


def _build_shp_config_layout() -> list:
    """Build the SHP configuration tab."""
    return [
        [sg.Checkbox("Enable SHP", default=True, key="-SHP-ENABLE-")],
        _build_numeric_control_row(
            "Peaking Gain",
            "-SHP-PEAKING-GAIN-",
            "-SHP-PEAKING-GAIN-SLIDER-",
            160,
            0,
            1024,
        ),
        [
            sg.Checkbox("Enable Coring", default=True, key="-SHP-CORING-ENABLE-"),
        ],
        _build_numeric_control_row(
            "Coring Threshold",
            "-SHP-CORING-THRESHOLD-",
            "-SHP-CORING-THRESHOLD-SLIDER-",
            0,
            0,
            255,
        ),
        [
            sg.Checkbox("Enable Shoot Ctrl", default=True, key="-SHP-SHOOT-ENABLE-"),
        ],
        _build_numeric_control_row(
            "Shoot Over",
            "-SHP-SHOOT-OVER-",
            "-SHP-SHOOT-OVER-SLIDER-",
            8,
            0,
            255,
        ),
        _build_numeric_control_row(
            "Shoot Under",
            "-SHP-SHOOT-UNDER-",
            "-SHP-SHOOT-UNDER-SLIDER-",
            64,
            0,
            255,
        ),
    ]





def _build_action_panel() -> list:
    """Build the action bar."""
    return [
        [
            sg.Button("Run", size=(10, 1), key="-RUN-"),
            sg.Button("Refresh", size=(10, 1), key="-REFRESH-"),
            sg.Button("Save Config & Result", size=(18, 1), key="-SAVE-"),
        ],
        [sg.Text("", key="-STATUS-", text_color="gray", size=(60, 1))],
    ]


def _build_main_layout() -> list:
    """Assemble the full UI layout."""
    return [
        [sg.Text("DCI_SHP Runner", font=("Helvetica", 14, "bold"))],
        [sg.HorizontalSeparator()],
        [
            sg.TabGroup(
                [[
                    sg.Tab("I/O Config", _build_input_output_layout()),
                    sg.Tab("DCI Config", _build_dci_config_layout()),
                    sg.Tab("SHP Config", _build_shp_config_layout()),
                ]],
                expand_x=True,
            )
        ],
        [sg.Frame("Actions", _build_action_panel(), expand_x=True)],
        [sg.HorizontalSeparator()],
        [
            sg.Column(
                [
                    [sg.Frame("Native Preview", [[sg.Image(key="-NATIVE-PREVIEW-")]], expand_x=True)],
                    [sg.Frame("Simulated Preview", [[sg.Image(key="-SIM-PREVIEW-")]], expand_x=True)],
                ],
                vertical_alignment="top",
            ),
            sg.Column(
                [
                    [sg.Frame("Global Curves", [[sg.Image(key="-CURVES-")]], expand_x=True)],
                    [sg.Frame("Histograms", [[sg.Image(key="-HISTS-")]], expand_x=True)],
                ],
                vertical_alignment="top",
            ),
        ],
        [sg.Frame("Metrics", [[sg.Multiline("", size=(80, 10), key="-METRICS-", disabled=True)]], expand_x=True)],
    ]


# ------------------------------------------------------------------ #
# Action helpers                                                     #
# ------------------------------------------------------------------ #


def _build_request_from_values(
    values: dict, runtime_config_path: str | None = None
) -> DciRunnerRequest:
    """Build a DciRunnerRequest from current UI field values."""
    input_format = _parse_format_display(
        values.get("-IN-FMT-", DEFAULT_FMT_DISPLAY), 0x0
    )
    input_colorspace = _parse_colorspace_display(
        values.get("-IN-CLR-", DEFAULT_CLRSPC_DISPLAY), 1
    )
    output_format = _parse_format_display(
        values.get("-OUT-FMT-", DEFAULT_FMT_DISPLAY), 0x0
    )
    output_colorspace = _parse_colorspace_display(
        values.get("-OUT-CLR-", DEFAULT_CLRSPC_DISPLAY), 1
    )
    pixel_format = input_format

    try:
        width = int(values.get("-WIDTH-", "1920"))
    except ValueError:
        width = 1920
    try:
        height = int(values.get("-HEIGHT-", "1080"))
    except ValueError:
        height = 1080
    try:
        frame_idx = int(values.get("-FRAMEIDX-", "0"))
    except ValueError:
        frame_idx = 0
    try:
        frame_num = int(values.get("-FRAMENUM-", "1"))
    except ValueError:
        frame_num = 1
    try:
        dump_mask = int(values.get("-DUMPMASK-", "0"))
    except ValueError:
        dump_mask = 0

    # Audit overrides
    override = DciAuditOverride(
        enable_cf_he_ratio_override=1,
        cf_he_ratio=_try_int(values.get("-CFHE-", "32"), 32),
        enable_bs_set_point_override=1,
        bs_set_point=_try_int(values.get("-BS-", "80"), 80),
        enable_ws_set_point_override=1,
        ws_set_point=_try_int(values.get("-WS-", "80"), 80),
        enable_clahe_local_ratio_override=1,
        clahe_local_ratio=_try_int(values.get("-CLAHE-R-", "19"), 19),
        enable_clahe_clip_value_override=1,
        clahe_clip_value=_try_float(values.get("-CLAHE-C-", "1.0"), 1.0),
    )

    audit = DciAuditConfig(
        enable=1 if values.get("-AUDIT-ENABLE-") else 0,
        node_mask=_try_int(values.get("-NODEMASK-", "0"), 0),
        export_mask=_try_int(values.get("-EXPORTMASK-", "0"), 0),
        tag=values.get("-TAG-", "ui_live"),
        working_dir=values.get("-OUTPUT-DIR-", ""),
        save_snapshot=0,
        snapshot_dir=values.get("-SNAPROOT-", ""),
        override_cfg=override,
    )

    return DciRunnerRequest(
        platform=1,
        input_file=values.get("-INPUT-", ""),
        output_file="",
        width=width,
        height=height,
        pixel_format=pixel_format,
        input_format=input_format,
        input_colorspace=input_colorspace,
        output_format=output_format,
        output_colorspace=output_colorspace,
        config_path=runtime_config_path or values.get("-CONFIG-", DEFAULT_CONFIG_PATH),
        reg_path="",
        is_src_fullrange=_is_full_range_colorspace(input_colorspace),
        frame_idx=frame_idx,
        frame_num=frame_num,
        debug_dump_mask=dump_mask,
        debug_path=values.get("-OUTPUT-DIR-", ""),
        audit=audit,
    )


def _try_int(val: str, default: int) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _try_float(val: str, default: float) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _parse_format_display(display_value: str, default_value: int) -> int:
    """Parse one CSC format combo display string into an integer code."""
    try:
        return int(display_value.split(" - ", 1)[0], 16)
    except (AttributeError, ValueError, IndexError):
        return default_value


def _parse_colorspace_display(display_value: str, default_value: int) -> int:
    """Parse one CSC colorspace combo display string into an integer code."""
    try:
        return int(display_value.split(" - ", 1)[0])
    except (AttributeError, ValueError, IndexError):
        return default_value


def _is_full_range_colorspace(colorspace: int) -> int:
    """Convert one CSC colorspace code into the runner full-range flag."""
    return 1 if colorspace in (1, 3, 5, 7) else 0


def _try_bool(values: dict, key: str) -> int:
    """Convert a checkbox value into a runner-friendly integer flag."""
    return 1 if values.get(key) else 0


def _get_shp_int(values: dict, key: str, default: int) -> int:
    """Read one SHP integer field from the UI."""
    return _try_int(values.get(key, str(default)), default)


def _fill_list_values(data: list, value: int) -> list:
    """Return a same-length list filled with one scalar value."""
    return [value for _ in data]


def _resolve_sharp_config_section(config_data: dict) -> dict:
    """Resolve the sharp config section from a full PQ config tree."""
    if "pq_tuning_param" in config_data:
        return config_data["pq_tuning_param"]["SHARPNESS"]
    if "pq_param" in config_data:
        return config_data["pq_param"]["sharp"]
    if "sharp" in config_data:
        return config_data["sharp"]
    return config_data


def _resolve_dci_config_section(config_data: dict) -> dict:
    """Resolve the DCI config section from a full PQ config tree."""
    if "pq_tuning_param" in config_data:
        dci_data = config_data["pq_tuning_param"].get("dci", {})
        if "s_vop_dci_interp_params" in dci_data:
            return dci_data["s_vop_dci_interp_params"]
        return dci_data
    if "dci" in config_data:
        dci_data = config_data["dci"]
        if "s_vop_dci_interp_params" in dci_data:
            return dci_data["s_vop_dci_interp_params"]
        return dci_data
    if "s_vop_dci_interp_params" in config_data:
        return config_data["s_vop_dci_interp_params"]
    return config_data


def _load_dci_values_from_config(config_path: str) -> dict:
    """Load DCI values from the selected source config."""
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    dci_data = _resolve_dci_config_section(config_data)

    try:
        ctrl_data = dci_data["s_vop_dci_ctrl"]
        bs_data = dci_data["s_bs_params"]
        ws_data = dci_data["s_ws_params"]
        clahe_data = dci_data["s_clahe_params"]

        return {
            "-CFHE-": ctrl_data["i_dci_CF_HE_ratio"],
            "-BS-": bs_data["i_dci_BS_set_point"],
            "-WS-": ws_data["i_dci_WS_set_point"],
            "-CLAHE-R-": clahe_data["i_dci_CLAHE_LocalRatio"],
            "-CLAHE-C-": round(float(clahe_data["i_dci_CLAHE_clip_value"]), 1),
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid dci config structure: {exc}") from exc


def _load_shp_values_from_config(config_path: str) -> dict:
    """Load SHP values from the selected source config."""
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    sharp_data = _resolve_sharp_config_section(config_data)

    try:
        return {
            "-SHP-ENABLE-": bool(sharp_data["i_EnabledSharpen"]),
            "-SHP-PEAKING-GAIN-": str(sharp_data["s_peaking"]["i_peakingGain"]),
            "-SHP-CORING-ENABLE-": bool(
                sharp_data["s_sharp_en_ctrl"]["i_peaking_coring_en"]
            ),
            "-SHP-SHOOT-ENABLE-": bool(
                sharp_data["s_sharp_en_ctrl"]["i_shoot_ctrl_en"]
            ),
            "-SHP-CORING-THRESHOLD-": str(
                sharp_data["s_peaking"]["s_coring"]["t_CoringThreshold"][0]
            ),
            "-SHP-SHOOT-OVER-": str(
                sharp_data["s_peaking"]["s_shootAdj"]["t_ShootAdjAlphaOver"][0]
            ),
            "-SHP-SHOOT-UNDER-": str(
                sharp_data["s_peaking"]["s_shootAdj"]["t_ShootAdjAlphaUnder"][0]
            ),
        }
    except (IndexError, KeyError, TypeError) as exc:
        raise ValueError(f"Invalid sharp config structure: {exc}") from exc


def _update_shp_fields_from_config(config_path: str, window: sg.Window):
    """Populate SHP UI fields from the selected source config."""
    if not config_path or not os.path.isfile(config_path):
        return

    shp_values = _load_shp_values_from_config(config_path)
    for key, value in shp_values.items():
        window[key].update(value=value)
    _set_numeric_control_value(
        window, "-SHP-PEAKING-GAIN-", "-SHP-PEAKING-GAIN-SLIDER-",
        _try_int(shp_values.get("-SHP-PEAKING-GAIN-", "160"), 160)
    )
    _set_numeric_control_value(
        window, "-SHP-CORING-THRESHOLD-", "-SHP-CORING-THRESHOLD-SLIDER-",
        _try_int(shp_values.get("-SHP-CORING-THRESHOLD-", "0"), 0)
    )
    _set_numeric_control_value(
        window, "-SHP-SHOOT-OVER-", "-SHP-SHOOT-OVER-SLIDER-",
        _try_int(shp_values.get("-SHP-SHOOT-OVER-", "8"), 8)
    )
    _set_numeric_control_value(
        window, "-SHP-SHOOT-UNDER-", "-SHP-SHOOT-UNDER-SLIDER-",
        _try_int(shp_values.get("-SHP-SHOOT-UNDER-", "64"), 64)
    )


def _update_dci_fields_from_config(config_path: str, window: sg.Window):
    """Populate DCI UI fields from the selected source config."""
    if not config_path or not os.path.isfile(config_path):
        return

    dci_values = _load_dci_values_from_config(config_path)
    _set_numeric_control_value(
        window, "-CFHE-", "-CFHE-SLIDER-", _try_int(dci_values.get("-CFHE-", 32), 32)
    )
    _set_numeric_control_value(
        window, "-BS-", "-BS-SLIDER-", _try_int(dci_values.get("-BS-", 80), 80)
    )
    _set_numeric_control_value(
        window, "-WS-", "-WS-SLIDER-", _try_int(dci_values.get("-WS-", 80), 80)
    )
    _set_numeric_control_value(
        window, "-CLAHE-R-", "-CLAHE-R-SLIDER-",
        _try_int(dci_values.get("-CLAHE-R-", 19), 19)
    )
    _set_numeric_control_value(
        window, "-CLAHE-C-", "-CLAHE-C-SLIDER-",
        _try_float(dci_values.get("-CLAHE-C-", 1.0), 1.0)
    )


def _load_config_into_ui(config_path: str, window: sg.Window):
    """Load config-backed UI values from the selected source config."""
    if not config_path or not os.path.isfile(config_path):
        raise ValueError("Config file not found")

    _update_dci_fields_from_config(config_path, window)
    _update_shp_fields_from_config(config_path, window)


def _set_numeric_control_value(
    window: sg.Window,
    spin_key: str,
    slider_key: str,
    value: int | float,
):
    """Update one numeric spinbox and slider pair with the same value."""
    window[spin_key].update(value=value)
    window[slider_key].update(value=value)


def _sync_numeric_control(
    window: sg.Window,
    values: dict,
    event: str,
    spin_key: str,
    slider_key: str,
    parser,
):
    """Synchronize one numeric spinbox and slider pair from the active event."""
    return_event = f"{spin_key}_ENTER"
    try:
        value = parser(
            values.get(spin_key)
            if event in (spin_key, return_event)
            else values.get(slider_key)
        )
    except (TypeError, ValueError):
        return

    if event in (spin_key, return_event):
        window[spin_key].update(value=value)
        window[slider_key].update(value=value)
        window[slider_key].set_focus()
    elif event == slider_key:
        window[spin_key].update(value=value)
        window[slider_key].update(value=value)
        window[slider_key].set_focus()



# Slider keys that support click-to-focus for keyboard arrow control
_SLIDER_KEYS = {
    "-CFHE-SLIDER-", "-BS-SLIDER-", "-WS-SLIDER-",
    "-CLAHE-R-SLIDER-", "-CLAHE-C-SLIDER-",
    "-SHP-PEAKING-GAIN-SLIDER-", "-SHP-CORING-THRESHOLD-SLIDER-",
    "-SHP-SHOOT-OVER-SLIDER-", "-SHP-SHOOT-UNDER-SLIDER-",
}


def _to_slider_float(value) -> float:
    """Convert one slider value into a float with stable single-decimal precision."""
    return round(float(value), 1)


def _bind_control_events(window: sg.Window):
    """Bind Return key on spins and arrow keys on sliders."""
    spin_keys = [
        "-CFHE-", "-BS-", "-WS-", "-CLAHE-R-", "-CLAHE-C-",
        "-SHP-PEAKING-GAIN-", "-SHP-CORING-THRESHOLD-",
        "-SHP-SHOOT-OVER-", "-SHP-SHOOT-UNDER-",
    ]
    for key in spin_keys:
        window[key].bind("<Return>", "_ENTER")

    for key in _SLIDER_KEYS:
        window[key].bind("<Button-1>", "_CLICK")


def _apply_shp_values_to_config(config_data: dict, values: dict) -> dict:
    """Apply SHP UI values to one loaded config JSON tree."""
    sharp_data = _resolve_sharp_config_section(config_data)

    try:
        shp_enable = _try_bool(values, "-SHP-ENABLE-")
        peaking_gain = _get_shp_int(
            values, "-SHP-PEAKING-GAIN-", 160
        )
        coring_enable = _try_bool(values, "-SHP-CORING-ENABLE-")
        shoot_ctrl_enable = _try_bool(values, "-SHP-SHOOT-ENABLE-")

        coring_threshold = _get_shp_int(values, "-SHP-CORING-THRESHOLD-", 0)
        shoot_over = _get_shp_int(values, "-SHP-SHOOT-OVER-", 8)
        shoot_under = _get_shp_int(values, "-SHP-SHOOT-UNDER-", 64)

        coring_list = sharp_data["s_peaking"]["s_coring"]["t_CoringThreshold"]
        over_list = sharp_data["s_peaking"]["s_shootAdj"]["t_ShootAdjAlphaOver"]
        under_list = sharp_data["s_peaking"]["s_shootAdj"]["t_ShootAdjAlphaUnder"]

        if shp_enable != sharp_data["i_EnabledSharpen"]:
            sharp_data["i_EnabledSharpen"] = shp_enable
        if peaking_gain != sharp_data["s_peaking"]["i_peakingGain"]:
            sharp_data["s_peaking"]["i_peakingGain"] = peaking_gain
        if coring_enable != sharp_data["s_sharp_en_ctrl"]["i_peaking_coring_en"]:
            sharp_data["s_sharp_en_ctrl"]["i_peaking_coring_en"] = coring_enable
        if shoot_ctrl_enable != sharp_data["s_sharp_en_ctrl"]["i_shoot_ctrl_en"]:
            sharp_data["s_sharp_en_ctrl"]["i_shoot_ctrl_en"] = shoot_ctrl_enable
        if coring_list and coring_threshold != coring_list[0]:
            sharp_data["s_peaking"]["s_coring"]["t_CoringThreshold"] = _fill_list_values(
                coring_list, coring_threshold
            )
        if over_list and shoot_over != over_list[0]:
            sharp_data["s_peaking"]["s_shootAdj"]["t_ShootAdjAlphaOver"] = _fill_list_values(
                over_list, shoot_over
            )
        if under_list and shoot_under != under_list[0]:
            sharp_data["s_peaking"]["s_shootAdj"]["t_ShootAdjAlphaUnder"] = _fill_list_values(
                under_list, shoot_under
            )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Invalid sharp config structure: {exc}") from exc

    return config_data


def _apply_dci_values_to_config(config_data: dict, values: dict) -> dict:
    """Apply DCI UI values to one loaded config JSON tree when supported."""
    dci_data = _resolve_dci_config_section(config_data)

    try:
        ctrl_data = dci_data["s_vop_dci_ctrl"]
        bs_data = dci_data["s_bs_params"]
        ws_data = dci_data["s_ws_params"]
        clahe_data = dci_data["s_clahe_params"]

        input_colorspace = _parse_colorspace_display(
            values.get("-IN-CLR-", DEFAULT_CLRSPC_DISPLAY), 1
        )
        ctrl_data["i_vopIn_csc_range"] = _is_full_range_colorspace(input_colorspace)
        ctrl_data["i_dci_CF_HE_ratio"] = _try_int(values.get("-CFHE-", "32"), 32)
        bs_data["i_dci_BS_set_point"] = _try_int(values.get("-BS-", "80"), 80)
        ws_data["i_dci_WS_set_point"] = _try_int(values.get("-WS-", "80"), 80)
        clahe_data["i_dci_CLAHE_LocalRatio"] = _try_int(values.get("-CLAHE-R-", "19"), 19)
        clahe_data["i_dci_CLAHE_clip_value"] = _try_float(values.get("-CLAHE-C-", "1.0"), 1.0)
    except (KeyError, TypeError):
        return config_data

    return config_data


def _generate_runtime_config(values: dict, working_dir: str) -> str:
    """Generate one runtime config copy with DCI and SHP values applied."""
    source_config_path = values.get("-CONFIG-", "").strip()
    if not source_config_path or not os.path.isfile(source_config_path):
        raise ValueError("Source config file not found")

    with open(source_config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    runtime_config = _apply_dci_values_to_config(config_data, values)
    runtime_config = _apply_shp_values_to_config(runtime_config, values)
    runtime_config_path = os.path.join(working_dir, "runner_config_runtime.json")
    with open(runtime_config_path, "w", encoding="utf-8") as f:
        json.dump(runtime_config, f, indent=2, ensure_ascii=False)

    return runtime_config_path


def _do_run(values: dict, state: DciUiState, window: sg.Window):
    """Execute a DCI run: build request, launch runner, load results."""
    exe_path = values.get("-EXE-", "").strip()
    if not exe_path or not os.path.isfile(exe_path):
        window["-STATUS-"].update("Runner executable not found", text_color="red")
        return

    working_dir = values.get("-OUTPUT-DIR-", "").strip()
    if not working_dir:
        window["-STATUS-"].update("Output directory is required", text_color="red")
        return

    source_config_path = values.get("-CONFIG-", "").strip()
    if not source_config_path or not os.path.isfile(source_config_path):
        window["-STATUS-"].update("Config file not found", text_color="red")
        return

    os.makedirs(working_dir, exist_ok=True)
    state.request_path = os.path.join(working_dir, "runner_request.json")
    state.result_path = os.path.join(working_dir, "runner_result.json")

    try:
        runtime_config_path = _generate_runtime_config(values, working_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        window["-STATUS-"].update(f"Runtime config failed: {exc}", text_color="red")
        return

    request = _build_request_from_values(values, runtime_config_path=runtime_config_path)
    write_runner_request(request, state.request_path)

    window["-STATUS-"].update("Running native DCI_SHP runner...", text_color="blue")
    window.refresh()

    completed = run_dci_request(exe_path, state.request_path, state.result_path)
    runner_result = load_runner_result(state.result_path)
    state.last_runner_result = runner_result

    if completed.returncode == 0 and runner_result and runner_result.status == "ok":
        window["-STATUS-"].update(
            f"Run completed successfully (exit {completed.returncode})",
            text_color="green",
        )
        _do_refresh(values, state, window)
    else:
        err = runner_result.message if runner_result else completed.stderr or "unknown error"
        window["-STATUS-"].update(
            f"Run failed (exit {completed.returncode}): {err}", text_color="red"
        )


def _do_refresh(values: dict, state: DciUiState, window: sg.Window):
    """Reload the working set and update all data views."""
    working_dir = values.get("-OUTPUT-DIR-", "").strip()
    ready, msg = check_working_set_ready(working_dir)
    if not ready:
        window["-STATUS-"].update(f"Working set not ready: {msg}", text_color="orange")
        return

    state.workspace = load_working_set(working_dir)
    ws = state.workspace
    _refresh_workspace_views(ws, working_dir, window)
    window["-STATUS-"].update("Workspace refreshed", text_color="green")


def _refresh_workspace_views(ws: dict, working_dir: str, window: sg.Window):
    """Update all chart and text views from the loaded workspace."""
    # Previews
    previews = resolve_preview_paths(working_dir, ws.get("manifest", {}))
    if previews.get("input") and os.path.isfile(previews["input"]):
        window["-NATIVE-PREVIEW-"].update(filename=previews["input"])
    if previews.get("output") and os.path.isfile(previews["output"]):
        # Show output preview; input remains separately visible
        pass  # We show it in the "Native Preview" frame

    # Global curve chart
    curves_data = ws.get("curves", {})
    if curves_data:
        series = build_curve_series(curves_data)
        png_bytes = render_curve_figure(series)
        if png_bytes:
            window["-CURVES-"].update(data=png_bytes)

    # Histogram chart
    hists_data = ws.get("hists", {})
    if hists_data:
        png_bytes = render_histogram_figure(hists_data)
        if png_bytes:
            window["-HISTS-"].update(data=png_bytes)

    # Metrics text
    metrics_data = ws.get("metrics", {})
    if metrics_data:
        window["-METRICS-"].update(
            json.dumps(metrics_data, indent=2, ensure_ascii=False)
        )


def _do_save(values: dict, state: DciUiState, window: sg.Window):
    """Save the current config and result as a timestamped snapshot."""
    working_dir = values.get("-OUTPUT-DIR-", "").strip()
    snapshot_root = values.get("-SNAPROOT-", "").strip()
    tag = values.get("-TAG-", "").strip() or "dci_case"

    if not working_dir or not os.path.isdir(working_dir):
        window["-STATUS-"].update("Output directory not ready", text_color="red")
        return

    if not snapshot_root:
        snapshot_root = os.path.join(os.path.dirname(working_dir), "dci_snapshots")

    os.makedirs(snapshot_root, exist_ok=True)

    request_path = state.request_path or os.path.join(working_dir, "runner_request.json")
    result_path = state.result_path or os.path.join(working_dir, "runner_result.json")

    try:
        dst_dir = save_snapshot(
            working_dir=working_dir,
            request_path=request_path,
            result_path=result_path,
            snapshot_root=snapshot_root,
            snapshot_name=tag,
        )
        window["-STATUS-"].update(
            f"Snapshot saved to {dst_dir}", text_color="green"
        )
        sg.popup(f"Snapshot saved to:\n{dst_dir}", title="Save Config & Result")
    except Exception as e:
        window["-STATUS-"].update(f"Snapshot failed: {e}", text_color="red")


def _do_open_dir(values: dict, window: sg.Window):
    """Open the output directory in Windows Explorer."""
    working_dir = values.get("-OUTPUT-DIR-", "").strip()
    if working_dir and os.path.isdir(working_dir):
        os.startfile(working_dir)
    else:
        window["-STATUS-"].update("Output directory not found", text_color="orange")


# ------------------------------------------------------------------ #
# Entry point                                                        #
# ------------------------------------------------------------------ #


def main():
    sg.theme("SystemDefault")
    layout = _build_main_layout()

    window = sg.Window(
        "DCI_SHP Runner",
        layout,
        resizable=True,
        finalize=True,
    )

    state = DciUiState()
    state.exe_path = _find_default_runner()

    # Pre-fill runner path if found
    if state.exe_path:
        window["-EXE-"].update(state.exe_path)
    _bind_control_events(window)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        elif event == "-RUN-":
            _do_run(values, state, window)

        elif event == "-LOAD-CONFIG-":
            try:
                _load_config_into_ui(values.get("-CONFIG-", "").strip(), window)
                window["-STATUS-"].update("Config loaded", text_color="green")
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                window["-STATUS-"].update(
                    f"Failed to load config: {exc}", text_color="orange"
                )

        elif event == "-REFRESH-":
            _do_refresh(values, state, window)

        elif event == "-SAVE-":
            _do_save(values, state, window)

        elif event == "-OPEN-DIR-":
            _do_open_dir(values, window)

        elif event == "-OPEN-SNAPROOT-":
            snaproot = values.get("-SNAPROOT-", "").strip()
            if snaproot and os.path.isdir(snaproot):
                os.startfile(snaproot)
            else:
                window["-STATUS-"].update("Snapshot root not found", text_color="orange")

        elif event == "-IN-FMT-":
            _update_clrspc_for_fmt(window, values, "-IN-CLR-", values["-IN-FMT-"])
            _show_native_raw_preview(window, values)

        elif event == "-OUT-FMT-":
            _update_clrspc_for_fmt(window, values, "-OUT-CLR-", values["-OUT-FMT-"])

        elif event == "-INPUT-":
            input_file = values.get("-INPUT-", "").strip()
            if input_file and os.path.isfile(input_file):
                basename = os.path.basename(input_file).lower()
                ext = os.path.splitext(basename)[1]
                # Guess format by extension
                if ext == ".yuv":
                    yuv_fmt = next((f for f in FMT_DISPLAY if f.startswith("0x9 ")), None)
                    if yuv_fmt:
                        window["-IN-FMT-"].update(value=yuv_fmt)
                        values["-IN-FMT-"] = yuv_fmt
                        _update_clrspc_for_fmt(window, values, "-IN-CLR-", yuv_fmt)
                elif ext == ".rgb":
                    rgb_fmt = next((f for f in FMT_DISPLAY if f.startswith("0x0 ")), None)
                    if rgb_fmt:
                        window["-IN-FMT-"].update(value=rgb_fmt)
                        values["-IN-FMT-"] = rgb_fmt
                        _update_clrspc_for_fmt(window, values, "-IN-CLR-", rgb_fmt)
                # Guess resolution from filename
                m_res = re.search(r"(\d+)x(\d+)", basename)
                if m_res:
                    window["-WIDTH-"].update(value=m_res.group(1))
                    values["-WIDTH-"] = m_res.group(1)
                    window["-HEIGHT-"].update(value=m_res.group(2))
                    values["-HEIGHT-"] = m_res.group(2)
                _show_native_raw_preview(window, values)

        elif event in ("-CFHE-", "-CFHE-SLIDER-", "-CFHE-_ENTER"):
            _sync_numeric_control(window, values, event, "-CFHE-", "-CFHE-SLIDER-", int)

        elif event in ("-BS-", "-BS-SLIDER-", "-BS-_ENTER"):
            _sync_numeric_control(window, values, event, "-BS-", "-BS-SLIDER-", int)

        elif event in ("-WS-", "-WS-SLIDER-", "-WS-_ENTER"):
            _sync_numeric_control(window, values, event, "-WS-", "-WS-SLIDER-", int)

        elif event in ("-CLAHE-R-", "-CLAHE-R-SLIDER-", "-CLAHE-R-_ENTER"):
            _sync_numeric_control(window, values, event, "-CLAHE-R-", "-CLAHE-R-SLIDER-", int)

        elif event in ("-CLAHE-C-", "-CLAHE-C-SLIDER-", "-CLAHE-C-_ENTER"):
            _sync_numeric_control(
                window, values, event, "-CLAHE-C-", "-CLAHE-C-SLIDER-", _to_slider_float
            )

        elif event in (
            "-SHP-PEAKING-GAIN-",
            "-SHP-PEAKING-GAIN-SLIDER-",
            "-SHP-PEAKING-GAIN-_ENTER",
        ):
            _sync_numeric_control(
                window,
                values,
                event,
                "-SHP-PEAKING-GAIN-",
                "-SHP-PEAKING-GAIN-SLIDER-",
                int,
            )

        elif event in (
            "-SHP-CORING-THRESHOLD-",
            "-SHP-CORING-THRESHOLD-SLIDER-",
            "-SHP-CORING-THRESHOLD-_ENTER",
        ):
            _sync_numeric_control(
                window,
                values,
                event,
                "-SHP-CORING-THRESHOLD-",
                "-SHP-CORING-THRESHOLD-SLIDER-",
                int,
            )

        elif event in (
            "-SHP-SHOOT-OVER-",
            "-SHP-SHOOT-OVER-SLIDER-",
            "-SHP-SHOOT-OVER-_ENTER",
        ):
            _sync_numeric_control(
                window,
                values,
                event,
                "-SHP-SHOOT-OVER-",
                "-SHP-SHOOT-OVER-SLIDER-",
                int,
            )

        elif event in (
            "-SHP-SHOOT-UNDER-",
            "-SHP-SHOOT-UNDER-SLIDER-",
            "-SHP-SHOOT-UNDER-_ENTER",
        ):
            _sync_numeric_control(
                window,
                values,
                event,
                "-SHP-SHOOT-UNDER-",
                "-SHP-SHOOT-UNDER-SLIDER-",
                int,
            )

        elif event.endswith("_CLICK"):
            # Set focus on slider when clicked so arrow keys work
            slider_key = event[: -len("_CLICK")]
            if slider_key in _SLIDER_KEYS:
                window[slider_key].set_focus()

    window.close()


def _find_default_runner() -> str:
    """Try to locate dci_verify_runner.exe near the project output directory."""
    candidates = [
        os.path.join(
            os.path.dirname(__file__), "..", "..", "output", "bin",
            "dci_verify_runner.exe",
        ),
        os.path.join(
            os.path.dirname(__file__), "..", "..", "project", "build_win32_Release",
            "src", "dci", "dci_verify_runner.exe",
        ),
        os.path.join(
            os.path.dirname(__file__), "..", "..", "project", "build_win32_Debug",
            "src", "dci", "dci_verify_runner.exe",
        ),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return os.path.abspath(p)
    return ""


if __name__ == "__main__":
    main()

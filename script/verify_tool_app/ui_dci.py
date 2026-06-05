"""
DCI module tab for PQ Test Tool.

Provides DCI audit controls (CF/HE ratio, BS/WS set points, CLAHE).
Processing is done via external dci_runner executable.
Right preview supports LUT-based median curve visualization from curves.json.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import PySimpleGUI as sg

from csc.run_csc import read_raw_to_planar, write_planar_to_raw
from dci.dci_models import (
    DciAuditConfig,
    DciAuditOverride,
    DciRunnerRequest,
    write_runner_request,
)
from dci.dci_runner import load_runner_result

TAB_LABEL = "DCI"

# ------------------------------------------------------------------ #
# DCI LUT constants (matches rkpq_dci_hw.h)                          #
# ------------------------------------------------------------------ #

DCI_GLOBAL_HIST_BIT = 10       # RKVOP_PQ_DCI_GLOBAL_HIST_BIT
DCI_LOCAL_HIST_BIT = 4         # RKVOP_PQ_DCI_LOCAL_HIST_BIT
DCI_LOCAL_HIST_CNT = 16        # entries per block LUT
DCI_GLOBAL_HIST_CNT = 1024     # (1 << 10)
DCI_MAX_LUMA = 1023
DCI_BLOCK_GRID = 16            # 16x16 spatial grid

# Curves cache: {audit_dir_path: curves_dict}
_CURVES_CACHE: dict[str, dict] = {}

# Project root for resolving relative paths
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_exe_path(path: str) -> str:
    """Resolve a relative path against project root. Returns absolute path."""
    if not path:
        return ""
    p = Path(path)
    if p.is_absolute():
        return str(p)
    return str((_PROJECT_ROOT / p).resolve())


def _get_default_exe_path() -> str:
    """Get the default DCI EXE path resolved against project root."""
    return _resolve_exe_path("output\\bin\\dci_verify_demo.exe")


# ------------------------------------------------------------------ #
# Curves loading                                                      #
# ------------------------------------------------------------------ #

COMBO_TO_CURVE_KEY = {
    "Global_CF": "g_cf",
    "Global_HE": "g_he",
    "Global_CF_HE": "g_cf_he",
    "Global_BWS": "g_bws",
    "Global_All": "global_lut",
    "Local_CLAHE": "local_lut",
}


def _load_curves(audit_dir: str) -> dict | None:
    """Load and cache curves.json from the audit directory. Returns curves dict or None."""
    if not audit_dir or not os.path.isdir(audit_dir):
        return None
    if audit_dir in _CURVES_CACHE:
        return _CURVES_CACHE[audit_dir]
    curves_path = os.path.join(audit_dir, "curves", "curves.json")
    if not os.path.isfile(curves_path):
        return None
    try:
        with open(curves_path, "r", encoding="utf-8") as f:
            curves = json.load(f)
        _CURVES_CACHE[audit_dir] = curves
        return curves
    except Exception:
        return None


# ------------------------------------------------------------------ #
# LUT apply logic                                                     #
# ------------------------------------------------------------------ #


def _apply_1d_lut(input_data: np.ndarray, lut: list, in_depth: int) -> np.ndarray:
    """Apply a 1D LUT to the Y channel of a planar image.

    Args:
        input_data: (3, H, W) planar array, only Y channel is mapped.
        lut: 1D LUT list (1024 or 1025 entries for 10-bit).
        in_depth: Input bit depth (8 or 10).

    Returns:
        (3, H, W) planar array with mapped Y channel.
    """
    output = input_data.copy()
    y_channel = output[0]
    lut_arr = np.array(lut, dtype=np.uint16)

    if in_depth == 10:
        # One-to-one: 10-bit input → 10-bit LUT
        y_clipped = np.clip(y_channel, 0, len(lut) - 1)
        output[0] = lut_arr[y_clipped].astype(y_channel.dtype)
    else:
        # 8-bit input: every 4th value in the LUT, output back to 8-bit
        lut_idx = np.clip(y_channel.astype(np.int32) * 4, 0, len(lut) - 1)
        mapped_10bit = lut_arr[lut_idx]
        output[0] = (mapped_10bit >> 2).astype(np.uint8)

    return output


def _apply_local_lut(input_data: np.ndarray, local_lut: list, in_depth: int) -> np.ndarray:
    """Apply local CLAHE LUT (16x16 blocks, 16 entries each) with spatial bilinear interpolation.

    Args:
        input_data: (3, H, W) planar array.
        local_lut: Flat list of 16*16*16 = 4096 values (u10).
        in_depth: Input bit depth (8 or 10).

    Returns:
        (3, H, W) planar array with mapped Y channel.
    """
    output = input_data.copy()
    y_channel = output[0]
    h, w = y_channel.shape

    # Reshape to (16, 16, 16) -> (v_idx, h_idx, lut_entry)
    lut_3d = np.array(local_lut, dtype=np.uint16).reshape(
        DCI_BLOCK_GRID, DCI_BLOCK_GRID, DCI_LOCAL_HIST_CNT
    )  # (16, 16, 16)

    # Build 2D block index array (H, W)
    blk_h = max(h / DCI_BLOCK_GRID, 1)
    blk_w = max(w / DCI_BLOCK_GRID, 1)

    y_idx = np.arange(h)
    x_idx = np.arange(w)

    # Per-pixel block indices and offsets
    v_idx0 = np.floor(y_idx[:, None] / blk_h).astype(np.int32)
    offset_v = y_idx[:, None] - v_idx0 * blk_h
    h_idx0 = np.floor(x_idx[None, :] / blk_w).astype(np.int32)
    offset_h = x_idx[None, :] - h_idx0 * blk_w

    v_idx1 = np.minimum(v_idx0 + 1, DCI_BLOCK_GRID - 1)
    h_idx1 = np.minimum(h_idx0 + 1, DCI_BLOCK_GRID - 1)

    # Bilinear weights (normalized to [0, 1])
    denom = (blk_h * blk_w) if (blk_h * blk_w) > 0 else 1
    wx0_val = (blk_w - offset_h) / denom
    wx1_val = offset_h / denom
    wy0_val = blk_h - offset_v
    wy1_val = offset_v

    w00 = (wx0_val * wy0_val).astype(np.float64)
    w10 = (wx0_val * wy1_val).astype(np.float64)
    w01 = (wx1_val * wy0_val).astype(np.float64)
    w11 = (wx1_val * wy1_val).astype(np.float64)

    if in_depth == 10:
        y = y_channel.astype(np.int32)
    else:
        y = (y_channel.astype(np.int32) << 2)  # upscale 8-bit to 10-bit equivalent

    y_clamped = np.clip(y, 0, DCI_MAX_LUMA)
    idx_loc = y_clamped >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT)  # >> 6, range [0, 15]
    wgt1_loc = y_clamped - (idx_loc << (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT))  # [0, 63]
    wgt0_loc = (1 << (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT)) - wgt1_loc  # 64 - wgt1

    # Look up 4 corner-block values using (v_idx, h_idx, idx_loc)
    lu_val0 = lut_3d[v_idx0[:, :], h_idx0[:, :], np.maximum(idx_loc - 1, 0)]
    lu_val1 = lut_3d[v_idx0[:, :], h_idx0[:, :], idx_loc]
    ru_val0 = lut_3d[v_idx0[:, :], h_idx1[:, :], np.maximum(idx_loc - 1, 0)]
    ru_val1 = lut_3d[v_idx0[:, :], h_idx1[:, :], idx_loc]
    lb_val0 = lut_3d[v_idx1[:, :], h_idx0[:, :], np.maximum(idx_loc - 1, 0)]
    lb_val1 = lut_3d[v_idx1[:, :], h_idx0[:, :], idx_loc]
    rb_val0 = lut_3d[v_idx1[:, :], h_idx1[:, :], np.maximum(idx_loc - 1, 0)]
    rb_val1 = lut_3d[v_idx1[:, :], h_idx1[:, :], idx_loc]

    # Per-block LUT interpolation (idx_loc == 0 uses value0=0)
    mask_zero = (idx_loc == 0)
    half_val = (1 << (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT - 1))  # 32

    lu = np.where(mask_zero,
                  (lu_val1 * wgt1_loc + half_val) >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT),
                  (lu_val0 * wgt0_loc + lu_val1 * wgt1_loc + half_val) >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT))
    ru = np.where(mask_zero,
                  (ru_val1 * wgt1_loc + half_val) >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT),
                  (ru_val0 * wgt0_loc + ru_val1 * wgt1_loc + half_val) >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT))
    lb = np.where(mask_zero,
                  (lb_val1 * wgt1_loc + half_val) >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT),
                  (lb_val0 * wgt0_loc + lb_val1 * wgt1_loc + half_val) >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT))
    rb = np.where(mask_zero,
                  (rb_val1 * wgt1_loc + half_val) >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT),
                  (rb_val0 * wgt0_loc + rb_val1 * wgt1_loc + half_val) >> (DCI_GLOBAL_HIST_BIT - DCI_LOCAL_HIST_BIT))

    # Spatial bilinear blend
    result = (w00 * lu + w10 * lb + w01 * ru + w11 * rb).astype(np.uint16)
    result = np.clip(result, 0, DCI_MAX_LUMA)

    if in_depth == 10:
        output[0] = result.astype(y_channel.dtype)
    else:
        output[0] = (result >> 2).astype(np.uint8)

    return output


# ------------------------------------------------------------------ #
# Layout                                                             #
# ------------------------------------------------------------------ #

def _build_numeric_control_row(
    label: str,
    spin_key: str,
    slider_key: str,
    default_value,
    min_value,
    max_value,
    resolution: float = 1.0,
    label_size: tuple = (22, 1),
) -> list:
    """Build a synchronized spinbox + slider + reset button control row."""
    steps = int(round((max_value - min_value) / resolution))
    spin_values = [
        round(min_value + i * resolution, 1 if resolution < 1 else 0)
        for i in range(steps + 1)
    ]
    if resolution >= 1:
        spin_values = [int(v) for v in spin_values]

    reset_key = f"{slider_key}-RESET-"

    return [
        sg.Text(label, size=label_size),
        sg.Slider(
            range=(min_value, max_value),
            default_value=default_value,
            resolution=resolution,
            orientation="h",
            size=(24, 15),
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
        sg.Button("Reset", key=reset_key, size=(6, 1)),
    ]


def build_controls() -> list:
    """Build the DCI Config tab layout."""
    default_exe = _get_default_exe_path()
    return [
        [
            sg.Text("DCI EXE", size=(10, 1)),
            sg.Input(default_exe, key="-DCI-EXE-", size=(46, 1)),
            sg.FileBrowse(
                file_types=(("Executable", "*.exe"),),
                target="-DCI-EXE-",
                size=(8, 1),
            ),
            sg.Button("Open Dir", key="-DCI-OPEN-EXE-DIR-", size=(8, 1)),
        ],
        [
            sg.Text("DCI Audit Dir", size=(10, 1)),
            sg.Input("D:\\RkDefaultDumpData\\dci_audit_smoke", key="-DCI-AUDIT-DIR-", size=(46, 1)),
            sg.FolderBrowse(target="-DCI-AUDIT-DIR-", size=(8, 1)),
            sg.Button("Open Dir", key="-DCI-OPEN-AUDIT-DIR-", size=(8, 1)),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Checkbox("Enable Audit", default=False, key="-AUDIT-ENABLE-"),
            sg.Text("Tag", size=(4, 1)),
            sg.Input("ui_live", size=(20, 1), key="-TAG-"),
            sg.Text("Show Median Result", size=(14, 1)),
            sg.Combo(
                ["None", "Global_CF", "Global_HE", "Global_CF_HE", "Global_BWS", "Global_All", "Local_CLAHE"],
                default_value="None",
                key="-DCI-COMBO-MEDIAN-",
                readonly=True,
                size=(12, 1),
                enable_events=True,
            ),
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
        _build_numeric_control_row("CF/HE Ratio", "-CFHE-", "-CFHE-SLIDER-", 32, 0, 64),
        _build_numeric_control_row("BS Set Point", "-BS-", "-BS-SLIDER-", 80, 0, 255),
        _build_numeric_control_row("WS Set Point", "-WS-", "-WS-SLIDER-", 80, 0, 255),
        _build_numeric_control_row("CLAHE Local Ratio", "-CLAHE-R-", "-CLAHE-R-SLIDER-", 19, 0, 32),
        _build_numeric_control_row("CLAHE Clip Value", "-CLAHE-C-", "-CLAHE-C-SLIDER-", 1.0, 0.0, 8.0, resolution=0.1),
    ]


# ------------------------------------------------------------------ #
# Event handling                                                     #
# ------------------------------------------------------------------ #

DCI_SLIDER_KEYS = [
    ("-CFHE-", "-CFHE-SLIDER-"),
    ("-BS-", "-BS-SLIDER-"),
    ("-WS-", "-WS-SLIDER-"),
    ("-CLAHE-R-", "-CLAHE-R-SLIDER-"),
    ("-CLAHE-C-", "-CLAHE-C-SLIDER-"),
]

# Default values for reset
DCI_SLIDER_DEFAULTS = {
    "-CFHE-SLIDER-": 32,
    "-BS-SLIDER-": 80,
    "-WS-SLIDER-": 80,
    "-CLAHE-R-SLIDER-": 19,
    "-CLAHE-C-SLIDER-": 1.0,
}

DCI_SPIN_DEFAULTS = {
    "-CFHE-": 32,
    "-BS-": 80,
    "-WS-": 80,
    "-CLAHE-R-": 19,
    "-CLAHE-C-": 1.0,
}


def handle_dci_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle DCI-specific events. Returns True if consumed."""
    # Slider/spin sync
    for spin_key, slider_key in DCI_SLIDER_KEYS:
        if event == slider_key:
            _sync_slider_to_spin(window, values, spin_key, slider_key)
            return True
        if event == spin_key:
            _sync_spin_to_slider(window, values, spin_key, slider_key)
            return True

    # Reset buttons
    if event.endswith("-RESET-"):
        slider_key = event.replace("-RESET-", "")
        _reset_numeric_control(window, slider_key)
        return True

    # Open Dir buttons
    if event in ("-DCI-OPEN-EXE-DIR-", "-DCI-OPEN-AUDIT-DIR-"):
        _open_dci_dir(values, event, window)
        return True

    # Audit dir changed → preload curves
    if event in ("-DCI-AUDIT-DIR-",):
        _preload_curves_on_dir_change(values, window)
        return True

    # COMBO MEDIAN change → invalidate right preview
    if event == "-DCI-COMBO-MEDIAN-":
        return True

    return False


def _sync_slider_to_spin(window: sg.Window, values: dict,
                         spin_key: str, slider_key: str):
    """When slider is dragged, update spin to match."""
    value = values[slider_key]
    window[spin_key].update(value=value)


def _sync_spin_to_slider(window: sg.Window, values: dict,
                          spin_key: str, slider_key: str):
    """When spin is changed (typed + enter, or arrows), update slider to match."""
    try:
        value = float(values[spin_key])
    except (ValueError, TypeError):
        return
    window[slider_key].update(value=value)
    window[spin_key].update(value=value)


def _reset_numeric_control(window: sg.Window, slider_key: str):
    """Reset a slider to its default value."""
    default_val = DCI_SLIDER_DEFAULTS.get(slider_key)
    if default_val is not None:
        window[slider_key].update(value=default_val)
        # Also update associated spin
        for spin_key, s_key in DCI_SLIDER_KEYS:
            if s_key == slider_key:
                window[spin_key].update(value=default_val)
                break


def _open_dci_dir(values: dict, event: str, window: sg.Window):
    """Open the folder containing the DCI EXE or Audit Dir path."""
    key_map = {
        "-DCI-OPEN-EXE-DIR-": "-DCI-EXE-",
        "-DCI-OPEN-AUDIT-DIR-": "-DCI-AUDIT-DIR-",
    }
    target_key = key_map.get(event)
    if target_key is None:
        return
    path = values.get(target_key, "").strip()
    if not path:
        return
    # Resolve relative paths for EXE
    if target_key == "-DCI-EXE-" and not os.path.isabs(path):
        path = _resolve_exe_path(path)
    target = os.path.dirname(path) if os.path.isfile(path) else path
    if os.path.isdir(target):
        try:
            os.startfile(target)
        except Exception:
            pass
    elif os.path.isfile(path):
        dirpath = os.path.dirname(path)
        if os.path.isdir(dirpath):
            try:
                os.startfile(dirpath)
            except Exception:
                pass


def _preload_curves_on_dir_change(values: dict, window: sg.Window):
    """Preload curves.json when audit dir changes. Show status."""
    audit_dir = values.get("-DCI-AUDIT-DIR-", "").strip()
    if not audit_dir:
        return
    curves = _load_curves(audit_dir)
    if curves is not None:
        keys_found = [k for k in ["g_cf", "g_he", "g_cf_he", "g_bws", "global_lut", "local_lut"] if k in curves]
        screen_text = f"curves.json loaded: {', '.join(keys_found)}"
        try:
            window.TKroot.title(f"PQ Verify Tool - {screen_text}")
        except Exception:
            pass


# ------------------------------------------------------------------ #
# Module protocol                                                    #
# ------------------------------------------------------------------ #

def read_params(values: dict) -> dict:
    """Extract DCI module parameters from window values."""
    return {
        "audit_enable": values.get("-AUDIT-ENABLE-", False),
        "tag": values.get("-TAG-", "ui_live"),
        "nodemask": values.get("-NODEMASK-", "0"),
        "exportmask": values.get("-EXPORTMASK-", "0"),
        "dumpmask": values.get("-DUMPMASK-", "0"),
        "cfhe_ratio": int(float(values.get("-CFHE-", "32"))),
        "bs_set_point": int(float(values.get("-BS-", "80"))),
        "ws_set_point": int(float(values.get("-WS-", "80"))),
        "clahe_local_ratio": int(float(values.get("-CLAHE-R-", "19"))),
        "clahe_clip_value": float(values.get("-CLAHE-C-", "1.0")),
        "combo_median": values.get("-DCI-COMBO-MEDIAN-", "None"),
        "audit_dir": values.get("-DCI-AUDIT-DIR-", ""),
    }


def process(input_data: np.ndarray, input_fmt: int, input_clrspc: int,
            output_fmt: int, output_clrspc: int, params: dict,
            io_params: dict):
    """Run DCI processing via external dci_runner exe."""
    try:
        exe_path = io_params.get("exe_path", "")
        config_path = io_params.get("config_path", "")
        output_dir = io_params.get("output_dir", tempfile.gettempdir())
        width = io_params.get("width", 1920)
        height = io_params.get("height", 1080)

        # Resolve relative exe path
        exe_path = _resolve_exe_path(exe_path)

        if not exe_path or not os.path.isfile(exe_path):
            return False, "DCI runner exe not found", input_fmt, input_clrspc

        # Write input data to temp raw file
        input_tmp = os.path.join(tempfile.gettempdir(), "_dci_input.raw")
        write_planar_to_raw(input_data, input_tmp, width, height, input_fmt)

        # Write output to output_dir
        output_file = os.path.join(output_dir, "dci_output.raw")
        request_path = os.path.join(output_dir, "_dci_request.json")
        result_path = os.path.join(output_dir, "_dci_result.json")

        # Build request
        request = DciRunnerRequest(
            input_file=input_tmp,
            output_file=output_file,
            width=width,
            height=height,
            pixel_format=input_fmt,
            input_format=input_fmt,
            input_colorspace=input_clrspc,
            output_format=output_fmt,
            output_colorspace=output_clrspc,
            config_path=config_path,
            frame_idx=io_params.get("frame_idx", 0),
            frame_num=io_params.get("frame_num", 1),
            debug_dump_mask=int(float(params.get("dumpmask", "0"))),
            audit=DciAuditConfig(
                enable=1 if params.get("audit_enable") else 0,
                node_mask=int(float(params.get("nodemask", "0"))),
                export_mask=int(float(params.get("exportmask", "0"))),
                tag=params.get("tag", "ui_live"),
                override_cfg=DciAuditOverride(
                    enable_cf_he_ratio_override=1,
                    cf_he_ratio=params.get("cfhe_ratio", 32),
                    enable_bs_set_point_override=1,
                    bs_set_point=params.get("bs_set_point", 80),
                    enable_ws_set_point_override=1,
                    ws_set_point=params.get("ws_set_point", 80),
                    enable_clahe_local_ratio_override=1,
                    clahe_local_ratio=params.get("clahe_local_ratio", 19),
                    enable_clahe_clip_value_override=1,
                    clahe_clip_value=params.get("clahe_clip_value", 1.0),
                ),
            ),
        )
        write_runner_request(request, request_path)

        # Run the DCI executable
        result = subprocess.run(
            [exe_path, "--request", request_path, "--result", result_path],
            check=False, capture_output=True, text=True, timeout=120,
        )
        runner_result = load_runner_result(result_path)

        if runner_result is None or runner_result.exit_code != 0:
            msg = runner_result.message if runner_result else result.stderr[:200]
            return False, f"DCI runner failed: {msg}", input_fmt, input_clrspc

        # Read back output
        output_data = read_raw_to_planar(output_file, width, height, output_fmt)
        return True, output_data, output_fmt, output_clrspc

    except subprocess.TimeoutExpired:
        return False, "DCI runner timeout", input_fmt, input_clrspc
    except Exception as e:
        return False, str(e), input_fmt, input_clrspc


def get_right_preview_image(snapshot, params: dict):
    """Generate right-side DCI median LUT preview data.

    Args:
        snapshot: (data, fmt, clrspc) tuple from pipeline.
        params: DCI module parameters (includes combo_median, audit_dir).

    Returns:
        (mapped_planar, fmt) tuple or None if median is "None" or no data.
        The caller converts to PIL Image for display.
    """
    combo_median = params.get("combo_median", "None")
    if combo_median == "None":
        return None

    curve_key = COMBO_TO_CURVE_KEY.get(combo_median)
    if curve_key is None:
        return None

    audit_dir = params.get("audit_dir", "").strip()
    curves = _load_curves(audit_dir)
    if curves is None:
        return None

    lut_data = curves.get(curve_key)
    if lut_data is None or not isinstance(lut_data, list) or len(lut_data) < 16:
        return None

    if snapshot is None:
        return None

    data, fmt, _ = snapshot
    from csc.run_csc import get_pixel_depth
    in_depth = get_pixel_depth(fmt)

    if combo_median == "Local_CLAHE":
        mapped = _apply_local_lut(data, lut_data, in_depth)
    else:
        mapped = _apply_1d_lut(data, lut_data, in_depth)

    return (mapped, fmt)

"""
DCI module tab for PQ Test Tool.

Provides DCI audit controls (CF/HE ratio, BS/WS set points, CLAHE).
Processing is done via external dci_runner executable.
Right preview supports LUT-based median curve visualization from curves.json.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from collections import defaultdict

# Ensure the parent script/ package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import PySimpleGUI as sg

from csc.run_csc import read_raw_to_planar
from verify_tool_app.ui_helpers import (
    SliderSpinConfig,
    bind_keyboard_events as _bind_kb_shared,
    build_numeric_control_row,
    handle_keyboard_event,
    sync_slider_to_spin,
    sync_spin_to_slider,
)
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

# DCI Support image formats
DCI_SUPPORT_IO_FORMATS = defaultdict(list, {
    0x13: [0x13],
    0x14: [0x14],
    0x16: [0x16],
    0x17: [0x17],
    0x18: [0x18],
    0x19: [0x19],
    0x1A: [0x1A],
})

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


def build_controls() -> list:
    """Build the DCI Config tab layout."""
    default_exe = _get_default_exe_path()
    return [
        [
            sg.Text("DCI EXE", size=(10, 1)),
            sg.Input(default_exe, key="-DCI-EXE-", size=(46, 1),
                     tooltip="DCI硬件模块可执行文件路径"),
            sg.FileBrowse(
                file_types=(("Executable", "*.exe"),),
                target="-DCI-EXE-",
                size=(8, 1),
            ),
            sg.Button("Open Dir", key="-DCI-OPEN-EXE-DIR-", size=(8, 1),
                      tooltip="在资源管理器中打开DCI EXE所在目录"),
            sg.Checkbox("Enable Dump", default=False, key="-DCI-DUMP-",
                        tooltip="启用Dump功能"),
            sg.Text("Show Median Result", size=(14, 1)),
            sg.Combo(
                ["None", "GLOAT_HIST_LUT", "Global_CF", "Global_HE", "Global_CF_HE", "Global_BWS", "Global_All", "Local_CLAHE"],
                default_value="None",
                key="-DCI-COMBO-MEDIAN-",
                readonly=True,
                size=(12, 1),
                enable_events=True,
                tooltip="右预览区显示的DCI中间结果类型",
            ),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Frame("CF", [
                build_numeric_control_row("Gain Low", "-CF-GL-", 32, 0, 32, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="低亮度预设曲线增益"),
                build_numeric_control_row("Gain Mid", "-CF-GM-", 32, 0, 32, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="中亮度预设曲线增益"),
                build_numeric_control_row("Gain High", "-CF-GH-", 32, 0, 32, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="高亮度预设曲线增益"),
                build_numeric_control_row("CF/HE Ratio", "-CFHE-", 32, 0, 64, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CF/HE融合比例控制"),
            ]),
            sg.Frame("HE", [
                build_numeric_control_row("Split Point ", "HE-SPLIT-", 125, 0, 1023, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="直方图分隔点"),
                build_numeric_control_row("Left Clip", "-HE-LC-", 1.0, 0.01, 1.0, resolution=0.05, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="左半直方图clip比例"),
                build_numeric_control_row("Right Clip", "-HE-RC-", 1.0, 0.01, 1.0, resolution=0.05, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="右半直方图clip比例"),
                build_numeric_control_row("Overlap", "-HE-OVERLAP-", 16, 0, 128, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="分隔点overlap宽度"),
            ]),
            sg.Frame("BS", [
                [sg.Checkbox("Enable", default=True, key="-BS-EN-", tooltip="启用BS处理")],
                build_numeric_control_row("Set Point", "-BS-SP-", 80, 0, 1023, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="黑场拉伸锚点"),
                build_numeric_control_row("Ratio", "-BS-RATIO-", 64, 0, 64, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="黑场拉伸强度"),
                build_numeric_control_row("Overlap", "-BS-OVERLAP-", 64, 0, 64, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="黑场锚点overlap宽度"),
            ]),
            sg.Frame("WS", [
                [sg.Checkbox("Enable", default=True, key="-WS-EN-", tooltip="启用WS处理")],
                build_numeric_control_row("Set Point", "-WS-SP-", 80, 0, 1023, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="白场拉伸锚点"),
                build_numeric_control_row("Ratio", "-WS-RATIO-", 64, 0, 64, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="白场拉伸强度"),
                build_numeric_control_row("Overlap", "-WS-OVERLAP-", 64, 0, 64, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="白场锚点overlap宽度"),
            ]),
        ],
        [sg.Frame("CLAHE", [
            [sg.Checkbox("Enable", default=True, key="-CLAHE-EN-", tooltip="启用CLAHE处理"),
             sg.Push(),
             sg.Button("Reset CF", key="-RESET-CF-", tooltip="重置CF参数"),
             sg.Button("Reset HE", key="-RESET-HE-", tooltip="重置HE参数"),
             sg.Button("Reset BS", key="-RESET-BS-", tooltip="重置BS参数"),
             sg.Button("Reset SW", key="-RESET-WS-", tooltip="重置WS参数"),
             sg.Button("Reset CLAHE", key="-RESET-CLAHE-", tooltip="重置CLAHE参数"),
            ],
            [
                *build_numeric_control_row("Clip Value", "-CLAHE-CV-", 1.0, 0.0, 3.0, resolution=0.1, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE裁剪阈值"),
                *build_numeric_control_row("Local Ratio", "-CLAHE-LR-", 19, 0, 32, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE局部融合比例"),
                *build_numeric_control_row("Left Alpha", "-CLAHE-LA-", 3.0, 0.1, 10.0, resolution=0.1, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE左半融合比例"),
                *build_numeric_control_row("Left ThrLMin", "-CLAHE-LTMIN-", 0.5, 0.0, 1.0, resolution=0.1, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE左半阈值最小值"),
            ],
            [
                *build_numeric_control_row("Left ThrLMax", "-CLAHE-LTMAX-", 2.3, 0.5, 5.0, resolution=0.1, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE左半阈值最大值"),
                *build_numeric_control_row("Left Luma Ratio", "-CLAHE-LLR-", 3.0, 0.1, 10.0, resolution=0.1, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE左半融合比例"),
                *build_numeric_control_row("Right ThrLMin", "-CLAHE-RTMIN-", 0.5, 0.0, 1.0, resolution=0.1, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE右半阈值最小值"),
                *build_numeric_control_row("Right ThrLMax", "-CLAHE-RTMAX-", 2.3, 0.5, 5.0, resolution=0.1, en_spin=True,
                                        label_size=(6,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE右半阈值最大值"),
            ],
        ])],
    ]

# ------------------------------------------------------------------ #
# Event handling                                                     #
# ------------------------------------------------------------------ #

# Per-module slider/spin pairs for group reset
DCI_CF_PAIRS = [
    SliderSpinConfig("-CF-GL-SPIN-", "-CF-GL-SLIDER-", 0, 32, 32, 1),
    SliderSpinConfig("-CF-GM-SPIN-", "-CF-GM-SLIDER-", 0, 32, 32, 1),
    SliderSpinConfig("-CF-GH-SPIN-", "-CF-GH-SLIDER-", 0, 32, 32, 1),
    SliderSpinConfig("-CFHE-SPIN-", "-CFHE-SLIDER-", 0, 64, 32, 1),
]
DCI_HE_PAIRS = [
    SliderSpinConfig("-HE-SPLIT-SPIN-", "-HE-SPLIT-SLIDER-", 0, 1023, 125, 1),
    SliderSpinConfig("-HE-LC-SPIN-", "-HE-LC-SLIDER-", 0.01, 1.0, 1.0, 0.01),
    SliderSpinConfig("-HE-RC-SPIN-", "-HE-RC-SLIDER-", 0.01, 1.0, 1.0, 0.01),
    SliderSpinConfig("-HE-OVERLAP-SPIN-", "-HE-OVERLAP-SLIDER-", 0, 128, 16, 1),
]
DCI_BS_PAIRS = [
    SliderSpinConfig("-BS-SP-SPIN-", "-BS-SP-SLIDER-", 0, 1023, 80, 1),
    SliderSpinConfig("-BS-RATIO-SPIN-", "-BS-RATIO-SLIDER-", 0, 64, 64, 1),
    SliderSpinConfig("-BS-OVERLAP-SPIN-", "-BS-OVERLAP-SLIDER-", 0, 64, 64, 1),
]
DCI_WS_PAIRS = [
    SliderSpinConfig("-WS-SP-SPIN-", "-WS-SP-SLIDER-", 0, 1023, 80, 1),
    SliderSpinConfig("-WS-RATIO-SPIN-", "-WS-RATIO-SLIDER-", 0, 64, 64, 1),
    SliderSpinConfig("-WS-OVERLAP-SPIN-", "-WS-OVERLAP-SLIDER-", 0, 64, 64, 1),
]
DCI_CLAHE_PAIRS = [
    SliderSpinConfig("-CLAHE-CV-SPIN-", "-CLAHE-CV-SLIDER-", 0.0, 3.0, 1.0, 0.1),
    SliderSpinConfig("-CLAHE-LR-SPIN-", "-CLAHE-LR-SLIDER-", 0, 32, 19, 1),
    SliderSpinConfig("-CLAHE-LA-SPIN-", "-CLAHE-LA-SLIDER-", 0.1, 10.0, 3.0, 0.1),
    SliderSpinConfig("-CLAHE-LTMIN-SPIN-", "-CLAHE-LTMIN-SLIDER-", 0.0, 1.0, 0.5, 0.1),
    SliderSpinConfig("-CLAHE-LTMAX-SPIN-", "-CLAHE-LTMAX-SLIDER-", 0.5, 5.0, 2.3, 0.1),
    SliderSpinConfig("-CLAHE-LLR-SPIN-", "-CLAHE-LLR-SLIDER-", 0.1, 10.0, 3.0, 0.1),
    SliderSpinConfig("-CLAHE-RTMIN-SPIN-", "-CLAHE-RTMIN-SLIDER-", 0.0, 1.0, 0.5, 0.1),
    SliderSpinConfig("-CLAHE-RTMAX-SPIN-", "-CLAHE-RTMAX-SLIDER-", 0.5, 5.0, 2.3, 0.1),
]

# Combined flat list for keyboard/sync dispatch
DCI_SLIDER_SPIN_PAIRS = DCI_CF_PAIRS + DCI_HE_PAIRS + DCI_BS_PAIRS + DCI_WS_PAIRS + DCI_CLAHE_PAIRS


def _reset_dci_slider_group(window: sg.Window, values: dict, pairs: list):
    """Reset a group of slider/spin pairs to their default values."""
    for pair in pairs:
        window[pair.slider_key].update(value=pair.def_val)
        display_val = int(pair.def_val) if pair.step >= 1 else pair.def_val
        window[pair.spin_key].update(value=display_val)
        values[pair.slider_key] = pair.def_val
        values[pair.spin_key] = display_val


def handle_dci_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle DCI-specific events. Returns True if consumed."""
    # Group reset buttons
    _RESET_DCI_MAP = {
        "-RESET-CF-": DCI_CF_PAIRS,
        "-RESET-HE-": DCI_HE_PAIRS,
        "-RESET-BS-": DCI_BS_PAIRS,
        "-RESET-WS-": DCI_WS_PAIRS,
        "-RESET-CLAHE-": DCI_CLAHE_PAIRS,
    }
    if event in _RESET_DCI_MAP:
        _reset_dci_slider_group(window, values, _RESET_DCI_MAP[event])
        return True

    # Keyboard suffix events via shared handler
    if handle_keyboard_event(event, values, window, DCI_SLIDER_SPIN_PAIRS):
        return True

    # Slider/spin sync
    for pair in DCI_SLIDER_SPIN_PAIRS:
        if event == pair.slider_key:
            sync_slider_to_spin(window, values, pair.slider_key, pair.spin_key, pair.step, pair)
            return True
        if event == pair.spin_key:
            sync_spin_to_slider(window, values, pair.spin_key, pair.slider_key, pair)
            return True

    # Open Dir buttons
    if event in ("-DCI-OPEN-EXE-DIR-",):
        _open_dci_dir(values, event, window)
        return True

    # COMBO MEDIAN change → invalidate right preview
    if event == "-DCI-COMBO-MEDIAN-":
        return True

    return False


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


def read_params(values: dict) -> dict:
    """Extract DCI module parameters from window values."""
    return {
        "exe_path": values.get("-DCI-EXE-", ""),
        "combo_median": values.get("-DCI-COMBO-MEDIAN-", "None"),
        # CF
        "cf_gain_low": int(float(values.get("-CF-GL-", "32"))),
        "cf_gain_mid": int(float(values.get("-CF-GM-", "32"))),
        "cf_gain_high": int(float(values.get("-CF-GH-", "32"))),
        "cfhe_ratio": int(float(values.get("-CFHE-", "32"))),
        # HE
        "he_split_point": int(float(values.get("HE-SPLIT-", "125"))),
        "he_left_clip": float(values.get("-HE-LC-", "1.0")),
        "he_right_clip": float(values.get("-HE-RC-", "1.0")),
        "he_overlap": int(float(values.get("-HE-OVERLAP-", "16"))),
        # BS
        "bs_enable": values.get("-BS-EN-", True),
        "bs_set_point": int(float(values.get("-BS-SP-", "80"))),
        "bs_ratio": int(float(values.get("-BS-RATIO-", "64"))),
        "bs_overlap": int(float(values.get("-BS-OVERLAP-", "64"))),
        # WS
        "ws_enable": values.get("-WS-EN-", True),
        "ws_set_point": int(float(values.get("-WS-SP-", "80"))),
        "ws_ratio": int(float(values.get("-WS-RATIO-", "64"))),
        "ws_overlap": int(float(values.get("-WS-OVERLAP-", "64"))),
        # CLAHE
        "clahe_enable": values.get("-CLAHE-EN-", True),
        "clahe_clip_value": float(values.get("-CLAHE-CV-", "1.0")),
        "clahe_local_ratio": int(float(values.get("-CLAHE-LR-", "19"))),
        "clahe_left_alpha": float(values.get("-CLAHE-LA-", "3.0")),
        "clahe_left_thr_lmin": float(values.get("-CLAHE-LTMIN", "0.5")),
        "clahe_left_thr_lmax": float(values.get("-CLAHE-LTMAX-", "2.3")),
        "clahe_left_luma_ratio": float(values.get("-CLAHE-LLR-", "3.0")),
        "clahe_right_thr_lmin": float(values.get("-CLAHE-RTMIN-", "0.5")),
        "clahe_right_thr_lmax": float(values.get("-CLAHE-RTMAX-", "2.3")),
    }


def process(src_frame, io_info: dict):
    """Run DCI processing via external dci_runner exe.

    Args:
        src_frame: ImageFrame with input data, fmt, clrspc.
        io_info: dict with "out_fmt", "out_clrspc", "elements",
                 and common I/O metadata (config_path, width, height, etc.).

    Returns:
        (ok: bool, dst_frame: ImageFrame | str)
    """
    from verify_tool_app.pq_verify_tool import ImageFrame

    try:
        params = read_params(io_info["elements"])
        input_fmt = src_frame.fmt
        input_clrspc = src_frame.clrspc
        output_fmt = io_info["out_fmt"]
        output_clrspc = io_info["out_clrspc"]

        exe_path = params.get("exe_path", "")
        config_path = io_info.get("config_path", "")
        output_dir = io_info.get("output_dir", tempfile.gettempdir())
        width = io_info.get("width", 1920)
        height = io_info.get("height", 1080)

        # Resolve relative exe path
        exe_path = _resolve_exe_path(exe_path)

        if not exe_path or not os.path.isfile(exe_path):
            return False, "DCI runner exe not found"

        # Write input channels raw (Y then U then V, each at native resolution)
        input_tmp = os.path.join(tempfile.gettempdir(), f"_dci_input_{width}x{height}_fmt{input_fmt}.yuv")
        with open(input_tmp, 'wb') as f:
            src_frame.pyr.tofile(f)
            src_frame.pug.tofile(f)
            src_frame.pvb.tofile(f)

        # Write output to output_dir
        output_file = os.path.join(output_dir, f"dci_output_{width}x{height}_fmt{output_fmt}.yuv")

        # Run the DCI executable
        dci_args = f'--clahe_clip 1.5 --clahe_local_ratio 20'
        shp_args = f'--shp_type 1 --shp_peaking_gain 150' # todo
        cmd = f'{exe_path} -i {input_tmp} -w {width} -g {height} -f {input_fmt} -r {input_clrspc} -F 0x13 -R 0x5 -o {output_file} -c {config_path} -m 0 {dci_args} {shp_args}'
        result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=500)

        # Read back output
        output_data = read_raw_to_planar(output_file, width, height, output_fmt)
        dst_frame = ImageFrame(output_data[0], output_data[1], output_data[2],
                               output_fmt, output_clrspc)
        return True, dst_frame

    except subprocess.TimeoutExpired:
        return False, "DCI runner timeout"
    except Exception as e:
        return False, str(e)


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


# ------------------------------------------------------------------ #
# Keyboard bindings                                                  #
# ------------------------------------------------------------------ #

def bind_keyboard_events(window: sg.Window):
    """Bind keyboard events (arrows, Enter, step) on all DCI sliders and spins."""
    _bind_kb_shared(window, DCI_SLIDER_SPIN_PAIRS)

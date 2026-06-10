"""
DCI module tab for PQ Test Tool.

Provides DCI audit controls (CF/HE ratio, BS/WS set points, CLAHE).
Processing is done via external dci_runner executable.
Right preview supports chart visualization from DCI dump files (LUT curves, histograms).
"""

from ntpath import exists
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
    LINE,
    STATUS_ERROR,
    STATUS_OK,
    update_status,
    bind_keyboard_events as _bind_kb_shared,
    build_numeric_control_row,
    handle_keyboard_event,
    sync_slider_to_spin,
    sync_spin_to_slider,
)

from config_def.module_config_dci import DciUserConfig

import dci.draw_global_lut as dgl

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
# Right preview — chart source mapping                                 #
# ------------------------------------------------------------------ #

# Map combo option → (chart_type, spec)
#   "combined"   → histogram + 4 LUT curves + CDF + y=x → returns PIL Image
#   "lut"        → apply 1D LUT to Y channel → returns (planar, fmt)
#   "local_lut"  → apply 16×16 local LUT with bilinear interp → returns (planar, fmt)
_COMBO_NONE = "None"
_COMBO_HIST_LUT = "Global_Hist_And_Lut"

_COMBO_SOURCE = {
    _COMBO_HIST_LUT: ("combined", [
        ("dci_glb1_cf_lut_frm0.txt",       "CF"),
        ("dci_glb2_he_lut_frm0.txt",       "HE"),
        ("dci_glb3_cfhe_lut_frm0.txt",     "CF_HE"),
        ("dci_glb4_cfhebws_lut_frm0.txt",  "Final(CF+HE+BWS)"),
    ]),
    "Global_CF":             ("lut", "dci_glb1_cf_lut_frm0.txt"),
    "Global_HE":             ("lut", "dci_glb2_he_lut_frm0.txt"),
    "Global_CF_HE":          ("lut", "dci_glb3_cfhe_lut_frm0.txt"),
    "Global_Final(CF+HE+BWS)": ("lut", "dci_glb4_cfhebws_lut_frm0.txt"),
    "Local_CLAHE":           ("local_lut", "dci_local_clahe_lut.txt"),
}


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
    default_exe = "G:/Codes/RkVopAlgos_git/pub_lib/ModelVerify/AMD64/bin/dci_sim_exe.exe"
    return [
        [
            sg.Text("DCI EXE"),
            sg.Input(default_exe, key="-DCI-EXE-", size=(50, 1),
                     tooltip="DCI模块可执行文件路径"),
            sg.FileBrowse(
                file_types=(("Executable", "*.exe"),),
                target="-DCI-EXE-",
            ),
            sg.Button("Open Dir", key="-DCI-OPEN-EXE-DIR-",
                      tooltip="在资源管理器中打开EXE所在目录"),
            sg.Button("Save Config", key="-DCI-SAVE-CFG-",
                      tooltip="保存配置参数到json配置文件"),
            sg.Text("Show Median Result"),
            sg.Combo(
                ["None", "Global_Hist_And_Lut", "Global_CF", "Global_HE", "Global_CF_HE", "Global_Final(CF+HE+BWS)", "Local_CLAHE"],
                default_value="None",
                key="-DCI-COMBO-MEDIAN-",
                readonly=True,
                enable_events=True,
                tooltip="右预览区显示的DCI中间结果类型（需要启用Dump功能）",
            ),
            sg.Checkbox("Enable Dump", default=False, key="-DCI-DUMP-",
                        tooltip="启用Dump功能"),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Frame("CF", [
                build_numeric_control_row("Gain Low", "-CF-GL-", 32, 0, 32, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="低亮度预设曲线增益"),
                build_numeric_control_row("Gain Mid", "-CF-GM-", 32, 0, 32, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="中亮度预设曲线增益"),
                build_numeric_control_row("Gain High", "-CF-GH-", 32, 0, 32, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="高亮度预设曲线增益"),
                build_numeric_control_row("CF/HE Ratio", "-CFHE-", 32, 0, 64, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CF/HE融合比例控制"),
            ]),
            sg.Frame("HE", [
                build_numeric_control_row("Split Point ", "HE-SPLIT-", 125, 0, 1023, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="直方图分隔点"),
                build_numeric_control_row("Left Clip", "-HE-LC-", 1.0, 0.01, 1.0, resolution=0.05, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="左半直方图clip比例"),
                build_numeric_control_row("Right Clip", "-HE-RC-", 1.0, 0.01, 1.0, resolution=0.05, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="右半直方图clip比例"),
                build_numeric_control_row("Overlap", "-HE-OVERLAP-", 16, 0, 128, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="分隔点overlap宽度"),
            ]),
            sg.Frame("BS", [
                [sg.Checkbox("Enable", default=True, key="-BS-EN-", enable_events=True, tooltip="启用BS处理")],
                build_numeric_control_row("Set Point", "-BS-SP-", 80, 0, 1023, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="黑场拉伸锚点"),
                build_numeric_control_row("Ratio", "-BS-RATIO-", 64, 0, 64, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="黑场拉伸强度"),
                build_numeric_control_row("Overlap", "-BS-OVERLAP-", 64, 0, 64, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="黑场锚点overlap宽度"),
            ]),
            sg.Frame("WS", [
                [sg.Checkbox("Enable", default=True, key="-WS-EN-", enable_events=True, tooltip="启用WS处理")],
                build_numeric_control_row("Set Point", "-WS-SP-", 80, 0, 1023, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="白场拉伸锚点"),
                build_numeric_control_row("Ratio", "-WS-RATIO-", 64, 0, 64, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="白场拉伸强度"),
                build_numeric_control_row("Overlap", "-WS-OVERLAP-", 64, 0, 64, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="白场锚点overlap宽度"),
            ]),
            sg.Frame("CA", [
                [sg.Checkbox("Enable", default=True, key="-CA-EN-", enable_events=True, tooltip="启用CA处理")],
                build_numeric_control_row("Saturation_w", "-CA-SATW-", 56, 0, 64, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="饱和度调整权重"),
                build_numeric_control_row("Adj Coring", "-CA-CORING-", 8, 0, 255, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="亮度门限下限"),
                build_numeric_control_row("Adj Threshold", "-CA-THRESH-", 16, 0, 255, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="亮度门限上限"),
            ]),
        ],
        [sg.Frame("CLAHE", [
            [sg.Checkbox("Enable", default=True, key="-CLAHE-EN-", enable_events=True, tooltip="启用CLAHE处理"),
             sg.Push(),
             sg.Button("Reset CF", key="-RESET-CF-", tooltip="重置CF参数"),
             sg.Button("Reset HE", key="-RESET-HE-", tooltip="重置HE参数"),
             sg.Button("Reset BS", key="-RESET-BS-", tooltip="重置BS参数"),
             sg.Button("Reset SW", key="-RESET-WS-", tooltip="重置WS参数"),
             sg.Button("Reset CA", key="-RESET-CA-", tooltip="重置CA参数"),
             sg.Button("Reset CLAHE", key="-RESET-CLAHE-", tooltip="重置CLAHE参数"),
            ],
            [
                *build_numeric_control_row("Clip Value", "-CLAHE-CV-", 1.0, 0.0, 3.0, resolution=0.1, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE裁剪阈值"),
                *build_numeric_control_row("Local Ratio", "-CLAHE-LR-", 19, 0, 32, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE局部融合比例"),
                *build_numeric_control_row("Left Alpha", "-CLAHE-LA-", 3.0, 0.1, 10.0, resolution=0.1, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE左半融合比例"),
                *build_numeric_control_row("Left ThrLMin", "-CLAHE-LTMIN-", 0.5, 0.0, 1.0, resolution=0.1, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE左半阈值最小值"),
            ],
            [
                *build_numeric_control_row("Left ThrLMax", "-CLAHE-LTMAX-", 2.3, 0.5, 5.0, resolution=0.1, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE左半阈值最大值"),
                *build_numeric_control_row("Left Luma Ratio", "-CLAHE-LLR-", 3.0, 0.1, 10.0, resolution=0.1, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE左半融合比例"),
                *build_numeric_control_row("Right ThrLMin", "-CLAHE-RTMIN-", 0.5, 0.0, 1.0, resolution=0.1, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE右半阈值最小值"),
                *build_numeric_control_row("Right ThrLMax", "-CLAHE-RTMAX-", 2.3, 0.5, 5.0, resolution=0.1, en_spin=True,
                                        label_size=(8,1), slider_size=(8,12), spin_size=(4,1), tooltip="CLAHE右半阈值最大值"),
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
DCI_CA_PAIRS = [
    SliderSpinConfig("-CA-SATW-SPIN-", "-CA-SATW-SLIDER-", 0, 64, 56, 1),
    SliderSpinConfig("-CA-CORING-SPIN-", "-CA-CORING-SLIDER-", 0, 1023, 8, 1),
    SliderSpinConfig("-CA-THRESH-SPIN-", "-CA-THRESH-SLIDER-", 0, 1023, 16, 1),
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
DCI_SLIDER_SPIN_PAIRS = DCI_CF_PAIRS + DCI_HE_PAIRS + DCI_BS_PAIRS + DCI_WS_PAIRS + DCI_CA_PAIRS + DCI_CLAHE_PAIRS


def _reset_dci_slider_group(window: sg.Window, values: dict, pairs: list):
    """Reset a group of slider/spin pairs to their default values."""
    for pair in pairs:
        window[pair.slider_key].update(value=pair.def_val)
        display_val = int(pair.def_val) if pair.step >= 1 else pair.def_val
        window[pair.spin_key].update(value=display_val)
        values[pair.slider_key] = pair.def_val
        values[pair.spin_key] = display_val


# Map DciUserConfig attribute -> UI slider/spin base key (build_numeric_control_row base).
# Tuple: (config_attr, ui_base_key, is_float)
_DCI_CONFIG_UI_MAP = [
    ("cf_gain_low",           "-CF-GL-",     False),
    ("cf_gain_mid",           "-CF-GM-",     False),
    ("cf_gain_high",          "-CF-GH-",     False),
    ("ctrl_dci_CF_HE_ratio",  "-CFHE-",      False),
    ("he_split_point",        "-HE-SPLIT-",   False),
    ("he_left_clip",          "-HE-LC-",     True),
    ("he_right_clip",         "-HE-RC-",     True),
    ("he_overlap",            "-HE-OVERLAP-", False),
    ("bs_set_point",          "-BS-SP-",     False),
    ("bs_ratio",              "-BS-RATIO-",  False),
    ("bs_overlap",            "-BS-OVERLAP-", False),
    ("ws_set_point",          "-WS-SP-",     False),
    ("ws_ratio",              "-WS-RATIO-",  False),
    ("ws_overlap",            "-WS-OVERLAP-", False),
    ("ca_saturation_w",       "-CA-SATW-",   False),
    ("ca_adj_luma_coring_zero", "-CA-CORING-", False),
    ("ca_adj_luma_coring_thrd", "-CA-THRESH-", False),
    ("clahe_clip_value",      "-CLAHE-CV-",  True),
    ("clahe_local_ratio",     "-CLAHE-LR-",  False),
    ("clahe_left_alpha",      "-CLAHE-LA-",  True),
    ("clahe_left_ThrLmin",    "-CLAHE-LTMIN-", True),
    ("clahe_left_ThrLmax",    "-CLAHE-LTMAX-", True),
    ("clahe_left_lumRatio",   "-CLAHE-LLR-", True),
    ("clahe_right_ThrRmin",   "-CLAHE-RTMIN-", True),
    ("clahe_right_ThrRmax",   "-CLAHE-RTMAX-", True),
]

# Checkbox controls mapped to config attributes
_DCI_CONFIG_CHECK_MAP = [
    ("bs_enable",   "-BS-EN-"),
    ("ws_enable",   "-WS-EN-"),
    ("ca_enable",   "-CA-EN-"),
    ("clahe_en",    "-CLAHE-EN-"),
]


def _load_dci_config_to_ui(window: sg.Window, values: dict, config_path: str):
    """Load a DCI config JSON and populate UI controls."""
    cfg = DciUserConfig()
    if not cfg.load(config_path):
        return  # load logs errors internally

    # Populate slider/spin controls
    for attr, base_key, is_float in _DCI_CONFIG_UI_MAP:
        val = getattr(cfg, attr)
        slider_key = f"{base_key}SLIDER-"
        spin_key = f"{base_key}SPIN-"
        window[slider_key].update(value=val)
        display_val = val if is_float else int(val)
        window[spin_key].update(value=display_val)
        values[slider_key] = val
        values[spin_key] = display_val

    # Populate checkboxes
    for attr, key in _DCI_CONFIG_CHECK_MAP:
        val = bool(getattr(cfg, attr))
        window[key].update(value=val)
        values[key] = val


def _save_dci_config_from_ui(values: dict, config_path: str):
    """Save current UI control values to a DCI config JSON file."""
    cfg = DciUserConfig()

    # Collect slider/spin values
    for attr, base_key, _is_float in _DCI_CONFIG_UI_MAP:
        spin_key = f"{base_key}SPIN-"
        val = values.get(spin_key, getattr(cfg, attr))
        setattr(cfg, attr, val)

    # Collect checkbox values
    for attr, key in _DCI_CONFIG_CHECK_MAP:
        setattr(cfg, attr, bool(values.get(key, getattr(cfg, attr))))

    cfg.dump(config_path)


def handle_dci_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle DCI-specific events. Returns True if consumed.

    All slider/spin/checkbox changes auto-save to the config JSON so
    the external DCI runner exe picks up the latest parameters.
    """
    config_path = values.get("-CONFIG-PATH-", "").strip()

    # Group reset buttons
    _RESET_DCI_MAP = {
        "-RESET-CF-": DCI_CF_PAIRS,
        "-RESET-HE-": DCI_HE_PAIRS,
        "-RESET-BS-": DCI_BS_PAIRS,
        "-RESET-WS-": DCI_WS_PAIRS,
        "-RESET-CA-": DCI_CA_PAIRS,
        "-RESET-CLAHE-": DCI_CLAHE_PAIRS,
    }
    if event in _RESET_DCI_MAP:
        _reset_dci_slider_group(window, values, _RESET_DCI_MAP[event])
        _auto_save_dci_config(values, config_path)
        return True

    # Keyboard suffix events via shared handler
    if handle_keyboard_event(event, values, window, DCI_SLIDER_SPIN_PAIRS):
        _enforce_ca_thresh_ge_coring(window, values, event)
        _auto_save_dci_config(values, config_path)
        return True

    # Slider/spin sync
    for pair in DCI_SLIDER_SPIN_PAIRS:
        if event == pair.slider_key:
            sync_slider_to_spin(window, values, pair.slider_key, pair.spin_key, pair.step, pair)
            break
        if event == pair.spin_key:
            sync_spin_to_slider(window, values, pair.spin_key, pair.slider_key, pair)
            break
    else:
        pair = None

    if pair is not None:
        _enforce_ca_thresh_ge_coring(window, values, event)
        _auto_save_dci_config(values, config_path)
        return True

    # Open Dir buttons
    if event in ("-DCI-OPEN-EXE-DIR-",):
        _open_dci_dir(values, event, window)
        return True

    # Save Config button — pop up file save dialog for save-as
    if event == "-DCI-SAVE-CFG-":
        save_path = sg.popup_get_file(
            "Save DCI config as",
            save_as=True,
            file_types=(("JSON", "*.json"),),
            default_extension=".json",
            no_window=True,
        )
        if save_path:
            try:
                _save_dci_config_from_ui(values, save_path)
                window["-CONFIG-PATH-"].update(value=save_path)
                values["-CONFIG-PATH-"] = save_path
                update_status(window, "DCI", LINE(), f"Config saved to {save_path}", level=STATUS_OK)
            except Exception as e:
                update_status(window, "DCI", LINE(), str(e), level=STATUS_ERROR)
        return True

    # COMBO MEDIAN change → invalidate right preview
    if event == "-DCI-COMBO-MEDIAN-":
        return True

    # Enable / Dump checkboxes — auto-save and trigger pipeline re-run
    if event in ("-BS-EN-", "-WS-EN-", "-CA-EN-", "-CLAHE-EN-"):
        _auto_save_dci_config(values, config_path)
        return True

    return False


def _auto_save_dci_config(values, config_path):
    """Silently save DCI UI values to the config JSON file."""
    if not config_path:
        return
    try:
        _save_dci_config_from_ui(values, config_path)
    except Exception:
        pass  # silent fail on auto-save, let exe report missing/bad config


def _enforce_ca_thresh_ge_coring(window: sg.Window, values: dict, event: str) -> None:
    """Ensure CA adj_threshold >= adj_coring_zero. Clamps threshold if needed."""
    ca_keys = {"-CA-CORING-SLIDER-", "-CA-CORING-SPIN-",
               "-CA-THRESH-SLIDER-", "-CA-THRESH-SPIN-"}
    if event not in ca_keys:
        return
    try:
        coring = int(float(values.get("-CA-CORING-SPIN-", 8)))
        thresh = int(float(values.get("-CA-THRESH-SPIN-", 16)))
    except (ValueError, TypeError):
        return
    if thresh >= coring:
        return
    # Clamp threshold up to coring value
    thresh = coring
    # window["-CA-THRESH-SLIDER-"].update(value=thresh)
    # window["-CA-THRESH-SPIN-"].update(value=thresh)
    # values["-CA-THRESH-SLIDER-"] = thresh
    # values["-CA-THRESH-SPIN-"] = thresh


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
        "dump_enable": values.get("-DCI-DUMP-", False),
        "combo_median": values.get("-DCI-COMBO-MEDIAN-", "None"),
        "output_dir": values.get("-OUTPUT-DIR-", "").strip(),
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
        # CA
        "ca_enable": values.get("-CA-EN-", True),
        "ca_saturation_w": int(float(values.get("-CA-SATW-", "56"))),
        "ca_adj_luma_coring_zero": int(float(values.get("-CA-CORING-", "8"))),
        "ca_adj_luma_coring_thrd": int(float(values.get("-CA-THRESH-", "16"))),
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
        input_tmp = os.path.join(output_dir, f"_dci_input_{width}x{height}_fmt{input_fmt:#x}.yuv")
        with open(input_tmp, 'wb') as f:
            src_frame.pyr.tofile(f)
            src_frame.pug.tofile(f)
            src_frame.pvb.tofile(f)

        # Write output to output_dir
        output_file = os.path.join(output_dir, f"dci_output_{width}x{height}_fmt{output_fmt:#x}.yuv")

        # Flush current UI values to a local config file so DCI exe reads latest params.
        # On first run, copy the original config as a base to preserve non-DCI fields.
        local_config_file = os.path.join(output_dir, "_dci_config.json")
        if not exists(local_config_file) and config_path and exists(config_path):
            subprocess.run(f"cp {config_path} {local_config_file}")
        try:
            _save_dci_config_from_ui(io_info["elements"], local_config_file)
        except Exception as e:
            return False, f"Failed to save DCI local config: {e}"

        # Run the DCI executable
        cmd = f'{exe_path} -i {input_tmp} -w {width} -g {height} -f {input_fmt:#x} -r {input_clrspc} -F {output_fmt:#x} -R {output_clrspc} -o {output_file} -c {local_config_file} -m 0'
        if params.get("dump_enable", False):
            cmd += " --dump 0xff"
        try:
            print(f"[DCI] About to run cmd: {cmd}")
            subprocess.run(cmd, check=True, capture_output=False, text=False)
        except subprocess.CalledProcessError as e:
            return False, f"DCI runner failed (exit code {e.returncode})"

        # Read back output
        output_data, _ = read_raw_to_planar(output_file, width, height, output_fmt)
        dst_frame = ImageFrame(output_data[0], output_data[1], output_data[2],
                               output_fmt, output_clrspc)
        return True, dst_frame

    except subprocess.TimeoutExpired:
        return False, "DCI runner timeout"
    except Exception as e:
        return False, str(e)


def get_right_preview_image(snapshot, params: dict):
    """Generate right-side DCI preview.

    Args:
        snapshot: (data, fmt, clrspc) tuple from pipeline.
        params: DCI module parameters (includes combo_median, output_dir).

    Returns:
        - PIL Image for charts (Global_Hist_And_Lut)
        - (mapped_planar, fmt) tuple for LUT-mapped images
        - None if no preview available
    """
    combo_median = params.get("combo_median", _COMBO_NONE)
    if combo_median == _COMBO_NONE:
        return None

    source = _COMBO_SOURCE.get(combo_median)
    if source is None:
        return None

    output_dir = params.get("output_dir", "").strip()
    if not output_dir or not os.path.isdir(output_dir):
        return None

    chart_type, spec = source

    if chart_type == "combined":
        return dgl.draw_combined_to_pil(output_dir, _COMBO_SOURCE[_COMBO_HIST_LUT][1])

    if snapshot is None:
        return None
    data, fmt, _clrspc = snapshot

    if chart_type == "lut":
        filepath = os.path.join(output_dir, spec)
        try:
            _lx, ly = dgl.parse_global_lut_file(filepath)
        except (ValueError, OSError):
            return None
        if ly is None:
            return None
        mapped = _apply_1d_lut(data, ly, _get_bit_depth(fmt))
        return (mapped, fmt)

    if chart_type == "local_lut":
        filepath = os.path.join(output_dir, spec)
        local_lut = dgl.parse_local_lut_flat(filepath)
        if local_lut is None:
            return None
        mapped = _apply_local_lut(data, local_lut, _get_bit_depth(fmt))
        return (mapped, fmt)

    return None


def _get_bit_depth(fmt: int) -> int:
    """Return bit depth for a given format code."""
    return 10 if (fmt & 0x10) else 8


# ------------------------------------------------------------------ #
# Keyboard bindings                                                  #
# ------------------------------------------------------------------ #

def bind_keyboard_events(window: sg.Window):
    """Bind keyboard events (arrows, Enter, step) on all DCI sliders and spins."""
    _bind_kb_shared(window, DCI_SLIDER_SPIN_PAIRS)

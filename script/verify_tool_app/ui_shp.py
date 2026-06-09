"""
SHP (Sharpen) module tab for PQ Test Tool.

Provides sharpen controls (peaking gain, coring, shoot over/under).
Processing is done via external sharpen executable.
"""
import os
import subprocess
import sys
import tempfile
from collections import defaultdict

# Ensure the parent script/ package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import PySimpleGUI as sg

from csc.run_csc import read_raw_to_planar
from verify_tool_app.ui_helpers import (
    SliderSpinConfig,
    LINE,
    STATUS_ERROR,
    STATUS_OK,
    update_status as update_status,
    bind_keyboard_events as _bind_kb_shared,
    build_numeric_control_row,
    handle_keyboard_event,
    sync_slider_to_spin,
    sync_spin_to_slider,
)

TAB_LABEL = "SHP"

# SHP Support image formats
SHP_SUPPORT_IO_FORMATS = defaultdict(
    list, {0x13: [0x13], 0x14: [0x14], 0x16: [0x16], 0x17: [0x17], 0x18: [0x18], 0x19: [0x19], 0x1A: [0x1A]}
)

# ------------------------------------------------------------------ #
# Layout                                                             #
# ------------------------------------------------------------------ #


def build_controls() -> list:
    """Build the SHP Config tab layout."""
    return [
        [
            sg.Text("SHP EXE", size=(10, 1)),
            sg.Input(key="-SHP-EXE-", size=(52, 1), tooltip="SHP锐化硬件模块可执行文件路径"),
            sg.FileBrowse(file_types=(("Executable", "*.exe"),)),
            sg.Button("Open Dir", key="-SHP-OPEN-EXE-DIR-",
                      tooltip="在资源管理器中打开EXE所在目录"),
            sg.Button("Save Config", key="-SHP-SAVE-CFG-",
                      tooltip="保存配置参数到json配置文件"),
        ],
        [sg.HorizontalSeparator()],
        [sg.Checkbox("Enable SHP", default=True, key="-SHP-ENABLE-", tooltip="启用锐化处理模块")],
        build_numeric_control_row("Peaking Gain", "-SHP-GAIN-", 160, 0, 1024, en_spin=True, tooltip="锐化强度"),
        [sg.Checkbox("Enable Coring", default=True, key="-SHP-CORING-ENABLE-", tooltip="启用Coring去噪")],
        build_numeric_control_row("Coring Threshold", "-SHP-CORINGTH-", 0, 0, 255, en_spin=True, tooltip="Coring去噪阈值"),
        [sg.Checkbox("Enable Shoot Ctrl", default=True, key="-SHP-SHOOT-ENABLE-", tooltip="启用Shoot过冲/下冲控制")],
        build_numeric_control_row("Shoot Over", "-SHP-SHOOT-OVER-", 8, 0, 255, en_spin=True, tooltip="过冲抑制强度"),
        build_numeric_control_row("Shoot Under", "-SHP-SHOOT-UNDER-", 64, 0, 255, en_spin=True, tooltip="下冲抑制强度"),
    ]


# ------------------------------------------------------------------ #
# Event handling                                                     #
# ------------------------------------------------------------------ #

SHP_SLIDER_SPIN_PAIRS = [
    SliderSpinConfig("-SHP-GAIN-SPIN-", "-SHP-GAIN-SLIDER-", 0, 1024, 160, 1),
    SliderSpinConfig("-SHP-CORINGTH-SPIN-", "-SHP-CORINGTH-SLIDER-", 0, 255, 0, 1),
    SliderSpinConfig("-SHP-SHOOT-OVER-SPIN-", "-SHP-SHOOT-OVER-SLIDER-", 0, 255, 8, 1),
    SliderSpinConfig("-SHP-SHOOT-UNDER-SPIN-", "-SHP-SHOOT-UNDER-SLIDER-", 0, 255, 64, 1),
]


def _save_shp_config_from_ui(values: dict, config_path: str):
    """Save SHP UI values to CONFIG-PATH json file using SharpConfig."""
    from config_def.module_config_sharp import SharpConfig

    cfg = SharpConfig()

    # Try loading existing config; if it fails, use a fresh default
    if os.path.isfile(config_path):
        cfg.load(config_path)

    # Overlay SHP UI simplified params onto SharpConfig fields
    cfg.s_peaking.i_peakingGain = int(values.get("-SHP-GAIN-SLIDER-", 160))
    cfg.s_sharp_en_ctrl.i_peaking_coring_en = 1 if values.get("-SHP-CORING-ENABLE-", False) else 0
    cfg.s_sharp_en_ctrl.i_shoot_ctrl_en = 1 if values.get("-SHP-SHOOT-ENABLE-", False) else 0

    coring_thr = int(values.get("-SHP-CORINGTH-SLIDER-", 0))
    for i in range(8):
        cfg.s_peaking.t_CoringThreshold[i] = coring_thr

    cfg.s_shootCtrl.i_Alpha_over = int(values.get("-SHP-SHOOT-OVER-SLIDER-", 8))
    cfg.s_shootCtrl.i_Alpha_under = int(values.get("-SHP-SHOOT-UNDER-SLIDER-", 64))

    cfg.dump(config_path)


def handle_shp_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle SHP-specific events. Returns True if consumed."""
    # Keyboard suffix events via shared handler
    if handle_keyboard_event(event, values, window, SHP_SLIDER_SPIN_PAIRS):
        return True

    for pair in SHP_SLIDER_SPIN_PAIRS:
        if event == pair.slider_key:
            sync_slider_to_spin(window, values, pair.slider_key, pair.spin_key, pair.step, pair)
            return True
        if event == pair.spin_key:
            sync_spin_to_slider(window, values, pair.spin_key, pair.slider_key, pair)
            return True

    # Save Config button — write UI values to CONFIG-PATH json file via SharpConfig
    if event == "-SHP-SAVE-CFG-":
        config_path = values.get("-CONFIG-PATH-", "").strip()
        if not config_path:
            update_status(window, "SHP", LINE(), "No config file path specified", level=STATUS_ERROR)
            return True
        try:
            _save_shp_config_from_ui(values, config_path)
            update_status(window, "SHP", LINE(), f"Config saved to {config_path}", level=STATUS_OK)
        except Exception as e:
            update_status(window, "SHP", LINE(), str(e), level=STATUS_ERROR)
        return True

    return False


# ------------------------------------------------------------------ #
# Module protocol                                                    #
# ------------------------------------------------------------------ #


def read_params(values: dict) -> dict:
    """Extract SHP module parameters from window values."""
    return {
        "sharpen_exe": values.get("-SHP-EXE-", ""),
        "enable": values.get("-SHP-ENABLE-", True),
        "peaking_gain": int(values.get("-SHP-GAIN-SPIN-", 160)),
        "coring_enable": values.get("-SHP-CORING-ENABLE-", True),
        "coring_threshold": int(values.get("-SHP-CORINGTH-SPIN-", 0)),
        "shoot_enable": values.get("-SHP-SHOOT-ENABLE-", True),
        "shoot_over": int(values.get("-SHP-SHOOT-OVER-SPIN-", 8)),
        "shoot_under": int(values.get("-SHP-SHOOT-UNDER-SPIN-", 64)),
    }


def process(src_frame, io_info: dict):
    """Run SHP processing via external sharpen exe.

    Args:
        src_frame: ImageFrame with input data, fmt, clrspc.
        io_info: dict with "out_fmt", "out_clrspc", "elements",
                 and common I/O metadata (width, height, output_dir).

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

        sharpen_exe = params.get("sharpen_exe", "")
        if not sharpen_exe or not os.path.isfile(sharpen_exe):
            return False, "Sharpen exe not found"

        width = io_info.get("width", 1920)
        height = io_info.get("height", 1080)

        # Write input channels raw (Y then U then V, each at native resolution)
        input_tmp = os.path.join(tempfile.gettempdir(), "_shp_input.raw")
        with open(input_tmp, 'wb') as f:
            src_frame.pyr.tofile(f)
            src_frame.pug.tofile(f)
            src_frame.pvb.tofile(f)

        # Output file
        output_dir = io_info.get("output_dir", tempfile.gettempdir())
        output_file = os.path.join(output_dir, "shp_output.raw")

        # Build command line arguments
        cmd = [
            sharpen_exe,
            "--input",
            input_tmp,
            "--output",
            output_file,
            "--width",
            str(width),
            "--height",
            str(height),
            "--format",
            str(input_fmt),
        ]
        if params.get("enable"):
            cmd.extend(["--peaking-gain", str(params["peaking_gain"])])
            cmd.extend(["--coring-threshold", str(params["coring_threshold"])])
            cmd.extend(["--shoot-over", str(params["shoot_over"])])
            cmd.extend(["--shoot-under", str(params["shoot_under"])])

        result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return False, f"Sharpen failed: {result.stderr[:200]}"

        if not os.path.isfile(output_file):
            return False, "Sharpen output file not created"

        output_data = read_raw_to_planar(output_file, width, height, output_fmt)
        dst_frame = ImageFrame(output_data[0], output_data[1], output_data[2], output_fmt, output_clrspc)
        return True, dst_frame

    except subprocess.TimeoutExpired:
        return False, "Sharpen timeout"
    except Exception as e:
        return False, str(e)


def get_right_preview_image(snapshot, params: dict):
    """No SHP-specific right-side preview yet."""
    return None


# ------------------------------------------------------------------ #
# Keyboard bindings                                                  #
# ------------------------------------------------------------------ #


def bind_keyboard_events(window: sg.Window):
    """Bind keyboard events on all SHP sliders and spins."""
    _bind_kb_shared(window, SHP_SLIDER_SPIN_PAIRS)

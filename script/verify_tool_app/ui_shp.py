"""
SHP (Sharpen) module tab for PQ Test Tool.

Provides sharpen controls (peaking gain, coring, shoot over/under).
Processing is done via external sharpen executable.
"""

import os
import subprocess
import tempfile

import numpy as np
import PySimpleGUI as sg

from csc.run_csc import read_raw_to_planar, write_planar_to_raw
from verify_tool_app.ui_helpers import (
    SliderSpinConfig,
    bind_keyboard_events as _bind_kb_shared,
    handle_keyboard_event,
    sync_slider_to_spin,
    sync_spin_to_slider,
)

TAB_LABEL = "SHP"


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
    tooltip: str = "",
    norm_key: str = None,
    reset_key: str = None,
) -> list:
    """Build a synchronized spinbox + slider + norm text + reset button control row."""
    steps = int(round((max_value - min_value) / resolution))
    spin_values = [
        round(min_value + i * resolution, 1 if resolution < 1 else 0)
        for i in range(steps + 1)
    ]
    if resolution >= 1:
        spin_values = [int(v) for v in spin_values]

    row = [
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
            tooltip=tooltip,
        ),
        sg.Spin(
            spin_values,
            initial_value=default_value,
            size=(8, 1),
            key=spin_key,
            enable_events=True,
            tooltip=tooltip,
        ),
    ]
    if norm_key is not None:
        row.append(sg.Text("", size=(8, 1), key=norm_key, justification="left"))
    if reset_key is not None:
        row.append(sg.Button("Reset", key=reset_key, size=(6, 1),
                             tooltip=f"重置{label}为默认值"))
    return row


def build_controls() -> list:
    """Build the SHP Config tab layout."""
    return [
        [
            sg.Text("SHP EXE", size=(10, 1)),
            sg.Input(key="-SHP-EXE-", size=(52, 1),
                     tooltip="SHP锐化硬件模块可执行文件路径"),
            sg.FileBrowse(
                file_types=(("Executable", "*.exe"),),
                size=(8, 1),
            ),
        ],
        [sg.HorizontalSeparator()],
        [sg.Checkbox("Enable SHP", default=True, key="-SHP-ENABLE-",
                     tooltip="启用锐化处理模块")],
        _build_numeric_control_row(
            "Peaking Gain", "-SHP-PEAKING-GAIN-", "-SHP-PEAKING-GAIN-SLIDER-",
            160, 0, 1024,
            norm_key="-SHP-PEAKING-GAIN-NORM-",
            reset_key="-SHP-PEAKING-GAIN-RESET-",
            tooltip="Peaking锐化增益（0~1024，默认160）",
        ),
        [sg.Checkbox("Enable Coring", default=True, key="-SHP-CORING-ENABLE-",
                     tooltip="启用Coring去噪（低于阈值的细节被抑制）")],
        _build_numeric_control_row(
            "Coring Threshold", "-SHP-CORING-THRESHOLD-", "-SHP-CORING-THRESHOLD-SLIDER-",
            0, 0, 255,
            norm_key="-SHP-CORING-THRESHOLD-NORM-",
            reset_key="-SHP-CORING-THRESHOLD-RESET-",
            tooltip="Coring去噪阈值（0~255，默认0）",
        ),
        [sg.Checkbox("Enable Shoot Ctrl", default=True, key="-SHP-SHOOT-ENABLE-",
                     tooltip="启用Shoot过冲/下冲控制")],
        _build_numeric_control_row(
            "Shoot Over", "-SHP-SHOOT-OVER-", "-SHP-SHOOT-OVER-SLIDER-",
            8, 0, 255,
            norm_key="-SHP-SHOOT-OVER-NORM-",
            reset_key="-SHP-SHOOT-OVER-RESET-",
            tooltip="过冲抑制强度（0~255，默认8）",
        ),
        _build_numeric_control_row(
            "Shoot Under", "-SHP-SHOOT-UNDER-", "-SHP-SHOOT-UNDER-SLIDER-",
            64, 0, 255,
            norm_key="-SHP-SHOOT-UNDER-NORM-",
            reset_key="-SHP-SHOOT-UNDER-RESET-",
            tooltip="下冲抑制强度（0~255，默认64）",
        ),
    ]


# ------------------------------------------------------------------ #
# Event handling                                                     #
# ------------------------------------------------------------------ #

SHP_SLIDER_SPIN_PAIRS = [
    SliderSpinConfig(spin_key="-SHP-PEAKING-GAIN-", slider_key="-SHP-PEAKING-GAIN-SLIDER-",
                     min_val=0, max_val=1024, def_val=160, step=1,
                     norm_key="-SHP-PEAKING-GAIN-NORM-",
                     norm_func=lambda v, _: f"{v/1024:.3f}",
                     reset_key="-SHP-PEAKING-GAIN-RESET-"),
    SliderSpinConfig(spin_key="-SHP-CORING-THRESHOLD-", slider_key="-SHP-CORING-THRESHOLD-SLIDER-",
                     min_val=0, max_val=255, def_val=0, step=1,
                     norm_key="-SHP-CORING-THRESHOLD-NORM-",
                     norm_func=lambda v, _: f"{v/255:.3f}",
                     reset_key="-SHP-CORING-THRESHOLD-RESET-"),
    SliderSpinConfig(spin_key="-SHP-SHOOT-OVER-", slider_key="-SHP-SHOOT-OVER-SLIDER-",
                     min_val=0, max_val=255, def_val=8, step=1,
                     norm_key="-SHP-SHOOT-OVER-NORM-",
                     norm_func=lambda v, _: f"{v/255:.3f}",
                     reset_key="-SHP-SHOOT-OVER-RESET-"),
    SliderSpinConfig(spin_key="-SHP-SHOOT-UNDER-", slider_key="-SHP-SHOOT-UNDER-SLIDER-",
                     min_val=0, max_val=255, def_val=64, step=1,
                     norm_key="-SHP-SHOOT-UNDER-NORM-",
                     norm_func=lambda v, _: f"{v/255:.3f}",
                     reset_key="-SHP-SHOOT-UNDER-RESET-"),
]


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
    return False


# ------------------------------------------------------------------ #
# Module protocol                                                    #
# ------------------------------------------------------------------ #

def read_params(values: dict) -> dict:
    """Extract SHP module parameters from window values."""
    return {
        "enable": values.get("-SHP-ENABLE-", True),
        "peaking_gain": int(values.get("-SHP-PEAKING-GAIN-", "160")),
        "coring_enable": values.get("-SHP-CORING-ENABLE-", True),
        "coring_threshold": int(values.get("-SHP-CORING-THRESHOLD-", "0")),
        "shoot_enable": values.get("-SHP-SHOOT-ENABLE-", True),
        "shoot_over": int(values.get("-SHP-SHOOT-OVER-", "8")),
        "shoot_under": int(values.get("-SHP-SHOOT-UNDER-", "64")),
    }


def process(input_data: np.ndarray, input_fmt: int, input_clrspc: int,
            output_fmt: int, output_clrspc: int, params: dict,
            io_params: dict):
    """Run SHP processing via external sharpen exe.

    Returns:
        (ok: bool, output_data: np.ndarray | str, out_fmt: int, out_clrspc: int)
    """
    try:
        sharpen_exe = io_params.get("sharpen_exe", "")
        if not sharpen_exe or not os.path.isfile(sharpen_exe):
            return False, "Sharpen exe not found", input_fmt, input_clrspc

        width = io_params.get("width", 1920)
        height = io_params.get("height", 1080)

        # Write input to temp raw
        input_tmp = os.path.join(tempfile.gettempdir(), "_shp_input.raw")
        write_planar_to_raw(input_data, input_tmp)

        # Output file
        output_dir = io_params.get("output_dir", tempfile.gettempdir())
        output_file = os.path.join(output_dir, "shp_output.raw")

        # Build command line arguments
        cmd = [
            sharpen_exe,
            "--input", input_tmp,
            "--output", output_file,
            "--width", str(width),
            "--height", str(height),
            "--format", str(input_fmt),
        ]
        if params.get("enable"):
            cmd.extend(["--peaking-gain", str(params["peaking_gain"])])
            cmd.extend(["--coring-threshold", str(params["coring_threshold"])])
            cmd.extend(["--shoot-over", str(params["shoot_over"])])
            cmd.extend(["--shoot-under", str(params["shoot_under"])])

        result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return False, f"Sharpen failed: {result.stderr[:200]}", input_fmt, input_clrspc

        if not os.path.isfile(output_file):
            return False, "Sharpen output file not created", input_fmt, input_clrspc

        output_data = read_raw_to_planar(output_file, width, height, output_fmt)
        return True, output_data, output_fmt, output_clrspc

    except subprocess.TimeoutExpired:
        return False, "Sharpen timeout", input_fmt, input_clrspc
    except Exception as e:
        return False, str(e), input_fmt, input_clrspc


def get_right_preview_image(snapshot, params: dict):
    """No SHP-specific right-side preview yet."""
    return None


# ------------------------------------------------------------------ #
# Keyboard bindings                                                  #
# ------------------------------------------------------------------ #

def bind_keyboard_events(window: sg.Window):
    """Bind keyboard events on all SHP sliders and spins."""
    _bind_kb_shared(window, SHP_SLIDER_SPIN_PAIRS)

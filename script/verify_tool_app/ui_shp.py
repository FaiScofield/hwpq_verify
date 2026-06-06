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
) -> list:
    """Build a synchronized spinbox + slider control row."""
    steps = int(round((max_value - min_value) / resolution))
    spin_values = [
        round(min_value + i * resolution, 1 if resolution < 1 else 0)
        for i in range(steps + 1)
    ]
    if resolution >= 1:
        spin_values = [int(v) for v in spin_values]

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


def build_controls() -> list:
    """Build the SHP Config tab layout."""
    return [
        [
            sg.Text("SHP EXE", size=(10, 1)),
            sg.Input(key="-SHP-EXE-", size=(52, 1)),
            sg.FileBrowse(
                file_types=(("Executable", "*.exe"),),
                size=(8, 1),
            ),
        ],
        [sg.HorizontalSeparator()],
        [sg.Checkbox("Enable SHP", default=True, key="-SHP-ENABLE-")],
        _build_numeric_control_row(
            "Peaking Gain", "-SHP-PEAKING-GAIN-", "-SHP-PEAKING-GAIN-SLIDER-",
            160, 0, 1024,
        ),
        [sg.Checkbox("Enable Coring", default=True, key="-SHP-CORING-ENABLE-")],
        _build_numeric_control_row(
            "Coring Threshold", "-SHP-CORING-THRESHOLD-", "-SHP-CORING-THRESHOLD-SLIDER-",
            0, 0, 255,
        ),
        [sg.Checkbox("Enable Shoot Ctrl", default=True, key="-SHP-SHOOT-ENABLE-")],
        _build_numeric_control_row(
            "Shoot Over", "-SHP-SHOOT-OVER-", "-SHP-SHOOT-OVER-SLIDER-",
            8, 0, 255,
        ),
        _build_numeric_control_row(
            "Shoot Under", "-SHP-SHOOT-UNDER-", "-SHP-SHOOT-UNDER-SLIDER-",
            64, 0, 255,
        ),
    ]


# ------------------------------------------------------------------ #
# Event handling                                                     #
# ------------------------------------------------------------------ #

SHP_SLIDER_KEYS = [
    ("-SHP-PEAKING-GAIN-", "-SHP-PEAKING-GAIN-SLIDER-"),
    ("-SHP-CORING-THRESHOLD-", "-SHP-CORING-THRESHOLD-SLIDER-"),
    ("-SHP-SHOOT-OVER-", "-SHP-SHOOT-OVER-SLIDER-"),
    ("-SHP-SHOOT-UNDER-", "-SHP-SHOOT-UNDER-SLIDER-"),
]


def handle_shp_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle SHP-specific events. Returns True if consumed."""
    # -- Keyboard suffix events (bind_keyboard_events) - step before exact match --
    if "+" in event:
        event_key, _, event_suffix = event.rpartition("+")
        if event_key.endswith("-SLIDER-") and event_suffix in ("LEFT", "RIGHT"):
            delta = -1 if event_suffix == "LEFT" else 1
            _step_shp_slider(window, values, event_key, delta)
            return True
        if not event_key.endswith("-SLIDER-") and event_suffix in ("STEP", "ENTER"):
            _commit_shp_spin_to_slider(window, values, event_key)
            return True

    for spin_key, slider_key in SHP_SLIDER_KEYS:
        if event in (spin_key, slider_key):
            _sync_numeric_control(window, values, spin_key, slider_key)
            return True
    return False


def _sync_numeric_control(window: sg.Window, values: dict,
                           spin_key: str, slider_key: str):
    """Keep spinbox and slider values synchronized."""
    try:
        value = float(values[spin_key])
    except (ValueError, TypeError):
        return
    window[slider_key].update(value=value)
    window[spin_key].update(value=value)


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

# SHP slider parameters: (min, max, resolution)
_SHP_SLIDER_PARAMS = {
    "-SHP-PEAKING-GAIN-SLIDER-": (0, 1024, 1),
    "-SHP-CORING-THRESHOLD-SLIDER-": (0, 255, 1),
    "-SHP-SHOOT-OVER-SLIDER-": (0, 255, 1),
    "-SHP-SHOOT-UNDER-SLIDER-": (0, 255, 1),
}


def _step_shp_slider(window: sg.Window, values: dict, slider_key: str, delta: int):
    """For SHP slider +LEFT / +RIGHT: step by resolution."""
    params = _SHP_SLIDER_PARAMS.get(slider_key)
    if params is None:
        return
    _min, _max, resolution = params
    try:
        cur = float(values.get(slider_key, 0))
    except (ValueError, TypeError):
        return
    val = max(_min, min(_max, cur + delta * resolution))
    if resolution >= 1:
        val = int(round(val))
    window[slider_key].update(value=val)
    # Sync spin
    for spin_key, s_key in SHP_SLIDER_KEYS:
        if s_key == slider_key:
            window[spin_key].update(value=val)
            break


def _commit_shp_spin_to_slider(window: sg.Window, values: dict, spin_key: str):
    """For SHP spin +STEP / +ENTER: commit spin value to slider."""
    try:
        val = float(values.get(spin_key, 0))
    except (ValueError, TypeError):
        return
    for s_key, slider_key in SHP_SLIDER_KEYS:
        if s_key == spin_key:
            window[slider_key].update(value=val)
            break


def bind_keyboard_events(window: sg.Window):
    """Bind keyboard events (arrows, Enter, step) on all SHP sliders and spins."""
    for spin_key, slider_key in SHP_SLIDER_KEYS:
        # Spin: Return / KP_Enter to commit, command for step
        try:
            window[spin_key].bind("<Return>", "+ENTER")
            window[spin_key].bind("<KP_Enter>", "+ENTER")
            window[spin_key].Widget.configure(
                command=lambda wk=window, sk=spin_key: wk.write_event_value(f"{sk}+STEP", None)
            )
        except Exception:
            pass
        # Slider: Left/Right arrow to step, Button-1 to focus
        try:
            sw = window[slider_key].Widget
            sw.configure(takefocus=1)
            sw.bind("<Button-1>", lambda e, w=sw: w.focus_set(), add="+")
            sw.bind("<Left>", lambda e, wk=window, sk=slider_key: wk.write_event_value(f"{sk}+LEFT", None))
            sw.bind("<Right>", lambda e, wk=window, sk=slider_key: wk.write_event_value(f"{sk}+RIGHT", None))
        except Exception:
            pass

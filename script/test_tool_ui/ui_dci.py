"""
DCI module tab for PQ Test Tool.

Provides DCI audit controls (CF/HE ratio, BS/WS set points, CLAHE).
Processing is done via external dci_runner executable.
"""

import os
import subprocess
import tempfile
import json

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
    """Build the DCI Config tab layout."""
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


def handle_dci_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle DCI-specific events. Returns True if consumed."""
    for spin_key, slider_key in DCI_SLIDER_KEYS:
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
    """Extract DCI module parameters from window values."""
    return {
        "audit_enable": values.get("-AUDIT-ENABLE-", False),
        "tag": values.get("-TAG-", "ui_live"),
        "nodemask": values.get("-NODEMASK-", "0"),
        "exportmask": values.get("-EXPORTMASK-", "0"),
        "dumpmask": values.get("-DUMPMASK-", "0"),
        "cfhe_ratio": int(values.get("-CFHE-", "32")),
        "bs_set_point": int(values.get("-BS-", "80")),
        "ws_set_point": int(values.get("-WS-", "80")),
        "clahe_local_ratio": int(values.get("-CLAHE-R-", "19")),
        "clahe_clip_value": float(values.get("-CLAHE-C-", "1.0")),
    }


def process(input_data: np.ndarray, input_fmt: int, input_clrspc: int,
            output_fmt: int, output_clrspc: int, params: dict,
            io_params: dict):
    """Run DCI processing via external dci_runner exe.

    Writes input as temp raw file, invokes runner, reads back output.

    Returns:
        (ok: bool, output_data: np.ndarray | str, out_fmt: int, out_clrspc: int)
    """
    try:
        exe_path = io_params.get("exe_path", "")
        config_path = io_params.get("config_path", "")
        output_dir = io_params.get("output_dir", tempfile.gettempdir())
        width = io_params.get("width", 1920)
        height = io_params.get("height", 1080)

        if not exe_path or not os.path.isfile(exe_path):
            return False, "DCI runner exe not found", input_fmt, input_clrspc

        # Write input data to temp raw file
        input_tmp = os.path.join(tempfile.gettempdir(), "_dci_input.raw")
        write_planar_to_raw(input_data, input_tmp)

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
            audit=DciAuditConfig(
                enable=1 if params.get("audit_enable") else 0,
                static_only=0,
                node_mask=params.get("nodemask", "0"),
                export_mask=params.get("exportmask", "0"),
                debug_dump_mask=params.get("dumpmask", "0"),
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
    """No DCI-specific right-side preview yet."""
    return None

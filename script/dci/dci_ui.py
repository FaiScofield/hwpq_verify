"""
PySimpleGUI-based DCI Layer 1 Runner UI.

Provides five panels:
  1. Input panel       -- file paths, geometry, format
  2. Audit control     -- enable, node/export masks, override knobs
  3. Preview panel     -- input/output preview, simulated preview
  4. Data panel        -- histogram plots, global curve plots, metrics text
  5. Action panel      -- Run, Refresh, Save Config & Result, Open Working Dir
"""

import json
import os
import sys
from dataclasses import dataclass, field

# Ensure the parent script/ package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PySimpleGUI as sg

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


def _build_input_panel() -> list:
    """Build the input configuration panel."""
    return [
        [
            sg.Text("Runner EXE"),
            sg.Input(key="-EXE-"),
            sg.FileBrowse(file_types=(("Executable", "*.exe"),)),
        ],
        [
            sg.Text("Working Dir"),
            sg.Input(key="-WORKING-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Text("Snapshot Root"),
            sg.Input(key="-SNAPROOT-"),
            sg.FolderBrowse(),
        ],
        [sg.HorizontalSeparator()],
        [sg.Text("Input File"), sg.Input(key="-INPUT-"), sg.FileBrowse()],
        [sg.Text("Output File"), sg.Input(key="-OUTPUT-"), sg.FileBrowse()],
        [
            sg.Text("Width"),
            sg.Input("1920", size=(8, 1), key="-WIDTH-"),
            sg.Text("Height"),
            sg.Input("1080", size=(8, 1), key="-HEIGHT-"),
        ],
        [
            sg.Text("Pixel Format"),
            sg.Combo(
                ["19 (YUV444 10-bit)", "0 (YUV420 8-bit)"],
                default_value="19 (YUV444 10-bit)",
                key="-PIXFMT-",
                readonly=True,
            ),
        ],
        [
            sg.Text("Is Src Full Range"),
            sg.Checkbox("", default=True, key="-FULLRANGE-"),
        ],
        [sg.Text("Config Path"), sg.Input(key="-CONFIG-"), sg.FileBrowse()],
        [sg.Text("Reg Path"), sg.Input(key="-REGPATH-"), sg.FolderBrowse()],
        [
            sg.Text("Frame Idx"),
            sg.Input("0", size=(8, 1), key="-FRAMEIDX-"),
            sg.Text("Frame Num"),
            sg.Input("1", size=(8, 1), key="-FRAMENUM-"),
        ],
        [sg.Text("Debug Dump Mask"), sg.Input("0", size=(8, 1), key="-DUMPMASK-")],
        [sg.Text("Debug Path"), sg.Input(key="-DEBUGPATH-"), sg.FolderBrowse()],
    ]


def _build_audit_panel() -> list:
    """Build the audit control panel with override knobs."""
    return [
        [
            sg.Checkbox("Enable Audit", default=False, key="-AUDIT-ENABLE-"),
            sg.Checkbox("Static Only", default=True, key="-STATIC-ONLY-"),
        ],
        [
            sg.Text("Node Mask"),
            sg.Input("0", size=(8, 1), key="-NODEMASK-"),
            sg.Text("Export Mask"),
            sg.Input("0", size=(8, 1), key="-EXPORTMASK-"),
        ],
        [
            sg.Text("Tag"),
            sg.Input("ui_live", size=(20, 1), key="-TAG-"),
        ],
        [
            sg.Checkbox("Override CF/HE Ratio", key="-OVR-CFHE-"),
            sg.Input("32", size=(6, 1), key="-CFHE-"),
            sg.Checkbox("Override BS Set Point", key="-OVR-BS-"),
            sg.Input("80", size=(6, 1), key="-BS-"),
        ],
        [
            sg.Checkbox("Override WS Set Point", key="-OVR-WS-"),
            sg.Input("80", size=(6, 1), key="-WS-"),
            sg.Checkbox("Override CLAHE Local Ratio", key="-OVR-CLAHE-R-"),
            sg.Input("19", size=(6, 1), key="-CLAHE-R-"),
        ],
        [
            sg.Checkbox("Override CLAHE Clip Value", key="-OVR-CLAHE-C-"),
            sg.Input("1.0", size=(6, 1), key="-CLAHE-C-"),
        ],
    ]


def _build_action_panel() -> list:
    """Build the action bar."""
    return [
        [
            sg.Button("Run", size=(10, 1), key="-RUN-"),
            sg.Button("Refresh", size=(10, 1), key="-REFRESH-"),
            sg.Button("Save Config & Result", size=(18, 1), key="-SAVE-"),
            sg.Button("Open Working Dir", size=(16, 1), key="-OPEN-DIR-"),
        ],
        [sg.Text("", key="-STATUS-", text_color="gray", size=(60, 1))],
    ]


def _build_main_layout() -> list:
    """Assemble the full UI layout."""
    return [
        [sg.Text("DCI Layer 1 Runner", font=("Helvetica", 14, "bold"))],
        [sg.HorizontalSeparator()],
        [sg.Frame("Input Configuration", _build_input_panel(), expand_x=True)],
        [sg.Frame("Audit Controls", _build_audit_panel(), expand_x=True)],
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


def _build_request_from_values(values: dict) -> DciRunnerRequest:
    """Build a DciRunnerRequest from current UI field values."""
    pixfmt_str = values.get("-PIXFMT-", "19 (YUV444 10-bit)")
    pixel_format = 19 if "19" in pixfmt_str else 0

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
        enable_cf_he_ratio_override=1 if values.get("-OVR-CFHE-") else 0,
        cf_he_ratio=_try_int(values.get("-CFHE-", "32"), 32),
        enable_bs_set_point_override=1 if values.get("-OVR-BS-") else 0,
        bs_set_point=_try_int(values.get("-BS-", "80"), 80),
        enable_ws_set_point_override=1 if values.get("-OVR-WS-") else 0,
        ws_set_point=_try_int(values.get("-WS-", "80"), 80),
        enable_clahe_local_ratio_override=1 if values.get("-OVR-CLAHE-R-") else 0,
        clahe_local_ratio=_try_int(values.get("-CLAHE-R-", "19"), 19),
        enable_clahe_clip_value_override=1 if values.get("-OVR-CLAHE-C-") else 0,
        clahe_clip_value=_try_float(values.get("-CLAHE-C-", "1.0"), 1.0),
    )

    audit = DciAuditConfig(
        enable=1 if values.get("-AUDIT-ENABLE-") else 0,
        static_only=1 if values.get("-STATIC-ONLY-") else 0,
        node_mask=_try_int(values.get("-NODEMASK-", "0"), 0),
        export_mask=_try_int(values.get("-EXPORTMASK-", "0"), 0),
        tag=values.get("-TAG-", "ui_live"),
        working_dir=values.get("-WORKING-", ""),
        save_snapshot=0,
        snapshot_dir=values.get("-SNAPROOT-", ""),
        override_cfg=override,
    )

    return DciRunnerRequest(
        platform=1,
        input_file=values.get("-INPUT-", ""),
        output_file=values.get("-OUTPUT-", ""),
        width=width,
        height=height,
        pixel_format=pixel_format,
        config_path=values.get("-CONFIG-", ""),
        reg_path=values.get("-REGPATH-", ""),
        is_src_fullrange=1 if values.get("-FULLRANGE-") else 0,
        frame_idx=frame_idx,
        frame_num=frame_num,
        debug_dump_mask=dump_mask,
        debug_path=values.get("-DEBUGPATH-", ""),
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


def _do_run(values: dict, state: DciUiState, window: sg.Window):
    """Execute a DCI run: build request, launch runner, load results."""
    exe_path = values.get("-EXE-", "").strip()
    if not exe_path or not os.path.isfile(exe_path):
        window["-STATUS-"].update("Runner executable not found", text_color="red")
        return

    working_dir = values.get("-WORKING-", "").strip()
    if not working_dir:
        window["-STATUS-"].update("Working directory is required", text_color="red")
        return

    os.makedirs(working_dir, exist_ok=True)
    state.request_path = os.path.join(working_dir, "runner_request.json")
    state.result_path = os.path.join(working_dir, "runner_result.json")

    request = _build_request_from_values(values)
    write_runner_request(request, state.request_path)

    window["-STATUS-"].update("Running native DCI runner...", text_color="blue")
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
    working_dir = values.get("-WORKING-", "").strip()
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
    working_dir = values.get("-WORKING-", "").strip()
    snapshot_root = values.get("-SNAPROOT-", "").strip()
    tag = values.get("-TAG-", "").strip() or "dci_case"

    if not working_dir or not os.path.isdir(working_dir):
        window["-STATUS-"].update("Working directory not ready", text_color="red")
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
    """Open the working directory in Windows Explorer."""
    working_dir = values.get("-WORKING-", "").strip()
    if working_dir and os.path.isdir(working_dir):
        os.startfile(working_dir)
    else:
        window["-STATUS-"].update("Working directory not found", text_color="orange")


# ------------------------------------------------------------------ #
# Entry point                                                        #
# ------------------------------------------------------------------ #


def main():
    sg.theme("SystemDefault")
    layout = _build_main_layout()

    window = sg.Window(
        "DCI Layer 1 Runner",
        layout,
        resizable=True,
        finalize=True,
    )

    state = DciUiState()
    state.exe_path = _find_default_runner()

    # Pre-fill runner path if found
    if state.exe_path:
        window["-EXE-"].update(state.exe_path)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        elif event == "-RUN-":
            _do_run(values, state, window)

        elif event == "-REFRESH-":
            _do_refresh(values, state, window)

        elif event == "-SAVE-":
            _do_save(values, state, window)

        elif event == "-OPEN-DIR-":
            _do_open_dir(values, window)

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

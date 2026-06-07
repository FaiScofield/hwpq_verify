"""
Shared slider+spin keyboard binding and event dispatch utilities.

Supports optional extensions per pair:
  - norm_key + norm_func: auto-display a normalized value on a Text widget.
  - reset_key: auto-handle reset button click to restore def_val.
"""

from __future__ import annotations
from collections import namedtuple
from typing import Callable

import PySimpleGUI as sg

# ------------------------------------------------------------------ #
# SliderSpinConfig                                                   #
# ------------------------------------------------------------------ #

SliderSpinConfig = namedtuple(
    "SliderSpinConfig",
    [
        "spin_key", "slider_key", "min_val", "max_val", "def_val", "step",
        "norm_key", "norm_func", "reset_key",
    ],
    defaults=(1, None, None, None),
)
# norm_func signature: Callable[[float, dict], str]
#   - arg0: current raw slider value
#   - arg1: window values dict (for reading context like algo_type combo)
#   - returns: string to display in norm_key Text widget

# ------------------------------------------------------------------ #
# Shared layout helper                                              #
# ------------------------------------------------------------------ #

def build_numeric_control_row(
    label: str,
    spin_key: str,
    slider_key: str,
    default_value,
    min_value,
    max_value,
    resolution: float = 1.0,
    label_size: tuple = (22, 1),
    slider_size: tuple = (28, 15),
    spin_size: tuple = (8, 1),
    norm_text_size: tuple = (8, 1),
    reset_button_size: tuple = (6, 1),
    tooltip: str = "",
    norm_key: str = None,
    reset_key: str = -1,  # -1 = auto-generate from slider_key; None = no button
) -> list:
    """Build a synchronized spinbox + slider + norm text + reset button control row.

    Args:
        reset_key: key for reset button. -1 (default) auto-generates as f"{slider_key}-RESET-"
                   and always shows button. None suppresses the reset button.
    """
    steps = int(round((max_value - min_value) / resolution))
    spin_values = [
        round(min_value + i * resolution, 1 if resolution < 1 else 0)
        for i in range(steps + 1)
    ]
    if resolution >= 1:
        spin_values = [int(v) for v in spin_values]

    # Auto-generate reset_key if needed
    if reset_key == -1:
        reset_key = f"{slider_key}-RESET-"

    row = [
        sg.Text(label, size=label_size),
        sg.Slider(
            range=(min_value, max_value),
            default_value=default_value,
            resolution=resolution,
            orientation="h",
            size=slider_size,
            key=slider_key,
            enable_events=True,
            disable_number_display=True,
            tooltip=tooltip,
        ),
        sg.Spin(
            spin_values,
            initial_value=default_value,
            size=spin_size,
            key=spin_key,
            enable_events=True,
            tooltip=tooltip,
        ),
    ]
    if norm_key is not None:
        row.append(sg.Text("", size=norm_text_size, key=norm_key, justification="left"))
    if reset_key is not None:
        row.append(sg.Button("Reset", key=reset_key, size=reset_button_size,
                             tooltip=f"Reset {label} to default"))
    return row


# ------------------------------------------------------------------ #
# Keyboard binding                                                   #
# ------------------------------------------------------------------ #

def bind_keyboard_events(window: sg.Window, pairs: list[SliderSpinConfig]):
    """Bind <Return>/<KP_Enter>/<Left>/<Right>/step on all slider/spin pairs."""
    for pair in pairs:
        try:
            window[pair.spin_key].bind("<Return>", "+ENTER")
            window[pair.spin_key].bind("<KP_Enter>", "+ENTER")
            window[pair.spin_key].Widget.configure(
                command=lambda wk=window, sk=pair.spin_key: wk.write_event_value(f"{sk}+STEP", None)
            )
        except Exception:
            pass
        try:
            sw = window[pair.slider_key].Widget
            sw.configure(takefocus=1)
            sw.bind(
                "<Button-1>",
                lambda e, w=sw: w.focus_set(),
                add="+",
            )
            sw.bind(
                "<Left>",
                lambda e, wk=window, sk=pair.slider_key: wk.write_event_value(f"{sk}+LEFT", None),
            )
            sw.bind(
                "<Right>",
                lambda e, wk=window, sk=pair.slider_key: wk.write_event_value(f"{sk}+RIGHT", None),
            )
        except Exception:
            pass


# ------------------------------------------------------------------ #
# Event dispatch                                                     #
# ------------------------------------------------------------------ #

def handle_keyboard_event(
    event: str,
    values: dict,
    window: sg.Window,
    pairs: list[SliderSpinConfig],
) -> bool:
    """Handle +LEFT/+RIGHT/+STEP/+ENTER suffix events and reset button clicks.

    Returns True if the event was consumed, False otherwise.
    """
    # Reset button clicks
    reset_map = {p.reset_key: p for p in pairs if p.reset_key}
    if event in reset_map:
        pair = reset_map[event]
        window[pair.slider_key].update(value=pair.def_val)
        spin_display = str(pair.def_val) if pair.step < 1 else int(pair.def_val)
        window[pair.spin_key].update(value=spin_display)
        values[pair.slider_key] = pair.def_val
        values[pair.spin_key] = spin_display
        _sync_norm(window, values, pair)
        return True

    if "+" not in event:
        return False

    slider_map = {p.slider_key: p for p in pairs}
    spin_map   = {p.spin_key: p for p in pairs}

    event_key, _, suffix = event.rpartition("+")

    if event_key in slider_map and suffix in ("LEFT", "RIGHT"):
        delta = -1 if suffix == "LEFT" else 1
        _step_slider(window, values, event_key, delta, slider_map[event_key])
        return True

    if event_key in spin_map and suffix in ("STEP", "ENTER"):
        _commit_spin(window, values, event_key, spin_map[event_key])
        return True

    return False


def _step_slider(
    window: sg.Window,
    values: dict,
    slider_key: str,
    delta: int,
    config: SliderSpinConfig,
):
    """Step slider value by delta*step, clamp, and sync spinbox."""
    cur = float(values.get(slider_key, 0))
    val = cur + delta * config.step
    val = max(config.min_val, min(config.max_val, val))
    if config.step >= 1:
        val = int(round(val))
    window[slider_key].update(value=val)
    spin_display = str(val) if config.step < 1 else val
    window[config.spin_key].update(value=spin_display)
    values[slider_key] = val
    values[config.spin_key] = spin_display
    _sync_norm(window, values, config)


def _commit_spin(
    window: sg.Window,
    values: dict,
    spin_key: str,
    config: SliderSpinConfig,
):
    """Read spin value and commit to slider."""
    try:
        val = float(values.get(spin_key, 0))
    except (ValueError, TypeError):
        return
    val = max(config.min_val, min(config.max_val, val))
    if config.step >= 1:
        val = int(round(val))
    window[config.slider_key].update(value=val)
    values[config.slider_key] = val
    _sync_norm(window, values, config)


# ------------------------------------------------------------------ #
# Norm sync helpers                                                  #
# ------------------------------------------------------------------ #

def _sync_norm(window: sg.Window, values: dict, config: SliderSpinConfig):
    """Update norm label Text widget if norm_key and norm_func are configured."""
    if config.norm_key is None or config.norm_func is None:
        return
    raw_val = values.get(config.slider_key, config.def_val)
    try:
        norm_val = config.norm_func(float(raw_val), values)
    except Exception:
        return
    window[config.norm_key].update(value=norm_val)


def sync_all_norms(window: sg.Window, values: dict, pairs: list[SliderSpinConfig]):
    """Refresh all norm labels for the given pairs."""
    for pair in pairs:
        _sync_norm(window, values, pair)


# ------------------------------------------------------------------ #
# Direct-event sync helpers                                          #
# ------------------------------------------------------------------ #

def sync_slider_to_spin(window: sg.Window, values: dict,
                        slider_key: str, spin_key: str, step: float = 1.0,
                        config: SliderSpinConfig = None):
    """When slider value changes directly (drag), update spinbox and optional norm."""
    cur = values.get(slider_key, 0)
    if step >= 1:
        cur = int(round(float(cur)))
    display_val = str(cur) if step < 1 else cur
    window[spin_key].update(value=display_val)
    values[spin_key] = display_val
    if config is not None:
        _sync_norm(window, values, config)


def sync_spin_to_slider(window: sg.Window, values: dict,
                        spin_key: str, slider_key: str,
                        config: SliderSpinConfig = None):
    """When spin value changes directly, update slider and optional norm."""
    try:
        val = float(values.get(spin_key, 0))
    except (ValueError, TypeError):
        return
    window[slider_key].update(value=val)
    values[slider_key] = val
    if config is not None:
        _sync_norm(window, values, config)

"""
Shared slider+spin keyboard binding and event dispatch utilities.
"""

from __future__ import annotations
from collections import namedtuple

import PySimpleGUI as sg

# ------------------------------------------------------------------ #
# SliderSpinConfig                                                   #
# ------------------------------------------------------------------ #

SliderSpinConfig = namedtuple(
    "SliderSpinConfig",
    ["spin_key", "slider_key", "min_val", "max_val", "def_val", "step"],
    defaults=(None, 1),
)

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
    """Handle +LEFT/+RIGHT/+STEP/+ENTER suffix events for slider/spin pairs.

    Returns True if the event was consumed, False otherwise.
    """
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
    values[slider_key] = val


# ------------------------------------------------------------------ #
# Direct-event sync helpers                                          #
# ------------------------------------------------------------------ #

def sync_slider_to_spin(window: sg.Window, values: dict,
                        slider_key: str, spin_key: str, step: float = 1.0):
    """When slider value changes directly (drag), update spinbox."""
    cur = values.get(slider_key, 0)
    if step >= 1:
        cur = int(round(float(cur)))
    display_val = str(cur) if step < 1 else cur
    window[spin_key].update(value=display_val)
    values[spin_key] = display_val


def sync_spin_to_slider(window: sg.Window, values: dict,
                        spin_key: str, slider_key: str):
    """When spin value changes directly, update slider."""
    try:
        val = float(values.get(spin_key, 0))
    except (ValueError, TypeError):
        return
    window[slider_key].update(value=val)
    values[slider_key] = val

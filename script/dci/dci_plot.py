"""
Matplotlib-based chart builders for DCI audit data.

Produces curve comparison charts, histogram plots, and metric
summaries suitable for embedding in the PySimpleGUI UI.
"""

from io import BytesIO
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for embedding
import matplotlib.pyplot as plt
import numpy as np


def build_curve_series(curves: dict) -> list:
    """Extract standard curve series from a curves dictionary.

    The expected keys in the curves object are:
      g_cf, g_he, g_cf_he, g_bws, global_lut

    Returns:
        List of (name, numpy_array) tuples for every available curve.
    """
    names = ["g_cf", "g_he", "g_cf_he", "g_bws", "global_lut"]
    return [
        (name, np.asarray(curves[name], dtype=np.float32))
        for name in names
        if name in curves
    ]


def render_curve_figure(
    series: list, title: str = "Global Curve Comparison"
) -> Optional[bytes]:
    """Render a multi-curve comparison chart.

    Args:
        series: List of (name, values) tuples.
        title:  Chart title.

    Returns:
        PNG bytes suitable for embedding in PySimpleGUI, or None if empty.
    """
    if not series:
        return None

    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    for name, values in series:
        ax.plot(values, label=name, linewidth=1.2)

    ax.set_title(title)
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Value")
    ax.legend(fontsize=8, loc="best")
    ax.grid(True, alpha=0.3)

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def render_histogram_figure(
    hists: dict, title: str = "Histogram"
) -> Optional[bytes]:
    """Render histogram data as a bar chart.

    Args:
        hists: Dictionary of histogram arrays (keyed by name).
        title: Chart title.

    Returns:
        PNG bytes, or None if empty.
    """
    if not hists:
        return None

    fig, axes = plt.subplots(
        1, len(hists), figsize=(3 * len(hists), 3), dpi=100, squeeze=False
    )
    axes = axes[0]

    for idx, (name, values) in enumerate(hists.items()):
        ax = axes[idx]
        arr = np.asarray(values, dtype=np.float32)
        ax.bar(range(len(arr)), arr, width=1.0)
        ax.set_title(name, fontsize=8)
        ax.set_xlabel("Bin")
        ax.set_ylabel("Count")

    fig.suptitle(title)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def render_simulated_preview_figure(
    images: dict, title: str = "LUT Simulation Preview"
) -> Optional[bytes]:
    """Render side-by-side simulated image previews.

    Args:
        images: Dict mapping label -> 2-D numpy array (float32, normalised 0-1).
        title:  Figure title.

    Returns:
        PNG bytes, or None if empty.
    """
    if not images:
        return None

    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=(3 * n, 3), dpi=100, squeeze=False)
    axes = axes[0]

    for idx, (label, img) in enumerate(images.items()):
        ax = axes[idx]
        ax.imshow(img, cmap="gray", vmin=0, vmax=1)
        ax.set_title(label, fontsize=8)
        ax.axis("off")

    fig.suptitle(title)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()

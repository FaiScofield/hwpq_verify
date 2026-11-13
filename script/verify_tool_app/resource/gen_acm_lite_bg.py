"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : gen_acm_lite_bg.py
Description : Generate the ACM_LITE delta-chart background images.

The Lite path runs in HSV with a 0..360 deg hue axis, so the backgrounds use
the same semantics as the runtime pipeline:

  * Delta Y: V is offset additively around 0.5 (top = +1, bottom = -1)
  * Delta S: S is scaled multiplicatively (top = +100%, bottom = 0%)
  * Delta H: hue is rotated by +/-96 deg (top = +96, bottom = -96)

Horizontal axis is the source hue (0..360 deg, closed at both ends), matching
the point-based hue table used by AcmImplHwRkLite.
"""

import os

import cv2
import numpy as np


WIDTH = 480
HEIGHT = 270
DELTA_H_DEG = 96.0


def _hsv_to_bgr(hue_deg: np.ndarray, sat: np.ndarray, val: np.ndarray) -> np.ndarray:
    """Convert HSV arrays (hue in degrees, S/V in 0..1) to a BGR uint8 image."""
    hsv = np.stack([
        np.mod(hue_deg, 360.0) / 2.0,   # OpenCV hue range is 0..179
        sat * 255.0,
        val * 255.0,
    ], axis=-1)
    hsv = np.clip(np.rint(hsv), 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def _hue_axis() -> np.ndarray:
    """Return a [H, W] hue grid covering 0..360 deg with identical end points."""
    hue = np.linspace(0.0, 360.0, WIDTH, dtype=np.float32)[None, :]
    return np.repeat(hue, HEIGHT, axis=0)


def generate_delta_y() -> np.ndarray:
    """Build the Delta Y background: additive V offset around the mid level."""
    hue = _hue_axis()
    delta_v = np.linspace(1.0, -1.0, HEIGHT, dtype=np.float32)[:, None]
    val = np.clip(0.5 + 0.5 * delta_v, 0.0, 1.0)
    val = np.repeat(val, WIDTH, axis=1)
    sat = np.ones_like(val)
    return _hsv_to_bgr(hue, sat, val)


def generate_delta_s() -> np.ndarray:
    """Build the Delta S background: multiplicative S scaling around 0.5."""
    hue = _hue_axis()
    delta_s = np.linspace(1.0, -1.0, HEIGHT, dtype=np.float32)[:, None]
    sat = np.clip(0.5 * (1.0 + delta_s), 0.0, 1.0)
    sat = np.repeat(sat, WIDTH, axis=1)
    val = np.ones_like(sat)
    return _hsv_to_bgr(hue, sat, val)


def generate_delta_h() -> np.ndarray:
    """Build the Delta H background: hue rotated by +/-96 deg."""
    hue = _hue_axis()
    delta_h = np.linspace(DELTA_H_DEG, -DELTA_H_DEG, HEIGHT, dtype=np.float32)[:, None]
    out_hue = np.mod(hue + delta_h, 360.0)
    sat = np.ones_like(out_hue)
    val = np.ones_like(out_hue)
    return _hsv_to_bgr(out_hue, sat, val)


def main() -> None:
    """Generate the three Lite background images into the resource folder."""
    out_dir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "verify_tool_app", "resource"))
    os.makedirs(out_dir, exist_ok=True)
    for name, image in (
        ("Lite_Y_deltaImg.bmp", generate_delta_y()),
        ("Lite_S_deltaImg.bmp", generate_delta_s()),
        ("Lite_H_deltaImg.bmp", generate_delta_h()),
    ):
        path = os.path.join(out_dir, name)
        cv2.imwrite(path, image)
        print(f"[BG] wrote {path} ({image.shape[1]}x{image.shape[0]})")


if __name__ == "__main__":
    main()

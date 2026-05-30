"""
Python-side LUT simulation for DCI audit visualisation.

Consumes exported LUTs and metadata from the audit working set and
synthesises image previews without calling the native library again.

Simulation types:
  - Single global curve previews (G_CF, G_HE, G_BWS)
  - Pairwise global curve combinations (e.g. G_CF → G_HE)
  - All-global combination
  - Local-only preview
  - Global + local fused preview
"""

import numpy as np
from typing import Optional


def sample_lut_linear(
    lut: np.ndarray, x: np.ndarray, domain_max: int = 1023
) -> np.ndarray:
    """Linearly interpolate a 1-D LUT over a domain of [0, domain_max].

    Args:
        lut:        1-D numpy array of LUT sample values.
        x:          1-D or 2-D array of input indices (integer-valued).
        domain_max: Maximum index the LUT is defined for.

    Returns:
        Interpolated values with the same shape as x, dtype float32.
    """
    xp = np.linspace(0.0, float(domain_max), num=len(lut), dtype=np.float32)
    return np.interp(x.astype(np.float32), xp, lut.astype(np.float32)).astype(
        np.float32
    )


def simulate_global_only(y_plane: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Apply a single global LUT to a Y-plane.

    Args:
        y_plane: 2-D array of Y-channel pixel values (10-bit, 0-1023).
        lut:     1-D global LUT.

    Returns:
        2-D float32 array of mapped values.
    """
    return sample_lut_linear(lut, y_plane)


def simulate_global_pair(
    y_plane: np.ndarray, lut_a: np.ndarray, lut_b: np.ndarray
) -> np.ndarray:
    """Apply two global LUTs in sequence (A then B).

    Args:
        y_plane: 2-D array of Y-channel pixel values (10-bit, 0-1023).
        lut_a:   First LUT (e.g. G_CF).
        lut_b:   Second LUT (e.g. G_HE).

    Returns:
        2-D float32 array after both LUTs applied.
    """
    mid = sample_lut_linear(lut_a, y_plane)
    return sample_lut_linear(lut_b, mid)


def fuse_global_local(
    global_y: np.ndarray,
    local_y: np.ndarray,
    local_ratio_map: np.ndarray,
    ratio_scale: float = 32.0,
) -> np.ndarray:
    """Blend global and local results using the per-block local ratio map.

    Closer to 1.0 means more local contribution.

    Args:
        global_y:        2-D float32 global-only result.
        local_y:         2-D float32 local-only result.
        local_ratio_map: 2-D integer ratio map (exported per-block).
        ratio_scale:     Normaliser for ratio values.

    Returns:
        2-D float32 blended image.
    """
    alpha = np.clip(local_ratio_map.astype(np.float32) / ratio_scale, 0.0, 1.0)
    return (1.0 - alpha) * global_y + alpha * local_y


def simulate_local_only(
    y_plane: np.ndarray,
    local_lut: np.ndarray,
    block_h: int,
    block_w: int,
) -> np.ndarray:
    """Apply per-block local LUTs to a Y-plane.

    Args:
        y_plane:   2-D array of Y-channel pixel values (H x W).
        local_lut: 3-D array (num_blocks, lut_size) of per-block LUTs.
        block_h:   Block height in pixels.
        block_w:   Block width in pixels.

    Returns:
        2-D float32 array of locally-mapped values.
    """
    h, w = y_plane.shape
    num_blocks = local_lut.shape[0]
    result = np.zeros_like(y_plane, dtype=np.float32)

    # Determine grid dimensions
    grid_cols = (w + block_w - 1) // block_w
    grid_rows = (h + block_h - 1) // block_h

    for bi in range(min(num_blocks, grid_rows * grid_cols)):
        row = bi // grid_cols
        col = bi % grid_cols
        y0 = row * block_h
        y1 = min(y0 + block_h, h)
        x0 = col * block_w
        x1 = min(x0 + block_w, w)
        block_pixels = y_plane[y0:y1, x0:x1]
        result[y0:y1, x0:x1] = sample_lut_linear(local_lut[bi], block_pixels)

    return result

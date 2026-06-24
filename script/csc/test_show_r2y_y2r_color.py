import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from get_csc_coefs import (
    g_r2y_mat_bt601,
    g_y2r_mat_bt601,
    g_r2y_mat_bt709,
    g_y2r_mat_bt709,
    g_r2y_mat_bt2020,
    g_y2r_mat_bt2020
)

_CSC_MATRICES = {
    "bt601": (g_r2y_mat_bt601, g_y2r_mat_bt601),
    "bt709": (g_r2y_mat_bt709, g_y2r_mat_bt709),
    "bt2020": (g_r2y_mat_bt2020, g_y2r_mat_bt2020),
}


def _get_csc_matrices(colorspace: str):
    """Return RGB<->YUV matrices for the requested colorspace."""
    key = colorspace.lower()
    if key not in _CSC_MATRICES:
        raise ValueError(f"Unsupported colorspace: {colorspace}. Expected one of {tuple(_CSC_MATRICES)}")
    return _CSC_MATRICES[key]


def _sample_axis(step: int) -> np.ndarray:
    """Build a sampling axis in [0, 255] while ensuring the endpoint is included."""
    if step <= 0:
        raise ValueError(f"step must be > 0, got {step}")
    axis = np.arange(0, 256, step, dtype=np.float32)
    if axis.size == 0 or axis[-1] != 255:
        axis = np.append(axis, 255.0)
    return axis


def _downsample_indices(count: int, max_points: int = 60000) -> np.ndarray:
    """Return evenly spaced indices so the scatter plot stays responsive."""
    if count <= max_points:
        return np.arange(count, dtype=np.int32)
    stride = int(np.ceil(count / max_points))
    return np.arange(0, count, stride, dtype=np.int32)


def _convex_hull_2d(points: np.ndarray) -> np.ndarray:
    """Compute the 2D convex hull using the monotonic chain algorithm."""
    if points.shape[0] <= 1:
        return points

    pts = np.unique(points.astype(np.float32), axis=0)
    if pts.shape[0] <= 2:
        return pts

    pts = pts[np.lexsort((pts[:, 1], pts[:, 0]))]

    def cross(o, a, b) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    hull = np.array(lower[:-1] + upper[:-1], dtype=np.float32)
    return hull


def _print_right_vertex_angle(hull_points: np.ndarray):
    """Print and return the right-most projected vertex and its angle relative to the +Cb axis."""
    if hull_points.shape[0] == 0:
        print("Projection hull is empty, cannot measure the right vertex angle.")
        return None, None

    right_vertex = hull_points[np.argmax(hull_points[:, 0])]
    angle_deg = float(np.degrees(np.arctan2(right_vertex[1], right_vertex[0])))
    print(
        "Projection right vertex: "
        f"(Cb={right_vertex[0]:.3f}, Cr={right_vertex[1]:.3f}), "
        f"angle_to_cb_axis={angle_deg:.3f} deg"
    )
    return right_vertex, angle_deg


def yuv_to_rgb(y, u, v, colorspace: str = "bt709"):
    """Convert YUV values to RGB using the selected colorspace matrix.

    Input Y is in [0, 255], and U/V use the common stored [0, 255] form.
    """
    _, mat_y2r = _get_csc_matrices(colorspace)
    yuv = np.stack([y, u - 128.0, v - 128.0], axis=-1).astype(np.float32)
    return np.dot(yuv.reshape(-1, 3), mat_y2r.T).reshape(yuv.shape)


def rgb_to_yuv(r, g, b, colorspace: str = "bt709"):
    """Convert RGB values to YUV using the selected colorspace matrix.

    Output Y is in [0, 255], and U/V are returned in stored [0, 255] form.
    """
    mat_r2y, _ = _get_csc_matrices(colorspace)
    rgb = np.stack([r, g, b], axis=-1).astype(np.float32)
    yuv = np.dot(rgb.reshape(-1, 3), mat_r2y.T).reshape(rgb.shape)
    yuv[..., 1:] += 128.0
    return yuv


def show_y2r_mesh_color(yuv, step: int = 2, project: bool = True, colorspace: str = "bt709"):
    if yuv is not None and len(yuv.shape) >= 2 and yuv.shape[-1] == 3:
        y_flat = yuv[..., 0].reshape(-1).astype(np.float32)
        u_flat = yuv[..., 1].reshape(-1).astype(np.float32)
        v_flat = yuv[..., 2].reshape(-1).astype(np.float32)
    else:
        y_vals = _sample_axis(step)
        u_vals = _sample_axis(step)
        v_vals = _sample_axis(step)
        U, V, Y = np.meshgrid(u_vals, v_vals, y_vals, indexing='ij')
        u_flat = U.ravel()
        v_flat = V.ravel()
        y_flat = Y.ravel()

    cb_flat = u_flat - 128.0
    cr_flat = v_flat - 128.0

    # Convert to RGB (full range, possibly outside [0,255]).
    rgb_full = yuv_to_rgb(y_flat, u_flat, v_flat, colorspace=colorspace)
    rgb_clipped = np.clip(rgb_full, 0, 255) / 255.0

    print(f"Colorspace: {colorspace}")
    print("Original RGB range:")
    print(f"R: [{rgb_full[:,0].min():.1f}, {rgb_full[:,0].max():.1f}]")
    print(f"G: [{rgb_full[:,1].min():.1f}, {rgb_full[:,1].max():.1f}]")
    print(f"B: [{rgb_full[:,2].min():.1f}, {rgb_full[:,2].max():.1f}]")

    # Points with any RGB channel outside [0,255] are considered overflow.
    is_overflow = np.any((rgb_full < 0) | (rgb_full > 255), axis=1)
    valid_mask = ~is_overflow
    print(f"Overflow points: {is_overflow.sum()}/{len(is_overflow)} = {is_overflow.sum()/len(is_overflow):.2%}")

    scatter_idx = _downsample_indices(int(valid_mask.sum()))
    valid_cb = cb_flat[valid_mask]
    valid_cr = cr_flat[valid_mask]
    valid_y = y_flat[valid_mask]
    valid_rgb = rgb_clipped[valid_mask]
    if valid_cb.size > scatter_idx.size:
        print(f"Scatter points downsampled: {valid_cb.size} -> {scatter_idx.size}")

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Cb')
    ax.set_ylabel('Cr')
    ax.set_zlabel('Y (Luma)')
    ax.set_xlim(-128, 127)
    ax.set_ylim(-128, 127)
    ax.set_title(f'3D YUV Space Colored by {colorspace.upper()} RGB')
    ax.scatter(
        valid_cb[scatter_idx],
        valid_cr[scatter_idx],
        valid_y[scatter_idx],
        c=valid_rgb[scatter_idx],
        s=2,
        alpha=0.6,
        edgecolors='none',
        depthshade=False,
    )

    if project and valid_cb.size >= 3:
        hull_points = _convex_hull_2d(np.stack([valid_cb, valid_cr], axis=-1))
        if hull_points.shape[0] >= 3:
            right_vertex, angle_deg = _print_right_vertex_angle(hull_points)
            hull_closed = np.vstack([hull_points, hull_points[0]])
            z_project = np.full(hull_closed.shape[0], float(np.min(y_flat)), dtype=np.float32)
            ax.plot(
                hull_closed[:, 0],
                hull_closed[:, 1],
                z_project,
                color='black',
                linewidth=2.0,
                linestyle='-',
                label='Projection Hull',
            )
            if right_vertex is not None:
                z_label = float(np.min(y_flat))
                ax.scatter(
                    [right_vertex[0]],
                    [right_vertex[1]],
                    [z_label],
                    color='red',
                    s=36,
                    depthshade=False,
                    label='Right Vertex',
                )
                ax.text(
                    right_vertex[0] + 4.0,
                    right_vertex[1] + 4.0,
                    z_label,
                    "Right vertex\n"
                    f"(Cb={right_vertex[0]:.1f}, Cr={right_vertex[1]:.1f})\n"
                    f"angle={angle_deg:.2f} deg",
                    color='red',
                    fontsize=9,
                )
            ax.legend(loc='upper right')

    plt.tight_layout()
    plt.show()
    plt.close()

    return rgb_clipped


def show_r2y_mesh_color(rgb, step: int = 2, colorspace: str = "bt709"):
    if rgb is not None and len(rgb.shape) >= 3:
        g_vals = rgb[:, :, 1]
        b_vals = rgb[:, :, 2]
        r_vals = rgb[:, :, 0]
    else:
        g_vals = _sample_axis(step)
        b_vals = _sample_axis(step)
        r_vals = _sample_axis(step)

    # Create meshgrid
    B, R, G = np.meshgrid(b_vals, r_vals, g_vals, indexing='ij')

    # Flatten for scatter plot
    b_flat = B.ravel()
    r_flat = R.ravel()
    g_flat = G.ravel()

    # Convert to YUV (full range, possibly outside [0,255]).
    yuv_full = rgb_to_yuv(r_flat, g_flat, b_flat, colorspace=colorspace)  # shape: (N, 3)
    yuv_clipped = np.clip(yuv_full, 0, 255) / 255.0

    print(f"Colorspace: {colorspace}")
    print("Original YUV range:")
    print(f"Y: [{yuv_full[:,0].min():.1f}, {yuv_full[:,0].max():.1f}]")
    print(f"U: [{yuv_full[:,1].min():.1f}, {yuv_full[:,1].max():.1f}]")
    print(f"V: [{yuv_full[:,2].min():.1f}, {yuv_full[:,2].max():.1f}]")

    # Find points where any channel is out of [0,255]
    is_overflow = np.any((yuv_full < 0) | (yuv_full > 255), axis=1)
    print(f"Overflow points: {is_overflow.sum()}/{len(is_overflow)} = {is_overflow.sum()/len(is_overflow):.2%}")

    # Plot
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('B (Cb)')
    ax.set_ylabel('R (Cr)')
    ax.set_zlabel('G (Luma)')
    ax.set_title(f'3D RGB Space Colored by {colorspace.upper()} YUV')
    ax.scatter(b_flat[~is_overflow], r_flat[~is_overflow], g_flat[~is_overflow],
            c=yuv_clipped[~is_overflow], s=20, alpha=0.8, edgecolors='none')

    # Overlay overflow points with red edge
    # ax.scatter(u_flat[is_overflow], v_flat[is_overflow], y_flat[is_overflow],
    #         c=rgb_clipped[is_overflow], s=10, alpha=0.5, edgecolors='none', linewidth=0.1)

    # Optional: add colorbar? Not meaningful for RGB, so skip.
    plt.tight_layout()
    plt.show()
    plt.close()

    return yuv_clipped

if __name__ == '__main__':
    show_y2r_mesh_color(None, step=1, project=True, colorspace="bt709")
    # show_r2y_mesh_color(None, step=2)

    # step = 4
    # length = 256 // step + 1
    # g_vals = np.linspace(0, 255, length)
    # b_vals = np.linspace(0, 255, length)
    # r_vals = np.linspace(0, 255, length)
    # B, R, G = np.meshgrid(b_vals, r_vals, g_vals, indexing='ij')

    # b_flat = B.ravel()
    # r_flat = R.ravel()
    # g_flat = G.ravel()
    # rgb = np.stack([r_flat, g_flat, b_flat], axis=-1)

    # # Convert to RGB (full range, possibly outside [0,255])
    # yuv_full = rgb_to_yuv_bt709(r_flat, g_flat, b_flat)  # shape: (N, 3)
    # yuv_clipped = np.clip(yuv_full, 0, 255)

    # rgb_full = yuv_to_rgb_bt709(yuv_clipped[:,0], yuv_clipped[:,1], yuv_clipped[:,2])
    # rgb_clipped = np.clip(rgb_full, 0, 255)

    # diff = np.abs(rgb_clipped - rgb).flatten()
    # cnt = np.count_nonzero(diff)

    # print(f"Total difference elements: {cnt}/{len(diff)}={cnt/len(diff):.2%}")
    # print(f"Mean difference: {diff.mean():.2f}")

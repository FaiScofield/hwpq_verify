import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# BT.709 YUV to RGB conversion (Y in [0,255], U/V in [-128,127])
def yuv_to_rgb_bt709(y, u, v):
    cb = u - 128
    cr = v - 128
    r = y + 1.5748 * cr
    g = y - 0.1873 * cb - 0.4681 * cr
    b = y + 1.8556 * cb
    return np.stack([r, g, b], axis=-1)  # shape: (..., 3)

def rgb_to_yuv_bt709(r, g, b):
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    u = -0.114572 * r - 0.385428 * g + 0.5 * b + 128
    v = 0.5 * r - 0.454153 * g - 0.045847 * b + 128
    return np.stack([y, u, v], axis=-1)  # shape: (..., 3)

def show_y2r_mesh_color(yuv, step: int = 2):
    if yuv is not None and len(yuv.shape) == 3:
        y_vals = yuv[:, :, 0]
        u_vals = yuv[:, :, 1]
        v_vals = yuv[:, :, 2]
    else:
        length = 256 // step + 1
        y_vals = np.linspace(0, 255, length)
        u_vals = np.linspace(0, 255, length)
        v_vals = np.linspace(0, 255, length)

    # Create meshgrid
    U, V, Y = np.meshgrid(u_vals, v_vals, y_vals, indexing='ij')

    # Flatten for scatter plot
    u_flat = U.ravel()
    v_flat = V.ravel()
    y_flat = Y.ravel()

    # Convert to RGB (full range, possibly outside [0,255])
    rgb_full = yuv_to_rgb_bt709(y_flat, u_flat, v_flat)  # shape: (N, 3)
    rgb_clipped = np.clip(rgb_full, 0, 255) / 255.0

    # You still have `rgb_full` with unclipped values!
    print("Original RGB range:")
    print(f"R: [{rgb_full[:,0].min():.1f}, {rgb_full[:,0].max():.1f}]")
    print(f"G: [{rgb_full[:,1].min():.1f}, {rgb_full[:,1].max():.1f}]")
    print(f"B: [{rgb_full[:,2].min():.1f}, {rgb_full[:,2].max():.1f}]")

    # Find points where any channel is out of [0,255]
    is_overflow = np.any((rgb_full < 0) | (rgb_full > 255), axis=1)
    print(f"Overflow points: {is_overflow.sum()}/{len(is_overflow)} = {is_overflow.sum()/len(is_overflow):.2%}")

    # Plot
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('U (Cb)')
    ax.set_ylabel('V (Cr)')
    ax.set_zlabel('Y (Luma)')
    ax.set_title('3D YUV Space Colored by BT.709 RGB (Clipped for Display)')
    ax.scatter(u_flat[~is_overflow], v_flat[~is_overflow], y_flat[~is_overflow],
            c=rgb_clipped[~is_overflow], s=20, alpha=0.8, edgecolors='none')

    # Overlay overflow points with red edge
    # ax.scatter(u_flat[is_overflow], v_flat[is_overflow], y_flat[is_overflow],
    #         c=rgb_clipped[is_overflow], s=10, alpha=0.5, edgecolors='none', linewidth=0.1)

    # Optional: add colorbar? Not meaningful for RGB, so skip.
    plt.tight_layout()
    plt.show()
    plt.close()

    return rgb_clipped

def show_r2y_mesh_color(rgb, step: int = 2):
    if rgb is not None and len(rgb.shape) >= 3:
        g_vals = rgb[:, :, 1]
        b_vals = rgb[:, :, 2]
        r_vals = rgb[:, :, 0]
    else:
        length = 256 // step + 1
        g_vals = np.linspace(0, 255, length)
        b_vals = np.linspace(0, 255, length)
        r_vals = np.linspace(0, 255, length)

    # Create meshgrid
    B, R, G = np.meshgrid(b_vals, r_vals, g_vals, indexing='ij')

    # Flatten for scatter plot
    b_flat = B.ravel()
    r_flat = R.ravel()
    g_flat = G.ravel()

    # Convert to RGB (full range, possibly outside [0,255])
    yuv_full = rgb_to_yuv_bt709(r_flat, g_flat, b_flat)  # shape: (N, 3)
    yuv_clipped = np.clip(yuv_full, 0, 255) / 255.0

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
    ax.set_title('3D YUV Space Colored by BT.709 RGB')
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
    show_y2r_mesh_color(None, step=2)
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
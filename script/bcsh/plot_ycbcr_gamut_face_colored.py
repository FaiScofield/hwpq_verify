# -*- coding: utf-8 -*-
"""按 RGB 立方体面着色/标注的色域边界（BT.709，Y=0.2/0.5/0.8）：
每段标注 R/G/B 通道 + 亮(=1)/暗(=0) 边界，每段对应哪张面一目了然。

运行: python plot_ycbcr_gamut_face_colored.py
输出: ycbcr_gamut_face_colored_Y*.png
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

# 注册 Windows 中文字体，避免 亮/暗 等 CJK 标注渲染为方框
for _fp in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simsun.ttc"):
    try:
        fm.fontManager.addfont(_fp)
        plt.rcParams["font.sans-serif"] = [fm.FontProperties(fname=_fp).get_name(),
                                            "DejaVu Sans"]
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

Y2R = np.array([[1.0, 0.0, 1.5748],
                [1.0, -0.187324, -0.468124],
                [1.0, 1.8556, 0.0]], dtype=float)
R2Y = np.linalg.inv(Y2R)

N = 1201
cb = np.linspace(-0.66, 0.66, N)
cr = np.linspace(-0.66, 0.66, N)
Cb, Cr = np.meshgrid(cb, cr)

# 亮侧（通道=1）浅色系，暗侧（通道=0）深色系
face_colors = {
    "R=0": "#b2182b", "R=1": "#f4a582",
    "G=0": "#4dac26", "G=1": "#a6d96a",
    "B=0": "#2166ac", "B=1": "#92c5de",
}
face_label = {"R=0": "R=0 暗", "R=1": "R=1 亮",
              "G=0": "G=0 暗", "G=1": "G=1 亮",
              "B=0": "B=0 暗", "B=1": "B=1 亮"}


def face_of_rgb(rgb):
    """返回该 RGB 点被钉在边界的通道面（通道=0 或 1）。"""
    lab = []
    if np.isclose(rgb[0], 0, atol=1e-6): lab.append("R=0")
    if np.isclose(rgb[1], 0, atol=1e-6): lab.append("G=0")
    if np.isclose(rgb[2], 0, atol=1e-6): lab.append("B=0")
    if np.isclose(rgb[0], 1, atol=1e-6): lab.append("R=1")
    if np.isclose(rgb[1], 1, atol=1e-6): lab.append("G=1")
    if np.isclose(rgb[2], 1, atol=1e-6): lab.append("B=1")
    return lab

# ---- luma 平面与立方体棱的交点（色域多边形顶点） ----
w = R2Y[0]
cube = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                 [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], float)
edges = [(i, j) for i in range(8) for j in range(i + 1, 8)
         if (cube[i] != cube[j]).sum() == 1]

def plot_gamut_face(Y: float, contour_extended: bool = False) -> None:
    """绘制固定 luma Y 的 (Cb,Cr) 色度平面：真实 RGB 渲染 + 面着色边界 + V/S 等高线。

    contour_extended=True 时，V/S 等高线在整个 Cb-Cr 平面绘制（可越过色域边界，
    但始终在 Cb-Cr 坐标系范围内；V 可超过 1 的亮侧过冲区、S 可超过 1 的 min<0 区），
    False 时仅在色域内绘制等高线。
    """
    R = Y + Y2R[0, 1] * Cb + Y2R[0, 2] * Cr
    G = Y + Y2R[1, 1] * Cb + Y2R[1, 2] * Cr
    B = Y + Y2R[2, 1] * Cb + Y2R[2, 2] * Cr
    mx = np.maximum(np.maximum(R, G), B)
    mn = np.minimum(np.minimum(R, G), B)
    in_g = (mn >= -1e-9) & (mx <= 1 + 1e-9)
    S = np.divide(mx - mn, mx, out=np.zeros_like(mx), where=mx > 0)
    S = np.where(mx > 0, S, np.nan)      # max<=0（全黑）无定义

    # 色域多边形顶点（luma 平面与立方体棱的交点）
    verts = []
    for (i, j) in edges:
        u, v = cube[i], cube[j]
        lu, lv = w @ u, w @ v
        if (lu - Y) * (lv - Y) < 0:
            t = (Y - lu) / (lv - lu)
            verts.append(u + t * (v - u))
    verts = np.array(verts)
    cen = verts.mean(axis=0)
    order = np.argsort(np.arctan2(verts[:, 2] - cen[2], verts[:, 1] - cen[1]))
    verts = verts[order]
    Vcc = np.array([R2Y[1:] @ v for v in verts])   # 顶点 (Cb, Cr)

    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=110)
    # 边界内渲染真实 RGB 颜色：RGB = Y + a*Cb + b*Cr（域内直接显示，域外浅灰）
    rgb_img = np.clip(np.stack([R, G, B], axis=-1), 0.0, 1.0)
    rgb_img = np.where(in_g[..., None], rgb_img, np.array([0.91, 0.91, 0.91]))
    ax.imshow(rgb_img, extent=(cb[0], cb[-1], cr[0], cr[-1]), origin="lower", zorder=0)

    # V / S 等高线：V=黑虚线，S=橙实线
    s_levels = [0.25, 0.5, 0.75, 1.0]
    if Y == 0.2:
        v_levels = [0.3, 0.5, 0.7, 0.9, 1.0]
    elif Y == 0.5:
        v_levels = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    else:   # Y == 0.8，V>=0.8 加密高端
        v_levels = [0.8, 0.85, 0.9, 0.95, 1.0]
    if contour_extended:
        # 延伸：等高线跨过色域边界绘制（S/V 均限制在 <=1，不画 >1 的越界线）
        S_plot = S                     # 全平面
        V_plot = mx                    # 全平面（max 恒良定义）
    else:
        S_plot = np.where(in_g, S, np.nan)
        V_plot = np.where(in_g, mx, np.nan)

    Sc = ax.contour(Cb, Cr, S_plot, levels=s_levels, colors="orange",
                    linestyles="-", linewidths=1.1, zorder=2)
    ax.clabel(Sc, fmt={l: f"S={l:.2f}" for l in s_levels}, fontsize=8)
    Vc = ax.contour(Cb, Cr, V_plot, levels=v_levels, colors="black",
                    linestyles="--", linewidths=1.0, zorder=2)
    ax.clabel(Vc, fmt={l: f"V={l:.1f}" for l in v_levels}, fontsize=8)

    # 每条边按所在立方体面着色并标注（R/G/B + 亮/暗）
    n = len(Vcc)
    for i in range(n):
        p0, p1 = Vcc[i], Vcc[(i + 1) % n]
        mid_rgb = (verts[i] + verts[(i + 1) % n]) / 2
        faces = face_of_rgb(mid_rgb)
        face = faces[0] if faces else "?"
        col = face_colors.get(face, "k")
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=col, lw=6,
                solid_capstyle="round", zorder=3)
        mcc = (p0 + p1) / 2
        ax.annotate(face_label.get(face, face), (mcc[0], mcc[1]), color="k",
                    fontsize=11, weight="bold", ha="center", va="center", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=col, lw=1.5))

    ax.plot(Vcc[:, 0], Vcc[:, 1], "ko", ms=5, zorder=5)
    ax.plot(0, 0, "k+", ms=10)
    ax.annotate("gray (S=0)", (0, 0), textcoords="offset points", xytext=(8, -16), fontsize=9)

    ax.set_xlabel("Cb")
    ax.set_ylabel("Cr")
    mode = "extended" if contour_extended else "inside-gamut"
    ax.set_title(f"YCbCr(BT.709) Y={Y:.1f}: gamut boundary by cube face ({n}-sided)\n"
                 f"亮=通道=1(浅色)，暗=通道=0(深色)；V/S 等高线 [{mode}]")
    ax.set_aspect("equal")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    out = rf"g:\Codes\gerrit_projects\hwpq_verify\output\ycbcr_gamut_face_colored_Y{Y:.1f}.png"
    fig.savefig(out)
    print("saved:", out)


if __name__ == "__main__":
    extended = "--extended" in sys.argv[1:]
    for _y in (0.2, 0.5, 0.8):
        plot_gamut_face(_y, contour_extended=extended)

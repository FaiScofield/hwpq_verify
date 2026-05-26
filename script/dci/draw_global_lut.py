import argparse
import re
import struct
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LUT_LINE_PATTERN = re.compile(r"global\s+lut\[(\d+)\]\s*=\s*(-?\d+)", re.IGNORECASE)
GLOBAL_HIST_BIN_COUNT = 256
GLOBAL_HIST_BIN_BYTES = 4


def ensure_path(path_value):
    """Convert a path-like input to a Path object."""
    if path_value is None:
        return None
    return Path(path_value)


def parse_args():
    """Parse command line arguments for LUT plotting."""
    parser = argparse.ArgumentParser(description="Draw DCI global LUT and/or global histogram figure")
    parser.add_argument("-gl", "--global_lut", dest="global_lut_file", default=None, help="input global LUT text file")
    parser.add_argument("-gh", "--global_hist", dest="global_hist_file", default=None, help="input global histogram binary file")
    parser.add_argument("-o", "--output", dest="output_file", default=None, help="output PNG file")
    args = parser.parse_args()
    if not args.global_lut_file and not args.global_hist_file:
        parser.error("at least one of -gl/--global_lut or -gh/--global_hist must be specified")
    return args


def parse_global_lut_file(input_path):
    """Parse LUT entries from a text file."""
    input_path = ensure_path(input_path)
    lut_map = {}
    with input_path.open("r", encoding="utf-8") as file_obj:
        for line_no, line in enumerate(file_obj, start=1):
            match = LUT_LINE_PATTERN.search(line)
            if not match:
                continue

            lut_idx = int(match.group(1))
            lut_val = int(match.group(2))
            lut_map[lut_idx] = lut_val

    if not lut_map:
        raise ValueError(f"no valid global LUT entries found in '{input_path}'")

    sorted_items = sorted(lut_map.items())
    x_values = [item[0] for item in sorted_items]
    y_values = [item[1] for item in sorted_items]
    return x_values, y_values


def parse_global_hist_file(input_path):
    """Parse a 256-bin uint32 global histogram binary file."""
    input_path = ensure_path(input_path)
    expected_size = GLOBAL_HIST_BIN_COUNT * GLOBAL_HIST_BIN_BYTES
    data = input_path.read_bytes()
    if len(data) != expected_size:
        raise ValueError(
            f"invalid global histogram file size: {len(data)} bytes, expected {expected_size} bytes"
        )

    hist_values = struct.unpack(f"<{GLOBAL_HIST_BIN_COUNT}I", data)
    x_values = list(range(GLOBAL_HIST_BIN_COUNT))
    y_values = list(hist_values)
    return x_values, y_values


def build_output_path(global_lut_path, global_hist_path, output_arg):
    """Build the output PNG path."""
    global_lut_path = ensure_path(global_lut_path)
    global_hist_path = ensure_path(global_hist_path)
    if output_arg:
        output_path = ensure_path(output_arg)
    elif global_lut_path and global_hist_path:
        output_path = global_lut_path.parent / "dci_global_lut_hist.png"
    elif global_lut_path:
        output_path = global_lut_path.with_suffix(".png")
    else:
        output_path = global_hist_path.with_suffix(".png")

    if output_path.suffix.lower() != ".png":
        output_path = output_path.with_suffix(".png")
    return output_path


def prepare_figure(output_path):
    """Prepare the figure canvas and output directory."""
    output_path = ensure_path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 6), dpi=150)


def draw_identity_reference(axis_obj, x_values, scale=1):
    """Draw a dashed y=scale*x reference line for LUT comparison."""
    ref_y_values = [scale * value for value in x_values]
    axis_obj.plot(x_values, ref_y_values, color="tab:gray", linewidth=1.0, linestyle="--", alpha=0.8)


def draw_global_lut_curve(x_values, y_values, input_path, output_path):
    """Draw and save the LUT curve figure."""
    input_path = ensure_path(input_path)
    output_path = ensure_path(output_path)
    prepare_figure(output_path)
    draw_identity_reference(plt.gca(), x_values, scale=4)
    plt.plot(x_values, y_values, color="tab:blue", linewidth=1.5, marker="o", markersize=2.5)
    plt.title(f"DCI Global LUT Curve\n{input_path.name}")
    plt.xlabel("LUT Index")
    plt.ylabel("LUT Value")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.xlim(min(x_values), max(x_values))
    plt.tight_layout()
    plt.savefig(output_path, format="png")
    plt.close()


def draw_global_histogram(x_values, y_values, input_path, output_path):
    """Draw and save the global histogram figure."""
    input_path = ensure_path(input_path)
    output_path = ensure_path(output_path)
    prepare_figure(output_path)
    plt.bar(x_values, y_values, width=0.9, color="tab:orange", edgecolor="tab:orange", linewidth=0.2)
    plt.title(f"DCI Global Histogram\n{input_path.name}")
    plt.xlabel("Histogram Bin")
    plt.ylabel("Count")
    plt.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
    plt.xlim(min(x_values), max(x_values))
    plt.tight_layout()
    plt.savefig(output_path, format="png")
    plt.close()


def draw_combined_plot(global_lut_path, global_hist_path, output_path):
    """Draw global LUT and global histogram on a shared x-axis with dual y-axes."""
    global_lut_path = ensure_path(global_lut_path)
    global_hist_path = ensure_path(global_hist_path)
    output_path = ensure_path(output_path)
    lut_x, lut_y = parse_global_lut_file(global_lut_path)
    hist_x, hist_y = parse_global_hist_file(global_hist_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax_lut = plt.subplots(figsize=(12, 6), dpi=150)
    ax_hist = ax_lut.twinx()
    draw_identity_reference(ax_lut, lut_x, scale=4)

    lut_line = ax_lut.plot(
        lut_x,
        lut_y,
        color="tab:blue",
        linewidth=1.5,
        marker="o",
        markersize=2.5,
        label="Global LUT",
    )[0]
    hist_bar = ax_hist.bar(
        hist_x,
        hist_y,
        width=0.9,
        color="tab:orange",
        edgecolor="tab:orange",
        linewidth=0.2,
        alpha=0.45,
        label="Global Histogram",
    )

    ax_lut.set_title(f"DCI Global LUT and Histogram\n{global_lut_path.name} | {global_hist_path.name}")
    ax_lut.set_xlabel("Index / Histogram Bin")
    ax_lut.set_ylabel("LUT Value", color="tab:blue")
    ax_hist.set_ylabel("Histogram Count", color="tab:orange")
    ax_lut.tick_params(axis="y", labelcolor="tab:blue")
    ax_hist.tick_params(axis="y", labelcolor="tab:orange")
    ax_lut.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    ax_lut.set_xlim(0, max(max(lut_x), max(hist_x)))
    ax_lut.legend([lut_line, hist_bar], ["Global LUT", "Global Histogram"], loc="best")

    fig.tight_layout()
    fig.savefig(output_path, format="png")
    plt.close(fig)


def main():
    """Run the LUT drawing tool."""
    args = parse_args()
    global_lut_path = Path(args.global_lut_file) if args.global_lut_file else None
    global_hist_path = Path(args.global_hist_file) if args.global_hist_file else None
    output_path = build_output_path(global_lut_path, global_hist_path, args.output_file)

    if global_lut_path and not global_lut_path.is_file():
        print(f"Error: global LUT file not found: {global_lut_path}")
        return 1
    if global_hist_path and not global_hist_path.is_file():
        print(f"Error: global histogram file not found: {global_hist_path}")
        return 1

    try:
        if global_lut_path and global_hist_path:
            draw_combined_plot(global_lut_path, global_hist_path, output_path)
        elif global_lut_path:
            lut_x, lut_y = parse_global_lut_file(global_lut_path)
            draw_global_lut_curve(lut_x, lut_y, global_lut_path, output_path)
        else:
            hist_x, hist_y = parse_global_hist_file(global_hist_path)
            draw_global_histogram(hist_x, hist_y, global_hist_path, output_path)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Saved DCI figure to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

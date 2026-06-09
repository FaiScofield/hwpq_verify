"""
I/O Config tab for PQ Test Tool.

Provides shared input/output file, resolution, format, and colorspace controls.
Also contains shared constants (FORMAT_NAMES, CLRSPC_NAMES, etc.) used across modules.
"""

import os
import re
import sys
from collections import defaultdict

# Ensure the parent script/ package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PySimpleGUI as sg

from csc.run_csc import get_frame_size

# ------------------------------------------------------------------ #
# Shared constants                                                   #
# ------------------------------------------------------------------ #

FORMAT_NAMES = {
    0x0: "RGB888",
    0x1: "RGBA8888",
    0x2: "RGB_Planar",
    0x3: "YUV444P_YU24",
    0x4: "YUV444SP_NV24",
    0x5: "YUV444I_VU24",
    0x6: "YUV422P_YU16",
    0x7: "YUV422SP_NV16",
    0x8: "YUV420P_YU12",
    0x9: "YUV420SP_NV12",
    0xA: "YUV400_Gray",
    0x10: "RGB_10LSB",
    0x11: "RGBA_10LSB",
    0x12: "RGB_Planar_10LSB",
    0x13: "YUV444P_10LSB",
    0x14: "YUV444SP_10LSB",
    0x15: "YUV444I_10LSB",
    0x16: "YUV422P_10LSB",
    0x17: "YUV422SP_10LSB",
    0x18: "YUV420P_10LSB",
    0x19: "YUV420SP_10LSB",
    0x1A: "YUV400_10LSB",
    0x20: "RGB_10Packed",
    0x21: "RGBA_1010102",
    0x22: "RGB_Planar_10Packed",
    0x23: "YUV444P_10Packed",
    0x24: "YUV444SP_10Packed_NV30",
    0x25: "YUV444I_10Packed",
    0x26: "YUV422P_10Packed",
    0x27: "YUV422SP_10Packed_NV20",
    0x28: "YUV420P_10Packed",
    0x29: "YUV420SP_10Packed_NV15",
    0x2A: "YUV400_10Packed",
}

CLRSPC_NAMES = {
    0: "RGB_Limited",
    1: "RGB_Full",
    2: "BT601_Limited",
    3: "BT601_Full",
    4: "BT709_Limited",
    5: "BT709_Full",
    6: "BT2020_Limited",
    7: "BT2020_Full",
}

FMT_OPTIONS = [
    0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A,
    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A,
]
CLRSPC_OPTIONS = [0, 1, 2, 3, 4, 5, 6, 7]

FMT_DISPLAY = [f"0x{fmt:X} - {FORMAT_NAMES.get(fmt, 'Unknown')}" for fmt in FMT_OPTIONS]
CLRSPC_DISPLAY = [f"{clr} - {CLRSPC_NAMES[clr]}" for clr in CLRSPC_OPTIONS]
CLRSPC_DISPLAY_RGB = [s for s in CLRSPC_DISPLAY if int(s.split(" ")[0]) in (0, 1)]
CLRSPC_DISPLAY_YUV = [s for s in CLRSPC_DISPLAY if int(s.split(" ")[0]) in range(2, 8)]

DEFAULT_FMT_DISPLAY = next(item for item in FMT_DISPLAY if item.startswith("0x0 "))
DEFAULT_CLRSPC_DISPLAY = next(item for item in CLRSPC_DISPLAY if item.startswith("1 "))

IO_LABEL_SIZE = (12, 1)
IO_FMT_LABEL_SIZE = (12, 1)
IO_CLR_LABEL_SIZE = (14, 1)
IO_FMT_COMBO_SIZE = (26, 1)
IO_CLR_COMBO_SIZE = (20, 1)
IO_BUTTON_SIZE = (8, 1)

STB_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}

TAB_LABEL = "I/O"


# ------------------------------------------------------------------ #
# Helper functions                                                   #
# ------------------------------------------------------------------ #


def _enforce_combo_width(window: sg.Window, key: str, width_chars: int):
    """Keep combo widget width stable after runtime value list updates."""
    try:
        window[key].Widget.configure(width=width_chars)
    except Exception:
        pass


def update_clrspc_for_fmt(window: sg.Window, values: dict, clrspc_key: str, fmt_str: str):
    """Update a colorspace combo options to match the selected format domain."""
    fmt_code = int(fmt_str.split(" ")[0], 16)
    base = fmt_code & 0xF
    if base <= 0x2:
        options = CLRSPC_DISPLAY_RGB
        default = CLRSPC_DISPLAY_RGB[1]  # RGB_Full
    else:
        options = CLRSPC_DISPLAY_YUV
        default = CLRSPC_DISPLAY_YUV[3]  # BT709_Full
    current_val = values.get(clrspc_key, "")
    new_val = current_val if current_val in options else default
    window[clrspc_key].update(values=options, value=new_val)
    _enforce_combo_width(window, clrspc_key, IO_CLR_COMBO_SIZE[0])
    values[clrspc_key] = new_val


def get_fmt_from_display(display_str: str) -> int:
    """Extract format integer from display string like '0x9 - YUV420SP_NV12'."""
    return int(display_str.split(" ")[0], 16)


def get_clrspc_from_display(display_str: str) -> int:
    """Extract colorspace integer from display string like '5 - BT709_Full'."""
    return int(display_str.split(" ")[0])


def read_io_params(values: dict) -> dict:
    """Extract common I/O parameters from window values."""
    return {
        "input_file": values.get("-INPUT-FILE-", "").strip(),
        "width": int(values.get("-WIDTH-", "1920")),
        "height": int(values.get("-HEIGHT-", "1080")),
        "in_fmt": get_fmt_from_display(values.get("-IN-FMT-", DEFAULT_FMT_DISPLAY)),
        "in_clrspc": get_clrspc_from_display(values.get("-IN-CLR-", DEFAULT_CLRSPC_DISPLAY)),
        "out_fmt": get_fmt_from_display(values.get("-OUT-FMT-", DEFAULT_FMT_DISPLAY)),
        "out_clrspc": get_clrspc_from_display(values.get("-OUT-CLR-", DEFAULT_CLRSPC_DISPLAY)),
        "output_dir": values.get("-OUTPUT-DIR-", "").strip(),
        "config_path": values.get("-CONFIG-PATH-", "").strip(),
        "frame_idx": int(values.get("-FRAME-IDX-", "0")),
        "frame_num": int(values.get("-FRAME-NUM-", "1")),
        "use_set_color": values.get("-USE-SET-COLOR-", False),
        "set_color_input": values.get("-SET-COLOR-INPUT-", "").strip(),
    }


def build_controls() -> list:
    """Build the I/O Config tab layout."""
    layout = [
        [
            sg.Text("Input File", size=IO_LABEL_SIZE),
            sg.Input("G:/Project/pq/inputs/old_town_cross_720p50_yuv444p_fr0_8bit.yuv", key="-INPUT-FILE-", size=(46, 1), enable_events=True,
                     tooltip="输入YUV/RGB原始数据文件路径；支持拖拽或浏览选择"),
            sg.FileBrowse(size=IO_BUTTON_SIZE),
            sg.Button("Reload", key="-RELOAD-", size=IO_BUTTON_SIZE,
                      tooltip="重新加载输入文件并自动推断格式与分辨率"),
        ],
        [
            sg.Text("Output Dir", size=IO_LABEL_SIZE),
            sg.Input("D:/RkDefaultDumpData/", key="-OUTPUT-DIR-", size=(46, 1),
                     tooltip="模块处理dump结果的输出目录"),
            sg.FolderBrowse(size=IO_BUTTON_SIZE),
            sg.Button("Open Dir", key="-OPEN-DIR-OUTPUT-", size=IO_BUTTON_SIZE,
                      tooltip="在资源管理器中打开输出目录"),
        ],
        [
            sg.Text("Config File", size=IO_LABEL_SIZE),
            sg.Input("G:/Codes/gerrit_projects/hwpq_verify/data/dci_config_3572.json", key="-CONFIG-PATH-", size=(46, 1),
                     tooltip="DCI/SHP模块的硬件寄存器配置文件路径"),
            sg.FileBrowse(target="-CONFIG-PATH-", key="-BROWSE-CONFIG-", size=IO_BUTTON_SIZE),
            sg.Button("Open Dir", key="-OPEN-DIR-CONFIG-", size=IO_BUTTON_SIZE,
                      tooltip="在资源管理器中打开配置文件所在目录"),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Width", size=(8, 1)),
            sg.Input("1920", key="-WIDTH-", size=(8, 1),
                     tooltip="图像宽度（像素）"),
            sg.Text("Height", size=(8, 1)),
            sg.Input("1080", key="-HEIGHT-", size=(8, 1),
                     tooltip="图像高度（像素）"),
            sg.Text("Frame Num", size=(8, 1)),
            sg.Input("1", key="-FRAME-NUM-", size=(8, 1), readonly=True,
                     tooltip="YUV文件中包含的总帧数（根据文件尺寸自动计算）"),
            sg.Text("Frame Idx", size=(8, 1)),
            sg.Input("0", key="-FRAME-IDX-", size=(8, 1),
                     tooltip="读取第几帧（从0开始）"),
        ],
        [
            sg.Text("Input Format", size=IO_FMT_LABEL_SIZE),
            sg.Combo(
                FMT_DISPLAY,
                default_value=DEFAULT_FMT_DISPLAY,
                key="-IN-FMT-",
                readonly=True,
                size=IO_FMT_COMBO_SIZE,
                enable_events=True,
                tooltip="输入数据的像素格式（RGB/YUV、8bit/10bit/10Packed等）",
            ),
            sg.Text("Input Colorsp", size=IO_CLR_LABEL_SIZE),
            sg.Combo(
                CLRSPC_DISPLAY_RGB,
                default_value=CLRSPC_DISPLAY_RGB[1],
                key="-IN-CLR-",
                readonly=True,
                size=IO_CLR_COMBO_SIZE,
                enable_events=True,
                tooltip="输入数据的色彩空间（RGB_Limited/Full 或 BT601/709/2020）",
            ),
        ],
        [
            sg.Text("Output Format", size=IO_FMT_LABEL_SIZE),
            sg.Combo(
                FMT_DISPLAY,
                default_value=DEFAULT_FMT_DISPLAY,
                key="-OUT-FMT-",
                readonly=True,
                size=IO_FMT_COMBO_SIZE,
                enable_events=True,
                tooltip="期望输出的像素格式",
            ),
            sg.Text("Output Colorsp", size=IO_CLR_LABEL_SIZE),
            sg.Combo(
                CLRSPC_DISPLAY_RGB,
                default_value=CLRSPC_DISPLAY_RGB[1],
                key="-OUT-CLR-",
                readonly=True,
                size=IO_CLR_COMBO_SIZE,
                enable_events=True,
                tooltip="期望输出的色彩空间",
            ),
        ],
        [
            sg.Checkbox(
                "Use Specified Color as Input",
                key="-USE-SET-COLOR-",
                default=False,
                enable_events=True,
                tooltip="启用后使用自定义纯色代替文件作为输入图像数据",
            ),
            sg.Input(
                "128 128 128",
                key="-SET-COLOR-INPUT-",
                size=(20, 1),
                disabled=True,
                enable_events=True,
                disabled_readonly_background_color=sg.theme_background_color(),
                tooltip="自定义RGB纯色值，三个整数用空格分隔（如 128 128 128）",
            ),
            sg.Text("Stream Depth"),
            sg.Combo(
                ["8bit", "10bit"],
                default_value="10bit",
                key="-STREAM-DEPTH-",
                readonly=True,
                tooltip="Pipeline数据流精度：8bit输入自动左移提升到10bit；10bit输出可选降位到8bit",
            ),
        ],
    ]
    return layout


def handle_io_event(event: str, values: dict, window: sg.Window) -> bool:
    """Handle I/O-specific events.

    Returns True if the event was consumed, False otherwise.
    """
    if event == "-IN-FMT-":
        update_clrspc_for_fmt(window, values, "-IN-CLR-", values["-IN-FMT-"])
        _recalc_frame_num(values, window)
        return True

    if event == "-IN-CLR-":
        return True

    if event == "-OUT-FMT-":
        update_clrspc_for_fmt(window, values, "-OUT-CLR-", values["-OUT-FMT-"])
        return True

    if event == "-OUT-CLR-":
        return True

    if event in ("-WIDTH-+ENTER", "-HEIGHT-+ENTER"):
        _recalc_frame_num(values, window)
        return True

    if event == "-USE-SET-COLOR-":
        enabled = values["-USE-SET-COLOR-"]
        window["-SET-COLOR-INPUT-"].update(disabled=not enabled)
        return True

    if event == "-SET-COLOR-INPUT-":
        # Enter pressed on color input — only apply when -USE-SET-COLOR- is active
        if values.get("-USE-SET-COLOR-", False):
            return True
        return True

    if event == "-INPUT-FILE-":
        _guess_input_params(values, window)
        _recalc_frame_num(values, window)
        return True

    if event == "-RELOAD-":
        # Turn off USE-SET-COLOR, re-analyze input file, then re-read
        window["-USE-SET-COLOR-"].update(value=False)
        window["-SET-COLOR-INPUT-"].update(disabled=True)
        values["-USE-SET-COLOR-"] = False
        _guess_input_params(values, window)
        _recalc_frame_num(values, window)
        return True

    if event == "-BROWSE-CONFIG-":
        # Config file selected via FileBrowse — trigger pipeline re-run
        return True

    if event.startswith("-OPEN-DIR-"):
        _open_containing_folder(values, event, window)
        return True

    return False


def _open_containing_folder(values: dict, event: str, window: sg.Window):
    """Open the folder containing the file referenced by an Open Dir button."""
    key_map = {
        "-OPEN-DIR-OUTPUT-": "-OUTPUT-DIR-",
        "-OPEN-DIR-CONFIG-": "-CONFIG-PATH-",
    }
    target_key = key_map.get(event)
    if target_key is None:
        return
    path = values.get(target_key, "").strip()
    if not path:
        return
    target = os.path.dirname(path) if os.path.isfile(path) else path
    if os.path.isdir(target):
        try:
            os.startfile(target)
        except Exception:
            pass
    elif os.path.isfile(path):
        dirpath = os.path.dirname(path)
        if os.path.isdir(dirpath):
            try:
                os.startfile(dirpath)
            except Exception:
                pass


def _recalc_frame_num(values: dict, window: sg.Window):
    """Recalculate Frame Num from file size and frame dimensions."""
    input_file = values.get("-INPUT-FILE-", "").strip()
    if not input_file or not os.path.isfile(input_file):
        return

    # Image files are compressed; always treated as a single frame
    ext = os.path.splitext(input_file)[1].lower()
    if ext in STB_IMAGE_EXTENSIONS:
        window["-FRAME-NUM-"].update(value="1")
        values["-FRAME-NUM-"] = "1"
        return

    fmt_str = values.get("-IN-FMT-", DEFAULT_FMT_DISPLAY)
    fmt_code = get_fmt_from_display(fmt_str)
    try:
        w = int(values.get("-WIDTH-", "1920"))
        h = int(values.get("-HEIGHT-", "1080"))
    except ValueError:
        w, h = 1920, 1080

    frame_size = get_frame_size(w, h, fmt_code)
    actual_size = os.path.getsize(input_file)
    frame_num = max(1, actual_size // frame_size) if frame_size > 0 else 1
    window["-FRAME-NUM-"].update(value=str(frame_num))
    values["-FRAME-NUM-"] = str(frame_num)

    if actual_size < frame_size:
        window["-STATUS-"].update(
            "File too small for frame size", text_color="orange"
        )


def _guess_input_params(values: dict, window: sg.Window):
    """Guess input format and resolution from filename."""
    input_file = values.get("-INPUT-FILE-", "").strip()
    if not input_file or not os.path.isfile(input_file):
        return

    basename = os.path.basename(input_file).lower()
    ext = os.path.splitext(basename)[1]

    if ext in STB_IMAGE_EXTENSIONS:
        # Treat image files as RGB888
        rgb_fmt = 0x0
        window["-IN-FMT-"].update(value=rgb_fmt)
        values["-IN-FMT-"] = rgb_fmt
        update_clrspc_for_fmt(window, values, "-IN-CLR-", rgb_fmt)
        # Read actual dimensions from image file
        try:
            from PIL import Image
            with Image.open(input_file) as im:
                wid, hgt = im.size
                window["-WIDTH-"].update(value=str(wid))
                values["-WIDTH-"] = str(wid)
                window["-HEIGHT-"].update(value=str(hgt))
                values["-HEIGHT-"] = str(hgt)
        except Exception:
            pass
        return

    if ext == ".yuv":
        yuv_fmt = next((f for f in FMT_DISPLAY if f.startswith("0x4 ")), None)
        if yuv_fmt:
            window["-IN-FMT-"].update(value=yuv_fmt)
            values["-IN-FMT-"] = yuv_fmt
            update_clrspc_for_fmt(window, values, "-IN-CLR-", yuv_fmt)
    elif ext == ".rgb":
        rgb_fmt = next((f for f in FMT_DISPLAY if f.startswith("0x0 ")), None)
        if rgb_fmt:
            window["-IN-FMT-"].update(value=rgb_fmt)
            values["-IN-FMT-"] = rgb_fmt
            update_clrspc_for_fmt(window, values, "-IN-CLR-", rgb_fmt)

    m_res = re.search(r"(\d+)x(\d+)", basename)
    if m_res:
        window["-WIDTH-"].update(value=m_res.group(1))
        values["-WIDTH-"] = m_res.group(1)
        window["-HEIGHT-"].update(value=m_res.group(2))
        values["-HEIGHT-"] = m_res.group(2)


def init_module(window: sg.Window):
    """Initialize I/O tab: sync colorspace combos and bind Enter key to WIDTH/HEIGHT."""
    update_clrspc_for_fmt(window, {}, "-IN-CLR-", DEFAULT_FMT_DISPLAY)
    update_clrspc_for_fmt(window, {}, "-OUT-CLR-", DEFAULT_FMT_DISPLAY)
    window["-WIDTH-"].bind("<Return>", "+ENTER")
    window["-WIDTH-"].bind("<KP_Enter>", "+ENTER")
    window["-HEIGHT-"].bind("<Return>", "+ENTER")
    window["-HEIGHT-"].bind("<KP_Enter>", "+ENTER")

"""
Copyright   : Copyright (c) 2026 by Rockchip. All right reserved.
FilePath    : native_compare.py
Author      : vance.wu@rock-chips.com
Date        : 2026-10-19
Description : BCSH Python 参考实现(hsv_adjust.py)与 C/C++ rk_swpq_exe 的自动比对核心。
              C++ 侧实现见 RkYuvAlgos_git 的 rkalgo_swpq_bcsh.cpp / rkpq_main.cpp。
"""

from __future__ import annotations

import csv
import json
import logging
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from script.bcsh.hsv_adjust import (  # noqa: E402
    adjust_hsv,
    adjust_rgb,
    hsv_to_rgb,
    rgb_to_hsv,
)

# rkpq_api.h 中的枚举值：BCSH 只支持 RGB 格式族，RGBA8888 可避开 Windows
# OpenCL 驱动不支持 CL_RGB 的问题，且能顺带验证 alpha 不被修改。
RKPQ_IMG_FMT_RGBA = 1000
RKPQ_MODULE_BCSH = 13
RKPQ_CLR_SPC_RGB_FULL = 7

MIN_FRAME_SIZE = 128
RGBA_CHANNELS = 4
_PROC_MODE_NAMES = {
    "auto": 0,
    "gpu": 1,
    "cpu": 2,
    "cpu_gpu": 3,
}

CLR_SPC_NAMES = {
    0: "601L",
    1: "601F",
    2: "709L",
    3: "709F",
    4: "2020L",
    5: "2020F",
    6: "RGB_LIMITED",
    7: "RGB_FULL",
    8: "DCI_P3",
    9: "DISPLAY_P3",
}

# 与 rkalgo_swpq_bcsh.cpp 的 bcshClrSpc2GrayCoef() 保持一致
GRAY_COEF = {
    0: "bt601",
    1: "bt601",
    2: "bt709",
    3: "bt709",
    4: "bt2020",
    5: "bt2020",
    6: "bt709",
    7: "bt709",
    8: "dci_p3",
    9: "display_p3",
}


def _round_clip(value: float, lo: int, hi: int) -> int:
    """四舍五入并钳位到 [lo, hi]。"""
    return int(min(max(round(value), lo), hi))


@dataclass(frozen=True)
class BcshNativeConfig:
    """一份 rkpq_bcsh_cfg 配置（参数均为 C++ 原始量纲）。"""

    model: str = "rgb"              # 'rgb' | 'hsv'
    color_space: int = RKPQ_CLR_SPC_RGB_FULL
    brightness: int = 1024          # [0, (1024), 2047]: RGB-加性偏移 / HSV-乘性增益
    contrast: int = 1024            # [0, (1024), 2047]，仅 RGB 模型
    saturation: int = 1024          # [0, (1024), 2047]，乘性增益
    hue: int = 1024                 # [0, (1024), 2047]: RGB-旋转角 / HSV-向目标色相的进度
    hue_goal: float = -1.0          # HSV 强制 SameTarget：必须在 [0, 360]，否则不调整色相
    proc_mode: int = 1              # 0-auto / 1-GPU / 2-CPU / 3-CPU&GPU
    enable: bool = True

    def validate(self) -> None:
        if self.model not in ("rgb", "hsv"):
            raise ValueError(f"model 必须是 'rgb' 或 'hsv'，实际为 {self.model!r}")
        if self.color_space not in CLR_SPC_NAMES:
            raise ValueError(f"不支持的颜色空间编号: {self.color_space}")
        for name in ("brightness", "contrast", "saturation", "hue"):
            value = getattr(self, name)
            if not 0 <= value <= 2047:
                raise ValueError(f"{name}={value} 超出 [0, 2047]")
        if self.model == "hsv" and not 0.0 <= self.hue_goal <= 360.0:
            raise ValueError(
                f"HSV 模型强制 SameTarget，hue_goal={self.hue_goal} 超出 [0, 360]"
            )
        if self.proc_mode not in (0, 1, 2, 3):
            raise ValueError(f"proc_mode={self.proc_mode} 超出 [0, 3]")

    def to_json_dict(self) -> dict:
        """转换为 rkpq_parseJsonConfigBcsh() 要求的 v2 JSON 布局。

        exe 侧要求 ``pq_tuning_param.bcsh`` 为配置组数组（取 ``config_info.activated.bcsh``
        指定的组，未指定时取第一组），组内使用短键名。
        """
        self.validate()
        return {
            "config_info": {"version": "2.0.0"},
            "pq_tuning_param": {
                "bcsh": [
                    {
                        "name": "default",
                        "enable": 1 if self.enable else 0,
                        "colorModel": 0 if self.model == "rgb" else 1,
                        "colorSpace": int(self.color_space),
                        "procMode": int(self.proc_mode),
                        "brightness": int(self.brightness),
                        "contrast": int(self.contrast),
                        "saturation": int(self.saturation),
                        "hue": int(self.hue),
                        "hueGoal": float(self.hue_goal),
                    }
                ]
            },
        }

    @classmethod
    def from_ui_params(
        cls,
        *,
        delta_b: float = 0.0,
        gain_b: float | None = None,
        gain_c: float = 1.0,
        delta_s: float = 1.0,
        delta_h_deg: float = 0.0,
        model: str = "rgb",
        color_space: int = RKPQ_CLR_SPC_RGB_FULL,
        hue_goal: float | None = None,
        progress: float | None = None,
        proc_mode: int = 1,
    ) -> "BcshNativeConfig":
        """把 UI 常用量纲转换为 C++ 的 [0, 1024, 2047] 整数参数。

        RGB 模型（中性 1024）：
        - delta_b ∈ [-1, 1]   -> nBrightness = 1024 + 1024*delta_b（B = ModeAdd）
        - gain_c  ∈ [0, 2]    -> nContrast   = 1024*gain_c  （C = GainAtZeroPoint）
        - delta_s ∈ [0, 2]    -> nSaturation = 1024*delta_s  （S = MixGray）
        - delta_h_deg ∈ [-180, 180] -> nHue = 1024 + 1024*delta_h_deg/180（H = RotateOnGray，1度量化）
        HSV 模型（强制 SameTarget，对比度不使用）：
        - gain_b ∈ [0, 2]  -> nBrightness = 1024*gain_b（B = ModeMul，未给 gain_b 时中性 1.0）
        - delta_s ∈ [0, 2] -> nSaturation = 1024*delta_s（S = ModeMul）
        - progress ∈ [0, 1] -> nHue = 1024*progress（向 hue_goal 旋转的进度，中性 0）
        """
        if model == "hsv":
            if hue_goal is None or not 0.0 <= float(hue_goal) <= 360.0:
                raise ValueError("HSV 模型强制 SameTarget，必须给出 [0, 360] 范围内的 hue_goal")
            if progress is None:
                raise ValueError("HSV SameTarget 模式需要同时给出 progress")
            goal = float(hue_goal)
            hue = _round_clip(progress * 1024.0, 0, 2047)
            gain_v = 1.0 if gain_b is None else float(gain_b)
            brightness = _round_clip(gain_v * 1024.0, 0, 2047)
        else:
            goal = -1.0
            hue = _round_clip(1024.0 + delta_h_deg * 1024.0 / 180.0, 0, 2047)
            brightness = _round_clip(1024.0 + delta_b * 1024.0, 0, 2047)
        return cls(
            model=model,
            color_space=color_space,
            brightness=brightness,
            contrast=_round_clip(gain_c * 1024.0, 0, 2047),
            saturation=_round_clip(delta_s * 1024.0, 0, 2047),
            hue=hue,
            hue_goal=goal,
            proc_mode=proc_mode,
        )

    def label(self) -> str:
        parts = [self.model, f"B{self.brightness}"]
        if self.model == "rgb":
            parts.append(f"C{self.contrast}")
        parts += [
            f"S{self.saturation}",
            f"H{self.hue}",
            f"cs{self.color_space}({CLR_SPC_NAMES.get(self.color_space, '?')})",
        ]
        if self.model == "hsv":
            parts.append(f"goal{self.hue_goal:g}")
        return " ".join(parts)


@dataclass(frozen=True)
class BcshCase:
    """一条待验证的用例。"""

    name: str
    config: BcshNativeConfig


@dataclass(frozen=True)
class DiffMetrics:
    """参考图与 C++ 输出图的误差统计（masked 为被排除的像素数）。"""

    max_abs: int
    mean_abs: float
    p99_abs: float
    count_gt1: int
    count_gt2: int
    total: int
    masked: int = 0

    def exceeded(self, max_diff: int) -> bool:
        return self.max_abs > max_diff


class NativeBcshError(RuntimeError):
    """调用 rk_swpq_exe 失败。"""


def find_default_exe() -> Path | None:
    """按环境变量、同级仓库和已知开发机路径查找 rk_swpq_exe。

    多个构建产物并存时取**修改时间最新**的一个：旧 exe 与新构建写入的
    OpenCL kernel 缓存（``D:/RkDefaultDumpData/pq_bcsh_*.bin``）可能不兼容，
    会导致 GPU 通路静默输出全 0。
    """
    env_exe = os.environ.get("RKPQ_EXE")
    if env_exe:
        return Path(env_exe)

    roots: list[Path] = []
    env_root = os.environ.get("RKYUVALGOS_ROOT")
    if env_root:
        roots.append(Path(env_root))
    for base in (_REPO_ROOT.parent, _REPO_ROOT.parent.parent):
        roots.append(base / "RkYuvAlgos_git")
    # 本机常见路径，放在最后兜底；其他机器请用 --exe 或 RKPQ_EXE 指定。
    roots.append(Path("G:/Codes/RkYuvAlgos_git"))

    candidates: list[Path] = []
    for root in roots:
        candidates.extend(
            [
                root / "project/vc/build_ninja_Release/rkswpq/rk_swpq_exe.exe",
                root / "project/vc/build_ninja_Debug/rkswpq/rk_swpq_exe.exe",
                root / "project/vc/build_msvc_ut/rkswpq/Debug/rk_swpq_exe.exe",
                root / "project/vc/build_msvc_ut/rkswpq/Release/rk_swpq_exe.exe",
                root / "project/vc/build_msvc/rkswpq/Debug/rk_swpq_exe.exe",
                root / "project/vc/build_msvc/rkswpq/Release/rk_swpq_exe.exe",
                root / "project/vc/build_Debug/rkswpq/rk_swpq_exe.exe",
            ]
        )

    existing = [path for path in candidates if path.is_file()]
    if not existing:
        return None
    newest = max(existing, key=lambda path: path.stat().st_mtime)
    if len(existing) > 1:
        logger.debug(
            "找到 %d 个 rk_swpq_exe，选用最新的 %s（%s）",
            len(existing), newest, time_str(newest),
        )
    return newest


def time_str(path: Path) -> str:
    """返回文件修改时间字符串（用于日志）。"""
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(path.stat().st_mtime))
    except OSError:
        return "unknown"


def _gray_coef(color_space: int) -> str:
    if color_space not in GRAY_COEF:
        raise ValueError(f"不支持的颜色空间编号: {color_space}")
    return GRAY_COEF[color_space]


def python_reference(rgb: np.ndarray, config: BcshNativeConfig) -> np.ndarray:
    """用 hsv_adjust.py 计算参考结果，并量化到 8bit RGB。

    只覆盖 C++ 实际实现的模式组合：
    - RGB 模型: B(add) -> C(GainAtZero) -> S(MixGray luma) -> H(RotateOnGray)，
      旋转角与 C++ 一致保持 1 度量化（'nHueAngleQ14' 的整数度取整）
    - HSV 模型: B(ModeMul) -> S(ModeMul) -> H(SameTarget)，对比度不使用，
      'hue_goal' 超出 [0, 360] 时色相不调整
    """
    config.validate()
    rgb8 = np.asarray(rgb, dtype=np.uint8)
    if rgb8.ndim != 3 or rgb8.shape[2] != 3:
        raise ValueError(f"rgb 形状必须为 (H, W, 3)，实际为 {rgb8.shape}")
    if not config.enable:
        return rgb8.copy()

    ds = config.saturation / 1024.0
    rgb_f = rgb8.astype(np.float32) / 255.0

    if config.model == "rgb":
        db = (config.brightness - 1024) / 1024.0
        gc = config.contrast / 1024.0
        # 与 C++ 的 nHueAngleQ14 一致：先四舍五入到整数度（RGB 模型精度保持不变）
        angle_deg = float(round((config.hue - 1024) * 180.0 / 1024.0))
        out = adjust_rgb(
            rgb_f,
            delta_b=db,
            delta_s=ds,
            gain_c=gc,
            tolerance_s=0.0,
            mode_c="zero",
            mode_b="add",
            angle_deg=angle_deg,
            gray_coef=_gray_coef(config.color_space),
            h_mode="rotategray",
        )
    else:
        # B = ModeMul：nBrightness 为乘性增益（中性 1024 -> 1.0）
        gain_v = config.brightness / 1024.0
        h, s, v = rgb_to_hsv(rgb_f)
        hsv = np.stack([h, s, v], axis=-1)
        adj = adjust_hsv(
            hsv,
            delta_b=gain_v,
            delta_s=ds,
            delta_h=0.0,
            gain_c=1.0,
            mode_s="mul",
            mode_b="mul",
        )
        # H = SameTarget（强制）：nHue 为向目标色相旋转的进度，中性 1024 -> 50%
        if 0.0 <= config.hue_goal <= 360.0:
            progress = min(config.hue / 1024.0, 1.0)
            arc = ((config.hue_goal - h + 180.0) % 360.0) - 180.0
            adj = np.stack(
                [(h + progress * arc) % 360.0, adj[..., 1], adj[..., 2]], axis=-1
            )
        out = hsv_to_rgb(adj)

    return np.floor(np.clip(out, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


def compare_rgb(
    reference: np.ndarray,
    native: np.ndarray,
    mask: np.ndarray | None = None,
) -> DiffMetrics:
    """统计两张 RGB 图的逐像素绝对误差。

    ``mask`` 为 True 的像素不参与统计（用于排除 SameTarget 模式在对跖色相
    附近因定点/浮点微小差异引起的符号翻转点）。
    """
    ref = np.asarray(reference, dtype=np.uint8)
    out = np.asarray(native, dtype=np.uint8)
    if ref.shape != out.shape:
        raise ValueError(f"参考/输出尺寸不一致: {ref.shape} != {out.shape}")
    diff = np.abs(out.astype(np.int16) - ref.astype(np.int16))
    masked = 0
    if mask is not None:
        mask_arr = np.asarray(mask, dtype=bool)
        if mask_arr.shape == diff.shape:
            masked = int(np.count_nonzero(mask_arr))
            diff = diff[~mask_arr]
        elif mask_arr.shape == diff.shape[:2]:
            # 2D 像素掩码：排除整像素的三个通道
            masked = int(np.count_nonzero(mask_arr))
            diff = diff[~mask_arr]
        else:
            raise ValueError(
                f"mask 尺寸不一致: {mask_arr.shape} 与 {diff.shape}"
            )
    else:
        diff = diff.reshape(-1)
    total = int(diff.size)
    if total == 0:
        return DiffMetrics(0, 0.0, 0.0, 0, 0, 0, masked)
    return DiffMetrics(
        max_abs=int(diff.max()),
        mean_abs=float(diff.mean()),
        p99_abs=float(np.percentile(diff, 99)),
        count_gt1=int(np.count_nonzero(diff > 1)),
        count_gt2=int(np.count_nonzero(diff > 2)),
        total=total,
        masked=masked,
    )


def same_target_antipode_mask(
    rgb: np.ndarray,
    config: BcshNativeConfig,
    margin_deg: float = 1.0,
) -> np.ndarray | None:
    """SameTarget 模式且 0 < progress < 1 时，标记目标色相的对跖色相带。

    对跖点两侧的最短弧方向相反，定点与浮点对 H 的微小差异会让旋转方向翻转，
    这是算法本身的病态点（两种结果都“正确”），不参与误差统计。
    """
    if config.model != "hsv" or not (0.0 <= config.hue_goal <= 360.0):
        return None
    progress = min(config.hue / 1024.0, 1.0)
    if progress <= 0.0 or progress >= 1.0:
        return None
    rgb_f = np.asarray(rgb, dtype=np.uint8).astype(np.float32) / 255.0
    h, _, _ = rgb_to_hsv(rgb_f)
    arc = ((config.hue_goal - h + 180.0) % 360.0) - 180.0
    return np.abs(arc) > (180.0 - float(margin_deg))


def make_test_chart(size: int = 256, seed: int = 0) -> np.ndarray:
    """生成覆盖色相环、6x6x6 RGB 立方、灰阶、极值和随机噪声的测试图。"""
    if size < MIN_FRAME_SIZE or size % 16 != 0:
        raise ValueError("size 必须 >= 128 且为 16 的倍数（保证 RGBA 行按 64B 对齐）")
    h = w = int(size)
    chart = np.zeros((h, w, 3), dtype=np.uint8)

    # 1) 色相环：S/V 三档，覆盖全部色相以及 H 旋转
    band = h // 6
    xs = np.arange(w, dtype=np.float32)
    hue = np.broadcast_to(xs[None, :] / w * 360.0, (band, w))
    for idx, (sat, val) in enumerate(((1.0, 1.0), (1.0, 0.5), (0.5, 1.0))):
        hsv = np.stack(
            [hue, np.full_like(hue, sat), np.full_like(hue, val)], axis=-1
        )
        rgb = np.floor(np.clip(hsv_to_rgb(hsv), 0.0, 1.0) * 255.0 + 0.5)
        chart[idx * band : (idx + 1) * band] = rgb.astype(np.uint8)

    # 2) 6x6x6 RGB 立方：覆盖各通道低/中/高组合
    cube_top = h // 2
    cube_h = h // 4
    levels = np.array([0, 51, 102, 153, 204, 255], dtype=np.uint8)
    cols, rows = 18, 12
    cell_w = max(1, w // cols)
    cell_h = max(1, cube_h // rows)
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            color = levels[[idx // 36, (idx // 6) % 6, idx % 6]]
            y0 = cube_top + row * cell_h
            y1 = min(cube_top + (row + 1) * cell_h, cube_top + cube_h)
            x0 = col * cell_w
            x1 = min((col + 1) * cell_w, w)
            chart[y0:y1, x0:x1] = color

    # 3) 灰阶 ramp
    gray_top = h * 3 // 4
    gray_h = h // 8
    ramp = np.floor(np.arange(w, dtype=np.float32) / max(1, w - 1) * 255.0 + 0.5)
    chart[gray_top : gray_top + gray_h] = ramp.astype(np.uint8)[None, :, None]

    # 4) 随机噪声 + 极值点（0/255、原色、次色、近钳位值）
    noise_top = h * 7 // 8
    rng = np.random.default_rng(seed)
    chart[noise_top:] = rng.integers(
        0, 256, size=(h - noise_top, w, 3), dtype=np.uint8
    )
    extremes = np.array(
        [
            [0, 0, 0],
            [255, 255, 255],
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255],
            [255, 255, 0],
            [0, 255, 255],
            [255, 0, 255],
            [1, 1, 1],
            [254, 254, 254],
        ],
        dtype=np.uint8,
    )
    chart[noise_top, : len(extremes)] = extremes
    return chart


def load_image_chart(path: str | os.PathLike, size: int = 256) -> np.ndarray:
    """读取真实图片并缩放到测试尺寸（RGB888）。"""
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - Pillow 已在 requirements 中
        raise ImportError("读取图片需要 Pillow") from exc

    if size < MIN_FRAME_SIZE or size % 16 != 0:
        raise ValueError("size 必须 >= 128 且为 16 的倍数")
    with Image.open(path) as img:
        rgb = np.array(img.convert("RGB").resize((size, size), Image.LANCZOS))
    return rgb.astype(np.uint8)


class NativeBcshRunner:
    """调用 rk_swpq_exe 的 BCSH 单模块（-m=13）。"""

    def __init__(
        self,
        exe: str | os.PathLike,
        *,
        timeout: float = 180.0,
        keep_temp: bool = False,
    ) -> None:
        self.exe = Path(exe)
        if not self.exe.is_file():
            raise FileNotFoundError(f"rk_swpq_exe 不存在: {self.exe}")
        self.timeout = float(timeout)
        self.keep_temp = keep_temp

    def _subprocess_env(self) -> dict:
        """子进程环境：把 exe 附近的 DLL 目录加入 PATH。

        MSVC 多配置构建把 ``pthreadVC2.dll`` 放在 ``<build>/rkswpq/Release``，
        而 exe 可能在 ``.../rkswpq/Debug``，故同时搜索 exe 同级、上一级及其
        Release 子目录。
        """
        env = os.environ.copy()
        dll_dirs: list[Path] = []
        for candidate in (self.exe.parent,
                          self.exe.parent / "Release",
                          self.exe.parent.parent / "Release",
                          self.exe.parent.parent):
            if candidate.is_dir() and candidate not in dll_dirs:
                dll_dirs.append(candidate)
        env["PATH"] = os.pathsep.join(
            [str(p) for p in dll_dirs] + [env.get("PATH", "")]
        )
        return env

    def run(
        self,
        rgb: np.ndarray,
        config: BcshNativeConfig,
        *,
        check_black: bool = False,
    ) -> np.ndarray:
        """执行一次 BCSH，返回 RGBA8888 输出 (H, W, 4)。

        帧小于 ``MIN_FRAME_SIZE`` 时按边缘复制补齐后处理，返回前裁回原尺寸
        （BCSH 是逐像素运算，补齐内容不影响结果）。

        ``check_black=True`` 时，若输入非全黑而输出 RGB 全 0 则报错（自检用，
        用于识别 exe 与 kernel 缓存不匹配等静默失败；正常用例中 B/C 置 0
        本来就会输出全黑，故默认关闭）。
        """
        config.validate()
        rgb8 = np.asarray(rgb, dtype=np.uint8)
        if rgb8.ndim != 3 or rgb8.shape[2] != 3:
            raise ValueError(f"rgb 形状必须为 (H, W, 3)，实际为 {rgb8.shape}")
        h, w = rgb8.shape[:2]
        if h < 1 or w < 1:
            raise ValueError(f"无效的分辨率: {w}x{h}")

        pad_h = max(0, MIN_FRAME_SIZE - h)
        pad_w = max(0, MIN_FRAME_SIZE - w)
        if pad_h or pad_w:
            rgb8 = np.pad(rgb8, ((0, pad_h), (0, pad_w), (0, 0)), mode="edge")
        proc_h, proc_w = rgb8.shape[:2]

        work_dir = Path(tempfile.mkdtemp(prefix="bcsh_native_"))
        try:
            in_path = work_dir / "in.rgba"
            out_path = work_dir / "out.rgba"
            cfg_path = work_dir / "cfg.json"

            rgba = np.empty((proc_h, proc_w, RGBA_CHANNELS), dtype=np.uint8)
            rgba[..., :3] = rgb8
            rgba[..., 3] = 255
            rgba.tofile(in_path)
            cfg_path.write_text(
                json.dumps(config.to_json_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            cmd = [
                str(self.exe),
                "-f=sim",
                f"-m={RKPQ_MODULE_BCSH}",
                f"-i={in_path}",
                f"-sw={proc_w}",
                f"-sh={proc_h}",
                # 帧本身始终按 full-range RGB 处理；eColorSpace 只影响 JSON 里的灰度系数
                f"-sf={RKPQ_IMG_FMT_RGBA}",
                f"-sc={RKPQ_CLR_SPC_RGB_FULL}",
                f"-o={out_path}",
                f"-df={RKPQ_IMG_FMT_RGBA}",
                f"-dc={RKPQ_CLR_SPC_RGB_FULL}",
                "-n=1",
                f"-j={cfg_path}",
            ]
            logger.debug(
                "BCSH exe 调用: %s | 处理尺寸 %dx%d（源 %dx%d）| exe 时间 %s",
                cmd[0], proc_w, proc_h, w, h, time_str(self.exe),
            )
            logger.debug(
                "BCSH 参数: model=%s colorSpace=%d procMode=%d B=%d C=%d S=%d H=%d goal=%s",
                config.model, config.color_space, config.proc_mode,
                config.brightness, config.contrast, config.saturation,
                config.hue, config.hue_goal,
            )
            logger.debug("BCSH 工作目录: %s", work_dir)
            proc = subprocess.run(
                cmd,
                cwd=str(work_dir),
                env=self._subprocess_env(),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
            )
            if proc.returncode != 0:
                tail = "\n".join(
                    ((proc.stdout or "") + (proc.stderr or "")).splitlines()[-30:]
                )
                logger.debug("BCSH exe 输出:\n%s", tail)
                if proc.returncode < 0 or proc.returncode > 0x7FFFFFFF:
                    code = proc.returncode & 0xFFFFFFFF
                    hint = "（0xC0000135 = 缺少 DLL，检查 pthreadVC2.dll 是否在 PATH）" \
                        if code == 0xC0000135 else ""
                    raise NativeBcshError(
                        f"rk_swpq_exe 异常退出（0x{code:08X}）{hint}\n{tail}"
                    )
                raise NativeBcshError(
                    f"rk_swpq_exe 返回 {proc.returncode}\n{tail}"
                )
            if not out_path.is_file():
                raise NativeBcshError("rk_swpq_exe 未生成输出文件")

            raw = np.fromfile(out_path, dtype=np.uint8)
            min_size = proc_h * proc_w * RGBA_CHANNELS
            if raw.size < min_size:
                raise NativeBcshError(
                    f"输出数据不足: {raw.size} < {min_size}"
                    f"（{proc_w}x{proc_h} RGBA8888）"
                )
            # 输出行 stride 可能带对齐填充，按实际文件大小反推
            stride = raw.size // proc_h
            if stride < proc_w * RGBA_CHANNELS:
                raise NativeBcshError(
                    f"输出 stride 异常: {stride} < {proc_w * RGBA_CHANNELS}"
                )
            rows = raw[: stride * proc_h].reshape(proc_h, stride)
            out = rows[:, : proc_w * RGBA_CHANNELS].reshape(
                proc_h, proc_w, RGBA_CHANNELS
            )
            if check_black:
                self._check_black_output(rgb8, out)
            logger.debug(
                "BCSH 输出统计: rgb min=%d max=%d mean=%.2f | alpha min=%d max=%d",
                int(out[..., :3].min()), int(out[..., :3].max()),
                float(out[..., :3].mean()),
                int(out[..., 3].min()), int(out[..., 3].max()),
            )
            return out[:h, :w].copy()
        finally:
            if self.keep_temp:
                print(f"[保留临时目录] {work_dir}")
            else:
                shutil.rmtree(work_dir, ignore_errors=True)

    def _check_black_output(self, src: np.ndarray, out: np.ndarray) -> None:
        """输入非全黑但输出 RGB 全 0 时报错。

        常见原因：exe 与 ``D:/RkDefaultDumpData/pq_bcsh_*.bin`` 里的 OpenCL
        kernel 缓存不匹配（旧 exe 加载新构建写出的 kernel），GPU 通路会静默
        输出全 0；此时改用与源码同时构建的新 exe，或删除该缓存文件。
        """
        src_rgb = src[..., :3] if src.ndim == 3 else src
        out_rgb = out[..., :3]
        if int(src_rgb.max()) > 0 and int(out_rgb.max()) == 0:
            raise NativeBcshError(
                "rk_swpq_exe 输出全黑（输入非全黑）：exe 可能过旧，与 "
                "D:/RkDefaultDumpData/pq_bcsh_*.bin 的 OpenCL kernel 缓存不匹配。\n"
                f"当前 exe: {self.exe}（{time_str(self.exe)}）\n"
                "处理建议：\n"
                "  1) 改用与当前源码同时构建的 rk_swpq_exe（取最新构建产物）；\n"
                "  2) 或删除 D:/RkDefaultDumpData/pq_bcsh_*.bin 后重试（会重新编译 kernel）；\n"
                "  3) 或用 procMode=2 走纯 CPU 通路验证。"
            )


def _unique_case_name(name: str, used: set[str]) -> str:
    if name not in used:
        used.add(name)
        return name
    index = 2
    while f"{name}_{index}" in used:
        index += 1
    final = f"{name}_{index}"
    used.add(final)
    return final


def _rgb_cases(seed: int, quick: bool, full: bool) -> list[BcshCase]:
    rng = random.Random(seed)
    cases: list[BcshCase] = []
    base = BcshNativeConfig(model="rgb")

    def add(name: str, **kwargs) -> None:
        cases.append(BcshCase(name, replace(base, **kwargs)))

    add("rgb_neutral")

    values = (0, 1024, 2047) if quick else (0, 512, 1024, 1536, 2047)
    for field_name, tag in (
        ("brightness", "B"),
        ("contrast", "C"),
        ("saturation", "S"),
        ("hue", "H"),
    ):
        for value in values:
            if value == 1024:
                continue
            add(f"rgb_{tag}{value}", **{field_name: value})

    random_num = 5 if quick else (10 if not full else 25)
    for index in range(random_num):
        add(
            f"rgb_rand{index}",
            brightness=rng.randint(0, 2047),
            contrast=rng.randint(0, 2047),
            saturation=rng.randint(0, 2047),
            hue=rng.randint(0, 2047),
        )

    if full:
        for cs in sorted(CLR_SPC_NAMES):
            add(
                f"rgb_cs{cs}",
                color_space=cs,
                brightness=rng.randint(0, 2047),
                contrast=rng.randint(0, 2047),
                saturation=rng.randint(0, 2047),
                hue=rng.randint(0, 2047),
            )
    elif not quick:
        for cs in (0, 1, 3, 5, 7, 8, 9):
            add(f"rgb_cs{cs}", color_space=cs, brightness=1200, contrast=1200,
                saturation=1200, hue=1144)
    return cases


def _hsv_cases(seed: int, quick: bool, full: bool) -> list[BcshCase]:
    rng = random.Random(seed + 1)
    cases: list[BcshCase] = []
    # HSV 模型强制 SameTarget：hue_goal 必须有效；hue(进度) 中性为 0（不旋转）
    base = BcshNativeConfig(model="hsv", hue_goal=120.0, hue=0)

    def add(name: str, **kwargs) -> None:
        cases.append(BcshCase(name, replace(base, **kwargs)))

    add("hsv_neutral")

    values = (0, 1024, 2047) if quick else (0, 512, 1024, 1536, 2047)
    for field_name, tag in (
        ("brightness", "B"),
        ("saturation", "S"),
    ):
        for value in values:
            if value == 1024:
                continue
            add(f"hsv_{tag}{value}", **{field_name: value})
    for value in values:
        if value == 0:
            continue  # 已由 hsv_neutral 覆盖
        add(f"hsv_H{value}", hue=value)

    random_num = 4 if quick else (8 if not full else 20)
    for index in range(random_num):
        add(
            f"hsv_rand{index}",
            brightness=rng.randint(0, 2047),
            saturation=rng.randint(0, 2047),
            hue=rng.randint(0, 2047),
        )

    goals = (30.0, 300.0) if quick else (0.0, 30.0, 90.0, 180.0, 300.0, 359.0)
    progresses = (0, 1024, 2047) if quick else (0, 512, 1024, 2047)
    for goal in goals:
        for progress in progresses:
            add(
                f"hsv_tgt_g{goal:g}_p{progress}",
                hue_goal=goal,
                hue=progress,
            )

    if not quick:
        for index in range(4 if not full else 10):
            add(
                f"hsv_tgt_rand{index}",
                brightness=rng.randint(0, 2047),
                saturation=rng.randint(0, 2047),
                hue=rng.randint(0, 2047),
                hue_goal=float(rng.randint(0, 359)),
            )
    return cases


def build_cases(
    model: str = "both",
    *,
    quick: bool = False,
    full: bool = False,
    seed: int = 0,
) -> list[BcshCase]:
    """生成默认参数扫描用例。"""
    if model not in ("rgb", "hsv", "both"):
        raise ValueError(f"model 必须是 'rgb'/'hsv'/'both'，实际为 {model!r}")
    if quick and full:
        raise ValueError("--quick 与 --full 不能同时使用")

    cases: list[BcshCase] = []
    if model in ("rgb", "both"):
        cases.extend(_rgb_cases(seed, quick, full))
    if model in ("hsv", "both"):
        cases.extend(_hsv_cases(seed, quick, full))

    used: set[str] = set()
    return [BcshCase(_unique_case_name(case.name, used), case.config) for case in cases]


def proc_mode_value(name: str) -> int:
    """把 CLI 的 proc-mode 名称转换为 C++ 枚举值。"""
    try:
        return _PROC_MODE_NAMES[name]
    except KeyError as exc:
        raise ValueError(f"未知 proc-mode: {name!r}") from exc


def write_report_csv(path: str | os.PathLike, rows: Iterable[dict],
                     fieldnames: Sequence[str]) -> None:
    """写 UTF-8-SIG CSV，便于直接用 Excel 打开。"""
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

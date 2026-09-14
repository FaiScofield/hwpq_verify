"""BCSH 参数取值范围/步长配置（Brightness/Contrast/Saturation/Hue）。

用户可通过 exe 同目录（打包后）或仓库根目录（源码运行）下的 JSON 文件
``test_app_hsv_params.json`` 自定义各通道/模式的 min/max/step/default。
缺失或非法字段自动回退内建默认值；首次运行且文件不存在时自动生成模板。
"""

import json
import os
import sys

PARAMS_FILE_NAME = "test_app_hsv_params.json"

# 内建默认值（文件缺失/损坏时的兜底）。
DEFAULT_PARAMS = {
    "Brightness": {
        "add": {"min": -1.0, "max": 1.0, "step": 0.01, "default": 0.0},
        "mul": {"min": 0.0, "max": 4.0, "step": 0.02, "default": 1.0},
        "rate2limit": {"min": 0.0, "max": 2.0, "step": 0.01, "default": 1.0},
    },
    "Contrast": {
        "gain": {"min": 0.0, "max": 4.0, "step": 0.01, "default": 1.0},
        "tanslant": {"min": -1.0, "max": 1.0, "step": 0.01, "default": 0.0},
        "faststone": {"min": -1.0, "max": 1.0, "step": 0.01, "default": 0.0},
    },
    "Saturation": {
        "add": {"min": -1.0, "max": 1.0, "step": 0.01, "default": 0.0},
        "mul": {"min": 0.0, "max": 4.0, "step": 0.01, "default": 1.0},
        "rate2limit": {"min": 0.0, "max": 2.0, "step": 0.01, "default": 1.0},
        "mixgray": {"min": 0.0, "max": 4.0, "step": 0.01, "default": 1.0},
    },
    "Hue": {
        "same_offset": {"min": -180.0, "max": 180.0, "step": 1.0, "default": 0.0},
        "same_target": {"min": 0.0, "max": 100.0, "step": 1.0, "default": 0.0},
    },
}

# 每通道滑块精度（滑块整数位置/单位），与 _connect_mapped_slider_spin 的 scale 一致。
SLIDER_SCALE = {"Brightness": 100, "Contrast": 100, "Saturation": 100, "Hue": 1}


def _is_leaf(entry) -> bool:
    """是否 {min,max,step,default} 叶子条目。"""
    return isinstance(entry, dict) and all(k in entry for k in ("min", "max", "step", "default"))


def _coerce_scalar(value, default):
    """把值转成 float；非法则用默认。"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _validate_leaf(data, defaults):
    """校验一个叶子条目：step>0、min<=default<=max，非法字段回退默认。"""
    if not isinstance(data, dict):
        return dict(defaults)
    out = {k: _coerce_scalar(data.get(k), defaults[k]) for k in ("min", "max", "step", "default")}
    if out["step"] <= 0 or out["min"] > out["max"]:
        return dict(defaults)
    if not (out["min"] <= out["default"] <= out["max"]):
        out["default"] = defaults["default"]
    return out


def _deep_copy(value):
    """JSON 安全深拷贝。"""
    return json.loads(json.dumps(value))


def _merge_params(defaults, data):
    """按 defaults 的结构递归合并用户数据，叶子条目逐项校验。"""
    if isinstance(defaults, dict):
        if not isinstance(data, dict):
            return _deep_copy(defaults)
        out = {}
        for key, dval in defaults.items():
            out[key] = _validate_leaf(data.get(key), dval) if _is_leaf(dval) \
                else _merge_params(dval, data.get(key))
        return out
    return _deep_copy(defaults)


def default_params_path() -> str:
    """参数 JSON 的默认位置：打包后为 exe 同目录，源码运行为仓库根目录。"""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, PARAMS_FILE_NAME)


def load_params(path=None):
    """加载参数配置；文件缺失/损坏时回退内建默认值。

    首次运行且文件不存在时自动写出模板文件（供用户编辑）。
    Returns (params, loaded_flag).
    """
    path = path or default_params_path()
    params = _merge_params(DEFAULT_PARAMS, None)
    if not os.path.isfile(path):
        try:
            save_params(params, path)
        except OSError:
            pass
        return params, False
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return params, False
    return _merge_params(DEFAULT_PARAMS, data), True


def save_params(params, path=None) -> str:
    """把参数配置写回 JSON 文件。"""
    path = path or default_params_path()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(params, fh, ensure_ascii=False, indent=2)
    return path


def param_entry(params, channel: str, mode: str | None = None):
    """取某通道（可选某模式）的叶子条目 {min,max,step,default}。"""
    entry = params.get(channel)
    if isinstance(entry, dict) and mode is not None and mode in entry:
        return entry[mode]
    if _is_leaf(entry):
        return entry
    fallback = DEFAULT_PARAMS.get(channel, {})
    return fallback.get(mode, fallback) if mode else fallback

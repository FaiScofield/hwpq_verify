"""
Shared operations

多个模块的统一行为： Reload Config / Save Config
"""

import json
import logging
import os
import tempfile

from PySide6.QtWidgets import QFileDialog, QMessageBox

logger = logging.getLogger(__name__)

# 模块页标签 -> 配置文件中 pq_tuning_param 下的节键名
_CONFIG_SECTION_KEY = {
    "ACM": "acm",
    "CSC": "csc",
    "DCI": "dci",
    "SHP": "SHARPNESS",
}


def config_section_key(module_tag: str) -> str:
    """Return the pq_tuning_param section key for a module page tag."""
    return _CONFIG_SECTION_KEY[module_tag]


def ask_reload(module_tag: str) -> bool:
    """Reload Config 确认对话框；True=重新加载并覆盖 / False=取消。"""
    box = QMessageBox(
        QMessageBox.Icon.Question,
        "Reload Config",
        f"是否要重新加载 {module_tag} 配置？\n该操作会覆盖当前配置数据。",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    box.button(QMessageBox.StandardButton.Yes).setText("Yes")
    box.button(QMessageBox.StandardButton.No).setText("No")
    return box.exec() == QMessageBox.StandardButton.Yes


def ask_save_mode(module_tag: str) -> str:
    """Save Config 三选对话框。

    Returns:
        "overwrite": 直接覆盖写入当前（I/O Config File）配置文件。
        "save_as":   另存为一个新文件（或覆盖其它已存在 json 的对应节）。
        "cancel":    取消本次保存。
    """
    box = QMessageBox(
        QMessageBox.Icon.Question,
        "Save Config",
        f"是否直接覆盖写入当前的配置文件（{module_tag}）？\n"
        "Yes=直接更新到 I/O 页 Config File 指定的文件；\n"
        "No=另存为一个新文件；Cancel=取消。",
        (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
         | QMessageBox.StandardButton.Cancel),
    )
    box.button(QMessageBox.StandardButton.Yes).setText("Yes")
    box.button(QMessageBox.StandardButton.No).setText("No")
    box.button(QMessageBox.StandardButton.Cancel).setText("Cancel")
    ret = box.exec()
    if ret == QMessageBox.StandardButton.Yes:
        return "overwrite"
    if ret == QMessageBox.StandardButton.No:
        return "save_as"
    return "cancel"


def pick_save_as_path(start_path: str, title: str) -> str:
    """No(另存)分支：优先打开 I/O Config File 所在目录让用户选择写入文件。"""
    start_dir = os.path.dirname(start_path) if start_path else ""
    if start_dir and not os.path.isdir(start_dir):
        start_dir = ""
    target, _ = QFileDialog.getSaveFileName(
        None, title, start_dir, "JSON Files (*.json)")
    if not target:
        return ""
    if not target.lower().endswith(".json"):
        target += ".json"
    return target


def build_own_root(dump_to: "Callable[[str], None]") -> dict | None:
    """把模块当前配置 dump 到临时文件并读回完整 json dict（含 pq_tuning_param 头）。

    ``dump_to(tmp_path)`` 由调用方提供（复用各模块现有的“构造 cfg + dump”逻辑）。
    """
    fd, tmp_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        dump_to(tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("Failed to snapshot module config: %s", exc)
        return None
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def _read_json_loose(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def write_config_section(own_root: dict, key: str, target_path: str) -> bool:
    """把模块配置节写入 target_path。

    - 目标文件已存在且可解析：只替换 ``pq_tuning_param[key]``，保留文件中
      其它模块/字段的数据（不覆盖）。
    - 目标文件不存在/损坏：以 own_root 全新写入（仍带 pq_tuning_param 头）。
    """
    section = (own_root.get("pq_tuning_param") or {}).get(key)
    if section is None:
        root = own_root
    else:
        root = _read_json_loose(target_path)
        root.setdefault("pq_tuning_param", {})[key] = section
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(root, f, indent=4, ensure_ascii=False)
        return True
    except OSError as exc:
        logger.error("Failed to write config '%s': %s", target_path, exc)
        return False

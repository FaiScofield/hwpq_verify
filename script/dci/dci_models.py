"""
DCI data models that mirror the Layer 1 JSON request/response contract.

These dataclasses are the single source of truth for the Python side.
All JSON serialisation between the UI and the native runner flows
through these models.
"""

import json
from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class DciAuditOverride:
    """Audit override knobs exposed in the Phase-1 UI."""

    enable_cf_he_ratio_override: int = 0
    cf_he_ratio: int = 32
    enable_bs_set_point_override: int = 0
    bs_set_point: int = 80
    enable_ws_set_point_override: int = 0
    ws_set_point: int = 80
    enable_clahe_local_ratio_override: int = 0
    clahe_local_ratio: int = 19
    enable_clahe_clip_value_override: int = 0
    clahe_clip_value: float = 1.0


@dataclass
class DciAuditConfig:
    """Audit configuration that mirrors the Layer 2 API fields."""

    enable: int = 0
    node_mask: int = 0
    export_mask: int = 0
    tag: str = ""
    working_dir: str = ""
    save_snapshot: int = 0
    snapshot_dir: str = ""
    override_cfg: DciAuditOverride = field(default_factory=DciAuditOverride)


@dataclass
class DciRunnerRequest:
    """Top-level request sent to the native DCI runner."""

    platform: int = 1
    input_file: str = ""
    output_file: str = ""
    width: int = 1920
    height: int = 1080
    pixel_format: int = 19
    input_format: int = 19
    input_colorspace: int = 4
    output_format: int = 19
    output_colorspace: int = 4
    config_path: str = ""
    reg_path: str = ""
    is_src_fullrange: int = 1
    frame_idx: int = 0
    frame_num: int = 1
    debug_dump_mask: int = 0
    debug_path: str = ""
    audit: DciAuditConfig = field(default_factory=DciAuditConfig)

    def to_json_dict(self) -> dict:
        """Convert the request tree to a plain dict suitable for json.dump."""
        return asdict(self)


@dataclass
class DciRunnerResult:
    """Parsed runner_result.json written by the native runner."""

    exit_code: int = -1
    status: str = ""
    message: str = ""
    working_dir: str = ""

    @staticmethod
    def from_json_dict(data: dict) -> "DciRunnerResult":
        return DciRunnerResult(
            exit_code=data.get("exit_code", -1),
            status=data.get("status", ""),
            message=data.get("message", ""),
            working_dir=data.get("working_dir", ""),
        )


# ------------------------------------------------------------------ #
# Convenience helpers                                               #
# ------------------------------------------------------------------ #


def write_runner_request(request: DciRunnerRequest, request_path: str) -> str:
    """Write a DciRunnerRequest to a JSON file and return the path."""
    with open(request_path, "w", encoding="utf-8") as f:
        json.dump(request.to_json_dict(), f, indent=2, ensure_ascii=False)
    return request_path


def load_runner_request(request_path: str) -> Optional[DciRunnerRequest]:
    """Load a previously-saved runner request JSON back into a model."""
    with open(request_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    req = DciRunnerRequest()
    req.platform = data.get("platform", 1)
    req.input_file = data.get("input_file", "")
    req.output_file = data.get("output_file", "")
    req.width = data.get("width", 1920)
    req.height = data.get("height", 1080)
    req.pixel_format = data.get("pixel_format", 19)
    req.input_format = data.get("input_format", 19)
    req.input_colorspace = data.get("input_colorspace", 4)
    req.output_format = data.get("output_format", 19)
    req.output_colorspace = data.get("output_colorspace", 4)
    req.config_path = data.get("config_path", "")
    req.reg_path = data.get("reg_path", "")
    req.is_src_fullrange = data.get("is_src_fullrange", 1)
    req.frame_idx = data.get("frame_idx", 0)
    req.frame_num = data.get("frame_num", 1)
    req.debug_dump_mask = data.get("debug_dump_mask", 0)
    req.debug_path = data.get("debug_path", "")

    audit_data = data.get("audit", {})
    req.audit.enable = audit_data.get("enable", 0)
    req.audit.static_only = audit_data.get("static_only", 1)
    req.audit.node_mask = audit_data.get("node_mask", 0)
    req.audit.export_mask = audit_data.get("export_mask", 0)
    req.audit.tag = audit_data.get("tag", "")
    req.audit.working_dir = audit_data.get("working_dir", "")
    req.audit.save_snapshot = audit_data.get("save_snapshot", 0)
    req.audit.snapshot_dir = audit_data.get("snapshot_dir", "")

    ovr = audit_data.get("override_cfg", {})
    req.audit.override_cfg.enable_cf_he_ratio_override = ovr.get(
        "enable_cf_he_ratio_override", 0
    )
    req.audit.override_cfg.cf_he_ratio = ovr.get("cf_he_ratio", 32)
    req.audit.override_cfg.enable_bs_set_point_override = ovr.get(
        "enable_bs_set_point_override", 0
    )
    req.audit.override_cfg.bs_set_point = ovr.get("bs_set_point", 80)
    req.audit.override_cfg.enable_ws_set_point_override = ovr.get(
        "enable_ws_set_point_override", 0
    )
    req.audit.override_cfg.ws_set_point = ovr.get("ws_set_point", 80)
    req.audit.override_cfg.enable_clahe_local_ratio_override = ovr.get(
        "enable_clahe_local_ratio_override", 0
    )
    req.audit.override_cfg.clahe_local_ratio = ovr.get("clahe_local_ratio", 19)
    req.audit.override_cfg.enable_clahe_clip_value_override = ovr.get(
        "enable_clahe_clip_value_override", 0
    )
    req.audit.override_cfg.clahe_clip_value = ovr.get("clahe_clip_value", 1.0)

    return req

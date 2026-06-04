"""
Working-set loader and snapshot manager for the DCI audit output.

Reads the live working tree written by the Layer 2/3 audit pipeline
and provides helpers to validate, preview, and snapshot the results.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Any, Optional


def _load_json_if_exists(path: str) -> Optional[dict]:
    """Load a JSON file if it exists; return None otherwise."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_working_set_ready(working_dir: str) -> tuple:
    """Verify that the mandatory working-set artifacts exist.

    Returns:
        (True, "ok") when ready, otherwise (False, reason_string).
    """
    if not working_dir:
        return False, "working_dir is not set"
    manifest_path = os.path.join(working_dir, "result_manifest.json")
    if not os.path.exists(manifest_path):
        return False, "result_manifest.json is missing"
    return True, "ok"


def load_working_set(working_dir: str) -> dict:
    """Load the complete working set from the audit output directory.

    Reads result_manifest.json and follows its references to load
    curves, histograms, and metrics.

    Returns:
        A dict with keys "manifest", "curves", "hists", "metrics".
        Missing artifacts are set to None rather than raising.
    """
    manifest_path = os.path.join(working_dir, "result_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    curves_file = manifest.get("curves", "curves/curves.json")
    hists_file = manifest.get("histograms", "hists/hists.json")
    metrics_file = manifest.get("metrics", "metrics/metrics.json")

    return {
        "working_dir": working_dir,
        "manifest": manifest,
        "curves": _load_json_if_exists(os.path.join(working_dir, curves_file)),
        "hists": _load_json_if_exists(os.path.join(working_dir, hists_file)),
        "metrics": _load_json_if_exists(os.path.join(working_dir, metrics_file)),
    }


def resolve_preview_paths(working_dir: str, manifest: dict) -> dict:
    """Resolve preview PNG paths from the manifest's image references.

    Returns:
        A dict with "input" and "output" keys, each an absolute path
        or None if the file was not exported.
    """
    images = manifest.get("images", {})
    result: dict[str, Optional[str]] = {}

    for key in ("input", "output"):
        rel = images.get(key)
        result[key] = os.path.join(working_dir, rel) if rel else None

    return result


def save_snapshot(
    working_dir: str,
    request_path: str,
    result_path: str,
    snapshot_root: str,
    snapshot_name: str,
) -> str:
    """Copy the live working set and Layer 1 request/result into a timestamped snapshot.

    Args:
        working_dir:    The live audit working directory.
        request_path:   Path to runner_request.json.
        result_path:    Path to runner_result.json.
        snapshot_root:  Root directory for snapshots.
        snapshot_name:  User-visible label (sanitised as a directory name).

    Returns:
        Absolute path to the new snapshot directory.
    """
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in snapshot_name)
    dst_dir = os.path.join(snapshot_root, f"{stamp}_{safe_name}")
    os.makedirs(dst_dir, exist_ok=False)

    # Copy Layer 1 artefacts
    if os.path.isfile(request_path):
        shutil.copy2(request_path, os.path.join(dst_dir, "runner_request.json"))
    if os.path.isfile(result_path):
        shutil.copy2(result_path, os.path.join(dst_dir, "runner_result.json"))

    # Copy the full audit working set
    if os.path.isdir(working_dir):
        shutil.copytree(working_dir, os.path.join(dst_dir, "audit_working_set"))

    return dst_dir

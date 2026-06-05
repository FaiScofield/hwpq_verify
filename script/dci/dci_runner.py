"""
Subprocess wrapper that launches the native DCI runner executable.

The runner is invoked via subprocess.run() with a pre-written request
JSON file. Any stdout/stderr is captured and the runner_result.json
is parsed after the process exits.
"""

import json
import os
import subprocess
from typing import Optional

from dci.dci_models import DciRunnerResult


def run_dci_request(
    exe_path: str, request_path: str, result_path: str
) -> subprocess.CompletedProcess:
    """Launch the native DCI runner with the given request and result paths.

    Args:
        exe_path:    Absolute path to dci_verify_runner.exe.
        request_path: Path to the JSON request file.
        result_path:  Path where runner_result.json will be written.

    Returns:
        CompletedProcess with captured stdout/stderr.
    """
    return subprocess.run(
        [exe_path, "--request", request_path, "--result", result_path],
        check=False,
        capture_output=True,
        text=True,
    )


def load_runner_result(result_path: str) -> Optional[DciRunnerResult]:
    """Load and parse runner_result.json.

    Returns:
        DciRunnerResult on success, None if the file is missing or malformed.
    """
    if not os.path.exists(result_path):
        return None
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return DciRunnerResult.from_json_dict(data)
    except (json.JSONDecodeError, OSError):
        return None

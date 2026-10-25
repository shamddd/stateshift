"""
StateShift Permanent Cloud Execution Lock
Implements fail-closed enforcement to prevent any unauthorized cloud provisioning or spending.
"""

import os
import sys
import json
from typing import Tuple, Dict, Any

LOCK_ENV_VAR = "STATE_SHIFT_CLOUD_EXECUTION_DISABLED"
LOCK_FILENAME = ".cloud_execution_locked"

def is_cloud_execution_locked() -> Tuple[bool, str]:
    """
    Checks whether cloud execution is currently disabled.
    Returns (is_locked: bool, reason: str).
    """
    # 1. Check environment variable (defaults to locked if set to '1' or missing safe override)
    env_val = os.environ.get(LOCK_ENV_VAR, "1").strip().lower()
    if env_val not in ("0", "false", "no"):
        return True, f"Environment variable {LOCK_ENV_VAR}={env_val} forbids cloud execution."

    # 2. Check for lock files in directory hierarchy
    search_dirs = [
        os.getcwd(),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
    ]
    for d in search_dirs:
        lock_path = os.path.join(d, LOCK_FILENAME)
        if os.path.isfile(lock_path):
            try:
                with open(lock_path, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)
                    reason = lock_data.get("reason", "Lock file present.")
                    return True, f"Execution lock file found at {lock_path}: {reason}"
            except Exception:
                return True, f"Execution lock file found at {lock_path}."

    return False, "Cloud execution is not locked."

def assert_cloud_execution_permitted() -> None:
    """
    Raises PermissionError immediately if cloud execution is locked.
    Must be called at the very top of any provisioning or launch pipeline.
    """
    locked, reason = is_cloud_execution_locked()
    if locked:
        msg = f"[CRITICAL SECURITY LOCK] Cloud execution is strictly prohibited: {reason}"
        print(msg, file=sys.stderr)
        raise PermissionError(msg)

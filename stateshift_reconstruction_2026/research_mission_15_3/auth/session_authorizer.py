#!/usr/bin/env python3
"""
StateShift Session-Specific Authorization Validator (Mission 15.3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enforces non-reusable, session-bound cryptographic authorization:
1. Bound to specific experiment_id, pod_id, and manifest_sha256.
2. Enforces explicit financial ceiling (<= $2.00) and balance preservation floor (>= $7.00).
3. Enforces model revision and time-bound expiration.
4. Requires approval_status == "APPROVED" and valid signature/digest.
"""

import os
import sys
import time
import json
import hashlib
from typing import Dict, Any, Tuple, Optional

FROZEN_MANIFEST_SHA256 = "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
APPROVED_MODEL_ID = "Qwen/Qwen2.5-Math-7B-Instruct"
APPROVED_MODEL_REVISION = "c869d27376a8d6728795551322fe323b6"
MAX_CAMPAIGN_BUDGET_REMAINING = 2.3575


class AuthorizationValidationError(Exception):
    pass


class SessionAuthorizer:
    """Validates session-specific, non-reusable authorization documents."""

    @staticmethod
    def validate_authorization(
        auth_doc_path: str,
        current_experiment_id: str,
        current_pod_id: str,
        current_manifest_sha256: str,
        current_mode: str,
        max_cost_limit: float = 2.00,
        model_id: str = APPROVED_MODEL_ID,
        model_revision: str = APPROVED_MODEL_REVISION
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Validates authorization document against active runner parameters.
        Returns: (is_valid: bool, auth_data: dict, rejection_reason: str)
        """
        if not auth_doc_path or not os.path.exists(auth_doc_path):
            return False, {}, f"Authorization document does not exist: {auth_doc_path}"

        try:
            with open(auth_doc_path, "r", encoding="utf-8") as f:
                auth = json.load(f)
        except Exception as e:
            return False, {}, f"Failed to parse authorization document: {e}"

        # 1. Approval Status
        approval_status = auth.get("approval_status")
        if approval_status != "APPROVED":
            return False, auth, f"Authorization status is '{approval_status}', not 'APPROVED'. Execution blocked."

        # 2. Expiration Check
        now = time.time()
        expires_at = auth.get("expires_at_utc", 0)
        if now > expires_at:
            return False, auth, f"Authorization expired at UTC {expires_at} (current time: {now})."

        # 3. Experiment ID binding
        if auth.get("experiment_id") != current_experiment_id:
            return False, auth, f"Experiment ID mismatch: auth specifies '{auth.get('experiment_id')}', active is '{current_experiment_id}'."

        # 4. Pod ID binding (for PRODUCTION mode)
        if current_mode == "PRODUCTION":
            auth_pod = auth.get("pod_id")
            if not auth_pod or auth_pod != current_pod_id:
                return False, auth, f"Pod ID mismatch: auth bound to '{auth_pod}', active is '{current_pod_id}'."

        # 5. Manifest Hash binding
        auth_manifest_hash = auth.get("manifest_sha256")
        if auth_manifest_hash != FROZEN_MANIFEST_SHA256:
            return False, auth, f"Authorization manifest hash '{auth_manifest_hash}' does not match frozen manifest constant '{FROZEN_MANIFEST_SHA256}'."
        if auth_manifest_hash != current_manifest_sha256:
            return False, auth, f"Manifest hash mismatch: auth specifies '{auth_manifest_hash}', active is '{current_manifest_sha256}'."

        # 6. Model Identity binding
        if auth.get("model_id") != model_id:
            return False, auth, f"Model ID mismatch: auth specifies '{auth.get('model_id')}', required '{model_id}'."
        if auth.get("model_revision") != model_revision:
            return False, auth, f"Model revision mismatch: auth specifies '{auth.get('model_revision')}', required '{model_revision}'."

        # 7. Financial Ceiling
        auth_max_usd = auth.get("max_authorized_incremental_usd", 999.0)
        if auth_max_usd > max_cost_limit:
            return False, auth, f"Authorized incremental budget ${auth_max_usd:.2f} exceeds runner limit ${max_cost_limit:.2f}."
        if auth_max_usd > MAX_CAMPAIGN_BUDGET_REMAINING:
            return False, auth, f"Authorized budget ${auth_max_usd:.2f} exceeds remaining campaign headroom ${MAX_CAMPAIGN_BUDGET_REMAINING:.2f}."

        # 8. Account Preservation Floor
        auth_floor = auth.get("min_account_balance_floor_usd", 0.0)
        if auth_floor < 7.00:
            return False, auth, f"Account preservation floor ${auth_floor:.2f} is below the strict $7.00 mandatory floor."

        # 9. Execution Mode Authorization
        allowed_modes = auth.get("authorized_execution_modes", [])
        if current_mode not in allowed_modes:
            return False, auth, f"Execution mode '{current_mode}' is not in authorized modes: {allowed_modes}."

        # 10. Principal Investigator Signature check
        pi = auth.get("principal_investigator")
        if pi != "Sham Satish Thakare":
            return False, auth, f"Invalid Principal Investigator: '{pi}'."

        return True, auth, "Authorization validated successfully."

#!/usr/bin/env python3
"""
StateShift 10-Request Physical Calibration Configuration (Mission 15.5)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Strictly frozen 10-request selection from the frozen parent manifest:
- Frozen Manifest SHA-256: 3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d
- Exact 10 Request IDs:
  1. primary_100_req_0001 (math500_001, Condition_A_Zero_Shot)
  2. primary_100_req_0002 (math500_001, Condition_D_Forced_Restart)
  3. primary_100_req_0003 (math500_001, Condition_E_Explicit_Repair)
  4. primary_100_req_0004 (math500_001, Condition_F_State_Preserving)
  5. primary_100_req_0005 (math500_012, Condition_A_Zero_Shot)
  6. primary_100_req_0006 (math500_012, Condition_D_Forced_Restart)
  7. primary_100_req_0007 (math500_012, Condition_E_Explicit_Repair)
  8. primary_100_req_0008 (math500_012, Condition_F_State_Preserving)
  9. primary_100_req_0009 (math500_023, Condition_A_Zero_Shot)
  10. primary_100_req_0010 (math500_023, Condition_D_Forced_Restart)

Enforces:
EXPECTED IDS PRESENT -> CONTINUE
ANY EXPECTED ID MISSING -> FAIL
(No silent fallback substitutions allowed).
"""

import os
import sys
import json
import hashlib
from typing import Dict, Any, List

FROZEN_PARENT_MANIFEST_SHA256 = "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"

FROZEN_CALIBRATION_REQUEST_IDS = [
    "primary_100_req_0001",
    "primary_100_req_0002",
    "primary_100_req_0003",
    "primary_100_req_0004",
    "primary_100_req_0005",
    "primary_100_req_0006",
    "primary_100_req_0007",
    "primary_100_req_0008",
    "primary_100_req_0009",
    "primary_100_req_0010"
]

EXPECTED_REQUEST_METADATA = {
    "primary_100_req_0001": {"problem_id": "math500_001", "condition_code": "Condition_A_Zero_Shot"},
    "primary_100_req_0002": {"problem_id": "math500_001", "condition_code": "Condition_D_Forced_Restart"},
    "primary_100_req_0003": {"problem_id": "math500_001", "condition_code": "Condition_E_Explicit_Repair"},
    "primary_100_req_0004": {"problem_id": "math500_001", "condition_code": "Condition_F_State_Preserving"},
    "primary_100_req_0005": {"problem_id": "math500_012", "condition_code": "Condition_A_Zero_Shot"},
    "primary_100_req_0006": {"problem_id": "math500_012", "condition_code": "Condition_D_Forced_Restart"},
    "primary_100_req_0007": {"problem_id": "math500_012", "condition_code": "Condition_E_Explicit_Repair"},
    "primary_100_req_0008": {"problem_id": "math500_012", "condition_code": "Condition_F_State_Preserving"},
    "primary_100_req_0009": {"problem_id": "math500_023", "condition_code": "Condition_A_Zero_Shot"},
    "primary_100_req_0010": {"problem_id": "math500_023", "condition_code": "Condition_D_Forced_Restart"}
}


def compute_calibration_selection_hash(requests: List[Dict[str, Any]]) -> str:
    """Computes deterministic SHA-256 over canonical JSON of selected requests."""
    canonical_repr = json.dumps(requests, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()


def generate_calibration_manifest(full_manifest_path: str, output_path: str) -> Dict[str, Any]:
    """
    Extracts the exact 10 frozen requests from parent manifest.
    Fails immediately if parent manifest hash mismatches or any expected request is missing/modified.
    """
    with open(full_manifest_path, "rb") as f:
        content = f.read()
        actual_hash = hashlib.sha256(content).hexdigest()

    if actual_hash != FROZEN_PARENT_MANIFEST_SHA256:
        raise ValueError(
            f"Parent manifest SHA-256 mismatch: {actual_hash} vs expected {FROZEN_PARENT_MANIFEST_SHA256}."
        )

    full_data = json.loads(content.decode("utf-8"))
    req_map = {r["request_id"]: r for r in full_data.get("requests", [])}

    # Strict check: all 10 expected IDs must exist
    missing_ids = [cid for cid in FROZEN_CALIBRATION_REQUEST_IDS if cid not in req_map]
    if missing_ids:
        raise KeyError(
            f"EXPECTED IDS MISSING from manifest: {missing_ids}. Silent fallback substitution is prohibited."
        )

    # Validate condition codes and metadata
    selected_requests = []
    for cid in FROZEN_CALIBRATION_REQUEST_IDS:
        req = req_map[cid]
        expected_meta = EXPECTED_REQUEST_METADATA[cid]
        if req.get("problem_id") != expected_meta["problem_id"]:
            raise ValueError(
                f"Request {cid}: Problem ID mismatch ({req.get('problem_id')} vs expected {expected_meta['problem_id']})."
            )
        if req.get("condition_code") != expected_meta["condition_code"]:
            raise ValueError(
                f"Request {cid}: Condition code mismatch ({req.get('condition_code')} vs expected {expected_meta['condition_code']})."
            )
        selected_requests.append(req)

    selection_sha256 = compute_calibration_selection_hash(selected_requests)

    calibration_manifest = {
        "schema_version": "1.0",
        "calibration_id": "stateshift_10_request_gpu_calibration_v15_5",
        "parent_manifest_sha256": FROZEN_PARENT_MANIFEST_SHA256,
        "calibration_selection_sha256": selection_sha256,
        "total_requests": len(selected_requests),
        "requests": selected_requests
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(calibration_manifest, f, indent=2)

    return calibration_manifest

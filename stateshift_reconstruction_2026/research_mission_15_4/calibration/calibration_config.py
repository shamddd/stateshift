#!/usr/bin/env python3
"""
StateShift 10-Request Physical Calibration Configuration (Mission 15.4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Design for future RunPod calibration:
- Evaluates actual model loading time, GPU VRAM, empirical tokens/sec,
  and cost per rollout before authorizing the full 400-request experiment.
- Predetermined selection of 10 requests from the frozen manifest.
- Clear non-duplication policy (calibration samples are accounted explicitly).
"""

import os
import sys
import json
import hashlib
from typing import Dict, Any, List

# Predetermined selection of 10 requests from the frozen manifest:
# Covers problem 1 across all 4 conditions, plus 6 additional distinct problems
CALIBRATION_REQUEST_IDS = [
    "req_000_A", "req_000_D", "req_000_E", "req_000_F",  # Problem 0 across all 4 conditions
    "req_001_A", "req_002_A", "req_003_A",               # Problems 1-3 Zero-Shot
    "req_004_D", "req_005_E", "req_006_F"                # Problems 4-6 diverse conditions
]


def generate_calibration_manifest(full_manifest_path: str, output_path: str) -> Dict[str, Any]:
    with open(full_manifest_path, "r", encoding="utf-8") as f:
        full_data = json.load(f)

    req_map = {r["request_id"]: r for r in full_data.get("requests", [])}
    
    # In case IDs in manifest are indexed differently, pick first 10 requests
    selected_requests = []
    if all(cid in req_map for cid in CALIBRATION_REQUEST_IDS):
        selected_requests = [req_map[cid] for cid in CALIBRATION_REQUEST_IDS]
    else:
        # Fallback to first 10 requests of the manifest
        selected_requests = full_data["requests"][:10]

    calibration_manifest = {
        "schema_version": "1.0",
        "calibration_id": "stateshift_10_request_gpu_calibration",
        "target_model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
        "target_model_revision": "c869d27376a8d6728795551322fe323b6",
        "total_requests": len(selected_requests),
        "requests": selected_requests,
        "parent_manifest_sha256": hashlib.sha256(open(full_manifest_path, "rb").read()).hexdigest(),
        "purpose": "Empirical throughput calibration only; does not replace or duplicate full experiment."
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(calibration_manifest, f, indent=2)

    return calibration_manifest

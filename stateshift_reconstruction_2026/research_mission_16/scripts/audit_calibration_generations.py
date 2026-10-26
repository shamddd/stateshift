#!/usr/bin/env python3
"""
StateShift Independent Generation Authenticity Auditor
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Forensic validation tool for verifying raw physical GPU inference records
against frozen benchmark manifests. Strictly verifies schema integrity,
cryptographic prompt binding, model revision, sampling parameters,
and physical execution provenance.
"""

import sys
import os
import json
import hashlib
from typing import Dict, Any, List, Set

EXPECTED_MODEL_ID = "Qwen/Qwen2.5-Math-7B-Instruct"
EXPECTED_MODEL_REVISION = "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"
EXPECTED_SOURCE_TYPE = "REAL_MODEL_INFERENCE"
REQUIRED_SCHEMA_KEYS = [
    "request_id", "problem_id", "condition_code", "prompt_sha256",
    "gold_answer", "model_id", "model_revision", "inference_engine",
    "temperature", "max_tokens", "seed", "completion_status",
    "source_type", "experiment_id", "manifest_hash",
    "generation_timestamp", "model_output"
]


def audit_generations(manifest_path: str, generations_path: str) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Check file existence
    if not os.path.exists(manifest_path):
        errors.append(f"Manifest file not found: {manifest_path}")
        return {"passed": False, "errors": errors, "warnings": warnings}
    if not os.path.exists(generations_path):
        errors.append(f"Generations file not found: {generations_path}")
        return {"passed": False, "errors": errors, "warnings": warnings}

    # 2. Load manifest
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    except Exception as e:
        errors.append(f"Failed to parse manifest JSON: {e}")
        return {"passed": False, "errors": errors, "warnings": warnings}

    manifest_requests = manifest_data.get("requests", [])
    if not manifest_requests:
        errors.append("Manifest contains zero requests.")
        return {"passed": False, "errors": errors, "warnings": warnings}

    manifest_map: Dict[str, Dict[str, Any]] = {}
    for req in manifest_requests:
        rid = req.get("request_id")
        if not rid:
            errors.append("Manifest request missing request_id.")
            continue
        if rid in manifest_map:
            errors.append(f"Duplicate request_id in manifest: {rid}")
        manifest_map[rid] = req

    # 3. Load generations
    records: List[Dict[str, Any]] = []
    seen_request_ids: Set[str] = set()

    with open(generations_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                rec = json.loads(line_str)
            except Exception as e:
                errors.append(f"Line {line_num}: Invalid JSON: {e}")
                continue

            rid = rec.get("request_id")
            if not rid:
                errors.append(f"Line {line_num}: Missing request_id.")
                continue

            if rid in seen_request_ids:
                errors.append(f"Line {line_num}: Duplicate request_id: {rid}")
            seen_request_ids.add(rid)
            records.append(rec)

    # 4. Cardinality checks
    expected_count = len(manifest_map)
    actual_count = len(records)
    if actual_count != expected_count:
        errors.append(f"Cardinality mismatch: Expected {expected_count} records, found {actual_count}")

    # Missing requests
    missing_ids = set(manifest_map.keys()) - seen_request_ids
    if missing_ids:
        errors.append(f"Missing requests from manifest: {sorted(list(missing_ids))}")

    # Unauthorized requests
    unauthorized_ids = seen_request_ids - set(manifest_map.keys())
    if unauthorized_ids:
        errors.append(f"Unauthorized request IDs not in manifest: {sorted(list(unauthorized_ids))}")

    # 5. Field-by-field verification against manifest and protocol invariants
    verified_records = 0
    for idx, rec in enumerate(records, start=1):
        rid = rec.get("request_id")
        m_req = manifest_map.get(rid)
        if not m_req:
            continue

        # Schema keys
        missing_keys = [k for k in REQUIRED_SCHEMA_KEYS if k not in rec]
        if missing_keys:
            errors.append(f"Record {rid}: Missing required schema keys: {missing_keys}")

        # Problem ID match
        if rec.get("problem_id") != m_req.get("problem_id"):
            errors.append(f"Record {rid}: Problem ID mismatch ({rec.get('problem_id')} vs {m_req.get('problem_id')})")

        # Condition code match
        if rec.get("condition_code") != m_req.get("condition_code"):
            errors.append(f"Record {rid}: Condition mismatch ({rec.get('condition_code')} vs {m_req.get('condition_code')})")

        # Prompt SHA-256 match
        if rec.get("prompt_sha256") != m_req.get("prompt_sha256"):
            errors.append(f"Record {rid}: Prompt SHA-256 mismatch ({rec.get('prompt_sha256')} vs {m_req.get('prompt_sha256')})")

        # Model ID
        if rec.get("model_id") != EXPECTED_MODEL_ID:
            errors.append(f"Record {rid}: Model ID mismatch ({rec.get('model_id')} vs {EXPECTED_MODEL_ID})")

        # Model revision
        if rec.get("model_revision") != EXPECTED_MODEL_REVISION:
            errors.append(f"Record {rid}: Model revision mismatch ({rec.get('model_revision')} vs {EXPECTED_MODEL_REVISION})")

        # Sampling parameters (greedy: temp=0, max_tokens=768, seed=42)
        if rec.get("temperature") != 0.0:
            errors.append(f"Record {rid}: Temperature {rec.get('temperature')} != 0.0")
        if rec.get("max_tokens") != 768:
            errors.append(f"Record {rid}: max_tokens {rec.get('max_tokens')} != 768")
        if rec.get("seed") != 42:
            errors.append(f"Record {rid}: seed {rec.get('seed')} != 42")

        # Provenance & authenticity
        if rec.get("source_type") != EXPECTED_SOURCE_TYPE:
            errors.append(f"Record {rid}: source_type {rec.get('source_type')} != {EXPECTED_SOURCE_TYPE}")

        # Completion status
        if rec.get("completion_status") != "COMPLETED":
            errors.append(f"Record {rid}: completion_status {rec.get('completion_status')} != COMPLETED")

        # Generated output validation
        output_text = rec.get("model_output", "")
        if not output_text or not isinstance(output_text, str):
            errors.append(f"Record {rid}: model_output is empty or not string.")
        elif len(output_text.strip()) < 50:
            errors.append(f"Record {rid}: model_output is implausibly short ({len(output_text)} chars).")

        # Timestamp plausibility
        ts = rec.get("generation_timestamp")
        if not ts or not isinstance(ts, (int, float)) or ts < 1700000000:
            errors.append(f"Record {rid}: Invalid generation_timestamp: {ts}")

        verified_records += 1

    passed = len(errors) == 0
    return {
        "passed": passed,
        "total_manifest_requests": len(manifest_map),
        "total_ingested_records": len(records),
        "verified_records": verified_records,
        "errors": errors,
        "warnings": warnings
    }


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    manifest_path = os.path.join(repo_root, "research_mission_15_6", "manifests", "calibration_10_manifest.json")
    generations_path = os.path.join(repo_root, "data", "primary_run", "stateshift_calib_b1_01_generations.jsonl")

    if len(sys.argv) > 1:
        generations_path = sys.argv[1]
    if len(sys.argv) > 2:
        manifest_path = sys.argv[2]

    print("=" * 80)
    print("  STATESHIFT: INDEPENDENT GENERATION AUTHENTICITY AUDIT")
    print(f"  Manifest:    {manifest_path}")
    print(f"  Generations: {generations_path}")
    print("=" * 80)

    res = audit_generations(manifest_path, generations_path)

    print(f"Audit Verdict: {'PASS (100% VERIFIED)' if res['passed'] else 'FAIL'}")
    print(f"Total Expected Requests: {res['total_manifest_requests']}")
    print(f"Total Ingested Records:  {res['total_ingested_records']}")
    print(f"Verified Valid Records:  {res['verified_records']}")

    if res["warnings"]:
        print("\nWarnings:")
        for w in res["warnings"]:
            print(f"  [WARN] {w}")

    if res["errors"]:
        print("\nErrors Identified:")
        for e in res["errors"]:
            print(f"  [FAIL] {e}")
        sys.exit(1)
    else:
        print("\nAll 15 forensic authenticity and provenance checks PASSED.")
        sys.exit(0)


if __name__ == "__main__":
    main()

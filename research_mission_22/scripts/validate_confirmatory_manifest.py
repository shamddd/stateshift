#!/usr/bin/env python3
"""
StateShift Confirmatory Manifest Validator (Mission 22)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Track

Validates:
1. Integrity of candidate pool and confirmatory manifests.
2. SHA-256 cryptographic checksums.
3. 924 requests across 231 problems (exactly 4 conditions per problem).
4. Zero overlap with Study 2 pilot.
5. Invariance of model revision, prompt hashes, and parameters.
"""

import os
import sys
import json
import hashlib
from collections import Counter, defaultdict

EXPECTED_CHECKSUMS = {
    "confirmatory_candidate_pool_manifest.jsonl": {
        "size": 550451,
        "sha256": "5a0ae79aa301d0e5dee51aa18d90a6dd3a0db96b0825e7ad0bb88b91456cb720",
        "records": 354
    },
    "confirmatory_231_manifest.jsonl": {
        "size": 1246234,
        "sha256": "2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5",
        "records": 924
    },
    "confirmatory_231_manifest.json": {
        "size": 1389819,
        "sha256": "3b0114558cdd36d409f2351388ec8fb36724cdf7ac0916e2c3c36420bff55f42",
        "records": 924
    }
}

PINNED_MODEL_REVISION = "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"

def compute_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def validate_manifests():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    pilot_csv = os.path.abspath(os.path.join(base_dir, "..", "data", "study2", "final_verified_outcomes.csv"))
    
    print("=" * 80)
    print("STATESHIFT CONFIRMATORY MANIFEST AUDIT & VALIDATION")
    print("=" * 80)
    
    # 1. Verify pilot outcomes presence
    assert os.path.exists(pilot_csv), f"Pilot CSV not found: {pilot_csv}"
    pilot_ids = set()
    with open(pilot_csv, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx > 0 and line.strip():
                pilot_ids.add(line.split(",")[0].strip())
    print(f"[PASS] Loaded {len(pilot_ids)} pilot problem IDs.")
    
    # 2. Checksum validation
    for fname, exp in EXPECTED_CHECKSUMS.items():
        fpath = os.path.join(data_dir, fname)
        assert os.path.exists(fpath), f"File missing: {fpath}"
        actual_size = os.path.getsize(fpath)
        actual_sha = compute_sha256(fpath)
        
        assert actual_size == exp["size"], f"Size mismatch for {fname}: expected {exp['size']}, got {actual_size}"
        assert actual_sha == exp["sha256"], f"Hash mismatch for {fname}: expected {exp['sha256']}, got {actual_sha}"
        print(f"[PASS] Cryptographic verification: {fname} (SHA256: {actual_sha[:12]}...)")
        
    # 3. Structural inspection of confirmatory_231_manifest.jsonl
    jsonl_path = os.path.join(data_dir, "confirmatory_231_manifest.jsonl")
    requests = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            requests.append(r)
            
            # Verify individual prompt hash
            computed_p_hash = hashlib.sha256(r["prompt_text"].encode("utf-8")).hexdigest()
            assert computed_p_hash == r["prompt_sha256"], f"Line {line_num}: prompt_sha256 mismatch!"
            assert r["model_revision"] == PINNED_MODEL_REVISION, f"Line {line_num}: model_revision mismatch!"
            assert r["temperature"] == 0.0, f"Line {line_num}: temperature must be 0.0!"
            assert r["max_tokens"] == 768, f"Line {line_num}: max_tokens must be 768!"
            assert r["seed"] == 42, f"Line {line_num}: seed must be 42!"
            
    print(f"[PASS] Validated {len(requests)} individual request records and prompt hashes.")
    assert len(requests) == 924, f"Expected 924 requests, got {len(requests)}"
    
    # 4. Problem-level invariants
    by_prob = defaultdict(list)
    for r in requests:
        by_prob[r["problem_id"]].append(r)
        
    assert len(by_prob) == 231, f"Expected 231 unique problems, got {len(by_prob)}"
    
    # Check zero overlap
    overlap = set(by_prob.keys()).intersection(pilot_ids)
    assert len(overlap) == 0, f"Critical failure: Overlap with pilot: {overlap}"
    print(f"[PASS] Zero-overlap invariant confirmed: 0 common problems between pilot and confirmatory set.")
    
    # Check condition completeness for every problem
    expected_conditions = {
        "Condition_A_Zero_Shot",
        "Condition_D_Forced_Restart",
        "Condition_E_Explicit_Repair",
        "Condition_F_State_Preserving"
    }
    
    for pid, plist in by_prob.items():
        assert len(plist) == 4, f"Problem {pid} does not have exactly 4 conditions!"
        conds = set(p["condition_code"] for p in plist)
        assert conds == expected_conditions, f"Problem {pid} missing conditions: {expected_conditions - conds}"
        
    print(f"[PASS] All 231 problems possess complete 4-condition matched batteries (A, D, E, F).")
    
    # Operator balance check
    op_counts = Counter(plist[0]["operator_code"] for plist in by_prob.values())
    assert op_counts["OP01_ARITHMETIC_MISCALCULATION"] == 24
    for k in range(2, 11):
        op_code = [op for op in op_counts if f"OP{k:02d}" in op][0]
        assert op_counts[op_code] == 23, f"Operator {op_code} quota incorrect: {op_counts[op_code]}"
    print(f"[PASS] Operator quotas verified (OP01: 24, OP02-OP10: 23 each = 231 total).")
    
    print("=" * 80)
    print("MANIFEST VALIDATION VERDICT: ALL AUDIT GATES PASSED (100% INTACT)")
    print("=" * 80)
    return True

if __name__ == "__main__":
    validate_manifests()

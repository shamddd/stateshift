#!/usr/bin/env python3
"""
Unit tests for Confirmatory Trial Dataset & Manifest (Mission 22)
Author: Sham Satish Thakare (github.com/shamddd)
"""

import os
import json
import hashlib
import pytest
from collections import Counter, defaultdict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MANIFEST_JSONL = os.path.join(DATA_DIR, "confirmatory_231_manifest.jsonl")
MANIFEST_JSON = os.path.join(DATA_DIR, "confirmatory_231_manifest.json")
CANDIDATE_POOL = os.path.join(DATA_DIR, "confirmatory_candidate_pool_manifest.jsonl")
PILOT_CSV = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "study2", "final_verified_outcomes.csv"))

def test_files_exist():
    assert os.path.exists(MANIFEST_JSONL)
    assert os.path.exists(MANIFEST_JSON)
    assert os.path.exists(CANDIDATE_POOL)
    assert os.path.exists(PILOT_CSV)

def test_candidate_pool_size():
    with open(CANDIDATE_POOL, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) == 354

def test_manifest_record_counts():
    requests = []
    with open(MANIFEST_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                requests.append(json.loads(line))
    assert len(requests) == 924
    
    with open(MANIFEST_JSON, "r", encoding="utf-8") as f:
        manifest_obj = json.load(f)
    assert manifest_obj["total_requests"] == 924
    assert manifest_obj["total_problems"] == 231
    assert len(manifest_obj["requests"]) == 924

def test_zero_overlap_with_pilot():
    pilot_ids = set()
    with open(PILOT_CSV, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx > 0 and line.strip():
                pilot_ids.add(line.split(",")[0].strip())
    assert len(pilot_ids) == 100
    
    with open(MANIFEST_JSONL, "r", encoding="utf-8") as f:
        confirmatory_ids = set(json.loads(line)["problem_id"] for line in f if line.strip())
    assert len(confirmatory_ids) == 231
    
    overlap = confirmatory_ids.intersection(pilot_ids)
    assert len(overlap) == 0

def test_condition_structure_and_hashes():
    with open(MANIFEST_JSONL, "r", encoding="utf-8") as f:
        requests = [json.loads(line) for line in f if line.strip()]
        
    by_prob = defaultdict(list)
    for r in requests:
        by_prob[r["problem_id"]].append(r)
        # Verify prompt hash
        expected_hash = hashlib.sha256(r["prompt_text"].encode("utf-8")).hexdigest()
        assert r["prompt_sha256"] == expected_hash
        assert r["model_revision"] == "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"
        assert r["temperature"] == 0.0
        assert r["max_tokens"] == 768
        assert r["seed"] == 42
        
    expected_conds = {
        "Condition_A_Zero_Shot",
        "Condition_D_Forced_Restart",
        "Condition_E_Explicit_Repair",
        "Condition_F_State_Preserving"
    }
    for pid, rlist in by_prob.items():
        assert len(rlist) == 4
        conds = set(r["condition_code"] for r in rlist)
        assert conds == expected_conds

def test_stratification_quotas():
    with open(MANIFEST_JSONL, "r", encoding="utf-8") as f:
        requests = [json.loads(line) for line in f if line.strip()]
        
    # Get unique problems
    seen = {}
    for r in requests:
        if r["problem_id"] not in seen:
            seen[r["problem_id"]] = r
            
    diff_counts = Counter(r["difficulty_level"] for r in seen.values())
    assert diff_counts[1] == 47
    assert diff_counts[2] == 46
    assert diff_counts[3] == 46
    assert diff_counts[4] == 46
    assert diff_counts[5] == 46
    
    op_counts = Counter(r["operator_code"] for r in seen.values())
    assert op_counts["OP01_ARITHMETIC_MISCALCULATION"] == 24
    for k in range(2, 11):
        op_code = [op for op in op_counts if f"OP{k:02d}" in op][0]
        assert op_counts[op_code] == 23

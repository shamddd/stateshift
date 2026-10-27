#!/usr/bin/env python3
"""
Regression and Audit Tests for Mission 22.1
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Track
"""

import os
import sys
import json
import pytest
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUNNER_SCRIPT = os.path.join(REPO_ROOT, "research_mission_22", "scripts", "run_confirmatory_trial.py")
MANIFEST_PATH = os.path.join(REPO_ROOT, "research_mission_22", "data", "confirmatory_231_manifest.jsonl")

def test_resume_behavior():
    sys.path.insert(0, os.path.join(REPO_ROOT, "research_mission_22", "scripts"))
    from run_confirmatory_trial import load_existing_checkpoint
    
    # Create temp output file with 2 completed records
    temp_out = "/tmp/test_resume_chk.jsonl"
    with open(temp_out, "w") as f:
        f.write(json.dumps({"request_id": "confirmatory_231_req_0001"}) + "\n")
        f.write(json.dumps({"request_id": "confirmatory_231_req_0002"}) + "\n")
        
    completed = load_existing_checkpoint(temp_out)
    assert len(completed) == 2
    assert "confirmatory_231_req_0001" in completed
    assert "confirmatory_231_req_0002" in completed
    
    if os.path.exists(temp_out):
        os.remove(temp_out)

def test_record_serialization_schema():
    sys.path.insert(0, os.path.join(REPO_ROOT, "research_mission_22", "scripts"))
    from run_confirmatory_trial import ConfirmatoryNeuralRunner
    
    runner = ConfirmatoryNeuralRunner(
        manifest_path=MANIFEST_PATH,
        output_path="/tmp/test_schema.jsonl",
        mock_eval=True
    )
    
    sample_req = runner.requests[0]
    rec = runner.execute_request(sample_req)
    
    required_fields = [
        "request_id", "problem_id", "condition_code", "prompt_sha256", "gold_answer",
        "model_id", "model_revision", "tokenizer_revision", "temperature", "max_tokens",
        "seed", "sampling_mode", "prompt_tokens", "output_tokens", "total_tokens",
        "finish_reason", "elapsed_seconds", "generation_timestamp", "execution_id",
        "source_type", "extracted_answer", "is_correct", "model_output"
    ]
    for field in required_fields:
        assert field in rec, f"Missing required field in output record: {field}"
        
    assert rec["source_type"] == "MOCK_LOCAL_TEST"
    assert rec["model_revision"] == "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"

def test_elevated_discordance_power_regression():
    sys.path.insert(0, os.path.join(REPO_ROOT, "research_mission_22", "scripts"))
    from confirmatory_exact_power import exact_mcnemar_power, find_min_sample_size
    
    # Verify N=312 falls short (<80%)
    pw_312 = exact_mcnemar_power(312, 0.14, 0.06)
    assert pw_312 < 0.800
    
    # Verify N=322 achieves >=80%
    pw_322 = exact_mcnemar_power(322, 0.14, 0.06)
    assert pw_322 >= 0.800
    
    min_n = find_min_sample_size(0.80, 0.14, 0.06)
    assert min_n == 322

def test_terminology_governance_in_reports():
    # Audit phase 2 report to verify forbidden terms are absent or explicitly quarantined
    phase2_doc = os.path.join(REPO_ROOT, "research_mission_22_1", "02_DATASET_INDEPENDENCE_CORRECTION.md")
    assert os.path.exists(phase2_doc)
    with open(phase2_doc, "r") as f:
        text = f.read()
    assert "disjoint held-out math-500 confirmatory sample" in text.lower()
    assert "Sample Disjointness (ESTABLISHED & VERIFIED)" in text
    assert "Benchmark Independence (NOT CLAIMED" in text
    assert "Pretraining Independence (NOT CLAIMED" in text

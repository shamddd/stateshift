#!/usr/bin/env python3
"""
Mission 15.2 Unit Tests: Strict Dataset Provenance and Completion Gate
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies all 20 test cases for IndependentDatasetVerifierV2:
1. Valid dataset -> passes
2. Missing model_id -> fails
3. Wrong model_revision -> fails
4. Wrong tokenizer_revision -> fails
5. Wrong temperature -> fails
6. Wrong max_tokens -> fails
7. Missing seed -> fails
8. Wrong prompt hash -> fails
9. Wrong condition_code -> fails
10. Duplicate request_id -> fails
11. Missing request_id -> fails
12. Synthetic provenance (source_type != REAL_MODEL_INFERENCE) -> fails
13. Generation with completion_status == FAILED -> fails
14. Generation with completion_status == TRUNCATED -> fails
15. Generation with completion_status == TIMEOUT -> fails
16. Empty model_output -> fails
17. Malformed JSONL line -> fails
18. Corrupted / unparseable file -> fails
19. Reopening catches modification / in-memory vs disk mismatch -> caught
20. Valid receipt generation -> verified
"""

import os
import sys
import json
import time
import shutil
import hashlib
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_2.evaluation.dataset_verifier_v2 import IndependentDatasetVerifierV2


@pytest.fixture
def test_env():
    tmp_dir = tempfile.mkdtemp()
    
    # Create sample manifest with 3 requests
    manifest_requests = [
        {
            "request_id": f"req_{i:03d}",
            "problem_id": f"prob_{i:03d}",
            "condition_code": "C1_STANDARD",
            "prompt_sha256": hashlib.sha256(f"prompt_{i}".encode()).hexdigest(),
            "gold_answer": "42",
            "model_id": "Qwen/Qwen2.5-Math-7B-Instruct"
        }
        for i in range(1, 4)
    ]
    manifest_data = {"version": "1.0", "requests": manifest_requests}
    manifest_path = os.path.join(tmp_dir, "test_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
        
    with open(manifest_path, "rb") as f:
        manifest_hash = hashlib.sha256(f.read()).hexdigest()
        
    def make_valid_record(req_idx):
        req = manifest_requests[req_idx - 1]
        return {
            "request_id": req["request_id"],
            "problem_id": req["problem_id"],
            "condition_code": req["condition_code"],
            "prompt_sha256": req["prompt_sha256"],
            "gold_answer": req["gold_answer"],
            "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
            "model_revision": "c869d27376a8d6728795551322fe323b6",
            "tokenizer_revision": "c869d27376a8d6728795551322fe323b6",
            "inference_engine": "vllm",
            "inference_engine_version": "0.6.3.post1",
            "temperature": 0.0,
            "max_tokens": 768,
            "seed": 42,
            "sampling_mode": "greedy",
            "completion_status": "COMPLETED",
            "finish_reason": "stop",
            "source_type": "REAL_MODEL_INFERENCE",
            "experiment_id": "exp_runpod_mission15_2",
            "manifest_hash": manifest_hash,
            "generation_timestamp": time.time(),
            "model_output": "The step-by-step reasoning solution is 42."
        }

    yield {
        "dir": tmp_dir,
        "manifest_path": manifest_path,
        "manifest_hash": manifest_hash,
        "manifest_requests": manifest_requests,
        "make_valid_record": make_valid_record
    }
    
    shutil.rmtree(tmp_dir, ignore_errors=True)


def write_dataset(records, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


# Case 1: Valid dataset passes
def test_valid_dataset_passes(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is True
    assert receipt["completed_valid_count"] == 3
    assert len(receipt["errors"]) == 0


# Case 2: Missing model_id fails
def test_missing_model_id(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    del records[0]["model_id"]
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("model_id" in err for err in receipt["errors"])


# Case 3: Wrong model_revision fails
def test_wrong_model_revision(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[0]["model_revision"] = ""
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("model_revision" in err for err in receipt["errors"])


# Case 4: Wrong tokenizer_revision fails
def test_wrong_tokenizer_revision(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[0]["tokenizer_revision"] = ""
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("tokenizer_revision" in err for err in receipt["errors"])


# Case 5: Wrong temperature fails
def test_wrong_temperature(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[1]["temperature"] = 0.7
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("Temperature must be 0.0" in err for err in receipt["errors"])


# Case 6: Wrong max_tokens fails
def test_wrong_max_tokens(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[2]["max_tokens"] = 512
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("Max tokens must be 768" in err for err in receipt["errors"])


# Case 7: Missing seed fails
def test_missing_seed(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    del records[0]["seed"]
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("seed" in err for err in receipt["errors"])


# Case 8: Wrong prompt hash fails
def test_wrong_prompt_hash(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[0]["prompt_sha256"] = "wrong_hash_deadbeef"
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("Prompt hash mismatch" in err for err in receipt["errors"])


# Case 9: Wrong condition fails
def test_wrong_condition_code(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[0]["condition_code"] = "C9_CORRUPTED"
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("Condition mismatch" in err for err in receipt["errors"])


# Case 10: Duplicate request_id fails
def test_duplicate_request_id(test_env):
    records = [test_env["make_valid_record"](1), test_env["make_valid_record"](1), test_env["make_valid_record"](3)]
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert receipt["duplicate_count"] == 1


# Case 11: Missing request_id fails
def test_missing_request_id(test_env):
    records = [test_env["make_valid_record"](1), test_env["make_valid_record"](2)]
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert receipt["missing_count"] == 1


# Case 12: Synthetic provenance fails
def test_synthetic_provenance_rejected(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[0]["source_type"] = "MOCK_SYNTHETIC"
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("Invalid source_type" in err for err in receipt["errors"])


# Case 13: Generation with completion_status == FAILED rejected
def test_failed_completion_status(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[1]["completion_status"] = "FAILED"
    records[1]["finish_reason"] = "error"
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert receipt["failed_count"] == 1


# Case 14: Generation with completion_status == TRUNCATED rejected
def test_truncated_completion_status(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[2]["completion_status"] = "TRUNCATED"
    records[2]["finish_reason"] = "length"
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert receipt["truncated_count"] == 1


# Case 15: Generation with completion_status == TIMEOUT rejected
def test_timeout_completion_status(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[0]["completion_status"] = "TIMEOUT"
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("Non-completed generation status" in err for err in receipt["errors"])


# Case 16: Empty model_output fails
def test_empty_model_output(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    records[0]["model_output"] = "   "
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("Empty model_output" in err for err in receipt["errors"])


# Case 17: Malformed JSONL line fails
def test_malformed_jsonl_line(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(records[0]) + "\n")
        f.write('{"request_id": "bad_json\n')
        f.write(json.dumps(records[2]) + "\n")
        
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("JSON decode failure" in err for err in receipt["errors"])


# Case 18: Corrupted file fails
def test_corrupted_empty_file(test_env):
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        pass
        
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("empty" in err for err in receipt["errors"])


# Case 19: Physical file reopening detects on-disk corruption
def test_physical_disk_reopening(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    
    # Corrupt on-disk file post in-memory preparation
    with open(ds_path, "a", encoding="utf-8") as f:
        f.write("corrupted garbage line\n")
        
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert any("JSON decode failure" in err for err in receipt["errors"])


# Case 20: Valid receipt generation verified
def test_valid_receipt_generation(test_env):
    records = [test_env["make_valid_record"](i) for i in [1, 2, 3]]
    ds_path = os.path.join(test_env["dir"], "dataset.jsonl")
    receipt_path = os.path.join(test_env["dir"], "receipt.json")
    write_dataset(records, ds_path)
    
    verifier = IndependentDatasetVerifierV2(test_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path, receipt_output_path=receipt_path)
    assert passed is True
    assert os.path.exists(receipt_path)
    
    with open(receipt_path, "r", encoding="utf-8") as f:
        saved_receipt = json.load(f)
        
    assert saved_receipt["passed"] is True
    assert saved_receipt["completed_valid_count"] == 3
    assert saved_receipt["dataset_sha256"] == receipt["dataset_sha256"]
    assert saved_receipt["manifest_sha256"] == test_env["manifest_hash"]

"""
Transactional Checkpoint Manager Test Suite (Mission 15.4)
Exercises atomic promotion, monotonicity, schema validation, corruption rejection,
conflict detection, and rollback preservation.
"""

import os
import json
import time
import tempfile
import pytest

from research_mission_15_4.checkpoint.transactional_checkpoint_manager import TransactionalCheckpointManager


@pytest.fixture
def manifest_and_manager(tmp_path):
    manifest_path = os.path.join(tmp_path, "manifest.json")
    man_data = {
        "schema_version": "1.0",
        "requests": [
            {"request_id": f"req_{i:03d}", "problem_id": f"prob_{i}", "condition_code": "A", "prompt_sha256": f"hash_{i}", "gold_answer": str(i)}
            for i in range(10)
        ]
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(man_data, f, indent=2)

    target_path = os.path.join(tmp_path, "dataset.jsonl")
    manager = TransactionalCheckpointManager(target_checkpoint_path=target_path, manifest_path=manifest_path)
    return manifest_path, target_path, manager


def make_record(manager, req_idx, output="Solution text", status="COMPLETED"):
    rid = f"req_{req_idx:03d}"
    return {
        "request_id": rid,
        "problem_id": f"prob_{req_idx}",
        "condition_code": "A",
        "prompt_sha256": f"hash_{req_idx}",
        "gold_answer": str(req_idx),
        "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
        "model_revision": "c869d27376a8d6728795551322fe323b6",
        "tokenizer_revision": "c869d27376a8d6728795551322fe323b6",
        "inference_engine": "vllm",
        "temperature": 0.0,
        "max_tokens": 2048,
        "seed": 42,
        "sampling_mode": "greedy",
        "completion_status": status,
        "finish_reason": "stop",
        "source_type": "REAL_MODEL_INFERENCE",
        "experiment_id": "exp_chk_01",
        "manifest_hash": manager.manifest_sha256,
        "generation_timestamp": time.time(),
        "model_output": output
    }


def test_checkpoint_atomic_promotion(manifest_and_manager, tmp_path):
    """Test standard valid candidate promotion."""
    _, target_path, manager = manifest_and_manager
    cand_path = os.path.join(tmp_path, "cand1.jsonl")
    
    recs = [make_record(manager, 0), make_record(manager, 1)]
    with open(cand_path, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")

    ok, count, msg = manager.promote_candidate_checkpoint(cand_path)
    assert ok
    assert count == 2
    assert os.path.exists(target_path)
    assert len(manager.promoted_records) == 2


def test_checkpoint_monotonicity_rejection(manifest_and_manager, tmp_path):
    """Test rejection when incoming candidate has fewer records than existing promoted."""
    _, target_path, manager = manifest_and_manager
    cand1 = os.path.join(tmp_path, "cand1.jsonl")
    recs = [make_record(manager, 0), make_record(manager, 1), make_record(manager, 2)]
    with open(cand1, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")

    manager.promote_candidate_checkpoint(cand1)
    assert len(manager.promoted_records) == 3

    # Candidate with only 2 records
    cand2 = os.path.join(tmp_path, "cand2.jsonl")
    with open(cand2, "w", encoding="utf-8") as f:
        f.write(json.dumps(recs[0]) + "\n" + json.dumps(recs[1]) + "\n")

    ok, count, msg = manager.promote_candidate_checkpoint(cand2)
    assert not ok
    assert "Regression rejection" in msg
    assert len(manager.promoted_records) == 3


def test_checkpoint_truncated_final_line_rejection(manifest_and_manager, tmp_path):
    """Test candidate with half-written / corrupted final JSON line is rejected."""
    _, _, manager = manifest_and_manager
    cand = os.path.join(tmp_path, "cand_corrupt.jsonl")
    with open(cand, "w", encoding="utf-8") as f:
        f.write(json.dumps(make_record(manager, 0)) + "\n")
        f.write('{"request_id": "req_001", "problem_id": "prob_1", "partially_written')

    ok, count, msg = manager.promote_candidate_checkpoint(cand)
    assert not ok
    assert "JSON decode failure" in msg


def test_checkpoint_duplicate_request_id_in_candidate(manifest_and_manager, tmp_path):
    """Test candidate containing duplicate request IDs within itself is rejected."""
    _, _, manager = manifest_and_manager
    cand = os.path.join(tmp_path, "cand_dup.jsonl")
    with open(cand, "w", encoding="utf-8") as f:
        f.write(json.dumps(make_record(manager, 0)) + "\n")
        f.write(json.dumps(make_record(manager, 0)) + "\n")

    ok, count, msg = manager.promote_candidate_checkpoint(cand)
    assert not ok
    assert "Duplicate request_id" in msg


def test_checkpoint_conflicting_historical_record(manifest_and_manager, tmp_path):
    """Test candidate that alters previously promoted output for the same request ID is rejected."""
    _, _, manager = manifest_and_manager
    cand1 = os.path.join(tmp_path, "cand1.jsonl")
    rec0 = make_record(manager, 0, output="Original immutable answer")
    with open(cand1, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec0) + "\n")
    manager.promote_candidate_checkpoint(cand1)

    # Candidate modifies rec0's output
    cand2 = os.path.join(tmp_path, "cand2.jsonl")
    rec0_modified = make_record(manager, 0, output="Altered answer")
    rec1 = make_record(manager, 1)
    with open(cand2, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec0_modified) + "\n" + json.dumps(rec1) + "\n")

    ok, count, msg = manager.promote_candidate_checkpoint(cand2)
    assert not ok
    assert "Contradiction rejection" in msg


def test_checkpoint_synthetic_provenance_rejection(manifest_and_manager, tmp_path):
    """Test candidate claiming synthetic or simulated provenance is rejected."""
    _, _, manager = manifest_and_manager
    cand = os.path.join(tmp_path, "cand_synth.jsonl")
    rec = make_record(manager, 0)
    rec["source_type"] = "MOCK_SYNTHETIC"
    with open(cand, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

    ok, count, msg = manager.promote_candidate_checkpoint(cand)
    assert not ok
    assert "Invalid source_type" in msg


def test_checkpoint_missing_mandatory_field(manifest_and_manager, tmp_path):
    """Test candidate record missing one of the 20 metadata fields is rejected."""
    _, _, manager = manifest_and_manager
    cand = os.path.join(tmp_path, "cand_missing.jsonl")
    rec = make_record(manager, 0)
    del rec["sampling_mode"]
    with open(cand, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

    ok, count, msg = manager.promote_candidate_checkpoint(cand)
    assert not ok
    assert "Missing required metadata keys" in msg


def test_checkpoint_backup_preservation_on_disk(manifest_and_manager, tmp_path):
    """Test that existing checkpoint is preserved and backed up to .bak on promotion."""
    _, target_path, manager = manifest_and_manager
    cand1 = os.path.join(tmp_path, "cand1.jsonl")
    with open(cand1, "w", encoding="utf-8") as f:
        f.write(json.dumps(make_record(manager, 0)) + "\n")
    manager.promote_candidate_checkpoint(cand1)

    cand2 = os.path.join(tmp_path, "cand2.jsonl")
    with open(cand2, "w", encoding="utf-8") as f:
        f.write(json.dumps(make_record(manager, 0)) + "\n" + json.dumps(make_record(manager, 1)) + "\n")
    manager.promote_candidate_checkpoint(cand2)

    assert os.path.exists(target_path)
    assert os.path.exists(manager.backup_checkpoint_path)
    with open(manager.backup_checkpoint_path, "r", encoding="utf-8") as f:
        lines = [l for l in f if l.strip()]
    assert len(lines) == 1  # Previous version preserved in .bak

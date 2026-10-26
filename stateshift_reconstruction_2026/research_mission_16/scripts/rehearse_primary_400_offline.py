#!/usr/bin/env python3
"""
StateShift 400-Request Offline Experiment Rehearsal (Mission 16)
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Executes a complete, zero-cost, offline dry-run rehearsal of the entire
frozen 400-request primary experiment. Validates manifest loading,
request scheduling, schema validation, atomic fsync persistence,
and idempotent resumption without cloud provisioning or paid compute.
"""

import os
import sys
import json
import time
import shutil

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from research_mission_15_6.runner.remote_experiment_runner import RemoteExperimentRunner


def run_offline_rehearsal():
    manifest_path = os.path.join(REPO_ROOT, "research_mission_15_6", "manifests", "primary_100_manifest.json")
    rehearsal_dir = os.path.join(REPO_ROOT, "data", "rehearsal_primary_400")
    if os.path.exists(rehearsal_dir):
        shutil.rmtree(rehearsal_dir)
    os.makedirs(rehearsal_dir, exist_ok=True)

    output_path = os.path.join(rehearsal_dir, "stateshift_rehearsal_400_generations.jsonl")
    record_path = os.path.join(rehearsal_dir, "execution_record.json")
    heartbeat_path = os.path.join(rehearsal_dir, "heartbeat.json")

    print("=" * 80)
    print("  STATESHIFT: 400-REQUEST PRIMARY OFFLINE REHEARSAL")
    print(f"  Manifest: {manifest_path}")
    print(f"  Output:   {output_path}")
    print("=" * 80)

    # 1. First Pass: Run first 200 requests (simulating partial execution)
    print("\n[Phase 1] Executing Partial Run (Requests 1 to 200)...")
    t0 = time.time()
    runner_p1 = RemoteExperimentRunner(
        manifest_path=manifest_path,
        output_file=output_path,
        record_file=record_path,
        heartbeat_file=heartbeat_path,
        experiment_id="stateshift_rehearsal_400",
        dry_run=True,
        limit_requests=200
    )
    runner_p1.run()
    elapsed_p1 = time.time() - t0
    print(f"[Phase 1 Complete] Ingested {len(runner_p1.completed_request_ids)} records in {elapsed_p1:.2f}s.")

    # 2. Second Pass: Resume from Request 201 to 400
    print("\n[Phase 2] Resuming from Request 201 to 400...")
    t1 = time.time()
    runner_p2 = RemoteExperimentRunner(
        manifest_path=manifest_path,
        output_file=output_path,
        record_file=record_path,
        heartbeat_file=heartbeat_path,
        experiment_id="stateshift_rehearsal_400",
        dry_run=True,
        limit_requests=400
    )
    assert len(runner_p2.completed_request_ids) == 200, "Resume failed to index 200 existing records!"
    runner_p2.run()
    elapsed_p2 = time.time() - t1
    print(f"[Phase 2 Complete] Resumed and reached {len(runner_p2.completed_request_ids)} records in {elapsed_p2:.2f}s.")

    # 3. Third Pass: Idempotency check (re-run on completed dataset)
    print("\n[Phase 3] Testing Idempotent Re-execution on Completed Output...")
    runner_p3 = RemoteExperimentRunner(
        manifest_path=manifest_path,
        output_file=output_path,
        record_file=record_path,
        heartbeat_file=heartbeat_path,
        experiment_id="stateshift_rehearsal_400",
        dry_run=True,
        limit_requests=400
    )
    assert len(runner_p3.completed_request_ids) == 400, "Existing completed set is not 400!"
    runner_p3.run()
    assert len(runner_p3.completed_request_ids) == 400, "Idempotent re-run altered completed set!"
    print("[Phase 3 Complete] Confirmed 100% idempotent: zero redundant rollouts executed.")

    # 4. Forensic Validation of Generated Output File
    print("\n[Phase 4] Verifying Final Output File Integrity...")
    with open(output_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    assert len(records) == 400, f"Expected 400 records on disk, found {len(records)}"
    seen_rids = set()
    condition_counts = {}
    for r in records:
        rid = r["request_id"]
        assert rid not in seen_rids, f"Duplicate request_id: {rid}"
        seen_rids.add(rid)
        c = r["condition_code"]
        condition_counts[c] = condition_counts.get(c, 0) + 1
        assert r["experiment_id"] == "stateshift_rehearsal_400"
        assert r["model_id"] == "Qwen/Qwen2.5-Math-7B-Instruct"
        assert r["temperature"] == 0.0
        assert r["seed"] == 42
        assert len(r["model_output"]) > 0

    print(f"Total Unique Ingested Records: {len(seen_rids)} / 400")
    print(f"Condition Distribution:        {condition_counts}")
    assert condition_counts == {
        "Condition_A_Zero_Shot": 100,
        "Condition_D_Forced_Restart": 100,
        "Condition_E_Explicit_Repair": 100,
        "Condition_F_State_Preserving": 100
    }, "Condition distribution mismatch!"

    print("\n" + "=" * 80)
    print("  400-REQUEST PRIMARY OFFLINE REHEARSAL: 100% SUCCESS")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_offline_rehearsal()
    sys.exit(0 if success else 1)

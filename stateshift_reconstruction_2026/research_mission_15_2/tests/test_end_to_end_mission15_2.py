#!/usr/bin/env python3
"""
Mission 15.2 End-to-End Integration Tests (15 Scenarios)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies all 15 End-to-End CPU-Only Integration Scenarios:
1. Normal 400-request completion -> NORMAL_COMPLETED
2. Budget breach at 143 records -> Provider termination first -> EMERGENCY_TERMINATED
3. SFTP hangs during budget breach -> Provider termination dispatched -> Not blocked
4. Provider API fails once then retries -> RETRY_PENDING -> Succeeded
5. Provider API fails repeatedly -> TERMINATION_UNCONFIRMED escalated
6. Provider reports STOPPED -> verify_pod_terminated rejects destruction
7. Controller restarts after dispatch -> Rehydrates state and verifies
8. Final file corrupted -> Verifier rejects -> VERIFICATION_FAILED
9. Model revision missing -> Verifier rejects -> VERIFICATION_FAILED
10. Decoding config differs -> Verifier rejects -> VERIFICATION_FAILED
11. 400 IDs but 3 failed generations -> Verifier rejects incomplete valid count
12. Synthetic record inserted -> Verifier rejects contamination
13. Pod destroyed with 143 records -> Partial dataset preserved, incomplete receipt
14. Provider termination succeeds -> Termination receipt confirms destruction
15. Provider state cannot be verified -> Marked TERMINATION_UNCONFIRMED in receipt
"""

import os
import sys
import time
import json
import shutil
import hashlib
import tempfile
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_2.runner.robust_cost_controller_v8 import (
    RobustCostControllerV8, ShutdownLifecycleState
)
from research_mission_15_2.runner.robust_cloud_orchestrator_v9 import (
    RobustCloudOrchestratorV9, OrchestratorStateV9, ExecutionMode
)
from research_mission_15_2.transport.runpod_transport_v2 import (
    ProductionRunPodTransportV2, RunPodAPIError
)
from research_mission_15_2.evaluation.dataset_verifier_v2 import (
    IndependentDatasetVerifierV2
)


@pytest.fixture
def e2e_env():
    tmp_dir = tempfile.mkdtemp()
    manifest_requests = [
        {
            "request_id": f"req_{i:03d}",
            "problem_id": f"prob_{i:03d}",
            "condition_code": "C1_STANDARD",
            "prompt_sha256": hashlib.sha256(f"p_{i}".encode()).hexdigest(),
            "gold_answer": "42",
            "model_id": "Qwen/Qwen2.5-Math-7B-Instruct"
        }
        for i in range(1, 401)
    ]
    manifest_data = {"version": "1.0", "requests": manifest_requests}
    manifest_path = os.path.join(tmp_dir, "manifest_400.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
        
    with open(manifest_path, "rb") as f:
        manifest_hash = hashlib.sha256(f.read()).hexdigest()
        
    def make_record(i, status="COMPLETED", output="Reasoning sol 42.", source="REAL_MODEL_INFERENCE",
                    temp=0.0, max_tok=768, seed=42, rev="c869d27376a8d6728795551322fe323b6"):
        req = manifest_requests[i - 1]
        return {
            "request_id": req["request_id"],
            "problem_id": req["problem_id"],
            "condition_code": req["condition_code"],
            "prompt_sha256": req["prompt_sha256"],
            "gold_answer": req["gold_answer"],
            "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
            "model_revision": rev,
            "tokenizer_revision": rev,
            "inference_engine": "vllm",
            "inference_engine_version": "0.6.3.post1",
            "temperature": temp,
            "max_tokens": max_tok,
            "seed": seed,
            "sampling_mode": "greedy",
            "completion_status": status,
            "finish_reason": "stop" if status == "COMPLETED" else "error",
            "source_type": source,
            "experiment_id": "exp_e2e_400",
            "manifest_hash": manifest_hash,
            "generation_timestamp": time.time(),
            "model_output": output
        }

    yield {
        "dir": tmp_dir,
        "manifest_path": manifest_path,
        "manifest_hash": manifest_hash,
        "make_record": make_record,
        "manifest_requests": manifest_requests
    }
    shutil.rmtree(tmp_dir, ignore_errors=True)


# Scenario 1: Normal 400-request completion
def test_scenario_1_normal_400_completion(e2e_env):
    records = [e2e_env["make_record"](i) for i in range(1, 401)]
    ds_path = os.path.join(e2e_env["dir"], "dataset_400.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
            
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.verify_pod_terminated.return_value = True
    
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s1",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_normal",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s1"),
        transport=mock_transport,
        mode=ExecutionMode.DRY_RUN
    )
    
    passed = orchestrator.finalize_and_verify(ds_path)
    assert passed is True
    assert orchestrator.state == OrchestratorStateV9.NORMAL_COMPLETED


# Scenario 2: Budget breach at 143 records -> Provider termination first
def test_scenario_2_budget_breach_provider_first(e2e_env):
    call_order = []
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.side_effect = lambda pid: (call_order.append("terminate_pod"), (True, {}))[1]
    mock_transport.verify_pod_terminated.side_effect = lambda pid, **kw: (call_order.append("verify_terminated"), True)[1]
    
    # Write 143 records on simulated remote
    remote_file = os.path.join(e2e_env["dir"], "remote_143.jsonl")
    with open(remote_file, "w", encoding="utf-8") as f:
        for i in range(1, 144):
            f.write(json.dumps(e2e_env["make_record"](i)) + "\n")
            
    def fake_fetch(rem, loc, **kw):
        call_order.append("fetch_file")
        shutil.copyfile(remote_file, loc)
        return True
    mock_transport.fetch_file.side_effect = fake_fetch

    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s2",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s2",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s2"),
        transport=mock_transport,
        mode=ExecutionMode.DRY_RUN
    )

    success = orchestrator.terminate_emergency(
        reason="Budget limit $2.00 reached at rollout 143",
        emergency_sync=True,
        remote_output_file=remote_file
    )
    assert success is True
    assert orchestrator.state == OrchestratorStateV9.EMERGENCY_TERMINATED
    # Confirm provider termination called BEFORE fetch
    assert call_order[0] == "terminate_pod"
    assert call_order[1] == "verify_terminated"
    assert "fetch_file" in call_order[2:]


# Scenario 3: SFTP hangs during budget breach
def test_scenario_3_sftp_hangs_nonblocking(e2e_env):
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {})
    mock_transport.verify_pod_terminated.return_value = True
    
    # Simulate SFTP timeout / hang
    def hang_fetch(rem, loc, **kw):
        raise TimeoutError("SFTP socket timeout after 10s")
    mock_transport.fetch_file.side_effect = hang_fetch

    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s3",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s3",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s3"),
        transport=mock_transport,
        mode=ExecutionMode.DRY_RUN
    )

    # Emergency termination must not be blocked or fail due to SFTP hang
    success = orchestrator.terminate_emergency(
        reason="Budget breach with SFTP hang",
        emergency_sync=True,
        remote_output_file="/workspace/output.jsonl"
    )
    assert success is True
    assert orchestrator.state == OrchestratorStateV9.EMERGENCY_TERMINATED
    assert mock_transport.terminate_pod.called


# Scenario 4: Provider API fails once then retries
def test_scenario_4_provider_api_transient_failure_retry(e2e_env):
    attempts = []
    def flaky_callback(reason):
        attempts.append(len(attempts) + 1)
        if len(attempts) == 1:
            raise ConnectionError("502 Bad Gateway")
        return True

    ctrl = RobustCostControllerV8(
        experiment_id="exp_s4",
        max_cost_usd=2.00,
        state_dir=os.path.join(e2e_env["dir"], "audit_s4"),
        retry_backoff_seconds=0.01,
        emergency_shutdown_callback=flaky_callback
    )
    ctrl.initialize_session(pod_metadata={"uptimeSeconds": 8500})
    
    # Tick 1: Triggers breach, callback fails -> RETRY_PENDING
    res1 = ctrl.check_and_enforce_budget()
    assert res1["action_taken"] == "RETRY_PENDING"
    assert ctrl.shutdown_state == ShutdownLifecycleState.RETRY_PENDING
    assert len(attempts) == 1
    
    # Tick 2: Retries and callback succeeds -> PROVIDER_CONFIRMED
    res2 = ctrl.check_and_enforce_budget()
    assert res2["action_taken"] == "SHUTDOWN_CONFIRMED"
    assert ctrl.shutdown_state == ShutdownLifecycleState.PROVIDER_CONFIRMED
    assert len(attempts) == 2


# Scenario 5: Provider API fails repeatedly -> TERMINATION_UNCONFIRMED
def test_scenario_5_provider_api_repeated_failures(e2e_env):
    def always_failing_callback(reason):
        raise RunPodAPIError("500 Persistent Internal Server Error")

    ctrl = RobustCostControllerV8(
        experiment_id="exp_s5",
        max_cost_usd=2.00,
        state_dir=os.path.join(e2e_env["dir"], "audit_s5"),
        max_shutdown_retries=2,
        retry_backoff_seconds=0.01,
        emergency_shutdown_callback=always_failing_callback
    )
    ctrl.initialize_session(pod_metadata={"uptimeSeconds": 8500})
    
    ctrl.check_and_enforce_budget() # Attempt 1 -> RETRY_PENDING
    ctrl.check_and_enforce_budget() # Attempt 2 -> RETRY_PENDING
    res3 = ctrl.check_and_enforce_budget() # Retries exhausted
    
    assert ctrl.shutdown_state == ShutdownLifecycleState.TERMINATION_UNCONFIRMED
    assert res3["action_taken"] == "ESCALATED_UNCONFIRMED"


# Scenario 6: Provider reports STOPPED -> verify_pod_terminated rejects destruction
def test_scenario_6_provider_reports_stopped(e2e_env):
    mock_http = MagicMock()
    mock_http.return_value = {
        "pod": {"id": "pod_s6", "desiredStatus": "STOPPED", "runtime": None}
    }
    transport = ProductionRunPodTransportV2(api_key="mock", http_client=mock_http)
    
    is_term = transport.verify_pod_terminated("pod_s6", max_checks=1, delay_seconds=0.01)
    assert is_term is False


# Scenario 7: Controller restarts after dispatch -> Rehydrates state
def test_scenario_7_controller_rehydrates_state(e2e_env):
    audit_dir = os.path.join(e2e_env["dir"], "audit_s7")
    ctrl1 = RobustCostControllerV8(
        experiment_id="exp_s7",
        max_cost_usd=2.00,
        state_dir=audit_dir,
        emergency_shutdown_callback=lambda r: True
    )
    ctrl1.initialize_session(pod_metadata={"uptimeSeconds": 8500})
    ctrl1.check_and_enforce_budget()
    assert ctrl1.shutdown_state == ShutdownLifecycleState.PROVIDER_CONFIRMED
    
    # New instance simulates process crash and rehydration
    ctrl2 = RobustCostControllerV8(
        experiment_id="exp_s7",
        max_cost_usd=2.00,
        state_dir=audit_dir
    )
    assert ctrl2.shutdown_state == ShutdownLifecycleState.PROVIDER_CONFIRMED
    res = ctrl2.check_and_enforce_budget()
    assert res["action_taken"] == "NONE"


# Scenario 8: Final file corrupted -> Verifier rejects
def test_scenario_8_final_file_corrupted(e2e_env):
    ds_path = os.path.join(e2e_env["dir"], "dataset_s8.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        for i in range(1, 400):
            f.write(json.dumps(e2e_env["make_record"](i)) + "\n")
        f.write('{"request_id": "corrupted_incomplete_json\n')
        
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s8",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s8",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s8"),
        mode=ExecutionMode.DRY_RUN
    )
    passed = orchestrator.finalize_and_verify(ds_path)
    assert passed is False
    assert orchestrator.state == OrchestratorStateV9.VERIFICATION_FAILED


# Scenario 9: Model revision missing -> Verifier rejects
def test_scenario_9_model_revision_missing(e2e_env):
    ds_path = os.path.join(e2e_env["dir"], "dataset_s9.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        for i in range(1, 401):
            rec = e2e_env["make_record"](i, rev="")
            f.write(json.dumps(rec) + "\n")
            
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s9",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s9",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s9"),
        mode=ExecutionMode.DRY_RUN
    )
    passed = orchestrator.finalize_and_verify(ds_path)
    assert passed is False
    assert orchestrator.state == OrchestratorStateV9.VERIFICATION_FAILED


# Scenario 10: Decoding config differs -> Verifier rejects
def test_scenario_10_decoding_config_differs(e2e_env):
    ds_path = os.path.join(e2e_env["dir"], "dataset_s10.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        for i in range(1, 401):
            temp_val = 0.5 if i == 50 else 0.0
            rec = e2e_env["make_record"](i, temp=temp_val)
            f.write(json.dumps(rec) + "\n")
            
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s10",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s10",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s10"),
        mode=ExecutionMode.DRY_RUN
    )
    passed = orchestrator.finalize_and_verify(ds_path)
    assert passed is False
    assert orchestrator.state == OrchestratorStateV9.VERIFICATION_FAILED


# Scenario 11: 400 IDs but 3 failed generations -> Incomplete
def test_scenario_11_failed_generations_incomplete(e2e_env):
    ds_path = os.path.join(e2e_env["dir"], "dataset_s11.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        for i in range(1, 401):
            stat = "FAILED" if i in [10, 20, 30] else "COMPLETED"
            rec = e2e_env["make_record"](i, status=stat)
            f.write(json.dumps(rec) + "\n")
            
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s11",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s11",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s11"),
        mode=ExecutionMode.DRY_RUN
    )
    passed = orchestrator.finalize_and_verify(ds_path)
    assert passed is False
    assert orchestrator.state == OrchestratorStateV9.VERIFICATION_FAILED


# Scenario 12: Synthetic record inserted -> Contamination rejected
def test_scenario_12_synthetic_record_rejected(e2e_env):
    ds_path = os.path.join(e2e_env["dir"], "dataset_s12.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        for i in range(1, 401):
            out = "SYNTHETIC INFRASTRUCTURE TEST output" if i == 15 else "Valid real solution."
            rec = e2e_env["make_record"](i, output=out)
            f.write(json.dumps(rec) + "\n")
            
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s12",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s12",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s12"),
        mode=ExecutionMode.DRY_RUN
    )
    passed = orchestrator.finalize_and_verify(ds_path)
    assert passed is False
    assert orchestrator.state == OrchestratorStateV9.VERIFICATION_FAILED


# Scenario 13: Pod destroyed with 143 records -> Incomplete
def test_scenario_13_partial_143_records_incomplete(e2e_env):
    ds_path = os.path.join(e2e_env["dir"], "dataset_s13.jsonl")
    with open(ds_path, "w", encoding="utf-8") as f:
        for i in range(1, 144):
            f.write(json.dumps(e2e_env["make_record"](i)) + "\n")
            
    verifier = IndependentDatasetVerifierV2(e2e_env["manifest_path"])
    passed, receipt = verifier.verify_final_local_dataset(ds_path)
    assert passed is False
    assert receipt["total_records_found"] == 143
    assert receipt["missing_count"] == 257


# Scenario 14: Provider termination succeeds -> Recorded in receipt
def test_scenario_14_provider_termination_receipt_success(e2e_env):
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {"podTerminate": True})
    mock_transport.verify_pod_terminated.return_value = True
    
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s14",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s14",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s14"),
        transport=mock_transport,
        mode=ExecutionMode.DRY_RUN
    )
    
    success = orchestrator.terminate_emergency("Manual test shutdown")
    assert success is True
    receipt_path = os.path.join(e2e_env["dir"], "data_s14", "termination_receipt_exp_s14.json")
    assert os.path.exists(receipt_path)
    with open(receipt_path, "r") as rf:
        rc = json.load(rf)
    assert rc["confirmed_by_provider"] is True
    assert rc["final_state"] == "EMERGENCY_TERMINATED"


# Scenario 15: Provider state cannot be verified -> Marked unconfirmed
def test_scenario_15_provider_unconfirmed_in_receipt(e2e_env):
    mock_transport = MagicMock(spec=ProductionRunPodTransportV2)
    mock_transport.terminate_pod.return_value = (True, {})
    mock_transport.verify_pod_terminated.return_value = False # Unconfirmed
    
    orchestrator = RobustCloudOrchestratorV9(
        experiment_id="exp_s15",
        manifest_path=e2e_env["manifest_path"],
        pod_id="pod_s15",
        local_data_dir=os.path.join(e2e_env["dir"], "data_s15"),
        transport=mock_transport,
        mode=ExecutionMode.DRY_RUN
    )
    
    success = orchestrator.terminate_emergency("Unconfirmed test shutdown")
    assert success is False
    assert orchestrator.state == OrchestratorStateV9.TERMINATION_UNCONFIRMED
    receipt_path = os.path.join(e2e_env["dir"], "data_s15", "termination_receipt_exp_s15.json")
    with open(receipt_path, "r") as rf:
        rc = json.load(rf)
    assert rc["confirmed_by_provider"] is False
    assert rc["final_state"] == "TERMINATION_UNCONFIRMED"

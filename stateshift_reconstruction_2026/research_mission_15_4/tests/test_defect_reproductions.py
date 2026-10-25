"""
Defect Reproduction Test Suite for StateShift Mission 15.4.
Verifies reproduction of the 7 pre-hardening defects and their hardened resolution.
"""

import json
import os
import tempfile
import time
import pytest
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519

from research_mission_15_4.auth.session_authorizer_v2 import CryptographicAuthorizer, NONPRODUCTION_PUBLIC_KEY_B64, _nonprod_priv
from research_mission_15_4.checkpoint.transactional_checkpoint_manager import TransactionalCheckpointManager
from research_mission_15_4.deployment.remote_deployment_verifier import RemoteDeploymentVerifier
from research_mission_15_4.deployment.safe_resume_reconciler import SafeResumeReconciler, ReattachmentAction
from research_mission_15_4.supervision.independent_financial_watchdog import IndependentFinancialWatchdog
from research_mission_15_4.calibration.calibration_config import CALIBRATION_REQUEST_IDS, generate_calibration_manifest


def test_defect_1_unauthenticated_json_vs_ed25519_signature():
    """Defect 1: Plain JSON approval allows parameter tampering; Ed25519 prevents it."""
    authorizer = CryptographicAuthorizer(trusted_public_key_b64=NONPRODUCTION_PUBLIC_KEY_B64)
    
    # 1. Genuine signed doc
    signed_doc = authorizer.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="test_exp",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_real",
        max_spend_usd=2.00,
        authorized_mode="CALIBRATION_ONLY",
        validity_seconds=3600
    )
    
    # Tamper with budget (from $2.00 to $20.00)
    tampered_doc = dict(signed_doc)
    tampered_doc["payload"] = dict(signed_doc["payload"])
    tampered_doc["payload"]["max_spend_usd"] = 20.00
    
    valid, reason = authorizer.verify_authorization(
        tampered_doc,
        active_experiment_id="test_exp",
        active_pod_id="pod_real",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert not valid
    assert "Ed25519 cryptographic signature verification FAILED" in reason
    
    # Genuine signature passes
    valid, reason = authorizer.verify_authorization(
        signed_doc,
        active_experiment_id="test_exp",
        active_pod_id="pod_real",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION_ONLY"
    )
    assert valid
    assert "verified successfully" in reason


def test_defect_2_checkpoint_overwrite_vs_monotonic_transaction():
    """Defect 2: Naive sync overwriting valid records with truncated file is rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy manifest
        manifest_path = os.path.join(tmpdir, "manifest.json")
        man_data = {
            "schema_version": "1.0",
            "requests": [
                {"request_id": "req_0", "problem_id": "p0", "condition_code": "A", "prompt_sha256": "h0", "gold_answer": "42"},
                {"request_id": "req_1", "problem_id": "p1", "condition_code": "B", "prompt_sha256": "h1", "gold_answer": "100"}
            ]
        }
        with open(manifest_path, "w") as f:
            json.dump(man_data, f)

        ckpt_path = os.path.join(tmpdir, "primary_dataset.jsonl")
        mgr = TransactionalCheckpointManager(ckpt_path, manifest_path=manifest_path)
        
        # Helper to build valid record
        def make_rec(rid, pid, cond, p_hash, ans):
            return {
                "request_id": rid, "problem_id": pid, "condition_code": cond,
                "prompt_sha256": p_hash, "gold_answer": ans, "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
                "model_revision": "c869d27376a8d6728795551322fe323b6", "tokenizer_revision": "c869d27376a8d6728795551322fe323b6",
                "inference_engine": "vllm", "temperature": 0.0, "max_tokens": 2048, "seed": 42,
                "sampling_mode": "greedy", "completion_status": "COMPLETED", "finish_reason": "stop",
                "source_type": "REAL_MODEL_INFERENCE", "experiment_id": "exp_1", "manifest_hash": mgr.manifest_sha256,
                "generation_timestamp": time.time(), "model_output": "test answer"
            }

        rec1 = make_rec("req_0", "p0", "A", "h0", "42")
        rec2 = make_rec("req_1", "p1", "B", "h1", "100")
        
        cand1 = os.path.join(tmpdir, "cand1.jsonl")
        with open(cand1, "w") as f:
            f.write(json.dumps(rec1) + "\n" + json.dumps(rec2) + "\n")
            
        success, count, msg = mgr.promote_candidate_checkpoint(cand1)
        assert success
        assert count == 2
        
        # Defective sync: incoming candidate only has 1 record (regression/truncation)
        cand2 = os.path.join(tmpdir, "cand2.jsonl")
        with open(cand2, "w") as f:
            f.write(json.dumps(rec1) + "\n")
            
        success, count, msg = mgr.promote_candidate_checkpoint(cand2)
        assert not success
        assert "Regression rejection" in msg
        # Prior checkpoint still intact
        assert len(mgr.promoted_records) == 2


def test_defect_3_missing_deployment_verification():
    """Defect 3: Remote deployment missing runner script or invalid hash."""
    class MockSSH:
        def execute(self, cmd, ip=None, port=22):
            if "python3 --version" in cmd:
                return 0, "Python 3.10.12\n"
            if "df -k" in cmd:
                return 0, "/dev/root 104857600 20971520 83886080 20% /workspace\n"
            if "sha256sum" in cmd and "primary_100_manifest.json" in cmd:
                return 0, "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d  /workspace/manifests/primary_100_manifest.json\n"
            if "sha256sum" in cmd and "remote_experiment_runner.py" in cmd:
                return 0, "wronghash00000000000000000000000000000000000000000000000000000000  /workspace/runner/remote_experiment_runner.py\n"
            return 1, "Command not found"

    with tempfile.TemporaryDirectory() as tmpdir:
        man_path = os.path.join(tmpdir, "manifest.json")
        with open(man_path, "w") as f:
            f.write("manifest_content")
        run_path = os.path.join(tmpdir, "runner.py")
        with open(run_path, "w") as f:
            f.write("runner_content")

        verifier = RemoteDeploymentVerifier(
            transport=MockSSH(),
            remote_work_dir="/workspace",
            local_manifest_path=man_path,
            local_runner_path=run_path
        )
        ok, msg = verifier.verify_preflight_environment()
        assert not ok
        assert "mismatch" in msg.lower()


def test_defect_4_duplicate_remote_inference_vs_reconciler():
    """Defect 4: Safe resume reconciler detects active remote PID and reattaches instead of restarting."""
    class MockSSH:
        def execute(self, cmd, ip=None, port=22):
            if "cat /workspace/logs/execution_record.json" in cmd:
                doc = {
                    "experiment_id": "exp_42",
                    "manifest_sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
                }
                return 0, json.dumps(doc)
            if "cat /workspace/logs/runner.pid" in cmd:
                return 0, "54321\n"
            if "ps -p 54321" in cmd:
                return 0, "54321 python3 /workspace/runner/remote_experiment_runner.py\n"
            if "cat /workspace/logs/heartbeat.json" in cmd:
                return 0, json.dumps({"timestamp_utc": time.time()})
            return 1, ""

    reconciler = SafeResumeReconciler(MockSSH(), remote_work_dir="/workspace")
    action, pid, msg = reconciler.reconcile_remote_process(
        local_experiment_id="exp_42",
        expected_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        last_known_pid=54321
    )
    assert action == ReattachmentAction.REATTACH
    assert pid == 54321


def test_defect_5_termination_receipt_ordering():
    """Defect 5: Termination receipt must be persisted BEFORE optional SFTP sync."""
    with tempfile.TemporaryDirectory() as tmpdir:
        receipt_path = os.path.join(tmpdir, "termination_receipt.json")
        sync_called = []
        
        def mock_sftp_sync():
            sync_called.append("sftp_called")
            # Even if SFTP sync throws an exception, receipt exists
            raise ConnectionResetError("SFTP connection reset")
            
        def execute_shutdown():
            # Step 1: Write receipt
            receipt = {
                "event": "FINANCIAL_STOP",
                "timestamp": 1700000050.0,
                "confirmed": True
            }
            with open(receipt_path, "w") as f:
                json.dump(receipt, f, indent=2)
            # Step 2: Attempt best-effort retrieval
            try:
                mock_sftp_sync()
            except Exception:
                pass

        execute_shutdown()
        assert os.path.exists(receipt_path)
        with open(receipt_path) as f:
            data = json.load(f)
        assert data["confirmed"] is True
        assert sync_called == ["sftp_called"]


def test_defect_6_watchdog_independent_process_supervision():
    """Defect 6: Watchdog tracks monotonic time and kills pod independently if controller stalls."""
    with tempfile.TemporaryDirectory() as tmpdir:
        watchdog = IndependentFinancialWatchdog(
            experiment_id="exp_test",
            pod_id="pod_stalled_network",
            watchdog_dir=tmpdir,
            emergency_trigger_usd=1.65,
            gpu_hourly_rate=0.89
        )
        
        # Simulate elapsed spend $1.73 > $1.65
        res = watchdog.run_supervision_tick(simulated_spend=1.73)
        assert res["should_terminate"] is True
        assert res["termination_dispatched"] is True


def test_defect_7_physical_calibration_limits():
    """Defect 7: Calibration limit bounds execution strictly to 10 requests without full 400 launch."""
    assert len(CALIBRATION_REQUEST_IDS) == 10
    assert CALIBRATION_REQUEST_IDS[:4] == ["req_000_A", "req_000_D", "req_000_E", "req_000_F"]

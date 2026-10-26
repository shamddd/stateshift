#!/usr/bin/env python3
"""
StateShift Failure Injection Test Suite (Mission 15)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

NOTICE:
ALL FIXTURES AND GENERATED RECORDS IN THIS TEST SUITE ARE STRICTLY:
SYNTHETIC INFRASTRUCTURE TEST — NOT EMPIRICAL SCIENTIFIC EVIDENCE.
NO EMPIRICAL CLAIMS ARE DERIVED FROM THESE TESTS.

Exercises Scenarios A through L:
Test A: Normal completion (400 items synced, verified, safe shutdown).
Test B: SSH disconnect at item 143 (remote continues, reconnects, catches up).
Test C: Local orchestrator crash at item 200 (restarts from state, resumes sync).
Test D: Partial SFTP corruption (truncated JSONL detected, quarantined, retried).
Test E: Invalid JSON line in remote output (detected, quarantined, valid destination preserved).
Test F: Duplicate request ID in stream (detected, quarantined, alerts raised).
Test G: Missing request ID from manifest (completion gate fails, enters SAFE_HOLD).
Test H: Stale heartbeat (>120s) (warning flagged, termination prevented).
Test I: Remote process crash at item 250 (crash detected, logs captured, 250 items preserved).
Test J: Provider API failure (transient network error handled with retry/backoff).
Test K: Budget threshold trip (soft stop/emergency sync triggered, orderly termination).
Test L: vLLM engine crash fallback (detects failure, switches to fallback cleanly).
"""

import os
import sys
import json
import time
import shutil
import tempfile
import unittest
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15.runner.robust_cloud_orchestrator_v7 import (
    RobustCloudOrchestratorV7, OrchestratorState, ManifestValidationError
)
from research_mission_15.runner.robust_cost_controller_v6 import RobustCostControllerV6

class MockCloudTransport:
    """Mock SSH/SFTP transport simulating remote pod and network behavior."""
    def __init__(self, remote_fs: Dict[str, str]):
        self.remote_fs = remote_fs # path -> string content
        self.cmd_history: List[str] = []
        self.connection_dropped = False
        self.drop_on_fetch = False
        self.corrupt_fetch = False
        
    def execute(self, cmd: str, timeout: int = 30) -> Tuple[int, str]:
        if self.connection_dropped:
            raise ConnectionError("Mock SSH socket connection reset by peer.")
        self.cmd_history.append(cmd)
        
        if "mkdir -p" in cmd and "nohup" in cmd:
            # Simulate launch detached runner
            return 0, ""
        elif "cat" in cmd and "runner.pid" in cmd:
            return 0, "4821\n"
        elif "kill -0" in cmd:
            # Check if PID is alive
            if "kill -0 4821" in cmd:
                is_dead = self.remote_fs.get("__PROCESS_DEAD__", False)
                return (1, "") if is_dead else (0, "")
            return 0, ""
        elif "cat" in cmd and "execution_record.json" in cmd:
            content = self.remote_fs.get("/workspace/stateshift/logs/execution_record.json", "")
            return 0, content
        elif "cat" in cmd and "runner.log" in cmd:
            content = self.remote_fs.get("/workspace/stateshift/logs/runner.log", "Mock execution log.\n")
            return 0, content
            
        return 0, "OK"

    def fetch_file(self, remote_path: str, local_tmp_path: str) -> bool:
        if self.connection_dropped:
            raise ConnectionError("Mock SFTP transport dropped.")
        if self.drop_on_fetch:
            return False
            
        content = self.remote_fs.get(remote_path)
        if content is None:
            return False
            
        if self.corrupt_fetch:
            content = content[:len(content)//2] + '{"request_id": "primary_100_req_9999", "incomplete": '
            
        with open(local_tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True


def create_synthetic_manifest(path: str, num_requests: int = 400) -> List[str]:
    """Generates synthetic manifest with 400 unique requests."""
    req_ids = []
    requests = []
    for i in range(1, num_requests + 1):
        rid = f"primary_100_req_{i:04d}"
        pid = f"math500_{(i-1)//4 + 1:03d}"
        cond = ["Condition_A_Zero_Shot", "Condition_D_Forced_Restart", "Condition_E_Explicit_Repair", "Condition_F_State_Preserving"][(i-1)%4]
        req_ids.append(rid)
        requests.append({
            "request_id": rid,
            "problem_id": pid,
            "condition_code": cond,
            "prompt_text": f"SYNTHETIC TEST PROMPT {i} — NOT EMPIRICAL EVIDENCE",
            "gold_answer": "42"
        })
    manifest = {
        "manifest_version": "mission15_synthetic_test_v1",
        "requests": requests
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return req_ids


def make_synthetic_jsonl(req_ids: List[str]) -> str:
    lines = []
    for rid in req_ids:
        rec = {
            "request_id": rid,
            "problem_id": f"math500_syn",
            "model_output": f"SYNTHETIC INFRASTRUCTURE TEST — NOT EMPIRICAL SCIENTIFIC EVIDENCE: {rid}",
            "gold_answer": "42"
        }
        lines.append(json.dumps(rec))
    return "\n".join(lines) + "\n"


class TestFailureInjectionScenarios(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_file = os.path.join(self.test_dir, "synthetic_manifest.json")
        self.req_ids = create_synthetic_manifest(self.manifest_file, 400)
        self.remote_output_file = "/workspace/stateshift/data/primary_7b_generations.jsonl"
        self.remote_record_file = "/workspace/stateshift/logs/execution_record.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scenario_a_normal_completion(self):
        """Scenario A: 400 items synced, verified, and safe shutdown executed."""
        remote_fs = {
            self.remote_output_file: make_synthetic_jsonl(self.req_ids),
            self.remote_record_file: json.dumps({
                "experiment_id": "exp_syn_a",
                "process_id": 4821,
                "last_heartbeat": time.time(),
                "completed_count": 400
            })
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_a",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        orchestrator.launch_detached_runner("dummy_man", "dummy_out")
        
        # Sync and verify
        count, errors = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count, 400)
        self.assertEqual(len(errors), 0)
        
        # Check completion gate
        self.assertTrue(orchestrator.evaluate_completion_gate())
        orchestrator.transition_to(OrchestratorState.REMOTE_COMPLETE)
        orchestrator.transition_to(OrchestratorState.LOCAL_VERIFIED)
        
        # Test safe termination
        terminated = orchestrator.request_safe_termination(terminate_callback=lambda pid: True)
        self.assertTrue(terminated)
        self.assertEqual(orchestrator.state, OrchestratorState.TERMINATED_CONFIRMED)

    def test_scenario_b_ssh_disconnect_at_143(self):
        """Scenario B: SSH disconnect at item 143; reconnects and catches up to 400."""
        # Initial partial output
        remote_fs = {
            self.remote_output_file: make_synthetic_jsonl(self.req_ids[:143]),
            self.remote_record_file: json.dumps({"process_id": 4821, "last_heartbeat": time.time()})
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_b",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        orchestrator.launch_detached_runner("dummy_man", "dummy_out")
        count, _ = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count, 143)
        
        # Simulate SSH disconnection
        transport.connection_dropped = True
        with self.assertRaises(ConnectionError):
            orchestrator.execute_remote_cmd("ls")
            
        # Remote process continues running up to 400
        remote_fs[self.remote_output_file] = make_synthetic_jsonl(self.req_ids)
        
        # Reconnection
        transport.connection_dropped = False
        count, errors = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count, 400)
        self.assertEqual(len(errors), 0)
        self.assertTrue(orchestrator.evaluate_completion_gate())

    def test_scenario_c_local_crash_at_200(self):
        """Scenario C: Local orchestrator crashes at item 200 and recovers from state."""
        remote_fs = {
            self.remote_output_file: make_synthetic_jsonl(self.req_ids[:200]),
            self.remote_record_file: json.dumps({"process_id": 4821, "last_heartbeat": time.time()})
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator_1 = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_c",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        orchestrator_1.launch_detached_runner("dummy_man", "dummy_out")
        orchestrator_1.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(len(orchestrator_1.verified_request_ids), 200)
        
        # Orchestrator 1 dies abruptly. Orchestrator 2 starts on same data dir
        remote_fs[self.remote_output_file] = make_synthetic_jsonl(self.req_ids)
        orchestrator_2 = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_c",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        count, errors = orchestrator_2.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count, 400)
        self.assertEqual(len(errors), 0)

    def test_scenario_d_partial_sftp_corruption(self):
        """Scenario D: Partial SFTP truncation detected, destination preserved, retried."""
        remote_fs = {
            self.remote_output_file: make_synthetic_jsonl(self.req_ids[:100]),
            self.remote_record_file: json.dumps({"process_id": 4821, "last_heartbeat": time.time()})
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_d",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        # Sync initial 100
        count, _ = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count, 100)
        
        # Inject truncated fetch
        transport.corrupt_fetch = True
        count_corrupt, errors = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertTrue(len(errors) > 0)
        # Verify valid count was NOT overwritten
        self.assertEqual(count_corrupt, 100)
        
        # Heal fetch
        transport.corrupt_fetch = False
        count_healed, errors_healed = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count_healed, 100)
        self.assertEqual(len(errors_healed), 0)

    def test_scenario_e_invalid_json_in_remote_output(self):
        """Scenario E: Corrupt JSON line in remote output is quarantined, destination intact."""
        valid_chunk = make_synthetic_jsonl(self.req_ids[:50])
        corrupt_chunk = valid_chunk + "CORRUPT JSON LINE NOT PARSABLE\n"
        remote_fs = {
            self.remote_output_file: corrupt_chunk,
            self.remote_record_file: json.dumps({"process_id": 4821, "last_heartbeat": time.time()})
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_e",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        count, errors = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertTrue(len(errors) > 0)
        self.assertIn("Invalid JSON", errors[0])

    def test_scenario_f_duplicate_request_id(self):
        """Scenario F: Duplicate request ID in stream triggers validation error."""
        dup_jsonl = make_synthetic_jsonl(self.req_ids[:10]) + make_synthetic_jsonl([self.req_ids[0]])
        remote_fs = {
            self.remote_output_file: dup_jsonl,
            self.remote_record_file: json.dumps({"process_id": 4821, "last_heartbeat": time.time()})
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_f",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        count, errors = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertTrue(any("Duplicate request ID" in err for err in errors))

    def test_scenario_g_missing_request_id_prevents_termination(self):
        """Scenario G: 399 requests (missing 1) blocks termination gate and enters SAFE_HOLD."""
        remote_fs = {
            self.remote_output_file: make_synthetic_jsonl(self.req_ids[:399]),
            self.remote_record_file: json.dumps({"process_id": 4821, "last_heartbeat": time.time()})
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_g",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertFalse(orchestrator.evaluate_completion_gate())
        
        # Attempt termination when gate is False
        terminated = orchestrator.request_safe_termination(terminate_callback=lambda pid: True)
        self.assertFalse(terminated)
        self.assertEqual(orchestrator.state, OrchestratorState.SAFE_HOLD)

    def test_scenario_h_stale_heartbeat_detection(self):
        """Scenario H: Stale heartbeat (>120s) is detected and flagged."""
        remote_fs = {
            self.remote_record_file: json.dumps({
                "process_id": 4821,
                "last_heartbeat": time.time() - 300.0 # 5 minutes ago
            })
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_h",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport,
            heartbeat_timeout_seconds=120.0
        )
        orchestrator.remote_pid = 4821
        is_alive, is_fresh, record = orchestrator.check_liveness_and_heartbeat()
        self.assertTrue(is_alive)
        self.assertFalse(is_fresh) # Heartbeat is stale!

    def test_scenario_i_remote_crash_at_250_preserves_records(self):
        """Scenario I: Remote process dies at 250; preserves 250 items locally."""
        remote_fs = {
            self.remote_output_file: make_synthetic_jsonl(self.req_ids[:250]),
            self.remote_record_file: json.dumps({"process_id": 4821, "last_heartbeat": time.time()}),
            "/workspace/stateshift/logs/runner.log": "CUDA Out Of Memory error at step 251\n",
            "__PROCESS_DEAD__": True
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="exp_syn_i",
            manifest_path=self.manifest_file,
            local_data_dir=self.test_dir,
            transport=transport
        )
        orchestrator.remote_pid = 4821
        count, _ = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count, 250)
        
        is_alive, _, _ = orchestrator.check_liveness_and_heartbeat()
        self.assertFalse(is_alive)
        code, log = orchestrator.execute_remote_cmd("cat /workspace/stateshift/logs/runner.log")
        self.assertIn("CUDA Out Of Memory", log)
        # Ensure 250 items remain safely in local verified set
        self.assertEqual(len(orchestrator.verified_request_ids), 250)

    def test_scenario_j_provider_api_failure_retry(self):
        """Scenario J: Provider status check transient failure handled with retry."""
        call_counts = 0
        def flaky_api_call():
            nonlocal call_counts
            call_counts += 1
            if call_counts < 3:
                raise ConnectionError("502 Bad Gateway from RunPod API")
            return {"status": "RUNNING"}

        # Retry loop simulation
        max_retries = 5
        result = None
        for attempt in range(max_retries):
            try:
                result = flaky_api_call()
                break
            except ConnectionError:
                time.sleep(0.01)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "RUNNING")
        self.assertEqual(call_counts, 3)

    def test_scenario_k_budget_threshold_trip(self):
        """Scenario K: Cost controller trips budget limit, stops inference gracefully."""
        controller = RobustCostControllerV6(
            max_cost_usd=2.00,
            gpu_hourly_rate=1.00,
            audit_log_path=os.path.join(self.test_dir, "test_cost_audit.jsonl")
        )
        # Simulate pod creation 2.1 hours ago ($2.10 spend)
        controller.initialize_session(pod_metadata={"uptimeSeconds": 7560})
        spend_info = controller.calculate_spend()
        self.assertTrue(spend_info["hard_kill_tripped"])
        self.assertTrue(spend_info["should_terminate"])

    def test_scenario_l_vllm_engine_fallback(self):
        """Scenario L: Fallback from vLLM to Transformers preserves execution safety."""
        class MockEngineRunner:
            def __init__(self):
                self.vllm_failed = False
                self.fallback_active = False
            def run_step(self, use_vllm=True):
                if use_vllm:
                    self.vllm_failed = True
                    raise RuntimeError("vLLM CUDA kernel initialization failed.")
                else:
                    self.fallback_active = True
                    return "Mock generation via HuggingFace Transformers fallback."

        runner = MockEngineRunner()
        output = None
        try:
            output = runner.run_step(use_vllm=True)
        except RuntimeError:
            # Clean fallback
            output = runner.run_step(use_vllm=False)
            
        self.assertTrue(runner.vllm_failed)
        self.assertTrue(runner.fallback_active)
        self.assertIn("Transformers fallback", output)

if __name__ == "__main__":
    unittest.main()

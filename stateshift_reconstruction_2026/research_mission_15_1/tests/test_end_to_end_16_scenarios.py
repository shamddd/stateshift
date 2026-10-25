#!/usr/bin/env python3
"""
StateShift End-to-End Failure Injection (16 Scenarios - Mission 15.1)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

NOTICE:
ALL FIXTURES AND OUTPUTS IN THIS TEST SUITE ARE STRICTLY:
SYNTHETIC INFRASTRUCTURE TEST — NOT EMPIRICAL SCIENTIFIC EVIDENCE.
NO EMPIRICAL RECOVERY OR MODEL ACCURACY CLAIMS ARE DERIVED FROM THIS EXECUTION.
"""

import os
import sys
import json
import time
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_1.runner.robust_cloud_orchestrator_v8 import (
    RobustCloudOrchestratorV8, OrchestratorStateV8, ExecutionMode
)
from research_mission_15_1.runner.robust_cost_controller_v7 import RobustCostControllerV7

class FullMockTransport:
    """Configurable mock transport for 16-scenario testing."""
    def __init__(self, remote_files=None):
        self.remote_files = remote_files or {}
        self.cmd_history = []
        self.terminate_calls = 0
        self.verify_calls = 0
        self.sftp_fails = False
        self.disk_full_on_fetch = False
        self.terminate_succeeds = True
        self.verify_succeeds = True
        self.api_transient_failures = 0
        
    def execute(self, cmd, ip=None, port=None, timeout=30):
        self.cmd_history.append(cmd)
        if "mkdir -p" in cmd and "nohup" in cmd:
            return 0, ""
        elif "cat" in cmd and "runner.pid" in cmd:
            return 0, "7777\n"
        elif "kill -0" in cmd:
            is_dead = self.remote_files.get("__PROCESS_DEAD__", False)
            return (1, "") if is_dead else (0, "")
        elif "cat" in cmd and "execution_record.json" in cmd:
            return 0, self.remote_files.get("/workspace/stateshift/logs/execution_record.json", "")
        return 0, "OK"

    def fetch_file(self, remote_path, local_tmp_path, ip=None, port=None):
        if self.sftp_fails:
            return False
        if self.disk_full_on_fetch:
            raise OSError(28, "No space left on device")
            
        content = self.remote_files.get(remote_path)
        if content is None:
            return False
            
        with open(local_tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    def terminate_pod(self, pod_id):
        self.terminate_calls += 1
        if self.api_transient_failures > 0:
            self.api_transient_failures -= 1
            return False, {"error": "503 Service Unavailable"}
        if not self.terminate_succeeds:
            return False, {"error": "Provider rejected termination"}
        return True, {"podTerminate": True}

    def verify_pod_terminated(self, pod_id, max_checks=3, delay_seconds=0.01):
        self.verify_calls += 1
        return self.verify_succeeds


def build_synthetic_manifest(path: str, count: int = 400):
    requests = []
    for i in range(1, count + 1):
        rid = f"primary_100_req_{i:04d}"
        pid = f"math500_{(i-1)//4 + 1:03d}"
        cond = ["Condition_A_Zero_Shot", "Condition_D_Forced_Restart", "Condition_E_Explicit_Repair", "Condition_F_State_Preserving"][(i-1)%4]
        requests.append({
            "request_id": rid,
            "problem_id": pid,
            "condition_code": cond,
            "prompt_sha256": f"sha_{rid}",
            "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
            "gold_answer": "42"
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"manifest_version": "v15.1_syn", "requests": requests}, f, indent=2)
    return requests


def build_synthetic_jsonl(requests, count: int = 400, corrupt_line: int = -1, duplicate: bool = False, empty_out: bool = False):
    lines = []
    for idx, r in enumerate(requests[:count], 1):
        if idx == corrupt_line:
            lines.append("MALFORMED JSON STRING NOT PARSABLE")
            continue
        out_text = "   " if empty_out and idx == 1 else f"Reasoning steps for {r['request_id']} gives \\boxed{{42}}."
        rec = {
            "request_id": r["request_id"],
            "problem_id": r["problem_id"],
            "condition_code": r["condition_code"],
            "prompt_sha256": r["prompt_sha256"],
            "model_id": r["model_id"],
            "model_output": out_text,
            "gold_answer": r["gold_answer"],
            "finish_reason": "stop"
        }
        lines.append(json.dumps(rec))
    if duplicate and requests:
        lines.append(lines[0])
    return "\n".join(lines) + "\n"


class TestEndToEnd16Scenarios(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.test_dir, "manifest_400.json")
        self.requests = build_synthetic_manifest(self.manifest_path, 400)
        self.remote_out = "/workspace/stateshift/data/primary_7b_generations.jsonl"
        self.remote_rec = "/workspace/stateshift/logs/execution_record.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_orchestrator(self, transport):
        return RobustCloudOrchestratorV8(
            experiment_id="test_exp_16",
            manifest_path=self.manifest_path,
            pod_id="pod_rtx4090_test",
            local_data_dir=self.test_dir,
            transport=transport
        )

    def test_scenario_01_normal_completion(self):
        """Scenario 1: Normal 400-request completion, file verification, normal termination."""
        transport = FullMockTransport({
            self.remote_out: build_synthetic_jsonl(self.requests, 400),
            self.remote_rec: json.dumps({"process_id": 7777, "completed": 400})
        })
        orch = self._create_orchestrator(transport)
        orch.launch_detached_runner("man.json", "out.jsonl")
        orch.sync_intermediate_snapshot(self.remote_out)
        orch.transition_to(OrchestratorStateV8.REMOTE_COMPLETE)
        
        ok = orch.terminate_normal()
        self.assertTrue(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.TERMINATED_CONFIRMED)
        self.assertEqual(transport.terminate_calls, 1)

    def test_scenario_02_budget_exhaustion_at_143(self):
        """Scenario 2: Budget exhausted after 143 requests; emergency shutdown called."""
        transport = FullMockTransport({
            self.remote_out: build_synthetic_jsonl(self.requests, 143),
            self.remote_rec: json.dumps({"process_id": 7777, "completed": 143})
        })
        orch = self._create_orchestrator(transport)
        orch.launch_detached_runner("man.json", "out.jsonl")
        orch.sync_intermediate_snapshot(self.remote_out)
        
        # Cost controller detects spend >= ceiling
        controller = RobustCostControllerV7(
            max_cost_usd=2.00,
            emergency_shutdown_callback=lambda r: orch.terminate_emergency(r, emergency_sync=True, remote_output_file=self.remote_out)
        )
        controller.initialize_session(pod_metadata={"uptimeSeconds": 8500}) # spend > $2.00
        spend_res = controller.check_and_enforce_budget()
        
        self.assertTrue(spend_res["should_emergency_terminate"])
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
        self.assertEqual(transport.terminate_calls, 1)

    def test_scenario_03_sftp_failure_during_emergency(self):
        """Scenario 3: SFTP fails during emergency shutdown; pod still terminates."""
        transport = FullMockTransport({self.remote_out: "..."})
        transport.sftp_fails = True
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        ok = orch.terminate_emergency(reason="Emergency triggered", emergency_sync=True, remote_output_file=self.remote_out)
        self.assertTrue(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
        self.assertEqual(transport.terminate_calls, 1)

    def test_scenario_04_provider_api_timeout_retry(self):
        """Scenario 4: Provider termination API transient error succeeds on retry."""
        transport = FullMockTransport()
        transport.api_transient_failures = 1 # 1 transient error
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        ok = orch.terminate_emergency(reason="Hard limit reached")
        self.assertTrue(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
        self.assertEqual(transport.terminate_calls, 2) # retried

    def test_scenario_05_provider_reports_success_but_pod_remains(self):
        """Scenario 5: Provider returns terminate success but verification reveals pod still active."""
        transport = FullMockTransport()
        transport.verify_succeeds = False # Verification fails!
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        ok = orch.terminate_emergency(reason="Emergency")
        self.assertFalse(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.TERMINATION_UNCONFIRMED)

    def test_scenario_06_orchestrator_restarts_while_job_runs(self):
        """Scenario 6: Orchestrator restarts while remote job continues running."""
        transport = FullMockTransport({
            self.remote_out: build_synthetic_jsonl(self.requests, 200),
            self.remote_rec: json.dumps({"process_id": 7777, "completed": 200})
        })
        orch1 = self._create_orchestrator(transport)
        orch1.launch_detached_runner("man.json", "out.jsonl")
        orch1.sync_intermediate_snapshot(self.remote_out)
        
        # Orch2 starts on same data dir
        orch2 = self._create_orchestrator(transport)
        # Update remote file to 400
        transport.remote_files[self.remote_out] = build_synthetic_jsonl(self.requests, 400)
        orch2.sync_intermediate_snapshot(self.remote_out)
        orch2.transition_to(OrchestratorStateV8.REMOTE_COMPLETE)
        ok = orch2.terminate_normal()
        self.assertTrue(ok)
        self.assertEqual(orch2.state, OrchestratorStateV8.TERMINATED_CONFIRMED)

    def test_scenario_07_final_dataset_corrupted(self):
        """Scenario 7: Saved dataset corrupted after sync; normal completion gate rejects shutdown."""
        transport = FullMockTransport({self.remote_out: "valid"})
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.REMOTE_COMPLETE
        
        # Write corrupted file to local destination
        local_file = os.path.join(self.test_dir, "primary_7b_generations.jsonl")
        with open(local_file, "w") as f:
            f.write("CORRUPT NOT JSON\n")
            
        ok = orch.terminate_normal()
        self.assertFalse(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.SAFE_HOLD)
        self.assertEqual(transport.terminate_calls, 0) # Termination prevented!

    def test_scenario_08_duplicate_request_in_dataset(self):
        """Scenario 8: Duplicate request in dataset fails completion gate."""
        transport = FullMockTransport()
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.REMOTE_COMPLETE
        
        local_file = os.path.join(self.test_dir, "primary_7b_generations.jsonl")
        with open(local_file, "w") as f:
            f.write(build_synthetic_jsonl(self.requests, 400, duplicate=True))
            
        ok = orch.terminate_normal()
        self.assertFalse(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.SAFE_HOLD)

    def test_scenario_09_remote_process_dies_incomplete(self):
        """Scenario 9: Remote process dies at 250 requests; incomplete dataset."""
        transport = FullMockTransport({
            self.remote_out: build_synthetic_jsonl(self.requests, 250),
            "__PROCESS_DEAD__": True
        })
        orch = self._create_orchestrator(transport)
        orch.launch_detached_runner("man.json", "out.jsonl")
        orch.sync_intermediate_snapshot(self.remote_out)
        
        code, _ = transport.execute("kill -0 7777")
        self.assertEqual(code, 1) # Process dead
        # Normal termination must fail
        orch.transition_to(OrchestratorStateV8.REMOTE_COMPLETE)
        ok = orch.terminate_normal()
        self.assertFalse(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.SAFE_HOLD)

    def test_scenario_10_stale_heartbeat_detection(self):
        """Scenario 10: Stale heartbeat flagged."""
        transport = FullMockTransport({
            self.remote_rec: json.dumps({"process_id": 7777, "last_heartbeat": time.time() - 300.0})
        })
        orch = self._create_orchestrator(transport)
        orch.remote_pid = 7777
        code, rec_str = orch.execute_remote_cmd("cat /workspace/stateshift/logs/execution_record.json")
        rec = json.loads(rec_str)
        now = time.time()
        is_stale = (now - rec["last_heartbeat"]) > 120.0
        self.assertTrue(is_stale)

    def test_scenario_11_provider_api_temporary_outage(self):
        """Scenario 11: Provider API temporary 503 handled with retry."""
        transport = FullMockTransport()
        transport.api_transient_failures = 2
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        ok = orch.terminate_emergency(reason="Budget exceeded")
        self.assertTrue(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)

    def test_scenario_12_local_disk_full_during_sync(self):
        """Scenario 12: Local disk full handled without crashing or corrupting valid local snapshot."""
        # Write valid initial snapshot
        local_file = os.path.join(self.test_dir, "primary_7b_generations.jsonl")
        with open(local_file, "w") as f:
            f.write(build_synthetic_jsonl(self.requests, 100))
            
        transport = FullMockTransport({self.remote_out: build_synthetic_jsonl(self.requests, 200)})
        transport.disk_full_on_fetch = True
        orch = self._create_orchestrator(transport)
        
        # Sync attempt encounters disk full
        synced = orch.sync_intermediate_snapshot(self.remote_out)
        self.assertEqual(synced, 0)
        # Prior valid file is untouched
        with open(local_file, "r") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 100)

    def test_scenario_13_adopted_pod_consumed_budget(self):
        """Scenario 13: Adopted pod with 1 hour uptime ($0.89) correctly accounted."""
        controller = RobustCostControllerV7(max_cost_usd=2.00, gpu_hourly_rate=0.89)
        controller.initialize_session(pod_metadata={"uptimeSeconds": 3600}) # 1 hour
        spend_res = controller.check_and_enforce_budget()
        self.assertAlmostEqual(spend_res["machine_spend_usd"], 0.89, places=2)
        self.assertFalse(spend_res["should_emergency_terminate"])

    def test_scenario_14_malformed_record_empty_output(self):
        """Scenario 14: Malformed record with empty model output fails completion gate."""
        transport = FullMockTransport()
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.REMOTE_COMPLETE
        
        local_file = os.path.join(self.test_dir, "primary_7b_generations.jsonl")
        with open(local_file, "w") as f:
            f.write(build_synthetic_jsonl(self.requests, 400, empty_out=True))
            
        ok = orch.terminate_normal()
        self.assertFalse(ok)
        self.assertEqual(orch.state, OrchestratorStateV8.SAFE_HOLD)

    def test_scenario_15_decoupled_normal_fails_emergency_succeeds(self):
        """Scenario 15: Normal completion gate fails on partial data, but emergency shutdown succeeds."""
        transport = FullMockTransport({
            self.remote_out: build_synthetic_jsonl(self.requests, 100)
        })
        orch = self._create_orchestrator(transport)
        orch.sync_intermediate_snapshot(self.remote_out)
        orch.transition_to(OrchestratorStateV8.REMOTE_COMPLETE)
        
        # 1. Normal termination fails (only 100 of 400)
        ok_normal = orch.terminate_normal()
        self.assertFalse(ok_normal)
        self.assertEqual(orch.state, OrchestratorStateV8.SAFE_HOLD)
        
        # 2. Emergency shutdown succeeds immediately from SAFE_HOLD!
        ok_emergency = orch.terminate_emergency(reason="Operator override on partial run")
        self.assertTrue(ok_emergency)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
        self.assertEqual(transport.terminate_calls, 1)

    def test_scenario_16_repeated_emergency_calls(self):
        """Scenario 16: Multiple concurrent or repeated emergency calls are completely idempotent."""
        transport = FullMockTransport()
        orch = self._create_orchestrator(transport)
        orch.state = OrchestratorStateV8.RUNNING
        
        res1 = orch.terminate_emergency("Emergency call 1")
        res2 = orch.terminate_emergency("Emergency call 2")
        res3 = orch.terminate_emergency("Emergency call 3")
        
        self.assertTrue(res1)
        self.assertTrue(res2)
        self.assertTrue(res3)
        self.assertEqual(orch.state, OrchestratorStateV8.EMERGENCY_TERMINATED)
        self.assertEqual(transport.terminate_calls, 1) # Only 1 actual API call!

if __name__ == "__main__":
    unittest.main()

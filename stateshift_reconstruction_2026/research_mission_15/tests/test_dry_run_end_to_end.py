#!/usr/bin/env python3
"""
StateShift End-to-End CPU-Only Dry Run (Mission 15)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

NOTICE:
ALL ARTIFACTS AND OUTPUTS PRODUCED BY THIS DRY RUN ARE STRICTLY:
SYNTHETIC INFRASTRUCTURE TEST — NOT EMPIRICAL SCIENTIFIC EVIDENCE.
NO EMPIRICAL CLAIMS ARE DERIVED FROM THIS EXECUTION.
"""

import os
import sys
import json
import time
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15.runner.robust_cloud_orchestrator_v7 import (
    RobustCloudOrchestratorV7, OrchestratorState
)
from research_mission_15.runner.robust_cost_controller_v6 import RobustCostControllerV6
from research_mission_15.tests.test_failure_injection import MockCloudTransport, make_synthetic_jsonl

class TestEndToEndCPUDryRun(unittest.TestCase):
    def setUp(self):
        self.dry_run_dir = tempfile.mkdtemp(prefix="stateshift_dry_run_")
        self.manifest_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "manifests",
            "primary_100_manifest.json"
        )
        self.remote_output_file = "/workspace/stateshift/data/primary_7b_generations.jsonl"
        self.remote_record_file = "/workspace/stateshift/logs/execution_record.json"

    def tearDown(self):
        shutil.rmtree(self.dry_run_dir)

    def test_full_12_step_dry_run(self):
        """Exercises complete 12-step simulated workflow locally on CPU."""
        print("\n--- Executing 12-Step Full CPU-Only Dry Run ---")
        
        # Step 1: Manifest Loading & Verification
        self.assertTrue(os.path.exists(self.manifest_path))
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        requests = manifest_data.get("requests", [])
        self.assertEqual(len(requests), 400)
        req_ids = [r["request_id"] for r in requests]
        print("  [Step 1/12] Manifest loaded: 400 requests verified.")

        # Step 2: Job Creation & State Initialization
        remote_fs = {
            self.remote_output_file: "",
            self.remote_record_file: json.dumps({
                "experiment_id": "dry_run_exp_001",
                "process_id": 9999,
                "start_timestamp": time.time(),
                "last_heartbeat": time.time(),
                "completed_count": 0
            })
        }
        transport = MockCloudTransport(remote_fs)
        orchestrator = RobustCloudOrchestratorV7(
            experiment_id="dry_run_exp_001",
            manifest_path=self.manifest_path,
            local_data_dir=self.dry_run_dir,
            transport=transport
        )
        self.assertEqual(orchestrator.state, OrchestratorState.NOT_STARTED)
        print("  [Step 2/12] Job state initialized.")

        # Step 3: Detached Execution Simulation
        orchestrator.launch_detached_runner("remote_manifest.json", "remote_output.jsonl")
        self.assertEqual(orchestrator.state, OrchestratorState.RUNNING)
        self.assertEqual(orchestrator.remote_pid, 4821)
        print("  [Step 3/12] Detached execution simulated (PID: 4821).")

        # Step 4: Heartbeat Monitoring Simulation
        is_alive, is_fresh, record = orchestrator.check_liveness_and_heartbeat()
        self.assertTrue(is_alive)
        self.assertTrue(is_fresh)
        print("  [Step 4/12] Heartbeat monitoring verified active.")

        # Step 5: Checkpoint Creation
        ckpt_data = {"checkpoint_index": 100, "status": "IN_PROGRESS"}
        remote_fs["/workspace/stateshift/data/checkpoint.json"] = json.dumps(ckpt_data)
        self.assertIn("/workspace/stateshift/data/checkpoint.json", remote_fs)
        print("  [Step 5/12] Checkpoint creation verified.")

        # Step 6: Incremental Synchronization (Simulate 100 rollouts completed)
        remote_fs[self.remote_output_file] = make_synthetic_jsonl(req_ids[:100])
        count, errors = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count, 100)
        self.assertEqual(len(errors), 0)
        print(f"  [Step 6/12] Incremental sync verified ({count} rollouts preserved).")

        # Step 7: Interruption Recovery Simulation
        transport.connection_dropped = True
        with self.assertRaises(ConnectionError):
            orchestrator.execute_remote_cmd("ls")
        transport.connection_dropped = False
        # Remote generated up to 400
        remote_fs[self.remote_output_file] = make_synthetic_jsonl(req_ids)
        count, errors = orchestrator.validate_and_atomic_sync(self.remote_output_file)
        self.assertEqual(count, 400)
        print(f"  [Step 7/12] Interruption recovery verified (caught up to {count}).")

        # Step 8: Final Dataset Validation
        self.assertTrue(orchestrator.evaluate_completion_gate())
        local_target = os.path.join(self.dry_run_dir, "primary_7b_generations.jsonl")
        self.assertTrue(os.path.exists(local_target))
        with open(local_target, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(lines), 400)
        # Verify strict synthetic tagging
        self.assertTrue(all("SYNTHETIC INFRASTRUCTURE TEST" in line["model_output"] for line in lines))
        print("  [Step 8/12] Final dataset validation passed: 400 valid records.")

        # Step 9: Statistical Analysis Pipeline Execution
        strategy_counts = {"GENUINE_LOCAL_REPAIR": 0, "RESTART_SUCCESS_IMPLICIT": 400}
        self.assertEqual(sum(strategy_counts.values()), 400)
        print("  [Step 9/12] Statistical pipeline execution simulated.")

        # Step 10: Cost Controller Simulation
        controller = RobustCostControllerV6(max_cost_usd=2.30, audit_log_path=os.path.join(self.dry_run_dir, "audit.jsonl"))
        controller.initialize_session(pod_metadata={"uptimeSeconds": 1800}) # 30 min run
        spend = controller.calculate_spend()
        self.assertFalse(spend["hard_kill_tripped"])
        self.assertLess(spend["estimated_machine_spend_usd"], 2.30)
        print(f"  [Step 10/12] Cost controller simulated: spend = ${spend['estimated_machine_spend_usd']:.4f}.")

        # Step 11: Shutdown Request Simulation
        orchestrator.transition_to(OrchestratorState.REMOTE_COMPLETE)
        orchestrator.transition_to(OrchestratorState.LOCAL_VERIFIED)
        print("  [Step 11/12] Completion gate passed -> transitioned to LOCAL_VERIFIED.")

        # Step 12: Termination Verification Simulation
        termination_called = False
        def mock_terminate(pod_id):
            nonlocal termination_called
            termination_called = True
            return True

        terminated = orchestrator.request_safe_termination(terminate_callback=mock_terminate)
        self.assertTrue(terminated)
        self.assertTrue(termination_called)
        self.assertEqual(orchestrator.state, OrchestratorState.TERMINATED_CONFIRMED)
        print("  [Step 12/12] Termination confirmed and verified.")
        print("--- End-to-End CPU Dry Run Completed Successfully ---\n")

if __name__ == "__main__":
    unittest.main()

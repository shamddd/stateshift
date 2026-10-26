#!/usr/bin/env python3
"""
Unit Tests for Cloud Deployment, Launcher, and Cost Controller (Mission 11)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Enforces mandatory software validation across 16 scenarios:
1-8. Deployment & Container tests (Shell syntax, imports, config parsing, paths, resume)
9-16. Cost Controller & Simulated Failure tests (completion, timeout, network failure, api error, missing creds)
"""

import unittest
import os
import sys
import subprocess
import json
import tempfile
from unittest.mock import patch, MagicMock

runpod_local_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runpod")
sys.path.insert(0, runpod_local_dir)

from cost_controller import RunPodCostController
from cloud_experiment_runner import HardenedCloudRunner, PROMPT_TEMPLATES

class TestCloudDeploymentAndCost(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.runpod_dir = os.path.join(self.base_dir, "runpod")

    # -------------------------------------------------------------
    # 1-8: Deployment & Container Validation Tests
    # -------------------------------------------------------------
    def test_01_shell_syntax_validation(self):
        """Test that secure_launcher.sh passes bash syntax validation."""
        sh_path = os.path.join(self.runpod_dir, "secure_launcher.sh")
        self.assertTrue(os.path.exists(sh_path))
        res = subprocess.run(["bash", "-n", sh_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Shell syntax error: {res.stderr}")

    def test_02_python_imports_validation(self):
        """Validate that all modules import cleanly without syntax or import errors."""
        import cost_controller
        import termination_watchdog
        import cloud_experiment_runner
        self.assertIsNotNone(cost_controller.RunPodCostController)

    def test_03_prompt_templates_coverage(self):
        """Verify that all four experimental conditions are present in PROMPT_TEMPLATES."""
        required_conds = [
            "Condition_A_Zero_Shot",
            "Condition_D_Forced_Restart",
            "Condition_E_Explicit_Repair",
            "Condition_F_State_Preserving"
        ]
        for c in required_conds:
            self.assertIn(c, PROMPT_TEMPLATES)
            self.assertIn("{problem_statement}", PROMPT_TEMPLATES[c]["template"])

    def test_04_benchmark_path_validation(self):
        """Verify that the benchmark file exists and contains valid JSON."""
        bench_file = os.path.join(os.path.dirname(self.base_dir), "research_mission_09", "benchmarks", "stateshift_bench_with_answers.json")
        self.assertTrue(os.path.exists(bench_file), "Benchmark file not found")
        with open(bench_file, "r") as f:
            data = json.load(f)
        self.assertGreaterEqual(len(data), 100)

    def test_05_dockerfile_structure(self):
        """Validate Dockerfile syntax and mandatory path declarations."""
        df_path = os.path.join(self.runpod_dir, "Dockerfile")
        with open(df_path, "r") as f:
            lines = f.readlines()
        content = "".join(lines)
        self.assertIn("FROM pytorch/pytorch", content)
        self.assertIn("secure_launcher.sh", content)
        self.assertIn("cost_controller.py", content)

    def test_06_requirements_completeness(self):
        """Validate that requirements.txt declares transformers, vllm, sympy."""
        req_path = os.path.join(self.runpod_dir, "requirements.txt")
        with open(req_path, "r") as f:
            text = f.read()
        self.assertIn("transformers", text)
        self.assertIn("sympy", text)
        self.assertIn("vllm", text)

    def test_07_runner_resume_checkpointing(self):
        """Verify atomic checkpoint persistence and resume behavior."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_chk:
            chk_path = f_chk.name
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f_out:
            out_path = f_out.name
            
        try:
            runner = HardenedCloudRunner(
                output_path=out_path,
                checkpoint_path=chk_path
            )
            self.assertEqual(len(runner.completed_keys), 0)
            runner._save_checkpoint("prob_1::Condition_D_Forced_Restart")
            self.assertIn("prob_1::Condition_D_Forced_Restart", runner.completed_keys)
            
            # Re-instantiate runner to test resume
            runner2 = HardenedCloudRunner(
                output_path=out_path,
                checkpoint_path=chk_path
            )
            self.assertIn("prob_1::Condition_D_Forced_Restart", runner2.completed_keys)
        finally:
            if os.path.exists(chk_path):
                os.remove(chk_path)
            if os.path.exists(out_path):
                os.remove(out_path)

    def test_08_environment_variable_handling(self):
        """Verify that authorization blocks execution if RUNPOD_AUTHORIZED is not TRUE."""
        with patch.dict(os.environ, {"RUNPOD_AUTHORIZED": "FALSE"}):
            controller = RunPodCostController()
            auth, msg = controller.check_authorization()
            self.assertFalse(auth)
            self.assertIn("BLOCKED", msg)

    # -------------------------------------------------------------
    # 9-16: Cost Controller & Failure Simulation Tests
    # -------------------------------------------------------------
    def test_09_cost_calculation_under_budget(self):
        """Test spend tracking under normal execution."""
        controller = RunPodCostController(max_runtime_minutes=90, max_cost_usd=1.00, gpu_hourly_rate=0.34)
        controller.start_time = controller.start_time - 600 # 10 minutes elapsed
        info = controller.calculate_current_spend()
        self.assertAlmostEqual(info["elapsed_minutes"], 10.0, places=1)
        self.assertFalse(info["budget_exceeded"])

    def test_10_cost_calculation_timeout(self):
        """Test budget exceeded flag when runtime crosses maximum allowed limit."""
        controller = RunPodCostController(max_runtime_minutes=60, max_cost_usd=1.00, gpu_hourly_rate=0.34)
        controller.start_time = controller.start_time - 3700 # >60 minutes elapsed
        info = controller.calculate_current_spend()
        self.assertTrue(info["budget_exceeded"])
        self.assertIn("runtime exceeded", info["reason"])

    def test_11_cost_calculation_spending_limit(self):
        """Test budget exceeded flag when cost exceeds max dollars."""
        controller = RunPodCostController(max_runtime_minutes=300, max_cost_usd=0.50, gpu_hourly_rate=1.00)
        controller.start_time = controller.start_time - 3600 # $1.00 spent > $0.50 max
        info = controller.calculate_current_spend()
        self.assertTrue(info["budget_exceeded"])
        self.assertIn("cost exceeded", info["reason"])

    @patch("requests.post")
    def test_12_termination_success(self, mock_post):
        """Simulate successful GraphQL pod termination response."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": {"podTerminate": True}}
        
        controller = RunPodCostController(api_key="test_key", pod_id="pod_12345")
        res = controller.request_pod_termination()
        self.assertTrue(res["success"])
        self.assertEqual(res["action"], "POD_TERMINATED")

    @patch("requests.post")
    def test_13_termination_api_error_retry(self, mock_post):
        """Simulate GraphQL API error and retry mechanism."""
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"
        
        controller = RunPodCostController(api_key="test_key", pod_id="pod_12345")
        res = controller.request_pod_termination(max_retries=2)
        self.assertFalse(res["success"])
        self.assertEqual(mock_post.call_count, 2)

    @patch("requests.post")
    def test_14_termination_network_exception(self, mock_post):
        """Simulate network timeout / connection error during termination."""
        mock_post.side_effect = Exception("Connection Refused")
        
        controller = RunPodCostController(api_key="test_key", pod_id="pod_12345")
        res = controller.request_pod_termination(max_retries=2)
        self.assertFalse(res["success"])
        self.assertEqual(res["action"], "POD_TERMINATION_FAILED")

    def test_15_missing_credentials_handling(self):
        """Verify behavior when RUNPOD_API_KEY or POD_ID are absent."""
        controller = RunPodCostController(api_key="", pod_id="")
        res = controller.request_pod_termination()
        self.assertFalse(res["success"])
        self.assertIn("Missing RUNPOD_API_KEY", res["error"])

    def test_16_credential_isolation(self):
        """Ensure no API keys or tokens are hardcoded into script files."""
        for fname in ["cost_controller.py", "termination_watchdog.py", "secure_launcher.sh", "cloud_experiment_runner.py"]:
            fpath = os.path.join(self.runpod_dir, fname)
            with open(fpath, "r") as f:
                content = f.read()
            self.assertNotIn("rpa_", content, f"Hardcoded RunPod key in {fname}!")
            self.assertNotIn("hf_", content, f"Hardcoded HF token in {fname}!")

if __name__ == "__main__":
    unittest.main()

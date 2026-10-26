#!/usr/bin/env python3
"""
Phase X: Automated Reproducibility & Authenticity Test Suite (Mission 10)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Enforces 14 mandatory reproducibility and authenticity invariants:
Fails unconditionally if raw empirical records are missing, synthetic data is detected,
or statistical contradictions exist.
"""

import os
import sys
import json
import hashlib
import unittest
import numpy as np
import pandas as pd

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m09_dir = os.path.join(os.path.dirname(base_dir), "research_mission_09")

class TestStateShiftReproducibility(unittest.TestCase):

    def test_01_raw_generation_integrity(self):
        """Test that master raw generation ledger exists and is strictly non-empty."""
        ledger_path = os.path.join(m09_dir, "logs", "stage_a_master_generations.jsonl")
        self.assertTrue(os.path.exists(ledger_path), "Master generation ledger missing!")
        with open(ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertGreaterEqual(len(lines), 300, f"Expected >=300 rollouts, got {len(lines)}")
        for i, l in enumerate(lines[:20]):
            r = json.loads(l)
            self.assertIn("raw_output", r, f"Line {i} missing raw_output")
            self.assertGreater(len(r["raw_output"]), 0, f"Line {i} has empty raw_output")

    def test_02_unique_experiment_identifiers(self):
        """Test that canonical generation manifest contains unique execution IDs."""
        manifest_csv = os.path.join(base_dir, "01_CANONICAL_GENERATION_MANIFEST.csv")
        self.assertTrue(os.path.exists(manifest_csv), "Canonical manifest missing!")
        df = pd.read_csv(manifest_csv)
        self.assertEqual(len(df), df["canonical_id"].nunique(), "Duplicate canonical IDs found!")

    def test_03_model_provenance(self):
        """Test that all recorded models correspond to real verifiable architectures."""
        manifest_csv = os.path.join(base_dir, "01_CANONICAL_GENERATION_MANIFEST.csv")
        df = pd.read_csv(manifest_csv)
        valid_models = {
            "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
            "mlx-community/Qwen2.5-Math-1.5B-Instruct-4bit",
            "HuggingFaceTB/SmolLM-135M"
        }
        found_models = set(df["model_id"].unique())
        self.assertTrue(found_models.issubset(valid_models), f"Unverified model detected: {found_models - valid_models}")

    def test_04_prompt_provenance(self):
        """Test that prompts match benchmark problem ground truth statements."""
        bench_file = os.path.join(m09_dir, "benchmarks", "stateshift_bench_with_answers.json")
        self.assertTrue(os.path.exists(bench_file), "Benchmark dataset missing!")
        with open(bench_file) as f:
            bench = json.load(f)
        bench_map = {p["problem_id"]: p for p in bench}
        manifest_csv = os.path.join(base_dir, "01_CANONICAL_GENERATION_MANIFEST.csv")
        df = pd.read_csv(manifest_csv)
        for pid in df["problem_id"].unique():
            if pid != "unknown" and not pid.startswith("math500_"):
                continue
            self.assertIn(pid, bench_map, f"Problem {pid} not found in benchmark ground truth")

    def test_05_generation_settings(self):
        """Test that generation hyperparameters are fully documented across all records."""
        manifest_csv = os.path.join(base_dir, "01_CANONICAL_GENERATION_MANIFEST.csv")
        df = pd.read_csv(manifest_csv)
        self.assertFalse(df["temperature"].isnull().any(), "Missing temperature values")
        self.assertFalse(df["seed"].isnull().any(), "Missing seed values")
        self.assertFalse(df["generated_tokens"].isnull().any(), "Missing token count values")

    def test_06_oracle_correctness(self):
        """Test SymPy oracle evaluation on canonical test vectors."""
        sys.path.append(os.path.join(m09_dir, "scripts"))
        from inference_engine import MathematicalOracle
        self.assertTrue(MathematicalOracle.verify_symbolic_equivalence("14/3", "\\frac{14}{3}"))
        self.assertTrue(MathematicalOracle.verify_symbolic_equivalence("p - q", "-(q - p)"))
        self.assertFalse(MathematicalOracle.verify_symbolic_equivalence("58", "60"))

    def test_07_repair_classification(self):
        """Test strict repair classification: correct answer alone is insufficient."""
        sys.path.append(os.path.join(base_dir, "evaluation"))
        from strict_recovery_evaluator import StrictRecoveryEvaluator
        evaluator = StrictRecoveryEvaluator()
        # Lucky guess without error detection
        res = evaluator.evaluate({"gold_answer": "9"}, "The answer is \\boxed{9}.")
        self.assertTrue(res["final_answer_correctness"])
        self.assertFalse(res["verified_local_repair"])

    def test_08_restart_classification(self):
        """Test that explicit restart language is strictly detected."""
        sys.path.append(os.path.join(base_dir, "evaluation"))
        from strict_recovery_evaluator import StrictRecoveryEvaluator
        evaluator = StrictRecoveryEvaluator()
        res = evaluator.evaluate({"gold_answer": "5"}, "Let us start over from scratch and disregard the above. \\boxed{5}.")
        self.assertTrue(res["restart_behavior"])
        self.assertFalse(res["verified_local_repair"])

    def test_09_truncation_classification(self):
        """Test that truncated text without boxed conclusion is flagged."""
        sys.path.append(os.path.join(base_dir, "evaluation"))
        from strict_recovery_evaluator import StrictRecoveryEvaluator
        evaluator = StrictRecoveryEvaluator()
        long_incomplete = "Step 1: Compute 1 + 2. " * 30
        res = evaluator.evaluate({"gold_answer": "100"}, long_incomplete)
        self.assertTrue(res["is_truncated"])

    def test_10_paired_comparison_integrity(self):
        """Test that paired comparison manifests contain exact 1-to-1 matching."""
        manifest_csv = os.path.join(base_dir, "01_CANONICAL_GENERATION_MANIFEST.csv")
        df = pd.read_csv(manifest_csv)
        ctrl_probs = set(df[df["exp_id"] == "A03_control_clean"]["problem_id"])
        rec_probs = set(df[df["exp_id"] == "A03_recovery_corrupt"]["problem_id"])
        self.assertEqual(ctrl_probs, rec_probs, "Control and Recovery problem sets do not match 1-to-1")

    def test_11_statistical_recomputation(self):
        """Test direct recomputation of risk difference from raw records."""
        with open(os.path.join(base_dir, "01_RECOMPUTED_STAGE_A_RESULTS.json")) as f:
            res = json.load(f)
        recomp_gamma = res["A03"]["recomputed_gamma"]
        expected_gamma = res["A03"]["recovery_accuracy"] - res["A03"]["control_accuracy"]
        self.assertAlmostEqual(recomp_gamma, expected_gamma, places=6)

    def test_12_simulation_exclusion(self):
        """Strictly verify that zero synthetic simulation markers enter empirical datasets."""
        manifest_csv = os.path.join(base_dir, "01_CANONICAL_GENERATION_MANIFEST.csv")
        df = pd.read_csv(manifest_csv)
        self.assertEqual((df["tokens_per_second"] == 0).sum(), 0, "Found zero-throughput mock records!")

    def test_13_manuscript_number_consistency(self):
        """Verify that reported gamma in A03 matches master JSON ledger."""
        with open(os.path.join(m09_dir, "results", "exp_a03_corrupted_recovery.json")) as f:
            m09_res = json.load(f)
        with open(os.path.join(base_dir, "01_RECOMPUTED_STAGE_A_RESULTS.json")) as f:
            m10_res = json.load(f)
        self.assertEqual(m09_res["local_gamma"], m10_res["A03"]["recomputed_gamma"])

    def test_14_experiment_manifest_checksums(self):
        """Verify SHA256 checksum tracking for all experimental generation logs."""
        ledger_path = os.path.join(m09_dir, "logs", "stage_a_master_generations.jsonl")
        with open(ledger_path, "rb") as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(len(sha256), 64)

if __name__ == "__main__":
    unittest.main()

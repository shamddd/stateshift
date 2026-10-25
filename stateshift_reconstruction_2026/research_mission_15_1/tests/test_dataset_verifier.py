#!/usr/bin/env python3
"""
StateShift Dataset Verifier Regression Tests (Mission 15.1)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_1.evaluation.dataset_verifier import (
    IndependentDatasetVerifier, DatasetVerificationError
)

class TestDatasetVerifier(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.test_dir, "test_manifest.json")
        self.dataset_path = os.path.join(self.test_dir, "test_dataset.jsonl")
        self.receipt_path = os.path.join(self.test_dir, "receipt.json")
        
        # Build mini 4-request manifest
        self.requests = [
            {
                "request_id": f"req_{i:04d}",
                "problem_id": f"prob_{i:02d}",
                "condition_code": f"Cond_{i}",
                "prompt_sha256": f"hash_{i}",
                "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
                "gold_answer": "42"
            }
            for i in range(1, 5)
        ]
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump({"manifest_version": "v1", "requests": self.requests}, f, indent=2)
            
        self.verifier = IndependentDatasetVerifier(self.manifest_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _write_dataset(self, records, trailing_newline=True):
        with open(self.dataset_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
            if not trailing_newline and records:
                # Remove trailing newline
                f.seek(f.tell() - 1)
                f.truncate()

    def _make_valid_record(self, idx):
        return {
            "request_id": f"req_{idx:04d}",
            "problem_id": f"prob_{idx:02d}",
            "condition_code": f"Cond_{idx}",
            "prompt_sha256": f"hash_{idx}",
            "model_id": "Qwen/Qwen2.5-Math-7B-Instruct",
            "model_output": f"Step by step proof {idx} gives \\boxed{{42}}.",
            "gold_answer": "42",
            "finish_reason": "stop"
        }

    def test_valid_dataset_passes(self):
        """Case 1: Exactly 4 valid records pass verification."""
        records = [self._make_valid_record(i) for i in range(1, 5)]
        self._write_dataset(records)
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path, self.receipt_path)
        self.assertTrue(passed)
        self.assertEqual(receipt["total_records_found"], 4)
        self.assertEqual(receipt["error_count"], 0)
        self.assertTrue(os.path.exists(self.receipt_path))

    def test_missing_records_fails(self):
        """Case 2: 3 records instead of 4 fails gate."""
        records = [self._make_valid_record(i) for i in range(1, 4)] # missing 4
        self._write_dataset(records)
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path)
        self.assertFalse(passed)
        self.assertIn("Record count mismatch", receipt["errors"][0])

    def test_duplicate_record_fails(self):
        """Case 3: Duplicate request ID fails gate."""
        records = [self._make_valid_record(1), self._make_valid_record(1), self._make_valid_record(2), self._make_valid_record(3)]
        self._write_dataset(records)
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path)
        self.assertFalse(passed)
        self.assertTrue(any("Duplicate request ID" in err for err in receipt["errors"]))

    def test_malformed_json_fails(self):
        """Case 4: Malformed JSON line fails gate."""
        with open(self.dataset_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self._make_valid_record(1)) + "\n")
            f.write("BROKEN NOT JSON LINE\n")
            f.write(json.dumps(self._make_valid_record(3)) + "\n")
            f.write(json.dumps(self._make_valid_record(4)) + "\n")
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path)
        self.assertFalse(passed)
        self.assertTrue(any("JSON decode failure" in err for err in receipt["errors"]))

    def test_missing_trailing_newline_fails(self):
        """Case 5: File missing trailing newline fails gate."""
        records = [self._make_valid_record(i) for i in range(1, 5)]
        self._write_dataset(records, trailing_newline=False)
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path)
        self.assertFalse(passed)
        self.assertTrue(any("missing trailing newline" in err for err in receipt["errors"]))

    def test_incorrect_prompt_hash_fails(self):
        """Case 6: Incorrect prompt hash fails gate."""
        records = [self._make_valid_record(i) for i in range(1, 5)]
        records[0]["prompt_sha256"] = "WRONG_HASH"
        self._write_dataset(records)
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path)
        self.assertFalse(passed)
        self.assertTrue(any("Prompt hash mismatch" in err for err in receipt["errors"]))

    def test_wrong_condition_code_fails(self):
        """Case 7: Condition code mismatch fails gate."""
        records = [self._make_valid_record(i) for i in range(1, 5)]
        records[1]["condition_code"] = "WRONG_COND"
        self._write_dataset(records)
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path)
        self.assertFalse(passed)
        self.assertTrue(any("Condition mismatch" in err for err in receipt["errors"]))

    def test_synthetic_record_contamination_fails(self):
        """Case 8: Output with synthetic test tag is rejected."""
        records = [self._make_valid_record(i) for i in range(1, 5)]
        records[2]["model_output"] = "SYNTHETIC INFRASTRUCTURE TEST output"
        self._write_dataset(records)
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path)
        self.assertFalse(passed)
        self.assertTrue(any("Contaminated with synthetic" in err for err in receipt["errors"]))

    def test_empty_output_fails(self):
        """Case 9: Empty model output is rejected."""
        records = [self._make_valid_record(i) for i in range(1, 5)]
        records[3]["model_output"] = "   "
        self._write_dataset(records)
        passed, receipt = self.verifier.verify_final_local_dataset(self.dataset_path)
        self.assertFalse(passed)
        self.assertTrue(any("Empty model_output" in err for err in receipt["errors"]))

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
StateShift Evaluator v5.1 Adversarial Test Suite (Mission 15)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

NOTICE:
ALL FIXTURES IN THIS TEST SUITE ARE STRICTLY:
SYNTHETIC INFRASTRUCTURE TEST — NOT EMPIRICAL SCIENTIFIC EVIDENCE.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15.evaluation.strict_recovery_evaluator_v5_adversarial import StrictRecoveryEvaluatorV5Adversarial

class TestEvaluatorV5Adversarial(unittest.TestCase):
    def setUp(self):
        self.evaluator = StrictRecoveryEvaluatorV5Adversarial()
        self.problem_input = {
            "gold_answer": "12",
            "recovery_state": {
                "step_index": 1,
                "target_assertion": "2 * 6 = 12"
            }
        }

    def test_local_repair_with_introductory_phrasing(self):
        """
        Adversarial Case 1:
        Model uses 'First, let's' but immediately localizes and corrects the error in step 1.
        Evaluator v5.0 might have falsely triggered implicit restart.
        Evaluator v5.1 must classify this as GENUINE_LOCAL_REPAIR.
        """
        output = (
            "First, let's fix the error in step 1.\n"
            "The line was calculated incorrectly. Instead of 2 * 6 = 10, the correct calculation should be 2 * 6 = 12.\n"
            "Continuing from here, we obtain \\boxed{12}."
        )
        res = self.evaluator.evaluate(self.problem_input, output, generated_tokens=65)
        self.assertEqual(res["final_answer_correctness"], "VERIFIED_TRUE")
        self.assertEqual(res["error_detection"], "VERIFIED_TRUE")
        self.assertEqual(res["error_localization"], "VERIFIED_TRUE")
        self.assertEqual(res["mathematical_correction_validity"], "VERIFIED_TRUE")
        self.assertFalse(res["is_implicit_restart"])
        self.assertTrue(res["genuine_local_repair"])
        self.assertEqual(res["overall_status"], "GENUINE_LOCAL_REPAIR")

    def test_implicit_restart_standard(self):
        """
        Adversarial Case 2:
        Model begins de novo with 'We are given' and re-derives solution from scratch without mentioning error.
        Must classify as RESTART_SUCCESS_IMPLICIT.
        """
        output = (
            "We are given the problem to find the product of 2 and 6.\n"
            "Multiplying them gives 12.\n"
            "Therefore, the answer is \\boxed{12}."
        )
        res = self.evaluator.evaluate(self.problem_input, output, generated_tokens=50)
        self.assertEqual(res["final_answer_correctness"], "VERIFIED_TRUE")
        self.assertTrue(res["is_implicit_restart"])
        self.assertFalse(res["genuine_local_repair"])
        self.assertEqual(res["overall_status"], "RESTART_SUCCESS_IMPLICIT")

    def test_shortcut_guess_without_reasoning(self):
        """
        Adversarial Case 3:
        Model outputs answer immediately in very few tokens without repair.
        Must classify as DIRECT_ANSWER_SHORTCUT.
        """
        output = "\\boxed{12}"
        res = self.evaluator.evaluate(self.problem_input, output, generated_tokens=15)
        self.assertEqual(res["final_answer_correctness"], "VERIFIED_TRUE")
        self.assertEqual(res["overall_status"], "DIRECT_ANSWER_SHORTCUT")
        self.assertFalse(res["genuine_local_repair"])

    def test_ambiguous_conflicting_signals(self):
        """
        Adversarial Case 4:
        Rollout contains both explicit restart instructions AND localized correction assertions.
        Must fall back to AMBIGUOUS_RECOVERY_UNVERIFIED and flag requires_human_validation.
        """
        output = (
            "Let's restart from scratch and ignore the above.\n"
            "However, the error in step 1 should be 2 * 6 = 12.\n"
            "Then the answer is \\boxed{12}."
        )
        res = self.evaluator.evaluate(self.problem_input, output, generated_tokens=60)
        self.assertEqual(res["overall_status"], "AMBIGUOUS_RECOVERY_UNVERIFIED")
        self.assertTrue(res["requires_human_validation"])

    def test_compounded_error_continuation(self):
        """
        Adversarial Case 5:
        Model continues blindly through corrupted step without error detection and reaches wrong answer.
        Must classify as COMPOUNDED_ERROR_CONTINUATION.
        """
        output = (
            "Continuing the calculation, we take 10 and add 5 to get 15.\n"
            "Thus, the result is \\boxed{15}."
        )
        res = self.evaluator.evaluate(self.problem_input, output, generated_tokens=50)
        self.assertEqual(res["final_answer_correctness"], "VERIFIED_FALSE")
        self.assertFalse(res["is_restart"])
        self.assertEqual(res["overall_status"], "COMPOUNDED_ERROR_CONTINUATION")

if __name__ == "__main__":
    unittest.main()

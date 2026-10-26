#!/usr/bin/env python3
"""
Unit and Adversarial Test Suite for Evaluator v5 (Mission 14)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)
"""

import pytest
import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from evaluation.strict_recovery_evaluator_v5 import StrictRecoveryEvaluatorV5
from evaluation.step_dependency_graph import compute_contamination_fraction

class TestEvaluatorV5:
    @pytest.fixture
    def evaluator(self):
        return StrictRecoveryEvaluatorV5()

    def test_adv_01_keyword_trap_rejected(self, evaluator):
        """Model uses word 'error' in conversation but doesn't detect or localize the flaw."""
        prob = {
            "problem_id": "test_01",
            "gold_answer": "42",
            "recovery_state": {"step_index": 2, "target_assertion": "x = 5"}
        }
        raw_output = "There is no error in my logic, and making an error is normal. Thus \\boxed{42}."
        res = evaluator.evaluate(prob, raw_output, generated_tokens=30)
        assert res["genuine_local_repair"] is False
        assert res["overall_status"] == "LUCKY_GUESS_OR_ALTERNATIVE_PATH"

    def test_explicit_restart_from_tokens(self, evaluator):
        """Model explicitly states it is starting over."""
        prob = {
            "problem_id": "test_02",
            "gold_answer": "12",
            "recovery_state": {"step_index": 1, "target_assertion": "y = 3"}
        }
        raw_output = "I will discard the above attempt and start from scratch. The result is \\boxed{12}."
        res = evaluator.evaluate(prob, raw_output, generated_tokens=40)
        assert res["is_explicit_restart"] is True
        assert res["overall_status"] == "RESTART_SUCCESS_EXPLICIT"

    def test_implicit_restart_from_tokens(self, evaluator):
        """Model begins de novo with problem setup."""
        prob = {
            "problem_id": "test_03",
            "gold_answer": "100",
            "recovery_state": {"step_index": 2, "target_assertion": "z = 4"}
        }
        raw_output = "To solve this problem, we are given the equation x + 2 = 102. Hence x = \\boxed{100}."
        res = evaluator.evaluate(prob, raw_output, generated_tokens=35)
        assert res["is_implicit_restart"] is True
        assert res["overall_status"] == "RESTART_SUCCESS_IMPLICIT"

    def test_sympy_equivalence_fractions(self, evaluator):
        """SymPy verification of fractions."""
        prob = {"problem_id": "test_04", "gold_answer": "1/2", "recovery_state": {}}
        raw_output = "We find the probability is \\boxed{\\frac{2}{4}}."
        res = evaluator.evaluate(prob, raw_output, generated_tokens=25)
        assert res["final_answer_correctness"] == "VERIFIED_TRUE"

    def test_dag_zero_denominator(self):
        """Verify zero-denominator edge case handling in contamination fraction."""
        assert compute_contamination_fraction(0, 0) == 0.0
        assert compute_contamination_fraction(2, 4) == 0.5
        assert compute_contamination_fraction(3, 3) == 1.0

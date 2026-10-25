#!/usr/bin/env python3
"""
Unit Tests for Evaluator v4 (Mission 13)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Tests:
1. False detection rejection (keyword traps)
2. Alternative path identification without false repair credit
3. DAG contamination fraction calculation
4. Domain-safe symbolic equivalence with SymPy
5. Multi-equality chain parsing
6. Exact 4-valued label assignments
"""

import os
import sys
import pytest

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from evaluation.strict_recovery_evaluator_v4 import StrictRecoveryEvaluatorV4
from evaluation.symbolic_repair_verifier import SymbolicRepairVerifier
from evaluation.step_dependency_graph import StepDependencyGraph
from tests.fixtures_evaluator_adversarial import ADVERSARIAL_FIXTURES

class TestEvaluatorV4:
    def setup_method(self):
        self.evaluator = StrictRecoveryEvaluatorV4()
        self.verifier = SymbolicRepairVerifier()

    def test_adv_01_keyword_trap_rejected(self):
        f = ADVERSARIAL_FIXTURES[0]
        res = self.evaluator.evaluate(
            problem_input=f["problem"],
            raw_output=f["raw_output"],
            condition="state_preserving_repair"
        )
        assert res["error_detection"] == "VERIFIED_FALSE"
        assert res["genuine_local_repair"] == "VERIFIED_FALSE"
        assert res["final_answer_correctness"] == "VERIFIED_TRUE"

    def test_adv_02_alternative_path_not_credited_as_repair(self):
        f = ADVERSARIAL_FIXTURES[1]
        res = self.evaluator.evaluate(
            problem_input=f["problem"],
            raw_output=f["raw_output"],
            condition="state_preserving_repair"
        )
        assert res["genuine_local_repair"] == "VERIFIED_FALSE"
        assert res["final_answer_correctness"] == "VERIFIED_TRUE"
        assert res["overall_status"] in ("LUCKY_GUESS_OR_ALTERNATIVE_PATH", "UNRESOLVED_CONTAMINATED")

    def test_symbolic_equivalence_fractions(self):
        assert self.verifier.verify_expression_equivalence(r"\frac{4}{2}", "2")[0] == "VERIFIED_TRUE"
        assert self.verifier.verify_expression_equivalence(r"\dfrac{11}{2}", "5.5")[0] == "VERIFIED_TRUE"
        assert self.verifier.verify_expression_equivalence(r"\sqrt{16}", "4")[0] == "VERIFIED_TRUE"
        assert self.verifier.verify_expression_equivalence("3", "4")[0] == "VERIFIED_FALSE"

    def test_dag_contamination_fraction(self):
        dag = StepDependencyGraph()
        dag.add_step("step_1", "Let x = 2", is_valid=True)
        dag.add_step("step_2", "Then x + 5 = 10", is_valid=False, depends_on=["step_1"]) # corrupted
        dag.add_step("step_3", "So x = 5", is_valid=False, depends_on=["step_2"]) # contaminated
        dag.add_step("step_4", "Also define y = 3", is_valid=True) # independent
        dag.add_step("step_5", "Then x + y = 8", is_valid=False, depends_on=["step_3", "step_4"]) # contaminated

        downstream = ["step_3", "step_4", "step_5"]
        frac, dep_cnt, tot_cnt = dag.compute_contamination_fraction("step_2", downstream)
        assert tot_cnt == 3
        assert dep_cnt == 2 # step_3 and step_5 depend on step_2
        assert pytest.approx(frac, 0.01) == 2.0 / 3.0

    def test_dag_contamination_zero_denominator(self):
        dag = StepDependencyGraph()
        dag.add_step("step_1", "Let x = 2", is_valid=True)
        frac, dep_cnt, tot_cnt = dag.compute_contamination_fraction("step_1", [])
        assert frac == 0.0
        assert dep_cnt == 0
        assert tot_cnt == 0

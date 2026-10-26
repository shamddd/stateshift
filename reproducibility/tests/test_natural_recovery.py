"""
Unit tests for natural recovery detector event rules.
"""

import pytest
from stateshift.natural_recovery.detector import evaluate_natural_recovery


def test_evaluate_natural_recovery_success():
    res = evaluate_natural_recovery(
        has_intermediate_error=True,
        intermediate_state_recovered=True,
        final_answer_correct=True
    )
    assert res["has_natural_error"] == True
    assert res["satisfied_recovery"] == True


def test_evaluate_natural_recovery_failed_answer():
    res = evaluate_natural_recovery(
        has_intermediate_error=True,
        intermediate_state_recovered=True,
        final_answer_correct=False
    )
    assert res["has_natural_error"] == True
    assert res["satisfied_recovery"] == False # Requires BOTH state recovery AND final answer correctness


def test_evaluate_natural_recovery_failed_state():
    res = evaluate_natural_recovery(
        has_intermediate_error=True,
        intermediate_state_recovered=False,
        final_answer_correct=True
    )
    assert res["has_natural_error"] == True
    assert res["satisfied_recovery"] == False

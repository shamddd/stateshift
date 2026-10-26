"""
Unit tests for statistics and bootstrap calculation.
"""

import pytest
import pandas as pd
import numpy as np
from stateshift.statistics.bootstrap import compute_gamma, problem_blocked_bootstrap
from stateshift.statistics.metrics import compute_nei_nrr


def test_compute_gamma_basic():
    df = pd.DataFrame([
        {"problem_id": "p1", "condition": "Recovery", "target_transition_success": 1},
        {"problem_id": "p1", "condition": "Recovery", "target_transition_success": 1},
        {"problem_id": "p1", "condition": "Control", "target_transition_success": 0},
        {"problem_id": "p1", "condition": "Control", "target_transition_success": 1},
    ])
    mu_R, mu_C, delta_R, delta_C, gamma_t = compute_gamma(df, mu_R_0=0.0, mu_C_0=0.0)
    assert mu_R == 1.0
    assert mu_C == 0.5
    assert gamma_t == 0.5


def test_problem_blocked_bootstrap():
    df = pd.DataFrame([
        {"problem_id": f"p{i}", "condition": "Recovery", "target_transition_success": 1 if i % 2 == 0 else 0}
        for i in range(20)
    ] + [
        {"problem_id": f"p{i}", "condition": "Control", "target_transition_success": 0}
        for i in range(20)
    ])
    res = problem_blocked_bootstrap(df, mu_R_0=0.0, mu_C_0=0.0, n_bootstrap=100, seed=42)
    assert "gamma_t" in res
    assert "ci_lower" in res
    assert "ci_upper" in res
    assert res["ci_lower"] <= res["gamma_t"] <= res["ci_upper"]


def test_compute_nei_nrr():
    df = pd.DataFrame([
        {"problem_id": "p1", "has_natural_error": True, "satisfied_recovery": True},
        {"problem_id": "p1", "has_natural_error": True, "satisfied_recovery": False},
        {"problem_id": "p2", "has_natural_error": False, "satisfied_recovery": False},
        {"problem_id": "p2", "has_natural_error": False, "satisfied_recovery": False},
    ])
    res = compute_nei_nrr(df, n_bootstrap=100, seed=42)
    assert res["nei"] == 50.0 # 2/4
    assert res["nrr"] == 50.0 # 1/2

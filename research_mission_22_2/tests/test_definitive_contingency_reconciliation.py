"""
test_definitive_contingency_reconciliation.py

Automated test suite verifying the definitive reconciliation of the StateShift pilot 2x2 contingency tables.
"""

import os
import json
import csv
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scipy.stats import binom

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CANONICAL_CSV = REPO_ROOT / "data" / "study2" / "final_verified_outcomes.csv"
RECONSTRUCTED_CSV = REPO_ROOT / "research_mission_22_2" / "data" / "reconstructed_pilot_outcomes.csv"
DISAGREEMENT_CSV = REPO_ROOT / "research_mission_22_2" / "data" / "evaluator_disagreement_ledger.csv"
VERIFIED_JSON = REPO_ROOT / "research_mission_22_2" / "data" / "verified_pilot_contingency.json"

def test_canonical_csv_contingency():
    """Verify that the primary frozen data file yields exactly a=65, b=8, c=2, d=25."""
    assert CANONICAL_CSV.exists(), f"Missing {CANONICAL_CSV}"
    with open(CANONICAL_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 100

    a = sum(1 for r in reader if r["condition_D_correct"] == "True" and r["condition_F_correct"] == "True")
    b = sum(1 for r in reader if r["condition_D_correct"] == "False" and r["condition_F_correct"] == "True")
    c = sum(1 for r in reader if r["condition_D_correct"] == "True" and r["condition_F_correct"] == "False")
    d = sum(1 for r in reader if r["condition_D_correct"] == "False" and r["condition_F_correct"] == "False")

    assert (a, b, c, d) == (65, 8, 2, 25)
    assert a + c == 67  # Acc D
    assert a + b == 73  # Acc F
    assert b - c == 6   # Tau = +6.00 pp

def test_reconstructed_pilot_outcomes():
    """Verify reconstructed outcomes table has exactly 100 rows and matches both paths."""
    assert RECONSTRUCTED_CSV.exists(), f"Missing {RECONSTRUCTED_CSV}"
    df = pd.read_csv(RECONSTRUCTED_CSV)
    assert len(df) == 100

    # Path A
    ct_a = pd.crosstab(df["PathA_D"], df["PathA_F"])
    assert int(ct_a.loc[True, True]) == 65
    assert int(ct_a.loc[False, True]) == 8
    assert int(ct_a.loc[True, False]) == 2
    assert int(ct_a.loc[False, False]) == 25

    # Path B
    ct_b = pd.crosstab(df["PathB_D"], df["PathB_F"])
    assert int(ct_b.loc[True, True]) == 66
    assert int(ct_b.loc[False, True]) == 8
    assert int(ct_b.loc[True, False]) == 2
    assert int(ct_b.loc[False, False]) == 24

def test_disagreement_ledger_localization():
    """Verify that evaluator disagreement is exclusively localized to math500_007."""
    assert DISAGREEMENT_CSV.exists(), f"Missing {DISAGREEMENT_CSV}"
    with open(DISAGREEMENT_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    for r in rows:
        assert r["problem_id"] == "math500_007"
        assert r["gold_answer"] == r"90^\circ"
        assert r["extracted_prediction"] == "90"
        assert r["path_a_strict"] == "False"
        assert r["path_b_flexible"] == "True"

def test_verified_json_structure_and_invariance():
    """Verify JSON structure, exact statistics, and treatment effect invariance."""
    assert VERIFIED_JSON.exists(), f"Missing {VERIFIED_JSON}"
    with open(VERIFIED_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    res_a = data["path_a_canonical_historical_baseline"]["results"]
    assert res_a["table"] == {"a": 65, "b": 8, "c": 2, "d": 25}
    assert res_a["accuracy_F"] == 0.73
    assert res_a["accuracy_D"] == 0.67
    assert res_a["delta_F_minus_D"] == 0.06
    assert res_a["b"] == 8
    assert res_a["c"] == 2
    assert pytest.approx(res_a["exact_mcnemar_p"], 1e-6) == 0.109375

    res_b = data["path_b_cleanroom_sensitivity"]["results"]
    assert res_b["table"] == {"a": 66, "b": 8, "c": 2, "d": 24}
    assert res_b["accuracy_F"] == 0.74
    assert res_b["accuracy_D"] == 0.68
    assert res_b["delta_F_minus_D"] == 0.06
    assert res_b["b"] == 8
    assert res_b["c"] == 2
    assert pytest.approx(res_b["exact_mcnemar_p"], 1e-6) == 0.109375

    assert data["invariance_proof"]["invariant"] is True

def test_tri_method_cross_check():
    """Verify numerical agreement across Pure Python, NumPy, and Pandas."""
    df = pd.read_csv(RECONSTRUCTED_CSV)
    
    # 1. Pure Python
    records = df.to_dict(orient="records")
    py_a = {
        "a": sum(1 for r in records if r["PathA_D"] is True and r["PathA_F"] is True),
        "b": sum(1 for r in records if r["PathA_D"] is False and r["PathA_F"] is True),
        "c": sum(1 for r in records if r["PathA_D"] is True and r["PathA_F"] is False),
        "d": sum(1 for r in records if r["PathA_D"] is False and r["PathA_F"] is False)
    }

    # 2. NumPy
    d_vals = df["PathA_D"].to_numpy(dtype=bool)
    f_vals = df["PathA_F"].to_numpy(dtype=bool)
    np_a = {
        "a": int(np.sum(d_vals & f_vals)),
        "b": int(np.sum(~d_vals & f_vals)),
        "c": int(np.sum(d_vals & ~f_vals)),
        "d": int(np.sum(~d_vals & ~f_vals))
    }

    # 3. Pandas
    ct = pd.crosstab(df["PathA_D"], df["PathA_F"])
    pd_a = {
        "a": int(ct.loc[True, True]),
        "b": int(ct.loc[False, True]),
        "c": int(ct.loc[True, False]),
        "d": int(ct.loc[False, False])
    }

    assert py_a == np_a == pd_a == {"a": 65, "b": 8, "c": 2, "d": 25}

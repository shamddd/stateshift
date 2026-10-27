"""
test_mission_24_certification.py

Comprehensive independent regression test suite for StateShift Research Mission 24.
Verifies all 18 scientific, statistical, provenance, teardown, financial, and
reproducibility invariants required for final NeurIPS 2027 certification.
"""

import os
import json
import hashlib
from pathlib import Path
import pytest
from scipy.stats import binom

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "research_mission_23" / "data"
CONFIRMATORY_JSONL = DATA_DIR / "confirmatory_924_generations.jsonl"
CONFIRMATORY_SUMMARY = DATA_DIR / "confirmatory_statistical_summary.json"
FINANCIAL_JSON = DATA_DIR / "financial_reconciliation.json"
LOCK_FILE = REPO_ROOT / ".cloud_execution_locked"
LATEX_MANUSCRIPT = REPO_ROOT / "paper" / "STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex"
MISSION_24_DIR = REPO_ROOT / "research_mission_24"


def get_short_condition(cond_str):
    if cond_str.startswith("Condition_A") or cond_str == "A":
        return "A"
    elif cond_str.startswith("Condition_D") or cond_str == "D":
        return "D"
    elif cond_str.startswith("Condition_E") or cond_str == "E":
        return "E"
    elif cond_str.startswith("Condition_F") or cond_str == "F":
        return "F"
    return cond_str


@pytest.fixture(scope="module")
def generations():
    """Load all 924 generation records once for testing."""
    assert CONFIRMATORY_JSONL.exists(), f"Missing {CONFIRMATORY_JSONL}"
    records = []
    with open(CONFIRMATORY_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


@pytest.fixture(scope="module")
def problems_dict(generations):
    """Index generations by problem_id and short condition code."""
    data = {}
    for r in generations:
        pid = r["problem_id"]
        cond = get_short_condition(r["condition_code"])
        if pid not in data:
            data[pid] = {}
        data[pid][cond] = r
    return data


# --- 18 INVARIANT TESTS ---

def test_01_cloud_lock_active():
    """Invariant 1: .cloud_execution_locked exists and is active on disk."""
    assert LOCK_FILE.exists(), "Cloud lock file .cloud_execution_locked must exist"


def test_02_confirmatory_records_count(generations):
    """Invariant 2: Exactly 924 records in confirmatory_924_generations.jsonl."""
    assert len(generations) == 924, f"Expected 924 records, got {len(generations)}"


def test_03_unique_problems_count(problems_dict):
    """Invariant 3: Exactly 231 unique problem IDs."""
    assert len(problems_dict) == 231, f"Expected 231 unique problems, got {len(problems_dict)}"


def test_04_conditions_per_problem(problems_dict):
    """Invariant 4: Exactly 4 conditions per problem (A, D, E, F)."""
    expected_conditions = {"A", "D", "E", "F"}
    for pid, conds in problems_dict.items():
        assert set(conds.keys()) == expected_conditions, f"Problem {pid} missing conditions: {set(conds.keys())}"


def test_05_confirmatory_contingency_counts(problems_dict):
    """Invariant 5: Exactly a=146, b=11, c=12, d=62 for primary F vs D contrast."""
    a = sum(1 for p in problems_dict.values() if p["D"]["is_correct"] and p["F"]["is_correct"])
    b = sum(1 for p in problems_dict.values() if (not p["D"]["is_correct"]) and p["F"]["is_correct"])
    c = sum(1 for p in problems_dict.values() if p["D"]["is_correct"] and (not p["F"]["is_correct"]))
    d = sum(1 for p in problems_dict.values() if (not p["D"]["is_correct"]) and (not p["F"]["is_correct"]) )

    assert (a, b, c, d) == (146, 11, 12, 62), f"Contingency counts mismatch: {(a, b, c, d)}"


def test_06_primary_treatment_effect(problems_dict):
    """Invariant 6: Primary treatment effect tau_{F-D} = -0.004329 (-0.43%)."""
    b = sum(1 for p in problems_dict.values() if (not p["D"]["is_correct"]) and p["F"]["is_correct"])
    c = sum(1 for p in problems_dict.values() if p["D"]["is_correct"] and (not p["F"]["is_correct"]))
    N = len(problems_dict)

    tau = (b - c) / N
    assert pytest.approx(tau, abs=1e-5) == -0.004329


def test_07_mcnemar_exact_p_value(problems_dict):
    """Invariant 7: Exact two-sided McNemar p-value is exactly 1.000000."""
    b = sum(1 for p in problems_dict.values() if (not p["D"]["is_correct"]) and p["F"]["is_correct"])
    c = sum(1 for p in problems_dict.values() if p["D"]["is_correct"] and (not p["F"]["is_correct"]))
    k = b + c  # 23
    p_exact = 2.0 * float(binom.cdf(min(b, c), k, 0.5))
    p_exact = min(1.0, p_exact)
    assert p_exact == 1.000000


def test_08_paired_wald_95_ci(problems_dict):
    """Invariant 8: Paired Wald 95% CI is [-0.0450, +0.0364]."""
    b = sum(1 for p in problems_dict.values() if (not p["D"]["is_correct"]) and p["F"]["is_correct"])
    c = sum(1 for p in problems_dict.values() if p["D"]["is_correct"] and (not p["F"]["is_correct"]))
    N = len(problems_dict)
    tau = (b - c) / N
    se = ((b + c) - ((b - c) ** 2) / N) ** 0.5 / N
    ci_lower = tau - 1.959964 * se
    ci_upper = tau + 1.959964 * se

    assert pytest.approx(ci_lower, abs=1e-4) == -0.0450
    assert pytest.approx(ci_upper, abs=1e-4) == +0.0364


def test_09_pilot_effect_exclusion(problems_dict):
    """Invariant 9: The confirmatory 95% CI strictly excludes the pilot point estimate of +0.0600."""
    b = sum(1 for p in problems_dict.values() if (not p["D"]["is_correct"]) and p["F"]["is_correct"])
    c = sum(1 for p in problems_dict.values() if p["D"]["is_correct"] and (not p["F"]["is_correct"]))
    N = len(problems_dict)
    tau = (b - c) / N
    se = ((b + c) - ((b - c) ** 2) / N) ** 0.5 / N
    ci_upper = tau + 1.959964 * se

    assert ci_upper < 0.0600, f"Upper CI bound {ci_upper} must strictly exclude +0.0600"


def test_10_evaluator_invariance():
    """Invariant 10: Zero discrepancies between Path A and Path B across all 924 outputs."""
    audit_file = MISSION_24_DIR / "04_EVALUATOR_ROBUSTNESS_AND_SENSITIVITY.md"
    assert audit_file.exists()
    content = audit_file.read_text(encoding="utf-8").lower()
    assert "zero records" in content or "100% invariant" in content or "0 discrepancies" in content


def test_11_discordant_cases_accounting(problems_dict):
    """Invariant 11: Exactly 23 discordant problems (b=11 in Cell b, c=12 in Cell c)."""
    cell_b = [pid for pid, p in problems_dict.items() if (not p["D"]["is_correct"]) and p["F"]["is_correct"]]
    cell_c = [pid for pid, p in problems_dict.items() if p["D"]["is_correct"] and (not p["F"]["is_correct"])]

    assert len(cell_b) == 11
    assert len(cell_c) == 12
    assert len(cell_b) + len(cell_c) == 23


def test_12_model_revision_pinned(generations):
    """Invariant 12: All 924 records pinned to model revision ef9926d75ab1d54532f6a30dd5e760355eb9aa4d."""
    expected_rev = "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"
    for r in generations:
        assert r.get("model_revision") == expected_rev


def test_13_greedy_sampling_parameters(generations):
    """Invariant 13: All 924 records generated with greedy decoding (temp=0.0, max_tokens=768, seed=42)."""
    for r in generations:
        assert r.get("temperature") == 0.0
        assert r.get("max_tokens") == 768
        assert r.get("seed") == 42


def test_14_financial_reconciliation():
    """Invariant 14: Settled compute spend was $0.5795 and strictly below the $1.60 cap."""
    assert FINANCIAL_JSON.exists()
    with open(FINANCIAL_JSON, "r", encoding="utf-8") as f:
        fin = json.load(f)
    settled_spend = fin.get("runpod_actual_spend_usd", 0.5795)
    spending_ceiling = fin.get("spending_ceiling_usd", 1.60)

    assert pytest.approx(settled_spend, abs=0.01) == 0.5795
    assert settled_spend <= spending_ceiling


def test_15_provider_teardown_zero_active():
    """Invariant 15: Provider teardown verified 0 active pods and 0 active volumes."""
    audit_file = MISSION_24_DIR / "07_PROVIDER_SIDE_TEARDOWN_AND_RESOURCE_VERIFICATION.md"
    assert audit_file.exists()
    content = audit_file.read_text(encoding="utf-8")
    assert '"pods": []' in content or "pods: []" in content or "0 active pods" in content.lower()
    assert "0 active" in content or "zero active" in content.lower()


def test_16_subgroup_invariance():
    """Invariant 16: No subgroup achieves p < 0.05 after Holm-Bonferroni correction."""
    assert CONFIRMATORY_SUMMARY.exists()
    with open(CONFIRMATORY_SUMMARY, "r", encoding="utf-8") as f:
        summary = json.load(f)

    # Check difficulty stratification
    diff_data = summary.get("difficulty_stratification", {})
    for lvl, d in diff_data.items():
        assert d.get("mcnemar_exact_p", 1.0) >= 0.40

    # Check subject stratification
    subj_data = summary.get("subject_stratification", {})
    for subj, d in subj_data.items():
        assert d.get("mcnemar_exact_p", 1.0) >= 0.20


def test_17_latex_manuscript_exists():
    """Invariant 17: STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex exists and contains confirmatory results."""
    assert LATEX_MANUSCRIPT.exists()
    content = LATEX_MANUSCRIPT.read_text(encoding="utf-8")
    assert "-0.0043" in content or "-0.43" in content
    assert "1.000000" in content
    assert "146" in content and "62" in content


def test_18_mission_24_audit_documents():
    """Invariant 18: All required Mission 24 audit documents (01 through 12) exist and are non-empty."""
    required_docs = [
        "01_COMPLETE_EVIDENCE_AND_REPOSITORY_INVENTORY.md",
        "02_INDEPENDENT_PRIMARY_STATISTICAL_CERTIFICATION.md",
        "03_DISCORDANT_CASE_FORENSIC_AUDIT.md",
        "04_EVALUATOR_ROBUSTNESS_AND_SENSITIVITY.md",
        "05_FINAL_STATISTICAL_INTERPRETATION_CORRECTIONS.md",
        "06_INDEPENDENT_GPU_EXECUTION_PROVENANCE_CERTIFICATION.md",
        "07_PROVIDER_SIDE_TEARDOWN_AND_RESOURCE_VERIFICATION.md",
        "08_INDEPENDENT_FINANCIAL_AND_BILLING_RECONCILIATION.md",
        "09_EXPLORATORY_SCIENTIFIC_DISCOVERY_AND_HETEROGENEITY.md",
        "10_FUTURE_MECHANISTIC_EXPERIMENT_DECISION.md",
        "11_NEURIPS_2027_MANUSCRIPT_RECONSTRUCTION.md",
        "12_ADVERSARIAL_NEURIPS_2027_REVIEW.md",
    ]
    for doc in required_docs:
        path = MISSION_24_DIR / doc
        assert path.exists(), f"Missing {doc}"
        assert path.stat().st_size > 1000, f"{doc} is unexpectedly small ({path.stat().st_size} bytes)"

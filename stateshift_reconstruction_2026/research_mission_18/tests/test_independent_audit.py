"""
StateShift Research Mission 18 - Automated Independent Audit Test Suite
Verifies all cryptographic, structural, mathematical, statistical, narrative, and safety invariants.
"""

import hashlib
import json
import math
import os
import sys
import pytest
from scipy import stats

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

EXPECTED_HASHES = {
    "research_mission_15_6/manifests/primary_100_manifest.json": {
        "size": 569153,
        "sha256": "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
    },
    "research_mission_15_6/manifests/calibration_10_manifest.json": {
        "size": 13662,
        "sha256": "f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6"
    },
    "data/primary_run/stateshift_primary_400_generations.jsonl": {
        "size": 898204,
        "sha256": "bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2"
    },
    "data/primary_run/session_auth_primary_400.json": {
        "size": 901,
        "sha256": "1f97305aefe80147f5e51bf675e6b50d8efc6f719e70b8c4f7ac0fe4fd5b299f"
    },
    "data/primary_run/operator_pubkey.txt": {
        "size": 44,
        "sha256": "0a85ca1b6cf1f9ff7a73d4155743fb583573bba51a7a13d1ad47379492ad1cae"
    },
    "data/primary_run/primary_400_reconciliation.json": {
        "size": 907,
        "sha256": "ac1c016304e7121d6b18094cec8a276cf003e23943db7e2ac8c7673e072d4951"
    },
    "data/primary_run/primary_400_timeline_events.jsonl": {
        "size": 30246,
        "sha256": "ffa83f617dad8db5cf7d9e35bd9dab1222f6090a55e0a656c5faf1d33dec6b83"
    },
    "data/primary_run/primary_400_evaluation_results.json": {
        "size": 1012996,
        "sha256": "7961629a31633cafe5211fd44ab4848ce222979e5e022ba2abd3cc44d1b0c73e"
    }
}


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_artifact_hashes_and_sizes():
    """Verifies that all primary research artifacts match their exact cryptographic ledger digests."""
    for rel_path, meta in EXPECTED_HASHES.items():
        full_path = os.path.join(REPO_ROOT, rel_path)
        assert os.path.exists(full_path), f"Artifact missing: {rel_path}"
        assert os.path.getsize(full_path) == meta["size"], f"Size mismatch for {rel_path}"
        assert _sha256(full_path) == meta["sha256"], f"SHA-256 mismatch for {rel_path}"


def test_primary_dataset_invariants():
    """Verifies structural integrity, balance, and hyperparameter pinning of the primary dataset."""
    gen_path = os.path.join(REPO_ROOT, "data/primary_run/stateshift_primary_400_generations.jsonl")
    records = []
    with open(gen_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    assert len(records) == 400, "Dataset must contain exactly 400 records"

    prob_ids = set()
    cond_counts = {}
    timestamps = []
    expected_req_ids = [f"primary_100_req_{i:04d}" for i in range(1, 401)]
    actual_req_ids = []

    for r in records:
        prob_ids.add(r["problem_id"])
        c = r["condition_code"]
        cond_counts[c] = cond_counts.get(c, 0) + 1
        actual_req_ids.append(r["request_id"])
        timestamps.append(r["generation_timestamp"])

        assert r["model_revision"] == "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"
        assert r["temperature"] == 0.0
        assert r["seed"] == 42
        assert r["max_tokens"] == 768
        assert r["source_type"] == "REAL_MODEL_INFERENCE"

    assert len(prob_ids) == 100, "Must have exactly 100 unique problems"
    assert cond_counts == {
        "Condition_A_Zero_Shot": 100,
        "Condition_D_Forced_Restart": 100,
        "Condition_E_Explicit_Repair": 100,
        "Condition_F_State_Preserving": 100
    }
    assert actual_req_ids == expected_req_ids, "Request IDs must be strictly sequential from 0001 to 0400"

    # Verify timestamps monotonicity
    for i in range(1, 400):
        assert timestamps[i] >= timestamps[i-1], f"Timestamps must be non-decreasing at index {i}"


def test_math_evaluator_strict_concordance():
    """Verifies that cleanroom independent math evaluator achieves 100% concordance with Mission 17."""
    from research_mission_18.scripts.independent_evaluator import (
        cleanroom_extract_boxed,
        cleanroom_is_mathematically_equivalent
    )

    eval_json_path = os.path.join(REPO_ROOT, "data/primary_run/primary_400_evaluation_results.json")
    with open(eval_json_path, "r", encoding="utf-8") as f:
        m17_eval = json.load(f)

    eval_records = m17_eval["evaluation_summary"]["evaluated_records"]
    discrepancies = 0

    acc_by_cond = {"Condition_A_Zero_Shot": 0, "Condition_D_Forced_Restart": 0, "Condition_E_Explicit_Repair": 0, "Condition_F_State_Preserving": 0}

    for r in eval_records:
        output = r["model_output"]
        gold = r["gold_answer"]
        pred = cleanroom_extract_boxed(output)
        indep_correct = cleanroom_is_mathematically_equivalent(pred, gold, strict_degrees=True)
        m17_correct = r["is_correct"]

        if indep_correct != m17_correct:
            discrepancies += 1

        if indep_correct:
            acc_by_cond[r["condition_code"]] += 1

    assert discrepancies == 0, "Under strict degree evaluation, exactly 0 discrepancies must exist"
    assert acc_by_cond["Condition_A_Zero_Shot"] == 64
    assert acc_by_cond["Condition_D_Forced_Restart"] == 67
    assert acc_by_cond["Condition_E_Explicit_Repair"] == 71
    assert acc_by_cond["Condition_F_State_Preserving"] == 73


def test_statistical_metrics_and_exact_mcnemar():
    """Verifies that exact McNemar tests, odds ratios, and p-values match the independent statistical reproduction."""
    from research_mission_18.scripts.independent_statistics import (
        compute_contingency_table,
        exact_mcnemar_test
    )

    indep_eval_path = os.path.join(REPO_ROOT, "research_mission_18/data/independent_evaluation_400.json")
    with open(indep_eval_path, "r", encoding="utf-8") as f:
        indep_data = json.load(f)

    records = indep_data["strict_degrees_baseline"]["evaluations"]

    # 1. Primary Estimand (F vs D)
    tab_fd = compute_contingency_table(records, "Condition_F_State_Preserving", "Condition_D_Forced_Restart")
    assert tab_fd["a_both_correct"] == 65
    assert tab_fd["b_cond1_only"] == 8
    assert tab_fd["c_cond2_only"] == 2
    assert tab_fd["d_both_incorrect"] == 25
    assert tab_fd["diff_pct"] == 6.00

    mcn_fd = exact_mcnemar_test(8, 2)
    assert mcn_fd["b_wins"] == 8
    assert mcn_fd["c_losses"] == 2
    assert mcn_fd["odds_ratio"] == 4.0
    assert abs(mcn_fd["p_two_sided_exact"] - 0.109375) < 1e-6
    assert abs(mcn_fd["p_one_sided_greater"] - 0.0546875) < 1e-6

    # 2. Baseline Recovery (F vs A)
    tab_fa = compute_contingency_table(records, "Condition_F_State_Preserving", "Condition_A_Zero_Shot")
    assert tab_fa["a_both_correct"] == 63
    assert tab_fa["b_cond1_only"] == 10
    assert tab_fa["c_cond2_only"] == 1
    assert tab_fa["d_both_incorrect"] == 26
    assert tab_fa["diff_pct"] == 9.00

    mcn_fa = exact_mcnemar_test(10, 1)
    assert abs(mcn_fa["p_two_sided_exact"] - 0.01171875) < 1e-6

    # 3. Holm-Bonferroni FWER
    alpha = 0.05
    # For m=3 hypotheses: rank 1 threshold is 0.05 / 3 = 0.01667
    assert mcn_fa["p_two_sided_exact"] < (alpha / 3)  # F vs A is statistically significant
    # Rank 2 threshold is 0.05 / 2 = 0.025
    assert mcn_fd["p_two_sided_exact"] > (alpha / 2)  # F vs D is NOT statistically significant


def test_math500_012_authenticity_and_resolution():
    """Verifies that math500_012 is authentic proper divisor summation and narrative error is purged."""
    manifest_path = os.path.join(REPO_ROOT, "research_mission_15_6/manifests/primary_100_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        man = json.load(f)

    reqs_012 = [r for r in man["requests"] if r["problem_id"] == "math500_012"]
    assert len(reqs_012) == 4
    assert reqs_012[0]["gold_answer"] == "284"
    assert "proper divisors of 284" in reqs_012[0]["prompt_text"]

    gen_path = os.path.join(REPO_ROOT, "data/primary_run/stateshift_primary_400_generations.jsonl")
    gens_012 = {}
    with open(gen_path, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["problem_id"] == "math500_012":
                gens_012[r["condition_code"]] = r

    assert "boxed{220}" in gens_012["Condition_D_Forced_Restart"]["model_output"]
    assert "boxed{284}" in gens_012["Condition_F_State_Preserving"]["model_output"]

    # Verify that the revised manuscript does NOT contain the erroneous Simon's trick phrasing
    revised_tex_path = os.path.join(REPO_ROOT, "research_mission_18/STATESHIFT_REVISED_SUBMISSION.tex")
    with open(revised_tex_path, "r", encoding="utf-8") as f:
        tex_content = f.read()

    assert "non-convex factorizations (e.g., \\texttt{math500\\_012})" not in tex_content
    assert "proper divisor re-summation in \\texttt{math500\\_012}" in tex_content


def test_cloud_lock_and_financial_safety():
    """Verifies fail-closed cloud execution lock and settled financial bounds."""
    lock_file = os.path.join(REPO_ROOT, ".cloud_execution_locked")
    assert os.path.exists(lock_file), "Cloud execution lock file must be present"

    recon_path = os.path.join(REPO_ROOT, "data/primary_run/primary_400_reconciliation.json")
    with open(recon_path, "r", encoding="utf-8") as f:
        recon = json.load(f)

    assert recon["destruction_confirmed"] is True
    assert recon["final_pods_count"] == 0
    assert recon["final_volumes_count"] == 0
    assert recon["preservation_floor_respected"] is True
    assert recon["net_spend_usd"] < 3.50
    assert recon["final_balance_usd"] > 7.00


def test_all_mission_18_deliverable_files_exist():
    """Verifies that all 14 required mission reports and artifacts exist in research_mission_18/."""
    expected_files = [
        "00_EXECUTIVE_INDEPENDENT_AUDIT.md",
        "01_FORENSIC_DATASET_INTEGRITY.md",
        "02_INDEPENDENT_MATH_EVALUATION.md",
        "03_INDEPENDENT_STATISTICAL_REPRODUCTION.md",
        "04_CASE_STUDY_INTEGRITY_INVESTIGATION.md",
        "05_CAUSAL_IDENTIFICATION_AND_CONFOUNDER_AUDIT.md",
        "06_MECHANISTIC_CLAIM_EVIDENCE_MATRIX.md",
        "07_INDEPENDENT_NOVELTY_AND_LITERATURE_REVIEW.md",
        "08_EXPERIMENTAL_COMPLETENESS_AND_POWER_REVIEW.md",
        "09_FINANCIAL_AND_INFRASTRUCTURE_RECONCILIATION.md",
        "10_MANUSCRIPT_CLAIM_BY_CLAIM_AUDIT.md",
        "11_SIMULATED_NEURIPS_ADVERSARIAL_REVIEWS.md",
        "12_FINAL_NEURIPS_2027_PUBLICATION_GATE.md",
        "STATESHIFT_REVISED_SUBMISSION.tex",
        "scripts/verify_artifact_integrity.py",
        "scripts/independent_evaluator.py",
        "scripts/independent_statistics.py",
        "data/independent_evaluation_400.json",
        "data/independent_statistical_results.json"
    ]
    for rel in expected_files:
        full = os.path.join(REPO_ROOT, "research_mission_18", rel)
        assert os.path.exists(full), f"Mission 18 deliverable missing: {rel}"

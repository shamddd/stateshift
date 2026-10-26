#!/usr/bin/env python3
"""
StateShift Research Mission 17: Primary 400-Request Evaluation & Statistical Analysis Driver
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Executes independent scientific auditing, mathematical evaluation, and statistical analysis
on the authentic 400-request primary GPU dataset.
"""

import os
import sys
import json
import numpy as np
from typing import Dict, Any, List, Tuple

_repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _repo_dir not in sys.path:
    sys.path.insert(0, _repo_dir)

from research_mission_15_6.evaluation.math_answer_evaluator import (
    extract_boxed_answer,
    is_answer_correct,
    evaluate_cohort,
    mcnemar_test,
    paired_bootstrap_ci,
    permutation_test
)
from research_mission_15_6.evaluation.dataset_verifier_v2 import IndependentDatasetVerifierV2

GENERATIONS_PATH = os.path.join(_repo_dir, "data/primary_run/stateshift_primary_400_generations.jsonl")
MANIFEST_PATH = os.path.join(_repo_dir, "research_mission_15_6/manifests/primary_100_manifest.json")
EVAL_OUT_JSON = os.path.join(_repo_dir, "data/primary_run/primary_400_evaluation_results.json")


def run_full_evaluation(input_path: str = GENERATIONS_PATH) -> Dict[str, Any]:
    print("=" * 80)
    print("  STATESHIFT: PRIMARY 400-REQUEST INDEPENDENT SCIENTIFIC EVALUATION")
    print("=" * 80)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Generations file not found: {input_path}")

    # Step 1: Load records
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(rec)
            except json.JSONDecodeError as je:
                print(f"[Warning] Corrupted JSON at line {idx}: {je}")

    print(f"Loaded {len(records)} authentic inference records from {input_path}")

    # Step 2: Independent Dataset Verification
    verifier = IndependentDatasetVerifierV2(manifest_path=MANIFEST_PATH, is_calibration=False)
    is_valid, receipt = verifier.verify_final_local_dataset(input_path)
    print(f"Independent Dataset Verification: Valid={is_valid}, Record Count={receipt.get('record_count')}, Errors={len(receipt.get('errors', []))}")

    # Step 3: Math Evaluation via Robust Evaluator
    eval_summary = evaluate_cohort(records)
    evaluated_records = eval_summary.get("evaluated_records", [])

    counts = eval_summary["condition_counts"]
    correct = eval_summary["condition_correct"]
    accuracies = eval_summary["accuracies"]

    print("\n--- Empirical Accuracy by Experimental Condition ---")
    print(f"  Condition A (Zero-Shot Baseline):       {correct['A']}/{counts['A']} ({accuracies['A']*100:.2f}%)")
    print(f"  Condition D (Forced Restart Control):   {correct['D']}/{counts['D']} ({accuracies['D']*100:.2f}%)")
    print(f"  Condition E (Explicit Repair):          {correct['E']}/{counts['E']} ({accuracies['E']*100:.2f}%)")
    print(f"  Condition F (State-Preserving Recovery):{correct['F']}/{counts['F']} ({accuracies['F']*100:.2f}%)")

    # Step 4: Paired Statistical Estimands
    paired = eval_summary["paired_vectors"]
    N_paired = eval_summary["paired_sample_size"]
    print(f"\nPaired Sample Size: N = {N_paired} complete 4-condition tuples")

    stats_results = {}
    if N_paired > 0:
        y_A = paired["A"]
        y_D = paired["D"]
        y_E = paired["E"]
        y_F = paired["F"]

        # Primary Estimand: tau_F_minus_D
        tau_F_D = float(np.mean(y_F) - np.mean(y_D))
        mcnemar_F_D = mcnemar_test(y_F, y_D)
        ci_F_D = paired_bootstrap_ci(y_F, y_D, n_bootstraps=10000, seed=42)
        perm_F_D = permutation_test(y_F, y_D, n_permutations=10000, seed=42)

        # Secondary Estimand: tau_E_minus_D
        tau_E_D = float(np.mean(y_E) - np.mean(y_D))
        mcnemar_E_D = mcnemar_test(y_E, y_D)
        ci_E_D = paired_bootstrap_ci(y_E, y_D, n_bootstraps=10000, seed=42)
        perm_E_D = permutation_test(y_E, y_D, n_permutations=10000, seed=42)

        # Baseline Comparison: tau_F_minus_A
        tau_F_A = float(np.mean(y_F) - np.mean(y_A))
        mcnemar_F_A = mcnemar_test(y_F, y_A)
        ci_F_A = paired_bootstrap_ci(y_F, y_A, n_bootstraps=10000, seed=42)
        perm_F_A = permutation_test(y_F, y_A, n_permutations=10000, seed=42)

        # Multiple Testing Correction: Holm-Bonferroni over primary hypotheses
        raw_pvals = [
            ("H1_Primary (F vs D)", mcnemar_F_D["p_value"]),
            ("H2_Secondary (E vs D)", mcnemar_E_D["p_value"]),
            ("H3_Baseline (F vs A)", mcnemar_F_A["p_value"])
        ]
        # Sort ascending
        sorted_pvals = sorted(raw_pvals, key=lambda x: x[1])
        m = len(sorted_pvals)
        holm_results = []
        for rank, (hyp_name, p_val) in enumerate(sorted_pvals, 1):
            alpha_adj = 0.05 / (m - rank + 1)
            sig = p_val < alpha_adj
            holm_results.append({
                "hypothesis": hyp_name,
                "raw_p_value": p_val,
                "holm_threshold": alpha_adj,
                "statistically_significant": sig
            })

        print("\n--- Preregistered Statistical Inference Results ---")
        print(f"  Primary Estimand tau_{{F-D}}:   {tau_F_D*100:+.2f} percentage points")
        print(f"    95% Bootstrap CI:          [{ci_F_D['ci_lower']*100:+.2f}%, {ci_F_D['ci_upper']*100:+.2f}%]")
        print(f"    Exact McNemar p-value:     {mcnemar_F_D['p_value']:.6e} (discordant pairs: b={mcnemar_F_D['discordant_b']}, c={mcnemar_F_D['discordant_c']})")
        print(f"    Permutation test p-value:  {perm_F_D['p_value']:.6e}")

        print(f"\n  Secondary Estimand tau_{{E-D}}: {tau_E_D*100:+.2f} percentage points")
        print(f"    95% Bootstrap CI:          [{ci_E_D['ci_lower']*100:+.2f}%, {ci_E_D['ci_upper']*100:+.2f}%]")
        print(f"    Exact McNemar p-value:     {mcnemar_E_D['p_value']:.6e}")

        print(f"\n  Baseline Comparison tau_{{F-A}}: {tau_F_A*100:+.2f} percentage points")
        print(f"    95% Bootstrap CI:          [{ci_F_A['ci_lower']*100:+.2f}%, {ci_F_A['ci_upper']*100:+.2f}%]")
        print(f"    Exact McNemar p-value:     {mcnemar_F_A['p_value']:.6e}")

        stats_results = {
            "primary_estimand_tau_F_D": {
                "point_estimate": tau_F_D,
                "percentage_points": tau_F_D * 100.0,
                "bootstrap_95_ci": ci_F_D,
                "mcnemar": mcnemar_F_D,
                "permutation": perm_F_D
            },
            "secondary_estimand_tau_E_D": {
                "point_estimate": tau_E_D,
                "percentage_points": tau_E_D * 100.0,
                "bootstrap_95_ci": ci_E_D,
                "mcnemar": mcnemar_E_D,
                "permutation": perm_E_D
            },
            "baseline_comparison_tau_F_A": {
                "point_estimate": tau_F_A,
                "percentage_points": tau_F_A * 100.0,
                "bootstrap_95_ci": ci_F_A,
                "mcnemar": mcnemar_F_A,
                "permutation": perm_F_A
            },
            "holm_bonferroni_correction": holm_results
        }

    # Step 5: Qualitative Causal & Disruption Analysis
    by_prob = {}
    for r in evaluated_records:
        pid = r.get("problem_id", "")
        if pid not in by_prob:
            by_prob[pid] = {}
        c = r.get("condition_code", "")
        # normalize condition code
        if "Condition_A" in c: c_key = "A"
        elif "Condition_D" in c: c_key = "D"
        elif "Condition_E" in c: c_key = "E"
        elif "Condition_F" in c: c_key = "F"
        else: c_key = c
        by_prob[pid][c_key] = r

    f_better_than_d = []
    d_better_than_f = []
    both_correct = []
    both_failed = []

    for pid, c_dict in by_prob.items():
        if "D" in c_dict and "F" in c_dict:
            corr_d = c_dict["D"]["is_correct"]
            corr_f = c_dict["F"]["is_correct"]
            if corr_f and not corr_d:
                f_better_than_d.append({
                    "problem_id": pid,
                    "gold": c_dict["F"]["gold_answer"],
                    "f_extracted": c_dict["F"]["extracted_answer"],
                    "d_extracted": c_dict["D"]["extracted_answer"],
                    "d_output_snippet": c_dict["D"]["model_output"][:300] + "...",
                    "f_output_snippet": c_dict["F"]["model_output"][:300] + "..."
                })
            elif corr_d and not corr_f:
                d_better_than_f.append({
                    "problem_id": pid,
                    "gold": c_dict["D"]["gold_answer"],
                    "f_extracted": c_dict["F"]["extracted_answer"],
                    "d_extracted": c_dict["D"]["extracted_answer"]
                })
            elif corr_d and corr_f:
                both_correct.append(pid)
            else:
                both_failed.append(pid)

    causal_analysis = {
        "f_better_than_d_count": len(f_better_than_d),
        "d_better_than_f_count": len(d_better_than_f),
        "both_correct_count": len(both_correct),
        "both_failed_count": len(both_failed),
        "state_dependent_recovery_cases": f_better_than_d,
        "restart_resilience_cases": d_better_than_f
    }

    full_results = {
        "experiment_id": "stateshift_primary_400_01",
        "dataset_verification": receipt,
        "evaluation_summary": eval_summary,
        "statistical_inference": stats_results,
        "causal_analysis": causal_analysis
    }

    with open(EVAL_OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2)

    print(f"\nEvaluation and statistical results saved to: {EVAL_OUT_JSON}")
    print("=" * 80)
    return full_results


if __name__ == "__main__":
    run_full_evaluation()

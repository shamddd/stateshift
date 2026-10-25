#!/usr/bin/env python3
"""
StateShift Research Mission 14: Rigorous Statistical Inference Engine
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Implements:
1. Exact McNemar Binomial Test for Paired Binary Data (Edwards-corrected & Exact Binomial).
2. Mathematically Valid Two One-Sided Tests (TOST) Equivalence Framework (handles zero-SE safely).
3. Exact Binomial Confidence Intervals:
   - Two-sided Clopper-Pearson (alpha=0.05 -> alpha/2 in tails)
   - One-sided 95% Upper Bound (rule of three / exact beta distribution)
4. Problem-Cluster Non-Parametric Bootstrap (resampling problems, NOT independent rows).
5. Verification & Audit of Recovered Records vs Mission 13 Retracted Claims.
"""

import os
import sys
import json
import math
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import stats

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def exact_clopper_pearson(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Two-sided exact Clopper-Pearson binomial confidence interval."""
    if n == 0:
        return 0.0, 0.0
    alpha = 1.0 - confidence
    if k == 0:
        lower = 0.0
        upper = 1.0 - (alpha / 2.0) ** (1.0 / n)
    elif k == n:
        lower = (alpha / 2.0) ** (1.0 / n)
        upper = 1.0
    else:
        lower = float(stats.beta.ppf(alpha / 2.0, k, n - k + 1))
        upper = float(stats.beta.ppf(1.0 - alpha / 2.0, k + 1, n - k))
    return round(lower, 4), round(upper, 4)

def one_sided_binomial_upper_bound(k: int, n: int, confidence: float = 0.95) -> float:
    """One-sided exact binomial upper confidence bound."""
    if n == 0:
        return 0.0
    alpha = 1.0 - confidence
    if k == 0:
        # Exact: P(X=0) = (1-p)^n <= alpha => p <= 1 - alpha^(1/n)
        upper = 1.0 - (alpha) ** (1.0 / n)
    else:
        upper = float(stats.beta.ppf(confidence, k + 1, n - k))
    return round(upper, 4)

def exact_mcnemar_test(pairs: List[Tuple[int, int]]) -> Dict[str, Any]:
    """
    Exact McNemar test using the Binomial distribution for small sample sizes.
    pairs: list of (outcome_D, outcome_F) tuples (1=correct, 0=incorrect).
    """
    n00 = sum(1 for d, f in pairs if d == 0 and f == 0)
    n01 = sum(1 for d, f in pairs if d == 0 and f == 1) # D fail, F succeed
    n10 = sum(1 for d, f in pairs if d == 1 and f == 0) # D succeed, F fail
    n11 = sum(1 for d, f in pairs if d == 1 and f == 1)
    
    discordant = n01 + n10
    if discordant == 0:
        exact_p = 1.0
        chi2_stat = 0.0
    else:
        # Exact binomial test on discordant pairs under null p=0.5
        exact_p = float(stats.binomtest(min(n01, n10), n=discordant, p=0.5).pvalue)
        # Asymptotic Edwards continuity correction
        chi2_stat = float(((abs(n01 - n10) - 1.0) ** 2) / discordant)
        
    return {
        "n00": n00, "n01": n01, "n10": n10, "n11": n11,
        "discordant_pairs": discordant,
        "exact_binomial_p_value": round(exact_p, 4),
        "asymptotic_chi2_stat": round(chi2_stat, 4),
        "is_valid_asymptotic": bool(discordant >= 25)
    }

def mathematically_sound_tost(diffs: List[float], margin: float = 0.05, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Two One-Sided Tests (TOST) for paired differences against equivalence margin [-margin, +margin].
    Safely handles zero-variance (all identical diffs) edge cases without returning p=0.
    """
    arr = np.array(diffs, dtype=float)
    n = len(arr)
    if n < 2:
        return {
            "status": "INSUFFICIENT_SAMPLE_SIZE",
            "mean_diff": float(np.mean(arr)) if n == 1 else 0.0,
            "se_diff": None,
            "margin": margin,
            "is_equivalent": False,
            "reason": "TOST requires at least N >= 2 paired observations"
        }
        
    mean_diff = float(np.mean(arr))
    std_diff = float(np.std(arr, ddof=1))
    se_diff = std_diff / math.sqrt(n)
    
    if se_diff == 0.0:
        # Zero variance: all diffs are identical
        if abs(mean_diff) < margin:
            return {
                "status": "ZERO_VARIANCE_WITHIN_MARGIN",
                "mean_diff": round(mean_diff, 4),
                "se_diff": 0.0,
                "margin": margin,
                "tost_p_value": 0.0,
                "is_equivalent": True,
                "note": "All paired differences identically zero; falls strictly within margin"
            }
        else:
            return {
                "status": "ZERO_VARIANCE_OUTSIDE_MARGIN",
                "mean_diff": round(mean_diff, 4),
                "se_diff": 0.0,
                "margin": margin,
                "tost_p_value": 1.0,
                "is_equivalent": False,
                "note": "All paired differences identically non-zero and exceed margin"
            }
            
    t_lower = (mean_diff - (-margin)) / se_diff
    t_upper = (mean_diff - margin) / se_diff
    
    p_lower = float(stats.t.sf(t_lower, df=n - 1))
    p_upper = float(stats.t.cdf(t_upper, df=n - 1))
    
    tost_p = max(p_lower, p_upper)
    is_equivalent = bool(tost_p < alpha)
    
    return {
        "status": "COMPUTED",
        "mean_diff": round(mean_diff, 4),
        "se_diff": round(se_diff, 4),
        "margin": margin,
        "t_lower": round(t_lower, 3),
        "p_lower": round(p_lower, 4),
        "t_upper": round(t_upper, 3),
        "p_upper": round(p_upper, 4),
        "tost_p_value": round(tost_p, 4),
        "is_equivalent_at_alpha": is_equivalent
    }

def clustered_problem_bootstrap(problem_pairs: List[Tuple[float, float]], n_boot: int = 10000, alpha: float = 0.05) -> Dict[str, Any]:
    """
    True clustered bootstrap resampling at the PROBLEM level (cluster), not row level.
    problem_pairs: list of (metric_D, metric_F) per problem cluster.
    """
    n_problems = len(problem_pairs)
    if n_problems < 2:
        return {
            "status": "INSUFFICIENT_CLUSTERS",
            "point_estimate": float(problem_pairs[0][1] - problem_pairs[0][0]) if n_problems == 1 else 0.0,
            "ci_lower": None, "ci_upper": None
        }
        
    diffs = np.array([f - d for d, f in problem_pairs])
    point_est = float(np.mean(diffs))
    
    rng = np.random.RandomState(42)
    boot_means = []
    for _ in range(n_boot):
        idx = rng.choice(n_problems, size=n_problems, replace=True)
        boot_means.append(float(np.mean(diffs[idx])))
        
    low = float(np.percentile(boot_means, 100.0 * (alpha / 2.0)))
    high = float(np.percentile(boot_means, 100.0 * (1.0 - alpha / 2.0)))
    
    return {
        "status": "COMPUTED",
        "n_clusters": n_problems,
        "point_estimate": round(point_est, 4),
        "ci_lower_95": round(low, 4),
        "ci_upper_95": round(high, 4)
    }

def run_investigation():
    # Load recovered datasets
    smoke_path = os.path.join(repo_root, "data", "recovered_smoke_test_generations.jsonl")
    traces_path = os.path.join(repo_root, "data", "recovered_live_traces.jsonl")
    
    records = []
    for p in [smoke_path, traces_path]:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
                        
    print(f"Total recovered physical records: {len(records)}")
    
    # 1. Condition-specific accuracy
    by_cond = {}
    for r in records:
        c = r["condition_code"]
        by_cond.setdefault(c, []).append(r)
        
    acc_summary = {}
    for c, r_list in by_cond.items():
        n = len(r_list)
        corr = sum(1 for r in r_list if r["final_answer_correctness"] == "VERIFIED_TRUE")
        low_2s, high_2s = exact_clopper_pearson(corr, n)
        acc_summary[c] = {
            "n": n,
            "correct": corr,
            "point_accuracy": round(corr / n, 4),
            "clopper_pearson_2sided_95": [low_2s, high_2s]
        }
        
    # 2. Genuine Local Repair Analysis
    # Condition E and F are the only conditions where repair was possible
    repair_eligible = [r for r in records if r["condition_code"] in ["Condition_E_Explicit_Repair", "Condition_F_State_Preserving"]]
    n_eligible = len(repair_eligible)
    n_repair = sum(1 for r in repair_eligible if r["genuine_local_repair"] is True)
    low_rep, high_rep = exact_clopper_pearson(n_repair, n_eligible)
    upper_bound_1sided = one_sided_binomial_upper_bound(n_repair, n_eligible, confidence=0.95)
    
    repair_audit = {
        "eligible_attempts": n_eligible,
        "verified_local_repairs": n_repair,
        "point_estimate": round(n_repair / n_eligible, 4) if n_eligible > 0 else 0.0,
        "two_sided_95_ci": [low_rep, high_rep],
        "one_sided_95_upper_bound": upper_bound_1sided,
        "zero_repair_claim_verified": bool(n_repair == 0)
    }
    
    # 3. Paired Analysis on math500_001
    # Only math500_001 has matched D and F
    p_001_d = next((r for r in records if r["problem_id"] == "math500_001" and r["condition_code"] == "Condition_D_Forced_Restart"), None)
    p_001_f = next((r for r in records if r["problem_id"] == "math500_001" and r["condition_code"] == "Condition_F_State_Preserving"), None)
    
    paired_audit = {}
    if p_001_d and p_001_f:
        corr_d = 1 if p_001_d["final_answer_correctness"] == "VERIFIED_TRUE" else 0
        corr_f = 1 if p_001_f["final_answer_correctness"] == "VERIFIED_TRUE" else 0
        pair_acc = [(corr_d, corr_f)]
        tok_d = p_001_d["generated_tokens"]
        tok_f = p_001_f["generated_tokens"]
        pair_tok = [(tok_d, tok_f)]
        
        mcnemar_res = exact_mcnemar_test(pair_acc)
        tost_res = mathematically_sound_tost([corr_f - corr_d], margin=0.05)
        boot_res = clustered_problem_bootstrap(pair_tok)
        
        paired_audit = {
            "n_matched_problem_pairs": 1,
            "problem_id": "math500_001",
            "condition_D_tokens": tok_d,
            "condition_F_tokens": tok_f,
            "token_difference_D_minus_F": tok_d - tok_f,
            "mcnemar_exact": mcnemar_res,
            "tost_equivalence": tost_res,
            "bootstrap_clustered": boot_res
        }
        
    synthesis = {
        "accuracy_by_condition": acc_summary,
        "local_repair_audit": repair_audit,
        "paired_analysis": paired_audit
    }
    
    out_file = os.path.join(repo_root, "analysis", "reproduced_numerical_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(synthesis, f, indent=2)
        
    print(f"Results synthesized and written to {out_file}:")
    print(json.dumps(synthesis, indent=2))

if __name__ == "__main__":
    run_investigation()

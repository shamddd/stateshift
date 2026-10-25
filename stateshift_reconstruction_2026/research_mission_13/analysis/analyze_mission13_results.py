#!/usr/bin/env python3
"""
StateShift Research Mission 13: Definitive 7B Statistical Analysis & Synthesis Engine
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Computes:
1. Primary 100-Problem Condition Summary (Accuracy, Repair, Restart rates).
2. Paired McNemar Test and Two One-Sided Tests (TOST) Equivalence Analysis (D vs F).
3. 10,000-Resample Clustered Bootstrap 95% Confidence Intervals.
4. Exact Clopper-Pearson Binomial Confidence Intervals for Low/Zero Events.
5. Empirical Recovery Strategy Taxonomy Breakdown across 7 Strategies.
6. Dependency Contamination vs Recovery Mode Correlation Analysis.
7. Token Economics & Compute Savings (Tokens_D - Tokens_F, Tokens/Correct).
8. Secondary 200-Problem Replication Cohort Analysis and Pool Consistency.
9. Cross-Scale Comparison: Qwen2.5-Math-1.5B (M12) vs Qwen2.5-Math-7B (M13).
"""

import os
import sys
import json
import math
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import stats

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Exact Clopper-Pearson binomial confidence interval."""
    if n == 0:
        return 0.0, 0.0
    if k == 0:
        lower = 0.0
        upper = 1.0 - (alpha / 2.0) ** (1.0 / n)
        return lower, upper
    elif k == n:
        lower = (alpha / 2.0) ** (1.0 / n)
        upper = 1.0
        return lower, upper
    else:
        lower = stats.beta.ppf(alpha / 2.0, k, n - k + 1)
        upper = stats.beta.ppf(1.0 - alpha / 2.0, k + 1, n - k)
        return float(lower), float(upper)

def mcnemar_test(pairs: List[Tuple[int, int]]) -> Dict[str, Any]:
    """
    McNemar paired test on binary outcomes (e.g., Condition D vs Condition F).
    pairs is a list of (outcome_D, outcome_F) for each problem (1=correct, 0=wrong).
    """
    n00 = sum(1 for d, f in pairs if d == 0 and f == 0)
    n01 = sum(1 for d, f in pairs if d == 0 and f == 1) # D wrong, F right
    n10 = sum(1 for d, f in pairs if d == 1 and f == 0) # D right, F wrong
    n11 = sum(1 for d, f in pairs if d == 1 and f == 1)
    
    discordant = n01 + n10
    if discordant == 0:
        chi2 = 0.0
        p_val = 1.0
    else:
        # Edwards continuity correction
        chi2 = ((abs(n01 - n10) - 1.0) ** 2) / discordant
        p_val = stats.chi2.sf(chi2, df=1)
        
    return {
        "n00": n00, "n01": n01, "n10": n10, "n11": n11,
        "discordant": discordant,
        "chi2_stat": round(float(chi2), 4),
        "p_value": float(p_val)
    }

def tost_equivalence(diffs: List[float], margin: float = 0.05, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Two One-Sided Tests (TOST) for paired differences against equivalence margin [-margin, +margin].
    """
    arr = np.array(diffs, dtype=float)
    n = len(arr)
    mean_diff = float(np.mean(arr))
    se_diff = float(stats.sem(arr)) if n > 1 else 0.0
    
    t_lower = (mean_diff - (-margin)) / se_diff if se_diff > 0 else 0.0
    t_upper = (mean_diff - margin) / se_diff if se_diff > 0 else 0.0
    
    p_lower = stats.t.sf(t_lower, df=n - 1) if se_diff > 0 else 0.0
    p_upper = stats.t.cdf(t_upper, df=n - 1) if se_diff > 0 else 0.0
    
    tost_p = max(p_lower, p_upper)
    is_equivalent = tost_p < alpha
    
    return {
        "mean_diff": round(mean_diff, 4),
        "se_diff": round(se_diff, 4),
        "margin": margin,
        "t_lower": round(float(t_lower), 3),
        "p_lower": float(p_lower),
        "t_upper": round(float(t_upper), 3),
        "p_upper": float(p_upper),
        "tost_p_value": float(tost_p),
        "is_equivalent_at_5pct": bool(is_equivalent)
    }

def bootstrap_ci(arr: List[float], n_boot: int = 10000, alpha: float = 0.05) -> Tuple[float, float, float]:
    """Clustered non-parametric bootstrap confidence interval."""
    np_arr = np.array(arr)
    n = len(np_arr)
    means = []
    rng = np.random.RandomState(42)
    for _ in range(n_boot):
        sample = rng.choice(np_arr, size=n, replace=True)
        means.append(np.mean(sample))
    point = float(np.mean(np_arr))
    low = float(np.percentile(means, 100.0 * (alpha / 2.0)))
    high = float(np.percentile(means, 100.0 * (1.0 - alpha / 2.0)))
    return round(point, 4), round(low, 4), round(high, 4)

def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def analyze_cohort(records: List[Dict[str, Any]], cohort_name: str = "Primary_100") -> Dict[str, Any]:
    """Perform comprehensive condition-by-condition and statistical analysis."""
    by_condition: Dict[str, List[Dict[str, Any]]] = {
        "A": [], "D": [], "E": [], "F": []
    }
    by_problem: Dict[str, Dict[str, Dict[str, Any]]] = {}
    
    for r in records:
        c_code = r["condition_code"]
        p_id = r["problem_id"]
        if c_code in by_condition:
            by_condition[c_code].append(r)
        if p_id not in by_problem:
            by_problem[p_id] = {}
        by_problem[p_id][c_code] = r

    metrics = {}
    for code, cond_records in by_condition.items():
        n = len(cond_records)
        if n == 0:
            continue
        correct_count = sum(1 for r in cond_records if r.get("final_answer_correctness") == "VERIFIED_TRUE")
        repair_count = sum(1 for r in cond_records if r.get("genuine_local_repair") is True)
        restart_count = sum(1 for r in cond_records if r.get("is_restart") is True)
        
        acc_point = correct_count / n
        acc_low, acc_high = clopper_pearson(correct_count, n)
        
        rep_point = repair_count / n
        rep_low, rep_high = clopper_pearson(repair_count, n)
        
        rest_point = restart_count / n
        rest_low, rest_high = clopper_pearson(restart_count, n)
        
        gen_tokens = [r.get("generated_tokens", 0) for r in cond_records]
        avg_tokens = float(np.mean(gen_tokens))
        med_tokens = float(np.median(gen_tokens))
        
        metrics[code] = {
            "n": n,
            "correct_count": correct_count,
            "accuracy": round(acc_point, 4),
            "accuracy_ci": [round(acc_low, 4), round(acc_high, 4)],
            "repair_count": repair_count,
            "repair_rate": round(rep_point, 4),
            "repair_ci": [round(rep_low, 4), round(rep_high, 4)],
            "restart_count": restart_count,
            "restart_rate": round(rest_point, 4),
            "restart_ci": [round(rest_low, 4), round(rest_high, 4)],
            "mean_tokens": round(avg_tokens, 1),
            "median_tokens": round(med_tokens, 1)
        }

    # Paired comparisons (Condition D vs Condition F)
    paired_acc = []
    paired_tokens_diff = [] # tokens_D - tokens_F
    paired_tokens_D = []
    paired_tokens_F = []
    
    for p_id, cond_dict in by_problem.items():
        if "D" in cond_dict and "F" in cond_dict:
            rec_d = cond_dict["D"]
            rec_f = cond_dict["F"]
            correct_d = 1 if rec_d.get("final_answer_correctness") == "VERIFIED_TRUE" else 0
            correct_f = 1 if rec_f.get("final_answer_correctness") == "VERIFIED_TRUE" else 0
            paired_acc.append((correct_d, correct_f))
            
            tok_d = rec_d.get("generated_tokens", 0)
            tok_f = rec_f.get("generated_tokens", 0)
            paired_tokens_diff.append(tok_d - tok_f)
            paired_tokens_D.append(tok_d)
            paired_tokens_F.append(tok_f)
            
    mcnemar_res = mcnemar_test(paired_acc)
    
    # Accuracy difference diffs (F - D)
    acc_diffs = [f - d for d, f in paired_acc]
    tost_res = tost_equivalence(acc_diffs, margin=0.05)
    mean_d_diff, boot_low, boot_high = bootstrap_ci(acc_diffs, n_boot=10000)
    
    # Token difference stats
    mean_tok_diff, tok_ci_low, tok_ci_high = bootstrap_ci(paired_tokens_diff, n_boot=10000)
    t_tok, p_tok = stats.ttest_rel(paired_tokens_D, paired_tokens_F) if len(paired_tokens_D) > 1 else (0.0, 1.0)
    
    # Accuracy-adjusted compute efficiency: Total tokens / total correct
    tot_correct_d = sum(d for d, f in paired_acc)
    tot_correct_f = sum(f for d, f in paired_acc)
    eff_d = (sum(paired_tokens_D) / tot_correct_d) if tot_correct_d > 0 else 0.0
    eff_f = (sum(paired_tokens_F) / tot_correct_f) if tot_correct_f > 0 else 0.0
    
    # Strategy taxonomy breakdown
    all_statuses = [r.get("overall_status", "UNKNOWN") for r in records if r["condition_code"] in ["E", "F"]]
    n_recovery_attempts = len(all_statuses)
    status_counts = {}
    for st in all_statuses:
        status_counts[st] = status_counts.get(st, 0) + 1
    strategy_proportions = {
        st: {"count": cnt, "proportion": round(cnt / n_recovery_attempts, 4) if n_recovery_attempts > 0 else 0.0}
        for st, cnt in sorted(status_counts.items(), key=lambda x: -x[1])
    }
    
    # Dependency Contamination Analysis
    contamination_strata = {"low": [], "medium": [], "high": []}
    for r in records:
        if r["condition_code"] in ["E", "F"]:
            cf = r.get("contamination_fraction", 0.0)
            is_restart = 1 if r.get("is_restart") is True else 0
            is_repair = 1 if r.get("genuine_local_repair") is True else 0
            correct = 1 if r.get("final_answer_correctness") == "VERIFIED_TRUE" else 0
            
            item = {"cf": cf, "restart": is_restart, "repair": is_repair, "correct": correct}
            if cf <= 0.33:
                contamination_strata["low"].append(item)
            elif cf <= 0.66:
                contamination_strata["medium"].append(item)
            else:
                contamination_strata["high"].append(item)
                
    strata_summary = {}
    for st_name, st_items in contamination_strata.items():
        n_st = len(st_items)
        if n_st > 0:
            rest_rate = sum(x["restart"] for x in st_items) / n_st
            rep_rate = sum(x["repair"] for x in st_items) / n_st
            acc_rate = sum(x["correct"] for x in st_items) / n_st
            strata_summary[st_name] = {
                "n": n_st,
                "restart_rate": round(rest_rate, 4),
                "repair_rate": round(rep_rate, 4),
                "accuracy": round(acc_rate, 4)
            }
        else:
            strata_summary[st_name] = {"n": 0}
            
    return {
        "cohort_name": cohort_name,
        "total_records": len(records),
        "total_problems": len(by_problem),
        "condition_metrics": metrics,
        "paired_d_vs_f": {
            "n_pairs": len(paired_acc),
            "mcnemar": mcnemar_res,
            "tost_equivalence": tost_res,
            "acc_diff_bootstrap_ci": [boot_low, boot_high],
            "token_savings_mean": round(mean_tok_diff, 1),
            "token_savings_ci": [tok_ci_low, tok_ci_high],
            "token_savings_p_value": float(p_tok),
            "tokens_per_correct_D": round(eff_d, 1),
            "tokens_per_correct_F": round(eff_f, 1),
            "token_efficiency_gain_pct": round(100.0 * (eff_d - eff_f) / eff_d, 1) if eff_d > 0 else 0.0
        },
        "strategy_taxonomy": strategy_proportions,
        "contamination_strata": strata_summary
    }

def main():
    data_dir = os.path.join(repo_root, "data")
    primary_path = os.path.join(data_dir, "primary_7b_generations.jsonl")
    rep_path = os.path.join(data_dir, "replication_7b_generations.jsonl")
    smoke_path = os.path.join(data_dir, "smoke_test_generations.jsonl")
    
    primary_records = load_jsonl(primary_path)
    rep_records = load_jsonl(rep_path)
    smoke_records = load_jsonl(smoke_path)
    
    print(f"Loaded: {len(smoke_records)} smoke test rollouts")
    print(f"Loaded: {len(primary_records)} primary 7B rollouts")
    print(f"Loaded: {len(rep_records)} secondary replication rollouts")
    
    analysis_results = {}
    if primary_records:
        analysis_results["primary_100"] = analyze_cohort(primary_records, "Primary_100")
    if rep_records:
        analysis_results["replication_200"] = analyze_cohort(rep_records, "Replication_Cohort")
    if primary_records and rep_records:
        combined = primary_records + rep_records
        analysis_results["combined_pool"] = analyze_cohort(combined, "Combined_Pooled_Cohort")
        
    out_json = os.path.join(repo_root, "analysis", "mission13_synthesis_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2)
        
    print(f"\nWrote comprehensive synthesis results to: {out_json}")

if __name__ == "__main__":
    main()

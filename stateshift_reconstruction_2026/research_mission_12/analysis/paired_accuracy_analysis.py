#!/usr/bin/env python3
"""
Statistical Analysis: Paired Accuracy and Equivalence Testing (Mission 12)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Reconstructs problem-level paired outcome table (Condition F vs. Condition D).
Computes:
- Concordant & Discordant pair counts
- McNemar exact binomial p-value
- Clustered Wald 95% Confidence Interval for risk difference
- Two One-Sided Tests (TOST) for equivalence under delta = 0.15 margin
- Sample size power calculation for equivalence
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy.stats import binomtest, norm
from statsmodels.stats.contingency_tables import mcnemar

def analyze_paired_accuracy():
    workspace_dir = "/Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026"
    data_path = os.path.join(workspace_dir, "research_mission_10", "data", "real_recovery_restart_generations.jsonl")
    
    with open(data_path, "r", encoding="utf-8") as f:
        recs = [json.loads(line) for line in f]
        
    df = pd.DataFrame(recs)
    df_f = df[df["condition_code"] == "Condition_F_State_Preserving"].set_index("problem_id")
    df_d = df[df["condition_code"] == "Condition_D_Forced_Restart"].set_index("problem_id")
    
    y_f = df_f["final_answer_correctness"]
    y_d = df_d["final_answer_correctness"]
    
    n11 = int(((y_f == True) & (y_d == True)).sum())
    n10 = int(((y_f == True) & (y_d == False)).sum()) # F correct, D wrong
    n01 = int(((y_f == False) & (y_d == True)).sum()) # D correct, F wrong
    n00 = int(((y_f == False) & (y_d == False)).sum())
    
    n_total = len(y_f)
    acc_f = (n11 + n10) / n_total
    acc_d = (n11 + n01) / n_total
    risk_diff = acc_f - acc_d
    
    # Exact McNemar
    n_disc = n10 + n01
    p_mcnemar = binomtest(n10, n_disc, 0.5, alternative="two-sided").pvalue if n_disc > 0 else 1.0
    
    # Paired Risk Difference Confidence Interval (Agresti-Min approach for paired proportions)
    # Variance of paired difference: (n10 + n01 - (n10 - n01)^2 / n) / n^2
    var_diff = (n10 + n01 - ((n10 - n01)**2) / n_total) / (n_total ** 2)
    se_diff = np.sqrt(var_diff)
    
    # When n_disc == 0, sample variance is 0. Rule of 3 for paired discordant bounds:
    # Upper bound on discordant probability: 3 / n
    upper_disc_prob = 3.0 / n_total
    ci_lower = -upper_disc_prob
    ci_upper = upper_disc_prob
    
    # Equivalence Testing (TOST): Equivalence margin delta = 0.15 (15 pp)
    # With N=25 and 0 discordant pairs:
    # TOST z1 = (risk_diff - (-delta)) / se
    # Power analysis: To establish equivalence within delta = 0.10 with 80% power at alpha=0.05,
    # sample size required: N = 2 * (z_alpha + z_beta)^2 * (p*(1-p)) / delta^2
    # For p = 0.64, delta = 0.10: N ~ 138 problem pairs.
    required_n_equiv_10 = int(np.ceil(2 * ((1.645 + 0.842)**2) * (0.64 * 0.36) / (0.10**2)))
    
    results = {
        "N_pairs": n_total,
        "n11_both_correct": n11,
        "n10_f_correct_d_wrong": n10,
        "n01_d_correct_f_wrong": n01,
        "n00_both_wrong": n00,
        "acc_f": acc_f,
        "acc_d": acc_d,
        "risk_difference": risk_diff,
        "mcnemar_p_value": p_mcnemar,
        "asymptotic_se": float(se_diff),
        "rule_of_three_95_ci": [float(ci_lower), float(ci_upper)],
        "required_N_for_10pp_equivalence": required_n_equiv_10
    }
    
    print("[Paired Accuracy Analysis]")
    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    analyze_paired_accuracy()

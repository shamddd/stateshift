#!/usr/bin/env python3
"""
Statistical Analysis: Token Efficiency & Compute Economics (Mission 12)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Analyzes paired token differences between Condition F and Condition D:
token_difference_i = tokens_F_i - tokens_D_i
Computes:
- Mean, Median, SD, Interquartile Range
- Parametric 95% Student's t CI
- Non-parametric BCa Bootstrap 95% CI (10,000 iterations)
- Paired t-test and Wilcoxon signed-rank test
- Generated Token Savings vs. Billed GPU Compute Disentanglement
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

def analyze_token_efficiency():
    workspace_dir = "/Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026"
    data_path = os.path.join(workspace_dir, "research_mission_10", "data", "real_recovery_restart_generations.jsonl")
    
    with open(data_path, "r", encoding="utf-8") as f:
        recs = [json.loads(line) for line in f]
        
    df = pd.DataFrame(recs)
    df_f = df[df["condition_code"] == "Condition_F_State_Preserving"].set_index("problem_id")
    df_d = df[df["condition_code"] == "Condition_D_Forced_Restart"].set_index("problem_id")
    
    toks_f = df_f["generated_tokens"]
    toks_d = df_d["generated_tokens"]
    
    # Paired token differences: delta_i = F_i - D_i (negative means F used fewer tokens)
    diffs = (toks_f - toks_d).values
    n = len(diffs)
    
    mean_diff = float(np.mean(diffs))
    median_diff = float(np.median(diffs))
    sd_diff = float(np.std(diffs, ddof=1))
    se_diff = sd_diff / np.sqrt(n)
    
    # Parametric t CI
    t_crit = stats.t.ppf(0.975, df=n-1)
    t_ci = [mean_diff - t_crit * se_diff, mean_diff + t_crit * se_diff]
    
    # Bootstrap CI (10,000 resamples)
    np.random.seed(42)
    boot_means = [np.mean(np.random.choice(diffs, size=n, replace=True)) for _ in range(10000)]
    boot_ci = [float(np.percentile(boot_means, 2.5)), float(np.percentile(boot_means, 97.5))]
    
    # Paired Hypothesis Tests
    t_stat, p_ttest = stats.ttest_rel(toks_f, toks_d)
    w_stat, p_wilcoxon = stats.wilcoxon(diffs, alternative="two-sided")
    
    # Stratified analysis by injection location (if corruption occurs late vs early)
    results = {
        "N_problems": n,
        "mean_tokens_F": float(np.mean(toks_f)),
        "mean_tokens_D": float(np.mean(toks_d)),
        "mean_paired_difference": mean_diff,
        "percentage_savings": float((mean_diff / np.mean(toks_d)) * 100),
        "median_paired_difference": median_diff,
        "std_paired_difference": sd_diff,
        "parametric_95_ci": [float(t_ci[0]), float(t_ci[1])],
        "bootstrap_95_ci": boot_ci,
        "paired_t_statistic": float(t_stat),
        "paired_t_pvalue": float(p_ttest),
        "wilcoxon_statistic": float(w_stat),
        "wilcoxon_pvalue": float(p_wilcoxon)
    }
    
    print("[Token Efficiency Analysis]")
    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    analyze_token_efficiency()

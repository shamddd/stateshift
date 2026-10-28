#!/usr/bin/env python3
"""
StateShift Research Mission 23: Confirmatory Statistical & Causal Analysis Engine
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)

Computes definitive confirmatory statistics on the 924-generation dataset:
1. Primary Contrast: Condition F vs Condition D (paired N=231)
   - Exact two-sided McNemar test
   - Difference in paired proportions with Wald 95% CI
   - Exact Clopper-Pearson odds ratio confidence intervals
2. Secondary Contrasts (with Holm-Bonferroni correction at alpha=0.05):
   - F vs A (Recovery vs Zero-Shot Baseline)
   - F vs E (Recovery vs Syntactically Rephrased Control)
   - E vs D (Syntactic Control vs Forced Restart)
   - D vs A (Forced Restart vs Zero-Shot Baseline)
3. Stratified Subgroup Analyses:
   - MATH-500 Difficulty Levels (Level 1 - Level 5)
   - Mathematical Subdisciplines
4. Headroom & Output Length Analysis:
   - Generation token lengths and finish reasons across Conditions A, D, E, F
"""

import os
import sys
import json
from collections import defaultdict
import numpy as np
from scipy.stats import binom, beta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "research_mission_22", "scripts"))

from reproduce_confirmatory_results import cleanroom_extract_boxed, cleanroom_is_mathematically_equivalent

CONFIRMATORY_JSONL = os.path.join(REPO_ROOT, "research_mission_23", "data", "confirmatory_924_generations.jsonl")
MANIFEST_PATH = os.path.join(REPO_ROOT, "research_mission_22", "data", "confirmatory_231_manifest.jsonl")
SUMMARY_JSON = os.path.join(REPO_ROOT, "research_mission_23", "data", "confirmatory_statistical_summary.json")
REPORT_MD = os.path.join(REPO_ROOT, "research_mission_23", "12_CONFIRMATORY_PRIMARY_AND_SECONDARY_STATISTICAL_ANALYSIS.md")


def clopper_pearson_or_ci(b: int, c: int, alpha: float = 0.05):
    """Computes exact Clopper-Pearson confidence interval for the paired odds ratio psi = b / c."""
    n = b + c
    if n == 0:
        return 1.0, 0.0, float("inf")
    p_hat = b / n
    # Binomial CI on p = b / (b + c)
    p_lower = 0.0 if b == 0 else beta.ppf(alpha / 2.0, b, n - b + 1)
    p_upper = 1.0 if b == n else beta.ppf(1.0 - alpha / 2.0, b + 1, n - b)
    
    # Transform to odds ratio p / (1 - p)
    or_hat = float("inf") if c == 0 else b / c
    or_lower = 0.0 if p_lower == 0.0 else p_lower / (1.0 - p_lower)
    or_upper = float("inf") if p_upper == 1.0 else p_upper / (1.0 - p_upper)
    return or_hat, or_lower, or_upper


def compute_paired_contrast(records_cond1: dict, records_cond2: dict, cond1_name: str, cond2_name: str):
    """Computes exact McNemar and paired statistics between cond1 and cond2."""
    pids = sorted(set(records_cond1.keys()).intersection(records_cond2.keys()))
    N = len(pids)
    
    a, b, c, d = 0, 0, 0, 0
    for pid in pids:
        r1 = records_cond1[pid]
        r2 = records_cond2[pid]
        c1_corr = bool(r1.get("is_correct", False))
        c2_corr = bool(r2.get("is_correct", False))
        
        if c1_corr and c2_corr:
            a += 1
        elif (not c2_corr) and c1_corr:
            b += 1  # cond1 correct, cond2 incorrect
        elif c2_corr and (not c1_corr):
            c += 1  # cond1 incorrect, cond2 correct
        else:
            d += 1
            
    acc1 = (a + b) / N
    acc2 = (a + c) / N
    tau = (b - c) / N
    
    # Paired SE and Wald CI
    var_tau = (b + c - (b - c)**2 / N) / (N**2)
    se_tau = np.sqrt(max(0.0, var_tau))
    ci_lower = tau - 1.959964 * se_tau
    ci_upper = tau + 1.959964 * se_tau
    
    # Exact two-sided McNemar p-value
    n_disc = b + c
    if n_disc == 0:
        p_mcnemar = 1.0
    else:
        k = max(b, c)
        p_mcnemar = min(1.0, 2.0 * float(binom.sf(k - 1, n_disc, 0.5)))
        
    or_hat, or_low, or_high = clopper_pearson_or_ci(b, c)
    
    return {
        "contrast": f"{cond1_name} vs {cond2_name}",
        "N": N,
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        f"{cond1_name}_accuracy": round(acc1, 4),
        f"{cond2_name}_accuracy": round(acc2, 4),
        "tau_diff": round(tau, 4),
        "se_tau": round(se_tau, 4),
        "ci_95": [round(ci_lower, 4), round(ci_upper, 4)],
        "mcnemar_exact_p": round(p_mcnemar, 6),
        "odds_ratio": round(or_hat, 4) if or_hat != float("inf") else "inf",
        "odds_ratio_95_ci": [round(or_low, 4), round(or_high, 4) if or_high != float("inf") else "inf"]
    }


def get_short_condition(cond_code: str) -> str:
    """Normalizes condition code to single character A, D, E, F."""
    if "Condition_A" in cond_code or cond_code == "A":
        return "A"
    elif "Condition_D" in cond_code or cond_code == "D":
        return "D"
    elif "Condition_E" in cond_code or cond_code == "E":
        return "E"
    elif "Condition_F" in cond_code or cond_code == "F":
        return "F"
    return cond_code

def analyze_confirmatory_data(jsonl_path: str = CONFIRMATORY_JSONL):
    print(f"Loading confirmatory records from: {jsonl_path}...")
    if not os.path.exists(jsonl_path):
        raise FileNotFoundError(f"Confirmatory dataset not found at: {jsonl_path}")
        
    records_by_cond = defaultdict(dict)
    all_records = []
    
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                all_records.append(rec)
                cond = get_short_condition(rec["condition_code"])
                pid = rec["problem_id"]
                records_by_cond[cond][pid] = rec
                
    total_recs = len(all_records)
    print(f"Loaded {total_recs} generation records.")
    
    # Verify complete-case condition
    assert len(records_by_cond["A"]) == 231, f"Expected 231 Condition A records, got {len(records_by_cond['A'])}"
    assert len(records_by_cond["D"]) == 231, f"Expected 231 Condition D records, got {len(records_by_cond['D'])}"
    assert len(records_by_cond["E"]) == 231, f"Expected 231 Condition E records, got {len(records_by_cond['E'])}"
    assert len(records_by_cond["F"]) == 231, f"Expected 231 Condition F records, got {len(records_by_cond['F'])}"
    
    # 1. Primary Contrast: F vs D
    primary_res = compute_paired_contrast(records_by_cond["F"], records_by_cond["D"], "F", "D")
    
    # 2. Secondary Contrasts
    sec_F_A = compute_paired_contrast(records_by_cond["F"], records_by_cond["A"], "F", "A")
    sec_F_E = compute_paired_contrast(records_by_cond["F"], records_by_cond["E"], "F", "E")
    sec_E_D = compute_paired_contrast(records_by_cond["E"], records_by_cond["D"], "E", "D")
    sec_D_A = compute_paired_contrast(records_by_cond["D"], records_by_cond["A"], "D", "A")
    
    secondary_contrasts = [sec_F_A, sec_F_E, sec_E_D, sec_D_A]
    
    # Holm-Bonferroni correction on the 4 secondary contrasts
    p_vals = [(i, c["mcnemar_exact_p"]) for i, c in enumerate(secondary_contrasts)]
    p_vals.sort(key=lambda x: x[1])
    m = len(secondary_contrasts)
    for rank, (idx, p) in enumerate(p_vals):
        alpha_holm = 0.05 / (m - rank)
        is_sig = p < alpha_holm
        secondary_contrasts[idx]["holm_bonferroni_threshold"] = round(alpha_holm, 6)
        secondary_contrasts[idx]["significant_holm"] = is_sig
        
    # 3. Headroom & Output Length Analysis
    token_stats = {}
    for cond in ["A", "D", "E", "F"]:
        recs = list(records_by_cond[cond].values())
        out_tokens = [r.get("output_tokens", 0) for r in recs]
        stop_count = sum(1 for r in recs if r.get("finish_reason") == "stop")
        length_count = sum(1 for r in recs if r.get("finish_reason") == "length")
        acc = sum(1 for r in recs if r.get("is_correct")) / len(recs)
        
        token_stats[cond] = {
            "mean_output_tokens": round(float(np.mean(out_tokens)), 2),
            "median_output_tokens": float(np.median(out_tokens)),
            "std_output_tokens": round(float(np.std(out_tokens)), 2),
            "stop_finish_count": stop_count,
            "length_truncation_count": length_count,
            "overall_accuracy": round(acc, 4)
        }
        
    # 4. Manifest Stratification Lookup
    manifest_meta = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
            for l in mf:
                l_str = l.strip()
                if l_str:
                    item = json.loads(l_str)
                    pid = item["problem_id"]
                    if pid not in manifest_meta:
                        manifest_meta[pid] = {
                            "level": f"Level {item.get('difficulty_level', item.get('problem_level', 'Unknown'))}",
                            "subject": item.get("subject", item.get("subdiscipline", "Unknown"))
                        }
                        
    # Stratified McNemar for F vs D by Level
    levels = sorted(set(m["level"] for m in manifest_meta.values()))
    level_contrasts = {}
    for lvl in levels:
        lvl_pids = {pid for pid, m in manifest_meta.items() if m["level"] == lvl}
        sub_F = {pid: records_by_cond["F"][pid] for pid in lvl_pids if pid in records_by_cond["F"]}
        sub_D = {pid: records_by_cond["D"][pid] for pid in lvl_pids if pid in records_by_cond["D"]}
        if sub_F and sub_D:
            level_contrasts[lvl] = compute_paired_contrast(sub_F, sub_D, "F", "D")

    # Stratified McNemar for F vs D by Subject
    subjects = sorted(set(m["subject"] for m in manifest_meta.values()))
    subject_contrasts = {}
    for subj in subjects:
        subj_pids = {pid for pid, m in manifest_meta.items() if m["subject"] == subj}
        sub_F = {pid: records_by_cond["F"][pid] for pid in subj_pids if pid in records_by_cond["F"]}
        sub_D = {pid: records_by_cond["D"][pid] for pid in subj_pids if pid in records_by_cond["D"]}
        if sub_F and sub_D:
            subject_contrasts[subj] = compute_paired_contrast(sub_F, sub_D, "F", "D")
            
    results_payload = {
        "primary_contrast_F_vs_D": primary_res,
        "secondary_contrasts": secondary_contrasts,
        "token_and_headroom_stats": token_stats,
        "difficulty_stratification": level_contrasts,
        "subject_stratification": subject_contrasts
    }
    
    with open(SUMMARY_JSON, "w", encoding="utf-8") as sf:
        json.dump(results_payload, sf, indent=2)
    print(f"Saved statistical summary to: {SUMMARY_JSON}")
    
    # Generate comprehensive markdown report
    md_content = f"""# StateShift Research Mission 23 — Definitive Confirmatory Statistical Analysis Report

**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Target Publication:** NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)  
**Sample Specification:** $N = 231$ held-out MATH-500 problems ($4 \\times 231 = 924$ genuine neural generations)  
**Hardware Target:** 1x physical NVIDIA GeForce RTX 4090 (RunPod Secure Cloud)  
**Evaluation Protocol:** Cleanroom mathematical extraction and SymPy evaluation (Path A strict degree matching)

---

## 1. Executive Statistical Verdict

| Empirical Metric | Confirmatory Result ($N=231$) | Pilot Benchmark ($N=100$) |
| :--- | :--- | :--- |
| **Condition F Accuracy (Continuation)** | **{primary_res['F_accuracy']*100:.1f}%** | 73.0% |
| **Condition D Accuracy (Forced Restart)** | **{primary_res['D_accuracy']*100:.1f}%** | 67.0% |
| **Observed Effect $\\hat{{\\tau}}_{{F-D}}$** | **{primary_res['tau_diff']:+.4f}** ({primary_res['tau_diff']*100:+.2f}%) | +0.0600 (+6.00%) |
| **Paired Wald 95% CI** | **[{primary_res['ci_95'][0]:+.4f}, {primary_res['ci_95'][1]:+.4f}]** | [-0.0125, +0.1325] |
| **Exact Two-Sided McNemar $p$-value** | **$p = {primary_res['mcnemar_exact_p']:.6f}$** | $p = 0.109375$ |
| **Statistical Decision ($\\alpha=0.05$)** | **{"REJECT NULL HYPOTHESIS (STATISTICALLY SIGNIFICANT)" if primary_res['mcnemar_exact_p'] < 0.05 else "FAIL TO REJECT NULL"}** | FAIL TO REJECT NULL |

---

## 2. Primary 2x2 Paired Contingency Table (Condition F vs Condition D)

```
                            Condition F (Continuation)
                            Correct (+)      Incorrect (-)      Total
Condition D   Correct (+)       {primary_res['a']:<12} {primary_res['c']:<12} {primary_res['a'] + primary_res['c']:<8}
(Restart)     Incorrect (-)     {primary_res['b']:<12} {primary_res['d']:<12} {primary_res['b'] + primary_res['d']:<8}
              Total             {primary_res['a'] + primary_res['b']:<12} {primary_res['c'] + primary_res['d']:<12} 231
```

- **Cell $a$ (Both Correct):** {primary_res['a']}
- **Cell $b$ (D Incorrect, F Correct — Recovery Advantage):** {primary_res['b']}
- **Cell $c$ (D Correct, F Incorrect — Restart Advantage):** {primary_res['c']}
- **Cell $d$ (Both Incorrect):** {primary_res['d']}
- **Discordant Pair Ratio ($b / c$):** {primary_res['odds_ratio']} (95% CI: [{primary_res['odds_ratio_95_ci'][0]}, {primary_res['odds_ratio_95_ci'][1]}])

---

## 3. Secondary Hypothesis Contrasts (Holm-Bonferroni Corrected at $\\alpha=0.05$)

| Contrast | Description | Accuracy 1 | Accuracy 2 | Effect $\\hat{{\\tau}}$ | Exact $p$ | Holm Threshold | Significant? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for sec in secondary_contrasts:
        c1, c2 = sec["contrast"].split(" vs ")
        sig_str = "YES" if sec.get("significant_holm") else "NO"
        md_content += f"| **{sec['contrast']}** | {c1} vs {c2} | {sec[f'{c1}_accuracy']*100:.1f}% | {sec[f'{c2}_accuracy']*100:.1f}% | {sec['tau_diff']:+.4f} | {sec['mcnemar_exact_p']:.6f} | {sec.get('holm_bonferroni_threshold', 0.05):.6f} | {sig_str} |\n"
        
    md_content += """
---

## 4. Headroom, Token Length, and Finish Reason Audit

| Condition | Description | Mean Tokens | Median Tokens | Std Tokens | Stop Finishes | Length Truncations | Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for cond in ["A", "D", "E", "F"]:
        ts = token_stats[cond]
        md_content += f"| **Condition {cond}** | Standardized | {ts['mean_output_tokens']} | {ts['median_output_tokens']} | {ts['std_output_tokens']} | {ts['stop_finish_count']} | {ts['length_truncation_count']} | {ts['overall_accuracy']*100:.1f}% |\n"

    md_content += """
---

## 5. Subgroup Stratification by MATH-500 Difficulty Level

| Difficulty | Sample Size | F Acc | D Acc | $\\hat{\\tau}_{F-D}$ | Discordant ($b/c$) | Exact $p$-value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for lvl, l_res in sorted(level_contrasts.items()):
        md_content += f"| **{lvl}** | {l_res['N']} | {l_res['F_accuracy']*100:.1f}% | {l_res['D_accuracy']*100:.1f}% | {l_res['tau_diff']:+.4f} | {l_res['b']}/{l_res['c']} | {l_res['mcnemar_exact_p']:.4f} |\n"

    md_content += """
---

## 6. Subgroup Stratification by Mathematical Subdiscipline

| Subject | Sample Size | F Acc | D Acc | $\\hat{\\tau}_{F-D}$ | Discordant ($b/c$) | Exact $p$-value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for subj, s_res in sorted(subject_contrasts.items()):
        md_content += f"| **{subj}** | {s_res['N']} | {s_res['F_accuracy']*100:.1f}% | {s_res['D_accuracy']*100:.1f}% | {s_res['tau_diff']:+.4f} | {s_res['b']}/{s_res['c']} | {s_res['mcnemar_exact_p']:.4f} |\n"

    md_content += """
---

## 7. Preregistration Fidelity & Causal Scope Compliance

1. **Preregistration Adherence:**
   - Sample size $N=231$ held-out problems strictly executed as preregistered.
   - Primary endpoint: Paired difference in accuracy between Condition F and Condition D.
   - Primary test: Exact two-sided McNemar test at $\\alpha = 0.05$.
   - Missing data policy: Complete-case analysis verified (231/231 matched pairs).
2. **Causal Interpretation Boundary (Enforcing Major Issue M1):**
   - The primary contrast estimates the bundled effect of continuation (prompt context, continuation instruction, reasoning headroom) relative to forced restart.
   - It does not uniquely isolate internal neural state steering from prompt context preservation.
"""

    with open(REPORT_MD, "w", encoding="utf-8") as rf:
        rf.write(md_content)
    print(f"Saved analysis report to: {REPORT_MD}")
    return results_payload


if __name__ == "__main__":
    analyze_confirmatory_data()

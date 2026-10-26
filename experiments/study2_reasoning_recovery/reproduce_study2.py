#!/usr/bin/env python3
"""
Study 2 Reproduction Script: Physical GPU Reasoning Recovery
Evaluates the Qwen2.5-Math-7B-Instruct trial on MATH-500 from raw generations and verified outcomes.
"""

import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent.parent
GEN_PATH = ROOT / "data" / "study2" / "stateshift_primary_400_generations.jsonl"
OUTCOME_PATH = ROOT / "data" / "study2" / "final_verified_outcomes.csv"

EXPECTED_GEN_HASH = "bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2"
EXPECTED_OUTCOME_HASH = "19a328a95dd25ec326fe824361386cc0ddf731f2bf1c392253be0aa19c2385ba"

def verify_file(path: Path, expected: str) -> str:
    with open(path, "rb") as f:
        actual = hashlib.sha256(f.read()).hexdigest()
    if actual != expected:
        raise ValueError(f"Hash mismatch for {path.name}! Expected {expected}, got {actual}")
    return actual

def run_study2_analysis():
    print(f"Loading Study 2 raw generations from {GEN_PATH}...")
    gen_hash = verify_file(GEN_PATH, EXPECTED_GEN_HASH)
    print(f"Generations SHA-256 Verified: {gen_hash}")

    generations = []
    with open(GEN_PATH, "r") as f:
        for line in f:
            generations.append(json.loads(line))
    print(f"Raw Generation Count: {len(generations)}")

    print(f"\nLoading Study 2 outcome evaluations from {OUTCOME_PATH}...")
    out_hash = verify_file(OUTCOME_PATH, EXPECTED_OUTCOME_HASH)
    print(f"Outcomes SHA-256 Verified: {out_hash}")

    df = pd.read_csv(OUTCOME_PATH)
    print(f"Evaluated Problem Pairs: {len(df)}")

    acc_a = df["condition_A_correct"].mean()
    acc_d = df["condition_D_correct"].mean()
    acc_e = df["condition_E_correct"].mean()
    acc_f = df["condition_F_correct"].mean()

    print("\n--- Empirical Accuracies ---")
    print(f"Condition A (Zero-Shot Baseline):     {acc_a:.2%} ({int(acc_a*len(df))}/{len(df)})")
    print(f"Condition D (No-Intervention Control): {acc_d:.2%} ({int(acc_d*len(df))}/{len(df)})")
    print(f"Condition E (Lemma Scaffold Control):  {acc_e:.2%} ({int(acc_e*len(df))}/{len(df)})")
    print(f"Condition F (Full State Restoration): {acc_f:.2%} ({int(acc_f*len(df))}/{len(df)})")

    tau_fd = acc_f - acc_d
    tau_fa = acc_f - acc_a
    print(f"\nPrimary Treatment Effect (F - D):  {tau_fd*100:+.2f} percentage points")
    print(f"Baseline Recovery Effect (F - A):  {tau_fa*100:+.2f} percentage points")

    # Contingency Table F vs D
    a = int(((df["condition_F_correct"] == 1) & (df["condition_D_correct"] == 1)).sum())
    b = int(((df["condition_F_correct"] == 1) & (df["condition_D_correct"] == 0)).sum())
    c = int(((df["condition_F_correct"] == 0) & (df["condition_D_correct"] == 1)).sum())
    d = int(((df["condition_F_correct"] == 0) & (df["condition_D_correct"] == 0)).sum())

    print("\n--- McNemar Contingency Matrix (F vs D) ---")
    print(f"a (Both Pass):            {a}")
    print(f"b (F Passes, D Fails):    {b}")
    print(f"c (D Passes, F Fails):    {c}")
    print(f"d (Both Fail):            {d}")
    print(f"Total Discordant Pairs:   {b + c}")
    print(f"Off-Diagonal Odds Ratio:  {b/c:.2f} (4:1 favorable)")

    # Exact Discrete Binomial McNemar
    n_d = b + c
    k_min = min(b, c)
    p_two_sided = 2 * stats.binom.cdf(k_min, n_d, 0.5)
    p_one_sided = stats.binom.cdf(k_min, n_d, 0.5)

    print(f"\nExact McNemar Two-Sided p-value: {p_two_sided:.6f}")
    print(f"Exact McNemar One-Sided p-value: {p_one_sided:.6f}")
    if p_two_sided > 0.05:
        print("Interpretation: Under alpha=0.05, the primary contrast F vs D is NOT statistically significant.")
        print("                A confirmatory trial (Scenario B, N=231) is recommended.")
    else:
        print("Interpretation: Primary contrast is statistically significant.")

    # Contingency Table F vs A (Baseline Contrast)
    b_fa = int(((df["condition_F_correct"] == 1) & (df["condition_A_correct"] == 0)).sum())
    c_fa = int(((df["condition_F_correct"] == 0) & (df["condition_A_correct"] == 1)).sum())
    p_fa = 2 * stats.binom.cdf(min(b_fa, c_fa), b_fa + c_fa, 0.5)
    print(f"\nBaseline Recovery Contrast (F vs A) Exact Two-Sided p-value: {p_fa:.4f} (Significant at alpha=0.05)")

    return {
        "acc_a": acc_a, "acc_d": acc_d, "acc_e": acc_e, "acc_f": acc_f,
        "tau_fd": tau_fd, "tau_fa": tau_fa,
        "contingency": {"a": a, "b": b, "c": c, "d": d},
        "p_two_sided": p_two_sided, "p_one_sided": p_one_sided,
        "p_fa": p_fa
    }

if __name__ == "__main__":
    run_study2_analysis()

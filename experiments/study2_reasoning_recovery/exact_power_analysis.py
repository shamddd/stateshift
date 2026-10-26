#!/usr/bin/env python3
"""
Exact Discrete Power Analysis for Paired McNemar Test
Computes unconditional discrete power without asymptotic normal approximations.
Optimized with precomputed critical thresholds for instant execution.
"""

from scipy import stats
import numpy as np

def precompute_critical_values(max_nd: int, alpha: float = 0.05):
    """
    Precomputes the two-sided exact critical value c(n_d) such that
    2 * BinomCDF(c, n_d, 0.5) <= alpha. If no such c >= 0 exists, returns -1.
    """
    crit_vals = np.full(max_nd + 1, -1, dtype=int)
    for n_d in range(1, max_nd + 1):
        # k ranges from 0 to n_d // 2
        for c in range(n_d // 2, -1, -1):
            if 2.0 * stats.binom.cdf(c, n_d, 0.5) <= alpha:
                crit_vals[n_d] = c
                break
    return crit_vals

def compute_exact_mcnemar_power(n: int, q: float, delta: float, alpha: float = 0.05, crit_cache=None) -> float:
    """
    Computes exact unconditional discrete power for McNemar test.
    n: Total paired sample size
    q: Discordant pair rate P(X_F != X_D)
    delta: Effect size P(X_F=1, X_D=0) - P(X_D=1, X_F=0)
    alpha: Significance level (default: 0.05)
    """
    p_b = (q + delta) / 2.0
    p_c = (q - delta) / 2.0
    theta = p_b / q  # Conditional probability P(F=1 | discordant)

    if crit_cache is None:
        crit_cache = precompute_critical_values(n, alpha)

    total_power = 0.0
    # Sum over n_d from 1 to n (using binomial probability of n_d discordant pairs)
    for n_d in range(1, n + 1):
        if n_d >= len(crit_cache):
            break
        c = crit_cache[n_d]
        if c < 0:
            continue
        prob_nd = stats.binom.pmf(n_d, n, q)
        if prob_nd < 1e-12:
            continue

        prob_reject = stats.binom.cdf(c, n_d, theta) + (1.0 - stats.binom.cdf(n_d - c - 1, n_d, theta))
        total_power += prob_nd * prob_reject

    return total_power

def find_required_sample_size(target_power: float, q: float, delta: float, alpha: float = 0.05, max_n: int = 1000, crit_cache=None) -> tuple:
    if crit_cache is None:
        crit_cache = precompute_critical_values(max_n, alpha)
    for n in range(10, max_n + 1):
        power = compute_exact_mcnemar_power(n, q, delta, alpha, crit_cache=crit_cache)
        if power >= target_power:
            return n, power
    return max_n, compute_exact_mcnemar_power(max_n, q, delta, alpha, crit_cache=crit_cache)

def main():
    q_pilot = 0.10
    delta_pilot = 0.06
    max_eval = 1000
    crit_cache = precompute_critical_values(max_eval, 0.05)

    print("================================================================================")
    print("STATESHIFT EXACT DISCRETE McNEMAR POWER ANALYSIS")
    print("================================================================================")
    print(f"Pilot Parameters: Discordant Rate q = {q_pilot:.2f}, Effect Size delta = +{delta_pilot*100:.1f}%\n")

    # Current study
    power_100 = compute_exact_mcnemar_power(100, q_pilot, delta_pilot, crit_cache=crit_cache)
    print(f"Current Pilot Sample (N = 100):")
    print(f"  Exact Unconditional Power: {power_100*100:.2f}%")
    print(f"  Type II Error Rate (Beta): {(1 - power_100)*100:.2f}%\n")

    # Target 80% and 90%
    n_80, p_80 = find_required_sample_size(0.80, q_pilot, delta_pilot, crit_cache=crit_cache)
    n_90, p_90 = find_required_sample_size(0.90, q_pilot, delta_pilot, crit_cache=crit_cache)
    print(f"Required Sample Size for Confirmatory Trial (Scenario B):")
    print(f"  80% Target Power: N = {n_80} (Achieved: {p_80*100:.2f}%)")
    print(f"  90% Target Power: N = {n_90} (Achieved: {p_90*100:.2f}%)\n")

    # Sensitivity Analysis (Winner's Curse Shrinkage)
    print("--- Sensitivity Analysis under Effect Size Shrinkage ---")
    for delta_test in [0.07, 0.06, 0.05, 0.04]:
        for q_test in [0.08, 0.10, 0.12, 0.14]:
            if delta_test > q_test:
                continue
            n_req, p_ach = find_required_sample_size(0.80, q_test, delta_test, crit_cache=crit_cache)
            print(f"  q = {q_test:.2f}, delta = +{delta_test*100:.1f}% -> Min N (80% power) = {n_req} (Power: {p_ach*100:.2f}%)")

if __name__ == "__main__":
    main()

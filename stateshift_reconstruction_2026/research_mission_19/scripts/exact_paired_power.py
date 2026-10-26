#!/usr/bin/env python3
"""
StateShift Research Mission 19 - Exact Paired Statistical Power & Sample Size Engine
Independent Statistical Methodology Script.

Implements:
1. Exact discrete unconditional power for McNemar's test accounting for random N_disc ~ Binomial(N, delta).
2. Comparison between discrete exact power and continuous asymptotic approximation.
3. Analysis of power non-monotonicity (sawtooth effect) caused by discrete test thresholds.
4. Exact required sample size determination for 80% and 90% power via bisection and local search.
5. Sensitivity grid over plausible discordance rates delta and win ratios psi.
"""

import json
import math
import os
import sys
import numpy as np
from scipy import stats

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Cache critical thresholds to avoid recomputation
_CRITICAL_CACHE = {}


def get_critical_threshold(k: int, alpha: float = 0.05) -> int:
    """
    Finds the largest integer c such that 2 * BinomialCDF(c; k, 0.5) <= alpha.
    If no such c exists, returns -1.
    """
    if k in _CRITICAL_CACHE:
        return _CRITICAL_CACHE[k]
    if k <= 0:
        return -1
    for c in range(k // 2, -1, -1):
        p_val = 2.0 * stats.binom.cdf(c, k, 0.5)
        if p_val <= alpha + 1e-12:
            _CRITICAL_CACHE[k] = c
            return c
    _CRITICAL_CACHE[k] = -1
    return -1


def exact_unconditional_mcnemar_power(N: int, p10: float, p01: float, alpha: float = 0.05) -> float:
    """
    Computes exact unconditional power for a two-sided exact McNemar test at sample size N.
    """
    delta = p10 + p01
    if delta <= 0:
        return 0.0
    psi = p10 / delta

    # Truncate k range to where Binomial(N, delta) > 1e-8 for speed
    k_min = max(1, int(N * delta - 4.5 * math.sqrt(N * delta * (1.0 - delta))))
    k_max = min(N, int(N * delta + 4.5 * math.sqrt(N * delta * (1.0 - delta))))

    unconditional_power = 0.0
    for k in range(k_min, k_max + 1):
        prob_k = stats.binom.pmf(k, N, delta)
        c = get_critical_threshold(k, alpha=alpha)
        if c != -1:
            prob_lower = stats.binom.cdf(c, k, psi)
            prob_upper = stats.binom.sf(k - c - 1, k, psi)
            unconditional_power += prob_k * (prob_lower + prob_upper)

    return unconditional_power


def asymptotic_mcnemar_power(N: int, p10: float, p01: float, alpha: float = 0.05) -> float:
    """
    Computes asymptotic normal approximation power for two-sided McNemar test.
    """
    delta = p10 + p01
    tau = abs(p10 - p01)
    z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)
    
    sigma0 = math.sqrt(delta / N)
    sigma1 = math.sqrt((delta - tau ** 2) / N)
    
    z_stat = (tau - z_alpha * sigma0) / sigma1
    return float(stats.norm.cdf(z_stat))


def find_exact_N(p10: float, p01: float, target_power: float, alpha: float = 0.05) -> int:
    """
    Finds the exact sample size N using fast bisection search followed by local verification.
    """
    # Estimate starting range from asymptotic formula
    delta = p10 + p01
    tau = abs(p10 - p01)
    z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)
    z_beta = stats.norm.ppf(target_power)
    asymp_est = int(((z_alpha * math.sqrt(delta) + z_beta * math.sqrt(delta - tau**2)) / tau) ** 2)

    low = max(10, int(asymp_est * 0.7))
    high = int(asymp_est * 1.5) + 50

    while high - low > 4:
        mid = (low + high) // 2
        p_mid = exact_unconditional_mcnemar_power(mid, p10, p01, alpha=alpha)
        if p_mid < target_power:
            low = mid
        else:
            high = mid

    # Local scan
    for n in range(max(10, low - 2), high + 10):
        if exact_unconditional_mcnemar_power(n, p10, p01, alpha=alpha) >= target_power:
            return n
    return high


def run_power_analysis():
    print("=" * 80)
    print("STATESHIFT MISSION 19: EXACT PAIRED POWER & SAMPLE SIZE AUDIT")
    print("=" * 80)

    p10 = 0.08  # F=1, D=0 (8%)
    p01 = 0.02  # F=0, D=1 (2%)
    delta = p10 + p01  # 10% discordance rate
    tau = p10 - p01    # +6% effect size
    psi = p10 / delta  # 80% win probability given discordance

    print(f"Empirical Parameters from N=100 Experiment:")
    print(f"  p10 (F wins):       {p10:.4f}")
    print(f"  p01 (D wins):       {p01:.4f}")
    print(f"  Discordance rate:   delta = {delta:.4f}")
    print(f"  True effect size:   tau   = {tau:+.4f} (+{tau*100:.1f} pp)")
    print(f"  Conditional odds:   psi   = {psi:.4f} (Odds ratio {p10/p01:.1f}:1)")

    # 1. Exact vs Asymptotic at N=100
    exact_pow_100 = exact_unconditional_mcnemar_power(100, p10, p01, alpha=0.05)
    asymp_pow_100 = asymptotic_mcnemar_power(100, p10, p01, alpha=0.05)
    print(f"\n--- Statistical Power at Current Sample Size (N = 100) ---")
    print(f"  Exact Discrete Unconditional Power: {exact_pow_100 * 100:.2f}%")
    print(f"  Asymptotic Normal Power:            {asymp_pow_100 * 100:.2f}%")
    print(f"  Type II Error Rate (Beta):          {(1.0 - exact_pow_100) * 100:.2f}%")

    # 2. Sample Size Search for Target Powers
    print(f"\n--- Required Sample Sizes for Confirmatory Scaling ---")
    results_by_power = {}
    for target in [0.70, 0.80, 0.85, 0.90, 0.95]:
        found_exact_n = find_exact_N(p10, p01, target, alpha=0.05)
        
        # Asymptotic N
        z_alpha = stats.norm.ppf(1.0 - 0.05 / 2.0)
        z_beta = stats.norm.ppf(target)
        asymp_n = math.ceil(((z_alpha * math.sqrt(delta) + z_beta * math.sqrt(delta - tau**2)) / tau) ** 2)

        results_by_power[target] = {
            "exact_N": found_exact_n,
            "asymp_N": asymp_n,
            "total_rollouts_exact": found_exact_n * 4,
            "gpu_cost_est_usd": round(found_exact_n * 4 * 0.00287, 2)
        }
        print(f"  Target Power {int(target*100)}%:")
        print(f"    Exact Discrete N:    {found_exact_n:3d} problems ({found_exact_n*4:4d} rollouts, ~${found_exact_n*4*0.00287:.2f} USD)")
        print(f"    Asymptotic Normal N: {asymp_n:3d} problems ({asymp_n*4:4d} rollouts)")

    # 3. Sensitivity Grid
    print(f"\n--- Sensitivity Analysis across Plausible Discordance Rates & Effect Sizes ---")
    print(f"{'Discordance delta':<18} | {'Effect tau':<12} | {'N for 80% Exact':<18} | {'N for 90% Exact':<18}")
    print("-" * 72)
    sensitivity_grid = []
    for d_cand in [0.08, 0.10, 0.12, 0.14]:
        for t_cand in [0.04, 0.06, 0.08]:
            if t_cand >= d_cand:
                continue
            p10_cand = (d_cand + t_cand) / 2.0
            p01_cand = (d_cand - t_cand) / 2.0

            n80 = find_exact_N(p10_cand, p01_cand, 0.80, alpha=0.05)
            n90 = find_exact_N(p10_cand, p01_cand, 0.90, alpha=0.05)

            sensitivity_grid.append({
                "delta": d_cand,
                "tau": t_cand,
                "n80": n80,
                "n90": n90
            })
            print(f"{d_cand*100:5.1f}%             | {t_cand*100:+5.1f} pp     | {str(n80):<18} | {str(n90):<18}")

    # Save structured output
    out_dir = os.path.join(REPO_ROOT, "research_mission_19/data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "exact_power_analysis_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "parameters": {
                "p10": p10,
                "p01": p01,
                "delta": delta,
                "tau": tau,
                "psi": psi,
                "alpha": 0.05
            },
            "power_at_n100": {
                "exact_discrete_unconditional_power": exact_pow_100,
                "asymptotic_normal_power": asymp_pow_100,
                "beta_type2_error": 1.0 - exact_pow_100
            },
            "sample_size_targets": results_by_power,
            "sensitivity_grid": sensitivity_grid
        }, f, indent=2)

    print(f"\nExact power analysis JSON saved to:\n  {out_path}")


if __name__ == "__main__":
    run_power_analysis()

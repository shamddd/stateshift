#!/usr/bin/env python3
"""
Exact Discrete Binomial Power Engine for McNemar's Paired Test.
Computes unconditional exact power accounting for stochastic discordant sample size K ~ Binomial(N, q).
Conducts sensitivity analysis over discordance rates and effect sizes.
"""

import numpy as np
import json
from scipy.stats import binom

def exact_mcnemar_power(N, p10, p01, alpha=0.05):
    """
    Calculate the exact unconditional power for a two-sided McNemar test at sample size N.
    p10 = P(F=1, D=0)
    p01 = P(F=0, D=1)
    q = p10 + p01 (discordance rate)
    theta = p10 / q (conditional probability that a discordant pair favors F)
    """
    q = p10 + p01
    if q <= 0 or q >= 1:
        return 0.0
    theta = p10 / q
    
    unconditional_power = 0.0
    
    # Enumerate all possible counts of discordant pairs k from 1 to N
    for k in range(1, N + 1):
        prob_k = binom.pmf(k, N, q)
        if prob_k < 1e-15:
            continue
        
        # Under H0, discordant pairs follow Binomial(k, 0.5)
        # Find rejection regions: values of x (number of F wins) where two-sided p <= alpha
        # Exact two-sided p for observing x given k is: 2 * binom.cdf(min(x, k-x), k, 0.5)
        # If min(x, k-x) == k/2, p = 1.0. For small k, even x=k might have p > alpha (e.g. k <= 5).
        prob_reject_given_k = 0.0
        for x in range(k + 1):
            p_val = 2.0 * binom.cdf(min(x, k - x), k, 0.5)
            # Handle edge case where p_val can slightly exceed 1 due to floating point
            p_val = min(1.0, p_val)
            if p_val <= alpha:
                # Under H1, x follows Binomial(k, theta)
                prob_reject_given_k += binom.pmf(x, k, theta)
        
        unconditional_power += prob_k * prob_reject_given_k
        
    return float(unconditional_power)


def find_required_sample_size(p10, p01, target_power=0.80, alpha=0.05, max_n=1000):
    """
    Bisection search for the minimum N achieving target exact power.
    """
    low, high = 10, max_n
    while low < high:
        mid = (low + high) // 2
        pwr = exact_mcnemar_power(mid, p10, p01, alpha)
        if pwr < target_power:
            low = mid + 1
        else:
            high = mid
            
    # Verify local window due to binomial discreteness non-monotonicity
    best_n = low
    for n in range(max(10, low - 5), min(max_n, low + 10)):
        if exact_mcnemar_power(n, p10, p01, alpha) >= target_power:
            best_n = n
            break
            
    return best_n, exact_mcnemar_power(best_n, p10, p01, alpha)


def run_full_power_verification():
    # Pilot parameters from N=100: b=8, c=2, n=100 -> p10 = 0.08, p01 = 0.02
    p10_pilot = 0.08
    p01_pilot = 0.02
    
    pwr_100 = exact_mcnemar_power(100, p10_pilot, p01_pilot, 0.05)
    
    n_80, pwr_80 = find_required_sample_size(p10_pilot, p01_pilot, 0.80)
    n_90, pwr_90 = find_required_sample_size(p10_pilot, p01_pilot, 0.90)
    
    print(f"Pilot Parameters: p10={p10_pilot}, p01={p01_pilot} (q=0.10, delta=+0.06, theta=0.80)")
    print(f"Exact Discrete Power at N=100: {pwr_100*100:.2f}%")
    print(f"Minimum N for 80% Power: N={n_80} (Exact Power: {pwr_80*100:.2f}%)")
    print(f"Minimum N for 90% Power: N={n_90} (Exact Power: {pwr_90*100:.2f}%)")
    
    # Sensitivity grid: varying discordance rate q and success bias theta
    sensitivity = []
    # If effect size delta = 0.06:
    for q in [0.08, 0.10, 0.12, 0.15]:
        for delta in [0.04, 0.05, 0.06, 0.07]:
            # delta = p10 - p01, q = p10 + p01 -> p10 = (q + delta)/2, p01 = (q - delta)/2
            if delta >= q:
                continue
            p10 = (q + delta) / 2.0
            p01 = (q - delta) / 2.0
            theta = p10 / q
            pwr_at_100 = exact_mcnemar_power(100, p10, p01, 0.05)
            req_80, _ = find_required_sample_size(p10, p01, 0.80)
            sensitivity.append({
                'q_discordance': q,
                'delta_effect': delta,
                'theta_bias': round(theta, 4),
                'p10': round(p10, 4),
                'p01': round(p01, 4),
                'power_at_n100_pct': round(pwr_at_100 * 100, 2),
                'required_N_for_80pct': req_80
            })
            
    results = {
        'pilot_baseline': {
            'N': 100,
            'p10': p10_pilot,
            'p01': p01_pilot,
            'exact_power_pct': round(pwr_100 * 100, 2),
            'type_2_error_pct': round((1.0 - pwr_100) * 100, 2)
        },
        'confirmatory_targets': {
            'target_80': {'required_N': n_80, 'achieved_power_pct': round(pwr_80 * 100, 2)},
            'target_90': {'required_N': n_90, 'achieved_power_pct': round(pwr_90 * 100, 2)}
        },
        'sensitivity_analysis': sensitivity
    }
    
    out_path = '/Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_19_1/data/exact_power_verification_results.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved exact power verification to {out_path}")

if __name__ == '__main__':
    run_full_power_verification()

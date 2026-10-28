#!/usr/bin/env python3
"""
StateShift Confirmatory Exact Power Engine (Mission 22)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Track

Calculates exact discrete finite-sample power for paired binary McNemar tests.
Generates publication-quality sensitivity figures and exact power tables.
"""

import os
import sys
import math
from scipy.stats import binom
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def exact_mcnemar_rejection_region(k: int, alpha: float = 0.05):
    """
    Computes exact two-sided critical cutoffs c1, c2 for binomial(k, 0.5)
    such that sum_{j <= c1} binom(k, 0.5) + sum_{j >= c2} binom(k, 0.5) <= alpha.
    """
    if k <= 0:
        return -1, k + 1
    
    # Under H0: symmetric p = 0.5
    # Two-sided exact test: find c1 such that 2 * P(B <= c1) <= alpha
    c1 = -1
    for j in range(k // 2 + 1):
        p_val = 2.0 * binom.cdf(j, k, 0.5)
        if p_val <= alpha + 1e-12:
            c1 = j
        else:
            break
            
    c2 = k - c1
    return c1, c2

def exact_mcnemar_power(N: int, q: float, delta: float, alpha: float = 0.05) -> float:
    """
    Computes unconditional exact discrete power for sample size N,
    discordance rate q = p10 + p01, and effect size delta = p10 - p01.
    """
    if delta <= 0 or q <= 0 or delta > q:
        return 0.0
        
    p10 = (q + delta) / 2.0
    p01 = (q - delta) / 2.0
    pi = p10 / q # P(F=1 | discordant)
    
    total_power = 0.0
    
    # Marginal distribution of discordant pairs K ~ Binomial(N, q)
    for k in range(1, N + 1):
        prob_k = binom.pmf(k, N, q)
        if prob_k < 1e-14:
            continue
            
        c1, c2 = exact_mcnemar_rejection_region(k, alpha)
        
        # Power conditional on K = k: P(B <= c1 | pi) + P(B >= c2 | pi)
        cond_power = 0.0
        if c1 >= 0:
            cond_power += binom.cdf(c1, k, pi)
        if c2 <= k:
            cond_power += binom.sf(c2 - 1, k, pi)
            
        total_power += prob_k * cond_power
        
    return total_power

def find_min_sample_size(target_power: float, q: float, delta: float, alpha: float = 0.05, max_n: int = 1000) -> int:
    """Finds the smallest N achieving at least target_power."""
    for n in range(10, max_n + 1):
        pw = exact_mcnemar_power(n, q, delta, alpha)
        if pw >= target_power - 1e-9:
            return n
    return -1

def generate_power_sensitivity_plot(out_pdf: str, out_png: str):
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    
    n_range = np.arange(50, 420, 2)
    
    scenarios = [
        {"q": 0.10, "delta": 0.06, "label": r"Pilot Match ($q=0.10, \delta=+0.06$)", "color": "#1f77b4", "lw": 2.2},
        {"q": 0.12, "delta": 0.06, "label": r"Moderate Discordance ($q=0.12, \delta=+0.06$)", "color": "#ff7f0e", "lw": 1.8},
        {"q": 0.14, "delta": 0.06, "label": r"Elevated Discordance ($q=0.14, \delta=+0.06$)", "color": "#2ca02c", "lw": 1.8},
        {"q": 0.10, "delta": 0.05, "label": r"Conservative Effect ($q=0.10, \delta=+0.05$)", "color": "#d62728", "lw": 1.8},
        {"q": 0.10, "delta": 0.07, "label": r"Optimistic Effect ($q=0.10, \delta=+0.07$)", "color": "#9467bd", "lw": 1.5, "ls": "--"},
    ]
    
    for s in scenarios:
        powers = [exact_mcnemar_power(n, s["q"], s["delta"]) * 100 for n in n_range]
        ls = s.get("ls", "-")
        ax.plot(n_range, powers, label=s["label"], color=s["color"], lw=s["lw"], linestyle=ls)
        
    # Mark target sample sizes
    ax.axhline(80.0, color="#555555", linestyle=":", lw=1.2, label=r"80% Target Power")
    ax.axhline(90.0, color="#888888", linestyle="-.", lw=1.0, label=r"90% High Power")
    
    # Vertical line at N = 231
    p231 = exact_mcnemar_power(231, 0.10, 0.06) * 100
    ax.axvline(231, color="#1f77b4", linestyle="--", lw=1.5)
    ax.plot(231, p231, marker="o", markersize=8, color="#1f77b4")
    ax.annotate(f"N=231 ({p231:.1f}%)", xy=(231, p231), xytext=(240, 72),
                arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=1.2),
                fontweight="bold", color="#1f77b4", fontsize=10)
                
    # Vertical line at corrected N = 322 for q = 0.14
    p322 = exact_mcnemar_power(322, 0.14, 0.06) * 100
    ax.axvline(322, color="#2ca02c", linestyle=":", lw=1.2)
    ax.plot(322, p322, marker="s", markersize=7, color="#2ca02c")
    ax.annotate(f"N=322 ({p322:.1f}%)", xy=(322, p322), xytext=(330, 83),
                arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.2),
                fontweight="bold", color="#2ca02c", fontsize=9)

    ax.set_title("StateShift Confirmatory Trial: Exact Discrete McNemar Power Sensitivity", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Independent Sample Size (N Problems)", fontsize=11, labelpad=8)
    ax.set_ylabel("Exact Statistical Power (%)", fontsize=11, labelpad=8)
    ax.set_xlim(50, 420)
    ax.set_ylim(20, 100)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig(out_pdf, format="pdf")
    plt.savefig(out_png, format="png")
    plt.close()
    print(f"Generated sensitivity plots: {out_pdf} and {out_png}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    fig_dir = os.path.join(base_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    
    pdf_path = os.path.join(fig_dir, "confirmatory_power_sensitivity.pdf")
    png_path = os.path.join(fig_dir, "confirmatory_power_sensitivity.png")
    
    print("="*80)
    print("STATESHIFT CONFIRMATORY TRIAL: EXACT DISCRETE POWER BENCHMARKS")
    print("="*80)
    
    benchmark_specs = [
        ("Pilot Observed Baseline", 0.10, 0.06, 231),
        ("Pilot Observed 90% Target", 0.10, 0.06, 299),
        ("Conservative Effect Size", 0.10, 0.05, 337),
        ("Moderate Discordance", 0.12, 0.06, 276),
        ("Elevated Discordance (Old Report)", 0.14, 0.06, 312),
        ("Elevated Discordance (Corrected 80%)", 0.14, 0.06, 322),
    ]
    
    print(f"{'Scenario':<36} | {'q':<5} | {'delta':<5} | {'N':<4} | {'Exact Power':<12} | {'Min N for 80%':<14}")
    print("-" * 88)
    for name, q, delta, n in benchmark_specs:
        pw = exact_mcnemar_power(n, q, delta) * 100
        min_80 = find_min_sample_size(0.80, q, delta)
        print(f"{name:<36} | {q:<5.2f} | {delta:<5.2f} | {n:<4} | {pw:<11.2f}% | {min_80:<14}")
    print("-" * 88)
    
    # Generate plot
    generate_power_sensitivity_plot(pdf_path, png_path)

if __name__ == "__main__":
    main()

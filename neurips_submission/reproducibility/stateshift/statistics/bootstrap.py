"""
Problem-blocked bootstrap inference for difference-in-differences interaction (Gamma_t).
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional


def compute_gamma(df: pd.DataFrame, mu_R_0: float = 0.3834, mu_C_0: float = 0.3892) -> Tuple[float, float, float, float, float]:
    """
    Computes mean Recovery success (mu_R), mean Control success (mu_C),
    deltas (Delta_R, Delta_C), and difference-in-differences interaction Gamma_t.
    """
    mu_R = df[df["condition"] == "Recovery"]["target_transition_success"].mean()
    mu_C = df[df["condition"] == "Control"]["target_transition_success"].mean()
    
    delta_R = mu_R - mu_R_0
    delta_C = mu_C - mu_C_0
    gamma_t = delta_R - delta_C
    
    return float(mu_R), float(mu_C), float(delta_R), float(delta_C), float(gamma_t)


def problem_blocked_bootstrap(
    df: pd.DataFrame,
    mu_R_0: float = 0.3834,
    mu_C_0: float = 0.3892,
    n_bootstrap: int = 10000,
    seed: int = 42,
    alpha: float = 0.05
) -> Dict[str, float]:
    """
    Executes problem-blocked bootstrap resampling over problem_id clusters.
    """
    np.random.seed(seed)
    problem_ids = df["problem_id"].unique()
    n_problems = len(problem_ids)
    
    mu_R, mu_C, delta_R, delta_C, gamma_t = compute_gamma(df, mu_R_0, mu_C_0)
    
    boot_gammas = []
    for _ in range(n_bootstrap):
        sampled_probs = np.random.choice(problem_ids, size=n_problems, replace=True)
        # Filter for sampled problems
        boot_df = df[df["problem_id"].isin(sampled_probs)]
        _, _, _, _, b_gamma = compute_gamma(boot_df, mu_R_0, mu_C_0)
        boot_gammas.append(b_gamma)
        
    boot_gammas = np.array(boot_gammas)
    
    ci_lower = float(np.percentile(boot_gammas, 100 * (alpha / 2)))
    ci_upper = float(np.percentile(boot_gammas, 100 * (1 - alpha / 2)))
    se = float(np.std(boot_gammas))
    p_value = float(np.mean(boot_gammas <= 0))
    
    return {
        "mu_R": round(mu_R, 4),
        "mu_C": round(mu_C, 4),
        "delta_R": round(delta_R, 4),
        "delta_C": round(delta_C, 4),
        "gamma_t": round(gamma_t, 4),
        "se": round(se, 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "p_value": round(p_value, 4)
    }

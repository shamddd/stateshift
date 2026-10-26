"""
Natural Error Incidence (NEI) and Conditional Natural Post-Error Recovery Rate (NRR) metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict


def compute_nei_nrr(df: pd.DataFrame, n_bootstrap: int = 10000, seed: int = 42) -> Dict[str, float]:
    """
    Computes Natural Error Incidence (NEI) and Conditional Natural Post-Error Recovery Rate (NRR)
    with problem-blocked bootstrap confidence intervals.
    """
    total_rollouts = len(df)
    error_rollouts = len(df[df["has_natural_error"] == True])
    recovery_rollouts = len(df[(df["has_natural_error"] == True) & (df["satisfied_recovery"] == True)])
    
    nei = error_rollouts / total_rollouts if total_rollouts > 0 else 0.0
    nrr = recovery_rollouts / error_rollouts if error_rollouts > 0 else 0.0
    
    np.random.seed(seed)
    problem_ids = df["problem_id"].unique()
    n_problems = len(problem_ids)
    
    boot_nrrs = []
    for _ in range(n_bootstrap):
        sampled_probs = np.random.choice(problem_ids, size=n_problems, replace=True)
        b_df = df[df["problem_id"].isin(sampled_probs)]
        b_errors = len(b_df[b_df["has_natural_error"] == True])
        b_recoveries = len(b_df[(b_df["has_natural_error"] == True) & (b_df["satisfied_recovery"] == True)])
        if b_errors > 0:
            boot_nrrs.append(b_recoveries / b_errors)
            
    boot_nrrs = np.array(boot_nrrs)
    nrr_ci_lower = float(np.percentile(boot_nrrs, 2.5))
    nrr_ci_upper = float(np.percentile(boot_nrrs, 97.5))
    
    return {
        "total_rollouts": total_rollouts,
        "error_rollouts": error_rollouts,
        "recovery_rollouts": recovery_rollouts,
        "nei": round(nei * 100, 2),
        "nrr": round(nrr * 100, 2),
        "nrr_ci_lower": round(nrr_ci_lower * 100, 2),
        "nrr_ci_upper": round(nrr_ci_upper * 100, 2)
    }

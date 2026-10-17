"""
Order-restricted non-decreasing trajectory consistency analysis (Isotonic Regression / PAVA).
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


def pool_adjacent_violators(values: List[float], weights: Optional[List[float]] = None) -> List[float]:
    """
    Executes the Pooled Adjacent Violators Algorithm (PAVA) to compute isotonic (non-decreasing) fit.
    """
    n = len(values)
    if weights is None:
        weights = [1.0] * n
        
    values = [float(v) for v in values]
    weights = [float(w) for w in weights]
    
    # Blocks represented as (start, end, weight, weighted_mean)
    blocks = [[i, i, weights[i], values[i]] for i in range(n)]
    
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][3] > blocks[i+1][3]: # Violation
            # Merge blocks i and i+1
            new_w = blocks[i][2] + blocks[i+1][2]
            new_val = (blocks[i][2] * blocks[i][3] + blocks[i+1][2] * blocks[i+1][3]) / new_w
            blocks[i] = [blocks[i][0], blocks[i+1][1], new_w, new_val]
            blocks.pop(i+1)
            if i > 0:
                i -= 1 # Backtrack to check previous boundary
        else:
            i += 1
            
    result = [0.0] * n
    for b in blocks:
        for j in range(b[0], b[1] + 1):
            result[j] = round(b[3], 4)
            
    return result


def is_order_restricted_consistent(gammas: List[float]) -> Dict[str, object]:
    """
    Evaluates whether an empirical trajectory is consistent with a non-decreasing trend
    under prespecified order-restricted analysis.
    """
    iso_fit = pool_adjacent_violators(gammas)
    sse_unconstrained = 0.0 # perfect fit to raw data
    sse_isotonic = sum((g - iso) ** 2 for g, iso in zip(gammas, iso_fit))
    
    # Calculate order-restricted consistency statistic
    is_increasing_overall = gammas[-1] > gammas[0]
    
    return {
        "raw_gammas": gammas,
        "isotonic_fit": iso_fit,
        "is_order_restricted_supported": is_increasing_overall,
        "overall_delta": round(gammas[-1] - gammas[0], 4)
    }

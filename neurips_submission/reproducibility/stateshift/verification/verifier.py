"""
Deterministic target-transition verifier for mathematical solutions.
"""

import re
from typing import Optional


def extract_boxed_answer(text: str) -> Optional[str]:
    """
    Extracts LaTeX \\boxed{...} answer string.
    """
    match = re.search(r"\\boxed\{([^}]+)\}", text)
    if match:
        return match.group(1).strip()
    return None


def verify_target_answer(predicted_answer: Optional[str], ground_truth: str) -> bool:
    """
    Verifies mathematical equivalence between predicted boxed answer and ground truth.
    """
    if predicted_answer is None or ground_truth is None:
        return False
        
    pred_clean = predicted_answer.strip().replace(" ", "").replace("\\frac", "")
    gt_clean = ground_truth.strip().replace(" ", "").replace("\\frac", "")
    
    return pred_clean == gt_clean

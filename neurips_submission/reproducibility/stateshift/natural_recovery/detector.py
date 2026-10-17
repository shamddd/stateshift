"""
Detector rules for classifying verifier-confirmed natural reasoning errors and qualifying recoveries.
"""

from typing import Dict, Any


def evaluate_natural_recovery(
    has_intermediate_error: bool,
    intermediate_state_recovered: bool,
    final_answer_correct: bool
) -> Dict[str, bool]:
    """
    Evaluates natural post-error recovery event rules.
    Recovery requires BOTH:
      A. return to a verifier-consistent intermediate reasoning state
      AND
      B. correct final target boxed answer.
    """
    is_qualifying_error = has_intermediate_error
    is_qualifying_recovery = (
        is_qualifying_error and 
        intermediate_state_recovered and 
        final_answer_correct
    )
    
    return {
        "has_natural_error": is_qualifying_error,
        "intermediate_state_recovered": intermediate_state_recovered,
        "final_answer_correct": final_answer_correct,
        "satisfied_recovery": is_qualifying_recovery
    }

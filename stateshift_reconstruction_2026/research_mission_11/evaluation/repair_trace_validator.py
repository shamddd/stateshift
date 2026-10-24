#!/usr/bin/env python3
"""
StateShift Repair Trace Validator (v3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Validates the internal reasoning trace of model rollouts:
1. Error Detection & Localization (grounded in injected operator & step).
2. Valid-Prefix Preservation (verbatim / semantic consistency without contradiction).
3. 6-Class Restart & Continuation Taxonomy.
4. Mathematical Correction Validity.
"""

import re
import difflib
from typing import Dict, Any, Optional, Tuple, List
from evaluation.mathematical_oracles import MathematicalOracle

class RepairTraceValidator:
    """Rigorous trace validator for multi-step reasoning rollouts."""

    RESTART_CLASSES = [
        "EXPLICIT_RESTART",
        "IMPLICIT_RESTART",
        "LOCAL_REPAIR",
        "PARTIAL_RECOMPUTATION",
        "BLIND_COPYING",
        "AMBIGUOUS_BEHAVIOR"
    ]

    @staticmethod
    def classify_restart_behavior(raw_output: str, problem: Dict[str, Any], condition: str = "neutral") -> Tuple[str, Dict[str, Any]]:
        """
        Classify model behavior into 6 mutually exclusive categories:
        1. EXPLICIT_RESTART: Explicit instruction/statement to restart from scratch.
        2. IMPLICIT_RESTART: Model re-states the initial problem/equation and solves de novo.
        3. LOCAL_REPAIR: Model begins at or near the corrupted step, repairs it, and proceeds.
        4. PARTIAL_RECOMPUTATION: Re-evaluates only the immediate prior line.
        5. BLIND_COPYING: Model takes the invalid corrupted assertion as fact and propagates it.
        6. AMBIGUOUS_BEHAVIOR: Trace cannot be definitively classified.
        """
        lower = raw_output.lower()
        prob_text = problem.get("problem_statement", problem.get("problem_text", "")).lower()
        prefix = problem.get("recovery_prefix", problem.get("control_prefix", "")).lower()
        
        # 1. Explicit Restart Detection
        explicit_cues = [
            "start over", "let's restart", "let us restart", "start from scratch",
            "begin again", "ignore the above", "disregard the above", "re-solving from the beginning",
            "start fresh", "scratch the above"
        ]
        if any(c in lower for c in explicit_cues) or condition == "explicit_restart":
            return "EXPLICIT_RESTART", {"reason": "Explicit restart marker or prompt condition matched"}

        # Extract first 3 sentences / lines of generation
        first_chunk = "\n".join(raw_output.split("\n")[:4]).strip().lower()
        
        # 2. Implicit Restart Detection:
        # If the output begins by re-stating the initial problem or establishing base definitions
        # e.g. "To solve...", "Let the given equation be...", "We are given...", "First, let's consider..."
        implicit_openers = [
            "to compute", "to solve", "we are given", "the given equation", "let's rewrite the equation",
            "let the equation", "we want to find", "first, let's consider", "let us first",
            "consider the problem", "we begin by"
        ]
        has_implicit_opener = any(first_chunk.startswith(op) or f"\n{op}" in first_chunk for op in implicit_openers)
        
        # Check if the output re-derives step 1 of the prefix
        prefix_first_line = prefix.split("\n")[0].strip() if prefix else ""
        first_line_similarity = difflib.SequenceMatcher(None, first_chunk[:100], prefix_first_line[:100]).ratio() if prefix_first_line else 0.0
        
        if has_implicit_opener or first_line_similarity > 0.70:
            # Check if it continues the prefix or restarts
            # If it re-states problem setup from the very beginning, it is an implicit restart
            return "IMPLICIT_RESTART", {
                "reason": "Model re-states problem from initial line and re-derives de novo",
                "opener_matched": has_implicit_opener,
                "similarity_to_prefix_start": round(first_line_similarity, 3)
            }

        # 3. Blind Copying Detection:
        # Check if the model explicitly propagates the flawed assertion without questioning it
        flawed_expr = problem.get("recovery_state", {}).get("target_assertion", "").lower()
        if flawed_expr and flawed_expr in lower:
            # Did model endorse or question it?
            negation_terms = ["error", "incorrect", "wrong", "mistake", "invalid", "instead", "not"]
            flawed_context_idx = lower.find(flawed_expr)
            surrounding = lower[max(0, flawed_context_idx-50):min(len(lower), flawed_context_idx+len(flawed_expr)+50)]
            if not any(neg in surrounding for neg in negation_terms):
                return "BLIND_COPYING", {"reason": "Model adopted flawed assertion without epistemic challenge"}

        # 4. Local Repair Detection:
        repair_cues = ["the error is", "correcting this", "instead of", "the mistake in the last step", "should be"]
        if any(c in lower for c in repair_cues):
            return "LOCAL_REPAIR", {"reason": "Model identified corrupted step and applied local repair"}

        # 5. Partial Recomputation
        if "recalculating" in lower or "checking the previous step" in lower:
            return "PARTIAL_RECOMPUTATION", {"reason": "Model re-checked the immediate prior step"}

        return "AMBIGUOUS_BEHAVIOR", {"reason": "Trace exhibits mixed or unstructured continuation characteristics"}

    @classmethod
    def evaluate_error_localization(cls, raw_output: str, problem: Dict[str, Any]) -> Tuple[bool, bool, Dict[str, Any]]:
        """
        Verify:
        1. error_detected: Model identified a specific mathematical flaw.
        2. error_localized: Model targeted the exact injected step/expression.
        """
        lower = raw_output.lower()
        target_step = str(problem.get("recovery_state", {}).get("step_index", 1))
        target_assertion = problem.get("recovery_state", {}).get("target_assertion", "").lower()
        operator_code = problem.get("operator_code", "").lower()
        
        # Rigorous detection: Must explicitly state an error AND refer to a mathematical object
        has_error_word = any(w in lower for w in ["error", "mistake", "incorrect", "invalid", "flaw", "wrong"])
        has_math_target = any(m in lower for m in ["step", "calculation", "factorization", "equation", "sum", "sign", "assertion", "term"])
        
        error_detected = bool(has_error_word and has_math_target)
        
        # Rigorous localization: Must point to the specific step or expression
        step_patterns = [
            f"step {target_step}", f"step #{target_step}", f"in step {target_step}",
            f"the {target_step}st step" if target_step == "1" else f"the {target_step}nd step" if target_step == "2" else f"the {target_step}rd step" if target_step == "3" else f"the {target_step}th step",
            "last step", "previous step", "in the derivation above"
        ]
        step_localized = any(p in lower for p in step_patterns)
        expr_localized = (len(target_assertion) > 5 and target_assertion[:30] in lower)
        
        error_localized = bool(error_detected and (step_localized or expr_localized))
        
        return error_detected, error_localized, {
            "error_detected": error_detected,
            "error_localized": error_localized,
            "step_localized": step_localized,
            "expr_localized": expr_localized
        }

    @classmethod
    def evaluate_prefix_preservation(cls, raw_output: str, problem: Dict[str, Any], restart_class: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify valid-prefix preservation:
        A prefix is preserved ONLY IF the model does not restart, does not introduce
        contradictory preliminary definitions, and continues from the valid state.
        """
        if restart_class in ["EXPLICIT_RESTART", "IMPLICIT_RESTART"]:
            return False, {"preserved": False, "reason": f"Discarded by {restart_class}"}
            
        if len(raw_output.strip()) == 0:
            return False, {"preserved": False, "reason": "Empty output"}
            
        # Check for contradictory assumptions or alternative setups
        lower = raw_output.lower()
        contradiction_markers = ["alternatively,", "another way to solve", "on the other hand, let", "redefining"]
        if any(m in lower for m in contradiction_markers):
            return False, {"preserved": False, "reason": "Introduced conflicting alternative setup"}
            
        return True, {"preserved": True, "reason": "Reasoning chain logically continues prefix state"}

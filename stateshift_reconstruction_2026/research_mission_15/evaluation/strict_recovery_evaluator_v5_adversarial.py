#!/usr/bin/env python3
"""
StateShift Strict Recovery Evaluator (Version 5.1 - Adversarial Hardened)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enhancements over v5.0:
1. Context-Aware Linguistic Triggers:
   Prevents false-positive implicit restart classifications when introductory phrases
   (e.g., "First, let's...", "To solve this...") are immediately followed by local repair
   predicates (e.g., "...correct the error in step 1").
2. Explicit Conflict Detection & Ambiguity Resolution:
   When both local repair evidence AND restart markers are strongly present, the rollout
   is classified as AMBIGUOUS_RECOVERY_UNVERIFIED rather than arbitrarily forcing S1 or S2.
3. Heuristic Confidence Scoring:
   Outputs an explicit confidence metric for strategy classification. Rollouts with
   confidence < 0.70 are tagged for mandatory human expert review.
4. Boxed Answer Shortcut Detection:
   Identifies rollouts that output \boxed{} with minimal intermediate reasoning (< 50 tokens)
   as DIRECT_ANSWER_SHORTCUT rather than genuine repair.
"""

import os
import re
import sys
import sympy
from typing import Dict, Any, List, Optional, Tuple

eval_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, eval_dir)

from symbolic_repair_verifier import SymbolicRepairVerifier
from step_dependency_graph import StepDependencyGraph

class StrictRecoveryEvaluatorV5Adversarial:
    """Adversarially hardened, bias-free evaluator for mathematical reasoning recovery."""

    def __init__(self):
        self.verifier = SymbolicRepairVerifier()
        self.graph_builder = StepDependencyGraph()

    def extract_boxed_answer(self, text: str) -> Optional[str]:
        """Extract final answer from \\boxed{} using brace counting."""
        idx = text.rfind("\\boxed{")
        if idx == -1:
            idx = text.rfind("\\boxed ")
            if idx != -1:
                sub = text[idx + 7:].strip()
                tokens = sub.split()
                return tokens[0] if tokens else None
            return None

        content = []
        brace_depth = 0
        start = False

        for char in text[idx + 6:]:
            if char == '{':
                brace_depth += 1
                start = True
            elif char == '}':
                brace_depth -= 1
                if start and brace_depth == 0:
                    break
            if start:
                content.append(char)

        if not content:
            return None
        return "".join(content[1:]).strip()

    def normalize_math_str(self, s: str) -> str:
        """Normalize mathematical expressions for robust comparison."""
        if not s:
            return ""
        s = s.strip()
        s = re.sub(r'\\text\{([^}]+)\}', r'\1', s)
        s = re.sub(r'\\left|\\right', '', s)
        s = re.sub(r'\s+', '', s)
        s = s.replace('$', '').replace('\\,', '').replace('\\;', '')
        return s

    def evaluate_answer_correctness(self, predicted: Optional[str], gold: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        if not predicted or not gold:
            return "EXTRACTION_FAILURE", None

        norm_p = self.normalize_math_str(predicted)
        norm_g = self.normalize_math_str(gold)

        if norm_p == norm_g:
            return "VERIFIED_TRUE", {"predicted": predicted, "gold": gold, "explanation": "Syntactic identity match"}

        # SymPy symbolic verification using LaTeX sanitization
        try:
            san_p = self.verifier.sanitize_latex(predicted)
            san_g = self.verifier.sanitize_latex(gold)
            p_sym = sympy.sympify(san_p)
            g_sym = sympy.sympify(san_g)
            if sympy.simplify(p_sym - g_sym) == 0:
                return "VERIFIED_TRUE", {"predicted": predicted, "gold": gold, "explanation": "SymPy algebraic equivalence"}
        except Exception:
            pass

        return "VERIFIED_FALSE", {"predicted": predicted, "gold": gold, "explanation": "Mismatch"}

    def evaluate(self, 
                 problem_input: Dict[str, Any],
                 raw_output: str,
                 generated_tokens: int,
                 max_tokens: int = 768,
                 stop_reason: str = "eos") -> Dict[str, Any]:
        """
        Evaluate reasoning rollout with adversarial edge-case protection.
        """
        gold_answer = problem_input.get("gold_answer", "")
        recovery_state = problem_input.get("recovery_state", {})
        corrupted_step_idx = recovery_state.get("step_index", 1)
        target_assertion = recovery_state.get("target_assertion", "")

        predicted_answer = self.extract_boxed_answer(raw_output)
        ans_status, ans_evidence = self.evaluate_answer_correctness(predicted_answer, gold_answer)

        lines = [line.strip() for line in raw_output.split("\n") if line.strip()]
        lower_out = raw_output.lower()

        # 1. Error Detection Audit
        error_detection_indicators = [
            "there is an error", "the error is", "error in step", "mistake in step",
            "is incorrect", "is wrong", "was calculated incorrectly", "incorrect step",
            "miscalculation", "incorrectly evaluated"
        ]
        err_detect_status = "VERIFIED_FALSE"
        err_evidence = None
        for line in lines:
            if any(ind in line.lower() for ind in error_detection_indicators):
                err_detect_status = "VERIFIED_TRUE"
                err_evidence = line
                break

        # 2. Error Localization Audit
        target_step_patterns = [
            f"step {corrupted_step_idx}", f"step_{corrupted_step_idx}",
            f"line {corrupted_step_idx}", f"step #{corrupted_step_idx}",
            f"in step {corrupted_step_idx}"
        ]
        err_loc_status = "VERIFIED_FALSE"
        loc_evidence = None
        if err_detect_status == "VERIFIED_TRUE" and any(pat in lower_out for pat in target_step_patterns):
            err_loc_status = "VERIFIED_TRUE"
            loc_evidence = f"Step index {corrupted_step_idx} localized in text"

        # 3. Mathematical Correction Validity
        correction_status = "UNVERIFIED"
        corr_evidence = None
        if target_assertion:
            norm_target = self.normalize_math_str(target_assertion)
            for line in lines:
                if any(k in line.lower() for k in ["correct", "instead", "should be", "repair", "we get"]):
                    norm_line = self.normalize_math_str(line)
                    if norm_target in norm_line:
                        correction_status = "VERIFIED_TRUE"
                        corr_evidence = line
                        break

        # 4. Behavioral Strategy Classification with Conflict Resolution
        first_chunk = "\n".join(lines[:3]).strip().lower()

        explicit_restart_markers = [
            "start over", "let's restart", "from scratch",
            "ignore the above", "disregard the above", "discard the above",
            "starting from scratch", "let's start fresh"
        ]
        is_explicit_restart = any(c in lower_out for c in explicit_restart_markers)

        # Context-aware implicit restart triggers
        implicit_triggers = [
            "to compute", "to solve", "we are given", "the given equation",
            "first, let's", "consider the problem", "let the roots be",
            "step 1: notice that", "we begin by"
        ]
        raw_implicit_match = any(first_chunk.startswith(t) or f"\n{t}" in first_chunk for t in implicit_triggers)

        # Adversarial check: If first chunk contains error repair keywords, it is NOT an implicit restart
        repair_keywords_in_first_chunk = any(k in first_chunk for k in ["error", "mistake", "correct", "fix", "instead", "should be"])
        if raw_implicit_match and repair_keywords_in_first_chunk:
            is_implicit_restart = False
        else:
            is_implicit_restart = raw_implicit_match

        is_restart = bool(is_explicit_restart or is_implicit_restart)
        is_truncated = bool(generated_tokens >= max_tokens or stop_reason == "length")
        prefix_preservation_status = "VERIFIED_FALSE" if is_restart else "VERIFIED_TRUE"

        # Local repair predicate
        is_genuine_local_repair = False
        if err_loc_status == "VERIFIED_TRUE" and correction_status == "VERIFIED_TRUE" and not is_restart and not is_truncated:
            if ans_status == "VERIFIED_TRUE":
                is_genuine_local_repair = True

        # Conflict check: Both explicit restart AND local repair claimed
        has_strategy_conflict = bool(is_explicit_restart and (err_loc_status == "VERIFIED_TRUE" and correction_status == "VERIFIED_TRUE"))

        # Shortcut check: Very few tokens with boxed answer
        is_shortcut_guess = bool(generated_tokens < 40 and ans_status == "VERIFIED_TRUE")

        # 5. Mutually Exclusive Strategy Assignment
        confidence = 0.95
        if has_strategy_conflict:
            overall_status = "AMBIGUOUS_RECOVERY_UNVERIFIED"
            confidence = 0.40
        elif is_truncated and ans_status != "VERIFIED_TRUE":
            overall_status = "GENERATION_LIMIT_TRUNCATION"
            confidence = 0.99
        elif is_genuine_local_repair:
            overall_status = "GENUINE_LOCAL_REPAIR"
            confidence = 0.95
        elif is_shortcut_guess:
            overall_status = "DIRECT_ANSWER_SHORTCUT"
            confidence = 0.85
        elif is_explicit_restart and ans_status == "VERIFIED_TRUE":
            overall_status = "RESTART_SUCCESS_EXPLICIT"
            confidence = 0.95
        elif is_implicit_restart and ans_status == "VERIFIED_TRUE":
            overall_status = "RESTART_SUCCESS_IMPLICIT"
            confidence = 0.90
        elif err_detect_status == "VERIFIED_TRUE" and correction_status == "VERIFIED_FALSE":
            overall_status = "HALLUCINATED_SELF_CORRECTION"
            confidence = 0.85
        elif not is_restart and ans_status == "VERIFIED_FALSE":
            overall_status = "COMPOUNDED_ERROR_CONTINUATION"
            confidence = 0.90
        elif is_restart and ans_status == "VERIFIED_FALSE":
            overall_status = "RESTART_FAILURE"
            confidence = 0.90
        elif ans_status == "VERIFIED_TRUE":
            overall_status = "LUCKY_GUESS_OR_ALTERNATIVE_PATH"
            confidence = 0.75
        else:
            overall_status = "UNVERIFIED_FAILURE"
            confidence = 0.60

        return {
            "predicted_answer": predicted_answer,
            "final_answer_correctness": ans_status,
            "error_detection": err_detect_status,
            "error_localization": err_loc_status,
            "mathematical_correction_validity": correction_status,
            "valid_prefix_preservation": prefix_preservation_status,
            "continuation_validity": "VERIFIED_FALSE" if is_truncated else "VERIFIED_TRUE",
            "is_explicit_restart": is_explicit_restart,
            "is_implicit_restart": is_implicit_restart,
            "is_restart": is_restart,
            "genuine_local_repair": is_genuine_local_repair,
            "overall_status": overall_status,
            "confidence": confidence,
            "requires_human_validation": bool(confidence < 0.70),
            "evaluator_version": "v5.1.0_adversarial_hardened"
        }

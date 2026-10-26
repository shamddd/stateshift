#!/usr/bin/env python3
"""
StateShift Strict Recovery Evaluator (Version 5 - Mission 14)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enhancements over v4:
1. Complete elimination of condition label leakage: Behavioral classification
   (is_explicit_restart, is_implicit_restart, is_local_repair) is derived
   STRICTLY from the generated tokens. Prompt condition is never used as an evaluation proxy.
2. Robust multi-pattern boxed answer extraction.
3. Explicit separation between syntactic identity, SymPy algebraic equivalence, and UNVERIFIED.
4. Mutually exclusive 7-strategy assignment based on verified behavioral predicates.
5. Strict preservation requirements for genuine local repair (error localization, valid correction, prefix preservation).
"""

import os
import re
import sys
import sympy
from typing import Dict, Any, List, Optional, Tuple

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from evaluation.symbolic_repair_verifier import SymbolicRepairVerifier
from evaluation.step_dependency_graph import StepDependencyGraph

class StrictRecoveryEvaluatorV5:
    """Strict, bias-free evaluator for mathematical reasoning recovery."""

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
        Evaluate a single reasoning rollout strictly from model output tokens.
        NO CONDITION BIAS: Condition label is not an argument to evaluate().
        """
        gold_answer = problem_input.get("gold_answer", "")
        recovery_state = problem_input.get("recovery_state", {})
        corrupted_step_idx = recovery_state.get("step_index", 1)
        target_assertion = recovery_state.get("target_assertion", "")

        predicted_answer = self.extract_boxed_answer(raw_output)
        ans_status, ans_evidence = self.evaluate_answer_correctness(predicted_answer, gold_answer)

        lines = [line.strip() for line in raw_output.split("\n") if line.strip()]
        lower_out = raw_output.lower()

        # 1. Error Detection Audit (Strict evidence: must identify or localize flaw)
        err_detect_status = "VERIFIED_FALSE"
        err_evidence = None
        has_detection_cue = any(phrase in lower_out for phrase in [
            "error in step", "mistake in step", "incorrect step",
            "the error is", "is flawed", "is incorrect", "is invalid",
            "the calculation is wrong", "the assertion is false"
        ])
        if has_detection_cue:
            err_detect_status = "VERIFIED_TRUE"
            err_evidence = "Explicit detection cue identified in generated text"

        # 2. Error Localization Audit
        err_loc_status = "VERIFIED_FALSE"
        loc_evidence = None
        target_step_patterns = [
            f"step {corrupted_step_idx}",
            f"step {corrupted_step_idx}:",
            f"step {corrupted_step_idx} is",
            f"step {corrupted_step_idx} contains"
        ]
        if any(pat in lower_out for pat in target_step_patterns):
            err_loc_status = "VERIFIED_TRUE"
            loc_evidence = f"Step index {corrupted_step_idx} localized in text"

        # 3. Mathematical Correction Validity
        correction_status = "UNVERIFIED"
        corr_evidence = None
        if target_assertion:
            norm_target = self.normalize_math_str(target_assertion)
            for line in lines:
                if any(k in line.lower() for k in ["correct", "instead", "should be", "repair"]):
                    norm_line = self.normalize_math_str(line)
                    if norm_target in norm_line:
                        correction_status = "VERIFIED_TRUE"
                        corr_evidence = line
                        break

        # 4. Behavioral Strategy Classification (STRICTLY FROM GENERATED TOKENS)
        first_chunk = "\n".join(lines[:3]).strip().lower()

        # Explicit restart marker (model explicitly states it is discarding/restarting)
        explicit_restart_markers = [
            "start over", "let's restart", "from scratch",
            "ignore the above", "disregard the above", "discard the above",
            "starting from scratch", "let's start fresh"
        ]
        is_explicit_restart = any(c in lower_out for c in explicit_restart_markers)

        # Implicit restart: model begins problem formulation de novo without acknowledging context
        implicit_triggers = [
            "to compute", "to solve", "we are given", "the given equation",
            "first, let's", "consider the problem", "let the roots be",
            "step 1: notice that", "we begin by"
        ]
        is_implicit_restart = any(first_chunk.startswith(t) or f"\n{t}" in first_chunk for t in implicit_triggers)

        # Truncation check
        is_truncated = bool(generated_tokens >= max_tokens or stop_reason == "length")

        is_restart = bool(is_explicit_restart or is_implicit_restart)

        # Prefix preservation
        prefix_preservation_status = "VERIFIED_FALSE" if is_restart else "VERIFIED_TRUE"

        # Local repair criteria
        is_genuine_local_repair = False
        if err_loc_status == "VERIFIED_TRUE" and correction_status == "VERIFIED_TRUE" and not is_restart and not is_truncated:
            if ans_status == "VERIFIED_TRUE":
                is_genuine_local_repair = True

        # Continuation validity
        continuation_status = "VERIFIED_FALSE" if is_truncated else "VERIFIED_TRUE"

        # 5. Mutually Exclusive 7-Strategy Assignment
        if is_truncated and ans_status != "VERIFIED_TRUE":
            overall_status = "GENERATION_LIMIT_TRUNCATION" # S6
        elif is_genuine_local_repair:
            overall_status = "GENUINE_LOCAL_REPAIR" # S1
        elif is_explicit_restart and ans_status == "VERIFIED_TRUE":
            overall_status = "RESTART_SUCCESS_EXPLICIT" # S2
        elif is_implicit_restart and ans_status == "VERIFIED_TRUE":
            overall_status = "RESTART_SUCCESS_IMPLICIT" # S3
        elif err_detect_status == "VERIFIED_TRUE" and correction_status == "VERIFIED_FALSE":
            overall_status = "HALLUCINATED_SELF_CORRECTION" # S5
        elif not is_restart and ans_status == "VERIFIED_FALSE":
            overall_status = "COMPOUNDED_ERROR_CONTINUATION" # S4
        elif is_restart and ans_status == "VERIFIED_FALSE":
            overall_status = "RESTART_FAILURE"
        elif ans_status == "VERIFIED_TRUE":
            overall_status = "LUCKY_GUESS_OR_ALTERNATIVE_PATH" # S7
        else:
            overall_status = "UNVERIFIED_FAILURE"

        return {
            "predicted_answer": predicted_answer,
            "final_answer_correctness": ans_status,
            "error_detection": err_detect_status,
            "error_localization": err_loc_status,
            "mathematical_correction_validity": correction_status,
            "valid_prefix_preservation": prefix_preservation_status,
            "continuation_validity": continuation_status,
            "is_explicit_restart": is_explicit_restart,
            "is_implicit_restart": is_implicit_restart,
            "is_restart": is_restart,
            "genuine_local_repair": is_genuine_local_repair,
            "overall_status": overall_status,
            "evidence_spans": {
                "final_answer": ans_evidence,
                "error_detection": {"status": err_detect_status, "evidence": err_evidence},
                "error_localization": {"status": err_loc_status, "evidence": loc_evidence},
                "correction_validity": {"status": correction_status, "evidence": corr_evidence},
                "continuation_validity": {"status": continuation_status, "is_truncated": is_truncated, "stop_reason": stop_reason, "generated_tokens": generated_tokens}
            },
            "evaluator_version": "v5.0.0_unbiased"
        }

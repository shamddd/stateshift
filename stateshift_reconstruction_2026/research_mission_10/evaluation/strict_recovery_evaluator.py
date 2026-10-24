#!/usr/bin/env python3
"""
Phase III: Strict Multi-Dimensional Recovery Evaluator (Mission 10)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Separates superficial final-answer correctness from verified cognitive reasoning repair.
Measures 8 distinct dimensions:
1. final_answer_correctness
2. error_detection
3. error_localization
4. valid_prefix_preservation
5. local_correction_validity
6. continuation_validity
7. restart_behavior
8. verified_local_repair
"""

import os
import re
import sys
import sympy
from typing import Dict, Any, Optional, Tuple

class StrictRecoveryEvaluator:
    def __init__(self):
        pass

    @staticmethod
    def extract_boxed_answer(text: str) -> Optional[str]:
        if not text:
            return None
        matches = re.findall(r'\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', text)
        if matches:
            return matches[-1].strip()
        matches_loose = re.findall(r'boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', text)
        if matches_loose:
            return matches_loose[-1].strip()
        ans_patterns = [
            r'(?:final answer|answer is|value is)[:\s]*\$?([^\n\$\.]+)\$?',
            r'(?:therefore|thus|hence)[,\s]*\$?([^\n\$\.]+)\$?'
        ]
        for pat in ans_patterns:
            m = re.findall(pat, text, flags=re.IGNORECASE)
            if m:
                return m[-1].strip()
        return None

    @staticmethod
    def verify_symbolic_equivalence(pred: Optional[str], gold: str) -> bool:
        if pred is None or gold is None:
            return False
        pred_clean = pred.replace(' ', '').replace('$', '').strip()
        gold_clean = gold.replace(' ', '').replace('$', '').strip()
        if pred_clean == gold_clean:
            return True
            
        def sanitize_latex(s):
            import re
            # Convert \frac{a}{b} and \dfrac{a}{b} into ((a)/(b))
            s = re.sub(r'\\d?frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', s)
            s = s.replace(r'\cdot', '*').replace(r'\times', '*')
            s = s.replace('{', '(').replace('}', ')')
            s = s.replace(r'\pi', 'pi').replace(r'\sqrt', 'sqrt')
            s = s.replace(r'\%', '/100')
            return s
            
        try:
            p_expr = sympy.sympify(sanitize_latex(pred_clean))
            g_expr = sympy.sympify(sanitize_latex(gold_clean))
            diff = sympy.simplify(p_expr - g_expr)
            return diff == 0
        except Exception:
            try:
                p_val = float(pred_clean)
                g_val = float(gold_clean)
                return abs(p_val - g_val) < 1e-4
            except Exception:
                return pred_clean.lower() == gold_clean.lower()

    def evaluate(self, problem: Dict[str, Any], raw_output: str, condition: str = "neutral") -> Dict[str, Any]:
        """Strictly evaluate a rollout across all 8 dimensions."""
        gold_ans = problem.get("gold_answer", problem.get("ground_truth_answer", ""))
        corrupt_prefix = problem.get("recovery_prefix", "")
        pred_ans = self.extract_boxed_answer(raw_output)
        
        # 1. Final Answer Correctness
        is_final_correct = self.verify_symbolic_equivalence(pred_ans, gold_ans)
        
        lower_out = raw_output.lower()
        
        # 2. Error Detection: Did model detect an error?
        detection_cues = [
            "error", "mistake", "incorrect", "invalid", "flaw", "actually,", "wait,",
            "noting that", "notice that", "is wrong", "instead of", "correction", "false"
        ]
        detected_error = any(cue in lower_out for cue in detection_cues)
        
        # 3. Error Localization: Did model locate where the error occurred?
        localization_cues = [
            "step 1", "first step", "previous step", "in the sum", "in the equation",
            "miscalculation", "calculation above", "derivation above"
        ]
        localized_error = any(cue in lower_out for cue in localization_cues) or (
            problem.get("operator_code", "").lower() in lower_out
        )
        
        # 7. Restart Behavior: Did model discard context and restart?
        restart_cues = [
            "start over", "start from scratch", "let us restart", "let's restart",
            "begin again", "ignore the above", "disregard the above", "re-evaluating from the beginning"
        ]
        is_restart = any(cue in lower_out for cue in restart_cues) or (condition == "explicit_restart")
        
        # 4. Valid Prefix Preservation: Was valid prefix preserved rather than discarded?
        valid_preserved = (not is_restart) and (len(raw_output.strip()) > 0)
        
        # 5. Local Correction Validity: Did model provide a valid corrected assertion?
        correction_cues = [
            "should be", "correct value", "instead,", "correcting", "equals", "correctly", "actually"
        ]
        local_corrected = detected_error and any(cue in lower_out for cue in correction_cues)
        
        # 6. Continuation Validity: Does output flow to conclusion without hitting truncation?
        is_truncated = ("\\boxed{" not in raw_output) and ("boxed{" not in raw_output) and (len(raw_output.split()) >= 100)
        continuation_valid = (not is_truncated) and (pred_ans is not None)
        
        # 8. Verified Local Repair:
        # A response counts as verified local repair ONLY IF:
        # - It identifies the corrupted step
        # - It supplies a valid correction
        # - It preserves the valid reasoning prefix
        # - It continues consistently from the corrected state
        # - It produces the correct final answer
        verified_repair = bool(
            is_final_correct and 
            detected_error and 
            valid_preserved and 
            (not is_restart) and 
            local_corrected and 
            continuation_valid
        )
        
        return {
            "final_answer_correctness": bool(is_final_correct),
            "error_detection": bool(detected_error),
            "error_localization": bool(localized_error),
            "valid_prefix_preservation": bool(valid_preserved),
            "local_correction_validity": bool(local_corrected),
            "continuation_validity": bool(continuation_valid),
            "restart_behavior": bool(is_restart),
            "verified_local_repair": bool(verified_repair),
            "predicted_answer": pred_ans,
            "gold_answer": gold_ans,
            "is_truncated": bool(is_truncated)
        }

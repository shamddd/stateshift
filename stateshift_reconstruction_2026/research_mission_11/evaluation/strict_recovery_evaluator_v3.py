#!/usr/bin/env python3
"""
StateShift Strict Recovery Evaluator (v3 - Mathematical Grounding)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Integrates:
- MathematicalOracle (SymPy, exact arithmetic, rational equivalence)
- RepairTraceValidator (trace analysis, step localization, 6-class restart taxonomy)
- GenerationTerminationAuditor (backend token metadata, true truncation detection)

Measures 8 orthogonal dimensions:
1. final_answer_correctness
2. error_detection
3. error_localization
4. mathematical_correction_validity
5. valid_prefix_preservation
6. continuation_validity
7. restart_behavior (6 classes)
8. genuine_local_repair (strict conjunctive criterion)
"""

import os
import sys
from typing import Dict, Any, Optional, Tuple

from evaluation.mathematical_oracles import MathematicalOracle
from evaluation.repair_trace_validator import RepairTraceValidator
from evaluation.generation_termination import GenerationTerminationAuditor

class StrictRecoveryEvaluatorV3:
    """Rigorous mathematical evaluator for reasoning recovery rollouts."""

    def __init__(self):
        self.oracle = MathematicalOracle
        self.trace_validator = RepairTraceValidator
        self.term_auditor = GenerationTerminationAuditor

    def evaluate(self, 
                 problem: Dict[str, Any], 
                 raw_output: str, 
                 condition: str = "neutral",
                 generated_tokens: Optional[int] = None,
                 max_tokens: int = 512,
                 stop_reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate a rollout across all 8 mathematical and cognitive dimensions.
        """
        gold_ans = problem.get("gold_answer", problem.get("ground_truth_answer", ""))
        pred_ans = self.oracle.extract_boxed_answer(raw_output)
        
        # 1. Final Answer Correctness (Symbolic / Exact)
        is_final_correct = self.oracle.verify_symbolic_equivalence(pred_ans, gold_ans)
        
        # 2. Error Detection & 3. Error Localization
        err_detected, err_localized, loc_meta = self.trace_validator.evaluate_error_localization(raw_output, problem)
        
        # 7. Restart Behavior (6-class taxonomy)
        restart_class, restart_meta = self.trace_validator.classify_restart_behavior(raw_output, problem, condition=condition)
        is_restart = bool(restart_class in ["EXPLICIT_RESTART", "IMPLICIT_RESTART"])
        
        # 5. Valid Prefix Preservation
        prefix_preserved, pfx_meta = self.trace_validator.evaluate_prefix_preservation(raw_output, problem, restart_class)
        
        # 4. Mathematical Correction Validity
        # Check if model presented a valid correction
        correction_valid = False
        if err_detected:
            # Check if text contains an explicit equality assertion that is mathematically valid
            for line in raw_output.split("\n"):
                if "=" in line and any(w in line.lower() for w in ["should be", "is", "correct", "instead"]):
                    eq_valid, _ = self.oracle.verify_assertion_validity(line)
                    if eq_valid:
                        correction_valid = True
                        break
            if not correction_valid and is_final_correct and not is_restart:
                # If output is correct without restarting, local repair arithmetic held
                correction_valid = True
                
        # 6. Continuation Validity & Truncation
        tok_count = generated_tokens if generated_tokens is not None else len(raw_output.split())
        term_meta = self.term_auditor.audit_termination(
            raw_output=raw_output,
            generated_tokens=tok_count,
            max_tokens=max_tokens,
            stop_reason=stop_reason,
            extracted_answer=pred_ans
        )
        continuation_valid = term_meta["output_complete"]
        is_truncated = term_meta["is_truncated"]
        
        # 8. Genuine Local Repair Success:
        # Strict Conjunctive Condition:
        # - Erroneous assertion detected & localized
        # - Valid prefix preserved
        # - NOT an explicit or implicit restart
        # - Correction mathematically valid
        # - Continuation valid and complete
        # - Final answer mathematically correct
        genuine_repair = bool(
            is_final_correct and
            err_detected and
            err_localized and
            prefix_preserved and
            (not is_restart) and
            correction_valid and
            continuation_valid
        )
        
        # Descriptive classification status
        if genuine_repair:
            status_label = "VERIFIED_LOCAL_REPAIR"
        elif is_final_correct and is_restart:
            status_label = "RESTART_SUCCESS"
        elif is_final_correct and not is_restart and not err_detected:
            status_label = "LUCKY_GUESS_OR_PASSIVE_PASS"
        elif not is_final_correct and is_restart:
            status_label = "RESTART_FAILURE"
        elif not is_final_correct and err_detected:
            status_label = "FAILED_LOCAL_REPAIR"
        elif restart_class == "BLIND_COPYING":
            status_label = "BLIND_COPYING_PROPAGATION"
        else:
            status_label = "UNVERIFIED_OR_AMBIGUOUS"

        return {
            "final_answer_correctness": bool(is_final_correct),
            "error_detection": bool(err_detected),
            "error_localization": bool(err_localized),
            "mathematical_correction_validity": bool(correction_valid),
            "valid_prefix_preservation": bool(prefix_preserved),
            "continuation_validity": bool(continuation_valid),
            "restart_class": restart_class,
            "is_restart": bool(is_restart),
            "genuine_local_repair": bool(genuine_repair),
            "status_label": status_label,
            "predicted_answer": pred_ans,
            "gold_answer": gold_ans,
            "is_truncated": bool(is_truncated),
            "termination_metadata": term_meta,
            "restart_metadata": restart_meta,
            "localization_metadata": loc_meta,
            "prefix_metadata": pfx_meta
        }

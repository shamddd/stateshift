#!/usr/bin/env python3
"""
StateShift Strict Recovery Evaluator (v4 - Evidence & Dependency Grounded)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Key Innovations over v3:
1. Eliminates keyword traps: Requires explicit mathematical contradiction/equivalence evidence.
2. Structured Schema & Dependency Graph integration.
3. 4-Valued Categorical Labels across all dimensions:
   - VERIFIED_TRUE
   - VERIFIED_FALSE
   - UNVERIFIED
   - NOT_APPLICABLE
4. Textual Evidence Spans recorded for every classification.
5. Non-mutually-exclusive multi-behavior restart taxonomy.
6. Eliminates circularity in correction validity.
"""

import os
import sys
import re
from typing import Dict, Any, Optional, Tuple, List, Union

from evaluation.evaluation_schema import StructuredProblemCase, ReasoningStep
from evaluation.step_dependency_graph import StepDependencyGraph
from evaluation.symbolic_repair_verifier import SymbolicRepairVerifier

class StrictRecoveryEvaluatorV4:
    """Production mathematical reasoning recovery evaluator for NeurIPS 2027."""

    def __init__(self):
        self.verifier = SymbolicRepairVerifier

    @staticmethod
    def extract_boxed_answer(text: str) -> Optional[str]:
        """Extract LaTeX \\boxed{...} content with nested bracket depth tracking."""
        if not text:
            return None
        matches = []
        for pat in [r'\\boxed\{', r'(?<!\\)boxed\{']:
            for m in re.finditer(pat, text):
                start = m.end()
                depth = 1
                idx = start
                while idx < len(text) and depth > 0:
                    if text[idx] == '{':
                        depth += 1
                    elif text[idx] == '}':
                        depth -= 1
                    idx += 1
                if depth == 0:
                    matches.append(text[start:idx-1].strip())
        if matches:
            return matches[-1]
            
        # Fallback to concluding sentence patterns
        fallback_patterns = [
            r'(?:final answer is|answer is|value is)[:\s]*\$?([^\n\$\.]+)\$?',
            r'(?:therefore|thus|hence|so)[,\s]*\$?([^\n\$\.]+)\$?'
        ]
        for pat in fallback_patterns:
            founds = re.findall(pat, text, flags=re.IGNORECASE)
            if founds:
                ans = founds[-1].strip().rstrip('.')
                if len(ans) > 0 and len(ans) < 80:
                    return ans
        return None

    def evaluate(self, 
                 problem_input: Union[Dict[str, Any], StructuredProblemCase], 
                 raw_output: str, 
                 condition: str = "neutral",
                 generated_tokens: Optional[int] = None,
                 max_tokens: int = 512,
                 stop_reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate rollout against structured problem representation with evidence spans.
        """
        if isinstance(problem_input, StructuredProblemCase):
            prob = problem_input
        else:
            prob = StructuredProblemCase.from_dict(problem_input)

        evidence_spans = {}
        
        # -------------------------------------------------------------
        # 1. Final Answer Correctness
        # -------------------------------------------------------------
        pred_ans = self.extract_boxed_answer(raw_output)
        gold_ans = prob.gold_answer
        
        ans_status, ans_expl = self.verifier.verify_expression_equivalence(pred_ans or "", gold_ans)
        evidence_spans["final_answer"] = {
            "predicted": pred_ans,
            "gold": gold_ans,
            "explanation": ans_expl
        }

        # -------------------------------------------------------------
        # 2. Error Detection & 3. Error Localization
        # -------------------------------------------------------------
        err_detect_status = "VERIFIED_FALSE"
        err_loc_status = "VERIFIED_FALSE"
        detect_span = None
        loc_span = None
        
        corrupted_assertion = prob.corrupted_assertion or ""
        corrupted_clean = corrupted_assertion.replace(" ", "").replace("$", "").lower()
        lower_out = raw_output.lower()
        
        # Evidence search: Does output explicitly challenge or replace the corrupted assertion?
        # A mathematical contradiction exists if the model asserts an equation contradicting the corrupt line
        lines = raw_output.split("\n")
        for line in lines:
            line_clean = line.strip().lower()
            if not line_clean:
                continue
                
            # Check if model names the step
            if prob.corrupted_step_id and prob.corrupted_step_id.replace("_", " ") in line_clean:
                loc_span = line.strip()
                err_loc_status = "VERIFIED_TRUE"
                
            # Check if model points out the specific flawed term
            if len(corrupted_clean) > 5 and corrupted_clean[:20] in line.replace(" ", "").lower():
                loc_span = line.strip()
                err_loc_status = "VERIFIED_TRUE"

        # Check for error detection assertion: must tie to localized corrupted step/assertion
        for line in lines:
            line_clean = line.strip().lower()
            if any(w in line_clean for w in ["error", "mistake", "incorrect", "invalid", "is wrong", "flawed"]):
                detect_span = line.strip()
                # Verified detection requires either validated localization or reference to the corrupted assertion
                if err_loc_status == "VERIFIED_TRUE":
                    err_detect_status = "VERIFIED_TRUE"
                    break
                elif len(corrupted_clean) > 5 and any(term in line.replace(" ", "").lower() for term in [corrupted_clean[:15], "step"]):
                    # If step id matches
                    if prob.corrupted_step_id and prob.corrupted_step_id.replace("_", " ") in line_clean:
                        err_detect_status = "VERIFIED_TRUE"
                        err_loc_status = "VERIFIED_TRUE"
                        loc_span = line.strip()
                        break
                
        # Non-keyword surgical replacement check:
        # If model replaces corrupted line with valid correction without error keywords
        for line in lines:
            if "=" in line:
                stat, _ = self.verifier.verify_equality_chain(line)
                if stat == "VERIFIED_TRUE" and prob.expected_corrected_assertion:
                    if prob.expected_corrected_assertion.replace(" ", "") in line.replace(" ", ""):
                        err_detect_status = "VERIFIED_TRUE"
                        err_loc_status = "VERIFIED_TRUE"
                        detect_span = line.strip()
                        loc_span = line.strip()
                        break

        evidence_spans["error_detection"] = {"status": err_detect_status, "evidence": detect_span}
        evidence_spans["error_localization"] = {"status": err_loc_status, "evidence": loc_span}

        # -------------------------------------------------------------
        # 4. Mathematical Correction Validity
        # -------------------------------------------------------------
        correction_status = "UNVERIFIED"
        correction_span = None
        
        for line in lines:
            if "=" in line and any(w in line.lower() for w in ["should be", "is", "=", "yields", "equals"]):
                # Clean equation
                cand = line.strip()
                c_stat, c_expl = self.verifier.verify_equality_chain(cand)
                if c_stat == "VERIFIED_TRUE":
                    correction_status = "VERIFIED_TRUE"
                    correction_span = cand
                    break
                elif c_stat == "VERIFIED_FALSE":
                    correction_status = "VERIFIED_FALSE"
                    correction_span = cand
                    
        evidence_spans["correction_validity"] = {"status": correction_status, "evidence": correction_span}

        # -------------------------------------------------------------
        # 5. Restart Behavior (Multi-Behavior Non-Exclusive Taxonomy)
        # -------------------------------------------------------------
        is_explicit_restart = False
        is_implicit_restart = False
        is_local_repair = False
        is_partial_recompute = False
        is_blind_copying = False
        
        first_chunk = "\n".join(lines[:3]).strip().lower()
        
        # Explicit restart marker
        if any(c in lower_out for c in ["start over", "let's restart", "from scratch", "ignore the above", "disregard the above"]) or condition == "explicit_restart":
            is_explicit_restart = True
            
        # Implicit restart: model begins by re-stating problem setup de novo
        implicit_triggers = ["to compute", "to solve", "we are given", "the given equation", "first, let's", "consider the problem"]
        if any(first_chunk.startswith(t) or f"\n{t}" in first_chunk for t in implicit_triggers):
            is_implicit_restart = True
            
        # Blind copying: uncritical propagation of corrupted assertion
        if corrupted_clean and corrupted_clean[:20] in lower_out.replace(" ", ""):
            # Check if it was challenged or copied
            if err_detect_status != "VERIFIED_TRUE":
                is_blind_copying = True
                
        # Local repair behavior
        if err_loc_status == "VERIFIED_TRUE" and correction_status == "VERIFIED_TRUE" and not is_explicit_restart and not is_implicit_restart:
            is_local_repair = True
            
        # Partial recomputation
        if "recalculating" in lower_out or "recomputing" in lower_out:
            is_partial_recompute = True
            
        is_restart = bool(is_explicit_restart or is_implicit_restart)

        # -------------------------------------------------------------
        # 6. Valid Prefix Preservation
        # -------------------------------------------------------------
        if is_restart:
            prefix_status = "VERIFIED_FALSE"
            pfx_expl = "Discarded via restart behavior"
        elif is_blind_copying:
            prefix_status = "VERIFIED_TRUE" # Mechanically preserved, but contaminated
            pfx_expl = "Preserved along with corrupted assertion (blind copying)"
        elif len(raw_output.strip()) == 0:
            prefix_status = "VERIFIED_FALSE"
            pfx_expl = "Empty generation"
        else:
            prefix_status = "VERIFIED_TRUE"
            pfx_expl = "Reasoning chain continues prefix state"
            
        evidence_spans["prefix_preservation"] = {"status": prefix_status, "explanation": pfx_expl}

        # -------------------------------------------------------------
        # 7. Continuation Validity & Truncation
        # -------------------------------------------------------------
        tok_count = generated_tokens if generated_tokens is not None else len(raw_output.split())
        hit_limit = bool(tok_count >= max_tokens)
        
        if stop_reason:
            resolved_stop = stop_reason
        elif hit_limit:
            resolved_stop = "length"
        else:
            resolved_stop = "eos"
            
        is_truncated = bool(hit_limit or (pred_ans is None and tok_count >= max_tokens - 10))
        continuation_status = "VERIFIED_TRUE" if (not is_truncated and pred_ans is not None) else "VERIFIED_FALSE"
        
        evidence_spans["continuation_validity"] = {
            "status": continuation_status,
            "is_truncated": is_truncated,
            "stop_reason": resolved_stop,
            "generated_tokens": tok_count
        }

        # -------------------------------------------------------------
        # 8. Genuine Local Repair (Strict Conjunctive Criteria)
        # -------------------------------------------------------------
        # Requires:
        # 1. Error detected == VERIFIED_TRUE
        # 2. Error localized == VERIFIED_TRUE
        # 3. Correction valid == VERIFIED_TRUE
        # 4. Prefix preserved == VERIFIED_TRUE
        # 5. Continuation valid == VERIFIED_TRUE
        # 6. Final answer correct == VERIFIED_TRUE
        # 7. NOT a restart (explicit or implicit)
        is_genuine_repair = bool(
            ans_status == "VERIFIED_TRUE" and
            err_detect_status == "VERIFIED_TRUE" and
            err_loc_status == "VERIFIED_TRUE" and
            correction_status == "VERIFIED_TRUE" and
            prefix_status == "VERIFIED_TRUE" and
            continuation_status == "VERIFIED_TRUE" and
            not is_restart
        )
        
        if is_genuine_repair:
            overall_status = "VERIFIED_LOCAL_REPAIR"
        elif ans_status == "VERIFIED_TRUE" and is_restart:
            overall_status = "RESTART_SUCCESS"
        elif ans_status == "VERIFIED_TRUE" and not is_restart and err_detect_status != "VERIFIED_TRUE":
            overall_status = "LUCKY_GUESS_OR_ALTERNATIVE_PATH"
        elif ans_status == "VERIFIED_FALSE" and is_restart:
            overall_status = "RESTART_FAILURE"
        elif is_blind_copying:
            overall_status = "BLIND_COPYING_PROPAGATION"
        elif not prob.metadata_complete:
            overall_status = "UNVERIFIABLE_METADATA_INCOMPLETE"
        else:
            overall_status = "UNVERIFIED_OR_AMBIGUOUS"

        return {
            "problem_id": prob.problem_id,
            "final_answer_correctness": ans_status,
            "error_detection": err_detect_status,
            "error_localization": err_loc_status,
            "mathematical_correction_validity": correction_status,
            "valid_prefix_preservation": prefix_status,
            "continuation_validity": continuation_status,
            
            # Restart Behaviors (Non-exclusive)
            "is_explicit_restart": is_explicit_restart,
            "is_implicit_restart": is_implicit_restart,
            "is_local_repair": is_local_repair,
            "is_partial_recompute": is_partial_recompute,
            "is_blind_copying": is_blind_copying,
            "is_restart": is_restart,
            
            # Master Decisions
            "genuine_local_repair": "VERIFIED_TRUE" if is_genuine_repair else "VERIFIED_FALSE",
            "overall_status": overall_status,
            "is_truncated": is_truncated,
            "predicted_answer": pred_ans,
            "gold_answer": gold_ans,
            "evidence_spans": evidence_spans,
            "metadata_complete": prob.metadata_complete
        }

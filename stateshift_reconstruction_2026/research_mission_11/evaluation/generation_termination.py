#!/usr/bin/env python3
"""
StateShift Generation Termination & Truncation Evaluator (v3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Replaces naive length and string heuristics with rigorous backend termination metadata:
- max_new_tokens
- generated_token_count
- eos_token_observed
- stop_reason (eos, length, stop_sequence, exception)
- hit_generation_limit
- answer_extracted
- output_complete
"""

import re
from typing import Dict, Any, Optional, Tuple

class GenerationTerminationAuditor:
    """Audits and classifies generation termination behavior."""

    @staticmethod
    def audit_termination(raw_output: str, 
                          generated_tokens: int, 
                          max_tokens: int,
                          eos_token_observed: Optional[bool] = None,
                          stop_reason: Optional[str] = None,
                          extracted_answer: Optional[str] = None) -> Dict[str, Any]:
        """
        Determines complete vs. truncated generation using backend metadata.
        """
        # 1. Did the generation hit the token limit?
        # Exact ceiling hit: generated_tokens >= max_tokens
        hit_generation_limit = bool(generated_tokens >= max_tokens)
        
        # 2. Stop Reason determination
        if stop_reason:
            resolved_stop_reason = stop_reason
        elif hit_generation_limit:
            resolved_stop_reason = "length"
        elif eos_token_observed:
            resolved_stop_reason = "eos"
        elif eos_token_observed is False and not hit_generation_limit:
            resolved_stop_reason = "stop_sequence"
        else:
            # Fallback based on sentence completion and boxed presence
            trimmed = raw_output.strip()
            ends_with_punc = trimmed.endswith(('.', '}', '$', ']', ')'))
            has_boxed = bool(r'\boxed{' in raw_output or 'boxed{' in raw_output)
            if has_boxed and ends_with_punc and not hit_generation_limit:
                resolved_stop_reason = "eos"
            elif hit_generation_limit:
                resolved_stop_reason = "length"
            else:
                resolved_stop_reason = "unspecified_end"

        # 3. Answer extracted?
        has_answer = extracted_answer is not None and len(extracted_answer.strip()) > 0
        
        # 4. Output Complete?
        # A rollout is complete IF:
        # - It did NOT hit the generation token limit, AND
        # - It extracted a final answer, AND
        # - It cleanly closed its LaTeX and syntactic structures
        output_complete = bool((not hit_generation_limit) and has_answer)
        
        # 5. Is Truncated?
        # Truncated means the reasoning flow was forcibly severed by max_tokens or premature cut
        is_truncated = bool(hit_generation_limit or (not has_answer and generated_tokens >= (max_tokens - 5)))

        return {
            "max_new_tokens": max_tokens,
            "generated_token_count": generated_tokens,
            "eos_token_observed": bool(resolved_stop_reason == "eos"),
            "stop_reason": resolved_stop_reason,
            "hit_generation_limit": hit_generation_limit,
            "answer_extracted": has_answer,
            "output_complete": output_complete,
            "is_truncated": is_truncated
        }

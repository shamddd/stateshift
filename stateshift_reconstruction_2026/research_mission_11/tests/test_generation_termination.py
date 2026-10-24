#!/usr/bin/env python3
"""
Unit Tests for Generation Termination & Truncation Auditor (v3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Enforces all 6 mandatory termination test scenarios specified in Mission 11 Section 7:
1. Generation ends at EOS.
2. Generation reaches maximum token limit.
3. Generation stops on a configured stop sequence.
4. Generation produces a final answer without boxing.
5. Generation produces a boxed answer but continues.
6. Generation produces no extractable answer.
"""

import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.generation_termination import GenerationTerminationAuditor
from evaluation.mathematical_oracles import MathematicalOracle

class TestGenerationTermination(unittest.TestCase):
    def setUp(self):
        self.auditor = GenerationTerminationAuditor

    def test_01_generation_ends_at_eos(self):
        """Scenario 1: Generation cleanly terminates before max_tokens with EOS."""
        raw = "The answer is 42. Thus, \\boxed{42}."
        meta = self.auditor.audit_termination(
            raw_output=raw,
            generated_tokens=150,
            max_tokens=512,
            eos_token_observed=True,
            stop_reason="eos",
            extracted_answer="42"
        )
        self.assertTrue(meta["eos_token_observed"])
        self.assertEqual(meta["stop_reason"], "eos")
        self.assertFalse(meta["hit_generation_limit"])
        self.assertTrue(meta["output_complete"])
        self.assertFalse(meta["is_truncated"])

    def test_02_generation_reaches_maximum_token_limit(self):
        """Scenario 2: Generation hits max token ceiling mid-proof."""
        raw = "Step 1: x = 5. Step 2: y = 10. Step 3: compute sum x + y... let us now"
        meta = self.auditor.audit_termination(
            raw_output=raw,
            generated_tokens=512,
            max_tokens=512,
            eos_token_observed=False,
            stop_reason="length",
            extracted_answer=None
        )
        self.assertFalse(meta["eos_token_observed"])
        self.assertEqual(meta["stop_reason"], "length")
        self.assertTrue(meta["hit_generation_limit"])
        self.assertFalse(meta["output_complete"])
        self.assertTrue(meta["is_truncated"])

    def test_03_generation_stops_on_configured_stop_sequence(self):
        """Scenario 3: Generation stops when hitting user stop token (e.g. '<|im_end|>')."""
        raw = "Therefore the value is \\boxed{7}."
        meta = self.auditor.audit_termination(
            raw_output=raw,
            generated_tokens=85,
            max_tokens=512,
            eos_token_observed=False,
            stop_reason="stop_sequence",
            extracted_answer="7"
        )
        self.assertEqual(meta["stop_reason"], "stop_sequence")
        self.assertFalse(meta["hit_generation_limit"])
        self.assertTrue(meta["answer_extracted"])
        self.assertTrue(meta["output_complete"])
        self.assertFalse(meta["is_truncated"])

    def test_04_generation_produces_final_answer_without_boxing(self):
        """Scenario 4: Complete derivation where answer is written without LaTeX \\boxed{}."""
        raw = "After simplifying the quadratic equation, we find that the final answer is 14."
        ans = MathematicalOracle.extract_boxed_answer(raw)
        self.assertEqual(ans, "14")
        meta = self.auditor.audit_termination(
            raw_output=raw,
            generated_tokens=120,
            max_tokens=512,
            eos_token_observed=True,
            extracted_answer=ans
        )
        self.assertTrue(meta["answer_extracted"])
        self.assertTrue(meta["output_complete"])
        self.assertFalse(meta["is_truncated"])

    def test_05_generation_produces_boxed_answer_but_continues(self):
        """Scenario 5: Derivation produces intermediate boxed formula but cleanly concludes."""
        raw = "We first note that \\boxed{a^2 + b^2 = c^2}. Substituting c=5 gives the final value \\boxed{25}."
        ans = MathematicalOracle.extract_boxed_answer(raw)
        self.assertEqual(ans, "25")
        meta = self.auditor.audit_termination(
            raw_output=raw,
            generated_tokens=90,
            max_tokens=512,
            eos_token_observed=True,
            extracted_answer=ans
        )
        self.assertTrue(meta["output_complete"])
        self.assertFalse(meta["is_truncated"])

    def test_06_generation_produces_no_extractable_answer(self):
        """Scenario 6: Incomplete or rambling output where no answer can be extracted."""
        raw = "Let x be a real number such that x > 0. We consider the function f(x) = log(x)."
        ans = MathematicalOracle.extract_boxed_answer(raw)
        self.assertIsNone(ans)
        meta = self.auditor.audit_termination(
            raw_output=raw,
            generated_tokens=200,
            max_tokens=512,
            eos_token_observed=True,
            extracted_answer=ans
        )
        self.assertFalse(meta["answer_extracted"])
        self.assertFalse(meta["output_complete"])

if __name__ == "__main__":
    unittest.main()

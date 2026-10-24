#!/usr/bin/env python3
"""
StateShift Evaluation Schema (v4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Defines structured problem, dependency, and evaluation case representations.
Explicitly flags missing or partial metadata for historical datasets.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict

@dataclass
class ReasoningStep:
    step_id: str
    assertion_text: str
    is_valid: bool
    depends_on: List[str] = field(default_factory=list)
    variables_defined: List[str] = field(default_factory=list)

@dataclass
class StructuredProblemCase:
    problem_id: str
    problem_statement: str
    gold_answer: str
    difficulty_level: int = 3
    subject: str = "Algebra"
    domain_assumptions: List[str] = field(default_factory=list)
    
    # State-Dependent Reasoning Schema
    valid_prefix_steps: List[ReasoningStep] = field(default_factory=list)
    corrupted_step_id: Optional[str] = None
    corrupted_assertion: Optional[str] = None
    expected_corrected_assertion: Optional[str] = None
    downstream_dependencies: List[str] = field(default_factory=list)
    operator_code: Optional[str] = None
    
    # Metadata Provenance
    metadata_complete: bool = True
    missing_fields: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuredProblemCase":
        prob_id = data.get("problem_id", data.get("bench_id", "unknown"))
        prob_stmt = data.get("problem_statement", data.get("problem_text", ""))
        gold_ans = data.get("gold_answer", data.get("ground_truth_answer", ""))
        
        missing = []
        if not prob_stmt:
            missing.append("problem_statement")
        if not gold_ans:
            missing.append("gold_answer")
            
        corrupt_step = None
        corrupt_assertion = None
        expected_correction = None
        
        rec_state = data.get("recovery_state", {})
        if rec_state:
            corrupt_step = f"step_{rec_state.get('step_index', 1)}"
            corrupt_assertion = rec_state.get("target_assertion")
        elif "recovery_prefix" in data:
            corrupt_assertion = data.get("recovery_prefix")
        else:
            missing.append("corrupted_assertion")
            
        if not corrupt_assertion:
            missing.append("corrupted_assertion")
            
        # Parse prefix steps
        valid_steps = []
        pfx_text = data.get("control_prefix", "")
        if pfx_text:
            for idx, line in enumerate(pfx_text.split("\n")):
                line_str = line.strip()
                if line_str:
                    valid_steps.append(ReasoningStep(
                        step_id=f"step_{idx+1}",
                        assertion_text=line_str,
                        is_valid=True
                    ))
        else:
            missing.append("valid_prefix_steps")

        return cls(
            problem_id=prob_id,
            problem_statement=prob_stmt,
            gold_answer=str(gold_ans),
            difficulty_level=data.get("difficulty_level", 3),
            subject=data.get("subject", "Algebra"),
            domain_assumptions=data.get("domain_assumptions", ["x in Reals"]),
            valid_prefix_steps=valid_steps,
            corrupted_step_id=corrupt_step,
            corrupted_assertion=corrupt_assertion,
            expected_corrected_assertion=data.get("expected_corrected_assertion"),
            downstream_dependencies=data.get("downstream_dependencies", []),
            operator_code=data.get("operator_code", "UNKNOWN"),
            metadata_complete=(len(missing) == 0),
            missing_fields=missing
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

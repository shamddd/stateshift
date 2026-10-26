#!/usr/bin/env python3
"""
StateShift Step Dependency Graph (v4)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference

Models reasoning sequences as Directed Acyclic Graphs (DAGs) to track:
- Antecedent dependencies for every mathematical assertion.
- Contamination propagation: Does step j rely on corrupted step k?
- Independence verification: Does the repaired continuation connect to the valid prefix?
"""

from typing import Dict, Any, List, Set, Optional, Tuple

def compute_contamination_fraction(dependent_steps: int, total_steps: int) -> float:
    """Safe calculation of downstream dependency contamination fraction."""
    if total_steps <= 0:
        return 0.0
    return float(min(1.0, max(0.0, dependent_steps / total_steps)))

class StepDependencyGraph:
    """DAG representation of mathematical derivations and dependencies."""

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, Set[str]] = {} # node -> set of antecedent nodes it depends on
        self.reverse_edges: Dict[str, Set[str]] = {} # node -> set of downstream nodes depending on it

    def add_step(self, step_id: str, assertion: str, is_valid: bool = True, depends_on: Optional[List[str]] = None):
        deps = set(depends_on) if depends_on else set()
        self.nodes[step_id] = {
            "assertion": assertion,
            "is_valid": is_valid
        }
        self.edges[step_id] = deps
        if step_id not in self.reverse_edges:
            self.reverse_edges[step_id] = set()
            
        for d in deps:
            if d not in self.reverse_edges:
                self.reverse_edges[d] = set()
            self.reverse_edges[d].add(step_id)

    def is_contaminated(self, step_id: str, corrupted_step_id: str) -> bool:
        """Check if step_id topologically depends on the corrupted_step_id."""
        if step_id == corrupted_step_id:
            return True
            
        visited = set()
        queue = list(self.edges.get(step_id, []))
        
        while queue:
            curr = queue.pop(0)
            if curr == corrupted_step_id:
                return True
            if curr not in visited:
                visited.add(curr)
                queue.extend(list(self.edges.get(curr, [])))
                
        return False

    def verify_repair_continuity(self, 
                                 corrupted_step_id: str, 
                                 repair_step_id: str, 
                                 conclusion_step_id: str) -> Tuple[bool, str]:
        """
        Verifies that:
        1. conclusion_step_id depends on repair_step_id.
        2. conclusion_step_id does NOT depend on corrupted_step_id.
        """
        if corrupted_step_id in self.nodes and self.is_contaminated(conclusion_step_id, corrupted_step_id):
            return False, f"Conclusion {conclusion_step_id} still depends on corrupted step {corrupted_step_id}"
            
        # Check that repair step was actually consumed downstream
        visited = set()
        queue = list(self.edges.get(conclusion_step_id, []))
        consumed_repair = False
        while queue:
            curr = queue.pop(0)
            if curr == repair_step_id:
                consumed_repair = True
                break
            if curr not in visited:
                visited.add(curr)
                queue.extend(list(self.edges.get(curr, [])))
                
        if not consumed_repair:
            return False, f"Conclusion {conclusion_step_id} bypassed repair step {repair_step_id}"
            
        return True, "Valid repair continuity confirmed"

    def compute_contamination_fraction(self, corrupted_step_id: str, downstream_step_ids: List[str]) -> Tuple[float, int, int]:
        """
        Computes:
        contamination_fraction = number_of_downstream_dependent_steps / number_of_downstream_steps
        Handling zero-denominator:
        If total downstream steps == 0, returns (0.0, 0, 0).
        """
        if not downstream_step_ids:
            return 0.0, 0, 0
            
        dependent_count = sum(1 for sid in downstream_step_ids if self.is_contaminated(sid, corrupted_step_id))
        total_count = len(downstream_step_ids)
        frac = dependent_count / total_count
        return frac, dependent_count, total_count

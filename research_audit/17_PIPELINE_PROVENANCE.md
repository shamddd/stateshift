# StateShift End-to-End Pipeline Provenance Architecture

**Audit Date**: October 18, 2026  
**Auditor**: Lead Systems & ML Infrastructure Engineer  

---

## 1. Experimental Pipeline DAG

The end-to-end StateShift research pipeline is structured as an immutable directed acyclic graph (DAG):

```
[MATH-500 Canonical Dataset] 
             │
             ▼
[Decontamination Audit & Human Adjudication] ──► confirmatory_problem_registry.json (N=454)
             │
             ├────────────────────────────────────────────────┐
             ▼                                                ▼
   Recovery Prefix Generation                        Control Prefix Matching
   (P_{i,R}: Invalid Step Injected)                  (P_{i,C}: Length-Matched Valid Step)
             │                                                │
             └───────────────────────┬────────────────────────┘
                                     │
                                     ▼
                    [Inference Dispatch Engine (vLLM)]
                    ├── Base Model: Qwen2.5-7B (t=0)
                    └── DeepScaleR Lineage: Steps 32, 64, ..., 256
                                     │
                                     ▼
                    [Deterministic Answer Verifier]
                    (Extract \boxed{...} + SymPy Equivalence)
                                     │
                                     ▼
                    controlled_endpoint_outcomes.csv (29,056 rows)
                    intermediate_rollouts.jsonl (checkpoints 32..224)
                                     │
                                     ▼
                    [Problem-Blocked Bootstrap Analysis]
                    (stateshift/statistics/bootstrap.py, B=10,000)
                                     │
                                     ▼
                    endpoint_summary_numbers.csv & figures/
```

---

## 2. Component Specifications

1. **Task Registry (`confirmatory_problem_registry.json`)**: Contains 454 pre-registered items, each specifying `problem_id`, `question`, `ground_truth_answer`, `recovery_prefix`, and `control_prefix`.
2. **Inference Parameters**:
   - `temperature`: 0.6
   - `top_p`: 0.95
   - `max_new_tokens`: 4,096
   - `system_prompt`: Standard DeepScaleR mathematical reasoning system prompt.
3. **Outcome Recording**:
   - Every rollout logs `pair_id`, `state_type`, `checkpoint_t`, `target_transition_success`, `generated_token_count`, and `raw_output_text`.

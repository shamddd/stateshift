# 03. Blind Human-Reference Validation Protocol

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Annotation Packet**: [`03_HUMAN_ANNOTATION_PACKET.csv`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/03_HUMAN_ANNOTATION_PACKET.csv) ($N = 60$ Randomized Traces)  

---

## 1. Principles of Independent Verification

In accordance with Section 4 instructions:
> *An LLM reviewing its own generated labels does not constitute independent human annotation.*  
> *If an actual independent human annotator is unavailable, prepare the annotation packet and report: **HUMAN VALIDATION PENDING**.*

To ensure zero circularity or self-fulfilling bias:
1. **Full Blinding**: The packet strips model name, temperature, generation budget, prompt condition (`Condition_A`, `D`, `E`, `F`), and previous evaluator ratings.
2. **Order Randomization**: Presentation order is randomly shuffled (seed 42) so annotators cannot identify paired contrasts.
3. **Explicit Mathematical Justification**: Annotators must cite the specific equation or line justifying each label.

---

## 2. Standardized Annotation Guidelines

For each trace, independent reviewers evaluate:
- **`human_final_correct`**: Is the final boxed answer mathematically equivalent to `gold_answer`? (Yes / No).
- **`human_error_detected`**: Does the trace demonstrate recognition of an inconsistency? (Yes / No).
- **`human_error_localized`**: Does the trace target the specific injected flaw? (Yes / No).
- **`human_prefix_preserved`**: Are earlier valid derivation steps retained without contradictory resets? (Yes / No).
- **`human_restart_behavior`**:
  - `EXPLICIT_RESTART`: Explicit directive to discard.
  - `IMPLICIT_RESTART`: Re-deriving from line 1 de novo.
  - `LOCAL_REPAIR`: Continuing from corrupted step with surgical fix.
  - `BLIND_COPY`: Propagating corrupted step as fact.
  - `AMBIGUOUS`: Inconclusive trace.
- **`human_genuine_repair`**: Does the trace satisfy all 5 requirements of verified local repair? (Yes / No).

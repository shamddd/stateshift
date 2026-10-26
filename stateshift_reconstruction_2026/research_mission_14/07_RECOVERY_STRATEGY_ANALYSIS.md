# StateShift Research Mission 14 — Deliverable 07: Recovery Strategy Analysis

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Date**: October 25, 2026  

---

## 1. Grounding the 7-Strategy Taxonomy in Physical Evidence

In Mission 13, a 7-category taxonomy was proposed to classify reasoning trajectories:
- S1: Genuine Local Repair
- S2: Restart Success (Explicit)
- S3: Restart Success (Implicit)
- S4: Compounded Error Continuation
- S5: Hallucinated Self-Correction
- S6: Generation Limit Truncation
- S7: Lucky Guess / Alternative Path

### Critical Audit Findings on Category Definitions:
1. **Behavioral vs. Prompt-Induced Categories**:
   - In Mission 13, Evaluator v4 contained a severe confound (line 196) that forced S2 (Explicit Restart) whenever the prompt was Condition D (`explicit_restart`).
   - In Mission 14, Evaluator v5 re-classifies trajectories **strictly from generated tokens**. Under Evaluator v5, an explicit restart is recorded only when the model itself produces explicit restart phrases (*"I will start from scratch"*, *"disregarding the above"*).
2. **Mutual Exclusivity & Exhaustiveness**:
   - Evaluator v5 establishes a strict hierarchical decision tree (Truncation $\to$ Genuine Local Repair $\to$ Explicit Restart $\to$ Implicit Restart $\to$ Hallucination $\to$ Compounded Error $\to$ Alternative Path), guaranteeing that every trajectory is assigned to exactly one category.

---

## 2. Analysis of Physical Evidence (N=6 Recovered Records)

Analyzing the 6 physically surviving records under Evaluator v5:

| Record ID | Condition | Prompt Condition | Text-Derived Classification | Evaluator v5 Strategy Code | Correctness |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `primary_100_req_0001` | Condition A | Neutral Baseline | Alternative valid derivation | **S7 (Alternative Path)** | `VERIFIED_TRUE` |
| `primary_100_req_0002` | Condition D | Discard Mandate | Began de novo with problem setup | **S3 (Implicit Restart)** | `VERIFIED_TRUE` |
| `primary_100_req_0003` | Condition E | Surgical Repair | Began de novo with problem setup | **S3 (Implicit Restart)** | `VERIFIED_TRUE` |
| `primary_100_req_0004` | Condition F | Verbatim Preserve | Began de novo with problem setup | **S3 (Implicit Restart)** | `VERIFIED_TRUE` |
| `primary_100_req_0131` | Condition E | Surgical Repair | Began de novo with problem setup | **S3 (Implicit Restart)** | `VERIFIED_TRUE` |
| `primary_100_req_0143` | Condition E | Surgical Repair | Began de novo with problem setup | **S3 (Implicit Restart)** | `VERIFIED_TRUE` |

### Key Observations:
1. **Zero Genuine Local Repairs (S1)**: In none of the 4 recovery-prompted traces (req 0003, 0004, 0131, 0143) did the model localize the error or perform surgical replacement.
2. **Total Dominance of Implicit Restarts (S3)**: In all 4 recovery traces—and even in Condition D where discarding was requested—the model did not emit meta-linguistic phrases like *"I am restarting"*; instead, it immediately started writing fresh mathematical derivations from first principles (*"To solve the problem, we start by..."*).
3. **Hypothesis vs. Fact**: The 81.7% aggregate restart rate reported in Mission 13 is officially treated as an **unconfirmed exploratory observation** until the complete 400-problem manifest is executed with detached logging. However, the qualitative reality of implicit restarting is directly verified in 100% of the surviving recovery traces.

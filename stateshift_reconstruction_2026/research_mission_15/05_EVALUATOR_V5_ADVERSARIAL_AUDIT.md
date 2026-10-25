# Research Mission 15: Evaluator v5.1 Adversarial Audit & Edge-Case Hardening

**Principal Investigator**: Sham Satish Thakare  
**Repository**: `github.com/shamddd/stateshift`  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15/05_EVALUATOR_V5_ADVERSARIAL_AUDIT.md`  
**Module**: `research_mission_15/evaluation/strict_recovery_evaluator_v5_adversarial.py`  
**Date**: October 25, 2026  
**Auditor**: Independent NLP & Evaluation Methodology Specialist  

---

## 1. Executive Summary

In Mission 14, Evaluator v5.0 successfully eliminated condition label leakage (such as `or condition == "explicit_restart"`), deriving classifications strictly from generated token sequences. However, automated heuristic classifiers remain vulnerable to linguistic boundary conditions, conflicting rhetorical markers, and non-monotonic generation shortcuts.

To prevent adversarial misclassifications, Evaluator v5.1 introduces:
1. **Context-Aware Implicit Restart Triggering**: Prevents false-positive restart classification when standard introductory phrasing (`"First, let's..."`, `"To solve this..."`) is used to introduce an in-place localized correction.
2. **Strategy Conflict Resolution**: Detects rollouts that contain contradictory signals (e.g., explicit restart declaration combined with localized in-place assertions) and falls back to `AMBIGUOUS_RECOVERY_UNVERIFIED` with `requires_human_validation = True`.
3. **Boxed Answer Shortcut Detection**: Identifies rollouts that jump directly to `\boxed{}` with minimal reasoning tokens (< 40 tokens) as `DIRECT_ANSWER_SHORTCUT`, preventing them from being counted as valid repairs.
4. **Heuristic Confidence Scoring**: Assigns explicit calibrated confidence to each classification.

### Audit Verdict: **PASSED (ADVERSARIALLY HARDENED & TESTED)**

---

## 2. Adversarial Vulnerability Analysis & Solutions

### 2.1 The Introductory Phrasing Confounder
- **Vulnerability in v5.0**: Evaluator v5.0 flagged `is_implicit_restart = True` whenever `first_chunk.startswith("first, let's")` or `"to solve"`. If an LLM performs genuine local repair and writes:
  > *"First, let's fix the error in step 1. The line was calculated incorrectly: instead of 2 * 6 = 10, it should be 2 * 6 = 12."*
  v5.0 classified `is_implicit_restart = True`. Since `is_genuine_local_repair` requires `not is_restart`, this genuine repair was erroneously denied and classified as an implicit restart or lucky guess!
- **v5.1 Hardening**: Lookahead check inspects `first_chunk` for error detection / repair indicators (`error`, `mistake`, `correct`, `fix`, `instead`, `should be`). If repair keywords are present, `is_implicit_restart` is suppressed. Verified in test case `test_local_repair_with_introductory_phrasing`.

### 2.2 Conflicting Multi-Strategy Assertions
- **Vulnerability in v5.0**: When an LLM outputs both an explicit restart marker (*"Let's start from scratch..."*) and subsequently repeats an error localization assertion, v5.0 assigned S2 without recording the epistemic ambiguity.
- **v5.1 Hardening**: Evaluator v5.1 detects the mutual exclusion conflict:
  ```python
  has_strategy_conflict = bool(is_explicit_restart and (err_loc_status == "VERIFIED_TRUE" and correction_status == "VERIFIED_TRUE"))
  if has_strategy_conflict:
      overall_status = "AMBIGUOUS_RECOVERY_UNVERIFIED"
      confidence = 0.40
  ```
  This cleanly isolates ambiguous rollouts for human verification rather than biasing automated statistics.

### 2.3 Direct Boxed Hallucination / Shortcuts
- **Vulnerability in v5.0**: A model outputting only `\boxed{12}` without showing reasoning steps received `ans_status = VERIFIED_TRUE` and was categorized as `LUCKY_GUESS_OR_ALTERNATIVE_PATH` (S7) with default confidence.
- **v5.1 Hardening**: Rollouts with fewer than 40 generated tokens that output a boxed answer without step-by-step reasoning are categorized specifically as `DIRECT_ANSWER_SHORTCUT`, clearly distinguishing them from full chain-of-thought solutions.

---

## 3. Evaluator Strategy Taxonomy (v5.1)

| Strategy ID | Canonical Name | Mathematical & Behavioral Predicates | Heuristic Confidence |
| :---: | :--- | :--- | :---: |
| **S1** | **GENUINE_LOCAL_REPAIR** | Error detected $\land$ localized to step $k$ $\land$ corrected symbolically $\land$ prefix preserved $\land$ final answer verified | 0.95 |
| **S2** | **RESTART_SUCCESS_EXPLICIT** | Explicit restart marker detected $\land$ final answer verified | 0.95 |
| **S3** | **RESTART_SUCCESS_IMPLICIT** | De novo problem formulation (no repair markers) $\land$ final answer verified | 0.90 |
| **S4** | **COMPOUNDED_ERROR_CONTINUATION** | Continues from corrupted step without repair $\land$ final answer incorrect | 0.90 |
| **S5** | **HALLUCINATED_SELF_CORRECTION** | Claims error detected $\land$ symbolic correction invalid/wrong | 0.85 |
| **S6** | **GENERATION_LIMIT_TRUNCATION** | Tokens $\ge$ max_tokens / length stop $\land$ final answer unreached | 0.99 |
| **S7** | **LUCKY_GUESS_OR_ALTERNATIVE_PATH** | Correct final answer without valid local repair or identifiable restart markers | 0.75 |
| **S8** | **DIRECT_ANSWER_SHORTCUT** | Correct answer with $<40$ tokens (zero chain-of-thought) | 0.85 |
| **S9** | **AMBIGUOUS_RECOVERY_UNVERIFIED** | Contradictory signals (e.g. explicit restart + in-place repair claim) | 0.40 (Human Gate) |
| **S10**| **RESTART_FAILURE** | Restart attempted (explicit or implicit) $\land$ final answer incorrect | 0.90 |

---

## 4. Test Verification

The adversarial test suite `research_mission_15/tests/test_evaluator_v5_adversarial.py` confirmed 100% pass rate across all 5 edge-case categories:
1. `test_local_repair_with_introductory_phrasing` — PASSED
2. `test_implicit_restart_standard` — PASSED
3. `test_shortcut_guess_without_reasoning` — PASSED
4. `test_ambiguous_conflicting_signals` — PASSED
5. `test_compounded_error_continuation` — PASSED

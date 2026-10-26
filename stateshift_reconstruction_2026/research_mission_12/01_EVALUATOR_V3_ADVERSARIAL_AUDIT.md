# 01. Adversarial Audit of Mathematical Recovery Evaluator v3

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Auditor**: Mathematical Reasoning Verification & Adversarial Audit Team  
**Test Fixtures**: [`tests/fixtures_evaluator_adversarial.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_12/tests/fixtures_evaluator_adversarial.py)  

---

## 1. Executive Summary: Vulnerabilities Discovered in Evaluator v3

While Evaluator v3 successfully eliminated crude regex patterns and achieved high performance on standard cases, adversarial probing reveals **seven fundamental structural vulnerabilities**:

1. **Keyword-Dependent Error Detection**:
   Evaluator v3 requires words like `"error"`, `"mistake"`, `"flaw"`, or `"wrong"`. In Fixture `ADV_05`, a model performing an exact algebraic replacement without conversational commentary is marked as `error_detection = False`.
2. **False Error Claims Accepted as Detection**:
   In Fixture `ADV_01`, a model that says *"I found an error in step 1: 2 is not prime"* has `error_detection = True` in v3 because `"error"` and `"step 1"` are present, even though the claimed flaw is mathematically false.
3. **Rigid Mutually Exclusive Restart Classes**:
   In Fixture `ADV_06`, when a model preserves Step 1 and recalculates Step 2, Evaluator v3 cannot represent hybrid recomputations, defaulting to `AMBIGUOUS_BEHAVIOR`.
4. **Circularity in Local Correction Validity**:
   Evaluator v3 marked `mathematical_correction_validity = True` whenever `is_final_correct and not is_restart`. This creates circular reasoning: it assumes that reaching the right answer without restarting implies the intermediate repair was valid.
5. **No Structured Step Dependency Graph**:
   In Fixture `ADV_03`, the model preserves Step 1, but its Step 3 directly depends on the invalid Step 2. Evaluator v3 has no graph representation to verify whether preserved lines are independent of corrupted assertions.
6. **Domain Constraint Blindness in SymPy**:
   Checking $A - B = 0$ can simplify expressions across undefined domains (e.g. dividing by zero or assuming $\sqrt{x^2} = x$ for $x < 0$).
7. **No Explicit "UNVERIFIED" Category for Non-Elementary Derivations**:
   When a proof step invokes an advanced theorem (Fixture `ADV_09`), Evaluator v3 attempts elementary parsing rather than returning `UNVERIFIED` for human adjudication.

---

## 2. Adversarial Fixture Benchmark Results

| Fixture ID | Description | Evaluator v3 Verdict | Ground-Truth Scientific Meaning | Failure Mode |
| :--- | :--- | :--- | :--- | :--- |
| **`ADV_01`** | False error claim | `error_detection: TRUE`<br>`localized: TRUE` | **FALSE DETECTION** (Claimed 2 is not prime) | **Keyword Trap**: Evaluator checked presence of `"error"` and `"step 1"` rather than verifying whether the claimed flaw was real. |
| **`ADV_02`** | Alternative derivation | `final_correct: TRUE`<br>`status: UNVERIFIED` | **CORRECT ANSWER, UNREPAIRED STEP** | **Missing Bypass Detection**: v3 failed to note that the injected step was ignored rather than repaired. |
| **`ADV_03`** | Valid prefix + invalid dependency | `valid_preserved: TRUE`<br>`restart: AMBIGUOUS` | **BLIND COPYING** (Corrupted dependency propagated) | **Graph Blindness**: Lacked dependency graph to verify whether Step 3 used corrupted Step 2. |
| **`ADV_04`** | Silent implicit restart | `restart: IMPLICIT`<br>`repair: FALSE` | **IMPLICIT RESTART** | **Handled correctly by v3.** |
| **`ADV_05`** | Surgical repair without keywords | `error_detection: FALSE`<br>`repair: FALSE` | **GENUINE LOCAL REPAIR** | **False Negative**: Model surgically repaired derivation without conversational error keywords. |
| **`ADV_06`** | Hybrid recomputation | `restart: AMBIGUOUS`<br>`repair: FALSE` | **PARTIAL RECOMPUTATION** | **Rigid Taxonomy**: Forced mutually exclusive classification on hybrid behavior. |
| **`ADV_07`** | Equivalent non-trivial syntax | `final_correct: TRUE` | **MATHEMATICALLY EQUIVALENT** | **Handled correctly by SymPy oracle.** |
| **`ADV_08`** | Lucky correct via false reasoning | `continuation_valid: TRUE`<br>`repair: FALSE` | **FALLACIOUS DERIVATION** | **False Step Acceptance**: Lacked step-by-step validity checking. |
| **`ADV_09`** | Non-elementary theorem | `status: UNVERIFIED` | **MATHEMATICALLY SOUND, UNVERIFIABLE** | **Handled correctly by fallback.** |

---

## 3. Required Architectural Specification for Evaluator v4

To eliminate these failure modes before running 7B experiments, **Evaluator v4** must implement:
1. **`evaluation_schema.py`**: A structured JSON schema defining `valid_prefix_steps`, `corrupted_step_id`, `corrupted_assertion`, `expected_corrected_assertion`, `downstream_dependencies`, and `domain_assumptions`.
2. **`step_dependency_graph.py`**: A directed acyclic graph (DAG) mapping each step's mathematical dependencies to verify whether downstream steps consume valid or corrupted assertions.
3. **`symbolic_repair_verifier.py`**: Domain-safe SymPy verifier checking equation equivalence, substitution validity, and domain restrictions (avoiding division by zero and branch cuts).
4. **4-Valued Categorical Labels**: Every dimension must support `VERIFIED_TRUE`, `VERIFIED_FALSE`, `UNVERIFIED`, and `NOT_APPLICABLE`, accompanied by an explicit textual evidence span.

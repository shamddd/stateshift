# Phase B: Confirmatory Selection Protocol & Stratification Specification

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22 — Confirmatory Trial Preflight  
**Date & Timestamp**: 2026-10-27T02:26:30+05:30  
**Target Venue**: NeurIPS 2027 Main Track  

---

## 1. Objectives and Pre-Commitment

This protocol specifies the exact deterministic algorithm used to sample $N = 231$ mathematical reasoning problems from the 354 candidate pool. The selection protocol is frozen prior to any GPU execution, ensuring complete protection against researcher degrees of freedom, p-hacking, or post-hoc problem curation.

---

## 2. Selection Methodology

### 2.1 Deterministic Pseudo-Random Number Generation
- **PRNG Engine**: Python `random.Random(seed)` using the Mersenne Twister algorithm.
- **Preregistered Random Seed**: `2027` (reflecting the NeurIPS 2027 publication target).
- **Sort Key Stability**: Before sampling, problems within each operator partition are sorted lexicographically by `problem_id` (e.g., `math500_013`, `math500_014`, ...).

### 2.2 Operator-Balanced Quotas
The candidate pool contains problems across 10 distinct error operator categories:
$$\sum_{k=1}^{10} n_k = 24 + 9 \times 23 = 231\text{ problems}$$

| Operator Code | Operator Name | Total in Pool | Quota Sampled | Sampling Ratio |
| :--- | :--- | :--- | :--- | :--- |
| **OP01** | Arithmetic Miscalculation | 36 | **24** | $66.7\%$ |
| **OP02** | Sign Flip | 36 | **23** | $63.9\%$ |
| **OP03** | Fraction Inversion | 36 | **23** | $63.9\%$ |
| **OP04** | Invalid Assumption | 36 | **23** | $63.9\%$ |
| **OP05** | Invalid Logical Deduction | 35 | **23** | $65.7\%$ |
| **OP06** | Multi-Step Decomposition Error | 35 | **23** | $65.7\%$ |
| **OP07** | Misapplied Identity | 35 | **23** | $65.7\%$ |
| **OP08** | Incorrect Tool Output | 35 | **23** | $65.7\%$ |
| **OP09** | Plausible False Conclusion | 35 | **23** | $65.7\%$ |
| **OP10** | Contradictory Absorbing State | 35 | **23** | $65.7\%$ |
| **TOTAL** | — | **354** | **231** | **$65.3\%$** |

---

## 3. Stratified Sample Balance

The deterministic selection with seed `2027` produces an empirical balance across difficulty levels and mathematical disciplines:

### 3.1 Difficulty Distribution
- **Level 1 (Elementary)**: 47 problems ($20.3\%$)
- **Level 2 (Easy)**: 46 problems ($19.9\%$)
- **Level 3 (Intermediate)**: 46 problems ($19.9\%$)
- **Level 4 (Challenging)**: 46 problems ($19.9\%$)
- **Level 5 (Olympiad / Hard)**: 46 problems ($19.9\%$)

The uniform difficulty profile ensures that statistical recovery effects are evaluated equally across both trivial derivations and high-complexity proofs.

### 3.2 Subject Distribution
- **Algebra**: 59 problems ($25.5\%$)
- **Prealgebra**: 42 problems ($18.2\%$)
- **Intermediate Algebra**: 41 problems ($17.7\%$)
- **Number Theory**: 28 problems ($12.1\%$)
- **Precalculus**: 24 problems ($10.4\%$)
- **Geometry**: 20 problems ($8.7\%$)
- **Counting & Probability**: 17 problems ($7.4\%$)

---

## 4. Manifest Expansion to Four Experimental Conditions

Each of the 231 problems is expanded into exactly 4 matched condition requests:
1. `Condition_A_Zero_Shot`: Unprompted baseline solving from scratch.
2. `Condition_D_Forced_Restart`: Explicit discard instruction forcing fresh restart.
3. `Condition_E_Explicit_Repair`: Identification and local surgical repair prompt.
4. `Condition_F_State_Preserving`: Verified state preservation intervention.

Total generated requests: $231 \times 4 = 924$ requests, indexed `confirmatory_231_req_0001` through `confirmatory_231_req_0924`.

---

## 5. Algorithmic Reproducibility Verification

The selection protocol is executable via:
```bash
python3 research_mission_22/scripts/build_confirmatory_datasets.py
```
Re-running this script produces byte-identical JSONL output matching SHA-256:
`2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5`.

# Phase 5: Frozen Option B Confirmatory Protocol & Preregistration

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Mission**: Research Mission 22.1 — Final Confirmatory Scientific Audit  
**Date & Timestamp**: 2026-10-27T05:42:20+05:30  
**Target Publication Venue**: NeurIPS 2027 Main Track  
**Preregistration Protocol Status**: **LOCKED AND FROZEN PRIOR TO CLOUD EXECUTION**  

---

## 1. Experimental Design: Option B Overview

The Principal Investigator has formally selected **Option B (Full 4-Condition Battery)** for the confirmatory trial:

| Component | Specification |
| :--- | :--- |
| **Study Identifier** | `STATESHIFT-CONFIRMATORY-OPTION-B` |
| **Evaluated Problem Count** | Exactly $N = 231$ held-out problems from MATH-500 |
| **Evaluated Conditions** | 4 Conditions: Condition A, Condition D, Condition E, Condition F |
| **Total Planned Generations** | Exactly $924$ requests ($231 \times 4$) |
| **Primary Comparison** | Condition F (State Preservation) vs. Condition D (Forced Restart) |
| **Secondary Contrasts** | Condition F vs. Condition A; Condition F vs. Condition E |
| **Primary Endpoint** | Binary mathematical equivalence against ground truth ($Y_{i,k} \in \{0, 1\}$) |
| **Primary Statistical Test** | Exact two-sided McNemar test conditional on discordant pairs $n_d$ |
| **Significance Level** | $\alpha = 0.05$ (two-sided) |
| **Multiplicity Adjustment** | Hierarchical gatekeeping + Holm-Bonferroni step-down for secondary tests |
| **Deterministic Sampling Seed**| `2027` (Mersenne Twister `random.Random(2027)`) |

---

## 2. Frozen Manifest & Generation Specifications

### 2.1 Manifest Artifacts
- **JSONL Manifest**: `research_mission_22/data/confirmatory_231_manifest.jsonl`
  - Record count: Exactly 924 requests
  - File size: 1,246,234 bytes
  - Canonical SHA-256: `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5`
- **JSON Manifest**: `research_mission_22/data/confirmatory_231_manifest.json`
  - Record count: Exactly 924 requests
  - File size: 1,389,819 bytes
  - Canonical SHA-256: `3b0114558cdd36d409f2351388ec8fb36724cdf7ac0916e2c3c36420bff55f42`

### 2.2 Execution Ordering Policy
Requests are ordered deterministically:
1. Primary sort: Lexicographic order of `problem_id` (`math500_006`, `math500_007`, ..., `math500_500`).
2. Secondary sort within problem: Condition sequence:
   - Request 1: `Condition_A_Zero_Shot`
   - Request 2: `Condition_D_Forced_Restart`
   - Request 3: `Condition_E_Explicit_Repair`
   - Request 4: `Condition_F_State_Preserving`

### 2.3 Frozen Neural Hyperparameters
- **Model ID**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Model Revision (Git Commit)**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Tokenizer Revision**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Precision**: `torch.bfloat16`
- **Decoding Temperature**: `0.0` (pure greedy decoding)
- **Top-$p$**: `1.0` (unfiltered)
- **Max New Tokens**: `768`
- **Random Seed**: `42` (`torch.manual_seed(42)`)

---

## 3. Evaluation Rules & Missing Data Policy

1. **Answer Extraction**:
   - Cleanroom recursive brace parser extracts terminal `\boxed{...}` expression.
   - If no boxed expression is found, fallback patterns (`the answer is`, `final answer:`) are evaluated. If no valid candidate is extracted, outcome is recorded as $0$ (incorrect).
2. **Equivalence Checking**:
   - Exact normalized string match after LaTeX wrapper stripping.
   - Symbolic simplification via SymPy (`simplify(pred - gold) == 0`).
   - Pure numerical float approximation within tolerance $10^{-6}$.
3. **Missing Data & Error Policy**:
   - Generation timeouts or CUDA runtime crashes (if any occur despite preflight): Recorded as $0$ (incorrect); under no circumstances will a problem be replaced or dropped.
   - Network / HTTP retries: Maximum 2 transient connection retries with exponential backoff allowed at the runner layer. Zero reasoning retries (no resamples on reasoning failures).

---

## 4. Preregistration Amendment Record

- **Amendment History**: No material amendments made to the 231 problem selections, prompt templates, or condition codes.
- **Unblinded Status Certification**: The Principal Investigator and audit agents certify that **zero confirmatory generations have been executed, inspected, or evaluated** ($0.00 cloud compute incurred; `.cloud_execution_locked` remains active).
- **Protocol Hash**: The complete Option B protocol is cryptographically locked under Git commit SHA `4458a9c` and its successor commits on branch `research/stateshift-mission22-1-final-authorization-audit`.

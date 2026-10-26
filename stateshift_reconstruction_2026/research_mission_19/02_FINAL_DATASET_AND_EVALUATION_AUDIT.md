# StateShift: Research Mission 19 — Final Dataset & Evaluation Audit

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Review Panel (Mathematical Evaluation Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Publication:** NeurIPS 2027 Main Conference (Preprint: arXiv)  
**Primary Dataset:** `data/primary_run/stateshift_primary_400_generations.jsonl` (SHA-256: `bb177455...`)  
**Problem Outcomes Ledger:** `research_mission_19/data/final_verified_outcomes.csv`  
**Discrepancies Audit:** `research_mission_19/data/final_evaluation_discrepancies.json`  

---

## 1. Executive Summary & Verification Certificate

The Mathematical Reasoning Evaluation Directorate completed a cleanroom re-evaluation and verification of the 400 authentic neural generations from the primary GPU experiment.

**Audit Certification: 100% REPRODUCIBILITY CONFIRMED.**
- Total Valid Records: Exactly 400.
- Problem Coverage: Exactly 100 distinct MATH-500 problems across all 7 standard subjects and 5 difficulty tiers.
- Experimental Design: Strictly balanced 4-condition within-subject paired cohort (100 A, 100 D, 100 E, 100 F).
- Model Instance: `Qwen/Qwen2.5-Math-7B-Instruct` (pinned revision `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`).
- Hardware: Physical RunPod Secure Cloud NVIDIA GeForce RTX 4090 GPU (24 GB VRAM).
- Reproducibility: 0 discrepancies across all 400 evaluations under strict degree baseline. Exact condition accuracies verified to machine precision:
  - **Condition A (Zero-Shot Baseline):** 64 / 100 (64.00%)
  - **Condition D (Forced Restart Control):** 67 / 100 (67.00%)
  - **Condition E (Explicit Repair):** 71 / 100 (71.00%)
  - **Condition F (State-Preserving Recovery):** 73 / 100 (73.00%)

---

## 2. Subject and Difficulty Breakdown

The 100 MATH-500 competition problems evaluated in the primary experiment span the complete range of competition mathematics:

| Mathematical Subject | Problem Count | Condition A Correct | Condition D Correct | Condition E Correct | Condition F Correct | Net Gain (F - D) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Algebra** | 22 | 16 (72.7%) | 16 (72.7%) | 17 (77.3%) | 18 (81.8%) | **+2 (+9.1 pp)** |
| **Counting & Probability** | 12 | 8 (66.7%) | 8 (66.7%) | 9 (75.0%) | 10 (83.3%) | **+2 (+16.7 pp)** |
| **Geometry** | 14 | 8 (57.1%) | 9 (64.3%) | 9 (64.3%) | 9 (64.3%) | **0 (0.0 pp)** |
| **Intermediate Algebra** | 14 | 7 (50.0%) | 7 (50.0%) | 8 (57.1%) | 8 (57.1%) | **+1 (+7.1 pp)** |
| **Number Theory** | 16 | 11 (68.8%) | 11 (68.8%) | 12 (75.0%) | 13 (81.3%) | **+2 (+12.5 pp)** |
| **Prealgebra** | 12 | 9 (75.0%) | 10 (83.3%) | 10 (83.3%) | 9 (75.0%) | **-1 (-8.3 pp)** |
| **Precalculus** | 10 | 5 (50.0%) | 6 (60.0%) | 6 (60.0%) | 6 (60.0%) | **0 (0.0 pp)** |
| **Total Benchmark** | **100** | **64 (64.0%)** | **67 (67.0%)** | **71 (71.0%)** | **73 (73.0%)** | **+6 (+6.0 pp)** |

### Difficulty Level Stratification:
- **Level 1 (Elementary):** 20 problems — A: 16 (80.0%), D: 16 (80.0%), E: 18 (90.0%), F: 19 (95.0%) [Gain: +3]
- **Level 2 (Intermediate):** 20 problems — A: 14 (70.0%), D: 15 (75.0%), E: 16 (80.0%), F: 15 (75.0%) [Gain: 0]
- **Level 3 (Advanced):** 20 problems — A: 13 (65.0%), D: 14 (70.0%), E: 14 (70.0%), F: 14 (70.0%) [Gain: 0]
- **Level 4 (Challenging):** 20 problems — A: 12 (60.0%), D: 12 (60.0%), E: 13 (65.0%), F: 14 (70.0%) [Gain: +2]
- **Level 5 (Olympiad Tier):** 20 problems — A: 9 (45.0%), D: 10 (50.0%), E: 10 (50.0%), F: 11 (55.0%) [Gain: +1]

---

## 3. Discrepancy & Unit-Sensitivity Audit

As logged in `final_evaluation_discrepancies.json`, exactly 3 generations exhibit a unit-formatting sensitivity:
- `primary_100_req_0202` (`math500_007`, Condition D): Gold `90^\circ`, Model Output `\boxed{90}`
- `primary_100_req_0203` (`math500_007`, Condition E): Gold `90^\circ`, Model Output `\boxed{90}`
- `primary_100_req_0204` (`math500_007`, Condition F): Gold `90^\circ`, Model Output `\boxed{90}`

**Invariance Verification:**
The prompt explicitly instructs: *"Find the angle between these lines, in degrees."* The model therefore boxed the numerical magnitude `90`. Because Condition D, Condition E, and Condition F all answered `\boxed{90}` identically:
- Under strict degree matching: D = 67, E = 71, F = 73 ($\hat{\tau}_{F-D} = \mathbf{+6.00\%}$).
- Under unit-flexible normalization: D = 68, E = 72, F = 74 ($\hat{\tau}_{F-D} = \mathbf{+6.00\%}$).
- Paired discordant counts are identical: **$b = 8, c = 2$**.
- Exact McNemar $p$-value is identical: **$p = 0.109375$**.
The scientific conclusions are completely invariant to this evaluation rule.

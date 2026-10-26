# 11. Full 7B Replication Experiment Plan

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Status**: Prepared and Frozen (Pending Pilot Empirical Calibration)  

---

## 1. Experimental Architecture ($N=400$ Rollouts)

Following the successful execution of the 10-problem pilot, the full confirmatory study will scale to:
- **100 Held-Out Problems** sampled across all 7 MATH-500 subject areas (Algebra, Prealgebra, Intermediate Algebra, Number Theory, Geometry, Counting & Probability, Precalculus) and all 5 difficulty levels.
- **4 Matched Conditions**:
  - `Condition_A_Zero_Shot`: $N = 100$
  - `Condition_D_Forced_Restart`: $N = 100$
  - `Condition_E_Explicit_Repair`: $N = 100$
  - `Condition_F_State_Preserving`: $N = 100$
- **Total Rollouts**: $N = 400$ generations.
- **Token Ceiling**: $T = 768$ tokens (informed by Mission 10 truncation curve).

---

## 2. Primary & Secondary Statistical Hypotheses

### Primary Hypothesis ($H_1$):
State-Preserving Repair (Condition F) matches or outperforms Forced Restart (Condition D) on common endpoint final-answer correctness ($\Delta \ge 0$), while requiring significantly fewer generation tokens ($p < 0.01$).
- **Statistical Test**: Exact paired McNemar test on discordant pairs ($n_{10}$ vs $n_{01}$) + Clustered GEE logistic regression with exchangeable correlation within problem clusters.

### Secondary Hypothesis ($H_2$):
Frontier 7B instruction-tuned reasoning models (`Qwen2.5-Math-7B-Instruct`) exhibit a non-zero Genuine Local Repair rate in Condition E, whereas sub-2B models collapse into implicit restarting.
- **Statistical Test**: Fisher's Exact test comparing local repair rate at 7B vs 1.5B ($0.0\%$).

---

## 3. Calibrated Runtime & Cost Modeling

| Experiment Metric | Conservative Estimate | Expected Estimate | Optimistic Estimate |
| :--- | :---: | :---: | :---: |
| **Inference Throughput** | 35 tokens / sec | 45 tokens / sec | 55 tokens / sec |
| **Mean Tokens / Rollout** | 450 tokens | 400 tokens | 350 tokens |
| **Total Tokens Generated** | 180,000 tokens | 160,000 tokens | 140,000 tokens |
| **Active Inference Time** | 85.7 min (1.43 hr) | 59.2 min (0.99 hr) | 42.4 min (0.71 hr) |
| **Setup & Teardown** | 15.0 min (0.25 hr) | 12.0 min (0.20 hr) | 10.0 min (0.17 hr) |
| **Total Pod Duration** | **1.68 hours** | **1.19 hours** | **0.88 hours** |
| **Hourly Rate (RTX 4090)**| $0.34 / hr | $0.34 / hr | $0.34 / hr |
| **Total Cloud Expense** | **$0.57** | **$0.40** | **$0.30** |

> [!NOTE]
> Even under the most conservative throughput assumptions, the entire 100-problem replication study costs **less than \$0.60**.

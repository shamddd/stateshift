# Study 1: Historical Checkpoint-Lineage Protocol & Replication

This directory contains reproduction code for **Study 1**, investigating latent recovery trajectories across the DeepScaleR-7B reinforcement learning checkpoint progression.

---

## 1. Experimental Overview

* **Base Model**: DeepScaleR-1.5B / DeepScaleR-7B checkpoint progression.
* **Problem Pairs**: $N = 454$ mathematical problem pairs from Olympiad, AIME, and MATH-500.
* **Evaluated Checkpoints**: Step 0 (Base Model) vs. Step 256 (RL post-trained).
* **Rollouts**: 32 rollouts per cell across 4 conditions (29,056 total evaluations).
* **Data Provenance**: **Tier 2 (Outcome-Level Reproduction)**. Complete outcome rows and token lengths are preserved in `data/study1/controlled_endpoint_outcomes.csv`. Raw generation texts are not present.

---

## 2. Replication Command

To verify the dataset SHA-256 and reproduce all cell means, interaction estimands, and clustered standard errors:

```bash
python experiments/study1_checkpoint_lineage/reproduce_study1.py
```

### Expected Output Summary:
* Step 0 Control: $38.92\%$
* Step 0 Recovery: $38.34\%$ (Diff: $-0.58\text{ pp}$)
* Step 256 Control: $59.21\%$
* Step 256 Recovery: $70.39\%$ (Diff: $+11.18\text{ pp}$)
* **Interaction $\Gamma_{256}$**: $+11.76\text{ percentage points}$
* **Clustered Standard Error**: $0.0114$ ($t = 10.34$, $p = 1.05 \times 10^{-22}$)
* **TOST Length Equivalence**: Confirmed equivalent at $[-5, +5]$ token margin ($p = 0.0256$).

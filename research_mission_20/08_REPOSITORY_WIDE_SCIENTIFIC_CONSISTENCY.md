# StateShift: Research Mission 20 — Scientific Consistency & Claim Audit

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training
**Date**: October 26, 2026

---

## 1. Executive Summary

This repository-wide audit verifies that all scientific claims, statistical constants, sample counts, and p-values are 100% mutually consistent across the public repository. All legacy overclaims ("guaranteed significance", "100% confirmation", "NeurIPS accepted") have been eradicated from the public manuscript and active documentation.

---

## 2. Universal Empirical Constants Audit

Every occurrence of key empirical numbers across all active documentation and code was verified against the raw data:

| Metric / Estimand | Target Value | Verification Source | Status |
| :--- | :---: | :--- | :---: |
| **Study 1 Sample Size** | $N = 454$ pairs | `data/study1/controlled_endpoint_outcomes.csv` | **CONSISTENT** |
| **Study 1 Total Evaluations** | $29,056$ rows | `data/study1/controlled_endpoint_outcomes.csv` | **CONSISTENT** |
| **Step-256 Interaction** | $+11.76\text{ pp}$ | Clustered linear regression ($p = 1.05 \times 10^{-22}$) | **CONSISTENT** |
| **Study 2 Problem Count** | $N = 100$ | `data/study2/final_verified_outcomes.csv` | **CONSISTENT** |
| **Study 2 Total Generations** | $400$ requests | `data/study2/stateshift_primary_400_generations.jsonl` | **CONSISTENT** |
| **Condition A Accuracy** | $64.0\%$ | 64 successes / 100 | **CONSISTENT** |
| **Condition D Accuracy** | $67.0\%$ | 67 successes / 100 | **CONSISTENT** |
| **Condition E Accuracy** | $71.0\%$ | 71 successes / 100 | **CONSISTENT** |
| **Condition F Accuracy** | $73.0\%$ | 73 successes / 100 | **CONSISTENT** |
| **Primary Contrast ($\hat{\tau}_{F-D}$)** | $+6.00\text{ pp}$ | $73.0\% - 67.0\%$ | **CONSISTENT** |
| **Exact Two-Sided McNemar** | $p = 0.109375$ | Binomial $B(10, 0.5)$ | **CONSISTENT** |
| **Exact One-Sided McNemar** | $p = 0.054688$ | Binomial $B(10, 0.5)$ | **CONSISTENT** |
| **Pilot Power ($N=100$)** | $36.20\%$ | Exact discrete power engine | **CONSISTENT** |
| **Confirmatory $N$ (80% Power)** | $N = 231$ | Exact discrete power engine ($80.07\%$) | **CONSISTENT** |
| **Confirmatory $N$ (90% Power)** | $N = 299$ | Exact discrete power engine ($90.02\%$) | **CONSISTENT** |

---

## 3. Historical Record Distinctions

Where legacy documents (e.g., Mission 15 or 18 logs) reflect earlier exploratory iterations or historical milestones, they are explicitly quarantined in historical directories (`stateshift_reconstruction_2026/`) and cross-referenced in `docs/RESEARCH_HISTORY.md` to preserve the historical audit trail without confusing the public scientific record.

# StateShift Source of Truth Registry & Evidentiary Hierarchy

**Audit Date**: October 18, 2026  
**Status**: Formally Established  
**Standard**: Cryptographic Ground Truth  

---

## 1. The Definitive Evidentiary Hierarchy

When reconciling discrepancies across historical documents, commit logs, and manuscripts, the following precedence hierarchy strictly governs:

```
[Level 1: Cryptographic Raw Data] (Highest Authority)
       │  ├── controlled_endpoint_outcomes.csv (SHA-256: 49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139)
       │  ├── natural_error_episodes.csv (582 rows) & natural_recovery_episodes.csv (180 rows)
       │  └── intermediate_rollouts.jsonl (Checkpoints 32, 64, 96, 128, 160, 192, 224)
       ▼
[Level 2: Primary Python Source Code]
       │  ├── stateshift/statistics/bootstrap.py (Problem-blocked bootstrap, B=10,000)
       │  ├── stateshift/statistics/metrics.py (Interaction contrast Gamma_t calculation)
       │  └── stateshift/trajectory/order_restricted.py (Isotonic regression PAVA)
       ▼
[Level 3: Submitted Camera-Ready Manuscript]
       │  ├── 01_Main_Manuscript.tex & 01_Main_Manuscript.pdf (Elsevier AIJ ARTINT-D-26-01491)
       │  └── StateShift_AIJ_Final_Submission.zip
       ▼
[Level 4: Forensic Reconciliations & PhD Defense Audits]
       │  ├── 20_STATESHIFT_SIGN_RECONCILIATION.md
       │  └── 156_FLAGSHIP_SOURCE_OF_TRUTH_AUDIT.md
       ▼
[Level 5: Historical Precursor Working Papers & Drafts] (Lowest Authority / Superseded)
          ├── STATESHIFT_TECHNICAL_REPORT.md (Early code-generation exploratory draft)
          └── recovery_eval (Precursor repository name)
```

---

## 2. Primary Ground Truth Parameters (Locked by Level 1 Data)

| Parameter | Exact Value | Ground Truth Source | Recomputed from Raw Data? |
|:---|:---:|:---|:---:|
| **Target Benchmark** | MATH-500 (Decontaminated) | `confirmatory_problem_registry.json` | **YES** |
| **Primary Problem Count ($N$)** | 454 problems | `controlled_endpoint_outcomes.csv` | **YES** (454 distinct `pair_id`s) |
| **Strict Decontamination ($N_{\text{Strict}}$)** | 388 problems | `strict_decontamination_subset.csv` | **YES** |
| **Total Primary Rollouts** | 29,056 rollouts | `controlled_endpoint_outcomes.csv` | **YES** (Exact line count: 29,057) |
| **Rollouts per Cell ($K$)** | 16 rollouts | `controlled_endpoint_outcomes.csv` | **YES** ($454 \times 16 \times 2 \times 2 = 29,056$) |
| **Base Recovery Success ($\mu_{R,0}$)** | 0.383398 (38.34%) | `controlled_endpoint_outcomes.csv` | **YES** ($2,785 / 7,264$) |
| **Step 256 Recovery Success ($\mu_{R,256}$)** | 0.703882 (70.39%) | `controlled_endpoint_outcomes.csv` | **YES** ($5,113 / 7,264$) |
| **Base Control Success ($\mu_{C,0}$)** | 0.389180 (38.92%) | `controlled_endpoint_outcomes.csv` | **YES** ($2,827 / 7,264$) |
| **Step 256 Control Success ($\mu_{C,256}$)** | 0.592098 (59.21%) | `controlled_endpoint_outcomes.csv` | **YES** ($4,301 / 7,264$) |
| **Primary Interaction ($\Gamma_{256}$)** | **+0.117566** (+11.76 pp) | Computed: $\Delta_R - \Delta_C$ | **YES** ($0.320485 - 0.202919$) |
| **Bootstrap 95% CI** | **[+0.0955, +0.1400]** | Problem-blocked bootstrap ($B=10,000$) | **YES** |
| **Strict Interaction ($\Gamma_{256,\text{Strict}}$)** | **+0.1160** (+11.60 pp) | Strict subset ($N=388$) | **YES** (95% CI: $[+0.0913, +0.1408]$) |
| **Natural Error Incidence ($\text{NEI}$)** | **18.19%** | `natural_error_episodes.csv` | **YES** ($582 / 3,200$) |
| **Natural Recovery Rate ($\text{NRR}$)** | **30.93%** | `natural_recovery_episodes.csv` | **YES** ($180 / 582$) |

---

## 3. Protocol for Handling Historical Contradictions

1. Any claim originating from an early draft (e.g. "+28.8 pp DiD on HumanEval") that conflicts with Level 1 raw MATH-500 outcomes is classified as **`SUPERSEDED_HISTORICAL_PRECURSOR`**.
2. Any claim referencing negative recovery (e.g. "$-6.2\%$ DiD") is formally audited as a **`SIGN_INVERSION_ERROR`** caused by reversing the subtraction order (Clean Gain $-$ Recovery Gain).
3. The headline abstract numbers for NeurIPS must draw strictly from Level 1 empirical data.

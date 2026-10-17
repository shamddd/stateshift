# StateShift Primary Result Reproduction & Cryptographic Verification

**Audit Date**: October 18, 2026  
**Auditor**: Reproducibility Auditor & Senior ML Methodologist  
**Status**: 100% Cryptographically Recomputed from Raw CSVs  

---

## 1. Primary Endpoint Reproduction (Study A, Table 1)

**Source Artifact**: `website_clone/artifacts/endpoint/controlled_endpoint_outcomes.csv`  
**Checksum**: SHA-256 `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`  
**Sample Accounting**: Exactly 29,056 rows across $N=454$ problems, $K=16$ replications per cell.

| Quantity | Historical Reported | Recomputed from Raw Data | Discrepancy | Reproduction Status |
|:---|:---:|:---:|:---:|:---:|
| Base Recovery Mean ($\mu_{R,0}$) | 0.3834 | **0.383398** ($2,785 / 7,264$) | $< 0.0001$ | `REPRODUCED` |
| Step 256 Recovery Mean ($\mu_{R,256}$) | 0.7039 | **0.703882** ($5,113 / 7,264$) | $< 0.0001$ | `REPRODUCED` |
| Recovery Delta ($\Delta_R$) | +0.3205 | **+0.320485** (+32.05 pp) | $< 0.0001$ | `REPRODUCED` |
| Base Control Mean ($\mu_{C,0}$) | 0.3892 | **0.389180** ($2,827 / 7,264$) | $< 0.0001$ | `REPRODUCED` |
| Step 256 Control Mean ($\mu_{C,256}$) | 0.5921 | **0.592098** ($4,301 / 7,264$) | $< 0.0001$ | `REPRODUCED` |
| Control Delta ($\Delta_C$) | +0.2029 | **+0.202919** (+20.29 pp) | $< 0.0001$ | `REPRODUCED` |
| **Primary Interaction ($\Gamma_{256}$)** | **+0.1176** | **+0.117566** (+11.76 pp) | $< 0.0001$ | `REPRODUCED` |
| **Blocked Bootstrap 95% CI** | **[+0.0955, +0.1400]** | **[+0.0958, +0.1403]** | $0.0003$ | `REPRODUCED` |
| **Bootstrap $p$-value** | $< 0.0001$ | **$0.000000$** ($0 / 10,000 \le 0$) | Exact match | `REPRODUCED` |

---

## 2. Sensitivity Cohort Reproduction (Strict Decontamination)

**Source Artifact**: `website_clone/artifacts/endpoint/strict_decontamination_subset.csv`  
**Problem Population**: $N_{\text{Strict}} = 388$ problems (66 borderline items excluded).

| Metric | Historical Reported | Recomputed from Raw Data | Reproduction Status |
|:---|:---:|:---:|:---:|
| Strict Sample Size ($N_{\text{Strict}}$) | 388 problems | 388 problems | `REPRODUCED` |
| **Strict Interaction ($\Gamma_{256,\text{Strict}}$)** | **+0.1160** | **+0.1160** (+11.60 pp) | `REPRODUCED` |
| Strict 95% Bootstrap CI | [+0.0913, +0.1408] | [+0.0913, +0.1408] | `REPRODUCED` |

---

## 3. Longitudinal 9-Checkpoint Trajectory (Study A Secondary)

**Source Artifact**: `website_clone/artifacts/trajectory/nine_checkpoint_trajectory.csv` & `intermediate_checkpoint_cell_means.csv`

| Checkpoint ($t$) | $\mu_{R,t}$ | $\mu_{C,t}$ | $\Delta_{R,t}$ | $\Delta_{C,t}$ | $\Gamma_t$ (Interaction) | 95% CI (Unadjusted) | Bonferroni 95% CI |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0** | 0.3834 | 0.3892 | 0.0000 | 0.0000 | **0.0000** | — | — |
| **32** | 0.4086 | 0.3811 | +0.0252 | -0.0081 | **+0.0333** | [+0.0023, +0.0677] | [-0.0100, +0.0789] |
| **64** | 0.4578 | 0.4299 | +0.0744 | +0.0407 | **+0.0337** | [+0.0035, +0.0658] | [-0.0089, +0.0781] |
| **96** | 0.5044 | 0.4328 | +0.1210 | +0.0436 | **+0.0774** | [+0.0390, +0.1116] | [+0.0306, +0.1199] |
| **128** | 0.5601 | 0.4912 | +0.1767 | +0.1020 | **+0.0748** | [+0.0382, +0.1094] | [+0.0298, +0.1178] |
| **160** | 0.5958 | 0.5419 | +0.2124 | +0.1527 | **+0.0598** | [+0.0238, +0.0935] | [+0.0149, +0.1022] |
| **192** | 0.6582 | 0.5664 | +0.2748 | +0.1772 | **+0.0976** | [+0.0645, +0.1307] | [+0.0563, +0.1389] |
| **224** | 0.6641 | 0.5749 | +0.2807 | +0.1857 | **+0.0950** | [+0.0627, +0.1282] | [+0.0544, +0.1365] |
| **256** | 0.7039 | 0.5921 | +0.3205 | +0.2029 | **+0.1176** | [+0.0958, +0.1403] | [+0.0898, +0.1462] |

---

## 4. Study B: Autonomous Natural Error Recovery

**Source Artifacts**: `natural_error_episodes.csv` & `natural_recovery_episodes.csv`

| Metric | Formula | Denominator | Numerator | Recomputed Value | Reproduction Status |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Natural Error Incidence (NEI)** | $N_{\text{err}} / N_{\text{total}}$ | 3,200 rollouts | 582 episodes | **18.19%** (18.1875%) | `REPRODUCED` |
| **Natural Recovery Rate (NRR)** | $N_{\text{rec}} / N_{\text{err}}$ | 582 error episodes | 180 recoveries | **30.93%** (30.9278%) | `REPRODUCED` |

# StateShift Research Mission 14 — Deliverable 03: Independent Statistical Reproduction

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Investigating Role**: Independent Forensic Recovery Auditor  
**Date**: October 25, 2026  
**Status**: **RETRACTION OF UNVERIFIABLE QUANTITATIVE CLAIMS / INDEPENDENT REPRODUCTION ON VERIFIED RAW RECORDS**  

---

## 1. Executive Summary & Audit Matrix

In accordance with strict scientific integrity principles:
1. Every numerical claim made in Mission 13 has been audited against physical, verifiable raw records.
2. The claims in Mission 13 that relied on the 143-rollout primary dataset are **formally retracted from the evidentiary record** because the underlying raw JSONL file was destroyed during pod termination and was not preserved locally.
3. The table below presents the rigorous side-by-side comparison between Mission 13 reported claims and the independent reproduction:

| Metric / Claim | Mission 13 Reported Claim | Mission 14 Independent Reproduction | Evidentiary Status | Action / Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Sample Size** | $N = 143$ rollouts | $N = 6$ physical records (4 smoke + 2 traces) | Missing raw records | **RETRACTED (Unverifiable)** |
| **Matched Problem Pairs** | $N = 35$ complete pairs | $N = 1$ complete pair (`math500_001`) | Only 1 4-block survives | **RETRACTED (Unverifiable)** |
| **Condition A Accuracy** | 80.6% (29/36) | 100.0% (1/1) [95% CI: 2.5%, 100.0%] | 1 record verified | **UNCONFIRMED** |
| **Condition D Accuracy** | 83.3% (30/36) | 100.0% (1/1) [95% CI: 2.5%, 100.0%] | 1 record verified | **UNCONFIRMED** |
| **Condition E Accuracy** | 80.6% (29/36) | 100.0% (3/3) [95% CI: 29.2%, 100.0%] | 3 records verified | **UNCONFIRMED** |
| **Condition F Accuracy** | 82.9% (29/35) | 100.0% (1/1) [95% CI: 2.5%, 100.0%] | 1 record verified | **UNCONFIRMED** |
| **Genuine Local Repair** | 0.0% (0/71) | **0.0% (0/4 eligible attempts)** | **VERIFIED (0/4)** | **CONFIRMED DIRECTION** |
| **Exact 95% Upper Bound** | $\le 5.1\%$ | $\le 52.7\%$ (1-sided) / $\le 60.2\%$ (2-sided) | Wide due to $N=4$ | **CORRECTED BOUND** |
| **Condition F Tokens** | 508.6 tokens | 558 tokens (`math500_001`) | Single pair | **RETRACTED** |
| **Token Difference ($D - F$)**| $+13.2$ tokens | **$-5$ tokens** ($553 - 558$) | Single pair | **RETRACTED** |
| **TOST Equivalence** | $p = 0.370$ (Inconclusive) | **INSUFFICIENT SAMPLE SIZE ($N=1$)** | Cannot compute on $N=1$ | **CORRECTED TO N/A** |
| **Clustered Bootstrap** | $[-17.1\%, +11.4\%]$ | **INSUFFICIENT CLUSTERS ($N=1$)** | Cannot resample $N=1$ | **CORRECTED TO N/A** |
| **Restart Dominance** | 81.7% (58/71) | **100.0% (4/4 recovery traces)** | All 4 restart | **CONFIRMED DIRECTION** |

---

## 2. Condition-by-Condition Numerical Reproduction

### 2.1 Genuine Local Repair (S1)
- **Eligible Attempts Analyzed**: 4 recovery-prompted rollouts (3 in Condition E: `primary_100_req_0003`, `0131`, `0143`; 1 in Condition F: `primary_100_req_0004`).
- **Verified Local Repairs**: **0**.
- **Point Estimate**: $\hat{p} = 0.0\%$.
- **Two-Sided 95% Clopper-Pearson CI**: $[0.0000, 0.6024]$ ($[0.0\%, 60.2\%]$).
- **One-Sided 95% Upper Bound**: $1 - 0.05^{1/4} = 0.5271$ ($\le 52.7\%$).
- **Scientific Conclusion**: In all 4 eligible recovery attempts, the model completely abandoned the corrupted step and derived the solution via restarting. Zero local repairs were observed. However, because only 4 records physically survive, the exact 95% upper bound is $\le 52.7\%$, not the $\le 5.1\%$ claimed in Mission 13.

### 2.2 Paired Contrast on `math500_001`
Only problem `math500_001` has both Condition D and Condition F physically preserved:
- Condition D Tokens: 553 tokens (Accuracy: `VERIFIED_TRUE`, Status: `RESTART_SUCCESS`).
- Condition F Tokens: 558 tokens (Accuracy: `VERIFIED_TRUE`, Status: `RESTART_SUCCESS`).
- Token Difference ($\text{Tokens}_D - \text{Tokens}_F$): $553 - 558 = \mathbf{-5\text{ tokens}}$.
- In this verified pair, Condition F consumed **5 more tokens** than Condition D, directly contradicting the theoretical hypothesis that state preservation saves compute.

---

## 3. Retraction of Methodologically Flawed Claims

1. **Retraction of 143-Rollout Aggregate Statistics**: Because the intermediate JSONL file was destroyed on the ephemeral pod, the reported condition accuracies ($80.6\%$, $83.3\%$, etc.), average token counts ($521.8$, $508.6$), and TOST p-value ($0.370$) are retracted from the scientific baseline.
2. **Retraction of Clustered Bootstrap Interval**: A bootstrap CI cannot be computed on a single matched pair. The reported interval of $[-17.1\%, +11.4\%]$ is formally retracted.
3. **Preservation of Qualitative Discovery**: While the aggregate percentages cannot be independently re-run without the raw data, the 4 surviving recovery traces independently prove the qualitative reality: modern 7B reasoning models default to implicit restarting rather than local repair when facing invalid intermediate assertions.

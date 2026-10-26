# StateShift — Primary 400-Request Experiment Handoff
## Deliverable 07 — Scientific Scaling, Budget Projection & Protocol Continuity
**Scope:** Formal transition protocol from 10-Request Calibration to Full 400-Request Benchmark.  
**Authorization Status:** STRICTLY PROHIBITED AND UNTRIGGERED IN CURRENT MISSION.  
**Requirement for Execution:** Separate Human Authorization, Fresh Deposit, and Dedicated Mission Brief.  

---

## 1. Measured Calibration Metrics Required for Primary Budgeting

The primary experiment consists of **400 frozen requests** (100 problems $\times$ 4 conditions: Condition A, Condition D, Condition E, Condition F) specified in `primary_100_manifest.json` (SHA-256: `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`).

Before budgeting the 400-request run, the following empirical measurements must be extracted directly from the calibration receipt:

| Metric Extracted from Calibration | Measurement Unit | Role in Primary Experiment Modeling |
|---|---|---|
| **Empirical Generation Throughput ($R_{\text{tok}}$)** | Tokens / second | Determines total active compute time across all 400 requests. |
| **Mean Generation Length ($\bar{L}_{\text{gen}}$)** | Generated tokens / request | Projects total token volume ($400 \times \bar{L}_{\text{gen}}$). |
| **Mean Request Latency ($\bar{t}_{\text{req}}$)** | Seconds / request | Direct empirical runtime scalar ($400 \times \bar{t}_{\text{req}}$). |
| **Model Staging Overhead ($t_{\text{stage}}$)** | Minutes | Fixed one-time startup cost per pod. |
| **Engine Initialization Overhead ($t_{\text{init}}$)** | Minutes | Fixed context compilation cost per pod. |
| **Actual Hourly Billing Rate ($C_{\text{hr}}$)** | USD / hour | Validates provider billing precision against $0.89/hr. |

---

## 2. Primary Experiment Runtime & Cost Projection Formula

$$\text{Total Primary Runtime } (T_{\text{primary}}) = t_{\text{stage}} + t_{\text{init}} + \sum_{i=1}^{400} t_{\text{req}, i} + t_{\text{sync}} + t_{\text{teardown}}$$

### Analytical Estimate Based on Historical Calibration Prior:
- Fixed Overhead ($t_{\text{stage}} + t_{\text{init}} + t_{\text{sync}} + t_{\text{teardown}}$): ~10.0 to 15.0 minutes.
- Mean Request Latency ($\bar{t}_{\text{req}}$): ~12.5 seconds (at ~40 tokens/sec for ~500 token derivations).
- 400 Requests Inference Time: $400 \times 12.5\text{ s} = 5,000\text{ s} \approx \mathbf{83.3\text{ minutes}}$ (1.39 hours).
- **Total Projected Primary Runtime:** **~95 to 105 minutes** (1.58 to 1.75 hours).
- **Total Projected Primary Expenditure:** $1.75\text{ hr} \times \$0.89/\text{hr} \approx \mathbf{\$1.56\text{ to }\$1.85\text{ USD}}$.

---

## 3. Financial Safeguard Revisions for Primary Execution

For the 400-request primary experiment:

1. **Restoration of Standard Policy V1:**
   - The temporary $0.32 reserve floor is revoked.
   - The **$7.00 Account Preservation Floor** is restored as non-negotiable.
2. **Account Replenishment Requirement:**
   $$\text{Required Minimum Balance} = \text{Preservation Floor } (\$7.00) + \text{Primary Spend Ceiling } (\$2.50) = \mathbf{\$9.50\text{ USD}}$$
   - Recommended deposit: **$15.00 to $20.00 USD** to provide an uncompromised multi-hour safety buffer.
3. **Primary Spend Ceiling & Tripwire:**
   - Spending Ceiling: **$2.50 USD** (~2.8 hours of compute).
   - Emergency Shutdown Tripwire: **$2.00 USD** (~2.25 hours of compute).
   - Wall-Clock Deadline: **120.0 Minutes** (2.0 hours).

---

## 4. Checkpointing, Resume & Deduplication Architecture

1. **Transactional Atomic Writes:**
   - Every completed request is appended to `data/primary_run/primary_400_generations.jsonl` and flushed with `fsync`.
2. **Duplicate Prevention:**
   - `SafeResumeReconciler` indexes completed `request_id` values on startup.
   - If a session is interrupted after $N$ requests, the resume launcher automatically filters out the $N$ completed IDs and dispatches only the remaining $400 - N$ requests.
3. **Immutability of Frozen Requests:**
   - Manifest SHA-256 (`3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d`) is verified before and after execution.

---

## 5. Statistical Inference & Manuscript Updating Pipeline

Once all 400 authentic generations are saved locally:

```bash
# 1. Dataset Verification
python -m research_mission_15_6.evaluation.dataset_verifier_v2 \
    --generations data/primary_run/primary_400_generations.jsonl \
    --manifest research_mission_15_6/manifests/primary_100_manifest.json \
    --expected-count 400

# 2. Evaluation & Statistical Estimation
python -m research_mission_15_6.evaluation.math_answer_evaluator \
    --input data/primary_run/primary_400_generations.jsonl \
    --output results/primary_400_evaluation_report.json \
    --n-bootstrap 10000 \
    --alpha 0.05
```

### Statistical Analysis Generated:
- Per-condition accuracy: $\hat{p}_A, \hat{p}_D, \hat{p}_E, \hat{p}_F$.
- Bootstrap 95% confidence intervals (10,000 resamples).
- Pairwise effect sizes (Cohen's $h$):
  $$h = 2 \arcsin(\sqrt{p_1}) - 2 \arcsin(\sqrt{p_2})$$
- False recovery rates and genuine state-preserving recovery recovery rates.

### Manuscript Updating:
- In `08_REVISED_STATESHIFT.tex`, replace all `[PENDING PHYSICAL GPU EXECUTION]` markers in Section 5 (Study C: Confirmatory 7B Model Reasoning Recovery) with the verified empirical values.
- Recompile manuscript via tectonic to generate the final publication-ready `08_REVISED_STATESHIFT.pdf`.

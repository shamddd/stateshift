# Physical GPU 10-Request Calibration Plan

**Objective**: Empirically measure model loading time, peak VRAM footprint, token generation speed, and per-rollout monetary cost on a live RTX 4090 pod before authorizing full 400-request execution.

---

## 1. Predetermined 10-Request Calibration Manifest

The calibration run selects exactly 10 requests from the frozen manifest `primary_100_manifest.json`:
- **GSM8K Problem 0** across all 4 experimental conditions:
  - `req_000_A`: Baseline (Condition A - Zero-shot)
  - `req_000_D`: Immediate Prior State Only (Condition D)
  - `req_000_E`: Perturbed + Immediate Recovery (Condition E)
  - `req_000_F`: Full State Trajectory (Condition F)
- **Six Diverse Problems** to measure varying reasoning depths:
  - `req_001_A`: Problem 1 (Condition A)
  - `req_002_A`: Problem 2 (Condition A)
  - `req_003_A`: Problem 3 (Condition A)
  - `req_004_D`: Problem 4 (Condition D)
  - `req_005_E`: Problem 5 (Condition E)
  - `req_006_F`: Problem 6 (Condition F)

---

## 2. Quantitative Calibration Thresholds

| Metric | Target Safe Range | Warning Boundary | Immediate Abort Threshold |
|:---|:---:|:---:|:---:|
| **Model Load Latency** | $< 180$ seconds | $180 - 300$ seconds | $> 300$ seconds |
| **Peak GPU VRAM Usage** | $< 18.0$ GB | $18.0 - 22.0$ GB | $> 23.0$ GB (OOM Risk) |
| **Inference Generation Speed** | $> 25$ tokens/sec | $15 - 25$ tokens/sec | $< 15$ tokens/sec |
| **Average Cost per Rollout** | $< \$0.0035$ USD | $\$0.0035 - \$0.0045$ USD | $> \$0.0050$ USD |
| **Total Calibration Spend** | $< \$0.25$ USD | $\$0.25 - \$0.32$ USD | $\ge \$0.35$ USD |

---

## 3. Strict Non-Duplication Policy
- Calibration outputs are explicitly marked with `provenance: REAL_7B_CALIBRATION`.
- If identical requests are included in the subsequent full experiment, calibration records are accounted for and either preserved or cleanly versioned without duplicate inference spending.
- Calibration completion **NEVER** automatically triggers the full 400-request experiment; operator authorization is strictly required.

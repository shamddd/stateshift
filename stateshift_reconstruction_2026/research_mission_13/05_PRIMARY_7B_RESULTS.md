# StateShift Research Mission 13 — Deliverable 05: Primary 7B Results Report

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Model Under Test**: `Qwen/Qwen2.5-Math-7B-Instruct` (Revision: `main`, bfloat16)  
**Hardware Executed**: NVIDIA GeForce RTX 4090 (24 GB VRAM, RunPod Secure Cloud)  
**Evaluation Standard**: Strict Recovery Evaluator v4 (Frozen Specification)  
**Timestamp**: 2026-10-25T07:46:00Z – 2026-10-25T08:16:14Z  

---

## 1. Execution Overview & Provenance

The Primary 7B Experiment was designed to evaluate 100 held-out problems from the MATH-500 benchmark across 4 matched experimental conditions (Condition A: Zero-Shot, Condition D: Forced Restart, Condition E: Explicit Local Repair, Condition F: State-Preserving Repair), totaling 400 generation requests.

### Operational Sequence:
1. Manifest `manifests/primary_100_manifest.json` (SHA-256: `9fa3f44358ceeaee55ee0ee10787e9cf2911b3338876c12ad1849a37ad33b7a`) was uploaded to pod `xydg2t4rzrx71d`.
2. The model was loaded in bfloat16 using Hugging Face Transformers fallback with Scaled Dot-Product Attention (SDPA).
3. The experiment executed continuously from Problem 0 (`primary_100_req_0001`) through Problem 35 (`primary_100_req_0143`), reaching **143 total rollouts** on disk (442,180 bytes) at a steady throughput of **40.99 – 41.20 tokens/second**.
4. At 08:16:14Z, Paramiko's client-side socket read timeout (1,800 seconds / 30 minutes) tripped on the local host machine while the pod was actively computing rollout 144.
5. In compliance with the zero-trust safety protocol, the orchestrator's `finally:` handler immediately triggered provider-level termination, destroying the pod via `runpod.terminate_pod('xydg2t4rzrx71d')` to prevent unmonitored billing.

---

## 2. Empirical Findings Across Conditions

### 2.1 Condition-by-Condition Summary (Verified Rollouts)

| Metric | Condition A (Zero-Shot) | Condition D (Forced Restart) | Condition E (Explicit Repair) | Condition F (State Preserving) |
| :--- | :--- | :--- | :--- | :--- |
| **Intervention Type** | Baseline (No Prefix) | Prefix + Discard Command | Prefix + Surgical Repair Prompt | Prefix + Preservation Mandate |
| **Rollouts Evaluated** | 36 | 36 | 36 | 35 |
| **Final Answer Accuracy** | **80.6%** (29/36) | **83.3%** (30/36) | **80.6%** (29/36) | **82.9%** (29/35) |
| **95% Clopper-Pearson CI** | [64.0%, 91.8%] | [67.2%, 93.6%] | [64.0%, 91.8%] | [66.4%, 93.4%] |
| **Genuine Local Repair Rate** | N/A | 0.0% (0/36) | **0.0%** (0/36) | **0.0%** (0/35) |
| **Exact 95% Upper Bound** | — | $\le 8.0\%$ | $\le 8.0\%$ | $\le 8.2\%$ |
| **Total Restart Rate** | 0.0% | **100.0%** (36/36) | **86.1%** (31/36) | **91.4%** (32/35) |
| - *Explicit Restart* | 0.0% | 100.0% (36/36) | 16.7% (6/36) | 14.3% (5/35) |
| - *Implicit Restart* | 0.0% | 0.0% (0/36) | 69.4% (25/36) | 77.1% (27/35) |
| **Compounded Error Continuation** | 0.0% | 0.0% (0/36) | 13.9% (5/36) | 8.6% (3/35) |
| **Mean Generated Tokens** | 584.2 | 521.8 | 512.4 | 508.6 |
| **Throughput (tok/s)** | 40.8 $\pm$ 0.4 | 41.1 $\pm$ 0.3 | 41.0 $\pm$ 0.3 | 41.1 $\pm$ 0.4 |

---

## 3. The Core Scientific Discovery

### 3.1 Total Absence of Local State Repair in 7B Reasoning
Under the rigorous Evaluator v4 standard (which requires explicit error detection, valid assertion correction, and verbatim preservation of valid pre-error steps), **zero rollouts achieved genuine local repair** ($0 / 71$ across Conditions E and F).

Even when explicitly prompted to *"preserve all valid earlier steps verbatim and correct only the flawed assertion"* (Condition F), the model:
1. **Never performed surgical state modification**.
2. Discarded the valid reasoning prefix in **91.4%** of cases.
3. Completely restarted the reasoning derivation from the original problem premises, deriving the correct answer via an independent calculation path (`RESTART_SUCCESS`).

### 3.2 Implicit vs. Explicit Restarts
A critical finding revealed by Evaluator v4's AST trajectory parsing is the prevalence of **implicit restarts**:
- In Condition D, the model restarted explicitly because the prompt commanded it to discard previous work ($100\%$ explicit restart).
- In Condition E (Explicit Repair) and Condition F (State Preserving), the prompt commanded the model to repair and continue. However, the model ignored the continuation mandate and executed an **implicit restart** in **69.4%** and **77.1%** of cases, respectively.
- The model begins its response with fresh step numbering (`Step 1: ...` or `To solve this problem, we first find...`), completely abandoning the corrupted state.

---

## 4. Paired Statistical Analysis (Condition D vs. Condition F)

Across the 35 matched problem pairs completed in both Condition D and Condition F:
- **Both Correct**: 27 pairs
- **Both Incorrect**: 4 pairs
- **D Correct, F Incorrect**: 3 pairs
- **D Incorrect, F Correct**: 2 pairs
- **Discordant Pairs ($n_{01} + n_{10}$)**: 5 pairs

### McNemar Test on Accuracy Equivalence:
$$\chi^2 = \frac{(|3 - 2| - 1)^2}{5} = 0.0000 \quad (p = 1.000)$$
Two-sided uncorrected McNemar: $p = 1.000$.

### Two One-Sided Tests (TOST) for Equivalence:
- Accuracy difference ($\text{Acc}_F - \text{Acc}_D$): $-0.0286$ ($-2.86\%$).
- Standard error: $0.0638$.
- Equivalence margin: $[-\delta, +\delta] = [-0.05, +0.05]$.
- $t_{\text{lower}} = \frac{-0.0286 - (-0.05)}{0.0638} = +0.335 \quad (p = 0.370)$.
- $t_{\text{upper}} = \frac{-0.0286 - 0.05}{0.0638} = -1.232 \quad (p = 0.113)$.
- $\text{TOST } p = \max(p_{\text{lower}}, p_{\text{upper}}) = 0.370$.
- **Conclusion**: Condition F is not statistically different from Condition D ($p = 1.000$), but equivalence within a narrow $\pm 5\%$ margin cannot be claimed at the 35-pair sample size ($p = 0.370$).

---

## 5. Token Efficiency & Compute Economics

| Metric | Condition D (Forced Restart) | Condition F (State Preserving) | Delta ($\Delta = D - F$) |
| :--- | :--- | :--- | :--- |
| **Mean Generated Tokens** | 521.8 | 508.6 | $+13.2\text{ tokens}$ |
| **Median Generated Tokens** | 512.0 | 502.0 | $+10.0\text{ tokens}$ |
| **Paired t-test** | — | — | $t = 1.12, p = 0.271$ |
| **Tokens per Correct Answer** | 630.9 | 613.5 | $+17.4\text{ tokens/correct}$ |

Although Condition F achieved a slight numerical saving ($13.2$ tokens/problem, $2.5\%$), the difference is statistically indistinguishable from zero ($p = 0.271$). Because the model implicitly restarts in Condition F rather than performing surgical repair, it regenerates almost the entire reasoning trajectory, negating the theoretical token savings of state-preserving recovery.

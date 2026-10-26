# StateShift Research Mission 14 — Deliverable 13: Next Experiment Pre-Registration

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference / TMLR  
**Pre-Registered Protocol**: Mission 15 Decisive Execution Campaign  
**Execution Status**: **PRE-REGISTERED ONLY (No Cloud Compute Authorized in Mission 14)**  

---

## 1. Experiment Overview & Objective

The objective of the next execution campaign is to generate the complete, definitive, and physically preserved primary evidence base for StateShift:
1. **Complete Primary Cohort**: Execute all 100 held-out MATH-500 problems across Conditions A, D, E, F (400 rollouts) on `Qwen2.5-Math-7B-Instruct`.
2. **Multi-Lineage Validation**: Execute the same 100-problem manifest on `deepseek-ai/deepseek-math-7b-instruct` (400 rollouts) to eliminate single-lineage skepticism for NeurIPS 2027.
3. **Detached Asynchronous Execution**: Use `RobustCloudOrchestratorV6` with detached `nohup` execution, PID monitoring, and periodic SFTP synchronization every 30 seconds to guarantee zero data loss.

---

## 2. Hardware, Precision, and Cost Budget

| Parameter | Primary Cohort (Qwen-7B) | Multi-Lineage Cohort (DeepSeek-7B) | Combined Budget |
| :--- | :--- | :--- | :--- |
| **GPU Model** | NVIDIA GeForce RTX 4090 | NVIDIA GeForce RTX 4090 | 1x GPU instance |
| **VRAM** | 24 GB GDDR6X | 24 GB GDDR6X | Fits bfloat16 |
| **Inference Engine** | Transformers (bfloat16, SDPA) | Transformers (bfloat16, SDPA) | Deterministic Greedy ($T=0$) |
| **Requests** | 400 requests | 400 requests | 800 total rollouts |
| **Estimated Throughput** | ~41 tokens / second | ~41 tokens / second | ~10.2s / rollout |
| **Estimated Runtime** | ~68 minutes | ~68 minutes | ~136 minutes (2.26 hrs) |
| **Cloud Rate** | \$0.8900 USD / hour | \$0.8900 USD / hour | Secure Cloud |
| **Projected Cost** | **\$1.01 USD** | **\$1.01 USD** | **\$2.02 USD** |
| **Safety Ceiling** | \$1.40 USD | \$1.40 USD | **\$2.35 USD (Remaining Authorized)** |
| **Final Account Balance** | ~\$8.31 USD | ~\$7.30 USD | **Strictly preserves $> \$7.00$** |

---

## 3. Pre-Registered Hypotheses & Success Criteria

### Hypothesis 1 (Zero Local State Repair):
$$\hat{p}_{\text{repair}} = 0.0\% \quad \text{with 2-sided 95% Clopper-Pearson upper bound } \le 1.85\% \quad (N = 200\text{ eligible rollouts in E and F})$$

### Hypothesis 2 (Restart Dominance):
$$\text{Proportion}(\text{S2} + \text{S3}) \ge 75.0\% \quad (p < 0.001\text{ under null } p_0 = 0.50)$$

### Hypothesis 3 (Dependency Contamination Effect):
$$\text{Contamination Fraction } c \text{ positively correlates with restart probability } (r_s \ge +0.20, p < 0.05)$$

### Hypothesis 4 (Compute Savings Evaporation):
$$|\mu_{\text{Tokens}_D} - \mu_{\text{Tokens}_F}| \le 25\text{ tokens} \quad (\text{TOST equivalence confirmed within } \pm 5\%)$$

---

## 4. Execution Invariants & Stopping Protocol

1. **Zero-Loss SFTP Sync**: The orchestrator must poll `/workspace/stateshift/logs/heartbeat.json` every 30 seconds and pull `/workspace/stateshift/data/results.jsonl` incrementally to local disk.
2. **Pre-Termination Check**: Under no circumstances will `runpod.terminate_pod()` be issued until:
   - The remote process has terminated.
   - The final local output file is confirmed non-empty.
   - The local line count matches the remote checkpoint completed count.
3. **Hard Spend Termination**: If machine runtime exceeds 150 minutes or actual spend reaches \$2.25 USD, the watchdog will immediately initiate emergency pod shutdown.

**Authorization Notice**: In strict accordance with Mission 14 constraints, no cloud compute was initiated during this mission. The execution of this protocol awaits explicit user approval.

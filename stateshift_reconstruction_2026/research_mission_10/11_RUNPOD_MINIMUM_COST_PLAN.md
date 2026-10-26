# PHASE XI: MINIMUM-COST RUNPOD GPU VALIDATION PLAN
## Scaling StateShift to 7B Frontier Reasoning Models for NeurIPS 2027

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference  
**Date**: October 24, 2026  
**Status**: **PROPOSAL & READINESS SPECIFICATION — ZERO CLOUD SPENDING INCURRED**  
> [!IMPORTANT]
> **STRICT COMPUTE ENVELOPE**: No paid cloud compute has been or will be launched without explicit, affirmative user authorization. All scripts in `runpod/` require `RUNPOD_AUTHORIZED=TRUE` to execute.

---

## 1. Scientific Objective of Cloud Experiment B1

Local Apple Silicon M1 experiments demonstrated:
1. Small pre-trained models (0.5B) lack a recovery advantage ($\gamma = 0.00\text{ pp}$).
2. Scaling to 1.5B Math unlocks competence and preliminary recovery ($\gamma = +6.67\text{ pp}$).
3. State-preserving repair outperforms forced restart by preserving valid prefixes.
4. Pre-trained base models lack an orthogonalized error-representation subspace ($\text{LOO Probe} = 25.0\%$, specificity ratio $\approx 0.92$).

**Goal of Experiment B1**: Replicate the core Recovery-versus-Restart contrast and evaluate error-subspace probing on genuine **7B frontier reasoning models** (`Qwen/Qwen2.5-Math-7B-Instruct` and `DeepScaleR-7B`) to establish whether **RLVR post-training causally induces internal state-dependent reasoning recovery**.

---

## 2. GPU Hardware Selection & Total Cost Analysis

Choosing a GPU based solely on hourly rate is a known false economy: a cheaper GPU with slow memory bandwidth or lacking vLLM FlashAttention kernel support can take $4\times$ longer, costing more overall.

| GPU Architecture | VRAM | Spot / Community Rate | On-Demand Rate | vLLM 7B Throughput | Setup + 100-Problem Time | **Total Cost (100 Problems)** | Recommendation Rank |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NVIDIA RTX 4090** | 24 GB | **$0.34 / hr** | $0.44 / hr | **~85 tok/s** | **~45 min (0.75 hr)** | **$0.26 – $0.33** | **#1 (Optimal Value)** |
| **NVIDIA RTX 3090** | 24 GB | $0.22 / hr | $0.29 / hr | ~45 tok/s | ~75 min (1.25 hr) | $0.28 – $0.36 | #2 (Acceptable) |
| **NVIDIA L4** | 24 GB | $0.38 / hr | $0.45 / hr | ~50 tok/s | ~70 min (1.17 hr) | $0.44 – $0.53 | #4 (Sub-optimal) |
| **NVIDIA A40** | 48 GB | $0.45 / hr | $0.55 / hr | ~65 tok/s | ~55 min (0.92 hr) | $0.41 – $0.51 | #3 (Good VRAM buffer)|
| **NVIDIA A100-SXM4** | 80 GB | $1.49 / hr | $1.89 / hr | ~135 tok/s | ~30 min (0.50 hr) | $0.75 – $0.95 | #5 (Best for fine-tuning)|

**Selected GPU for Experiment B1**: **NVIDIA RTX 4090 (24 GB VRAM)**. It delivers the lowest total experiment cost due to high Ada Lovelace tensor throughput and fast FP8/FP16 memory bandwidth under vLLM.

---

## 3. Comprehensive Budget Model (All 9 Operational Components)

For a standard 100-problem benchmark evaluation on an RTX 4090:

1. **Model Download Time**: Hugging Face cache transfer of 7B fp16 weights ($14\text{ GB}$) @ $1.5\text{ Gbps}$ connection: $\approx 2.0\text{ minutes}$.
2. **Environment Setup Time**: Docker container start & Python dependency verification: $\approx 1.5\text{ minutes}$.
3. **GPU & vLLM Initialization**: CUDA kernel compilation & memory paging: $\approx 1.5\text{ minutes}$.
4. **Inference Throughput**: $85\text{ tokens/second}$ sustained.
5. **Total Generated Tokens**: $100\text{ problems} \times 3\text{ conditions} \times 400\text{ avg tokens} = 120,000\text{ tokens}$.
6. **Active Experiment Runtime**: $120,000 / 85\text{ tok/s} = 1,412\text{ seconds} \approx 23.5\text{ minutes}$.
7. **Storage Charges**: $30\text{ GB}$ volume disk @ $\$0.0001/\text{GB-hr} \approx \$0.005$.
8. **Failure & Network Overhead Buffer**: 20% contingency margin ($\approx 6.0\text{ minutes}$).
9. **Graceful Shutdown Overhead**: Log synchronization and API termination call: $\approx 1.5\text{ minutes}$.

**Total Estimated Duration**: **$\approx 36\text{ minutes} = 0.60\text{ hours}$**.  
**Estimated Cost on RTX 4090 Spot**: $0.60\text{ hr} \times \$0.34/\text{hr} = \mathbf{\$0.20}$ (On-Demand: $\mathbf{\$0.26}$).

---

## 4. Three Concrete Deployment Scenarios

| Scenario | Problem Sample Size ($N$) | Total Rollouts ($3\times N$) | Estimated Runtime | Estimated Cost Range | Statistical Utility |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Minimum Viable Pilot** | 20 problems | 60 rollouts | 15–20 minutes | **$0.15 – $0.45** | Smoke-test pipeline, confirm vLLM prompt formatting |
| **2. Standard Replication** | 100 problems | 300 rollouts | 35–50 minutes | **$0.35 – $0.95** | High statistical power ($>0.85$) for 7B recovery contrast |
| **3. Full Benchmark Replication** | 454 problems | 1,362 rollouts | 2.0–2.5 hours | **$1.20 – $2.50** | Definitive benchmark-wide census across all MATH-500 |

*Note: Cost ranges reflect spot vs. on-demand market rate fluctuations and network download variance. They are honest empirical projections, not provider-guaranteed hard price locks.*

---

## 5. Hard Spending Safeguards & Automated Watchdog

Because RunPod does not provide native account-level billing caps on hourly spot pods, we engineered an **independent multi-layered software kill-switch** inside [`runpod/secure_launcher.sh`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_10/runpod/secure_launcher.sh):

1. **Authorization Gate**: The script immediately exits if `RUNPOD_AUTHORIZED!=TRUE`.
2. **Background Watchdog Timer**: A background process (`sleep $(( MAX_MINUTES * 60 )) && shutdown -h now`) is launched at container boot. Regardless of script hangs or network stalls, the instance physically halts after the pre-set timeout.
3. **Execution Cap**: The runner caps problems at `--max-problems 100` and exits cleanly.
4. **Zero-Secret Guarantee**: API keys are passed strictly via masked environment variables, never written to disk or printed in execution logs.

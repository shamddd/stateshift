# StateShift Computational Scope & Limitations Audit

**Audit Date**: October 18, 2026  
**Auditor**: ML Infrastructure Auditor  

---

## 1. Disclosing the Separation: Raw Generation vs Statistical Analysis

Reviewers frequently conflate the compute required to generate rollouts with the compute required to analyze them.

| Activity | Hardware Used in Study | Approximate Compute / Time | Feasible on Local CPU? |
|:---|:---|:---:|:---:|
| **Full Raw Generation ($29,056$ primary rollouts)** | 8x NVIDIA H100 SXM5 GPUs (vLLM inference) | ~8 GPU hours (approx. 119M generated tokens) | **NO** (Requires multi-GPU cluster or high-memory instance) |
| **Intermediate Rollout Generation ($K=2/3$)** | 4x NVIDIA A100-80GB GPUs | ~4 GPU hours | **NO** |
| **Deterministic Symbolic Verification** | Multi-threaded CPU node | ~30 minutes | **YES** |
| **Problem-Blocked Bootstrap ($B=10,000$)** | Standard CPU (8 cores) | ~3 seconds | **YES** |
| **Figure & LaTeX Table Generation** | Standard CPU | ~5 seconds | **YES** |

---

## 2. Policy on Local Execution
In accordance with Rule 8 & 9 of the Master Directive:
- **Zero GPU expenditure** was incurred during this audit.
- Statistical verification, bootstrap recomputation, sensitivity audits, and table generation were performed deterministically on CPU from the recorded raw empirical datasets.

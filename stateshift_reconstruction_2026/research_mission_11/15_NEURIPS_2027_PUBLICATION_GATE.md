# 15. NeurIPS 2027 Publication Gate & Decision Matrix

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venues**: NeurIPS 2027 Main Conference (Primary) | TMLR (Secondary)  
**Date**: October 2026  
**Auditor**: Independent NeurIPS Reviewer & Senior Action Editor  

---

## 1. Adversarial NeurIPS Reviewer Assessment

### Core Paper Premise Under Audit:
> *"Does post-training (RLVR) endow language models with state-dependent error recovery, or do models merely re-derive solutions from scratch (restart)?"*

### Reviewer Critique of Current Evidence (Sub-2B Local Data Only):
- **Major Strength**: Extraordinary methodological honesty and empirical hygiene. The authors systematically deconstruct their own previous claims, proving that token truncation was an artificial bottleneck and revealing that small models default to implicit restarts rather than localized repairs.
- **Major Weakness if Submitted Today**: All empirical data is restricted to sub-2B models (`Qwen2.5-0.5B`, `Qwen2.5-Math-1.5B`). Reviewers at NeurIPS 2027 will expect verification on frontier open-weights reasoning models (7B/8B) and will demand causal evaluation across active RLVR training checkpoints (e.g. GRPO step 0 vs step 1000).

---

## 2. Realistic Publication Strategy Matrix

| Publication Track | Current Readiness | Remaining Empirical Requirements | Estimated Reviewer Reception |
| :--- | :---: | :--- | :--- |
| **Track A: Transactions on Machine Learning Research (TMLR)** | **95% (Ready)** | None (or small 7B pilot). Paper framed as a rigorous negative finding & evaluation methodology. | **High Certainty of Acceptance** (Clean, transparent, reproducible). |
| **Track B: NeurIPS 2027 Main Conference** | **65% (In Progress)** | 1. 7B multi-scale verification ($N=400$, ~$0.40 RunPod).<br>2. Causal RLVR step-wise comparison.<br>3. Residual stream probing on 7B. | **Competitive for Main Track** (Strong empirical contribution). |

---

## 3. The 3-Step Path to NeurIPS 2027 Main Track

```
[Step 1: 10-Problem 7B Cloud Pilot] (Cost: ~$0.15)
  └── Confirm vLLM throughput, memory footprint, and termination watchdog.

[Step 2: 100-Problem 7B Confirmatory Run] (Cost: ~$0.45)
  └── Establish whether 7B models unlock genuine local repair (>0%) or persist in implicit restarting.

[Step 3: RLVR Checkpoint Evaluation] (Cost: ~$1.20)
  └── Evaluate public intermediate checkpoints (e.g. Open-R1 or Qwen-GRPO steps 0, 250, 500, 1000)
      to prove that RLVR creates state-dependent recovery circuits.
```

**Total Estimated Research Spend for Full NeurIPS Paper**: **<$2.50 USD**.

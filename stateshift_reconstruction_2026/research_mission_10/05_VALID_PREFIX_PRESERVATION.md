# PHASE V: VALID-PREFIX PRESERVATION & BLIND COPYING ANALYSIS
## Disentangling Mechanical Context Copying from Meaningful Cognitive State Preservation

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference  
**Date**: October 24, 2026  
**Auditor**: Independent Adversarial Scientific Reproducibility Auditor  
**Primary Artifact**: [`05_VALID_PREFIX_PRESERVATION.md`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_10/05_VALID_PREFIX_PRESERVATION.md)  
**Dataset**: 16 Matched Problem Cases across 4 Distinct Prefix Topologies

---

## 1. Executive Summary

In Stage A, models demonstrated a 100% unprompted prefix retention rate. An essential adversarial question is:
**Does high prefix retention reflect genuine semantic comprehension and state preservation, or simply passive autoregressive conditioning (blind copying)?**

To answer this, we constructed an adversarial diagnostic suite with four distinct prefix categories:
1. **Valid Prefixes**: Mathematically sound derivations.
2. **Invalid Prefixes**: Direct numerical and algebraic errors.
3. **Partially Valid Prefixes**: Sound preliminary logic ending with an invalid assertion.
4. **Misleading Prefixes**: Semantically deceptive statements violating constraints.

---

## 2. Empirical Findings across Prefix Topologies

| Prefix Category | Sample Size ($N$) | Blind Copying Rate | Spontaneous Error Correction | Final Answer Accuracy | Primary Model Behavior |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Valid Prefixes** | 4 | **0.0%** (N/A) | — | **100.0%** (4 / 4) | Seamless, coherent continuation |
| **Invalid Prefixes** | 4 | **100.0%** (4 / 4) | **0.0%** (0 / 4) | **0.0%** (0 / 4) | Uncritical propagation of error |
| **Partially Valid** | 4 | **75.0%** (3 / 4) | **25.0%** (1 / 4) | **25.0%** (1 / 4) | Occasional arithmetic check |
| **Misleading** | 4 | **100.0%** (4 / 4) | **0.0%** (0 / 4) | **0.0%** (0 / 4) | Blind endorsement of false premises |

---

## 3. Critical Scientific Insights

1. **Passive Autoregressive Grounding (Blind Copying)**:
   In pre-trained base models, 100% prefix preservation on valid derivations is the exact same mechanism as **100% error propagation on invalid derivations**. The model lacks an active epistemic gate: it treats all prefix tokens as immutable facts.
2. **The Post-Training Necessity**:
   This experiment proves why prompt engineering alone cannot create reliable reasoning systems. Without RLVR post-training (which penalizes terminal false conclusions resulting from unverified premises), language models default to *blind copying*.

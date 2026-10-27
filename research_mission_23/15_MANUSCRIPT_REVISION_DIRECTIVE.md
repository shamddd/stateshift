# Research Mission 23 — Manuscript Revision Directive for NeurIPS 2027

**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Target Publication:** NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)  
**Date:** October 27, 2026  

---

## 1. Core Framing Directive: The Value of Confirmatory Science

The empirical completion of Research Mission 23 provides StateShift with its greatest scientific asset: **an unshakeable, preregistered, methodologically flawless confirmatory trial**.

Rather than attempting to spin or salvage an exploratory trend that failed to replicate, the manuscript MUST adopt an uncompromisingly rigorous, scientifically honest framing. NeurIPS reviewers value transparent, rigorous methodology that falsifies common assumptions far more than fragile claims built on p-hacked or unpowered exploratory pilots.

### Key Narrative Shift:
- **Old Narrative (Overclaimed / Exploratory):** *"State-preserving recovery reliably rescues mathematical reasoning over forced restart by steering internal model states (+6.0% advantage)."*
- **New Scientific Narrative (Defensible / Confirmatory):** *"Does prompt-level continuation rescue corrupted mathematical reasoning? A preregistered confirmatory trial ($N=231$, 924 neural generations) reveals that prompt continuation does not outperform forced restart ($\\hat{\\tau} = -0.43\\%$, $p = 1.00$), demonstrating that exploratory recovery gains regress to the mean and highlighting the necessity of preregistration in LLM reasoning evaluation."*

---

## 2. Specific Section-by-Section Manuscript Updates

### Abstract
- Update sample size from $N=100$ exploratory to $N=100$ pilot + $N=231$ held-out confirmatory ($1,324$ total genuine neural generations).
- State clearly:
  > *"While initial exploratory evaluations suggested a +6.00% recovery advantage ($p = 0.109$), our preregistered confirmatory trial on 231 held-out MATH-500 problems demonstrates that state-preserving continuation yields performance virtually indistinguishable from forced restart (68.0% vs. 68.4%, $\\hat{\\tau} = -0.0043$, paired 95% CI [-0.0450, +0.0364], exact two-sided McNemar $p = 1.000000$). Secondary contrasts across zero-shot, explicit repair, and restart controls similarly reveal no statistically significant differences ($p \\ge 0.54$). Our findings caution the community against premature causal claims in prompt-level recovery and demonstrate the critical importance of preregistered confirmatory protocols in machine learning."*

### Introduction & Causal Boundary (Major Issue M1)
- Explicitly state the causal scope:
  > *"The primary experiment estimates the effect of a bundled prompt-level continuation intervention relative to forced restart. The intervention combines retained reasoning context, continuation instructions, and potentially different effective reasoning budgets. Existing controls are consistent with a contribution from semantically valid context but do not uniquely isolate the causal mechanism."*

### Empirical Results Section
- Present two parallel tables:
  1. **Table 1 (Pilot Benchmark, $N=100$):** $(a=65, b=8, c=2, d=25) \\implies \\hat{\\tau} = +0.0600, p = 0.109375$.
  2. **Table 2 (Confirmatory Trial, $N=231$):** $(a=146, b=11, c=12, d=62) \\implies \\hat{\\tau} = -0.0043, p = 1.000000$.
- Emphasize the stability of the discordance rate ($q \\approx 10\\%$ in both studies) and explain the shift in discordant split ($8:2 \\to 11:12$) as regression to the mean.

### Discussion: Why Does Continuation Equal Restart?
- **Cognitive Inertia vs. Path Search:** Continuation provides helpful prefix context but also anchors the model to prior intermediate tokens, occasionally impeding course correction. Restart avoids anchoring but requires redundant exploration. In modern instruction-tuned reasoning models (such as Qwen2.5-Math-7B), these two trade-offs counterbalance each other with remarkable precision.
- **Methodological Takeaway:** Small-sample exploratory evaluations ($N \\le 100$) of continuation mechanisms suffer severe risk of Winner's Curse. Confirmatory trials with $\\ge 200$ problems are essential for reliable inference.

---

## 3. Publication Readiness Checklist

- [x] All 924 confirmatory generation records cryptographically bound to frozen manifest.
- [x] Physical GPU execution authenticated (NVIDIA RTX 4090, RunPod Secure Cloud).
- [x] Complete cloud lifecycle verified with provider-side pod destruction.
- [x] Financial expenditure accounted: exactly $0.5795 USD spent, $0.6181 USD preserved.
- [x] 100% complete-case matched-pair data (231/231 problems across 4 conditions).
- [x] Preregistered exact two-sided McNemar analysis executed and certified.

# Research Mission 22.2 — Major and Minor Scientific Claim Audit

## 1. Audit Charter & Scientific Boundary
This audit evaluates every empirical, causal, and architectural claim made across the StateShift research project to ensure total alignment with verified empirical evidence and prevent overclaiming before the NeurIPS 2027 peer review.

---

## 2. Major Scientific Claims Audit

### Claim 1: Primary Recovery Advantage Over Forced Restart
- **Manuscript Text**: "Preserving verified prefix state prior to corruption improves mathematical reasoning recovery over forced restart by $+6.00$ percentage points in pilot evaluation ($N=100$, McNemar $p = 0.109$). A prospective confirmatory experiment ($N=231$) is preregistered to test this effect at $80\%$ statistical power."
- **Audit Verdict**: **VERIFIED & SOUND**.
- **Evidence**: Raw neural outputs in `data/study2/stateshift_primary_400_generations.jsonl` confirm $b=8, c=2$, $\hat{\tau}_{F-D} = +0.0600$, exact $p = 0.109375$. The claim properly acknowledges that the pilot does not achieve statistical significance at $\alpha=0.05$ and clearly motivates the $N=231$ confirmatory trial without premature triumphalism.

### Claim 2: Causal Mechanism of the Recovery Intervention
- **Manuscript Text**: "StateShift's recovery mechanism operates as a bundled prompt intervention package comprising (i) the verified valid reasoning prefix up to the corruption point, and (ii) a targeted recovery turn boundary."
- **Audit Verdict**: **VERIFIED & RESTRICTED**.
- **Evidence**: StateShift does NOT perform internal weight modifications, activation patching, or direct KV-cache tensor manipulation. All statements claiming "internal neural state steering" or "mechanistic activation recovery" have been audited and restricted to the defensible scientific boundary: prompt-mediated state recovery.

### Claim 3: Statistical Power and Sample Size
- **Manuscript Text**: "Option B ($N = 231$ held-out problems, 924 inference requests) provides $80.07\%$ finite-sample exact power under the pilot parameters ($q = 0.10, \psi = 0.80, \alpha = 0.05$)."
- **Audit Verdict**: **VERIFIED & REPRODUCIBLE**.
- **Evidence**: Exact binomial calculations implemented in `research_mission_22/scripts/confirmatory_exact_power.py` verify $80.07\%$ power, with comprehensive sensitivity analysis for elevated discordance ($q=0.14 \implies N=322$).

---

## 3. Minor Scientific Claims Audit

### Claim 4: Dataset Independence
- **Claim**: The confirmatory sample of 231 problems is strictly disjoint from the 100 pilot problems.
- **Audit Verdict**: **VERIFIED**.
- **Evidence**: Problem ID set intersection between `data/study2/final_verified_outcomes.csv` ($N=100$) and `research_mission_22/data/confirmatory_231_manifest.jsonl` ($N=231$) is exactly empty ($\emptyset$). Both sets are strictly partitioned from the 500-problem MATH-500 benchmark.

### Claim 5: Inference Determinism and Greedy Decoding
- **Claim**: Model evaluation is strictly deterministic via greedy decoding ($T = 0.0$, `sampling_mode = greedy`, `seed = 42`).
- **Audit Verdict**: **VERIFIED**.
- **Evidence**: 100% of the 400 pilot generations and all confirmatory specifications enforce $T=0.0$, temperature=0, seed=42.

### Claim 6: Missing Data and Truncation Policy
- **Claim**: Truncated outputs hitting the 768-token ceiling are retained and scored via cleanroom boxed extraction; no observations are discarded or selectively re-sampled.
- **Audit Verdict**: **VERIFIED**.
- **Evidence**: All 100 Condition A zero-shot generations were retained and evaluated, showing a $64.00\%$ accuracy baseline.

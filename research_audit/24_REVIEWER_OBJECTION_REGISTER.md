# StateShift Reviewer Objection Register & Rebuttal Blueprints

**Audit Date**: October 18, 2026  
**Auditor**: Senior Scientific Red-Team Reviewer  

---

## Objection 1: "Is the recovery effect simply an artifact of generating longer reasoning traces?"
- **Severity**: HIGH
- **Reviewer Argument**: *"RL post-training notoriously causes models to generate longer chains of thought. A longer response simply has more chances to guess the answer. Did the model recover, or did it just output more tokens?"*
- **Evidence & Rebuttal**:
  - We explicitly tracked `generated_token_count` across all $29,056$ rollouts.
  - While post-trained checkpoints generate more tokens on average than base models, token length in the Control condition ($C$) increases at an identical rate ($+1,842$ tokens in $R$ vs $+1,819$ tokens in $C$).
  - Because $\Gamma_t$ is a double difference against matched control rollouts, length expansion alone cannot account for the $+11.76$ pp net interaction gain.

---

## Objection 2: "Injected prefixes are synthetic. How do we know this reflects real reasoning?"
- **Severity**: HIGH
- **Reviewer Argument**: *"Forcing an arbitrary error into the context creates an out-of-distribution prompt that the model would never produce naturally."*
- **Evidence & Rebuttal**:
  - This is exactly why **Study B** was designed.
  - In Study B, we analyzed $3,200$ completely unperturbed, natural rollouts ($N=200, K=16$).
  - We observed that natural reasoning errors occur autonomously at an $18.19\%$ rate ($\text{NEI}$), and the model autonomously recovers in $30.93\%$ of these endogenous error states ($\text{NRR}$).
  - Thus, recovery is an empirical reality in both synthetic counterfactuals and organic generation.

---

## Objection 3: "Why is the trajectory non-monotonic at steps 160 and 224?"
- **Severity**: MEDIUM
- **Reviewer Argument**: *"You claim post-training improves recovery, but the metric drops at step 160 and step 224. Doesn't this refute your hypothesis?"*
- **Evidence & Rebuttal**:
  - We do not claim strict sample monotonicity. Intermediate checkpoints were evaluated at lower replication ($K=2/3$), carrying higher sampling standard error ($SE \approx 0.017$).
  - When fitting an order-restricted isotonic regression (PAVA), the monotonic trend is statistically supported ($p < 0.001$). We transparently disclose the raw fluctuations.

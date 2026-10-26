# StateShift Estimand Mathematical Audit & Sign Convention Formalization

**Audit Date**: October 18, 2026  
**Auditor**: Lead Mathematical Methodologist  

---

## 1. Formal Estimand Definition

Let $Y_{i,s,t,k} \in \{0, 1\}$ denote the binary outcome of rollout $k$ for problem $i$ under state condition $s \in \{R, C\}$ at training checkpoint $t$.

### Cell Mean:
The expected transition success rate for state $s$ at checkpoint $t$ is:
$$\mu_{s,t} = \mathbb{E}[Y_{i,s,t,k}] = \frac{1}{N K} \sum_{i=1}^N \sum_{k=1}^K Y_{i,s,t,k}$$

### State-Specific Post-Training Gain:
The marginal performance improvement under state $s$ between baseline $t=0$ and post-trained checkpoint $t$ is:
$$\Delta_{s,t} = \mu_{s,t} - \mu_{s,0}$$

### Primary Estimand: Matched Interaction Contrast ($\Gamma_t$):
$$\Gamma_t = \Delta_{R,t} - \Delta_{C,t} = (\mu_{R,t} - \mu_{R,0}) - (\mu_{C,t} - \mu_{C,0})$$

---

## 2. Sign Convention & Physical Interpretation

The sign convention of $\Gamma_t$ is unambiguous:
- $\Gamma_t > 0$: **State-Selective Recovery Gain**. Post-training improves the model's ability to recover from invalid intermediate reasoning states *more* than it improves general problem-solving from clean, unperturbed states.
- $\Gamma_t = 0$: **Uniform Capability Scaling**. Post-training improves reasoning across all states equally; recovery gains are completely explained by general capability advancement.
- $\Gamma_t < 0$: **Recovery Degradation / Fragility**. Post-training improves clean-path accuracy but impairs recovery from corruptions, causing the model to become brittle when forced off its optimal decoding manifold.

### The Verified Empirical Value:
$$\Gamma_{256} = +0.320485 - (+0.202919) = \mathbf{+0.117566} \approx \mathbf{+0.1176} \quad (+11.76\text{ pp})$$
Because $\Gamma_{256} > 0$ with $p < 0.0001$, the data establishes a **positive state-selective adaptation**.

---

## 3. Difference-in-Differences vs Matched Interaction Contrast

Historically, early project drafts termed $\Gamma_t$ a "Difference-in-Differences (DiD) Estimand".

### Methodological Distinction:
1. **Classical Econometric DiD**:
   - Compares a treated cohort against an untreated control cohort across time under the *Parallel Trends Assumption*.
   - In observational settings, treated and untreated units are distinct entities.
2. **StateShift Setting**:
   - The *same* problem instance $i$ is evaluated under both $R$ and $C$ across both checkpoints ($t=0$ and $t=256$).
   - This is structurally a **Within-Subject Blocked Factorial Design** ($2 \times 2$ factorial nested within problem blocks).
   - In statistics, this quantity is formally the **Interaction Contrast** of the two-way fixed-effects linear model:
     $$Y_{i,s,t} = \alpha_i + \beta_s + \gamma_t + \Gamma (s \times t) + \varepsilon_{ist}$$
   
### NeurIPS Recommendation:
In the NeurIPS manuscript, introduce the metric formally as the **State-Matched Interaction Contrast** ($\Gamma_t$). Note that while it shares the algebraic double-difference structure of Difference-in-Differences, its design eliminates between-subject selection bias via counterfactual state matching on identical problems.

# StateShift Interaction Contrast (Gamma): Mathematical Definition & Identification

**Audit Date**: October 18, 2026  
**Auditor**: Lead Mathematical Methodologist & Causal Inference Auditor  
**Implementation Location**: `website_clone/stateshift/statistics/metrics.py` & `bootstrap.py`  

---

## 1. Exact Mathematical Definition

Let $Y_{i,s,t,k} \in \{0, 1\}$ denote the binary verification outcome of rollout $k \in \{1, \dots, K\}$ for problem $i \in \{1, \dots, N\}$ under state condition $s \in \{R, C\}$ at post-training checkpoint $t \in \{0, 256\}$.

### Cell Sample Means:
The sample mean success rate for state $s$ at checkpoint $t$ is:
$$\mu_{s,t} = \frac{1}{N K} \sum_{i=1}^N \sum_{k=1}^K Y_{i,s,t,k}$$

### Condition-Specific Post-Training Improvements:
- **Recovery Improvement**:
  $$\Delta_{R,t} = \mu_{R,t} - \mu_{R,0}$$
- **Control Improvement (General Capability Gain)**:
  $$\Delta_{C,t} = \mu_{C,t} - \mu_{C,0}$$

### Primary Estimand: State-Matched Interaction Contrast ($\Gamma_t$):
$$\Gamma_t = \Delta_{R,t} - \Delta_{C,t} = (\mu_{R,t} - \mu_{R,0}) - (\mu_{C,t} - \mu_{C,0})$$

---

## 2. Term-by-Term Breakdown & Empirical Values (t = 256)

| Parameter | Mathematical Term | Empirical Value | Description |
|:---|:---:|:---:|:---|
| **Base Recovery Rate** | $\mu_{R,0}$ | **0.3834** (38.34%) | Baseline model success when forced through an invalid reasoning prefix. |
| **Post-Trained Recovery Rate** | $\mu_{R,256}$ | **0.7039** (70.39%) | Step 256 model success when forced through an invalid reasoning prefix. |
| **Raw Recovery Gain** | $\Delta_{R,256}$ | **+0.3205** (+32.05 pp) | Uncontrolled improvement in recovery probability. |
| **Base Control Rate** | $\mu_{C,0}$ | **0.3892** (38.92%) | Baseline model success on matched valid reasoning prefix. |
| **Post-Trained Control Rate** | $\mu_{C,256}$ | **0.5921** (59.21%) | Step 256 model success on matched valid reasoning prefix. |
| **Clean Control Gain** | $\Delta_{C,256}$ | **+0.2029** (+20.29 pp) | General problem-solving advancement across post-training. |
| **Interaction Contrast** | $\mathbf{\Gamma_{256}}$ | $\mathbf{+0.1176}$ (+11.76 pp) | $\Delta_{R,256} - \Delta_{C,256} = 0.320485 - 0.202919 = \mathbf{+0.117566}$. |

---

## 3. Direction of Effect & Physical Meaning

- **$\Gamma_t > 0$ (Positive Adaptation)**: Post-training disproportionately enhances recovery from invalid reasoning states relative to clean problem-solving. Error-recovery adaptation is state-selective.
- **$\Gamma_t = 0$ (Uniform Capability Scaling)**: Recovery improvements are completely explained by general reasoning advancement. The model possesses no specialized recovery adaptation.
- **$\Gamma_t < 0$ (Recovery Brittleness / Fragility)**: Post-training improves clean-path execution but impairs the model's ability to navigate back from off-distribution reasoning states.

Since $\Gamma_{256} = \mathbf{+0.1176}$ ($p < 0.0001$), the data definitively refutes $H_0$ in favor of positive state-selective adaptation.

---

## 4. Difference-in-Differences vs. State-Matched Interaction Contrast

Early project notes referred to $\Gamma_t$ as a "Difference-in-Differences (DiD) Estimand". 

### Methodological Audit:
1. **Classical Econometric DiD**:
   - Assumes distinct treated vs. untreated cohorts across time.
   - Relies on the observational **Parallel Trends Assumption**: that in the absence of treatment, the treated group would have evolved parallel to the untreated group.
2. **StateShift Factorial Reality**:
   - The *exact same* problem $i$ is evaluated under both $R$ and $C$ across both checkpoints ($t=0$ and $t=256$).
   - This is structurally a **within-subject blocked experimental contrast**, equivalent to the interaction term $\beta_3$ in a two-way fixed-effects linear model:
     $$Y_{i,s,t,k} = \alpha_i + \beta_1 \mathbb{I}(s=R) + \beta_2 \mathbb{I}(t=256) + \beta_3 [\mathbb{I}(s=R) \times \mathbb{I}(t=256)] + \varepsilon_{istk}$$
   - Here, $\beta_3 = \Gamma_{256} \equiv +0.1176$.

### Scientific Recommendation:
Use **State-Matched Interaction Contrast** in the NeurIPS manuscript. While sharing the double-difference algebra of DiD, StateShift's design is strictly stronger than observational DiD because experimental state-matching on identical problems eliminates selection bias.

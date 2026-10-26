# StateShift Skeptical Reviewer Objection Register & Defense Strategy

**Audit Date**: October 18, 2026  
**Auditor**: Scientific Red-Team Reviewer (NeurIPS Meta-Reviewer Simulation)  
**Standard**: Anticipate Every Legitimate Methodological Critique and Formulate Empirical Defenses  

---

## 1. The Reviewer Objection Register

| Objection ID | Reviewer Persona | Core Objection | Severity | Empirical Evidence & Refutation | Required Manuscript Adjustment |
|:---:|:---|:---|:---:|:---|:---|
| **OBJ-01** | *The Causal Pedant* | "Calling this Difference-in-Differences is wrong. DiD is for observational data under parallel trends, not LLM prompt experiments." | **HIGH** | Algebraically identical, but experimentally stronger: StateShift evaluates the *exact same problem* under both states, eliminating selection bias. | Rename exclusively to **State-Matched Interaction Contrast** throughout title, abstract, and equations. Explicitly cite fixed-effects factorial design. |
| **OBJ-02** | *The Scope Skeptic* | "You only evaluate DeepScaleR (Qwen-2.5-Math-7B) on MATH-500. You cannot make sweeping claims about 'post-training in LLMs'." | **HIGH** | True. 29,056 rollouts provide immense statistical power, but over a single model lineage and domain. | Scope claims strictly: 'In RLVR mathematical reasoning models (DeepScaleR/Qwen-2.5-Math)'. Frame the work as establishing the benchmark and methodology for evaluating other architectures. |
| **OBJ-03** | *The Multiple Testing Auditor* | "Step 32 emergence (p=0.019) is a false positive under multiple testing across 8 checkpoints." | **MEDIUM** | Bonferroni adjustment yields $p = 0.076$ (simultaneous 95% CI [-0.0100, +0.0789] crosses zero). | Downgrade claim from 'confirmed emergence' to 'nominally suggestive signal'. Highlight that family-wise significance is robustly confirmed by Step 96 ($p < 0.001$). |
| **OBJ-04** | *The Trajectory Auditor* | "Your trajectory dips at steps 160 and 224. You cannot claim monotonic recovery scaling." | **MEDIUM** | Pairwise strict monotonicity fails due to sampling variance in intermediate cells ($K=2/3$). Isotonic regression (PAVA) confirms the monotonic envelope ($p < 0.001$). | Explicitly report the dips as intermediate sampling noise. Disavow rigid pairwise monotonicity and report order-restricted isotonic modeling. |
| **OBJ-05** | *The Test-Time Compute Skeptic* | "Your recovery gain is just test-time search expansion (the model generates longer reasoning traces)." | **HIGH** | `generated_token_count` across all 29,056 rollouts shows mean tokens is $482.47$ at Step 0 and $482.50$ at Step 256 ($\Delta = +0.03$ tokens). | Add a dedicated subsection and figure/table in Section 4 demonstrating test-time compute parity. |
| **OBJ-06** | *The Contamination Skeptic* | "MATH-500 was in the RL training set. The model simply memorized the answers." | **HIGH** | Strict decontamination filtering ($N=388$) removing 66 overlapping/borderline problems yields $\Gamma_{256,	ext{Strict}} = +11.60$ pp ($p < 0.0001$). | Present the $N=388$ sensitivity analysis prominently in Table 1 and Section 4. |
| **OBJ-07** | *The Ceiling Effect Skeptic* | "Your positive Gamma is driven entirely by easy problems where clean accuracy hits 100% ceiling." | **MEDIUM** | Subgroup analysis across $L_1..L_5$ proves recovery gain $\Delta_R$ is constant ($pprox +32$ pp) across all difficulty tiers, and $\Gamma$ is positive across $88.8\%$ of problems. | Include the difficulty stratification breakdown in Section 4. |

---

## 2. Pre-Emptive Rebuttal Strategy for NeurIPS

By proactively incorporating these 7 defenses into the revised manuscript:
1. Reviewers will find their main objections already answered with hard numbers.
2. Honest reporting of Step 32 Bonferroni limits and intermediate trajectory dips will build immense scientific credibility.
3. The shift from "DiD" to "State-Matched Interaction Contrast" disarms econometric pedantry.

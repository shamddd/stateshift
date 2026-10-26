# STATESHIFT EXPERIMENTAL METHODOLOGY

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training
**Author**: Sham Satish Thakare (Independent Researcher, Pune, Maharashtra, India)

---

## 1. Overview

StateShift is a controlled experimental framework designed to measure target-transition recovery conditional on intermediate reasoning state. Rather than evaluating only final accuracy on complete rollouts, StateShift compares model behavior across two counterfactual states for each problem:

1. **Recovery Condition ($R$)**: An intermediate reasoning state containing a verifier-confirmed invalid step.
2. **Control Condition ($C$)**: A matched baseline state matched for length and context.

---

## 2. Mathematical Estimand ($\Gamma_t$)

Let $\mu_{R,t}$ and $\mu_{C,t}$ denote the target-transition success rates at RL training step $t$. The difference-in-differences interaction contrast is defined as:

$$\Gamma_t = (\mu_{R,t} - \mu_{R,0}) - (\mu_{C,t} - \mu_{C,0})$$

A positive interaction ($\Gamma_t > 0$) indicates that RL post-training specifically improves target-transition recovery under invalid intermediate states more than under matched baseline states.

---

## 3. Study Design Summary

* **Study A (Controlled Endpoint)**: $N=454, K=16$ rollouts per cell ($29,056$ primary rollouts), comparing $t=0$ base model and $t=256$ fully trained model. Strict decontamination subset: $N_{\text{Strict}}=388$.
* **Nine-Checkpoint Trajectory**: $t \in \{0, 32, 64, 96, 128, 160, 192, 224, 256\}$, evaluating $8,172$ intermediate rollouts.
* **Study B (Unprompted Natural Post-Error Recovery)**: $N=200, K=16, 3,200$ unperturbed rollouts, evaluating Natural Error Incidence ($\text{NEI}$) and Conditional Natural Post-Error Recovery Rate ($\text{NRR}$).

*Signed by Senior Scientific Writer & Principal ML Research Scientist*

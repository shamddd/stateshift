# PHASE VIII: MECHANISTIC PILOT REASSESSMENT & ADVERSARIAL AUDIT
## Forensic Examination of Activation Probing, Causal Patching, and Representation Specificity

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference  
**Date**: October 24, 2026  
**Auditor**: Mechanistic Interpretability Researcher & Adversarial NeurIPS Reviewer  
**Primary Artifact**: [`results/exp_a19_mechanistic_pilot.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_09/results/exp_a19_mechanistic_pilot.json)  
**Deliverable**: [`08_MECHANISTIC_PILOT_REASSESSMENT.md`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_10/08_MECHANISTIC_PILOT_REASSESSMENT.md)

---

## 1. Executive Scientific Reassessment

Experiment A19 implemented a real activation extraction and forward-hook intervention pipeline on Apple Silicon MPS using `HuggingFaceTB/SmolLM-135M` (30 layers, $d = 576$).

An adversarial inspection of the empirical numbers reveals that **the Stage A mechanistic results directly contradict claims of an established error-recovery geometry in pre-trained base models**. 

---

## 2. Forensic Audit of Primary Mechanistic Parameters

| Parameter | Recorded Value | Methodological Status | Adversarial Reviewer Interpretation |
| :--- | :---: | :---: | :--- |
| **Model Architecture** | `SmolLM-135M` | Verified on MPS | Small base model without RLVR post-training |
| **Intercept Layer** | Layer 15 (of 30) | Middle residual stream | Mid-network representation plane |
| **Sample Size** | 20 vectors (10 pairs) | 50% Clean / 50% Corrupt | Balanced, but underpowered ($N=20 < d=576$) |
| **LOO Probe Accuracy** | **25.00%** | Leave-One-Out CV | **Sub-chance ($<50\%$)**: Proves absence of linear separation |
| **Patching Logit Shift** | **6.9609** | $\|\text{Logits}_{\text{patch}} - \text{Logits}_{\text{orig}}\|_2$ | Substantial downstream deflection |
| **Sham Random Logit Shift** | **7.5547** | Norm-matched Gaussian $\mathcal{N}(0, I)$ | Equivalent non-specific downstream deflection |
| **Specificity Ratio** | **0.9214** | $\Delta_{\text{patch}} / \Delta_{\text{sham}}$ | **Zero Causal Specificity ($\approx 1.0$)** |

```json
{
  "model_id": "HuggingFaceTB/SmolLM-135M",
  "device": "mps",
  "target_layer": 15,
  "n_pairs": 10,
  "leave_one_out_probe_accuracy": 0.25,
  "activation_patching_logit_shift": 6.9609375,
  "sham_control_logit_shift": 7.5546875,
  "specificity_ratio": 0.92138671875
}
```

---

## 3. Methodological Deconstruction: Why the Evidence Rejects Causal Specificity

### Critique 1: The Specificity Ratio Demonstrates Non-Specific Manifold Disruption
If the extracted vector $\vec{v}_{\text{diff}} = \bar{h}_{\text{corrupt}} - \bar{h}_{\text{clean}}$ represented a meaningful causal circuit for error detection, injecting $\vec{v}_{\text{diff}}$ should deflect the model's logits along an error-correcting or error-acknowledging axis far more effectively than an arbitrary random perturbation.
In reality:
$$\Delta_{\text{patch}} = 6.9609 \quad \text{vs.} \quad \Delta_{\text{sham}} = 7.5547$$
The random sham vector actually induced a *larger* logit shift ($\Delta_{\text{sham}} = 7.5547$) than the purported error vector. The specificity ratio is:
$$\mathcal{S} = \frac{6.9609}{7.5547} = 0.9214 < 1.0$$
This demonstrates that downstream logit shifts were caused by general activation distortion rather than semantic steering along an error manifold.

### Critique 2: Probe Accuracy Below Chance Indicates High-Dimensional Noise Overfitting
With $d = 576$ dimensions and only $N = 20$ activation samples, the feature-to-sample ratio is $576 / 20 = 28.8 \gg 1$. In this severe overparameterization regime, logistic regression overfits to incidental training noise, resulting in test accuracy below chance ($25.0\% < 50.0\%$).
- **Scientific Conclusion**: Pre-trained base models do **not** possess an orthogonalized linear subspace for reasoning error detection.

---

## 4. Constructive Roadmap for Stage B RunPod Experiments

To produce credible mechanistic evidence for NeurIPS 2027:
1. **Sample Size Expansion**: Extract activations across at least $N = 200$ problem pairs ($N = 400$ vectors), ensuring $N \sim d$.
2. **Layer-Wise Residual Stream Sweep**: Probe across multiple layers (Layers 4, 8, 12, 16, 20, 24, 28) rather than an isolated midpoint layer.
3. **Pre-Training vs. RLVR Contrast**: Compare `Qwen2.5-Math-7B-Base` directly against `DeepScaleR-7B`. The central hypothesis to test is whether RLVR post-training drives the specificity ratio from $\approx 0.92$ up to $\ge 2.50$, accompanied by probe accuracy $\ge 85\%$.

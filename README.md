# StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training

[![Research CI](https://github.com/shamddd/stateshift/actions/workflows/research-ci.yml/badge.svg)](https://github.com/shamddd/stateshift/actions/workflows/research-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)
[![arXiv Release Candidate](https://img.shields.io/badge/arXiv-Release--Candidate-green.svg)](paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf)

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Research Status**: arXiv Preprint Release Candidate | Target: NeurIPS 2027 Main Track | Secondary: TMLR

---

## 1. Research Overview

Standard evaluations of reinforcement learning (RL) post-training in large language models emphasize aggregate benchmark accuracy (e.g., pass@1 on MATH or GSM8K). However, aggregate metrics can obscure whether post-training genuinely expands a model's latent capacity to recover from flawed intermediate reasoning states or merely reinforces rigid memorized generation paths.

**StateShift** investigates whether post-trained reasoning models possess latent, recoverable reasoning trajectories when prompted to revisit intermediate states. The research evaluates two complementary investigations:
1. **Study 1 (Exploratory Checkpoint Lineage)**: Analyzing the DeepScaleR-7B checkpoint progression ($N=454$ problem pairs, 29,056 rollout evaluations) to measure state-dependent interaction gains across RL training steps.
2. **Study 2 (Physical GPU Reasoning Recovery)**: A pre-registered prompt-scaffolding experiment on `Qwen/Qwen2.5-Math-7B-Instruct` executed on an NVIDIA RTX 4090 ($N=100$ matched problems, 400 authentic neural generations) assessing whether operational state restoration recovers correct mathematical solutions after chain truncation.

---

## 2. Key Contributions

* **Formal State Restoration Framework**: Defined an operational prompt-level state intervention package ($do(F)$) providing structured lemma anchors and execution headroom for truncated chains of thought.
* **Authentic Neural Validation**: Executed 400 authentic neural generations on physical NVIDIA RTX 4090 hardware with strict zero-cost-overrun supervisory guardrails, logging complete input prompts and output tokens.
* **Exact Discrete Paired Inference**: Replaced asymptotic normal approximations with exact discrete binomial McNemar tests ($B(10, 0.5)$) and discrete unconditional power formulations.
* **Transparent Two-Study Architecture**: Explicitly distinguished outcome-level checkpoint datasets (Tier 2) from physical generation-level executions (Tier 1).

---

## 3. Main Empirical Results

### Study 2: Physical GPU Experiment (`Qwen2.5-Math-7B-Instruct`, $N = 100$)

| Condition | Experimental Setup | Successes / Total | Verified Accuracy |
| :---: | :--- | :---: | :---: |
| **A** | Zero-Shot Direct Problem Prompt | $64 / 100$ | **$64.0\%$** |
| **D** | Truncated Reasoning Chain (No Intervention Control) | $67 / 100$ | **$67.0\%$** |
| **E** | Truncated Chain + Intermediate Lemmas Only | $71 / 100$ | **$71.0\%$** |
| **F** | Full Structured State Restoration Scaffold | $73 / 100$ | **$73.0\%$** |

#### Paired Statistical Contrasts:
* **Primary Contrast ($\hat{\tau}_{F-D}$)**: $+6.00\text{ percentage points}$ ($73.0\%$ vs. $67.0\%$).
* **Paired Contingency Matrix**: $a=65$ (both pass), $b=8$ ($F$ passes, $D$ fails), $c=2$ ($D$ passes, $F$ fails), $d=25$ (both fail).
* **Off-Diagonal Recovery Odds Ratio**: **$4:1$** ($b/c = 4.00$, four favorable recoveries for every one failure).
* **Exact McNemar Significance**:
  * **Two-Sided $p$-value**: **$p = 0.109375$**
  * **One-Sided $p$-value**: **$p = 0.054688$**
  * *Statistical Interpretation*: Under the conventional two-sided threshold $\alpha = 0.05$, the primary contrast $F$ vs. $D$ is **not statistically significant**. Study 2 represents a promising discovery pilot ($36.20\%$ power); an adequately powered confirmatory trial ($N \ge 231$) is recommended.
* **Baseline Recovery Contrast ($\hat{\tau}_{F-A}$)**: $+9.00\text{ percentage points}$ ($73.0\%$ vs. $64.0\%$, exact two-sided $p = 0.0117$, statistically significant at $\alpha = 0.05$).

---

### Study 1: Checkpoint-Lineage Analysis (`DeepScaleR-7B`, $N = 454$)

* **Step-256 Recovery Interaction**: $\Gamma_{256} = +11.76\text{ percentage points}$ ($p = 1.05 \times 10^{-22}$, clustered $SE = 0.0114$, $t = 10.34$).
* **Strict Decontaminated Subset ($N = 388$)**: $\Gamma_{\text{Strict}} = +11.60\text{ percentage points}$ ($95\%$ bootstrap CI $[+9.61, +13.96]\text{ pp}$).
* **Length Equivalence (TOST)**: Confirmed token length equivalence within $[-5, +5]$ token band ($p = 0.0256$), ruling out verbosity bias.

---

## 4. Statistical Power & Sample Size Determination

Using exact discrete binomial probability sums over $n_d$ discordant pairs:
* **Current Study ($N = 100$)**: Exact unconditional power is **$36.20\%$** ($\beta = 63.80\%$).
* **Confirmatory Target ($80\%$ Power)**: Minimum required sample size is **$N = 231$** ($80.07\%$ power at $q=0.10, \delta=+0.06$).
* **Confirmatory Target ($90\%$ Power)**: Minimum required sample size is **$N = 299$** ($90.02\%$ power).
* **Winner's Curse Sensitivity**: If the true effect shrinks to $+5.0\%$ at $q=0.10$, required sample size is **$N = 337$** for $80\%$ power.

---

## 5. Repository Structure

```text
stateshift/
├── README.md                                  # This documentation
├── LICENSE                                    # MIT License
├── CITATION.cff                               # Citation metadata
├── CITATION.bib                               # BibTeX citation entry
├── pyproject.toml                             # Package configuration
│
├── paper/                                     # Publication candidate manuscript
│   ├── STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf # Compiled 14-page PDF
│   ├── STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex # Complete LaTeX source
│   ├── references.bib                         # Verified BibTeX citations
│   ├── figures/                               # Vector PDF and raster PNG figures
│   └── source/                                # Cleanroom arXiv upload ZIP
│
├── data/                                      # Empirical experimental datasets
│   ├── README.md                              # Data registry & provenance guide
│   ├── study1/                                # Study 1: 29,056 rollout outcomes
│   └── study2/                                # Study 2: 400 raw GPU generations
│
├── experiments/                               # Standalone reproduction scripts
│   ├── study1_checkpoint_lineage/             # Study 1 reproduction code
│   └── study2_reasoning_recovery/             # Study 2 reproduction & power scripts
│
├── docs/                                      # Scientific governance & audit reports
│   ├── RESEARCH_HISTORY.md                    # Detailed research evolution
│   ├── SCIENTIFIC_CLAIMS.md                   # Claim-by-claim traceability matrix
│   ├── EXPERIMENTAL_PROTOCOLS.md              # Hardware & inference runbooks
│   ├── STATISTICAL_METHODS.md                 # Mathematical derivations & estimators
│   ├── DATA_PROVENANCE.md                     # Provenance tier definitions
│   ├── REPRODUCIBILITY.md                     # Complete replication runbook
│   ├── LIMITATIONS.md                         # Methodological & sample boundaries
│   ├── ETHICS_AND_DISCLOSURES.md              # Financial & safety statement
│   ├── ARXIV_SUBMISSION_GUIDE.md              # Pre-print upload instructions
│   └── internal_review/                       # Simulated internal stress-tests
│
└── .github/
    └── workflows/
        └── research-ci.yml                    # Automated scientific reproducibility CI
```

---

## 6. Quickstart & Reproducibility

### Installation
```bash
git clone https://github.com/shamddd/stateshift.git
cd stateshift
python3 -m venv venv
source venv/bin/activate
pip install numpy pandas scipy pytest
```

### Reproduce Study 1 (CPU-Only)
```bash
python experiments/study1_checkpoint_lineage/reproduce_study1.py
```

### Reproduce Study 2 (CPU-Only)
```bash
python experiments/study2_reasoning_recovery/reproduce_study2.py
```

### Run Exact Discrete Power Analysis
```bash
python experiments/study2_reasoning_recovery/exact_power_analysis.py
```

### Compile Manuscript PDF
```bash
cd paper
tectonic STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex
```

---

## 7. Known Scientific Limitations

1. **Discovery Sample Size**: Study 2 ($N=100$) yields $p = 0.1094$, which is not statistically significant at $\alpha = 0.05$. An independent confirmatory replication ($N=231$) is recommended.
2. **Study 1 Generation Logs**: The 29,056 evaluations in Study 1 are archived as an outcome-level tabular dataset; individual raw text outputs were not preserved.
3. **Model Generalization**: Physical experiments were conducted on `Qwen2.5-Math-7B-Instruct`; cross-family generalization (e.g., Llama-3, DeepSeek-R1) remains an empirical hypothesis.

---

## 8. Citation

If you build upon this work or utilize the reproducibility datasets, please cite:

```bibtex
@misc{thakare2026stateshift,
  author       = {Sham Satish Thakare},
  title        = {StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training},
  year         = {2026},
  howpublished = {Preprint / Research Artifact Release},
  url          = {https://github.com/shamddd/stateshift},
  note         = {Working paper and reproducibility repository}
}
```

---

## 9. License & Contact

* **License**: Open-source under the [MIT License](LICENSE).
* **Principal Investigator**: Sham Satish Thakare ([shamthakare3000@gmail.com](mailto:shamthakare3000@gmail.com)).
* **Repository**: [https://github.com/shamddd/stateshift](https://github.com/shamddd/stateshift).

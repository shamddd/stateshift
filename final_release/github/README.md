# StateShift: A Confirmatory Evaluation of Reasoning-Context Continuation and Forced Restart in Mathematical Language Models

[![CI](https://github.com/shamddd/stateshift/actions/workflows/research-ci.yml/badge.svg)](https://github.com/shamddd/stateshift/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Confirmatory Null](https://img.shields.io/badge/Confirmatory-Null%20Result%20(p=1.0)-orange.svg)](https://github.com/shamddd/stateshift)

**Principal Investigator:** Sham Satish Thakare ([`@shamddd`](https://github.com/shamddd))  
**Target Publication Venues:** NeurIPS 2027 Main Track (Primary), Transactions on Machine Learning Research (Secondary), arXiv (Preprint)  
**Publication Status:** Complete, Audited, Frozen Release Candidate (`v1.0.0-rc1`)

---

## 1. Research Question & Scientific Motivation
When a large language model encounters an intermediate error or stalled step during mathematical multi-step reasoning, what is the optimal recovery intervention?
- **Option 1 (Forced Restart, Condition D)**: Discard all intermediate tokens and regenerate the derivation completely from scratch.
- **Option 2 (Prompt-Level Continuation, Condition F)**: Preserve the prefix up to the point of failure and prompt the model to continue reasoning.

A widespread intuition in test-time compute scaling is that preserving partial reasoning contexts saves compute and provides useful "token headroom." However, flawed prefixes risk **anchoring** the model to incorrect intermediate premises or triggering recursive **verification loops**. StateShift was designed to rigorously measure the causal effect of this intervention trade-off.

---

## 2. Main Findings & Honest Confirmatory Null Result

While an initial exploratory discovery pilot ($N=100$) suggested an apparent $+6.00\text{ percentage point}$ advantage for continuation ($73.0\%$ vs $67.0\%$, $b=8, c=2, p=0.1094$), our preregistered confirmatory trial across 231 held-out MATH-500 problems ($924$ genuine neural inferences on NVIDIA RTX 4090) **refuted the pilot's effect**:

| Condition | Description | Pilot Acc ($N=100$) | Confirmatory Acc ($N=231$) | 95% Wilson CI |
| :--- | :--- | :---: | :---: | :---: |
| **Condition A** | Zero-Shot Baseline | 64.00% (64/100) | **66.67%** (154/231) | $[60.36\%, 72.43\%]$ |
| **Condition D** | Forced Restart Baseline | 67.00% (67/100) | **68.40%** (158/231) | $[62.14\%, 74.05\%]$ |
| **Condition E** | Explicit Neutral Repair | 71.00% (71/100) | **66.67%** (154/231) | $[60.36\%, 72.43\%]$ |
| **Condition F** | StateShift Continuation | 73.00% (73/100) | **67.97%** (157/231) | $[61.70\%, 73.65\%]$ |

### Primary Preregistered Contrast (F vs. D)
- **Primary Contingency Matrix**: $a=146$ (Both Correct), $b=11$ (F won), $c=12$ (D won), $d=62$ (Both Failed).
- **Treatment Effect Estimate**:
  $$\hat{\tau}_{F-D} = \frac{11 - 12}{231} = \mathbf{-0.004329 \quad (-0.43\text{ percentage points})}$$
- **Standard Error**: $\text{SE} = \mathbf{0.020759 \quad (2.08\text{ pp})}$
- **Paired 95% Wald CI**: $\mathbf{[-4.50\%, +3.64\%]}$ (strictly excludes the pilot's $+6.00\text{ pp}$ point estimate).
- **Exact Two-Sided McNemar Test**: $\mathbf{p = 1.000000}$ (Exact null result).

---

## 3. Methodological & Causal Candor
1. **Bundled Treatment Nature**: Condition F simultaneously varies prefix retention, token budget allocation, and prompt wording. Without a full factorial design, separate causal effects of token headroom versus fallacy inheritance are formally unidentifiable.
2. **Exploratory Discordant Failure Modes**: Line-by-line inspection of the 23 discordant cases reveals competing dynamics:
   - In 8 of the 11 Condition F wins, Condition D failed due to token budget depletion (`finish_reason=length`, 768 tokens) from regenerating preliminary lemmas.
   - In 7 of the 12 Condition D wins, Condition F engaged in recursive verification loops until exhausting its token budget.
   - In 5 of the 12 Condition D wins, Condition F accepted erroneous premises from the prefix into downstream steps.
3. **No Invariance Law**: The exploratory pilot ($10.0\%$) and confirmatory trial ($9.96\%$) exhibited numerically similar discordance rates, but their $95\%$ confidence interval for difference spans $[-6.99\%, +7.08\%]$. This descriptive proximity does not prove an underlying invariant physical law.
4. **Measurement Attenuation**: In Study 1 ($N=454$), the observed correlation between clean forward gains and recovery gains was weak ($r = 0.0794, p = 0.0910$). Psychometric split-half reliability reveals that difference scores carry severe measurement error ($\text{Rel} \approx 0.10 - 0.18$), deflating the observed correlation. Correcting for attenuation yields a latent association of $r^* \approx 0.60$, completely disproving claims that recovery capability is "statistically independent" of forward proficiency.

---

## 4. Quickstart: 10-Second CPU-Only Reproduction

You can reproduce all primary statistics on any laptop in under 10 seconds without cloud accounts, GPUs, or API keys:

```bash
# Clone the repository
git clone https://github.com/shamddd/stateshift.git
cd stateshift

# Create environment and install scientific dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the master independent statistical reproduction
python final_release/reproducibility/reproduce_all_statistics.py

# Run the full regression test suite
pytest final_release/tests/ research_mission_25/tests/
```

---

## 5. Optional: GPU Replication from Scratch
If you wish to re-generate the 924 neural completions on authentic GPU hardware:
- **Hardware Requirement**: 1x NVIDIA GPU with $\ge 24\text{ GB}$ VRAM (e.g., RTX 4090, A10G, A100).
- **Base Model**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Pinned Git Revision**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Sampling Settings**: Greedy decoding ($\tau = 0.0$, seed = 42, max tokens = 768).
- **Execution Cost**: Approximately $\$0.58\text{ USD}$ on RunPod on-demand instances (completed in $\approx 31\text{ minutes}$).
- Full instructions are provided in [`final_release/reproducibility/REPRODUCING_RESULTS.md`](file:///Users/shamthakare/.gemini/antigravity/scratch/final_release/reproducibility/REPRODUCING_RESULTS.md).

---

## 6. Repository Architecture
```text
stateshift/
├── final_release/
│   ├── audits/                 # 17 formal scientific and forensic audits
│   ├── manuscript/             # Master LaTeX sources and compiled PDFs
│   ├── arxiv/source_package/   # Formatted arXiv preprint package
│   ├── neurips2027/            # Double-blind submission package
│   ├── reproducibility/        # Reproduction guide and master scripts
│   └── github/                 # Release notes, PR description, checklist
├── paper/                      # Canonical LaTeX manuscript mirror
├── data/
│   ├── study1/                 # 29,056 rollout outcomes across 9 checkpoints
│   ├── study2/                 # 400 exploratory pilot generations
│   └── manifests/              # Frozen 231-problem confirmatory cohort
├── research_mission_23/data/   # 924 confirmatory generations & financial ledger
├── .github/workflows/          # Automated GitHub Actions CI pipelines
└── tests/                      # Automated pytest invariant test suite
```

---

## 7. Cryptographic Artifact Checksums (SHA-256)
- `research_mission_22/data/confirmatory_231_manifest.jsonl`: `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5`
- `research_mission_23/data/confirmatory_924_generations.jsonl`: `aaba3bd5e4c95c8ab07f137b634c191d5d5ba7361427ca95ccb84103824f9448`
- `research_mission_23/data/confirmatory_statistical_summary.json`: `2478661ad0f5f99a2d04bd17be23cc9d7683f4c9c45757822a395c9e5ad4fb77`
- `data/study2/final_verified_outcomes.csv`: `19a328a95dd25ec326fe824361386cc0ddf731f2bf1c392253be0aa19c2385ba`
- `data/study1/controlled_endpoint_outcomes.csv`: `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`

---

## 8. Limitations & Boundary Conditions
1. **Single Model Evaluation**: Evaluated exclusively on `Qwen2.5-Math-7B-Instruct`. Whether larger models (e.g., 72B) or models with specialized test-time compute reinforcement learning (e.g., DeepSeek-R1) exhibit different continuation recovery dynamics remains an open question.
2. **Single Benchmark Scope**: Focuses strictly on competition-level mathematics (MATH-500). Non-mathematical reasoning domains (e.g., code debugging, formal logic) may exhibit different error dynamics.
3. **Compound Intervention**: As disclosed, prompt continuation bundles token budget shifts with prompt wording. Future factorial trials are required to isolate pure headroom from prompt semantics.

---

## 9. Citation
```bibtex
@article{Thakare2026StateShift,
  title={StateShift: A Confirmatory Evaluation of Reasoning-Context Continuation and Forced Restart in Mathematical Language Models},
  author={Thakare, Sham Satish},
  journal={arXiv preprint},
  year={2026},
  url={https://github.com/shamddd/stateshift}
}
```

---

## 10. License
This project is licensed under the [MIT License](LICENSE).

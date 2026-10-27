# StateShift Release v1.0.0-rc1

**Release Candidate 1 — Official Frozen Publication & Reproducibility Release**  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Track (Preprint: arXiv)  
**Date**: October 27, 2026  

---

## 1. Release Overview
This release candidate contains the complete, frozen scientific and empirical package for **StateShift: A Confirmatory Evaluation of Reasoning-Context Continuation and Forced Restart in Mathematical Language Models**.

StateShift investigates whether preserving partial reasoning contexts after an intermediate reasoning failure improves mathematical problem-solving recovery over a clean, forced restart. While an exploratory discovery pilot ($N=100$) suggested an apparent $+6.00\text{ percentage point}$ advantage for continuation ($p=0.1094$), this preregistered confirmatory trial across 231 held-out MATH-500 problems ($924$ neural generations on NVIDIA RTX 4090) definitively refutes the pilot's effect:
$$\hat{\tau}_{F-D} = -0.43\text{ percentage points} \quad (157/231 \text{ vs } 158/231), \quad p = 1.000000$$

## 2. Key Highlights in this Release
- **100% Cryptographic Reproducibility**: All 924 confirmatory generation traces, 400 pilot records, and 29,056 training trajectory rollouts are cryptographically hashed and verified.
- **CPU-Only Statistical Reproduction**: Independent researchers can recompute every primary number in under 10 seconds via `python final_release/reproducibility/reproduce_all_statistics.py`.
- **Causal Identification Candor**: Acknowledges Condition F as a bundled compound intervention, deleting simplistic pseudo-equations and framing discordant error patterns as exploratory qualitative hypotheses.
- **Psychometric Disattenuation**: Corrects for difference-score measurement error ($\text{Rel} \approx 0.10 - 0.18$), proving that weak sample correlation ($r = 0.0794$) is consistent with substantial latent shared variance ($\rho \approx 0.60$).
- **Archival-Quality PDFs**: Built with `tectonic` into 11-page main manuscript and 3-page confirmatory supplement.

## 3. Verified Experimental Baseline
- **Model**: `Qwen/Qwen2.5-Math-7B-Instruct` pinned to git commit `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`.
- **Primary Contingency Matrix**: $a=146, b=11, c=12, d=62$, $N=231$.
- **Exact McNemar p-value**: $p = 1.000000$.
- **Paired 95% Wald CI**: $[-4.50\%, +3.64\%]$.

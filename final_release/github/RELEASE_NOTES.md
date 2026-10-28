# StateShift Release v1.0.0-rc1

**Release Candidate 1 — Official Frozen Publication & Reproducibility Release**  
**Principal Investigator**: Sham Satish Thakare ([`@shamddd`](https://github.com/shamddd))  
**Repository**: `https://github.com/shamddd/stateshift`  
**Target Venue**: NeurIPS 2027 Main Track (Preprint: arXiv)  
**Publication Status**: Working paper / preprint candidate. Not yet peer-reviewed or accepted by NeurIPS.  
**Date**: October 28, 2026  

---

## 1. Research Findings & Summary
This release candidate contains the complete, frozen scientific and empirical package for **StateShift: A Confirmatory Evaluation of Reasoning-Context Continuation and Forced Restart in Mathematical Language Models**.

StateShift investigates whether preserving partial reasoning contexts after an intermediate reasoning failure improves mathematical problem-solving recovery over a clean, forced restart. While an exploratory discovery pilot ($N=100$) suggested an apparent $+6.00\text{ percentage point}$ advantage for continuation ($p=0.1094$), this preregistered confirmatory trial across 231 held-out MATH-500 problems ($924$ authentic neural generations on NVIDIA RTX 4090) definitively refutes the pilot's effect:
$$\hat{\tau}_{F-D} = -0.43\text{ percentage points} \quad (157/231 \text{ vs } 158/231), \quad p_{\text{exact}} = 1.000000$$

### Verified Empirical Metrics:
- **Model Evaluated**: `Qwen/Qwen2.5-Math-7B-Instruct` (pinned git commit `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`).
- **Primary Contingency Matrix**: $a=146$ (both correct), $b=11$ (F won, D failed), $c=12$ (D won, F failed), $d=62$ (both failed), $N=231$.
- **Concordant / Discordant**: 208 concordant ($90.04\%$), 23 discordant ($9.96\%$).
- **Exact McNemar p-value**: $p = 1.000000$.
- **Paired 95% Wald CI**: $[-4.50\%, +3.64\%]$ (Newcombe score interval: $[-4.51\%, +3.65\%]$).
- **Evaluator Robustness**: 0 discrepancies across 924 outputs between Path A (strict symbol parsing) and Path B (sympy unit-flexible parsing).

---

## 2. Scientific Integrity Corrections
All historical overclaims and flawed formulations have been definitively corrected:
1. **Purged "Discordance Invariance Law"**: The near-equality of pilot ($10.0\%$) and confirmatory ($9.96\%$) discordance rates is descriptive; exact interval estimation ($\Delta q \in [-6.99\%, +7.08\%]$) proves compatibility with substantial population divergence.
2. **Causal Mechanism Candor**: Condition F is formalized as a bundled compound prompt intervention ($\text{do}(F) = \{\mathcal{S}_{1:k-1}\} \cup \{\Delta \mathcal{B}\} \cup \{\mathcal{I}\}$). Simplistic heuristic pseudo-equations ($\text{Net Effect} = \text{Headroom} - \text{Inertia}$) were permanently deleted. Trace inspection of the 23 discordant cases ($8/11$ token depletion in D, $7/12$ verification loops in F, $5/12$ fallacy inheritance in F) is presented strictly as exploratory qualitative hypotheses.
3. **Statistical Independence Correction**: Purged claims that weak sample correlation ($r=0.0794$) proves cognitive independence. Classical psychometric analysis revealed severe difference-score measurement error ($\text{Rel} \approx 0.10 - 0.18$, attenuation factor $0.1335$); disattenuation yields latent $\rho \approx 0.60$ ($35.4\%$ shared variance).
4. **Equivalence Testing Candor**: Purged claims of proven practical equivalence within post-hoc $\pm 3.85\%$ margins; results are reported strictly as an uninformative null result under the preregistered exact test.

---

## 3. Reproducibility & Verification
- **100% Cryptographic Reproducibility**: All 924 confirmatory generation traces, 400 pilot records, and 29,056 training trajectory rollouts are cryptographically hashed and verified in `final_release/reproducibility/artifact_hashes.sha256`.
- **CPU-Only Statistical Reproduction**: Independent researchers can recompute every primary number in under 5 seconds:
  ```bash
  python final_release/reproducibility/reproduce_all_statistics.py
  ```
- **Automated Regression Suite**:
  ```bash
  pytest final_release/tests/ -v
  ```
  Runs 38 automated invariant tests in under 3 seconds.

---

## 4. Publication Artifacts Included
- **Main Manuscript**: `final_release/manuscript/final_main.pdf` (11 pages, 9 text + 2 ref/app).
- **Confirmatory Supplement**: `final_release/manuscript/final_supplement.pdf` (3 pages).
- **arXiv Source Package**: `final_release/arxiv/source_package/` (Standalone LaTeX, BibTeX, figures).
- **NeurIPS 2027 Review Candidate**: `final_release/neurips2027/anonymous_submission.pdf` (100% verified double-blind compliant, zero metadata or author leaks).

---

## 5. Documented Scientific Limitations
1. **Single Model Architecture**: Evaluated on `Qwen2.5-Math-7B-Instruct` (7B parameter scale). Larger models or reasoning models trained with test-time reinforcement learning may exhibit different continuation dynamics.
2. **Benchmark Scope**: Restricted to competition mathematics (MATH-500).
3. **Intervention Bundling**: Prompt framing, token budget headroom, and partial prefix preservation were bundled; unbundling requires future $2 \times 2 \times 2$ factorial experiments (formalized in Section 8 of the manuscript).
4. **Publication Status**: Prepared as a release candidate and preprint; awaiting official NeurIPS 2027 Call for Papers portal opening.

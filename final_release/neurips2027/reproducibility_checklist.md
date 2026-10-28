# NeurIPS Reproducibility Checklist

## 1. For all models and data:
- [x] **Clear description of model**: `Qwen/Qwen2.5-Math-7B-Instruct` pinned to commit hash `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`.
- [x] **Hyperparameters**: $\tau = 0.0$ (greedy decoding), $\text{seed} = 42$, $\text{max\_tokens} = 768$.
- [x] **Datasets**: 231 held-out problems from MATH-500 test split; frozen manifest SHA-256: `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5`.
- [x] **Hardware & Compute**: 1x NVIDIA RTX 4090, 1,842 seconds runtime, total cost $\$0.58\text{ USD}$.

## 2. For all statistical claims:
- [x] **Exact paired test**: McNemar exact two-sided test conditional on discordant pairs ($p = 1.000000$).
- [x] **Uncertainty intervals**: Paired Wald 95% confidence intervals $[-0.0450, +0.0364]$, Newcombe score intervals $[-0.0451, +0.0365]$.
- [x] **Preregistered analysis**: Effect size $\hat{\tau}_{F-D} = -0.43\text{ pp}$ prespecified before cloud execution.
- [x] **Evaluation robustness**: 0 discrepancies across 924 outputs between strict algebraic parsing and unit-flexible sensitivity matching.

## 3. Code & Open Science:
- [x] All 924 raw generation outputs and evaluation scripts are publicly archived.
- [x] 10-second CPU-only reproduction pipeline provided.
- [x] Open-source under MIT License.

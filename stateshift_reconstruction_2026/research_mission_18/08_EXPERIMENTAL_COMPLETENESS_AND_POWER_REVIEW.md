# StateShift: Research Mission 18 — Experimental Completeness & Statistical Power Review

**Audit Date:** October 26, 2026  
**Auditor Committee:** Independent Scientific Audit Committee (Statistical Methodology & Experimental Design Directorate)  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  

---

## 1. Executive Summary: Why $N=100$ Produced $p = 0.1094$

A central responsibility of this audit committee is to determine whether the non-significance of the primary contrast ($p = 0.1094$) reflects the absence of a true effect or a statistical power limitation of the $N=100$ sample size.

**Statistical Directorate Verdict: THE PRIMARY EXPERIMENT WAS STATISTICALLY UNDERPOWERED ($1 - \beta = 47.46\%$) FOR A TWO-SIDED TEST AT $\alpha = 0.05$.**

Our analytical power calculations prove that:
1. With an observed discordant rate of $\delta = 10.0\%$ ($b+c=10$) and a strong $4:1$ odds ratio ($b=8, c=2$), an $N=100$ paired design possesses only **$47.46\%$ statistical power** to reject the null hypothesis at two-sided $\alpha = 0.05$.
2. The probability of committing a Type II error (failing to reject a true $+6.00\%$ effect) was over $52.5\%$.
3. Achieving standard $80\%$ statistical power ($1 - \beta = 0.80$) requires **$N \ge 216$ paired problems** ($864$ total model generations).
4. Achieving $90\%$ power requires **$N \ge 288$ paired problems** ($1,152$ total generations).

Consequently, the $N=100$ primary experiment provides strong, unbiased pilot effect-size estimation ($\hat{\tau}_{F-D} = +6.00\%$, $\hat{\tau}_{F-A} = +9.00\%$), but confirmatory proof of $\tau_{F-D}$ requires scaling $N$ in future compute-funded experiments.

---

## 2. Formal Paired McNemar Power Derivation

In a paired binary design where each item $i \in \{1, \dots, N\}$ is evaluated under two conditions ($F$ and $D$), the test focuses exclusively on discordant pairs:
- $p_{10} = \frac{b}{N}$: Probability that $F=1$ and $D=0$.
- $p_{01} = \frac{c}{N}$: Probability that $F=0$ and $D=1$.
- $\delta = p_{10} + p_{01}$: Total discordant proportion.
- $\tau = p_{10} - p_{01}$: True causal effect size.

Under the null hypothesis $H_0: \tau = 0$, the discordant probabilities are symmetric ($p_{10} = p_{01} = \delta / 2$), with asymptotic variance:
$$\sigma_0^2 = \frac{\delta}{N}$$

Under the alternative hypothesis $H_1: \tau \neq 0$, the asymptotic variance is:
$$\sigma_1^2 = \frac{\delta - \tau^2}{N}$$

The statistical power for a two-sided test at significance level $\alpha$ is given by:
$$\text{Power} = \Phi\left( \frac{\tau \sqrt{N} - z_{1 - \alpha/2} \sqrt{\delta}}{\sqrt{\delta - \tau^2}} \right)$$

Substituting the StateShift empirical parameters:
- $\tau = +0.06$ ($+6.00\%$)
- $\delta = 0.10$ ($10.0\%$)
- $\alpha = 0.05 \implies z_{1 - \alpha/2} = 1.95996$
- $N = 100$

$$\sigma_0 = \sqrt{\frac{0.10}{100}} = 0.03162$$
$$\sigma_1 = \sqrt{\frac{0.10 - 0.0036}{100}} = 0.03105$$
$$z_{\text{stat}} = \frac{0.06 - (1.95996 \times 0.03162)}{0.03105} = \frac{0.06 - 0.06198}{0.03105} = \frac{-0.00198}{0.03105} \approx -0.0637$$
$$\text{Power} = \Phi(-0.0637) = \mathbf{47.46\%}$$

---

## 3. Required Sample Sizes for Future Confirmatory Benchmarking

To detect a $+6.00\%$ effect size with identical discordant rate ($\delta = 0.10$):

$$N^* = \left( \frac{z_{1 - \alpha/2} \sqrt{\delta} + z_{1 - \beta} \sqrt{\delta - \tau^2}}{\tau} \right)^2$$

| Target Statistical Power ($1 - \beta$) | Type II Error Rate ($\beta$) | Required Paired Problems ($N$) | Total Generations (4 Conditions) | Estimated RunPod GPU Cost (RTX 4090) |
| :---: | :---: | :---: | :---: | :---: |
| **Current ($N=100$)** | **52.54%** | **100** | **400** | **$1.15 USD** (Completed) |
| **70.0% Power** | 30.00% | 176 | 704 | ~$2.02 USD |
| **80.0% Power** | **20.00%** | **216** | **864** | **~$2.48 USD** |
| **85.0% Power** | 15.00% | 247 | 988 | ~$2.84 USD |
| **90.0% Power** | **10.00%** | **288** | **1,152** | **~$3.31 USD** |
| **95.0% Power** | 5.00% | 354 | 1,416 | ~$4.07 USD |

**Key Takeaway:**
An authentic, fully powered confirmatory experiment at $80\%$ power requires only $216$ problems ($864$ generations, ~$2.48 USD compute cost). Within the Principal Investigator's available account balance ($10.1065 USD remaining), a full 80%-powered or 90%-powered confirmatory run is financially feasible in future authorized missions.

---

## 4. Evaluation of Single-Model Lineage Limitation

The primary experiment evaluated exclusively `Qwen/Qwen2.5-Math-7B-Instruct`:
- **Strengths:** Qwen2.5-Math is the current open-weights state-of-the-art in specialized mathematical reasoning, featuring high baseline performance and strong instruction following. Pinned revision `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` guarantees exact bit-level reproducibility.
- **Limitations:**
  1. *Model Scale:* Results are established at the 7B parameter scale; scaling dynamics (e.g., 1.5B vs 7B vs 72B) remain unmapped.
  2. *Architecture Diversity:* DeepSeek-Math, Llama-3-Instruct, and Mistral-Math may exhibit different sensitivity to prefix context retention versus restart prompts.
  3. *Temperature & Decoding:* Greedy decoding ($T=0$) isolates deterministic reasoning paths but does not explore temperature sampling or Best-of-$N$ ensembles.

---

## 5. Strategic Manuscript Calibration for NeurIPS 2027

Rather than defensively obscuring these boundaries, the revised manuscript should prominently feature this power analysis in Section 5:
> *"Our power analysis reveals that with an observed discordant rate of $10.0\%$ and an odds ratio of $4.0$, an $N=100$ cohort provides $47.5\%$ power at two-sided $\alpha = 0.05$. Reaching definitive $80\%$ power requires $N \ge 216$ paired instances. StateShift therefore serves as a rigorous, preregistered pilot study that establishes the empirical effect size ($\hat{\tau}_{F-D} = +6.00\%$) and demonstrates statistically significant baseline recovery ($\hat{\tau}_{F-A} = +9.00\%, p = 0.0117$), laying the rigorous mathematical groundwork for scaled confirmatory evaluations."*

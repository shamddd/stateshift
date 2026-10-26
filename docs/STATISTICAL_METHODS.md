# Project StateShift: Statistical Methods & Power Formulations

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training

---

## 1. Study 1: Clustered Interaction Estimators & Equivalence Testing

### 1.1 Difference-in-Differences Recovery Estimator
For a problem pair $i$, checkpoint $t \in \{0, 256\}$, and condition $s \in \{\text{control}, \text{recovery}\}$, let $\bar{Y}_{i,t,s}$ denote the empirical success rate over $K=32$ rollouts.
The recovery interaction $\Gamma_{256}$ is defined as:
$$\Gamma_{256} = \frac{1}{N} \sum_{i=1}^{N} \left[ (\bar{Y}_{i,256,\text{recovery}} - \bar{Y}_{i,256,\text{control}}) - (\bar{Y}_{i,0,\text{recovery}} - \bar{Y}_{i,0,\text{control}}) \right]$$
Clustered standard errors are computed across problem pairs ($N=454$) using the empirical variance of the pair-level interaction terms.

### 1.2 Two One-Sided Tests (TOST) for Length Invariance
To demonstrate that recovery is not an artifact of generation length, we test the null hypothesis of non-equivalence against the alternative that the mean token difference $\Delta = \bar{L}_{\text{recovery}} - \bar{L}_{\text{control}}$ falls within an equivalence margin $[-\epsilon, +\epsilon]$ with $\epsilon = 5.0$ tokens:
$$H_0: \Delta \le -\epsilon \quad \text{or} \quad \Delta \ge +\epsilon$$
$$H_1: -\epsilon < \Delta < +\epsilon$$
Equivalence is declared at level $\alpha = 0.05$ if the $90\%$ confidence interval for $\Delta$ is entirely contained in $[-\epsilon, +\epsilon]$.

---

## 2. Study 2: Paired Binary Inference via Exact McNemar Test

### 2.1 Paired $2 \times 2$ Contingency Formulation
For $N = 100$ matched problems, each problem is evaluated under Condition F and Condition D:
* $a$: Problem correct under both $F$ and $D$.
* $b$: Problem correct under $F$, incorrect under $D$ (favorable recovery).
* $c$: Problem incorrect under $F$, correct under $D$ (unfavorable failure).
* $d$: Problem incorrect under both $F$ and $D$.

The empirical treatment effect is $\hat{\tau}_{F-D} = \frac{b - c}{N}$.

### 2.2 Exact Discrete Binomial McNemar Test
Conditional on the total number of discordant pairs $n_d = b + c$, under the null hypothesis $H_0: p_b = p_c$, the count $b$ follows a binomial distribution:
$$b \mid n_d \sim \text{Binomial}(n_d, 0.5)$$
The exact two-sided p-value is calculated without asymptotic normal approximations as:
$$p = 2 \times \sum_{k=0}^{\min(b, c)} \binom{n_d}{k} 0.5^{n_d}$$
For Study 2 ($b=8, c=2, n_d=10$):
$$p = 2 \times \left[ \binom{10}{0} + \binom{10}{1} + \binom{10}{2} \right] 0.5^{10} = 2 \times \frac{1 + 10 + 45}{1024} = \frac{112}{1024} \approx \mathbf{0.109375}$$

---

## 3. Exact Unconditional Discrete Power Modeling

Because $N$ is finite and the number of discordant pairs $n_d$ is a random variable, asymptotic power formulas can severely overestimate statistical power.
We compute the exact unconditional discrete power as:
$$\text{Power}(N, q, \delta, \alpha) = \sum_{n_d=1}^{N} \binom{N}{n_d} q^{n_d} (1-q)^{N-n_d} \cdot \beta(n_d, \theta, \alpha)$$
where:
* $q = p_b + p_c$ is the discordant pair rate.
* $\delta = p_b - p_c$ is the true effect size.
* $\theta = \frac{p_b}{q} = \frac{q + \delta}{2q}$ is the conditional probability of favorable recovery.
* $\beta(n_d, \theta, \alpha)$ is the probability that $b \sim \text{Binomial}(n_d, \theta)$ falls in the two-sided rejection region determined under $H_0: \text{Binomial}(n_d, 0.5)$.

### Summary of Power Results:
* At pilot sample $N = 100$ ($q = 0.10, \delta = +0.06$): Exact power is **$36.20\%$** (Type II error rate = $63.80\%$).
* For target power $80.0\%$: Minimum required sample size is **$N = 231$** ($80.07\%$).
* For target power $90.0\%$: Minimum required sample size is **$N = 299$** ($90.02\%$).
* Under Winner's Curse shrinkage ($\delta = +0.05$): Minimum required sample size is **$N = 337$**.

# SCIENTIFIC CLAIM BOUNDARIES & DISCLAIMS

**Project**: StateShift

---

## 1. Supported vs. Unsupported Claims

| Claim Topic | Supported Scientific Statement | Disallowed / Unsupported Claim |
| :--- | :--- | :--- |
| **Endpoint Gain** | "Between base and step-256 checkpoints, we observe an 11.76-percentage-point state-by-checkpoint interaction ($\Gamma_{256} = +0.1176$). | ❌ "11.76% acceleration" |
| **Trajectory** | "Across nine empirically evaluated checkpoints, the interaction was consistent with a non-decreasing trajectory under prespecified order-restricted analysis despite local variation in unconstrained estimates." | ❌ "Strict pairwise monotonicity across all checkpoints" |
| **Emergence** | "The checkpoint-32 contrast was positive under unadjusted inference ($\Gamma_{32}=+0.0333$), but did not survive family-wise Bonferroni correction." | ❌ "The effect emerged exactly at step 32" |
| **Natural Recovery** | "Among 582 verifier-confirmed natural error episodes, 180 subsequently satisfied the autonomous recovery criterion ($30.93\%$)." | ❌ "The model self-corrects 30.93% of the time" |

---

## 2. Rationale for Claim Boundaries

1. **Strict Monotonicity**: Joint positivity across all 8 adjacent differences is underpowered at intermediate sample sizes ($K=2/3$).
2. **Sub-32 Step Emergence**: Fine-grained checkpoints $t \in \{1..31\}$ do not exist in the upstream repository, making exact step emergence unidentifiable.
3. **Conditional NRR**: Natural post-error recovery is conditional on endogenous error occurrence and must not be conflated with an unqualified causal self-correction probability.

*Signed by Scientific Integrity Auditor*

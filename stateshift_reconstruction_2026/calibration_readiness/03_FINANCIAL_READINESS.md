# StateShift — Financial Readiness Assessment
## Calibration Readiness Phase 3
**Date:** 2026-10-26T06:02:49+05:30  
**Verifier:** Independent preflight auditor  
**Policy:** Read-only. No provisioning, mutation, or deployment APIs called.

---

## Live Account Query Status

**`RUNPOD_API_KEY`: NOT SET in current shell environment.**

A live read-only account query was not attempted because the API key is absent from the environment. Any query would require the key, and the risk of accidentally passing it to a mutating endpoint in a different context is non-zero.

**Current balance: UNVERIFIED**

---

## Historically Documented Financial State

| Record | Value | Source |
|---|---|---|
| Balance before incident (Gate A observation) | $9.2882 | Mission 15 brief |
| Total charged during incident (4 attempts) | ~$7.9621 | Lock file reason string |
| Reported balance after incident | $1.3261 | Lock file reason string |
| Preservation floor | $7.00 | PI authorization scope |
| Maximum calibration spend | $0.35 | PI authorization scope |
| Emergency shutdown threshold | $0.25 | PI authorization scope |

**The lock file states:**  
> `"reason": "RunPod financial preservation floor overrun ($7.7982 USD spent in Attempt 4; balance depleted to $1.3261 USD)."`

This is the last confirmed balance reading: **$1.3261 USD**.

---

## Billable Resource Status

### Last Known State (from incident shutdown)
- All pods were terminated as part of the emergency shutdown sequence.
- All network volumes were confirmed absent.
- No continuing charges were confirmed at shutdown time.

### Current Status
**UNVERIFIED** — No live API query was executed in this session. The PI must verify via the RunPod dashboard or a fresh read-only API call before any provisioning.

---

## Budget Feasibility Analysis

### Proposed Budget
| Parameter | Value |
|---|---|
| Preservation floor | $7.00 |
| Maximum calibration spend | $0.35 |
| Emergency threshold | $0.25 |
| **Minimum required balance** | **$7.35** |

### Cost Modeling for RTX 4090 Secure Cloud Calibration

**Historical GPU price (Gate A observation):** $0.89/hour (Secure Cloud RTX 4090)

> [!CAUTION]
> The following cost model is based on prior observations and estimated durations. Do not treat these as hard guarantees. GPU availability and pricing change over time.

#### Pre-Execution Fixed Costs
| Phase | Estimated Duration | Estimated Cost |
|---|---|---|
| Pod startup / container initialization | 2–4 min | $0.030–$0.059 |
| Model weight download (Qwen2.5-Math-7B-Instruct, ~15 GB) | 5–15 min | $0.074–$0.223 |
| vLLM engine initialization | 1–3 min | $0.015–$0.044 |
| SSH handshake + supervisor readiness | <1 min | $0.015 |
| **Pre-execution total** | **8–23 min** | **$0.134–$0.341** |

#### Inference Execution Costs
| Parameter | Value |
|---|---|
| Requests | 10 |
| Max tokens per request | 768 |
| Observed tokens/second (historical) | ~40 tokens/sec |
| Estimated tokens per request | ~300–768 |
| Estimated time per request | 7.5–19 sec |
| Total inference time | ~75–190 sec (1.25–3.2 min) |
| Inference cost | $0.019–$0.047 |

#### Post-Execution Costs
| Phase | Estimated Duration | Estimated Cost |
|---|---|---|
| Results retrieval via SFTP | 1 min | $0.015 |
| Pod termination + verification | 1–2 min | $0.015–$0.030 |
| Telemetry latency buffer | 2 min | $0.030 |

#### Total Estimated Cost Range

| Scenario | Duration | Cost |
|---|---|---|
| **Best case** (model cached or fast DL) | ~12 min | ~$0.178 |
| **Expected case** | ~20–25 min | ~$0.30–$0.37 |
| **Worst case** (slow DL, GPU queue) | ~35–40 min | ~$0.52–$0.59 |

> [!CAUTION]
> The **expected case cost ($0.30–$0.37) is at or above the authorized $0.35 ceiling**. The worst case significantly exceeds it.
>
> **The dominant cost driver is model weight download time.** `Qwen2.5-Math-7B-Instruct` has approximately 15 GB of weights. On a shared RunPod node, network bandwidth to HuggingFace Hub varies widely. Download times of 10–20 minutes are realistic. This alone may consume $0.148–$0.297 before a single inference request is submitted.

---

## Budget Feasibility Verdict

### Is $0.35 a realistic calibration ceiling?

**Verdict: MARGINAL — potentially infeasible.**

The $0.35 ceiling is achievable only if model weights are already cached on the RunPod node (unlikely for a fresh pod) or download completes in under 8 minutes. In the most common scenario (no cache, standard network speed), the download alone may push total spend to $0.25–$0.35 before inference begins.

**A more defensible calibration budget is $0.60–$0.75.** This provides a realistic buffer for a 30–40 minute session without changing the fundamental 10-request experiment scope.

### Is $7.00 preservation floor achievable?

**Verdict: NOT ACHIEVABLE at current reported balance of $1.3261.**

The last confirmed account balance ($1.3261) is $5.67 below the $7.00 preservation floor. Even if no additional charges have occurred since the incident, the account balance must be **topped up to at least $7.75–$8.00** before calibration is feasible ($7.00 floor + $0.75 spending buffer).

---

## Required Actions Before Financial Authorization

| Action | Responsibility | Current Status |
|---|---|---|
| Verify live RunPod account balance via dashboard | PI | PENDING |
| Verify zero active pods | PI | PENDING |
| Verify zero network volumes | PI | PENDING |
| Verify zero residual billable charges | PI | PENDING |
| Top up account to ≥ $8.00 if balance is still ~$1.33 | PI | PENDING |
| Confirm current RTX 4090 Secure Cloud price | PI | PENDING |
| Agree on revised spending ceiling if $0.35 is infeasible | PI + Agent | PENDING |
| Set `RUNPOD_API_KEY` in execution shell | Engineer | PENDING |

---

## Soft Billing Cap Warning

> [!WARNING]
> The software watchdog provides **best-effort** financial protection. It cannot provide a hard billing guarantee.
>
> RunPod billing occurs on the provider side. The watchdog monitors spend from the client side. If the watchdog process crashes, SSH hangs, or telemetry is delayed, charges may accumulate before the termination request is issued and confirmed.
>
> **Always maintain a financial buffer above the floor.** A $7.00 floor with a $1.33 balance is not a floor — it is already a violation. The PI must top up the account before any execution is authorized.

---

## Phase 3 Summary

| Item | Value | Verified? |
|---|---|---|
| Live account balance | Unknown | ❌ UNVERIFIED |
| Historical balance (post-incident) | $1.3261 | ✅ (from lock file) |
| Active pods | Unknown | ❌ UNVERIFIED |
| Network volumes | Unknown | ❌ UNVERIFIED |
| Residual billable charges | Unknown | ❌ UNVERIFIED |
| GPU price (RTX 4090 SC) | $0.89/hr (historical) | ⚠️ UNVERIFIED LIVE |
| Expected calibration cost | $0.30–$0.37 | ESTIMATED |
| $0.35 ceiling feasible | Marginal | ⚠️ ADVISORY |
| Current balance ≥ $7.35 minimum | ❌ NO (reported $1.33) | |
| Account top-up required | ≥ +$6.75 to reach $8.00 | PENDING PI ACTION |

**Phase 3 verdict: BLOCKED — Account balance must be verified and topped up before calibration authorization is possible.**

# StateShift Mission 15.2: Retryable Financial Shutdown State Machine

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_2/02_RETRYABLE_FINANCIAL_SHUTDOWN.md`  

---

## 1. Executive Problem Statement

In previous versions of the cost controller (`RobustCostControllerV7` and earlier), emergency shutdown triggering relied upon a simplistic single-boolean flag (`emergency_shutdown_triggered = True`). When a budget violation ($>\$2.00$) or time limit ($>160\text{ min}$) was detected:
1. `emergency_shutdown_triggered` was set to `True` immediately prior to or inside the trigger condition.
2. The controller invoked the emergency shutdown callback.
3. If that callback encountered a transient network hiccup, HTTP error (e.g., 502/503/504), or raised any exception, execution was interrupted.
4. On all subsequent monitoring ticks, `emergency_shutdown_triggered` remained `True`, causing the controller to return `action_taken = "NONE"`.

The shutdown action was therefore permanently suppressed after a single transient failure, leaving a billable GPU instance running without further termination attempts.

---

## 2. Finite State Machine Architecture (`RobustCostControllerV8`)

`RobustCostControllerV8` replaces the boolean trigger with a formal, persistent finite state machine with 7 explicit lifecycle states:

```
                  ┌──────────────────────┐
                  │    NOT_REQUESTED     │
                  └──────────┬───────────┘
                             │ Budget/Runtime breach
                             ▼
                  ┌──────────────────────┐
                  │      REQUESTED       │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │     DISPATCHING      │
                  └───────┬───────┬──────┘
       Callback Succeeded │       │ Callback Failed / Exception
                          ▼       ▼
┌────────────────────────────┐ ┌────────────────────────────┐
│     PROVIDER_CONFIRMED     │ │       RETRY_PENDING        │
└────────────────────────────┘ └──────────────┬─────────────┘
                                              │ Next tick (retry backoff)
                                              ▼
                                 (Attempt < Max Retries) ──> DISPATCHING
                                              │
                                 (Attempt >= Max Retries)
                                              ▼
                               ┌────────────────────────────┐
                               │  TERMINATION_UNCONFIRMED   │
                               │    (Critical Escalation)   │
                               └────────────────────────────┘
```

### State Definitions
1. `NOT_REQUESTED`: Normal operation. Machine spend and account deductions are within bounds.
2. `REQUESTED`: Limit breach detected; shutdown sequence queued.
3. `DISPATCHING`: Termination callback currently executing with atomic audit timestamping.
4. `DISPATCHED`: Termination callback executed, awaiting provider destruction confirmation.
5. `PROVIDER_CONFIRMED`: Provider-side pod destruction authoritatively confirmed (pod null or `TERMINATED`/`DELETED`). Terminal safe state.
6. `RETRY_PENDING`: Callback raised an exception or provider returned failure. Bounded exponential backoff timer armed. Retry queued for next monitoring tick.
7. `TERMINATION_UNCONFIRMED`: Bounded retries exhausted ($N \ge 3$) without provider destruction confirmation. Critical alerts emitted; manual intervention required.

---

## 3. Durable Persistence & Rehydration Semantics

To protect against orchestrator process crashes, OOM events, or supervisor reboots, the cost controller persists its shutdown lifecycle state to disk after every state transition:
- **State File**: `shutdown_state_<experiment_id>.json`
- **Write Mechanism**: Two-phase atomic write (`.tmp` $\to$ `flush()` $\to$ `os.fsync()` $\to$ `os.replace()`).
- **Rehydration Protocol**: Upon instantiation, `RobustCostControllerV8` checks for an existing state file:
  - If found, it recovers `shutdown_state`, `shutdown_attempts`, `last_attempt_time`, and `last_error_message`.
  - If in `RETRY_PENDING` or `DISPATCHING`, it resumes retry dispatch without resetting attempt counters.
  - If in `PROVIDER_CONFIRMED`, it safely suppresses duplicate shutdown attempts while logging confirmation.

---

## 4. Test Verification Summary

Phase 2 verified this state machine across four dedicated test cases in `research_mission_15_2/tests/test_financial_shutdown_retry.py`:
1. `test_callback_exception_enters_retry_pending_and_retries`: Callback throws `RuntimeError("Transient connection error")`. Tick 1 transitions to `RETRY_PENDING` (`action_taken="RETRY_PENDING"`). Tick 2 retries and succeeds, transitioning to `PROVIDER_CONFIRMED` (`action_taken="SHUTDOWN_CONFIRMED"`).
2. `test_callback_returns_false_enters_retry_pending`: Callback returns `False`. State transitions to `RETRY_PENDING` and retries on subsequent tick until confirmed.
3. `test_controller_restarts_and_resumes_unresolved_shutdown`: Controller process terminated mid-shutdown. New instance rehydrates state from disk and executes retry without dropping previous attempt records.
4. `test_retries_exhausted_escalates_to_unconfirmed`: Callback persistently fails across all allocated retry attempts ($N=3$). State transitions to `TERMINATION_UNCONFIRMED`, emitting critical escalation alerts.

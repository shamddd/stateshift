# Research Mission 22.2 — Cloud Financial Safety and Termination Audit

## 1. Financial Ledger & Hardware Allocation

- **Account Balance (RunPod)**: Verified at **$10.1065 USD**.
- **Mission 22.2 Cloud Authorization**: **$0.00 USD** (Strictly Local CPU Audit).
- **Target Confirmatory Cloud Allocation**: Maximum **$1.60 USD** ceiling.
- **Hardware Profile**: Exactly one (1) NVIDIA RTX 4090 (24GB VRAM, Secure Cloud).
- **Estimated Execution Duration**: 45 to 55 minutes for 924 inference requests.
- **Projected Pod Cost**: $0.74/hr $\times$ 1.0 hr $\approx$ **$0.74 USD** (Well beneath the $1.60 ceiling).

---

## 2. The 11 Fail-Closed Financial & Hardware Safety Barriers

The execution architecture enforces 11 independent, defense-in-depth safety barriers:

1. **Physical File Lock Barrier**: The existence of `.cloud_execution_locked` in the repository root halts any cloud initialization before any network socket is opened.
2. **Explicit Cloud Opt-In Flag**: Cloud provisioning requires the `--cloud-runpod` CLI argument. Without this flag, the runner defaults to local dry-run execution.
3. **Cryptographic Token Verification**: Cloud execution requires passing `--authorization-token <TOKEN>`, whose SHA-256 hash must match the pre-shared secret.
4. **Hard Financial Ceiling Guard**: The runner queries the RunPod balance API and computes the maximum spend ceiling ($1.60 USD); if projected cost exceeds $1.60, execution halts.
5. **Preservation Floor Guard**: The runner enforces a minimum account balance floor of $5.00 USD; provisioning is aborted if remaining funds would drop below $5.00.
6. **Strict Single-Pod Concurrency**: The runner logic allows `max_pods = 1`. Any loop or retry logic is barred from spinning up secondary pods.
7. **Secure Cloud Tier Constraint**: Only RunPod Secure Cloud data centers are permitted; lower-reliability Community Cloud endpoints are blocked.
8. **Hard Execution Timeout**: An internal watchdog terminates the run if elapsed wall-clock time exceeds 60 minutes.
9. **Idle Daemon Auto-Termination**: If no generation record is completed within 300 seconds, the pod is terminated automatically.
10. **Signal Trap Handlers**: `SIGINT`, `SIGTERM`, and `SIGHUP` handlers are registered to trap aborts and issue an immediate API termination call.
11. **`atexit` Cleanup Guarantee**: Python's `atexit` module registers the pod termination routine, ensuring cleanup even on unexpected uncaught exceptions.

---

## 3. External Supervisor Recommendation

While the in-process safety barriers provide robust defense, standard cloud reliability practices recommend an **External Watchdog Supervisor**:
- A lightweight independent script running on the local workstation that monitors the pod status via the RunPod REST API.
- If the local runner process exits, crashes, or loses network connectivity, the external supervisor issues a force-kill command to the remote pod after 5 minutes of inactivity.
- This guarantees zero runaway financial expenditure under total client failure.

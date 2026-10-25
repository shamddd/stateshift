# 02 Independent Watchdog Process Specification

**Module:** `research_mission_15_5/supervision/independent_financial_watchdog.py`

---

## 1. Process Architecture
The watchdog runs as a completely independent OS process spawned via `subprocess.Popen` with its own process group (`os.setpgrp`).
- **Decoupled Lifecycle:** Possesses an independent PID tracked in `watchdog_<exp_id>.pid`.
- **Clock Independence:** Utilizes its own `time.monotonic()` ticker, immune to controller clock tampering or stalls.
- **Heartbeat Monitoring:** Monitors `controller_state_<exp_id>.json`. If the controller heartbeat becomes stale (>30.0s) or the controller process dies unexpectedly, the watchdog enters fail-safe emergency termination.
- **Controller SIGKILL Resilience:** Verified via Scenario B: killing the controller process with `kill -9` leaves the watchdog active and executing its supervision loop until safe pod destruction is verified.

## 2. Autonomous Termination Authority
The watchdog holds direct provider API credentials (`RUNPOD_API_KEY`) and dispatches GraphQL mutations (`podTerminate`) independently if:
1. Effective spend reaches or exceeds `$0.2500` USD in calibration mode (or `$2.5000` USD in full production).
2. Pod uptime exceeds maximum authorized duration + 5-minute grace period.
3. Account balance drops below the mandatory preservation floor (`$7.0000` USD).
4. Controller heartbeat goes permanently stale.

# StateShift Canonical Production Entry Point: stateshift_launch.py

**Project:** StateShift Research Mission 15.6  
**Document:** `04_CANONICAL_PRODUCTION_ENTRY_POINT.md`  
**Module:** `research_mission_15_6.runner.stateshift_launch`  
**Status:** Unified Canonical CLI Entry Point for All Operations  

---

## 1. Overview & Architectural Role

`research_mission_15_6.runner.stateshift_launch` is the single, canonical production entry point for the entire StateShift project. It completely unifies:
- **Preflight checks**
- **10-request GPU calibration**
- **400-request production replication**
- **Simulated fault-injection testing**

No other script should be executed directly by operators.

---

## 2. Command Line Interface Specification

```bash
python3 -m research_mission_15_6.runner.stateshift_launch [OPTIONS]
```

### Core Execution Arguments

| Option | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `--mode` | string | `calibration` | Execution mode: `preflight`, `calibration`, `production`, `simulation`. |
| `--experiment-id` | string | *Required* | Unique experiment identifier (e.g. `stateshift-calibration-10`). |
| `--manifest` | path | *Auto-selected* | Path to manifest JSON. If omitted, automatically selects mode-appropriate manifest (`calibration_10_manifest.json` or `primary_100_manifest.json`). |
| `--authorization` | path | `None` | Path to signed cryptographic session authorization document (`.json`). |
| `--trusted-public-key`| string/path | `None` | Base64-encoded Ed25519 PI public key, or path to file containing it. |
| `--allow-test-key` | flag | `False` | Allows temporary testing key (STRICTLY FOR TESTING ONLY; prohibited in production). |

### Infrastructure Connection Arguments

| Option | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `--pod-id` | string | `None` | RunPod GPU Pod ID (e.g. `xydg2t4rzrx71d`). |
| `--ip` | string | `None` | SSH public IP address of the pod. |
| `--port` | integer | `22` | SSH port forwarded by RunPod. |
| `--ssh-key` | path | `None` | Path to local SSH private key file. |

### Directory & Budget Arguments

| Option | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `--local-data-dir` | path | `data/primary_run` | Local directory for storing checkpoints, logs, receipts. |
| `--remote-work-dir`| path | `/workspace/stateshift_run` | Remote working directory inside the pod container. |
| `--max-cost` | float | *Mode default* | Maximum authorized dollar spend ($0.35 for calibration, $2.50 for production). |
| `--max-runtime` | float | `60.0` | Maximum allowed runtime in minutes. |
| `--gpu-rate` | float | `0.89` | GPU hourly billing rate in USD (RTX 4090 standard). |
| `--poll-interval` | float | `1.0` | Polling cycle frequency in seconds. |
| `--resume` | flag | `False` | Resumes interrupted execution from existing local checkpoint. |

### Simulation Arguments (Rejected in CALIBRATION and PRODUCTION)

`--simulate-records [N]`, `--simulate-spend [USD]`, `--simulate-corrupt-dataset`, `--simulate-unconfirmed-termination`, `--simulate-sftp-failure`, `--simulate-ssh-disconnect`, `--simulate-runtime-overrun`, `--simulate-engine-fallback`, `--simulate-deployment-failure`, `--simulate-watchdog-crash`, `--simulate-corrupt-checkpoint`.

---

## 3. Strict Exit Code Contract

| Exit Code | Semantic Meaning | Scenarios Triggering Code |
| :---: | :--- | :--- |
| **`0`** | **Verified Success** | Execution achieved target rollouts, local dataset passed 100% verification, verification receipt generated, provider termination confirmed. |
| **`1`** | **Execution Failure** | Runtime network drop, SSH hang, SFTP failure, spend emergency breach, unconfirmed pod termination. |
| **`2`** | **Security / Configuration Rejection** | Missing/invalid cryptographic signature, pod ID mismatch, budget ceiling mismatch, expired authorization, replayed nonce, manifest hash mismatch, simulation flag passed in paid mode. |

---

## 4. Canonical Invocation Examples

### 1. Simulated 10-Request Calibration (Local Rehearsal)
```bash
python3 -m research_mission_15_6.runner.stateshift_launch \
    --mode simulation \
    --experiment-id exp_sim_rehearsal_01 \
    --local-data-dir data/sim_rehearsal \
    --simulate-records 10 \
    --simulate-spend 0.15 \
    --poll-interval 0.05
```

### 2. Physical RunPod GPU Preflight
```bash
python3 -m research_mission_15_6.runner.stateshift_launch \
    --mode preflight \
    --experiment-id stateshift-preflight-check \
    --pod-id xydg2t4rzrx71d \
    --ip 123.45.67.89 \
    --port 22222 \
    --ssh-key ~/.ssh/id_ed25519 \
    --trusted-public-key $STATESHIFT_TRUSTED_PUBLIC_KEY
```

### 3. Production Calibration (Human-Authorized)
```bash
python3 -m research_mission_15_6.runner.stateshift_launch \
    --mode calibration \
    --experiment-id stateshift-calib-real-10 \
    --pod-id xydg2t4rzrx71d \
    --ip 123.45.67.89 \
    --port 22222 \
    --ssh-key ~/.ssh/id_ed25519 \
    --authorization ./auth_calibration_signed.json \
    --trusted-public-key $STATESHIFT_TRUSTED_PUBLIC_KEY \
    --local-data-dir data/calibration_run \
    --max-cost 0.35
```

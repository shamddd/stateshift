# StateShift Mission 15.3: Exact Production CLI Subprocess Tests

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Author**: Sham Satish Thakare (`github.com/shamddd`)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Deliverable**: `research_mission_15_3/08_EXACT_CLI_END_TO_END_TESTS.md`  

---

## 1. Executive Summary

To eliminate the "isolated helper class illusion" discovered in Mission 15.2, acceptance testing in Mission 15.3 was conducted exclusively by invoking the actual production CLI (`stateshift_production_runner.py`) as a standalone operating system subprocess across 10 mandatory simulation scenarios.

---

## 2. The 10 Mandatory Subprocess Scenarios

```bash
pytest -v research_mission_15_3/tests/test_exact_cli_subprocess_scenarios.py
```

| Scenario | Tested Failure / Operational Mode | Verification Command & Strategy | Result |
|:---:|:---|:---|:---:|
| **A** | **Complete Experiment** | Subprocess runs 400 rollouts, verifies all 18 dimensions, confirms normal termination, writes receipts. | **PASS** |
| **B** | **Budget Stop** | Subprocess simulates 143 rollouts, triggers spend at \$2.05, confirms Priority-1 emergency shutdown. | **PASS** |
| **C** | **SSH Disconnection** | Subprocess simulates transient SSH socket drop during inference; runner reconnects and completes. | **PASS** |
| **D** | **SFTP Failure** | Subprocess simulates SFTP socket hang; financial watchdog remains active and triggers termination. | **PASS** |
| **E** | **Controller Crash & Resume** | Subprocess 1 is SIGKILLed after 200 rollouts; Subprocess 2 resumes with `--resume` to 400 rollouts without duplicates. | **PASS** |
| **F** | **Provider Outage Escalation** | Subprocess simulates unconfirmed termination; operator alert and `CRITICAL_ALERT_POD_*.txt` committed to disk. | **PASS** |
| **G** | **Dataset Corruption Gate** | Subprocess writes 400 records with unparseable trailing line; gate rejects dataset (`INTEGRITY_FAILURE`). | **PASS** |
| **H** | **Authorization Mismatch** | Subprocess invoked with mismatched pod ID in authorization doc; fails closed before cloud action. | **PASS** |
| **I** | **Engine Fallback** | Subprocess simulates vLLM init failure; automatic fallback to Transformers verified in output records. | **PASS** |
| **J** | **Runtime Overrun** | Subprocess simulates elapsed runtime exceeding 160 minutes; watchdog halts run before safety reserve breach. | **PASS** |

**Pass Rate**: 10 / 10 passed (100%).

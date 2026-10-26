# StateShift: Forensic Repository & Evidence Inventory
## Deliverable 01 — Artifact Authentication, SHA-256 Ledger & Evidence Classification
**Document Version:** 1.0.0  
**Audit Timestamp:** 2026-10-26T07:59:00+05:30  
**Principal Investigator:** Sham Satish Thakare  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Repository Working Copy:** `/Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/`  
**Current Git Branch:** `research/stateshift-final-preexperiment-validation`  
**Current HEAD Commit:** [`9564ec3ac548ae0dc528311a6e601a0913456925`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_6/runner/execute_authorized_budget1_calibration.py) (`9564ec3`)  
**Calibration Execution Commit:** [`d48d7ec`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_6/runner/execute_authorized_budget1_calibration.py)  

---

## 1. Master Evidence Inventory Ledger

Every artifact relevant to the calibration run (`stateshift_calib_b1_01`), financial reconciliation, supervisor daemon, frozen manifests, and manuscript has been inspected on physical disk and hashed using SHA-256:

| Artifact Description | Relative Path | Byte Size | SHA-256 Hash | Evidence Classification |
| :--- | :--- | :---: | :--- | :--- |
| **Calibration Generations JSONL** | `data/primary_run/stateshift_calib_b1_01_generations.jsonl` | 23,347 B | `3efcb61c27b95d01ed8784b2fd114796c5baf1546a336a459ca5da56d5c108b5` | **VERIFIED PRIMARY EVIDENCE** |
| **Calibration 10 Manifest** | `research_mission_15_6/manifests/calibration_10_manifest.json` | 13,662 B | `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6` | **VERIFIED PRIMARY EVIDENCE** |
| **Primary 400 Manifest** | `research_mission_15_6/manifests/primary_100_manifest.json` | 557,212 B | `3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d` | **VERIFIED PRIMARY EVIDENCE** |
| **Session Authorization Token** | `data/primary_run/session_auth_calib_b1.json` | 920 B | `147281e7c5c1e0070a4f20362b60de508e8866792dca9b248f6edfd1a50a648d` | **VERIFIED PRIMARY EVIDENCE** |
| **Timeline Events Ledger** | `data/primary_run/gpu_session_timeline_events.jsonl` | 7,649 B | `9d83a2e6883608af2ede841d3298ef3e6c14c002a23af7d52a1261fcdf6c151b` | **VERIFIED PRIMARY EVIDENCE** |
| **Provisioning Audit Ledger** | `data/primary_run/provisioning_audit.jsonl` | 1,419 B | `cddfcf71dfe3fccb9a2b52f7e039c81d828c85240f8cf51fc0bf87481aa0cc1a` | **VERIFIED PRIMARY EVIDENCE** |
| **Calibration Reconciliation JSON**| `data/primary_run/calibration_reconciliation_b1.json` | 842 B | `83abebdf4a5579cf7df0527b5fc4ba2a2c92fdd93491eb91021eebb4fd7f62bf` | **VERIFIED PRIMARY EVIDENCE** |
| **Termination State Receipt** | `data/primary_run/termination_state_stateshift_calib_b1_01.json`| 359 B | `438a8204e51d5baee61b2bc0fa2dbc8b8991d150c80502ecee74c62d48abb444` | **VERIFIED PRIMARY EVIDENCE** |
| **Nonces Registry Store** | `data/primary_run/used_nonces.json` | 217 B | `c930d16e7a0432e1474940990f5fb54f850a03b4908979231ccb659242f956f1` | **VERIFIED PRIMARY EVIDENCE** |
| **Watchdog State Ledger** | `data/primary_run/watchdog/watchdog_state_stateshift_calib_b1_01.json` | 423 B | `5a0438b31cf8695dd09681d71b08edb03b197e24724d86bc18abd401002d1dab` | **VERIFIED PRIMARY EVIDENCE** |
| **Watchdog Heartbeat** | `data/primary_run/watchdog/watchdog_heartbeat_stateshift_calib_b1_01.json` | 269 B | `0ae57a94ea876eb374111527f17f15b7da57901d33796960df9b2b141a8dd45e` | **VERIFIED PRIMARY EVIDENCE** |
| **Watchdog Pod Registration** | `data/primary_run/watchdog/watchdog_register_pod_stateshift_calib_b1_01.json` | 147 B | `1873118ed9e3df3cb5ef2b77c3e517ee64b18cb056ae57097acb46a1d0f5515d` | **VERIFIED PRIMARY EVIDENCE** |
| **Watchdog Readiness Token** | `data/primary_run/watchdog/watchdog_readiness_stateshift_calib_b1_01_sess_b1_1792980363.json` | 515 B | `cabd42cb979141766d5d5bb0d9177e6a766ba16192179bb8b448b0637144088e` | **VERIFIED PRIMARY EVIDENCE** |
| **Manuscript LaTeX Source** | `08_REVISED_STATESHIFT.tex` | 25,078 B | `333c914ea71792daee65bdb0cec2138c80dff9830a9c9e801c7e6a55bc0226f6` | **VERIFIED PRIMARY EVIDENCE** |
| **Cloud Execution Lock (Repo)** | `.cloud_execution_locked` | 640 B | `0b2da8ae8c649082d3e44f176eddc4689010bfdd45d02bcd2b5a5652484ec8de` | **VERIFIED PRIMARY EVIDENCE** |
| **Cloud Execution Lock (Parent)**| `../.cloud_execution_locked` | 640 B | `0b2da8ae8c649082d3e44f176eddc4689010bfdd45d02bcd2b5a5652484ec8de` | **VERIFIED PRIMARY EVIDENCE** |
| **Deliverable 00 Summary** | `budget1_calibration_execution/00_EXECUTIVE_VERDICT.md` | 6,388 B | `0c118e79a45e1066c4af4a282377e193ce3ab505312424cd7c1e68e9bcc3bfd4` | **SECONDARY REPORT** |
| **Deliverable 05 Timeline** | `budget1_calibration_execution/05_GPU_SESSION_TIMELINE.md` | 7,444 B | `a9cbe1892ae88d55993af8fa4100060fbd737ec7b3ae9c1f9008fa7adc867141` | **SECONDARY REPORT** |
| **Deliverable 06 Audit** | `budget1_calibration_execution/06_AUTHENTIC_GENERATION_AUDIT.md` | 6,407 B | `a6f19ae2278c3ea952245f6751be0311e7cc2160b1182882021484cd03226848` | **SECONDARY REPORT** |
| **Deliverable 07 Financial** | `budget1_calibration_execution/07_FINANCIAL_RECONCILIATION.md` | 4,188 B | `a309c0dfb78d9491832399cd9979c344e090e0993c81287da65ae3e49bc8bbce` | **SECONDARY REPORT** |
| **Deliverable 08 Proof** | `budget1_calibration_execution/08_PROVIDER_TERMINATION_PROOF.md` | 3,517 B | `6d07dc392da4c777e2de264a2883a2f6d36614065f060b5060a2f49d33c93c28` | **SECONDARY REPORT** |
| **Deliverable 09 Forecast** | `budget1_calibration_execution/09_PRIMARY_EXPERIMENT_COST_FORECAST.md` | 4,360 B | `e9cd71b21f23acbc69dae6874aab7f0f9855d1a8e7766ba92fec2cc9af2fc0b8` | **SECONDARY REPORT** |
| **Deliverable 10 Scientific** | `budget1_calibration_execution/10_FINAL_SCIENTIFIC_REPORT.md` | 6,980 B | `bfb2a6cd97a65947abed56bdf65a7243c048b5bbc28b68f68818283a22049769` | **SECONDARY REPORT** |

---

## 2. Evidence Classification Criteria

1. **VERIFIED PRIMARY EVIDENCE:**
   Raw files produced by execution processes, runtime supervisor daemons, cryptographic signatures, immutable input manifests, or physical system state. These records possess direct provenance from the GPU session, operating system, or git tree.
2. **SECONDARY REPORT:**
   Interpretive analyses, summaries, markdown documentation, or narrative reports synthesized from primary evidence. These provide contextual synthesis but require verification against primary sources.
3. **INCOMPLETE:**
   Artifacts that omit essential fields, are truncated, or lack necessary cryptographic/provenance headers. *(None identified).*
4. **MISSING:**
   Artifacts specified by documentation or expected by protocol that could not be found on disk. *(None identified: the primary 400 manifest was confirmed at `research_mission_15_6/manifests/primary_100_manifest.json` matching the exact SHA-256).*
5. **CONTRADICTORY:**
   Artifacts containing mutually exclusive claims, conflicting timestamps, or mismatched telemetry. *(None identified).*

---

## 3. Physical GPU & Model Revision Provenance

* **Model Revision:** Canonical 40-character commit `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` is recorded in each of the 10 JSON records in `data/primary_run/stateshift_calib_b1_01_generations.jsonl`.
* **Hardware Provenance:** Verified on physical `NVIDIA GeForce RTX 4090, 24564 MiB, Driver 595.91.07` hosted at IP `209.170.80.132:10254` via `nvidia-smi` captured in the live SSH audit and logged in `data/primary_run/gpu_session_timeline_events.jsonl`.
* **Execution State:** Cloud execution lock is strictly `ACTIVE` in both repo root and parent directory.

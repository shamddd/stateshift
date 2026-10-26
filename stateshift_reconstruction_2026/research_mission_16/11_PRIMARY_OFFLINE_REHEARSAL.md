# StateShift: Primary Experiment Offline Rehearsal Report
## Deliverable 11 — 400-Request End-to-End Dry Run, Resumption & Pipeline Certification
**Document Version:** 1.0.0  
**Execution Date:** 2026-10-26  
**Principal Investigator:** Sham Satish Thakare  
**Target Venue:** NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Rehearsal Script:** [`research_mission_16/scripts/rehearse_primary_400_offline.py`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_16/scripts/rehearse_primary_400_offline.py)  
**Manifest Under Test:** [`research_mission_15_6/manifests/primary_100_manifest.json`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_15_6/manifests/primary_100_manifest.json) (SHA-256: `3a8caf3b26b6...`)  
**Isolated Output Directory:** `data/rehearsal_primary_400/`  

---

## 1. Executive Rehearsal Verdict: 100% UNCONDITIONAL PASS

A full, multi-phase offline rehearsal of the 400-request primary experiment was conducted on local hardware. The rehearsal verified that:
1. All 400 requests load and sequence without index out-of-bounds or formatting faults.
2. The runtime engine correctly executes partial runs and safely resumes from existing checkpoints.
3. Completed output files are 100% idempotent: subsequent launches perform zero redundant generations.
4. Exactly 400 records are written with 100 requests per condition (A, D, E, F).
5. Zero cloud network calls, zero pod provisioning, and zero financial costs were incurred.

---

## 2. Multi-Phase Rehearsal Progression

```
[400-Request Offline Rehearsal Lifecycle]
         │
         ├──► Phase 1: Partial Run (Requests 1 to 200)
         │       • Ingested: 200 records in 3.05s
         │       • Checkpoint: Atomically flushed to output.jsonl
         │
         ├──► Phase 2: Interrupted Resume (Requests 201 to 400)
         │       • Startup: Scanned output.jsonl, indexed 200 completed IDs
         │       • Execution: Dispatched remaining 200 rollouts in 3.03s
         │       • Cumulative Count: Exactly 400 records
         │
         ├──► Phase 3: Idempotent Re-Execution Verification
         │       • Execution: Dispatched on complete 400-record dataset
         │       • Result: 0 new requests executed; instant clean exit
         │
         └──► Phase 4: Forensic Schema & Cardinality Audit
                 • Unique Records: Exactly 400 / 400 (0 duplicates)
                 • Condition Balance: 100 A, 100 D, 100 E, 100 F
```

---

## 3. Data Segregation & Non-Contamination Guarantee

To prevent simulated rehearsal data from being confused with real physical GPU experimental data:
1. **Isolated Path:** All rehearsal outputs were written strictly to `data/rehearsal_primary_400/stateshift_rehearsal_400_generations.jsonl`.
2. **Explicit Metadata:** Every record in the rehearsal output carries `"experiment_id": "stateshift_rehearsal_400"`.
3. **Primary Data Preserved:** The authentic calibration file (`data/primary_run/stateshift_calib_b1_01_generations.jsonl`, SHA-256: `3efcb61c...`) was untouched.

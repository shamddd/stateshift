# StateShift Deliverable 19: Next GPU Mission Handoff Protocol

**Project**: StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (github.com/shamddd)  
**Target Venue**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Next Stage**: Human-Authorized 10-Request Physical Calibration  
**Cloud Execution Status**: FAIL-CLOSED LOCK ACTIVE  
**Date**: October 26, 2026  

---

## 1. Executive Handoff Statement

Principal Investigator Sham Satish Thakare:

The local pre-experiment engineering, scientific verification, evaluation, and manuscript completion mission is **100% COMPLETE**. All 101 automated unit, adversarial, regression, and simulation tests pass cleanly, and the NeurIPS manuscript PDF (`08_REVISED_STATESHIFT.pdf`) has been compiled and validated.

Zero cloud dollars were expended ($0.00). Cloud execution remains strictly locked.

The system is now parked at the **Physical Calibration Gate**. No autonomous actions, retries, or cloud allocations can take place without your explicit, separate human authorization.

---

## 2. Scope & Boundaries of the Next Operation

When you choose to authorize the next stage, the operational scope is strictly restricted to:

- **Provider**: RunPod
- **Cloud Tier**: **Secure Cloud ONLY** (Community Cloud fallback prohibited)
- **Target GPU**: Exactly one NVIDIA RTX 4090 (24 GB VRAM)
- **Maximum Number of Pods**: **Exactly ONE ($N=1$)**
- **Experiment Scope**: Exactly 10 frozen calibration requests (`calibration_10_manifest.json`)
- **Manifest SHA-256**: `f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6`
- **Model**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Pinned Revision**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Planned Spending Ceiling**: **$0.35 USD**
- **Emergency Shutdown Trigger**: **$0.25 USD**
- **Account Preservation Floor**: **$7.00 USD**
- **Maximum Staging Latency**: 180 seconds (wall-clock monotonic deadline)
- **Full 400-Request Experiment**: **STRICTLY PROHIBITED** during calibration.

---

## 3. Human Authorization Protocol

To initiate physical calibration, the following two steps are required:

### Step 1: Account Balance Verification
Ensure your RunPod balance is confirmed above the $\$7.00$ floor:
$$\text{Current Balance} \ge \$7.35 \text{ USD}$$

### Step 2: Human Execution Approval
Provide the canonical human authorization prompt:
> *"I approve provisioning one Secure Cloud RTX 4090 on RunPod for the StateShift 10-request calibration, with a planned spending limit of $0.35, emergency shutdown at $0.25, and a $7.00 account balance floor. Do not run the full 400-request experiment."*

The launch orchestrator will then:
1. Temporarily unlock the local execution lock exclusively for the duration of this single session.
2. Spawn and verify the pre-provision independent supervisor daemon.
3. Provision exactly one Secure Cloud RTX 4090 pod.
4. Execute the 10 calibration requests within bounded deadlines.
5. Retrieve and evaluate the 10 completions using `math_answer_evaluator.py`.
6. Issue emergency teardown and confirm complete pod destruction.
7. Return the Calibration Scorecard (Deliverable 13 criteria).

---

## 4. Summary of Certified Local Assets

All deliverables are checked in on branch `research/stateshift-final-preexperiment-validation`:
- Deliverables folder: `final_preexperiment/`
- Test suite: `research_mission_15_6/tests/` (101 passing tests)
- Evaluation pipeline: `research_mission_15_6/evaluation/math_answer_evaluator.py`
- Compiled manuscript: `08_REVISED_STATESHIFT.pdf`

The handoff is complete. We await your decision.

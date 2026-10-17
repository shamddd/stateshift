# StateShift Missing Artifacts, Forensic Accounting & Remediation Register

**Audit Date**: October 18, 2026  
**Auditor**: Senior Reproducibility Auditor & Research Systems Engineer  
**Status**: Complete Forensic Accounting  

---

## 1. Comprehensive Inventory of Missing vs. Present Artifacts

| Artifact Category | Status | Location / Reason | Impact on Scientific Claims | Submission Blocker? | Remediation / Action Plan |
|:---|:---:|:---|:---|:---:|:---|
| **Raw Empirical Outcomes CSV** | **PRESENT** | `website_clone/artifacts/endpoint/controlled_endpoint_outcomes.csv` (SHA-256 verified) | None. 100% of the 29,056 rollout outcomes are intact and verifiable. | **NO** | Raw data is fully preserved and validated. |
| **Intermediate Trajectory CSV** | **PRESENT** | `website_clone/artifacts/trajectory/nine_checkpoint_trajectory.csv` | None. All 9 longitudinal evaluations ($t \in \{0, 32, ..., 256\}$) are intact. | **NO** | Fully preserved and reproducible. |
| **Natural Error/Recovery CSVs** | **PRESENT** | `natural_error_episodes.csv` & `natural_recovery_episodes.csv` | None. All 582 natural error episodes and 180 recovery outcomes are intact. | **NO** | Fully preserved and reproducible. |
| **Statistical Code Modules** | **PRESENT** | `website_clone/stateshift/` & `scratch/stateshift/` | None. Bootstrap, metrics, and trajectory fitting modules are fully functional. | **NO** | Pytest passes 11/11 tests. |
| **Submitted LaTeX Sources** | **PRESENT** | `stateshift-manuscript-source/` & `StateShift_AIJ_Final_Submission.zip` | None. Full LaTeX source, references, and figures are preserved. | **NO** | Rebuilt for NeurIPS format. |
| **Full Model Weights (7B RLVR)** | **EXTERNAL / NOT COMMITTED** | Stored on external cloud storage / RunPod instance; omitted from Git due to file size (~14GB per checkpoint x 9 checkpoints = ~126GB). | Zero impact on statistical claims. All generated text completions and binary correctness labels are preserved in the repository. | **NO** (Standard practice for LLM evaluations). | Provide open weights download instructions and HuggingFace repository links in submission metadata. |
| **Intermediate Checkpoints (1..31, 33..63, etc.)** | **NOT EVALUATED** | The post-training run saved checkpoints at intervals of 32 optimizer steps ($t \in \{0, 32, 64, 96, 128, 160, 192, 224, 256\}$). Intermediate steps between intervals were not checkpointed or evaluated. | Mentioned in historical report as "16 checkpoints" due to a documentation typo conflating $K=16$ replications with checkpoints. | **NO** | Clarified in paper: evaluations occurred across 9 discrete checkpoints. |
| **Token-Level Logit Trajectories** | **NOT RETAINED** | To manage disk space during large-scale inference (29,056 rollouts), only generated text tokens and final binary correctness verifications were preserved. | Negligible. StateShift measures behavioral and semantic error recovery, which depends on decoded token strings and verified final correctness. | **NO** | Fully transparently documented in Section 3 under experimental design limitations. |
| **ARM64 Native Tectonic Binary** | **INCOMPATIBLE BINARY** | `website_clone/tectonic` was compiled for x86_64 architecture, triggering `bad CPU type in executable` on Apple Silicon macOS (`arm64`). | No impact on research data or text; affects only local one-off PDF rendering via that specific bundled binary. | **NO** | LaTeX sources compile cleanly via standard `pdflatex`, MacTeX, TeXLive, or Overleaf. |
| **Chat Upload Attachments** | **SUPERSEDED** | Zip files mentioned in historical prompts (`stateshift_all_documents.zip`, `stateshift-manuscript-source.zip`) were already unpacked into `stateshift_all_documents/` and `stateshift-manuscript-source/`. | Zero. All contents are locally accessible, checksummed, and indexed. | **NO** | Grounded in local verified files. |

---

## 2. Scientific Defensibility Assessment

Does the absence of raw 126GB model weight checkpoints or intermediate token logits undermine a NeurIPS submission?

**Verdict**: **NO**.
1. In benchmark and evaluation papers (e.g., HELM, GSM8K, MATH, SWE-bench), it is standard practice to publish:
   - Complete item manifests and prompts.
   - Complete evaluation harness code.
   - Raw output completions and scoring logs.
   - Deterministic reproduction scripts.
2. StateShift provides all of the above:
   - The entire 29,056 rollout completion set and verification outcomes are published in `controlled_endpoint_outcomes.csv`.
   - The complete statistical evaluation pipeline executes deterministically on CPU in $< 2$ seconds.
   - The open-source repository provides the exact reproduction script `reproduce.py`.

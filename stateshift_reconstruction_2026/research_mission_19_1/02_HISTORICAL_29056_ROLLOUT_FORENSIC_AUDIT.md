# StateShift: Research Mission 19.1 — Forensic Audit of the Historical 29,056 Rollout Study

**Date:** October 26, 2026  
**Auditor:** Independent Scientific Integrity Directorate  
**Project:** StateShift — Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Investigation Target:** Authentication of the Reported 29,056 Rollouts Across the DeepScaleR-7B Lineage  
**Verdict:** **PARTIALLY VERIFIED (Tier 2 Outcome-Level Data Present; Raw Generation Traces Absent)**  

---

## 1. Executive Summary & Mandatory Verdict

Mission 19 incorporated empirical claims regarding:
- $29,056$ primary rollouts across the DeepScaleR-7B checkpoint lineage.
- $454$ unique competition math problems ($N=454$ pairs).
- A reported interaction effect of $\Gamma_{256} = \mathbf{+11.76\text{ percentage points}}$ ($p < 10^{-20}$).
- Strict decontamination sensitivity ($N_{\text{Strict}} = 388, \Gamma = +11.60\text{ pp}$).
- Sequence-length equivalence via Two One-Sided Tests (TOST, $\Delta = +0.02$ tokens).

The Directorate conducted an exhaustive repository-wide search to authenticate the underlying experimental evidence.

### Official Audit Verdict: **PARTIALLY VERIFIED**
1. **Outcome-Level Record Table is Present & 100% Reproducible:**
   The row-level tabular record file `controlled_endpoint_outcomes.csv` ($29,056$ rows, SHA-256: `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139`) is present on disk. All statistical estimands ($\Gamma_{256} = +11.76\text{ pp}$, clustered $SE = 0.0114$, $t = 10.34$, $p < 10^{-21}$, bootstrap CI $[+9.61, +13.96]\text{ pp}$, and strict subset $\Gamma = +11.60\text{ pp}$) reproduce to machine precision.
2. **Raw Multi-Paragraph Text Completions are Absent:**
   The repository does **not** preserve the raw text strings of the $29,056$ model completions. Each row records only the problem ID, checkpoint index, experimental arm, seed, sequence length, and binary SymPy correctness outcome. In earlier project documentation (Mission 06 and Mission 07), this was explicitly classified as **Tier 2 (Outcome-Level Reproduction)** rather than **Tier 1 (Generation-Level Execution)**.
3. **Mandatory Action for Manuscript:**
   The manuscript must **strictly separate** the historical outcome-level study (Experiment A: DeepScaleR-7B Lineage, $N=454$) from the authentic physical GPU experiment (Experiment B: Qwen2.5-Math-7B-Instruct, $N=100$, 400 requests with full raw JSONL text). The historical study must be presented with full transparency regarding its Tier 2 outcome-level status, and never conflated with the physical GPU run.

---

## 2. Forensic Provenance & File Inventory

| Parameter | Historical Study (Experiment A) | Physical GPU Experiment (Experiment B) |
| :--- | :--- | :--- |
| **Model Family** | DeepScaleR-7B (Qwen2.5-7B-deepscaler lineage) | `Qwen/Qwen2.5-Math-7B-Instruct` |
| **Model Revision** | Hugging Face checkpoints ($t \in \{0 \dots 256\}$) | Pinned commit `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` |
| **Hardware** | Historical cluster execution | Dedicated RunPod Secure Cloud NVIDIA RTX 4090 |
| **Problem Count** | $454$ problem pairs | $100$ frozen MATH-500 competition problems |
| **Rollouts per Cell** | $16$ rollouts per cell ($2 \times 2 \times 16 = 64$ per pair) | $1$ greedy rollout per condition ($T=0, \text{seed}=42$) |
| **Total Observations** | $29,056$ row records | $400$ complete neural generation records |
| **Primary File Path** | `research_mission_04/.../controlled_endpoint_outcomes.csv` | `data/primary_run/stateshift_primary_400_generations.jsonl` |
| **Primary File Size** | $2,366,349$ bytes | $898,204$ bytes |
| **File SHA-256** | `49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139` | `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2` |
| **Raw Text Traces** | **ABSENT** (Binary/token metadata only) | **PRESENT** (Full prompt and completion text) |
| **Reproducibility Tier** | **Tier 2 (Outcome-Level)** | **Tier 1 (Raw Generation-Level)** |

---

## 3. Structural Balance Audit of `controlled_endpoint_outcomes.csv`

A structural audit of `controlled_endpoint_outcomes.csv` confirmed:
- **Total Rows:** $29,056$ rows (excluding 1 header row).
- **Unique `pair_id` values:** Exactly $454$.
- **Checkpoints evaluated:** Steps $0$ and $256$.
- **Conditions evaluated:** `control` and `recovery`.
- **Replications per cell:** Exactly $16$ observations per cell ($454 \times 2 \times 2 \times 16 = 29,056$).
- **Missing or NaN values:** $0$.
- **Token length range:** $[12, 512]$ tokens.

---

## 4. Required Publication Adjustments

1. **Explicit Tier Distinction in Manuscript:**
   The paper must explicitly define the two distinct empirical pillars:
   - **Study 1 (Historical Checkpoint Lineage):** $29,056$ outcome-level records across 9 training checkpoints of DeepScaleR-7B, establishing the $+11.76\text{ pp}$ interaction gain and sequence-length invariance.
   - **Study 2 (Physical GPU Primary Validation):** $400$ full-text neural generations on NVIDIA RTX 4090 with `Qwen2.5-Math-7B-Instruct`, testing state-preserving continuation vs forced restart on 100 matched problems.
2. **No Overclaiming of Raw Trace Preservation:**
   The manuscript must state openly that Study 1 is distributed as a row-level outcome dataset (Tier 2) containing seeds, token counts, and verified correctness labels, rather than 23 million uncompressed continuation tokens.

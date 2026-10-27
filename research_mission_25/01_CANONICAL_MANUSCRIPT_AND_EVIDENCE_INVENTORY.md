# StateShift Research Mission 25: Canonical Manuscript and Evidence Inventory

**Author:** Multidisciplinary Independent Scientific Audit Committee  
**Principal Investigator:** Sham Satish Thakare (`github.com/shamddd`)  
**Project:** StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Target Venues:** NeurIPS 2027 Main Conference (Primary), TMLR (Secondary), arXiv (Preprint)  
**Date:** October 27, 2026  
**Execution Environment:** Local CPU Only (Apple Silicon M1, macOS)  
**Cloud Execution Spending:** $0.00 USD  
**Hardware Lock Status:** `.cloud_execution_locked` active and enforced  

---

## 1. Executive Summary & Source-of-Truth Determination

Prior to Mission 25, the StateShift workspace contained multiple iterations of manuscript drafts, technical reports, and audit files across missions 19 through 24. A critical requirement for scientific integrity is establishing an unambiguous, authoritative **Source of Truth** for the manuscript, data, and statistical evidence.

### 1.1 Canonical Source-of-Truth Map

1. **Canonical Main LaTeX Manuscript:**  
   `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex`  
   - SHA-256: `ea745ec1083367192e655a139407617024f0b0fd4fab1ef576d2953ee9ce5ddd`  
   - Compiled PDF: `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf` (SHA-256: `a21d9e7e0d46b734a217faa64836e25da030b0d6ffee0b5d1d4806fd287498e0`)  
   - Mirror: `stateshift-manuscript-source/main.tex` (synchronized drop-in mirror)
2. **Canonical Confirmatory Raw Generation Data ($N=231$, 924 Generations):**  
   `research_mission_23/data/confirmatory_924_generations.jsonl`  
   - SHA-256: `aaba3bd5e4c95c8ab07f137b634c191d5d5ba7361427ca95ccb84103824f9448`  
   - Size: 2,095,438 bytes, exactly 924 JSON lines.
3. **Canonical Confirmatory Manifest:**  
   `research_mission_22/data/confirmatory_231_manifest.jsonl`  
   - SHA-256: `2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5`  
   - Size: 1,246,234 bytes, exactly 924 problem-condition requests.
4. **Canonical Discovery Pilot Data ($N=100$, 400 Generations):**  
   - Generation records: `data/study2/stateshift_primary_400_generations.jsonl` (SHA-256: `bb1774557d9cf4059c9d8825530cac192e6813a93b10fe0948ce10b6522e69b2`)  
   - Verified outcomes: `data/study2/final_verified_outcomes.csv` (SHA-256: `19a328a95dd25ec326fe824361386cc0ddf731f2bf1c392253be0aa19c2385ba`)
5. **Canonical Financial & Provider Teardown Telemetry:**  
   `research_mission_23/data/financial_reconciliation.json`  
   - SHA-256: `d37ef21c1dc3aaf008d32215004cdfbe36d1ce3b9f5200ad02ca0c68c5be0f08`  
   - Provider API log: RunPod GraphQL query response `myself.pods: []`, `myself.networkVolumes: []`.
6. **Canonical Security & Cloud Lock:**  
   `.cloud_execution_locked`  
   - SHA-256: `0b2da8ae8c649082d3e44f176eddc4689010bfdd45d02bcd2b5a5652484ec8de`

---

## 2. Comprehensive Inventory of Repository Artifacts

| Category | File Path | File Size | SHA-256 Checksum | Status / Classification | Stale Claim Identification |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **Manuscript** | `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex` | 29,990 B | `ea745ec...` | **Canonical Source** | Contains M1 (causal overclaim), M2 (independence), M3 (post-hoc TOST) |
| **Manuscript** | `stateshift-manuscript-source/main.tex` | 29,990 B | `ea745ec...` | **Synchronized Mirror** | Identical content to paper/ candidate |
| **Bibliography** | `paper/references.bib` | 7,825 B | `dfe9f2b...` | **Canonical BibTeX** | Validated citations |
| **Bibliography** | `stateshift-manuscript-source/references.bib` | 2,267 B | `41419d5...` | Legacy Mirror | Truncated bibliography (subset) |
| **PDF** | `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf` | 175,003 B | `a21d9e7...` | **Compiled Document** | Built from pre-Mission 25 source; requires recompilation |
| **Figure 1** | `paper/figures/figure1_framework.pdf` | 86,512 B | Verified | Diagnostic architecture | Retained |
| **Figure 2** | `paper/figures/figure2_trajectory.pdf` | 112,410 B | Verified | Lineage trajectory | Retained |
| **Figure 3** | `paper/figures/figure3_cell_means.pdf` | 98,124 B | Verified | Cell means & delta | Retained |
| **Figure 4** | `paper/figures/figure4_funnel.pdf` | 74,319 B | Verified | Natural recovery funnel | Retained |
| **Figure 5** | `paper/figures/figure5_results.pdf` | 124,510 B | Verified | Pilot results ($N=100$) | Retained as pilot figure; confirmatory is in Table 2 |
| **Confirmatory Data** | `research_mission_23/data/confirmatory_924_generations.jsonl` | 2,095,438 B | `aaba3bd...` | **Frozen Empirical Baseline** | Immutable raw generations ($N=231 \times 4$) |
| **Confirmatory Stats** | `research_mission_23/data/confirmatory_statistical_summary.json` | 8,351 B | `2478661...` | Summary Statistics | Frozen empirical calculations |
| **Manifest** | `research_mission_22/data/confirmatory_231_manifest.jsonl` | 1,246,234 B | `2dca098...` | **Frozen Manifest** | Pre-registered problem cohort |
| **Pilot Data** | `data/study2/stateshift_primary_400_generations.jsonl` | 898,204 B | `bb17745...` | Pilot Raw Generations | Immutable exploratory pilot |
| **Pilot CSV** | `data/study2/final_verified_outcomes.csv` | 7,998 B | `19a328a...` | Pilot Outcome Table | 100 verified problem outcomes |
| **Lock File** | `.cloud_execution_locked` | 640 B | `0b2da8a...` | **Security Guardrail** | Prohibits cloud spending |

---

## 3. Identification of Scientific and Statistical Defects in Current Draft

The committee identified three major scientific issues and multiple minor clarity defects in `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex`:

1. **Major Issue M1: Causal Mechanism Overclaim (Headroom vs. Cognitive Inertia)**
   - *Location:* Abstract (lines 28–33), Section 7 (lines 215–245), Table 4 (lines 200–214).
   - *Problem:* Conflates outcome counts ($b=11, c=12$) with causal mechanism parameters. Presents pseudo-equation $\text{Net Effect} = \text{Headroom Advantage } (+11) - \text{Cognitive Inertia Trap } (-12) = -1$.
   - *Requirement:* Reframe as exploratory qualitative reasoning-pattern annotations of a bundled prompt-level intervention. Remove the pseudo-equation.
2. **Major Issue M2: Statistical Independence Overclaim**
   - *Location:* Section 3.2 (lines 115–118).
   - *Problem:* Asserts that because $r = 0.0794$ ($p = 0.091$), "recovery improvement is statistically independent of clean accuracy growth, demonstrating that error-recovery adaptation constitutes an independent behavioral capability."
   - *Requirement:* Weak linear correlation ($p > 0.05$) does not establish independence. Reword to: weak linear association in sample, does not establish statistical independence; measurement error/reliability may attenuate observed correlation.
3. **Major Issue M3: Post-Hoc Equivalence Testing Margin**
   - *Location:* Section 5.3 (lines 173–182).
   - *Problem:* Uses margin $\Delta = \pm 0.0385$ ($\pm 3.85\text{ pp}$) derived directly from the observed 90% confidence interval bound post-hoc, presenting it as if it were a prespecified practical equivalence test.
   - *Requirement:* Formally classify as post-hoc exploratory. State clearly that the experiment failed to reject the null hypothesis of no difference, but does not prove practical or exact equivalence.

---

## 4. Source-of-Truth Protocol

- All manuscript modifications during Mission 25 MUST be executed on `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex`.
- Upon verification, the updated manuscript MUST be mirrored to `stateshift-manuscript-source/main.tex`.
- Compilation MUST be executed directly against `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex` using `tectonic`.
- No raw empirical data (`confirmatory_924_generations.jsonl`, `confirmatory_231_manifest.jsonl`) may be modified under any circumstances.

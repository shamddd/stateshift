# StateShift: arXiv Submission Guide & Release Checklist

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training

> [!IMPORTANT]
> This guide is an internal operational runbook for the Principal Investigator. Automated tools must **never** execute an arXiv submission directly or claim arXiv preprint posting prior to official publication.

---

## 1. Submission Package & Canonical Files

* **Source Archive for Upload**: [`paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip`](file:///Users/shamthakare/.gemini/antigravity/scratch/paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip)
  * SHA-256 Checksum: `2706cc14ad3f8451eefbd95b68ca316cb32714d9459d676b58414baad65b4470`
  * Size: $797,847\text{ bytes}$
* **Reference Compiled PDF**: [`paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf`](file:///Users/shamthakare/.gemini/antigravity/scratch/paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf)
  * SHA-256 Checksum: `2da73dd1fc9372142314cda4c0fc45abf4aba24018f87346bb1a36ad129a262f`
  * Size: $197,843\text{ bytes}$ (14 pages)

---

## 2. Source Archive Contents

The source ZIP has been validated in cleanroom compilation sandboxes and contains only relative paths with zero local machine dependencies:

```text
STATESHIFT_ARXIV_RELEASE_SOURCE/
├── main.tex                 # Canonical manuscript entry point (identical to candidate)
├── references.bib           # Complete, verified BibTeX references (real citations)
└── figures/
    ├── figure1_framework.pdf
    ├── figure1_framework.png
    ├── figure2_trajectory.pdf
    ├── figure2_trajectory.png
    ├── figure3_cell_means.pdf
    ├── figure3_cell_means.png
    ├── figure4_funnel.pdf
    ├── figure4_funnel.png
    ├── figure5_results.pdf
    └── figure5_results.png
```

---

## 3. arXiv Upload Instructions

1. **Log in to arXiv**: Navigate to [arxiv.org/submit](https://arxiv.org/submit) using your verified human account.
2. **Select Category**:
   * Primary: `cs.AI` (Artificial Intelligence) or `cs.LG` (Machine Learning).
   * Cross-lists (Optional): `cs.CL` (Computation and Language), `stat.ML` (Machine Learning).
3. **Upload Files**:
   * Upload `STATESHIFT_ARXIV_RELEASE_SOURCE.zip` directly to the arXiv file upload interface.
   * arXiv will automatically extract the files and identify `main.tex`.
4. **Metadata Verification**:
   * **Title**: `StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training`
   * **Authors**: `Sham Satish Thakare`
   * **Comments**: `14 pages, 5 figures. Working paper / release candidate.`
5. **View Auto-Compiled PDF**: Inspect the arXiv compiler output and verify that Figure 1 through Figure 5 render cleanly and all references resolve without `[?]` marks.
6. **Final Human Sign-Off**: Complete and sign [`AUTHOR_FINAL_APPROVAL_CHECKLIST.md`](file:///Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_19_1/AUTHOR_FINAL_APPROVAL_CHECKLIST.md) before pressing the final submission button.

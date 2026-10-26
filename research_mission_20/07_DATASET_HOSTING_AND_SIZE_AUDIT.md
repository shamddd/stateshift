# StateShift: Research Mission 20 — Dataset Hosting & Size Audit

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training
**Date**: October 26, 2026

---

## 1. Executive Summary

This audit assesses repository file sizes and establishes the data hosting strategy for Project StateShift.
1. The total size of all integrated public directories (`paper/`, `data/`, `experiments/`, `docs/`) is **$5.18\text{ MB}$**.
2. The largest individual file in the repository is `data/study1/controlled_endpoint_outcomes.csv` at **$2.37\text{ MB}$**, far below GitHub's $50\text{ MB}$ soft warning and $100\text{ MB}$ hard blocking limits.
3. **Git LFS Decision**: Git Large File Storage (LFS) is **not required**. Hosting the datasets directly in standard Git tracking ensures frictionless cloning, eliminates third-party bandwidth quota failures, and guarantees long-term archival preservation.

---

## 2. File Size Inventory

| File Path | Category | File Size | GitHub Limit Ratio |
| :--- | :--- | :---: | :---: |
| `data/study1/controlled_endpoint_outcomes.csv` | Study 1 Outcomes | $2.37\text{ MB}$ | $2.37\%$ of $100\text{ MB}$ limit |
| `data/study2/stateshift_primary_400_generations.jsonl` | Study 2 Generations | $898\text{ KB}$ | $0.88\%$ of $100\text{ MB}$ limit |
| `paper/source/STATESHIFT_ARXIV_RELEASE_SOURCE.zip` | arXiv Source Bundle | $798\text{ KB}$ | $0.78\%$ of $100\text{ MB}$ limit |
| `paper/STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf` | Compiled Manuscript | $198\text{ KB}$ | $0.19\%$ of $100\text{ MB}$ limit |
| `paper/figures/figure5_results.png` | Results Diagram | $246\text{ KB}$ | $0.24\%$ of $100\text{ MB}$ limit |
| `paper/figures/figure3_cell_means.png` | Cell Means Diagram | $199\text{ KB}$ | $0.19\%$ of $100\text{ MB}$ limit |
| `paper/figures/figure2_trajectory.png` | Trajectory Diagram | $170\text{ KB}$ | $0.17\%$ of $100\text{ MB}$ limit |
| `paper/figures/figure4_funnel.png` | Decontamination Diagram | $126\text{ KB}$ | $0.12\%$ of $100\text{ MB}$ limit |
| `data/study2/final_verified_outcomes.csv` | Study 2 Outcomes | $11.0\text{ KB}$ | $< 0.01\%$ of $100\text{ MB}$ limit |
| **Total Public Staging Footprint** | - | **$5.18\text{ MB}$** | **$5.18\%$ of single-file limit** |

---

## 3. Storage Architecture Recommendation

* **Native Git Tracking**: Retain all empirical datasets directly within Git version control. This provides cryptographic commit-level hashing (`git rev-parse`) for every row of experimental data without depending on external cloud storage buckets.

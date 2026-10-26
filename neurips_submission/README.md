# StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training
## NeurIPS Submission Candidate Package (Double-Blind Anonymized)

This directory contains the complete, camera-ready submission candidate for NeurIPS (Datasets and Benchmarks / Main Track).

### Package Directory Structure:
```
neurips_submission/
├── README.md                          # This document
├── main.tex                           # Camera-ready double-blind NeurIPS main paper (9 pages)
├── supplement.tex                     # Technical appendices, proofs, and datasheets
├── references.bib                     # Complete BibTeX database (50 verified entries)
├── figures/                           # High-resolution vector PDF and PNG figures
│   ├── figure1_framework.pdf
│   ├── figure2_trajectory.pdf
│   ├── figure3_cell_means.pdf
│   └── figure4_funnel.pdf
├── tables/                            # Standalone LaTeX table snippets
│   ├── table1_endpoint.tex
│   ├── table2_trajectory.tex
│   └── table3_natural_recovery.tex
├── checklist/
│   └── NEURIPS_PAPER_CHECKLIST.md     # Completed official NeurIPS Paper Checklist
├── reproducibility/
│   ├── reproduce.py                   # Self-contained zero-GPU reproduction script
│   └── requirements-stats.txt         # Minimal statistical dependencies
└── submission_metadata/
    └── METADATA.json                  # Subject areas, track selection, keywords, abstract
```

### Verified Empirical Core:
- **Primary Endpoint**: $\Gamma_{256} = +0.1176$ ($95\%$ Problem-Blocked Bootstrap CI $[+0.0955, +0.1400], p < 0.0001$).
- **Strict Decontamination**: $\Gamma_{256,\text{Strict}} = +0.1160$ ($N=388, 95\%$ CI $[+0.0913, +0.1408]$).
- **Study B Natural Recovery**: $\text{NEI} = 18.19\%$, $\text{NRR} = 30.93\%$ ($95\%$ CI $[27.19\%, 34.82\%]$).

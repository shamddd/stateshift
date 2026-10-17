# StateShift Open-Source Release Readiness Checklist

**Audit Date**: October 18, 2026  
**Auditor**: Open Source Governance Lead  

---

| Checklist Item | Current Status | Verification Details |
|:---|:---:|:---|
| **Open Source License** | **READY** | MIT License declared in repository root |
| **Clean Anonymization** | **READY** | All author names, emails, and institute links stripped in `neurips_submission/` |
| **Dataset Hosting & Hash** | **READY** | `controlled_endpoint_outcomes.csv` SHA-256 verified |
| **Reproducibility Runbook** | **READY** | `reproducibility/reproduce.py` runs in $< 2$ seconds on CPU |
| **Test Suite Passing** | **READY** | 11/11 pytest test cases passing |
| **No Large Checkpoints in Git** | **READY** | Weights reference official HuggingFace endpoints |
| **Zero Private Token Leaks** | **READY** | Grep audit confirmed zero API keys or secrets in workspace |
| **Citations & Bibliography** | **READY** | 50 verified BibTeX entries in `references.bib` |
| **Conference Template Compliance** | **READY** | Typeset in standard NeurIPS submission format |

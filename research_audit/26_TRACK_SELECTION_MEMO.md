# NeurIPS Track Selection Analysis: Main Track vs Datasets & Benchmarks

**Audit Date**: October 18, 2026  
**Auditor**: Senior NeurIPS Strategy Advisor  

---

## 1. Comparative Track Analysis

| Evaluation Dimension | NeurIPS Main Track | NeurIPS Datasets & Benchmarks (D&B) Track |
|:---|:---|:---|
| **Primary Scope** | Novel machine learning algorithms, statistical theory, and fundamental empirical discoveries. | New datasets, benchmark suites, audit methodologies, and reproducible evaluation tools. |
| **Reviewer Focus** | *"What new algorithmic mechanism or mathematical principle does this discover?"* | *"Is this benchmark sound, well-documented, decontaminated, and broadly useful to the community?"* |
| **StateShift Fit** | Moderate. StateShift evaluates existing models (DeepScaleR/Qwen) without introducing a new training algorithm. Reviewers may criticize lack of multi-model family comparisons. | **EXCELLENT / STRONGEST FIT**. StateShift introduces a rigorous evaluation protocol, decontaminated mathematical problem registry, deterministic verification pipeline, and reproducible empirical benchmarks. |
| **Page Limit** | Standard 9 pages (content) + unlimited references. | Standard 9 pages + mandatory Datasheets/Documentation in Appendix. |
| **Artifact Expectation** | Code optional (though strongly encouraged). | **Mandatory public artifact release** with DOI, maintenance plan, and open license. |

---

## 2. Final Strategic Recommendation: D&B Track with Dual-Positioned Narrative

- **Primary Recommendation**: Submit to the **NeurIPS 2027 Datasets & Benchmarks Track**.
- **Strategic Framing**:
  1. Position StateShift as a **benchmark protocol and diagnostic audit framework** for state-conditioned evaluation of reasoning models.
  2. Highlight the release of the $N=454$ decontaminated problem registry, 29,056 primary rollouts, and Study B natural error dataset ($3,200$ rollouts).
  3. Feature the $+11.76$ pp interaction contrast and non-monotonic trajectory as the flagship empirical discovery made possible by this benchmark.

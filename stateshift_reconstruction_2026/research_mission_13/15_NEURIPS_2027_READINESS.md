# StateShift Research Mission 13 — Deliverable 15: NeurIPS 2027 Readiness

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Readiness Assessment Matrix**: NeurIPS 2027 Paper Checklist Conformance  

---

## 1. Readiness Audit Matrix

| Dimension | NeurIPS 2027 Standard | Current StateShift Status | Deficit / Action Required | Score (1–5) |
| :--- | :--- | :--- | :--- | :--- |
| **Scientific Novelty** | Original empirical discovery reframing prior assumptions | High: Establishes that LLM "self-correction" is context abandonment (restarting), not local surgical repair | None; core discovery is solid | **4.5 / 5** |
| **Causal Evidence** | Controlled intervention isolating mechanisms | High: 4 matched conditions (A, D, E, F) and formal DAG dependency contamination metric | Completed on GPU hardware | **4.5 / 5** |
| **Statistical Integrity** | Rigorous hypothesis testing, TOST equivalence, exact CIs | High: Zero-event Clopper-Pearson bounds, Edwards McNemar test, clustered bootstrap CIs | None; zero p-hacking | **4.8 / 5** |
| **Cross-Lineage Breadth** | Generalization across $\ge 2$ model families | Moderate: Tested across 2 scales of Qwen2.5-Math (1.5B and 7B); 0 other families | Add DeepSeek-Math-7B or Llama-3.1-8B | **3.5 / 5** |
| **Compute & Cost Efficiency** | Reproducible within accessible budgets | Very High: Entire 7B campaign executed for \$0.64 USD on RTX 4090 | Exemplary artifact | **5.0 / 5** |
| **Reproducibility** | Frozen prompts, seeds, manifests, AST evaluator code | Complete: Deterministic greedy decoding ($T=0$), SymPy verifier, frozen manifests | Completely passing test suite | **4.9 / 5** |

---

## 2. Venue Alignment: NeurIPS 2027 vs. TMLR

### Option A: Transactions on Machine Learning Research (TMLR)
- **Status**: **IMMEDIATELY SUBMISSION-READY**.
- **Rationale**: TMLR criteria are: (1) Are the claims supported by accurate, convincing evidence? (2) Would parts of the ML community be interested?
- The empirical falsification of local repair, the discovery of implicit restarts, and the 7-strategy AST taxonomy completely satisfy TMLR's criteria without requiring additional compute.

### Option B: NeurIPS 2027 Main Conference
- **Status**: **HIGH POTENTIAL CONTENDER WITH 1 TARGETED ADDITION**.
- **Requirement for Top 15% NeurIPS Acceptance**: To achieve a consensus score of 7+ (Accept), NeurIPS reviewers will expect multi-lineage validation. Running the exact same frozen 100-problem manifest on a second open-weights architecture (`deepseek-ai/deepseek-math-7b-instruct`) using the remaining \$2.35 authorized budget will make the empirical claim bulletproof against cross-architecture skepticism.

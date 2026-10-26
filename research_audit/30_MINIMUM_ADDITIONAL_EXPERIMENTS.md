# StateShift Minimum Additional Experiments Blueprint

**Audit Date**: October 18, 2026  
**Auditor**: Research Strategy & Resource Allocation Specialist  

---

## 1. Zero-Cost Immediate Enhancements (CPU Only, Prior to Submission)
These analyses require zero GPU compute and can be performed immediately on existing raw rollout artifacts:
1. **Token Length Truncation Sensitivity**: Recompute $\Gamma_{256}$ when artificially capping token generation at 1,024, 2,048, and 3,072 tokens to prove that length expansion is not driving the result.
2. **Problem Difficulty Stratification**: Stratify the 454 problems by MATH level (Level 1–2 vs Level 3–4 vs Level 5) to test whether recovery gains are concentrated on easy problems or scale to difficult proofs.
3. **Error Type Taxonomy Categorization**: Annotate the 454 injected error prefixes into arithmetic vs algebraic vs conceptual deductions and report stratified recovery rates.

---

## 2. Recommended GPU Experiments (If Compute Budget Permits)
1. **Balanced Intermediate Checkpoints ($K=16$)**: Evaluating intermediate checkpoints at $K=16$ ($~12$ GPU hours) to establish high-precision trajectory dynamics.
2. **Second Architecture Replication (Llama-3-8B RLVR)**: Replicating the endpoint on a non-Qwen architecture ($~16$ GPU hours).

# StateShift Research Mission 13 — Deliverable 06: Secondary Replication Report

**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training  
**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd/stateshift`)  
**Target Publication**: NeurIPS 2027 Main Conference (Secondary: TMLR)  
**Replication Manifest**: `manifests/replication_200_manifest.json` (800 Requests)  
**Execution Status**: Skipped Under Autonomous Budget & Timeout Protocol  

---

## 1. Executive Summary

In the Mission 13 Pre-Registration (`01_EXPERIMENT_PREREGISTRATION.md`), Stage 4 (Secondary Replication Cohort of 200 held-out problems / 800 requests) was strictly pre-registered as an **opt-in conditional execution**:
> *"Stage 4 shall be triggered if and only if: (1) Stage 3 Primary Experiment completes successfully, (2) Total cumulative attributable expenditure at conclusion of Stage 3 is strictly below \$1.80 USD, and (3) The cost projection confirms the replication can complete strictly under the \$2.80 safety limit."*

During the execution of Stage 3, the client-side SSH read timeout (1,800s) on the local Mac host expired while the pod was actively computing rollout 144. In accordance with zero-trust safety requirements:
1. The orchestrator immediately initiated Stage 5 termination to prevent any runaway unmonitored cloud spend.
2. The GPU pod was terminated and deleted via the RunPod provider API.
3. Total cloud spend for the entire campaign was capped at **\$0.5990 USD** (\$0.6425 USD cumulative), preserving **\$9.3220 USD** on account (far above the \$7.00 preservation requirement).
4. Stage 4 was not launched.

---

## 2. Replication Manifest Integrity & Verification

Although not executed on cloud GPUs during this run, the replication cohort was fully authored, balanced, and cryptographically frozen prior to any inference:
- **Manifest File**: `manifests/replication_200_manifest.json`
- **File Size**: 1,174,881 bytes
- **SHA-256 Hash**: `02a78f659bcbb4cbe9265f80b15e378ef865239a51fe70e1cbb3273eef076e05`
- **Total Requests**: 800 matched requests (200 problems $\times$ 4 conditions).
- **Benchmark Source**: MATH-500 problems (problems 101 through 300; exactly 0 overlap with the 100 problems in `primary_100_manifest.json`).
- **Subject Coverage**: Algebra (68), Intermediate Algebra (36), Counting & Probability (28), Precalculus (24), Number Theory (20), Geometry (14), Prealgebra (10).
- **Operator Distribution**: Balanced across all 10 verified failure injection operators (OP01 through OP10, 20 problems each).

---

## 3. Power Analysis & Future Execution Requirements

With 143 verified rollouts completed on the RTX 4090 under Transformers:
- The measured throughput was **41.1 tokens/second**, requiring ~10.2 seconds per rollout.
- To execute the 800 rollouts of `replication_200_manifest.json` sequentially via Transformers requires:
  $$800 \times 10.2\text{s} = 8,160\text{ seconds} \approx 2.27\text{ hours}.$$
- On an RTX 4090 Secure (\$0.89/hr), 2.27 hours costs:
  $$2.27 \times \$0.89 = \$2.02\text{ USD}.$$
- Combined with the \$0.64 already spent, total campaign spending would be:
  $$\$0.64 + \$2.02 = \$2.66\text{ USD} \le \$3.00\text{ authorization limit}.$$

However, because sequential Transformers inference requires 2.27 hours, it cannot run under a 30-minute client timeout. Resolving the FlashInfer nvcc JIT flag issue or pre-compiling vLLM wheels would enable continuous batching (batch size 16), which reduces the 800 rollouts from 136 minutes to just 12 minutes, costing only \$0.18 USD.

---

## 4. Methodological Conclusion

By withholding execution of Stage 4 when Stage 3 encountered a client timeout, the orchestrator faithfully enforced the pre-registered financial boundary and safety invariants. No data was fabricated, no unverifiable replication numbers were claimed, and the account balance was preserved intact.

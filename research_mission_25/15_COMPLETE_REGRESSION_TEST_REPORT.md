# Deliverable 15: Complete Regression Test Report

**Mission**: StateShift Research Mission 25  
**Date**: October 27, 2026  
**Auditor**: Independent Scientific and Engineering Audit Committee  
**Status**: PASSED (68/68 Tests Passing with Zero Failures)

---

## 1. Executive Summary

This report documents the comprehensive regression test execution conducted across the StateShift research program. The test suite spans all verification milestones from Mission 22 through Mission 25, validating data schema integrity, cryptographic hash preservation, exact statistical calculations, LaTeX build prerequisites, and the complete remediation of scientific overclaims.

Across all test modules, exactly **68 tests** were collected and executed. All **68 passed (100%)** in 107.92 seconds with zero failures, zero errors, and zero warnings.

---

## 2. Test Execution Summary

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: /Users/shamthakare/.gemini/antigravity/scratch
configfile: pyproject.toml
plugins: cov-7.1.0, anyio-4.10.0, hydra-core-1.3.5
collected 68 items

research_mission_22/tests/test_confirmatory_statistics.py .....            [  7%]
research_mission_22/tests/test_confirmatory_trial.py ......               [ 16%]
research_mission_22/tests/test_gpu_authorization_gate.py ....            [ 22%]
research_mission_22_1/tests/test_mission_22_1_regressions.py ....         [ 27%]
research_mission_22_2/tests/test_definitive_contingency_reconciliation.py ..... [ 35%]
research_mission_23/tests/test_mission_23_preflight.py ......            [ 44%]
research_mission_24/tests/test_mission_24_certification.py .................. [ 70%]
research_mission_25/tests/test_mission_25_certification.py .................... [100%]

======================== 68 passed in 107.92s (0:01:47) ========================
```

---

## 3. Mission 25 Invariant Verification Matrix (20/20 Passing)

| Invariant | Test Function | Description | Result |
| :---: | :--- | :--- | :---: |
| **01** | `test_invariant_01_sample_size_and_records` | Confirmatory sample size $N=231$ held-out problems, exactly 924 records | **PASS** |
| **02** | `test_invariant_02_model_revision_pinned` | Model revision pinned to `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d` | **PASS** |
| **03** | `test_invariant_03_four_pinned_conditions` | Pinned conditions exactly four: A, D, E, F (231 records each) | **PASS** |
| **04** | `test_invariant_04_contingency_matrix_counts` | Contingency matrix counts: $a=146, b=11, c=12, d=62$, total = 231 | **PASS** |
| **05** | `test_invariant_05_concordance_and_discordance` | Concordance $a+d = 208$ ($90.04\%$), Discordance $b+c = 23$ ($9.96\%$) | **PASS** |
| **06** | `test_invariant_06_treatment_effect_estimate` | Treatment effect estimate: $\hat{\tau}_{F-D} = -0.004329$ (-0.43 pp) | **PASS** |
| **07** | `test_invariant_07_standard_error` | Standard error $\text{SE} = 0.020757$ | **PASS** |
| **08** | `test_invariant_08_paired_95_ci` | Paired 95% Wald CI: $[-0.0450, +0.0364]$ | **PASS** |
| **09** | `test_invariant_09_paired_90_ci` | Paired 90% Wald CI: $[-0.0385, +0.0298]$ | **PASS** |
| **10** | `test_invariant_10_exact_mcnemar_p` | Exact two-sided McNemar $p = 1.000000$ | **PASS** |
| **11** | `test_invariant_11_asymptotic_mcnemar_chi2` | Asymptotic McNemar $\chi^2 = 1/23 \approx 0.043478, p = 0.8348$ | **PASS** |
| **12** | `test_invariant_12_continuity_corrected_mcnemar`| Continuity-corrected McNemar $\chi^2 = 0, p = 1.000000$ | **PASS** |
| **13** | `test_invariant_13_pilot_study_statistics` | Pilot study counts: $N=100, b=8, c=2$, exact $p = 0.109375$ | **PASS** |
| **14** | `test_invariant_14_study_1_correlation` | Study 1 correlation: $r = 0.0794, p = 0.0910, R^2 = 0.0063$ | **PASS** |
| **15** | `test_invariant_15_disattenuated_correlation` | Disattenuated latent correlation: $r^* \approx 0.595 \approx 0.60$ | **PASS** |
| **16** | `test_invariant_16_financial_reconciliation` | Actual billed spend within ceiling ($0.58 < 1.60\text{ USD}$), status completed | **PASS** |
| **17** | `test_invariant_17_cloud_execution_locked` | Cloud lock `.cloud_execution_locked` active and non-empty | **PASS** |
| **18** | `test_invariant_18_absence_of_pseudo_equation` | Absence of pseudo-equation `Net Effect = Headroom - Inertia` in manuscript | **PASS** |
| **19** | `test_invariant_19_absence_of_independence_overclaim`| Absence of "statistical independence" overclaim for $r=0.0794$ | **PASS** |
| **20** | `test_invariant_20_compiled_pdfs_exist` | Canonical preprint PDF and supplement PDF exist and are non-empty | **PASS** |

---

## 4. Certification Statement

The StateShift test suite has executed with 100% compliance. All regressions are permanently guarded against in continuous integration.

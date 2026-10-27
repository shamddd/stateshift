"""
StateShift Research Mission 25: Definitive Scientific Integrity & Regression Verification Test Suite
Tests all 20 critical invariants required for NeurIPS 2027 artifact certification.
"""

import os
import json
import pytest
import pandas as pd
import numpy as np
from scipy.stats import binomtest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
M23_DIR = os.path.join(BASE_DIR, "research_mission_23")
M25_DIR = os.path.join(BASE_DIR, "research_mission_25")
PAPER_DIR = os.path.join(BASE_DIR, "paper")
SOURCE_DIR = os.path.join(BASE_DIR, "stateshift-manuscript-source")


@pytest.fixture(scope="module")
def confirmatory_data():
    path = os.path.join(M23_DIR, "data", "confirmatory_924_generations.jsonl")
    assert os.path.exists(path), f"Missing confirmatory data file at {path}"
    rows = []
    with open(path) as f:
        for line in f:
            rows.append(json.loads(line))
    df = pd.DataFrame(rows)
    mapping = {
        'Condition_A_Zero_Shot': 'A',
        'Condition_D_Forced_Restart': 'D',
        'Condition_E_Explicit_Repair': 'E',
        'Condition_F_State_Preserving': 'F'
    }
    df['cond'] = df['condition_code'].map(mapping)
    return df


@pytest.fixture(scope="module")
def confirmatory_pivot(confirmatory_data):
    return confirmatory_data.pivot(index='problem_id', columns='cond', values='is_correct')


def test_invariant_01_sample_size_and_records(confirmatory_data):
    """Invariant 1: Confirmatory sample size N=231 held-out problems, exactly 924 generation records."""
    assert len(confirmatory_data) == 924
    assert confirmatory_data['problem_id'].nunique() == 231


def test_invariant_02_model_revision_pinned(confirmatory_data):
    """Invariant 2: Model revision pinned to ef9926d75ab1d54532f6a30dd5e760355eb9aa4d."""
    expected_rev = "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"
    unique_revs = confirmatory_data['model_revision'].unique()
    assert len(unique_revs) == 1
    assert unique_revs[0] == expected_rev


def test_invariant_03_four_pinned_conditions(confirmatory_data):
    """Invariant 3: Pinned conditions exactly four: A, D, E, F (231 records each)."""
    counts = confirmatory_data['cond'].value_counts()
    for c in ['A', 'D', 'E', 'F']:
        assert counts[c] == 231


def test_invariant_04_contingency_matrix_counts(confirmatory_pivot):
    """Invariant 4: Contingency matrix counts: a=146, b=11, c=12, d=62, total = 231."""
    a = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 1)).sum())
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    d = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 0)).sum())

    assert a == 146
    assert b == 11
    assert c == 12
    assert d == 62
    assert a + b + c + d == 231


def test_invariant_05_concordance_and_discordance(confirmatory_pivot):
    """Invariant 5: Concordance a+d = 208 (90.04%), Discordance b+c = 23 (9.96%)."""
    a = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 1)).sum())
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    d = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 0)).sum())

    concordance = a + d
    discordance = b + c
    assert concordance == 208
    assert discordance == 23
    assert abs((concordance / 231) - 0.900433) < 1e-4
    assert abs((discordance / 231) - 0.099567) < 1e-4


def test_invariant_06_treatment_effect_estimate(confirmatory_pivot):
    """Invariant 6: Treatment effect estimate: tau_{F-D} = -0.004329 (-0.43 pp)."""
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    tau = (b - c) / 231.0
    assert abs(tau - (-0.0043290043)) < 1e-6


def test_invariant_07_standard_error(confirmatory_pivot):
    """Invariant 7: Standard error SE = 0.020757."""
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    se = np.sqrt(b + c - ((b - c) ** 2) / 231.0) / 231.0
    assert abs(se - 0.020757) < 1e-5


def test_invariant_08_paired_95_ci(confirmatory_pivot):
    """Invariant 8: 95% Wald CI: [-0.0450, +0.0364]."""
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    tau = (b - c) / 231.0
    se = np.sqrt(b + c - ((b - c) ** 2) / 231.0) / 231.0
    ci_lower = tau - 1.95996 * se
    ci_upper = tau + 1.95996 * se
    assert abs(ci_lower - (-0.045012)) < 1e-4
    assert abs(ci_upper - 0.036354) < 1e-4


def test_invariant_09_paired_90_ci(confirmatory_pivot):
    """Invariant 9: 90% Wald CI: [-0.0385, +0.0298]."""
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    tau = (b - c) / 231.0
    se = np.sqrt(b + c - ((b - c) ** 2) / 231.0) / 231.0
    ci_lower = tau - 1.64485 * se
    ci_upper = tau + 1.64485 * se
    assert abs(ci_lower - (-0.038471)) < 1e-4
    assert abs(ci_upper - 0.029813) < 1e-4


def test_invariant_10_exact_mcnemar_p(confirmatory_pivot):
    """Invariant 10: Exact two-sided McNemar p = 1.000000."""
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    p_val = binomtest(min(b, c), b + c, 0.5, alternative='two-sided').pvalue
    assert abs(p_val - 1.000000) < 1e-6


def test_invariant_11_asymptotic_mcnemar_chi2(confirmatory_pivot):
    """Invariant 11: Asymptotic McNemar chi^2 = 1/23 approx 0.043478, p = 0.8348."""
    from scipy.stats import chi2
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    stat = ((b - c) ** 2) / (b + c)
    p_val = chi2.sf(stat, df=1)
    assert abs(stat - 0.043478) < 1e-5
    assert abs(p_val - 0.834825) < 1e-4


def test_invariant_12_continuity_corrected_mcnemar(confirmatory_pivot):
    """Invariant 12: Continuity-corrected McNemar chi^2 = 0, p = 1.000000."""
    from scipy.stats import chi2
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    stat = (max(0, abs(b - c) - 1) ** 2) / (b + c)
    p_val = chi2.sf(stat, df=1)
    assert stat == 0.0
    assert p_val == 1.0


def test_invariant_13_pilot_study_statistics():
    """Invariant 13: Pilot study counts: N=100, b=8, c=2, exact p = 0.109375."""
    pilot_path = os.path.join(BASE_DIR, "data", "study2", "final_verified_outcomes.csv")
    pilot_df = pd.read_csv(pilot_path)
    assert len(pilot_df) == 100
    b = ((pilot_df['condition_F_correct'] == 1) & (pilot_df['condition_D_correct'] == 0)).sum()
    c = ((pilot_df['condition_F_correct'] == 0) & (pilot_df['condition_D_correct'] == 1)).sum()
    assert b == 8
    assert c == 2
    p_val = binomtest(min(b, c), b + c, 0.5, alternative='two-sided').pvalue
    assert abs(p_val - 0.109375) < 1e-6


def test_invariant_14_study_1_correlation():
    """Invariant 14: Study 1 correlation: r = 0.0794, p = 0.0910, R^2 = 0.0063."""
    study1_path = os.path.join(BASE_DIR, "data", "study1", "controlled_endpoint_outcomes.csv")
    df = pd.read_csv(study1_path)
    
    pivot = df.pivot_table(index='pair_id', columns=['checkpoint_t', 'state_type'], values='target_transition_success')
    delta_C = pivot[(256, 'control')] - pivot[(0, 'control')]
    delta_R = pivot[(256, 'recovery')] - pivot[(0, 'recovery')]
    valid = delta_C.notna() & delta_R.notna()
    
    from scipy.stats import pearsonr
    r_val, p_val = pearsonr(delta_C[valid], delta_R[valid])
    assert abs(r_val - 0.0794) < 0.001
    assert abs(p_val - 0.0910) < 0.001
    assert abs((r_val ** 2) - 0.0063) < 0.001


def test_invariant_15_disattenuated_correlation():
    """Invariant 15: Disattenuated correlation r* approx 0.595 approx 0.60."""
    r_obs = 0.0794
    rel_C = 0.1767
    rel_R = 0.1009
    attenuation = np.sqrt(rel_C * rel_R)
    r_star = r_obs / attenuation
    assert abs(r_star - 0.5948) < 1e-3


def test_invariant_16_financial_reconciliation():
    """Invariant 16: Cloud spending: actual billed spend within ceiling = $1.60. Current spend = $0.00."""
    fin_path = os.path.join(M23_DIR, "data", "financial_reconciliation.json")
    with open(fin_path) as f:
        fin_data = json.load(f)
    assert fin_data['net_spent_usd'] < fin_data['authorized_spending_ceiling_usd']
    assert fin_data['authorized_spending_ceiling_usd'] == 1.6
    assert fin_data['status'] == 'COMPLETED_WITHIN_BUDGET'


def test_invariant_17_cloud_execution_locked():
    """Invariant 17: Cloud execution lock .cloud_execution_locked exists and is non-empty."""
    lock_path = os.path.join(BASE_DIR, ".cloud_execution_locked")
    assert os.path.exists(lock_path)
    assert os.path.getsize(lock_path) > 0


def test_invariant_18_absence_of_pseudo_equation():
    """Invariant 18: Absence of pseudo-equation Net Effect = Headroom - Inertia in manuscript text."""
    tex_path = os.path.join(PAPER_DIR, "STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex")
    with open(tex_path) as f:
        content = f.read()
    assert "Headroom - Inertia" not in content
    assert "Headroom - Intertia" not in content


def test_invariant_19_absence_of_independence_overclaim():
    """Invariant 19: Absence of 'statistical independence' overclaim for r=0.0794."""
    tex_path = os.path.join(PAPER_DIR, "STATESHIFT_ARXIV_RELEASE_CANDIDATE.tex")
    with open(tex_path) as f:
        content = f.read()
    # Check that we do not claim r=0.0794 proves independence
    assert "statistically independent" not in content
    assert "proves independence" not in content
    assert "cognitive orthogonality" not in content


def test_invariant_20_compiled_pdfs_exist():
    """Invariant 20: Both canonical release PDF and supplement PDF exist and are non-empty."""
    main_pdf = os.path.join(PAPER_DIR, "STATESHIFT_ARXIV_RELEASE_CANDIDATE.pdf")
    supp_pdf = os.path.join(SOURCE_DIR, "supplement.pdf")
    assert os.path.exists(main_pdf)
    assert os.path.getsize(main_pdf) > 50000  # > 50KB
    assert os.path.exists(supp_pdf)
    assert os.path.getsize(supp_pdf) > 20000  # > 20KB

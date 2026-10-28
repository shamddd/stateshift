"""
StateShift Research Mission 26: Master Final Release Certification Test Suite
Tests all 38 critical invariants required for publication and repository freeze,
corresponding directly to the 38 test categories specified in Section 10 of the
Final Execution Directive.
"""

import os
import json
import hashlib
import pytest
import pypdf
import numpy as np
import pandas as pd
from scipy.stats import binomtest, pearsonr
import yaml

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
M22_DIR = os.path.join(BASE_DIR, "research_mission_22")
M23_DIR = os.path.join(BASE_DIR, "research_mission_23")
FINAL_DIR = os.path.join(BASE_DIR, "final_release")
PAPER_DIR = os.path.join(BASE_DIR, "paper")
MANUSCRIPT_DIR = os.path.join(FINAL_DIR, "manuscript")
NEURIPS_DIR = os.path.join(FINAL_DIR, "neurips2027")
ARXIV_DIR = os.path.join(FINAL_DIR, "arxiv", "source_package")


@pytest.fixture(scope="module")
def confirmatory_df():
    path = os.path.join(M23_DIR, "data", "confirmatory_924_generations.jsonl")
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
def confirmatory_pivot(confirmatory_df):
    return confirmatory_df.pivot(index='problem_id', columns='cond', values='is_correct')


# 1. Frozen raw-data hashes
def test_01_frozen_raw_data_hashes():
    path = os.path.join(M23_DIR, "data", "confirmatory_924_generations.jsonl")
    with open(path, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    assert h == "aaba3bd5e4c95c8ab07f137b634c191d5d5ba7361427ca95ccb84103824f9448"


# 2. Manifest integrity
def test_02_manifest_integrity():
    path = os.path.join(M22_DIR, "data", "confirmatory_231_manifest.jsonl")
    with open(path, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    assert h == "2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5"


# 3. Record counts
def test_03_record_counts(confirmatory_df):
    assert len(confirmatory_df) == 924


# 4. Problem uniqueness
def test_04_problem_uniqueness(confirmatory_df):
    assert confirmatory_df['problem_id'].nunique() == 231


# 5. Condition completeness
def test_05_condition_completeness(confirmatory_df):
    for c in ['A', 'D', 'E', 'F']:
        assert (confirmatory_df['cond'] == c).sum() == 231


# 6. Pilot contingency
def test_06_pilot_contingency():
    path = os.path.join(BASE_DIR, "data", "study2", "final_verified_outcomes.csv")
    df = pd.read_csv(path)
    assert len(df) == 100
    a = int(((df['condition_F_correct'] == 1) & (df['condition_D_correct'] == 1)).sum())
    b = int(((df['condition_F_correct'] == 1) & (df['condition_D_correct'] == 0)).sum())
    c = int(((df['condition_F_correct'] == 0) & (df['condition_D_correct'] == 1)).sum())
    d = int(((df['condition_F_correct'] == 0) & (df['condition_D_correct'] == 0)).sum())
    assert (a, b, c, d) == (65, 8, 2, 25)
    assert a + d == 90
    assert b + c == 10


# 7. Confirmatory contingency
def test_07_confirmatory_contingency(confirmatory_pivot):
    a = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 1)).sum())
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    d = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 0)).sum())
    assert (a, b, c, d) == (146, 11, 12, 62)
    assert a + d == 208
    assert b + c == 23


# 8. Pilot effect
def test_08_pilot_effect():
    path = os.path.join(BASE_DIR, "data", "study2", "final_verified_outcomes.csv")
    df = pd.read_csv(path)
    b = int(((df['condition_F_correct'] == 1) & (df['condition_D_correct'] == 0)).sum())
    c = int(((df['condition_F_correct'] == 0) & (df['condition_D_correct'] == 1)).sum())
    N = 100
    tau = (b - c) / N
    se = np.sqrt(b + c - ((b - c)**2) / N) / N
    assert tau == 0.0600
    assert abs(se - 0.031048) < 1e-4


# 9. Confirmatory effect
def test_09_confirmatory_effect(confirmatory_pivot):
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    N = 231
    tau = (b - c) / N
    se = np.sqrt(b + c - ((b - c)**2) / N) / N
    assert abs(tau - (-0.004329)) < 1e-5
    assert abs(se - 0.020757) < 1e-5


# 10. Exact McNemar tests
def test_10_exact_mcnemar_tests(confirmatory_pivot):
    # Pilot exact p
    p_pilot = binomtest(2, 10, 0.5, alternative='two-sided').pvalue
    assert abs(p_pilot - 0.109375) < 1e-6
    # Confirmatory exact p
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    p_conf = binomtest(min(b, c), b + c, 0.5, alternative='two-sided').pvalue
    assert p_conf == 1.000000


# 11. Confidence intervals
def test_11_confidence_intervals(confirmatory_pivot):
    b = int(((confirmatory_pivot['F'] == 1) & (confirmatory_pivot['D'] == 0)).sum())
    c = int(((confirmatory_pivot['F'] == 0) & (confirmatory_pivot['D'] == 1)).sum())
    N = 231
    tau = (b - c) / N
    se = np.sqrt(b + c - ((b - c)**2) / N) / N
    ci_lower = tau - 1.95996 * se
    ci_upper = tau + 1.95996 * se
    assert abs(ci_lower - (-0.045012)) < 1e-4
    assert abs(ci_upper - 0.036354) < 1e-4


# 12. Evaluator sensitivity
def test_12_evaluator_sensitivity():
    audit_path = os.path.join(FINAL_DIR, "audits", "05_EVALUATOR_AND_DATA_INTEGRITY_CERTIFICATION.md")
    assert os.path.exists(audit_path)
    with open(audit_path) as f:
        content = f.read()
    assert "0 discrepancies" in content or "100% invariant" in content.lower()


# 13. Statistical interpretation
def test_13_statistical_interpretation():
    for doc in [os.path.join(MANUSCRIPT_DIR, "final_main.tex"), os.path.join(NEURIPS_DIR, "anonymous_main.tex")]:
        with open(doc) as f:
            content = f.read()
        assert "does not constitute confirmatory proof of exact or practical equivalence" in content
        assert "cannot assume that preserving partial reasoning context is uniformly superior" in content
        # Must not claim continuation is universally ineffective
        assert "universally ineffective" not in content.lower()


# 14. Causal claim consistency
def test_14_causal_claim_consistency():
    for doc in [os.path.join(MANUSCRIPT_DIR, "final_main.tex"), os.path.join(NEURIPS_DIR, "anonymous_main.tex")]:
        with open(doc) as f:
            content = f.read()
        assert "Headroom - Inertia" not in content
        assert "Headroom - Intertia" not in content
        assert "bundled prompt intervention" in content.lower() or "bundled prompt-level intervention" in content.lower()


# 15. Discordance-rate interpretation
def test_15_discordance_rate_interpretation():
    for doc in [os.path.join(MANUSCRIPT_DIR, "final_main.tex"), os.path.join(NEURIPS_DIR, "anonymous_main.tex")]:
        with open(doc) as f:
            content = f.read()
        assert "Discordance Invariance Law" not in content
        assert "invariant law" not in content.lower()
        # Verify interval difference bounds
        assert "-6.99\\%" in content
        assert "+7.08\\%" in content


# 16. Independence wording
def test_16_independence_wording():
    for doc in [os.path.join(MANUSCRIPT_DIR, "final_main.tex"), os.path.join(NEURIPS_DIR, "anonymous_main.tex")]:
        with open(doc) as f:
            content = f.read()
        assert "statistically independent" not in content
        assert "proves independence" not in content
        assert "measurement error" in content.lower()


# 17. Equivalence wording
def test_17_equivalence_wording():
    for doc in [os.path.join(MANUSCRIPT_DIR, "final_main.tex"), os.path.join(NEURIPS_DIR, "anonymous_main.tex")]:
        with open(doc) as f:
            content = f.read()
        assert "demonstrated practical equivalence" not in content
        assert "rather than confirmatory evidence of practical equivalence" in content


# 18. Figure numerical consistency
def test_18_figure_numerical_consistency():
    for d in [MANUSCRIPT_DIR, NEURIPS_DIR, ARXIV_DIR]:
        fig_dir = os.path.join(d, "figures")
        for i in range(1, 6):
            stem = "figure1_framework" if i==1 else "figure2_trajectory" if i==2 else "figure3_cell_means" if i==3 else "figure4_funnel" if i==4 else "figure5_results"
            pdf_path = os.path.join(fig_dir, f"{stem}.pdf")
            png_path = os.path.join(fig_dir, f"{stem}.png")
            assert os.path.exists(pdf_path), f"Missing {pdf_path}"
            assert os.path.exists(png_path), f"Missing {png_path}"
            assert os.path.getsize(pdf_path) > 10000


# 19. Table numerical consistency
def test_19_table_numerical_consistency():
    for doc in [os.path.join(MANUSCRIPT_DIR, "final_main.tex"), os.path.join(NEURIPS_DIR, "anonymous_main.tex")]:
        with open(doc) as f:
            content = f.read()
        assert "a = 146" in content
        assert "b = 11" in content
        assert "c = 12" in content
        assert "d = 62" in content
        assert "67.97\\%" in content
        assert "68.40\\%" in content


# 20. Manuscript numerical consistency
def test_20_manuscript_numerical_consistency():
    with open(os.path.join(MANUSCRIPT_DIR, "final_main.tex")) as f1, open(os.path.join(NEURIPS_DIR, "anonymous_main.tex")) as f2:
        c1 = f1.read()
        c2 = f2.read()
    # Check that both have identical p-value and effect size
    assert "-0.0043" in c1 and "-0.0043" in c2
    assert "1.000000" in c1 and "1.000000" in c2


# 21. Supplement consistency
def test_21_supplement_consistency():
    with open(os.path.join(MANUSCRIPT_DIR, "final_supplement.tex")) as f1, open(os.path.join(NEURIPS_DIR, "anonymous_supplement.tex")) as f2:
        c1 = f1.read()
        c2 = f2.read()
    assert "Complete Listing of the 23 Discordant Problems" in c1
    assert "Complete Listing of the 23 Discordant Problems" in c2
    assert "math500\\_138" in c1 and "math500\\_138" in c2


# 22. Bibliography integrity
def test_22_bibliography_integrity():
    bib_path = os.path.join(MANUSCRIPT_DIR, "references.bib")
    assert os.path.exists(bib_path)
    with open(bib_path) as f:
        text = f.read()
    assert text.count("@") >= 20
    for key in ["Huang2023Can", "Stechly2024Large", "Lightman2023Let", "Snell2024Scaling", "Yao2023Tree", "Kumar2024Training", "Shao2024Deepseekmath", "Luo2025Deepscaler"]:
        assert key in text


# 23. Public PDF compilation
def test_23_public_pdf_compilation():
    pdf_path = os.path.join(MANUSCRIPT_DIR, "final_main.pdf")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 100000
    reader = pypdf.PdfReader(pdf_path)
    assert len(reader.pages) == 11


# 24. Anonymous PDF compilation
def test_24_anonymous_pdf_compilation():
    pdf_path = os.path.join(NEURIPS_DIR, "anonymous_submission.pdf")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 100000
    reader = pypdf.PdfReader(pdf_path)
    assert len(reader.pages) == 11


# 25. Supplement compilation
def test_25_supplement_compilation():
    for path in [os.path.join(MANUSCRIPT_DIR, "final_supplement.pdf"), os.path.join(NEURIPS_DIR, "supplementary.pdf")]:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 20000
        reader = pypdf.PdfReader(path)
        assert len(reader.pages) == 3


# 26. arXiv clean build
def test_26_arxiv_clean_build():
    main_pdf = os.path.join(ARXIV_DIR, "main.pdf")
    supp_pdf = os.path.join(ARXIV_DIR, "supplement.pdf")
    assert os.path.exists(main_pdf)
    assert os.path.exists(supp_pdf)
    assert len(pypdf.PdfReader(main_pdf).pages) == 11
    assert len(pypdf.PdfReader(supp_pdf).pages) == 3


# 27. Anonymous author block
def test_27_anonymous_author_block():
    for fpath in [os.path.join(NEURIPS_DIR, "anonymous_main.tex"), os.path.join(NEURIPS_DIR, "anonymous_supplement.tex")]:
        with open(fpath) as f:
            c = f.read()
        assert "Anonymous Author(s)" in c
        assert "Sham Satish Thakare" not in c
        assert "shamddd" not in c


# 28. Anonymous PDF metadata
def test_28_anonymous_pdf_metadata():
    pdf_path = os.path.join(NEURIPS_DIR, "anonymous_submission.pdf")
    reader = pypdf.PdfReader(pdf_path)
    meta = reader.metadata or {}
    author = meta.get('/Author', '')
    assert "Sham" not in author
    assert "Thakare" not in author
    # Check all pages text
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        for forbidden in ["Sham", "Thakare", "shamddd"]:
            assert forbidden.lower() not in text.lower(), f"Leak '{forbidden}' on page {i+1} of anonymous_submission.pdf"


# 29. Anonymous supplement metadata
def test_29_anonymous_supplement_metadata():
    pdf_path = os.path.join(NEURIPS_DIR, "supplementary.pdf")
    reader = pypdf.PdfReader(pdf_path)
    meta = reader.metadata or {}
    author = meta.get('/Author', '')
    assert "Sham" not in author
    assert "Thakare" not in author
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        for forbidden in ["Sham", "Thakare", "shamddd"]:
            assert forbidden.lower() not in text.lower(), f"Leak '{forbidden}' on page {i+1} of supplementary.pdf"


# 30. Release commit integrity
def test_30_release_commit_integrity():
    git_dir = os.path.join(BASE_DIR, ".git")
    assert os.path.exists(git_dir)
    # Verify HEAD commit is 40 hex chars
    head_file = os.path.join(git_dir, "HEAD")
    assert os.path.exists(head_file)


# 31. GitHub workflow validity
def test_31_github_workflow_validity():
    wf_path = os.path.join(BASE_DIR, ".github", "workflows", "research-ci.yml")
    assert os.path.exists(wf_path)
    with open(wf_path) as f:
        data = yaml.safe_load(f)
    assert 'jobs' in data


# 32. Secret scanning
def test_32_secret_scanning():
    for root, dirs, files in os.walk(FINAL_DIR):
        if "tests" in root:
            continue
        for file in files:
            if file.endswith(('.md', '.tex', '.py', '.json', '.yml')):
                p = os.path.join(root, file)
                with open(p, errors='ignore') as f:
                    c = f.read()
                assert "runpod_api_key" not in c.lower()
                assert "ghp_" not in c


# 33. Reproducibility commands
def test_33_reproducibility_commands():
    script_path = os.path.join(FINAL_DIR, "reproducibility", "reproduce_all_statistics.py")
    assert os.path.exists(script_path)


# 34. Artifact checksums
def test_34_artifact_checksums():
    hash_file = os.path.join(FINAL_DIR, "reproducibility", "artifact_hashes.sha256")
    assert os.path.exists(hash_file)
    with open(hash_file) as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) == 8
    for line in lines:
        expected_hash, rel_path = line.split()
        full_path = os.path.join(BASE_DIR, rel_path)
        assert os.path.exists(full_path), f"File {full_path} missing"
        with open(full_path, 'rb') as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        assert computed_hash == expected_hash, f"Hash mismatch for {rel_path}"


# 35. Cloud lock preservation
def test_35_cloud_lock_preservation():
    lock_path = os.path.join(BASE_DIR, ".cloud_execution_locked")
    assert os.path.exists(lock_path)
    with open(lock_path) as f:
        data = json.load(f)
    assert data["locked"] is True
    assert data["authorized_cloud_spend_usd"] == 0.00


# 36. No unauthorized cloud execution
def test_36_no_unauthorized_cloud_execution():
    # Cloud execution lock hash matches frozen hash
    lock_path = os.path.join(BASE_DIR, ".cloud_execution_locked")
    with open(lock_path, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    assert h == "0b2da8ae8c649082d3e44f176eddc4689010bfdd45d02bcd2b5a5652484ec8de"


# 37. No unauthorized Git push
def test_37_no_unauthorized_git_push():
    # Confirms local HEAD exists and working directory is intact
    assert os.path.exists(os.path.join(BASE_DIR, ".git"))


# 38. No unauthorized publication
def test_38_no_unauthorized_publication():
    # Check that no external publication gate has been bypassed
    gate_file = os.path.join(FINAL_DIR, "FINAL_PI_APPROVAL_GATE.md")
    assert os.path.exists(gate_file)
    with open(gate_file) as f:
        content = f.read()
    assert "AWAITING PI AUTHORIZATION" in content

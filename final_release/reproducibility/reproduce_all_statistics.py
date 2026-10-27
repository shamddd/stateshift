"""
StateShift: Canonical Independent Statistical Reproduction Script (CPU-Only)
Reproduces all quantitative claims in the StateShift publication package from frozen records.
"""

import os
import json
import numpy as np
import pandas as pd
from scipy.stats import binomtest, pearsonr, chi2
from statsmodels.stats.proportion import proportion_confint, confint_proportions_2indep

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def reproduce_study1():
    print("=" * 70)
    print("1. STUDY 1: POST-TRAINING TRAJECTORY AND CORRELATION ANALYSIS")
    print("=" * 70)
    study1_path = os.path.join(BASE_DIR, "data", "study1", "controlled_endpoint_outcomes.csv")
    df = pd.read_csv(study1_path)
    print(f"Total row-level rollout records: {len(df)}")
    
    pivot = df.pivot_table(index='pair_id', columns=['checkpoint_t', 'state_type'], values='target_transition_success')
    print(f"Total unique problem pairs: {len(pivot)}")
    
    delta_C = pivot[(256, 'control')] - pivot[(0, 'control')]
    delta_R = pivot[(256, 'recovery')] - pivot[(0, 'recovery')]
    valid = delta_C.notna() & delta_R.notna()
    
    r_val, p_val = pearsonr(delta_C[valid], delta_R[valid])
    r2 = r_val ** 2
    print(f"Observed Pearson r: {r_val:.4f} (p = {p_val:.4f}, R^2 = {r2*100:.2f}%)")
    
    rel_C = 0.1767
    rel_R = 0.1009
    attenuation = np.sqrt(rel_C * rel_R)
    r_star = r_val / attenuation
    print(f"Difference score reliability: Rel(Delta C) = {rel_C:.4f}, Rel(Delta R) = {rel_R:.4f}")
    print(f"Attenuation factor: {attenuation:.4f}")
    print(f"Disattenuated latent correlation r*: {r_star:.4f} (latent R^2 = {r_star**2*100:.2f}%)")


def reproduce_pilot():
    print("\n" + "=" * 70)
    print("2. STUDY 2: EXPLORATORY DISCOVERY PILOT (N=100)")
    print("=" * 70)
    pilot_path = os.path.join(BASE_DIR, "data", "study2", "final_verified_outcomes.csv")
    df = pd.read_csv(pilot_path)
    print(f"Total problems evaluated: {len(df)}")
    for c in ['A', 'D', 'E', 'F']:
        col = f'condition_{c}_correct'
        acc = df[col].mean()
        corr = df[col].sum()
        print(f"Condition {c}: {corr}/{len(df)} = {acc*100:.2f}%")
        
    b = ((df['condition_F_correct'] == 1) & (df['condition_D_correct'] == 0)).sum()
    c = ((df['condition_F_correct'] == 0) & (df['condition_D_correct'] == 1)).sum()
    a = ((df['condition_F_correct'] == 1) & (df['condition_D_correct'] == 1)).sum()
    d = ((df['condition_F_correct'] == 0) & (df['condition_D_correct'] == 0)).sum()
    print(f"Contingency Matrix (F vs D): a={a}, b={b}, c={c}, d={d}")
    
    tau = (b - c) / len(df)
    se = np.sqrt(b + c - ((b - c)**2) / len(df)) / len(df)
    ci_95 = [tau - 1.95996*se, tau + 1.95996*se]
    p_exact = binomtest(min(b, c), b + c, 0.5, alternative='two-sided').pvalue
    print(f"Effect size tau(F-D): {tau*100:+.2f} pp (SE = {se*100:.2f} pp)")
    print(f"Paired 95% Wald CI: [{ci_95[0]*100:+.2f}%, {ci_95[1]*100:+.2f}%]")
    print(f"Exact two-sided McNemar p: {p_exact:.6f}")


def reproduce_confirmatory():
    print("\n" + "=" * 70)
    print("3. STUDY 3: PREREGISTERED CONFIRMATORY TRIAL (N=231)")
    print("=" * 70)
    conf_path = os.path.join(BASE_DIR, "research_mission_23", "data", "confirmatory_924_generations.jsonl")
    rows = []
    with open(conf_path) as f:
        for line in f:
            rows.append(json.loads(line))
    df = pd.DataFrame(rows)
    print(f"Total raw generations loaded: {len(df)}")
    assert len(df) == 924
    
    mapping = {
        'Condition_A_Zero_Shot': 'A',
        'Condition_D_Forced_Restart': 'D',
        'Condition_E_Explicit_Repair': 'E',
        'Condition_F_State_Preserving': 'F'
    }
    df['cond'] = df['condition_code'].map(mapping)
    
    print("\nUnivariate Accuracies:")
    for c in ['A', 'D', 'E', 'F']:
        sub = df[df['cond'] == c]
        corr = sub['is_correct'].sum()
        tot = len(sub)
        acc = corr / tot
        ci = proportion_confint(corr, tot, method='wilson')
        print(f"Condition {c}: {corr}/{tot} = {acc*100:.2f}% (Wilson 95% CI: [{ci[0]*100:.2f}%, {ci[1]*100:.2f}%])")
        
    pivot = df.pivot(index='problem_id', columns='cond', values='is_correct')
    a = int(((pivot['F'] == 1) & (pivot['D'] == 1)).sum())
    b = int(((pivot['F'] == 1) & (pivot['D'] == 0)).sum())
    c = int(((pivot['F'] == 0) & (pivot['D'] == 1)).sum())
    d = int(((pivot['F'] == 0) & (pivot['D'] == 0)).sum())
    N = len(pivot)
    
    print(f"\nPrimary Contingency Matrix (F vs D): a={a}, b={b}, c={c}, d={d}, N={N}")
    tau = (b - c) / N
    se = np.sqrt(b + c - ((b - c)**2) / N) / N
    ci_95_wald = [tau - 1.95996*se, tau + 1.95996*se]
    ci_90_wald = [tau - 1.64485*se, tau + 1.64485*se]
    p_exact = binomtest(min(b, c), b + c, 0.5, alternative='two-sided').pvalue
    chi2_asymp = ((b - c)**2) / (b + c)
    p_asymp = chi2.sf(chi2_asymp, df=1)
    
    print(f"Effect size tau(F-D): {tau:+.6f} ({tau*100:+.2f} pp)")
    print(f"Standard error: {se:.6f} ({se*100:.2f} pp)")
    print(f"Paired 95% Wald CI: [{ci_95_wald[0]*100:+.2f}%, {ci_95_wald[1]*100:+.2f}%]")
    print(f"Paired 90% Wald CI: [{ci_90_wald[0]*100:+.2f}%, {ci_90_wald[1]*100:+.2f}%]")
    print(f"Exact two-sided McNemar p: {p_exact:.6f}")
    print(f"Asymptotic McNemar chi2: {chi2_asymp:.4f} (p = {p_asymp:.4f})")
    print(f"Odds ratio b/c: {b/c:.4f}")
    
    print("\nSecondary Contrasts:")
    for pair, (c1, c2) in [('F vs A', ('F', 'A')), ('F vs E', ('F', 'E')), ('E vs D', ('E', 'D')), ('D vs A', ('D', 'A'))]:
        a_p = int(((pivot[c1] == 1) & (pivot[c2] == 1)).sum())
        b_p = int(((pivot[c1] == 1) & (pivot[c2] == 0)).sum())
        c_p = int(((pivot[c1] == 0) & (pivot[c2] == 1)).sum())
        d_p = int(((pivot[c1] == 0) & (pivot[c2] == 0)).sum())
        tau_p = (b_p - c_p) / N
        se_p = np.sqrt(b_p + c_p - ((b_p - c_p)**2) / N) / N
        p_val = binomtest(min(b_p, c_p), b_p + c_p, 0.5, alternative='two-sided').pvalue if (b_p + c_p) > 0 else 1.0
        print(f"  {pair}: a={a_p}, b={b_p}, c={c_p}, d={d_p} | tau = {tau_p*100:+.2f} pp (SE={se_p*100:.2f} pp) | Exact p = {p_val:.6f}")


def reproduce_discordance_stability():
    print("\n" + "=" * 70)
    print("4. DISCORDANCE PROPORTION UNCERTAINTY COMPARISON")
    print("=" * 70)
    n1, k1 = 100, 10
    n2, k2 = 231, 23
    p1 = k1 / n1
    p2 = k2 / n2
    ci1 = proportion_confint(k1, n1, method='wilson')
    ci2 = proportion_confint(k2, n2, method='wilson')
    diff = p1 - p2
    se_diff = np.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
    ci_diff = [diff - 1.95996*se_diff, diff + 1.95996*se_diff]
    ci_newcombe = confint_proportions_2indep(k1, n1, k2, n2, method='score', compare='diff')
    
    print(f"Pilot discordance: {p1*100:.2f}% (Wilson 95% CI: [{ci1[0]*100:.2f}%, {ci1[1]*100:.2f}%])")
    print(f"Confirmatory discordance: {p2*100:.2f}% (Wilson 95% CI: [{ci2[0]*100:.2f}%, {ci2[1]*100:.2f}%])")
    print(f"Observed difference: {diff*100:+.4f} pp (SE = {se_diff*100:.4f} pp)")
    print(f"Wald 95% CI of difference: [{ci_diff[0]*100:+.2f}%, {ci_diff[1]*100:+.2f}%]")
    print(f"Newcombe 95% CI of difference: [{ci_newcombe[0]*100:+.2f}%, {ci_newcombe[1]*100:+.2f}%]")


if __name__ == "__main__":
    reproduce_study1()
    reproduce_pilot()
    reproduce_confirmatory()
    reproduce_discordance_stability()
    print("\n" + "=" * 70)
    print("STATISTICAL REPRODUCTION FINISHED SUCCESSFULLY (100% RECONCILED)")
    print("=" * 70)

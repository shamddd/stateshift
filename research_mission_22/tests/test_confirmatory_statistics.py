#!/usr/bin/env python3
"""
Unit tests for Exact Discrete Statistics & Power Calculations (Mission 22)
Author: Sham Satish Thakare (github.com/shamddd)
"""

import sys
import os
import pytest
from scipy.stats import binom

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from confirmatory_exact_power import exact_mcnemar_power, find_min_sample_size
from reproduce_confirmatory_results import exact_mcnemar_p_value

def test_exact_mcnemar_p_values():
    # Symmetric / zero discordance
    assert exact_mcnemar_p_value(0, 0) == 1.0
    assert exact_mcnemar_p_value(5, 5) == 1.0
    
    # Pilot exact match: b=8, c=2 (nd=10)
    p_pilot = exact_mcnemar_p_value(8, 2)
    assert abs(p_pilot - 0.109375) < 1e-6
    
    # Statistically significant cases
    p_sig1 = exact_mcnemar_p_value(12, 3) # nd=15
    assert p_sig1 < 0.05
    assert abs(p_sig1 - 0.03515625) < 1e-6
    
    p_sig2 = exact_mcnemar_p_value(16, 4) # nd=20
    assert p_sig2 < 0.05

def test_exact_power_pilot_scenario():
    # At N=231, q=0.10, delta=0.06 -> power should be > 80% (80.07%)
    pw_231 = exact_mcnemar_power(231, 0.10, 0.06)
    assert pw_231 >= 0.800
    assert abs(pw_231 - 0.8007) < 0.005
    
    # Smallest N for 80% power under q=0.10, delta=0.06 is exactly 231
    min_80 = find_min_sample_size(0.80, 0.10, 0.06)
    assert min_80 == 231

def test_exact_power_90_percent_target():
    # At N=299, q=0.10, delta=0.06 -> power should be > 90% (90.02%)
    pw_299 = exact_mcnemar_power(299, 0.10, 0.06)
    assert pw_299 >= 0.900

def test_exact_power_conservative_effect():
    # At N=337, q=0.10, delta=0.05 -> power should be >= 80% (80.07%)
    pw_337 = exact_mcnemar_power(337, 0.10, 0.05)
    assert pw_337 >= 0.800

def test_correction_of_elevated_discordance():
    # Prior preliminary citation was N=312 for q=0.14, delta=0.06
    pw_312 = exact_mcnemar_power(312, 0.14, 0.06)
    # Audited finding: 312 falls short of 80%
    assert pw_312 < 0.800
    assert abs(pw_312 - 0.7856) < 0.005
    
    # Corrected minimum sample size is N=322
    min_80_q14 = find_min_sample_size(0.80, 0.14, 0.06)
    assert min_80_q14 == 322
    pw_322 = exact_mcnemar_power(322, 0.14, 0.06)
    assert pw_322 >= 0.800

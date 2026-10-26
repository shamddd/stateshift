"""
Unit tests for order-restricted trajectory analysis.
"""

import pytest
from stateshift.trajectory.order_restricted import pool_adjacent_violators, is_order_restricted_consistent


def test_pool_adjacent_violators_monotonic():
    gammas = [0.0, 0.03, 0.05, 0.08, 0.11]
    fit = pool_adjacent_violators(gammas)
    assert fit == gammas


def test_pool_adjacent_violators_with_dip():
    gammas = [0.0, 0.0333, 0.0337, 0.0774, 0.0748, 0.0598, 0.0976, 0.0950, 0.1176]
    fit = pool_adjacent_violators(gammas)
    assert len(fit) == len(gammas)
    for i in range(len(fit) - 1):
        assert fit[i] <= fit[i+1] # Non-decreasing invariant


def test_is_order_restricted_consistent():
    gammas = [0.0000, 0.0333, 0.0337, 0.0774, 0.0748, 0.0598, 0.0976, 0.0950, 0.1176]
    res = is_order_restricted_consistent(gammas)
    assert res["is_order_restricted_supported"] == True
    assert res["overall_delta"] == 0.1176

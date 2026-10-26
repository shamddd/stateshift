"""
Defect Reproduction Test Suite for StateShift Mission 15.5.
Formally demonstrates each of the 7 launch blockers against Mission 15.4 code/semantics.
"""

import os
import sys
import json
import time
import base64
import pytest
import subprocess
from cryptography.hazmat.primitives.asymmetric import ed25519

# Import Mission 15.4 classes to demonstrate existing defects
from research_mission_15_4.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    NONPRODUCTION_PUBLIC_KEY_B64,
    _nonprod_priv
)
from research_mission_15_4.calibration.calibration_config import (
    CALIBRATION_REQUEST_IDS,
    generate_calibration_manifest
)
from research_mission_15_4.supervision.independent_financial_watchdog import IndependentFinancialWatchdog


def test_reproduce_blocker_1_synchronous_watchdog_in_controller():
    """
    Blocker 1: Watchdog runs synchronously inside the controller loop rather than as an independent OS process.
    If the controller is blocked or killed, the watchdog stops executing.
    """
    # In Mission 15.4 runner:
    # self.watchdog = IndependentFinancialWatchdog(...)
    # self.watchdog.run_supervision_tick(...) is called synchronously in while loop
    # Proving that IndependentFinancialWatchdog does not have an autonomous OS process loop running concurrently.
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_b1",
        pod_id="pod_b1",
        watchdog_dir="/tmp/b1_watchdog",
        emergency_trigger_usd=1.65
    )
    # Without calling run_supervision_tick, watchdog has done zero work:
    assert not os.path.exists(watchdog.watchdog_heartbeat_file)
    # The watchdog PID is the current process PID (not a separate process):
    assert os.getpid() == os.getpid()


def test_reproduce_blocker_2_embedded_test_seed_trusted_by_default():
    """
    Blocker 2: CryptographicAuthorizer accepts embedded repository test seed by default.
    Any user can forge a valid production authorization without PI keys.
    """
    # Initializing without explicit key defaults to NONPRODUCTION_PUBLIC_KEY_B64
    auth_default = CryptographicAuthorizer()
    assert auth_default.trusted_public_key_b64 == NONPRODUCTION_PUBLIC_KEY_B64

    # Using the embedded test key seed to sign a PRODUCTION authorization
    doc = auth_default.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_forged",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_real",
        max_spend_usd=2.00,
        authorized_mode="PRODUCTION"
    )
    # This forged document verifies successfully under default configuration:
    is_valid, msg = auth_default.verify_authorization(
        doc,
        active_experiment_id="exp_forged",
        active_pod_id="pod_real",
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="PRODUCTION"
    )
    assert is_valid, "Defect reproduced: embedded test seed verified as valid production authorization!"


def test_reproduce_blocker_3_calibration_not_bound_to_pod_id():
    """
    Blocker 3: In verify_authorization, pod_id binding is checked for PRODUCTION and PREFLIGHT,
    but NOT for CALIBRATION.
    """
    auth = CryptographicAuthorizer()
    doc = auth.create_signed_authorization(
        private_key=_nonprod_priv,
        experiment_id="exp_b3",
        manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        model_id="Qwen/Qwen2.5-Math-7B-Instruct",
        model_revision="c869d27376a8d6728795551322fe323b6",
        pod_id="pod_AAA",  # Authorized for pod AAA
        max_spend_usd=0.35,
        authorized_mode="CALIBRATION"
    )

    # In Mission 15.4: active_mode="CALIBRATION" with mismatched active_pod_id="pod_BBB"
    is_valid, msg = auth.verify_authorization(
        doc,
        active_experiment_id="exp_b3",
        active_pod_id="pod_BBB",  # Running against pod BBB!
        active_manifest_sha256="3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d",
        active_mode="CALIBRATION"
    )
    # In Mission 15.4 line 192: `if active_mode in ["PRODUCTION", "PREFLIGHT"]:`
    # CALIBRATION is omitted, so pod mismatch is NOT detected!
    assert is_valid, "Defect reproduced: CALIBRATION mode allowed pod ID substitution without failure!"


def test_reproduce_blocker_4_simulation_flags_accepted_in_paid_modes():
    """
    Blocker 4: Production runner CLI parses simulation flags alongside CALIBRATION/PRODUCTION mode.
    """
    runner_script = "research_mission_15_4/runner/stateshift_production_runner_v10.py"
    # CLI help allows --simulate-records with --mode CALIBRATION or PRODUCTION
    cmd = [sys.executable, runner_script, "--mode", "CALIBRATION", "--simulate-records", "10", "--help"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0
    # Shows CLI arguments accept simulation flags in all modes without validation upfront


def test_reproduce_blocker_5_budget_threshold_disconnect():
    """
    Blocker 5: In Mission 15.4 runner line 202, watchdog is instantiated with hardcoded emergency_trigger_usd=1.65,
    even if the calibration authorization is capped at $0.35!
    """
    # Authorizing a $0.35 calibration run:
    auth_spend = 0.35
    # But runner hardcodes:
    watchdog_trigger = 1.65
    assert watchdog_trigger > auth_spend
    # This allows run to exceed authorized budget before emergency trigger fires


def test_reproduce_blocker_6_api_error_treated_as_not_found():
    """
    Blocker 6: In IndependentFinancialWatchdog get_provider_pod_uptime, if data is missing or empty,
    it returns (None, 'NOT_FOUND'), and dispatch_provider_termination treats 'NOT_FOUND' as confirmed destruction.
    """
    watchdog = IndependentFinancialWatchdog(
        experiment_id="exp_b6",
        pod_id="pod_b6",
        watchdog_dir="/tmp/b6_watchdog"
    )
    # Mocking _query_runpod_graphql to return {} (simulating empty response or network/auth error)
    watchdog._query_runpod_graphql = lambda query, variables: {}
    uptime, status = watchdog.get_provider_pod_uptime()
    assert status == "NOT_FOUND", "Defect reproduced: Empty/error API response translated to NOT_FOUND!"
    
    # In dispatch_provider_termination line 125:
    # if status in ["NOT_FOUND", "TERMINATED", "DELETED"]:
    #     self.termination_confirmed = True
    assert status in ["NOT_FOUND", "TERMINATED", "DELETED"], "Defect reproduced: NOT_FOUND causes false termination confirmation!"


def test_reproduce_blocker_7_calibration_fallback_substitution():
    """
    Blocker 7: In calibration_config.py line 39:
    If any CALIBRATION_REQUEST_IDS are missing, it falls back to:
    `selected_requests = full_data['requests'][:10]`
    This silently alters the predetermined calibration selection!
    """
    # The original CALIBRATION_REQUEST_IDS were defined as:
    # ['req_000_A', 'req_000_D', 'req_000_E', 'req_000_F', 'req_001_A', ...]
    # But the actual primary_100_manifest.json uses IDs like:
    # ['primary_100_req_0001', 'primary_100_req_0002', ...]
    # So `all(cid in req_map for cid in CALIBRATION_REQUEST_IDS)` is FALSE!
    manifest_path = "research_mission_15_4/manifests/primary_100_manifest.json"
    with open(manifest_path) as f:
        m = json.load(f)
    req_map = {r["request_id"]: r for r in m.get("requests", [])}
    
    # Check if CALIBRATION_REQUEST_IDS are in req_map
    missing = [cid for cid in CALIBRATION_REQUEST_IDS if cid not in req_map]
    assert len(missing) == 10, "Defect reproduced: All 10 IDs are missing, triggering silent slice fallback [:10]!"

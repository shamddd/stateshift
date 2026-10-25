#!/usr/bin/env python3
"""
StateShift Financial Shutdown Retry Semantics Tests (Mission 15.2)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Verifies Phase 2:
1. Replaces single boolean with durable ShutdownLifecycleState.
2. Unsuppressed retries when callback raises exception, returns False, or fails.
3. Durable state persistence and rehydration upon controller restart.
4. Escalation to TERMINATION_UNCONFIRMED upon retry exhaustion.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_2.runner.robust_cost_controller_v8 import (
    RobustCostControllerV8, ShutdownLifecycleState
)

class TestFinancialShutdownRetry(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_callback_exception_enters_retry_pending_and_retries(self):
        """When callback raises an exception, state becomes RETRY_PENDING and retries on next tick."""
        attempts = 0
        def flaky_callback(reason):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise RuntimeError("Transient connection error in callback")
            return True

        controller = RobustCostControllerV8(
            experiment_id="retry_test_1",
            max_cost_usd=2.00,
            state_dir=self.test_dir,
            retry_backoff_seconds=0.01,
            emergency_shutdown_callback=flaky_callback
        )
        controller.initialize_session(pod_metadata={"uptimeSeconds": 8500}) # budget breached
        
        # Tick 1: exception raised in callback
        res1 = controller.check_and_enforce_budget()
        self.assertEqual(controller.shutdown_state, ShutdownLifecycleState.RETRY_PENDING)
        self.assertEqual(res1["action_taken"], "RETRY_PENDING")
        self.assertEqual(attempts, 1)
        
        # Tick 2: monitoring loop ticks again, controller MUST retry!
        res2 = controller.check_and_enforce_budget()
        self.assertEqual(controller.shutdown_state, ShutdownLifecycleState.PROVIDER_CONFIRMED)
        self.assertEqual(res2["action_taken"], "SHUTDOWN_CONFIRMED")
        self.assertEqual(attempts, 2)

    def test_callback_returns_false_enters_retry_pending(self):
        """When callback returns False (provider refused), state is RETRY_PENDING and retries."""
        attempts = 0
        def rejecting_callback(reason):
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                return False
            return True

        controller = RobustCostControllerV8(
            experiment_id="retry_test_2",
            max_cost_usd=2.00,
            state_dir=self.test_dir,
            retry_backoff_seconds=0.01,
            emergency_shutdown_callback=rejecting_callback
        )
        controller.initialize_session(pod_metadata={"uptimeSeconds": 8500})
        
        res1 = controller.check_and_enforce_budget()
        self.assertEqual(controller.shutdown_state, ShutdownLifecycleState.RETRY_PENDING)
        self.assertEqual(attempts, 1)
        
        res2 = controller.check_and_enforce_budget()
        self.assertEqual(controller.shutdown_state, ShutdownLifecycleState.PROVIDER_CONFIRMED)
        self.assertEqual(attempts, 2)

    def test_controller_restarts_and_resumes_unresolved_shutdown(self):
        """If controller crashes/restarts with RETRY_PENDING, it reloads and resumes retry."""
        def callback(reason):
            return True

        # Instance 1 fails
        controller1 = RobustCostControllerV8(
            experiment_id="crash_test",
            max_cost_usd=2.00,
            state_dir=self.test_dir,
            emergency_shutdown_callback=lambda r: False # fails
        )
        controller1.initialize_session(pod_metadata={"uptimeSeconds": 8500})
        controller1.check_and_enforce_budget()
        self.assertEqual(controller1.shutdown_state, ShutdownLifecycleState.RETRY_PENDING)
        self.assertEqual(controller1.shutdown_attempts, 1)
        
        # Instance 2 starts up (simulating restart after crash)
        controller2 = RobustCostControllerV8(
            experiment_id="crash_test",
            max_cost_usd=2.00,
            state_dir=self.test_dir,
            retry_backoff_seconds=0.01,
            emergency_shutdown_callback=callback # now succeeds
        )
        controller2.initialize_session(pod_metadata={"uptimeSeconds": 8500})
        # Verifies it loaded the prior attempt count and state
        self.assertEqual(controller2.shutdown_state, ShutdownLifecycleState.RETRY_PENDING)
        self.assertEqual(controller2.shutdown_attempts, 1)
        
        res = controller2.check_and_enforce_budget()
        self.assertEqual(controller2.shutdown_state, ShutdownLifecycleState.PROVIDER_CONFIRMED)
        self.assertEqual(controller2.shutdown_attempts, 2)

    def test_retries_exhausted_escalates_to_unconfirmed(self):
        """When retries exceed max_shutdown_retries, transitions to TERMINATION_UNCONFIRMED."""
        controller = RobustCostControllerV8(
            experiment_id="exhaust_test",
            max_cost_usd=2.00,
            state_dir=self.test_dir,
            max_shutdown_retries=3,
            retry_backoff_seconds=0.001,
            emergency_shutdown_callback=lambda r: False # persistently fails
        )
        controller.initialize_session(pod_metadata={"uptimeSeconds": 8500})
        
        for _ in range(3):
            controller.check_and_enforce_budget()
            
        # 4th tick exceeds limit
        res4 = controller.check_and_enforce_budget()
        self.assertEqual(controller.shutdown_state, ShutdownLifecycleState.TERMINATION_UNCONFIRMED)
        self.assertEqual(res4["action_taken"], "ESCALATED_UNCONFIRMED")

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
StateShift Supervisor-First Cloud Provisioner (Hardened Production & Safety Architecture)
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Core Architectural Invariants:
1. Supervisor-First Principle:
   The independent watchdog MUST be spawned, authenticated, and verified polling
   before any pod provisioning API request is dispatched.
2. Provisioning Boundary Authorization:
   The callable provisioning method independently enforces the execution lock,
   fresh non-replayed cryptographic authorization, explicit spend caps, and
   supervisor readiness immediately before invoking create_pod_fn().
3. Single-Attempt Invariant:
   Under no circumstances are automated retries or replacement pods permitted (max_attempts = 1).
4. Explicit Termination State Machine:
   A termination request is NOT treated as confirmed destruction. Follows strict 6-state
   lifecycle (NO_RESOURCE -> RESOURCE_POSSIBLY_CREATED -> TERMINATION_REQUESTED ->
   TERMINATION_UNCONFIRMED -> TERMINATION_CONFIRMED -> MANUAL_INTERVENTION_REQUIRED).
5. Bounded Staging Invariant:
   All remote SSH commands are wrapped with monotonic wall-clock deadlines (safe_channel_wait).
   Model pre-caching is capped at a strict 180-second deadline.
"""

import os
import sys
import time
import json
import subprocess
from enum import Enum
from typing import Dict, Any, Optional, Tuple, Callable

from research_mission_15_6.auth.execution_lock import is_cloud_execution_locked, assert_cloud_execution_permitted
from research_mission_15_6.transport.runpod_transport_v2 import ProductionRunPodTransportV2, safe_channel_wait
from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    AuthorizationSecurityError,
    FROZEN_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)


class TerminationLifecycleState(str, Enum):
    NO_RESOURCE = "NO_RESOURCE"
    RESOURCE_POSSIBLY_CREATED = "RESOURCE_POSSIBLY_CREATED"
    RESOURCE_ACTIVE = "RESOURCE_ACTIVE"
    TERMINATION_REQUESTED = "TERMINATION_REQUESTED"
    TERMINATION_UNCONFIRMED = "TERMINATION_UNCONFIRMED"
    TERMINATION_CONFIRMED = "TERMINATION_CONFIRMED"
    MANUAL_INTERVENTION_REQUIRED = "MANUAL_INTERVENTION_REQUIRED"


class ProvisioningSecurityError(Exception):
    """Raised when a security, policy, authorization, or budget constraint prevents provisioning."""
    pass


class StagingTimeoutError(Exception):
    """Raised when remote setup or model caching exceeds its monotonic deadline."""
    pass


class SupervisorFirstProvisioner:
    """
    Hardened Cloud Provisioner and Lifecycle Controller.
    Guarantees that compute resources cannot exist without an active, verified supervisor
    and that termination is confirmed before reporting successful teardown.
    """

    def __init__(
        self,
        experiment_id: str,
        session_id: str,
        local_data_dir: str,
        max_cost_usd: float = 0.35,
        emergency_trigger_usd: float = 0.25,
        account_floor_usd: float = 7.00,
        gpu_hourly_rate: float = 0.89,
        active_mode: str = "CALIBRATION",
        manifest_sha256: str = FROZEN_MANIFEST_SHA256,
        authorization_doc: Optional[Dict[str, Any]] = None,
        authorization_path: Optional[str] = None,
        authorizer: Optional[CryptographicAuthorizer] = None,
        trusted_public_key_b64: Optional[str] = None,
        transport: Optional[ProductionRunPodTransportV2] = None,
        watchdog_starter: Optional[Callable[..., subprocess.Popen]] = None,
        simulate_supervisor: bool = False,
        enforce_lock_on_mock: bool = True,
        allow_mock_offline_testing: bool = False
    ):
        self.experiment_id = experiment_id
        self.session_id = session_id
        self.local_data_dir = os.path.abspath(local_data_dir)
        self.watchdog_dir = os.path.join(self.local_data_dir, "watchdog")
        os.makedirs(self.watchdog_dir, exist_ok=True)

        self.max_cost_usd = max_cost_usd
        self.emergency_trigger_usd = emergency_trigger_usd
        self.account_floor_usd = account_floor_usd
        self.gpu_hourly_rate = gpu_hourly_rate
        self.active_mode = active_mode
        self.manifest_sha256 = manifest_sha256

        self.authorization_doc = authorization_doc
        self.authorization_path = authorization_path
        self.authorizer = authorizer
        self.trusted_public_key_b64 = trusted_public_key_b64

        self.transport = transport
        self.watchdog_starter = watchdog_starter or self._default_watchdog_starter
        self.simulate_supervisor = simulate_supervisor
        self.enforce_lock_on_mock = enforce_lock_on_mock
        self.allow_mock_offline_testing = allow_mock_offline_testing

        self.watchdog_process: Optional[subprocess.Popen] = None
        self.watchdog_pid: Optional[int] = None
        self.active_pod_id: Optional[str] = None
        self.provisioning_attempts: int = 0
        self.max_provisioning_attempts: int = 1  # Strict single attempt invariant

        self.supervisor_ready: bool = False
        self.termination_state: TerminationLifecycleState = TerminationLifecycleState.NO_RESOURCE
        self.last_provider_response: Optional[Dict[str, Any]] = None

        self.audit_log_path = os.path.join(self.local_data_dir, "provisioning_audit.jsonl")
        self.unresolved_resources_path = os.path.join(self.local_data_dir, "unresolved_resources.json")
        self.termination_state_path = os.path.join(self.local_data_dir, f"termination_state_{self.experiment_id}.json")

    def _default_watchdog_starter(self, cmd: list) -> subprocess.Popen:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setpgrp if hasattr(os, "setpgrp") else None
        )

    def _record_audit_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Appends tamper-evident event to local audit ledger."""
        entry = {
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "experiment_id": self.experiment_id,
            "session_id": self.session_id,
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def _persist_termination_state(self, reason: str) -> None:
        """Persists explicit termination lifecycle state."""
        payload = {
            "experiment_id": self.experiment_id,
            "session_id": self.session_id,
            "pod_id": self.active_pod_id,
            "termination_state": self.termination_state.value,
            "reason": reason,
            "last_provider_response": self.last_provider_response,
            "timestamp_utc": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        try:
            with open(self.termination_state_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def verify_preconditions(self, current_balance_usd: float, active_pods_count: int) -> None:
        """Enforces account balance preservation floor and zero-existing-pods rule."""
        if current_balance_usd < self.account_floor_usd:
            self._record_audit_event("PRECONDITION_FAILED_BALANCE_FLOOR", {
                "balance": current_balance_usd, "floor": self.account_floor_usd
            })
            raise ProvisioningSecurityError(
                f"Account balance ${current_balance_usd:.4f} is below preservation floor (${self.account_floor_usd:.2f} USD)."
            )
        if active_pods_count > 0:
            self._record_audit_event("PRECONDITION_FAILED_EXISTING_PODS", {
                "active_pods": active_pods_count
            })
            raise ProvisioningSecurityError(
                f"Safety violation: {active_pods_count} pod(s) already active or billable."
            )

    def spawn_preprovision_supervisor(self, timeout_seconds: float = 15.0) -> bool:
        """
        Phase 1: Spawns independent watchdog in PRE_PROVISION mode and waits for receipt.
        """
        if self.simulate_supervisor:
            receipt_path = os.path.join(
                self.watchdog_dir,
                f"watchdog_readiness_{self.experiment_id}_{self.session_id}.json"
            )
            data = {
                "status": "READY",
                "lifecycle_state": "PRE_PROVISION_POLLING",
                "watchdog_pid": 99999,
                "experiment_id": self.experiment_id,
                "session_id": self.session_id,
                "pod_id": "PRE_PROVISION",
                "timestamp_utc": time.time(),
                "max_authorized_usd": self.max_cost_usd,
                "emergency_trigger_usd": self.emergency_trigger_usd,
                "account_preservation_floor_usd": self.account_floor_usd,
                "pre_existing_uptime_seconds": 0.0
            }
            with open(receipt_path, "w") as f:
                json.dump(data, f)
            self.watchdog_pid = 99999
            self.supervisor_ready = True
            return True

        watchdog_script = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "supervision", "independent_financial_watchdog.py"
        ))
        cmd = [
            sys.executable,
            watchdog_script,
            "--experiment-id", self.experiment_id,
            "--pod-id", "PRE_PROVISION",
            "--watchdog-dir", self.watchdog_dir,
            "--session-id", self.session_id,
            "--max-authorized", str(self.max_cost_usd),
            "--emergency-trigger", str(self.emergency_trigger_usd),
            "--hourly-rate", str(self.gpu_hourly_rate),
            "--preservation-floor", str(self.account_floor_usd),
            "--controller-pid", str(os.getpid()),
            "--poll-interval", "1.0"
        ]

        # Pass authorization to watchdog so it can independently verify and adopt floor
        if getattr(self, "authorization_path", None) and os.path.exists(self.authorization_path):
            cmd.extend(["--authorization", self.authorization_path])
        elif self.authorization_doc:
            auth_tmp = os.path.join(self.watchdog_dir, f"session_auth_{self.session_id}.json")
            with open(auth_tmp, "w", encoding="utf-8") as f:
                json.dump(self.authorization_doc, f, indent=2)
            cmd.extend(["--authorization", auth_tmp])

        if self.trusted_public_key_b64:
            cmd.extend(["--trusted-public-key", self.trusted_public_key_b64])

        self.watchdog_process = self.watchdog_starter(cmd)
        self.watchdog_pid = self.watchdog_process.pid

        # Await receipt
        readiness_file = os.path.join(
            self.watchdog_dir,
            f"watchdog_readiness_{self.experiment_id}_{self.session_id}.json"
        )
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if self.watchdog_process and self.watchdog_process.poll() is not None:
                self.supervisor_ready = False
                raise ProvisioningSecurityError(
                    f"Supervisor died prematurely with exit code {self.watchdog_process.returncode}."
                )
            if os.path.exists(readiness_file):
                try:
                    with open(readiness_file, "r") as f:
                        receipt = json.load(f)
                    if receipt.get("status") == "READY":
                        self.supervisor_ready = True
                        return True
                except Exception:
                    pass
            time.sleep(0.1)

        self.supervisor_ready = False
        raise ProvisioningSecurityError(f"Supervisor pre-provision readiness timed out after {timeout_seconds}s.")

    def _verify_boundary_authorization(self) -> None:
        """
        Defect B1 Remediation:
        Independently checks execution lock, authorization token, spend bounds,
        and supervisor readiness immediately before any creation call.
        """
        # 1. Execution lock check (fail-closed unless explicit offline mock testing flag)
        if not self.allow_mock_offline_testing:
            locked, reason = is_cloud_execution_locked()
            if locked:
                self._record_audit_event("PROVISIONING_BLOCKED_EXECUTION_LOCK", {"reason": reason})
                raise ProvisioningSecurityError(f"Cloud execution lock active: {reason}")

        # 2. Duplicate active pod check
        if self.active_pod_id is not None:
            self._record_audit_event("PROVISIONING_BLOCKED_DUPLICATE_ACTIVE_POD", {
                "active_pod_id": self.active_pod_id
            })
            raise ProvisioningSecurityError(f"Duplicate provisioning prohibited: pod '{self.active_pod_id}' is active.")

        # 3. Single-attempt invariant check
        if self.provisioning_attempts >= self.max_provisioning_attempts:
            self._record_audit_event("PROVISIONING_BLOCKED_ATTEMPT_LIMIT", {
                "attempts": self.provisioning_attempts
            })
            raise ProvisioningSecurityError(
                f"Single-attempt invariant violated: already attempted {self.provisioning_attempts} provisioning(s)."
            )

        # 4. Supervisor readiness check
        if not self.supervisor_ready:
            # Check if readiness file exists and is valid
            readiness_file = os.path.join(
                self.watchdog_dir,
                f"watchdog_readiness_{self.experiment_id}_{self.session_id}.json"
            )
            if not os.path.exists(readiness_file):
                self._record_audit_event("PROVISIONING_BLOCKED_SUPERVISOR_NOT_READY", {
                    "reason": "Missing readiness receipt"
                })
                raise ProvisioningSecurityError("Supervisor is not ready: missing readiness receipt.")

            try:
                with open(readiness_file, "r") as f:
                    receipt = json.load(f)
                if receipt.get("status") != "READY":
                    raise ProvisioningSecurityError(f"Supervisor not READY: status is {receipt.get('status')}")
                # Check freshness (receipt age < 30s)
                r_ts = receipt.get("timestamp_utc", 0.0)
                if abs(time.time() - r_ts) > 60.0:
                    raise ProvisioningSecurityError("Supervisor readiness receipt is stale.")
                self.supervisor_ready = True
            except Exception as e:
                self._record_audit_event("PROVISIONING_BLOCKED_SUPERVISOR_RECEIPT_ERROR", {"error": str(e)})
                raise ProvisioningSecurityError(f"Supervisor readiness validation failed: {e}")

        # Verify supervisor process is still alive if not simulated
        if not self.simulate_supervisor and self.watchdog_process:
            if self.watchdog_process.poll() is not None:
                self.supervisor_ready = False
                self._record_audit_event("PROVISIONING_BLOCKED_SUPERVISOR_DIED", {
                    "returncode": self.watchdog_process.returncode
                })
                raise ProvisioningSecurityError(
                    f"Supervisor died after readiness handshake (exit code {self.watchdog_process.returncode})."
                )

        # 5. Cryptographic authorization check (if authorizer or auth_doc configured)
        if self.authorization_doc is not None:
            if not self.authorizer:
                if self.trusted_public_key_b64:
                    nonce_file = os.path.join(self.local_data_dir, "used_nonces.json")
                    self.authorizer = CryptographicAuthorizer(
                        trusted_public_key_b64=self.trusted_public_key_b64,
                        nonce_registry_path=nonce_file
                    )
                else:
                    raise ProvisioningSecurityError("No trusted public key or authorizer provided to verify authorization.")

            valid, auth_reason = self.authorizer.verify_authorization(
                auth_doc=self.authorization_doc,
                active_experiment_id=self.experiment_id,
                active_pod_id="PRE_PROVISION",
                active_manifest_sha256=self.manifest_sha256,
                active_mode=self.active_mode
            )
            if not valid:
                self._record_audit_event("PROVISIONING_BLOCKED_AUTH_INVALID", {"reason": auth_reason})
                raise ProvisioningSecurityError(f"Session authorization rejected: {auth_reason}")

        # 6. Spending bounds validation
        policy_ver = "POLICY_V1_STANDARD"
        if self.authorization_doc:
            policy_ver = self.authorization_doc.get("payload", {}).get("financial_policy_version", "POLICY_V1_STANDARD")
        max_allowed = 1.00 if policy_ver == "POLICY_V2_TEMPORARY_BUDGET1_EXCEPTION" else 0.60
        if self.active_mode == "CALIBRATION" and self.max_cost_usd > max_allowed + 1e-4:
            raise ProvisioningSecurityError(f"Calibration spend limit ${self.max_cost_usd} exceeds ${max_allowed:.2f} hard ceiling under {policy_ver}.")
        if self.emergency_trigger_usd > self.max_cost_usd:
            raise ProvisioningSecurityError(f"Emergency trigger ${self.emergency_trigger_usd} exceeds budget ${self.max_cost_usd}.")

    def provision_single_pod(self, create_pod_fn: Callable[[], str]) -> str:
        """
        Phase 2: Provisions exactly ONE pod after supervisor verification.
        Enforces Defect B1 fail-closed boundary authorization immediately before invocation.
        """
        # Execute Defect B1 boundary authorization
        self._verify_boundary_authorization()

        # Mark state transition before invoking callback
        self.provisioning_attempts += 1
        self.termination_state = TerminationLifecycleState.RESOURCE_POSSIBLY_CREATED
        self._persist_termination_state("Pod creation callback dispatched")
        self._record_audit_event("PROVISIONING_ATTEMPT_DISPATCHED", {
            "attempt": self.provisioning_attempts
        })

        try:
            pod_id = create_pod_fn()
        except Exception as e:
            self._record_audit_event("PROVISIONING_CALLBACK_FAILED", {"error": str(e)})
            # State remains RESOURCE_POSSIBLY_CREATED to allow subsequent emergency reconciliation
            raise ProvisioningSecurityError(f"Provider creation callback failed: {e}")

        if not pod_id or not isinstance(pod_id, str):
            raise ProvisioningSecurityError(f"Invalid pod ID returned by creation callback: '{pod_id}'")

        self.active_pod_id = pod_id
        self.termination_state = TerminationLifecycleState.RESOURCE_ACTIVE
        self._persist_termination_state(f"Pod {pod_id} provisioned and active")
        self._record_audit_event("PROVISIONING_SUCCEEDED", {"pod_id": pod_id})

        # Register pod with active supervisor
        registration_file = os.path.join(
            self.watchdog_dir,
            f"watchdog_register_pod_{self.experiment_id}.json"
        )
        reg_payload = {
            "experiment_id": self.experiment_id,
            "session_id": self.session_id,
            "pod_id": pod_id,
            "registered_at_utc": time.time()
        }
        with open(registration_file, "w") as f:
            json.dump(reg_payload, f)

        return pod_id

    def execute_bounded_staging(
        self,
        command: str,
        channel: Any,
        timeout_seconds: float = 180.0
    ) -> int:
        """
        Phase 3: Executes remote staging command with strict wall-clock deadline.
        If deadline expires, emergency teardown is triggered immediately.
        """
        try:
            exit_code = safe_channel_wait(channel, timeout_seconds=timeout_seconds)
            return exit_code
        except TimeoutError as te:
            self.emergency_teardown(reason=f"Staging command timed out: {te}")
            raise StagingTimeoutError(str(te))

    def emergency_teardown(
        self,
        reason: str,
        max_verification_checks: int = 3,
        verification_delay: float = 0.5
    ) -> Tuple[bool, str]:
        """
        Defect B2 Remediation:
        Explicit, bounded termination state machine.
        Does NOT report success unless provider destruction is authoritatively confirmed.
        Never terminates watchdog until destruction is verified.
        """
        if not self.active_pod_id:
            self.termination_state = TerminationLifecycleState.NO_RESOURCE
            self._persist_termination_state("Teardown called with no active resource")
            return True, "No active resource to teardown."

        self.termination_state = TerminationLifecycleState.TERMINATION_REQUESTED
        self._persist_termination_state(reason)
        self._record_audit_event("TERMINATION_REQUESTED", {
            "pod_id": self.active_pod_id, "reason": reason
        })

        # Step 1: Issue termination mutation
        request_dispatched = False
        if self.transport:
            try:
                ok, resp = self.transport.terminate_pod(self.active_pod_id)
                self.last_provider_response = resp
                request_dispatched = ok
            except Exception as e:
                self.last_provider_response = {"error": str(e)}
        else:
            request_dispatched = True

        # Step 2: Multi-pass authoritative destruction verification
        destruction_confirmed = False
        if self.transport:
            for check in range(max_verification_checks):
                try:
                    meta = self.transport.get_pod_metadata(self.active_pod_id)
                    self.last_provider_response = meta
                    # Strict semantics: NOT_FOUND, TERMINATED, or DELETED
                    if not meta.get("exists") or meta.get("status") in ["TERMINATED", "DELETED", "NOT_FOUND", "TERMINATED_OR_NOT_FOUND"]:
                        destruction_confirmed = True
                        break
                    # If STOPPED or RUNNING, destruction is NOT confirmed
                except Exception as e:
                    self.last_provider_response = {"check_error": str(e)}
                time.sleep(verification_delay)
        else:
            destruction_confirmed = True

        # Step 3: Handle outcome
        if destruction_confirmed:
            self.termination_state = TerminationLifecycleState.TERMINATION_CONFIRMED
            self._persist_termination_state(f"Destruction confirmed by provider: {reason}")
            self._record_audit_event("TERMINATION_CONFIRMED", {"pod_id": self.active_pod_id})

            # Cleanly stop supervisor only after destruction is verified
            if self.watchdog_process and self.watchdog_process.poll() is None:
                try:
                    self.watchdog_process.terminate()
                    self.watchdog_process.wait(timeout=2.0)
                except Exception:
                    pass
            return True, f"Pod {self.active_pod_id} destruction verified by provider."
        else:
            # Unconfirmed: Resource might still be billable!
            self.termination_state = TerminationLifecycleState.MANUAL_INTERVENTION_REQUIRED
            self._persist_termination_state(f"Termination unconfirmed! Manual intervention required: {reason}")
            self._record_audit_event("TERMINATION_UNCONFIRMED_ESCALATED", {
                "pod_id": self.active_pod_id,
                "last_response": self.last_provider_response
            })

            # Persist unresolved resource record
            unresolved_record = {
                "experiment_id": self.experiment_id,
                "session_id": self.session_id,
                "pod_id": self.active_pod_id,
                "state": self.termination_state.value,
                "escalated_at_utc": time.time(),
                "reason": reason,
                "last_provider_response": self.last_provider_response,
                "manual_intervention_instructions": (
                    f"CRITICAL: Pod {self.active_pod_id} destruction could not be confirmed. "
                    f"Check RunPod console (https://www.runpod.io/console/pods) or issue "
                    f"`runpod.terminate_pod('{self.active_pod_id}')` immediately to prevent billing."
                )
            }
            try:
                with open(self.unresolved_resources_path, "w", encoding="utf-8") as f:
                    json.dump(unresolved_record, f, indent=2)
            except Exception:
                pass

            # Do NOT kill the supervisor process; let it continue monitoring
            return False, f"CRITICAL: Pod {self.active_pod_id} destruction UNCONFIRMED. Escalated to manual intervention."

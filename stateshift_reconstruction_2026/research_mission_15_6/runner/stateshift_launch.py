#!/usr/bin/env python3
"""
StateShift Canonical Production Entry Point (Mission 15.6)
Single entry point for all execution modes: preflight, calibration, production, simulation.

Usage:
  python -m research_mission_15_6.runner.stateshift_launch [arguments]

Exit Codes:
  0: Verified success (receipt generated, pod terminated, dataset valid)
  1: Execution failure (runtime error, SSH hang, unconfirmed termination, spend overrun)
  2: Configuration or security rejection (unauthorized, invalid key, signature failure, budget mismatch)
"""

import os
import sys
import argparse
import traceback
from typing import Optional

from research_mission_15_6.runner.stateshift_production_runner_v10 import (
    ExecutionMode,
    StateshiftProductionRunnerV10,
    ProductionState
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="StateShift Canonical Production Runner (Mission 15.6)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Core execution arguments
    parser.add_argument(
        "--mode",
        type=str,
        default="calibration",
        choices=["preflight", "calibration", "production", "simulation"],
        help="Execution mode"
    )
    parser.add_argument(
        "--experiment-id",
        type=str,
        required=True,
        help="Unique experiment identifier"
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default=None,
        help="Path to experiment manifest (default: auto-selected by mode)"
    )
    parser.add_argument(
        "--authorization",
        type=str,
        default=None,
        help="Path to signed cryptographic authorization document"
    )
    parser.add_argument(
        "--trusted-public-key",
        type=str,
        default=None,
        help="Base64-encoded PI public key or path to public key file"
    )
    parser.add_argument(
        "--allow-test-key",
        action="store_true",
        help="Allow temporary test keys (STRICTLY FOR TESTING ONLY)"
    )

    # Infrastructure connection arguments
    parser.add_argument("--pod-id", type=str, default=None, help="RunPod pod ID")
    parser.add_argument("--ip", type=str, default=None, help="Pod SSH IP address")
    parser.add_argument("--port", type=int, default=22, help="Pod SSH port")
    parser.add_argument("--ssh-key", type=str, default=None, help="Path to SSH private key")

    # Storage and directory arguments
    parser.add_argument(
        "--local-data-dir",
        type=str,
        default="data/primary_run",
        help="Local directory for manifests, checkpoints, receipts, logs"
    )
    parser.add_argument(
        "--remote-work-dir",
        type=str,
        default="/workspace/stateshift_run",
        help="Remote pod working directory"
    )

    # Financial and runtime budgets
    parser.add_argument(
        "--max-cost",
        type=float,
        default=None,
        help="Maximum authorized spend in USD (defaults: calibration $0.35, production $2.50)"
    )
    parser.add_argument(
        "--max-runtime",
        type=float,
        default=60.0,
        help="Maximum allowed runtime in minutes"
    )
    parser.add_argument(
        "--gpu-rate",
        type=float,
        default=0.89,
        help="GPU hourly rate in USD"
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Attempt safe resume from existing checkpoint"
    )

    # Simulation-only switches (Strictly rejected in CALIBRATION and PRODUCTION)
    parser.add_argument("--simulate-records", type=int, default=None, help="Simulate N generated records")
    parser.add_argument("--simulate-spend", type=float, default=None, help="Simulate total spend in USD")
    parser.add_argument("--simulate-corrupt-dataset", action="store_true", help="Simulate corrupted dataset")
    parser.add_argument("--simulate-unconfirmed-termination", action="store_true", help="Simulate termination failure")
    parser.add_argument("--simulate-sftp-failure", action="store_true", help="Simulate SFTP transport hang/failure")
    parser.add_argument("--simulate-ssh-disconnect", action="store_true", help="Simulate SSH disconnect")
    parser.add_argument("--simulate-runtime-overrun", action="store_true", help="Simulate runtime overrun")
    parser.add_argument("--simulate-engine-fallback", action="store_true", help="Simulate unapproved engine fallback")
    parser.add_argument("--simulate-deployment-failure", action="store_true", help="Simulate remote deployment failure")
    parser.add_argument("--simulate-watchdog-crash", action="store_true", help="Simulate watchdog crash")
    parser.add_argument("--simulate-corrupt-checkpoint", action="store_true", help="Simulate corrupt checkpoint")

    return parser.parse_args()


def resolve_manifest_path(mode: ExecutionMode, manifest_arg: Optional[str]) -> str:
    if manifest_arg and os.path.exists(manifest_arg):
        return os.path.abspath(manifest_arg)
    
    # Locate relative to mission directory
    mission_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    manifests_dir = os.path.join(mission_dir, "manifests")
    
    if mode in [ExecutionMode.CALIBRATION, ExecutionMode.SIMULATION]:
        calib_manifest = os.path.join(manifests_dir, "calibration_10_manifest.json")
        if os.path.exists(calib_manifest):
            return calib_manifest
    elif mode == ExecutionMode.PRODUCTION:
        prod_manifest = os.path.join(manifests_dir, "primary_100_manifest.json")
        if os.path.exists(prod_manifest):
            return prod_manifest

    # Fallback to manifest_arg if provided even if relative
    if manifest_arg:
        return os.path.abspath(manifest_arg)
    
    raise ValueError(f"No manifest specified or found for mode {mode.value}")


def resolve_trusted_key(trusted_key_arg: Optional[str]) -> Optional[str]:
    if not trusted_key_arg:
        return None
    # If it's a file path, read content
    if os.path.exists(trusted_key_arg):
        with open(trusted_key_arg, "r") as f:
            return f.read().strip()
    return trusted_key_arg.strip()


def main() -> int:
    args = parse_args()

    mode_map = {
        "preflight": ExecutionMode.PREFLIGHT,
        "calibration": ExecutionMode.CALIBRATION,
        "production": ExecutionMode.PRODUCTION,
        "simulation": ExecutionMode.SIMULATION
    }
    mode = mode_map[args.mode]

    # Resolve default manifest if omitted
    try:
        manifest_path = resolve_manifest_path(mode, args.manifest)
    except Exception as e:
        print(f"[Launch Error] Security/Configuration Rejection: {e}")
        return 2

    # Resolve default budget ceiling if omitted
    max_cost = args.max_cost
    if max_cost is None:
        if mode in [ExecutionMode.CALIBRATION, ExecutionMode.SIMULATION]:
            max_cost = 0.35
        elif mode == ExecutionMode.PRODUCTION:
            max_cost = 2.50
        else:
            max_cost = 0.10

    trusted_key = resolve_trusted_key(args.trusted_public_key)

    try:
        runner = StateshiftProductionRunnerV10(
            experiment_id=args.experiment_id,
            manifest_path=manifest_path,
            authorization_path=args.authorization,
            mode=mode,
            pod_id=args.pod_id,
            ip=args.ip,
            port=args.port,
            ssh_key_path=args.ssh_key,
            local_data_dir=args.local_data_dir,
            remote_work_dir=args.remote_work_dir,
            max_cost_usd=max_cost,
            max_runtime_minutes=args.max_runtime,
            gpu_hourly_rate=args.gpu_rate,
            poll_interval_seconds=args.poll_interval,
            trusted_public_key_b64=trusted_key,
            allow_test_key_for_testing=args.allow_test_key,
            simulate_records=args.simulate_records,
            simulate_spend_usd=args.simulate_spend,
            simulate_corrupt_dataset=args.simulate_corrupt_dataset,
            simulate_unconfirmed_termination=args.simulate_unconfirmed_termination,
            simulate_sftp_failure=args.simulate_sftp_failure,
            simulate_ssh_disconnect=args.simulate_ssh_disconnect,
            simulate_runtime_overrun=args.simulate_runtime_overrun,
            simulate_engine_fallback=args.simulate_engine_fallback,
            simulate_deployment_failure=args.simulate_deployment_failure,
            simulate_watchdog_crash=args.simulate_watchdog_crash,
            simulate_corrupt_checkpoint=args.simulate_corrupt_checkpoint,
            resume=args.resume
        )
    except (ValueError, PermissionError, SecurityError if "SecurityError" in globals() else Exception) as exc:
        print(f"[Launch Error] Security/Configuration Rejection during initialization: {exc}")
        return 2

    print(f"\n=======================================================")
    print(f" StateShift Launch Initiated: {args.experiment_id}")
    print(f" Mode: {mode.value.upper()} | Manifest: {os.path.basename(manifest_path)}")
    print(f" Budget Ceiling: ${max_cost:.2f} USD")
    print(f"=======================================================\n")

    try:
        success = runner.run()
        if success:
            print(f"\n[Launch Success] Execution {args.experiment_id} completed with state {runner.state.value}.")
            print(f"Verified Receipt: {runner.receipt_file}")
            print(f"Local Dataset: {runner.local_dataset_file}")
            return 0
        else:
            print(f"\n[Launch Failure] Execution {args.experiment_id} failed with state {runner.state.value}.")
            # Check if failure was due to security/authorization rejection
            if runner.state in [ProductionState.INTEGRITY_FAILURE, ProductionState.CREATED]:
                return 2
            if "REJECTED" in runner.state.value:
                return 2
            return 1
    except Exception as exc:
        print(f"\n[Launch Unhandled Exception] Execution aborted: {exc}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

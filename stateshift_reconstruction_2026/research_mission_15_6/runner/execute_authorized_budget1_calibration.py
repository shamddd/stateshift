#!/usr/bin/env python3
"""
StateShift: Authorized $1 GPU Calibration Execution Orchestrator
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)
Author: Sham Satish Thakare (github.com/shamddd)

Strict Financial & Operational Bounds:
- Cloud Provider: RunPod
- Compute: Exactly ONE Secure Cloud RTX 4090 (24 GB VRAM)
- Model: Qwen/Qwen2.5-Math-7B-Instruct @ ef9926d75ab1d54532f6a30dd5e760355eb9aa4d
- Manifest: Frozen 10 Requests (SHA-256: f6c2ed07a50e5d4cec5ff4f24c5c7ef0355841fcec39b3b9d8b6d86385cb0de6)
- Planned Spending Ceiling: $1.0000 USD
- Emergency Tripwire: $0.7000 USD
- Target Balance Reserve: $0.3200 USD
- Maximum Wall-Clock Lifetime: 45.0 Minutes
- Invariants: Single-attempt invariant (0 replacement pods), supervisor-first, fail-closed relocking.
"""

import os
import sys
import time
import json
import base64
import hashlib
import traceback
import subprocess
import urllib.request
from typing import Dict, Any, Optional, Tuple

# Set workspace root
REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

import runpod
import paramiko
from cryptography.hazmat.primitives import serialization
from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    FROZEN_CALIBRATION_MANIFEST_SHA256,
    PINNED_MODEL_ID,
    PINNED_MODEL_REVISION
)
from research_mission_15_6.deployment.supervisor_first_provisioner import (
    SupervisorFirstProvisioner,
    ProvisioningSecurityError
)
from research_mission_15_6.auth.execution_lock import is_cloud_execution_locked

LOCK_FILE = os.path.join(REPO_DIR, ".cloud_execution_locked")
LOCK_FILE_BAK = os.path.join(REPO_DIR, ".cloud_execution_locked.bak")
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")
SSH_PUB_PATH = os.path.expanduser("~/.ssh/id_ed25519.pub")

EXPERIMENT_ID = "stateshift_calib_b1_01"
SESSION_ID = f"sess_b1_{int(time.time())}"
LOCAL_DATA_DIR = os.path.join(REPO_DIR, "data/primary_run")
AUTH_PATH = os.path.join(LOCAL_DATA_DIR, "session_auth_calib_b1.json")
PUBKEY_PATH = os.path.join(LOCAL_DATA_DIR, "operator_pubkey.txt")
GENERATIONS_OUT = os.path.join(LOCAL_DATA_DIR, "stateshift_calib_b1_01_generations.jsonl")
RECONCILIATION_OUT = os.path.join(LOCAL_DATA_DIR, "calibration_reconciliation_b1.json")
TIMELINE_LOG = os.path.join(LOCAL_DATA_DIR, "gpu_session_timeline_events.jsonl")

# Load RunPod API Key
import tomli
with open(os.path.expanduser("~/.runpod/config.toml"), "rb") as f:
    cfg = tomli.load(f)
API_KEY = cfg.get("default", {}).get("api_key", "")
if not API_KEY:
    raise RuntimeError("RunPod API key missing from ~/.runpod/config.toml")

os.environ["RUNPOD_API_KEY"] = API_KEY
runpod.api_key = API_KEY
GRAPHQL_ENDPOINT = f"https://api.runpod.io/graphql?api_key={API_KEY}"


def log_timeline_event(event_type: str, details: Dict[str, Any]):
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    entry = {
        "timestamp_utc": time.time(),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": event_type,
        "details": details
    }
    with open(TIMELINE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{entry['iso_time']}] {event_type}: {details}")


def query_runpod_account() -> Dict[str, Any]:
    query = """
    query {
      myself {
        id
        email
        clientBalance
        currentSpendPerHr
        pods {
          id
          name
          desiredStatus
          costPerHr
        }
        networkVolumes {
          id
          name
          size
        }
      }
    }
    """
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    )
    with urllib.request.urlopen(req, timeout=25.0) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        if "errors" in data:
            raise RuntimeError(f"GraphQL Errors: {data['errors']}")
        return data.get("data", {}).get("myself", {})


def lock_cloud_execution():
    """Fail-closed relocking."""
    os.environ["STATE_SHIFT_CLOUD_EXECUTION_DISABLED"] = "1"
    if os.path.exists(LOCK_FILE_BAK) and not os.path.exists(LOCK_FILE):
        os.replace(LOCK_FILE_BAK, LOCK_FILE)
    elif not os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "locked": True,
                "reason": "Calibration session completed. Fail-closed relock active.",
                "timestamp_utc": time.time()
            }, f, indent=2)
    print("[Safety Guard] Cloud execution lock RE-ENGAGED.")


def unlock_cloud_execution_for_session():
    """Unlocks execution strictly for this single authorized process."""
    os.environ["STATE_SHIFT_CLOUD_EXECUTION_DISABLED"] = "0"
    if os.path.exists(LOCK_FILE):
        os.replace(LOCK_FILE, LOCK_FILE_BAK)
    print("[Safety Guard] Cloud execution unlocked for authorized session.")


def main():
    print("=" * 80)
    print("  STATESHIFT: AUTHORIZED $1 GPU CALIBRATION EXECUTION")
    print("=" * 80)
    log_timeline_event("SESSION_INITIATED", {"experiment_id": EXPERIMENT_ID, "session_id": SESSION_ID})

    # Step 1: Pre-Execution Verification Gate
    print("\n[Phase G: Pre-Provisioning Gate Verification]")
    acct = query_runpod_account()
    initial_balance = float(acct.get("clientBalance", 0.0))
    active_pods = acct.get("pods") or []
    active_vols = acct.get("networkVolumes") or []

    print(f"User ID:                {acct.get('id')}")
    print(f"Current Live Balance:   ${initial_balance:.4f} USD")
    print(f"Active / Stopped Pods:  {len(active_pods)}")
    print(f"Network Storage Volumes:{len(active_vols)}")

    if initial_balance < 0.32:
        raise RuntimeError(f"Solvency check failed: Balance ${initial_balance:.4f} < $0.32 reserve floor.")
    if len(active_pods) > 0:
        raise RuntimeError(f"Safety violation: {len(active_pods)} pods already running/stopped!")
    if len(active_vols) > 0:
        raise RuntimeError(f"Safety violation: {len(active_vols)} network volumes already exist!")

    # Verify authorization document
    with open(AUTH_PATH, "r", encoding="utf-8") as f:
        auth_doc = json.load(f)
    pub_b64 = open(PUBKEY_PATH, "r", encoding="utf-8").read().strip()

    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub_b64)
    valid, auth_msg = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id=EXPERIMENT_ID,
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_CALIBRATION_MANIFEST_SHA256,
        active_mode="CALIBRATION"
    )
    if not valid:
        raise RuntimeError(f"Cryptographic authorization check failed: {auth_msg}")
    print(f"Cryptographic Authorization: VERIFIED VALID ({auth_msg})")

    # Step 2: Initialize Supervisor-First Provisioner
    provisioner = SupervisorFirstProvisioner(
        experiment_id=EXPERIMENT_ID,
        session_id=SESSION_ID,
        local_data_dir=LOCAL_DATA_DIR,
        max_cost_usd=1.00,
        emergency_trigger_usd=0.70,
        account_floor_usd=0.32,
        gpu_hourly_rate=0.89,
        active_mode="CALIBRATION",
        manifest_sha256=FROZEN_CALIBRATION_MANIFEST_SHA256,
        authorization_doc=auth_doc,
        authorization_path=AUTH_PATH,
        trusted_public_key_b64=pub_b64
    )

    # Step 3: Spawn Pre-Provision Supervisor Daemon
    print("\n[Phase 1: Spawning Independent Financial Supervisor Daemon]")
    supervisor_ready = provisioner.spawn_preprovision_supervisor(timeout_seconds=20.0)
    if not supervisor_ready:
        raise RuntimeError("Independent financial watchdog failed to publish readiness receipt!")
    print(f"Independent Financial Watchdog: READY (PID: {provisioner.watchdog_pid})")
    log_timeline_event("SUPERVISOR_READY", {"watchdog_pid": provisioner.watchdog_pid})

    # Step 4: Unlock execution strictly for provisioning
    unlock_cloud_execution_for_session()

    pod_id = None
    created_at_time = time.time()
    t_monotonic_start = time.monotonic()
    hardware_info = {}
    completed_generations = 0

    try:
        # Step 5: Provision Exactly ONE Pod (Enforcing Single-Attempt Invariant)
        print("\n[Phase 2: Single-Attempt Cloud Provisioning on RunPod Secure Cloud]")
        pub_key_str = open(SSH_PUB_PATH).read().strip()

        def do_create_pod() -> str:
            spec = runpod.create_pod(
                name="stateshift-calib-rtx4090",
                image_name="runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
                gpu_type_id="NVIDIA GeForce RTX 4090",
                cloud_type="SECURE",
                support_public_ip=True,
                start_ssh=True,
                gpu_count=1,
                volume_in_gb=0,              # Strict: ZERO paid persistent storage
                container_disk_in_gb=40,     # 40GB ephemeral disk
                ports="22/tcp",
                env={"PUBLIC_KEY": pub_key_str}
            )
            pid = spec.get("id")
            if not pid:
                raise RuntimeError(f"RunPod create_pod returned invalid response: {spec}")
            return pid

        pod_id = provisioner.provision_single_pod(create_pod_fn=do_create_pod)
        created_at_time = time.time()
        print(f"Pod provisioned successfully! Pod ID: {pod_id}")
        log_timeline_event("POD_PROVISIONED", {"pod_id": pod_id})

        # Step 6: Await RUNNING Status and Public SSH Endpoint
        print("\nAwaiting pod RUNNING status and SSH endpoint allocation...")
        ssh_ip = None
        ssh_port = None
        for attempt in range(60):
            time.sleep(3.0)
            elapsed_m = (time.monotonic() - t_monotonic_start) / 60.0
            if elapsed_m > 45.0:
                raise TimeoutError("Hard 45-minute wall-clock limit exceeded during pod boot!")

            p_info = runpod.get_pod(pod_id)
            if not p_info:
                continue
            status = p_info.get("desiredStatus")
            runtime = p_info.get("runtime") or {}
            ports = runtime.get("ports") or []
            print(f"  Check {attempt+1:02d}: status={status}, ports={len(ports)} (elapsed: {elapsed_m:.1f}m)")

            for p in ports:
                if p.get("privatePort") == 22:
                    ssh_ip = p.get("ip")
                    ssh_port = p.get("publicPort")
                    break

            if status == "RUNNING" and ssh_ip and ssh_port:
                print(f"Pod is actively RUNNING! SSH Endpoint: {ssh_ip}:{ssh_port}")
                log_timeline_event("POD_RUNNING", {"pod_id": pod_id, "ip": ssh_ip, "port": ssh_port})
                break
        else:
            raise TimeoutError("Pod failed to enter RUNNING status with SSH ports assigned within 180s.")

        # Step 7: SSH Connect & Hardware Audit
        print("\n[Phase 3: Hardware Audit & Staging Environment over SSH]")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.Ed25519Key.from_private_key_file(SSH_KEY_PATH)

        for ssh_att in range(30):
            try:
                ssh.connect(hostname=ssh_ip, port=ssh_port, username="root", pkey=pkey, timeout=10)
                print("SSH connection established successfully!")
                break
            except Exception as e:
                print(f"  Waiting for SSH daemon (attempt {ssh_att+1}): {e}")
                time.sleep(3.0)
        else:
            raise ConnectionError(f"Could not connect via SSH to {ssh_ip}:{ssh_port}")

        def run_ssh(cmd, timeout=300):
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            out_str = stdout.read().decode("utf-8").strip()
            err_str = stderr.read().decode("utf-8").strip()
            return exit_code, out_str, err_str

        # Hardware verification
        code, gpu_out, _ = run_ssh("nvidia-smi --query-gpu=gpu_name,memory.total,driver_version --format=csv,noheader")
        print(f"NVIDIA-SMI Hardware Audit: {gpu_out}")
        if "4090" not in gpu_out:
            raise RuntimeError(f"Hardware mismatch: Expected RTX 4090, got: {gpu_out}")

        code, df_out, _ = run_ssh("df -h /workspace | tail -1")
        print(f"Workspace Storage: {df_out}")

        code, py_out, _ = run_ssh("python3 --version")
        print(f"Remote Python: {py_out}")

        hardware_info = {
            "gpu_hardware": gpu_out,
            "workspace_disk": df_out,
            "remote_python": py_out,
            "ssh_ip": ssh_ip,
            "ssh_port": ssh_port
        }
        log_timeline_event("HARDWARE_AUDIT_VERIFIED", hardware_info)

        # Step 8: Remote Dependencies & Directory Setup
        print("\nInstalling lightweight dependencies (transformers<4.47, accelerate, sentencepiece)...")
        code, _, pip_err = run_ssh("pip install -q 'transformers<4.47' accelerate sentencepiece protobuf", timeout=180)
        if code != 0:
            print(f"pip install notice (code {code}): {pip_err}")

        remote_work_dir = "/workspace/stateshift"
        run_ssh(f"mkdir -p {remote_work_dir}/manifests {remote_work_dir}/runner {remote_work_dir}/data {remote_work_dir}/logs")

        # Step 9: SFTP Upload of Manifest & Runner
        print("\nUploading frozen calibration manifest and remote runner via SFTP...")
        sftp = ssh.open_sftp()
        local_cal_manifest = os.path.join(REPO_DIR, "research_mission_15_6/manifests/calibration_10_manifest.json")
        local_runner = os.path.join(REPO_DIR, "research_mission_15_6/runner/remote_experiment_runner.py")

        sftp.put(local_cal_manifest, f"{remote_work_dir}/manifests/calibration_10_manifest.json")
        sftp.put(local_cal_manifest, f"{remote_work_dir}/manifests/primary_100_manifest.json")
        sftp.put(local_runner, f"{remote_work_dir}/runner/remote_experiment_runner.py")

        # Pre-cache script for Qwen2.5-Math-7B-Instruct @ ef9926d75ab1d54532f6a30dd5e760355eb9aa4d
        cache_script = f"""import time, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

m = '{PINNED_MODEL_ID}'
rev = '{PINNED_MODEL_REVISION}'
print('Pre-caching tokenizer...')
tok = AutoTokenizer.from_pretrained(m, revision=rev, trust_remote_code=True)
print('Pre-caching model weights (bfloat16)...')
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(m, revision=rev, torch_dtype=torch.bfloat16, device_map='auto', trust_remote_code=True)
print(f'Model weights cached successfully in {{time.time()-t0:.2f}}s!')
"""
        with sftp.file(f"{remote_work_dir}/cache_model.py", "w") as f:
            f.write(cache_script)
        sftp.close()

        print(f"Pre-caching {PINNED_MODEL_ID} @ {PINNED_MODEL_REVISION}...")
        t_cache_0 = time.time()
        code, dl_out, dl_err = run_ssh(f"python3 {remote_work_dir}/cache_model.py", timeout=420)
        cache_duration = time.time() - t_cache_0
        print(f"Model Pre-cache Output ({cache_duration:.1f}s):\n{dl_out}")
        if dl_err:
            print(f"Model Pre-cache Stderr:\n{dl_err}")
        hardware_info["cache_duration_sec"] = cache_duration
        log_timeline_event("MODEL_PRECACHED", {"duration_sec": cache_duration})

        # Step 10: Launch Detached Remote Experiment Runner
        print("\n[Phase 4: Launching Remote Experiment Runner for 10 Requests]")
        remote_out = f"{remote_work_dir}/data/output.jsonl"
        remote_rec = f"{remote_work_dir}/logs/record.json"
        remote_hb = f"{remote_work_dir}/logs/heartbeat.json"
        remote_log = f"{remote_work_dir}/logs/runner.log"

        launch_cmd = (
            f"nohup python3 {remote_work_dir}/runner/remote_experiment_runner.py "
            f"--manifest {remote_work_dir}/manifests/calibration_10_manifest.json "
            f"--output {remote_out} "
            f"--record {remote_rec} "
            f"--heartbeat {remote_hb} "
            f"--experiment-id {EXPERIMENT_ID} "
            f"--model-id {PINNED_MODEL_ID} "
            f"--model-revision {PINNED_MODEL_REVISION} "
            f"--limit-requests 10 "
            f"--temperature 0.0 "
            f"--max-tokens 768 "
            f"--seed 42 "
            f"< /dev/null > {remote_log} 2>&1 &"
        )
        code, _, _ = run_ssh(launch_cmd)
        print("Remote experiment runner dispatched in background.")
        log_timeline_event("REMOTE_RUNNER_DISPATCHED", {"command": launch_cmd})

        # Step 11: Real-Time In-Flight Supervision & Incremental Ingestion Loop
        print("\n[Phase 5: In-Flight Supervision & Incremental Dataset Ingestion]")
        sftp = ssh.open_sftp()
        last_seen_lines = 0
        local_records = []

        if os.path.exists(GENERATIONS_OUT):
            os.remove(GENERATIONS_OUT)

        while True:
            time.sleep(4.0)
            elapsed_min = (time.monotonic() - t_monotonic_start) / 60.0
            
            # Check hard runtime deadline (45 min)
            if elapsed_min >= 45.0:
                print(f"[KILL] Hard 45.0-minute limit exceeded: {elapsed_min:.1f}m!")
                log_timeline_event("LIMIT_EXCEEDED_RUNTIME", {"elapsed_min": elapsed_min})
                break

            # Check spend tripwire ($0.70)
            cur_acct = query_runpod_account()
            cur_bal = float(cur_acct.get("clientBalance", 0.0))
            spent_usd = initial_balance - cur_bal
            if spent_usd >= 0.70:
                print(f"[KILL] Emergency spend tripwire ($0.70) exceeded: spent ${spent_usd:.4f} USD!")
                log_timeline_event("LIMIT_EXCEEDED_SPEND", {"spent_usd": spent_usd})
                break

            # Poll remote output file
            try:
                with sftp.file(remote_out, "r") as rf:
                    lines = rf.readlines()
                current_count = len(lines)
                if current_count > last_seen_lines:
                    for line_idx in range(last_seen_lines, current_count):
                        raw_line = lines[line_idx].strip()
                        if raw_line:
                            record = json.loads(raw_line)
                            local_records.append(record)
                            with open(GENERATIONS_OUT, "a", encoding="utf-8") as wf:
                                wf.write(raw_line + "\n")
                                wf.flush()
                                os.fsync(wf.fileno())
                            print(f"  [Progress] Request {record.get('request_id')} completed (Tokens: {record.get('generated_tokens', record.get('total_tokens'))}, Condition: {record.get('condition_code')})")
                    last_seen_lines = current_count
                    completed_generations = current_count
                    log_timeline_event("RECORDS_INGESTED", {"completed": completed_generations, "spent_usd": spent_usd, "elapsed_min": elapsed_min})
            except IOError:
                # File not created yet
                pass

            if completed_generations >= 10:
                print("\nAll 10 authentic calibration requests completed successfully!")
                log_timeline_event("ALL_REQUESTS_COMPLETED", {"total": 10})
                break

            # Check if remote runner process died prematurely
            code, ps_out, _ = run_ssh("pgrep -f remote_experiment_runner.py")
            if code != 0 and completed_generations < 10:
                # Process died
                print("Remote experiment runner process exited before 10 requests completed.")
                code, runner_log_tail, _ = run_ssh(f"tail -n 30 {remote_log}")
                print(f"Runner log:\n{runner_log_tail}")
                log_timeline_event("REMOTE_RUNNER_PREMATURE_EXIT", {"runner_log": runner_log_tail})
                break

        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"\n[Execution Exception] {e}")
        traceback.print_exc()
        log_timeline_event("EXECUTION_EXCEPTION", {"error": str(e), "traceback": traceback.format_exc()})

    finally:
        # Step 12: Authoritative Pod Teardown & Multi-Pass Destruction Verification
        print("\n" + "=" * 80)
        print("  PHASE 6: AUTHORITATIVE POD TEARDOWN & DESTRUCTION VERIFICATION")
        print("=" * 80)

        t_end = time.time()
        elapsed_sec = t_end - created_at_time

        if pod_id:
            print(f"Dispatching authoritative teardown for Pod ID: {pod_id}...")
            log_timeline_event("TEARDOWN_DISPATCHED", {"pod_id": pod_id})
            
            try:
                # Primary teardown via supervisor provisioner
                term_ok, term_msg = provisioner.emergency_teardown(reason="Calibration completed or terminated")
                print(f"Provisioner teardown response: {term_ok} ({term_msg})")
            except Exception as te:
                print(f"Provisioner teardown error: {te}")

            # Backup multi-pass authoritative provider verification
            destruction_confirmed = False
            for check in range(30):
                time.sleep(2.0)
                try:
                    p = runpod.get_pod(pod_id)
                    if not p or p.get("desiredStatus") in ["TERMINATED", "DELETED", None]:
                        destruction_confirmed = True
                        print(f"Pod {pod_id} destruction CONFIRMED by RunPod API.")
                        break
                    print(f"  Check {check+1:02d}: Pod still present with status '{p.get('desiredStatus')}'...")
                    # Re-issue terminate mutation if needed
                    runpod.terminate_pod(pod_id)
                except Exception as ex:
                    # API error or not found
                    if "not found" in str(ex).lower():
                        destruction_confirmed = True
                        print(f"Pod {pod_id} confirmed NOT_FOUND by RunPod API.")
                        break
            
            log_timeline_event("DESTRUCTION_VERIFICATION", {"pod_id": pod_id, "confirmed": destruction_confirmed})

        # Step 13: Stop Watchdog Process
        if provisioner.watchdog_process and provisioner.watchdog_process.poll() is None:
            try:
                provisioner.watchdog_process.terminate()
                provisioner.watchdog_process.wait(timeout=3.0)
                print("Watchdog daemon stopped cleanly.")
            except Exception:
                pass

        # Step 14: Relock Cloud Execution
        lock_cloud_execution()

        # Step 15: Post-Execution Financial Reconciliation
        print("\n" + "=" * 80)
        print("  PHASE 7: FINAL FINANCIAL RECONCILIATION AUDIT")
        print("=" * 80)
        time.sleep(3.0)
        post_acct = query_runpod_account()
        final_balance = float(post_acct.get("clientBalance", 0.0))
        final_pods = post_acct.get("pods") or []
        final_vols = post_acct.get("networkVolumes") or []
        net_spend = initial_balance - final_balance

        print(f"Initial RunPod Balance:   ${initial_balance:.4f} USD")
        print(f"Final RunPod Balance:     ${final_balance:.4f} USD")
        print(f"Net Cloud Expenditure:    ${net_spend:.4f} USD")
        print(f"Planned Spending Ceiling: $1.0000 USD (Complied: {net_spend <= 1.00})")
        print(f"Emergency Shutdown Trigger:$0.7000 USD (Complied: {net_spend <= 0.70})")
        print(f"Target Preservation Reserve: $0.3200 USD (Final Balance: ${final_balance:.4f} USD)")
        print(f"Total Session Duration:   {elapsed_sec:.1f}s ({elapsed_sec/60:.2f} minutes)")
        print(f"Remaining Active Pods:    {len(final_pods)}")
        print(f"Remaining Volumes:        {len(final_vols)}")
        print(f"Completed Generations:    {completed_generations} / 10")
        print("=" * 80)

        recon_data = {
            "experiment_id": EXPERIMENT_ID,
            "session_id": SESSION_ID,
            "pod_id": pod_id,
            "gpu_hardware": hardware_info.get("gpu_hardware", "NVIDIA RTX 4090"),
            "initial_balance_usd": initial_balance,
            "final_balance_usd": final_balance,
            "net_spend_usd": net_spend,
            "elapsed_seconds": elapsed_sec,
            "elapsed_minutes": elapsed_sec / 60.0,
            "completed_generations": completed_generations,
            "spend_within_ceiling": net_spend <= 1.00,
            "spend_within_trigger": net_spend <= 0.70,
            "final_pods_count": len(final_pods),
            "final_volumes_count": len(final_vols),
            "destruction_confirmed": destruction_confirmed if 'destruction_confirmed' in locals() else True,
            "hardware_info": hardware_info
        }

        with open(RECONCILIATION_OUT, "w", encoding="utf-8") as f:
            json.dump(recon_data, f, indent=2)
        print(f"Financial reconciliation ledger saved to: {RECONCILIATION_OUT}")
        log_timeline_event("SESSION_FINALIZED", recon_data)


if __name__ == "__main__":
    main()

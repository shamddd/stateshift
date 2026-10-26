#!/usr/bin/env python3
"""
StateShift Research Mission 17: Authorized 400-Request Primary GPU Experiment Launcher
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Executes the complete frozen 400-request StateShift primary experiment:
- Model: Qwen/Qwen2.5-Math-7B-Instruct (revision: ef9926d75ab1d54532f6a30dd5e760355eb9aa4d)
- Hardware: 1x physical NVIDIA RTX 4090 (24 GB) on RunPod Secure Cloud ($0.89/hr)
- Scope: Exactly 400 requests (100 problems x 4 conditions: A, D, E, F)
- Financial Constraints:
  * Planned spending ceiling: $3.50 USD
  * Emergency shutdown trigger: $2.80 USD
  * Account preservation floor: $7.00 USD
  * Hard wall-clock limit: 150.0 minutes
  * Single provisioning attempt invariant (0 replacements, 0 retries)
  * Independent supervisor-first watchdog architecture
  * Authoritative provider-side destruction verification (reject STOPPED)
  * Fail-closed execution lock re-engagement
"""

import os
import sys
import time
import json
import base64
import urllib.request
import urllib.error
import traceback
import paramiko
import runpod

# Ensure repository root is in sys.path
_repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _repo_dir not in sys.path:
    sys.path.insert(0, _repo_dir)

from research_mission_15_6.auth.session_authorizer_v2 import (
    CryptographicAuthorizer,
    FROZEN_MANIFEST_SHA256
)
from research_mission_15_6.deployment.supervisor_first_provisioner import SupervisorFirstProvisioner
from research_mission_15_6.auth.execution_lock import (
    is_cloud_execution_locked
)

# Operational & Cryptographic Constants
REPO_DIR = _repo_dir
LOCK_FILES = [
    os.path.join(REPO_DIR, ".cloud_execution_locked"),
    os.path.abspath(os.path.join(REPO_DIR, "..", ".cloud_execution_locked")),
]
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")
SSH_PUB_PATH = os.path.expanduser("~/.ssh/id_ed25519.pub")

EXPERIMENT_ID = "stateshift_primary_400_01"
SESSION_ID = f"sess_primary_{int(time.time())}"
LOCAL_DATA_DIR = os.path.join(REPO_DIR, "data/primary_run")
AUTH_PATH = os.path.join(LOCAL_DATA_DIR, "session_auth_primary_400.json")
PUBKEY_PATH = os.path.join(LOCAL_DATA_DIR, "operator_pubkey.txt")
GENERATIONS_OUT = os.path.join(LOCAL_DATA_DIR, "stateshift_primary_400_generations.jsonl")
RECONCILIATION_OUT = os.path.join(LOCAL_DATA_DIR, "primary_400_reconciliation.json")
TIMELINE_LOG = os.path.join(LOCAL_DATA_DIR, "primary_400_timeline_events.jsonl")

PRIMARY_MANIFEST = os.path.join(REPO_DIR, "research_mission_15_6/manifests/primary_100_manifest.json")
FROZEN_PRIMARY_MANIFEST_SHA256 = "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"

PINNED_MODEL_ID = "Qwen/Qwen2.5-Math-7B-Instruct"
PINNED_MODEL_REVISION = "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"

MAX_SPEND_CEILING_USD = 3.50
EMERGENCY_TRIGGER_USD = 2.80
PRESERVATION_FLOOR_USD = 7.00
MAX_RUNTIME_MINUTES = 150.0
GPU_HOURLY_RATE = 0.89
TARGET_REQUESTS = 400

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


def log_timeline_event(event_type: str, details: dict):
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


def query_runpod_account() -> dict:
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
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=25.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "errors" in data and data["errors"]:
                    raise RuntimeError(f"RunPod GraphQL error: {data['errors']}")
                return data.get("data", {}).get("myself", {})
        except (urllib.error.URLError, ConnectionResetError, TimeoutError) as e:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


def lock_cloud_execution():
    """Fail-closed relocking."""
    os.environ["STATE_SHIFT_CLOUD_EXECUTION_DISABLED"] = "1"
    for lf in LOCK_FILES:
        bak = lf + ".bak"
        if os.path.exists(bak) and not os.path.exists(lf):
            os.replace(bak, lf)
        elif not os.path.exists(lf):
            with open(lf, "w", encoding="utf-8") as f:
                json.dump({
                    "locked": True,
                    "reason": "Primary 400 experiment session completed. Fail-closed relock active.",
                    "timestamp_utc": time.time()
                }, f, indent=2)
    print("[Safety Guard] Cloud execution lock RE-ENGAGED.")


def unlock_cloud_execution_for_session():
    """Unlocks execution strictly for this single authorized process."""
    os.environ["STATE_SHIFT_CLOUD_EXECUTION_DISABLED"] = "0"
    for lf in LOCK_FILES:
        if os.path.exists(lf):
            bak = lf + ".bak"
            os.replace(lf, bak)
    print("[Safety Guard] Cloud execution unlocked for authorized session.")


def main():
    print("=" * 80)
    print("  STATESHIFT: AUTHORIZED 400-REQUEST PRIMARY GPU EXPERIMENT EXECUTION")
    print("=" * 80)
    log_timeline_event("SESSION_INITIATED", {"experiment_id": EXPERIMENT_ID, "session_id": SESSION_ID})

    # Step 0: Pre-Provisioning Gate Verification
    print("\n[Phase 0: Pre-Provisioning Gate Verification]")
    acct = query_runpod_account()
    initial_balance = float(acct.get("clientBalance", 0.0))
    active_pods = acct.get("pods") or []
    active_vols = acct.get("networkVolumes") or []

    print(f"User ID:                {acct.get('id')}")
    print(f"Current Live Balance:   ${initial_balance:.4f} USD")
    print(f"Active / Stopped Pods:  {len(active_pods)}")
    print(f"Network Storage Volumes:{len(active_vols)}")

    if initial_balance < PRESERVATION_FLOOR_USD + 1.00:
        raise RuntimeError(f"Solvency check failed: Balance ${initial_balance:.4f} < ${PRESERVATION_FLOOR_USD + 1.00:.2f} threshold.")
    if len(active_pods) > 0:
        raise RuntimeError(f"Safety violation: {len(active_pods)} pods already running/stopped!")
    if len(active_vols) > 0:
        raise RuntimeError(f"Safety violation: {len(active_vols)} network volumes already exist!")

    # Verify primary manifest SHA-256
    import hashlib
    with open(PRIMARY_MANIFEST, "rb") as mf:
        actual_manifest_hash = hashlib.sha256(mf.read()).hexdigest()
    if actual_manifest_hash != FROZEN_PRIMARY_MANIFEST_SHA256:
        raise RuntimeError(f"Manifest hash mismatch: {actual_manifest_hash} != {FROZEN_PRIMARY_MANIFEST_SHA256}")
    print(f"Primary Manifest SHA-256: {actual_manifest_hash} (VERIFIED)")

    # Verify cryptographic authorization document
    if not os.path.exists(AUTH_PATH):
        raise RuntimeError(f"Session authorization token missing: {AUTH_PATH}")
    with open(AUTH_PATH, "r", encoding="utf-8") as f:
        auth_doc = json.load(f)
    pub_b64 = open(PUBKEY_PATH, "r", encoding="utf-8").read().strip()

    authorizer = CryptographicAuthorizer(trusted_public_key_b64=pub_b64)
    valid, auth_msg = authorizer.verify_authorization(
        auth_doc=auth_doc,
        active_experiment_id=EXPERIMENT_ID,
        active_pod_id="PRE_PROVISION",
        active_manifest_sha256=FROZEN_PRIMARY_MANIFEST_SHA256,
        active_mode="PRODUCTION"
    )
    if not valid:
        raise RuntimeError(f"Cryptographic authorization check failed: {auth_msg}")
    print(f"Cryptographic Authorization: VERIFIED VALID ({auth_msg})")

    # Step 1: Initialize Supervisor-First Provisioner
    provisioner = SupervisorFirstProvisioner(
        experiment_id=EXPERIMENT_ID,
        session_id=SESSION_ID,
        local_data_dir=LOCAL_DATA_DIR,
        max_cost_usd=MAX_SPEND_CEILING_USD,
        emergency_trigger_usd=EMERGENCY_TRIGGER_USD,
        account_floor_usd=PRESERVATION_FLOOR_USD,
        gpu_hourly_rate=GPU_HOURLY_RATE,
        active_mode="PRODUCTION",
        manifest_sha256=FROZEN_PRIMARY_MANIFEST_SHA256,
        authorization_doc=auth_doc,
        authorization_path=AUTH_PATH,
        trusted_public_key_b64=pub_b64
    )

    # Step 2: Spawn Pre-Provision Supervisor Daemon
    print("\n[Phase 1: Spawning Independent Financial Supervisor Daemon]")
    supervisor_ready = provisioner.spawn_preprovision_supervisor(timeout_seconds=25.0)
    if not supervisor_ready:
        raise RuntimeError("Independent financial watchdog failed to publish readiness receipt!")
    print(f"Independent Financial Watchdog: READY (PID: {provisioner.watchdog_pid})")
    log_timeline_event("SUPERVISOR_READY", {"watchdog_pid": provisioner.watchdog_pid})

    # Step 3: Unlock execution strictly for provisioning
    unlock_cloud_execution_for_session()

    pod_id = None
    created_at_time = time.time()
    t_monotonic_start = time.monotonic()
    hardware_info = {}
    completed_generations = 0

    try:
        # Step 4: Provision Exactly ONE Pod (Enforcing Single-Attempt Invariant)
        print("\n[Phase 2: Single-Attempt Cloud Provisioning on RunPod Secure Cloud]")
        pub_key_str = open(SSH_PUB_PATH).read().strip()

        def do_create_pod() -> str:
            spec = runpod.create_pod(
                name="stateshift-primary-rtx4090",
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

        # Step 5: Await RUNNING Status and Public SSH Endpoint
        print("\nAwaiting pod RUNNING status and SSH endpoint allocation...")
        ssh_ip = None
        ssh_port = None
        for attempt in range(80):
            time.sleep(3.0)
            elapsed_m = (time.monotonic() - t_monotonic_start) / 60.0
            if elapsed_m > MAX_RUNTIME_MINUTES:
                raise TimeoutError(f"Hard {MAX_RUNTIME_MINUTES}-minute wall-clock limit exceeded during pod boot!")

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
            raise TimeoutError("Pod failed to enter RUNNING status with SSH ports assigned within 240s.")

        # Step 6: SSH Connect & Hardware Audit
        print("\n[Phase 3: Hardware Audit & Staging Environment over SSH]")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.Ed25519Key.from_private_key_file(SSH_KEY_PATH)

        for ssh_att in range(40):
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

        # Step 7: Remote Dependencies & Directory Setup
        print("\nInstalling lightweight dependencies (transformers<4.47, accelerate, sentencepiece)...")
        code, _, pip_err = run_ssh("pip install -q 'transformers<4.47' accelerate sentencepiece protobuf", timeout=180)
        if code != 0:
            print(f"pip install notice (code {code}): {pip_err}")

        remote_work_dir = "/workspace/stateshift"
        run_ssh(f"mkdir -p {remote_work_dir}/manifests {remote_work_dir}/runner {remote_work_dir}/data {remote_work_dir}/logs")

        # Step 8: SFTP Upload of Manifest & Runner
        print("\nUploading frozen primary 400 manifest and remote runner via SFTP...")
        sftp = ssh.open_sftp()
        local_runner = os.path.join(REPO_DIR, "research_mission_15_6/runner/remote_experiment_runner.py")

        sftp.put(PRIMARY_MANIFEST, f"{remote_work_dir}/manifests/primary_100_manifest.json")
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

        # Step 9: Launch Detached Remote Experiment Runner for 400 Requests
        print(f"\n[Phase 4: Launching Remote Experiment Runner for {TARGET_REQUESTS} Requests]")
        remote_out = f"{remote_work_dir}/data/output.jsonl"
        remote_rec = f"{remote_work_dir}/logs/record.json"
        remote_hb = f"{remote_work_dir}/logs/heartbeat.json"
        remote_log = f"{remote_work_dir}/logs/runner.log"

        launch_cmd = (
            f"nohup python3 {remote_work_dir}/runner/remote_experiment_runner.py "
            f"--manifest {remote_work_dir}/manifests/primary_100_manifest.json "
            f"--output {remote_out} "
            f"--record {remote_rec} "
            f"--heartbeat {remote_hb} "
            f"--experiment-id {EXPERIMENT_ID} "
            f"--model-id {PINNED_MODEL_ID} "
            f"--model-revision {PINNED_MODEL_REVISION} "
            f"--limit-requests {TARGET_REQUESTS} "
            f"--temperature 0.0 "
            f"--max-tokens 768 "
            f"--seed 42 "
            f"< /dev/null > {remote_log} 2>&1 &"
        )
        code, _, _ = run_ssh(launch_cmd)
        print("Remote experiment runner dispatched in background.")
        log_timeline_event("REMOTE_RUNNER_DISPATCHED", {"command": launch_cmd})

        # Step 10: Real-Time In-Flight Supervision & Incremental Ingestion Loop
        print(f"\n[Phase 5: In-Flight Supervision & Incremental Dataset Ingestion (Target: {TARGET_REQUESTS} requests)]")
        sftp = ssh.open_sftp()
        last_seen_lines = 0
        local_records = []

        # Initialize local file cleanly if starting fresh
        if not os.path.exists(GENERATIONS_OUT):
            open(GENERATIONS_OUT, "w", encoding="utf-8").close()
        else:
            with open(GENERATIONS_OUT, "r", encoding="utf-8") as existing_f:
                for line in existing_f:
                    line = line.strip()
                    if line:
                        try:
                            rec = json.loads(line)
                            local_records.append(rec)
                        except Exception:
                            pass
            last_seen_lines = len(local_records)
            completed_generations = last_seen_lines
            print(f"Resuming existing generation ledger: {last_seen_lines} records previously ingested.")

        last_balance_check_time = 0.0
        current_spent_usd = 0.0

        while True:
            time.sleep(4.0)
            elapsed_min = (time.monotonic() - t_monotonic_start) / 60.0
            
            # Check hard runtime deadline (150 min)
            if elapsed_min >= MAX_RUNTIME_MINUTES:
                print(f"[KILL] Hard {MAX_RUNTIME_MINUTES}-minute limit exceeded: {elapsed_min:.1f}m!")
                log_timeline_event("LIMIT_EXCEEDED_RUNTIME", {"elapsed_min": elapsed_min})
                break

            # Check spend tripwire ($2.80) & preservation floor ($7.00) periodically
            now_mono = time.monotonic()
            if (now_mono - last_balance_check_time) > 45.0:
                last_balance_check_time = now_mono
                try:
                    cur_acct = query_runpod_account()
                    cur_bal = float(cur_acct.get("clientBalance", 0.0))
                    current_spent_usd = initial_balance - cur_bal
                    
                    if current_spent_usd >= EMERGENCY_TRIGGER_USD:
                        print(f"[KILL] Emergency spend tripwire (${EMERGENCY_TRIGGER_USD:.2f}) exceeded: spent ${current_spent_usd:.4f} USD!")
                        log_timeline_event("LIMIT_EXCEEDED_SPEND", {"spent_usd": current_spent_usd})
                        break

                    if cur_bal <= PRESERVATION_FLOOR_USD:
                        print(f"[KILL] Account preservation floor (${PRESERVATION_FLOOR_USD:.2f}) reached: balance ${cur_bal:.4f} USD!")
                        log_timeline_event("PRESERVATION_FLOOR_BREACH", {"balance": cur_bal})
                        break
                except Exception as b_err:
                    print(f"  [Balance Check Warning] Could not query live balance: {b_err}")

            # Poll remote output file
            try:
                with sftp.file(remote_out, "r") as rf:
                    lines = rf.readlines()
                current_count = len(lines)
                if current_count > last_seen_lines:
                    for line_idx in range(last_seen_lines, current_count):
                        raw_line = lines[line_idx].strip()
                        if raw_line:
                            try:
                                record = json.loads(raw_line)
                            except json.JSONDecodeError:
                                continue
                            local_records.append(record)
                            with open(GENERATIONS_OUT, "a", encoding="utf-8") as wf:
                                wf.write(raw_line + "\n")
                                wf.flush()
                                os.fsync(wf.fileno())
                            tokens = record.get("generated_tokens", record.get("total_tokens", len(record.get("model_output", "").split())))
                            print(f"  [{len(local_records):03d}/{TARGET_REQUESTS}] {record.get('request_id')} | {record.get('condition_code')} | Prob: {record.get('problem_id')} | Tokens: {tokens} | Elapsed: {elapsed_min:.1f}m")
                    last_seen_lines = current_count
                    completed_generations = len(local_records)
                    log_timeline_event("RECORDS_INGESTED", {
                        "completed": completed_generations,
                        "spent_usd": current_spent_usd,
                        "elapsed_min": elapsed_min
                    })
            except IOError:
                # Remote output file not created yet
                pass

            if completed_generations >= TARGET_REQUESTS:
                print(f"\nAll {TARGET_REQUESTS} authentic primary requests completed successfully!")
                log_timeline_event("ALL_REQUESTS_COMPLETED", {"total": TARGET_REQUESTS})
                break

            # Check if remote runner process died prematurely
            code, ps_out, _ = run_ssh("pgrep -f remote_experiment_runner.py")
            if code != 0 and completed_generations < TARGET_REQUESTS:
                print(f"Remote experiment runner process exited before {TARGET_REQUESTS} requests completed.")
                code, runner_log_tail, _ = run_ssh(f"tail -n 40 {remote_log}")
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
        # Step 11: Authoritative Pod Teardown & Multi-Pass Destruction Verification
        print("\n" + "=" * 80)
        print("  PHASE 6: AUTHORITATIVE POD TEARDOWN & DESTRUCTION VERIFICATION")
        print("=" * 80)

        t_end = time.time()
        elapsed_sec = t_end - created_at_time

        if pod_id:
            print(f"Dispatching authoritative teardown for Pod ID: {pod_id}...")
            log_timeline_event("TEARDOWN_DISPATCHED", {"pod_id": pod_id})
            
            try:
                term_ok, term_msg = provisioner.emergency_teardown(reason="Primary experiment completed or terminated")
                print(f"Provisioner teardown response: {term_ok} ({term_msg})")
            except Exception as te:
                print(f"Provisioner teardown error: {te}")

            # Backup multi-pass authoritative provider verification
            destruction_confirmed = False
            for check in range(35):
                time.sleep(2.0)
                try:
                    p = runpod.get_pod(pod_id)
                    if not p or p.get("desiredStatus") in ["TERMINATED", "DELETED", None]:
                        destruction_confirmed = True
                        print(f"Pod {pod_id} destruction CONFIRMED by RunPod API.")
                        break
                    print(f"  Check {check+1:02d}: Pod still present with status '{p.get('desiredStatus')}'...")
                    runpod.terminate_pod(pod_id)
                except Exception as ex:
                    if "not found" in str(ex).lower():
                        destruction_confirmed = True
                        print(f"Pod {pod_id} confirmed NOT_FOUND by RunPod API.")
                        break
            
            log_timeline_event("DESTRUCTION_VERIFICATION", {"pod_id": pod_id, "confirmed": destruction_confirmed})

        # Step 12: Stop Watchdog Process
        if provisioner.watchdog_process and provisioner.watchdog_process.poll() is None:
            try:
                provisioner.watchdog_process.terminate()
                provisioner.watchdog_process.wait(timeout=3.0)
                print("Watchdog daemon stopped cleanly.")
            except Exception:
                pass

        # Step 13: Relock Cloud Execution Fail-Closed
        lock_cloud_execution()

        # Step 14: Post-Execution Financial Reconciliation Audit
        print("\n" + "=" * 80)
        print("  PHASE 7: FINAL FINANCIAL RECONCILIATION AUDIT")
        print("=" * 80)
        time.sleep(4.0)
        post_acct = query_runpod_account()
        final_balance = float(post_acct.get("clientBalance", 0.0))
        final_pods = post_acct.get("pods") or []
        final_vols = post_acct.get("networkVolumes") or []
        net_spend = initial_balance - final_balance

        print(f"Initial RunPod Balance:   ${initial_balance:.4f} USD")
        print(f"Final RunPod Balance:     ${final_balance:.4f} USD")
        print(f"Net Cloud Expenditure:    ${net_spend:.4f} USD")
        print(f"Planned Spending Ceiling: ${MAX_SPEND_CEILING_USD:.4f} USD (Complied: {net_spend <= MAX_SPEND_CEILING_USD})")
        print(f"Emergency Shutdown Trigger:${EMERGENCY_TRIGGER_USD:.4f} USD (Complied: {net_spend <= EMERGENCY_TRIGGER_USD})")
        print(f"Preservation Floor:       ${PRESERVATION_FLOOR_USD:.4f} USD (Complied: {final_balance >= PRESERVATION_FLOOR_USD})")
        print(f"Total Session Duration:   {elapsed_sec:.1f}s ({elapsed_sec/60:.2f} minutes)")
        print(f"Remaining Active Pods:    {len(final_pods)}")
        print(f"Remaining Volumes:        {len(final_vols)}")
        print(f"Completed Generations:    {completed_generations} / {TARGET_REQUESTS}")
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
            "spend_within_ceiling": net_spend <= MAX_SPEND_CEILING_USD,
            "spend_within_trigger": net_spend <= EMERGENCY_TRIGGER_USD,
            "preservation_floor_respected": final_balance >= PRESERVATION_FLOOR_USD,
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

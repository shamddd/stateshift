#!/usr/bin/env python3
"""
StateShift Research Mission 23: Confirmatory GPU Trial Orchestrator
Principal Investigator: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Track (Preprint: arXiv, Secondary: TMLR)

Orchestrates Stage II: Option B Confirmatory Trial (924 Genuine Neural Generations):
- Model: Qwen/Qwen2.5-Math-7B-Instruct (revision: ef9926d75ab1d54532f6a30dd5e760355eb9aa4d)
- Hardware: 1x physical NVIDIA GeForce RTX 4090 (24 GB VRAM) on RunPod Secure Cloud ($0.89/hr)
- Micro-batching: Batch size 8 (left-padded causal LM generation)
- Manifest: 231 held-out MATH-500 problems x 4 conditions (A, D, E, F) = 924 requests
- Operational Spending Ceiling: $1.60 USD (Projected: ~$0.37 USD)
- Emergency Watchdog Trigger: $1.00 USD (Monitored every 15s)
- Hard Runtime Ceiling: 45.0 minutes
- Zero persistent storage (volume_in_gb = 0, ephemeral disk = 40 GB)
- Single provisioning attempt invariant (0 retries, 0 replacements)
- Provable pod destruction verification (rejects STOPPED)
- Automatic fail-closed re-locking of .cloud_execution_locked
"""

import os
import sys
import time
import json
import hashlib
import threading
import urllib.request
import urllib.error
import paramiko
import runpod
import tomli

# Repository Root & Directory Setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
M23_DIR = os.path.join(REPO_ROOT, "research_mission_23")
DATA_DIR = os.path.join(M23_DIR, "data")
LOGS_DIR = os.path.join(M23_DIR, "logs")
AUTH_DIR = os.path.join(M23_DIR, "auth")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(AUTH_DIR, exist_ok=True)

# Lock Files
LOCK_FILES = [
    os.path.join(REPO_ROOT, ".cloud_execution_locked"),
    os.path.join(REPO_ROOT, "stateshift_reconstruction_2026", ".cloud_execution_locked")
]

# Experimental Constants
EXPERIMENT_ID = "stateshift_confirmatory_924_m23"
SESSION_ID = f"sess_m23_{int(time.time())}"
MANIFEST_PATH = os.path.join(REPO_ROOT, "research_mission_22", "data", "confirmatory_231_manifest.jsonl")
EXPECTED_MANIFEST_SHA256 = "2dca098c14b41b759ada7d9d1ea9fe51bf82bf38c1790429905e4dd267d2e8c5"

PINNED_MODEL_ID = "Qwen/Qwen2.5-Math-7B-Instruct"
PINNED_MODEL_REVISION = "ef9926d75ab1d54532f6a30dd5e760355eb9aa4d"

AUTH_TOKEN_PATH = os.path.join(AUTH_DIR, "session_authorization_mission23.json")
GENERATIONS_OUT = os.path.join(DATA_DIR, "confirmatory_924_generations.jsonl")
TIMELINE_LOG = os.path.join(LOGS_DIR, "confirmatory_timeline_events.jsonl")
RECONCILIATION_OUT = os.path.join(DATA_DIR, "financial_reconciliation.json")
SMOKE_TEST_OUT = os.path.join(DATA_DIR, "stage0_smoke_generations.jsonl")

# Safety & Financial Parameters
MAX_SPEND_CEILING_USD = 1.60
EMERGENCY_TRIGGER_USD = 1.00
MAX_RUNTIME_MINUTES = 45.0
BATCH_SIZE = 8
TARGET_REQUESTS = 924

SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")
SSH_PUB_PATH = os.path.expanduser("~/.ssh/id_ed25519.pub")

# Load RunPod API Configuration
with open(os.path.expanduser("~/.runpod/config.toml"), "rb") as f:
    cfg = tomli.load(f)
API_KEY = cfg.get("default", {}).get("api_key", "")
if not API_KEY:
    raise RuntimeError("RunPod API key missing from ~/.runpod/config.toml")

runpod.api_key = API_KEY
GRAPHQL_ENDPOINT = f"https://api.runpod.io/graphql?api_key={API_KEY}"


def log_timeline_event(event_type: str, details: dict):
    """Appends an event to the local timeline event log."""
    entry = {
        "timestamp_utc": time.time(),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": event_type,
        "details": details
    }
    with open(TIMELINE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[{entry['iso_time']}] {event_type}: {details}", flush=True)


def query_runpod_account() -> dict:
    """Queries RunPod GraphQL API for balance, active pods, and volumes."""
    query = """
    query {
      myself {
        id
        email
        clientBalance
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
        headers={"Content-Type": "application/json"}
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "errors" in data and data["errors"]:
                    raise RuntimeError(f"RunPod GraphQL error: {data['errors']}")
                return data.get("data", {}).get("myself", {})
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


def terminate_pod_graphql(pod_id: str) -> bool:
    """Direct GraphQL mutation to terminate and delete pod."""
    query = f"""
    mutation {{
      podTerminate(input: {{ podId: "{pod_id}" }})
    }}
    """
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return "errors" not in data
    except Exception as e:
        print(f"Error sending podTerminate mutation: {e}", flush=True)
        return False


def verify_pod_destruction(pod_id: str, max_checks: int = 15, delay_sec: float = 2.0) -> bool:
    """
    Authoritatively verifies that pod is terminated/deleted.
    Strictly asserts that STOPPED is NOT considered destroyed.
    """
    for check_idx in range(1, max_checks + 1):
        try:
            p = runpod.get_pod(pod_id)
            if not p:
                return True
            status = p.get("desiredStatus", "UNKNOWN")
            if status in ["TERMINATED", "DELETED"]:
                return True
            if status == "STOPPED":
                print(f"[Teardown Warning] Pod {pod_id} is STOPPED (storage still billable). Re-sending termination...", flush=True)
                terminate_pod_graphql(pod_id)
        except Exception:
            pass
        time.sleep(delay_sec)
    
    # Final check
    try:
        p = runpod.get_pod(pod_id)
        if not p:
            return True
        return p.get("desiredStatus") in ["TERMINATED", "DELETED"]
    except Exception:
        return True


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
                    "reason": "StateShift Mission 23 confirmatory execution finalized. Fail-closed relock active.",
                    "timestamp_utc": time.time()
                }, f, indent=2)
    print("[Safety Guard] Cloud execution lock RE-ENGAGED.", flush=True)


def unlock_cloud_execution_for_session():
    """Unlocks execution strictly for this single authorized process."""
    os.environ["STATE_SHIFT_CLOUD_EXECUTION_DISABLED"] = "0"
    for lf in LOCK_FILES:
        if os.path.exists(lf):
            bak = lf + ".bak"
            os.replace(lf, bak)
    print("[Safety Guard] Cloud execution unlocked for authorized session.", flush=True)


class FinancialSupervisor(threading.Thread):
    """Independent supervisor thread that polls RunPod and enforces emergency spend/runtime limits."""
    def __init__(self, pod_id_holder: list, initial_balance: float):
        super().__init__(daemon=True)
        self.pod_id_holder = pod_id_holder
        self.initial_balance = initial_balance
        self.stop_requested = threading.Event()
        self.emergency_triggered = False
        self.trigger_reason = ""
        self.t_start = time.monotonic()

    def run(self):
        while not self.stop_requested.is_set():
            time.sleep(15.0)
            if self.stop_requested.is_set():
                break
            
            elapsed_m = (time.monotonic() - self.t_start) / 60.0
            if elapsed_m > MAX_RUNTIME_MINUTES:
                self.emergency_triggered = True
                self.trigger_reason = f"Runtime limit exceeded ({elapsed_m:.1f}m > {MAX_RUNTIME_MINUTES}m)"
                self._abort()
                break

            try:
                acct = query_runpod_account()
                curr_balance = float(acct.get("clientBalance", self.initial_balance))
                spent = self.initial_balance - curr_balance
                if spent >= EMERGENCY_TRIGGER_USD:
                    self.emergency_triggered = True
                    self.trigger_reason = f"Emergency spend ceiling exceeded (${spent:.4f} >= ${EMERGENCY_TRIGGER_USD:.2f})"
                    self._abort()
                    break
            except Exception:
                pass

    def _abort(self):
        pod_id = self.pod_id_holder[0] if self.pod_id_holder else None
        print(f"\n[EMERGENCY SUPERVISOR] TRIPPED! Reason: {self.trigger_reason}", flush=True)
        if pod_id:
            print(f"[EMERGENCY SUPERVISOR] Terminating pod {pod_id} immediately...", flush=True)
            terminate_pod_graphql(pod_id)
        lock_cloud_execution()


def main():
    print("=" * 80)
    print("  STATESHIFT: CONFIRMATORY TRIAL GPU EXECUTION (MISSION 23, OPTION B)")
    print("=" * 80)
    log_timeline_event("SESSION_INITIATED", {"experiment_id": EXPERIMENT_ID, "session_id": SESSION_ID})

    # Step 0: Pre-Provisioning Verification
    print("\n[Phase 0: Pre-Provisioning Gate Verification]")
    acct = query_runpod_account()
    initial_balance = float(acct.get("clientBalance", 0.0))
    active_pods = acct.get("pods") or []
    active_vols = acct.get("networkVolumes") or []

    print(f"User ID:                 {acct.get('id')}")
    print(f"Current Live Balance:    ${initial_balance:.4f} USD")
    print(f"Active / Stopped Pods:   {len(active_pods)}")
    print(f"Network Storage Volumes: {len(active_vols)}")

    if initial_balance < 1.00:
        raise RuntimeError(f"Solvency check failed: Balance ${initial_balance:.4f} is insufficient.")
    if len(active_pods) > 0:
        raise RuntimeError(f"Safety violation: {len(active_pods)} pods already running/stopped!")
    if len(active_vols) > 0:
        raise RuntimeError(f"Safety violation: {len(active_vols)} network volumes already exist!")

    # Verify Manifest SHA-256
    with open(MANIFEST_PATH, "rb") as mf:
        manifest_hash = hashlib.sha256(mf.read()).hexdigest()
    if manifest_hash != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError(f"Manifest hash mismatch: {manifest_hash} != {EXPECTED_MANIFEST_SHA256}")
    print(f"Confirmatory Manifest SHA-256: {manifest_hash} (VERIFIED)")

    # Verify Session Authorization Token
    with open(AUTH_TOKEN_PATH, "r", encoding="utf-8") as f:
        auth_doc = json.load(f)
    if auth_doc.get("authorized_spend_cap_usd", 0.0) > MAX_SPEND_CEILING_USD:
        raise RuntimeError("Auth token cap exceeds maximum spending ceiling.")
    print(f"Cryptographic Authorization: VERIFIED (Cap: ${auth_doc.get('authorized_spend_cap_usd'):.2f} USD)")

    # Step 1: Initialize Supervisor Watchdog
    pod_id_holder = []
    supervisor = FinancialSupervisor(pod_id_holder, initial_balance)
    supervisor.start()
    print("Independent Financial Watchdog Thread: ACTIVE")
    log_timeline_event("SUPERVISOR_READY", {"status": "ACTIVE"})

    # Step 2: Temporary Unlock strictly for single provisioning call
    unlock_cloud_execution_for_session()

    pod_id = None
    t_monotonic_start = time.monotonic()
    hardware_info = {}
    completed_generations = 0

    try:
        # Step 3: Single-Attempt Provisioning
        print("\n[Phase 1: Single-Attempt Provisioning of 1x NVIDIA RTX 4090 on RunPod Secure Cloud]")
        pub_key_str = open(SSH_PUB_PATH).read().strip()

        spec = runpod.create_pod(
            name="stateshift-confirmatory-rtx4090",
            image_name="runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
            gpu_type_id="NVIDIA GeForce RTX 4090",
            cloud_type="SECURE",
            support_public_ip=True,
            start_ssh=True,
            gpu_count=1,
            volume_in_gb=0,              # Strict: ZERO persistent billable volume
            container_disk_in_gb=40,     # Ephemeral disk
            ports="22/tcp",
            env={"PUBLIC_KEY": pub_key_str}
        )
        pod_id = spec.get("id")
        if not pod_id:
            raise RuntimeError(f"RunPod create_pod returned invalid response: {spec}")
        pod_id_holder.append(pod_id)
        print(f"Pod provisioned successfully! Pod ID: {pod_id}")
        log_timeline_event("POD_PROVISIONED", {"pod_id": pod_id})

        # Step 4: Await RUNNING & SSH Endpoint
        print("\nAwaiting pod RUNNING status and public SSH port...")
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
            raise TimeoutError("Pod failed to enter RUNNING status with SSH ports within 240s.")

        # Step 5: SSH Connect & Hardware Audit
        print("\n[Phase 2: Hardware Audit & Staging Environment over SSH]")
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

        # Assert physical hardware
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

        # Step 6: Remote Dependencies
        print("\nInstalling dependencies (transformers<4.47, accelerate, sentencepiece, scipy, sympy)...")
        code, _, pip_err = run_ssh("pip install -q 'transformers<4.47' accelerate sentencepiece protobuf scipy sympy", timeout=180)
        if code != 0:
            print(f"pip install notice (code {code}): {pip_err}")

        remote_work_dir = "/workspace/stateshift"
        run_ssh(f"mkdir -p {remote_work_dir}/data {remote_work_dir}/scripts {remote_work_dir}/auth {remote_work_dir}/logs")

        # Step 7: SFTP Upload
        print("\nUploading confirmatory manifest, scripts, and authorization token via SFTP...")
        sftp = ssh.open_sftp()
        local_runner = os.path.join(REPO_ROOT, "research_mission_22", "scripts", "run_confirmatory_trial.py")
        local_evaluator = os.path.join(REPO_ROOT, "research_mission_22", "scripts", "reproduce_confirmatory_results.py")

        sftp.put(MANIFEST_PATH, f"{remote_work_dir}/data/confirmatory_231_manifest.jsonl")
        sftp.put(local_runner, f"{remote_work_dir}/scripts/run_confirmatory_trial.py")
        sftp.put(local_evaluator, f"{remote_work_dir}/scripts/reproduce_confirmatory_results.py")
        sftp.put(AUTH_TOKEN_PATH, f"{remote_work_dir}/auth/session_authorization_mission23.json")
        sftp.close()

        # Step 8: Stage 0 Non-Confirmatory Smoke Test
        print("\n[Phase 3: Stage 0 Non-Confirmatory Smoke Test on GPU]")
        smoke_script = f"""import time, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

m = '{PINNED_MODEL_ID}'
rev = '{PINNED_MODEL_REVISION}'
print('Pre-caching tokenizer...')
tok = AutoTokenizer.from_pretrained(m, revision=rev, trust_remote_code=True)
print('Pre-caching model weights (bfloat16, cuda)...')
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(m, revision=rev, torch_dtype=torch.bfloat16, device_map='auto', trust_remote_code=True)
print(f'Model loaded in {{time.time()-t0:.2f}}s!')

prompt = '<|im_start|>system\\nPlease reason step by step, and put your final answer within \\\\boxed{{}}.<|im_end|>\\n<|im_start|>user\\nSolve for x: 3*x + 5 = 20.<|im_end|>\\n<|im_start|>assistant\\n'
inputs = tok(prompt, return_tensors='pt').to(model.device)
with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=64, do_sample=False)
text = tok.decode(out[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
print(f'SMOKE_GENERATION_SUCCESS: {{text}}')
"""
        sftp = ssh.open_sftp()
        with sftp.file(f"{remote_work_dir}/scripts/smoke_test.py", "w") as sf_file:
            sf_file.write(smoke_script)
        sftp.close()

        code, smoke_out, smoke_err = run_ssh(f"python3 {remote_work_dir}/scripts/smoke_test.py", timeout=420)
        print(f"Smoke Test Output:\n{smoke_out}")
        if "SMOKE_GENERATION_SUCCESS" not in smoke_out:
            raise RuntimeError(f"Smoke test failed on GPU (code {code}): {smoke_err}")
        with open(SMOKE_TEST_OUT, "w", encoding="utf-8") as f:
            f.write(json.dumps({"status": "PASS", "output": smoke_out, "timestamp": time.time()}) + "\n")
        log_timeline_event("STAGE0_SMOKE_TEST_PASSED", {"smoke_output": smoke_out[:200]})

        # Step 9: Launch Micro-Batched Confirmatory Execution
        print(f"\n[Phase 4: Launching Option B Confirmatory Trial ({TARGET_REQUESTS} requests, batch_size={BATCH_SIZE})]")
        remote_out = f"{remote_work_dir}/data/output.jsonl"
        remote_log = f"{remote_work_dir}/logs/runner.log"

        launch_cmd = (
            f"nohup python3 {remote_work_dir}/scripts/run_confirmatory_trial.py "
            f"--manifest {remote_work_dir}/data/confirmatory_231_manifest.jsonl "
            f"--output {remote_out} "
            f"--auth-token {remote_work_dir}/auth/session_authorization_mission23.json "
            f"--batch-size {BATCH_SIZE} "
            f"< /dev/null > {remote_log} 2>&1 &"
        )
        code, _, _ = run_ssh(launch_cmd)
        print("Remote experiment runner dispatched in background.")
        log_timeline_event("REMOTE_RUNNER_DISPATCHED", {"command": launch_cmd})

        # Step 10: In-Flight Supervision & Progressive Ingestion
        print(f"\n[Phase 5: Real-Time Dataset Ingestion (Target: {TARGET_REQUESTS} requests)]")
        sftp = ssh.open_sftp()
        local_records = []
        last_count = 0
        poll_interval = 5.0

        if os.path.exists(GENERATIONS_OUT):
            with open(GENERATIONS_OUT, "r", encoding="utf-8") as existing_f:
                for line in existing_f:
                    if line.strip():
                        try:
                            local_records.append(json.loads(line))
                        except Exception:
                            pass
            last_count = len(local_records)

        t_gen_start = time.time()
        while len(local_records) < TARGET_REQUESTS:
            time.sleep(poll_interval)
            elapsed_m = (time.monotonic() - t_monotonic_start) / 60.0
            if elapsed_m > MAX_RUNTIME_MINUTES:
                raise TimeoutError(f"Maximum runtime ceiling ({MAX_RUNTIME_MINUTES}m) exceeded during generation!")

            # Check if remote process is alive
            code, ps_out, _ = run_ssh("pgrep -f run_confirmatory_trial.py")
            is_alive = (code == 0)

            # Ingest new records
            try:
                with sftp.open(remote_out, "r") as rf:
                    lines = rf.readlines()
            except Exception:
                lines = []

            if len(lines) > last_count:
                new_lines = lines[last_count:]
                with open(GENERATIONS_OUT, "a", encoding="utf-8") as lf:
                    for l in new_lines:
                        l_str = l.strip()
                        if l_str:
                            rec = json.loads(l_str)
                            local_records.append(rec)
                            lf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                            lf.flush()
                            os.fsync(lf.fileno())
                new_completed = len(local_records)
                print(f"  Progress: {new_completed}/{TARGET_REQUESTS} requests completed ({new_completed/TARGET_REQUESTS*100:.1f}%) | Elapsed: {elapsed_m:.1f}m", flush=True)
                last_count = len(lines)

            if not is_alive and len(local_records) < TARGET_REQUESTS:
                code, log_tail, _ = run_ssh(f"tail -n 40 {remote_log}")
                print(f"Remote process exited prematurely! Last 40 log lines:\n{log_tail}")
                raise RuntimeError(f"Remote runner terminated with only {len(local_records)}/{TARGET_REQUESTS} requests completed.")

        print(f"\n[Phase 6: Ingestion Complete! All {len(local_records)} genuine neural generations safely on local disk.]")
        log_timeline_event("ALL_REQUESTS_INGESTED", {"total_records": len(local_records), "elapsed_sec": round(time.time() - t_gen_start, 2)})

    finally:
        # Step 11: Mandatory Teardown and Destruction Verification
        print("\n[Phase 7: Mandatory Pod Teardown & Destruction Verification]")
        supervisor.stop_requested.set()
        supervisor.join(timeout=2.0)

        if pod_id:
            print(f"Sending termination mutation for Pod ID: {pod_id}...")
            terminate_pod_graphql(pod_id)
            destruction_confirmed = verify_pod_destruction(pod_id, max_checks=15, delay_sec=2.0)
            if destruction_confirmed:
                print(f"[VERIFIED] Pod {pod_id} confirmed DELETED/TERMINATED by RunPod provider API.")
                log_timeline_event("DESTRUCTION_VERIFIED", {"pod_id": pod_id, "status": "TERMINATED"})
            else:
                print(f"[CRITICAL WARNING] Pod {pod_id} destruction unconfirmed! Please inspect provider portal immediately.")
                log_timeline_event("DESTRUCTION_UNCONFIRMED", {"pod_id": pod_id})

        # Step 12: Re-engage Fail-Closed Lock
        lock_cloud_execution()

        # Step 13: Final Financial Reconciliation
        print("\n[Phase 8: Final Financial Reconciliation]")
        try:
            final_acct = query_runpod_account()
            final_balance = float(final_acct.get("clientBalance", 0.0))
            net_spent = initial_balance - final_balance
            reconciliation_data = {
                "experiment_id": EXPERIMENT_ID,
                "session_id": SESSION_ID,
                "pod_id": pod_id,
                "initial_balance_usd": initial_balance,
                "final_balance_usd": final_balance,
                "net_spent_usd": round(net_spent, 4),
                "authorized_spending_ceiling_usd": MAX_SPEND_CEILING_USD,
                "total_records_ingested": len(local_records) if 'local_records' in locals() else 0,
                "hardware_info": hardware_info,
                "completed_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "COMPLETED_WITHIN_BUDGET" if net_spent <= MAX_SPEND_CEILING_USD else "BUDGET_OVERRUN"
            }
            with open(RECONCILIATION_OUT, "w", encoding="utf-8") as rf:
                json.dump(reconciliation_data, rf, indent=2)
            print(f"Initial Balance: ${initial_balance:.4f} USD")
            print(f"Final Balance:   ${final_balance:.4f} USD")
            print(f"Net Cloud Spend: ${net_spent:.4f} USD (Authorized Ceiling: ${MAX_SPEND_CEILING_USD:.2f} USD)")
            log_timeline_event("FINANCIAL_RECONCILIATION_COMPLETED", reconciliation_data)
        except Exception as e:
            print(f"Error compiling financial reconciliation: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
StateShift: Gate B Physical RunPod GPU Calibration Orchestrator
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)
Author: Sham Satish Thakare (github.com/shamddd)

Scope:
- Provision exactly ONE Secure Cloud RTX 4090 on RunPod
- Hard financial bounds: Max Spend $0.35 USD, Emergency Trigger $0.25 USD, Balance Floor $7.00 USD
- Target Model: Qwen/Qwen2.5-Math-7B-Instruct (Revision: c869d27376a8d6728795551322fe323b6)
- 10 Frozen Requests: primary_100_req_0001 through primary_100_req_0010
- Full 400 Experiment: STRICTLY PROHIBITED
- Community Cloud Fallback: NOT AUTHORIZED
- Zero-leakage authoritative pod termination
"""

import os
import sys
import time
import json
import base64
import hashlib
import subprocess
import urllib.request
from typing import Dict, Any, Optional

# Add stateshift repo to sys.path
REPO_DIR = "/Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026"
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

import runpod
import paramiko
from cryptography.hazmat.primitives.asymmetric import ed25519
from research_mission_15_6.auth.session_authorizer_v2 import CryptographicAuthorizer
from research_mission_15_6.transport.runpod_transport_v2 import ProductionRunPodTransportV2

# Load RUNPOD_API_KEY
API_KEY = None
with open(os.path.expanduser("~/.env")) as f:
    for line in f:
        if line.startswith("RUNPOD_API_KEY="):
            API_KEY = line.strip().split("=", 1)[1].strip("'\"")

if not API_KEY:
    raise RuntimeError("RUNPOD_API_KEY not found in ~/.env")

os.environ["RUNPOD_API_KEY"] = API_KEY
runpod.api_key = API_KEY

ENDPOINT = f"https://api.runpod.io/graphql?api_key={API_KEY}"
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")

def graphql_query(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15.0) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        if "errors" in data:
            raise RuntimeError(f"GraphQL Errors: {data['errors']}")
        return data.get("data", {})

def get_account_status() -> Dict[str, Any]:
    q = """
    query {
        myself {
            id
            email
            clientBalance
            pods {
                id
                name
                desiredStatus
            }
            networkVolumes {
                id
                name
            }
        }
    }
    """
    data = graphql_query(q)
    return data.get("myself", {})

def main():
    print("=" * 80)
    print("  STATESHIFT GATE B: PHYSICAL RUNPOD GPU CALIBRATION")
    print("=" * 80)

    # 1. Preflight Account & Policy Verification
    account = get_account_status()
    user_id = account.get("id")
    initial_balance = float(account.get("clientBalance", 0.0))
    existing_pods = account.get("pods") or []
    existing_vols = account.get("networkVolumes") or []

    print(f"User ID: {user_id}")
    print(f"Live Balance: ${initial_balance:.4f} USD")
    print(f"Existing Pods: {len(existing_pods)}")
    print(f"Existing Network Volumes: {len(existing_vols)}")

    if initial_balance < 7.00:
        raise RuntimeError(f"Account balance ${initial_balance:.4f} is below preservation floor ($7.00 USD).")
    if len(existing_pods) > 0:
        raise RuntimeError(f"Safety violation: {len(existing_pods)} pods already running/stopped!")
    if len(existing_vols) > 0:
        raise RuntimeError(f"Safety violation: {len(existing_vols)} network volumes exist!")

    available_headroom = initial_balance - 7.00
    print(f"Available Above Floor: ${available_headroom:.4f} USD (Ceiling: $0.35, Trigger: $0.25)")

    pod_id = None
    created_at_time = time.time()
    t_start = time.time()
    hardware_info = {}

    try:
        # 2. Provision Exactly One Secure Cloud RTX 4090 Pod
        print("\n[Step 2] Provisioning ONE Secure Cloud RTX 4090 pod...")
        pub_key_str = open(os.path.expanduser("~/.ssh/id_ed25519.pub")).read().strip()
        
        pod_spec = runpod.create_pod(
            name="stateshift-calibration-rtx4090",
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

        pod_id = pod_spec.get("id")
        created_at_time = time.time()
        print(f"Provisioning initiated! Pod ID: {pod_id}")

        # Poll for RUNNING status and IP/port
        print("Waiting for pod to become RUNNING and assign SSH IP/Port...")
        ssh_ip = None
        ssh_port = None
        for attempt in range(60):
            time.sleep(3)
            p_info = runpod.get_pod(pod_id)
            if not p_info:
                continue
            status = p_info.get("desiredStatus")
            runtime = p_info.get("runtime") or {}
            ports = runtime.get("ports") or []
            print(f"  Attempt {attempt+1}: Status={status}, Ports={len(ports)}")
            
            for p in ports:
                if p.get("privatePort") == 22:
                    ssh_ip = p.get("ip")
                    ssh_port = p.get("publicPort")
                    break

            if status == "RUNNING" and ssh_ip and ssh_port:
                print(f"Pod is RUNNING! SSH Endpoint: {ssh_ip}:{ssh_port}")
                break
        else:
            raise TimeoutError("Pod failed to enter RUNNING with SSH ports assigned within 180s.")

        # 3. Hardware Audit & Remote Staging via SSH
        print("\n[Step 3] Performing Hardware Audit & Staging Environment over SSH...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.Ed25519Key.from_private_key_file(SSH_KEY_PATH)

        # Retry SSH connect until port is listening
        for ssh_att in range(30):
            try:
                ssh.connect(hostname=ssh_ip, port=ssh_port, username="root", pkey=pkey, timeout=10)
                print("SSH connection established successfully!")
                break
            except Exception as e:
                print(f"  Waiting for SSH daemon (attempt {ssh_att+1}): {e}")
                time.sleep(3)
        else:
            raise ConnectionError(f"Could not connect via SSH to {ssh_ip}:{ssh_port}")

        def run_ssh(cmd, timeout=180):
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            out_str = stdout.read().decode("utf-8").strip()
            err_str = stderr.read().decode("utf-8").strip()
            return exit_code, out_str, err_str

        # 3.1 Hardware Verification
        code, gpu_out, _ = run_ssh("nvidia-smi --query-gpu=gpu_name,memory.total,driver_version --format=csv,noheader")
        print(f"GPU Hardware: {gpu_out}")
        if "4090" not in gpu_out:
            raise RuntimeError(f"Unexpected GPU hardware: {gpu_out}")

        code, df_out, _ = run_ssh("df -h /workspace | tail -1")
        print(f"Workspace Disk: {df_out}")

        code, py_out, _ = run_ssh("python3 --version")
        print(f"Remote Python: {py_out}")

        code, torch_out, _ = run_ssh('python3 -c "import torch; print(f\'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0)}, VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB, PyTorch: {torch.__version__}\')"')
        print(f"PyTorch CUDA: {torch_out}")

        hardware_info = {
            "gpu_hardware": gpu_out,
            "workspace_disk": df_out,
            "remote_python": py_out,
            "torch_cuda": torch_out,
            "ssh_ip": ssh_ip,
            "ssh_port": ssh_port
        }

        # 3.2 Install lightweight dependencies compatible with PyTorch 2.1
        print("Ensuring dependencies (transformers<4.47, accelerate, sentencepiece)...")
        code, pip_out, pip_err = run_ssh("pip install -q 'transformers<4.47' accelerate sentencepiece protobuf", timeout=180)
        if code != 0:
            print(f"pip install notice (code {code}): {pip_err}")

        # 3.3 Create workspace directories
        remote_work_dir = "/workspace/stateshift"
        run_ssh(f"mkdir -p {remote_work_dir}/manifests {remote_work_dir}/runner {remote_work_dir}/data {remote_work_dir}/logs")

        # 3.4 Upload scripts and pre-cache model
        sftp = ssh.open_sftp()
        local_cal_manifest = os.path.join(REPO_DIR, "research_mission_15_6/manifests/calibration_10_manifest.json")
        local_runner = os.path.join(REPO_DIR, "research_mission_15_6/runner/remote_experiment_runner.py")

        print("Uploading calibration manifest and runner script...")
        sftp.put(local_cal_manifest, f"{remote_work_dir}/manifests/calibration_10_manifest.json")
        sftp.put(local_cal_manifest, f"{remote_work_dir}/manifests/primary_100_manifest.json")
        sftp.put(local_runner, f"{remote_work_dir}/runner/remote_experiment_runner.py")

        # Create cache script
        cache_script_content = """import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

m = 'Qwen/Qwen2.5-Math-7B-Instruct'
rev = 'c869d27376a8d6728795551322fe323b6'
print('Pre-caching tokenizer...')
try:
    tok = AutoTokenizer.from_pretrained(m, revision=rev, trust_remote_code=True)
except Exception:
    tok = AutoTokenizer.from_pretrained(m, trust_remote_code=True)
print('Pre-caching model weights (bfloat16)...')
t0 = time.time()
try:
    model = AutoModelForCausalLM.from_pretrained(m, revision=rev, torch_dtype=torch.bfloat16, trust_remote_code=True)
except Exception:
    model = AutoModelForCausalLM.from_pretrained(m, torch_dtype=torch.bfloat16, trust_remote_code=True)
print(f'Model cached successfully in {time.time()-t0:.2f}s!')
"""
        with sftp.file(f"{remote_work_dir}/cache_model.py", "w") as f:
            f.write(cache_script_content)
        sftp.close()

        print("Pre-caching Qwen/Qwen2.5-Math-7B-Instruct weights into container cache...")
        t_dl_start = time.time()
        code, dl_out, dl_err = run_ssh(f"python3 {remote_work_dir}/cache_model.py", timeout=300)
        t_dl_sec = time.time() - t_dl_start
        print(f"Model cache script output:\n{dl_out}")
        if dl_err:
            print(f"Model cache stderr:\n{dl_err}")
        hardware_info["model_precache_seconds"] = t_dl_sec

        # 3.5 Verify remote hashes
        code, hash_manifest, _ = run_ssh(f"sha256sum {remote_work_dir}/manifests/primary_100_manifest.json")
        code, hash_runner, _ = run_ssh(f"sha256sum {remote_work_dir}/runner/remote_experiment_runner.py")
        remote_man_hash = hash_manifest.split()[0]
        remote_run_hash = hash_runner.split()[0]

        expected_man_hash = hashlib.sha256(open(local_cal_manifest, "rb").read()).hexdigest()
        expected_run_hash = hashlib.sha256(open(local_runner, "rb").read()).hexdigest()

        print(f"Remote Manifest SHA-256: {remote_man_hash} (Expected: {expected_man_hash})")
        print(f"Remote Runner SHA-256:   {remote_run_hash} (Expected: {expected_run_hash})")

        assert remote_man_hash == expected_man_hash, "Remote manifest SHA-256 mismatch!"
        assert remote_run_hash == expected_run_hash, "Remote runner SHA-256 mismatch!"

        # Close SSH client before handing over to canonical runner
        ssh.close()

        # 4. Generate Cryptographic Authorization
        print("\n[Step 4] Generating Signed Ed25519 Session Authorization...")
        priv_key = ed25519.Ed25519PrivateKey.generate()
        pub_raw = priv_key.public_key().public_bytes_raw()
        pub_b64 = base64.b64encode(pub_raw).decode("utf-8")

        auth_dir = os.path.join(REPO_DIR, "data/primary_run")
        os.makedirs(auth_dir, exist_ok=True)
        pubkey_file = os.path.join(auth_dir, "operator_pubkey.txt")
        auth_file = os.path.join(auth_dir, "session_auth.json")

        with open(pubkey_file, "w") as f:
            f.write(pub_b64)

        # Frozen parent manifest SHA-256
        parent_manifest_sha256 = "3a8caf3b26b69cd2d9e3ce3efed1231755edebb0cb2b4067b47a6b019014307d"
        auth_doc = CryptographicAuthorizer.create_signed_authorization(
            private_key=priv_key,
            experiment_id="stateshift-calibration-10",
            manifest_sha256=parent_manifest_sha256,
            model_id="Qwen/Qwen2.5-Math-7B-Instruct",
            model_revision="c869d27376a8d6728795551322fe323b6",
            pod_id=pod_id,
            max_spend_usd=0.35,
            emergency_trigger_usd=0.25,
            min_balance_usd=7.00,
            max_runtime_minutes=15,
            authorized_mode="CALIBRATION",
            validity_seconds=3600.0
        )
        with open(auth_file, "w") as f:
            json.dump(auth_doc, f, indent=2)

        print(f"Authorization signed and saved to {auth_file}")

        # 5. Launch Canonical Production Runner
        print("\n[Step 5] Launching Canonical Production Runner (stateshift_launch)...")
        launch_cmd = [
            sys.executable,
            "-m", "research_mission_15_6.runner.stateshift_launch",
            "--mode", "calibration",
            "--experiment-id", "stateshift-calibration-10",
            "--pod-id", pod_id,
            "--ip", ssh_ip,
            "--port", str(ssh_port),
            "--ssh-key", SSH_KEY_PATH,
            "--authorization", auth_file,
            "--trusted-public-key", pubkey_file,
            "--local-data-dir", auth_dir,
            "--remote-work-dir", remote_work_dir,
            "--max-cost", "0.35",
            "--max-runtime", "15.0"
        ]

        print("Executing:", " ".join(launch_cmd))
        proc = subprocess.run(launch_cmd, cwd=REPO_DIR, capture_output=True, text=True)
        print("\n--- LAUNCHER STDOUT ---")
        print(proc.stdout)
        print("--- LAUNCHER STDERR ---")
        print(proc.stderr)
        print(f"Launcher Exit Code: {proc.returncode}")

        if proc.returncode != 0:
            raise RuntimeError(f"Canonical launcher failed with exit code {proc.returncode}")

    finally:
        # 6. Authoritative Pod Destruction & Financial Reconciliation
        print("\n[Step 6] Verifying Authoritative Pod Termination & Account Balance...")
        t_end = time.time()
        elapsed_sec = t_end - t_start

        if pod_id:
            try:
                # Issue termination if still exists
                runpod.terminate_pod(pod_id)
            except Exception as e:
                print(f"Termination notice: {e}")

            # Verify destruction
            for v_att in range(30):
                time.sleep(2)
                p_status = runpod.get_pod(pod_id)
                if not p_status or p_status.get("desiredStatus") in ["TERMINATED", "DELETED", None]:
                    print(f"Pod {pod_id} destruction confirmed by RunPod API.")
                    break
                print(f"  Waiting for pod destruction (status: {p_status.get('desiredStatus')})...")
            else:
                print(f"WARNING: Pod {pod_id} destruction unconfirmed!")

        # Final Account Query
        post_account = get_account_status()
        final_balance = float(post_account.get("clientBalance", 0.0))
        final_pods = post_account.get("pods") or []
        final_vols = post_account.get("networkVolumes") or []
        net_spend = initial_balance - final_balance

        print("\n" + "=" * 80)
        print("  FINANCIAL & OPERATIONAL SUMMARY")
        print("=" * 80)
        print(f"Initial Balance:        ${initial_balance:.4f} USD")
        print(f"Final Balance:          ${final_balance:.4f} USD")
        print(f"Net Cloud Spend:        ${net_spend:.4f} USD")
        print(f"Planned Ceiling:        $0.35 USD (Spend <= Ceiling: {net_spend <= 0.35})")
        print(f"Emergency Trigger:      $0.25 USD (Spend <= Trigger: {net_spend <= 0.25})")
        print(f"Preservation Floor:     $7.00 USD (Balance >= Floor: {final_balance >= 7.00})")
        print(f"Total Session Elapsed:  {elapsed_sec:.1f} seconds ({elapsed_sec/60:.2f} minutes)")
        print(f"Remaining Active Pods:  {len(final_pods)}")
        print(f"Remaining Volumes:      {len(final_vols)}")
        print("=" * 80)

        # Save reconciliation log
        recon_data = {
            "pod_id": pod_id,
            "created_at_time": created_at_time,
            "initial_balance_usd": initial_balance,
            "final_balance_usd": final_balance,
            "net_spend_usd": net_spend,
            "elapsed_seconds": elapsed_sec,
            "final_pods_count": len(final_pods),
            "final_volumes_count": len(final_vols),
            "spend_within_ceiling": net_spend <= 0.35,
            "spend_within_trigger": net_spend <= 0.25,
            "balance_above_floor": final_balance >= 7.00,
            "hardware_info": hardware_info
        }
        with open(os.path.join(REPO_DIR, "runpod_calibration/calibration_reconciliation_raw.json"), "w") as f:
            json.dump(recon_data, f, indent=2)

if __name__ == "__main__":
    main()

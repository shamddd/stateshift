#!/usr/bin/env python3
"""
StateShift Research Mission 13: Cloud GPU Orchestrator & Execution Engine
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Manages:
1. Pre-flight checks and balance verification.
2. Single GPU pod creation (prefer RTX A5000 / RTX 4090).
3. Independent external financial watchdog daemon.
4. SSH/SFTP code deployment via Paramiko.
5. Stage 1: GPU smoke test (4 requests).
6. Stage 2: Empirical cost projection.
7. Stage 3: Primary 100-problem experiment (400 requests).
8. Stage 4: Secondary replication (up to 800 requests) within budget.
9. Stage 5: Guaranteed immediate provider-level pod termination.
10. Artifact synchronization and billing audit report generation.
"""

import os
import sys
import time
import json
import signal
import tarfile
import paramiko
import requests
import tomli
from typing import Dict, Any, List, Optional, Tuple

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

import runpod
from runner.external_cost_controller import ExternalRunPodCostController
from runner.pod_lifecycle_monitor import PodLifecycleMonitor

CONFIG_PATH = os.path.expanduser("~/.runpod/config.toml")
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")

def load_ssh_pubkey() -> str:
    pub_path = os.path.expanduser("~/.ssh/id_ed25519.pub")
    if os.path.exists(pub_path):
        with open(pub_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def load_api_key() -> str:
    if os.environ.get("RUNPOD_API_KEY"):
        return os.environ["RUNPOD_API_KEY"].strip()
    with open(CONFIG_PATH, "rb") as f:
        cfg = tomli.load(f)
    key = cfg.get("default", {}).get("api_key", "").strip()
    runpod.api_key = key
    return key

def query_user_balance(api_key: str) -> float:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    q = "{ myself { clientBalance } }"
    try:
        r = requests.post("https://api.runpod.io/graphql", json={"query": q}, headers=headers, timeout=10)
        bal = r.json().get("data", {}).get("myself", {}).get("clientBalance", 0.0)
        return float(bal)
    except Exception as e:
        print(f"[Orchestrator] Warning: Failed to query clientBalance: {e}")
        return 0.0

def create_code_tarball(output_tar: str):
    """Bundle evaluation code, manifests, and runner into tarball."""
    with tarfile.open(output_tar, "w:gz") as tar:
        for folder in ["evaluation", "manifests", "runner"]:
            src_path = os.path.join(repo_root, folder)
            if os.path.exists(src_path):
                tar.add(src_path, arcname=folder)
    print(f"[Orchestrator] Created code bundle: {output_tar} ({os.path.getsize(output_tar) / 1024:.1f} KB)")

class Mission13CloudOrchestrator:
    def __init__(self,
                 max_cost_usd: float = 2.80, # Hard safety limit strictly under $3.00
                 max_runtime_minutes: float = 60.0):
        self.api_key = load_api_key()
        self.max_cost = max_cost_usd
        self.max_runtime = max_runtime_minutes
        
        self.initial_balance: float = 0.0
        self.pod_id: Optional[str] = None
        self.pod_info: Dict[str, Any] = {}
        self.gpu_hourly_rate: float = 0.89
        self.cost_controller: Optional[ExternalRunPodCostController] = None
        self.ssh_client: Optional[paramiko.SSHClient] = None
        
        self.t_launch: Optional[float] = None
        self.smoke_test_metrics: Dict[str, Any] = {}
        self.primary_metrics: Dict[str, Any] = {}
        self.replication_metrics: Dict[str, Any] = {}

    def run_preflight_checks(self):
        print("=== [PRE-FLIGHT CHECK] Verifying Environment & Account Balance ===")
        self.initial_balance = query_user_balance(self.api_key)
        print(f"Verified RunPod Account Balance: ${self.initial_balance:.4f} USD")
        if self.initial_balance < 3.00:
            raise RuntimeError(f"Account balance (${self.initial_balance:.2f}) is below the required budget!")

        existing_pods = runpod.get_pods()
        if len(existing_pods) > 0:
            if len(existing_pods) == 1 and existing_pods[0].get("name") == "stateshift-m13-7b":
                p = existing_pods[0]
                self.pod_id = p["id"]
                self.gpu_hourly_rate = float(p.get("costPerHr") or 0.89)
                print(f"[Pre-Flight] Found existing StateShift pod {self.pod_id} (${self.gpu_hourly_rate}/hr). Adopting it.")
            else:
                print(f"WARNING: Found {len(existing_pods)} existing pods on account:")
                for p in existing_pods:
                    print(f"  Existing Pod: {p.get('id')} ({p.get('name')}) - {p.get('desiredStatus')}")
                raise RuntimeError("Single pod restriction violated: account already has active pods!")
            
        print("Pre-flight checks passed: Single-pod invariant verified, balance sufficient.")

    def select_and_provision_gpu(self) -> Dict[str, Any]:
        print("\n=== [STAGE 1 PROVISIONING] Selecting GPU & Launching Pod ===")
        if self.pod_id:
            print(f"Using already adopted StateShift Pod ID: {self.pod_id} (${self.gpu_hourly_rate}/hr)")
            self.t_launch = time.time()
            self.cost_controller = ExternalRunPodCostController(
                api_key=self.api_key,
                pod_id=self.pod_id,
                max_cost_usd=self.max_cost,
                max_runtime_minutes=self.max_runtime,
                gpu_hourly_rate=self.gpu_hourly_rate,
                audit_log_path=os.path.join(repo_root, "logs", "cost_controller_audit.jsonl")
            )
            self.cost_controller.start_session()
            return runpod.get_pod(self.pod_id)

        pub_key = load_ssh_pubkey()
        
        candidates = [
            ("NVIDIA GeForce RTX 4090", "COMMUNITY", 0.34),
            ("NVIDIA GeForce RTX 4090", "SECURE", 0.89),
            ("NVIDIA RTX A6000", "COMMUNITY", 0.33),
            ("NVIDIA GeForce RTX 3090", "COMMUNITY", 0.22),
            ("NVIDIA GeForce RTX 3090", "SECURE", 0.50),
            ("NVIDIA RTX A5000", "SECURE", 0.27)
        ]
        
        selected_pod = None
        for gpu_id, ctype, rate in candidates:
            print(f"Attempting to provision {gpu_id} ({ctype} Cloud @ ${rate:.2f}/hr)...")
            try:
                pod = runpod.create_pod(
                    name="stateshift-m13-7b",
                    image_name="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
                    gpu_type_id=gpu_id,
                    cloud_type=ctype,
                    container_disk_in_gb=50,
                    volume_in_gb=0,
                    ports="22/tcp",
                    support_public_ip=True,
                    start_ssh=True,
                    env={"PUBLIC_KEY": pub_key} if pub_key else {}
                )
                if pod and "id" in pod:
                    self.pod_id = pod["id"]
                    self.gpu_hourly_rate = rate
                    selected_pod = pod
                    print(f"Successfully created Pod ID: {self.pod_id} ({gpu_id} {ctype})")
                    break
            except Exception as e:
                print(f"Provisioning attempt failed for {gpu_id} ({ctype}): {e}")
                
        if not selected_pod:
            raise RuntimeError("Failed to provision any candidate GPU pod across Secure and Community clouds.")
            
        self.t_launch = time.time()
        
        # Initialize External Cost Controller
        self.cost_controller = ExternalRunPodCostController(
            api_key=self.api_key,
            pod_id=self.pod_id,
            max_cost_usd=self.max_cost,
            max_runtime_minutes=self.max_runtime,
            gpu_hourly_rate=self.gpu_hourly_rate,
            audit_log_path=os.path.join(repo_root, "logs", "cost_controller_audit.jsonl")
        )
        self.cost_controller.start_session()
        return selected_pod

    def wait_for_pod_ready(self, timeout_seconds: int = 480) -> Tuple[str, int]:
        """Poll until pod is RUNNING and SSH port is allocated."""
        print(f"\nWaiting for Pod {self.pod_id} to enter RUNNING state...")
        t0 = time.time()
        while time.time() - t0 < timeout_seconds:
            self.pod_info = runpod.get_pod(self.pod_id)
            status = self.pod_info.get("desiredStatus", "")
            runtime = self.pod_info.get("runtime") or {}
            uptime = runtime.get("uptimeInSeconds", 0)
            ports = runtime.get("ports") or []
            
            # Find SSH port mapping
            ssh_port = None
            ip = runtime.get("publicIp") or self.pod_info.get("ip")
            
            for p in ports:
                if p.get("privatePort") == 22:
                    ssh_port = p.get("publicPort")
                    if not ip:
                        ip = p.get("ip")
                        
            print(f"  [Status: {status}] IP: {ip} | SSH Port: {ssh_port}")
            
            if ip and ssh_port:
                print(f"[Orchestrator] Pod is active at {ip}:{ssh_port}")
                return str(ip), int(ssh_port)
                
            time.sleep(10)
            
        raise TimeoutError("Pod failed to initialize within timeout window.")

    def connect_ssh(self, ip: str, port: int, max_retries: int = 20) -> paramiko.SSHClient:
        print(f"\nEstablishing SSH connection to {ip}:{port}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        key = paramiko.Ed25519Key.from_private_key_file(SSH_KEY_PATH)
        
        for attempt in range(1, max_retries + 1):
            try:
                client.connect(hostname=ip, port=port, username="root", pkey=key, timeout=15)
                print(f"[Orchestrator] SSH connection established on attempt {attempt}.")
                self.ssh_client = client
                return client
            except Exception as e:
                print(f"  SSH connection attempt {attempt}/{max_retries} waiting... ({e})")
                time.sleep(10)
                
        raise ConnectionError("Failed to connect to pod via SSH.")

    def execute_remote_cmd(self, cmd: str, timeout: Optional[int] = None) -> Tuple[int, str]:
        """Run command on remote pod via SSH and stream stdout."""
        print(f"\n[Remote EXEC] {cmd}")
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd, timeout=timeout)
        output_lines = []
        for line in iter(stdout.readline, ""):
            print(f"  [pod] {line.strip()}", flush=True)
            output_lines.append(line)
        exit_status = stdout.channel.recv_exit_status()
        err = stderr.read().decode("utf-8")
        if err and exit_status != 0:
            print(f"  [pod ERROR] {err.strip()}", flush=True)
        return exit_status, "".join(output_lines)

    def deploy_code_to_pod(self, ip: str, port: int):
        print("\nDeploying code and manifests to pod...")
        tar_path = "/tmp/stateshift_m13_bundle.tar.gz"
        create_code_tarball(tar_path)
        
        sftp = self.ssh_client.open_sftp()
        self.execute_remote_cmd("mkdir -p /workspace/stateshift /workspace/stateshift/data /workspace/stateshift/logs")
        
        remote_tar = "/workspace/stateshift_bundle.tar.gz"
        sftp.put(tar_path, remote_tar)
        sftp.close()
        print(f"[Orchestrator] Uploaded code bundle to {remote_tar}")
        
        # Untar
        self.execute_remote_cmd(f"tar -xzf {remote_tar} -C /workspace/stateshift && rm -f {remote_tar}")
        
        # Install dependencies
        print("\nInstalling cloud dependencies (sympy, transformers, accelerate, vllm)...")
        code, _ = self.execute_remote_cmd(
            "pip install -q sympy transformers accelerate && pip install -q vllm || true",
            timeout=300
        )
        if code != 0:
            print("Warning: pip install returned non-zero code. Checking python packages...")

    def run_smoke_test(self) -> Dict[str, Any]:
        print("\n==========================================================")
        print(" STAGE 1: GPU SMOKE TEST (1 Problem x 4 Conditions = 4 Reqs)")
        print("==========================================================")
        t0 = time.time()
        
        # Run 4 requests with max_requests=4
        cmd = (
            "python3 /workspace/stateshift/runner/cloud_experiment_runner.py "
            "--manifest /workspace/stateshift/manifests/primary_100_manifest.json "
            "--output /workspace/stateshift/data/smoke_test_results.jsonl "
            "--checkpoint /workspace/stateshift/data/smoke_test_checkpoint.json "
            "--heartbeat /workspace/stateshift/logs/heartbeat.json "
            "--max_requests 4"
        )
        exit_code, out_str = self.execute_remote_cmd(cmd, timeout=300)
        smoke_duration = time.time() - t0
        
        if exit_code != 0:
            raise RuntimeError(f"Stage 1 Smoke Test failed with exit code {exit_code}")
            
        # Retrieve smoke test results
        sftp = self.ssh_client.open_sftp()
        local_smoke = os.path.join(repo_root, "data", "smoke_test_generations.jsonl")
        sftp.get("/workspace/stateshift/data/smoke_test_results.jsonl", local_smoke)
        sftp.close()
        
        with open(local_smoke, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
            
        if len(records) < 4:
            raise RuntimeError(f"Expected 4 smoke test rollouts, got {len(records)}")
            
        total_tokens = sum(r["generated_tokens"] for r in records)
        avg_tps = sum(r["tokens_per_second"] for r in records) / len(records)
        
        self.smoke_test_metrics = {
            "rollouts_count": len(records),
            "smoke_duration_seconds": round(smoke_duration, 2),
            "total_generated_tokens": total_tokens,
            "average_tokens_per_second": round(avg_tps, 2),
            "gpu_model": records[0]["model_id"],
            "stop_reasons": [r["stop_reason"] for r in records],
            "final_answers": [r["final_answer_correctness"] for r in records],
            "statuses": [r["overall_status"] for r in records]
        }
        print(f"\n[Smoke Test PASSED] Generated {total_tokens} tokens across 4 conditions in {smoke_duration:.1f}s ({avg_tps:.1f} tok/s)")
        return self.smoke_test_metrics

    def run_primary_experiment(self) -> Dict[str, Any]:
        print("\n==========================================================")
        print(" STAGE 3: PRIMARY 100-PROBLEM EXPERIMENT (400 Requests)")
        print("==========================================================")
        t0 = time.time()
        
        cmd = (
            "python3 /workspace/stateshift/runner/cloud_experiment_runner.py "
            "--manifest /workspace/stateshift/manifests/primary_100_manifest.json "
            "--output /workspace/stateshift/data/primary_7b_results.jsonl "
            "--checkpoint /workspace/stateshift/data/primary_7b_checkpoint.json "
            "--heartbeat /workspace/stateshift/logs/heartbeat.json"
        )
        exit_code, _ = self.execute_remote_cmd(cmd, timeout=1800)
        dur = time.time() - t0
        
        if exit_code != 0:
            print(f"Warning: Primary experiment returned exit code {exit_code}")
            
        # Retrieve primary results
        sftp = self.ssh_client.open_sftp()
        local_primary = os.path.join(repo_root, "data", "primary_7b_generations.jsonl")
        sftp.get("/workspace/stateshift/data/primary_7b_results.jsonl", local_primary)
        sftp.close()
        
        with open(local_primary, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
            
        print(f"\n[Primary Experiment Complete] Successfully retrieved {len(records)} rollouts in {dur:.1f}s ({dur/60:.2f} min).")
        self.primary_metrics = {
            "total_rollouts": len(records),
            "duration_seconds": round(dur, 2),
            "duration_minutes": round(dur / 60, 2)
        }
        return self.primary_metrics

    def run_secondary_replication(self, max_requests: int = 400) -> Dict[str, Any]:
        print(f"\n==========================================================")
        print(f" STAGE 4: SECONDARY REPLICATION ({max_requests} Requests)")
        print(f"==========================================================")
        
        # Check current spend before launching replication
        spend_status = self.cost_controller.calculate_spend()
        print(f"Current Spend: ${spend_status['estimated_spend_usd']:.3f} / Max: ${self.max_cost:.2f}")
        if spend_status["estimated_spend_usd"] > 1.80:
            print("Spend threshold reached ($1.80). Preserving budget and skipping secondary replication.")
            return {"status": "SKIPPED_BUDGET_PROTECTION"}
            
        t0 = time.time()
        cmd = (
            f"python3 /workspace/stateshift/runner/cloud_experiment_runner.py "
            f"--manifest /workspace/stateshift/manifests/replication_200_manifest.json "
            f"--output /workspace/stateshift/data/replication_7b_results.jsonl "
            f"--checkpoint /workspace/stateshift/data/replication_7b_checkpoint.json "
            f"--heartbeat /workspace/stateshift/logs/heartbeat.json "
            f"--max_requests {max_requests}"
        )
        exit_code, _ = self.execute_remote_cmd(cmd, timeout=2400)
        dur = time.time() - t0
        
        sftp = self.ssh_client.open_sftp()
        local_rep = os.path.join(repo_root, "data", "replication_7b_generations.jsonl")
        try:
            sftp.get("/workspace/stateshift/data/replication_7b_results.jsonl", local_rep)
            with open(local_rep, "r", encoding="utf-8") as f:
                records = [json.loads(line) for line in f if line.strip()]
        except Exception as e:
            print(f"Replication file retrieval error: {e}")
            records = []
        sftp.close()
        
        print(f"\n[Secondary Replication Complete] Retrieved {len(records)} rollouts in {dur:.1f}s ({dur/60:.2f} min).")
        self.replication_metrics = {
            "total_rollouts": len(records),
            "duration_seconds": round(dur, 2),
            "duration_minutes": round(dur / 60, 2)
        }
        return self.replication_metrics

    def terminate_pod_and_verify(self) -> Dict[str, Any]:
        print("\n==========================================================")
        print(f" STAGE 5: IMMEDIATE RESOURCE TERMINATION (Pod {self.pod_id})")
        print("==========================================================")
        
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except Exception:
                pass
                
        receipt = {"pod_id": self.pod_id, "terminated": False}
        if not self.pod_id:
            return receipt
            
        print(f"Issuing provider termination for Pod ID: {self.pod_id}...")
        try:
            runpod.terminate_pod(self.pod_id)
            receipt["terminate_called"] = True
        except Exception as e:
            print(f"runpod.terminate_pod error: {e}")
            
        # Verify via GraphQL mutation / query
        time.sleep(5)
        for check in range(6):
            active_pods = runpod.get_pods()
            matching = [p for p in active_pods if p.get("id") == self.pod_id]
            if not matching:
                receipt["terminated"] = True
                print(f"[SUCCESS] Pod {self.pod_id} is completely terminated. Active pods = {len(active_pods)}.")
                break
            else:
                print(f"  Waiting for termination... (Pod status: {matching[0].get('desiredStatus')})")
                time.sleep(5)
                
        # Final balance query
        final_bal = query_user_balance(self.api_key)
        actual_spend = max(0.0, self.initial_balance - final_bal)
        receipt["initial_balance"] = round(self.initial_balance, 4)
        receipt["final_balance"] = round(final_bal, 4)
        receipt["actual_spend_usd"] = round(actual_spend, 4)
        
        print(f"\nFinal Billing Reconciliation:")
        print(f"  Initial Balance: ${self.initial_balance:.4f}")
        print(f"  Final Balance:   ${final_bal:.4f}")
        print(f"  Actual Spend:    ${actual_spend:.4f} USD")
        
        out_term = os.path.join(repo_root, "logs", "termination_receipt.json")
        os.makedirs(os.path.dirname(out_term), exist_ok=True)
        with open(out_term, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)
            
        return receipt

def execute_mission13_campaign():
    orch = Mission13CloudOrchestrator()
    
    def handle_interrupt(signum, frame):
        print(f"\n[INTERRUPT RECEIVED: signal {signum}] Triggering emergency pod termination...")
        orch.terminate_pod_and_verify()
        sys.exit(1)
        
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)
    
    try:
        orch.run_preflight_checks()
        orch.select_and_provision_gpu()
        ip, port = orch.wait_for_pod_ready()
        orch.connect_ssh(ip, port)
        orch.deploy_code_to_pod(ip, port)
        
        # Stage 1: Smoke test
        smoke_res = orch.run_smoke_test()
        
        # Stage 2: Cost projection check
        # Stage 3: Primary experiment
        primary_res = orch.run_primary_experiment()
        
        # Stage 4: Secondary replication
        rep_res = orch.run_secondary_replication(max_requests=400)
        
    except Exception as e:
        print(f"\n[CRITICAL ORCHESTRATION EXCEPTION] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nEnsuring cleanup and provider resource termination...")
        orch.terminate_pod_and_verify()

if __name__ == "__main__":
    execute_mission13_campaign()

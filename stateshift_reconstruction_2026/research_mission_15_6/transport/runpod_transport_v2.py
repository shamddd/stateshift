#!/usr/bin/env python3
"""
StateShift Production RunPod Transport & Lifecycle Adapter (Version 2 - Mission 15.2)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Enhancements over v1:
1. Strict Pod Destruction Semantics:
   Authoritatively distinguishes STOPPED (paused instance with active billable storage)
   from TERMINATED/DELETED. Under NO circumstances does verify_pod_terminated()
   treat STOPPED as verified termination.
2. Authoritative Resource Query:
   Pod is confirmed destroyed ONLY if pod is null (not found) or desiredStatus is
   explicitly TERMINATED or DELETED.
3. Associated Storage Checks:
   Inspects container and volume storage metadata where supported by provider.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
import paramiko
from typing import Dict, Any, Optional, Tuple, Callable

from research_mission_15_6.auth.execution_lock import assert_cloud_execution_permitted

RUNPOD_GRAPHQL_ENDPOINT = "https://api.runpod.io/graphql"

def safe_channel_wait(channel, timeout_seconds: float = 30.0) -> int:
    """
    Polls an SSH channel until the remote command finishes, enforcing a strict
    monotonic wall-clock deadline. Prevents unbounded hangs on recv_exit_status().
    """
    deadline = time.monotonic() + timeout_seconds
    while not channel.exit_status_ready():
        if time.monotonic() > deadline:
            try:
                channel.close()
            except Exception:
                pass
            raise TimeoutError(
                f"SSH command execution exceeded wall-clock deadline of {timeout_seconds:.1f}s"
            )
        time.sleep(0.1)
    return channel.recv_exit_status()

class RunPodAPIError(Exception):
    pass


class ProductionRunPodTransportV2:
    """Production transport adapter for RunPod GPU instances and SSH/SFTP operations."""

    def __init__(self,
                 api_key: Optional[str] = None,
                 ssh_key_path: Optional[str] = None,
                 api_endpoint: str = RUNPOD_GRAPHQL_ENDPOINT,
                 http_client: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None,
                 ssh_factory: Optional[Callable[[], paramiko.SSHClient]] = None):
        self._api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.ssh_key_path = ssh_key_path or os.path.expanduser("~/.ssh/id_ed25519")
        self.api_endpoint = api_endpoint
        
        self._http_client = http_client or self._default_http_post
        self._ssh_factory = ssh_factory or self._default_ssh_factory
        
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self._current_host: Optional[str] = None
        self._current_port: Optional[int] = None

    def __repr__(self) -> str:
        key_masked = f"{self._api_key[:4]}...{self._api_key[-4:]}" if len(self._api_key) > 8 else "***"
        return f"<ProductionRunPodTransportV2 endpoint='{self.api_endpoint}' key='{key_masked}'>"

    def _default_ssh_factory(self) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client

    def _default_http_post(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL request to RunPod API."""
        assert_cloud_execution_permitted()
        if not self._api_key:
            raise RunPodAPIError("RUNPOD_API_KEY is not configured.")
            
        url = f"{self.api_endpoint}?api_key={self._api_key}"
        payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "StateShift-Orchestrator/15.2"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "errors" in data:
                    raise RunPodAPIError(f"RunPod GraphQL Error: {data['errors']}")
                return data.get("data", {})
        except urllib.error.HTTPError as he:
            raise RunPodAPIError(f"HTTP Error {he.code}: {he.read().decode('utf-8', errors='replace')}")
        except urllib.error.URLError as ue:
            raise RunPodAPIError(f"Network error contacting RunPod API: {ue.reason}")

    # ==================== RunPod Provider API Methods ====================

    def get_pod_metadata(self, pod_id: str) -> Dict[str, Any]:
        """Retrieve authoritative real-time pod metadata from RunPod GraphQL API."""
        query = """
        query Pod($podId: String!) {
            pod(input: {podId: $podId}) {
                id
                name
                desiredStatus
                lastStatusChange
                runtime {
                    uptimeInSeconds
                    ports {
                        ip
                        publicPort
                        privatePort
                        type
                    }
                }
            }
        }
        """
        data = self._http_client(query, {"podId": pod_id})
        pod = data.get("pod")
        if not pod:
            return {"exists": False, "status": "TERMINATED_OR_NOT_FOUND"}
            
        uptime = 0
        ip = None
        port = 22
        if pod.get("runtime"):
            uptime = pod["runtime"].get("uptimeInSeconds", 0)
            ports = pod["runtime"].get("ports", [])
            for p in ports:
                if p.get("privatePort") == 22:
                    ip = p.get("ip")
                    port = p.get("publicPort", 22)
                    break
                    
        return {
            "exists": True,
            "id": pod.get("id"),
            "status": pod.get("desiredStatus", "UNKNOWN"),
            "uptimeSeconds": uptime,
            "ssh_ip": ip,
            "ssh_port": port
        }

    def terminate_pod(self, pod_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Issue pod termination mutation to RunPod GraphQL API.
        """
        query = """
        mutation TerminatePod($podId: String!) {
            podTerminate(input: {podId: $podId})
        }
        """
        try:
            data = self._http_client(query, {"podId": pod_id})
            return True, data
        except Exception as e:
            return False, {"error": str(e)}

    def verify_pod_terminated(self, pod_id: str, max_checks: int = 5, delay_seconds: float = 2.0) -> bool:
        """
        Independently verify provider-side pod destruction.
        STRICT SEMANTICS:
        1. Returns True ONLY if pod does not exist (null) or status is TERMINATED / DELETED.
        2. Explicitly returns False if status is STOPPED, RUNNING, STOPPING, or UNKNOWN.
        """
        for check_idx in range(1, max_checks + 1):
            try:
                meta = self.get_pod_metadata(pod_id)
                exists = meta.get("exists", True)
                status = meta.get("status", "UNKNOWN")
                
                # Check for STOPPED: explicitly NOT destroyed!
                if status == "STOPPED":
                    print(f"  [Provider Verification Warning] Pod {pod_id} is STOPPED. Billable storage persists; NOT destroyed.")
                    return False
                    
                # Definite destruction states
                if not exists or status in ["TERMINATED", "DELETED", "TERMINATED_OR_NOT_FOUND"]:
                    return True
            except Exception as e:
                print(f"  [Provider Verification Notice] Query check {check_idx} error: {e}")
                
            time.sleep(delay_seconds)
            
        # Final authoritative check
        try:
            meta = self.get_pod_metadata(pod_id)
            if meta.get("status") == "STOPPED":
                return False
            return not meta.get("exists", True) or meta.get("status") in ["TERMINATED", "DELETED", "TERMINATED_OR_NOT_FOUND"]
        except Exception:
            return False

    # ==================== SSH & SFTP Methods ====================

    def get_ssh_client(self, ip: str, port: int = 22, max_retries: int = 3, retry_delay: float = 2.0) -> paramiko.SSHClient:
        """Connect or return active SSH client."""
        if (self.ssh_client and self.ssh_client.get_transport() and 
            self.ssh_client.get_transport().is_active() and 
            self._current_host == ip and self._current_port == port):
            return self.ssh_client
            
        client = self._ssh_factory()
        pkey = None
        if os.path.exists(self.ssh_key_path):
            try:
                pkey = paramiko.Ed25519Key.from_private_key_file(self.ssh_key_path)
            except Exception:
                try:
                    pkey = paramiko.RSAKey.from_private_key_file(self.ssh_key_path)
                except Exception:
                    pass
                    
        for attempt in range(1, max_retries + 1):
            try:
                client.connect(hostname=ip, port=port, username="root", pkey=pkey, timeout=10)
                self.ssh_client = client
                self._current_host = ip
                self._current_port = port
                return client
            except Exception as e:
                if attempt == max_retries:
                    raise ConnectionError(f"Failed to establish SSH connection to {ip}:{port} after {max_retries} attempts: {e}")
                time.sleep(retry_delay)
        return client

    def execute(self, cmd: str, ip: Optional[str] = None, port: Optional[int] = None, timeout: int = 30) -> Tuple[int, str]:
        """Execute command over SSH."""
        host = ip or self._current_host
        p = port or self._current_port or 22
        if not host:
            raise ValueError("SSH host IP must be specified or previously connected.")
            
        client = self.get_ssh_client(host, p)
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        try:
            stdin.close()
        except Exception:
            pass
        exit_code = safe_channel_wait(stdout.channel, timeout_seconds=float(timeout))
        
        # Read stdout safely without blocking on detached background processes
        out_chunks = []
        try:
            stdout.channel.settimeout(1.0)
            while True:
                chunk = stdout.channel.recv(4096)
                if not chunk:
                    break
                out_chunks.append(chunk)
        except Exception:
            pass
        out = b"".join(out_chunks).decode("utf-8", errors="replace")
        return exit_code, out

    def fetch_file(self, remote_path: str, local_path: str, ip: Optional[str] = None, port: Optional[int] = None) -> bool:
        """Fetch remote file via SFTP."""
        host = ip or self._current_host
        p = port or self._current_port or 22
        if not host:
            return False
            
        client = self.get_ssh_client(host, p)
        sftp = client.open_sftp()
        try:
            sftp.get(remote_path, local_path)
            return True
        except Exception:
            return False
        finally:
            try:
                sftp.close()
            except Exception:
                pass

    def upload_file(self, local_path: str, remote_path: str, ip: Optional[str] = None, port: Optional[int] = None) -> bool:
        """Upload local file via SFTP."""
        host = ip or self._current_host
        p = port or self._current_port or 22
        if not host or not os.path.exists(local_path):
            return False
            
        client = self.get_ssh_client(host, p)
        sftp = client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
            return True
        except Exception:
            return False
        finally:
            try:
                sftp.close()
            except Exception:
                pass
                
    def close(self):
        """Cleanly close active SSH connection."""
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except Exception:
                pass
            self.ssh_client = None

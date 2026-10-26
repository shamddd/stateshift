#!/usr/bin/env python3
"""
Mission 15.2 Unit Tests: Provider Pod Destruction Verification
Verifies strict semantics of ProductionRunPodTransportV2:
- Pod STOPPED must return False (storage remains billable)
- Pod RUNNING / STOPPING must return False
- Pod TERMINATED / DELETED / Not Found must return True
- Network errors or malformed payloads must return False (failsafe)
"""

import sys
import os
import pytest
import json
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from research_mission_15_2.transport.runpod_transport_v2 import ProductionRunPodTransportV2, RunPodAPIError


def test_verify_pod_terminated_stopped_returns_false():
    """Verify that STOPPED pods return False because billable volume persists."""
    mock_http = MagicMock()
    # Return pod metadata with status STOPPED
    mock_http.return_value = {
        "pod": {
            "id": "pod-123",
            "name": "stateshift-gpu",
            "desiredStatus": "STOPPED",
            "runtime": None
        }
    }
    
    transport = ProductionRunPodTransportV2(
        api_key="mock_key",
        http_client=mock_http
    )
    
    # Should immediately recognize STOPPED and return False
    result = transport.verify_pod_terminated("pod-123", max_checks=1, delay_seconds=0.01)
    assert result is False, "STOPPED pod must return False since volume billing persists"


def test_verify_pod_terminated_running_returns_false():
    """Verify that RUNNING pods return False."""
    mock_http = MagicMock()
    mock_http.return_value = {
        "pod": {
            "id": "pod-123",
            "name": "stateshift-gpu",
            "desiredStatus": "RUNNING",
            "runtime": {"uptimeInSeconds": 100, "ports": []}
        }
    }
    
    transport = ProductionRunPodTransportV2(
        api_key="mock_key",
        http_client=mock_http
    )
    
    result = transport.verify_pod_terminated("pod-123", max_checks=2, delay_seconds=0.01)
    assert result is False, "RUNNING pod must return False"


def test_verify_pod_terminated_stopping_returns_false():
    """Verify that STOPPING pods return False."""
    mock_http = MagicMock()
    mock_http.return_value = {
        "pod": {
            "id": "pod-123",
            "name": "stateshift-gpu",
            "desiredStatus": "STOPPING",
            "runtime": None
        }
    }
    
    transport = ProductionRunPodTransportV2(
        api_key="mock_key",
        http_client=mock_http
    )
    
    result = transport.verify_pod_terminated("pod-123", max_checks=2, delay_seconds=0.01)
    assert result is False, "STOPPING pod must return False"


def test_verify_pod_terminated_terminated_status_returns_true():
    """Verify that TERMINATED status returns True."""
    mock_http = MagicMock()
    mock_http.return_value = {
        "pod": {
            "id": "pod-123",
            "desiredStatus": "TERMINATED",
            "runtime": None
        }
    }
    
    transport = ProductionRunPodTransportV2(
        api_key="mock_key",
        http_client=mock_http
    )
    
    result = transport.verify_pod_terminated("pod-123", max_checks=1, delay_seconds=0.01)
    assert result is True, "TERMINATED pod must return True"


def test_verify_pod_terminated_deleted_status_returns_true():
    """Verify that DELETED status returns True."""
    mock_http = MagicMock()
    mock_http.return_value = {
        "pod": {
            "id": "pod-123",
            "desiredStatus": "DELETED",
            "runtime": None
        }
    }
    
    transport = ProductionRunPodTransportV2(
        api_key="mock_key",
        http_client=mock_http
    )
    
    result = transport.verify_pod_terminated("pod-123", max_checks=1, delay_seconds=0.01)
    assert result is True, "DELETED pod must return True"


def test_verify_pod_terminated_null_pod_returns_true():
    """Verify that null pod (pod not found / destroyed) returns True."""
    mock_http = MagicMock()
    mock_http.return_value = {
        "pod": None
    }
    
    transport = ProductionRunPodTransportV2(
        api_key="mock_key",
        http_client=mock_http
    )
    
    result = transport.verify_pod_terminated("pod-123", max_checks=1, delay_seconds=0.01)
    assert result is True, "Null pod (not found) confirms destruction"


def test_verify_pod_terminated_http_error_returns_false():
    """Verify that persistent HTTP / API errors return False (failsafe)."""
    mock_http = MagicMock()
    mock_http.side_effect = RunPodAPIError("503 Service Unavailable")
    
    transport = ProductionRunPodTransportV2(
        api_key="mock_key",
        http_client=mock_http
    )
    
    result = transport.verify_pod_terminated("pod-123", max_checks=2, delay_seconds=0.01)
    assert result is False, "Unconfirmed destruction on network failure must return False"


def test_verify_pod_terminated_transient_error_then_terminated():
    """Verify that transient network errors followed by TERMINATED return True."""
    mock_http = MagicMock()
    mock_http.side_effect = [
        RunPodAPIError("500 Internal Server Error"),
        {"pod": {"id": "pod-123", "desiredStatus": "TERMINATED"}}
    ]
    
    transport = ProductionRunPodTransportV2(
        api_key="mock_key",
        http_client=mock_http
    )
    
    result = transport.verify_pod_terminated("pod-123", max_checks=3, delay_seconds=0.01)
    assert result is True, "Transient error followed by confirmed termination must return True"

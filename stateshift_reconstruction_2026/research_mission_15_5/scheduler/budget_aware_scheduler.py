#!/usr/bin/env python3
"""
StateShift Budget-Aware Experiment Scheduler (Mission 15.3)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference (Secondary: TMLR)

Ensures that no batch is dispatched unless the remaining authorized budget
can safely accommodate the batch generation plus the mandatory shutdown reserve.
If the budget cannot safely support the next batch, scheduling halts with
status PARTIAL_BUDGET_STOP, preserving already completed rollouts.
"""

import time
from typing import Dict, Any, List, Optional, Tuple


class BudgetAwareScheduler:
    """Predictive scheduler for GPU batch inference under strict financial bounds."""

    def __init__(
        self,
        max_authorized_usd: float = 2.00,
        safety_reserve_usd: float = 0.35,
        gpu_hourly_rate: float = 0.89,
        estimated_shutdown_overhead_seconds: float = 90.0,
        initial_tokens_per_second: float = 41.0,
        default_tokens_per_request: float = 550.0
    ):
        self.max_authorized_usd = max_authorized_usd
        self.safety_reserve_usd = safety_reserve_usd
        self.gpu_hourly_rate = gpu_hourly_rate
        self.shutdown_overhead_cost = (estimated_shutdown_overhead_seconds / 3600.0) * gpu_hourly_rate
        
        # Performance estimators
        self.tokens_per_second = initial_tokens_per_second
        self.default_tokens_per_request = default_tokens_per_request
        self.observed_request_latencies: List[float] = []
        self.observed_output_lengths: List[int] = []

    def update_observed_metrics(self, latency_seconds: float, generated_tokens: int):
        """Update rolling execution metrics from completed requests."""
        if latency_seconds > 0:
            self.observed_request_latencies.append(latency_seconds)
            self.observed_output_lengths.append(generated_tokens)
            # Rolling window of last 20 requests
            recent_latencies = self.observed_request_latencies[-20:]
            recent_tokens = self.observed_output_lengths[-20:]
            total_time = sum(recent_latencies)
            total_toks = sum(recent_tokens)
            if total_time > 0:
                self.tokens_per_second = total_toks / total_time
            if len(recent_tokens) > 0:
                self.default_tokens_per_request = sum(recent_tokens) / len(recent_tokens)

    def estimate_batch_cost(self, batch_size: int, concurrency: int = 4) -> Tuple[float, float]:
        """
        Estimates runtime and monetary cost for the next batch.
        Returns: (estimated_runtime_seconds, estimated_cost_usd)
        """
        # Effective sequential passes needed
        passes = max(1, (batch_size + concurrency - 1) // concurrency)
        
        # Estimate seconds per pass
        if self.observed_request_latencies:
            avg_lat = sum(self.observed_request_latencies[-10:]) / len(self.observed_request_latencies[-10:])
        else:
            avg_lat = self.default_tokens_per_request / max(1.0, self.tokens_per_second)
            
        est_seconds = passes * avg_lat
        est_cost_usd = (est_seconds / 3600.0) * self.gpu_hourly_rate
        return est_seconds, est_cost_usd

    def can_schedule_next_batch(
        self,
        batch_size: int,
        current_spend_usd: float,
        concurrency: int = 4
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluates whether the next batch can be safely dispatched without
        infringing upon the safety reserve or authorized budget ceiling.
        """
        est_seconds, est_batch_cost = self.estimate_batch_cost(batch_size, concurrency)
        
        # Total required headroom = batch cost + mandatory reserve + shutdown overhead
        required_headroom = est_batch_cost + self.safety_reserve_usd + self.shutdown_overhead_cost
        projected_spend_after_batch = current_spend_usd + est_batch_cost
        effective_limit = self.max_authorized_usd - self.safety_reserve_usd - self.shutdown_overhead_cost
        
        decision_meta = {
            "batch_size": batch_size,
            "current_spend_usd": round(current_spend_usd, 4),
            "estimated_batch_cost_usd": round(est_batch_cost, 4),
            "estimated_batch_seconds": round(est_seconds, 2),
            "safety_reserve_usd": self.safety_reserve_usd,
            "shutdown_overhead_usd": round(self.shutdown_overhead_cost, 4),
            "projected_spend_after_batch": round(projected_spend_after_batch, 4),
            "effective_spending_ceiling": round(effective_limit, 4),
            "tokens_per_second_estimate": round(self.tokens_per_second, 2)
        }

        if projected_spend_after_batch > effective_limit:
            reason = (
                f"Projected spend ${projected_spend_after_batch:.4f} breaches effective spending ceiling "
                f"${effective_limit:.4f} (budget ${self.max_authorized_usd:.2f} less reserve ${self.safety_reserve_usd:.2f} and shutdown overhead ${self.shutdown_overhead_cost:.4f})."
            )
            return False, "PARTIAL_BUDGET_STOP", decision_meta

        return True, "CAN_SCHEDULE", decision_meta

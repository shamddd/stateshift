#!/usr/bin/env python3
"""
Generate GPU Price and Runtime Comparison Table (Mission 12)
Author: Sham Satish Thakare (github.com/shamddd)
Target: NeurIPS 2027 Main Conference
"""

import os
import csv

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(repo_root, "11_GPU_PRICE_AND_RUNTIME_COMPARISON.csv")

headers = [
    "GPU_Model", "VRAM_GB", "Cloud_Type", "Hourly_Rate_USD", "VLLM_Throughput_tok_s",
    "Model_Fit_7B_bf16", "Startup_Overhead_min", "Pilot_Inference_min", "Pilot_Total_min",
    "Pilot_Cost_USD", "Full_Replication_Total_min", "Full_Replication_Cost_USD", "Recommendation"
]

rows = [
    ["NVIDIA RTX 4090", 24, "Secure Cloud", 0.74, 75.0, "EXCELLENT (14GB weights + 4GB KV)", 3.0, 3.6, 6.6, 0.081, 38.6, 0.476, "RECOMMENDED (Optimal speed/cost)"],
    ["NVIDIA RTX A5000", 24, "Secure Cloud", 0.49, 45.0, "EXCELLENT (14GB weights + 4GB KV)", 3.0, 5.9, 8.9, 0.073, 62.2, 0.508, "ALTERNATIVE (Budget constrained)"],
    ["NVIDIA RTX 3090", 24, "Community Cloud", 0.29, 42.0, "GOOD (PCIe / reliability varies)", 4.0, 6.3, 10.3, 0.050, 67.5, 0.326, "NOT RECOMMENDED (Network variance)"],
    ["NVIDIA L40S", 48, "Secure Cloud", 1.09, 85.0, "OVERPROVISIONED (24GB excess)", 3.0, 3.1, 6.1, 0.111, 34.4, 0.625, "UNNECESSARY (Excess VRAM)"],
    ["NVIDIA A100-SXM4", 80, "Secure Cloud", 1.89, 110.0, "OVERPROVISIONED (62GB excess)", 3.0, 2.4, 5.4, 0.170, 27.2, 0.857, "UNNECESSARY (High hourly cost)"],
    ["NVIDIA H100-SXM5", 80, "Secure Cloud", 3.49, 160.0, "OVERPROVISIONED (62GB excess)", 3.0, 1.7, 4.7, 0.273, 19.7, 1.146, "PROHIBITIVE (Excessive rate)"]
]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Generated: {csv_path}")

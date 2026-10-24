# StateShift Reproducible RunPod GPU Container (Mission 12)
# Base: PyTorch 2.4.0 with CUDA 12.4 and cuDNN 9
FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    ca-certificates \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

# Ensure workspace directories exist
RUN mkdir -p /workspace/output /workspace/checkpoints /workspace/logs /workspace/evaluation /root/.cache/huggingface

# Copy runner, evaluation subsystem, and scripts
COPY evaluation/ /workspace/evaluation/
COPY cloud_experiment_runner.py /workspace/cloud_experiment_runner.py
COPY external_cost_controller.py /workspace/external_cost_controller.py
COPY pod_lifecycle_monitor.py /workspace/pod_lifecycle_monitor.py
COPY secure_launcher.sh /workspace/secure_launcher.sh
RUN chmod +x /workspace/secure_launcher.sh

CMD ["/bin/bash", "/workspace/secure_launcher.sh"]

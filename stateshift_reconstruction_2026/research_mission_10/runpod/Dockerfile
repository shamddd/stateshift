FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

WORKDIR /workspace

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget jq bc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy experiment runners and benchmarks
COPY cloud_experiment_runner.py /workspace/
COPY secure_launcher.sh /workspace/
RUN chmod +x /workspace/secure_launcher.sh

ENV PYTHONUNBUFFERED=1
CMD ["bash"]

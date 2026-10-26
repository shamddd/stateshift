# RunPod Cloud Execution Package (StateShift Mission 13)

To prevent Python package shadowing with the official `runpod` Python client library (`import runpod` from PyPI `site-packages`), active runner and orchestration modules are maintained in `runner/`:

- `runner/orchestrator_mission13.py`: Autonomous cloud provisioning, multi-stage execution, cost control, and resource termination engine.
- `runner/cloud_experiment_runner.py`: High-throughput GPU inference runner with native vLLM continuous batching and inline Evaluator v4 scoring.
- `runner/external_cost_controller.py`: Independent external financial watchdog enforcing strict $2.80 safety ceiling and runtime timeouts.
- `runner/pod_lifecycle_monitor.py`: Background lifecycle and heartbeat monitor.
- `runner/authorization_validator.py`: Zero-trust pre-flight authorization and balance validator.
- `runner/secure_launcher.sh`: Container entrypoint script.
- `runner/Dockerfile`: Minimal CUDA-enabled reproducibility environment specification.

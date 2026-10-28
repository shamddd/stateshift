# StateShift Computational Environment Specification

## 1. Operating Systems & Hardware
- **Local CPU Audit Platform**: macOS (Apple Silicon M1, 8 cores, 16GB RAM)
- **Linux CI Platform**: Ubuntu 22.04 LTS (x86_64, GitHub Actions runner)
- **Cloud GPU Platform (Mission 23 Inferences)**: RunPod Secure Cloud, 1x NVIDIA GeForce RTX 4090 (24GB VRAM), Driver 595.91.07, CUDA 12.4

## 2. Python Runtime & Core Libraries
- **Python**: 3.10.x, 3.11.x, 3.12.x, or 3.13.x (Tested clean across all versions)
- **NumPy**: `numpy>=1.24.0` (Local verification: `2.2.3`)
- **Pandas**: `pandas>=2.0.0` (Local verification: `2.2.3`)
- **SciPy**: `scipy>=1.10.0` (Local verification: `1.15.2`)
- **Statsmodels**: `statsmodels>=0.14.0` (Local verification: `0.14.4`)
- **SymPy**: `sympy>=1.12` (Local verification: `1.13.3`)
- **Pytest**: `pytest>=7.0.0` (Local verification: `8.4.2`)

## 3. LaTeX Compilation Engine
- **Engine**: `tectonic 0.15.0` (or higher) self-contained XeTeX compiler.
- **Required Packages (embedded in modern TeXLive/Tectonic)**:
  `amsmath`, `amssymb`, `amsfonts`, `amsthm`, `booktabs`, `graphicx`, `hyperref`, `xcolor`, `geometry`, `microtype`, `subcaption`.

## 4. Model Provenance
- **Model Name**: `Qwen/Qwen2.5-Math-7B-Instruct`
- **Pinned Checkpoint SHA**: `ef9926d75ab1d54532f6a30dd5e760355eb9aa4d`
- **Decoding Configuration**:
  ```python
  sampling_params = {
      "temperature": 0.0,
      "max_tokens": 768,
      "seed": 42
  }
  ```

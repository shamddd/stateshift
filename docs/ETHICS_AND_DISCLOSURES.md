# Project StateShift: Ethics, Disclosures & Computational Budget Statement

**Principal Investigator**: Sham Satish Thakare (`github.com/shamddd`)
**Project**: StateShift: Tracking State-Dependent Reasoning Recovery Across Post-Training

---

## 1. Computational Budget & Financial Disclosure

* **Cloud Infrastructure**: Cloud execution was performed using RunPod Secure Cloud instances.
* **GPU Hardware**: A single NVIDIA RTX 4090 ($24\text{ GB}$ VRAM) was provisioned for physical inference.
* **Expenditure Accounting**:
  * Authorized budget: $\$1.00$ USD ceiling.
  * Actual calibration spend: $\$0.2110$ USD.
  * Remaining account balance: $\$10.1065$ USD preserved intact.
  * Total GPU wall-clock time across calibration and primary execution was under 45 minutes.
* **Execution Safety Lock**: Following completion of the authorized physical GPU runs, the fail-closed cloud execution lock (`.cloud_execution_locked`) was immediately engaged to ensure zero ongoing cloud spend.

---

## 2. Benchmark Usage & Licensing

* **Evaluation Benchmarks**:
  * **MATH-500**: Used for Study 2 evaluation under open academic research terms.
  * **AIME / Olympiad Benchmarks**: Used for Study 1 checkpoint evaluation under fair academic research use.
* **Model Licensing**:
  * `Qwen/Qwen2.5-Math-7B-Instruct`: Subject to the official Qwen License Agreement permitting non-commercial and commercial research and deployment under stated thresholds.
  * `DeepScaleR-7B`: Subject to the DeepScaleR permissive research release.

---

## 3. Human Authorship & Automated Assistant Governance

* **Human Authorship**: Principal Investigator Sham Satish Thakare holds exclusive authorial sovereignty and final approval rights.
* **AI Assistance**: Automated coding assistants were utilized exclusively for code reconstruction, unit testing, formatting verification, and statistical verification. All final publication decisions, scientific interpretations, and checklist sign-offs are reserved for the human author (`AUTHOR_FINAL_APPROVAL_CHECKLIST.md`).
* **Simulated Reviews**: Internal simulated adversarial peer-review reports are explicitly marked as internal simulated evaluations and must not be represented as external peer review or conference acceptance.

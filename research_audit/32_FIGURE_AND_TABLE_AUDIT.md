# StateShift Figure and Table Scientific Integrity Audit

**Audit Date**: October 18, 2026  
**Auditor**: Lead Visualization & Numerical Consistency Auditor  

---

## 1. Figure Audits

### Figure 1: Experimental Design & Recovery Evaluation Framework
- **Source Graphic**: `figures/figure1_framework.pdf` & `figure1_framework.png`
- **Content**: Illustrates problem input $Q_i$, bifurcation into Recovery prefix $P_{i,R}$ (invalid step) and Control prefix $P_{i,C}$ (matched valid step), model decoding continuation, and SymPy verifier outcome $Y \in \{0, 1\}$.
- **Axes & Annotations**: Diagrammatic flowchart. Zero unsupported causal assertions. Verified accurate.

### Figure 2: Full Nine-Checkpoint Interaction Trajectory ($\Gamma_t$)
- **Source Graphic**: `figures/figure2_trajectory.pdf` & `figure2_trajectory.png`
- **Data Source**: `nine_checkpoint_trajectory.csv` & `intermediate_checkpoint_cell_means.csv`
- **Axes**: X-axis: RL Training Steps $t \in \{0, 32, \dots, 256\}$; Y-axis: Interaction Contrast $\Gamma_t$ (percentage points).
- **Uncertainty**: Error bars represent $95\%$ problem-blocked bootstrap confidence intervals.
- **Integrity Note**: Fluctuations at $t=160$ and $t=224$ are clearly displayed without smoothing. Verified accurate.

### Figure 3: Absolute Cell Success Rates Across Checkpoints
- **Source Graphic**: `figures/figure3_cell_means.pdf` & `figure3_cell_means.png`
- **Data Source**: `controlled_endpoint_outcomes.csv` & `intermediate_rollouts.jsonl`
- **Curves**: Plots $\mu_{R,t}$ (Recovery success) and $\mu_{C,t}$ (Control success) across all 9 checkpoints.
- **Verified Values**: Correctly plots $\mu_{R,0}=38.34\%, \mu_{R,256}=70.39\%, \mu_{C,0}=38.92\%, \mu_{C,256}=59.21\%$.

### Figure 4: Natural Post-Error Recovery Funnel (Study B)
- **Source Graphic**: `figures/figure4_funnel.pdf` & `figure4_funnel.png`
- **Data Source**: `natural_error_episodes.csv` & `natural_recovery_episodes.csv`
- **Values**: Total Rollouts ($3,200$) $\to$ Verifier-Confirmed Natural Errors ($582, 18.19\%$) $\to$ Autonomous Recoveries ($180, 30.93\%$). Verified exact.

---

## 2. Table Audits

- **Table 1 (Primary Endpoint)**: Matches `controlled_endpoint_outcomes.csv` with zero rounding error.
- **Table 2 (9-Checkpoint Trajectory)**: Matches `nine_checkpoint_trajectory.csv` and `intermediate_checkpoint_cell_means.csv`.
- **Table 3 (Study B Natural Recovery)**: Matches `natural_error_episodes.csv` and `natural_recovery_episodes.csv`.

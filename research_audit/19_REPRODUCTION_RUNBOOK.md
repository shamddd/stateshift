# StateShift Reproduction Runbook (CPU-Deterministic)

**Audit Date**: October 18, 2026  
**Execution Environment**: macOS / Linux (x86_64 or Apple Silicon ARM64)  
**Hardware Requirements**: Standard CPU (>= 8 GB RAM, no GPU required for statistical reproduction)  

---

## 1. Quickstart: 3-Command Verification

To reproduce all headline statistics, tables, and blocked bootstrap intervals:

```bash
# 1. Clone repository / enter project directory
cd stateshift

# 2. Install lightweight statistical dependencies
pip install -r requirements-stats.txt # pandas, numpy, scipy

# 3. Execute deterministic reproduction suite
python -m stateshift.statistics.reproduce_all
```

---

## 2. Granular Step-by-Step Reproduction

### Step 1: Verify Raw Dataset Integrity
Verify that `controlled_endpoint_outcomes.csv` matches the official SHA-256 hash:
```bash
shasum -a 256 artifacts/endpoint/controlled_endpoint_outcomes.csv
# Expected: 49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139
```

### Step 2: Recompute Primary Confirmatory Endpoint (Table 1)
```bash
python -c "
import pandas as pd
df = pd.read_csv('artifacts/endpoint/controlled_endpoint_outcomes.csv')
p = df.pivot_table(index='pair_id', columns=['state_type', 'checkpoint_t'], values='target_transition_success', aggfunc='mean')
gamma = (p[('recovery', 256)] - p[('recovery', 0)]) - (p[('control', 256)] - p[('control', 0)])
print('Gamma_256:', gamma.mean())
"
```

### Step 3: Reproduce 9-Point Trajectory (Table 2)
```bash
cat artifacts/trajectory/nine_checkpoint_trajectory.csv
```

### Step 4: Reproduce Natural Post-Error Recovery (Table 3)
```bash
python -c "
import pandas as pd
err = pd.read_csv('artifacts/natural_recovery/natural_error_episodes.csv')
rec = pd.read_csv('artifacts/natural_recovery/natural_recovery_episodes.csv')
print(f'NEI: {len(err)}/3200 = {len(err)/3200:.4%}')
print(f'NRR: {len(rec)}/{len(err)} = {len(rec)/len(err):.4%}')
"
```

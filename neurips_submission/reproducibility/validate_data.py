import os
import hashlib
import pandas as pd

def resolve_path(subpath):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "..", subpath),
        os.path.join(base_dir, subpath),
        os.path.join(os.getcwd(), subpath),
        os.path.join(base_dir, "..", "..", subpath),
        os.path.join("/Users/shamthakare/.gemini/antigravity/scratch/website_clone", subpath)
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

def get_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def check_data():
    print("=== [2] DATASET INTEGRITY & PROVENANCE VALIDATION ===")
    data_path = resolve_path("artifacts/endpoint/controlled_endpoint_outcomes.csv")
    assert os.path.exists(data_path), f"File missing: {data_path}"
    
    sha = get_sha256(data_path)
    expected_sha = "49549bbd73349bb0e1879603bdbeb04c4a8617ab85d0b31323cfeb188a5c6139"
    print(f"  Endpoint CSV Path:    {data_path}")
    print(f"  Endpoint CSV SHA-256: {sha}")
    assert sha == expected_sha, f"SHA mismatch! Expected: {expected_sha}"
    print("  SHA-256 Checksum: VERIFIED (Exact Match)")
    
    df = pd.read_csv(data_path)
    print(f"  Total row count:     {len(df):,} (Expected: 29,056)")
    assert len(df) == 29056, "Incorrect row count"
    
    n_prob = df['pair_id'].nunique()
    print(f"  Unique problem count:{n_prob} (Expected: 454)")
    assert n_prob == 454, "Incorrect problem count"
    
    null_count = df.isnull().sum().sum()
    print(f"  Missing / NaN cells: {null_count} (Expected: 0)")
    assert null_count == 0, "Found missing values in raw outcomes"
    
    cell_counts = df.groupby(['pair_id', 'state_type', 'checkpoint_t']).size()
    assert (cell_counts == 16).all(), "Imbalanced replications per cell"
    print("  Factorial Cell Balance: Exactly 16 rollouts per problem-condition-checkpoint cell (100% Balanced)")
    
    # Check trajectory file
    traj_path = resolve_path("artifacts/trajectory/nine_checkpoint_trajectory.csv")
    assert os.path.exists(traj_path), f"Missing: {traj_path}"
    df_traj = pd.read_csv(traj_path)
    print(f"  Trajectory Checkpoints: {len(df_traj)} checkpoints loaded successfully (t in {list(df_traj['checkpoint'].values)})")
    
    # Check natural recovery files
    err_path = resolve_path("artifacts/natural_recovery/natural_error_episodes.csv")
    rec_path = resolve_path("artifacts/natural_recovery/natural_recovery_episodes.csv")
    assert os.path.exists(err_path) and os.path.exists(rec_path), "Natural recovery files missing"
    df_err = pd.read_csv(err_path)
    df_rec = pd.read_csv(rec_path)
    print(f"  Study B Episodes: {len(df_err)} natural errors, {len(df_rec)} natural recoveries (Denominator 3,200 rollouts)")
    
    print("Dataset validation: ALL CHECKS PASSED.\n")

if __name__ == '__main__':
    check_data()

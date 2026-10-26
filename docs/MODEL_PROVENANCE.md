# MODEL PROVENANCE & WEIGHT IDENTITY LEDGER

**Project**: StateShift
**Base Pretrained Model ($t=0$)**: `Qwen/Qwen2.5-7B`
**RL Training Model Lineage**: `UWNSL/Qwen2.5-7B-deepscaler_4k_step_X`

---

## 1. Verified Hugging Face Checkpoint Commit SHAs

Every evaluated model checkpoint in the 9-checkpoint empirical trajectory corresponds to an immutable commit on Hugging Face:

| Checkpoint Step ($t$) | Repository ID | Verified Git Commit SHA | Verification Status |
| :---: | :--- | :--- | :---: |
| **$t=0$** | `Qwen/Qwen2.5-7B` | Base Pretrained Model | **`VERIFIED`** |
| **$t=32$** | `UWNSL/Qwen2.5-7B-deepscaler_4k_step_32` | `f46f9eac9908013a502735b7e882821f492ca61e` | **`VERIFIED_LIVE`** |
| **$t=64$** | `UWNSL/Qwen2.5-7B-deepscaler_4k_step_64` | `d57afa929761825af618c6545ab7f7a5b28b3dc1` | **`VERIFIED_LIVE`** |
| **$t=96$** | `UWNSL/Qwen2.5-7B-deepscaler_4k_step_96` | `5164cb6d7dcace900aed6a961cea33de40f2b6dc` | **`VERIFIED_LIVE`** |
| **$t=128$** | `UWNSL/Qwen2.5-7B-deepscaler_4k_step_128` | `27d9d8455a50c0cb0af37e9676bac4e2a1ecddec` | **`VERIFIED_LIVE`** |
| **$t=160$** | `UWNSL/Qwen2.5-7B-deepscaler_4k_step_160` | `d8df8a5d6290bcc7b4b5fa108121cc5b9808bf58` | **`VERIFIED_LIVE`** |
| **$t=192$** | `UWNSL/Qwen2.5-7B-deepscaler_4k_step_192` | `cb3f9bda37c44699246d04b9af21df41879e0ac3` | **`VERIFIED_LIVE`** |
| **$t=224$** | `UWNSL/Qwen2.5-7B-deepscaler_4k_step_224` | `1833fa4e7beea19c2451e1f7a4dfe3068454edaf` | **`VERIFIED_LIVE`** |
| **$t=256$** | `UWNSL/Qwen2.5-7B-deepscaler_4k_step_256` | `7667ad787966f5733fdca3d2b240452d7095ff95` | **`VERIFIED_LIVE`** |

---

## 2. Audit Note on Historical Placeholder Metadata

During initial pilot development, an MD5 string (`50bdcb5a50bdcb5a50bdcb5a50bdcb5a50bdcb5a`) was temporarily logged in early metadata files. This string was flagged during pre-publication auditing as `INVALID_SYNTHETIC_PLACEHOLDER_REVISION`. All analyses strictly utilize the live, cryptographically verified Hugging Face commits listed above.

Weight identity auditing established `SINGLE_CACHED_OBJECT_REFERENCED_BY_BOTH_RUNS`, confirming zero weight divergence between primary and trajectory evaluation runs.

*Signed by Model Provenance Auditor & Reproducibility Engineer*

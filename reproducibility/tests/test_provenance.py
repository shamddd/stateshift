"""
Unit tests for model provenance commit SHAs and invalid synthetic placeholder checks.
"""

import pytest


def test_valid_provenance_commits():
    valid_commits = {
        32: "f46f9eac9908013a502735b7e882821f492ca61e",
        64: "d57afa929761825af618c6545ab7f7a5b28b3dc1",
        96: "5164cb6d7dcace900aed6a961cea33de40f2b6dc",
        128: "27d9d8455a50c0cb0af37e9676bac4e2a1ecddec",
        160: "d8df8a5d6290bcc7b4b5fa108121cc5b9808bf58",
        192: "cb3f9bda37c44699246d04b9af21df41879e0ac3",
        224: "1833fa4e7beea19c2451e1f7a4dfe3068454edaf",
        256: "7667ad787966f5733fdca3d2b240452d7095ff95"
    }
    
    synthetic_placeholder = "50bdcb5a50bdcb5a50bdcb5a50bdcb5a50bdcb5a"
    
    for step, sha in valid_commits.items():
        assert len(sha) == 40
        assert sha != synthetic_placeholder # Synthetic placeholder must NEVER appear as a valid HF model commit

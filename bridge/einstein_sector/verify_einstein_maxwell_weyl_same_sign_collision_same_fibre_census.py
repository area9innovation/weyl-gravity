"""Independent structural verifier for the six-candidate same-fibre census."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_same_fibre_census.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    assert payload["schema_sha256"] == sha(ROOT / payload["schema_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])
    assert [row["candidate_index"] for row in payload["candidate_rows"]] == list(range(16, 22))
    count = 0
    for row in payload["candidate_rows"]:
        assert row["channel_count"] == 18 and row["nonzero_defect_count"] == 144
        for channel in row["channels"]:
            assert len(channel["defects"]) == 8
            for defect in channel["defects"]:
                interval = defect["witness"]
                lower, upper = Fraction(interval["lower"]), Fraction(interval["upper"])
                assert lower <= upper and (lower > 0 or upper < 0) and interval["excludes_zero"]
                count += 1
    assert count == 864
    flags = payload["classification"]
    assert flags["all_108_same_fibre_temporal_channels_off_shell"] and flags["all_864_target_shell_defects_nonzero"]
    assert not flags["cross_fibre_resonance_join_classified"] and not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_SAME_FIBRE_CENSUS verifier: PASS")


if __name__ == "__main__":
    verify()

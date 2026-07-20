"""Independent verifier for the full internal automatic-face normal form."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    Draft202012Validator(json.loads(schema_path.read_text())).validate(payload)
    assert payload["schema_sha256"] == _sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == _sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == _sha(ROOT / item["path"])

    multiplicities = payload["multiplicity_theorem"]
    assert [multiplicities["q_minus_current_eigenlines_per_node"], multiplicities["p_extra_current_eigenlines_per_node"], multiplicities["q_plus_current_eigenlines_per_node"]] == [2, 4, 2]
    assert payload["orthogonal_block_theorem"]["one_current_orthogonal_eigenline_real_inertia"] == [4, 4, 2]
    assert payload["full_internal_formula"]["inertia_positive_negative_null"] == ["4*M-2", "4*M-2", "2*M-2*N+2"]

    expected = {
        17: [(4, 12, [46, 46, 18]), (4, 10, [38, 38, 14]), (5, 14, [54, 54, 20])],
        18: [(4, 10, [38, 38, 14]), (4, 8, [30, 30, 10]), (5, 12, [46, 46, 16])],
        19: [(4, 10, [38, 38, 14]), (4, 8, [30, 30, 10]), (5, 12, [46, 46, 16])],
        20: [(4, 12, [46, 46, 18]), (4, 10, [38, 38, 14]), (5, 14, [54, 54, 20])],
        21: [(4, 12, [46, 46, 18]), (4, 10, [38, 38, 14]), (5, 14, [54, 54, 20])],
    }
    rows = {row["candidate_index"]: row for row in payload["candidate_rows"]}
    assert rows[16]["verdict"] == "NOT_APPLICABLE"
    for index, wanted in expected.items():
        actual = []
        for stratum in rows[index]["support_strata"]:
            n = stratum["occupied_axis_eigenlines_N"]
            m = stratum["total_current_eigenlines_M"]
            inertia = stratum["full_internal_mu_J3_real_inertia"]
            assert inertia == [4 * m - 2, 4 * m - 2, 2 * m - 2 * n + 2]
            assert sum(inertia) == stratum["rotation_kernel_real_dimension"]
            assert stratum["rotation_kernel_real_dimension"] == 10 * m - 2 * n - 2
            actual.append((n, m, inertia))
        assert actual == wanted

    flags = payload["classification"]
    assert flags["all_current_orthogonal_internal_directions_included"]
    assert flags["full_fixed_occupation_rotation_kernel_inertia_complete_on_automatic_faces"]
    assert not flags["occupation_strata_glued"]
    assert not flags["active_resonance_components_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_FULL_INTERNAL_ROTATION_NORMAL_FORM verifier: PASS")


if __name__ == "__main__":
    verify()

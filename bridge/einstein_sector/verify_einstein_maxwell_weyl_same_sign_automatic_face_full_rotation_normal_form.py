"""Independent verifier for the complete automatic-face rotation Hessian."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_full_rotation_normal_form.json"
NODE_DIMENSION = {
    "q_minus_n1": 2,
    "p_extra_n1": 4,
    "q_plus_n1": 2,
    "q_minus_n2": 2,
    "p_extra_n2": 4,
    "q_plus_n2": 2,
}
EXPECTED = {
    17: [("R1_relative_interior", 4, 12), ("R2_relative_interior", 4, 10), ("cone(R1,R2)_relative_interior", 5, 14)],
    18: [("R2_relative_interior", 4, 10), ("R4_relative_interior", 4, 8), ("cone(R2,R4)_relative_interior", 5, 12)],
    19: [("R2_relative_interior", 4, 10), ("R4_relative_interior", 4, 8), ("cone(R2,R4)_relative_interior", 5, 12)],
    20: [("R1_relative_interior", 4, 12), ("R3_relative_interior", 4, 10), ("cone(R1,R3)_relative_interior", 5, 14)],
    21: [("R1_relative_interior", 4, 12), ("R3_relative_interior", 4, 10), ("cone(R1,R3)_relative_interior", 5, 14)],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])
    assert payload["primary_multiplicity_dictionary"]["node_dimensions"] == NODE_DIMENSION

    rows = payload["candidate_rows"]
    assert [row["candidate_index"] for row in rows] == list(range(16, 22))
    assert rows[0]["verdict"] == "NOT_APPLICABLE"
    for row in rows[1:]:
        index = row["candidate_index"]
        observed = []
        for stratum in row["support_strata"]:
            nodes = stratum["occupied_nodes_N"]
            dimension = stratum["total_internal_complex_dimension_D"]
            assert dimension == sum(NODE_DIMENSION[node] for node in stratum["support"])
            positive = 4 * dimension - 2
            negative = positive
            null = 2 * dimension - nodes + 2
            quotient_null = 2 * dimension - 2 * nodes + 2
            assert stratum["unquotiented_real_inertia"] == [positive, negative, null]
            assert stratum["node_phase_quotiented_real_inertia"] == [positive, negative, quotient_null]
            assert sum(stratum["unquotiented_real_inertia"]) == stratum["unquotiented_fixed_norm_kernel_real_dimension"]
            assert sum(stratum["node_phase_quotiented_real_inertia"]) == stratum["node_phase_quotiented_kernel_real_dimension"]
            observed.append((stratum["stratum"], nodes, dimension))
        assert observed == EXPECTED[index]
    flags = payload["classification"]
    assert flags["candidates_17_through_21_complete_fixed_norm_rotation_hessians_classified"]
    assert flags["all_axial_polar_internal_directions_included"]
    assert flags["unquotiented_and_node_phase_quotiented_inertias_certified"]
    assert flags["all_transverse_rotation_hessians_indefinite"]
    assert not flags["rotation_zero_local_semialgebraic_components_classified"]
    assert not flags["active_resonance_components_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_FULL_ROTATION_NORMAL_FORM verifier: PASS")


if __name__ == "__main__":
    verify()

"""Independent verifier for the candidate-17/20 current-radical witness."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive(interval: dict[str, object]) -> bool:
    numerator, denominator = interval["lower"].split("/")
    return Fraction(int(numerator), int(denominator)) > 0 and interval["positive"]


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

    current_audit = payload["parity_current_reduction"]["direct_action_current_shell_audit"]
    assert current_audit["q_minus"]["polar_over_axial_ratio"] == "3"
    assert current_audit["q_plus"]["polar_over_axial_ratio"] == "3"
    assert current_audit["q_minus"]["common_sign"] == "negative"
    assert current_audit["q_plus"]["common_sign"] == "positive"

    radical = payload["universal_smooth_radical"]
    assert radical["jacobian_rank"] == 3
    assert radical["affine_tangent_complex_dimension"] == 7
    assert radical["restricted_tangent_rank"] == 6
    assert radical["restricted_tangent_nullity"] == 1
    assert radical["normalized_positive_to_negative_current_coefficient_ratio"] == "1/16"
    assert radical["absolute_current_occupation_ratio_positive_over_negative"] == "13/192"
    assert radical["fixed_norm_tangency"] == {"f_inner_delta_f": "0", "g_inner_delta_g": "0"}
    assert all(value == "0" for pair in radical["individual_rotation_moments"].values() for value in pair)
    assert radical["ambient_radical_vector_delta_f_delta_g"] == ["0", "1/4", "0", "1/4", "0", "0", "1", "0", "1", "0"]

    rows = payload["scalar_cone_witnesses"]
    assert [row["candidate_index"] for row in rows] == [17, 20]
    assert [row["active_ray"] for row in rows] == ["R3", "R2"]
    assert all(row["automatic_ray"] == "R1" for row in rows)
    assert all(row["resulting_positive_over_negative_ratio"] == "13/192" for row in rows)
    assert all(positive(row["automatic_ray_coefficient_interval"]) for row in rows)
    assert all(positive(row["active_ray_ratio_minus_13_over_192_interval"]) for row in rows)

    flags = payload["classification"]
    assert flags["candidate17_smooth_active_restricted_current_degeneracy"]
    assert flags["candidate20_smooth_active_restricted_current_degeneracy"]
    assert flags["degeneracy_occurs_inside_each_exact_scalar_cone"]
    assert flags["degenerate_points_have_all_five_stabilizer_moment_maps_zero"]
    assert flags["degenerate_points_are_bounded_second_order_tangents"]
    assert not flags["global_active_component_symplectic_orbifold"]
    assert not flags["proper_moment_map_connected_fibre_theorem_applicable_globally"]
    assert not flags["candidate18_active_restricted_current_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_L1_ACTIVE_RESTRICTED_CURRENT_DEGENERACY verifier: PASS")


if __name__ == "__main__":
    verify()

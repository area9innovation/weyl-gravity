"""Independent verifier for the six resonance-face fibre stratifications."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decomposition(record: dict, index: int) -> dict:
    value = record["decompositions"]
    rows = value if isinstance(value, list) else [item for item in value.values() if isinstance(item, dict)]
    return next(row for row in rows if row.get("candidate_index") == index)


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == sha(ROOT / provenance["generator_path"])
    records = {}
    for name, item in provenance["inputs"].items():
        path = ROOT / item["path"]
        assert item["sha256"] == sha(path)
        records[name] = json.loads(path.read_text())

    supports = {row["ray_id"]: set(row["support"]) for row in records["scalar_rays"]["extreme_rays"]}
    expected_faces = {16: [], 17: ["R1", "R2"], 18: ["R2", "R4"], 19: ["R2", "R4"], 20: ["R1", "R3"], 21: ["R1", "R3"]}
    expected_active = {16: (20, 12, 1), 17: (20, 14, 1), 18: (30, 22, 1), 19: (30, 10, 4), 20: (20, 14, 1), 21: (20, 10, 2)}
    isolated = records["isolated"]["candidate_ledger"]["rows"]
    rows = payload["face_rows"]
    assert [row["candidate_index"] for row in rows] == list(range(16, 22))
    for row in rows:
        index = row["candidate_index"]
        collision = isolated[index - 1]
        assert row["collision"]["first_node"] == f"{collision['first_branch']}_n1"
        assert row["collision"]["second_node"] == f"{collision['second_branch']}_n2"
        assert row["collision"]["temporal_channel"] == collision["admissible_temporal_channel"]
        automatic = row["automatic_zero_face"]["ray_generators"]
        assert automatic == expected_faces[index]
        if automatic:
            optional = row["automatic_zero_face"]["condition"].split()[0]
            assert automatic == [ray for ray, support in supports.items() if optional not in support]
        active = row["active_stratum"]
        assert (active["ambient_complex_dimension"], active["resonance_complex_dimension"], active["active_component_count_over_C"]) == expected_active[index]
        assert row["real_nonemptiness"] == "CERTIFIED_BY_THE_AXISYMMETRIC_SCALAR_CONE_SECTION"

    row19 = rows[3]
    source19 = decomposition(records["regular_pencil_L4"], 19)["zero_variety"]
    ids19 = [item["component_id"] for item in source19["irreducible_components_over_C"] if item["component_id"].startswith("mixed_eigenline_")]
    assert [item["component_id"] for item in row19["active_stratum"]["active_components"]] == ids19
    assert source19["all_mixed_components_real_supported"]
    row21 = rows[5]
    source21 = decomposition(records["scalar_L4"], 21)
    ids21 = [item["component_id"] for item in source21["irreducible_components_over_C"] if item["component_id"].startswith("mixed_")]
    assert [item["component_id"] for item in row21["active_stratum"]["active_components"]] == ids21
    assert source21["r_squared_interval"]["positive"]
    assert [row["collision"]["temporal_channel"] for row in rows] == ["SUM", "DIFFERENCE", "SUM", "SUM", "DIFFERENCE", "SUM"]

    flags = payload["classification"]
    assert flags["all_six_resonance_fibres_stratified_over_complete_scalar_cones"]
    assert flags["all_active_complex_component_ledgers_complete"]
    assert flags["real_nonempty_section_on_every_scalar_cone_point"]
    assert flags["bounded_fibre_product_formula_imported"]
    assert not flags["full_real_connected_component_decomposition"]
    assert not flags["rotation_moment_map_reduction_completed"]
    assert not flags["complete_real_bounded_component_decomposition"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_RESONANCE_FACE_FIBRES verifier: PASS")


if __name__ == "__main__":
    verify()

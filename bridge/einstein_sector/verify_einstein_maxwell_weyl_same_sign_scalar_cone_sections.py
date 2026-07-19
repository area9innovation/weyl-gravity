"""Independent verifier for the six complete scalar-cone amplitude sections."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json"


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
    generator = payload["provenance"]["generator_path"]
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / generator)
    inputs = payload["provenance"]["inputs"]
    records = {}
    for name, item in inputs.items():
        assert item["sha256"] == sha(ROOT / item["path"])
        records[name] = json.loads((ROOT / item["path"]).read_text())

    scalar_rows = records["scalar_rays"]["candidate_rows"]
    isolated_rows = records["isolated"]["candidate_ledger"]["rows"]
    candidate19 = decomposition(records["candidate19"], 19)
    candidate21 = decomposition(records["candidate21"], 21)
    mixed19 = next(
        item
        for item in candidate19["zero_variety"]["irreducible_components_over_C"]
        if item["component_id"] == "mixed_eigenline_1"
    )
    mixed21 = next(
        item
        for item in candidate21["irreducible_components_over_C"]
        if item["component_id"] == "mixed_plus"
    )
    assert candidate19["zero_variety"]["all_mixed_components_real_supported"]
    assert candidate21["r_squared_interval"]["positive"]
    assert records["same_fibre"]["classification"]["all_864_target_shell_defects_nonzero"]
    assert records["finite_cone"]["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"]

    rows = payload["section_rows"]
    assert [row["candidate_index"] for row in rows] == list(range(16, 22))
    methods = Counter(row["section"]["method"] for row in rows)
    assert methods == Counter({"ALL_AXIAL_AXISYMMETRIC_ODD_L_SECTION": 4, "REAL_REGULAR_PENCIL_L4_SECTION": 1, "REAL_SCALAR_MIXED_PARITY_L4_SECTION": 1})
    for row in rows:
        index = row["candidate_index"]
        assert row["rho"] == scalar_rows[index - 16]["rho"]
        output_ell = isolated_rows[index - 1]["output_ell"]
        method = row["section"]["method"]
        if method == "ALL_AXIAL_AXISYMMETRIC_ODD_L_SECTION":
            assert output_ell in (1, 3)
            assert clebsch_gordan(2, 2, output_ell, 0, 0, 0) == 0
            assert f"|{output_ell},0>" in row["section"]["resonance_zero"]
        elif method == "REAL_REGULAR_PENCIL_L4_SECTION":
            assert index == 19 and output_ell == 4
            assert row["section"]["component_id"] == mixed19["component_id"]
            assert mixed19["dimension_over_C"] == 10
            assert "independent nonnegative fibre scaling" in row["section"]["resonance_zero"]
        elif method == "REAL_SCALAR_MIXED_PARITY_L4_SECTION":
            assert index == 21 and output_ell == 4
            assert row["section"]["component_id"] == mixed21["component_id"]
            assert row["section"]["r"] == mixed21["r"]
            assert row["section"]["s"] == mixed21["s"]
            assert "independent fibre scaling" in row["section"]["resonance_zero"]
        else:
            raise AssertionError(f"unknown section method: {method}")
        assert row["rotation_zero"].startswith("all amplitudes have m=0")
        assert row["same_fibre"].endswith("off shell")
        assert row["bounded_verdict"] == "EVERY_SCALAR_NULL_OCCUPATION_HAS_A_BOUNDED_AMPLITUDE_LIFT"
    flags = payload["classification"]
    assert flags["all_six_complete_scalar_cones_have_bounded_amplitude_sections"]
    assert flags["bounded_to_scalar_occupation_projection_surjective"]
    assert flags["all_scalar_cone_faces_and_pairwise_ray_sums_covered"]
    assert not flags["every_amplitude_over_each_scalar_occupation_bounded"]
    assert not flags["six_full_phase_parity_fibres_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_SCALAR_CONE_SECTIONS verifier: PASS")


if __name__ == "__main__":
    verify()

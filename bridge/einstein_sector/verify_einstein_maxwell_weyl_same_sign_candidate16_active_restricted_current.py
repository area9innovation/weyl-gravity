"""Independent verifier for candidate 16's active restricted current."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current.json"


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

    component = payload["component"]
    assert component["affine_ambient_complex_dimension"] == 20
    assert component["affine_resonance_complex_dimension"] == 12
    assert component["projective_resonance_complex_dimension"] == 10
    assert component["irreducible_components_over_C"] == 1

    theorem = payload["restricted_current_theorem"]
    assert theorem["node_current_signs"] == {"q_minus_n1": -1, "q_minus_n2": -1}
    assert theorem["node_internal_complex_dimensions"] == {"q_minus_n1": 10, "q_minus_n2": 10}
    assert theorem["smooth_locus_generic_real_symplectic_rank"] == 20
    assert theorem["every_complex_smooth_stratum_restricted_current_nondegenerate"]
    assert not theorem["singular_points_treated_as_smooth_manifold_points"]

    flags = payload["classification"]
    assert flags["candidate16_active_restricted_current_gate_closed"]
    assert flags["same_sign_definite_restriction_proof"]
    assert flags["complete_axial_polar_internal_spaces_included"]
    assert flags["every_complex_smooth_stratum_symplectic"]
    assert not flags["rotation_zero_fibre_connected"]
    assert not flags["singular_stratum_moment_map_topology_classified"]
    assert not flags["candidates17_through21_restricted_currents_classified"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_ACTIVE_RESTRICTED_CURRENT verifier: PASS")


if __name__ == "__main__":
    verify()

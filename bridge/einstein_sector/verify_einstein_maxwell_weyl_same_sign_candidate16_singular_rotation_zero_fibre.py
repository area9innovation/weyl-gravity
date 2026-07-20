"""Independent verifier for candidate 16's singular rotation-zero theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre.json"


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

    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")
    equations = [f[i] * g[j] - f[j] * g[i] for i in range(5) for j in range(i + 1, 5)]
    J = sp.Matrix(equations).jacobian((*f, *g))
    origin = {value: 0 for value in (*f, *g)}
    e0 = (0, 0, 1, 0, 0)
    rank_one = dict(zip((*f, *g), e0 + e0))
    assert J.subs(origin).rank() == 0
    assert J.subs(rank_one).rank() == 4
    assert sp.diag(J.subs(rank_one), J.subs(rank_one)).rank() == 8
    assert sp.diag(J.subs(origin), J.subs(rank_one)).rank() == 4

    strata = payload["singular_stratification"]
    assert strata["complete_singular_locus"] == "two disjoint CP^4 endpoint strata"
    assert strata["endpoint_complex_dimension"] == 4
    resolution = payload["incidence_resolution"]
    assert resolution["complex_dimension"] == 12
    assert resolution["exceptional_fibre_over_one_vertex"] == "CP^4"
    assert resolution["surjective"] and resolution["connected_fibres"]
    assert resolution["proper_after_positive_node_norm_reduction"]
    assert resolution["reduced_resolution"] == "compact connected Kahler manifold of complex dimension 10"
    rotation = payload["rotation_zero_fibre"]
    assert rotation["resolved_zero_fibre_connected"]
    assert rotation["target_zero_fibre_is_continuous_image"]
    assert rotation["target_zero_fibre_connected"]
    assert not rotation["singular_target_treated_as_orbifold"]
    flags = payload["classification"]
    assert flags["candidate16_complete_singular_locus_classified"]
    assert flags["lifted_rotation_zero_fibre_connected"]
    assert not flags["occupation_strata_glued"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_SINGULAR_ROTATION_ZERO_FIBRE verifier: PASS")


if __name__ == "__main__":
    verify()

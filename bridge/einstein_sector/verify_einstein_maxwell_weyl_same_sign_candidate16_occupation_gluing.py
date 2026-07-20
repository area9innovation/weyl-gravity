"""Independent verifier for candidate 16 occupation gluing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing.json"


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

    inputs = payload["provenance"]["inputs"]
    scalar_payload = json.loads((ROOT / inputs["scalar_cone"]["path"]).read_text())
    scalar = next(row for row in scalar_payload["candidate_rows"] if row["candidate_index"] == 16)
    assert scalar["cone_dimension"] == 3
    assert scalar["counts"]["positive_extreme_rays"] == 4
    assert len(scalar["positive_extreme_rays"]) == 4
    assert all(row["all_weights_positive_exact"] for row in scalar["positive_extreme_rays"])

    base = payload["normalized_scalar_base"]
    assert base["affine_cone_dimension"] == scalar["cone_dimension"] == 3
    assert base["positive_extreme_rays"] == scalar["counts"]["positive_extreme_rays"] == 4
    assert base["compact"] and base["connected"]
    assert base["isomorphism_type"] == "a compact convex two-dimensional polytope with four certified vertices"
    total = payload["total_zero_link"]
    assert total["projection_proper"] and total["projection_surjective"]
    assert total["every_fibre_connected"]
    assert total["complete_normalized_zero_link_connected"]
    flags = payload["classification"]
    assert flags["candidate16_active_occupation_gluing_closed"]
    assert not flags["origin_adjoined"]
    assert not flags["cross_candidate_gluing"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_OCCUPATION_GLUING verifier: PASS")


if __name__ == "__main__":
    verify()

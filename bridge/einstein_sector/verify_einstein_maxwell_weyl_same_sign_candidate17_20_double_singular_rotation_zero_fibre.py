"""Independent verifier for the candidate-17/20 connected singular hub."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    Draft202012Validator(json.loads(schema_path.read_text())).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    singular_item = payload["provenance"]["inputs"]["singular_locus"]
    product = json.loads((ROOT / singular_item["path"]).read_text())["two_parity_product"]
    assert product["intersection"] == "S_plus x S_minus"
    assert product["intersection_complex_dimension"] == 8

    resolution = payload["incidence_resolution"]
    base_dimension = 2 + 2
    reduced_dimension = base_dimension + (2 - 1) + (2 - 1)
    assert base_dimension == resolution["base_complex_dimension"] == 4
    assert reduced_dimension == resolution["reduced_complex_dimension"] == 6
    assert resolution["compact"] and resolution["connected"] and resolution["kahler"]
    assert resolution["surjective_to_target_hub"] and resolution["connected_resolution_fibres"]
    assert resolution["equivariant_for_lifted_SO3"]

    rotation = payload["rotation_zero_fibre"]
    assert rotation["resolved_zero_fibre_connected"]
    assert rotation["target_hub_zero_fibre_is_continuous_image"]
    assert rotation["target_hub_zero_fibre_connected"]
    flags = payload["classification"]
    assert flags["candidate17_double_singular_rotation_zero_hub_connected"]
    assert flags["candidate20_double_singular_rotation_zero_hub_connected"]
    assert not flags["complete_singular_components_connected"]
    assert not flags["complete_singular_rotation_zero_quotient_connected"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DOUBLE_SINGULAR_ROTATION_ZERO_FIBRE verifier: PASS")


if __name__ == "__main__":
    verify()

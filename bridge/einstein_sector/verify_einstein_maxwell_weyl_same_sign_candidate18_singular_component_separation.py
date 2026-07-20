"""Independent verifier for candidate 18 singular-component separation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation.json"


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
    source_item = payload["provenance"]["inputs"]["singular_resolution"]
    source = json.loads((ROOT / source_item["path"]).read_text())["complete_carrier"]
    assert source["intersection"] == "C^10 x {0} x {0}"
    assert source["irreducible_singular_components"] == 2
    descent = payload["group_descent"]
    assert descent["rotation_zero_nonempty_in_each_component"]
    assert descent["singular_rotation_zero_quotient_component_lower_bound"] == 2
    flags = payload["classification"]
    assert flags["candidate18_positive_occupation_singular_components_separated"]
    assert flags["candidate18_singular_rotation_zero_quotient_at_least_two_components"]
    assert not flags["candidate18_each_component_connected"]
    assert not flags["candidate18_full_rotation_zero_fibre_disconnected"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_SINGULAR_COMPONENT_SEPARATION verifier: PASS")


if __name__ == "__main__":
    verify()

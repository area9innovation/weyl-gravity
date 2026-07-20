"""Independent verifier for candidate-17/20 singular-component incidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence.json"


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
    assert product["singular_locus"] == "(S_plus x K_minus) union (K_plus x S_minus)"
    assert product["intersection"] == "S_plus x S_minus"
    assert product["intersection_complex_dimension"] == 8

    section_item = payload["provenance"]["inputs"]["sections"]
    sections = json.loads((ROOT / section_item["path"]).read_text())
    witness = sections["candidate17_20_section"]
    assert "S_plus x S_minus" in witness["singularity_witness"]
    assert witness["occupation_check"] == [
        "(1/6)*(6*N_minus)=N_minus",
        "(1/16)*(1/6)*(96*N_plus)=N_plus",
    ]
    assert sections["universal_section"]["node_phase_actions_free"]

    descent = payload["group_descent"]
    assert descent["component_label_separation_lower_bound"] == 1
    assert "images" in descent["quotient_images_intersect"]
    flags = payload["classification"]
    assert flags["candidate17_positive_occupation_singular_component_images_intersect"]
    assert flags["candidate20_positive_occupation_singular_component_images_intersect"]
    assert not flags["candidate17_20_component_labels_prove_quotient_separation"]
    assert not flags["candidate17_20_complete_singular_rotation_zero_quotient_connected"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_SINGULAR_COMPONENT_INCIDENCE verifier: PASS")


if __name__ == "__main__":
    verify()

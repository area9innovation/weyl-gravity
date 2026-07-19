#!/usr/bin/env python3
"""Fast verifier for the direct exceptional axial zero-source fixture."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axial_ell1_zero_source_fixture.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_axial_ell1_zero_source_fixture.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["schema_sha256"] != hashlib.sha256(SCHEMA.read_bytes()).hexdigest():
        raise AssertionError("schema hash changed")
    helper = ROOT / value["provenance"]["tensor_helper_path"]
    if hashlib.sha256(helper.read_bytes()).hexdigest() != value["provenance"]["tensor_helper_sha256"]:
        raise AssertionError("tensor helper changed")
    if value["axisymmetric_harmonic"] != "P_1(cos(theta)); averaged norm 1/3":
        raise AssertionError("P1 normalization was hidden")
    flags = value["classification"]
    if not flags["direct_four_dimensional_source_computed"] or flags["combined_balanced_source_solved"]:
        raise AssertionError("fixture lifecycle changed")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_AXIAL_ELL1_ZERO_SOURCE_FIXTURE fast verification: PASS")

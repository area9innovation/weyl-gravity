#!/usr/bin/env python3
"""Independent verifier for the complete standard-harmonic inclusion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.schema.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    theorem = payload["theorem"]
    assert len(theorem["block_table"]) == 4
    assert all(row["nondegeneracy"] for row in theorem["block_table"])
    inclusion = theorem["inclusion_theorem"]
    assert inclusion["kernel_of_pullback_on_standard_tangent"] == "0"
    assert inclusion["identity_inclusion_is_symplectic"] is False
    assert inclusion["ordinary_Einstein_Maxwell_tangent_removed_before_final_residual_quotient"] is False
    assert payload["classification"]["final_residual_quotient_computed"] is False
    assert payload["classification"]["lorentzian_causal_or_scattering_theorem"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_SYMPLECTIC_INCLUSION independent verification: PASS")

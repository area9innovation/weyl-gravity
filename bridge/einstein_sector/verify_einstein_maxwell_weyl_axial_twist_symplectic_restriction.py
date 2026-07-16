#!/usr/bin/env python3
"""Independent verifier for the axial twist restriction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_twist_symplectic_restriction.schema.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    for record in payload["provenance"]["direct_implementation"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    forms = payload["theorem"]["cauchy_forms_after_common_factor_L_N_1m"]
    source = sp.Matrix(forms["einstein_maxwell"])
    target = sp.Matrix(forms["weyl_maxwell"])
    assert target == -2 * source
    assert source.rank() == target.rank() == 2
    assert payload["classification"]["radiative_mu_zero_continuation_used"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_AXIAL_TWIST_SYMPLECTIC_RESTRICTION independent verification: PASS")

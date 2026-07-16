#!/usr/bin/env python3
"""Independent verifier for the homogeneous global restriction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.schema.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    for record in payload["provenance"]["direct_implementation"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    theorem = payload["theorem"]
    source = sp.Matrix(theorem["cauchy_forms_after_common_factor_2piL"]["einstein_maxwell"])
    target = sp.Matrix(theorem["cauchy_forms_after_common_factor_2piL"]["weyl_maxwell"])
    relative = sp.Matrix(theorem["relative_endomorphism"]["matrix"])
    shear = sp.Matrix([[sp.Rational(value) for value in row] for row in theorem["explicit_linear_symplectomorphism"]["S_equals_I_plus_N_over_2"]])
    assert source.inv() * target == relative
    assert (relative - sp.eye(6)) ** 2 == sp.zeros(6)
    assert (relative - sp.eye(6)).rank() == 2
    assert shear.T * source * shear == target
    assert source.rank() == target.rank() == 6
    assert payload["classification"]["identity_inclusion_symplectic"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_GLOBAL_SYMPLECTIC_RESTRICTION independent verification: PASS")

#!/usr/bin/env python3
"""Independent consumer for the Berger generator conjugation audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-generator-conjugation-audit-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    for item in certificate["source_manifest"].values():
        path = ROOT / item["path"]
        if _sha256(path) != item["sha256"]:
            raise AssertionError(f"source hash mismatch: {path}")

    t = sp.symbols("t", real=True)
    omega, rho = sp.symbols("omega rho", nonzero=True, real=True)
    R = sp.Matrix([[0, -1], [1, 0]])
    U = sp.Matrix(
        [[sp.cos(omega * t), -sp.sin(omega * t)], [sp.sin(omega * t), sp.cos(omega * t)]]
    )
    background = U * sp.Matrix([rho, 0])
    if sp.simplify(sp.diff(background, t) - omega * R * background) != sp.zeros(2, 1):
        raise AssertionError("independent K-background check failed")
    if sp.diff(background, t) == sp.zeros(2, 1):
        raise AssertionError("independent D-background check failed")

    flags = certificate["flags"]
    if flags != {
        "AFFINE_D_CARTAN_CONSTRUCTED": False,
        "AFFINE_D_ZERO_ARITY_NONZERO": True,
        "EXPORTED_UNARY_GENERATOR_IS_K": True,
        "EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D": False,
        "PAPER09_D_CARTAN_AS_PREVIOUSLY_WRITTEN": False,
        "PAPER09_K_CARTAN_INTERPRETATION": True,
        "THEOREM_FROZEN": False,
    }:
        raise AssertionError("generator flag boundary drifted")
    print("BERGER_GENERATOR_CONJUGATION_AUDIT independent audit: PASS")
    print("e0=K; D has affine zero-arity omega R(rho,0); affine D-Cartan open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

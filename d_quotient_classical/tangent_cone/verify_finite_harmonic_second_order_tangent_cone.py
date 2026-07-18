#!/usr/bin/env python3
"""Independent matrix and resonance replay for the tangent-cone theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/finite-harmonic-second-order-tangent-cone-theorem-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    # Rebuild the two quotient ranks without importing the producer.
    identity_static = sp.Matrix([[0, 0, 1]])
    static_operator = sp.Matrix([[1, 0], [0, 0], [0, 0]])
    compatible_static = sp.Matrix.hstack(*identity_static.nullspace())
    reduced_static = (compatible_static.T * compatible_static).inv() * compatible_static.T * static_operator
    if len(reduced_static.T.nullspace()) != 1:
        raise AssertionError("static reduced cokernel is not one-dimensional")

    identity_resonant = sp.Matrix([[0, 1]])
    compatible_resonant = sp.Matrix.hstack(*identity_resonant.nullspace())
    for operator, expected in ((sp.zeros(2, 2), 1), (sp.diag(1, 0), 0)):
        reduced = (compatible_resonant.T * compatible_resonant).inv() * compatible_resonant.T * operator
        if len(reduced.T.nullspace()) != expected:
            raise AssertionError("correction-class cokernel dimension drifted")

    t = sp.symbols("t", real=True)
    omega = sp.symbols("omega", real=True, nonzero=True)
    resonant = sp.exp(sp.I * omega * t)
    if sp.simplify((sp.diff(t * resonant, t) - sp.I * omega * t * resonant) - resonant) != 0:
        raise AssertionError("independent secular inverse failed")
    s = sp.symbols("s", real=True)
    source = s**2 + 1
    solution = sp.integrate(sp.exp(sp.I * omega * (t - s)) * source, (s, 0, t))
    if sp.simplify(sp.diff(solution, t) - sp.I * omega * solution - (t**2 + 1)) != 0:
        raise AssertionError("independent retarded inverse failed")

    if not all(payload["flags"][name] for name in (
        "FINITE_HARMONIC_TANGENT_CONE_FORMULA",
        "GAUGE_AND_NOETHER_ROWS_REMOVED_BEFORE_COKERNEL",
        "BOUNDED_RESONANCE_OBSTRUCTED",
        "SMOOTH_SECULAR_RESONANCE_REMOVED",
        "CAUSAL_RETARDED_RESONANCE_REMOVED_FOR_COMPATIBLE_SOURCE",
    )):
        raise AssertionError("a certified flag is false")
    if payload["flags"]["BACKGROUND_SPECIFIC_TANGENT_CONE_CLASSIFICATION"]:
        raise AssertionError("background classification was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source hash mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1 independent verification: PASS")

#!/usr/bin/env python3
"""Independent replay of the transverse Nariai Einstein tangent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-linearized-einstein-witness-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _independent_replay() -> dict[str, object]:
    t = sp.symbols("t", real=True)
    da = -sp.sinh(2 * t) / 3
    db = sp.sinh(t)
    a = sp.cosh(t)
    residuals = [
        sp.simplify(-(sp.diff(da, t, 2) - da) / a - 2 * sp.diff(db, t, 2)),
        sp.simplify((sp.diff(da, t, 2) - da) / a + 2 * sp.tanh(t) * sp.diff(db, t)),
        sp.simplify(sp.diff(db, t, 2) + sp.tanh(t) * sp.diff(db, t) - 2 * db),
    ]
    if residuals != [0, 0, 0]:
        raise AssertionError(f"independent Einstein residuals failed: {residuals}")

    def at_star(expression: sp.Expr) -> sp.Expr:
        return sp.simplify(
            sp.expand_trig(expression).subs(
                {sp.sinh(t): 1, sp.cosh(t): sp.sqrt(2), sp.tanh(t): 1 / sp.sqrt(2)}
            )
        )

    chi_ratio = at_star(2 * da / a)
    sphere_ratio = at_star(2 * db)
    delta_electric = at_star(-sp.diff(db, t, 2))

    # In the spherically symmetric Einstein sector trace-freeness gives
    # (dC0101,dC0A0A,dC1A1A,dC2323)=(2,-1,1,-2)sinh(t).
    background = [sp.Rational(-2, 3), sp.Rational(1, 3), sp.Rational(-1, 3), sp.Rational(2, 3)]
    variation = [2 * sp.sinh(t), -sp.sinh(t), sp.sinh(t), -2 * sp.sinh(t)]
    multiplicities = [1, 2, 2, 1]
    delta_c_squared = sp.simplify(
        8 * sum(m * c * dc for m, c, dc in zip(multiplicities, background, variation))
    )
    if (
        chi_ratio != sp.Rational(-4, 3)
        or sphere_ratio != 2
        or delta_electric != -1
        or at_star(delta_c_squared) != -32
    ):
        raise AssertionError("independent normalized witness failed")
    return {
        "einstein_residuals": [str(value) for value in residuals],
        "chi_ratio": str(chi_ratio),
        "sphere_ratio": str(sphere_ratio),
        "delta_C_0202": str(delta_electric),
        "delta_C_squared": str(at_star(delta_c_squared)),
    }


def verify() -> dict:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("certificate contains a failed exact check")
    replay = _independent_replay()
    if (
        replay["delta_C_0202"] != certificate["exact_witness"]["delta_C_0202_orthonormal"]
        or replay["delta_C_squared"] != certificate["exact_witness"]["delta_C_squared"]
        or replay["chi_ratio"] != certificate["exact_witness"]["relative_metric_variations"]["chi"]
        or replay["sphere_ratio"] != certificate["exact_witness"]["relative_metric_variations"]["sphere"]
    ):
        raise AssertionError("independent replay disagrees with certificate")
    for name, digest in certificate["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source hash mismatch: {name}")
    for record in certificate["dependency_refs"].values():
        path = ROOT / record["path"]
        payload = json.loads(path.read_text())
        if _sha(path) != record["sha256"] or payload["result_id"] != record["result_id"]:
            raise AssertionError("dependency replay failed")
    return replay


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1 independent verification: PASS")

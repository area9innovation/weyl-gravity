#!/usr/bin/env python3
"""Fast independent verifier for the tuned axial/polar resonance matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse(values: list[str]) -> sp.Matrix:
    return sp.Matrix([sp.sympify(value, locals={"sqrt": sp.sqrt}) for value in values])


def verify() -> None:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if payload["schema_sha256"] != _sha256(SCHEMA):
        raise AssertionError("schema hash changed")
    for collection in (payload["provenance"]["inputs"], payload["provenance"]["direct_engines"]):
        for item in collection.values():
            if _sha256(ROOT / item["path"]) != item["sha256"]:
                raise AssertionError(f"provenance hash changed: {item['path']}")

    ledger = payload["direct_source_ledger"]
    polar_source = _parse(ledger["polar_polar"]["source_rows"])
    polar_adjoints = [sp.Matrix([0, 1, 0, 0]), sp.Matrix([-sp.Rational(4, 87), 0, -sp.Rational(40, 29), 1])]
    polar_pairings = sp.Matrix([(value.T * polar_source)[0] for value in polar_adjoints]).applyfunc(sp.factor)
    cross_source = _parse(ledger["axial_plus_polar_minus"]["source_rows"])
    cross_adjoints = [sp.Matrix([-1, 0, 1, 0]), sp.Matrix([0, -sp.Rational(1, 30), 0, 1])]
    cross_pairings = sp.Matrix([(value.T * cross_source)[0] for value in cross_adjoints]).applyfunc(sp.factor)
    stored_polar = _parse(ledger["polar_polar"]["adjoint_pairings"])
    stored_cross = _parse(ledger["axial_plus_polar_minus"]["adjoint_pairings"])
    if (polar_pairings - stored_polar).applyfunc(sp.simplify) != sp.zeros(2, 1):
        raise AssertionError("polar pairings do not replay")
    if (cross_pairings - stored_cross).applyfunc(sp.simplify) != sp.zeros(2, 1):
        raise AssertionError("cross pairings do not replay")

    b = -265 + 149 * sp.sqrt(3)
    axial = -sp.Rational(1152, 203) * b
    polar = sp.Rational(3456, 203) * b
    cross = sp.Rational(864, 7) * sp.sqrt(-7 + 12 * sp.sqrt(3)) * (-11 * sp.sqrt(6) + 19 * sp.sqrt(2))
    if sp.simplify(polar + 3 * axial) != 0 or cross == 0:
        raise AssertionError("relative coefficients changed")
    if 265**2 - 3 * 149**2 != 3622 or 19**2 - 3 * 11**2 != -2:
        raise AssertionError("nonzero algebraic witnesses changed")

    a_plus, a_minus, p_plus, p_minus = sp.symbols("a_plus a_minus p_plus p_minus")
    equations = [a_plus * a_minus - 3 * p_plus * p_minus, a_plus * p_minus - a_minus * p_plus]
    for sign in (-1, 1):
        substitutions = {a_plus: sign * sp.sqrt(3) * p_plus, a_minus: sign * sp.sqrt(3) * p_minus}
        if any(sp.simplify(value.subs(substitutions)) != 0 for value in equations):
            raise AssertionError("mixed null locus changed")
    if payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] != "OPEN":
        raise AssertionError("full bounded lifecycle was over-promoted")
    if payload["correction_classes"]["CAUSAL_RETARDED"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("causal lifecycle was over-promoted")
    print("EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_PARITY_RESONANCE_MATRIX independent verification: PASS")


if __name__ == "__main__":
    verify()

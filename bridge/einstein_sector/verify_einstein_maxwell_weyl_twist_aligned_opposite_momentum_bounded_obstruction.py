#!/usr/bin/env python3
"""Fast independent verifier for the twist-aligned bounded obstruction fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_vector(values: list[str]) -> sp.Matrix:
    return sp.Matrix([sp.sympify(value, locals={"sqrt": sp.sqrt}) for value in values])


def _polar_action_at_fixture() -> sp.Matrix:
    lam = sp.Integer(20)
    k = sp.Integer(0)
    omega = sp.sqrt(sp.Rational(58, 3))
    at, mixed, ct, maxwell = sp.symbols("A_t B C_t U")
    row_00 = -sp.Rational(1, 2) * (
        at * (k**4 + 2 * lam * k**2 + lam * (2 * lam - 3) / 2)
        + mixed * (2 * k**3 * omega + 2 * lam * k * omega)
        + ct * (k**2 * omega**2 + lam * k**2 / 2 - lam * omega**2 / 2 + lam * (lam + 1) / 2)
        + 2 * lam * maxwell
    )
    row_01 = sp.Rational(1, 2) * (
        at * (k**3 * omega + lam * k * omega)
        + mixed * (2 * k**2 * omega**2 - 3 * lam * k**2 / 2 + 3 * lam * omega**2 / 2 - lam * (3 * lam - 2) / 2)
        + ct * (k * omega**3 - lam * k * omega)
    )
    row_11 = -sp.Rational(1, 2) * (
        at * (k**2 * omega**2 + lam * k**2 / 2 - lam * omega**2 / 2 + lam * (lam + 1) / 2)
        + mixed * (2 * k * omega**3 - 2 * lam * k * omega)
        + ct * (omega**4 - 2 * lam * omega**2 + lam * (2 * lam - 3) / 2)
        - 2 * lam * maxwell
    )
    row_maxwell = at / 2 - ct / 2 + maxwell * (omega**2 - k**2 - lam)
    tensor_rows = sp.Matrix([row_00, row_01, row_11, row_maxwell])
    coefficients = (at, mixed, ct, maxwell)
    tensor = tensor_rows.jacobian(coefficients)
    return (sp.diag(-1, 2, -1, 2 * lam) * tensor).applyfunc(sp.factor)


def verify() -> None:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if payload["schema_sha256"] != _sha256(SCHEMA):
        raise AssertionError("schema hash changed")
    for item in payload["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        if _sha256(path) != item["sha256"]:
            raise AssertionError(f"input hash changed: {path}")
    helper = ROOT / payload["provenance"]["tensor_helper_path"]
    if _sha256(helper) != payload["provenance"]["tensor_helper_sha256"]:
        raise AssertionError("tensor-helper hash changed")

    expected_source = sp.Matrix(
        [
            -sp.Rational(64, 7) * (163 + 261 * sp.sqrt(3)),
            0,
            sp.Rational(32, 105) * (-21293 + 9450 * sp.sqrt(3)),
            sp.Rational(384, 7) * (-137 + 55 * sp.sqrt(3)),
        ]
    )
    source = _parse_vector(payload["direct_four_dimensional_source"]["source_rows"])
    if source != expected_source:
        raise AssertionError("stored direct source changed")

    block = _polar_action_at_fixture()
    if block != block.T or block.rank() != 2:
        raise AssertionError("polar p-shell block changed")
    adjoints = block.T.nullspace()
    expected_adjoints = [
        sp.Matrix([0, 1, 0, 0]),
        sp.Matrix([-sp.Rational(4, 87), 0, -sp.Rational(40, 29), 1]),
    ]
    if adjoints != expected_adjoints:
        raise AssertionError(f"polar adjoints changed: {adjoints}")
    pairings = sp.Matrix([sp.factor((adjoint.T * source)[0]) for adjoint in adjoints])
    expected_nonzero = -sp.Rational(1152, 203) * (-265 + 149 * sp.sqrt(3))
    if (pairings - sp.Matrix([0, expected_nonzero])).applyfunc(sp.simplify) != sp.zeros(2, 1):
        raise AssertionError(f"adjoint pairings changed: {pairings}")
    if 265**2 - 3 * 149**2 != 3622 or expected_nonzero == 0:
        raise AssertionError("nonzero algebraic witness failed")

    omega_minus_squared = sp.Rational(29, 6)
    omega_plus_squared = sp.Rational(29, 6) + 4 * sp.sqrt(3)
    if sp.factor(omega_plus_squared - 9 * omega_minus_squared) == 0:
        raise AssertionError("cross-branch three-to-one collision appeared")
    if payload["collision_audit"]["only_q_minus_pair_reaches_2omega_minus"] is not True:
        raise AssertionError("collision isolation was weakened")
    correction = payload["correction_classes"]
    if correction["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] != "OBSTRUCTED":
        raise AssertionError("bounded fixture was not obstructed")
    if correction["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"] != "CERTIFIED":
        raise AssertionError("smooth secular lifecycle changed")
    if correction["CAUSAL_RETARDED"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("causal lifecycle was over-promoted")
    if payload["classification"]["general_bounded_zero_locus_classified"] is not False:
        raise AssertionError("scoped fixture was over-promoted")
    print("EINSTEIN_MAXWELL_WEYL_TWIST_ALIGNED_OPPOSITE_MOMENTUM_BOUNDED_OBSTRUCTION fast verification: PASS")


if __name__ == "__main__":
    verify()

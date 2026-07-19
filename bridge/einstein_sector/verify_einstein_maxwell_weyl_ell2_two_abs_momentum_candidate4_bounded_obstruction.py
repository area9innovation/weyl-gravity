#!/usr/bin/env python3
"""Independent algebraic verifier for the candidate-4 obstruction."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator,
)


CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.schema.json"
CANDIDATES = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json"


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def independently_verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    candidate = json.loads(CANDIDATES.read_text())["candidate_ledger"]["rows"][3]
    assert canonical(parse(candidate["rho"]) - parse(value["candidate"]["rho"])) == 0
    assert candidate["canonical_signed_momenta"] == [1, -2]
    assert candidate["first_branch"] == candidate["second_branch"] == "q_minus"
    assert candidate["target_branch"] == "p_extra"
    assert candidate["output_ell"] == 4

    rho = parse(value["candidate"]["rho"])
    k_1, k_2 = sp.sqrt(rho), -2 * sp.sqrt(rho)
    offset = 6 - 2 * sp.sqrt(3)
    omega_1 = sp.sqrt(rho + offset)
    omega_2 = sp.sqrt(4 * rho + offset)
    momentum = k_1 + k_2
    frequency = omega_1 + omega_2
    assert canonical(frequency**2 - momentum**2 - sp.Rational(58, 3)) == 0

    source = sp.Matrix([parse(item) for item in value["quadratic_source"]["source_action_rows"]])
    encoded_adjoints = value["polar_p_cokernel"]["adjoint_columns"]
    adjoints = sp.Matrix([[parse(item) for item in row] for row in encoded_adjoints])
    expected_adjoints = sp.Matrix.hstack(
        sp.Matrix([
            1,
            -(3 * momentum**2 + 29) / (3 * momentum * frequency),
            1,
            0,
        ]),
        sp.Matrix([
            sp.Rational(4, 3),
            -2 * (momentum**2 + 20) / (3 * momentum * frequency),
            0,
            1,
        ]),
    )
    assert (adjoints - expected_adjoints).applyfunc(canonical) == sp.zeros(4, 2)

    action, (eigenvalue, target_momentum, target_frequency) = _action_operator()
    block = action.subs({
        eigenvalue: 20,
        target_momentum: momentum,
        target_frequency: frequency,
    })
    assert (block.T * adjoints).applyfunc(canonical) == sp.zeros(4, 2)
    assert block.rank() == 2
    assert adjoints.rank() == 2

    pairings = (adjoints.T * source).applyfunc(canonical)
    expected = -sp.Rational(1152, 203) * (-265 + 149 * sp.sqrt(3))
    assert canonical(pairings[0]) == 0
    assert canonical(pairings[1] - expected) == 0
    assert [str(canonical(item)) for item in pairings] == value["polar_p_cokernel"]["pairings"]
    assert 265**2 - 3 * 149**2 == value["polar_p_cokernel"]["quadratic_field_norm_witness"] == 3622
    assert value["second_order_verdict"]["status"] == "OBSTRUCTED"
    assert value["workload_progress"]["remaining_axisymmetric_L4_coefficients"] == 106


if __name__ == "__main__":
    independently_verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE4_BOUNDED_OBSTRUCTION independent verification: PASS")

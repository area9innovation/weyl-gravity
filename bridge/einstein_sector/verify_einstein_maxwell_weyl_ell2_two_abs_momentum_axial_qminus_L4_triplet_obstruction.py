#!/usr/bin/env python3
"""Independent exact verifier for the axial q-minus L=4 triplet."""
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


CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.schema.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_qminus_pair_L4_q2_slice.json"
CANDIDATES = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json"


def parse(value: str, **symbols: sp.Expr) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, **symbols})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def direct_slice_source(
    k_1: sp.Expr,
    omega_1: sp.Expr,
    k_2: sp.Expr,
    omega_2: sp.Expr,
) -> sp.Matrix:
    """Specialize the content-addressed action rows without producer imports."""

    value = json.loads(SLICE.read_text())
    assert value["result_id"] == "EINSTEIN_MAXWELL_WEYL_ELL2_AXIAL_QMINUS_PAIR_L4_Q2_SLICE"
    assert value["pbw_support"]["relevant_q2_terms"] == 842
    symbols = {"k_1": k_1, "omega_1": omega_1, "k_2": k_2, "omega_2": omega_2}
    return sp.Matrix([parse(row, **symbols) for row in value["source_action_rows"]])


def verify_symbolic_q_adjoint(encoded: dict[str, object]) -> None:
    """Independently reduce the q adjoint modulo its two shell relations."""

    momentum, frequency, target_mass = sp.symbols("K Omega mu", real=True)
    adjoint = sp.Matrix([
        -2 * (20 * momentum**2 - target_mass * momentum**2 - 20),
        2 * momentum * frequency * (20 - target_mass),
        -2 * (20 * momentum**2 - target_mass * momentum**2 + 400 - 20 * target_mass - 20),
        20,
    ])
    action, (eigenvalue, target_momentum, target_frequency) = _action_operator()
    defect = action.subs({
        eigenvalue: 20,
        target_momentum: momentum,
        target_frequency: frequency,
    }).T * adjoint
    shell = frequency**2 - momentum**2 - target_mass
    mass_polynomial = target_mass**2 - 40 * target_mass + 360
    shell_remainders = [
        sp.factor(sp.rem(sp.Poly(sp.expand(entry), frequency), sp.Poly(shell, frequency)).as_expr())
        for entry in defect
    ]
    final_remainders = [
        sp.factor(sp.rem(remainder, mass_polynomial, target_mass))
        for remainder in shell_remainders
    ]
    assert final_remainders == [0, 0, 0, 0]
    assert encoded["shell_relation"] == str(shell)
    assert encoded["q_mass_polynomial"] == str(mass_polynomial)
    assert encoded["shell_remainders_before_q_mass_reduction"] == [
        str(value) for value in shell_remainders
    ]
    assert encoded["final_remainders"] == ["0", "0", "0", "0"]


def verify_q_record(record: dict[str, object], target_sign: int) -> None:
    rho = parse(str(record["rho"]))
    k_1, k_2 = sp.sqrt(rho), -2 * sp.sqrt(rho)
    offset = 6 - 2 * sp.sqrt(3)
    omega_1 = sp.sqrt(rho + offset)
    omega_2 = sp.sqrt(4 * rho + offset)
    momentum = k_1 + k_2
    frequency = omega_1 + omega_2
    target_mass = 20 + target_sign * 2 * sp.sqrt(10)
    assert canonical(frequency**2 - momentum**2 - target_mass) == 0
    assert parse(str(record["shell_defect"])) == 0

    source = direct_slice_source(k_1, omega_1, k_2, omega_2)

    adjoint = sp.Matrix([
        -2 * (20 * momentum**2 - target_mass * momentum**2 - 20),
        2 * momentum * frequency * (20 - target_mass),
        -2 * (20 * momentum**2 - target_mass * momentum**2 + 400 - 20 * target_mass - 20),
        20,
    ])
    assert record["target_block_rank"] == 3
    assert record["cokernel_dimension"] == 1
    assert record["kernel_defect"] == ["0", "0", "0", "0"]

    pairing = canonical((adjoint.T * source)[0])
    assert canonical(pairing - parse(str(record["pairing"]))) == 0
    coefficients = record["pairing_annihilating_polynomial_coefficients"]
    polynomial = sp.Poly.from_list(coefficients, sp.symbols("pairing"))
    assert canonical(polynomial.as_expr().subs(polynomial.gens[0], pairing)) == 0
    assert record["annihilator_defect"] == "0"
    assert polynomial.eval(0) == record["nonzero_constant_term"] != 0


def independently_verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert hashlib.sha256(SCHEMA.read_bytes()).hexdigest() == value["schema_sha256"]
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    rows = json.loads(CANDIDATES.read_text())["candidate_ledger"]["rows"]
    for index, target in ((3, "q_minus"), (4, "p_extra"), (5, "q_plus")):
        row = rows[index - 1]
        assert row["first_branch"] == row["second_branch"] == "q_minus"
        assert row["target_branch"] == target
        assert row["output_ell"] == 4
        assert row["canonical_signed_momenta"] == [1, -2]

    momentum, frequency, target_mass = sp.symbols("K Omega mu", real=True)
    symbolic_adjoint = sp.Matrix([
        -2 * (20 * momentum**2 - target_mass * momentum**2 - 20),
        2 * momentum * frequency * (20 - target_mass),
        -2 * (20 * momentum**2 - target_mass * momentum**2 + 400 - 20 * target_mass - 20),
        20,
    ])
    action, (eigenvalue, target_momentum, target_frequency) = _action_operator()
    symbolic_block = action.subs({eigenvalue: 20, target_momentum: momentum, target_frequency: frequency})
    defect = symbolic_block.T * symbolic_adjoint
    shell = frequency**2 - momentum**2 - target_mass
    mass_polynomial = target_mass**2 - 40 * target_mass + 360
    remainders = [
        sp.factor(sp.rem(
            sp.rem(sp.Poly(sp.expand(entry), frequency), sp.Poly(shell, frequency)).as_expr(),
            mass_polynomial,
            target_mass,
        ))
        for entry in defect
    ]
    assert remainders == [0, 0, 0, 0]
    symbolic = value["q_primary_symbolic_adjoint"]
    assert symbolic["shell_relation"] == str(shell)
    assert symbolic["q_mass_polynomial"] == str(mass_polynomial)
    assert symbolic["final_remainders"] == ["0", "0", "0", "0"]

    triplet = value["triplet"]
    verify_symbolic_q_adjoint(value["q_primary_symbolic_adjoint"])
    verify_q_record(triplet[0], -1)
    verify_q_record(triplet[2], 1)
    assert triplet[1]["candidate_index"] == 4
    assert triplet[1]["target_branch"] == "p_extra"
    assert triplet[1]["bounded_status"] == "OBSTRUCTED"
    assert triplet[1]["nonzero_norm_witness"] == 3622
    assert triplet[1]["pairings"][0] == "0"
    assert triplet[1]["pairings"][1] != "0"

    common = value["q_primary_common_nonzero_witness"]
    expected = [
        2401,
        13649577984,
        -3277767710343168,
        -271550576338082463744,
        480328793324440503975936,
    ]
    assert common["annihilating_polynomial_coefficients"] == expected
    assert common["constant_term"] == expected[-1] != 0
    assert common["zero_is_not_a_root"]
    assert common["certified_polar_primary_decomposition"] == "(K[omega]/(p))^2 direct-sum K[omega]/(q)"
    assert value["workload_progress"]["resolved_axisymmetric_L4_coefficients"] == 4
    assert value["workload_progress"]["remaining_axisymmetric_L4_coefficients"] == 104
    assert not value["classification"]["all_axisymmetric_L4_coefficients_classified"]


if __name__ == "__main__":
    independently_verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_AXIAL_QMINUS_L4_TRIPLET_OBSTRUCTION independent verification: PASS")

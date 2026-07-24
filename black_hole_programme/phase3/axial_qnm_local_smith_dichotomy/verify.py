#!/usr/bin/env python3
"""Independent exact verifier for the local QNM Smith dichotomy."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value)


def matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(item) for item in row] for row in rows])


def valuation_polynomial(value: sp.Expr, z: sp.Symbol) -> int:
    polynomial = sp.Poly(sp.cancel(value), z)
    if polynomial.is_zero:
        raise ValueError("zero has infinite valuation")
    return min(power[0] for power, coefficient in polynomial.terms()
               if coefficient != 0)


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != (
        "phase3-axial-qnm-local-smith-dichotomy-v1"
    ):
        errors.append("schema drift")
    if document.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]:
        errors.append("dependency-tag drift")
    if document.get("status") != "EXACT_DICHOTOMY_BETA_UNEVALUATED":
        errors.append("open beta evaluation was promoted")
    if document["scope"].get("time_phase") != "exp(+I*omega*t)":
        errors.append("time convention drift")
    if document["scope"].get("damped_QNM_half_plane") != "Im(omega)>0":
        errors.append("damped-half-plane drift")

    schema_ref = document["provenance"]["schema"]
    if (schema_ref["path"] != "schema.json"
            or schema_ref["sha256"] != sha256(SCHEMA)):
        errors.append("schema provenance drift")

    z = sp.Symbol("z")
    u_a, u_f = sp.symbols("u_a u_f")
    b_0, b_1, g_0 = sp.symbols("b_0 b_1 g_0")
    c_0, d_0 = sp.symbols("c_0 d_0")
    a = u_a * z
    f = u_f

    elimination = document["spin_one_elimination"]
    left = matrix(elimination["left_matrix"])
    source = matrix(elimination["input_matrix"])
    target = matrix(elimination["output_matrix"])
    if sp.simplify(left * source - target) != sp.zeros(3):
        errors.append("spin-one elimination identity failed")
    if sp.simplify(left.det() - 1) != 0:
        errors.append("spin-one elimination is not invertible")
    if sp.simplify(target[2, 2] - f) != 0:
        errors.append("spin-one unit drift")

    proof = document["local_dvr_proof"]
    nonzero = proof["nonzero_class_case"]
    zero = proof["zero_class_case"]
    matrix_unit = sp.Matrix([[a, b_0 + b_1 * z], [0, a]])
    matrix_divisible = sp.Matrix([[a, a * g_0], [0, a]])
    for name, model, expected in (
        ("nonzero", matrix_unit, [0, 2]),
        ("zero", matrix_divisible, [1, 1]),
    ):
        finite_values = [
            valuation_polynomial(entry, z)
            for entry in model if entry != 0
        ]
        first = min(finite_values)
        det_value = valuation_polynomial(model.det(), z)
        actual = [first, det_value - first]
        if actual != expected:
            errors.append(f"{name} local-DVR Smith derivation failed")
    if nonzero["spin_two_pair_valuations"] != [0, 2]:
        errors.append("nonzero-class Smith valuations drift")
    if nonzero["factor_ordered_full_valuations"] != [0, 2, 0]:
        errors.append("nonzero-class factor order drift")
    if nonzero["sorted_full_smith_valuations"] != [0, 0, 2]:
        errors.append("nonzero-class sorted Smith drift")
    if zero["spin_two_pair_valuations"] != [1, 1]:
        errors.append("zero-class Smith valuations drift")
    if zero["factor_ordered_full_valuations"] != [1, 1, 0]:
        errors.append("zero-class factor order drift")
    if zero["sorted_full_smith_valuations"] != [0, 1, 1]:
        errors.append("zero-class sorted Smith drift")

    selector = proof["connection_minor_selector"]
    resonance = matrix(selector["resonance_matrix_nonzero_branch"])
    minor = sp.factor(resonance.extract([0, 2], [1, 2]).det())
    if sp.simplify(minor - b_0 * u_f) != 0:
        errors.append("connection-minor selector identity failed")
    if parse(selector["minor_rows_one_three_columns_two_three"]) != minor:
        errors.append("recorded connection minor drift")
    if resonance.rank() != 2:
        errors.append("nonzero-class resonance rank is not two")
    if resonance.subs(b_0, 0).rank() != 1:
        errors.append("zero-class resonance rank is not one")
    if selector["nonzero_class_rank"] != 2:
        errors.append("recorded nonzero-class rank drift")
    if selector["zero_class_rank"] != 1:
        errors.append("recorded zero-class rank drift")
    fitting = selector["second_fitting_ideal"]
    full_nonzero = sp.Matrix([
        [a, b_0 + b_1 * z, c_0],
        [0, a, d_0],
        [0, 0, f],
    ])
    full_zero = sp.Matrix([
        [a, a * g_0, c_0],
        [0, a, d_0],
        [0, 0, f],
    ])
    pairs = [(0, 1), (0, 2), (1, 2)]
    nonzero_minors = [
        sp.factor(full_nonzero.extract(rows, cols).det())
        for rows in pairs for cols in pairs
    ]
    zero_minors = [
        sp.factor(full_zero.extract(rows, cols).det())
        for rows in pairs for cols in pairs
    ]
    recorded_nonzero = [
        parse(value) for value in fitting["generators_nonzero_branch"]
    ]
    recorded_zero = [
        parse(value) for value in fitting["generators_zero_branch"]
    ]
    if any(sp.simplify(x - y) != 0
           for x, y in zip(recorded_nonzero, nonzero_minors)):
        errors.append("nonzero-class Fitting generators drift")
    if any(sp.simplify(x - y) != 0
           for x, y in zip(recorded_zero, zero_minors)):
        errors.append("zero-class Fitting generators drift")
    nonzero_vals = [
        valuation_polynomial(value, z)
        for value in nonzero_minors if value != 0
    ]
    zero_vals = [
        valuation_polynomial(value, z)
        for value in zero_minors if value != 0
    ]
    if min(nonzero_vals) != 0 or fitting["nonzero_class"] != "O_{omega_n}":
        errors.append("nonzero-class second Fitting ideal is not the unit ideal")
    if min(zero_vals) != 1 or fitting["zero_class"] != "(a)":
        errors.append("zero-class second Fitting ideal is not (a)")
    if selector["frame_scope"] != "normalized triangular factor frame":
        errors.append("selected minor was made frame invariant")

    inverse_unit = matrix(nonzero["inverse_matrix"])
    inverse_divisible = matrix(zero["inverse_matrix"])
    if sp.simplify(matrix_unit * inverse_unit - sp.eye(2)) != sp.zeros(2):
        errors.append("nonzero-class inverse mismatch")
    if (sp.simplify(
            matrix_divisible * inverse_divisible - sp.eye(2))
            != sp.zeros(2)):
        errors.append("zero-class inverse mismatch")
    offdiag_unit = sp.cancel(inverse_unit[0, 1])
    if valuation_polynomial(offdiag_unit.as_numer_denom()[1], z) != 2:
        errors.append("double-pole denominator not certified")
    if valuation_polynomial(
            inverse_divisible[0, 1].as_numer_denom()[1], z) != 1:
        errors.append("semisimple inverse pole is not simple")

    fredholm = document["fredholm_invariant"]
    normal = fredholm["finite_normal_form"]
    L = matrix(normal["L"])
    Q = matrix(normal["Q"])
    E = matrix(normal["E"])
    right = sp.Matrix([parse(item) for item in normal["right_germ"]])
    left_germ = sp.Matrix([[
        parse(item) for item in normal["left_germ"]
    ]])
    if L * right != sp.zeros(2, 1) or left_germ * L != sp.zeros(1, 2):
        errors.append("Fredholm kernel/cokernel normal form failed")
    beta = (left_germ * E * right)[0]
    shifted = (
        left_germ * (E + L * Q - Q * L) * right
    )[0]
    if sp.simplify(shifted - beta) != 0:
        errors.append("Fredholm commutator invariance failed")
    if parse(normal["beta_shift"]) != 0:
        errors.append("recorded beta shift is nonzero")

    conditional = fredholm["conditional_operator_resolvent"]
    effective = matrix(conditional["effective_pencil"])
    effective_inverse = matrix(conditional["effective_inverse"])
    if sp.simplify(effective * effective_inverse - sp.eye(2)) != sp.zeros(2):
        errors.append("conditional Fredholm effective inverse failed")
    principal = sp.simplify(
        sp.limit(z**2 * effective_inverse[0, 1], z, 0)
    )
    if parse(conditional["double_pole_principal_coefficient"]) != principal:
        errors.append("conditional Fredholm principal coefficient drift")
    if principal != -sp.Symbol("beta_n") / sp.Symbol("alpha_n")**2:
        errors.append("conditional Fredholm double-pole formula failed")
    if conditional["physical_realization_constructed"]:
        errors.append("physical Fredholm realization falsely claimed")

    boundary = document["boundary"]
    if boundary["beta_n_evaluated"]:
        errors.append("beta evaluation falsely claimed")
    if boundary["smith_case_selected_for_any_QNM"]:
        errors.append("QNM Smith case falsely selected")
    missing = set(boundary["missing"])
    if not any("adjoint QNM" in item for item in missing):
        errors.append("adjoint-QNM dependency omitted")
    if not any("beta_n" in item for item in missing):
        errors.append("beta evaluation dependency omitted")
    flags = document["claim_flags"]
    for flag in (
        "spin_one_unit_elimination_exact",
        "local_smith_dichotomy_exact",
        "fredholm_commutator_invariance_exact",
        "connection_minor_rank_selector_exact",
        "conditional_fredholm_principal_part_exact",
    ):
        if flags.get(flag) is not True:
            errors.append(f"exact claim demoted: {flag}")
    for flag in (
        "beta_n_evaluated",
        "physical_QNM_fredholm_realization_constructed",
        "simple_QNM_smith_case_selected",
        "double_resolvent_pole_established",
    ):
        if flags.get(flag) is not False:
            errors.append(f"open claim promoted: {flag}")
    return errors


def verify() -> list[str]:
    return verify_document(json.loads(CERTIFICATE.read_text()))


def main() -> None:
    errors = verify()
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        raise SystemExit(1)
    print(
        "verified=true local_smith_dichotomy=true "
        "beta_n_evaluated=false"
    )


if __name__ == "__main__":
    main()

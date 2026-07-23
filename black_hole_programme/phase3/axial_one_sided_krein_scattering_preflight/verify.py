#!/usr/bin/env python3
"""Independent exact verifier for the one-sided Krein preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"


def strict_sign_positive_axis(
    expression: sp.Expr, omega: sp.Symbol, expected: int
) -> bool:
    numerator, denominator = sp.fraction(sp.cancel(expected * expression))
    for polynomial in (numerator, denominator):
        coefficients = sp.Poly(polynomial, omega).all_coeffs()
        if not all(coefficient >= 0 for coefficient in coefficients):
            return False
        if not any(coefficient > 0 for coefficient in coefficients):
            return False
    return sp.cancel(expected * expression.subs(omega, 1)) > 0


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    imported_documents: dict[str, dict] = {}

    for name, imported in document["imports"].items():
        path = ROOT / imported["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != imported["sha256"]:
            errors.append(f"import hash drift: {imported['path']}")
        imported_documents[name] = json.loads(path.read_text())
    for imported in document["source_provenance"].values():
        path = ROOT / imported["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != imported["sha256"]:
            errors.append(f"source hash drift: {imported['path']}")

    if document["status"] != "METHOD_SHORTFALL":
        errors.append("closed physical activation was promoted")
    flags = document["claim_flags"]
    if (
        flags["physical_one_sided_J_isometry_certified"]
        or flags["physical_reflection_defect_inertia_certified"]
        or flags["physical_full_scattering_matrix_constructed"]
    ):
        errors.append("physical scattering claim escaped the fail-closed gate")

    j0 = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
    jsigma = sp.diag(1, -1, -1)
    q = sp.Matrix([
        [1 / sp.sqrt(2), 1 / sp.sqrt(2), 0],
        [1 / sp.sqrt(2), -1 / sp.sqrt(2), 0],
        [0, 0, 1],
    ])
    if sp.simplify(q.conjugate().T * j0 * q - jsigma) != sp.zeros(3):
        errors.append("J0-to-Jsigma congruence failed")
    if j0 == jsigma:
        errors.append("null and signature bases were conflated")

    omega = sp.Symbol("omega", real=True, positive=True)
    local = {"omega": omega, "I": sp.I}
    audit = document["determinant_audit"]
    det_h = sp.sympify(audit["horizon_raw_determinant"], locals=local)
    det_g_factor = sp.sympify(
        audit["incoming_factor_basis_determinant"], locals=local
    )
    det_g_raw = sp.sympify(audit["incoming_raw_determinant"], locals=local)
    ratio = sp.sympify(
        audit["endpoint_normalizer_determinant_ratio"], locals=local
    )
    prefactor = sp.sympify(
        audit["Tminus_rational_prefactor_modulus_squared"], locals=local
    )
    if sp.cancel(det_g_factor / (9 * omega ** 2) - det_g_raw) != 0:
        errors.append("incoming factor/raw determinant conversion failed")
    if sp.cancel(det_h / det_g_raw - ratio) != 0:
        errors.append("endpoint normalizer determinant ratio failed")
    if sp.cancel(ratio - prefactor) != 0:
        errors.append("normalizer ratio does not cancel Tminus prefactor")
    if sp.cancel(ratio - 1) == 0:
        errors.append("bare inverse-Tminus determinant was accepted")
    horizon_document = imported_documents["future_horizon_gram"]
    pivots = [
        sp.sympify(value, locals=local)
        for value in horizon_document["ldl_pivots"]
    ]
    if not all(
        strict_sign_positive_axis(value, omega, sign)
        for value, sign in zip(pivots, (1, -1, -1))
    ):
        errors.append("positive-real horizon pivot audit failed")
    quotient_document = imported_documents["future_horizon_factor_quotient"]
    quotient = sp.sympify(
        quotient_document["spin_one_quotient"]["unit_quotient_norm"],
        locals=local,
    )
    factor_determinant = sp.sympify(
        quotient_document["spin_two_extension"]["determinant"], locals=local
    )
    if not (
        strict_sign_positive_axis(quotient, omega, -1)
        and strict_sign_positive_axis(factor_determinant, omega, -1)
    ):
        errors.append("positive-real horizon factor audit failed")

    # Method-distinct component replay in the null frame.
    names = ("a", "b", "c", "d", "e", "f")
    symbols: dict[str, tuple[sp.Symbol, sp.Symbol]] = {}
    matrices = []
    daggers = []
    for suffix in ("R", "A"):
        plain = sp.symbols(" ".join(f"{name}{suffix}" for name in names))
        bars = sp.symbols(" ".join(f"{name}{suffix}bar" for name in names))
        symbols[suffix] = plain, bars
        a, b, c, d, e, f = plain
        ab, bb, cb, db, eb, fb = bars
        matrices.append(sp.Matrix([[a, b, d], [0, c, e], [0, 0, f]]))
        daggers.append(
            sp.Matrix([[ab, 0, 0], [bb, cb, 0], [db, eb, fb]])
        )
    component = sum(
        (dagger * j0 * matrix for dagger, matrix in zip(daggers, matrices)),
        sp.zeros(3),
    )
    upper_terms = []
    for suffix in ("R", "A"):
        (a, b, c, d, e, f), (ab, bb, cb, db, eb, fb) = symbols[suffix]
        upper_terms.append(sp.Matrix([
            [0, ab * c, ab * e],
            [a * cb, b * cb + bb * c, bb * e + cb * d],
            [a * eb, b * eb + c * db, d * eb + db * e - f * fb],
        ]))
    expected_component = sum(upper_terms, sp.zeros(3))
    if sp.simplify(component - expected_component) != sp.zeros(3):
        errors.append("upper triangular component replay failed")
    lower_matrices = []
    lower_daggers = []
    for suffix in ("R", "A"):
        (a, b, c, d, e, f), (ab, bb, cb, db, eb, fb) = symbols[suffix]
        lower_matrices.append(
            sp.Matrix([[a, 0, 0], [b, c, 0], [d, e, f]])
        )
        lower_daggers.append(
            sp.Matrix([[ab, bb, db], [0, cb, eb], [0, 0, fb]])
        )
    lower_component = sum(
        (
            dagger * j0 * matrix
            for dagger, matrix in zip(lower_daggers, lower_matrices)
        ),
        sp.zeros(3),
    )
    lower_terms = []
    for suffix in ("R", "A"):
        (a, b, c, d, e, f), (ab, bb, cb, db, eb, fb) = symbols[suffix]
        lower_terms.append(sp.Matrix([
            [a * bb + ab * b - d * db, ab * c - db * e, -db * f],
            [a * cb - d * eb, -e * eb, -eb * f],
            [-d * fb, -e * fb, -f * fb],
        ]))
    if sp.simplify(lower_component - sum(lower_terms, sp.zeros(3))) != (
        sp.zeros(3)
    ):
        errors.append("lower triangular component replay failed")
    triangular = document["triangular_J0_identities"]
    if triangular["independent_equations"] != [
        "sum_X conjugate(a_X)*c_X=1",
        "sum_X conjugate(a_X)*e_X=0",
        "sum_X (conjugate(b_X)*c_X+conjugate(c_X)*b_X)=0",
        "sum_X (conjugate(b_X)*e_X+conjugate(c_X)*d_X)=0",
        "sum_X (conjugate(d_X)*e_X+conjugate(e_X)*d_X-abs(f_X)^2)=-1",
    ]:
        errors.append("recorded upper triangular equations changed")
    if triangular["lower_independent_equations"] != [
        "sum_X (conjugate(a_X)*b_X+conjugate(b_X)*a_X-abs(d_X)^2)=0",
        "sum_X (conjugate(a_X)*c_X-conjugate(d_X)*e_X)=1",
        "sum_X conjugate(d_X)*f_X=0",
        "sum_X abs(e_X)^2=0, hence e_R=e_A=0",
        "sum_X abs(f_X)^2=1",
    ]:
        errors.append("recorded lower triangular equations changed")
    # The five upper-triangular equations plus their conjugates are exactly
    # the independent upper half of component == J0.
    if triangular["alpha_gamma_mu_reduction"] != (
        "REFUSED_NOT_PROVED"
    ):
        errors.append("alpha/gamma/mu reduction was unsoundly promoted")

    activation = document["activation"]
    if activation["status"] != "MISSING_GLOBAL_CONNECTION":
        errors.append("global connection gate status changed")
    if any(
        activation[key]
        for key in (
            "physical_one_sided_J_isometry_certified",
            "physical_reflection_defect_inertia_certified",
            "physical_U_2_4_completion_certified",
        )
    ):
        errors.append("conditional U(2,4) theorem was made physical")

    theorem = document["conditional_exact_theorem"]
    if theorem["reflection_defect"]["inertia"] != [1, 2, 0]:
        errors.append("reflection defect inertia changed")
    if theorem["completion"]["physical_full_scattering_matrix"]:
        errors.append("algebraic completion was mislabeled physical")
    horizon_audit = document["horizon_positive_real_scope_audit"]
    recurrence = horizon_audit["symbolic_recurrence_audit"]
    if not horizon_audit["promoted_beyond_pilot"]:
        errors.append("positive-real horizon extension was dropped")
    if recurrence["positive_real_collisions"]:
        errors.append("positive-real recurrence collision was admitted")
    if (
        recurrence["minimum_omitted_exact_cross_current_order"] != 2
        or recurrence["constant_term_affected"]
    ):
        errors.append("symbolic omitted-head power count changed")
    for text in recurrence["basis_denominator_factors"]:
        factor = sp.sympify(text, locals=local)
        modulus_squared = sp.factor(
            factor * sp.conjugate(factor).subs(sp.conjugate(omega), omega)
        )
        if sp.Poly(modulus_squared, omega).all_coeffs()[-1] <= 0:
            errors.append(f"unproved positive-real denominator: {text}")
    eigenbasis_determinant = sp.sympify(
        recurrence["residue_eigenbasis_determinant"], locals=local
    )
    if not strict_sign_positive_axis(
        sp.factor(
            eigenbasis_determinant
            * sp.conjugate(eigenbasis_determinant).subs(
                sp.conjugate(omega), omega
            )
        ),
        omega,
        1,
    ):
        errors.append("positive-real residue eigenbasis audit failed")
    if (
        len(recurrence["compatible_resonances"]) != 3
        or any(
            not witness.endswith("residual=0")
            for witness in recurrence["compatible_resonances"]
        )
    ):
        errors.append("compatible resonance audit changed")

    return errors


def verify() -> list[str]:
    return verify_document(json.loads(CERTIFICATE.read_text()))


if __name__ == "__main__":
    found = verify()
    if found:
        for error in found:
            print(f"FAIL {error}")
        raise SystemExit(1)
    print(
        "verified=true conditional_J_isometry=true "
        "physical_activation=false determinant_ratio=true"
    )

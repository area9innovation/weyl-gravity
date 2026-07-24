#!/usr/bin/env python3
"""Independent verifier for the axial projective-cocycle certificate."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
R, W = sp.symbols("r omega")
I = sp.I


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def zero(value: sp.Expr) -> bool:
    return sp.cancel(sp.together(value)) == 0


def maximal_minor_gcd(value: sp.Matrix) -> sp.Expr:
    minors = [
        sp.factor(value[list(rows), :].det())
        for rows in itertools.combinations(range(value.rows), value.cols)
    ]
    nonzero = [minor for minor in minors if minor != 0]
    result = nonzero[0]
    for minor in nonzero[1:]:
        result = sp.gcd(result, minor)
    return sp.factor(result)


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "phase3-axial-qnm-projective-cocycle-v1":
        errors.append("schema drift")
    if document.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]:
        errors.append("dependency-tag drift")
    if document.get("status") != (
        "EXACT_RATIONAL_COCYCLE_NONTRIVIAL_QNM_UNEVALUATED"
    ):
        errors.append("status drift")

    imports = {}
    for name, reference in document.get("imports", {}).items():
        path = ROOT / reference["path"]
        if not path.is_file() or sha256(path) != reference["sha256"]:
            errors.append(f"input hash drift: {name}")
        else:
            imports[name] = json.loads(path.read_text())
    if len(imports) != 2:
        return errors

    triangular = imports["triangular_factorization"]
    complete = imports["complete_reconstruction"]
    flow6 = matrix(complete["complete_reconstruction"]["flow6"])
    source = flow6[4:, :4]
    embedding = matrix(
        triangular["carrier_exact_sequence"]["RW_embedding_J"]
    )
    master = matrix(
        triangular["Einstein_kernel_RW_equivalence"][
            "U_H1F_to_PsiPsiPrime"
        ]
    )
    extension = (master * source * embedding).applyfunc(
        lambda value: sp.cancel(sp.together(value))
    )
    rw = triangular["operators"]["L_RW"]
    a_rw, b_rw = parse(rw["a"]), parse(rw["b"])
    e00, e01, e10, e11 = (
        extension[0, 0], extension[0, 1],
        extension[1, 0], extension[1, 1],
    )
    s1_r = sp.cancel(e11 + e00 + sp.diff(e01, R))
    s0_r = sp.cancel(
        a_rw * e00 + e10 + sp.diff(e00, R) - b_rw * e01
    )
    f = (R - 2) / R
    dstar = lambda value: sp.cancel(f * sp.diff(value, R))
    u = sp.cancel(W**2 - 6 * (R - 2) * (R - 1) / R**4)
    s1 = sp.cancel(f * s1_r)
    s0 = sp.cancel(f**2 * s0_r - I * W * f * s1_r)
    cocycle = sp.cancel(s0 - sp.Rational(1, 2) * dstar(s1))
    projective = lambda value: sp.cancel(
        dstar(dstar(dstar(value)))
        + 4 * u * dstar(value)
        + 2 * dstar(u) * value
    )
    scalar = document["scalarization"]
    for key, value in (("U", u), ("s1_r", s1_r), ("s0_r", s0_r),
                       ("s1", s1), ("s0", s0)):
        if not zero(parse(scalar[key]) - value):
            errors.append(f"scalarization mismatch: {key}")
    if not scalar.get("first_extension_row_included"):
        errors.append("first extension row omitted")
    if not zero(parse(document["projective_cocycle"]["calI"]) - cocycle):
        errors.append("projective cocycle mismatch")

    ga = sp.Function("ga")(R)
    gb = sp.Function("gb")(R)
    delta_s1 = dstar(dstar(ga)) + 2 * dstar(gb)
    delta_s0 = dstar(dstar(gb)) - ga * dstar(u) - 2 * dstar(ga) * u
    gauge_check = sp.cancel(
        delta_s0 - sp.Rational(1, 2) * dstar(delta_s1)
        + sp.Rational(1, 2) * projective(ga)
    )
    if gauge_check != 0 or not document[
        "projective_cocycle"
    ]["gauge_identity_verified"]:
        errors.append("gauge identity failed")

    rho = 2 * I / W
    lead_i = sp.factor(sp.limit((R - rho)**4 * cocycle, R, rho))
    lead_k = sp.factor(sp.limit(
        (R - rho)**4 * projective(1 / (R * W - 2 * I)), R, rho
    ))
    rho_gauge = sp.factor(-2 * lead_i / lead_k) / (R * W - 2 * I)
    if not zero(
        rho_gauge
        - parse(document["local_pole_audit"]["forced_apparent_gauge"])
    ):
        errors.append("forced apparent gauge mismatch")
    m = sp.Symbol("m")
    r0_indicial = sp.factor(sp.limit(
        projective(R**m) / R**(m - 6), R, 0
    ))
    infinity_lead = sp.factor(sp.limit(
        projective(R**m) / R**(m - 1), R, sp.oo
    ))
    if not zero(r0_indicial + 8 * (m - 6) * (m - 2) * (m + 2)):
        errors.append("r=0 indicial drift")
    if infinity_lead != 4 * m * W**2:
        errors.append("infinity degree audit drift")

    residual = sp.cancel(
        cocycle + sp.Rational(1, 2) * projective(rho_gauge)
    )
    c2, c1, c0 = sp.symbols("c2 c1 c0")
    completion = c2 / R**2 + c1 / R + c0
    exact_poly = sp.Poly(
        sp.together(projective(completion) + 2 * residual)
        .as_numer_denom()[0], R
    )
    exact_matrix, exact_rhs = sp.linear_eq_to_matrix(
        exact_poly.all_coeffs(), [c2, c1, c0]
    )
    exact_record = document["rational_nonexactness"]
    if (exact_matrix.rank() != 3
            or exact_matrix.row_join(exact_rhs).rank() != 4):
        errors.append("rational nonexactness rank proof failed")
    if (exact_record["matrix_rank"] != 3
            or exact_record["augmented_rank"] != 4
            or exact_record["solution"] != "EMPTY"):
        errors.append("rational nonexactness record drift")
    exact_left = sp.Matrix([
        parse(value) for value in exact_record["left_null_witness"]
    ])
    if any(not zero(value) for value in exact_left.T * exact_matrix):
        errors.append("rational left-null witness failed")
    exact_obstruction = sp.cancel((exact_left.T * exact_rhs)[0])
    if (not zero(exact_obstruction - 40 * I * (W**2 - 3) / (3 * W))
            or not zero(
                exact_obstruction
                - parse(exact_record["left_null_obstruction"])
            )):
        errors.append("rational specialization obstruction drift")

    reducing = parse(
        document["reduced_representative"]["a_reducing"]
    )
    reduced = sp.cancel(
        cocycle + sp.Rational(1, 2) * projective(reducing)
    )
    if not zero(
        reduced
        - parse(document["reduced_representative"]["calI_reduced"])
    ):
        errors.append("reduced representative mismatch")
    if document["reduced_representative"][
        "canonical_under_all_analytic_gauges"
    ]:
        errors.append("reduced representative overpromoted")

    q = sp.Symbol("q")
    angular = -f / R**2
    angular_poly = sp.Poly(
        sp.together(
            projective(completion) + 2 * residual - 2 * q * angular
        ).as_numer_denom()[0], R
    )
    angular_matrix, angular_rhs = sp.linear_eq_to_matrix(
        angular_poly.all_coeffs(), [c2, c1, c0, q]
    )
    angular_record = document["angular_class_test"]
    if (angular_matrix.rank() != 4
            or angular_matrix.row_join(angular_rhs).rank() != 5):
        errors.append("angular nonproportionality rank proof failed")
    if (angular_record["matrix_rank"] != 4
            or angular_record["augmented_rank"] != 5
            or angular_record["solution"] != "EMPTY"):
        errors.append("angular class record drift")
    angular_left = sp.Matrix([
        parse(value) for value in angular_record["left_null_witness"]
    ])
    if any(not zero(value) for value in angular_left.T * angular_matrix):
        errors.append("angular left-null witness failed")
    angular_obstruction = sp.cancel((angular_left.T * angular_rhs)[0])
    if (not zero(
            angular_obstruction
            - 120 * I * W * (W - 2 * I) * (W + 2 * I)
            / (11 * W**2 - 6))
            or not zero(
                angular_obstruction
                - parse(angular_record["left_null_obstruction"])
            )):
        errors.append("angular specialization obstruction drift")
    if "not a physical background tangent" not in angular_record[
        "classification"
    ]:
        errors.append("angular scope drift")
    specialization = document["finite_specialization_corollary"]
    if specialization["rank_change_locus_exactness_matrix"] != ["omega=0"]:
        errors.append("exactness rank-change locus drift")
    if specialization["rank_change_locus_angular_matrix"] != ["omega=0"]:
        errors.append("angular rank-change locus drift")
    if not zero(
        maximal_minor_gcd(exact_matrix)
        - parse(specialization["maximal_minor_gcd_exactness"])
    ):
        errors.append("exactness maximal-minor gcd drift")
    if not zero(
        maximal_minor_gcd(angular_matrix)
        - parse(specialization["maximal_minor_gcd_angular"])
    ):
        errors.append("angular maximal-minor gcd drift")
    if ("No splitting or nonsplitting statement"
            not in specialization["safe_reading"]):
        errors.append("specialization boundary overpromoted")

    flags = document["claim_flags"]
    for name in (
        "exact_scalarization_rederived",
        "projective_gauge_law_exact",
        "generic_rational_ansatz_exhaustive",
        "generic_rational_cocycle_nontrivial",
        "declared_reduced_representative_exact",
        "generic_angular_class_nonproportional",
    ):
        if flags.get(name) is not True:
            errors.append(f"proved flag demoted: {name}")
    for name in (
        "beta_n_evaluated",
        "physical_QNM_fredholm_realization_constructed",
        "simple_QNM_smith_case_selected",
        "QNM_double_pole_established",
    ):
        if flags.get(name) is not False:
            errors.append(f"open flag promoted: {name}")
    return errors


def verify() -> list[str]:
    errors = verify_document(json.loads(CERTIFICATE.read_text()))
    receipt = json.loads(RECEIPT.read_text())
    for name, expected in receipt.get("artifacts", {}).items():
        path = HERE / name
        if not path.is_file() or sha256(path) != expected:
            errors.append(f"artifact hash drift: {name}")
    return errors


if __name__ == "__main__":
    found = verify()
    if found:
        for error in found:
            print(f"FAIL {error}")
        raise SystemExit(1)
    print(
        "verified=true rational_nonexact=true "
        "angular_nonproportional=true beta_n_evaluated=false"
    )

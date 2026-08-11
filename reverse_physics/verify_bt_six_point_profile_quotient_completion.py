#!/usr/bin/env python3
"""Independent verifier for the BT six-point profile quotient completion."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-profile-quotient-completion-v1.schema.json",
)
PHYSICAL = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
)
SIX = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
)
INTERFERENCE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1.json",
)
BRANCHING = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_matrix(rows, local):
    import sympy as sp

    return sp.Matrix(
        [[sp.factor(sp.sympify(value, locals=local)) for value in row] for row in rows]
    )


def rational_matrix(rows):
    import sympy as sp

    return sp.Matrix([[frac(value) for value in row] for row in rows])


def fixture_replay(row):
    import sympy as sp

    a0, a1, tau1, a2 = (
        frac(row[name]) for name in ("a0", "a1", "tau1", "a2")
    )
    u = (2 * tau1 * (a0 + a1) - (a0 - a1) ** 2) / (2 * tau1**2)
    v = a2 / 2
    eta = sp.Matrix(
        [[0, 0, 0, 3], [0, 0, 3, 0], [0, 3, 0, 0], [3, 0, 0, 0]]
    )
    K = sp.Matrix([[0, 3], [3, 0]])
    R = sp.Matrix([[1, 0, 1, 0], [0, 1, 0, 1]])
    D = sp.diag(u, u, v, v)
    G = D.T * R.T * K * R * D
    A = eta.inv() * G
    P = A / (2 * u * v)
    X = sp.Matrix([frac(value) for value in row["coefficients"]])
    C = R * D * X
    physical = (C.T * K * C)[0]
    projected = 2 * u * v * (P * X).T * eta * (P * X)
    return (
        frac(row["u"]) == u
        and frac(row["v"]) == v
        and frac(row["two_u_v"]) == 2 * u * v
        and rational_matrix(row["raised_pullback"]) == A
        and rational_matrix(row["projector"]) == P
        and [frac(value) for value in row["physical_collapse"]] == list(C)
        and frac(row["physical_contraction"]) == physical
        and frac(row["projected_contraction"]) == projected[0]
        and physical == projected[0]
        and row["contractions_agree"] is True
    )


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    disposition = certificate.get("disposition", {})
    quotient = certificate.get("canonical_quotient", {})
    affiliation = certificate.get("branching_affiliation", {})
    preflight = (
        not errors
        and certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1"
        and disposition.get("canonical_krein_orthogonal_quotient")
        == "CONSTRUCTED"
        and disposition.get("physical_collapse_reconstruction")
        == "EXACT_POINTWISE_IDENTITY"
        and disposition.get("second_positive_scalar_species_jump")
        == "AMPLITUDE_AFFILIATED_ON_QUOTIENT"
        and disposition.get("third_jump_species_affiliation") == "NOT_COMPUTED"
        and disposition.get("complete_BT_probability") == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and quotient.get("kernel_disposition")
        == "NONDEGENERATE_AND_EXACTLY_PHYSICAL_COLLAPSE_INVISIBLE"
        and quotient.get("image_raised_endomorphism") == "2*u*v*I2"
        and affiliation.get("second_jump_status")
        == "AMPLITUDE_AFFILIATED_ON_CANONICAL_PROFILE_QUOTIENT"
        and frac(affiliation.get("conditional_second_rate")) == Fraction(5, 64)
        and "anything LORENTZIAN-CAUSAL"
        in certificate.get("does_not_establish", [])
    )
    if not preflight:
        return {"serialized_claim_preflight": False}

    u, v, z = sp.symbols("u v z", positive=True, nonzero=True)
    local = {"u": u, "v": v, "z": z}
    eta = sp.Matrix(
        [[0, 0, 0, 3], [0, 0, 3, 0], [0, 3, 0, 0], [3, 0, 0, 0]]
    )
    K = sp.Matrix([[0, 3], [3, 0]])
    R = sp.Matrix([[1, 0, 1, 0], [0, 1, 0, 1]])
    D = sp.diag(u, u, v, v)
    G = D.T * R.T * K * R * D
    A = (eta.inv() * G).applyfunc(sp.factor)
    P = (A / (2 * u * v)).applyfunc(sp.factor)
    N_minus = sp.Matrix([[v, 0], [0, v], [-u, 0], [0, -u]])
    N_plus = sp.Matrix([[v, 0], [0, v], [u, 0], [0, u]])
    J = sp.Matrix([[0, 1], [1, 0]])

    serialized_eta = parse_matrix(
        certificate["declared_carrier"]["tensor_metric_eta"], local
    )
    serialized_A = parse_matrix(
        certificate["physical_pullback"]["raised_A_generic"], local
    )
    serialized_P = parse_matrix(quotient["projector_P_generic"], local)
    serialized_kernel = parse_matrix(quotient["kernel_basis_columns"], local)
    serialized_image = parse_matrix(quotient["image_basis_columns"], local)
    characteristic = A.charpoly()
    characteristic_variable = characteristic.gen

    l0, q0, l1, q1 = sp.symbols("l0 q0 l1 q1", real=True)
    X = sp.Matrix([l0, q0, l1, q1])
    C = R * D * X
    pointwise = sp.simplify(
        (C.T * K * C)[0]
        - 2 * u * v * ((P * X).T * eta * (P * X))[0]
    )

    physical = load(PHYSICAL)
    six = load(SIX)
    interference = load(INTERFERENCE)
    branching = load(BRANCHING)
    q0_rate = frac(
        physical["normalization_ledger"]["physical_per_pair_Born_normalized_response"]
    )
    selected = frac(
        six["threshold_and_factorial_analysis"]["normalization"]
        ["selected_nested_history_relative_to_Born"]
    )
    branching_q1 = frac(
        branching["rate_factorization"]["extension_rate_squares"][1]
    )

    Q, L = sp.symbols("Q L", real=True, nonzero=True)
    D5 = sp.diag(2 * Q, 2 * Q, 2 * L, 2 * L)
    X5 = sp.Matrix([0, sp.Rational(1, 2), sp.Rational(1, 2), 0])
    C5 = R * D5 * X5
    A5 = eta.inv() * D5.T * R.T * K * R * D5
    P5 = A5 / (8 * Q * L)
    hard5 = (X5.T * eta * X5)[0]
    projected5 = sp.factor((P5 * X5).T * eta * (P5 * X5))[0]
    child5 = (C5.T * K * C5)[0]

    fixtures = quotient.get("exact_fixtures", [])
    checks = {
        "schema": not errors,
        "identity_tags_lifecycle": certificate.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED",
        "serialized_tensor_metric": serialized_eta == eta
        and eta.det() == 81,
        "direct_pullback_matrix": serialized_A == A and A.rank() == 2,
        "spectrum_and_minimal_identity": sp.simplify(
            characteristic.as_expr()
            - characteristic_variable**2
            * (characteristic_variable - 2 * u * v) ** 2
        ) == 0
        and sp.simplify(A * A - 2 * u * v * A) == sp.zeros(4),
        "serialized_projector": serialized_P == P,
        "projector_idempotent_selfadjoint": sp.simplify(P * P - P)
        == sp.zeros(4)
        and sp.simplify(eta.inv() * P.T * eta - P) == sp.zeros(4),
        "serialized_kernel_image_bases": serialized_kernel == N_minus
        and serialized_image == N_plus,
        "kernel_exact_and_collapse_invisible": A * N_minus == sp.zeros(4, 2)
        and R * D * N_minus == sp.zeros(2),
        "image_exact_and_scalar_collapse": P * N_plus == N_plus
        and sp.simplify(R * D * N_plus - 2 * u * v * sp.eye(2))
        == sp.zeros(2),
        "orthogonal_nondegenerate_split": sp.simplify(
            N_minus.T * eta * N_plus
        ) == sp.zeros(2)
        and sp.simplify(N_minus.T * eta * N_minus + 6 * u * v * J)
        == sp.zeros(2)
        and sp.simplify(N_plus.T * eta * N_plus - 6 * u * v * J)
        == sp.zeros(2),
        "profile_fundamental_symmetry_positive": sp.simplify(
            (N_plus.T * eta * N_plus) * J - 6 * u * v * sp.eye(2)
        ) == sp.zeros(2),
        "pointwise_physical_reconstruction": pointwise == 0,
        "three_exact_fraction_fixtures": len(fixtures) == 3
        and all(fixture_replay(row) for row in fixtures),
        "outer_degenerate_surface_resolved": not any(
            symbol.name == "tau2" for symbol in P.free_symbols
        )
        and quotient.get("outer_degenerate_surface")
        == "RESOLVED_WITHOUT_DIVIDING_BY_B01; P HAS_NO_TAU2_DEPENDENCE",
        "five_point_prefix_hard_and_projection": hard5 == sp.Rational(3, 2)
        and projected5 == sp.Rational(3, 4),
        "five_point_prefix_collapse_and_ratio": C5 == sp.Matrix([L, Q])
        and child5 == 6 * L * Q
        and sp.simplify(-child5 / hard5 + 4 * L * Q) == 0,
        "predecessor_obstruction_scoped_and_imported": interference[
            "disposition"
        ]["second_positive_scalar_I2_species_jump"]
        == "EXACTLY_OBSTRUCTED_ON_DECLARED_CARRIER"
        and disposition.get("six_point_interference_obstruction")
        == "RESOLVED_BY_MINIMAL_GRADING_FAITHFUL_ENLARGEMENT",
        "conditional_rate_from_independent_certificates": q0_rate
        == Fraction(1, 48)
        and selected == Fraction(5, 3072)
        and selected / q0_rate == branching_q1 == Fraction(5, 64),
        "topology_independent_tree_phase": {
            ((-sp.I) ** vertices) * sp.I ** (vertices - 1)
            for vertices in range(1, 7)
        }
        == {-sp.I},
        "claim_boundary": disposition.get("third_jump_species_affiliation")
        == "NOT_COMPUTED"
        and disposition.get("complete_BT_probability") == "NOT_CONSTRUCTED"
        and disposition.get("spacetime_local_physical_S_matrix")
        == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL"
        in certificate.get("does_not_establish", []),
        "hashes": len(certificate.get("provenance", {}).get("inputs", []))
        == 5
        and all(
            row.get("sha256") == sha256(row.get("path", ""))
            for row in certificate.get("provenance", {}).get("inputs", [])
        ),
        "producer_checks": certificate.get("checks", {}).get("passed")
        == certificate.get("checks", {}).get("total")
        == 42
        and certificate.get("checks", {}).get("failures") == []
        and all(certificate.get("checks", {}).get("details", {}).values()),
    }
    for error in errors:
        print("schema", list(error.path), error.message)
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("[OK ] " if ok else "[FAIL] ") + name)
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (len(checks) - len(failures), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

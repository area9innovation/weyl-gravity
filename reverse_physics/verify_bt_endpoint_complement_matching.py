#!/usr/bin/env python3
"""Independent verifier for the BT endpoint-complement matching theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ENDPOINT_COMPLEMENT_MATCHING_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-endpoint-complement-matching-v1.schema.json",
)
EXPECTED_INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-endpoint-complement-matching.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
]


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sp_rat(value, sp):
    value = frac(value)
    return sp.Rational(value.numerator, value.denominator)


def main(argv=None):
    import jsonschema
    import sympy as sp

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    cert = load(args.verify)
    schema = load(SCHEMA)
    checks = {}
    try:
        jsonschema.Draft202012Validator(schema).validate(cert)
        checks["strict_schema"] = True
    except jsonschema.ValidationError:
        checks["strict_schema"] = False

    checks["identity_and_claim_tags"] = (
        cert.get("certificate")
        == "REVERSE_PHYSICS_BT_ENDPOINT_COMPLEMENT_MATCHING_V1"
        and cert.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and cert.get("lifecycle_state") == "CLASSIFIED"
    )
    records = cert.get("provenance", {}).get("inputs", [])
    checks["exact_input_inventory"] = [row.get("path") for row in records] == EXPECTED_INPUTS
    checks["all_input_hashes_reproduced"] = (
        len(records) == len(EXPECTED_INPUTS)
        and all(
            row.get("sha256")
            == sha256(os.path.join(ROOT, row.get("path", "")))
            for row in records
        )
    )
    predecessors = [load(os.path.join(ROOT, path)) for path in EXPECTED_INPUTS[1:]]
    endpoint, moller, physical, eq19, zero_mode = predecessors
    checks["all_predecessor_rails_green"] = all(
        value["checks"]["ok"] for value in predecessors
    )

    z = sp.symbols("z", real=True)
    probes = [sp.Integer(1), z * (1 - z), z**2 * (1 - z) ** 2]
    # Method-distinct from the producer: integrate the Taylor-subtracted
    # polynomials symbolically instead of using coefficient sums.
    def left_plus(polynomial):
        jet = (
            polynomial.subs(z, 0)
            + z * sp.diff(polynomial, z).subs(z, 0)
            + z**2 * sp.diff(polynomial, z, 2).subs(z, 0) / 2
        )
        return sp.integrate(sp.cancel((polynomial - jet) / z**3), (z, 0, 1))

    def h_plus(polynomial):
        return sp.simplify(
            -sp.Rational(1, 2)
            * (left_plus(polynomial) + left_plus(polynomial.subs(z, 1 - z)))
        )

    def endpoint_action(polynomial, order):
        return sp.simplify(
            (-1) ** order * sp.diff(polynomial, z, order).subs(z, 0)
            + sp.diff(polynomial, z, order).subs(z, 1)
        )

    A = sp.Matrix(
        [[endpoint_action(probe, order) for order in range(3)] for probe in probes]
    )
    base = sp.Matrix([h_plus(probe) for probe in probes])
    checks["symbolic_integration_reconstructs_reference"] = base == sp.Matrix([0, 0, sp.Rational(3, 2)])
    checks["derivative_actions_reconstruct_jet_matrix"] = A == sp.Matrix([[2, 0, 0], [0, -2, -4], [0, 0, 4]])
    checks["endpoint_coordinates_are_independent"] = A.det() == -16

    extension = cert.get("endpoint_extension", {})
    serialized_A = sp.Matrix(
        [[sp_rat(value, sp) for value in row] for row in extension.get("jet_action_matrix", [])]
    )
    serialized_base = sp.Matrix(
        [sp_rat(value, sp) for value in extension.get("reference_actions_on_product_probes", [])]
    )
    checks["serialized_endpoint_data_reproduced"] = (
        serialized_A == A
        and serialized_base == base
        and sp_rat(extension.get("jet_matrix_determinant", {}), sp) == A.det()
    )

    rho = sp.symbols("rho", positive=True)
    c0, c1, c2 = sp.symbols("c0 c1 c2", real=True)
    K = sp.Matrix(
        [
            [base[0] + 2 * c0, base[1] - 2 * c1 - 4 * c2],
            [base[1] - 2 * c1 - 4 * c2, base[2] + 4 * c2],
        ]
    )
    target = sp.Matrix([[0, -rho], [-rho, -2]])
    # Independent triangular elimination, not the producer's solve call.
    c0_star = -base[0] / 2
    c2_star = (-2 - base[2]) / 4
    c1_star = sp.simplify((rho + base[1] - 4 * c2_star) / 2)
    solution = {c0: c0_star, c1: c1_star, c2: c2_star}
    checks["triangular_matching_solution"] = solution == {
        c0: 0,
        c1: sp.Rational(7, 4) + rho / 2,
        c2: -sp.Rational(7, 8),
    }
    checks["matched_gram_identity"] = sp.simplify(K.subs(solution) - target) == sp.zeros(2)
    checks["matching_system_unique"] = A.det() != 0

    theorem = cert.get("matching_theorem", {})
    checks["serialized_matching_law"] = (
        theorem.get("target_gram") == "G_missing(rho)=[[0,-rho],[-rho,-2]]"
        and theorem.get("unique_coefficients") == ["c0=0", "c1=7/4+rho/2", "c2=-7/8"]
        and theorem.get("coefficient_derivative_with_respect_to_rho") == ["0", "1/2", "0"]
    )
    beta00, beta01, beta11 = sp.symbols("beta00 beta01 beta11", real=True)
    generic_c1 = (rho + beta01 + beta11 + 2) / 2
    checks["reference_change_cannot_remove_slope"] = sp.diff(generic_c1, rho) == sp.Rational(1, 2)

    source_fixture_rows = physical["amplitude_factorization"]["exact_fixtures"]
    cert_fixture_rows = cert.get("physical_fixtures", [])
    source_rhos = [sp_rat(row["rho"], sp) for row in source_fixture_rows]
    checks["three_exact_physical_rhos_imported"] = (
        len(cert_fixture_rows) == len(source_rhos) == 3
        and [sp_rat(row["rho"], sp) for row in cert_fixture_rows] == source_rhos
    )
    fixture_matches = []
    fixture_c1s = []
    for index, (row, rho_i) in enumerate(zip(cert_fixture_rows, source_rhos)):
        coeffs = [sp_rat(value, sp) for value in row.get("coefficients", [])]
        if len(coeffs) != 3:
            fixture_matches.append(False)
            continue
        K_i = K.subs({c0: coeffs[0], c1: coeffs[1], c2: coeffs[2]})
        serialized_gram = sp.Matrix(
            [[sp_rat(value, sp) for value in gram_row]
             for gram_row in row.get("matched_gram", [])]
        )
        fixture_matches.append(
            row.get("fixture_index") == index
            and coeffs == [0, sp.Rational(7, 4) + rho_i / 2, -sp.Rational(7, 8)]
            and K_i == sp.Matrix([[0, -rho_i], [-rho_i, -2]])
            and serialized_gram == K_i
        )
        fixture_c1s.append(coeffs[1])
    checks["all_fixture_matches_reconstructed"] = all(fixture_matches)
    checks["physical_rhos_and_required_c1s_are_distinct"] = (
        len(set(source_rhos)) == 3 and len(set(fixture_c1s)) == 3
    )

    # A fixed K cannot equal two different targets; this is independent of
    # the chosen affine endpoint reference.
    rho_a, rho_b = sp.symbols("rho_a rho_b", real=True)
    target_a = sp.Matrix([[0, -rho_a], [-rho_a, -2]])
    target_b = sp.Matrix([[0, -rho_b], [-rho_b, -2]])
    difference = sp.simplify(target_a - target_b)
    checks["universal_subtraction_witness"] = (
        difference[0, 1] == rho_b - rho_a
        and difference.subs(rho_b, rho_a) == sp.zeros(2)
    )
    checks["one_fixed_extension_fails_on_physical_domain"] = (
        len(set(source_rhos)) > 1
        and theorem.get("universal_status")
        == "NO_SINGLE_RHO_INDEPENDENT_COEFFICIENT_TRIPLE_MATCHES_DISTINCT_PHYSICAL_RHOS"
    )
    checks["pointwise_fit_not_promoted_to_dynamics"] = (
        theorem.get("pointwise_status")
        == "UNIQUE_ALGEBRAIC_MATCH_EXISTS_FOR_EACH_FIXED_RHO"
        and cert.get("disposition", {}).get("pointwise_endpoint_match")
        == "EXISTS_UNIQUELY_BUT_IS_NOT_DERIVED_FROM_BT_DYNAMICS"
        and cert.get("disposition", {}).get("BT_derived_missing_complement")
        == "NOT_CONSTRUCTED"
    )

    disposition = cert.get("disposition", {})
    checks["eq19_boundary_is_fail_closed"] = (
        disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and eq19["disposition"]["finite_mode_order_lambda_Eq19"]
        == "PROVED_WITH_Q1_ZERO"
        and zero_mode["disposition"]["Eq19_order_lambda_pushforward"]
        == "NOT_REPRODUCED_FROM_PUBLIC_DATA"
    )
    checks["physical_boundary_is_fail_closed"] = (
        disposition.get("complete_BT_probability") == "NOT_CONSTRUCTED"
        and disposition.get("physical_two_sided_S_operator") == "NOT_CONSTRUCTED"
        and moller["disposition"]["public_Rt_equals_physical_splitting"]
        == "EXACTLY_FALSE"
    )
    boundaries = cert.get("does_not_establish", [])
    checks["scope_boundary_is_explicit"] = (
        len(boundaries) == 10
        and any("spectator-dependent" in item for item in boundaries)
        and any("LORENTZIAN-CAUSAL" in item for item in boundaries)
        and any("new physical or spacetime dimension" in item for item in boundaries)
    )

    failures = [name for name, ok in checks.items() if not bool(ok)]
    print("checks %d/%d" % (len(checks) - len(failures), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

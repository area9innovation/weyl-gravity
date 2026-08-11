#!/usr/bin/env python3
"""Independent verifier for the finite physical BT Moller column."""
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
    "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-physical-moller-column-v1.schema.json",
)
EXPECTED_INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-finite-physical-moller-column.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
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


def parse_matrix(rows, locals_):
    import sympy as sp

    return sp.Matrix(
        [[sp.sympify(value, locals=locals_) for value in row] for row in rows]
    )


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

    checks["identity_and_boundary_tags"] = (
        cert.get("certificate")
        == "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1"
        and cert.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and cert.get("lifecycle_state") == "CLASSIFIED"
    )
    provenance = cert.get("provenance", {})
    records = provenance.get("inputs", [])
    checks["exact_input_inventory"] = [row.get("path") for row in records] == EXPECTED_INPUTS
    checks["all_input_hashes_reproduced"] = len(records) == len(EXPECTED_INPUTS) and all(
        row.get("sha256") == sha256(os.path.join(ROOT, row.get("path", "")))
        for row in records
    )

    hp = load(os.path.join(ROOT, EXPECTED_INPUTS[1]))
    continuum = load(os.path.join(ROOT, EXPECTED_INPUTS[2]))
    physical = load(os.path.join(ROOT, EXPECTED_INPUTS[3]))
    ledger = load(os.path.join(ROOT, EXPECTED_INPUTS[4]))
    eq19 = load(os.path.join(ROOT, EXPECTED_INPUTS[5]))
    checks["all_predecessor_rails_green"] = all(
        value["checks"]["ok"] for value in (hp, continuum, physical, ledger, eq19)
    )

    column = cert.get("physical_vacuum_moller_column", {})
    counts = column.get("history_counts")
    edge_counts = column.get("edge_counts")
    rates = [frac(value) for value in column.get("conditional_rates", [])]
    expected_rates = [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)]
    checks["carrier_partition_reconstructed"] = (
        counts == [1, 3, 12, 60]
        and edge_counts == [3, 12, 60]
        and column.get("physical_edge_marks") == list(range(75))
        and continuum["seventy_five_mark_completion"]
        ["physically_intertwined_edge_marks"] == list(range(75))
    )
    checks["conditional_rates_reconstructed"] = rates == expected_rates
    exit_rates = [
        Fraction(3) * rates[0],
        Fraction(4) * rates[1],
        Fraction(5) * rates[2],
        Fraction(0),
    ]
    drifts = [value / 2 for value in exit_rates]
    checks["drift_reconstructed_from_child_counts"] = (
        column.get("amplitude_drifts") == [str(value) for value in drifts]
        and hp["hudson_parthasarathy_cocycle"]
        ["drift_eigenvalues_by_level"] == [str(value) for value in drifts]
    )

    a, s = sp.symbols("a s", nonnegative=True)
    probabilities = sp.Matrix(
        [
            sp.sympify(value, locals={"a": a, "exp": sp.exp})
            for value in column.get("sector_probabilities", [])
        ]
    )
    generator = sp.Matrix(
        [
            [-sp.Rational(exit_rates[0].numerator, exit_rates[0].denominator), 0, 0, 0],
            [sp.Rational(exit_rates[0].numerator, exit_rates[0].denominator), -sp.Rational(exit_rates[1].numerator, exit_rates[1].denominator), 0, 0],
            [0, sp.Rational(exit_rates[1].numerator, exit_rates[1].denominator), -sp.Rational(exit_rates[2].numerator, exit_rates[2].denominator), 0],
            [0, 0, sp.Rational(exit_rates[2].numerator, exit_rates[2].denominator), 0],
        ]
    )
    checks["markov_generator_is_positive_conservative"] = (
        all(generator[i, j] >= 0 for i in range(4) for j in range(4) if i != j)
        and all(sum(generator[i, j] for i in range(4)) == 0 for j in range(4))
    )
    checks["serialized_probabilities_solve_forward_equation"] = (
        sp.simplify(sp.diff(probabilities, a) - generator * probabilities)
        == sp.zeros(4, 1)
        and probabilities.subs(a, 0) == sp.Matrix([1, 0, 0, 0])
    )
    checks["serialized_probabilities_normalize"] = sp.simplify(sum(probabilities) - 1) == 0

    # Method-distinct reconstruction: solve in Laplace space rather than
    # integrating the producer's ordered simplex kernels.
    resolvent = sp.simplify((s * sp.eye(4) - generator).inv() * sp.Matrix([1, 0, 0, 0]))
    hp_laplace = sp.Matrix(
        [
            sp.sympify(row["aggregate_transform"], locals={"s": s})
            for row in hp["vacuum_reduction"]["population_laplace_rows"]
        ]
    )
    checks["laplace_resolvent_matches_independent_hp_rows"] = sp.simplify(
        resolvent - hp_laplace
    ) == sp.zeros(4, 1)
    leading = [
        sp.expand(probabilities[k].series(a, 0, 5).removeO()).coeff(a, k)
        for k in range(4)
    ]
    checks["leading_tree_coefficients"] = leading == [
        1,
        sp.Rational(1, 16),
        sp.Rational(5, 512),
        sp.Rational(9, 8192),
    ]
    checks["composition_isometry_is_well_typed"] = (
        column.get("definition") == "M_a=A_<=3 U_a I_Omega"
        and continuum["seventy_five_mark_completion"]["direct_sum"].startswith("A_<=3=")
        and hp["hudson_parthasarathy_cocycle"]["solution"].startswith("UNIQUE_BOUNDED")
        and column.get("status")
        == "EXACT_PHYSICAL_CONTINUUM_VACUUM_COLUMN_ON_THE_AVAILABLE_FINITE_HIERARCHY"
    )

    response = cert.get("finite_model_inclusive_response", {})
    hard = frac(response.get("hard_absolute_response", {"numerator": 9, "denominator": 1}))
    real = frac(response.get("real_absolute_response", {"numerator": 9, "denominator": 1}))
    checks["finite_model_hard_real_pair"] = (
        frac(response["Born_coefficient"]) == Fraction(3, 32)
        and frac(response["hard_normalized_linear_response"]) == Fraction(-1, 16)
        and frac(response["real_normalized_linear_response"]) == Fraction(1, 16)
        and hard == Fraction(-3, 512)
        and real == Fraction(3, 512)
        and hard + real == 0
        and frac(response["inclusive_absolute_response"]) == 0
    )
    checks["public_rt_excluded_from_scattering_ledger"] = (
        ledger["combined_ledger"]["typing_rule"]
        == "THE_RT_PUSHFORWARD_RESPONSE_IS_NOT_ADDED_TO_THE_PHYSICAL_SMATRIX_LEDGER"
        and "not added" in response.get("typing", "")
    )

    bridge = cert.get("minimal_public_Rt_compression", {})
    rho, L, Q = sp.symbols("rho L Q", nonzero=True, real=True)
    local = {"rho": rho, "L": L, "Q": Q}
    J = parse_matrix(bridge.get("domain_metric_J", []), local)
    D = parse_matrix(bridge.get("public_leg_D", []), local)
    T = parse_matrix(bridge.get("physical_leg_T", []), local)
    C = parse_matrix(bridge.get("missing_leg_C", []), local)
    F = parse_matrix(bridge.get("common_leg_F", []), local)
    W = parse_matrix(bridge.get("bridge_W", []), local)
    eta = sp.diag(J, J)
    G_D = sp.simplify(D.T * J * D)
    N_D = sp.simplify(J * G_D)
    G_C = sp.simplify(C.T * J * C)
    N_C = sp.simplify(J * G_C)
    checks["public_rank_jordan_reconstructed"] = (
        G_D == sp.diag(0, 2)
        and N_D == sp.Matrix([[0, 2], [0, 0]])
        and N_D.rank() == 1
        and N_D**2 == sp.zeros(2)
    )
    checks["missing_pullback_is_forced"] = G_C == -rho * J - G_D
    checks["missing_inertia_and_trace"] = (
        sp.factor(G_C.det()) == -rho**2
        and sp.trace(G_C) == -2
        and sp.trace(N_C) == -2 * rho
    )
    checks["common_pullback_matches_physical"] = sp.simplify(
        (F.T * eta * F - T.T * J * T).subs(rho, -4 * L * Q)
    ) == sp.zeros(2)
    checks["commuting_compression_square"] = (
        sp.simplify(W * T - F) == sp.zeros(4, 2)
        and F[:2, :] == D
    )
    checks["bridge_krein_isometry"] = sp.simplify(
        (W.T * eta * W).subs(rho, -4 * L * Q) - J
    ) == sp.zeros(2)
    checks["two_dimensions_are_minimal"] = (
        C.rank() == 2 and G_C.rank() == 2 and sp.factor(G_C.det()) == -rho**2
    )
    checks["positive_and_null_only_complements_excluded"] = (
        sp.factor(G_C.det()) == -rho**2
        and sp.trace(N_C) == -2 * rho
        and "no positive-Hilbert" in bridge.get("positive_auxiliary_obstruction", "")
        and "trace-null" in bridge.get("null_remainder_obstruction", "")
    )

    # Recheck the bridge at every exact physical fixture without relying on
    # the producer's symbolic substitution.
    fixture_checks = []
    for row in physical["amplitude_factorization"]["exact_fixtures"]:
        rho_i = sp.Rational(row["rho"]["numerator"], row["rho"]["denominator"])
        L2 = sp.Rational(row["twice_L"]["numerator"], row["twice_L"]["denominator"])
        Q2 = sp.Rational(row["twice_Q"]["numerator"], row["twice_Q"]["denominator"])
        T_i = sp.diag(Q2, L2)
        C_i = C.subs(rho, rho_i)
        F_i = D.col_join(C_i)
        W_i = F_i * T_i.inv()
        fixture_checks.append(
            -4 * (L2 / 2) * (Q2 / 2) == rho_i
            and T_i.T * J * T_i == -rho_i * J
            and F_i.T * eta * F_i == -rho_i * J
            and sp.simplify(W_i.T * eta * W_i - J) == sp.zeros(2)
        )
    checks["three_exact_physical_bridge_fixtures"] = all(fixture_checks)

    typed = cert.get("typed_Eq19_boundary", {})
    disposition = cert.get("disposition", {})
    checks["eq19_boundary_is_fail_closed"] = (
        typed.get("Eq19_all_orders") == "NOT_PROVED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and eq19["disposition"]["finite_mode_order_lambda_Eq19"]
        == "PROVED_WITH_Q1_ZERO"
        and "algebraic existence does not prove" in typed.get("missing_dynamical_statement", "")
    )
    checks["physical_scope_is_fail_closed"] = (
        disposition.get("full_two_sided_physical_S_operator") == "NOT_CONSTRUCTED"
        and disposition.get("fourth_jump") == "NOT_COMPUTED"
        and disposition.get("complete_BT_probability") == "NOT_CONSTRUCTED"
        and disposition.get("spacetime_Moller_LSZ_S_operator") == "NOT_CONSTRUCTED"
        and len(cert.get("does_not_establish", [])) == 13
    )
    checks["no_new_dimension_or_lorentzian_promotion"] = (
        any("new physical or spacetime dimension" in item for item in cert.get("does_not_establish", []))
        and any("LORENTZIAN-CAUSAL" in item for item in cert.get("does_not_establish", []))
    )

    failures = [name for name, ok in checks.items() if not bool(ok)]
    print("checks %d/%d" % (len(checks) - len(failures), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

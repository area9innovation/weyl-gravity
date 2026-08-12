#!/usr/bin/env python3
"""Independent verifier for the finite-hierarchy crossed pre-trace no-go."""
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
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_NONFACTORIZING_PRETRACE_NO_GO_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-six-point-nonfactorizing-pretrace-no-go-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}

    sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
    from bt_six_point_strongly_ordered_tree import HARD_FIXTURES
    from verify_bt_six_point_strongly_ordered_tree import exact_tree_kernel

    inputs = certificate["provenance"]["inputs"]
    predecessors = [load(os.path.join(ROOT, row["path"])) for row in inputs[1:]]
    finite = certificate["finite_pretrace_rows"]
    factorization = certificate["exact_factorization"]
    crossing = certificate["finite_hierarchy_crossing"]
    disposition = certificate["physical_disposition"]

    a0, a1, a2, e, tau1, tau2 = sp.symbols(
        "a0 a1 a2 e tau1 tau2", positive=True
    )
    x, r = sp.symbols("x r", positive=True)
    z = sp.symbols("z")
    local = {
        symbol.name: symbol
        for symbol in (a0, a1, a2, e, tau1, tau2, x, r, z)
    }

    def expression(value):
        return sp.sympify(value, locals=local)

    def matrix(value):
        return sp.Matrix([[expression(entry) for entry in row] for row in value])

    recorded = finite["three_hard_fixture_rows"]
    common = recorded[0]["leading_components"]
    component_expr = {int(mask): expression(value) for mask, value in common.items()}

    # Method-distinct explicit enumeration of all 220 rooted trees at finite e.
    points = [
        (1, 4, 3, Fraction(1, 5), 10, 17),
        (2, 7, 5, Fraction(2, 7), 13, 23),
    ]
    explicit_ok = True
    counts = set()
    for point, hard in zip(points, HARD_FIXTURES[:2]):
        order, count, _, leading = exact_tree_kernel(point, hard, return_leading=True)
        counts.add(count)
        substitutions = dict(zip((a0, a1, a2, e, tau1, tau2), point))
        expected = {
            mask: Fraction(
                int(sp.numer(sp.cancel(expr.subs(substitutions)))),
                int(sp.denom(sp.cancel(expr.subs(substitutions)))),
            )
            for mask, expr in component_expr.items()
        }
        explicit_ok &= (
            order == 2
            and leading.coefficients == expected
        )

    L0 = -a2**2/(4*tau2)
    Q0 = a2*(2*tau2-a2)/(4*tau2**2)
    L1 = a2/(2*tau2)
    Q1 = (tau2+a2)/(2*tau2**2)
    M = sp.Matrix([[L0, L1], [Q0, Q1]])
    u = expression(factorization["u_e"])
    v = expression(factorization["v_e"])
    singleton = expression(finite["singleton_row"])
    pair = expression(finite["pair_row"])
    residual = sp.simplify(sp.Matrix([singleton, pair])-M*sp.Matrix([u, v]))

    uc = expression(crossing["u_cross"])
    vc = expression(crossing["v_cross"])
    Nu = expression(crossing["minus_six_a2_squared_x_squared_u_cross"])
    Nv = expression(crossing["six_a2_x_v_cross"])
    expected_Nu = sp.factor(
        3*a2**2*((r-1)**2+2*x*(r+1))
        + 2*e**2*x**2*(r**2+r+1)
    )
    expected_Nv = sp.factor(
        3*a2**2*x
        + 3*a2*e*((r-1)**2+x*(r+1))
        + 2*e**2*x*(r**2+r+1)
    )
    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3*J
    eta = sp.kronecker_product(J, K)
    R = sp.Matrix.hstack(sp.eye(2), sp.eye(2))
    D = sp.diag(uc, uc, vc, vc)
    A = sp.simplify(eta.inv()*D.T*R.T*K*R*D)
    characteristic = sp.factor(A.charpoly(z).as_expr())
    fixed = sp.simplify(6*uc*vc*sp.eye(2))

    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_pass": all(value["checks"]["ok"] for value in predecessors),
        "three_recorded_fixture_rows_identical": len(
            {json.dumps(row["leading_components"], sort_keys=True) for row in recorded}
        ) == 1,
        "independent_explicit_220_tree_finite_fixtures": explicit_ok
        and counts == {220},
        "singleton_rows_equal_pretrace": all(
            sp.simplify(component_expr[mask]-singleton) == 0
            for mask in (1, 2, 4)
        ),
        "pair_rows_equal_pretrace": all(
            sp.simplify(component_expr[mask]-pair) == 0
            for mask in (3, 5, 6)
        ),
        "cubic_spectator_mask_absent": 7 not in component_expr
        and finite["cubic_row"] == "0",
        "outer_profile_matrix_reconstructs": sp.simplify(
            matrix(factorization["outer_profile_matrix"])-M
        ) == sp.zeros(2),
        "outer_profile_matrix_invertible": sp.factor(M.det())
        == -3*a2**2/(8*tau2**2),
        "factorization_residual_is_zero": residual == sp.zeros(2, 1)
        and factorization["nonfactorizing_residual"] == ["0", "0"],
        "u_cross_numerator_positive_polynomial": sp.simplify(Nu-expected_Nu)
        == 0 and sp.simplify(Nu+6*a2**2*x**2*uc) == 0,
        "v_cross_numerator_positive_polynomial": sp.simplify(Nv-expected_Nv)
        == 0 and sp.simplify(Nv-6*a2*x*vc) == 0,
        "crossing_metric_reconstructs": matrix(crossing["metric_eta"]) == eta,
        "crossing_collapse_reconstructs": matrix(
            crossing["coherent_collapse_R_plus"]
        ) == R,
        "crossed_D_reconstructs": sp.simplify(matrix(crossing["crossed_D"])-D)
        == sp.zeros(4),
        "crossed_raised_pullback_reconstructs": sp.simplify(
            matrix(crossing["raised_pullback"])-A
        ) == sp.zeros(4),
        "negative_rank_two_characteristic_reconstructs": (
            crossing["rank"] == 2
            and sp.simplify(
                expression(crossing["characteristic_polynomial"])-characteristic
            ) == 0
            and sp.simplify(characteristic-z**2*(z-2*uc*vc)**2) == 0
        ),
        "fixed_hilbertized_gram_reconstructs": sp.simplify(
            matrix(crossing["fixed_hilbertized_gram"])-fixed
        ) == sp.zeros(2),
        "sign_domain_is_fail_closed": (
            crossing["u_sign"] == "STRICTLY_NEGATIVE"
            and crossing["v_sign"] == "STRICTLY_POSITIVE"
            and "a2>0" in crossing["domain"]
            and "e>0" in crossing["domain"]
        ),
        "correlated_cylinder_obstruction_recorded": (
            disposition["finite_hierarchy_nonfactorizing_pretrace_residue"]
            == "EXACTLY_ZERO_ON_CORRELATED_SQUARE_FREE_CYLINDER"
            and disposition["first_twelve_reversed_histories_on_available_cylinder"]
            == "NO_POSITIVE_FIXED_SHARP_INTERTWINER"
        ),
        "full_phase_space_and_doubled_routes_remain_open": (
            disposition["complete_noncorrelated_crossed_three_to_three_phase_space"]
            == "NOT_COMPUTED"
            and disposition["doubled_or_off_diagonal_source"] == "NOT_DERIVED"
        ),
        "claim_boundary_remains_fail_closed": (
            disposition["complete_crossed_probability"] == "NOT_COMPUTED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
            and disposition["spacetime_Moller_LSZ_S_operator"]
            == "NOT_CONSTRUCTED"
        ),
        "next_gate_requires_genuine_enlargement": (
            "minimal doubled cross-paired source" in certificate["next_gate"]
            and "complete non-correlated crossed 3-to-3" in certificate["next_gate"]
            and "another same-carrier parity" in certificate["next_gate"]
        ),
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

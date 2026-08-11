#!/usr/bin/env python3
"""Independent verifier for the BT eight-point outer-threshold profile."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator

import verify_bt_eight_point_fourth_moment as finite_rail


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_OUTER_THRESHOLD_PROFILE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-outer-threshold-profile-v1.schema.json",
)
PREDECESSOR = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_HARD_PROFILE_OBSTRUCTION_V1.json",
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


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def exact_J_coefficients():
    """Derive the J1..J4 r-log-r coefficients by pole derivatives."""
    import sympy as sp

    z, m = sp.symbols("z m", positive=True)
    u = 1 + m**2 + m * (z + 1 / z)
    measure = m**2 * (1 - z**2) ** 2 / z**3

    def pole_residue(expression, point, order):
        if order <= 0:
            return sp.S.Zero
        regular = sp.cancel((z - point) ** order * expression)
        return sp.factor(
            sp.limit(
                sp.diff(regular, z, order - 1) / sp.factorial(order - 1),
                z,
                point,
            )
        )

    coefficients = []
    for power in range(1, 5):
        integrand = sp.cancel(measure / u**power)
        residue_zero = pole_residue(integrand, 0, max(3 - power, 0))
        residue_minus_m = pole_residue(integrand, -m, power)
        log_m = sp.series(
            -(residue_zero + residue_minus_m), m, 0, 3
        ).removeO().expand()
        coefficients.append(sp.factor(log_m.coeff(m, 2) / 2))
    return coefficients


def verify(certificate):
    import sympy as sp

    schema_errors = list(
        Draft202012Validator(load(SCHEMA)).iter_errors(certificate)
    )
    if schema_errors:
        return {"schema_validation": False}
    analysis = certificate["hard_profile_analysis"]
    rows = analysis["rows"]
    u, e3 = sp.symbols("tau4 e3")
    profiles = [sp.sympify(row["outer_profile"]) for row in rows]
    leading = [sp.factor(sp.cancel(e3 * row).subs(e3, 0)) for row in profiles]
    threshold_functions = [sp.factor(row.subs(u, 1)) for row in profiles]
    threshold_poles = [
        sp.factor(sp.cancel(e3 * row).subs(e3, 0))
        for row in threshold_functions
    ]
    difference = sp.factor(leading[0] - leading[1])
    pole_difference = sp.factor(threshold_poles[0] - threshold_poles[1])
    inputs = certificate["provenance"]["inputs"]
    predecessor = load(PREDECESSOR)

    soft = analysis["soft_fixture"]
    hard = analysis["hard_fixtures"]
    eps = [Fraction(1, 5), Fraction(2, 7), Fraction(3, 11)]
    finite_rows = [finite_rail.finite_tree_kernel(soft, item, eps) for item in hard]
    predecessor_values = [
        Fraction(row["finite_projected_value"])
        for row in predecessor["correlated_boundary"]["rows"]
    ]

    checks = {
        "schema_validation": not schema_errors,
        "outer_profile_hashes": all(
            text_sha256(row["outer_profile"]) == row["outer_profile_sha256"]
            and len(row["outer_profile"]) == row["outer_profile_length"]
            for row in rows
        ),
        "leading_profile_reconstruction": all(
            sp.cancel(actual - sp.sympify(row["leading_e3_profile"])) == 0
            and text_sha256(row["leading_e3_profile"])
            == row["leading_e3_profile_sha256"]
            for actual, row in zip(leading, rows)
        ),
        "independent_J1_through_J4_coefficients": exact_J_coefficients()
        == [1, 1, 1, 1],
        "threshold_function_is_coefficient_sum": all(
            sp.cancel(actual - sp.sympify(row["threshold_coefficient_function"]))
            == 0
            and text_sha256(row["threshold_coefficient_function"])
            == row["threshold_coefficient_function_sha256"]
            for actual, row in zip(threshold_functions, rows)
        ),
        "pure_J2_difference": sp.cancel(
            difference - sp.Rational(771, 1568) / u
        )
        == 0,
        "fixed_u_three_replay": difference.subs(u, 3)
        == sp.Rational(257, 1568),
        "outer_threshold_pole_difference": pole_difference
        == sp.Rational(771, 1568)
        == sp.Rational(
            frac(analysis["threshold_e3_pole_difference"]).numerator,
            frac(analysis["threshold_e3_pole_difference"]).denominator,
        ),
        "physical_log_difference": 5 * pole_difference
        == sp.Rational(3855, 1568),
        "method_distinct_complete_finite_tree_replay": [row[2] for row in finite_rows]
        == predecessor_values,
        "input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "fourth_moment_and_Eq19_stay_open": (
            certificate["disposition"]["threshold_integrated_fourth_moment"]
            == "NOT_COMPUTED"
            and certificate["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
        ),
    }
    return checks


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

#!/usr/bin/env python3
"""Independent verifier for the BT one-site uniform Poincare theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from math import comb

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_UNIFORM_POINCARE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-single-site-uniform-poincare-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate(coefficients: list[int], value: Fraction) -> Fraction:
    result = Fraction()
    for coefficient in reversed(coefficients):
        result = result * value + coefficient
    return result


def right_closed_numerator(t_value: Fraction) -> Fraction:
    d_value = t_value**2 + t_value + 1
    return 16 * d_value**3 - t_value * (
        4 * (t_value + 1) ** 2 + d_value
    ) ** 2


def left_closed_numerator(w_value: Fraction) -> Fraction:
    d_value = w_value**4 + w_value**2 + 1
    inner = 2 * (w_value + 1) * (w_value**2 + 1) ** 2 + w_value**2 * d_value
    return 4 * d_value**3 * (w_value + 1) ** 2 - w_value**2 * inner**2


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hash_current"] = len(inputs) == 1 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )
    scalar = certificate["exact_scalar_inequalities"]
    right = scalar["right_square_polynomial_power_coefficients"]
    left = scalar["left_square_polynomial_power_coefficients"]
    checks["right_polynomial_independent_evaluation"] = len(right) == 7 and all(
        evaluate(right, value) == right_closed_numerator(value)
        for value in [Fraction(index, 3) for index in range(1, 9)]
    )
    checks["left_polynomial_independent_evaluation"] = len(left) == 15 and all(
        evaluate(left, value) == left_closed_numerator(value)
        for value in [Fraction(index, 4) for index in range(1, 17)]
    )
    right_shifted = scalar["right_square_polynomial_after_t_equals_1_plus_y"]
    left_shifted = scalar["left_square_polynomial_after_w_equals_1_plus_y"]
    reconstructed_right_shift = [
        sum(right[power] * comb(power, order) for power in range(order, len(right)))
        for order in range(len(right))
    ]
    reconstructed_left_shift = [
        sum(left[power] * comb(power, order) for power in range(order, len(left)))
        for order in range(len(left))
    ]
    checks["shifted_positive_polynomials"] = (
        right_shifted == reconstructed_right_shift
        and left_shifted == reconstructed_left_shift
        and all(value > 0 for value in right_shifted + left_shifted)
    )
    fixtures = scalar["exact_fixtures"]
    u_value = Fraction(4)
    v_value = Fraction(32)

    def derivative(t_value: Fraction) -> Fraction:
        return (
            u_value**2 * (t_value - t_value**-2)
            + 8 * u_value * (t_value**-1 - t_value)
            + v_value * (t_value**2 - t_value)
        )

    checks["radial_fixtures"] = (
        u_value**2 * v_value == 8**3
        and derivative(Fraction(2)) == decode(fixtures["right_t_2_derivative"])
        and derivative(Fraction(1, 2))
        == decode(fixtures["left_t_1_over_2_derivative"])
        and derivative(Fraction(2)) > 0
        and derivative(Fraction(1, 2)) < 0
    )
    transfer = certificate["hardy_muckenhoupt_transfer"]
    checks["hardy_constants"] = (
        transfer["radial_rate"] == "rho=8/lambda^2"
        and transfer["muckenhoupt_products"]
        == "B_+<=1/rho=lambda^2/8 and B_-<=lambda^2/8"
        and transfer["log_coordinate_poincare"] == "C_P,psi<=lambda^2/2"
        and transfer["phi_coordinate_poincare"]
        == "C_P,phi<=1/2 because psi=lambda*phi"
        and transfer["conditional_variance"]
        == "Var_mu(f|eta in h_o^perp)<=1/2*E_mu[(D_h_o f)^2|eta in h_o^perp]"
        and "h_o=delta_o-N^-1*1"
        in certificate["centered_fiber"]["mean_zero_coordinate"]
    )
    disposition = certificate["method_disposition"]
    checks["claim_boundary"] = (
        disposition["uniform_one_site_poincare"]
        == "PROVED_WITH_CONSTANT_ONE_HALF"
        and disposition["uniform_one_site_log_sobolev"] == "OPEN"
        and disposition["uniform_inter_site_influence"] == "OPEN"
        and disposition["volume_uniform_global_poincare"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["required_nonclaims"] = {
        "a uniform one-site logarithmic-Sobolev inequality",
        "a global finite-volume or volume-uniform Poincare/Witten estimate",
        "the normalized lowest-mode or interacting Gibbs H^-1 bound",
        "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
        and all(certificate["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())

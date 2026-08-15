#!/usr/bin/env python3
"""Independent verifier for the BT signed-response axial gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SIGNED_RESPONSE_AXIAL_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-signed-response-axial-gate-v1.schema.json",
)
Bivariate = dict[tuple[int, int], Fraction]


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def badd(left: Bivariate, right: Bivariate) -> Bivariate:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, Fraction()) + coefficient
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def bscale(poly: Bivariate, scalar: Fraction | int) -> Bivariate:
    scalar = Fraction(scalar)
    return {monomial: scalar * coefficient for monomial, coefficient in poly.items() if scalar * coefficient}


def bmul(left: Bivariate, right: Bivariate, order: int = 4) -> Bivariate:
    result: Bivariate = {}
    for (left_lambda, left_x), left_coefficient in left.items():
        for (right_lambda, right_x), right_coefficient in right.items():
            lambda_degree = left_lambda + right_lambda
            if lambda_degree > order:
                continue
            monomial = (lambda_degree, left_x + right_x)
            result[monomial] = result.get(monomial, Fraction()) + left_coefficient * right_coefficient
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def gaussian_moment(degree: int) -> Fraction:
    if degree % 2:
        return Fraction()
    result = Fraction(1, 72 ** (degree // 2))
    for odd in range(1, degree, 2):
        result *= odd
    return result


def integrate(poly: Bivariate, order: int = 4) -> list[Fraction]:
    result = [Fraction() for _ in range(order + 1)]
    for (lambda_degree, x_degree), coefficient in poly.items():
        result[lambda_degree] += coefficient * gaussian_moment(x_degree)
    return result


def divide(numerator: list[Fraction], denominator: list[Fraction]) -> list[Fraction]:
    quotient = [Fraction() for _ in numerator]
    for degree in range(len(numerator)):
        quotient[degree] = (
            numerator[degree]
            - sum(
                (quotient[power] * denominator[degree - power] for power in range(degree)),
                Fraction(),
            )
        ) / denominator[0]
    return quotient


def independent_expansion(order: int = 4) -> dict[str, list[Fraction]]:
    # Build U=F(lambda*x)/lambda^2-36*x^2 directly from the two
    # exponentials, then exponentiate by its ordinary power series.  This is
    # intentionally distinct from the producer's differential recurrence.
    perturbation: Bivariate = {}
    for degree in range(3, order + 3):
        coefficient = Fraction(
            (64 * (-1) ** degree + 8) * (2**degree - 2),
            2 * math.factorial(degree),
        )
        perturbation[(degree - 2, degree)] = coefficient
    weight: Bivariate = {(0, 0): Fraction(1)}
    power: Bivariate = {(0, 0): Fraction(1)}
    for exponent in range(1, order + 1):
        power = bmul(power, perturbation, order)
        weight = badd(weight, bscale(power, Fraction((-1) ** exponent, math.factorial(exponent))))

    z: Bivariate = {(1, 1): Fraction(1)}
    exp_z: Bivariate = {
        (degree, degree): Fraction(1, math.factorial(degree))
        for degree in range(order + 1)
    }
    z_exp_z: Bivariate = {
        (degree, degree): Fraction(1, math.factorial(degree - 1))
        for degree in range(1, order + 1)
    }
    normalizer = integrate(weight, order)

    def mean(observable: Bivariate) -> list[Fraction]:
        return divide(integrate(bmul(observable, weight, order), order), normalizer)

    mean_z = mean(z)
    mean_exp_z = mean(exp_z)
    mean_z_exp_z = mean(z_exp_z)
    covariance = []
    for degree in range(order + 1):
        product = sum(
            (mean_z[power] * mean_exp_z[degree - power] for power in range(degree + 1)),
            Fraction(),
        )
        covariance.append(mean_z_exp_z[degree] - product)
    return {
        "normalizer": normalizer,
        "mean_z": mean_z,
        "mean_exp_z": mean_exp_z,
        "mean_z_exp_z": mean_z_exp_z,
        "covariance": covariance,
    }


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

    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(certificate))
    inputs = certificate["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 2 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )
    exact = certificate["exact_weak_coupling_expansion"]
    rebuilt = independent_expansion()
    fields = {
        "normalizer_coefficients_lambda0_to_lambda4": "normalizer",
        "mean_z_coefficients_lambda0_to_lambda4": "mean_z",
        "mean_exp_z_coefficients_lambda0_to_lambda4": "mean_exp_z",
        "mean_z_exp_z_coefficients_lambda0_to_lambda4": "mean_z_exp_z",
        "covariance_coefficients_lambda0_to_lambda4": "covariance",
    }
    checks["independent_formal_integrals"] = all(
        [decode(value) for value in exact[certificate_field]] == rebuilt[rebuilt_field]
        for certificate_field, rebuilt_field in fields.items()
    )
    checks["independent_vacuum_coefficient"] = (
        rebuilt["covariance"][2] == Fraction(1, 72)
        and rebuilt["covariance"][4] == Fraction(43, 46656)
        and decode(exact["beta_lambda2_coefficient"]) == Fraction(-43, 5184)
        and decode(exact["axial_lambda2_correction"]) == Fraction(-43, 46656)
        and decode(exact["mixed_lambda2_correction"]) == Fraction(-43, 23328)
    )
    response = certificate["conditional_response"]
    checks["distance_two_path_signs"] = (
        "<0" in response["axial_distance_two"]
        and "negative sum of the two positive path products" in response["mixed_distance_two"]
        and "Cov_q(z,exp(z))>0" in response["strict_covariance_sign"]
    )
    symbol = certificate["annealed_axial_symbol"]
    checks["symbol_reduction"] = (
        symbol["row_sum"] == "8*n_L+8*a_L+24*m_L=1"
        and symbol["relaxation_symbol"]
        == "Rhat_L(p*e_1)=beta_L*omega(p)-a_L*omega(p)^2"
        and symbol["beta"] == "beta_L=n_L+4*a_L+6*m_L=1/8+3*(a_L+m_L)"
        and symbol["unresolved_scalar"]
        == "the sign and volume scaling of beta_L under the actual full Gibbs measure"
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["pointwise_signed_conditional_response_contraction"]
        == "OBSTRUCTED_AT_WEAK_COUPLING_AND_LARGE_VOLUME"
        and disposition["annealed_beta_nonnegative_or_lower_bound"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "a negative annealed beta_L or instability of the heat-bath Markov process",
        "failure of every signed, block, or multiscale response method",
        "the normalized lowest-mode or interacting Gibbs H^-1 bound or its failure",
        "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
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

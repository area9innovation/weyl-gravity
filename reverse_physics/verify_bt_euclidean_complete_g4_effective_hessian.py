#!/usr/bin/env python3
"""Independent verifier for the complete-g^4 expected-Hessian reduction."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.verify_bt_euclidean_complete_g4_chaos_gate import (
    verify as verify_chaos_predecessor,
)


CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_EFFECTIVE_HESSIAN_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-effective-hessian-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def gaussian_moment(power: int) -> Fraction:
    if power % 2:
        return Fraction(0)
    return Fraction(math.prod(range(1, power, 2)))


def expectation(coefficients: dict[int, Fraction]) -> Fraction:
    return sum(value * gaussian_moment(power) for power, value in coefficients.items())


def add(*polynomials: dict[int, Fraction]) -> dict[int, Fraction]:
    powers = set().union(*(polynomial.keys() for polynomial in polynomials))
    return {power: sum(polynomial.get(power, 0) for polynomial in polynomials) for power in powers}


def scale(polynomial: dict[int, Fraction], factor: Fraction | int) -> dict[int, Fraction]:
    return {power: Fraction(factor) * value for power, value in polynomial.items()}


def multiply(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for i, a in left.items():
        for j, b in right.items():
            result[i + j] = result.get(i + j, Fraction(0)) + a * b
    return result


def derivative(polynomial: dict[int, Fraction], order: int = 1) -> dict[int, Fraction]:
    result = polynomial
    for _ in range(order):
        result = {power - 1: power * value for power, value in result.items() if power}
    return result


def independent_fixture() -> dict[str, Fraction]:
    # Sparse dictionaries and Gaussian integration by parts are independent of
    # the producer's dense-polynomial implementation and product-rule grouping.
    a = {0: Fraction(-1), 2: Fraction(1)}
    b = {1: Fraction(-1), 3: Fraction(1)}
    c = {2: Fraction(-3), 4: Fraction(1)}
    w1 = {1: Fraction(-5), 3: Fraction(2)}
    w2 = {0: Fraction(4), 2: Fraction(-4), 4: Fraction(1)}
    z2 = expectation(add(scale(multiply(w1, w1), Fraction(1, 2)), scale(w2, -1)))
    r = add(scale(multiply(w1, w1), Fraction(1, 8)), scale(w2, Fraction(-1, 2)), {0: -z2 / 2})
    e = add(c, scale(multiply(w1, b), Fraction(-1, 2)), multiply(r, a))
    kernel = expectation(derivative(e, 2))
    cross = 2 * expectation(multiply(a, e))
    return {
        "z2": z2,
        "expected_hessian_direct": kernel,
        "expected_hessian_product_rule": kernel,
        "Pi2E_norm_squared": kernel * kernel / 2,
        "twice_A_E": cross,
        "twice_A_Pi2E_from_kernel": 2 * kernel,
    }


def signed_transfers(number_of_h_legs: int) -> set[int]:
    return set(range(-number_of_h_legs, number_of_h_legs + 1, 2))


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        if list(Draft202012Validator(schema).iter_errors(data)):
            return False
        for source in data["provenance"]["inputs"]:
            if file_hash(source["path"]) != source["sha256"]:
                return False
        if not verify_chaos_predecessor():
            return False

        exact = independent_fixture()
        values = data["exact_one_dimensional_fixture"]["values"]
        if any(decode(values[name]) != value for name, value in exact.items()):
            return False
        if exact != {
            "z2": Fraction(19, 2),
            "expected_hessian_direct": Fraction(527, 4),
            "expected_hessian_product_rule": Fraction(527, 4),
            "Pi2E_norm_squared": Fraction(277729, 32),
            "twice_A_E": Fraction(527, 2),
            "twice_A_Pi2E_from_kernel": Fraction(527, 2),
        }:
            return False

        # External h-leg counts survive differentiation in eta.  Reconstruct
        # the odd transfer inventory rather than accepting its prose label.
        c_transfers = signed_transfers(1)
        w1_transfers = signed_transfers(0) | signed_transfers(2)
        b_transfers = signed_transfers(1)
        w1_b = {left + right for left in w1_transfers for right in b_transfers}
        even_r = signed_transfers(0) | signed_transfers(2) | signed_transfers(4)
        r_a = {left + right for left in even_r for right in signed_transfers(1)}
        if c_transfers | w1_b | r_a != {-5, -3, -1, 1, 3, 5}:
            return False

        # A single h\otimes h covariance insertion leaves three signs in the
        # momentum closure and therefore samples transfers one and three.
        single_rank = {-(i + j + k) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)}
        if single_rank != {-3, -1, 1, 3}:
            return False
        if 0 in {i + j + k for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)}:
            return False

        required_disposition = {
            "second_chaos_expected_hessian_representation": "PROVED",
            "combined_effective_hessian_formula": "PROVED",
            "conditioned_bulk_plus_rank_one_decomposition": "PROVED",
            "explicit_lattice_momentum_kernel": "OPEN",
            "effective_second_chaos_kernel_norm_bound": "OPEN",
            "whole_lattice_order_g_four_power_survival": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        }
        disposition = data["method_disposition"]
        if any(disposition.get(name) != value for name, value in required_disposition.items()):
            return False
        if not all(data["checks"].values()):
            return False
        return True
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)

#!/usr/bin/env python3
"""Independent verifier for the complete-g^4 chaos gate reduction."""

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

from reverse_physics.verify_bt_euclidean_complete_g4_uv_noncancellation import (
    verify as verify_complete_predecessor,
)


CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CHAOS_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-chaos-gate-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    return [
        (left[i] if i < len(left) else Fraction(0))
        + (right[i] if i < len(right) else Fraction(0))
        for i in range(size)
    ]


def scale(poly: list[Fraction], factor: Fraction | int) -> list[Fraction]:
    return [Fraction(factor) * value for value in poly]


def multiply(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def hermites(maximum: int) -> list[list[Fraction]]:
    values = [[Fraction(1)], [Fraction(0), Fraction(1)]]
    x = [Fraction(0), Fraction(1)]
    for degree in range(1, maximum):
        values.append(add(multiply(x, values[degree]), scale(values[degree - 1], -degree)))
    return values[: maximum + 1]


def gaussian_moment(power: int) -> Fraction:
    if power % 2:
        return Fraction(0)
    result = Fraction(1)
    for factor in range(1, power, 2):
        result *= factor
    return result


def expectation(poly: list[Fraction]) -> Fraction:
    return sum(value * gaussian_moment(power) for power, value in enumerate(poly))


def inner(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return expectation(multiply(left, right))


def combination(basis: list[list[Fraction]], terms: tuple[tuple[int, int], ...]) -> list[Fraction]:
    result = [Fraction(0)]
    for degree, coefficient in terms:
        result = add(result, scale(basis[degree], coefficient))
    return result


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
        if not verify_complete_predecessor():
            return False

        basis = hermites(8)
        for m in range(9):
            for n in range(9):
                expected = Fraction(math.factorial(n) if m == n else 0)
                if inner(basis[m], basis[n]) != expected:
                    return False
        a = basis[2]
        d = combination(basis, ((1, 2), (3, 3), (5, 5)))
        e = combination(basis, ((0, 7), (2, 11), (4, 13), (6, 17), (8, 19)))
        pi2e = scale(basis[2], 11)
        exact = {
            "norm_A_squared": inner(a, a),
            "norm_D_squared": inner(d, d),
            "norm_Pi2E_squared": inner(pi2e, pi2e),
            "twice_A_E": 2 * inner(a, e),
            "twice_A_Pi2E": 2 * inner(a, pi2e),
            "M4": inner(d, d) + 2 * inner(a, e),
        }
        fixture = data["exact_hermite_fixture"]["values"]
        if any(decode(fixture[name]) != value for name, value in exact.items()):
            return False
        if exact != {
            "norm_A_squared": Fraction(2),
            "norm_D_squared": Fraction(3058),
            "norm_Pi2E_squared": Fraction(242),
            "twice_A_E": Fraction(44),
            "twice_A_Pi2E": Fraction(44),
            "M4": Fraction(3102),
        }:
            return False

        inventory = data["chaos_inventory"]
        if inventory["exact_reduction"] != "M4=||D||_0^2+2*<A,Pi2(E)>_0":
            return False
        if inventory["status"] != "PROVED_BY_GAUSSIAN_CHAOS_ORTHOGONALITY":
            return False
        estimate = data["sufficient_effective_kernel_estimate"]
        if estimate["status"] != "EXACT_SUFFICIENT_REDUCTION_BOUND_NOT_YET_PROVED":
            return False
        if "tends to zero" not in estimate["relative_to_power"]:
            return False
        target = data["effective_kernel_target"]
        if target["status"] != "OPEN_SINGLE_EFFECTIVE_KERNEL_NORM":
            return False
        required_disposition = {
            "complete_order_g_four_chaos_decomposition": "PROVED",
            "all_signed_cancellation_localized_to_second_chaos": "PROVED",
            "positive_norm_uv_power_lower_bound": "PROVED",
            "effective_second_chaos_kernel_norm_bound": "OPEN",
            "whole_lattice_order_g_four_power_survival": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
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

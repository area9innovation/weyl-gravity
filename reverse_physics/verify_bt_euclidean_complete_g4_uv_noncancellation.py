#!/usr/bin/env python3
"""Independent verifier for complete-g^4 UV-local noncancellation."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.verify_bt_euclidean_quartic_score_power_obstruction import (
    verify as verify_quartic_predecessor,
)


CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_UV_NONCANCELLATION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-uv-noncancellation-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def convolve(left: list[Fraction], right: list[Fraction], degree: int) -> list[Fraction]:
    result = [Fraction(0) for _ in range(degree + 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= degree:
                result[i + j] += a * b
    return result


def gaussian_moment(power: int, variance: Fraction) -> Fraction:
    if power % 2:
        return Fraction(0)
    result = Fraction(1)
    for factor in range(1, power, 2):
        result *= factor
    return result * variance ** (power // 2)


def gaussian_expectation(polynomial: list[Fraction], variance: Fraction) -> Fraction:
    return sum(
        coefficient * gaussian_moment(power, variance)
        for power, coefficient in enumerate(polynomial)
    )


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
        if not verify_quartic_predecessor():
            return False

        # Independent action expansion by truncated series squaring.
        a, b, c, d = map(Fraction, (2, 3, 5, 7))
        residual = [a, b / 2, c / 6, d / 24]
        action = [value / 2 for value in convolve(residual, residual, 3)]
        action_fixture = data["exact_action_expansion"]["exact_fixture"]
        if [decode(action_fixture[name]) for name in ("S1", "S2", "S3")] != action[1:4]:
            return False
        if action[1:4] != [Fraction(3), Fraction(67, 24), Fraction(11, 6)]:
            return False

        # Independent Gaussian-polynomial evaluation of W1 and W2.
        variance = Fraction(2)
        s1 = list(map(Fraction, (1, 2, 3, 4)))
        s2 = list(map(Fraction, (5, 6, 7, 8, 9)))
        mean_s1 = gaussian_expectation(s1, variance)
        mean_s2 = gaussian_expectation(s2, variance)
        variance_s1 = gaussian_expectation(convolve(s1, s1, 6), variance) - mean_s1**2
        w2 = mean_s2 - variance_s1 / 2
        fiber_fixture = data["free_fiber_effective_action"]["exact_fixture"]
        expected_fiber = {
            "variance": variance,
            "W1": mean_s1,
            "VarS1": variance_s1,
            "MeanS2": mean_s2,
            "W2": w2,
        }
        if any(decode(fiber_fixture[name]) != value for name, value in expected_fiber.items()):
            return False
        if expected_fiber != {
            "variance": Fraction(2),
            "W1": Fraction(7),
            "VarS1": Fraction(2192),
            "MeanS2": Fraction(127),
            "W2": Fraction(-969),
        }:
            return False

        # Independent normalized-series division for the two-state fixture.
        states = (
            (Fraction(1, 3), Fraction(1), Fraction(2), Fraction(-1), Fraction(3), Fraction(1)),
            (Fraction(2, 3), Fraction(-2), Fraction(1), Fraction(4), Fraction(-3, 2), Fraction(-2)),
        )
        numerator = [Fraction(0) for _ in range(5)]
        denominator = [Fraction(0) for _ in range(5)]
        for weight, a0, b0, c0, w1, w2_state in states:
            score = [Fraction(0), a0, b0, c0]
            score_square = convolve(score, score, 4)
            density = [Fraction(1), -w1, w1**2 / 2 - w2_state]
            weighted_score = convolve(score_square, density, 4)
            for degree in range(5):
                numerator[degree] += weight * weighted_score[degree]
            for degree, coefficient in enumerate(density):
                denominator[degree] += weight * coefficient
        quotient = [Fraction(0) for _ in range(5)]
        for degree in range(5):
            quotient[degree] = numerator[degree] - sum(
                denominator[j] * quotient[degree - j]
                for j in range(1, degree + 1)
            )
        normalization = data["complete_order_g_four"]["exact_normalization_fixture"]
        required_normalization = {
            "mean_W1": -denominator[1],
            "normalization_z2": denominator[2],
            "M2": quotient[2],
            "M3": quotient[3],
            "M4_direct": quotient[4],
            "M4_square_root": quotient[4],
        }
        if any(decode(normalization[name]) != value for name, value in required_normalization.items()):
            return False
        if quotient[4] != Fraction(-211, 12):
            return False

        complete = data["complete_order_g_four"]
        if complete["status"] != "COMPLETE_THROUGH_ORDER_G_FOUR":
            return False
        if complete["direct_formula"] != "M4=E0[B^2+2*A*C-2*A*B*W1+A^2*(W1^2/2-W2-z2)]":
            return False
        uv = data["uv_local_soft_filtration"]
        if uv["status"] != "UV_LOCAL_POWER_CANCELLATION_OBSTRUCTED":
            return False
        if uv["term_orders"]["B_squared"] != "O(|p|^2) with a strictly positive coefficient on an open neighborhood of the exact fixture":
            return False
        if data["global_cancellation_boundary"]["status"] != "WHOLE_LATTICE_COEFFICIENT_OPEN_IR_COMPLEMENT_ISOLATED":
            return False
        required_disposition = {
            "complete_order_g_four_background_score_formula": "PROVED",
            "complete_order_g_four_uv_local_p_squared_coefficient": "POSITIVE_NONZERO",
            "uv_local_or_diagramwise_power_cancellation": "OBSTRUCTED",
            "whole_lattice_order_g_four_power_cancellation": "OPEN",
            "infrared_complement_power_bound": "OPEN",
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

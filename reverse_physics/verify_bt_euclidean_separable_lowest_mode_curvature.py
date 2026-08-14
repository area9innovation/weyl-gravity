#!/usr/bin/env python3
"""Independent checks for the BT separable lowest-mode theorem."""

from __future__ import annotations

import json
import hashlib
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SEPARABLE_LOWEST_MODE_CURVATURE_V1.json")
SCHEMA_PATH = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-separable-lowest-mode-curvature-v1.schema.json")
MODE = (1, 0, -1, 0)
CORRELATED = (
    (-3, -5, -5, -6),
    (-5, -2, -2, -1),
    (-4, -5, -4, -6),
    (6, 2, 5, -2),
)


def p2(exponent: int) -> Fraction:
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2 ** (-exponent))


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def independent_parts(field: tuple[tuple[int, ...], ...]) -> tuple[Fraction, Fraction]:
    temporal = Fraction()
    spatial = Fraction()
    for t, row in enumerate(field):
        for x, value in enumerate(row):
            weights_t = [p2(field[s][x] - value) for s in ((t - 1) % 4, (t + 1) % 4)]
            differences = [MODE[(t - 1) % 4] - MODE[t], MODE[(t + 1) % 4] - MODE[t]]
            first = sum((w * d for w, d in zip(weights_t, differences)), Fraction())
            second = sum((w * d * d for w, d in zip(weights_t, differences)), Fraction())
            temporal_residual = sum(weights_t, Fraction(-2))
            temporal += first * first + temporal_residual * second
            spatial_residual = sum(
                (p2(row[y] - value) for y in ((x - 1) % 4, (x + 1) % 4)),
                Fraction(-2),
            )
            spatial += spatial_residual * second
    return temporal, spatial


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        if list(Draft202012Validator(schema).iter_errors(data)):
            return False
        temporal, spatial = independent_parts(CORRELATED)
        fixture = data["exact_correlated_fixture"]
        if decode(fixture["temporal_line_part_per_inert_spatial_cell"]) != temporal:
            return False
        if decode(fixture["spatial_correlation_remainder_per_inert_spatial_cell"]) != spatial:
            return False
        if not (spatial < 0 < temporal + spatial):
            return False
        if sum(CORRELATED[t][x] * MODE[t] for t in range(4) for x in range(4)):
            return False
        if data["method_disposition"]["all_background_recentered_conditional_variance"] != "OPEN":
            return False
        if data["method_disposition"]["actual_interacting_h_minus_one_second_moment"] != "OPEN":
            return False
        if data["foundational_dependency_cut"]["weakest_base_or_reversal"] != "NOT_ESTABLISHED":
            return False
        if data["theorem"]["retained_fraction_of_free_curvature"] != {"numerator": 2, "denominator": 3}:
            return False
        separable = tuple(
            tuple((0, 1, -1, 0)[t] + (0, 1, -1, 0)[x] for x in range(4))
            for t in range(4)
        )
        sep_temporal, sep_spatial = independent_parts(separable)
        sep_fixture = data["exact_separable_fixture"]
        if decode(sep_fixture["temporal_line_part"]) != 16 * sep_temporal:
            return False
        if decode(sep_fixture["spatial_remainder"]) != 16 * sep_spatial:
            return False
        if decode(sep_fixture["full_hessian"]) != 16 * (sep_temporal + sep_spatial):
            return False
        if data["checks"] != {
            "all_background_extension_remains_open": True,
            "centering_constant_does_not_change_weights": True,
            "conditional_variance_constant_is_three": True,
            "correlated_fixture_is_mode_orthogonal": True,
            "correlated_total_hessian_remains_positive": True,
            "correlation_remainder_is_strictly_negative": True,
            "general_curvature_fraction_is_two_thirds": True,
            "interacting_h_minus_one_bound_remains_open": True,
            "mode_is_lowest_axial_eigenvector_at_L4": True,
            "no_continuum_born_krein_or_lorentzian_promotion": True,
            "separable_spatial_remainder_is_nonnegative": True,
        }:
            return False
        for source in data["provenance"]["inputs"]:
            if sha256(os.path.join(ROOT, source["path"])) != source["sha256"]:
                return False
        return True
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)

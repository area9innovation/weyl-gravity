#!/usr/bin/env python3
"""Independent verifier for the BT cubic-current chaos obstruction."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_CURRENT_CHAOS_OBSTRUCTION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-cubic-current-chaos-obstruction-v1.schema.json")
MOTIF = {(0, 0, 0, 0): -1, (0, 1, 0, 0): 1, (1, 0, 0, 0): 1, (1, 2, 0, 0): -1}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def digest(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def enumerate_motif(length: int) -> dict:
    points = list(itertools.product(range(length), repeat=4))

    def shift(point: tuple[int, ...], axis: int, step: int) -> tuple[int, ...]:
        changed = list(point)
        changed[axis] = (changed[axis] + step) % length
        return tuple(changed)

    field = {point: Fraction(MOTIF.get(point, 0)) for point in points}
    laplacian, quadratic, cubic = {}, {}, {}
    for point in points:
        differences = [field[shift(point, axis, step)] - field[point] for axis in range(4) for step in (-1, 1)]
        laplacian[point] = sum(differences, Fraction(0))
        quadratic[point] = sum((value**2 for value in differences), Fraction(0)) / 2
        cubic[point] = sum((value**3 for value in differences), Fraction(0)) / 6
    current = {}
    for point in points:
        other = shift(point, 0, 1)
        delta = field[other] - field[point]
        current[point] = cubic[point] - cubic[other] + delta * (quadratic[point] + quadratic[other]) + delta**2 * (laplacian[point] - laplacian[other]) / 2
    return {
        "norm": sum((value**2 for value in laplacian.values()), Fraction(0)),
        "total": sum(current.values(), Fraction(0)),
        "profile": [sum((current[point] for point in points if point[0] == time), Fraction(0)) for time in range(length)],
        "laplacian_support": sum(value != 0 for value in laplacian.values()),
        "current_support": sum(value != 0 for value in current.values()),
    }


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], "input hash drift")

        support = {tuple(item["site"]): item["value"] for item in cert["compact_cubic_motif"]["exponent_support"]}
        require(support == MOTIF, "motif support drift")
        require(all(sum(value for point, value in support.items() if point[0] == time) == 0 for time in (0, 1)), "motif left background slice")
        five, seven = enumerate_motif(5), enumerate_motif(7)
        require(five["norm"] == seven["norm"] == 350, "free action norm drift")
        require(five["total"] == seven["total"] == 38, "cubic current total drift")
        require(five["profile"] == [44, -3, 0, 0, -3], "five-torus profile drift")
        require(seven["profile"] == [44, -3, 0, 0, 0, 0, -3], "seven-torus profile drift")
        require(five["laplacian_support"] == seven["laplacian_support"] == 28, "Laplacian support drift")
        require(five["current_support"] == seven["current_support"] == 45, "current support drift")

        motif = cert["compact_cubic_motif"]
        require(frac(motif["free_action_inner_product_norm_squared"]) == 350, "certified norm drift")
        require([frac(value) for value in motif["cubic_current_row_profile"]] == five["profile"], "certified profile drift")
        require(frac(motif["fourier_profile_floor"]) == 38, "profile floor drift")
        require(motif["nonzero_laplacian_count"] == 28 and motif["nonzero_cubic_current_count"] == 45, "support counts drift")

        variance_density = Fraction(6 * 38**2, 625 * 350**3)
        tuned_density = variance_density * Fraction(2, 5) ** 6
        divergence = tuned_density / Fraction(1936, 49)
        obstruction = cert["extensive_variance_obstruction"]
        require(variance_density == Fraction(1083, 3349609375), "variance arithmetic failed")
        require(frac(obstruction["general_variance_density"]) == variance_density, "general variance density drift")
        require(tuned_density == frac(obstruction["lambda_point_four_variance_density"]) == Fraction(69312, 52337646484375), "tuned density drift")
        require(divergence == frac(obstruction["normalized_divergence_coefficient"]) == Fraction(4332, 129241943359375), "normalized divergence drift")

        disposition = cert["method_disposition"]
        require(disposition["cubic_current_termwise_hyperuniformity"] == "OBSTRUCTED", "cubic obstruction weakened")
        require(disposition["homogeneous_order_by_order_absolute_current_bound"] == "OBSTRUCTED", "termwise obstruction weakened")
        require(disposition["cross_order_and_measure_Ward_cancellation"] == "OPEN", "Ward cancellation promoted")
        require(disposition["complete_perturbative_current_susceptibility"] == "NOT_DECIDED", "complete perturbative result promoted")
        require(disposition["nonperturbative_background_marginal_susceptibility"] == "OPEN", "interacting susceptibility promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(disposition["continuum_limit"] == disposition["born_rule"] == disposition["lorentzian_transfer"] == "NOT_ESTABLISHED", "physics boundary promoted")
        require(disposition["krein_reconstruction"] == "NOT_ASSESSED", "Krein boundary promoted")
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT cubic-current chaos obstruction: PASS" if ok else "BT cubic-current chaos obstruction: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

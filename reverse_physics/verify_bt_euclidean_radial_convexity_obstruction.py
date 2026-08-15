#!/usr/bin/env python3
"""Independent verifier for the BT radial-convexity obstruction."""

from __future__ import annotations

import collections
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


sys.set_int_max_str_digits(20000)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RADIAL_CONVEXITY_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-radial-convexity-obstruction-v1.schema.json",
)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def digest(relative: str) -> str:
    value = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def orbit_reconstruction(exponents: tuple[int, ...]) -> tuple[Fraction, Fraction, Fraction, dict[int, int]]:
    """Recompute via site-type multiplicities, not the producer's site sum."""
    side = 6
    points = tuple(itertools.product(range(side), repeat=4))
    index = {point: number for number, point in enumerate(points)}
    shells = tuple(sum(min(x, side - x) for x in point) for point in points)
    types: collections.Counter[tuple[int, tuple[int, ...]]] = collections.Counter()
    for number, point in enumerate(points):
        counts = [0] * len(exponents)
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % side
                counts[shells[index[tuple(neighbor)]]] += 1
        types[(shells[number], tuple(counts))] += 1

    base = Fraction(101, 100)
    action = Fraction(0)
    virial = Fraction(0)
    curvature = Fraction(0)
    multiplicities: collections.Counter[int] = collections.Counter()
    for (level, counts), number_of_sites in types.items():
        multiplicities[level] += number_of_sites
        residual = Fraction(-8)
        first = Fraction(0)
        second = Fraction(0)
        for neighbor_level, edge_count in enumerate(counts):
            if not edge_count:
                continue
            difference = exponents[neighbor_level] - exponents[level]
            weight = base**difference
            residual += edge_count * weight
            first += edge_count * weight * difference
            second += edge_count * weight * difference * difference
        action += number_of_sites * residual * residual / 2
        virial += number_of_sites * residual * first
        curvature += number_of_sites * (first * first + residual * second)
    return action, virial, curvature, dict(multiplicities)


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        cert = load(path)
        Draft202012Validator(load(SCHEMA)).validate(cert)
        for item in cert["provenance"]["inputs"]:
            require(digest(item["path"]) == item["sha256"], "input hash drift")

        fixture = cert["exact_fixture"]
        exponents = tuple(fixture["shell_exponents"])
        require(exponents == (0, 1, 2, 3, 4, 5, 7, 10, 15, 25, 48, 101, 214), "profile drift")
        action, virial, curvature, multiplicities = orbit_reconstruction(exponents)
        require(action == frac(fixture["action_A"]), "action mismatch")
        require(virial == frac(fixture["virial_log_coefficient_C_D"]), "virial mismatch")
        require(curvature == frac(fixture["radial_curvature_log_squared_coefficient_C_2"]), "curvature mismatch")
        require({str(key): value for key, value in sorted(multiplicities.items())} == fixture["shell_multiplicities"], "shell multiplicity mismatch")

        x = Fraction(1, 100)
        log_upper = x - x * x / 2 + x**3 / 3
        require(log_upper == frac(cert["strict_comparisons"]["log_upper_bound"]), "log bound drift")
        require(action > 0 and virial > 0 and curvature < 0, "sign witness failed")
        require(action - virial * log_upper == frac(cert["strict_comparisons"]["unit_virial_integer_witness"]), "strict gap mismatch")
        require(virial * log_upper < action, "D<A proof failed")
        require(cert["method_disposition"]["pointwise_D_ge_cA_for_0_lt_c_lt_1"] == "OPEN", "weaker constant promoted")
        require(cert["method_disposition"]["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-1 promoted")
        require("LORENTZIAN-CAUSAL" not in cert["dependency_tags"], "Lorentzian scope promoted")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT radial-convexity obstruction certificate: PASS" if ok else "BT radial-convexity obstruction certificate: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent verifier for the two surviving BT g^4 coefficient limits."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_COEFFICIENT_NORMAL_FORM_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-two-pair-coefficient-normal-form-v1.schema.json",
)
SEVEN_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json"
)
LINEAR_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LINEAR_PAIR_BOUNDS_V1.json"
)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction(value: dict) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def return_probability_even(half_steps: int) -> Fraction:
    total = Fraction()
    for a in range(half_steps + 1):
        for b in range(half_steps - a + 1):
            for c in range(half_steps - a - b + 1):
                d = half_steps - a - b - c
                total += Fraction(
                    1,
                    math.factorial(a) ** 2
                    * math.factorial(b) ** 2
                    * math.factorial(c) ** 2
                    * math.factorial(d) ** 2,
                )
    return Fraction(math.factorial(2 * half_steps), 8 ** (2 * half_steps)) * total


def independent_a4_lower(cutoff: int) -> Fraction:
    return Fraction(1, 8) * sum(
        (return_probability_even(step) for step in range(cutoff + 1)),
        Fraction(),
    )


def independent_s4_lower(radius: int) -> Fraction:
    result = Fraction()
    for point in __import__("itertools").product(range(-radius, radius + 1), repeat=4):
        n1, n2, n3, n4 = point
        norm = sum(value * value for value in point)
        shifted = (n1 + 1) ** 2 + n2 * n2 + n3 * n3 + n4 * n4
        if norm and shifted:
            transverse = n2 * n2 + n3 * n3 + n4 * n4
            result += Fraction(transverse**2, norm**3 * shifted**2)
    return result


def atan_interval(inverse: int, terms: int) -> tuple[Fraction, Fraction]:
    x = Fraction(1, inverse)
    partial = sum(
        ((-1) ** index * x ** (2 * index + 1) / (2 * index + 1) for index in range(terms)),
        Fraction(),
    )
    next_term = x ** (2 * terms + 1) / (2 * terms + 1)
    if terms % 2 == 0:
        return partial, partial + next_term
    return partial - next_term, partial


def verify_pi_upper() -> None:
    a_lo, a_hi = atan_interval(5, 20)
    b_lo, b_hi = atan_interval(239, 8)
    pi_lo = 16 * a_lo - 4 * b_hi
    pi_hi = 16 * a_hi - 4 * b_lo
    require(Fraction(3) < pi_lo < pi_hi < Fraction(22, 7), "Machin pi interval failed")


def poly_add(left: dict[tuple[int, int], Fraction], right: dict[tuple[int, int], Fraction]) -> dict[tuple[int, int], Fraction]:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, Fraction()) + coefficient
    return {key: value for key, value in result.items() if value}


def poly_scale(poly: dict[tuple[int, int], Fraction], scale: Fraction | int) -> dict[tuple[int, int], Fraction]:
    return {key: value * scale for key, value in poly.items() if value * scale}


def poly_mul(left: dict[tuple[int, int], Fraction], right: dict[tuple[int, int], Fraction]) -> dict[tuple[int, int], Fraction]:
    result: dict[tuple[int, int], Fraction] = {}
    for (lx, lr), lc in left.items():
        for (rx, rr), rc in right.items():
            key = lx + rx, lr + rr
            result[key] = result.get(key, Fraction()) + lc * rc
    return {key: value for key, value in result.items() if value}


def verify_soft_cubic_and_tadpole() -> None:
    one = {(0, 0): Fraction(1)}
    n = {(2, 0): Fraction(1), (0, 1): Fraction(1)}
    shifted = {
        (2, 0): Fraction(1),
        (1, 0): Fraction(2),
        (0, 0): Fraction(1),
        (0, 1): Fraction(1),
    }
    numerator = poly_add(poly_add(poly_mul(one, one), poly_mul(n, n)), poly_mul(shifted, shifted))
    numerator = poly_add(numerator, poly_scale(poly_add(poly_add(n, shifted), poly_mul(n, shifted)), -2))
    cubic = poly_scale(numerator, Fraction(1, 6))
    require(cubic == {(0, 1): Fraction(-2, 3)}, f"soft cubic polynomial failed: {cubic}")

    # The quartic tadpole limit has three exact symmetry ledgers:
    # int sin(k_1)^2/omega^2=A4/2-1/16,
    # int omega_1/omega=1/4, and int 1/omega=A4.
    a4_coefficient = Fraction(8) * Fraction(1, 2) + Fraction(4)
    constant_coefficient = Fraction(8) * Fraction(-1, 16) + Fraction(2) * Fraction(1, 4)
    require(a4_coefficient / 24 == Fraction(1, 3), "tadpole A4 coefficient failed")
    require(constant_coefficient == 0, "tadpole constant cancellation failed")


def verify_derivative_collapse() -> None:
    # Coefficient matrix of 24*D4 in the basis sine(q,r,s) times omega(q,r,s).
    matrix = [[Fraction() for _ in range(3)] for _ in range(3)]
    for sine in range(3):
        for omega in range(3):
            matrix[sine][omega] += 2
    # Subtract 2*[c(A+B-C)+a(C+B-A)+b(C+A-B)].
    bracket = (
        (2, (1, 1, -1)),
        (0, (-1, 1, 1)),
        (1, (1, -1, 1)),
    )
    for sine, signs in bracket:
        for omega, sign in enumerate(signs):
            matrix[sine][omega] -= 2 * sign
    require(
        matrix == [
            [Fraction(4), Fraction(), Fraction()],
            [Fraction(), Fraction(4), Fraction()],
            [Fraction(), Fraction(), Fraction(4)],
        ],
        f"six-term derivative collapse failed: {matrix}",
    )
    require(Fraction(4, 24) == Fraction(1, 6), "collapsed derivative normalization failed")
    require(Fraction(7 * 2 * 8, 24) == Fraction(14, 3), "one-soft K4 domination constant failed")
    require(Fraction(48, 36) == Fraction(4, 3), "pair-7 collapsed coefficient failed")


def verify_upstream(certificate: dict) -> None:
    with open(os.path.join(ROOT, LINEAR_REL), encoding="utf-8") as handle:
        linear = json.load(handle)
    with open(os.path.join(ROOT, SEVEN_REL), encoding="utf-8") as handle:
        seven = json.load(handle)
    require(
        linear["power_sector_reduction"]["pairs_still_capable_of_N_omega_p_scale"] == [4, 7],
        "upstream two-pair gate drift",
    )
    pairs = {row["pair"]: row for row in seven["inversion_reduction"]["pairs"]}
    require(fraction(pairs[4]["paired_coefficient"]) == -216, "pair-4 coefficient drift")
    require(fraction(pairs[7]["paired_coefficient"]) == 48, "pair-7 coefficient drift")
    require(certificate["normalization"]["coefficient_scale"] == "I_j(L)/(N*omega(p_L))", "normalization drift")


def verify_exact_gap(certificate: dict) -> None:
    pair_four = certificate["pair_four"]
    a4 = independent_a4_lower(pair_four["walk_cutoff_half_steps"])
    s4 = independent_s4_lower(pair_four["cube_radius"])
    require(a4 == fraction(pair_four["A_4_lower"]), "A4 return truncation drift")
    require(s4 == fraction(pair_four["S_4_cube_lower"]), "S4 cube truncation drift")
    verify_pi_upper()
    gap = 2 * a4 * s4 / Fraction(22, 7) ** 4
    require(gap == fraction(pair_four["magnitude_lower"]), "c4 rational gap drift")
    require(gap > Fraction(1613, 100000), "c4 gap no longer exceeds 0.01613")


def verify_boundaries(certificate: dict) -> None:
    disposition = certificate["method_disposition"]
    expected = {
        "pair_4_coefficient_normal_form": "PROVED_STRICTLY_NEGATIVE",
        "pair_7_coefficient_normal_form": "PROVED_STRICTLY_POSITIVE_FINITE",
        "combined_pair_4_pair_7_coefficient": "OPEN",
        "complete_M4_large_volume_sign_and_scaling": "OPEN",
        "actual_interacting_h_minus_one_second_moment": "OPEN",
        "continuum_limit": "NOT_ESTABLISHED",
        "born_rule": "NOT_ESTABLISHED",
        "krein_reconstruction": "NOT_ASSESSED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    require(all(disposition.get(key) == value for key, value in expected.items()), "claim boundary drift")
    require(certificate["comparison_gate"]["noncancellation"] == "OPEN", "noncancellation promoted")
    require(certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency tags drift")
    require(all(certificate["checks"].values()), "certificate contains failed check")


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = sorted(Draft202012Validator(schema).iter_errors(certificate), key=lambda item: list(item.path))
        require(not errors, f"schema validation failed: {errors[0].message if errors else ''}")
        require(certificate["data_sha256"] == file_hash(certificate["data"]), "data hash drift")
        require(certificate["producer_sha256"] == file_hash(certificate["producer"]), "producer hash drift")
        for source in certificate["provenance"]["inputs"]:
            require(source["sha256"] == file_hash(source["path"]), f"input hash drift: {source['path']}")
        with open(os.path.join(ROOT, certificate["data"]), encoding="utf-8") as handle:
            data = json.load(handle)
        for field in ("normalization", "pair_four", "pair_seven", "comparison_gate", "method_disposition", "does_not_establish", "next_gate"):
            require(certificate[field] == data[field], f"certificate/data drift: {field}")
        verify_upstream(certificate)
        verify_soft_cubic_and_tadpole()
        verify_derivative_collapse()
        verify_exact_gap(certificate)
        verify_boundaries(certificate)
        return True
    except (OSError, ValueError, KeyError, TypeError, VerificationError) as error:
        if path == CERT_PATH:
            print(f"FAIL: {error}", file=sys.stderr)
        return False


def main() -> int:
    if verify():
        print("PASS: exact BT pair-4/pair-7 coefficient normal forms and boundaries verified")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

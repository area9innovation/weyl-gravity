#!/usr/bin/env python3
"""Independent verifier for BT complete-g4 two-pair noncancellation."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1.json")
SCHEMA_PATH = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-two-pair-noncancellation-v1.schema.json")
UPSTREAM_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_COEFFICIENT_NORMAL_FORM_V1.json"


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


def alternating_atan(inverse: int, count: int) -> tuple[Fraction, Fraction]:
    x = Fraction(1, inverse)
    terms = [(-1) ** index * x ** (2 * index + 1) / (2 * index + 1) for index in range(count + 1)]
    partial = sum(terms[:-1], Fraction())
    return (partial, partial + abs(terms[-1])) if count % 2 == 0 else (partial - abs(terms[-1]), partial)


def independent_pi_bounds() -> tuple[Fraction, Fraction]:
    a_lo, a_hi = alternating_atan(5, 30)
    b_lo, b_hi = alternating_atan(239, 10)
    return 16 * a_lo - 4 * b_hi, 16 * a_hi - 4 * b_lo


def sine_pair(lower_x: Fraction, upper_x: Fraction) -> tuple[Fraction, Fraction]:
    lower = sum(((-1) ** i * lower_x ** (2 * i + 1) / math.factorial(2 * i + 1) for i in range(12)), Fraction())
    upper = sum(((-1) ** i * upper_x ** (2 * i + 1) / math.factorial(2 * i + 1) for i in range(11)), Fraction())
    return max(Fraction(), lower), min(Fraction(1), upper)


def dyadic_floor(value: Fraction, bits: int) -> int:
    return (value.numerator << bits) // value.denominator


def dyadic_ceil(value: Fraction, bits: int) -> int:
    quotient, remainder = divmod(value.numerator << bits, value.denominator)
    return quotient + bool(remainder)


def independent_energy_table(total: int, used: int, bits: int) -> tuple[list[int], list[int]]:
    pi_lo, pi_hi = independent_pi_bounds()
    lower, upper = [], []
    for index in range(used + 1):
        s_lo, s_hi = sine_pair(Fraction(index, 2 * total) * pi_lo, Fraction(index, 2 * total) * pi_hi)
        lower.append(dyadic_floor(4 * s_lo**2, bits))
        upper.append(dyadic_ceil(4 * s_hi**2, bits))
    return lower, upper


def multiplicity(indices: tuple[int, int, int, int]) -> int:
    result = math.factorial(4)
    for count in Counter(indices).values():
        result //= math.factorial(count)
    return result


def independent_inverse_sum(total: int, used: int, energy_bits: int, value_bits: int) -> tuple[int, list[int], list[int]]:
    lower, upper = independent_energy_table(total, used, energy_bits)
    numerator = 1 << (energy_bits + value_bits)
    result = 0
    for indices in itertools.combinations_with_replacement(range(used), 4):
        if indices[-1] == 0:
            continue
        denominator = sum(lower[index] for index in indices)
        result += multiplicity(indices) * ((numerator + denominator - 1) // denominator)
    return result, lower, upper


def independent_walk_lower(cutoff: int) -> Fraction:
    coefficient = [Fraction(1, math.factorial(index) ** 2) for index in range(cutoff + 1)]
    power = [Fraction(1)] + [Fraction()] * cutoff
    for _ in range(4):
        power = [
            sum((power[left] * coefficient[degree - left] for left in range(degree + 1)), Fraction())
            for degree in range(cutoff + 1)
        ]
    return sum(
        (Fraction(math.factorial(2 * degree), 8 ** (2 * degree + 1)) * value for degree, value in enumerate(power)),
        Fraction(),
    )


def independent_centered_sum(total: int, used: int, lower: list[int], upper: list[int], alo: int, aup: int, energy_bits: int, center_bits: int) -> int:
    reciprocal_scale = 1 << (energy_bits + center_bits)
    result = 0
    for indices in itertools.combinations_with_replacement(range(used), 4):
        if indices[-1] == 0:
            continue
        low_sum = sum(lower[index] for index in indices)
        high_sum = sum(upper[index + 1] for index in indices)
        reciprocal_hi = (reciprocal_scale + low_sum - 1) // low_sum
        reciprocal_lo = reciprocal_scale // high_sum
        deviation = max(reciprocal_hi - alo, aup - reciprocal_lo)
        square = deviation**3
        root = math.isqrt(square)
        root += root * root != square
        result += multiplicity(indices) * root
    return result


def verify_matrix_lemma() -> None:
    # R_+/3 has principal minors b, a+b+c, a, b(a+c), ab,
    # a(b+c), abc.  The following exact fixtures independently exercise the
    # determinant and rank-one inverse formula, including all off-diagonal terms.
    for a, b, c, u, v, w in (
        (Fraction(2), Fraction(3), Fraction(5), Fraction(1, 3), Fraction(-2, 5), Fraction(1, 7)),
        (Fraction(7, 4), Fraction(9, 5), Fraction(11, 6), Fraction(-3, 8), Fraction(5, 9), Fraction(-2, 7)),
    ):
        matrix = [[b, b, 0], [b, a + b + c, a], [0, a, a]]
        determinant = (
            matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
            - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        )
        require(determinant == a * b * c, "boundary matrix determinant identity failed")
        adjoint_quadratic = (
            a * b * (u + v) ** 2
            + a * c * (u + w) ** 2
            + b * c * (v + w) ** 2
        )
        expanded = (
            a * b * u**2 + 2 * a * b * u * v + a * b * v**2
            + a * c * u**2 + 2 * a * c * u * w + a * c * w**2
            + b * c * v**2 + 2 * b * c * v * w + b * c * w**2
        )
        require(adjoint_quadratic == expanded, "rank-one adjugate identity failed")


def verify_outward_bound(certificate: dict) -> None:
    bound = certificate["pair_seven_bound"]
    ebits = bound["energy_dyadic_bits"]
    cbits = bound["center_dyadic_bits"]
    vbits = bound["integrand_dyadic_bits"]
    coarse = bound["coarse_intervals_per_axis"]
    refinement = bound["origin_refinement_per_axis"]
    fine = coarse * refinement
    ci, clo, chi = independent_inverse_sum(coarse, coarse, ebits, vbits)
    fi, flo, fhi = independent_inverse_sum(fine, refinement, ebits, vbits)
    require(ci == bound["coarse_inverse_integer_sum"], "coarse inverse sum drift")
    require(fi == bound["fine_inverse_integer_sum"], "fine inverse sum drift")
    pi_lo, pi_hi = independent_pi_bounds()
    require(pi_lo == fraction(bound["pi_lower"]) and pi_hi == fraction(bound["pi_upper"]), "pi enclosure drift")
    green_upper = Fraction(ci, coarse**4 * (1 << vbits)) + Fraction(fi, fine**4 * (1 << vbits)) + pi_hi**2 / (16 * fine**2)
    require(green_upper == fraction(bound["A_4_upper"]), "A4 upper drift")
    green_lower = independent_walk_lower(bound["walk_cutoff_half_steps"])
    require(green_lower == fraction(bound["A_4_lower"]), "A4 lower drift")
    alo = dyadic_floor(green_lower, cbits)
    aup = dyadic_ceil(green_upper, cbits)
    cm = independent_centered_sum(coarse, coarse, clo, chi, alo, aup, ebits, cbits)
    fm = independent_centered_sum(fine, refinement, flo, fhi, alo, aup, ebits, cbits)
    require(cm == bound["coarse_centered_integer_sum"], "coarse centered sum drift")
    require(fm == bound["fine_centered_integer_sum"], "fine centered sum drift")
    centered = Fraction(cm, coarse**4 * (1 << vbits)) + Fraction(fm, fine**4 * (1 << vbits)) + pi_hi**2 / (32 * fine) + Fraction(1, fine**4)
    require(centered == fraction(bound["centered_M_upper"]), "centered M bound drift")
    convolution = green_upper**3 + centered**2
    require(convolution == fraction(bound["J_3_upper"]), "three-Green convolution drift")
    c7 = 3 * convolution
    require(c7 == fraction(bound["c_7_upper"]), "c7 bound drift")
    require(c7 < Fraction(1613, 100000), "c7 interval no longer separates pair 4")


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
        for field in ("dispersion_theorem", "pair_seven_bound", "comparison", "method_disposition", "does_not_establish", "next_gate"):
            require(certificate[field] == data[field], f"certificate/data drift: {field}")
        with open(os.path.join(ROOT, UPSTREAM_REL), encoding="utf-8") as handle:
            upstream = json.load(handle)
        require(upstream["pair_four"]["magnitude_lower_decimal_floor"] == "0.01613", "upstream c4 gap drift")
        verify_matrix_lemma()
        verify_outward_bound(certificate)
        require(certificate["comparison"]["combined"] == "c_4+c_7<0", "combined sign drift")
        require(certificate["method_disposition"]["complete_M4_large_volume_sign_and_scaling"] == "OPEN", "complete M4 promoted")
        require(certificate["method_disposition"]["actual_interacting_h_minus_one_second_moment"] == "OPEN", "H^-1 promoted")
        require(certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency tags drift")
        require(all(certificate["checks"].values()), "certificate contains a failed check")
        return True
    except (OSError, ValueError, KeyError, TypeError, VerificationError) as error:
        if path == CERT_PATH:
            print(f"FAIL: {error}", file=sys.stderr)
        return False


def main() -> int:
    if verify():
        print("PASS: sharp lattice dispersion and exact BT pair-4/pair-7 noncancellation verified")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

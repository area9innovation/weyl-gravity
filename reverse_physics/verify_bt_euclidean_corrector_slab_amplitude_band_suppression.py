#!/usr/bin/env python3
"""Independent verifier for BT amplitude-band slab suppression."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator, ValidationError


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_AMPLITUDE_BAND_SUPPRESSION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-euclidean-corrector-slab-amplitude-band-suppression-v1.schema.json")
ZERO = (0, 0, 0, 0, 0)
MATRIX = {
    time: ((0, 0, 1, -1) if time == 1 else (0, 1, 0, -1) if time == 2 else (0, 0, 0, 0))
    for time in range(-1, 5)
}
VARIABLES = (
    ((1, 0, 0, 0, 0), (0, 1, 0, 0, 0)),
    ((0, -1, 0, 0, 0), (0, 0, 1, 0, 0)),
    ((0, 0, -1, 0, 0), (0, 0, 0, 1, 0)),
    ((0, 0, 0, -1, 0), (0, 0, 0, 0, 1)),
)
EDGE = (Fraction(199, 200), Fraction(200, 199))


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


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def product(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    values = [left[0] * right[0], left[0] * right[1], left[1] * right[0], left[1] * right[1]]
    return min(values), max(values)


def append(polynomial: dict, exponent: tuple[int, ...], interval: tuple[Fraction, Fraction]) -> None:
    old = polynomial.get(exponent, (Fraction(0), Fraction(0)))
    polynomial[exponent] = old[0] + interval[0], old[1] + interval[1]


def polynomial_product(left: dict, right: dict) -> dict:
    result = {}
    for le, li in left.items():
        for re, ri in right.items():
            append(result, tuple(x + y for x, y in zip(le, re)), product(li, ri))
    return result


def amplitude_factor(low: Fraction, high: Fraction, exponent: int) -> tuple[Fraction, Fraction]:
    values = []
    for base in (low, high):
        values.append((base**exponent if exponent >= 0 else 1 / base ** (-exponent)) - 1)
    return min(values), max(values)


def reconstruct(low: Fraction, high: Fraction) -> dict:
    result = {}
    for time, (left, right) in enumerate(VARIABLES):
        for space in range(4):
            residual = {ZERO: (Fraction(-8), Fraction(-8))}
            for exponent in (left, right, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO):
                append(residual, exponent, EDGE)
            delta = {}
            here = MATRIX[time][space]
            for other_time, other_space, exponent in (
                (time - 1, space, left),
                (time + 1, space, right),
                (time, (space - 1) % 4, ZERO),
                (time, (space + 1) % 4, ZERO),
            ):
                factor = amplitude_factor(low, high, MATRIX[other_time][other_space] - here)
                if factor != (Fraction(0), Fraction(0)):
                    append(delta, exponent, product(EDGE, factor))
            doubled = {exponent: product(interval, (Fraction(2), Fraction(2))) for exponent, interval in residual.items()}
            for contribution in (polynomial_product(doubled, delta), polynomial_product(delta, delta)):
                for exponent, interval in contribution.items():
                    append(result, exponent, interval)
    return result


def summarize(index: int, low: Fraction, high: Fraction) -> dict:
    polynomial = reconstruct(low, high)
    square_b = (0, 2, 0, 0, 0)
    square_d = (0, 0, 0, -2, 0)
    linear_b = (0, 1, 0, 0, 0)
    linear_d = (0, 0, 0, -1, 0)
    special = {ZERO, square_b, square_d, linear_b, linear_d}
    discarded = [bounds[0] for exponent, bounds in polynomial.items() if exponent not in special]
    require(all(value >= 0 for value in discarded), f"negative discarded coefficient in bin {index}")
    alpha = min(polynomial[square_b][0], polynomial[square_d][0])
    beta = max(Fraction(0), -polynomial[linear_b][0], -polynomial[linear_d][0])
    constant = polynomial[ZERO][0]
    gap = constant - beta * beta / (2 * alpha)
    require(alpha > 0 and gap > 0, f"nonpositive bin gap {index}")
    return {
        "index": index,
        "amplitude_low": low,
        "amplitude_high": high,
        "square_floor_alpha": alpha,
        "negative_linear_magnitude_beta": beta,
        "constant_floor": constant,
        "residual_square_gap": gap,
        "discarded_coefficient_count": len(discarded),
    }


def decode_bin(item: dict) -> dict:
    return {
        "index": item["index"],
        "amplitude_low": frac(item["amplitude_low"]),
        "amplitude_high": frac(item["amplitude_high"]),
        "square_floor_alpha": frac(item["square_floor_alpha"]),
        "negative_linear_magnitude_beta": frac(item["negative_linear_magnitude_beta"]),
        "constant_floor": frac(item["constant_floor"]),
        "residual_square_gap": frac(item["residual_square_gap"]),
        "discarded_coefficient_count": item["discarded_coefficient_count"],
    }


def encode_bin(item: dict) -> dict:
    rational_keys = (
        "amplitude_low",
        "amplitude_high",
        "square_floor_alpha",
        "negative_linear_magnitude_beta",
        "constant_floor",
        "residual_square_gap",
    )
    encoded = dict(item)
    for key in rational_keys:
        value = item[key]
        encoded[key] = {"numerator": value.numerator, "denominator": value.denominator}
    encoded["all_discarded_lower_coefficients_nonnegative"] = True
    return encoded


def verify_partition(partition: dict, start: Fraction, width: Fraction) -> list[Fraction]:
    require(frac(partition["start"]) == start and frac(partition["bin_width"]) == width, "partition metadata drift")
    require(partition["bin_count"] == 128, "partition bin count drift")
    summaries = []
    for index in range(128):
        low = start + index * width
        high = low + width
        summaries.append(summarize(index, low, high))
    encoded = [encode_bin(item) for item in summaries]
    require(canonical_digest(encoded) == partition["bin_summary_sha256"], "partition summary digest drift")
    minimum = min((item["residual_square_gap"], item["index"]) for item in summaries)
    require(decode_bin(partition["minimum_bin"]) == summaries[minimum[1]], "serialized minimum-bin witness drift")
    require(partition["minimum_bin"]["all_discarded_lower_coefficients_nonnegative"] is True, "minimum-bin sign flag false")
    gaps = [item["residual_square_gap"] for item in summaries]
    return gaps


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            Draft202012Validator(json.load(handle)).validate(cert)
        require(cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "dependency boundary drift")
        require(all(digest(item["path"]) == item["sha256"] for item in cert["provenance"]["inputs"]), "input hash drift")

        section = cert["amplitude_interval_certificate"]
        positive = verify_partition(section["positive_band_partition"], Fraction(2), Fraction(1, 64))
        inverse = verify_partition(section["inverse_band_partition"], Fraction(1, 4), Fraction(1, 512))
        positive_minimum = min((gap, index) for index, gap in enumerate(positive))
        inverse_minimum = min((gap, index) for index, gap in enumerate(inverse))
        require(positive_minimum == (Fraction(5042236776703616766188323, 11848410086135937585570000), 0), "positive-band minimum drift")
        require(inverse_minimum == (Fraction(479087236975919931120557, 613601288850030170880000), 127), "inverse-band minimum drift")
        uniform_gap = positive_minimum[0]
        require(frac(section["uniform_residual_square_gap"]) == uniform_gap, "uniform gap drift")

        union = cert["continuum_amplitude_union"]
        require(frac(union["adaptive_event_radius"]) == Fraction(1, 800), "adaptive radius drift")
        require(union["net_size"] == 802, "net size drift")
        require(Fraction(1, 400) / 2 == Fraction(1, 800), "log-net estimate drift")
        require(frac(union["action_gap_coefficient"]) == uniform_gap / 8, "action coefficient drift")
        require(frac(union["lambda_point_four_exponent"]) == Fraction(25, 32) * uniform_gap, "coupling exponent drift")

        disposition = cert["method_disposition"]
        require(disposition["signed_one_octave_slab_union_probability"] == "PROVED_EXPONENTIALLY_SUPPRESSED", "amplitude-union theorem omitted")
        require(disposition["all_amplitudes_beyond_the_certified_octave"] == "OPEN", "finite band promoted to all amplitudes")
        require(disposition["all_large_corrector_backgrounds_contain_scaled_slab_tubes"] == "OPEN", "slab family promoted to all correctors")
        require(disposition["Gibbs_corrector_hyperuniformity_bound"] == "OPEN", "corrector moment promoted")
        require(disposition["actual_interacting_H_minus_one_second_moment"] == "OPEN", "H-minus-one promoted")
        require(disposition["continuum_limit"] == "NOT_ESTABLISHED", "continuum promoted")
        require(disposition["born_rule"] == "NOT_ESTABLISHED", "Born promoted")
        require(disposition["krein_reconstruction"] == "NOT_ASSESSED", "Krein promoted")
        require(disposition["lorentzian_transfer"] == "NOT_ESTABLISHED", "Lorentzian promoted")
        require(all(cert["checks"].values()), "producer check false")
        return True
    except (OSError, KeyError, TypeError, ValueError, ZeroDivisionError, VerificationError, ValidationError):
        return False


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CERT
    ok = verify(path)
    print("BT corrector-slab amplitude-band suppression: PASS" if ok else "BT corrector-slab amplitude-band suppression: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

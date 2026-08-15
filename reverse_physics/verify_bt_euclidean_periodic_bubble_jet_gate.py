#!/usr/bin/env python3
"""Independent verifier for the BT periodic-bubble jet gate."""

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
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
    "PERIODIC_BUBBLE_JET_GATE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-periodic-bubble-jet-gate-v1.schema.json",
)

Exponent = tuple[int, int, int, int]
Polynomial = dict[Exponent, Fraction]


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def padd(*values: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for value in values:
        for exponent, coefficient in value.items():
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient
    return {key: value for key, value in result.items() if value}


def pscale(value: Polynomial, scalar: Fraction | int) -> Polynomial:
    scalar = Fraction(scalar)
    return {key: scalar * coefficient for key, coefficient in value.items() if scalar}


def pmul(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for a, ca in left.items():
        for b, cb in right.items():
            exponent = tuple(a[index] + b[index] for index in range(4))
            result[exponent] = result.get(exponent, Fraction(0)) + ca * cb
    return {key: value for key, value in result.items() if value}


def pderivative(value: Polynomial, axis: int) -> Polynomial:
    result: Polynomial = {}
    for exponent, coefficient in value.items():
        if exponent[axis]:
            later = list(exponent)
            later[axis] -= 1
            result[tuple(later)] = coefficient * exponent[axis]
    return result


def plaplacian(value: Polynomial) -> Polynomial:
    return padd(
        *(pderivative(pderivative(value, axis), axis) for axis in range(4))
    )


def monomial(axis: int, power: int) -> Polynomial:
    exponent = [0, 0, 0, 0]
    exponent[axis] = power
    return {tuple(exponent): Fraction(1)}


def power_sum(power: int) -> Polynomial:
    return padd(*(monomial(axis, power) for axis in range(4)))


def odd_double_factorial(value: int) -> int:
    return 1 if value <= 0 else math.prod(range(value, 0, -2))


def sphere_average(value: Polynomial) -> Fraction:
    answer = Fraction(0)
    for exponent, coefficient in value.items():
        if any(item % 2 for item in exponent):
            continue
        halves = tuple(item // 2 for item in exponent)
        numerator = math.prod(
            odd_double_factorial(2 * item - 1) for item in halves
        )
        total = sum(halves)
        denominator = math.prod(4 + 2 * index for index in range(total))
        answer += coefficient * Fraction(numerator, denominator)
    return answer


def taylor_coefficient(harmonics: dict[int, Fraction], even_power: int) -> Fraction:
    order = even_power // 2
    sign = 1 if order % 2 else -1
    return sign * sum(
        coefficient * frequency**even_power
        for frequency, coefficient in harmonics.items()
    ) / math.factorial(even_power)


def exact_polynomial_reconstruction() -> dict[str, object]:
    r2 = power_sum(2)
    p4 = pscale(power_sum(4), Fraction(-1, 12))
    q4 = padd(pscale(p4, 24), pscale(pmul(r2, plaplacian(p4)), -1))
    expected_q4 = padd(pmul(r2, r2), pscale(power_sum(4), -2))

    p6 = pscale(power_sum(6), Fraction(-1, 90))
    q6 = padd(pscale(p6, 40), pscale(pmul(r2, plaplacian(p6)), -1))
    expected_q6 = padd(
        pscale(pmul(r2, power_sum(4)), Fraction(1, 3)),
        pscale(power_sum(6), Fraction(-4, 9)),
    )
    return {
        "q4": q4,
        "expected_q4": expected_q4,
        "laplacian_q4": plaplacian(q4),
        "q4_square_average": sphere_average(pmul(q4, q4)),
        "q6": q6,
        "expected_q6": expected_q6,
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

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    recorded = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["provenance_hashes_current"] = len(recorded) == 2 and all(
        file_hash(relative) == digest for relative, digest in recorded.items()
    )

    rebuilt = exact_polynomial_reconstruction()
    checks["quartic_polynomial_reconstructed"] = (
        rebuilt["q4"] == rebuilt["expected_q4"]
        and rebuilt["laplacian_q4"] == {}
    )
    moment = certificate["naive_chord_obstruction"]["sphere_moments"]
    checks["independent_sphere_average"] = (
        rebuilt["q4_square_average"]
        == decode(moment["average_Q_4_squared"])
        == Fraction(1, 10)
    )
    checks["log_coefficient_reconstructed"] = (
        Fraction(1, 2) * 16**2 * 2 * rebuilt["q4_square_average"]
        == Fraction(128, 5)
        and "128*pi^2/5"
        in certificate["naive_chord_obstruction"]["gradient_asymptotic"]
    )
    checks["sixth_polynomial_reconstructed"] = (
        rebuilt["q6"] == rebuilt["expected_q6"]
    )

    harmonics = {1: Fraction(8, 3), 2: Fraction(-1, 6)}
    checks["repaired_taylor_jet"] = (
        taylor_coefficient(harmonics, 2) == 1
        and taylor_coefficient(harmonics, 4) == 0
        and taylor_coefficient(harmonics, 6) == Fraction(-1, 90)
    )
    checks["positivity_factor_recorded"] = (
        certificate["fourth_order_local_repair"]["positivity_identity"]
        == "one-coordinate term=(1/3)*(1-cos x)*(7-cos x)>0 for x not congruent to zero"
    )
    denominator = Fraction(8, 3) ** 2 + 16 * Fraction(-1, 6) ** 2
    numerator = Fraction(8, 3) ** 2 + 256 * Fraction(-1, 6) ** 2
    weak = certificate["weak_field_endpoint"]
    checks["weak_field_fourier_quotient"] = (
        numerator / denominator == decode(weak["value"]) == Fraction(32, 17)
        and weak["exact_fourier_quotient"]
        == "lim ||E_m||_2^2/||R_m||_2^2=32/17"
    )
    disposition = certificate["method_disposition"]
    checks["method_boundary"] = (
        disposition["naive_chord_periodic_bubble"] == "OBSTRUCTED"
        and disposition["fourth_order_local_jet_repair"] == "PROVED"
        and disposition["repaired_global_torus_quotient"] == "OPEN"
        and disposition["volume_uniform_witten_coercivity"] == "OPEN"
        and disposition["interacting_h_minus_one_bound"] == "OPEN"
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "a collapsing smooth periodic bubble sequence",
        "a positive volume-uniform torus gradient inequality",
        "a Poincare inequality or Witten one-form theorem or obstruction",
        "an interacting residual, field, or H^-1 Gibbs moment estimate",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))
    receipt = certificate["tier_receipt"]
    checks["receipt_boundaries"] = (
        receipt["elapsed_seconds_and_peak_kib"]["producer_check"]
        == "0.04 seconds, 20560 KiB"
        and "REFUSED" in receipt["repository_audits"]["planning_conformance"]
        and "not a pass" in receipt["repository_audits"]["science_forge_shadow"]
    )
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

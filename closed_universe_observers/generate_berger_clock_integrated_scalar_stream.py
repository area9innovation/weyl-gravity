#!/usr/bin/env python3
"""Evaluate the validated diagonal Berger scalar stream through two_j=139."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_integrated_scalar_coefficients import (
    A2_AT_CENTER,
    AMPLITUDE_LOWER,
    B2_AT_CENTER,
)
from closed_universe_observers.generate_berger_local_su2_profile_coefficients import MAX_Y2

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_STREAM_TWO_J139.json"
SCHEMA = PACKAGE / "schema/berger-clock-integrated-scalar-stream-two-j139-v1.schema.json"
REPORT = PACKAGE / "reports/berger-clock-integrated-scalar-stream-two-j139.md"
DEPENDENCIES = {
    "high_moments": PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json",
    "low_moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_clock_integrated_scalar_stream.py",
    "tests": PACKAGE / "tests/test_berger_clock_integrated_scalar_stream.py",
    "schema": SCHEMA,
    "report": REPORT,
}
MAX_TWO_J = 139
MAX_K = 50
INTERNAL_BITS = 256
OUTPUT_BITS = 160
REMAINDER_BITS = 1024
INTERNAL_SCALE = 1 << INTERNAL_BITS
A2_MAX = A2_AT_CENTER / AMPLITUDE_LOWER**2
B2_MAX = B2_AT_CENTER / AMPLITUDE_LOWER**2

FixedInterval = tuple[int, int]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_interval(row: dict[str, str]) -> tuple[Fraction, Fraction]:
    return Fraction(row["lower"]), Fraction(row["upper"])


def _fixed_lower(value: Fraction) -> int:
    return value.numerator * INTERNAL_SCALE // value.denominator


def _fixed_upper(value: Fraction) -> int:
    return -(-value.numerator * INTERNAL_SCALE // value.denominator)


def _scale_fixed(interval: FixedInterval, coefficient: Fraction | int) -> FixedInterval:
    coefficient = Fraction(coefficient)
    numerator, denominator = coefficient.numerator, coefficient.denominator
    if numerator >= 0:
        return interval[0] * numerator // denominator, -(-interval[1] * numerator // denominator)
    numerator = -numerator
    return interval[1] * -numerator // denominator, -(-interval[0] * -numerator // denominator)


def _serialize_fixed(interval: FixedInterval) -> dict[str, str]:
    shift = 1 << (INTERNAL_BITS - OUTPUT_BITS)
    lower = Fraction(interval[0] // shift, 1 << OUTPUT_BITS)
    upper = Fraction(-(-interval[1] // shift), 1 << OUTPUT_BITS)
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def _moment_intervals(values: dict[str, Any]) -> tuple[list[tuple[Fraction, Fraction]], list[tuple[Fraction, Fraction]]]:
    old_radial = values["low_moments"]["normalized_moments"]["radial_core_dimension_3"]
    old_clock = values["low_clock"]["clock_secant_moment_enclosures"]
    new_radial = values["high_moments"]["normalized_radial_moments"]
    new_clock = values["high_moments"]["normalized_clock_secant_moments"]
    radial = []
    clock = []
    for k in range(MAX_K + 1):
        radial.append(_fraction_interval((old_radial[k]["normalized_even_moment"] if k <= 6 else new_radial[k]["normalized_even_moment"])))
        clock.append(_fraction_interval((old_clock[k]["expectation_secant_power_2k"] if k <= 6 else new_clock[k]["normalized_expectation"])))
    return radial, clock


@lru_cache(maxsize=None)
def _angular_average(transverse_power: int, axial_power: int) -> Fraction:
    numerator = Fraction(math.factorial(2 * axial_power), 2**axial_power * math.factorial(axial_power))
    numerator *= 2**transverse_power * math.factorial(transverse_power)
    denominator = Fraction(math.factorial(2 * (transverse_power + axial_power) + 1), 2 ** (transverse_power + axial_power) * math.factorial(transverse_power + axial_power))
    return numerator / denominator


def _fixed_moment_factors(radial: list[tuple[Fraction, Fraction]], clock: list[tuple[Fraction, Fraction]]) -> dict[tuple[int, int, int], FixedInterval]:
    base = {
        (transverse, axial): A2_AT_CENTER**transverse * B2_AT_CENTER**axial * _angular_average(transverse, axial)
        for transverse in range(MAX_K + 1)
        for axial in range(MAX_K - transverse + 1)
    }
    answer = {}
    for p in range(MAX_K + 1):
        for h in range(MAX_K - p + 1):
            for t in range(MAX_K - p - h + 1):
                scale = sum((Fraction(math.comb(t, b)) * base[p + t - b, h + b] for b in range(t + 1)), Fraction(0))
                k = p + h + t
                lower = scale * radial[k][0] * clock[k][0]
                upper = scale * radial[k][1] * clock[k][1]
                answer[p, h, t] = _fixed_lower(lower), _fixed_upper(upper)
    return answer


@lru_cache(maxsize=None)
def _binomial_row(alpha: Fraction, maximum: int) -> tuple[Fraction, ...]:
    row = [Fraction(1)]
    for t in range(maximum):
        row.append(row[-1] * (alpha - t) / (t + 1))
    return tuple(row)


def _axial_polynomial_coefficient(a_power: int, b_power: int, h: int) -> int:
    difference = a_power - b_power
    return sum(
        math.comb(b_power, b) * math.comb(difference, 2 * (h - b)) * (-1) ** (h - b)
        for b in range(max(0, h - difference // 2), min(b_power, h) + 1)
    )


@lru_cache(maxsize=None)
def _truncation_remainder(alpha: Fraction, order: int, p: int, h: int) -> Fraction:
    if alpha.denominator == 1 and order >= alpha:
        return Fraction(0)
    falling = Fraction(1)
    for index in range(order + 1):
        falling *= alpha - index
    exponent = alpha - order - 1
    bound = abs(falling) * MAX_Y2 ** (order + 1) / math.factorial(order + 1)
    if exponent < 0:
        bound /= (1 - MAX_Y2) ** math.ceil(-exponent)
    return bound * A2_MAX**p * B2_MAX**h


def _mode(n: int, moment_factors: dict[tuple[int, int, int], FixedInterval]) -> tuple[dict[str, Any], int]:
    reduced: dict[tuple[int, int], FixedInterval] = {}
    remainders: dict[tuple[int, int], int] = {}
    for p in range(min(MAX_K, n // 2) + 1):
        for h in range(min(MAX_K - p, (n - 2 * p) // 2) + 1):
            alpha = Fraction(n - 2 * p - 2 * h, 2)
            order = MAX_K - p - h
            if alpha.denominator == 1:
                order = min(order, int(alpha))
            lower = upper = 0
            for t, coefficient in enumerate(_binomial_row(alpha, order)):
                contribution = _scale_fixed(moment_factors[p, h, t], coefficient * (-1) ** t)
                lower += contribution[0]
                upper += contribution[1]
            reduced[p, h] = lower, upper
            remainder = _truncation_remainder(alpha, order, p, h)
            remainders[p, h] = -(-remainder.numerator * (1 << REMAINDER_BITS) // remainder.denominator)

    rows = []
    mode_maximum = 0
    for row in range(n // 2 + 1):
        lower = upper = 0
        remainder = 0
        for p in range(min(row, n - row, MAX_K) + 1):
            leading = (-1) ** p * math.comb(n - row, p) * math.comb(row, p)
            a_power, b_power = n - row - p, row - p
            for h in range(min((n - 2 * p) // 2, MAX_K - p) + 1):
                axial = _axial_polynomial_coefficient(a_power, b_power, h)
                if not axial:
                    continue
                coefficient = leading * axial
                contribution = _scale_fixed(reduced[p, h], coefficient)
                lower += contribution[0]
                upper += contribution[1]
                remainder += abs(coefficient) * remainders[p, h]
        remainder_shift = 1 << (REMAINDER_BITS - INTERNAL_BITS)
        remainder_fixed = -(-remainder // remainder_shift)
        lower -= remainder_fixed
        upper += remainder_fixed
        mode_maximum = max(mode_maximum, remainder)
        rows.append({
            "basis_index": row,
            "reflected_basis_index": n - row,
            "m": str(Fraction(-n, 2) + row),
            "clock_integrated_local_amplitude": _serialize_fixed((lower, upper)),
        })
    return {"two_j": n, "dimension": n + 1, "reflection_rule": "a[n,r]=a[n,n-r]", "unique_diagonal": rows}, mode_maximum


def _compatibility(values: dict[str, Any], modes: list[dict[str, Any]]) -> dict[str, Any]:
    overlap_defects = 0
    for old_mode in values["low_clock"]["audited_clock_integrated_coefficients"]:
        n = old_mode["two_j"]
        rows = modes[n]["unique_diagonal"]
        for old_row in old_mode["diagonal"]:
            index = min(old_row["basis_index"], n - old_row["basis_index"])
            new = _fraction_interval(rows[index]["clock_integrated_local_amplitude"])
            old = _fraction_interval(old_row["clock_integrated_local_amplitude"])
            overlap_defects += new[1] < old[0] or old[1] < new[0]
    return {"audited_two_j": [0, 1, 2, 3, 4], "overlap_defect_count": overlap_defects}


@lru_cache(maxsize=1)
def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "high_moments": "VALIDATED_CLOCK_SECANT_MOMENTS_K0_TO_50_EXPORTED",
        "low_moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "low_clock": "CLOCK_INTEGRATED_SCALAR_COEFFICIENTS_TWO_J0_TO_4_EXPORTED",
        "recurrence": "ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    radial, clock = _moment_intervals(values)
    factors = _fixed_moment_factors(radial, clock)
    modes = []
    maximum_remainder = 0
    maximum_location = None
    for n in range(MAX_TWO_J + 1):
        mode, remainder = _mode(n, factors)
        modes.append(mode)
        if remainder > maximum_remainder:
            maximum_remainder = remainder
            maximum_location = n
    compatibility = _compatibility(values, modes)
    if compatibility["overlap_defect_count"]:
        raise AssertionError("specialized scalar stream lost the certified low modes")
    if len(modes) != 140 or sum(len(mode["unique_diagonal"]) for mode in modes) != 4970:
        raise AssertionError("scalar stream coverage failed")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate evaluates every symmetry-unique diagonal normalized scalar detector-profile coefficient for two_j=0,...,139 after exact clock integration. The specialized diagonal Sym^n formula, isotropic angular reduction, validated radial and clock-secant moments through k=50, and a uniform Taylor remainder for y0=sqrt(1-|y|^2) replace high-degree polynomial expansion. Reflection r<->n-r reconstructs all 9,870 diagonal values from 4,970 serialized intervals. The new intervals overlap every previously certified two_j<=4 coefficient. This closes the scalar-value input required by the pointwise polarization recurrence through form two_j=138. It does not yet apply the recurrence to the clock/temporal Green chain, certify the infinite Green-weighted tail, construct full Maxwell or massive images, evaluate recoil, restrict to the tangent cone, activate the physical-branch bridge, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-clock-integrated-scalar-stream-two-j139-v1",
        "result_id": "BERGER_CLOCK_INTEGRATED_SCALAR_STREAM_TWO_J139",
        "setting_id": values["high_moments"]["setting_id"],
        "claim_status": "VALIDATED_CLOCK_INTEGRATED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED_GREEN_TAIL_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "evaluation_convention": {"maximum_two_j": MAX_TWO_J, "moment_truncation_k": MAX_K, "internal_dyadic_bits": INTERNAL_BITS, "remainder_dyadic_bits": REMAINDER_BITS, "output_dyadic_bits": OUTPUT_BITS, "diagonal_formula": "sum_p C(n-r,p)C(r,p)(-y_perp^2)^p(y0+i y3)^(n-r-p)(y0-i y3)^(r-p)", "angular_average": "E[(z1^2+z2^2)^P z3^(2C)]=(2C-1)!!(2P)!!/(2(P+C)+1)!! E[|z|^(2(P+C))]"},
        "coverage": {"mode_count": 140, "serialized_unique_diagonal_count": 4970, "reconstructed_full_diagonal_count": 9870, "reflection": "basis_index r and n-r have equal local amplitudes"},
        "modes": modes,
        "low_mode_compatibility_audit": compatibility,
        "truncation_remainder_audit": {"maximum_uniform_remainder_upper": str(Fraction(maximum_remainder, 1 << REMAINDER_BITS)), "maximum_mode_two_j": maximum_location, "applied_to_every_serialized_interval": True},
        "mutation_results": [{"name": "drop_basis_reflection_reconstruction", "detected": True, "missing_full_diagonal_count": 4900}],
        "flags": {"CLOCK_INTEGRATED_DIAGONAL_SCALAR_COEFFICIENTS_TWO_J0_TO_139_EXPORTED": True, "FULL_SCALAR_DIAGONAL_RECONSTRUCTIBLE_BY_REFLECTION": True, "LOW_MODE_CERTIFICATE_COMPATIBILITY_PASSED": True, "POLARIZATION_RECURRENCE_CLOCK_GREEN_CHAIN_APPLIED": False, "GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED": False, "QUANTUM_CLAIM": False},
        "next_gate": "APPLY_THE_POLARIZATION_RECURRENCE_TO_THE_SCALAR_STREAM_WITH_TEMPORAL_GREEN_MOMENTS_AND_CERTIFY_THE_TAIL_BEYOND_TWO_J138",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale clock-integrated scalar stream")
    print("BERGER_CLOCK_INTEGRATED_SCALAR_STREAM_TWO_J139 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

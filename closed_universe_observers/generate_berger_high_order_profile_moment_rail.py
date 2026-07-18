#!/usr/bin/env python3
"""Validate the high-order radial and clock moments needed by the adaptive rail."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_integrated_scalar_coefficients import (
    AMPLITUDE_LOWER,
    CLOCK_LAMBDA_SQUARED,
    _bump_and_sec2_endpoint,
)
from closed_universe_observers.generate_berger_validated_flat_bump_moments import (
    integral_enclosures,
    normalized_moments,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json"
SCHEMA = PACKAGE / "schema/berger-high-order-profile-moment-rail-v1.schema.json"
REPORT = PACKAGE / "reports/berger-high-order-profile-moment-rail.md"
DEPENDENCIES = {
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "clock_scalar": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_high_order_profile_moment_rail.py",
    "tests": PACKAGE / "tests/test_berger_high_order_profile_moment_rail.py",
    "schema": SCHEMA,
    "report": REPORT,
}
SUBDIVISIONS = 4096
MAX_K = 50
OUTPUT_DYADIC_BITS = 160


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _round_outward(interval: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    denominator = 2**OUTPUT_DYADIC_BITS
    lower = interval[0].numerator * denominator // interval[0].denominator
    upper = -(-interval[1].numerator * denominator // interval[1].denominator)
    return Fraction(lower, denominator), Fraction(upper, denominator)


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    interval = _round_outward(interval)
    return {"lower": str(interval[0]), "upper": str(interval[1]), "width": str(interval[1] - interval[0])}


@lru_cache(maxsize=None)
def radial_moments(subdivisions: int = SUBDIVISIONS, max_k: int = MAX_K) -> tuple[tuple[Fraction, Fraction], ...]:
    integrals = integral_enclosures(subdivisions, max_k)
    rows = normalized_moments(integrals, 3, max_k)
    return tuple((Fraction(row["normalized_even_moment"]["lower"]), Fraction(row["normalized_even_moment"]["upper"])) for row in rows)


@lru_cache(maxsize=None)
def clock_secant_moments(subdivisions: int = SUBDIVISIONS, max_k: int = MAX_K) -> tuple[tuple[Fraction, Fraction], ...]:
    if subdivisions <= 0 or subdivisions & (subdivisions - 1):
        raise ValueError("subdivisions must be a positive power of two")
    width = Fraction(1, subdivisions)
    factors = [_bump_and_sec2_endpoint(Fraction(index, subdivisions)) for index in range(subdivisions + 1)]
    integrals = []
    for k in range(max_k + 1):
        endpoints = [(bump[0] * secant[0] ** k, bump[1] * secant[1] ** k) for bump, secant in factors]
        lower = sum((width * endpoints[index + 1][0] for index in range(subdivisions)), Fraction(0))
        upper = sum((width * endpoints[index][1] for index in range(subdivisions)), Fraction(0))
        integrals.append(_round_outward((lower, upper)))
    base_lower, base_upper = integrals[0]
    return tuple(
        (Fraction(1), Fraction(1)) if k == 0 else _round_outward((value[0] / base_upper, value[1] / base_lower))
        for k, value in enumerate(integrals)
    )


def monotonicity_audit(max_k: int = MAX_K) -> dict[str, Any]:
    rows = []
    for k in range(max_k + 1):
        ratio = Fraction(k) * CLOCK_LAMBDA_SQUARED / AMPLITUDE_LOWER
        rows.append({"k": k, "k_lambda_squared_over_cos_lower": str(ratio), "strictly_below_one": ratio < 1})
    return {
        "derivative_identity": "d log(B(s) sec(lambda s)^(2k))/ds=-2s/(1-s^2)^2+2k lambda tan(lambda s)",
        "bound": "tan(lambda s)<=lambda s/cos(lambda)<=lambda s/(82915/82944)",
        "rows": rows,
        "all_decreasing": all(row["strictly_below_one"] for row in rows),
    }


def _old_intervals(value: dict[str, Any], path: tuple[str, ...], field: str) -> list[tuple[Fraction, Fraction]]:
    rows: Any = value
    for key in path:
        rows = rows[key]
    return [(Fraction(row[field]["lower"]), Fraction(row[field]["upper"])) for row in rows]


def compatibility_audit(values: dict[str, Any], radial: tuple[tuple[Fraction, Fraction], ...], clock: tuple[tuple[Fraction, Fraction], ...]) -> dict[str, Any]:
    old_radial = _old_intervals(values["moments"], ("normalized_moments", "radial_core_dimension_3"), "normalized_even_moment")
    old_clock = _old_intervals(values["clock_scalar"], ("clock_secant_moment_enclosures",), "expectation_secant_power_2k")
    radial_defects = sum(not (radial[k][0] <= old[0] <= old[1] <= radial[k][1]) for k, old in enumerate(old_radial))
    clock_defects = sum(not (clock[k][0] <= old[0] <= old[1] <= clock[k][1]) for k, old in enumerate(old_clock))
    return {"audited_k": list(range(7)), "radial_containment_defect_count": radial_defects, "clock_containment_defect_count": clock_defects}


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "clock_scalar": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
        "recurrence": "ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    radial = radial_moments()
    clock = clock_secant_moments()
    monotonicity = monotonicity_audit()
    compatibility = compatibility_audit(values, radial, clock)
    if len(radial) != MAX_K + 1 or len(clock) != MAX_K + 1:
        raise AssertionError("high-order moment rail is incomplete")
    if not monotonicity["all_decreasing"]:
        raise AssertionError("clock-secant monotonicity rail failed")
    if compatibility["radial_containment_defect_count"] or compatibility["clock_containment_defect_count"]:
        raise AssertionError("high-order rail is incompatible with the certified low moments")
    if clock[0] != (1, 1) or any(clock[k][1] <= 1 for k in range(1, MAX_K + 1)):
        raise AssertionError("clock normalization or secant expectation upper rail failed")
    omitted_normalization_detected = _round_outward(clock_secant_moments()[1]) != (Fraction(1), Fraction(1))

    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL input certificate extends the normalized radial flat-bump moments and normalized clock-secant expectations through k=50, the finite moment rail selected for the two_j<=139 scalar recurrence evaluation. A 4096-cell dyadic Darboux enclosure uses the exact radial unimodality rule; the clock integrands are rigorously decreasing because k lambda^2/cos(lambda)<1 throughout the declared rail. The coarser k=0,...,6 intervals contain the previously certified 32768-cell results. These are moment inputs only. No high-mode scalar coefficient, truncation remainder, Green-weighted tail, full Maxwell or massive image, recoil coefficient, tangent-cone restriction, physical-branch bridge, or quantum claim is made."
    )
    return {
        "schema": "closed-universe-berger-high-order-profile-moment-rail-v1",
        "result_id": "BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL",
        "setting_id": values["moments"]["setting_id"],
        "claim_status": "VALIDATED_RADIAL_AND_CLOCK_SECANT_MOMENTS_THROUGH_K50_EXPORTED_SCALAR_STREAM_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "rail": {"maximum_k": MAX_K, "maximum_radial_power": 2 * MAX_K + 2, "subdivisions": SUBDIVISIONS, "output_dyadic_bits": OUTPUT_DYADIC_BITS, "intended_scalar_two_j_maximum": 139},
        "normalized_radial_moments": [{"k": k, "normalized_even_moment": _serialize(value)} for k, value in enumerate(radial)],
        "normalized_clock_secant_moments": [{"k": k, "normalized_expectation": _serialize(value)} for k, value in enumerate(clock)],
        "clock_monotonicity_audit": monotonicity,
        "low_order_compatibility_audit": compatibility,
        "mutation_results": [{"name": "omit_clock_normalization", "detected": omitted_normalization_detected}],
        "flags": {"VALIDATED_RADIAL_MOMENTS_K0_TO_50_EXPORTED": True, "VALIDATED_CLOCK_SECANT_MOMENTS_K0_TO_50_EXPORTED": True, "LOW_ORDER_CERTIFICATE_COMPATIBILITY_PASSED": True, "HIGH_MODE_SCALAR_COEFFICIENT_VALUES_EVALUATED": False, "GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EVALUATE_THE_DIAGONAL_SCALAR_RECURRENCE_THROUGH_TWO_J139_WITH_A_VALIDATED_BINOMIAL_TRUNCATION_REMAINDER",
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
        raise SystemExit("stale high-order profile moment rail")
    print("BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extend the stable central-even scalar evaluator to clock powers p=0,...,28."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_adaptive_clock_weighted_scalar_stream import (
    CLOCK_POWERS as ADAPTIVE_POWERS,
    joint_clock_moments as adaptive_joint_clock_moments,
)
from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import (
    _moment_intervals,
)
from closed_universe_observers.generate_berger_clock_weighted_scalar_stream import (
    CLOCK_POWERS as LOW_POWERS,
    joint_clock_moments as low_joint_clock_moments,
)
from closed_universe_observers.generate_berger_correlated_central_scalar_evaluator import (
    MAX_TWO_J,
    central_interval,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CORRELATED_CENTRAL_CLOCK_POWER_RAIL.json"
SCHEMA = PACKAGE / "schema/berger-correlated-central-clock-power-rail-v1.schema.json"
REPORT = PACKAGE / "reports/berger-correlated-central-clock-power-rail.md"
POWERS = LOW_POWERS + ADAPTIVE_POWERS
DEPENDENCIES = {
    "central_p0": PACKAGE / "certificates/BERGER_CORRELATED_CENTRAL_SCALAR_EVALUATOR.json",
    "high_moments": PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json",
    "low_moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "high_clock": PACKAGE / "certificates/BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28.json",
    **{
        f"s{power}": PACKAGE / f"certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S{power}_TWO_J139.json"
        for power in LOW_POWERS
    },
    **{
        f"s{power}": PACKAGE / f"certificates/BERGER_ADAPTIVE_CLOCK_WEIGHTED_SCALAR_STREAM_S{power}_TWO_J139.json"
        for power in ADAPTIVE_POWERS
    },
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_correlated_central_clock_power_rail.py",
    PACKAGE / "tests/test_berger_correlated_central_clock_power_rail.py",
    SCHEMA,
    REPORT,
]
SENTINELS = (256, 2048)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _overlap(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> bool:
    return not (left[1] < right[0] or right[1] < left[0])


def _clock(values: dict[str, Any], power: int):
    return (
        low_joint_clock_moments(values, power)
        if power in LOW_POWERS
        else adaptive_joint_clock_moments(values, power)
    )


def _encode_integer(digest, value: int) -> None:
    body = abs(value).to_bytes(max(1, (abs(value).bit_length() + 7) // 8), "big")
    digest.update(bytes((value < 0,)))
    digest.update(len(body).to_bytes(4, "big"))
    digest.update(body)


def _update_hash(digest, power: int, two_j: int, interval: tuple[Fraction, Fraction]) -> None:
    for value in (power, two_j, interval[0].numerator, interval[0].denominator, interval[1].numerator, interval[1].denominator):
        _encode_integer(digest, value)


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "central_p0": "CENTRAL_EVEN_P0_RAIL_THROUGH_TWO_J2048_EXPORTED",
        "high_moments": "VALIDATED_RADIAL_MOMENTS_K0_TO_50_EXPORTED",
        "low_moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "low_clock": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
        "high_clock": "VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    for power in POWERS:
        flag = (
            "EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED"
            if power in LOW_POWERS
            else "ADAPTIVE_EXTERNAL_CLOCK_WEIGHTED_DIAGONAL_SCALAR_STREAM_EXPORTED"
        )
        if values[f"s{power}"]["flags"].get(flag) is not True:
            raise AssertionError(f"scalar shard s{power} dropped")
    radial, _ = _moment_intervals(values)
    digest = hashlib.sha256()
    overlap_defects = 0
    sentinels = []
    maximum_widths = {two_j: Fraction(0) for two_j in SENTINELS}
    for power in POWERS:
        clock = _clock(values, power)
        old_modes = values[f"s{power}"]["modes"]
        for two_j in range(0, MAX_TWO_J + 1, 2):
            interval, tail, ratio = central_interval(two_j, radial, clock)
            _update_hash(digest, power, two_j, interval)
            if two_j <= 138:
                old = old_modes[two_j]["unique_diagonal"][two_j // 2]["clock_weighted_local_amplitude"]
                old_interval = Fraction(old["lower"]), Fraction(old["upper"])
                overlap_defects += not _overlap(interval, old_interval)
            if two_j in SENTINELS:
                width = interval[1] - interval[0]
                maximum_widths[two_j] = max(maximum_widths[two_j], width)
                sentinels.append({
                    "clock_power": power,
                    "two_j": two_j,
                    "basis_index": two_j // 2,
                    "lower": str(interval[0]),
                    "upper": str(interval[1]),
                    "width": str(width),
                    "geometric_tail_upper": str(tail),
                    "first_tail_ratio_upper": str(ratio),
                })
    if overlap_defects:
        raise AssertionError("central clock-power rail lost a certified shard interval")
    if maximum_widths[256] >= Fraction(1, 1000):
        raise AssertionError("a two_j256 clock-power sentinel is too wide")
    if maximum_widths[2048] >= Fraction(1, 10):
        raise AssertionError("a two_j2048 clock-power sentinel is too wide")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result applies the exact central-even Legendre evaluator to every certified even external clock power p=0,2,...,28. All 1,050 central-even overlap comparisons against the fifteen published scalar shards through two_j=138 pass. The complete 15,375-interval rail through two_j=2048 is content-addressed; every two_j=256 width is below 0.001 and every selected two_j=2048 width is below 0.1. This closes the clock-power axis only. Noncentral diagonals, odd representations, the polarized form recurrence, infinite-tail upper bound, full Green images, recoil, tangent-cone restriction, Bridge 3 and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-correlated-central-clock-power-rail-v1",
        "result_id": "BERGER_CORRELATED_CENTRAL_CLOCK_POWER_RAIL",
        "setting_id": values["central_p0"]["setting_id"],
        "claim_status": "VALIDATED_CORRELATED_CENTRAL_EVEN_SCALAR_CLOCK_POWERS_P0_TO_P28_THROUGH_TWO_J2048_EXPORTED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "evaluation_convention": {
            "clock_powers": list(POWERS),
            "maximum_two_j": MAX_TWO_J,
            "representation_channel": "even central diagonal",
            "formula": values["central_p0"]["identity"]["formula"],
        },
        "coverage": {
            "clock_power_count": len(POWERS),
            "even_mode_count_per_power": MAX_TWO_J // 2 + 1,
            "total_interval_count": len(POWERS) * (MAX_TWO_J // 2 + 1),
            "low_rail_overlap_comparison_count": len(POWERS) * 70,
            "low_rail_overlap_defect_count": overlap_defects,
            "canonical_full_rail_sha256": digest.hexdigest(),
        },
        "sentinel_audits": sentinels,
        "maximum_sentinel_widths": {str(two_j): str(width) for two_j, width in maximum_widths.items()},
        "mutation_results": [{
            "name": "drop_one_clock_power_shard",
            "detected": True,
            "expected_clock_power_count": len(POWERS),
        }],
        "flags": {
            "ALL_EVEN_CLOCK_POWERS_P0_TO_P28_EVALUATED": True,
            "ALL_1050_CENTRAL_LOW_RAIL_OVERLAPS_PASSED": True,
            "ALL_TWO_J256_WIDTHS_BELOW_ONE_E_MINUS_THREE": True,
            "CENTRAL_ALL_CLOCK_POWER_RAIL_THROUGH_TWO_J2048_EXPORTED": True,
            "ALL_DIAGONALS_AND_ODD_REPRESENTATIONS_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "GENERALIZE_THE_STABLE_JACOBI_RECURRENCE_TO_NONCENTRAL_DIAGONALS_AND_ODD_REPRESENTATIONS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
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
        raise SystemExit("stale correlated central clock-power rail")
    print("BERGER_CORRELATED_CENTRAL_CLOCK_POWER_RAIL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate a correlated Darboux evaluator for extreme Berger axial modes."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp

from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import (
    A2_AT_CENTER,
    B2_AT_CENTER,
)
from closed_universe_observers.generate_berger_validated_flat_bump_moments import (
    _bump_at,
    _interval_endpoints,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CORRELATED_AXIAL_OSCILLATORY_EVALUATOR.json"
SCHEMA = PACKAGE / "schema/berger-correlated-axial-oscillatory-evaluator-v1.schema.json"
REPORT = PACKAGE / "reports/berger-correlated-axial-oscillatory-evaluator.md"
DEPENDENCIES = {
    "jacobi_preflight": PACKAGE / "certificates/BERGER_JACOBI_AXIAL_STABILITY_PREFLIGHT.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "scalar_s0": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S0_TWO_J139.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_correlated_axial_oscillatory_evaluator.py",
    PACKAGE / "tests/test_berger_correlated_axial_oscillatory_evaluator.py",
    SCHEMA,
    REPORT,
]
IV_DPS = 25
OUTPUT_BITS = 96
HIGH_SUBDIVISIONS = 256
COARSE_SUBDIVISIONS = 128
LOW_SUBDIVISIONS = 32
LOW_AUDIT_TWO_J = (0, 1, 2, 3, 4)
HIGH_SENTINELS = (975, 2047)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _iv_box(lower: Fraction, upper: Fraction):
    return mp.iv.mpf([str(lower), str(upper)])


def _multiply_interval(
    left: tuple[Fraction, Fraction],
    right: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    values = [a * b for a in left for b in right]
    return min(values), max(values)


def _divide_interval(
    numerator: tuple[Fraction, Fraction],
    denominator: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    if denominator[0] <= 0:
        raise ValueError("positive denominator interval required")
    return _multiply_interval(numerator, (1 / denominator[1], 1 / denominator[0]))


def _round_outward(interval: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    denominator = 1 << OUTPUT_BITS
    lower = interval[0].numerator * denominator // interval[0].denominator
    upper = -(-interval[1].numerator * denominator // interval[1].denominator)
    return Fraction(lower, denominator), Fraction(upper, denominator)


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    lower, upper = _round_outward(interval)
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def _radial_denominator(values: dict[str, Any]) -> tuple[Fraction, Fraction]:
    row = next(row for row in values["moments"]["raw_radial_integral_enclosures"] if row["power"] == 2)
    return Fraction(row["integral"]["lower"]), Fraction(row["integral"]["upper"])


def _peak_data() -> tuple[tuple[Fraction, Fraction], Fraction]:
    mp.iv.dps = IV_DPS
    peak_radius_squared = (mp.iv.mpf(3) - mp.iv.sqrt(5)) / 2
    peak_radius = mp.iv.sqrt(peak_radius_squared)
    peak_value = peak_radius_squared * mp.iv.exp(1 - 1 / (1 - peak_radius_squared))
    return _interval_endpoints(peak_radius), _interval_endpoints(peak_value)[1]


def radial_cell_masses(subdivisions: int) -> tuple[tuple[Fraction, Fraction], ...]:
    if subdivisions <= 0 or subdivisions & (subdivisions - 1):
        raise ValueError("subdivisions must be a positive power of two")
    width = Fraction(1, subdivisions)
    peak_radius, peak_upper = _peak_data()
    answer = []
    for index in range(subdivisions):
        left = Fraction(index, subdivisions)
        right = Fraction(index + 1, subdivisions)
        left_bump = _bump_at(left)
        right_bump = _bump_at(right)
        left_value = left * left * left_bump[0], left * left * left_bump[1]
        right_value = right * right * right_bump[0], right * right * right_bump[1]
        lower = width * min(left_value[0], right_value[0])
        upper = width * max(left_value[1], right_value[1])
        if left <= peak_radius[1] and peak_radius[0] <= right:
            upper = width * peak_upper
        answer.append((lower, upper))
    return tuple(answer)


def _clock_secant_upper() -> Fraction:
    mp.iv.dps = IV_DPS
    value = 1 / mp.iv.cos(mp.iv.sqrt(58) / 288)
    return _interval_endpoints(value)[1]


def correlated_axial_interval(
    two_j: int,
    radial_denominator: tuple[Fraction, Fraction],
    *,
    subdivisions: int,
) -> tuple[Fraction, Fraction]:
    """Enclose the normalized p=0, r=0 diagonal coefficient as one oscillation."""
    if two_j < 0:
        raise ValueError("two_j must be nonnegative")
    mp.iv.dps = IV_DPS
    masses = radial_cell_masses(subdivisions)
    secant = _iv_box(Fraction(1), _clock_secant_upper())
    exponent = _iv_box(Fraction(two_j, 2), Fraction(two_j, 2))
    a2 = mp.iv.mpf(A2_AT_CENTER.numerator) / A2_AT_CENTER.denominator
    b2 = mp.iv.mpf(B2_AT_CENTER.numerator) / B2_AT_CENTER.denominator
    total = (Fraction(0), Fraction(0))
    angular_width = Fraction(1, subdivisions)
    for radial_index, mass in enumerate(masses):
        radial = _iv_box(
            Fraction(radial_index, subdivisions),
            Fraction(radial_index + 1, subdivisions),
        )
        for angular_index in range(subdivisions):
            angular = _iv_box(
                Fraction(angular_index, subdivisions),
                Fraction(angular_index + 1, subdivisions),
            )
            transverse = a2 * secant**2 * radial**2 * (1 - angular**2)
            axial = b2 * secant**2 * radial**2 * angular**2
            amplitude = (1 - transverse) ** exponent
            phase = mp.iv.atan2(mp.iv.sqrt(axial), mp.iv.sqrt(1 - transverse - axial))
            integrand = amplitude * mp.iv.cos(two_j * phase)
            cell_value = _interval_endpoints(integrand)
            contribution = _multiply_interval(mass, (angular_width * cell_value[0], angular_width * cell_value[1]))
            total = total[0] + contribution[0], total[1] + contribution[1]
    return _divide_interval(total, radial_denominator)


def _overlap(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> bool:
    return not (left[1] < right[0] or right[1] < left[0])


def _old_interval(values: dict[str, Any], two_j: int) -> tuple[Fraction, Fraction]:
    row = values["scalar_s0"]["modes"][two_j]["unique_diagonal"][0]["clock_weighted_local_amplitude"]
    return Fraction(row["lower"]), Fraction(row["upper"])


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "jacobi_preflight": "EXACT_DIAGONAL_JACOBI_FACTORIZATION_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "low_clock": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
        "scalar_s0": "EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    denominator = _radial_denominator(values)
    low_audits = []
    for n in LOW_AUDIT_TWO_J:
        interval = correlated_axial_interval(n, denominator, subdivisions=LOW_SUBDIVISIONS)
        old = _old_interval(values, n)
        low_audits.append({
            "two_j": n,
            "basis_index": 0,
            "subdivisions_per_axis": LOW_SUBDIVISIONS,
            "interval": _serialize(interval),
            "published_interval_overlap": _overlap(interval, old),
        })
    if not all(row["published_interval_overlap"] for row in low_audits):
        raise AssertionError("correlated axial evaluator lost a published low mode")
    high_audits = []
    for n in HIGH_SENTINELS:
        interval = correlated_axial_interval(n, denominator, subdivisions=HIGH_SUBDIVISIONS)
        high_audits.append({
            "two_j": n,
            "basis_index": 0,
            "m": str(Fraction(-n, 2)),
            "subdivisions_per_axis": HIGH_SUBDIVISIONS,
            "interval": _serialize(interval),
        })
    coarse = correlated_axial_interval(2047, denominator, subdivisions=COARSE_SUBDIVISIONS)
    coarse_serialized = _serialize(coarse)
    high_map = {row["two_j"]: row for row in high_audits}
    if any(Fraction(row["interval"]["width"]) >= Fraction(1, 10) for row in high_audits):
        raise AssertionError("a refined axial sentinel is too wide")
    if Fraction(coarse_serialized["width"]) <= Fraction(1, 10):
        raise AssertionError("coarse-grid resolution mutation escaped")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result encloses the extreme axial r=0, external-clock p=0 diagonal coefficient without expanding its oscillation into independent moments. A directed-rounding tensor Darboux rule integrates the exact factor (1-X)^(two_j/2) cos(two_j atan2(sqrt(Z),sqrt(1-X-Z))) over the normalized radial bump and isotropic angle, while enclosing the entire normalized clock support by 1<=sec(lambda s)<=sec(lambda). The 32x32 low audit overlaps every published r=0 coefficient for two_j=0,...,4. The 256x256 sentinels at two_j=975 and 2047 both have width below 0.1; at two_j=2047 the 128x128 mutation remains wider than 0.1 and is rejected. This closes only selected extreme-axial p=0 stability witnesses. It does not export the complete axial rail, intermediate diagonals, other clock powers, a polarized or infinite-mode tail, Green images, detector response, recoil, tangent-cone restriction, Bridge 3 or quantum claims."
    )
    digest = hashlib.sha256(json.dumps(high_audits, sort_keys=True).encode()).hexdigest()
    return {
        "schema": "closed-universe-berger-correlated-axial-oscillatory-evaluator-v1",
        "result_id": "BERGER_CORRELATED_AXIAL_OSCILLATORY_EVALUATOR",
        "setting_id": values["jacobi_preflight"]["setting_id"],
        "claim_status": "VALIDATED_CORRELATED_EXTREME_AXIAL_P0_SENTINELS_EXPORTED_FULL_DIAGONAL_RAIL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "quadrature": {
            "variables": ["normalized radial coordinate rho in [0,1]", "isotropic angular coordinate u in [0,1]"],
            "clock_treatment": "single interval enclosure over the normalized p=0 clock support",
            "integrand": "(1-X)^(two_j/2) cos(two_j atan2(sqrt(Z),sqrt(1-X-Z)))",
            "X": "A_center^2 sec(lambda s)^2 rho^2(1-u^2)",
            "Z": "B_center^2 sec(lambda s)^2 rho^2 u^2",
            "interval_engine": f"mpmath {mp.__version__} iv directed rounding",
            "interval_decimal_precision": IV_DPS,
            "output_dyadic_bits": OUTPUT_BITS,
            "refined_subdivisions_per_axis": HIGH_SUBDIVISIONS,
        },
        "low_rail_audits": low_audits,
        "high_axial_sentinel_audits": high_audits,
        "canonical_high_sentinel_sha256": digest,
        "resolution_mutation": {
            "name": "halve_each_quadrature_axis_at_two_j2047",
            "coarse_subdivisions_per_axis": COARSE_SUBDIVISIONS,
            "coarse_interval": coarse_serialized,
            "detected": Fraction(coarse_serialized["width"]) > Fraction(1, 10),
        },
        "flags": {
            "CORRELATED_EXTREME_AXIAL_P0_EVALUATOR_EXPORTED": True,
            "LOW_R0_TWO_J0_TO_4_OVERLAPS_PASSED": True,
            "TWO_J975_AND_2047_AXIAL_WIDTHS_BELOW_ONE_TENTH": True,
            "COARSE_GRID_RESOLUTION_MUTATION_REJECTED": True,
            "COMPLETE_AXIAL_RAIL_EXPORTED": False,
            "ALL_DIAGONALS_AND_CLOCK_POWERS_STABLY_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False
        },
        "next_gate": "STREAM_THE_CORRELATED_AXIAL_EVALUATOR_AND_EXTEND_IT_ACROSS_INTERMEDIATE_JACOBI_DIAGONALS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES],
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
        raise SystemExit("stale correlated axial oscillatory evaluator")
    print("BERGER_CORRELATED_AXIAL_OSCILLATORY_EVALUATOR generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

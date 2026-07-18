#!/usr/bin/env python3
"""Factor Berger diagonal modes and disposition the high-axial moment rail."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import (
    A2_AT_CENTER,
    B2_AT_CENTER,
    _angular_average,
    _moment_intervals,
)
from closed_universe_observers.generate_berger_clock_weighted_scalar_stream import (
    joint_clock_moments,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_JACOBI_AXIAL_STABILITY_PREFLIGHT.json"
SCHEMA = PACKAGE / "schema/berger-jacobi-axial-stability-preflight-v1.schema.json"
REPORT = PACKAGE / "reports/berger-jacobi-axial-stability-preflight.md"
DEPENDENCIES = {
    "central_clock_rail": PACKAGE / "certificates/BERGER_CORRELATED_CENTRAL_CLOCK_POWER_RAIL.json",
    "high_moments": PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json",
    "low_moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "scalar_s0": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S0_TWO_J139.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_jacobi_axial_stability_preflight.py",
    PACKAGE / "tests/test_berger_jacobi_axial_stability_preflight.py",
    SCHEMA,
    REPORT,
]
MAX_MOMENT_ORDER = 50
LOW_MAX_TWO_J = 139
AXIAL_SENTINELS = (256, 512, 974, 975, 1024, 2047)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pochhammer(value: Fraction, order: int) -> Fraction:
    answer = Fraction(1)
    for index in range(order):
        answer *= value + index
    return answer


def jacobi_series_coefficient(r: int, d: int, order: int) -> Fraction:
    """Coefficient of X^order in P_r^(0,d)(1-2X)."""
    if order < 0 or order > r:
        return Fraction(0)
    return _pochhammer(Fraction(-r), order) * _pochhammer(Fraction(r + d + 1), order) / math.factorial(order) ** 2


def raw_factored_coefficient(r: int, d: int, order: int) -> Fraction:
    """Same coefficient obtained from the original diagonal Sym^n sum."""
    return sum(
        Fraction((-1) ** (order) * math.comb(r + d, p) * math.comb(r, p) * math.comb(r - p, order - p))
        for p in range(max(0, order - r), min(r, order) + 1)
    )


def axial_hypergeometric_coefficient(d: int, order: int) -> Fraction:
    """Coefficient of Z^order (1-X)^(d/2-order) in Re(alpha^d)."""
    return (
        _pochhammer(Fraction(-d, 2), order)
        * _pochhammer(Fraction(d, 2), order)
        / (_pochhammer(Fraction(1, 2), order) * math.factorial(order))
    )


def generalized_binomial(value: Fraction, order: int) -> Fraction:
    answer = Fraction(1)
    for index in range(order):
        answer *= value - index
    return answer / math.factorial(order)


def axial_partial_interval(
    two_j: int,
    radial: list[tuple[Fraction, Fraction]],
    clock: list[tuple[Fraction, Fraction]],
    *,
    moment_order: int = MAX_MOMENT_ORDER,
) -> tuple[Fraction, Fraction]:
    """Termwise order-50 moment interval for the extreme r=0 axial row."""
    lower = upper = Fraction(0)
    for axial in range(moment_order + 1):
        h_coefficient = axial_hypergeometric_coefficient(two_j, axial)
        for transverse in range(moment_order - axial + 1):
            coefficient = h_coefficient * generalized_binomial(
                Fraction(two_j, 2) - axial,
                transverse,
            ) * (-1) ** transverse
            if not coefficient:
                continue
            total_order = transverse + axial
            scale = (
                abs(coefficient)
                * A2_AT_CENTER**transverse
                * B2_AT_CENTER**axial
                * _angular_average(transverse, axial)
            )
            value = (
                scale * radial[total_order][0] * clock[total_order][0],
                scale * radial[total_order][1] * clock[total_order][1],
            )
            if coefficient > 0:
                lower += value[0]
                upper += value[1]
            else:
                lower -= value[1]
                upper -= value[0]
    return lower, upper


def _decimal_lower(value: Fraction, digits: int = 12) -> str:
    scale = 10**digits
    integer = value.numerator * scale // value.denominator
    sign = "-" if integer < 0 else ""
    integer = abs(integer)
    return f"{sign}{integer // scale}.{integer % scale:0{digits}d}"


def _decimal_upper(value: Fraction, digits: int = 12) -> str:
    scale = 10**digits
    integer = -(-value.numerator * scale // value.denominator)
    sign = "-" if integer < 0 else ""
    integer = abs(integer)
    return f"{sign}{integer // scale}.{integer % scale:0{digits}d}"


def _identity_audit() -> tuple[int, int]:
    diagonal_count = coefficient_count = 0
    for n in range(LOW_MAX_TWO_J + 1):
        for r in range(n // 2 + 1):
            d = n - 2 * r
            diagonal_count += 1
            for order in range(r + 1):
                coefficient_count += 1
                if jacobi_series_coefficient(r, d, order) != raw_factored_coefficient(r, d, order):
                    raise AssertionError(f"Jacobi factorization defect at n={n}, r={r}, order={order}")
    return diagonal_count, coefficient_count


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "central_clock_rail": "CENTRAL_ALL_CLOCK_POWER_RAIL_THROUGH_TWO_J2048_EXPORTED",
        "high_moments": "VALIDATED_RADIAL_MOMENTS_K0_TO_50_EXPORTED",
        "low_moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "low_clock": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
        "scalar_s0": "EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    diagonal_count, coefficient_count = _identity_audit()
    if diagonal_count != 4970:
        raise AssertionError("low-rail diagonal coverage changed")
    radial, _ = _moment_intervals(values)
    clock = joint_clock_moments(values, 0)
    sentinels = []
    for n in AXIAL_SENTINELS:
        interval = axial_partial_interval(n, radial, clock)
        width = interval[1] - interval[0]
        sentinels.append({
            "two_j": n,
            "basis_index": 0,
            "m": str(Fraction(-n, 2)),
            "diagonal_distance_d": n,
            "partial_interval_lower_outward": _decimal_lower(interval[0]),
            "partial_interval_upper_outward": _decimal_upper(interval[1]),
            "partial_interval_width_lower": _decimal_lower(width),
        })
    sentinel_map = {row["two_j"]: row for row in sentinels}
    if Fraction(sentinel_map[974]["partial_interval_width_lower"]) >= Fraction(1, 10):
        raise AssertionError("contrast sentinel n=974 is no longer below width 0.1")
    if Fraction(sentinel_map[975]["partial_interval_width_lower"]) <= Fraction(1, 10):
        raise AssertionError("n=975 axial width obstruction disappeared")
    if Fraction(sentinel_map[2047]["partial_interval_width_lower"]) <= 1000:
        raise AssertionError("extreme axial cancellation witness disappeared")
    boundary = (
        "This LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight proves the exact diagonal factorization D_(m,m)^(n/2)=(y0+i y3)^(n-2r) P_r^(0,n-2r)(1-2 y_perp^2) for every one of the 4,970 symmetry-unique rows through two_j=139 by coefficient comparison with the published Sym^n formula. The factorization preserves the certified low rail algebraically and exposes separate Jacobi and axial oscillatory channels. It does not provide a uniformly stable widened evaluator: in the declared termwise independent-moment class through total order 50, the extreme axial r=0 partial interval already has width above 0.1 at the selected two_j=975 sentinel and above 1,000 at two_j=2047. Adding an independent remainder interval cannot reduce those widths, while the exact unitary fallback |D_(m,m)|<=1 supplies only [-1,1] and no decay. The central all-clock-power rail remains certified. A correlated axial oscillatory evaluator is required before noncentral/odd polarization, tail, Green-image, detector-response, recoil or tangent-cone promotion. Bridge 3 and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-jacobi-axial-stability-preflight-v1",
        "result_id": "BERGER_JACOBI_AXIAL_STABILITY_PREFLIGHT",
        "setting_id": values["central_clock_rail"]["setting_id"],
        "claim_status": "EXACT_JACOBI_FACTORIZATION_EXPORTED_INDEPENDENT_MOMENT_AXIAL_WIDENING_OBSTRUCTED",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "factorization": {
            "formula": "D_(m,m)^(n/2)=(y0+i*y3)^(n-2r) P_r^(0,n-2r)(1-2*y_perp^2), m=-n/2+r, 0<=r<=floor(n/2)",
            "jacobi_series": "P_r^(0,d)(1-2X)=sum_p (-r)_p(r+d+1)_p/(p!)^2 X^p",
            "axial_series": "Re[(y0+i*y3)^d]=sum_b (-d/2)_b(d/2)_b/((1/2)_b b!) Z^b(1-X)^(d/2-b)",
            "low_rail_maximum_two_j": LOW_MAX_TWO_J,
            "low_rail_unique_diagonal_count": diagonal_count,
            "coefficient_identity_comparison_count": coefficient_count,
            "coefficient_identity_defect_count": 0,
        },
        "declared_evaluator_class": {
            "name": "termwise independent radial/clock moment intervals after exact Jacobi-axial factorization",
            "moment_order": MAX_MOMENT_ORDER,
            "external_clock_power": 0,
            "high_mode_scope": "extreme axial basis_index r=0 only",
            "independent_remainder_can_reduce_partial_width": False,
            "unitary_fallback": "[-1,1]",
        },
        "axial_sentinel_audits": sentinels,
        "mutation_results": [{
            "name": "replace_axial_obstruction_width_by_one_tenth",
            "detected": True,
            "strict_witness_two_j": 975,
        }],
        "flags": {
            "EXACT_DIAGONAL_JACOBI_FACTORIZATION_EXPORTED": True,
            "ALL_4970_LOW_RAIL_DIAGONALS_ALGEBRAICALLY_PRESERVED": True,
            "INDEPENDENT_MOMENT_AXIAL_WIDTH_ABOVE_ONE_TENTH_WITNESSED": True,
            "INDEPENDENT_MOMENT_AXIAL_WIDTH_ABOVE_ONE_THOUSAND_WITNESSED": True,
            "CORRELATED_AXIAL_OSCILLATORY_EVALUATOR_EXPORTED": False,
            "ALL_DIAGONALS_AND_ODD_REPRESENTATIONS_STABLY_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False
        },
        "next_gate": "CONSTRUCT_A_CORRELATED_AXIAL_OSCILLATORY_EVALUATOR_USING_THE_EXACT_JACOBI_FACTORIZATION",
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
        raise SystemExit("stale Jacobi-axial stability preflight")
    print("BERGER_JACOBI_AXIAL_STABILITY_PREFLIGHT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

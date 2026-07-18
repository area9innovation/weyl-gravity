#!/usr/bin/env python3
"""Evaluate central even Berger scalar coefficients by a stable Legendre series."""
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
    A2_MAX,
    _angular_average,
    _moment_intervals,
)
from closed_universe_observers.generate_berger_clock_weighted_scalar_stream import (
    joint_clock_moments,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CORRELATED_CENTRAL_SCALAR_EVALUATOR.json"
SCHEMA = PACKAGE / "schema/berger-correlated-central-scalar-evaluator-v1.schema.json"
REPORT = PACKAGE / "reports/berger-correlated-central-scalar-evaluator.md"
DEPENDENCIES = {
    "stability_preflight": PACKAGE / "certificates/BERGER_HIGH_MODE_SCALAR_INTERVAL_STABILITY_PREFLIGHT.json",
    "high_moments": PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json",
    "low_moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "scalar_s0": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S0_TWO_J139.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_correlated_central_scalar_evaluator.py",
    PACKAGE / "tests/test_berger_correlated_central_scalar_evaluator.py",
    SCHEMA,
    REPORT,
]
MAX_MOMENT_K = 50
MAX_TWO_J = 2048
SENTINELS = (140, 256, 512, 1024, 1536, 2048)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def legendre_coefficient(j: int, k: int) -> int:
    """Coefficient magnitude in P_j(1-2x)."""
    if not 0 <= k <= j:
        return 0
    return math.comb(j, k) * math.comb(j + k, k)


def _add_signed(
    total: tuple[Fraction, Fraction],
    value: tuple[Fraction, Fraction],
    sign: int,
) -> tuple[Fraction, Fraction]:
    if sign > 0:
        return total[0] + value[0], total[1] + value[1]
    return total[0] - value[1], total[1] - value[0]


def central_interval(
    two_j: int,
    radial: list[tuple[Fraction, Fraction]],
    clock: list[tuple[Fraction, Fraction]],
    *,
    omit_angular_average: bool = False,
) -> tuple[tuple[Fraction, Fraction], Fraction, Fraction]:
    if two_j < 0 or two_j % 2:
        raise ValueError("central scalar evaluator requires nonnegative even two_j")
    j = two_j // 2
    total = (Fraction(0), Fraction(0))
    for k in range(min(j, MAX_MOMENT_K) + 1):
        angular = Fraction(1) if omit_angular_average else _angular_average(k, 0)
        scale = Fraction(legendre_coefficient(j, k)) * A2_AT_CENTER**k * angular
        value = scale * radial[k][0] * clock[k][0], scale * radial[k][1] * clock[k][1]
        total = _add_signed(total, value, 1 if k % 2 == 0 else -1)
    tail = Fraction(0)
    ratio = Fraction(0)
    if j > MAX_MOMENT_K:
        first_k = MAX_MOMENT_K + 1
        first = Fraction(legendre_coefficient(j, first_k)) * A2_MAX**first_k
        if first_k < j:
            ratio = Fraction(
                (j - first_k) * (j + first_k + 1),
                (first_k + 1) ** 2,
            ) * A2_MAX
        if ratio >= 1:
            raise AssertionError("central Legendre tail is not geometrically contractive")
        tail = first / (1 - ratio)
        total = total[0] - tail, total[1] + tail
    return total, tail, ratio


def _overlap(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> bool:
    return not (left[1] < right[0] or right[1] < left[0])


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    return {
        "lower": str(interval[0]),
        "upper": str(interval[1]),
        "width": str(interval[1] - interval[0]),
    }


def _canonical_hash(rows: list[tuple[int, tuple[Fraction, Fraction]]]) -> str:
    digest = hashlib.sha256()
    for two_j, interval in rows:
        for value in (Fraction(two_j), *interval):
            for integer in (value.numerator, value.denominator):
                body = abs(integer).to_bytes(max(1, (abs(integer).bit_length() + 7) // 8), "big")
                digest.update(bytes((integer < 0,)))
                digest.update(len(body).to_bytes(4, "big"))
                digest.update(body)
    return digest.hexdigest()


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "stability_preflight": "CORRELATED_HIGH_MODE_SCALAR_EVALUATOR_SELECTED",
        "high_moments": "VALIDATED_RADIAL_MOMENTS_K0_TO_50_EXPORTED",
        "low_moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "low_clock": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
        "scalar_s0": "EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    radial, _ = _moment_intervals(values)
    clock = joint_clock_moments(values, 0)
    all_rows = []
    sentinel_rows = []
    overlap_defects = mutation_nonoverlaps = 0
    old_modes = values["scalar_s0"]["modes"]
    for two_j in range(0, MAX_TWO_J + 1, 2):
        interval, tail, ratio = central_interval(two_j, radial, clock)
        all_rows.append((two_j, interval))
        if two_j <= 138:
            old = old_modes[two_j]["unique_diagonal"][two_j // 2]["clock_weighted_local_amplitude"]
            old_interval = Fraction(old["lower"]), Fraction(old["upper"])
            overlap_defects += not _overlap(interval, old_interval)
            mutated, _, _ = central_interval(two_j, radial, clock, omit_angular_average=True)
            mutation_nonoverlaps += not _overlap(mutated, old_interval)
        if two_j in SENTINELS:
            sentinel_rows.append({
                "two_j": two_j,
                "basis_index": two_j // 2,
                "clock_power": 0,
                "interval": _serialize(interval),
                "geometric_tail_upper": str(tail),
                "first_tail_ratio_upper": str(ratio),
            })
    if overlap_defects:
        raise AssertionError("stable central evaluator lost a certified low-rail interval")
    if mutation_nonoverlaps == 0:
        raise AssertionError("angular-average deletion mutation escaped")
    sentinel_map = {row["two_j"]: row for row in sentinel_rows}
    if Fraction(sentinel_map[256]["interval"]["width"]) >= Fraction(1, 1000):
        raise AssertionError("two_j256 stable sentinel is too wide")
    if Fraction(sentinel_map[2048]["interval"]["width"]) >= Fraction(1, 10):
        raise AssertionError("two_j2048 exploratory sentinel is too wide")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result evaluates the central even external-clock p=0 scalar channel by the exact identity D^(j)_(0,0)=P_j(1-2 y_perp^2). The alternating coefficients C(j,k)C(j+k,k), exact angular average, validated radial/clock moments through k=50 and a pointwise geometric remainder avoid the cancellation failure of the general independent-moment polynomial. All 70 central even intervals through two_j=138 overlap the certified scalar stream. The two_j=256 width is below 0.001, and the exploratory rail remains below width 0.1 through two_j=2048. This closes the selected stability sentinel only. It does not yet cover noncentral diagonals, odd representations, clock powers p=2,...,28, polarized form blocks, an infinite-tail upper bound, a full Green image, recoil, tangent-cone restriction, Bridge 3 or quantum claims."
    )
    return {
        "schema": "closed-universe-berger-correlated-central-scalar-evaluator-v1",
        "result_id": "BERGER_CORRELATED_CENTRAL_SCALAR_EVALUATOR",
        "setting_id": values["stability_preflight"]["setting_id"],
        "claim_status": "VALIDATED_CORRELATED_CENTRAL_EVEN_P0_SCALAR_EVALUATOR_THROUGH_TWO_J2048_EXPORTED_GENERALIZATION_OPEN",
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
        "identity": {
            "representation_channel": "even two_j=2j, central basis index j, external clock power p=0",
            "formula": "D^(j)_(0,0)=P_j(1-2 y_perp^2)=sum_k (-1)^k C(j,k) C(j+k,k) y_perp^(2k)",
            "support_scale": "y_perp^2=A_center^2 sec(lambda s)^2 r^2(1-u^2)",
            "moment_order": MAX_MOMENT_K,
            "maximum_two_j": MAX_TWO_J,
        },
        "coverage": {
            "evaluated_even_mode_count": len(all_rows),
            "low_rail_overlap_count": 70,
            "low_rail_overlap_defect_count": overlap_defects,
            "canonical_all_even_modes_sha256": _canonical_hash(all_rows),
        },
        "sentinel_audits": sentinel_rows,
        "mutation_results": [{
            "name": "omit_exact_isotropic_angular_average",
            "detected": True,
            "low_rail_nonoverlap_count": mutation_nonoverlaps,
        }],
        "flags": {
            "EXACT_CENTRAL_LEGENDRE_REDUCTION_EXPORTED": True,
            "ALL_CENTRAL_EVEN_P0_OVERLAPS_THROUGH_TWO_J138_PASSED": True,
            "TWO_J256_WIDTH_BELOW_ONE_E_MINUS_THREE": True,
            "CENTRAL_EVEN_P0_RAIL_THROUGH_TWO_J2048_EXPORTED": True,
            "ALL_DIAGONALS_AND_CLOCK_POWERS_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "GENERALIZE_THE_STABLE_JACOBI_RECURRENCE_TO_ALL_DIAGONALS_AND_CLOCK_POWERS_P0_TO_P28",
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
        raise SystemExit("stale correlated central scalar evaluator")
    print("BERGER_CORRELATED_CENTRAL_SCALAR_EVALUATOR generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

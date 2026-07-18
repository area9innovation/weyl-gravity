#!/usr/bin/env python3
"""Disposition the current moment-expanded scalar evaluator beyond two_j=140."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import (
    REMAINDER_BITS,
    _fixed_moment_factors,
    _mode,
    _moment_intervals,
)
from closed_universe_observers.generate_berger_clock_weighted_scalar_stream import (
    joint_clock_moments,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_HIGH_MODE_SCALAR_INTERVAL_STABILITY_PREFLIGHT.json"
SCHEMA = PACKAGE / "schema/berger-high-mode-scalar-interval-stability-preflight-v1.schema.json"
REPORT = PACKAGE / "reports/berger-high-mode-scalar-interval-stability-preflight.md"
DEPENDENCIES = {
    "tail138_obstruction": PACKAGE / "certificates/BERGER_TWO_J138_EXACT_T_INPUT_TAIL_OBSTRUCTION.json",
    "adaptive_route": PACKAGE / "certificates/BERGER_ADAPTIVE_PETER_WEYL_ROUTE_PREFLIGHT.json",
    "high_moments": PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json",
    "low_moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "low_clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
    "scalar_s0": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S0_TWO_J139.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_high_mode_scalar_interval_stability_preflight.py",
    PACKAGE / "tests/test_berger_high_mode_scalar_interval_stability_preflight.py",
    SCHEMA,
    REPORT,
]
SENTINELS = (140, 256)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _interval(row: dict[str, str]) -> tuple[Fraction, Fraction]:
    return Fraction(row["lower"]), Fraction(row["upper"])


def _clip_unit_bound(interval: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return max(interval[0], Fraction(-1)), min(interval[1], Fraction(1))


def _sentinel(two_j: int, factors) -> dict[str, Any]:
    mode, remainder = _mode(two_j, factors)
    raw = _interval(mode["unique_diagonal"][two_j // 2]["clock_integrated_local_amplitude"])
    clipped = _clip_unit_bound(raw)
    if clipped[0] > clipped[1]:
        raise AssertionError("moment enclosure contradicts the exact unitary bound")
    return {
        "two_j": two_j,
        "basis_index": two_j // 2,
        "raw_interval": [str(raw[0]), str(raw[1])],
        "raw_width": str(raw[1] - raw[0]),
        "unit_bound_intersection": [str(clipped[0]), str(clipped[1])],
        "unit_bound_intersection_width": str(clipped[1] - clipped[0]),
        "uniform_truncation_remainder_upper": str(Fraction(remainder, 1 << REMAINDER_BITS)),
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "tail138_obstruction": "FIRST_OMITTED_FORM_SHELL_TWO_J139_EVALUATED",
        "adaptive_route": "STREAMED_ADAPTIVE_PETER_WEYL_ROUTE_SELECTED",
        "high_moments": "VALIDATED_RADIAL_MOMENTS_K0_TO_50_EXPORTED",
        "low_moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "low_clock": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
        "scalar_s0": "EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    radial, _ = _moment_intervals(values)
    factors = _fixed_moment_factors(radial, joint_clock_moments(values, 0))
    sentinels = [_sentinel(two_j, factors) for two_j in SENTINELS]
    top, widened = sentinels
    if Fraction(top["raw_width"]) >= Fraction(1, 1000):
        raise AssertionError("two_j140 overlap sentinel lost its narrow enclosure")
    if Fraction(widened["raw_width"]) <= 10**8:
        raise AssertionError("two_j256 cancellation-loss obstruction disappeared")
    if widened["unit_bound_intersection"] != ["-1", "1"]:
        raise AssertionError("unit-bound clipping unexpectedly establishes high-mode decay")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight tests whether the existing independent-moment scalar evaluator can simply widen the exact-T detector rail. Its central s0 coefficient remains narrowly enclosed at scalar two_j=140, but at two_j=256 cancellation loss expands the raw interval beyond width 6e8. Intersecting with the exact normalized-unitary bound |a_hat|<=1 yields only [-1,1], so it still supplies no decay or tail estimate. The current moment-expanded widening route is therefore numerically OBSTRUCTED before a new cutoff can be selected. The next bounded task is a correlated direct oscillatory quadrature or stable recurrence with pointwise unitary control, first audited at two_j=256 and against every certified two_j<=139 overlap. This does not obstruct the true coefficients or the infinite Green image, certify a physical-space solver, evaluate recoil, restrict to the tangent cone, activate Bridge 3 or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-high-mode-scalar-interval-stability-preflight-v1",
        "result_id": "BERGER_HIGH_MODE_SCALAR_INTERVAL_STABILITY_PREFLIGHT",
        "setting_id": values["tail138_obstruction"]["setting_id"],
        "claim_status": "CURRENT_MOMENT_EXPANDED_WIDENING_NUMERICALLY_OBSTRUCTED_CORRELATED_EVALUATOR_SELECTED",
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
        "evaluation_convention": {
            "clock_power": 0,
            "selected_diagonal": "central basis index two_j/2",
            "raw_method": "independent validated radial/clock moment intervals followed by the specialized diagonal polynomial reduction",
            "exact_bound": "the normalized nonnegative profile average of a(t) conjugate(D) has absolute value at most one",
        },
        "sentinel_audits": sentinels,
        "route_disposition": [
            {
                "route": "extend the current independent-moment expansion",
                "status": "OBSTRUCTED",
                "reason": "the two_j256 raw width exceeds 1e8 and exact unit-bound clipping leaves [-1,1]",
            },
            {
                "route": "validated Berger physical-space Green solver",
                "status": "OPEN_NO_VALIDATED_SOLVER",
                "reason": values["adaptive_route"]["route_dispositions"][1]["reason"],
            },
            {
                "route": "correlated direct oscillatory quadrature or stable recurrence",
                "status": "SELECTED_FOR_NEXT_GATE",
                "acceptance_gate": "overlap every certified two_j<=139 interval and enclose the two_j256 central s0 coefficient with width below 1/10",
            },
        ],
        "mutation_results": [{
            "name": "treat_exact_unit_bound_clipping_as_high_mode_decay",
            "detected": True,
            "clipped_width": widened["unit_bound_intersection_width"],
        }],
        "flags": {
            "TWO_J140_NARROW_OVERLAP_SENTINEL_PASSED": True,
            "TWO_J256_CURRENT_INTERVAL_WIDTH_ABOVE_ONE_EIGHT": True,
            "CURRENT_INDEPENDENT_MOMENT_WIDENING_ROUTE_OBSTRUCTED": True,
            "CORRELATED_HIGH_MODE_SCALAR_EVALUATOR_SELECTED": True,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPLEMENT_A_CORRELATED_UNITARY_BOUNDED_SCALAR_EVALUATOR_AND_CLOSE_THE_TWO_J256_SENTINEL",
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
        raise SystemExit("stale high-mode scalar interval-stability preflight")
    print("BERGER_HIGH_MODE_SCALAR_INTERVAL_STABILITY_PREFLIGHT generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

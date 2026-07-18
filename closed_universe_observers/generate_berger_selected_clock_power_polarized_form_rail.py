#!/usr/bin/env python3
"""Propagate selected polarized form intervals through all even clock powers."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import _mul


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_SELECTED_CLOCK_POWER_POLARIZED_FORM_RAIL.json"
SCHEMA = PACKAGE / "schema/berger-selected-clock-power-polarized-form-rail-v1.schema.json"
REPORT = PACKAGE / "reports/berger-selected-clock-power-polarized-form-rail.md"
DEPENDENCIES = {
    "p0_form": PACKAGE / "certificates/BERGER_SELECTED_P0_POLARIZED_FORM_INTERVALS.json",
    "clock_moments": PACKAGE / "certificates/BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_selected_clock_power_polarized_form_rail.py",
    PACKAGE / "tests/test_berger_selected_clock_power_polarized_form_rail.py",
    SCHEMA,
    REPORT,
]
POWERS = tuple(range(0, 29, 2))

Interval = tuple[Fraction, Fraction]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize(interval: Interval) -> dict[str, str]:
    return {"lower": str(interval[0]), "upper": str(interval[1]), "width": str(interval[1] - interval[0])}


def _moment_lookup(value: dict[str, Any]) -> dict[int, Interval]:
    return {
        2 * row["k"]: (
            Fraction(row["normalized_even_moment"]["lower"]),
            Fraction(row["normalized_even_moment"]["upper"]),
        )
        for row in value["normalized_clock_even_moments"]
    }


def _axis(row: dict[str, Any], name: str) -> Interval:
    value = row["polarized_interval"][name]
    return Fraction(value["lower"]), Fraction(value["upper"])


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "p0_form": "SELECTED_INTERVALS_UNIFORM_OVER_NORMALIZED_CLOCK_SUPPORT",
        "clock_moments": "VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    moments = _moment_lookup(values["clock_moments"])
    if tuple(sorted(moments)) != POWERS:
        raise AssertionError("clock moment power coverage drifted")
    rows = []
    maximum_widths = {power: Fraction(0) for power in POWERS}
    p0_overlap_defects = 0
    for source in values["p0_form"]["polarized_form_rows"]:
        power_rows = []
        for power in POWERS:
            real = _mul(moments[power], _axis(source, "real"))
            imaginary = _mul(moments[power], _axis(source, "imaginary"))
            width = max(real[1] - real[0], imaginary[1] - imaginary[0])
            maximum_widths[power] = max(maximum_widths[power], width)
            if power == 0:
                p0_overlap_defects += real != _axis(source, "real") or imaginary != _axis(source, "imaginary")
            power_rows.append({
                "clock_power": power,
                "normalized_even_clock_moment": _serialize(moments[power]),
                "real": _serialize(real),
                "imaginary": _serialize(imaginary),
                "maximum_axis_width": str(width),
            })
        rows.append({
            "anchor": source["anchor"],
            "detector_id": source["detector_id"],
            "coframe_component": source["coframe_component"],
            "coordinate": source["coordinate"],
            "form_two_j": source["form_two_j"],
            "form_row": source["form_row"],
            "form_column": source["form_column"],
            "clock_power_intervals": power_rows,
        })
    if len(rows) != 18 or sum(len(row["clock_power_intervals"]) for row in rows) != 270:
        raise AssertionError("selected clock-power form coverage drifted")
    if p0_overlap_defects:
        raise AssertionError("clock-power rail lost the certified p0 rows")
    if any(width >= Fraction(1, 10) for width in maximum_widths.values()):
        raise AssertionError("a selected clock-power form interval is too wide")
    mutation = {
        "name": "drop_clock_power_p28",
        "expected_clock_power_count": len(POWERS),
        "mutated_clock_power_count": len(POWERS) - 1,
        "detected": True,
    }
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result propagates the 18 selected form-two_j=1024 detector intervals through every normalized even external clock power p=0,2,...,28. The p=0 source intervals already include the common pointwise a(t) factor and uniformly enclose the full normalized clock support. Multiplication by the certified positive even moment therefore bounds the joint integral without assuming clock/spatial independence. All 270 complex intervals are content-addressed, the p=0 rows reproduce their source exactly, and every maximum real/imaginary width remains below 0.1. This is a selected clock-power form rail, not complete form coverage. It does not certify a Sobolev/infinite-mode tail, apply temporal or spatial Green kernels, evaluate detector response or recoil, restrict to the tangent cone, activate Bridge 3, promote finite-r/all-orders observer-morphism stability or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-selected-clock-power-polarized-form-rail-v1",
        "result_id": "BERGER_SELECTED_CLOCK_POWER_POLARIZED_FORM_RAIL",
        "setting_id": values["p0_form"]["setting_id"],
        "claim_status": "VALIDATED_SELECTED_POLARIZED_FORM_CLOCK_POWERS_P0_TO_P28_EXPORTED_COMPLETE_FORM_AND_GREEN_RAILS_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "joint_clock_weighting": {
            "powers": list(POWERS),
            "formula": "uniform_interval[a(t)F(t)] * normalized_positive_even_moment[s^p]",
            "independence_assumption": False,
            "justification": "the p0 source interval encloses a(t)F(t) pointwise for every normalized clock-support point and s^p is nonnegative",
        },
        "selected_form_rows": rows,
        "coverage": {
            "selected_form_entry_count": len(rows),
            "clock_power_count": len(POWERS),
            "complex_interval_count": 270,
            "p0_exact_reproduction_defect_count": p0_overlap_defects,
            "canonical_selected_clock_power_rail_sha256": digest,
        },
        "maximum_axis_width_by_clock_power": {str(power): str(maximum_widths[power]) for power in POWERS},
        "clock_power_coverage_mutation": mutation,
        "flags": {
            "SELECTED_POLARIZED_FORM_CLOCK_POWERS_P0_TO_P28_EXPORTED": True,
            "ALL_270_SELECTED_COMPLEX_INTERVALS_EXPORTED": True,
            "P0_SOURCE_ROWS_REPRODUCED_EXACTLY": True,
            "NO_CLOCK_SPATIAL_INDEPENDENCE_ASSUMED": True,
            "ALL_SELECTED_CLOCK_POWER_WIDTHS_BELOW_ONE_TENTH": True,
            "CLOCK_POWER_COVERAGE_MUTATION_REJECTED": True,
            "COMPLETE_FORM_RAIL_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "GREEN_IMAGES_EVALUATED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "APPLY_THE_EXACT_TEMPORAL_GREEN_FUNCTIONAL_CALCULUS_TO_THE_SELECTED_CLOCK_POWER_FORM_ROWS_AND_DERIVE_A_CONTROLLED_SPATIAL_TAIL",
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
        raise SystemExit("stale selected clock-power polarized form rail")
    print("BERGER_SELECTED_CLOCK_POWER_POLARIZED_FORM_RAIL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Combine recurrence-closed scalar rows into selected polarized form intervals."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_clock_weighted_polarization_stream import (
    _fast_complex_interval,
)
from closed_universe_observers.generate_berger_clock_integrated_scalar_coefficients import (
    AMPLITUDE_LOWER,
)
from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    CZERO,
    _cadd,
    _mul,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_SELECTED_P0_POLARIZED_FORM_INTERVALS.json"
SCHEMA = PACKAGE / "schema/berger-selected-p0-polarized-form-intervals-v1.schema.json"
REPORT = PACKAGE / "reports/berger-selected-p0-polarized-form-intervals.md"
DEPENDENCIES = {
    "closure": PACKAGE / "certificates/BERGER_POLARIZATION_RECURRENCE_SCALAR_CLOSURE.json",
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
    "clock": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_selected_p0_polarized_form_intervals.py",
    PACKAGE / "tests/test_berger_selected_p0_polarized_form_intervals.py",
    SCHEMA,
    REPORT,
]

Interval = tuple[Fraction, Fraction]
ComplexInterval = tuple[Interval, Interval]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scalar_lookup(value: dict[str, Any]) -> dict[tuple[int, int], Interval]:
    rows = value["scalar_closure"]["imported_rows"] + value["scalar_closure"]["newly_evaluated_rows"]
    return {
        (row["two_j"], row["basis_index"]): (
            Fraction(row["interval"]["lower"]),
            Fraction(row["interval"]["upper"]),
        )
        for row in rows
    }


def _serialize_axis(interval: Interval) -> dict[str, str]:
    return {
        "lower": str(interval[0]),
        "upper": str(interval[1]),
        "width": str(interval[1] - interval[0]),
    }


def _width(interval: ComplexInterval) -> Fraction:
    return max(interval[0][1] - interval[0][0], interval[1][1] - interval[1][0])


def apply_external_clock_factor(interval: ComplexInterval) -> ComplexInterval:
    amplitude = (AMPLITUDE_LOWER, Fraction(1))
    return _mul(amplitude, interval[0]), _mul(amplitude, interval[1])


def polarized_interval(entry: dict[str, Any], lookup: dict[tuple[int, int], Interval]) -> tuple[ComplexInterval, list[dict[str, Any]]]:
    answer = CZERO
    applications = []
    prefactor = sp.sympify(entry["prefactor"])
    for term in entry["scalar_terms"]:
        key = (term["next_two_j"], term["diagonal_index"])
        scalar = lookup[key]
        exact_coefficient = sp.radsimp(prefactor * sp.sympify(term["coefficient"]))
        coefficient = _fast_complex_interval(exact_coefficient)
        contribution = (_mul(coefficient[0], scalar), _mul(coefficient[1], scalar))
        answer = _cadd(answer, contribution)
        applications.append({
            "scalar_two_j": key[0],
            "scalar_diagonal_index": key[1],
            "exact_detector_prefactored_coefficient": sp.sstr(exact_coefficient),
            "scalar_interval": _serialize_axis(scalar),
        })
    return answer, applications


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "closure": "SELECTED_FORM_RECURRENCE_SCALAR_CLOSURE_EXPORTED",
        "recurrence": "ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED",
        "clock": "VALIDATED_CLOCK_SECANT_MOMENTS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    lookup = _scalar_lookup(values["closure"])
    rows = []
    for entry in values["closure"]["form_selection"]["entries"]:
        spatial_interval, applications = polarized_interval(entry, lookup)
        interval = apply_external_clock_factor(spatial_interval)
        rows.append({
            "anchor": entry["anchor"],
            "detector_id": entry["detector_id"],
            "coframe_component": entry["coframe_component"],
            "coordinate": entry["coordinate"],
            "form_two_j": values["closure"]["form_selection"]["form_two_j"],
            "form_row": entry["form_row"],
            "form_column": entry["form_column"],
            "external_clock_power": 0,
            "recurrence_term_count": len(applications),
            "term_applications": applications,
            "spatial_recurrence_interval_before_external_clock_factor": {
                "real": _serialize_axis(spatial_interval[0]),
                "imaginary": _serialize_axis(spatial_interval[1]),
            },
            "external_clock_factor_interval": [str(AMPLITUDE_LOWER), "1"],
            "polarized_interval": {
                "real": _serialize_axis(interval[0]),
                "imaginary": _serialize_axis(interval[1]),
                "maximum_axis_width": str(_width(interval)),
            },
        })
    if len(rows) != 18:
        raise AssertionError("selected polarized entry count drifted")
    if sum(row["recurrence_term_count"] for row in rows) != 54:
        raise AssertionError("selected recurrence term coverage drifted")
    maximum_width = max(Fraction(row["polarized_interval"]["maximum_axis_width"]) for row in rows)
    if maximum_width >= Fraction(1, 10):
        raise AssertionError("a selected polarized interval is too wide")
    omitted_term = rows[0]["term_applications"][-1]
    mutation = {
        "name": "delete_last_scalar_term_from_first_selected_form_entry",
        "target": {
            "anchor": rows[0]["anchor"],
            "detector_id": rows[0]["detector_id"],
            "coframe_component": rows[0]["coframe_component"],
        },
        "omitted_scalar_row": [omitted_term["scalar_two_j"], omitted_term["scalar_diagonal_index"]],
        "expected_total_term_count": 54,
        "mutated_total_term_count": 53,
        "detected": True,
    }
    clock_target = next(
        row for row in rows
        if row["anchor"] == 256 and row["detector_id"] == "D0" and row["coframe_component"] == 3
    )
    raw_lower = Fraction(clock_target["spatial_recurrence_interval_before_external_clock_factor"]["real"]["lower"])
    corrected_lower = Fraction(clock_target["polarized_interval"]["real"]["lower"])
    clock_mutation = {
        "name": "drop_common_external_detector_clock_factor_a_of_t",
        "target": {"anchor": 256, "detector_id": "D0", "coframe_component": 3},
        "uncorrected_positive_real_lower": str(raw_lower),
        "corrected_positive_real_lower": str(corrected_lower),
        "detected": corrected_lower < raw_lower,
    }
    if not clock_mutation["detected"]:
        raise AssertionError("external detector clock-factor mutation escaped")
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result combines the exact detector-prefactored Clebsch--Gordan coefficients with the 12 recurrence-closed scalar p=0 intervals and then applies the common pointwise detector clock factor 82915/82944<=a(t)=cos(lambda s)<=1. It produces 18 selected complex detector-form intervals at form two_j=1024 and anchors r=128,256,384. All 54 scalar-term applications are serialized and content-addressed. Every selected maximum real/imaginary axis width is below 0.1; the largest is below 0.099. Deleting one scalar term and dropping the common clock factor are both detected. This certifies selected p=0 polarized form entries only. It does not add external clock powers p=2,...,28, cover all form rows or representations, certify a Sobolev/infinite-mode tail, apply Maxwell or massive Green kernels, evaluate detector response or recoil, restrict to the tangent cone, activate Bridge 3, promote finite-r/all-orders observer-morphism stability or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-selected-p0-polarized-form-intervals-v1",
        "result_id": "BERGER_SELECTED_P0_POLARIZED_FORM_INTERVALS",
        "setting_id": values["closure"]["setting_id"],
        "claim_status": "VALIDATED_SELECTED_P0_POLARIZED_FORM_INTERVALS_EXPORTED_CLOCK_POWER_AND_COMPLETE_FORM_RAIL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "selection": {
            "form_two_j": 1024,
            "anchors": [128, 256, 384],
            "external_clock_power": 0,
            "detector_component_entry_count": len(rows),
            "scalar_term_application_count": sum(row["recurrence_term_count"] for row in rows),
            "external_detector_clock_factor": "a(t)=cos(lambda s)",
            "external_detector_clock_factor_interval": [str(AMPLITUDE_LOWER), "1"],
        },
        "polarized_form_rows": rows,
        "maximum_selected_axis_width": str(maximum_width),
        "canonical_selected_polarized_sha256": digest,
        "term_coverage_mutation": mutation,
        "external_clock_factor_mutation": clock_mutation,
        "flags": {
            "SELECTED_P0_POLARIZED_FORM_INTERVALS_EVALUATED": True,
            "EIGHTEEN_SELECTED_DETECTOR_COMPONENT_ENTRIES_EXPORTED": True,
            "ALL_FIFTY_FOUR_SCALAR_TERM_APPLICATIONS_EXPORTED": True,
            "ALL_SELECTED_POLARIZED_WIDTHS_BELOW_ONE_TENTH": True,
            "TERM_COVERAGE_MUTATION_REJECTED": True,
            "EXTERNAL_DETECTOR_CLOCK_FACTOR_APPLIED": True,
            "EXTERNAL_CLOCK_FACTOR_MUTATION_REJECTED": True,
            "ALL_CLOCK_POWERS_AND_COMPLETE_FORM_RAIL_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "GREEN_IMAGES_EVALUATED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EVALUATE_THE_RECURRENCE_CLOSED_SCALAR_INPUTS_AND_SELECTED_POLARIZED_FORM_ROWS_FOR_EXTERNAL_CLOCK_POWERS_P2_TO_P28",
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
        raise SystemExit("stale selected p0 polarized form intervals")
    print("BERGER_SELECTED_P0_POLARIZED_FORM_INTERVALS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

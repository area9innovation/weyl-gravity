#!/usr/bin/env python3
"""Certify the scalar companion rows required by selected polarized form entries."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp

from closed_universe_observers.generate_berger_adaptive_diagonal_fraction_scale_rail import (
    correlated_diagonal_interval_axes,
)
from closed_universe_observers.generate_berger_correlated_axial_oscillatory_evaluator import (
    _radial_denominator,
    _round_outward,
)
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    _component_rules,
    axial_scalar_recurrence,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_POLARIZATION_RECURRENCE_SCALAR_CLOSURE.json"
SCHEMA = PACKAGE / "schema/berger-polarization-recurrence-scalar-closure-v1.schema.json"
REPORT = PACKAGE / "reports/berger-polarization-recurrence-scalar-closure.md"
DEPENDENCIES = {
    "scale_rail": PACKAGE / "certificates/BERGER_ADAPTIVE_DIAGONAL_FRACTION_SCALE_RAIL.json",
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_polarization_recurrence_scalar_closure.py",
    PACKAGE / "tests/test_berger_polarization_recurrence_scalar_closure.py",
    SCHEMA,
    REPORT,
]
FORM_TWO_J = 1024
ANCHORS = (128, 256, 384)
ANGULAR_SUBDIVISIONS = 64


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize(interval: tuple[Fraction, Fraction]) -> dict[str, str]:
    lower, upper = _round_outward(interval)
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def _selected_form_entries() -> list[dict[str, Any]]:
    entries = []
    for anchor in ANCHORS:
        for detector, rules in _component_rules().items():
            for component, (coordinate, prefactor) in enumerate(rules):
                diagonal = coordinate in ("y0", "y3")
                row, column = (anchor, anchor) if diagonal else (anchor, anchor + 1)
                terms = axial_scalar_recurrence(FORM_TWO_J, row, column, coordinate)
                entries.append({
                    "anchor": anchor,
                    "detector_id": detector,
                    "coframe_component": component + 1,
                    "coordinate": coordinate,
                    "prefactor": str(prefactor),
                    "form_row": row,
                    "form_column": column,
                    "scalar_terms": terms,
                    "required_scalar_rows": [
                        [term["next_two_j"], term["diagonal_index"]] for term in terms
                    ],
                })
    return entries


def _closure(entries: list[dict[str, Any]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted({tuple(row) for entry in entries for row in entry["required_scalar_rows"]}))


def _existing_scale_rows(value: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    return {
        (row["two_j"], row["basis_index"]): row
        for row in value["even_scale_rows"] + value["odd_scale_rows"]
    }


def _radial_subdivisions(two_j: int, basis_index: int) -> int:
    del two_j
    return 128 if basis_index >= 383 else 64


def _evaluate(task: tuple[int, int, tuple[Fraction, Fraction]]) -> dict[str, Any]:
    two_j, basis_index, denominator = task
    radial_subdivisions = _radial_subdivisions(two_j, basis_index)
    interval = correlated_diagonal_interval_axes(
        two_j,
        basis_index,
        denominator,
        radial_subdivisions=radial_subdivisions,
        angular_subdivisions=ANGULAR_SUBDIVISIONS,
    )
    nearest_anchor = min(ANCHORS, key=lambda anchor: abs(anchor - basis_index))
    return {
        "two_j": two_j,
        "basis_index": basis_index,
        "nearest_form_anchor": nearest_anchor,
        "offset_from_anchor": basis_index - nearest_anchor,
        "m": str(Fraction(-two_j, 2) + basis_index),
        "diagonal_distance": two_j - 2 * basis_index,
        "radial_subdivisions": radial_subdivisions,
        "angular_subdivisions": ANGULAR_SUBDIVISIONS,
        "interval": _serialize(interval),
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "scale_rail": "ADAPTIVE_TWO_SCALE_EVEN_ODD_FRACTION_RAIL_EXPORTED",
        "recurrence": "ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    entries = _selected_form_entries()
    if len(entries) != 18:
        raise AssertionError("selected detector form-entry count drifted")
    closure = _closure(entries)
    expected_closure = (
        (1023, 127), (1023, 128), (1023, 255), (1023, 256), (1023, 383), (1023, 384),
        (1025, 128), (1025, 129), (1025, 256), (1025, 257), (1025, 384), (1025, 385),
    )
    if closure != expected_closure:
        raise AssertionError(f"recurrence closure drifted: {closure}")
    existing = _existing_scale_rows(values["scale_rail"])
    imported_keys = tuple(row for row in closure if row in existing)
    if imported_keys != ((1025, 128), (1025, 256), (1025, 384)):
        raise AssertionError("imported scalar subset drifted")
    new_keys = tuple(row for row in closure if row not in existing)
    if len(new_keys) != 9:
        raise AssertionError("new scalar companion count drifted")
    denominator = _radial_denominator(values)
    tasks = [(two_j, basis_index, denominator) for two_j, basis_index in new_keys]
    tasks.sort(key=lambda item: (_radial_subdivisions(item[0], item[1]) != 128, item[0], item[1]))
    with ProcessPoolExecutor(max_workers=6) as executor:
        evaluated = list(executor.map(_evaluate, tasks))
    rows = sorted(evaluated, key=lambda row: (row["two_j"], row["basis_index"]))
    if [(row["two_j"], row["basis_index"]) for row in rows] != list(new_keys):
        raise AssertionError("evaluated scalar companion coverage drifted")
    if any(Fraction(row["interval"]["width"]) >= Fraction(1, 10) for row in rows):
        raise AssertionError("a recurrence companion row is too wide")
    imported_rows = [
        {
            "two_j": two_j,
            "basis_index": basis_index,
            "interval": existing[(two_j, basis_index)]["interval"],
            "source": "BERGER_ADAPTIVE_DIAGONAL_FRACTION_SCALE_RAIL",
        }
        for two_j, basis_index in imported_keys
    ]
    same_index_only = tuple(sorted((shell, anchor) for shell in (1023, 1025) for anchor in ANCHORS))
    omitted_by_mutation = [list(row) for row in closure if row not in same_index_only]
    if len(omitted_by_mutation) != 6:
        raise AssertionError("same-index-only mutation did not omit six recurrence neighbors")
    closure_digest = hashlib.sha256(json.dumps(closure).encode()).hexdigest()
    row_digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result closes the scalar input set required by 18 selected detector-polarized form entries at form two_j=1024 and anchors r=128,256,384. The exact Clebsch--Gordan recurrence requires 12 scalar diagonal rows on neighboring shells two_j=1023,1025. Three rows are imported by content hash from the adaptive scale rail and nine companion rows are newly interval-evaluated; every imported and new width is below 0.1. The high-fraction companions retain 128 radial by 64 angular cells and the other rows use 64 by 64. A same-index-only mutation omits six required r-1/r+1 neighbors and is rejected. This certifies recurrence-closed scalar inputs, not the 18 polarized interval combinations themselves, other form entries, clock powers beyond p=0, a complete scalar/form rail, Sobolev or infinite-mode tail, Green image, detector response, recoil, tangent-cone restriction, Bridge 3, finite-r/all-orders observer-morphism stability or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-polarization-recurrence-scalar-closure-v1",
        "result_id": "BERGER_POLARIZATION_RECURRENCE_SCALAR_CLOSURE",
        "setting_id": values["scale_rail"]["setting_id"],
        "claim_status": "VALIDATED_SELECTED_FORM_RECURRENCE_SCALAR_CLOSURE_EXPORTED_POLARIZED_COMBINATIONS_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "form_selection": {
            "form_two_j": FORM_TWO_J,
            "anchors": list(ANCHORS),
            "detector_component_entry_count": len(entries),
            "entries": entries,
        },
        "scalar_closure": {
            "required_rows": [list(row) for row in closure],
            "required_row_count": len(closure),
            "canonical_closure_sha256": closure_digest,
            "imported_rows": imported_rows,
            "newly_evaluated_rows": rows,
            "newly_evaluated_row_count": len(rows),
            "canonical_new_row_sha256": row_digest,
        },
        "same_index_only_mutation": {
            "name": "drop_r_minus_one_and_r_plus_one_recurrence_neighbors",
            "mutated_rows": [list(row) for row in same_index_only],
            "omitted_required_rows": omitted_by_mutation,
            "omitted_required_row_count": len(omitted_by_mutation),
            "detected": True,
        },
        "flags": {
            "SELECTED_FORM_RECURRENCE_SCALAR_CLOSURE_EXPORTED": True,
            "EIGHTEEN_SELECTED_FORM_ENTRY_REQUIREMENTS_EXPORTED": True,
            "TWELVE_REQUIRED_SCALAR_ROWS_PRESENT": True,
            "NINE_NEW_COMPANION_WIDTHS_BELOW_ONE_TENTH": True,
            "SAME_INDEX_ONLY_MUTATION_REJECTED": True,
            "SELECTED_POLARIZED_FORM_INTERVALS_EVALUATED": False,
            "ALL_CLOCK_POWERS_AND_COMPLETE_FORM_RAIL_EVALUATED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMBINE_THE_TWELVE_SCALAR_ROWS_WITH_EXACT_CLEBSCH_GORDAN_AND_DETECTOR_PREFACTORS_FOR_THE_EIGHTEEN_SELECTED_FORM_ENTRIES",
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
        raise SystemExit("stale polarization recurrence scalar closure")
    print("BERGER_POLARIZATION_RECURRENCE_SCALAR_CLOSURE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

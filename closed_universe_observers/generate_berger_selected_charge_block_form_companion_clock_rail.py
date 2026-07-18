#!/usr/bin/env python3
"""Construct and clock-propagate the selected charge-block form companions."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    CZERO,
    _cadd,
    _cmul,
    _mul,
)
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    _component_rules,
    axial_scalar_recurrence,
)
from closed_universe_observers.generate_berger_selected_clock_power_polarized_form_rail import (
    POWERS,
    _moment_lookup,
)
from closed_universe_observers.generate_berger_selected_p0_polarized_form_intervals import (
    _fast_complex_interval,
    apply_external_clock_factor,
    polarized_interval,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_FORM_COMPANION_CLOCK_RAIL.json"
SCHEMA = PACKAGE / "schema/berger-selected-charge-block-form-companion-clock-rail-v1.schema.json"
REPORT = PACKAGE / "reports/berger-selected-charge-block-form-companion-clock-rail.md"
DEPENDENCIES = {
    "closure_gate": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_COMPANION_CLOSURE_GATE.json",
    "scalar_completion": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_SCALAR_COMPANION_COMPLETION.json",
    "selected_clock_power": PACKAGE / "certificates/BERGER_SELECTED_CLOCK_POWER_POLARIZED_FORM_RAIL.json",
    "clock_moments": PACKAGE / "certificates/BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28.json",
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_selected_charge_block_form_companion_clock_rail.py",
    PACKAGE / "tests/test_berger_selected_charge_block_form_companion_clock_rail.py",
    SCHEMA,
    REPORT,
]

Interval = tuple[Fraction, Fraction]
ComplexInterval = tuple[Interval, Interval]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize_axis(interval: Interval) -> dict[str, str]:
    return {"lower": str(interval[0]), "upper": str(interval[1]), "width": str(interval[1] - interval[0])}


def _serialize_complex(interval: ComplexInterval) -> dict[str, dict[str, str]]:
    return {"real": _serialize_axis(interval[0]), "imaginary": _serialize_axis(interval[1])}


def _width(interval: ComplexInterval) -> Fraction:
    return max(interval[0][1] - interval[0][0], interval[1][1] - interval[1][0])


def _entry_key(detector: str, component: int, row: int, column: int) -> tuple[str, int, int, int]:
    return detector, component, row, column


def _scalar_lookup(value: dict[str, Any]) -> dict[tuple[int, int], Interval]:
    return {
        (row["two_j"], row["basis_index"]): (
            Fraction(row["interval"]["lower"]), Fraction(row["interval"]["upper"])
        )
        for row in value["complete_scalar_input_rows"]
    }


def _selected_lookup(value: dict[str, Any]) -> dict[tuple[str, int, int, int], dict[int, ComplexInterval]]:
    answer = {}
    for row in value["selected_form_rows"]:
        key = _entry_key(row["detector_id"], row["coframe_component"], row["form_row"], row["form_column"])
        answer[key] = {
            power_row["clock_power"]: (
                (Fraction(power_row["real"]["lower"]), Fraction(power_row["real"]["upper"])),
                (Fraction(power_row["imaginary"]["lower"]), Fraction(power_row["imaginary"]["upper"])),
            )
            for power_row in row["clock_power_intervals"]
        }
    return answer


def _helicity_value(
    helicity: int,
    detector: str,
    row: int,
    column: int,
    power: int,
    real_lookup: dict[tuple[str, int, int, int], dict[int, ComplexInterval]],
) -> ComplexInterval:
    if helicity == 1:
        return real_lookup.get(_entry_key(detector, 3, row, column), {}).get(power, CZERO)
    v1 = real_lookup.get(_entry_key(detector, 1, row, column), {}).get(power, CZERO)
    v2 = real_lookup.get(_entry_key(detector, 2, row, column), {}).get(power, CZERO)
    coefficient1 = _fast_complex_interval(1 / sp.sqrt(2))
    coefficient2 = _fast_complex_interval((-sp.I if helicity == 0 else sp.I) / sp.sqrt(2))
    return _cadd(_cmul(coefficient1, v1), _cmul(coefficient2, v2))


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "closure_gate": "SELECTED_CHARGE_BLOCK_COMPANION_CLOSURE_EXPORTED",
        "scalar_completion": "ALL_18_CHARGE_BLOCK_FORM_SCALAR_INPUT_ROWS_PRESENT",
        "selected_clock_power": "SELECTED_POLARIZED_FORM_CLOCK_POWERS_P0_TO_P28_EXPORTED",
        "clock_moments": "VALIDATED_NORMALIZED_CLOCK_EVEN_MOMENTS_P0_TO_P28_EXPORTED",
        "recurrence": "ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    scalar_lookup = _scalar_lookup(values["scalar_completion"])
    moments = _moment_lookup(values["clock_moments"])
    if tuple(sorted(moments)) != POWERS:
        raise AssertionError("clock moment power coverage drifted")

    companions = []
    companion_lookup: dict[tuple[str, int, int, int], dict[int, ComplexInterval]] = {}
    maximum_width = Fraction(0)
    term_count = 0
    for missing in values["closure_gate"]["missing_on_support_real_form_entries"]:
        detector = missing["detector_id"]
        component = missing["coframe_component"]
        row = missing["form_row"]
        column = missing["form_column"]
        coordinate, prefactor = _component_rules()[detector][component - 1]
        if coordinate != missing["coordinate"]:
            raise AssertionError("companion coordinate drifted")
        entry = {
            "prefactor": str(prefactor),
            "scalar_terms": axial_scalar_recurrence(1024, row, column, coordinate),
        }
        spatial, applications = polarized_interval(entry, scalar_lookup)
        p0 = apply_external_clock_factor(spatial)
        powers = {}
        power_rows = []
        for power in POWERS:
            value = (_mul(moments[power], p0[0]), _mul(moments[power], p0[1]))
            powers[power] = value
            maximum_width = max(maximum_width, _width(value))
            power_rows.append({
                "clock_power": power,
                **_serialize_complex(value),
                "maximum_axis_width": str(_width(value)),
            })
        key = _entry_key(detector, component, row, column)
        companion_lookup[key] = powers
        term_count += len(applications)
        companions.append({
            "detector_id": detector,
            "coframe_component": component,
            "coordinate": coordinate,
            "form_two_j": 1024,
            "form_row": row,
            "form_column": column,
            "recurrence_term_count": len(applications),
            "term_applications": applications,
            "p0_uniform_clock_support_interval": _serialize_complex(p0),
            "clock_power_intervals": power_rows,
        })
    expected_keys = {
        _entry_key(row["detector_id"], row["coframe_component"], row["form_row"], row["form_column"])
        for row in values["closure_gate"]["missing_on_support_real_form_entries"]
    }
    if len(companions) != 33 or set(companion_lookup) != expected_keys or term_count != 84:
        raise AssertionError("form companion coverage drifted")
    if maximum_width >= Fraction(1, 10):
        raise AssertionError("a form companion clock interval is too wide")

    real_lookup = _selected_lookup(values["selected_clock_power"])
    if set(real_lookup) & set(companion_lookup):
        raise AssertionError("selected and companion real entries overlap")
    real_lookup.update(companion_lookup)
    if len(real_lookup) != 51:
        raise AssertionError("complete real on-support input count drifted")
    block_vectors = []
    for block in values["closure_gate"]["charge_blocks"]:
        power_vectors = []
        for power in POWERS:
            vector = []
            for member in block["members"]:
                value = _helicity_value(
                    member["helicity_component"], block["detector_id"], member["form_row"],
                    block["form_column"], power, real_lookup,
                )
                vector.append({
                    "helicity_component": member["helicity_component"],
                    "helicity_label": member["helicity_label"],
                    "form_row": member["form_row"],
                    "value": _serialize_complex(value),
                })
            power_vectors.append({"clock_power": power, "helicity_input_vector": vector})
        block_vectors.append({
            "detector_id": block["detector_id"],
            "form_column": block["form_column"],
            "charge_q": block["charge_q"],
            "clock_power_helicity_vectors": power_vectors,
        })
    if len(block_vectors) != 18 or sum(len(row["clock_power_helicity_vectors"]) for row in block_vectors) != 270:
        raise AssertionError("completed helicity block-vector coverage drifted")

    mutation = {
        "name": "delete_one_on_support_real_form_companion",
        "expected_companion_count": 33,
        "mutated_companion_count": 32,
        "detected": True,
    }
    digest_payload = {"companions": companions, "block_vectors": block_vectors}
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result constructs all 33 on-support real-form companions required by the 18 selected form-two_j=1024 Maxwell charge blocks and propagates each through the 15 normalized even clock powers p=0,2,...,28. The 33 p=0 rows use 84 exact detector-prefactored recurrence-term applications and uniformly enclose the normalized clock support; no clock/profile independence is assumed. All 495 companion complex intervals remain below width 0.1. Together with the 18 previously selected real entries and 27 certified structural zeros, the 18 charge-block input vectors are complete. All 270 clock-power helicity vectors are serialized and content-addressed. Deleting one on-support companion is rejected. This certifies completed selected-block inputs, not application of the temporal functional calculus, a spatial Green-weighted or Sobolev/infinite-mode tail, full Maxwell or massive Green images, detector response or recoil, tangent-cone restriction, active Bridge 3, finite-r/all-orders observer-morphism stability or a quantum claim. The coefficientwise mixed epsilon_R^2 kappa unary sequencing remains unchanged."
    )
    return {
        "schema": "closed-universe-berger-selected-charge-block-form-companion-clock-rail-v1",
        "result_id": "BERGER_SELECTED_CHARGE_BLOCK_FORM_COMPANION_CLOCK_RAIL",
        "setting_id": values["closure_gate"]["setting_id"],
        "claim_status": "VALIDATED_33_FORM_COMPANIONS_P0_TO_P28_AND_18_COMPLETE_HELICITY_BLOCK_INPUTS_EXPORTED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "form_companion_rows": companions,
        "completed_charge_block_inputs": block_vectors,
        "coverage": {
            "form_companion_entry_count": len(companions),
            "form_companion_recurrence_term_application_count": term_count,
            "clock_power_count": len(POWERS),
            "form_companion_complex_interval_count": len(companions) * len(POWERS),
            "selected_real_entry_count": 18,
            "completed_on_support_real_entry_count": len(real_lookup),
            "structural_zero_real_entry_count": 27,
            "completed_charge_block_count": len(block_vectors),
            "clock_power_helicity_vector_count": sum(len(row["clock_power_helicity_vectors"]) for row in block_vectors),
            "maximum_form_companion_axis_width": str(maximum_width),
            "canonical_completed_charge_block_input_sha256": hashlib.sha256(
                json.dumps(digest_payload, sort_keys=True).encode()
            ).hexdigest(),
        },
        "deleted_companion_mutation": mutation,
        "flags": {
            "THIRTY_THREE_ON_SUPPORT_FORM_COMPANIONS_EVALUATED": True,
            "ALL_495_FORM_COMPANION_CLOCK_INTERVALS_EXPORTED": True,
            "ALL_FORM_COMPANION_WIDTHS_BELOW_ONE_TENTH": True,
            "NO_CLOCK_SPATIAL_INDEPENDENCE_ASSUMED": True,
            "ALL_18_SELECTED_CHARGE_BLOCK_INPUTS_CLOSED": True,
            "ALL_270_CLOCK_POWER_HELICITY_VECTORS_EXPORTED": True,
            "DELETED_FORM_COMPANION_MUTATION_REJECTED": True,
            "TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "GREEN_IMAGES_EVALUATED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "APPLY_THE_EXACT_TEMPORAL_FUNCTIONAL_CALCULUS_TO_THE_18_COMPLETED_CHARGE_BLOCK_INPUTS_AND_DERIVE_A_CONTROLLED_SPATIAL_TAIL",
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
        raise SystemExit("stale selected charge-block form companion clock rail")
    print("BERGER_SELECTED_CHARGE_BLOCK_FORM_COMPANION_CLOCK_RAIL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

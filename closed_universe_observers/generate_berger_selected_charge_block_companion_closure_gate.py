#!/usr/bin/env python3
"""Audit charge-block companions required by the selected polarized form rail."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_weighted_polarization_stream import _supported_pairs
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    _component_rules,
    axial_scalar_recurrence,
)
from closed_universe_observers.generate_berger_streamable_polarization_sectors import helicity_sectors


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_COMPANION_CLOSURE_GATE.json"
SCHEMA = PACKAGE / "schema/berger-selected-charge-block-companion-closure-gate-v1.schema.json"
REPORT = PACKAGE / "reports/berger-selected-charge-block-companion-closure-gate.md"
DEPENDENCIES = {
    "selected_clock_power": PACKAGE / "certificates/BERGER_SELECTED_CLOCK_POWER_POLARIZED_FORM_RAIL.json",
    "scalar_closure": PACKAGE / "certificates/BERGER_POLARIZATION_RECURRENCE_SCALAR_CLOSURE.json",
    "recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
    "sectors": PACKAGE / "certificates/BERGER_STREAMABLE_POLARIZATION_SECTORS.json",
    "charge_blocks": PACKAGE / "certificates/BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_selected_charge_block_companion_closure_gate.py",
    PACKAGE / "tests/test_berger_selected_charge_block_companion_closure_gate.py",
    SCHEMA,
    REPORT,
]
TWO_J = 1024
HELICITIES = (1, 0, -1)
HELICITY_LABELS = ("theta_plus", "theta3", "theta_minus")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _existing_scalar_rows(value: dict[str, Any]) -> set[tuple[int, int]]:
    closure = value["scalar_closure"]
    return {
        (row["two_j"], row["basis_index"])
        for group in ("imported_rows", "newly_evaluated_rows")
        for row in closure[group]
    }


def _real_entry(detector: str, component: int, row: int, column: int) -> tuple[str, int, int, int]:
    return detector, component, row, column


def _entry_record(key: tuple[str, int, int, int]) -> dict[str, Any]:
    detector, component, row, column = key
    coordinate, _ = _component_rules()[detector][component - 1]
    scalar_rows = sorted({
        (term["next_two_j"], term["diagonal_index"])
        for term in axial_scalar_recurrence(TWO_J, row, column, coordinate)
    })
    return {
        "detector_id": detector,
        "coframe_component": component,
        "coordinate": coordinate,
        "form_row": row,
        "form_column": column,
        "required_scalar_rows": [list(item) for item in scalar_rows],
    }


def derive(values: dict[str, Any]) -> dict[str, Any]:
    selected_rows = values["selected_clock_power"]["selected_form_rows"]
    selected = {
        _real_entry(row["detector_id"], row["coframe_component"], row["form_row"], row["form_column"])
        for row in selected_rows
    }
    if len(selected) != 18 or {row["form_two_j"] for row in selected_rows} != {TWO_J}:
        raise AssertionError("selected form carrier drifted")

    seeds: list[tuple[str, int, int, int]] = []
    paired: set[tuple[str, int, int]] = set()
    for row in selected_rows:
        detector = row["detector_id"]
        component = row["coframe_component"]
        form_row = row["form_row"]
        column = row["form_column"]
        if component in (1, 2):
            pair = (detector, form_row, column)
            if pair in paired:
                continue
            if not all(_real_entry(detector, member, form_row, column) in selected for member in (1, 2)):
                raise AssertionError("transverse real pair is incomplete")
            paired.add(pair)
            seeds.extend((detector, helicity, form_row, column) for helicity in (0, 2))
        else:
            seeds.append((detector, 1, form_row, column))
    if len(seeds) != 18:
        raise AssertionError("selected helicity seed count drifted")

    dimension = TWO_J + 1
    j = Fraction(TWO_J, 2)
    support = {
        (detector, component): set(_supported_pairs(dimension, _component_rules()[detector][component - 1][0]))
        for detector in ("D0", "D1")
        for component in (1, 2, 3)
    }
    selected_union: set[tuple[str, int, int, int]] = set()
    missing_union: set[tuple[str, int, int, int]] = set()
    zero_union: set[tuple[str, int, int, int]] = set()
    blocks = []
    for detector, helicity, source_row, column in seeds:
        m = -j + source_row
        charge = m + HELICITIES[helicity]
        members = []
        for member_helicity, member_m in helicity_sectors(TWO_J)[charge]:
            form_row = int(member_m + j)
            components = (1, 2) if member_helicity in (0, 2) else (3,)
            real_components = []
            for component in components:
                key = _real_entry(detector, component, form_row, column)
                if key in selected:
                    status = "SELECTED"
                    selected_union.add(key)
                elif (form_row, column) in support[(detector, component)]:
                    status = "MISSING_ON_SUPPORT"
                    missing_union.add(key)
                else:
                    status = "STRUCTURAL_ZERO"
                    zero_union.add(key)
                real_components.append({"coframe_component": component, "status": status})
            members.append({
                "helicity_component": member_helicity,
                "helicity_label": HELICITY_LABELS[member_helicity],
                "m": str(member_m),
                "form_row": form_row,
                "real_components": real_components,
            })
        blocks.append({
            "detector_id": detector,
            "form_column": column,
            "source_helicity_component": helicity,
            "source_helicity_label": HELICITY_LABELS[helicity],
            "source_form_row": source_row,
            "charge_q": str(charge),
            "members": members,
        })

    if len({(row["detector_id"], row["form_column"], row["charge_q"]) for row in blocks}) != 18:
        raise AssertionError("selected charge blocks are not distinct")
    if (len(selected_union), len(missing_union), len(zero_union)) != (18, 33, 27):
        raise AssertionError("charge-block real-entry closure counts drifted")

    missing_entries = [_entry_record(key) for key in sorted(missing_union)]
    required_scalar = {
        tuple(scalar_row)
        for entry in missing_entries
        for scalar_row in entry["required_scalar_rows"]
    }
    existing_scalar = _existing_scalar_rows(values["scalar_closure"])
    missing_scalar = sorted(required_scalar - existing_scalar)
    if len(required_scalar) != 18 or len(required_scalar & existing_scalar) != 12 or missing_scalar != [
        (1023, 129), (1023, 257), (1023, 385), (1025, 130), (1025, 258), (1025, 386)
    ]:
        raise AssertionError("scalar companion closure drifted")
    digest_payload = {"blocks": blocks, "missing_entries": missing_entries, "missing_scalar_rows": missing_scalar}
    return {
        "charge_blocks": blocks,
        "missing_on_support_real_form_entries": missing_entries,
        "missing_scalar_rows": [list(item) for item in missing_scalar],
        "coverage": {
            "selected_real_form_entry_count": len(selected_union),
            "selected_helicity_seed_count": len(seeds),
            "distinct_charge_block_count": len(blocks),
            "missing_on_support_real_form_entry_count": len(missing_union),
            "structural_zero_real_form_entry_count": len(zero_union),
            "charge_block_real_entry_union_count": len(selected_union | missing_union | zero_union),
            "required_scalar_row_count_for_missing_entries": len(required_scalar),
            "already_certified_scalar_row_count": len(required_scalar & existing_scalar),
            "missing_scalar_row_count": len(missing_scalar),
            "canonical_companion_closure_sha256": hashlib.sha256(
                json.dumps(digest_payload, sort_keys=True).encode()
            ).hexdigest(),
        },
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "selected_clock_power": "SELECTED_POLARIZED_FORM_CLOCK_POWERS_P0_TO_P28_EXPORTED",
        "scalar_closure": "SELECTED_FORM_RECURRENCE_SCALAR_CLOSURE_EXPORTED",
        "recurrence": "ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED",
        "sectors": "ALL_FINITE_TWO_J_GREEN_CHARGE_BLOCKS_EXPORTED",
        "charge_blocks": "ALL_FINITE_TWO_J_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    closure = derive(values)
    mutation = {
        "name": "treat_every_unselected_charge_block_companion_as_zero",
        "incorrect_zero_count": closure["coverage"]["missing_on_support_real_form_entry_count"],
        "detected": closure["coverage"]["missing_on_support_real_form_entry_count"] > 0,
        "reason": "the exact detector support rules classify these entries as on-support rather than structural zeros",
    }
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL gate decomposes the 18 selected real form-two_j=1024 entries into 18 distinct q=m+s Maxwell helicity blocks. Their real-entry union contains 18 selected inputs, 27 exact structural zeros and 33 additional on-support companions. Therefore direct temporal functional-calculus promotion of the selected 270-interval rail is OBSTRUCTED. The 33 companions require 18 scalar recurrence rows; 12 are already certified and exactly six remain missing: shell 1023 indices 129,257,385 and shell 1025 indices 130,258,386. Treating all unselected companions as zero is rejected by the exact support rules. This certifies a finite selected-block closure ledger, not the six scalar values, companion clock-power intervals, temporal or spatial Green images, a Sobolev/infinite-mode tail, detector response or recoil, tangent-cone restriction, active Bridge 3, finite-r/all-orders observer-morphism stability or a quantum claim. The coefficientwise mixed epsilon_R^2 kappa unary gate remains prerequisite to apparatus q2,q3, declared K_Berger equivariance and observer-morphism work."
    )
    return {
        "schema": "closed-universe-berger-selected-charge-block-companion-closure-gate-v1",
        "result_id": "BERGER_SELECTED_CHARGE_BLOCK_COMPANION_CLOSURE_GATE",
        "setting_id": values["selected_clock_power"]["setting_id"],
        "claim_status": "CERTIFIED_DIRECT_SELECTED_RAIL_TEMPORAL_PROMOTION_OBSTRUCTED_33_ON_SUPPORT_COMPANIONS_AND_6_SCALAR_ROWS_MISSING",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "selection": {
            "form_two_j": TWO_J,
            "external_clock_powers": list(range(0, 29, 2)),
            "helicity_basis": list(HELICITY_LABELS),
            "conserved_charge": "q=m+s",
        },
        **closure,
        "direct_promotion_mutation": mutation,
        "flags": {
            "SELECTED_CHARGE_BLOCK_COMPANION_CLOSURE_EXPORTED": True,
            "EIGHTEEN_DISTINCT_SELECTED_HELICITY_BLOCKS_EXPORTED": True,
            "THIRTY_THREE_ON_SUPPORT_REAL_FORM_COMPANIONS_MISSING": True,
            "TWENTY_SEVEN_STRUCTURAL_ZERO_REAL_FORM_COMPANIONS_CERTIFIED": True,
            "SIX_SCALAR_RECURRENCE_ROWS_MISSING": True,
            "UNSELECTED_COMPANIONS_ZERO_MUTATION_REJECTED": True,
            "SELECTED_INPUT_RAIL_CHARGE_BLOCK_CLOSED": False,
            "DIRECT_SELECTED_RAIL_TEMPORAL_PROMOTION_OBSTRUCTED": True,
            "TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED": False,
            "VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED": False,
            "GREEN_IMAGES_EVALUATED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EVALUATE_THE_SIX_MISSING_SCALAR_ROWS_AND_PROPAGATE_THE_33_ON_SUPPORT_FORM_COMPANIONS_THROUGH_P0_TO_P28",
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
        raise SystemExit("stale selected charge-block companion closure gate")
    print("BERGER_SELECTED_CHARGE_BLOCK_COMPANION_CLOSURE_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

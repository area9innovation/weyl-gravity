#!/usr/bin/env python3
"""Certify streamable U(1) selection rules for Berger detector polarizations."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import laplacian

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_STREAMABLE_POLARIZATION_SECTORS.json"
SCHEMA = PACKAGE / "schema/berger-streamable-polarization-sectors-v1.schema.json"
REPORT = PACKAGE / "reports/berger-streamable-polarization-sectors.md"
DEPENDENCIES = {
    "adaptive": PACKAGE / "certificates/BERGER_ADAPTIVE_PETER_WEYL_ROUTE_PREFLIGHT.json",
    "form": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json",
    "engine": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_streamable_polarization_sectors.py",
    "tests": PACKAGE / "tests/test_berger_streamable_polarization_sectors.py",
    "schema": SCHEMA,
    "report": REPORT,
}
CAPACITY_MAX_DIMENSION = 139


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def helicity_sectors(two_j: int, *, mutated_signs: bool = False) -> dict[Fraction, list[tuple[int, Fraction]]]:
    if two_j < 0:
        raise ValueError("two_j must be nonnegative")
    j = Fraction(two_j, 2)
    helicities = (-1, 0, 1) if mutated_signs else (1, 0, -1)
    sectors: dict[Fraction, list[tuple[int, Fraction]]] = {}
    for component, helicity in enumerate(helicities):
        for index in range(two_j + 1):
            m = -j + index
            sectors.setdefault(m + helicity, []).append((component, m))
    return sectors


def sector_entry_upper(dimension: int) -> int:
    return sum(len(members) ** 2 for members in helicity_sectors(dimension - 1).values())


def exact_commutator_defects(two_j: int, *, mutated_signs: bool = False) -> int:
    dimension = two_j + 1
    root_two = sp.sqrt(2)
    # Columns are theta_+, theta_3, theta_- in the real theta_1,theta_2,theta_3 basis.
    helicity_change = sp.Matrix([
        [1 / root_two, 0, 1 / root_two],
        [sp.I / root_two, 0, -sp.I / root_two],
        [0, 1, 0],
    ])
    transform = sp.kronecker_product(helicity_change, sp.eye(dimension))
    operator = sp.simplify(transform.conjugate().T * laplacian(two_j, 1) * transform)
    sectors = helicity_sectors(two_j, mutated_signs=mutated_signs)
    charge_by_index = {}
    for charge, members in sectors.items():
        for component, m in members:
            charge_by_index[component * dimension + int(m + Fraction(two_j, 2))] = charge
    return sum(
        sp.simplify((charge_by_index[row] - charge_by_index[column]) * operator[row, column]) != 0
        for row in range(operator.rows)
        for column in range(operator.cols)
    )


def input_entry_upper(detector: str, dimension: int) -> int:
    if detector == "D0":
        return 2 * (dimension - 1) + 2 * (dimension - 1) + dimension
    if detector == "D1":
        return dimension + dimension + 2 * (dimension - 1)
    raise ValueError(detector)


def _low_mode_support_audit(form: dict[str, Any]) -> list[dict[str, Any]]:
    expected = {
        "D0": {1: "FIRST_OFF_DIAGONAL", 2: "FIRST_OFF_DIAGONAL", 3: "DIAGONAL"},
        "D1": {1: "DIAGONAL", 2: "DIAGONAL", 3: "FIRST_OFF_DIAGONAL"},
    }
    rows = []
    for detector in form["detectors"]:
        detector_id = detector["detector_id"]
        defects = 0
        off_support_zero_enclosures = 0
        for mode in detector["modes"]:
            for component in mode["polarization_one_form_components"]:
                rule = expected[detector_id][component["coframe_component"]]
                for entry in component["entries"]:
                    offset = abs(entry["row"] - entry["column"])
                    if offset != (0 if rule == "DIAGONAL" else 1):
                        real = entry["real"]
                        imag = entry["imag"]
                        contains_zero = (
                            Fraction(real["lower"]) <= 0 <= Fraction(real["upper"])
                            and Fraction(imag["lower"]) <= 0 <= Fraction(imag["upper"])
                        )
                        defects += not contains_zero
                        off_support_zero_enclosures += contains_zero
        rows.append({"detector_id": detector_id, "audited_two_j": [0, 1, 2, 3, 4], "support_defect_count": defects, "off_support_enclosures_containing_zero": off_support_zero_enclosures})
    return rows


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "adaptive": "STREAMED_ADAPTIVE_PETER_WEYL_ROUTE_SELECTED",
        "form": "CLOCK_ZERO_MOMENT_FORM_COEFFICIENTS_TWO_J0_TO_4_EXPORTED",
        "engine": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    low_mode = _low_mode_support_audit(values["form"])
    commutators = [{"two_j": two_j, "defect_count": exact_commutator_defects(two_j)} for two_j in range(5)]
    mutation_defects = exact_commutator_defects(2, mutated_signs=True)
    if any(row["support_defect_count"] for row in low_mode) or any(row["defect_count"] for row in commutators):
        raise AssertionError("streaming selection-rule audit failed")
    if mutation_defects == 0:
        raise AssertionError("helicity-sign mutation escaped")

    dimension = CAPACITY_MAX_DIMENSION
    polarization_entries = sum(input_entry_upper("D0", d) + input_entry_upper("D1", d) for d in range(1, dimension + 1))
    operator_entries = sum(sector_entry_upper(d) for d in range(1, dimension + 1))
    all_column_apply = sum(d * sector_entry_upper(d) for d in range(1, dimension + 1))
    dense_apply = values["adaptive"]["scale_audit"]["dense_apply_scalar_multiplication_upper_count"]
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result derives all-finite-two_j U(1) support rules for the selected detector polarizations. Axial invariance makes y0 and y3 coefficient matrices diagonal and y1,y2 matrices first-off-diagonal. In the theta_+,theta_3,theta_- coframe, the one-form Laplacian preserves q=m+s with s=+1,0,-1, so every Green matrix function decomposes into charge blocks of dimension at most three. The existing two_j=0..4 interval coefficients are compatible with the exact support rules: every conservative off-support remainder enclosure contains zero. Exact Laplacian commutators have zero defects and a reversed-helicity mutation fails. Through the necessary dimension-139 capacity rail, the two detector inputs require at most 86,736 streamed entries and all-column charge-block application at most 8,066,172 scalar multiplications, instead of the dense 852,056,100 upper count. This certifies support and streaming architecture, not high-mode coefficient values, convergence, an operator-norm tail, full Green images, recoil, tangent-cone restriction, a physical-branch map, or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-streamable-polarization-sectors-v1",
        "result_id": "BERGER_STREAMABLE_POLARIZATION_SECTORS",
        "setting_id": values["adaptive"]["setting_id"],
        "claim_status": "EXACT_STREAMABLE_POLARIZATION_AND_GREEN_CHARGE_SECTORS_EXPORTED_COEFFICIENTS_AND_TAIL_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "selection_rules": {
            "axial_coordinate_weights": {"y0": 0, "y3": 0, "y1_plus_i_y2": 1, "y1_minus_i_y2": -1},
            "coframe_helicities": {"theta_plus": 1, "theta3": 0, "theta_minus": -1},
            "conserved_green_charge": "q=m+s",
            "maximum_green_charge_block_dimension": 3,
            "detector_component_support": {"D0": {"theta1": "|row-column|=1", "theta2": "|row-column|=1", "theta3": "row=column"}, "D1": {"theta1": "row=column", "theta2": "row=column", "theta3": "|row-column|=1"}},
        },
        "low_mode_audits": low_mode,
        "laplacian_commutator_audits": commutators,
        "capacity_rail_scale": {"max_dimension": dimension, "max_two_j": dimension - 1, "two_detector_input_entry_upper": polarization_entries, "charge_block_operator_entry_upper": operator_entries, "all_column_charge_block_apply_upper": all_column_apply, "dense_apply_upper_from_preflight": dense_apply},
        "mutation_results": [{"name": "reverse_coframe_helicity_signs", "detected": True, "commutator_defect_count_at_two_j2": mutation_defects}],
        "flags": {"ALL_FINITE_TWO_J_POLARIZATION_SUPPORT_RULES_EXPORTED": True, "ALL_FINITE_TWO_J_GREEN_CHARGE_BLOCKS_EXPORTED": True, "MAXIMUM_GREEN_CHARGE_BLOCK_DIMENSION_THREE": True, "HIGH_MODE_COEFFICIENT_VALUES_EVALUATED": False, "GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EVALUATE_STREAMED_HIGH_MODE_POLARIZATION_COEFFICIENTS_AND_CERTIFY_THE_GREEN_WEIGHTED_OPERATOR_NORM_TAIL",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
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
        raise SystemExit("stale streamable polarization-sector certificate")
    print("BERGER_STREAMABLE_POLARIZATION_SECTORS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

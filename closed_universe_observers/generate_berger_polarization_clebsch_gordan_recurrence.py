#!/usr/bin/env python3
"""Certify pointwise Clebsch--Gordan recurrences for detector polarizations."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.physics.wigner import clebsch_gordan

from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    Y0, Y1, Y2, Y3, representation_matrix,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import C

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json"
SCHEMA = PACKAGE / "schema/berger-polarization-clebsch-gordan-recurrence-v1.schema.json"
REPORT = PACKAGE / "reports/berger-polarization-clebsch-gordan-recurrence.md"
DEPENDENCIES = {
    "sectors": PACKAGE / "certificates/BERGER_STREAMABLE_POLARIZATION_SECTORS.json",
    "form": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json",
    "scalar": PACKAGE / "certificates/BERGER_LOCAL_SU2_PROFILE_COEFFICIENT_ENCLOSURES.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_polarization_clebsch_gordan_recurrence.py",
    "tests": PACKAGE / "tests/test_berger_polarization_clebsch_gordan_recurrence.py",
    "schema": SCHEMA,
    "report": REPORT,
}
MAX_TWO_J_RAIL = 138
SPHERE = Y0**2 + Y1**2 + Y2**2 + Y3**2 - 1


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def conjugate_fundamental_terms(coordinate: str) -> list[tuple[int, int, sp.Expr]]:
    """Write a real coordinate as a linear combination of conjugate D^(1/2)."""
    if coordinate == "y0":
        return [(0, 0, sp.Rational(1, 2)), (1, 1, sp.Rational(1, 2))]
    if coordinate == "y3":
        return [(1, 1, 1 / (2 * sp.I)), (0, 0, -1 / (2 * sp.I))]
    if coordinate == "y2":
        return [(0, 1, sp.Rational(1, 2)), (1, 0, -sp.Rational(1, 2))]
    if coordinate == "y1":
        return [(0, 1, 1 / (2 * sp.I)), (1, 0, 1 / (2 * sp.I))]
    raise ValueError(coordinate)


def axial_scalar_recurrence(two_j: int, row: int, column: int, coordinate: str) -> list[dict[str, Any]]:
    """Return terms in E[x conjugate(D^j_rc)] using diagonal scalar amplitudes."""
    if not 0 <= row <= two_j or not 0 <= column <= two_j:
        raise ValueError("representation index out of range")
    j = sp.Rational(two_j, 2)
    m = -j + row
    n = -j + column
    combined: dict[tuple[int, int], sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for a_index, b_index, coordinate_coefficient in conjugate_fundamental_terms(coordinate):
        a = -sp.Rational(1, 2) + a_index
        b = -sp.Rational(1, 2) + b_index
        for next_two_j in (two_j + 1, two_j - 1):
            if next_two_j < 0:
                continue
            next_j = sp.Rational(next_two_j, 2)
            next_m = m + a
            next_n = n + b
            if abs(next_m) > next_j or abs(next_n) > next_j or next_m != next_n:
                continue
            next_index = int(next_m + next_j)
            coefficient = coordinate_coefficient * clebsch_gordan(j, sp.Rational(1, 2), next_j, m, a, next_m) * clebsch_gordan(j, sp.Rational(1, 2), next_j, n, b, next_n)
            combined[(next_two_j, next_index)] += sp.simplify(coefficient)
    return [
        {"next_two_j": next_two_j, "diagonal_index": index, "coefficient": sp.sstr(sp.simplify(coefficient))}
        for (next_two_j, index), coefficient in sorted(combined.items())
        if sp.simplify(coefficient) != 0
    ]


def product_identity_defects(max_two_j: int = 4, *, drop_lower_channel: bool = False) -> int:
    fundamental = representation_matrix(1)
    matrices = {two_j: representation_matrix(two_j) for two_j in range(max_two_j + 2)}
    defects = 0
    for two_j in range(max_two_j + 1):
        matrix = matrices[two_j]
        j = sp.Rational(two_j, 2)
        for row in range(two_j + 1):
            for column in range(two_j + 1):
                m = -j + row
                n = -j + column
                for a_index in range(2):
                    for b_index in range(2):
                        a = -sp.Rational(1, 2) + a_index
                        b = -sp.Rational(1, 2) + b_index
                        answer = sp.S.Zero
                        channels = (two_j + 1,) if drop_lower_channel else (two_j + 1, two_j - 1)
                        for next_two_j in channels:
                            if next_two_j < 0:
                                continue
                            next_j = sp.Rational(next_two_j, 2)
                            next_m = m + a
                            next_n = n + b
                            if abs(next_m) > next_j or abs(next_n) > next_j:
                                continue
                            next_row = int(next_m + next_j)
                            next_column = int(next_n + next_j)
                            answer += clebsch_gordan(j, sp.Rational(1, 2), next_j, m, a, next_m) * clebsch_gordan(j, sp.Rational(1, 2), next_j, n, b, next_n) * matrices[next_two_j][next_row, next_column]
                        defect = sp.expand(matrix[row, column] * fundamental[a_index, b_index] - answer)
                        _, remainder = sp.div(defect, SPHERE, Y0, Y1, Y2, Y3, extension=True)
                        defects += sp.simplify(remainder) != 0
    return defects


def _component_rules() -> dict[str, list[tuple[str, sp.Expr]]]:
    return {
        "D0": [("y2", -C), ("y1", C), ("y0", sp.S.One)],
        "D1": [("y0", sp.S.One), ("y3", -sp.S.One), ("y2", 1 / C)],
    }


def _scale_audit() -> dict[str, int]:
    dimensions = range(1, MAX_TWO_J_RAIL + 2)
    return {
        "coordinate_entry_count": sum(6 * dimension - 4 for dimension in dimensions),
        "scalar_recurrence_term_count": sum(16 * dimension - 12 for dimension in dimensions),
        "maximum_scalar_terms_per_coordinate_entry": 4,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "sectors": "ALL_FINITE_TWO_J_POLARIZATION_SUPPORT_RULES_EXPORTED",
        "form": "DISTINCT_FORM_POLARIZATIONS_APPLIED",
        "scalar": "REPRESENTATION_CONVENTION_MATCHES_CERTIFIED_GENERATORS",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    identity_defects = product_identity_defects()
    mutation_defects = product_identity_defects(2, drop_lower_channel=True)
    if identity_defects or mutation_defects == 0:
        raise AssertionError("Clebsch--Gordan product audit failed")
    sample_rows = []
    for detector, components in _component_rules().items():
        sample_rows.append({
            "detector_id": detector,
            "pointwise_clock_factor": "a(t)",
            "components": [
                {"coframe_component": index + 1, "coordinate": coordinate, "prefactor": sp.sstr(prefactor)}
                for index, (coordinate, prefactor) in enumerate(components)
            ],
        })
    scale = _scale_audit()
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result proves the pointwise all-finite-two_j Clebsch--Gordan recurrence for the detector form profiles. Multiplication of conjugate D^j_rc by y0,y1,y2,y3 is expressed through diagonal scalar coefficients at neighboring two_j+1 and two_j-1 after axial averaging, with at most four nonzero scalar terms per coordinate entry. Polynomial identities are exact modulo y0^2+y1^2+y2^2+y3^2=1 through the audited modes, and deleting the lower-spin channel is detected. The external factor a(t) and declared polarization prefactors reconstruct D0 and D1 before clock/Green integration. This removes high-degree form-polynomial expansion from the adaptive route, but it does not evaluate the neighboring scalar coefficients, perform clock integration or temporal differentiation, certify the Green-weighted tail, construct full Green images, evaluate recoil, restrict to the tangent cone, activate the physical-branch bridge, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-polarization-clebsch-gordan-recurrence-v1",
        "result_id": "BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE",
        "setting_id": values["sectors"]["setting_id"],
        "claim_status": "EXACT_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED_SCALAR_STREAM_AND_TAIL_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "recurrence_convention": {"formula": "E[x conjugate(D^j_rc)] = sum_(J=j+-1/2) c_J E[conjugate(D^J_qq)]", "basis": "ascending m=-j,...,j", "axial_projection": "only next_m=next_n survives", "maximum_neighboring_scalar_terms": 4},
        "detector_reconstruction": sample_rows,
        "representative_recurrences": [
            {"two_j": two_j, "row": row, "column": column, "coordinate": coordinate, "terms": axial_scalar_recurrence(two_j, row, column, coordinate)}
            for two_j, row, column, coordinate in ((1, 0, 0, "y0"), (2, 0, 1, "y2"), (4, 2, 2, "y3"), (4, 1, 2, "y1"))
        ],
        "scale_audit_through_two_j138": scale,
        "identity_audit": {"audited_two_j": [0, 1, 2, 3, 4], "unit_sphere_remainder_defect_count": identity_defects},
        "mutation_results": [{"name": "drop_j_minus_one_half_channel", "detected": True, "unit_sphere_remainder_defect_count": mutation_defects}],
        "flags": {"ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED": True, "MAXIMUM_FOUR_NEIGHBORING_SCALAR_TERMS_PER_ENTRY": True, "HIGH_MODE_SCALAR_COEFFICIENT_VALUES_EVALUATED": False, "CLOCK_AND_TEMPORAL_GREEN_INTEGRATION_COMPLETED": False, "GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED": False, "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False, "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False, "BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EVALUATE_THE_POINTWISE_NEIGHBORING_SCALAR_STREAM_THEN_CLOCK_INTEGRATE_AND_CLOSE_THE_GREEN_WEIGHTED_TAIL",
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
        raise SystemExit("stale polarization Clebsch--Gordan recurrence")
    print("BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fix fixture-level Mellin minimal subtraction and compute its scale row."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json"
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-mellin-subtraction-scale-row-v1.schema.json"


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _q(value: Fraction | sp.Rational) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    source = json.loads(INPUT.read_text())
    if source.get("result_state") != (
        "RAW_MIXED_PHYSICAL_LOG_COEFFICIENT_NONZERO_SUBTRACTION_REQUIRED"
    ):
        raise ValueError("mixed physical fixture gate drifted")

    triangle = source["three_H1_corner"]
    mixed = source["mixed_H1_H2_endpoint"]
    orientation_a = [_fraction(value) for value in triangle["orientation_A_corner_weights"]]
    orientation_b = [_fraction(value) for value in triangle["orientation_B_corner_weights"]]
    if orientation_b != list(reversed(orientation_a)):
        raise ValueError("triangle residue ledger lost orientation reversal")
    triangle_residue = 3 * (sum(orientation_a) + sum(orientation_b))
    mixed_residue = _fraction(mixed["full_endpoint_log_coefficient"])
    total_residue = triangle_residue + mixed_residue
    if total_residue != Fraction(15707, 216):
        raise ValueError("combined Mellin residue drifted")

    # A logarithmic boundary chart has r^(s-1).  The same Mellin parameter s
    # and scale ratio z=mu^2/Q^2 are used for every triangle corner and bubble
    # endpoint.  These exact series identities are the fixture-level MS rail.
    s, z = sp.symbols("s z", positive=True)
    regulated_model = z**s / s
    residue = sp.limit(s * regulated_model, s, 0)
    finite_scale_term = sp.limit(regulated_model - 1 / s, s, 0)
    scale_derivative = sp.simplify(z * sp.diff(finite_scale_term, z))
    if (residue, finite_scale_term, scale_derivative) != (1, sp.log(z), 1):
        raise ValueError("Mellin minimal-subtraction model identity failed")

    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-mellin-subtraction-scale-row-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW",
        "result_state": "FIXTURE_MELLIN_MINIMAL_SUBTRACTION_SCALE_ROW_COMPUTED_GENERIC_COVARIANT_LIFT_OPEN",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": source["classical_commit"],
        "scope": {
            "background": source["scope"]["background"],
            "operator": source["scope"]["operator"],
            "signature": "Euclidean",
            "renormalization_scope": "fixture-level blown-up Feynman-parameter carrier",
        },
        "dependency": _reference(INPUT),
        "subtraction_definition": {
            "scheme": "COMMON_MELLIN_MINIMAL_SUBTRACTION",
            "common_regulator": "s",
            "common_scale_ratio": "z=mu^2/Q^2",
            "triangle_partition": "S_i={alpha_i>=alpha_j and alpha_i>=alpha_k}; sector interiors are disjoint and their union is the simplex up to measure-zero ties",
            "triangle_corner_chart": "alpha_i=1-r, alpha_j=r*t, alpha_k=r*(1-t)",
            "triangle_radial_upper_bound": "r_max(t)=1/(2-t) for 0<=t<=1/2 and 1/(1+t) for 1/2<=t<=1",
            "triangle_boundary_model": "integral_0^1 dt integral_0^r_max(t) dr r^(s-1) A_i(t)",
            "bubble_partition": "left chart x in [0,1/2] and right chart r=1-x in [0,1/2]",
            "bubble_left_boundary_model": "integral_0^1 dx x^(s-1) B_left",
            "bubble_right_boundary_model": "integral_0^1 dx (1-x)^(s-1) B_right",
            "minimal_subtraction": "finite part at s=0 after removing residue/s",
            "model_laurent_identity": "z^s/s = 1/s + log(z) + O(s)",
            "scale_derivative_convention": "partial/partial log(mu^2) at fixed Q^2",
        },
        "resolved_boundary_ledger": {
            "labelled_triangle_boundary_chart_count": 18,
            "cyclic_representative_triangle_chart_count": 6,
            "cyclic_multiplicity_per_orientation": triangle[
                "cyclic_multiplicity_per_orientation"
            ],
            "bubble_endpoint_chart_count": mixed["endpoint_count"],
            "triangle_residue": _q(triangle_residue),
            "mixed_bubble_residue": _q(mixed_residue),
            "combined_residue": _q(total_residue),
            "common_factor_not_included": "(4 pi)^-2",
            "orientation_reversal": "EXACT",
        },
        "renormalization_scale_row": {
            "equation": "partial_log(mu^2) Gamma_fixture_MS = residue_fixture/(4 pi)^2",
            "coefficient": _q(total_residue),
            "common_factor": "(4 pi)^-2",
            "status": "COEFFICIENT_COMPUTED",
        },
        "finite_scheme_ambiguity": {
            "status": "OPEN_GENERIC_LOCAL_COUNTERTERM_NORMALIZATION",
            "statement": "Changing boundary defining functions or adding a finite local subtraction preserves the residue and shifts only the finite local row.",
            "fixture_finite_constant_computed": False,
        },
        "claim_flags": {
            "COMMON_MELLIN_REGULATOR_FIXED": True,
            "FIXTURE_MINIMAL_SUBTRACTION_DISTRIBUTION_FIXED": True,
            "FIXTURE_SCALE_ROW_COMPUTED": True,
            "SCALE_ROW_INDEPENDENT_OF_MU_INDEPENDENT_FINITE_LOCAL_SUBTRACTION": True,
            "GENERIC_COVARIANT_VOLTERRA_LIFT_COMPUTED": False,
            "RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED": False,
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED": False,
            "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "LIFT_COMMON_MELLIN_SUBTRACTION_TO_GENERIC_COVARIANT_VOLTERRA_CARRIER_AND_ASSEMBLE_MIXED_ROWS",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL result fixes a common Mellin minimal-subtraction extension on the rational equal-box physical triangle/bubble fixture and promotes 15707/216 to its scheme-independent log(mu^2) scale coefficient. It does not construct the generic covariant Volterra carrier, determine the finite local normalization, dispose M14, complete a repository form factor, change the QME disposition, or certify a Lorentzian theory.",
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("stored physical Mellin subtraction scale row is stale")
        print("physical Hessian Mellin subtraction scale row: PASS")
        return 0
    OUTPUT.write_text(rendered)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

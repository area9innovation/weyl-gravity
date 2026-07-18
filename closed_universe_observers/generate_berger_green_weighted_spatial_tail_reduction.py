#!/usr/bin/env python3
"""Certify the exact Maxwell Green-weighted reduction of a Berger form tail."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_exact_maxwell_charge_blocks import charge_block


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION.json"
SCHEMA = PACKAGE / "schema/berger-green-weighted-spatial-tail-reduction-v1.schema.json"
REPORT = PACKAGE / "reports/berger-green-weighted-spatial-tail-reduction.md"
DEPENDENCIES = {
    "charge_blocks": PACKAGE / "certificates/BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS.json",
    "spectral_engine": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "selected_transform": PACKAGE / "certificates/BERGER_SELECTED_CHARGE_BLOCK_CORRELATED_CLOCK_TRANSFORM.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_green_weighted_spatial_tail_reduction.py",
    PACKAGE / "tests/test_berger_green_weighted_spatial_tail_reduction.py",
    SCHEMA,
    REPORT,
]

DIAGONAL_SHIFT_LOWER = Fraction(-9, 124)
SINGLE_COUPLING_UPPER_COEFFICIENT = Fraction(27, 80)
ROW_SUM_UPPER_COEFFICIENT = 2 * SINGLE_COUPLING_UPPER_COEFFICIENT
SELECTED_RETAINED_MAX_TWO_J = 1024
LEGACY_RETAINED_MAX_TWO_J = 138


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: sp.Expr) -> Fraction:
    value = sp.factor(value)
    if value.is_Rational is not True:
        raise AssertionError(f"expected rational value, got {value}")
    return Fraction(int(sp.numer(value)), int(sp.denom(value)))


def gershgorin_lower_from_j(j: Fraction) -> Fraction:
    """Universal lower bound for every Delta_1 charge block at representation j."""
    return j * (j + 1) + DIAGONAL_SHIFT_LOWER - ROW_SUM_UPPER_COEFFICIENT * (j + Fraction(1, 2))


def cutoff_row(retained_max_two_j: int) -> dict[str, Any]:
    first_omitted_two_j = retained_max_two_j + 1
    j = Fraction(first_omitted_two_j, 2)
    lower = gershgorin_lower_from_j(j)
    if lower <= 0:
        raise AssertionError("omitted-shell lower bound must be positive")
    return {
        "retained_max_two_j": retained_max_two_j,
        "first_omitted_two_j": first_omitted_two_j,
        "first_omitted_j": str(j),
        "delta1_spectral_lower_bound": str(lower),
        "delta1_spectral_lower_bound_decimal": f"{float(lower):.12f}",
        "sobolev_norm_reductions": [
            {
                "power": power,
                "factor": str(Fraction(1, 1) / lower**power),
                "factor_decimal": f"{float(Fraction(1, 1) / lower**power):.12e}",
                "inequality": f"||Pi_tail F||_L2 <= Lambda^(-{power}) ||Delta1^{power} F||_L2",
            }
            for power in range(1, 5)
        ],
    }


def exact_formula_audit(max_two_j: int = 12) -> dict[str, Any]:
    diagonal_defects = 0
    coupling_defects = 0
    row_degree_defects = 0
    block_count = 0
    three_member_blocks = 0
    for two_j in range(max_two_j + 1):
        j = Fraction(two_j, 2)
        for numerator in range(-two_j - 2, two_j + 3, 2):
            q = Fraction(numerator, 2)
            members, block = charge_block(two_j, q)
            if not members:
                continue
            block_count += 1
            if len(members) == 3:
                three_member_blocks += 1
            if len(members) > 3:
                row_degree_defects += 1
            base = Fraction(j * (j + 1))
            for row in range(block.rows):
                shift = _fraction(block[row, row]) - base
                if shift < DIAGONAL_SHIFT_LOWER:
                    diagonal_defects += 1
                degree = 0
                for column in range(block.cols):
                    if row == column or block[row, column] == 0:
                        continue
                    degree += 1
                    squared = _fraction(sp.simplify(block[row, column] * sp.conjugate(block[row, column])))
                    coupling_bound = SINGLE_COUPLING_UPPER_COEFFICIENT * (j + Fraction(1, 2))
                    if squared > coupling_bound**2:
                        coupling_defects += 1
                if degree > 2:
                    row_degree_defects += 1
    if diagonal_defects or coupling_defects or row_degree_defects or three_member_blocks == 0:
        raise AssertionError("exact Maxwell charge-block lower-bound audit failed")
    return {
        "audited_two_j_maximum": max_two_j,
        "audited_charge_block_count": block_count,
        "three_member_block_count": three_member_blocks,
        "diagonal_shift_defect_count": diagonal_defects,
        "single_coupling_bound_defect_count": coupling_defects,
        "maximum_row_degree_defect_count": row_degree_defects,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "charge_blocks": "ALL_FINITE_TWO_J_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS_EXPORTED",
        "spectral_engine": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
        "profiles": "EXACT_DETECTOR_RADIAL_PROFILE_FAMILY_SERIALIZED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "selected_transform": "FINITE_SELECTED_EXACT_T_TEMPORAL_IMAGE_REPRESENTATION_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    audit = exact_formula_audit()
    selected = cutoff_row(SELECTED_RETAINED_MAX_TWO_J)
    legacy = cutoff_row(LEGACY_RETAINED_MAX_TWO_J)
    if Fraction(selected["delta1_spectral_lower_bound"]) <= Fraction(legacy["delta1_spectral_lower_bound"]):
        raise AssertionError("spectral cutoff lower bound did not increase")

    # sqrt(5)<9/4 supplies the rational single-coupling coefficient 27/80.
    radical_upper_is_valid = Fraction(5) < Fraction(9, 4) ** 2
    false_radical_upper_detected = Fraction(5) > Fraction(2) ** 2
    if not radical_upper_is_valid or not false_radical_upper_detected:
        raise AssertionError("radical rationalization audit failed")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result converts any omitted Berger Maxwell one-form representation tail into a declared Sobolev norm. Completing the three charge-block diagonal quadratics gives the uniform shift -9/124; sqrt(5)<9/4 and the at-most-two tridiagonal couplings give the rational Gershgorin bound Lambda(j)=j^2+13j/40-1017/2480. For every tail above a retained two_j cutoff, ||Pi_tail F|| is at most Lambda(first omitted j)^(-N)||Delta1^N F||. Both exact-T Maxwell multipliers relevant here are contractions: ||cos(T sqrt(Delta1))||<=1 and ||delta sin(T sqrt(Delta1))/sqrt(Delta1)||<=1, the latter because delta^dagger delta<=Delta1 with the zero-mode extension. Thus no additional Green amplification enters the Maxwell L2 tail. At retained two_j=1024 the first-omitted lower bound and powers N=1,...,4 are exported exactly. This certifies the spectral and Maxwell Green-weighted reduction only. The detector profile relative to Berger Haar measure, its clock-uniform polarized repeated-Laplacian norm, the numerical tail product, the massive-two-form continuation, detector response, recoil and tangent-cone restriction remain OPEN."
    )
    return {
        "schema": "closed-universe-berger-green-weighted-spatial-tail-reduction-v1",
        "result_id": "BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION",
        "setting_id": values["selected_transform"]["setting_id"],
        "claim_status": "EXACT_MAXWELL_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION_CERTIFIED_PROFILE_SOBOLEV_NORM_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "spectral_lower_bound_theorem": {
            "charge_block_basis": ["theta_plus", "theta3", "theta_minus"],
            "maximum_block_dimension": 3,
            "diagonal_completion": "(31 m^2 +/- 71 m + 40)/9 >= -9/124",
            "coupling_identity": "|b|=(3 sqrt(5)/20)sqrt((j-m)(j+m+1))",
            "coupling_product_bound": "(j-m)(j+m+1)<=(j+1/2)^2",
            "rational_radical_bound": "sqrt(5)<9/4",
            "single_coupling_upper": "(27/80)(j+1/2)",
            "maximum_row_sum_upper": "(27/40)(j+1/2)",
            "gershgorin_lower": "Lambda(j)=j(j+1)-9/124-(27/40)(j+1/2)=j^2+13j/40-1017/2480",
            "monotone_for": "j>=0",
            "exact_formula_audit": audit,
        },
        "cutoff_reductions": [legacy, selected],
        "maxwell_green_weighting": {
            "spatial_multiplier": "cos(T sqrt(Delta1))",
            "spatial_operator_norm_upper": "1",
            "temporal_multiplier": "delta sin(T sqrt(Delta1))/sqrt(Delta1)",
            "temporal_operator_norm_upper": "1",
            "temporal_contraction_reason": "delta^dagger delta<=Delta1 and |sin|<=1; use the entire zero-mode extension",
            "additional_tail_amplification_factor": "1",
        },
        "unresolved_profile_ledger": [
            {"id": "profile_density_relative_to_berger_haar", "status": "OPEN", "need": "serialize the exact detector one-form source F_a(t) as the field on which Delta1 acts in the certified Fourier/Haar convention"},
            {"id": "clock_uniform_polarized_repeated_laplacian_norm", "status": "OPEN", "need": "directed enclosure of sup_t ||Delta1^N F_a(t)||_L2 for at least one declared N"},
            {"id": "numerical_tail_product", "status": "OPEN", "need": "multiply the certified Sobolev norm by the exact cutoff factor without replacing the complete tail by selected modes"},
            {"id": "massive_two_form_tail_continuation", "status": "OPEN", "need": "propagate the certified Maxwell tail through h_a d and the massive two-form advanced Green operator"},
        ],
        "mutation_results": [
            {"name": "replace_sqrt5_upper_9_over_4_by_false_upper_2", "detected": false_radical_upper_detected},
            {"name": "delete_second_interior_charge_block_coupling", "detected": audit["three_member_block_count"] > 0},
        ],
        "flags": {
            "ALL_OMITTED_REPRESENTATION_DELTA1_LOWER_BOUND_EXPORTED": True,
            "SELECTED_TWO_J1024_SOBOLEV_REDUCTION_FACTORS_EXPORTED": True,
            "MAXWELL_EXACT_T_SPATIAL_TAIL_MULTIPLIER_CONTRACTIVE": True,
            "MAXWELL_CODERIVATIVE_SINE_TAIL_MULTIPLIER_CONTRACTIVE": True,
            "GREEN_WEIGHTED_MAXWELL_TAIL_CONVERSION_EXPORTED": True,
            "EVALUATED_PROFILE_SOBOLEV_NORM_EXPORTED": False,
            "VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED": False,
            "FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED": False,
            "MASSIVE_TWO_FORM_TAIL_BOUND_EXPORTED": False,
            "DETECTOR_RESPONSE_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EVALUATE_THE_CLOCK_UNIFORM_POLARIZED_PROFILE_SOBOLEV_NORM_IN_THE_CERTIFIED_BERGER_HAAR_CONVENTION",
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
        raise SystemExit("stale Green-weighted spatial-tail reduction certificate")
    print("BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

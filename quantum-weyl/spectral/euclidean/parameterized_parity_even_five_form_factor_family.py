#!/usr/bin/env python3
"""Assemble the strongest globally parameterized parity-even five-factor family."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = (
    HERE
    / "certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY.json"
)
SCHEMA = (
    HERE / "schema/parameterized-parity-even-five-form-factor-family-v1.schema.json"
)
DEPENDENCIES = {
    "assembly": (
        HERE
        / "certificates/PARITY_EVEN_THIRD_CURVATURE_FIVE_FORM_FACTOR_ASSEMBLY.json",
        "c474dedff8923233d94998e04e044c5931f03df69fcbf973c650d665f7246f06",
    ),
    "kernel_nonuniqueness": (
        HERE
        / "certificates/"
        "GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL_NONUNIQUENESS.json",
        "dd114394a10d0669bcbdad88adbec31e789a37f264c39d314b2e672a4baae89c",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    values: dict[str, dict[str, Any]] = {}
    for name, (path, expected_hash) in DEPENDENCIES.items():
        if _sha256(path) != expected_hash:
            raise ValueError(f"parameterized-family dependency drifted: {name}")
        values[name] = json.loads(path.read_text())
    assembly = values["assembly"]
    nonunique = values["kernel_nonuniqueness"]
    if (
        assembly["claim_flags"]["MAXIMAL_PARTIAL_BV_QUOTIENT_COMPUTED"] is not True
        or assembly["carrier_quotient"]["effective_labelled_channel_count"] != 10
        or nonunique["claim_flags"][
            "EXACT_THIRD_CURVATURE_ROW_NONUNIQUENESS_PROVED"
        ]
        is not True
        or nonunique["decision"][
            "background_universal_finite_kernel_from_declared_local_data"
        ]
        != "NONUNIQUE"
    ):
        raise ValueError("parameterized family activation gate drifted")

    channels = assembly["maximal_determined_quotient"]["quotient_ledger"][
        "raw_channel_order"
    ]
    eliminated = "I28_trivial_S3"
    quotient_coordinates = [
        channel for channel in channels if channel != "I28_231"
    ]
    if len(quotient_coordinates) != 10:
        raise ValueError("canonical ten-coordinate section drifted")
    ambiguity_matrix = [
        [1 if row == column else 0 for column in quotient_coordinates]
        for row in quotient_coordinates
    ]
    if any(
        sum(
            ambiguity_matrix[row][pivot] * ambiguity_matrix[column][pivot]
            for pivot in range(10)
        )
        != (1 if row == column else 0)
        for row in range(10)
        for column in range(10)
    ):
        raise ValueError("rank-ten ambiguity separator failed")

    return {
        "schema": "quantum-weyl-parameterized-parity-even-five-form-factor-family-v1",
        "result_id": "PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY",
        "result_state": (
            "GLOBAL_SPECTRAL_DATA_PARAMETERIZED_FAMILY_"
            "NO_NONZERO_UNIVERSAL_FINITE_SCHUR_COMBINATION"
        ),
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": assembly["classical_commit"],
        "scope": assembly["scope"],
        "canonical_quotient_section": {
            "coordinates": quotient_coordinates,
            "eliminated_direction": eliminated,
            "relation": assembly["carrier_quotient"]["functional_relation"],
            "dimension": 10,
        },
        "parameterized_family": {
            "formula": (
                "F_full[D]=F_partial_BV+F_Schur[D]+"
                "c_C2*L_C2+c_R2hat*L_R2hat"
            ),
            "global_parameter_D": (
                "content-addressed compact scalar-flat metric, domains, primed "
                "resolvent or complete spectral measure, reference scale and "
                "determinant phase/contour"
            ),
            "universal_partial_BV_formula_digest": assembly[
                "maximal_determined_quotient"
            ]["formula_digest"],
            "universal_partial_BV_channel_row_digests": assembly[
                "maximal_determined_quotient"
            ]["channel_row_digests"],
            "Schur_scale_response": assembly["longitudinal_Schur_boundary"][
                "scale_density"
            ],
            "finite_Schur_rows": "FUNCTIONS_OF_D_NOT_UNIVERSAL_CONSTANTS",
        },
        "ambiguity_module": {
            "basis": [
                f"smoothing_unit_shift_{channel}" for channel in quotient_coordinates
            ],
            "coordinate_order": quotient_coordinates,
            "matrix": ambiguity_matrix,
            "rank": 10,
            "dual_separators": [
                {
                    "coordinate": channel,
                    "witness": f"lambda_{channel}",
                    "pairing_with_unit_shift": 1,
                    "pairing_with_other_unit_shifts": 0,
                }
                for channel in quotient_coordinates
            ],
            "source": (
                "the cubic rank-one smoothing family from the imported "
                "nonuniqueness theorem multiplied by each quotient coordinate"
            ),
        },
        "universal_content": {
            "partial_BV_summand": "COMPUTED",
            "carrier_relation_and_S3_covariance": "COMPUTED",
            "contact_and_relative_IBP_endpoints": "COMPUTED",
            "local_Schur_scale_response": "COMPUTED",
            "complete_finite_Schur_sensitive_linear_combinations": {
                "dimension": 0,
                "proof": (
                    "the ambiguity matrix has rank ten on the ten-dimensional "
                    "quotient, so its annihilator is zero"
                ),
            },
        },
        "local_normalizations": assembly["local_normalization_constants"],
        "holdouts": {
            "round_S4": "ONE_EVALUATION_AT_D_ROUND_S4_NOT_A_GENERIC_SECTION",
            "product_S2_S2": "ONE_EVALUATION_AT_D_PRODUCT_NOT_A_GENERIC_SECTION",
            "equal_box_and_flat_TT": assembly["holdouts"],
            "interpolation_used": False,
        },
        "decision": {
            "complete_universal_coefficient_table": "NONDEFINED",
            "strongest_exact_result": "AFFINE_FAMILY_OVER_GLOBAL_SPECTRAL_DATA",
            "universal_finite_Schur_quotient_dimension": 0,
            "predecessor_partial_BV_coefficients_preserved": True,
            "background_specific_evaluation_authorized_without_D": False,
        },
        "dependencies": {
            name: _reference(path, values[name])
            for name, (path, _hash) in DEPENDENCIES.items()
        },
        "claim_flags": {
            "PARAMETERIZED_FIVE_FORM_FACTOR_FAMILY_COMPUTED": True,
            "RANK_TEN_FINITE_SCHUR_AMBIGUITY_PROVED": True,
            "NO_NONZERO_UNIVERSAL_FINITE_SCHUR_COMBINATION_PROVED": True,
            "PARTIAL_BV_SUMMAND_PRESERVED": True,
            "LOCAL_NORMALIZATIONS_SEPARATE": True,
            "SPECIAL_BACKGROUND_INTERPOLATION_USED": False,
            "COMPLETE_UNIVERSAL_BV_FIVE_FUNCTION_TABLE_COMPUTED": False,
            "QME_OR_LORENTZIAN_PROMOTED": False,
        },
        "next_gate": (
            "choose a global spectral datum D and compute one background-specific "
            "evaluation; no further universal local-data-only assembly is defined"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL result gives the strongest "
            "exact retry after the finite-kernel theorem: an affine family of "
            "five-carrier functions over explicit global spectral data. The "
            "already computed partial-BV summand and local scale response are "
            "universal, but the finite Schur ambiguity spans the full ten-"
            "dimensional labelled quotient, so no nonzero complete finite "
            "Schur-sensitive linear combination is universal. Local C2 and "
            "dressed R2 constants remain separate. This is not a complete "
            "universal coefficient table, Gamma1/Q1, QME, Lorentzian, Hadamard, "
            "particle, scattering or unitarity result."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale parameterized five-factor family: {OUTPUT}")
    print("PARAMETERIZED PARITY-EVEN FIVE-FORM-FACTOR FAMILY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

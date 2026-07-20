#!/usr/bin/env python3
"""Freeze the maximal generic parity-even five-form-factor assembly boundary."""

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
    / "certificates/PARITY_EVEN_THIRD_CURVATURE_FIVE_FORM_FACTOR_ASSEMBLY.json"
)
SCHEMA = (
    HERE
    / "schema/parity-even-third-curvature-five-form-factor-assembly-v1.schema.json"
)

SOURCES = {
    "carrier_manifest": (
        ROOT
        / "quantum-weyl/transfer/certificates/"
        "FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
        "203cc58ea7d2b1cfd468bc660c616e8319250ab522614bcbc16410b1c7006c4c",
    ),
    "physical_H1_cubed_channels": (
        HERE
        / "certificates/"
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json",
        "21a28ad483c8964390306b7dc6c8cd7c5ab5c1dcfb577eda0acad81f70bfc23b",
    ),
    "six_master_coordinates": (
        HERE
        / "certificates/"
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_SIX_MASTER_COORDINATES.json",
        "d205896de6c5f2d6a534889e9bdb566a590b9e2c47a28d1def2ff5585994de9c",
    ),
    "relative_IBP_boundary_flux": (
        HERE
        / "certificates/"
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json",
        "ac587092ac6c7415e09d0b7e0541604e9622c7664d89c6a0c767dc9cac70368f",
    ),
    "H1_H2_contact_finite_rows": (
        HERE
        / "certificates/"
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_ROWS.json",
        "e9e6661a5994e90fed7f7f45eb7a19481a721cad41f24b41e104955a9396c940",
    ),
    "physical_five_form_factors": (
        HERE
        / "certificates/"
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS.json",
        "35d7d8c96bca681d61e72f16ca64db8b9af00ad1dc6f90475cca3ce7e65671b2",
    ),
    "maximal_partial_BV_form_factors": (
        HERE
        / "certificates/"
        "GENERIC_BACKGROUND_PARTIAL_BV_THIRD_CURVATURE_FORM_FACTORS.json",
        "8797773521188acf0e9a4bfae4b08aca7399deeb3439d8ccc989a69c7ffdcc95",
    ),
    "full_BV_multiplicity": (
        HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
        "5bdc6ee4674e3a58ab0da0d4f8dc848ac7eebc4b84544c2079dee766362b9970",
    ),
    "longitudinal_Schur_resummation": (
        HERE
        / "certificates/"
        "GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
        "b40ec3a8bd3a21d8e0ece7c98f98e1776e8c47d557b8c8b5427e422b60c65a78",
    ),
    "longitudinal_Schur_scale": (
        HERE
        / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
        "8073ad3800d4ad9662232769efeb45971e49b5eaf1f4b933714245d85771bd1d",
    ),
    "round_S4_holdout": (
        HERE
        / "certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
        "b16768333e62f624720130d1c922b42772f10bf7ad10ee1ac27832c847588591",
    ),
    "product_S2_S2_weighted_holdout": (
        HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS.json",
        "f2fcd5674c2ade12534a50acca4fcbe2056626cc2daa1f229122a303d837ff9d",
    ),
    "product_S2_S2_det3_holdout": (
        HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE.json",
        "0aaf843e0eb7d771b7ac29a1ec5ef4d7c0d0a79797bdc09c3ee049c9872fa094",
    ),
    "flat_TT_normalization": (
        HERE
        / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
        "b8fd2da678cb64d0bae6adaacb888beb49af3d3e45ddd9bce93005fb9018e9f9",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reference(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    values: dict[str, dict[str, Any]] = {}
    for name, (path, expected_hash) in SOURCES.items():
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise ValueError(f"pinned dependency hash drifted: {name}")
        values[name] = json.loads(path.read_text())

    manifest = values["carrier_manifest"]
    h1 = values["physical_H1_cubed_channels"]
    masters = values["six_master_coordinates"]
    flux = values["relative_IBP_boundary_flux"]
    contact = values["H1_H2_contact_finite_rows"]
    physical = values["physical_five_form_factors"]
    partial = values["maximal_partial_BV_form_factors"]
    multiplicity = values["full_BV_multiplicity"]
    schur = values["longitudinal_Schur_resummation"]
    scale = values["longitudinal_Schur_scale"]
    round_s4 = values["round_S4_holdout"]
    product_rows = values["product_S2_S2_weighted_holdout"]
    product_det3 = values["product_S2_S2_det3_holdout"]
    flat = values["flat_TT_normalization"]

    if (
        manifest["claim_flags"][
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"
        ]
        is not True
        or manifest["raw_module"]["generic_label_orbit_dimension"] != 11
        or manifest["quotient_module"]["generic_label_orbit_dimension"] != 10
        or len(h1["projection_rows"]) != 11
        or masters["claim_flags"]["ALL_ELEVEN_CHANNELS_COORDINATED"] is not True
        or flux["claim_flags"]["ALL_ELEVEN_CHANNELS_INTEGRATED"] is not True
        or contact["claim_flags"]["ALL_THREE_CONTACT_FINITE_ROWS_PROJECTED"]
        is not True
        or physical["claim_flags"]["FIVE_PHYSICAL_CARRIER_FUNCTIONS_ASSEMBLED"]
        is not True
        or partial["claim_flags"][
            "PARTIAL_BV_FIVE_CARRIER_REPRESENTATIVE_COMPUTED"
        ]
        is not True
        or multiplicity["integration_slice"]["all_rows_accounted"] is not True
        or multiplicity["cancellations"]["factor_coverage_status"] != "VERIFIED"
        or schur["claim_flags"][
            "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED"
        ]
        is not True
        or scale["claim_flags"]["SCHUR_SCALE_COEFFICIENT_COMPUTED"] is not True
        or scale["claim_flags"]["REFERENCE_FINITE_R_K_COMPUTED"] is not False
        or scale["claim_flags"]["REFERENCE_FINITE_R_K2_COMPUTED"] is not False
        or round_s4["claim_flags"]["ROUND_S4_R_DELTA_K_COMPUTED"] is not True
        or product_rows["claim_flags"]["PRODUCT_WEIGHTED_R_K_COMPUTED"]
        is not True
        or product_det3["claim_flags"][
            "PRODUCT_REGULAR_COMPLEMENT_DET3_VALUE_COMPUTED"
        ]
        is not True
        or flat["repository_normalization"]["flat_TT_leading_coefficient"]
        != {"numerator": 1, "denominator": 2}
    ):
        raise ValueError("five-form-factor input gate drifted")

    maximal_payload = {
        "formula_digest": partial["formula_digest"],
        "function_basis": partial["function_basis"],
        "quotient_ledger": partial["quotient_ledger"],
        "channel_row_digests": {
            row["channel_id"]: _digest(row) for row in partial["channel_rows"]
        },
    }
    result = {
        "schema": (
            "quantum-weyl-parity-even-third-curvature-"
            "five-form-factor-assembly-v1"
        ),
        "result_id": "PARITY_EVEN_THIRD_CURVATURE_FIVE_FORM_FACTOR_ASSEMBLY",
        "result_state": (
            "MAXIMAL_PARTIAL_BV_FIVE_CARRIER_QUOTIENT_COMPUTED_"
            "FULL_BV_NONDEFINED_BY_MISSING_GENERIC_SCHUR_FINITE_KERNEL"
        ),
        "lifecycle_state": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": partial["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic scalar-flat nonexceptional momentum chart",
            "parity": "EVEN",
            "subtraction": (
                "common resolved-boundary Mellin minimal subtraction with "
                "weighted proper-time Schur determinant at reference scale mu_0"
            ),
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "carrier_quotient": {
            "carrier_function_count": 5,
            "raw_labelled_channel_count": 11,
            "effective_labelled_channel_count": 10,
            "functional_relation": partial["quotient_ledger"]["unique_relation"],
            "functional_relation_status": partial["quotient_ledger"][
                "relation_status"
            ],
            "source_permutation_covariance": (
                "the manifest S3 modules and the stored label_order on every "
                "orientation channel are retained"
            ),
        },
        "maximal_determined_quotient": {
            "status": "COEFFICIENT_COMPUTED_PARTIAL_BV",
            "included_sectors": partial["scope"]["included_sectors"],
            "excluded_sectors": partial["scope"]["excluded_sectors"],
            **maximal_payload,
            "scale_status": (
                "physical scale rows are included channelwise; the generic "
                "longitudinal Schur scale response is known only in the local "
                "Ricci basis and is not projected as a finite five-carrier row"
            ),
        },
        "local_normalization_constants": {
            "strict_C2": {
                "status": "UNFIXED_ADDITIVE_LOCAL_CONSTANT",
                "folded_into_nonlocal_functions": False,
            },
            "dressed_R2": {
                "status": (
                    "SEPARATE_ACTION_DEPENDENT_CONSTANT_OUTSIDE_THE_STRICT_"
                    "SCALAR_FLAT_CARRIER"
                ),
                "folded_into_nonlocal_functions": False,
            },
        },
        "holdouts": {
            "equal_box_contact": {
                "status": "EXACT",
                "data": contact["equal_box_regression"],
            },
            "flat_TT": {
                "status": "EXACT_NORMALIZATION_ONLY",
                "leading_coefficient": flat["repository_normalization"][
                    "flat_TT_leading_coefficient"
                ],
            },
            "round_S4": {
                "status": "SPECIAL_BACKGROUND_EXACT_NOT_INTERPOLATED",
                "zero_mode_policy_applied": round_s4["claim_flags"][
                    "ROUND_S4_ZERO_MODE_POLICY_APPLIED"
                ],
                "finite_rows_digest": _digest(round_s4["exact_finite_rows"]),
            },
            "product_S2_S2": {
                "status": "SPECIAL_BACKGROUND_RIGOROUS_INTERVAL_NOT_INTERPOLATED",
                "weighted_rows_digest": _digest(product_rows["weighted_rows"]),
                "det3_enclosure_digest": _digest(product_det3["det3_enclosure"]),
            },
        },
        "longitudinal_Schur_boundary": {
            "normalized_operator": schur["exact_determinant_factorization"][
                "normalized_scalar_Schur_operator"
            ],
            "scale_response": scale["Schur_determinant_scale_row"][
                "scale_response"
            ],
            "scale_density": scale["Schur_determinant_scale_row"]["Ricci_basis"],
            "reference_finite_R_K": "NOT_COMPUTED",
            "reference_finite_R_K2": "NOT_COMPUTED",
            "full_regularized_determinant": "NOT_COMPUTED",
        },
        "first_missing_analytic_datum": {
            "datum_id": "GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL",
            "why_first": (
                "the exact Schur factorization has reduced the three open "
                "longitudinal Diff-Weyl towers to one scalar trace-log, but "
                "symbol and Wodzicki data determine only its scale response; "
                "finite weighted traces change under smoothing perturbations"
            ),
            "nondefinition_witness": round_s4["generic_missing_input_theorem"],
            "receiver_contract": {
                "background": (
                    "generic closed scalar-flat Euclidean four-manifold, or a "
                    "declared local generic chart with a compatible global completion"
                ),
                "operator": (
                    "S_L(W)=(2/3)I+(1/3)delta(F+W)^(-1)d on the same "
                    "primed scalar complement used by the vector ghost"
                ),
                "weight": (
                    "Q_mu=(Delta_0+Pi_0)/mu^2 with Pi_0 restoring only the "
                    "deleted scalar zero modes before restriction"
                ),
                "required_data": [
                    "content-addressed primed Green/resolvent kernel for F+W",
                    "common-domain scalar weight kernel or equivalent complete spectral measure",
                    "reference finite R_mu0(K) and finite-part R_mu0(K^2)",
                    "det_3(I+K) remainder through curvature order three",
                    "five-carrier functional variations with labelled Box_i and S3 action",
                    "zero-mode projector and exceptional-mode ledger",
                    "branch, regularity and boundary-condition domains",
                ],
                "required_checks": [
                    "reproduce the certified Schur Wodzicki scale density",
                    "reproduce round-S4 exact finite rows under specialization",
                    "fall inside the rigorous S2(1)xS2(2) intervals under specialization",
                    "preserve the I28 coefficientwise relation",
                    "reject a zero-mode projector mutation",
                ],
                "regularization": (
                    "same Mellin/proper-time subtraction and reference scale "
                    "as the physical/contact assembly"
                ),
            },
        },
        "sector_disposition": {
            **partial["sector_disposition"],
            "ghost_longitudinal_Schur_scale": "COMPUTED",
            "ghost_longitudinal_Schur_reference_finite_rows": "NONDEFINED",
            "full_BV_multiplicity": "PINNED_SPECIAL_BACKGROUND_LEDGER",
            "full_generic_BV_five_form_factors": "NOT_COMPUTED",
        },
        "dependencies": {
            name: _reference(path, values[name])
            for name, (path, _expected_hash) in SOURCES.items()
        },
        "claim_flags": {
            "FIVE_CARRIER_MANIFEST_PINNED": True,
            "ELEVEN_PHYSICAL_H1_CUBED_CHANNELS_PINNED": True,
            "CONTACT_AND_RELATIVE_IBP_ROWS_INCLUDED": True,
            "MAXIMAL_PARTIAL_BV_QUOTIENT_COMPUTED": True,
            "SCHUR_SCALE_RESPONSE_COMPUTED": True,
            "GENERIC_SCHUR_REFERENCE_FINITE_ROWS_COMPUTED": False,
            "FULL_GENERIC_BV_FIVE_FORM_FACTORS_COMPUTED": False,
            "SPECIAL_BACKGROUND_ROWS_INTERPOLATED_TO_GENERIC": False,
            "LOCAL_NORMALIZATIONS_FOLDED_INTO_NONLOCAL_FUNCTIONS": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "QME_OR_LORENTZIAN_PROMOTED": False,
        },
        "next_gate": (
            "supply and independently verify the generic primed Schur finite "
            "relative trace kernel, then project its cubic variation and the "
            "remaining generic BV factors onto the five-carrier quotient"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL result freezes the maximal "
            "currently determined generic parity-even third-curvature quotient: "
            "all physical, ghost-n3 and vector ghost n1/n2 rows, including "
            "relative-IBP flux and contact endpoints. It also pins the complete "
            "special-background BV multiplicities and the normalized longitudinal "
            "Schur scale response. The generic reference-scale finite Schur "
            "kernel is not available, so the complete ghost and full-BV five "
            "functions are nondefined. Special backgrounds are holdouts, not "
            "interpolation data. Local C2 and dressed R2 constants remain "
            "separate. No anomaly coefficient, Gamma1, Q1, QME, residual, "
            "Lorentzian, state, particle, scattering or unitarity claim is made."
        ),
    }
    validate(result)
    return result


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
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale five-form-factor assembly: {OUTPUT}")
    print("PARITY-EVEN THIRD-CURVATURE FIVE-FORM-FACTOR ASSEMBLY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

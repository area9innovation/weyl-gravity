#!/usr/bin/env python3
"""Generate the fail-closed claim map for the Paper 12 working draft."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly.tex"
PDF = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly.pdf"
SUPPLEMENT = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-computational-supplement.tex"
SUPPLEMENT_PDF = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-computational-supplement.pdf"
REFEREE_RESPONSE = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-referee-response.md"
GENERATED_TABLES = ROOT / "paper/generated/12-quantum-anomaly-certificate-tables.tex"
TABLE_GENERATOR = ROOT / "paper/generate_12_quantum_anomaly_tables.py"
TABLE_VERIFIER = ROOT / "paper/verify_12_quantum_anomaly_tables.py"
OUTPUT = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json"
INPUTS = {
    "strict_AFN0_even": ROOT / "quantum-weyl/local_bv/certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json",
    "strict_AFN0_odd": ROOT / "quantum-weyl/local_bv/certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json",
    "strict_gauge_fixed": ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "strict_minimal_KT": ROOT / "quantum-weyl/local_bv/certificates/MINIMAL_BV_KOSZUL_TATE_COLLAPSE.json",
    "euclidean_elliptic_complex": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json",
    "euclidean_multiplicity": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "euclidean_integration_slice": ROOT / "quantum-weyl/spectral/euclidean/certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json",
    "strict_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "matter_no_go": ROOT / "quantum-weyl/anomalies/certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json",
    "cotangent_lift": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "wz_preflight": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "extended_cohomology": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "Q1_disposition": ROOT / "quantum-weyl/transfer/certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
    "anomaly_induced_Gamma1": ROOT / "quantum-weyl/transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "flat_TT_logarithmic_Gamma1": ROOT / "quantum-weyl/transfer/certificates/FLAT_TT_LOGARITHMIC_GAMMA1.json",
    "curvature_squared_covariant_log_Gamma1": ROOT / "quantum-weyl/transfer/certificates/CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1.json",
    "FV_conformized_C2_log_Gamma1": ROOT / "quantum-weyl/transfer/certificates/FV_CONFORMIZED_C2_LOG_GAMMA1.json",
    "FV_anomaly_action_Ricci_sector": ROOT / "quantum-weyl/transfer/certificates/FV_ANOMALY_ACTION_RICCI_SECTOR.json",
    "algebraic_cubic_Weyl_carriers": ROOT / "quantum-weyl/transfer/certificates/FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS.json",
    "third_curvature_Weyl_manifest": ROOT / "quantum-weyl/transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
    "BoxR_scheme_conversion": ROOT / "quantum-weyl/spectral/euclidean/certificates/WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_inputs() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    even = values["strict_AFN0_even"]
    odd = values["strict_AFN0_odd"]
    gauge = values["strict_gauge_fixed"]
    minimal_kt = values["strict_minimal_KT"]
    elliptic = values["euclidean_elliptic_complex"]
    multiplicity = values["euclidean_multiplicity"]
    integration_slice = values["euclidean_integration_slice"]
    strict = values["strict_breaking"]
    matter = values["matter_no_go"]
    lift = values["cotangent_lift"]
    wz_preflight = values["wz_preflight"]
    extended = values["extended_cohomology"]
    q1 = values["Q1_disposition"]
    gamma1 = values["anomaly_induced_Gamma1"]
    flat_tt_log = values["flat_TT_logarithmic_Gamma1"]
    curvature_squared_log = values["curvature_squared_covariant_log_Gamma1"]
    fv_conformized_log = values["FV_conformized_C2_log_Gamma1"]
    fv_anomaly_ricci = values["FV_anomaly_action_Ricci_sector"]
    cubic_weyl = values["algebraic_cubic_Weyl_carriers"]
    third_curvature_weyl = values["third_curvature_Weyl_manifest"]
    box_r_scheme_conversion = values["BoxR_scheme_conversion"]
    if (
        even.get("result_state") != "COMPLETE_AFN0_EVEN_CANDIDATE_QUOTIENT"
        or even.get("smallest_relative_sector", {}).get("closure_rank") != 6
        or even.get("smallest_relative_sector", {}).get("boundary_rank") != 4
        or odd.get("result_state") != "COMPLETE_AFN0_ODD_CANDIDATE_QUOTIENT"
        or odd.get("smallest_relative_sector", {}).get("quotient_dimension") != 1
        or gauge.get("gauge_fixed_cohomology", {}).get("H14_even_dimension") != 2
        or gauge.get("gauge_fixed_cohomology", {}).get("H14_odd_dimension") != 1
        or minimal_kt.get("spectral_sequence", {}).get("collapse_page") != "E2"
        or len(minimal_kt.get("contraction", {}).get("contractible_pairs", [])) != 6
        or elliptic.get("result_state")
        != "COMPLETE_GAUGE_FIXED_BV_PRINCIPAL_SYMBOL_SEQUENCE_EXACT_AND_ELLIPTIC"
        or len(multiplicity.get("repository_factors", [])) != 4
        or len(integration_slice.get("factor_exponent_ledger", [])) != 4
        or strict.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or strict.get("coefficients", {}).get("ANOM_OMEGA_C2")
        != {"numerator": 199, "denominator": 30}
        or strict.get("coefficients", {}).get("ANOM_OMEGA_E4")
        != {"numerator": -87, "denominator": 20}
        or matter.get("result_state")
        != "NO_NONNEGATIVE_STANDARD_UNITARY_FREE_MATTER_CANCELLATION"
        or lift.get("contractible_quartet", {}).get("status")
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        or wz_preflight.get("local_primitives", {}).get("B_E")
        != "integral sqrt(g) [tau E4 + 4 G^{mu nu} d_mu tau d_nu tau - 4 (Box tau)(d tau)^2 + 2 (d tau)^4]"
        or extended.get("result_state")
        != "TAU_ADIC_EXTENDED_GAUGE_FIXED_H04_H14_COMPLETE_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED"
        or extended.get("H04", {}).get("even_quotient_dimension") != 3
        or extended.get("H04", {}).get("odd_quotient_dimension") != 1
        or extended.get("H14", {}).get("even_quotient_dimension") != 0
        or extended.get("H14", {}).get("odd_quotient_dimension") != 0
        or extended.get("one_loop_QME", {}).get("status")
        != "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY"
        or q1.get("finite_counterterm_ambiguity", {}).get("bulk_response_rank") != 2
        or q1.get("decision", {}).get("complete_Q1") != "NO_CERTIFIED_OPERATOR"
        or q1.get("decision", {}).get("residual_transfer") != "FORBIDDEN"
        or gamma1.get("result_state")
        != "ANOMALY_INDUCED_EUCLIDEAN_GAMMA1_REPRESENTATIVE_CERTIFIED_WEYL_INVARIANT_REMAINDER_OPEN"
        or gamma1.get("exact_coefficient_solve", {}).get("rank") != 3
        or gamma1.get("decision", {}).get("complete_finite_nonlocal_Gamma1")
        != "NO_CERTIFIED_FUNCTIONAL"
        or flat_tt_log.get("decision", {}).get("flat_TT_universal_logarithmic_form_factor")
        != "CERTIFIED"
        or flat_tt_log.get("exact_logarithmic_form_factor", {}).get("logarithmic_coefficient")
        != {"numerator": -199, "denominator": 60}
        or flat_tt_log.get("claim_flags", {}).get("FINITE_C2_NORMALIZATION_FIXED")
        is not False
        or curvature_squared_log.get("decision", {}).get(
            "covariant_C2_log_through_curvature_order_two"
        )
        != "CERTIFIED"
        or curvature_squared_log.get("operator_choice_independence", {}).get(
            "first_difference_order"
        )
        != 3
        or curvature_squared_log.get("claim_flags", {}).get(
            "COMPLETE_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED"
        )
        is not False
        or fv_conformized_log.get("decision", {}).get(
            "selected_C2_log_local_Weyl_completion"
        )
        != "CERTIFIED"
        or fv_conformized_log.get("carrier_crosswalk", {}).get("identity_status")
        != "DISTINCT_CARRIERS_NO_IDENTIFICATION"
        or fv_conformized_log.get("claim_flags", {}).get(
            "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED"
        )
        is not False
        or fv_anomaly_ricci.get("decision", {}).get("FV_anomaly_action")
        != "CERTIFIED"
        or fv_anomaly_ricci.get("decision", {}).get(
            "Ricci_scalar_sector_dependence"
        )
        != "CERTIFIED"
        or fv_anomaly_ricci.get("decision", {}).get(
            "independent_nonlocal_R2_form_factor"
        )
        != "NOT_AN_INDEPENDENT_DATUM_IN_DECLARED_FV_CONFORMAL_DECOMPOSITION"
        or cubic_weyl.get("decision", {}).get(
            "zero_derivative_algebraic_C3_carriers"
        )
        != "CERTIFIED_COMPLETE"
        or cubic_weyl.get("tensor_carriers", {}).get("parity_dimensions")
        != {"even": 1, "odd": 1}
        or cubic_weyl.get("claim_flags", {}).get(
            "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED"
        )
        is not False
        or third_curvature_weyl.get("raw_module", {}).get(
            "generic_label_orbit_dimension"
        )
        != 12
        or third_curvature_weyl.get("quotient_module", {}).get(
            "generic_label_orbit_dimension"
        )
        != 11
        or third_curvature_weyl.get("claim_flags", {}).get(
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"
        )
        is not True
        or third_curvature_weyl.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "RAW_ZETA_BOXR_COEFFICIENT_COMPUTED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED"
        )
        is not True
        or box_r_scheme_conversion.get("claim_flags", {}).get(
            "NONLOCAL_R2_FORM_FACTOR_COMPUTED"
        )
        is not False
    ):
        raise ValueError("Paper 12 theorem dependency drifted")
    return values


def build() -> dict[str, Any]:
    values = _load_inputs()
    strict = values["strict_breaking"]
    extended = values["extended_cohomology"]
    gamma1 = values["anomaly_induced_Gamma1"]
    flat_tt_log = values["flat_TT_logarithmic_Gamma1"]
    curvature_squared_log = values["curvature_squared_covariant_log_Gamma1"]
    fv_conformized_log = values["FV_conformized_C2_log_Gamma1"]
    fv_anomaly_ricci = values["FV_anomaly_action_Ricci_sector"]
    cubic_weyl = values["algebraic_cubic_Weyl_carriers"]
    third_curvature_weyl = values["third_curvature_Weyl_manifest"]
    box_r_scheme_conversion = values["BoxR_scheme_conversion"]
    return {
        "schema": "paper-12-pure-weyl-one-loop-bv-anomaly-claim-map-v1",
        "result_id": "PAPER_12_PURE_WEYL_ONE_LOOP_BV_ANOMALY_DRAFT",
        "result_state": "DRAFT_ALLOWED_STRICT_OBSTRUCTION_TAU_ADIC_EXTENDED_QME_RESTORATION_ANOMALY_INDUCED_GAMMA1_AND_FV_CONFORMIZED_C2_LOGARITHM",
        "lifecycle_state": "WRITING_STARTED",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
        ],
        "headline": "Strict pure Weyl gravity is locally QME-obstructed at one loop; the formal tau-adic compensator extension has a restored one-loop local Euclidean QME; the FV anomaly action fixes the Ricci-scalar sector, the algebraic C3 basis is complete, and the parity-even five-carrier third-curvature manifest has an exact 12-to-11 label quotient, while repository form-factor functions, coefficients, odd derivative data and finite normalizations remain open.",
        "manuscript": _relative(MANUSCRIPT),
        "manuscript_sha256": _sha256(MANUSCRIPT),
        "compiled_pdf": _relative(PDF),
        "compiled_pdf_sha256": _sha256(PDF),
        "publication_artifacts": {
            _relative(path): _sha256(path)
            for path in (
                SUPPLEMENT,
                SUPPLEMENT_PDF,
                REFEREE_RESPONSE,
                GENERATED_TABLES,
                TABLE_GENERATOR,
                TABLE_VERIFIER,
            )
        },
        "theory_dispositions": {
            "strict_fixed_field_content": "OBSTRUCTED",
            "tau_adic_compensator_extended_local_Euclidean_one_loop": "QME_RESTORED",
        },
        "certified_claims": {
            "strict_quotient_scope": "REGULAR_BACH_LOCUS",
            "minimal_Koszul_Tate_collapse_page": "E2",
            "Euclidean_symbol_bundle_dimensions": [5, 10, 5],
            "determinant_factor_count": 4,
            "determinant_to_Slavnov_bridge_displayed": True,
            "strict_full_gauge_fixed_H14_even_dimension": 2,
            "strict_full_gauge_fixed_H14_odd_dimension": 1,
            "pure_Diff_and_mixed_additional_classes": 0,
            "C2_coefficient": strict["coefficients"]["ANOM_OMEGA_C2"],
            "E4_coefficient": strict["coefficients"]["ANOM_OMEGA_E4"],
            "CdualC_coefficient": strict["coefficients"]["ANOM_OMEGA_C_DUAL_C"],
            "BoxR_coefficient": strict["coefficients"]["ANOM_OMEGA_BOX_R"],
            "strict_one_loop_local_Euclidean_QME_obstructed": True,
            "standard_unitary_free_matter_cancellation_excluded": True,
            "minimal_BV_compensator_cotangent_lift_exact": True,
            "Weyl_quartet_contractible": True,
            "Euler_Wess_Zumino_primitive_displayed": True,
            "formal_tau_adic_coordinate_change_invertible": True,
            "extended_H04_even_dimension": extended["H04"]["even_quotient_dimension"],
            "extended_H04_odd_dimension": extended["H04"]["odd_quotient_dimension"],
            "extended_H14_even_dimension": extended["H14"]["even_quotient_dimension"],
            "extended_H14_odd_dimension": extended["H14"]["odd_quotient_dimension"],
            "extended_one_loop_local_Euclidean_QME_restored": True,
            "WZ_local_counterterm_Q1_contribution_fixed": True,
            "finite_counterterm_bulk_Q1_ambiguity_rank": 2,
            "anomaly_induced_nonlocal_Gamma1_representative": True,
            "anomaly_induced_functional_coefficients": gamma1["exact_coefficient_solve"]["solution_vector"],
            "flat_TT_logarithmic_form_factor": True,
            "flat_TT_logarithmic_coefficient": flat_tt_log["exact_logarithmic_form_factor"]["logarithmic_coefficient"],
            "flat_TT_scale_response": flat_tt_log["exact_logarithmic_form_factor"]["RG_scale_response"],
            "covariant_C2_log_through_curvature_order_two": True,
            "first_unresolved_C2_log_completion_order": curvature_squared_log["operator_choice_independence"]["first_difference_order"],
            "FV_conformized_C2_log_local_Weyl_completion": True,
            "FV_scalar_flat_representative": fv_conformized_log["fv_scalar_flat_representative"]["status"],
            "FV_first_forced_completion_order": fv_conformized_log["cubic_carrier"]["first_completion_order"],
            "FV_and_WZ_dressed_metrics_distinct": True,
            "FV_anomaly_action_fixed": True,
            "Ricci_scalar_sector_structurally_dependent": True,
            "nonlocal_R2_form_factor_disposition": fv_anomaly_ricci["decision"]["independent_nonlocal_R2_form_factor"],
            "algebraic_C3_carrier_dimensions": cubic_weyl["tensor_carriers"]["parity_dimensions"],
            "algebraic_C3_chiral_parity_crosswalk_exact": True,
            "parity_even_third_curvature_carrier_count": third_curvature_weyl["raw_module"]["carrier_labeled_function_count"],
            "third_curvature_raw_label_dimension": third_curvature_weyl["raw_module"]["generic_label_orbit_dimension"],
            "third_curvature_4d_quotient_label_dimension": third_curvature_weyl["quotient_module"]["generic_label_orbit_dimension"],
            "third_curvature_functional_relation_rank": third_curvature_weyl["four_dimensional_identity"]["relation_rank"],
            "raw_zeta_BoxR_coefficient": box_r_scheme_conversion["heat_kernel_row_reconstruction"]["raw_BoxR_coefficient"],
            "raw_to_repository_R2_scheme_shift": box_r_scheme_conversion["repository_scheme_conversion"]["raw_to_BoxR_zero_counterterm"],
            "repository_29_over_120_local_R2_reproduced": True,
            "Berger_WZ_tau_contraction_merge_rejected": True,
        },
        "explicit_nonclaims": {
            "finite_polynomial_in_tau_theorem": False,
            "all_loop_extended_QME": False,
            "Lorentzian_QME": False,
            "renormalized_Lorentzian_products": False,
            "global_BRST_Hadamard_state": False,
            "positive_particle_Hilbert_space": False,
            "unitarity_theorem": False,
            "residual_quantum_transfer": False,
            "complete_renormalized_Q1_supplied": False,
            "complete_renormalized_Gamma1_supplied": False,
            "independent_cubic_Weyl_invariant_form_factors": False,
            "parity_odd_third_curvature_carrier_manifest": False,
            "absolute_dressed_Rhat2_normalization": False,
            "same_background_compensator_contraction": False,
            "quantum_Cartan_identity": False,
            "full_BV_Bridge_4_particle_crosswalk": False,
            "Berger_Bridge_4_particle_crosswalk": False,
            "Bridge_5_interacting_BRST_map": False,
            "theorem_frozen": False,
        },
        "next_gate": {
            "status": "REPOSITORY_PARITY_EVEN_THIRD_CURVATURE_FORM_FACTOR_FUNCTIONS_AND_COEFFICIENTS_PARITY_ODD_MANIFEST_FINITE_C2_ABSOLUTE_RHAT2_NORMALIZATION_RENORMALIZED_PRODUCTS_AND_SAME_BACKGROUND_EXTENDED_CLASSICAL_CONTRACTION",
            "required_inputs": [
                "same-background compensator-inclusive classical contraction",
                "finite C2 and absolute dressed Rhat2 normalization conditions",
                "five repository parity-even third-curvature form-factor functions and coefficients, the parity-odd derivative carrier manifest, and global Paneitz/FV Green data",
                "renormalized BV operator data fixing complete Q1",
            ],
            "required_outputs": [
                "q1=pi_ext Q1 iota_ext",
                "first-order residual nilpotency",
                "quantum D-Cartan defect",
                "H3-to-H4 and H4-to-H5 maps",
                "pairing correction",
            ],
        },
        "inputs": {
            _relative(path): {
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in INPUTS.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("Paper 12 claim map is stale; rerun with --emit")
    if not args.emit and not args.check:
        print(rendered, end="")


if __name__ == "__main__":
    main()

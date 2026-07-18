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
    "strict_diff_mixed_minimal_H14": ROOT / "quantum-weyl/local_bv/certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json",
    "strict_gauge_fixed": ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "strict_minimal_KT": ROOT / "quantum-weyl/local_bv/certificates/MINIMAL_BV_KOSZUL_TATE_COLLAPSE.json",
    "euclidean_elliptic_complex": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json",
    "euclidean_multiplicity": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "euclidean_integration_slice": ROOT / "quantum-weyl/spectral/euclidean/certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json",
    "euclidean_factor_coefficients": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json",
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
    "CPT_universal_third_curvature_kernels": ROOT / "quantum-weyl/transfer/certificates/CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS.json",
    "generic_background_ghost_CPT_obstruction": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json",
    "generic_ghost_Endo_Duhamel_reduction": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json",
    "generic_ghost_n3_adiabatic_carrier": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER.json",
    "generic_ghost_n3_triangle_kernel": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json",
    "scalar_flat_K_Ricci_crosswalk": ROOT / "quantum-weyl/transfer/certificates/SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK.json",
    "generic_ghost_n3_five_carrier_projection": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json",
    "generic_ghost_n1_n2_Hodge_resolvent_reduction": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json",
    "generic_ghost_n1_n2_vector_CPT_projection": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION.json",
    "generic_ghost_longitudinal_Schur_resummation": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
    "generic_ghost_Schur_Schatten_split": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json",
    "generic_ghost_Schur_Wodzicki_residue": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json",
    "generic_ghost_Schur_weighted_trace_scale": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
    "round_S4_ghost_Schur_finite_weighted_traces": ROOT / "quantum-weyl/spectral/euclidean/certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
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
    diff_mixed = values["strict_diff_mixed_minimal_H14"]
    gauge = values["strict_gauge_fixed"]
    minimal_kt = values["strict_minimal_KT"]
    elliptic = values["euclidean_elliptic_complex"]
    multiplicity = values["euclidean_multiplicity"]
    integration_slice = values["euclidean_integration_slice"]
    factor_coefficients = values["euclidean_factor_coefficients"]
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
    cpt_kernels = values["CPT_universal_third_curvature_kernels"]
    generic_ghost_cpt = values["generic_background_ghost_CPT_obstruction"]
    generic_ghost_endo = values["generic_ghost_Endo_Duhamel_reduction"]
    generic_ghost_n3 = values["generic_ghost_n3_adiabatic_carrier"]
    generic_ghost_n3_triangle = values["generic_ghost_n3_triangle_kernel"]
    scalar_flat_k_ricci = values["scalar_flat_K_Ricci_crosswalk"]
    generic_ghost_n3_projection = values["generic_ghost_n3_five_carrier_projection"]
    generic_ghost_n1_n2 = values["generic_ghost_n1_n2_Hodge_resolvent_reduction"]
    generic_ghost_n1_n2_vector = values["generic_ghost_n1_n2_vector_CPT_projection"]
    generic_ghost_longitudinal_schur = values["generic_ghost_longitudinal_Schur_resummation"]
    generic_ghost_schur_schatten = values["generic_ghost_Schur_Schatten_split"]
    generic_ghost_schur_wodzicki = values["generic_ghost_Schur_Wodzicki_residue"]
    generic_ghost_schur_scale = values["generic_ghost_Schur_weighted_trace_scale"]
    round_s4_ghost_schur_finite = values["round_S4_ghost_Schur_finite_weighted_traces"]
    box_r_scheme_conversion = values["BoxR_scheme_conversion"]
    if (
        even.get("result_state") != "COMPLETE_AFN0_EVEN_CANDIDATE_QUOTIENT"
        or even.get("smallest_relative_sector", {}).get("closure_rank") != 6
        or even.get("smallest_relative_sector", {}).get("boundary_rank") != 4
        or odd.get("result_state") != "COMPLETE_AFN0_ODD_CANDIDATE_QUOTIENT"
        or odd.get("smallest_relative_sector", {}).get("quotient_dimension") != 1
        or diff_mixed.get("result_state")
        != "MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS_NONMINIMAL_OPEN"
        or diff_mixed.get("claim_flags", {}).get("AFN0_DIFF_MIXED_TOTAL_COMPLEX_COMPLETE")
        is not True
        or diff_mixed.get("claim_flags", {}).get("PURE_DIFF_H14_ZERO") is not True
        or diff_mixed.get("claim_flags", {}).get("INDEPENDENT_MIXED_DIFF_WEYL_H14_ZERO")
        is not True
        or gauge.get("gauge_fixed_cohomology", {}).get("H14_even_dimension") != 2
        or gauge.get("gauge_fixed_cohomology", {}).get("H14_odd_dimension") != 1
        or minimal_kt.get("spectral_sequence", {}).get("collapse_page") != "E2"
        or len(minimal_kt.get("contraction", {}).get("contractible_pairs", [])) != 6
        or elliptic.get("result_state")
        != "COMPLETE_GAUGE_FIXED_BV_PRINCIPAL_SYMBOL_SEQUENCE_EXACT_AND_ELLIPTIC"
        or len(multiplicity.get("repository_factors", [])) != 4
        or len(integration_slice.get("factor_exponent_ledger", [])) != 4
        or factor_coefficients.get("coefficient_result", {}).get("coefficients", {}).get("C2")
        != {"numerator": 199, "denominator": 30}
        or factor_coefficients.get("coefficient_result", {}).get("coefficients", {}).get("E4")
        != {"numerator": -87, "denominator": 20}
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
        != 11
        or third_curvature_weyl.get("quotient_module", {}).get(
            "generic_label_orbit_dimension"
        )
        != 10
        or third_curvature_weyl.get("claim_flags", {}).get(
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"
        )
        is not True
        or third_curvature_weyl.get("claim_flags", {}).get(
            "SCALAR_FLAT_I29_REVERSAL_IDENTITY_REPLAYED"
        )
        is not True
        or third_curvature_weyl.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or [
            row.get("carrier_id")
            for row in cpt_kernels.get("universal_kernels", [])
        ]
        != ["I10", "I24", "I25", "I28", "I29"]
        or cpt_kernels.get("universal_kernels", [])[-1].get("stabilizer") != "S3"
        or cpt_kernels.get("source_fixture", {}).get("status")
        != "COEFFICIENT_COMPUTED"
        or cpt_kernels.get("claim_flags", {}).get(
            "FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED"
        )
        is not True
        or cpt_kernels.get("claim_flags", {}).get(
            "REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED"
        )
        is not False
        or cpt_kernels.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or generic_ghost_cpt.get("CPT_applicability_decision", {}).get("verdict")
        != "DIRECT_MINIMAL_CPT_SUBSTITUTION_FOR_THE_GENERIC_GHOST_SECTOR_IS_OBSTRUCTED"
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_GHOST_PRINCIPAL_SYMBOL_NONMINIMAL"
        )
        is not True
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_GHOST_HODGE_SPLIT_OBSTRUCTED"
        )
        is not True
        or generic_ghost_cpt.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED"
        )
        is not False
        or generic_ghost_endo.get("exact_Endo_split", {}).get("local_perturbation")
        != "W=-2 Ric"
        or generic_ghost_endo.get("Duhamel_expansion", {}).get(
            "maximum_W_insertions_through_cubic_order"
        )
        != 3
        or generic_ghost_endo.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED"
        )
        is not True
        or generic_ghost_endo.get("claim_flags", {}).get(
            "GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED"
        )
        is not False
        or generic_ghost_n3.get("angular_average", {}).get("coefficients", {}).get(
            "tr_R3"
        )
        != {"numerator": 503, "denominator": 648}
        or generic_ghost_n3.get("three_insertion_log_term", {}).get(
            "coefficients", {}
        ).get("tr_R3")
        != {"numerator": -503, "denominator": 243}
        or generic_ghost_n3.get("carrier_crosswalk", {}).get(
            "repository_I10_normalization_map"
        )
        != "NO_CERTIFIED_MAP"
        or generic_ghost_n3_triangle.get("projector_sector_expansion", {}).get(
            "sector_count"
        )
        != 8
        or generic_ghost_n3_triangle.get("projector_sector_expansion", {}).get(
            "total_Wick_rows"
        )
        != 20
        or generic_ghost_n3_triangle.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED"
        )
        is not True
        or generic_ghost_n3_triangle.get("carrier_projection", {}).get(
            "repository_five_carrier_projection"
        )
        != "NOT_COMPUTED"
        or scalar_flat_k_ricci.get("linear_crosswalk", {}).get("identity")
        != "K_munu=Ric_munu+O(curvature^2)"
        or scalar_flat_k_ricci.get("cubic_order_counting", {}).get(
            "first_replacement_error_order"
        )
        != 4
        or scalar_flat_k_ricci.get("five_carrier_target", {}).get(
            "projection_status"
        )
        != "NOT_COMPUTED"
        or generic_ghost_n3_projection.get("quotient_section", {}).get(
            "raw_effective_channel_count"
        )
        != 11
        or generic_ghost_n3_projection.get("quotient_section", {}).get(
            "quotient_dimension"
        )
        != 10
        or generic_ghost_n3_projection.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not True
        or generic_ghost_n3_projection.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or generic_ghost_n1_n2.get("proper_time_to_resolvent", {}).get(
            "resolvent_identity"
        )
        != "G_H0=G_F-(1/3)d Delta_0^-2 delta"
        or generic_ghost_n1_n2.get("log_determinant_expansion", {}).get(
            "carrier_count"
        )
        != 5
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED"
        )
        is not True
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED"
        )
        is not True
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED"
        )
        is not False
        or generic_ghost_n1_n2.get("claim_flags", {}).get(
            "GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED"
        )
        is not False
        or generic_ghost_n1_n2_vector.get("minimal_operator_sign_flip", {}).get(
            "surviving_rows"
        )
        != [1, 3, 14]
        or generic_ghost_n1_n2_vector.get("claim_flags", {}).get(
            "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED"
        )
        is not True
        or generic_ghost_n1_n2_vector.get("claim_flags", {}).get(
            "ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED"
        )
        is not False
        or generic_ghost_longitudinal_schur.get(
            "exact_determinant_factorization", {}
        ).get("normalized_scalar_Schur_operator")
        != "S_L(W)=(2/3)I+(1/3)delta(F+W)^-1 d"
        or generic_ghost_longitudinal_schur.get("claim_flags", {}).get(
            "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION"
        )
        is not True
        or generic_ghost_longitudinal_schur.get("claim_flags", {}).get(
            "GENERIC_LONGITUDINAL_SCHUR_FORM_FACTORS_COMPUTED"
        )
        is not False
        or generic_ghost_longitudinal_schur.get(
            "regularization_boundary", {}
        ).get("zeta_multiplicative_anomaly")
        != "LOCAL_TERM_NOT_EVALUATED"
        or generic_ghost_schur_schatten.get(
            "sharp_ideal_classification", {}
        ).get("minimal_modified_determinant_order")
        != 3
        or generic_ghost_schur_schatten.get(
            "critical_local_residue", {}
        ).get("Ricci_basis")
        != "Wres(K^2)=(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/27"
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "SCHUR_CORRECTION_S3_CLASS_PROVED"
        )
        is not True
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "CANONICAL_DET3_TAIL_DEFINED"
        )
        is not True
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED"
        )
        is not True
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED"
        )
        is not False
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "WODZICKI_RESIDUE_K_COMPUTED"
        )
        is not False
        or generic_ghost_schur_wodzicki.get("exact_residues", {}).get(
            "K_Ricci_basis"
        )
        != "Wres(K)=(4 pi)^-2 integral[R^2+4 Ric_mn Ric^mn]/9"
        or generic_ghost_schur_wodzicki.get("exact_residues", {}).get(
            "log_S_Ricci_basis"
        )
        != "Wres(log S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54"
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "WODZICKI_RESIDUE_K_COMPUTED"
        )
        is not True
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "WODZICKI_RESIDUE_LOG_S_COMPUTED"
        )
        is not True
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "RENORMALIZED_R_K_COMPUTED"
        )
        is not False
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "FINITE_PART_R_K2_COMPUTED"
        )
        is not False
        or generic_ghost_schur_wodzicki.get("claim_flags", {}).get(
            "ZETA_SCALE_COEFFICIENT_COMPUTED"
        )
        is not False
        or generic_ghost_schur_scale.get("claim_flags", {}).get(
            "SCHUR_SCALE_COEFFICIENT_COMPUTED"
        )
        is not True
        or generic_ghost_schur_scale.get("Schur_determinant_scale_row", {}).get(
            "Ricci_basis"
        )
        != "d/dlog(mu) log Det_(3,R_mu)(S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54"
        or generic_ghost_schur_scale.get("claim_flags", {}).get(
            "REFERENCE_FINITE_R_K_COMPUTED"
        )
        is not False
        or generic_ghost_schur_scale.get("claim_flags", {}).get(
            "REFERENCE_FINITE_R_K2_COMPUTED"
        )
        is not False
        or generic_ghost_schur_schatten.get("claim_flags", {}).get(
            "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"
        )
        is not False
        or round_s4_ghost_schur_finite.get("claim_flags", {}).get(
            "ROUND_S4_R_DELTA_K_COMPUTED"
        )
        is not True
        or round_s4_ghost_schur_finite.get("claim_flags", {}).get(
            "ROUND_S4_FINITE_R_DELTA_K2_COMPUTED"
        )
        is not True
        or round_s4_ghost_schur_finite.get("claim_flags", {}).get(
            "GENERIC_BACKGROUND_R_K_COMPUTED"
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
    diff_mixed = values["strict_diff_mixed_minimal_H14"]
    extended = values["extended_cohomology"]
    gamma1 = values["anomaly_induced_Gamma1"]
    flat_tt_log = values["flat_TT_logarithmic_Gamma1"]
    curvature_squared_log = values["curvature_squared_covariant_log_Gamma1"]
    fv_conformized_log = values["FV_conformized_C2_log_Gamma1"]
    fv_anomaly_ricci = values["FV_anomaly_action_Ricci_sector"]
    cubic_weyl = values["algebraic_cubic_Weyl_carriers"]
    third_curvature_weyl = values["third_curvature_Weyl_manifest"]
    cpt_kernels = values["CPT_universal_third_curvature_kernels"]
    generic_ghost_cpt = values["generic_background_ghost_CPT_obstruction"]
    generic_ghost_endo = values["generic_ghost_Endo_Duhamel_reduction"]
    generic_ghost_n3 = values["generic_ghost_n3_adiabatic_carrier"]
    generic_ghost_n3_triangle = values["generic_ghost_n3_triangle_kernel"]
    scalar_flat_k_ricci = values["scalar_flat_K_Ricci_crosswalk"]
    generic_ghost_n3_projection = values["generic_ghost_n3_five_carrier_projection"]
    generic_ghost_n1_n2 = values["generic_ghost_n1_n2_Hodge_resolvent_reduction"]
    generic_ghost_n1_n2_vector = values["generic_ghost_n1_n2_vector_CPT_projection"]
    generic_ghost_longitudinal_schur = values["generic_ghost_longitudinal_Schur_resummation"]
    generic_ghost_schur_schatten = values["generic_ghost_Schur_Schatten_split"]
    generic_ghost_schur_wodzicki = values["generic_ghost_Schur_Wodzicki_residue"]
    generic_ghost_schur_scale = values["generic_ghost_Schur_weighted_trace_scale"]
    round_s4_ghost_schur_finite = values["round_S4_ghost_Schur_finite_weighted_traces"]
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
        "headline": "Strict pure Weyl gravity is locally QME-obstructed at one loop; the formal tau-adic compensator extension has a restored one-loop local Euclidean QME; the FV anomaly action fixes the Ricci-scalar sector, the algebraic C3 basis is complete, and the parity-even five-carrier third-curvature manifest has an exact scalar-flat I29 symmetry enhancement and 11-to-10 effective label quotient. Five universal CPT source kernels are exact, the generic ghost n=3 triangle is projected exactly onto that quotient, the curved n=1/n=2 pure-vector CPT sum is exact, and all longitudinal D_W towers are resummed into one normalized scalar Schur kernel. The Schur correction lies in S_3, its canonical det_3 tail is defined, Wres(K), Wres(K^2), and Wres(log S_L) are exact, the declared order-two weighted trace fixes the pole and scale row, and the round-S4 reference finite K/K2 rows are exact. A smoothing witness proves that the generic finite rows require a full Green kernel or spectral measure; any local zeta multiplicative anomaly, simplex integration, the generic physical fourth-order kernel, complete repository functions and coefficients, odd derivative data and finite normalizations remain open.",
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
            "pure_Diff_and_mixed_additional_classes": sum(
                diff_mixed["AFN0_H14"][sector][parity + "_dimension"]
                for sector in ("pure_Diff", "mixed_independent")
                for parity in ("even", "odd")
            ),
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
            "universal_CPT_third_curvature_kernels_imported": True,
            "universal_CPT_source_fixture_status": cpt_kernels["source_fixture"]["status"],
            "universal_CPT_kernel_box_homogeneities": [
                row["gamma_box_homogeneity"]
                for row in cpt_kernels["universal_kernels"]
            ],
            "generic_background_ghost_minimal_CPT_substitution_obstructed": True,
            "generic_background_ghost_effective_divergence_coefficient": generic_ghost_cpt["algebraic_Weyl_ghost_elimination"]["beta_controls"][0]["effective_divergence_coefficient"],
            "generic_background_ghost_principal_eigenvalues": generic_ghost_cpt["nonminimal_principal_symbol"]["eigenvalues_e0"],
            "Einstein_scalar_ghost_factor_reproduced": True,
            "generic_ghost_Endo_Duhamel_reduction_supplied": True,
            "generic_ghost_Endo_alpha": generic_ghost_endo["exact_Endo_split"]["alpha"],
            "generic_ghost_local_perturbation": generic_ghost_endo["exact_Endo_split"]["local_perturbation"],
            "generic_ghost_maximum_cubic_Ricci_insertions": generic_ghost_endo["Duhamel_expansion"]["maximum_W_insertions_through_cubic_order"],
            "generic_ghost_n3_adiabatic_angular_carrier": True,
            "generic_ghost_n3_angular_tr_R3_coefficient": generic_ghost_n3["angular_average"]["coefficients"]["tr_R3"],
            "generic_ghost_n3_Tr_log_tr_R3_coefficient": generic_ghost_n3["three_insertion_log_term"]["coefficients"]["tr_R3"],
            "generic_ghost_n3_zero_momentum_stabilizer": generic_ghost_n3["polarized_S3_carrier"]["stabilizer"],
            "generic_ghost_n3_nonzero_momentum_parametric_kernel": True,
            "generic_ghost_n3_projector_sector_count": generic_ghost_n3_triangle["projector_sector_expansion"]["sector_count"],
            "generic_ghost_n3_total_Wick_rows": generic_ghost_n3_triangle["projector_sector_expansion"]["total_Wick_rows"],
            "scalar_flat_K_Ricci_linear_crosswalk": scalar_flat_k_ricci["linear_crosswalk"]["identity"],
            "cubic_K_to_Ricci_first_error_order": scalar_flat_k_ricci["cubic_order_counting"]["first_replacement_error_order"],
            "generic_ghost_triangle_five_carrier_target": scalar_flat_k_ricci["five_carrier_target"]["carrier_ids"],
            "generic_ghost_n3_five_carrier_parametric_projection": True,
            "generic_ghost_n3_projection_raw_channel_count": generic_ghost_n3_projection["quotient_section"]["raw_effective_channel_count"],
            "generic_ghost_n3_projection_quotient_dimension": generic_ghost_n3_projection["quotient_section"]["quotient_dimension"],
            "generic_ghost_n3_projection_formula_digest": generic_ghost_n3_projection["formula_digest"],
            "generic_ghost_n1_n2_Hodge_resolvent_reduction": True,
            "generic_ghost_n1_n2_minimal_carrier_count": generic_ghost_n1_n2["log_determinant_expansion"]["carrier_count"],
            "generic_ghost_n1_coefficients": [
                row["coefficient"]
                for row in generic_ghost_n1_n2["log_determinant_expansion"]["n1_carriers"]
            ],
            "generic_ghost_n2_coefficients": [
                row["coefficient"]
                for row in generic_ghost_n1_n2["log_determinant_expansion"]["n2_carriers"]
            ],
            "generic_ghost_vector_n1_plus_n2_CPT_projection": True,
            "generic_ghost_vector_n1_plus_n2_CPT_formula": generic_ghost_n1_n2_vector["minimal_operator_sign_flip"]["n1_plus_n2_formula"],
            "generic_ghost_longitudinal_DW_missing_carriers": generic_ghost_n1_n2_vector["minimal_missing_carrier_theorem"]["missing_carriers"],
            "generic_ghost_vector_n1_plus_n2_formula_digest": generic_ghost_n1_n2_vector["formula_digest"],
            "generic_ghost_longitudinal_Schur_factorization": True,
            "generic_ghost_normalized_Schur_operator": generic_ghost_longitudinal_schur["exact_determinant_factorization"]["normalized_scalar_Schur_operator"],
            "generic_ghost_longitudinal_cubic_coefficients": generic_ghost_longitudinal_schur["resolvent_series"]["Hodge_carrier_match"]["completed_n3_longitudinal_coefficients"],
            "generic_ghost_zeta_multiplicative_anomaly_status": generic_ghost_longitudinal_schur["regularization_boundary"]["zeta_multiplicative_anomaly"],
            "generic_ghost_4d_trace_class_status": generic_ghost_longitudinal_schur["regularization_boundary"]["generic_4d_trace_class_status"],
            "generic_ghost_Schur_S3_class": True,
            "generic_ghost_modified_Fredholm_order": generic_ghost_schur_schatten["sharp_ideal_classification"]["minimal_modified_determinant_order"],
            "generic_ghost_det3_tail_defined": True,
            "generic_ghost_K2_Wodzicki_residue": generic_ghost_schur_schatten["critical_local_residue"]["Ricci_basis"],
            "generic_ghost_K2_scalar_flat_Wodzicki_residue": generic_ghost_schur_schatten["critical_local_residue"]["scalar_flat_basis"],
            "generic_ghost_K_Wodzicki_residue": generic_ghost_schur_wodzicki["exact_residues"]["K_Ricci_basis"],
            "generic_ghost_log_S_Wodzicki_residue": generic_ghost_schur_wodzicki["exact_residues"]["log_S_Ricci_basis"],
            "generic_ghost_Einstein_K_Wodzicki_residue": generic_ghost_schur_wodzicki["exact_residues"]["Einstein_basis"],
            "generic_ghost_order_two_weighted_trace_scale_coefficient": generic_ghost_schur_scale["Schur_determinant_scale_row"]["Ricci_basis"],
            "generic_ghost_order_two_weighted_trace_pole_coefficients": generic_ghost_schur_scale["exact_conversion"]["pole_coefficients_Ricci_basis"],
            "round_S4_ghost_Schur_R_Delta_K": round_s4_ghost_schur_finite["exact_finite_rows"]["Delta_weighted_finite_rows"]["R_Delta_K"],
            "round_S4_ghost_Schur_FP_R_Delta_K2": round_s4_ghost_schur_finite["exact_finite_rows"]["Delta_weighted_finite_rows"]["FP_R_Delta_K2"],
            "round_S4_ghost_Schur_low_order_split": round_s4_ghost_schur_finite["exact_finite_rows"]["Delta_weighted_finite_rows"]["low_order_renormalized_split"],
            "generic_Schur_finite_rows_minimal_missing_input": round_s4_ghost_schur_finite["generic_missing_input_theorem"]["required_generic_input"],
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
            "repository_generic_background_CPT_trace_substitution": False,
            "generic_nonminimal_ghost_CPT_determinant": False,
            "generic_nonminimal_ghost_insertion_traces_evaluated": False,
            "generic_ghost_all_five_n1_n2_carriers_evaluated": False,
            "generic_ghost_longitudinal_DW_carriers_evaluated": False,
            "generic_ghost_longitudinal_Schur_form_factors_evaluated": False,
            "zeta_factorization_without_local_multiplicative_anomaly": False,
            "ordinary_Fredholm_determinant_class": False,
            "generic_ghost_full_Schur_regularized_determinant": False,
            "generic_ghost_renormalized_R_K": False,
            "generic_ghost_finite_part_R_K2": False,
            "generic_ghost_zeta_multiplicative_anomaly_computed": False,
            "generic_ghost_n3_integrated_five_carrier_form_factors": False,
            "absolute_dressed_Rhat2_normalization": False,
            "same_background_compensator_contraction": False,
            "quantum_Cartan_identity": False,
            "full_BV_Bridge_4_particle_crosswalk": False,
            "Berger_Bridge_4_particle_crosswalk": False,
            "Bridge_5_interacting_BRST_map": False,
            "theorem_frozen": False,
        },
        "next_gate": {
            "status": "SUPPLY_GENERIC_PRIMED_GREEN_OR_SPECTRAL_MEASURE_AND_PHYSICAL_FOURTH_ORDER_HESSIAN_THEN_COMPUTE_FINITE_SCHUR_ROWS_AND_MULTIPLICATIVE_TERM",
            "required_inputs": [
                "same-background compensator-inclusive classical contraction",
                "finite C2 and absolute dressed Rhat2 normalization conditions",
                "full generic-background primed Green/resolvent kernel or complete spectral measure for the reference-scale finite R(K), finite R(K^2), det3 tail and any local zeta multiplicative term; the round-S4 special-background benchmark is complete but does not substitute for this carrier",
                "simplex integration of the exact generic Diff-Weyl ghost n=3 five-carrier parametric projection",
                "same-gauge generic-background physical fourth-order Hessian and remaining trace substitutions matching the five universal CPT kernels to repository parity-even third-curvature functions and coefficients, the parity-odd derivative carrier manifest, and global Paneitz/FV Green data",
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

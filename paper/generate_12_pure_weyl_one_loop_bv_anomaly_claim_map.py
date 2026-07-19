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
    "generic_physical_hessian_linear_curvature": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "generic_physical_hessian_curvature_squared": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED.json",
    "generic_physical_hessian_n3_triangle_fixture": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE.json",
    "generic_physical_hessian_n3_five_carrier_projection": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json",
    "generic_physical_hessian_n3_integration_obstruction": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json",
    "generic_physical_hessian_mixed_H1_H2_corner_fixture": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json",
    "generic_physical_hessian_mellin_subtraction_scale_row": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW.json",
    "generic_physical_hessian_covariant_Volterra_carrier": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json",
    "generic_physical_hessian_H1_H2_contact_residue_projection": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION.json",
    "generic_physical_hessian_symmetric_mixed_boundary_incidence": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_SYMMETRIC_MIXED_BOUNDARY_INCIDENCE.json",
    "generic_physical_hessian_triangle_corner_residues": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_CORNER_RESIDUES.json",
    "generic_physical_hessian_full_boundary_incidence": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE.json",
    "generic_physical_hessian_H1_H2_contact_finite_rows": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_ROWS.json",
    "generic_physical_hessian_triangle_master_completeness": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_MASTER_COMPLETENESS.json",
    "generic_physical_hessian_triangle_renormalized_master_values": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RENORMALIZED_MASTER_VALUES.json",
    "generic_physical_hessian_triangle_six_master_coordinates": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_SIX_MASTER_COORDINATES.json",
    "generic_physical_hessian_triangle_relative_IBP_boundary_flux": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json",
    "generic_physical_hessian_third_curvature_form_factors": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS.json",
    "generic_physical_plus_ghost_n3_third_curvature_form_factors": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_PLUS_GHOST_N3_THIRD_CURVATURE_FORM_FACTORS.json",
    "generic_background_ghost_CPT_obstruction": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json",
    "generic_ghost_Endo_Duhamel_reduction": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json",
    "generic_ghost_n3_adiabatic_carrier": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER.json",
    "generic_ghost_n3_triangle_kernel": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json",
    "scalar_flat_K_Ricci_crosswalk": ROOT / "quantum-weyl/transfer/certificates/SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK.json",
    "generic_ghost_n3_five_carrier_projection": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json",
    "generic_ghost_n3_barycentric_factorization": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json",
    "generic_ghost_n3_pole3_relative_IBP": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP.json",
    "scalar_triangle_differential_system": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json",
    "generic_ghost_n3_pole3_integrated_functions": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS.json",
    "generic_ghost_n3_I29_integrated_function": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json",
    "generic_ghost_n3_symmetric_point_simplex_integration": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json",
    "generic_ghost_n1_n2_Hodge_resolvent_reduction": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json",
    "generic_ghost_n1_n2_vector_CPT_projection": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION.json",
    "generic_ghost_longitudinal_Schur_resummation": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
    "generic_ghost_Schur_Schatten_split": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json",
    "generic_ghost_Schur_Wodzicki_residue": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json",
    "generic_ghost_Schur_weighted_trace_scale": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
    "round_S4_ghost_Schur_finite_weighted_traces": ROOT / "quantum-weyl/spectral/euclidean/certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
    "round_S4_ghost_Schur_zeta_factorization": ROOT / "quantum-weyl/spectral/euclidean/certificates/ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION.json",
    "generic_ghost_Schur_weight_raised_zeta_factorization": ROOT / "quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION.json",
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
    physical_hessian_linear = values["generic_physical_hessian_linear_curvature"]
    physical_hessian_h2 = values["generic_physical_hessian_curvature_squared"]
    physical_hessian_n3_fixture = values["generic_physical_hessian_n3_triangle_fixture"]
    physical_hessian_n3_projection = values[
        "generic_physical_hessian_n3_five_carrier_projection"
    ]
    physical_hessian_n3_obstruction = values[
        "generic_physical_hessian_n3_integration_obstruction"
    ]
    physical_hessian_mixed = values[
        "generic_physical_hessian_mixed_H1_H2_corner_fixture"
    ]
    physical_hessian_mellin = values[
        "generic_physical_hessian_mellin_subtraction_scale_row"
    ]
    physical_hessian_volterra = values[
        "generic_physical_hessian_covariant_Volterra_carrier"
    ]
    physical_hessian_contacts = values[
        "generic_physical_hessian_H1_H2_contact_residue_projection"
    ]
    physical_hessian_incidence = values[
        "generic_physical_hessian_symmetric_mixed_boundary_incidence"
    ]
    physical_hessian_triangle_residues = values[
        "generic_physical_hessian_triangle_corner_residues"
    ]
    physical_hessian_full_incidence = values[
        "generic_physical_hessian_full_boundary_incidence"
    ]
    physical_hessian_contact_finite = values[
        "generic_physical_hessian_H1_H2_contact_finite_rows"
    ]
    physical_hessian_triangle_masters = values[
        "generic_physical_hessian_triangle_master_completeness"
    ]
    physical_hessian_triangle_master_values = values[
        "generic_physical_hessian_triangle_renormalized_master_values"
    ]
    physical_hessian_triangle_master_coordinates = values[
        "generic_physical_hessian_triangle_six_master_coordinates"
    ]
    physical_hessian_triangle_boundary_flux = values[
        "generic_physical_hessian_triangle_relative_IBP_boundary_flux"
    ]
    physical_hessian_form_factors = values[
        "generic_physical_hessian_third_curvature_form_factors"
    ]
    physical_plus_ghost_n3 = values[
        "generic_physical_plus_ghost_n3_third_curvature_form_factors"
    ]
    generic_ghost_cpt = values["generic_background_ghost_CPT_obstruction"]
    generic_ghost_endo = values["generic_ghost_Endo_Duhamel_reduction"]
    generic_ghost_n3 = values["generic_ghost_n3_adiabatic_carrier"]
    generic_ghost_n3_triangle = values["generic_ghost_n3_triangle_kernel"]
    scalar_flat_k_ricci = values["scalar_flat_K_Ricci_crosswalk"]
    generic_ghost_n3_projection = values["generic_ghost_n3_five_carrier_projection"]
    generic_ghost_n3_barycentric = values["generic_ghost_n3_barycentric_factorization"]
    generic_ghost_n3_relative_ibp = values["generic_ghost_n3_pole3_relative_IBP"]
    scalar_triangle_system = values["scalar_triangle_differential_system"]
    generic_ghost_n3_integrated = values["generic_ghost_n3_pole3_integrated_functions"]
    generic_ghost_n3_i29 = values["generic_ghost_n3_I29_integrated_function"]
    generic_ghost_n3_symmetric = values["generic_ghost_n3_symmetric_point_simplex_integration"]
    generic_ghost_n1_n2 = values["generic_ghost_n1_n2_Hodge_resolvent_reduction"]
    generic_ghost_n1_n2_vector = values["generic_ghost_n1_n2_vector_CPT_projection"]
    generic_ghost_longitudinal_schur = values["generic_ghost_longitudinal_Schur_resummation"]
    generic_ghost_schur_schatten = values["generic_ghost_Schur_Schatten_split"]
    generic_ghost_schur_wodzicki = values["generic_ghost_Schur_Wodzicki_residue"]
    generic_ghost_schur_scale = values["generic_ghost_Schur_weighted_trace_scale"]
    round_s4_ghost_schur_finite = values["round_S4_ghost_Schur_finite_weighted_traces"]
    round_s4_ghost_schur_zeta = values["round_S4_ghost_Schur_zeta_factorization"]
    generic_ghost_schur_weight_raised = values["generic_ghost_Schur_weight_raised_zeta_factorization"]
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
        or physical_hessian_linear.get("gauge_crosswalk", {}).get("same_gauge")
        is not True
        or physical_hessian_linear.get("traceless_projector", {}).get(
            "projected_traceless_rank"
        )
        != 9
        or physical_hessian_linear.get("scalar_flat_restriction", {}).get(
            "surviving_term_counts"
        )
        != {"N_lambda": 6, "U": 3, "V_rho_sigma": 7}
        or physical_hessian_linear.get("third_curvature_applicability", {}).get(
            "status"
        )
        != "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY"
        or physical_hessian_linear.get("claim_flags", {}).get(
            "FULL_GENERIC_PHYSICAL_HESSIAN_SUPPLIED"
        )
        is not False
        or physical_hessian_h2.get("claim_flags", {}).get(
            "ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED"
        )
        is not True
        or physical_hessian_h2.get("claim_flags", {}).get(
            "GAUGE_ORDERING_DOES_NOT_CHANGE_ALGEBRAIC_H2"
        )
        is not True
        or physical_hessian_h2.get("scalar_flat_restriction", {}).get(
            "effective_term_count"
        )
        != 9
        or physical_hessian_h2.get("round_S4_crosscheck", {}).get("sum")
        != "+24 K^2-16 K^2=+8 K^2"
        or physical_hessian_h2.get("claim_flags", {}).get(
            "PHYSICAL_MIXED_H1_H2_TRACE_COMPUTED"
        )
        is not False
        or physical_hessian_n3_fixture.get("claim_flags", {}).get(
            "PHYSICAL_H1_FORMAL_ADJOINT_COMPLETION_VERIFIED"
        )
        is not True
        or physical_hessian_n3_fixture.get("claim_flags", {}).get(
            "PHYSICAL_N3_EXACT_INTERIOR_SIMPLEX_FIXTURE_COMPUTED"
        )
        is not True
        or physical_hessian_n3_fixture.get("exact_interior_fixture", {}).get(
            "Delta"
        )
        != {"numerator": 104, "denominator": 45}
        or physical_hessian_n3_fixture.get("exact_interior_fixture", {}).get(
            "loop_trace", {}
        ).get("monomial_count")
        != 210
        or physical_hessian_n3_fixture.get("exact_interior_fixture", {}).get(
            "formal_adjoint_check", {}
        ).get("completed_vertex_defect_count")
        != 0
        or physical_hessian_n3_fixture.get("claim_flags", {}).get(
            "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not False
        or physical_hessian_n3_projection.get("claim_flags", {}).get(
            "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"
        )
        is not True
        or physical_hessian_n3_projection.get("claim_flags", {}).get(
            "PHYSICAL_N3_TRIANGLE_INTEGRATED"
        )
        is not False
        or physical_hessian_n3_projection.get("interpolation_certificate", {}).get(
            "training_fixture_count"
        )
        != 28
        or physical_hessian_n3_projection.get("interpolation_certificate", {}).get(
            "degree_six_box_evaluation_rank_mod_prime"
        )
        != 28
        or physical_hessian_n3_obstruction.get("relative_quotient", {}).get(
            "symmetric_point_relative_IBP_plus_master_rank"
        )
        != 49
        or physical_hessian_n3_obstruction.get("relative_quotient", {}).get(
            "M14_augmented_rank"
        )
        != 50
        or physical_hessian_n3_obstruction.get("corner_asymptotic", {}).get(
            "total_log_1_over_epsilon_coefficient"
        )
        != {"numerator": 1, "denominator": 2}
        or physical_hessian_n3_obstruction.get("claim_flags", {}).get(
            "H2_CANCELLATION_OF_CORNER_CLASS_PROVED"
        )
        is not False
        or physical_hessian_mixed.get("result_state")
        != "RAW_MIXED_PHYSICAL_LOG_COEFFICIENT_NONZERO_SUBTRACTION_REQUIRED"
        or physical_hessian_mixed.get("combined_raw_logarithm", {}).get("sum")
        != {"numerator": 15707, "denominator": 216}
        or physical_hessian_mixed.get("claim_flags", {}).get(
            "RAW_ALGEBRAIC_H2_CANCELLATION_IDENTITY_REFUTED_BY_FIXTURE"
        )
        is not True
        or physical_hessian_mixed.get("claim_flags", {}).get(
            "RENORMALIZED_SUBTRACTION_FIXED"
        )
        is not False
        or physical_hessian_mixed.get("claim_flags", {}).get(
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED"
        )
        is not False
        or physical_hessian_mellin.get("claim_flags", {}).get(
            "FIXTURE_MINIMAL_SUBTRACTION_DISTRIBUTION_FIXED"
        )
        is not True
        or physical_hessian_mellin.get("claim_flags", {}).get(
            "GENERIC_COVARIANT_VOLTERRA_LIFT_COMPUTED"
        )
        is not False
        or physical_hessian_mellin.get("renormalization_scale_row", {}).get(
            "coefficient"
        )
        != {"numerator": 15707, "denominator": 216}
        or physical_hessian_volterra.get("claim_flags", {}).get(
            "GENERIC_COVARIANT_VOLTERRA_CARRIER_COMPUTED"
        )
        is not True
        or physical_hessian_volterra.get("claim_flags", {}).get(
            "GENERIC_TENSOR_KERNELS_EVALUATED"
        )
        is not False
        or physical_hessian_volterra.get("claim_flags", {}).get(
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED"
        )
        is not False
        or physical_hessian_contact_finite.get("claim_flags", {}).get(
            "GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED"
        )
        is not True
        or physical_hessian_contact_finite.get("claim_flags", {}).get(
            "FINITE_COUNTERTERM_NORMALIZATION_FIXED"
        )
        is not False
        or physical_hessian_contact_finite.get("claim_flags", {}).get(
            "RENORMALIZED_PHYSICAL_TRIANGLE_BULK_REDUCED"
        )
        is not False
        or physical_hessian_contact_finite.get("interpolation", {}).get("row_count")
        != 33
        or physical_hessian_contact_finite.get("equal_box_regression", {}).get(
            "combined_contact_finite_value"
        )
        != {"numerator": 3188, "denominator": 27}
        or physical_hessian_triangle_masters.get("claim_flags", {}).get(
            "ALL_ELEVEN_PHYSICAL_ROWS_IN_SIX_MASTER_SPAN"
        )
        is not True
        or physical_hessian_triangle_masters.get("claim_flags", {}).get(
            "STANDARD_S3_MASTER_PAIR_REQUIRED"
        )
        is not True
        or physical_hessian_triangle_masters.get("claim_flags", {}).get(
            "RENORMALIZED_SIX_MASTER_VALUES_COMPUTED"
        )
        is not False
        or physical_hessian_triangle_master_values.get("claim_flags", {}).get(
            "RENORMALIZED_M14_SINGLET_VALUE_COMPUTED"
        )
        is not True
        or physical_hessian_triangle_master_values.get("claim_flags", {}).get(
            "RENORMALIZED_STANDARD_S3_PAIR_VALUES_COMPUTED"
        )
        is not True
        or physical_hessian_triangle_master_values.get("claim_flags", {}).get(
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"
        )
        is not False
        or physical_hessian_triangle_master_coordinates.get("claim_flags", {}).get(
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED"
        )
        is not True
        or physical_hessian_triangle_master_coordinates.get("claim_flags", {}).get(
            "PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED"
        )
        is not False
        or len(physical_hessian_triangle_master_coordinates.get("channel_rows", []))
        != 11
        or physical_hessian_triangle_boundary_flux.get("claim_flags", {}).get(
            "PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED"
        )
        is not True
        or physical_hessian_triangle_boundary_flux.get("claim_flags", {}).get(
            "PHYSICAL_N3_TRIANGLE_INTEGRATED"
        )
        is not True
        or physical_hessian_triangle_boundary_flux.get("claim_flags", {}).get(
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"
        )
        is not False
        or physical_hessian_triangle_boundary_flux.get("identity_ledger", {}).get(
            "integrated_basis_coordinate_count"
        )
        != 77
        or physical_hessian_form_factors.get("claim_flags", {}).get(
            "FIVE_PHYSICAL_CARRIER_FUNCTIONS_ASSEMBLED"
        )
        is not True
        or physical_hessian_form_factors.get("claim_flags", {}).get(
            "ABSOLUTE_FINITE_C2_NORMALIZATION_FIXED"
        )
        is not False
        or physical_hessian_form_factors.get("quotient_ledger", {}).get(
            "quotient_dimension"
        )
        != 10
        or physical_plus_ghost_n3.get("claim_flags", {}).get(
            "PHYSICAL_PLUS_GHOST_N3_MELLIN_MS_REPRESENTATIVE_COMPUTED"
        )
        is not True
        or physical_plus_ghost_n3.get("claim_flags", {}).get(
            "FULL_BV_FORM_FACTORS_COMPUTED"
        )
        is not False
        or physical_plus_ghost_n3.get("quotient_ledger", {}).get(
            "quotient_dimension"
        )
        != 10
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
        or generic_ghost_n3_symmetric.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATED"
        )
        is not True
        or len(generic_ghost_n3_symmetric.get("channel_rows", [])) != 11
        or generic_ghost_n3_symmetric.get("claim_flags", {}).get(
            "GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED"
        )
        is not False
        or generic_ghost_n3_barycentric.get("factorization_summary", {}).get(
            "channels_with_exact_Delta_factor"
        )
        != 10
        or generic_ghost_n3_barycentric.get("factorization_summary", {}).get(
            "channels_with_nonzero_direct_open_edge_restriction"
        )
        != ["I10_123"]
        or generic_ghost_n3_barycentric.get("claim_flags", {}).get(
            "GENERIC_RELATIVE_IBP_REDUCTION_COMPUTED"
        )
        is not False
        or len(generic_ghost_n3_relative_ibp.get("channel_rows", [])) != 10
        or generic_ghost_n3_relative_ibp.get("rank_ledger", {}).get(
            "open_edge_tangent_plus_master_and_targets_rank"
        )
        != 30
        or generic_ghost_n3_relative_ibp.get("rank_ledger", {}).get(
            "corner_zero_tangent_plus_master_rank"
        )
        != 26
        or generic_ghost_n3_relative_ibp.get("claim_flags", {}).get(
            "TEN_POLE3_ROWS_REDUCED_TO_J_AND_TWO_DERIVATIVE_MASTERS"
        )
        is not True
        or generic_ghost_n3_relative_ibp.get("claim_flags", {}).get(
            "I29_POLE4_REDUCED"
        )
        is not False
        or scalar_triangle_system.get("claim_flags", {}).get(
            "SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED"
        )
        is not True
        or scalar_triangle_system.get("claim_flags", {}).get(
            "TWO_LOG_MASTER_REDUCTION_COMPUTED"
        )
        is not True
        or len(generic_ghost_n3_integrated.get("channel_rows", [])) != 10
        or generic_ghost_n3_integrated.get("claim_flags", {}).get(
            "TEN_POLE3_GENERIC_INTEGRATED_FUNCTIONS_COMPUTED"
        )
        is not True
        or generic_ghost_n3_integrated.get("identity_ledger", {}).get(
            "symmetric_point_regression_status"
        )
        != "ALL_EXACT_MATCH"
        or generic_ghost_n3_integrated.get("claim_flags", {}).get(
            "I29_POLE4_REDUCED"
        )
        is not False
        or generic_ghost_n3_i29.get("rank_ledger", {}).get("tangent_rank") != 46
        or generic_ghost_n3_i29.get("rank_ledger", {}).get(
            "tangent_plus_masters_rank"
        )
        != 49
        or generic_ghost_n3_i29.get("rank_ledger", {}).get(
            "tangent_plus_masters_and_target_rank"
        )
        != 49
        or generic_ghost_n3_i29.get("exact_reconstruction", {}).get(
            "full_55_row_symbolic_relative_IBP_defect"
        )
        != "ZERO"
        or generic_ghost_n3_i29.get("claim_flags", {}).get("I29_POLE4_REDUCED")
        is not True
        or generic_ghost_n3_i29.get("claim_flags", {}).get(
            "ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED"
        )
        is not True
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
        or round_s4_ghost_schur_zeta.get("local_residue_derivation", {}).get(
            "exact_factorization_defect"
        )
        != {"numerator": 5, "denominator": 3}
        or round_s4_ghost_schur_zeta.get("claim_flags", {}).get(
            "ROUND_S4_ZETA_FACTORIZED_SCHUR_RATIO_COMPUTED"
        )
        is not True
        or round_s4_ghost_schur_zeta.get("claim_flags", {}).get(
            "GENERIC_NONCOMMUTING_ZETA_FACTORIZATION_DEFECT_COMPUTED"
        )
        is not False
        or generic_ghost_schur_weight_raised.get("generic_local_result", {}).get(
            "coefficient_of_(4pi)^-2_integral_R2"
        )
        != {"numerator": -1, "denominator": 108}
        or generic_ghost_schur_weight_raised.get("generic_local_result", {}).get(
            "coefficient_of_(4pi)^-2_integral_Ric2"
        )
        != {"numerator": -1, "denominator": 54}
        or generic_ghost_schur_weight_raised.get("round_S4_crosscheck", {}).get(
            "weight_raised_defect"
        )
        != {"numerator": -1, "denominator": 3}
        or generic_ghost_schur_weight_raised.get("factorization_convention_crosswalk", {}).get(
            "difference_of_defects"
        )
        != {"numerator": 2, "denominator": 1}
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
    physical_hessian_linear = values["generic_physical_hessian_linear_curvature"]
    physical_hessian_h2 = values["generic_physical_hessian_curvature_squared"]
    physical_hessian_n3_fixture = values["generic_physical_hessian_n3_triangle_fixture"]
    physical_hessian_n3_projection = values[
        "generic_physical_hessian_n3_five_carrier_projection"
    ]
    physical_hessian_n3_obstruction = values[
        "generic_physical_hessian_n3_integration_obstruction"
    ]
    physical_hessian_mixed = values[
        "generic_physical_hessian_mixed_H1_H2_corner_fixture"
    ]
    physical_hessian_mellin = values[
        "generic_physical_hessian_mellin_subtraction_scale_row"
    ]
    physical_hessian_volterra = values[
        "generic_physical_hessian_covariant_Volterra_carrier"
    ]
    physical_hessian_contacts = values[
        "generic_physical_hessian_H1_H2_contact_residue_projection"
    ]
    physical_hessian_incidence = values[
        "generic_physical_hessian_symmetric_mixed_boundary_incidence"
    ]
    physical_hessian_triangle_residues = values[
        "generic_physical_hessian_triangle_corner_residues"
    ]
    physical_hessian_full_incidence = values[
        "generic_physical_hessian_full_boundary_incidence"
    ]
    physical_hessian_contact_finite = values[
        "generic_physical_hessian_H1_H2_contact_finite_rows"
    ]
    physical_hessian_triangle_masters = values[
        "generic_physical_hessian_triangle_master_completeness"
    ]
    physical_hessian_triangle_master_values = values[
        "generic_physical_hessian_triangle_renormalized_master_values"
    ]
    physical_hessian_triangle_master_coordinates = values[
        "generic_physical_hessian_triangle_six_master_coordinates"
    ]
    physical_hessian_triangle_boundary_flux = values[
        "generic_physical_hessian_triangle_relative_IBP_boundary_flux"
    ]
    physical_hessian_form_factors = values[
        "generic_physical_hessian_third_curvature_form_factors"
    ]
    physical_plus_ghost_n3 = values[
        "generic_physical_plus_ghost_n3_third_curvature_form_factors"
    ]
    generic_ghost_cpt = values["generic_background_ghost_CPT_obstruction"]
    generic_ghost_endo = values["generic_ghost_Endo_Duhamel_reduction"]
    generic_ghost_n3 = values["generic_ghost_n3_adiabatic_carrier"]
    generic_ghost_n3_triangle = values["generic_ghost_n3_triangle_kernel"]
    scalar_flat_k_ricci = values["scalar_flat_K_Ricci_crosswalk"]
    generic_ghost_n3_projection = values["generic_ghost_n3_five_carrier_projection"]
    generic_ghost_n3_barycentric = values["generic_ghost_n3_barycentric_factorization"]
    generic_ghost_n3_relative_ibp = values["generic_ghost_n3_pole3_relative_IBP"]
    scalar_triangle_system = values["scalar_triangle_differential_system"]
    generic_ghost_n3_integrated = values["generic_ghost_n3_pole3_integrated_functions"]
    generic_ghost_n3_i29 = values["generic_ghost_n3_I29_integrated_function"]
    generic_ghost_n3_symmetric = values["generic_ghost_n3_symmetric_point_simplex_integration"]
    generic_ghost_n1_n2 = values["generic_ghost_n1_n2_Hodge_resolvent_reduction"]
    generic_ghost_n1_n2_vector = values["generic_ghost_n1_n2_vector_CPT_projection"]
    generic_ghost_longitudinal_schur = values["generic_ghost_longitudinal_Schur_resummation"]
    generic_ghost_schur_schatten = values["generic_ghost_Schur_Schatten_split"]
    generic_ghost_schur_wodzicki = values["generic_ghost_Schur_Wodzicki_residue"]
    generic_ghost_schur_scale = values["generic_ghost_Schur_weighted_trace_scale"]
    round_s4_ghost_schur_finite = values["round_S4_ghost_Schur_finite_weighted_traces"]
    round_s4_ghost_schur_zeta = values["round_S4_ghost_Schur_zeta_factorization"]
    generic_ghost_schur_weight_raised = values["generic_ghost_Schur_weight_raised_zeta_factorization"]
    box_r_scheme_conversion = values["BoxR_scheme_conversion"]
    return {
        "schema": "paper-12-pure-weyl-one-loop-bv-anomaly-claim-map-v1",
        "result_id": "PAPER_12_PURE_WEYL_ONE_LOOP_BV_ANOMALY_DRAFT",
        "result_state": "DRAFT_ALLOWED_STRICT_OBSTRUCTION_TAU_ADIC_EXTENDED_QME_RESTORATION_ANOMALY_INDUCED_GAMMA1_AND_FV_CONFORMIZED_C2_LOGARITHM",
        "lifecycle_state": "WRITING_STARTED",
        "referee_revision": {
            "review_snapshot": "EARLIER_TEN_PAGE_SNAPSHOT",
            "requested_revision_status": "IMPLEMENTED_AND_MACHINE_REPLAYED",
            "human_scientific_review_status": "PENDING",
            "theorem_freeze_authorized": False,
        },
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
        ],
        "headline": "Strict pure Weyl gravity is locally QME-obstructed at one loop; the formal tau-adic compensator extension has a restored one-loop local Euclidean QME; the FV anomaly action fixes the Ricci-scalar sector, the algebraic C3 basis is complete, and the parity-even five-carrier third-curvature manifest has an exact scalar-flat I29 symmetry enhancement and 11-to-10 effective label quotient. Five universal CPT source kernels are exact and the generic ghost n=3 triangle is projected exactly onto that quotient. Ten generic numerators cancel one Delta; only I10 has a nonzero direct open-edge restriction, while the I28 relation is pointwise. All ten pole-three rows have exact relative-IBP primitives. The exact S3-covariant scalar-triangle differential system reduces their derivative masters to J and two bubble-log ratios, while equal corner weights make the sole nonzero corner flux rational. The pole-four I29 row also reduces by a full 55-row exact relative-IBP identity to the same master basis, so all eleven generic ghost n=3 functions are complete and regress exactly to the symmetric-point integration. The curved n=1/n=2 pure-vector CPT sum is exact, and all longitudinal D_W towers are resummed into one normalized scalar Schur kernel. The Schur correction lies in S_3; Wres(K), Wres(K^2), and Wres(log S_L) are exact, the declared order-two weighted trace fixes the pole and scale row, and the round-S4 reference finite K/K2 rows, canonical det_3 tail, weighted modified determinant, and Einstein-ratio defect 5/3 are complete. The distinct generic weight-raised local defect is exactly -(1/4)Wres(K^2) and specializes to -1/3. A smoothing witness proves that the generic finite rows require a full Green kernel or spectral measure. The same-gauge physical three-H1 alpha numerator is exact and projected onto all eleven raw channels of the five-carrier quotient. Its isolated symmetric-point integral is logarithmically corner obstructed by a rank-one M14 class. The projected algebraic H2 block is imported and operationally polarized on an exact equal-box TT fixture. All six H1-cubed orderings and all six mixed-bubble endpoints give the nonzero raw logarithmic coefficient 15707/216. A generic covariant Volterra carrier joins the six ordered triangle cells and three H1-H2 contact cells under the common Mellin extension. All generic contact endpoint residues are projected to 33 exact raw five-carrier functions with two unseen replays and exact I28 reduction. The three generic triangle corner functions and their full contact incidence are exact and nonzero, so M14 is disposed as a Mellin-renormalized scale row. The minimally-subtracted finite parts of all three H1-H2 contacts are also projected to 33 exact rational rows; their equal-box TT sum is 3188/27. The eleven integrated triangle channels, finite contacts and combined scale rows are now assembled into five exact carrier-labelled physical-Hessian Mellin-MS functions. Generic ghost and remaining BV finite rows, complete repository functions and coefficients, odd derivative data and finite normalizations remain open.",
        "manuscript": _relative(MANUSCRIPT),
        "latest_coefficient_update": "All eleven integrated generic scalar-flat ghost n=3 channels are added to the physical-Hessian Mellin-MS five-carrier representative with the exact ten-dimensional I28 quotient preserved; ghost n1/n2, generic finite Schur and remaining BV rows stay open.",
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
            "same_gauge_physical_Hessian_linear_curvature_imported": True,
            "physical_Hessian_linear_formula_digest": physical_hessian_linear["source_operator"]["formula_digest"],
            "physical_Hessian_linear_source_row_counts": {
                name: len(rows)
                for name, rows in physical_hessian_linear["source_operator"]["coefficient_rows"].items()
            },
            "physical_Hessian_scalar_flat_surviving_row_counts": physical_hessian_linear["scalar_flat_restriction"]["surviving_term_counts"],
            "physical_Hessian_repository_normalization": physical_hessian_linear["repository_normalization"]["repository_functional_Hessian"],
            "physical_Hessian_algebraic_H2_imported": True,
            "physical_Hessian_H2_formula_digest": physical_hessian_h2["source_operator"]["formula_digest"],
            "physical_Hessian_H2_source_row_count": len(physical_hessian_h2["source_operator"]["coefficient_rows"]),
            "physical_Hessian_H2_scalar_flat_effective_row_count": physical_hessian_h2["scalar_flat_restriction"]["effective_term_count"],
            "physical_Hessian_H2_gauge_ordering_crosswalk": physical_hessian_h2["gauge_ordering_crosswalk"]["monic_H1_difference"],
            "physical_Hessian_H2_round_algebraic_eigenvalue": physical_hessian_h2["round_S4_crosscheck"]["algebraic_U2_on_TT"],
            "physical_Hessian_H2_round_commutator_split": physical_hessian_h2["round_S4_crosscheck"]["sum"],
            "physical_n3_three_linear_insertion_vertex_ready": True,
            "physical_H1_formal_adjoint_momentum_vertex_verified": True,
            "physical_n3_exact_interior_simplex_fixture_computed": True,
            "physical_n3_interior_fixture_Delta": physical_hessian_n3_fixture["exact_interior_fixture"]["Delta"],
            "physical_n3_interior_fixture_loop_monomial_count": physical_hessian_n3_fixture["exact_interior_fixture"]["loop_trace"]["monomial_count"],
            "physical_n3_interior_fixture_kernel_without_4pi2": physical_hessian_n3_fixture["exact_interior_fixture"]["kernel_without_(4pi)^-2"],
            "physical_n3_full_alpha_polynomial_computed": True,
            "physical_n3_five_carrier_projection_computed": True,
            "physical_n3_projection_formula_digest": physical_hessian_n3_projection["formula_digest"],
            "physical_n3_projection_training_fixture_count": physical_hessian_n3_projection["interpolation_certificate"]["training_fixture_count"],
            "physical_n3_projection_unseen_fixture_count": physical_hessian_n3_projection["interpolation_certificate"]["unseen_fixture_count"],
            "physical_n3_projection_exact_term_count": sum(
                row["term_count"]
                for row in physical_hessian_n3_projection["projection_rows"]
            ),
            "physical_n3_isolated_H1_integration_corner_obstructed": True,
            "physical_n3_M14_relative_rank_jump": physical_hessian_n3_obstruction["relative_quotient"]["M14_rank_jump"],
            "physical_n3_M14_total_log_corner_coefficient": physical_hessian_n3_obstruction["corner_asymptotic"]["total_log_1_over_epsilon_coefficient"],
            "physical_n3_M14_nonzero_raw_orientation_count": len(physical_hessian_n3_obstruction["nonzero_obstruction_channels"]),
            "physical_Hessian_operational_H2_polarization_fixture": True,
            "physical_Hessian_raw_H1_cubed_log_coefficient": physical_hessian_mixed["combined_raw_logarithm"]["three_H1_corner_coefficient"],
            "physical_Hessian_raw_mixed_H1_H2_log_coefficient": physical_hessian_mixed["combined_raw_logarithm"]["mixed_H1_H2_endpoint_coefficient"],
            "physical_Hessian_raw_combined_log_coefficient": physical_hessian_mixed["combined_raw_logarithm"]["sum"],
            "physical_Hessian_universal_algebraic_H2_cancellation_refuted_by_fixture": True,
            "physical_Hessian_fixture_Mellin_minimal_subtraction_fixed": True,
            "physical_Hessian_fixture_log_mu2_scale_coefficient": physical_hessian_mellin["renormalization_scale_row"]["coefficient"],
            "physical_Hessian_generic_covariant_Volterra_carrier_computed": True,
            "physical_Hessian_Volterra_ordered_triangle_cell_count": physical_hessian_volterra["decorated_carrier"]["ordered_triangle_cell_count"],
            "physical_Hessian_Volterra_mixed_contact_cell_count": physical_hessian_volterra["decorated_carrier"]["mixed_contact_cell_count"],
            "physical_Hessian_generic_contact_endpoint_residues_projected": True,
            "physical_Hessian_generic_contact_projection_row_count": physical_hessian_contacts["interpolation"]["row_count"],
            "physical_Hessian_generic_contact_unseen_fixture_count": physical_hessian_contacts["interpolation"]["unseen_fixture_count"],
            "physical_Hessian_generic_contact_formula_digest": physical_hessian_contacts["interpolation"]["formula_digest"],
            "physical_Hessian_symmetric_mixed_boundary_incidence_assembled": True,
            "physical_Hessian_symmetric_H2_cancellation_refuted": True,
            "physical_Hessian_symmetric_triangle_full_log_coefficient": physical_hessian_incidence["equal_box_tensor_reconstruction"]["triangle_full_log_coefficient"],
            "physical_Hessian_symmetric_contact_full_log_coefficient": physical_hessian_incidence["equal_box_tensor_reconstruction"]["contact_full_log_coefficient"],
            "physical_Hessian_symmetric_combined_log_mu2_coefficient": physical_hessian_incidence["equal_box_tensor_reconstruction"]["combined_log_mu2_coefficient"],
            "physical_Hessian_generic_triangle_corner_residues_computed": True,
            "physical_Hessian_generic_triangle_symmetric_rows_replayed": physical_hessian_triangle_residues["regressions"]["symmetric_obstruction_rows_matched"],
            "physical_Hessian_full_generic_boundary_incidence_assembled": True,
            "physical_Hessian_generic_M14_disposed": True,
            "physical_Hessian_generic_M14_disposition": physical_hessian_full_incidence["generic_disposition"]["M14"],
            "physical_Hessian_generic_contact_finite_rows_computed": True,
            "physical_Hessian_generic_contact_finite_row_count": physical_hessian_contact_finite["interpolation"]["row_count"],
            "physical_Hessian_generic_contact_finite_unseen_fixture_count": physical_hessian_contact_finite["interpolation"]["unseen_fixture_count"],
            "physical_Hessian_equal_box_contact_finite_value": physical_hessian_contact_finite["equal_box_regression"]["combined_contact_finite_value"],
            "physical_Hessian_triangle_six_master_span_complete": True,
            "physical_Hessian_triangle_six_master_generic_rank": physical_hessian_triangle_masters["rank_ladder"][-1]["generic_rank"],
            "physical_Hessian_triangle_standard_S3_pair_required": True,
            "physical_Hessian_triangle_renormalized_new_master_values_computed": True,
            "physical_Hessian_triangle_renormalized_master_value_count": len(physical_hessian_triangle_master_values["master_rows"]),
            "physical_Hessian_triangle_six_master_coordinates_computed": True,
            "physical_Hessian_triangle_six_master_coordinate_count": sum(len(row["master_coordinates"]) for row in physical_hessian_triangle_master_coordinates["channel_rows"]),
            "physical_Hessian_triangle_relative_IBP_boundary_flux_computed": True,
            "physical_Hessian_triangle_integrated_channel_count": physical_hessian_triangle_boundary_flux["identity_ledger"]["channel_count"],
            "physical_Hessian_triangle_corner_count": physical_hessian_triangle_boundary_flux["identity_ledger"]["corner_count"],
            "physical_Hessian_triangle_structured_basis_coordinate_count": physical_hessian_triangle_boundary_flux["identity_ledger"]["integrated_basis_coordinate_count"],
            "physical_Hessian_five_carrier_Mellin_MS_form_factors_assembled": True,
            "physical_Hessian_form_factor_carrier_count": physical_hessian_form_factors["quotient_ledger"]["carrier_function_count"],
            "physical_Hessian_form_factor_orientation_channel_count": physical_hessian_form_factors["quotient_ledger"]["raw_orientation_channel_count"],
            "physical_Hessian_form_factor_quotient_dimension": physical_hessian_form_factors["quotient_ledger"]["quotient_dimension"],
            "physical_Hessian_finite_C2_normalization": physical_hessian_form_factors["scheme_disposition"]["finite_C2_normalization"],
            "physical_plus_ghost_n3_five_carrier_representative_assembled": True,
            "physical_plus_ghost_n3_channel_count": physical_plus_ghost_n3["quotient_ledger"]["raw_channel_count"],
            "physical_plus_ghost_n3_quotient_dimension": physical_plus_ghost_n3["quotient_ledger"]["quotient_dimension"],
            "physical_plus_ghost_n3_I28_relation_status": physical_plus_ghost_n3["quotient_ledger"]["relation_status"],
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
            "generic_ghost_n3_generic_Delta_cancellation_count": generic_ghost_n3_barycentric["factorization_summary"]["channels_with_exact_Delta_factor"],
            "generic_ghost_n3_unique_direct_edge_source": generic_ghost_n3_barycentric["factorization_summary"]["channels_with_nonzero_direct_open_edge_restriction"],
            "generic_ghost_n3_minimum_vertex_integrability_margin": generic_ghost_n3_barycentric["factorization_summary"]["minimum_vertex_integrability_margin"],
            "generic_ghost_n3_pointwise_I28_relation": generic_ghost_n3_barycentric["factorization_summary"]["pointwise_I28_relation"],
            "generic_ghost_n3_barycentric_formula_digest": generic_ghost_n3_barycentric["formula_digest"],
            "generic_ghost_n3_pole3_relative_IBP_channel_count": len(generic_ghost_n3_relative_ibp["channel_rows"]),
            "generic_ghost_n3_pole3_master_span_rank": generic_ghost_n3_relative_ibp["rank_ledger"]["open_edge_tangent_plus_master_and_targets_rank"],
            "generic_ghost_n3_corner_zero_span_rank": generic_ghost_n3_relative_ibp["rank_ledger"]["corner_zero_tangent_plus_master_rank"],
            "generic_ghost_n3_corner_zero_augmented_ranks": [row["augmented_rank"] for row in generic_ghost_n3_relative_ibp["rank_ledger"]["corner_zero_augmented_ranks"]],
            "generic_ghost_n3_pole3_relative_IBP_formula_digest": generic_ghost_n3_relative_ibp["formula_digest"],
            "scalar_triangle_differential_system_computed": True,
            "scalar_triangle_differential_formula_digest": scalar_triangle_system["formula_digest"],
            "generic_ghost_n3_ten_pole3_integrated_functions": True,
            "generic_ghost_n3_pole3_integrated_formula_digest": generic_ghost_n3_integrated["formula_digest"],
            "generic_ghost_n3_pole3_integrated_symmetric_regressions": generic_ghost_n3_integrated["identity_ledger"]["symmetric_point_regression_count"],
            "generic_ghost_n3_I29_pole4_reduced": True,
            "generic_ghost_n3_I29_formula_digest": generic_ghost_n3_i29["formula_digest"],
            "generic_ghost_n3_I29_full_symbolic_defect": generic_ghost_n3_i29["exact_reconstruction"]["full_55_row_symbolic_relative_IBP_defect"],
            "generic_ghost_n3_I29_symmetric_J_coefficient": generic_ghost_n3_i29["identity_ledger"]["symmetric_point_J_coefficient"],
            "generic_ghost_n3_I29_symmetric_rational_term": generic_ghost_n3_i29["identity_ledger"]["symmetric_point_rational_term"],
            "generic_ghost_n3_all_eleven_functions_computed": True,
            "generic_ghost_n3_symmetric_point_simplex_integrated": True,
            "generic_ghost_n3_symmetric_point": generic_ghost_n3_symmetric["scope"]["kinematic_point"],
            "generic_ghost_n3_symmetric_point_channel_count": len(generic_ghost_n3_symmetric["channel_rows"]),
            "generic_ghost_n3_symmetric_point_scalar_master": generic_ghost_n3_symmetric["scalar_triangle_master"]["closed_form"],
            "generic_ghost_n3_symmetric_point_formula_digest": generic_ghost_n3_symmetric["formula_digest"],
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
            "generic_ghost_unspecified_factorization_zeta_anomaly_status": generic_ghost_longitudinal_schur["regularization_boundary"]["zeta_multiplicative_anomaly"],
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
            "round_S4_ghost_Schur_det3_tail": round_s4_ghost_schur_finite["exact_finite_rows"]["canonical_det3_tail"],
            "round_S4_ghost_Schur_weighted_modified_determinant": round_s4_ghost_schur_finite["exact_finite_rows"]["full_modified_determinant"],
            "round_S4_ghost_Schur_zeta_weighted_factorization_defect": round_s4_ghost_schur_zeta["local_residue_derivation"]["exact_factorization_defect"],
            "round_S4_ghost_Schur_zeta_determinant_ratio": round_s4_ghost_schur_zeta["factorization_result"]["zeta_determinant_ratio_decimal"],
            "generic_ghost_weight_raised_local_factorization_defect": generic_ghost_schur_weight_raised["generic_local_result"]["operator_formula"],
            "generic_ghost_weight_raised_R2_coefficient": generic_ghost_schur_weight_raised["generic_local_result"]["coefficient_of_(4pi)^-2_integral_R2"],
            "generic_ghost_weight_raised_Ric2_coefficient": generic_ghost_schur_weight_raised["generic_local_result"]["coefficient_of_(4pi)^-2_integral_Ric2"],
            "round_S4_weight_raised_factorization_defect": generic_ghost_schur_weight_raised["round_S4_crosscheck"]["weight_raised_defect"],
            "round_S4_weight_raised_zeta_determinant_ratio": generic_ghost_schur_weight_raised["round_S4_crosscheck"]["zeta_ratio_log_det_(S_L_Delta)_minus_log_det_Delta"],
            "factorization_convention_defect_difference": generic_ghost_schur_weight_raised["factorization_convention_crosswalk"]["difference_of_defects"],
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
            "full_generic_physical_Hessian": False,
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
            "generic_ghost_zeta_multiplicative_anomaly_computed_without_declared_factorization": False,
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
            "status": "COMPUTE_GHOST_N1_N2_AND_GENERIC_FINITE_SCHUR_ROWS_THEN_ADD_REMAINING_BV_SECTORS",
            "required_inputs": [
                "same-background compensator-inclusive classical contraction",
                "finite C2 and absolute dressed Rhat2 normalization conditions",
                "full generic-background primed Green/resolvent kernel or complete spectral measure for the reference-scale finite R(K), finite R(K^2), and det3 rows; the round-S4 special-background benchmark is complete but does not substitute for this global carrier",
                "curved-Endo ghost n1/n2 and generic finite Schur rows from a primed Green/resolvent kernel or complete spectral measure, to be added with remaining BV sectors to the physical-plus-ghost-n3 five-carrier representative",
                "remaining trace substitutions matching the complete full-BV rows to repository parity-even third-curvature functions and coefficients, the parity-odd derivative carrier manifest, and global Paneitz/FV Green data",
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

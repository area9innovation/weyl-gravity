#!/usr/bin/env python3
"""Independent fail-closed verification of the Paper 12 claim map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_MAP = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(CLAIM_MAP.read_text())
    assert payload["schema"] == "paper-12-pure-weyl-one-loop-bv-anomaly-claim-map-v1"
    assert payload["result_id"] == "PAPER_12_PURE_WEYL_ONE_LOOP_BV_ANOMALY_DRAFT"
    assert payload["lifecycle_state"] == "WRITING_STARTED"
    assert payload["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    manuscript = ROOT / payload["manuscript"]
    assert manuscript.is_file()
    assert _sha256(manuscript) == payload["manuscript_sha256"]
    compiled_pdf = ROOT / payload["compiled_pdf"]
    assert compiled_pdf.is_file()
    assert _sha256(compiled_pdf) == payload["compiled_pdf_sha256"]
    artifacts = payload["publication_artifacts"]
    assert len(artifacts) == 6
    for relative, expected in artifacts.items():
        artifact = ROOT / relative
        assert artifact.is_file(), relative
        assert _sha256(artifact) == expected, relative

    dispositions = payload["theory_dispositions"]
    assert dispositions == {
        "strict_fixed_field_content": "OBSTRUCTED",
        "tau_adic_compensator_extended_local_Euclidean_one_loop": "QME_RESTORED",
    }
    claims = payload["certified_claims"]
    assert claims["strict_quotient_scope"] == "REGULAR_BACH_LOCUS"
    assert claims["minimal_Koszul_Tate_collapse_page"] == "E2"
    assert claims["Euclidean_symbol_bundle_dimensions"] == [5, 10, 5]
    assert claims["determinant_factor_count"] == 4
    assert claims["determinant_to_Slavnov_bridge_displayed"] is True
    assert claims["strict_full_gauge_fixed_H14_even_dimension"] == 2
    assert claims["strict_full_gauge_fixed_H14_odd_dimension"] == 1
    assert claims["pure_Diff_and_mixed_additional_classes"] == 0
    assert claims["C2_coefficient"] == {"numerator": 199, "denominator": 30}
    assert claims["E4_coefficient"] == {"numerator": -87, "denominator": 20}
    assert claims["CdualC_coefficient"] == {"numerator": 0, "denominator": 1}
    assert claims["BoxR_coefficient"] == {"numerator": 0, "denominator": 1}
    assert claims["extended_H04_even_dimension"] == 3
    assert claims["extended_H04_odd_dimension"] == 1
    assert claims["extended_H14_even_dimension"] == 0
    assert claims["extended_H14_odd_dimension"] == 0
    assert claims["finite_counterterm_bulk_Q1_ambiguity_rank"] == 2
    assert claims["anomaly_induced_nonlocal_Gamma1_representative"] is True
    assert claims["anomaly_induced_functional_coefficients"] == [
        {"numerator": 199, "denominator": 120},
        {"numerator": -87, "denominator": 160},
        {"numerator": 29, "denominator": 120},
    ]
    assert claims["flat_TT_logarithmic_form_factor"] is True
    assert claims["flat_TT_logarithmic_coefficient"] == {
        "numerator": -199,
        "denominator": 60,
    }
    assert claims["flat_TT_scale_response"] == {
        "numerator": 199,
        "denominator": 30,
    }
    assert claims["covariant_C2_log_through_curvature_order_two"] is True
    assert claims["first_unresolved_C2_log_completion_order"] == 3
    assert claims["FV_conformized_C2_log_local_Weyl_completion"] is True
    assert claims["FV_scalar_flat_representative"] == "EXACT_SCALAR_FLAT_REPRESENTATIVE_ON_DECLARED_INVERSE_DOMAIN"
    assert claims["FV_first_forced_completion_order"] == 3
    assert claims["FV_and_WZ_dressed_metrics_distinct"] is True
    assert claims["FV_anomaly_action_fixed"] is True
    assert claims["Ricci_scalar_sector_structurally_dependent"] is True
    assert (
        claims["nonlocal_R2_form_factor_disposition"]
        == "NOT_AN_INDEPENDENT_DATUM_IN_DECLARED_FV_CONFORMAL_DECOMPOSITION"
    )
    assert claims["algebraic_C3_carrier_dimensions"] == {"even": 1, "odd": 1}
    assert claims["algebraic_C3_chiral_parity_crosswalk_exact"] is True
    assert claims["parity_even_third_curvature_carrier_count"] == 5
    assert claims["third_curvature_raw_label_dimension"] == 12
    assert claims["third_curvature_4d_quotient_label_dimension"] == 11
    assert claims["third_curvature_functional_relation_rank"] == 1
    assert claims["universal_CPT_third_curvature_kernels_imported"] is True
    assert claims["universal_CPT_source_fixture_status"] == "COEFFICIENT_COMPUTED"
    assert claims["universal_CPT_kernel_box_homogeneities"] == [-1, -2, -2, -3, -4]
    assert claims["generic_background_ghost_minimal_CPT_substitution_obstructed"] is True
    assert claims["generic_background_ghost_effective_divergence_coefficient"] == {
        "numerator": 1,
        "denominator": 2,
    }
    assert claims["generic_background_ghost_principal_eigenvalues"] == [
        {"numerator": 3, "denominator": 2},
        {"numerator": 1, "denominator": 1},
        {"numerator": 1, "denominator": 1},
        {"numerator": 1, "denominator": 1},
    ]
    assert claims["Einstein_scalar_ghost_factor_reproduced"] is True
    assert claims["generic_ghost_Endo_Duhamel_reduction_supplied"] is True
    assert claims["generic_ghost_Endo_alpha"] == {"numerator": -1, "denominator": 2}
    assert claims["generic_ghost_local_perturbation"] == "W=-2 Ric"
    assert claims["generic_ghost_maximum_cubic_Ricci_insertions"] == 3
    assert claims["generic_ghost_n3_adiabatic_angular_carrier"] is True
    assert claims["generic_ghost_n3_angular_tr_R3_coefficient"] == {
        "numerator": 503,
        "denominator": 648,
    }
    assert claims["generic_ghost_n3_Tr_log_tr_R3_coefficient"] == {
        "numerator": -503,
        "denominator": 243,
    }
    assert claims["generic_ghost_n3_zero_momentum_stabilizer"] == "S3"
    assert claims["generic_ghost_n3_nonzero_momentum_parametric_kernel"] is True
    assert claims["generic_ghost_n3_projector_sector_count"] == 8
    assert claims["generic_ghost_n3_total_Wick_rows"] == 20
    assert claims["raw_zeta_BoxR_coefficient"] == {
        "basis": ["1", "log(3/2)"],
        "rational": {"numerator": -159, "denominator": 80},
        "log_3_over_2": {"numerator": 7, "denominator": 2},
    }
    assert claims["raw_to_repository_R2_scheme_shift"] == {
        "basis": ["1", "log(3/2)"],
        "rational": {"numerator": -53, "denominator": 320},
        "log_3_over_2": {"numerator": 7, "denominator": 24},
    }
    assert claims["repository_29_over_120_local_R2_reproduced"] is True
    assert claims["Berger_WZ_tau_contraction_merge_rejected"] is True
    assert claims["Euler_Wess_Zumino_primitive_displayed"] is True
    boolean_claims = {
        key: value for key, value in claims.items() if isinstance(value, bool)
    }
    assert boolean_claims and all(boolean_claims.values())
    assert payload["explicit_nonclaims"]
    assert all(value is False for value in payload["explicit_nonclaims"].values())
    assert (
        payload["next_gate"]["status"]
        == "PROJECT_GHOST_N3_TRIANGLE_TO_REPOSITORY_I10_COMPUTE_N1_N2_CURVED_ENDO_TRACES_AND_PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL"
    )

    dependencies = {}
    assert len(payload["inputs"]) == 26
    for relative, reference in payload["inputs"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert _sha256(path) == reference["sha256"], relative
        value = json.loads(path.read_text())
        assert value["result_id"] == reference["result_id"], relative
        dependencies[reference["result_id"]] = value

    strict = dependencies["REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"]
    extended = dependencies["WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY"]
    q1 = dependencies["ONE_LOOP_SLAVNOV_Q1_DISPOSITION"]
    gamma1 = dependencies["ANOMALY_INDUCED_NONLOCAL_GAMMA1"]
    flat_tt_log = dependencies["FLAT_TT_LOGARITHMIC_GAMMA1"]
    curvature_squared_log = dependencies["CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1"]
    fv_conformized_log = dependencies["FV_CONFORMIZED_C2_LOG_GAMMA1"]
    fv_anomaly_ricci = dependencies["FV_ANOMALY_ACTION_RICCI_SECTOR"]
    cubic_weyl = dependencies["FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS"]
    third_curvature_weyl = dependencies["FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST"]
    cpt_kernels = dependencies["CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS"]
    generic_ghost_cpt = dependencies["GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION"]
    generic_ghost_endo = dependencies["GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION"]
    generic_ghost_n3 = dependencies["GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER"]
    generic_ghost_n3_triangle = dependencies["GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL"]
    box_r_scheme_conversion = dependencies["WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION"]
    minimal_kt = dependencies["MINIMAL_BV_KOSZUL_TATE_COLLAPSE"]
    elliptic = dependencies["REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX"]
    multiplicity = dependencies["REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER"]
    wz_preflight = dependencies["WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT"]
    assert strict["qme_disposition"]["status"] == "OBSTRUCTED_STRICT_FIELD_CONTENT"
    assert strict["coefficients"]["ANOM_OMEGA_C2"] == claims["C2_coefficient"]
    assert strict["coefficients"]["ANOM_OMEGA_E4"] == claims["E4_coefficient"]
    assert extended["H04"]["even_quotient_dimension"] == 3
    assert extended["H14"]["boundary_rank"] == 4
    assert (
        extended["one_loop_QME"]["strict_breaking_coordinates"]
        == extended["one_loop_QME"]["boundary_image_coordinates"]
    )
    assert extended["lifecycle"]["residual_transfer"].startswith("FORBIDDEN_")
    assert q1["finite_counterterm_ambiguity"]["bulk_response_rank"] == 2
    assert q1["decision"]["complete_Q1"] == "NO_CERTIFIED_OPERATOR"
    assert q1["decision"]["residual_transfer"] == "FORBIDDEN"
    assert gamma1["exact_coefficient_solve"]["rank"] == 3
    assert gamma1["decision"]["complete_finite_nonlocal_Gamma1"] == "NO_CERTIFIED_FUNCTIONAL"
    assert flat_tt_log["decision"]["flat_TT_universal_logarithmic_form_factor"] == "CERTIFIED"
    assert flat_tt_log["claim_flags"]["FINITE_C2_NORMALIZATION_FIXED"] is False
    assert curvature_squared_log["operator_choice_independence"]["first_difference_order"] == 3
    assert curvature_squared_log["decision"]["residual_transfer"] == "FORBIDDEN"
    assert fv_conformized_log["decision"]["selected_C2_log_local_Weyl_completion"] == "CERTIFIED"
    assert fv_conformized_log["carrier_crosswalk"]["identity_status"] == "DISTINCT_CARRIERS_NO_IDENTIFICATION"
    assert fv_conformized_log["claim_flags"]["INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED"] is False
    assert fv_anomaly_ricci["decision"]["FV_anomaly_action"] == "CERTIFIED"
    assert fv_anomaly_ricci["decision"]["Ricci_scalar_sector_dependence"] == "CERTIFIED"
    assert fv_anomaly_ricci["claim_flags"]["SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED"] is False
    assert cubic_weyl["tensor_carriers"]["parity_dimensions"] == {"even": 1, "odd": 1}
    assert cubic_weyl["decision"]["zero_derivative_algebraic_C3_carriers"] == "CERTIFIED_COMPLETE"
    assert cubic_weyl["claim_flags"]["INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED"] is False
    assert third_curvature_weyl["raw_module"]["generic_label_orbit_dimension"] == 12
    assert third_curvature_weyl["quotient_module"]["generic_label_orbit_dimension"] == 11
    assert third_curvature_weyl["claim_flags"]["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"] is False
    assert cpt_kernels["source_fixture"]["status"] == "COEFFICIENT_COMPUTED"
    assert [row["carrier_id"] for row in cpt_kernels["universal_kernels"]] == [
        "I10", "I24", "I25", "I28", "I29"
    ]
    assert cpt_kernels["claim_flags"]["FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED"] is True
    assert cpt_kernels["claim_flags"]["REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED"] is False
    assert cpt_kernels["claim_flags"]["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"] is False
    assert generic_ghost_cpt["CPT_applicability_decision"]["verdict"] == (
        "DIRECT_MINIMAL_CPT_SUBSTITUTION_FOR_THE_GENERIC_GHOST_SECTOR_IS_OBSTRUCTED"
    )
    assert generic_ghost_cpt["claim_flags"]["GENERIC_GHOST_PRINCIPAL_SYMBOL_NONMINIMAL"] is True
    assert generic_ghost_cpt["claim_flags"]["GENERIC_GHOST_HODGE_SPLIT_OBSTRUCTED"] is True
    assert generic_ghost_cpt["claim_flags"]["GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED"] is False
    assert generic_ghost_endo["exact_Endo_split"]["local_perturbation"] == "W=-2 Ric"
    assert generic_ghost_endo["Duhamel_expansion"]["maximum_W_insertions_through_cubic_order"] == 3
    assert generic_ghost_endo["claim_flags"]["GENERIC_NONMINIMAL_GHOST_CPT_REDUCTION_SUPPLIED"] is True
    assert generic_ghost_endo["claim_flags"]["GENERIC_NONMINIMAL_GHOST_INSERTION_TRACES_EVALUATED"] is False
    assert generic_ghost_n3["angular_average"]["coefficients"]["tr_R3"] == {
        "numerator": 503, "denominator": 648
    }
    assert generic_ghost_n3["three_insertion_log_term"]["coefficients"]["tr_R3"] == {
        "numerator": -503, "denominator": 243
    }
    assert generic_ghost_n3["claim_flags"]["GENERIC_GHOST_N3_FULL_MOMENTUM_KERNEL_COMPUTED"] is False
    assert generic_ghost_n3_triangle["projector_sector_expansion"]["sector_count"] == 8
    assert generic_ghost_n3_triangle["projector_sector_expansion"]["total_Wick_rows"] == 20
    assert generic_ghost_n3_triangle["claim_flags"]["GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED"] is True
    assert generic_ghost_n3_triangle["claim_flags"]["GENERIC_GHOST_N3_REPOSITORY_I10_PROJECTION_COMPUTED"] is False
    assert box_r_scheme_conversion["decision"]["repository_BoxR_zero_scheme_conversion"] == "CERTIFIED"
    assert box_r_scheme_conversion["decision"]["nonlocal_R2_form_factor"] == "NOT_COMPUTED"
    assert minimal_kt["spectral_sequence"]["collapse_page"] == "E2"
    assert len(elliptic["principal_symbol_exactness"]) == 4
    assert len(multiplicity["repository_factors"]) == 4
    assert "tau E4" in wz_preflight["local_primitives"]["B_E"]
    print("Paper 12 pure-Weyl one-loop BV anomaly claim map: PASS")


if __name__ == "__main__":
    main()

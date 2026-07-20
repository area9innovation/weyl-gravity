#!/usr/bin/env python3
"""Independent fail-closed verification of the Paper 12 claim map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_MAP = ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json"
COVERAGE = (
    ROOT
    / "paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json"
)
EXPECTED_MANUSCRIPT_SHA256 = (
    "d1a5fccfb25a6656bff1b9dea489e52cd23db2a36ed4301c5db087b3e95bf817"
)
ALL_LOOP_INPUT_SHA256 = (
    "3649925e44d99bea0020f3d1c20a16c54a44f6c9714a3c273c20a6e6d8f84dbc"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(CLAIM_MAP.read_text())
    assert payload["schema"] == "paper-12-pure-weyl-one-loop-bv-anomaly-claim-map-v1"
    assert payload["result_id"] == "PAPER_12_PURE_WEYL_ONE_LOOP_BV_ANOMALY_DRAFT"
    assert payload["lifecycle_state"] == "WRITING_STARTED"
    assert payload["referee_revision"] == {
        "review_snapshot": "EARLIER_TEN_PAGE_SNAPSHOT",
        "requested_revision_status": "IMPLEMENTED_AND_MACHINE_REPLAYED",
        "human_scientific_review_status": "PENDING",
        "theorem_freeze_authorized": False,
    }
    assert payload["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    manuscript = ROOT / payload["manuscript"]
    assert manuscript.is_file()
    assert _sha256(manuscript) == payload["manuscript_sha256"]
    assert payload["manuscript_sha256"] == EXPECTED_MANUSCRIPT_SHA256
    manuscript_text = manuscript.read_text()
    normalized_manuscript = " ".join(manuscript_text.split())
    abstract = manuscript_text.split("\\begin{abstract}", 1)[1].split(
        "\\end{abstract}", 1
    )[0]
    # Freeze the human-readable bridges requested in the focused referee
    # revision. Certificate hashes alone cannot prove that these arguments
    # remain visible to a reader.
    required_manuscript_fragments = [
        "regular Bach-locus chart",
        "The proof is an antifield-number spectral sequence",
        "The complete local determinant ledger is small enough to display",
        "operator & order & rank & statistics",
        "determinant-to-Slavnov bridge",
        "\\dd\\,\\star\\bigl(R\\,\\dd\\omega-\\omega\\,\\dd R\\bigr)",
        "Q_Wh+hQ_W=N_{\\rm quartet}",
        "B_E=\\int\\!\\sqrt g",
        "This restoration has a physical price",
        "The separating functional is simply",
        "same principal symbol, connection, self-adjoint domain",
        "-\\frac{199}{60}=-\\frac c2",
        "Sharp Schatten split and critical Schur residue",
        "Non-Einstein product Schur spectrum and coupled priming",
        "Product-background Schur det3 enclosure",
        "0.3263039",
        "3^{-6}",
        "\\det{}_3(\\mathbf1+K)",
        "\\operatorname{Wres}(K)=",
        "\\operatorname{Wres}(K^2)",
        "\\operatorname{Wres}\\log S_L",
        "Order-two weighted-trace pole and scale row",
        "\\frac{\\dd}{\\dd\\log\\mu}",
        "Exact round-$S^4$ finite Schur benchmark",
        "Exact round-$S^4$ zeta-to-weighted factorization defect",
        "m_Q(A,B)=\\frac53",
        "Generic weight-raised Schur zeta factorization",
        "m_Q^{\\rm wr}(S_L)=-\\frac14\\operatorname{Wres}(K^2)",
        "Generic pole-three relative-simplex IBP reduction",
        "\\lambda(B_{\\rm corner-zero})=0",
        "Complete generic functions for the ten pole-three rows",
        "Complete generic pole-four $I_{29}$ function",
        "\\lambda\\,\\partial_{x_1}J_\\triangle",
        "0.4981635654196290984312532999414818723861192934",
        "-3.9781454856154116274753955548059869205821661933",
        "full primed Green kernel or equivalent spectral measure",
        "Same-gauge physical-Hessian linear-curvature import",
        "Physical plus ghost-$n=3$ carrier assembly",
        "Exact vector-$n=1+n=2$ integration and partial-BV assembly",
        "Algebraic $H_2$ cancellation of the symmetric $M_{14}$ divergence is therefore refuted",
        "action-compatible cyclic pushforward is exactly obstructed",
        "Conditional all-order formal local restoration",
        "repository has not constructed an all-order regulator or subtraction scheme",
        "Regulator and measure status",
        "operatorname{Ber}_{\\rm BV}^{(N)}",
        "Candidate~A's auxiliary-scalaron parent is a scoped classical obstruction",
        "Candidate~B's reducible three-form parent is also a scoped classical obstruction",
        "do not prove a universal no-go for compensator repairs",
    ]
    for fragment in required_manuscript_fragments:
        assert fragment in normalized_manuscript, fragment
    assert "Hadamard" not in abstract
    compiled_pdf = ROOT / payload["compiled_pdf"]
    assert compiled_pdf.is_file()
    assert _sha256(compiled_pdf) == payload["compiled_pdf_sha256"]
    artifacts = payload["publication_artifacts"]
    assert len(artifacts) == 8
    for relative, expected in artifacts.items():
        artifact = ROOT / relative
        assert artifact.is_file(), relative
        assert _sha256(artifact) == expected, relative

    coverage = json.loads(COVERAGE.read_text())
    assert coverage["ir"] == "science-forge-ir-v0"
    nodes = {node["id"]: node for node in coverage["nodes"]}
    paper_id = "sf:paper/12-pure-weyl-one-loop-bv-anomaly"
    result_id = (
        "sf:quantum-weyl.anomalies/result/"
        "TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY"
    )
    claim_id = (
        f"{paper_id}/claim/conditional-all-order-formal-local-restoration"
    )
    assert nodes[paper_id]["body"] == {
        "paper_class": "technical",
        "path": payload["manuscript"],
        "manuscript_sha256": payload["manuscript_sha256"],
    }
    assert nodes[result_id]["body"]["lifecycle"] == "CERTIFIED"
    assert nodes[result_id]["body"]["boundary"] == (
        "changed-tau-adic-compensator-formal-local-under-declared-qap"
    )
    assert nodes[result_id]["body"]["dependency_tags"] == ["LOCAL-ALGEBRAIC"]
    assert nodes[result_id]["body"]["certificate_sha256"] == ALL_LOOP_INPUT_SHA256
    assert nodes[result_id]["body"]["stale"] is False
    assert nodes[result_id]["body"]["superseded"] is False
    materiality = next(
        node for node in coverage["nodes"] if node["kind"] == "materiality"
    )
    assert materiality["body"]["result_id"] == result_id
    assert materiality["body"]["materiality"] == "TECHNICAL"
    assert materiality["body"]["version"] == 1
    assert materiality["body"]["by"] == "quantum-planning-team"
    assert materiality["body"]["native"]["source_schema"] == "materiality-v0"
    assert nodes[claim_id]["body"]["paper"] == paper_id
    assert nodes[claim_id]["body"]["material"] is True
    assert nodes[claim_id]["body"]["asserts_lifecycle"] == "CERTIFIED"
    assert nodes[claim_id]["body"]["cites"] == [result_id]
    edge = next(
        node for node in coverage["nodes"] if node["kind"] == "result_paper_edge"
    )
    assert edge["body"]["from"] == result_id
    assert edge["body"]["to"] == paper_id
    assert edge["body"]["claim"] == claim_id
    assert edge["body"]["edge_kind"] == "PRIMARY_THEOREM"
    assert edge["body"]["stale"] is False
    assert edge["body"]["native"]["source_schema"] == "result-paper-edge-v0"
    regulator_results = {
        "TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION": (
            "20915ec21d0c96534a7091b57ee2c3baf5728526a32d00de83dd75b4b94e7e5f",
            "dr-ms-evanescence-obstruction",
        ),
        "DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT": (
            "28d6821e0774767f991ce79d507dd0059eae2f274c7114c4bec8a07ccc915371",
            "dressed-berezinian-locality-boundary",
        ),
        "DRESSED_EVANESCENT_GEOMETRIC_BV_MODULE_PREFLIGHT": (
            "8685f36ddfbc6a77cdab8048965fb54b575e160a96962651c05a66c167390724",
            "evanescent-full-bv-completion-boundary",
        ),
        "DRESSED_FOUR_DIMENSIONAL_COVARIANT_REGULATOR_PREFLIGHT": (
            "62f53393712a58c25ca26f2318e9feba4fea8efedd2659e4eeb76b7634de2f13",
            "four-dimensional-regulator-receiver-boundary",
        ),
    }
    for name, (digest, claim_suffix) in regulator_results.items():
        rid = f"sf:quantum-weyl.anomalies/result/{name}"
        regulator_claim = f"{paper_id}/claim/{claim_suffix}"
        assert nodes[regulator_claim]["body"]["cites"] == [rid]
        assert nodes[rid]["body"]["certificate_sha256"] == digest
        assert nodes[rid]["body"]["stale"] is False
        materiality_rows = [
            node for node in coverage["nodes"]
            if node["kind"] == "materiality"
            and node["body"]["result_id"] == rid
        ]
        assert len(materiality_rows) == 1
        assert materiality_rows[0]["body"]["materiality"] == "TECHNICAL"
        edge_rows = [
            node for node in coverage["nodes"]
            if node["kind"] == "result_paper_edge"
            and node["body"]["from"] == rid
        ]
        assert len(edge_rows) == 1
        assert edge_rows[0]["body"]["claim"] == regulator_claim
        assert edge_rows[0]["body"]["stale"] is False

    dispositions = payload["theory_dispositions"]
    assert dispositions == {
        "strict_fixed_field_content": "OBSTRUCTED",
        "tau_adic_compensator_extended_local_Euclidean_one_loop": "QME_RESTORED",
        "tau_adic_compensator_extended_formal_all_loop": "CONDITIONAL_QME_RESTORED_UNDER_DECLARED_QAP",
    }
    assert payload["conditional_all_loop_evidence"] == {
        "result_id": "TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY",
        "source_commit": "7fabe987861f1e4facfc2282e7023274df2ddc72",
        "sha256": ALL_LOOP_INPUT_SHA256,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "quantum_action_principle_status": "DECLARED_HYPOTHESIS_NOT_CONSTRUCTED_REGULATOR",
        "claim_boundary": payload["conditional_all_loop_evidence"]["claim_boundary"],
    }
    assert "does not construct the required regulator" in payload[
        "conditional_all_loop_evidence"
    ]["claim_boundary"]
    regulator = payload["regulator_measure_status"]
    assert regulator == {
        "dr_ms_strict_four_dimensional_module": "DECLARED_DR_MS_ARCHITECTURE_OBSTRUCTED_AT_EVANESCENT_CLOSURE",
        "finite_carrier_BV_Berezinian": "exp(-40 tau)",
        "action_independent_continuum_Jacobian": "OBSTRUCTED",
        "common_d_dimensional_AFN0_premodule": "CLASSIFIED",
        "full_d_dimensional_BV_module": "OBSTRUCTED_ACTION_INDEPENDENTLY",
        "four_dimensional_receiver": "CLASSIFIED",
        "actual_four_dimensional_regulator": "NOT_CONSTRUCTED",
        "candidate_A_classical": "OBSTRUCTED",
        "candidate_B_classical": "OBSTRUCTED",
        "candidate_actions_selected": False,
        "candidate_hessians_imported": False,
        "candidate_pair_scope": "TWO_DECLARED_MINIMAL_REPAIRS_ONLY_NOT_UNIVERSAL_COMPENSATOR_NO_GO",
        "scheme_equivalence": "NO_CERTIFIED_SCHEME_EQUIVALENCE_MAP",
    }
    assert payload["classical_candidate_evidence"] == {
        "candidate_A": {
            "result_id": "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1",
            "result_commit": "5c642e2ad14d45f6074b1327c69707b7b9b08f5d",
            "close_commit": "218cd5ad9",
            "sha256": "889c3c2870bb2b28dfe2e4e510526f8644c0b7358884d07fcad351199ae747c6",
            "lifecycle": "OBSTRUCTED",
            "imported_hessian": False,
        },
        "candidate_B": {
            "result_id": "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1",
            "result_commit": "cc0e0036c6acce2bc3d8ba81057031d90a71333a",
            "close_commit": "c7af7b707",
            "sha256": "e8a8aeb97398c3b8812b20118daa56850e32a516bf4e9db15c00b99cec7a8faa",
            "lifecycle": "OBSTRUCTED",
            "imported_hessian": False,
        },
        "universal_compensator_no_go": False,
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
    assert claims["finite_BV_Berezinian_nonunit"] is True
    assert claims["action_independent_continuum_Jacobian_obstructed"] is True
    assert claims["common_d_dimensional_even_AFN0_premodule_classified"] is True
    assert claims["full_d_dimensional_BV_module_action_independently_obstructed"] is True
    assert claims["four_dimensional_covariant_receiver_conditional"] is True
    assert claims["four_dimensional_covariant_regulator_not_instantiated"] is True
    assert claims["DR_MS_and_four_dimensional_schemes_not_identified"] is True
    assert claims["extended_H04_odd_dimension"] == 1
    assert claims["extended_H14_even_dimension"] == 0
    assert claims["extended_H14_odd_dimension"] == 0
    assert claims["extended_formal_all_loop_local_QME_conditionally_restorable"] is True
    assert claims["extended_all_loop_QAP_is_declared_hypothesis"] is True
    assert claims["extended_all_loop_stable_H14_zero"] is True
    assert claims["extended_all_loop_stable_H04_even_dimension"] == 3
    assert claims["extended_all_loop_stable_H04_odd_dimension"] == 1
    assert claims["finite_counterterm_bulk_Q1_ambiguity_rank"] == 2
    assert claims[
        "relative_Einstein_Weyl_action_cyclic_pushforward_obstructed"
    ] is True
    assert claims[
        "relative_Einstein_Weyl_316_unary_cotangent_carrier_retained"
    ] is True
    assert claims[
        "relative_Einstein_Weyl_316_pairing_is_distinct_from_action_pairings"
    ] is True
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
    assert claims["third_curvature_raw_label_dimension"] == 11
    assert claims["third_curvature_4d_quotient_label_dimension"] == 10
    assert claims["third_curvature_functional_relation_rank"] == 1
    assert claims["universal_CPT_third_curvature_kernels_imported"] is True
    assert claims["universal_CPT_source_fixture_status"] == "COEFFICIENT_COMPUTED"
    assert claims["universal_CPT_kernel_box_homogeneities"] == [-1, -2, -2, -3, -4]
    assert claims["same_gauge_physical_Hessian_linear_curvature_imported"] is True
    assert claims["physical_Hessian_linear_source_row_counts"] == {
        "N_lambda": 8,
        "U": 5,
        "V_rho_sigma": 9,
    }
    assert claims["physical_Hessian_scalar_flat_surviving_row_counts"] == {
        "N_lambda": 6,
        "U": 3,
        "V_rho_sigma": 7,
    }
    assert claims["physical_Hessian_repository_normalization"] == (
        "H_repository=(1/2)H_source"
    )
    assert claims["physical_n3_three_linear_insertion_vertex_ready"] is True
    assert claims["physical_H1_formal_adjoint_momentum_vertex_verified"] is True
    assert claims["physical_n3_exact_interior_simplex_fixture_computed"] is True
    assert claims["physical_n3_interior_fixture_Delta"] == {
        "numerator": 104,
        "denominator": 45,
    }
    assert claims["physical_n3_interior_fixture_loop_monomial_count"] == 210
    assert claims["physical_n3_interior_fixture_kernel_without_4pi2"] == {
        "numerator": -3532544138843839,
        "denominator": 319810083840000,
    }
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
    assert claims["product_S2_S2_ghost_Schur_spectral_measure_supplied"] is True
    assert claims["product_S2_S2_ghost_Schur_exceptional_correction"] == "3^-6"
    assert claims["product_S2_S2_ghost_Schur_Wres_K2_fixture"] == {
        "numerator": 28,
        "denominator": 27,
    }
    assert claims["product_S2_S2_ghost_Schur_det3_computed"] is True
    assert claims["product_S2_S2_ghost_Schur_det3_common_prefix"].startswith(
        "0.3263039"
    )
    assert (
        claims["product_S2_S2_ghost_Schur_det3_lower_bound"]
        < claims["product_S2_S2_ghost_Schur_det3_upper_bound"]
    )
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
    assert claims["generic_ghost_n1_n2_Hodge_resolvent_reduction"] is True
    assert claims["generic_ghost_n1_n2_minimal_carrier_count"] == 5
    assert claims["generic_ghost_n1_coefficients"] == [
        {"numerator": 1, "denominator": 1},
        {"numerator": -1, "denominator": 3},
    ]
    assert claims["generic_ghost_n2_coefficients"] == [
        {"numerator": -1, "denominator": 2},
        {"numerator": 1, "denominator": 3},
        {"numerator": -1, "denominator": 18},
    ]
    assert claims["generic_ghost_vector_n1_plus_n2_CPT_projection"] is True
    assert claims["generic_ghost_vector_n1_plus_n2_CPT_formula"] == (
        "6 Gamma1 S1 - 2 Gamma3 S3 - 2 Gamma14 S14"
    )
    assert claims["generic_ghost_vector_n1_n2_integrated_functions"] is True
    assert claims["generic_ghost_vector_n1_n2_nonzero_channel_count"] == 6
    assert claims["generic_ghost_vector_n1_n2_zero_channel_count"] == 5
    assert claims["generic_ghost_vector_n1_n2_no_new_master"] is True
    assert claims["partial_BV_five_carrier_representative_computed"] is True
    assert claims["partial_BV_quotient_dimension"] == 10
    assert claims["partial_BV_I28_relation_status"] == {
        "coordinates": ["ZERO"],
        "scale": "ZERO",
    }
    assert claims["generic_ghost_longitudinal_DW_missing_carriers"] == [
        "N1_LONGITUDINAL_SCALAR",
        "N2_VECTOR_LONGITUDINAL",
        "N2_LONGITUDINAL_LONGITUDINAL",
    ]
    assert claims["generic_ghost_longitudinal_Schur_factorization"] is True
    assert claims["generic_ghost_normalized_Schur_operator"] == (
        "S_L(W)=(2/3)I+(1/3)delta(F+W)^-1 d"
    )
    assert claims["generic_ghost_longitudinal_cubic_coefficients"] == [
        {"numerator": -1, "denominator": 3},
        {"numerator": 1, "denominator": 9},
        {"numerator": -1, "denominator": 81},
    ]
    assert claims["generic_ghost_unspecified_factorization_zeta_anomaly_status"] == (
        "LOCAL_TERM_NOT_EVALUATED"
    )
    assert claims["generic_ghost_4d_trace_class_status"] == (
        "ORDER_MINUS_TWO_DOES_NOT_PROVE_TRACE_CLASS_IN_DIMENSION_FOUR"
    )
    assert claims["generic_ghost_Schur_S3_class"] is True
    assert claims["generic_ghost_modified_Fredholm_order"] == 3
    assert claims["generic_ghost_det3_tail_defined"] is True
    assert claims["generic_ghost_K2_Wodzicki_residue"] == (
        "Wres(K^2)=(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/27"
    )
    assert claims["generic_ghost_K2_scalar_flat_Wodzicki_residue"] == (
        "Wres(K^2)=(4 pi)^-2 integral[2 Ric_mn Ric^mn]/27 when R=0"
    )
    assert claims["generic_ghost_K_Wodzicki_residue"] == (
        "Wres(K)=(4 pi)^-2 integral[R^2+4 Ric_mn Ric^mn]/9"
    )
    assert claims["generic_ghost_log_S_Wodzicki_residue"] == (
        "Wres(log S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54"
    )
    assert claims["generic_ghost_order_two_weighted_trace_scale_coefficient"] == (
        "d/dlog(mu) log Det_(3,R_mu)(S_L)=(4 pi)^-2 integral[5 R^2+22 Ric_mn Ric^mn]/54"
    )
    assert claims["generic_ghost_order_two_weighted_trace_pole_coefficients"][
        "log_S"
    ] == {
        "R2": {"numerator": 5, "denominator": 108},
        "Ric2": {"numerator": 11, "denominator": 54},
    }
    assert claims["round_S4_ghost_Schur_R_Delta_K"]["exact"].startswith("-20/9")
    assert claims["round_S4_ghost_Schur_FP_R_Delta_K2"]["exact"].startswith("-(2/3)")
    assert claims["round_S4_ghost_Schur_low_order_split"]["decimal"].startswith(
        "-4.4763090510350407"
    )
    assert claims["round_S4_ghost_Schur_det3_tail"][
        "certified_common_decimal_prefix"
    ].startswith("0.4981635654196290984312532999414818723861")
    assert claims["round_S4_ghost_Schur_weighted_modified_determinant"][
        "high_precision_decimal"
    ].startswith("-3.9781454856154116274753955548059869205821")
    assert claims["round_S4_ghost_Schur_zeta_weighted_factorization_defect"] == {
        "numerator": 5,
        "denominator": 3,
    }
    assert claims["round_S4_ghost_Schur_zeta_determinant_ratio"].startswith(
        "-2.311478818948744960808728888139320253"
    )
    assert claims["generic_ghost_weight_raised_local_factorization_defect"] == (
        "m_Q^wr(S_L)=-(1/4)Wres(K^2)"
    )
    assert claims["generic_ghost_weight_raised_R2_coefficient"] == {
        "numerator": -1,
        "denominator": 108,
    }
    assert claims["generic_ghost_weight_raised_Ric2_coefficient"] == {
        "numerator": -1,
        "denominator": 54,
    }
    assert claims["round_S4_weight_raised_factorization_defect"] == {
        "numerator": -1,
        "denominator": 3,
    }
    assert claims["round_S4_weight_raised_zeta_determinant_ratio"].startswith(
        "-4.311478818948744960808728888139320253"
    )
    assert claims["factorization_convention_defect_difference"] == {
        "numerator": 2,
        "denominator": 1,
    }
    assert claims["generic_Schur_finite_rows_minimal_missing_input"] == (
        "the full primed Green/resolvent kernel or equivalent complete spectral measure on the selected background"
    )
    assert claims["Berger_WZ_tau_contraction_merge_rejected"] is True
    assert claims["Euler_Wess_Zumino_primitive_displayed"] is True
    boolean_claims = {
        key: value for key, value in claims.items() if isinstance(value, bool)
    }
    assert boolean_claims and all(boolean_claims.values())
    assert payload["explicit_nonclaims"]
    assert all(value is False for value in payload["explicit_nonclaims"].values())
    assert payload["explicit_nonclaims"][
        "generic_ghost_full_Schur_regularized_determinant"
    ] is False
    assert payload["explicit_nonclaims"]["generic_ghost_renormalized_R_K"] is False
    assert payload["explicit_nonclaims"]["generic_ghost_finite_part_R_K2"] is False
    assert payload["explicit_nonclaims"]["full_generic_physical_Hessian"] is False
    assert payload["explicit_nonclaims"]["unconditional_all_loop_extended_QME"] is False
    assert payload["explicit_nonclaims"]["constructed_all_loop_regulator"] is False
    assert payload["explicit_nonclaims"]["convergent_all_loop_expansion"] is False
    assert payload["explicit_nonclaims"]["global_anomalies_excluded"] is False
    assert claims["physical_Hessian_algebraic_H2_imported"] is True
    assert claims["physical_Hessian_H2_source_row_count"] == 18
    assert claims["physical_Hessian_H2_scalar_flat_effective_row_count"] == 9
    assert claims["physical_Hessian_H2_round_algebraic_eigenvalue"] == "+24 K^2 identity"
    assert claims["physical_Hessian_H2_round_commutator_split"] == "+24 K^2-16 K^2=+8 K^2"
    assert claims["physical_n3_full_alpha_polynomial_computed"] is True
    assert claims["physical_n3_five_carrier_projection_computed"] is True
    assert claims["physical_n3_projection_training_fixture_count"] == 28
    assert claims["physical_n3_projection_unseen_fixture_count"] == 2
    assert claims["physical_n3_projection_exact_term_count"] == 5755
    assert claims["physical_n3_isolated_H1_integration_corner_obstructed"] is True
    assert claims["physical_n3_M14_relative_rank_jump"] == 1
    assert claims["physical_n3_M14_total_log_corner_coefficient"] == {
        "numerator": 1,
        "denominator": 2,
    }
    assert claims["physical_n3_M14_nonzero_raw_orientation_count"] == 8
    assert claims["physical_Hessian_operational_H2_polarization_fixture"] is True
    assert claims["physical_Hessian_raw_H1_cubed_log_coefficient"] == {
        "numerator": -1975,
        "denominator": 72,
    }
    assert claims["physical_Hessian_raw_mixed_H1_H2_log_coefficient"] == {
        "numerator": 2704,
        "denominator": 27,
    }
    assert claims["physical_Hessian_raw_combined_log_coefficient"] == {
        "numerator": 15707,
        "denominator": 216,
    }
    assert claims[
        "physical_Hessian_universal_algebraic_H2_cancellation_refuted_by_fixture"
    ] is True
    assert claims["physical_Hessian_fixture_Mellin_minimal_subtraction_fixed"] is True
    assert claims["physical_Hessian_fixture_log_mu2_scale_coefficient"] == {
        "numerator": 15707,
        "denominator": 216,
    }
    assert claims["physical_Hessian_generic_covariant_Volterra_carrier_computed"] is True
    assert claims["physical_Hessian_Volterra_ordered_triangle_cell_count"] == 6
    assert claims["physical_Hessian_Volterra_mixed_contact_cell_count"] == 3
    assert claims["physical_Hessian_generic_contact_endpoint_residues_projected"] is True
    assert claims["physical_Hessian_generic_contact_projection_row_count"] == 33
    assert claims["physical_Hessian_generic_contact_unseen_fixture_count"] == 2
    assert claims["physical_Hessian_symmetric_mixed_boundary_incidence_assembled"] is True
    assert claims["physical_Hessian_symmetric_H2_cancellation_refuted"] is True
    assert claims["physical_Hessian_symmetric_triangle_full_log_coefficient"] == {
        "numerator": -1975,
        "denominator": 72,
    }
    assert claims["physical_Hessian_symmetric_contact_full_log_coefficient"] == {
        "numerator": 2704,
        "denominator": 27,
    }
    assert claims["physical_Hessian_symmetric_combined_log_mu2_coefficient"] == {
        "numerator": 15707,
        "denominator": 216,
    }
    assert claims["physical_Hessian_generic_triangle_corner_residues_computed"] is True
    assert claims["physical_Hessian_generic_triangle_symmetric_rows_replayed"] == 11
    assert claims["physical_Hessian_full_generic_boundary_incidence_assembled"] is True
    assert claims["physical_Hessian_generic_M14_disposed"] is True
    assert claims["physical_Hessian_generic_M14_disposition"] == (
        "NONZERO_SCALE_ROW_RENORMALIZED_BY_COMMON_MELLIN_EXTENSION"
    )
    assert claims["physical_Hessian_generic_contact_finite_rows_computed"] is True
    assert claims["physical_Hessian_generic_contact_finite_row_count"] == 33
    assert claims["physical_Hessian_generic_contact_finite_unseen_fixture_count"] == 2
    assert claims["physical_Hessian_equal_box_contact_finite_value"] == {
        "numerator": 3188,
        "denominator": 27,
    }
    assert claims["physical_Hessian_triangle_six_master_span_complete"] is True
    assert claims["physical_Hessian_triangle_six_master_generic_rank"] == 52
    assert claims["physical_Hessian_triangle_standard_S3_pair_required"] is True
    assert claims["physical_Hessian_triangle_renormalized_new_master_values_computed"] is True
    assert claims["physical_Hessian_triangle_renormalized_master_value_count"] == 3
    assert claims["physical_Hessian_five_carrier_Mellin_MS_form_factors_assembled"] is True
    assert claims["physical_Hessian_form_factor_carrier_count"] == 5
    assert claims["physical_Hessian_form_factor_orientation_channel_count"] == 11
    assert claims["physical_Hessian_form_factor_quotient_dimension"] == 10
    assert claims["physical_plus_ghost_n3_five_carrier_representative_assembled"] is True
    assert claims["physical_plus_ghost_n3_channel_count"] == 11
    assert claims["physical_plus_ghost_n3_quotient_dimension"] == 10
    assert claims["physical_plus_ghost_n3_I28_relation_status"] == "ZERO_COEFFICIENTWISE"
    assert claims["physical_Hessian_finite_C2_normalization"] == "NOT_FIXED"
    assert payload["explicit_nonclaims"][
        "generic_ghost_zeta_multiplicative_anomaly_computed_without_declared_factorization"
    ] is False
    assert (
        payload["next_gate"]["status"]
        == "ANALYTICALLY_CONTINUE_PRODUCT_WEIGHTED_R_K_AND_FINITE_PART_R_K2_THEN_ADD_REMAINING_BV_SECTORS"
    )

    dependencies = {}
    assert claims["generic_ghost_n3_symmetric_point_simplex_integrated"] is True
    assert claims["generic_ghost_n3_symmetric_point"] == {"x1": 1, "x2": 1, "x3": 1}
    assert claims["generic_ghost_n3_symmetric_point_channel_count"] == 11
    assert claims["generic_ghost_n3_symmetric_point_scalar_master"] == (
        "4*Cl2(pi/3)/sqrt(3)"
    )
    assert claims["generic_ghost_n3_generic_Delta_cancellation_count"] == 10
    assert claims["generic_ghost_n3_unique_direct_edge_source"] == ["I10_123"]
    assert claims["generic_ghost_n3_minimum_vertex_integrability_margin"] == 1
    assert claims["generic_ghost_n3_pointwise_I28_relation"] == (
        "I28_123+I28_132+I28_231=0"
    )
    assert claims["generic_ghost_n3_pole3_relative_IBP_channel_count"] == 10
    assert claims["generic_ghost_n3_pole3_master_span_rank"] == 30
    assert claims["generic_ghost_n3_corner_zero_span_rank"] == 26
    assert claims["generic_ghost_n3_corner_zero_augmented_ranks"] == [27] * 10
    assert claims["scalar_triangle_differential_system_computed"] is True
    assert claims["generic_ghost_n3_ten_pole3_integrated_functions"] is True
    assert claims["generic_ghost_n3_pole3_integrated_symmetric_regressions"] == 10
    assert claims["generic_ghost_n3_I29_pole4_reduced"] is True
    assert claims["generic_ghost_n3_I29_full_symbolic_defect"] == "ZERO"
    assert claims["generic_ghost_n3_I29_symmetric_J_coefficient"] == {
        "numerator": -496,
        "denominator": 6561,
    }
    assert claims["generic_ghost_n3_I29_symmetric_rational_term"] == {
        "numerator": 1160,
        "denominator": 6561,
    }
    assert claims["generic_ghost_n3_all_eleven_functions_computed"] is True
    assert claims["physical_Hessian_triangle_six_master_coordinates_computed"] is True
    assert claims["physical_Hessian_triangle_six_master_coordinate_count"] == 66
    assert claims["physical_Hessian_triangle_relative_IBP_boundary_flux_computed"] is True
    assert claims["physical_Hessian_triangle_integrated_channel_count"] == 11
    assert claims["physical_Hessian_triangle_corner_count"] == 33
    assert claims["physical_Hessian_triangle_structured_basis_coordinate_count"] == 77
    assert len(payload["inputs"]) == 76
    for relative, reference in payload["inputs"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert _sha256(path) == reference["sha256"], relative
        value = json.loads(path.read_text())
        assert value["result_id"] == reference["result_id"], relative
        dependencies[reference["result_id"]] = value

    strict = dependencies["REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"]
    diff_mixed = dependencies["AFN0_DIFF_MIXED_MINIMAL_BV_H14"]
    factor_coefficients = dependencies[
        "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH"
    ]
    extended = dependencies["WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY"]
    all_loop = dependencies["TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY"]
    q1 = dependencies["ONE_LOOP_SLAVNOV_Q1_DISPOSITION"]
    relative_cyclic_pushforward = dependencies[
        "RELATIVE_EINSTEIN_WEYL_CYCLIC_PUSHFORWARD_OBSTRUCTION"
    ]
    assert relative_cyclic_pushforward["verdict"][
        "action_compatible_cyclic_pushforward_exists"
    ] is False
    assert relative_cyclic_pushforward["verdict"][
        "canonical_316_unary_cyclic_carrier_exists"
    ] is True
    assert relative_cyclic_pushforward["verdict"][
        "canonical_316_pairing_is_action_pairing"
    ] is False
    gamma1 = dependencies["ANOMALY_INDUCED_NONLOCAL_GAMMA1"]
    flat_tt_log = dependencies["FLAT_TT_LOGARITHMIC_GAMMA1"]
    curvature_squared_log = dependencies["CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1"]
    fv_conformized_log = dependencies["FV_CONFORMIZED_C2_LOG_GAMMA1"]
    fv_anomaly_ricci = dependencies["FV_ANOMALY_ACTION_RICCI_SECTOR"]
    cubic_weyl = dependencies["FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS"]
    third_curvature_weyl = dependencies["FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST"]
    cpt_kernels = dependencies["CPT_UNIVERSAL_THIRD_CURVATURE_KERNELS"]
    physical_hessian_n3_fixture = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE"
    ]
    physical_hessian_h2 = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED"
    ]
    physical_hessian_n3_obstruction = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION"
    ]
    physical_hessian_mixed = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE"
    ]
    physical_hessian_mellin = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW"
    ]
    physical_hessian_volterra = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER"
    ]
    physical_hessian_contacts = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION"
    ]
    physical_hessian_incidence = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_SYMMETRIC_MIXED_BOUNDARY_INCIDENCE"
    ]
    physical_hessian_triangle_residues = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_CORNER_RESIDUES"
    ]
    physical_hessian_full_incidence = dependencies[
        "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE"
    ]
    generic_ghost_cpt = dependencies["GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION"]
    generic_ghost_endo = dependencies["GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION"]
    generic_ghost_n3 = dependencies["GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER"]
    generic_ghost_n3_triangle = dependencies["GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL"]
    scalar_flat_k_ricci = dependencies["SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK"]
    generic_ghost_n3_projection = dependencies["GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION"]
    generic_ghost_n3_relative_ibp = dependencies[
        "GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP"
    ]
    generic_ghost_n1_n2 = dependencies["GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION"]
    generic_ghost_n1_n2_vector = dependencies["GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION"]
    generic_ghost_vector_integrated = dependencies[
        "GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_INTEGRATED_FUNCTIONS"
    ]
    partial_bv = dependencies[
        "GENERIC_BACKGROUND_PARTIAL_BV_THIRD_CURVATURE_FORM_FACTORS"
    ]
    generic_ghost_longitudinal_schur = dependencies["GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION"]
    generic_ghost_schur_schatten = dependencies["GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT"]
    generic_ghost_schur_wodzicki = dependencies["GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE"]
    generic_ghost_schur_scale = dependencies[
        "GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE"
    ]
    round_s4_ghost_schur_finite = dependencies[
        "ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES"
    ]
    round_s4_ghost_schur_zeta = dependencies[
        "ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION"
    ]
    generic_ghost_schur_weight_raised = dependencies[
        "GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION"
    ]
    box_r_scheme_conversion = dependencies["WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION"]
    minimal_kt = dependencies["MINIMAL_BV_KOSZUL_TATE_COLLAPSE"]
    elliptic = dependencies["REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX"]
    multiplicity = dependencies["REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER"]
    wz_preflight = dependencies["WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT"]
    assert strict["qme_disposition"]["status"] == "OBSTRUCTED_STRICT_FIELD_CONTENT"
    assert diff_mixed["claim_flags"]["AFN0_DIFF_MIXED_TOTAL_COMPLEX_COMPLETE"] is True
    assert diff_mixed["claim_flags"]["PURE_DIFF_H14_ZERO"] is True
    assert diff_mixed["claim_flags"]["INDEPENDENT_MIXED_DIFF_WEYL_H14_ZERO"] is True
    assert sum(
        diff_mixed["AFN0_H14"][sector][parity + "_dimension"]
        for sector in ("pure_Diff", "mixed_independent")
        for parity in ("even", "odd")
    ) == claims["pure_Diff_and_mixed_additional_classes"]
    assert factor_coefficients["coefficient_result"]["coefficients"]["C2"] == claims[
        "C2_coefficient"
    ]
    assert factor_coefficients["coefficient_result"]["coefficients"]["E4"] == claims[
        "E4_coefficient"
    ]
    assert strict["coefficients"]["ANOM_OMEGA_C2"] == claims["C2_coefficient"]
    assert strict["coefficients"]["ANOM_OMEGA_E4"] == claims["E4_coefficient"]
    assert extended["H04"]["even_quotient_dimension"] == 3
    assert extended["H14"]["boundary_rank"] == 4
    assert _sha256(
        ROOT
        / "quantum-weyl/anomalies/certificates/TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY.json"
    ) == ALL_LOOP_INPUT_SHA256
    assert all_loop["lifecycle"]["tau_adic_all_loop_formal_local"] == (
        "CONDITIONAL_QME_RESTORED_UNDER_DECLARED_QAP"
    )
    assert all_loop["quantum_action_principle"]["status"] == (
        "DECLARED_HYPOTHESIS_NOT_CONSTRUCTED_REGULATOR"
    )
    assert not any(all_loop["claim_flags"].values())
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
    assert third_curvature_weyl["raw_module"]["generic_label_orbit_dimension"] == 11
    assert third_curvature_weyl["quotient_module"]["generic_label_orbit_dimension"] == 10
    assert third_curvature_weyl["claim_flags"]["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"] is False
    assert cpt_kernels["source_fixture"]["status"] == "COEFFICIENT_COMPUTED"
    assert [row["carrier_id"] for row in cpt_kernels["universal_kernels"]] == [
        "I10", "I24", "I25", "I28", "I29"
    ]
    assert cpt_kernels["claim_flags"]["FIVE_UNIVERSAL_CPT_KERNELS_IMPORTED"] is True
    assert cpt_kernels["claim_flags"]["REPOSITORY_GENERIC_BACKGROUND_TRACE_SUBSTITUTION_SUPPLIED"] is False
    assert cpt_kernels["claim_flags"]["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"] is False
    assert physical_hessian_n3_fixture["exact_interior_fixture"]["Delta"] == claims[
        "physical_n3_interior_fixture_Delta"
    ]
    assert physical_hessian_n3_fixture["exact_interior_fixture"]["loop_trace"][
        "monomial_count"
    ] == claims["physical_n3_interior_fixture_loop_monomial_count"]
    assert physical_hessian_n3_fixture["exact_interior_fixture"][
        "kernel_without_(4pi)^-2"
    ] == claims["physical_n3_interior_fixture_kernel_without_4pi2"]
    assert physical_hessian_n3_fixture["exact_interior_fixture"][
        "formal_adjoint_check"
    ]["completed_vertex_defect_count"] == 0
    assert physical_hessian_n3_fixture["claim_flags"][
        "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"
    ] is False
    assert physical_hessian_h2["claim_flags"][
        "ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED"
    ] is True
    assert physical_hessian_h2["claim_flags"][
        "GAUGE_ORDERING_DOES_NOT_CHANGE_ALGEBRAIC_H2"
    ] is True
    assert physical_hessian_h2["claim_flags"][
        "PHYSICAL_MIXED_H1_H2_TRACE_COMPUTED"
    ] is False
    assert physical_hessian_n3_obstruction["relative_quotient"][
        "symmetric_point_relative_IBP_plus_master_rank"
    ] == 49
    assert physical_hessian_n3_obstruction["relative_quotient"][
        "M14_augmented_rank"
    ] == 50
    assert physical_hessian_n3_obstruction["claim_flags"][
        "H2_CANCELLATION_OF_CORNER_CLASS_PROVED"
    ] is False
    assert physical_hessian_mixed["result_state"] == (
        "RAW_MIXED_PHYSICAL_LOG_COEFFICIENT_NONZERO_SUBTRACTION_REQUIRED"
    )
    assert physical_hessian_mixed["combined_raw_logarithm"]["sum"] == claims[
        "physical_Hessian_raw_combined_log_coefficient"
    ]
    assert physical_hessian_mixed["claim_flags"][
        "RAW_ALGEBRAIC_H2_CANCELLATION_IDENTITY_REFUTED_BY_FIXTURE"
    ] is True
    assert physical_hessian_mixed["claim_flags"]["RENORMALIZED_SUBTRACTION_FIXED"] is False
    assert physical_hessian_mixed["claim_flags"]["PHYSICAL_M14_CORNER_CLASS_DISPOSED"] is False
    assert physical_hessian_mellin["claim_flags"][
        "FIXTURE_MINIMAL_SUBTRACTION_DISTRIBUTION_FIXED"
    ] is True
    assert physical_hessian_mellin["renormalization_scale_row"]["coefficient"] == (
        claims["physical_Hessian_fixture_log_mu2_scale_coefficient"]
    )
    assert physical_hessian_mellin["claim_flags"][
        "GENERIC_COVARIANT_VOLTERRA_LIFT_COMPUTED"
    ] is False
    assert physical_hessian_volterra["claim_flags"][
        "GENERIC_COVARIANT_VOLTERRA_CARRIER_COMPUTED"
    ] is True
    assert physical_hessian_volterra["decorated_carrier"][
        "ordered_triangle_cell_count"
    ] == claims["physical_Hessian_Volterra_ordered_triangle_cell_count"]
    assert physical_hessian_volterra["decorated_carrier"][
        "mixed_contact_cell_count"
    ] == claims["physical_Hessian_Volterra_mixed_contact_cell_count"]
    assert physical_hessian_volterra["claim_flags"][
        "RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED"
    ] is False
    assert physical_hessian_contacts["interpolation"]["row_count"] == 33
    assert physical_hessian_contacts["claim_flags"][
        "ALL_THREE_CONTACT_CELLS_PROJECTED"
    ] is True
    assert physical_hessian_incidence["claim_flags"][
        "SYMMETRIC_POINT_TRIANGLE_CONTACT_INCIDENCE_ASSEMBLED"
    ] is True
    assert physical_hessian_incidence["claim_flags"][
        "SYMMETRIC_POINT_H2_CANCELLATION_OF_M14_REFUTED"
    ] is True
    assert physical_hessian_incidence["M14_disposition"][
        "generic_box_disposition"
    ] == "NOT_COMPUTED"
    assert physical_hessian_triangle_residues["claim_flags"][
        "GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED"
    ] is True
    assert physical_hessian_full_incidence["claim_flags"][
        "FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED"
    ] is True
    assert physical_hessian_full_incidence["claim_flags"][
        "GENERIC_PHYSICAL_M14_DISPOSED"
    ] is True
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
    assert generic_ghost_n3_triangle["claim_flags"]["GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"] is False
    assert scalar_flat_k_ricci["linear_crosswalk"]["identity"] == "K_munu=Ric_munu+O(curvature^2)"
    assert scalar_flat_k_ricci["cubic_order_counting"]["first_replacement_error_order"] == 4
    assert scalar_flat_k_ricci["five_carrier_target"]["carrier_ids"] == [
        "I10", "I24", "I25", "I28", "I29"
    ]
    assert scalar_flat_k_ricci["five_carrier_target"]["projection_status"] == "NOT_COMPUTED"
    assert generic_ghost_n3_projection["quotient_section"]["raw_effective_channel_count"] == 11
    assert generic_ghost_n3_projection["quotient_section"]["quotient_dimension"] == 10
    assert generic_ghost_n3_projection["claim_flags"]["GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"] is True
    assert generic_ghost_n3_projection["claim_flags"]["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"] is False
    assert claims["generic_ghost_n3_five_carrier_parametric_projection"] is True
    assert claims["generic_ghost_n3_projection_raw_channel_count"] == 11
    assert claims["generic_ghost_n3_projection_quotient_dimension"] == 10
    assert claims["generic_ghost_n3_projection_formula_digest"] == generic_ghost_n3_projection["formula_digest"]
    assert len(generic_ghost_n3_relative_ibp["channel_rows"]) == 10
    assert generic_ghost_n3_relative_ibp["rank_ledger"][
        "open_edge_tangent_plus_master_and_targets_rank"
    ] == 30
    assert generic_ghost_n3_relative_ibp["rank_ledger"][
        "corner_zero_tangent_plus_master_rank"
    ] == 26
    assert generic_ghost_n3_relative_ibp["claim_flags"][
        "TEN_POLE3_ROWS_REDUCED_TO_J_AND_TWO_DERIVATIVE_MASTERS"
    ] is True
    assert generic_ghost_n3_relative_ibp["claim_flags"]["I29_POLE4_REDUCED"] is False
    scalar_triangle = dependencies["GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM"]
    assert scalar_triangle["claim_flags"][
        "SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED"
    ] is True
    assert scalar_triangle["claim_flags"]["TWO_LOG_MASTER_REDUCTION_COMPUTED"] is True
    assert len(scalar_triangle["identity_ledger"]["S3_covariance"]) == 6
    assert len(scalar_triangle["identity_ledger"]["mixed_integrability"]) == 3
    assert claims["scalar_triangle_differential_formula_digest"] == scalar_triangle[
        "formula_digest"
    ]
    integrated_pole3 = dependencies[
        "GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS"
    ]
    assert len(integrated_pole3["channel_rows"]) == 10
    assert integrated_pole3["claim_flags"][
        "TEN_POLE3_GENERIC_INTEGRATED_FUNCTIONS_COMPUTED"
    ] is True
    assert integrated_pole3["claim_flags"]["CORNER_ANGULAR_FLUXES_EVALUATED"] is True
    assert integrated_pole3["claim_flags"]["I29_POLE4_REDUCED"] is False
    assert integrated_pole3["identity_ledger"]["symmetric_point_regression_status"] == (
        "ALL_EXACT_MATCH"
    )
    assert claims["generic_ghost_n3_pole3_integrated_formula_digest"] == (
        integrated_pole3["formula_digest"]
    )
    assert generic_ghost_n1_n2["proper_time_to_resolvent"]["resolvent_identity"] == (
        "G_H0=G_F-(1/3)d Delta_0^-2 delta"
    )
    assert generic_ghost_n1_n2["log_determinant_expansion"]["carrier_count"] == 5
    assert generic_ghost_n1_n2["claim_flags"][
        "GENERIC_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION_COMPUTED"
    ] is True
    assert generic_ghost_n1_n2["claim_flags"][
        "GENERIC_GHOST_N1_N2_NONMINIMAL_ARCHITECTURE_CLOSED"
    ] is True
    assert generic_ghost_n1_n2["claim_flags"][
        "GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED"
    ] is False
    assert generic_ghost_n1_n2["claim_flags"][
        "GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED"
    ] is False
    assert generic_ghost_n1_n2_vector["minimal_operator_sign_flip"][
        "surviving_rows"
    ] == [1, 3, 14]
    assert generic_ghost_n1_n2_vector["claim_flags"][
        "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED"
    ] is True
    assert generic_ghost_n1_n2_vector["claim_flags"][
        "ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED"
    ] is False
    assert generic_ghost_vector_integrated["claim_flags"][
        "GENERIC_GHOST_VECTOR_N1_N2_INTEGRATED_FUNCTIONS_COMPUTED"
    ] is True
    assert generic_ghost_vector_integrated["claim_flags"][
        "NO_NEW_TRANSCENDENTAL_MASTER_REQUIRED"
    ] is True
    assert generic_ghost_vector_integrated["identity_ledger"][
        "nonzero_channel_count"
    ] == 6
    assert generic_ghost_vector_integrated["identity_ledger"][
        "zero_channel_count"
    ] == 5
    assert partial_bv["claim_flags"][
        "PARTIAL_BV_FIVE_CARRIER_REPRESENTATIVE_COMPUTED"
    ] is True
    assert partial_bv["claim_flags"]["GHOST_VECTOR_N1_N2_INCLUDED"] is True
    assert partial_bv["claim_flags"]["GHOST_LONGITUDINAL_CARRIERS_INCLUDED"] is False
    assert partial_bv["quotient_ledger"]["quotient_dimension"] == 10
    assert generic_ghost_longitudinal_schur["claim_flags"][
        "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED"
    ] is True
    assert generic_ghost_longitudinal_schur["claim_flags"][
        "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION"
    ] is True
    assert generic_ghost_longitudinal_schur["claim_flags"][
        "GENERIC_LONGITUDINAL_SCHUR_FORM_FACTORS_COMPUTED"
    ] is False
    assert generic_ghost_longitudinal_schur["regularization_boundary"][
        "zeta_multiplicative_anomaly"
    ] == "LOCAL_TERM_NOT_EVALUATED"
    assert generic_ghost_longitudinal_schur["regularization_boundary"][
        "generic_4d_trace_class_status"
    ] == "ORDER_MINUS_TWO_DOES_NOT_PROVE_TRACE_CLASS_IN_DIMENSION_FOUR"
    assert generic_ghost_schur_schatten["sharp_ideal_classification"][
        "minimal_modified_determinant_order"
    ] == 3
    assert generic_ghost_schur_schatten["claim_flags"][
        "SCHUR_CORRECTION_S3_CLASS_PROVED"
    ] is True
    assert generic_ghost_schur_schatten["claim_flags"][
        "CANONICAL_DET3_TAIL_DEFINED"
    ] is True
    assert generic_ghost_schur_schatten["claim_flags"][
        "CRITICAL_K2_WODZICKI_RESIDUE_COMPUTED"
    ] is True
    assert generic_ghost_schur_schatten["claim_flags"][
        "FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED"
    ] is False
    assert generic_ghost_schur_schatten["claim_flags"][
        "WODZICKI_RESIDUE_K_COMPUTED"
    ] is False
    assert generic_ghost_schur_schatten["claim_flags"][
        "ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"
    ] is False
    assert generic_ghost_schur_wodzicki["exact_residues"]["K_Ricci_basis"] == (
        claims["generic_ghost_K_Wodzicki_residue"]
    )
    assert generic_ghost_schur_wodzicki["exact_residues"]["log_S_Ricci_basis"] == (
        claims["generic_ghost_log_S_Wodzicki_residue"]
    )
    assert generic_ghost_schur_wodzicki["claim_flags"][
        "WODZICKI_RESIDUE_K_COMPUTED"
    ] is True
    assert generic_ghost_schur_wodzicki["claim_flags"][
        "WODZICKI_RESIDUE_LOG_S_COMPUTED"
    ] is True
    assert generic_ghost_schur_wodzicki["claim_flags"][
        "ZETA_SCALE_COEFFICIENT_COMPUTED"
    ] is False
    assert generic_ghost_schur_scale["claim_flags"][
        "SCHUR_SCALE_COEFFICIENT_COMPUTED"
    ] is True
    assert generic_ghost_schur_scale["Schur_determinant_scale_row"][
        "Ricci_basis"
    ] == claims["generic_ghost_order_two_weighted_trace_scale_coefficient"]
    assert generic_ghost_schur_scale["exact_conversion"][
        "pole_coefficients_Ricci_basis"
    ] == claims["generic_ghost_order_two_weighted_trace_pole_coefficients"]
    assert generic_ghost_schur_scale["claim_flags"][
        "REFERENCE_FINITE_R_K_COMPUTED"
    ] is False
    assert round_s4_ghost_schur_finite["exact_finite_rows"][
        "Delta_weighted_finite_rows"
    ]["R_Delta_K"] == claims["round_S4_ghost_Schur_R_Delta_K"]
    assert round_s4_ghost_schur_finite["exact_finite_rows"][
        "Delta_weighted_finite_rows"
    ]["FP_R_Delta_K2"] == claims["round_S4_ghost_Schur_FP_R_Delta_K2"]
    assert round_s4_ghost_schur_finite["exact_finite_rows"][
        "canonical_det3_tail"
    ] == claims["round_S4_ghost_Schur_det3_tail"]
    assert round_s4_ghost_schur_finite["exact_finite_rows"][
        "full_modified_determinant"
    ] == claims["round_S4_ghost_Schur_weighted_modified_determinant"]
    assert round_s4_ghost_schur_finite["claim_flags"][
        "FULL_ROUND_S4_DET3_TAIL_COMPUTED"
    ] is True
    assert round_s4_ghost_schur_finite["claim_flags"][
        "GENERIC_BACKGROUND_R_K_COMPUTED"
    ] is False
    assert round_s4_ghost_schur_zeta["local_residue_derivation"][
        "exact_factorization_defect"
    ] == claims["round_S4_ghost_Schur_zeta_weighted_factorization_defect"]
    assert round_s4_ghost_schur_zeta["factorization_result"][
        "zeta_determinant_ratio_decimal"
    ] == claims["round_S4_ghost_Schur_zeta_determinant_ratio"]
    assert round_s4_ghost_schur_zeta["claim_flags"][
        "GENERIC_NONCOMMUTING_ZETA_FACTORIZATION_DEFECT_COMPUTED"
    ] is False
    assert generic_ghost_schur_weight_raised["generic_local_result"][
        "operator_formula"
    ] == claims["generic_ghost_weight_raised_local_factorization_defect"]
    assert generic_ghost_schur_weight_raised["generic_local_result"][
        "coefficient_of_(4pi)^-2_integral_R2"
    ] == claims["generic_ghost_weight_raised_R2_coefficient"]
    assert generic_ghost_schur_weight_raised["round_S4_crosscheck"][
        "weight_raised_defect"
    ] == claims["round_S4_weight_raised_factorization_defect"]
    assert generic_ghost_schur_weight_raised["claim_flags"][
        "GENERIC_BACKGROUND_FINITE_SCHUR_ROWS_COMPUTED"
    ] is False
    assert claims["generic_ghost_vector_n1_plus_n2_formula_digest"] == (
        generic_ghost_n1_n2_vector["formula_digest"]
    )
    assert box_r_scheme_conversion["decision"]["repository_BoxR_zero_scheme_conversion"] == "CERTIFIED"
    assert box_r_scheme_conversion["decision"]["nonlocal_R2_form_factor"] == "NOT_COMPUTED"
    assert minimal_kt["spectral_sequence"]["collapse_page"] == "E2"
    assert len(elliptic["principal_symbol_exactness"]) == 4
    assert len(multiplicity["repository_factors"]) == 4
    assert "tau E4" in wz_preflight["local_primitives"]["B_E"]
    print("Paper 12 pure-Weyl one-loop BV anomaly claim map: PASS")


if __name__ == "__main__":
    main()

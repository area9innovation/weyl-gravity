#!/usr/bin/env python3
"""Fail-closed verification of the current Paper 11 representative theorem."""

from __future__ import annotations

import copy
import hashlib
import gzip
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CLAIM_MAP = ROOT / "paper/11-gravity-light-cyclic-causal-ell3-claim-map.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_current_deformation_disposition(payload: dict) -> None:
    """Reject the three stale Paper 11 order-two promotions explicitly."""
    crosswalk = {row["claim_id"]: row for row in payload["claim_crosswalk"]}
    claims = payload["certified_claims"]
    assert crosswalk["P11-C5"]["status"] == "SUPERSEDED"
    assert crosswalk["P11-C6"]["status"] == "OPEN"
    assert claims["full_BV_order_two_filtered_removal_obstructed"] is False
    assert claims["full_BV_unremovable_within_declared_filtered_cyclic_class"] is False
    assert claims["complete_bounded_cyclic_class_decided"] is False


def _assert_stale_claim_mutations_rejected(payload: dict) -> None:
    mutations = (
        lambda mutant: mutant["certified_claims"].__setitem__(
            "full_BV_order_two_filtered_removal_obstructed", True
        ),
        lambda mutant: next(
            row for row in mutant["claim_crosswalk"] if row["claim_id"] == "P11-C5"
        ).__setitem__("status", "CURRENT"),
        lambda mutant: next(
            row for row in mutant["claim_crosswalk"] if row["claim_id"] == "P11-C6"
        ).__setitem__("status", "CURRENT"),
    )
    for mutate in mutations:
        mutant = copy.deepcopy(payload)
        mutate(mutant)
        try:
            _assert_current_deformation_disposition(mutant)
        except AssertionError:
            continue
        raise AssertionError("stale Paper 11 deformation claim mutation was accepted")


def main() -> None:
    payload = json.loads(CLAIM_MAP.read_text(encoding="utf-8"))
    assert payload["schema"] == "paper-11-gravity-light-cyclic-causal-ell3-claim-map-v1"
    assert payload["result_id"] == "PAPER_11_GRAVITY_LIGHT_CYCLIC_CAUSAL_ELL3_REPRESENTATIVE_THEOREM_FROZEN"
    assert (
        payload["result_state"]
        == "FROZEN_SDR_REPRESENTATIVE_THEOREM_FROZEN_BOUNDED_CYCLIC_CLASS_OPEN"
    )
    assert payload["lifecycle_state"] == "THEOREM_FROZEN"
    assert payload["freeze_disposition"]["mathematical_claims"] == "THEOREM_FROZEN"
    assert payload["freeze_disposition"]["additional_internal_major_calculation_required_before_circulation"] is False
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    assert payload["paper_scope"]["operator_coefficient_field"] == "Q(sqrt(10))"
    assert (
        payload["paper_scope"]["deformation_coefficient_field"]
        == "Q(sqrt(2),sqrt(10))"
    )
    crosswalk = {row["claim_id"]: row for row in payload["claim_crosswalk"]}
    assert set(crosswalk) == {f"P11-C{index}" for index in range(1, 11)}
    assert crosswalk["P11-C1"]["status"] == "CURRENT"
    assert crosswalk["P11-C5"]["status"] == "SUPERSEDED"
    assert crosswalk["P11-C6"]["status"] == "OPEN"
    assert crosswalk["P11-C8"]["status"] == "CURRENT"
    assert crosswalk["P11-C9"]["status"] == "OPEN"
    assert crosswalk["P11-C10"]["status"] == "ABSENT_FROM_PAPER"
    allowed_statuses = {"CURRENT", "NARROWED", "SUPERSEDED", "OPEN", "ABSENT_FROM_PAPER"}
    assert all(row["status"] in allowed_statuses for row in crosswalk.values())
    assert payload["coverage"]["human_materiality_review"] == "COMPLETE"
    assert payload["coverage"]["all_material_imports_have_result_to_paper_edges"] is True
    assert payload["coverage"]["uncovered_material_results"] == []
    edges = payload["result_to_paper_edges"]
    assert len(edges) == 6
    assert {edge["materiality"] for edge in edges} <= {"HEADLINE", "TECHNICAL", "NEGATIVE_RESULT"}
    assert {claim for edge in edges for claim in edge["claim_ids"]} >= {
        "P11-C3", "P11-C4", "P11-C5", "P11-C6", "P11-C7", "P11-C8", "P11-C9", "P11-C10"
    }

    claims = payload["certified_claims"]
    required_true = {
        "theorem_frozen_at_declared_scope",
        "typed_cyclic_64_to_36_contraction",
        "formal_cyclic_transfer_theorem_separated_from_sparse_implementation_audit",
        "human_readable_full_and_retained_carrier_map_printed",
        "full_row_38_identified_as_Theta_star",
        "row_38_contractible_clock_doublet_support_displayed",
        "exact_cyclic_SDR_adjoint_relations_displayed",
        "exact_witness_inclusion_columns_printed",
        "retained_mixed_ell2_nonzero",
        "retained_mixed_ell3_nonzero",
        "retained_exchange_zero_after_exact_projection",
        "mixed_exchange_claim_scoped_to_frozen_SDR",
        "retained_arity_three_identity_all_36_rows",
        "degree_zero_lowered_cyclicity_independently_replayed",
        "pairing_weight_mutation_rejected",
        "full_retained_BV_ell3_cyclicity_independently_replayed",
        "degree_two_polarization_mutation_rejected",
        "coupled_K_Berger_cyclic_causal_Cartan_through_arity_three",
        "causal_complete_to_retained_bridge_displayed",
        "canonical_same_bundle_retained_36_branch_projector_obstructed",
        "retained_46_STF2_graph_carrier_constructed",
        "retained_46_cyclic_SDR_to_36",
        "retained_46_contractible_complement",
        "retained_46_Schur_complement_equals_A10",
        "retained_46_exact_graph_shear_exported",
        "retained_46_projector_solver_contract_frozen",
        "retained_46_principal_filtered_module_certified",
        "retained_46_principal_direct_sum_anchor_obstructed",
        "retained_46_V2_filtered_descent_computed",
        "retained_46_physical_filtered_lift_obstructed",
        "retained_46_subprincipal_verdict_landed",
        "constant_field_physical_cyclic_redefinition_screen_computed",
        "first_jet_physical_cyclic_redefinition_screen_computed",
        "full_BV_zero_first_jet_dual_screen_computed",
        "zero_jet_full_BV_ghost_shear_trivialization_computed",
        "physical_action_order_two_trivialization_computed",
        "second_jet_witness_invalidation_computed",
        "cyclic_branch_extension_obstruction_certified",
    }
    assert all(claims[name] is True for name in required_true)
    assert claims["retained_mixed_ell2_coefficient_count"] == 1_474
    assert claims["retained_mixed_ell3_coefficient_count"] == 25_950
    assert claims["degree_zero_lowered_coefficient_count"] == 25_662
    assert claims["degree_zero_lowered_cyclicity_defect_count"] == 0
    assert claims["pairing_weight_mutation_defect_count"] == 17_108
    assert claims["ghost_antifield_completion_coefficient_count"] == 288
    assert claims["ghost_antifield_positive_transpose_sign_count"] == 120
    assert claims["ghost_antifield_negative_transpose_sign_count"] == 168
    assert claims["full_BV_cyclicity_defect_count"] == 0
    assert claims["degree_two_polarization_mutation_defect_count"] == 132
    assert claims["gravity_output_two_Maxwell_input_count"] == 7_614
    assert claims["Maxwell_output_one_Maxwell_input_count"] == 18_336
    assert claims["exact_witness_inclusion_column_coefficient_count"] == 106
    assert claims["projector_obstruction_nondivisible_remainder_count"] == 92
    assert claims["projector_obstruction_minimum_additional_BV_rows"] == 4
    assert claims["smallest_natural_support_local_candidate_rank"] == 46
    assert claims["retained_46_total_rows"] == 46
    assert claims["retained_46_degree_ranks"] == [4, 19, 19, 4]
    assert claims["retained_46_projector_independent_graph_coefficient_count"] == 225
    assert claims["retained_46_principal_anchor_normalized_evaluation"] == "1"
    assert claims["retained_46_full_null_symbol_cohomology_dimensions"] == [0, 6, 6, 0]
    assert claims["retained_46_physical_helicity_projective_rank"] == 2
    assert claims["retained_46_generalized_wave_module_rank"] == 4
    assert claims["retained_46_physical_pairing_nondegenerate"] is True
    assert claims["retained_46_subprincipal_normalized_evaluation"] == ["1", "0"]
    assert claims["retained_46_cross_polarization_lift_coefficient"] == "71/40"
    assert claims["constant_field_mixed_quartic_dimension"] == 550
    assert claims["constant_field_coboundary_rank"] == 550
    assert claims["constant_field_coboundary_cokernel_dimension"] == 0
    assert claims["constant_field_target_nonzero_coordinate_count"] == 63
    assert claims["constant_field_explicit_F3_primitive_coefficient_count"] == 51
    assert claims["first_jet_dimension_per_axis"] == 1330
    assert claims["first_jet_positive_map_rank"] == 1327
    assert claims["first_jet_positive_map_cokernel_dimension"] == 3
    assert claims["first_jet_Schur_rank"] == 557
    assert claims["first_jet_positive_primitive_counts"] == [43, 94, 95, 108]
    assert claims["full_BV_filtered_obstruction_page"] == 1
    assert claims["full_BV_filtered_obstruction_support_count"] == 22
    assert claims["full_BV_zero_page_columns_checked"] == 5_984
    assert claims["full_BV_first_page_columns_checked_per_axis"] == 14_998
    assert claims["full_BV_first_page_defects_per_axis"] == [0, 0, 0, 0]
    assert claims["physical_action_order_two_primitive_coefficient_count"] == 4_276
    assert claims["second_jet_counterexample_cotangent_component_count"] == 5
    assert claims["second_jet_counterexample_page_one_term_count"] == 252
    assert claims["second_jet_counterexample_pairing"] == "755/9"
    assert claims["cyclic_branch_extension_normalized_evaluation"] == ["1", "0"]
    assert claims["full_BV_order_two_filtered_removal_obstructed"] is False
    assert claims["full_BV_unremovable_within_declared_filtered_cyclic_class"] is False
    assert claims["complete_bounded_cyclic_class_decided"] is False
    _assert_current_deformation_disposition(payload)
    _assert_stale_claim_mutations_rejected(payload)

    witnesses = payload["explicit_nonzero_witnesses"]
    assert witnesses["gravity_equation_output"] == {
        "output": "h_hat_star_00",
        "inputs": ["h_hat_13", "A_1", "A_3"],
        "PBW_derivative_word": "zero_in_every_input_slot",
        "coefficient": "+1",
        "output_degree": 1,
        "input_degrees": [0, 0, 0],
        "pairing_partner": "h_hat_00",
    }
    assert witnesses["Maxwell_equation_output"] == {
        "output": "A_plus_1",
        "inputs": ["h_hat_01", "h_hat_03", "A_3"],
        "PBW_derivative_word": "zero_in_every_input_slot",
        "coefficient": "-1",
        "output_degree": 1,
        "input_degrees": [0, 0, 0],
        "pairing_partner": "A_1",
    }

    nonclaims = payload["explicit_nonclaims"]
    assert nonclaims
    assert all(value is False for value in nonclaims.values())
    assert (
        payload["next_gate"]["status"]
        == "RANK46_SUBPRINCIPAL_PHYSICAL_LIFT_OBSTRUCTED_ENLARGEMENT_OR_UNSPLIT_REQUIRED"
    )
    assert (
        payload["next_gate"]["carrier"]
        == "BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1"
    )
    assert (
        payload["next_gate"]["solver_contract"]
        == "BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_SOLVER_CONTRACT_V1"
    )
    assert (
        payload["next_gate"]["principal_anchor"]
        == "BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1"
    )
    assert (
        payload["next_gate"]["physical_helicity_filtered_quotient"]
        == "BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1"
    )
    assert (
        payload["next_gate"]["subprincipal_obstruction"]
        == "BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1"
    )
    assert (
        payload["next_gate"]["constant_field_redefinition"]
        == "BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1"
    )
    assert (
        payload["next_gate"]["deformation_required_input"]
        == "COMPLETE_COUPLED_FULL_BV_ZERO_FIRST_SECOND_JET_SOLVE_OR_REPLACEMENT_COKERNEL"
    )
    assert payload["next_gate"]["filtered_deformation_status"] == "COMPLETE_BOUNDED_CYCLIC_CLASS_OPEN_AFTER_SECOND_JET_WITNESS_INVALIDATION"
    assert payload["next_gate"]["historical_filtered_screen"] == "BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1"
    assert payload["next_gate"]["filtered_disposition"] == "BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1"
    assert payload["next_gate"]["physical_order_two_primitive"] == "BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1"
    assert payload["next_gate"]["branch_extension_obstruction"] == "BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1"
    assert payload["next_gate"]["first_jet_redefinition"] == "BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1"
    assert (
        payload["next_gate"]["required_input"]
        == "UNSPLIT_RETAINED_COMPLEX_OR_NONCONTRACTIBLE_FILTERED_ENLARGEMENT"
    )

    for relative, expected in payload["inputs"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert _sha256(path) == expected, relative

    full_BV = json.loads(
        (
            ROOT
            / "quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY.json"
        ).read_text(encoding="utf-8")
    )
    full_diagnostics = full_BV["exact_replay"]["diagnostics"]
    assert full_BV["claim_flags"][
        "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED"
    ] is True
    assert full_diagnostics["ghost_antifield_completion_coefficient_count"] == 288
    assert full_diagnostics["full_BV_cyclicity_defect_count"] == 0
    assert (
        full_diagnostics[
            "omitted_degree_two_polarization_mutation_defect_count"
        ]
        == 132
    )

    legacy_carrier = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
        ).read_text(encoding="utf-8")
    )
    full_rows = {
        row["index"]: (row["row_id"], row["degree"])
        for row in legacy_carrier["full_complex"]["component_rows"]
    }
    retained_rows = {
        row["index"]: (row["row_id"], row["degree"])
        for row in legacy_carrier["retained_complex"]["component_rows"]
    }
    assert full_rows[38] == ("Theta_star", 1)
    assert full_rows[52] == ("tau_star", 2)
    assert retained_rows[13] == ("h_hat_star_00", 1)
    assert retained_rows[32] == ("A_plus_1", 1)

    contraction = legacy_carrier["contraction"]
    assert len(contraction["iota_36_to_64"]["entries"]) == 86
    assert len(contraction["pi_64_to_36"]["entries"]) == 86
    assert len(contraction["S_64"]["entries"]) == 19
    assert not any(
        target in {38, 52}
        for target, _source, _operator in contraction["iota_36_to_64"]["entries"]
    )
    assert not any(
        source in {38, 52}
        for _target, source, _operator in contraction["pi_64_to_36"]["entries"]
    )
    assert [3, 16, [[[0, 0, 0, 0], "1"]]] in contraction["S_64"]["entries"]
    assert [38, 52, [[[0, 0, 0, 0], "-1"]]] in contraction["S_64"]["entries"]
    checks = legacy_carrier["exact_checks"]
    assert checks["homotopy_square_zero"] is True
    assert checks["homotopy_inclusion_zero"] is True
    assert checks["projection_homotopy_zero"] is True

    from d_quotient_classical.backreacted_clock.berger_portable_coupled_typed_pairing_sdr import (
        _adjoint,
        _is_zero,
        _multiply,
        _subtract,
        exact_matrices,
    )

    typed_matrices = exact_matrices(legacy_carrier)
    assert _is_zero(
        _subtract(
            _multiply(_adjoint(typed_matrices["iota"]), typed_matrices["omega64"]),
            _multiply(typed_matrices["omega36"], typed_matrices["projection"]),
        )
    )
    typed_checks = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
        ).read_text(encoding="utf-8")
    )["exact_checks"]
    assert typed_checks["typed_pairing_induced_by_iota"] is True
    assert typed_checks["homotopy_typed_cyclic"] is True

    projector_obstruction = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        projector_obstruction["result_state"]
        == "NORMALIZED_LOCAL_PROJECTOR_OBSTRUCTION_CANONICAL_SAME_BUNDLE_SCOPE"
    )
    assert (
        projector_obstruction["exact_endpoint_normal_form"][
            "degree_two_nondivisible_entries"
        ]
        == 92
    )
    assert (
        projector_obstruction["smallest_carrier_enlargement_required"][
            "exact_symbol_lower_bound"
        ]["minimum_additional_BV_rows"]
        == 4
    )
    assert (
        projector_obstruction["smallest_carrier_enlargement_required"][
            "smallest_natural_support_local_candidate"
        ]["candidate_retained_rank"]
        == 46
    )

    rank46 = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert rank46["result_state"] == "CERTIFIED_CYCLIC_GRAPH_CARRIER_PROJECTOR_OPEN"
    assert rank46["dependency_tags"] == ["LOCAL-ALGEBRAIC"]
    assert rank46["carrier"]["total_rows"] == 46
    assert rank46["carrier"]["degree_ranks"] == {
        "-1": 4,
        "0": 19,
        "1": 19,
        "2": 4,
    }
    assert all(rank46["exact_checks"].values())
    assert rank46["flags"]["CYCLIC_GRAPH_SDR_46_TO_36"] is True
    for flag in (
        "CANONICAL_BRANCH_PROJECTOR_CERTIFIED",
        "ELL3_BRANCH_MIXING_AUTHORIZED",
        "Q2_Q3_LIFT_MATERIALIZED",
        "K_BERGER_EQUIVARIANCE_CERTIFIED",
        "LORENTZIAN_CAUSAL",
        "QUANTUM_CLAIM",
    ):
        assert rank46["flags"][flag] is False
    assert (
        rank46["next_gate"]
        == "BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1"
    )
    for artifact in ("graph_shear_U_46", "graph_shear_U_46_inverse"):
        assert rank46["artifacts"][artifact]["shape"] == [46, 46]
    assert rank46["exact_checks"]["graph_shear_inverse"] is True
    assert rank46["exact_checks"]["graph_shear_typed_cyclic"] is True

    solver_contract = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_SOLVER_CONTRACT_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        solver_contract["result_state"]
        == "SOLVER_CONTRACT_FROZEN_PROJECTOR_VERDICT_NOT_RUN"
    )
    assert solver_contract["claim_flags"]["SOLVER_CONTRACT_FROZEN"] is True
    assert solver_contract["claim_flags"]["BRANCH_PROJECTOR_ACCEPTED"] is False
    assert (
        solver_contract["declared_graph_ansatz"][
            "independent_coefficient_count_over_Q_sqrt10"
        ]
        == 225
    )

    principal_anchor = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        principal_anchor["result_state"]
        == "PRINCIPAL_DIRECT_SUM_ANCHOR_OBSTRUCTED_FILTERED_SUBPRINCIPAL_GATE_REQUIRED"
    )
    assert principal_anchor["idempotent_audit"]["solutions_a_b"] == [
        ["0", "0"],
        ["1", "0"],
    ]
    assert (
        principal_anchor["normalized_obstruction_witness"]["normalized_evaluation"]
        == "1"
    )
    assert principal_anchor["claim_flags"]["FULL_RANK_46_PROJECTOR_OBSTRUCTED"] is False
    assert principal_anchor["claim_flags"]["SUBPRINCIPAL_ANCHOR_REQUIRED"] is True

    physical_quotient = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        physical_quotient["result_state"]
        == "PHYSICAL_HELICITY_PROJECTIVE_MODULE_CERTIFIED_V2_FILTERED_DESCENT_OPEN"
    )
    assert physical_quotient["null_cone_chart"]["projective_rank"] == 2
    assert physical_quotient["null_cone_chart"]["global_two_column_frame_asserted"] is False
    assert physical_quotient["full_Berger_null_symbol_cohomology"]["cohomology_dimensions"] == [0, 6, 6, 0]
    assert physical_quotient["filtered_principal_module"]["generalized_wave_rank_over_Q_sqrt10"] == 4
    assert physical_quotient["claim_flags"]["V2_FILTERED_DESCENT_COMPUTED"] is False
    assert physical_quotient["claim_flags"]["ELL3_BRANCH_MIXING_AUTHORIZED"] is False

    subprincipal = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert subprincipal["result_state"] == "SUBPRINCIPAL_PHYSICAL_MODULE_LIFT_OBSTRUCTED_AT_STANDARD_NULL_FIBRE"
    assert subprincipal["normalized_obstruction"]["normalized_evaluation_on_physical_columns"] == [["1", "0"]]
    assert subprincipal["normalized_obstruction"]["cross_polarization_lifts"] is True
    assert subprincipal["normalized_obstruction"]["cross_physical_equation_coefficient"] == "71/40"
    assert subprincipal["claim_flags"]["V2_FILTERED_DESCENT_COMPUTED"] is True
    assert subprincipal["claim_flags"]["RANK46_PHYSICAL_FILTERED_LIFT_OBSTRUCTED"] is True
    assert subprincipal["claim_flags"]["GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO"] is False
    assert subprincipal["claim_flags"]["ELL3_BRANCH_MIXING_AUTHORIZED"] is False

    constant_redefinition = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        constant_redefinition["result_state"]
        == "CONSTANT_FIELD_PHYSICAL_MIXED_QUARTIC_TRIVIALIZED_FULL_BV_AND_POSITIVE_JET_OPEN"
    )
    constant_verdict = constant_redefinition["exact_verdict"]
    assert constant_verdict["coboundary_matrix_shape"] == [550, 2690]
    assert constant_verdict["coboundary_rank"] == 550
    assert constant_verdict["cokernel_dimension"] == 0
    assert constant_verdict["primitive_nonzero_count"] == 51
    assert constant_verdict["primitive_arity_counts"] == {"F2": 0, "F3": 51}
    assert constant_redefinition["claim_flags"]["CYCLIC_DEFORMATION_CLASS_DECIDED"] is False
    assert constant_redefinition["claim_flags"]["FULL_JET_BOUNDED_REDEFINITION_COMPUTED"] is False

    first_jet = json.loads(
        (ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1.json").read_text(encoding="utf-8")
    )
    assert first_jet["result_state"] == "FIRST_JET_PHYSICAL_MIXED_QUARTIC_TRIVIALIZED_FULL_BV_AND_ORDER2_OPEN"
    assert first_jet["coupled_schur_problem"]["C_rank"] == 1327
    assert first_jet["coupled_schur_problem"]["Schur_rank"] == 557
    assert first_jet["exact_primitive"]["positive_jet_nonzero_by_axis"] == [43, 94, 95, 108]
    assert first_jet["claim_flags"]["FULL_BV_REDEFINITION_MATCHED"] is False
    assert first_jet["claim_flags"]["JET_ORDER_TWO_OR_HIGHER_COMPUTED"] is False

    filtered_obstruction = json.loads(
        (ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1.json").read_text(encoding="utf-8")
    )
    assert filtered_obstruction["result_state"] == "FILTERED_CYCLIC_FULL_BV_REMOVAL_OBSTRUCTED_AT_FIRST_ASSOCIATED_GRADED_PAGE"
    assert filtered_obstruction["lifecycle_status"] == "OBSTRUCTED"
    assert filtered_obstruction["filtration"]["target_bound"] == 2
    assert filtered_obstruction["filtration"]["obstruction_page"] == 1
    witness = filtered_obstruction["obstruction_witness"]
    assert witness["support_count"] == 22
    replay = witness["exhaustive_transpose_replay"]
    assert replay["zero_label_columns_checked"] == 5_984
    assert replay["first_label_columns_checked_per_axis"] == 14_998
    assert replay["zero_column_defects"] == 0
    assert replay["first_column_defects_per_axis"] == [0, 0, 0, 0]
    assert replay["target_pairing"] == "1"
    assert filtered_obstruction["claim_flags"]["ORDER_TWO_FILTERED_REMOVAL_OBSTRUCTED"] is True
    assert filtered_obstruction["claim_flags"]["SDR_INDEPENDENT_DEFORMATION_CLASS"] is False
    assert filtered_obstruction["claim_flags"]["RESIDUAL_COHOMOLOGY_OPERATION_NONZERO"] is False

    disposition = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert disposition["result_state"] == "ORDER_TWO_OBSTRUCTION_WITHDRAWN_COMPLETE_BOUNDED_CYCLIC_CLASS_OPEN"
    assert disposition["exact_counterexample"]["cotangent_component_count"] == 5
    assert disposition["exact_counterexample"]["native_page_one_term_count"] == 252
    assert disposition["exact_counterexample"]["old_witness_pairing"] == "755/9"
    assert disposition["claim_flags"]["ORDER_TWO_FILTERED_REMOVAL_OBSTRUCTED"] is False
    assert disposition["claim_flags"]["COMPLETE_ORDER_TWO_TRIVIALIZATION_EXISTS"] is False
    assert disposition["claim_flags"]["COMPLETE_ORDER_TWO_CLASS_NONZERO"] is False

    ghost_shear = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_ZERO_JET_GHOST_SHEAR_COMPLETION_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert ghost_shear["claim_flags"]["ZERO_JET_FULL_BV_TRIVIALIZATION_EXISTS"] is True
    assert ghost_shear["primitive_replay"]["primitive_nonzero_coefficients"] == 67

    physical_order_two = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert physical_order_two["status"] == "PHYSICAL_ACTION_ORDER_TWO_TRIVIALIZED"
    assert physical_order_two["claim_flags"]["PHYSICAL_ACTION_ORDER_TWO_TRIVIALIZATION_COMPUTED"] is True
    assert physical_order_two["claim_flags"]["FULL_BV_POSITIVE_JET_REDEFINITION_MATCHED"] is False

    branch_extension = json.loads(
        (
            ROOT
            / "d_quotient_classical/certificates/BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json"
        ).read_text(encoding="utf-8")
    )
    assert branch_extension["claim_flags"]["FIRST_EXTENSION_OBSTRUCTION_CLASS_CERTIFIED"] is True
    assert branch_extension["claim_flags"]["CYCLIC_L_INFINITY_BRANCH_SPLIT_EXISTS"] is False
    assert branch_extension["claim_flags"]["MODE_PAIR_SOURCE_TABLE_AUTHORIZED"] is False
    assert branch_extension["first_obstruction_class"]["normalized_evaluation"] == [["1", "0"]]

    observer_gate = json.loads(
        (
            ROOT
            / "closed_universe_observers/certificates/BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE.json"
        ).read_text(encoding="utf-8")
    )
    assert observer_gate["flags"]["INTERACTING_OBSERVER_DEFORMATION_CONSTRUCTED"] is False
    assert observer_gate["flags"]["EXTENDED_RETARDED_GREEN_CERTIFIED"] is False

    common_action = json.loads(
        (
            ROOT
            / "closed_universe_observers/certificates/BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION.json"
        ).read_text(encoding="utf-8")
    )
    assert "No such carrier exists" in common_action["claim_boundary"]

    from generate_11_witness_inclusion_columns import (
        OUTPUT as WITNESS_COLUMNS,
        build as build_witness_columns,
    )

    assert WITNESS_COLUMNS.read_text(encoding="utf-8") == build_witness_columns()

    zero = [0, 0, 0, 0]
    for output, inputs, coefficient in (
        (13, (9, 28, 30), {"rational": 1, "sqrt10": 0}),
        (32, (4, 6, 30), {"rational": -1, "sqrt10": 0}),
    ):
        row_path = (
            ROOT
            / f"d_quotient_classical/generated/berger_retained_mixed_ell3/row_{output:02d}.json.gz"
        )
        with gzip.open(row_path, "rt", encoding="utf-8") as handle:
            row_payload = json.load(handle)
        expected_term = [
            inputs[0],
            zero,
            inputs[1],
            zero,
            inputs[2],
            zero,
            coefficient,
        ]
        assert expected_term in row_payload["terms"], expected_term

    manuscript = ROOT / payload["manuscript"]
    assert _sha256(manuscript) == payload["manuscript_sha256"]
    text = manuscript.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    required_markers = [
        r"\boxed{\begin{gathered} \text{The retained mixed gravity--Maxwell bracket survives this}\\ \text{cyclic homological reduction through }\ell_3. \end{gathered}}",
        r"\begin{proposition}[Formal cyclic transfer through arity three]",
        r"\begin{theorem}[Nonzero retained mixed bracket for the frozen cyclic SDR]",
        r"\begin{proposition}[Constant-field cyclic-redefinition screen]",
        r"\begin{proposition}[First positive-jet cyclic-redefinition screen]",
        r"\begin{proposition}[Second-jet disposition of the former obstruction]",
        r"\begin{proposition}[Independent degree-zero lowered cyclicity]",
        r"\begin{proposition}[Independent full-BV quartic cyclicity]",
        r"\begin{theorem}[Cyclic causal Cartan compatibility]",
        r"$\mathbf{38}$ & $1$ & $\boldsymbol{\Theta^*}$",
        r"\newcommand{\pr}{\operatorname{pr}}",
        r"S^2=0,\qquad S\iota=0,\qquad \pi S=0",
        r"\iota^\dagger\Omega_{64}=\Omega_{36}\pi,\qquad \iota^\dagger\Omega_{64}\iota=\Omega_{36},\qquad S^\dagger\Omega_{64}+\Omega_{64}S=0",
        r"[\ell_3(\widehat h_{13},A_1,A_3)]_{\widehat h^*_{00}}^{(0)}&=+1",
        r"[\ell_3(\widehat h_{01},\widehat h_{03},A_3)]_{A^+_1}^{(0)}&=-1",
        r"\Lambda_{64,\pm}=S+\iota\Lambda_{36,\pm}\pi",
        r"\pi\Lambda_{64,\pm}\iota=\Lambda_{36,\pm}",
        r"25{,}950",
        r"25{,}662",
        r"17{,}108",
        r"not yet a photon or graviton scattering amplitude",
        r"The complete constant-field page is removable by the exact",
        r"BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1",
        r"BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1",
        r"\input{paper/11-gravity-light-ell3-witness-inclusion-columns.tex}",
        r"\frac{71p_1^2+71p_2^2+9p_3^2}{80}",
        r"the smallest natural support-local candidate adds a spatial STF2 prolongation",
        r"\begin{proposition}[Exact rank-$46$ STF2 graph carrier]",
        r"A_{10}+F^\dagger F&-F^\dagger",
        r"q_1^{46}S_{46}+S_{46}q_1^{46} =I_{46}-\iota_{36}^{46}\pi_{46}^{36}",
        r"BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1",
        r"\begin{proposition}[Normalized principal branch-anchor obstruction]",
        r"A=\Q(\sqrt{10})[\epsilon]/(\epsilon^2)",
        r"\epsilon s(1)=\epsilon",
        r"\left(1,0\right)",
        r"$71/40$",
        r"BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1",
        r"BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1",
        r"\frac{755}{9}",
        r"$4{,}276$-coefficient homogeneous correction",
        r"$1{,}380$ exact page-zero full-BV residual coefficients",
    ]
    for marker in required_markers:
        assert marker in normalized, marker

    forbidden_markers = [
        "the residual mixing table is complete",
        "the topological particle branch",
        "a Lorentzian quantum master equation is restored",
        "a positive-Hilbert-space theorem is proved",
        "arity four is certified",
        "The gravity--light interaction survives cyclic causal reduction",
        "All retained exchange sectors vanish",
        r"\rank E(e_{C^2})=1",
        "nonvanishing does not rest on a basis-dependent coefficient count",
        "the canonical local Einstein/extra-Weyl split is available on the 36-row carrier",
        "That carrier has not yet been constructed",
        "Equation~\\eqref{eq:mixing} is now authorized",
        r"\begin{theorem}[Scoped filtered cyclic obstruction]",
        "Consequently no admissible nonnegative filtered cyclic",
        "The obstruction lives on the first associated-graded page",
        "full-BV nonremovability in its declared filtered cyclic class",
    ]
    for marker in forbidden_markers:
        assert marker not in text, marker

    print("PAPER_11_GRAVITY_LIGHT_CYCLIC_CAUSAL_ELL3_THEOREM_FROZEN_CLAIM_MAP: PASS")


if __name__ == "__main__":
    main()

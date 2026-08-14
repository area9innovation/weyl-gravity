#!/usr/bin/env python3
"""Generate the auditable claim map for paper 21.

The generator imports existing certificates as authorities.  It does not
reproduce their scientific computations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper/21-reverse-foundations-of-physics-claim-map.json"
PAPER = "paper/21-reverse-foundations-of-physics.tex"
APPENDIX = "paper/21-reverse-foundations-of-physics-appendices.tex"
APPENDIX_GENERATOR = "paper/generate_21_reverse_foundations_appendices.py"
ATLAS_DATA = "foundations/site/data.json"
ASSEMBLY_DATA = "foundations/site/assemblies.json"

AUTHORITY_PATHS = {
    "intersection_cube": "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V15.json",
    "bt_euclidean_import": "foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json",
    "bt_free_reconstruction_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json",
    "bt_interacting_os_preflight": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_OS_WITNESS_PREFLIGHT_V1.json",
    "bt_lambda04_os_kernel_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json",
    "bt_uniform_convexity_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_UNIFORM_CONVEXITY_OBSTRUCTION_V1.json",
    "bt_schwinger_dyson_mode_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1.json",
    "bt_bilaplacian_reference_bridge": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_BILAPLACIAN_REFERENCE_BRIDGE_V1.json",
    "bt_low_mode_uv_schur_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_MODE_UV_SCHUR_OBSTRUCTION_V1.json",
    "bt_action_weight_virial_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1.json",
    "bt_affine_virial_action_density": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "bt_orthogonal_hessian_block_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ORTHOGONAL_HESSIAN_BLOCK_OBSTRUCTION_V1.json",
    "bt_residual_spectrahedral_pushforward": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json",
    "bt_residual_boundary_curvature_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_BOUNDARY_CURVATURE_OBSTRUCTION_V1.json",
    "bt_residual_tilt_jacobian_cancellation": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_TILT_JACOBIAN_CANCELLATION_V1.json",
    "bt_centered_fiber_domination_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CENTERED_FIBER_DOMINATION_OBSTRUCTION_V1.json",
    "bt_conditional_mass_escape_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CONDITIONAL_MASS_ESCAPE_OBSTRUCTION_V1.json",
    "bt_runaway_fiber_width_bound": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RUNAWAY_FIBER_WIDTH_BOUND_V1.json",
    "bt_separable_lowest_mode_curvature": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SEPARABLE_LOWEST_MODE_CURVATURE_V1.json",
    "bt_all_background_lowest_mode_curvature": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json",
    "bt_annealed_center_score_reduction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1.json",
    "bt_cubic_score_log_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "bt_score_rg_matching": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
    "bt_zero_fiber_ward_weight_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ZERO_FIBER_WARD_WEIGHT_OBSTRUCTION_V1.json",
    "bt_quartic_score_power_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_QUARTIC_SCORE_POWER_OBSTRUCTION_V1.json",
    "bt_complete_g4_uv_noncancellation": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_UV_NONCANCELLATION_V1.json",
    "bt_complete_g4_chaos_gate": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CHAOS_GATE_V1.json",
    "bt_complete_g4_effective_hessian": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_EFFECTIVE_HESSIAN_V1.json",
    "bt_complete_g4_connected_normalization": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1.json",
    "bt_complete_g4_l4_decision": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_DECISION_V1.json",
    "bt_complete_g4_general_l_two_loop": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1.json",
    "bt_complete_g4_seven_kernel_reduction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1.json",
    "full_surface_gap_audit": "foundations/results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json",
    "explorer_snapshot": "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json",
    "theory_assembly": "foundations/results/FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1.json",
    "gr_cassini_assembly": "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json",
    "mannheim_ngc3198_assembly": "foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json",
    "ngc3198_common_fit_comparison": "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json",
    "explicit_krein": "foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json",
    "krein_state_selection": "foundations/results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json",
    "separable_cstar_state_chain": "foundations/results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json",
    "coded_wave": "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json",
    "coded_wave_observable_reconstruction": "foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json",
    "coded_local_weak_wave_test_class": "foundations/results/FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1.json",
    "coded_weak_wave_h2_test_completion": "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json",
    "fixed_support_smooth_to_h2_translator": "foundations/results/FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1.json",
    "support_indexed_test_space_comparison": "foundations/results/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1.json",
    "scalar_minkowski_green_choice_audit": "foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1.json",
    "scalar_minkowski_biwave_green": "foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1.json",
    "scalar_biwave_to_weyl_bv_delta": "foundations/results/FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1.json",
    "finite_graph_causality": "foundations/results/FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1.json",
    "finite_bv": "foundations/results/FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(payload: dict) -> str:
    body = dict(payload)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_authority(relative: str) -> tuple[dict, dict]:
    path = ROOT / relative
    data = json.loads(path.read_text())
    record = {
        "path": relative,
        "sha256": sha256(path),
        "result_id": data.get("result_id", data.get("certificate")),
        "lifecycle": data.get("lifecycle", data.get("lifecycle_state")),
        "dependency_tags": data.get("dependency_tags", []),
    }
    return data, record


def build() -> dict:
    loaded: dict[str, dict] = {}
    authorities: dict[str, dict] = {}
    for name, path in AUTHORITY_PATHS.items():
        loaded[name], authorities[name] = load_authority(path)

    cube = loaded["intersection_cube"]
    bt_euclidean = loaded["bt_euclidean_import"]
    bt_free_obstruction = loaded["bt_free_reconstruction_obstruction"]
    bt_interacting_os = loaded["bt_interacting_os_preflight"]
    bt_lambda04_os = loaded["bt_lambda04_os_kernel_obstruction"]
    bt_action_weight = loaded["bt_action_weight_virial_obstruction"]
    bt_affine_virial = loaded["bt_affine_virial_action_density"]
    bt_orthogonal_hessian = loaded["bt_orthogonal_hessian_block_obstruction"]
    bt_residual_pushforward = loaded["bt_residual_spectrahedral_pushforward"]
    bt_residual_curvature = loaded["bt_residual_boundary_curvature_obstruction"]
    bt_residual_tilt = loaded["bt_residual_tilt_jacobian_cancellation"]
    bt_centered_fiber = loaded["bt_centered_fiber_domination_obstruction"]
    bt_conditional_escape = loaded["bt_conditional_mass_escape_obstruction"]
    bt_runaway_width = loaded["bt_runaway_fiber_width_bound"]
    bt_separable_curvature = loaded["bt_separable_lowest_mode_curvature"]
    bt_all_background_curvature = loaded["bt_all_background_lowest_mode_curvature"]
    bt_center_score = loaded["bt_annealed_center_score_reduction"]
    bt_cubic_score = loaded["bt_cubic_score_log_obstruction"]
    bt_score_rg = loaded["bt_score_rg_matching"]
    bt_ward_weight = loaded["bt_zero_fiber_ward_weight_obstruction"]
    bt_quartic_score = loaded["bt_quartic_score_power_obstruction"]
    bt_complete_g4 = loaded["bt_complete_g4_uv_noncancellation"]
    bt_g4_chaos = loaded["bt_complete_g4_chaos_gate"]
    bt_g4_hessian = loaded["bt_complete_g4_effective_hessian"]
    bt_g4_connected = loaded["bt_complete_g4_connected_normalization"]
    bt_g4_l4 = loaded["bt_complete_g4_l4_decision"]
    bt_g4_general_l = loaded["bt_complete_g4_general_l_two_loop"]
    bt_g4_seven = loaded["bt_complete_g4_seven_kernel_reduction"]
    site = loaded["explorer_snapshot"]
    gr_cassini = loaded["gr_cassini_assembly"]
    mannheim_ngc3198 = loaded["mannheim_ngc3198_assembly"]
    ngc3198_common_fit = loaded["ngc3198_common_fit_comparison"]
    coded_wave_observable = loaded["coded_wave_observable_reconstruction"]
    coded_local_weak_wave = loaded["coded_local_weak_wave_test_class"]
    coded_h2_test = loaded["coded_weak_wave_h2_test_completion"]
    smooth_translator = loaded["fixed_support_smooth_to_h2_translator"]
    support_indexed = loaded["support_indexed_test_space_comparison"]
    scalar_green = loaded["scalar_minkowski_green_choice_audit"]
    scalar_biwave = loaded["scalar_minkowski_biwave_green"]
    weyl_bv_delta = loaded["scalar_biwave_to_weyl_bv_delta"]
    atlas_data = json.loads((ROOT / ATLAS_DATA).read_text())
    assembly_data = json.loads((ROOT / ASSEMBLY_DATA).read_text())
    evidence = atlas_data["evidence"]
    literature = [entry for entry in evidence.values() if entry["kind"] == "LITERATURE"]
    local_results = [entry for entry in evidence.values() if entry["kind"] == "LOCAL_RESULT"]
    dimensions = cube["dimensions"]
    payload = {
        "schema_version": "paper-21-reverse-foundations-claim-map-v1",
        "result_id": "PAPER21_REVERSE_FOUNDATIONS_INTRODUCTION_V1",
        "result_kind": "PROGRAMME_SYNTHESIS_AND_TYPED_CASE_STUDY_MAP",
        "lifecycle": "WORKING_DRAFT",
        "created": "2026-08-14",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "paper": {
            "path": PAPER,
            "sha256": sha256(ROOT / PAPER),
            "appendix": {
                "path": APPENDIX,
                "sha256": sha256(ROOT / APPENDIX),
                "source_path": ATLAS_DATA,
                "source_sha256": sha256(ROOT / ATLAS_DATA),
                "source_canonical_digest": atlas_data["canonical_digest"],
                "assembly_source_path": ASSEMBLY_DATA,
                "assembly_source_sha256": sha256(ROOT / ASSEMBLY_DATA),
                "assembly_source_canonical_digest": assembly_data["canonical_digest"],
                "generator_path": APPENDIX_GENERATOR,
                "generator_sha256": sha256(ROOT / APPENDIX_GENERATOR),
            },
        },
        "formal_object": {
            "judgement": "L + S + M + Enc(P) |-[_R] O",
            "coordinates": {
                "L": "logic and inference rules",
                "S": "set, type, or existence theory",
                "M": "mathematical carrier and analytic machinery",
                "Enc(P)": "physical postulates under an explicit encoding",
                "R": "representation of inputs and outputs",
                "O": "one declared theorem-level physical obligation",
            },
            "relation_types": [
                "USED_BY_DISPLAYED_PROOF",
                "SUFFICIENT_OVER_BASE",
                "NECESSARY_OVER_BASE",
                "EQUIVALENT_OVER_BASE",
                "AVOIDED_BY_REFORMULATION",
                "INDEPENDENT_OVER_BASE",
                "UNKNOWN",
            ],
        },
        "atlas_snapshot": {
            "axis_sizes": dimensions["axis_sizes"],
            "cartesian_total": dimensions["cartesian_total"],
            "emitted_cells": dimensions["emitted_cells"],
            "coverage_classified_cells": dimensions["coverage_classified_cells"],
            "migration_pending_cells": dimensions["migration_pending_cells"],
            "emitted_status_counts": dimensions["status_counts"],
            "synthetic_complements": dimensions["cartesian_total"] - dimensions["emitted_cells"],
            "total_not_mapped_in_explorer": site["counts"]["not_mapped"],
            "reviewed_open_gaps": site["counts"]["reviewed_gap"],
            "evidence_records": site["counts"]["evidence_records"],
            "literature_records": len(literature),
            "local_result_records": len(local_results),
            "content_pinned_literature": sum(
                entry["artifact_status"] == "CONTENT_PINNED" for entry in literature
            ),
            "metadata_only_literature": sum(
                entry["artifact_status"] == "METADATA_ONLY" for entry in literature
            ),
            "evidence_records_used_by_matrix": len({
                evidence_id
                for cell in atlas_data["cells"]
                for evidence_id in cell.get("evidence", [])
            }),
            "axis_options": sum(len(axis["keys"]) for axis in atlas_data["axes"]),
            "implication_nodes": len(atlas_data["graph"]["nodes"]),
            "implication_edges": len(atlas_data["graph"]["edges"]),
            "strength_ladder_levels": len(atlas_data["ladder"]),
            "literature_complete": site["claim_flags"]["literature_complete"],
            "all_cells_assessed": cube["claim_flags"]["all_576_coordinates_assessed"],
            "prototype_assemblies": len(assembly_data["assemblies"]),
            "research_programme_lenses": sum(
                bool(item.get("camp_summary") and item.get("scope_note"))
                for item in assembly_data["assemblies"]
            ),
            "model_scoped_assemblies": len(assembly_data["model_scoped_assemblies"]),
            "gr_cassini_stages": len(gr_cassini["stages"]),
            "gr_cassini_interfaces": len(gr_cassini["interfaces"]),
            "gr_cassini_required_obligations": gr_cassini["applicability_summary"]["required"],
            "gr_cassini_required_obligations_satisfied": gr_cassini["applicability_summary"]["required_satisfied"],
            "gr_cassini_bounded_complete": gr_cassini["assembly_disposition"]["complete_within_declared_scope"],
            "gr_cassini_prediction_inside_reported_band": gr_cassini["empirical_comparison_rail"]["prediction_inside_reported_band"],
            "mannheim_ngc3198_stages": len(mannheim_ngc3198["stages"]),
            "mannheim_ngc3198_interfaces": len(mannheim_ngc3198["interfaces"]),
            "mannheim_ngc3198_endpoint_coarse_gate_passed": mannheim_ngc3198["numerical_reproduction_rail"]["gate_passed"],
            "mannheim_ngc3198_sparc_rms_km_s": mannheim_ngc3198["empirical_comparison_rail"]["unweighted_rms_residual_km_s"],
            "mannheim_ngc3198_sparc_reduced_chi2": mannheim_ngc3198["empirical_comparison_rail"]["reduced_chi_squared_no_refit"],
            "mannheim_ngc3198_sparc_coarse_gate_passed": mannheim_ngc3198["empirical_comparison_rail"]["coarse_rms_gate_passed"],
            "mannheim_ngc3198_sparc_random_error_gate_passed": mannheim_ngc3198["empirical_comparison_rail"]["random_error_reduced_chi2_gate_passed"],
            "mannheim_ngc3198_empirically_supported": mannheim_ngc3198["assembly_disposition"]["empirically_supported_within_declared_scope"],
            "ngc3198_common_fit_models": len(ngc3198_common_fit["models"]),
            "ngc3198_common_fit_ranking_AICc": ngc3198_common_fit["ranking_by_AICc"],
            "ngc3198_common_fit_random_error_passes": [item["model_id"] for item in ngc3198_common_fit["models"] if item["random_error_gate"]["passed"]],
            "ngc3198_common_fit_complete_theory_selected": ngc3198_common_fit["claim_flags"]["complete_theory_selected"],
            "coded_wave_observable_cutoff": coded_wave_observable["cutoff_theorem"]["cutoff"],
            "coded_wave_observable_full_state_reconstruction": coded_wave_observable["claim_flags"]["full_state_reconstruction_proved"],
            "coded_local_weak_wave_basis_tests": coded_local_weak_wave["localized_test_class"]["basis_size"],
            "coded_local_weak_wave_separation_rank": coded_local_weak_wave["separation"]["rank"],
            "coded_local_weak_wave_all_smooth_tests": coded_local_weak_wave["claim_flags"]["all_smooth_tests_covered"],
            "coded_local_weak_wave_causal_support": coded_local_weak_wave["claim_flags"]["strict_causal_support_proved"],
            "coded_h2_test_derivatives": len(coded_h2_test["rational_test_codes"]["derivative_multiindices"]),
            "coded_h2_test_density_status": coded_h2_test["named_completion"]["density_status"],
            "coded_h2_represented_smooth_tests_covered": coded_h2_test["claim_flags"]["represented_smooth_tests_covered"],
            "coded_h2_full_lf_topology": coded_h2_test["claim_flags"]["full_lf_test_topology_reconstructed"],
            "coded_h2_arbitrary_distribution_uniqueness": coded_h2_test["claim_flags"]["uniqueness_among_arbitrary_distributions_proved"],
            "coded_h2_causal_support": coded_h2_test["claim_flags"]["strict_causal_support_proved"],
            "coded_h2_fixture_wave_offsets": {item["id"]: item["binary_cutoff_offsets"]["scalar_wave"] for item in coded_h2_test["fixtures"]},
            "smooth_translator_fixture_shifts": {f"{item['margin'][0]}/{item['margin'][1]}": item["index_shift"] for item in smooth_translator["fixtures"]},
            "smooth_translator_choice_used": smooth_translator["claim_flags"]["choice_principle_used"],
            "support_indexed_stages": len(support_indexed["fixtures"]),
            "support_indexed_inclusion_checks": len(support_indexed["inclusion_checks"]),
            "support_indexed_name_equivalence": support_indexed["claim_flags"]["conventional_and_tagged_names_equivalent"],
            "support_indexed_full_lf_topology": support_indexed["claim_flags"]["full_lf_locally_convex_topology_identified"],
            "scalar_green_fixtures": len(scalar_green["fixtures"]),
            "scalar_green_support_samples": len(scalar_green["support_samples"]),
            "scalar_green_causal_support": scalar_green["claim_flags"]["strict_causal_support_proved"],
            "scalar_green_weyl_bv_propagator": scalar_green["claim_flags"]["weyl_bv_propagator_constructed"],
            "bt_euclidean_direct_capabilities": sum(item["evidence_role"] == "DIRECT_LOCAL" for item in bt_euclidean["capability_decisions"]),
            "bt_euclidean_reconstruction_status": next(item["new_status"] for item in bt_euclidean["capability_decisions"] if item["coordinate"]["obligation"] == "RECONSTRUCTION_LIMITS"),
            "bt_euclidean_numerical_status": bt_euclidean["numerical_reproducibility_records"][0]["status"],
            "bt_euclidean_carrier_relation": bt_euclidean["carrier_interface"]["relation"],
            "bt_free_os_reflected_norm": bt_free_obstruction["finite_volume_os_obstruction"]["four_dimensional_slice_average_reflected_norm"],
            "bt_free_os_near_zero_status": bt_free_obstruction["disposition"]["ordinary_os_reflection_positivity_near_lambda_zero"],
            "bt_free_os_lambda_0p4_status": bt_free_obstruction["disposition"]["ordinary_os_reflection_positivity_at_lambda_0p4"],
            "bt_free_h_minus_one_bound": bt_free_obstruction["free_volume_uniform_estimate"]["uniform_result"]["bound"],
            "bt_free_l2_status": bt_free_obstruction["disposition"]["free_uniform_l2_estimate"],
            "bt_interacting_os_numerical_status": bt_interacting_os["disposition"]["lambda_0p4_reflected_witness"],
            "bt_interacting_os_local_z": bt_interacting_os["algorithm_summaries"]["local_metropolis"]["z_from_zero"],
            "bt_interacting_os_hmc_z": bt_interacting_os["algorithm_summaries"]["hmc"]["z_from_zero"],
            "bt_interacting_os_cross_sampler_z": bt_interacting_os["cross_sampler_mean_z"],
            "bt_lambda_0p4_exact_os_status": bt_lambda04_os["disposition"]["ordinary_os_reflection_positivity_at_lambda_0p4"],
            "bt_interacting_uniform_h_minus_one_status": bt_action_weight["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"],
            "bt_pointwise_action_weight_necessary_exponent": "AT_LEAST_ONE_HALF",
            "bt_pointwise_virial_constant_two_status": bt_action_weight["radial_virial_obstruction"]["status"],
            "bt_affine_virial_status": bt_affine_virial["method_disposition"]["affine_pointwise_virial_bound"],
            "bt_actual_action_density_status": bt_affine_virial["method_disposition"]["actual_uniform_action_density_moment"],
            "bt_actual_half_action_factor_status": bt_affine_virial["method_disposition"]["actual_annealed_half_action_density_factor"],
            "bt_lambda_0p4_action_density_bound": bt_affine_virial["actual_gibbs_action_density"]["lambda_point_four_uniform_action_density_bound"],
            "bt_global_orthogonal_hessian_block_status": bt_orthogonal_hessian["method_disposition"]["global_orthogonal_hessian_block_positivity"],
            "bt_pointwise_half_action_curvature_route_status": bt_orthogonal_hessian["method_disposition"]["pointwise_half_action_curvature_route"],
            "bt_orthogonal_hessian_cell_value": bt_orthogonal_hessian["cell_calculation"]["directional_hessian"],
            "bt_residual_boundary_coordinate_status": bt_residual_pushforward["method_disposition"]["residual_spectrahedral_boundary_coordinates"],
            "bt_residual_tree_jacobian_status": bt_residual_pushforward["method_disposition"]["ground_state_tree_jacobian"],
            "bt_residual_entropy_jacobian_minimum_status": bt_residual_pushforward["method_disposition"]["vertex_transitive_entropy_jacobian_minimum"],
            "bt_residual_cycle_jacobian": bt_residual_pushforward["exact_cycle_fixture"]["restricted_jacobian"],
            "bt_normalized_lowest_mode_marginal_status": bt_residual_pushforward["method_disposition"]["normalized_lowest_mode_marginal_bound"],
            "bt_residual_pointwise_strict_convexity_status": bt_residual_curvature["method_disposition"]["pointwise_strict_convexity"],
            "bt_residual_uniform_curvature_status": bt_residual_curvature["method_disposition"]["uniform_positive_principal_curvature"],
            "bt_residual_weighted_mean_curvature_status": bt_residual_curvature["method_disposition"]["global_positive_gaussian_weighted_mean_curvature"],
            "bt_residual_trial_curvature_q2": bt_residual_curvature["lambda_point_four_fixture"]["trial_normal_curvature"],
            "bt_residual_weighted_mean_curvature_q2": bt_residual_curvature["lambda_point_four_fixture"]["gaussian_weighted_mean_curvature"],
            "bt_residual_induced_tilt_surface_jacobian_status": bt_residual_tilt["method_disposition"]["induced_tilt_surface_jacobian"],
            "bt_residual_inverse_tree_jacobian_cancellation_status": bt_residual_tilt["method_disposition"]["inverse_tree_jacobian_cancellation"],
            "bt_residual_tree_log_convexity_tilt_status": bt_residual_tilt["method_disposition"]["tree_log_convexity_as_extra_tilt_confinement"],
            "bt_direct_action_fiber_bound_status": bt_residual_tilt["method_disposition"]["direct_action_difference_or_fiber_ratio_bound"],
            "bt_residual_tilt_surface_ratio_c4": bt_residual_tilt["exact_cycle_tilt"]["surface_jacobian_ratio"],
            "bt_residual_tilt_inverse_density_ratio_c4": bt_residual_tilt["exact_cycle_tilt"]["inverse_density_jacobian_ratio"],
            "bt_residual_tilt_boltzmann_gap_c4": bt_residual_tilt["exact_cycle_tilt"]["boltzmann_exponent_gap"],
            "bt_centered_fiber_relative_domination_status": bt_centered_fiber["method_disposition"]["centered_pointwise_relative_action_domination"],
            "bt_centered_fiber_boltzmann_status": bt_centered_fiber["method_disposition"]["centered_pointwise_boltzmann_ratio_bound"],
            "bt_integrated_lowest_mode_marginal_evenness_status": bt_centered_fiber["method_disposition"]["integrated_lowest_mode_marginal_evenness"],
            "bt_annealed_recentered_fiber_status": bt_centered_fiber["method_disposition"]["annealed_or_recentered_fiber_ratio_bound"],
            "bt_centered_fiber_n1_action_ratio": bt_centered_fiber["exact_n1_fixture"]["per_spatial_site_action_ratio"],
            "bt_centered_fiber_all_n_ratio_bound": bt_centered_fiber["scalable_action_obstruction"]["action_ratio_bound"],
            "bt_conditional_mass_escape_status": bt_conditional_escape["method_disposition"]["conditional_mass_escape_on_exact_family"],
            "bt_uniform_raw_conditional_moment_status": bt_conditional_escape["method_disposition"]["uniform_backgroundwise_raw_conditional_second_moment"],
            "bt_uniform_recentered_conditional_variance_status": bt_conditional_escape["method_disposition"]["uniform_recentered_conditional_variance"],
            "bt_annealed_center_second_moment_status": bt_conditional_escape["method_disposition"]["annealed_center_second_moment"],
            "bt_conditional_escape_m2_tail_exponent": bt_conditional_escape["exact_m2_fixture"]["binary_tail_exponent"],
            "bt_runaway_family_recentered_variance_status": bt_runaway_width["method_disposition"]["runaway_family_recentered_conditional_variance"],
            "bt_runaway_family_curvature_lower_bound": bt_runaway_width["uniform_lower_bound"]["lower_bound"],
            "bt_runaway_family_conditional_mean_escape_status": bt_runaway_width["method_disposition"]["runaway_family_conditional_mean_escape"],
            "bt_all_background_recentered_variance_status": bt_runaway_width["method_disposition"]["all_background_uniform_recentered_conditional_variance"],
            "bt_separable_lowest_mode_curvature_status": bt_separable_curvature["method_disposition"]["separable_background_lowest_mode_curvature"],
            "bt_separable_conditional_variance_status": bt_separable_curvature["method_disposition"]["separable_background_conditional_variance"],
            "bt_correlated_spatial_remainder_status": bt_separable_curvature["method_disposition"]["all_background_spatial_remainder_nonnegative"],
            "bt_correlated_spatial_remainder_fixture": bt_separable_curvature["exact_correlated_fixture"]["spatial_correlation_remainder_per_inert_spatial_cell"],
            "bt_all_background_lowest_mode_curvature_status": bt_all_background_curvature["method_disposition"]["all_background_lowest_mode_strong_convexity"],
            "bt_all_background_conditional_variance_status": bt_all_background_curvature["method_disposition"]["all_background_uniform_recentered_conditional_variance"],
            "bt_all_background_curvature_constant": bt_all_background_curvature["cycle_completion"]["final_action_curvature_constant"],
            "bt_all_background_variance_constant": bt_all_background_curvature["theorem"]["variance_constant"],
            "bt_annealed_center_after_width_status": bt_all_background_curvature["method_disposition"]["annealed_center_second_moment"],
            "bt_center_to_score_reduction_status": bt_center_score["method_disposition"]["annealed_center_to_zero_fiber_score_reduction"],
            "bt_center_score_bound_status": bt_center_score["method_disposition"]["annealed_zero_fiber_score_bound"],
            "bt_center_score_integrated_moment_status": bt_center_score["method_disposition"]["normalized_lowest_mode_second_moment"],
            "bt_cubic_soft_leg_status": bt_cubic_score["method_disposition"]["lattice_cubic_soft_leg_factor"],
            "bt_cubic_fixed_order_uniform_score_status": bt_cubic_score["method_disposition"]["fixed_bare_coupling_coefficientwise_uniform_score_proof"],
            "bt_cubic_nonperturbative_score_status": bt_cubic_score["method_disposition"]["nonperturbative_annealed_zero_fiber_score_bound"],
            "bt_cubic_dyadic_block_lower_bound": bt_cubic_score["rigorous_logarithmic_lower_bound"]["lower_bound_per_block"],
            "bt_score_log_residue_status": bt_score_rg["method_disposition"]["lattice_score_logarithmic_residue"],
            "bt_rg_matched_leading_score_status": bt_score_rg["method_disposition"]["rg_matched_leading_score_uniformity"],
            "bt_rg_matched_leading_score_limit": bt_score_rg["matched_refinement"]["score_limit_exact"],
            "bt_fixed_spacing_large_volume_score_status": bt_score_rg["method_disposition"]["fixed_spacing_large_volume_score_bound"],
            "bt_rg_nonperturbative_score_status": bt_score_rg["method_disposition"]["nonperturbative_annealed_zero_fiber_score_bound"],
            "bt_ordinary_eom_score_identity_status": bt_score_rg["method_disposition"]["ordinary_finite_lattice_eom_score_identity"],
            "bt_eom_to_zero_fiber_transfer_status": bt_score_rg["method_disposition"]["ordinary_eom_to_zero_fiber_score_transfer"],
            "bt_specific_zero_fiber_ward_status": bt_score_rg["method_disposition"]["bt_specific_zero_fiber_ward_identity"],
            "bt_zero_fiber_change_of_measure_status": bt_ward_weight["method_disposition"]["zero_fiber_constrained_change_of_measure"],
            "bt_q_zero_uniform_lower_bound_status": bt_ward_weight["method_disposition"]["bt_background_uniform_q_zero_lower_bound"],
            "bt_constrained_ward_to_annealed_score_status": bt_ward_weight["method_disposition"]["pointwise_constrained_ward_to_annealed_score_transfer"],
            "bt_annealed_inverse_density_status": bt_ward_weight["method_disposition"]["annealed_inverse_density_or_center_bound"],
            "bt_quartic_kernel_status": bt_quartic_score["method_disposition"]["exact_quartic_score_kernel"],
            "bt_quartic_soft_degree": bt_quartic_score["method_disposition"]["quartic_external_soft_degree"],
            "bt_isolated_quartic_square_status": bt_quartic_score["method_disposition"]["isolated_quartic_score_square_uniform_in_L"],
            "bt_complete_order_g_four_score_status": bt_quartic_score["method_disposition"]["complete_order_g_four_score_coefficient"],
            "bt_quartic_power_cancellation_status": bt_quartic_score["method_disposition"]["power_cancellation_in_renormalized_zero_fiber_composite"],
            "bt_complete_g4_formula_status": bt_complete_g4["method_disposition"]["complete_order_g_four_background_score_formula"],
            "bt_complete_g4_uv_coefficient_status": bt_complete_g4["method_disposition"]["complete_order_g_four_uv_local_p_squared_coefficient"],
            "bt_complete_g4_uv_cancellation_status": bt_complete_g4["method_disposition"]["uv_local_or_diagramwise_power_cancellation"],
            "bt_complete_g4_whole_lattice_cancellation_status": bt_complete_g4["method_disposition"]["whole_lattice_order_g_four_power_cancellation"],
            "bt_complete_g4_ir_complement_status": bt_complete_g4["method_disposition"]["infrared_complement_power_bound"],
            "bt_g4_chaos_decomposition_status": bt_g4_chaos["method_disposition"]["complete_order_g_four_chaos_decomposition"],
            "bt_g4_signed_second_chaos_status": bt_g4_chaos["method_disposition"]["all_signed_cancellation_localized_to_second_chaos"],
            "bt_g4_positive_norm_power_status": bt_g4_chaos["method_disposition"]["positive_norm_uv_power_lower_bound"],
            "bt_g4_effective_kernel_bound_status": bt_g4_chaos["method_disposition"]["effective_second_chaos_kernel_norm_bound"],
            "bt_g4_whole_lattice_survival_status": bt_g4_chaos["method_disposition"]["whole_lattice_order_g_four_power_survival"],
            "bt_g4_expected_hessian_status": bt_g4_hessian["method_disposition"]["second_chaos_expected_hessian_representation"],
            "bt_g4_conditioned_covariance_decomposition_status": bt_g4_hessian["method_disposition"]["conditioned_bulk_plus_rank_one_decomposition"],
            "bt_g4_explicit_momentum_kernel_status": bt_g4_hessian["method_disposition"]["explicit_lattice_momentum_kernel"],
            "bt_g4_hessian_kernel_bound_status": bt_g4_hessian["method_disposition"]["effective_second_chaos_kernel_norm_bound"],
            "bt_g4_connected_reorganization_status": bt_g4_connected["method_disposition"]["complete_M4_connected_covariance_reorganization"],
            "bt_g4_normalization_alignment_status": bt_g4_connected["method_disposition"]["normalization_aligned_A_sector"],
            "bt_g4_termwise_alignment_bound_status": bt_g4_connected["method_disposition"]["separate_or_triangle_bound_on_aligned_sector"],
            "bt_g4_connected_maximum_loop_rank": bt_g4_connected["method_disposition"]["complete_connected_M4_maximum_loop_rank"],
            "bt_g4_exact_cancellation_status": bt_g4_connected["method_disposition"]["exact_whole_lattice_M4_cancellation"],
            "bt_g4_conditioned_maximum_loop_rank": bt_g4_l4["method_disposition"]["conditioned_connected_maximum_loop_rank"],
            "bt_g4_l4_complete_M4_status": bt_g4_l4["method_disposition"]["finite_L4_complete_M4"],
            "bt_g4_l4_complete_M4": bt_g4_l4["exact_L4_decision"]["M4"],
            "bt_g4_all_volume_zero_identity_status": bt_g4_l4["method_disposition"]["all_volume_exact_M4_zero_identity"],
            "bt_g4_large_volume_sign_and_scaling_status": bt_g4_l4["method_disposition"]["large_volume_M4_sign_and_scaling"],
            "bt_g4_general_l_two_loop_formula_status": bt_g4_general_l["method_disposition"]["generic_L_at_least_five_complete_two_loop_formula"],
            "bt_g4_power_tadpole_survival_status": bt_g4_general_l["method_disposition"]["power_sized_Y_squared_and_XY_tadpole_survival"],
            "bt_g4_factorized_conditioning_status": bt_g4_general_l["method_disposition"]["factorized_conditioning_sector"],
            "bt_g4_factorized_tuned_branch_status": bt_g4_general_l["method_disposition"]["factorized_conditioning_sector_on_tuned_running_branch"],
            "bt_g4_remaining_fourteen_kernel_status": bt_g4_general_l["method_disposition"]["remaining_fourteen_unfactorized_two_loop_kernel_bound"],
            "bt_g4_general_l_surviving_integrands": bt_g4_general_l["two_loop_atlas"]["statistics"]["surviving_integrand_count"],
            "bt_g4_seven_kernel_reduction_status": bt_g4_seven["method_disposition"]["fourteen_to_seven_inversion_reduction"],
            "bt_g4_paired_quartic_status": bt_g4_seven["method_disposition"]["paired_quartic_uniform_product_bound"],
            "bt_g4_negative_nested_carrier_status": bt_g4_seven["method_disposition"]["negative_nested_one_soft_carrier"],
            "bt_g4_termwise_tuned_g4_status": bt_g4_seven["method_disposition"]["termwise_tuned_order_g_four_uniformity"],
            "bt_g4_combined_seven_kernel_status": bt_g4_seven["method_disposition"]["combined_seven_kernel_large_volume_sign_and_scaling"],
            "standard_reference_direct_obligations": next(item for item in assembly_data["assemblies"] if item["id"] == "STANDARD_MIXED_REFERENCE")["coverage"]["direct"],
            "external_calibration_records": len(assembly_data["calibration_controls"][0]["records"]),
            "external_calibration_benchmark_families": sum(item["status"] == "SUPPORTED_CONTROL" for item in assembly_data["calibration_controls"][0]["benchmark_coverage"]),
        },
        "claims": [
            {
                "claim_id": "RF-01-TYPED-JUDGEMENT",
                "statement": "Physical, mathematical, foundational, and representational assumptions must be typed before implication strength is assigned.",
                "status": "PROGRAMME_DEFINITION",
                "authorities": [],
                "dependency_tags": ["LOCAL-ALGEBRAIC"],
            },
            {
                "claim_id": "RF-02-NAVIGATIONAL-ATLAS",
                "statement": "The current 6 x 6 x 16 atlas is a navigational projection with 576 coordinates, not an ontology or an independence theorem.",
                "status": "CORPUS_SYNTHESIS",
                "authorities": ["intersection_cube", "full_surface_gap_audit", "explorer_snapshot"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-03-EXPLICIT-KREIN-ZF",
                "statement": "The displayed named reduced-mode Krein carrier and Fock lift are constructible in ZF without a Countable Choice operation; finite cutoffs are PRA-checkable.",
                "status": "SUFFICIENT_OVER_BASE",
                "authorities": ["explicit_krein"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-04-STATE-SELECTION-SPLIT",
                "statement": "Explicit normalized states exist in the displayed ZF carrier, but the fundamental symmetry does not select a unique physical state; the normal permutation-invariant density-state obstruction is scoped to its stated symmetry class.",
                "status": "SUFFICIENCY_AND_SCOPED_OBSTRUCTION",
                "authorities": ["krein_state_selection", "separable_cstar_state_chain"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-05-CODED-WAVE-RCA0",
                "statement": "RCA_0 suffices for the represented coded-circle wave evolution, uniqueness, group law, and energy conservation with supplied fast Cauchy rates.",
                "status": "SUFFICIENT_OVER_BASE",
                "authorities": ["coded_wave"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-06-EVOLUTION-CAUSALITY-SPLIT",
                "statement": "The coded evolution result does not construct advanced or retarded Green maps or prove continuum causal support.",
                "status": "DOES_NOT_ESTABLISH",
                "authorities": ["coded_wave"],
                "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-07-FINITE-CONTINUUM-SPLIT",
                "statement": "Exact graph-step causal support is certified for a finite rational recurrence and is not a continuum Lorentzian causal theorem.",
                "status": "LOCAL_RESULT_WITH_BOUNDARY",
                "authorities": ["finite_graph_causality"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-08-FINITE-BV-BOUNDARY",
                "statement": "One explicitly presented finite energy-two BV contraction is PRA-checkable; this does not establish an infinite classical freeze or a quantum promotion.",
                "status": "SUFFICIENT_OVER_BASE",
                "authorities": ["finite_bv"],
                "dependency_tags": ["LOCAL-ALGEBRAIC"],
            },
            {
                "claim_id": "RF-09-GR-CASSINI-ASSEMBLY",
                "statement": "For the declared standard-GR solar-vacuum model, the exact field-equation-to-null-delay chain gives gamma=1 and the resulting prediction lies inside the publisher's displayed Cassini band; the operational and empirical joins remain literature-scoped.",
                "status": "MODEL_SCOPED_EMPIRICAL_COMPARISON",
                "authorities": ["gr_cassini_assembly"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-10-BT-EUCLIDEAN-LATTICE",
                "statement": "The positive finite BT Euclidean lattice supplies five direct finite-volume capabilities and a coarse independent-sampler reproduction record; reconstruction remains open, and its full nonperturbative carrier is not identical to the all-real BT/Krein carrier.",
                "status": "LOCAL_RESULT_WITH_NUMERICAL_AND_CARRIER_BOUNDARIES",
                "authorities": ["bt_euclidean_import"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            },
            {
                "claim_id": "RF-11-BT-FREE-RECONSTRUCTION-OBSTRUCTION",
                "statement": "On the zero-mode-fixed 6^4 free BT lattice, a shift-invariant positive-time slice observable has exact reflected norm -1/1296; fixed-volume continuity extends the ordinary-OS obstruction to some open coupling interval around zero, while lambda=0.4 remains open. The free L^4 family has a uniform H^-1 second-moment bound 15/32 and a logarithmically divergent L2 second moment.",
                "status": "SCOPED_OS_OBSTRUCTION_AND_FREE_UNIFORM_ESTIMATE",
                "authorities": ["bt_free_reconstruction_obstruction"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            },
            {
                "claim_id": "RF-12-BT-INTERACTING-OS-PREFLIGHT",
                "statement": "At lambda=0.4 on 6^4, all eight independent HMC and local-Metropolis chain means for the reflected witness are negative; equal-replica scores are -6.25 and -2.53 standard errors and the algorithm means differ by 0.64 combined standard errors. This numerical result is supporting only; the separate exact kernel certificate decides ordinary OS positivity.",
                "status": "NUMERICAL_FINITE_VOLUME_SUPPORTING_EXACT_OBSTRUCTION",
                "authorities": ["bt_interacting_os_preflight"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            },
            {
                "claim_id": "RF-13-BT-INTERACTING-RECONSTRUCTION-FRONTIER",
                "statement": "At lambda=0.4 on the 6^4 lattice, an exact two-point reflected density-kernel minor obstructs ordinary OS positivity. The affine virial theorem proves a volume-uniform actual Gibbs action-density bound and annealed half-action factor. Exact period-four data obstruct the global Schur route. The residual map identifies positive fields modulo scale with a Schrödinger spectrahedral boundary and gives the exact normalized Gaussian-surface/tree-Jacobian pushforward. Its curvature and tree-Jacobian shortcuts are obstructed. An exact orthogonal-background family makes centered pointwise relative-action domination fail. On the subsequence eta_m=4m log(2) a, every global fiber minimizer lies below u=-m and the conditional probability of u>=-m is at most 2^-m, so the background-uniform raw conditional second moment is obstructed. On that same runaway family, however, K_m(2^u)>=115/4 proves a uniform recentered conditional-variance bound and E_qm[u]<-m/2: the obstruction is moving center rather than widening fiber. A plaquette absorption theorem proves for every background and L>=4 that the lowest axial curvature is at least (2/9)*N*omega_L^2 and conditional variance is at most 9/(2*N*omega_L^2). Strong convexity reduces the annealed center to one zero-fiber-score estimate. Its leading free orthogonal-background coefficient has residue 5/(16*pi^2) times log L, obstructing fixed-bare coefficientwise uniformity. On a fixed-physical-volume asymptotically free trajectory, however, g_L^2 log L tends to 8*pi^2/5 and the leading normalized score coefficient tends exactly to 1/2. This restores leading-log uniformity only on the tuned refinement branch. The exact ordinary equation-of-motion Ward identity controls the sampled full score, and a shifted-Gaussian fixture with full-score variance 2 but zero-fiber-score variance 100 obstructs its general transfer to the missing target. Exact disintegration further proves that constrained and integrated-marginal identities weight backgrounds by q_eta(0), while the target requires division by q_eta(0). On the actual BT runaway family the u-density obeys q_m^(u)(0)<=2^-m/m; the t-density differs only by the fixed factor 1/log(2), so no pointwise uniform lower bound can remove that weight. The annealed estimate may still succeed by exploiting the Gibbs rarity of those backgrounds. At complete order g^4, the fourteen unfactorized two-loop entries reduce to seven inversion pairs; one negative nested carrier has magnitude at least c*L^2, obstructing termwise tuned-g_L^4 bounds while leaving cancellation in the seven-kernel sum open. Fixed-spacing large volume, all-order resummation, and the nonperturbative Gibbs score remain open. Half-period translation proves the fully integrated marginal is even. The all-background width is closed; a nonperturbative center estimate and the actual interacting H^-1 moment remain open.",
                "status": "EXACT_FINITE_OS_AND_METHOD_OBSTRUCTIONS_WITH_ALL_BACKGROUND_WIDTH_RG_MATCHED_LEADING_LOG_WARD_WEIGHT_QUARTIC_POWER_UV_G4_NONCANCELLATION_CHAOS_HESSIAN_CONNECTED_L4_GENERAL_L_AND_SEVEN_KERNEL_POWER_CARRIER_GATES",
                "authorities": [
                    "bt_lambda04_os_kernel_obstruction",
                    "bt_uniform_convexity_obstruction",
                    "bt_schwinger_dyson_mode_obstruction",
                    "bt_bilaplacian_reference_bridge",
                    "bt_low_mode_uv_schur_obstruction",
                    "bt_action_weight_virial_obstruction",
                    "bt_affine_virial_action_density",
                    "bt_orthogonal_hessian_block_obstruction",
                    "bt_residual_spectrahedral_pushforward",
                    "bt_residual_boundary_curvature_obstruction",
                    "bt_residual_tilt_jacobian_cancellation",
                    "bt_centered_fiber_domination_obstruction",
                    "bt_conditional_mass_escape_obstruction",
                    "bt_runaway_fiber_width_bound",
                    "bt_separable_lowest_mode_curvature",
                    "bt_all_background_lowest_mode_curvature",
                    "bt_annealed_center_score_reduction",
                    "bt_cubic_score_log_obstruction",
                    "bt_score_rg_matching",
                    "bt_zero_fiber_ward_weight_obstruction",
                    "bt_quartic_score_power_obstruction",
                    "bt_complete_g4_uv_noncancellation",
                    "bt_complete_g4_chaos_gate",
                    "bt_complete_g4_effective_hessian",
                    "bt_complete_g4_connected_normalization",
                    "bt_complete_g4_l4_decision",
                    "bt_complete_g4_general_l_two_loop",
                    "bt_complete_g4_seven_kernel_reduction",
                ],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            },
            {
                "claim_id": "RF-14-MANNHEIM-NGC3198-ASSEMBLY",
                "statement": "For the declared Mannheim--Kazanas NGC 3198 thin-disk model, independent evaluation coarsely reproduces the paper's endpoint and passes a no-refit SPARC RMS gate, but fails the declared reduced-chi-squared gate from SPARC random errors alone; the mixed comparison does not establish empirical support.",
                "status": "NUMERICAL_REPRODUCTION_WITH_MIXED_CROSS_DATASET_COMPARISON",
                "authorities": ["mannheim_ngc3198_assembly"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-15-NGC3198-COMMON-FIT-CONTROL",
                "statement": "Under one bounded NGC 3198 protocol with common velocities and analytic baryonic geometry, GR plus NFW has the lowest AICc and is the only tested family passing the declared random-error gate; this does not select a complete theory or generalize beyond one galaxy.",
                "status": "BOUNDED_SINGLE_GALAXY_COMMON_PROTOCOL_MODEL_COMPARISON",
                "authorities": ["ngc3198_common_fit_comparison"],
                "dependency_tags": ["LOCAL-ALGEBRAIC"],
            },
            {
                "claim_id": "RF-16-CODED-OBSERVABLE-RECONSTRUCTION",
                "statement": "For the declared rational wave fixtures and periodic detector, RCA_0 proves uniform reconstruction of one smeared observable from finite rational dyadic interpolants with explicit cutoff N(k)=k+ell(K)+1; no full-state or causal reconstruction follows.",
                "status": "SUFFICIENT_OVER_BASE_WITH_RECONSTRUCTION_BOUNDARY",
                "authorities": ["coded_wave_observable_reconstruction"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-17-LOCALIZED-COEFFICIENT-WEAK-WAVE",
                "statement": "Ten characteristic-localized rational polynomial tests have an exact rank-10 labelled chiral measurement matrix and certify the weak transport and derived scalar wave identities coefficient by coefficient; the finite span is not every smooth test and proves no causal support.",
                "status": "FINITE_LOCALIZED_TEST_THEOREM_WITH_DISTRIBUTIONAL_BOUNDARY",
                "authorities": ["coded_local_weak_wave_test_class"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-18-NAMED-H2-WEAK-WAVE-COMPLETION",
                "statement": "Over RCA_0, fast H2 names of rational periodic compact-time C1 piecewise-polynomial tests carry an explicit weak-residual modulus, so the coded energy solution defines a continuous distributional field-state functional and satisfies the weak wave equation on every represented test; this does not reconstruct the unrestricted LF test topology or prove uniqueness among arbitrary distributions or causal support.",
                "status": "REPRESENTATION_AWARE_WEAK_SOLUTION_COMPLETION_WITH_LF_AND_CAUSAL_BOUNDARIES",
                "authorities": ["coded_weak_wave_h2_test_completion"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-19-FIXED-SUPPORT-SMOOTH-TO-H2-TRANSLATOR",
                "statement": "Over RCA_0, a periodic smooth test carrying rational fixed-support advice and a supplied derivative approximation rate through order two translates uniformly to the rational compact-time H2 name by an explicit cubic cutoff and base-four index shift, without a choice operation; no name is manufactured from a bare extensional function.",
                "status": "REPRESENTATION_TRANSLATOR_WITH_EXPLICIT_ADVICE_AND_MODULUS",
                "authorities": ["fixed_support_smooth_to_h2_translator"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-20-SUPPORT-INDEXED-TEST-SPACE-COMPARISON",
                "statement": "Over RCA_0, conventional compact-test names with a discrete support bound and tagged fixed-support union names are exactly intertranslatable, and the stagewise H2 embedding is coherent; this name equivalence neither identifies the full locally convex LF topology nor makes the H2 embedding surjective.",
                "status": "REPRESENTED_NAME_EQUIVALENCE_WITH_LF_TOPOLOGY_BOUNDARY",
                "authorities": ["support_indexed_test_space_comparison"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-21-SCALAR-MINKOWSKI-GREEN-CHOICE-AUDIT",
                "statement": "For the flat scalar 1+1 wave operator, canonical exact retarded and advanced Green maps satisfy two-sided code identities, strict causal support, and adjoint duality in PRA and extend to supplied fast source names over RCA_0 without choice; this is not a Weyl/BV propagator or quantum causal construction.",
                "status": "SCOPED_SCALAR_LORENTZIAN_CAUSAL_GREEN_CERTIFICATE",
                "authorities": ["scalar_minkowski_green_choice_audit"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-22-SCALAR-MINKOWSKI-BIWAVE-GREEN",
                "statement": "For the flat scalar 1+1 biwave operator B=P^2, the canonical compositions of scalar retarded and advanced Green maps satisfy exact two-sided code identities, strict causal support, and adjoint duality in PRA; supplied fast L2 names extend over RCA_0 on a finite observation horizon with four past-zero Cauchy data and no global bounded-energy claim.",
                "status": "SCOPED_SCALAR_FOURTH_ORDER_LORENTZIAN_CAUSAL_CERTIFICATE",
                "authorities": ["scalar_minkowski_biwave_green"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-23-SCALAR-BIWAVE-TO-WEYL-BV-DELTA",
                "statement": "Sixteen typed gates separate the flat scalar biwave certificate from a full Lorentzian Weyl BV propagator. The delta records a positive four-row Nariai control, an open Berger route, two scoped architectural no-go theorems, and the failed authoritative classical import gate; it constructs no full-complex propagator, Hadamard state, renormalized products, causal pAQFT, or Lorentzian QME.",
                "status": "FAIL_CLOSED_CROSS_THEORY_DEPENDENCY_DELTA",
                "authorities": ["scalar_biwave_to_weyl_bv_delta"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            },
        ],
        "literature_scope": [
            {"source_id": "simpson-2009", "url": "https://doi.org/10.1017/CBO9780511581007", "role": "reverse mathematics and subsystem calibration"},
            {"source_id": "carcassi-aidala-2022", "url": "https://doi.org/10.1007/s10701-022-00555-z", "role": "reverse physics"},
            {"source_id": "hardy-2001", "url": "https://arxiv.org/abs/quant-ph/0101012", "role": "operational reconstruction and continuity"},
            {"source_id": "chiribella-dariano-perinotti-2011", "url": "https://doi.org/10.1103/PhysRevA.84.012311", "role": "informational reconstruction and purification"},
            {"source_id": "blackadar-farah-karagila-2023", "url": "https://arxiv.org/abs/2304.09602", "role": "Hilbert spaces in ZF without Countable Choice"},
            {"source_id": "blackadar-farah-2026", "url": "https://arxiv.org/abs/2602.15812", "role": "separable C*-algebras in ZF"},
            {"source_id": "coquand-spitters-2009", "url": "https://doi.org/10.1017/S0305004109002515", "role": "constructive Gelfand duality"},
            {"source_id": "heunen-landsman-spitters-2009", "url": "https://arxiv.org/abs/0709.4364", "role": "topos algebraic quantum theory"},
            {"source_id": "gibbons-hoffman-wootters-2004", "url": "https://arxiv.org/abs/quant-ph/0401155", "role": "finite-field phase-space construction"},
            {"source_id": "baer-2015", "url": "https://arxiv.org/abs/1310.0738", "role": "classical Green-hyperbolic theory"},
            {"source_id": "pauly-steinberg-2018", "url": "https://doi.org/10.1007/s00224-016-9745-6", "role": "represented smooth and compactly supported test-function spaces"},
            {"source_id": "van-schaftingen-2014", "url": "https://doi.org/10.1016/j.jmaa.2014.05.036", "role": "piecewise-polynomial approximation in Sobolev norms"},
            {"source_id": "weihrauch-zhong-2006", "url": "https://doi.org/10.1137/S0097539704446360", "role": "computable fundamental solutions"},
            {"source_id": "weihrauch-zhong-2002", "url": "https://doi.org/10.1112/S0024611502013643", "role": "computable wave propagation on differentiable and Sobolev representations"},
            {"source_id": "pischke-2025", "url": "https://arxiv.org/abs/2304.01723", "role": "proof mining for nonlinear semigroups"},
            {"source_id": "bertotti-iess-tortora-2003", "url": "https://doi.org/10.1038/nature01997", "role": "standard-GR solar-system positive control"},
            {"source_id": "kramer-et-al-2021", "url": "https://doi.org/10.1103/PhysRevX.11.041050", "role": "standard-GR compact-binary positive control"},
            {"source_id": "lvk-gwtc3-2021", "url": "https://arxiv.org/abs/2112.06861", "role": "standard-GR gravitational-wave positive control"},
            {"source_id": "abbott-et-al-gw170817-2017", "url": "https://arxiv.org/abs/1710.05834", "role": "standard-GR multimessenger propagation positive control"},
            {"source_id": "mannheim-obrien-2012", "url": "https://arxiv.org/abs/1011.3495", "role": "published conformal-gravity rotation-curve equations and NGC 3198 parameter row"},
            {"source_id": "lelli-mcgaugh-schombert-2016", "url": "https://astroweb.case.edu/SPARC/", "role": "official later SPARC NGC 3198 cross-dataset rotation curve"},
        ],
        "claim_flags": {
            "programme_definition_supplied": True,
            "typed_relations_supplied": True,
            "case_study_authorities_pinned": True,
            "static_atlas_appendix_generated": True,
            "complete_evidence_register_generated": True,
            "complete_literature_register_generated": True,
            "evidence_usage_crosswalk_generated": True,
            "model_scoped_end_to_end_assembly_generated": True,
            "bounded_empirical_comparison_registered": True,
            "mannheim_ngc3198_mixed_assembly_registered": True,
            "ngc3198_common_fit_comparison_registered": True,
            "bt_euclidean_finite_capabilities_imported": True,
            "bt_euclidean_coarse_reproduction_separated": True,
            "bt_free_os_obstruction_certified": True,
            "bt_free_h_minus_one_estimate_certified": True,
            "bt_lambda_0p4_os_status_decided": True,
            "bt_lambda_0p4_two_sampler_sign_support": True,
            "bt_interacting_uniform_h_minus_one_established": False,
            "bt_half_action_density_candidate_established": False,
            "bt_actual_interacting_action_density_established": True,
            "bt_actual_annealed_half_action_factor_established": True,
            "bt_global_orthogonal_hessian_block_obstructed": True,
            "bt_pointwise_half_action_curvature_route_obstructed": True,
            "bt_residual_spectrahedral_pushforward_established": True,
            "bt_vertex_transitive_entropy_jacobian_minimum_established": True,
            "bt_normalized_lowest_mode_marginal_established": False,
            "bt_residual_pointwise_strict_convexity_established": True,
            "bt_residual_uniform_positive_curvature_established": False,
            "bt_residual_positive_weighted_mean_curvature_established": False,
            "bt_standard_boundary_curvature_spectral_gap_route_obstructed": True,
            "bt_residual_tilt_jacobian_cancellation_established": True,
            "bt_tree_log_convexity_extra_tilt_confinement_obstructed": True,
            "bt_direct_action_fiber_bound_established": False,
            "bt_centered_pointwise_fiber_domination_obstructed": True,
            "bt_integrated_lowest_mode_marginal_evenness_established": True,
            "bt_annealed_recentered_fiber_bound_established": False,
            "bt_conditional_mass_escape_established": True,
            "bt_uniform_backgroundwise_raw_conditional_moment_obstructed": True,
            "bt_uniform_recentered_conditional_variance_established": True,
            "bt_runaway_family_recentered_conditional_variance_established": True,
            "bt_runaway_family_conditional_mean_escape_established": True,
            "bt_separable_lowest_mode_curvature_established": True,
            "bt_all_background_lowest_mode_curvature_established": True,
            "bt_all_background_lowest_mode_curvature_absorption_established": True,
            "bt_all_background_recentered_conditional_variance_established": True,
            "bt_annealed_center_second_moment_established": False,
            "bt_center_to_zero_fiber_score_reduction_established": True,
            "bt_fixed_bare_coefficientwise_score_route_obstructed": True,
            "bt_nonperturbative_annealed_score_established": False,
            "bt_score_log_residue_established": True,
            "bt_rg_matched_leading_score_uniformity_restored": True,
            "bt_fixed_spacing_large_volume_score_established": False,
            "bt_ordinary_eom_score_identity_established": True,
            "bt_eom_to_zero_fiber_general_transfer_obstructed": True,
            "bt_specific_zero_fiber_ward_identity_established": False,
            "bt_quartic_score_kernel_established": True,
            "bt_isolated_quartic_score_square_uniformity_obstructed": True,
            "bt_complete_order_g_four_score_established": False,
            "bt_quartic_power_cancellation_established": False,
            "bt_complete_order_g_four_formula_established": True,
            "bt_complete_order_g_four_uv_noncancellation_established": True,
            "bt_complete_order_g_four_whole_lattice_decided": False,
            "bt_complete_order_g_four_ir_complement_bounded": False,
            "bt_complete_order_g_four_chaos_decomposition_established": True,
            "bt_complete_order_g_four_signed_gate_reduced_to_second_chaos": True,
            "bt_complete_order_g_four_expected_hessian_formula_established": True,
            "bt_complete_order_g_four_conditioning_finite_rank_decomposition_established": True,
            "bt_complete_order_g_four_connected_reorganization_established": True,
            "bt_complete_order_g_four_normalization_alignment_established": True,
            "bt_complete_order_g_four_termwise_alignment_bound_obstructed": True,
            "bt_complete_order_g_four_connected_maximum_loop_rank_two": True,
            "bt_complete_order_g_four_exact_cancellation_established": False,
            "bt_complete_order_g_four_conditioned_maximum_loop_rank_two": True,
            "bt_complete_order_g_four_l4_negative_nonzero_established": True,
            "bt_complete_order_g_four_all_volume_zero_identity_obstructed": True,
            "bt_complete_order_g_four_large_volume_scaling_established": False,
            "bt_complete_order_g_four_general_l_two_loop_formula_established": True,
            "bt_complete_order_g_four_power_tadpoles_canceled": True,
            "bt_complete_order_g_four_factorized_conditioning_log_squared_bound_established": True,
            "bt_complete_order_g_four_factorized_tuned_branch_uniformity_established": True,
            "bt_complete_order_g_four_remaining_fourteen_kernel_bound_established": False,
            "bt_complete_order_g_four_fourteen_to_seven_reduction_established": True,
            "bt_complete_order_g_four_paired_quartic_bound_established": True,
            "bt_complete_order_g_four_negative_nested_L2_carrier_established": True,
            "bt_complete_order_g_four_termwise_tuned_uniformity_obstructed": True,
            "bt_complete_order_g_four_combined_seven_kernel_scaling_established": False,
            "bt_complete_order_g_four_explicit_momentum_kernel_established": False,
            "bt_complete_order_g_four_effective_kernel_bound_established": False,
            "bt_complete_order_g_four_power_survival_established": False,
            "research_programme_lenses_explained": True,
            "coded_wave_observable_reconstruction_certified": True,
            "coded_local_weak_wave_test_class_certified": True,
            "coded_local_weak_wave_all_smooth_tests_covered": False,
            "coded_local_weak_wave_causal_support_proved": False,
            "coded_h2_test_completion_certified": True,
            "coded_h2_represented_smooth_tests_covered": True,
            "coded_h2_full_lf_topology_reconstructed": False,
            "coded_h2_arbitrary_distribution_uniqueness_proved": False,
            "coded_h2_causal_support_proved": False,
            "fixed_support_smooth_to_h2_translator_certified": True,
            "fixed_support_translator_uses_choice": False,
            "support_indexed_name_equivalence_certified": True,
            "support_indexed_full_lf_topology_reconstructed": False,
            "scalar_minkowski_green_certified": True,
            "scalar_minkowski_causal_support_proved": True,
            "scalar_green_promoted_to_weyl_bv": False,
            "scalar_minkowski_biwave_certified": scalar_biwave["claim_flags"]["strict_causal_support_proved"],
            "scalar_biwave_four_zero_data_certified": scalar_biwave["claim_flags"]["four_zero_data_selection_proved"],
            "weyl_bv_dependency_delta_certified": weyl_bv_delta["claim_flags"]["transfer_requirements_classified"],
            "weyl_bv_classical_import_gate_passed": weyl_bv_delta["claim_flags"]["classical_import_gate_passed"],
            "full_weyl_bv_propagator_constructed": weyl_bv_delta["claim_flags"]["full_weyl_bv_propagator_constructed"],
            "weakest_foundation_proved": False,
            "global_physics_implies_choice_theorem": False,
            "axes_independent_proved": False,
            "atlas_exhaustive": False,
            "literature_complete": False,
            "new_lorentzian_claim": True,
            "quantum_lifecycle_promoted": False,
        },
        "does_not_establish": [
            "a universal weakest foundation for physics or Weyl gravity",
            "that physical evidence implies the Axiom of Choice or its negation",
            "that the atlas axes are independent or every coordinate is coherent",
            "literature completeness or absence theorems for reviewed open gaps",
            "representation invariance of the RCA_0 coded-wave upper bound",
            "full-state reconstruction from the single coded wave observable",
            "a uniform H2 name constructor for every bare extensional smooth test without support and rate advice",
            "the unrestricted LF smooth-test topology from the support-indexed represented union",
            "surjectivity of the smooth-test embedding onto the H2 completion",
            "uniqueness among arbitrary distributional weak solutions",
            "a variable-coefficient, curved-spacetime, Weyl, or metric-BV Green operator from the flat scalar 1+1 benchmark",
            "a complete Lorentzian off-shell BV propagator",
            "a BRST-compatible Hadamard state for the full metric BV complex",
            "renormalized Lorentzian time-ordered products or causal perturbative AQFT",
            "restoration of a Lorentzian quantum master equation",
            "promotion of any quantum lifecycle state",
            "reproduction of the Cassini raw-data reduction, likelihood, covariance analysis, or systematic-error budget",
            "a complete standard-GR theory or empirical support for a Weyl-gravity model",
            "a population-level model ranking or complete-theory selection from the NGC 3198 common-fit control",
            "a continuum, empirical, Born-rule, or Lorentzian promotion from the BT Euclidean finite lattice",
            "reflection-positivity failure at every nonzero coupling or in a continuum limit",
            "a volume-uniform BT action-weighted conditional-fiber or one-mode marginal bound",
            "divergence of the BT lowest-mode second moment from the centered pointwise fiber obstruction",
            "divergence of the integrated BT lowest-mode marginal from conditional mass escape on exceptional backgrounds",
            "divergence of the full interacting BT score or moment from the logarithmic leading perturbative coefficient",
            "divergence of the full interacting BT score or moment from the isolated quartic-score square",
            "the unrestricted whole-lattice order-g^4 sign or scaling from fixed-carrier ultraviolet noncancellation",
            "the effective second-chaos kernel bound from the exact Wiener-chaos reduction alone",
            "the explicit BT lattice momentum kernel or its norm bound from the expected-Hessian formula alone",
            "a large-volume M4 sign or scaling law from the exact finite-volume L=4 decision",
            "a bound for the 14 unfactorized two-loop kernels, the full M4 asymptotics, or the interacting H^-1 moment from the factorized log-squared bound",
            "the sign or scaling of the combined seven-kernel sum, complete M4, or the actual interacting H^-1 moment from the isolated negative L^2 carrier",
        ],
        "authorities": authorities,
        "independent_checker": {
            "path": "paper/verify_21_reverse_foundations_claim_map.py",
            "checks": [
                "authority content hashes",
                "authority result identities and dependency tags",
                "atlas counts against source artifacts",
                "generated appendix hash and normalized atlas source",
                "complete literature citations, URLs, artifact statuses, roles, and boundaries",
                "complete local-certificate locators, positive flags, dependency tags, and boundaries",
                "all-record matrix, graph, and strength-ladder usage crosswalk",
                "claim-to-authority dependency boundaries",
                "required paper language and bibliography keys",
                "canonical claim-map digest",
            ],
        },
    }
    for claim in payload["claims"]:
        if claim["claim_id"] == "RF-13-BT-INTERACTING-RECONSTRUCTION-FRONTIER":
            claim["statement"] += (
                " The exact quartic zero-fiber-score kernel is linearly soft, with "
                "derivative -1/3 at a quarter-period fixture, and its isolated free "
                "square grows at least as L^2 after normalization. Since g_L^4 is "
                "only logarithmically small, cubic RG matching alone cannot control "
                "this term. This does not prove divergence: exact cancellation in "
                "the complete order-g^4 composite remains the next gate."
                " The complete normalized order-g^4 background-score formula is now "
                "assembled. On fixed ultraviolet carriers its signed corrections "
                "start at p^4, so they cannot cancel the positive p^2 quartic-square "
                "sector. The unrestricted coefficient remains open because such a "
                "cancellation could still be nonuniform and arise from the shrinking "
                "infrared complement."
                " Wiener-chaos orthogonality further reduces every potentially "
                "negative contribution to the second-chaos projection of one "
                "effective three-leg kernel; a linear-soft weighted norm bound for "
                "that kernel would make the signed cross term negligible and decide "
                "survival of the full power. That norm bound remains open."
                " The remaining projection is now represented by the single expected "
                "Hessian K_E=E_0[D^2E]. The conditioned covariance splits exactly "
                "into a translation-invariant bulk and a rank-one real-cosine "
                "correction: the bulk selects transfer p, the single-rank terms can "
                "also sample transfer 3p, and the double-rank cross term vanishes for "
                "L>=4. This removes the Wick-pairing inventory but does not evaluate "
                "the Fourier kernel or prove its norm bound."
                " The standalone norm route is badly conditioned: the coefficient "
                "multiplying A contains an extensive normalization-aligned mean "
                "whose disconnected cross cancels a matching part of ||D||^2 only "
                "in the complete connected covariance. Exact labeled Wick "
                "enumeration of that connected form leaves only zero-, one-, and "
                "two-loop sums. The bulk table's momentum-forbidden labels do not "
                "by themselves cover rank-one covariance insertions, but an exact "
                "all-volume signed-source audit proves that the conditioned formula "
                "still has maximum loop rank two. Exact rational evaluation gives "
                "M4(4)=-338835474713437/204838502400000, and an independent modular "
                "enumeration proves the same value. This refutes an all-volume zero "
                "identity but does not decide the large-volume sign or scaling."
                " For every integer L>=5, an exact affine-flow atlas combines 96 "
                "source-conserving oriented topology flows into 21 common integrands after "
                "zero-mode removal. Five cancel exactly. In particular, every "
                "power-sized quartic-tadpole square Y_L^2 and bubble-tadpole cross "
                "X_L*Y_L cancels between fixed-p bulk propagators and rank-one "
                "covariances before absolute values. The conditioning-scale "
                "remainder is the positive 162*X_L^2/[N*omega(p)^2], with an exact "
                "O(log(L)^2) bound, so g_L^4 times this sector is bounded on the "
                "certified tuned refinement branch. The fourteen unfactorized "
                "entries reduce exactly to seven inversion pairs. The paired "
                "quartic vertex lies between omega(k)*omega(r)/6 and 19/6 times "
                "that product, and one strictly negative nested pair obeys "
                "T_L<=-(N-1)/[4*N*omega(p)], hence has at least c*L^2 magnitude. "
                "This obstructs termwise tuned-g_L^4 bounds, but not a cancellation "
                "inside the complete seven-kernel sum. Its common power coefficient, "
                "lower-loop recombination, full M4 asymptotics, and the interacting "
                "H^-1 moment remain open."
            )
            break
    payload["canonical_digest"] = canonical_digest(payload)
    return payload


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != expected:
            raise SystemExit(f"stale generated artifact: {OUTPUT.relative_to(ROOT)}")
        print(f"PASS {OUTPUT.relative_to(ROOT)} is current")
        return 0
    OUTPUT.write_text(expected)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

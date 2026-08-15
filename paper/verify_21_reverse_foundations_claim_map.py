#!/usr/bin/env python3
"""Independent structural checker for the paper 21 claim map."""

from __future__ import annotations

import hashlib
import json
import collections
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_MAP = ROOT / "paper/21-reverse-foundations-of-physics-claim-map.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_without_self(data: dict) -> str:
    body = dict(data)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def tex(value: object) -> str:
    text = str(value)
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("×", r"\(\times\)"),
        ("→", r"\(\rightarrow\)"),
        ("—", "---"),
        ("–", "--"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def scientific_tex(value: object) -> str:
    text = tex(value)
    for plain, formula in [
        (r"G\_mu\_nu=0", r"\(G_{\mu\nu}=0\)"),
        ("f(r)=1-2m/r", r"\(f(r)=1-2m/r\)"),
        ("beta=gamma=1", r"\(\beta=\gamma=1\)"),
        ("gamma-1=0", r"\(\gamma-1=0\)"),
        ("1+gamma=2", r"\(1+\gamma=2\)"),
        ("gamma+1", r"\(\gamma+1\)"),
    ]:
        text = text.replace(plain, formula)
    return text


def main() -> int:
    data = json.loads(CLAIM_MAP.read_text())
    require(data["result_id"] == "PAPER21_REVERSE_FOUNDATIONS_INTRODUCTION_V1", "wrong result id")
    require(data["lifecycle"] == "WORKING_DRAFT", "paper must remain a working draft")
    require(data["canonical_digest"] == digest_without_self(data), "canonical digest mismatch")

    for name, authority in data["authorities"].items():
        path = ROOT / authority["path"]
        require(path.is_file(), f"missing authority {name}: {path}")
        require(sha256(path) == authority["sha256"], f"authority hash drift: {name}")
        source = json.loads(path.read_text())
        require(source.get("result_id", source.get("certificate")) == authority["result_id"], f"authority result drift: {name}")
        require(source.get("lifecycle", source.get("lifecycle_state")) == authority["lifecycle"], f"authority lifecycle drift: {name}")
        require(source.get("dependency_tags", []) == authority["dependency_tags"], f"authority tag drift: {name}")

    cube = json.loads((ROOT / data["authorities"]["intersection_cube"]["path"]).read_text())
    site = json.loads((ROOT / data["authorities"]["explorer_snapshot"]["path"]).read_text())
    gr_cassini = json.loads((ROOT / data["authorities"]["gr_cassini_assembly"]["path"]).read_text())
    mannheim_ngc3198 = json.loads((ROOT / data["authorities"]["mannheim_ngc3198_assembly"]["path"]).read_text())
    ngc3198_common_fit = json.loads((ROOT / data["authorities"]["ngc3198_common_fit_comparison"]["path"]).read_text())
    coded_wave_observable = json.loads((ROOT / data["authorities"]["coded_wave_observable_reconstruction"]["path"]).read_text())
    coded_local_weak_wave = json.loads((ROOT / data["authorities"]["coded_local_weak_wave_test_class"]["path"]).read_text())
    coded_h2_test = json.loads((ROOT / data["authorities"]["coded_weak_wave_h2_test_completion"]["path"]).read_text())
    smooth_translator = json.loads((ROOT / data["authorities"]["fixed_support_smooth_to_h2_translator"]["path"]).read_text())
    support_indexed = json.loads((ROOT / data["authorities"]["support_indexed_test_space_comparison"]["path"]).read_text())
    scalar_green = json.loads((ROOT / data["authorities"]["scalar_minkowski_green_choice_audit"]["path"]).read_text())
    strict_q1 = json.loads((ROOT / data["authorities"]["strict_portable_local_q1"]["path"]).read_text())
    strict_q1q2 = json.loads((ROOT / data["authorities"]["strict_local_q1_q2_identity"]["path"]).read_text())
    strict_cyclic = json.loads((ROOT / data["authorities"]["strict_minimal_bv_cyclic_sign_reconciliation"]["path"]).read_text())
    gate_v5 = json.loads((ROOT / data["authorities"]["classical_import_gate_v5"]["path"]).read_text())
    strict_386_transport = json.loads((ROOT / data["authorities"]["strict_386_causal_sign_transport"]["path"]).read_text())
    completion_atlas_v4 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v4"]["path"]).read_text())
    strict_386_endpoint = json.loads((ROOT / data["authorities"]["strict_386_endpoint_q1_content_bridge"]["path"]).read_text())
    completion_atlas_v5 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v5"]["path"]).read_text())
    strict_386_suspension = json.loads((ROOT / data["authorities"]["strict_386_suspended_adjoint_bridge"]["path"]).read_text())
    completion_atlas_v6 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v6"]["path"]).read_text())
    strict_386_pairing = json.loads((ROOT / data["authorities"]["strict_386_component_pairing_serialization"]["path"]).read_text())
    completion_atlas_v7 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v7"]["path"]).read_text())
    strict_386_sign_repair = json.loads((ROOT / data["authorities"]["strict_386_auxiliary_q_sign_repair"]["path"]).read_text())
    completion_atlas_v10 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v10"]["path"]).read_text())
    strict_386_full_q1 = json.loads((ROOT / data["authorities"]["strict_386_full_q1_component_jet_table"]["path"]).read_text())
    completion_atlas_v11 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v11"]["path"]).read_text())
    strict_386_local_sdr = json.loads((ROOT / data["authorities"]["strict_386_local_sdr_component_maps"]["path"]).read_text())
    completion_atlas_v12 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v12"]["path"]).read_text())
    strict_386_canonical_shear = json.loads((ROOT / data["authorities"]["strict_386_canonical_shear_component_jets"]["path"]).read_text())
    completion_atlas_v13 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v13"]["path"]).read_text())
    strict_386_graph_sdr = json.loads((ROOT / data["authorities"]["strict_386_graph_q1_sdr_component_jets"]["path"]).read_text())
    completion_atlas_v14 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v14"]["path"]).read_text())
    strict_386_green_name = json.loads((ROOT / data["authorities"]["strict_386_graph_green_action_name"]["path"]).read_text())
    strict_386_unary_causal = json.loads((ROOT / data["authorities"]["strict_386_unary_causal_common_snapshot"]["path"]).read_text())
    completion_atlas_v15 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v15"]["path"]).read_text())
    strict_386_full_d = json.loads((ROOT / data["authorities"]["strict_386_full_d_action"]["path"]).read_text())
    gate_v6 = json.loads((ROOT / data["authorities"]["classical_import_gate_v6"]["path"]).read_text())
    completion_atlas_v16 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v16"]["path"]).read_text())
    strict_386_q2_preflight = json.loads((ROOT / data["authorities"]["strict_386_stabilized_q2_lift_preflight"]["path"]).read_text())
    gate_v7 = json.loads((ROOT / data["authorities"]["classical_import_gate_v7"]["path"]).read_text())
    completion_atlas_v17 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v17"]["path"]).read_text())
    strict_386_q2_green = json.loads((ROOT / data["authorities"]["strict_386_stabilized_q2_green_composition_preflight"]["path"]).read_text())
    completion_atlas_v18 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v18"]["path"]).read_text())
    strict_386_recursive_trees = json.loads((ROOT / data["authorities"]["strict_386_recursive_causal_tree_domains"]["path"]).read_text())
    completion_atlas_v19 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v19"]["path"]).read_text())
    strict_386_formal = json.loads((ROOT / data["authorities"]["strict_386_polarized_formal_moller_coefficients"]["path"]).read_text())
    completion_atlas_v20 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v20"]["path"]).read_text())
    strict_386_field_inverse = json.loads((ROOT / data["authorities"]["strict_386_field_equation_green_quotient_inverse"]["path"]).read_text())
    completion_atlas_v21 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v21"]["path"]).read_text())
    strict_386_quadratic_obstruction = json.loads((ROOT / data["authorities"]["strict_386_quadratic_truncation_lambda2_source_obstruction"]["path"]).read_text())
    completion_atlas_v22 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v22"]["path"]).read_text())
    strict_386_q3_witness = json.loads((ROOT / data["authorities"]["strict_386_pure_weyl_q3_witness"]["path"]).read_text())
    completion_atlas_v23 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v23"]["path"]).read_text())
    classical_minimal_q3 = json.loads((ROOT / data["authorities"]["classical_minimal_bv_q3_export"]["path"]).read_text())
    strict_minimal_q3 = json.loads((ROOT / data["authorities"]["strict_pure_weyl_minimal_bv_q3_import"]["path"]).read_text())
    strict_minimal_arity3 = json.loads((ROOT / data["authorities"]["strict_minimal_bv_arity_three_identity"]["path"]).read_text())
    strict_minimal_q3_cyclicity = json.loads((ROOT / data["authorities"]["strict_minimal_bv_q3_cyclicity"]["path"]).read_text())
    completion_atlas_v24 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v24"]["path"]).read_text())
    strict_386_q3_preflight = json.loads((ROOT / data["authorities"]["strict_386_stabilized_q3_lift_preflight"]["path"]).read_text())
    completion_atlas_v25 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v25"]["path"]).read_text())
    classical_aux_cubic = json.loads((ROOT / data["authorities"]["classical_ordinary_derivative_auxiliary_cubic_export"]["path"]).read_text())
    strict_identity_obstruction = json.loads((ROOT / data["authorities"]["strict_386_nonminimal_theory_identity_obstruction"]["path"]).read_text())
    gate_v8 = json.loads((ROOT / data["authorities"]["classical_import_gate_v8"]["path"]).read_text())
    completion_atlas_v26 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v26"]["path"]).read_text())
    classical_quadratic_map = json.loads((ROOT / data["authorities"]["classical_quadratic_auxiliary_elimination_map"]["path"]).read_text())
    strict_quadratic_channel = json.loads((ROOT / data["authorities"]["strict_386_quadratic_auxiliary_elimination_channel"]["path"]).read_text())
    gate_v9 = json.loads((ROOT / data["authorities"]["classical_import_gate_v9"]["path"]).read_text())
    completion_atlas_v27 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v27"]["path"]).read_text())
    classical_shifted_cubic = json.loads((ROOT / data["authorities"]["classical_shifted_auxiliary_cubic_inventory"]["path"]).read_text())
    strict_shifted_cubic = json.loads((ROOT / data["authorities"]["strict_386_shifted_auxiliary_cubic_inventory"]["path"]).read_text())
    gate_v10 = json.loads((ROOT / data["authorities"]["classical_import_gate_v10"]["path"]).read_text())
    completion_atlas_v28 = json.loads((ROOT / data["authorities"]["lorentzian_weyl_bv_completion_atlas_v28"]["path"]).read_text())
    bt_euclidean = json.loads((ROOT / data["authorities"]["bt_euclidean_import"]["path"]).read_text())
    bt_free_obstruction = json.loads((ROOT / data["authorities"]["bt_free_reconstruction_obstruction"]["path"]).read_text())
    bt_interacting_os = json.loads((ROOT / data["authorities"]["bt_interacting_os_preflight"]["path"]).read_text())
    bt_lambda04_os = json.loads((ROOT / data["authorities"]["bt_lambda04_os_kernel_obstruction"]["path"]).read_text())
    bt_all_coupling_os = json.loads((ROOT / data["authorities"]["bt_all_coupling_os_kernel_obstruction"]["path"]).read_text())
    bt_action_weight = json.loads((ROOT / data["authorities"]["bt_action_weight_virial_obstruction"]["path"]).read_text())
    bt_affine_virial = json.loads((ROOT / data["authorities"]["bt_affine_virial_action_density"]["path"]).read_text())
    bt_orthogonal_hessian = json.loads((ROOT / data["authorities"]["bt_orthogonal_hessian_block_obstruction"]["path"]).read_text())
    bt_residual_pushforward = json.loads((ROOT / data["authorities"]["bt_residual_spectrahedral_pushforward"]["path"]).read_text())
    bt_residual_curvature = json.loads((ROOT / data["authorities"]["bt_residual_boundary_curvature_obstruction"]["path"]).read_text())
    bt_residual_tilt = json.loads((ROOT / data["authorities"]["bt_residual_tilt_jacobian_cancellation"]["path"]).read_text())
    bt_centered_fiber = json.loads((ROOT / data["authorities"]["bt_centered_fiber_domination_obstruction"]["path"]).read_text())
    bt_conditional_escape = json.loads((ROOT / data["authorities"]["bt_conditional_mass_escape_obstruction"]["path"]).read_text())
    bt_runaway_width = json.loads((ROOT / data["authorities"]["bt_runaway_fiber_width_bound"]["path"]).read_text())
    bt_separable_curvature = json.loads((ROOT / data["authorities"]["bt_separable_lowest_mode_curvature"]["path"]).read_text())
    bt_all_background_curvature = json.loads((ROOT / data["authorities"]["bt_all_background_lowest_mode_curvature"]["path"]).read_text())
    bt_center_score = json.loads((ROOT / data["authorities"]["bt_annealed_center_score_reduction"]["path"]).read_text())
    bt_cubic_score = json.loads((ROOT / data["authorities"]["bt_cubic_score_log_obstruction"]["path"]).read_text())
    bt_score_rg = json.loads((ROOT / data["authorities"]["bt_score_rg_matching"]["path"]).read_text())
    bt_ward_weight = json.loads((ROOT / data["authorities"]["bt_zero_fiber_ward_weight_obstruction"]["path"]).read_text())
    bt_quartic_score = json.loads((ROOT / data["authorities"]["bt_quartic_score_power_obstruction"]["path"]).read_text())
    bt_complete_g4 = json.loads((ROOT / data["authorities"]["bt_complete_g4_uv_noncancellation"]["path"]).read_text())
    bt_g4_chaos = json.loads((ROOT / data["authorities"]["bt_complete_g4_chaos_gate"]["path"]).read_text())
    bt_g4_hessian = json.loads((ROOT / data["authorities"]["bt_complete_g4_effective_hessian"]["path"]).read_text())
    bt_g4_connected = json.loads((ROOT / data["authorities"]["bt_complete_g4_connected_normalization"]["path"]).read_text())
    bt_g4_l4 = json.loads((ROOT / data["authorities"]["bt_complete_g4_l4_decision"]["path"]).read_text())
    bt_g4_general_l = json.loads((ROOT / data["authorities"]["bt_complete_g4_general_l_two_loop"]["path"]).read_text())
    bt_g4_seven = json.loads((ROOT / data["authorities"]["bt_complete_g4_seven_kernel_reduction"]["path"]).read_text())
    bt_g4_subpower = json.loads((ROOT / data["authorities"]["bt_complete_g4_subpower_pair_bounds"]["path"]).read_text())
    bt_g4_linear = json.loads((ROOT / data["authorities"]["bt_complete_g4_linear_pair_bounds"]["path"]).read_text())
    bt_g4_two_pair = json.loads((ROOT / data["authorities"]["bt_complete_g4_two_pair_coefficient_normal_form"]["path"]).read_text())
    bt_g4_two_pair_noncancellation = json.loads((ROOT / data["authorities"]["bt_complete_g4_two_pair_noncancellation"]["path"]).read_text())
    bt_g4_lower_loops = json.loads((ROOT / data["authorities"]["bt_complete_g4_lower_loop_bounds"]["path"]).read_text())
    bt_tuned_remainder = json.loads((ROOT / data["authorities"]["bt_tuned_remainder_compensation"]["path"]).read_text())
    bt_radial_convexity = json.loads((ROOT / data["authorities"]["bt_radial_convexity_obstruction"]["path"]).read_text())
    bt_log_bubble = json.loads((ROOT / data["authorities"]["bt_log_bubble_virial_no_go"]["path"]).read_text())
    bt_bubble_balance = json.loads((ROOT / data["authorities"]["bt_log_bubble_entropy_soft_score_balance"]["path"]).read_text())
    bt_full_phase_current = json.loads((ROOT / data["authorities"]["bt_full_phase_current_gate"]["path"]).read_text())
    bt_weighted_current_v2 = json.loads((ROOT / data["authorities"]["bt_full_phase_weighted_current_gate_v2"]["path"]).read_text())
    bt_corrector_energy_no_go = json.loads((ROOT / data["authorities"]["bt_flux_corrector_pointwise_energy_no_go"]["path"]).read_text())
    bt_corrector_slab_fiber = json.loads((ROOT / data["authorities"]["bt_corrector_slab_fiber_stability"]["path"]).read_text())
    bt_corrector_slab_cylinder = json.loads((ROOT / data["authorities"]["bt_corrector_slab_cylinder_suppression"]["path"]).read_text())
    dims = cube["dimensions"]
    atlas = data["atlas_snapshot"]
    require(atlas["axis_sizes"] == [6, 6, 16], "unexpected axis sizes")
    require(atlas["cartesian_total"] == 576, "unexpected Cartesian total")
    require(atlas["emitted_cells"] == dims["emitted_cells"] == 576, "emitted-cell mismatch")
    require(atlas["coverage_classified_cells"] == dims["coverage_classified_cells"] == 576, "classified-cell mismatch")
    require(sum(atlas["emitted_status_counts"].values()) == atlas["emitted_cells"], "status counts do not cover emitted cells")
    require(atlas["synthetic_complements"] == 0, "synthetic complement mismatch")
    require(atlas["total_not_mapped_in_explorer"] == site["counts"]["not_mapped"] == 0, "explorer not-mapped mismatch")
    require(atlas["reviewed_open_gaps"] == site["counts"]["reviewed_gap"] == 169, "reviewed-gap mismatch")
    require(atlas["evidence_records"] == site["counts"]["evidence_records"] == 83, "evidence-record mismatch")
    require(atlas["literature_records"] == 51, "literature-record mismatch")
    require(atlas["local_result_records"] == 32, "local-result-record mismatch")
    require(atlas["content_pinned_literature"] == 39, "content-pinned literature mismatch")
    require(atlas["metadata_only_literature"] == 12, "metadata-only literature mismatch")
    require(atlas["evidence_records_used_by_matrix"] == 83, "matrix evidence usage is incomplete")
    require(atlas["migration_pending_cells"] == 0, "migration must remain fully reviewed")
    require(atlas["all_cells_assessed"] is True, "full-surface assessment flag is not certified")
    require(atlas["coded_wave_observable_cutoff"] == coded_wave_observable["cutoff_theorem"]["cutoff"] == "N(k)=k+ell(K)+1", "coded observable cutoff drift")
    require(atlas["coded_wave_observable_full_state_reconstruction"] is coded_wave_observable["claim_flags"]["full_state_reconstruction_proved"] is False, "coded observable promoted to full-state reconstruction")
    require(atlas["coded_local_weak_wave_basis_tests"] == coded_local_weak_wave["localized_test_class"]["basis_size"] == 10, "localized weak-wave basis count drift")
    require(atlas["coded_local_weak_wave_separation_rank"] == coded_local_weak_wave["separation"]["rank"] == 10, "localized weak-wave rank drift")
    require(atlas["coded_local_weak_wave_all_smooth_tests"] is coded_local_weak_wave["claim_flags"]["all_smooth_tests_covered"] is False, "finite test span promoted to all smooth tests")
    require(atlas["coded_local_weak_wave_causal_support"] is coded_local_weak_wave["claim_flags"]["strict_causal_support_proved"] is False, "coefficient weak identity promoted to causal support")
    require(atlas["coded_h2_test_derivatives"] == len(coded_h2_test["rational_test_codes"]["derivative_multiindices"]) == 6, "H2 derivative carrier drift")
    require(atlas["coded_h2_test_density_status"] == coded_h2_test["named_completion"]["density_status"] == "BY_DECLARED_REPRESENTATION", "H2 density status drift")
    require(atlas["coded_h2_represented_smooth_tests_covered"] is coded_h2_test["claim_flags"]["represented_smooth_tests_covered"] is True, "represented smooth-test coverage missing")
    require(atlas["coded_h2_full_lf_topology"] is coded_h2_test["claim_flags"]["full_lf_test_topology_reconstructed"] is False, "named H2 completion promoted to LF topology")
    require(atlas["coded_h2_arbitrary_distribution_uniqueness"] is coded_h2_test["claim_flags"]["uniqueness_among_arbitrary_distributions_proved"] is False, "energy-image uniqueness promoted to arbitrary distributions")
    require(atlas["coded_h2_causal_support"] is coded_h2_test["claim_flags"]["strict_causal_support_proved"] is False, "named weak solution promoted to causal support")
    require(atlas["coded_h2_fixture_wave_offsets"] == {item["id"]: item["binary_cutoff_offsets"]["scalar_wave"] for item in coded_h2_test["fixtures"]}, "H2 fixture cutoff drift")
    require(atlas["smooth_translator_fixture_shifts"] == {f"{item['margin'][0]}/{item['margin'][1]}": item["index_shift"] for item in smooth_translator["fixtures"]}, "smooth translator shift drift")
    require(atlas["smooth_translator_choice_used"] is smooth_translator["claim_flags"]["choice_principle_used"] is False, "smooth translator choice boundary drift")
    require(atlas["support_indexed_stages"] == len(support_indexed["fixtures"]) == 6, "support-indexed stage count drift")
    require(atlas["support_indexed_inclusion_checks"] == len(support_indexed["inclusion_checks"]) == 15, "support-indexed inclusion count drift")
    require(atlas["support_indexed_name_equivalence"] is support_indexed["claim_flags"]["conventional_and_tagged_names_equivalent"] is True, "support-indexed name equivalence missing")
    require(atlas["support_indexed_full_lf_topology"] is support_indexed["claim_flags"]["full_lf_locally_convex_topology_identified"] is False, "represented union promoted to LF topology")
    require(atlas["scalar_green_fixtures"] == len(scalar_green["fixtures"]) == 4, "scalar Green fixture drift")
    require(atlas["scalar_green_support_samples"] == len(scalar_green["support_samples"]) == 8, "scalar Green support-sample drift")
    require(atlas["scalar_green_causal_support"] is scalar_green["claim_flags"]["strict_causal_support_proved"] is True, "scalar causal support missing")
    require(atlas["scalar_green_weyl_bv_propagator"] is scalar_green["claim_flags"]["weyl_bv_propagator_constructed"] is False, "scalar Green result promoted to Weyl/BV")
    require(atlas["bt_euclidean_direct_capabilities"] == 5, "BT direct-capability count mismatch")
    require(atlas["bt_euclidean_reconstruction_status"] == "PRIORITY_GAP", "BT reconstruction boundary mismatch")
    require(atlas["bt_euclidean_numerical_status"] == "COARSE_REPRODUCTION_ONLY", "BT numerical status mismatch")
    require(atlas["bt_euclidean_carrier_relation"] == "INCOMPATIBLE", "BT carrier relation mismatch")
    require(bt_euclidean["claim_flags"]["continuum_reconstruction_established"] is False, "BT continuum claim promoted")
    require(atlas["bt_free_os_reflected_norm"] == {"numerator": -1, "denominator": 1296}, "BT reflected norm drift")
    require(atlas["bt_free_os_near_zero_status"] == "OBSTRUCTED_ON_SOME_OPEN_INTERVAL", "BT near-zero OS status drift")
    require(atlas["bt_free_os_lambda_0p4_status"] == "OPEN", "BT lambda=0.4 status promoted")
    require(atlas["bt_free_h_minus_one_bound"] == {"numerator": 15, "denominator": 32}, "BT H^-1 bound drift")
    require(atlas["bt_free_l2_status"] == "OBSTRUCTED", "BT L2 obstruction drift")
    require(bt_free_obstruction["disposition"]["continuum_limit"] == "NOT_ESTABLISHED", "BT free estimate promoted to continuum")
    require(atlas["bt_interacting_os_numerical_status"] == "TWO_SAMPLER_NEGATIVE_SIGN_SUPPORT_NOT_EXACT", "BT interacting numerical status drift")
    require(abs(atlas["bt_interacting_os_local_z"] + 2.5326776073871837) < 1e-12, "BT local sign score drift")
    require(abs(atlas["bt_interacting_os_hmc_z"] + 6.254432004803571) < 1e-12, "BT HMC sign score drift")
    require(abs(atlas["bt_interacting_os_cross_sampler_z"] + 0.6439112862910602) < 1e-12, "BT cross-sampler score drift")
    require(bt_interacting_os["disposition"]["ordinary_os_reflection_positivity_at_lambda_0p4"] == "OPEN", "BT numerical preflight promoted to exact OS obstruction")
    require(atlas["bt_lambda_0p4_exact_os_status"] == bt_lambda04_os["disposition"]["ordinary_os_reflection_positivity_at_lambda_0p4"] == "OBSTRUCTED", "BT exact lambda=0.4 OS status drift")
    require(atlas["bt_all_nonzero_coupling_even_volume_os_status"] == bt_all_coupling_os["scope_disposition"]["ordinary_os_at_every_lambda_nonzero_even_L_at_least_6"] == "OBSTRUCTED", "BT all-coupling even-volume OS status drift")
    require(atlas["bt_continuum_fixed_observable_os_status"] == bt_all_coupling_os["scope_disposition"]["continuum_os_for_fixed_cutoff_independent_observables"] == "NOT_DECIDED", "BT fixed-observable continuum OS boundary drift")
    require(atlas["bt_interacting_uniform_h_minus_one_status"] == bt_action_weight["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"] == "OPEN", "BT interacting uniform estimate promoted")
    require(atlas["bt_pointwise_action_weight_necessary_exponent"] == "AT_LEAST_ONE_HALF", "BT necessary action-weight exponent drift")
    require(atlas["bt_pointwise_virial_constant_two_status"] == "POINTWISE_VIRIAL_CONSTANT_TWO_OBSTRUCTED", "BT virial obstruction drift")
    require(atlas["bt_affine_virial_status"] == bt_affine_virial["method_disposition"]["affine_pointwise_virial_bound"] == "PROVED", "BT affine virial theorem drift")
    require(atlas["bt_actual_action_density_status"] == bt_affine_virial["method_disposition"]["actual_uniform_action_density_moment"] == "PROVED", "BT actual action-density theorem drift")
    require(atlas["bt_actual_half_action_factor_status"] == bt_affine_virial["method_disposition"]["actual_annealed_half_action_density_factor"] == "PROVED", "BT annealed half-action theorem drift")
    require(atlas["bt_lambda_0p4_action_density_bound"] == {"numerator": 1222, "denominator": 25}, "BT action-density constant drift")
    require(bt_affine_virial["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"] == "OPEN", "BT affine theorem promoted to H^-1")
    require(atlas["bt_global_orthogonal_hessian_block_status"] == bt_orthogonal_hessian["method_disposition"]["global_orthogonal_hessian_block_positivity"] == "OBSTRUCTED", "BT orthogonal Hessian obstruction drift")
    require(atlas["bt_pointwise_half_action_curvature_route_status"] == bt_orthogonal_hessian["method_disposition"]["pointwise_half_action_curvature_route"] == "OBSTRUCTED_AS_FORMULATED", "BT half-action curvature disposition drift")
    require(atlas["bt_orthogonal_hessian_cell_value"] == {"numerator": -13880, "denominator": 81}, "BT orthogonal Hessian value drift")
    require(bt_orthogonal_hessian["method_disposition"]["direct_normalized_low_mode_marginal"] == "OPEN", "BT direct marginal promoted")
    require(bt_orthogonal_hessian["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"] == "OPEN", "BT Hessian obstruction promoted to H^-1 failure")
    require(atlas["bt_residual_boundary_coordinate_status"] == bt_residual_pushforward["method_disposition"]["residual_spectrahedral_boundary_coordinates"] == "PROVED", "BT residual boundary coordinate theorem drift")
    require(atlas["bt_residual_tree_jacobian_status"] == bt_residual_pushforward["method_disposition"]["ground_state_tree_jacobian"] == "PROVED", "BT residual tree Jacobian theorem drift")
    require(atlas["bt_residual_entropy_jacobian_minimum_status"] == bt_residual_pushforward["method_disposition"]["vertex_transitive_entropy_jacobian_minimum"] == "PROVED", "BT residual entropy Jacobian minimum drift")
    require(atlas["bt_residual_cycle_jacobian"] == bt_residual_pushforward["exact_cycle_fixture"]["restricted_jacobian"] == {"numerator": 85, "denominator": 2}, "BT residual C4 Jacobian drift")
    require(atlas["bt_normalized_lowest_mode_marginal_status"] == bt_residual_pushforward["method_disposition"]["normalized_lowest_mode_marginal_bound"] == "OPEN", "BT normalized lowest-mode marginal promoted")
    require(bt_residual_pushforward["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"] == "OPEN", "BT residual reformulation promoted to H^-1 theorem")
    require(bt_residual_pushforward["foundational_dependency_cut"]["weakest_base_or_reversal"] == "NOT_ESTABLISHED", "BT residual dependency cut promoted to reversal")
    require(atlas["bt_residual_pointwise_strict_convexity_status"] == bt_residual_curvature["method_disposition"]["pointwise_strict_convexity"] == "PROVED", "BT residual strict convexity theorem drift")
    require(atlas["bt_residual_uniform_curvature_status"] == bt_residual_curvature["method_disposition"]["uniform_positive_principal_curvature"] == "OBSTRUCTED", "BT residual uniform-curvature obstruction drift")
    require(atlas["bt_residual_weighted_mean_curvature_status"] == bt_residual_curvature["method_disposition"]["global_positive_gaussian_weighted_mean_curvature"] == "OBSTRUCTED_AT_LAMBDA_0P4", "BT residual weighted-mean-curvature obstruction drift")
    require(atlas["bt_residual_trial_curvature_q2"] == bt_residual_curvature["lambda_point_four_fixture"]["trial_normal_curvature"] == {"numerator": 80, "denominator": 2601}, "BT residual q=2 trial curvature drift")
    require(atlas["bt_residual_weighted_mean_curvature_q2"] == bt_residual_curvature["lambda_point_four_fixture"]["gaussian_weighted_mean_curvature"] == {"numerator": -398039, "denominator": 88434}, "BT residual q=2 weighted mean curvature drift")
    require(bt_residual_curvature["method_disposition"]["other_boundary_or_intrinsic_inequalities"] == "NOT_ASSESSED", "BT boundary obstruction widened to other inequalities")
    require(bt_residual_curvature["method_disposition"]["normalized_lowest_mode_marginal_bound"] == "OPEN", "BT boundary obstruction promoted to marginal result")
    require(bt_residual_curvature["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"] == "OPEN", "BT boundary obstruction promoted to H^-1 result")
    require(atlas["bt_residual_induced_tilt_surface_jacobian_status"] == bt_residual_tilt["method_disposition"]["induced_tilt_surface_jacobian"] == "PROVED", "BT induced tilt Jacobian theorem drift")
    require(atlas["bt_residual_inverse_tree_jacobian_cancellation_status"] == bt_residual_tilt["method_disposition"]["inverse_tree_jacobian_cancellation"] == "PROVED", "BT inverse tree-Jacobian cancellation drift")
    require(atlas["bt_residual_tree_log_convexity_tilt_status"] == bt_residual_tilt["method_disposition"]["tree_log_convexity_as_extra_tilt_confinement"] == "OBSTRUCTED", "BT tree log-convexity tilt disposition drift")
    require(atlas["bt_direct_action_fiber_bound_status"] == bt_residual_tilt["method_disposition"]["direct_action_difference_or_fiber_ratio_bound"] == "OPEN", "BT action-fiber bound promoted")
    require(atlas["bt_residual_tilt_surface_ratio_c4"] == bt_residual_tilt["exact_cycle_tilt"]["surface_jacobian_ratio"] == {"numerator": 9, "denominator": 10}, "BT residual C4 tilt surface ratio drift")
    require(atlas["bt_residual_tilt_inverse_density_ratio_c4"] == bt_residual_tilt["exact_cycle_tilt"]["inverse_density_jacobian_ratio"] == {"numerator": 10, "denominator": 9}, "BT residual C4 inverse density ratio drift")
    require(atlas["bt_residual_tilt_boltzmann_gap_c4"] == bt_residual_tilt["exact_cycle_tilt"]["boltzmann_exponent_gap"] == {"numerator": 5325, "denominator": 128}, "BT residual C4 Boltzmann gap drift")
    require(bt_residual_tilt["method_disposition"]["normalized_lowest_mode_marginal_bound"] == "OPEN", "BT tilt reduction promoted to marginal theorem")
    require(bt_residual_tilt["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"] == "OPEN", "BT tilt reduction promoted to H^-1 theorem")
    require(bt_residual_tilt["foundational_dependency_cut"]["weakest_base_or_reversal"] == "NOT_ESTABLISHED", "BT tilt dependency cut promoted to reversal")
    require(atlas["bt_centered_fiber_relative_domination_status"] == bt_centered_fiber["method_disposition"]["centered_pointwise_relative_action_domination"] == "OBSTRUCTED", "BT centered relative-action obstruction drift")
    require(atlas["bt_centered_fiber_boltzmann_status"] == bt_centered_fiber["method_disposition"]["centered_pointwise_boltzmann_ratio_bound"] == "OBSTRUCTED", "BT centered Boltzmann obstruction drift")
    require(atlas["bt_integrated_lowest_mode_marginal_evenness_status"] == bt_centered_fiber["method_disposition"]["integrated_lowest_mode_marginal_evenness"] == "PROVED", "BT integrated marginal evenness drift")
    require(atlas["bt_annealed_recentered_fiber_status"] == bt_centered_fiber["method_disposition"]["annealed_or_recentered_fiber_ratio_bound"] == "OPEN", "BT annealed fiber bound promoted")
    require(atlas["bt_centered_fiber_n1_action_ratio"] == bt_centered_fiber["exact_n1_fixture"]["per_spatial_site_action_ratio"] == {"numerator": 2627836, "denominator": 8346171}, "BT centered n=1 action ratio drift")
    require(atlas["bt_centered_fiber_all_n_ratio_bound"] == "A(eta_n+t_n h)/A(eta_n)<=9/(4*x^2)=9/(4*4^n)", "BT all-n centered fiber bound drift")
    require(bt_centered_fiber["method_disposition"]["normalized_lowest_mode_second_moment_bound"] == "OPEN", "BT centered fiber obstruction promoted to a marginal moment theorem")
    require(bt_centered_fiber["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"] == "OPEN", "BT centered fiber obstruction promoted to H^-1")
    require(atlas["bt_conditional_mass_escape_status"] == bt_conditional_escape["method_disposition"]["conditional_mass_escape_on_exact_family"] == "PROVED", "BT conditional mass-escape theorem drift")
    require(atlas["bt_uniform_raw_conditional_moment_status"] == bt_conditional_escape["method_disposition"]["uniform_backgroundwise_raw_conditional_second_moment"] == "OBSTRUCTED", "BT raw conditional-moment obstruction drift")
    require(atlas["bt_uniform_recentered_conditional_variance_status"] == bt_conditional_escape["method_disposition"]["uniform_recentered_conditional_variance"] == "OPEN", "BT recentered conditional variance promoted")
    require(atlas["bt_annealed_center_second_moment_status"] == bt_conditional_escape["method_disposition"]["annealed_center_second_moment"] == "OPEN", "BT annealed center moment promoted")
    require(atlas["bt_conditional_escape_m2_tail_exponent"] == bt_conditional_escape["exact_m2_fixture"]["binary_tail_exponent"], "BT conditional escape fixture drift")
    require(bt_conditional_escape["method_disposition"]["normalized_lowest_mode_second_moment"] == "OPEN", "BT conditional escape promoted to integrated marginal theorem")
    require(bt_conditional_escape["method_disposition"]["actual_interacting_h_minus_one_second_moment"] == "OPEN", "BT conditional escape promoted to H^-1 theorem")
    require(atlas["bt_runaway_family_recentered_variance_status"] == bt_runaway_width["method_disposition"]["runaway_family_recentered_conditional_variance"] == "PROVED", "BT runaway-family width theorem drift")
    require(atlas["bt_runaway_family_curvature_lower_bound"] == bt_runaway_width["uniform_lower_bound"]["lower_bound"] == {"numerator": 115, "denominator": 4}, "BT runaway-family curvature bound drift")
    require(atlas["bt_runaway_family_conditional_mean_escape_status"] == bt_runaway_width["method_disposition"]["runaway_family_conditional_mean_escape"] == "PROVED", "BT runaway-family conditional-mean escape drift")
    require(atlas["bt_all_background_recentered_variance_status"] == bt_runaway_width["method_disposition"]["all_background_uniform_recentered_conditional_variance"] == "OPEN", "BT exact-family width theorem widened to all backgrounds")
    require(bt_runaway_width["method_disposition"]["annealed_center_second_moment"] == "OPEN", "BT runaway-family theorem promoted to annealed center bound")
    require(bt_runaway_width["method_disposition"]["actual_interacting_h_minus_one_second_moment"] == "OPEN", "BT runaway-family theorem promoted to H^-1")
    require(atlas["bt_separable_lowest_mode_curvature_status"] == bt_separable_curvature["method_disposition"]["separable_background_lowest_mode_curvature"] == "PROVED", "BT separable curvature theorem drift")
    require(atlas["bt_separable_conditional_variance_status"] == bt_separable_curvature["method_disposition"]["separable_background_conditional_variance"] == "PROVED", "BT separable conditional variance drift")
    require(atlas["bt_correlated_spatial_remainder_status"] == bt_separable_curvature["method_disposition"]["all_background_spatial_remainder_nonnegative"] == "OBSTRUCTED", "BT correlated remainder obstruction drift")
    require(atlas["bt_correlated_spatial_remainder_fixture"] == {"numerator": -456623975, "denominator": 262144}, "BT correlated remainder fixture drift")
    require(bt_separable_curvature["method_disposition"]["all_background_recentered_conditional_variance"] == "OPEN", "BT separable theorem widened to all backgrounds")
    require(bt_separable_curvature["method_disposition"]["actual_interacting_h_minus_one_second_moment"] == "OPEN", "BT separable theorem promoted to H^-1")
    require(atlas["bt_all_background_lowest_mode_curvature_status"] == bt_all_background_curvature["method_disposition"]["all_background_lowest_mode_strong_convexity"] == "PROVED", "BT all-background curvature theorem drift")
    require(atlas["bt_all_background_conditional_variance_status"] == bt_all_background_curvature["method_disposition"]["all_background_uniform_recentered_conditional_variance"] == "PROVED", "BT all-background conditional variance drift")
    require(atlas["bt_all_background_curvature_constant"] == {"numerator": 2, "denominator": 9}, "BT all-background curvature constant drift")
    require(atlas["bt_all_background_variance_constant"] == {"numerator": 9, "denominator": 2}, "BT all-background variance constant drift")
    require(atlas["bt_annealed_center_after_width_status"] == bt_all_background_curvature["method_disposition"]["annealed_center_second_moment"] == "OPEN", "BT annealed center promoted after width theorem")
    require(bt_all_background_curvature["method_disposition"]["normalized_lowest_mode_second_moment"] == "OPEN", "BT width theorem promoted to normalized marginal")
    require(bt_all_background_curvature["method_disposition"]["actual_interacting_h_minus_one_second_moment"] == "OPEN", "BT width theorem promoted to H^-1")
    require(atlas["bt_center_to_score_reduction_status"] == bt_center_score["method_disposition"]["annealed_center_to_zero_fiber_score_reduction"] == "PROVED", "BT center-to-score reduction drift")
    require(atlas["bt_center_score_bound_status"] == bt_center_score["method_disposition"]["annealed_zero_fiber_score_bound"] == "OPEN", "BT numerical center diagnostic promoted to a score theorem")
    require(atlas["bt_center_score_integrated_moment_status"] == bt_center_score["method_disposition"]["normalized_lowest_mode_second_moment"] == "OPEN", "BT center reduction promoted to an integrated moment")
    require(atlas["bt_cubic_soft_leg_status"] == bt_cubic_score["method_disposition"]["lattice_cubic_soft_leg_factor"] == "PROVED", "BT cubic soft-leg factor drift")
    require(atlas["bt_cubic_fixed_order_uniform_score_status"] == bt_cubic_score["method_disposition"]["fixed_bare_coupling_coefficientwise_uniform_score_proof"] == "OBSTRUCTED_AS_FORMULATED", "BT fixed-order score obstruction drift")
    require(atlas["bt_cubic_nonperturbative_score_status"] == bt_cubic_score["method_disposition"]["nonperturbative_annealed_zero_fiber_score_bound"] == "OPEN", "BT fixed-order obstruction promoted to nonperturbative failure")
    require(atlas["bt_cubic_dyadic_block_lower_bound"] == {"numerator": 1, "denominator": 4665600}, "BT cubic dyadic lower-bound constant drift")
    require(bt_cubic_score["method_disposition"]["actual_interacting_h_minus_one_second_moment"] == "OPEN", "BT cubic coefficient obstruction promoted to H^-1 failure")
    require(atlas["bt_score_log_residue_status"] == bt_score_rg["method_disposition"]["lattice_score_logarithmic_residue"] == "PROVED", "BT score logarithmic residue drift")
    require(atlas["bt_rg_matched_leading_score_status"] == bt_score_rg["method_disposition"]["rg_matched_leading_score_uniformity"] == "RESTORED_AT_LEADING_LOG", "BT RG-matched leading score status drift")
    require(atlas["bt_rg_matched_leading_score_limit"] == bt_score_rg["matched_refinement"]["score_limit_exact"] == {"numerator": 1, "denominator": 2}, "BT RG-matched score limit drift")
    require(atlas["bt_fixed_spacing_large_volume_score_status"] == bt_score_rg["method_disposition"]["fixed_spacing_large_volume_score_bound"] == "OPEN", "BT matched refinement imported into fixed-spacing volume")
    require(atlas["bt_rg_nonperturbative_score_status"] == bt_score_rg["method_disposition"]["nonperturbative_annealed_zero_fiber_score_bound"] == "OPEN", "BT leading RG match promoted to a Gibbs theorem")
    require(bt_score_rg["method_disposition"]["actual_interacting_h_minus_one_second_moment"] == "OPEN", "BT leading RG match promoted to H^-1")
    require(atlas["bt_ordinary_eom_score_identity_status"] == bt_score_rg["method_disposition"]["ordinary_finite_lattice_eom_score_identity"] == "PROVED", "BT ordinary EOM score identity drift")
    require(atlas["bt_eom_to_zero_fiber_transfer_status"] == bt_score_rg["method_disposition"]["ordinary_eom_to_zero_fiber_score_transfer"] == "OBSTRUCTED_AS_A_LOGICAL_INFERENCE", "BT EOM score transferred to zero fiber")
    require(atlas["bt_specific_zero_fiber_ward_status"] == bt_score_rg["method_disposition"]["bt_specific_zero_fiber_ward_identity"] == "OPEN", "BT-specific zero-fiber Ward identity promoted")
    require(atlas["bt_zero_fiber_change_of_measure_status"] == bt_ward_weight["method_disposition"]["zero_fiber_constrained_change_of_measure"] == "PROVED", "BT zero-fiber change of measure drift")
    require(atlas["bt_q_zero_uniform_lower_bound_status"] == bt_ward_weight["method_disposition"]["bt_background_uniform_q_zero_lower_bound"] == "OBSTRUCTED", "BT conditional-density lower-bound obstruction drift")
    require(atlas["bt_constrained_ward_to_annealed_score_status"] == bt_ward_weight["method_disposition"]["pointwise_constrained_ward_to_annealed_score_transfer"] == "OBSTRUCTED_AS_FORMULATED", "BT constrained-Ward transfer disposition drift")
    require(atlas["bt_annealed_inverse_density_status"] == bt_ward_weight["method_disposition"]["annealed_inverse_density_or_center_bound"] == "OPEN", "BT Ward-weight obstruction promoted to an annealed theorem")
    require(atlas["bt_quartic_kernel_status"] == bt_quartic_score["method_disposition"]["exact_quartic_score_kernel"] == "PROVED", "BT quartic score kernel drift")
    require(atlas["bt_quartic_soft_degree"] == bt_quartic_score["method_disposition"]["quartic_external_soft_degree"] == "LINEAR_NONZERO", "BT quartic soft degree drift")
    require(atlas["bt_isolated_quartic_square_status"] == bt_quartic_score["method_disposition"]["isolated_quartic_score_square_uniform_in_L"] == "OBSTRUCTED", "BT isolated quartic-square obstruction drift")
    require(atlas["bt_complete_order_g_four_score_status"] == bt_quartic_score["method_disposition"]["complete_order_g_four_score_coefficient"] == "OPEN", "BT isolated quartic result promoted to complete order g4")
    require(atlas["bt_quartic_power_cancellation_status"] == bt_quartic_score["method_disposition"]["power_cancellation_in_renormalized_zero_fiber_composite"] == "OPEN", "BT quartic power cancellation promoted")
    require(atlas["bt_complete_g4_formula_status"] == bt_complete_g4["method_disposition"]["complete_order_g_four_background_score_formula"] == "PROVED", "BT complete order-g4 formula drift")
    require(atlas["bt_complete_g4_uv_coefficient_status"] == bt_complete_g4["method_disposition"]["complete_order_g_four_uv_local_p_squared_coefficient"] == "POSITIVE_NONZERO", "BT complete order-g4 UV coefficient drift")
    require(atlas["bt_complete_g4_uv_cancellation_status"] == bt_complete_g4["method_disposition"]["uv_local_or_diagramwise_power_cancellation"] == "OBSTRUCTED", "BT complete order-g4 UV noncancellation drift")
    require(atlas["bt_complete_g4_whole_lattice_cancellation_status"] == bt_complete_g4["method_disposition"]["whole_lattice_order_g_four_power_cancellation"] == "OPEN", "BT UV-local result promoted to whole-lattice cancellation decision")
    require(atlas["bt_complete_g4_ir_complement_status"] == bt_complete_g4["method_disposition"]["infrared_complement_power_bound"] == "OPEN", "BT infrared complement promoted")
    require(atlas["bt_g4_chaos_decomposition_status"] == bt_g4_chaos["method_disposition"]["complete_order_g_four_chaos_decomposition"] == "PROVED", "BT order-g4 chaos decomposition drift")
    require(atlas["bt_g4_signed_second_chaos_status"] == bt_g4_chaos["method_disposition"]["all_signed_cancellation_localized_to_second_chaos"] == "PROVED", "BT signed second-chaos reduction drift")
    require(atlas["bt_g4_positive_norm_power_status"] == bt_g4_chaos["method_disposition"]["positive_norm_uv_power_lower_bound"] == "PROVED", "BT positive norm power lower bound drift")
    require(atlas["bt_g4_effective_kernel_bound_status"] == bt_g4_chaos["method_disposition"]["effective_second_chaos_kernel_norm_bound"] == "OPEN", "BT effective second-chaos kernel bound promoted")
    require(atlas["bt_g4_whole_lattice_survival_status"] == bt_g4_chaos["method_disposition"]["whole_lattice_order_g_four_power_survival"] == "OPEN", "BT chaos reduction promoted to whole-lattice power survival")
    require(atlas["bt_g4_expected_hessian_status"] == bt_g4_hessian["method_disposition"]["second_chaos_expected_hessian_representation"] == "PROVED", "BT expected-Hessian representation drift")
    require(atlas["bt_g4_conditioned_covariance_decomposition_status"] == bt_g4_hessian["method_disposition"]["conditioned_bulk_plus_rank_one_decomposition"] == "PROVED", "BT conditioned covariance decomposition drift")
    require(atlas["bt_g4_explicit_momentum_kernel_status"] == bt_g4_hessian["method_disposition"]["explicit_lattice_momentum_kernel"] == "OPEN", "BT Hessian formula promoted to explicit momentum kernel")
    require(atlas["bt_g4_hessian_kernel_bound_status"] == bt_g4_hessian["method_disposition"]["effective_second_chaos_kernel_norm_bound"] == "OPEN", "BT Hessian formula promoted to kernel bound")
    require(atlas["bt_g4_connected_reorganization_status"] == bt_g4_connected["method_disposition"]["complete_M4_connected_covariance_reorganization"] == "PROVED", "BT connected reorganization drift")
    require(atlas["bt_g4_normalization_alignment_status"] == bt_g4_connected["method_disposition"]["normalization_aligned_A_sector"] == "PROVED_EXTENSIVE", "BT normalization alignment drift")
    require(atlas["bt_g4_termwise_alignment_bound_status"] == bt_g4_connected["method_disposition"]["separate_or_triangle_bound_on_aligned_sector"] == "OBSTRUCTED_AS_FORMULATED", "BT termwise alignment-bound obstruction drift")
    require(atlas["bt_g4_connected_maximum_loop_rank"] == bt_g4_connected["method_disposition"]["complete_connected_M4_maximum_loop_rank"] == "TWO", "BT connected loop-rank drift")
    require(atlas["bt_g4_exact_cancellation_status"] == bt_g4_connected["method_disposition"]["exact_whole_lattice_M4_cancellation"] == "OPEN_NUMERICALLY_SUPPORTED", "BT numerical preflight promoted to exact cancellation")
    require(atlas["bt_g4_conditioned_maximum_loop_rank"] == bt_g4_l4["method_disposition"]["conditioned_connected_maximum_loop_rank"] == "TWO", "BT conditioned loop-rank drift")
    require(atlas["bt_g4_l4_complete_M4_status"] == bt_g4_l4["method_disposition"]["finite_L4_complete_M4"] == "NEGATIVE_NONZERO_EXACT", "BT exact L4 decision drift")
    require(atlas["bt_g4_l4_complete_M4"] == bt_g4_l4["exact_L4_decision"]["M4"] == {"numerator": -338835474713437, "denominator": 204838502400000}, "BT exact L4 rational drift")
    require(atlas["bt_g4_all_volume_zero_identity_status"] == bt_g4_l4["method_disposition"]["all_volume_exact_M4_zero_identity"] == "OBSTRUCTED_BY_L4_COUNTEREXAMPLE", "BT all-volume zero-identity obstruction drift")
    require(atlas["bt_g4_large_volume_sign_and_scaling_status"] == bt_g4_l4["method_disposition"]["large_volume_M4_sign_and_scaling"] == "OPEN", "BT finite L4 decision promoted to a large-volume theorem")
    require(atlas["bt_g4_general_l_two_loop_formula_status"] == bt_g4_general_l["method_disposition"]["generic_L_at_least_five_complete_two_loop_formula"] == "PROVED", "BT general-L two-loop formula drift")
    require(atlas["bt_g4_power_tadpole_survival_status"] == bt_g4_general_l["method_disposition"]["power_sized_Y_squared_and_XY_tadpole_survival"] == "CANCELED_EXACTLY", "BT power-tadpole cancellation drift")
    require(atlas["bt_g4_factorized_conditioning_status"] == bt_g4_general_l["method_disposition"]["factorized_conditioning_sector"] == "POSITIVE_O_LOG_SQUARED", "BT factorized conditioning bound drift")
    require(atlas["bt_g4_factorized_tuned_branch_status"] == bt_g4_general_l["method_disposition"]["factorized_conditioning_sector_on_tuned_running_branch"] == "UNIFORMLY_BOUNDED", "BT tuned factorized-sector conclusion drift")
    require(atlas["bt_g4_remaining_fourteen_kernel_status"] == bt_g4_general_l["method_disposition"]["remaining_fourteen_unfactorized_two_loop_kernel_bound"] == "OPEN", "BT factorized result promoted to remaining kernels")
    require(atlas["bt_g4_general_l_surviving_integrands"] == bt_g4_general_l["two_loop_atlas"]["statistics"]["surviving_integrand_count"] == 16, "BT general-L integrand count drift")
    require(atlas["bt_g4_seven_kernel_reduction_status"] == bt_g4_seven["method_disposition"]["fourteen_to_seven_inversion_reduction"] == "PROVED", "BT seven-kernel reduction drift")
    require(atlas["bt_g4_paired_quartic_status"] == bt_g4_seven["method_disposition"]["paired_quartic_uniform_product_bound"] == "PROVED", "BT paired-quartic bound drift")
    require(atlas["bt_g4_negative_nested_carrier_status"] == bt_g4_seven["method_disposition"]["negative_nested_one_soft_carrier"] == "NEGATIVE_ORDER_L_SQUARED_MAGNITUDE", "BT negative nested carrier drift")
    require(atlas["bt_g4_termwise_tuned_g4_status"] == bt_g4_seven["method_disposition"]["termwise_tuned_order_g_four_uniformity"] == "OBSTRUCTED", "BT termwise tuned-g4 obstruction drift")
    require(atlas["bt_g4_combined_seven_kernel_status"] == bt_g4_seven["method_disposition"]["combined_seven_kernel_large_volume_sign_and_scaling"] == "OPEN", "BT isolated carrier promoted to combined seven-kernel scaling")
    require(atlas["bt_g4_subpower_pairs"] == bt_g4_subpower["power_sector_reduction"]["subpower_pairs"] == [1, 2, 5], "BT subpower pair set drift")
    require(atlas["bt_g4_power_capable_pairs"] == bt_g4_subpower["power_sector_reduction"]["pairs_still_capable_of_N_omega_p_scale"] == [3, 4, 6, 7], "BT four-pair power gate drift")
    require(atlas["bt_g4_three_pair_tuned_uniformity_status"] == bt_g4_subpower["method_disposition"]["pairs_1_2_5_tuned_g_four_uniformity"] == "PROVED", "BT three-pair tuned uniformity drift")
    require(atlas["bt_g4_four_pair_power_coefficient_status"] == bt_g4_subpower["method_disposition"]["combined_pairs_3_4_6_7_power_coefficient"] == "OPEN", "BT subpower result promoted to four-pair coefficient")
    require(atlas["bt_g4_pair_three_scale"] == bt_g4_linear["method_disposition"]["pair_3_scale"] == "O_L", "BT pair-3 scale drift")
    require(atlas["bt_g4_pair_six_scale"] == bt_g4_linear["method_disposition"]["pair_6_scale"] == "O_L_LOG_L", "BT pair-6 scale drift")
    require(atlas["bt_g4_five_subpower_pairs"] == bt_g4_linear["power_sector_reduction"]["subpower_pairs"] == [1, 2, 3, 5, 6], "BT five-pair subpower set drift")
    require(atlas["bt_g4_two_power_capable_pairs"] == bt_g4_linear["power_sector_reduction"]["pairs_still_capable_of_N_omega_p_scale"] == [4, 7], "BT two-pair power gate drift")
    require(atlas["bt_g4_pair_four_seven_coefficient_status"] == bt_g4_linear["method_disposition"]["combined_pairs_4_7_power_coefficient"] == "OPEN", "BT linear-pair result promoted to pair-4/pair-7 coefficient")
    require(atlas["bt_g4_pair_four_coefficient_status"] == bt_g4_two_pair["method_disposition"]["pair_4_coefficient_normal_form"] == "PROVED_STRICTLY_NEGATIVE", "BT pair-4 coefficient normal form drift")
    require(atlas["bt_g4_pair_four_magnitude_floor"] == bt_g4_two_pair["pair_four"]["magnitude_lower_decimal_floor"] == "0.01613", "BT pair-4 exact gap drift")
    require(atlas["bt_g4_pair_seven_coefficient_status"] == bt_g4_two_pair["method_disposition"]["pair_7_coefficient_normal_form"] == "PROVED_STRICTLY_POSITIVE_FINITE", "BT pair-7 coefficient normal form drift")
    require(atlas["bt_g4_two_pair_comparison_status"] == bt_g4_two_pair["method_disposition"]["combined_pair_4_pair_7_coefficient"] == "OPEN", "BT two-pair normal forms promoted to noncancellation")

    allowed_tags = {"LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"}
    claim_ids = set()
    for claim in data["claims"]:
        require(claim["claim_id"] not in claim_ids, f"duplicate claim id {claim['claim_id']}")
        claim_ids.add(claim["claim_id"])
        require(set(claim["dependency_tags"]) <= allowed_tags, f"invalid dependency tag in {claim['claim_id']}")
        for authority in claim["authorities"]:
            require(authority in data["authorities"], f"unknown authority in {claim['claim_id']}")
    require(claim_ids == {f"RF-{n:02d}-{suffix}" for n, suffix in [
        (1, "TYPED-JUDGEMENT"),
        (2, "NAVIGATIONAL-ATLAS"),
        (3, "EXPLICIT-KREIN-ZF"),
        (4, "STATE-SELECTION-SPLIT"),
        (5, "CODED-WAVE-RCA0"),
        (6, "EVOLUTION-CAUSALITY-SPLIT"),
        (7, "FINITE-CONTINUUM-SPLIT"),
        (8, "FINITE-BV-BOUNDARY"),
        (9, "GR-CASSINI-ASSEMBLY"),
        (10, "BT-EUCLIDEAN-LATTICE"),
        (11, "BT-FREE-RECONSTRUCTION-OBSTRUCTION"),
        (12, "BT-INTERACTING-OS-PREFLIGHT"),
        (13, "BT-INTERACTING-RECONSTRUCTION-FRONTIER"),
        (14, "MANNHEIM-NGC3198-ASSEMBLY"),
        (15, "NGC3198-COMMON-FIT-CONTROL"),
        (16, "CODED-OBSERVABLE-RECONSTRUCTION"),
        (17, "LOCALIZED-COEFFICIENT-WEAK-WAVE"),
        (18, "NAMED-H2-WEAK-WAVE-COMPLETION"),
        (19, "FIXED-SUPPORT-SMOOTH-TO-H2-TRANSLATOR"),
        (20, "SUPPORT-INDEXED-TEST-SPACE-COMPARISON"),
        (21, "SCALAR-MINKOWSKI-GREEN-CHOICE-AUDIT"),
        (22, "SCALAR-MINKOWSKI-BIWAVE-GREEN"),
        (23, "SCALAR-BIWAVE-TO-WEYL-BV-DELTA"),
        (24, "STRICT-WEYL-LOCAL-Q1-Q2"),
        (25, "STRICT-WEYL-CAUSAL-CONVENTION-STABILITY"),
        (26, "BT-HOMOGENEOUS-VIRIAL-NO-GO"),
        (27, "BT-BUBBLE-ENTROPY-SOFT-SCORE-BALANCE"),
        (28, "STRICT-WEYL-ENDPOINT-Q1-CONTENT-BRIDGE"),
        (29, "BT-FULL-PHASE-CURRENT-GATE"),
        (30, "STRICT-WEYL-SUSPENDED-ADJOINT-BRIDGE"),
        (31, "STRICT-WEYL-COMPONENT-PAIRING-SERIALIZATION"),
        (32, "BT-CORRECTOR-POINTWISE-ENERGY-NO-GO"),
        (33, "BT-CORRECTOR-SLAB-FIBER-STABILITY"),
        (34, "BT-CORRECTOR-SLAB-CYLINDER-SUPPRESSION"),
        (35, "STRICT-WEYL-FULL-Q1-COMPONENT-SNAPSHOT"),
        (36, "STRICT-WEYL-SPLIT-LOCAL-SDR"),
        (37, "STRICT-WEYL-CANONICAL-SHEAR-COMPONENT-JETS"),
        (38, "STRICT-WEYL-GRAPH-Q1-SDR-COMPONENT-JETS"),
        (39, "STRICT-WEYL-REPRESENTED-GREEN-ACTION-NAMES"),
        (40, "STRICT-WEYL-UNARY-CAUSAL-COMMON-SNAPSHOT"),
        (41, "STRICT-WEYL-FULL-CYLINDER-D-ACTION"),
        (42, "STRICT-WEYL-GATE-V6-RECONCILIATION"),
        (43, "STRICT-WEYL-STABILIZED-Q2-LIFT-PREFLIGHT"),
        (44, "STRICT-WEYL-GATE-V7-THEORY-IDENTITY-FRONTIER"),
        (45, "STRICT-WEYL-CANDIDATE-Q2-GREEN-FIRST-RESPONSE"),
        (46, "STRICT-WEYL-CANDIDATE-POLARIZED-CAUSAL-TREES"),
        (47, "STRICT-WEYL-POLARIZED-FORMAL-COEFFICIENTS-AND-BV-GATE"),
        (48, "STRICT-WEYL-FIELD-EQUATION-GREEN-QUOTIENT-INVERSE"),
        (49, "STRICT-WEYL-QUADRATIC-TRUNCATION-Q3-NECESSITY"),
        (50, "STRICT-PURE-WEYL-CUBIC-WITNESS-CANCELLATION"),
        (51, "STRICT-PURE-WEYL-MINIMAL-Q3-COMPLETION"),
        (52, "STRICT-WEYL-386-STABILIZED-Q3-PREFLIGHT"),
        (53, "STRICT-WEYL-NONMINIMAL-THEORY-IDENTITY-OBSTRUCTION"),
        (54, "STRICT-WEYL-GATE-V8-NONLINEAR-EQUIVALENCE-FRONTIER"),
        (55, "STRICT-WEYL-QUADRATIC-AUXILIARY-ELIMINATION-COMPONENT"),
        (56, "STRICT-WEYL-GATE-V9-COMPONENTWISE-PULLBACK-FRONTIER"),
        (57, "STRICT-WEYL-SHIFTED-CUBIC-INVENTORY-AND-VV-BV-LIFT"),
        (58, "STRICT-WEYL-GATE-V10-THREE-FRONT-COMPLETION-ATLAS"),
    ]}, "claim set drift")

    flags = data["claim_flags"]
    require(flags["strict_pure_weyl_local_q1_q2_certified"] is True, "strict pure-Weyl q1/q2 flag missing")
    require(flags["strict_minimal_bv_cyclicity_reconciled"] is True, "strict minimal BV cyclicity flag missing")
    require(flags["strict_386_causal_convention_stability_certified"] is True, "strict 386 causal convention-stability flag missing")
    require(flags["strict_386_endpoint_q1_content_identified"] is True, "strict endpoint q1 content flag missing")
    require(flags["strict_386_endpoint_all_700_bach_columns_match"] is True, "strict endpoint Bach-column flag missing")
    require(flags["strict_386_pairing_suspension_bridge_certified"] is True, "strict endpoint pairing suspension bridge missing")
    require(flags["strict_386_full_suspended_green_adjoint_replayed"] is True, "strict suspended Green adjoint replay missing")
    require(flags["strict_386_component_basis_serialized"] is True, "strict 386 component basis missing")
    require(flags["strict_386_component_pairing_serialized"] is True, "strict 386 component pairing missing")
    require(flags["strict_386_componentwise_t_adjoint_replayed"] is True, "strict componentwise T adjoint missing")
    require(flags["strict_386_full_q1_component_bytes_serialized"] is True, "strict full-q1 component bytes missing")
    require(flags["strict_386_full_q1_squared_zero_replayed"] is True, "strict full-q1 nilpotency replay missing")
    require(flags["strict_386_full_q1_suspended_cyclicity_replayed"] is True, "strict full-q1 suspended cyclicity replay missing")
    require(flags["strict_386_local_sdr_component_maps_serialized"] is True, "strict local SDR component maps missing")
    require(flags["strict_386_local_sdr_identities_replayed"] is True, "strict local SDR identity replay missing")
    require(flags["strict_386_local_sdr_cyclicity_replayed"] is True, "strict local SDR cyclicity replay missing")
    require(flags["strict_386_canonical_shear_component_jets_serialized"] is True, "strict canonical shear component jets missing")
    require(flags["strict_386_canonical_shear_inverse_replayed"] is True, "strict canonical shear inverse replay missing")
    require(flags["strict_386_canonical_shear_bv_canonicality_replayed"] is True, "strict canonical shear BV canonicality replay missing")
    require(flags["strict_386_unshifted_graph_q1_snapshot_complete"] is True, "strict graph-coordinate q1 snapshot missing")
    require(flags["strict_386_unshifted_graph_sdr_snapshot_complete"] is True, "strict graph-coordinate SDR snapshot missing")
    require(flags["strict_386_graph_suspension_transported"] is True, "strict graph suspension transport missing")
    require(flags["strict_386_represented_green_actions_serialized"] is True, "strict represented Green actions omitted")
    require(flags["strict_386_unary_causal_common_snapshot_accepted"] is True, "strict unary-causal common snapshot omitted")
    require(flags["strict_386_effective_numeric_green_solver"] is False, "strict convergent Green name promoted to an effective solver")
    require(flags["strict_386_distribution_kernel_bytes_serialized"] is False, "strict convergent Green name promoted to kernel bytes")
    require(flags["strict_386_classical_import_gate_passed"] is False, "strict classical import gate promoted")
    require(flags["strict_386_all_operator_component_adjoints_replayed"] is False, "strict all-operator replay promoted")
    require(flags["strict_386_local_d_certified"] is True, "strict 386 local D omitted")
    require(flags["strict_386_full_local_d_action_certified"] is True, "strict full local D action omitted")
    require(flags["strict_386_d_q1_commutator_replayed"] is True, "strict D/q1 replay omitted")
    require(flags["strict_386_d_formal_skew_adjoint_replayed"] is True, "strict D formal adjoint replay omitted")
    require(flags["strict_386_unary_causal_d_scoped_snapshot_accepted"] is True, "strict unary-causal-D scope omitted")
    require(flags["strict_386_full_carrier_q2_certified"] is False, "strict full-carrier q2 promoted")
    require(flags["strict_386_d_q2_derivation_replayed"] is False, "strict D/q2 replay promoted")
    require(flags["strict_386_d_cartan_homotopy_constructed"] is False and flags["strict_d_gauge_or_charge_decided"] is False, "strict D Cartan/charge boundary promoted")
    require(flags["strict_386_stabilized_q2_candidate_certified"] is True, "strict stabilized q2 candidate omitted")
    require(flags["strict_386_stabilized_q1_q2_identity_verified"] is True and flags["strict_386_stabilized_q2_cyclicity_verified"] is True and flags["strict_386_stabilized_d_q2_derivation_verified"] is True, "strict stabilized q2 identities omitted")
    require(flags["strict_386_authoritative_full_q2_imported"] is False and flags["strict_386_candidate_theory_identity_certified"] is False, "strict candidate promoted to authoritative q2")
    require(flags["strict_386_candidate_q2_green_same_carrier_verified"] is True and flags["strict_386_candidate_first_nonlinear_causal_response_certified"] is True, "strict candidate q2/Green first response omitted")
    require(flags["strict_386_candidate_q2_green_causal_support_certified"] is True and flags["strict_386_candidate_q2_green_response_identity_verified"] is True and flags["strict_386_q2_green_foundations_stratified"] is True, "strict candidate q2/Green support, identity, or foundations omitted")
    require(flags["strict_386_authoritative_q2_green_compatibility_certified"] is False and flags["strict_386_recursive_nonlinear_green_trees_certified"] is False, "strict candidate q2/Green promoted to authority or recursive completion")
    require(flags["strict_386_candidate_retarded_all_finite_q2_trees_certified"] is True and flags["strict_386_candidate_advanced_all_finite_q2_trees_certified"] is True and flags["strict_386_candidate_fixed_step_tree_continuity_certified"] is True, "strict polarized finite-tree theorem omitted")
    require(flags["strict_386_first_mixed_sign_domain_nondefinition_at_four_leaves"] is True, "strict mixed-sign boundary omitted")
    require(flags["strict_386_unrestricted_mixed_sign_trees_certified"] is False and flags["strict_386_arbitrary_causal_difference_trees_certified"] is False and flags["strict_386_infinite_tree_series_convergence_certified"] is False and flags["strict_386_authoritative_q2_recursive_trees_certified"] is False and flags["strict_386_q3_or_higher_causal_trees_certified"] is False, "strict recursive-tree result over-promoted")
    require(flags["strict_386_candidate_polarized_formal_coefficients_certified"] is True, "strict formal coefficient theorem omitted")
    require(flags["strict_386_weyl_bv_maurer_cartan_series_certified"] is False and flags["strict_386_authoritative_formal_moller_map_certified"] is False and flags["strict_386_analytic_moller_convergence_certified"] is False, "strict formal coefficients over-promoted")
    require(strict_q1["claim_flags"]["Q1_SQUARED_ZERO_CERTIFIED"] is True, "strict q1 square-zero authority drift")
    require(strict_q1q2["channel_inventory"]["channel_count"] == 18, "strict q1/q2 channel count drift")
    require(strict_q1q2["channel_inventory"]["composable_path_count"] == 51, "strict q1/q2 path count drift")
    require(strict_q1q2["claim_flags"]["Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED"] is True, "strict q1/q2 authority drift")
    require(strict_q1q2["claim_flags"]["STRICT_FULL_LOCAL_D_ACTION_CERTIFIED"] is False, "strict local D action promoted")
    require(strict_q1q2["claim_flags"]["BV_CYCLICITY_Q2_REPLAYED"] is False, "strict BV cyclicity promoted")
    require(strict_cyclic["cyclicity_receiver"]["basis_dimension"] == 30, "strict cyclicity basis drift")
    require(strict_cyclic["cyclicity_receiver"]["source_convention_defect"]["coefficient_count"] == 540, "strict source-convention defect count drift")
    require(strict_cyclic["cyclicity_receiver"]["expanded_q2_coefficient_count"] == 932, "strict cyclicity expansion count drift")
    require(strict_cyclic["cyclicity_receiver"]["translated_convention_defect"]["coefficient_count"] == 0, "translated minimal convention is not cyclic")
    require(strict_cyclic["claim_flags"]["Q1_SQUARED_ZERO_PRESERVED"] is True, "q1 square-zero was not preserved by the sign translation")
    require(strict_cyclic["claim_flags"]["Q1_Q2_ARITY_TWO_NILPOTENCY_PRESERVED"] is True, "q1/q2 identity was not preserved by the sign translation")
    require(strict_cyclic["claim_flags"]["STRICT_FULL_LOCAL_D_ACTION_CERTIFIED"] is False, "strict local D action promoted by cyclicity reconciliation")
    require(strict_cyclic["claim_flags"]["FULL_COMMON_CARRIER_PAIRING_CERTIFIED"] is False, "minimal pairing promoted to the full carrier")
    require(gate_v5["gate_disposition"]["gate_a_status"] == "FAIL_CLOSED", "Gate-A v5 promoted")
    require(gate_v5["gate_disposition"]["accepted_common_snapshot_hashes"] == 0, "Gate-A v5 common hash promoted")
    require(gate_v5["claim_flags"]["STRICT_MINIMAL_Q1_Q2_CYCLICITY_SCOPED_REPLAY"] is True, "Gate-A v5 omitted scoped cyclicity repair")
    require(strict_386_transport["transport"]["rank"] == 386, "strict causal transport rank drift")
    require(strict_386_transport["transport"]["positive_eigenvalue_multiplicity"] == 381, "strict causal transport positive-sign count drift")
    require(strict_386_transport["transport"]["negative_eigenvalue_multiplicity"] == 5, "strict causal transport negative-sign count drift")
    require(strict_386_transport["claim_flags"]["STRICT_386_CAUSAL_GREEN_HOMOTOPY_PRESERVED"] is True, "strict causal Green homotopy was not transported")
    require(strict_386_transport["claim_flags"]["GATE_V5_TO_386_COMMON_BYTES_IDENTIFIED"] is False, "strict type bridge promoted to common bytes")
    require(strict_386_transport["claim_flags"]["STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED"] is False, "strict unary transport promoted to nonlinear compatibility")
    require(completion_atlas_v4["strict_causal_sign_transport"]["causal_stage_preserved"] is True, "completion atlas omitted causal sign transport")
    require(completion_atlas_v4["strict_causal_sign_transport"]["common_bytes_identified"] is False, "completion atlas promoted common bytes")
    require(completion_atlas_v4["claim_flags"]["lorentzian_full_theory_certified"] is False, "completion atlas promoted a full Lorentzian theory")
    require(strict_386_endpoint["coefficientwise_identification"]["arrow_table_counts"]["total"] == 80, "strict endpoint q1 table count drift")
    require(strict_386_endpoint["coefficientwise_identification"]["gate_bach_columns_matching"] == 700, "strict endpoint Bach-column count drift")
    require(strict_386_endpoint["coefficientwise_identification"]["common_nonzero_coefficients"] == 619, "strict endpoint common coefficient count drift")
    require(strict_386_endpoint["pairing_disposition"]["simultaneously_transported_causal_ghost_pullback_equals_gate_canonical"] is False, "strict endpoint pairing sign promoted")
    require(strict_386_endpoint["pairing_disposition"]["simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical"] is True, "strict endpoint negative pairing sign omitted")
    require(strict_386_endpoint["claim_flags"]["STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED"] is False, "strict endpoint q1 bridge promoted to q2")
    require(completion_atlas_v5["strict_endpoint_q1_content_bridge"]["arrow_tables_matching"] == 80, "completion atlas V5 omitted endpoint q1 bridge")
    require(completion_atlas_v5["claim_flags"]["strict_386_pairing_suspension_bridge_certified"] is False, "completion atlas V5 promoted pairing suspension")
    require(completion_atlas_v5["claim_flags"]["lorentzian_full_theory_certified"] is False, "completion atlas V5 promoted a full Lorentzian theory")
    require(strict_386_suspension["endpoint_exact_algebra"]["gate_pairing_nonzero_entries"] == 54, "strict suspension pre-pullback endpoint pairing count drift")
    require(strict_386_suspension["endpoint_exact_algebra"]["identities"]["R_equals_T_sharp_gate_T"] is True, "strict suspension character identity missing")
    require(strict_386_suspension["full_carrier_extension"]["R_386_positive"] == 376, "strict suspension positive-sign count drift")
    require(strict_386_suspension["full_carrier_extension"]["R_386_negative"] == 10, "strict suspension negative-sign count drift")
    require(strict_386_suspension["claim_flags"]["FULL_386_SUSPENDED_GREEN_ADJOINT_REPLAYED"] is True, "strict suspended Green adjoint was not replayed")
    require(strict_386_suspension["claim_flags"]["FULL_386_COMPONENT_PAIRING_SERIALIZED_IN_GATE_CONVENTION"] is False, "strict component pairing promoted")
    require(strict_386_suspension["claim_flags"]["STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED"] is False, "strict suspended adjoint promoted to q2")
    require(completion_atlas_v6["strict_suspended_adjoint_bridge"]["full_suspended_green_adjoint_replayed"] is True, "completion atlas V6 omitted suspended adjoint replay")
    require(completion_atlas_v6["claim_flags"]["strict_386_component_pairing_serialized"] is False, "completion atlas V6 promoted component pairing")
    require(completion_atlas_v6["claim_flags"]["strict_386_local_d_certified"] is False, "completion atlas V6 promoted local D")
    require(completion_atlas_v6["claim_flags"]["lorentzian_full_theory_certified"] is False, "completion atlas V6 promoted a full Lorentzian theory")
    basis = strict_386_pairing["component_basis"]
    pairing = strict_386_pairing["pairing_serialization"]
    reconciliation = strict_386_pairing["terminology_reconciliation"]
    operator_boundary = strict_386_pairing["operator_adjoint_disposition"]
    require(basis["dimension"] == 386 and basis["endpoint_dimension"] == 30 and basis["algebraic_complement_split"] == "356=36+320", "strict component basis split drift")
    require(len(basis["rows"]) == 386 and len({row["index"] for row in basis["rows"]}) == 386, "strict component row serialization drift")
    require(pairing["nonzero_ordered_entry_count"] == 410 and pairing["rank"] == 386 and len(pairing["entries"]) == 410, "strict component pairing serialization drift")
    require(reconciliation["suspension_v1_value"] == 54 and reconciliation["gate_coordinate_endpoint_pairing_nonzero_entries"] == 30, "strict endpoint coordinate reconciliation drift")
    require(strict_386_pairing["suspension_serialization"]["componentwise_T_adjoint_relation_replayed"] is True, "strict componentwise T adjoint replay missing")
    require(operator_boundary["every_component_operator_adjoint_replayed"] is False, "strict operator component replay promoted")
    require(strict_386_pairing["claim_flags"]["STRICT_386_LOCAL_D_CERTIFIED"] is False and strict_386_pairing["claim_flags"]["STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED"] is False, "strict pairing result promoted to nonlinear gates")
    require(completion_atlas_v7["strict_component_pairing_serialization"]["pairing_entries"] == 410, "completion atlas V7 omitted component pairing")
    require(completion_atlas_v7["claim_flags"]["strict_386_all_operator_component_adjoints_replayed"] is False, "completion atlas V7 promoted all operator adjoints")
    require(completion_atlas_v7["claim_flags"]["strict_386_local_d_certified"] is False and completion_atlas_v7["claim_flags"]["strict_386_q2_green_compatibility_certified"] is False, "completion atlas V7 promoted D/q2")
    require(strict_386_sign_repair["repair"]["repair_applied"] is True and strict_386_sign_repair["exact_replay"]["repaired_plus_sign"]["odd_pairing_cyclicity_defects"] == 0, "strict auxiliary-q sign repair missing")
    require(strict_386_sign_repair["exact_replay"]["rejected_minus_sign_regression"]["odd_pairing_cyclicity_defects"] == 8, "strict auxiliary-q regression rail drift")
    require(strict_386_sign_repair["verification"]["tier_3"]["status"] == "PASS" and "82/82 PASS" in strict_386_sign_repair["verification"]["tier_3"]["terminal_guard"], "strict auxiliary-q Tier-3 receipt missing")
    require(completion_atlas_v10["strict_auxiliary_q_sign_repair"]["repair_applied"] is True, "completion atlas V10 omitted sign repair")
    require(completion_atlas_v10["claim_flags"]["strict_full_386_q1_portable_component_bytes"] is False and completion_atlas_v10["claim_flags"]["lorentzian_full_theory_certified"] is False, "completion atlas V10 promoted full q1 or Lorentzian theory")
    q1_serialization = strict_386_full_q1["q1_serialization"]
    q1_inventory = q1_serialization["counts"]
    require(q1_serialization["carrier_dimension"] == 386 and q1_serialization["carrier_split"] == "30+36+320", "strict full-q1 carrier split drift")
    require(q1_inventory["operator_tables"] == 18 and q1_inventory["coefficient_multiindex_tables"] == 127 and q1_inventory["nonzero_rational_coefficients"] == 2193, "strict full-q1 inventory drift")
    require(strict_386_full_q1["nilpotency_replay"]["full_q1_squared_zero"] is True and strict_386_full_q1["suspended_cyclicity_replay"]["exact_defects"] == 0 and strict_386_full_q1["suspended_cyclicity_replay"]["coefficientwise_multiindices_checked"] == 70, "strict full-q1 exact replay missing")
    require(strict_386_full_q1["claim_flags"]["STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_SERIALIZED"] is True, "strict full-q1 portable bytes omitted")
    require(strict_386_full_q1["claim_flags"]["STRICT_386_FULL_SDR_OPERATOR_TABLES_SERIALIZED"] is False and strict_386_full_q1["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is False, "strict full-q1 result promoted SDR or Gate A")
    require(completion_atlas_v11["strict_full_q1_component_jet_table"]["nonzero_rational_coefficients"] == 2193, "completion atlas V11 omitted full q1")
    require(completion_atlas_v11["claim_flags"]["strict_full_386_q1_portable_component_bytes"] is True and completion_atlas_v11["claim_flags"]["strict_pure_weyl_classical_gate_passed"] is False, "completion atlas V11 q1/Gate-A boundary drift")
    local_maps = strict_386_local_sdr["component_maps"]
    require(local_maps["H_alg"]["nonzero_entries"] == 190 and local_maps["P_alg"]["nonzero_entries"] == 356, "strict local SDR homotopy/projector inventory drift")
    require(local_maps["P_end"]["nonzero_entries"] == 30 and local_maps["i_end"]["nonzero_entries"] == 30 and local_maps["p_end"]["nonzero_entries"] == 30, "strict local SDR endpoint map inventory drift")
    local_replay = strict_386_local_sdr["exact_replay"]
    require(local_replay["qH_plus_Hq_equals_P_alg"] is True and local_replay["qH_plus_Hq_defects"] == 0 and local_replay["derivative_multiindices_checked"] == 70, "strict local SDR homotopy replay missing")
    require(local_replay["p_end_i_end_identity"] is True and local_replay["i_end_p_end_equals_P_end"] is True and local_replay["projectors_idempotent"] is True and local_replay["projectors_commute_with_q"] is True, "strict local SDR retract replay missing")
    require(local_replay["H_alg_squared_zero"] is True and local_replay["H_alg_i_end_zero"] is True and local_replay["p_end_H_alg_zero"] is True and local_replay["H_alg_cyclicity_defects"] == 0, "strict local SDR side-condition/cyclicity replay missing")
    local_foundations = strict_386_local_sdr["support_and_foundations"]
    require(local_foundations["maximum_differential_order"] == 0 and local_foundations["support_local"] is True and local_foundations["finite_exact_upper_bound"] == "PRA", "strict local SDR foundational bound drift")
    require(local_foundations["choice_operation_added"] is False and local_foundations["infinite_selection_added"] is False and local_foundations["analytic_green_theorem_used"] is False, "strict local SDR foundational boundary drift")
    local_transport = strict_386_local_sdr["coordinate_transport_boundary"]
    require(local_transport["split_SDR_complete"] is True and local_transport["T_A_B_canonical_shear_serialized"] is False and local_transport["unshifted_curvature_graph_SDR_snapshot_complete"] is False, "strict local SDR coordinate boundary drift")
    require(strict_386_local_sdr["claim_flags"]["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"] is False and strict_386_local_sdr["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is False, "strict local SDR promoted Green actions or Gate A")
    atlas_sdr = completion_atlas_v12["strict_local_sdr_component_maps"]
    require(atlas_sdr["H_alg_nonzero_entries"] == 190 and atlas_sdr["derivative_multiindices_checked"] == 70 and atlas_sdr["homotopy_identity_defects"] == 0 and atlas_sdr["cyclicity_defects"] == 0, "completion atlas V12 omitted split local SDR")
    require(completion_atlas_v12["claim_flags"]["strict_386_split_local_sdr_component_maps_serialized"] is True and completion_atlas_v12["claim_flags"]["strict_386_canonical_shear_component_jets_serialized"] is False, "completion atlas V12 split-SDR/shear boundary drift")
    require(completion_atlas_v12["claim_flags"]["strict_386_represented_green_actions_serialized"] is False and completion_atlas_v12["claim_flags"]["strict_pure_weyl_classical_gate_passed"] is False and completion_atlas_v12["claim_flags"]["lorentzian_full_theory_certified"] is False, "completion atlas V12 Green/Gate/quantum boundary drift")
    shear_transform = strict_386_canonical_shear["canonical_transform"]
    require(shear_transform["forward"]["table_count"] == 7 and shear_transform["inverse"]["table_count"] == 7, "strict canonical shear table inventory drift")
    require(shear_transform["forward"]["nonzero_off_diagonal_coefficients"] == 1321 and shear_transform["inverse"]["nonzero_off_diagonal_coefficients"] == 1321, "strict canonical shear coefficient inventory drift")
    shear_replay = strict_386_canonical_shear["exact_replay"]
    require(shear_replay["raw_T_A_B_hash_defects"] == 0 and shear_replay["generalized_auxiliary_attachment_nonzero_coefficients"] == 0, "strict canonical shear source reconciliation drift")
    require(shear_replay["elementary_inverse_defects"] == 0 and shear_replay["elementary_BV_canonicality_defects"] == 0, "strict elementary shear replay drift")
    require(shear_replay["full_left_inverse_defects"] == 0 and shear_replay["full_right_inverse_defects"] == 0 and shear_replay["degree_zero_defects"] == 0, "strict full shear inverse/degree replay drift")
    require(shear_replay["forbidden_derivative_derivative_products_in_inverse_replay"] == 0 and shear_replay["cross_term_PBW_commutator_required"] is False, "strict canonical shear suppressed a curved-jet composition")
    require(shear_replay["forward_cross_terms"] == 1 and shear_replay["inverse_cross_terms"] == 1 and shear_replay["full_BV_canonicality"] is True, "strict canonical shear cross-term/canonicality drift")
    shear_gate = strict_386_canonical_shear["gate_disposition"]
    require(shear_gate["canonical_shear_snapshot_bound"] is True and shear_gate["graph_coordinate_q1_component_replay_complete"] is False and shear_gate["graph_coordinate_sdr_component_replay_complete"] is False, "strict canonical shear graph boundary drift")
    require(strict_386_canonical_shear["claim_flags"]["STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_TABLE_SERIALIZED"] is True and strict_386_canonical_shear["claim_flags"]["STRICT_386_CANONICAL_SHEAR_INVERSE_REPLAYED"] is True and strict_386_canonical_shear["claim_flags"]["STRICT_386_CANONICAL_SHEAR_BV_CANONICALITY_REPLAYED"] is True, "strict canonical shear claim flags missing")
    require(strict_386_canonical_shear["claim_flags"]["STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED"] is False and strict_386_canonical_shear["claim_flags"]["STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED"] is False and strict_386_canonical_shear["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is False, "strict canonical shear promoted graph replay or Gate A")
    atlas_shear = completion_atlas_v13["strict_canonical_shear_component_jets"]
    require(atlas_shear["forward_table_count"] == 7 and atlas_shear["inverse_table_count"] == 7 and atlas_shear["left_inverse_defects"] == 0 and atlas_shear["right_inverse_defects"] == 0, "completion atlas V13 omitted canonical shear replay")
    require(completion_atlas_v13["claim_flags"]["strict_386_canonical_shear_component_jets_serialized"] is True and completion_atlas_v13["claim_flags"]["strict_386_canonical_shear_inverse_replayed"] is True and completion_atlas_v13["claim_flags"]["strict_386_canonical_shear_bv_canonicality_replayed"] is True, "completion atlas V13 shear boundary drift")
    require(completion_atlas_v13["claim_flags"]["strict_386_unshifted_graph_q1_snapshot_complete"] is False and completion_atlas_v13["claim_flags"]["strict_386_unshifted_graph_sdr_snapshot_complete"] is False and completion_atlas_v13["claim_flags"]["strict_pure_weyl_classical_gate_passed"] is False and completion_atlas_v13["claim_flags"]["lorentzian_full_theory_certified"] is False, "completion atlas V13 promoted graph/Gate/quantum completion")
    require(len(completion_atlas_v13["route_selection"]) == 8 and completion_atlas_v13["route_selection"][0]["route"] == "STRICT_386_SPLIT_TO_GRAPH_SDR_REPLAY", "completion atlas V13 frontier ordering drift")
    graph_counts = strict_386_graph_sdr["graph_q1_serialization"]["counts"]
    require(graph_counts["operator_tables"] == 27 and graph_counts["graph_attachment_tables"] == 9 and graph_counts["combined_derivative_multiindices"] == 70 and graph_counts["nonzero_rational_coefficients"] == 4374, "strict graph q1 inventory drift")
    graph_replay = strict_386_graph_sdr["exact_replay"]
    require(graph_replay["qH_plus_Hq_defects"] == 0 and graph_replay["p_graph_i_graph_identity_defects"] == 0 and graph_replay["H_alg_graph_cyclicity_defects"] == 0 and graph_replay["R_graph_squared_defects"] == 0, "strict graph SDR direct replay drift")
    require(graph_replay["untransported_diagonal_R_cyclicity_defects"] == 8 and graph_replay["transported_R_raw_parallel_cyclicity_residual_coefficients"] == 32 and graph_replay["raw_N_A_minus_B_C_parallel_residual_coefficients"] == 16 and graph_replay["transported_R_PBW_reduced_cyclicity_defects"] == 0, "strict graph suspension/PBW boundary drift")
    require(strict_386_graph_sdr["claim_flags"]["STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED"] is True and strict_386_graph_sdr["claim_flags"]["STRICT_386_GRAPH_SDR_IDENTITIES_REPLAYED"] is True and strict_386_graph_sdr["claim_flags"]["STRICT_386_GRAPH_SUSPENSION_TRANSPORTED"] is True, "strict graph positive flags missing")
    require(strict_386_graph_sdr["claim_flags"]["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"] is False and strict_386_graph_sdr["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is False and strict_386_graph_sdr["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] is False and strict_386_graph_sdr["claim_flags"]["QME_RESTORED"] is False, "strict graph result promoted downstream claims")
    atlas_graph = completion_atlas_v14["strict_graph_q1_sdr_component_jets"]
    require(atlas_graph["operator_tables"] == 27 and atlas_graph["nonzero_rational_coefficients"] == 4374 and atlas_graph["transported_suspension_entries"] == 394 and atlas_graph["old_diagonal_suspension_cyclicity_defects"] == 8, "completion atlas V14 omitted graph replay")
    require(completion_atlas_v14["claim_flags"]["strict_386_unshifted_graph_q1_snapshot_complete"] is True and completion_atlas_v14["claim_flags"]["strict_386_unshifted_graph_sdr_snapshot_complete"] is True and completion_atlas_v14["claim_flags"]["strict_386_graph_suspension_transported"] is True, "completion atlas V14 graph flags missing")
    require(completion_atlas_v14["claim_flags"]["strict_386_represented_green_actions_serialized"] is False and completion_atlas_v14["claim_flags"]["strict_pure_weyl_classical_gate_passed"] is False and completion_atlas_v14["claim_flags"]["lorentzian_full_theory_certified"] is False, "completion atlas V14 promoted Green/Gate/quantum completion")
    require(len(completion_atlas_v14["route_selection"]) == 8 and completion_atlas_v14["route_selection"][0]["route"] == "STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "completion atlas V14 frontier ordering drift")
    green_flags = strict_386_green_name["claim_flags"]
    require(strict_386_green_name["carrier"]["graph_rows"] == 386 and strict_386_green_name["carrier"]["tractor_rank"] == 15, "strict Green-name carrier drift")
    require(len(strict_386_green_name["parent_spectral_name"]["spatial_spectrum"]) == 3 and strict_386_green_name["parent_spectral_name"]["basis_choice"].startswith("none;"), "strict Green-name spectral representation drift")
    require(strict_386_green_name["analytic_and_exact_replay"]["modal_inverse_jump_checked_exactly"] is True and strict_386_green_name["analytic_and_exact_replay"]["zero_mode_checked_exactly"] is True and strict_386_green_name["analytic_and_exact_replay"]["full_graph_homotopy_identity_exact"] is True, "strict Green-name analytic/exact replay missing")
    require(green_flags["STRICT_ENDPOINT_GREEN_CONVERGENT_NAME_SERIALIZED"] is True and green_flags["STRICT_FULL_GRAPH_GREEN_CONVERGENT_NAME_SERIALIZED"] is True and green_flags["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"] is True, "strict represented Green-name flags missing")
    require(green_flags["STRICT_386_RECEIVER_EXECUTABLE_NUMERIC_GREEN_SOLVER"] is False and green_flags["STRICT_386_DISTRIBUTION_KERNEL_BYTES_SERIALIZED"] is False and green_flags["CLASSICAL_IMPORT_GATE_PASSED"] is False, "strict Green name promoted effectivity, kernel bytes, or Gate A")
    require(strict_386_green_name["foundational_strength"]["weakest_base"] == "NOT_ESTABLISHED" and strict_386_green_name["foundational_strength"]["physics_implies_choice_principle"] is False, "strict Green-name foundational boundary drift")
    unary_flags = strict_386_unary_causal["claim_flags"]
    require(strict_386_unary_causal["scope"]["carrier_rows"] == 386 and strict_386_unary_causal["scope"]["accepted_hashes"] == 13 and len(strict_386_unary_causal["accepted_objects"]) == 13, "strict unary-causal snapshot inventory drift")
    require(strict_386_unary_causal["common_snapshot"]["receiver_status"] == "ACCEPTED_SCOPED" and strict_386_unary_causal["common_snapshot"]["all_objects_share_carrier"] is True and strict_386_unary_causal["common_snapshot"]["both_causal_orientations_present"] is True, "strict unary-causal snapshot acceptance drift")
    gate_boundary = strict_386_unary_causal["gate_v5_reconciliation"]
    require((gate_boundary["exports_required"], gate_boundary["top_level_hashes_required"], gate_boundary["freeze_checks_required"], gate_boundary["top_level_hashes_accepted_by_this_scoped_result"]) == (20, 7, 10, 0), "strict unary-causal Gate-A boundary drift")
    require([item["id"] for item in gate_boundary["missing_bundle"]] == ["M1_COMMON_STRICT_SNAPSHOT", "M2_STRICT_Q2_D", "M3_RESIDUAL_SDR", "M4_FULL_CYCLIC_PAIRING", "M5_RESIDUAL_EXACT_PAYLOAD", "M6_CENTERED_REPRESENTATIVES"], "strict unary-causal missing-bundle ledger drift")
    require(unary_flags["STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_ACCEPTED"] is True and unary_flags["CLASSICAL_IMPORT_GATE_PASSED"] is False and unary_flags["HADAMARD_STATE_CONSTRUCTED"] is False and unary_flags["QME_RESTORED"] is False, "strict unary-causal snapshot promoted downstream lifecycle")
    require(completion_atlas_v15["claim_flags"]["strict_386_represented_green_actions_serialized"] is True and completion_atlas_v15["claim_flags"]["strict_386_unary_causal_common_snapshot_accepted"] is True, "completion atlas V15 omitted Green/snapshot successors")
    require(completion_atlas_v15["claim_flags"]["strict_pure_weyl_classical_gate_passed"] is False and completion_atlas_v15["claim_flags"]["strict_386_local_d_certified"] is False and completion_atlas_v15["claim_flags"]["lorentzian_full_theory_certified"] is False, "completion atlas V15 promoted Gate, D, or quantum theory")
    require(len(completion_atlas_v15["route_selection"]) == 8 and completion_atlas_v15["route_selection"][0]["route"] == "STRICT_386_FULL_D_ACTION", "completion atlas V15 frontier ordering drift")
    d_flags = strict_386_full_d["claim_flags"]
    require(strict_386_full_d["generator_selection"]["selected_real_generator"] == "T=partial_t" and strict_386_full_d["generator_selection"]["formal_adjoint_on_compact_support"] == "T^sharp=-T", "strict full-D generator convention drift")
    require(strict_386_full_d["exact_replay"]["D_rows_checked"] == 386 and strict_386_full_d["exact_replay"]["D_diagonal_coefficients_checked"] == 386, "strict full-D row inventory drift")
    require((strict_386_full_d["exact_replay"]["q1_operator_tables_checked"], strict_386_full_d["exact_replay"]["q1_derivative_multiindices_checked"], strict_386_full_d["exact_replay"]["q1_rational_coefficients_checked"]) == (27, 70, 4374), "strict D/q1 inventory drift")
    require(strict_386_full_d["exact_replay"]["D_q1_commutator_defects"] == 0 and strict_386_full_d["exact_replay"]["formal_skew_adjoint_pairing_entries_checked"] == 410 and strict_386_full_d["exact_replay"]["formal_skew_adjoint_defects"] == 0, "strict full-D exact replay drift")
    require(strict_386_full_d["extended_common_snapshot"]["accepted_object_hashes"] == 14 and strict_386_full_d["extended_common_snapshot"]["receiver_status"] == "ACCEPTED_SCOPED_D_EXTENSION", "strict unary-causal-D snapshot drift")
    require(d_flags["STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED"] is True and d_flags["STRICT_386_D_Q1_COMMUTATOR_REPLAYED"] is True and d_flags["STRICT_386_D_FORMAL_SKEW_ADJOINT_REPLAYED"] is True, "strict full-D positive flags missing")
    require(d_flags["STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT"] is False and d_flags["STRICT_386_D_Q2_DERIVATION_REPLAYED"] is False and d_flags["CLASSICAL_IMPORT_GATE_PASSED"] is False and d_flags["QME_RESTORED"] is False, "strict full-D result promoted q2, Gate A, or QME")
    require(gate_v6["gate_disposition"]["gate_a_status"] == "FAIL_CLOSED" and gate_v6["gate_disposition"]["same_theory_receiver_verified_scoped"] == 11 and gate_v6["gate_disposition"]["freeze_checks_receiver_verified_scoped"] == 8 and gate_v6["gate_disposition"]["accepted_common_snapshot_hashes"] == 0, "Gate V6 disposition drift")
    require(gate_v6["transitive_provenance_drift"]["files_checked"] == 21 and gate_v6["transitive_provenance_drift"]["drifted_files"] == 5 and gate_v6["transitive_provenance_drift"]["status"] == "DRIFT_RECORDED_GATE_REMAINS_FAIL_CLOSED", "Gate V6 provenance-drift ledger drift")
    require(gate_v6["claim_flags"]["STRICT_386_FULL_LOCAL_D_ACTION_SCOPED_REPLAY"] is True and gate_v6["claim_flags"]["STRICT_386_D_Q1_COMMUTATOR_SCOPED_REPLAY"] is True and gate_v6["claim_flags"]["STRICT_386_FULL_CARRIER_Q2"] is False and gate_v6["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is False, "Gate V6 scope firewall drift")
    require(completion_atlas_v16["strict_full_d_action"]["q1_coefficients_checked"] == 4374 and completion_atlas_v16["strict_gate_v6_reconciliation"]["transitive_provenance_drifted_files"] == 5, "completion atlas V16 D/Gate projection drift")
    require(completion_atlas_v16["claim_flags"]["strict_386_full_local_d_action_certified"] is True and completion_atlas_v16["claim_flags"]["strict_386_d_q1_commutator_replayed"] is True and completion_atlas_v16["claim_flags"]["strict_386_full_carrier_q2_certified"] is False and completion_atlas_v16["claim_flags"]["strict_pure_weyl_classical_gate_passed"] is False, "completion atlas V16 promotion boundary drift")
    require(len(completion_atlas_v16["route_selection"]) == 8 and completion_atlas_v16["route_selection"][0]["route"] == "STRICT_386_Q2_D_COMMON_CARRIER", "completion atlas V16 frontier ordering drift")
    q2_flags = strict_386_q2_preflight["claim_flags"]
    require((strict_386_q2_preflight["scope"]["carrier_rows"], strict_386_q2_preflight["scope"]["endpoint_rows"], strict_386_q2_preflight["scope"]["split_contractible_rows"]) == (386, 30, 356), "strict q2 preflight carrier drift")
    require((strict_386_q2_preflight["graph_transport_dag"]["expanded_ordered_component_channels"], strict_386_q2_preflight["graph_transport_dag"]["unique_block_triples"], strict_386_q2_preflight["graph_transport_dag"]["active_input_row_envelope"], strict_386_q2_preflight["graph_transport_dag"]["active_output_row_envelope"], strict_386_q2_preflight["graph_transport_dag"]["interaction_inert_rows"]) == (140, 68, 110, 110, 196), "strict q2 preflight support envelope drift")
    require(strict_386_q2_preflight["identity_transport"]["q1_q2_arity_two"]["defects"] == 0 and strict_386_q2_preflight["identity_transport"]["q2_koszul_symmetry"]["defects"] == 0 and strict_386_q2_preflight["identity_transport"]["q2_cyclicity"]["defects"] == 0 and strict_386_q2_preflight["identity_transport"]["D_q2_derivation"]["derivation_defects"] == 0, "strict q2 candidate identity drift")
    require(q2_flags["STRICT_386_STABILIZED_Q2_CANDIDATE_CONSTRUCTED"] is True and q2_flags["STRICT_386_STABILIZED_D_Q2_DERIVATION_VERIFIED"] is True and q2_flags["STRICT_386_AUTHORITATIVE_FULL_Q2_IMPORTED"] is False and q2_flags["STRICT_386_CANDIDATE_AUTHORITATIVE_EQUIVALENCE_CERTIFIED"] is False and q2_flags["CLASSICAL_IMPORT_GATE_PASSED"] is False, "strict q2 preflight authority firewall drift")
    require(gate_v7["gate_disposition"]["gate_a_status"] == "FAIL_CLOSED" and gate_v7["gate_disposition"]["same_theory_receiver_verified_scoped"] == 11 and gate_v7["gate_disposition"]["freeze_checks_receiver_verified_scoped"] == 8 and gate_v7["gate_disposition"]["freeze_checks_supporting_evidence_only"] == 1 and gate_v7["gate_disposition"]["accepted_common_snapshot_hashes"] == 0, "Gate V7 disposition drift")
    require(gate_v7["required_hash_disposition"]["q2_hash"]["accepted"] is None and gate_v7["claim_flags"]["STRICT_386_STABILIZED_Q2_CANDIDATE"] is True and gate_v7["claim_flags"]["STRICT_386_AUTHORITATIVE_FULL_CARRIER_Q2"] is False and gate_v7["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] is False, "Gate V7 candidate/import firewall drift")
    require(gate_v7["transitive_provenance_drift"]["files_checked"] == 23 and gate_v7["transitive_provenance_drift"]["drifted_files"] == 5, "Gate V7 provenance-drift ledger drift")
    require(completion_atlas_v17["strict_stabilized_q2_lift_preflight"]["expanded_component_channels"] == 140 and completion_atlas_v17["strict_gate_v7_reconciliation"]["accepted_top_level_hashes"] == 0, "completion atlas V17 q2/Gate projection drift")
    require(completion_atlas_v17["claim_flags"]["strict_386_stabilized_q2_candidate_certified"] is True and completion_atlas_v17["claim_flags"]["strict_386_authoritative_full_q2_imported"] is False and completion_atlas_v17["claim_flags"]["strict_pure_weyl_classical_gate_passed"] is False, "completion atlas V17 authority boundary drift")
    require(len(completion_atlas_v17["route_selection"]) == 8 and completion_atlas_v17["route_selection"][0]["route"] == "STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "completion atlas V17 frontier ordering drift")
    q2_green_flags = strict_386_q2_green["claim_flags"]
    require(strict_386_q2_green["carrier_alignment"]["carrier_rows"] == 386 and strict_386_q2_green["carrier_alignment"]["basis_match"] is True and strict_386_q2_green["carrier_alignment"]["pairing_match"] is True and strict_386_q2_green["carrier_alignment"]["graph_q1_match"] is True, "strict q2/Green carrier alignment drift")
    require(strict_386_q2_green["homotopy_response_replay"]["sign_orientations_checked"] == 2 and strict_386_q2_green["homotopy_response_replay"]["response_identity_structural_defects"] == 0 and strict_386_q2_green["homotopy_response_replay"]["causal_difference_identity_structural_defects"] == 0, "strict q2/Green response identity drift")
    require(strict_386_q2_green["local_q2_continuity"]["conservative_per_input_derivative_order_bound"] == 10 and strict_386_q2_green["local_q2_continuity"]["conservative_total_derivative_order_bound"] == 13, "strict q2/Green differential-order bound drift")
    require(strict_386_q2_green["foundational_strength"]["layers"][2]["completed_infinite_spaces_required"] is True and strict_386_q2_green["foundational_strength"]["weakest_complete_foundational_base"] == "NOT_ESTABLISHED", "strict q2/Green foundational boundary drift")
    require(q2_green_flags["STRICT_386_CANDIDATE_Q2_GREEN_RESPONSE_IDENTITY_VERIFIED"] is True and q2_green_flags["STRICT_386_AUTHORITATIVE_Q2_GREEN_COMPATIBILITY_CERTIFIED"] is False and q2_green_flags["STRICT_386_RECURSIVE_NONLINEAR_GREEN_TREES_CERTIFIED"] is False and q2_green_flags["HADAMARD_STATE_CONSTRUCTED"] is False and q2_green_flags["QME_RESTORED"] is False, "strict q2/Green lifecycle firewall drift")
    require(completion_atlas_v18["strict_q2_green_composition_preflight"]["response_identity_defects"] == 0 and completion_atlas_v18["strict_q2_green_composition_preflight"]["authoritative_q2_green_compatibility"] is False and completion_atlas_v18["strict_q2_green_composition_preflight"]["recursive_nonlinear_green_trees"] is False, "completion atlas V18 q2/Green projection drift")
    require(len(completion_atlas_v18["route_selection"]) == 9 and completion_atlas_v18["route_selection"][0]["route"] == "STRICT_386_AUTHORITATIVE_Q2_IDENTITY" and completion_atlas_v18["route_selection"][1]["route"] == "STRICT_RECURSIVE_CAUSAL_TREE_DOMAINS", "completion atlas V18 frontier ordering drift")
    tree_flags = strict_386_recursive_trees["claim_flags"]
    require(strict_386_recursive_trees["analytic_extension_import"]["theorem"] == "Theorem 3.8" and strict_386_recursive_trees["analytic_extension_import"]["source_pdf_sha256"] == "879948318de8b4a5a74b52179f78120d074bc7773734b82495b6db4c363f4c99", "recursive-tree analytic import drift")
    require(strict_386_recursive_trees["recursive_polarized_tree_theorem"]["retarded"]["all_finite_plane_binary_trees"] is True and strict_386_recursive_trees["recursive_polarized_tree_theorem"]["advanced"]["all_finite_plane_binary_trees"] is True and strict_386_recursive_trees["recursive_polarized_tree_theorem"]["finite_tree_support_domain_defects"] == 0, "recursive-tree polarized theorem drift")
    four = next(item for item in strict_386_recursive_trees["sign_decoration_census"] if item["leaves"] == 4)
    require((four["all_sign_decorations"], four["admissible_total"], four["not_uniformly_defined"]) == (40, 38, 2) and strict_386_recursive_trees["mixed_sign_boundary"]["first_uniform_failure_leaf_count"] == 4, "recursive-tree mixed-sign census drift")
    require(strict_386_recursive_trees["zero_mode_mismatch_witness"]["defects"] == 0 and "diverges quadratically" in strict_386_recursive_trees["zero_mode_mismatch_witness"]["advanced_on_PC_witness"], "recursive-tree zero-mode boundary drift")
    require(tree_flags["STRICT_386_CANDIDATE_RETARDED_ALL_FINITE_Q2_TREES_CERTIFIED"] is True and tree_flags["STRICT_386_CANDIDATE_ADVANCED_ALL_FINITE_Q2_TREES_CERTIFIED"] is True and tree_flags["STRICT_386_UNRESTRICTED_MIXED_SIGN_TREES_CERTIFIED"] is False and tree_flags["STRICT_386_INFINITE_TREE_SERIES_CONVERGENCE_CERTIFIED"] is False and tree_flags["STRICT_386_AUTHORITATIVE_Q2_RECURSIVE_TREES_CERTIFIED"] is False and tree_flags["HADAMARD_STATE_CONSTRUCTED"] is False and tree_flags["QME_RESTORED"] is False, "recursive-tree lifecycle firewall drift")
    require(completion_atlas_v19["strict_recursive_causal_tree_domains"]["retarded_all_finite_trees"] is True and completion_atlas_v19["strict_recursive_causal_tree_domains"]["four_leaf_admissible"] == 38 and completion_atlas_v19["strict_recursive_causal_tree_domains"]["four_leaf_not_uniformly_defined"] == 2, "completion atlas V19 recursive-tree projection drift")
    require(len(completion_atlas_v19["route_selection"]) == 11 and completion_atlas_v19["route_selection"][0]["route"] == "STRICT_386_AUTHORITATIVE_Q2_IDENTITY" and completion_atlas_v19["route_selection"][1]["route"] == "STRICT_POLARIZED_FORMAL_MOLLER_COEFFICIENTS", "completion atlas V19 frontier ordering drift")
    formal_flags = strict_386_formal["claim_flags"]
    formal_rows = strict_386_formal["catalan_tree_formula"]["checked_rows"]
    require(len(formal_rows) == 9 and formal_rows[-1]["leaves"] == 9 and formal_rows[-1]["plane_tree_count"] == 1430 and all(row["recurrence_residual"] == "0" for row in formal_rows), "formal coefficient census drift")
    require(strict_386_formal["bv_equation_diagnostic"]["order_lambda_residual"] == "q1(r_1)+(1/2)q2(x,x)=0" and strict_386_formal["bv_equation_diagnostic"]["order_lambda_squared_residual"] == "(1/4)(B_sigma(x,q2(x,x))+B_sigma(q2(x,x),x))" and strict_386_formal["bv_equation_diagnostic"]["order_lambda_squared_zero_certified"] is False, "formal BV diagnostic drift")
    require(formal_flags["STRICT_386_CANDIDATE_POLARIZED_FORMAL_COEFFICIENTS_CERTIFIED"] is True and formal_flags["STRICT_386_CANDIDATE_LAMBDA_ADIC_STABILIZATION_VERIFIED"] is True and formal_flags["STRICT_386_CANDIDATE_ANALYTIC_SERIES_CONVERGENCE_CERTIFIED"] is False and formal_flags["STRICT_386_WEYL_BV_MAURER_CARTAN_SERIES_CERTIFIED"] is False and formal_flags["STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED"] is False and formal_flags["QME_RESTORED"] is False, "formal coefficient lifecycle firewall drift")
    require(completion_atlas_v20["strict_polarized_formal_coefficients"]["largest_checked_tree_count"] == 1430 and completion_atlas_v20["strict_polarized_formal_coefficients"]["order_lambda_squared_bv_residual_zero_certified"] is False and completion_atlas_v20["strict_polarized_formal_coefficients"]["authoritative_weyl_bv_moller_map"] is False, "completion atlas V20 formal projection drift")
    require(len(completion_atlas_v20["route_selection"]) == 12 and [item["route"] for item in completion_atlas_v20["route_selection"][:3]] == ["STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "STRICT_TYPED_FIELD_EQUATION_GREEN_INVERSE", "STRICT_Q2_Q3_MAURER_CARTAN_CLOSURE"], "completion atlas V20 frontier ordering drift")
    typed = strict_386_field_inverse["typed_complex"]
    identities = strict_386_field_inverse["restricted_homotopy_identities"]
    obstruction = strict_386_field_inverse["full_inverse_obstruction"]
    require(typed["degree_counts"]["0"] == 116 and typed["degree_counts"]["1"] == 116 and typed["gauge_map"]["nonzero_rational_jet_coefficients"] == 425 and typed["field_equation_operator"]["nonzero_rational_jet_coefficients"] == 3264 and typed["noether_map"]["nonzero_rational_jet_coefficients"] == 425, "typed field-equation census drift")
    require(identities["source_identity"] == "K G_sigma + A_sigma N = identity_C1" and identities["field_identity"] == "G_sigma K + R C_sigma = identity_C0" and identities["structural_defects"] == 0, "typed field-equation identities drift")
    require(obstruction["full_left_inverse_of_K_on_C0"] is False and obstruction["full_right_inverse_of_K_on_C1"] is False and obstruction["status"] == "EXACT_GAUGE_COMPLEX_OBSTRUCTION", "full ungauge-fixed inverse obstruction drift")
    require(completion_atlas_v21["strict_field_equation_green_quotient_inverse"]["constrained_right_inverse"] is True and completion_atlas_v21["strict_field_equation_green_quotient_inverse"]["quotient_left_inverse"] is True and completion_atlas_v21["strict_field_equation_green_quotient_inverse"]["full_ungauge_fixed_two_sided_inverse"] is False, "completion atlas V21 typed inverse projection drift")
    require(len(completion_atlas_v21["route_selection"]) == 11 and [item["route"] for item in completion_atlas_v21["route_selection"][:2]] == ["STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "STRICT_Q2_Q3_SOURCE_COCYCLE_CLOSURE"], "completion atlas V21 frontier ordering drift")
    quadratic = strict_386_quadratic_obstruction["quadratic_truncation_disposition"]
    require(quadratic["quadratic_only_lambda_squared_source_closed"] is False and quadratic["witness_jacobiator_weyl_identity"] == "75760/27" and quadratic["witness_source_closure_defect"] == "37880/27" and quadratic["required_q3_q1_image_on_witness"] == "-75760/9", "quadratic-truncation obstruction drift")
    require(completion_atlas_v22["strict_quadratic_truncation_lambda2_source_obstruction"]["authoritative_q3_required"] is True and completion_atlas_v22["strict_quadratic_truncation_lambda2_source_obstruction"]["authoritative_q3_imported"] is False and completion_atlas_v22["strict_quadratic_truncation_lambda2_source_obstruction"]["not_a_full_weyl_no_go"] is True, "completion atlas V22 q3 boundary drift")
    require([item["route"] for item in completion_atlas_v22["route_selection"][:2]] == ["STRICT_AUTHORITATIVE_Q2_Q3_ARITY_THREE_EXPORT", "STRICT_LAMBDA2_FULL_SOURCE_COCYCLE_CLOSURE"], "completion atlas V22 frontier ordering drift")
    cubic = strict_386_q3_witness["exact_cubic_fixture"]
    cancellation = strict_386_q3_witness["arity_three_cancellation"]
    berger = next(item for item in strict_386_q3_witness["q3_source_compatibility"]["sources"] if item["source_id"] == "BERGER_SUPPORT_LOCAL_Q3")
    q3_flags = strict_386_q3_witness["claim_flags"]
    require(cubic["metric_output_term_count"] == 41 and cubic["nonzero_metric_output_rows"] == 10 and cubic["q1_q3_weyl_noether"] == "-75760/9", "pure-Weyl cubic witness census drift")
    require(all(value == "0" for value in cubic["q1_q3_diff_noether"].values()) and cubic["nonlinear_weyl_identity_t3"] == "0", "pure-Weyl cubic Noether identities drift")
    require(cancellation["arity_three_defect"] == "0" and cancellation["full_lambda2_source_q1_defect_on_witness"] == "0" and cancellation["witness_source_closure"] is True and cancellation["general_full_source_closure"] is False, "pure-Weyl cubic cancellation boundary drift")
    require(berger["strict_386_direct_import"] is False and berger["disposition"] == "NO_CERTIFIED_SAME_THEORY_CARRIER_MAP" and berger["nonexistence_claimed"] is False, "Berger q3 compatibility boundary drift")
    require(q3_flags["STRICT_PURE_WEYL_METRIC_Q3_DIAGONAL_WITNESS_DERIVED"] is True and q3_flags["STRICT_PURE_WEYL_Q3_WITNESS_CANCELLATION_CERTIFIED"] is True and q3_flags["STRICT_386_WITNESS_FULL_SOURCE_CLOSURE_CERTIFIED"] is True and q3_flags["STRICT_386_ARBITRARY_INPUT_Q3_CERTIFIED"] is False and q3_flags["STRICT_386_FULL_BV_ARITY_THREE_IDENTITY_CERTIFIED"] is False and q3_flags["CLASSICAL_IMPORT_GATE_PASSED"] is False and q3_flags["HADAMARD_STATE_CONSTRUCTED"] is False and q3_flags["QME_RESTORED"] is False, "pure-Weyl q3 lifecycle firewall drift")
    v23_projection = completion_atlas_v23["strict_pure_weyl_q3_witness"]
    require(v23_projection["metric_q3_term_count"] == 41 and v23_projection["lambda2_witness_source_q1_defect"] == "0" and v23_projection["authoritative_arbitrary_input_q3_imported"] is False and v23_projection["Berger_disposition"] == "NO_CERTIFIED_SAME_THEORY_CARRIER_MAP", "completion atlas V23 q3 projection drift")
    require([item["route"] for item in completion_atlas_v23["route_selection"][:3]] == ["STRICT_AUTHORITATIVE_ARBITRARY_FULL_BV_Q2_Q3_EXPORT", "STRICT_ARITY_THREE_386_CYCLIC_STABILIZATION", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE"], "completion atlas V23 frontier ordering drift")
    require(classical_minimal_q3["claim_flags"]["AUTHORITATIVE_MINIMAL_BV_Q3_EXPORTED"] is True and classical_minimal_q3["claim_flags"]["ALL_SIX_MINIMAL_OUTPUT_ROWS_CLASSIFIED"] is True and classical_minimal_q3["claim_flags"]["STRICT_386_NONMINIMAL_Q3_STABILIZED"] is False, "classical minimal-q3 export boundary drift")
    minimal_checks = strict_minimal_q3["exact_receiver_checks"]
    require(minimal_checks["S3_input_permutations_replayed"] == 6 and minimal_checks["S3_exact_symmetry"] is True and minimal_checks["seven_diagonal_polarization"]["exact_equality"] is True and minimal_checks["pinned_diagonal_witness"]["metric_output_term_count"] == 41 and minimal_checks["pinned_diagonal_witness"]["q1_q3_weyl_noether"] == "-75760/9", "minimal-q3 independent receiver drift")
    arity_inventory = strict_minimal_arity3["channel_inventory"]
    require(arity_inventory["channel_count"] == 72 and arity_inventory["composable_path_count"] == 212 and arity_inventory["path_kind_counts"] == {"q1_q3": 2, "q2_q2": 204, "q3_q1": 6}, "minimal arity-three channel census drift")
    require(strict_minimal_arity3["claim_flags"]["MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED"] is True and strict_minimal_arity3["claim_flags"]["Q3_SIGN_MUTATIONS_DETECTED"] is True and strict_minimal_arity3["claim_flags"]["STRICT_386_Q3_STABILIZED"] is False, "minimal arity-three lifecycle boundary drift")
    cyclic_form = strict_minimal_q3_cyclicity["cyclic_four_form"]
    require(cyclic_form["permutation_group"] == "S4" and cyclic_form["cyclicity_defect_mod_d"] == "0" and strict_minimal_q3_cyclicity["claim_flags"]["QUARTIC_METRIC_VERTEX_S4_SYMMETRIC_MOD_D"] is True and strict_minimal_q3_cyclicity["claim_flags"]["STRICT_386_Q3_STABILIZED"] is False, "minimal q3 cyclicity boundary drift")
    v24_q3 = completion_atlas_v24["strict_minimal_q3_completion"]
    require(v24_q3["arbitrary_three_metric_inputs"] is True and v24_q3["arity_three_channels"] == 72 and v24_q3["arity_three_paths"] == 212 and v24_q3["quartic_permutation_group"] == "S4" and v24_q3["strict_386_q3_stabilized"] is False and v24_q3["classical_import_gate_a_passed"] is False, "completion atlas V24 minimal/386 projection drift")
    require([item["route"] for item in completion_atlas_v24["route_selection"][:3]] == ["STRICT_ARITY_THREE_386_CYCLIC_STABILIZATION", "STRICT_NONMINIMAL_THEORY_IDENTITY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE"], "completion atlas V24 frontier ordering drift")
    q3_dag = strict_386_q3_preflight["graph_transport_dag"]
    q3_identity = strict_386_q3_preflight["identity_transport"]
    q3_theory = strict_386_q3_preflight["theory_identity_boundary"]
    require(q3_dag["expanded_ternary_block_channels"] == 16 and q3_dag["active_input_row_envelope"] == 50 and q3_dag["active_output_row_envelope"] == 50 and q3_dag["interaction_inert_rows"] == 286, "386-row candidate q3 DAG census drift")
    require(q3_identity["q1_q2_q3_arity_three"]["minimal_typed_channels"] == 72 and q3_identity["q1_q2_q3_arity_three"]["minimal_composable_paths"] == 212 and q3_identity["q1_q2_q3_arity_three"]["defects"] == 0 and q3_identity["q3_cyclicity_mod_d"]["defects_mod_d"] == 0 and q3_identity["D_q3_derivation"]["derivation_defects"] == 0, "386-row candidate q3 identity transport drift")
    require(q3_theory["candidate_equals_authoritative_nonminimal_classical_theory"] == "NOT_ESTABLISHED" and q3_theory["candidate_causal_lambda2_source_closure"] is False and strict_386_q3_preflight["claim_flags"]["STRICT_386_AUTHORITATIVE_FULL_Q3_IMPORTED"] is False, "386-row candidate q3 authority firewall drift")
    v25_q3 = completion_atlas_v25["strict_386_stabilized_q3_preflight"]
    require(v25_q3["candidate_q3_stabilized"] is True and v25_q3["authoritative_full_q3_imported"] is False and v25_q3["authoritative_nonminimal_equivalence"] is False and v25_q3["candidate_causal_lambda2_source_closure"] is False and v25_q3["classical_import_gate_a_passed"] is False, "completion atlas V25 candidate/authority projection drift")
    require([item["route"] for item in completion_atlas_v25["route_selection"][:3]] == ["STRICT_NONMINIMAL_THEORY_IDENTITY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE"], "completion atlas V25 frontier ordering drift")
    classical_channel = classical_aux_cubic["auxiliary_cubic_interaction"]
    require(classical_channel["candidate_block_channel"] == ["AUX_F_HAT", "AUX_V", "AUX_V"] and classical_channel["witness"]["mixed_derivative_d_t_d_s_squared_at_zero"] == "-1" and classical_aux_cubic["theory_identity_disposition"]["cyclic_L_infinity_equivalence_obstructed"] is False, "classical auxiliary cubic export drift")
    identity_channel = strict_identity_obstruction["exact_channel_comparison"]
    identity_disposition = strict_identity_obstruction["theory_identity_disposition"]
    require(identity_channel["cyclic_form_channel"] == "Omega(f_hat,q2(v,v))" and identity_channel["source_ordinary_derivative_value"] == "-1" and identity_channel["candidate_trivial_stabilization_value"] == "0" and identity_channel["source_minus_candidate_defect"] == "-1" and identity_channel["literal_identity"] is False, "strict nonminimal identity obstruction drift")
    require(identity_disposition["candidate_internal_q1_q2_and_cyclicity_certificates_preserved"] is True and identity_disposition["candidate_is_authoritative_ordinary_derivative_nonminimal_theory"] is False and identity_disposition["linear_canonical_shear_suffices_for_theory_identity"] is False and identity_disposition["nonlinear_canonical_or_L_infinity_equivalence_may_exist"] is True and identity_disposition["nonlinear_equivalence_constructed"] is False, "strict nonlinear-equivalence firewall drift")
    v26_identity = completion_atlas_v26["strict_nonminimal_theory_identity_obstruction"]
    require(v26_identity["source_minus_candidate_defect"] == "-1" and v26_identity["literal_identity_refuted"] is True and v26_identity["linear_shear_only_identity_refuted"] is True and v26_identity["nonlinear_equivalence_may_exist"] is True and v26_identity["nonlinear_equivalence_constructed"] is False and v26_identity["nonlinear_equivalence_obstructed"] is False and v26_identity["classical_import_gate_a_passed"] is False, "completion atlas V26 identity projection drift")
    gate_v8_m2 = gate_v8["m2_theory_identity_obstruction"]
    require(gate_v8["gate_disposition"]["gate_a_status"] == "FAIL_CLOSED" and gate_v8["gate_disposition"]["accepted_common_snapshot_hashes"] == 0 and gate_v8["required_hash_disposition"]["q2_hash"]["accepted"] is None, "Gate V8 hash/Gate-A firewall drift")
    require(gate_v8_m2["source_value"] == "-1" and gate_v8_m2["candidate_value"] == "0" and gate_v8_m2["defect"] == "-1" and gate_v8_m2["nonlinear_equivalence_may_exist"] is True and gate_v8_m2["nonlinear_equivalence_constructed"] is False and gate_v8_m2["nonlinear_equivalence_obstructed"] is False, "Gate V8 nonlinear-equivalence disposition drift")
    require(completion_atlas_v26["strict_gate_v8_reconciliation"]["result_id"] == gate_v8["result_id"] and completion_atlas_v26["strict_gate_v8_reconciliation"]["accepted_top_level_hashes"] == 0, "completion atlas V26 Gate V8 projection drift")
    require([item["route"] for item in completion_atlas_v26["route_selection"][:4]] == ["STRICT_NONLINEAR_AUXILIARY_ELIMINATION_MAP_Q2", "STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY", "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE"], "completion atlas V26 frontier ordering drift")
    quadratic_fixture = classical_quadratic_map["quadratic_auxiliary_map"]["fixture"]
    require(classical_quadratic_map["quadratic_auxiliary_map"]["source_to_split_homogeneous_quadratic_component"] == "F_(2)(v)=v tensor v-(1/2)g v^2" and quadratic_fixture["source_f_hat_v_v_mixed_polarization"] == "-1" and quadratic_fixture["inverse_shift_mass_cross_mixed_polarization"] == "1" and quadratic_fixture["corrected_channel_residual"] == "0", "authoritative quadratic auxiliary map drift")
    channel_replay = strict_quadratic_channel["channel_pullback_replay"]
    require(channel_replay["carrier_rows"] == 386 and channel_replay["pre_correction_source_value"] == "-1" and channel_replay["inverse_shift_mass_cross_correction"] == "1" and channel_replay["transformed_source_value"] == "0" and channel_replay["candidate_value"] == "0" and channel_replay["transformed_source_minus_candidate_residual"] == "0" and channel_replay["support_local"] is True and channel_replay["uses_green_operator"] is False and channel_replay["uses_choice_principle"] is False, "independent quadratic channel replay drift")
    require(strict_quadratic_channel["equivalence_boundary"]["receiver_componentwise_386_cotangent_lift_serialized"] is False and strict_quadratic_channel["equivalence_boundary"]["complete_source_q2_pullback_replayed"] is False and strict_quadratic_channel["equivalence_boundary"]["complete_source_q3_pullback_replayed"] is False and strict_quadratic_channel["equivalence_boundary"]["full_cyclic_L_infinity_equivalence_constructed"] is False, "quadratic channel full-equivalence firewall drift")
    require(gate_v9["gate_disposition"]["gate_a_status"] == "FAIL_CLOSED" and gate_v9["gate_disposition"]["accepted_common_snapshot_hashes"] == 0 and gate_v9["required_hash_disposition"]["q2_hash"]["accepted"] is None, "Gate V9 hash/Gate-A firewall drift")
    v27_quadratic = completion_atlas_v27["strict_quadratic_auxiliary_elimination"]
    require(v27_quadratic["source_before_correction"] == "-1" and v27_quadratic["inverse_shift_correction"] == "1" and v27_quadratic["transformed_source"] == "0" and v27_quadratic["candidate"] == "0" and v27_quadratic["residual"] == "0", "completion atlas V27 nonlinear-component projection drift")
    require([item["route"] for item in completion_atlas_v27["route_selection"][:3]] == ["STRICT_NONLINEAR_SHIFT_CUBIC_CHANNEL_INVENTORY", "STRICT_386_BV_COTANGENT_LIFT_COMPONENTS", "STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY"], "completion atlas V27 frontier ordering drift")
    classical_mass = classical_shifted_cubic["shifted_auxiliary_mass_vertex"]
    classical_vv = classical_shifted_cubic["quadratic_vv_field_map"]
    require(classical_mass["nonzero_component_monomials"] == 72 and classical_mass["pure_trace_h_check_count"] == 55 and classical_mass["pure_trace_h_defects"] == 0, "classical shifted-mass component table drift")
    require(classical_vv["nonzero_homogeneous_component_coefficients"] == 22 and classical_shifted_cubic["inventory_completeness"]["known_required_cubic_block_families_enumerated"] == 7 and classical_shifted_cubic["inventory_completeness"]["exhaustive_full_nonlinear_BV_family_census"] is False, "classical vv/family census drift")
    strict_lift = strict_shifted_cubic["vv_BV_cotangent_lift"]
    strict_complete = strict_shifted_cubic["inventory_completeness"]
    strict_comparison = strict_shifted_cubic["candidate_comparison"]
    require((strict_lift["carrier_rows"], strict_lift["field_map_nonzero_component_coefficients"], strict_lift["cotangent_partner_nonzero_component_coefficients"], strict_lift["quadratic_active_output_rows"], strict_lift["quadratic_zero_output_rows"], len(strict_lift["canonicality_slices"]), strict_lift["canonicality_defects"]) == (386, 22, 16, 14, 372, 4, 0), "strict vv BV cotangent-lift census drift")
    require((strict_complete["component_coefficient_complete_families"], strict_complete["component_coefficient_open_families"]) == (2, 5) and strict_complete["vv_BV_cotangent_lift_component_complete"] is True and strict_complete["hh_hv_BV_cotangent_lift_component_complete"] is False and strict_complete["diffeomorphism_BV_representation_component_complete"] is False and strict_complete["exhaustive_full_nonlinear_BV_family_census"] is False and strict_complete["full_386_quadratic_BV_cotangent_lift_serialized"] is False, "strict shifted-cubic completeness firewall drift")
    require(strict_comparison["new_exact_source_candidate_component_defect_count"] == 72 and strict_comparison["further_metric_dependent_canonical_or_L_infinity_normalization_may_exist"] is True and strict_comparison["full_nonlinear_equivalence_obstructed"] is False, "strict shifted-mass comparison boundary drift")
    require(gate_v10["gate_disposition"]["gate_a_status"] == "FAIL_CLOSED" and gate_v10["gate_disposition"]["accepted_common_snapshot_hashes"] == 0 and gate_v10["required_hash_disposition"]["q2_hash"]["accepted"] is None, "Gate V10 hash/Gate-A firewall drift")
    require([item["route"] for item in completion_atlas_v28["route_selection"][:3]] == ["STRICT_SECOND_FRECHET_HH_HV_AUXILIARY_SHIFT_COMPONENTS", "STRICT_DIFF_AUXILIARY_BV_REPRESENTATION_COMPONENTS", "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST"], "completion atlas V28 three-front ordering drift")
    require(completion_atlas_v28["strict_gate_v10_reconciliation"]["gate_a_status"] == "FAIL_CLOSED" and completion_atlas_v28["strict_shifted_auxiliary_cubic_inventory"]["vv_canonicality_defects"] == 0 and completion_atlas_v28["claim_flags"]["strict_386_nonlinear_equivalence_constructed"] is False and completion_atlas_v28["claim_flags"]["strict_386_nonlinear_equivalence_obstructed"] is False, "completion atlas V28 promotion firewall drift")
    require(flags["strict_386_field_equation_green_component_typed"] is True and flags["strict_386_field_equation_constrained_right_inverse_certified"] is True and flags["strict_386_field_equation_quotient_left_inverse_certified"] is True and flags["strict_386_ungauge_fixed_full_inverse_obstructed"] is True and flags["strict_386_q2_only_lambda2_source_obstructed"] is True and flags["strict_386_authoritative_q3_cancellation_target_exact"] is True and flags["strict_386_authoritative_q3_imported"] is False and flags["strict_386_full_weyl_lambda2_source_closure_certified"] is False and flags["strict_386_all_order_nonlinear_source_closure_certified"] is False, "typed inverse/nonlinear lifecycle firewall drift")
    require(flags["strict_pure_weyl_metric_q3_witness_derived"] is True and flags["strict_pure_weyl_q3_witness_cancellation_certified"] is True and flags["strict_386_lambda2_witness_full_source_closed"] is True and flags["strict_386_Berger_q3_direct_import_compatible"] is False and flags["strict_386_arbitrary_input_q3_certified"] is False and flags["strict_386_full_bv_arity_three_identity_certified"] is False, "paper cubic-witness authority firewall drift")
    require(flags["strict_authoritative_minimal_q3_imported"] is True and flags["strict_minimal_full_bv_arity_three_identity_certified"] is True and flags["strict_minimal_q3_cyclicity_certified"] is True and flags["strict_386_q3_stabilized"] is False, "paper minimal-q3/386 firewall drift")
    require(flags["strict_386_candidate_q3_stabilized"] is True and flags["strict_386_candidate_full_bv_arity_three_identity_certified"] is True and flags["strict_386_candidate_q3_cyclicity_mod_d_certified"] is True and flags["strict_386_candidate_d_q3_derivation_certified"] is True, "paper candidate q3 stabilization flags missing")
    require(flags["strict_386_authoritative_nonminimal_equivalence_certified"] is False and flags["strict_386_candidate_causal_lambda2_source_closure_certified"] is False, "paper candidate q3 authority/causal firewall drift")
    require(flags["strict_386_literal_trivial_stabilization_identity_refuted"] is True and flags["strict_386_linear_shear_theory_identity_refuted"] is True and flags["strict_386_candidate_internal_identities_preserved"] is True and flags["strict_386_nonlinear_equivalence_may_exist"] is True, "paper theory-identity obstruction flags missing")
    require(flags["strict_386_nonlinear_equivalence_constructed"] is False and flags["strict_386_nonlinear_equivalence_obstructed"] is False, "paper nonlinear-equivalence boundary drift")
    require(flags["classical_import_gate_v8_fail_closed"] is True, "paper Gate V8 fail-closed flag missing")
    require(flags["strict_386_first_nonlinear_equivalence_component_constructed"] is True and flags["strict_386_f_hat_v_v_pullback_channel_closed"] is True and flags["strict_386_quadratic_auxiliary_map_support_local"] is True, "paper first nonlinear component flags missing")
    require(flags["strict_386_quadratic_auxiliary_map_uses_green_operator"] is False and flags["strict_386_quadratic_auxiliary_map_uses_choice_principle"] is False, "paper auxiliary map foundations boundary drift")
    require(flags["strict_386_full_cotangent_lift_serialized"] is False and flags["strict_386_full_source_q2_q3_pullback_replayed"] is False and flags["classical_import_gate_v9_fail_closed"] is True, "paper Gate V9/full-pullback firewall drift")
    require(flags["strict_386_known_required_cubic_families_enumerated"] is True and flags["strict_386_shifted_mass_h_f_hat_f_hat_components_imported"] is True and flags["strict_386_vv_field_map_components_imported"] is True and flags["strict_386_vv_cotangent_partner_components_serialized"] is True and flags["strict_386_vv_bv_cotangent_lift_canonical"] is True, "paper shifted-cubic/vv BV flags missing")
    require(flags["strict_386_exhaustive_full_nonlinear_bv_family_census"] is False and flags["strict_386_hh_hv_bv_cotangent_lift_component_complete"] is False and flags["strict_386_diff_bv_representation_component_complete"] is False and flags["classical_import_gate_v10_fail_closed"] is True, "paper Gate V10/exhaustive-lift firewall drift")
    require(flags["static_atlas_appendix_generated"] is True, "static atlas appendix flag is not certified")
    require(flags["complete_evidence_register_generated"] is True, "complete evidence register flag is not certified")
    require(flags["complete_literature_register_generated"] is True, "complete literature register flag is not certified")
    require(flags["evidence_usage_crosswalk_generated"] is True, "evidence crosswalk flag is not certified")
    require(flags["model_scoped_end_to_end_assembly_generated"] is True, "model-scoped assembly flag is not certified")
    require(flags["bounded_empirical_comparison_registered"] is True, "bounded empirical comparison flag is not certified")
    require(flags["mannheim_ngc3198_mixed_assembly_registered"] is True, "Mannheim mixed assembly flag is not certified")
    require(flags["ngc3198_common_fit_comparison_registered"] is True, "NGC 3198 common-fit flag is not certified")
    require(flags["bt_euclidean_finite_capabilities_imported"] is True, "BT finite import flag is not certified")
    require(flags["bt_euclidean_coarse_reproduction_separated"] is True, "BT numerical separation flag is not certified")
    require(flags["bt_free_os_obstruction_certified"] is True, "BT OS obstruction flag is not certified")
    require(flags["bt_free_h_minus_one_estimate_certified"] is True, "BT free uniform estimate flag is not certified")
    require(flags["bt_lambda_0p4_os_status_decided"] is True, "BT lambda=0.4 exact OS status missing")
    require(flags["bt_all_nonzero_coupling_even_volume_os_obstruction_certified"] is True, "BT all-coupling even-volume OS obstruction flag missing")
    require(flags["bt_fixed_observable_continuum_os_decided"] is False, "BT fixed-observable continuum OS boundary promoted")
    require(flags["bt_lambda_0p4_two_sampler_sign_support"] is True, "BT interacting sign-support flag missing")
    require(flags["bt_interacting_uniform_h_minus_one_established"] is False, "BT interacting H^-1 bound promoted")
    require(flags["bt_half_action_density_candidate_established"] is False, "BT half-action-density candidate promoted")
    require(flags["bt_actual_interacting_action_density_established"] is True, "BT actual action-density theorem missing")
    require(flags["bt_actual_annealed_half_action_factor_established"] is True, "BT annealed half-action theorem missing")
    require(flags["bt_global_orthogonal_hessian_block_obstructed"] is True, "BT orthogonal Hessian obstruction flag missing")
    require(flags["bt_pointwise_half_action_curvature_route_obstructed"] is True, "BT half-action curvature obstruction flag missing")
    require(flags["bt_residual_spectrahedral_pushforward_established"] is True, "BT residual spectrahedral pushforward flag missing")
    require(flags["bt_vertex_transitive_entropy_jacobian_minimum_established"] is True, "BT entropy Jacobian minimum flag missing")
    require(flags["bt_normalized_lowest_mode_marginal_established"] is False, "BT normalized marginal flag promoted")
    require(flags["bt_residual_pointwise_strict_convexity_established"] is True, "BT residual strict-convexity flag missing")
    require(flags["bt_residual_uniform_positive_curvature_established"] is False, "BT residual uniform-curvature flag promoted")
    require(flags["bt_residual_positive_weighted_mean_curvature_established"] is False, "BT residual weighted-mean-curvature flag promoted")
    require(flags["bt_standard_boundary_curvature_spectral_gap_route_obstructed"] is True, "BT boundary curvature route obstruction flag missing")
    require(flags["bt_residual_tilt_jacobian_cancellation_established"] is True, "BT residual tilt cancellation flag missing")
    require(flags["bt_tree_log_convexity_extra_tilt_confinement_obstructed"] is True, "BT tree tilt confinement obstruction flag missing")
    require(flags["bt_direct_action_fiber_bound_established"] is False, "BT action-fiber bound promoted")
    require(flags["bt_centered_pointwise_fiber_domination_obstructed"] is True, "BT centered fiber obstruction flag missing")
    require(flags["bt_integrated_lowest_mode_marginal_evenness_established"] is True, "BT marginal evenness flag missing")
    require(flags["bt_annealed_recentered_fiber_bound_established"] is False, "BT annealed fiber bound promoted")
    require(flags["bt_conditional_mass_escape_established"] is True, "BT conditional mass escape flag missing")
    require(flags["bt_uniform_backgroundwise_raw_conditional_moment_obstructed"] is True, "BT raw conditional moment obstruction flag missing")
    require(flags["bt_uniform_recentered_conditional_variance_established"] is True, "BT all-background recentered conditional variance theorem omitted")
    require(flags["bt_all_background_lowest_mode_curvature_established"] is True, "BT all-background curvature theorem omitted")
    require(flags["bt_all_background_lowest_mode_curvature_absorption_established"] is True, "BT plaquette absorption theorem omitted")
    require(flags["bt_all_background_recentered_conditional_variance_established"] is True, "BT all-background conditional variance theorem omitted")
    require(flags["bt_annealed_center_second_moment_established"] is False, "BT width theorem promoted to annealed center bound")
    require(flags["bt_center_to_zero_fiber_score_reduction_established"] is True, "BT center-to-score reduction omitted")
    require(flags["bt_fixed_bare_coefficientwise_score_route_obstructed"] is True, "BT fixed-order score obstruction omitted")
    require(flags["bt_nonperturbative_annealed_score_established"] is False, "BT fixed-order obstruction promoted to a nonperturbative result")
    require(flags["bt_score_log_residue_established"] is True, "BT score logarithmic residue omitted")
    require(flags["bt_rg_matched_leading_score_uniformity_restored"] is True, "BT RG-matched leading score result omitted")
    require(flags["bt_fixed_spacing_large_volume_score_established"] is False, "BT RG refinement result promoted to fixed-spacing large volume")
    require(flags["bt_ordinary_eom_score_identity_established"] is True, "BT ordinary EOM score identity omitted")
    require(flags["bt_eom_to_zero_fiber_general_transfer_obstructed"] is True, "BT EOM-to-zero-fiber no-transfer omitted")
    require(flags["bt_specific_zero_fiber_ward_identity_established"] is False, "BT-specific zero-fiber Ward identity promoted")
    require(flags["bt_quartic_score_kernel_established"] is True, "BT quartic score kernel omitted")
    require(flags["bt_isolated_quartic_score_square_uniformity_obstructed"] is True, "BT isolated quartic-square obstruction omitted")
    require(flags["bt_complete_order_g_four_score_established"] is False, "BT isolated quartic result promoted to complete order g4")
    require(flags["bt_quartic_power_cancellation_established"] is False, "BT quartic power cancellation promoted")
    require(flags["bt_complete_order_g_four_formula_established"] is True, "BT complete order-g4 formula omitted")
    require(flags["bt_complete_order_g_four_uv_noncancellation_established"] is True, "BT complete order-g4 UV noncancellation omitted")
    require(flags["bt_complete_order_g_four_whole_lattice_decided"] is True, "BT downstream whole-lattice decision omitted")
    require(flags["bt_complete_order_g_four_ir_complement_bounded"] is False, "BT infrared complement promoted")
    require(flags["bt_complete_order_g_four_chaos_decomposition_established"] is True, "BT order-g4 chaos decomposition omitted")
    require(flags["bt_complete_order_g_four_signed_gate_reduced_to_second_chaos"] is True, "BT signed second-chaos reduction omitted")
    require(flags["bt_complete_order_g_four_expected_hessian_formula_established"] is True, "BT expected-Hessian formula omitted")
    require(flags["bt_complete_order_g_four_conditioning_finite_rank_decomposition_established"] is True, "BT conditioning finite-rank split omitted")
    require(flags["bt_complete_order_g_four_connected_reorganization_established"] is True, "BT connected reorganization omitted")
    require(flags["bt_complete_order_g_four_normalization_alignment_established"] is True, "BT normalization alignment omitted")
    require(flags["bt_complete_order_g_four_termwise_alignment_bound_obstructed"] is True, "BT termwise alignment obstruction omitted")
    require(flags["bt_complete_order_g_four_connected_maximum_loop_rank_two"] is True, "BT connected loop-rank result omitted")
    require(flags["bt_complete_order_g_four_exact_cancellation_established"] is False, "BT connected preflight promoted to exact cancellation")
    require(flags["bt_complete_order_g_four_conditioned_maximum_loop_rank_two"] is True, "BT conditioned loop-rank result omitted")
    require(flags["bt_complete_order_g_four_l4_negative_nonzero_established"] is True, "BT exact L4 result omitted")
    require(flags["bt_complete_order_g_four_all_volume_zero_identity_obstructed"] is True, "BT all-volume zero-identity obstruction omitted")
    require(flags["bt_complete_order_g_four_large_volume_scaling_established"] is True, "BT downstream large-volume scaling omitted")
    require(flags["bt_complete_order_g_four_general_l_two_loop_formula_established"] is True, "BT general-L two-loop formula omitted")
    require(flags["bt_complete_order_g_four_power_tadpoles_canceled"] is True, "BT exact power-tadpole cancellation omitted")
    require(flags["bt_complete_order_g_four_factorized_conditioning_log_squared_bound_established"] is True, "BT factorized conditioning bound omitted")
    require(flags["bt_complete_order_g_four_factorized_tuned_branch_uniformity_established"] is True, "BT tuned factorized-sector consequence omitted")
    require(flags["bt_complete_order_g_four_remaining_fourteen_kernel_bound_established"] is True, "BT downstream fourteen-kernel result omitted")
    require(flags["bt_complete_order_g_four_fourteen_to_seven_reduction_established"] is True, "BT fourteen-to-seven reduction omitted")
    require(flags["bt_complete_order_g_four_paired_quartic_bound_established"] is True, "BT paired-quartic bound omitted")
    require(flags["bt_complete_order_g_four_negative_nested_L2_carrier_established"] is True, "BT negative nested L2 carrier omitted")
    require(flags["bt_complete_order_g_four_termwise_tuned_uniformity_obstructed"] is True, "BT termwise tuned uniformity obstruction omitted")
    require(flags["bt_complete_order_g_four_combined_seven_kernel_scaling_established"] is True, "BT complete seven-kernel scaling omitted")
    require(flags["bt_complete_order_g_four_pairs_1_2_5_log_squared_established"] is True, "BT three-pair log-squared bounds omitted")
    require(flags["bt_complete_order_g_four_pairs_1_2_5_tuned_uniformity_established"] is True, "BT three-pair tuned uniformity omitted")
    require(flags["bt_complete_order_g_four_power_gate_reduced_to_pairs_3_4_6_7"] is True, "BT four-pair power reduction omitted")
    require(flags["bt_complete_order_g_four_four_pair_power_coefficient_established"] is True, "BT four-pair power coefficient omitted")
    require(flags["bt_complete_order_g_four_pair_three_O_L_established"] is True, "BT pair-3 O(L) bound omitted")
    require(flags["bt_complete_order_g_four_pair_six_O_L_log_L_established"] is True, "BT pair-6 O(L log L) bound omitted")
    require(flags["bt_complete_order_g_four_power_gate_reduced_to_pairs_4_7"] is True, "BT two-pair power gate omitted")
    require(flags["bt_complete_order_g_four_pair_4_7_coefficient_established"] is True, "BT pair-4/pair-7 coefficient omitted")
    require(flags["bt_complete_order_g_four_pair_4_limit_established"] is True, "BT pair-4 limit omitted")
    require(flags["bt_complete_order_g_four_pair_4_coefficient_below_minus_0_01613"] is True, "BT pair-4 rational gap omitted")
    require(flags["bt_complete_order_g_four_pair_7_limit_established"] is True, "BT pair-7 limit omitted")
    require(flags["bt_complete_order_g_four_pair_7_positive_finite"] is True, "BT pair-7 sign or finiteness omitted")
    require(flags["bt_complete_order_g_four_pair_4_7_noncancellation_established"] is True, "BT two-pair noncancellation omitted")
    require(bt_g4_two_pair_noncancellation["comparison"]["combined"] == "c_4+c_7<0", "BT strict two-pair sign drift")
    require(bt_g4_two_pair_noncancellation["method_disposition"]["complete_M4_large_volume_sign_and_scaling"] == "OPEN", "BT complete M4 promoted")
    require(flags["bt_complete_order_g_four_zero_loop_limit_established"] is True, "BT zero-loop limit omitted")
    require(flags["bt_complete_order_g_four_one_loop_log_bound_established"] is True, "BT one-loop bound omitted")
    require(flags["bt_complete_order_g_four_lower_loops_subpower_established"] is True, "BT lower-loop subpower theorem omitted")
    require(flags["bt_complete_order_g_four_complete_leading_coefficient_negative"] is True, "BT complete M4 leading sign omitted")
    require(flags["bt_complete_order_g_four_tuned_perturbative_uniformity_established"] is False, "BT perturbative uniformity promoted")
    require(flags["bt_tuned_fixed_order_uniform_remainder_obstructed"] is True, "BT tuned uniform-remainder obstruction omitted")
    require(flags["bt_tuned_leading_power_compensation_required"] is True, "BT tuned compensation theorem omitted")
    require(flags["bt_radial_convexity_obstructed"] is True, "BT radial-convexity obstruction omitted")
    require(flags["bt_unit_homogeneous_virial_obstructed"] is True, "BT unit virial obstruction omitted")
    require(flags["bt_subunit_positive_homogeneous_virial_established"] is False, "BT positive subunit virial promoted despite obstruction")
    require(flags["bt_any_nonnegative_homogeneous_virial_obstructed"] is True, "BT complete nonnegative homogeneous virial no-go omitted")
    require(flags["bt_pointwise_nonnegative_radial_virial_obstructed"] is True, "BT pointwise virial sign no-go omitted")
    require(flags["bt_gibbs_weighted_block_estimate_established"] is False, "BT pointwise no-go promoted to Gibbs estimate")
    require(flags["bt_energy_only_bubble_rarity_obstructed"] is True, "BT energy-only bubble-rarity obstruction omitted")
    require(flags["bt_quadratic_bubble_score_soft_factor_established"] is True, "BT quadratic bubble soft factor omitted")
    require(flags["bt_dilute_bubble_score_activity_vanishes"] is True, "BT dilute score activity balance omitted")
    require(flags["bt_interacting_multibubble_cluster_bound_established"] is False, "BT dilute balance promoted to cluster theorem")
    require(flags["bt_full_phase_background_translation_invariance_established"] is True, "BT full-phase translation invariance omitted")
    require(flags["bt_full_phase_current_divergence_identity_established"] is True, "BT canonical-current identity omitted")
    require(flags["bt_canonical_current_pointwise_second_factor_obstructed"] is True, "BT canonical second-factor obstruction omitted")
    require(flags["bt_weighted_random_conductance_current_identity_established"] is True, "BT weighted-current identity omitted")
    require(flags["bt_corrector_pointwise_action_route_obstructed"] is True, "BT corrector action-route no-go omitted")
    require(flags["bt_corrector_pointwise_dirichlet_route_obstructed"] is True, "BT corrector Dirichlet-route no-go omitted")
    require(flags["bt_corrector_Gibbs_hyperuniformity_established"] is False, "BT pointwise no-go promoted to Gibbs theorem")
    require(flags["bt_corrector_slab_fiber_stability_established"] is True, "BT slab fiber stability omitted")
    require(flags["bt_corrector_slab_point_density_suppression_established"] is True, "BT slab point-density suppression omitted")
    require(flags["bt_corrector_slab_neighborhood_probability_established"] is True, "BT slab-cylinder probability theorem omitted")
    require(flags["bt_corrector_global_tail_established"] is False, "single slab cylinder promoted to global corrector tail")
    require(bt_corrector_slab_cylinder["method_disposition"]["localized_slab_positive_radius_cylinder_probability"] == "PROVED_EXPONENTIALLY_SUPPRESSED", "BT slab-cylinder authority drift")
    require(bt_corrector_slab_cylinder["gibbs_cylinder_probability"]["lambda_point_four_exponent"] == {"numerator": 403338322161150510073, "denominator": 453757769960991129600}, "BT slab-cylinder exponent drift")
    require(bt_corrector_slab_cylinder["method_disposition"]["all_large_corrector_backgrounds_contain_certified_cylinders"] == "OPEN", "BT slab cylinder promoted to all large correctors")
    require(flags["bt_translation_invariant_flux_corrector_established"] is False, "BT flux corrector promoted")
    require(flags["bt_translation_invariant_current_susceptibility_established"] is False, "BT current susceptibility promoted")
    require(flags["bt_exact_interacting_score_scaling_established"] is False, "BT exact interacting score promoted")
    require(flags["bt_actual_interacting_H_minus_one_established"] is False, "BT interacting H-minus-one promoted")
    require(atlas["bt_g4_zero_loop_limit"] == bt_g4_lower_loops["zero_loop"]["large_volume_limit"] == "lim_(L->infinity) M4_zero(L)=111/(32*pi^4)", "BT zero-loop limit drift")
    require(atlas["bt_g4_one_loop_scaling_status"] == bt_g4_lower_loops["one_loop_summary"]["asymptotic_status"] == "O_LOG_L_AND_little_o_N_omega_p", "BT one-loop scaling drift")
    require(atlas["bt_g4_complete_leading_power_status"] == bt_g4_lower_loops["complete_leading_power"]["status"] == "COMPLETE_M4_LEADING_POWER_COEFFICIENT_STRICTLY_NEGATIVE", "BT complete leading-power drift")
    require(atlas["bt_tuned_remainder_compensation_status"] == bt_tuned_remainder["exact_balance"]["status"] == "LEADING_POWER_COMPENSATION_FORCED", "BT tuned compensation drift")
    require(atlas["bt_tuned_remainder_gap"] == bt_tuned_remainder["coefficient_gap"]["gap"] == {"numerator": 13403, "denominator": 500000000}, "BT tuned gap drift")
    require(atlas["bt_tuned_exact_score_status"] == bt_tuned_remainder["method_disposition"]["sign_or_scaling_of_exact_interacting_score"] == "OPEN", "BT exact score promoted")
    require(atlas["bt_radial_convexity_status"] == bt_radial_convexity["method_disposition"]["radial_convexity_of_A_rho_psi"] == "OBSTRUCTED", "BT radial-convexity obstruction drift")
    require(atlas["bt_unit_virial_status"] == bt_radial_convexity["method_disposition"]["pointwise_D_ge_A"] == "OBSTRUCTED", "BT unit virial obstruction drift")
    require(atlas["bt_subunit_positive_virial_status"] == bt_log_bubble["method_disposition"]["pointwise_D_ge_cA_for_any_c_ge_0"] == "OBSTRUCTED", "BT nonnegative homogeneous virial no-go drift")
    require(atlas["bt_pointwise_nonnegative_virial_status"] == bt_log_bubble["method_disposition"]["pointwise_D_ge_0"] == "OBSTRUCTED", "BT pointwise virial sign no-go drift")
    require(atlas["bt_gibbs_weighted_block_estimate_status"] == bt_log_bubble["method_disposition"]["nonpointwise_Gibbs_weighted_block_estimate"] == "OPEN", "BT log bubble promoted to Gibbs theorem")
    require(bt_log_bubble["method_disposition"]["actual_interacting_H_minus_one_second_moment"] == "OPEN", "BT log bubble promoted to H-minus-one theorem")
    require(bt_log_bubble["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "BT log-bubble dependency boundary drift")
    require(atlas["bt_bubble_energy_only_rarity_status"] == bt_bubble_balance["method_disposition"]["energy_only_bubble_rarity_bound"] == "OBSTRUCTED", "BT energy-only bubble-rarity status drift")
    require(atlas["bt_bubble_dilute_score_activity_status"] == bt_bubble_balance["method_disposition"]["dilute_single_bubble_score_weighted_activity"] == "VANISHES", "BT dilute score activity status drift")
    require(atlas["bt_bubble_multibubble_cluster_status"] == bt_bubble_balance["method_disposition"]["interacting_multibubble_cluster_bound"] == "OPEN", "BT dilute balance promoted to multibubble theorem")
    require(atlas["bt_bubble_reduced_action"] == bt_bubble_balance["optimized_wall"]["reduced_action"] == {"numerator": 1965963925, "denominator": 733296564}, "BT optimized bubble action drift")
    require(atlas["bt_bubble_positive_entropy_gap"] == bt_bubble_balance["tuned_entropy_balance"]["positive_entropy_gap"] == {"numerator": 1902925399, "denominator": 2933186256}, "BT bubble entropy gap drift")
    require(bt_bubble_balance["method_disposition"]["actual_annealed_zero_fiber_score_bound"] == "OPEN", "BT dilute balance promoted to actual score theorem")
    require(bt_bubble_balance["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "BT bubble-balance dependency boundary drift")
    require(atlas["bt_full_phase_background_translation_status"] == bt_full_phase_current["method_disposition"]["full_cosine_sine_background_translation_invariance"] == "PROVED", "BT full-phase translation status drift")
    require(atlas["bt_full_phase_current_identity_status"] == bt_full_phase_current["method_disposition"]["canonical_current_divergence_identity"] == "PROVED", "BT canonical-current identity drift")
    require(atlas["bt_full_phase_pointwise_second_factor_status"] == bt_weighted_current_v2["method_disposition"]["slice_valid_unweighted_periodic_gradient_identity"] == "OBSTRUCTED", "BT slice-valid second-factor status drift")
    require(atlas["bt_full_phase_weighted_current_status"] == bt_weighted_current_v2["method_disposition"]["weighted_random_conductance_gradient_identity"] == "PROVED", "BT weighted-current identity drift")
    require(atlas["bt_full_phase_flux_corrector_status"] == bt_weighted_current_v2["method_disposition"]["translation_invariant_flux_corrector_bound"] == "OPEN", "BT flux corrector promoted")
    require(atlas["bt_full_phase_current_susceptibility_status"] == bt_weighted_current_v2["method_disposition"]["translation_invariant_current_susceptibility_bound"] == "OPEN", "BT current susceptibility promoted")
    require(atlas["bt_full_phase_fixture_current_zero_mode"] == bt_weighted_current_v2["slice_valid_fixture"]["full_time_current_zero_mode"] == {"numerator": -24, "denominator": 1}, "BT slice-valid current fixture drift")
    require(bt_weighted_current_v2["method_disposition"]["v1_fixture_as_full_phase_slice_witness"] == "WITHDRAWN_SCOPE_ERROR", "BT V1 fixture scope error omitted")
    require(bt_weighted_current_v2["method_disposition"]["actual_interacting_H_minus_one_second_moment"] == "OPEN", "BT weighted-current gate promoted to H-minus-one theorem")
    require(bt_weighted_current_v2["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "BT weighted-current dependency boundary drift")
    require(atlas["bt_corrector_pointwise_action_route_status"] == bt_corrector_energy_no_go["method_disposition"]["pointwise_corrector_bound_by_N_omega_action"] == "OBSTRUCTED", "BT corrector action-route status drift")
    require(atlas["bt_corrector_pointwise_dirichlet_route_status"] == bt_corrector_energy_no_go["method_disposition"]["pointwise_corrector_bound_by_N_omega_weighted_dirichlet_energy"] == "OBSTRUCTED", "BT corrector Dirichlet-route status drift")
    require(atlas["bt_corrector_Gibbs_hyperuniformity_status"] == bt_corrector_energy_no_go["method_disposition"]["Gibbs_corrector_hyperuniformity_bound"] == "OPEN", "BT pointwise corrector no-go promoted to Gibbs theorem")
    require(atlas["bt_corrector_action_ratio_linear_coefficient"] == bt_corrector_energy_no_go["diverging_ratios"]["action_ratio_linear_coefficient"] == {"numerator": 49, "denominator": 360096}, "BT corrector ratio coefficient drift")
    require(bt_corrector_energy_no_go["method_disposition"]["actual_interacting_H_minus_one_second_moment"] == "OPEN", "BT corrector no-go promoted to H-minus-one theorem")
    require(bt_corrector_energy_no_go["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "BT corrector no-go dependency boundary drift")
    require(atlas["bt_corrector_slab_fiber_action_escape_status"] == bt_corrector_slab_fiber["method_disposition"]["localized_slab_two_mode_fiber_action_escape"] == "OBSTRUCTED", "BT slab fiber stability drift")
    require(atlas["bt_corrector_slab_point_density_escape_status"] == bt_corrector_slab_fiber["method_disposition"]["localized_slab_integrated_marginal_point_density_escape"] == "OBSTRUCTED", "BT slab point-density status drift")
    require(atlas["bt_corrector_slab_neighborhood_probability_status"] == bt_corrector_slab_fiber["method_disposition"]["localized_slab_neighborhood_probability_bound"] == "OPEN", "BT point density promoted to neighborhood probability")
    require(atlas["bt_corrector_slab_fiber_action_coefficient"] == bt_corrector_slab_fiber["fiber_action_lower_bound"]["coefficient"] == {"numerator": 2683, "denominator": 800}, "BT slab fiber coefficient drift")
    require(bt_corrector_slab_fiber["method_disposition"]["Gibbs_corrector_hyperuniformity_bound"] == "OPEN", "BT slab stability promoted to Gibbs corrector theorem")
    require(bt_corrector_slab_fiber["method_disposition"]["actual_interacting_H_minus_one_second_moment"] == "OPEN", "BT slab stability promoted to H-minus-one theorem")
    require(bt_corrector_slab_fiber["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "BT slab fiber dependency boundary drift")
    require(bt_full_phase_current["method_disposition"]["actual_interacting_H_minus_one_second_moment"] == "OPEN", "BT full-phase reduction promoted to H-minus-one theorem")
    require(bt_full_phase_current["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], "BT full-phase dependency boundary drift")
    require(atlas["bt_g4_interacting_H_minus_one_status"] == "OPEN", "BT interacting H-minus-one atlas promotion")
    require(flags["bt_complete_order_g_four_explicit_momentum_kernel_established"] is False, "BT expected-Hessian formula promoted to explicit momentum kernel")
    require(flags["bt_complete_order_g_four_effective_kernel_bound_established"] is False, "BT effective second-chaos kernel bound promoted")
    require(flags["bt_complete_order_g_four_power_survival_established"] is True, "BT whole-lattice power noncancellation omitted")
    require(flags["bt_runaway_family_recentered_conditional_variance_established"] is True, "BT runaway-family recentered variance flag missing")
    require(flags["bt_runaway_family_conditional_mean_escape_established"] is True, "BT runaway-family conditional-mean escape flag missing")
    require(flags["bt_annealed_center_second_moment_established"] is False, "BT annealed center moment promoted")
    require(flags["research_programme_lenses_explained"] is True, "research-programme exposition flag is not certified")
    require(flags["coded_wave_observable_reconstruction_certified"] is True, "coded observable reconstruction flag is not certified")
    require(flags["coded_local_weak_wave_test_class_certified"] is True, "localized weak-wave flag is not certified")
    require(flags["coded_local_weak_wave_all_smooth_tests_covered"] is False, "finite localized span promoted to every smooth test")
    require(flags["coded_local_weak_wave_causal_support_proved"] is False, "localized weak identity promoted to causal support")
    require(flags["coded_h2_test_completion_certified"] is True, "named H2 completion flag is not certified")
    require(flags["coded_h2_represented_smooth_tests_covered"] is True, "represented smooth-test flag missing")
    require(flags["coded_h2_full_lf_topology_reconstructed"] is False, "named H2 completion promoted to LF topology")
    require(flags["coded_h2_arbitrary_distribution_uniqueness_proved"] is False, "energy-image uniqueness promoted")
    require(flags["coded_h2_causal_support_proved"] is False, "named weak solution promoted to causal support")
    require(flags["fixed_support_smooth_to_h2_translator_certified"] is True, "smooth translator flag missing")
    require(flags["fixed_support_translator_uses_choice"] is False, "smooth translator choice flag promoted")
    require(flags["support_indexed_name_equivalence_certified"] is True, "support-indexed equivalence flag missing")
    require(flags["support_indexed_full_lf_topology_reconstructed"] is False, "support-indexed comparison promoted to LF topology")
    require(flags["scalar_minkowski_green_certified"] is True, "scalar Green flag missing")
    require(flags["scalar_minkowski_causal_support_proved"] is True, "scalar causal-support flag missing")
    require(flags["scalar_green_promoted_to_weyl_bv"] is False, "scalar Green flag promoted to Weyl/BV")
    require(flags["scalar_minkowski_biwave_certified"] is True, "scalar biwave flag missing")
    require(flags["scalar_biwave_four_zero_data_certified"] is True, "scalar biwave four-data flag missing")
    require(flags["weyl_bv_dependency_delta_certified"] is True, "Weyl/BV dependency delta flag missing")
    require(flags["weyl_bv_classical_import_gate_passed"] is False, "classical import gate promoted")
    require(flags["full_weyl_bv_propagator_constructed"] is False, "dependency delta promoted to full propagator")
    require(flags["new_lorentzian_claim"] is True, "scoped scalar Lorentzian claim missing")
    for false_flag in [
        "weakest_foundation_proved",
        "global_physics_implies_choice_theorem",
        "axes_independent_proved",
        "atlas_exhaustive",
        "literature_complete",
        "quantum_lifecycle_promoted",
    ]:
        require(flags[false_flag] is False, f"fail-closed flag promoted: {false_flag}")

    paper_path = ROOT / data["paper"]["path"]
    require(sha256(paper_path) == data["paper"]["sha256"], "paper source hash drift")
    appendix_record = data["paper"]["appendix"]
    appendix_path = ROOT / appendix_record["path"]
    atlas_data_path = ROOT / appendix_record["source_path"]
    assembly_data_path = ROOT / appendix_record["assembly_source_path"]
    appendix_generator_path = ROOT / appendix_record["generator_path"]
    require(appendix_path.is_file(), "generated paper appendix is missing")
    require(sha256(appendix_path) == appendix_record["sha256"], "generated appendix hash drift")
    require(sha256(atlas_data_path) == appendix_record["source_sha256"], "appendix atlas-source hash drift")
    require(sha256(assembly_data_path) == appendix_record["assembly_source_sha256"], "appendix assembly-source hash drift")
    require(sha256(appendix_generator_path) == appendix_record["generator_sha256"], "appendix generator hash drift")
    atlas_data = json.loads(atlas_data_path.read_text())
    assembly_data = json.loads(assembly_data_path.read_text())
    require(atlas_data["canonical_digest"] == appendix_record["source_canonical_digest"], "appendix atlas-source digest drift")
    require(assembly_data["canonical_digest"] == appendix_record["assembly_source_canonical_digest"], "appendix assembly-source digest drift")
    require(atlas["axis_options"] == sum(len(axis["keys"]) for axis in atlas_data["axes"]) == 28, "appendix axis-option mismatch")
    require(atlas["implication_nodes"] == len(atlas_data["graph"]["nodes"]) == 12, "appendix implication-node mismatch")
    require(atlas["implication_edges"] == len(atlas_data["graph"]["edges"]) == 10, "appendix implication-edge mismatch")
    require(atlas["strength_ladder_levels"] == len(atlas_data["ladder"]) == 6, "appendix ladder-level mismatch")
    require(atlas["prototype_assemblies"] == len(assembly_data["assemblies"]) == 9, "appendix assembly-count mismatch")
    require(atlas["research_programme_lenses"] == 9, "research-programme lens metadata mismatch")
    require(atlas["model_scoped_assemblies"] == len(assembly_data["model_scoped_assemblies"]) == 2, "model-scoped assembly-count mismatch")
    model = next(item for item in assembly_data["model_scoped_assemblies"] if item["result_id"] == gr_cassini["result_id"])
    mannheim_model = next(item for item in assembly_data["model_scoped_assemblies"] if item["result_id"] == mannheim_ngc3198["result_id"])
    require(model["result_id"] == gr_cassini["result_id"], "GR/Cassini model assembly identity drift")
    require(model["canonical_digest"] == gr_cassini["canonical_digest"], "GR/Cassini embedded assembly digest drift")
    require(atlas["gr_cassini_stages"] == len(gr_cassini["stages"]) == 6, "GR/Cassini stage-count mismatch")
    require(atlas["gr_cassini_interfaces"] == len(gr_cassini["interfaces"]) == 5, "GR/Cassini interface-count mismatch")
    require(atlas["gr_cassini_required_obligations"] == gr_cassini["applicability_summary"]["required"] == 3, "GR/Cassini applicability count mismatch")
    require(atlas["gr_cassini_required_obligations_satisfied"] == 3, "GR/Cassini required obligations are not closed")
    require(atlas["gr_cassini_bounded_complete"] is gr_cassini["assembly_disposition"]["complete_within_declared_scope"] is True, "GR/Cassini bounded completion is not certified")
    require(atlas["gr_cassini_prediction_inside_reported_band"] is gr_cassini["empirical_comparison_rail"]["prediction_inside_reported_band"] is True, "GR/Cassini comparison is not supported in the reported band")
    require(gr_cassini["assembly_disposition"]["complete_theory"] is False, "bounded GR assembly promoted to complete theory")
    require(gr_cassini["claim_flags"]["raw_cassini_data_reanalysed"] is False, "Cassini literature comparison promoted to raw-data reanalysis")
    require(mannheim_model["canonical_digest"] == mannheim_ngc3198["canonical_digest"], "Mannheim embedded assembly digest drift")
    require(atlas["mannheim_ngc3198_stages"] == len(mannheim_ngc3198["stages"]) == 7, "Mannheim stage-count mismatch")
    require(atlas["mannheim_ngc3198_interfaces"] == len(mannheim_ngc3198["interfaces"]) == 6, "Mannheim interface-count mismatch")
    require(atlas["mannheim_ngc3198_endpoint_coarse_gate_passed"] is True, "Mannheim endpoint coarse gate not reproduced")
    require(atlas["mannheim_ngc3198_sparc_coarse_gate_passed"] is True, "Mannheim SPARC coarse RMS gate did not pass")
    require(atlas["mannheim_ngc3198_sparc_random_error_gate_passed"] is False, "Mannheim random-error gate incorrectly promoted")
    require(atlas["mannheim_ngc3198_empirically_supported"] is False, "Mannheim assembly incorrectly promoted to empirical support")
    require(atlas["ngc3198_common_fit_models"] == len(ngc3198_common_fit["models"]) == 3, "common-fit family count drift")
    require(atlas["ngc3198_common_fit_ranking_AICc"] == ngc3198_common_fit["ranking_by_AICc"], "common-fit AICc ranking drift")
    require(atlas["ngc3198_common_fit_random_error_passes"] == ["GR_NFW_DARK_HALO"], "common-fit gate disposition drift")
    require(atlas["ngc3198_common_fit_complete_theory_selected"] is False, "common-fit promoted to complete theory")
    require(abs(atlas["mannheim_ngc3198_sparc_rms_km_s"] - 4.5382719695501885) < 1e-12, "Mannheim SPARC RMS drift")
    require(abs(atlas["mannheim_ngc3198_sparc_reduced_chi2"] - 5.592211904260559) < 1e-12, "Mannheim SPARC chi-squared drift")
    standard = next(item for item in assembly_data["assemblies"] if item["id"] == "STANDARD_MIXED_REFERENCE")
    require(atlas["standard_reference_direct_obligations"] == standard["coverage"]["direct"] == 16, "classical reference coverage mismatch")
    control = assembly_data["calibration_controls"][0]
    require(atlas["external_calibration_records"] == len(control["records"]) == 4, "calibration record mismatch")
    require(atlas["external_calibration_benchmark_families"] == sum(item["status"] == "SUPPORTED_CONTROL" for item in control["benchmark_coverage"]) == 3, "calibration benchmark mismatch")

    appendix = appendix_path.read_text()
    for token in ("Bateman--Turok", "Mannheim conformal-gravity programme", "Pure-Weyl BV--BFV"):
        require(token in appendix, f"research-programme lens missing from appendix: {token}")
    require(r"All obligations & 127 & 90 & 160 & 30 & 169 & 0 & 576" in appendix, "appendix coverage totals drift")
    require("contains 83 evidence records: 32 local result records and 51 literature records" in appendix, "appendix evidence summary drift")
    require("BT positive Euclidean lattice programme" in appendix, "BT Euclidean prototype missing")
    require("COARSE REPRODUCTION ONLY" in appendix, "BT numerical boundary missing")
    require("The classical-standard mixed-carrier reference has complete direct coverage" in appendix, "classical reference calibration missing")
    require("First bounded end-to-end assembly" in appendix, "model-scoped GR/Cassini appendix section missing")
    require("The six typed stages of the standard-GR solar-exterior assembly" in appendix, "GR/Cassini stage table missing")
    require(tex(gr_cassini["assembly_disposition"]["status"].replace("_", " ").lower()) in appendix, "GR/Cassini bounded disposition missing")
    require("applicability mask requires 3" in appendix, "GR/Cassini applicability summary missing")
    for stage in gr_cassini["stages"]:
        require(tex(stage["label"]) in appendix, f"GR/Cassini stage missing: {stage['id']}")
        require(scientific_tex(stage["establishes"]) in appendix, f"GR/Cassini stage boundary missing: {stage['id']}")
    require("Second bounded assembly: mixed result" in appendix, "Mannheim mixed appendix section missing")
    require("The seven typed stages of the Mannheim conformal-gravity NGC 3198 assembly" in appendix, "Mannheim stage table missing")
    require("No parameter is refitted" in appendix, "Mannheim no-refit boundary missing")
    require(r"reduced $\chi^2$" in appendix, "Mannheim failed random-error metric missing")
    require("Common-protocol NGC 3198 control" in appendix, "common-fit appendix section missing")
    require("GR plus NFW dark halo" in appendix, "common-fit NFW row missing")
    require("AICc penalizes the two extra NFW parameters" in appendix, "common-fit penalty boundary missing")
    for stage in mannheim_ngc3198["stages"]:
        require(tex(stage["label"]) in appendix, f"Mannheim stage missing: {stage['id']}")
        require(scientific_tex(stage["establishes"]) in appendix, f"Mannheim stage boundary missing: {stage['id']}")
    for record in control["records"]:
        require(tex(record["citation"]) in appendix, f"calibration citation missing: {record['id']}")
        require(tex(record["boundary"]) in appendix, f"calibration boundary missing: {record['id']}")
    for axis in atlas_data["axes"]:
        for option in axis["keys"]:
            require(option["label"] in appendix, f"axis option missing from appendix: {option['id']}")
    for edge in atlas_data["graph"]["edges"]:
        fragment = edge["meaning"].replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")
        require(fragment in appendix, f"implication edge missing from appendix: {edge['from']} -> {edge['to']}")
    for step in atlas_data["ladder"]:
        require(rf"\cert{{{step['level']}}}" in appendix, f"ladder gate missing from appendix: {step['level']}")
    linked_evidence = {
        evidence_id
        for edge in atlas_data["graph"]["edges"]
        for evidence_id in edge.get("evidence", [])
    } | {step["source"] for step in atlas_data["ladder"] if step.get("source")}
    for evidence_id in linked_evidence:
        require(rf"\cert{{{evidence_id}}}" in appendix, f"linked evidence missing from appendix: {evidence_id}")

    evidence = atlas_data["evidence"]
    require(appendix.count(r"\hypertarget{atlas-evidence-") == 83, "evidence-register anchor count drift")
    require(appendix.count(r"\hyperlink{atlas-evidence-") == 83, "evidence-crosswalk link count drift")
    cell_usage = {evidence_id: [] for evidence_id in evidence}
    for cell in atlas_data["cells"]:
        for evidence_id in cell.get("evidence", []):
            require(evidence_id in evidence, f"cell references unknown evidence: {evidence_id}")
            cell_usage[evidence_id].append(cell)
    graph_usage = collections.defaultdict(list)
    for edge_number, edge in enumerate(atlas_data["graph"]["edges"], start=1):
        for evidence_id in edge.get("evidence", []):
            require(evidence_id in evidence, f"graph references unknown evidence: {evidence_id}")
            graph_usage[evidence_id].append(edge_number)
    ladder_usage = collections.defaultdict(list)
    for step in atlas_data["ladder"]:
        if step.get("source"):
            require(step["source"] in evidence, f"ladder references unknown evidence: {step['source']}")
            ladder_usage[step["source"]].append(step["level"])
    status_order = ["LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"]
    status_short = {
        "LOCAL_RESULT": "Local",
        "LITERATURE_RESULT": "Literature",
        "PIECES_ONLY": "Pieces",
        "PRIORITY_GAP": "Priority gap",
        "REVIEWED_GAP": "Reviewed gap",
        "NOT_MAPPED": "Not mapped",
    }

    for number, (evidence_id, entry) in enumerate(sorted(evidence.items()), start=1):
        anchor = f"atlas-evidence-{number}"
        require(
            rf"\hypertarget{{{anchor}}}{{\cert{{{evidence_id}}}}}" in appendix,
            f"evidence register entry missing: {evidence_id}",
        )
        require(
            rf"\hyperlink{{{anchor}}}{{\cert{{{evidence_id}}}}}" in appendix,
            f"evidence crosswalk entry missing: {evidence_id}",
        )
        require(cell_usage[evidence_id], f"evidence record has no matrix usage: {evidence_id}")
        status_counts = collections.Counter(cell["status"] for cell in cell_usage[evidence_id])
        status_summary = ", ".join(
            f"{status_short[status]} {status_counts[status]}"
            for status in status_order
            if status_counts[status]
        )
        matrix_use = f"{len(cell_usage[evidence_id])} coordinates ({status_summary})."
        target = rf"\hyperlink{{{anchor}}}{{\cert{{{evidence_id}}}}}"
        target += " (literature)" if entry["kind"] == "LITERATURE" else " (local)"
        require(
            f"{target} & {tex(matrix_use)} &" in appendix,
            f"matrix usage count missing: {evidence_id}",
        )
        if graph_usage[evidence_id]:
            require(
                "graph edges " + ", ".join(map(str, graph_usage[evidence_id])) in appendix,
                f"graph crosswalk missing: {evidence_id}",
            )
        if ladder_usage[evidence_id]:
            require(
                tex("ladder " + ", ".join(ladder_usage[evidence_id])) in appendix,
                f"ladder crosswalk missing: {evidence_id}",
            )
        if entry["kind"] == "LITERATURE":
            for field in ["citation", "source_kind", "artifact_status", "stable_url", "supported_statements", "boundary"]:
                require(field in entry, f"literature record lacks {field}: {evidence_id}")
            require(tex(entry["citation"]) in appendix, f"literature citation missing: {evidence_id}")
            require(rf"\url{{{entry['stable_url']}}}" in appendix, f"literature URL missing: {evidence_id}")
            require(rf"\cert{{{entry['artifact_status']}}}" in appendix, f"artifact status missing: {evidence_id}")
            for statement in entry["supported_statements"]:
                require(tex(statement) in appendix, f"supported statement missing: {evidence_id}")
            require(tex(entry["boundary"]) in appendix, f"literature boundary missing: {evidence_id}")
        else:
            for field in ["result_path", "report_path", "result_kind", "lifecycle", "dependency_tags", "claim_flags", "does_not_establish"]:
                require(field in entry, f"local record lacks {field}: {evidence_id}")
            require(rf"\cert{{{entry['result_path']}}}" in appendix, f"result locator missing: {evidence_id}")
            require(rf"\cert{{{entry['report_path']}}}" in appendix, f"report locator missing: {evidence_id}")
            for tag in entry["dependency_tags"]:
                require(tag in appendix, f"local dependency tag missing: {evidence_id} / {tag}")
            for exclusion in entry["does_not_establish"]:
                require(tex(exclusion) in appendix, f"local boundary item missing: {evidence_id}")
            for flag, enabled in entry["claim_flags"].items():
                if enabled:
                    require(tex(flag.replace("_", " ")) in appendix, f"local positive flag missing: {evidence_id} / {flag}")

    paper = paper_path.read_text()
    prose = " ".join(paper.split())
    for phrase in [
        r"L+S+M+\Enc(P)",
        r"The cube is not an ontology",
        r"State existence is not state selection",
        r"Weak wave evolution is not causal Green theory",
        r"N(k)=k+\ell(K)+1",
        r"diagonal of exact rank ten",
        r"does not cover every smooth compactly supported test",
        r"Compare the represented union with the full LF topology",
        r"N_W(k)=k+\ell(\lceil4E\rceil)",
        r"nonmetrizable LF",
        r"uniqueness only inside the represented energy solution image",
        r"FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1",
        r"FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1",
        r"FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1",
        r"FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1",
        r"FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1",
        r"STRICT_386_GRAPH_GREEN_ACTION_NAME_V1",
        r"STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15",
        r"Thirteen hashes fix the",
        r"accepts zero of its seven required top-level hashes",
        r"STRICT_386_FULL_D_ACTION_V1",
        r"CLASSICAL_IMPORT_GATE_V6_RECONCILIATION",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16",
        r"4,374 rational coefficients",
        r"five of twenty-one files",
        r"full-carrier extension of strict \(q_2\)",
        r"STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1",
        r"CLASSICAL_IMPORT_GATE_V7_RECONCILIATION",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17",
        r"STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V18",
        r"STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19",
        r"STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V20",
        r"STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21",
        r"STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V22",
        r"STRICT_386_PURE_WEYL_Q3_WITNESS_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23",
        r"CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1",
        r"STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1",
        r"STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1",
        r"STRICT_MINIMAL_BV_Q3_CYCLICITY_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24",
        r"STRICT_386_STABILIZED_Q3_LIFT_PREFLIGHT_V1",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25",
        r"CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1",
        r"STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1",
        r"CLASSICAL_IMPORT_GATE_V8_RECONCILIATION",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V26",
        r"CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1",
        r"STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1",
        r"CLASSICAL_IMPORT_GATE_V9_RECONCILIATION",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27",
        r"CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1",
        r"STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1",
        r"CLASSICAL_IMPORT_GATE_V10_RECONCILIATION",
        r"FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V28",
        r"72 nonzero",
        r"16 cotangent-partner",
        r"14 output rows",
        r"other 372",
        r"three Diff auxiliary BV representation vertices",
        r"41 exact rational",
        r"NO_CERTIFIED_SAME_THEORY_CARRIER_MAP",
        r"STRICT_NONMINIMAL_THEORY_IDENTITY",
        r"STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        r"STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        r"STRICT_NONLINEAR_AUXILIARY_ELIMINATION_MAP_Q2",
        r"STRICT_SOURCE_Q2_Q3_PULLBACK_IDENTITY",
        r"all 72 typed channels and 212 composable",
        r"140 ordered-component channels",
        r"68 potentially nonzero block triples",
        r"cyclic \(L_\infty\) isomorphism",
        r"zero of seven authoritative hashes",
        r"STRICT_AUTHORITATIVE_Q2_Q3_ARITY_THREE_EXPORT",
        r"STRICT_LAMBDA2_FULL_SOURCE_COCYCLE_CLOSURE",
        r"37880/27",
        r"q_1(q_3(x,x,x))",
        r"Catalan",
        r"lambda squared",
        r"first nonlinear causal response",
        r"Thirty-eight",
        r"past-compact smooth sources",
        r"completed LF/Fréchet spaces",
        r"This is a genuine \rtype{LORENTZIAN-CAUSAL} result",
        r"not a Weyl/BV propagator or quantum causal construction",
        r"Exact finite causality is not continuum causality",
        r"none of the case studies constructs a complete Lorentzian off-shell",
        r"bounded prediction assembly",
        r"reverse-foundations-of-physics-appendices.tex",
        r"D\geq2A-\frac{488}{5}N",
        r"\mathbb E\sqrt{1+\frac AN}\leq\frac{\sqrt{1247}}5",
        r"\operatorname{Hess}A[v,v]=72-\frac{19712}{81}",
        r"=-\frac{13880}{81}<0",
        r"\mathcal C_G=\{r:K(r)\succeq0\}",
        r"\mathcal J_H(\psi)=\sqrt N\,\|\Omega^2\|_2\,\tau_\psi",
        r"\mathcal J_H(\psi)\geq N\kappa(G)",
        r"no weakest-base reversal is claimed",
        r"\mathrm{II}_r(h,h)=\frac{2}{\|\Omega^2\|_2}",
        r"\lim_{q\to\infty}q^6\kappa_{\mathrm{trial}}(q)=4",
        r"H_{2/5}=-\frac{398039}{88434}<0",
        r"not an obstruction to every intrinsic",
        r"\operatorname{Jac}_{\partial\mathcal C_G}T_{t,h}(R(\psi))",
        r"=e^{-S(\psi+th)+S(\psi)}",
        r"\frac9{10}\frac{10}9=1",
        r"conditional-fiber integral",
        r"\frac{A(\eta_n+t_nh)}{A(\eta_n)}",
        r"\frac{9}{4\,4^n}",
        r"m_h(t)=m_h(-t)",
        r"annealed or background-recentered",
        r"q_m\{u\geq-m\}\leq2^{-m}",
        r"\mathbb E_{q_m}[u^2]",
        r"recentered conditional width",
        r"annealed second moment of the moving center",
        r"REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1",
        r"REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LINEAR_PAIR_BOUNDS_V1",
        r"REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_COEFFICIENT_NORMAL_FORM_V1",
        r"REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1",
        r"negative pair 4 and positive pair 7",
        r"c_4<-0.01613",
        r"c_7<0.016103194",
        r"REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2",
        r"\sum_xJ_{x,1}=-24",
        r"susceptibility estimate",
        r"J_{xy}=\Omega_x\Omega_y(u_x-u_y)",
        r"K_{x,i}=(\Omega_x\Omega_{x+e_i}-1)(u_x-u_{x+e_i})",
        r"REVERSE_PHYSICS_BT_EUCLIDEAN_FLUX_CORRECTOR_POINTWISE_ENERGY_NO_GO_V1",
        r"\frac{49}{360096}L",
        r"Gibbs rarity and correlation",
        r"REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_FIBER_STABILITY_V1",
        r"\frac{2683}{800}L^3",
        r"not a neighborhood probability",
    ]:
        require(phrase in prose, f"required boundary missing from paper: {phrase}")
    for citation in [
        "CarcassiAidala2022",
        "Simpson2009",
        "Hardy2001",
        "Chiribella2011",
        "BlackadarFarahKaragila2023",
        "CoquandSpitters2009",
        "HeunenLandsmanSpitters2009",
        "GibbonsHoffmanWootters2004",
        "Baer2015",
        "HawkinsRejzner2020",
        "HohmZwiebach2017",
        "Pischke2025",
        "Bertotti2003",
        "Kramer2021",
        "LVKGWTC32021",
        "AbbottGW1708172017",
        "PaulySteinberg2018",
        "VanSchaftingen2014",
        "WeihrauchZhong2002",
    ]:
        require(f"bibitem{{{citation}}}" in paper, f"missing bibliography entry: {citation}")

    print("PASS paper 21 claim map, authority hashes, atlas counts, and claim boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

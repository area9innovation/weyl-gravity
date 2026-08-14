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
    bt_euclidean = json.loads((ROOT / data["authorities"]["bt_euclidean_import"]["path"]).read_text())
    bt_free_obstruction = json.loads((ROOT / data["authorities"]["bt_free_reconstruction_obstruction"]["path"]).read_text())
    bt_interacting_os = json.loads((ROOT / data["authorities"]["bt_interacting_os_preflight"]["path"]).read_text())
    bt_lambda04_os = json.loads((ROOT / data["authorities"]["bt_lambda04_os_kernel_obstruction"]["path"]).read_text())
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
    require(atlas["evidence_records"] == site["counts"]["evidence_records"] == 81, "evidence-record mismatch")
    require(atlas["literature_records"] == 51, "literature-record mismatch")
    require(atlas["local_result_records"] == 30, "local-result-record mismatch")
    require(atlas["content_pinned_literature"] == 39, "content-pinned literature mismatch")
    require(atlas["metadata_only_literature"] == 12, "metadata-only literature mismatch")
    require(atlas["evidence_records_used_by_matrix"] == 81, "matrix evidence usage is incomplete")
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
    ]}, "claim set drift")

    flags = data["claim_flags"]
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
    require(flags["bt_complete_order_g_four_whole_lattice_decided"] is False, "BT UV-local result promoted to whole-lattice decision")
    require(flags["bt_complete_order_g_four_ir_complement_bounded"] is False, "BT infrared complement promoted")
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
    require("contains 81 evidence records: 30 local result records and 51 literature records" in appendix, "appendix evidence summary drift")
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
    require(appendix.count(r"\hypertarget{atlas-evidence-") == 81, "evidence-register anchor count drift")
    require(appendix.count(r"\hyperlink{atlas-evidence-") == 81, "evidence-crosswalk link count drift")
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

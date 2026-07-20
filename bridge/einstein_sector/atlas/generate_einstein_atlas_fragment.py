#!/usr/bin/env python3
"""Generate the compact Plebański-Hacyan Einstein residual-atlas fragment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).with_name("einstein-compact-product-atlas-fragment.json")
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]
CERTIFICATES = {
    "standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "radiative": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "harmonic_taub_sign": ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json",
    "harmonic_sign_resonance_join": ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "balanced": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "exceptional_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "exceptional_nonzero_k_cofiber": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "exceptional_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
    "exceptional_difference_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance.json",
    "exceptional_ad_pivots": ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots.json",
    "exceptional_difference_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.json",
    "exceptional_resonance_ellipse": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
    "exceptional_minus_frequency_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.json",
    "exceptional_zero_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_zero_frequency_source.json",
    "exceptional_bounded_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_bounded_obstruction.json",
    "exceptional_single_minus_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_single_minus_dressing_no_go.json",
    "exceptional_finite_minus_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.json",
    "exceptional_wiener_minus_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.json",
    "exceptional_standard_global_minus_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_standard_global_minus_no_go.json",
    "exceptional_ell1_oscillator_minus_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_ell1_oscillator_minus_no_go.json",
    "same_ell_generic_pair_minus_nonresonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_ell_generic_pair_minus_nonresonance.json",
    "cross_ell_generic_output_nonresonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json",
    "ell1_generic_pair_minus_nonresonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_generic_pair_minus_nonresonance.json",
    "exceptional_complete_k0_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_complete_k0_no_go.json",
    "exceptional_sobolev_bohr_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_sobolev_bohr_no_go.json",
    "twist_independence": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json",
    "twist_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json",
    "d_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json",
    "d_full_time": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial.json",
    "ad_polynomial_zero": ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus.json",
    "abd_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json",
    "homogeneous_twist_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json",
    "aligned_twist_extra_face": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json",
    "complete_global_extra_cone": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
    "global_extra_bounded_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "global_extra_smooth_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.json",
    "complete_global_ell2_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone.json",
    "abd_axial_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json",
    "abd_polar_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.json",
    "abd_general_ell_minus_fixtures": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures.json",
    "aligned_global_minus_extra_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone.json",
    "axial_all_m_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion.json",
    "global_axial_all_m_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone.json",
    "global_ell2_both_parity_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_ell2_all_m_both_parity_bounded_cone.json",
    "fixed_ell_combined": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    "abd_generic_lambda_pivot": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
    "global_fixed_ell_k0_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.json",
    "complete_global_twist_fixed_ell_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone.json",
    "global_finite_harmonic_k0_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone.json",
    "complete_global_twist_finite_harmonic_k0_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_finite_harmonic_k0_bounded_cone.json",
    "constant_twist_wave_counterexample": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_wave_counterexample.json",
    "constant_twist_extra_position_zero_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.json",
    "constant_twist_einstein_position_zero_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.json",
    "constant_twist_ell2_moment_resonance_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone.json",
    "constant_twist_ell2_complete_bounded_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone.json",
    "constant_twist_ell2_projector_repair": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_projector_repair.json",
    "twist_position_velocity_ell2_complete_bounded_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone.json",
    "twist_circumference_wilson_ell2_complete_bounded_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone.json",
    "d_twist_ell2_complete_bounded_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone.json",
    "complete_global_twist_ell2_bounded_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone.json",
    "fixed_ell_constant_twist_factorization": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_factorization.json",
    "fixed_ell_constant_twist_zero_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map.json",
    "fixed_ell_constant_twist_bounded_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.json",
    "nonzero_k_constant_twist_same_shell": ROOT / "bridge/certificates/einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell.json",
    "finite_multimomentum_divisor": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_multimomentum_resonance_divisor.json",
    "ell2_two_abs_momentum_identity_audit": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_identity_audit.json",
    "ell2_two_abs_momentum_isolated_candidates": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "collision_scalar_separation": ROOT / "bridge/certificates/einstein_maxwell_weyl_collision_scalar_separation_classification.json",
    "same_sign_collision_same_fibre_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_same_fibre_census.json",
    "same_sign_collision_bounded_witnesses": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_bounded_witnesses.json",
    "same_sign_scalar_extreme_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "same_sign_scalar_candidate_audit": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones.json",
    "same_sign_extreme_ray_lifts": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_extreme_ray_lifts.json",
    "same_sign_scalar_cone_sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json",
    "same_sign_phase_parity_fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
    "same_sign_resonance_face_fibres": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "same_sign_automatic_face_rotation_links": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_links.json",
    "same_sign_axisymmetric_rotation_singularity": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity.json",
    "same_sign_automatic_face_rotation_normal_form": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form.json",
    "same_sign_automatic_face_full_internal_rotation_normal_form": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form.json",
    "same_sign_automatic_face_full_rotation_normal_form": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_full_rotation_normal_form.json",
    "same_sign_candidate16_active_restricted_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current.json",
    "same_sign_candidate16_singular_rotation_zero_fibre": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre.json",
    "same_sign_candidate16_occupation_gluing": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing.json",
    "same_sign_active_linear_sheet_rotation_links": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links.json",
    "same_sign_candidate17_20_axisymmetric_restricted_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current.json",
    "same_sign_L1_active_restricted_current_degeneracy": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy.json",
    "same_sign_candidate18_active_restricted_current_degeneracy": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy.json",
    "same_sign_active_presymplectic_divisors": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_presymplectic_divisors.json",
    "same_sign_third_transvectant_singular_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json",
    "same_sign_candidate18_complex_singular_resolution": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution.json",
    "same_sign_active_singular_rotation_zero_sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections.json",
    "same_sign_candidate18_singular_component_separation": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_component_separation.json",
    "same_sign_candidate18_singular_smooth_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_singular_smooth_bridge.json",
    "same_sign_candidate17_20_singular_component_incidence": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence.json",
    "same_sign_candidate17_20_double_singular_rotation_zero_fibre": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre.json",
    "same_sign_candidate17_20_common_square_rotation_quotient": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient.json",
    "same_sign_candidate17_20_singular_radial_contraction": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction.json",
    "same_sign_candidate17_20_moving_square_contraction": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.json",
    "same_sign_candidate17_20_independent_node_scaling_contraction": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction.json",
    "same_sign_candidate17_20_deformable_kernel_incidence_normal_form": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form.json",
    "same_sign_candidate17_20_deformable_kernel_complete_contraction": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction.json",
    "same_sign_candidate17_20_component_incidence_classification": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification.json",
    "same_sign_active_phase_reduced_presymplectic_divisors": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.json",
    "same_sign_active_local_rotation_leaf_descent": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent.json",
    "ell2_two_abs_momentum_parity_workload": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json",
    "ell2_two_abs_momentum_candidate4_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.json",
    "ell2_two_abs_momentum_axial_qminus_L4_triplet": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.json",
    "ell2_two_abs_momentum_axial_axial_L4_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.json",
    "ell2_two_abs_momentum_polar_polar_L4_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.json",
    "ell2_two_abs_momentum_axial_polar_L4_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.json",
    "ell2_two_abs_momentum_polar_axial_L4_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.json",
    "ell2_two_abs_momentum_nonaxisymmetric_L3_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix.json",
    "ell2_two_abs_momentum_nonaxisymmetric_L1_L3_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.json",
    "ell2_two_abs_momentum_cross_fibre_amplitude_system": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json",
    "ell2_two_abs_momentum_scalar_L4_zero_varieties": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json",
    "ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces.json",
    "ell2_two_abs_momentum_scalar_L3_zero_variety": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L3_zero_variety.json",
    "ell2_two_abs_momentum_scalar_L1_zero_varieties": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json",
    "ell2_two_abs_momentum_candidate4_L4_zero_variety": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_L4_zero_variety.json",
    "ell2_two_abs_momentum_target_doublet_L3_zero_varieties": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.json",
    "ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.json",
    "ell2_two_abs_momentum_rank_one_branch_zero_varieties": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_rank_one_branch_zero_varieties.json",
    "ell2_two_abs_momentum_regular_pencil_L4_zero_varieties": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json",
    "ell2_two_abs_momentum_candidate13_L4_incidence_reduction": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json",
    "ell2_two_abs_momentum_candidate13_pure_extra_taub_join": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.json",
    "ell2_two_abs_momentum_candidate13_mixed_null_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.json",
    "ell2_two_abs_momentum_candidate13_same_fibre_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.json",
    "ell2_two_abs_momentum_candidate13_mixed_bounded_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension.json",
    "ell2_two_abs_momentum_candidate13_complete_mixed_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone.json",
    "candidate13_scalar_separation_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_scalar_separation_no_go.json",
    "candidate13_mixed_pressure_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json",
    "finite_generic_bounded_zero_block": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json",
    "candidate13_bounded_zero_frequency": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition.json",
    "twist_aligned_opposite_momentum_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json",
    "symbolic_ell_qminus_self_collision": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.json",
    "symbolic_ell_axial_qminus_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction.json",
    "symbolic_ell_qminus_parity_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix.json",
    "symbolic_ell_standard_branch_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census.json",
    "symbolic_ell_mixed_sheet_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_mixed_sheet_bounded_extension.json",
    "symbolic_ell_tuned_axisymmetric_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone.json",
    "opposite_momentum_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json",
    "twist_aligned_opposite_momentum_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.json",
    "opposite_momentum_ell2_parity_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json",
    "opposite_momentum_ell2_mixed_parity_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension.json",
    "opposite_momentum_ell2_tuned_axisymmetric_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone.json",
    "opposite_momentum_ell2_tuned_all_primary_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone.json",
    "aligned_twist_extra_coefficients": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.json",
    "global_self_coefficients": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_orbit_self_second_order.json",
    "extra_self_coefficients": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_extra_self_second_order.json",
    "finite_generic_smooth": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "complete_finite_smooth": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
    "standard_global_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "electric_wilson_transport": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "circumference_classification": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "branch_dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
    "exceptional_offshell": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json",
    "covariant_chain_map": ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json",
    "relative_linear_triangle": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    "relative_candidate13_derived_source_crosswalk": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1.json",
    "relative_current_cofiber_receiver": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CURRENT_COFIBER_ASSEMBLY_V1.json",
    "relative_full_domain_f2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
    "asymptotic_raw_flux_corner": ROOT / "bridge/certificates/asymptotic_bach_raw_flux_corner_obstruction.json",
    "homogeneous_cofiber": ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json",
    "twist_cofiber": ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json",
    "generic_cyclic_obstruction": ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json",
    "abstract_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict:
    return json.loads(CERTIFICATES[name].read_text(encoding="utf-8"))


def _evidence(*names: str) -> list[dict[str, str]]:
    rows = []
    for name in names:
        path = CERTIFICATES[name]
        payload = _load(name)
        rows.append({"path": str(path.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha256(path)})
    return rows


BASE = {
    "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
    "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
    "boundaries": "closed Cauchy slice S1_L x S2; no asymptotic boundary; before final residual SO(4,2) quotient",
    "charge_sector": "fixed magnetic U(1) bundle P_N with N=2; electric tangent allowed unless narrowed",
}


def _scope(**updates: object) -> dict[str, object]:
    value: dict[str, object] = dict(BASE)
    value.update(updates)
    return value


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second_order(bounded: tuple[str, str], secular: tuple[str, str], causal: tuple[str, str]) -> dict[str, object]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(*bounded),
        "smooth_secular": _claim(*secular),
        "causal_retarded": _claim(*causal),
    }


def _entry(
    identifier: str,
    scope: dict[str, object],
    descriptions: dict[str, str],
    dispersion: tuple[str, str],
    lee_wald: tuple[str, str],
    taub_maps: tuple[str, str],
    resonance: tuple[str, str],
    second_order: dict[str, object],
    evidence: list[dict[str, str]],
    boundary: str,
) -> dict[str, object]:
    return {
        "id": identifier,
        "scope": scope,
        "descriptions": descriptions,
        "mode_data": {
            "dispersion": _claim(*dispersion),
            "lee_wald": _claim(*lee_wald),
            "taub_maps": _claim(*taub_maps),
            "resonance": _claim(*resonance),
            "second_order": second_order,
        },
        "evidence": evidence,
        "claim_boundary": boundary,
    }


def entries() -> list[dict[str, object]]:
    open_causal = ("OPEN", "No compact-product causal/retarded Green theorem has been certified.")
    result = [
        _entry(
            "einstein.ph.bridge.relative_branch_dictionary_v1",
            _scope(carrier="same-background Einstein-Maxwell/Weyl-Maxwell inclusion, solution cofibers and branch dictionary", degree=1, parity="axial, polar, exceptional and global sectors kept separate", ell="generic >=2 plus explicitly listed exceptional/global gaps", m="all where certified", k="all compact momenta where certified", omega="q-primary, p-primary and generalized-zero branches without cross-background identification"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            ("CERTIFIED", "The same-background branch dictionary separates q-primary Einstein, p-primary extra and generalized-zero carriers in every declared certified sector."),
            ("CERTIFIED", "The Einstein, pulled-back Weyl and direct relative action forms are exported separately on the complete declared carrier; their generic inertia defect OBSTRUCTS a standard-pairing cyclic map."),
            ("OPEN", "Quadratic data are partial handoffs and do not complete the relative interaction obstruction map."),
            ("CERTIFIED", "The noncyclic three-form all-row triangle, support-local mapping cofiber, connected residual endpoints and U1 winding lattice activate compact-product Bridge 1 at the linear algebraic/cofiber level."),
            _second_order(("OPEN", "Bridge 1 is a linear carrier gate; the complete bounded tangent cone is not certified."), ("OPEN", "No all-sector smooth-secular relative theorem."), open_causal),
            _evidence("relative_linear_triangle", "covariant_chain_map", "branch_dictionary", "exceptional_offshell", "exceptional_nonzero_k_cofiber"),
            "Global map lifecycle is NONCYCLIC_THREE_FORM_LINEAR_TRIANGLE_CERTIFIED and compact-product Bridge 1 is active only at the linear algebraic/cofiber level. One natural support-local minimal chain map globalizes the complete harmonic coefficient algebra without harmonic selection; the three action forms and declared fixed-N=2 residual endpoints are explicit. Every standard-pairing cyclic correction is obstructed. Compact-product causal Green data and q2/q3 relative compatibility remain open. No similarly named mode on Berger, black-hole, asymptotic or vacuum-cylinder backgrounds is identified by this row.",
        ),
        _entry(
            "einstein.ph.bridge.relative_candidate13_derived_source_crosswalk",
            _scope(theory="Einstein-Maxwell source relative to Weyl-Maxwell target", boundaries="candidate-13 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="generic ell=2 q-primary Einstein image plus p-primary relative cofiber on signed n=1,-2 fibres", degree=2, parity="axial and polar", ell="input ell=2; outputs L=0,...,4", m="all m and allowed output M", k="signed n=1,-2 fibres with reality conjugates", omega="all generic branch shells and quadratic signed sums", charge_sector="fixed magnetic U1 bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The q-primary Einstein image and p-primary relative cofiber are crosswalked on the same candidate-13 compact-product background only."),
            ("CERTIFIED","The source, pulled-back target and cofiber action-derived forms remain three distinct noncyclic triangle forms."),
            ("CERTIFIED","The smooth zero-block map lands in the five-current/Koszul receiver; bounded inversion adds a distinct circle-pressure component R_c."),
            ("CERTIFIED","The finite-frequency relative map lands in the separate 18-dimensional candidate-13 adjoint-cokernel coefficient receiver."),
            _second_order(("CERTIFIED","The bounded reduced-source pullback is exactly {0}: the common zero of the typed receiver is the origin by the exact scalar separator."),("CERTIFIED","The smooth derived source is the nontrivial five-moment-map zero locus because the pressure and resonance components have secular inverses."),("NO_CERTIFIED_MAP","No background-specific retarded relative correction complex is certified.")),
            _evidence("relative_candidate13_derived_source_crosswalk","relative_linear_triangle","relative_current_cofiber_receiver","relative_full_domain_f2_obstruction","ell2_two_abs_momentum_candidate13_complete_mixed_cone","candidate13_scalar_separation_no_go","finite_generic_bounded_zero_block","candidate13_bounded_zero_frequency","candidate13_mixed_pressure_obstruction","branch_dictionary"),
            "This is a same-background REDUCED-MODE bounded and smooth derived-source crosswalk. The bounded pullback is certified but contains only the origin; the smooth pullback is nontrivial. The frozen-unary full-domain support-local f2 remains obstructed, no support-local derived BV subcomplex is constructed, arity three is not authorized, and higher maps remain fail-closed.",
        ),
        _entry(
            "einstein.asymptotic.minkowski.weyl.raw_flux_corner_obstruction",
            _scope(
                theory="linearized pure-Weyl gravity reduced Cartesian TT polarization",
                background="Minkowski space in outgoing retarded coordinates",
                boundaries="large-r cuts of I+ in one fixed conformal completion; I-, i0 and corner matching undeclared",
                charge_sector="radiative p=1 and boundary-metric p=0 indicial data; Coulombic aspects absent",
                carrier="two-term scalar amplitudes for one TT polarization and one angular Laplacian eigenmode",
                degree=1,
                parity="one flat TT polarization; the same reduced algebra applies to the other",
                ell="scalar-amplitude angular eigenvalue L; no full tensor-harmonic classification",
                m="suppressed by angular orthogonality",
                k="radial asymptotic expansion, not compact momentum",
                omega="arbitrary retarded-time profiles in the formal p=0 and p=1 indicial channels",
            ),
            {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "OBSTRUCTED",
                "nonlinear": "NOT_APPLICABLE",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            (
                "CERTIFIED",
                "The reduced fourth-order indicial carrier has p=0 boundary-metric and p=1 same-falloff Einstein/Bach channels; full tensor reconstruction remains open.",
            ),
            (
                "OBSTRUCTED",
                "The raw cut current diverges linearly on generic p0-p0 data, while fixing p0 makes the p1-p1 raw I+ form vanish; the finite p0-p1 cross term is not a radiative p1-p1 form.",
            ),
            (
                "NOT_APPLICABLE",
                "Compact Taub moment maps do not transfer to this null-boundary carrier; P0 and D_M charges remain open, H_ESU is not boundary-preserving on the fixed patch, and D_rad has no certified real Lorentzian map.",
            ),
            (
                "OPEN",
                "Full tensor repeated-root reconstruction, polyhomogeneous logarithms, Coulombic data and the i0/I+ corner prescription are not classified.",
            ),
            _second_order(
                ("NOT_APPLICABLE", "No bounded compact second-order correction class is declared on this asymptotic linear seed."),
                ("NOT_APPLICABLE", "No smooth-secular compact correction theorem transfers to this background."),
                ("NO_CERTIFIED_MAP", "No retarded full tensor BV-BFV complex or finite renormalized null-infinity phase space is certified."),
            ),
            _evidence("asymptotic_raw_flux_corner"),
            "This LOCAL-ALGEBRAIC, REDUCED-MODE row certifies the first null-infinity boundary/corner obstruction only. It neither constructs nor rules out a counterterm-improved tensor BV-BFV phase space, and it computes no asymptotic charge, particle, scattering, stability, unitarity, or compact-to-asymptotic mode map.",
        ),
        _entry(
            "einstein.ph.em_wm.standard.generic_radiative",
            _scope(carrier="Einstein q-primary image in the Weyl-Maxwell axial and polar coefficient complexes", degree=1, parity="axial and polar", ell=">=2", m="all", k="2*pi*n/L, n in Z", omega="omega^2=k^2+lambda +/- sqrt(2*lambda), lambda=ell(ell+1)"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Two Einstein-Maxwell q-primary shells: omega^2=k^2+lambda +/- sqrt(2*lambda)."),
            ("CERTIFIED", "The identity inclusion is nonnull and nondegenerate but has branch-dependent relative endomorphism R; axial and polar branches are covered."),
            ("CERTIFIED", "The five compact stabilizer moment maps and their harmonic selection rules are explicit, but the pure-Einstein common zero locus is not classified."),
            ("OPEN", "The complete finite-harmonic q-primary resonance functionals are not classified."),
            _second_order(("OPEN", "No general bounded finite-harmonic Einstein-sector extension theorem."), ("OPEN", "No general smooth-secular Einstein-sector extension theorem."), open_causal),
            _evidence("standard", "axial_current", "polar_current", "taub", "abstract_cone"),
            "This is a compact pre-final-residual linear phase-space entry, not an asymptotic graviton, scattering, or all-orders Einstein-sector theorem.",
        ),
        _entry(
            "einstein.ph.wm.extra.generic_p_primary",
            _scope(theory="Weyl-Maxwell target", carrier="two p-primary extra polarizations in each axial and polar generic block", degree=1, parity="axial and polar", ell=">=2", m="all", k="2*pi*n/L, n in Z", omega="omega_e^2=k^2+lambda-2/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The extra shell is omega_e^2=k^2+lambda-2/3 and has two cyclic p-primary summands per parity."),
            ("CERTIFIED", "The direct Lee-Wald extra block is nonradical with positive-frequency current inertia (2,0) per parity and is orthogonal to the Einstein image."),
            ("CERTIFIED", "mu_H is negative definite on every nonzero real pure-extra finite-energy tangent at fixed magnetic bundle."),
            ("OPEN", "Additional bounded resonance functionals are not needed for the pure-extra Taub no-go and are not globally classified."),
            _second_order(("OBSTRUCTED", "Every nonzero real pure-extra tangent violates the fixed-bundle time-translation Taub constraint."), ("OBSTRUCTED", "Allowing secular propagation corrections does not remove the certified stabilizer moment-map obstruction."), open_causal),
            _evidence("axial_operator", "polar_operator", "axial_current", "polar_current", "taub", "abstract_cone"),
            "The obstruction is classical and fixed-bundle. It does not erase the linear mode, prove a quantum ghost, or supply a Lorentzian-causal no-go.",
        ),
        _entry(
            "einstein.ph.wm.taub.harmonic_sign_stratification",
            _scope(theory="Einstein-Maxwell source included in Weyl-Maxwell target", carrier="all certified generic and exceptional q/p oscillators plus homogeneous and twist generalized-zero blocks", degree=2, parity="axial and polar where present", ell="homogeneous 0, exceptional 1, generic ell>=2", m="all certified SO3 multiplicities", k="all allowed compact momenta on oscillator blocks; k=0 on global blocks", omega="stationary q/p shells and separately typed generalized-zero polynomial classes"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            ("CERTIFIED", "Every certified additional-Weyl solution-cofiber oscillator is retained: generic p-primary modes and exceptional ell=1 extra modes, both parities and every allowed momentum."),
            ("CERTIFIED", "The complete extra cofiber has positive current and strictly negative mu_H; the Einstein q-minus primary has the opposite sign in both parities for every ell>=2."),
            ("CERTIFIED", "Opposite momenta, relative phases and multiple |k| fibres cannot cancel the pure-extra H sum; electric variation contributes with the same negative sign."),
            ("CERTIFIED", "Homogeneous and twist cofibers vanish, so their indefinite/zero Taub strata are Einstein-image blocks rather than counterexamples to extra-cofiber definiteness."),
            _second_order(("OPEN", "Pure-extra oscillator directions are obstructed, but the complete mixed bounded cone is not classified by the sign theorem."), ("OPEN", "The Taub sign theorem obstructs pure-extra directions even with secular corrections, while the full mixed smooth-secular cone remains open."), ("NO_CERTIFIED_MAP", "No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("harmonic_taub_sign", "taub", "exceptional_current", "exceptional_nonzero_k_cofiber", "radiative"),
            "Fixed magnetic bundle only. Uniform flux variation, complete resonance functionals, final residual descent, all-orders integration, causal propagation and quantum interpretation remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.harmonic_sign_resonance_join",
            _scope(theory="Einstein-Maxwell image and additional-Weyl cofiber inside Weyl-Maxwell", carrier="joined complete finite obstruction map; classified subcarrier is all standard globals plus arbitrary finite generic ell>=2,k=0 q/p waves", degree=2, parity="axial and polar where present", ell="joined 0,1,>=2; classified subcarrier globals plus arbitrary finite generic ell>=2", m="all certified SO3 multiplicities", k="joined all certified momenta; classified subcarrier k=0", omega="all certified q/p shells and generalized-zero polynomial classes"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            ("CERTIFIED", "Every certified branch is retained in the joined coefficientwise obstruction map without identifying distinct momentum or circumference carriers."),
            ("CERTIFIED", "Branch-diagonal Lee-Wald occupation weights supply the all-harmonic sign block; pure additional-Weyl finite sums have strictly negative mu_H and the Einstein q-minus block has the opposite sign."),
            ("CERTIFIED", "The stabilizer block is (mu_H,mu_Px,mu_J1,mu_J2,mu_J3); its zero block is orthogonal to all positive-degree P_(j,r) and nonzero-shell R_(j,a) output summands."),
            ("CERTIFIED", "The complete bounded map is {mu,P,R}; the polynomial and exceptional twist-resonance witnesses independently show that mu=0 is not bounded solvability."),
            _second_order(("CERTIFIED", "On the maximal complete subcarrier—standard globals plus arbitrary finite generic ell>=2,k=0 waves—the exact bounded cone is the certified wave-free/wave-nonzero stratified union. The full finite-carrier zero geometry remains OPEN."), ("CERTIFIED", "On the complete certified finite carrier, smooth exponential-polynomial extension is equivalent to the five moment maps vanishing."), ("NO_CERTIFIED_MAP", "No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("harmonic_sign_resonance_join", "harmonic_taub_sign", "complete_global_twist_finite_harmonic_k0_bounded", "complete_finite_smooth"),
            "The joined map is complete as a finite coefficientwise formula, but its full bounded common zero geometry is not classified. The exact solved subcarrier excludes exceptional oscillator inputs and nonzero momentum; candidate-13 and tuned opposite-momentum controls remain separate with NO_CERTIFIED_MAP between them. Infinite completion, final residual descent, all-orders, causal, observational and quantum claims remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.ell2_k0_balanced_jet",
            _scope(theory="Weyl-Maxwell target with Einstein q-primary and extra p-primary inputs", carrier="one real axial ell=2,m=0,k=0 Einstein-minus mode plus one extra mode at the certified balancing amplitude", degree=2, parity="axial input with polar and homogeneous quadratic outputs", ell="input ell=2; outputs ell=0,2,4", m=0, k=0, omega="omega_-^2=6-2*sqrt(3), omega_e^2=16/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The two incommensurable input shells are omega_-^2=6-2*sqrt(3) and omega_e^2=16/3."),
            ("CERTIFIED", "The Einstein and extra inputs are orthogonal nonnull Lee-Wald directions with opposite Taub signs."),
            ("CERTIFIED", "The exact positive balancing amplitude makes all five stabilizer moment maps vanish."),
            ("CERTIFIED", "Every finite output channel is nonresonant or has its zero-frequency source canceled; all action rows are Noether-completed."),
            _second_order(("CERTIFIED", "A complete real finite-quasiperiodic second-order correction is constructed channel by channel."), ("CERTIFIED", "The bounded correction is also an admissible smooth exponential-polynomial correction."), open_causal),
            _evidence("balanced", "taub", "abstract_cone"),
            "This is one explicit second-order jet, not the full mixed cone, an exact nonlinear family, or an all-orders closure theorem.",
        ),
        _entry(
            "einstein.ph.wm.extra.exceptional_ell1_k0",
            _scope(theory="Weyl-Maxwell target", carrier="complete axial-plus-polar exceptional extra dipole block", degree=1, parity="axial and polar", ell=1, m="-1,0,1", k=0, omega="omega_e^2=4/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The exceptional extra dipole shell has omega_e^2=4/3."),
            ("CERTIFIED", "The exceptional axial and polar current blocks are nonradical and positive definite before the final residual quotient."),
            ("CERTIFIED", "The pure exceptional block has a definite fixed-bundle Taub obstruction."),
            ("CERTIFIED", "The all-m positive-positive source has a nonzero polar ell=2 p-shell projection; its exact STF zero locus is only the origin."),
            _second_order(("OBSTRUCTED", "Every nonzero exceptional dipole is obstructed by the certified Taub and resonant functionals."), ("OBSTRUCTED", "The stabilizer Taub obstruction persists even if a resonant propagation correction is allowed to be secular."), open_causal),
            _evidence("exceptional_current", "exceptional_cofiber", "exceptional_resonance", "abstract_cone"),
            "This all-m compact no-go is pre-final-residual and does not identify an asymptotic state or a quantum particle.",
        ),
        _entry(
            "einstein.ph.wm.interaction.exceptional_ell1_k0_difference_frequency_census",
            _scope(theory="Weyl-Maxwell target", carrier="every certified k=0 oscillator pair capable by angular selection of producing the exceptional L=2 target", degree=2, parity="parity-blind conservative triangle census", ell="generic pairs with |ell_1-ell_2|<=2 plus physical/exceptional ell1 against generic ell=2,3", m="all Clebsch-Gordan-allowed values", k=0, omega="|omega_1-omega_2| tested against 4/sqrt(3)"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The generic q/p and physical/exceptional dipole shell inventory is complete for the declared k=0 triangle census."),
            ("CERTIFIED", "The branch frequencies are the action-normalized stationary shells imported from the linear target classification."),
            ("NOT_APPLICABLE", "This row classifies shell arithmetic, not a stabilizer moment-map zero locus."),
            ("CERTIFIED", "Twenty-seven exact resultant polynomials and twelve dipole minimal polynomials prove that no unequal-frequency k=0 pair reaches 2*omega_e,L=2."),
            _second_order(("OPEN", "The frequency census leaves one live positive-sum generalized-zero-global times ell=2-extra source column whose coefficientwise bounded zero locus remains open."), ("CERTIFIED", "Off-shell difference-frequency channels admit finite exponential-polynomial inverses; the complete smooth theorem remains separate."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_difference_census", "exceptional_resonance", "exceptional_current"),
            "This closes only k=0 difference-frequency arithmetic. The live global-times-ell2-extra source, opposite nonzero momenta, complete bounded mixed cone, causal propagation and quantum interpretation remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.exceptional_ell1_ad_resonance_pivots",
            _scope(theory="Weyl-Maxwell target", carrier="radion position a or circumference velocity d crossed with one exceptional axial/polar extra dipole", degree=2, parity="axial and polar kept separate", ell="0 x 1 -> 1", m="all by SO3 multiplicity one", k=0, omega="omega_exceptional^2=4/3"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The exceptional axial and polar representatives and their physical adjoint cokernel rows are fixed by the direct ell=1 operators."),
            ("CERTIFIED", "Both exceptional branches have nonradical action-derived currents; this row uses their operator adjoints rather than identifying the parities."),
            ("CERTIFIED", "The universal bounded polynomial ledger removes b and twist velocity B before the displayed a/d pivots are applied."),
            ("CERTIFIED", "Direct four-dimensional full-time sources give a nonzero a*t pivot and, after a=0, a nonzero d pivot in each parity."),
            _second_order(("OPEN", "The a pivot is unscreenable, but the constant d pivot shares its L=1 shell with the live exceptional-times-ell2-extra difference channel; the joint zero locus is open."), ("CERTIFIED", "The complete finite-support smooth theorem permits finite secular inverses once the five moment maps vanish."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_ad_pivots", "exceptional_difference_census", "exceptional_resonance", "abstract_cone"),
            "This is a coefficient theorem, not a complete exceptional mixed bounded cone. The eight exceptional-times-ell2-extra difference columns, nonzero momentum and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.exceptional_ell1_ell2_extra_difference_matrix",
            _scope(theory="Weyl-Maxwell target", carrier="one conjugate exceptional ell1 extra dipole crossed with one positive-frequency ell2 extra primary", degree=2, parity="all axial/polar input pairs and both ell2 multiplicities", ell="1 x 2 -> L=1", m="axisymmetric direct fixtures", k=0, omega="2*omega_exceptional-omega_exceptional=omega_exceptional"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The exceptional and ell2 extra representatives are certified distinct p-primary carrier blocks."),
            ("CERTIFIED", "The L=1 physical adjoint witnesses are action-normalized separately in axial and polar parity."),
            ("OPEN", "The five moment maps have not yet been intersected with the sparse L1 equations and the exceptional L2 self-defect."),
            ("CERTIFIED", "All eight direct axisymmetric columns are computed: six adjoint projections vanish, while the axial/polar survivors are -768/5 and -864/5 and both use ell2 polar e2."),
            _second_order(("OPEN", "The unique polar-e2 control amplitude and d satisfy two explicit L1 equations, but the all-m tensor and joint L2/moment-map zero locus remain open."), ("CERTIFIED", "The complete finite-support smooth theorem allows finite secular inversion on the five-moment-map zero cone."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_difference_matrix", "exceptional_ad_pivots", "exceptional_resonance", "d_completion", "abstract_cone"),
            "This is the complete axisymmetric L1 difference matrix, not the all-m bounded tangent cone. The L2 self channel, moment maps, nonzero momentum and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_axisymmetric_resonance_ellipse",
            _scope(theory="Weyl-Maxwell target", carrier="axisymmetric exceptional axial/polar dipoles, circumference velocity d, and ell2 extra control amplitudes", degree=2, parity="both exceptional parities with polar and axial ell2 controls", ell="inputs 1 and 2; resonant outputs L=1,2", m=0, k=0, omega="omega_exceptional and 2*omega_exceptional"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Every input is a certified nonradical exceptional or generic-extra primary, with d in the standard generalized-zero block."),
            ("CERTIFIED", "The exceptional and ell2 control current Grams are action-derived and positive on their extra-primary blocks."),
            ("OBSTRUCTED", "P_x and rotations vanish, but mu_H is strictly negative on every nonzero point of the displayed resonance ellipse; an Einstein-minus occupation is required."),
            ("CERTIFIED", "All L1/L2 resonant adjoint equations reduce to the exact nonempty ellipse 16*r_x^2+3*r_p^2=115*d^2 with explicit controls."),
            _second_order(("OPEN", "The resonance-compatible ellipse is not yet a bounded second-order tangent because its Hamiltonian balance and all new Einstein-minus cross sources remain unsolved."), ("CERTIFIED", "The imported complete finite-support theorem supplies smooth secular inversion once all five moment maps vanish."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_resonance_ellipse", "exceptional_difference_matrix", "exceptional_resonance", "d_completion", "abstract_cone"),
            "This is an axisymmetric resonance-compatibility theorem. It does not certify the Hamiltonian-balanced enlargement, a complete second-order correction, all m, nonzero momentum or higher lifecycles.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_ellipse_einstein_minus_frequency_gate",
            _scope(theory="Weyl-Maxwell target", carrier="pure-axial endpoint of the exceptional resonance ellipse plus one axial ell2 Einstein-minus balance oscillator", degree=2, parity="all conservatively allowed target parities", ell="inputs 1 and 2; every angularly allowed output", m=0, k=0, omega="all signed Einstein-minus cross frequencies"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The exceptional, generic-extra control and Einstein-minus inputs are certified distinct nonradical stationary carrier blocks."),
            ("CERTIFIED", "The action-derived exceptional and ell2 control Grams and the negative relative Einstein-minus weight fix the exact balance normalization."),
            ("CERTIFIED", "One explicit Einstein-minus occupation cancels mu_H; axisymmetry and k=0 leave mu_Px and all three mu_Ji zero."),
            ("CERTIFIED", "Forty exact algebraic comparisons prove every new Einstein-minus cross frequency is off the physical target shells; nonzero-frequency homogeneous output is empty."),
            _second_order(("OBSTRUCTED", "Although the complete zero-frequency source cancels, d and the required Einstein-minus coefficient are both nonzero and their exact same-shell adjoint pairing excludes a bounded/finite-quasiperiodic correction."), ("CERTIFIED", "The complete finite-support theorem supplies a smooth exponential-polynomial inverse with the required secular shell term because all five moment maps vanish."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_bounded_obstruction", "exceptional_minus_frequency_gate", "exceptional_zero_source", "exceptional_resonance_ellipse", "exceptional_current", "radiative", "complete_finite_smooth", "abstract_cone"),
            "This certifies one axisymmetric endpoint obstruction, not the general exceptional mixed zero locus. It does not assemble all m, treat nonzero momentum or promote causal, residual or quantum claims.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_ellipse_single_minus_dressing_no_go",
            _scope(theory="Weyl-Maxwell target", carrier="any point of the axisymmetric exceptional resonance ellipse plus one real axisymmetric Einstein-minus q-primary", degree=2, parity="axial or polar dressing, kept separate", ell="exceptional/control inputs 1,2 and one dressing ell_d>=2", m=0, k=0, omega="omega_minus^2=ell_d*(ell_d+1)-sqrt(2*ell_d*(ell_d+1))"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Every ellipse input and the single Einstein-minus dressing remain in their explicit same-background carrier blocks."),
            ("CERTIFIED", "The Einstein-minus relative current weight is negative and nondegenerate for every physical ell, supplying the opposite Taub sign."),
            ("CERTIFIED", "The m=0,k=0 dressing amplitude can cancel mu_H while all momentum and rotation moment maps stay zero."),
            ("CERTIFIED", "The generic-lambda axial and polar d-cross pivots are nonzero for every ell>=2 and all m by SO3 multiplicity one."),
            _second_order(("OBSTRUCTED", "Every ellipse point has d!=0, whereas any nonzero single Einstein-minus dressing forces d=0 in the bounded shell ideal."), ("CERTIFIED", "The complete finite-support smooth theorem supplies the corresponding secular correction on the five-moment-map zero cone."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_single_minus_no_go", "exceptional_resonance_ellipse", "abd_generic_lambda_pivot", "radiative", "complete_finite_smooth", "abstract_cone"),
            "This excludes one dressing mode at a time. Multiple minus modes, additional carriers, nonzero momentum, all-orders integration and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_ellipse_finite_minus_dressing_no_go",
            _scope(theory="Weyl-Maxwell target", carrier="any axisymmetric exceptional resonance-ellipse point plus an arbitrary finite k=0 Einstein-minus q-primary sum", degree=2, parity="both dressing parities", ell="arbitrary finite subset of ell>=2", m="all m with total rotation moment map zero", k=0, omega="all occupied omega_minus(ell)"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All finite dressing coefficients remain in explicit same-background Einstein-minus carrier blocks."),
            ("CERTIFIED","Every occupied minus block has nondegenerate opposite-sign current weight."),
            ("CERTIFIED","Amplitudes may balance all five stabilizer moment maps, but at least one minus coefficient is nonzero."),
            ("CERTIFIED","Exact dispersion inequalities exclude all angularly allowed three-minus and original-minus collisions on a d-times-minus shell."),
            _second_order(("OBSTRUCTED","The nonzero d-cross map acts independently on every occupied minus block, forcing all charge-balancing minus coefficients to vanish."),("CERTIFIED","The complete finite-support theorem supplies a smooth secular correction on the stabilizer zero cone."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_finite_minus_no_go","exceptional_single_minus_no_go","abd_generic_lambda_pivot","complete_finite_smooth","abstract_cone"),
            "Additional nonminus carriers, infinite completion, nonzero momentum, all-orders integration and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_ellipse_wiener_minus_dressing_no_go",
            _scope(theory="Weyl-Maxwell target", carrier="any axisymmetric exceptional resonance-ellipse point plus a smooth Wiener-Bohr k=0 Einstein-minus q-primary sum", degree=2, parity="both dressing parities", ell="every ell>=2 with countable support", m="all m with absolutely convergent stabilizer moment maps", k=0, omega="countable occupied omega_minus(ell) set"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The declared smooth Wiener-Bohr carrier has absolutely convergent derivative-weighted harmonic coefficients and retains every branch label."),
            ("CERTIFIED","Every occupied minus block has a nondegenerate opposite-sign current weight; the five moment maps converge absolutely."),
            ("CERTIFIED","Any common-zero dressing must contain a nonzero minus coefficient because the undressed ellipse has strictly negative mu_H."),
            ("CERTIFIED","Continuous Bohr-frequency and spherical projections isolate d*C_parity(lambda)*c_(ell,m,parity) on every resonant minus shell."),
            _second_order(("OBSTRUCTED","A bounded smooth uniformly almost-periodic correction forces every minus coefficient to vanish separately, contradicting moment-map balance."),("OPEN","The finite secular theorem supplies no uniform estimates for an infinite secular sum."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_wiener_minus_no_go","exceptional_finite_minus_no_go","abd_generic_lambda_pivot","abstract_cone"),
            "This is a strong smooth Wiener-Bohr completion, not the maximal finite-energy/Sobolev space. Additional carriers, nonzero momentum, infinite secular solvability and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_ellipse_standard_global_minus_no_go",
            _scope(theory="Weyl-Maxwell target", carrier="any axisymmetric exceptional resonance-ellipse point plus arbitrary standard generalized-zero data and a smooth Wiener-Bohr k=0 Einstein-minus sum", degree=2, parity="homogeneous plus both axial/polar dressing parities", ell="global 0,1; exceptional/control 1,2; countable minus ell>=2", m="all global components and minus m with convergent moment maps", k=0, omega="generalized zero, exceptional/control frequencies and occupied omega_minus(ell)"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every global coordinate and minus coefficient retains its same-background carrier and fixed-bundle meaning."),
            ("CERTIFIED","After the bounded polynomial ideal, surviving global data have nonpositive or zero mu_H; moment-map balance still needs a nonzero minus coefficient."),
            ("CERTIFIED","The universal global polynomial ideal is b=B=0 and Q_e*a=0; its validity extends to bounded Wiener-Bohr oscillator products."),
            ("CERTIFIED","Electric, Wilson, circumference and constant-twist columns have zero relevant minus-shell adjoint component; the triangular a then d pivots remain unscreened."),
            _second_order(("OBSTRUCTED","The a pivot first forces a=0; the nonzero total ellipse d pivot then removes every required minus coefficient."),("OPEN","No uniform estimate certifies the infinite secular sum."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_standard_global_minus_no_go","exceptional_wiener_minus_no_go","standard_global_bounded","electric_wilson_transport","circumference_classification","fixed_ell_constant_twist_bounded_cone","abd_generic_lambda_pivot","abstract_cone"),
            "All standard generalized-zero additions are covered. Genuinely oscillatory nonminus carriers, maximal Sobolev completion, nonzero momentum and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_ellipse_ell1_oscillator_minus_no_go",
            _scope(theory="Weyl-Maxwell target", carrier="exceptional resonance ellipse, arbitrary standard generalized-zero data, arbitrary finite physical/extra k=0 ell1 oscillators, and a smooth Wiener-Bohr k=0 Einstein-minus sum", degree=2, parity="both ell1 and minus parities", ell="global 0,1; added oscillatory 1; control 2; countable minus ell>=2", m="all ell1 and minus m with convergent moment maps", k=0, omega="0, 2/sqrt(3), 2, 4/sqrt(3), and occupied omega_minus(ell)"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All physical and extra dipole additions retain their exceptional branch, parity and harmonic labels."),
            ("CERTIFIED","The physical and extra dipole current blocks are nonradical in both parities before the final residual quotient."),
            ("CERTIFIED","Both added ell1 oscillator blocks have the same strictly negative mu_H sign as the ellipse, so a nonzero minus balance remains necessary."),
            ("CERTIFIED","Adjacent-gap separation excludes ell1-minus collisions, and fourteen exact low-ell comparisons exclude ell1-ell1, ell1-control and constant-twist-ell1 collisions with the L=2,3 minus targets."),
            _second_order(("OBSTRUCTED","No added dipole product screens the nonzero d-times-minus pivot, which removes every required minus coefficient."),("OPEN","No uniform estimate certifies the infinite secular sum."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_ell1_oscillator_minus_no_go","exceptional_standard_global_minus_no_go","exceptional_current","exceptional_finite_minus_no_go","abstract_cone"),
            "All k=0 physical and extra ell1 oscillator additions are covered. Generic ell>=2 nonminus carriers, maximal Sobolev completion, nonzero momentum and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.complete_k0_pair_to_minus_nonresonance",
            _scope(theory="Weyl-Maxwell target", carrier="every unordered pair of certified k=0 physical or extra oscillators tested against every generic Einstein-minus target shell", degree=2, parity="all input/output parity combinations conservatively retained", ell="ell1 and every generic ell>=2 input pair; every angularly allowed generic target L>=2", m="all Clebsch-Gordan-allowed values", k=0, omega="all signed sums and differences of physical dipole, exceptional dipole, q-minus, p-extra and q-plus frequencies"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The complete certified k=0 oscillator inventory retains its physical/extra branch, parity, ell and m labels."),
            ("CERTIFIED","Every tested source and target branch has an action-derived nonradical Lee-Wald block before the final residual quotient."),
            ("NOT_APPLICABLE","This row is a shell-arithmetic census; stabilizer moment maps are evaluated on the carrier-specific tangent-cone row."),
            ("CERTIFIED","Exact distinct-ell, same-ell and ell1-generic inequalities prove that no quadratic oscillator pair lands on any generic Einstein-minus shell."),
            _second_order(("OPEN","Shell nonresonance alone does not establish a bounded correction because generalized-zero columns and direct source coefficients remain carrier-dependent."),("OPEN","No general infinite smooth-secular inverse follows from the arithmetic census."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell complex is certified.")),
            _evidence("same_ell_generic_pair_minus_nonresonance","cross_ell_generic_output_nonresonance","ell1_generic_pair_minus_nonresonance"),
            "This is complete only for k=0 pair-to-generic-minus shell arithmetic. It does not identify a source coefficient, classify nonzero momentum, prove an unrestricted bounded cone, or promote causal, residual, observational or quantum claims.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_ellipse_complete_k0_no_go",
            _scope(theory="Weyl-Maxwell target", carrier="any nonzero axisymmetric exceptional resonance-ellipse point, arbitrary standard generalized-zero data, arbitrary finite k=0 nonminus oscillators and a smooth Wiener-Bohr k=0 Einstein-minus sum", degree=2, parity="all certified homogeneous, axial and polar parities", ell="global 0,1; all finite physical/extra ell1 and generic nonminus ell>=2; countable minus ell>=2", m="all retained m with absolutely convergent stabilizer moment maps", k=0, omega="generalized zero plus the complete certified k=0 q/p oscillator inventory"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every declared input remains in its same-background fixed-bundle carrier; no cross-background or residual identification is used."),
            ("CERTIFIED","All oscillator and generalized-zero current blocks used by the Taub reduction are action normalized and retain their certified signs."),
            ("CERTIFIED","The ellipse and every nonminus addition contribute on the nonpositive side of mu_H, so every common zero requires a nonzero Einstein-minus coefficient."),
            ("OBSTRUCTED","The complete pair census and global reduction isolate d*C_parity(lambda)*c_(ell,m,parity) on each minus shell; d and every physical pivot are nonzero, forcing all required minus coefficients to vanish."),
            _second_order(("OBSTRUCTED","The bounded smooth uniformly almost-periodic second-order tangent cone has empty intersection with the complete declared carrier over every nonzero ellipse point."),("OPEN","Finite secular sufficiency has no certified uniform inverse estimate for the countable Wiener-Bohr dressing."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_complete_k0_no_go","ell1_generic_pair_minus_nonresonance","exceptional_standard_global_minus_no_go","exceptional_wiener_minus_no_go","abstract_cone"),
            "Complete only at k=0 for finite nonminus support and the declared smooth Wiener-Bohr minus topology. Maximal finite-energy/Sobolev completions, infinite secular inversion, nonzero momentum, causal propagation, final residual descent, all-orders integration and quantum interpretation remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.exceptional_ellipse_sobolev_bohr_complete_k0_no_go",
            _scope(theory="Weyl-Maxwell target", carrier="any nonzero axisymmetric exceptional resonance-ellipse point, arbitrary standard generalized-zero data, arbitrary finite k=0 nonminus oscillators and a Sobolev-Bohr k=0 Einstein-minus sum", degree=2, parity="all certified homogeneous, axial and polar parities", ell="global 0,1; finite nonminus ell>=1; countable Einstein-minus ell>=2", m="all retained m with convergent stabilizer moment maps", k=0, omega="generalized zero plus the complete certified k=0 q/p oscillator inventory"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The s>=6 Sobolev graph completion retains every same-background branch, parity, ell and m label without residual or cross-background identification."),
            ("CERTIFIED","The declared graph topology is defined with a positive Sobolev norm; all imported Lee-Wald and Taub signs retain their action-derived normalization."),
            ("CERTIFIED","The stabilizer maps converge on the declared graph domain, and every common zero over the nonpositive ellipse/nonminus carrier still needs nonzero Einstein-minus occupation."),
            ("OBSTRUCTED","Continuous Sobolev products, Banach-valued Bohr projection and Bochner-Fejer density extend the isolated nonzero d*C_parity(lambda) minus-shell functional beyond the Wiener class."),
            _second_order(("OBSTRUCTED","No bounded uniformly almost-periodic correction in the order-four s>=6 Sobolev graph domain exists over a nonzero ellipse point."),("OPEN","No uniform inverse estimate controls a countable secular correction."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell complex is certified.")),
            _evidence("exceptional_sobolev_bohr_no_go","exceptional_complete_k0_no_go","abstract_cone"),
            "Complete only at k=0 in the declared integer s>=6 uniformly almost-periodic Sobolev graph domain with finite nonminus support. Sharp energy/low-regularity completion, infinite secular inversion, nonzero momentum, causal propagation, final residual descent, all-orders integration and quantum interpretation remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.extra.exceptional_ell1_nonzero_k",
            _scope(theory="Weyl-Maxwell target", carrier="axial-plus-polar exceptional ell=1 solution cofiber at nonzero compact momentum", degree=1, parity="axial and polar", ell=1, m="-1,0,1", k="2*pi*n/L with n!=0", omega="standard omega^2=k^2+4 and extra omega^2=k^2+4/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            ("CERTIFIED", "The target quotient contains one standard and one extra class in each parity; the standard shell is the Einstein-Maxwell image."),
            ("CERTIFIED", "Polynomial representatives give extra Gram weights 4*(3*k^2+4) in both parities and zero standard-extra pairing."),
            ("OPEN", "The linear cofiber and current do not classify the nonzero-k fixed-bundle tangent cone."),
            ("OPEN", "No complete nonzero-k quadratic resonance table is certified."),
            _second_order(("OPEN", "No bounded second-order classification on this carrier."), ("OPEN", "No smooth-secular second-order classification on this carrier."), open_causal),
            _evidence("exceptional_nonzero_k_cofiber", "exceptional_offshell", "branch_dictionary", "abstract_cone"),
            "This is a same-background REDUCED-MODE solution cofiber whose coefficient map is the reduction of the certified natural support-local minimal chain map. It does not supply finite residual descent, causal propagation, a particle interpretation, or a cross-background map.",
        ),
        _entry(
            "einstein.ph.wm.mixed.twist_exceptional_independence",
            _scope(theory="Weyl-Maxwell target", carrier="one real m=0 exceptional axial dipole plus a collinear standard twist velocity", degree=2, parity="axial input; polar ell=2 resonant output", ell="input ell=1; output ell=2", m=0, k=0, omega="omega_e^2=4/3 plus generalized-zero twist velocity"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The input combines the exceptional omega_e^2=4/3 shell with a generalized-zero twist velocity."),
            ("CERTIFIED", "Both inputs belong to certified nonnull compact current blocks before the final residual quotient."),
            ("CERTIFIED", "The twist amplitude is chosen so every stabilizer moment map mu_X vanishes."),
            ("CERTIFIED", "A polar ell=2 p-shell adjoint functional remains nonzero: mu_X(u)=0 but R_bounded(u)!=0."),
            _second_order(("OBSTRUCTED", "The nonzero resonant functional forbids a bounded/finite-quasiperiodic correction despite vanishing moment maps."), ("OPEN", "A complete smooth-secular correction has not been constructed or obstructed."), open_causal),
            _evidence("twist_independence", "exceptional_current", "abstract_cone"),
            "This is the independence witness separating stabilizer moment maps from dynamical resonance functionals; it is not a full exceptional mixed-cone classification.",
        ),
        _entry(
            "einstein.ph.wm.mixed.homogeneous_twist_velocity_jet",
            _scope(theory="Weyl-Maxwell target", carrier="standard homogeneous a-coordinate balanced with an arbitrary SO(3)-rotated twist-velocity vector at A=0", degree=2, parity="homogeneous scalar plus axial ell=1", ell="0 plus 1; quadratic outputs 0,1,2", m="all by SO(3) orbit", k=0, omega="generalized zero frequency"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The homogeneous/twist input is a generalized-zero Jordan block rather than an oscillatory shell."),
            ("CERTIFIED", "The homogeneous and twist pairs are nondegenerate blocks of the standard compact phase space."),
            ("CERTIFIED", "The harmonic-normalized balance 3*a^2=4*|B|^2 satisfies the compact stabilizer constraints."),
            ("CERTIFIED", "All homogeneous, axial ell=1 and polar ell=2 output rows are solved on the A=0 SO(3) orbit."),
            _second_order(("OPEN", "No bounded-correction theorem is asserted for this generalized-zero velocity input."), ("CERTIFIED", "A complete smooth exponential-polynomial second-order correction is constructed."), open_causal),
            _evidence("standard", "twist_extension", "abstract_cone"),
            "This certifies the A=0 twist-velocity orbit only; twist position and the full global cone remain open.",
        ),
        _entry(
            "einstein.ph.wm.standard.global_bounded_cone",
            _scope(theory="Weyl-Maxwell target restricted to the standard Einstein-Maxwell generalized-zero image", carrier="complete homogeneous (a,b,c,d,Q_e,W_x) plus axial twist position/velocity vectors (A,B), with oscillatory inputs excluded", degree=2, parity="homogeneous and axial ell=1 inputs; homogeneous, axial ell=1 and polar ell=2 outputs kept distinct", ell="input 0 and 1; output 0,1,2", m="all real twist components by SO3 covariance", k=0, omega="generalized zero only"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The carrier is the complete standard generalized-zero block: K=a+b*t, C=a*t^2+(b/3)t^3+c+d*t, A_x=W_x+Q_e*t and twist A+B*t."),
            ("CERTIFIED", "The homogeneous and twist Lee-Wald blocks are nondegenerate and mutually orthogonal before the final residual quotient."),
            ("CERTIFIED", "After polynomial elimination the global moment maps force a=Q_e=0; c,d,W_x and constant A remain."),
            ("CERTIFIED", "The positive-degree ideal has real zero locus b=B=0 and Q_e*a=0; STF(B tensor B) supplies the SO3-complete twist witness."),
            _second_order(("CERTIFIED", "The complete bounded cone is {(c,d,W_x,A)}. Its homogeneous source vanishes and constant A has a time-independent polar L=2 correction."), ("CERTIFIED", "The bounded correction is also a smooth exponential-polynomial correction."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("standard_global_bounded", "standard", "taub", "abstract_cone"),
            "This is the complete bounded second-order theorem only for the standard generalized-zero carrier. Universally it forces b=B=0 and Q_e*a=0 in every finite-support bounded candidate, but the complete a/d polynomial maps, c/d/constant-A shell resonances, infinite sums, causal propagation, final residual states, observables and quantum transfer remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.electric_wilson_complete_oscillator_transport",
            _scope(theory="Weyl-Maxwell target", carrier="Q_e or W_x crossed with every certified nonzero-frequency standard q-primary or extra p-primary compact oscillator", degree=2, parity="both parities; Hodge duality may exchange representatives", ell="exceptional ell=1 and generic ell>=2", m="all allowed m", k="every 2*pi*n/L", omega="every certified nonzero real q/p shell frequency"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The carrier is the complete certified nonzero-frequency q/p inventory; duality preserves k, ell and omega while it may exchange parity representatives."),
            ("CERTIFIED", "All imported oscillator blocks have certified compact Lee-Wald forms before final residual descent."),
            ("OPEN", "This transport theorem does not solve the simultaneous stabilizer moment-map equations for the full carrier."),
            ("CERTIFIED", "Q_e-times-oscillator sources are bounded linear images and W_x-times-oscillator sources vanish, so these columns have zero P_(j,r) and R_(j,a) components."),
            _second_order(("CERTIFIED", "Electromagnetic duality supplies f_cross=star_bar f+(D_g star)[h]F_bar with unchanged frequency; the fixed-bundle lift is exact for ell>=1. W_x needs zero correction."), ("CERTIFIED", "The bounded correction is contained in the smooth exponential-polynomial class."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("electric_wilson_transport", "complete_finite_smooth", "standard_global_bounded"),
            "This removes Q_e and W_x only from oscillator cross columns. The independent global condition Q_e*a=0, the complete a/d polynomial maps, c/d/constant-A resonance, full bounded cone, all-orders duality and residual/observational/quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.circumference_complete_oscillator_column",
            _scope(theory="Weyl-Maxwell target", carrier="constant circumference c crossed with every certified nonzero-frequency standard q-primary or extra p-primary compact oscillator", degree=2, parity="both parities", ell="exceptional ell=1 and generic ell>=2", m="all allowed m", k="every 2*pi*n/L, stratified into k=0 and k!=0", omega="every certified nonzero real q/p shell frequency"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Every branch has omega_R^2=k^2/R^2+m_branch^2 along the exact circle-radius family R^2=1+eta*c."),
            ("CERTIFIED", "The action-derived current is nonradical on every standard branch and extra multiplicity block."),
            ("OPEN", "This column theorem does not solve the simultaneous compact stabilizer equations."),
            ("CERTIFIED", "At k!=0 the exact radius derivative has nonzero shell pairing proportional to c*k^2; it is R_(j,a), not P_(j,r). At k=0 ordinary index transport is bounded."),
            _second_order(("CERTIFIED", "The c-cross column is bounded-compatible exactly when c=0 or oscillator support is contained in k=0; every nonzero-k coefficient is otherwise resonantly obstructed."), ("CERTIFIED", "All k admit exact-family transport; nonzero k uses i*c*k^2*t*u/(2*omega)."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("circumference_classification", "complete_finite_smooth", "axial_current", "polar_current", "exceptional_current"),
            "This classifies only c-times-oscillator interactions. The a/d polynomial maps, k=0 d, constant-A and wave resonances, full bounded cone, all-orders, residual, observational and quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.d_times_ell2_extra",
            _scope(theory="Weyl-Maxwell target", carrier="homogeneous circumference velocity d crossed with the two extra-primary amplitudes in each parity", degree=2, parity="axial and polar", ell=2, m="all", k=0, omega="output omega_e^2=16/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The resonant output is the axial p-shell at omega_e^2=16/3."),
            ("CERTIFIED", "The extra input multiplicities are the certified nonradical axial and polar Lee-Wald blocks."),
            ("OPEN", "The simultaneous five stabilizer moment maps for this enlarged input have not been solved."),
            ("CERTIFIED", "The t=0 d-cross maps are isomorphisms in both parities with block determinant 8266752. Full-time reconstruction adds a nonzero polar-e2 P_(j,1) vector proportional to d*z2."),
            _second_order(("OPEN", "The constant resonant projections are controllable, but the polar-e2 polynomial condition d*z2=0 must be solved jointly with a and other same-channel columns."), ("OPEN", "No complete smooth-secular extension has been assembled."), open_causal),
            _evidence("d_completion", "d_full_time", "axial_current", "polar_current", "abstract_cone"),
            "The old direct fixtures evaluated t=0. Their adjoint isomorphism is retained as a constant-term statement; it is not a complete bounded d-column theorem. Other harmonics, moment maps and the joint a/d polynomial cone remain open.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ad_ell2_extra_polynomial_zero_locus",
            _scope(theory="Weyl-Maxwell target", carrier="homogeneous a,d directions crossed with all four axial/polar ell=2,k=0 extra-primary amplitudes after universal b=0", degree=2, parity="two axial and two polar extra columns", ell="0 x 2 -> 2", m="all by SO3 equivariance", k=0, omega="generalized zero crossed with omega_e=4/sqrt(3)"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The four extra amplitudes occupy the certified ell=2 p-primary shell."),
            ("CERTIFIED", "The source rows and restored d coefficient are normalized against the action-derived extra blocks."),
            ("OPEN", "This cross-ledger theorem does not solve the simultaneous compact stabilizer equations."),
            ("CERTIFIED", "The exact positive-degree ideal is <a*z_ax1,a*z_ax2,a*z_pol1,a*z_pol2,d*z_pol2>; its three algebraic faces are printed."),
            _second_order(("OPEN", "The P_(j,r) cross zero locus is complete, but constant shell resonances and self/twist products remain to be imposed."), ("CERTIFIED", "All polynomial sources admit finite secular inversion once the five stabilizer moment maps vanish, by the complete smooth theorem."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("ad_polynomial_zero", "d_full_time", "abd_matrix", "complete_finite_smooth", "abstract_cone"),
            "This certifies only the a/d-times-extra positive-degree cross ideal at ell=2,k=0. The old nonzero-extra common-zero cone survives because it already has a=b=d=0; constant resonance, other harmonics and the complete bounded cone remain open.",
        ),
        _entry(
            "einstein.ph.wm.interaction.abd_times_ell2_extra",
            _scope(theory="Weyl-Maxwell target", carrier="homogeneous generalized-zero a,b,d directions crossed with both ell=2 extra-primary amplitudes", degree=2, parity="axial and polar outputs kept separate", ell="0 x 2 -> 2", m="m=0 direct fixtures; all m by SO(3) equivariance", k=0, omega="polynomial-in-time generalized zero crossed with omega_e=4/sqrt(3)"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Every cross source lies on the ell=2 p-primary output shell with polynomial-in-time coefficients."),
            ("CERTIFIED", "The projected rows use the certified nonradical axial and polar extra-shell Lee-Wald/adjoint bases."),
            ("OPEN", "The simultaneous stabilizer zero locus including twist position and velocity has not been solved."),
            ("OPEN", "The printed a,b chains and t=0 d adjoint columns are exact, but full-time reconstruction adds a polar-e2 d*z2*t coefficient omitted by the older matrix."),
            _second_order(("OPEN", "The a/d polynomial zero locus must be recomputed with the repaired P_(j,1) column before the constant resonance matrix is used."), ("OPEN", "Secular inversion must be proved through the complete operator."), open_causal),
            _evidence("abd_matrix", "d_completion", "d_full_time", "axial_current", "polar_current", "abstract_cone"),
            "The older rank-three matrix remains evidence for its printed a,b and t=0 d columns, but its complete bounded-functional claim is superseded by the full-time d repair.",
        ),
        _entry(
            "einstein.ph.wm.interaction.abd_times_generic_k0_einstein_minus_pivot_fixtures",
            _scope(theory="Weyl-Maxwell target", carrier="homogeneous generalized-zero a,b,d directions crossed with axial or polar k=0 Einstein-minus q-primary fixtures", degree=2, parity="axial and polar kept separate", ell="direct ell=2,3 full triangular fixtures and ell=4 leading fixture", m="m=0 direct fixtures", k=0, omega="omega_-^2=lambda-sqrt(2*lambda)"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Every replayed input uses the generic Einstein-minus representative on its exact physical q-primary shell."),
            ("CERTIFIED", "The direct action rows use the same self-adjoint q-primary normalization as the frozen ell=2 axial and polar fixtures."),
            ("OPEN", "The multi-ell source fixtures do not classify the complete stabilizer common-zero locus."),
            ("CERTIFIED", "Exact ell=2,3 full triangular pivots and ell=4 leading pivots reconstruct candidates C_A=3*i*omega_-(1-3*sqrt(2*lambda)) and C_P=lambda^2(2*lambda-1)/6."),
            _second_order(("OPEN", "The candidate pivots are nonzero for physical lambda>=6, but a symbolic functional-form or degree bound is still required before promotion to every ell."), ("OPEN", "This fixture ledger does not construct the remaining smooth-secular channels."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("abd_general_ell_minus_fixtures", "abd_axial_minus", "abd_polar_minus", "taub", "abstract_cone"),
            "This is a fail-closed physical-fibre fixture row, not a general-ell theorem. All m promotion beyond each fixed ell, nonzero momentum, complete cross-ell bounded zero loci, causal propagation, all-orders integration, residual descent, observables and quantum maps remain open.",
        ),
        _entry(
            "einstein.ph.wm.interaction.homogeneous_twist_times_ell2_extra",
            _scope(theory="Weyl-Maxwell target", carrier="complete homogeneous a,b,d and axial twist position/velocity block crossed with the axial-plus-polar ell=2 extra-primary multiplicity space; c,W_x,Q_e removed", degree=2, parity="all axial/polar inputs and outputs retained", ell="(0 or 1) x 2 -> resonant L=2", m="all by one nonzero Clebsch-Gordan fixture and SO(3) equivariance", k=0, omega="generalized-zero global/twist data crossed with omega_e=4/sqrt(3)"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The output is the ell=2 p-primary shell; the non-axisymmetric channel <1,1;2,0|2,1>=sqrt(2)/2 fixes the unique SO(3)-equivariant V1 tensor V2 -> V2 map."),
            ("CERTIFIED", "All four output adjoint rows are normalized against the certified nonradical axial and polar extra-shell blocks."),
            ("OPEN", "The five stabilizer moment maps have not yet been solved simultaneously with the completed resonance matrix."),
            ("OPEN", "The twist-position and twist-velocity adjoint matrices remain exact, but the imported d column was evaluated at t=0 and omits the repaired polar-e2 P_(j,1) coefficient."),
            _second_order(("OPEN", "The simultaneous zero locus must be rechecked against the full-time d polynomial before this is called a complete bounded matrix."), ("OPEN", "Smooth exponential-polynomial secular sufficiency is not inferred from the resonant projection alone."), open_causal),
            _evidence("homogeneous_twist_matrix", "abd_matrix", "d_full_time", "axial_current", "polar_current", "abstract_cone"),
            "The twist adjoint blocks are retained, but the complete bounded-matrix lifecycle is withdrawn pending the repaired joint a/d polynomial solve.",
        ),
        _entry(
            "einstein.ph.wm.mixed.aligned_twist_ell2_extra_compatibility_face",
            _scope(theory="Weyl-Maxwell target", carrier="complete declared homogeneous/twist block crossed with one ell=2,k=0 generic extra multiplet; surviving locus is the aligned SO(3) orbit", degree=2, parity="all four axial/polar extra multiplicities retained", ell="(0 or 1) x 2 -> resonant 2", m="all modulo SO(3); every solution is m=0 about the common twist axis", k=0, omega="generalized-zero global/twist data crossed with omega_e=4/sqrt(3)"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The extra input lies on the generic ell=2 p-shell and the twist input is generalized-zero."),
            ("CERTIFIED", "The extra occupation X uses the direct positive axial-plus-polar Lee-Wald Gram; the standard twist block supplies the opposite Taub sign."),
            ("CERTIFIED", "The complete common-zero locus has a=b=d=0, A=alpha*n, B=beta*n and beta^2=Q_e^2/2+(2/3)X; all five stabilizer maps vanish."),
            ("CERTIFIED", "Exact coefficient elimination and rank minors prove every common zero is an SO(3) rotation of the aligned m=0 face; there is no additional off-axis branch in the declared carrier."),
            _second_order(("OBSTRUCTED", "Every nonzero orbit point has B!=0 and an uncancellable zero-frequency polar L=2 source coefficient -7*B^2*t^2, outside the image of bounded finite-quasiperiodic corrections."), ("CERTIFIED", "Every orbit point admits a real smooth spatially periodic finite exponential-polynomial correction. Global/global, all 16 aligned twist--extra L=1,3 channels, and all 20 C4 extra/extra bilinear generators are coefficient-explicit; the sole homogeneous source cancels as beta^2-Q_e^2/2-(2/3)X=0."), open_causal),
            _evidence("global_self_coefficients", "extra_self_coefficients", "aligned_twist_extra_coefficients", "global_extra_smooth_extension", "global_extra_bounded_obstruction", "complete_global_extra_cone", "aligned_twist_extra_face", "homogeneous_twist_matrix", "axial_current", "polar_current", "taub", "abstract_cone"),
            "This correction-class split and coefficient ledger are complete only in one declared homogeneous/twist times ell=2,k=0 shared-axis SO3 orbit. It is not an opposite-momentum or multi-fibre classification, causal theorem, all-orders family, residual state or quantum claim.",
        ),
        _entry(
            "einstein.ph.wm.mixed.complete_global_ell2_extra_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="complete homogeneous, twist and axial-plus-polar ell=2,k=0 extra-primary carrier", degree=2, parity="homogeneous, axial twist, and both generic extra parities", ell="input 0,1,2 with complete quadratic output inventory", m="all by SO3 covariance", k=0, omega="generalized zero plus +/-4/sqrt(3)"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The carrier adjoins the complete nonradical ell=2,k=0 p-primary block to the standard generalized-zero sector."),
            ("CERTIFIED", "The extra occupation has positive Gram weights 1296,208/3,22464,12288; standard global and twist blocks retain their certified forms."),
            ("CERTIFIED", "After boundedness forces b=B=0, mu_H=-a^2-Q_e^2-(4/3)X is strictly negative away from a=Q_e=x_extra=0."),
            ("CERTIFIED", "The repaired a/d P ideal and old common-zero orbit are reconciled; no constant resonance solve can restore an extra mode already excluded by mu_H."),
            _second_order(("CERTIFIED", "The complete bounded cone is exactly {(c,d,W_x,A)} and contains no nonzero ell=2 extra direction."), ("CERTIFIED", "The complete smooth-secular condition remains the five-moment-map zero locus and is strictly larger."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("complete_global_ell2_bounded", "standard_global_bounded", "ad_polynomial_zero", "complete_global_extra_cone", "global_extra_bounded_obstruction", "complete_finite_smooth"),
            "This is complete only for the homogeneous/twist plus ell=2,k=0 extra carrier. Standard Einstein oscillators, other harmonics and momenta, complete finite bounded, all-orders, residual, observational and quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.aligned_global_axial_ell2_minus_extra_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="complete homogeneous and aligned axial-twist data plus axial ell=2,m=0,k=0 Einstein-minus and both extra primaries", degree=2, parity="homogeneous and axial", ell="input 0,1,2 with complete declared quadratic outputs", m="aligned m=0", k=0, omega="generalized zero, sqrt(6-2*sqrt(3)), and 4/sqrt(3)"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The wave branch contains the nonradical opposite-sign Einstein-minus q-primary and both axial extra p-primary coefficients."),
            ("CERTIFIED", "The direct action Hessian is self-adjoint; the a,b,d shell pairing has independent t, t^2 and constant pivots, while the wave source coefficients are action-normalized."),
            ("CERTIFIED", "The full bounded zero-frequency source, not only mu_H, forces Q_e=0; the remaining minus-extra occupation equation is exact."),
            ("CERTIFIED", "For nonzero wave data the direct shell ideal forces a=b=d=0; universal boundedness also forces B_z=0."),
            _second_order(("CERTIFIED", "The cone is the union of the static (c,d,W_x,A_z) branch and the wave branch (c,W_x,A_z) times x_minus=(972*x_e1+52*x_e2)/(27*(-6+5*sqrt(3)))."), ("CERTIFIED", "Every bounded correction is also a smooth exponential-polynomial correction."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("aligned_global_minus_extra_bounded", "abd_axial_minus", "standard_global_bounded", "electric_wilson_transport", "circumference_classification", "taub", "abstract_cone"),
            "This is complete only on the aligned axial ell=2,m=0,k=0 face. Einstein-plus, polar input, all m, other ell and momenta, infinite sums, all-orders, residual, observational and quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.constant_twist_ell2_projector_repair",
            _scope(theory="Weyl-Maxwell target", carrier="constant axial twist position crossed with the complete axial/polar ell=2,k=0 Einstein q-primary and extra p-primary wave carrier", degree=2, parity="axial and polar with output carrier types kept distinct", ell="1 x 2 with correctly typed L=2 same-shell projection and L=1,3 off-shell outputs", m="all by SO3 equivariance", k=0, omega="all ell=2 q/p shells"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The wave carrier retains the complete ell=2 q/p shell decomposition and the constant generalized-zero twist position."),
            ("CERTIFIED", "The q/p adjoint representatives and action-derived wave moment maps retain their independently certified normalization."),
            ("CERTIFIED", "The wave self-source is bounded-solvable exactly on mu_H=mu_J1=mu_J2=mu_J3=0; constant twist position adds no moment-map restriction."),
            ("CERTIFIED", "The former nonzero incidence used *dY_11 (lambda=2) against lambda=6 adjoints. Direct replay with *dY_21 makes every Einstein and extra same-shell position map zero; L=1,3 outputs remain off shell."),
            _second_order(("CERTIFIED", "Z2_bounded(A,wave)=R_A^3 x {wave: mu_H=mu_J1=mu_J2=mu_J3=0}."), ("CERTIFIED", "Every certified bounded correction is also a smooth finite exponential-polynomial correction."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("constant_twist_ell2_projector_repair", "fixed_ell_combined", "standard_global_bounded", "taub"),
            "This lifecycle repair supersedes the old constant-twist counterexample and every nonzero same-shell incidence matrix derived from the mistyped axial projector. It is complete only for constant twist position with ell=2,k=0 waves; velocity, other globals, other ell/momenta, causal propagation and higher lifecycles remain separate.",
        ),
        _entry(
            "einstein.ph.wm.interaction.constant_twist_wave_counterexample",
            _scope(theory="Weyl-Maxwell target", carrier="one constant axial twist-position tangent crossed with a rotationally neutral ell=2,k=0 Einstein-minus/extra balanced wave", degree=2, parity="axial input with axial resonant output", ell="1 x 2 -> 2", m="twist m=1 crossed with wave m=0", k=0, omega="omega_extra=4/sqrt(3) and the distinct omega_minus shell"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The twist is generalized-zero and the wave uses distinct certified Einstein-minus and extra p-primary shells."),
            ("CERTIFIED", "The balanced wave is nonnull and has vanishing H,J_i moment maps before the twist-position interaction is tested."),
            ("CERTIFIED", "The complete stabilizer moment maps vanish for the declared rotationally neutral wave with constant twist position."),
            ("CERTIFIED", "The twist-position times axial-extra e1 column has the exact adjoint-cokernel coefficient 24*sqrt(3); the twist-minus term lies at a different frequency and cannot cancel it."),
            _second_order(("OBSTRUCTED", "This explicit nonzero-A wave tangent has a nonzero bounded resonance functional despite vanishing stabilizer moment maps."), ("OPEN", "A secular correction may absorb the shell resonance, but no correction is constructed in this certificate."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("constant_twist_wave_counterexample", "homogeneous_twist_matrix", "taub", "abstract_cone"),
            "This is one independence witness for the bounded tangent-cone theorem. It refutes arbitrary constant twist as a spectator on wave branches but does not classify the complete nonzero-A zero locus.",
        ),
        _entry(
            "einstein.ph.wm.interaction.constant_twist_ell2_extra_position_zero_locus",
            _scope(theory="Weyl-Maxwell target", carrier="constant axial twist position A in V1 crossed with the complete axial-plus-polar ell=2,k=0 extra p-primary space C4 tensor V2", degree=2, parity="all four axial/polar extra multiplicities", ell="1 x 2 -> resonant 2", m="all twist and wave components; nonzero A reduced covariantly to the z axis", k=0, omega="omega_extra=4/sqrt(3)"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The carrier is the complete 20-complex-dimensional positive-frequency ell=2 extra p-primary shell crossed with a constant real twist position."),
            ("CERTIFIED", "The four extra multiplicities retain their nondegenerate action-derived Lee--Wald block; the resonance calculation uses the independently derived adjoint matrix."),
            ("OPEN", "This row does not impose the H,J_i moment maps or intersect the extra shell with the Einstein q-primary balance."),
            ("CERTIFIED", "For nonzero A, SO3 covariance gives ker R_A=(C4 tensor ker T_A)+(ker P tensor V2), where ker P=span{polar_e1,-4*sqrt(3)*axial_e1+15*polar_e2}; its complex dimension is 12."),
            _second_order(("OPEN", "The twist-position resonance zero locus is necessary and sufficient on the extra shell; the Einstein-shell maps are now classified separately, while their moment-cone intersection, wave self-products and nonresonant inversion remain open."), ("NOT_APPLICABLE", "The complete smooth-secular theorem is recorded separately; this row classifies a bounded-only resonance functional."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("constant_twist_extra_position_zero_locus", "homogeneous_twist_matrix", "aligned_twist_extra_face", "constant_twist_wave_counterexample"),
            "This is a complete zero-locus theorem only for twist position times the ell=2 extra p-primary shell. It does not merge that shell with the separately certified Einstein q-primary kernels or classify twist velocity, the complete mixed bounded cone, other ell or momentum, causal propagation, residual descent or quantum theory.",
        ),
        _entry(
            "einstein.ph.wm.interaction.constant_twist_ell2_einstein_position_zero_locus",
            _scope(theory="Weyl-Maxwell target", carrier="constant axial twist position A in V1 crossed with both axial/polar ell=2,k=0 Einstein q-primary shells", degree=2, parity="axial and polar multiplicities on each plus/minus shell", ell="1 x 2 -> resonant 2", m="all twist and wave components; nonzero A reduced covariantly to the z axis", k=0, omega="omega_minus=sqrt(6-2*sqrt(3)); omega_plus=sqrt(6+2*sqrt(3))"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The carrier is the complete 20-complex-dimensional positive-frequency axial/polar Einstein q-primary space on the two distinct ell=2 shells."),
            ("CERTIFIED", "Each Einstein shell has its action-derived Lee--Wald weight; the direct source rows are paired against independently certified self-adjoint q-shell representatives."),
            ("OPEN", "This row does not impose H,J_i=0 or intersect the four-dimensional Einstein resonance kernel with the twelve-dimensional extra-shell kernel."),
            ("CERTIFIED", "Both shell incidence matrices equal [[0,216/5],[432/5,0]] and are invertible. Hence only the axial and polar m=0 coefficients survive on each shell; the combined complex kernel dimension is four."),
            _second_order(("OPEN", "The shellwise twist-position resonance kernels are necessary and sufficient for this cross term, but the simultaneous stabilizer/wave-self-source zero locus and complete correction remain open."), ("NOT_APPLICABLE", "The complete smooth-secular theorem is recorded separately; this row classifies a bounded-only resonance functional."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("constant_twist_einstein_position_zero_locus", "constant_twist_extra_position_zero_locus", "homogeneous_twist_matrix", "taub"),
            "This is a complete zero-locus theorem only for constant twist position times both ell=2 Einstein q-primary shells. It does not classify twist velocity, simultaneous moment and all-branch resonance equations, the complete mixed bounded cone, other ell or momentum, causal propagation, residual descent or quantum theory.",
        ),
        _entry(
            "einstein.ph.wm.interaction.constant_twist_ell2_moment_resonance_cone",
            _scope(theory="Weyl-Maxwell target", carrier="one nonzero constant axial twist position crossed with every axial/polar ell=2,k=0 Einstein-plus, Einstein-minus and extra-primary coefficient", degree=2, parity="both parities and all four extra multiplicities", ell="global twist ell=1 crossed with wave ell=2", m="all m=-2,...,2 relative to the twist axis", k=0, omega="generalized zero twist and all three ell2 q/p frequencies"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The resonance carrier has sixteen complex dimensions: four Einstein q-primary and twelve extra p-primary directions after imposing every constant-twist same-shell projection."),
            ("CERTIFIED", "The direct extra-coordinate Gram is diag(1296,208/3,9,22464); its resonance kernel splits G-orthogonally into two spin-two copies and two neutral m=0 directions."),
            ("CERTIFIED", "The complete common zero cone is J_z=J_plus=0 on the two extra spin-two copies together with (6+2*sqrt(3))*A_plus+(16/3)*A_extra-(6-2*sqrt(3))*A_minus=0."),
            ("CERTIFIED", "The twist-position resonance support and all H,J_i equations are necessary and sufficient. A nonaxisymmetric witness has c_-2=c_2=polar_e1, A_extra=18 and A_minus=24+8*sqrt(3)."),
            _second_order(("OPEN", "This predecessor row stops at the exact moment/resonance cone; bounded sufficiency is certified by the separate constant_twist_ell2_complete_bounded_cone successor row."), ("CERTIFIED", "The existing complete finite-harmonic smooth exponential-polynomial theorem contains this finite carrier."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("constant_twist_ell2_moment_resonance_cone", "constant_twist_einstein_position_zero_locus", "constant_twist_extra_position_zero_locus", "moment_cone", "complete_finite_smooth"),
            "This predecessor is the complete simultaneous stabilizer and same-shell twist-position resonance cone only for nonzero constant A and ell=2,k=0 waves. Its former L=1,3 inversion gate is closed only in the separately evidenced successor row; twist velocity, other ell/momenta, causal propagation, residual descent and quantum theory remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.constant_twist_ell2_complete_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="one constant axial twist position plus the complete axial/polar ell=2,k=0 Einstein plus/minus and extra-primary wave carrier", degree=2, parity="axial and polar", ell="global 1 plus wave 2; outputs 0,...,4", m="all wave m; for nonzero A expressed relative to the twist axis", k=0, omega="generalized zero plus the three distinct ell2 positive-frequency shells"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The same-background carrier retains the complete q/p primary decomposition and the constant-twist global direction; no modes are identified across backgrounds."),
            ("CERTIFIED", "The branch-normalized Lee--Wald forms define the four stabilizer moment equations and the raw-to-current coefficient crosswalk."),
            ("CERTIFIED", "For nonzero A, the Einstein shells are supported at m_A=0, the nonzero-m extra coefficients lie in the two-dimensional internal position kernel, and H=J_i=0; this intersection is nonempty and includes an off-axis +/-2 witness."),
            ("CERTIFIED", "The q/p shell kernels exhaust the twist--wave resonances; all L=1,3 outputs are off shell."),
            _second_order(("CERTIFIED", "The displayed shell restrictions plus H=J_i=0 are necessary and sufficient for a bounded correction on the declared carrier."), ("CERTIFIED", "Every certified bounded correction is also smooth exponential-polynomial; the larger unrestricted secular cone is not reclassified."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl--Maxwell complex is certified.")),
            _evidence("constant_twist_ell2_complete_bounded_cone", "constant_twist_einstein_position_zero_locus", "constant_twist_extra_position_zero_locus", "fixed_ell_combined", "standard_global_bounded", "taub"),
            "This theorem excludes twist velocity and every other homogeneous tangent, other ell, nonzero or opposite momentum, unrestricted secular corrections, causal propagation, all-orders integration, residual descent, observables and quantum theory.",
        ),
        _entry(
            "einstein.ph.wm.mixed.twist_position_velocity_ell2_complete_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="arbitrary real axial twist position and velocity plus the complete axial/polar ell=2,k=0 Einstein plus/minus and extra-primary wave carrier", degree=2, parity="axial generalized-zero twist and axial/polar waves", ell="global 1 plus wave 2; outputs 0,...,4", m="all three real twist components and all wave m=-2,...,2", k=0, omega="generalized zero plus the three distinct ell2 positive-frequency shells", charge_sector="fixed magnetic U(1) bundle P_N with N=2; electric, Wilson-line, circumference and all other homogeneous tangents set to zero"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The generalized-zero twist position/velocity pair is retained before the bounded second-order test; no mode is identified across backgrounds or carrier languages."),
            ("CERTIFIED", "The action-derived twist form distinguishes the constant position from its Jordan velocity partner."),
            ("CERTIFIED", "Boundedness forces B=0 because the polar L=2 source contains STF(B tensor B)*t^2 with norm squared 2|B|^4/3; the remaining H,J_i and shell equations are exactly the constant-position cone."),
            ("CERTIFIED", "The complete bounded resonance ledger is the constant-position q/p incidence ledger on the B=0 face."),
            _second_order(("CERTIFIED", "B=0 together with the constant-position shell restrictions and H=J_i=0 is necessary and sufficient on the declared carrier."), ("CERTIFIED", "The bounded corrections are smooth exponential-polynomial; the larger secular cone with B nonzero is not classified."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("twist_position_velocity_ell2_complete_bounded_cone", "constant_twist_ell2_complete_bounded_cone", "standard_global_bounded", "taub"),
            "Other homogeneous tangents, other ell, nonzero or opposite momentum, the unrestricted secular cone, causal propagation, all-orders integration, residual observables and quantum theory remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.twist_circumference_wilson_ell2_complete_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="constant circumference c, flat Wilson W_x, axial twist position/velocity A,B and the complete axial/polar ell=2,k=0 q/p wave carrier", degree=2, parity="homogeneous spectators, axial generalized-zero twist and axial/polar waves", ell="global 0,1 plus wave 2; outputs 0,...,4", m="all twist components and wave m", k=0, omega="generalized zero plus all ell2 shells", charge_sector="fixed magnetic bundle N=2; a,b,d,Q_e set to zero"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The c and W_x global directions are retained as distinct fixed-background tangent coordinates."),
            ("CERTIFIED", "Their source-theory pairings remain those of the standard homogeneous/Wilson block."),
            ("CERTIFIED", "The bounded cone is R_c x R_Wx times the complete twist-wave cone: c and W_x are arbitrary, B=0, and the constant-position H,J_i and shell equations remain."),
            ("CERTIFIED", "Exact k=0 radius transport removes the c-times-wave source, while every W_x mixed source vanishes because delta F=0."),
            _second_order(("CERTIFIED", "The displayed product cone is necessary and sufficient on the declared carrier."), ("CERTIFIED", "The bounded corrections are smooth exponential-polynomial; the unrestricted secular cone is not reclassified."), ("NO_CERTIFIED_MAP", "No retarded Weyl-Maxwell complex is certified on this background.")),
            _evidence("twist_circumference_wilson_ell2_complete_bounded_cone", "twist_position_velocity_ell2_complete_bounded_cone", "circumference_classification", "electric_wilson_transport", "standard_global_bounded"),
            "The dynamical globals a,d,Q_e, other harmonics and momenta, causal propagation, all-orders integration, residual observables and quantum theory remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.d_twist_ell2_complete_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="circumference position/velocity c,d, Wilson W_x, twist A,B and complete ell=2,k=0 q/p waves", degree=2, parity="homogeneous, axial and polar", ell="global 0,1 plus wave 2", m="all twist and wave m", k=0, omega="generalized zero plus all ell2 shells", charge_sector="fixed N=2 magnetic bundle; a,b,Q_e set to zero"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The same-background d,c,W_x,A,B and q/p wave carriers remain distinct before the quadratic test."),
            ("CERTIFIED","The action-normalized Einstein-minus block supplies the isolated d-cross pivot in each parity."),
            ("CERTIFIED","Every nonzero H=0 wave contains Einstein-minus occupation and therefore forces d=0; the wave-free static stratum retains arbitrary d."),
            ("CERTIFIED","SO3 multiplicity one promotes the nonzero d pivot to all m, and axial/polar outputs cannot cancel."),
            _second_order(("CERTIFIED","The bounded cone is exactly the union of the static d stratum and the d=0 predecessor wave cone."),("CERTIFIED","The bounded corrections lie in the smooth exponential-polynomial class; the unrestricted secular cone is not reclassified."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("d_twist_ell2_complete_bounded_cone","twist_circumference_wilson_ell2_complete_bounded_cone","abd_axial_minus","abd_polar_minus","moment_cone","standard_global_bounded"),
            "Radion and electric tangents, other harmonics/momenta, causal propagation, all-orders integration, residual observables and quantum theory remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="complete standard homogeneous (a,b,c,d,Q_e,W_x), axial twist (A,B), and every axial/polar ell=2,k=0 q/p wave coefficient", degree=2, parity="homogeneous, axial and polar", ell="input 0,1,2 with all quadratic outputs", m="all twist and wave m", k=0, omega="generalized zero plus all ell2 shells", charge_sector="fixed magnetic U(1) bundle P_N with N=2 and the complete electric/holonomy tangent block included"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","This is the complete same-background standard global/twist plus ell2,k0 carrier; no cross-background identification is used."),
            ("CERTIFIED","The action-derived moment and branch pairings distinguish the static moduli, dynamical globals and all q/p wave branches."),
            ("CERTIFIED","The static stratum has a=b=Q_e=B=0; every nonzero wave additionally forces d=0, while c,W_x and the constant-twist incidence cone survive."),
            ("CERTIFIED","The all-m radion pivot and independent zero-frequency E11=Q_e^2/2 witness close the last two dynamical global directions."),
            _second_order(("CERTIFIED","The displayed static/wave union is necessary and sufficient for bounded corrections on the complete declared carrier."),("CERTIFIED","Bounded corrections lie in the smooth exponential-polynomial class; the unrestricted secular cone is not reclassified."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("complete_global_twist_ell2_bounded_cone","d_twist_ell2_complete_bounded_cone","global_ell2_both_parity_bounded","abd_axial_minus","abd_polar_minus","standard_global_bounded","electric_wilson_transport"),
            "Other ell, nonzero momentum, unrestricted secular corrections, causal propagation, all-orders integration, residual observables and quantum theory remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.global_axial_ell2_all_m_minus_extra_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="complete homogeneous and axial-twist globals plus axial ell=2,k=0 Einstein-minus and both extra primaries", degree=2, parity="homogeneous and axial", ell="input 0,1,2 with every output L=0,...,4", m="all wave m=-2,...,2 and arbitrary real twist vector", k=0, omega="generalized zero, sqrt(6-2*sqrt(3)), and 4/sqrt(3)"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The axial q/p wave block retains every m and both extra multiplicities; global a,b,d are rotational scalars."),
            ("CERTIFIED", "Schur's lemma promotes the nonzero direct m=0 a,b,d shell pivots to scalar identities on V_2; the wave currents remain action-normalized."),
            ("CERTIFIED", "The wave density matrices satisfy total H=J_1=J_2=J_3=0; the independent bounded homogeneous row excludes Q_e."),
            ("OPEN", "The A=0 zero-frequency axial L=1 source has an explicit constant right inverse, but a perpendicular constant twist times axial extra e1 has adjoint coefficient 24*sqrt(3)."),
            _second_order(("OPEN", "The wave-free static branch with arbitrary A and the complete A=0 axial wave-density subcone are certified; the nonzero-A wave zero locus is open."), ("CERTIFIED", "The certified bounded subcones embed in the smooth exponential-polynomial class."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("global_axial_all_m_bounded", "constant_twist_wave_counterexample", "axial_all_m_bounded", "aligned_global_minus_extra_bounded", "abd_axial_minus", "standard_global_bounded", "taub", "abstract_cone"),
            "The former arbitrary-A product claim is withdrawn. This row certifies the static branch and A=0 axial ell=2,k=0 wave subcone only; nonzero-A, polar waves, other ell and momenta, infinite sums and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.global_ell2_all_m_both_parity_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="complete standard homogeneous/twist globals plus every axial and polar ell=2,k=0 Einstein-plus, Einstein-minus and both extra-primary coefficient", degree=2, parity="homogeneous, axial and polar", ell="input 0,1,2 with complete ell2 quadratic output theorem", m="all wave m=-2,...,2 and all three real twist components", k=0, omega="generalized zero and every ell2 q/p shell"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The wave carrier contains every axial/polar ell=2 q-primary and both p-primary multiplicities at allowed k=0 frequencies."),
            ("CERTIFIED", "The direct axial and polar m=0 action-source pivots promote by SO3 multiplicity one; all wave currents and Taub maps retain their action normalization."),
            ("CERTIFIED", "A nonzero common zero necessarily contains an Einstein-minus component; the full homogeneous source independently excludes electric tangent Q_e on the wave branch."),
            ("OPEN", "The A=0 ell2 output ledger is invertible off the stabilizer cokernel and its compatible L1 source has a constant right inverse; nonzero-A adds an independent twist-position resonance map."),
            _second_order(("OPEN", "The static branch, the complete A=0 all-m axial--polar wave cone, and the constant-twist-only nonzero-A incidence cone are certified; interactions with the other homogeneous tangents remain open."), ("CERTIFIED", "The certified bounded subcones are smooth finite exponential-polynomial corrections."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl--Maxwell complex is certified.")),
            _evidence("global_ell2_both_parity_bounded", "constant_twist_ell2_complete_bounded_cone", "constant_twist_wave_counterexample", "global_axial_all_m_bounded", "axial_all_m_bounded", "abd_axial_minus", "abd_polar_minus", "standard_global_bounded", "taub", "abstract_cone"),
            "This partial predecessor is superseded for the complete ell=2,k=0 global/twist carrier by einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone. Its historical static, A=0 wave and constant-twist-only strata remain certified; it must not be used to reopen the now-closed radion, electric or simultaneous-twist gates.",
        ),
        _entry(
            "einstein.ph.wm.interaction.fixed_ell_constant_twist_factorization",
            _scope(theory="Weyl-Maxwell target", carrier="one nonzero constant axial twist position crossed with one arbitrary fixed generic ell,k=0 q/p wave block", degree=2, parity="axial and polar multiplicity spaces retained", ell="one arbitrary integer ell>=2", m="all m=-ell,...,ell", k=0, omega="each fixed-ell Einstein plus/minus q shell and extra p shell separately", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The fixed-ell q/p branch multiplicity spaces remain distinct; no cross-background or cross-branch identification is used."),
            ("CERTIFIED","SO3 multiplicity one factors every all-m resonance map as (A_hat dot J_ell) tensor a finite action-normalized multiplicity matrix."),
            ("CERTIFIED","The twist adds no same-shell equation beyond the independently certified compact stabilizer moment maps."),
            ("CERTIFIED","Action-normalized Feynman--Hellmann reduction gives Q_(ell,+)=Q_(ell,-)=0 and P_ell=0 for every fixed ell>=2 at k=0."),
            _second_order(("CERTIFIED","For every one fixed ell>=2, Z2_bounded(A,wave)=R_A^3 times the complete wave common stabilizer zero cone; both neighboring angular outputs are uniformly off shell."),("CERTIFIED","Bounded corrections lie in the complete finite-support smooth-secular class."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("fixed_ell_constant_twist_bounded_cone","fixed_ell_constant_twist_zero_map","fixed_ell_constant_twist_factorization","constant_twist_ell2_projector_repair","fixed_ell_combined","global_fixed_ell_k0_bounded"),
            "The bounded product cone is certified for every one fixed ell>=2 at k=0. Finite multi-ell sums, nonzero momentum, causal propagation and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.nonzero_k_constant_twist_same_shell",
            _scope(theory="Weyl-Maxwell target", carrier="one nonzero constant axial twist position crossed with one fixed generic ell and one real signed nonzero-momentum q/p wave block", degree=2, parity="axial and polar multiplicities retained", ell="every one fixed integer ell>=2", m="all m=-ell,...,ell relative to the twist axis", k="every allowed 2*pi*n/L with n!=0; conjugate +/-k pair retained", omega="Einstein q-minus, q-plus and extra p shells kept distinct", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The q-minus, q-plus and p shells retain their exact nonzero-k dispersions and are not merged."),
            ("CERTIFIED","The action-derived axial/polar shell Grams are nondegenerate on every physical momentum fibre."),
            ("OPEN","The compact stabilizer maps remain separate necessary conditions; this row isolates the independent twist-wave same-shell functional."),
            ("CERTIFIED","Feynman--Hellmann gives q-minus/+ scalars +/-4*k*sqrt(2*lambda) and p scalar -2*k, each multiplying (A_hat dot J_ell) and the nondegenerate branch Gram; the common kernel is exactly m_A=0, and both neighboring angular outputs are invertible."),
            _second_order(("OPEN","The complete A-times-wave bilinear column has a bounded correction exactly on the m_A=0 face; wave-wave terms, opposite-momentum cross terms and other global constraints keep the full tangent equation open."),("NOT_APPLICABLE","Secular corrections can absorb a same-shell source; this theorem does not reclassify the already certified smooth-secular cone."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("nonzero_k_constant_twist_same_shell","fixed_ell_constant_twist_zero_map","fixed_ell_constant_twist_factorization","axial_current","polar_current"),
            "The theorem is complete only for the constant-twist-times-wave bilinear column at one fixed generic ell and one nonzero absolute momentum. Opposite-momentum wave-wave terms, multiple |k| fibres, the full bounded tangent equation and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.finite_multimomentum_resonance_divisor",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with one common circumference L; before final residual quotient", carrier="arbitrary finite set of positive-offset physical and extra oscillator branches at arbitrary signed compact momentum integers", degree=2, parity="all parities retained before source projection", ell="arbitrary finite input and angularly allowed output set", m="arbitrary finite Clebsch-Gordan-allowed set", k="k_n=2*pi*n/L for finitely many signed nonzero integers n", omega="every signed quadratic sum/difference channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All q-minus, p-extra, q-plus and exceptional positive-offset shells retain their branch and signed compact-momentum labels."),
            ("CERTIFIED","The same-background branch dictionary supplies the action-derived source/target current blocks; this row does not identify their coefficients."),
            ("NOT_APPLICABLE","This is nonzero-frequency shell arithmetic; zero-frequency stabilizer components remain separate Taub rows."),
            ("CERTIFIED","For rho=(2*pi/L)^2 the squared shell divisor is linear: each nonidentity finite-carrier channel has at most one admissible positive algebraic rho, while identity channels remain explicit source-matrix gates."),
            _second_order(("OPEN","A shell collision is only a candidate resonant functional; no bounded correction or obstruction is inferred without the projected source coefficient."),("OPEN","Off-shell channels are invertible, but identity and zero-frequency rows prevent a general smooth-secular promotion."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("finite_multimomentum_divisor","twist_aligned_opposite_momentum_gate","branch_dictionary"),
            "Finite-carrier shell arithmetic only. Identity-resonant rows, source coefficients, the complete multiple-|k| tangent cone, infinite momentum support, final residual descent and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_identity_audit",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with arbitrary common circumference L; before final residual quotient", carrier="all q-minus, p-extra and q-plus ell=2 oscillators on cross pairs between |n|=1 and |n|=2", degree=2, parity="all input/output parity combinations conservatively retained", ell="input 2 x 2; outputs L=1,2,3,4 and separately exact nonzero-Fourier L=0", m="all Clebsch-Gordan-allowed values", k="signed n in {+/-1,+/-2} times 2*pi/L, restricted to cross-|n| pairs", omega="all signed temporal sum/difference channels", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All three input primaries, eleven target shells and both relative spatial signs retain their branch and momentum labels in 198 canonical rows."),
            ("CERTIFIED","Every row uses the same-background action-derived source/target carrier; no source coefficient or pairing value is inferred."),
            ("NOT_APPLICABLE","The audit concerns nonzero-frequency cross-fibre shell identity; zero-frequency stabilizer maps remain separate."),
            ("CERTIFIED","No canonical row has both circumference-divisor coefficients zero, so no |n|=1 times |n|=2 collision persists for every circumference; the exceptional set is finite."),
            _second_order(("OPEN","At each isolated exceptional circumference the projected source coefficient remains an independent resonant-functional gate."),("OPEN","Same-fibre, zero-frequency and isolated cross-fibre rows prevent a complete smooth-secular promotion."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("ell2_two_abs_momentum_identity_audit","finite_multimomentum_divisor","branch_dictionary"),
            "Identity-resonance audit only for ell=2 cross pairs between |n|=1 and |n|=2. Isolated candidates, source coefficients, same-fibre rows, the full two-fibre tangent cone and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_isolated_candidates",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference restricted to one of 21 exact algebraic candidates; before final residual quotient", carrier="all q-minus, p-extra and q-plus ell=2 oscillators on cross pairs between |n|=1 and |n|=2", degree=2, parity="all input/output parity combinations conservatively retained before source projection", ell="input 2 x 2; candidate outputs L=1,2,3,4 with nonzero-Fourier L=0 separately exact", m="all Clebsch-Gordan-allowed values", k="signed n in {+/-1,+/-2} times 2*pi/L, restricted to cross-|n| pairs", omega="the exact SUM or DIFFERENCE channel assigned row by row", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All three input primaries and every retained target retain their exact branch, signed-momentum and temporal-channel labels."),
            ("CERTIFIED","Every candidate uses the same-background action-derived source/target carrier; no projected source coefficient or pairing value is inferred."),
            ("NOT_APPLICABLE","This is a nonzero-frequency shell-collision ledger; zero-frequency stabilizer moment maps remain separate necessary conditions."),
            ("CERTIFIED","Exact positivity and the unsquared temporal-sign test reduce the 198 identity-audit rows to 21 admissible rows at 21 distinct positive algebraic rho values, containing both SUM and DIFFERENCE channels."),
            _second_order(("OPEN","This resonance-location row does not import the later cone theorems: indices 1-15 are bounded-origin, and indices 16-21 have certified nonzero points but not full cone classifications."),("OPEN","Off-shell rows are removable, but this location ledger does not classify the smooth-secular amplitude sets."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("ell2_two_abs_momentum_isolated_candidates","collision_scalar_separation","ell2_two_abs_momentum_identity_audit","finite_multimomentum_divisor","branch_dictionary"),
            "Exact resonance-location theorem only for ell=2 cross pairs between |n|=1 and |n|=2. Later rows close bounded origin for candidates 1-15 and exhibit nonzero bounded points for 16-21; the six full cone geometries and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_collision_scalar_separation_classification",
            _scope(theory="Weyl-Maxwell target", background="21 distinct tuned compact magnetically supported Plebanski-Hacyan circumference fibres, retained as separate atlas subscopes", boundaries="closed S1_L times S2 before final residual quotient", carrier="candidatewise complete generic ell=2 q-minus, p-extra and q-plus coefficients on signed n=(1,-2) or n=(1,2) fibres", degree=2, parity="axial and polar", ell=2, m="all m=-2,...,2", k="candidatewise signed two-fibre momenta; no cross-rho identification", omega="all generic q-minus, p-extra and q-plus shells", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","All 21 exact rho values and their signed momentum orientations are retained as distinct background rows in the imported ledger."),
            ("CERTIFIED","The action-derived q-minus negative and p-extra/q-plus positive current signs are checked in both parities."),
            ("CERTIFIED","A universal midpoint factorization strictly separates every positive-rho n=(1,-2) carrier, including candidates 1-15; candidates 16-21 have exact positive Farkas dependencies and nonzero scalar-null occupations."),
            ("OPEN","The scalar theorem makes resonance ideals redundant for indices 1-15. Later certificates exhibit one resonance-compatible point at each same-sign index 16-21, but do not classify the six full ideals."),
            _second_order(("CERTIFIED","The complete bounded generic cones are {0} for indices 1-15; indices 16-21 each have a separately certified nonzero bounded point, while their full cones remain OPEN."),("OPEN","R_c has a secular inverse, so this scalar classification does not determine the complete smooth-secular cones."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("collision_scalar_separation","same_sign_collision_same_fibre_census","same_sign_collision_bounded_witnesses","ell2_two_abs_momentum_isolated_candidates","finite_generic_bounded_zero_block","standard","axial_current","polar_current","taub"),
            "This is an exact family ledger with 21 explicitly distinct circumference scopes, not a mode identification across backgrounds. It excludes exceptional/global inputs and leaves the six full same-sign cone geometries, all-orders integration, causal correction, residual observables, particles and quantum states fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_collision_same_fibre_census",
            _scope(theory="Weyl-Maxwell target", background="six distinct tuned compact magnetically supported Plebanski-Hacyan circumference fibres, candidates 16--21 retained separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="candidatewise complete generic ell=2 q-minus, p-extra and q-plus coefficients restricted to quadratic products within signed n=1 or within signed n=2", degree=2, parity="axial and polar", ell="input 2 x 2; outputs L=0,...,4", m="all Clebsch-Gordan-allowed values", k="same-fibre output n=2 or n=4 and the corresponding difference channel n=0; no cross-rho identification", omega="all nonzero-frequency sums and unequal-branch differences; equal-branch zero-frequency products belong to the separate finite-generic receiver", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Every source and target retains its candidate, signed momentum, branch, parity, angular degree and temporal channel."),
            ("CERTIFIED","The shell tests use the same-background action-derived q-minus, p-extra and q-plus branch dictionary."),
            ("NOT_APPLICABLE","The nonzero-frequency census is separate from the already certified zero-frequency stabilizer and circle-pressure receiver."),
            ("CERTIFIED","All 864 exact same-fibre target-shell defects are nonzero; the nonzero-Fourier homogeneous quotients are certified empty."),
            _second_order(("CERTIFIED","Every declared same-fibre nonzero-frequency source has a bounded inverse; only the candidate-specific cross-fibre resonance remains in the six joins."),("CERTIFIED","The same bounded inverses are smooth exponential-polynomial inverses on this finite carrier."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_collision_same_fibre_census","ell2_two_abs_momentum_isolated_candidates","finite_generic_bounded_zero_block","branch_dictionary"),
            "This closes only the same-fibre source matrix gate on candidates 16--21. Cross-fibre amplitudes, exceptional/global carriers, full cone geometry, all-orders integration and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_collision_bounded_witnesses",
            _scope(theory="Weyl-Maxwell target", background="six distinct tuned compact magnetically supported Plebanski-Hacyan circumference fibres, candidates 16--21 retained separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="one explicit finite real generic tangent on each candidate's signed n=(1,2) two-fibre carrier", degree=2, parity="axial m=0 except the certified real axial-polar mixed component on candidate 21", ell="input ell=2; candidate-specific resonant output L=1,3 or 4", m=0, k="candidatewise signed n=(1,2), never identified across rho", omega="the four occupied positive-frequency shells and their reality conjugates", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Each witness retains its exact candidate index, rho, support and isolated cross-fibre resonance row."),
            ("CERTIFIED","The positive Farkas occupations use the action-derived absolute-current forms; candidate 21 rescales its two real mixed-parity vectors by their exact positive norms."),
            ("CERTIFIED","The exact Farkas dependence kills mu_H, mu_Px and R_c, while axisymmetric support kills all three lifted rotation moment maps."),
            ("CERTIFIED","Candidates 17--19 omit a resonant factor, candidates 16 and 20 use the odd-L axisymmetric zero, and candidate 21 uses its certified real mixed-parity L=4 component; the 864-defect census removes every same-fibre hit."),
            _second_order(("CERTIFIED","Each of the six distinct same-sign collision cones contains the displayed nonzero bounded point."),("CERTIFIED","The same six bounded corrections are finite smooth quasiperiodic corrections; no larger smooth cone is classified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_collision_bounded_witnesses","same_sign_collision_same_fibre_census","collision_scalar_separation","ell2_two_abs_momentum_isolated_candidates","finite_generic_bounded_zero_block"),
            "This is a nonemptiness theorem on six separate bounded cones, not a classification of their full real geometry. Exceptional/global inputs, all-orders integration, causal correction, residual observables, particles and quantum states remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_scalar_extreme_rays",
            _scope(theory="Weyl-Maxwell target", background="arbitrary positive-rho same-sign n=(1,2) compact product fibre, with candidates 16--21 instantiated separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="six nonnegative absolute-current occupations for q-minus, p-extra and q-plus on n=1,2", degree=2, parity="parity-independent scalar occupation projection", ell=2, m="summed current occupation", k="signed n=(1,2)", omega="all six generic positive-frequency shells", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The universal moment-curve order retains both momentum fibres and all three branch labels without identifying circumference backgrounds."),
            ("CERTIFIED","The current sign sequence is (-,+,+,-,+,+); positive column rescaling reduces the scalar receiver to six ordered moment-curve columns."),
            ("CERTIFIED","Moment-curve circuit alternation gives exactly four scalar-null extreme rays: both q-minus nodes and one positive branch on each fibre."),
            ("OPEN","This scalar projection does not impose rotations or the candidate-specific bilinear resonance maps."),
            _second_order(("OPEN","The four scalar extreme rays are necessary occupation strata; their amplitude lifts are certified in a separate row."),("OPEN","The scalar cone alone does not classify smooth amplitude sums."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_scalar_extreme_rays","same_sign_scalar_candidate_audit","collision_scalar_separation","same_sign_collision_same_fibre_census"),
            "This is the complete scalar nonnegative occupation cone for any positive-rho same-sign fibre. It does not classify arbitrary amplitude sums, rotations, resonances, full bounded cones or higher lifecycles.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_extreme_ray_lifts",
            _scope(theory="Weyl-Maxwell target", background="six distinct collision candidates 16--21, retained separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="one axisymmetric real amplitude lift for each of four scalar extreme-ray supports per candidate", degree=2, parity="axial except the declared real mixed-parity L=4 components", ell="input ell=2; candidate-specific output L=1,3,4", m=0, k="signed n=(1,2)", omega="the four shells occupied by each extreme ray and their reality conjugates", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","All 24 rows retain their candidate, rho, scalar ray support, branch pair and output shell."),
            ("CERTIFIED","Each lift uses the action-derived absolute-current occupation on its universal scalar extreme ray."),
            ("CERTIFIED","Axisymmetric support kills all three rotations, and the scalar ray kills mu_H, mu_Px and R_c."),
            ("CERTIFIED","Ten lifts omit a resonant factor, ten use an odd-L Clebsch--Gordan zero, two use candidate 19's real regular-pencil component, and two use candidate 21's real mixed-parity component."),
            _second_order(("CERTIFIED","Every one of the 24 scalar extreme rays has a nonzero bounded finite-quasiperiodic amplitude lift."),("CERTIFIED","Each declared lift also has a finite smooth correction; arbitrary sums remain unclassified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_extreme_ray_lifts","same_sign_scalar_extreme_rays","same_sign_collision_bounded_witnesses","same_sign_collision_same_fibre_census"),
            "This is scalar-extreme-ray saturation, not a classification of arbitrary nonnegative sums: phase/parity cross terms can reactivate the bilinear resonance. Full cone geometry and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_scalar_cone_sections",
            _scope(theory="Weyl-Maxwell target", background="six distinct collision candidates 16--21, retained separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="one explicit axisymmetric amplitude section over every point of each complete four-ray scalar occupation cone", degree=2, parity="all-axial on odd-L candidates; fixed real mixed parity on candidates 19 and 21", ell="input ell=2; candidate-specific output L=1,3,4", m=0, k="signed n=(1,2)", omega="arbitrary nonnegative occupations on all six generic shells subject to H/Px/Rc=0", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The section retains every scalar-cone point on each of six distinct rho fibres; no cross-background identification is made."),
            ("CERTIFIED","Absolute-current normalization supplies independent nonnegative fibre scaling on the fixed real zero components."),
            ("CERTIFIED","Every section is axisymmetric and lies over the complete H/Px/Rc common-zero cone, so all six zero-frequency receivers vanish."),
            ("CERTIFIED","The odd-L all-axial section and the two real L4 mixed sections kill the cross-fibre resonance for arbitrary scalar-cone occupations; all same-fibre channels are removable."),
            _second_order(("CERTIFIED","The bounded cone projects surjectively onto the complete scalar occupation cone on every candidate 16--21."),("CERTIFIED","The declared section has finite smooth corrections; the full phase/parity fibres remain unclassified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_scalar_cone_sections","same_sign_extreme_ray_lifts","same_sign_scalar_extreme_rays","same_sign_collision_same_fibre_census"),
            "This is occupation-surjectivity, not a statement that every amplitude over a scalar-null occupation is bounded. The complete phase/parity fibres, full real components and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_phase_parity_fibre_product",
            _scope(theory="Weyl-Maxwell target", background="six distinct collision candidates 16--21, retained separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="complete generic ell=2 axial/polar positive-frequency amplitude carrier with conjugate reality completion", degree=2, parity="both axial and polar with arbitrary relative phases", ell="input ell=2; candidate-specific resonant output L=1,3,4", m="all m=-2,...,2", k="signed n=(1,2), never identified across rho", omega="all six generic positive-frequency shells and the single candidate-specific cross-fibre resonant channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Each formula retains its exact candidate, circumference, branch, parity, angular and temporal carrier; no background or mode identification is made."),
            ("CERTIFIED","The occupation map uses the action-derived absolute-current forms, and all phase/parity amplitudes remain explicit above it."),
            ("CERTIFIED","The scalar H/Px/Rc cone and all three lifted rotation moment maps occur as separate factors in every bounded-cone formula."),
            ("CERTIFIED","All six cross-fibre complex resonance varieties are decomposed; the same-fibre census removes every other nonzero-frequency condition."),
            _second_order(("CERTIFIED","For each candidate, Z_i^bounded = pi_i^{-1}(C_i) intersect mu_J^{-1}(0) intersect V(B_i) is necessary and sufficient."),("CERTIFIED","The bounded formula embeds in the separately certified smooth-secular moment-map cone."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_phase_parity_fibre_product","same_sign_scalar_cone_sections","same_sign_scalar_candidate_audit","same_sign_collision_same_fibre_census","finite_generic_bounded_zero_block","ell2_two_abs_momentum_cross_fibre_amplitude_system"),
            "This is a complete equational fibre-product description, not an irreducible real Hermitian component or singular-stratum decomposition. All-orders, causal, residual, observational and quantum promotions remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_resonance_face_fibres",
            _scope(theory="Weyl-Maxwell target", background="six distinct collision candidates 16--21, retained separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="complete complex positive-frequency phase/parity resonance fibre over every face of each same-sign scalar occupation cone", degree=2, parity="axial and polar", ell="input ell=2; candidate-specific output L=1,3,4", m="all m via the certified binary-form intertwiners", k="signed n=(1,2)", omega="candidate-specific isolated SUM channel on 16,18,19,21 and DIFFERENCE channel on 17,20", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Each face row retains its candidate, rho, resonant branch pair, target shell and all-m parity carrier; no circumference backgrounds are identified."),
            ("CERTIFIED","The scalar norm levels use the action-derived absolute-current occupations, but no quotient of their angular phase fibres is inferred."),
            ("CERTIFIED","The exact bounded fibre-product formula retains H/Px/Rc and all three lifted rotation moment maps; their real component decomposition remains open."),
            ("CERTIFIED","Optional-branch-zero faces are automatic. On active strata the complete complex component counts are 1,1,1,4,1,2 for candidates 16--21, with real nonempty sections."),
            _second_order(("CERTIFIED","Inside the exact necessary-and-sufficient bounded fibre-product formula, every scalar-cone face now has a complete complex resonance-component ledger; real components remain undecomposed."),("CERTIFIED","The same exact bounded solutions embed in the certified smooth-secular correction class; its real component decomposition is likewise open."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_resonance_face_fibres","same_sign_phase_parity_fibre_product","same_sign_scalar_cone_sections","ell2_two_abs_momentum_target_doublet_L3_zero_varieties","ell2_two_abs_momentum_scalar_L1_zero_varieties","ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties","ell2_two_abs_momentum_regular_pencil_L4_zero_varieties","ell2_two_abs_momentum_scalar_L4_zero_varieties"),
            "This is a complete complex resonance-face stratification inside the exact bounded fibre-product formula. It is not a real connected-component or singular-stratum decomposition and not a higher-lifecycle result.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_automatic_face_rotation_links",
            _scope(theory="Weyl-Maxwell target", background="five distinct collision candidates 17--21, retained separately; candidate 16 has no nonzero automatic face", boundaries="closed S1_L times S2 before final residual quotient", carrier="every nonzero fixed-occupation support stratum on the candidate-specific automatic two-ray resonance face", degree=2, parity="complete axial/polar node amplitude spaces with arbitrary phases", ell="input ell=2", m="all m=-2,...,2 under the diagonal lifted SO(3) action", k="signed n=(1,2), never identified across rho", omega="occupied generic positive-frequency nodes and conjugate reality completion", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Every row retains its exact automatic scalar-cone face and support stratum on one declared circumference background."),
            ("CERTIFIED","Fixed node norms and node-phase reduction give a compact projective product with nonzero signed action-derived Fubini--Study forms."),
            ("CERTIFIED","The diagonal lifted SO(3) moment map has a nonempty connected zero fibre on every declared fixed-occupation stratum."),
            ("CERTIFIED","The cross-fibre resonance vanishes identically because one full bilinear factor is zero on each automatic face."),
            _second_order(("CERTIFIED","Every nonzero fixed-occupation bounded link on the five automatic faces is nonempty and connected."),("CERTIFIED","These bounded links also lie in the smooth-secular cone; no active-stratum topology is inferred."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_automatic_face_rotation_links","same_sign_resonance_face_fibres","same_sign_phase_parity_fibre_product","same_sign_scalar_cone_sections","taub","standard","axial_current","polar_current"),
            "This uses compact Hamiltonian moment-map connectedness only on automatic faces, where the fixed-norm phase quotient is a smooth projective product. Active resonance varieties, gluing across occupation strata, singularities and all higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_axisymmetric_rotation_critical_locus",
            _scope(theory="Weyl-Maxwell target", background="six distinct collision candidates 16--21, retained separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="the certified all-m=0 amplitude section over every same-sign scalar-cone point", degree=2, parity="candidate-specific axial or fixed real mixed parity", ell=2, m=0, k="signed n=(1,2)", omega="all occupied generic shells in the scalar-cone section", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The rank theorem is uniform on the six separately scoped scalar-cone sections and uses only their common spin-two m=0 carrier."),
            ("CERTIFIED","The exact spin-two invariant angular form gives two independent transverse rotation covectors at every nonzero section point."),
            ("CERTIFIED","The lifted-rotation Jacobian has rank zero at the origin and exactly two at every nonzero section point because d(mu_J3)=0 there."),
            ("CERTIFIED","The underlying section remains inside the exact candidatewise scalar and resonance zero set; this row adds only the rotation critical-locus theorem."),
            _second_order(("CERTIFIED","Every declared section point is bounded, but every nonzero point is critical for the three-component rotation map and cannot seed a regular codimension-three chart."),("CERTIFIED","The same critical section lies in the smooth-secular class; no local component decomposition is inferred."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_axisymmetric_rotation_singularity","same_sign_resonance_face_fibres","same_sign_phase_parity_fibre_product","same_sign_scalar_cone_sections","taub"),
            "This is an exact Jacobian-rank theorem, not a quadratic-normal-form, local tangent-cone, connected-component, singular-stratum or higher-lifecycle classification.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_automatic_face_rotation_normal_form",
            _scope(theory="Weyl-Maxwell target", background="five distinct collision candidates 17--21, retained separately; candidate 16 has no nonzero automatic face", boundaries="closed S1_L times S2 before final residual quotient", carrier="current-eigenline-aligned angular slice and one exact full-amplitude arc through every axisymmetric point on every nonzero automatic-face support stratum", degree=2, parity="the occupied axial/polar current eigenlines selected by the certified section", ell=2, m="base m=0 with transverse m=+/-1,+/-2; exact arc uses m=0,+/-2", k="signed n=(1,2), never identified across rho", omega="occupied generic positive-frequency nodes with conjugate reality completion", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The theorem applies support-stratum by support-stratum on the five automatic faces and keeps candidate 16 NOT_APPLICABLE."),
            ("CERTIFIED","The action-derived spin-two angular form gives exact aligned-kernel inertia (4N-2,4N-2,2) for N occupied current eigenlines."),
            ("CERTIFIED","The missing mu_J3 equation is hyperbolic on the aligned angular slice, and every axisymmetric point lies on an exact fixed-norm nonaxisymmetric rotation-zero arc."),
            ("CERTIFIED","The absent resonant node remains zero along the exact arc, so the complete bilinear resonance remains automatic."),
            _second_order(("CERTIFIED","The exact nonaxisymmetric arc stays in the necessary-and-sufficient bounded fibre product on every declared automatic-face stratum."),("CERTIFIED","The same finite-amplitude arc lies in the smooth-secular cone; the full local singular stratification remains open."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_automatic_face_rotation_normal_form","same_sign_automatic_face_rotation_links","same_sign_axisymmetric_rotation_singularity","same_sign_resonance_face_fibres","same_sign_phase_parity_fibre_product","taub"),
            "This certifies the complete normal form only on the aligned angular slice plus one exact arc in the full amplitude link. Internal current-orthogonal directions, active resonance components, occupation-stratum gluing and all higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_automatic_face_full_internal_rotation_normal_form",
            _scope(theory="Weyl-Maxwell target", background="five distinct collision candidates 17--21, retained separately; candidate 16 is NOT_APPLICABLE", boundaries="closed S1_L times S2 before final residual quotient", carrier="complete axial/polar current-eigenline tangent on every ray and relative-interior fixed-occupation support stratum of each automatic face", degree=2, parity="all axial and polar q-primary and p-primary internal eigenlines", ell=2, m="all m=-2,...,2 around the axisymmetric base", k="candidatewise signed n=(1,-2) or (1,2), never identified across rho", omega="all occupied generic positive-frequency nodes with conjugate reality completion", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","All five automatic faces are kept candidatewise, with both rays and their relative interior listed separately."),
            ("CERTIFIED","The current multiplicities are two eigenlines on each q node and four on each p node; every current-orthogonal eigenline contributes inertia (4,4,2)."),
            ("CERTIFIED","For N occupied nodes and M total current eigenlines, the complete fixed-occupation rotation-kernel inertia is (4M-2,4M-2,2M-2N+2)."),
            ("CERTIFIED","The theorem remains on automatic faces, where the complete bilinear resonance factor vanishes identically."),
            _second_order(("CERTIFIED","All fifteen realized ray/interior fixed-occupation strata have complete internal rotation normal forms; their inertias range from (30,30,10) to (54,54,20)."),("CERTIFIED","The same obstruction-zero strata lie in the smooth-secular class; occupation gluing and active components remain open."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_automatic_face_full_internal_rotation_normal_form","same_sign_automatic_face_rotation_normal_form","same_sign_automatic_face_rotation_links","axial_current","polar_current"),
            "This closes the internal normal form only at fixed occupations on automatic faces. It does not glue occupation strata, classify active resonance components, perform residual descent, or promote all-orders, causal, observational or quantum claims.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_automatic_face_full_rotation_normal_form",
            _scope(theory="Weyl-Maxwell target", background="five distinct collision candidates 17--21, retained separately; candidate 16 has no nonzero automatic face", boundaries="closed S1_L times S2 before final residual quotient", carrier="complete tangent at each axisymmetric fixed-node-norm automatic-face point, including all axial/polar internal directions and all spin-two magnetic coefficients", degree=2, parity="complete axial and polar q-primary and p-primary internal spaces", ell=2, m="all m=-2,...,2; both unquotiented and node-phase-quotiented forms recorded", k="signed n=(1,2), never identified across rho", omega="occupied generic positive-frequency nodes with conjugate reality completion", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Every ray interior and two-ray relative interior is retained separately on each of the five automatic faces; candidate 16 is NOT_APPLICABLE."),
            ("CERTIFIED","For N occupied nodes of total internal complex dimension D, the full fixed-norm rotation Hessian has unquotiented inertia (4D-2,4D-2,2D-N+2) and node-phase-quotiented inertia (4D-2,4D-2,2D-2N+2)."),
            ("CERTIFIED","All internal polarization directions are included. They add matched hyperbolic blocks and explicit m=0 radical directions; the transverse part is indefinite on every support stratum."),
            ("CERTIFIED","The automatic bilinear resonance remains identically zero on every declared support stratum."),
            _second_order(("CERTIFIED","Every declared fixed-norm link lies in the necessary-and-sufficient bounded fibre product; its complete rotation Hessian at the axisymmetric point is classified."),("CERTIFIED","The same rotation-zero links lie in the smooth-secular cone; their radical is not yet resolved into nonlinear local components."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_automatic_face_full_rotation_normal_form","same_sign_automatic_face_full_internal_rotation_normal_form","same_sign_automatic_face_rotation_normal_form","same_sign_automatic_face_rotation_links","same_sign_resonance_face_fibres","axial_operator","polar_operator","axial_current","polar_current"),
            "This is the complete quadratic rotation normal form only at fixed node norms on automatic faces. The nonlinear radical resolution, gluing of occupation strata, active resonance components and all higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate16_active_restricted_current",
            _scope(theory="Weyl-Maxwell target", background="candidate 16 only at rho=17*(79+51*sqrt(3))/132", boundaries="closed S1_L times S2 before final residual quotient", carrier="the irreducible q-minus(n=1) x q-minus(n=2) active resonance variety after both nonzero node norms are fixed and both node phases are quotiented", degree=2, parity="complete axial and polar q-minus current spaces", ell="input 2 x 2; output L=3", m="all m=-2,...,2 on both input nodes", k="signed n=(1,2) on candidate 16 only", omega="positive-frequency q-minus plus q-minus SUM collision into p-extra", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The affine resonance variety is one irreducible complex dimension-12 target-doublet L3 cone; its two-node projectivization is a complex tenfold in CP^9 x CP^9."),
            ("CERTIFIED","Both complete axial/polar input blocks have negative q-minus current, so the restricted form is negative Kahler and nondegenerate on every complex smooth stratum; the generic real symplectic rank is 20."),
            ("OPEN","The projective variety is singular. Its lifted-rotation zero-fibre topology is not inferred from the smooth-orbifold connected-fibre theorem."),
            ("CERTIFIED","The complete candidate-16 active cross-fibre resonance ideal is the imported irreducible target-doublet L3 variety."),
            _second_order(("CERTIFIED","The separately certified axisymmetric section supplies nonzero bounded points, but the complete singular rotation-zero intersection is not classified."),("CERTIFIED","Those finite points also lie in the smooth-secular class; no all-orders claim follows."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate16_active_restricted_current","same_sign_resonance_face_fibres","ell2_two_abs_momentum_target_doublet_L3_zero_varieties","same_sign_scalar_extreme_rays","axial_current","polar_current"),
            "This closes only the candidate-16 stratumwise restricted-current gate. Singular Hamiltonian topology, candidates 17--21, final residual descent, all-orders integration and causal, observational or quantum claims remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate16_singular_rotation_zero_fibre",
            _scope(theory="Weyl-Maxwell target", background="candidate 16 only at rho=17*(79+51*sqrt(3))/132", boundaries="closed S1_L times S2 before final residual quotient", carrier="the complete candidate-16 fixed-positive-node-norm active link, including both singular endpoints, after the two node-phase quotients", degree=2, parity="complete axial and polar q-minus current spaces", ell="input 2 x 2; output L=3", m="all m=-2,...,2 through the spin-two incidence resolution", k="candidatewise signed n=(1,-2) or (1,2), never identified across rho", omega="positive-frequency q-minus plus q-minus SUM collision into p-extra", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidate 16, its two q-minus nodes, rank-one factors, fixed occupations and lifted diagonal SO(3) action retain their declared same-background labels."),
            ("CERTIFIED","The current stays negative Kahler on every smooth stratum; the singular locus consists of two endpoint CP^4 strata and is not misreported as a current radical."),
            ("CERTIFIED","The compact connected incidence resolution has a nonempty connected lifted-SO(3) moment-map zero fibre; connected resolution fibres make the complete singular target zero fibre connected."),
            ("CERTIFIED","Each rank-one factor is singular only at its vertex. The product resolution has complex dimension 12 and its positive-norm node-phase quotient is a compact connected Kahler tenfold."),
            _second_order(("CERTIFIED","The imported all-m=0 point proves the fixed-occupation rotation-zero fibre nonempty, and the exact candidate-16 bounded fibre-product theorem supplies its second-order membership."),("CERTIFIED","The same finite carrier lies in the smooth-secular class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate16_singular_rotation_zero_fibre","same_sign_candidate16_active_restricted_current","same_sign_collision_bounded_witnesses","ell2_two_abs_momentum_target_doublet_L3_zero_varieties","taub"),
            "This classifies candidate 16 at each fixed positive active occupation after node-phase quotient. It does not declare a global orbifold, glue occupation strata, perform final residual descent, prove all-orders integration, or supply causal, observational or quantum transport.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate16_occupation_gluing",
            _scope(theory="Weyl-Maxwell target", background="candidate 16 only at rho=17*(79+51*sqrt(3))/132", boundaries="closed S1_L times S2 before final residual quotient", carrier="the complete candidate-16 active lifted-rotation zero link over every nonzero scalar occupation, after total-occupation normalization and both node-phase quotients", degree=2, parity="complete axial and polar q-minus current spaces", ell="input 2 x 2; output L=3", m="all m=-2,...,2 through the fixed-occupation incidence resolutions", k="candidatewise signed n=(1,-2) or (1,2), never identified across rho", omega="positive-frequency q-minus plus q-minus SUM collision into p-extra", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Only candidate 16 is glued over its own normalized scalar cone; the origin and all other circumference backgrounds remain separate."),
            ("CERTIFIED","The negative Kahler current and incidence resolution are unchanged on every positive occupation fibre, including the two singular endpoint strata."),
            ("CERTIFIED","The normalized scalar base is a compact connected two-polytope. The rotation-zero projection is proper and surjective with connected fibres, hence the complete normalized link is connected."),
            ("CERTIFIED","Four positive scalar rays generate a three-dimensional cone; total-occupation normalization gives the exact compact base and both active q-minus norms stay strictly positive."),
            _second_order(("CERTIFIED","The exact bounded section supplies surjectivity over the complete nonzero normalized scalar cone; fixed-occupation connectedness supplies every fibre."),("CERTIFIED","The same finite normalized link lies in the smooth-secular class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate16_occupation_gluing","same_sign_candidate16_singular_rotation_zero_fibre","same_sign_candidate16_active_restricted_current","same_sign_scalar_extreme_rays","same_sign_phase_parity_fibre_product"),
            "This glues all nonzero candidate-16 scalar occupations after total-occupation normalization. The cone origin, other candidate backgrounds, final residual descent, all-orders integration and causal, observational or quantum transport remain outside the theorem.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_active_linear_sheet_rotation_links",
            _scope(theory="Weyl-Maxwell target", background="candidates 19 and 21 only, retained as distinct compact Plebanski--Hacyan collision backgrounds", boundaries="closed S1_L times S2 before final residual quotient", carrier="the four real pencil-eigenline sheets of candidate 19 and two real parity-proportional sheets of candidate 21 at every fixed active occupation and spectator support stratum", degree=2, parity="complete axial/polar graph or eigenline subspaces on resonant nodes and complete spaces on spectators", ell="input 2 x 2; output L=4", m="all m=-2,...,2", k="signed n=(1,2), candidatewise and never identified across rho", omega="candidate-specific positive-frequency SUM collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The four candidate-19 and two candidate-21 real active sheets remain distinct; no residual or cross-background identification is made."),
            ("CERTIFIED","Every active core is a positive C^5 node subspace orthogonal to a negative C^5 node subspace, so the restricted Hermitian current has inertia (5,5,0); definite spectator blocks preserve nondegeneracy."),
            ("CERTIFIED","At every fixed occupation, each sheet's CP^4 x CP^4 core and its spectator projective factors have a nonempty connected lifted-rotation zero fibre."),
            ("CERTIFIED","The six declared linear sheets are complete active components of their candidate-specific cross-fibre resonance varieties."),
            _second_order(("CERTIFIED","Each of the six sheets has one connected fixed-occupation bounded rotation-zero link; different sheets and occupation strata are not glued."),("CERTIFIED","The same finite links lie in the smooth-secular cone without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_active_linear_sheet_rotation_links","same_sign_resonance_face_fibres","ell2_two_abs_momentum_regular_pencil_L4_zero_varieties","ell2_two_abs_momentum_scalar_L4_zero_varieties","same_sign_phase_parity_fibre_product","taub","axial_current","polar_current"),
            "This covers only the six smooth real linear active sheets on candidates 19 and 21. Candidates 16--18 and 20, sheet identification, occupation gluing, final residual descent, all-orders integration and causal, observational or quantum claims remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_axisymmetric_restricted_current",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 only, retained as distinct compact Plebanski--Hacyan collision backgrounds", boundaries="closed S1_L times S2 before final residual quotient", carrier="the all-axial all-m=0 section over every nonzero active scalar-cone point and the complete axial/polar Zariski tangent to the third-transvectant resonance variety", degree=2, parity="both linearized parity channels around the all-axial base", ell="input 2 x 2; output L=1", m="base m=0 with complete all-m Zariski tangent", k="signed n=(1,2), candidatewise and never identified across rho", omega="positive-frequency q-minus/q-plus DIFFERENCE collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Both irreducible active varieties are products of two third-transvectant kernels; their axisymmetric sections lie on the square-quartic rank-drop stratum."),
            ("CERTIFIED","Exact raywise occupation inequalities give affine Zariski-tangent current inertia (6,10,0) and projective inertia (5,9,0), hence projective real symplectic rank 28 throughout both active scalar cones."),
            ("OPEN","The section points are algebraically singular: affine Zariski-tangent dimension 16 exceeds variety dimension 14, so no smooth-locus or connected rotation-fibre theorem is inferred."),
            ("CERTIFIED","The complete linearized third-transvectant derivative has rank four at the all-m=0 section and its two-complex-dimensional tangent excess is explicit."),
            _second_order(("CERTIFIED","The separately certified axisymmetric points are nonzero bounded points and their Zariski-tangent currents are nondegenerate; the full active rotation-zero variety remains open."),("CERTIFIED","Those finite points lie in the smooth-secular class without a smooth-locus or all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_axisymmetric_restricted_current","same_sign_resonance_face_fibres","ell2_two_abs_momentum_scalar_L1_zero_varieties","same_sign_scalar_extreme_rays","standard"),
            "This is a complete active-scalar-cone theorem only on the candidate-17/20 axisymmetric sections and their Zariski tangents. It does not make the singular points smooth, classify the full active smooth locus or rotation-zero topology, treat candidate 18, or promote higher lifecycles.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_l1_active_restricted_current_degeneracy",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 only, retained as distinct compact Plebanski--Hacyan collision backgrounds", boundaries="closed S1_L times S2 before final residual quotient", carrier="one exact smooth nonaxisymmetric point in each complete K_T3_plus x K_T3_minus active resonance variety, lifted to an exact scalar-cone occupation", degree=2, parity="both current-orthogonal real parity eigenchannels", ell="input 2 x 2; output L=1", m="real reflection-symmetric m=0,+/-2 base with m=+/-1 current radical; all rotation moments vanish", k="signed n=(1,2), candidatewise and never identified across rho", omega="candidate-specific q-minus/q-plus DIFFERENCE collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"OBSTRUCTED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The candidate-17 and candidate-20 backgrounds, branch/momentum nodes, exact scalar-ray mixtures and smooth transvectant carrier remain separate."),
            ("OBSTRUCTED","At positive/negative occupation ratio 13/192, the smooth fixed-norm projective tangent has an exact nonzero current radical; neither complete active variety is globally symplectic."),
            ("CERTIFIED","The smooth witness has zero J1,J2,J3 moments individually, and the exact scalar-cone lift kills H and P_x; all five stabilizer moment maps vanish."),
            ("CERTIFIED","Both third-transvectant equations vanish in both current-orthogonal parity eigenchannels; the Jacobian has full rank three per channel."),
            _second_order(("CERTIFIED","Positive ray mixtures R3+sR1 on candidate 17 and R2+sR1 on candidate 20 place the smooth radical witness inside the exact necessary-and-sufficient bounded fibre product."),("CERTIFIED","The same finite witnesses lie in the smooth-secular cone; the full presymplectic degeneracy divisor remains open."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_L1_active_restricted_current_degeneracy","same_sign_candidate17_20_axisymmetric_restricted_current","same_sign_resonance_face_fibres","ell2_two_abs_momentum_scalar_L1_zero_varieties","same_sign_scalar_extreme_rays","same_sign_phase_parity_fibre_product","standard","axial_current","polar_current","taub"),
            "This is an exact smooth current-degeneracy witness on candidates 17 and 20, not a complete degeneracy-divisor or connected-component classification. Candidate 18, occupation gluing, final residual descent, all-orders integration and causal, observational or quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate18_active_restricted_current_degeneracy",
            _scope(theory="Weyl-Maxwell target", background="candidate 18 only at its certified compact Plebanski--Hacyan circumference", boundaries="closed S1_L times S2 before final residual quotient", carrier="the complete p-extra(n=1) x q-minus(n=2) active L=3 resonance variety at the exact ratio-one scalar-cone occupation, including p-extra kernel spectators", degree=2, parity="both transformed rank-one parity channels and two exact internal current eigenlines", ell="input 2 x 2; output L=3", m="m=0 base carriers with the full four-complex-dimensional transverse spin-two radical; m=0 spectators", k="signed n=(1,2) on candidate 18 only", omega="positive-frequency p-extra plus q-minus SUM collision into q-plus", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"OBSTRUCTED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidate 18, its p-extra/q-minus branch nodes, both transformed parity channels, exact current eigenlines and scalar-ray lift retain their declared carrier labels."),
            ("OBSTRUCTED","Each of the two smooth eigenline families has a four-complex-dimensional fixed-norm projective current radical; the complete active variety is not globally symplectic."),
            ("CERTIFIED","The exact R3+s18 R1 scalar lift kills H and P_x, while m=0 resonant carriers and spectators kill J1,J2,J3; all five stabilizer moment maps vanish."),
            ("CERTIFIED","Both first-transvectant rank-one factors are nonzero proportional pairs and smooth; the complete affine active variety has complex dimension 22 including its ten-dimensional spectator space."),
            _second_order(("CERTIFIED","The positive exact mixture R3+s18 R1 gives equal p-extra(n=1) and q-minus(n=2) absolute-current occupation and lies in the necessary-and-sufficient bounded fibre product."),("CERTIFIED","The same finite witnesses lie in the smooth-secular cone; the complete presymplectic degeneracy divisor remains open."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate18_active_restricted_current_degeneracy","same_sign_resonance_face_fibres","ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties","same_sign_scalar_extreme_rays","same_sign_phase_parity_fibre_product","standard","axial_current","polar_current","taub"),
            "This is an exact smooth bounded current-degeneracy-family theorem on candidate 18, not a complete degeneracy-divisor, presymplectic-quotient, connected-component or occupation-gluing classification. Final residual descent, all-orders integration and causal, observational or quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_active_presymplectic_divisors",
            _scope(theory="Weyl-Maxwell target", background="three distinct collision candidates 17, 18 and 20, retained separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="the complete smooth active third-transvectant products on candidates 17/20 and rank-one-quartic product with current-orthogonal spectators on candidate 18", degree=2, parity="both exact factorized parity channels", ell="input 2 x 2; output L=1 on candidates 17/20 and L=3 on candidate 18", m="all m=-2,...,2", k="candidate-specific allowed compact momenta, never identified across rho", omega="candidate-specific certified SUM or DIFFERENCE collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The third-transvectant and rank-one carriers remain candidate-labelled; the theorem uses no cross-background mode identification."),
            ("CERTIFIED","On every smooth chart the restricted-current radical is ker(J H^{-1} J^dagger); det(J H^{-1} J^dagger)=0 is the complete degeneracy divisor and its determinantal ideals give every corank stratum."),
            ("CERTIFIED","Quotienting each smooth tangent by that exact radical gives a finite-dimensional nondegenerate Hermitian current. This is a tangent-space quotient, not a global Hausdorff quotient or residual reduction."),
            ("CERTIFIED","The imported active resonance ideals supply the full-row-rank Jacobians on their smooth loci. At the candidate-17/20 bounded witness the conormal nullity is one, while a second exact smooth point has det(K)=8293671904 and proves the divisor proper; candidate 18 has two aligned conormal-nullity-four branches."),
            _second_order(("CERTIFIED","The previously certified smooth radical witnesses remain inside the exact bounded fibre product; the divisor theorem classifies their tangent-current corank but does not glue occupations."),("CERTIFIED","The same finite witnesses lie in the smooth-secular class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_active_presymplectic_divisors","same_sign_L1_active_restricted_current_degeneracy","same_sign_candidate18_active_restricted_current_degeneracy","ell2_two_abs_momentum_scalar_L1_zero_varieties","ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties","axial_current","polar_current"),
            "This classifies smooth tangent-space degeneracy divisors and linear presymplectic quotients only. Singular-locus reduction, constant-rank/global quotient topology, occupation gluing, final residual descent, all-orders integration and causal, observational or quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_third_transvectant_singular_locus",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately", boundaries="closed S1_L times S2 before node-phase, lifted-rotation or final residual quotient", carrier="both parity factors of the complete complex third-transvectant resonance variety", degree=2, parity="two exact factorized parity eigenchannels", ell="input 2 x 2; output L=1", m="all m=-2,...,2 in the binary-quartic carrier", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific difference collision into L=1 extra output", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"OPEN","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The complete complex singular carriers are classified candidatewise and paritywise; candidates 17 and 20 remain distinct backgrounds."),
            ("OPEN","The theorem does not restrict the Lee-Wald form to the real fixed-occupation singular strata or construct their presymplectic quotient."),
            ("OPEN","Node phases and the lifted SO(3) moment-map zero condition have not yet been imposed on these singular components."),
            ("CERTIFIED","For one factor rank J<3 exactly on (f,g)=(a v(lambda),b v(lambda)); its projectivization is P2 x P1. The two-parity product has exactly two eleven-dimensional singular components meeting in dimension eight."),
            _second_order(("OPEN","The complex singular carrier has not yet been intersected with the real bounded fibre product."),("OPEN","No singular-stratum secular extension theorem is inferred."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_third_transvectant_singular_locus","ell2_two_abs_momentum_scalar_L1_zero_varieties","same_sign_active_presymplectic_divisors"),
            "This is a complete complex-algebraic singular-locus theorem before fixed norms and group reduction. Real Hermitian intersections, node-phase and lifted-rotation quotients, global connectedness, occupation gluing, final residual descent and all later physical maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate18_complex_singular_resolution",
            _scope(theory="Weyl-Maxwell target", background="candidate 18 only", boundaries="closed S1_L times S2 before node-phase, lifted-rotation or final residual quotient", carrier="ten positive current-orthogonal spectators times two rank-at-most-one 5x2 parity factors", degree=2, parity="both exact factorized parity channels", ell="input 2 x 2; output L=3", m="all m=-2,...,2; all ten spectators retained", k="candidate-specific allowed compact momenta, never identified across rho", omega="candidate-specific certified SUM collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"OPEN","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Only candidate 18 is classified; its ten spectators and two parity factors remain explicit and are not identified with another background."),
            ("OPEN","The complex resolution has not yet been equipped with the real fixed-occupation Lee-Wald restriction or its radical quotient."),
            ("OPEN","Node phases and the lifted SO(3) moment-map zero condition have not yet been imposed on the resolved carrier."),
            ("CERTIFIED","The singular locus has exactly two dimension-16 components, where one rank-one factor is the vertex, meeting in the dimension-10 spectator space. The smooth connected incidence resolution has dimension 22 and connected fibres."),
            _second_order(("OPEN","The resolved complex carrier has not yet been intersected with the real bounded fibre product."),("OPEN","No singular-stratum secular extension theorem is inferred."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate18_complex_singular_resolution","same_sign_active_presymplectic_divisors","same_sign_candidate18_active_restricted_current_degeneracy"),
            "This classifies and resolves the complete candidate-18 complex carrier only. Real Hermitian fixed-occupation strata, current degeneracy on the resolution, node-phase and lifted-rotation quotients, connected zero fibres, occupation gluing and later physical maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_active_singular_rotation_zero_sections",
            _scope(theory="Weyl-Maxwell target", background="candidates 17, 18 and 20 separately", boundaries="closed S1_L times S2 before node-phase, lifted-rotation or final residual quotient", carrier="real positive-frequency fixed-active-occupation links after conjugate reality completion", degree=2, parity="one declared parity factor carries the section and the other is at its singular vertex", ell="input 2 x 2; output L=1 on candidates 17/20 and L=3 on candidate 18", m="only m=0 is nonzero in the explicit section", k="candidate-specific allowed compact momenta, never identified across candidates", omega="candidate-specific certified collision frequency", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"OPEN","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The explicit sections retain candidate, parity, node and momentum labels; no carrier is identified across backgrounds."),
            ("OPEN","The sections lie on the real fixed-occupation singular carrier, but the resolved Lee-Wald current and singular presymplectic quotient remain unclassified."),
            ("CERTIFIED","For every N_minus>0 and N_plus>0, an axisymmetric singular point has all three lifted rotational moment maps zero. Positive total node norms keep both node-phase actions free."),
            ("CERTIFIED","Candidates 17/20 use the common-square third-transvectant singularity; candidate 18 uses one rank-one factor and the vertex of the other, with all ten spectators set explicitly to zero."),
            _second_order(("CERTIFIED","The exact section lies in the already certified bounded real fibre product at every positive active occupation; this is an existence witness, not a component classification."),("CERTIFIED","The finite section also lies in the smooth-secular correction class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_active_singular_rotation_zero_sections","same_sign_third_transvectant_singular_locus","same_sign_candidate18_complex_singular_resolution","same_sign_active_phase_reduced_presymplectic_divisors","same_sign_collision_bounded_witnesses"),
            "This proves unavoidable singular rotation-zero points at every positive active occupation. It does not classify the complete real singular components, their node-phase or lifted-rotation quotient, connectedness, occupation gluing, final residual descent or later physical maps.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate18_singular_component_separation",
            _scope(theory="Weyl-Maxwell target", background="candidate 18 only", boundaries="closed S1_L times S2 before final residual quotient", carrier="the candidate-18 singular locus on every fixed level with strictly positive negative-current active-node occupation", degree=2, parity="both labelled factorized parity channels, not exchanged by the connected physical group", ell="input 2 x 2; output L=3", m="all m=-2,...,2; all ten spectators retained", k="candidate-specific allowed compact momenta, never identified across rho", omega="candidate-specific certified SUM collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"OPEN","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Only candidate 18 is covered. The two singular components retain their parity-factor labels and are not exchanged by node phases or lifted SO(3)."),
            ("OPEN","The Lee-Wald current on each resolved singular component and any smooth bridge between the components remain unclassified."),
            ("CERTIFIED","Both singular components contain rotation-zero points. At N_minus>0 their intersection is excluded, and the connected node-phase and lifted-rotation actions preserve each component."),
            ("CERTIFIED","The singular fixed-positive-occupation locus is the disjoint union of two nonempty clopen invariant subsets; its rotation-zero quotient therefore has at least two components."),
            _second_order(("CERTIFIED","The two explicit singular rotation-zero sections lie in the bounded real fibre product; no full-fibre disconnection is inferred."),("CERTIFIED","The same finite sections lie in the smooth-secular correction class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate18_singular_component_separation","same_sign_active_singular_rotation_zero_sections","same_sign_candidate18_complex_singular_resolution","same_sign_active_phase_reduced_presymplectic_divisors"),
            "This proves a two-component lower bound for the candidate-18 singular rotation-zero quotient only. It does not prove either component connected or the full smooth-plus-singular zero fibre disconnected, and it does not glue occupations or perform later physical descent.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate18_singular_smooth_bridge",
            _scope(theory="Weyl-Maxwell target", background="candidate 18 only", boundaries="closed S1_L times S2 before final residual quotient", carrier="an explicit central-m axisymmetric path in the complete fixed-positive-occupation resonance variety", degree=2, parity="both exact factorized parity channels", ell="input 2 x 2; output L=3", m="only m=0 is occupied along the bridge", k="candidate-specific allowed compact momenta, never identified across rho", omega="candidate-specific certified SUM collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Only candidate 18 is covered; the path retains the two labelled parity factors and does not identify another background."),
            ("CERTIFIED","The bridge lies in the complete fixed-occupation carrier, is complex-smooth in its interior, and keeps both node-phase actions free."),
            ("CERTIFIED","All three lifted rotational moment maps vanish along the path because only the central m=0 coefficient is occupied."),
            ("CERTIFIED","At every positive occupation pair, one endpoint lies in each singular component and the open path lies in the smooth rank-one-by-rank-one carrier."),
            _second_order(("CERTIFIED","The explicit path stays inside the exact bounded real fibre product at fixed occupations."),("CERTIFIED","The same finite path lies in the smooth-secular correction class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate18_singular_smooth_bridge","same_sign_candidate18_singular_component_separation","same_sign_active_phase_reduced_presymplectic_divisors","same_sign_candidate18_complex_singular_resolution"),
            "This joins one certified point in each candidate-18 singular component through the smooth rotation-zero carrier at every positive occupation. It does not prove every zero-fibre component meets this bridge, global connectedness, occupation gluing or later physical descent.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_singular_component_incidence",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately", boundaries="closed S1_L times S2 before final residual quotient", carrier="the complete singular locus of both third-transvectant parity factors on every positive fixed-active-occupation level", degree=2, parity="both labelled factorized parity channels", ell="input 2 x 2; output L=1", m="all m=-2,...,2; explicit intersection witness uses m=0", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"OPEN","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidates 17 and 20 remain distinct; the theorem retains both labelled parity singular components on each background."),
            ("OPEN","The Lee-Wald current and connectedness inside each complete real singular component remain unclassified."),
            ("CERTIFIED","At every positive occupation, the two singular-component images meet on an explicit axisymmetric rotation-zero orbit with both node-phase actions free."),
            ("CERTIFIED","The complex components meet in S_plus x S_minus of dimension eight. Unlike candidate 18, positive occupations do not remove this intersection."),
            _second_order(("CERTIFIED","The exact intersection witness lies in the bounded real fibre product at every positive occupation."),("CERTIFIED","The same finite witness lies in the smooth-secular correction class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_singular_component_incidence","same_sign_third_transvectant_singular_locus","same_sign_active_singular_rotation_zero_sections","same_sign_active_phase_reduced_presymplectic_divisors"),
            "This proves physical incidence of the two algebraic singular-component images, so their labels give no quotient-separation lower bound. It does not prove either component or the complete singular rotation-zero quotient connected, glue occupations or perform later physical descent.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_double_singular_rotation_zero_fibre",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately", boundaries="closed S1_L times S2 after both common node-phase quotients and before final residual quotient", carrier="the complete double-singular intersection S_plus x S_minus at every fixed positive active-occupation pair", degree=2, parity="two exact factorized parity eigenchannels", ell="input 2 x 2; output L=1", m="all m=-2,...,2 in the binary-quartic incidence carrier", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidates 17 and 20 remain separate. The theorem covers the common double-singular hub on each background and does not identify either larger singular component with the other."),
            ("CERTIFIED","The fixed-norm phase-reduced incidence resolution is a compact connected Kähler manifold of complex dimension six, equivariant for the lifted diagonal SO(3), with connected fibres onto the target hub."),
            ("CERTIFIED","Kirwan connectedness makes the resolved lifted-rotation moment-map zero fibre connected; its continuous image is the complete connected target-hub zero fibre. An axisymmetric positive-occupation witness proves nonemptiness."),
            ("CERTIFIED","The affine hub S_plus x S_minus has complex dimension eight and is resolved over P2_plus x P2_minus by the product of Tot(O(-2) direct_sum O(-2)) incidence resolutions."),
            _second_order(("CERTIFIED","The complete double-singular fixed-occupation hub has a connected bounded rotation-zero fibre after both node phases."),("CERTIFIED","The same finite-dimensional hub belongs to the smooth exponential-polynomial correction class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_double_singular_rotation_zero_fibre","same_sign_candidate17_20_singular_component_incidence","same_sign_third_transvectant_singular_locus","same_sign_active_singular_rotation_zero_sections","stabilizer"),
            "This proves connectedness only for the complete double-singular intersection hub at each fixed positive occupation. It does not prove either larger singular component or their full union connected, glue occupations, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_common_square_rotation_quotient",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately", boundaries="closed S1_L times S2 after both free active-node phases and before final residual quotient", carrier="one declared parity factor with both active nodes proportional to one nonzero square quartic and the other parity factor at zero", degree=2, parity="one labelled factorized parity channel occupied", ell="input 2 x 2; output L=1", m="all m=-2,...,2 through the binary-quadratic Cartan square", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision with the exact frequency-weighted rotation coefficient", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidates 17 and 20 remain separate, and the occupied parity factor is declared rather than identified with the other factor."),
            ("CERTIFIED","The action-derived rotation coefficient is delta=omega_plus*N_plus-omega_minus*N_minus. Candidate 17 has delta<0 on its complete active cone; candidate 20 changes sign between R2 and R4."),
            ("CERTIFIED","For delta nonzero the Cartan-square zero set is phase-real RP2 and its lifted-SO(3) quotient is one point. On candidate 20's exact delta=0 divisor the entire CP2 survives and its quotient is a closed interval."),
            ("CERTIFIED","The common-square map is the equivariant binary Cartan square. Its symmetric-tracefree commutator identity gives the exact moment-map zero criterion."),
            _second_order(("CERTIFIED","The one-parity common-square carrier lies in the exact bounded tangent cone; candidate 20 bifurcates between a point quotient off balance and an interval quotient on balance."),("CERTIFIED","The same finite carrier belongs to the smooth exponential-polynomial correction class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_common_square_rotation_quotient","same_sign_candidate17_20_double_singular_rotation_zero_fibre","same_sign_candidate17_20_axisymmetric_restricted_current","same_sign_scalar_extreme_rays","taub"),
            "This classifies only the one-parity common-square carrier at fixed occupations. It corrects the tempting but false inference that the unweighted occupation gap forbids rotational balance. The complete two-parity singular union, occupation gluing and every later physical descent remain open.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_singular_radial_contraction",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately; the complete-union theorem is candidate 20 on its exact active balance divisor", boundaries="closed S1_L times S2 after both free active-node phases and before lifted-rotation or final residual quotient", carrier="the complete singular union (S_plus x K_minus) union (K_plus x S_minus) at fixed positive active occupations, including the square-factor vertex strata", degree=2, parity="both labelled factorized parity channels", ell="input 2 x 2; output L=1", m="all m=-2,...,2 through the common-square and third-transvectant kernel factors", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision with exact frequency-weighted balance coefficient", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidates 17 and 20 remain distinct. The complete singular-union conclusion applies only to candidate 20 on delta=omega_plus*N_plus-omega_minus*N_minus=0; off-balance conclusions are restricted to the phase-real common-square sublocus."),
            ("CERTIFIED","Scaling the arbitrary kernel factor by t and transferring the released occupations into one common-square direction preserves both node norms and gives the exact residual mu_rotation(t)=(1-t^2)*delta*mu_square."),
            ("CERTIFIED","On candidate 20's exact balance divisor every rotation-zero point of either complete singular component, including a receiving square-factor vertex, contracts continuously to the connected double-singular hub."),
            ("CERTIFIED","The third-transvectant resonance remains zero under the radial kernel scaling and common-square transfer. At t=0 the path lies in S_plus x S_minus."),
            _second_order(("CERTIFIED","On the candidate-20 balance divisor the complete fixed-occupation singular-union rotation-zero fibre is connected through the certified radial paths and connected hub; off balance only the phase-real radial subloci are certified."),("CERTIFIED","The same finite-dimensional radial paths lie in the smooth exponential-polynomial correction class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_singular_radial_contraction","same_sign_candidate17_20_common_square_rotation_quotient","same_sign_candidate17_20_double_singular_rotation_zero_fibre","same_sign_third_transvectant_singular_locus","taub"),
            "The exact off-balance residual obstructs this canonical radial contraction when the common-square moment is nonzero; it is not a nonradial no-go. Candidate 17 and candidate 20 off balance therefore retain OPEN complete-singular connectedness. Occupation gluing, final residual descent, and causal, observational or quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_moving_square_contraction",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately; balance, sign-compatible and complementary ansatz-obstruction strata are retained separately", boundaries="closed S1_L times S2 after both free active-node phases and before lifted-rotation or final residual quotient", carrier="both complete singular components under uniform scaling of the arbitrary K factor, exact occupation transfer and arbitrary continuous motion of the receiving common-square direction", degree=2, parity="both labelled factorized parity channels", ell="input 2 x 2; output L=1", m="all m=-2,...,2 through the normalized Cartan-square moment ball and third-transvectant kernel", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision with alpha=omega_plus*A_plus-omega_minus*A_minus and delta=omega_plus*N_plus-omega_minus*N_minus", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidates 17 and 20 remain distinct. Candidate 20's delta=0 theorem is retained; off balance the repaired positive statement is alpha*delta>0 or alpha=0, together with phase-real directions and square vertices."),
            ("CERTIFIED","The normalized Cartan-square moment map has the complete closed unit ball as image, with radius F(u)=3u/(2+u^2). For alpha*delta>0, r(s)=s*alpha/[s*alpha+(1-s)*delta] stays in [0,1] and cancels the scaled kernel moment."),
            ("CERTIFIED","The repaired uniform-scaling/moving-square ansatz is disposed. If alpha*delta<0 and the initial square moment is nonzero, the receiving coefficient has one interior zero while the kernel moment remains nonzero. At alpha=0 the complete stratum contracts by a coefficient-zero square pre-rotation followed by the phase-real uniform path."),
            ("CERTIFIED","Uniform scaling preserves the third-transvectant kernel equation, every moved receiving factor remains common-square, and sign-compatible paths end in the connected double-singular hub."),
            _second_order(("CERTIFIED","Candidate 17's complete alpha<=0 stratum and candidate 20 off balance with alpha=0 or alpha having the sign of delta contract to the hub; phase-real and square-vertex points remain covered. The complementary obstruction is only for the declared uniform-scaling ansatz."),("CERTIFIED","All declared paths are finite smooth exponential-polynomial carrier paths; no all-orders promotion is made."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_moving_square_contraction","same_sign_candidate17_20_singular_radial_contraction","same_sign_candidate17_20_common_square_rotation_quotient","same_sign_candidate17_20_double_singular_rotation_zero_fibre","same_sign_third_transvectant_singular_locus"),
            "This is not a general nonradial no-go and does not establish complete candidate-17 or candidate-20 off-balance connectedness or disconnection. Fixed-direction independent K-node scaling is classified by its successor row; K-direction deformations inside T3(f,g)=0, occupation gluing, final residual descent and causal, observational or quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_independent_node_scaling_contraction",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately; only their strict alpha*delta<0 non-phase-real strata are newly classified", boundaries="closed S1_L times S2 after both free active-node phases and before lifted-rotation or final residual quotient", carrier="both complete singular components with fixed K-node directions, independent squared node scales (x,y) in [0,1]^2, exact occupation transfer and arbitrary continuous motion of the receiving common-square direction", degree=2, parity="both labelled factorized parity channels", ell="input 2 x 2; output L=1", m="all m=-2,...,2 through fixed weighted K-node moments and the normalized Cartan-square moment ball", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision with strict alpha*delta<0", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidates 17 and 20 remain distinct. The theorem classifies only each candidate's own strict opposite-sign stratum and imports the repaired alpha=0 contraction separately."),
            ("CERTIFIED","With fixed weighted node moments U,V, independent scaling gives M_K=-x*U+y*V and c=delta+a*x-b*y. The receiving Cartan-square moment ranges over the complete closed unit ball."),
            ("CERTIFIED","Every path crosses c=0, where rotation zero forces M_K=0. Thus contraction is possible exactly when I={(x,y) in [0,1]^2:c=0=M_K} is nonempty. For nonzero U,V this requires positive collinearity and the explicit box inequalities."),
            ("CERTIFIED","When I is nonempty, a three-stage path reaches it with the initial square direction, moves the square moment to zero while c=M_K=0, and then reaches the connected hub with a phase-real square direction."),
            _second_order(("CERTIFIED","The fixed-direction independent-node-scaling ansatz is completely classified: incidence points contract, while off-incidence strict opposite-sign points are obstructed within this ansatz."),("CERTIFIED","The same finite carrier paths are smooth exponential-polynomial paths; no all-orders promotion is made."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_independent_node_scaling_contraction","same_sign_candidate17_20_moving_square_contraction","same_sign_candidate17_20_double_singular_rotation_zero_fibre","same_sign_third_transvectant_singular_locus"),
            "This is not a no-go for deformation of the K-node directions inside T3(f,g)=0 or for general nonradial paths. Complete candidate-17 and candidate-20 off-balance connectedness or disconnection, occupation gluing, final residual descent and causal, observational or quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_deformable_kernel_incidence_normal_form",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately on their strict alpha*delta<0 fixed-total-occupation strata", boundaries="closed S1_L times S2 after compactifying both K-node occupations, quotienting their phases and the lifted SO(3), and before final residual quotient", carrier="the complete compactified T3(F,G)=0 kernel-amplitude carrier, including arbitrary direction deformation, zero-node boundaries, common-square singular points and all compact stabilizer orbit types", degree=2, parity="both labelled factorized parity channels", ell="input 2 x 2; output L=1", m="all m=-2,...,2 in the compact spin-two kernel carrier", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision with strict alpha*delta<0", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidates 17 and 20 retain distinct coefficient chambers and atlas scopes. The common proof supplies no mode identification across their backgrounds."),
            ("CERTIFIED","The compactified admissible base is A={T3(F,G)=0, ||F||_W,||G||_W<=1, ||M_K||<=|c|} modulo both node phases and lifted SO(3). Zero-node stabilizers and the algebraic singular locus are retained rather than divided away."),
            ("CERTIFIED","For strict opposite signs, contraction to the hub is equivalent to the initial path component of A meeting I={c=0=M_K}. The Cartan-square moment map has connected fibres and the explicit radial normal form supplies the required path lift."),
            ("CERTIFIED","T3 is odd and bilinear, so the compactified carrier and incidence-to-hub scaling preserve resonance. Both sign chambers have explicit one-zero-node phase-real incidence points."),
            _second_order(("OPEN","The exact component-incidence criterion is certified, but whether every admissible candidate-17 or candidate-20 strict-sign component meets I remains open."),("OPEN","The finite semialgebraic criterion embeds in the smooth exponential-polynomial class, but its component enumeration remains open and no all-orders promotion is made."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_deformable_kernel_incidence_normal_form","same_sign_candidate17_20_independent_node_scaling_contraction","same_sign_candidate17_20_moving_square_contraction","same_sign_candidate17_20_double_singular_rotation_zero_fibre","same_sign_third_transvectant_singular_locus"),
            "The deformable-direction problem is reduced exactly to compact semialgebraic component incidence, not declared connected. Nonemptiness of I does not imply every component reaches it. Complete candidate-17 and candidate-20 off-balance connectedness, occupation gluing, final residual descent and causal, observational or quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_deformable_kernel_complete_contraction",
            _scope(theory="Weyl-Maxwell target", background="candidates 17 and 20 separately at every fixed positive active occupation, including candidate 20 on and off its exact balance divisor", boundaries="closed S1_L times S2 after compactifying both K-node occupations and reducing their phases and lifted rotations, before occupation gluing or final residual quotient", carrier="both complete singular components (S_plus x K_minus) union (K_plus x S_minus), including arbitrary compactified T3-kernel directions, zero-node boundaries and all stabilizer strata", degree=2, parity="both labelled factorized parity channels", ell="input 2 x 2; output L=1", m="all m=-2,...,2 in the spin-two kernel and common-square carriers", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision on every alpha/delta sign stratum", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidate 17 and candidate 20 retain distinct backgrounds, coefficients and atlas scopes. The common contraction proof does not identify their modes."),
            ("CERTIFIED","The normalized spin-two moment lies in the unit ball. A time-reversal homotopy has m(f_theta)=cos(2theta)*m(f)/[1+sigma*sin(2theta)] and monotonically reaches a phase-real zero-moment direction."),
            ("CERTIFIED","In each strict opposite-sign chamber, convexity permits deletion of the oppositely signed kernel node before time-reversal damping of the survivor. Every admissible component therefore reaches the one-zero-node incidence and the connected hub."),
            ("CERTIFIED","At a zero node the third transvectant vanishes identically; the survivor deformation is unrestricted. Bilinear radial scaling preserves T3 and crosses c=0 only after M_K=0."),
            _second_order(("CERTIFIED","Combining the new opposite-sign path with the repaired same-sign/alpha=0 path and candidate-20 balance contraction proves the complete fixed-positive-occupation singular rotation-zero unions connected for candidates 17 and 20."),("CERTIFIED","All paths are finite smooth exponential-polynomial carrier paths; this is not an all-orders solution theorem."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_deformable_kernel_complete_contraction","same_sign_candidate17_20_deformable_kernel_incidence_normal_form","same_sign_candidate17_20_moving_square_contraction","same_sign_candidate17_20_singular_radial_contraction","same_sign_candidate17_20_double_singular_rotation_zero_fibre","same_sign_third_transvectant_singular_locus"),
            "This closes fixed-positive-active-occupation singular rotation-zero topology only. It does not identify candidates 17 and 20, glue distinct total-occupation strata, construct a global Hausdorff leaf space beyond this carrier, perform final residual descent, establish all-orders integration, or supply causal, observational or quantum maps.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_candidate17_20_component_incidence_classification",
            _scope(theory="Weyl-Maxwell target", background="candidate 17 and candidate 20 retained separately; the two candidate-20 off-balance delta-sign chambers are also separate", boundaries="closed S1_L times S2 on each fixed positive active occupation after compactifying both K-node occupations and quotienting node phases and lifted rotations, before occupation gluing or final residual descent", carrier="the strict alpha*delta<0 admissible orbit spaces with four exhaustive occupation strata and every realized compact orbit type, including nonfree stabilizers", degree=2, parity="both labelled factorized parity channels", ell="input 2 x 2; output L=1", m="all m=-2,...,2 in the compact spin-two kernel carrier", k="candidate-specific signed compact momenta, never identified across candidates", omega="candidate-specific DIFFERENCE collision in the strict opposite-sign chambers", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","Candidate 17 has one rho_17 component ledger; candidate 20 has separate negative- and positive-delta rho_20 ledgers. No mode or background identification is made."),
            ("CERTIFIED","The four exhaustive occupation strata are interior, F-zero, G-zero and origin, each refined by every realized compact stabilizer type. Zero-node phase stabilizers and the full origin isotropy are retained."),
            ("CERTIFIED","Each of the three strict-sign candidate chambers has exactly one path component. Its unique component meets I={c=0=M_K}; no nonincident component exists."),
            ("CERTIFIED","For delta<0 the incidence lies on G=0 at x=-delta/a; for delta>0 it lies on F=0 at y=delta/b. The independently checked wrong-node paths cross the wall prematurely."),
            _second_order(("CERTIFIED","The candidate-specific pi_0 classification completes the fixed-positive-occupation bounded singular carrier."),("CERTIFIED","The same finite carrier paths are smooth exponential-polynomial paths; this does not establish all-orders integration."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_candidate17_20_component_incidence_classification","same_sign_candidate17_20_deformable_kernel_complete_contraction","same_sign_candidate17_20_deformable_kernel_incidence_normal_form","same_sign_candidate17_20_moving_square_contraction","same_sign_candidate17_20_singular_radial_contraction","same_sign_candidate17_20_double_singular_rotation_zero_fibre"),
            "This classifies candidate-specific pi_0 and zero-wall incidence only on fixed positive active occupations. It does not identify candidates, glue distinct total occupations, construct a global Hausdorff quotient outside this carrier, perform final residual descent, solve all mixed cones or evolution, or establish causal, observational or quantum claims.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_active_phase_reduced_presymplectic_divisors",
            _scope(theory="Weyl-Maxwell target", background="three distinct collision candidates 17, 18 and 20, retained separately", boundaries="closed S1_L times S2 before lifted-rotation or final residual quotient", carrier="the complete smooth regular active resonance varieties at nonzero fixed active-node occupations after the two common node-phase quotients", degree=2, parity="both exact factorized parity channels with their common physical-node phases coupled", ell="input 2 x 2; output L=1 on candidates 17/20 and L=3 on candidate 18", m="all m=-2,...,2", k="candidate-specific allowed compact momenta, never identified across rho", omega="candidate-specific certified SUM or DIFFERENCE collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The candidate-labelled branch and momentum carriers are unchanged; no parity factor, circumference background or spectator coordinate is identified with another."),
            ("CERTIFIED","Appending the two total-node Hermitian horizontal rows gives A. On every regular chart det(A H^{-1} A^dagger)=0 is the complete fixed-occupation node-phase-reduced divisor; its determinantal ideals give every reduced corank."),
            ("OPEN","The exact bounded witnesses still have all five stabilizer moments zero, but the lifted SO(3) zero fibre and quotient are not inferred from the node-phase reduction."),
            ("CERTIFIED","Candidates 17/20 use one coupled 8x8 determinant with horizontal dimension 12; candidate 18 uses 100 product charts, a 10x30 augmented matrix, horizontal dimension 20 and retains all ten positive spectators."),
            _second_order(("CERTIFIED","The imported candidate-17/18/20 radical points remain in the exact bounded fibre product. The general reduced divisor is a current theorem, not a claim that every divisor point satisfies all Taub and resonance functionals."),("CERTIFIED","The same finite witnesses lie in the smooth-secular class; no all-orders leaf is inferred."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_active_phase_reduced_presymplectic_divisors","same_sign_active_presymplectic_divisors","same_sign_L1_active_restricted_current_degeneracy","same_sign_candidate18_active_restricted_current_degeneracy","same_sign_phase_parity_fibre_product","axial_current","polar_current"),
            "This classifies the smooth regular fixed-active-occupation current after the two common node phases only. Lifted-rotation reduction, global/Hausdorff leaf-space topology, singular-locus reduction, occupation gluing, final residual descent, all-orders integration and causal, observational or quantum maps remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_same_sign_active_local_rotation_leaf_descent",
            _scope(theory="Weyl-Maxwell target", background="three distinct collision candidates 17, 18 and 20, retained separately", boundaries="closed S1_L times S2 before global rotation or final residual quotient", carrier="every smooth constant-corank fixed-occupation active stratum after the two common node phases, on a simple saturated current-radical neighbourhood", degree=2, parity="both coupled parity channels; candidate-18 positive spectators retained", ell="input 2 x 2; output L=1 on candidates 17/20 and L=3 on candidate 18", m="all m=-2,...,2 under the lifted diagonal SO(3) action", k="candidate-specific allowed compact momenta, never identified across rho", omega="candidate-specific certified SUM or DIFFERENCE collision", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The theorem applies candidatewise after the already certified common-node-phase reduction; it does not identify radical leaves, parity channels or backgrounds."),
            ("CERTIFIED","The closed reduced Lee-Wald form descends through its constant-rank radical to each local simple symplectic leaf quotient."),
            ("CERTIFIED","Hamiltonianity gives d<mu,xi>(r)=0 for every current radical r. The lifted rotation moment map is basic on radical leaves, and imposing mu=0 commutes locally with removing the radical."),
            ("CERTIFIED","The current radical and lifted-rotation constraint remain distinct compatible structures; neither is substituted for the other."),
            _second_order(("CERTIFIED","The previously certified bounded radical points retain their local rotation-zero condition on the leaf quotient; no complete fibre connectedness follows."),("CERTIFIED","The same local finite strata lie in the smooth-secular class without an all-orders promotion."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("same_sign_active_local_rotation_leaf_descent","same_sign_active_phase_reduced_presymplectic_divisors","same_sign_active_presymplectic_divisors","same_sign_L1_active_restricted_current_degeneracy","same_sign_candidate18_active_restricted_current_degeneracy","taub"),
            "This covers only smooth constant-corank fixed-occupation strata on local simple saturated neighbourhoods. It does not construct a global leaf space, prove complete rotation-zero-fibre connectedness, reduce singular strata, glue occupations or candidates, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_parity_workload",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at the 21 isolated algebraic circumference candidates; before final residual quotient", carrier="parity-typed q-minus, p-extra and q-plus ell=2 cross pairs between |n|=1 and |n|=2", degree=2, parity="84 allowed axial/polar input-output channels; forbidden parity assignments removed", ell="input 2 x 2; candidate outputs L=1,3,4", m="all m through multiplicity-one V2 tensor V2 intertwiners; odd L requires nonaxisymmetric fixtures", k="signed n in {+/-1,+/-2} times 2*pi/L, restricted to cross-|n| pairs", omega="the exact SUM or DIFFERENCE channel assigned to each isolated row", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All parity-typed input and target branch multiplicities retain their exact shell and compact-momentum labels."),
            ("CERTIFIED","The action-derived generic and exceptional quotient multiplicities give 164 reduced scalar adjoint coefficient slots, split equally between axial and polar targets."),
            ("NOT_APPLICABLE","Parity/angular selection does not replace the separate five compact stabilizer moment maps."),
            ("CERTIFIED","Parity removes half of 168 naive assignments but no all-m shell row: 84 channels survive; 108 coefficients are L=4 axisymmetric fixtures and 56 odd-L coefficients require nonaxisymmetric fixtures."),
            _second_order(("OPEN","None of the 164 projected source coefficients is inferred to vanish; bounded extension or obstruction remains undecided."),("OPEN","The parity workload does not solve resonant rows even when secular corrections are admitted."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("ell2_two_abs_momentum_parity_workload","ell2_two_abs_momentum_isolated_candidates","branch_dictionary"),
            "Parity/angular workload theorem only for the 21 ell=2 cross-|n| candidates. No source zero, same-fibre classification, tangent-cone verdict or higher lifecycle is inferred.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate4_axial_bounded_obstruction",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at candidate-4 rho=29*(-361+783*sqrt(3))/26772; before final residual quotient", carrier="one axial q-minus ell=2,m=0 oscillator on n=+1 crossed with one axial q-minus ell=2,m=0 oscillator on n=-2", degree=2, parity="axial times axial input; polar p-primary output", ell="input 2 x 2; output L=4", m="0+0 -> M=0", k="k1=sqrt(rho), k2=-2*sqrt(rho), K=-sqrt(rho)", omega="positive-frequency SUM channel on the polar p shell", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The two input q-minus branches and polar p-primary target retain their exact same-background parity, momentum, harmonic and frequency labels."),
            ("CERTIFIED","The action-derived q2 PBW projection exactly reproduces the frozen opposite-momentum calibration before evaluating the candidate-4 source."),
            ("NOT_APPLICABLE","This nonzero-frequency resonant functional is independent of, and does not replace, the five compact stabilizer moment maps."),
            ("OBSTRUCTED","The complete two-dimensional polar p-shell cokernel pairing is (0,-1152*(-265+149*sqrt(3))/203), whose nonzero component has quadratic-field norm witness 3622."),
            _second_order(("OBSTRUCTED","No bounded or finite-quasiperiodic correction exists for this declared cross-|n| tangent."),("OPEN","A smooth secular correction for this candidate has not been constructed or excluded."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_candidate4_obstruction","ell2_two_abs_momentum_parity_workload","ell2_two_abs_momentum_isolated_candidates","polar_operator","abstract_cone"),
            "This G1 row resolves only the two axial-axial polar p-primary coefficients of candidate 4. The other 162 workload coefficients, complete two-fibre tangent cone, smooth-secular and causal classes, residual descent and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_qminus_l4_triplet_obstruction",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at three separately tuned candidate-3, candidate-4 and candidate-5 algebraic circumferences; before final residual quotient", carrier="one axial q-minus ell=2,m=0 oscillator on n=+1 crossed with one axial q-minus ell=2,m=0 oscillator on n=-2", degree=2, parity="axial times axial input; polar L=4 output on q-minus, p-extra or q-plus target primary", ell="input 2 x 2; output L=4", m="0+0 -> M=0", k="signed compact-momentum integers (+1,-2), with each target row retaining its own algebraic circumference", omega="positive-frequency SUM channel on the row-specific target shell", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The q-minus inputs and each q-minus, p-extra or q-plus target retain exact same-background branch, parity, harmonic, signed-momentum, frequency and circumference labels; the three fibres are not identified."),
            ("CERTIFIED","The content-addressed action-derived q2 slice supplies the polar L=4 source, while the certified polar primary decomposition fixes the complete q and p target cokernel multiplicities."),
            ("NOT_APPLICABLE","These nonzero-frequency resonant functionals are independent of, and do not replace, the five compact stabilizer moment maps."),
            ("OBSTRUCTED","Candidate 4 has the certified nonzero two-component p-primary pairing; the candidate-3 and candidate-5 q-primary pairings obey one exact quartic annihilator whose nonzero constant term excludes zero."),
            _second_order(("OBSTRUCTED","No bounded or finite-quasiperiodic correction exists for any of the three declared cross-|n| tangents."),("OPEN","A smooth secular correction has not been constructed or excluded for these rows."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_axial_qminus_L4_triplet","ell2_two_abs_momentum_candidate4_obstruction","ell2_two_abs_momentum_parity_workload","ell2_two_abs_momentum_isolated_candidates","polar_operator","abstract_cone"),
            "This G1 row resolves four scalar adjoint coefficients across candidates 3, 4 and 5 at three separate circumferences. The other 160 workload coefficients, complete two-fibre tangent cone, smooth-secular and causal classes, residual descent and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_axial_l4_matrix",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at twelve separately tuned algebraic circumference rows; before final residual quotient", carrier="all twenty axisymmetric axial ell=2 branch-basis cross products between |n|=1 and |n|=2 that resonate at L=4", degree=2, parity="axial times axial input; polar L=4 output", ell="input 2 x 2; output L=4", m="0+0 -> M=0", k="row-specific signed compact momenta on |n|=1 and |n|=2; circumference rows retained separately", omega="row-specific positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every q-minus, p-extra and q-plus input and target keeps its exact same-background branch, parity, harmonic, signed-momentum, frequency and circumference label; distinct rows are not identified."),
            ("CERTIFIED","The action-derived generic axial-pair q2 slice supplies all 27 polar L=4 adjoint coefficients and reproduces the narrow q-minus/q-minus slice exactly."),
            ("NOT_APPLICABLE","These nonzero-frequency resonant functionals are independent of, and do not replace, the five compact stabilizer moment maps."),
            ("OBSTRUCTED","Exactly one of 27 scalar components vanishes, while 26 have exact rational intervals excluding zero; every one of the twenty declared branch-basis fixtures has a nonzero complete cokernel vector."),
            _second_order(("OBSTRUCTED","No bounded or finite-quasiperiodic correction exists for any of the twenty declared axial-axial branch-basis fixtures."),("OPEN","Smooth-secular corrections and cancellations among arbitrary axial linear combinations are not classified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_axial_axial_L4_matrix","ell2_two_abs_momentum_axial_qminus_L4_triplet","ell2_two_abs_momentum_parity_workload","polar_operator","abstract_cone"),
            "This G2 row classifies the complete 27-coefficient axial-axial L4 basis matrix, not its arbitrary-amplitude zero variety. The other 81 axisymmetric and 56 odd-L coefficients, complete two-fibre tangent cone, smooth-secular and causal classes, residual descent and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_polar_polar_l4_matrix",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at twelve separately tuned algebraic circumference rows; before final residual quotient", carrier="all twenty axisymmetric polar ell=2 branch-basis cross products between |n|=1 and |n|=2 that resonate at L=4", degree=2, parity="polar times polar input; polar L=4 output", ell="input 2 x 2; output L=4", m="0+0 -> M=0", k="row-specific signed compact momenta on |n|=1 and |n|=2; circumference rows retained separately", omega="row-specific positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every q-minus, p-extra and q-plus polar input and target keeps its exact same-background branch, parity, harmonic, signed-momentum, frequency and circumference label; distinct rows are not identified."),
            ("CERTIFIED","The action-derived generic polar-pair q2 slice supplies all 27 polar L=4 adjoint coefficients, reproduces the prior direct four-dimensional polar source and checks every input representative against the polar Hessian."),
            ("NOT_APPLICABLE","These nonzero-frequency resonant functionals are independent of, and do not replace, the five compact stabilizer moment maps."),
            ("OBSTRUCTED","Exactly one of 27 scalar components vanishes, while 26 have exact rational intervals excluding zero; every one of the twenty declared polar branch-basis fixtures has a nonzero complete cokernel vector."),
            _second_order(("OBSTRUCTED","No bounded or finite-quasiperiodic correction exists for any of the twenty declared polar-polar branch-basis fixtures."),("OPEN","Smooth-secular corrections and cancellations among arbitrary polar linear combinations are not classified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_polar_polar_L4_matrix","ell2_two_abs_momentum_axial_axial_L4_matrix","ell2_two_abs_momentum_parity_workload","polar_operator","abstract_cone"),
            "This G2 row classifies the complete 27-coefficient polar-polar L4 basis matrix, not its arbitrary-amplitude zero variety. The two ordered cross-parity matrices, 56 odd-L coefficients, complete two-fibre tangent cone, smooth-secular and causal classes, residual descent and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_polar_l4_matrix",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at twelve separately tuned algebraic circumference rows; before final residual quotient", carrier="twenty ordered axisymmetric axial-first polar-second ell=2 branch-basis cross products between |n|=1 and |n|=2 that resonate at L=4", degree=2, parity="axial first, polar second; axial L=4 output", ell="input 2 x 2; output L=4", m="0+0 -> M=0", k="row-specific signed compact momenta; circumference rows retained separately", omega="row-specific positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every axial-first and polar-second branch, signed momentum, frequency and circumference label is retained; the reverse input order is not identified with this carrier."),
            ("CERTIFIED","The shared action-derived cross-parity q2 slice contains both ordered PBW supports and reproduces the prior direct four-dimensional axial-plus-polar-minus source exactly."),
            ("NOT_APPLICABLE","These nonzero-frequency resonant functionals are independent of, and do not replace, the five compact stabilizer moment maps."),
            ("OBSTRUCTED","All 27 scalar adjoint coefficients have exact rational intervals excluding zero, so every one of the twenty forward-ordered basis fixtures has a nonzero cokernel vector."),
            _second_order(("OBSTRUCTED","No bounded or finite-quasiperiodic correction exists for any declared forward-ordered basis fixture."),("OPEN","Arbitrary-amplitude cancellations and smooth-secular corrections are not classified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_axial_polar_L4_matrix","ell2_two_abs_momentum_polar_polar_L4_matrix","ell2_two_abs_momentum_parity_workload","axial_operator","abstract_cone"),
            "This row is the forward ordered 27-coefficient basis matrix, not the reverse order or an amplitude-cone theorem. The reverse 27 coefficients, 56 odd-L coefficients and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_polar_axial_l4_matrix",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at twelve separately tuned algebraic circumference rows; before final residual quotient", carrier="twenty ordered axisymmetric polar-first axial-second ell=2 branch-basis cross products between |n|=1 and |n|=2 that resonate at L=4", degree=2, parity="polar first, axial second; axial L=4 output", ell="input 2 x 2; output L=4", m="0+0 -> M=0", k="row-specific signed compact momenta; circumference rows retained separately", omega="row-specific positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every polar-first and axial-second branch, signed momentum, frequency and circumference label is retained; explicit role substitution, not name matching, relates this computation to the shared slice."),
            ("CERTIFIED","The shared action-derived q2 slice contains 832 terms in each PBW input order; the reverse workload assigns the physical branch and momentum data to the opposite declared roles."),
            ("NOT_APPLICABLE","These nonzero-frequency resonant functionals are independent of, and do not replace, the five compact stabilizer moment maps."),
            ("OBSTRUCTED","All 27 scalar adjoint coefficients have exact rational intervals excluding zero, so every one of the twenty reverse-ordered basis fixtures has a nonzero cokernel vector."),
            _second_order(("OBSTRUCTED","No bounded or finite-quasiperiodic correction exists for any declared reverse-ordered basis fixture."),("OPEN","Arbitrary-amplitude cancellations and smooth-secular corrections are not classified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_polar_axial_L4_matrix","ell2_two_abs_momentum_axial_polar_L4_matrix","ell2_two_abs_momentum_parity_workload","axial_operator","abstract_cone"),
            "This row closes 108 of 108 axisymmetric L4 basis coefficients, not the arbitrary-amplitude zero variety. The 56 nonaxisymmetric L1/L3 coefficients, complete two-fibre cone and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_nonaxisymmetric_l3_matrix",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at six separately tuned algebraic circumference rows; before final residual quotient", carrier="all 36 Clebsch-Gordan-coupled L3 branch-basis cross products between |n|=1 and |n|=2", degree=2, parity="both same-parity and both ordered cross-parity inputs; parity-selected L3 output", ell="input 2 x 2; output L=3", m="coupled M=3 representative of the multiplicity-one V3 carrier", k="row-specific signed compact momenta; circumference rows retained separately", omega="row-specific positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every branch, parity ordering, signed momentum, frequency, circumference and V3 carrier label is retained; no mode names are identified across fibres."),
            ("CERTIFIED","The equatorial coefficient-jet projector reproduces all three existing L4 parity calibrations and supplies one generic L3 action source for each ordered parity class."),
            ("NOT_APPLICABLE","These nonzero-frequency resonant functionals are independent of, and do not replace, the five compact stabilizer moment maps."),
            ("OBSTRUCTED","All 44 target-adjoint coefficients have exact intervals excluding zero; all 36 declared branch-basis fixtures have nonzero complete cokernel vectors."),
            _second_order(("OBSTRUCTED","No bounded or finite-quasiperiodic correction exists for any declared L3 branch-basis fixture."),("OPEN","Arbitrary-amplitude cancellations and smooth-secular corrections are not classified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_nonaxisymmetric_L3_matrix","ell2_two_abs_momentum_polar_axial_L4_matrix","ell2_two_abs_momentum_parity_workload","abstract_cone"),
            "This row closes the 44-coefficient L3 basis matrix, not its arbitrary-amplitude zero variety. The twelve nonaxisymmetric L1 coefficients, complete two-fibre cone, smooth-secular and causal classes remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_nonaxisymmetric_l1_matrix",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 at three separately tuned algebraic circumference rows; before final residual quotient", carrier="final twelve exceptional L1 difference-channel branch-basis coefficients, with the certified L3 submatrix replayed as a completion check", degree=2, parity="all four ordered axial/polar input pairs retained", ell="input 2 x 2; output L=1", m="multiplicity-one Clebsch-Gordan V1 carrier extracted at M=1", k="row-specific signed compact momenta on |n|=1 and |n|=2; circumference rows retained separately", omega="row-specific signed DIFFERENCE channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All theory, background, boundary, charge, parity, harmonic, magnetic, signed-momentum, temporal-sign and circumference labels are retained; the L1 exceptional and generic L3/L4 targets are not merged."),
            ("CERTIFIED","The action-derived Clebsch-Gordan projector reproduces all four L4 normalizations, replays the certified 44-coefficient L3 slice and contracts the final twelve L1 sources with the certified nonzero-k exceptional target covectors."),
            ("NOT_APPLICABLE","These nonzero-frequency resonant functionals are independent of, and do not replace, the five compact stabilizer moment maps."),
            ("OBSTRUCTED","All twelve exceptional L1 adjoint coefficients are nonzero; with the certified L3 and L4 matrices this closes all 164 declared branch-basis scalar coefficients."),
            _second_order(("OBSTRUCTED","No bounded or finite-quasiperiodic correction exists for any of the twelve declared L1 branch-basis fixtures."),("OPEN","The arbitrary-amplitude common zero variety and smooth-secular correction class are not classified."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_nonaxisymmetric_L1_L3_completion","ell2_two_abs_momentum_nonaxisymmetric_L3_matrix","ell2_two_abs_momentum_polar_axial_L4_matrix","ell2_two_abs_momentum_parity_workload","exceptional_nonzero_k_cofiber","abstract_cone"),
            "This final L1 row closes 164 of 164 branch-basis scalar coefficients across the separately certified L1, L3 and L4 matrices, not the arbitrary-amplitude zero variety or complete two-fibre tangent cone. Smooth-secular, causal, residual, observational and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_cross_fibre_amplitude_system",
            _scope(theory="Weyl-Maxwell target", boundaries="twenty-one separately tuned closed S1_L times S2 circumference fibres; before final residual quotient", carrier="factorized all-m bilinear resonance systems for complex positive-frequency ell=2 amplitudes on |n|=1 and |n|=2", degree=2, parity="both input and target parities retained with branch multiplicity matrices", ell="input 2 x 2; three L=1, six L=3 and twelve L=4 fibres", m="all input m=-2,...,2 and every output M through exact normalized Clebsch-Gordan tensors", k="row-specific signed compact momenta; physical circumference fibres kept separate", omega="row-specific signed SUM or DIFFERENCE channel; negative-frequency equations are conjugate", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Exact algebraic comparison partitions the workload into twenty-one pairwise distinct physical circumference fibres; amplitudes are never cancelled across different backgrounds."),
            ("CERTIFIED","The 54 target-parity/adjoint equations on 128 ordered branch-basis fixtures contain 164 action-derived internal coefficients (162 nonzero, two zero components); branch-multiplicity matrices and normalized Clebsch-Gordan maps lift them to 418 complex scalar magnetic equations."),
            ("OPEN","The five compact stabilizer moment maps have not yet been joined to the twenty-one fibrewise resonance systems."),
            ("CERTIFIED","The complete factorized cross-fibre equations and both mandatory one-fibre-zero planes are explicit; nontrivial mixed components remain undecomposed."),
            _second_order(("OPEN","The irreducible mixed zero varieties, same-fibre quadratic sources and intersection with the stabilizer moment maps remain open."),("OPEN","Smooth-secular correction classes are not classified on the factorized amplitude varieties."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_cross_fibre_amplitude_system","ell2_two_abs_momentum_nonaxisymmetric_L1_L3_completion","ell2_two_abs_momentum_polar_axial_L4_matrix","ell2_two_abs_momentum_parity_workload","abstract_cone"),
            "This is the complete necessary cross-fibre resonance system, not an irreducible zero-variety decomposition or tangent-cone theorem. Same-fibre sources, Taub intersections and higher correction classes remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l4_zero_varieties",
            _scope(theory="Weyl-Maxwell target", boundaries="five separately tuned closed S1_L times S2 circumference fibres; before final residual quotient", carrier="the scalar-internal all-m L4 resonance blocks on candidates 3,5,9,15,21", degree=2, parity="axial and polar amplitude quartics retained on both momentum fibres", ell="input 2 x 2; output L=4", m="all magnetic components through Sym^4(C^2) multiplication into Sym^8(C^2)", k="row-specific signed |n|=1 and |n|=2 momenta", omega="positive-frequency SUM channel; real tangents include conjugates", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The five physical circumference fibres 3,5,9,15,21 remain separate; no cross-background amplitude identification is used."),
            ("CERTIFIED","The scalar parity coefficients use the action-derived normalized L4 coordinate, and every coefficient plus each sheet ratio has an exact nonzero interval witness."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not yet been intersected with these resonance components."),
            ("CERTIFIED","Each complete all-m resonance zero variety has exactly four ten-dimensional linear components over C: two one-fibre-zero planes and two mixed proportionality sheets; all ten mixed sheets have real representatives."),
            _second_order(("OPEN","The resonance varieties are decomposed, but same-fibre sources and their Taub intersection remain necessary before a bounded tangent-cone verdict."),("OPEN","Smooth-secular correction classes are not classified on these four-component varieties."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_scalar_L4_zero_varieties","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This decomposes exactly five scalar-internal L4 cross-fibre resonance varieties, not the other sixteen fibres or the complete two-fibre tangent cone. Same-fibre sources, Taub intersections and higher correction classes remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_odd_l_highest_weight_zero_subspaces",
            _scope(theory="Weyl-Maxwell target", boundaries="nine separately tuned closed S1_L times S2 circumference fibres; before final residual quotient", carrier="highest-weight aligned mixed subspaces on all cross-|n| fibres with target L=1 or L=3", degree=2, parity="all declared input parities and branch copies retained", ell="input 2 x 2; output L=1 or L=3", m="both declared signed-frequency carriers supported at m=2, hence M=4", k="row-specific signed |n|=1 and |n|=2 momenta", omega="six SUM rows and three signed DIFFERENCE rows; real partners retained", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All nine physical circumference fibres remain distinct; the three L1 difference carriers and six L3 sum carriers are not identified across backgrounds or temporal signs."),
            ("CERTIFIED","The action-derived branch and target data are retained, but the vanishing occurs already in the exact Clebsch--Gordan factor before any coefficient matrix is contracted."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not been restricted to these highest-weight subspaces."),
            ("CERTIFIED","Supporting both signed-frequency ell=2 inputs at m=2 forces M=4, so all 130 scalar equations with target L=1 or L=3 vanish; every odd-L fibre has a mixed nonzero point."),
            _second_order(("OPEN","These are cross-fibre resonance-zero subspaces, not bounded second-order solutions; same-fibre sources and Taub constraints remain unjoined."),("OPEN","Smooth-secular correction is not classified on these subspaces."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This certifies mixed zero subspaces on all nine odd-L fibres, not their complete irreducible ideals or the two-fibre tangent cone. Same-fibre, Taub, bounded, smooth-secular, residual, causal and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l3_zero_variety",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-2 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="complete scalar-internal all-m cross-|n| resonance variety", degree=2, parity="axial and polar amplitudes on both momentum fibres", ell="input 2 x 2; output L=3", m="all magnetic components through the first binary-quartic transvectant", k="signed compact momenta (1,-2)", omega="positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Candidate 2 remains one declared physical circumference fibre and is not identified with the other twenty collision backgrounds."),
            ("CERTIFIED","The exact action-derived parity pencil has four nonzero coefficients and an invertible real eigenbasis with nonzero eigenvalues plus and minus lambda."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not been restricted to this determinantal variety."),
            ("CERTIFIED","The complete all-m resonance variety is one irreducible complex dimension-12 Cartesian product of two rank-at-most-one 5 x 2 determinantal varieties, defined by twenty minors."),
            _second_order(("OPEN","A complete resonance ideal is necessary but not sufficient for bounded extension; same-fibre sources and Taub constraints remain unjoined."),("OPEN","Smooth-secular correction is not classified on this determinantal variety."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_scalar_L3_zero_variety","ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This classifies the candidate-2 scalar L3 resonance ideal, not the other fifteen fibrewise ideals or the two-fibre tangent cone. Same-fibre, Taub, bounded, smooth-secular, residual, causal and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l1_zero_varieties",
            _scope(theory="Weyl-Maxwell target", boundaries="three separately tuned closed S1_L times S2 circumference fibres; before final residual quotient", carrier="complete scalar-internal all-m cross-|n| resonance varieties", degree=2, parity="axial and polar amplitudes on both momentum fibres", ell="input 2 x 2; output L=1", m="all magnetic components through the third binary-quartic transvectant", k="row-specific signed |n|=1 and |n|=2 momenta", omega="signed DIFFERENCE channel with temporal signs (+1,-1)", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Candidates 14,17,20 remain three distinct physical circumference fibres, and the negative-frequency B carriers retain their opposite-m reality partners."),
            ("CERTIFIED","Every action-derived parity pencil has exact lambda squared equal to 128/5 and diagonalizes into two independent third-transvectant equations."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not been restricted to these three varieties."),
            ("CERTIFIED","Each complete all-m resonance variety is one irreducible complex dimension-14 Cartesian product of two third-transvectant kernels; the exact rank-drop and elimination ideals are certified."),
            _second_order(("OPEN","Complete resonance ideals are necessary but not sufficient for bounded extension; same-fibre sources and Taub constraints remain unjoined."),("OPEN","Smooth-secular correction is not classified on these varieties."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_scalar_L1_zero_varieties","ell2_two_abs_momentum_scalar_L3_zero_variety","ell2_two_abs_momentum_scalar_L4_zero_varieties","ell2_two_abs_momentum_candidate4_L4_zero_variety","ell2_two_abs_momentum_target_doublet_L3_zero_varieties","ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties","ell2_two_abs_momentum_rank_one_branch_zero_varieties","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This classifies all three scalar L1 resonance ideals. Together with the separately certified later fibres, all 20 fibrewise cross-fibre resonance ideals are now classified; the two-fibre tangent cone is still open. Same-fibre, Taub, bounded, smooth-secular, residual, causal and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate4_l4_zero_variety",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-4 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="complete scalar-input target-doublet all-m cross-|n| resonance variety", degree=2, parity="axial and polar amplitudes on both momentum fibres", ell="input 2 x 2; output L=4", m="all magnetic components through binary-quartic multiplication", k="signed compact momenta (1,-2)", omega="positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Candidate 4 remains one declared physical circumference fibre and is not identified with any other collision background."),
            ("CERTIFIED","The two target-adjoint components per parity reduce exactly to one cross-parity and one same-parity multiplication equation; three normalized coefficients have exact nonzero interval witnesses."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not been restricted to these four components."),
            ("CERTIFIED","The complete all-m resonance variety has exactly four ten-dimensional linear components over C: two one-fibre-zero planes and the two real mixed sheets with common parity ratio plus or minus sqrt(3)."),
            _second_order(("OPEN","The resonance variety is decomposed, but same-fibre sources and Taub constraints remain unjoined."),("OPEN","Smooth-secular correction is not classified on the four components."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_candidate4_L4_zero_variety","ell2_two_abs_momentum_target_doublet_L3_zero_varieties","ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties","ell2_two_abs_momentum_rank_one_branch_zero_varieties","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This classifies the candidate-4 target-doublet L4 resonance ideal. Together with the separately certified later classes, all 20 fibrewise cross-fibre resonance ideals are now classified; the two-fibre tangent cone, same-fibre, Taub, bounded, smooth-secular, residual, causal and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_target_doublet_l3_zero_varieties",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-1 and candidate-16 closed S1_L times S2 circumference fibres; before final residual quotient", carrier="complete scalar-input target-doublet all-m cross-|n| resonance varieties", degree=2, parity="axial and polar amplitudes on both momentum fibres", ell="input 2 x 2; output L=3", m="all magnetic components through the first binary-quartic transvectant", k="candidate-specific signed |n|=1 and |n|=2 momenta", omega="positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Candidates 1 and 16 remain two separately tuned physical circumference fibres; the shared normal form does not identify their backgrounds."),
            ("CERTIFIED","In both fibres the four target-adjoint rows reduce exactly to two first-transvectant equations, with a real invertible sqrt(3) parity transform."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not been restricted to these determinantal cones."),
            ("CERTIFIED","Each complete all-m resonance variety is one irreducible complex dimension-12 product of two rank-at-most-one 5-by-2 determinantal cones."),
            _second_order(("OPEN","The resonance ideals are complete, but same-fibre sources and Taub constraints remain unjoined."),("OPEN","Smooth-secular correction is not classified on these cones."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_target_doublet_L3_zero_varieties","ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties","ell2_two_abs_momentum_rank_one_branch_zero_varieties","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This classifies candidates 1 and 16 only. Together with the separately certified later classes, all 20 fibrewise cross-fibre resonance ideals are now classified; the two-fibre tangent cone, same-fibre, Taub, bounded, smooth-secular, residual, causal and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_multiplicity_two_l3_zero_varieties",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-6, candidate-10 and candidate-18 closed S1_L times S2 circumference fibres; before final residual quotient", carrier="complete all-m L3 cross-|n| resonance varieties with one multiplicity-two p_extra source branch", degree=2, parity="axial and polar amplitudes", ell="input 2 x 2; output L=3", m="all magnetic components through the first binary-quartic transvectant", k="candidate-specific signed |n|=1 and |n|=2 momenta", omega="positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Candidates 6, 10 and 18 remain three separately tuned circumference fibres; no cross-background mode identification is made."),
            ("CERTIFIED","Exact algebraic-number reduction gives the factors -24 sqrt(2) and -8 sqrt(2), an active parity-pencil square of 384, and one spectator quartic per parity."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not been restricted to these varieties."),
            ("CERTIFIED","Each all-m resonance variety is one irreducible complex dimension-22 product: two six-dimensional rank-one cones times a ten-dimensional spectator affine space."),
            _second_order(("OPEN","The resonance ideals are complete, but same-fibre sources and Taub constraints remain unjoined."),("OPEN","Smooth-secular correction is not classified on these varieties."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties","ell2_two_abs_momentum_rank_one_branch_zero_varieties","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This classifies candidates 6, 10 and 18 only. Together with the separately certified later fibres, all 20 fibrewise cross-fibre resonance ideals are now classified; same-fibre, Taub, bounded, smooth-secular, residual, causal and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_rank_one_branch_l4_zero_varieties",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-8 and candidate-12 closed S1_L times S2 circumference fibres; before final residual quotient", carrier="complete all-m L4 cross-|n| resonance varieties with one multiplicity-two p_extra source branch", degree=2, parity="axial and polar amplitudes", ell="input 2 x 2; output L=4", m="all magnetic components through binary-quartic multiplication", k="candidate-specific signed |n|=1 and |n|=2 momenta", omega="positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Candidates 8 and 12 remain two separately tuned circumference fibres; the shared algebraic type does not identify their backgrounds."),
            ("CERTIFIED","Eight exact algebraic-number identities give squared row ratios 3/40 and 120 with negative signs, leaving one active and one spectator quartic per parity."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not been restricted to these four-component varieties."),
            ("CERTIFIED","Each all-m resonance variety has four complex dimension-20 components in ambient dimension 30: two one-fibre-zero planes and two real mixed sheets, each times a ten-dimensional spectator space."),
            _second_order(("OPEN","The resonance ideals are complete, but same-fibre sources and Taub constraints remain unjoined."),("OPEN","Smooth-secular correction is not classified on these varieties."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_rank_one_branch_zero_varieties","ell2_two_abs_momentum_regular_pencil_L4_zero_varieties","ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This classifies candidates 8 and 12 only. Together with the separately certified candidate-13 prime cone and other fibres, all 20 cross-fibre ideals are now classified; same-fibre, Taub, bounded, smooth-secular, residual, causal and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_regular_pencil_l4_zero_varieties",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-7, candidate-11 and candidate-19 closed S1_L times S2 circumference fibres; before final residual quotient", carrier="complete all-m L4 cross-|n| resonance varieties with one scalar and one multiplicity-two source branch and a target doublet", degree=2, parity="axial and polar amplitudes", ell="input 2 x 2; output L=4", m="all magnetic components through binary-quartic multiplication", k="candidate-specific signed |n|=1 and |n|=2 momenta", omega="positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Candidates 7, 11 and 19 remain three separately tuned circumference fibres; their common regular-pencil geometry does not identify the backgrounds."),
            ("CERTIFIED","Exact rational intervals certify four invertible parity matrices and positive trace, determinant and discriminant for the squared internal pencil on every fibre."),
            ("OPEN","The five stabilizer moment maps and same-fibre quadratic sources have not been restricted to these non-equidimensional varieties."),
            ("CERTIFIED","Each all-m zero variety has exactly six real-supported linear components in ambient dimension 30: one dimension-20 scalar-fibre-zero component and five dimension-10 components, four of them mixed pencil eigenlines."),
            _second_order(("OPEN","The resonance ideals are complete, but same-fibre sources and Taub constraints remain unjoined."),("OPEN","Smooth-secular correction is not classified on these varieties."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_regular_pencil_L4_zero_varieties","ell2_two_abs_momentum_rank_one_branch_zero_varieties","ell2_two_abs_momentum_cross_fibre_amplitude_system","abstract_cone"),
            "This classifies candidates 7, 11 and 19 only. Together with the separately certified candidate-13 prime cone, all 20 cross-fibre ideals are now classified; same-fibre, Taub, bounded, smooth-secular, residual, causal and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_l4_incidence_reduction",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-13 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="complete all-m L4 cross-|n| resonance block with two multiplicity-two p_extra source branches and scalar q_plus targets", degree=2, parity="axial and polar amplitudes", ell="input 2 x 2; output L=4", m="all magnetic components through two binary-octic product equations", k="signed |n|=1 and |n|=2 momenta (1,-2)", omega="positive-frequency SUM channel", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The exact candidate-13 p_extra/p_extra to q_plus collision and its separately tuned circumference fibre are retained without cross-background identification."),
            ("CERTIFIED","All four internal blocks are invertible, exact interval arithmetic gives four distinct nonzero real generalized roots, and an explicit three-root cancellation witness forbids the earlier one-eigenline factorization."),
            ("CERTIFIED","The time-translation Taub form is negative definite on the complete declared pure-extra carrier, so the prime resonance cone meets the common zero of all five stabilizer moment maps only at the origin."),
            ("CERTIFIED","The all-m equations define one prime complex dimension-22 cone in ambient dimension 40. Coordinate-boundary strata are at most dimension 20; all-active torsion strata are at most 21 and splitting-jump strata are at most 20."),
            _second_order(("OBSTRUCTED","Every nonzero real tangent in the candidate-13 pure-extra carrier violates the negative-definite time-translation Taub constraint."),("OBSTRUCTED","Allowing smooth secular propagation terms does not remove the stabilizer adjoint-cokernel pairing."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_candidate13_pure_extra_taub_join","ell2_two_abs_momentum_candidate13_L4_incidence_reduction","ell2_two_abs_momentum_regular_pencil_L4_zero_varieties","ell2_two_abs_momentum_cross_fibre_amplitude_system","taub","abstract_cone"),
            "This is the complete candidate-13 cross-fibre zero-variety theorem and pure-extra Taub no-go. Same-fibre source matrices and the larger mixed Einstein-extra two-fibre cone remain open; causal, residual, observational and quantum lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-13 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="one normalized axial p-primary mode at n=1 plus normalized axial Einstein-minus q-primary modes at n=1 and n=-2; p-primary occupation at n=-2 is zero", degree=2, parity="axial", ell="input ell=2; candidate-13 cross-fibre output L=4", m=0, k="signed momentum integers n=1 and n=-2 with k_n=n*sqrt(rho)", omega="p-primary n=1 and q-minus n=1,-2 positive-frequency shells with conjugates understood", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","At rho=(-250+461 sqrt(10))/2132, the exact p-primary and Einstein-minus frequencies on the n=1,-2 fibres are retained without identifying another circumference background."),
            ("CERTIFIED","The p-primary unit-current direction is positive and the axial Einstein-minus unit-current directions are negative, so their H and P_x occupations can cancel exactly."),
            ("CERTIFIED","The displayed positive occupations make H and P_x vanish; m=0 support and the angular selection rules make J_1,J_2,J_3 vanish."),
            ("CERTIFIED","The candidate-13 p(n=1) times p(n=-2) functionals vanish on the certified second-fibre-zero sheet, and all 21 cross-fibre circumference values are pairwise distinct."),
            _second_order(("OPEN","Same-fibre adjoint-cokernel functionals have not yet been evaluated on the exact mixed witness."),("OPEN","The smooth-secular verdict also awaits the same-fibre source restriction."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_candidate13_mixed_null_witness","ell2_two_abs_momentum_candidate13_pure_extra_taub_join","ell2_two_abs_momentum_cross_fibre_amplitude_system","ell2_two_abs_momentum_isolated_candidates","taub","axial_current","abstract_cone"),
            "This is a nonzero independence and activation witness on one declared axial m=0 mixed carrier. It proves that the pure-extra Taub no-go does not extend after adjoining Einstein-minus modes and that the candidate-13 cross-fibre resonance alone does not decide extension. Same-fibre functionals, the complete mixed cone, bounded and smooth-secular correction, causal propagation, residual observables and quantum claims remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_same_fibre_resonance_census",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-13 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="same-fibre products of q-minus, p-extra and q-plus ell=2 modes on each |n|=1,2 momentum fibre", degree=2, parity="all parity combinations at the shell-arithmetic level", ell="input 2 x 2; outputs L=0,1,2,3,4 kept separate", m="all Clebsch-Gordan-allowed values", k="same-fibre sums K=2*n*sqrt(rho) and unequal-branch differences K=0", omega="positive-positive sums and unequal-branch positive-negative differences; equal-branch zero-frequency products excluded", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All three generic ell=2 branch dispersions are evaluated separately on each candidate-13 |n|=1,2 fibre."),
            ("CERTIFIED","The shell inventory uses the action-derived q-minus, p-extra and q-plus branch dictionary; it makes no new current-sign claim."),
            ("OPEN","The five moment maps are certified elsewhere, but their join to the remaining zero-frequency source matrix is not complete."),
            ("CERTIFIED","All 18 nonzero-frequency same-fibre channels are off shell: 144 exact L=1,...,4 defects exclude zero; L=0 sums use the empty nonzero-Fourier quotient and L=0 differences use the empty homogeneous nonzero-frequency quotient."),
            _second_order(("OPEN","Only equal-branch zero-frequency homogeneous/twist adjoint-cokernel rows remain, but they are not yet evaluated on the mixed carrier."),("OPEN","The smooth-secular verdict awaits the same zero-frequency source restriction."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_candidate13_same_fibre_census","ell2_two_abs_momentum_candidate13_mixed_null_witness","ell2_two_abs_momentum_candidate13_L4_incidence_reduction","abstract_cone"),
            "This is a complete nonzero-frequency same-fibre shell census, not a source-coefficient or tangent-cone theorem. The L=0 K!=0 and K=0 cases use distinct certified quotient theorems. Equal-branch zero-frequency homogeneous/twist sources, their Taub join, bounded and smooth-secular correction, causal propagation, residual observables and quantum claims remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_mixed_bounded_extension",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-13 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="one normalized axial p-primary mode at n=1 plus normalized axial Einstein-minus q-primary modes at n=1 and n=-2; p-primary occupation at n=-2 is zero", degree=2, parity="axial", ell="input ell=2; quadratic outputs L=0,...,4", m=0, k="signed momentum integers n=1 and n=-2 with k_n=n*sqrt(rho)", omega="finite q-minus/p-primary sum, difference and zero-frequency products with conjugates", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The exact candidate-13 circumference, three occupied generic modes and their reality conjugates are retained without cross-background identification."),
            ("CERTIFIED","The action-normalized p-primary and Einstein-minus current signs supply the exact positive occupations used by the mixed witness."),
            ("CERTIFIED","All five persistent stabilizer pairings vanish, but the independent bounded circle-pressure functional R_c is strictly negative."),
            ("CERTIFIED","All 18 nonzero same-fibre channels are off shell; the candidate-13 cross-fibre functional vanishes on the second-fibre-zero plane, and the other 20 collision circumferences are distinct."),
            _second_order(("OBSTRUCTED","R_c<0 has no bounded homogeneous image, despite vanishing moment maps and finite-frequency resonance coefficients."),("CERTIFIED","The complete finite-support smooth theorem supplies a finite secular correction; componentwise pressure-row normalization is not asserted here."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_candidate13_mixed_bounded_extension","candidate13_mixed_pressure_obstruction","ell2_two_abs_momentum_candidate13_same_fibre_census","ell2_two_abs_momentum_candidate13_mixed_null_witness","finite_generic_smooth","abstract_cone"),
            "This certifies one exact axial m=0 mixed tangent as bounded-obstructed and smoothly second-order extendible, not the full candidate-13 mixed cone. Arbitrary phases and polar amplitudes, all-orders integration, causal propagation, residual observables and quantum claims remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.finite_generic_bounded_zero_block",
            _scope(theory="Weyl-Maxwell target", carrier="arbitrary real finite sums of generic ell>=2 p- and q-primary oscillators; generalized-zero inputs excluded", degree=2, parity="axial and polar", ell="all generic input ell>=2 and every quadratically allowed static output L", m="all input m and output M", k="all allowed compact momenta and opposite-momentum K=0 products", omega="equal-shell products with reality conjugates at Omega=0"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every declared input remains in its exact p- or q-primary compact-product shell; this row classifies only K=Omega=0 quadratic outputs."),
            ("CERTIFIED","The complete Hermitian shell blocks define circle pressure R_c=(1/2) sum k_j^2 h_j, including degenerate-polarization cross terms."),
            ("CERTIFIED","The static receiver is the five stabilizer moment maps plus circle pressure; the formal Wilson-acceleration mean covector has identically zero quadratic source."),
            ("CERTIFIED","L=1 contributes only the three lifted rotations, polar L=1 contributes none, and every static L>=2 block is reduced-invertible."),
            _second_order(("CERTIFIED","The complete bounded zero-frequency source is in the reduced image iff mu_H=mu_Px=mu_J1=mu_J2=mu_J3=R_c=0."),("CERTIFIED","In the smooth exponential-polynomial class the zero-frequency pressure row has a secular inverse, leaving only the five stabilizer conditions."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("finite_generic_bounded_zero_block","candidate13_bounded_zero_frequency","complete_finite_smooth","taub","abstract_cone"),
            "This is the complete bounded zero-frequency receiver for finite generic oscillatory inputs. Generalized-zero inputs and all nonzero-frequency resonances are excluded; it is not by itself a complete finite-harmonic cone, all-orders theorem, causal map, residual observable or quantum statement.",
        ),
        _entry(
            "einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_complete_mixed_cone",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-13 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="all generic ell=2 q-minus, p-extra and q-plus coefficients on signed n=1 and n=-2 collision fibres with reality conjugates", degree=2, parity="both axial and polar inputs and all selected output parities", ell="input ell=2; every quadratic output L=0,1,2,3,4", m="all m=-2,...,2 and every allowed output M", k="signed n=1 and n=-2 candidate-13 fibres and their conjugates", omega="all generic branch shells and quadratic signed sums", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The complete finite generic candidate-13 two-fibre carrier is kept on one exact circumference background."),
            ("CERTIFIED","The branch dictionary and stabilizer moment maps use the action-derived reduced current forms; no new quantum sign claim is made."),
            ("CERTIFIED","The bounded zero-frequency receiver is exactly the five stabilizers plus circle pressure R_c; an exact combination of H, P_x and R_c is strictly positive on every nonzero declared tangent."),
            ("CERTIFIED","The bounded nonzero-frequency obstruction is exactly the 18-coefficient prime candidate-13 cross-fibre ideal; all same-fibre and other cross-fibre channels are off shell."),
            _second_order(("CERTIFIED","The bounded cone is exactly {0}; the scalar separator makes the five-stabilizer, R_c and R_13 common-zero formula definite on the real carrier."),("CERTIFIED","The smooth exponential-polynomial cone is exactly the nontrivial common zero of the five stabilizer moment maps."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("ell2_two_abs_momentum_candidate13_complete_mixed_cone","candidate13_scalar_separation_no_go","finite_generic_bounded_zero_block","candidate13_bounded_zero_frequency","candidate13_mixed_pressure_obstruction","ell2_two_abs_momentum_candidate13_mixed_bounded_extension","ell2_two_abs_momentum_candidate13_same_fibre_census","ell2_two_abs_momentum_candidate13_L4_incidence_reduction","finite_generic_smooth","abstract_cone"),
            "This is a complete real bounded-origin and smooth second-order cone theorem on the declared finite generic candidate-13 carrier. The complex zero variety, other collision circumferences, exceptional/global inputs, all-orders, causal, residual, observational and quantum claims remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.candidate13_scalar_separation_no_go",
            _scope(theory="Weyl-Maxwell target", boundaries="candidate-13 closed S1_L times S2 circumference fibre; before final residual quotient", carrier="all generic ell=2 q-minus, p-extra and q-plus coefficients on signed n=1 and n=-2 fibres with reality conjugates", degree=2, parity="axial and polar", ell=2, m="all m=-2,...,2", k="signed n=1,-2 candidate-13 fibres", omega="all q-minus, p-extra and q-plus positive-frequency shells", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},
            ("CERTIFIED","The exact candidate-13 branch shells and signed momentum fibres are retained without cross-background identification."),
            ("CERTIFIED","The q-minus current is negative while the p-extra and q-plus current blocks are positive, in both parities with positive angular Gram form."),
            ("CERTIFIED","D=-(8/(5L))mu_H-(3/(2L sqrt(rho)))mu_Px-(2/rho)R_c has a strictly positive occupation coefficient on every declared branch and fibre."),
            ("NOT_APPLICABLE","The no-go follows already from the scalar charge/pressure receiver; the eighteen finite-frequency coefficients are redundant on its zero set."),
            _second_order(("OBSTRUCTED","Every nonzero real tangent in the declared carrier is bounded-obstructed; the bounded tangent cone is {0}."),("CERTIFIED","The separator does not constrain the smooth-secular cone because R_c has a secular inverse; that cone remains the five-moment-map zero set."),("NO_CERTIFIED_MAP","No background-specific retarded Weyl-Maxwell correction complex is certified.")),
            _evidence("candidate13_scalar_separation_no_go","ell2_two_abs_momentum_candidate13_complete_mixed_cone","candidate13_mixed_pressure_obstruction","standard","axial_current","polar_current","taub"),
            "This exact positivity theorem is real, candidate-13-specific and limited to the declared generic two-fibre carrier. It does not classify the complex zero variety, another circumference, exceptional/global inputs, all-orders integration, causal correction, residual observables, particles or quantum states.",
        ),
        _entry(
            "einstein.ph.wm.interaction.twist_aligned_opposite_momentum_resonance_gate",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference tuned to the displayed allowed nonzero momentum; before final residual quotient", carrier="constant twist position plus paired axisymmetric +/-k Einstein-plus/minus standing waves", degree=2, parity="generic input parity retained; polar extra resonant output", ell="every one fixed integer ell>=2 with output L=2ell", m="m_A=0 inputs and M=0 output", k="one tuned allowed nonzero +/-k pair", omega="q-plus/minus inputs and p-primary sum-frequency output", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The exact q-minus/q-plus dispersions and the polar L=2ell p shell are retained on one declared tuned compact momentum fibre."),
            ("CERTIFIED","The standing-wave densities use the nondegenerate q-branch action forms; the twist-wave column remains action normalized."),
            ("CERTIFIED","Equal +/-k m_A=0 densities and the displayed q-minus/q-plus balance make H,P_x,J_1,J_2,J_3 vanish."),
            ("CERTIFIED","The twist bounded kernel is satisfied and the two q-minus coefficients populate the polar L=2ell,K=0 p shell with nonzero top Gaunt coupling; this independence row does not import the later dynamical matrix."),
            _second_order(("OPEN","Moment maps and twist alignment alone are insufficient to decide bounded extension; the independently certified two-parity matrix and its still-open null-sheet inversion are recorded in later rows."),("CERTIFIED","The complete fixed-(ell,|k|) common-zero cone has a finite smooth exponential-polynomial correction."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("twist_aligned_opposite_momentum_gate","nonzero_k_constant_twist_same_shell"),
            "This is an exact intersection/independence gate, not a bounded obstruction. The later two-parity row certifies the dynamical matrix; this row does not import it. Fixed-L momentum census, multiple |k| fibres and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.symbolic_ell_qminus_self_collision",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference tuned to the displayed allowed nonzero momentum; before final residual quotient", carrier="Einstein-minus q-primary self-products at one fixed ell and momenta +/-k; other primary cross-products excluded", degree=2, parity="arithmetic theorem for either certified input parity; symbolic source coefficient not yet computed", ell="every integer input ell>=2; output L=1,...,2ell plus separately exact L=0 Fourier block", m="axisymmetric m_A=0 input and M=0 top output", k="+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)", omega="positive sum and zero difference of omega_minus", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The exact q-minus dispersion and every exceptional, p-primary and q-primary target shell are retained at symbolic ell."),
            ("CERTIFIED","The input q-primary branch and polar p-primary target use the action-derived shell normalization; no current-sign inference is made."),
            ("NOT_APPLICABLE","This row is a characteristic-shell census on the already declared common-moment carrier, not a new Taub-map theorem."),
            ("CERTIFIED","For every ell>=2 the unique q-minus self-product collision is polar p-primary L=2ell,K=0,Omega=2omega_minus; doubled-momentum and zero-difference shells are excluded exactly."),
            _second_order(("OPEN","This arithmetic row does not import a dynamical verdict; the complete two-parity resonant matrix and its null variety are certified in a separate row, while full bounded inversion on that variety remains open."),("CERTIFIED","The nonzero p-shell collision has the certified finite smooth exponential-polynomial secular inverse."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("symbolic_ell_qminus_self_collision","twist_aligned_opposite_momentum_gate","finite_generic_smooth"),
            "Complete only for q-minus self-product shell arithmetic at one tuned |k| for each ell>=2. The dynamical two-parity matrix is certified in a separate row; full bounded inversion on its null sheets, Q-plus/extra cross-products, multiple |k| joins and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.symbolic_ell_axial_qminus_obstruction",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference tuned separately for each ell; before final residual quotient", carrier="twist-aligned five-moment-map common-zero tangent with axial Einstein-plus/minus waves at +/-k; resonant coefficient from the q-minus self-product", degree=2, parity="axial input; polar p-primary output", ell="every integer input ell>=2; output L=2ell", m="axisymmetric m_A=0 input and M=0 output, certified through the exact highest-weight M=2ell coefficient", k="+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)", omega="input omega_minus and output Omega=2omega_minus", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The axial q-minus input and polar L=2ell p-primary output retain their exact same-background branch, parity, momentum and frequency labels."),
            ("CERTIFIED","The coefficient is evaluated from the action-derived q2 PBW operator and the target adjoint from the self-adjoint polar action Hessian."),
            ("CERTIFIED","The enclosing twist-aligned tangent has H,P_x,J_1,J_2,J_3 equal to zero for every ell>=2."),
            ("CERTIFIED","Highest weight isolates L=2ell without interpolation; the exact axisymmetric pairing is strictly positive because its quadratic-field norm factors positively."),
            _second_order(("OBSTRUCTED","For every ell>=2 the nonzero polar p-shell adjoint functional excludes bounded and finite-quasiperiodic correction on the declared axial common-zero tangent."),("CERTIFIED","The stabilizer moment maps vanish and the finite nonzero-frequency p-shell obstruction has the certified smooth secular inverse."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("symbolic_ell_axial_qminus_obstruction","symbolic_ell_qminus_self_collision","twist_aligned_opposite_momentum_gate","finite_generic_smooth"),
            "Complete only for axial inputs at one separately tuned |k| fibre for each ell>=2. Polar and mixed input coefficients, one fixed circumference across ell, multiple |k| joins, final residual descent and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.twist_aligned_opposite_momentum_bounded_obstruction",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference tuned so k^2=2*sqrt(3)-7/6 is allowed; before final residual quotient", carrier="nonzero aligned constant twist plus axial ell=2,m=0 Einstein-plus/minus waves at +/-k", degree=2, parity="axial inputs and polar output", ell="input ell=2; output L=4", m="input m=0; output M=0", k="+/-sqrt(2*sqrt(3)-7/6); output K=0", omega="q-minus input omega_-^2=29/6; polar p-shell output Omega=2omega_-", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The exact axial q-minus representatives, polar L=4 p-shell target and tuned compact momentum are retained without cross-background identification."),
            ("CERTIFIED","The input occupations use the action-derived q-branch forms and the target adjoints come from the self-adjoint polar action Hessian."),
            ("CERTIFIED","All five stabilizer moment maps vanish and the complete constant-twist-times-wave bounded column is solved on the aligned m_A=0 face."),
            ("CERTIFIED","The direct four-dimensional q-minus +/-k source pairs nontrivially with the second polar p-shell adjoint; no other occupied input pair shares this carrier."),
            _second_order(("OBSTRUCTED","The exact nonzero polar L=4,K=0,Omega=2omega_- adjoint pairing excludes bounded and finite-quasiperiodic corrections."),("CERTIFIED","A finite smooth exponential-polynomial correction with a secular resonant term is certified because all stabilizer moment maps vanish."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("twist_aligned_opposite_momentum_obstruction","twist_aligned_opposite_momentum_gate","finite_generic_smooth"),
            "This is one tuned ell=2 obstruction fixture. The general bounded zero locus, fixed-circumference census, other ell/parities, multiple |k| fibres and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.symbolic_ell_qminus_parity_resonance_matrix",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference tuned separately for each ell; before final residual quotient", carrier="axial and polar Einstein-minus coefficients at opposite tuned compact momenta inside the common-zero construction", degree=2, parity="both input parities; polar and axial p-primary L=2ell outputs kept separate", ell="every integer input ell>=2; output L=2ell", m="axisymmetric input and output, derived through the exact highest-weight coefficient", k="+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)", omega="input omega_minus and output Omega=2omega_minus", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Both q-minus input parities and the polar/axial L=2ell p-primary outputs retain their exact same-background labels."),
            ("CERTIFIED","All three coefficients use the action-derived quadratic PBW slice and the exact action-Hessian p-shell adjoints."),
            ("CERTIFIED","The matrix is evaluated inside the existing opposite-momentum common-zero construction; this row does not broaden its Taub balance."),
            ("CERTIFIED","The three coefficients are nonzero for every ell>=2, and their two equations have exactly two coordinate planes plus two nonzero mixed-parity sheets."),
            _second_order(("OPEN","Off the resonant zero variety bounded correction is obstructed; complete all-channel bounded inversion on the two symbolic mixed sheets is not yet certified."),("CERTIFIED","The finite p-shell resonances admit the certified smooth exponential-polynomial secular inverse once the moment maps vanish."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("symbolic_ell_qminus_parity_matrix","symbolic_ell_axial_qminus_obstruction","symbolic_ell_qminus_self_collision","finite_generic_smooth"),
            "This row classifies only the unique L=2ell q-minus sum-frequency resonance matrix at one separately tuned |k| for each ell>=2. Full bounded inversion on the null sheets, fixed circumference, multiple |k| joins and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.opposite_momentum_ell2_parity_resonance_matrix",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with k^2=2*sqrt(3)-7/6 allowed; before final residual quotient", carrier="axial and polar ell=2,m=0 Einstein-minus coefficients at +/-k inside the twist-aligned common-zero construction", degree=2, parity="both input parities with polar and axial L=4 outputs", ell="input ell=2; output L=4", m="input m=0; output M=0", k="+/-sqrt(2*sqrt(3)-7/6); output K=0", omega="omega_-^2=29/6; output Omega=2omega_-", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The certified axial and polar Einstein-minus representatives are retained on one same-background tuned momentum fibre."),
            ("CERTIFIED","All three direct source blocks use action-normalized target rows and the exact axial/polar p-shell adjoints."),
            ("CERTIFIED","The carrier is embedded in the preceding five-moment-map common-zero construction; this row does not change that balance."),
            ("CERTIFIED","The complete L=4 sum-frequency matrix has nonzero axial, polar and cross coefficients and the displayed exact mixed null face."),
            _second_order(("OPEN","Pure axial and pure polar directions are obstructed, but the mixed L4-null face still requires every remaining output block to vanish or be inverted."),("CERTIFIED","Finite secular inversion remains certified on the five-moment-map zero cone."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("opposite_momentum_ell2_parity_matrix","twist_aligned_opposite_momentum_obstruction","finite_generic_smooth"),
            "This row classifies only the tuned L=4,K=0,Omega=2omega_- resonance matrix. It does not certify a complete bounded extension on the mixed null face or classify other outputs, ell, momentum fibres or higher lifecycles.",
        ),
        _entry(
            "einstein.ph.wm.interaction.symbolic_ell_standard_branch_collision_census",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference tuned separately for each ell; before final residual quotient", carrier="all q-minus/q-plus self and cross products at signed momenta +/-k; no extra-primary inputs", degree=2, parity="over-complete shell arithmetic before parity selection", ell="every integer input ell>=2; target L=0,...,2ell", m="all angular outputs allowed by the product; no coefficient claim", k="+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)", omega="all positive sums and absolute differences of omega_minus and omega_plus", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OPEN","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The q-minus and q-plus standard branches retain their exact same-background dispersions and signed momenta."),
            ("CERTIFIED","This is characteristic-shell arithmetic using the action-derived p/q factors; it makes no new current-sign claim."),
            ("NOT_APPLICABLE","This census does not alter the separately certified common-zero moment-map construction."),
            ("CERTIFIED","Every q-plus-involving sum/difference channel is off shell; the sole standard-branch collision remains the q-minus L=2ell polar p shell."),
            _second_order(("OPEN","The nonzero-frequency standard-branch ledger closes, but the zero-frequency and compatible-source join on the symbolic mixed sheets remains open."),("CERTIFIED","Finite standard-branch sources on the moment-map zero cone admit the certified smooth exponential-polynomial correction."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("symbolic_ell_standard_branch_census","symbolic_ell_qminus_parity_matrix","symbolic_ell_qminus_self_collision","finite_generic_smooth"),
            "Complete only for q-minus/q-plus inputs at one separately tuned |k| per ell. Extra-primary inputs, multiple |k| fibres, the complete bounded source join and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.symbolic_ell_mixed_sheet_bounded_extension",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference tuned separately for each ell; before final residual quotient", carrier="wave-only m=0 q-minus mixed-parity sheet plus equal +/-k q-plus Hamiltonian balance; no twist or extra-primary input", degree=2, parity="both q-minus parities with either common sheet sign; one normalized q-plus multiplicity", ell="every integer ell>=2", m="m=0 relative to the declared axis", k="+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)", omega="q-minus and q-plus branches with real conjugates", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","Every input and output remains on one tuned compact Plebanski-Hacyan fibre with branch, parity and signed momentum retained."),
            ("CERTIFIED","The q-primary density balance and both p-shell adjoint projections use the action-derived normalizations."),
            ("CERTIFIED","Equal signed occupations kill P_x, m=0 kills J_i, and the action-normalized q-plus occupation cancels the q-minus Hamiltonian."),
            ("CERTIFIED","The standard-branch census leaves one collision, and both of its independent adjoint projections vanish on either symbolic mixed sheet."),
            _second_order(("CERTIFIED","The complete bounded adjoint-cokernel criterion supplies a bounded finite-quasiperiodic correction for both sheet signs at every ell>=2."),("CERTIFIED","The bounded correction already belongs to the smooth exponential-polynomial class."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("symbolic_ell_mixed_sheet_extension","symbolic_ell_standard_branch_census","symbolic_ell_qminus_parity_matrix","finite_generic_smooth"),
            "Two explicit wave-only bounded families are certified for each separately tuned ell>=2. The full sheet amplitude cone, extra-primary inputs, fixed circumference, multiple |k| fibres, all-orders integration and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.symbolic_ell_tuned_axisymmetric_bounded_cone",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with circumference tuned separately for each ell; before final residual quotient", carrier="arbitrary m=0 axial/polar q-minus amplitudes at +/-k and action-normalized q-plus balancing occupations; no extra-primary input", degree=2, parity="both q-minus parities and either mixed-sheet sign", ell="every integer ell>=2", m="m=0", k="one tuned +/-k pair", omega="q-minus and q-plus branches", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The same-background q-minus/q-plus branch labels and tuned signed momenta are retained."),
            ("CERTIFIED","The cone uses the action-normalized q-branch occupations and exact p-shell adjoint matrix."),
            ("CERTIFIED","The explicit B_+/- solution gives the sharp nonnegative occupation interval and removes the one-sided planes."),
            ("CERTIFIED","The resonance zero variety and complete standard-branch census leave exactly two mixed components plus the origin."),
            _second_order(("CERTIFIED","The origin plus both mixed sheets in the sharp amplitude interval are necessary and sufficient for bounded correction in the declared carrier."),("CERTIFIED","Every bounded correction is smooth exponential-polynomial."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("symbolic_ell_tuned_axisymmetric_cone","symbolic_ell_mixed_sheet_extension","symbolic_ell_qminus_parity_matrix","opposite_momentum_cone"),
            "Complete only for the tuned m=0 q-minus/q-plus one-|k| carrier. Extra-primary inputs, nonaxisymmetric data, fixed circumference, multiple |k| fibres, all-orders and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.opposite_momentum_ell2_mixed_parity_bounded_extension",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with k^2=2*sqrt(3)-7/6 allowed; before final residual quotient", carrier="one constant twist position, paired m=0 axial/polar Einstein-minus waves and paired normalized Einstein-plus balancing waves", degree=2, parity="mixed axial/polar Einstein-minus input with one Einstein-plus multiplicity", ell="input ell=2; every quadratic output L=0,...,4", m="axisymmetric about the twist axis", k="+/-sqrt(2*sqrt(3)-7/6); outputs K=0,+/-2k", omega="all zero, sum and difference frequencies of the q-minus/q-plus inputs", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All inputs and outputs stay on the same tuned compact Plebanski-Hacyan background and retain branch, parity, momentum and frequency labels."),
            ("CERTIFIED","The q-primary occupations and both L=4 p-primary adjoint rows use the action-derived Lee-Wald/Hessian normalizations."),
            ("CERTIFIED","Equal opposite-momentum occupations kill P_x, axisymmetry kills J_i, and a normalized q-plus occupation cancels the q-minus Hamiltonian deficit."),
            ("CERTIFIED","An 80-row exact over-complete collision census has one shell hit; both independent adjoint projections on it vanish at a_+=sqrt(3)p_+, a_-=sqrt(3)p_-."),
            _second_order(("CERTIFIED","The zero block is exhausted by the five vanishing moment maps, L=0 nonzero Fourier blocks are exact, twist-wave blocks are boundedly removable, and the sole nonzero-frequency resonance cancels; a bounded finite-quasiperiodic correction exists."),("CERTIFIED","The bounded correction is already a smooth exponential-polynomial correction."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("opposite_momentum_ell2_mixed_parity_bounded","opposite_momentum_ell2_parity_matrix","nonzero_k_constant_twist_same_shell","finite_generic_smooth"),
            "This is one tuned nonzero bounded second-order jet, not the full mixed null face or general bounded cone. Other ell, circumference and |k| fibres, exceptional inputs, all-orders integration and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.opposite_momentum_ell2_tuned_axisymmetric_bounded_cone",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with k^2=2*sqrt(3)-7/6 allowed; before final residual quotient", carrier="one constant twist position plus arbitrary m_A=0 axial/polar q-minus amplitudes and normalized q-plus balancing multiplicities at +/-k; no p-primary input", degree=2, parity="both q-minus parities and arbitrary q-plus multiplicity factorization", ell="input ell=2; every quadratic output L=0,...,4", m="m_A=0", k="+/-sqrt(2*sqrt(3)-7/6)", omega="q-minus and q-plus shells", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","The complete carrier stays on one same-background tuned compact fibre with q-plus/q-minus branches and signed momenta retained."),
            ("CERTIFIED","The occupation variables are defined by the action-derived Hermitian q-branch forms; parity orthogonality makes each N_sigma positive on the absolute q-minus form."),
            ("CERTIFIED","H and P_x have a nonnegative q-plus solution exactly when |N_+-N_-|<=r(N_++N_-); J_i vanish on m_A=0."),
            ("CERTIFIED","The two resonance equations have four linear complex components; moment balance removes the two one-sided planes and leaves exactly the sigma=+/- mixed-parity components with a sharp amplitude interval."),
            _second_order(("CERTIFIED","The origin plus the two mixed components with (1-r)/(1+r)<=|p_+|^2/|p_-|^2<=(1+r)/(1-r) are necessary and sufficient for a bounded correction in the declared carrier."),("CERTIFIED","The complete moment cone is smooth-secular extendible, including the bounded subcone."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("opposite_momentum_ell2_tuned_axisymmetric_cone","opposite_momentum_ell2_mixed_parity_bounded","opposite_momentum_ell2_parity_matrix"),
            "Complete only for the tuned ell=2 axisymmetric q-plus/q-minus/constant-twist carrier. Extra p-primary inputs, nonaxisymmetric modes, other fibres, all-orders integration and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.interaction.opposite_momentum_ell2_tuned_all_primary_bounded_cone",
            _scope(theory="Weyl-Maxwell target", boundaries="closed S1_L times S2 with k^2=2*sqrt(3)-7/6 allowed; before final residual quotient", carrier="one constant twist position plus arbitrary m_A=0 q-minus axial/polar and complete q-plus/p-extra multiplicities at +/-k", degree=2, parity="all certified q-minus, q-plus and p-extra multiplicities at m_A=0", ell="input ell=2; every quadratic output L=0,...,4", m="m_A=0", k="+/-sqrt(2*sqrt(3)-7/6)", omega="q-minus, p-extra and q-plus shells", charge_sector="fixed magnetic U(1) bundle P_N with N=2"),
            {"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"CERTIFIED","observational":"OPEN","quantum":"OPEN"},
            ("CERTIFIED","All three primary branches and signed momenta remain distinct on one same-background tuned compact fibre."),
            ("CERTIFIED","The complete positive and negative occupation variables use the action-derived branch forms and retain all m_A=0 multiplicities."),
            ("CERTIFIED","The positive-branch affine moment polytope is nonempty exactly when |N_+-N_-|<=r_e(N_++N_-), with r_e=omega_-/omega_e."),
            ("CERTIFIED","A 140-row exact over-complete census finds no new collision from p-extra inputs; the sole q-minus L4 collision retains the same two-row mixed-parity zero set."),
            _second_order(("CERTIFIED","The origin plus two mixed q-minus sheets with the r_e imbalance interval and complete positive-branch moment polytope are necessary and sufficient for bounded correction."),("CERTIFIED","The bounded cone is contained in the complete fixed-fibre smooth-secular cone."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("opposite_momentum_ell2_tuned_all_primary_cone","opposite_momentum_ell2_tuned_axisymmetric_cone","opposite_momentum_ell2_mixed_parity_bounded"),
            "Complete only for the tuned ell=2 axisymmetric all-primary/constant-twist carrier. Nonaxisymmetric modes, other fibres, multiple |k| carriers, all-orders integration and higher lifecycles remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.global_fixed_ell_k0_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="complete standard globals plus every axial/polar q/p primary in one arbitrary fixed generic ell block", degree=2, parity="homogeneous, axial and polar", ell="one fixed integer ell>=2 with global ell=0,1 data adjoined", m="all wave m=-ell,...,ell and all three real twist components", k=0, omega="generalized zero and every fixed-ell q/p shell"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The carrier contains every q/p primary at one arbitrary fixed ell>=2 and all standard global coordinates."),
            ("CERTIFIED", "The generic-lambda axial and polar pivots are obtained by a direct formal-Legendre-jet tensor calculation, not finite-ell interpolation."),
            ("CERTIFIED", "Every nonzero common H,J_i zero contains an Einstein-minus component; the full homogeneous source separately excludes Q_e."),
            ("CERTIFIED", "The generic pivots remove a,b,d, the independent homogeneous row removes Q_e, and the corrected fixed-ell flat-connection theorem leaves constant twist position A free."),
            _second_order(("CERTIFIED", "The exact bounded cone is stratified: wave=0 retains c,d,W_x,A; every nonzero H,J_i-zero wave retains c,W_x,A and removes a,b,d,Q_e,B."), ("CERTIFIED", "The bounded corrections are smooth finite exponential-polynomial corrections; the unrestricted secular cone is not reclassified."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("complete_global_twist_fixed_ell_bounded", "fixed_ell_constant_twist_bounded_cone", "global_fixed_ell_k0_bounded", "abd_generic_lambda_pivot", "standard_global_bounded", "electric_wilson_transport", "circumference_classification", "taub", "abstract_cone"),
            "The historical A=0 restriction is superseded by the complete fixed-ell constant-twist theorem. This result remains blockwise in one fixed ell at k=0; finite multi-ell, nonzero-momentum, exceptional and higher scopes remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.global_finite_harmonic_k0_bounded_cone",
            _scope(theory="Weyl-Maxwell target", carrier="complete standard globals plus an arbitrary finite sum of generic axial/polar q/p primaries at rest", degree=2, parity="homogeneous, axial and polar", ell="arbitrary finite subset of ell>=2 with global ell=0,1 data adjoined", m="all retained wave m values and all three real twist components", k=0, omega="generalized zero and all retained q/p shells"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The carrier contains every retained q/p primary across an arbitrary finite set of generic ell blocks and every standard global coordinate."),
            ("CERTIFIED", "The action-normalized finite-wave theorem and generic-lambda global pivots retain ell,m,parity and primary-shell separation."),
            ("CERTIFIED", "The total H,J_i equations retain cross-ell cancellations; every nonzero common zero contains an isolated Einstein-minus coefficient, and the homogeneous source separately excludes Q_e."),
            ("CERTIFIED", "Bilinearity reduces A times a finite wave sum to the sum of the independently removable fixed-ell A-wave sources; wave-wave cross-ell products remain separately certified."),
            _second_order(("CERTIFIED", "The exact finite-harmonic cone retains c,d,W_x,A without waves and c,W_x,A over every nonzero total H,J_i-zero wave sum."), ("CERTIFIED", "The bounded correction is a real smooth spatially periodic finite exponential-polynomial sum."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("complete_global_twist_finite_harmonic_k0_bounded", "global_finite_harmonic_k0_bounded", "fixed_ell_constant_twist_bounded_cone", "complete_global_twist_fixed_ell_bounded", "taub", "abstract_cone"),
            "Complete only for arbitrary finite generic ell>=2 sums at k=0. Infinite completion, exceptional inputs, nonzero momentum and higher scopes remain fail-closed.",
        ),
        _entry(
            "einstein.ph.wm.mixed.finite_generic_all_momenta_smooth_cone",
            _scope(theory="Weyl-Maxwell target with all generic Einstein and extra primaries", carrier="arbitrary finite generic-harmonic sum with all compact momentum fibres kept as distinct input and output blocks", degree=2, parity="axial and polar, including cross-parity quadratic outputs", ell="all finite input ell>=2; every Clebsch-Gordan output L=0,...,ell_1+ell_2", m="arbitrary finite input m values and all selected output M", k="arbitrary finite set of allowed 2*pi*n/L values; signed output sums K retained", omega="all signed input-shell sums and differences; finite polynomial prefactors allowed on resonant outputs"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Every input belongs to a certified generic q- or p-primary shell; every quadratic output is retained under its exact (L,M,K,Omega,parity) label."),
            ("CERTIFIED", "The generic branch currents and the five compact stabilizer moment maps are action-normalized on every input fibre."),
            ("CERTIFIED", "After Noether and gauge descent, the complete persistent smooth-secular adjoint cokernel is span{H,P_x,J_1,J_2,J_3}."),
            ("CERTIFIED", "Bounded resonant functionals R_(j,a) are defined on every finite nonzero on-shell output block; their coefficientwise common zero locus remains open."),
            _second_order(("OPEN", "The exact bounded cone formula mu_X=R_(j,a)=0 is certified, but its coefficientwise zero locus has not been solved."), ("CERTIFIED", "For arbitrary finite generic inputs, multiple |k| fibres and all relative phases, mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0 is necessary and sufficient for a real smooth spatially periodic finite exponential-polynomial second-order correction."), open_causal),
            _evidence("finite_generic_smooth", "taub", "abstract_cone"),
            "This is the complete finite generic ell>=2 smooth-secular cone on the compact product. Exceptional/global input modes, the bounded resonance zero locus, infinite harmonic completion, causal/retarded propagation, all-orders integration, final residual states, observables and quantum transfer remain explicit open scopes.",
        ),
        _entry(
            "einstein.ph.wm.complete_finite_harmonic_smooth_cone",
            _scope(theory="complete certified Weyl-Maxwell linear target", carrier="arbitrary finite-support sum of generic q/p primaries, standard/extra ell=1 modes, axial twists and homogeneous charge/holonomy/Jordan data", degree=2, parity="all certified axial, polar and homogeneous sectors", ell="complete certified ell=0, ell=1 and generic ell>=2 inventory", m="all certified multiplicities", k="arbitrary finite set of allowed compact momenta, with generalized-zero global data at k=0", omega="all certified oscillator shells and generalized-zero polynomial blocks; finite polynomial prefactors allowed in the correction"),
            {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The branch dictionary exhausts the declared finite linear input inventory: generic q/p, standard/extra dipoles, twists and homogeneous data."),
            ("CERTIFIED", "Every input block has an action-derived current and the complete direct sum is the carrier for the covariant moment maps."),
            ("CERTIFIED", "The complete smooth adjoint cokernel is exactly span{H,P_x,J_1,J_2,J_3}, paired with the five Taub moment maps."),
            ("CERTIFIED", "The bounded ledger has independent polynomial-growth P_(j,r) and shell-resonance R_(j,a) functionals; its common zero locus is open."),
            _second_order(("OPEN", "The exact bounded formula mu_X=P_(j,r)=R_(j,a)=0 is certified, but its complete common zero locus is not solved."), ("CERTIFIED", "For every finite-support tangent in the complete certified linear inventory, vanishing of the five moment maps is necessary and sufficient for a real smooth spatially periodic finite exponential-polynomial second-order correction."), ("NO_CERTIFIED_MAP", "No background-specific compact-source retarded Weyl-Maxwell complex is certified.")),
            _evidence("complete_finite_smooth", "branch_dictionary", "taub", "abstract_cone"),
            "This is the complete finite-support smooth-secular tangent cone on the compact Plebanski-Hacyan target before final residual quotient. Bounded classification, infinite-mode convergence, causal/retarded propagation, all-orders integration, residual states, observables and quantum transfer remain fail-closed.",
        ),
        _entry(
            "einstein.crosswalk.compact_product_to_asymptotic_or_vacuum_cylinder",
            _scope(theory="crosswalk", background="compact Plebanski-Hacyan <-> asymptotically flat/dS/AdS or vacuum conformal cylinder", boundaries="cross-background boundary/carrier identification", charge_sector="crosswalk", carrier="mode identification map", degree="crosswalk", parity="n/a", ell="n/a", m="n/a", k="n/a", omega="n/a"),
            {axis: "NO_CERTIFIED_MAP" for axis in AXES},
            ("NO_CERTIFIED_MAP", "No dispersion-preserving cross-background map is certified."),
            ("NO_CERTIFIED_MAP", "No Lee-Wald crosswalk is certified."),
            ("NO_CERTIFIED_MAP", "No stabilizer/Taub crosswalk is certified."),
            ("NO_CERTIFIED_MAP", "No resonance crosswalk is certified."),
            _second_order(("NO_CERTIFIED_MAP", "No bounded correction-class crosswalk."), ("NO_CERTIFIED_MAP", "No secular correction-class crosswalk."), ("NO_CERTIFIED_MAP", "No causal/retarded correction-class crosswalk.")),
            [],
            "Compact-product modes must not be called asymptotic gravitons or vacuum-cylinder residual classes without an explicit certified crosswalk.",
        ),
    ]

    superseded = {
        "einstein.ph.wm.interaction.constant_twist_wave_counterexample",
        "einstein.ph.wm.interaction.constant_twist_ell2_extra_position_zero_locus",
        "einstein.ph.wm.interaction.constant_twist_ell2_einstein_position_zero_locus",
        "einstein.ph.wm.interaction.constant_twist_ell2_moment_resonance_cone",
        "einstein.ph.wm.mixed.constant_twist_ell2_complete_bounded_cone",
    }
    regenerated_successors = {
        "einstein.ph.wm.mixed.twist_position_velocity_ell2_complete_bounded_cone",
        "einstein.ph.wm.mixed.twist_circumference_wilson_ell2_complete_bounded_cone",
        "einstein.ph.wm.mixed.d_twist_ell2_complete_bounded_cone",
        "einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone",
    }
    superseded_ell2_aggregates = {
        "einstein.ph.wm.mixed.global_axial_ell2_all_m_minus_extra_bounded_cone",
        "einstein.ph.wm.mixed.global_ell2_all_m_both_parity_bounded_cone",
    }
    reopened_generic_twist_rows: set[str] = set()
    for entry in result:
        identifier = entry["id"]
        if identifier in superseded:
            entry["descriptions"]["nonlinear"] = "OBSTRUCTED"
            entry["mode_data"]["resonance"] = _claim(
                "OBSTRUCTED",
                "Superseded: the asserted nonzero position map came from projecting an L=1 axial carrier against L=2 adjoints. The corrected L=2 projector gives the zero map.",
            )
            entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"] = _claim(
                "OBSTRUCTED",
                "The historical incidence-based verdict is refuted by einstein.ph.wm.interaction.constant_twist_ell2_projector_repair.",
            )
            entry["claim_boundary"] = (
                "SUPERSEDED BY einstein.ph.wm.interaction.constant_twist_ell2_projector_repair. "
                "Retained only as a fail-closed historical row; it must not support a current theorem."
            )
        elif identifier in regenerated_successors:
            entry["descriptions"]["nonlinear"] = "CERTIFIED"
            entry["mode_data"]["resonance"] = _claim(
                "CERTIFIED",
                "The regenerated successor imports the corrected zero constant-position map and retains its independently certified velocity, spectator, d, radion and electric source components according to scope.",
            )
            entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"] = _claim(
                "CERTIFIED",
                {
                    "einstein.ph.wm.mixed.twist_position_velocity_ell2_complete_bounded_cone": "B=0, A is arbitrary, and the complete ell2 wave satisfies mu_H=mu_J1=mu_J2=mu_J3=0.",
                    "einstein.ph.wm.mixed.twist_circumference_wilson_ell2_complete_bounded_cone": "c,W_x,A are arbitrary, B=0, and the complete ell2 wave satisfies mu_H=mu_J1=mu_J2=mu_J3=0.",
                    "einstein.ph.wm.mixed.d_twist_ell2_complete_bounded_cone": "The exact cone is the union of wave=0 with c,d,W_x,A arbitrary and B=0, and wave!=0 with d=B=0, c,W_x,A arbitrary and mu_H=mu_J1=mu_J2=mu_J3=0.",
                    "einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone": "The exact cone is the union of wave=0 with a=b=Q_e=B=0 and c,d,W_x,A arbitrary, and wave!=0 with a=b=d=Q_e=B=0, c,W_x,A arbitrary and mu_H=mu_J1=mu_J2=mu_J3=0.",
                }[identifier],
            )
            entry["mode_data"]["taub_maps"] = _claim(
                "CERTIFIED",
                "The complete wave factor is the common compact stabilizer zero cone mu_H=mu_J1=mu_J2=mu_J3=0; constant twist position adds no equation after the harmonic-type repair.",
            )
            entry["claim_boundary"] = (
                "REGENERATED after einstein.ph.wm.interaction.constant_twist_ell2_projector_repair. "
                "Certified only on this row's declared ell=2,k=0 bounded carrier; other ell/momenta and causal or higher lifecycles remain fail-closed."
            )
        elif identifier in superseded_ell2_aggregates:
            entry["descriptions"]["nonlinear"] = "OBSTRUCTED"
            entry["mode_data"]["resonance"] = _claim(
                "OBSTRUCTED",
                "This historical aggregate imported the mistyped nonzero constant-position map and is superseded by the regenerated complete-global ell2 theorem.",
            )
            entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"] = _claim(
                "OBSTRUCTED",
                "Use einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone for the corrected necessary-and-sufficient cone on this ell2 carrier.",
            )
            entry["claim_boundary"] = (
                "SUPERSEDED BY einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone. "
                "Retained only as a historical aggregate and must not support a current theorem."
            )
        elif identifier in reopened_generic_twist_rows:
            entry["descriptions"]["nonlinear"] = "OPEN"
            entry["mode_data"]["resonance"] = _claim(
                "OPEN",
                "The old constant-twist regression used a mistyped output carrier. This row retains only its twist-independent ingredients until a correctly typed fixed-ell source map is derived.",
            )
            entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"] = _claim(
                "OPEN",
                "The nonzero-constant-twist bounded cone is not classified in this scope after the projector repair.",
            )
            entry["claim_boundary"] = (
                "LIFECYCLE REOPENED for every constant-twist-dependent statement. "
                "The ell=2 corrected spectator theorem does not by itself identify or classify another ell or a finite multi-ell sum."
            )
    return result


def build() -> dict[str, object]:
    records = {name: _load(name) for name in CERTIFICATES}
    if not records["standard"]["classification"]["complete_standard_harmonic_linear_restriction"]:
        raise AssertionError("standard inclusion input lost completeness")
    if not records["taub"]["classification"]["all_nonzero_generic_pure_extra_fixed_bundle_tangents_second_order_obstructed"]:
        raise AssertionError("generic pure-extra Taub input changed")
    harmonic_taub = records["harmonic_taub_sign"]["classification"]
    if not (
        harmonic_taub["generic_extra_all_ell_all_k_both_parities_negative"]
        and harmonic_taub["exceptional_extra_ell1_all_k_both_parities_negative"]
        and harmonic_taub["finite_pure_extra_harmonic_sums_negative"]
        and harmonic_taub["Einstein_q_minus_opposite_sign_all_ell_both_parities"]
        and harmonic_taub["homogeneous_and_twist_solution_cofibers_zero"]
    ):
        raise AssertionError("harmonic Taub-sign stratification changed")
    if harmonic_taub["full_mixed_second_order_cone_classified"] or harmonic_taub["causal_or_quantum_claim"]:
        raise AssertionError("harmonic Taub-sign stratification exceeded its scope")
    harmonic_join = records["harmonic_sign_resonance_join"]["classification"]
    if not (
        harmonic_join["complete_branch_labelled_obstruction_map_joined"]
        and harmonic_join["block_orthogonality_certified"]
        and harmonic_join["bounded_necessity_and_sufficiency_formula_certified"]
        and harmonic_join["smooth_finite_harmonic_cone_certified"]
        and harmonic_join["pure_extra_face_is_origin"]
        and harmonic_join["maximal_generic_k0_global_mixed_bounded_cone_classified"]
    ):
        raise AssertionError("harmonic sign-resonance join changed")
    if (
        harmonic_join["exceptional_generic_global_arbitrary_k_common_zero_classified"]
        or harmonic_join["multiple_abs_momentum_full_cone_classified"]
        or harmonic_join["all_orders_causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("harmonic sign-resonance join exceeded scope")
    if not records["balanced"]["classification"]["complete_second_order_extension_constructed"]:
        raise AssertionError("balanced second-order extension input changed")
    if not records["exceptional_resonance"]["classification"]["complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed"]:
        raise AssertionError("exceptional all-m input changed")
    exceptional_ad = records["exceptional_ad_pivots"]["classification"]
    if not (
        exceptional_ad["a_times_exceptional_leading_pivot_nonzero_both_parities"]
        and exceptional_ad["d_times_exceptional_constant_pivot_nonzero_both_parities"]
        and exceptional_ad["exceptional_times_ell2_extra_difference_collision_open"]
    ):
        raise AssertionError("exceptional a/d pivot input changed")
    if exceptional_ad["complete_exceptional_mixed_bounded_zero_locus_solved"] or exceptional_ad["causal_or_quantum_claim"]:
        raise AssertionError("exceptional a/d pivot theorem exceeded its scope")
    exceptional_difference = records["exceptional_difference_matrix"]["classification"]
    if not (
        exceptional_difference["all_eight_axisymmetric_difference_columns_direct_four_dimensional"]
        and exceptional_difference["six_adjoint_columns_zero"]
        and exceptional_difference["two_adjoint_columns_nonzero"]
        and exceptional_difference["unique_ell2_polar_e2_control_amplitude"]
    ):
        raise AssertionError("exceptional difference matrix changed")
    if exceptional_difference["SO3_all_m_tensor_assembled"] or exceptional_difference["complete_exceptional_mixed_bounded_zero_locus_solved"] or exceptional_difference["causal_or_quantum_claim"]:
        raise AssertionError("exceptional difference matrix exceeded its scope")
    exceptional_ellipse = records["exceptional_resonance_ellipse"]["classification"]
    if not (exceptional_ellipse["axisymmetric_L1_L2_resonance_zero_locus_nonempty"] and exceptional_ellipse["explicit_resonance_ellipse_parameterized"] and exceptional_ellipse["Einstein_minus_balance_required"]):
        raise AssertionError("exceptional resonance ellipse changed")
    if exceptional_ellipse["Hamiltonian_moment_map_zero"] or exceptional_ellipse["complete_second_order_source_solved"] or exceptional_ellipse["causal_or_quantum_claim"]:
        raise AssertionError("exceptional resonance ellipse exceeded its scope")
    exceptional_minus = records["exceptional_minus_frequency_gate"]["classification"]
    if not (
        exceptional_minus["minimal_single_Einstein_minus_H_balance_explicit"]
        and exceptional_minus["mu_H_mu_Px_mu_Ji_all_zero_on_balanced_axisymmetric_fixture"]
        and exceptional_minus["all_Einstein_minus_exceptional_cross_shells_nonresonant"]
        and exceptional_minus["all_Einstein_minus_ell2_control_cross_shells_nonresonant"]
    ):
        raise AssertionError("exceptional Einstein-minus frequency gate changed")
    if exceptional_minus["complete_quadratic_source_solved"] or exceptional_minus["bounded_second_order_extension_certified"] or exceptional_minus["causal_or_quantum_claim"]:
        raise AssertionError("exceptional Einstein-minus frequency gate exceeded its scope")
    exceptional_zero = records["exceptional_zero_source"]["classification"]
    if not (exceptional_zero["mixed_ell_normalization_repaired"] and exceptional_zero["complete_zero_frequency_source_solved"]):
        raise AssertionError("exceptional zero-frequency source changed")
    if exceptional_zero["complete_nonzero_frequency_polynomial_source_solved"] or exceptional_zero["bounded_second_order_extension_certified"] or exceptional_zero["causal_or_quantum_claim"]:
        raise AssertionError("exceptional zero-frequency source exceeded its scope")
    exceptional_obstruction = records["exceptional_bounded_obstruction"]["classification"]
    if not (
        exceptional_obstruction["nonzero_stabilizer_balanced_tangent_explicit"]
        and exceptional_obstruction["complete_zero_frequency_source_solved"]
        and exceptional_obstruction["unique_d_times_Einstein_minus_shell_pairing_nonzero"]
        and exceptional_obstruction["bounded_or_finite_quasiperiodic_extension_obstructed"]
        and exceptional_obstruction["smooth_exponential_polynomial_extension_certified"]
    ):
        raise AssertionError("exceptional bounded obstruction changed")
    if exceptional_obstruction["general_exceptional_mixed_zero_locus_classified"] or exceptional_obstruction["causal_or_quantum_claim"]:
        raise AssertionError("exceptional bounded obstruction exceeded its scope")
    exceptional_single = records["exceptional_single_minus_no_go"]["classification"]
    if not (
        exceptional_single["entire_axisymmetric_resonance_ellipse_covered"]
        and exceptional_single["every_single_m0_Einstein_minus_dressing_ell_ge_2_covered"]
        and exceptional_single["both_dressing_parities_covered"]
        and exceptional_single["stabilizer_balance_possible_but_bounded_extension_obstructed"]
        and exceptional_single["smooth_secular_extension_certified"]
    ):
        raise AssertionError("exceptional single-minus no-go changed")
    if exceptional_single["multiple_minus_modes_or_other_carriers_classified"] or exceptional_single["causal_or_quantum_claim"]:
        raise AssertionError("exceptional single-minus no-go exceeded its scope")
    exceptional_finite = records["exceptional_finite_minus_no_go"]["classification"]
    if not (exceptional_finite["arbitrary_finite_minus_superpositions_covered"] and exceptional_finite["three_minus_shell_resonances_excluded_analytically"] and exceptional_finite["bounded_extension_obstructed"] and exceptional_finite["smooth_secular_extension_certified"]):
        raise AssertionError("exceptional finite-minus no-go changed")
    if exceptional_finite["additional_nonminus_carriers_classified"] or exceptional_finite["infinite_completion_classified"] or exceptional_finite["causal_or_quantum_claim"]:
        raise AssertionError("exceptional finite-minus no-go exceeded its scope")
    exceptional_wiener = records["exceptional_wiener_minus_no_go"]["classification"]
    if not (exceptional_wiener["smooth_wiener_bohr_minus_completion_classified"] and exceptional_wiener["bounded_almost_periodic_extension_obstructed"] and exceptional_wiener["bohr_harmonic_projection_continuous"] and exceptional_wiener["coefficientwise_source_isolation_proved"]):
        raise AssertionError("exceptional Wiener-Bohr no-go changed")
    if exceptional_wiener["maximal_finite_energy_or_sobolev_completion_classified"] or exceptional_wiener["smooth_infinite_secular_extension_classified"] or exceptional_wiener["additional_nonminus_carriers_classified"] or exceptional_wiener["causal_or_quantum_claim"]:
        raise AssertionError("exceptional Wiener-Bohr no-go exceeded its scope")
    exceptional_global = records["exceptional_standard_global_minus_no_go"]["classification"]
    if not (exceptional_global["all_standard_generalized_zero_additions_covered"] and exceptional_global["smooth_wiener_bohr_minus_completion_covered"] and exceptional_global["bounded_extension_obstructed"] and exceptional_global["twist_velocity_and_cubic_jordan_velocity_eliminated"] and exceptional_global["electric_wilson_circumference_and_constant_twist_transport_accounted_for"]):
        raise AssertionError("exceptional standard-global no-go changed")
    if exceptional_global["genuinely_oscillatory_nonminus_carriers_classified"] or exceptional_global["maximal_sobolev_or_finite_energy_completion_classified"] or exceptional_global["smooth_infinite_secular_extension_classified"] or exceptional_global["causal_or_quantum_claim"]:
        raise AssertionError("exceptional standard-global no-go exceeded its scope")
    exceptional_ell1 = records["exceptional_ell1_oscillator_minus_no_go"]["classification"]
    if not (exceptional_ell1["all_k0_physical_and_extra_ell1_oscillator_additions_covered"] and exceptional_ell1["all_ell1_m_and_both_parities_covered"] and exceptional_ell1["ell1_minus_shell_collisions_excluded"] and exceptional_ell1["low_ell_original_and_global_collisions_excluded_exactly"] and exceptional_ell1["bounded_extension_obstructed"]):
        raise AssertionError("exceptional ell1-oscillator no-go changed")
    if exceptional_ell1["generic_ell_ge_2_nonminus_oscillators_classified"] or exceptional_ell1["maximal_sobolev_or_finite_energy_completion_classified"] or exceptional_ell1["smooth_infinite_secular_extension_classified"] or exceptional_ell1["causal_or_quantum_claim"]:
        raise AssertionError("exceptional ell1-oscillator no-go exceeded its scope")
    same_ell_pairs = records["same_ell_generic_pair_minus_nonresonance"]["classification"]
    if not (same_ell_pairs["all_equal_input_ell_at_least_2_covered"] and same_ell_pairs["all_six_unordered_branch_pairs_covered"] and same_ell_pairs["all_sum_and_difference_channels_covered"] and same_ell_pairs["combined_all_generic_input_ell_pairs_minus_nonresonant"]):
        raise AssertionError("same-ell generic pair census changed")
    if same_ell_pairs["exceptional_ell1_times_generic_pairs_classified"] or same_ell_pairs["quadratic_source_coefficients_computed"] or same_ell_pairs["causal_or_quantum_claim"]:
        raise AssertionError("same-ell generic pair census exceeded its scope")
    ell1_generic_pairs = records["ell1_generic_pair_minus_nonresonance"]["classification"]
    if not (ell1_generic_pairs["both_ell1_frequencies_covered"] and ell1_generic_pairs["all_three_generic_branches_covered"] and ell1_generic_pairs["all_sum_and_difference_channels_covered"] and ell1_generic_pairs["complete_k0_oscillator_pair_to_minus_census_closed"]):
        raise AssertionError("ell1-generic pair census changed")
    if ell1_generic_pairs["quadratic_source_coefficients_computed"] or ell1_generic_pairs["nonzero_momentum_classified"] or ell1_generic_pairs["causal_or_quantum_claim"]:
        raise AssertionError("ell1-generic pair census exceeded its scope")
    complete_k0 = records["exceptional_complete_k0_no_go"]["classification"]
    if not (complete_k0["complete_declared_k0_carrier_covered"] and complete_k0["all_standard_globals_covered"] and complete_k0["all_finite_k0_nonminus_oscillators_covered"] and complete_k0["smooth_wiener_bohr_minus_completion_covered"] and complete_k0["bounded_tangent_cone_intersection_empty_over_nonzero_ellipse"]):
        raise AssertionError("complete k0 exceptional no-go changed")
    if complete_k0["maximal_sobolev_or_finite_energy_completion_classified"] or complete_k0["smooth_infinite_secular_extension_classified"] or complete_k0["nonzero_momentum_classified"] or complete_k0["all_orders_integrability"] or complete_k0["causal_or_quantum_claim"]:
        raise AssertionError("complete k0 exceptional no-go exceeded its scope")
    sobolev_bohr = records["exceptional_sobolev_bohr_no_go"]["classification"]
    if not (sobolev_bohr["finite_order_sobolev_bohr_completion_classified"] and sobolev_bohr["strict_extension_beyond_smooth_wiener_domain"] and sobolev_bohr["bounded_uniformly_almost_periodic_sobolev_extension_obstructed"] and sobolev_bohr["continuous_quadratic_source_map_certified"] and sobolev_bohr["continuous_bohr_adjoint_projection_certified"] and sobolev_bohr["complete_declared_k0_carrier_covered"]):
        raise AssertionError("Sobolev-Bohr complete k0 no-go changed")
    if sobolev_bohr["maximal_finite_energy_or_low_regularity_completion_classified"] or sobolev_bohr["smooth_infinite_secular_extension_classified"] or sobolev_bohr["nonzero_momentum_classified"] or sobolev_bohr["causal_or_quantum_claim"]:
        raise AssertionError("Sobolev-Bohr complete k0 no-go exceeded its scope")
    multimomentum = records["finite_multimomentum_divisor"]["classification"]
    if not (multimomentum["arbitrary_two_signed_momentum_integers_covered"] and multimomentum["all_signed_temporal_sum_difference_channels_covered"] and multimomentum["squared_divisor_linear_in_circumference_parameter"] and multimomentum["one_fibre_h0_h4_formulas_recovered"] and multimomentum["finite_nonidentity_exceptional_circumference_set_certified"] and multimomentum["identity_resonant_channels_fail_closed"]):
        raise AssertionError("finite multimomentum divisor changed")
    if multimomentum["quadratic_source_coefficients_computed"] or multimomentum["complete_multifibre_tangent_cone_classified"] or multimomentum["causal_or_quantum_claim"]:
        raise AssertionError("finite multimomentum divisor exceeded its scope")
    symbolic_axial = records["symbolic_ell_axial_qminus_obstruction"]["classification"]
    if not (symbolic_axial["action_derived_q2_used"] and symbolic_axial["highest_weight_projection_exact_without_interpolation"] and symbolic_axial["symbolic_axial_dynamical_adjoint_coefficient_computed"] and symbolic_axial["coefficient_strictly_positive_every_integer_ell_ge_2"] and symbolic_axial["all_ell_tuned_axial_common_zero_tangent_bounded_obstructed"]):
        raise AssertionError("symbolic-ell axial q-minus obstruction changed")
    if symbolic_axial["polar_or_mixed_input_coefficient_computed"] or symbolic_axial["fixed_circumference_or_multiple_abs_momentum_classified"] or symbolic_axial["causal_or_quantum_claim"]:
        raise AssertionError("symbolic-ell axial q-minus obstruction exceeded its scope")
    symbolic_parity = records["symbolic_ell_qminus_parity_matrix"]["classification"]
    if not (symbolic_parity["action_derived_two_parity_matrix_computed"] and symbolic_parity["all_three_coefficients_nonzero_every_integer_ell_ge_2"] and symbolic_parity["complete_resonance_zero_variety_classified"] and symbolic_parity["nonzero_two_momentum_null_sheets_exist_every_integer_ell_ge_2"]):
        raise AssertionError("symbolic-ell two-parity resonance matrix changed")
    if symbolic_parity["general_all_channel_bounded_extension_on_null_sheets"] or symbolic_parity["fixed_circumference_or_multiple_abs_momentum_classified"] or symbolic_parity["causal_or_quantum_claim"]:
        raise AssertionError("symbolic-ell two-parity resonance matrix exceeded its scope")
    standard_census = records["symbolic_ell_standard_branch_census"]["classification"]
    if not (standard_census["all_standard_qminus_qplus_input_pairs_covered"] and standard_census["all_sum_difference_and_K0_K2k_channels_covered"] and standard_census["qplus_involving_characteristic_collisions_excluded"] and standard_census["unique_nonzero_frequency_standard_branch_collision_is_qminus_L2ell_p"]):
        raise AssertionError("symbolic-ell standard-branch collision census changed")
    if standard_census["complete_bounded_second_order_extension_certified"] or standard_census["extra_primary_or_multiple_abs_momentum_inputs_classified"] or standard_census["causal_or_quantum_claim"]:
        raise AssertionError("symbolic-ell standard-branch collision census exceeded its scope")
    mixed_sheet = records["symbolic_ell_mixed_sheet_extension"]["classification"]
    if not (mixed_sheet["both_symbolic_mixed_sheet_signs_covered"] and mixed_sheet["every_integer_ell_ge_2_has_nonzero_bounded_second_order_jet"] and mixed_sheet["complete_standard_branch_quadratic_output_census_used"] and mixed_sheet["five_moment_maps_and_all_bounded_resonant_functionals_vanish"] and mixed_sheet["bounded_correction_exists_by_complete_cokernel_criterion"]):
        raise AssertionError("symbolic-ell mixed-sheet bounded extension changed")
    if mixed_sheet["full_mixed_sheet_amplitude_cone_classified"] or mixed_sheet["extra_primary_or_multiple_abs_momentum_inputs_classified"] or mixed_sheet["all_orders_integrability"] or mixed_sheet["causal_or_quantum_claim"]:
        raise AssertionError("symbolic-ell mixed-sheet bounded extension exceeded its scope")
    tuned_cone = records["symbolic_ell_tuned_axisymmetric_cone"]["classification"]
    if not (tuned_cone["complete_tuned_axisymmetric_standard_branch_bounded_cone_classified"] and tuned_cone["both_mixed_sheet_components_and_origin_included"] and tuned_cone["sharp_action_normalized_amplitude_interval_certified"] and tuned_cone["one_sided_planes_removed_by_moment_positivity"] and tuned_cone["relative_phases_included"]):
        raise AssertionError("symbolic-ell tuned bounded cone changed")
    if tuned_cone["extra_primary_or_multiple_abs_momentum_inputs_classified"] or tuned_cone["all_orders_integrability"] or tuned_cone["causal_or_quantum_claim"]:
        raise AssertionError("symbolic-ell tuned bounded cone exceeded its scope")
    two_fibre = records["ell2_two_abs_momentum_identity_audit"]["classification"]
    if not (two_fibre["complete_cross_abs_momentum_identity_audit"] and two_fibre["all_three_input_primary_branches_covered"] and two_fibre["all_physical_L1_to_L4_target_shells_covered"] and two_fibre["no_identity_resonant_channel"] and two_fibre["generic_circumference_cross_fibre_nonresonance_certified"]):
        raise AssertionError("ell2 two-absolute-momentum identity audit changed")
    if two_fibre["isolated_circumference_source_coefficients_computed"] or two_fibre["complete_two_fibre_tangent_cone_classified"] or two_fibre["causal_or_quantum_claim"]:
        raise AssertionError("ell2 two-absolute-momentum identity audit exceeded its scope")
    candidates = records["ell2_two_abs_momentum_isolated_candidates"]["classification"]
    if not (candidates["all_198_identity_audit_rows_filtered"] and candidates["all_positive_candidates_decided_exactly"] and candidates["unsquared_temporal_sign_test_complete"] and candidates["twenty_one_distinct_admissible_candidates"]):
        raise AssertionError("ell2 two-absolute-momentum candidate ledger changed")
    if candidates["floating_point_sign_decision_used"] or candidates["projected_source_coefficients_computed"] or candidates["complete_two_fibre_tangent_cone_classified"] or candidates["causal_or_quantum_claim"]:
        raise AssertionError("ell2 two-absolute-momentum candidate ledger exceeded its scope")
    scalar_collision = records["collision_scalar_separation"]["classification"]
    if not (
        scalar_collision["all_21_collision_backgrounds_checked_exactly"]
        and scalar_collision["universal_positive_rho_opposite_sign_separator_certified"]
        and scalar_collision["fifteen_strict_scalar_separators_certified"]
        and scalar_collision["fifteen_complete_bounded_generic_cones_are_origin"]
        and scalar_collision["six_positive_farkas_dependences_certified"]
        and scalar_collision["six_scalar_common_zero_sets_nontrivial"]
    ):
        raise AssertionError("collision scalar-separation classification changed")
    if (
        scalar_collision["floating_point_sign_decision_used"]
        or scalar_collision["six_full_resonance_joined_bounded_cones_classified"]
        or scalar_collision["cross_background_mode_identification_made"]
        or scalar_collision["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("collision scalar-separation classification exceeded scope")
    same_fibre = records["same_sign_collision_same_fibre_census"]["classification"]
    if not (
        same_fibre["all_six_same_sign_candidates_checked_exactly"]
        and same_fibre["all_864_target_shell_defects_nonzero"]
        and same_fibre["all_108_same_fibre_temporal_channels_off_shell"]
        and not same_fibre["same_fibre_nonzero_frequency_source_matrices_required"]
        and same_fibre["zero_frequency_receiver_imported_separately"]
    ):
        raise AssertionError("same-sign same-fibre census changed")
    if same_fibre["cross_fibre_resonance_join_classified"] or same_fibre["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign same-fibre census exceeded scope")
    bounded_witnesses = records["same_sign_collision_bounded_witnesses"]["classification"]
    if not (
        bounded_witnesses["all_six_scalar_pressure_null_witnesses_exact"]
        and bounded_witnesses["all_six_rotation_zero_witnesses_exact"]
        and bounded_witnesses["all_six_cross_fibre_resonance_zero_witnesses_exact"]
        and bounded_witnesses["all_six_same_fibre_nonzero_frequency_ledgers_empty"]
        and bounded_witnesses["all_six_nonzero_bounded_points_certified"]
    ):
        raise AssertionError("same-sign bounded witness theorem changed")
    if (
        bounded_witnesses["all_six_complete_bounded_cones_classified"]
        or bounded_witnesses["cross_background_mode_identification_made"]
        or bounded_witnesses["all_orders_integrability"]
        or bounded_witnesses["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("same-sign bounded witness theorem exceeded scope")
    scalar_rays = records["same_sign_scalar_extreme_rays"]["classification"]
    if not (
        scalar_rays["all_positive_rho_same_sign_scalar_cones_have_four_extreme_rays"]
        and scalar_rays["every_extreme_ray_contains_both_q_minus_nodes"]
        and scalar_rays["every_extreme_ray_chooses_one_positive_branch_per_fibre"]
        and scalar_rays["candidates_16_through_21_instantiated_without_background_identification"]
    ):
        raise AssertionError("same-sign scalar extreme-ray theorem changed")
    if scalar_rays["rotation_or_resonance_zero_loci_joined"] or scalar_rays["full_bounded_cones_classified"] or scalar_rays["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign scalar extreme-ray theorem exceeded scope")
    scalar_audit = records["same_sign_scalar_candidate_audit"]["classification"]
    if not (
        scalar_audit["all_six_scalar_occupation_cones_classified"]
        and scalar_audit["all_six_receiver_matrices_rank_three"]
        and scalar_audit["all_120_support_three_minors_nonzero"]
        and scalar_audit["all_90_support_four_circuits_classified"]
        and scalar_audit["four_positive_extreme_rays_per_candidate"]
        and scalar_audit["universal_extreme_support_combinatorics"]
    ):
        raise AssertionError("same-sign candidatewise scalar occupation audit changed")
    if scalar_audit["full_rotation_and_resonance_join_classified"] or scalar_audit["cross_background_mode_identification_made"] or scalar_audit["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign candidatewise scalar occupation audit exceeded scope")
    ray_lifts = records["same_sign_extreme_ray_lifts"]["classification"]
    if not (
        ray_lifts["all_24_scalar_extreme_rays_have_nonzero_bounded_lifts"]
        and ray_lifts["all_rotation_moment_maps_zero_on_lifts"]
        and ray_lifts["all_cross_fibre_resonances_zero_on_lifts"]
        and ray_lifts["all_same_fibre_nonzero_frequency_channels_removable"]
    ):
        raise AssertionError("same-sign extreme-ray lift theorem changed")
    if ray_lifts["arbitrary_nonnegative_sums_of_lifts_classified"] or ray_lifts["six_full_real_bounded_cones_classified"] or ray_lifts["all_orders_integrability"] or ray_lifts["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign extreme-ray lift theorem exceeded scope")
    cone_sections = records["same_sign_scalar_cone_sections"]["classification"]
    if not (
        cone_sections["all_six_complete_scalar_cones_have_bounded_amplitude_sections"]
        and cone_sections["bounded_to_scalar_occupation_projection_surjective"]
        and cone_sections["all_scalar_cone_faces_and_pairwise_ray_sums_covered"]
        and cone_sections["all_rotation_moment_maps_zero_on_sections"]
        and cone_sections["all_cross_and_same_fibre_bounded_functionals_zero_on_sections"]
    ):
        raise AssertionError("same-sign scalar-cone section theorem changed")
    if cone_sections["every_amplitude_over_each_scalar_occupation_bounded"] or cone_sections["six_full_phase_parity_fibres_classified"] or cone_sections["all_orders_integrability"] or cone_sections["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign scalar-cone section theorem exceeded scope")
    fibre_product = records["same_sign_phase_parity_fibre_product"]["classification"]
    if not (
        fibre_product["all_six_bounded_cones_have_exact_necessary_and_sufficient_equational_formulas"]
        and fibre_product["all_six_cross_fibre_complex_resonance_varieties_decomposed"]
        and fibre_product["all_same_fibre_nonzero_frequency_rows_removable"]
        and fibre_product["all_six_scalar_occupation_cones_classified"]
        and fibre_product["all_relative_phases_and_both_parities_retained_in_formula"]
        and fibre_product["all_three_rotation_moment_maps_retained_in_formula"]
    ):
        raise AssertionError("same-sign phase/parity fibre-product theorem changed")
    if fibre_product["all_six_real_hermitian_phase_parity_intersections_decomposed"] or fibre_product["componentwise_topology_or_singular_strata_classified"] or fibre_product["all_orders_integrability"] or fibre_product["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign phase/parity fibre-product theorem exceeded equational scope")
    resonance_faces = records["same_sign_resonance_face_fibres"]["classification"]
    if not (
        resonance_faces["all_six_resonance_fibres_stratified_over_complete_scalar_cones"]
        and resonance_faces["all_optional_branch_zero_faces_identified"]
        and resonance_faces["all_active_complex_component_ledgers_complete"]
        and resonance_faces["real_nonempty_section_on_every_scalar_cone_point"]
        and resonance_faces["bounded_fibre_product_formula_imported"]
    ):
        raise AssertionError("same-sign resonance-face theorem changed")
    if resonance_faces["full_real_connected_component_decomposition"] or resonance_faces["rotation_moment_map_reduction_completed"] or resonance_faces["complete_real_bounded_component_decomposition"] or resonance_faces["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign resonance-face theorem exceeded scope")
    automatic_links = records["same_sign_automatic_face_rotation_links"]["classification"]
    if not (
        automatic_links["candidates_17_through_21_automatic_faces_classified"]
        and automatic_links["all_nonzero_fixed_occupation_rotation_zero_links_nonempty"]
        and automatic_links["all_nonzero_fixed_occupation_rotation_zero_links_connected"]
        and automatic_links["negative_current_factors_handled_as_signed_symplectic_forms"]
    ):
        raise AssertionError("same-sign automatic-face rotation-link theorem changed")
    if automatic_links["active_resonance_strata_classified"] or automatic_links["projectivized_active_component_topology_classified"] or automatic_links["singular_strata_classified"] or automatic_links["all_orders_integrability"] or automatic_links["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign automatic-face rotation-link theorem exceeded scope")
    rotation_singularity = records["same_sign_axisymmetric_rotation_singularity"]["classification"]
    if not (
        rotation_singularity["all_nonzero_axisymmetric_section_points_rotation_critical"]
        and rotation_singularity["rotation_jacobian_rank_exactly_two"]
        and rotation_singularity["origin_rotation_jacobian_rank_zero"]
    ):
        raise AssertionError("same-sign axisymmetric rotation singularity changed")
    if rotation_singularity["implicit_function_regular_seed_available_on_axisymmetric_section"] or rotation_singularity["local_real_zero_set_components_classified"] or rotation_singularity["singular_tangent_cone_classified"] or rotation_singularity["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign axisymmetric rotation singularity exceeded scope")
    rotation_normal_form = records["same_sign_automatic_face_rotation_normal_form"]["classification"]
    if not (
        rotation_normal_form["candidates_17_through_21_automatic_face_normal_forms_classified"]
        and rotation_normal_form["all_aligned_quadratic_normal_forms_indefinite"]
        and rotation_normal_form["all_aligned_quadratic_normal_forms_have_real_nullity_two"]
        and rotation_normal_form["exact_nonaxisymmetric_fixed_occupation_rotation_zero_arc_at_every_axisymmetric_point"]
    ):
        raise AssertionError("same-sign automatic-face rotation normal form changed")
    if rotation_normal_form["automatic_face_axisymmetric_points_isolated"] or rotation_normal_form["full_local_singular_strata_classified"] or rotation_normal_form["active_resonance_components_classified"] or rotation_normal_form["all_orders_integrability"] or rotation_normal_form["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign automatic-face rotation normal form exceeded scope")
    full_internal = records["same_sign_automatic_face_full_internal_rotation_normal_form"]["classification"]
    if not (
        full_internal["candidates_17_through_21_full_internal_normal_forms_classified"]
        and full_internal["all_ray_and_relative_interior_support_strata_classified"]
        and full_internal["all_current_orthogonal_internal_directions_included"]
        and full_internal["full_fixed_occupation_rotation_kernel_inertia_complete_on_automatic_faces"]
    ):
        raise AssertionError("same-sign automatic-face full-internal normal form changed")
    if full_internal["occupation_strata_glued"] or full_internal["active_resonance_components_classified"] or full_internal["all_orders_integrability"] or full_internal["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign automatic-face full-internal normal form exceeded scope")
    full_rotation_normal_form = records["same_sign_automatic_face_full_rotation_normal_form"]["classification"]
    if not (
        full_rotation_normal_form["candidates_17_through_21_complete_fixed_norm_rotation_hessians_classified"]
        and full_rotation_normal_form["all_automatic_face_support_strata_listed"]
        and full_rotation_normal_form["all_axial_polar_internal_directions_included"]
        and full_rotation_normal_form["unquotiented_and_node_phase_quotiented_inertias_certified"]
        and full_rotation_normal_form["all_transverse_rotation_hessians_indefinite"]
    ):
        raise AssertionError("same-sign automatic-face full rotation normal form changed")
    if full_rotation_normal_form["rotation_zero_local_semialgebraic_components_classified"] or full_rotation_normal_form["active_resonance_components_classified"] or full_rotation_normal_form["all_orders_integrability"] or full_rotation_normal_form["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign automatic-face full rotation normal form exceeded scope")
    candidate16_current = records["same_sign_candidate16_active_restricted_current"]["classification"]
    if not (
        candidate16_current["candidate16_active_restricted_current_gate_closed"]
        and candidate16_current["same_sign_definite_restriction_proof"]
        and candidate16_current["complete_axial_polar_internal_spaces_included"]
        and candidate16_current["every_complex_smooth_stratum_symplectic"]
    ):
        raise AssertionError("candidate-16 active restricted-current theorem changed")
    if candidate16_current["rotation_zero_fibre_connected"] or candidate16_current["singular_stratum_moment_map_topology_classified"] or candidate16_current["candidates17_through21_restricted_currents_classified"] or candidate16_current["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-16 active restricted-current theorem exceeded scope")
    candidate16_singular = records["same_sign_candidate16_singular_rotation_zero_fibre"]["classification"]
    if not (
        candidate16_singular["candidate16_complete_singular_locus_classified"]
        and candidate16_singular["two_endpoint_CP4_strata"]
        and candidate16_singular["positive_norm_incidence_resolution_compact_connected_kahler"]
        and candidate16_singular["incidence_resolution_fibres_connected"]
        and candidate16_singular["lifted_rotation_zero_fibre_nonempty"]
        and candidate16_singular["lifted_rotation_zero_fibre_connected"]
    ):
        raise AssertionError("candidate-16 singular rotation-zero theorem changed")
    if candidate16_singular["global_orbifold_claim"] or candidate16_singular["occupation_strata_glued"] or candidate16_singular["all_orders_integrability"] or candidate16_singular["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-16 singular rotation-zero theorem exceeded scope")
    candidate16_gluing = records["same_sign_candidate16_occupation_gluing"]["classification"]
    if not (
        candidate16_gluing["candidate16_projectivized_scalar_base_classified"]
        and candidate16_gluing["candidate16_fixed_occupation_zero_fibres_connected"]
        and candidate16_gluing["candidate16_occupation_projection_proper_surjective"]
        and candidate16_gluing["candidate16_complete_normalized_rotation_zero_link_connected"]
        and candidate16_gluing["candidate16_active_occupation_gluing_closed"]
    ):
        raise AssertionError("candidate-16 occupation gluing changed")
    if candidate16_gluing["origin_adjoined"] or candidate16_gluing["cross_candidate_gluing"] or candidate16_gluing["final_residual_descent"] or candidate16_gluing["all_orders_integrability"] or candidate16_gluing["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-16 occupation gluing exceeded scope")
    linear_sheets = records["same_sign_active_linear_sheet_rotation_links"]["classification"]
    if not (
        linear_sheets["candidate19_four_active_linear_sheets_classified"]
        and linear_sheets["candidate21_two_active_linear_sheets_classified"]
        and linear_sheets["all_six_restricted_currents_nondegenerate"]
        and linear_sheets["all_six_fixed_occupation_rotation_zero_links_connected_componentwise"]
        and linear_sheets["spectator_support_strata_included"]
    ):
        raise AssertionError("active linear-sheet rotation-link theorem changed")
    if linear_sheets["candidate16_singular_active_variety_classified_here"] or linear_sheets["candidates17_18_20_active_varieties_classified"] or linear_sheets["different_active_sheets_identified_by_residual_symmetry"] or linear_sheets["occupation_strata_glued"] or linear_sheets["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("active linear-sheet rotation-link theorem exceeded scope")
    candidate17_20 = records["same_sign_candidate17_20_axisymmetric_restricted_current"]["classification"]
    if not (
        candidate17_20["candidate17_complete_active_scalar_cone_axisymmetric_current_classified"]
        and candidate17_20["candidate20_complete_active_scalar_cone_axisymmetric_current_classified"]
        and candidate17_20["all_four_active_ray_occupation_gaps_exactly_positive"]
        and candidate17_20["axisymmetric_sections_singular"]
        and candidate17_20["restricted_zariski_tangent_currents_nondegenerate"]
    ):
        raise AssertionError("candidate-17/20 axisymmetric restricted-current theorem changed")
    if candidate17_20["full_smooth_locus_restricted_current_classified"] or candidate17_20["rotation_zero_fibre_connected"] or candidate17_20["candidate18_active_variety_classified"] or candidate17_20["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 axisymmetric restricted-current theorem exceeded scope")
    L1_degeneracy = records["same_sign_L1_active_restricted_current_degeneracy"]["classification"]
    if not (
        L1_degeneracy["candidate17_smooth_active_restricted_current_degeneracy"]
        and L1_degeneracy["candidate20_smooth_active_restricted_current_degeneracy"]
        and L1_degeneracy["degeneracy_occurs_inside_each_exact_scalar_cone"]
        and L1_degeneracy["degenerate_points_have_all_five_stabilizer_moment_maps_zero"]
        and L1_degeneracy["degenerate_points_are_bounded_second_order_tangents"]
    ):
        raise AssertionError("candidate-17/20 smooth current-degeneracy theorem changed")
    if L1_degeneracy["global_active_component_symplectic_orbifold"] or L1_degeneracy["proper_moment_map_connected_fibre_theorem_applicable_globally"] or L1_degeneracy["complete_presymplectic_stratification_classified"] or L1_degeneracy["candidate18_active_restricted_current_classified"] or L1_degeneracy["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 smooth current-degeneracy theorem exceeded scope")
    candidate18_degeneracy = records["same_sign_candidate18_active_restricted_current_degeneracy"]["classification"]
    if not (
        candidate18_degeneracy["candidate18_active_restricted_current_degeneracy"]
        and candidate18_degeneracy["two_exact_internal_eigenline_families"]
        and candidate18_degeneracy["degenerate_points_are_smooth_on_the_complete_active_resonance_variety"]
        and candidate18_degeneracy["degenerate_points_have_all_five_stabilizer_moment_maps_zero"]
        and candidate18_degeneracy["degenerate_points_are_bounded_second_order_tangents"]
    ):
        raise AssertionError("candidate-18 smooth current-degeneracy theorem changed")
    if candidate18_degeneracy["candidate18_global_active_component_symplectic_orbifold"] or candidate18_degeneracy["complete_candidate18_degeneracy_divisor_classified"] or candidate18_degeneracy["occupation_strata_glued"] or candidate18_degeneracy["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-18 smooth current-degeneracy theorem exceeded scope")
    active_divisors = records["same_sign_active_presymplectic_divisors"]["classification"]
    if not (
        active_divisors["candidate17_smooth_divisor_classified"]
        and active_divisors["candidate18_smooth_divisor_classified"]
        and active_divisors["candidate20_smooth_divisor_classified"]
        and active_divisors["presymplectic_linear_quotient_on_every_smooth_stratum_classified"]
        and active_divisors["higher_corank_strata_fail_closed_by_determinantal_ideals"]
    ):
        raise AssertionError("same-sign active presymplectic-divisor theorem changed")
    if active_divisors["global_quotient_topology_classified"] or active_divisors["occupation_strata_glued"] or active_divisors["singular_locus_quotient_classified"] or active_divisors["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign active presymplectic-divisor theorem exceeded scope")
    transvectant_singular = records["same_sign_third_transvectant_singular_locus"]["classification"]
    if not (
        transvectant_singular["candidate17_complete_complex_singular_locus_classified"]
        and transvectant_singular["candidate20_complete_complex_singular_locus_classified"]
        and transvectant_singular["both_parity_product_singular_components_classified"]
        and transvectant_singular["singular_incidence_resolution_constructed"]
    ):
        raise AssertionError("third-transvectant singular-locus theorem changed")
    if transvectant_singular["fixed_occupation_real_singular_strata_classified"] or transvectant_singular["node_phase_singular_reduction_classified"] or transvectant_singular["lifted_rotation_singular_reduction_classified"] or transvectant_singular["global_zero_fibre_connected"] or transvectant_singular["occupation_strata_glued"] or transvectant_singular["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("third-transvectant singular-locus theorem exceeded scope")
    candidate18_singular = records["same_sign_candidate18_complex_singular_resolution"]["classification"]
    if not (
        candidate18_singular["candidate18_complete_complex_singular_locus_classified"]
        and candidate18_singular["candidate18_global_complex_incidence_resolution_constructed"]
        and candidate18_singular["ten_positive_spectators_retained"]
    ):
        raise AssertionError("candidate-18 complex singular resolution changed")
    if candidate18_singular["fixed_occupation_real_singular_strata_classified"] or candidate18_singular["node_phase_singular_reduction_classified"] or candidate18_singular["lifted_rotation_singular_reduction_classified"] or candidate18_singular["global_zero_fibre_connected"] or candidate18_singular["occupation_strata_glued"] or candidate18_singular["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-18 complex singular resolution exceeded scope")
    singular_sections = records["same_sign_active_singular_rotation_zero_sections"]["classification"]
    if not (
        singular_sections["candidate17_every_positive_occupation_has_singular_rotation_zero_point"]
        and singular_sections["candidate18_every_positive_occupation_has_singular_rotation_zero_point"]
        and singular_sections["candidate20_every_positive_occupation_has_singular_rotation_zero_point"]
        and not singular_sections["singular_strata_avoidable_by_positive_norms"]
        and not singular_sections["singular_strata_avoidable_by_rotation_zero_condition"]
    ):
        raise AssertionError("active singular rotation-zero sections changed")
    if singular_sections["real_singular_component_decomposition_complete"] or singular_sections["node_phase_singular_quotient_classified"] or singular_sections["lifted_rotation_singular_quotient_classified"] or singular_sections["global_zero_fibre_connected"] or singular_sections["occupation_strata_glued"] or singular_sections["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("active singular rotation-zero sections exceeded scope")
    candidate18_separation = records["same_sign_candidate18_singular_component_separation"]["classification"]
    if not (
        candidate18_separation["candidate18_both_singular_components_rotation_zero_nonempty"]
        and candidate18_separation["candidate18_positive_occupation_singular_components_separated"]
        and candidate18_separation["candidate18_singular_rotation_zero_quotient_at_least_two_components"]
    ):
        raise AssertionError("candidate-18 singular component separation changed")
    if candidate18_separation["candidate18_each_component_connected"] or candidate18_separation["candidate18_full_rotation_zero_fibre_disconnected"] or candidate18_separation["smooth_strata_connect_components_classified"] or candidate18_separation["occupation_strata_glued"] or candidate18_separation["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-18 singular component separation exceeded scope")
    candidate18_bridge = records["same_sign_candidate18_singular_smooth_bridge"]["classification"]
    if not (
        candidate18_bridge["bridge_exists_at_every_positive_occupation_pair"]
        and candidate18_bridge["bridge_interior_complex_smooth"]
        and candidate18_bridge["candidate18_singular_components_joined_in_full_rotation_zero_fibre"]
        and candidate18_bridge["node_phase_actions_free_along_bridge"]
    ):
        raise AssertionError("candidate-18 singular smooth bridge changed")
    if candidate18_bridge["all_singular_points_connected_to_bridge"] or candidate18_bridge["full_rotation_zero_fibre_connected"] or candidate18_bridge["global_leaf_space_classified"] or candidate18_bridge["occupation_strata_glued"] or candidate18_bridge["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-18 singular smooth bridge exceeded scope")
    candidate17_20_incidence = records["same_sign_candidate17_20_singular_component_incidence"]["classification"]
    if not (
        candidate17_20_incidence["candidate17_positive_occupation_singular_component_images_intersect"]
        and candidate17_20_incidence["candidate20_positive_occupation_singular_component_images_intersect"]
        and not candidate17_20_incidence["candidate17_20_component_labels_prove_quotient_separation"]
    ):
        raise AssertionError("candidate-17/20 singular component incidence changed")
    if candidate17_20_incidence["candidate17_20_each_singular_component_connected"] or candidate17_20_incidence["candidate17_20_complete_singular_rotation_zero_quotient_connected"] or candidate17_20_incidence["occupation_strata_glued"] or candidate17_20_incidence["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 singular component incidence exceeded scope")
    candidate17_20_hub = records["same_sign_candidate17_20_double_singular_rotation_zero_fibre"]["classification"]
    if not (
        candidate17_20_hub["candidate17_double_singular_rotation_zero_hub_connected"]
        and candidate17_20_hub["candidate20_double_singular_rotation_zero_hub_connected"]
        and candidate17_20_hub["positive_fixed_occupations_all_covered"]
    ):
        raise AssertionError("candidate-17/20 double-singular connected hub changed")
    if candidate17_20_hub["complete_singular_components_connected"] or candidate17_20_hub["complete_singular_rotation_zero_quotient_connected"] or candidate17_20_hub["occupation_strata_glued"] or candidate17_20_hub["final_residual_descent"] or candidate17_20_hub["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 double-singular connected hub exceeded scope")
    common_square = records["same_sign_candidate17_20_common_square_rotation_quotient"]["classification"]
    if not (
        common_square["one_parity_common_square_fixed_occupation_rotation_quotient_classified"]
        and common_square["candidate17_common_square_rotation_zero_quotient_always_one_point"]
        and common_square["candidate20_rotation_balance_divisor_nonempty"]
        and common_square["candidate20_on_balance_common_square_rotation_zero_quotient_closed_interval"]
    ):
        raise AssertionError("candidate-17/20 common-square rotation quotient changed")
    if common_square["unweighted_occupation_gap_sufficient_for_rotation_imbalance"] or common_square["candidate20_all_positive_occupations_have_point_quotient"] or common_square["complete_two_parity_singular_union_quotient_classified"] or common_square["occupation_strata_glued"] or common_square["final_residual_descent"] or common_square["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 common-square rotation quotient exceeded scope")
    singular_radial = records["same_sign_candidate17_20_singular_radial_contraction"]["classification"]
    if not (
        singular_radial["exact_radial_transfer_identity_certified"]
        and singular_radial["square_factor_vertex_case_included"]
        and singular_radial["candidate20_balance_complete_singular_union_contracts_to_hub"]
        and singular_radial["candidate20_balance_complete_singular_rotation_zero_fibre_connected"]
        and singular_radial["candidate17_phase_real_common_square_sublocus_contracts_to_hub"]
        and singular_radial["candidate20_off_balance_phase_real_common_square_sublocus_contracts_to_hub"]
    ):
        raise AssertionError("candidate-17/20 singular radial contraction changed")
    if singular_radial["candidate17_complete_singular_rotation_zero_fibre_connected"] or singular_radial["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"] or singular_radial["off_balance_nonradial_contraction_no_go"] or singular_radial["occupation_strata_glued"] or singular_radial["final_residual_descent"] or singular_radial["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 singular radial contraction exceeded scope")
    moving_square = records["same_sign_candidate17_20_moving_square_contraction"]["classification"]
    if not (
        moving_square["normalized_cartan_square_moment_image_closed_ball"]
        and moving_square["uniform_kernel_scaling_moving_square_ansatz_classified"]
        and moving_square["alpha_delta_positive_complete_singular_stratum_contracts_to_hub"]
        and moving_square["candidate17_alpha_negative_complete_singular_stratum_contracts_to_hub"]
        and moving_square["candidate20_off_balance_alpha_same_sign_delta_stratum_contracts_to_hub"]
        and moving_square["square_factor_vertex_off_balance_contracts_to_hub"]
        and moving_square["opposite_sign_interior_zero_obstruction_certified"]
        and moving_square["zero_alpha_complete_stratum_contracts_to_hub"]
    ):
        raise AssertionError("candidate-17/20 moving-square contraction changed")
    if moving_square["candidate17_complete_singular_rotation_zero_fibre_connected"] or moving_square["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"] or moving_square["general_nonradial_no_go"] or moving_square["nonuniform_scaling_classified"] or moving_square["occupation_strata_glued"] or moving_square["final_residual_descent"] or moving_square["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 moving-square contraction exceeded scope")
    independent_scaling = records["same_sign_candidate17_20_independent_node_scaling_contraction"]["classification"]
    if not (
        independent_scaling["zero_alpha_uniform_scaling_repair_imported"]
        and independent_scaling["strict_opposite_sign_incidence_necessary"]
        and independent_scaling["strict_opposite_sign_incidence_sufficient"]
        and independent_scaling["fixed_direction_independent_node_scaling_ansatz_classified"]
        and independent_scaling["positive_collinear_incidence_formula_certified"]
        and independent_scaling["one_zero_moment_incidence_formulas_certified"]
        and independent_scaling["nonpositive_collinearity_obstructed_within_ansatz"]
        and independent_scaling["incidence_points_contract_to_connected_hub"]
        and independent_scaling["generic_fixed_direction_opposite_sign_points_obstructed"]
    ):
        raise AssertionError("candidate-17/20 independent-node scaling changed")
    if independent_scaling["candidate17_complete_singular_rotation_zero_fibre_connected"] or independent_scaling["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"] or independent_scaling["general_nonradial_no_go"] or independent_scaling["K_direction_deformation_classified"] or independent_scaling["occupation_strata_glued"] or independent_scaling["final_residual_descent"] or independent_scaling["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 independent-node scaling exceeded scope")
    deformable_incidence = records["same_sign_candidate17_20_deformable_kernel_incidence_normal_form"]["classification"]
    if not (
        deformable_incidence["compactified_T3_kernel_moduli_defined"]
        and deformable_incidence["node_phase_and_lifted_rotation_quotient_defined"]
        and deformable_incidence["singular_stabilizers_and_boundary_occupations_retained"]
        and deformable_incidence["square_moment_path_lifting_certified"]
        and deformable_incidence["strict_opposite_sign_component_incidence_necessary"]
        and deformable_incidence["strict_opposite_sign_component_incidence_sufficient"]
        and deformable_incidence["candidate17_deformable_kernel_component_criterion_certified"]
        and deformable_incidence["candidate20_deformable_kernel_component_criterion_certified"]
        and deformable_incidence["both_strict_sign_boundary_incidence_sets_nonempty"]
    ):
        raise AssertionError("candidate-17/20 deformable-kernel incidence theorem changed")
    if deformable_incidence["every_admissible_component_meets_incidence"] or deformable_incidence["candidate17_complete_singular_rotation_zero_fibre_connected"] or deformable_incidence["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"] or deformable_incidence["global_zero_fibre_connected"] or deformable_incidence["occupation_strata_glued"] or deformable_incidence["final_residual_descent"] or deformable_incidence["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 deformable-kernel incidence theorem exceeded scope")
    deformable_complete = records["same_sign_candidate17_20_deformable_kernel_complete_contraction"]["classification"]
    if not (
        deformable_complete["normalized_spin_two_moment_unit_ball_bound_certified"]
        and deformable_complete["time_reversal_zero_moment_homotopy_certified"]
        and deformable_complete["time_reversal_moment_norm_monotone"]
        and deformable_complete["delta_negative_convex_positive_node_deletion_certified"]
        and deformable_complete["delta_positive_convex_negative_node_deletion_certified"]
        and deformable_complete["every_admissible_component_meets_incidence"]
        and deformable_complete["strict_opposite_sign_complete_deformable_kernel_contraction"]
        and deformable_complete["candidate17_complete_singular_rotation_zero_fibre_connected"]
        and deformable_complete["candidate20_balance_complete_singular_rotation_zero_fibre_connected"]
        and deformable_complete["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"]
        and deformable_complete["candidate20_complete_singular_rotation_zero_fibre_connected"]
        and deformable_complete["all_positive_fixed_active_occupations_covered"]
    ):
        raise AssertionError("candidate-17/20 complete deformable-kernel contraction changed")
    if deformable_complete["candidate17_candidate20_identified"] or deformable_complete["occupation_strata_glued"] or deformable_complete["final_residual_descent"] or deformable_complete["all_orders_integration"] or deformable_complete["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 complete deformable-kernel contraction exceeded scope")
    component_classification = records["same_sign_candidate17_20_component_incidence_classification"]["classification"]
    if not (
        component_classification["candidate17_strict_sign_component_count_one"]
        and component_classification["candidate20_negative_delta_strict_sign_component_count_one"]
        and component_classification["candidate20_positive_delta_strict_sign_component_count_one"]
        and component_classification["every_strict_sign_component_meets_incidence"]
        and component_classification["four_occupation_strata_exhaustive_and_disjoint"]
        and component_classification["zero_node_boundaries_retained"]
        and component_classification["nonfree_orbit_types_retained"]
        and component_classification["singular_stabilizers_retained"]
        and component_classification["fixed_positive_occupation_complete_candidate17_connected"]
        and component_classification["fixed_positive_occupation_complete_candidate20_connected"]
    ):
        raise AssertionError("candidate-17/20 component-incidence classification changed")
    if component_classification["nonincident_component_exists"] or component_classification["candidate17_candidate20_identified"] or component_classification["occupation_strata_glued_across_distinct_total_occupations"] or component_classification["final_residual_descent"] or component_classification["all_mixed_cones_or_evolution_claim"] or component_classification["causal_observer_or_quantum_claim"]:
        raise AssertionError("candidate-17/20 component-incidence classification exceeded scope")
    phase_reduced_divisors = records["same_sign_active_phase_reduced_presymplectic_divisors"]["classification"]
    if not (
        phase_reduced_divisors["candidate17_regular_fixed_occupation_phase_reduced_divisor_classified"]
        and phase_reduced_divisors["candidate18_regular_fixed_occupation_phase_reduced_divisor_classified"]
        and phase_reduced_divisors["candidate20_regular_fixed_occupation_phase_reduced_divisor_classified"]
        and phase_reduced_divisors["common_node_phase_coupling_retained"]
        and phase_reduced_divisors["candidate18_positive_spectators_retained"]
        and phase_reduced_divisors["linear_presymplectic_quotient_on_every_regular_reduced_tangent_classified"]
        and phase_reduced_divisors["constant_corank_local_leaf_quotient_classified"]
    ):
        raise AssertionError("same-sign active phase-reduced divisor theorem changed")
    if phase_reduced_divisors["lifted_rotation_reduction_classified"] or phase_reduced_divisors["global_leaf_space_or_Hausdorff_quotient_classified"] or phase_reduced_divisors["singular_locus_reduction_classified"] or phase_reduced_divisors["occupation_strata_glued"] or phase_reduced_divisors["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign active phase-reduced divisor theorem exceeded scope")
    local_rotation = records["same_sign_active_local_rotation_leaf_descent"]["classification"]
    if not (
        local_rotation["candidate17_local_rotation_leaf_descent_classified"]
        and local_rotation["candidate18_local_rotation_leaf_descent_classified"]
        and local_rotation["candidate20_local_rotation_leaf_descent_classified"]
        and local_rotation["moment_map_basic_on_current_radical"]
        and local_rotation["local_zero_fibre_and_radical_reductions_commute"]
        and not local_rotation["node_phases_identified_with_rotations"]
    ):
        raise AssertionError("same-sign active local rotation-leaf descent changed")
    if local_rotation["global_leaf_space_or_Hausdorff_quotient_classified"] or local_rotation["global_rotation_zero_fibre_connected"] or local_rotation["singular_locus_reduction_classified"] or local_rotation["occupation_strata_glued"] or local_rotation["final_residual_descent"] or local_rotation["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("same-sign active local rotation-leaf descent exceeded scope")
    parity_workload = records["ell2_two_abs_momentum_parity_workload"]["classification"]
    if not (parity_workload["all_twenty_one_candidates_parity_typed"] and parity_workload["all_m_angular_nonvanishing_witnessed"] and parity_workload["odd_L_axisymmetric_fixtures_excluded"] and parity_workload["reduced_source_workload_complete"]):
        raise AssertionError("ell2 two-absolute-momentum parity workload changed")
    if parity_workload["projected_source_coefficients_computed"] or parity_workload["complete_two_fibre_tangent_cone_classified"] or parity_workload["causal_or_quantum_claim"]:
        raise AssertionError("ell2 two-absolute-momentum parity workload exceeded its scope")
    candidate4 = records["ell2_two_abs_momentum_candidate4_obstruction"]["classification"]
    if not (candidate4["candidate_4_exact_source_computed"] and candidate4["frozen_opposite_momentum_fixture_reproduced_exactly"] and candidate4["complete_p_primary_cokernel_paired"] and candidate4["one_pairing_nonzero"] and candidate4["bounded_candidate_4_obstructed"]):
        raise AssertionError("ell2 two-absolute-momentum candidate-4 obstruction changed")
    if candidate4["all_candidate_rows_classified"] or candidate4["causal_or_quantum_claim"]:
        raise AssertionError("ell2 two-absolute-momentum candidate-4 obstruction exceeded its scope")
    triplet_value = records["ell2_two_abs_momentum_axial_qminus_L4_triplet"]
    triplet = triplet_value["classification"]
    if not (
        triplet["complete_axial_qminus_qminus_L4_candidate_triplet_classified"]
        and triplet["qminus_target_pairing_nonzero"]
        and triplet["p_extra_target_pairing_nonzero"]
        and triplet["qplus_target_pairing_nonzero"]
        and triplet["all_three_declared_tangents_bounded_obstructed"]
    ):
        raise AssertionError("ell2 two-absolute-momentum axial q-minus L4 triplet changed")
    witness = triplet_value["q_primary_common_nonzero_witness"]
    if not witness["zero_is_not_a_root"] or witness["constant_term"] == 0:
        raise AssertionError("ell2 two-absolute-momentum q-primary witness lost nonvanishing")
    if triplet["all_axisymmetric_L4_coefficients_classified"] or triplet["causal_or_quantum_claim"]:
        raise AssertionError("ell2 two-absolute-momentum axial q-minus L4 triplet exceeded its scope")
    axial_matrix_value = records["ell2_two_abs_momentum_axial_axial_L4_matrix"]
    axial_matrix = axial_matrix_value["classification"]
    summary = axial_matrix_value["matrix_summary"]
    if not (
        axial_matrix["complete_axial_axial_L4_basis_matrix_classified"]
        and axial_matrix["all_twenty_basis_fixtures_bounded_obstructed"]
        and summary["target_adjoint_coefficients"] == 27
        and summary["zero_target_adjoint_coefficients"] == 1
        and summary["nonzero_target_adjoint_coefficients"] == 26
    ):
        raise AssertionError("ell2 two-absolute-momentum axial-axial L4 matrix changed")
    if (
        axial_matrix["arbitrary_axial_linear_combinations_classified"]
        or axial_matrix["all_axisymmetric_L4_coefficients_classified"]
        or axial_matrix["causal_or_quantum_claim"]
    ):
        raise AssertionError("ell2 two-absolute-momentum axial-axial L4 matrix exceeded its scope")
    polar_matrix_value = records["ell2_two_abs_momentum_polar_polar_L4_matrix"]
    polar_matrix = polar_matrix_value["classification"]
    polar_summary = polar_matrix_value["matrix_summary"]
    if not (
        polar_matrix["complete_polar_polar_L4_basis_matrix_classified"]
        and polar_matrix["all_twenty_basis_fixtures_bounded_obstructed"]
        and polar_summary["target_adjoint_coefficients"] == 27
        and polar_summary["zero_target_adjoint_coefficients"] == 1
        and polar_summary["nonzero_target_adjoint_coefficients"] == 26
        and polar_matrix_value["direct_calibration"]["matches_direct_four_dimensional_source"]
    ):
        raise AssertionError("ell2 two-absolute-momentum polar-polar L4 matrix changed")
    if (
        polar_matrix["arbitrary_polar_linear_combinations_classified"]
        or polar_matrix["all_axisymmetric_L4_coefficients_classified"]
        or polar_matrix["causal_or_quantum_claim"]
    ):
        raise AssertionError("ell2 two-absolute-momentum polar-polar L4 matrix exceeded its scope")
    forward_value = records["ell2_two_abs_momentum_axial_polar_L4_matrix"]
    forward = forward_value["classification"]
    forward_summary = forward_value["matrix_summary"]
    if not (
        forward["complete_ordered_axial_polar_L4_basis_matrix_classified"]
        and forward["all_twenty_basis_fixtures_bounded_obstructed"]
        and forward_summary["target_adjoint_coefficients"] == 27
        and forward_summary["nonzero_target_adjoint_coefficients"] == 27
        and forward_value["direct_calibration"]["exact_match"]
    ):
        raise AssertionError("ordered axial-polar L4 matrix changed")
    if forward["reverse_input_order_matrix_classified"] or forward["arbitrary_cross_parity_linear_combinations_classified"] or forward["causal_or_quantum_claim"]:
        raise AssertionError("ordered axial-polar L4 matrix exceeded its scope")
    reverse_value = records["ell2_two_abs_momentum_polar_axial_L4_matrix"]
    reverse = reverse_value["classification"]
    reverse_summary = reverse_value["matrix_summary"]
    if not (
        reverse["complete_ordered_polar_axial_L4_basis_matrix_classified"]
        and reverse["all_twenty_basis_fixtures_bounded_obstructed"]
        and reverse["all_axisymmetric_L4_basis_coefficients_classified"]
        and reverse_summary["target_adjoint_coefficients"] == 27
        and reverse_summary["nonzero_target_adjoint_coefficients"] == 27
        and reverse_value["graded_symmetry_audit"]["reverse_matrix_obtained_by_explicit_role_substitution"]
        and not reverse_value["graded_symmetry_audit"]["name_based_mode_identification_used"]
    ):
        raise AssertionError("ordered polar-axial L4 matrix changed")
    if reverse["arbitrary_cross_parity_linear_combinations_classified"] or reverse["complete_two_fibre_tangent_cone_classified"] or reverse["causal_or_quantum_claim"]:
        raise AssertionError("ordered polar-axial L4 matrix exceeded its scope")
    l3_value = records["ell2_two_abs_momentum_nonaxisymmetric_L3_matrix"]
    l3 = l3_value["classification"]
    l3_summary = l3_value["matrix_summary"]
    if not (
        l3["complete_nonaxisymmetric_L3_basis_matrix_classified"]
        and l3["all_44_L3_adjoint_coefficients_classified"]
        and l3["all_basis_fixtures_bounded_obstructed"]
        and l3["remaining_nonaxisymmetric_L1_coefficients"] == 12
        and l3_summary["target_adjoint_coefficients"] == 44
        and l3_summary["nonzero_target_adjoint_coefficients"] == 44
        and l3_summary["basis_fixtures_with_nonzero_cokernel_vector"] == 36
    ):
        raise AssertionError("nonaxisymmetric L3 matrix changed")
    completion_value = records["ell2_two_abs_momentum_nonaxisymmetric_L1_L3_completion"]
    completion = completion_value["classification"]
    completion_summary = completion_value["matrix_summary"]
    if not (
        completion["complete_nonaxisymmetric_L1_L3_branch_basis_matrix_classified"]
        and completion["all_56_odd_L_reduced_coefficients_classified"]
        and completion["certified_L3_submatrix_replayed"]
        and completion["all_164_branch_basis_coefficients_classified"]
        and completion_summary["target_adjoint_coefficients"] == 56
        and completion_summary["nonzero_target_adjoint_coefficients"] == 56
        and completion_summary["basis_fixtures_with_nonzero_cokernel_vector"] == 48
    ):
        raise AssertionError("complete nonaxisymmetric L1/L3 matrix changed")
    if (
        completion["arbitrary_amplitude_zero_variety_classified"]
        or completion["complete_two_fibre_tangent_cone_classified"]
        or completion["smooth_secular_classified"]
        or completion["causal_or_quantum_claim"]
    ):
        raise AssertionError("complete branch-basis matrix exceeded its scope")
    assembly_value = records["ell2_two_abs_momentum_cross_fibre_amplitude_system"]
    assembly = assembly_value["classification"]
    assembly_summary = assembly_value["summary"]
    if not (
        assembly["all_certified_cross_fibre_coefficients_lifted_to_all_m_equations"]
        and assembly["physical_circumference_fibres_kept_separate"]
        and assembly["factorized_cross_fibre_resonance_system_certified"]
        and assembly["mandatory_first_fibre_zero_plane_certified"]
        and assembly["mandatory_second_fibre_zero_plane_certified"]
        and assembly_summary["pairwise_distinct_algebraic_circumference_fibres"] == 21
        and assembly_summary["L1_fibres"] == 3
        and assembly_summary["L3_fibres"] == 6
        and assembly_summary["L4_fibres"] == 12
        and assembly_summary["target_parity_adjoint_equations_before_M_expansion"] == 54
        and assembly_summary["ordered_branch_basis_fixtures"] == 128
        and assembly_summary["certified_reduced_internal_coefficients"] == 164
        and assembly_summary["nonzero_reduced_internal_coefficients"] == 162
        and assembly_summary["zero_reduced_internal_coefficients"] == 2
        and assembly_summary["factorized_complex_scalar_magnetic_equations"] == 418
    ):
        raise AssertionError("two-absolute-momentum cross-fibre amplitude system changed")
    if (
        assembly["irreducible_zero_variety_decomposition_classified"]
        or assembly["taub_common_zero_intersection_classified"]
        or assembly["same_fibre_quadratic_sources_classified"]
        or assembly["complete_two_fibre_tangent_cone_classified"]
        or assembly["causal_or_quantum_claim"]
    ):
        raise AssertionError("cross-fibre amplitude system exceeded its scope")
    scalar_l4_value = records["ell2_two_abs_momentum_scalar_L4_zero_varieties"]
    scalar_l4 = scalar_l4_value["classification"]
    scalar_l4_summary = scalar_l4_value["summary"]
    if not (
        scalar_l4["complete_scalar_internal_L4_zero_varieties_classified"]
        and scalar_l4["all_m_mixed_components_classified"]
        and scalar_l4["all_five_r_squared_values_positive_exactly"]
        and scalar_l4_summary["classified_physical_fibres"] == 5
        and scalar_l4_summary["irreducible_components_per_fibre_over_C"] == 4
        and scalar_l4_summary["mixed_components_real_on_declared_coefficient_embedding"] == 10
        and scalar_l4_summary["remaining_cross_fibre_physical_fibres_open"] == 16
    ):
        raise AssertionError("scalar-internal L4 zero varieties changed")
    if (
        scalar_l4["remaining_sixteen_cross_fibre_zero_varieties_classified"]
        or scalar_l4["same_fibre_quadratic_sources_classified"]
        or scalar_l4["taub_common_zero_intersection_classified"]
        or scalar_l4["complete_two_fibre_tangent_cone_classified"]
        or scalar_l4["causal_or_quantum_claim"]
    ):
        raise AssertionError("scalar-internal L4 zero varieties exceeded scope")
    odd_value = records["ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces"]
    odd = odd_value["classification"]
    odd_summary = odd_value["summary"]
    if not (
        odd["all_nine_odd_L_highest_weight_zero_subspaces_certified"]
        and odd["mixed_nonzero_points_certified_on_every_odd_L_fibre"]
        and odd_summary["classified_physical_fibres"] == 9
        and odd_summary["L1_difference_fibres"] == 3
        and odd_summary["L3_sum_fibres"] == 6
        and odd_summary["target_scalar_equations_vanishing"] == 130
        and odd_summary["sum_of_highest_weight_subspace_dimensions_over_C"] == 42
    ):
        raise AssertionError("odd-L highest-weight zero subspaces changed")
    if (
        odd["complete_odd_L_zero_varieties_classified"]
        or odd["same_fibre_quadratic_sources_classified"]
        or odd["taub_common_zero_intersection_classified"]
        or odd["complete_two_fibre_tangent_cone_classified"]
        or odd["causal_or_quantum_claim"]
    ):
        raise AssertionError("odd-L highest-weight witness exceeded scope")
    scalar_l3_value = records["ell2_two_abs_momentum_scalar_L3_zero_variety"]
    scalar_l3 = scalar_l3_value["classification"]
    scalar_l3_zero = scalar_l3_value["zero_variety"]
    if not (
        scalar_l3["candidate_2_scalar_L3_zero_variety_classified"]
        and scalar_l3["all_m_irreducible_decomposition_classified"]
        and scalar_l3["parity_pencil_diagonalized_exactly"]
        and scalar_l3["lambda_squared_positive_exactly"]
        and scalar_l3_zero["ambient_dimension_over_C"] == 20
        and scalar_l3_zero["dimension_over_C"] == 12
        and scalar_l3_zero["irreducible_components_over_C"] == 1
    ):
        raise AssertionError("candidate-2 scalar L3 zero variety changed")
    if (
        scalar_l3["remaining_fifteen_cross_fibre_zero_varieties_classified"]
        or scalar_l3["same_fibre_quadratic_sources_classified"]
        or scalar_l3["taub_common_zero_intersection_classified"]
        or scalar_l3["complete_two_fibre_tangent_cone_classified"]
        or scalar_l3["causal_or_quantum_claim"]
    ):
        raise AssertionError("candidate-2 scalar L3 theorem exceeded scope")
    scalar_l1_value = records["ell2_two_abs_momentum_scalar_L1_zero_varieties"]
    scalar_l1 = scalar_l1_value["classification"]
    scalar_l1_summary = scalar_l1_value["summary"]
    if not (
        scalar_l1["all_three_scalar_L1_zero_varieties_classified"]
        and scalar_l1["all_m_irreducible_decomposition_classified"]
        and scalar_l1["third_transvectant_rank_stratification_certified"]
        and scalar_l1["parity_pencils_diagonalized_exactly"]
        and scalar_l1_summary["classified_physical_fibres"] == 3
        and scalar_l1_summary["dimension_per_fibre_over_C"] == 14
        and scalar_l1_summary["irreducible_components_per_fibre_over_C"] == 1
        and scalar_l1_summary["parent_physical_fibres_outside_this_certificate"] == 18
    ):
        raise AssertionError("scalar L1 zero varieties changed")
    if (
        scalar_l1["other_eighteen_parent_fibre_zero_varieties_classified"]
        or scalar_l1["same_fibre_quadratic_sources_classified"]
        or scalar_l1["taub_common_zero_intersection_classified"]
        or scalar_l1["complete_two_fibre_tangent_cone_classified"]
        or scalar_l1["causal_or_quantum_claim"]
    ):
        raise AssertionError("scalar L1 theorem exceeded scope")
    candidate4_value = records["ell2_two_abs_momentum_candidate4_L4_zero_variety"]
    candidate4 = candidate4_value["classification"]
    candidate4_components = candidate4_value["zero_variety"]["irreducible_components_over_C"]
    if not (
        candidate4["candidate_4_target_doublet_L4_zero_variety_classified"]
        and candidate4["all_m_irreducible_decomposition_classified"]
        and candidate4["two_target_components_reduced_exactly"]
        and len(candidate4_components) == 4
        and all(component["dimension_over_C"] == 10 for component in candidate4_components)
        and candidate4_value["zero_variety"]["all_mixed_components_real"]
    ):
        raise AssertionError("candidate-4 target-doublet L4 zero variety changed")
    if (
        candidate4["other_twenty_parent_fibre_zero_varieties_classified"]
        or candidate4["same_fibre_quadratic_sources_classified"]
        or candidate4["taub_common_zero_intersection_classified"]
        or candidate4["complete_two_fibre_tangent_cone_classified"]
        or candidate4["smooth_secular_classified"]
        or candidate4["causal_or_quantum_claim"]
    ):
        raise AssertionError("candidate-4 target-doublet theorem exceeded scope")
    doublet_l3_value = records["ell2_two_abs_momentum_target_doublet_L3_zero_varieties"]
    doublet_l3 = doublet_l3_value["classification"]
    doublet_l3_summary = doublet_l3_value["summary"]
    if not (
        doublet_l3["both_target_doublet_L3_zero_varieties_classified"]
        and doublet_l3["all_m_irreducible_decomposition_classified"]
        and doublet_l3["target_rows_reduced_exactly"]
        and doublet_l3_summary["classified_physical_fibres"] == 2
        and doublet_l3_summary["dimension_per_fibre_over_C"] == 12
        and doublet_l3_summary["irreducible_components_per_fibre_over_C"] == 1
        and [item["candidate_index"] for item in doublet_l3_value["decompositions"]] == [1, 16]
    ):
        raise AssertionError("target-doublet L3 zero varieties changed")
    if (
        doublet_l3["other_nineteen_parent_fibre_zero_varieties_classified"]
        or doublet_l3["same_fibre_quadratic_sources_classified"]
        or doublet_l3["taub_common_zero_intersection_classified"]
        or doublet_l3["complete_two_fibre_tangent_cone_classified"]
        or doublet_l3["smooth_secular_classified"]
        or doublet_l3["causal_or_quantum_claim"]
    ):
        raise AssertionError("target-doublet L3 theorem exceeded scope")
    multiplicity_l3_value = records["ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties"]
    multiplicity_l3 = multiplicity_l3_value["classification"]
    multiplicity_l3_summary = multiplicity_l3_value["summary"]
    if not (
        multiplicity_l3["all_three_multiplicity_two_L3_zero_varieties_classified"]
        and multiplicity_l3["all_m_irreducible_decomposition_classified"]
        and multiplicity_l3["internal_spectator_split_certified"]
        and multiplicity_l3["real_parity_pencils_diagonalizable"]
        and multiplicity_l3_summary["classified_physical_fibres"] == 3
        and multiplicity_l3_summary["dimension_per_fibre_over_C"] == 22
        and multiplicity_l3_summary["ambient_dimension_per_fibre_over_C"] == 30
        and multiplicity_l3_summary["irreducible_components_per_fibre_over_C"] == 1
        and [item["candidate_index"] for item in multiplicity_l3_value["decompositions"]] == [6, 10, 18]
    ):
        raise AssertionError("multiplicity-two L3 zero varieties changed")
    if (
        multiplicity_l3["other_eighteen_parent_fibre_zero_varieties_classified"]
        or multiplicity_l3["same_fibre_quadratic_sources_classified"]
        or multiplicity_l3["taub_common_zero_intersection_classified"]
        or multiplicity_l3["complete_two_fibre_tangent_cone_classified"]
        or multiplicity_l3["smooth_secular_classified"]
        or multiplicity_l3["causal_or_quantum_claim"]
    ):
        raise AssertionError("multiplicity-two L3 theorem exceeded scope")
    rank_one_l4_value = records["ell2_two_abs_momentum_rank_one_branch_zero_varieties"]
    rank_one_l4 = rank_one_l4_value["classification"]
    rank_one_l4_summary = rank_one_l4_value["summary"]
    if not (
        rank_one_l4["both_multiplicity_two_L4_zero_varieties_classified"]
        and rank_one_l4["all_m_irreducible_decomposition_classified"]
        and rank_one_l4["internal_spectator_split_certified"]
        and rank_one_l4["all_mixed_components_real"]
        and rank_one_l4_summary["classified_physical_fibres"] == 2
        and rank_one_l4_summary["dimension_per_component_over_C"] == 20
        and rank_one_l4_summary["ambient_dimension_per_fibre_over_C"] == 30
        and rank_one_l4_summary["irreducible_components_per_fibre_over_C"] == 4
        and [item["candidate_index"] for item in rank_one_l4_value["decompositions"]] == [8, 12]
    ):
        raise AssertionError("multiplicity-two L4 zero varieties changed")
    if (
        rank_one_l4["other_nineteen_parent_fibre_zero_varieties_classified"]
        or rank_one_l4["same_fibre_quadratic_sources_classified"]
        or rank_one_l4["taub_common_zero_intersection_classified"]
        or rank_one_l4["complete_two_fibre_tangent_cone_classified"]
        or rank_one_l4["smooth_secular_classified"]
        or rank_one_l4["causal_or_quantum_claim"]
    ):
        raise AssertionError("multiplicity-two L4 theorem exceeded scope")
    regular_l4_value = records["ell2_two_abs_momentum_regular_pencil_L4_zero_varieties"]
    regular_l4 = regular_l4_value["classification"]
    regular_l4_summary = regular_l4_value["summary"]
    if not (
        regular_l4["three_regular_pencil_L4_zero_varieties_classified"]
        and regular_l4["all_m_irreducible_decomposition_classified"]
        and regular_l4["four_distinct_real_pencil_roots_certified"]
        and regular_l4_summary["classified_physical_fibres"] == 3
        and regular_l4_summary["irreducible_components_per_fibre_over_C"] == 6
        and regular_l4_summary["component_dimensions_over_C"] == [20, 10, 10, 10, 10, 10]
        and regular_l4_summary["remaining_unclassified_cross_fibre_candidates"] == [13]
        and [item["candidate_index"] for item in regular_l4_value["decompositions"]] == [7, 11, 19]
    ):
        raise AssertionError("regular-pencil L4 zero varieties changed")
    if (
        regular_l4["candidate_13_zero_variety_classified"]
        or regular_l4["same_fibre_quadratic_sources_classified"]
        or regular_l4["taub_common_zero_intersection_classified"]
        or regular_l4["complete_two_fibre_tangent_cone_classified"]
        or regular_l4["smooth_secular_classified"]
        or regular_l4["causal_or_quantum_claim"]
    ):
        raise AssertionError("regular-pencil L4 theorem exceeded scope")
    candidate13_value = records["ell2_two_abs_momentum_candidate13_L4_incidence_reduction"]
    candidate13 = candidate13_value["classification"]
    candidate13_generic = candidate13_value["generic_open_stratum"]
    if not (
        candidate13["candidate_13_exact_pencil_reduction_certified"]
        and candidate13["four_distinct_real_generalized_roots_certified"]
        and candidate13["generic_rank_18_open_component_certified"]
        and candidate13["generic_component_dimension_22_certified"]
        and candidate13["three_root_cancellation_witness_certified"]
        and candidate13["coordinate_boundary_dimension_20_certified"]
        and candidate13["all_active_torsion_strata_certified"]
        and candidate13["all_active_splitting_jump_strata_certified"]
        and candidate13["complete_rank_stratification_certified"]
        and candidate13["full_candidate_13_zero_variety_classified"]
        and candidate13["candidate_13_ideal_prime"]
        and candidate13_generic["linear_rank"] == 18
        and candidate13_generic["kernel_dimension"] == 2
        and candidate13_generic["incidence_dimension_over_C"] == 22
    ):
        raise AssertionError("candidate-13 incidence reduction changed")
    if (
        candidate13["same_fibre_quadratic_sources_classified"]
        or candidate13["taub_common_zero_intersection_classified"]
        or candidate13["complete_two_fibre_tangent_cone_classified"]
        or candidate13["smooth_secular_classified"]
        or candidate13["causal_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 incidence reduction exceeded scope")
    candidate13_taub = records["ell2_two_abs_momentum_candidate13_pure_extra_taub_join"]["classification"]
    if not (
        candidate13_taub["candidate_13_prime_resonance_cone_imported"]
        and candidate13_taub["candidate_13_pure_extra_H_Taub_negative_definite"]
        and candidate13_taub["candidate_13_resonance_Taub_common_zero_is_origin"]
        and candidate13_taub["candidate_13_nonzero_pure_extra_bounded_extension_obstructed"]
        and candidate13_taub["candidate_13_nonzero_pure_extra_smooth_secular_extension_obstructed"]
    ):
        raise AssertionError("candidate-13 pure-extra Taub join changed")
    if (
        candidate13_taub["candidate_13_same_fibre_source_matrices_classified"]
        or candidate13_taub["mixed_Einstein_extra_two_fibre_cone_classified"]
        or candidate13_taub["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 pure-extra Taub join exceeded scope")
    candidate13_mixed = records["ell2_two_abs_momentum_candidate13_mixed_null_witness"]["classification"]
    if not (
        candidate13_mixed["nonzero_real_mixed_witness_certified"]
        and candidate13_mixed["all_five_stabilizer_moment_maps_zero"]
        and candidate13_mixed["candidate_13_cross_fibre_resonance_functionals_zero"]
        and candidate13_mixed["candidate_13_mixed_Taub_resonance_common_zero_nontrivial"]
    ):
        raise AssertionError("candidate-13 mixed null witness changed")
    if (
        candidate13_mixed["same_fibre_resonance_functionals_classified"]
        or candidate13_mixed["complete_mixed_two_fibre_tangent_cone_classified"]
        or candidate13_mixed["bounded_or_smooth_second_order_extension_certified"]
        or candidate13_mixed["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 mixed null witness exceeded scope")
    candidate13_same = records["ell2_two_abs_momentum_candidate13_same_fibre_census"]
    candidate13_same_flags = candidate13_same["classification"]
    if not (
        candidate13_same["channel_count"] == 18
        and candidate13_same["nonzero_defect_count"] == 144
        and candidate13_same_flags["candidate_13_all_nonzero_same_fibre_channels_off_shell"]
        and candidate13_same_flags["ell0_nonzero_fourier_quotient_empty_imported"]
        and candidate13_same_flags["ell0_homogeneous_nonzero_frequency_quotient_empty_imported"]
        and not candidate13_same_flags["same_fibre_nonzero_frequency_source_matrices_required_for_bounded_gate"]
    ):
        raise AssertionError("candidate-13 same-fibre census changed")
    if (
        candidate13_same_flags["same_fibre_zero_frequency_source_matrices_classified"]
        or candidate13_same_flags["mixed_Einstein_extra_taub_intersection_classified"]
        or candidate13_same_flags["complete_mixed_two_fibre_tangent_cone_classified"]
        or candidate13_same_flags["causal_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 same-fibre census exceeded scope")
    candidate13_extension = records["ell2_two_abs_momentum_candidate13_mixed_bounded_extension"]
    candidate13_extension_flags = candidate13_extension["classification"]
    if not (
        not candidate13_extension_flags["candidate_13_mixed_witness_bounded_second_order_extendible"]
        and candidate13_extension_flags["candidate_13_mixed_witness_bounded_second_order_obstructed"]
        and candidate13_extension_flags["candidate_13_mixed_witness_smooth_second_order_extendible"]
        and candidate13_extension_flags["candidate_13_bounded_pressure_functional_nonzero"]
        and candidate13_extension_flags["all_five_zero_frequency_adjoint_pairings_vanish"]
        and candidate13_extension_flags["all_same_fibre_nonzero_frequency_blocks_off_shell"]
        and candidate13_extension_flags["all_cross_fibre_bounded_resonance_functionals_vanish"]
        and not candidate13_extension_flags["complete_finite_block_bounded_source_in_image"]
    ):
        raise AssertionError("candidate-13 mixed bounded extension changed")
    if (
        candidate13_extension_flags["full_candidate_13_mixed_tangent_cone_classified"]
        or candidate13_extension_flags["all_orders_integrability"]
        or candidate13_extension_flags["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 mixed bounded extension exceeded scope")
    bounded_zero = records["finite_generic_bounded_zero_block"]["classification"]
    if not (
        bounded_zero["homogeneous_bounded_dynamical_mean_cokernel_dimension_two"]
        and bounded_zero["circle_pressure_source_functional_certified"]
        and bounded_zero["wilson_acceleration_source_functional_identically_zero"]
        and bounded_zero["five_stabilizers_plus_circle_pressure_complete_on_finite_generic_zero_block"]
        and bounded_zero["bounded_zero_frequency_necessity_and_sufficiency_certified"]
    ):
        raise AssertionError("finite-generic bounded zero-block theorem changed")
    if (
        bounded_zero["generalized_zero_inputs_included"]
        or bounded_zero["nonzero_frequency_resonance_ledger_classified"]
        or bounded_zero["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("finite-generic bounded zero-block theorem exceeded scope")
    candidate13_zero = records["candidate13_bounded_zero_frequency"]["classification"]
    if not (
        candidate13_zero["complete_candidate13_bounded_zero_frequency_receiver_certified"]
        and candidate13_zero["five_stabilizers_plus_circle_pressure_necessary_and_sufficient"]
        and candidate13_zero["additional_zero_frequency_Maxwell_functional_absent"]
        and candidate13_zero["additional_zero_frequency_L1_functional_absent"]
        and candidate13_zero["static_L_at_least_2_functional_absent"]
    ):
        raise AssertionError("candidate-13 bounded zero-frequency specialization changed")
    candidate13_cone = records["ell2_two_abs_momentum_candidate13_complete_mixed_cone"]
    candidate13_cone_flags = candidate13_cone["classification"]
    candidate13_separator_flags = records["candidate13_scalar_separation_no_go"]["classification"]
    if not (
        candidate13_cone_flags["complete_candidate13_bounded_tangent_cone_formula_certified"]
        and candidate13_cone_flags["candidate13_known_bounded_functional_ledger_certified"]
        and candidate13_cone_flags["complete_candidate13_bounded_functional_ledger_certified"]
        and candidate13_cone_flags["complete_candidate13_smooth_tangent_cone_formula_certified"]
        and candidate13_cone_flags["five_stabilizer_pressure_and_eighteen_resonance_functionals_necessary_bounded"]
        and candidate13_cone_flags["five_stabilizer_pressure_and_eighteen_resonance_functionals_sufficient_bounded"]
        and candidate13_cone_flags["five_stabilizer_functionals_necessary_and_sufficient_smooth"]
        and candidate13_cone_flags["same_fibre_nonzero_frequency_source_functionals_absent_after_shell_reduction"]
        and candidate13_cone_flags["pure_extra_face_is_origin"]
        and candidate13_cone_flags["candidate13_complete_bounded_cone_is_origin"]
        and not candidate13_cone_flags["nonzero_mixed_bounded_point_exists"]
        and candidate13_cone_flags["nonzero_mixed_bounded_point_nonexistence_certified"]
        and candidate13_cone_flags["nonzero_mixed_smooth_point_certified"]
        and candidate13_cone_flags["real_algebraic_component_decomposition_classified"]
        and candidate13_separator_flags["exact_rational_Farkas_functional_certified"]
        and candidate13_separator_flags["strictly_positive_on_every_declared_branch_fibre_parity_and_m"]
        and candidate13_separator_flags["candidate13_complete_bounded_cone_is_origin"]
    ):
        raise AssertionError("candidate-13 complete mixed cone changed")
    if (
        candidate13_cone_flags["all_orders_integrability"]
        or candidate13_cone_flags["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 complete mixed cone exceeded scope")
    if l3["arbitrary_amplitude_zero_variety_classified"] or l3["causal_or_quantum_claim"]:
        raise AssertionError("nonaxisymmetric L3 matrix exceeded its scope")
    if not records["exceptional_cofiber"]["classification"]["exceptional_solution_cofiber_certified"]:
        raise AssertionError("exceptional solution-cofiber input changed")
    if not records["exceptional_nonzero_k_cofiber"]["classification"]["nonzero_k_exceptional_solution_cofiber_certified"]:
        raise AssertionError("exceptional nonzero-k solution-cofiber input changed")
    if not records["twist_independence"]["classification"]["nonzero_adjoint_cokernel_witness_certified"]:
        raise AssertionError("twist independence witness changed")
    if not records["d_completion"]["classification"]["d_cross_adjoint_map_invertible_in_both_parities"]:
        raise AssertionError("d-cross parity completion changed")
    d_full_time = records["d_full_time"]["classification"]
    if not (
        d_full_time["full_time_d_ell2_extra_leading_polynomial_classified"]
        and d_full_time["polar_e2_d_extra_t_coefficient_nonzero"]
        and d_full_time["old_d_constant_adjoint_isomorphism_retained"]
    ):
        raise AssertionError("full-time d polynomial repair changed")
    if d_full_time["old_d_result_was_complete_bounded_column"]:
        raise AssertionError("old d constant projection was over-promoted")
    ad_zero = records["ad_polynomial_zero"]["classification"]
    if not (
        ad_zero["complete_a_d_ell2_extra_cross_polynomial_ideal_classified"]
        and ad_zero["four_radion_amplitude_products_forced_zero"]
        and ad_zero["d_times_second_polar_amplitude_forced_zero"]
        and ad_zero["old_nonzero_extra_common_zero_cone_survives_repair"]
    ):
        raise AssertionError("repaired a/d polynomial zero locus changed")
    if ad_zero["complete_bounded_cone_solved"]:
        raise AssertionError("a/d polynomial theorem over-promoted the bounded cone")
    if not records["abd_matrix"]["classification"]["every_parity_polarization_abd_polynomial_chain_rank_three"]:
        raise AssertionError("a,b,d resonance-matrix input changed")
    if not records["homogeneous_twist_matrix"]["classification"]["complete_homogeneous_twist_bounded_resonance_matrix"]:
        raise AssertionError("complete homogeneous/twist matrix input changed")
    if not records["aligned_twist_extra_face"]["classification"]["nonzero_simultaneous_stabilizer_and_bounded_resonance_zero_face"]:
        raise AssertionError("aligned twist--extra compatibility face changed")
    if records["aligned_twist_extra_face"]["classification"]["bounded_second_order_correction_constructed"]:
        raise AssertionError("aligned compatibility face was over-promoted")
    if not records["complete_global_extra_cone"]["classification"]["complete_common_zero_locus_in_declared_nonzero_extra_carrier"]:
        raise AssertionError("complete homogeneous/twist--extra common-zero cone changed")
    if records["complete_global_extra_cone"]["classification"]["bounded_second_order_right_inverse_constructed"]:
        raise AssertionError("necessary common-zero cone was over-promoted to sufficiency")
    if not records["global_extra_bounded_obstruction"]["classification"]["bounded_or_finite_quasiperiodic_correction_obstructed"]:
        raise AssertionError("global--extra bounded obstruction changed")
    if records["global_extra_bounded_obstruction"]["classification"]["smooth_exponential_polynomial_correction_constructed"]:
        raise AssertionError("bounded obstruction over-promoted the smooth class")
    if not records["global_extra_smooth_extension"]["classification"]["smooth_exponential_polynomial_second_order_correction_exists"]:
        raise AssertionError("global--extra smooth extension changed")
    if records["global_extra_smooth_extension"]["classification"]["bounded_correction_exists"]:
        raise AssertionError("smooth extension over-promoted the bounded class")
    if not records["global_extra_smooth_extension"]["classification"]["coefficient_explicit_correction_printed"]:
        raise AssertionError("complete smooth coefficient ledger was lost")
    complete_global_ell2 = records["complete_global_ell2_bounded"]["classification"]
    if not (
        complete_global_ell2["complete_declared_global_ell2_extra_carrier_covered"]
        and complete_global_ell2["bounded_tangent_cone_classified"]
        and complete_global_ell2["bounded_cone_equals_standard_global_cone"]
        and complete_global_ell2["all_nonzero_ell2_extra_directions_bounded_obstructed"]
    ):
        raise AssertionError("complete global+ell2-extra bounded cone changed")
    if complete_global_ell2["other_harmonics_classified"]:
        raise AssertionError("global+ell2 theorem over-promoted other harmonics")
    minus_resonance = records["abd_axial_minus"]["classification"]
    if not (
        minus_resonance["direct_four_dimensional_source_rows_computed"]
        and minus_resonance["bounded_cross_ideal_classified"]
        and minus_resonance["nonzero_minus_forces_a_b_d_zero"]
    ):
        raise AssertionError("axial Einstein-minus global resonance changed")
    general_fixtures = records["abd_general_ell_minus_fixtures"]["classification"]
    if not (
        general_fixtures["ell2_and_ell3_complete_triangular_pivots_direct"]
        and general_fixtures["ell4_leading_b_pivots_direct"]
        and general_fixtures["candidate_functional_laws_reconstructed"]
    ):
        raise AssertionError("multi-ell Einstein-minus pivot fixtures changed")
    if general_fixtures["general_ell_pivot_theorem"]:
        raise AssertionError("multi-ell fixtures over-promoted the general-ell theorem")
    aligned_global_wave = records["aligned_global_minus_extra_bounded"]["classification"]
    if not (
        aligned_global_wave["complete_declared_aligned_carrier_covered"]
        and aligned_global_wave["bounded_zero_locus_necessary_and_sufficient"]
        and aligned_global_wave["opposite_sign_wave_branch_survives_global_adjoining"]
        and aligned_global_wave["electric_taub_cancellation_bounded_obstructed"]
    ):
        raise AssertionError("aligned global minus-extra bounded cone changed")
    if aligned_global_wave["polar_or_all_m_input_classified"]:
        raise AssertionError("aligned global-wave theorem over-promoted all m or polar input")
    axial_bounded = records["axial_all_m_bounded"]["classification"]
    if not (
        axial_bounded["all_m_axial_ell2_bounded_cone_classified"]
        and axial_bounded["zero_L1_constant_right_inverse_explicit"]
        and axial_bounded["prior_polynomial_Jordan_caveat_removed"]
    ):
        raise AssertionError("axial all-m bounded completion changed")
    global_axial = records["global_axial_all_m_bounded"]["classification"]
    if not (
        global_axial["all_wave_m_and_both_axial_extra_polarizations_included"]
        and global_axial["SO3_shell_promotion_certified"]
        and global_axial["A_arbitrary_wave_branch_withdrawn"]
        and global_axial["A_zero_wave_subcone_certified"]
    ):
        raise AssertionError("corrected global axial all-m bounded cone changed")
    if global_axial["complete_declared_global_axial_all_m_carrier_covered"] or global_axial["bounded_zero_locus_necessary_and_sufficient"]:
        raise AssertionError("global axial arbitrary-A product was re-promoted")
    if global_axial["polar_input_classified"]:
        raise AssertionError("global axial theorem over-promoted polar input")
    twist_counterexample = records["constant_twist_wave_counterexample"]["classification"]
    if not (
        twist_counterexample["A_arbitrary_wave_branch_refuted"]
        and twist_counterexample["nonzero_adjoint_pairing_certified"]
    ):
        raise AssertionError("constant-twist wave counterexample changed")
    twist_repair = records["constant_twist_ell2_projector_repair"]
    if not (
        twist_repair["classification"]["harmonic_type_mismatch_repaired"]
        and twist_repair["classification"]["old_constant_twist_counterexample_refuted"]
        and twist_repair["classification"]["constant_twist_position_is_bounded_spectator_on_complete_ell2_wave_cone"]
        and twist_repair["classification"]["corrected_bounded_zero_locus_necessary_and_sufficient"]
        and twist_repair["corrected_position_maps"]["Einstein_plus_minus"] == "zero"
        and twist_repair["corrected_position_maps"]["extra"] == "zero"
    ):
        raise AssertionError("constant-twist ell2 projector repair changed")
    if twist_repair["classification"]["other_ell_or_momentum_classified"] or twist_repair["classification"]["causal_or_quantum_claim"]:
        raise AssertionError("constant-twist projector repair exceeded its declared scope")
    twist_zero_locus = records["constant_twist_extra_position_zero_locus"]
    if not (
        twist_zero_locus["classification"]["complete_nonzero_A_ell2_extra_position_resonance_kernel_classified"]
        and twist_zero_locus["classification"]["all_m_and_all_four_extra_multiplicities_included"]
        and twist_zero_locus["complete_zero_locus"]["kernel_positive_frequency_complex_dimension"] == 12
        and twist_zero_locus["complete_zero_locus"]["operator_rank"] == 8
    ):
        raise AssertionError("constant-twist extra-shell position zero locus changed")
    if twist_zero_locus["classification"]["simultaneous_moment_and_all_branch_resonance_zero_locus_classified"]:
        raise AssertionError("extra-shell twist zero locus over-promoted the mixed wave cone")
    twist_einstein_zero_locus = records["constant_twist_einstein_position_zero_locus"]
    if not (
        twist_einstein_zero_locus["classification"]["both_Einstein_q_primary_twist_position_maps_classified"]
        and twist_einstein_zero_locus["classification"]["each_parity_incidence_matrix_invertible"]
        and twist_einstein_zero_locus["projection_theorem"]["combined_q_primary_kernel_positive_frequency_complex_dimension"] == 4
        and twist_einstein_zero_locus["projection_theorem"]["combined_q_primary_operator_rank"] == 16
    ):
        raise AssertionError("constant-twist Einstein-shell position zero locus changed")
    if twist_einstein_zero_locus["classification"]["simultaneous_moment_and_all_branch_resonance_zero_locus_classified"]:
        raise AssertionError("Einstein-shell twist zero locus over-promoted the mixed wave cone")
    twist_moment_cone = records["constant_twist_ell2_moment_resonance_cone"]
    if not (
        twist_moment_cone["classification"]["complete_nonzero_A_ell2_twist_position_resonance_kernel_intersected_with_H_J"]
        and twist_moment_cone["classification"]["both_Einstein_shells_and_complete_extra_shell_included"]
        and twist_moment_cone["classification"]["necessary_and_sufficient_common_zero_equations"]
        and twist_moment_cone["classification"]["nonaxisymmetric_common_zero_witness_certified"]
        and twist_moment_cone["common_zero_cone"]["generic_smooth_stratum_real_dimension"] == 28
    ):
        raise AssertionError("constant-twist ell2 moment/resonance cone changed")
    if twist_moment_cone["classification"]["bounded_full_second_order_equation_solved_on_common_cone"]:
        raise AssertionError("moment/resonance cone over-promoted bounded second order")
    twist_complete = records["constant_twist_ell2_complete_bounded_cone"]["classification"]
    if not (
        twist_complete["simultaneous_moment_and_all_branch_resonance_zero_locus_classified"]
        and twist_complete["complete_constant_twist_plus_ell2_wave_carrier_covered"]
        and twist_complete["bounded_zero_locus_necessary_and_sufficient"]
        and twist_complete["nonaxisymmetric_nonzero_A_survivor_exhibited"]
    ):
        raise AssertionError("complete constant-twist ell2 bounded cone changed")
    if twist_complete["twist_velocity_or_other_global_tangents_classified"] or twist_complete["other_ell_or_nonzero_momentum_classified"]:
        raise AssertionError("constant-twist ell2 cone exceeded its declared carrier")
    twist_position_velocity = records["twist_position_velocity_ell2_complete_bounded_cone"]["classification"]
    if not (
        twist_position_velocity["complete_twist_position_velocity_plus_ell2_wave_carrier_covered"]
        and twist_position_velocity["twist_velocity_forced_zero_in_bounded_class"]
        and twist_position_velocity["bounded_zero_locus_necessary_and_sufficient"]
        and twist_position_velocity["nonaxisymmetric_nonzero_position_survivor_retained"]
    ):
        raise AssertionError("twist-position/velocity ell2 bounded cone changed")
    if twist_position_velocity["other_homogeneous_tangents_classified"] or twist_position_velocity["unrestricted_smooth_secular_cone_classified"]:
        raise AssertionError("twist-position/velocity theorem exceeded its declared carrier or correction class")
    spectator_cone = records["twist_circumference_wilson_ell2_complete_bounded_cone"]["classification"]
    if not (
        spectator_cone["complete_c_Wx_A_B_plus_ell2_wave_carrier_covered"]
        and spectator_cone["circumference_and_Wilson_are_exact_bounded_spectators"]
        and spectator_cone["bounded_zero_locus_necessary_and_sufficient"]
    ):
        raise AssertionError("c/Wx twist-wave product cone changed")
    if spectator_cone["radion_circumference_velocity_or_electric_tangents_classified"]:
        raise AssertionError("spectator theorem promoted a dynamical homogeneous direction")
    d_cone = records["d_twist_ell2_complete_bounded_cone"]["classification"]
    if not (d_cone["complete_d_c_Wx_A_B_plus_ell2_carrier_covered"] and d_cone["bounded_stratified_zero_locus_necessary_and_sufficient"] and d_cone["nonzero_wave_forces_d_zero"] and d_cone["static_d_branch_retained"]):
        raise AssertionError("d/twist ell2 bounded cone changed")
    if d_cone["radion_or_electric_tangent_classified"]:
        raise AssertionError("d theorem promoted radion or electric data")
    full_global_ell2 = records["complete_global_twist_ell2_bounded_cone"]["classification"]
    if not (full_global_ell2["complete_standard_global_twist_plus_ell2_k0_carrier_covered"] and full_global_ell2["bounded_zero_locus_necessary_and_sufficient"] and full_global_ell2["older_partial_global_ell2_row_superseded"]):
        raise AssertionError("complete global/twist ell2 cone changed")
    if full_global_ell2["other_ell_or_nonzero_momentum_classified"] or full_global_ell2["causal_or_quantum_claim"]:
        raise AssertionError("complete global/twist ell2 theorem exceeded its scope")
    fixed_ell_twist = records["fixed_ell_constant_twist_factorization"]["classification"]
    if not (fixed_ell_twist["all_fixed_ell_all_m_factorization_certified"] and fixed_ell_twist["all_m_problem_reduced_to_finite_multiplicity_matrices"]):
        raise AssertionError("fixed-ell twist factorization changed")
    if fixed_ell_twist["complete_fixed_ell_constant_twist_cone_classified"] or fixed_ell_twist["causal_or_quantum_claim"]:
        raise AssertionError("fixed-ell twist reduction exceeded its scope")
    fixed_ell_zero = records["fixed_ell_constant_twist_zero_map"]["classification"]
    if not (
        fixed_ell_zero["generic_ell_Einstein_multiplicity_matrices_zero"]
        and fixed_ell_zero["generic_ell_extra_multiplicity_matrix_zero"]
        and fixed_ell_zero["all_fixed_ell_all_m_same_shell_resonance_zero"]
    ):
        raise AssertionError("fixed-ell constant-twist zero map changed")
    if fixed_ell_zero["bounded_fixed_ell_constant_twist_cone_complete"] or fixed_ell_zero["causal_or_quantum_claim"]:
        raise AssertionError("fixed-ell zero map exceeded its same-shell scope")
    fixed_ell_bounded = records["fixed_ell_constant_twist_bounded_cone"]["classification"]
    if not (
        fixed_ell_bounded["every_fixed_ell_neighbor_output_invertible"]
        and fixed_ell_bounded["every_fixed_ell_constant_twist_bounded_product_cone_certified"]
        and fixed_ell_bounded["all_m_both_parities_all_qp_primaries_included"]
    ):
        raise AssertionError("fixed-ell constant-twist bounded cone changed")
    if fixed_ell_bounded["finite_multi_ell_twist_cone_classified"] or fixed_ell_bounded["causal_or_quantum_claim"]:
        raise AssertionError("fixed-ell bounded cone exceeded its declared scope")
    complete_fixed_global = records["complete_global_twist_fixed_ell_bounded"]["classification"]
    if not (
        complete_fixed_global["every_fixed_generic_ell_complete_global_bounded_cone_classified"]
        and complete_fixed_global["all_standard_globals_all_m_both_parities_all_qp_branches_included"]
        and complete_fixed_global["bounded_zero_locus_necessary_and_sufficient"]
        and complete_fixed_global["constant_twist_position_free_on_wave_stratum"]
    ):
        raise AssertionError("complete fixed-ell global/twist cone changed")
    if complete_fixed_global["finite_multi_ell_twist_cone_classified"] or complete_fixed_global["causal_or_quantum_claim"]:
        raise AssertionError("complete fixed-ell global theorem exceeded its scope")
    complete_finite_global = records["complete_global_twist_finite_harmonic_k0_bounded"]["classification"]
    if not (
        complete_finite_global["arbitrary_finite_generic_ell_complete_global_bounded_cone_classified"]
        and complete_finite_global["constant_twist_position_free_on_wave_stratum"]
        and complete_finite_global["bounded_zero_locus_necessary_and_sufficient"]
    ):
        raise AssertionError("complete finite-harmonic global successor changed")
    if complete_finite_global["infinite_harmonic_completion_classified"] or complete_finite_global["causal_or_quantum_claim"]:
        raise AssertionError("finite-harmonic successor exceeded its scope")
    if not records["global_self_coefficients"]["classification"]["complete_aligned_global_self_source_classified"]:
        raise AssertionError("global self coefficient input changed")
    if not records["extra_self_coefficients"]["classification"]["complete_C4_extra_self_source_coefficient_explicit"]:
        raise AssertionError("extra self coefficient input changed")
    finite_generic = records["finite_generic_smooth"]["classification"]
    if not (
        finite_generic["arbitrary_finite_generic_harmonic_sums_classified_smooth_global"]
        and finite_generic["multiple_absolute_momentum_fibres_classified_smooth_global"]
        and finite_generic["complete_reduced_adjoint_cokernel_decomposition_certified"]
    ):
        raise AssertionError("finite generic smooth-secular theorem changed")
    if finite_generic["bounded_resonance_zero_locus_solved"]:
        raise AssertionError("finite generic theorem over-promoted the bounded cone")
    complete_finite = records["complete_finite_smooth"]["classification"]
    if not (
        complete_finite["complete_certified_linear_input_inventory_included"]
        and complete_finite["exceptional_and_global_inputs_included"]
        and complete_finite["complete_finite_harmonic_smooth_tangent_cone_classified"]
    ):
        raise AssertionError("complete finite-harmonic smooth theorem changed")
    if complete_finite["bounded_common_zero_locus_solved"]:
        raise AssertionError("complete finite theorem over-promoted the bounded cone")
    standard_global_bounded = records["standard_global_bounded"]["classification"]
    if not (
        standard_global_bounded["complete_standard_generalized_zero_polynomial_ideal_classified"]
        and standard_global_bounded["complete_standard_generalized_zero_bounded_cone_classified"]
        and standard_global_bounded["universal_b_twist_velocity_and_Qe_a_elimination_on_complete_finite_carrier"]
    ):
        raise AssertionError("standard global bounded theorem changed")
    if standard_global_bounded["complete_finite_bounded_common_zero_locus_solved"]:
        raise AssertionError("standard global theorem over-promoted the complete bounded cone")
    electric_wilson = records["electric_wilson_transport"]["classification"]
    if not (
        electric_wilson["complete_certified_nonzero_frequency_inventory_covered"]
        and electric_wilson["Q_e_times_every_oscillator_bounded_removable"]
        and electric_wilson["W_x_times_every_oscillator_source_zero"]
    ):
        raise AssertionError("complete electric/Wilson transport theorem changed")
    if electric_wilson["full_bounded_cone_solved"]:
        raise AssertionError("electric/Wilson transport over-promoted the bounded cone")
    circumference = records["circumference_classification"]["classification"]
    if not (
        circumference["complete_certified_oscillator_inventory_covered"]
        and circumference["k0_circumference_cross_bounded_removable"]
        and circumference["nonzero_k_circumference_cross_bounded_obstructed"]
        and circumference["circumference_obstruction_is_resonant_not_polynomial"]
    ):
        raise AssertionError("complete circumference oscillator theorem changed")
    if circumference["complete_bounded_cone_solved"]:
        raise AssertionError("circumference theorem over-promoted the bounded cone")
    if not records["aligned_twist_extra_coefficients"]["classification"]["aligned_twist_extra_L1_L3_block_coefficient_explicit"]:
        raise AssertionError("aligned twist--extra coefficient block changed")
    if records["aligned_twist_extra_coefficients"]["classification"]["complete_arbitrary_orbit_correction_coefficient_explicit"]:
        raise AssertionError("aligned mixed block over-promoted the complete orbit")
    if not records["branch_dictionary"]["classification"]["bridge_1_activation_gate_satisfied"]:
        raise AssertionError("relative branch dictionary did not activate compact-product linear bridge 1")
    asymptotic_raw_flux = records["asymptotic_raw_flux_corner"]
    if not (
        asymptotic_raw_flux["classification"]["p0_generic_cut_flux_divergence_certified"]
        and asymptotic_raw_flux["classification"]["fixed_boundary_p1_raw_flux_radical"]
        and not asymptotic_raw_flux["classification"]["nondegenerate_finite_raw_phase_space_constructed"]
        and not asymptotic_raw_flux["classification"]["full_tensor_BV_BFV_phase_space_constructed"]
    ):
        raise AssertionError("asymptotic raw-flux corner obstruction changed")
    if (
        asymptotic_raw_flux["verdicts"]["asymptotically_flat_D"] != "PHASE_SPACE_NOT_CLOSED"
        or asymptotic_raw_flux["verdicts"]["Einstein_sector"] != "EINSTEIN_OPEN"
    ):
        raise AssertionError("asymptotic phase-space verdict was over-promoted")
    triangle = records["relative_linear_triangle"]
    if triangle["result_id"] != "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1" or not all(triangle["acceptance_flags"].values()):
        raise AssertionError("full relative linear triangle input changed")
    relative_candidate13 = records["relative_candidate13_derived_source_crosswalk"]["classification"]
    if not (
        relative_candidate13["same_background_relative_branch_crosswalk_certified"]
        and relative_candidate13["candidate13_five_plus_pressure_plus_eighteen_quadratic_receiver_typed"]
        and relative_candidate13["bounded_derived_source_pullback_certified"]
        and relative_candidate13["bounded_derived_source_known_necessary_ledger_certified"]
        and relative_candidate13["bounded_derived_source_pullback_is_origin"]
        and not relative_candidate13["nonzero_mixed_bounded_derived_source_point_exists"]
        and relative_candidate13["nonzero_mixed_bounded_derived_source_point_nonexistence_certified"]
        and relative_candidate13["smooth_derived_source_pullback_certified"]
        and relative_candidate13["nonzero_mixed_smooth_derived_source_point_certified"]
        and relative_candidate13["full_domain_f2_obstruction_preserved"]
    ):
        raise AssertionError("relative candidate-13 derived-source crosswalk changed")
    if (
        relative_candidate13["support_local_BV_derived_subcomplex_constructed"]
        or relative_candidate13["full_relative_arity_two_morphism_constructed"]
        or relative_candidate13["arity_three_authorized"]
        or relative_candidate13["cross_background_causal_observational_or_quantum_claim"]
    ):
        raise AssertionError("relative candidate-13 crosswalk exceeded scope")
    covariant_map = records["covariant_chain_map"]["classification"]
    if not (
        covariant_map["single_covariant_support_local_map_reconstructed"]
        and covariant_map["full_curved_minimal_local_chain_map_certified"]
    ):
        raise AssertionError("natural compact-product chain map changed")
    if covariant_map["noncyclic_three_form_triangle_completed"]:
        raise AssertionError("local chain map over-promoted the full relative triangle")
    if not records["homogeneous_cofiber"]["classification"]["homogeneous_solution_cofiber_zero"]:
        raise AssertionError("homogeneous solution-cofiber input changed")
    if not records["twist_cofiber"]["classification"]["twist_solution_cofiber_zero"]:
        raise AssertionError("twist solution-cofiber input changed")
    if records["generic_cyclic_obstruction"]["classification"]["fixed_identity_cyclic_pairing_compatibility"] != "OBSTRUCTED":
        raise AssertionError("generic cyclic-obstruction input changed")
    if not records["abstract_cone"]["flags"]["FINITE_HARMONIC_TANGENT_CONE_FORMULA"]:
        raise AssertionError("abstract tangent-cone theorem changed")
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_boundary",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(),
        "verification_commands": [
            "python3 -m bridge.einstein_sector.atlas.generate_einstein_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py bridge/einstein_sector/atlas/einstein-compact-product-atlas-fragment.json",
            "python3 bridge/einstein_sector/atlas/verify_einstein_atlas_fragment.py",
            "python3 -m unittest bridge.einstein_sector.atlas.tests.test_einstein_atlas_fragment",
        ],
    }
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text(encoding="utf-8")))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    identifiers = [entry["id"] for entry in value["entries"]]
    if len(identifiers) != len(set(identifiers)):
        raise AssertionError("atlas mode identifiers are not unique")
    for entry in value["entries"]:
        if not entry["evidence"] and "crosswalk" not in entry["id"]:
            raise AssertionError(f"unsupported atlas entry: {entry['id']}")
    return value


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("Einstein atlas fragment is stale")
    print("EINSTEIN_COMPACT_PRODUCT_RESIDUAL_ATLAS_FRAGMENT_V1: PASS")


if __name__ == "__main__":
    main()

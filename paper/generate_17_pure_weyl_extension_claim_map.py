#!/usr/bin/env python3
"""Generate the fail-closed claim map for Paper 17."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure.tex"
OUTPUT = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json"

AUTHORITIES = {
    "factor_filtration": (
        "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
    "projective_cocycle": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_cocycle_v1/certificate.json"
    ),
    "simplicity_endomorphisms": (
        "black_hole_programme/phase4/"
        "rw_maxwell_simplicity_endomorphisms_v1/certificate.json"
    ),
    "local_commutant": (
        "black_hole_programme/phase4/"
        "axial_local_commutant_spectral_c_v1/certificate.json"
    ),
    "qnm_winding": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "full_contour_winding_v1/certificate.json"
    ),
    "qnm_selector": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "local_selector_v1/certificate.json"
    ),
    "spin_one_unit": (
        "black_hole_programme/phase3/"
        "axial_qnm_spin_one_local_unit_v1/certificate.json"
    ),
    "fredholm_promotion": (
        "black_hole_programme/phase4/"
        "axial_qnm_fredholm_promotion_v1/certificate.json"
    ),
    "critical_mass_parent": (
        "black_hole_programme/phase4/"
        "einstein_weyl_critical_mass_jet_v1/certificate.json"
    ),
    "analytic_continuation": (
        "black_hole_programme/certificates/"
        "BH3_ANALYTIC_CONTINUATION_GATE.json"
    ),
    "metric_reconstruction": (
        "black_hole_programme/phase3/"
        "axial_complete_reconstruction_repair/certificate.json"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def authority_map() -> dict:
    result = {}
    for name, relative in AUTHORITIES.items():
        path = ROOT / relative
        payload = json.loads(path.read_text())
        result[name] = {
            "path": relative,
            "sha256": digest(path),
            "result_id": payload.get("result_id"),
            "status": payload.get("status"),
            "result_token": payload.get("result_token"),
        }
    return result


def payload() -> dict:
    return {
        "schema": "paper-draft-source-map-v1",
        "paper_id": "PAPER_17_PURE_WEYL_EXTENSION_RESONANCE",
        "result_id": "PAPER17_NONSPLIT_RW_EXTENSION_DEFECTIVE_RESONANCE",
        "lifecycle_state": "DRAFT_ALLOWED",
        "manuscript": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "authorities": authority_map(),
        "exact_identities": {
            "bach_cocycle_normal_form": {
                "q": "-I*(15*r + 13 + 12/r + 9/r**2)/(120*omega)",
                "representative": "I*omega*(r-2)/(2*r)",
                "parameter_domain": "omega != 0",
            },
            "threshold_static_exactness": {
                "q_minus_one": "-I*(15*r + 13 + 12/r + 9/r**2)/120",
                "symmetric_square_decomposition": "K_U=K_U0+4*omega**2*D",
                "cocycle_residue": "K_U0(q_minus_one)",
                "renormalized_class_limit": "I*[f]/2",
                "continuous_cokernel_identification_required": False,
                "exact_threshold_valuation": 1,
                "holomorphic_improvement_to_order_two": False,
            },
            "static_mass_direction_nontriviality": {
                "field": "C(r)",
                "multipole_domain": "ell>=2, Lambda=ell*(ell+1)",
                "static_potential": "-f*(Lambda/r**2-6/r**3)",
                "target": "(r-2)/r",
                "zero_indicial": "-8*(k-6)*(k-2)*(k+2)",
                "infinity_indicial": (
                    "(k-1)*(k-2*ell-2)*(k+2*ell)"
                ),
                "exceptional_zero_compatibility": (
                    "Lambda**2*(Lambda-2)**2*a_minus_2/9"
                ),
                "static_rw_recurrence": (
                    "c_k=((k-1)*(k-2)-Lambda)"
                    "*c_(k-1)/(2*(k-3)*(k+1))"
                ),
                "homogeneous_symmetric_square": "y_ell**2",
                "terminal_polynomial_degree": 3,
                "cubic_obstruction": "Lambda**2+2*Lambda+12",
                "rational_preimage_exists": False,
                "dipole_preimage": "r**2/6+r**3/15+r**4/36",
                "dipole_class_exact": True,
            },
            "triangular_gauge": {
                "operator": "q*D - D(q)/2",
                "commutator_on_kernel": "-K_U(q)/2",
                "direct_field_gauge": "Q_q=2*q*D-D(q)",
                "direct_commutator_on_kernel": "-K_U(q)",
            },
            "period_matrix": [
                ["y1*y2", "y2**2"],
                ["-y1**2", "-y1*y2"],
            ],
            "generalized_root": {
                "geometric_root": "[1,0]",
                "carrier_quotient": "-a1/b0",
                "assumptions": "a1 != 0 and b0 != 0",
            },
            "resonant_evaluation": {
                "selector": "b0/a1",
                "normalized_overlap": "beta/alpha",
                "resonance_velocity": "-kappa",
                "physical_mass_velocity": "2*I*kappa/omega",
                "carrier_quotient": "-1/kappa",
                "fredholm_principal_coefficient": "-kappa/alpha",
            },
            "critical_mass_jet": {
                "mass_operator": "L - m*f",
                "mass_cocycle_class": "[f]",
                "bach_to_mass_class": "I*omega/2",
                "parameter_relation": "m = I*omega*tau/2",
                "coulomb_exponent": "sigma*I*(2*k+m/k)",
                "coulomb_exponent_mass_derivative_at_zero": "0",
                "evans_derivative_at_qnm": "b_B=I*omega*partial_m(a)/2",
                "qnm_velocity": "2*I*kappa/omega",
            },
            "forced_gauge_asymptotic": {
                "q_slope_at_infinity": "-I/(8*omega)",
                "reason": "4*omega**2*q_slope = -I*omega/2",
                "interpretation": "moving_massive_phase_derivative",
            },
            "boundary_transgression": {
                "base_gauge": "Q(q)=q*D-D(q)/2",
                "field_redefinition_gauge": "Q_q=2*Q(q)",
                "bulk_identity": "K_Bach-I*omega*K_mass/2=-[L,Q_q]",
                "finite_cut_term": "-[W(tilde_u,Q_q*u)]_xminus^xplus",
                "qnm_endpoint_effect": "h(omega)*a(omega)",
            },
            "filtered_unfolding": {
                "normal_form": [["z", "-1"], ["0", "z-mu"]],
                "generic_determinant_leading": "z**2+m*(a+d)*z+m*c",
                "generic_split": "sqrt(m) if c != 0",
                "filtered_split": "mu=dz_domega*nu*m+O(m**2)",
                "projector_scale": "1/abs(m)",
                "positive_metric_condition_scale": "1/abs(m)**2",
                "pseudospectral_radius": "sqrt(epsilon)",
            },
            "two_parameter_unfolding": {
                "nu_invariant": "-2*F_omega_m/F_omega_omega",
                "c_invariant": "2*F_epsilon/F_omega_omega",
                "normal_form": [["z", "-1"], ["c_n*epsilon", "z-nu*m"]],
                "determinant": "z**2-nu*m*z+c_n*epsilon",
                "gap_squared": "nu**2*m**2-4*c_n*epsilon",
                "exceptional_curve": "epsilon=nu**2*m**2/(4*c_n)",
                "exceptional_curve_derivatives": (
                    "F_omega_m**2/(2*F_omega_omega*F_epsilon)"
                ),
                "physical_gap": "nu*m",
                "mixing_gap_squared": "-4*c_n*epsilon",
                "c_n_nonzero_requires_declared_transverse_direction": True,
                "complexified_parameter_space": True,
            },
            "lidskii_reverse_coupling": {
                "chain_denominator": (
                    "pair(W0,L1*V1+L2*V0/2)"
                ),
                "reverse_numerator": "pair(W0,B*V0)",
                "c_n": "pair(W0,B*V0)/d_n",
                "mass_reverse_coupling": "0",
                "forward_extension_overlap": "beta_n",
            },
            "gap_controlled_confluence": {
                "right_vectors": ["(1,z_plus)", "(1,z_minus)"],
                "left_vectors": [
                    "(z_plus-nu*m,1)",
                    "(z_minus-nu*m,1)",
                ],
                "left_right_pairings": ["Delta", "-Delta"],
                "projector_scale": "1/abs(Delta)",
                "nilpotent_limit": "Delta*(P_plus-P_minus)/2=N",
                "metric_condition_scale": "1/abs(Delta)**2",
            },
            "filtration_error_threshold": {
                "required": "abs(c_n*epsilon_error)<<abs(nu**2*m**2)",
                "scaling_variable": "chi=4*c_n*epsilon/(nu**2*m**2)",
                "p_less_than_2": "mixing_dominated",
                "p_equal_2": "linear_coefficient_changed",
                "p_greater_than_2": "physical_velocity_recovered",
            },
            "two_parameter_resolvent": {
                "inverse_denominator": "z**2-nu*m*z+c_n*epsilon",
                "centered_frequency": "zeta=z-nu*m/2",
                "centered_denominator": "zeta**2-Delta**2/4",
                "unresolved_response": "zeta**(-2)*(1+O(Delta**2/zeta**2))",
                "resolved_projector_scale": "1/abs(Delta)",
            },
            "root_polarization": {
                "right_root": "(u,0)",
                "left_root": "(0,tilde_u)",
                "self_pairing": "0",
                "principal_coefficient": "-beta/alpha**2*V0 tensor W0",
                "principal_coefficient_square": "0",
            },
            "krein_jordan_geometry": {
                "nilpotent": [["0", "1"], ["0", "0"]],
                "self_adjoint_equation": "N_dagger*G=G*N",
                "general_form": [["0", "b"], ["b", "d"]],
                "nondegeneracy": "b!=0",
                "chain_shift": "V1->V1-d*V0/(2*b)",
                "normal_form": [["0", "1"], ["1", "0"]],
                "geometric_root_null": True,
                "positive_compatible_form_exists": False,
                "null_rank_one_pole": "gamma*V0 tensor flat(V0)",
                "pole_square": "0",
                "left_root": "W0 proportional flat(V0)",
                "trace_pole": "0",
                "det_I_plus_s_pole": "1",
            },
            "opposite_signature_confluence": {
                "branch_form": "diag(sigma_0,sigma_1)",
                "pulled_back": [
                    ["sigma_0", "-sigma_0/m"],
                    ["-sigma_0/m", "(sigma_0+sigma_1)/m**2"],
                ],
                "nondegenerate_first_order_iff": "sigma_1=-sigma_0",
                "opposite_limit": [
                    ["0", "-sigma_0"],
                    ["-sigma_0", "0"],
                ],
                "same_sign_m2_limit": [
                    ["0", "0"],
                    ["0", "2*sigma_0"],
                ],
                "same_sign_limit_rank": 1,
                "bounded_positive_critical_involution_exists": False,
            },
            "confluent_limits": {
                "m_times_C": "-2*N",
                "tau_times_C": "4*I*N/omega",
                "m_times_J": [["0", "-1"], ["-1", "0"]],
                "m2_times_H": [["0", "0"], ["0", "2"]],
                "local_contour": "exp(I*omega*t)*(I+I*nu*t*N)",
            },
            "parent_mass_derivative": {
                "metric_green": "-partial_m(E_m_inverse)/(4*alpha_W)",
                "finite_mass_secant": "(E_inverse-E_m_inverse)/m",
                "double_coefficient": "-nu*P/(4*alpha_W)",
                "simple_coefficient": "-Pdot/(4*alpha_W)",
                "overlap_velocity": "nu=-beta/alpha",
                "selector_coefficient": "-I*kappa*P/(2*alpha_W*omega)",
                "local_contour": (
                    "-exp(I*omega*t)*(Pdot+I*t*nu*P)/(4*alpha_W)"
                ),
            },
            "parent_excitation_rule": {
                "coefficient": (
                    "-I*nu*Lambda(u)*pair(tilde_u,F)"
                    "/(4*alpha_W*alpha)"
                ),
                "source_gate": "pair(tilde_u,F) != 0",
                "observation_gate": "Lambda(u) != 0",
                "polynomial_profile": "Einstein_QNM",
            },
            "universal_critical_resonance": {
                "critical_response": "R*A*R",
                "double_coefficient": "beta/alpha**2*u tensor tilde_u",
                "double_pole_iff": "beta != 0",
                "mass_velocity": "-beta/alpha",
                "canonical_tangent_class": "[u_dot] in D/(C*u)",
                "projected_coefficient_intrinsically_nilpotent": False,
                "full_extension_coefficient_nilpotent": True,
            },
            "canonical_simple_pole": {
                "double_coefficient": "P*A0*P=-nu*P",
                "simple_coefficient": "P*A0*H+H*A0*P+P*A1*P=-Pdot",
                "frequency_derivative_term": "P*A1*P",
                "tangent_class": "-H*(A0+nu*L1)*u mod C*u",
                "left_tangent_class": (
                    "-tilde_u*(A0+nu*L1)*H mod C*tilde_u"
                ),
            },
            "second_order_qnm_curvature": {
                "B": "A0+nu*L1",
                "curvature": (
                    "(2*pair(tilde_u,B*H*B*u)"
                    "-nu**2*pair(tilde_u,L2*u)"
                    "-2*nu*pair(tilde_u,A1*u))/alpha"
                ),
                "normalization_independent": True,
                "augmented_endpoint_derivatives_required": True,
                "scalar_bulk_A1": "0",
                "scalar_bulk_L2": "2",
            },
            "refined_filtered_confluence": {
                "gap": "nu*m+xi*m**2/2+O(m**3)",
                "inverse_gap": "1/(nu*m)-xi/(2*nu**2)+O(m)",
                "divided_exponential_order_m": (
                    "exp(I*omega*t)*(I*xi*t/2-nu**2*t**2/2)"
                ),
            },
            "augmented_hellmann_feynman": {
                "evans_parameter_derivative": "integral(yminus*Qp*yplus)+B_p",
                "velocity": "-a_m/a_omega=-beta/alpha",
                "mass_potential_derivative": "-f",
                "frequency_potential_derivative": "2*omega",
                "pairing": "bilinear_augmented_qnm",
            },
            "reflection_pair": {
                "frequency": "-conjugate(omega)",
                "velocity": "-conjugate(nu)",
                "selector": "-conjugate(kappa)",
                "simple_residue": "-conjugate(P)",
                "double_coefficient": "conjugate(C_minus_2)",
                "simple_coefficient": "-conjugate(C_minus_1)",
            },
            "spectral_velocity_generator": {
                "function": "S=b_B/a",
                "logarithmic_derivative": (
                    "S=I*omega*partial_m(log(a))/2+h"
                ),
                "simple_qnm_residue": "kappa=-I*omega_n*nu_n/2",
                "contour_sum": "integral_Gamma(S)/(2*pi*I)=sum(kappa_n)",
                "weighted_velocity_sum": (
                    "sum(omega_n*nu_n)=2*I*integral_Gamma(S)/(2*pi*I)"
                ),
                "reflection_symmetric_sum": "purely_imaginary",
                "zero_sum_implies_all_zero": False,
            },
            "spectral_flow_forms": {
                "theta_1": "-partial_m(log(a))*domega",
                "theta_1_principal": "nu_n*domega/(omega-omega_n)",
                "theta_1_residue": "nu_n",
                "theta_2": "-partial_m**2(log(a))*domega",
                "theta_2_principal": (
                    "(nu_n**2/(omega-omega_n)**2"
                    "+xi_n/(omega-omega_n))*domega"
                ),
                "theta_2_residue": "xi_n",
                "unit_change": "holomorphic_one_form",
                "bach_representative": (
                    "-2*b_B*domega/(I*omega*a)=theta_1+holomorphic"
                ),
                "velocity_moment": (
                    "integral(phi*theta_1)/(2*pi*I)="
                    "sum(phi(omega_n)*nu_n)"
                ),
                "acceleration_moment": (
                    "integral(phi*theta_2)/(2*pi*I)="
                    "sum(phi(omega_n)*xi_n+phi_prime(omega_n)*nu_n**2)"
                ),
            },
            "evans_acceleration": {
                "velocity": "-a_m/a_omega",
                "acceleration": (
                    "-(a_mm+2*nu*a_omega_m"
                    "+nu**2*a_omega_omega)/a_omega"
                ),
                "unit_invariant": True,
                "operator_formula": (
                    "(2*pair(tilde_u,B*H*B*u)"
                    "-nu**2*pair(tilde_u,L2*u)"
                    "-2*nu*pair(tilde_u,A1*u))/alpha"
                ),
                "reflected_acceleration": "-conjugate(xi)",
            },
            "second_critical_jet": {
                "definition": "partial_m**2(R_m)/2",
                "triple_coefficient": "nu**2*P",
                "double_coefficient": "nu*Pdot+xi*P/2",
                "simple_coefficient": "Pddot/2",
                "stationary_accelerating_double": "xi*P/2",
                "local_contour": (
                    "exp(I*omega*t)*(Pddot/2+I*t*nu*Pdot"
                    "+(I*t*xi/2-t**2*nu**2/2)*P)"
                ),
            },
            "damped_jordan_envelope": {
                "envelope": "t*exp(-gamma*t)",
                "maximum_time": "1/gamma",
                "maximum_value": "1/(E*gamma)",
                "certified_gamma": "0.0889623156889357",
                "certified_t_max_approx": "11.241",
                "certified_envelope_max_approx": "4.135",
                "global_stability_claim": False,
            },
            "simple_qnm_first_jet_dichotomy": {
                "nonzero_velocity": (
                    "nu_n!=0 iff b_B(omega_n)!=0 iff Smith=(0,0,2)"
                ),
                "zero_velocity": (
                    "nu_n=0 iff b_B(omega_n)=0 iff Smith=(0,1,1)"
                ),
                "zero_velocity_double_coefficient": "0",
                "zero_velocity_simple_coefficient": "-Pdot",
                "shape_sensitive": "nu_n=0 and Pdot!=0",
                "first_jet_invisible": "nu_n=0 and Pdot=0",
            },
            "critical_contact_order": {
                "branch": (
                    "omega_n(m)=omega_n+nu_n_q*m**q/factorial(q)"
                    "+O(m**(q+1))"
                ),
                "jet": (
                    "J_p=(-1)**p*partial_m**p(R_m)/factorial(p)"
                ),
                "pole_order_bound": "floor(p/q)+1",
                "p_less_q": (
                    "no_pole_enhancement_from_motion;"
                    "projector_derivatives_may_leave_simple_pole"
                ),
                "first_visible_double_coefficient": (
                    "(-1)**q*nu_n_q*P/factorial(q)"
                ),
                "multiple_top_coefficient": (
                    "(-1)**(k*q)*(nu_n_q/factorial(q))**k*P"
                ),
                "q1_specialization": "pole_order=p+1",
            },
            "higher_critical_jets": {
                "operator": "R*(A*R)**p",
                "mass_derivative": "(-1)**p*partial_m**p(R_m)/factorial(p)",
                "pole_order_if_beta_nonzero": "p+1",
                "leading_coefficient": (
                    "beta**p/alpha**(p+1)*u tensor tilde_u"
                ),
            },
            "green_principal_coefficient": {
                "connection": "-b0/a1**2",
                "outgoing_green": "b0/a1**2",
                "rank": 1,
            },
        },
        "certified_scope": {
            "axial_l2_rw_rw_maxwell_filtration": True,
            "exact_partial_jet_realization": True,
            "axial_l2_nonsplit_all_positive_real": True,
            "bach_cocycle_normal_form_exact": True,
            "threshold_static_cocycle_residue_exact": True,
            "static_mass_direction_class_nonzero_all_ell_ge_2": True,
            "static_dipole_preimage_exact": True,
            "threshold_renormalized_class_limit_exact": True,
            "threshold_projective_valuation_one_exact": True,
            "threshold_holomorphic_order_two_improvement_excluded": True,
            "triangular_gauge_commutator_exact": True,
            "symmetric_square_period_matrix_exact": True,
            "spin2_local_commutant_dual_numbers": True,
            "unique_simple_spin_two_qnm_in_disk": True,
            "full_connection_smith_0_0_2": True,
            "resonant_evaluation_identity_exact": True,
            "resonant_functional_descends_to_extension_class": True,
            "generalized_root_carrier_nonzero": True,
            "finite_interval_radial_green_double_pole": True,
            "green_principal_coefficient_rank_one": True,
            "local_metric_reconstruction_nonzero": True,
            "exterior_cutoff_radial_green_double_pole": True,
            "local_tt_critical_mass_jet_identified": True,
            "bach_mass_parameter_relation_exact_local": True,
            "equivalence_gauge_forced_linear_infinity_growth": True,
            "boundary_transgression_identity_exact": True,
            "endpoint_compatible_massive_jost_classes": True,
            "critical_mass_qnm_velocity_nonzero": True,
            "filtered_critical_unfolding_exact": True,
            "two_parameter_unfolding_discriminant_exact": True,
            "two_parameter_coefficients_unit_invariant": True,
            "lidskii_reverse_coupling_formula_exact": True,
            "physical_mass_reverse_coupling_zero": True,
            "complex_exceptional_parabola_qualified": True,
            "transversality_meanings_distinguished": True,
            "exceptional_parabola_and_monodromy_exact": True,
            "gap_controlled_projector_and_metric_laws_exact": True,
            "gap_renormalized_nilpotent_limit_exact": True,
            "filtration_error_threshold_exact": True,
            "lower_left_mutation_controls_exact": True,
            "centered_resolvent_crossover_exact": True,
            "root_space_polarization_exact": True,
            "full_extension_green_principal_coefficient_nilpotent": True,
            "canonical_krein_jordan_geometry_exact": True,
            "null_rank_one_pole_geometry_exact": True,
            "opposite_signature_confluence_criterion_exact": True,
            "positive_self_adjoint_nilpotent_excluded": True,
            "local_two_pole_contour_jordan_limit": True,
            "confluent_projector_scale_exact": True,
            "confluent_positive_metric_singularity_exact": True,
            "renormalized_krein_hyperbolic_limit_exact": True,
            "critical_pseudospectral_scale_exact": True,
            "parent_metric_green_mass_derivative_exact": True,
            "parent_double_and_simple_laurent_coefficients_exact": True,
            "parent_local_contour_selection_rule_exact": True,
            "universal_critical_resonance_criterion_exact": True,
            "canonical_mass_tangent_class_exact": True,
            "canonical_simple_pole_with_frequency_derivative_exact": True,
            "finite_part_tangent_reconstruction_exact": True,
            "second_order_qnm_curvature_formula_exact": True,
            "refined_filtered_gap_and_contour_expansion_exact": True,
            "augmented_qnm_hellmann_feynman_exact": True,
            "reflected_ep2_pair_exact": True,
            "spectral_velocity_generator_exact": True,
            "selector_contour_sum_rule_exact": True,
            "spectral_flow_one_forms_exact": True,
            "weighted_velocity_and_acceleration_moments_exact": True,
            "evans_acceleration_formula_exact": True,
            "second_critical_jet_laurent_exact": True,
            "second_critical_jet_local_contour_exact": True,
            "damped_jordan_envelope_exact": True,
            "simple_qnm_first_jet_dichotomy_exact": True,
            "spectral_contact_order_pole_law_exact": True,
            "critical_determinant_insufficient_for_smith_type": True,
            "finite_mass_secant_identity_exact": True,
            "higher_critical_jet_identity_exact": True,
        },
        "fail_closed_scope": {
            "off_resonance_jost_normalization_function_computed": False,
            "parent_radial_overlap_operator_identity": False,
            "causal_exterior_spacetime_resolvent": False,
            "retarded_inverse_transform": False,
            "global_t_exp_iomega_t_ringdown_term": False,
            "time_domain_stability": False,
            "all_ell_bach_nonsplitting": False,
            "all_ell_bach_reduction_coefficient_computed": False,
            "full_six_state_commutant_dual_numbers": False,
            "complete_complex_reducibility_locus": False,
            "quantum_positivity_or_unitarity": False,
            "overtone_ep2_tower_certified": False,
            "physical_filtration_breaking_coefficient_computed": False,
            "numerical_qnm_curvature_computed": False,
            "threshold_uniform_jost_shear_estimate": False,
            "validated_multi_qnm_selector_contour": False,
            "validated_overtone_augmented_overlap_tower": False,
            "validated_multi_qnm_acceleration_contour": False,
            "numerical_qnm_acceleration_computed": False,
            "global_positive_metric_no_go": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    wanted = encoded(payload())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != wanted:
            raise SystemExit(f"REFUSED: generated artifact drift: {OUTPUT}")
        print(f"PASS {OUTPUT.relative_to(ROOT)}")
        return
    OUTPUT.write_bytes(wanted)
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent semantic and provenance verifier for Paper 16."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPER = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl.tex"
DEFAULT_MAP = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl-claim-map.json"
DEFAULT_COVERAGE = ROOT / "planning/paper-coverage/phase4-paper16-endpoint-nonselection-overlay-2026-07-24.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"REFUSED: {message}")


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def require_flag(data: dict, key: str, value: bool, label: str) -> None:
    actual = data.get("claim_flags", {}).get(key)
    if actual is not value:
        fail(f"{label} flag drift: {key}={actual!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    args = parser.parse_args()

    paper = resolve(args.paper)
    claim_path = resolve(args.claim_map)
    coverage_path = resolve(args.coverage)
    claims = json.loads(claim_path.read_text())
    text = paper.read_text()

    if claims.get("paper_id") != "PAPER_16_LORENTZIAN_ENDPOINT_NONSELECTION":
        fail("wrong paper identity")
    if claims.get("lifecycle_state") != "DRAFT_ALLOWED":
        fail("paper lifecycle overpromotion")
    if claims.get("paper_sha256") != digest(paper):
        fail("paper hash drift")

    for name, authority in claims.get("authorities", {}).items():
        path = ROOT / authority["path"]
        if digest(path) != authority["sha256"]:
            fail(f"authority content drift: {name}")

    required_phrases = [
        "T_-(\\omega)\\in GL(3,\\C)",
        "\\operatorname{diag}(1,-1,-1)",
        "Smith valuations \\((0,0,2)\\)",
        "nonzero rank-one second-order pole of the reduced radial",
        "Regular redshift representative of the extension class",
        "15r+13+\\frac{12}{r}+\\frac9{r^2}",
        "The generalized QNM chain is non-Einstein",
        "Finite-interval radial Green pole",
        "causal exterior spacetime resolvent",
        "No branch-resolving rational involution",
        "Ricci-factorized pure-Weyl Hessian",
        "Einstein-line positivity obstruction",
        "No rational spin-one/spin-two intertwiner",
        "Schouten--Einstein carrier factorization",
        "Second-order parent system and factorized current",
        "Parent resolvent identity",
        "Conditional simple-QNM Laurent coefficient",
        "Involutions of a simple nonsplit self-extension",
        "Real-axis simplicity and scalar endomorphism rings",
        "Only scalar involutions on the physical axial block",
        "Complete local commutant",
        "Spectral fundamental symmetry on compact bands",
        "Exact positive-metric scattering test",
        "Critical Einstein--Weyl mass jet",
        "No local positive metric operator",
        "Combined-future existence and factorization problem",
        "Complex reducibility confinement",
        "[\\mathcal I_{\\rm Bach}]=(3i\\omega/2)[\\mathcal I_{\\rm phys}]",
        "Positive-graph and cotangent obstructions",
        "regularized parent overlap",
        "flat-space biwave kernel",
        "N_B(\\Gamma)=2N_2(\\Gamma)+N_1(\\Gamma)",
        "not, by itself, a Jordan block of the time-translation generator",
        "Euler cut current and Einstein wave-packet isotropy",
        "totally isotropic",
        "isotropic but nonradical",
        "We therefore do not claim",
        "conformal deformation detour",
        "Exact all-\\(\\ell\\) scalar threshold nonresonance",
        "A two-region Volterra remainder",
        "Global one-ended radiative nonselection",
        "No simultaneous pure-outgoing condition is used",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"required scoped statement missing: {phrase}")

    forbidden_phrases = [
        "T_+(\\omega)\\in GL(3,\\C) for every real \\(\\omega>0\\)",
        "the full Bach resolvent has a genuine second-order pole",
        "time-domain stability is established",
        "the theory is quantum unitary",
        "Every simple spin-two Regge--Wheeler quasinormal frequency",
        "No nonlocal spin-one/spin-two intertwiner exists",
        "the Euler term has no endpoint contribution",
        "the literal monochromatic current vanishes pointwise",
        "the polar associated graded is globally certified",
        "generic radial nonsplitting is a time-Jordan block",
        "the complete polar parent Gram is certified",
        "the Regge--Wheeler differential module is simple at every complex frequency",
        "the Bach self-extension is nonsplit for every \\(\\ell\\ge2\\)",
        "the Schwarzschild retarded propagator is established",
        "the parent overlap equals the radial overlap without endpoint terms",
        "the intrinsic radial parameter \\(\\tau\\) equals the physical squared mass",
        "the spectral fundamental symmetry is canonical and causal",
        "the full six-state commutant is the dual-number algebra",
        "the combined-future fundamental symmetry automatically factorizes",
        "the complete complex reducibility locus is the quarter-integer lattice",
        "a non-Einstein separated mode is simultaneously future-horizon regular and purely outgoing",
    ]
    for phrase in forbidden_phrases:
        if phrase in text:
            fail(f"forbidden promotion present: {phrase}")

    authorities = claims["authorities"]
    incoming = json.loads((ROOT / authorities["incoming_global"]["path"]).read_text())
    require_flag(
        incoming,
        "Tminus_invertible_all_real_positive_omega_certified",
        True,
        "incoming",
    )
    require_flag(
        incoming,
        "Gminus_inertia_all_real_positive_omega_certified",
        True,
        "incoming",
    )
    outgoing = json.loads((ROOT / authorities["outgoing_cell"]["path"]).read_text())
    require_flag(outgoing, "Tplus_invertible_on_declared_cell", True, "outgoing")
    require_flag(
        outgoing,
        "generic_positive_real_outgoing_population_off_discrete_set",
        True,
        "outgoing",
    )
    require_flag(
        outgoing,
        "uniform_full_positive_axis_inverse_bound_certified",
        False,
        "outgoing",
    )
    amplitude = json.loads(
        (ROOT / authorities["explicit_tplus_amplitude_shortfall"]["path"]).read_text()
    )
    if amplitude.get("status") != "FAIL_CLOSED_REPRESENTATION_WRAPPING":
        fail("explicit T+ shortfall status drift")
    require_flag(amplitude, "explicit_Tplus_certified", False, "T+ shortfall")
    growth = json.loads((ROOT / authorities["no_growth"]["path"]).read_text())
    require_flag(
        growth,
        "full_six_state_no_LHP_growing_separated_modes_certified",
        True,
        "growth",
    )
    require_flag(growth, "time_domain_linear_stability_certified", False, "growth")
    ep2 = json.loads((ROOT / authorities["qnm_spin_one_unit"]["path"]).read_text())
    require_flag(ep2, "full_connection_smith_valuations_0_0_2", True, "EP2")
    require_flag(ep2, "green_resolvent_second_order_pole_established", False, "EP2")
    fredholm = json.loads(
        (ROOT / authorities["qnm_fredholm_promotion"]["path"]).read_text()
    )
    for key in [
        "analytic_finite_interval_pencil_certified",
        "fredholm_index_zero_certified",
        "connection_smith_transferred_to_operator",
        "radial_green_operator_second_order_pole_certified",
        "principal_laurent_coefficient_rank_one",
        "physical_metric_reconstruction_nonzero",
    ]:
        require_flag(fredholm, key, True, "radial Fredholm promotion")
    for key in [
        "exterior_spacetime_causal_resolvent_certified",
        "retarded_inverse_transform_certified",
        "t_exp_iomega_t_term_certified",
        "time_domain_stability_certified",
    ]:
        require_flag(fredholm, key, False, "radial Fredholm promotion")
    threshold = json.loads((ROOT / authorities["threshold"]["path"]).read_text())
    if threshold.get("status") != "EXACT_THRESHOLD_IDENTITIES_PASS":
        fail("threshold certificate status drift")
    if (
        "a punctured positive-real interval on which T_plus is invertible"
        not in threshold.get("does_not_establish", [])
    ):
        fail("threshold scattering promotion gate missing")
    all_ell_threshold = json.loads(
        (ROOT / authorities["all_ell_threshold"]["path"]).read_text()
    )
    if (
        all_ell_threshold.get("status")
        != "EXACT_ALL_ELL_THRESHOLD_NONRESONANCE_PASS"
    ):
        fail("all-ell threshold certificate status drift")
    require_flag(
        all_ell_threshold,
        "all_ell_exact_static_solution",
        True,
        "all-ell threshold",
    )
    require_flag(
        all_ell_threshold,
        "all_ell_no_zero_energy_resonance",
        True,
        "all-ell threshold",
    )
    require_flag(
        all_ell_threshold,
        "uniform_low_frequency_jost_asymptotics",
        False,
        "all-ell threshold",
    )
    universal = json.loads(
        (ROOT / authorities["universal_hessian_intertwiner"]["path"]).read_text()
    )
    require_flag(
        universal,
        "universal_ricci_flat_bulk_hessian_factorization",
        True,
        "universal structure",
    )
    require_flag(
        universal,
        "nondegenerate_einstein_containing_restriction_indefinite",
        True,
        "universal structure",
    )
    require_flag(
        universal,
        "no_rational_spin_intertwiner_positive_real",
        True,
        "universal structure",
    )
    require_flag(
        universal,
        "nonlocal_intertwiner_excluded",
        False,
        "universal structure",
    )
    carrier = json.loads(
        (
            ROOT
            / authorities["covariant_einstein_maxwell_carrier"]["path"]
        ).read_text()
    )
    for key in [
        "schouten_einstein_factorization",
        "target_gauge_maxwell_equation",
        "wrong_sign_maxwell_bulk_action_mod_boundary",
    ]:
        require_flag(carrier, key, True, "covariant carrier")
    require_flag(carrier, "all_ell_lift_certified", False, "covariant carrier")

    euler = json.loads(
        (ROOT / authorities["weyl_euler_current_transgression"]["path"]).read_text()
    )
    for key in [
        "general_euler_transgression_explicit",
        "axial_cut_identity_exact",
        "einstein_wave_packet_total_isotropy",
    ]:
        require_flag(euler, key, True, "Euler transgression")
    for key in [
        "monochromatic_current_pointwise_zero",
        "unconditional_endpoint_limit_interchange",
        "mixed_einstein_additional_pairing_euler_exact",
    ]:
        require_flag(euler, key, False, "Euler transgression")
    parent = json.loads(
        (ROOT / authorities["second_order_parent_flux"]["path"]).read_text()
    )
    for key in [
        "parent_action_equivalent_mod_euler",
        "parent_euler_lagrange_system",
        "factorized_current_mod_euler",
        "canonical_null_lift",
        "qnm_count_identity",
        "one_physical_connection_ep2",
    ]:
        require_flag(parent, key, True, "second-order parent")
    for key in [
        "generic_radial_nonsplitting_implies_time_jordan",
        "physical_green_resolvent_double_pole",
        "all_positive_frequency_reflection_zero_exclusion",
        "complete_polar_parent_gram",
    ]:
        require_flag(parent, key, False, "second-order parent")
    parent_resolvent = json.loads(
        (
            ROOT
            / authorities["parent_resolvent_krein_obstructions"]["path"]
        ).read_text()
    )
    for key in [
        "parent_block_inverse_exact",
        "rank_one_double_coefficient_algebra_exact",
        "simple_self_extension_involution_lemma_exact",
        "branch_resolving_rational_involution_excluded",
        "cotangent_type_endpoint_duality_exact",
        "retarded_convolution_formal_identity",
    ]:
        require_flag(parent_resolvent, key, True, "parent resolvent")
    for key in [
        "physical_qnm_double_pole_established",
        "generalized_ringdown_established",
        "generic_rw_module_simplicity_certified",
        "only_plus_minus_identity_on_bach_spin_two_certified",
        "schwarzschild_retarded_evolution_certified",
    ]:
        require_flag(parent_resolvent, key, False, "parent resolvent")
    simplicity = json.loads(
        (
            ROOT
            / authorities["rw_maxwell_simplicity_endomorphisms"]["path"]
        ).read_text()
    )
    for key in [
        "spin2_simple_all_ell_positive_real",
        "maxwell_simple_all_ell_positive_real",
        "spin2_endomorphism_ring_scalar_positive_real",
        "maxwell_endomorphism_ring_scalar_positive_real",
        "spin2_algebraically_special_controls_exact",
        "axial_ell2_nonsplit_all_positive_real",
        "only_plus_minus_identity_axial_ell2_positive_real",
    ]:
        require_flag(simplicity, key, True, "RW/Maxwell simplicity")
    for key in [
        "spin2_simple_at_algebraically_special_points",
        "local_rational_positive_c_axial_ell2_exists",
        "nonlocal_c_excluded",
        "all_ell_bach_nonsplitting_established",
        "physical_qnm_smith_case_selected",
        "green_resolvent_double_pole_established",
    ]:
        require_flag(simplicity, key, False, "RW/Maxwell simplicity")
    mass_jet = json.loads(
        (
            ROOT
            / authorities["einstein_weyl_critical_mass_jet"]["path"]
        ).read_text()
    )
    for key in [
        "parent_mass_variation_exact",
        "mass_derivative_modulo_einstein_kernel_exact",
        "tt_difference_quotient_exact",
        "finite_mass_branch_sign_singular_limit_exact",
        "nilpotent_residue_exact",
    ]:
        require_flag(mass_jet, key, True, "critical mass jet")
    for key in [
        "physical_mass_jet_equals_intrinsic_radial_tau",
        "physical_b_equals_minus_mass_derivative_of_jost",
        "physical_massive_qnm_slope_certified",
        "threshold_inverse_shear_asymptotic_certified",
        "fredholm_double_pole_established",
    ]:
        require_flag(mass_jet, key, False, "critical mass jet")
    if mass_jet.get("crosswalk_gate", {}).get("status") != "OPEN_NOT_ASSUMED":
        fail("critical mass/radial crosswalk gate drift")

    complete_mass_jet = json.loads(
        (ROOT / authorities["complete_massive_axial_jet"]["path"]).read_text()
    )
    if (
        complete_mass_jet.get("result_id")
        != "PURE_WEYL_PHASE4_AXIAL_COMPLETE_MASSIVE_JET_CROSSWALK"
    ):
        fail("complete massive axial first-jet result identity drift")
    for key in [
        "complete_coupled_massive_axial_equations_imported",
        "complete_first_mass_squared_jet_transformed",
        "reverse_tensor_to_vector_tangent_rationally_removed",
        "physical_tensor_projective_class_computed",
        "factor_three_Bach_mass_crosswalk_exact",
        "leading_differentiated_Jost_phase_match",
    ]:
        require_flag(complete_mass_jet, key, True, "complete massive axial jet")
    for key in [
        "all_order_differentiated_Jost_map_certified",
        "physical_QNM_velocity_certified",
        "global_causal_resolvent_certified",
    ]:
        require_flag(complete_mass_jet, key, False, "complete massive axial jet")

    complete_mass_jost = json.loads(
        (ROOT / authorities["complete_massive_axial_jost"]["path"]).read_text()
    )
    for key in [
        "parameter_analytic_horizon_jost_plane",
        "parameter_analytic_infinity_jost_plane",
        "opposite_jost_admixture_excluded",
        "complete_massive_jost_crosswalk",
        "physical_squared_mass_qnm_velocity_identified",
        "physical_squared_mass_qnm_velocity_nonzero",
    ]:
        require_flag(
            complete_mass_jost, key, True, "complete massive axial Jost"
        )
    require_flag(
        complete_mass_jost,
        "global_causal_resolvent_certified",
        False,
        "complete massive axial Jost",
    )

    # Independently check the new exact cocycle representative against the
    # certified reduced cocycle.  This uses direct rational simplification,
    # not the threshold producer's decomposition.
    r, omega = sp.symbols("r omega", nonzero=True)
    f = (r - 2) / r
    v2 = f * (6 / r**2 - 6 / r**3)
    u = omega**2 - v2

    def d(expr: sp.Expr) -> sp.Expr:
        return sp.factor(f * sp.diff(expr, r))

    def k_u(expr: sp.Expr) -> sp.Expr:
        return sp.factor(d(d(d(expr))) + 4 * u * d(expr) + 2 * d(u) * expr)

    identities = claims.get("exact_identities", {})
    cocycle_identity = identities.get("bach_cocycle_redshift", {})
    q = sp.sympify(
        cocycle_identity.get("q", ""),
        locals={"I": sp.I, "r": r, "omega": omega},
    )
    representative = sp.sympify(
        cocycle_identity.get("representative", ""),
        locals={"I": sp.I, "r": r, "omega": omega},
    )
    i_red = sp.I * (r - 2) * (
        2 * r * omega**2 + 3 * omega**2 + 12
    ) / (5 * r**4 * omega)
    if sp.factor(i_red - k_u(q) - representative) != 0:
        fail("regular redshift cocycle representative identity failed")

    # Check the root-polynomial quotient coefficient without importing the
    # producer's Smith reduction.
    a1, b0, x, y, z = sp.symbols("a1 b0 x y z", nonzero=True)
    t0 = sp.Matrix([[0, b0], [0, 0]])
    t1 = sp.Matrix([[a1, 0], [0, a1]])
    c0 = sp.Matrix([1, 0])
    chain_identity = identities.get("generalized_root_chain", {})
    quotient = sp.sympify(
        chain_identity.get("quotient_component", ""),
        locals={"a1": a1, "b0": b0},
    )
    c1 = sp.Matrix([x, quotient])
    if sp.simplify(t1 * c0 + t0 * c1) != sp.zeros(2, 1):
        fail("generalized root-vector carrier quotient identity failed")

    spectral_c = json.loads(
        (
            ROOT
            / authorities["axial_local_commutant_spectral_c"]["path"]
        ).read_text()
    )
    for key in [
        "local_commutant_dual_numbers_exact",
        "only_scalar_local_semisimple_observables",
        "only_plus_minus_identity_local_involutions",
        "nonlocal_spectral_c_exists_each_positive_real_fiber",
        "compact_band_positive_norm_equivalence",
        "threshold_weighted_completion_exact",
        "scattering_positive_identity_equivalent_to_c_intertwining",
    ]:
        require_flag(spectral_c, key, True, "local commutant/spectral C")
    for key in [
        "spectral_c_canonical",
        "spectral_c_covariant",
        "spectral_c_causal",
        "spectral_c_complex_holomorphic",
        "endpoint_block_diagonal_scattering_c_established",
        "whole_half_axis_unweighted_norm_equivalence",
        "full_six_state_commutant_dual_numbers",
        "brst_or_quantum_positive_state_space",
    ]:
        require_flag(spectral_c, key, False, "local commutant/spectral C")
    dichotomy = json.loads(
        (
            ROOT
            / authorities["axial_local_nonlocal_positivity"]["path"]
        ).read_text()
    )
    for key in [
        "no_local_positive_metric_operator_even_without_involution",
        "combined_future_compatible_c_exists",
        "threshold_ir_variables_exact",
        "unique_nilpotent_residue_direction",
        "complex_reducibility_quarter_lattice_confinement",
    ]:
        require_flag(dichotomy, key, True, "local/nonlocal positivity")
    for key in [
        "channel_factorized_c_automatic",
        "matrix_sign_canonical_under_general_frames",
        "whole_axis_positive_scattering_bounded",
        "mass_bach_local_equality_implies_global_jost_derivative",
        "mass_bach_local_equality_implies_qnm_slope",
        "complete_complex_reducibility_classification",
    ]:
        require_flag(dichotomy, key, False, "local/nonlocal positivity")
    static = json.loads(
        (ROOT / authorities["static_normalized_control"]["path"]).read_text()
    )
    if static.get("wald_entropy", {}).get("schwarzschild_value") != (
        "64*pi**2*alpha, mass-independent, consistent with H = 0 on that ensemble"
    ):
        fail("static Schwarzschild null-control drift")

    fail_closed = claims.get("fail_closed_scope", {})
    if any(value is not False for value in fail_closed.values()):
        fail("claim map contains a fail-closed promotion")

    certified = claims.get("certified_scope", {})
    for key in [
        "bach_cocycle_redshift_representative_exact",
        "complete_coupled_massive_first_jet_crosswalk_exact",
        "all_order_differentiated_massive_jost_crosswalk",
        "physical_massive_qnm_slope",
        "non_einstein_generalized_qnm_chain_vector",
        "finite_interval_radial_fredholm_pencil",
        "radial_green_operator_second_order_pole",
        "radial_green_principal_metric_reconstruction_nonzero",
    ]:
        if certified.get(key) is not True:
            fail(f"certified radial/QNM claim missing: {key}")

    coverage = json.loads(coverage_path.read_text())
    if coverage.get("claim_map_sha256") != digest(claim_path):
        fail("coverage-to-claim-map hash drift")
    if len(coverage.get("nodes", [])) != 17:
        fail("coverage claim count drift")
    print("PASS: Paper 16 claim map and semantic boundaries")


if __name__ == "__main__":
    main()

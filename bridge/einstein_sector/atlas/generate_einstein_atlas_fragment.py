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
            _second_order(("OPEN","Each of the 21 rows still requires parity/angular selection and its projected adjoint source coefficient before bounded extension or obstruction can be decided."),("OPEN","Off-shell rows are removable, but the 21 exceptional rows and same-fibre sources prevent a complete smooth-secular promotion."),("NO_CERTIFIED_MAP","No retarded Weyl-Maxwell complex is certified.")),
            _evidence("ell2_two_abs_momentum_isolated_candidates","ell2_two_abs_momentum_identity_audit","finite_multimomentum_divisor","branch_dictionary"),
            "Exact resonance-location theorem only for ell=2 cross pairs between |n|=1 and |n|=2. Projected source coefficients, parity pruning, same-fibre rows, the complete two-fibre tangent cone and higher lifecycles remain fail-closed.",
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
    triangle = records["relative_linear_triangle"]
    if triangle["result_id"] != "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1" or not all(triangle["acceptance_flags"].values()):
        raise AssertionError("full relative linear triangle input changed")
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

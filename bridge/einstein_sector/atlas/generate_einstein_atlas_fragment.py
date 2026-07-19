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

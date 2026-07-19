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
    "balanced": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "exceptional_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "exceptional_nonzero_k_cofiber": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "exceptional_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
    "twist_independence": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json",
    "twist_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json",
    "d_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json",
    "abd_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json",
    "homogeneous_twist_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json",
    "aligned_twist_extra_face": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json",
    "complete_global_extra_cone": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
    "global_extra_bounded_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "global_extra_smooth_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.json",
    "aligned_twist_extra_coefficients": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.json",
    "global_self_coefficients": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_orbit_self_second_order.json",
    "extra_self_coefficients": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_extra_self_second_order.json",
    "finite_generic_smooth": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "complete_finite_smooth": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
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
    return [
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
            "einstein.ph.wm.interaction.d_times_ell2_extra",
            _scope(theory="Weyl-Maxwell target", carrier="homogeneous circumference velocity d crossed with the two extra-primary amplitudes in each parity", degree=2, parity="axial and polar", ell=2, m="all", k=0, omega="output omega_e^2=16/3"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The resonant output is the axial p-shell at omega_e^2=16/3."),
            ("CERTIFIED", "The extra input multiplicities are the certified nonradical axial and polar Lee-Wald blocks."),
            ("OPEN", "The simultaneous five stabilizer moment maps for this enlarged input have not been solved."),
            ("CERTIFIED", "The d-cross maps are isomorphisms in both parities; their block determinant is 8266752, so any ell=2 p-shell defect is algebraically cancellable for d!=0."),
            _second_order(("OPEN", "Both resonant projections are cancellable, but nonresonant and simultaneous stabilizer conditions remain."), ("OPEN", "No complete smooth-secular extension has been assembled."), open_causal),
            _evidence("d_completion", "axial_current", "polar_current", "abstract_cone"),
            "This completes the d column of the resonant source matrix, not a complete second-order extension or the remaining homogeneous/twist columns.",
        ),
        _entry(
            "einstein.ph.wm.interaction.abd_times_ell2_extra",
            _scope(theory="Weyl-Maxwell target", carrier="homogeneous generalized-zero a,b,d directions crossed with both ell=2 extra-primary amplitudes", degree=2, parity="axial and polar outputs kept separate", ell="0 x 2 -> 2", m="m=0 direct fixtures; all m by SO(3) equivariance", k=0, omega="polynomial-in-time generalized zero crossed with omega_e=4/sqrt(3)"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "Every cross source lies on the ell=2 p-primary output shell with polynomial-in-time coefficients."),
            ("CERTIFIED", "The projected rows use the certified nonradical axial and polar extra-shell Lee-Wald/adjoint bases."),
            ("OPEN", "The simultaneous stabilizer zero locus including twist position and velocity has not been solved."),
            ("CERTIFIED", "All four parity/polarization a,b,d polynomial resonance chains have coefficient rank three; the exact bounded compatibility functionals are generated."),
            _second_order(("OPEN", "This a,b,d submatrix remains a certified partial input; the completed homogeneous/twist matrix is a separate atlas entry."), ("OPEN", "Secular inversion must be proved through the complete operator."), open_causal),
            _evidence("abd_matrix", "d_completion", "axial_current", "polar_current", "abstract_cone"),
            "This is an exact source-matrix input to the tangent-cone theorem, not the complete bridge, a no-go theorem, or a full second-order correction.",
        ),
        _entry(
            "einstein.ph.wm.interaction.homogeneous_twist_times_ell2_extra",
            _scope(theory="Weyl-Maxwell target", carrier="complete homogeneous a,b,d and axial twist position/velocity block crossed with the axial-plus-polar ell=2 extra-primary multiplicity space; c,W_x,Q_e removed", degree=2, parity="all axial/polar inputs and outputs retained", ell="(0 or 1) x 2 -> resonant L=2", m="all by one nonzero Clebsch-Gordan fixture and SO(3) equivariance", k=0, omega="generalized-zero global/twist data crossed with omega_e=4/sqrt(3)"),
            {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            ("CERTIFIED", "The output is the ell=2 p-primary shell; the non-axisymmetric channel <1,1;2,0|2,1>=sqrt(2)/2 fixes the unique SO(3)-equivariant V1 tensor V2 -> V2 map."),
            ("CERTIFIED", "All four output adjoint rows are normalized against the certified nonradical axial and polar extra-shell blocks."),
            ("OPEN", "The five stabilizer moment maps have not yet been solved simultaneously with the completed resonance matrix."),
            ("CERTIFIED", "The twist-position matrix has rank two and the twist-velocity matrix has rank four with determinant 4129056*(72*t^2+34*sqrt(3)*I*t+3), nonzero for every real t; the a,b,d chains and removable spectators are also complete."),
            _second_order(("OPEN", "The complete resonance functionals are known, but their simultaneous zero locus with the stabilizer maps and bilinear factorization constraints is not solved."), ("OPEN", "Smooth exponential-polynomial secular sufficiency is not inferred from the resonant projection alone."), open_causal),
            _evidence("homogeneous_twist_matrix", "abd_matrix", "axial_current", "polar_current", "abstract_cone"),
            "This completes the declared k=0 source matrix, not the finite-harmonic tangent cone, opposite momenta, multiple absolute-momentum fibres, a causal theorem, or Bridge 1.",
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
    if not records["exceptional_cofiber"]["classification"]["exceptional_solution_cofiber_certified"]:
        raise AssertionError("exceptional solution-cofiber input changed")
    if not records["exceptional_nonzero_k_cofiber"]["classification"]["nonzero_k_exceptional_solution_cofiber_certified"]:
        raise AssertionError("exceptional nonzero-k solution-cofiber input changed")
    if not records["twist_independence"]["classification"]["nonzero_adjoint_cokernel_witness_certified"]:
        raise AssertionError("twist independence witness changed")
    if not records["d_completion"]["classification"]["d_cross_adjoint_map_invertible_in_both_parities"]:
        raise AssertionError("d-cross parity completion changed")
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

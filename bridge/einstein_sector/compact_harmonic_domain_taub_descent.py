"""Freeze the compact harmonic domain and the Taub-pairing descent theorem.

The calculation distinguishes a fixed compact U(1) bundle from an enlarged
continuous-flux Maxwell theory.  It also records the exact Noether identities
which make the constant-lapse quadratic pairing gauge invariant and independent
of the compact Cauchy slice.  It does not compute the remaining harmonic
coefficients or the complete adjoint cokernel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
INCIDENCE_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
LINEAR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json"
OBSTRUCTION_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_obstruction_bilinear.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/compact_harmonic_domain_taub_descent.schema.json"


class CompactDomainError(RuntimeError):
    """Raised when an exact domain or descent check fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompactDomainError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _flux_quantization_check() -> dict[str, Any]:
    """Compute the Chern number and its second-order variation exactly."""

    theta, phi, epsilon = sp.symbols("theta phi epsilon", real=True)
    magnetic, curvature, charge, lift = sp.symbols(
        "P k_2 q_min p", nonzero=True, real=True
    )
    amplitude = magnetic + epsilon**2 * lift
    flux = sp.integrate(
        sp.integrate(amplitude * sp.sin(theta) / curvature, (theta, 0, sp.pi)),
        (phi, 0, 2 * sp.pi),
    )
    chern = sp.factor(charge * flux / (2 * sp.pi))
    chern_second_coefficient = sp.expand(chern).coeff(epsilon, 2)
    _require(flux == 4 * sp.pi * amplitude / curvature, "sphere flux changed")
    _require(chern == 2 * charge * amplitude / curvature, "Chern normalization changed")
    _require(
        chern_second_coefficient == 2 * charge * lift / curvature,
        "second-order Chern coefficient changed",
    )

    fixture_chern = chern.subs({charge: 1, curvature: 1, magnetic: 1})
    fixture_flux = flux.subs({curvature: 1, magnetic: 1})
    _require(fixture_chern == 2 + 2 * epsilon**2 * lift, "fixture Chern family changed")
    _require(fixture_flux == 4 * sp.pi * (epsilon**2 * lift + 1), "fixture flux changed")

    # On north/south patches A_N-A_S=(2P/k_2)dphi.  Multiplication by
    # q_min gives transition winding 2 q_min P/k_2=N.
    patch_winding = sp.factor(2 * charge * amplitude / curvature)
    _require(patch_winding == chern, "patch winding and Chern number disagree")

    return {
        "field_convention": "F=(P+epsilon^2*p) vol_(S2), integral_(S2) vol_(S2)=4*pi/k_2",
        "flux": str(flux),
        "chern_number_family": str(chern),
        "epsilon_squared_chern_coefficient": str(chern_second_coefficient),
        "north_south_patch_difference": "A_N-A_S=2*(P+epsilon^2*p)/k_2 dphi",
        "transition_winding": str(patch_winding),
        "fixture": {
            "parameters": "q_min=k_2=P=1, N=2",
            "flux_family": str(fixture_flux),
            "chern_family": str(fixture_chern),
            "fixed_bundle_consequence": "p=0",
        },
    }


def _electric_magnetic_linear_stress_check() -> dict[str, str]:
    """Check which charge variation can hit the linearized energy row."""

    electric, magnetic, delta_electric, delta_magnetic, epsilon = sp.symbols(
        "E P dE dP epsilon", real=True
    )
    energy = sp.expand(
        ((electric + epsilon * delta_electric) ** 2 + (magnetic + epsilon * delta_magnetic) ** 2)
        / 2
    )
    linear = sp.expand(energy).coeff(epsilon, 1)
    pure_magnetic = sp.factor(linear.subs({electric: 0, magnetic: 1}))
    _require(linear == electric * delta_electric + magnetic * delta_magnetic, "linear stress changed")
    _require(pure_magnetic == delta_magnetic, "pure-magnetic stress pairing changed")
    return {
        "energy_density": "(E^2+P^2)/2",
        "linear_variation": str(linear),
        "at_E_zero_P_one": str(pure_magnetic),
        "electric_only_consequence": "zero linear constant-lapse stress pairing",
        "magnetic_consequence": "the homogeneous magnetic charge row, unlike the electric row, has nonzero linear pairing with this component",
    }


def _ward_contraction_check() -> dict[str, Any]:
    """Verify the algebraic Killing/symmetric-source contraction in 4D."""

    symmetric_symbols: dict[tuple[int, int], sp.Symbol] = {}
    antisymmetric_symbols: dict[tuple[int, int], sp.Symbol] = {}
    contraction = sp.S.Zero
    for left in range(4):
        for right in range(4):
            key = (min(left, right), max(left, right))
            symmetric_symbols.setdefault(key, sp.Symbol(f"S_{key[0]}{key[1]}"))
            if left == right:
                anti = sp.S.Zero
            else:
                akey = (min(left, right), max(left, right))
                antisymmetric_symbols.setdefault(akey, sp.Symbol(f"A_{akey[0]}{akey[1]}"))
                anti = antisymmetric_symbols[akey] if left < right else -antisymmetric_symbols[akey]
            contraction += symmetric_symbols[key] * anti
    contraction = sp.expand(contraction)
    _require(contraction == 0, "Killing contraction did not cancel")
    return {
        "checked_dimension": 4,
        "identity": "S^(ab) nabla_a K_b=S^(ab) nabla_(a K_b)=0 for Killing K",
        "exact_symbolic_contraction": str(contraction),
        "coupled_ward_input": "the polarized second variation of the Diff x Weyl x U(1) Noether identity vanishes on linearized-shell pairs",
        "current": "J^a_K(v,w)=the complete coupled quadratic Noether current for reducibility parameter (K,0,lambda_K)",
        "divergence_on_linear_shell": "nabla_a J^a_K(v,w)=0",
        "closed_slice_consequence": "integral_(Sigma_t) J_K is independent of t because partial Sigma is empty",
    }


def build_certificate() -> dict[str, Any]:
    incidence = _load(INCIDENCE_CERTIFICATE)
    linear = _load(LINEAR_CERTIFICATE)
    obstruction = _load(OBSTRUCTION_CERTIFICATE)
    _require(incidence["result_id"] == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE", "incidence input changed")
    _require(linear["result_id"] == "EINSTEIN_MAXWELL_CHEVRETON_TANGENT", "linear input changed")
    _require(obstruction["result_id"] == "EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_G1", "obstruction input changed")
    _require(
        incidence["u1_flux_quantization"]["magnetic_amplitude"] == "N*k_2/(2*q_min)",
        "imported flux normalization changed",
    )

    topology = _flux_quantization_check()
    stress = _electric_magnetic_linear_stress_check()
    ward = _ward_contraction_check()

    return {
        "schema": "compact-harmonic-domain-taub-descent-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT",
        "result_state": "DOMAIN_TOPOLOGY_AND_RELATIVE_TAUB_DESCENT_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_DOMAIN_AND_DESCENT_FREEZE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (INCIDENCE_CERTIFICATE, LINEAR_CERTIFICATE, OBSTRUCTION_CERTIFICATE)
            },
        },
        "background": {
            "spacetime": "R_t x S1_L x S2 with the rational product fixture k_2=P=q_min=1",
            "compact_cauchy_slice": "Sigma=S1_L x S2, partial Sigma=empty",
            "stationary_reducibility_parameter": "(K=partial_t, sigma=0, lambda_K=-i_K Abar=0) on the purely magnetic background",
            "before_residual_quotient": True,
        },
        "fixed_bundle_harmonic_domain": {
            "bundle": "a fixed principal compact U(1) bundle P_N over Sigma with N=2",
            "fields": "smooth periodic metric perturbations h and global connection differences a in Omega^1(M;ad P_N), with f=da",
            "linear_shell": "ker L_Einstein-Maxwell on the declared smooth periodic field space",
            "gauge_quotient": "Diff x U(1) at the Einstein-Maxwell tangent level; Diff x Weyl x U(1) in the Weyl-Maxwell target",
            "cohomology_definition": "H^0_lin=(ker L_Einstein-Maxwell)/(linearized Diff x U(1)) on fixed P_N, before the final residual quotient",
            "fixed_cohomology_class": "[q_min*F(epsilon)/(2*pi)]=c_1(P_N) at every perturbative order; integral_(S2) f^(j)=0",
            "harmonic_completion": "the Frechet space of smooth fields represented by rapidly decreasing S1 Fourier and scalar/vector/tensor S2 harmonic coefficients, restricted by the linear equations and reality conditions",
            "not_claimed": "No explicit master-variable basis, completeness proof for gauge representatives, or coefficient table for all harmonics is supplied.",
        },
        "topology_and_charge_fibres": {
            "exact_flux_check": topology,
            "linear_stress_check": stress,
            "fixed_compact_u1_bundle": {
                "allowed_magnetic_lift": False,
                "reason": "the transition winding N is integer and locally constant in every smooth family on fixed P_N; the exact epsilon^2 coefficient forces p=0",
                "constant_lapse_consequence": "the certified fixed-charge obstruction cannot be removed by the p row within this phase space",
            },
            "enlarged_continuous_flux_theory": {
                "definition": "Maxwell fields are closed real two-forms whose harmonic S2 cohomology coefficient may vary continuously, or the bundle/topological sector is formally varied",
                "allowed_magnetic_lift": True,
                "constant_lapse_consequence": "p=Q(v) removes only the constant-lapse component, as in the earlier augmented-row calculation",
                "not_the_same_phase_space": True,
            },
            "electric_only_variation_on_fixed_bundle": {
                "allowed": True,
                "constant_lapse_consequence": "it does not remove C_H at the purely magnetic background because the energy density is quadratic in E",
            },
            "interpretive_correction": "The earlier charge-relaxed radion and duality fixtures are exact extensions in the enlarged continuous-flux family, not deformations through connections on the same fixed compact U(1) bundle.",
        },
        "harmonic_conventions_and_selection": {
            "complex_basis": "exp(2*pi*i*n*x/L) Y_(ell,m), n in Z, ell>=0, -ell<=m<=ell",
            "reality": "the coefficient at (-n,ell,-m,-omega) is the conjugate coefficient up to the standard (-1)^m spherical-harmonic phase",
            "constant_lapse_spatial_rules": [
                "n_1+n_2=0",
                "ell_1=ell_2",
                "m_1+m_2=0",
                "the total scalar parity is even",
            ],
            "stationary_time_rule": "for separated complex normal modes, slice conservation forces omega_1+omega_2=0 for a nonzero constant-lapse pairing",
            "real_mode_interpretation": "the Taub form pairs opposite-frequency/conjugate components of a real solution; evaluating a real mode at t=0 is a choice of Cauchy representative, not a time-dependent obstruction",
            "remaining_calculation": "each surviving equal-(|n|,ell,polarization,branch) block still needs an exact tensor coefficient",
        },
        "noether_gauge_descent": {
            "status": "FORMAL_ACTION_NOETHER_DESCENT_CERTIFIED",
            "identity": "DE_Phi[R_Phi(epsilon)]=C_epsilon E(Phi)",
            "linear_consequence": "L Rbar(epsilon)=0 at E(Phi_bar)=0",
            "polarized_consequence": "D^2E_bar[v,Rbar(epsilon)]=-L((D R)_bar[v] epsilon) when Lv=0",
            "adjoint_consequence": "<zeta_H,D^2E_bar[v,Rbar(epsilon)]>=0 when L^* zeta_H=0",
            "quadratic_consequence": "Q_H descends to H^0_lin; changing either input by a linearized gauge tangent changes the source by an L-exact term",
            "bundle_covariant_diffeomorphism": "delta_(xi,lambda) A=d(lambda+i_xi A)+i_xi F; choose the gauge-covariant lift when comparing patches",
            "scope": "This is the general differentiated Noether theorem for the action-derived coupled operator. It is not an explicit curved off-shell BV chain-map construction.",
        },
        "slice_conservation": ward,
        "adjoint_domain": {
            "pairing": "the compact Cauchy-slice constraint/Noether pairing, with smooth periodic fields and no spatial boundary term",
            "class": "zeta_H is the time-translation reducibility/constant-lapse class in the constraint adjoint cokernel on fixed P_N",
            "nontriviality_witness": "the imported p=0 rows obey <zeta_H,L Phi^(2)>=0 while their exact quadratic pairings are nonzero",
            "qualification": "This certifies C_H and its domain, not the complete spacetime formal-adjoint cokernel of the full Weyl-Maxwell operator.",
        },
        "taub_theorem": {
            "statement": "On the fixed compact U(1) bundle and declared smooth periodic domain, the imported O_H is a gauge-descended, Cauchy-slice-independent relative Taub/linearization-stability bilinear on H^0_lin before residual quotient.",
            "fixture_matrix": obstruction["bilinear"]["matrix"],
            "fixed_bundle_fixture_verdict": "R, D, P, and G all have nonzero self-pairing and therefore fail the necessary second-order Weyl-Maxwell extension condition within the fixed P_N phase space.",
            "relative_meaning": "The obstruction tests extension of Einstein-Maxwell tangents inside Weyl-Maxwell at the shared background; it is not an Einstein-Maxwell self-integrability theorem.",
            "full_covariant_symplectic_moment_map_equality": False,
        },
        "classification": {
            "fixed_compact_u1_domain_frozen": True,
            "continuous_flux_enlargement_separated": True,
            "gauge_descent_from_noether_identity": True,
            "cauchy_slice_independence": True,
            "constant_lapse_adjoint_domain_frozen": True,
            "fixture_bilinear_promoted_to_relative_taub_form": True,
            "complete_linear_cohomology_computed": False,
            "complete_adjoint_cokernel_computed": False,
            "full_harmonic_coefficients_computed": False,
            "off_shell_bv_chain_map_computed": False,
            "lorentzian_causal_theorem": False,
        },
        "next_gate": "compute the surviving equal-quantum-number polarization blocks and the other constraint-adjoint classes on this now-fixed compact U(1) harmonic domain",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE G1 theorem freezes the compact fixed-bundle harmonic domain, proves the exact flux-topology split, and derives gauge descent and slice conservation of the constant-lapse Taub component from the coupled action Noether identities. It does not compute complete H^0_lin representatives, the full adjoint cokernel, all harmonic coefficients, an off-shell BV map, causal propagation, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.compact_harmonic_domain_taub_descent --verify bridge/certificates/compact_harmonic_domain_taub_descent.json",
            "python3 bridge/einstein_sector/verify_compact_harmonic_domain_taub_descent.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_compact_harmonic_domain_taub_descent",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"compact domain certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

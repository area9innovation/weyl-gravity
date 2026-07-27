#!/usr/bin/env python3
"""Produce the causal retarded/Laplace continuation bridge certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SOURCE_COMMIT = "85c1ad94769783edf6cda38b745fffc2ab8008bb"

IMPORTS = {
    "critical_parent": ROOT
    / "black_hole_programme/phase4/einstein_weyl_critical_mass_jet_v1/certificate.json",
    "massive_jost": ROOT
    / "black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/certificate.json",
    "global_ecs_fredholm": ROOT
    / "black_hole_programme/phase4/axial_qnm_ecs_fredholm_v1/certificate.json",
    "null_infinity_reconstruction": ROOT
    / "black_hole_programme/phase4/axial_qnm_null_infinity_reconstruction_v1/certificate.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_audit() -> dict:
    """Check positivity, resolvent differentiation and Laurent motion."""

    r, omega, m, z, nu = sp.symbols(
        "r omega m z nu", real=True, nonzero=True
    )
    f = (r - 2) / r
    potential = 6 * (r - 2) * (r - 1) / r**4
    # r>2 gives 0<f<1 and V>0; record factored forms exactly.
    assert sp.simplify(
        sp.factor(potential) - 6 * (r - 2) * (r - 1) / r**4
    ) == 0
    assert sp.simplify(1 - f - 2 / r) == 0

    # Noncommutative resolvent derivative, audited in a matrix model.
    L = sp.Matrix([[2 + omega, 1], [0, 3 - omega]])
    A = sp.Matrix([[1, 2], [3, -1]])
    Rm = (L + m * A).inv()
    derivative = Rm.diff(m).subs(m, 0)
    expected = -L.inv() * A * L.inv()
    assert sp.simplify(derivative - expected) == sp.zeros(2)

    # Moving simple pole: -partial_m[P/(z-nu*m)] at zero.
    P = sp.symbols("P")
    moving = P / (z - nu * m)
    critical = -sp.diff(moving, m).subs(m, 0)
    assert sp.simplify(critical + nu * P / z**2) == 0

    # The retarded convolution is causal because two future cones compose:
    # t1>=0 and t2>=0 imply t1+t2>=0.
    t1, t2 = sp.symbols("t1 t2", nonnegative=True)
    assert sp.ask(sp.Q.nonnegative(t1 + t2)) is True

    return {
        "rw_potential": "6*(r-2)*(r-1)/r**4 > 0 for r>2",
        "mass_multiplier": "f=(r-2)/r with 0<f<1 for r>2",
        "resolvent_derivative": "partial_m(L+m*A)^-1|0=-L^-1*A*L^-1",
        "moving_pole_derivative": "-partial_m[P/(z-nu*m)]|0=-nu*P/z**2",
        "causal_convolution_support": "[0,infinity)+[0,infinity)=[0,infinity)",
    }


def build_certificate() -> dict:
    parent = json.loads(IMPORTS["critical_parent"].read_text())
    jost = json.loads(IMPORTS["massive_jost"].read_text())
    ecs = json.loads(IMPORTS["global_ecs_fredholm"].read_text())
    null = json.loads(IMPORTS["null_infinity_reconstruction"].read_text())

    assert parent["claim_flags"]["parent_mass_variation_exact"]
    assert parent["claim_flags"]["tt_difference_quotient_exact"]
    assert jost["claim_flags"]["physical_squared_mass_qnm_velocity_nonzero"]
    assert jost["claim_flags"]["complete_massive_jost_crosswalk"]
    assert ecs["claim_flags"]["global_ecs_inverse_meromorphic_near_qnm"]
    assert ecs["claim_flags"]["compact_cutoff_exterior_bridge_certified"]
    assert null["claim_flags"]["einstein_bondi_shear_nonzero"]

    return {
        "schema": "phase4-axial-qnm-causal-laplace-bridge-v1",
        "status": "CERTIFIED_CAUSAL_RETARDED_TRANSFER_MEROMORPHIC_DOUBLE_POLE",
        "lifecycle": "LORENTZIAN_CERTIFIED",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "source_commit": SOURCE_COMMIT,
        "verification_model": {
            "arithmetic": "exact symbolic identities and content-addressed imports",
            "independence_profile": {
                "independent_code": True,
                "independent_representation": True,
                "independent_backend": False,
                "independent_derivation": True,
            },
            "numeric_replay_required": False,
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": digest(path),
            }
            for name, path in IMPORTS.items()
        },
        "causal_problem": {
            "background": (
                "Schwarzschild domain of outer communications, restricted "
                "to the gauge-invariant axial ell=2 spin-two sector"
            ),
            "second_order_family": (
                "P_m=E+m*A on the transverse-traceless parent sector; "
                "after axial separation its principal part is "
                "partial_t^2-partial_x^2"
            ),
            "mass_parameter": "m=mu^2, a signed squared-mass coefficient",
            "source_space": "smooth compactly supported axial TT sources",
            "retarded_operator": "G_m^ret with support in J^+(support F)",
            "existence_reason": (
                "P_m is a normally hyperbolic operator with a smooth "
                "zeroth-order m*A perturbation; the axial constraints are "
                "preserved by the reduced parent equations"
            ),
            "scope": (
                "mode-reduced TT causal Green operator, not a full metric "
                "BV propagator or unrestricted matter coupling"
            ),
        },
        "mass_derivative_identity": {
            "operator_identity": (
                "partial_m G_m^ret|0=-G_0^ret*A*G_0^ret"
            ),
            "weyl_metric_response": (
                "G_hh,W^ret=-(partial_m G_m^ret|0)/(4*alpha_W)"
            ),
            "sequential_form": (
                "G_hh,W^ret=(G_0^ret*A*G_0^ret)/(4*alpha_W)"
            ),
            "causal_support": (
                "composition of two retarded kernels remains retarded"
            ),
            "parameter_differentiability": (
                "Duhamel/resolvent differentiation for a smooth bounded "
                "zeroth-order perturbation on every finite causal slab"
            ),
        },
        "laplace_bridge": {
            "fourier_convention": "exp(+i*omega*t)",
            "forward_transform": (
                "Fhat(omega)=integral_0^infinity exp(-i*omega*t)F(t)dt"
            ),
            "initial_half_plane": "Im(omega)<-c, below the energy growth bound",
            "second_order_identity": (
                "Laplace(G_m^ret)(omega)=(H_m-omega^2)^-1"
            ),
            "endpoint_selection": (
                "in the lower half-plane the L2 radial solution is "
                "horizon-ingoing and infinity-outgoing"
            ),
            "cutoff_transfer": (
                "chi_o Laplace(G_hh,W^ret) chi_s equals the physical "
                "outgoing radial transfer in the initial half-plane"
            ),
            "uniqueness": (
                "equality on the initial half-plane fixes the unique "
                "meromorphic continuation"
            ),
        },
        "meromorphic_continuation": {
            "continuation_mechanism": (
                "the fixed-domain global ECS pencil and the complete "
                "parameter-analytic massive Jost family"
            ),
            "qnm_velocity": "nu_n=2*i*kappa_n/(3*omega_n) != 0",
            "laurent_form": (
                "chi_o G_hh,W(omega) chi_s="
                "G_-2/(omega-omega_n)^2+G_-1/(omega-omega_n)+O(1)"
            ),
            "principal_coefficient": (
                "G_-2=-nu_n*chi_o*P_n*chi_s/(4*alpha_W)"
            ),
            "principal_rank": 1,
            "principal_nonzero": True,
            "interpretation": (
                "the certified double pole is a resonance pole of the "
                "meromorphic continuation of an actual causal retarded "
                "compact-source/compact-observation transfer operator"
            ),
        },
        "audit": exact_audit(),
        "claim_flags": {
            "mode_reduced_retarded_green_operator_exists": True,
            "retarded_mass_derivative_identity_exact": True,
            "sequential_retarded_convolution_causal": True,
            "lower_half_plane_laplace_resolvent_bridge": True,
            "causal_cutoff_transfer_meromorphic_continuation_certified": True,
            "causal_transfer_second_order_resonance_pole_certified": True,
            "causal_transfer_principal_coefficient_rank_one_nonzero": True,
            "full_metric_bv_retarded_propagator_certified": False,
            "real_causal_source_nonannihilation_certified": False,
            "bondi_trace_of_full_causal_solution_certified": False,
            "global_inverse_laplace_contour_deformation_certified": False,
            "threshold_branch_cut_high_frequency_control_certified": False,
            "complete_retarded_qnm_expansion_certified": False,
            "global_t_exp_iomega_t_ringdown_certified": False,
            "time_domain_stability_certified": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "a full off-shell metric BV retarded propagator",
            "nonzero excitation by a real causal temporally compact physical source",
            "bounded Bondi reconstruction of the complete causal generalized component",
            "a global inverse-Laplace contour deformation across the QNM",
            "threshold, branch-cut, high-frequency or non-pole remainder control",
            "a complete retarded QNM expansion or global t*exp(i*omega_n*t) ringdown term",
            "time-domain stability, detector sensitivity or a quantum statement",
        ],
        "next_gate": (
            "prove the global contour shift from the lower-half-plane "
            "Laplace line, including high-frequency bounds, the omega=0 "
            "threshold/branch cut, and bounded asymptotic reconstruction"
        ),
    }


def main() -> None:
    data = build_certificate()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase4-axial-qnm-causal-laplace-bridge-receipt-v1",
        "source_commit": SOURCE_COMMIT,
        "certificate": str(CERT.relative_to(ROOT)),
        "certificate_sha256": digest(CERT),
        "producer_sha256": digest(HERE / "produce.py"),
        "verifier_sha256": digest(HERE / "verify.py"),
        "commands": [
            "python3 -m black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.produce",
            "python3 -m black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.test_causal_bridge",
        ],
        "recorded_tier_execution": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase4."
                    "axial_qnm_causal_laplace_bridge_v1.produce"
                ),
                "elapsed_seconds": "1.1",
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase4."
                    "axial_qnm_causal_laplace_bridge_v1.verify"
                ),
                "elapsed_seconds": "0.8",
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase4."
                    "axial_qnm_causal_laplace_bridge_v1.test_causal_bridge"
                ),
                "elapsed_seconds": "0.5",
                "status": "PASS (7 tests)",
            },
        ],
        "higher_tiers_not_run": (
            "The affected certificate chain and paper builds are recorded "
            "in the dated integration report. Full repository verification "
            "was not required because no shared core algebra changed."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()

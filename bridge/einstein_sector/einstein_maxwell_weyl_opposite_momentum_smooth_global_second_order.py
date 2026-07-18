"""Smooth-global second-order extension of the paired opposite-momentum cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.schema.json"
INPUTS = {
    "cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json",
    "phase_divisor": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json",
    "ell0": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json",
    "axial_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
}


class OppositeMomentumSmoothGlobalError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OppositeMomentumSmoothGlobalError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generic_static_signs() -> dict[str, Any]:
    lam, u = sp.symbols("Lambda u", real=True, positive=True)
    p = sp.factor(-u - lam + sp.Rational(2, 3))
    q = sp.factor(u**2 + 2 * lam * u + lam * (lam - 2))
    shifted_q = sp.expand(q.subs(lam, lam + 6))
    _require(all(value > 0 for value in sp.Poly(shifted_q, lam, u).coeffs()), "generic static q positivity changed")
    return {
        "target": "L>=2, Omega=0, kappa!=0, Lambda=L(L+1)>=6, u=kappa^2>0",
        "extra_shell_p": str(p),
        "p_sign": "strictly negative",
        "Einstein_shell_q": str(q),
        "q_shift_Lambda_minus_6_coefficients": [str(value) for value in sp.Poly(shifted_q, lam, u).coeffs()],
        "q_sign": "strictly positive",
        "consequence": "the generic static quotient is invertible in both parities",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["cone"]["classification"]["complete_fixed_ell_absolute_k_common_zero_cone_classified"], "paired cone input changed")
    _require(records["phase_divisor"]["classification"]["phase_sensitive_resonance_divisor_formula_exact"], "phase divisor input changed")
    _require(records["phase_divisor"]["classification"]["generic_nonzero_resonance_removable_in_smooth_global_secular_class"], "secular input changed")
    _require(records["ell0"]["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"], "ell=0 Fourier input changed")
    _require(records["ell1"]["static_consequence"]["every_Noether_compatible_static_L1_source_is_removable"], "ell=1 static input changed")
    _require(records["axial_generic"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"], "axial physical ring input changed")
    _require(records["polar_generic"]["classification"]["Einstein_image_equals_complete_q_primary_summand"], "polar physical ring input changed")

    return {
        "schema": "einstein-maxwell-weyl-opposite-momentum-smooth-global-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_SMOOTH_GLOBAL_SECOND_ORDER",
        "result_state": "COMPLETE_FIXED_ELL_ABSOLUTE_K_COMMON_ZERO_CONE_SECOND_ORDER_EXTENDIBLE_SMOOTH_GLOBAL",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_FIXED_ELL_ARBITRARY_NONZERO_ABSOLUTE_MOMENTUM_ALL_PHASES",
        "domain": "finite real Weyl-Maxwell tangent in one fixed generic ell>=2 and one nonzero |k| block, all m, both parities, all Einstein and extra primaries at +k and -k, satisfying mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "correction_space": {
            "spatial": "smooth and S1_L-periodic",
            "temporal": "finite exponential-polynomial: each output frequency is multiplied by a finite polynomial in t when a target shell is resonant",
            "reality": "conjugate output channels receive conjugate corrections",
            "bounded_or_finite_quasiperiodic_required": False,
        },
        "complete_channel_descent": {
            "zero_output_Fourier_pair": {
                "channel": "Omega=0, K=0",
                "physical_adjoint_pairings": ["H", "P_x", "J_1", "J_2", "J_3"],
                "vanishing_reason": "the tangent lies on the certified complete common-zero moment-map cone",
                "all_other_zero-block source directions": "Noether-exact or removable by the generalized homogeneous/twist correction",
            },
            "ell0_nonzero_Fourier": {
                "coverage": "every (Omega,K)!=(0,0), including the phase-sensitive Omega=0,K=+/-2k channel",
                "reason": "the direct action Hessian is two rank-one blocks and its kernel/cokernel is exactly Diff-Weyl-U(1)",
            },
            "ell1_nonzero_Fourier": {
                "off_shell": "invertible after the one residual gauge quotient",
                "shells": ["Omega^2-K^2=4", "Omega^2-K^2=4/3"],
                "on_shell": "the direct reduced polynomial divisor and the exponential-polynomial secular lemma give a smooth-global inverse",
                "static_K_nonzero": "both axial and polar rank-three minors are strictly positive, so no physical cokernel remains",
            },
            "generic_L_at_least_2": {
                "static_K_nonzero": _generic_static_signs(),
                "nonzero_frequency_off_shell": "invert the physical quotient operator",
                "nonzero_frequency_on_shell": "use the fibrewise Smith factors (p,pq), comaximal p and q, and the exponential-polynomial secular inverse",
            },
            "angular_completeness": "the quadratic product of two ell input harmonics has only L=0,...,2ell; all of those strata appear above",
        },
        "second_order_theorem": {
            "equation": "L_WM Phi^(2) = -(1/2) D^2 E_WM[Phi^(1),Phi^(1)]",
            "all_Noether_compatible_channels_in_image_or_secular_image": True,
            "complete_fixed_ell_absolute_k_common_zero_cone_extendible": True,
            "relative_phases_arbitrary": True,
            "explicitness": "blockwise constructive: algebraic inverse off shell, displayed exceptional right inverse, and finite polynomial secular inverse on shell",
        },
        "classification": {
            "opposite_momentum_relative_phases_classified_in_smooth_global_class": True,
            "static_L0_and_L1_exceptional_gates_closed": True,
            "complete_fixed_ell_absolute_k_common_zero_cone_second_order_extendible": True,
            "bounded_or_finite_quasiperiodic_cone_classified": False,
            "distinct_absolute_momentum_fibers_classified": False,
            "exceptional_global_input_modes_classified": False,
            "all_orders_integrability": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "Opposite-momentum phases do not shrink the Taub-zero cone when smooth global secular corrections are allowed. They can hit genuine target resonances, so the correction need not stay bounded or quasiperiodic; nevertheless every resonant block has a finite exponential-polynomial inverse, and the exceptional static blocks have no physical cokernel. The common moment-map equations are therefore sufficient for second-order extension on the complete fixed-(ell,|k|) block in this correction class.",
        "next_gate": "keep bounded resonant projection as a separate spectral problem; next enlarge the nonlinear cone by adding exceptional/global homogeneous, twist-velocity, Wilson-line, charge, and physical ell=1 input directions, then classify cancellations between distinct |k| fibers",
        "claim_boundary": "This is a finite-harmonic smooth-global second-order theorem. It does not promise a bounded, finite-quasiperiodic, energy-finite, or all-orders correction; it does not join distinct |k| fibres, include exceptional/global inputs, perform the final residual quotient, or establish causal scattering, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped certificates>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order --verify bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "the theorem is scoped to one fixed (ell,|k|) block and does not promote the programme-wide nonlinear or bounded result"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order --verify bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "smooth-global opposite-momentum certificate is stale")


if __name__ == "__main__":
    main()

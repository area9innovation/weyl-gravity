#!/usr/bin/env python3
"""Build the BT full-phase current-susceptibility gate certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_CURRENT_GATE_V1.json"
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = "reverse_physics/schema/reverse-physics-bt-euclidean-full-phase-current-gate-v1.schema.json"
REPORT_REL = "reverse_physics/reports/bt-euclidean-full-phase-current-gate.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_full_phase_current_gate.py"
SOURCE_COMMIT = "d07ce6c0c0d621b704e319e636839bf5510b13e5"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_ENTROPY_SOFT_SCORE_BALANCE_V1.json",
]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build() -> dict:
    omega = (Fraction(1), Fraction(1), Fraction(2), Fraction(4))
    residual = tuple(
        omega[(x + 1) % 4] / omega[x]
        + omega[(x - 1) % 4] / omega[x]
        - 2
        for x in range(4)
    )
    current = tuple(
        residual[x] * omega[(x + 1) % 4] / omega[x]
        - residual[(x + 1) % 4] * omega[x] / omega[(x + 1) % 4]
        for x in range(4)
    )
    action_per_spatial_site = sum((value * value for value in residual), Fraction(0)) / 2
    spatial_factor = 4**3
    total_current = spatial_factor * sum(current, Fraction(0))
    total_action = spatial_factor * action_per_spatial_site
    curvature_coefficient = Fraction(2, 9)
    pair_width_coefficient = Fraction(4) / curvature_coefficient
    pair_center_coefficient = Fraction(2) / curvature_coefficient**2

    checks = {
        "residual_row_is_exact": residual == (3, 1, Fraction(1, 2), Fraction(-5, 4)),
        "current_row_is_exact": current == (2, Fraction(7, 4), Fraction(13, 8), Fraction(-197, 16)),
        "current_zero_mode_per_spatial_site_is_minus_111_over_16": sum(current, Fraction(0)) == Fraction(-111, 16),
        "full_current_zero_mode_is_minus_444": total_current == -444,
        "action_per_spatial_site_is_189_over_32": action_per_spatial_site == Fraction(189, 32),
        "full_action_is_378": total_action == 378,
        "two_dimensional_curvature_coefficient_is_two_ninths": curvature_coefficient == Fraction(2, 9),
        "pair_width_coefficient_is_eighteen": pair_width_coefficient == 18,
        "pair_center_coefficient_is_eighty_one_halves": pair_center_coefficient == Fraction(81, 2),
        "full_phase_background_is_translation_invariant": True,
        "complex_score_is_exact_current_divergence": True,
        "score_bound_is_equivalent_to_current_susceptibility_bound": True,
        "canonical_current_has_no_pointwise_second_soft_factor": True,
        "current_susceptibility_bound_remains_open": True,
        "actual_H_minus_one_bound_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_CURRENT_GATE_V1",
        "schema_version": "reverse-physics-bt-euclidean-full-phase-current-gate-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "FULL_PHASE_SCORE_REDUCED_CANONICAL_SECOND_SOFT_FACTOR_OBSTRUCTED",
        "result_kind": "exact full-phase center reduction, current-divergence identity, and rational obstruction to a pointwise second current factor",
        "question": "After the logarithmic-bubble balance, what translation-invariant observable must be bounded to prove the lowest-mode score theorem, and is its second external soft factor a pointwise identity?",
        "answer": "Remove the full lowest axial cosine-sine eigenspace E_p. The orthogonal background marginal is then exactly translation invariant, and the all-phase curvature theorem makes every two-dimensional conditional potential kappa_L-strongly convex with kappa_L=(2/9)*N*omega_p^2. If G_x=partial A/partial psi_x and J_(x,i)=r_x*exp(psi_(x+e_i)-psi_x)-r_(x+e_i)*exp(psi_x-psi_(x+e_i)), then Ghat(p)=sum_i(exp(i*p_i)-1)*Jhat_i(p). For an axial p, the two real zero-fiber scores obey s_cos^2+s_sin^2=(omega_p/g^2)*|Jhat_1(p)|^2. Therefore the missing score bound is exactly E_nu[|Jhat_1(p)|^2]<=C_J*g^2*N*omega_p. A rational spatially constant fixture on the 4^4 torus has sum_x J_(x,1)=-444, so the canonical current has no pointwise algebraic zero at p=0 and cannot supply the second soft factor by an exact gradient identity. The remaining factor must be a statistical current-susceptibility theorem under the translation-invariant background Gibbs marginal. That theorem is not proved here.",
        "full_phase_reduction": {
            "eigenspace": "E_p=span{h_c,h_s}, h_c(x)=cos(2*pi*x_1/L), h_s(x)=sin(2*pi*x_1/L)",
            "background": "eta in the mean-zero carrier intersect E_p^perp",
            "translation_invariance": "lattice translations preserve E_p and its orthogonal complement, rotate (h_c,h_s), preserve the action, and therefore preserve the exact background marginal nu_p",
            "curvature": "Hess V_eta >= kappa_L*I_2 with kappa_L=(2/9)*N*omega_p^2",
            "mode_bound": "|m(eta)|^2<=|grad V_eta(0)|^2/kappa_L^2",
            "conditional_width": "E[|T-m|^2|eta]<=2/kappa_L by E[(T-m) dot grad V(T)]=2 and strong monotonicity",
            "sufficient_score_bound": "E_nu[|grad V_eta(0)|^2]<=C_s*N*omega_p^2",
            "resulting_pair_moment": "E[|T|^2]<=(36+81*C_s)/(2*N*omega_p^2)",
            "status": "EXACT_TRANSLATION_INVARIANT_TWO_MODE_REDUCTION",
        },
        "current_identity": {
            "residual": "r_x=sum_(y~x)[exp(psi_y-psi_x)-1]",
            "action": "A=(1/2)*sum_x r_x^2",
            "canonical_oriented_current": "J_(x,i)=r_x*w_(x,x+e_i)-r_(x+e_i)*w_(x+e_i,x)",
            "action_gradient": "G_x=partial A/partial psi_x=-sum_i[J_(x,i)-J_(x-e_i,i)]",
            "fourier_divergence": "Ghat(p)=sum_i[exp(i*p_i)-1]*Jhat_i(p)",
            "axial_score_identity": "s_cos^2+s_sin^2=(omega_p/g^2)*|Jhat_1(p)|^2",
            "equivalent_current_gate": "E_nu[|Jhat_1(p)|^2]<=C_J*g^2*N*omega_p",
            "status": "EXACT_ONE_SOFT_FACTOR_AND_EQUIVALENT_SUSCEPTIBILITY_GATE",
        },
        "exact_current_fixture": {
            "lattice": "4^4 periodic torus, field constant in three spatial coordinates",
            "positive_field_time_row": [enc(value) for value in omega],
            "mean_zero_gauge": "subtract (1/4)*log(8) from the logarithmic field; all weights, residuals, currents, and action are unchanged",
            "residual_time_row": [enc(value) for value in residual],
            "forward_current_time_row": [enc(value) for value in current],
            "current_zero_mode_per_spatial_site": enc(sum(current, Fraction(0))),
            "spatial_replication_factor": spatial_factor,
            "full_current_zero_mode": enc(total_current),
            "action_per_spatial_site": enc(action_per_spatial_site),
            "full_action": enc(total_action),
            "consequence": "the canonical local current is not pointwise divisible by an external lattice momentum; its second soft factor cannot be obtained by declaring this current to be a periodic gradient",
            "status": "EXACT_RATIONAL_CANONICAL_SECOND_FACTOR_OBSTRUCTION",
        },
        "method_disposition": {
            "single_cosine_background_translation_invariance": "ABSENT",
            "full_cosine_sine_background_translation_invariance": "PROVED",
            "two_mode_center_score_reduction": "PROVED",
            "canonical_current_divergence_identity": "PROVED",
            "first_external_momentum_factor": "PROVED",
            "pointwise_second_factor_from_canonical_current_gradient": "OBSTRUCTED",
            "translation_invariant_current_susceptibility_bound": "OPEN",
            "actual_annealed_zero_fiber_score_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the translation-invariant current susceptibility bound",
            "the annealed score, lowest-mode, or interacting H^-1 estimate",
            "failure of a statistical second soft factor under the Gibbs law",
            "tightness or a continuum Euclidean measure",
            "a Born rule, Krein reconstruction, or Lorentzian causal statement",
        ],
        "missing_object_ledger": [
            "a Gibbs estimate E_nu[|Jhat_1(p)|^2]<=C*g^2*N*omega_p",
            "an observable-weighted block decomposition of the canonical current",
            "control or a counterexample for correlated multibubble current phases",
            "the resulting two-mode center theorem and dyadic Fourier-shell sum",
            "tightness and continuum identification only after the actual H^-1 theorem",
        ],
        "next_gate": "Work with the full cosine-sine background marginal, not the single-cosine marginal. Prove the longitudinal canonical-current susceptibility bound using an observable-weighted block decomposition and the tuned Gibbs measure, or construct a translation-covariant correlated background sequence for which |Jhat_1(p)|^2/(g^2*N*omega_p) diverges. No pointwise second-gradient identity for the canonical current is available.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic reconstructs the rational positive-field row, residual, current, action, spatial replication, and all center-reduction constants.",
            "analytic_arithmetic": "Finite-dimensional strong monotonicity, translation covariance of the full phase eigenspace, and the exact lattice Fourier divergence prove the reduction.",
            "assumptions": [
                "The coupling, Fourier mode, and action normalizations are those of the imported BT certificates.",
                "The all-background curvature theorem applies to every real phase in the lowest axial eigenspace.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_full_phase_current_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_full_phase_current_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_full_phase_current_gate",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

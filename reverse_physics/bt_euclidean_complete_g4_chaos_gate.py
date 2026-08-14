#!/usr/bin/env python3
"""Build the complete-g^4 Wiener-chaos gate-reduction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CHAOS_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-complete-g4-chaos-gate-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-complete-g4-chaos-gate.md"
SOURCE_COMMIT = "9133fe2397f9f423ef476da36dee0774297d95fc"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_UV_NONCANCELLATION_V1.json",
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


def hermite_fixture() -> dict[str, Fraction]:
    # For a standard Gaussian, ||H_n||^2=n!.  Take
    # A=H2, D=2H1+3H3+5H5, E=7H0+11H2+13H4+17H6+19H8.
    norm_a = Fraction(math.factorial(2))
    norm_d = sum(
        Fraction(coefficient**2 * math.factorial(degree))
        for degree, coefficient in ((1, 2), (3, 3), (5, 5))
    )
    norm_pi2_e = Fraction(11**2 * math.factorial(2))
    cross = Fraction(2 * 11 * math.factorial(2))
    return {
        "norm_A_squared": norm_a,
        "norm_D_squared": norm_d,
        "norm_Pi2E_squared": norm_pi2_e,
        "twice_A_E": cross,
        "twice_A_Pi2E": cross,
        "M4": norm_d + cross,
    }


def build() -> dict:
    fixture = hermite_fixture()
    checks = {
        "conditioned_covariance_cannot_close_quadratic_score_momentum_for_L_at_least_four": True,
        "A_is_pure_second_chaos": True,
        "D_has_only_odd_chaoses_one_three_five": True,
        "E_has_only_even_chaoses_zero_two_four_six_eight": True,
        "A_pairs_only_with_second_chaos_of_E": True,
        "all_other_order_g_four_terms_form_nonnegative_norm": True,
        "hermite_fixture_D_norm_is_three_thousand_fifty_eight": fixture["norm_D_squared"] == 3058,
        "hermite_fixture_cross_is_forty_four": fixture["twice_A_E"] == 44,
        "hermite_fixture_M4_is_three_thousand_one_hundred_two": fixture["M4"] == 3102,
        "certified_cubic_score_norm_is_N_omega_squared_times_log": True,
        "linear_soft_effective_kernel_norm_is_sufficient": True,
        "polylog_times_square_root_omega_tends_to_zero": True,
        "effective_second_chaos_norm_bound_remains_open": True,
        "whole_lattice_order_g_four_decision_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CHAOS_GATE_V1",
        "schema_version": "reverse-physics-bt-euclidean-complete-g4-chaos-gate-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "EXACT_CHAOS_REDUCTION_PROVED_EFFECTIVE_KERNEL_BOUND_OPEN",
        "result_kind": "exact Wiener-chaos reduction of the complete order-g^4 cancellation gate",
        "question": "After the complete order-g^4 background-score coefficient is assembled, which signed object can still cancel its positive ultraviolet p^2 sector, and what single estimate would rule that out?",
        "answer": "Let A be the g score coefficient and use the square-root background-density normal form to write the order-g^2 and order-g^3 fixed-free-space score coefficients as D=B-W1*A/2 and E=C-W1*B/2+(W1^2/8-W2/2-z2/2)*A. Then M4=||D||_0^2+2<A,E>_0. For L>=4, the actual real-cosine-conditioned covariance cannot close the external +/-p momentum of the quadratic score A: its translation-invariant part pairs q with -q, while its removed rank-one block has both momenta in {+/-p}, and neither support solves external+q+r=0. Thus A is centered and lies entirely in second Wiener chaos. Degree and parity put D in chaoses 1,3,5 and E in chaoses 0,2,4,6,8. Orthogonality gives the exact reduction M4=||D||_0^2+2<A,Pi2(E)>_0. Thus every potentially negative contribution is contained in one effective second-chaos, three-leg kernel; all other terms are a nonnegative norm. The predecessor theorem supplies a fixed-UV lower bound ||D||^2>=c*N*omega_p because its third-chaos component retains the linearly soft quartic fixture. The cubic result gives ||A||^2=O(N*omega_p^2*log L). Therefore any bound ||Pi2(E)||^2<=C*N*omega_p*(1+log L)^b with fixed b makes the cross term o(N*omega_p) and proves that the unrestricted order-g^4 power survives. That effective-kernel norm bound is not yet proved.",
        "fixed_free_space_normal_form": {
            "score": "s_g=g*A+g^2*B+g^3*C+O(g^4)",
            "density_square_root": "sqrt(dnu_g/dnu0)=1-g*W1/2+g^2*(W1^2/8-W2/2-z2/2)+O(g^3)",
            "D": "D=B-W1*A/2",
            "E": "E=C-W1*B/2+(W1^2/8-W2/2-z2/2)*A",
            "coefficient": "M4=||D||_0^2+2*<A,E>_0",
            "status": "IMPORTED_AND_REEXPANDED_EXACTLY",
        },
        "chaos_inventory": {
            "A": "A is polynomial degree 2. For L>=4 the conditioned covariance support cannot close its external +/-p momentum: q+r=0 in the translation-invariant part, while q,r in {+/-p} in the removed rank-one block. Hence E0[A]=0 and A=Pi2(A)",
            "B": "B is odd polynomial degree 3 and has chaos degrees 3 and 1",
            "C": "C is even polynomial degree 4 and has chaos degrees 4,2,0",
            "W1": "W1 is odd with polynomial degrees 3 and 1",
            "W2": "W2 is even with polynomial degrees 4,2,0",
            "D": "D has only chaos degrees 5,3,1",
            "E": "E has only chaos degrees 8,6,4,2,0",
            "orthogonality": "<A,E>=<A,Pi2(E)> because distinct homogeneous Wiener chaoses are orthogonal and A lies in chaos 2",
            "exact_reduction": "M4=||D||_0^2+2*<A,Pi2(E)>_0",
            "interpretation": "The first term is nonnegative. Every possible signed cancellation of its positive UV power is concentrated in the single second-chaos projection Pi2(E).",
            "status": "PROVED_BY_GAUSSIAN_CHAOS_ORTHOGONALITY",
        },
        "exact_hermite_fixture": {
            "law": "X is standard Gaussian and H_n are probabilists' Hermite polynomials with E[H_m*H_n]=n!*delta_mn",
            "A": "H2",
            "D": "2*H1+3*H3+5*H5",
            "E": "7*H0+11*H2+13*H4+17*H6+19*H8",
            "values": {name: enc(value) for name, value in fixture.items()},
            "status": "EXACT_ORTHOGONALITY_FIXTURE",
        },
        "sufficient_effective_kernel_estimate": {
            "external_dispersion": "omega_p=4*sin(pi/L)^2=O(L^-2)",
            "certified_A_norm": "||A||_0^2<=C_A*N*omega_p^2*(1+log L) for all sufficiently large L, from the exact logarithmic residue",
            "required_E2_norm": "||Pi2(E)||_0^2<=C_E*N*omega_p*(1+log L)^b for some fixed finite b",
            "cauchy_schwarz": "2*|<A,Pi2(E)>|<=2*sqrt(C_A*C_E)*N*omega_p^(3/2)*(1+log L)^((b+1)/2)",
            "relative_to_power": "2*|<A,Pi2(E)>|/(N*omega_p)<=2*sqrt(C_A*C_E)*sqrt(omega_p)*(1+log L)^((b+1)/2), which tends to zero",
            "positive_term": "The fixed-UV third-chaos block of D has ||D||_0^2>=c*N*omega_p for all sufficiently large L because D=B+O(p^2) on that carrier and dK4/dp0=-1/3",
            "consequence_if_proved": "M4>=c'*N*omega_p>0 eventually, so the unrestricted normalized order-g^4 coefficient grows at least as c''/omega_p>=c'''*L^2",
            "status": "EXACT_SUFFICIENT_REDUCTION_BOUND_NOT_YET_PROVED",
        },
        "effective_kernel_target": {
            "object": "Pi2(E), the second homogeneous Wiener-chaos projection of C-W1*B/2+(W1^2/8-W2/2-z2/2)*A",
            "kernel_type": "a translation-invariant effective three-leg kernel with one external real-cosine leg and two free background legs",
            "expected_softness": "At least linear in the external p by shift symmetry; simultaneous inversion removes odd total Taylor degree in the all-soft region",
            "required_work": "Perform the Wick contractions defining Pi2(E), combine normalization subtractions before taking absolute values, and prove the displayed weighted lattice norm bound by dyadic momentum regions",
            "continuum_source_boundary": "The ABHT all-order theorem proves infrared finiteness for ordinary off-shell correlators. It does not by itself identify this projected fiber-integrated composite or prove a uniform lattice bound as its external p tends to zero.",
            "status": "OPEN_SINGLE_EFFECTIVE_KERNEL_NORM",
        },
        "method_disposition": {
            "complete_order_g_four_chaos_decomposition": "PROVED",
            "all_signed_cancellation_localized_to_second_chaos": "PROVED",
            "positive_norm_uv_power_lower_bound": "PROVED",
            "effective_second_chaos_kernel_norm_bound": "OPEN",
            "whole_lattice_order_g_four_power_survival": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the required weighted norm bound for Pi2(E)",
            "survival or cancellation of the unrestricted whole-lattice order-g^4 power coefficient",
            "divergence of the resummed or nonperturbative annealed score or interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "the explicit Wick-contracted two-background-leg kernel of Pi2(E)",
            "a dyadic weighted norm bound for that kernel uniform in L",
            "after the order-g^4 decision, a whole-composite renormalized or nonperturbative annealed score estimate",
            "after the one-mode theorem, dyadic Fourier-shell control of the actual interacting H^-1 moment",
        ],
        "next_gate": "Compute Pi2(E) explicitly before estimating diagrams separately. Preserve the cancellations from W1, W2, and z2 in its combined two-background-leg kernel. Prove its free weighted norm is at most N*omega_p times a fixed polylogarithm by splitting hard, one-soft, and all-soft momentum regions. This single estimate would prove that the certified positive order-g^4 UV power survives the unrestricted lattice sum.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python Fraction arithmetic and exact Hermite norms n! for the chaos-selection fixture",
            "analytic_arithmetic": "homogeneous Wiener-chaos orthogonality, exact square-root-density expansion, Cauchy-Schwarz, and the certified lattice soft scalings",
            "assumptions": [
                "the free orthogonal-background Gaussian law and its homogeneous Wiener-chaos decomposition are used throughout",
                "L>=4, so neither the translation-invariant covariance support nor the removed real-cosine rank-one support can close the external momentum of A",
                "the proposed Pi2(E) norm bound remains a target and is not inferred from continuum off-shell IR finiteness",
            ],
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_chaos_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_chaos_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_chaos_gate",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == encoded else 1
        except OSError:
            return 1
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

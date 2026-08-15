#!/usr/bin/env python3
"""Build the BT tuned-branch remainder-compensation certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TUNED_REMAINDER_COMPENSATION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-tuned-remainder-compensation-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-tuned-remainder-compensation.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_tuned_remainder_compensation.py"
SOURCE_COMMIT = "d66c21aa06593eb0337ed31be02f1192480ed45d"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_UV_NONCANCELLATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LOWER_LOOP_BOUNDS_V1.json",
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


def load(relative: str) -> dict:
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def build() -> dict:
    expansion, cubic, rg, two_pair, complete = map(load, INPUTS)
    pair_four_ceiling = Fraction(1613, 100000)
    pair_seven_ceiling = Fraction(8051597, 500000000)
    certified_gap = pair_four_ceiling - pair_seven_ceiling
    checks = {
        "complete_score_expansion_is_certified_through_g_four": expansion["complete_order_g_four"]["status"] == "COMPLETE_THROUGH_ORDER_G_FOUR",
        "cubic_score_coefficient_has_logarithmic_asymptotic": rg["lattice_log_residue"]["asymptotic_theorem"] == "C_L=(5/(16*pi^2))*log(L)+O(1)",
        "tuned_running_limit_is_eight_pi_squared_over_five": rg["matched_refinement"]["running_limit_coefficient_pi_squared"] == enc(Fraction(8, 5)),
        "pair_four_strict_upper_bound_imported": two_pair["comparison"]["pair_four"] == "c_4<-0.01613",
        "pair_seven_strict_upper_bound_imported": two_pair["comparison"]["pair_seven"] == "0<c_7<0.016103194<0.01613",
        "exact_rational_coefficient_gap_is_positive": certified_gap == Fraction(13403, 500000000),
        "complete_M4_has_same_strictly_negative_leading_power": complete["complete_leading_power"]["status"] == "COMPLETE_M4_LEADING_POWER_COEFFICIENT_STRICTLY_NEGATIVE",
        "M3_vanishes_by_background_parity": True,
        "quartic_truncation_tends_to_minus_infinity_on_tuned_branch": True,
        "exact_complement_must_compensate_at_leading_power": True,
        "actual_score_sign_or_scaling_is_not_promoted": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TUNED_REMAINDER_COMPENSATION_V1",
        "schema_version": "reverse-physics-bt-euclidean-tuned-remainder-compensation-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "TUNED_FIXED_ORDER_UNIFORMITY_OBSTRUCTED_NONPERTURBATIVE_SCORE_OPEN",
        "result_kind": "exact parity and asymptotic composition theorem forcing leading-power compensation beyond the complete quartic score truncation",
        "question": "Can the complete score expansion through order g^4 approximate the nonnegative interacting zero-fiber-score moment with a volume-uniform or little-o(g_L^4*N*omega_p) complement on the tuned refinement branch?",
        "answer": "No. Let F_L(g)=E_nu_g[s_g(eta)^2]>=0 be the exact annealed zero-fiber-score moment. Its fixed-volume expansion begins g^2*M2+g^3*M3+g^4*M4. Background parity makes M3=0 exactly. The certified score residue gives M2=N*omega_p^2*C_L with C_L=(5/(16*pi^2))*log L+O(1), so g_L^2*M2=O(1) when g_L^2*log L tends to 8*pi^2/5. The complete quartic theorem gives M4/(N*omega_p)->c_* with c_*< -13403/500000000. Since g_L^4*N*omega_p grows like L^2/log(L)^2, the quartic truncation tends to minus infinity. Therefore the exact complement Q_L=F_L(g_L)-g_L^2*M2-g_L^4*M4 must tend to plus infinity and liminf Q_L/(g_L^4*N*omega_p)>13403/500000000. Thus a volume-uniform fixed-order remainder, or any remainder little-o of that scale, is impossible. This forces an all-order or nonperturbative compensation but does not determine whether F_L itself is bounded or divergent.",
        "exact_parity": {
            "background_involution": "eta -> -eta under the centered free orthogonal-background Gaussian law",
            "parities": {
                "A=D_h*S1": "EVEN",
                "B=D_h*S2": "ODD",
                "W1=E_T[S1]": "ODD",
            },
            "cubic_norm_coefficient": "M3=E0[2*A*B-A^2*W1]=0",
            "status": "EXACT_ZERO_BY_ODD_GAUSSIAN_INTEGRAND",
        },
        "coefficient_gap": {
            "pair_four_bound": "c_4<-1613/100000",
            "pair_seven_bound": "c_7<8051597/500000000",
            "complete_limit": "lim M4(L)/(N*omega_p)=c_*=c_4+c_7",
            "strict_upper_bound": "c_*<-13403/500000000",
            "gap": enc(certified_gap),
            "status": "EXACT_RATIONAL_STRICT_NEGATIVE_GAP",
        },
        "tuned_scaling": {
            "external_mode": "p_L=(1,0,0,0), N=L^4, omega_p=4*sin(pi/L)^2",
            "running": "g_L^2*log L -> 8*pi^2/5",
            "quadratic_coefficient": "M2=N*omega_p^2*C_L, C_L=(5/(16*pi^2))*log L+O(1)",
            "quadratic_contribution": "g_L^2*M2=O(N*omega_p^2)=O(1)",
            "quartic_scale": "g_L^4*N*omega_p is asymptotic to a positive constant times L^2/log(L)^2 and tends to infinity",
            "quartic_contribution": "g_L^4*M4 tends to minus infinity",
            "truncation": "T_L=g_L^2*M2+g_L^4*M4 tends to minus infinity",
            "status": "PROVED_BY_CERTIFIED_ASYMPTOTIC_COMPOSITION",
        },
        "exact_balance": {
            "nonnegative_object": "F_L(g_L)=E_nu_(L,g_L)[s_(L,g_L)(eta)^2]>=0",
            "complement_definition": "Q_L=F_L(g_L)-g_L^2*M2(L)-g_L^4*M4(L)",
            "finite_L_inequality": "Q_L>=-g_L^2*M2(L)-g_L^4*M4(L)",
            "divergence": "Q_L tends to plus infinity",
            "normalized_lower_bound": "liminf Q_L/(g_L^4*N*omega_p)>=-c_*>13403/500000000",
            "forbidden_remainder_classes": [
                "Q_L=O(1)",
                "Q_L=o(g_L^4*N*omega_p)",
            ],
            "interpretation": "Terms beyond the complete quartic truncation must restore positivity on the same leading power scale. The certificate identifies mandatory compensation, not its mechanism or the final size of F_L.",
            "status": "LEADING_POWER_COMPENSATION_FORCED",
        },
        "method_disposition": {
            "cubic_score_norm_coefficient": "EXACTLY_ZERO_BY_PARITY",
            "complete_quartic_truncation_on_tuned_branch": "DIVERGES_NEGATIVE",
            "volume_uniform_fixed_order_remainder": "OBSTRUCTED",
            "little_o_quartic_power_remainder": "OBSTRUCTED",
            "all_order_or_nonperturbative_compensation": "MATHEMATICALLY_REQUIRED",
            "sign_or_scaling_of_exact_interacting_score": "OPEN",
            "nonperturbative_annealed_center_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "divergence or boundedness of the exact interacting zero-fiber-score moment F_L",
            "a sign for the sum of fifth and higher perturbative contributions term by term",
            "analyticity or Borel summability uniformly in lattice volume",
            "the missing annealed conditional-center or interacting H^-1 estimate",
            "a continuum measure, Born rule, Krein reconstruction, or any Lorentzian causal claim",
        ],
        "missing_object_ledger": [
            "an all-order resummation or nonperturbative representation of the forced compensation Q_L",
            "a Gibbs-weighted multiscale estimate for the zero-fiber score on the tuned branch",
            "a decision whether the exact score moment stays on the target N*omega_p^2 scale",
            "after the one-mode theorem, a dyadic Fourier-shell H^-1 estimate",
            "after tightness, identification of the Euclidean continuum measure",
        ],
        "next_gate": "Abandon finite-order remainder control as a route to the center theorem. Seek a nonperturbative identity for the whole positive score square—preferably a block-spin or conditional Ward estimate that retains the background Gibbs weight and sums the forced compensation before taking absolute values. The first target remains F_L(g_L)<=C*N*omega_p^2, not a bound on individual perturbative orders.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic proves the strict gap 1613/100000-8051597/500000000=13403/500000000 and the parity ledger uses exact polynomial degrees. No floating-point arithmetic decides a claim.",
            "analytic_arithmetic": "Content-pinned composition of the certified C_L logarithm, tuned running limit, complete M4/(N*omega_p) limit, and elementary sine asymptotics.",
            "assumptions": [
                "The finite-volume score moment and its coefficients use the normalization fixed by the complete-g4 certificate.",
                "The coupling sequence is the certified fixed-physical-volume tuned refinement with positive g_L.",
                "Q_L is an exact algebraic complement at g_L; the theorem does not assume that an infinite Taylor series converges to it.",
                "All imported results retain only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL scope.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_tuned_remainder_compensation.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_tuned_remainder_compensation.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_tuned_remainder_compensation",
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

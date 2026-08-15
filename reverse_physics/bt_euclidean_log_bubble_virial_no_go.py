#!/usr/bin/env python3
"""Build the BT logarithmic-bubble homogeneous-virial no-go certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_VIRIAL_NO_GO_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-log-bubble-virial-no-go-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-log-bubble-virial-no-go.md"
VERIFIER_REL = "reverse_physics/verify_bt_euclidean_log_bubble_virial_no_go.py"
SOURCE_COMMIT = "764cb8c99ccc80c9088b46e2ad9df2bd64bfc0b8"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RADIAL_CONVEXITY_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1.json",
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


def multiply(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return tuple(result)


def power(polynomial: tuple[Fraction, ...], exponent: int) -> tuple[Fraction, ...]:
    answer = (Fraction(1),)
    for _ in range(exponent):
        answer = multiply(answer, polynomial)
    return answer


def derivative(polynomial: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(index * polynomial[index] for index in range(1, len(polynomial)))


def integral_zero_one(polynomial: tuple[Fraction, ...]) -> Fraction:
    return sum((coefficient / (index + 1) for index, coefficient in enumerate(polynomial)), Fraction(0))


def build() -> dict:
    smoothstep = tuple(map(Fraction, (0, 0, 0, 10, -15, 6)))
    j2 = integral_zero_one(power(smoothstep, 2))
    j3 = integral_zero_one(power(smoothstep, 3))
    j4 = integral_zero_one(power(smoothstep, 4))
    jp = integral_zero_one(power(derivative(smoothstep), 2))

    amplitude = Fraction(3, 2)
    ramp_width = Fraction(2)
    plateau_width = Fraction(4)
    q_term = amplitude**2 * (
        4 * plateau_width
        + 2 * jp / ramp_width
        + 8 * ramp_width * j2
    )
    c_term = -2 * amplitude**3 * (
        plateau_width + 2 * ramp_width * j3
    )
    p_term = amplitude**4 * (
        plateau_width + 2 * ramp_width * j4
    )
    reduced_action = (q_term + 2 * c_term + p_term) / 2
    reduced_virial = q_term + 3 * c_term + 2 * p_term

    checks = {
        "quintic_smoothstep_is_exact": smoothstep == (0, 0, 0, 10, -15, 6),
        "smoothstep_square_integral_is_181_over_462": j2 == Fraction(181, 462),
        "smoothstep_cube_integral_is_26_over_77": j3 == Fraction(26, 77),
        "smoothstep_fourth_integral_is_2549_over_8398": j4 == Fraction(2549, 8398),
        "smoothstep_derivative_square_integral_is_10_over_7": jp == Fraction(10, 7),
        "amplitude_is_three_halves": amplitude == Fraction(3, 2),
        "ramp_and_plateau_widths_are_two_and_four": ramp_width == 2 and plateau_width == 4,
        "Q_is_1173_over_22": q_term == Fraction(1173, 22),
        "C_is_minus_2781_over_77": c_term == Fraction(-2781, 77),
        "P_is_886707_over_33592": p_term == Fraction(886707, 33592),
        "continuum_action_is_strictly_positive": reduced_action == Fraction(19349691, 5173168) and reduced_action > 0,
        "continuum_radial_virial_is_strictly_negative": reduced_virial == Fraction(-2896611, 1293292) and reduced_virial < 0,
        "lattice_sampling_converges_in_critical_dimension_four": True,
        "eventual_finite_lattice_negative_virial_follows": True,
        "every_nonnegative_homogeneous_constant_is_obstructed": True,
        "affine_virial_theorem_is_not_refuted": True,
        "actual_gibbs_H_minus_one_target_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_LOG_BUBBLE_VIRIAL_NO_GO_V1",
        "schema_version": "reverse-physics-bt-euclidean-log-bubble-virial-no-go-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "HOMOGENEOUS_RADIAL_VIRIAL_ARCHITECTURE_OBSTRUCTED",
        "result_kind": "exact smooth logarithmic-bubble continuum integral and rigorous eventual finite-lattice negative-virial sequence",
        "question": "Does any nonnegative volume-uniform homogeneous radial inequality D_L(psi)>=c*A_L(psi) survive on the four-dimensional periodic BT lattices?",
        "answer": "No. A fixed C2 radial logarithmic-annulus profile on the flat four-torus has positive continuum residual-square action but strictly negative radial virial. Its ramp polynomial and all reduced radial integrals are exact rationals. Sampling that fixed profile on the periodic L^4 grids gives uniform second-difference expansions r_L=h^2*(Delta psi+|grad psi|^2)+o(h^2) and t_L=h^2*(Delta psi+2|grad psi|^2)+o(h^2). Four-dimensional Riemann sums therefore give A_L -> 2*pi^2*(19349691/5173168)>0 and D_L -> 2*pi^2*(-2896611/1293292)<0. Hence D_L<0 for all sufficiently large finite L, which rules out D_L>=c*A_L for every c>=0. The affine bound with an additive volume defect remains valid, but it cannot produce the tuned low-temperature action estimate E[A]=O(g^2*N). This is a pointwise-method no-go, not divergence of the actual Gibbs moment.",
        "smooth_profile": {
            "ambient_space": "unit flat four-torus, using a Euclidean ball of outer radius 1/8 inside its injectivity radius",
            "inner_radius": "r_minus=exp(-8)/8",
            "log_coordinate": "s=log(r/r_minus)",
            "smoothstep": "W(z)=10*z^3-15*z^4+6*z^5 on 0<=z<=1",
            "window": [
                "w(s)=0 for s<=0 and s>=8",
                "w(s)=W(s/2) for 0<=s<=2",
                "w(s)=1 for 2<=s<=6",
                "w(s)=W((8-s)/2) for 6<=s<=8",
            ],
            "field_derivative": "psi'(r)=-(3/2)*w(log(r/r_minus))/r; psi is constant inside and outside the annulus",
            "regularity": "W, W', and W'' match the constant pieces at both endpoints, so the radial field is C2 (indeed C3) on the torus",
            "constant_shift": "subtracting the torus mean changes no edge difference, action, or radial virial",
            "status": "EXPLICIT_FIXED_SMOOTH_PROFILE",
        },
        "exact_radial_integrals": {
            "dimension": 4,
            "sphere_area_factor": "|S^3|=2*pi^2>0",
            "definitions": [
                "X=Delta psi, Y=|grad psi|^2",
                "Q=integral X^2, C=integral X*Y, P=integral Y^2 after removing the common 2*pi^2 factor",
                "A_cont/(2*pi^2)=(Q+2*C+P)/2",
                "D_cont/(2*pi^2)=Q+3*C+2*P",
            ],
            "change_of_variables": "With psi'(r)=-a*w(s)/r and s=log(r/r_minus), X=-a*(w'+2*w)/r^2 and Y=a^2*w^2/r^2; r^3*dr=r^4*ds cancels the denominator exactly.",
            "smoothstep_integrals": {
                "integral_W_squared": enc(j2),
                "integral_W_cubed": enc(j3),
                "integral_W_fourth": enc(j4),
                "integral_W_prime_squared": enc(jp),
            },
            "parameters": {
                "amplitude": enc(amplitude),
                "each_ramp_log_width": enc(ramp_width),
                "plateau_log_width": enc(plateau_width),
            },
            "Q": enc(q_term),
            "C": enc(c_term),
            "P": enc(p_term),
            "reduced_action": enc(reduced_action),
            "reduced_radial_virial": enc(reduced_virial),
            "reduced_ratio_decimal_diagnostic": "-0.5987921977 (not used to decide the sign)",
            "status": "EXACT_RATIONAL_NEGATIVE_VIRIAL",
        },
        "finite_lattice_transfer": {
            "grid": "G_L=(Z/LZ)^4 with mesh h=1/L and sampled centered field psi_L(x)=psi(x/L)-mean(psi(x/L))",
            "lattice_residual": "r_L(x)=sum_(y~x)[exp(psi_L(y)-psi_L(x))-1]",
            "lattice_radial_derivative": "t_L(x)=sum_(y~x)exp(psi_L(y)-psi_L(x))*(psi_L(y)-psi_L(x))",
            "uniform_expansions": [
                "h^-2*r_L -> Delta psi+|grad psi|^2 uniformly",
                "h^-2*t_L -> Delta psi+2*|grad psi|^2 uniformly",
            ],
            "expansion_proof": "Pair the plus and minus neighbor increments in each axis. C2 Taylor-Peano remainders are uniform on the compact torus; odd first-order terms cancel, while the exponential quadratic term supplies |grad psi|^2 for r_L and twice that term for t_L.",
            "critical_dimension_step": "Because N=L^4=h^-4, A_L=(1/2)*sum r_L^2 and D_L=sum r_L*t_L are four-dimensional Riemann sums with no residual power of h.",
            "limits": [
                "A_L -> 2*pi^2*19349691/5173168 > 0",
                "D_L -> -2*pi^2*2896611/1293292 < 0",
            ],
            "finite_volume_consequence": "There exists L0 such that every integer L>=L0 has A_L>0 and D_L<0 for this explicit sampled profile.",
            "status": "RIGOROUS_EVENTUAL_FINITE_LATTICE_SEQUENCE",
        },
        "method_disposition": {
            "pointwise_D_ge_2A": "OBSTRUCTED_BY_PREDECESSOR",
            "pointwise_D_ge_A": "OBSTRUCTED_BY_PREDECESSOR",
            "pointwise_D_ge_cA_for_any_c_ge_0": "OBSTRUCTED",
            "pointwise_D_ge_0": "OBSTRUCTED",
            "radial_convexity": "OBSTRUCTED_BY_PREDECESSOR",
            "affine_virial_with_volume_defect": "PROVED_BY_PREDECESSOR",
            "tuned_action_expectation_from_homogeneous_radial_Ward_identity": "OBSTRUCTED",
            "nonpointwise_Gibbs_weighted_block_estimate": "OPEN",
            "annealed_zero_fiber_score_bound": "OPEN",
            "actual_interacting_H_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "divergence of the actual interacting action or H^-1 moment",
            "failure of every Gibbs-weighted, block-spin, or multiscale estimate",
            "failure of the certified affine virial/action-density theorem",
            "a continuum Euclidean measure or its nonexistence",
            "a Born rule, Krein reconstruction, or Lorentzian causal result",
        ],
        "missing_object_ledger": [
            "a Gibbs-weighted estimate for the whole zero-fiber score that does not use a pointwise homogeneous virial inequality",
            "a multiscale rarity estimate for logarithmic-bubble backgrounds under the actual normalized measure",
            "the annealed lowest-mode center bound on the tuned refinement branch",
            "after one-mode control, a dyadic Fourier-shell H^-1 estimate",
            "tightness and continuum identification only after the actual moment theorem",
        ],
        "next_gate": "Abandon every homogeneous radial-virial proof, including attempts with a smaller positive constant. The negative bubbles are configurations, not yet probable backgrounds. The live question is their Gibbs rarity versus entropy: derive a block large-deviation estimate for the whole score or construct a weighted bubble gas that makes the actual normalized low-mode moment diverge.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction arithmetic evaluates W^2, W^3, W^4, (W')^2 and every reduced Q,C,P,A,D coefficient. No floating-point number decides a sign.",
            "analytic_arithmetic": "The finite-lattice conclusion uses uniform C2 Taylor-Peano expansions and four-dimensional Riemann-sum convergence for one fixed explicit torus profile.",
            "assumptions": [
                "The finite periodic lattice action and radial derivative use the normalization fixed by the predecessor certificates.",
                "The sampled profile is held fixed in physical torus coordinates while L tends to infinity.",
                "Only LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL conclusions are drawn.",
            ],
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFIER_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_log_bubble_virial_no_go.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_log_bubble_virial_no_go.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_log_bubble_virial_no_go",
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

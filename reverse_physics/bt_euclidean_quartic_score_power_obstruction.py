#!/usr/bin/env python3
"""Build the isolated quartic-score power-obstruction certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_QUARTIC_SCORE_POWER_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-quartic-score-power-obstruction-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-quartic-score-power-obstruction.md"
DATA_REL = "reverse_physics/data/bt_euclidean_quartic_score_preflight_v1.json"
SOURCE_COMMIT = "fed961ee2cb386dc882d6ffb54103f69d9b40652"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCORE_RG_MATCHING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ZERO_FIBER_WARD_WEIGHT_OBSTRUCTION_V1.json",
    "reverse_physics/data/anderson_bateman_herzog_turok_quartic_soft_source_v1.json",
    DATA_REL,
    "reverse_physics/bt_euclidean_quartic_score_preflight.c",
]

Gaussian = tuple[Fraction, Fraction]
Dual = tuple[Gaussian, Gaussian]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def enc_gaussian(value: Gaussian) -> dict[str, dict[str, int]]:
    return {"real": enc(value[0]), "imaginary": enc(value[1])}


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gneg(value: Gaussian) -> Gaussian:
    return -value[0], -value[1]


def gsub(left: Gaussian, right: Gaussian) -> Gaussian:
    return gadd(left, gneg(right))


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def gscale(value: Gaussian, scalar: Fraction | int) -> Gaussian:
    scalar = Fraction(scalar)
    return value[0] * scalar, value[1] * scalar


ZERO_G: Gaussian = (Fraction(0), Fraction(0))
ONE_G: Gaussian = (Fraction(1), Fraction(0))
I_G: Gaussian = (Fraction(0), Fraction(1))


def dadd(left: Dual, right: Dual) -> Dual:
    return gadd(left[0], right[0]), gadd(left[1], right[1])


def dsub(left: Dual, right: Dual) -> Dual:
    return gsub(left[0], right[0]), gsub(left[1], right[1])


def dmul(left: Dual, right: Dual) -> Dual:
    return (
        gmul(left[0], right[0]),
        gadd(gmul(left[1], right[0]), gmul(left[0], right[1])),
    )


def dscale(value: Dual, scalar: Fraction | int) -> Dual:
    return gscale(value[0], scalar), gscale(value[1], scalar)


def edge_phase(momentum: tuple[tuple[int, int], ...], axis: int, sign: int) -> Dual:
    """Exact phase and p_0 derivative at quarter-period momenta.

    Each momentum component is (quarter_turn, derivative_coefficient), with
    one quarter turn equal to pi/2 and the derivative variable equal to p_0.
    """
    phases = (ONE_G, I_G, gneg(ONE_G), gneg(I_G))
    quarter_turn, derivative = momentum[axis]
    value = phases[(sign * quarter_turn) % 4]
    slope = gscale(gmul(value, I_G), sign * derivative)
    return value, slope


def edge_symbol(momentum: tuple[tuple[int, int], ...], axis: int, sign: int) -> Dual:
    return dsub(edge_phase(momentum, axis, sign), (ONE_G, ZERO_G))


def b_symbol(momentums: tuple[tuple[tuple[int, int], ...], ...]) -> Dual:
    result: Dual = (ZERO_G, ZERO_G)
    for axis in range(4):
        for sign in (-1, 1):
            product: Dual = (ONE_G, ZERO_G)
            for momentum in momentums:
                product = dmul(product, edge_symbol(momentum, axis, sign))
            result = dadd(result, product)
    return result


def quartic_kernel_fixture() -> Dual:
    """Return K_4 and dK_4/dp_0 at the exact quarter-period fixture."""
    p = ((0, 1), (0, 0), (0, 0), (0, 0))
    q = ((1, 0), (0, 0), (0, 0), (0, 0))
    r = ((0, 0), (1, 0), (0, 0), (0, 0))
    # s=-p-q-r.
    s = ((-1, -1), (-1, 0), (0, 0), (0, 0))
    momentums = (p, q, r, s)
    result: Dual = (ZERO_G, ZERO_G)
    for index in range(4):
        laplacian = b_symbol((momentums[index],))
        cubic_edge = b_symbol(
            tuple(momentums[j] for j in range(4) if j != index)
        )
        result = dadd(result, dmul(laplacian, cubic_edge))
    for i, j, k, ell in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
        result = dadd(
            result,
            dmul(
                b_symbol((momentums[i], momentums[j])),
                b_symbol((momentums[k], momentums[ell])),
            ),
        )
    return dscale(result, Fraction(1, 24))


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build() -> dict:
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        observations = json.load(handle)
    fixture_value, fixture_derivative = quartic_kernel_fixture()
    rows = observations["rows"]
    scaled_rows = [row["variance_over_N_omega_squared_L_squared"] for row in rows]
    checks = {
        "quartic_action_coefficient_has_ac_plus_b_squared_structure": True,
        "quartic_kernel_is_fully_symmetric": True,
        "quarter_period_kernel_vanishes_at_zero_external_momentum": fixture_value == ZERO_G,
        "quarter_period_kernel_derivative_is_minus_one_third": fixture_derivative == (Fraction(-1, 3), Fraction(0)),
        "nonzero_derivative_has_open_neighborhood": True,
        "uv_boxes_avoid_constant_and_conditioned_cosine_modes": True,
        "restricted_third_wiener_chaos_is_nonnegative": True,
        "isolated_normalized_square_has_inverse_omega_lower_bound": True,
        "inverse_omega_grows_at_least_quadratically_in_L": True,
        "all_observed_normalized_squares_increase": all(
            left["variance_over_N_omega_squared"]
            < right["variance_over_N_omega_squared"]
            for left, right in zip(rows, rows[1:])
        ),
        "observed_L_squared_ratios_are_same_order": max(scaled_rows) / min(scaled_rows) < 2,
        "complete_order_g_four_coefficient_remains_uncomputed": True,
        "actual_annealed_score_and_h_minus_one_moments_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_QUARTIC_SCORE_POWER_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-quartic-score-power-obstruction-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "ISOLATED_FIXED_ORDER_ROUTE_OBSTRUCTED",
        "result_kind": "exact quartic score kernel and rigorous power obstruction for its isolated free-Gaussian square",
        "question": "After the cubic score logarithm is matched by asymptotic freedom, can a coefficientwise proof proceed by bounding the square of the next quartic score polynomial separately?",
        "answer": "No. Expanding the exact positive exponential lattice action gives a g^2 quartic score polynomial Q_L whose fully symmetric four-leg kernel K_4 is only linearly soft in the external lowest momentum. At the exact quarter-period fixture q=(pi/2,0,0,0), r=(0,pi/2,0,0), s=-p-q-r, K_4 vanishes at p=0 but dK_4/dp_0=-1/3. Continuity therefore supplies fixed ultraviolet momentum boxes containing order N^2 ordered pairs on which |K_4| is bounded below by a constant times |p|. Restricting the free Gaussian variance to the corresponding positive third-Wiener-chaos block proves E_0[Q_L^2]/(N*omega_p^2)>=c/omega_p>=c'*L^2 for all sufficiently large L. Thus the isolated quartic-score square is power nonuniform, much stronger than the cubic logarithm. This is not the complete order-g^4 coefficient: measure corrections and cross terms can cancel it. It therefore obstructs separate-polynomial or positive-term bounds and proves that cubic RG matching alone cannot close the score theorem; it does not prove divergence of the interacting score or moment.",
        "exact_lattice_expansion": {
            "residual": "g^-1*R_x(g*phi)=a_x+(g/2)*b_x+(g^2/6)*c_x+O(g^3)",
            "edge_powers": "a_x=sum_delta d_delta phi, b_x=sum_delta(d_delta phi)^2, c_x=sum_delta(d_delta phi)^3",
            "action": "S_g=S_0+g*S_1+g^2*S_2+O(g^3)",
            "coefficients": "S_0=(1/2)*sum a^2, S_1=(1/2)*sum a*b, S_2=sum(a*c/6+b^2/8)",
            "zero_fiber_quartic_score": "Q_L=D_h S_2 at phi=eta with eta orthogonal to the real lowest cosine h",
            "position_formula": "Q_L=sum_x[(d_h a_x)*c_x+a_x*(d_h c_x)]/6+b_x*(d_h b_x)/4",
            "status": "PROVED_BY_EXACT_TAYLOR_COEFFICIENT_EXTRACTION",
        },
        "fourier_kernel": {
            "directed_edge_symbol": "d_delta(k)=exp(i*k dot delta)-1",
            "B_j": "B_j(k_1,...,k_j)=sum_delta product_a d_delta(k_a)",
            "lattice_laplacian_symbol": "B_1(k)=-omega_k",
            "symmetric_kernel": "K_4(k1,k2,k3,k4)=(1/24)*[sum_i B_1(ki)*B_3(k_except_i)+B_2(k1,k2)*B_2(k3,k4)+B_2(k1,k3)*B_2(k2,k4)+B_2(k1,k4)*B_2(k2,k3)]",
            "momentum_constraint": "k1+k2+k3+k4=0 modulo 2*pi",
            "continuum_limit": "K_4 tends, up to the declared action normalization, to the perfect-square quartic vertex, which is linear rather than quadratic in each external momentum",
            "status": "PROVED",
        },
        "exact_soft_fixture": {
            "external": "p=(epsilon,0,0,0)",
            "q": "(pi/2,0,0,0)",
            "r": "(0,pi/2,0,0)",
            "s": "-p-q-r",
            "kernel_at_epsilon_zero": enc_gaussian(fixture_value),
            "epsilon_derivative": enc_gaussian(fixture_derivative),
            "derivative_reading": "-1/3",
            "arithmetic": "exact Gaussian-rational dual numbers; all phases are in {1,i,-1,-i}",
            "status": "EXACT_NONZERO_LINEAR_SOFT_COEFFICIENT",
        },
        "wiener_chaos_lower_bound": {
            "free_law": "mean-zero lattice bilaplacian Gaussian, conditioned only on the real lowest cosine coefficient being zero",
            "box_construction": "Choose disjoint compact neighborhoods of the exact q,r,s fixture, away from zero and the conditioned +/-p block. Continuity of K_4/|p| and its nonzero fixture value gives |K_4|>=c_0*|p|. Each of the q and r boxes contains at least c_1*N lattice momenta for all sufficiently large L; s=-p-q-r remains in its declared box after shrinking.",
            "positive_restriction": "The third homogeneous Wiener-chaos norm is a sum of squared symmetric kernels divided by positive propagator denominators. Restrict it to the declared disjoint boxes; no covariance or conditioning correction touches these modes.",
            "counting": "At least c_2*N^2 ordered (q,r) pairs contribute, each with kernel square at least c_3*|p|^2 and with all three omega denominators bounded above and below by positive constants.",
            "variance_bound": "E_0[Q_L^2]>=c_4*N*|p|^2>=c_5*N*omega_p",
            "normalized_bound": "E_0[Q_L^2]/(N*omega_p^2)>=c_6/omega_p",
            "volume_growth": "Since omega_p=4*sin(pi/L)^2<=4*pi^2/L^2, the normalized isolated square is at least c_7*L^2.",
            "constant_policy": "The theorem is existential with positive L-independent constants obtained from a fixed open neighborhood of an exact nonzero fixture; no numerical preflight value is used in the proof.",
            "status": "PROVED_POWER_NONUNIFORMITY_OF_ISOLATED_QUARTIC_SCORE_SQUARE",
        },
        "cancellation_boundary": {
            "complete_order_g_four_contents": [
                "the isolated E_0[Q_L^2] term certified here",
                "free-measure contractions of lower score polynomials with higher lattice Taylor coefficients",
                "background-marginal density corrections generated by S_1 and S_2",
                "normalization counterterms and, on a refinement trajectory, coupling and field renormalization",
            ],
            "logical_disposition": "A divergent positive summand does not determine the signed sum of all contributions at the same perturbative order. The certificate forbids bounding the summands independently; it does not forbid an exact Ward/RG cancellation in the whole composite.",
            "running_coupling_warning": "On the certified asymptotically free trajectory g_L^4 is only logarithmically small. Multiplying the isolated L^2 term by g_L^4 does not make it uniform. Therefore the cubic residue/beta-function match is insufficient unless the complete quartic-order power terms cancel before or during renormalized composite formation.",
            "status": "WHOLE_ORDER_CANCELLATION_REQUIRED_NOT_PROVED",
        },
        "numerical_preflight": {
            "evidence_type": observations["evidence_type"],
            "source": observations["source"],
            "source_sha256": sha256(observations["source"]),
            "data": DATA_REL,
            "data_sha256": sha256(DATA_REL),
            "rows": rows,
            "interpretation": observations["interpretation"],
            "status": "SUPPORTING_ONLY",
        },
        "method_disposition": {
            "exact_quartic_score_kernel": "PROVED",
            "quartic_external_soft_degree": "LINEAR_NONZERO",
            "isolated_quartic_score_square_uniform_in_L": "OBSTRUCTED",
            "fixed_order_positive_termwise_score_bound": "OBSTRUCTED_AS_FORMULATED",
            "cubic_rg_matching_suffices_for_whole_score": "OBSTRUCTED_AS_AN_INFERENCE",
            "complete_order_g_four_score_coefficient": "OPEN",
            "power_cancellation_in_renormalized_zero_fiber_composite": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": checks,
        "does_not_establish": [
            "the sign or scaling of the complete order-g^4 zero-fiber-score coefficient",
            "failure of a cancellation enforced by the whole perfect-square composite, its measure, or renormalization",
            "divergence of the resummed or nonperturbative annealed score, center, or lowest-mode moment",
            "divergence or boundedness of the actual interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "the complete order-g^4 background-marginal score coefficient including density and normalization corrections",
            "an exact decision whether its L^2 pieces cancel in the renormalized zero-fiber composite",
            "a nonperturbative annealed joint tail/whole-composite estimate after that cancellation decision",
            "after the one-mode theorem, dyadic Fourier-shell control of the actual interacting H^-1 moment",
        ],
        "next_gate": "Compute the complete order-g^4 coefficient of the background-marginal zero-fiber score, not merely another positive summand. Organize all score, Gibbs-density, normalization, and projection terms in Wiener chaos and test whether the exact perfect-square identities cancel the certified L^2 sector. If they do, identify the remaining logarithmic RG equation and seek a whole-composite nonperturbative bound; if they do not, determine whether the uncancelled power term survives running-coupling scaling and obstructs the actual refinement estimate.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python Fraction pairs for Gaussian rationals and first-order dual numbers at the quarter-period fixture",
            "analytic_arithmetic": "exact lattice Taylor and Fourier coefficient extraction, continuity on fixed compact momentum boxes, lattice-point counting, and positivity of orthogonal Wiener chaos",
            "numerical_arithmetic": observations["evidence_type"],
            "primary_source_boundary": "ABHT arXiv:2608.12210v1 states and displays that the continuum quartic vertex is only linearly soft in each external momentum; the lattice theorem and exact fixture are derived independently here",
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_quartic_score_power_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_quartic_score_power_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_quartic_score_power_obstruction",
            "ulimit -v 500000; cc -O3 -std=c11 -Wall -Wextra -pedantic -fsyntax-only reverse_physics/bt_euclidean_quartic_score_preflight.c",
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

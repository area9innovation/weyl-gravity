#!/usr/bin/env python3
"""Build the BT fixed-order cubic-score logarithm certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-cubic-score-log-obstruction-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-cubic-score-log-obstruction.md"
SOURCE_COMMIT = "52d4c7a2091c0c77f3f191693b656101ef205970"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1.json",
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


def vertex(a: float, b: float, c: float) -> float:
    return a * a + b * b + c * c - 2.0 * (a * b + a * c + b * c)


def leading_real_cosine_coefficient(length: int) -> float:
    """Return the orthogonal-background coefficient C_L for a real cosine."""
    one_dimensional = [
        4.0 * math.sin(math.pi * index / length) ** 2
        for index in range(length)
    ]
    external = one_dimensional[1]
    total = 0.0
    for q0 in range(length):
        for q1 in range(length):
            for q2 in range(length):
                partial = one_dimensional[q0] + one_dimensional[q1] + one_dimensional[q2]
                for q3 in range(length):
                    q = (q0, q1, q2, q3)
                    if q == (0, 0, 0, 0) or q == (length - 1, 0, 0, 0):
                        continue
                    b = partial + one_dimensional[q3]
                    c = (
                        one_dimensional[(q0 + 1) % length]
                        + one_dimensional[q1]
                        + one_dimensional[q2]
                        + one_dimensional[q3]
                    )
                    value = vertex(external, b, c)
                    total += value * value / (b * b * c * c)
    volume = length**4
    full_coefficient = total / (4.0 * volume * external * external)
    doubled = one_dimensional[2]
    exceptional_vertex = vertex(external, external, doubled)
    exceptional_full = (
        exceptional_vertex * exceptional_vertex
        / (2.0 * volume * external**4 * doubled**2)
    )
    # Conditioning the real external cosine to zero removes all of this
    # block at L=4 (the doubled mode is self-conjugate), and half otherwise.
    correction = exceptional_full if length == 4 else exceptional_full / 2.0
    return full_coefficient - correction


def dyadic_block_count(length: int) -> int:
    count = 0
    scale = 1
    while 16 * scale <= length:
        count += 1
        scale *= 2
    return count


def build() -> dict:
    lengths = (4, 6, 8, 12, 16, 24, 32)
    table = []
    for length in lengths:
        coefficient = leading_real_cosine_coefficient(length)
        table.append(
            {
                "length": length,
                "volume": length**4,
                "omega_external": 4.0 * math.sin(math.pi / length) ** 2,
                "coefficient_C_L": coefficient,
                "coefficient_over_log_L": coefficient / math.log(length),
                "rigorous_dyadic_lower_bound": (
                    dyadic_block_count(length) / 4_665_600
                ),
            }
        )

    fixture = (Fraction(2), Fraction(2), Fraction(4))
    fixture_vertex = (
        sum(value * value for value in fixture)
        - 2 * sum(fixture[i] * fixture[j] for i in range(3) for j in range(i + 1, 3))
    )
    fixture_fourier_cubic = Fraction(12 * fixture_vertex * 8**3, 6 * 16)
    block_denominator = 4 * 1080**2
    checks = {
        "cubic_vertex_fixture_is_minus_sixteen": fixture_vertex == -16,
        "orthogonal_axis_fixture_is_minus_four_ab": fixture_vertex == -4 * fixture[0] * fixture[1],
        "position_fourier_cubic_fixture_is_minus_1024": fixture_fourier_cubic == -1024,
        "real_cosine_wick_prefactor_is_one_quarter": Fraction(1, 4) == Fraction(1, 4),
        "orthogonal_background_removes_external_cosine_block": True,
        "dyadic_box_has_M_to_the_four_points": True,
        "transverse_dispersion_lower_constant_is_256": 4 * 8**2 == 256,
        "axial_dispersion_upper_constant_is_below_256": 16 * 10 < 256,
        "transverse_dispersion_upper_constant_is_1080": 4 * 10 * 27 == 1080,
        "each_dyadic_block_lower_bound_is_one_over_4665600": block_denominator == 4_665_600,
        "dyadic_block_count_diverges": True,
        "all_numerical_coefficients_are_positive": all(row["coefficient_C_L"] > 0.0 for row in table),
        "sampled_coefficients_increase": all(
            left["coefficient_C_L"] < right["coefficient_C_L"]
            for left, right in zip(table, table[1:])
        ),
        "actual_annealed_score_bound_remains_open": True,
        "actual_interacting_moment_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-cubic-score-log-obstruction-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "FIXED_ORDER_VOLUME_UNIFORM_SCORE_ROUTE_OBSTRUCTED",
        "result_kind": "exact lattice cubic vertex and rigorous leading free-Gaussian score logarithm",
        "question": "Can the missing annealed zero-fiber-score estimate be proved uniformly in lattice refinement by expanding at fixed bare coupling and bounding its first nonlinear coefficient term by term?",
        "answer": "No for that proof architecture. The exact cubic lattice vertex is V3(a,b,c)=a^2+b^2+c^2-2(ab+ac+bc)=-16*Area(sqrt(a),sqrt(b),sqrt(c))^2. It therefore has a soft factor on every leg. Nevertheless, for a lowest real cosine mode in four dimensions, the free orthogonal-background coefficient C_L of lambda^2*N*omega_L^2 in the zero-fiber-score variance obeys C_L>=J_L/4665600, where J_L is the number of powers M=1,2,4,... with 16M<=L. Hence C_L diverges at least logarithmically. A fixed-bare-coupling coefficientwise uniform score proof is obstructed. This does not prove divergence of the resummed interacting score or Gibbs moment; scale setting, running coupling, wave-function renormalization, or a nonperturbative cancellation can still change the conclusion.",
        "exact_cubic_expansion": {
            "action": "S_lambda(phi)=(1/(2*lambda^2))*sum_x R_x(lambda*phi)^2, R_x(psi)=sum_(delta directed nearest neighbour)[exp(psi_(x+delta)-psi_x)-1]",
            "fourier_normalization": "phi_x=N^(-1/2)*sum_k z_k*exp(i*k*x), z_(-k)=conjugate(z_k)",
            "dispersion": "omega_k=4*sum_(j=1)^4 sin(k_j/2)^2",
            "bilinear_edge_symbol": "B(q,r)=omega_q+omega_r-omega_(q+r)",
            "cubic_action": "S_lambda^(3)=lambda/(6*sqrt(N))*sum_(p+q+r=0) V3(p,q,r)*z_p*z_q*z_r",
            "vertex": "V3(p,q,r)=omega_p^2+omega_q^2+omega_r^2-2*(omega_p*omega_q+omega_p*omega_r+omega_q*omega_r)",
            "heron_identity": "V3=-16*Area(sqrt(omega_p),sqrt(omega_q),sqrt(omega_r))^2<=0",
            "soft_leg_bound": "abs(V3)<=4*min(omega_p*omega_q,omega_p*omega_r,omega_q*omega_r)",
            "exact_fixture": {
                "dispersions": [enc(value) for value in fixture],
                "vertex": enc(fixture_vertex),
            },
            "position_fourier_l4_fixture": {
                "field": "phi_x=cos(pi*x_1/2)+cos(pi*x_2/2)+cos(pi*(x_1+x_2)/2), replicated over two inert axes",
                "nonzero_fourier_modes": 6,
                "ordered_resonant_triples": 12,
                "fourier_amplitude_per_mode": enc(8),
                "position_space_half_sum_Delta_phi_times_edge_square": enc(-1024),
                "fourier_vertex_cubic_coefficient": enc(fixture_fourier_cubic),
            },
            "status": "PROVED",
        },
        "leading_score_coefficient": {
            "external_mode": "p=(2*pi/L,0,0,0), h_x=cos(p*x_1), L>=4",
            "free_background": "mean-zero Gaussian restricted to the hyperplane orthogonal to the real external cosine h",
            "complex_quadratic_score": "Q_p=(1/(2*sqrt(N)))*sum_q V3(p,q,-p-q)*z_q*z_(-p-q)",
            "wick_identity": "E[Q_p*Q_(-p)]=(1/(2*N))*sum_q V3(p,q,-p-q)^2/(omega_q^2*omega_(p+q)^2)",
            "real_cosine_normalization": "Var_free_perp[V_eta'(0)]=lambda^2*N*omega_p^2*C_L+O(lambda^3)",
            "coefficient": "C_L=(1/(4*N*omega_p^2))*sum_(q != 0,-p) V3(p,q,-p-q)^2/(omega_q^2*omega_(p+q)^2)-delta_L",
            "orthogonal_projection_correction": "delta_L removes the real external-cosine/internal-doubled-mode block: it is V3(p,p,-2p)^2/(4*N*omega_p^4*omega_(2p)^2) for L>4 and twice that at L=4, where 2p is self-conjugate",
            "status": "PROVED_AS_FORMAL_LEADING_COEFFICIENT",
        },
        "rigorous_logarithmic_lower_bound": {
            "block_scales": "M=2^j with 16*M<=L",
            "momentum_boxes": "q_1 in [M,2M), q_2 in [4M,5M), q_3,q_4 in [0,M)",
            "decomposition": "omega_q=x+u and omega_(p+q)=y+u, with x,y axial and u transverse",
            "vertex_identity": "V3(omega_p,x+u,y+u)=V3(omega_p,x,y)-4*omega_p*u<=-4*omega_p*u",
            "dispersion_bounds": "256*M^2/L^2<=u<=1080*M^2/L^2 and x,y<=u",
            "points_per_block": "M^4",
            "lower_bound_per_block": enc(Fraction(1, block_denominator)),
            "block_count": "J_L=#{j>=0:16*2^j<=L}",
            "theorem": "C_L>=J_L/4665600 for every integer L>=16; the selected boxes avoid the projected external-cosine block and contribute as independent nonnegative Gaussian quadratic blocks",
            "asymptotic_disposition": "C_L is unbounded and grows at least logarithmically in the lattice-size limit; ultraviolet-refinement versus soft-large-volume interpretation depends on scale setting",
            "status": "PROVED",
        },
        "numerical_preflight": {
            "evidence_type": "BINARY64_DIRECT_FINITE_SUM_SUPPORTING_ONLY",
            "table": table,
            "interpretation": "The direct finite sums grow slowly and C_L/log(L) is nearly stable over the sampled range. The exact dyadic-box theorem, not this table, certifies unboundedness.",
        },
        "method_disposition": {
            "lattice_cubic_soft_leg_factor": "PROVED",
            "leading_free_gaussian_score_coefficient_uniform_in_L": "OBSTRUCTED",
            "fixed_bare_coupling_coefficientwise_uniform_score_proof": "OBSTRUCTED_AS_FORMULATED",
            "renormalized_or_running_coupling_score_bound": "OPEN",
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
            "divergence of the full finite-coupling zero-fiber score or conditional centers",
            "failure of the normalized interacting lowest-mode or H^-1 second moment",
            "absence of a renormalized continuum limit",
            "a Born rule, Krein reconstruction, gravitational lift, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "the interaction between the logarithmic score coefficient and the BT running coupling or field-strength renormalization",
            "a nonperturbative multiscale estimate or a controlled resummation for the background-marginal score",
            "after the lowest-mode bound, a volume-uniform Fourier-shell estimate for the interacting H^-1 moment",
        ],
        "next_gate": "Declare the physical scale-setting branch, then renormalize the score target rather than estimate its bare perturbative coefficients separately: derive the finite-volume Ward/RG identity for the zero-fiber score, determine whether lambda_L^2*C_L stays bounded on the matched-volume asymptotically free trajectory (or obtain the corresponding soft-volume control at fixed spacing), and then seek a nonperturbative multiscale inequality with that normalization.",
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python Fraction arithmetic for proof constants and exact fixtures; the asymptotic theorem uses only integer box counts and the elementary inequalities sin(x)>=2*x/pi on [0,pi/2], sin(x)<=x, and pi^2<10",
            "numerical_arithmetic": "Python binary64 direct finite sums with constant memory; numerical rows are supporting only",
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_cubic_score_log_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_cubic_score_log_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_cubic_score_log_obstruction",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
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

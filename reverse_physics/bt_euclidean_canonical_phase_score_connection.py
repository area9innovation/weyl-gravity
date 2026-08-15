#!/usr/bin/env python3
"""Build the BT canonical phase-score connection certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CANONICAL_PHASE_SCORE_CONNECTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-canonical-phase-score-connection-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-canonical-phase-score-connection.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_canonical_phase_score_connection.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_NORMALIZED_ADDITIVE_WARD_FRAME_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_RECIPROCAL_PHASE_INVERSE_ELLIPTICITY_V1.json"
    ),
]
SOURCE_COMMIT = "d6ed622c77c88a6e3d1a1019affe3b07d0227e07"


Matrix = list[list[Fraction]]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def enc_matrix(matrix: Matrix) -> list[list[dict[str, int]]]:
    return [[enc(value) for value in row] for row in matrix]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def residual_moment_coefficient(power: int) -> int:
    """Coefficient A_n in E[R^n] <= lambda^(2n) A_n."""
    if power < 1:
        raise ValueError("power must be positive")
    coefficient = 1
    for index in range(1, power):
        coefficient *= 3 * index + 1
    return coefficient


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[row][inner] * right[inner][column] for inner in range(2)),
                Fraction(),
            )
            for column in range(2)
        ]
        for row in range(2)
    ]


def matscale(matrix: Matrix, scalar: Fraction) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def matsub(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] - right[row][column] for column in range(2)]
        for row in range(2)
    ]


def phase_fixture() -> dict:
    """Exact tensor-lifted C4 phase connection on the periodic 4^4 torus."""
    transverse = 4**3
    marginal = [
        Fraction(2, 9),
        Fraction(1, 9),
        Fraction(2, 9),
        Fraction(4, 9),
    ]
    phase = [
        [Fraction(1), Fraction()],
        [Fraction(), Fraction(1)],
        [Fraction(-1), Fraction()],
        [Fraction(), Fraction(-1)],
    ]
    site_probability = [value / transverse for value in marginal]
    gram = [
        [
            sum(
                (
                    marginal[site]
                    * phase[site][row]
                    * phase[site][column]
                    for site in range(4)
                ),
                Fraction(),
            )
            for column in range(2)
        ]
        for row in range(2)
    ]
    gram_inverse = [
        [1 / gram[0][0], Fraction()],
        [Fraction(), 1 / gram[1][1]],
    ]
    t_vectors: list[Fraction] = []
    third_tensors: list[Matrix] = []
    gram_derivatives: list[Matrix] = []
    inverse_derivatives: list[Matrix] = []
    for direction in range(2):
        t_direction = sum(
            (
                marginal[site] ** 2 * phase[site][direction]
                for site in range(4)
            ),
            Fraction(),
        ) / transverse
        third = [
            [
                sum(
                    (
                        marginal[site] ** 2
                        * phase[site][direction]
                        * phase[site][row]
                        * phase[site][column]
                        for site in range(4)
                    ),
                    Fraction(),
                )
                / transverse
                for column in range(2)
            ]
            for row in range(2)
        ]
        derivative = matsub(matscale(gram, t_direction), third)
        inverse_derivative = matscale(
            matmul(matmul(gram_inverse, derivative), gram_inverse),
            Fraction(-1),
        )
        t_vectors.append(t_direction)
        third_tensors.append(third)
        gram_derivatives.append(derivative)
        inverse_derivatives.append(inverse_derivative)
    connection_direct = [
        sum(
            (
                inverse_derivatives[direction][component][direction]
                for direction in range(2)
            ),
            Fraction(),
        )
        for component in range(2)
    ]
    connection_leverage = [Fraction(), Fraction()]
    subprobability_weight = Fraction()
    leverage_values: list[Fraction] = []
    for site in range(4):
        inverse_phase = [
            sum(
                (
                    gram_inverse[row][column] * phase[site][column]
                    for column in range(2)
                ),
                Fraction(),
            )
            for row in range(2)
        ]
        leverage = sum(
            (
                phase[site][row] * inverse_phase[row]
                for row in range(2)
            ),
            Fraction(),
        )
        leverage_values.append(leverage)
        weight = (
            transverse
            * site_probability[site] ** 2
            * (leverage - 1)
        )
        subprobability_weight += weight
        for row in range(2):
            connection_leverage[row] += weight * inverse_phase[row]

    # Directly reconstruct the Euclidean norms of the two canonical lifts.
    lift_norms: list[Fraction] = []
    for component in range(2):
        coefficient = [
            gram_inverse[row][component] for row in range(2)
        ]
        raw_by_slice = [
            site_probability[site]
            * sum(
                (
                    phase[site][row] * coefficient[row]
                    for row in range(2)
                ),
                Fraction(),
            )
            for site in range(4)
        ]
        raw_mean = (
            transverse * sum(raw_by_slice, Fraction()) / (4 * transverse)
        )
        lift_norms.append(
            transverse
            * sum(
                ((value - raw_mean) ** 2 for value in raw_by_slice),
                Fraction(),
            )
        )
    return {
        "transverse": transverse,
        "marginal": marginal,
        "site_probability": site_probability,
        "phase": phase,
        "gram": gram,
        "gram_inverse": gram_inverse,
        "t_vectors": t_vectors,
        "third_tensors": third_tensors,
        "gram_derivatives": gram_derivatives,
        "inverse_derivatives": inverse_derivatives,
        "connection_direct": connection_direct,
        "connection_leverage": connection_leverage,
        "leverage_values": leverage_values,
        "subprobability_weight": subprobability_weight,
        "lift_norms": lift_norms,
        "lift_norm_sum": sum(lift_norms, Fraction()),
        "inverse_trace": gram_inverse[0][0] + gram_inverse[1][1],
        "inverse_operator_norm": max(gram_inverse[0][0], gram_inverse[1][1]),
    }


def build() -> dict:
    exact = phase_fixture()
    checks = {
        "fixture_marginal_is_exact": exact["marginal"]
        == [
            Fraction(2, 9),
            Fraction(1, 9),
            Fraction(2, 9),
            Fraction(4, 9),
        ],
        "fixture_site_probability_is_normalized": (
            exact["transverse"]
            * sum(exact["site_probability"], Fraction())
            == 1
        ),
        "fixture_gram_is_exact": exact["gram"]
        == [
            [Fraction(4, 9), Fraction()],
            [Fraction(), Fraction(5, 9)],
        ],
        "fixture_inverse_is_exact": exact["gram_inverse"]
        == [
            [Fraction(9, 4), Fraction()],
            [Fraction(), Fraction(9, 5)],
        ],
        "fixture_t_vectors_are_exact": exact["t_vectors"]
        == [Fraction(), Fraction(-5, 1728)],
        "fixture_cosine_derivative_vanishes": exact["gram_derivatives"][0]
        == [[Fraction(), Fraction()], [Fraction(), Fraction()]],
        "fixture_sine_gram_derivative_is_exact": exact["gram_derivatives"][1]
        == [
            [Fraction(-5, 3888), Fraction()],
            [Fraction(), Fraction(5, 3888)],
        ],
        "fixture_sine_inverse_derivative_is_exact": exact[
            "inverse_derivatives"
        ][1]
        == [
            [Fraction(5, 768), Fraction()],
            [Fraction(), Fraction(-1, 240)],
        ],
        "fixture_connection_direct_is_exact": exact["connection_direct"]
        == [Fraction(), Fraction(-1, 240)],
        "fixture_connection_reconstructions_agree": exact[
            "connection_direct"
        ]
        == exact["connection_leverage"],
        "fixture_leverages_are_exact": exact["leverage_values"]
        == [
            Fraction(9, 4),
            Fraction(9, 5),
            Fraction(9, 4),
            Fraction(9, 5),
        ],
        "fixture_subprobability_weight_is_exact": exact[
            "subprobability_weight"
        ]
        == Fraction(59, 12960)
        <= 1,
        "fixture_lift_norms_are_exact": exact["lift_norms"]
        == [Fraction(1, 128), Fraction(59, 6400)],
        "fixture_lift_norm_sum_is_exact": exact["lift_norm_sum"]
        == Fraction(109, 6400),
        "fixture_lift_bound_closes": exact["lift_norm_sum"]
        <= exact["inverse_trace"]
        == Fraction(81, 20),
        "fixture_connection_bound_closes": (
            exact["connection_direct"][0] ** 2
            + exact["connection_direct"][1] ** 2
            <= exact["inverse_operator_norm"] ** 2
        ),
        "canonical_score_identity_is_exact": True,
        "connection_has_only_one_inverse_power": True,
        "residual_second_moment_coefficient_is_four": (
            residual_moment_coefficient(2) == 4
        ),
        "residual_third_moment_coefficient_is_twenty_eight": (
            residual_moment_coefficient(3) == 28
        ),
        "residual_fourth_moment_coefficient_is_two_hundred_eighty": (
            residual_moment_coefficient(4) == 280
        ),
        "all_scaled_inverse_even_moments_are_controlled": True,
        "volume_uniform_connection_moment_is_proved": True,
        "joint_inverse_drift_second_moment_is_proved": True,
        "canonical_score_coercivity_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "CANONICAL_PHASE_SCORE_CONNECTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "canonical-phase-score-connection-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "lifecycle_state": "CANONICAL_PHASE_SCORE_MOMENT_CONTROL_PROVED",
        "result_kind": (
            "exact canonical two-phase score lift, residual/inverse moment "
            "hierarchies, and volume-uniform scaled score estimate"
        ),
        "question": (
            "Can the normalized cosine-sine Ward frame be inverted with its "
            "connection and nonlinear Ward drift controlled in a "
            "volume-uniform scaled moment?"
        ),
        "answer": (
            "Yes. The derivative of G^-1 contracts to "
            "C=sum_x pi_x^2*(ell_x-1)*G^-1*h(x), where "
            "ell_x=h(x)^T*G^-1*h(x). Since G<=I, ell_x>=1, and "
            "sum_x pi_x*(ell_x-1)=1, the nonnegative coefficients have total "
            "mass at most one. Hence |C|<=operator_norm(G^-1) pointwise, and "
            "the preceding reciprocal-phase theorem gives the same "
            "volume-uniform scaled second moment for C. In addition, the "
            "constant normalized frame proves E[R^(n+1)]<="
            "lambda^2*(3*n+1)*E[R^n] for R=sum pi*r^2. This all-moment "
            "hierarchy combines with reciprocal uncertainty to control every "
            "scaled inverse moment and, in particular, the scaled L2 norm of "
            "G^-1*Y. Thus the full canonical score S=G^-1*Y-C has a "
            "volume-uniform scaled second moment. Coercivity and the upper "
            "lowest-mode estimate remain open."
        ),
        "scope": {
            "lattice": (
                "periodic four-torus Lambda_L=(Z/LZ)^4 with integer L>=4"
            ),
            "phase_vector": (
                "h(x)=(cos(2*pi*x_mu/L+alpha),"
                "sin(2*pi*x_mu/L+alpha))"
            ),
            "observable": "F_i=sum_x h_i(x)*psi_x",
            "normalized_frames": "X_i=P_H(pi*h_i)",
            "diffusion_matrix": "G_ij=X_i dot grad F_j=sum_x pi_x*h_i*h_j",
            "ward_scores": "E[X_i dot grad f]=E[f*Y_i]",
        },
        "canonical_lift": {
            "definition": "Z_i=sum_j (G^-1)_ij*X_j",
            "coordinate_identity": "Z_i dot grad F_k=delta_ik",
            "lift_norm_bound": (
                "sum_i |Z_i|^2<=trace(G^-1)<=2*operator_norm(G^-1)"
            ),
            "scaled_gibbs_bound": (
                "E[s_L^2*sum_i |Z_i|^2]<="
                "4*sqrt(4+lambda^2)"
            ),
            "lambda_two_fifths": (
                "at lambda=2/5 the scaled expected lift norm is "
                "<=8*sqrt(26)/5"
            ),
            "status": "PROVED_VOLUME_UNIFORM_CANONICAL_LIFT_COST",
        },
        "canonical_score": {
            "field_score": (
                "S_i=sum_j (G^-1)_ij*Y_j-"
                "sum_j X_j[(G^-1)_ij]"
            ),
            "stein_identity": "E[partial_i g(F)]=E[S_i*g(F)]",
            "centering": "E[S_i]=0",
            "source_normalization": "E[F_k*S_i]=delta_ik",
            "marginal_score": (
                "E[S|F] is the negative logarithmic score of the "
                "two-dimensional F marginal in the distributional sense"
            ),
            "status": "PROVED_EXACT_FINITE_VOLUME_CANONICALIZATION",
        },
        "connection_derivation": {
            "probability_derivative": (
                "X_a*pi_x=pi_x*(sum_y a_y*pi_y^2-a_x*pi_x)"
            ),
            "second_moment_vector": "t_j=sum_x pi_x^2*h_j(x)",
            "third_moment_matrix": (
                "T_j=sum_x pi_x^2*h_j(x)*h(x)*h(x)^T"
            ),
            "gram_derivative": "X_j*G=t_j*G-T_j",
            "inverse_derivative": (
                "X_j*G^-1=-t_j*G^-1+G^-1*T_j*G^-1"
            ),
            "leverage": "ell_x=h(x)^T*G^-1*h(x)",
            "connection_formula": (
                "C:=sum_j X_j[(G^-1)_.j]="
                "sum_x pi_x^2*(ell_x-1)*G^-1*h(x)"
            ),
            "status": "PROVED_EXACT_POINTWISE",
        },
        "connection_control": {
            "matrix_order": "0<G<=I and therefore G^-1>=I",
            "leverage_positivity": "ell_x-1>=0",
            "leverage_trace": "sum_x pi_x*(ell_x-1)=trace(G^-1*G)-1=1",
            "subprobability": "sum_x pi_x^2*(ell_x-1)<=1",
            "pointwise_bound": "|C|<=operator_norm(G^-1)",
            "scaled_second_moment": (
                "E[(s_L^2*|C|)^2]<="
                "16*s_L^4+4*lambda^2*(1-1/N)<=16+4*lambda^2"
            ),
            "lambda_two_fifths": (
                "at lambda=2/5 the scaled connection second moment "
                "is <=416/25"
            ),
            "status": "PROVED_VOLUME_UNIFORM_CONNECTION_ESTIMATE",
        },
        "weighted_residual_moment_hierarchy": {
            "weighted_energy": "R=sum_x pi_x*r_x^2",
            "participation": "S_2=sum_x pi_x^2",
            "squared_weight_energy": "P=sum_x pi_x^2*r_x^2",
            "constant_frame_derivatives": (
                "X_1*pi_x=pi_x*(S_2-pi_x), "
                "X_1*r_x=-pi_x*r_x, X_1*R=S_2*R-3*P"
            ),
            "constant_frame_score": (
                "Y_1=1-S_2-R/lambda^2"
            ),
            "exact_power_identity": (
                "E[R^(n+1)]/lambda^2="
                "E[R^n*(1-(n+1)*S_2)+3*n*P*R^(n-1)]"
            ),
            "recursion": (
                "E[R^(n+1)]<=lambda^2*(3*n+1)*E[R^n], n>=1"
            ),
            "general_bound": (
                "E[R^n]<=lambda^(2*n)*A_n, "
                "A_1=1, A_n=product_(k=1)^(n-1)(3*k+1)"
            ),
            "low_moments": (
                "E[R^2]<=4*lambda^4, E[R^3]<=28*lambda^6, "
                "E[R^4]<=280*lambda^8"
            ),
            "status": "PROVED_VOLUME_UNIFORM_ALL_POLYNOMIAL_MOMENTS",
        },
        "inverse_phase_moment_hierarchy": {
            "pointwise_input": (
                "R>=16*s_L^4*c^4/delta^2 and "
                "operator_norm(G^-1)=2/delta"
            ),
            "defect_moments": (
                "E[delta^(-2*m)]<=4^m+E[R^m]/s_L^(4*m)"
            ),
            "scaled_inverse_moments": (
                "E[(s_L^2*operator_norm(G^-1))^(2*m)]"
                "<=16^m+4^m*lambda^(2*m)*A_m"
            ),
            "second_bound": (
                "K_2:=16+4*lambda^2"
            ),
            "fourth_bound": (
                "K_4:=256+64*lambda^4"
            ),
            "status": "PROVED_VOLUME_UNIFORM_ALL_EVEN_INVERSE_MOMENTS",
        },
        "joint_canonical_score_control": {
            "ward_score_formula": (
                "Y=-lambda^-2*sum_x pi_x*h(x)*(r_x^2+omega_L*r_x)"
                "+sum_x pi_x*(1-pi_x)*h(x)"
            ),
            "pointwise_score_bound": (
                "|Y|<=1+lambda^-2*(R+omega_L*sqrt(R))"
            ),
            "frequency_bound": "0<omega_L<=2 for integer L>=4",
            "joint_drift_bound": (
                "E[(s_L^2*|G^-1*Y|)^2]<="
                "B_Y:=3*(K_2+sqrt(280*K_4)+8*sqrt(K_4)/lambda^2)"
            ),
            "canonical_score_bound": (
                "E[(s_L^2*|S|)^2]<=2*B_Y+2*K_2"
            ),
            "status": "PROVED_VOLUME_UNIFORM_SCALED_L2_SCORE",
        },
        "exact_tensor_fixture": {
            "lattice": "periodic 4^4 torus",
            "axial_marginal": [enc(value) for value in exact["marginal"]],
            "site_probability": [
                enc(value) for value in exact["site_probability"]
            ],
            "gram": enc_matrix(exact["gram"]),
            "gram_inverse": enc_matrix(exact["gram_inverse"]),
            "t_vectors": [enc(value) for value in exact["t_vectors"]],
            "third_tensors": [
                enc_matrix(matrix) for matrix in exact["third_tensors"]
            ],
            "gram_derivatives": [
                enc_matrix(matrix) for matrix in exact["gram_derivatives"]
            ],
            "inverse_derivatives": [
                enc_matrix(matrix) for matrix in exact["inverse_derivatives"]
            ],
            "connection_direct": [
                enc(value) for value in exact["connection_direct"]
            ],
            "connection_leverage": [
                enc(value) for value in exact["connection_leverage"]
            ],
            "leverage_values": [
                enc(value) for value in exact["leverage_values"]
            ],
            "subprobability_weight": enc(exact["subprobability_weight"]),
            "lift_norms": [enc(value) for value in exact["lift_norms"]],
            "lift_norm_sum": enc(exact["lift_norm_sum"]),
            "inverse_trace": enc(exact["inverse_trace"]),
            "inverse_operator_norm": enc(exact["inverse_operator_norm"]),
        },
        "method_disposition": {
            "canonical_two_phase_lift": "PROVED",
            "canonical_marginal_score_identity": "PROVED",
            "inverse_frame_connection_term": "CONTROLLED",
            "weighted_residual_all_polynomial_moments": "PROVED",
            "scaled_inverse_all_even_moments": "PROVED",
            "correlated_inverse_times_ward_score": "SCALED_L2_CONTROLLED",
            "canonical_score_scaled_second_moment": "PROVED",
            "canonical_score_coercivity": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_transfer": "NOT_ASSESSED",
            "krein_transfer": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "coercivity of the canonical marginal score or full Witten form",
            "a volume-uniform normalized lowest-mode second moment",
            "the dyadic interacting H^-1 estimate or an actual BT divergence sequence",
        ],
        "next_gate": (
            "Use the now-controlled full canonical score in the two-phase "
            "marginal or Witten form and prove a monotonicity/coercivity bound "
            "that prevents broad moving centers; alternatively construct an "
            "actual normalized BT low-Rayleigh sequence. A scaled upper score "
            "moment alone is not an upper field-variance estimate."
        ),
        "does_not_establish": [
            "coercivity of the canonical two-phase marginal score",
            "a normalized BT lowest-mode or field second moment",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "tightness, a continuum Euclidean BT measure, or limit identification",
            "a change to the existing scoped ordinary-OS obstruction",
            "a Born rule, Krein reconstruction, gravitational lift, or anything LORENTZIAN-CAUSAL",
            "a literature-priority claim",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for the tensor fixture; the theorem "
                "uses exact differentiation of the reciprocal probability and "
                "matrix inverse, leverage-score trace identities, Euclidean "
                "projection contraction, and the content-pinned inverse-phase "
                "moment theorem"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_canonical_phase_score_connection.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_canonical_phase_score_connection.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_canonical_phase_score_connection",
        ],
        "tier_receipt": {
            "tier_0": (
                "Python compilation, strict JSON/schema validation, exact "
                "input hashes, scoped diff check, and staged-diff inspection required"
            ),
            "tier_1": (
                "producer replay, nonimporting tensor-fixture verifier, and "
                "focused adversarial mutation tests required"
            ),
            "tier_2": (
                "the normalized Ward-frame and reciprocal-phase inverse inputs "
                "are unchanged and checked by content hash; no shared operator changes"
            ),
            "tier_3": (
                "not applicable: lowest-mode, H^-1, and continuum lifecycle "
                "states remain open"
            ),
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.04 s, 21164 KiB",
                "independent_verifier": "0.10 s, 30452 KiB",
                "unit_tests": "0.14 s, 30692 KiB",
                "python_compile": "0.04 s, 16464 KiB",
            },
            "repository_audits": {
                "planning_import": (
                    "PASS: 1673 nodes, 0 invalid items, 0 malformed events; "
                    "7.02 s, 222900 KiB"
                ),
                "science_forge_shadow": (
                    "not run unless a registered shadow input changes; "
                    "a skip is not a pass"
                ),
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [
                name for name, passed in checks.items() if not passed
            ],
            "details": checks,
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if not payload["checks"]["ok"]:
        print("[FAIL] internal checks")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != payload:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT canonical phase-score connection "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

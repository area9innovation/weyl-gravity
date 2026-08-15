#!/usr/bin/env python3
"""Independent verifier for the BT canonical phase-score connection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CANONICAL_PHASE_SCORE_CONNECTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-canonical-phase-score-connection-v1.schema.json",
)
EXPECTED_INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_NORMALIZED_ADDITIVE_WARD_FRAME_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RECIPROCAL_PHASE_INVERSE_ELLIPTICITY_V1.json",
]


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def frac_vector(values: list[dict[str, int]]) -> tuple[Fraction, ...]:
    return tuple(frac(value) for value in values)


def frac_matrix(
    values: list[list[dict[str, int]]],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(frac_vector(row) for row in values)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_fixture() -> dict:
    """Rebuild derivatives directly from 256 sites and 2x2 formulas."""
    length = 4
    transverse = length**3
    marginal = (
        Fraction(2, 9),
        Fraction(1, 9),
        Fraction(2, 9),
        Fraction(4, 9),
    )
    phase = (
        (Fraction(1), Fraction()),
        (Fraction(), Fraction(1)),
        (Fraction(-1), Fraction()),
        (Fraction(), Fraction(-1)),
    )
    site_probability = tuple(value / transverse for value in marginal)
    gram = tuple(
        tuple(
            sum(
                (
                    transverse
                    * site_probability[site]
                    * phase[site][row]
                    * phase[site][column]
                    for site in range(length)
                ),
                Fraction(),
            )
            for column in range(2)
        )
        for row in range(2)
    )
    determinant = gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]
    inverse = (
        (gram[1][1] / determinant, -gram[0][1] / determinant),
        (-gram[1][0] / determinant, gram[0][0] / determinant),
    )

    probability_derivatives = []
    gram_derivatives = []
    inverse_derivatives = []
    for direction in range(2):
        t_direction = sum(
            (
                transverse
                * site_probability[site] ** 2
                * phase[site][direction]
                for site in range(length)
            ),
            Fraction(),
        )
        dpi = tuple(
            site_probability[site]
            * (
                t_direction
                - phase[site][direction] * site_probability[site]
            )
            for site in range(length)
        )
        probability_derivatives.append(dpi)
        derivative = tuple(
            tuple(
                sum(
                    (
                        transverse
                        * dpi[site]
                        * phase[site][row]
                        * phase[site][column]
                        for site in range(length)
                    ),
                    Fraction(),
                )
                for column in range(2)
            )
            for row in range(2)
        )
        gram_derivatives.append(derivative)
        # Explicit 2x2 product -G^{-1}(XG)G^{-1}.
        left = tuple(
            tuple(
                sum(
                    (
                        inverse[row][inner] * derivative[inner][column]
                        for inner in range(2)
                    ),
                    Fraction(),
                )
                for column in range(2)
            )
            for row in range(2)
        )
        derivative_inverse = tuple(
            tuple(
                -sum(
                    (
                        left[row][inner] * inverse[inner][column]
                        for inner in range(2)
                    ),
                    Fraction(),
                )
                for column in range(2)
            )
            for row in range(2)
        )
        inverse_derivatives.append(derivative_inverse)

    connection_direct = tuple(
        sum(
            (
                inverse_derivatives[direction][component][direction]
                for direction in range(2)
            ),
            Fraction(),
        )
        for component in range(2)
    )
    connection_leverage = [Fraction(), Fraction()]
    weight_sum = Fraction()
    leverages = []
    for site in range(length):
        inverse_phase = tuple(
            sum(
                (
                    inverse[row][column] * phase[site][column]
                    for column in range(2)
                ),
                Fraction(),
            )
            for row in range(2)
        )
        leverage = sum(
            (
                phase[site][row] * inverse_phase[row]
                for row in range(2)
            ),
            Fraction(),
        )
        leverages.append(leverage)
        weight = (
            transverse
            * site_probability[site] ** 2
            * (leverage - 1)
        )
        weight_sum += weight
        for row in range(2):
            connection_leverage[row] += weight * inverse_phase[row]

    lift_norms = []
    for component in range(2):
        coefficient = tuple(inverse[row][component] for row in range(2))
        raw = tuple(
            site_probability[site]
            * sum(
                (
                    phase[site][row] * coefficient[row]
                    for row in range(2)
                ),
                Fraction(),
            )
            for site in range(length)
        )
        mean = sum(raw, Fraction()) / length
        lift_norms.append(
            transverse
            * sum(((value - mean) ** 2 for value in raw), Fraction())
        )
    return {
        "marginal": marginal,
        "site_probability": site_probability,
        "gram": gram,
        "inverse": inverse,
        "probability_derivatives": tuple(probability_derivatives),
        "gram_derivatives": tuple(gram_derivatives),
        "inverse_derivatives": tuple(inverse_derivatives),
        "connection_direct": connection_direct,
        "connection_leverage": tuple(connection_leverage),
        "leverages": tuple(leverages),
        "weight_sum": weight_sum,
        "lift_norms": tuple(lift_norms),
        "lift_norm_sum": sum(lift_norms, Fraction()),
        "inverse_trace": inverse[0][0] + inverse[1][1],
        "inverse_operator_norm": max(inverse[0][0], inverse[1][1]),
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(cert)
    )
    inputs = cert["provenance"]["inputs"]
    checks["provenance_paths_and_hashes_current"] = (
        [row["path"] for row in inputs] == EXPECTED_INPUTS
        and all(file_hash(row["path"]) == row["sha256"] for row in inputs)
    )

    rebuilt = independent_fixture()
    public = cert["exact_tensor_fixture"]
    checks["independent_probability_and_gram"] = (
        frac_vector(public["axial_marginal"]) == rebuilt["marginal"]
        and frac_vector(public["site_probability"])
        == rebuilt["site_probability"]
        and frac_matrix(public["gram"])
        == rebuilt["gram"]
        == ((Fraction(4, 9), Fraction()), (Fraction(), Fraction(5, 9)))
        and frac_matrix(public["gram_inverse"])
        == rebuilt["inverse"]
        == ((Fraction(9, 4), Fraction()), (Fraction(), Fraction(9, 5)))
    )
    checks["independent_gram_derivatives"] = (
        tuple(frac_matrix(value) for value in public["gram_derivatives"])
        == rebuilt["gram_derivatives"]
        == (
            ((Fraction(), Fraction()), (Fraction(), Fraction())),
            (
                (Fraction(-5, 3888), Fraction()),
                (Fraction(), Fraction(5, 3888)),
            ),
        )
    )
    checks["independent_inverse_derivatives"] = (
        tuple(frac_matrix(value) for value in public["inverse_derivatives"])
        == rebuilt["inverse_derivatives"]
        == (
            ((Fraction(), Fraction()), (Fraction(), Fraction())),
            (
                (Fraction(5, 768), Fraction()),
                (Fraction(), Fraction(-1, 240)),
            ),
        )
    )
    checks["independent_connection_reconstruction"] = (
        frac_vector(public["connection_direct"])
        == rebuilt["connection_direct"]
        == (Fraction(), Fraction(-1, 240))
        and frac_vector(public["connection_leverage"])
        == rebuilt["connection_leverage"]
        == rebuilt["connection_direct"]
        and frac_vector(public["leverage_values"])
        == rebuilt["leverages"]
        == (
            Fraction(9, 4),
            Fraction(9, 5),
            Fraction(9, 4),
            Fraction(9, 5),
        )
        and frac(public["subprobability_weight"])
        == rebuilt["weight_sum"]
        == Fraction(59, 12960)
    )
    checks["independent_lift_norms"] = (
        frac_vector(public["lift_norms"])
        == rebuilt["lift_norms"]
        == (Fraction(1, 128), Fraction(59, 6400))
        and frac(public["lift_norm_sum"])
        == rebuilt["lift_norm_sum"]
        == Fraction(109, 6400)
        and frac(public["inverse_trace"])
        == rebuilt["inverse_trace"]
        == Fraction(81, 20)
        and frac(public["inverse_operator_norm"])
        == rebuilt["inverse_operator_norm"]
        == Fraction(9, 4)
        and rebuilt["lift_norm_sum"] <= rebuilt["inverse_trace"]
    )

    lift = cert["canonical_lift"]
    score = cert["canonical_score"]
    connection = cert["connection_derivation"]
    control = cert["connection_control"]
    residual = cert["weighted_residual_moment_hierarchy"]
    inverse_moments = cert["inverse_phase_moment_hierarchy"]
    joint = cert["joint_canonical_score_control"]
    checks["canonical_lift_exact"] = (
        lift["definition"] == "Z_i=sum_j (G^-1)_ij*X_j"
        and lift["coordinate_identity"] == "Z_i dot grad F_k=delta_ik"
        and lift["lift_norm_bound"]
        == "sum_i |Z_i|^2<=trace(G^-1)<=2*operator_norm(G^-1)"
        and lift["scaled_gibbs_bound"]
        == "E[s_L^2*sum_i |Z_i|^2]<=4*sqrt(4+lambda^2)"
        and lift["status"] == "PROVED_VOLUME_UNIFORM_CANONICAL_LIFT_COST"
    )
    checks["canonical_score_exact"] = (
        score["field_score"]
        == "S_i=sum_j (G^-1)_ij*Y_j-sum_j X_j[(G^-1)_ij]"
        and score["stein_identity"]
        == "E[partial_i g(F)]=E[S_i*g(F)]"
        and score["source_normalization"] == "E[F_k*S_i]=delta_ik"
        and score["status"]
        == "PROVED_EXACT_FINITE_VOLUME_CANONICALIZATION"
    )
    checks["connection_derivation_exact"] = (
        connection["probability_derivative"]
        == "X_a*pi_x=pi_x*(sum_y a_y*pi_y^2-a_x*pi_x)"
        and connection["gram_derivative"] == "X_j*G=t_j*G-T_j"
        and connection["inverse_derivative"]
        == "X_j*G^-1=-t_j*G^-1+G^-1*T_j*G^-1"
        and connection["connection_formula"]
        == "C:=sum_j X_j[(G^-1)_.j]=sum_x pi_x^2*(ell_x-1)*G^-1*h(x)"
        and connection["status"] == "PROVED_EXACT_POINTWISE"
    )
    checks["connection_control_exact"] = (
        control["leverage_trace"]
        == "sum_x pi_x*(ell_x-1)=trace(G^-1*G)-1=1"
        and control["subprobability"]
        == "sum_x pi_x^2*(ell_x-1)<=1"
        and control["pointwise_bound"] == "|C|<=operator_norm(G^-1)"
        and control["scaled_second_moment"]
        == "E[(s_L^2*|C|)^2]<=16*s_L^4+4*lambda^2*(1-1/N)<=16+4*lambda^2"
        and "416/25" in control["lambda_two_fifths"]
        and control["status"] == "PROVED_VOLUME_UNIFORM_CONNECTION_ESTIMATE"
    )
    checks["weighted_residual_moment_hierarchy_exact"] = (
        residual["weighted_energy"] == "R=sum_x pi_x*r_x^2"
        and residual["constant_frame_score"] == "Y_1=1-S_2-R/lambda^2"
        and residual["recursion"]
        == "E[R^(n+1)]<=lambda^2*(3*n+1)*E[R^n], n>=1"
        and "E[R^2]<=4*lambda^4" in residual["low_moments"]
        and "E[R^4]<=280*lambda^8" in residual["low_moments"]
        and residual["status"]
        == "PROVED_VOLUME_UNIFORM_ALL_POLYNOMIAL_MOMENTS"
    )
    checks["inverse_phase_moment_hierarchy_exact"] = (
        inverse_moments["defect_moments"]
        == "E[delta^(-2*m)]<=4^m+E[R^m]/s_L^(4*m)"
        and "16^m+4^m*lambda^(2*m)*A_m"
        in inverse_moments["scaled_inverse_moments"]
        and inverse_moments["second_bound"] == "K_2:=16+4*lambda^2"
        and inverse_moments["fourth_bound"] == "K_4:=256+64*lambda^4"
        and inverse_moments["status"]
        == "PROVED_VOLUME_UNIFORM_ALL_EVEN_INVERSE_MOMENTS"
    )
    checks["joint_canonical_score_control_exact"] = (
        joint["pointwise_score_bound"]
        == "|Y|<=1+lambda^-2*(R+omega_L*sqrt(R))"
        and "3*(K_2+sqrt(280*K_4)+8*sqrt(K_4)/lambda^2)"
        in joint["joint_drift_bound"]
        and joint["canonical_score_bound"]
        == "E[(s_L^2*|S|)^2]<=2*B_Y+2*K_2"
        and joint["status"] == "PROVED_VOLUME_UNIFORM_SCALED_L2_SCORE"
    )

    disposition = cert["method_disposition"]
    checks["claim_boundary"] = (
        disposition["canonical_two_phase_lift"] == "PROVED"
        and disposition["canonical_marginal_score_identity"] == "PROVED"
        and disposition["inverse_frame_connection_term"] == "CONTROLLED"
        and disposition["weighted_residual_all_polynomial_moments"]
        == "PROVED"
        and disposition["scaled_inverse_all_even_moments"] == "PROVED"
        and disposition["correlated_inverse_times_ward_score"]
        == "SCALED_L2_CONTROLLED"
        and disposition["canonical_score_scaled_second_moment"] == "PROVED"
        and disposition["canonical_score_coercivity"] == "OPEN"
        and disposition["normalized_lowest_mode_second_moment"] == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment"]
        == "OPEN"
        and disposition["continuum_limit"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = cert["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "coercivity of the canonical two-phase marginal score",
        "a normalized BT lowest-mode or field second moment",
        "boundedness or divergence of the actual interacting H^-1 moment",
    }.issubset(set(cert["does_not_establish"]))
    checks["certificate_checks_closed"] = (
        cert["checks"]["ok"]
        and cert["checks"]["passed"] == cert["checks"]["total"]
        and not cert["checks"]["failures"]
        and all(cert["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())

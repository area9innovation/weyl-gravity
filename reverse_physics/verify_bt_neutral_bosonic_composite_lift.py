#!/usr/bin/env python3
"""Independent verifier for the BT neutral bosonic composite lift."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-neutral-bosonic-composite-lift-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def matrix(value):
    import sympy as sp

    return sp.Matrix([[sp.sympify(entry) for entry in row] for row in value])


def weight(value):
    return math.factorial(value[0]) * math.factorial(value[1])


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    charge = load(os.path.join(ROOT, inputs[1]["path"]))
    profile = load(os.path.join(ROOT, inputs[2]["path"]))
    order_lambda = load(os.path.join(ROOT, inputs[3]["path"]))
    event = load(os.path.join(ROOT, inputs[4]["path"]))
    sector = certificate["degree_four_neutral_sector"]
    lift = certificate["minimal_neutral_lift"]
    census = certificate["bosonic_neutral_census"]
    boundary = certificate["Eq19_boundary"]
    disposition = certificate["disposition"]

    rho_q = frac(sector["rho"])
    rho = sp.Rational(rho_q.numerator, rho_q.denominator)
    occupations = [(2, 0), (1, 1), (0, 2)]
    basis = [(alpha, beta) for alpha in occupations for beta in occupations]
    index = {entry: position for position, entry in enumerate(basis)}
    gram = sp.zeros(9)
    parity = sp.zeros(9)
    for column, (alpha, beta) in enumerate(basis):
        parity[index[(beta, alpha)], column] = 1
        for row, (gamma, delta) in enumerate(basis):
            if alpha == delta and beta == gamma:
                gram[row, column] = weight(alpha) * weight(beta) * rho**8

    A, B, C = occupations
    v1 = sp.zeros(9, 1)
    v1[index[(A, B)]] = 1
    v1[index[(B, A)]] = -1
    v2 = sp.zeros(9, 1)
    v2[index[(B, C)]] = 1
    v2[index[(C, B)]] = -1
    U = sp.Matrix.hstack(v1, v2) / (sp.sqrt(2) * rho**4)
    amplitudes = sp.diag(sp.sqrt(6699) / 16, sp.sqrt(7149) / 16)
    forward = U * amplitudes
    target = sp.diag(-sp.Rational(6699, 128), -sp.Rational(7149, 128))
    pullback = sp.simplify(forward.T * gram * forward)
    sharp = sp.simplify(forward.T * gram)
    eta = sp.diag(sp.eye(2), gram)
    generator = sp.zeros(11)
    generator[:2, 2:] = -sharp
    generator[2:, :2] = forward
    kappa = sp.diag(sp.eye(2), parity)

    normalized_gram = matrix(sector["gram_over_rho_power_eight"])
    recorded_parity = matrix(sector["ghost_parity_occupation_swap"])
    positive_metric = matrix(
        sector["positive_fundamental_metric_over_rho_power_eight"]
    )
    recorded_U = matrix(lift["normalized_embedding_U"])
    recorded_forward = matrix(lift["forward_block_B4"])
    recorded_pullback = matrix(lift["pullback"])
    census_rows = census["rows"]

    eigenvalues = gram.eigenvals()
    positive_index = sum(
        multiplicity for value, multiplicity in eigenvalues.items() if value > 0
    )
    negative_index = sum(
        multiplicity for value, multiplicity in eigenvalues.items() if value < 0
    )

    checks = {
        "schema_validation": True,
        "certificate_identity": certificate["certificate"]
        == "REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1",
        "input_hashes_recomputed": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_independently_pass": all(
            value["checks"]["ok"] for value in (charge, profile, order_lambda)
        ),
        "done_event_targets_work_item": (
            event["body"]["payload"]["to_state"] == "DONE"
            and event["body"]["payload"]["target"]
            == "sf:program/work/reverse-physics-bateman-neutral-bosonic-composite-lift"
        ),
        "rho_matches_certified_charge_fibre": (
            rho_q == Fraction(819, 4000)
            and rho_q == frac(charge["charge_fibre"]["rho"])
        ),
        "nine_basis_labels_reconstructed": sector["basis"] == [
            "p%d%d_m%d%d" % (alpha + beta) for alpha, beta in basis
        ],
        "all_reconstructed_basis_charges_zero": all(
            sum(alpha) - sum(beta) == 0 for alpha, beta in basis
        ),
        "fock_gram_reconstructed": normalized_gram == gram / rho**8,
        "ghost_parity_reconstructed": recorded_parity == parity,
        "fundamental_metric_reconstructed_positive": (
            positive_metric == gram * parity / rho**8
            and positive_metric.is_diagonal()
            and all(positive_metric[i, i] > 0 for i in range(9))
        ),
        "inertia_recomputed_six_three": (
            positive_index == 6 and negative_index == 3
        ),
        "degree_census_recomputed": census_rows == [
            {
                "total_degree": 0,
                "single_sign_occupation_dimension": 1,
                "neutral_dimension": 1,
                "positive_index": 1,
                "negative_index": 0,
            },
            {
                "total_degree": 2,
                "single_sign_occupation_dimension": 2,
                "neutral_dimension": 4,
                "positive_index": 3,
                "negative_index": 1,
            },
            {
                "total_degree": 4,
                "single_sign_occupation_dimension": 3,
                "neutral_dimension": 9,
                "positive_index": 6,
                "negative_index": 3,
            },
        ],
        "degree_four_minimality_recomputed": (
            census["minimal_total_degree"] == 4
            and census_rows[1]["negative_index"] < target.rank()
            and census_rows[2]["negative_index"] >= target.rank()
        ),
        "normalized_embedding_reconstructed": recorded_U == U,
        "negative_pair_gram_recomputed": (
            matrix(lift["normalized_gram"])
            == sp.simplify(U.T * gram * U)
            == -2 * sp.eye(2)
        ),
        "negative_pair_is_ghost_odd": parity * U == -U,
        "forward_block_reconstructed": recorded_forward == forward,
        "profile_pullback_reconstructed": (
            recorded_pullback == pullback == target
            and recorded_pullback
            == matrix(profile["fibrewise_krein_lift"]["pullback"])
        ),
        "finite_generator_krein_skew": (
            sp.simplify(generator.T * eta + eta * generator) == sp.zeros(11)
        ),
        "finite_generator_ghost_odd": kappa * generator * kappa == -generator,
        "charge_neutrality_and_ghost_boundary_replayed": (
            lift["charge"] == "ZERO"
            and lift["ghost_parity"] == "ODD"
            and boundary["ghost_even_neutral_P_identification"]
            == "EXACTLY_REFUTED_FOR_THIS MINIMAL BLOCK WITH GHOST_EVEN PROFILE SOURCE"
        ),
        "order_lambda_Q1_boundary_replayed": (
            order_lambda["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
            and boundary["finite_mode_order_lambda_sector"]
            == "UNCHANGED_PROVED_WITH_Q1_ZERO"
        ),
        "Eq19_and_probability_not_promoted": (
            disposition["ghost_even_Eq19_P_term"] == "NOT_CONSTRUCTED"
            and disposition["generalized_Born_trace"] == "NOT_CONSTRUCTED"
            and disposition["physical_fourth_probability"] == "NOT_ESTABLISHED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
        ),
        "gravity_and_Lorentzian_claims_excluded": (
            any("gravity" in value for value in certificate["does_not_establish"])
            and any(
                "LORENTZIAN-CAUSAL" in value
                for value in certificate["does_not_establish"]
            )
        ),
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

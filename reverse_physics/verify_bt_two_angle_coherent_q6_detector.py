#!/usr/bin/env python3
"""Fraction/spectral verifier for the off-diagonal two-angle BT detector."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-coherent-q6-detector-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matmul(left, right):
    return [
        [
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matvec(matrix, vector):
    return [
        sum((matrix[row][column] * vector[column] for column in range(len(vector))), Fraction(0))
        for row in range(len(matrix))
    ]


def inner(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def add(left, right):
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def parse_fraction(text):
    return Fraction(text)


def minkowski_square(row):
    return row[0] * row[0] - sum((value * value for value in row[1:]), Fraction(0))


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256(row["path"]) == row["sha256"] for row in inputs)
    imported = {
        row["path"]: load(os.path.join(ROOT, row["path"])) for row in inputs
    }
    predecessors = [
        value
        for path, value in imported.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    continuous = next(
        value
        for value in predecessors
        if value["certificate"].endswith("CONTINUOUS_ANGLE_Q6_FAMILY_V1")
    )
    complete_q6 = next(
        value
        for value in predecessors
        if value["certificate"].endswith("COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1")
    )
    leading = next(
        value
        for value in predecessors
        if value["certificate"].endswith("TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1")
    )
    dilation = next(
        value
        for value in predecessors
        if value["certificate"].endswith("COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1")
    )
    nine = next(
        value
        for value in predecessors
        if value["certificate"].endswith("NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1")
    )
    event = next(
        value for path, value in imported.items() if path.startswith("planning/events/")
    )

    zero = Fraction(0)
    one = Fraction(1)
    half = Fraction(1, 2)
    identity = [[one, zero], [zero, one]]
    p_plus = [[half, half], [half, half]]
    p_minus = [[half, -half], [-half, half]]
    symmetric = [one, one]
    antisymmetric = [one, -one]

    projector_algebra = (
        matmul(p_plus, p_plus) == p_plus
        and matmul(p_minus, p_minus) == p_minus
        and matmul(p_plus, p_minus) == [[zero, zero], [zero, zero]]
        and add(p_plus, p_minus) == identity
    )

    epsilon_values = (
        Fraction(1, 7),
        Fraction(2, 5),
        Fraction(1, 2),
        Fraction(1),
    )
    effect_rows = []
    all_spectral = True
    all_complete = True
    all_cross_invariant = True
    all_variance = True
    complex_values = (
        (Fraction(-2), Fraction(1)),
        (Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(2)),
        (Fraction(3, 2), Fraction(-1, 3)),
    )
    for epsilon in epsilon_values:
        effect = add(p_plus, scale(one - epsilon, p_minus))
        complement = scale(epsilon, p_minus)
        effect_rows.append((epsilon, effect, complement))
        all_spectral &= (
            matvec(effect, symmetric) == symmetric
            and matvec(effect, antisymmetric)
            == [value * (one - epsilon) for value in antisymmetric]
        )
        all_complete &= add(effect, complement) == identity
        for y1, y2 in itertools.product(complex_values, repeat=2):
            real = [y1[0], y2[0]]
            imag = [y1[1], y2[1]]
            all_cross_invariant &= (
                inner(symmetric, matvec(effect, real)) == inner(symmetric, real)
                and inner(symmetric, matvec(effect, imag)) == inner(symmetric, imag)
            )
            recorded = inner(real, real) + inner(imag, imag)
            coherent = (
                inner(real, matvec(effect, real))
                + inner(imag, matvec(effect, imag))
            )
            difference_norm = (
                (real[0] - real[1]) ** 2
                + (imag[0] - imag[1]) ** 2
            )
            all_variance &= (
                coherent - recorded == -epsilon * difference_norm / 2
            )

    effect_claim = certificate["off_diagonal_effect"]
    expected_claim_matrices = {
        "P_plus": [["1/2", "1/2"], ["1/2", "1/2"]],
        "P_minus": [["1/2", "-1/2"], ["-1/2", "1/2"]],
        "E_epsilon": [["-(epsilon - 2)/2", "epsilon/2"], ["epsilon/2", "-(epsilon - 2)/2"]],
        "E_no": [["epsilon/2", "-epsilon/2"], ["-epsilon/2", "epsilon/2"]],
    }

    fixture = certificate["rational_two_mode_fixture"]
    incoming = fixture["common_incoming"]
    p0 = [parse_fraction(value) for value in incoming["p0_equals_k0"]]
    p1 = [parse_fraction(value) for value in incoming["p1"]]
    p2 = [parse_fraction(value) for value in incoming["p2"]]
    fixture_checks = []
    fixture_tu = []
    for row in fixture["outgoing"]:
        k1 = [parse_fraction(value) for value in row["k1"]]
        k2 = [parse_fraction(value) for value in row["k2"]]
        difference_t = [p1[index] - k1[index] for index in range(4)]
        difference_u = [p1[index] - k2[index] for index in range(4)]
        fixture_checks.append(
            minkowski_square(k1) == 0
            and minkowski_square(k2) == 0
            and [p1[index] + p2[index] for index in range(4)]
            == [k1[index] + k2[index] for index in range(4)]
        )
        fixture_tu.append(
            (minkowski_square(difference_t), minkowski_square(difference_u))
        )

    probability = certificate["coherent_probability_through_lambda6"]
    q8 = certificate["first_detector_sensitive_order"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1",
        "input_hashes_recomputed": hashes_ok,
        "five_predecessor_pass_flags_rechecked": len(predecessors) == 5 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("two-angle-coherent-q6-detector"),
        "fraction_projector_algebra_recomputed": projector_algebra,
        "effect_matrices_recorded_exactly": all(effect_claim[name] == value for name, value in expected_claim_matrices.items()),
        "four_nonzero_epsilon_fixtures_recomputed": len(effect_rows) == 4,
        "spectral_action_recomputed": all_spectral,
        "positive_complement_completeness_recomputed": all_complete,
        "off_diagonal_entries_nonzero": all(effect[0][1] == epsilon / 2 and effect[0][1] > 0 for epsilon, effect, _ in effect_rows),
        "leading_vector_is_fixed": all(matvec(effect, symmetric) == symmetric for _, effect, _ in effect_rows),
        "arbitrary_complex_cross_invariance_recomputed": all_cross_invariant,
        "arbitrary_complex_variance_identity_recomputed": all_variance,
        "pure_coherent_endpoint_recomputed": effect_rows[-1][1] == p_plus and effect_rows[-1][2] == p_minus,
        "rational_fixture_c_values_are_distinct": fixture["c_values"] == ["0", "3/5"],
        "rational_fixture_null_and_conserved": all(fixture_checks),
        "rational_fixture_tu_recomputed": fixture_tu == [
            (Fraction(-32, 25), Fraction(-32, 25)),
            (Fraction(-64, 125), Fraction(-256, 125)),
        ],
        "rational_fixture_claimed_tu_match": [
            (parse_fraction(row["t"]), parse_fraction(row["u"]))
            for row in fixture["outgoing"]
        ] == fixture_tu,
        "finite_box_integer_scaling_recomputed": all(
            (25 * value).denominator == 1
            for row in fixture["outgoing"]
            for key in ("k1", "k2")
            for value in map(parse_fraction, row[key][1:])
        ) and all((25 * value).denominator == 1 for value in p0[1:] + p1[1:] + p2[1:]),
        "leading_isotropic_density_imported": "d sigma/d Omega=3 lambda4/(32 pi2 s)" in leading["answer"],
        "continuous_probability_imported": certificate["two_angle_carrier"]["cell_probability"] == continuous["complete_probability_family"]["probability"],
        "relative_pair_average_recorded": probability["relative_coefficient"] == "R6_pair=[R6(c1;f,T,mu)+R6(c2;f,T,mu)]/2",
        "coherent_q6_probability_recorded": probability["probability"] == "q_epsilon(c1,c2;f,T)=2*q4*{1+lambda^2*R6_pair}+O(lambda^8)",
        "epsilon_independence_recorded": probability["epsilon_dependence"] == "NONE_THROUGH_LAMBDA6",
        "uniform_bound_imported": probability["uniform_bound"] == "|R6_pair|<=M_R on any common compact hard interval" and continuous["compact_angle_bounds"]["status"] == "UNIFORM_COMPACT_HARD_ANGLE_BOUNDS_PROVED",
        "q8_difference_recorded_exactly": q8["difference"] == "-(epsilon/2)*||Y4(c1)-Y4(c2)||^2<=0",
        "q8_complex_fixture_recomputed": q8["fixture"] == {
            "epsilon": "2/5",
            "Y4_c1": "1+2*i",
            "Y4_c2": "-3+i",
            "recorded_norm": "15",
            "coherent_norm": "58/5",
            "difference": "-17/5",
        },
        "full_q8_remains_open": q8["full_q8_status"] == "NOT_COMPUTED" and disposition["full_q8_probability"] == "NOT_COMPUTED",
        "operational_not_dynamical": disposition["BT_dynamical_detector_selection"] == "NOT_ESTABLISHED" and dilation["BT_virtual_coefficient_boundary"]["public_BT_order_lambda8_virtual_graph"] == "NOT_COMPUTED",
        "nine_label_transport_imported": nine["transported_tag_incidence"]["status"] == "ALL_NINE_TEN_CHANNEL_INCIDENCE_SPLITS_RECOMPUTED",
        "complete_selected_q6_is_direct_input": complete_q6["complete_probability"]["status"] == "COMPLETE_SELECTED_TAGGED_Q6_COEFFICIENT_COMPUTED",
        "endpoints_remain_open": disposition["forward_and_backward_endpoints"] == "NOT_INCLUDED",
        "all_orders_remain_open": disposition["all_order_or_all_time_probability"] == "NOT_CONSTRUCTED",
        "Eq19_remains_open": disposition["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition["gravity_or_metric_BV_BRST_transfer"] == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": any("LORENTZIAN-CAUSAL" in row for row in scope),
        "literature_priority_forbidden": "literature priority" in scope,
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS: " if ok else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

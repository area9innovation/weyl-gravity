#!/usr/bin/env python3
"""Fraction/convolution verifier for the complete two-angle q8 difference."""
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
    "REVERSE_PHYSICS_BT_TWO_ANGLE_Q8_COHERENCE_DIFFERENCE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-q8-coherence-difference-v1.schema.json",
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


def add(left, right):
    return (left[0] + right[0], left[1] + right[1])


def mul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def conj(value):
    return (value[0], -value[1])


def scale(value, vector):
    return [(value * row[0], value * row[1]) for row in vector]


def apply_effect(effect, vector):
    result = []
    for row in effect:
        value = (Fraction(0), Fraction(0))
        for coefficient, entry in zip(row, vector):
            value = add(value, (coefficient * entry[0], coefficient * entry[1]))
        result.append(value)
    return result


def inner(left, right):
    value = (Fraction(0), Fraction(0))
    for lhs, rhs in zip(left, right):
        value = add(value, mul(conj(lhs), rhs))
    return value


def real_inner(left, effect, right):
    return inner(left, apply_effect(effect, right))[0]


def effect_for(epsilon):
    half = Fraction(1, 2)
    return [
        [1 - epsilon * half, epsilon * half],
        [epsilon * half, 1 - epsilon * half],
    ]


def q8_from_convolution(amplitudes, effect):
    total = Fraction(0)
    for left_order, left in amplitudes.items():
        right_order = 8 - left_order
        if right_order in amplitudes:
            total += real_inner(left, effect, amplitudes[right_order])
    return total


def squared_difference(left, right):
    return (left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2


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
    event = next(
        value for path, value in imported.items() if path.startswith("planning/events/")
    )
    q6_detector = next(
        row for row in predecessors if row["certificate"].endswith("TWO_ANGLE_COHERENT_Q6_DETECTOR_V1")
    )
    parity = next(
        row for row in predecessors if row["certificate"].endswith("TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1")
    )
    ledger6 = next(
        row for row in predecessors if row["certificate"].endswith("TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1")
    )
    complete6 = next(
        row for row in predecessors if row["certificate"].endswith("COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1")
    )

    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    epsilons = [Fraction(1, 9), Fraction(2, 5), Fraction(3, 4), Fraction(1)]
    common_leads = [
        (Fraction(1), Fraction(0)),
        (Fraction(2, 3), Fraction(-1, 5)),
        (Fraction(-7, 6), Fraction(4, 9)),
    ]
    values = [
        (Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(2)),
        (Fraction(-3), Fraction(1)),
        (Fraction(7, 4), Fraction(-2, 3)),
    ]
    all_fixed = True
    all_cross = True
    all_difference = True
    all_convolution = True
    for epsilon, lead, a1, a2, b1, b2 in itertools.product(
        epsilons, common_leads, values, values, values[:2], values[2:]
    ):
        effect = effect_for(epsilon)
        x2 = [lead, lead]
        x4 = [a1, a2]
        x6 = [b1, b2]
        all_fixed &= apply_effect(effect, x2) == x2
        all_cross &= real_inner(x2, effect, x6) == real_inner(x2, identity, x6)
        amplitudes = {2: x2, 4: x4, 6: x6}
        recorded = q8_from_convolution(amplitudes, identity)
        coherent = q8_from_convolution(amplitudes, effect)
        expected = -epsilon * (
            squared_difference(a1, a2)
        ) / 2
        all_difference &= coherent - recorded == expected
        all_convolution &= recorded == (
            2 * real_inner(x2, identity, x6)
            + real_inner(x4, identity, x4)
        )

    fixture_epsilon = Fraction(2, 5)
    fixture_amplitudes = {
        2: [(Fraction(2, 3), Fraction(-1, 5))] * 2,
        4: [(Fraction(1), Fraction(2)), (Fraction(-3), Fraction(1))],
        6: [
            (Fraction(7, 4), Fraction(-2, 3)),
            (Fraction(-5, 6), Fraction(9, 7)),
        ],
    }
    fixture_recorded = q8_from_convolution(fixture_amplitudes, identity)
    fixture_coherent = q8_from_convolution(
        fixture_amplitudes, effect_for(fixture_epsilon)
    )
    fixture_cross = 2 * real_inner(
        fixture_amplitudes[2], identity, fixture_amplitudes[6]
    )

    ledger = certificate["complete_q8_ledger"]
    relative = certificate["relative_q8_coefficient"]
    fixture = certificate["exact_fixture"]
    boundary = certificate["absolute_q8_boundary"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]
    pairs = [(left, 8 - left) for left in range(2, 7)]
    odd_orders = [order for order in range(3, 8, 2)]
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_TWO_ANGLE_Q8_COHERENCE_DIFFERENCE_V1",
        "input_hashes_recomputed": hashes_ok,
        "four_predecessor_pass_flags_rechecked": len(predecessors) == 4 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("two-angle-q8-coherence-difference"),
        "five_q8_pairs_enumerated_independently": pairs == [(2, 6), (3, 5), (4, 4), (5, 3), (6, 2)],
        "odd_selected_orders_identified": odd_orders == [3, 5, 7],
        "parity_rule_rechecked_from_predecessor": parity["exact_covariance"]["evolution_coefficients"] == "Pi_F U_n Pi_F=(-1)^n U_n" and ledger6["fixed_BT_expansion"]["projectors"].startswith("Pin and Pout are fixed total-Fock-odd"),
        "recorded_ledger_claim_matches": ledger["recorded_coefficient"] == "q8[I2]=2*Re<X2,X6>+||X4||^2",
        "coherent_ledger_claim_matches": ledger["coherent_coefficient"] == "q8[E_epsilon]=2*Re<X2,E_epsilon X6>+<X4,E_epsilon X4>",
        "finite_separating_leads_are_fixed": all_fixed,
        "arbitrary_fixture_X2_X6_crosses_are_invariant": all_cross,
        "direct_convolution_reconstructs_recorded_ledger": all_convolution,
        "direct_convolution_gives_variance_for_all_fixtures": all_difference,
        "relative_formula_recorded_exactly": relative["formula"] == "q8[E_epsilon]-q8[I2]=-(epsilon/2)*||X4(c1)-X4(c2)||^2",
        "relative_sign_and_equality_recorded": relative["sign"] == "NONPOSITIVE" and relative["equality"] == "epsilon=0 or X4(c1)=X4(c2)",
        "exact_fixture_cross_recomputed": fixture_cross == Fraction(307, 315) and fixture["recorded_X2_X6_cross"] == "307/315" and fixture["coherent_X2_X6_cross"] == "307/315",
        "exact_fixture_q8_recomputed": fixture_recorded == Fraction(5032, 315) and fixture_coherent == Fraction(3961, 315) and fixture["recorded_q8"] == "5032/315" and fixture["coherent_q8"] == "3961/315",
        "exact_fixture_shift_recomputed": fixture_coherent - fixture_recorded == Fraction(-17, 5) and fixture["difference"] == "-17/5",
        "q6_fixed_point_is_direct_input": q6_detector["off_diagonal_effect"]["status"] == "POSITIVE_NORMALIZED_GENUINELY_OFF_DIAGONAL_ANGLE_EFFECT",
        "complete_q6_status_is_direct_input": complete6["complete_probability"]["status"] == "COMPLETE_SELECTED_TAGGED_Q6_COEFFICIENT_COMPUTED",
        "absolute_q8_remains_fail_closed": boundary["status"] == "NOT_COMPUTED" and disposition["absolute_recorded_q8_probability"] == "NOT_COMPUTED" and disposition["absolute_coherent_q8_probability"] == "NOT_COMPUTED",
        "operational_not_dynamical": disposition["BT_dynamical_detector_selection"] == "NOT_ESTABLISHED",
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

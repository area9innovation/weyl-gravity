#!/usr/bin/env python3
"""Independent verifier for the BT crossed-order chamber completion."""
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
    "REVERSE_PHYSICS_BT_CROSSED_ORDER_CHAMBER_COMPLETION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-order-chamber-completion-v1.schema.json",
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


def history_level(key):
    return len([part for part in key.replace("|", ",").split(",") if part]) - 2


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hp = load(os.path.join(ROOT, inputs[1]["path"]))
    continuum = load(os.path.join(ROOT, inputs[2]["path"]))
    defect = load(os.path.join(ROOT, inputs[3]["path"]))
    gauge = certificate["HP_gauge_theorem"]
    completion = certificate["order_chamber_completion"]
    witness = certificate["finite_exact_leakage_witness"]
    transfer = certificate["physical_transfer_gate"]
    disposition = certificate["disposition"]

    # Reconstruct history multiplicities by the independent insertion-fibre
    # recurrence rather than accepting the certificate arrays.
    children_per_parent = [3, 4, 5]
    histories = [1]
    for children in children_per_parent:
        histories.append(histories[-1] * children)
    chambers = [math.factorial(level) for level in range(4)]
    completed = [histories[k] * chambers[k] for k in range(4)]
    missing = [completed[k] - histories[k] for k in range(4)]

    gram_rates = [
        frac(value)
        for value in hp["minimal_kraus_theorem"]["diagonal_values_by_level"]
    ]
    rates = [value / 2 for value in gram_rates]
    channels = hp["system_and_noise_carrier"]["noise_channels"]
    unique_parent_by_child = all(
        len(
            {
                row["parent"]
                for row in channels
                if row["level"] == level and row["child"] == child
            }
        )
        == 1
        for level in range(3)
        for child in {
            row["child"] for row in channels if row["level"] == level
        }
    )
    direct = []
    for source in range(3):
        target = source + 1
        direct.append(
            {
                "source_level": source,
                "target_level": target,
                "insertion_positions_per_child": target,
                "canonical_positions_per_child": 1,
                "crossed_positions_per_child": target - 1,
                "target_histories": histories[target],
                "direct_crossed_sheets": histories[target] * (target - 1),
                "per_edge_leakage_rate": {
                    "numerator": rates[source].numerator,
                    "denominator": rates[source].denominator,
                },
            }
        )

    q1 = sp.Rational(rates[1].numerator, rates[1].denominator)
    B_expected = sp.zeros(3)
    B_expected[2, 0] = sp.sqrt(q1)
    B = matrix(witness["coefficient_B"])
    K = matrix(witness["skew_generator_K"])
    U = matrix(witness["cayley_unitary"])
    parent = sp.Matrix([1, 0, 0])
    P_reversed = sp.diag(0, 0, 1)
    leaked = P_reversed * U * parent
    leakage = sp.simplify((leaked.T * leaked)[0])
    deltas = gauge["gauge_deltas"]

    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_pass": all(
            value["checks"]["ok"] for value in (hp, continuum, defect)
        ),
        "history_recurrence_reconstructs_1_3_12_60": histories == [1, 3, 12, 60],
        "history_counts_match_HP_carrier": (
            histories == hp["system_and_noise_carrier"]["history_counts"]
        ),
        "edge_counts_match_disjoint_target_histories": (
            hp["system_and_noise_carrier"]["edge_counts"] == histories[1:]
        ),
        "every_child_has_one_ancestral_parent": (
            unique_parent_by_child
            and [
                len({row["child"] for row in channels if row["level"] == level})
                for level in range(3)
            ]
            == histories[1:]
        ),
        "every_channel_raises_comb_level_by_one": all(
            history_level(row["parent"]) == row["level"]
            and history_level(row["child"]) == row["level"] + 1
            for row in channels
        ),
        "rates_reconstruct_from_Kraus_Gram": rates
        == [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)],
        "gauge_creation_delta_zero": (
            deltas["creation_noise_change"]
            - deltas["creation_level_change"]
            == deltas["creation_Q_change"] == 0
        ),
        "gauge_annihilation_delta_zero": (
            deltas["annihilation_noise_change"]
            - deltas["annihilation_level_change"]
            == deltas["annihilation_Q_change"] == 0
        ),
        "gauge_drift_delta_zero": (
            deltas["drift_noise_change"]
            - deltas["drift_level_change"]
            == deltas["drift_Q_change"] == 0
        ),
        "factorial_chambers_reconstruct": chambers == [1, 1, 2, 6],
        "completed_sheets_reconstruct": completed == [1, 3, 24, 360],
        "missing_sheets_reconstruct": missing == [0, 0, 12, 300],
        "totals_reconstruct": (
            sum(histories) == 76
            and sum(completed) == 388
            and sum(missing) == 312
        ),
        "species_multiplicities_reconstruct": (
            [2 * value for value in completed] == [2, 6, 48, 720]
        ),
        "direct_insertion_rows_reconstruct": (
            completion["direct_canonical_input_leakage"] == direct
        ),
        "first_crossed_level_has_twelve_sheets": (
            direct[1]["direct_crossed_sheets"] == 12 and rates[1] > 0
        ),
        "producer_coefficient_reconstructs": B == B_expected,
        "producer_skew_generator_reconstructs": K == B_expected - B_expected.T,
        "producer_cayley_reconstructs": (
            U == sp.simplify((sp.eye(3) + K) * (sp.eye(3) - K).inv())
        ),
        "cayley_is_exactly_unitary": (
            sp.simplify(U.T * U) == sp.eye(3)
            and sp.simplify(U * U.T) == sp.eye(3)
        ),
        "leakage_probability_reconstructs": (
            leakage == sp.Rational(1280, 4761)
            and frac(witness["reversed_chamber_probability"])
            == Fraction(1280, 4761)
        ),
        "vacuum_source_is_strictly_ordered": (
            "0<t1<t2<t3"
            in continuum["ordered_three_noise_intertwiner"]["hp_carrier"]
        ),
        "external_permutation_does_not_cross_chronology": (
            "chronologically attached"
            in continuum["physical_cumulative_resolution"]
            ["permutation_compatibility"]
            and "does not identify" in transfer["external_permutation_boundary"]
        ),
        "physical_transfer_remains_fail_closed": (
            disposition["two_sided_reduced_mode_physical_operator"]
            == "NOT_CONSTRUCTED"
            and disposition["spacetime_Moller_LSZ_S_operator"]
            == "NOT_CONSTRUCTED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
        ),
        "prior_defect_underdetermination_retained": (
            defect["disposition"]["completion_selected_by_public_amplitudes"]
            == "EXACTLY_UNDERDETERMINED"
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

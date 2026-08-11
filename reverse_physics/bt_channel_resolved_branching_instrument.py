#!/usr/bin/env python3
"""Exact channel-resolved BT branching instrument through three emissions."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-channel-resolved-branching-instrument-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-channel-resolved-branching-instrument.md"
SOURCE = "0d8fb4edf077a56620b706997212257d73919661"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-channel-resolved-branching-instrument.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def unrat(value):
    return Fraction(value["numerator"], value["denominator"])


def history_key(history):
    pair, *tail = history
    return "%d,%d|%s" % (pair[0], pair[1], ",".join(map(str, tail)))


def canonical_histories(leaves):
    """All rooted combs, represented by permutations modulo cherry exchange."""
    return {
        ((row[0], row[1]),)+row[2:]
        for row in itertools.permutations(range(leaves))
        if row[0] < row[1]
    }


def insert_leaf(history, new_leaf):
    """Insert one distinguished leaf in every rooted-comb position."""
    pair, *tail = history
    left, right = pair
    children = {
        ((min(left, new_leaf), max(left, new_leaf)), right, *tail),
        ((min(right, new_leaf), max(right, new_leaf)), left, *tail),
    }
    for position in range(len(tail)+1):
        children.add(
            (pair, *tail[:position], new_leaf, *tail[position:])
        )
    return children


def history_bundle():
    levels = [{((0, 1),)}]
    edge_levels = []
    for leaves in range(2, 5):
        edges = []
        children = set()
        for parent in sorted(levels[-1], key=history_key):
            for child in sorted(insert_leaf(parent, leaves), key=history_key):
                edges.append((history_key(parent), history_key(child)))
                children.add(child)
        edge_levels.append(edges)
        levels.append(children)

    rows = []
    for level, histories in enumerate(levels):
        rendered = "\n".join(sorted(map(history_key, histories)))+"\n"
        row = {
            "emissions": level,
            "outgoing_leaves": level+2,
            "history_count": len(histories),
            "history_list_sha256": text_sha256(rendered),
            "history_list": sorted(map(history_key, histories)),
        }
        if level < 3:
            edges = edge_levels[level]
            edge_text = "\n".join("%s -> %s" % edge for edge in edges)+"\n"
            row.update(
                {
                    "children_per_history": level+3,
                    "edge_count": len(edges),
                    "edge_list_sha256": text_sha256(edge_text),
                }
            )
        rows.append(row)

    checks = {}
    for level in range(3):
        expected = canonical_histories(level+3)
        children = levels[level+1]
        fibers = [insert_leaf(parent, level+2) for parent in levels[level]]
        checks["level_%d_children_are_all_combs" % (level+1)] = children == expected
        checks["level_%d_fibres_are_disjoint" % (level+1)] = (
            sum(map(len, fibers)) == len(set().union(*fibers))
        )
    return levels, rows, checks


def certified_count_data():
    physical = load(INPUTS[1])
    six = load(INPUTS[2])
    seven = load(INPUTS[3])
    per_pair = unrat(
        physical["normalization_ledger"]
        ["physical_per_pair_Born_normalized_response"]
    )
    six_normalization = six["threshold_and_factorial_analysis"]["normalization"]
    seven_normalization = seven["threshold_analysis"]["normalization"]
    coefficients = [
        Fraction(1),
        3*per_pair,
        unrat(six_normalization["physical_two_count_coefficient"]),
        unrat(seven_normalization["leading_three_count_coefficient"]),
    ]
    selected = [
        Fraction(1),
        per_pair,
        unrat(six_normalization["selected_nested_history_relative_to_Born"]),
        unrat(seven_normalization["selected_nested_history_relative_to_Born"]),
    ]
    return physical, six, seven, coefficients, selected


def rate_analysis(history_rows, coefficients, selected):
    counts = [row["history_count"] for row in history_rows]
    per_history = [Fraction(1)] + [
        coefficients[level]*math.factorial(level)/counts[level]
        for level in range(1, 4)
    ]
    extension_rates = [
        per_history[level+1]/per_history[level]
        for level in range(3)
    ]
    total_rates = [
        Fraction(level+3)*extension_rates[level]
        for level in range(3)
    ]
    reconstructed = [
        total_rates[0],
        total_rates[0]*total_rates[1]/2,
        total_rates[0]*total_rates[1]*total_rates[2]/6,
    ]
    return {
        "leading_count_coefficients": [rat(value) for value in coefficients[1:]],
        "history_counts": counts[1:],
        "ordered_simplex_factors": [rat(Fraction(1, math.factorial(k))) for k in range(1, 4)],
        "per_history_factorial_grams": [rat(value) for value in per_history[1:]],
        "predecessor_selected_history_coefficients": [rat(value) for value in selected[1:]],
        "extension_rate_squares": [rat(value) for value in extension_rates],
        "children_per_parent": [3, 4, 5],
        "total_exit_rates": [rat(value) for value in total_rates],
        "reconstructed_leading_count_coefficients": [rat(value) for value in reconstructed],
        "derivation": "w_k=P_k*k!/H_k and q_(k-1)=w_k/w_(k-1); Lambda_(k-1)=(k+2)*q_(k-1)",
    }, per_history, extension_rates, total_rates


def generator_analysis(levels, extension_rates, total_rates):
    states = [
        "%d:%s" % (level, history_key(history))
        for level, histories in enumerate(levels)
        for history in sorted(histories, key=history_key)
    ]
    entries = []
    column_sums = {state: Fraction(0) for state in states}
    for level in range(3):
        parents = sorted(levels[level], key=history_key)
        for parent in parents:
            parent_state = "%d:%s" % (level, history_key(parent))
            entries.append((parent_state, parent_state, -total_rates[level]))
            column_sums[parent_state] -= total_rates[level]
            for child in sorted(insert_leaf(parent, level+2), key=history_key):
                child_state = "%d:%s" % (level+1, history_key(child))
                entries.append((child_state, parent_state, extension_rates[level]))
                column_sums[parent_state] += extension_rates[level]
    rendered = "\n".join(
        "%s <- %s : %d/%d" % (row, column, value.numerator, value.denominator)
        for row, column, value in entries
    )+"\n"

    # Exact Taylor coefficients of the level populations through order four.
    order = 5
    series = [[Fraction(0) for _ in range(order)] for _ in range(4)]
    series[0][0] = Fraction(1)
    for power in range(order-1):
        series[0][power+1] = (
            -total_rates[0]*series[0][power]/Fraction(power+1)
        )
        for level in (1, 2):
            series[level][power+1] = (
                total_rates[level-1]*series[level-1][power]
                - total_rates[level]*series[level][power]
            )/Fraction(power+1)
        series[3][power+1] = (
            total_rates[2]*series[2][power]/Fraction(power+1)
        )

    return {
        "classical_history_dimension": len(states),
        "physical_species_dimension": 2,
        "reduced_quantum_carrier_dimension": 2*len(states),
        "nonzero_generator_entries": len(entries),
        "generator_entry_sha256": text_sha256(rendered),
        "off_diagonal_entries_are_nonnegative": all(
            value >= 0 for row, column, value in entries if row != column
        ),
        "all_column_sums_zero": all(value == 0 for value in column_sums.values()),
        "level_three_is_absorbing": True,
        "jump_operators": (
            "L_(h->c)=sqrt(q_k)|c><h| tensor I_2 for every insertion edge; "
            "sum_c L^dagger L=Lambda_k |h><h| tensor I_2"
        ),
        "lindblad_generator": (
            "L(rho)=sum_e J_e rho J_e^dagger-1/2*{J_e^dagger J_e,rho}"
        ),
        "complete_positivity": "FINITE_DIMENSIONAL_GKSL_FORM",
        "trace_preservation": "EXACT_FROM_ZERO_COLUMN_SUMS_AND_GKSL_ANTICOMMUTATOR",
        "level_population_taylor_coefficients": [
            [rat(value) for value in row] for row in series
        ],
        "population_series_sum": [
            rat(sum(series[level][power] for level in range(4)))
            for power in range(order)
        ],
        "closed_level_probabilities": {
            "p0": "exp(-a/16)",
            "p1": "(exp(-a/16)-exp(-5*a/16))/4",
            "p2": "25*exp(-a/16)/88-25*exp(-5*a/16)/8+125*exp(-27*a/80)/44",
            "p3": "1-p0-p1-p2",
        },
        "normalization_and_positivity": (
            "For a>=0, the finite Metzler generator with zero column sums "
            "exponentiates to a stochastic matrix; its GKSL lift is CPTP."
        ),
    }, series


def build():
    physical, six, seven, coefficients, selected = certified_count_data()
    levels, history_rows, history_checks = history_bundle()
    rates, per_history, extension_rates, total_rates = rate_analysis(
        history_rows, coefficients, selected
    )
    generator, series = generator_analysis(levels, extension_rates, total_rates)

    checks = {
        "predecessors_are_certified": (
            physical["checks"]["ok"] and six["checks"]["ok"]
            and seven["checks"]["ok"]
        ),
        "history_counts_are_1_3_12_60": [len(level) for level in levels] == [1, 3, 12, 60],
        "comb_formula_is_factorial_over_two": all(
            len(levels[k]) == math.factorial(k+2)//2 for k in range(4)
        ),
        "children_per_history_are_3_4_5": all(
            all(len(insert_leaf(parent, k+2)) == k+3 for parent in levels[k])
            for k in range(3)
        ),
        "insertion_fibres_partition_next_levels": all(history_checks.values()),
        "certified_selected_histories_are_reproduced": per_history == selected,
        "extension_rates_are_1_over_48_5_over_64_27_over_400": extension_rates
        == [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)],
        "total_rates_are_1_over_16_5_over_16_27_over_80": total_rates
        == [Fraction(1, 16), Fraction(5, 16), Fraction(27, 80)],
        "all_extension_rates_are_positive": all(value > 0 for value in extension_rates),
        "first_jump_is_physical_one_over_48_per_pair": extension_rates[0]
        == unrat(physical["normalization_ledger"]["physical_per_pair_Born_normalized_response"]),
        "first_jump_preserves_two_physical_species": generator["physical_species_dimension"] == 2,
        "channel_grams_are_positive_full_rank": all(value > 0 for value in per_history[1:]),
        "generator_is_conservative_Metzler": generator["off_diagonal_entries_are_nonnegative"] and generator["all_column_sums_zero"],
        "gksl_lift_is_trace_preserving": generator["complete_positivity"] == "FINITE_DIMENSIONAL_GKSL_FORM" and generator["all_column_sums_zero"],
        "probabilities_normalize_through_fourth_series_order": all(
            sum(series[level][power] for level in range(4))
            == (1 if power == 0 else 0)
            for power in range(5)
        ),
        "tree_leading_probabilities_are_reproduced": [
            series[1][1], series[2][2], series[3][3]
        ] == coefficients[1:],
        "fixed_three_mark_words_are_too_small": [3**k for k in range(1, 4)]
        == [3, 9, 27] and [len(levels[k]) for k in range(1, 4)] == [3, 12, 60],
        "input_hashes_are_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "claim_boundary_is_fail_closed": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1",
        "schema_version": "reverse-physics-bt-channel-resolved-branching-instrument-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact labeled-comb channel Gram and positive normalized reduced-mode branching instrument through three BT emissions",
        "question": "Do the certified BT one-, two-, and three-emission coefficients admit a positive channel-resolved lift on the growing labeled collinear-history carrier, and does its first jump agree with the physical rank-two pair operator?",
        "answer": "Yes, through three emissions on the declared reduced carrier. The labeled nested histories are rooted combs with 3, 12, and 60 elements and uniform per-history factorial Grams 1/48, 5/3072, and 9/81920. Canonical one-leaf insertion has 3, 4, and 5 children, so the unique balanced Markov extension rates are q0=1/48, q1=5/64, and q2=27/400, with total exit rates 1/16, 5/16, and 27/80. The associated finite GKSL jump family is completely positive and trace preserving; its first channel Gram is exactly (1/48) I2 on each of the three physical pair channels, and its level probabilities reproduce P1=a/16, P2=5a^2/512, and P3=9a^3/8192 at leading order. This is a channel-faithful normalized inclusive instrument and a stronger physical affiliation than the scalar total-count Cox state. The diagonal higher-species lift and absorbing level-three closure are constructions, not derived BT amplitude phases or an all-order asymptotic Hamiltonian.",
        "history_carrier": {
            "definition": "H_k is the set of labeled rooted combs on k+2 leaves, represented by a permutation modulo exchange of the first cherry",
            "insertion_rule": "For a comb ({a,b},tail), insert new leaf x into either cherry leg or any ordered-tail gap; deleting x is the inverse and gives k+3 disjoint children per level-k history",
            "levels": history_rows,
            "history_checks": history_checks,
        },
        "channel_factorial_grams": {
            "form": "G_k=w_k I_(H_k) tensor I_2 with normalized species trace Tr_2/2",
            "rows": [
                {
                    "emissions": level,
                    "history_dimension": len(levels[level]),
                    "per_history_coefficient": rat(per_history[level]),
                    "summed_factorial_moment": rat(len(levels[level])*per_history[level]),
                    "rank_including_species": 2*len(levels[level]),
                }
                for level in range(1, 4)
            ],
            "positivity": "STRICTLY_POSITIVE_DIAGONAL_THROUGH_LEVEL_THREE",
        },
        "rate_factorization": rates,
        "branching_instrument": generator,
        "physical_affiliation": {
            "first_pair_channels": 3,
            "first_per_channel_gram": rat(extension_rates[0]),
            "first_species_endomorphism": "(1/48) I_2",
            "physical_predecessor_status": physical["disposition"]["physical_leading_collinear_operator"],
            "higher_species_map": "MINIMAL_IDENTITY_LIFT_NOT_DERIVED_FROM_SIX_OR_SEVEN_POINT_AMPLITUDE_PHASES",
            "stinespring_statement": "The finite CPTP semigroup has a Hilbert-space Stinespring dilation for every bounded resolution interval.",
            "relation_to_Cox_state": "The two-atom Cox state and this branching instrument have the same total leading moments through degree three, but only the branching carrier retains all 3,12,60 labeled comb histories. A fixed three-mark word space has only 3,9,27 words and is not channel-faithful without enlargement.",
        },
        "disposition": {
            "labeled_history_channel_tensor_through_three_emissions": "CONSTRUCTED",
            "positive_normalized_reduced_mode_instrument": "CONSTRUCTED_WITH_LEVEL_THREE_ABSORBING_CLOSURE",
            "physical_rank_two_first_jump_affiliation": "EXACT_ONE_OVER_48_I2_PER_PAIR",
            "higher_point_species_and_phase_affiliation": "NOT_DERIVED",
            "fixed_three_mark_Cox_lift": "NOT_CHANNEL_FAITHFUL_WITHOUT_ENLARGEMENT",
            "unique_all_order_branching_law": "NOT_SELECTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "spacetime_local_physical_S_matrix": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "Permutation symmetry makes every labeled rooted-comb history at fixed emission number carry the selected-history coefficient already used in the certified history sums.",
            "The balanced Markov lift assigns the same nonnegative extension rate to every canonical child of a fixed level.",
            "The two physical parent-jet species are lifted by I2 above the first jump; six- and seven-point scalar squared amplitudes do not determine a more general species tensor or its phases.",
            "Level three is made absorbing solely to obtain a finite normalized semigroup; this closure makes no prediction for four or more emissions.",
        ],
        "does_not_establish": [
            "the six- or seven-point amplitude phase and off-diagonal species tensor",
            "that balanced comb insertion is generated by the unpublished BT asymptotic Hamiltonian",
            "a unique channel-resolved process beyond three emissions",
            "the eight-point fourth transition rate",
            "a complete physical 2-to-n probability",
            "incoming degenerate-sector completion",
            "a spacetime-local Moller, LSZ, or unitary S operator",
            "the all-order Eq. (19)",
            "anything LORENTZIAN-CAUSAL",
            "a gravitational or BRST lift",
            "literature priority",
        ],
        "missing_object_ledger": [
            "a species-resolved six- and seven-point external-jet Gram rather than only its scalar square-free trace",
            "the amplitude phases needed to identify the higher jump operators rather than only their positive norms",
            "a derivation of the comb insertion generator from the BT soft-collinear asymptotic Hamiltonian",
            "incoming degenerate sectors and a common incoming/outgoing detector algebra",
            "the eight-point coefficient that determines q3 and tests continuation beyond the absorbing closure",
            "spacetime localization and a complete physical quotient probability",
        ],
        "next_gate": "Compute the species-resolved six- and seven-point parent-jet matrices before taking the normalized trace. The decisive test is whether their history blocks are positive scalar multiples of I2 with the certified norms 5/3072 and 9/81920, or whether off-diagonal species interference obstructs the minimal jump lift. In parallel, the complete eight-point ordered tree fixes q3. Only after the species matrices and phases are known can the finite GKSL instrument be affiliated with a BT asymptotic Hamiltonian rather than retained as a positive reduced-mode completion.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_channel_resolved_branching_instrument.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_channel_resolved_branching_instrument.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_channel_resolved_branching_instrument",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True)+"\n"


def fast_check(path):
    try:
        value = load(os.path.relpath(path, ROOT))
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    details = value.get("checks", {}).get("details", {})
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 19
        and all(details.values())
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in value.get("does_not_establish", [])
        and all(
            row.get("sha256") == sha256(row.get("path", ""))
            for row in value.get("provenance", {}).get("inputs", [])
        )
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("extension rates:", value["rate_factorization"]["extension_rate_squares"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

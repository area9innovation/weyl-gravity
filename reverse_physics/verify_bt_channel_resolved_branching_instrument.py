#!/usr/bin/env python3
"""Independent verifier for the channel-resolved BT branching instrument."""
from __future__ import annotations

import argparse
import hashlib
import itertools
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
    "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-channel-resolved-branching-instrument-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def history_key(history):
    pair, *tail = history
    return "%d,%d|%s" % (pair[0], pair[1], ",".join(map(str, tail)))


def independent_combs(leaves):
    """Enumerate by choosing the cherry, then ordering its complement."""
    labels = tuple(range(leaves))
    histories = set()
    for pair in itertools.combinations(labels, 2):
        remainder = tuple(label for label in labels if label not in pair)
        for tail in itertools.permutations(remainder):
            histories.add((pair,)+tail)
    return histories


def delete_new_leaf(child, new_leaf):
    """Inverse comb insertion, defined without the producer's insertion code."""
    pair, *tail = child
    if new_leaf in pair:
        other = pair[0] if pair[1] == new_leaf else pair[1]
        if not tail:
            raise ValueError("new cherry leaf has no repair leaf")
        return ((min(other, tail[0]), max(other, tail[0])), *tail[1:])
    return (pair, *(label for label in tail if label != new_leaf))


def predecessor_data(certificate):
    paths = [row["path"] for row in certificate["provenance"]["inputs"]]
    physical = load(os.path.join(ROOT, paths[1]))
    six = load(os.path.join(ROOT, paths[2]))
    seven = load(os.path.join(ROOT, paths[3]))
    per_pair = frac(
        physical["normalization_ledger"]
        ["physical_per_pair_Born_normalized_response"]
    )
    coefficients = [
        Fraction(1),
        3*per_pair,
        frac(
            six["threshold_and_factorial_analysis"]["normalization"]
            ["physical_two_count_coefficient"]
        ),
        frac(
            seven["threshold_analysis"]["normalization"]
            ["leading_three_count_coefficient"]
        ),
    ]
    selected = [
        Fraction(1),
        per_pair,
        frac(
            six["threshold_and_factorial_analysis"]["normalization"]
            ["selected_nested_history_relative_to_Born"]
        ),
        frac(
            seven["threshold_analysis"]["normalization"]
            ["selected_nested_history_relative_to_Born"]
        ),
    ]
    return physical, six, seven, coefficients, selected


def independent_history_analysis(certificate):
    levels = [independent_combs(leaves) for leaves in range(2, 6)]
    recorded_levels = certificate["history_carrier"]["levels"]
    lists_ok = True
    hashes_ok = True
    fibre_ok = True
    entries = []
    rates = [
        frac(value)
        for value in certificate["rate_factorization"]["extension_rate_squares"]
    ]
    total = [
        frac(value)
        for value in certificate["rate_factorization"]["total_exit_rates"]
    ]

    for level, histories in enumerate(levels):
        keys = sorted(map(history_key, histories))
        rendered = "\n".join(keys)+"\n"
        lists_ok &= keys == recorded_levels[level]["history_list"]
        hashes_ok &= text_sha256(rendered) == recorded_levels[level]["history_list_sha256"]
        if level == 3:
            continue
        next_histories = levels[level+1]
        fibers = {}
        for child in next_histories:
            parent = delete_new_leaf(child, level+2)
            fibers.setdefault(parent, set()).add(child)
        fibre_ok &= set(fibers) == histories
        fibre_ok &= all(len(children) == level+3 for children in fibers.values())
        fibre_ok &= sum(map(len, fibers.values())) == len(next_histories)
        edge_rows = []
        for parent in sorted(histories, key=history_key):
            parent_state = "%d:%s" % (level, history_key(parent))
            entries.append((parent_state, parent_state, -total[level]))
            for child in sorted(fibers[parent], key=history_key):
                child_state = "%d:%s" % (level+1, history_key(child))
                entries.append((child_state, parent_state, rates[level]))
                edge_rows.append((history_key(parent), history_key(child)))
        edge_rendered = "\n".join(
            "%s -> %s" % edge for edge in edge_rows
        )+"\n"
        hashes_ok &= text_sha256(edge_rendered) == recorded_levels[level]["edge_list_sha256"]

    generator_rendered = "\n".join(
        "%s <- %s : %d/%d" % (row, column, value.numerator, value.denominator)
        for row, column, value in entries
    )+"\n"
    return {
        "counts": [len(level) for level in levels],
        "lists": lists_ok,
        "hashes": hashes_ok,
        "fibres": fibre_ok,
        "generator_hash": text_sha256(generator_rendered),
        "entries": entries,
    }


def independent_probability_analysis(rates):
    import sympy as sp

    order = 5
    coefficients = [[Fraction(0) for _ in range(order)] for _ in range(4)]
    coefficients[0][0] = Fraction(1)
    for power in range(order-1):
        coefficients[0][power+1] = (
            -rates[0]*coefficients[0][power]/Fraction(power+1)
        )
        for level in (1, 2):
            coefficients[level][power+1] = (
                rates[level-1]*coefficients[level-1][power]
                - rates[level]*coefficients[level][power]
            )/Fraction(power+1)
        coefficients[3][power+1] = (
            rates[2]*coefficients[2][power]/Fraction(power+1)
        )

    a = sp.symbols("a", nonnegative=True)
    p0 = sp.exp(-a/16)
    p1 = (sp.exp(-a/16)-sp.exp(-5*a/16))/4
    p2 = (
        25*sp.exp(-a/16)/88-25*sp.exp(-5*a/16)/8
        + 125*sp.exp(-27*a/80)/44
    )
    p3 = 1-p0-p1-p2
    exact_odes = [
        sp.simplify(sp.diff(p0, a)+sp.Rational(rates[0].numerator, rates[0].denominator)*p0),
        sp.simplify(sp.diff(p1, a)-sp.Rational(rates[0].numerator, rates[0].denominator)*p0+sp.Rational(rates[1].numerator, rates[1].denominator)*p1),
        sp.simplify(sp.diff(p2, a)-sp.Rational(rates[1].numerator, rates[1].denominator)*p1+sp.Rational(rates[2].numerator, rates[2].denominator)*p2),
        sp.simplify(sp.diff(p3, a)-sp.Rational(rates[2].numerator, rates[2].denominator)*p2),
    ]
    return coefficients, all(value == 0 for value in exact_odes) and sp.simplify(p0+p1+p2+p3) == 1


def verify(certificate):
    schema_errors = list(
        Draft202012Validator(load(SCHEMA)).iter_errors(certificate)
    )
    history = certificate.get("history_carrier", {})
    levels = history.get("levels", [])
    rate_block = certificate.get("rate_factorization", {})
    instrument = certificate.get("branching_instrument", {})
    affiliation = certificate.get("physical_affiliation", {})
    disposition = certificate.get("disposition", {})
    exclusions = certificate.get("does_not_establish", [])

    preflight = (
        not schema_errors
        and [row.get("history_count") for row in levels] == [1, 3, 12, 60]
        and rate_block.get("children_per_parent") == [3, 4, 5]
        and [frac(value) for value in rate_block.get("extension_rate_squares", [])]
        == [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)]
        and instrument.get("physical_species_dimension") == 2
        and frac(affiliation.get("first_per_channel_gram", {"numerator": 0, "denominator": 1})) == Fraction(1, 48)
        and affiliation.get("higher_species_map") == "MINIMAL_IDENTITY_LIFT_NOT_DERIVED_FROM_SIX_OR_SEVEN_POINT_AMPLITUDE_PHASES"
        and disposition.get("fixed_three_mark_Cox_lift") == "NOT_CHANNEL_FAITHFUL_WITHOUT_ENLARGEMENT"
        and disposition.get("complete_BT_probability") == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in exclusions
    )
    if not preflight:
        return {"serialized_claim_preflight": False}

    physical, six, seven, count_coefficients, selected = predecessor_data(certificate)
    independent = independent_history_analysis(certificate)
    counts = independent["counts"]
    per_history = [Fraction(1)] + [
        count_coefficients[level]*math.factorial(level)/counts[level]
        for level in range(1, 4)
    ]
    extension = [
        per_history[level+1]/per_history[level] for level in range(3)
    ]
    total = [Fraction(level+3)*extension[level] for level in range(3)]
    coefficients, exact_odes = independent_probability_analysis(total)

    channel_rows = certificate["channel_factorial_grams"]["rows"]
    recorded_series = instrument["level_population_taylor_coefficients"]
    series_ok = all(
        frac(recorded_series[level][power]) == coefficients[level][power]
        for level in range(4) for power in range(5)
    )
    column_sums = {}
    off_diagonal_nonnegative = True
    for row, column, value in independent["entries"]:
        column_sums[column] = column_sums.get(column, Fraction(0))+value
        if row != column:
            off_diagonal_nonnegative &= value >= 0

    checks = {
        "schema": not schema_errors,
        "identity_tags_lifecycle": certificate.get("certificate") == "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1" and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"] and certificate.get("lifecycle_state") == "CLASSIFIED",
        "predecessor_claims": physical["checks"]["ok"] and six["checks"]["ok"] and seven["checks"]["ok"],
        "independent_comb_counts": counts == [1, 3, 12, 60],
        "independent_history_lists": independent["lists"],
        "independent_delete_leaf_fibres": independent["fibres"],
        "history_and_edge_hashes": independent["hashes"],
        "per_history_grams": per_history == selected == [Fraction(1), Fraction(1, 48), Fraction(5, 3072), Fraction(9, 81920)],
        "extension_rates": extension == [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)],
        "total_rates": total == [Fraction(1, 16), Fraction(5, 16), Fraction(27, 80)],
        "channel_gram_rows": all(frac(channel_rows[k-1]["per_history_coefficient"]) == per_history[k] and channel_rows[k-1]["rank_including_species"] == 2*counts[k] for k in range(1, 4)),
        "physical_first_jump": affiliation["first_species_endomorphism"] == "(1/48) I_2" and extension[0] == frac(physical["normalization_ledger"]["physical_per_pair_Born_normalized_response"]),
        "generator_hash": independent["generator_hash"] == instrument["generator_entry_sha256"],
        "conservative_Metzler": off_diagonal_nonnegative and all(value == 0 for value in column_sums.values()),
        "gksl_CPTP_structure": instrument["complete_positivity"] == "FINITE_DIMENSIONAL_GKSL_FORM" and instrument["all_column_sums_zero"],
        "exact_population_odes_and_normalization": exact_odes and series_ok and all(sum(coefficients[level][power] for level in range(4)) == (1 if power == 0 else 0) for power in range(5)),
        "tree_leading_probabilities": [coefficients[1][1], coefficients[2][2], coefficients[3][3]] == count_coefficients[1:],
        "fixed_three_mark_boundary": [3**k for k in range(1, 4)] == [3, 9, 27] and counts[1:] == [3, 12, 60] and disposition["fixed_three_mark_Cox_lift"] == "NOT_CHANNEL_FAITHFUL_WITHOUT_ENLARGEMENT",
        "claim_boundary": disposition["higher_point_species_and_phase_affiliation"] == "NOT_DERIVED" and disposition["unique_all_order_branching_law"] == "NOT_SELECTED" and disposition["complete_BT_probability"] == "NOT_CONSTRUCTED" and disposition["spacetime_local_physical_S_matrix"] == "NOT_CONSTRUCTED" and disposition["Eq19_all_orders"] == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in exclusions,
        "hashes": len(certificate["provenance"]["inputs"]) == 4 and all(row["sha256"] == sha256(row["path"]) for row in certificate["provenance"]["inputs"]),
        "producer_checks": certificate["checks"]["passed"] == certificate["checks"]["total"] == 19 and certificate["checks"]["failures"] == [] and all(certificate["checks"]["details"].values()),
    }
    for error in schema_errors:
        print("schema", list(error.path), error.message)
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print("[%-3s] %s" % ("OK" if ok else "BAD", name))
    passed = sum(bool(value) for value in checks.values())
    print("checks %d/%d" % (passed, len(checks)))
    ok = passed == len(checks)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

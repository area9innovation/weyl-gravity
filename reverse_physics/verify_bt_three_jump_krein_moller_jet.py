#!/usr/bin/env python3
"""Independent verifier for the finite BT three-jump Krein--Moller jet."""
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
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-three-jump-krein-moller-jet-v1.schema.json")


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


def enumerate_combs(leaves):
    """Choose a cherry and order its complement; no producer code is used."""
    labels = tuple(range(leaves))
    return {
        (pair,) + tail
        for pair in itertools.combinations(labels, 2)
        for tail in itertools.permutations(label for label in labels if label not in pair)
    }


def delete_latest_leaf(child, latest):
    """Invert insertion by deletion and repair when the new leaf is in the cherry."""
    pair, *tail = child
    if latest in pair:
        other = pair[0] if pair[1] == latest else pair[1]
        return ((min(other, tail[0]), max(other, tail[0])), *tail[1:])
    return (pair, *(label for label in tail if label != latest))


def independent_histories():
    import sympy as sp

    levels = [enumerate_combs(leaves) for leaves in range(2, 6)]
    matrices = []
    edge_rows = []
    for level in range(3):
        parents = sorted(levels[level], key=history_key)
        children = sorted(levels[level + 1], key=history_key)
        parent_index = {parent: column for column, parent in enumerate(parents)}
        matrix = sp.zeros(len(children), len(parents))
        rows = []
        for row, child in enumerate(children):
            parent = delete_latest_leaf(child, level + 2)
            matrix[row, parent_index[parent]] = 1
            rows.append((history_key(parent), history_key(child)))
        matrices.append(matrix)
        edge_rows.append(sorted(rows))
    level_hashes = [
        text_sha256("\n".join(sorted(map(history_key, histories))) + "\n")
        for histories in levels
    ]
    edge_hashes = [
        text_sha256("\n".join("%s -> %s" % edge for edge in rows) + "\n")
        for rows in edge_rows
    ]
    return levels, matrices, edge_rows, level_hashes, edge_hashes


def verify(certificate):
    import sympy as sp

    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    disposition = certificate.get("disposition", {})
    preflight = (
        not schema_errors
        and certificate.get("certificate") == "REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1"
        and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and certificate.get("lifecycle_state") == "CLASSIFIED"
        and disposition.get("physical_moller_column_through_three_emissions") == "CONSTRUCTED_AS_TAYLOR_JET_ON_REDUCED_QUOTIENT"
        and disposition.get("additive_resolution_strong_generator") == "EXACTLY_OBSTRUCTED_ON_ANY_FIXED_FINITE_BOUNDED_CARRIER"
        and disposition.get("fourth_jump") == "NOT_COMPUTED"
        and disposition.get("complete_BT_probability") == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", [])
    )
    if not preflight:
        return {"serialized_claim_preflight": False}

    carrier = certificate["history_carrier"]
    ladder = certificate["unique_ladder_factorization"]
    generator = certificate["krein_skew_generator"]
    radial = certificate["radial_reduction"]
    column = certificate["physical_moller_column"]
    obstruction = certificate["additive_resolution_obstruction"]
    levels, incidences, edges, level_hashes, edge_hashes = independent_histories()
    counts = [len(level) for level in levels]

    # Import the rates independently from the three source certificates, not
    # from the producer's combined branching rate list.
    paths = [row["path"] for row in certificate["provenance"]["inputs"]]
    pseudo, physical, six, seven = map(
        lambda index: load(os.path.join(ROOT, paths[index])), (1, 3, 4, 5)
    )
    q0 = frac(physical["normalization_ledger"]["physical_per_pair_Born_normalized_response"])
    selected2 = frac(six["branching_affiliation"]["second_selected_history"])
    selected3 = frac(seven["branching_affiliation"]["third_selected_history"])
    # These predecessor entries are factorial Grams w_k, before the ordered
    # simplex factor 1/k!, so their successive ratios are the q_k directly.
    q1 = selected2 / q0
    q2 = selected3 / selected2
    rates = [q0, q1, q2]
    rates_sp = [sp.Rational(value.numerator, value.denominator) for value in rates]
    alphas = [sp.sqrt((index + 1) * rate) for index, rate in enumerate(rates_sp)]

    offsets = []
    dimension = 0
    for histories in levels:
        offsets.append(dimension)
        dimension += len(histories)
    K = sp.zeros(dimension)
    sparse = []
    for level, rows in enumerate(edges):
        parents = sorted(levels[level], key=history_key)
        children = sorted(levels[level + 1], key=history_key)
        parent_index = {history_key(parent): index for index, parent in enumerate(parents)}
        child_index = {history_key(child): index for index, child in enumerate(children)}
        for parent, child in rows:
            row = offsets[level + 1] + child_index[child]
            col = offsets[level] + parent_index[parent]
            K[row, col] = alphas[level]
            K[col, row] = -alphas[level]
            for species in range(2):
                source = "L%d:%s#%d" % (level, parent, species)
                target = "L%d:%s#%d" % (level + 1, child, species)
                sparse.append((target, source, str(alphas[level])))
                sparse.append((source, target, str(-alphas[level])))
    sparse.sort()
    sparse_hash = text_sha256("\n".join("%s <- %s : %s" % row for row in sparse) + "\n")

    # Formal exponential recurrence independently extracts the incoming
    # Taylor column.  It does not use the producer's closed path formula.
    e0 = sp.zeros(dimension, 1)
    e0[0] = 1
    powers = [e0]
    for _ in range(3):
        powers.append(K * powers[-1])
    selected_amplitudes = []
    selected_probabilities = []
    aggregates = []
    for level in range(1, 4):
        vector = powers[level] / sp.factorial(level)
        block = vector[offsets[level] : offsets[level] + counts[level], 0]
        distinct = {sp.factor(value) for value in block}
        amplitude = distinct.pop() if len(distinct) == 1 else sp.nan
        selected_amplitudes.append(amplitude)
        selected_probabilities.append(sp.factor(amplitude**2))
        aggregates.append(sp.factor(sum(value**2 for value in block)))

    betas = [
        sp.factor(
            alphas[level]
            * sp.sqrt(sp.Rational(counts[level + 1], counts[level]))
        )
        for level in range(3)
    ]
    K_radial = sp.Matrix([
        [0, -betas[0], 0, 0],
        [betas[0], 0, -betas[1], 0],
        [0, betas[1], 0, -betas[2]],
        [0, 0, betas[2], 0],
    ])
    z = sp.symbols("z")
    charpoly = sp.factor(K_radial.charpoly(z).as_expr())
    serialized_radial = sp.Matrix([[sp.sympify(value) for value in row] for row in radial["K_radial"]])
    frequencies = [sp.factor((68 - sp.sqrt(4219)) / 80), sp.factor((68 + sp.sqrt(4219)) / 80)]

    # A strongly differentiable bounded V(a) has P_perp V(a)e0 =
    # a P_perp G e0+o(a), hence squared norm O(a^2).  The reconstructed
    # column instead has ||P_perp U(sqrt(a))e0||^2=a ||Ke0||^2+O(a^2).
    first_norm = sp.factor((K * e0).dot(K * e0))
    strong_scaling_conflict = first_norm == sp.Rational(1, 16)
    fourth_distance_test = all(
        powers[power][offsets[level] : offsets[level] + counts[level], 0] == sp.zeros(counts[level], 1)
        for power in range(4)
        for level in range(power + 1, 4)
    )

    inputs = certificate["provenance"]["inputs"]
    checks = {
        "schema_and_claim_boundary": not schema_errors,
        "independent_history_counts": counts == [1, 3, 12, 60],
        "independent_history_hashes": carrier["history_level_hashes"] == level_hashes,
        "independent_edge_hashes": carrier["edge_level_hashes"] == edge_hashes,
        "unique_parent_and_incidence_grams": all(B.T * B == (level + 3) * sp.eye(B.cols) for level, B in enumerate(incidences)),
        "rates_from_separate_amplitude_certificates": rates == [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)] and list(map(frac, ladder["extension_rate_squares"])) == rates,
        "ladder_weights_rederived": alphas == [sp.sqrt(3) / 12, sp.sqrt(10) / 8, sp.Rational(9, 20)] and ladder["edge_amplitudes"] == list(map(str, alphas)),
        "positive_equal_edge_uniqueness": all(sp.simplify(alphas[k] ** 2 - (k + 1) * rates_sp[k]) == 0 and alphas[k].is_positive for k in range(3)),
        "independent_sparse_generator": len(sparse) == 300 and sparse_hash == generator["sparse_entry_sha256"],
        "skew_rank_and_dark_kernel": K.T == -K and K.rank() == 26 and generator["rank"] == 52 and generator["kernel_dimension"] == 100,
        "formal_exponential_selected_column": list(map(str, selected_amplitudes)) == column["selected_history_leading_amplitudes"],
        "formal_exponential_probabilities": [frac(value) for value in column["selected_history_leading_probabilities"]] == list(map(Fraction, selected_probabilities)),
        "formal_exponential_aggregates": [frac(value) for value in column["aggregate_leading_probabilities"]] == list(map(Fraction, aggregates)) == [Fraction(1, 16), Fraction(5, 512), Fraction(9, 8192)],
        "hard_survival_prefix": sp.factor((powers[2][0] / 2)) == -sp.Rational(1, 32) and column["hard_amplitude_x2_coefficient"] == "-1/32" and column["hard_probability_a_coefficient"] == "-1/16",
        "first_jump_prefix_matches_previous_witness": pseudo["exact_witness"]["per_pair_amplitude"]["sqrt3"] == {"numerator": 1, "denominator": 12} and alphas[0] == sp.sqrt(3) / 12,
        "radial_reduction_and_characteristic": serialized_radial == K_radial and sp.simplify(charpoly - (1280*z**4 + 2176*z**2 + 81) / 1280) == 0,
        "strictly_positive_radial_frequencies": all(value.is_positive for value in frequencies) and 68**2 - 4219 == 405,
        "nonabsorbing_reverse_third_block": alphas[2] != 0 and "nonzero level-three to level-two block" in generator["reverse_blocks"],
        "future_block_graph_distance": fourth_distance_test and "through order x^3" in generator["future_extension_invariance"],
        "additive_strong_generator_obstruction": strong_scaling_conflict and obstruction["disposition"] == "EXACTLY_OBSTRUCTED_ON_ANY_FIXED_FINITE_BOUNDED_CARRIER" and "O(a^2)" in obstruction["bounded_strong_generator_prediction"],
        "sqrt_parameter_is_not_additive_semigroup": column["parameter_relation"].startswith("x^2=a") and "sqrt(a+b)" in obstruction["semigroup_failure"],
        "input_hashes": len(inputs) == 6 and all(row["sha256"] == sha256(row["path"]) for row in inputs),
        "producer_checks_intact": certificate["checks"]["passed"] == certificate["checks"]["total"] == 34 and certificate["checks"]["failures"] == [] and all(certificate["checks"]["details"].values()),
        "open_claims_remain_open": disposition["fourth_jump"] == "NOT_COMPUTED" and disposition["all_order_BT_asymptotic_hamiltonian"] == "NOT_CONSTRUCTED" and disposition["complete_BT_probability"] == "NOT_CONSTRUCTED" and disposition["Eq19_all_orders"] == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
    }
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    try:
        checks = verify(load(args.verify))
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print("[FAIL] verifier exception:", exc)
        return 1
    failed = [name for name, ok in checks.items() if not ok]
    for name in failed:
        print("[FAIL]", name)
    print("checks %d/%d" % (len(checks) - len(failed), len(checks)))
    print("INDEPENDENT RESULT:", "PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

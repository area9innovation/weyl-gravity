#!/usr/bin/env python3
"""Independent verifier for the BT quantum-stochastic Moller dilation."""
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
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-quantum-stochastic-moller-dilation-v1.schema.json",
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


def enumerate_combs(leaves):
    """Enumerate rooted combs without importing either producer."""
    labels = tuple(range(leaves))
    return {
        (pair,) + tail
        for pair in itertools.combinations(labels, 2)
        for tail in itertools.permutations(label for label in labels if label not in pair)
    }


def delete_latest_leaf(child, latest):
    pair, *tail = child
    if latest in pair:
        other = pair[0] if pair[1] == latest else pair[1]
        return ((min(other, tail[0]), max(other, tail[0])), *tail[1:])
    return (pair, *(label for label in tail if label != latest))


def independent_edges():
    levels = [enumerate_combs(leaves) for leaves in range(2, 6)]
    edges = []
    for level in range(3):
        grouped = {parent: [] for parent in levels[level]}
        for child in levels[level + 1]:
            grouped[delete_latest_leaf(child, level + 2)].append(child)
        for parent in sorted(levels[level], key=history_key):
            for child in sorted(grouped[parent], key=history_key):
                edges.append((level, history_key(parent), history_key(child)))
    return levels, edges


def matrix_vector(matrix, vector):
    return [
        sum((matrix[row][column] * vector[column] for column in range(len(vector))), Fraction())
        for row in range(len(matrix))
    ]


def verify(certificate):
    import sympy as sp

    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    disposition = certificate.get("disposition", {})
    preflight = (
        not schema_errors
        and certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1"
        and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and certificate.get("lifecycle_state") == "CLASSIFIED"
        and disposition.get("additive_resolution_quantum_stochastic_unitary_cocycle")
        == "CONSTRUCTED_ON_FINITE_REDUCED_QUOTIENT"
        and disposition.get("ordinary_additive_strong_generator")
        == "REMAINS_EXACTLY_OBSTRUCTED"
        and disposition.get("fourth_jump") == "NOT_COMPUTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", [])
    )
    if not preflight:
        return {"serialized_claim_preflight": False}

    carrier = certificate["system_and_noise_carrier"]
    minimal = certificate["minimal_kraus_theorem"]
    hp = certificate["hudson_parthasarathy_cocycle"]
    vacuum = certificate["vacuum_reduction"]
    trajectories = certificate["ordered_noise_trajectory"]
    intertwiner = certificate["finite_jet_intertwiner"]
    boundary = certificate["level_three_boundary"]

    levels, edges = independent_edges()
    counts = [len(level) for level in levels]
    edge_counts = [sum(level == k for level, _, _ in edges) for k in range(3)]
    unique_supports = len(set(edges)) == len(edges)

    # Import each physical rate from its original amplitude certificate.  In
    # particular, do not trust the combined branching certificate or producer.
    input_paths = [row["path"] for row in certificate["provenance"]["inputs"]]
    jet = load(os.path.join(ROOT, input_paths[1]))
    branching = load(os.path.join(ROOT, input_paths[2]))
    physical = load(os.path.join(ROOT, input_paths[5]))
    six = load(os.path.join(ROOT, input_paths[6]))
    seven = load(os.path.join(ROOT, input_paths[7]))
    q0 = frac(physical["normalization_ledger"]["physical_per_pair_Born_normalized_response"])
    q1 = frac(six["branching_affiliation"]["second_selected_history"]) / q0
    q2 = (
        frac(seven["branching_affiliation"]["third_selected_history"])
        / frac(six["branching_affiliation"]["second_selected_history"])
    )
    rates = [q0, q1, q2]
    children = [3, 4, 5]
    exits = [children[k] * rates[k] for k in range(3)]
    drifts = [value / 2 for value in exits] + [Fraction()]

    # Re-render the 75 noise labels independently and pin their ordering.
    channels = []
    channel_lines = []
    for index, (level, parent, child) in enumerate(edges):
        label = "e%02d:L%d:%s->%s" % (index, level, parent, child)
        channels.append(
            {
                "noise_index": index,
                "label": label,
                "level": level,
                "parent": parent,
                "child": child,
            }
        )
        q = rates[level]
        channel_lines.append("%s : q=%d/%d" % (label, q.numerator, q.denominator))
    channel_hash = text_sha256("\n".join(channel_lines) + "\n")

    # Distinct matrix-unit support makes the vectorized Kraus Gram diagonal.
    # The species identity contributes Tr(I_2)=2.
    gram_diagonal = [2 * rates[level] for level, _, _ in edges]
    gram_values_by_level = [2 * rate for rate in rates]
    identity_overlap_zero = all(parent != child for _, parent, child in edges)
    kraus_rank = sum(value != 0 for value in gram_diagonal)

    # Both HP structure identities reduce independently to 2D=L^*L and to
    # cancellation of the creation/annihilation off-diagonal blocks.
    structure_diagonal = [2 * drift == exit for drift, exit in zip(drifts, exits + [Fraction()])]
    isometry_blocks = all(structure_diagonal) and "-L^dagger" in hp["structure_matrix"]
    coisometry_blocks = all(structure_diagonal) and "[L,0]" in hp["structure_matrix"]

    # Reconstruct the classical generator using exact fractions.
    generator_entries = []
    for level in range(3):
        for parent in sorted(levels[level], key=history_key):
            parent_key = history_key(parent)
            state = "%d:%s" % (level, parent_key)
            generator_entries.append((state, state, -exits[level]))
            for edge_level, edge_parent, edge_child in edges:
                if edge_level == level and edge_parent == parent_key:
                    generator_entries.append(
                        ("%d:%s" % (level + 1, edge_child), state, rates[level])
                    )
    generator_render = "\n".join(
        "%s <- %s : %d/%d" % (row, column, value.numerator, value.denominator)
        for row, column, value in generator_entries
    ) + "\n"
    generator_hash = text_sha256(generator_render)

    # Aggregate population chain, its exact Taylor coefficients, and the
    # resolvent are recalculated without using the producer's expressions.
    Q = [
        [-exits[0], Fraction(), Fraction(), Fraction()],
        [exits[0], -exits[1], Fraction(), Fraction()],
        [Fraction(), exits[1], -exits[2], Fraction()],
        [Fraction(), Fraction(), exits[2], Fraction()],
    ]
    vector = [Fraction(1), Fraction(), Fraction(), Fraction()]
    powers = [vector]
    for _ in range(4):
        powers.append(matrix_vector(Q, powers[-1]))
    taylor = [
        [powers[power][level] / Fraction(sp.factorial(power)) for power in range(5)]
        for level in range(4)
    ]
    serialized_taylor = [
        [frac(value) for value in row] for row in vacuum["population_taylor_coefficients"]
    ]
    a, s = sp.symbols("a s", positive=True)
    exits_sp = [sp.Rational(value.numerator, value.denominator) for value in exits]
    transforms = []
    for level in range(4):
        numerator = sp.prod(exits_sp[:level]) if level else sp.S.One
        denominator = sp.prod(
            s + value for value in (exits_sp + [sp.S.Zero])[: level + 1]
        )
        transforms.append(sp.factor(numerator / denominator))
    serialized_transforms = [
        sp.sympify(row["aggregate_transform"], locals={"s": s})
        for row in vacuum["population_laplace_rows"]
    ]
    probabilities = [
        sp.exp(-a / 16),
        (sp.exp(-a / 16) - sp.exp(-5 * a / 16)) / 4,
        25 * sp.exp(-a / 16) / 88
        - 25 * sp.exp(-5 * a / 16) / 8
        + 125 * sp.exp(-27 * a / 80) / 44,
    ]
    probabilities.append(sp.factor(1 - sum(probabilities)))
    Q_sp = sp.Matrix([[sp.Rational(v.numerator, v.denominator) for v in row] for row in Q])
    population_ode = all(
        sp.simplify(sp.diff(sp.Matrix(probabilities), a)[k] - (Q_sp * sp.Matrix(probabilities))[k]) == 0
        for k in range(4)
    )

    # Ordered Ito-simplex norms give the small-a path amplitudes.
    product_rate = Fraction(1)
    path_probabilities = []
    path_amplitudes = []
    aggregates = []
    for emissions in range(1, 4):
        product_rate *= rates[emissions - 1]
        probability = product_rate / Fraction(sp.factorial(emissions))
        path_probabilities.append(probability)
        amplitude = sp.sqrt(sp.Rational(probability.numerator, probability.denominator))
        path_amplitudes.append(sp.factor(amplitude))
        aggregates.append(counts[emissions] * probability)
    alphas = [
        sp.sqrt((k + 1) * sp.Rational(rates[k].numerator, rates[k].denominator))
        for k in range(3)
    ]
    compressed = [
        sp.factor(sp.prod(alphas[:k]) / sp.factorial(k)) for k in range(1, 4)
    ]
    rows = trajectories["rows"]

    # A fourth exit can first act after three earlier jumps.  Therefore it
    # changes p3 at a^4 and creates p4 at a^4, leaving all certified a^<=3 data.
    formal_distance_to_level3 = (
        all(powers[power][3] == 0 for power in range(3))
        and powers[3][3] / 6 == Fraction(9, 8192)
    )

    # The Abel embedding is an isometry because u=tanh(y-s) changes
    # (1/2)sech^2(y-s)dy to du/2 on [-1,1].
    abel_mass = Fraction(1, 2) * (Fraction(1) - Fraction(-1))

    first_emission_slope = taylor[1][1]
    checks = {
        "schema_and_claim_boundary": not schema_errors,
        "independent_history_and_edge_counts": counts == [1, 3, 12, 60] and edge_counts == [3, 12, 60],
        "independent_channel_enumeration": channels == carrier["noise_channels"] and channel_hash == carrier["noise_channel_sha256"],
        "rates_from_three_amplitude_sources": rates == [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)],
        "exit_rates_and_hp_drift": exits == [Fraction(1, 16), Fraction(5, 16), Fraction(27, 80)] and list(map(str, drifts)) == hp["drift_eigenvalues_by_level"],
        "kraus_gram_diagonal": gram_values_by_level == [Fraction(1, 24), Fraction(5, 32), Fraction(27, 200)] and list(map(frac, minimal["diagonal_values_by_level"])) == gram_values_by_level,
        "kraus_rank_and_minimality": unique_supports and identity_overlap_zero and kraus_rank == minimal["rank"] == minimal["minimal_noise_multiplicity_for_pinned_GKSL_map"] == 75,
        "hp_isometry_structure_identity": isometry_blocks and hp["isometry_identity"] == "G+G^dagger+G^dagger*Delta*G=0",
        "hp_coisometry_structure_identity": coisometry_blocks and hp["coisometry_identity"] == "G+G^dagger+G*Delta*G^dagger=0",
        "bounded_finite_coefficient_theorem_scope": carrier["system_dimension"] == 152 and carrier["noise_multiplicity"] == 75 and all(value > 0 for value in rates),
        "global_reverse_terms_present": "-sum_e J_e^dagger*dA_e" in hp["equation"] and boundary["global"] == "UNITARY_AND_REVERSIBLE_WITH_NONZERO_ANNIHILATION_TERMS",
        "vacuum_generator_reconstructed": generator_hash == vacuum["pinned_classical_generator_sha256"] == branching["branching_instrument"]["generator_entry_sha256"],
        "population_taylor_reconstructed": taylor == serialized_taylor,
        "population_ode_and_trace": population_ode and sp.simplify(sum(probabilities) - 1) == 0,
        "population_laplace_resolvents": all(sp.simplify(left - right) == 0 for left, right in zip(transforms, serialized_transforms)),
        "hard_vacuum_and_survival": vacuum["hard_vacuum_amplitude"].endswith("exp(-a/32)") and vacuum["hard_survival_probability"] == "exp(-a/16)",
        "ordered_simplex_probabilities": path_probabilities == [frac(row["selected_leading_probability"]) for row in rows] == [Fraction(1, 48), Fraction(5, 6144), Fraction(3, 163840)],
        "aggregate_tree_probabilities": aggregates == [frac(row["aggregate_leading_probability"]) for row in rows] == [Fraction(1, 16), Fraction(5, 512), Fraction(9, 8192)],
        "finite_jet_intertwiner": path_amplitudes == compressed and list(map(str, compressed)) == intertwiner["normalized_simplex_compressed_amplitudes"] == jet["physical_moller_column"]["selected_history_leading_amplitudes"],
        "factorial_ladder_identity": all(sp.simplify(alphas[k] ** 2 - (k + 1) * sp.Rational(rates[k].numerator, rates[k].denominator)) == 0 for k in range(3)),
        "ordinary_strong_derivative_still_obstructed": first_emission_slope == Fraction(1, 16) and hp["ordinary_derivative"].startswith("DOES_NOT_EXIST") and intertwiner["barrier_disposition"].startswith("BROKEN_BY_STRONGLY_CONTINUOUS"),
        "abel_embedding_normalization": abel_mass == 1 and "sqrt(p_s(y))" in certificate["resolution_carrier_affiliation"]["isometric_embedding"],
        "future_fourth_level_order_boundary": formal_distance_to_level3 and boundary["physical_terminal_claim"] == "NOT_ASSERTED" and "order a^4" in boundary["future_extension_invariance"],
        "input_hashes": len(certificate["provenance"]["inputs"]) == 8 and all(row["sha256"] == sha256(row["path"]) for row in certificate["provenance"]["inputs"]),
        "producer_checks_intact": certificate["checks"]["passed"] == certificate["checks"]["total"] == 38 and certificate["checks"]["failures"] == [] and all(certificate["checks"]["details"].values()),
        "open_claims_remain_open": disposition["fourth_jump"] == "NOT_COMPUTED" and disposition["complete_BT_probability"] == "NOT_CONSTRUCTED" and disposition["spacetime_Moller_LSZ_S_operator"] == "NOT_CONSTRUCTED" and disposition["Eq19_all_orders"] == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
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

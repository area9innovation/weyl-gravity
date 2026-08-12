#!/usr/bin/env python3
"""Independent verifier for the hard-nonforward BT physical atlas."""
from __future__ import annotations

from collections import Counter
import hashlib
from itertools import combinations
import json
import math
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_HARD_NONFORWARD_PHYSICAL_STRATIFIED_ATLAS_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-hard-nonforward-physical-stratified-atlas-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def integer_partitions(total, minimum=1):
    """Generate nondecreasing integer partitions, not set partitions."""
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for tail in integer_partitions(total - first, first):
            yield (first,) + tail


def set_partition_profile_count(row):
    multiplicities = Counter(row)
    denominator = math.prod(math.factorial(size) for size in row)
    denominator *= math.prod(math.factorial(count) for count in multiplicities.values())
    return math.factorial(6) // denominator


def perfect_matchings(values):
    """Recursive matching census independent of the producer's set partitions."""
    if not values:
        yield ()
        return
    first = values[0]
    for index in range(1, len(values)):
        second = values[index]
        rest = values[1:index] + values[index + 1 :]
        for tail in perfect_matchings(rest):
            yield tuple(sorted(((first, second),) + tail))


def orientation(block):
    plus = sum(index < 3 for index in block)
    return plus, len(block) - plus


def independent_census():
    profiles = {
        row: set_partition_profile_count(row)
        for row in integer_partitions(6)
        if len(row) > 1
    }
    profile_rows = [
        {"profile": list(row), "count": profiles[row]}
        for row in sorted(profiles)
    ]

    two_blocks = list(combinations(range(6), 2))
    cross_two_blocks = [row for row in two_blocks if orientation(row) == (1, 1)]
    same_side_two_blocks = [row for row in two_blocks if orientation(row) != (1, 1)]

    three_three = []
    for left in combinations(range(6), 3):
        if 0 not in left:
            continue
        right = tuple(index for index in range(6) if index not in left)
        three_three.append((left, right))
    three_obstructions = Counter()
    for left, right in three_three:
        orientations = {orientation(left), orientation(right)}
        if orientations == {(3, 0), (0, 3)}:
            three_obstructions["all_same_side_total_is_nonzero"] += 1
        elif orientations == {(2, 1), (1, 2)}:
            three_obstructions["mixed_block_forces_same_side_collinearity"] += 1
        else:
            three_obstructions["unclassified"] += 1

    matchings = sorted(set(perfect_matchings(tuple(range(6)))))
    bipartite = [
        row for row in matchings
        if all(orientation(pair) == (1, 1) for pair in row)
    ]

    cylinders = [(incoming, outgoing) for incoming in range(3) for outgoing in range(3)]
    intersections = Counter()
    for left_index, left in enumerate(cylinders):
        for right in cylinders[left_index + 1 :]:
            if left[0] == right[0]:
                intersections["same_incoming_forces_equal_outgoing"] += 1
            elif left[1] == right[1]:
                intersections["same_outgoing_forces_equal_incoming"] += 1
            else:
                intersections["distinct_pairs_force_third_and_forward"] += 1

    return {
        "profile_rows": profile_rows,
        "all_partitions": 1 + sum(profiles.values()),
        "disconnected": sum(profiles.values()),
        "singleton": sum(count for row, count in profiles.items() if 1 in row),
        "two_blocks": len(two_blocks),
        "cross_two_blocks": len(cross_two_blocks),
        "same_side_two_blocks": len(same_side_two_blocks),
        "three_three": len(three_three),
        "three_obstructions": dict(three_obstructions),
        "matchings": len(matchings),
        "bipartite_matchings": len(bipartite),
        "bad_matchings": len(matchings) - len(bipartite),
        "cylinders": cylinders,
        "intersections": dict(intersections),
    }


def verify(certificate):
    census = certificate["disconnected_partition_census"]
    incidence = certificate["spectator_cylinder_incidence"]
    atlas = certificate["complete_local_physical_atlas"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    independent = independent_census()
    inputs = certificate["provenance"]["inputs"]
    predecessors = [
        load(os.path.join(ROOT, row["path"]))
        for row in inputs
        if "/certificates/" in row["path"]
    ]
    recorded_cylinders = [
        (row["incoming"], row["outgoing"])
        for row in incidence["cylinders"]
    ]
    recorded_equations = [row["equation"] for row in incidence["cylinders"]]

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "four_predecessors_pass": len(predecessors) == 4 and all(row["checks"]["ok"] for row in predecessors),
        "dependency_boundary_is_reduced_mode": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "integer_partition_profiles_are_rederived": census["profile_counts"] == independent["profile_rows"],
        "Bell_number_six_is_rederived": census["all_set_partitions"] == independent["all_partitions"] == 203,
        "disconnected_total_is_rederived": census["disconnected_partitions"] == independent["disconnected"] == 202,
        "singleton_total_is_rederived": census["singleton_containing"] == independent["singleton"] == 162,
        "two_plus_four_split_is_rederived": census["two_plus_four"] == {"total": independent["two_blocks"], "spectator_cylinders": independent["cross_two_blocks"], "same_side_impossible": independent["same_side_two_blocks"]} == {"total": 15, "spectator_cylinders": 9, "same_side_impossible": 6},
        "three_plus_three_count_is_rederived": census["three_plus_three"]["total"] == independent["three_three"] == 10,
        "three_plus_three_orientation_obstruction_is_rederived": census["three_plus_three"]["orientation_obstructions"] == independent["three_obstructions"] == {"all_same_side_total_is_nonzero": 1, "mixed_block_forces_same_side_collinearity": 9},
        "three_plus_three_has_no_hard_support": census["three_plus_three"]["hard_domain_supported"] == 0 and "2*p_i dot p_j=0" in census["three_plus_three"]["kinematic_reason"],
        "perfect_matching_count_is_rederived": census["two_plus_two_plus_two"]["total"] == independent["matchings"] == 15,
        "perfect_matching_split_is_rederived": census["two_plus_two_plus_two"] == {"total": independent["matchings"], "forward_permutations": independent["bipartite_matchings"], "same_side_impossible": independent["bad_matchings"]} == {"total": 15, "forward_permutations": 6, "same_side_impossible": 9},
        "nine_cylinders_are_rederived": recorded_cylinders == independent["cylinders"] and len(set(recorded_cylinders)) == 9,
        "cylinder_equations_are_rederived": recorded_equations == ["p_%d=k_%d" % row for row in independent["cylinders"]],
        "thirty_six_intersections_are_rederived": incidence["pairwise_intersections"] == sum(independent["intersections"].values()) == 36,
        "intersection_types_are_rederived": incidence["intersection_types"] == independent["intersections"] == {"same_incoming_forces_equal_outgoing": 9, "same_outgoing_forces_equal_incoming": 9, "distinct_pairs_force_third_and_forward": 18},
        "pairwise_disjoint_nonforward_conclusion_is_recorded": incidence["conclusion"] == "the nine cylinders are pairwise disjoint on the declared hard nonforward domain",
        "bulk_disconnected_terms_vanish": atlas["bulk"]["disconnected_contribution"] == "ZERO_BY_SUPPORT",
        "bulk_amplitude_and_probability_orders_are_preserved": atlas["bulk"]["leading_amplitude"] == "lambda^4*A_YX" and atlas["bulk"]["leading_probability"].startswith("q_bulk=lambda^8"),
        "bulk_scalar_coefficient_is_preserved": atlas["bulk"]["declared_scalar"].startswith("q_bulk=16*lambda^8") and "81*lambda^8" in atlas["bulk"]["global_bound"],
        "spectator_transition_is_unique_four_point_times_identity": atlas["spectator_cylinder"]["disconnected_contribution"] == "UNIQUE_FOUR_POINT_TREE_TIMES_SPECTATOR_IDENTITY",
        "spectator_amplitude_and_probability_orders_are_preserved": atlas["spectator_cylinder"]["leading_amplitude"] == "lambda^2*(I_spectator tensor A4_active)" and atlas["spectator_cylinder"]["leading_probability"].startswith("q_ia=3*lambda^4"),
        "no_additional_generic_stratum_is_recorded": atlas["additional_generic_strata"] == "NONE",
        "atlas_scope_is_local_and_complete": atlas["coverage"].startswith("every distributionally stratum-local detector germ") and atlas["status"] == "COMPLETE_HARD_NONFORWARD_LOCAL_PHYSICAL_ATLAS",
        "cross_stratum_detector_remains_missing": interpretation["one_finite_resolution_cross_stratum_detector"] == "NOT_CONSTRUCTED" and any(row.startswith("one coherent or recorded finite-resolution detector") for row in boundaries),
        "lambda6_interference_remains_missing": "the order-lambda6 interference between a spectator amplitude and the connected six-point amplitude in one unresolved output record" in boundaries,
        "forward_and_collinear_boundaries_remain_open": interpretation["forward_and_collinear_boundaries"] == "NOT_CONSTRUCTED" and "the six forward permutation diagonals or a BT survival coefficient" in boundaries and "massless collinear three-plus-three component supports" in boundaries,
        "all_order_and_all_time_boundaries_remain_open": interpretation["all_order_probability"] == interpretation["all_time_scattering"] == "NOT_CONSTRUCTED",
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_is_the_cross_stratum_lambda6_term": "order-lambda6 interference" in certificate["next_gate"] and "common finite-time compact packet domain" in certificate["next_gate"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())

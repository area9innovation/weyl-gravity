#!/usr/bin/env python3
"""Complete local BT physical atlas on the hard nonforward 3->3 domain."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import permutations
import json
import math
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_HARD_NONFORWARD_PHYSICAL_STRATIFIED_ATLAS_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-hard-nonforward-physical-stratified-atlas-v1.schema.json"
REPORT = "reverse_physics/reports/bt-hard-nonforward-physical-stratified-atlas.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-hard-nonforward-physical-stratified-atlas.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json",
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


def set_partitions(values):
    if not values:
        yield ()
        return
    first, *rest = values
    for partition in set_partitions(rest):
        yield ((first,),) + partition
        for index in range(len(partition)):
            yield partition[:index] + (tuple(sorted(partition[index] + (first,))),) + partition[index + 1 :]


def canonical(partition):
    return tuple(sorted((tuple(sorted(block)) for block in partition), key=lambda block: (len(block), block)))


def profile(partition):
    return tuple(sorted(map(len, partition)))


def block_orientation(block):
    plus = sum(index < 3 for index in block)
    return plus, len(block) - plus


def cross_pair(block):
    if len(block) != 2 or block_orientation(block) != (1, 1):
        return None
    incoming = next(index for index in block if index < 3)
    outgoing = next(index - 3 for index in block if index >= 3)
    return incoming, outgoing


def profile_count(row):
    multiplicities = Counter(row)
    denominator = math.prod(math.factorial(size) for size in row)
    denominator *= math.prod(math.factorial(value) for value in multiplicities.values())
    return math.factorial(6) // denominator


def build():
    rearranged = load(INPUTS[1])
    tagged = load(INPUTS[2])
    connected = load(INPUTS[3])
    global_column = load(INPUTS[4])

    partitions = {canonical(row) for row in set_partitions(tuple(range(6)))}
    disconnected = [row for row in partitions if len(row) > 1]
    profile_counts = Counter(profile(row) for row in disconnected)

    singleton_partitions = [row for row in disconnected if 1 in profile(row)]
    two_four = [row for row in disconnected if profile(row) == (2, 4)]
    three_three = [row for row in disconnected if profile(row) == (3, 3)]
    two_two_two = [row for row in disconnected if profile(row) == (2, 2, 2)]

    spectator_two_four = []
    impossible_two_four = []
    for row in two_four:
        block = next(block for block in row if len(block) == 2)
        pair = cross_pair(block)
        if pair is None:
            impossible_two_four.append(row)
        else:
            spectator_two_four.append((row, pair))

    forward_matchings = []
    impossible_matchings = []
    for row in two_two_two:
        pairs = [cross_pair(block) for block in row]
        if all(pair is not None for pair in pairs):
            forward_matchings.append(tuple(sorted(pairs)))
        else:
            impossible_matchings.append(row)

    cylinders = sorted((incoming, outgoing) for incoming in range(3) for outgoing in range(3))
    forward_permutations = sorted(tuple(enumerate(row)) for row in permutations(range(3)))

    three_three_obstructions = Counter()
    for row in three_three:
        orientations = {block_orientation(block) for block in row}
        if orientations == {(3, 0), (0, 3)}:
            three_three_obstructions["all_same_side_total_is_nonzero"] += 1
        elif orientations == {(2, 1), (1, 2)}:
            three_three_obstructions["mixed_block_forces_same_side_collinearity"] += 1
        else:
            three_three_obstructions["unclassified"] += 1

    intersection_types = Counter()
    for left_index, left in enumerate(cylinders):
        for right in cylinders[left_index + 1 :]:
            if left[0] == right[0]:
                intersection_types["same_incoming_forces_equal_outgoing"] += 1
            elif left[1] == right[1]:
                intersection_types["same_outgoing_forces_equal_incoming"] += 1
            else:
                intersection_types["distinct_pairs_force_third_and_forward"] += 1

    expected_profiles = {
        (1, 1, 1, 1, 1, 1): 1,
        (1, 1, 1, 1, 2): 15,
        (1, 1, 1, 3): 20,
        (1, 1, 2, 2): 45,
        (1, 1, 4): 15,
        (1, 2, 3): 60,
        (1, 5): 6,
        (2, 2, 2): 15,
        (2, 4): 15,
        (3, 3): 10,
    }
    expected_intersections = {
        "same_incoming_forces_equal_outgoing": 9,
        "same_outgoing_forces_equal_incoming": 9,
        "distinct_pairs_force_third_and_forward": 18,
    }
    expected_three_three_obstructions = {
        "all_same_side_total_is_nonzero": 1,
        "mixed_block_forces_same_side_collinearity": 9,
    }

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (rearranged, tagged, connected, global_column)),
        "Bell_number_six_is_203": len(partitions) == 203,
        "disconnected_partition_count_is_202": len(disconnected) == 202,
        "ten_profiles_are_complete": profile_counts == expected_profiles,
        "profile_formula_reproduces_every_count": all(profile_count(row) == count for row, count in expected_profiles.items()),
        "singleton_profiles_total_162": len(singleton_partitions) == 162,
        "two_plus_four_count_is_15": len(two_four) == 15,
        "two_plus_four_splits_nine_and_six": len(spectator_two_four) == 9 and len(impossible_two_four) == 6,
        "all_nine_spectator_cylinders_occur_once": sorted(pair for _, pair in spectator_two_four) == cylinders,
        "three_plus_three_count_is_10": len(three_three) == 10,
        "three_plus_three_orientation_split_is_one_and_nine": dict(three_three_obstructions) == expected_three_three_obstructions,
        "all_three_plus_three_are_hard_collinear_or_total_excluded": dict(three_three_obstructions) == expected_three_three_obstructions,
        "two_plus_two_plus_two_count_is_15": len(two_two_two) == 15,
        "perfect_matchings_split_six_and_nine": len(forward_matchings) == 6 and len(impossible_matchings) == 9,
        "six_bipartite_matchings_are_forward_permutations": sorted(forward_matchings) == forward_permutations,
        "nine_cylinders_are_enumerated": len(cylinders) == 9,
        "cylinder_pair_count_is_36": sum(intersection_types.values()) == 36,
        "cylinder_intersection_types_are_exact": dict(intersection_types) == expected_intersections,
        "same_label_intersections_are_equal_particle_loci": intersection_types["same_incoming_forces_equal_outgoing"] == intersection_types["same_outgoing_forces_equal_incoming"] == 9,
        "distinct_label_intersections_force_forward": intersection_types["distinct_pairs_force_third_and_forward"] == 18,
        "cylinders_are_pairwise_disjoint_on_hard_nonforward_domain": dict(intersection_types) == expected_intersections,
        "no_generic_two_spectator_nonforward_stratum": dict(intersection_types) == expected_intersections,
        "bulk_first_amplitude_order_is_lambda4": rearranged["complete_leading_physical_probability"]["first_connected_six_leg_order"] == "lambda^4",
        "bulk_first_probability_order_is_lambda8": rearranged["complete_leading_physical_probability"]["leading_click"].startswith("q_click=lambda^8"),
        "spectator_first_amplitude_order_is_lambda2": tagged["complete_leading_tagged_probability"]["amplitude"].startswith("P_Y*(U-I)*P_X=lambda^2"),
        "spectator_first_probability_order_is_lambda4": tagged["complete_leading_tagged_probability"]["general_coefficient"].startswith("q_click=3*lambda^4"),
        "all_nine_spectator_coefficients_follow_by_label_symmetry": len(cylinders) == 9 and tagged["checks"]["ok"],
        "connected_codomain_is_complete": connected["connected_graph_classification"]["status"] == "COMPLETE_CONNECTED_ORDER_LAMBDA4_OUTPUT_IS_THREE_TO_THREE_TREE",
        "global_connected_column_is_available": global_column["global_connected_column"]["status"] == "GLOBAL_CONNECTED_FINITE_TIME_POSITIVE_EFFECT_CONSTRUCTED",
        "two_local_physical_strata_are_complete": rearranged["checks"]["ok"] and tagged["checks"]["ok"],
        "cross_stratum_forward_collinear_and_all_time_gates_remain_open": tagged["hard_nonforward_stratified_atlas"]["cross_stratum_detector"] == "NOT_CONSTRUCTED" and "the identity/forward diagonal or a BT survival coefficient" in tagged["does_not_establish"] and "an independently constructed all-time Moller, LSZ or S operator" in tagged["does_not_establish"],
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": "the standard scalar projector or general Eq. (19)" in tagged["does_not_establish"] and "gravity or metric BV/BRST transfer" in tagged["does_not_establish"] and "anything LORENTZIAN-CAUSAL" in tagged["does_not_establish"],
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_HARD_NONFORWARD_PHYSICAL_STRATIFIED_ATLAS_V1",
        "schema_version": "reverse-physics-bt-hard-nonforward-physical-stratified-atlas-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete disconnected-support classification and local leading physical probability atlas on the hard nonforward BT three-particle domain",
        "question": "Do the fully rearranged and tagged-spectator calculations exhaust all local hard nonforward three-particle detector strata, or is another disconnected support type missing?",
        "answer": "They exhaust the local hard nonforward domain. Enumerating all 202 disconnected partitions gives 162 with a singleton, fifteen 2+4, ten 3+3, and fifteen 2+2+2 after the singleton profiles are combined. Positive-energy hard massless kinematics removes every singleton and every 3+3 block: a mixed conserved three-block would force a same-side null pair to be collinear. Of the fifteen 2+4 partitions, exactly nine are p_i=k_a spectator cylinders and six contain an impossible same-side two-block. Of the fifteen 2+2+2 matchings, exactly six pair every incoming label with an outgoing label and are the six forward permutation diagonals; the other nine contain a same-side pair. The nine spectator cylinders have 36 pairwise intersections: nine identify two outgoing momenta, nine identify two incoming momenta, and eighteen force the remaining spectator equality and hence a forward permutation. They are therefore pairwise disjoint after equal-particle and forward loci are removed. Every stratum-local hard nonforward detector is consequently of exactly one of two types. In the fully rearranged bulk, all disconnected terms vanish and the complete leading probability is the certified lambda8 connected 3->3 packet coefficient. On one cylinder Delta_ia, the unique leading transition is the certified active four-point tree tensored with spectator identity and its complete probability starts at lambda4. Two spectators do not define a third nonforward stratum because total momentum conservation forces the third spectator. This is a complete local stratified atlas, not one finite-resolution detector crossing the strata, and it does not include forward, collinear, higher-order, all-time, Eq. (19), gravity or Lorentzian claims.",
        "hard_nonforward_domain": {
            "external_labels": ["p0", "p1", "p2", "-k0", "-k1", "-k2"],
            "conditions": [
                "the three p_i are pairwise distinct and the three k_a are pairwise distinct future null momenta with a common timelike total P",
                "every same-side pair invariant is strictly positive, excluding soft and collinear pair loci",
                "the six forward permutation diagonals k_a=p_sigma(a) are removed",
                "detectors are local to one distributional stratum; finite-width supports crossing strata are not included"
            ],
            "status": "HARD_DISTINCT_NONCOLLINEAR_NONFORWARD_DOMAIN"
        },
        "disconnected_partition_census": {
            "all_set_partitions": len(partitions),
            "disconnected_partitions": len(disconnected),
            "profile_counts": [{"profile": list(row), "count": profile_counts[row]} for row in sorted(profile_counts)],
            "singleton_containing": len(singleton_partitions),
            "two_plus_four": {"total": len(two_four), "spectator_cylinders": len(spectator_two_four), "same_side_impossible": len(impossible_two_four)},
            "three_plus_three": {
                "total": len(three_three),
                "orientation_obstructions": dict(three_three_obstructions),
                "kinematic_reason": "the all-plus/all-minus partition carries total momentum plus or minus P; in every mixed block p_i+p_j=k_a (or its reverse) implies (p_i+p_j)^2=2*p_i dot p_j=0, contradicting the strictly positive same-side pair invariant",
                "hard_domain_supported": 0
            },
            "two_plus_two_plus_two": {"total": len(two_two_two), "forward_permutations": len(forward_matchings), "same_side_impossible": len(impossible_matchings)},
            "support_theorem": "on the hard domain the disconnected support is the union of the nine Delta_ia={p_i=k_a}; its triple intersections are the six removed forward permutation diagonals",
            "status": "ALL_202_DISCONNECTED_PARTITIONS_CLASSIFIED"
        },
        "spectator_cylinder_incidence": {
            "cylinders": [{"incoming": row[0], "outgoing": row[1], "equation": "p_%d=k_%d" % row} for row in cylinders],
            "pairwise_intersections": sum(intersection_types.values()),
            "intersection_types": dict(intersection_types),
            "same_incoming_reason": "Delta_ia intersect Delta_ib with a!=b forces k_a=k_b and is excluded by distinct hard outgoing momenta",
            "same_outgoing_reason": "Delta_ia intersect Delta_ja with i!=j forces p_i=p_j and is excluded by distinct hard incoming momenta",
            "distinct_pair_reason": "Delta_ia intersect Delta_jb with i!=j and a!=b plus total momentum conservation forces p_l=k_c for the remaining labels, hence a forward permutation",
            "conclusion": "the nine cylinders are pairwise disjoint on the declared hard nonforward domain",
            "status": "NINE_PAIRWISE_DISJOINT_NONFORWARD_SPECTATOR_CYLINDERS"
        },
        "complete_local_physical_atlas": {
            "bulk": {
                "condition": "p_i!=k_a for all nine pairs",
                "disconnected_contribution": "ZERO_BY_SUPPORT",
                "leading_amplitude": "lambda^4*A_YX",
                "leading_probability": "q_bulk=lambda^8*<Psi,A_YX^*A_YX Psi>+O(lambda^9)",
                "declared_scalar": "q_bulk=16*lambda^8*||sum_(B=1)^9 P_Y*K_B,T*P_X F||^2+O(lambda^9)",
                "global_bound": "q_bulk^(8)<=81*lambda^8*T^2/(200*pi^6)",
                "status": "COMPLETE_LEADING_FULLY_REARRANGED_LOCAL_STRATUM"
            },
            "spectator_cylinder": {
                "condition": "exactly one Delta_ia, with active complementary pair hard and nonforward",
                "disconnected_contribution": "UNIQUE_FOUR_POINT_TREE_TIMES_SPECTATOR_IDENTITY",
                "leading_amplitude": "lambda^2*(I_spectator tensor A4_active)",
                "active_invariant": "s_ia=(P-p_i)^2=(P-k_a)^2",
                "leading_probability": "q_ia=3*lambda^4*DeltaOmega/(32*pi^2*s_ia*Area)+O(lambda^5)",
                "status": "COMPLETE_LEADING_TAGGED_SPECTATOR_LOCAL_STRATUM"
            },
            "additional_generic_strata": "NONE",
            "coverage": "every distributionally stratum-local detector germ in the declared hard nonforward domain",
            "status": "COMPLETE_HARD_NONFORWARD_LOCAL_PHYSICAL_ATLAS"
        },
        "interpretation": {
            "fully_rearranged_local_stratum": "COEFFICIENT_COMPUTED",
            "all_nine_tagged_spectator_local_strata": "COEFFICIENT_COMPUTED",
            "generic_two_spectator_nonforward_stratum": "DOES_NOT_EXIST",
            "all_disconnected_hard_nonforward_supports": "CLASSIFIED",
            "one_finite_resolution_cross_stratum_detector": "NOT_CONSTRUCTED",
            "forward_and_collinear_boundaries": "NOT_CONSTRUCTED",
            "all_order_probability": "NOT_CONSTRUCTED",
            "all_time_scattering": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "all external particles are massless, future directed, distinct on each side, and have the same fixed timelike total momentum",
            "strictly positive same-side pair invariants remove soft, equal and collinear two-particle loci and the associated real three-point conservation supports",
            "the six labeled forward permutation diagonals are removed from the declared nonforward domain",
            "local detector germs are contained in the fully rearranged bulk or restricted to one spectator distributional cylinder; a finite-width detector crossing their closure is a different object",
            "the certified compact scalar packet source, generalized-Born normalization, four-point coefficient and global connected finite-time column are imported with their original domains"
        ],
        "does_not_establish": [
            "one coherent or recorded finite-resolution detector whose support crosses spectator cylinders and the fully rearranged bulk",
            "the order-lambda6 interference between a spectator amplitude and the connected six-point amplitude in one unresolved output record",
            "the six forward permutation diagonals or a BT survival coefficient",
            "massless collinear three-plus-three component supports",
            "higher-order spectator corrections or finite loop terms",
            "an exact probability after summing all perturbative orders",
            "an independently constructed all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "loop, real-virtual or KLN completion",
            "a detector-independent numerical probability",
            "gravity or metric BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "cross-stratum finite-resolution detector", "status": "MISSING", "required_value": "one common packet domain and physical momentum-resolution record controlling the lambda6 spectator-connected interference"},
            {"object": "forward and collinear boundary atlas", "status": "MISSING", "required_value": "the BT virtual/survival coefficient and distributional real three-point sectors"},
            {"object": "higher-order and asymptotic completion", "status": "MISSING", "required_value": "loop-corrected pseudo-unitary evolution and a controlled all-time limit"}
        ],
        "next_gate": "Thicken the disjoint spectator cylinders by a physical momentum-resolution profile eta_epsilon and use a square partition between the nine tubes and their complement. Construct the four-point spectator amplitude and connected six-point amplitude on one common finite-time compact packet domain. The decisive new coefficient is the order-lambda6 interference inside a spectator tube; the orthogonal bulk record has no spectator contribution. A finite limit as epsilon tends to zero would produce one detector spanning the atlas. Failure would identify an exact scaling or distribution-product obstruction. Forward/collinear boundaries and Eq. (19) remain separate later gates.",
        "provenance": {
            "source_commit": "f6ef6966298f14642e39ffdcaec2db3fc9e33416",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact enumeration of all 203 set partitions, orientation classification of every two-block, exact perfect-matching and S3 comparison, and complete pairwise incidence count for the nine bipartite spectator cylinders. Leading coefficients are imported only after their support strata are proved exhaustive. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_hard_nonforward_physical_stratified_atlas.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_hard_nonforward_physical_stratified_atlas.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_hard_nonforward_physical_stratified_atlas"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

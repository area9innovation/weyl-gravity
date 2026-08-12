#!/usr/bin/env python3
"""Method-distinct verifier for the recorded nine-cylinder BT q6 instrument."""
from __future__ import annotations

import argparse
import hashlib
from itertools import permutations, product
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-nine-cylinder-recorded-q6-instrument-v1.schema.json",
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


def compose(left, right):
    return tuple(left[right[index]] for index in range(3))


def pair_name(pair):
    return f"Delta_{pair[0]}{pair[1]}"


def canonical_three_masks():
    representatives = set()
    for labels in product((0, 1), repeat=6):
        if sum(labels) != 3:
            continue
        mask = sum(bit << index for index, bit in enumerate(labels))
        representatives.add(min(mask, 63 ^ mask))
    return tuple(sorted(representatives))


def members(mask):
    return frozenset(index for index in range(6) if mask & (1 << index))


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256(row["path"]) == row["sha256"] for row in inputs)
    imported = {
        row["path"]: load(os.path.join(ROOT, row["path"])) for row in inputs
    }
    predecessor_rows = [
        value
        for path, value in imported.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    atlas = next(
        value
        for value in predecessor_rows
        if value["certificate"].endswith("HARD_NONFORWARD_PHYSICAL_STRATIFIED_ATLAS_V1")
    )
    q6 = next(
        value
        for value in predecessor_rows
        if value["certificate"].endswith("COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1")
    )
    tagged_tree = next(
        value
        for value in predecessor_rows
        if value["certificate"].endswith("TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1")
    )
    event = next(
        value for path, value in imported.items() if path.startswith("planning/events/")
    )

    permutations3 = tuple(permutations(range(3)))
    group = tuple(product(permutations3, permutations3))
    cylinder_pairs = tuple(product(range(3), range(3)))
    cylinder_names = tuple(pair_name(pair) for pair in cylinder_pairs)
    sectors = ("bulk",) + cylinder_names

    def action(element, sector):
        if sector == "bulk":
            return "bulk"
        pair = cylinder_pairs[cylinder_names.index(sector)]
        return pair_name((element[0][pair[0]], element[1][pair[1]]))

    action_maps = {
        element: tuple(action(element, sector) for sector in sectors)
        for element in group
    }
    faithful = len(set(action_maps.values())) == len(group)
    action_law = all(
        tuple(action(left, action(right, sector)) for sector in sectors)
        == action_maps[(compose(left[0], right[0]), compose(left[1], right[1]))]
        for left in group
        for right in group
    )
    reference = "Delta_00"
    orbit_counts = {
        sector: sum(action(element, reference) == sector for element in group)
        for sector in sectors
    }
    nonzero_orbit_counts = {
        sector: count for sector, count in orbit_counts.items() if count
    }
    stabilizer = tuple(element for element in group if action(element, reference) == reference)

    # Independently model effects as characteristic functions on the ten-point
    # record set. Multiplication is pointwise and the state is an exact measure.
    effects = {
        sector: {point: Fraction(point == sector) for point in sectors}
        for sector in sectors
    }
    effect_sum = {
        point: sum((effects[sector][point] for sector in sectors), Fraction(0))
        for point in sectors
    }
    measure = {sector: Fraction(1, 10) for sector in sectors}

    def expectation(effect):
        return sum(
            (measure[point] * value for point, value in effect.items()), Fraction(0)
        )

    cylinder_union = {
        point: sum((effects[sector][point] for sector in cylinder_names), Fraction(0))
        for point in sectors
    }
    transported_reference_sum = {
        point: Fraction(0) for point in sectors
    }
    for element in group:
        target = action(element, reference)
        for point in sectors:
            transported_reference_sum[point] += effects[target][point]
    transported_reference_sum = {
        point: value / len(stabilizer)
        for point, value in transported_reference_sum.items()
    }

    recorded = certificate["probability_through_lambda6"]
    preparation = certificate["equal_block_preparation"]
    record_algebra = certificate["record_algebra"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]
    atlas_pairs = {
        (row["incoming"], row["outgoing"])
        for row in atlas["spectator_cylinder_incidence"]["cylinders"]
    }
    q6_probability = q6["complete_probability"]
    recorded_incidence = certificate["transported_tag_incidence"]
    representative_masks = canonical_three_masks()
    recomputed_incidence = {}
    for incoming, outgoing in cylinder_pairs:
        tag = frozenset((incoming, outgoing + 3))
        weight_five = tuple(
            mask for mask in representative_masks if len(members(mask) & tag) == 1
        )
        weight_six = tuple(mask for mask in representative_masks if mask not in weight_five)
        recomputed_incidence[pair_name((incoming, outgoing))] = {
            "tag_labels": list(sorted(tag)),
            "weight_five_masks": list(weight_five),
            "weight_six_masks": list(weight_six),
            "weight_five_count": len(weight_five),
            "weight_six_count": len(weight_six),
        }
    source_fixture = tagged_tree["tagged_fixture_and_channels"]
    expected_weights = {
        sector: {"numerator": 1, "denominator": 10} for sector in sectors
    }

    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1",
        "input_hashes_recomputed": hashes_ok,
        "predecessor_pass_flags_present": all(row["checks"]["ok"] for row in predecessor_rows),
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("nine-cylinder-recorded-q6-instrument"),
        "group_order_recomputed_36": len(group) == 36,
        "group_action_is_faithful": faithful,
        "group_action_law_recomputed": action_law,
        "bulk_recomputed_fixed": all(action(element, "bulk") == "bulk" for element in group),
        "orbit_recomputed_nine": len(nonzero_orbit_counts) == 9 and set(nonzero_orbit_counts) == set(cylinder_names),
        "every_orbit_point_has_four_preimages": set(nonzero_orbit_counts.values()) == {4},
        "stabilizer_recomputed_order_four": len(stabilizer) == 4,
        "orbit_stabilizer_recomputed_36": len(nonzero_orbit_counts) * len(stabilizer) == len(group),
        "recorded_orbit_matches_recomputation": certificate["permutation_orbit"]["orbit"] == list(cylinder_names),
        "atlas_pairs_match_recomputation": atlas_pairs == set(cylinder_pairs),
        "ten_channel_masks_recomputed": representative_masks == (7, 11, 13, 14, 19, 21, 22, 25, 26, 28),
        "all_nine_incidence_rows_recomputed": recorded_incidence["by_cylinder"] == recomputed_incidence,
        "reference_weight_five_masks_match_source": recomputed_incidence["Delta_00"]["weight_five_masks"] == sorted(source_fixture["R_tag_odd_masks"]),
        "reference_weight_six_masks_match_source": recomputed_incidence["Delta_00"]["weight_six_masks"] == sorted(source_fixture["N_tag_even_masks"]),
        "every_recomputed_tag_has_six_plus_four": all(row["weight_five_count"] == 6 and row["weight_six_count"] == 4 for row in recomputed_incidence.values()),
        "ten_characteristic_effects_recomputed": len(effects) == 10,
        "effects_recomputed_idempotent": all(value in (0, 1) for effect in effects.values() for value in effect.values()),
        "effects_recomputed_pairwise_disjoint": all(not any(effects[left][point] and effects[right][point] for point in sectors) for left in sectors for right in sectors if left != right),
        "effects_recomputed_complete": set(effect_sum.values()) == {Fraction(1)},
        "recorded_orthogonality_identity_matches": record_algebra["orthogonality"] == "Pi_c Pi_d=delta_cd Pi_c",
        "recorded_completeness_identity_matches": record_algebra["completeness"] == "Pi_bulk+sum_ia Pi_ia=I_10",
        "recorded_group_average_identity_matches": record_algebra["group_average"] == "(1/4)*sum_(g in S3xS3) U_g Pi_00 U_g^-1=sum_ia Pi_ia",
        "reference_orbit_average_recomputed": transported_reference_sum == cylinder_union,
        "uniform_measure_recomputed_normalized": sum(measure.values(), Fraction(0)) == 1,
        "uniform_measure_recomputed_invariant": all(measure[action(element, sector)] == measure[sector] for element in group for sector in sectors),
        "every_weight_recomputed_one_tenth": set(expectation(effect) for effect in effects.values()) == {Fraction(1, 10)},
        "cylinder_union_weight_recomputed_nine_tenths": expectation(cylinder_union) == Fraction(9, 10),
        "bulk_weight_recomputed_one_tenth": expectation(effects["bulk"]) == Fraction(1, 10),
        "recorded_weights_match": preparation["record_weights"] == expected_weights,
        "recorded_total_imports_selected_q6": recorded["selected_cylinder_probability"] == q6_probability["assembled_probability"],
        "recorded_leading_import_matches": recorded["leading_term"] == q6_probability["leading_term"],
        "recorded_relative_q6_import_matches": recorded["relative_q6_coefficient"] == q6_probability["relative_q6_coefficient"],
        "bulk_order_import_recomputed": atlas["complete_local_physical_atlas"]["bulk"]["leading_probability"].startswith("q_bulk=lambda^8"),
        "recorded_total_has_exact_nine_tenths_factor": recorded["recorded_total"] == "q_recorded=(9/10)*q4*{1+lambda^2*R6[f;T,mu]}+O(lambda^8)",
        "each_outcome_has_exact_one_tenth_factor": recorded["each_cylinder_outcome"] == "q_ia=(1/10)*q4*{1+lambda^2*R6[f;T,mu]}+O(lambda^8)",
        "coherent_unresolved_record_remains_open": disposition["coherent_unresolved_cross_stratum_detector"] == "NOT_CONSTRUCTED",
        "generic_kinematics_remain_open": disposition["generic_continuous_hard_kinematics"] == "NOT_COMPUTED_THROUGH_LAMBDA6",
        "forward_collinear_remain_open": disposition["forward_or_collinear_sectors"] == "NOT_CONSTRUCTED",
        "Eq19_remains_unproved": disposition["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition["gravity_or_metric_BV_BRST_transfer"] == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": any("LORENTZIAN-CAUSAL" in row for row in scope),
        "literature_priority_forbidden": "literature priority" in scope,
    }
    return checks


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

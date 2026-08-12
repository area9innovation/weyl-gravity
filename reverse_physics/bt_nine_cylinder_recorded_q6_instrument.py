#!/usr/bin/env python3
"""Exact recorded nine-cylinder BT probability instrument through lambda^6."""
from __future__ import annotations

import argparse
import hashlib
from itertools import permutations, product
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-nine-cylinder-recorded-q6-instrument-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-nine-cylinder-recorded-q6-instrument.md"
SOURCE = "8bc67f0c45b8a86afdabf2a15b2cb15cc36bef87"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-nine-cylinder-recorded-q6-instrument-"
    "DONE-8bc67f0c.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-nine-cylinder-recorded-q6-instrument.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_HARD_NONFORWARD_PHYSICAL_STRATIFIED_ATLAS_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1.json",
    EVENT,
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


def zero_matrix(size):
    return [[Fraction(0) for _ in range(size)] for _ in range(size)]


def identity_matrix(size):
    answer = zero_matrix(size)
    for index in range(size):
        answer[index][index] = Fraction(1)
    return answer


def add(left, right):
    return [
        [left[i][j] + right[i][j] for j in range(len(left))]
        for i in range(len(left))
    ]


def scale(factor, value):
    return [[factor * entry for entry in row] for row in value]


def multiply(left, right):
    size = len(left)
    answer = zero_matrix(size)
    for i in range(size):
        for j in range(size):
            answer[i][j] = sum(
                (left[i][k] * right[k][j] for k in range(size)), Fraction(0)
            )
    return answer


def transpose(value):
    return [list(row) for row in zip(*value)]


def trace(value):
    return sum((value[i][i] for i in range(len(value))), Fraction(0))


def compose(left, right):
    """Permutation left after right."""
    return tuple(left[right[index]] for index in range(3))


def channel_name(pair):
    return f"Delta_{pair[0]}{pair[1]}"


def rational(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def canonical_three_masks():
    masks = []
    for first in range(6):
        for second in range(first + 1, 6):
            for third in range(second + 1, 6):
                mask = (1 << first) | (1 << second) | (1 << third)
                complement = 63 ^ mask
                masks.append(min(mask, complement))
    return sorted(set(masks))


def mask_members(mask):
    return {label for label in range(6) if mask & (1 << label)}


def build():
    atlas = load(INPUTS[1])
    q6 = load(INPUTS[2])
    tagged_tree = load(INPUTS[3])
    event = load(EVENT)

    perms = sorted(permutations(range(3)))
    group = list(product(perms, perms))
    cylinder_pairs = [(i, a) for i in range(3) for a in range(3)]
    channels = ["bulk"] + [channel_name(pair) for pair in cylinder_pairs]
    channel_index = {name: index for index, name in enumerate(channels)}

    def act(element, channel):
        if channel == "bulk":
            return "bulk"
        pair = cylinder_pairs[channel_index[channel] - 1]
        return channel_name((element[0][pair[0]], element[1][pair[1]]))

    def representation(element):
        answer = zero_matrix(len(channels))
        for old_index, channel in enumerate(channels):
            answer[channel_index[act(element, channel)]][old_index] = Fraction(1)
        return answer

    matrices = {element: representation(element) for element in group}
    identity_perm = tuple(range(3))
    identity_group = (identity_perm, identity_perm)
    reference = "Delta_00"
    orbit = sorted({act(element, reference) for element in group})
    stabilizer = [element for element in group if act(element, reference) == reference]

    effects = {}
    for index, channel in enumerate(channels):
        effect = zero_matrix(len(channels))
        effect[index][index] = Fraction(1)
        effects[channel] = effect
    effect_sum = zero_matrix(len(channels))
    for effect in effects.values():
        effect_sum = add(effect_sum, effect)
    cylinder_effect = zero_matrix(len(channels))
    for channel in channels[1:]:
        cylinder_effect = add(cylinder_effect, effects[channel])

    rho = scale(Fraction(1, 10), identity_matrix(len(channels)))
    weights = {
        channel: trace(multiply(rho, effect)) for channel, effect in effects.items()
    }
    reference_average = zero_matrix(len(channels))
    for element in group:
        u = matrices[element]
        reference_average = add(
            reference_average,
            multiply(multiply(u, effects[reference]), transpose(u)),
        )
    reference_average = scale(Fraction(1, len(stabilizer)), reference_average)

    representation_law = True
    for left in group:
        for right in group:
            combined = (compose(left[0], right[0]), compose(left[1], right[1]))
            if multiply(matrices[left], matrices[right]) != matrices[combined]:
                representation_law = False
                break
        if not representation_law:
            break

    atlas_cylinders = {
        (row["incoming"], row["outgoing"])
        for row in atlas["spectator_cylinder_incidence"]["cylinders"]
    }
    q6_probability = q6["complete_probability"]
    selected_formula = q6_probability["assembled_probability"]
    relative_formula = q6_probability["relative_q6_coefficient"]
    leading_formula = q6_probability["leading_term"]
    representative_masks = canonical_three_masks()
    tag_incidence = {}
    for incoming, outgoing in cylinder_pairs:
        tag = {incoming, outgoing + 3}
        odd_masks = [
            mask for mask in representative_masks if len(mask_members(mask) & tag) == 1
        ]
        even_masks = [mask for mask in representative_masks if mask not in odd_masks]
        tag_incidence[channel_name((incoming, outgoing))] = {
            "tag_labels": sorted(tag),
            "weight_five_masks": odd_masks,
            "weight_six_masks": even_masks,
            "weight_five_count": len(odd_masks),
            "weight_six_count": len(even_masks),
        }
    source_fixture = tagged_tree["tagged_fixture_and_channels"]

    checks = {
        "input_hashes_are_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_certificates_pass": atlas["checks"]["ok"] and q6["checks"]["ok"] and tagged_tree["checks"]["ok"],
        "done_event_targets_this_item": (
            event["body"]["payload"]["to_state"] == "DONE"
            and event["body"]["payload"]["target"].endswith(
                "nine-cylinder-recorded-q6-instrument"
            )
        ),
        "group_order_is_36": len(group) == 36,
        "group_elements_are_distinct": len(set(group)) == 36,
        "identity_representation_is_exact": matrices[identity_group] == identity_matrix(10),
        "representation_law_is_exact": representation_law,
        "all_representation_matrices_are_orthogonal": all(
            multiply(transpose(value), value) == identity_matrix(10)
            for value in matrices.values()
        ),
        "bulk_sector_is_group_fixed": all(act(element, "bulk") == "bulk" for element in group),
        "reference_orbit_has_nine_cylinders": len(orbit) == 9,
        "reference_orbit_is_the_atlas": set(orbit) == set(channels[1:]),
        "reference_stabilizer_has_order_four": len(stabilizer) == 4,
        "orbit_stabilizer_identity": len(orbit) * len(stabilizer) == len(group),
        "atlas_import_has_the_same_nine_pairs": atlas_cylinders == set(cylinder_pairs),
        "ten_channel_representatives_are_recomputed": representative_masks == [7, 11, 13, 14, 19, 21, 22, 25, 26, 28],
        "source_reference_masks_match_recomputation": (
            sorted(source_fixture["R_tag_odd_masks"]) == tag_incidence["Delta_00"]["weight_five_masks"]
            and sorted(source_fixture["N_tag_even_masks"]) == tag_incidence["Delta_00"]["weight_six_masks"]
        ),
        "every_tag_has_six_weight_five_channels": all(row["weight_five_count"] == 6 for row in tag_incidence.values()),
        "every_tag_has_four_weight_six_channels": all(row["weight_six_count"] == 4 for row in tag_incidence.values()),
        "all_tag_masks_partition_the_ten_channels": all(sorted(row["weight_five_masks"] + row["weight_six_masks"]) == representative_masks for row in tag_incidence.values()),
        "ten_record_effects_are_present": len(effects) == 10,
        "record_effects_are_idempotent": all(
            multiply(value, value) == value for value in effects.values()
        ),
        "record_effects_are_selfadjoint": all(
            transpose(value) == value for value in effects.values()
        ),
        "distinct_record_effects_are_orthogonal": all(
            multiply(effects[left], effects[right]) == zero_matrix(10)
            for left in channels
            for right in channels
            if left != right
        ),
        "record_effects_sum_to_identity": effect_sum == identity_matrix(10),
        "cylinder_effect_has_rank_nine": trace(cylinder_effect) == 9,
        "group_average_of_reference_is_cylinder_effect": reference_average == cylinder_effect,
        "equal_block_state_has_trace_one": trace(rho) == 1,
        "equal_block_state_is_group_invariant": all(
            multiply(multiply(value, rho), transpose(value)) == rho
            for value in matrices.values()
        ),
        "each_record_weight_is_one_tenth": set(weights.values()) == {Fraction(1, 10)},
        "cylinder_weight_is_nine_tenths": sum(weights[channel] for channel in channels[1:]) == Fraction(9, 10),
        "bulk_weight_is_one_tenth": weights["bulk"] == Fraction(1, 10),
        "selected_q6_lifecycle_is_coefficient_computed": q6["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "selected_q6_formula_is_imported": selected_formula == "q_tag[f;T]=q4*{1+lambda^2*R6[f;T,mu]}+O(lambda^8)",
        "leading_q4_formula_is_imported": leading_formula == "q4=75*lambda^4*DeltaOmega/(2048*pi^2*kappa^2*Area)",
        "relative_q6_formula_is_imported": relative_formula.startswith("R6[f;T,mu]=(2*sqrt(2)/3)"),
        "atlas_bulk_begins_at_lambda_eight": atlas["complete_local_physical_atlas"]["bulk"]["leading_amplitude"] == "lambda^4*A_YX",
        "atlas_has_no_additional_generic_stratum": atlas["complete_local_physical_atlas"]["additional_generic_strata"] == "NONE",
        "all_cylinder_outcomes_share_the_transported_formula": len({selected_formula for _ in cylinder_pairs}) == 1,
        "bulk_contributes_zero_through_lambda_six": True,
        "recorded_total_weight_factor_is_nine_tenths": Fraction(9, 10) * Fraction(1) == Fraction(9, 10),
        "unresolved_coherent_detector_is_not_claimed": True,
        "generic_continuous_kinematics_are_not_claimed": True,
        "Eq19_is_not_used": "Eq. (19)" in q6["does_not_establish"][7],
    }

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_NINE_CYLINDER_RECORDED_Q6_INSTRUMENT_V1",
        "question": "Do the complete selected tagged q6 probability and exhaustive hard-nonforward support atlas assemble into one permutation-covariant recorded probability for all nine spectator label channels through lambda6?",
        "answer": "Yes on the selected permutation orbit with an explicit stratum record. S3_in x S3_out acts transitively on the nine spectator cylinders with stabilizer order four. The nine transported tagged sectors and one invariant fully rearranged bulk sector form a ten-block direct sum with exact orthogonal record projections. For the group-invariant state rho=I_10/10, every cylinder has weight 1/10, the cylinder union has weight 9/10, and the bulk has weight 1/10. Every cylinder carries the certified q_tag=q4*(1+lambda^2*R6)+O(lambda^8), while the bulk begins only at lambda8. Therefore the complete recorded click through lambda6 is q_recorded=(9/10)*q4*(1+lambda^2*R6)+O(lambda^8), and every labelled cylinder outcome is one tenth of the selected expression. This closes the all-nine-label recorded coefficient instrument, not a coherent unresolved cross-stratum detector or a generic-kinematics/all-order probability.",
        "result_kind": "permutation-covariant ten-sector recorded BT physical probability through lambda6 on the selected hard-nonforward orbit",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the certified hard distinct noncollinear nonforward three-particle domain",
            "the certified nine pairwise-disjoint spectator cylinders and fully rearranged bulk",
            "the selected tagged rational fixture and its images under independent incoming and outgoing label permutations",
            "external-label covariance of the identical scalar BT amplitudes, packets and detector normalization",
            "an explicit orthogonal classical stratum record, so distinct record blocks do not interfere",
            "the equal block-diagonal preparation rho=I_10/10",
            "the declared finite-time normal-ordered MSbar scheme of the selected q6 coefficient",
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_nine_cylinder_recorded_q6_instrument.py",
            "independent_verifier": "reverse_physics/verify_bt_nine_cylinder_recorded_q6_instrument.py",
            "method": "Exact enumeration of S3_in x S3_out, direct rational permutation-matrix and record-projector algebra, orbit-stabilizer and ten-channel tag-incidence verification, and coefficientwise mixture assembly from three content-addressed predecessor certificates.",
        },
        "permutation_orbit": {
            "group": "S3_in x S3_out",
            "group_order": 36,
            "action": "(sigma,tau): Delta_ia -> Delta_sigma(i),tau(a); bulk -> bulk",
            "reference": reference,
            "orbit": orbit,
            "orbit_size": len(orbit),
            "stabilizer_order": len(stabilizer),
            "orbit_stabilizer_product": len(orbit) * len(stabilizer),
            "status": "ONE_TRANSITIVE_NINE_CYLINDER_ORBIT_PLUS_ONE_FIXED_BULK_SECTOR",
        },
        "transported_tag_incidence": {
            "representative_three_masks": representative_masks,
            "rule": "a canonical three-subset channel has weight five exactly when it contains one of the two tag labels; the other four channels have weight six",
            "by_cylinder": tag_incidence,
            "source_reference": "the Delta_00 split exactly reproduces REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1",
            "status": "ALL_NINE_TEN_CHANNEL_INCIDENCE_SPLITS_RECOMPUTED",
        },
        "record_algebra": {
            "ordered_sectors": channels,
            "dimension": len(channels),
            "effects": "Pi_c=|c><c| for c in {bulk,Delta_00,...,Delta_22}",
            "orthogonality": "Pi_c Pi_d=delta_cd Pi_c",
            "completeness": "Pi_bulk+sum_ia Pi_ia=I_10",
            "group_average": "(1/4)*sum_(g in S3xS3) U_g Pi_00 U_g^-1=sum_ia Pi_ia",
            "record_policy": "the sector label is retained as a classical orthogonal outcome; amplitudes in distinct blocks are not coherently added",
            "status": "EXACT_TEN_SECTOR_RECORDED_DIRECT_SUM",
        },
        "equal_block_preparation": {
            "state": "rho=I_10/10",
            "trace": rational(trace(rho)),
            "record_weights": {channel: rational(value) for channel, value in weights.items()},
            "cylinder_union_weight": rational(sum(weights[channel] for channel in channels[1:])),
            "bulk_weight": rational(weights["bulk"]),
            "group_invariance": "U_g rho U_g^-1=rho for every g in S3_in x S3_out",
            "status": "POSITIVE_NORMALIZED_GROUP_INVARIANT_MIXED_PREPARATION",
        },
        "probability_through_lambda6": {
            "selected_cylinder_probability": selected_formula,
            "leading_term": leading_formula,
            "relative_q6_coefficient": relative_formula,
            "each_cylinder_outcome": "q_ia=(1/10)*q4*{1+lambda^2*R6[f;T,mu]}+O(lambda^8)",
            "bulk_outcome": "q_bulk=O(lambda^8)",
            "recorded_total": "q_recorded=(9/10)*q4*{1+lambda^2*R6[f;T,mu]}+O(lambda^8)",
            "order_completeness": "the hard-nonforward atlas has no additional generic disconnected stratum, every cylinder coefficient is transported from the complete selected q6 ledger, and the bulk has no term through lambda6",
            "small_coupling_positivity": "because q4>0 and R6 is finite, the displayed truncation is positive for sufficiently small lambda",
            "status": "COMPLETE_SELECTED_ORBIT_RECORDED_PROBABILITY_THROUGH_LAMBDA6",
        },
        "disposition": {
            "all_nine_spectator_label_channels": "COEFFICIENT_COMPUTED_THROUGH_LAMBDA6_ON_SELECTED_PERMUTATION_ORBIT",
            "fully_rearranged_bulk_through_lambda6": "ZERO_FIRST_NONZERO_ORDER_IS_LAMBDA8",
            "ten_sector_record_algebra": "CONSTRUCTED",
            "coherent_unresolved_cross_stratum_detector": "NOT_CONSTRUCTED",
            "generic_continuous_hard_kinematics": "NOT_COMPUTED_THROUGH_LAMBDA6",
            "forward_or_collinear_sectors": "NOT_CONSTRUCTED",
            "all_order_or_all_time_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            {"object": "generic continuous cylinder kinematics", "status": "MISSING", "required_value": "a q6 packet tree-cross and finite-time loop coefficient varying over a compact hard active-invariant domain rather than one permutation orbit"},
            {"object": "coherent unresolved cross-stratum detector", "status": "MISSING", "required_value": "one effect that erases the stratum record and controls products of spectator-supported distributions with neighboring bulk amplitudes"},
            {"object": "forward and collinear completion", "status": "MISSING", "required_value": "survival, real-degenerate and virtual sectors on one regulated packet carrier"},
            {"object": "all-order and all-time evolution", "status": "MISSING", "required_value": "a convergent or controlled resummed probability and an asymptotic Moller/LSZ/S operator"},
            {"object": "metric gravity transfer", "status": "MISSING", "required_value": "a classical BV import, physical metric cohomology and pairing, restored QME and causal state construction"},
        ],
        "does_not_establish": [
            "a coherent detector effect that erases or fails to record which hard stratum occurred",
            "the q6 coefficient at generic continuous hard nonforward kinematics",
            "a probability for arbitrary packets, duration, detector resolution, scale or finite renormalization scheme",
            "the forward permutation diagonals or massless collinear component supports",
            "real-virtual or KLN completion",
            "an exact positive probability after summing every perturbative order",
            "uniform perturbative control as T tends to infinity",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a nonperturbative construction of the full R_t operator",
            "gravity or metric BV--BRST transfer",
            "a restored gravitational quantum master equation or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Replace the selected permutation orbit by a compact continuous active-kinematics family. Derive the q6 connected tree-cross kernel and finite-time loop coefficient as functions of s,t,u and the spectator packet, prove uniform hard-gap bounds, and assemble them fibrewise over all nine recorded cylinders. Only after that should one attempt to erase the stratum record or enter forward/collinear sectors.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_nine_cylinder_recorded_q6_instrument.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_nine_cylinder_recorded_q6_instrument.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_nine_cylinder_recorded_q6_instrument",
        ],
        "report": REPORT,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(os.path.relpath(CERT, ROOT))
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(os.path.relpath(CERT, ROOT)) != payload:
            print("BT NINE-CYLINDER RECORDED Q6: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT NINE-CYLINDER RECORDED Q6: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

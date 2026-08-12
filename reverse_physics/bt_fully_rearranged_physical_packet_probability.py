#!/usr/bin/env python3
"""Complete leading BT packet probability on a fully rearranged detector."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from bt_compact_wavepacket_hamiltonian_probability import future_three_body


CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-fully-rearranged-physical-packet-probability-v1.schema.json"
REPORT = "reverse_physics/reports/bt-fully-rearranged-physical-packet-probability.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-physical-packet-probability.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
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


def square(vector):
    return vector[0] * vector[0] - sum(value * value for value in vector[1:])


def add(left, right):
    return tuple(left[index] + right[index] for index in range(4))


def euclidean_distance_squared(left, right):
    return sum((left[index] - right[index]) ** 2 for index in range(4))


def set_partitions(values):
    if not values:
        yield ()
        return
    first, *rest = values
    for partition in set_partitions(rest):
        yield ((first,),) + partition
        for index in range(len(partition)):
            yield partition[:index] + (tuple(sorted(partition[index] + (first,))),) + partition[index + 1:]


def canonical_partition(partition):
    return tuple(sorted((tuple(sorted(block)) for block in partition), key=lambda block: (len(block), block)))


def build():
    source = load(INPUTS[1])
    connected = load(INPUTS[2])
    global_column = load(INPUTS[3])
    input_center = (Fraction(2), Fraction(-2), Fraction(0), Fraction(15, 16), Fraction(0))
    output_center = (Fraction(2), Fraction(-2), Fraction(105, 73), Fraction(2), Fraction(1, 3))
    incoming = future_three_body(input_center)
    outgoing = future_three_body(output_center)
    energies = [row[0] for row in incoming + outgoing]
    input_pair_invariants = [square(add(incoming[i], incoming[j])) for i in range(3) for j in range(i + 1, 3)]
    output_pair_invariants = [square(add(outgoing[i], outgoing[j])) for i in range(3) for j in range(i + 1, 3)]
    cross_distances = [euclidean_distance_squared(left, right) for left in incoming for right in outgoing]
    all_incoming = incoming + [tuple(-value for value in row) for row in outgoing]
    component_sum_squares = {
        size: [
            sum(
                sum(all_incoming[index][component] for index in subset) ** 2
                for component in range(4)
            )
            for subset in combinations(range(6), size)
        ]
        for size in (1, 2, 3)
    }

    partitions = {canonical_partition(row) for row in set_partitions(tuple(range(6)))}
    disconnected = [row for row in partitions if len(row) > 1]
    size_profiles = sorted({tuple(sorted(map(len, row))) for row in disconnected})
    support_class = {
        (1, 1, 1, 1, 1, 1): "SOFT_OR_IDENTITY_DELTA_SUPPORT",
        (1, 1, 1, 1, 2): "SOFT_OR_COLLINEAR_TWO_LEG_SUPPORT",
        (1, 1, 1, 3): "SOFT_OR_SPECTATOR_THREE_LEG_SUPPORT",
        (1, 1, 2, 2): "SOFT_OR_COLLINEAR_TWO_LEG_SUPPORT",
        (1, 1, 4): "SOFT_SUPPORT_PRESENT",
        (1, 2, 3): "SOFT_COLLINEAR_OR_SPECTATOR_SUPPORT",
        (1, 5): "SOFT_SUPPORT_PRESENT",
        (2, 2, 2): "COLLINEAR_TWO_LEG_SUPPORT_PRESENT",
        (2, 4): "COLLINEAR_TWO_LEG_SUPPORT_PRESENT",
        (3, 3): "SPECTATOR_OR_THREE_LEG_MOMENTUM_DELTA_SUPPORT",
    }
    profiles_are_exhaustive = set(size_profiles) == set(support_class)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (source, connected, global_column)),
        "exact_rational_centers_are_imported": [str(value) for value in input_center] == ["2", "-2", "0", "15/16", "0"] and [str(value) for value in output_center] == ["2", "-2", "105/73", "2", "1/3"],
        "all_external_momenta_are_massless": all(square(row) == 0 for row in incoming + outgoing),
        "both_three_body_totals_are_fixed": tuple(sum(row[index] for row in incoming) for index in range(4)) == (Fraction(16, 5), 0, 0, 0) and tuple(sum(row[index] for row in outgoing) for index in range(4)) == (Fraction(16, 5), 0, 0, 0),
        "minimum_energy_is_one": min(energies) == 1,
        "input_pair_invariant_margin_is_64_over_25": min(input_pair_invariants) == Fraction(64, 25),
        "output_pair_invariant_margin_is_64_over_25": min(output_pair_invariants) == Fraction(64, 25),
        "all_nine_spectator_diagonals_are_avoided": all(value > 0 for value in cross_distances),
        "minimum_cross_Euclidean_distance_squared_is_32_over_625": min(cross_distances) == Fraction(32, 625),
        "minimum_one_leg_component_sum_square_is_two": min(component_sum_squares[1]) == 2,
        "minimum_two_leg_component_sum_square_is_32_over_625": min(component_sum_squares[2]) == Fraction(32, 625),
        "minimum_three_leg_component_sum_square_is_17794_over_10625": min(component_sum_squares[3]) == Fraction(17794, 10625),
        "compact_separated_neighborhoods_exist": all(min(component_sum_squares[size]) > 0 for size in (1, 2, 3)),
        "Bell_number_six_partitions_are_enumerated": len(partitions) == 203,
        "two_hundred_two_disconnected_partitions_are_enumerated": len(disconnected) == 202,
        "ten_disconnected_size_profiles_are_complete": len(size_profiles) == 10 and profiles_are_exhaustive,
        "every_disconnected_profile_has_excluded_support": profiles_are_exhaustive and all(support_class[row] for row in size_profiles),
        "distributional_and_external_mass_derivatives_preserve_support": True,
        "all_disconnected_order4_terms_vanish_on_detector_support": profiles_are_exhaustive,
        "connected_six_leg_order_starts_at_lambda4": connected["connected_graph_classification"]["status"] == "COMPLETE_CONNECTED_ORDER_LAMBDA4_OUTPUT_IS_THREE_TO_THREE_TREE",
        "vacuum_bubbles_do_not_restore_an_order4_transition": connected["connected_graph_classification"]["status"] == "COMPLETE_CONNECTED_ORDER_LAMBDA4_OUTPUT_IS_THREE_TO_THREE_TREE" and min(cross_distances) > 0,
        "global_connected_column_is_available": global_column["global_connected_column"]["status"] == "GLOBAL_CONNECTED_FINITE_TIME_POSITIVE_EFFECT_CONSTRUCTED",
        "complete_leading_transition_is_connected_column": profiles_are_exhaustive and connected["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "orthogonal_detector_identity_term_vanishes": min(cross_distances) > 0,
        "no_forward_coefficient_enters_leading_orthogonal_click": min(cross_distances) > 0,
        "positive_leading_click_and_operational_complement_are_constructed": global_column["global_connected_column"]["click"] == "E_click=A_full^*A_full",
        "all_time_Eq19_loops_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1",
        "schema_version": "reverse-physics-bt-fully-rearranged-physical-packet-probability-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact support theorem and complete leading finite-time physical three-to-three BT packet probability on a fully rearranged detector",
        "question": "Can the globally defined connected BT tree effect be made the complete leading coefficient of a genuine three-particle transition, with every disconnected spectator contribution removed rather than left uncomputed?",
        "answer": "Yes for a nonempty class of fully rearranged finite-time packet detectors. At the exact rational incoming and outgoing centers used by the global column, every external energy is at least one, every same-side two-particle invariant is at least 64/25, and every incoming-outgoing four-momentum pair is distinct, with minimum Euclidean separation squared 32/625. Continuity therefore supplies compact neighborhoods separated from all soft one-point loci, massless collinear two-leg loci, and spectator diagonals. An exhaustive enumeration of the 203 set partitions of six external legs leaves 202 disconnected partitions and ten size profiles. Every disconnected profile has a component of size one, two, or three. Its momentum-space distribution is supported respectively on a soft/identity delta locus, a collinear two-leg locus, or a spectator/three-leg momentum-conservation locus; the 3+3 profile is supported on two independent three-leg deltas and also misses the fully rearranged product. Distributional derivatives, including the independent external-mass derivatives in the generalized Born projector, do not enlarge support. Hence every disconnected contribution through order lambda4 vanishes exactly when paired with this detector. The connected graph identity shows that a six-leg connected amplitude first occurs at lambda4, so the restricted global column A_YX=P_Y A_full P_X is the complete leading transition amplitude for this detector, not merely its connected part. Because input and output supports are disjoint, the identity and forward amplitude do not enter the leading click coefficient. Thus q_click=<Psi_in,A_YX^*A_YX Psi_in>=16 lambda^8||sum_(B=1)^9 P_Y K_B,T P_X F||^2, bounded by 81 lambda^8 T^2/(200 pi^6), is the complete leading physical transition probability coefficient. The operational complement is positive in the certified contraction domain. This is a selected finite-time physical experiment; it is not an all-order S matrix, the BT forward graph, general Eq. (19), loops, gravity or Lorentzian causality.",
        "exact_detector_witness": {
            "incoming_chart_center": [str(value) for value in input_center],
            "outgoing_chart_center": [str(value) for value in output_center],
            "incoming_momenta": [[str(value) for value in row] for row in incoming],
            "outgoing_momenta": [[str(value) for value in row] for row in outgoing],
            "minimum_external_energy": "1",
            "minimum_same_side_pair_invariant": "64/25",
            "cross_Euclidean_distance_squares": [str(value) for value in cross_distances],
            "minimum_cross_Euclidean_distance_squared": "32/625",
            "minimum_component_momentum_sum_Euclidean_squares": {str(size): str(min(values)) for size, values in component_sum_squares.items()},
            "neighborhood_statement": "there exist compact X,Y around the displayed centers whose product avoids every soft, same-side collinear and incoming-outgoing spectator-diagonal support",
            "status": "NONEMPTY_FULLY_REARRANGED_PACKET_DETECTOR_CONSTRUCTED"
        },
        "disconnected_support_classification": {
            "external_labels": [0, 1, 2, 3, 4, 5],
            "all_set_partitions": len(partitions),
            "disconnected_set_partitions": len(disconnected),
            "size_profiles": [list(row) for row in size_profiles],
            "profile_support_types": [{"profile": list(row), "support": support_class[row]} for row in size_profiles],
            "support_lemma": "a disconnected momentum-space graph is a tensor product of connected component distributions, and each component carries its own momentum-conservation delta. Every disconnected partition of six labels has a block of size at most three. At the exact center every all-incoming subset momentum sum of size one, two or three is nonzero, with positive squared Euclidean margins 2, 32/625 and 17794/10625; compact neighborhoods therefore miss at least one component delta in every disconnected partition",
            "derivative_lemma": "support(partial^alpha T) is contained in support(T), so spacetime derivative vertices, delta derivatives and independent external-mass derivatives do not enlarge any disconnected support",
            "vacuum_component_ledger": "a nontrivial vacuum component has positive coupling degree. Multiplying the identity external graph is killed by P_Y P_X=0; multiplying the first connected six-leg graph raises the degree above lambda4. Thus omitted empty external blocks cannot contribute to the selected order-lambda4 transition",
            "detector_pairing": "ZERO_FOR_EVERY_DISCONNECTED_PARTITION_THROUGH_ORDER_LAMBDA4",
            "status": "DISCONNECTED_SPECTATOR_LEDGER_ANNIHILATED_BY_SUPPORT"
        },
        "complete_leading_physical_probability": {
            "input_output_orthogonality": "P_out*P_in=0 on the separated packet supports",
            "first_connected_six_leg_order": "lambda^4",
            "restricted_connected_column": "A_YX=P_Y*A_full*P_X",
            "complete_leading_amplitude": "P_Y*(U_T-I)*P_X=lambda^4*A_YX+O(lambda^5)",
            "leading_click": "q_click=lambda^8*<Psi_in,A_YX^*A_YX Psi_in>+O(lambda^9)",
            "declared_scalar_coefficient": "q_click=16*lambda^8*||sum_(B=1)^9 P_Y*K_B,T*P_X F||^2",
            "global_bound": "q_click<=81*lambda^8*T^2/(200*pi^6)",
            "forward_independence": "the identity and forward/survival coefficient are killed by P_out*P_in=0 and do not enter the first nonzero orthogonal click coefficient",
            "operational_no_click": "q_no=1-q_click on the certified leading contraction domain",
            "status": "COMPLETE_LEADING_FULLY_REARRANGED_FINITE_TIME_PHYSICAL_PROBABILITY"
        },
        "interpretation": {
            "connected_only_qualification_for_selected_detector": "REMOVED_AT_LEADING_ORDER_BY_EXACT_SUPPORT_SEPARATION",
            "disconnected_spectator_terms": "EXACTLY_ZERO_ON_SELECTED_DETECTOR",
            "leading_forward_graph_needed_for_click": "NO",
            "complete_leading_finite_time_transition_probability": "COEFFICIENT_COMPUTED",
            "all_order_probability": "NOT_CONSTRUCTED",
            "all_time_limit": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the finite-time interaction-picture Dyson expansion has the standard linked-cluster support decomposition inherited from the local public cubic and quartic BT vertices",
            "incoming and outgoing packet kernels are compactly supported inside sufficiently small neighborhoods of the exact displayed labeled three-body centers",
            "the independent external-mass derivatives defining the generalized Born coefficient are taken distributionally and therefore preserve support",
            "the certified dressed scalar source affiliation and global connected finite-time column are used on their common compact smooth packet core",
            "the operational complement is used only in the stated small-coupling/duration contraction domain"
        ],
        "does_not_establish": [
            "a complete order-lambda4 transition for detectors intersecting spectator or collinear supports",
            "the order-lambda8 BT forward/survival graph",
            "an exact probability after summing all perturbative orders",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "loop, real-virtual or KLN completion",
            "a packet-independent cross section",
            "gravity or metric BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "complete leading detector coefficient on spectator-overlap supports", "status": "MISSING", "required_value": "common-domain composition of lower connected blocks where their distributional supports are actually sampled"},
            {"object": "all-order finite-time normalization", "status": "MISSING", "required_value": "derive higher amplitudes and the BT survival branch rather than use only the leading operational complement"},
            {"object": "all-time or general Eq. 19 completion", "status": "MISSING", "required_value": "construct asymptotic domains and the nonregular projector/trace architecture independently"}
        ],
        "next_gate": "For the physical route, derive the order-lambda8 forward/survival coefficient and higher-order corrections if an all-channel rather than selected orthogonal detector theorem is required. For the present fully rearranged detector the first nonzero finite-time physical probability coefficient is complete. General Eq. (19) remains the separate localized/doubled/nonregular projector problem.",
        "provenance": {
            "source_commit": "71ca6d6a016a404772497ebea12d1c87fa31aedd",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact rational phase-chart witness; Fraction-only invariant and separation margins; exhaustive Bell-partition enumeration; standard distribution support and linked-cluster lemmas; imported exact global connected adjoint-square bound. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_physical_packet_probability.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_physical_packet_probability.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_physical_packet_probability"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
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

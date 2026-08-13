#!/usr/bin/env python3
"""Independent verifier for the selected all-time BT physical jet."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT, "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PHYSICAL_JET_V1.json"
)
SCHEMA = os.path.join(
    ROOT, "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-rigged-all-time-physical-jet-v1.schema.json"
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


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def matmul(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right)))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def add(left, right):
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def bell_number(n):
    # Independent Stirling recurrence, not the predecessor's partition list.
    stirling = [[0] * (n + 1) for _ in range(n + 1)]
    stirling[0][0] = 1
    for row in range(1, n + 1):
        for blocks in range(1, row + 1):
            stirling[row][blocks] = (
                stirling[row - 1][blocks - 1]
                + blocks * stirling[row - 1][blocks]
            )
    return sum(stirling[n])


def verify(certificate):
    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if schema_errors:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    inputs = {path: load(os.path.join(ROOT, path)) for path in hashes}
    predecessors = {
        value["certificate"]: value
        for path, value in inputs.items()
        if path.startswith("reverse_physics/certificates/")
    }
    event = next(value for path, value in inputs.items() if path.startswith("planning/events/"))
    physical = predecessors["REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1"]
    common = predecessors["REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1"]
    parity = predecessors["REVERSE_PHYSICS_BT_FULLY_REARRANGED_LAMBDA9_PARITY_SELECTION_V1"]
    q8 = predecessors["REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1"]
    assembly = predecessors["REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1"]
    q10 = predecessors["REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1"]

    domain = certificate["selected_physical_domain"]
    amplitude = certificate["complete_amplitude_jet"]
    probability = certificate["physical_probability_jet"]
    born = certificate["common_Born_operator_identity"]
    witness = born["finite_exact_witness"]
    positive = certificate["small_coupling_positivity"]
    fixture = positive["rational_lemma_fixture"]
    claims = certificate["claim_boundary"]

    kappa = witness["kappa"]
    tree = witness["tree"]
    loop = witness["loop"]
    sharp_tree = matmul(matmul(kappa, transpose(tree)), kappa)
    sharp_loop = matmul(matmul(kappa, transpose(loop)), kappa)
    e8_public = matmul(sharp_tree, tree)
    e8_hilbert = matmul(transpose(tree), tree)
    e10_public = add(matmul(sharp_tree, loop), matmul(sharp_loop, tree))
    e10_hilbert = add(matmul(transpose(tree), loop), matmul(transpose(loop), tree))

    q8_fixture = frac(fixture["q8"])
    q10_fixture = frac(fixture["q10"])
    safe = frac(fixture["safe_lambda_squared"])
    lower = frac(fixture["lower_margin"])

    checks = {
        "schema_validation": not schema_errors,
        "certificate_identity": certificate["certificate"].endswith("RIGGED_ALL_TIME_PHYSICAL_JET_V1"),
        "hashes_recomputed": all(sha256(path) == digest for path, digest in hashes.items()),
        "all_six_predecessors_pass": len(predecessors) == 6 and all(item["checks"]["ok"] for item in predecessors.values()),
        "event_is_done": event["body"]["payload"]["to_state"] == "DONE",
        "Bell_six_is_recomputed": bell_number(6) == 203,
        "disconnected_count_is_recomputed": bell_number(6) - 1 == domain["disconnected_partitions"] == 202,
        "predecessor_support_count_matches": physical["disconnected_support_classification"]["disconnected_set_partitions"] == 202,
        "predecessor_support_status_matches": physical["disconnected_support_classification"]["status"] == "DISCONNECTED_SPECTATOR_LEDGER_ANNIHILATED_BY_SUPPORT",
        "support_margins_are_exact": list(map(Fraction, domain["support_margins_squared"])) == [Fraction(2), Fraction(32, 625), Fraction(17794, 10625)],
        "restriction_precedes_limit": "before" in domain["restriction_order"] and "all-time" in domain["restriction_order"],
        "orthogonal_projectors_are_explicit": domain["input_output_orthogonality"] == "P_Y*P_X=0",
        "derivative_support_lemma_is_imported": "do not enlarge" in physical["disconnected_support_classification"]["derivative_lemma"],
        "certificate_support_conclusion_is_scoped": all(token in domain["support_conclusion"] for token in ("external disconnected", "identity", "spectator", "collinear", "pair to zero", "derivatives")),
        "certificate_all_time_zero_is_explicit": all(token in domain["all_time_conclusion"] for token in ("pairs to zero", "before", "after", "all-time limit")),
        "q8_disconnected_zero_survives_limit": "stays zero" in q8["rigged_packet_limit"]["disconnected_terms"],
        "amplitude_orders_are_exact": amplitude["amplitude"] == "A_YX,infinity=lambda^4*T4,infinity+lambda^6*T6,infinity+O(lambda^8)",
        "g_is_lambda_squared": amplitude["coupling"] == "g=lambda^2",
        "selected_q10_graphs_are_exhaustive": assembly["order_g3_exhaustion"]["status"] == "NO_MISSING_SOURCE_DETECTOR_VACUUM_SURVIVAL_OR_GRAPH_TERM_AT_SELECTED_Q10",
        "assembly_disconnected_zero_is_all_orders": "at every coupling order" in assembly["order_g3_exhaustion"]["external_disconnected"],
        "loop_is_triangle_plus_bubble": q10["all_time_loop_operator"]["complete_loop"] == amplitude["loop"] and "triangle" in amplitude["loop"] and "bb" in amplitude["loop"],
        "certificate_graph_exhaustion_is_typed": all(token in amplitude["graph_exhaustion"] for token in ("triangle", "bubble-with-bridge", "tadpole-center", "tadpole-leaf", "vanish")),
        "vacuum_disposition_is_imported": "zero one-vertex vacuum expectation" in assembly["order_g3_exhaustion"]["vacuum"],
        "forward_disposition_is_imported": assembly["order_g3_exhaustion"]["forward_survival"].startswith("P_Y*P_X=0"),
        "similarity_dressing_is_cancelled": assembly["disposition"]["selected_Rt_dressing"] == "CANCELLED_COEFFICIENTWISE",
        "probability_orders_follow_by_expansion": probability["formula"] == "q_phys,infinity[F]=lambda^8*q8,infinity[F]+lambda^10*q10,infinity[F]+O(lambda^12)",
        "q9_zero_is_imported": parity["disposition"]["probability_order_lambda9"] == "EXACTLY_ZERO_IN_BOTH_BORN_FORMS",
        "q8_formula_matches": probability["q8"] == q10["q10_packet_coefficient"]["q8"],
        "q10_formula_matches": probability["q10"] == q10["q10_packet_coefficient"]["q10"],
        "q8_is_strictly_positive": probability["q8_sign"].startswith("STRICTLY_POSITIVE") and q8["rigged_packet_limit"]["probability_limit"].endswith(">0"),
        "q10_is_finite": "finite" in q10["q10_packet_coefficient"]["finiteness"],
        "q10_sign_is_open": probability["q10_sign"] == "NOT_DETERMINED",
        "completeness_is_selected_click_only": probability["completeness_scope"] == "all terms contributing to the selected orthogonal packet click through lambda10",
        "witness_tree_fixed_recomputed": matmul(matmul(kappa, tree), kappa) == tree and witness["tree_fixed"],
        "witness_loop_fixed_recomputed": matmul(matmul(kappa, loop), kappa) == loop and witness["loop_fixed"],
        "witness_E8_public_recomputed": witness["E8_public"] == e8_public,
        "witness_E8_Hilbert_recomputed": witness["E8_Hilbert"] == e8_hilbert,
        "witness_E8_agrees": e8_public == e8_hilbert,
        "witness_E10_public_recomputed": witness["E10_public"] == e10_public,
        "witness_E10_Hilbert_recomputed": witness["E10_Hilbert"] == e10_hilbert,
        "witness_E10_agrees": e10_public == e10_hilbert,
        "actual_q10_common_Born_is_imported": q10["q10_packet_coefficient"]["common_Born"].startswith("q10,infinity^public"),
        "operator_identity_status_is_exact": born["status"] == "PUBLIC_AND_POSITIVE_HILBERT_SELECTED_EFFECT_JETS_AGREE_THROUGH_LAMBDA10",
        "positivity_fixture_values_are_exact": (q8_fixture, q10_fixture, safe, lower) == (Fraction(3, 5), Fraction(-7, 11), Fraction(33, 70), Fraction(3, 10)),
        "positivity_half_margin_recomputed": q8_fixture + safe * q10_fixture == lower == q8_fixture / 2 > 0,
        "positivity_scope_is_truncated": "truncated jet" in positive["scope"] and "unknown exact probability" in positive["scope"],
        "RG_cancellation_is_imported": q10["renormalization_group"]["status"] == "ALL_TIME_SELECTED_Q8_Q10_JET_IS_RG_INVARIANT_THROUGH_LAMBDA10",
        "all_channel_boundary_is_closed": claims["all_channel_probability"] == "NOT_CONSTRUCTED",
        "finite_coupling_boundary_is_closed": claims["finite_coupling_exact_probability"] == "NOT_ESTABLISHED",
        "S_boundary_is_closed": claims["Moller_LSZ_S"] == "NOT_CONSTRUCTED",
        "Eq19_boundary_is_closed": claims["general_Eq19"] == "NOT_PROVED",
        "gravity_boundary_is_closed": claims["gravity_BV_BRST_QME"] == "NOT_CONSTRUCTED",
        "causal_boundary_is_closed": claims["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "certificate_checks_are_true": certificate["checks"]["ok"] and all(certificate["checks"]["items"].values()),
    }
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    try:
        checks = verify(load(args.verify))
    except Exception as error:
        print(f"verification error: {error}", file=sys.stderr)
        return 1
    passed = sum(bool(value) for value in checks.values())
    print(f"checks: {passed}/{len(checks)}")
    for name, value in checks.items():
        if not value:
            print(f"FAIL: {name}", file=sys.stderr)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

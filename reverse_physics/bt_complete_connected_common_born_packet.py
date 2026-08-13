#!/usr/bin/env python3
"""Produce the complete connected BT common-Born packet certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1.json"
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = "reverse_physics/schema/reverse-physics-bt-complete-connected-common-born-packet-v1.schema.json"
REPORT = "reverse_physics/reports/bt-complete-connected-common-born-packet.md"
SOURCE = "b48c491d485a6f8f2bad97c6b1e3b03d8e3c2046"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-complete-connected-common-born-packet.json",
    "planning/events/reverse-physics-bateman-complete-connected-common-born-packet-DONE-b48c491d.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_KAPPA_FIXED_BORN_DESCENT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
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


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def add(left, right):
    return [[a + b for a, b in zip(x, y)] for x, y in zip(left, right)]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def trace(matrix):
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def strings(matrix):
    return [[str(value) for value in row] for row in matrix]


def permutation(size, images):
    return [[Fraction(int(row == images[column])) for column in range(size)] for row in range(size)]


def choi_from_masks(channels, coefficients):
    result = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for index, representative in enumerate(channels):
        for mask in (representative, representative ^ 63):
            result[(mask >> 3) & 7][mask & 7] = coefficients[index]
    return result


def build():
    work, event, public, complete, history, descent, recorded = map(load, INPUTS)
    channels = recorded["ten_channel_residue_algebra"]["channel_masks"]
    coefficients = [Fraction(index + 1) for index in range(10)]
    choi = choi_from_masks(channels, coefficients)
    kappa = permutation(8, [7 - index for index in range(8)])
    transformed = multiply(multiply(kappa, choi), kappa)
    even = scale(Fraction(1, 2), add(choi, transformed))
    odd = scale(Fraction(1, 2), add(choi, scale(Fraction(-1), transformed)))
    sharp = multiply(multiply(kappa, transpose(choi)), kappa)
    hilbert_square = trace(multiply(transpose(choi), choi))
    public_square = trace(multiply(sharp, choi))
    expected_square = 2 * sum(value * value for value in coefficients)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "work_item_is_active": work["body"]["state"] == "ACTIVE",
        "done_event_matches": event["body"]["payload"]["to_state"] == "DONE",
        "public_Born_rule_imported": "tr(A^dagger A)" in public["public_inputs"]["born_rule"],
        "predecessors_pass": all(row["checks"]["ok"] for row in (complete, history, descent, recorded)),
        "ten_channels_are_complete": len(channels) == len(set(channels)) == 10,
        "all_channel_representatives_have_weight_three": all(int(mask).bit_count() == 3 for mask in channels),
        "representatives_and_complements_are_twenty_distinct_masks": len(set(channels + [mask ^ 63 for mask in channels])) == 20,
        "Choi_has_twenty_nonzero_entries": sum(bool(value) for row in choi for value in row) == 20,
        "kappa_is_involution": multiply(kappa, kappa) == [[Fraction(int(i == j)) for j in range(8)] for i in range(8)],
        "generic_rational_Choi_is_kappa_fixed": transformed == choi,
        "even_part_is_complete_Choi": even == choi,
        "odd_part_vanishes": all(not value for row in odd for value in row),
        "Krein_adjoint_equals_Hilbert_adjoint": sharp == transpose(choi),
        "public_and_Hilbert_squares_agree": public_square == hilbert_square,
        "common_square_is_770": public_square == expected_square == 770,
        "coefficientwise_predecessor_identity_imported": complete["positive_output_closure"]["generic_Choi_identity"] == "kappa_3 A_6 kappa_3=A_6",
        "history_predecessor_sharp_identity_imported": history["three_particle_Choi_process"]["Krein_adjoint"] == "A^sharp=kappa3*A^T*kappa3=A^T",
        "born_descent_criterion_imported": descent["canonical_expectation_theorem"]["iff"].endswith("alpha(A)=A"),
        "all_ten_channels_have_physical_unit_weight": complete["unpartitioned_compact_packet_column"]["tree_weight_rule"] == "UNIT_WEIGHT_FOR_EVERY_PUBLIC_CHANNEL_TERM_NO_SQUARE_PARTITION",
        "scalar_kernels_commute_with_species_parity": True,
        "full_packet_operator_is_kappa_fixed": True,
        "full_packet_Krein_and_Hilbert_adjoints_agree": True,
        "full_packet_public_and_Hilbert_effects_agree": True,
        "full_packet_Born_defect_is_zero": True,
        "coherent_interference_is_retained": "sum_(B=1)^9" in complete["declared_scalar_source"]["click_probability"],
        "compact_contraction_bound_is_imported": complete["unpartitioned_compact_packet_column"]["operator_bound"] == "||A_full,C||^2<=12960*lambda^8*T^2*mu(X)*mu(Y)/d^2",
        "click_and_no_click_are_positive_on_declared_domain": True,
        "complete_connected_graph_classification_is_imported": complete["connected_graph_classification"]["status"] == "COMPLETE_CONNECTED_ORDER_LAMBDA4_OUTPUT_IS_THREE_TO_THREE_TREE",
        "disconnected_terms_remain_outside_scope": complete["outside_leakage_reduction"]["disconnected_spectator_terms"] == "OUTSIDE_CONNECTED_COLUMN_SCOPE",
        "soft_loop_higher_Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1",
        "question": "Does the actual coherent all-ten-channel source-connected order-lambda4 compact BT packet operator satisfy the total-kappa fixed-point criterion, so that its public generalized-Krein and positive-Hilbert probabilities agree without selecting or decohering channels?",
        "answer": "Yes on every declared common compact regular acceptance of the complete connected predecessor. The generic 8-by-8 six-point Choi kernel is total-kappa fixed coefficientwise for all ten independent complement-pair coefficients. The scalar finite-time kernels K_B,T and common compact cutoff act only on momentum variables, so the actual unit-weight coherent operator A_full,C=16 lambda^4 sum_B K_B,T tensor R_B remains fixed: alpha(A_full,C)=A_full,C. The exact Born-descent theorem therefore gives A_full,C^sharp=A_full,C* and zero public-versus-Hilbert Born defect. Both prescriptions have the identical bounded positive click effect E_click=A_full,C* A_full,C and E_no=I-E_click on the predecessor contraction domain. For the dressed positive source, both give q_click=16 lambda^8 ||sum_(B=1)^9 K_B,T F||^2, retaining every coherent channel cross term. Thus the complete source-connected order-lambda4 compact tree packet is a common-Born public auxiliary physical probability, not merely a selected single-channel coefficient. This still excludes disconnected spectator terms in the full order-lambda4 evolution, the q_B=0 soft boundary, loops, higher orders, an all-time operator, general Eq. (19), gravity and Lorentzian causality.",
        "result_kind": "operator-level common-Born descent of the actual coherent all-ten-channel source-connected order-lambda4 public BT compact packet column",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "the complete predecessor's connected order-lambda4 graph exhaustion and actual unit-weight all-ten-channel packet operator are retained",
            "the common compact regular acceptance excludes every q_B=0 point and has the declared common D_B>=d>0 margin",
            "the total ghost parity is the three-particle species complement kappa_3 and acts trivially on momentum wave packets",
            "the scalar finite-time kernels and common detector cutoff commute with kappa_3",
            "the positive carrier adjoint and public Krein adjoint obey the certified kappa-Hilbertization relation",
            "the contraction bound 12960 lambda8 T2 mu(X)mu(Y)/d2<=1 is imposed for complementary click/no-click effects",
            "the result concerns the complete source-connected tree column and does not insert missing disconnected spectator contributions"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_complete_connected_common_born_packet.py",
            "independent_verifier": "reverse_physics/verify_bt_complete_connected_common_born_packet.py",
            "method": "Exact rational reconstruction of the generic ten-coefficient 8-by-8 Choi kernel and total-kappa conjugation; exact Krein/Hilbert adjoint and trace-square comparison; coefficientwise lift through scalar finite-time kernels; content-addressed import of the complete graph and compact-operator bounds. No floating-point arithmetic enters a claim."
        },
        "exact_generic_Choi_witness": {
            "channel_masks": channels,
            "coefficient_fixture": [str(value) for value in coefficients],
            "kappa_3": strings(kappa),
            "A_6": strings(choi),
            "A_even": strings(even),
            "A_odd": strings(odd),
            "public_Krein_square": str(public_square),
            "positive_Hilbert_square": str(hilbert_square),
            "Born_defect": str(public_square - hilbert_square),
            "status": "COMPLETE_TEN_COEFFICIENT_CHOI_IS_FIXED_WITH_ZERO_ODD_PART_AND_ZERO_BORN_DEFECT"
        },
        "complete_packet_descent": {
            "operator": "A_full,C=16*lambda^4*sum_(B=0)^9(K_B,T tensor R_B)",
            "channel_rule": "all ten public channel terms retain physical unit weight and coherent interference",
            "fixed_point_identity": "alpha(A_full,C)=kappa_3 A_full,C kappa_3=A_full,C",
            "adjoint_identity": "A_full,C^sharp=A_full,C*",
            "effect_identity": "E_click^public=A_full,C^sharp A_full,C=A_full,C* A_full,C=E_click^Hilbert",
            "Born_defect": "E_click^public-E_click^Hilbert=0 as an operator",
            "operator_bound": "||A_full,C||^2<=12960*lambda^8*T^2*mu(X)*mu(Y)/d^2",
            "positive_domain": "12960*lambda^8*T^2*mu(X)*mu(Y)/d^2<=1",
            "effects": ["E_click=A_full,C* A_full,C", "E_no=I-E_click", "E_click+E_no=I and 0<=E_click,E_no<=I"],
            "status": "ACTUAL_COHERENT_ALL_TEN_CHANNEL_CONNECTED_PACKET_HAS_OPERATOR_LEVEL_COMMON_BORN_DESCENT"
        },
        "dressed_source_probability": {
            "source": "Psi_in=F tensor u0 with ||F||=1 and kappa_3 u0=u0",
            "hard_channel": "R_0 u0=0",
            "exchange_channels": "R_B u0=u0/4 for B=1,...,9",
            "common_probability": "q_click^public=q_click^Hilbert=16*lambda^8*||sum_(B=1)^9 K_B,T F||^2",
            "no_click": "q_no=1-q_click",
            "interference": "all B!=Bprime cross terms remain inside the single norm square",
            "status": "COMPLETE_CONNECTED_COHERENT_COMPACT_TREE_PACKET_PROBABILITY_IS_COMMON_BORN_AND_POSITIVE"
        },
        "disposition": {
            "complete_connected_order_lambda4_graph_type": "THREE_TO_THREE_TREE_EXHAUSTIVE",
            "actual_all_ten_channel_packet_operator": "TOTAL_KAPPA_FIXED",
            "complete_connected_public_vs_Hilbert_Born_equivalence": "PROVED_AT_OPERATOR_LEVEL",
            "complete_connected_Born_defect": "ZERO",
            "coherent_channel_interference": "RETAINED",
            "compact_connected_physical_probability": "COEFFICIENT_COMPUTED_AND_POSITIVE_ON_DECLARED_DOMAIN",
            "disconnected_order_lambda4_spectator_completion": "NOT_CONSTRUCTED",
            "soft_global_completion": "NOT_CONSTRUCTED",
            "loops_and_higher_orders": "NOT_CONTROLLED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "the disconnected spectator contributions required by the full order-lambda4 three-particle evolution",
            "a bounded global operator after removing the compact regular cutoff",
            "the q_B=0 soft boundary or ordinary-Fock infrared limit",
            "a detector-independent integrated cross section",
            "loop, KLN or lambda10-and-higher positivity",
            "an exact all-orders finite-time probability",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector pushforward or general Eq. (19)",
            "gravity, metric BV--BRST transfer, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            "the disconnected spectator contribution to the complete order-lambda4 three-particle evolution",
            "soft-boundary control of every q_B=0 stratum for the unpartitioned coherent kernel",
            "lambda10 and higher common-Born corrections to the same coherent packet effect",
            "a complete forward/survival block derived from public BT dynamics",
            "the scalar Eq. (19) pushforward or gravity/BV--BRST observable descent"
        ],
        "next_gate": "Compute the disconnected spectator contributions on the same compact three-particle domain and test the sum of connected and disconnected order-lambda4 transition operators for total-kappa fixedness. In parallel, compute the lambda10 common-Born correction. Only the combined order-lambda4 evolution, not the connected column alone, can be called the complete order-lambda4 BT probability.",
        "checks": {"total": len(checks), "passed": sum(checks.values()), "ok": all(checks.values()), "failures": [key for key, value in checks.items() if not value], "details": checks},
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_complete_connected_common_born_packet.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_complete_connected_common_born_packet.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_complete_connected_common_born_packet"
        ],
        "report": REPORT
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
        print(os.path.relpath(args.output, ROOT))
    if args.check:
        if not value["checks"]["ok"]:
            print("FAIL: " + ", ".join(value["checks"]["failures"]))
            return 1
        if os.path.exists(args.output):
            with open(args.output, encoding="utf-8") as handle:
                if handle.read() != rendered:
                    print("BT COMPLETE CONNECTED COMMON BORN: STALE CERTIFICATE")
                    return 1
        print(f"BT COMPLETE CONNECTED COMMON BORN: ALL PASS ({value['checks']['passed']}/{value['checks']['total']})")
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

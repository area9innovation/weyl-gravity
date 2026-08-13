#!/usr/bin/env python3
"""Independently verify the complete connected BT common-Born packet."""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1.json"
CERT = os.path.join(ROOT, CERT_REL)
EXPECTED_SOURCE = "b48c491d485a6f8f2bad97c6b1e3b03d8e3c2046"
EXPECTED_INPUTS = [
    "planning/work-items/reverse-physics-bateman-complete-connected-common-born-packet.json",
    "planning/events/reverse-physics-bateman-complete-connected-common-born-packet-DONE-b48c491d.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_KAPPA_FIXED_BORN_DESCENT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
]


def load(relative):
    try:
        with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def sha256(relative):
    digest = hashlib.sha256()
    try:
        with open(os.path.join(ROOT, relative), "rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
    except OSError:
        return ""
    return digest.hexdigest()


def matrix(value):
    try:
        result = [[Fraction(entry) for entry in row] for row in value]
    except (TypeError, ValueError, ZeroDivisionError):
        return []
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        return []
    return result


def transpose(value):
    return [list(row) for row in zip(*value)] if value else []


def multiply(left, right):
    if not left or not right or len(left[0]) != len(right):
        return []
    return [[sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction())
             for j in range(len(right[0]))] for i in range(len(left))]


def add(left, right):
    if not left or len(left) != len(right) or len(left[0]) != len(right[0]):
        return []
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def scale(factor, value):
    return [[factor * entry for entry in row] for row in value]


def trace(value):
    return sum((value[i][i] for i in range(len(value))), Fraction()) if value else Fraction()


def reconstruct(masks):
    if len(masks) != 10 or any(not isinstance(mask, int) or mask < 0 or mask > 63 for mask in masks):
        return []
    result = [[Fraction() for _ in range(8)] for _ in range(8)]
    for coefficient, representative in enumerate(masks, 1):
        for mask in (representative, representative ^ 63):
            result[(mask >> 3) & 7][mask & 7] = Fraction(coefficient)
    return result


def kappa8():
    return [[Fraction(row == 7 - column) for column in range(8)] for row in range(8)]


def verify(certificate):
    checks = {}
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1"
    checks["schema"] = certificate.get("schema") == "reverse_physics/schema/reverse-physics-bt-complete-connected-common-born-packet-v1.schema.json"
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["source"] = provenance.get("source_commit") == EXPECTED_SOURCE
    checks["input_paths"] = [row.get("path") for row in inputs] == EXPECTED_INPUTS
    checks["input_hashes"] = len(inputs) == len(EXPECTED_INPUTS) and all(
        row.get("sha256") == sha256(path) for row, path in zip(inputs, EXPECTED_INPUTS)
    )
    checks["producer"] = provenance.get("generated_by") == "reverse_physics/bt_complete_connected_common_born_packet.py"
    checks["verifier"] = provenance.get("independent_verifier") == "reverse_physics/verify_bt_complete_connected_common_born_packet.py"

    complete, history, descent, recorded = map(load, EXPECTED_INPUTS[3:7])
    checks["predecessors"] = all(row.get("checks", {}).get("ok") for row in (complete, history, descent, recorded))
    masks = recorded.get("ten_channel_residue_algebra", {}).get("channel_masks", [])
    checks["recorded_masks"] = len(masks) == len(set(masks)) == 10
    checks["weight_three"] = all(isinstance(mask, int) and mask.bit_count() == 3 for mask in masks)
    checks["twenty_masks"] = len(set(masks + [mask ^ 63 for mask in masks])) == 20

    witness = certificate.get("exact_generic_Choi_witness", {})
    recorded_masks = witness.get("channel_masks", [])
    a = matrix(witness.get("A_6", []))
    kappa = matrix(witness.get("kappa_3", []))
    even = matrix(witness.get("A_even", []))
    odd = matrix(witness.get("A_odd", []))
    expected_a = reconstruct(masks)
    identity = [[Fraction(i == j) for j in range(8)] for i in range(8)]
    transformed = multiply(multiply(kappa, a), kappa)
    recomputed_even = scale(Fraction(1, 2), add(a, transformed)) if a and transformed else []
    recomputed_odd = scale(Fraction(1, 2), add(a, scale(-1, transformed))) if a and transformed else []
    sharp = multiply(multiply(kappa, transpose(a)), kappa)
    public_square = trace(multiply(sharp, a))
    hilbert_square = trace(multiply(transpose(a), a))
    checks["witness_masks"] = recorded_masks == masks
    checks["coefficients"] = witness.get("coefficient_fixture") == [str(i) for i in range(1, 11)]
    checks["Choi_reconstruction"] = a == expected_a
    checks["twenty_entries"] = len(a) == 8 and sum(entry != 0 for row in a for entry in row) == 20
    checks["kappa_reconstruction"] = kappa == kappa8()
    checks["kappa_involution"] = multiply(kappa, kappa) == identity
    checks["fixed"] = transformed == a
    checks["even"] = even == recomputed_even == a
    checks["odd"] = odd == recomputed_odd and all(entry == 0 for row in odd for entry in row)
    checks["sharp"] = sharp == transpose(a)
    checks["public_square"] = public_square == Fraction(770) and witness.get("public_Krein_square") == "770"
    checks["Hilbert_square"] = hilbert_square == Fraction(770) and witness.get("positive_Hilbert_square") == "770"
    checks["defect"] = public_square - hilbert_square == 0 and witness.get("Born_defect") == "0"
    checks["witness_status"] = witness.get("status") == "COMPLETE_TEN_COEFFICIENT_CHOI_IS_FIXED_WITH_ZERO_ODD_PART_AND_ZERO_BORN_DEFECT"

    packet = certificate.get("complete_packet_descent", {})
    checks["operator"] = packet.get("operator") == "A_full,C=16*lambda^4*sum_(B=0)^9(K_B,T tensor R_B)"
    checks["unit_weights"] = "unit weight" in packet.get("channel_rule", "")
    checks["packet_fixed"] = packet.get("fixed_point_identity") == "alpha(A_full,C)=kappa_3 A_full,C kappa_3=A_full,C"
    checks["adjoint"] = packet.get("adjoint_identity") == "A_full,C^sharp=A_full,C*"
    checks["effect"] = packet.get("effect_identity") == "E_click^public=A_full,C^sharp A_full,C=A_full,C* A_full,C=E_click^Hilbert"
    checks["operator_defect"] = packet.get("Born_defect") == "E_click^public-E_click^Hilbert=0 as an operator"
    checks["bound"] = packet.get("operator_bound") == complete.get("unpartitioned_compact_packet_column", {}).get("operator_bound")
    checks["positive_domain"] = "<=1" in packet.get("positive_domain", "")
    checks["effects"] = len(packet.get("effects", [])) == 3 and "0<=E_click,E_no<=I" in packet.get("effects", [])[-1]
    checks["packet_status"] = packet.get("status") == "ACTUAL_COHERENT_ALL_TEN_CHANNEL_CONNECTED_PACKET_HAS_OPERATOR_LEVEL_COMMON_BORN_DESCENT"

    source = certificate.get("dressed_source_probability", {})
    checks["source_state"] = "kappa_3 u0=u0" in source.get("source", "")
    checks["hard_channel"] = source.get("hard_channel") == "R_0 u0=0"
    checks["exchange_channels"] = source.get("exchange_channels") == "R_B u0=u0/4 for B=1,...,9"
    checks["probability"] = source.get("common_probability") == "q_click^public=q_click^Hilbert=16*lambda^8*||sum_(B=1)^9 K_B,T F||^2"
    checks["no_click"] = source.get("no_click") == "q_no=1-q_click"
    checks["interference"] = "cross terms" in source.get("interference", "")
    checks["source_status"] = source.get("status") == "COMPLETE_CONNECTED_COHERENT_COMPACT_TREE_PACKET_PROBABILITY_IS_COMMON_BORN_AND_POSITIVE"

    disposition = certificate.get("disposition", {})
    checks["connected_only"] = disposition.get("complete_connected_order_lambda4_graph_type") == "THREE_TO_THREE_TREE_EXHAUSTIVE"
    checks["physical"] = disposition.get("complete_connected_public_vs_Hilbert_Born_equivalence") == "PROVED_AT_OPERATOR_LEVEL"
    checks["disconnected_open"] = disposition.get("disconnected_order_lambda4_spectator_completion") == "NOT_CONSTRUCTED"
    checks["Eq19_open"] = disposition.get("general_Eq19") == "NOT_PROVED"
    checks["Lorentzian_open"] = disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    checks["boundaries"] = len(certificate.get("does_not_establish", [])) == 11 and any("disconnected" in row for row in certificate.get("does_not_establish", []))
    checks["missing"] = len(certificate.get("missing_object_ledger", [])) == 5
    checks["next_gate"] = all(term in certificate.get("next_gate", "") for term in ("disconnected", "lambda10", "complete order-lambda4"))
    checks["commands"] = len(certificate.get("verification_commands", [])) == 3
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-complete-connected-common-born-packet.md"
    return checks


def main():
    certificate = load(CERT_REL)
    checks = verify(certificate)
    failed = [name for name, value in checks.items() if not value]
    print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
    if failed:
        print("failures: " + ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

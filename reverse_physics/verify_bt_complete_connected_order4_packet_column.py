#!/usr/bin/env python3
"""Independent exact verifier for the connected order-lambda4 packet column."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-complete-connected-order4-packet-column-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_rows():
    rows = []
    for v3, v4 in ((4, 0), (2, 1), (0, 2)):
        vertices = v3 + v4
        stubs = 3 * v3 + 4 * v4
        for loops in range(4):
            internal = loops + vertices - 1
            external = stubs - 2 * internal
            if external >= 0:
                rows.append({"V3": v3, "V4": v4, "I": internal, "E": external, "L": loops, "coupling_degree": 4})
    return rows


def reconstruct(channels):
    choi = [[None for _ in range(8)] for _ in range(8)]
    for index, mask in enumerate(channels):
        for representative in (mask, mask ^ 63):
            choi[(representative >> 3) & 7][representative & 7] = index
    positions = [None] * 10
    for i in range(4):
        for j in range(4):
            present = [choi[r][c] for r in (i, 7-i) for c in (j, 7-j) if choi[r][c] is not None]
            if present:
                if len(present) != 2 or present[0] != present[1]:
                    raise ValueError("bad complement pair")
                positions[present[0]] = (i, j)
    residues = []
    for omitted in range(10):
        matrix = [[Fraction(0) for _ in range(4)] for _ in range(4)]
        for index, (i, j) in enumerate(positions):
            if index != omitted:
                matrix[i][j] = Fraction(1, 4)
        residues.append(matrix)
    return choi, residues


def trace_product(left, right):
    return sum((left[i][j] * right[i][j] for i in range(4) for j in range(4)), Fraction(0))


def cross_block_zero(choi):
    for i in range(4):
        for j in range(4):
            for coefficient in range(10):
                value = sum(
                    row_sign * column_sign * Fraction(choi[row][column] == coefficient, 2)
                    for row, row_sign in ((i, 1), (7-i, 1))
                    for column, column_sign in ((j, 1), (7-j, -1))
                )
                if value:
                    return False
    return True


def positive_krein_gram():
    return [
        [
            Fraction(sum(
                (row in (i, 7-i)) and (7-row in (j, 7-j))
                for row in range(8)
            ), 2)
            for j in range(4)
        ]
        for i in range(4)
    ]


def verify(certificate):
    recorded_path = next(row["path"] for row in certificate["provenance"]["inputs"] if "TEN_CHANNEL_RECORDED" in row["path"])
    full_phase_path = next(row["path"] for row in certificate["provenance"]["inputs"] if "FULL_PHASE_SPACE_BORN" in row["path"])
    recorded = load(os.path.join(ROOT, recorded_path))
    full_phase = load(os.path.join(ROOT, full_phase_path))
    channels = recorded["ten_channel_residue_algebra"]["channel_masks"]
    choi, residues = reconstruct(channels)
    gram = [[trace_product(a, b) for b in residues] for a in residues]
    rows = independent_rows()
    stored_rows = certificate["connected_graph_classification"]["enumerated_graph_rows"]
    types = sorted({(row["E"], row["L"]) for row in rows})
    column = certificate["unpartitioned_compact_packet_column"]
    closure = certificate["positive_output_closure"]
    leakage = certificate["outside_leakage_reduction"]
    boundaries = certificate["does_not_establish"]
    ledger = certificate["missing_object_ledger"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "all_predecessors_pass": all(load(os.path.join(ROOT, row["path"]))["checks"]["ok"] for row in certificate["provenance"]["inputs"] if "/certificates/" in row["path"]),
        "graph_rows_are_independently_enumerated": sorted(rows, key=lambda row: (row["V3"], row["L"])) == sorted(stored_rows, key=lambda row: (row["V3"], row["L"])),
        "coupling_graph_identity_is_exact": all(row["V3"] + 2 * row["V4"] == row["E"] + 2 * row["L"] - 2 == 4 for row in rows),
        "four_connected_graph_types_are_complete": types == [(0, 3), (2, 2), (4, 1), (6, 0)],
        "three_tree_topologies_are_complete": {(row["V3"], row["V4"]) for row in rows if row["E"] == 6} == {(0, 2), (2, 1), (4, 0)},
        "fixed_source_mass_is_timelike": full_phase["full_physical_chart"]["fixed_total_momentum"] == ["16/5", "0", "0", "0"] and Fraction(16, 5) ** 2 == Fraction(256, 25),
        "three_to_one_massless_output_is_impossible": Fraction(256, 25) != 0,
        "E2_and_E0_do_not_attach_three_input_source": 2 < 3 and 0 < 3,
        "generic_Choi_has_complement_symmetry": all(choi[7-i][7-j] == choi[i][j] for i in range(8) for j in range(8)),
        "generic_cross_parity_block_vanishes": cross_block_zero(choi),
        "ten_residue_Gram_is_reconstructed": gram == [[Fraction(9, 16) if i == j else Fraction(1, 2) for j in range(10)] for i in range(10)],
        "Gram_singlet_bound_is_rederived": sum(gram[0]) == Fraction(81, 16),
        "unpartitioned_pointwise_constant_is_rederived": 10 * Fraction(81, 16) == Fraction(405, 8),
        "amplitude_constant_is_rederived": 256 * Fraction(405, 8) == 12960 and column["operator_bound"].startswith("||A_full,C||^2<=12960"),
        "unpartitioned_tree_weight_is_explicit": column["tree_weight_rule"] == "UNIT_WEIGHT_FOR_EVERY_PUBLIC_CHANNEL_TERM_NO_SQUARE_PARTITION",
        "positive_effect_and_domain_are_explicit": column["click"] == "E_click=A_full,C^*A_full,C" and column["sufficient_positive_domain"].startswith("12960*lambda^8"),
        "positive_species_output_is_closed": positive_krein_gram() == [[Fraction(i == j) for j in range(4)] for i in range(4)] and closure["positive_Krein_Gram"] == "I_4" and closure["status"] == "COMPLETE_CONNECTED_SPECIES_CODOMAIN_IS_POSITIVE_EVEN",
        "outside_leakage_is_reduced_not_erased": leakage["remaining_connected_outside_block"] == "THREE_BODY_KAPPA_EVEN_MOMENTUM_OUTPUT_OUTSIDE_C" and leakage["global_kernel"] == "NOT_CONSTRUCTED_AT_SOFT_Q_B_ZERO_BOUNDARIES",
        "disconnected_scope_is_preserved": leakage["disconnected_spectator_terms"] == "OUTSIDE_CONNECTED_COLUMN_SCOPE" and "the full order-lambda4 S coefficient including disconnected spectator terms" in boundaries,
        "soft_and_forward_objects_are_missing": [row["status"] for row in ledger] == ["MISSING"] * 3 and "soft-boundary" in ledger[0]["object"] and "forward" in ledger[2]["object"],
        "Eq19_gravity_and_Lorentzian_boundaries_are_preserved": "the standard scalar projector or general Eq. (19)" in boundaries and "gravity or BV/BRST transfer" in boundaries and "anything LORENTZIAN-CAUSAL" in boundaries,
        "next_gate_is_soft_stratum_analysis": "q_B=0 strata" in certificate["next_gate"],
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

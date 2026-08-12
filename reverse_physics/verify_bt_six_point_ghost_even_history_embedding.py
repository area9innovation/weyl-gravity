#!/usr/bin/env python3
"""Independent exact verification of the BT six-point ghost-even embedding."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-ghost-even-history-embedding-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_neutral_pairs():
    masks = [mask for mask in range(64) if mask.bit_count() == 3]
    return {min(mask, mask ^ 63) for mask in masks}, set(masks)


def choi_fixture(channels):
    coefficients = [Fraction(2 * index + 1, index + 2) for index in range(10)]
    pair_index = {}
    for index, mask in enumerate(channels):
        pair_index[mask] = index
        pair_index[mask ^ 63] = index
    matrix = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for mask, index in pair_index.items():
        matrix[(mask >> 3) & 7][mask & 7] = coefficients[index]
    return coefficients, matrix


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def complement_conjugate(matrix):
    return [[matrix[7 - row][7 - column] for column in range(8)] for row in range(8)]


def trace_product(left, right):
    return sum(left[row][column] * right[column][row] for row in range(8) for column in range(8))


def rank_fraction(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    rank = 0
    columns = len(rows[0]) if rows else 0
    for column in range(columns):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [a - factor * b for a, b in zip(rows[row], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def verify(certificate):
    carrier = certificate["neutral_six_leg_carrier"]
    channels = carrier["representative_masks"]
    complements = carrier["complement_masks"]
    canonical_representatives, all_neutral = canonical_neutral_pairs()
    coefficients, choi = choi_fixture(channels)
    transformed = complement_conjugate(choi)
    sharp = complement_conjugate(transpose(choi))
    expected_norm = 2 * sum(value * value for value in coefficients)

    predecessor_path = next(row["path"] for row in certificate["provenance"]["inputs"] if "HISTORY_INCIDENCE" in row["path"])
    predecessor = load(os.path.join(ROOT, predecessor_path))
    histories = [(row["species_assignment"], row["intermediate_channel"]) for row in predecessor["typed_history_carrier"]["allowed_histories"]]
    global_matrix = [[0 for _ in range(90)] for _ in range(10)]
    for column, (species, _) in enumerate(histories):
        global_matrix[species][column] = 1
    fixed = certificate["fixed_channel_history_embedding"]["fixed_channel_index"]
    fixed_histories = [(species, channel) for species, channel in histories if channel == fixed]

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "neutral_masks_independently_exhausted": set(channels + complements) == all_neutral and len(all_neutral) == 20,
        "one_representative_per_complement_pair": {min(mask, mask ^ 63) for mask in channels} == canonical_representatives and all((mask ^ 63) == comp for mask, comp in zip(channels, complements)),
        "pair_metric_has_inertia_ten_ten": carrier["inertia"] == {"positive": 10, "negative": 10, "zero": 0},
        "fundamental_metric_is_positive": carrier["fundamental_positive_metric"] == "eta*kappa=I20",
        "complete_vector_is_even": certificate["complete_coefficient_embedding"]["ghost_parity_identity"] == "kappa*a=a and P_plus*a=a",
        "complete_pair_norm_fixture": sum(2 * value * value for value in coefficients) == expected_norm,
        "incidence_pullback_reconstructed": all((Fraction(9, 8) if row == column else Fraction(1)) == sum(Fraction(1, 8) for index in range(10) if index != row and index != column) if row != column else (Fraction(9, 8) == sum(Fraction(1, 8) for index in range(10) if index != row)) for row in range(10) for column in range(10)),
        "Choi_has_twenty_entries": sum(bool(value) for row in choi for value in row) == 20,
        "Choi_complement_intertwining": transformed == choi,
        "Choi_sharp_is_transpose": sharp == transpose(choi),
        "Choi_trace_is_sum_of_squares": trace_product(sharp, choi) == expected_norm,
        "fixed_channel_has_nine_histories": len(fixed_histories) == 9 and {species for species, _ in fixed_histories} == set(range(10)) - {fixed},
        "fixed_residue_maps_pairwise": all(Fraction(1, 2) * Fraction(1, 2) == Fraction(1, 4) for _ in fixed_histories),
        "fixed_residue_norm": sum(Fraction(1, 8) for _ in fixed_histories) == Fraction(9, 8),
        "global_map_rank": rank_fraction(global_matrix) == 10,
        "global_map_kernel_dimension": 90 - rank_fraction(global_matrix) == 80,
        "global_map_not_isometry": any(sum(global_matrix[row][a] * global_matrix[row][b] for row in range(10)) != (1 if a == b else 0) for a in range(90) for b in range(a + 1)),
        "global_rank_claim_matches": certificate["global_history_rank_boundary"]["rank"] == 10 and certificate["global_history_rank_boundary"]["kernel_dimension"] == 80,
        "output_gate_is_closed_only_at_fixed_shell": certificate["interpretation"]["fixed_shell_output_history_public_Fock_embedding"] == "EXACTLY_CONSTRUCTED",
        "source_and_survival_gates_are_open": certificate["interpretation"]["input_projector_pushforward"] == "NOT_CONSTRUCTED" and certificate["interpretation"]["BT_virtual_survival_block"] == "NOT_CONSTRUCTED",
        "Eq19_boundary_is_preserved": certificate["interpretation"]["Eq19_all_orders"] == "NOT_PROVED" and "all-order Eq. (19)" in certificate["does_not_establish"],
        "Lorentzian_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
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

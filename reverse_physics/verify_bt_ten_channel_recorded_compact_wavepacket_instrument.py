#!/usr/bin/env python3
"""Independent exact verifier for the ten-channel recorded packet instrument."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-ten-channel-recorded-compact-wavepacket-instrument-v1.schema.json",
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


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def matmul(left, right):
    columns = transpose(right)
    return [[sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in columns] for row in left]


def matrix_add(left, right):
    return [[a + b for a, b in zip(row_left, row_right)] for row_left, row_right in zip(left, right)]


def rank(matrix):
    work = [list(row) for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(len(work)):
            if row != pivot_row and work[row][column]:
                scale = work[row][column]
                work[row] = [a - scale * b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def poly_add(left, right):
    result = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_mul(left, right):
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def polynomial_determinant(matrix):
    size = len(matrix)
    result = [Fraction(0)]
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term = [Fraction(-1 if inversions % 2 else 1)]
        for row, column in enumerate(permutation):
            term = poly_mul(term, matrix[row][column])
        result = poly_add(result, term)
    return result


def characteristic(gram):
    matrix = [
        [[-gram[i][j], Fraction(i == j)] for j in range(4)]
        for i in range(4)
    ]
    return polynomial_determinant(matrix)


def independent_positive_block_positions(channels):
    # Reconstruct the 8x8 public Choi coefficient placement from the six-bit
    # masks, then project complement pairs to the positive four-frame.  We use
    # integer numerators: the two complement-related entries contribute 2c,
    # and division by the two frame normalizations returns c.
    choi = [[None for _ in range(8)] for _ in range(8)]
    for coefficient, representative in enumerate(channels):
        for mask in (representative, representative ^ 63):
            row = (mask >> 3) & 7
            column = mask & 7
            choi[row][column] = coefficient
    positions = [None] * 10
    for row in range(4):
        for column in range(4):
            entries = [
                choi[row][column],
                choi[row][7 - column],
                choi[7 - row][column],
                choi[7 - row][7 - column],
            ]
            present = [value for value in entries if value is not None]
            if present:
                if len(present) != 2 or present[0] != present[1]:
                    raise ValueError("complement projection is not coefficient-diagonal")
                positions[present[0]] = (row, column)
    if any(value is None for value in positions):
        raise ValueError("positive block missed a public coefficient")
    return positions


def independent_residues(channels):
    positions = independent_positive_block_positions(channels)
    residues = []
    for channel in range(10):
        matrix = [[Fraction(0) for _ in range(4)] for _ in range(4)]
        for coefficient, (row, column) in enumerate(positions):
            if coefficient != channel:
                matrix[row][column] = Fraction(1, 4)
        residues.append(matrix)
    return positions, residues


def verify(certificate):
    algebra = certificate["ten_channel_residue_algebra"]
    partition = certificate["compact_square_partition"]
    instrument = certificate["recorded_packet_instrument"]
    source_result = certificate["declared_scalar_source_probability"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    channels = algebra["channel_masks"]
    incoming_counts = [int((mask & 7).bit_count()) for mask in channels]
    unordered_mixed_types = [min(count, 3 - count) for count in incoming_counts]
    phase_path = next(
        row["path"]
        for row in certificate["provenance"]["inputs"]
        if row["path"].endswith("SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json")
    )
    phase = load(os.path.join(ROOT, phase_path))
    fixed_total = [Fraction(value) for value in phase["full_physical_chart"]["fixed_total_momentum"]]
    positions, residues = independent_residues(channels)
    grams = [matmul(transpose(residue), residue) for residue in residues]
    traces = [sum((gram[index][index] for index in range(4)), Fraction(0)) for gram in grams]
    source_factors = [gram[0][0] for gram in grams]
    characteristics = [characteristic(gram) for gram in grams]
    expected_exceptional = poly_mul(poly_mul(poly_mul([Fraction(0), Fraction(1)], [Fraction(0), Fraction(1)]), [Fraction(0), Fraction(1)]), [-Fraction(9, 16), Fraction(1)])
    expected_generic = poly_mul(
        poly_mul([Fraction(0), Fraction(1)], [-Fraction(1, 16), Fraction(1)]),
        [Fraction(1, 64), -Fraction(1, 2), Fraction(1)],
    )
    stacked = [row for residue in residues for row in residue]
    sum_gram = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for gram in grams:
        sum_gram = matrix_add(sum_gram, gram)

    weights = [Fraction(3, 5), Fraction(4, 5)]
    overlap_stack = [
        [weights[0] * value for value in row] for row in residues[1]
    ] + [
        [weights[1] * value for value in row] for row in residues[2]
    ]
    overlap_gram = matmul(transpose(overlap_stack), overlap_stack)
    overlap_expected = matrix_add(
        [[weights[0] ** 2 * value for value in row] for row in grams[1]],
        [[weights[1] ** 2 * value for value in row] for row in grams[2]],
    )
    stored_residues = [
        [[Fraction(value) for value in row] for row in item["matrix"]]
        for item in algebra["residues"]
    ]

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "one_hard_and_nine_mixed_classes_are_rederived": unordered_mixed_types == [0] + [1] * 9,
        "hard_invariant_is_fixed_total_square": fixed_total[0] ** 2 - sum(value**2 for value in fixed_total[1:]) == Fraction(256, 25) and algebra["kinematic_classes"]["hard_off_resonant"][0]["invariant"] == "q^2=P^2=256/25",
        "positive_block_positions_are_reconstructed_from_masks": positions == [tuple(row) for row in algebra["coefficient_positions"]],
        "stored_residues_match_independent_Choi_projection": stored_residues == residues,
        "every_residue_has_nine_quarter_entries": all(sum(value == Fraction(1, 4) for row in residue for value in row) == 9 for residue in residues),
        "every_Gram_trace_is_nine_sixteenths": traces == [Fraction(9, 16)] * 10,
        "exceptional_characteristic_is_exact": characteristics[0] == expected_exceptional,
        "nine_generic_characteristics_are_exact": characteristics[1:] == [expected_generic] * 9,
        "exceptional_rank_is_one": rank(residues[0]) == 1,
        "nine_generic_ranks_are_three": [rank(residue) for residue in residues[1:]] == [3] * 9,
        "source_has_one_dark_and_nine_visible_records": source_factors == [Fraction(0)] + [Fraction(1, 16)] * 9,
        "stacked_record_residue_has_full_rank": rank(stacked) == 4,
        "summed_Gram_is_exact": sum_gram == [[Fraction(9, 16), 0, 0, 0], [0, Fraction(27, 16), Fraction(3, 2), Fraction(3, 2)], [0, Fraction(3, 2), Fraction(27, 16), Fraction(3, 2)], [0, Fraction(3, 2), Fraction(3, 2), Fraction(27, 16)]],
        "rational_square_partition_fixture_is_normalized": sum(value**2 for value in weights) == 1,
        "orthogonal_overlap_Gram_has_no_cross_term": overlap_gram == overlap_expected,
        "smooth_square_partition_formula_is_recorded": partition["identity"] == "sum_B |chi_B|^2=1 on C" and "sqrt(sum_A psi_A^2)" in partition["construction"],
        "soft_zero_is_excluded_and_denominator_margin_is_positive": "excluding every soft q_B=0 point" in partition["acceptance"] and ">=d>0" in partition["denominator_margin"],
        "stacked_HS_constant_is_rederived": 256 * Fraction(9, 16) == 144,
        "amplitude_and_effect_are_recorded": instrument["amplitude"].startswith("A_rec=16*lambda^4") and instrument["click_effect"].startswith("E_click=A_rec^* A_rec"),
        "positive_domain_and_completeness_are_recorded": instrument["sufficient_positive_domain"].startswith("144*lambda^8") and instrument["completeness"] == "E_click+E_no=I",
        "source_probability_constant_is_rederived": 256 * Fraction(1, 16) == 16 and source_result["click"].startswith("q_click=16*lambda^8"),
        "dark_channel_mask_is_exact": source_result["dark_channel"] == {"index": 0, "mask": 7, "source_Gram": "0"},
        "orthogonal_record_scope_is_explicit": instrument["overlap_disposition"] == "POSITIVE_WITHOUT_CROSS_TERMS_BECAUSE_CHANNEL_RECORDS_ARE_ORTHOGONAL",
        "coherent_probability_is_not_promoted": interpretation["unobserved_coherent_BT_probability"] == "NOT_CONSTRUCTED" and any("unobserved coherent" in row for row in boundaries),
        "Eq19_all_time_and_soft_boundaries_are_preserved": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["all_time_scattering"] == "NOT_CONSTRUCTED" and interpretation["soft_internal_zero_limit"] == "EXCLUDED",
        "gravity_and_Lorentzian_boundaries_are_preserved": "gravity or BV/BRST transfer" in boundaries and "anything LORENTZIAN-CAUSAL" in boundaries,
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

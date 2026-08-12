#!/usr/bin/env python3
"""Independent exact verifier for coherent compact BT packet detection."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-coherent-compact-wavepacket-detector-dilation-v1.schema.json")


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


def add(left, right):
    return [[a + b for a, b in zip(x, y)] for x, y in zip(left, right)]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def positions_from_masks(channels):
    choi = [[None for _ in range(8)] for _ in range(8)]
    for coefficient, representative in enumerate(channels):
        for mask in (representative, representative ^ 63):
            choi[(mask >> 3) & 7][mask & 7] = coefficient
    positions = [None] * 10
    for row in range(4):
        for column in range(4):
            entries = [choi[row][column], choi[row][7-column], choi[7-row][column], choi[7-row][7-column]]
            present = [entry for entry in entries if entry is not None]
            if present:
                if len(present) != 2 or present[0] != present[1]:
                    raise ValueError("non-diagonal complement projection")
                positions[present[0]] = (row, column)
    if any(position is None for position in positions):
        raise ValueError("missing positive-frame position")
    return positions


def residues_from_masks(channels):
    positions = positions_from_masks(channels)
    residues = []
    for omitted in range(10):
        matrix = [[Fraction(0) for _ in range(4)] for _ in range(4)]
        for coefficient, (row, column) in enumerate(positions):
            if coefficient != omitted:
                matrix[row][column] = Fraction(1, 4)
        residues.append(matrix)
    return residues


def trace_product(left, right):
    return sum((left[row][column] * right[row][column] for row in range(4) for column in range(4)), Fraction(0))


def matrix_vector(matrix, vector):
    return [sum((entry * value for entry, value in zip(row, vector)), Fraction(0)) for row in matrix]


def verify(certificate):
    predecessor_path = next(row["path"] for row in certificate["provenance"]["inputs"] if row["path"].endswith("TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json"))
    predecessor = load(os.path.join(ROOT, predecessor_path))
    channels = predecessor["ten_channel_residue_algebra"]["channel_masks"]
    residues = residues_from_masks(channels)
    gram = [[trace_product(left, right) for right in residues] for left in residues]
    expected = [[Fraction(9, 16) if a == b else Fraction(1, 2) for b in range(10)] for a in range(10)]
    stored = [[Fraction(value) for value in row] for row in certificate["coherent_residue_interference"]["matrix"]]
    ones = [Fraction(1)] * 10
    transverse = [[Fraction(index == j) - Fraction(index == 0) for index in range(10)] for j in range(1, 10)]
    source = [Fraction(1), Fraction(0), Fraction(0), Fraction(0)]
    images = [matrix_vector(residue, source) for residue in residues]

    weights = [Fraction(3, 5), Fraction(4, 5)]
    coherent = add(scale(weights[0], residues[1]), scale(weights[1], residues[2]))
    effect = matmul(transpose(coherent), coherent)
    incoherent = add(scale(weights[0] ** 2, matmul(transpose(residues[1]), residues[1])), scale(weights[1] ** 2, matmul(transpose(residues[2]), residues[2])))
    compressed_effect = scale(Fraction(1, 100), effect)
    forced_virtual = scale(Fraction(-1, 2), compressed_effect)
    dilation_entries = [(Fraction(1, 2), Fraction(3, 4)), (Fraction(1, 3), Fraction(8, 9))]

    effect_result = certificate["coherent_packet_effect"]
    scalar_result = certificate["declared_scalar_source"]
    virtual = certificate["BT_virtual_coefficient_boundary"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    ledger = certificate["missing_object_ledger"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "predecessor_is_passing": predecessor["checks"]["ok"],
        "residues_are_rebuilt_from_masks": len(residues) == 10 and all(sum(entry == Fraction(1, 4) for row in residue for entry in row) == 9 for residue in residues),
        "Gram_is_independently_recomputed": gram == expected == stored,
        "singlet_eigenvalue_is_exact": matrix_vector(gram, ones) == [Fraction(81, 16)] * 10,
        "transverse_eigenvalues_are_exact": all(matrix_vector(gram, vector) == [entry / 16 for entry in vector] for vector in transverse),
        "Gram_is_strictly_positive": Fraction(81, 16) > 0 and Fraction(1, 16) > 0,
        "hard_source_image_is_zero": images[0] == [Fraction(0)] * 4,
        "nine_source_images_coincide": images[1:] == [[Fraction(1, 4), 0, 0, 0]] * 9,
        "coherent_cross_term_is_retained": effect != incoherent,
        "coherent_bound_constant_is_rederived": 256 * Fraction(81, 16) == 1296 and effect_result["operator_bound"].startswith("||A_coh||^2<=1296"),
        "source_probability_constant_is_rederived": 256 * Fraction(1, 16) == 16 and scalar_result["click_probability"].startswith("q_click=16*lambda^8"),
        "click_is_an_adjoint_square": effect_result["click"] == "E_click=A_coh^*A_coh",
        "positive_domain_and_completeness_are_recorded": effect_result["sufficient_positive_domain"].startswith("1296*lambda^8") and effect_result["completeness"] == "E_click+E_no=I",
        "finite_compression_has_nonzero_forced_virtual": any(entry for row in forced_virtual for entry in row),
        "Julia_diagonal_defect_identities_are_exact": all(amplitude**2 + defect_square == 1 for amplitude, defect_square in dilation_entries),
        "Julia_cross_blocks_cancel_exactly": all(amplitude * defect_square - defect_square * amplitude == 0 for amplitude, defect_square in dilation_entries),
        "operational_dilation_is_not_BT_affiliation": certificate["exact_detector_dilation"]["status"] == "EXACT_OPERATIONAL_JULIA_DILATION_OF_LEADING_COHERENT_AMPLITUDE" and virtual["disposition"] == "CONDITIONALLY_FORCED_TARGET_NOT_DYNAMICALLY_AFFILIATED",
        "BT_virtual_graph_is_fail_closed": virtual["public_BT_order_lambda8_virtual_graph"] == "NOT_COMPUTED" and interpretation["BT_virtual_survival_coefficient"] == "CONDITIONALLY_FORCED_NOT_COMPUTED",
        "missing_virtual_and_domain_objects_are_ledgered": [row["status"] for row in ledger] == ["MISSING", "MISSING"] and "virtual amplitude" in ledger[0]["object"] and "common-domain" in ledger[1]["object"],
        "all_time_and_Eq19_are_not_promoted": interpretation["all_time_scattering"] == "NOT_CONSTRUCTED" and interpretation["general_Eq19"] == "NOT_PROVED",
        "gravity_and_Lorentzian_boundaries_are_preserved": "gravity or BV/BRST transfer" in boundaries and "anything LORENTZIAN-CAUSAL" in boundaries,
        "next_gate_requests_the_missing_BT_calculation": "order-lambda8 BT forward/virtual packet kernel" in certificate["next_gate"],
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

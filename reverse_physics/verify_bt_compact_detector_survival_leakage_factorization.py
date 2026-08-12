#!/usr/bin/env python3
"""Independent verifier for compact-detector survival/leakage factorization."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_DETECTOR_SURVIVAL_LEAKAGE_FACTORIZATION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-compact-detector-survival-leakage-factorization-v1.schema.json")


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


def multiply(left, right):
    columns = transpose(right)
    return [[sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in columns] for row in left]


def add(*matrices):
    return [[sum((matrix[i][j] for matrix in matrices), Fraction(0)) for j in range(3)] for i in range(3)]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def completion(click, leakage):
    generator = [[0, -click, -leakage], [click, 0, 0], [leakage, 0, 0]]
    second = scale(Fraction(1, 2), multiply(generator, generator))
    defect = add(second, transpose(second), multiply(transpose(generator), generator))
    return generator, second, defect


def stored_fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def verify(certificate):
    click = Fraction(3, 10)
    leakages = [Fraction(0), Fraction(2, 5)]
    completions = [completion(click, leakage) for leakage in leakages]
    click_probability = click**2
    leakage_probability = leakages[1] ** 2
    virtuals = [second[0][0] for _, second, _ in completions]
    survivals = [2 * value for value in virtuals]
    no_clicks = [survivals[index] + leakages[index] ** 2 for index in range(2)]
    witness = certificate["two_completion_witness"]
    identity = certificate["order_lambda8_identity"]
    disposition = certificate["compact_BT_disposition"]
    boundaries = certificate["does_not_establish"]
    ledger = certificate["missing_object_ledger"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "all_predecessors_pass": all(load(os.path.join(ROOT, row["path"]))["checks"]["ok"] for row in certificate["provenance"]["inputs"] if "/certificates/" in row["path"]),
        "both_generators_are_independently_skew": all(transpose(generator) == scale(-1, generator) for generator, _, _ in completions),
        "both_order_two_defects_vanish": all(all(entry == 0 for row in defect for entry in row) for _, _, defect in completions),
        "stored_click_amplitude_matches": stored_fraction(witness["selected_click_amplitude"]) == click,
        "stored_click_probability_matches": stored_fraction(witness["selected_click_probability"]) == click_probability,
        "stored_leakage_amplitudes_match": stored_fraction(witness["minimal_leakage_amplitude"]) == leakages[0] and stored_fraction(witness["leaky_amplitude"]) == leakages[1],
        "stored_leakage_probability_matches": stored_fraction(witness["leaky_probability"]) == leakage_probability,
        "stored_virtuals_match": [stored_fraction(witness["minimal_forward_Hermitian_coefficient"]), stored_fraction(witness["leaky_forward_Hermitian_coefficient"])] == virtuals,
        "same_click_has_different_virtuals": virtuals == [Fraction(-9, 200), Fraction(-1, 8)] and virtuals[0] != virtuals[1],
        "survival_contains_click_and_leakage": survivals == [-click_probability, -(click_probability + leakage_probability)],
        "both_no_click_coefficients_equal_minus_click": no_clicks == [-click_probability, -click_probability],
        "stored_common_no_click_matches": stored_fraction(witness["common_detector_no_click_coefficient"]) == -click_probability,
        "operator_factorization_is_recorded": identity["factorization"] == "detector no-click=true survival+outside leakage" and "B_out^*B_out" in identity["forward_Hermitian_part"],
        "minimal_Julia_is_not_promoted": disposition["minimal_Julia_dilation"] == "ZERO_LEAKAGE_COMPLETION_NOT_UNIQUE_BT_EVOLUTION",
        "outside_block_is_fail_closed": disposition["outside_positive_transition_block"] == "UNCOMPUTED_AND_NOT_CERTIFIED_ZERO",
        "full_dynamics_is_not_promoted": disposition["complete_BT_finite_time_evolution"] == "NOT_CONSTRUCTED",
        "missing_objects_are_preserved": [row["status"] for row in ledger] == ["MISSING"] * 3 and "complete leading BT transition column" in ledger[0]["object"],
        "Eq19_gravity_and_Lorentzian_boundaries_are_preserved": "the standard scalar projector or general Eq. (19)" in boundaries and "gravity or BV/BRST transfer" in boundaries and "anything LORENTZIAN-CAUSAL" in boundaries,
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

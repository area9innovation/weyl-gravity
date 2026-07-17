#!/usr/bin/env python3
"""Independent exact verifier for the cloned-observer rank fixture."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/rank_one_cloned_observer_input.json"
CERTIFICATE = PACKAGE / "certificates/RANK_ONE_CLONED_OBSERVER_FIXTURE.json"
SCHEMA = PACKAGE / "schema/rank-one-cloned-observer-fixture-v1.schema.json"
INPUT_SCHEMA = PACKAGE / "schema/rank-one-cloned-observer-input-v1.schema.json"


def _apply_patch(data: dict, patch: dict) -> dict:
    mutated = json.loads(json.dumps(data))
    mutated.update(patch)
    return mutated


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rational(value: str | int) -> sp.Rational:
    item = Fraction(str(value))
    return sp.Rational(item.numerator, item.denominator)


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.simplify(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def main() -> int:
    data = json.loads(INPUT.read_text())
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    if certificate["declared_input_sha256"] != _sha256(INPUT):
        raise AssertionError("declared fixture input drifted")
    for source in certificate["provenance"]["source_manifest"]:
        if _sha256(ROOT / source["path"]) != source["sha256"]:
            raise AssertionError(f"source drift: {source['path']}")

    numerator = sp.Matrix(data["orthogonal_numerator"])
    denominator = _rational(data["orthogonal_denominator"])
    orthogonal = numerator / denominator
    dimension = orthogonal.rows
    if orthogonal * orthogonal.T != sp.eye(dimension):
        raise AssertionError("independent orthogonality replay failed")

    projection_rows = data["projection_rows"]
    global_encoding = sp.Matrix([sp.sqrt(dimension) * orthogonal.row(row) for row in projection_rows])
    global_gram = sp.simplify(global_encoding.T * global_encoding)
    nonzero_entries = [value for value in global_gram if value != 0]
    if not nonzero_entries:
        raise AssertionError("global Gram matrix vanished")
    for rows in itertools.combinations(range(global_gram.rows), 2):
        for columns in itertools.combinations(range(global_gram.cols), 2):
            if global_gram.extract(rows, columns).det() != 0:
                raise AssertionError("nonzero global 2x2 minor")

    observer_count = len(data["effective_basis"]["observer_labels"])
    matter_count = len(data["effective_basis"]["matter_labels"])
    observer_encoding = sp.zeros(observer_count, matter_count)
    for observer_index, probability in enumerate(data["pointer_probabilities"]):
        for matter_index in range(matter_count):
            source_column = observer_index * matter_count + matter_index
            observer_encoding[data["clone_map"][observer_index], matter_index] += (
                sp.sqrt(dimension * _rational(probability)) * orthogonal[projection_rows[0], source_column]
            )
    observer_gram = sp.simplify(observer_encoding.T * observer_encoding)
    if observer_gram.det() == 0:
        raise AssertionError("observer encoding lost full rank")
    if _matrix_strings(global_encoding) != certificate["generated_matrices"]["global_encoding"]:
        raise AssertionError("global encoding data mismatch")
    if _matrix_strings(global_gram) != certificate["generated_matrices"]["global_gram"]:
        raise AssertionError("global Gram data mismatch")
    if _matrix_strings(observer_encoding) != certificate["generated_matrices"]["observer_encoding"]:
        raise AssertionError("observer encoding data mismatch")
    if _matrix_strings(observer_gram) != certificate["generated_matrices"]["observer_gram"]:
        raise AssertionError("observer Gram data mismatch")
    if certificate["exact_witnesses"]["global_rank"] != 1:
        raise AssertionError("persisted global rank is not one")
    if certificate["exact_witnesses"]["observer_rank"] != 2:
        raise AssertionError("persisted observer rank is not two")
    mutation_results = {item["name"]: item for item in certificate["mutation_results"]}
    for mutation in data["mutations"]:
        mutated = _apply_patch(data, mutation["patch"])
        mutated_rows = mutated["projection_rows"]
        mutated_projection = sp.Matrix([sp.sqrt(dimension) * orthogonal.row(row) for row in mutated_rows])
        mutated_gram = sp.simplify(mutated_projection.T * mutated_projection)
        for row in mutated["factorization_amplitude_rows"]:
            amplitude = sp.sqrt(dimension) * orthogonal.row(row)
            mutated_gram += amplitude.T * amplitude
        mutated_clone_injective = len(set(mutated["clone_map"])) == observer_count
        mutated_overlap = sp.Matrix([[_rational(value) for value in row] for row in mutated["pointer_basis_overlap_squared"]])
        mutated_output_rows = observer_count if mutated["observer_channel_enabled"] else 1
        mutated_observer = sp.zeros(mutated_output_rows * len(mutated_rows), matter_count)
        for observer_index, probability in enumerate(mutated["pointer_probabilities"]):
            clone_index = mutated["clone_map"][observer_index] if mutated["observer_channel_enabled"] else 0
            for projection_index, source_row in enumerate(mutated_rows):
                for matter_index in range(matter_count):
                    source_column = observer_index * matter_count + matter_index
                    mutated_observer[clone_index * len(mutated_rows) + projection_index, matter_index] += (
                        sp.sqrt(dimension * _rational(probability)) * orthogonal[source_row, source_column]
                    )
        requirements = {
            "global_gram_rank_one": mutated_gram.rank() == 1,
            "observer_encoding_rank_gt_one": mutated_observer.rank() > 1,
            "pointer_basis_aligned": mutated_overlap == sp.eye(observer_count),
            "pointer_reference_injective": mutated["observer_channel_enabled"] and mutated_clone_injective,
        }
        requirement = mutation["expected_failed_requirement"]
        if requirements[requirement] is not False:
            raise AssertionError(f"mutation did not fail independently: {mutation['name']}")
        persisted = mutation_results[mutation["name"]]
        if persisted["expected_failed_requirement"] != requirement or persisted["observed_requirement_value"] is not False:
            raise AssertionError(f"mutation certificate mismatch: {mutation['name']}")
    if certificate["flags"]["BERGER_QUANTUM_COMPARISON"] is not False:
        raise AssertionError("fixture illegally promoted the Berger quantum comparison")
    print("RANK_ONE_CLONED_OBSERVER_FIXTURE independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

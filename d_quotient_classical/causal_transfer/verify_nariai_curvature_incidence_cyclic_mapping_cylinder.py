#!/usr/bin/env python3
"""Independent formal-matrix consumer for the Nariai cyclic cylinder."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from covariant_completion.minimal_witness.formal_operators import OperatorPolynomial as O


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-cyclic-mapping-cylinder-v1.schema.json"
SIZE = 8
DEGREES = (-1, -1, 0, 0, 1, 1, 2, 2)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero():
    return [[O.zero() for _ in range(SIZE)] for _ in range(SIZE)]


def _identity():
    value = _zero()
    for index in range(SIZE): value[index][index] = O.identity()
    return value


def _add(left, right):
    return [[left[i][j] + right[i][j] for j in range(SIZE)] for i in range(SIZE)]


def _scale(matrix, coefficient):
    return [[entry.scale(coefficient) for entry in row] for row in matrix]


def _multiply(left, right):
    value = _zero()
    for i in range(SIZE):
        for j in range(SIZE):
            for k in range(SIZE): value[i][j] = value[i][j] + left[i][k] * right[k][j]
    return value


def _adjoint(value):
    involution = {"d": "dsharp", "dsharp": "d", "M": "M", "L": "Lsharp", "Lsharp": "L"}
    return O._from_dict({tuple(involution[name] for name in reversed(word)): coefficient for word, coefficient in value.terms})


def _matrix_adjoint(matrix):
    return [[_adjoint(matrix[j][i]) for j in range(SIZE)] for i in range(SIZE)]


def _is_zero(matrix):
    return all(entry == O.zero() for row in matrix for entry in row)


def _reduce(value):
    terms = {}
    for word, coefficient in value.terms:
        if any(word[i:i+2] in {("M", "d"), ("dsharp", "M")} for i in range(max(0, len(word)-1))):
            continue
        terms[word] = terms.get(word, Fraction()) + coefficient
    return O._from_dict(terms)


def _zero_mod(matrix):
    return all(_reduce(entry) == O.zero() for row in matrix for entry in row)


def _digest(matrix):
    payload = "\n".join(",".join(entry.display() for entry in row) for row in matrix)
    return hashlib.sha256(payload.encode()).hexdigest()


def _parse_operator(terms):
    return O._from_dict({tuple(word): Fraction(numerator, denominator) for word, numerator, denominator in terms})


def _parse_matrix(value):
    if value["shape"] != [SIZE, SIZE]: raise ValueError("formal matrix shape drifted")
    matrix = _zero()
    for row, column, terms in value["entries"]: matrix[row][column] = _parse_operator(terms)
    if _digest(matrix) != value["sha256"]: raise ValueError("formal matrix digest drifted")
    return matrix


def verify():
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest: raise ValueError(f"source digest drifted: {relative}")
    for name, dependency in value["dependency_refs"].items():
        if _sha256(ROOT / dependency["path"]) != dependency["sha256"]: raise ValueError(f"dependency drifted: {name}")

    matrices = {name: _parse_matrix(matrix) for name, matrix in value["exact_matrices"].items()}
    split = matrices["split"]
    pairing = matrices["pairing"]
    transform = matrices["split_to_graph"]
    inverse = matrices["graph_to_split"]
    prolonged = matrices["prolonged"]
    inclusion = matrices["inclusion"]
    projection = matrices["projection"]
    homotopy = matrices["homotopy"]
    identity = _identity()
    degree_sign = _zero()
    for index, degree in enumerate(DEGREES): degree_sign[index][index] = O.identity(-1 if degree % 2 else 1)
    if not _is_zero(_add(_multiply(transform, inverse), _scale(identity, -1))): raise ValueError("right inverse failed")
    if not _is_zero(_add(_multiply(inverse, transform), _scale(identity, -1))): raise ValueError("left inverse failed")
    if _multiply(_multiply(transform, split), inverse) != prolonged: raise ValueError("conjugated differential drifted")
    if not _zero_mod(_multiply(split, split)): raise ValueError("split Q square failed")
    if not _zero_mod(_multiply(prolonged, prolonged)): raise ValueError("prolonged Q square failed")
    split_cyclic = _add(_multiply(_matrix_adjoint(split), pairing), _multiply(_multiply(degree_sign, pairing), split))
    if not _is_zero(split_cyclic): raise ValueError("split cyclicity failed")
    cyclic = _add(_multiply(_matrix_adjoint(prolonged), pairing), _multiply(_multiply(degree_sign, pairing), prolonged))
    if not _is_zero(cyclic): raise ValueError("prolonged cyclicity failed")
    canonical = _add(_multiply(_multiply(_matrix_adjoint(transform), pairing), transform), _scale(pairing, -1))
    if not _is_zero(canonical): raise ValueError("canonical shear failed")
    parent_identity = _zero()
    for index in (0, 3, 5, 6): parent_identity[index][index] = O.identity()
    if not _is_zero(_add(_multiply(projection, inclusion), _scale(parent_identity, -1))): raise ValueError("PI failed")
    if not _zero_mod(_add(_multiply(prolonged, inclusion), _scale(_multiply(inclusion, split), -1))): raise ValueError("inclusion chain map failed")
    if not _zero_mod(_add(_multiply(projection, prolonged), _scale(_multiply(split, projection), -1))): raise ValueError("projection chain map failed")
    retract = _add(_add(_multiply(inclusion, projection), _scale(identity, -1)), _scale(_add(_multiply(prolonged, homotopy), _multiply(homotopy, prolonged)), -1))
    if not _zero_mod(retract): raise ValueError("mapping-cylinder SDR failed")
    homotopy_cyclic = _add(_multiply(_matrix_adjoint(homotopy), pairing), _scale(_multiply(_multiply(degree_sign, pairing), homotopy), -1))
    if not _is_zero(homotopy_cyclic): raise ValueError("homotopy cyclicity failed")
    for row in range(SIZE):
        for column in range(SIZE):
            if split[row][column] != O.zero() and DEGREES[row] != DEGREES[column] + 1:
                raise ValueError("split differential degree drifted")
            if prolonged[row][column] != O.zero() and DEGREES[row] != DEGREES[column] + 1:
                raise ValueError("prolonged differential degree drifted")
            if transform[row][column] != O.zero() and DEGREES[row] != DEGREES[column]:
                raise ValueError("canonical shear degree drifted")
            if pairing[row][column] != O.zero() and DEGREES[row] + DEGREES[column] != 1:
                raise ValueError("odd pairing degree drifted")
            if homotopy[row][column] != O.zero() and DEGREES[row] != DEGREES[column] - 1:
                raise ValueError("homotopy degree drifted")
    atoms = {atom for matrix in matrices.values() for row in matrix for entry in row for word, _ in entry.terms for atom in word}
    if atoms != {"d", "dsharp", "M", "L", "Lsharp"}: raise ValueError(f"operator alphabet drifted: {atoms}")
    if value["flags"]["METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE"] is not False: raise ValueError("metric endpoint was overpromoted")
    print("NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1 independent verification: PASS")
    return value


if __name__ == "__main__": verify()

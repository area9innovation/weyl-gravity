#!/usr/bin/env python3
"""Independent quotient-model verifier for the Berger module closure.

The producer realizes spin four as the kernel of invariant contraction.  This
consumer instead forms Sym^4 modulo the invariant quadratic ideal, so the two
rails do not share the representation construction.
"""

from __future__ import annotations

from itertools import product
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from jsonschema import Draft202012Validator
import numpy as np
from scipy.sparse import csr_matrix

from d_quotient_classical.causal_transfer import (
    berger_q26_cauchy_bv_carrier_obstruction as predecessor,
)


GRAPH = predecessor.GRAPH
ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/berger_q26_finite_row_module_closure_v1/spin4_closure_witness.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-q26-finite-row-module-closure-lower-bound-v1.schema.json"
SIX_ROW = ROOT / "d_quotient_classical/certificates/BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1.json"
Q104 = ROOT / "quantum-weyl/lorentzian/generated/berger_canonical_graph_q_cauchy_obstruction/rejected_candidate_q_Cauchy_104.json"
A104 = ROOT / "quantum-weyl/lorentzian/generated/berger_a104_endpoint_completion/global_A104.json"
PRIME = 1009
SEED = 26072034
PINNED_COMMIT = "988f8ee6c59b539ae516eb8a8f882a57a95f71e0"
PINNED_PATH = (
    "physics/symplectic-reconstruction/d_quotient_classical/certificates/"
    "BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json"
)
PINNED_SHA256 = "24d2db35fb3dc696081d1e93208fdbd0b8f31922cdac7a063033650a9e686a01"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _rref(value: np.ndarray) -> tuple[np.ndarray, list[int]]:
    result = value.copy() % PRIME
    row = 0
    pivots: list[int] = []
    for column in range(result.shape[1]):
        candidates = np.flatnonzero(result[row:, column])
        if not len(candidates):
            continue
        selected = row + int(candidates[0])
        result[[row, selected]] = result[[selected, row]]
        result[row] = (
            result[row] * pow(int(result[row, column]), -1, PRIME)
        ) % PRIME
        for other in range(result.shape[0]):
            if other != row and result[other, column]:
                result[other] = (
                    result[other] - result[other, column] * result[row]
                ) % PRIME
        pivots.append(column)
        row += 1
        if row == result.shape[0]:
            break
    return result, pivots


def _nullspace(value: np.ndarray) -> np.ndarray:
    reduced, pivots = _rref(value)
    free = [
        column for column in range(value.shape[1])
        if column not in pivots
    ]
    result = np.zeros((value.shape[1], len(free)), dtype=np.int64)
    for local, column in enumerate(free):
        result[column, local] = 1
        for row, pivot in enumerate(pivots):
            result[pivot, local] = -reduced[row, column] % PRIME
    return result


def _inverse(value: np.ndarray) -> np.ndarray:
    size = value.shape[0]
    augmented = np.concatenate(
        [value.copy() % PRIME, np.eye(size, dtype=np.int64)], axis=1
    )
    for column in range(size):
        candidates = np.flatnonzero(augmented[column:, column])
        if not len(candidates):
            raise AssertionError("singular quotient section")
        selected = column + int(candidates[0])
        augmented[[column, selected]] = augmented[[selected, column]]
        augmented[column] = (
            augmented[column]
            * pow(int(augmented[column, column]), -1, PRIME)
        ) % PRIME
        for row in range(size):
            if row != column and augmented[row, column]:
                augmented[row] = (
                    augmented[row]
                    - augmented[row, column] * augmented[column]
                ) % PRIME
    return augmented[:, size:]


def _spin_four_quotient() -> list[np.ndarray]:
    monomials = [
        value for value in product(range(5), repeat=3) if sum(value) == 4
    ]
    degree_two = [
        value for value in product(range(3), repeat=3) if sum(value) == 2
    ]
    index = {value: position for position, value in enumerate(monomials)}
    base = [
        np.asarray(matrix.tolist(), dtype=np.int64) % PRIME
        for matrix in predecessor._representation()
    ]

    def induced(matrix: np.ndarray) -> np.ndarray:
        result = np.zeros((15, 15), dtype=np.int64)
        for column, exponents in enumerate(monomials):
            for old_axis, count in enumerate(exponents):
                if not count:
                    continue
                for new_axis in range(3):
                    coefficient = int(matrix[new_axis, old_axis])
                    if not coefficient:
                        continue
                    output = list(exponents)
                    output[old_axis] -= 1
                    output[new_axis] += 1
                    row = index[tuple(output)]
                    result[row, column] = (
                        result[row, column] + count * coefficient
                    ) % PRIME
        return result

    # Quotient by (x^2+y^2+z^2/3) Sym^2.
    ideal = np.zeros((15, 6), dtype=np.int64)
    weights = (1, 1, pow(3, -1, PRIME))
    for column, exponents in enumerate(degree_two):
        for axis, weight in enumerate(weights):
            output = list(exponents)
            output[axis] += 2
            ideal[index[tuple(output)], column] = weight
    annihilator = _nullspace(ideal.T)
    quotient = annihilator.T
    if quotient.shape != (9, 15) or np.any(quotient @ ideal % PRIME):
        raise AssertionError("spin-four quotient construction failed")
    _, selected_columns = _rref(quotient)
    selected = selected_columns[:9]
    section = np.zeros((15, 9), dtype=np.int64)
    section[selected, :] = _inverse(quotient[:, selected])
    if not np.array_equal(
        quotient @ section % PRIME, np.eye(9, dtype=np.int64)
    ):
        raise AssertionError("spin-four quotient section failed")
    result = [np.eye(9, dtype=np.int64)]
    result.extend(
        quotient @ induced(base[axis]) % PRIME @ section % PRIME
        for axis in range(1, 4)
    )
    for left, right, target, coefficient in (
        (1, 2, 3, 1),
        (2, 3, 1, 3),
        (3, 1, 2, 3),
    ):
        if np.any(
            (
                result[left] @ result[right]
                - result[right] @ result[left]
                - coefficient * result[target]
            )
            % PRIME
        ):
            raise AssertionError("quotient representation relation failed")
    return result


def _coefficient(polynomial: GRAPH.Polynomial) -> int:
    return sum(
        value.numerator
        * pow(value.denominator, -1, PRIME)
        * pow(2, monomial[0], PRIME)
        * pow(3, monomial[2], PRIME)
        for monomial, value in polynomial.items()
    ) % PRIME


def _evaluate_operator(
    operator: GRAPH.Operator, representation: list[np.ndarray]
) -> np.ndarray:
    result = np.zeros((9, 9), dtype=np.int64)
    for word, polynomial in operator.items():
        represented = np.eye(9, dtype=np.int64)
        for axis in word:
            represented = represented @ representation[axis] % PRIME
        result = (result + _coefficient(polynomial) * represented) % PRIME
    return result


def _evaluate_matrix(
    matrix: GRAPH.Matrix, representation: list[np.ndarray]
) -> np.ndarray:
    result = np.zeros((936, 936), dtype=np.int64)
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            if operator:
                result[
                    9 * row:9 * (row + 1),
                    9 * column:9 * (column + 1),
                ] = _evaluate_operator(operator, representation)
    return result


def _compress(
    parts: list[np.ndarray],
    generator: np.random.Generator,
    count: int,
) -> np.ndarray:
    candidates = np.concatenate(parts, axis=1)
    rows, columns = candidates.shape
    indices = np.empty(rows * count, dtype=np.int32)
    data = np.empty(rows * count, dtype=np.int64)
    indptr = np.arange(0, (rows + 1) * count, count, dtype=np.int32)
    for column in range(rows):
        start = column * count
        stop = start + count
        indices[start:stop] = generator.choice(columns, count, replace=False)
        data[start:stop] = generator.integers(1, PRIME, count)
    transform = csr_matrix(
        (data, indices, indptr), shape=(rows, columns)
    )
    return np.asarray(transform @ candidates.T).T % PRIME


def _determinant(value: np.ndarray) -> int:
    matrix = value.copy() % PRIME
    determinant = 1
    for column in range(matrix.shape[1]):
        candidates = np.flatnonzero(matrix[column:, column])
        if not len(candidates):
            return 0
        selected = column + int(candidates[0])
        if selected != column:
            matrix[[column, selected]] = matrix[[selected, column]]
            determinant = -determinant % PRIME
        pivot = int(matrix[column, column])
        determinant = determinant * pivot % PRIME
        matrix[column] = (
            matrix[column] * pow(pivot, -1, PRIME)
        ) % PRIME
        if column + 1 < matrix.shape[0]:
            factors = matrix[column + 1:, column].copy()
            matrix[column + 1:] = (
                matrix[column + 1:]
                - factors[:, None] * matrix[column]
            ) % PRIME
    return determinant


def _independent_replay() -> dict[str, int]:
    q_record = _load(Q104)
    a_record = _load(A104)
    q_value = GRAPH._load_record(q_record, (104, 104))
    evolution = GRAPH._canonical_symbols(
        GRAPH._load_hashed_operator(A104, (104, 104))
    )
    representation = _spin_four_quotient()
    q_matrix = _evaluate_matrix(q_value, representation)
    a_matrix = _evaluate_matrix(evolution, representation)
    square = q_matrix @ q_matrix % PRIME
    commutator = (a_matrix @ q_matrix - q_matrix @ a_matrix) % PRIME
    generator = np.random.default_rng(SEED)
    closure = _compress([square, commutator], generator, 100)
    for level in range(1, 9):
        closure = _compress(
            [
                closure,
                q_matrix @ closure % PRIME,
                a_matrix @ closure % PRIME,
                q_matrix.T @ closure % PRIME,
                a_matrix.T @ closure % PRIME,
            ],
            generator,
            150,
        )
        determinant = _determinant(closure)
        if determinant:
            return {"level": level, "determinant": determinant}
    raise AssertionError("independent spin-four closure did not become full")


def verify() -> None:
    certificate = _load(CERT)
    payload = _load(PAYLOAD)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if _sha(PAYLOAD) != certificate["exact_payload"]["sha256"]:
        raise AssertionError("closure payload digest drifted")
    for relative, expected in certificate["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source digest drifted: {relative}")
    pinned = subprocess.run(
        ["git", "show", f"{PINNED_COMMIT}:{PINNED_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if hashlib.sha256(pinned).hexdigest() != PINNED_SHA256:
        raise AssertionError("pinned predecessor drifted")
    for key in ("q_Cauchy", "A104"):
        ref = certificate["pinned_inputs"][key]
        if _sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"operator input drifted: {key}")
    if _sha(SIX_ROW) != certificate["pinned_inputs"]["six_row_terminal"]["sha256"]:
        raise AssertionError("six-row terminal input drifted")
    if payload["closure_levels"][-1]["certified_independent_columns"] != 936:
        raise AssertionError("producer payload does not contain full closure")
    replay = _independent_replay()
    if not replay["determinant"]:
        raise AssertionError("independent full minor vanished")
    if certificate["representation_module_closure"]["added_rows_at_least"] != 104:
        raise AssertionError("104-row bound drifted")
    if (
        certificate["classification"]["one_hundred_four_row_extension_sufficient"]
        or certificate["classification"]["Hadamard_or_quantum_claim"]
    ):
        raise AssertionError("lower bound was over-promoted")
    print(
        "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1: "
        f"VERIFIED (quotient determinant={replay['determinant']} mod {PRIME})"
    )


if __name__ == "__main__":
    verify()

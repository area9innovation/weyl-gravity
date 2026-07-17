#!/usr/bin/env python3
"""Independent exact replay of the constant-field mixed-ell3 redefinition."""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Mapping

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-constant-field-redefinition-v1.schema.json"
SQRT10 = sp.sqrt(10)
FIELD_ROWS = tuple(range(3, 13)) + tuple(range(27, 31))
LOCAL = {row: index for index, row in enumerate(FIELD_ROWS)}
G = tuple(range(10))
A = tuple(range(10, 14))
PAIR = {
    **{row: (LOCAL[row - 10], sp.Integer(1)) for row in range(13, 23)},
    **{row: (LOCAL[row - 4], sp.Integer(2)) for row in range(31, 35)},
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scalar(value: object) -> sp.Expr:
    if isinstance(value, int):
        return sp.Integer(value)
    if isinstance(value, str):
        return sp.sympify(value, locals={"sqrt": sp.sqrt})
    return sp.Rational(int(value["numerator"]), int(value["denominator"]))


def _q10(value: Mapping[str, object]) -> sp.Expr:
    return sp.expand(_scalar(value["rational"]) + SQRT10 * _scalar(value["sqrt10"]))


def _add(poly: dict[tuple[int, ...], sp.Expr], monomial: Iterable[int], coefficient: sp.Expr) -> None:
    key = tuple(sorted(monomial))
    value = sp.expand(poly.get(key, 0) + coefficient)
    if value:
        poly[key] = value
    else:
        poly.pop(key, None)


def _derivative(poly: Mapping[tuple[int, ...], sp.Expr], field: int) -> dict[tuple[int, ...], sp.Expr]:
    value: dict[tuple[int, ...], sp.Expr] = {}
    for monomial, coefficient in poly.items():
        multiplicity = monomial.count(field)
        if multiplicity:
            reduced = list(monomial)
            reduced.remove(field)
            _add(value, reduced, coefficient * multiplicity)
    return value


def _payloads(value: dict) -> dict[str, dict]:
    payloads = {}
    for name, record in value["dependency_refs"].items():
        path = ROOT / record["path"]
        if _sha256(path) != record["sha256"]:
            raise ValueError(f"dependency digest drifted: {name}")
        payloads[name] = json.loads(path.read_text())
    return payloads


def _polynomials(payloads: Mapping[str, dict]) -> tuple[dict, dict, dict]:
    typed = payloads["typed_retained_carrier"]
    quadratic: dict[tuple[int, ...], sp.Expr] = {}
    for output, source, terms in typed["retained_complex"]["classical_unary_q1"]["entries"]:
        if output not in PAIR or source not in LOCAL:
            continue
        paired, weight = PAIR[output]
        for word, coefficient in terms:
            if sum(word) == 0:
                _add(quadratic, (paired, LOCAL[source]), weight * _scalar(coefficient))

    cubic: dict[tuple[int, ...], sp.Expr] = {}
    for name in ("retained_gravity_ell2", "retained_mixed_ell2"):
        for row in payloads[name]["rows"]:
            if row["output"] not in PAIR:
                continue
            paired, weight = PAIR[row["output"]]
            for left, left_word, right, right_word, coefficient in row["terms"]:
                if left in LOCAL and right in LOCAL and sum(left_word) + sum(right_word) == 0:
                    _add(cubic, (paired, LOCAL[left], LOCAL[right]), weight * _q10(coefficient))

    quartic: dict[tuple[int, ...], sp.Expr] = {}
    manifest = payloads["retained_mixed_ell3"]
    for chunk in manifest["chunks"]:
        path = ROOT / chunk["path"]
        if _sha256(path) != chunk["file_sha256"]:
            raise ValueError("retained ell3 chunk drifted")
        with gzip.open(path, "rt") as handle:
            row = json.load(handle)
        if row["output"] not in PAIR:
            continue
        paired, weight = PAIR[row["output"]]
        for first, first_word, second, second_word, third, third_word, coefficient in row["terms"]:
            if (
                first in LOCAL
                and second in LOCAL
                and third in LOCAL
                and sum(first_word) + sum(second_word) + sum(third_word) == 0
            ):
                _add(
                    quartic,
                    (paired, LOCAL[first], LOCAL[second], LOCAL[third]),
                    weight * _q10(coefficient),
                )
    return quadratic, cubic, quartic


def _basis() -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(sorted((*gravity, *Maxwell)))
        for gravity in itertools.combinations_with_replacement(G, 2)
        for Maxwell in itertools.combinations_with_replacement(A, 2)
    )


def _labels() -> tuple[tuple[str, int, tuple[int, ...]], ...]:
    value = []
    for output in G:
        for gravity in G:
            for Maxwell in itertools.combinations_with_replacement(A, 2):
                value.append(("F3", output, (gravity, *Maxwell)))
    for output in A:
        for gravity in itertools.combinations_with_replacement(G, 2):
            for Maxwell in A:
                value.append(("F3", output, (*gravity, Maxwell)))
    for output in G:
        for gravity in itertools.combinations_with_replacement(G, 2):
            value.append(("F2", output, gravity))
        for Maxwell in itertools.combinations_with_replacement(A, 2):
            value.append(("F2", output, Maxwell))
    for output in A:
        for gravity in G:
            for Maxwell in A:
                value.append(("F2", output, (gravity, Maxwell)))
    return tuple(value)


def _matrix(quadratic: Mapping, cubic: Mapping) -> tuple[sp.MutableSparseMatrix, tuple, tuple]:
    basis = _basis()
    index = {monomial: row for row, monomial in enumerate(basis)}
    labels = _labels()
    d2 = tuple(_derivative(quadratic, field) for field in range(14))
    d3 = tuple(_derivative(cubic, field) for field in range(14))
    entries = {}
    for column, (arity, output, inputs) in enumerate(labels):
        derivative = d2[output] if arity == "F3" else d3[output]
        for monomial, coefficient in derivative.items():
            target = tuple(sorted((*monomial, *inputs)))
            if target in index:
                key = (index[target], column)
                entries[key] = sp.expand(entries.get(key, 0) + coefficient)
    return sp.MutableSparseMatrix(550, 2690, {key: val for key, val in entries.items() if val}), basis, labels


def verify(value: dict | None = None) -> dict:
    value = json.loads(CERT.read_text()) if value is None else value
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"source-manifest digest drifted: {relative}")

    quadratic, cubic, quartic = _polynomials(_payloads(value))
    matrix, basis, labels = _matrix(quadratic, cubic)
    verdict = value["exact_verdict"]
    if len(matrix.todok()) != verdict["coboundary_matrix_nonzero_entries"]:
        raise ValueError("independent coboundary support count disagrees")
    rank_basis = matrix[:, verdict["rank_basis_columns"]]
    if rank_basis.rank() != 550:
        raise ValueError("independent exact rank basis is singular")

    label_index = {label: column for column, label in enumerate(labels)}
    primitive = sp.zeros(2690, 1)
    for record in verdict["primitive"]:
        label = (record["arity"], record["output_local"], tuple(record["input_locals"]))
        if FIELD_ROWS[record["output_local"]] != record["output_row"]:
            raise ValueError("primitive output row/local mismatch")
        if [FIELD_ROWS[field] for field in record["input_locals"]] != record["input_rows"]:
            raise ValueError("primitive input row/local mismatch")
        column = label_index[label]
        if primitive[column] != 0:
            raise ValueError("duplicate primitive coefficient")
        primitive[column] = sp.sympify(record["coefficient"], locals={"sqrt": sp.sqrt})
    target = sp.Matrix([quartic.get(monomial, 0) for monomial in basis])
    if matrix * primitive != target:
        raise ValueError("independent primitive reconstruction failed")
    if sum(value != 0 for value in target) != 63:
        raise ValueError("independent constant-field target count disagrees")

    flags = value["claim_flags"]
    if (
        flags["CONSTANT_FIELD_PHYSICAL_QUARTIC_TRIVIALIZATION_COMPUTED"] is not True
        or flags["CYCLIC_DEFORMATION_CLASS_DECIDED"] is not False
        or flags["FULL_JET_BOUNDED_REDEFINITION_COMPUTED"] is not False
        or flags["ELL3_NONREMOVABLE"] is not False
        or flags["ELL3_BRANCH_MIXING_AUTHORIZED"] is not False
        or flags["QUANTUM_CLAIM"] is not False
    ):
        raise ValueError("claim boundary drifted")
    print("BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()

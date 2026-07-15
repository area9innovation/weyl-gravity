#!/usr/bin/env python3
"""Independent sparse-PBW consumer for the retained Berger q1 certificate."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-minimal-operator-v1.schema.json"
U, V, ALPHA_B = sp.symbols("u v alpha_B", nonzero=True, real=True)


def validate_portable_schema_contract(
    schema: dict[str, object], payload: dict[str, object]
) -> None:
    """Check the strict PBW subset without relying on an optional package.

    Release CI may additionally run a general Draft 2020-12 validator.  This
    local check deliberately covers the exact structural bug that once made
    ``q1_blocks`` impossible to validate: required keys must also be declared
    when ``additionalProperties`` is false.
    """

    q1_schema = schema["properties"]["q1_blocks"]
    required = q1_schema["required"]
    properties = q1_schema.get("properties", {})
    if q1_schema.get("additionalProperties") is False and any(
        key not in properties for key in required
    ):
        raise AssertionError("q1_blocks requires undeclared properties")
    definitions = schema.get("$defs", {})
    for name in ("pbwOperatorRecord", "pbwMatrixEntry", "pbwTerm"):
        if name not in definitions:
            raise AssertionError(f"missing strict PBW schema definition: {name}")

    expected_shapes = {
        "K_spatial": [10, 3],
        "H_retained": [10, 10],
        "minus_K_spatial_sharp": [3, 10],
    }
    blocks = payload["q1_blocks"]
    if set(blocks) != set(expected_shapes):
        raise AssertionError("q1 block keys are not exact")
    for name, expected_shape in expected_shapes.items():
        record = blocks[name]
        if set(record) != {"shape", "entries", "sha256"}:
            raise AssertionError(f"{name}: PBW record keys are not strict")
        if record["shape"] != expected_shape:
            raise AssertionError(f"{name}: PBW shape drifted")
        rows, columns = expected_shape
        digest = record["sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise AssertionError(f"{name}: invalid sha256")
        for entry in record["entries"]:
            if not isinstance(entry, list) or len(entry) != 3:
                raise AssertionError(f"{name}: malformed PBW matrix entry")
            row, column, terms = entry
            if not isinstance(row, int) or not 0 <= row < rows:
                raise AssertionError(f"{name}: PBW row out of range")
            if not isinstance(column, int) or not 0 <= column < columns:
                raise AssertionError(f"{name}: PBW column out of range")
            if not isinstance(terms, list) or not terms:
                raise AssertionError(f"{name}: empty PBW entry")
            for term in terms:
                if not isinstance(term, list) or len(term) != 2:
                    raise AssertionError(f"{name}: malformed PBW term")
                exponents, coefficient = term
                if (
                    not isinstance(exponents, list)
                    or len(exponents) != 4
                    or any(not isinstance(value, int) or value < 0 for value in exponents)
                ):
                    raise AssertionError(f"{name}: invalid PBW exponent vector")
                if not isinstance(coefficient, str) or not coefficient:
                    raise AssertionError(f"{name}: invalid PBW coefficient")


def _structure(first: int, second: int) -> dict[int, sp.Expr]:
    return {
        (1, 2): {3: U},
        (2, 1): {3: -U},
        (2, 3): {1: V},
        (3, 2): {1: -V},
        (3, 1): {2: V},
        (1, 3): {2: -V},
    }.get((first, second), {})


@lru_cache(maxsize=None)
def _reduce_word(word: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], sp.Expr], ...]:
    inversion = next((i for i in range(len(word) - 1) if word[i] > word[i + 1]), None)
    if inversion is None:
        return ((word, sp.S.One),)
    left, right = word[inversion], word[inversion + 1]
    swapped = word[:inversion] + (right, left) + word[inversion + 2 :]
    output = dict(_reduce_word(swapped))
    for target, coefficient in _structure(left, right).items():
        shorter = word[:inversion] + (target,) + word[inversion + 2 :]
        for reduced, nested in _reduce_word(shorter):
            output[reduced] = output.get(reduced, 0) + coefficient * nested
    return tuple(
        (reduced, sp.factor(coefficient))
        for reduced, coefficient in sorted(output.items())
        if sp.factor(coefficient) != 0
    )


def _normalize(terms: dict[tuple[int, ...], sp.Expr]) -> dict[tuple[int, ...], sp.Expr]:
    output: dict[tuple[int, ...], sp.Expr] = {}
    for word, coefficient in terms.items():
        for reduced, factor in _reduce_word(word):
            output[reduced] = output.get(reduced, 0) + coefficient * factor
    return {
        word: value
        for word, coefficient in sorted(output.items())
        if (value := sp.factor(sp.cancel(coefficient))) != 0
    }


def _add(*operators: dict[tuple[int, ...], sp.Expr]) -> dict[tuple[int, ...], sp.Expr]:
    terms: dict[tuple[int, ...], sp.Expr] = {}
    for operator in operators:
        for word, coefficient in operator.items():
            terms[word] = terms.get(word, 0) + coefficient
    return _normalize(terms)


def _scale(operator: dict[tuple[int, ...], sp.Expr], coefficient: sp.Expr) -> dict[tuple[int, ...], sp.Expr]:
    return _normalize({word: coefficient * value for word, value in operator.items()})


def _compose(
    outer: dict[tuple[int, ...], sp.Expr],
    inner: dict[tuple[int, ...], sp.Expr],
) -> dict[tuple[int, ...], sp.Expr]:
    return _normalize(
        {
            outer_word + inner_word: outer_coefficient * inner_coefficient
            for outer_word, outer_coefficient in outer.items()
            for inner_word, inner_coefficient in inner.items()
        }
    )


def _adjoint(operator: dict[tuple[int, ...], sp.Expr]) -> dict[tuple[int, ...], sp.Expr]:
    return _normalize(
        {
            tuple(reversed(word)): (-1) ** len(word) * coefficient
            for word, coefficient in operator.items()
        }
    )


def _load_matrix(record: dict[str, object]) -> list[list[dict[tuple[int, ...], sp.Expr]]]:
    body = {"shape": record["shape"], "entries": record["entries"]}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert record["sha256"] == digest
    rows, columns = record["shape"]
    matrix = [[{} for _ in range(columns)] for _ in range(rows)]
    symbols = {"u": U, "v": V, "alpha_B": ALPHA_B}
    for row, column, terms in record["entries"]:
        operator = {}
        for exponents, coefficient in terms:
            word = tuple(axis for axis, count in enumerate(exponents) for _ in range(count))
            operator[word] = sp.sympify(coefficient, locals=symbols)
        matrix[row][column] = _normalize(operator)
    return matrix


def _multiply(outer, inner):
    assert len(outer[0]) == len(inner)
    return [
        [
            _add(*(_compose(outer[row][middle], inner[middle][column]) for middle in range(len(inner))))
            for column in range(len(inner[0]))
        ]
        for row in range(len(outer))
    ]


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    validate_portable_schema_contract(schema, payload)
    blocks = payload["q1_blocks"]
    gauge = _load_matrix(blocks["K_spatial"])
    hessian = _load_matrix(blocks["H_retained"])
    noether = _load_matrix(blocks["minus_K_spatial_sharp"])
    assert (len(gauge), len(gauge[0])) == (10, 3)
    assert (len(hessian), len(hessian[0])) == (10, 10)
    assert (len(noether), len(noether[0])) == (3, 10)

    for row in range(10):
        for column in range(10):
            assert _add(hessian[row][column], _scale(_adjoint(hessian[column][row]), -1)) == {}
    for row in range(3):
        for column in range(10):
            assert _add(noether[row][column], _adjoint(gauge[column][row])) == {}
    assert all(value == {} for row in _multiply(hessian, gauge) for value in row)
    assert all(value == {} for row in _multiply(noether, hessian) for value in row)

    flags = payload["flags"]
    assert flags["BERGER_RETAINED_MINIMAL_OPERATOR"] is True
    assert flags["BERGER_NONMINIMAL_COMPLETION"] is False
    assert flags["BERGER_CAUSAL_GREEN_HOMOTOPY"] is False
    assert flags["CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT"] is False
    assert payload["next_gate"] == "BERGER_NONMINIMAL_COMPLETION"
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_RETAINED_MINIMAL_OPERATOR_INDEPENDENT: PASS")
    print("strict PBW schema, block digests, H^sharp=H, -K^sharp row, and both q1^2 compositions: PASS")
    print("nonminimal, causal, q2, and arity-two gates: OPEN")


if __name__ == "__main__":
    main()

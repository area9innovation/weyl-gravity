#!/usr/bin/env python3
"""Independent exact verifier for the Berger q26 Cauchy obstruction.

The verifier does not import the producer or the Quantum graph-obstruction
module.  Its PBW backend uses sparse ``Fraction`` coefficient dictionaries,
avoiding repeated symbolic factorization while remaining exact.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/berger_q26_cauchy_bv_carrier_obstruction_v1/adjoint_representation_witness.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-q26-cauchy-bv-carrier-obstruction-v1.schema.json"
A104 = ROOT / "quantum-weyl/lorentzian/generated/berger_a104_endpoint_completion/global_A104.json"
Q_CAUCHY = ROOT / "quantum-weyl/lorentzian/generated/berger_canonical_graph_q_cauchy_obstruction/rejected_candidate_q_Cauchy_104.json"

ALPHA, U, V = sp.symbols("alpha_B u v")
DEGREES = tuple([-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6) * 2
Monomial = tuple[int, int, int]
Polynomial = dict[Monomial, Fraction]
Operator = dict[tuple[int, ...], Polynomial]
Matrix = list[list[Operator]]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _zero(rows: int, columns: int) -> Matrix:
    return [[{} for _ in range(columns)] for _ in range(rows)]


def _polynomial(expression: sp.Expr) -> Polynomial:
    poly = sp.Poly(sp.expand(expression), ALPHA, U, V, domain=sp.QQ)
    return {
        monomial: Fraction(int(value.p), int(value.q))
        for monomial, value in poly.terms()
        if value
    }


def _poly_add(*values: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for value in values:
        for monomial, coefficient in value.items():
            result[monomial] = result.get(monomial, Fraction()) + coefficient
    return {
        monomial: coefficient
        for monomial, coefficient in result.items()
        if coefficient
    }


def _poly_scale(value: Polynomial, scalar: int | Fraction) -> Polynomial:
    factor = Fraction(scalar)
    return {
        monomial: factor * coefficient
        for monomial, coefficient in value.items()
        if factor * coefficient
    }


def _poly_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                left_monomial[index] + right_monomial[index]
                for index in range(3)
            )
            result[monomial] = (
                result.get(monomial, Fraction())
                + left_coefficient * right_coefficient
            )
    return {
        monomial: coefficient
        for monomial, coefficient in result.items()
        if coefficient
    }


def _structure(first: int, second: int) -> dict[int, Polynomial]:
    return {
        (1, 2): {3: {(0, 1, 0): Fraction(1)}},
        (2, 1): {3: {(0, 1, 0): Fraction(-1)}},
        (2, 3): {1: {(0, 0, 1): Fraction(1)}},
        (3, 2): {1: {(0, 0, 1): Fraction(-1)}},
        (3, 1): {2: {(0, 0, 1): Fraction(1)}},
        (1, 3): {2: {(0, 0, 1): Fraction(-1)}},
    }.get((first, second), {})


@lru_cache(maxsize=None)
def _reduce_word(
    word: tuple[int, ...],
) -> tuple[tuple[tuple[int, ...], tuple[tuple[Monomial, Fraction], ...]], ...]:
    inversion = next(
        (
            index
            for index in range(len(word) - 1)
            if word[index] > word[index + 1]
        ),
        None,
    )
    if inversion is None:
        return ((word, (((0, 0, 0), Fraction(1)),)),)
    left, right = word[inversion], word[inversion + 1]
    swapped = word[:inversion] + (right, left) + word[inversion + 2 :]
    output = {
        reduced: dict(factor)
        for reduced, factor in _reduce_word(swapped)
    }
    for target, coefficient in _structure(left, right).items():
        shorter = word[:inversion] + (target,) + word[inversion + 2 :]
        for reduced, nested_items in _reduce_word(shorter):
            nested = dict(nested_items)
            output[reduced] = _poly_add(
                output.get(reduced, {}),
                _poly_multiply(coefficient, nested),
            )
    return tuple(
        (reduced, tuple(sorted(coefficient.items())))
        for reduced, coefficient in sorted(output.items())
        if coefficient
    )


def _normalize(terms: Operator) -> Operator:
    output: Operator = {}
    for word, coefficient in terms.items():
        for reduced, factor_items in _reduce_word(word):
            output[reduced] = _poly_add(
                output.get(reduced, {}),
                _poly_multiply(coefficient, dict(factor_items)),
            )
    return {
        word: coefficient
        for word, coefficient in sorted(output.items())
        if coefficient
    }


def _add(*operators: Operator) -> Operator:
    output: Operator = {}
    for operator in operators:
        for word, coefficient in operator.items():
            output[word] = _poly_add(output.get(word, {}), coefficient)
    return _normalize(output)


def _scale(operator: Operator, scalar: int) -> Operator:
    return {
        word: _poly_scale(coefficient, scalar)
        for word, coefficient in operator.items()
        if _poly_scale(coefficient, scalar)
    }


def _compose(outer: Operator, inner: Operator) -> Operator:
    output: Operator = {}
    for outer_word, outer_coefficient in outer.items():
        for inner_word, inner_coefficient in inner.items():
            word = outer_word + inner_word
            output[word] = _poly_add(
                output.get(word, {}),
                _poly_multiply(outer_coefficient, inner_coefficient),
            )
    return _normalize(output)


def _load_operator(path: Path) -> Matrix:
    record = json.loads(path.read_text())
    body = {key: value for key, value in record.items() if key != "sha256"}
    if record.get("sha256") != _digest(body):
        raise AssertionError(f"internal operator hash drifted: {path}")
    if record.get("shape") != [104, 104]:
        raise AssertionError(f"operator shape drifted: {path}")
    result = _zero(104, 104)
    seen: set[tuple[int, int]] = set()
    for row, column, terms in record["entries"]:
        if (row, column) in seen:
            raise AssertionError("duplicate sparse coordinate")
        seen.add((row, column))
        operator: Operator = {}
        for exponents, coefficient_text in terms:
            word = tuple(
                axis
                for axis, count in enumerate(exponents)
                for _ in range(count)
            )
            expression = sp.sympify(
                coefficient_text, locals={"alpha_B": ALPHA, "u": U, "v": V}
            )
            operator[word] = _poly_add(
                operator.get(word, {}), _polynomial(expression)
            )
        result[row][column] = _normalize(operator)
    return result


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    right_sparse = [
        [(column, operator) for column, operator in enumerate(row) if operator]
        for row in right
    ]
    result = _zero(len(left), len(right[0]))
    for row, values in enumerate(left):
        accumulators: dict[int, list[Operator]] = {}
        for middle, outer in enumerate(values):
            if not outer:
                continue
            for column, inner in right_sparse[middle]:
                accumulators.setdefault(column, []).append(
                    _compose(outer, inner)
                )
        for column, operators in accumulators.items():
            result[row][column] = _add(*operators)
    return result


def _subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            _add(left[row][column], _scale(right[row][column], -1))
            for column in range(len(left[0]))
        ]
        for row in range(len(left))
    ]


def _representation() -> tuple[sp.Matrix, ...]:
    identity = sp.eye(3)
    d1 = sp.Matrix([[0, 0, 0], [0, 0, -3], [0, 1, 0]])
    d2 = sp.Matrix([[0, 0, 3], [0, 0, 0], [-1, 0, 0]])
    d3 = sp.Matrix([[0, -3, 0], [3, 0, 0], [0, 0, 0]])
    if not (
        d1 * d2 - d2 * d1 == d3
        and d2 * d3 - d3 * d2 == 3 * d1
        and d3 * d1 - d1 * d3 == 3 * d2
    ):
        raise AssertionError("independent representation check failed")
    return identity, d1, d2, d3


def _evaluate(
    operator: Operator, representation: tuple[sp.Matrix, ...]
) -> sp.Matrix:
    result = sp.zeros(3)
    for word, polynomial in operator.items():
        coefficient = sum(
            sp.Rational(value.numerator, value.denominator)
            * 2 ** monomial[0]
            * 1 ** monomial[1]
            * 3 ** monomial[2]
            for monomial, value in polynomial.items()
        )
        represented = sp.eye(3)
        for axis in word:
            represented *= representation[axis]
        result += coefficient * represented
    return result


def _block(matrix: Matrix, source_degree: int, shift: int) -> sp.Matrix:
    representation = _representation()
    rows = [
        index
        for index, degree in enumerate(DEGREES)
        if degree == source_degree + shift
    ]
    columns = [
        index for index, degree in enumerate(DEGREES)
        if degree == source_degree
    ]
    result = sp.zeros(3 * len(rows), 3 * len(columns))
    for local_row, row in enumerate(rows):
        for local_column, column in enumerate(columns):
            result[
                3 * local_row:3 * (local_row + 1),
                3 * local_column:3 * (local_column + 1),
            ] = _evaluate(matrix[row][column], representation)
    return result


def _check_minor(matrix: sp.Matrix, witness: dict[str, Any]) -> None:
    rows = witness["pivot_rows"]
    columns = witness["pivot_columns"]
    determinant = sp.factor(matrix.extract(rows, columns).det())
    if matrix.rank() != witness["rank"]:
        raise AssertionError("represented block rank drifted")
    if str(determinant) != witness["determinant"] or determinant == 0:
        raise AssertionError("represented pivot minor drifted")


def verify() -> None:
    certificate = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)

    for ref in certificate["dependency_refs"].values():
        path = ROOT / ref["path"]
        if _sha(path) != ref["sha256"]:
            raise AssertionError(f"dependency hash drifted: {path}")
    for relative, digest in certificate["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source hash drifted: {relative}")
    payload_ref = certificate["exact_witness_payload"]
    if _sha(ROOT / payload_ref["path"]) != payload_ref["sha256"]:
        raise AssertionError("exact witness payload hash drifted")

    q_cauchy = _load_operator(Q_CAUCHY)
    a104 = _load_operator(A104)
    square = _multiply(q_cauchy, q_cauchy)
    commutator = _subtract(
        _multiply(a104, q_cauchy), _multiply(q_cauchy, a104)
    )
    if sum(bool(operator) for row in square for operator in row) != 157:
        raise AssertionError("independent square replay failed")
    if sum(bool(operator) for row in commutator for operator in row) != 207:
        raise AssertionError("independent commutator replay failed")

    blocks = {
        **{
            name: _block(square, degree, 2)
            for name, degree in (
                ("degree_minus1_to_plus1", -1),
                ("degree_0_to_plus2", 0),
            )
        },
        **{
            name: _block(commutator, degree, 1)
            for name, degree in (
                ("degree_minus1_to_0", -1),
                ("degree_0_to_plus1", 0),
                ("degree_plus1_to_plus2", 1),
            )
        },
    }
    for name in ("degree_minus1_to_plus1", "degree_0_to_plus2"):
        _check_minor(blocks[name], payload["square_blocks"][name])
    for name in (
        "degree_minus1_to_0",
        "degree_0_to_plus1",
        "degree_plus1_to_plus2",
    ):
        _check_minor(blocks[name], payload["commutator_blocks"][name])

    square_ranks = [
        payload["square_blocks"]["degree_minus1_to_plus1"]["rank"],
        payload["square_blocks"]["degree_0_to_plus2"]["rank"],
    ]
    lower_bound = certificate["extension_lower_bound"]
    if (
        square_ranks,
        (square_ranks[0] + 2) // 3,
        (square_ranks[1] + 2) // 3,
        lower_bound["total_added_rows_at_least"],
    ) != ([13, 3], 5, 1, 6):
        raise AssertionError("degreewise carrier lower bound failed")

    for forbidden in (
        "BERGER_6_ROW_EXTENSION_SUFFICIENT",
        "BERGER_ALTERNATIVE_COMPANION_NO_GO",
        "BERGER_CAUCHY_KREIN_FORM",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    ):
        if certificate["claim_flags"][forbidden]:
            raise AssertionError(f"forbidden promotion: {forbidden}")


if __name__ == "__main__":
    verify()
    print("independent Berger q26 Cauchy BV carrier obstruction audit: PASS")

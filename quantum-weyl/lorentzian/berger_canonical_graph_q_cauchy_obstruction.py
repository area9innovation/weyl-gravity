"""Exact obstruction to the canonical Berger companion BRST graph lift.

The retained differential ``q26`` admits a tautological nilpotent lift through
the solution graph of each second-order companion.  This module tests whether
that lift descends to the frozen 104-row stationary Cauchy evolution.  It does
not search the space of corrected companion lifts.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from transfer import berger_retained_q1_import as Q1
from transfer.berger_gauge_fixed_nonminimal_import import (
    _adjoint_transpose,
    _zero,
)

from . import metric_lower_by_two_biwave_import as LOWER
from .berger_a104_endpoint_completion import (
    CLASSICAL_EXPORT,
    GENERATED as A104_GENERATED,
    _load_hashed_operator,
)
from .berger_a104_cauchy_operator_preflight import _matrix_record


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A104_CERTIFICATE = HERE / "certificates/BERGER_A104_ENDPOINT_COMPLETION.json"
A104_OPERATOR = A104_GENERATED / "global_A104.json"
Q1_CERTIFICATE = (
    ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
)
Q1_SCHEMA = (
    ROOT / "d_quotient_classical/schema/berger-retained-minimal-operator-v1.schema.json"
)
Q1_LAYOUT = (
    ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
)
Q1_IMPORT = (
    ROOT
    / "quantum-weyl/transfer/certificates/BERGER_RETAINED_MINIMAL_Q1_IMPORT.json"
)
GENERATED = HERE / "generated/berger_canonical_graph_q_cauchy_obstruction"
OUTPUT = HERE / "certificates/BERGER_CANONICAL_GRAPH_Q_CAUCHY_OBSTRUCTION.json"
REPORT = HERE.parent / "reports/berger-canonical-graph-q-cauchy-obstruction.md"


PRIMARY_INDICES = tuple(
    list(range(0, 3))
    + list(range(6, 16))
    + list(range(26, 36))
    + list(range(46, 49))
)
AUXILIARY_INDICES = tuple(
    list(range(3, 6))
    + list(range(16, 26))
    + list(range(36, 46))
    + list(range(49, 52))
)
DEGREES_26 = tuple([-1] * 3 + [0] * 10 + [1] * 10 + [2] * 3)
DEGREES_52 = tuple(
    [-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6
)
DEGREES_104 = DEGREES_52 + DEGREES_52


Monomial = tuple[int, int, int]
Polynomial = dict[Monomial, Fraction]
Operator = dict[tuple[int, ...], Polynomial]
Matrix = list[list[Operator]]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _polynomial(value: sp.Expr | Polynomial) -> Polynomial:
    """Convert once to sparse QQ[alpha_B,u,v] coefficient arithmetic."""

    if isinstance(value, dict):
        return {monomial: coefficient for monomial, coefficient in value.items() if coefficient}
    result: Polynomial = {}
    polynomial = sp.Poly(sp.expand(value), Q1.ALPHA_B, Q1.U, Q1.V, domain=sp.QQ)
    for monomial, coefficient in polynomial.terms():
        result[monomial] = Fraction(int(coefficient.p), int(coefficient.q))
    return result


def _polynomial_add(*values: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for value in values:
        for monomial, coefficient in value.items():
            result[monomial] = result.get(monomial, Fraction()) + coefficient
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def _polynomial_scale(value: Polynomial, scalar: Fraction) -> Polynomial:
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in value.items()
        if scalar * coefficient
    }


def _polynomial_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                left_monomial[index] + right_monomial[index] for index in range(3)
            )
            result[monomial] = (
                result.get(monomial, Fraction())
                + left_coefficient * right_coefficient
            )
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


@lru_cache(maxsize=None)
def _word_reduction(word: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], tuple[tuple[Monomial, Fraction], ...]], ...]:
    return tuple(
        (reduced, tuple(sorted(_polynomial(factor).items())))
        for reduced, factor in Q1._reduce_word(word)
    )


def _polynomial_expression(value: Polynomial) -> sp.Expr:
    return sp.Add(
        *(
            sp.Rational(coefficient.numerator, coefficient.denominator)
            * Q1.ALPHA_B ** monomial[0]
            * Q1.U ** monomial[1]
            * Q1.V ** monomial[2]
            for monomial, coefficient in sorted(value.items())
        )
    )


def _normalize(terms: Operator) -> Operator:
    output: Operator = {}
    for word, coefficient in terms.items():
        coefficient = _polynomial(coefficient)
        for reduced, factor_items in _word_reduction(word):
            factor = dict(factor_items)
            output[reduced] = _polynomial_add(
                output.get(reduced, {}),
                _polynomial_multiply(coefficient, factor),
            )
    return {
        word: value for word, value in sorted(output.items()) if value
    }


def _add(*operators: Operator) -> Operator:
    terms: Operator = {}
    for operator in operators:
        for word, coefficient in operator.items():
            terms[word] = _polynomial_add(terms.get(word, {}), coefficient)
    return _normalize(terms)


def _scale(operator: Operator, coefficient: int | Fraction) -> Operator:
    scalar = Fraction(coefficient)
    return {
        word: _polynomial_scale(value, scalar)
        for word, value in operator.items()
        if _polynomial_scale(value, scalar)
    }


def _compose(outer: Operator, inner: Operator) -> Operator:
    products: Operator = {}
    for outer_word, outer_coefficient in outer.items():
        for inner_word, inner_coefficient in inner.items():
            word = outer_word + inner_word
            products[word] = _polynomial_add(
                products.get(word, {}),
                _polynomial_multiply(outer_coefficient, inner_coefficient),
            )
    return _normalize(products)


def _canonical_symbols(matrix: Matrix) -> Matrix:
    canonical = {"u": Q1.U, "v": Q1.V, "alpha_B": Q1.ALPHA_B}
    result = _zero(len(matrix), len(matrix[0]))
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            converted: Operator = {}
            for word, coefficient in operator.items():
                substitutions = {
                    symbol: canonical[symbol.name]
                    for symbol in coefficient.free_symbols
                    if symbol.name in canonical and symbol != canonical[symbol.name]
                }
                converted[word] = _polynomial(coefficient.xreplace(substitutions))
            result[row][column] = _normalize(converted)
    return result


def _identity(rank: int) -> Matrix:
    result = _zero(rank, rank)
    for index in range(rank):
        result[index][index] = {(): {(0, 0, 0): Fraction(1)}}
    return result


def _embed(
    target: Matrix,
    block: Matrix,
    row_indices: tuple[int, ...] | range,
    column_indices: tuple[int, ...] | range,
) -> None:
    rows = tuple(row_indices)
    columns = tuple(column_indices)
    if len(block) != len(rows) or any(len(row) != len(columns) for row in block):
        raise ValueError("PBW block embedding shape mismatch")
    for local_row, global_row in enumerate(rows):
        for local_column, global_column in enumerate(columns):
            target[global_row][global_column] = block[local_row][local_column]


def _sparse_multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("PBW matrix multiplication shape mismatch")
    right_rows = [
        [(column, operator) for column, operator in enumerate(row) if operator]
        for row in right
    ]
    result = _zero(len(left), len(right[0]))
    for row, values in enumerate(left):
        accumulators: dict[int, list[Operator]] = {}
        for middle, outer in enumerate(values):
            if not outer:
                continue
            for column, inner in right_rows[middle]:
                accumulators.setdefault(column, []).append(_compose(outer, inner))
        for column, terms in accumulators.items():
            result[row][column] = _add(*terms)
    return result


def _subtract(left: Matrix, right: Matrix) -> Matrix:
    if len(left) != len(right) or len(left[0]) != len(right[0]):
        raise ValueError("PBW matrix subtraction shape mismatch")
    return [
        [
            _add(left[row][column], _scale(right[row][column], -1))
            for column in range(len(left[0]))
        ]
        for row in range(len(left))
    ]


def _is_zero(matrix: Matrix) -> bool:
    return all(not operator for row in matrix for operator in row)


def _load_record(record: dict[str, Any], shape: tuple[int, int]) -> Matrix:
    body = {key: value for key, value in record.items() if key != "sha256"}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if record.get("sha256") != digest or record.get("shape") != list(shape):
        raise ValueError("factor record shape or internal hash drifted")
    matrix = _zero(*shape)
    for row, column, terms in record["entries"]:
        operator: Operator = {}
        for exponents, coefficient_text in terms:
            word = tuple(
                axis for axis, count in enumerate(exponents) for _ in range(count)
            )
            coefficient = sp.sympify(
                coefficient_text,
                locals={"u": Q1.U, "v": Q1.V, "alpha_B": Q1.ALPHA_B},
            )
            operator[word] = _polynomial_add(
                operator.get(word, {}), _polynomial(coefficient)
            )
        matrix[row][column] = _normalize(operator)
    return matrix


def _load_q26() -> Matrix:
    payload = json.loads(Q1_CERTIFICATE.read_text())
    schema = json.loads(Q1_SCHEMA.read_text())
    layout = json.loads(Q1_LAYOUT.read_text())
    imported = json.loads(Q1_IMPORT.read_text())
    Q1.validate_classical_retained_q1(payload, schema, layout)
    expected = imported["provenance"]["classical_sources"]["operator_certificate"]
    if expected["sha256"] != _sha256(Q1_CERTIFICATE):
        raise ValueError("retained q1 import and working certificate diverged")
    gauge_raw, _ = Q1._load_record(
        "K_spatial", payload["q1_blocks"]["K_spatial"]
    )
    hessian_raw, _ = Q1._load_record(
        "H_retained", payload["q1_blocks"]["H_retained"]
    )
    noether_raw, _ = Q1._load_record(
        "minus_K_spatial_sharp",
        payload["q1_blocks"]["minus_K_spatial_sharp"],
    )
    gauge = _canonical_symbols(gauge_raw)
    hessian = _canonical_symbols(hessian_raw)
    noether = _canonical_symbols(noether_raw)
    q26 = _zero(26, 26)
    _embed(q26, gauge, range(3, 13), range(0, 3))
    _embed(q26, hessian, range(13, 23), range(3, 13))
    _embed(q26, noether, range(23, 26), range(13, 23))
    if not _is_zero(_sparse_multiply(q26, q26)):
        raise ValueError("assembled retained q26 is not nilpotent")
    return q26


def _target_auxiliary_factor() -> Matrix:
    export = json.loads(CLASSICAL_EXPORT.read_text())
    factors = export["factor_records"]
    ghost = _load_record(factors["F_spatial_K_spatial"], (3, 3))
    identity = _load_record(
        factors["Box_1_spatial_covector_formal_adjoint"], (3, 3)
    )
    lower_source = LOWER._git_json(LOWER.CERTIFICATE)
    references = lower_source["normal_form"]["artifacts"]
    metric_raw = LOWER._load_artifact(
        references["rough_tensor_wave"], "rough_tensor_wave"
    )
    metric = _canonical_symbols(metric_raw)
    metric_antifield = _canonical_symbols(_adjoint_transpose(metric_raw))
    factor = _zero(26, 26)
    _embed(factor, ghost, range(0, 3), range(0, 3))
    _embed(factor, metric, range(3, 13), range(3, 13))
    _embed(factor, metric_antifield, range(13, 23), range(13, 23))
    _embed(factor, identity, range(23, 26), range(23, 26))
    return factor


def _build_q52(q26: Matrix, auxiliary_factor: Matrix) -> Matrix:
    primary = _zero(26, 52)
    for row in range(26):
        for column in range(26):
            primary[row][PRIMARY_INDICES[column]] = q26[row][column]
    auxiliary = _sparse_multiply(auxiliary_factor, primary)
    q52 = _zero(52, 52)
    _embed(q52, primary, PRIMARY_INDICES, range(52))
    _embed(q52, auxiliary, AUXILIARY_INDICES, range(52))
    if not _is_zero(_sparse_multiply(q52, q52)):
        raise ValueError("companion q52 is not nilpotent")
    return q52


def _split_time(operator: Operator) -> dict[int, Operator]:
    pieces: dict[int, Operator] = {}
    for word, coefficient in operator.items():
        temporal = word.count(0)
        spatial = tuple(axis for axis in word if axis != 0)
        piece = pieces.setdefault(temporal, {})
        piece[spatial] = _polynomial_add(piece.get(spatial, {}), coefficient)
    return {order: _normalize(piece) for order, piece in pieces.items()}


def _spatialize(q52: Matrix, A104: Matrix) -> Matrix:
    selector = _zero(52, 104)
    _embed(selector, _identity(52), range(52), range(52))
    maximum_time_order = max(
        (word.count(0) for row in q52 for operator in row for word in operator),
        default=0,
    )
    jets = [selector]
    for _ in range(maximum_time_order):
        jets.append(_sparse_multiply(jets[-1], A104))

    top = _zero(52, 104)
    for row, values in enumerate(q52):
        accumulators: dict[int, list[Operator]] = {}
        for source, operator in enumerate(values):
            if not operator:
                continue
            for temporal_order, spatial_operator in _split_time(operator).items():
                for column, jet_operator in enumerate(jets[temporal_order][source]):
                    if jet_operator:
                        accumulators.setdefault(column, []).append(
                            _compose(spatial_operator, jet_operator)
                        )
        for column, terms in accumulators.items():
            top[row][column] = _add(*terms)
    bottom = _sparse_multiply(top, A104)
    return top + bottom


def _degree_plus_one(matrix: Matrix, degrees: tuple[int, ...]) -> bool:
    return all(
        not operator or degrees[row] == degrees[column] + 1
        for row, values in enumerate(matrix)
        for column, operator in enumerate(values)
    )


def _matrix_record_poly(matrix: Matrix) -> dict[str, Any]:
    sympy_matrix = _zero(len(matrix), len(matrix[0]))
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            sympy_matrix[row][column] = {
                word: _polynomial_expression(coefficient)
                for word, coefficient in operator.items()
            }
    return _matrix_record(sympy_matrix)


def _defect_record(matrix: Matrix, degrees: tuple[int, ...]) -> dict[str, Any]:
    entries = [
        (row, column, operator)
        for row, values in enumerate(matrix)
        for column, operator in enumerate(values)
        if operator
    ]
    if not entries:
        return {"nonzero_sparse_entries": 0, "first_witness": None}
    row, column, operator = entries[0]
    terms = [
        {
            "derivative_exponents": [word.count(axis) for axis in range(4)],
            "coefficient": str(sp.factor(_polynomial_expression(coefficient))),
        }
        for word, coefficient in sorted(operator.items())
    ]
    witness = {
        "row": row,
        "column": column,
        "row_degree": degrees[row],
        "column_degree": degrees[column],
        "terms": terms,
    }
    witness["sha256"] = hashlib.sha256(
        json.dumps(witness, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "nonzero_sparse_entries": len(entries),
        "first_witness": witness,
    }


@lru_cache(maxsize=1)
def build() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    a104_certificate = json.loads(A104_CERTIFICATE.read_text())
    if (
        a104_certificate.get("claim_flags", {}).get(
            "BERGER_FULL_A104_CAUCHY_OPERATOR"
        )
        is not True
        or a104_certificate.get("coverage", {}).get("unknown_coordinates") != 0
    ):
        raise ValueError("complete A104 boundary drifted")
    A104 = _canonical_symbols(_load_hashed_operator(A104_OPERATOR, (104, 104)))
    q26 = _load_q26()
    auxiliary_factor = _target_auxiliary_factor()
    q52 = _build_q52(q26, auxiliary_factor)
    q_cauchy = _spatialize(q52, A104)
    q_cauchy_square = _sparse_multiply(q_cauchy, q_cauchy)
    evolution_commutator = _subtract(
        _sparse_multiply(A104, q_cauchy),
        _sparse_multiply(q_cauchy, A104),
    )
    checks = {
        "q26_squared_zero": _is_zero(_sparse_multiply(q26, q26)),
        "q52_has_degree_plus_one": _degree_plus_one(q52, DEGREES_52),
        "q52_squared_zero": _is_zero(_sparse_multiply(q52, q52)),
        "q_Cauchy_has_degree_plus_one": _degree_plus_one(
            q_cauchy, DEGREES_104
        ),
        "candidate_is_exact_stationary_jet_reduction_of_q52": True,
        "candidate_q_Cauchy_squared_zero": _is_zero(q_cauchy_square),
        "full_A104_commutes_with_candidate_q_Cauchy": _is_zero(
            evolution_commutator
        ),
    }
    expected = {
        "q26_squared_zero": True,
        "q52_has_degree_plus_one": True,
        "q52_squared_zero": True,
        "q_Cauchy_has_degree_plus_one": True,
        "candidate_is_exact_stationary_jet_reduction_of_q52": True,
        "candidate_q_Cauchy_squared_zero": False,
        "full_A104_commutes_with_candidate_q_Cauchy": False,
    }
    if checks != expected:
        raise ValueError(f"canonical graph-lift disposition drifted: {checks}")
    q52_record = _matrix_record_poly(q52)
    q_cauchy_record = _matrix_record_poly(q_cauchy)
    result = {
        "schema": "quantum-weyl-berger-canonical-graph-q-cauchy-obstruction-v1",
        "result_id": "BERGER_CANONICAL_GRAPH_Q_CAUCHY_OBSTRUCTION",
        "result_state": "CANONICAL_GRAPH_LIFT_REJECTED_ALTERNATIVE_Q_COMPANION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "classical_commit": a104_certificate["classical_commit"],
        "setting_id": a104_certificate["setting_id"],
        "candidate_definition": {
            "q52": "i_solution q26 p_solution on each degreewise companion graph",
            "q_Cauchy_104": "exact stationary first-jet reduction of q52 using full A104",
            "scope": "THIS_CANONICAL_GRAPH_LIFT_ONLY_NOT_ALL_LOCAL_COMPANION_LIFTS",
        },
        "exact_checks": checks,
        "counts": {
            "q52_nonzero_sparse_entries": len(q52_record["entries"]),
            "candidate_q_Cauchy_nonzero_sparse_entries": len(
                q_cauchy_record["entries"]
            ),
        },
        "defects": {
            "candidate_q_Cauchy_square": _defect_record(
                q_cauchy_square, DEGREES_104
            ),
            "A104_candidate_q_Cauchy_commutator": _defect_record(
                evolution_commutator, DEGREES_104
            ),
        },
        "minimal_missing_carrier": {
            "status": "EXACTLY_IDENTIFIED",
            "object": "a q26-compatible companion/Cauchy BRST lift for the frozen A104, or a corrected BRST-compatible companion witness with its induced A104",
            "required_checks": [
                "q_Cauchy_has_degree_plus_one",
                "q_Cauchy_squared_zero",
                "full_A104_supercommutes_with_q_Cauchy",
                "compatibility_with_the_retained_q26_solution_map",
            ],
        },
        "claim_flags": {
            "BERGER_FULL_A104_CAUCHY_OPERATOR": True,
            "BERGER_CANONICAL_GRAPH_Q_CAUCHY_LIFT_REJECTED": True,
            "BERGER_Q_CAUCHY_104": False,
            "BERGER_CAUCHY_KREIN_FORM": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_Q26_COMPATIBLE_COMPANION_CAUCHY_BRST_LIFT",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC plus LORENTZIAN-CAUSAL audit rejects only "
            "the tautological solution-graph lift of q26 through the frozen A104: its "
            "stationary Cauchy reduction has nonzero square and evolution commutator. "
            "It is not a nonexistence theorem for corrected local companion lifts and "
            "does not invalidate the independently certified 26-row causal Green "
            "homotopy, construct a Cauchy/Krein form, a Hadamard state, renormalized "
            "products, a QME or a quantum theory."
        ),
    }
    return result, {
        "candidate_q52_companion": q52_record,
        "rejected_candidate_q_Cauchy_104": q_cauchy_record,
    }


if __name__ == "__main__":
    result, _artifacts = build()
    print(json.dumps(result, indent=2, sort_keys=True))

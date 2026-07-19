#!/usr/bin/env python3
"""Project the physical three-H1 triangle onto the scalar-flat CPT carriers.

The imported same-gauge physical Hessian is quadratic in its incoming loop
momentum.  This module therefore uses a small exact sparse polynomial algebra
instead of expanding raw tensor graphs or repeatedly factoring SymPy
expressions.  It reconstructs the complete alpha polynomial on 28
box-unisolvent momentum fixtures, solves the scalar-flat carrier quotient, and
checks the result on two unseen momentum fixtures.  The fixture calculations
are content-addressed under the ignored build directory so an interrupted
exact run can resume without weakening the replay.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, TypeAlias

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_ghost_n3_five_carrier_projection import (
    A1,
    A2,
    CHANNELS,
    DERIVATIVE_ORDERS,
    MOMENTUM_FIXTURES,
    _carrier_system,
    _fixture_momenta,
    _homogeneous_monomials,
    _q,
    _transverse_tracefree_basis,
)
from .generic_background_physical_hessian_n3_triangle_fixture import (
    INTEGRATED_WICK_COEFFICIENTS,
    SCALAR_FLAT_ROW_FORMULAS,
    TRACELESS_BASIS,
    TRACELESS_GRAM_INVERSE,
    _linearized_riemann,
)


HERE = Path(__file__).resolve().parent
QROOT = HERE.parents[1]
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-n3-five-carrier-projection-v1.schema.json"
CACHE_DIRECTORY = ROOT / "build/quantum-weyl-physical-n3-five-carrier"
COORDINATE_ENGINE_VERSION = "physical-hessian-n3-five-carrier-coordinate-v2"
DEPENDENCIES = {
    "physical_H1": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "physical_interior_fixture": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE.json",
    "carrier_manifest": QROOT / "transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
    "K_Ricci_crosswalk": QROOT / "transfer/certificates/SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK.json",
    "ghost_carrier_section": HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json",
}

# Degree-six box interpolation requires 28 fixtures.  The first ten are the
# already-certified degree-three fixtures.  The additional fixtures were
# selected deterministically (seed 120731) by modular rank growth and are
# independently checked over Q before use.
PHYSICAL_MOMENTUM_FIXTURES: tuple[
    tuple[tuple[int, ...], tuple[int, ...]], ...
] = MOMENTUM_FIXTURES + (
    ((4, -4, 2, -1), (1, 4, -4, -2)),
    ((0, 2, 4, 1), (2, -1, -4, 2)),
    ((-4, 0, -2, 2), (-3, -3, 3, 3)),
    ((-2, 2, 0, -4), (-1, 3, 3, -3)),
    ((3, -4, -2, -3), (-4, -1, -4, 2)),
    ((4, -3, -3, 2), (-2, 2, -4, -1)),
    ((4, 0, 2, -4), (2, 2, -4, 3)),
    ((-4, 3, -3, 0), (2, -1, -2, 1)),
    ((1, 1, -1, -1), (-2, -1, 2, 0)),
    ((2, -2, -2, -3), (0, -2, 4, 2)),
    ((-4, 2, -3, -3), (2, 1, -4, -3)),
    ((-4, -4, -2, -4), (-1, -2, 2, 4)),
    ((2, 1, -2, -1), (2, 1, -2, -2)),
    ((-1, 1, 2, -2), (-4, -1, -4, 3)),
    ((-2, -1, -4, -2), (-4, -4, 1, 2)),
    ((-2, 2, 0, 4), (-3, -2, 2, 4)),
    ((-1, 1, -4, 1), (3, 3, 4, 2)),
    ((2, -3, 0, 0), (1, 3, -2, 3)),
)

UNSEEN_MOMENTUM_FIXTURES: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...] = (
    ((1, 2, 0, -1), (-2, 0, 1, 2)),
    ((2, -1, 1, 0), (-1, 2, -2, 1)),
)

QExponent: TypeAlias = tuple[int, int, int, int]
FullExponent: TypeAlias = tuple[int, int, int, int, int, int]
AlphaExponent: TypeAlias = tuple[int, int]
Polynomial: TypeAlias = dict[tuple[int, ...], Fraction]
Q_ZERO: QExponent = (0, 0, 0, 0)
FULL_ZERO: FullExponent = (0, 0, 0, 0, 0, 0)
ALPHA_ZERO: AlphaExponent = (0, 0)
UNISOLVENCE_PRIME = 1_000_003


def _fraction(value: Any) -> Fraction:
    rational = sp.Rational(value)
    return Fraction(int(rational.p), int(rational.q))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value["result_id"]),
        "sha256": _sha256(path),
    }


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _modular_rank(rows: list[list[int]], prime: int) -> int:
    matrix = [[value % prime for value in row] for row in rows]
    rank = 0
    column_count = len(matrix[0]) if matrix else 0
    for column in range(column_count):
        pivot = next(
            (index for index in range(rank, len(matrix)) if matrix[index][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column], -1, prime)
        matrix[rank] = [(value * inverse) % prime for value in matrix[rank]]
        for index in range(len(matrix)):
            if index == rank or not matrix[index][column]:
                continue
            coefficient = matrix[index][column]
            matrix[index] = [
                (left - coefficient * right) % prime
                for left, right in zip(matrix[index], matrix[rank])
            ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def _modular_pivot_rows(rows: list[list[int]], prime: int) -> tuple[int, ...]:
    """Return independent original row indices, certified modulo ``prime``."""

    matrix = [
        [value % prime for value in column]
        for column in zip(*rows)
    ]
    rank = 0
    pivots: list[int] = []
    original_column_count = len(rows)
    for column in range(original_column_count):
        pivot = next(
            (index for index in range(rank, len(matrix)) if matrix[index][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivots.append(column)
        inverse = pow(matrix[rank][column], -1, prime)
        matrix[rank] = [(value * inverse) % prime for value in matrix[rank]]
        for index in range(len(matrix)):
            if index == rank or not matrix[index][column]:
                continue
            coefficient = matrix[index][column]
            matrix[index] = [
                (left - coefficient * right) % prime
                for left, right in zip(matrix[index], matrix[rank])
            ]
        rank += 1
        if rank == len(matrix):
            break
    return tuple(pivots)


def _cache_path(
    fixture: tuple[tuple[int, ...], tuple[int, ...]]
) -> Path:
    key = _canonical_digest(
        {
            "coordinate_engine_version": COORDINATE_ENGINE_VERSION,
            "fixture": fixture,
            "physical_H1_sha256": _sha256(DEPENDENCIES["physical_H1"]),
            "physical_interior_fixture_sha256": _sha256(
                DEPENDENCIES["physical_interior_fixture"]
            ),
            "ghost_carrier_section_sha256": _sha256(
                DEPENDENCIES["ghost_carrier_section"]
            ),
        }
    )
    return CACHE_DIRECTORY / f"{key}.json"


def _serialize_polynomial(polynomial: sp.Poly) -> list[dict[str, Any]]:
    return [
        {"exponents": list(exponents), "coefficient": _q(coefficient)}
        for exponents, coefficient in polynomial.terms()
    ]


def _deserialize_polynomial(terms: list[dict[str, Any]]) -> sp.Poly:
    expression = sum(
        sp.Rational(
            term["coefficient"]["numerator"],
            term["coefficient"]["denominator"],
        )
        * A1 ** term["exponents"][0]
        * A2 ** term["exponents"][1]
        for term in terms
    )
    return sp.Poly(expression, A1, A2)


def _load_coordinate_cache(
    fixture: tuple[tuple[int, ...], tuple[int, ...]]
) -> tuple[tuple[int, int, int], list[sp.Poly], dict[str, Any]] | None:
    path = _cache_path(fixture)
    if not path.exists():
        return None
    value = json.loads(path.read_text())
    if (
        value.get("coordinate_engine_version") != COORDINATE_ENGINE_VERSION
        or value.get("fixture") != [list(vector) for vector in fixture]
        or len(value.get("coordinate_polynomials", [])) != 11
    ):
        return None
    boxes = tuple(value["boxes"])
    return (
        boxes,
        [_deserialize_polynomial(row) for row in value["coordinate_polynomials"]],
        value["ledger"],
    )


def _store_coordinate_cache(
    fixture: tuple[tuple[int, ...], tuple[int, ...]],
    boxes: tuple[int, int, int],
    polynomials: list[sp.Poly],
    ledger: dict[str, Any],
) -> None:
    CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    value = {
        "coordinate_engine_version": COORDINATE_ENGINE_VERSION,
        "fixture": [list(vector) for vector in fixture],
        "boxes": list(boxes),
        "coordinate_polynomials": [
            _serialize_polynomial(polynomial) for polynomial in polynomials
        ],
        "ledger": ledger,
    }
    path = _cache_path(fixture)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _poly_add(*polynomials: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def _poly_scale(polynomial: Polynomial, coefficient: Any) -> Polynomial:
    scalar = _fraction(coefficient)
    if not scalar:
        return {}
    return {
        exponent: scalar * value
        for exponent, value in polynomial.items()
        if scalar * value
    }


def _poly_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    if not left or not right:
        return {}
    result: Polynomial = {}
    for left_exponent, left_value in left.items():
        for right_exponent, right_value in right.items():
            exponent = tuple(
                left_exponent[index] + right_exponent[index]
                for index in range(len(left_exponent))
            )
            result[exponent] = (
                result.get(exponent, Fraction(0)) + left_value * right_value
            )
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def _poly_power(polynomial: Polynomial, power: int) -> Polynomial:
    result: Polynomial = {tuple(0 for _ in next(iter(polynomial))): Fraction(1)}
    for _ in range(power):
        result = _poly_multiply(result, polynomial)
    return result


def _q_constant(value: Any) -> Polynomial:
    coefficient = _fraction(value)
    return {Q_ZERO: coefficient} if coefficient else {}


def _q_linear(vector: Iterable[Any]) -> Polynomial:
    result: Polynomial = {}
    for index, value in enumerate(vector):
        coefficient = _fraction(value)
        if coefficient:
            exponent = [0, 0, 0, 0]
            exponent[index] = 1
            result[tuple(exponent)] = coefficient
    return result


def _q_quadratic(matrix: sp.Matrix) -> Polynomial:
    result: Polynomial = {}
    for first in range(4):
        for second in range(4):
            coefficient = _fraction(matrix[first, second])
            if not coefficient:
                continue
            exponent = [0, 0, 0, 0]
            exponent[first] += 1
            exponent[second] += 1
            key = tuple(exponent)
            result[key] = result.get(key, Fraction(0)) + coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def _shift_q_polynomial(polynomial: Polynomial, shift: sp.Matrix) -> Polynomial:
    result: Polynomial = {}
    coordinate_polynomials = []
    for index in range(4):
        unit = [0, 0, 0, 0]
        unit[index] = 1
        coordinate_polynomials.append(
            _poly_add(_q_linear(unit), _q_constant(shift[index]))
        )
    for exponent, coefficient in polynomial.items():
        term: Polynomial = {Q_ZERO: coefficient}
        for index, power in enumerate(exponent):
            for _ in range(power):
                term = _poly_multiply(term, coordinate_polynomials[index])
        result = _poly_add(result, term)
    return result


def _riemann_bilinear(
    left: sp.Matrix, riemann: list, right: sp.Matrix
) -> sp.Rational:
    return sp.Rational(
        sum(
            left[m, n] * riemann[m][a][n][b] * right[a, b]
            for m in range(4)
            for a in range(4)
            for n in range(4)
            for b in range(4)
        )
    )


def _seed_q_polynomial(
    momentum: sp.Matrix,
    ricci: sp.Matrix,
    riemann: list,
    left: sp.Matrix,
    right: sp.Matrix,
) -> Polynomial:
    k = momentum
    k2 = k.dot(k)
    tr_ricci_right = sp.trace(ricci.T * right)
    tr_ricci_left = sp.trace(ricci.T * left)
    left_right = sp.trace(left.T * right)
    riemann_row = _riemann_bilinear(left, riemann, right)
    return _poly_add(
        _poly_scale(_q_quadratic(left), -sp.Rational(4, 3) * tr_ricci_right),
        _poly_scale(_q_quadratic(right), -sp.Rational(4, 3) * tr_ricci_left),
        _poly_scale(_q_quadratic(left.T * ricci * right), -2),
        _poly_scale(_q_quadratic(ricci.T * left * right), 4),
        _poly_scale(_q_quadratic(ricci.T * right * left), 4),
        _poly_scale(_q_quadratic(sp.eye(4)), -4 * riemann_row),
        _poly_scale(_q_quadratic(ricci), -2 * left_right),
        _poly_scale(_q_linear(left.T * k), sp.Rational(4, 3) * tr_ricci_right),
        _poly_scale(_q_linear(right.T * ricci.T * left * k), 2),
        _poly_scale(_q_linear(right.T * k), -4 * tr_ricci_left),
        _poly_scale(_q_linear(left.T * ricci * right * k), -4),
        _poly_scale(_q_linear(ricci.T * left * right * k), 4),
        _poly_scale(_q_linear(k), -4 * riemann_row),
        _q_constant(-sp.Rational(4, 3) * (k.T * left * k)[0] * tr_ricci_right),
        _q_constant(-2 * k2 * sp.trace(right.T * ricci * left)),
        _q_constant(-2 * k2 * riemann_row),
    )


def _vertex_q_matrix(momentum: sp.Matrix, ricci: sp.Matrix) -> list[list[Polynomial]]:
    riemann = _linearized_riemann(momentum, ricci)
    covariant: list[list[Polynomial]] = []
    for left in TRACELESS_BASIS:
        row = []
        for right in TRACELESS_BASIS:
            direct = _seed_q_polynomial(momentum, ricci, riemann, left, right)
            adjoint_seed = _seed_q_polynomial(
                -momentum, ricci, riemann, right, left
            )
            adjoint = _shift_q_polynomial(adjoint_seed, momentum)
            row.append(_poly_scale(_poly_add(direct, adjoint), Fraction(1, 2)))
        covariant.append(row)
    return [
        [
            _poly_add(
                *(
                    _poly_scale(covariant[index][column], TRACELESS_GRAM_INVERSE[row, index])
                    for index in range(9)
                )
            )
            for column in range(9)
        ]
        for row in range(9)
    ]


def _routing_coordinates(momentum: list[sp.Matrix], leg: int) -> list[Polynomial]:
    k1, _, k3 = momentum
    constants = (sp.zeros(4, 1), k1, -k3)
    constant = constants[leg]
    result = []
    for index in range(4):
        polynomial: Polynomial = {}
        if constant[index]:
            polynomial[FULL_ZERO] = _fraction(constant[index])
        alpha1_exponent = [0] * 6
        alpha1_exponent[0] = 1
        polynomial[tuple(alpha1_exponent)] = polynomial.get(
            tuple(alpha1_exponent), Fraction(0)
        ) - _fraction(k1[index])
        alpha2_exponent = [0] * 6
        alpha2_exponent[1] = 1
        polynomial[tuple(alpha2_exponent)] = polynomial.get(
            tuple(alpha2_exponent), Fraction(0)
        ) + _fraction(k3[index])
        loop_exponent = [0] * 6
        loop_exponent[index + 2] = 1
        polynomial[tuple(loop_exponent)] = Fraction(1)
        result.append(
            {exponent: coefficient for exponent, coefficient in polynomial.items() if coefficient}
        )
    return result


def _route_q_polynomial(polynomial: Polynomial, coordinates: list[Polynomial]) -> Polynomial:
    result: Polynomial = {}
    for exponent, coefficient in polynomial.items():
        term: Polynomial = {FULL_ZERO: coefficient}
        for index, power in enumerate(exponent):
            for _ in range(power):
                term = _poly_multiply(term, coordinates[index])
        result = _poly_add(result, term)
    return result


def _route_matrix(
    matrix: list[list[Polynomial]], coordinates: list[Polynomial]
) -> list[list[Polynomial]]:
    return [
        [_route_q_polynomial(entry, coordinates) for entry in row]
        for row in matrix
    ]


def _matrix_multiply(
    left: list[list[Polynomial]], right: list[list[Polynomial]]
) -> list[list[Polynomial]]:
    return [
        [
            _poly_add(
                *(
                    _poly_multiply(left[row][index], right[index][column])
                    for index in range(9)
                    if left[row][index] and right[index][column]
                )
            )
            for column in range(9)
        ]
        for row in range(9)
    ]


def _trace_product(
    third: list[list[Polynomial]],
    second: list[list[Polynomial]],
    first: list[list[Polynomial]],
) -> Polynomial:
    product = _matrix_multiply(third, second)
    return _poly_add(
        *(
            _poly_multiply(product[row][column], first[column][row])
            for row in range(9)
            for column in range(9)
            if product[row][column] and first[column][row]
        )
    )


def _wick_alpha_polynomial(polynomial: Polynomial, pair_count: int) -> Polynomial:
    result: Polynomial = {}
    for exponent, coefficient in polynomial.items():
        loop_exponents = exponent[2:]
        if sum(loop_exponents) != 2 * pair_count:
            continue
        multiplicity = 1
        for power in loop_exponents:
            if power % 2:
                multiplicity = 0
                break
            for value in range(power - 1, 0, -2):
                multiplicity *= value
        if multiplicity:
            alpha_exponent = exponent[:2]
            result[alpha_exponent] = result.get(
                alpha_exponent, Fraction(0)
            ) + coefficient * multiplicity
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def _alpha_linear(constant: int, alpha1: int, alpha2: int) -> Polynomial:
    result: Polynomial = {}
    if constant:
        result[ALPHA_ZERO] = Fraction(constant)
    if alpha1:
        result[(1, 0)] = Fraction(alpha1)
    if alpha2:
        result[(0, 1)] = Fraction(alpha2)
    return result


def _delta_polynomial(boxes: tuple[int, int, int]) -> Polynomial:
    alpha0 = _alpha_linear(1, -1, -1)
    alpha1 = _alpha_linear(0, 1, 0)
    alpha2 = _alpha_linear(0, 0, 1)
    return _poly_add(
        _poly_scale(_poly_multiply(alpha0, alpha1), boxes[0]),
        _poly_scale(_poly_multiply(alpha1, alpha2), boxes[1]),
        _poly_scale(_poly_multiply(alpha2, alpha0), boxes[2]),
    )


def _common_numerator(
    third: list[list[Polynomial]],
    second: list[list[Polynomial]],
    first: list[list[Polynomial]],
    boxes: tuple[int, int, int],
) -> Polynomial:
    trace = _trace_product(third, second, first)
    alpha_weight = _poly_multiply(
        _poly_multiply(_alpha_linear(1, -1, -1), _alpha_linear(0, 1, 0)),
        _alpha_linear(0, 0, 1),
    )
    delta = _delta_polynomial(boxes)
    result: Polynomial = {}
    for pair_count, coefficient in enumerate(INTEGRATED_WICK_COEFFICIENTS):
        wick = _wick_alpha_polynomial(trace, pair_count)
        contribution = _poly_multiply(
            alpha_weight,
            _poly_multiply(
                _poly_power(delta, pair_count),
                wick,
            ),
        )
        result = _poly_add(result, _poly_scale(contribution, coefficient))
    return result


def _to_sympy_poly(polynomial: Polynomial) -> sp.Poly:
    expression = sum(
        sp.Rational(value.numerator, value.denominator)
        * A1 ** exponent[0]
        * A2 ** exponent[1]
        for exponent, value in polynomial.items()
    )
    return sp.Poly(expression, A1, A2)


def _fixture_coordinate_polynomials(
    fixture: tuple[tuple[int, ...], tuple[int, ...]],
    *,
    use_cache: bool = True,
) -> tuple[tuple[int, int, int], list[sp.Poly], dict[str, Any]]:
    if use_cache:
        cached = _load_coordinate_cache(fixture)
        if cached is not None:
            return cached
    momenta = _fixture_momenta(fixture)
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    choices, matrix, pivot_rows, inverse = _carrier_system(momenta)
    vertex_banks = [
        [_vertex_q_matrix(momentum, tensor) for tensor in basis]
        for momentum, basis in zip(momenta, bases)
    ]
    routed_banks = [
        [
            _route_matrix(vertex, _routing_coordinates(momenta, leg))
            for vertex in bank
        ]
        for leg, bank in enumerate(vertex_banks)
    ]
    boxes = tuple(int(momentum.dot(momentum)) for momentum in momenta)
    amplitudes = []
    for row_index in pivot_rows:
        choice = choices[row_index]
        amplitudes.append(
            _common_numerator(
                routed_banks[2][choice[2]],
                routed_banks[1][choice[1]],
                routed_banks[0][choice[0]],
                boxes,
            )
        )
    coordinates: list[Polynomial] = []
    for coordinate in range(11):
        coordinates.append(
            _poly_add(
                *(
                    _poly_scale(amplitude, inverse[coordinate, index])
                    for index, amplitude in enumerate(amplitudes)
                )
            )
        )
    if any(sum(exponent) > 9 for row in coordinates for exponent in row):
        raise ValueError("physical alpha-degree bound was exceeded")
    polynomials = [_to_sympy_poly(row) for row in coordinates]
    ledger = {
        "momenta": [list(map(int, momentum)) for momentum in momenta],
        "box_invariants": list(boxes),
        "carrier_matrix_shape": list(matrix.shape),
        # _carrier_system already verifies these exact ranks before inversion.
        "carrier_matrix_rank": 10,
        "pivot_tensor_rows": list(pivot_rows),
        "gauge_completed_rank": 11,
        "pivot_amplitude_alpha_term_counts": [len(row) for row in amplitudes],
        "coordinate_alpha_term_counts": [len(row) for row in coordinates],
    }
    if use_cache:
        _store_coordinate_cache(fixture, boxes, polynomials, ledger)
    return boxes, polynomials, ledger


def _term_map(row: dict[str, Any]) -> dict[tuple[int, ...], sp.Rational]:
    return {
        tuple(term["alpha_exponents"] + term["box_exponents"]): sp.Rational(
            term["coefficient"]["numerator"], term["coefficient"]["denominator"]
        )
        for term in row["terms"]
    }


def _interpolate_laurent_rows(
    fixture_rows: list[tuple[tuple[int, int, int], list[sp.Poly]]]
) -> list[dict[str, Any]]:
    """Interpolate after clearing the uniform external-box denominator.

    The scalar-flat TT realization reconstructs each Riemann carrier from
    Ricci through h=2 Ric/k^2.  A three-curvature amplitude may therefore
    contain one inverse box per external leg.  Multiplication by x1*x2*x3
    turns every channel into a homogeneous polynomial of degree 6-d/2.
    """

    output = []
    solvers: dict[
        int,
        tuple[
            tuple[tuple[int, ...], ...],
            sp.Matrix,
            tuple[int, ...],
            sp.Matrix,
        ],
    ] = {}
    for channel_index, (carrier, labels) in enumerate(CHANNELS):
        derivative_order = DERIVATIVE_ORDERS[carrier]
        box_degree = 6 - derivative_order // 2
        if box_degree not in solvers:
            box_monomials = _homogeneous_monomials(box_degree, 3)
            integer_rows = [
                [
                    int(
                        sp.prod(
                            boxes[index] ** exponent[index]
                            for index in range(3)
                        )
                    )
                    for exponent in box_monomials
                ]
                for boxes, _ in fixture_rows
            ]
            if _modular_rank(integer_rows, UNISOLVENCE_PRIME) != len(
                box_monomials
            ):
                raise ValueError(
                    f"physical box basis is not unisolvent for {carrier}"
                )
            pivot_rows = _modular_pivot_rows(integer_rows, UNISOLVENCE_PRIME)
            if len(pivot_rows) != len(box_monomials):
                raise ValueError(f"physical pivot-row selection failed for {carrier}")
            box_matrix = sp.Matrix(integer_rows)
            square = sp.Matrix(
                [list(box_matrix.row(index)) for index in pivot_rows]
            )
            inverse = square.inv()
            solvers[box_degree] = (
                box_monomials,
                box_matrix,
                pivot_rows,
                inverse,
            )
        box_monomials, box_matrix, pivot_rows, inverse = solvers[box_degree]
        alpha_monomials = sorted(
            {
                exponent
                for _, polynomials in fixture_rows
                for exponent, _ in polynomials[channel_index].terms()
            }
        )
        terms = []
        for alpha_exponents in alpha_monomials:
            values = sp.Matrix(
                [
                    sp.prod(boxes)
                    * polynomials[channel_index].coeff_monomial(alpha_exponents)
                    for boxes, polynomials in fixture_rows
                ]
            )
            coefficients = inverse * sp.Matrix([values[index] for index in pivot_rows])
            if box_matrix * coefficients != values:
                raise ValueError(
                    f"physical Laurent interpolation residual for {carrier} {labels}"
                )
            for box_exponents, coefficient in zip(box_monomials, coefficients):
                if coefficient:
                    terms.append(
                        {
                            "alpha_exponents": list(alpha_exponents),
                            "box_exponents": list(box_exponents),
                            "coefficient": _q(coefficient),
                        }
                    )
        output.append(
            {
                "channel_id": f"{carrier}_{''.join(str(index + 1) for index in labels)}",
                "carrier_id": carrier,
                "label_order": [index + 1 for index in labels],
                "explicit_derivative_order": derivative_order,
                "form_factor_box_homogeneity": -(1 + derivative_order // 2),
                "common_denominator_power": 4,
                "box_denominator_exponents": [1, 1, 1],
                "numerator_box_degree": box_degree,
                "maximum_alpha_degree": max(
                    (sum(term["alpha_exponents"]) for term in terms), default=0
                ),
                "term_count": len(terms),
                "terms": terms,
            }
        )
    return output


def _validate_projection_rows(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 11:
        raise ValueError("raw physical projection channel count drifted")
    for row, (carrier, labels) in zip(rows, CHANNELS):
        expected_degree = 6 - DERIVATIVE_ORDERS[carrier] // 2
        if (
            row["carrier_id"] != carrier
            or row["label_order"] != [index + 1 for index in labels]
            or row["box_denominator_exponents"] != [1, 1, 1]
            or row["numerator_box_degree"] != expected_degree
            or row["term_count"] != len(row["terms"])
        ):
            raise ValueError("physical projection row metadata drifted")
        if any(
            sum(term["box_exponents"]) != expected_degree
            or sum(term["alpha_exponents"]) > 9
            for term in row["terms"]
        ):
            raise ValueError("physical projection term grading drifted")
    i28_maps = [_term_map(row) for row in rows[7:10]]
    keys = set().union(*(row.keys() for row in i28_maps))
    if any(sum(row.get(key, sp.S.Zero) for row in i28_maps) != 0 for key in keys):
        raise ValueError("physical symmetric I28 component was not removed")


def _evaluate_projection_row(
    row: dict[str, Any], boxes: tuple[int, int, int]
) -> sp.Poly:
    expression = sp.S.Zero
    for term in row["terms"]:
        coefficient = term["coefficient"]
        box_factor = sp.prod(
            boxes[index] ** exponent
            for index, exponent in enumerate(term["box_exponents"])
        )
        expression += (
            sp.Rational(coefficient["numerator"], coefficient["denominator"])
            * box_factor
            * A1 ** term["alpha_exponents"][0]
            * A2 ** term["alpha_exponents"][1]
        )
    denominator = sp.prod(
        boxes[index] ** exponent
        for index, exponent in enumerate(row["box_denominator_exponents"])
    )
    return sp.Poly(sp.expand(expression / denominator), A1, A2)


def _validate_unseen(
    rows: list[dict[str, Any]],
    fixture: tuple[tuple[int, ...], tuple[int, ...]],
) -> dict[str, Any]:
    boxes, coordinates, ledger = _fixture_coordinate_polynomials(fixture)
    defects = []
    for row, coordinate in zip(rows, coordinates):
        predicted = _evaluate_projection_row(row, boxes)
        if predicted != coordinate:
            defects.append(row["channel_id"])
    if defects:
        raise ValueError(f"unseen physical projection defects: {defects}")
    return {
        **ledger,
        "channel_defect_count": 0,
        "coordinate_polynomial_sha256": _canonical_digest(
            [
                [
                    [list(exponent), _q(coefficient)]
                    for exponent, coefficient in polynomial.terms()
                ]
                for polynomial in coordinates
            ]
        ),
    }


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    physical = values["physical_H1"]
    fixture = values["physical_interior_fixture"]
    manifest = values["carrier_manifest"]
    crosswalk = values["K_Ricci_crosswalk"]
    ghost = values["ghost_carrier_section"]
    if (
        physical.get("claim_flags", {}).get(
            "PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY"
        )
        is not True
        or fixture.get("claim_flags", {}).get(
            "PHYSICAL_H1_FORMAL_ADJOINT_COMPLETION_VERIFIED"
        )
        is not True
        or [row.get("carrier_id") for row in manifest.get("carrier_manifest", [])]
        != ["I10", "I24", "I25", "I28", "I29"]
        or crosswalk.get("linear_crosswalk", {}).get("identity")
        != "K_munu=Ric_munu+O(curvature^2)"
        or ghost.get("quotient_section", {}).get("quotient_dimension") != 10
    ):
        raise ValueError("physical five-carrier dependency drifted")


def build(*, include_unseen: bool = True) -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    _validate_dependencies(dependencies)
    fixture_rows = []
    fixture_ledger = []
    for fixture in PHYSICAL_MOMENTUM_FIXTURES:
        boxes, polynomials, ledger = _fixture_coordinate_polynomials(fixture)
        fixture_rows.append((boxes, polynomials))
        fixture_ledger.append(ledger)
    projection_rows = _interpolate_laurent_rows(fixture_rows)
    _validate_projection_rows(projection_rows)
    unseen = (
        [_validate_unseen(projection_rows, fixture) for fixture in UNSEEN_MOMENTUM_FIXTURES]
        if include_unseen
        else []
    )
    formula_digest = _canonical_digest(projection_rows)
    value = {
        "schema": "quantum-weyl-generic-background-physical-hessian-n3-five-carrier-projection-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION",
        "result_state": "PHYSICAL_THREE_H1_COMMON_NUMERATOR_AND_FIVE_CARRIER_PROJECTION_EXACT",
        "lifecycle_state": "COEFFICIENT_BEARING_PARAMETRIC_PROJECTION_COMPUTED_INTEGRATION_AND_H2_OPEN",
        "classical_commit": dependencies["physical_H1"]["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic nonexceptional momenta on the scalar-flat K/Ricci carrier",
            "input_block": "bosonic (1/6) Tr[(H0^-1 H1)^3] of the same-gauge rank-nine traceless physical Hessian",
            "output": "exact common-Delta alpha polynomials in the symmetric-I28 five-carrier quotient section",
        },
        "exact_polynomial_architecture": {
            "vertex_incoming_momentum_degree": 2,
            "sparse_variables": ["alpha1", "alpha2", "l0", "l1", "l2", "l3"],
            "raw_graph_expansion_avoided": True,
            "formal_adjoint_completion_imported": True,
            "Wick_coefficients_after_Feynman_and_trace_log": [
                _q(value) for value in INTEGRATED_WICK_COEFFICIENTS
            ],
            "alpha0": "1-alpha1-alpha2",
            "Delta": "alpha0*alpha1*x1+alpha1*alpha2*x2+alpha2*alpha0*x3",
            "common_integrand": "(4 pi)^-2 sum_channel I_channel N_channel(alpha,x)/(x1*x2*x3*Delta^4)",
            "maximum_alpha_degree": 9,
            "coordinate_cache_policy": (
                "content-addressed exact fixture coordinates under ignored build/; "
                "cache key includes engine version and dependency hashes"
            ),
            "source_seed_formula_sha256": _canonical_digest(
                [
                    {
                        "term_id": row["term_id"],
                        "coefficient": _q(row["coefficient"]),
                        "formula": row["formula"],
                    }
                    for row in SCALAR_FLAT_ROW_FORMULAS
                ]
            ),
        },
        "quotient_section": {
            "raw_channel_ids": [
                f"{carrier}_{''.join(str(index + 1) for index in labels)}"
                for carrier, labels in CHANNELS
            ],
            "raw_effective_channel_count": 11,
            "quotient_dimension": 10,
            "relation": "CPT-IV (A.35) is the unique null row; the section removes the symmetric I28 component",
            "carrier_derivative_orders": DERIVATIVE_ORDERS,
        },
        "interpolation_certificate": {
            "training_fixture_count": len(fixture_rows),
            "training_fixtures": fixture_ledger,
            "common_box_denominator": "x1*x2*x3 from scalar-flat TT Riemann reconstruction",
            "box_degree_rule": "after clearing x1*x2*x3, 6-d/2 for carrier derivative order d",
            "maximum_box_monomial_count": len(_homogeneous_monomials(6, 3)),
            "unisolvence_modulus": UNISOLVENCE_PRIME,
            "degree_six_box_evaluation_rank_mod_prime": _modular_rank(
                [
                    [
                        int(sp.prod(
                            boxes[index] ** exponent[index]
                            for index in range(3)
                        ))
                        for exponent in _homogeneous_monomials(6, 3)
                    ]
                    for boxes, _ in fixture_rows
                ],
                UNISOLVENCE_PRIME,
            ),
            "alpha_degree_bound": 9,
            "unseen_fixture_count": len(unseen),
            "unseen_fixtures": unseen,
        },
        "projection_rows": projection_rows,
        "formula_digest": formula_digest,
        "claim_flags": {
            "PHYSICAL_H1_FORMAL_ADJOINT_MOMENTUM_VERTEX_VERIFIED": True,
            "PHYSICAL_N3_FULL_ALPHA_POLYNOMIAL_COMPUTED": True,
            "PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED": True,
            "PHYSICAL_N3_UNSEEN_FIXTURES_VERIFIED": include_unseen,
            "PHYSICAL_N3_TRIANGLE_INTEGRATED": False,
            "CURVATURE_SQUARED_H2_IMPORTED": False,
            "PHYSICAL_MIXED_H1_H2_ROWS_COMPUTED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "negative_controls": {
            "raw_graph_expansion": {
                "rejected": True,
                "reason": "the exact quadratic vertex closes in the declared sparse polynomial algebra",
            },
            "promote_projection_to_integrated_form_factors": {
                "rejected": True,
                "reason": "the alpha-simplex integration and H2/mixed physical rows remain open",
            },
        },
        "next_gate": "INTEGRATE_PHYSICAL_N3_FIVE_CARRIER_ALPHA_ROWS_AND_IMPORT_CURVATURE_SQUARED_H2",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate computes the complete common-Delta alpha polynomial of the same-gauge physical three-H1 triangle and projects it exactly onto the scalar-flat five-carrier quotient. It uses the formally self-adjoint rank-nine momentum vertex, 28 box-unisolvent momentum fixtures, the common x1*x2*x3 denominator induced by scalar-flat TT Riemann reconstruction, the unique CPT-IV quotient relation, and two unseen exact fixtures. It does not integrate the alpha-simplex rows, import the curvature-squared H2 layer, compute mixed H1-H2 rows, assemble the complete repository form factors, fix finite normalizations, supply Gamma1 or Q1, authorize residual transfer, or establish a Lorentzian QME, Hadamard state, particle, positivity, scattering, or unitarity theorem."
        ),
    }
    if include_unseen:
        validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    _validate_projection_rows(value["projection_rows"])
    if value["formula_digest"] != _canonical_digest(value["projection_rows"]):
        raise ValueError("physical five-carrier formula digest drifted")
    flags = value["claim_flags"]
    if (
        flags["PHYSICAL_N3_FULL_ALPHA_POLYNOMIAL_COMPUTED"] is not True
        or flags["PHYSICAL_N3_FIVE_CARRIER_PROJECTION_COMPUTED"] is not True
        or flags["PHYSICAL_N3_UNSEEN_FIXTURES_VERIFIED"] is not True
        or flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"] is not False
        or flags["CURVATURE_SQUARED_H2_IMPORTED"] is not False
        or flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"] is not False
        or flags["LORENTZIAN_CERTIFIED"] is not False
    ):
        raise ValueError("physical five-carrier claim boundary drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--check-stored",
        action="store_true",
        help="validate the stored certificate without replaying exact fixtures",
    )
    parser.add_argument("--skip-unseen", action="store_true")
    args = parser.parse_args()
    if args.check_stored:
        validate(json.loads(OUTPUT.read_text()))
        print("PHYSICAL HESSIAN N3 FIVE-CARRIER STORED CERTIFICATE: PASS")
        return 0
    value = build(include_unseen=not args.skip_unseen)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale physical n=3 five-carrier projection: {OUTPUT}")
    print(
        "PHYSICAL HESSIAN N3 FIVE-CARRIER PROJECTION: EXACT PARAMETRIC ROWS PASS; INTEGRATION AND H2 OPEN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

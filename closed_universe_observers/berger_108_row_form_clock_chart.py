#!/usr/bin/env python3
"""Quadratic relational-clock chart for Maxwell and emitter differential forms.

The chart is the degree-two part of pullback by ``y0=x0+Theta(x)``:

    form_dressed = form_raw - L_(Theta e0) form_raw + O(3).

It includes the signed formal-adjoint cotangent lift on the canonical
108-row carrier.  The exported object is the symmetric Taylor coefficient
``F2`` (the coordinate map is ``F=id+F2/2!+...``).
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import (
    generator,
    normalize,
)
from closed_universe_observers.generate_berger_nonlinear_clock_temporal_cotangent_f2_f3 import (
    formal_adjoint_operator,
)


THETA = 16
THETA_DUAL = 38
ONE = (Fraction(1), Fraction(0))

DUAL = {
    THETA: THETA_DUAL,
    **{row: 59 + row - 55 for row in range(55, 59)},
    **{row: 96 + row - 84 for row in range(84, 96)},
}
PAIRING_SIGN = {
    THETA: 1,
    **{row: -1 for row in range(55, 59)},
    **{row: 1 for row in range(84, 96)},
}

# Component orders for the canonical one- and two-form rows.
FORM2 = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))


def constant(value: int) -> replay.Polynomial:
    return normalize([((Fraction(value), Fraction(0)), ())])


def _background(row: int, word: tuple[int, ...]) -> replay.Polynomial:
    return normalize(
        [
            (
                ONE,
                (generator("background", f"row_{row}", spacetime=tuple(word.count(axis) for axis in range(4))),),
            )
        ]
    )


def field_corrections() -> list[tuple[int, int, tuple[int, ...], int, tuple[int, ...], int]]:
    """Return monomials in ``-L_(Theta e0)`` with their polynomial coefficient."""

    terms: list[tuple[int, int, tuple[int, ...], int, tuple[int, ...], int]] = []

    # One-form A: -Theta e0 A_mu - A_0 e_mu Theta.
    for component in range(4):
        target = 55 + component
        terms.append((target, THETA, (), target, (0,), -1))
        terms.append((target, 55, (), THETA, (component,), -1))

    # Each emitter two-form: -Theta e0 K - dTheta wedge i_e0 K.
    for offset in (84, 90):
        for component, (first, second) in enumerate(FORM2):
            target = offset + component
            terms.append((target, THETA, (), target, (0,), -1))
            if first == 0:
                # -(e0 Theta) K_0i
                terms.append((target, THETA, (0,), target, (), -1))
            else:
                # -(ei Theta) K_0j +(ej Theta) K_0i
                k0_second = offset + FORM2.index((0, second))
                k0_first = offset + FORM2.index((0, first))
                terms.append((target, THETA, (first,), k0_second, (), -1))
                terms.append((target, THETA, (second,), k0_first, (), 1))
    return terms


def field_f2_rows() -> dict[int, arity.BilinearRow]:
    """Return the symmetric field half of the Taylor coefficient F2."""

    rows: dict[int, arity.BilinearRow] = defaultdict(dict)
    for output, left, left_word, right, right_word, coefficient in field_corrections():
        arity.add_bilinear_term(
            rows[output],
            (left, left_word, right, right_word),
            constant(coefficient),
        )
        arity.add_bilinear_term(
            rows[output],
            (right, right_word, left, left_word),
            constant(coefficient),
        )
    return {row: value for row, value in rows.items() if value}


def frechet_operator() -> replay.Operator:
    """Frechet derivative of the actual quadratic correction F2/2!."""

    operator: replay.Operator = {}
    for output, left, left_word, right, right_word, coefficient in field_corrections():
        replay.add_operator_term(
            operator,
            (output, left, left_word),
            replay.scale(_background(right, right_word), (Fraction(coefficient), Fraction(0))),
        )
        replay.add_operator_term(
            operator,
            (output, right, right_word),
            replay.scale(_background(left, left_word), (Fraction(coefficient), Fraction(0))),
        )
    return operator


def cotangent_f2_rows() -> dict[int, arity.BilinearRow]:
    """Return ``-S^-1 (D C2)^dagger S`` as a symmetric bilinear tensor."""

    adjoint = formal_adjoint_operator(frechet_operator())
    rows: dict[int, arity.BilinearRow] = defaultdict(dict)
    for (field_output, field_input, dual_word), polynomial in adjoint.items():
        # The adjoint indices are (varied field, original output field).
        output = DUAL[field_output]
        dual_input = DUAL[field_input]
        sign = -PAIRING_SIGN[field_input] * PAIRING_SIGN[field_output]
        for monomial, coefficient in polynomial.items():
            if len(monomial) != 1:
                raise AssertionError("form-clock cotangent coefficient ceased to be linear")
            kind, name, vertical, spacetime = monomial[0]
            if kind != "background" or vertical or not name.startswith("row_"):
                raise AssertionError("unexpected form-clock cotangent coefficient")
            field = int(name[4:])
            field_word = replay.word(spacetime)
            value = replay.scalar_mul(coefficient, (Fraction(sign), Fraction(0)))
            constant = normalize([(value, ())])
            arity.add_bilinear_term(
                rows[output],
                (field, field_word, dual_input, dual_word),
                constant,
            )
            arity.add_bilinear_term(
                rows[output],
                (dual_input, dual_word, field, field_word),
                constant,
            )
    return {row: value for row, value in rows.items() if value}


def f2_rows() -> dict[int, arity.BilinearRow]:
    rows: dict[int, arity.BilinearRow] = defaultdict(dict)
    for block in (field_f2_rows(), cotangent_f2_rows()):
        for output, row in block.items():
            for key, coefficient in row.items():
                arity.add_bilinear_term(rows[output], key, coefficient)
    return {row: value for row, value in sorted(rows.items()) if value}


def _q1_after_f2_row(
    target: int,
    total_degree: arity.Bidegree,
    q1: replay.GradedOperator,
    f2: arity.GradedBilinearRows,
) -> arity.BilinearRow:
    """Return only the ``q1 after F2`` part of the arity-two composition."""

    result: arity.BilinearRow = {}
    indexed = {degree: arity.q1_rows(operator) for degree, operator in q1.items()}
    for q1_degree, unary_rows in indexed.items():
        for f2_degree, binary_rows in f2.items():
            if arity.add_degree(q1_degree, f2_degree) != total_degree:
                continue
            for middle, outer_word, outer_coefficient in unary_rows.get(target, ()):
                for (left, left_word, right, right_word), coefficient in binary_rows.get(middle, {}).items():
                    for (new_left_word, new_right_word), value in arity.apply_output_word(
                        outer_word, coefficient, left_word, right_word
                    ).items():
                        arity.add_bilinear_term(
                            result,
                            (left, new_left_word, right, new_right_word),
                            replay.multiply(outer_coefficient, value),
                        )
    return result


def conjugation_correction(q1: replay.GradedOperator | None = None) -> arity.GradedBilinearRows:
    """Return ``D F2 q1 - q1 F2`` induced by the quadratic chart."""

    q1 = q1 or replay.load_q1()
    f2: arity.GradedBilinearRows = {
        degree: (f2_rows() if degree == (0, 0) else {})
        for degree in arity.SUPPORTED_BIDEGREES
    }
    parity = arity.parities()
    indexed = {degree: arity.q1_rows(operator) for degree, operator in q1.items()}
    result: arity.GradedBilinearRows = {}
    for degree in arity.SUPPORTED_BIDEGREES:
        rows: dict[int, arity.BilinearRow] = {}
        for output in range(108):
            total = arity.arity_two_row(output, degree, q1, f2, parity, indexed)
            q1_after = _q1_after_f2_row(output, degree, q1, f2)
            correction = dict(total)
            for key, coefficient in q1_after.items():
                arity.add_bilinear_term(
                    correction,
                    key,
                    replay.scale(coefficient, (Fraction(-2), Fraction(0))),
                )
            if correction:
                rows[output] = correction
        result[degree] = rows
    return result

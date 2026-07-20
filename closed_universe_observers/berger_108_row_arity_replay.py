#!/usr/bin/env python3
"""Exact sparse composition primitives for the complete Berger 108-row brackets.

The observer payloads have coefficient jets, so the constant-coefficient
``BilinearOperator`` used by the original 64-row calculation is insufficient:
outer PBW words must differentiate both the coefficient and every input slot.
This module implements that differential-coefficient coderivation directly in
the canonical 108-row grammar.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import json
from typing import Iterable

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers import berger_108_row_nonlinear_clock_second_jet as second_jet
from closed_universe_observers.generate_berger_108_row_complete_q2_pbw import PAYLOAD as Q2_PAYLOAD


Bidegree = tuple[int, int]
BilinearKey = tuple[int, tuple[int, ...], int, tuple[int, ...]]
BilinearRow = dict[BilinearKey, replay.Polynomial]
GradedBilinearRows = dict[Bidegree, dict[int, BilinearRow]]
SUPPORTED_BIDEGREES: tuple[Bidegree, ...] = ((0, 0), (1, 0), (0, 1), (1, 1))
EMITTER_SWITCH_CLOCK_RATE = Fraction(3, 4)


def add_degree(left: Bidegree, right: Bidegree) -> Bidegree:
    return left[0] + right[0], left[1] + right[1]


def completed_q1() -> replay.GradedOperator:
    """Load q1 and install the certified nonlinear-clock second-jet correction."""

    value = replay.load_q1()
    correction, _parts = second_jet.candidate_completion(
        value[(0, 0)], value[(1, 0)]
    )
    value[(1, 0)] = replay.add_operators(value[(1, 0)], correction)
    return value


def load_q2(*, sources: set[str] | None = None) -> GradedBilinearRows:
    """Load the source-labelled typed complete q2 payload by first bidegree."""

    document = json.loads(Q2_PAYLOAD.read_text())
    if document["shape"] != [108, 108, 108]:
        raise AssertionError("complete q2 shape changed")
    output: GradedBilinearRows = {degree: defaultdict(dict) for degree in SUPPORTED_BIDEGREES}
    for row in document["rows"]:
        target = row["output"]
        for term in row["terms"]:
            if sources is not None and term["source"] not in sources:
                continue
            key = (
                term["left_input_row"],
                replay.word(term["left_pbw_multiindex"]),
                term["right_input_row"],
                replay.word(term["right_pbw_multiindex"]),
            )
            for degree, coefficient in replay.split_bidegree(replay.polynomial(term)).items():
                current = output[degree][target].get(key, {})
                value = replay.add(current, coefficient)
                if value:
                    output[degree][target][key] = value
                elif key in output[degree][target]:
                    del output[degree][target][key]
    return {
        degree: {row: terms for row, terms in sorted(rows.items()) if terms}
        for degree, rows in output.items()
    }


def parities() -> tuple[int, ...]:
    document = json.loads(replay.COMPONENT.read_text())
    rows = document["carrier_contract"]["rows"]
    if [row["index"] for row in rows] != list(range(108)):
        raise AssertionError("component row order changed")
    return tuple(row["degree"] % 2 for row in rows)


def add_bilinear_term(
    row: BilinearRow,
    key: BilinearKey,
    coefficient: replay.Polynomial,
) -> None:
    value = replay.add(row.get(key, {}), coefficient)
    if value:
        row[key] = value
    elif key in row:
        del row[key]


def specialize_emitter_switch_profiles(value: replay.Polynomial) -> replay.Polynomial:
    """Restrict h_b jets to h_b(Theta_bar), e0 Theta_bar=3/4, ei Theta_bar=0.

    The exact emitter switches are functions of the relational clock rather
    than independent spacetime profiles.  On the pinned homogeneous Berger
    background, spatial switch jets vanish and each temporal derivative
    raises the one-variable switch jet with a factor 3/4.
    """

    terms = []
    rate = (EMITTER_SWITCH_CLOCK_RATE, Fraction(0))
    for monomial, coefficient in value.items():
        factors = []
        current = coefficient
        killed = False
        for kind, name, vertical, spacetime in monomial:
            if kind != "profile":
                factors.append((kind, name, vertical, spacetime))
                continue
            if name not in {"h0", "h1"}:
                factors.append((kind, name, vertical, spacetime))
                continue
            if len(vertical) > 1:
                raise ValueError(f"unsupported emitter switch vertical jet: {vertical}")
            if any(spacetime[axis] for axis in (1, 2, 3)):
                killed = True
                break
            time_order = spacetime[0]
            for _ in range(time_order):
                current = replay.scalar_mul(current, rate)
            vertical_order = (vertical[0] if vertical else 0) + time_order
            factors.append(
                replay.generator(
                    kind,
                    name,
                    (vertical_order,) if vertical_order else (),
                    (0, 0, 0, 0),
                )
            )
        if not killed:
            terms.append((current, factors))
    return replay.normalize(terms)


def specialize_bilinear_rows(
    rows: dict[int, BilinearRow],
) -> dict[int, BilinearRow]:
    """Apply the exact emitter-switch background quotient coefficientwise."""

    output: dict[int, BilinearRow] = {}
    for target, row in rows.items():
        specialized = {
            key: coefficient
            for key, value in row.items()
            if (coefficient := specialize_emitter_switch_profiles(value))
        }
        if specialized:
            output[target] = specialized
    return output


def apply_output_word(
    outer_word: tuple[int, ...],
    coefficient: replay.Polynomial,
    left_word: tuple[int, ...],
    right_word: tuple[int, ...],
) -> dict[tuple[tuple[int, ...], tuple[int, ...]], replay.Polynomial]:
    """Expand ``D_outer(C D_left x D_right y)`` in left-coefficient PBW form."""

    states = {(left_word, right_word): coefficient}
    for axis in reversed(outer_word):
        updated: dict[
            tuple[tuple[int, ...], tuple[int, ...]], replay.Polynomial
        ] = {}
        for (current_left, current_right), current_coefficient in states.items():
            differentiated = replay.derivative(current_coefficient, axis)
            if differentiated:
                key = current_left, current_right
                updated[key] = replay.add(updated.get(key, {}), differentiated)
            for reduced_left, structure_coefficient in replay._pbw_word(
                (axis, *current_left)
            ):
                key = reduced_left, current_right
                contribution = replay.scale(current_coefficient, structure_coefficient)
                updated[key] = replay.add(updated.get(key, {}), contribution)
            for reduced_right, structure_coefficient in replay._pbw_word(
                (axis, *current_right)
            ):
                key = current_left, reduced_right
                contribution = replay.scale(current_coefficient, structure_coefficient)
                updated[key] = replay.add(updated.get(key, {}), contribution)
        states = {key: value for key, value in updated.items() if value}
    return states


def q1_rows(operator: replay.Operator) -> dict[int, list[tuple[int, tuple[int, ...], replay.Polynomial]]]:
    result: dict[int, list[tuple[int, tuple[int, ...], replay.Polynomial]]] = defaultdict(list)
    for (row, column, current_word), coefficient in operator.items():
        result[row].append((column, current_word, coefficient))
    return result


def arity_two_row(
    target: int,
    total_degree: Bidegree,
    q1: replay.GradedOperator,
    q2: GradedBilinearRows,
    parity: tuple[int, ...],
    indexed_q1: dict[Bidegree, dict[int, list[tuple[int, tuple[int, ...], replay.Polynomial]]]] | None = None,
) -> BilinearRow:
    """Return one exact row of ``q1 q2+q2(q1,.)+(-1)^|.|q2(.,q1)``."""

    result: BilinearRow = {}
    indexed_q1 = indexed_q1 or {
        degree: q1_rows(operator) for degree, operator in q1.items()
    }
    for q1_degree, unary_rows in indexed_q1.items():
        for q2_degree, binary_rows in q2.items():
            if add_degree(q1_degree, q2_degree) != total_degree:
                continue

            # q1 after q2: the outer word differentiates the coefficient and
            # is distributed over both binary inputs.
            for middle, outer_word, outer_coefficient in unary_rows.get(target, ()):
                for (left, left_word, right, right_word), coefficient in binary_rows.get(middle, {}).items():
                    for (new_left_word, new_right_word), value in apply_output_word(
                        outer_word, coefficient, left_word, right_word
                    ).items():
                        add_bilinear_term(
                            result,
                            (left, new_left_word, right, new_right_word),
                            replay.multiply(outer_coefficient, value),
                        )

            # q2 after q1 in the first and second slots.
            for (left, left_word, right, right_word), coefficient in binary_rows.get(target, {}).items():
                for new_left, inner_word, inner_coefficient in unary_rows.get(left, ()):
                    for new_word, value in replay.apply_word(
                        left_word, inner_coefficient, inner_word
                    ).items():
                        add_bilinear_term(
                            result,
                            (new_left, new_word, right, right_word),
                            replay.multiply(coefficient, value),
                        )
                sign = (Fraction(-1), Fraction(0)) if parity[left] else replay.ONE_SCALAR
                for new_right, inner_word, inner_coefficient in unary_rows.get(right, ()):
                    for new_word, value in replay.apply_word(
                        right_word, inner_coefficient, inner_word
                    ).items():
                        add_bilinear_term(
                            result,
                            (left, left_word, new_right, new_word),
                            replay.scale(replay.multiply(coefficient, value), sign),
                        )
    return result


def bilinear_summary(rows: dict[int, BilinearRow]) -> dict[str, object]:
    return {
        "operator_key_count": sum(len(row) for row in rows.values()),
        "serialized_term_count": sum(
            len(coefficient) for row in rows.values() for coefficient in row.values()
        ),
        "nonzero_output_rows": sorted(row for row, terms in rows.items() if terms),
        "maximum_total_input_order": max(
            (
                len(left_word) + len(right_word)
                for row in rows.values()
                for _left, left_word, _right, right_word in row
            ),
            default=0,
        ),
    }


def arity_two_degree(
    degree: Bidegree,
    q1: replay.GradedOperator | None = None,
    q2: GradedBilinearRows | None = None,
) -> dict[int, BilinearRow]:
    q1 = q1 or completed_q1()
    q2 = q2 or load_q2()
    parity = parities()
    indexed_q1 = {item: q1_rows(operator) for item, operator in q1.items()}
    return {
        target: defect
        for target in range(108)
        if (defect := arity_two_row(target, degree, q1, q2, parity, indexed_q1))
    }

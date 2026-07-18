"""Action-derived Einstein--Maxwell Taylor operations on the compact product.

This producer targets the complete minimal ``Diff x U(1)`` BV carrier at the
common rational Plebanski--Hacyan fixture.  It deliberately works before the
Einstein--Weyl relative comparison: no target equation or branch label is
used to determine a source coefficient.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product

import sympy as sp

from bridge.einstein_sector.product_taylor_engine import (
    BASE_POINT,
    BZERO,
    COORDINATES,
    JZERO,
    LZERO,
    TZERO,
    BilinearOperator,
    LinearOperator,
    PAIRS,
    PAIR_INDEX,
    TaylorJet,
    TrilinearOperator,
    compose_linear,
    covariant_derivative,
    formal_adjoint_matrix,
    graded_complete_bilinear,
    graded_complete_trilinear,
    metric_geometry,
    negative_transpose_bilinear_left,
    negative_transpose_bilinear_right,
    negative_transpose_trilinear_slot,
    sum_jets,
)


LAMBDA = sp.Rational(1, 2)
KAPPA = sp.Integer(1)
MAGNETIC_P = sp.Integer(1)
METRIC_FIELDS = tuple(range(10))
MAXWELL_FIELDS = tuple(range(10, 14))
GHOSTS = tuple(range(5))
GHOST_SLICE = tuple(range(0, 5))
FIELD_SLICE = tuple(range(5, 19))
EQUATION_SLICE = tuple(range(19, 33))
IDENTITY_SLICE = tuple(range(33, 38))
TOTAL_ROWS = 38
PARITIES = (1,) * 5 + (0,) * 14 + (1,) * 14 + (0,) * 5


def _field_strength() -> dict[tuple[int, int], TaylorJet]:
    output: dict[tuple[int, int], TaylorJet] = {}
    for first, second in product(range(4), repeat=2):
        background = sp.S.Zero
        if (first, second) == (2, 3):
            background = MAGNETIC_P * sp.sin(COORDINATES[2])
        elif (first, second) == (3, 2):
            background = -MAGNETIC_P * sp.sin(COORDINATES[2])
        potential_second = TaylorJet.field(MAXWELL_FIELDS[second])
        potential_first = TaylorJet.field(MAXWELL_FIELDS[first])
        output[(first, second)] = (
            TaylorJet.constant(background)
            + potential_second.derivative(first)
            - potential_first.derivative(second)
        )
    return output


@lru_cache(maxsize=1)
def physical_euler_rows() -> tuple[TaylorJet, ...]:
    geometry = metric_geometry()
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    ricci = geometry["ricci"]
    scalar = geometry["scalar"]
    volume = geometry["volume_ratio"]
    assert isinstance(metric, dict) and isinstance(inverse, dict)
    assert isinstance(ricci, dict) and isinstance(scalar, TaylorJet)
    assert isinstance(volume, TaylorJet)

    field_strength = _field_strength()
    raised_field_strength = {
        (first, second): sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * field_strength[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        for first, second in product(range(4), repeat=2)
    }
    invariant = sum_jets(
        field_strength[(first, second)] * raised_field_strength[(first, second)]
        for first, second in product(range(4), repeat=2)
    )
    stress_lower = {
        (first, second): sum_jets(
            inverse[(left, right)]
            * field_strength[(first, left)]
            * field_strength[(second, right)]
            for left, right in product(range(4), repeat=2)
        )
        - metric[(first, second)] * invariant.scale(sp.Rational(1, 4))
        for first, second in product(range(4), repeat=2)
    }
    einstein_lower = {
        (first, second): ricci[(first, second)]
        - metric[(first, second)] * scalar.scale(sp.Rational(1, 2))
        + metric[(first, second)].scale(LAMBDA)
        for first, second in product(range(4), repeat=2)
    }

    metric_rows = []
    for first, second in PAIRS:
        multiplicity = 1 if first == second else 2
        raised_difference = sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * (stress_lower[(left, right)] - einstein_lower[(left, right)].scale(1 / KAPPA))
            for left, right in product(range(4), repeat=2)
        )
        metric_rows.append(volume * raised_difference.scale(sp.Rational(multiplicity, 2)))

    # The Euler density is represented relative to the fixed product volume
    # sin(theta) dt dx dtheta dphi.  This avoids coordinate-density factors in
    # the exported odd pairing.
    potential_rows = []
    background_measure = sp.sin(COORDINATES[2])
    for target in range(4):
        density = {
            (axis,): volume * raised_field_strength[(axis, target)]
            for axis in range(4)
        }
        divergence = sum_jets(
            (density[(axis,)].scale(background_measure)).derivative(axis)
            for axis in range(4)
        ).scale(1 / background_measure)
        potential_rows.append(divergence)

    rows = tuple((*metric_rows, *potential_rows))
    if len(rows) != 14:
        raise AssertionError("Einstein--Maxwell physical row count drifted")
    for index, row in enumerate(rows):
        background = sp.trigsimp(row.background)
        if background != 0:
            raise AssertionError(f"common product is not on shell in row {index}: {background}")
    return rows


def physical_summary() -> dict[str, object]:
    rows = physical_euler_rows()
    return {
        "row_count": len(rows),
        "q1_term_counts": [len(row.linear.at_base_point().terms) for row in rows],
        "q2_term_counts": [len(row.bilinear.at_base_point().terms) for row in rows],
        "q3_term_counts": [len(row.trilinear.at_base_point().terms) for row in rows],
        "maximum_orders": {
            "q1": max(row.linear.at_base_point().maximum_total_order for row in rows),
            "q2": max(row.bilinear.at_base_point().maximum_total_order for row in rows),
            "q3": max(row.trilinear.at_base_point().maximum_total_order for row in rows),
        },
    }


def gauge_generator() -> tuple[LinearOperator, ...]:
    """Return the covariantized linear Diff x U(1) action on 14 fields."""

    background_metric = sp.diag(-1, 1, 1, sp.sin(COORDINATES[2]) ** 2)
    background_field = sp.zeros(4)
    background_field[2, 3] = MAGNETIC_P * sp.sin(COORDINATES[2])
    background_field[3, 2] = -background_field[2, 3]
    rows: list[LinearOperator] = []
    for first, second in PAIRS:
        terms = []
        for vector in range(4):
            derivative = sp.diff(background_metric[first, second], COORDINATES[vector])
            if derivative != 0:
                terms.append((vector, (), derivative))
            if background_metric[vector, second] != 0:
                terms.append((vector, (first,), background_metric[vector, second]))
            if background_metric[first, vector] != 0:
                terms.append((vector, (second,), background_metric[first, vector]))
        rows.append(LinearOperator.from_terms(terms))
    for component in range(4):
        rows.append(
            LinearOperator.from_terms(
                (
                    *((vector, (), background_field[vector, component]) for vector in range(4)),
                    (4, (component,), sp.S.One),
                )
            )
        )
    return tuple(rows)


def _linear_matrix(rows: tuple[TaylorJet, ...]) -> tuple[tuple[LinearOperator, ...], ...]:
    output = [[LZERO for _ in range(14)] for _ in range(14)]
    for row, jet in enumerate(rows):
        grouped: list[list[tuple[int, tuple[int, ...], sp.Expr]]] = [[] for _ in range(14)]
        for component, word, coefficient in jet.linear.terms:
            grouped[component].append((component, word, coefficient))
        for column in range(14):
            output[row][column] = LinearOperator.from_terms(grouped[column])
    return tuple(tuple(row) for row in output)


def _operator_matrix(rows: tuple[LinearOperator, ...], input_count: int) -> tuple[tuple[LinearOperator, ...], ...]:
    output = [[LZERO for _ in range(input_count)] for _ in rows]
    for row, operator in enumerate(rows):
        grouped: list[list[tuple[int, tuple[int, ...], sp.Expr]]] = [[] for _ in range(input_count)]
        for component, word, coefficient in operator.terms:
            grouped[component].append((component, word, coefficient))
        for column in range(input_count):
            output[row][column] = LinearOperator.from_terms(grouped[column])
    return tuple(tuple(row) for row in output)


def _reindex_linear(operator: LinearOperator, mapping: dict[int, int]) -> LinearOperator:
    return LinearOperator.from_terms((mapping[component], word, coefficient) for component, word, coefficient in operator.terms)


@lru_cache(maxsize=1)
def build_q1() -> tuple[LinearOperator, ...]:
    output = [LZERO for _ in range(TOTAL_ROWS)]
    generator = gauge_generator()
    ghost_map = {index: GHOST_SLICE[index] for index in range(5)}
    field_map = {index: FIELD_SLICE[index] for index in range(14)}
    equation_map = {index: EQUATION_SLICE[index] for index in range(14)}

    for local, operator in enumerate(generator):
        output[FIELD_SLICE[local]] = _reindex_linear(operator, ghost_map)
    for local, row in enumerate(physical_euler_rows()):
        output[EQUATION_SLICE[local]] = _reindex_linear(row.linear, field_map)

    generator_matrix = _operator_matrix(generator, 5)
    adjoint = formal_adjoint_matrix(generator_matrix)
    for ghost in range(5):
        terms = []
        for equation in range(14):
            terms.extend(
                (EQUATION_SLICE[component], word, -coefficient)
                for component, word, coefficient in adjoint[ghost][equation].terms
            )
        output[IDENTITY_SLICE[ghost]] = LinearOperator.from_terms(terms)

    result = tuple(output)
    defects = [compose_linear(row, result).at_base_point() for row in result]
    if any(defect.terms for defect in defects):
        raise AssertionError(
            "Einstein--Maxwell minimal q1 is not nilpotent: "
            + str([(row, len(defect.terms)) for row, defect in enumerate(defects) if defect.terms])
        )
    return result


def row_layout() -> list[dict[str, object]]:
    metric_names = [f"g_{first}{second}" for first, second in PAIRS]
    field_names = [*metric_names, *[f"A_{axis}" for axis in range(4)]]
    ghost_names = [*[f"c_{axis}" for axis in range(4)], "lambda_cov"]
    rows = []
    for index, name in enumerate(ghost_names):
        rows.append({"index": GHOST_SLICE[index], "row_id": name, "degree": -1, "parity": "odd", "bundle_id": "Diff_ghost" if index < 4 else "U1_covariant_ghost", "dual_row": IDENTITY_SLICE[index]})
    for index, name in enumerate(field_names):
        rows.append({"index": FIELD_SLICE[index], "row_id": name, "degree": 0, "parity": "even", "bundle_id": "symmetric_covariant_2" if index < 10 else "U1_potential_covector", "dual_row": EQUATION_SLICE[index]})
    for index, name in enumerate(field_names):
        rows.append({"index": EQUATION_SLICE[index], "row_id": name + "_star", "degree": 1, "parity": "odd", "bundle_id": "metric_Euler_density" if index < 10 else "Maxwell_Euler_density", "dual_row": FIELD_SLICE[index]})
    for index, name in enumerate(ghost_names):
        rows.append({"index": IDENTITY_SLICE[index], "row_id": name + "_star", "degree": 2, "parity": "even", "bundle_id": "Diff_identity_density" if index < 4 else "U1_identity_density", "dual_row": GHOST_SLICE[index]})
    return sorted(rows, key=lambda row: int(row["index"]))


def pairing_terms() -> list[dict[str, object]]:
    terms = []
    for left, right in [*zip(GHOST_SLICE, IDENTITY_SLICE), *zip(FIELD_SLICE, EQUATION_SLICE)]:
        terms.append({"left_row": left, "right_row": right, "coefficient": "1"})
        terms.append({"left_row": right, "right_row": left, "coefficient": "-1"})
    return terms


def _shift_bilinear(operator: BilinearOperator, mapping: dict[int, int]) -> BilinearOperator:
    return BilinearOperator.from_terms(
        (mapping[left], left_word, mapping[right], right_word, coefficient)
        for left, left_word, right, right_word, coefficient in operator.terms
    )


def _shift_trilinear(operator: TrilinearOperator, mapping: dict[int, int]) -> TrilinearOperator:
    return TrilinearOperator.from_terms(
        (
            mapping[first], first_word,
            mapping[second], second_word,
            mapping[third], third_word,
            coefficient,
        )
        for first, first_word, second, second_word, third, third_word, coefficient in operator.terms
    )


def _ghost_bracket() -> tuple[BilinearOperator, ...]:
    """Taylor coefficient of the coordinate Diff ghost bracket."""

    outputs = [BZERO for _ in range(5)]
    for target in range(4):
        ordered = BilinearOperator.from_terms(
            (GHOST_SLICE[vector], (), GHOST_SLICE[target], (vector,), sp.S.One)
            for vector in range(4)
        )
        outputs[target] = graded_complete_bilinear(ordered, PARITIES)
    return tuple(outputs)


def _gauge_field_action() -> tuple[BilinearOperator, ...]:
    """Nonlinear covariant Diff x U(1) action on ``(h,a)``."""

    outputs = [BZERO for _ in range(14)]
    for first, second in PAIRS:
        local_output = PAIR_INDEX[(first, second)]
        terms = []
        for vector in range(4):
            ghost = GHOST_SLICE[vector]
            terms.append((ghost, (), FIELD_SLICE[local_output], (vector,), sp.S.One))
            first_metric = FIELD_SLICE[PAIR_INDEX[tuple(sorted((vector, second)))]]
            second_metric = FIELD_SLICE[PAIR_INDEX[tuple(sorted((first, vector)))]]
            terms.append((ghost, (first,), first_metric, (), sp.S.One))
            terms.append((ghost, (second,), second_metric, (), sp.S.One))
        outputs[local_output] = graded_complete_bilinear(
            BilinearOperator.from_terms(terms), PARITIES
        )

    # With lambda_cov=lambda+i_c A, the potential transforms as
    # q a=i_c(F_bar+da)+d lambda_cov.  Its nonlinear term is i_c da.
    for component in range(4):
        terms = []
        for vector in range(4):
            ghost = GHOST_SLICE[vector]
            terms.append((ghost, (), FIELD_SLICE[10 + component], (vector,), sp.S.One))
            terms.append((ghost, (), FIELD_SLICE[10 + vector], (component,), -sp.S.One))
        outputs[10 + component] = graded_complete_bilinear(
            BilinearOperator.from_terms(terms), PARITIES
        )
    return tuple(outputs)


def _covariant_u1_ghost_q2() -> BilinearOperator:
    """Return ``q2(lambda_cov)=i_c i_c F_bar`` in polarized convention."""

    field = sp.zeros(4)
    field[2, 3] = MAGNETIC_P * sp.sin(COORDINATES[2])
    field[3, 2] = -field[2, 3]
    return BilinearOperator.from_terms(
        (GHOST_SLICE[first], (), GHOST_SLICE[second], (), field[first, second])
        for first, second in product(range(4), repeat=2)
        if field[first, second] != 0
    )


def _ordered_gauge_part(operator: BilinearOperator) -> BilinearOperator:
    """Keep one ghost-field orientation from an already completed action."""

    return BilinearOperator.from_terms(
        term for term in operator.terms
        if term[0] in GHOST_SLICE and term[2] in FIELD_SLICE
    )


@lru_cache(maxsize=1)
def build_q2() -> tuple[BilinearOperator, ...]:
    """Complete cyclic 38-row binary Taylor coefficient."""

    outputs = [BZERO for _ in range(TOTAL_ROWS)]
    ghost_bracket = _ghost_bracket()
    for output, operator in enumerate(ghost_bracket):
        outputs[GHOST_SLICE[output]] = outputs[GHOST_SLICE[output]] + operator

    outputs[GHOST_SLICE[4]] = outputs[GHOST_SLICE[4]] + _covariant_u1_ghost_q2()

    gauge_action = _gauge_field_action()
    for local_output, operator in enumerate(gauge_action):
        global_output = FIELD_SLICE[local_output]
        outputs[global_output] = outputs[global_output] + operator
        ordered = _ordered_gauge_part(operator)
        for field_input, mate in negative_transpose_bilinear_right(
            ordered, dual_output=EQUATION_SLICE[local_output]
        ).items():
            outputs[EQUATION_SLICE[field_input - FIELD_SLICE[0]]] = (
                outputs[EQUATION_SLICE[field_input - FIELD_SLICE[0]]]
                + graded_complete_bilinear(mate, PARITIES)
            )
        for ghost_input, mate in negative_transpose_bilinear_left(
            ordered, dual_output=EQUATION_SLICE[local_output]
        ).items():
            outputs[IDENTITY_SLICE[ghost_input]] = (
                outputs[IDENTITY_SLICE[ghost_input]]
                + graded_complete_bilinear(mate, PARITIES)
            )

    field_map = {index: FIELD_SLICE[index] for index in range(14)}
    for local_output, equation in enumerate(physical_euler_rows()):
        outputs[EQUATION_SLICE[local_output]] = (
            outputs[EQUATION_SLICE[local_output]]
            + _shift_bilinear(equation.bilinear, field_map)
        )

    # Coadjoint rows from the Diff and covariant-U(1) ghost vertices.
    all_ghost_rows = (*ghost_bracket[:4], _covariant_u1_ghost_q2())
    for local_output, operator in enumerate(all_ghost_rows):
        for ghost_input, mate in negative_transpose_bilinear_right(
            operator, dual_output=IDENTITY_SLICE[local_output]
        ).items():
            outputs[IDENTITY_SLICE[ghost_input]] = (
                outputs[IDENTITY_SLICE[ghost_input]]
                + graded_complete_bilinear(mate, PARITIES)
            )

    result = tuple(outputs)
    for output, operator in enumerate(result):
        if operator != operator.koszul_swapped(PARITIES):
            raise AssertionError(f"q2 lost Koszul symmetry on row {output}")
    return result


def _apply_output_linear_bilinear(
    outer: LinearOperator,
    rows: tuple[BilinearOperator, ...],
) -> BilinearOperator:
    values = []
    for middle, word, coefficient in outer.terms:
        current = rows[middle]
        for axis in word:
            current = current.derivative(axis)
        values.append(current.scale(coefficient))
    return BilinearOperator.from_terms(term for value in values for term in value.terms)


def _precompose_bilinear_q1(
    operator: BilinearOperator,
    q1: tuple[LinearOperator, ...],
    *,
    slot: int,
) -> BilinearOperator:
    terms = []
    for left, left_word, right, right_word, coefficient in operator.terms:
        if slot == 0:
            current = q1[left]
            for axis in left_word:
                current = current.derivative(axis)
            terms.extend(
                (new_left, new_word, right, right_word, coefficient * value)
                for new_left, new_word, value in current.terms
            )
        elif slot == 1:
            current = q1[right]
            for axis in right_word:
                current = current.derivative(axis)
            sign = -1 if PARITIES[left] else 1
            terms.extend(
                (left, left_word, new_right, new_word, sign * coefficient * value)
                for new_right, new_word, value in current.terms
            )
        else:
            raise ValueError("bilinear slot must be zero or one")
    return BilinearOperator.from_terms(terms)


def arity_two_defects() -> tuple[BilinearOperator, ...]:
    """Return the exact coefficientwise arity-two part of ``Q^2``."""

    q1 = build_q1()
    q2 = build_q2()
    output = []
    for target in range(TOTAL_ROWS):
        defect = _apply_output_linear_bilinear(q1[target], q2)
        if q2[target].terms:
            defect = defect + _precompose_bilinear_q1(q2[target], q1, slot=0)
            defect = defect + _precompose_bilinear_q1(q2[target], q1, slot=1)
        output.append(defect.at_base_point())
    return tuple(output)


def _covariant_u1_ghost_q3_ordered() -> TrilinearOperator:
    """One ordered representative of ``i_c i_c da``."""

    terms = []
    for first, second in product(range(4), repeat=2):
        terms.append(
            (
                GHOST_SLICE[first], (), GHOST_SLICE[second], (),
                FIELD_SLICE[10 + second], (first,), sp.S.One,
            )
        )
        terms.append(
            (
                GHOST_SLICE[first], (), GHOST_SLICE[second], (),
                FIELD_SLICE[10 + first], (second,), -sp.S.One,
            )
        )
    return TrilinearOperator.from_terms(terms)


@lru_cache(maxsize=1)
def build_q3() -> tuple[TrilinearOperator, ...]:
    """Complete cyclic 38-row ternary Taylor coefficient."""

    outputs = [TZERO for _ in range(TOTAL_ROWS)]
    field_map = {index: FIELD_SLICE[index] for index in range(14)}
    for local_output, equation in enumerate(physical_euler_rows()):
        outputs[EQUATION_SLICE[local_output]] = _shift_trilinear(
            equation.trilinear, field_map
        )

    ordered = _covariant_u1_ghost_q3_ordered()
    lambda_q3 = graded_complete_trilinear(ordered, PARITIES).scale(sp.Rational(1, 2))
    outputs[GHOST_SLICE[4]] = outputs[GHOST_SLICE[4]] + lambda_q3

    # Cotangent partners of the same quartic BV vertex.  The ordered
    # representative is symmetric in its two ghost positions after summing
    # the antisymmetric field-strength indices, so one ghost transpose and
    # the potential transpose exhaust the cyclic mates.
    for field_input, mate in negative_transpose_trilinear_slot(
        ordered, slot=2, dual_output=IDENTITY_SLICE[4]
    ).items():
        outputs[EQUATION_SLICE[field_input - FIELD_SLICE[0]]] = (
            outputs[EQUATION_SLICE[field_input - FIELD_SLICE[0]]]
            - graded_complete_trilinear(mate, PARITIES).scale(sp.Rational(1, 2))
        )
    for ghost_input, mate in negative_transpose_trilinear_slot(
        ordered, slot=0, dual_output=IDENTITY_SLICE[4]
    ).items():
        outputs[IDENTITY_SLICE[ghost_input]] = (
            outputs[IDENTITY_SLICE[ghost_input]]
            - graded_complete_trilinear(mate, PARITIES)
        )

    result = tuple(outputs)
    for output, operator in enumerate(result):
        for permutation in ((1, 0, 2), (0, 2, 1)):
            if operator != operator.koszul_permuted(permutation, PARITIES):
                raise AssertionError(
                    f"q3 lost Koszul symmetry on row {output}, permutation {permutation}"
                )
    return result


def _apply_output_linear_trilinear(
    outer: LinearOperator,
    rows: tuple[TrilinearOperator, ...],
) -> TrilinearOperator:
    values = []
    for middle, word, coefficient in outer.terms:
        current = rows[middle]
        for axis in word:
            current = current.derivative(axis)
        values.append(current.scale(coefficient))
    return TrilinearOperator.from_terms(term for value in values for term in value.terms)


def _precompose_trilinear_q1(
    operator: TrilinearOperator,
    q1: tuple[LinearOperator, ...],
    *,
    slot: int,
) -> TrilinearOperator:
    terms = []
    for first, first_word, second, second_word, third, third_word, coefficient in operator.terms:
        rows = (first, second, third)
        words = (first_word, second_word, third_word)
        current = q1[rows[slot]]
        for axis in words[slot]:
            current = current.derivative(axis)
        sign = -1 if sum(PARITIES[rows[index]] for index in range(slot)) % 2 else 1
        for new_row, new_word, value in current.terms:
            new_rows = list(rows)
            new_words = list(words)
            new_rows[slot] = new_row
            new_words[slot] = new_word
            terms.append(
                (
                    new_rows[0], new_words[0],
                    new_rows[1], new_words[1],
                    new_rows[2], new_words[2],
                    sign * coefficient * value,
                )
            )
    return TrilinearOperator.from_terms(terms)


def _q2_q2_row(
    outer: BilinearOperator,
    q2: tuple[BilinearOperator, ...],
) -> TrilinearOperator:
    terms = []
    for middle, outer_word, last, last_word, outer_coefficient in outer.terms:
        current = q2[middle]
        for axis in outer_word:
            current = current.derivative(axis)
        for first, first_word, second, second_word, inner_coefficient in current.terms:
            coefficient = outer_coefficient * inner_coefficient
            terms.append(
                (first, first_word, second, second_word, last, last_word, coefficient)
            )
            swap_sign = -1 if PARITIES[second] * PARITIES[last] else 1
            terms.append(
                (first, first_word, last, last_word, second, second_word, swap_sign * coefficient)
            )
            rotate_sign = -1 if PARITIES[last] * (PARITIES[first] + PARITIES[second]) % 2 else 1
            terms.append(
                (last, last_word, first, first_word, second, second_word, rotate_sign * coefficient)
            )
    return TrilinearOperator.from_terms(terms)


def arity_three_defect_row(target: int) -> TrilinearOperator:
    """Memory-bounded exact arity-three coefficient of ``Q^2``."""

    q1 = build_q1()
    q2 = build_q2()
    q3 = build_q3()
    defect = _q2_q2_row(q2[target], q2)
    defect = defect + _apply_output_linear_trilinear(q1[target], q3)
    if q3[target].terms:
        for slot in range(3):
            defect = defect + _precompose_trilinear_q1(q3[target], q1, slot=slot)
    return defect.at_base_point()


def unary_checks() -> dict[str, object]:
    rows = physical_euler_rows()
    generator = gauge_generator()
    ward = []
    for row in rows:
        defect = compose_linear(row.linear, generator).at_base_point()
        ward.append(len(defect.terms))
    if any(ward):
        raise AssertionError(f"Einstein--Maxwell Hessian failed gauge invariance: {ward}")

    hessian = _linear_matrix(rows)
    adjoint = formal_adjoint_matrix(hessian)
    adjoint_defects = []
    for row in range(14):
        for column in range(14):
            defect = (hessian[row][column] - adjoint[row][column]).at_base_point()
            if defect.terms:
                adjoint_defects.append((row, column, len(defect.terms)))
    if adjoint_defects:
        raise AssertionError(f"Einstein--Maxwell Hessian lost formal self-adjointness: {adjoint_defects[:12]}")
    return {
        "gauge_generator_row_count": len(generator),
        "hessian_ward_defect_term_counts": ward,
        "formal_adjoint_defects": adjoint_defects,
        "base_point": {str(key): str(value) for key, value in BASE_POINT.items()},
    }


if __name__ == "__main__":
    import json

    print(json.dumps({"physical": physical_summary(), "unary_checks": unary_checks()}, indent=2, sort_keys=True))

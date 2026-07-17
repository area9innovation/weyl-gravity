#!/usr/bin/env python3
"""Exact support-local Maxwell extension of the 54-row Berger BV q2.

The gravity operation remains the authoritative content-addressed base.  This
module constructs the ten-row Maxwell unary block and the sparse 64-row q2
overlay directly from the Maxwell action and its Diff-semidirect-U(1) BV
master terms in the left-invariant Berger PBW basis.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _exact_data as _gravity_exact_data,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ETA,
    PAIRS,
    LinearOperator,
    _adjoint_matrix,
    _compose_matrices,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    BZERO,
    GAUGE_FIXED_PARITIES,
    U,
    U0,
    V,
    V0,
    BilinearOperator,
    _apply_output_linear,
    _fixture_bilinear,
    _fixture_linear,
    _leibniz_adjoint_terms,
    _negative_transpose_left,
    _negative_transpose_right,
    _outer,
    _precompose_bilinear_slot,
    _structure,
    _sum_bilinear,
    _clock_canonical_maps_fixture,
)


GRAVITY_ROWS = 54
TOTAL_ROWS = 64
CM = 54
A_ROWS = tuple(range(55, 59))
APLUS_ROWS = tuple(range(59, 63))
CMPLUS = 63
GHOST_DUAL_ROWS = tuple(range(49, 54))
FRAME_TO_GHOST = {0: 3, 1: 0, 2: 1, 3: 2}
ETA_DIAGONAL = tuple(ETA[index, index] for index in range(4))
MAXWELL_PAIRS = tuple((first, second) for first in range(4) for second in range(first + 1, 4))
COMBINED_PARITIES = GAUGE_FIXED_PARITIES + (1,) + (0,) * 4 + (1,) * 4 + (0,)


def _zero_linear_matrix(rows: int, columns: int) -> list[list[LinearOperator]]:
    return [[LinearOperator() for _ in range(columns)] for _ in range(rows)]


def _scalar_operator(*terms: tuple[tuple[int, ...], sp.Expr]) -> LinearOperator:
    return LinearOperator.from_terms((0, word, coefficient) for word, coefficient in terms)


def _fixture_structure(first: int, second: int, target: int) -> sp.Expr:
    return sp.expand(
        _structure(first, second).get(target, sp.S.Zero).subs({U: U0, V: V0})
    )


def _graded_complete(operator: BilinearOperator) -> BilinearOperator:
    return operator + BilinearOperator.from_terms(
        (
            right,
            right_word,
            left,
            left_word,
            (-1 if COMBINED_PARITIES[left] * COMBINED_PARITIES[right] else 1)
            * coefficient,
        )
        for left, left_word, right, right_word, coefficient in operator.terms
    )


@lru_cache(maxsize=1)
def maxwell_field_strength_matrix() -> tuple[tuple[LinearOperator, ...], ...]:
    """Return F_ab=e_a A_b-e_b A_a-C_ab^c A_c on local A columns."""

    matrix: list[list[LinearOperator]] = []
    for first, second in MAXWELL_PAIRS:
        row = []
        for component in range(4):
            terms: list[tuple[tuple[int, ...], sp.Expr]] = []
            if component == second:
                terms.append(((first,), sp.S.One))
            if component == first:
                terms.append(((second,), -sp.S.One))
            structure = _fixture_structure(first, second, component)
            if structure:
                terms.append(((), -structure))
            row.append(_scalar_operator(*terms))
        matrix.append(row)
    return tuple(tuple(row) for row in matrix)


@lru_cache(maxsize=1)
def maxwell_unary_blocks() -> dict[str, tuple[tuple[LinearOperator, ...], ...]]:
    """Return d, the action Hessian, and d^sharp in the Maxwell complex."""

    field_strength = [list(row) for row in maxwell_field_strength_matrix()]
    kinetic_weight = _zero_linear_matrix(6, 6)
    for index, (first, second) in enumerate(MAXWELL_PAIRS):
        kinetic_weight[index][index] = _scalar_operator(
            ((), -ETA_DIAGONAL[first] * ETA_DIAGONAL[second])
        )
    hessian = [
        [_fixture_linear(entry) for entry in row]
        for row in _compose_matrices(
            _compose_matrices(_adjoint_matrix(field_strength), kinetic_weight),
            field_strength,
        )
    ]
    gradient = [[_scalar_operator(((axis,), sp.S.One))] for axis in range(4)]
    divergence = _adjoint_matrix(gradient)
    if any(
        _fixture_linear(entry).terms
        for row in _compose_matrices(hessian, gradient)
        for entry in row
    ):
        raise AssertionError("Maxwell Hessian does not annihilate exact potentials")
    if any(
        _fixture_linear(entry).terms
        for row in _compose_matrices(divergence, hessian)
        for entry in row
    ):
        raise AssertionError("Maxwell Noether divergence does not annihilate the Hessian")
    return {
        "gradient": tuple(tuple(row) for row in gradient),
        "hessian": tuple(tuple(row) for row in hessian),
        "divergence": tuple(tuple(row) for row in divergence),
    }


@lru_cache(maxsize=1)
def build_coupled_q1_fixture() -> tuple[tuple[LinearOperator, ...], ...]:
    gravity = _gravity_exact_data()["q_gauge_fixed"]
    output = _zero_linear_matrix(TOTAL_ROWS, TOTAL_ROWS)
    for row in range(GRAVITY_ROWS):
        for column in range(GRAVITY_ROWS):
            output[row][column] = gravity[row][column]
    blocks = maxwell_unary_blocks()
    for component in range(4):
        output[A_ROWS[component]][CM] = blocks["gradient"][component][0]
        output[CMPLUS][APLUS_ROWS[component]] = blocks["divergence"][0][component]
        for source in range(4):
            output[APLUS_ROWS[component]][A_ROWS[source]] = blocks["hessian"][component][source]
    square = _compose_matrices(output, output)
    if any(_fixture_linear(entry).terms for row in square for entry in row):
        raise AssertionError("combined 64-row unary differential is not nilpotent")
    return tuple(tuple(row) for row in output)


def _field_strength_operator(first: int, second: int) -> LinearOperator:
    return LinearOperator.from_terms(
        (
            *(
                (A_ROWS[second], (first,), sp.S.One),
                (A_ROWS[first], (second,), -sp.S.One),
            ),
            *(
                (A_ROWS[target], (), -coefficient)
                for target in range(4)
                if (coefficient := _fixture_structure(first, second, target))
            ),
        )
    )


@lru_cache(maxsize=1)
def maxwell_metric_source_rows() -> tuple[BilinearOperator, ...]:
    """Return q2(A,A)->h_hat_plus in repository metric-row normalization."""

    field_strength = {
        (first, second): _field_strength_operator(first, second)
        for first, second in product(range(4), repeat=2)
    }
    rows = []
    for first, second in PAIRS:
        multiplicity = 2 if first != second else 1
        first_term = _sum_bilinear(
            (
                _outer(field_strength[(first, contracted)], field_strength[(second, contracted)])
                + _outer(field_strength[(second, contracted)], field_strength[(first, contracted)])
            ).scale(ETA_DIAGONAL[contracted])
            for contracted in range(4)
        )
        trace = _sum_bilinear(
            _outer(field_strength[(left, right)], field_strength[(left, right)]).scale(
                ETA_DIAGONAL[left] * ETA_DIAGONAL[right]
            )
            for left, right in product(range(4), repeat=2)
        )
        trace_weight = (
            -sp.Rational(1, 2) * ETA_DIAGONAL[first]
            if first == second
            else sp.S.Zero
        )
        rows.append(
            _fixture_bilinear(
                (first_term + trace.scale(trace_weight)).scale(
                    multiplicity * ETA_DIAGONAL[first] * ETA_DIAGONAL[second]
                )
            )
        )
    return tuple(rows)


@lru_cache(maxsize=1)
def maxwell_dressed_physical_source_rows() -> tuple[BilinearOperator, ...]:
    """Transport the raw metric source to (h_hat,R,Theta) Euler rows.

    Four-dimensional Weyl invariance makes the R row vanish.  The temporal
    clock dressing g_hat=h_hat+K_tau Theta produces the derivative-valued
    Theta row required by the temporal diffeomorphism Noether identity.
    """

    canonical, _inverse = _clock_canonical_maps_fixture()
    raw_metric = maxwell_metric_source_rows()
    output = []
    for dressed_equation in range(12):
        terms = []
        for raw_equation, source in enumerate(raw_metric):
            outer = canonical[17 + dressed_equation][17 + raw_equation]
            if outer.terms and source.terms:
                terms.extend(_apply_output_linear(outer, source).terms)
        output.append(_fixture_bilinear(BilinearOperator.from_terms(terms)))
    if output[10].terms:
        raise AssertionError("four-dimensional Maxwell Weyl invariance did not kill the R row")
    if not output[11].terms:
        raise AssertionError("clock dressing did not generate the Theta Noether row")
    return tuple(output)


@lru_cache(maxsize=1)
def maxwell_equation_mixed_rows() -> tuple[BilinearOperator, ...]:
    """Cyclically transpose all dressed physical sources to A-plus."""

    terms: list[list[tuple]] = [[] for _ in range(4)]
    for equation, operator in enumerate(maxwell_dressed_physical_source_rows()):
        physical_field = 5 + equation
        for left, left_word, right, right_word, coefficient in operator.terms:
            if left not in A_ROWS or right not in A_ROWS:
                raise AssertionError("metric Maxwell source contains a non-Maxwell input")
            for differentiated_right, differentiated_metric, multiplicity in _leibniz_adjoint_terms(
                left_word, right_word, ()
            ):
                terms[left - A_ROWS[0]].append(
                    (
                        physical_field,
                        differentiated_metric,
                        right,
                        differentiated_right,
                        coefficient * sp.Rational(1, 2) * multiplicity,
                    )
                )
    return tuple(
        _fixture_bilinear(_graded_complete(BilinearOperator.from_terms(row_terms)))
        for row_terms in terms
    )


def _maxwell_covector_gauge_action(component: int) -> BilinearOperator:
    terms = []
    for vector in range(4):
        ghost = FRAME_TO_GHOST[vector]
        terms.append((ghost, (), A_ROWS[component], (vector,), sp.S.One))
        terms.append((ghost, (component,), A_ROWS[vector], (), sp.S.One))
        for target in range(4):
            coefficient = _fixture_structure(vector, component, target)
            if coefficient:
                terms.append((ghost, (), A_ROWS[target], (), -coefficient))
    return BilinearOperator.from_terms(terms)


@lru_cache(maxsize=1)
def build_maxwell_q2_overlay() -> tuple[BilinearOperator, ...]:
    """Return all Maxwell additions as a sparse 64-row q2 overlay."""

    outputs = [BZERO for _ in range(TOTAL_ROWS)]
    for equation, operator in enumerate(maxwell_dressed_physical_source_rows()):
        outputs[27 + equation] = outputs[27 + equation] + operator
    for component, operator in enumerate(maxwell_equation_mixed_rows()):
        outputs[APLUS_ROWS[component]] = outputs[APLUS_ROWS[component]] + operator

    for component in range(4):
        ordered = _maxwell_covector_gauge_action(component)
        outputs[A_ROWS[component]] = outputs[A_ROWS[component]] + _graded_complete(ordered)
        for field_input, mate in _negative_transpose_right(
            ordered, dual_output=APLUS_ROWS[component]
        ).items():
            outputs[APLUS_ROWS[field_input - A_ROWS[0]]] = (
                outputs[APLUS_ROWS[field_input - A_ROWS[0]]] + _graded_complete(mate)
            )
        for ghost_input, mate in _negative_transpose_left(
            ordered, dual_output=APLUS_ROWS[component]
        ).items():
            outputs[GHOST_DUAL_ROWS[ghost_input]] = (
                outputs[GHOST_DUAL_ROWS[ghost_input]]
                + _graded_complete(mate).scale(2)
            )

    scalar_action = BilinearOperator.from_terms(
        (FRAME_TO_GHOST[vector], (), CM, (vector,), sp.S.One)
        for vector in range(4)
    )
    outputs[CM] = outputs[CM] + _graded_complete(scalar_action)
    for field_input, mate in _negative_transpose_right(
        scalar_action, dual_output=CMPLUS
    ).items():
        if field_input != CM:
            raise AssertionError("scalar ghost action has an unexpected field input")
        outputs[CMPLUS] = outputs[CMPLUS] + _graded_complete(mate)
    for ghost_input, mate in _negative_transpose_left(
        scalar_action, dual_output=CMPLUS
    ).items():
        outputs[GHOST_DUAL_ROWS[ghost_input]] = (
            outputs[GHOST_DUAL_ROWS[ghost_input]]
            + _graded_complete(mate).scale(2)
        )

    result = tuple(_fixture_bilinear(operator) for operator in outputs)
    for output, operator in enumerate(result):
        if operator != operator.koszul_swapped(COMBINED_PARITIES):
            raise AssertionError(f"Maxwell q2 overlay lost Koszul symmetry on row {output}")
    return result


def arity_two_overlay_defect_row(target: int) -> BilinearOperator:
    """Memory-bounded coefficientwise q1-q2 defect for one overlay row."""

    q1 = build_coupled_q1_fixture()
    q2 = build_maxwell_q2_overlay()
    defect = BZERO
    for middle, outer in enumerate(q1[target]):
        if outer.terms and q2[middle].terms:
            defect = defect + _apply_output_linear(outer, q2[middle])
    if q2[target].terms:
        defect = defect + _precompose_bilinear_slot(
            q2[target], q1, slot=0, parities=COMBINED_PARITIES
        )
        defect = defect + _precompose_bilinear_slot(
            q2[target],
            q1,
            slot=1,
            parities=COMBINED_PARITIES,
            second_slot_q1_sign=True,
        )
    return _fixture_bilinear(defect)


def evaluate_bilinear(
    operator: BilinearOperator,
    left_values: dict[int, sp.Expr],
    right_values: dict[int, sp.Expr],
    time: sp.Symbol,
) -> sp.Expr:
    def derivative(value: sp.Expr, word: tuple[int, ...]) -> sp.Expr:
        output = value
        for axis in reversed(word):
            output = sp.diff(output, time) if axis == 0 else sp.S.Zero
        return output

    return sp.trigsimp(
        sum(
            coefficient
            * derivative(left_values.get(left, sp.S.Zero), left_word)
            * derivative(right_values.get(right, sp.S.Zero), right_word)
            for left, left_word, right, right_word, coefficient in operator.terms
        )
    )


def physical_regressions() -> dict[str, object]:
    beta = 2 * sp.sqrt(10) / 3
    time = sp.symbols("t", real=True)
    standing = {A_ROWS[1]: 2 * sp.cos(beta * time)}
    metric_values = {
        5: sp.Rational(5120, 567),
        9: -sp.Rational(2466560, 147819),
        12: -sp.Rational(76705280, 4582389),
        14: -sp.Rational(14080, 1953),
    }
    metric_source = [
        sp.factor(evaluate_bilinear(operator, standing, standing, time))
        for operator in maxwell_metric_source_rows()
    ]
    mixed_source = [
        sp.factor(evaluate_bilinear(operator, metric_values, standing, time))
        for operator in maxwell_equation_mixed_rows()
    ]
    expected_metric = [
        sp.Rational(160, 9), 0, 0, 0, -sp.Rational(160, 9),
        0, 0, sp.Rational(160, 9), 0, sp.Rational(160, 9),
    ]
    expected_mixed = [
        0,
        sp.Rational(564428800, 35920017) * sp.cos(beta * time),
        0,
        0,
    ]
    if metric_source != expected_metric:
        raise AssertionError("support-local A,A-to-h-plus failed the standing fixture")
    if mixed_source != expected_mixed:
        raise AssertionError("support-local h,A-to-A-plus failed the frequency fixture")
    return {
        "standing_metric_source": [str(value) for value in metric_source],
        "standing_mixed_Aplus_component_source": [str(value) for value in mixed_source],
        "canonical_three_form_e023_source": "-564428800*cos(2*sqrt(10)*t/3)/35920017",
        "metric_factor_two_recovered": True,
        "canonical_Maxwell_Euler_sign_recovered": True,
    }

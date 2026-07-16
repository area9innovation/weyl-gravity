from __future__ import annotations

import sympy as sp

from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine


def _constant_linear_coefficient(operator, component: int = 0):
    return sum(
        coefficient
        for current, word, coefficient in operator.terms
        if current == component and not word
    )


def _constant_bilinear_coefficient(operator, left: int = 0, right: int = 0):
    return sum(
        coefficient
        for first, first_word, second, second_word, coefficient in operator.terms
        if first == left and second == right and not first_word and not second_word
    )


def _constant_trilinear_coefficient(
    operator, first: int = 0, second: int = 0, third: int = 0
):
    return sum(
        coefficient
        for a, a_word, b, b_word, c, c_word, coefficient in operator.terms
        if (a, b, c) == (first, second, third)
        and not a_word
        and not b_word
        and not c_word
    )


def test_scalar_jet_third_derivatives_are_exact() -> None:
    previous = engine.TAYLOR_ORDER
    engine.TAYLOR_ORDER = 3
    try:
        value = engine.Jet2.field(0, sp.Integer(2))
        reciprocal = value.reciprocal()
        quartic = value.power(4)
    finally:
        engine.TAYLOR_ORDER = previous

    assert _constant_linear_coefficient(reciprocal.linear) == -sp.Rational(1, 4)
    assert _constant_bilinear_coefficient(reciprocal.bilinear) == sp.Rational(1, 4)
    assert _constant_trilinear_coefficient(reciprocal.trilinear) == -sp.Rational(3, 8)
    assert _constant_linear_coefficient(quartic.linear) == 32
    assert _constant_bilinear_coefficient(quartic.bilinear) == 48
    assert _constant_trilinear_coefficient(quartic.trilinear) == 48


def test_trilinear_pbw_storage_detects_slot_permutations() -> None:
    operator = engine.TrilinearOperator.from_terms(
        ((0, (1,), 1, (2,), 2, (3,), sp.Integer(7)),)
    )
    permuted = operator.permuted((2, 0, 1))
    assert permuted.terms == ((2, (3,), 0, (1,), 1, (2,), sp.Integer(7)),)


def test_volume_density_selected_third_variations() -> None:
    previous = engine.TAYLOR_ORDER
    engine._volume_density_ratio.cache_clear()
    engine.TAYLOR_ORDER = 3
    try:
        volume = engine._volume_density_ratio()
    finally:
        engine.TAYLOR_ORDER = previous
        engine._volume_density_ratio.cache_clear()

    variables = sp.symbols("x0:10")
    metric = sp.diag(-1, 1, 1, 1)
    for pair, variable in zip(engine.PAIRS, variables, strict=True):
        first, second = pair
        metric[first, second] += variable
        if first != second:
            metric[second, first] += variable
    exact = sp.sqrt(-metric.det())
    zero = {variable: 0 for variable in variables}
    table = {
        (first, second, third): coefficient
        for first, first_word, second, second_word, third, third_word, coefficient in volume.trilinear.terms
        if not first_word and not second_word and not third_word
    }
    for first, second, third in ((0, 0, 0), (0, 1, 1), (1, 2, 3), (4, 4, 9)):
        expected = sp.diff(
            exact, variables[first], variables[second], variables[third]
        ).subs(zero)
        assert sp.simplify(table.get((first, second, third), 0) - expected) == 0

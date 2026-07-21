"""Independent covariant-density replay for the four-derivative response.

This verifier does not import the response producer.  It constructs the six
action densities directly in the exact compact-product Taylor-jet algebra,
polarizes their second variations, substitutes independent axial and polar
harmonic representatives, and performs the sphere integrals as exact
polynomial integrals in ``z=cos(theta)``.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_product_taylor import _field_strength
from bridge.einstein_sector.product_taylor_engine import (
    COORDINATES,
    PAIR_INDEX,
    TaylorJet,
    metric_geometry,
    sum_jets,
)


THETA = COORDINATES[2]
OMEGA = sp.symbols("omega", real=True)
Z, SINE_SYMBOL = sp.symbols("z sine_symbol", real=True)
BASIS = ("1", "R", "F2", "RiemFF", "F2sq", "P2")


def _epsilon4(indices: tuple[int, int, int, int]) -> int:
    if len(set(indices)) < 4:
        return 0
    inversions = sum(
        indices[left] > indices[right]
        for left in range(4)
        for right in range(left + 1, 4)
    )
    return -1 if inversions % 2 else 1


@lru_cache(maxsize=1)
def _densities() -> dict[str, TaylorJet]:
    geometry = metric_geometry()
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    riemann = geometry["riemann"]
    scalar = geometry["scalar"]
    volume = geometry["volume_ratio"]
    assert isinstance(metric, dict)
    assert isinstance(inverse, dict)
    assert isinstance(riemann, dict)
    assert isinstance(scalar, TaylorJet)
    assert isinstance(volume, TaylorJet)
    field = _field_strength()
    field_up = {
        (first, second): sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * field[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        for first, second in product(range(4), repeat=2)
    }
    field_squared = sum_jets(
        field[(first, second)] * field_up[(first, second)]
        for first, second in product(range(4), repeat=2)
    )
    epsilon_contraction = sum_jets(
        field[(a, b)]
        * field[(c, d)].scale(sp.Rational(_epsilon4((a, b, c, d)), 2))
        for a, b, c, d in product(range(4), repeat=4)
        if _epsilon4((a, b, c, d))
    )
    pseudoscalar = epsilon_contraction / volume.scale(sp.sin(THETA))
    riemann_lower = {
        (a, b, c, d): sum_jets(
            metric[(a, target)] * riemann[(target, b, c, d)]
            for target in range(4)
        )
        for a, b, c, d in product(range(4), repeat=4)
    }
    riemann_ff = sum_jets(
        riemann_lower[(a, b, c, d)]
        * field_up[(a, b)]
        * field_up[(c, d)]
        for a, b, c, d in product(range(4), repeat=4)
    )
    return {
        "1": volume,
        "R": volume * scalar,
        "F2": volume * field_squared,
        "RiemFF": volume * riemann_ff,
        "F2sq": volume * field_squared.power(2),
        "P2": volume * pseudoscalar.power(2),
    }


def _differentiate_mode(
    expression: sp.Expr, word: tuple[int, ...], frequency_sign: int
) -> sp.Expr:
    value = expression
    for axis in word:
        if axis == 0:
            value = frequency_sign * sp.I * OMEGA * value
        elif axis == 2:
            value = sp.diff(value, THETA)
        else:
            return sp.S.Zero
    return value


def _integrate_axisymmetric(expression_with_measure: sp.Expr) -> sp.Expr:
    """Integrate exactly after the oriented substitution z=cos(theta)."""

    value = sp.trigsimp(
        expression_with_measure / sp.sin(THETA), method="fu"
    ).replace(sp.Abs, lambda argument: argument)
    value = sp.expand_trig(value.rewrite(sp.sin))
    value = sp.cancel(
        value.subs({sp.sin(THETA): SINE_SYMBOL, sp.cos(THETA): Z})
    )
    value = sp.powdenest(
        sp.cancel(value.subs(SINE_SYMBOL, sp.sqrt(1 - Z**2))), force=True
    ).replace(sp.Abs, lambda argument: argument)
    value = sp.cancel(value)
    if value.has(sp.sqrt(1 - Z**2)):
        raise AssertionError(f"sphere integrand did not become rational: {value}")
    return sp.integrate(value, (Z, -1, 1))


def _polarized_kernel(
    density: TaylorJet,
    left_modes: list[dict[int, sp.Expr]],
    right_modes: list[dict[int, sp.Expr]],
    ell: int,
) -> sp.Matrix:
    norm = sp.Rational(2, 2 * ell + 1)
    output = sp.zeros(len(left_modes), len(right_modes))
    for row, left in enumerate(left_modes):
        for column, right in enumerate(right_modes):
            expression = sum(
                coefficient
                * _differentiate_mode(left[first], first_word, +1)
                * _differentiate_mode(right[second], second_word, -1)
                for first, first_word, second, second_word, coefficient
                in density.bilinear.terms
                if first in left and second in right
            )
            output[row, column] = sp.factor(
                _integrate_axisymmetric(expression * sp.sin(THETA)) / norm
            )
    return output


def _modes(ell: int) -> dict[str, list[dict[int, sp.Expr]]]:
    eigenvalue = sp.Integer(ell * (ell + 1))
    harmonic = sp.legendre(ell, sp.cos(THETA))
    axial_one_form = -sp.sin(THETA) * sp.diff(harmonic, THETA)
    return {
        "axial_q": [
            {PAIR_INDEX[(1, 3)]: axial_one_form},
            {11: harmonic},
        ],
        "axial_p": [
            {
                PAIR_INDEX[(0, 3)]: -eigenvalue * axial_one_form,
                10: eigenvalue * harmonic,
            },
            {
                PAIR_INDEX[(1, 3)]: -sp.Rational(2, 3) * axial_one_form,
                11: eigenvalue * harmonic,
            },
        ],
        "polar_q": [
            {
                PAIR_INDEX[(0, 0)]: -harmonic,
                PAIR_INDEX[(1, 1)]: -harmonic,
                PAIR_INDEX[(2, 2)]: harmonic,
                PAIR_INDEX[(3, 3)]: harmonic * sp.sin(THETA) ** 2,
            },
            {
                PAIR_INDEX[(0, 0)]: 2 * harmonic,
                PAIR_INDEX[(1, 1)]: 2 * harmonic,
                13: axial_one_form,
            },
        ],
        "polar_p": [
            {PAIR_INDEX[(0, 1)]: harmonic},
            {
                PAIR_INDEX[(0, 0)]: -8 * harmonic,
                PAIR_INDEX[(1, 1)]: -12 * eigenvalue * harmonic,
                13: 3 * (3 * eigenvalue - 2) * axial_one_form,
            },
        ],
    }


def _expected_q(name: str, parity: str, eigenvalue: sp.Expr) -> sp.Matrix:
    lam = eigenvalue
    axial = {
        "1": sp.zeros(2),
        "R": sp.Matrix([[2 * lam, 0], [0, 0]]),
        "F2": sp.Matrix([[0, 0], [0, -8]]),
        "RiemFF": sp.Matrix([[0, 8 * lam], [8 * lam, 0]]),
        "F2sq": sp.Matrix([[0, 0], [0, -32]]),
        "P2": sp.Matrix([[0, 0], [0, 64]]),
    }
    polar = {
        "1": sp.zeros(2),
        "R": sp.Matrix([[2, -4], [-4, 0]]),
        "F2": sp.Matrix([[0, 0], [0, -8 * lam]]),
        "RiemFF": sp.Matrix([[4, -8 * lam], [-8 * lam, 0]]),
        "F2sq": sp.Matrix([[0, 0], [0, -32 * lam]]),
        "P2": sp.zeros(2),
    }
    return (axial if parity == "axial" else polar)[name]


def _expected_p(name: str, parity: str, eigenvalue: sp.Expr) -> sp.Matrix:
    lam = eigenvalue
    axial = {
        "1": sp.Matrix([[0, sp.Rational(2, 3) * lam], [0, 0]]),
        "R": sp.Matrix([[0, sp.Rational(4, 9) * lam], [0, 0]]),
        "F2": sp.Matrix([[0, sp.Rational(4, 3) * lam * (3 * lam - 1)], [0, 0]]),
        "RiemFF": sp.Matrix(
            [[0, sp.Rational(4, 3) * lam * (7 * lam - 4)], [0, -sp.Rational(32, 9) * lam]]
        ),
        "F2sq": sp.Matrix([[0, 8 * lam * (2 * lam - 1)], [0, 0]]),
        "P2": sp.Matrix([[0, 0], [0, sp.Rational(32, 3) * lam * (3 * lam - 2)]]),
    }
    polar = {
        "1": sp.Matrix([[0, -12 * lam], [0, 4 * (3 * lam + 2)]]),
        "R": sp.Matrix([[0, -4 * (5 * lam + 2)], [0, 4 * (lam + 2) * (3 * lam + 2)]]),
        "F2": sp.Matrix([[0, -4 * (9 * lam**2 - 6 * lam + 4)], [0, 8 * (3 * lam + 2)]]),
        "RiemFF": sp.Matrix(
            [
                [0, -4 * (33 * lam**2 - 28 * lam + 12)],
                [0, 8 * (9 * lam**3 - 12 * lam**2 + 10 * lam + 4)],
            ]
        ),
        "F2sq": sp.Matrix(
            [
                [0, -16 * (3 * lam - 1) * (9 * lam - 4)],
                [0, 16 * (18 * lam**3 - 12 * lam**2 + 3 * lam + 2)],
            ]
        ),
        "P2": sp.zeros(2),
    }
    return (axial if parity == "axial" else polar)[name]


def verify() -> None:
    densities = _densities()
    # Three fibres determine the at-most-quadratic q-response entries.  The
    # fourth fibre independently controls the cubic polar p-cross entries.
    for ell in (2, 3, 4):
        eigenvalue = sp.Integer(ell * (ell + 1))
        modes = _modes(ell)
        for name in BASIS:
            for parity in ("axial", "polar"):
                kernel = _polarized_kernel(
                    densities[name],
                    modes[f"{parity}_q"],
                    modes[f"{parity}_q"],
                    ell,
                )
                response = kernel.diff(OMEGA).applyfunc(
                    lambda value: sp.factor(value / OMEGA)
                )
                if response != _expected_q(name, parity, eigenvalue):
                    raise AssertionError(
                        f"{name} {parity} q response failed at ell={ell}: {response}"
                    )
    for ell in (2, 3, 4, 5):
        eigenvalue = sp.Integer(ell * (ell + 1))
        modes = _modes(ell)
        for name in BASIS:
            for parity in ("axial", "polar"):
                kernel = _polarized_kernel(
                    densities[name],
                    modes[f"{parity}_q"],
                    modes[f"{parity}_p"],
                    ell,
                ).applyfunc(
                    lambda value: sp.factor(
                        sp.expand(value).subs(
                            OMEGA**2, eigenvalue - sp.Rational(2, 3)
                        )
                    )
                )
                if kernel != _expected_p(name, parity, eigenvalue):
                    raise AssertionError(
                        f"{name} {parity} p cross failed at ell={ell}: {kernel}"
                    )


if __name__ == "__main__":
    verify()

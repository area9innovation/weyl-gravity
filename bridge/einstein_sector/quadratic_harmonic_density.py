"""Exact normal forms for quadratic axisymmetric harmonic densities.

The reducer uses only the spherical eigenfunction equation

    Y'' + cot(theta) Y' + lambda Y = 0

and integration by parts through an explicit quadratic primitive.  It is
intended for direct-current certificate rails; it does not evaluate a finite
list of integer harmonics or interpolate in ``lambda``.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


class QuadraticHarmonicDensityError(RuntimeError):
    pass


@dataclass(frozen=True)
class QuadraticHarmonicNormalForm:
    reduced_density: sp.Expr
    canonical_coefficient: sp.Expr
    primitive: sp.Expr
    remainder: sp.Expr


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise QuadraticHarmonicDensityError(message)


def derivative_rules(
    harmonic: sp.Expr,
    theta: sp.Symbol,
    eigenvalue: sp.Expr,
    maximum_order: int,
) -> dict[sp.Expr, sp.Expr]:
    """Return ODE-derived rules for Y^(n), 2 <= n <= maximum_order."""

    _require(maximum_order >= 2, "maximum derivative order must be at least two")
    first = sp.diff(harmonic, theta)
    rules: dict[sp.Expr, sp.Expr] = {
        sp.diff(harmonic, theta, 2): -sp.cot(theta) * first - eigenvalue * harmonic
    }
    for order in range(3, maximum_order + 1):
        previous = sp.diff(rules[sp.diff(harmonic, theta, order - 1)], theta)
        for lower_order in range(order - 1, 1, -1):
            previous = previous.xreplace(
                {sp.diff(harmonic, theta, lower_order): rules[sp.diff(harmonic, theta, lower_order)]}
            )
        rules[sp.diff(harmonic, theta, order)] = sp.trigsimp(
            sp.expand_trig(previous)
        )
    return rules


def reduce_derivatives(
    expression: sp.Expr,
    harmonic: sp.Expr,
    theta: sp.Symbol,
    eigenvalue: sp.Expr,
    maximum_order: int = 6,
) -> sp.Expr:
    rules = derivative_rules(harmonic, theta, eigenvalue, maximum_order)
    reduced = expression
    for order in range(maximum_order, 1, -1):
        reduced = reduced.xreplace(
            {sp.diff(harmonic, theta, order): rules[sp.diff(harmonic, theta, order)]}
        )
    return sp.trigsimp(sp.expand_trig(reduced))


def quadratic_normal_form(
    density: sp.Expr,
    harmonic: sp.Expr,
    theta: sp.Symbol,
    eigenvalue: sp.Expr,
    maximum_order: int = 6,
    primitive_degree: int = 8,
) -> QuadraticHarmonicNormalForm:
    """Reduce ``density`` to ``c*sin(theta)*Y^2`` modulo a derivative.

    The calculation is transported to ``z=cos(theta)``, where the Legendre
    equation is polynomial.  A pole-vanishing primitive

        F=A(z)y^2+B(z)y y_z+C(z)y_z^2

    is solved coefficientwise with ``C=(1-z^2) polynomial(z)``.  This includes
    the derivative-squared primitive required by the certified axial current.
    """

    first = sp.diff(harmonic, theta)
    reduced = reduce_derivatives(
        density, harmonic, theta, eigenvalue, maximum_order
    )
    z = sp.Symbol("harmonic_z", real=True)
    z_harmonic = sp.Function("harmonic_profile")(z)
    z_first = sp.diff(z_harmonic, z)
    radial = sp.sqrt(1 - z**2)
    z_density = sp.expand_trig(reduced / sp.sin(theta)).xreplace(
        {harmonic: z_harmonic, first: -radial * z_first}
    )
    z_density = z_density.subs(
        {
            sp.sin(theta): radial,
            sp.cos(theta): z,
            sp.tan(theta): radial / z,
            sp.cot(theta): z / radial,
            sp.sec(theta): 1 / z,
            sp.csc(theta): 1 / radial,
        },
        simultaneous=True,
    )
    z_density = sp.factor(sp.powdenest(sp.simplify(z_density), force=True))
    value_symbol, derivative_symbol = sp.symbols("harmonic_value harmonic_derivative")
    polynomial_expression = sp.expand(
        z_density.xreplace(
            {z_harmonic: value_symbol, z_first: derivative_symbol}
        )
    )
    polynomial = sp.Poly(polynomial_expression, value_symbol, derivative_symbol)
    allowed = {(2, 0), (1, 1), (0, 2)}
    _require(
        set(polynomial.monoms()).issubset(allowed),
        f"density is not homogeneous quadratic in Y,Y': {polynomial.monoms()}",
    )
    q_value = polynomial.coeff_monomial(value_symbol**2)
    q_mixed = polynomial.coeff_monomial(value_symbol * derivative_symbol)
    q_derivative = polynomial.coeff_monomial(derivative_symbol**2)

    coefficients = sp.symbols(f"primitive_c0:{primitive_degree + 1}")
    canonical_symbol = sp.Symbol("canonical_coefficient")
    primitive_derivative = (1 - z**2) * sum(
        coefficient * z**degree
        for degree, coefficient in enumerate(coefficients)
    )
    primitive_mixed = sp.factor(
        q_derivative
        - sp.diff(primitive_derivative, z)
        - 4 * z * primitive_derivative / (1 - z**2)
    )
    primitive_value = sp.factor(
        (
            q_mixed
            - sp.diff(primitive_mixed, z)
            - 2 * z * primitive_mixed / (1 - z**2)
            + 2 * eigenvalue * primitive_derivative / (1 - z**2)
        )
        / 2
    )
    residual_value = sp.factor(
        q_value
        - sp.diff(primitive_value, z)
        + eigenvalue * primitive_mixed / (1 - z**2)
        - canonical_symbol
    )
    numerator = sp.together(residual_value).as_numer_denom()[0]
    equations = sp.Poly(sp.expand(numerator), z).all_coeffs()
    solution = sp.solve(
        equations,
        (*coefficients, canonical_symbol),
        dict=True,
        simplify=False,
    )
    _require(bool(solution), "no polynomial quadratic primitive was found")
    chosen = solution[0]
    free = set().union(*(value.free_symbols for value in chosen.values())) & set(coefficients)
    chosen.update({symbol: sp.S.Zero for symbol in free})
    canonical = sp.factor(chosen[canonical_symbol].subs(chosen))
    primitive_derivative = sp.factor(primitive_derivative.subs(chosen))
    primitive_mixed = sp.factor(primitive_mixed.subs(chosen))
    primitive_value = sp.factor(primitive_value.subs(chosen))
    for endpoint in (-1, 1):
        for name, coefficient in (
            ("value", primitive_value),
            ("mixed", primitive_mixed),
            ("derivative", primitive_derivative),
        ):
            _require(
                sp.simplify(sp.limit(coefficient, z, endpoint)) == 0,
                f"{name} primitive coefficient does not vanish at z={endpoint}",
            )
    primitive = sp.factor(
        primitive_value * z_harmonic**2
        + primitive_mixed * z_harmonic * z_first
        + primitive_derivative * z_first**2
    )
    z_second_rule = (
        2 * z * z_first - eigenvalue * z_harmonic
    ) / (1 - z**2)
    remainder = sp.factor(
        sp.together(
            z_density
            - canonical * z_harmonic**2
            - sp.diff(primitive, z)
        ).xreplace({sp.diff(z_harmonic, z, 2): z_second_rule})
    )
    remainder = sp.simplify(remainder)
    _require(remainder == 0, "quadratic harmonic normal-form remainder is nonzero")
    return QuadraticHarmonicNormalForm(
        reduced_density=reduced,
        canonical_coefficient=canonical,
        primitive=primitive,
        remainder=remainder,
    )

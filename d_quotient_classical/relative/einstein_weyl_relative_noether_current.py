"""Local polarized relative Noether currents on the product background.

The stabilizer action on the Maxwell perturbation uses the gauge-covariant
lift ``i_X da``.  This is globally defined for a connection difference on the
fixed bundle and differs from the coordinate Lie derivative by a linear U(1)
gauge transformation.
"""

from __future__ import annotations

import sympy as sp

from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    DIMENSION,
    einstein_maxwell_current_component,
    exterior_derivative,
    weyl_maxwell_current_component,
)


Variation = tuple[sp.Matrix, sp.Matrix]


def lie_derivative_metric(
    metric_variation: sp.Matrix,
    generator: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
) -> sp.Matrix:
    """Linear stabilizer action on a covariant symmetric two-tensor."""

    if metric_variation.shape != (DIMENSION, DIMENSION) or generator.shape != (DIMENSION, 1):
        raise ValueError("metric variation or generator has the wrong shape")
    return sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda mu, nu: sp.factor(
            sum(generator[rho] * sp.diff(metric_variation[mu, nu], coordinates[rho]) for rho in range(DIMENSION))
            + sum(metric_variation[rho, nu] * sp.diff(generator[rho], coordinates[mu]) for rho in range(DIMENSION))
            + sum(metric_variation[mu, rho] * sp.diff(generator[rho], coordinates[nu]) for rho in range(DIMENSION))
        ),
    )


def gauge_covariant_lie_derivative_potential(
    potential_variation: sp.Matrix,
    generator: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
) -> sp.Matrix:
    """Return ``i_X da`` for a fixed-bundle Maxwell perturbation."""

    if potential_variation.shape != (DIMENSION, 1) or generator.shape != (DIMENSION, 1):
        raise ValueError("potential variation or generator has the wrong shape")
    field_variation = exterior_derivative(potential_variation, coordinates)
    return sp.Matrix(
        DIMENSION,
        1,
        lambda mu, _: sp.factor(sum(generator[rho] * field_variation[rho, mu] for rho in range(DIMENSION))),
    )


def stabilizer_action(
    variation: Variation,
    generator: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
) -> Variation:
    metric_variation, potential_variation = variation
    return (
        lie_derivative_metric(metric_variation, generator, coordinates),
        gauge_covariant_lie_derivative_potential(potential_variation, generator, coordinates),
    )


def relative_symplectic_current_component(
    metric: sp.Matrix,
    field: sp.Matrix,
    first: Variation,
    second: Variation,
    coordinates: tuple[sp.Symbol, ...],
    component: int,
    *,
    alpha_b: sp.Expr = sp.Integer(3),
    kappa: sp.Expr = sp.Integer(1),
) -> sp.Expr:
    """Return ``omega_WM - omega_EM`` in one vector-density component."""

    target = weyl_maxwell_current_component(
        metric, field, first, second, coordinates, component, alpha_b
    )
    source = einstein_maxwell_current_component(
        metric, field, first, second, coordinates, component, kappa
    )
    return sp.factor(target - source)


def polarized_relative_noether_current_component(
    metric: sp.Matrix,
    field: sp.Matrix,
    first: Variation,
    second: Variation,
    generator: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    component: int,
    *,
    alpha_b: sp.Expr = sp.Integer(3),
    kappa: sp.Expr = sp.Integer(1),
) -> sp.Expr:
    """Return the symmetric Hessian current for one stabilizer generator."""

    action_first = stabilizer_action(first, generator, coordinates)
    action_second = stabilizer_action(second, generator, coordinates)
    left = relative_symplectic_current_component(
        metric, field, first, action_second, coordinates, component, alpha_b=alpha_b, kappa=kappa
    )
    right = relative_symplectic_current_component(
        metric, field, second, action_first, coordinates, component, alpha_b=alpha_b, kappa=kappa
    )
    return sp.factor((left + right) / 2)


def polarized_relative_noether_current(
    metric: sp.Matrix,
    field: sp.Matrix,
    first: Variation,
    second: Variation,
    generator: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    *,
    alpha_b: sp.Expr = sp.Integer(3),
    kappa: sp.Expr = sp.Integer(1),
) -> sp.Matrix:
    """Return all four components of the local relative current density."""

    return sp.Matrix(
        DIMENSION,
        1,
        lambda component, _: polarized_relative_noether_current_component(
            metric,
            field,
            first,
            second,
            generator,
            coordinates,
            component,
            alpha_b=alpha_b,
            kappa=kappa,
        ),
    )

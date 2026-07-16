"""Exact coordinate Lee--Wald currents for the product-background kill tests.

The curvature-squared potential is evaluated through the curvature momentum

    P^{abcd}=d[(alpha_B/8) C^2]/dR_abcd=(alpha_B/4) C^{abcd}.

All objects are linearized before contraction.  In particular the variation
of ``nabla P`` is retained even though the locally symmetric background obeys
``nabla C=0``.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


DIMENSION = 4


def _rank4_zero() -> list[list[list[list[sp.Expr]]]]:
    return [
        [
            [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]


def _connection(
    metric: sp.Matrix, inverse: sp.Matrix, coordinates: tuple[sp.Symbol, ...]
) -> list[list[list[sp.Expr]]]:
    return [
        [
            [
                sp.simplify(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(DIMENSION)
                    )
                    / 2
                )
                for right in range(DIMENSION)
            ]
            for left in range(DIMENSION)
        ]
        for target in range(DIMENSION)
    ]


def _delta_connection(
    metric: sp.Matrix,
    inverse: sp.Matrix,
    inverse_variation: sp.Matrix,
    variation: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
) -> list[list[list[sp.Expr]]]:
    result = [
        [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for target in range(DIMENSION):
        for left in range(DIMENSION):
            for right in range(DIMENSION):
                background_part = sum(
                    inverse_variation[target, index]
                    * (
                        sp.diff(metric[index, right], coordinates[left])
                        + sp.diff(metric[index, left], coordinates[right])
                        - sp.diff(metric[left, right], coordinates[index])
                    )
                    for index in range(DIMENSION)
                )
                variation_part = sum(
                    inverse[target, index]
                    * (
                        sp.diff(variation[index, right], coordinates[left])
                        + sp.diff(variation[index, left], coordinates[right])
                        - sp.diff(variation[left, right], coordinates[index])
                    )
                    for index in range(DIMENSION)
                )
                result[target][left][right] = sp.simplify(
                    (background_part + variation_part) / 2
                )
    return result


def _riemann_and_variation(
    connection: list[list[list[sp.Expr]]],
    connection_variation: list[list[list[sp.Expr]]],
    coordinates: tuple[sp.Symbol, ...],
) -> tuple[list[list[list[list[sp.Expr]]]], list[list[list[list[sp.Expr]]]]]:
    riemann = _rank4_zero()
    variation = _rank4_zero()
    for target in range(DIMENSION):
        for source in range(DIMENSION):
            for left in range(DIMENSION):
                for right in range(DIMENSION):
                    base = (
                        sp.diff(connection[target][right][source], coordinates[left])
                        - sp.diff(connection[target][left][source], coordinates[right])
                    )
                    delta = (
                        sp.diff(
                            connection_variation[target][right][source],
                            coordinates[left],
                        )
                        - sp.diff(
                            connection_variation[target][left][source],
                            coordinates[right],
                        )
                    )
                    for index in range(DIMENSION):
                        base += (
                            connection[target][left][index]
                            * connection[index][right][source]
                            - connection[target][right][index]
                            * connection[index][left][source]
                        )
                        delta += (
                            connection_variation[target][left][index]
                            * connection[index][right][source]
                            + connection[target][left][index]
                            * connection_variation[index][right][source]
                            - connection_variation[target][right][index]
                            * connection[index][left][source]
                            - connection[target][right][index]
                            * connection_variation[index][left][source]
                        )
                    riemann[target][source][left][right] = sp.simplify(base)
                    variation[target][source][left][right] = sp.simplify(delta)
    return riemann, variation


def _weyl_lower_and_variation(
    metric: sp.Matrix,
    inverse: sp.Matrix,
    metric_variation: sp.Matrix,
    inverse_variation: sp.Matrix,
    connection: list[list[list[sp.Expr]]],
    connection_variation: list[list[list[sp.Expr]]],
    coordinates: tuple[sp.Symbol, ...],
) -> tuple[list[list[list[list[sp.Expr]]]], list[list[list[list[sp.Expr]]]]]:
    riemann_up, delta_riemann_up = _riemann_and_variation(
        connection, connection_variation, coordinates
    )
    ricci = sp.zeros(DIMENSION)
    delta_ricci = sp.zeros(DIMENSION)
    for source in range(DIMENSION):
        for right in range(DIMENSION):
            ricci[source, right] = sp.simplify(
                sum(
                    riemann_up[target][source][target][right]
                    for target in range(DIMENSION)
                )
            )
            delta_ricci[source, right] = sp.simplify(
                sum(
                    delta_riemann_up[target][source][target][right]
                    for target in range(DIMENSION)
                )
            )
    scalar = sp.simplify(
        sum(inverse[left, right] * ricci[left, right] for left in range(DIMENSION) for right in range(DIMENSION))
    )
    delta_scalar = sp.simplify(
        sum(
            inverse_variation[left, right] * ricci[left, right]
            + inverse[left, right] * delta_ricci[left, right]
            for left in range(DIMENSION)
            for right in range(DIMENSION)
        )
    )
    riemann_lower = _rank4_zero()
    delta_riemann_lower = _rank4_zero()
    for first in range(DIMENSION):
        for second in range(DIMENSION):
            for third in range(DIMENSION):
                for fourth in range(DIMENSION):
                    riemann_lower[first][second][third][fourth] = sp.simplify(
                        sum(
                            metric[first, target]
                            * riemann_up[target][second][third][fourth]
                            for target in range(DIMENSION)
                        )
                    )
                    delta_riemann_lower[first][second][third][fourth] = sp.simplify(
                        sum(
                            metric_variation[first, target]
                            * riemann_up[target][second][third][fourth]
                            + metric[first, target]
                            * delta_riemann_up[target][second][third][fourth]
                            for target in range(DIMENSION)
                        )
                    )
    weyl = _rank4_zero()
    delta_weyl = _rank4_zero()
    for first in range(DIMENSION):
        for second in range(DIMENSION):
            for third in range(DIMENSION):
                for fourth in range(DIMENSION):
                    trace_piece = (
                        metric[first, third] * ricci[second, fourth]
                        - metric[first, fourth] * ricci[second, third]
                        - metric[second, third] * ricci[first, fourth]
                        + metric[second, fourth] * ricci[first, third]
                    )
                    delta_trace_piece = (
                        metric_variation[first, third] * ricci[second, fourth]
                        + metric[first, third] * delta_ricci[second, fourth]
                        - metric_variation[first, fourth] * ricci[second, third]
                        - metric[first, fourth] * delta_ricci[second, third]
                        - metric_variation[second, third] * ricci[first, fourth]
                        - metric[second, third] * delta_ricci[first, fourth]
                        + metric_variation[second, fourth] * ricci[first, third]
                        + metric[second, fourth] * delta_ricci[first, third]
                    )
                    metric_pair = (
                        metric[first, third] * metric[second, fourth]
                        - metric[first, fourth] * metric[second, third]
                    )
                    delta_metric_pair = (
                        metric_variation[first, third] * metric[second, fourth]
                        + metric[first, third] * metric_variation[second, fourth]
                        - metric_variation[first, fourth] * metric[second, third]
                        - metric[first, fourth] * metric_variation[second, third]
                    )
                    weyl[first][second][third][fourth] = sp.simplify(
                        riemann_lower[first][second][third][fourth]
                        - trace_piece / 2
                        + scalar * metric_pair / 6
                    )
                    delta_weyl[first][second][third][fourth] = sp.simplify(
                        delta_riemann_lower[first][second][third][fourth]
                        - delta_trace_piece / 2
                        + delta_scalar * metric_pair / 6
                        + scalar * delta_metric_pair / 6
                    )
    return weyl, delta_weyl


def _raise_weyl_and_variation(
    weyl: list[list[list[list[sp.Expr]]]],
    delta_weyl: list[list[list[list[sp.Expr]]]],
    inverse: sp.Matrix,
    inverse_variation: sp.Matrix,
) -> tuple[list[list[list[list[sp.Expr]]]], list[list[list[list[sp.Expr]]]]]:
    raised = _rank4_zero()
    delta_raised = _rank4_zero()
    diagonal = [inverse[index, index] for index in range(DIMENSION)]
    for first in range(DIMENSION):
        for second in range(DIMENSION):
            for third in range(DIMENSION):
                for fourth in range(DIMENSION):
                    scale = diagonal[first] * diagonal[second] * diagonal[third] * diagonal[fourth]
                    raised[first][second][third][fourth] = sp.simplify(
                        scale * weyl[first][second][third][fourth]
                    )
                    delta = scale * delta_weyl[first][second][third][fourth]
                    for replacement in range(DIMENSION):
                        delta += (
                            inverse_variation[first, replacement]
                            * diagonal[second]
                            * diagonal[third]
                            * diagonal[fourth]
                            * weyl[replacement][second][third][fourth]
                            + diagonal[first]
                            * inverse_variation[second, replacement]
                            * diagonal[third]
                            * diagonal[fourth]
                            * weyl[first][replacement][third][fourth]
                            + diagonal[first]
                            * diagonal[second]
                            * inverse_variation[third, replacement]
                            * diagonal[fourth]
                            * weyl[first][second][replacement][fourth]
                            + diagonal[first]
                            * diagonal[second]
                            * diagonal[third]
                            * inverse_variation[fourth, replacement]
                            * weyl[first][second][third][replacement]
                        )
                    delta_raised[first][second][third][fourth] = sp.simplify(delta)
    return raised, delta_raised


@dataclass(frozen=True)
class LinearizedGeometry:
    metric: sp.Matrix
    inverse: sp.Matrix
    volume: sp.Expr
    connection: list[list[list[sp.Expr]]]
    inverse_variation: sp.Matrix
    volume_variation: sp.Expr
    connection_variation: list[list[list[sp.Expr]]]
    weyl_up: list[list[list[list[sp.Expr]]]]
    delta_weyl_up: list[list[list[list[sp.Expr]]]]


def linearized_geometry(
    metric: sp.Matrix,
    variation: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
) -> LinearizedGeometry:
    inverse = metric.inv()
    inverse_variation = sp.simplify(-inverse * variation * inverse)
    sine = sp.sin(coordinates[2])
    volume = sp.sqrt(-metric.det()).subs(sp.Abs(sine), sine)
    trace = sp.simplify(
        sum(inverse[left, right] * variation[left, right] for left in range(DIMENSION) for right in range(DIMENSION))
    )
    volume_variation = sp.simplify(volume * trace / 2)
    connection = _connection(metric, inverse, coordinates)
    connection_variation = _delta_connection(
        metric, inverse, inverse_variation, variation, coordinates
    )
    weyl_lower, delta_weyl_lower = _weyl_lower_and_variation(
        metric,
        inverse,
        variation,
        inverse_variation,
        connection,
        connection_variation,
        coordinates,
    )
    weyl_up, delta_weyl_up = _raise_weyl_and_variation(
        weyl_lower, delta_weyl_lower, inverse, inverse_variation
    )
    return LinearizedGeometry(
        metric=metric,
        inverse=inverse,
        volume=volume,
        connection=connection,
        inverse_variation=inverse_variation,
        volume_variation=volume_variation,
        connection_variation=connection_variation,
        weyl_up=weyl_up,
        delta_weyl_up=delta_weyl_up,
    )


def _nabla_covariant_two(
    tensor: sp.Matrix,
    connection: list[list[list[sp.Expr]]],
    coordinates: tuple[sp.Symbol, ...],
    derivative: int,
    first: int,
    second: int,
) -> sp.Expr:
    return sp.simplify(
        sp.diff(tensor[first, second], coordinates[derivative])
        - sum(
            connection[target][derivative][first] * tensor[target, second]
            + connection[target][derivative][second] * tensor[first, target]
            for target in range(DIMENSION)
        )
    )


def _delta_nabla_covariant_two(
    tensor: sp.Matrix,
    connection_variation: list[list[list[sp.Expr]]],
    derivative: int,
    first: int,
    second: int,
) -> sp.Expr:
    return sp.simplify(
        -sum(
            connection_variation[target][derivative][first] * tensor[target, second]
            + connection_variation[target][derivative][second] * tensor[first, target]
            for target in range(DIMENSION)
        )
    )


def _divergence_rank4_component(
    tensor: list[list[list[list[sp.Expr]]]],
    connection: list[list[list[sp.Expr]]],
    coordinates: tuple[sp.Symbol, ...],
    first: int,
    second: int,
    third: int,
) -> sp.Expr:
    result = sp.S.Zero
    for derivative in range(DIMENSION):
        result += sp.diff(
            tensor[first][second][third][derivative], coordinates[derivative]
        )
        for target in range(DIMENSION):
            result += (
                connection[first][derivative][target]
                * tensor[target][second][third][derivative]
                + connection[second][derivative][target]
                * tensor[first][target][third][derivative]
                + connection[third][derivative][target]
                * tensor[first][second][target][derivative]
                + connection[derivative][derivative][target]
                * tensor[first][second][third][target]
            )
    return sp.simplify(result)


def _delta_divergence_rank4_component(
    tensor: list[list[list[list[sp.Expr]]]],
    delta_tensor: list[list[list[list[sp.Expr]]]],
    connection: list[list[list[sp.Expr]]],
    delta_connection: list[list[list[sp.Expr]]],
    coordinates: tuple[sp.Symbol, ...],
    first: int,
    second: int,
    third: int,
) -> sp.Expr:
    result = sp.S.Zero
    for derivative in range(DIMENSION):
        result += sp.diff(
            delta_tensor[first][second][third][derivative],
            coordinates[derivative],
        )
        for target in range(DIMENSION):
            result += (
                delta_connection[first][derivative][target]
                * tensor[target][second][third][derivative]
                + connection[first][derivative][target]
                * delta_tensor[target][second][third][derivative]
                + delta_connection[second][derivative][target]
                * tensor[first][target][third][derivative]
                + connection[second][derivative][target]
                * delta_tensor[first][target][third][derivative]
                + delta_connection[third][derivative][target]
                * tensor[first][second][target][derivative]
                + connection[third][derivative][target]
                * delta_tensor[first][second][target][derivative]
                + delta_connection[derivative][derivative][target]
                * tensor[first][second][third][target]
                + connection[derivative][derivative][target]
                * delta_tensor[first][second][third][target]
            )
    return sp.simplify(result)


def _momentum_theta_time_variation(
    geometry: LinearizedGeometry,
    test_metric: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    momentum: list[list[list[list[sp.Expr]]]],
    momentum_variation: list[list[list[list[sp.Expr]]]],
) -> sp.Expr:
    """Return the first variation of the f(g,Riemann) potential."""

    base_bracket = sp.S.Zero
    delta_bracket = sp.S.Zero
    mu = 0
    for first in range(DIMENSION):
        for second in range(DIMENSION):
            divergence = _divergence_rank4_component(
                momentum,
                geometry.connection,
                coordinates,
                mu,
                first,
                second,
            )
            delta_divergence = _delta_divergence_rank4_component(
                momentum,
                momentum_variation,
                geometry.connection,
                geometry.connection_variation,
                coordinates,
                mu,
                first,
                second,
            )
            base_contraction = sp.S.Zero
            delta_contraction = sp.S.Zero
            for derivative in range(DIMENSION):
                nabla_test = _nabla_covariant_two(
                    test_metric,
                    geometry.connection,
                    coordinates,
                    derivative,
                    first,
                    second,
                )
                delta_nabla_test = _delta_nabla_covariant_two(
                    test_metric,
                    geometry.connection_variation,
                    derivative,
                    first,
                    second,
                )
                base_contraction += (
                    momentum[mu][first][second][derivative]
                    * nabla_test
                )
                delta_contraction += (
                    momentum_variation[mu][first][second][derivative]
                    * nabla_test
                    + momentum[mu][first][second][derivative]
                    * delta_nabla_test
                )
            base_bracket += base_contraction - divergence * test_metric[first, second]
            delta_bracket += (
                delta_contraction - delta_divergence * test_metric[first, second]
            )
    return sp.factor(
        2
        * (
            geometry.volume_variation * base_bracket
            + geometry.volume * delta_bracket
        )
    )


def weyl_theta_time_variation(
    geometry: LinearizedGeometry,
    test_metric: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    alpha_b: sp.Expr,
) -> sp.Expr:
    """Return delta_1 Theta_C2^t(delta_2 g) as a vector density."""

    momentum = _rank4_zero()
    momentum_variation = _rank4_zero()
    for first in range(DIMENSION):
        for second in range(DIMENSION):
            for third in range(DIMENSION):
                for fourth in range(DIMENSION):
                    momentum[first][second][third][fourth] = (
                        alpha_b
                        * geometry.weyl_up[first][second][third][fourth]
                        / 4
                    )
                    momentum_variation[first][second][third][fourth] = (
                        alpha_b
                        * geometry.delta_weyl_up[first][second][third][fourth]
                        / 4
                    )
    return _momentum_theta_time_variation(
        geometry,
        test_metric,
        coordinates,
        momentum,
        momentum_variation,
    )


def einstein_theta_time_variation(
    geometry: LinearizedGeometry,
    test_metric: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    kappa: sp.Expr = sp.Integer(1),
) -> sp.Expr:
    """Curvature-momentum evaluation for (R-2 Lambda)/(2 kappa)."""

    momentum = _rank4_zero()
    momentum_variation = _rank4_zero()
    inverse = geometry.inverse
    delta_inverse = geometry.inverse_variation
    for first in range(DIMENSION):
        for second in range(DIMENSION):
            for third in range(DIMENSION):
                for fourth in range(DIMENSION):
                    momentum[first][second][third][fourth] = (
                        inverse[first, third] * inverse[second, fourth]
                        - inverse[first, fourth] * inverse[second, third]
                    ) / (4 * kappa)
                    momentum_variation[first][second][third][fourth] = (
                        delta_inverse[first, third] * inverse[second, fourth]
                        + inverse[first, third] * delta_inverse[second, fourth]
                        - delta_inverse[first, fourth] * inverse[second, third]
                        - inverse[first, fourth] * delta_inverse[second, third]
                    ) / (4 * kappa)
    return _momentum_theta_time_variation(
        geometry,
        test_metric,
        coordinates,
        momentum,
        momentum_variation,
    )


def maxwell_theta_time_variation(
    metric: sp.Matrix,
    field: sp.Matrix,
    metric_variation: sp.Matrix,
    field_variation: sp.Matrix,
    test_potential: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
) -> sp.Expr:
    inverse = metric.inv()
    inverse_variation = sp.simplify(-inverse * metric_variation * inverse)
    sine = sp.sin(coordinates[2])
    volume = sp.sqrt(-metric.det()).subs(sp.Abs(sine), sine)
    trace = sp.simplify(
        sum(inverse[left, right] * metric_variation[left, right] for left in range(DIMENSION) for right in range(DIMENSION))
    )
    delta_volume = sp.simplify(volume * trace / 2)
    field_up = sp.simplify(inverse * field * inverse)
    delta_field_up = sp.simplify(
        inverse_variation * field * inverse
        + inverse * field_variation * inverse
        + inverse * field * inverse_variation
    )
    return sp.factor(
        -sum(
            (
                delta_volume * field_up[0, index]
                + volume * delta_field_up[0, index]
            )
            * test_potential[index]
            for index in range(DIMENSION)
        )
    )


def exterior_derivative(
    potential: sp.Matrix, coordinates: tuple[sp.Symbol, ...]
) -> sp.Matrix:
    return sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda left, right: sp.diff(potential[right], coordinates[left])
        - sp.diff(potential[left], coordinates[right]),
    )


def weyl_maxwell_current_time(
    metric: sp.Matrix,
    field: sp.Matrix,
    first: tuple[sp.Matrix, sp.Matrix],
    second: tuple[sp.Matrix, sp.Matrix],
    coordinates: tuple[sp.Symbol, ...],
    alpha_b: sp.Expr = sp.Integer(3),
) -> sp.Expr:
    first_metric, first_potential = first
    second_metric, second_potential = second
    first_geometry = linearized_geometry(metric, first_metric, coordinates)
    second_geometry = linearized_geometry(metric, second_metric, coordinates)
    first_on_second = weyl_theta_time_variation(
        first_geometry, second_metric, coordinates, alpha_b
    ) + maxwell_theta_time_variation(
        metric,
        field,
        first_metric,
        exterior_derivative(first_potential, coordinates),
        second_potential,
        coordinates,
    )
    second_on_first = weyl_theta_time_variation(
        second_geometry, first_metric, coordinates, alpha_b
    ) + maxwell_theta_time_variation(
        metric,
        field,
        second_metric,
        exterior_derivative(second_potential, coordinates),
        first_potential,
        coordinates,
    )
    return sp.factor(first_on_second - second_on_first)


def einstein_maxwell_current_time(
    metric: sp.Matrix,
    field: sp.Matrix,
    first: tuple[sp.Matrix, sp.Matrix],
    second: tuple[sp.Matrix, sp.Matrix],
    coordinates: tuple[sp.Symbol, ...],
    kappa: sp.Expr = sp.Integer(1),
) -> sp.Expr:
    """Independent curvature-momentum form of the Einstein--Maxwell current."""

    first_metric, first_potential = first
    second_metric, second_potential = second
    first_geometry = linearized_geometry(metric, first_metric, coordinates)
    second_geometry = linearized_geometry(metric, second_metric, coordinates)
    first_on_second = einstein_theta_time_variation(
        first_geometry, second_metric, coordinates, kappa
    ) + maxwell_theta_time_variation(
        metric,
        field,
        first_metric,
        exterior_derivative(first_potential, coordinates),
        second_potential,
        coordinates,
    )
    second_on_first = einstein_theta_time_variation(
        second_geometry, first_metric, coordinates, kappa
    ) + maxwell_theta_time_variation(
        metric,
        field,
        second_metric,
        exterior_derivative(second_potential, coordinates),
        first_potential,
        coordinates,
    )
    return sp.factor(first_on_second - second_on_first)

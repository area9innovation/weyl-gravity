"""Direct full-time a,d cross sources against exceptional ell=1 modes."""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


def _mixed_coefficient(
    expression: sp.Expr,
    epsilon: sp.Symbol,
    global_amplitude: sp.Symbol,
    wave_amplitude: sp.Symbol,
    wave: sp.Expr,
) -> sp.Expr:
    value = (
        sp.diff(
            sp.diff(sp.diff(expression, epsilon, 2) / 2, global_amplitude),
            wave_amplitude,
        )
        .subs(epsilon, 0)
        / wave
    )
    return sp.factor(sp.cancel(_canonical(value)))


def axial_source(global_case: str) -> sp.Matrix:
    epsilon = sp.symbols("epsilon")
    global_amplitude, wave_amplitude = sp.symbols("u v")
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    harmonic = z
    axial_one_form = sphere_factor
    frequency = 2 / sp.sqrt(3)
    wave = sp.exp(-sp.I * frequency * time)

    # Exceptional axial representative (H_t,H_x,Q_t,Q_x)=(0,1,0,-3).
    h_time, h_space, q_time, q_space = (
        wave_amplitude * value * wave for value in (0, 1, 0, -3)
    )
    circle_profile = {"a": time**2, "d": time}[global_case]
    sphere_profile = {"a": sp.Integer(1), "d": sp.Integer(0)}[global_case]

    background_metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    perturbation = sp.zeros(4)
    perturbation[1, 1] = global_amplitude * circle_profile
    perturbation[2, 2] = global_amplitude * sphere_profile / sphere_factor
    perturbation[3, 3] = global_amplitude * sphere_profile * sphere_factor
    perturbation[0, 3] = perturbation[3, 0] = h_time * axial_one_form
    perturbation[1, 3] = perturbation[3, 1] = h_space * axial_one_form
    metric = background_metric + epsilon * perturbation
    background_inverse = sp.diag(-1, 1, sphere_factor, 1 / sphere_factor)
    inverse = (
        background_inverse
        - epsilon * background_inverse * perturbation * background_inverse
        + epsilon**2
        * background_inverse
        * perturbation
        * background_inverse
        * perturbation
        * background_inverse
    ).applyfunc(sp.expand)
    truncate = lambda expression: _trunc(expression, epsilon, 2)
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = truncate(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2
                )
    field = sp.zeros(4)
    field[2, 3] = -1
    field[3, 2] = 1
    field[0, 1] = epsilon * sp.diff(q_space, time) * harmonic
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * q_time * sp.diff(harmonic, z)
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * q_space * sp.diff(harmonic, z)
    field[2, 1] = -field[1, 2]
    data = _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        2,
    )
    metric_equations, maxwell_equations = _equations(data, 2, ((0, 3), (1, 3)))
    rows = [
        2 * metric_equations[(0, 3)] / axial_one_form,
        -2 * metric_equations[(1, 3)] / axial_one_form,
        maxwell_equations[0] / harmonic,
        maxwell_equations[1] / harmonic,
    ]
    return sp.Matrix(
        [
            _mixed_coefficient(
                row, epsilon, global_amplitude, wave_amplitude, wave
            )
            for row in rows
        ]
    )


def polar_source(global_case: str) -> sp.Matrix:
    epsilon = sp.symbols("epsilon")
    global_amplitude, wave_amplitude = sp.symbols("u v")
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    harmonic = z
    polar_one_form = sphere_factor
    frequency = 2 / sp.sqrt(3)
    wave = sp.exp(-sp.I * frequency * time)
    circle_profile = {"a": time**2, "d": time}[global_case]
    sphere_profile = {"a": sp.Integer(1), "d": sp.Integer(0)}[global_case]

    # Exceptional polar representative (A_t,B,C_t,U)=(0,1,0,0).
    metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    metric[0, 1] = metric[1, 0] = epsilon * wave_amplitude * wave * harmonic
    metric[1, 1] += epsilon * global_amplitude * circle_profile
    metric[2, 2] += epsilon * global_amplitude * sphere_profile / sphere_factor
    metric[3, 3] += epsilon * global_amplitude * sphere_profile * sphere_factor
    truncate = lambda expression: _trunc(expression, epsilon, 2)
    inverse = metric.inv().applyfunc(truncate)
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for first in range(4):
            for second in range(4):
                connection[target][first][second] = truncate(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, second], coordinates[first])
                            + sp.diff(metric[index, first], coordinates[second])
                            - sp.diff(metric[first, second], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2
                )
    field = sp.zeros(4)
    field[2, 3] = -1
    field[3, 2] = 1
    data = _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        2,
    )
    metric_equations, maxwell_equations = _equations(
        data, 2, ((0, 0), (0, 1), (1, 1))
    )
    scalar_norm = sp.integrate(harmonic**2, (z, -1, 1))

    def scalar_projection(row: sp.Expr) -> sp.Expr:
        coefficient = _mixed_coefficient(
            row, epsilon, global_amplitude, wave_amplitude, wave
        )
        return _canonical(
            sp.integrate(coefficient * harmonic, (z, -1, 1)) / scalar_norm
        )

    # The exceptional representative has U=0, but the fourth action row is
    # retained for the raw Noether audit.
    maxwell_coefficient = _mixed_coefficient(
        maxwell_equations[3], epsilon, global_amplitude, wave_amplitude, wave
    )
    vector_norm = sp.integrate(
        sphere_factor * sp.diff(harmonic, z) ** 2, (z, -1, 1)
    )
    maxwell_projection = _canonical(
        sp.integrate(
            maxwell_coefficient * sphere_factor * sp.diff(harmonic, z),
            (z, -1, 1),
        )
        / vector_norm
    )
    return sp.Matrix(
        [
            -scalar_projection(metric_equations[(0, 0)]),
            2 * scalar_projection(metric_equations[(0, 1)]),
            -scalar_projection(metric_equations[(1, 1)]),
            4 * maxwell_projection,
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parity", choices=("axial", "polar"), required=True)
    parser.add_argument("--global-case", choices=("a", "d"), required=True)
    arguments = parser.parse_args()
    producer = {"axial": axial_source, "polar": polar_source}[arguments.parity]
    print([str(value) for value in producer(arguments.global_case)])


if __name__ == "__main__":
    main()

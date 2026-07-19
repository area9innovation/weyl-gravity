"""Explore generalized-zero global sources crossed with polar ell=2 Einstein-minus."""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


def source(global_case: str) -> sp.Matrix:
    epsilon = sp.symbols("epsilon")
    polar_amplitude, global_amplitude = sp.symbols("u v")
    root = sp.sqrt(3)
    frequency = sp.sqrt(6 - 2 * root)
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    harmonic = sp.legendre(2, z)
    polar_one_form = sphere_factor * sp.diff(harmonic, z)
    wave = sp.exp(-sp.I * frequency * time)
    a_time, mixed, a_space, maxwell = (12, 0, 12 - 24 * root, 6)
    circle_profile = {"a": time**2, "b": time**3 / 3, "d": time}[global_case]
    sphere_profile = {"a": sp.Integer(1), "b": time, "d": sp.Integer(0)}[global_case]
    trunc = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    metric[0, 0] += epsilon * polar_amplitude * a_time * wave * harmonic
    metric[0, 1] = metric[1, 0] = epsilon * polar_amplitude * mixed * wave * harmonic
    metric[1, 1] += epsilon * (
        polar_amplitude * a_space * wave * harmonic + global_amplitude * circle_profile
    )
    metric[2, 2] += epsilon * global_amplitude * sphere_profile / sphere_factor
    metric[3, 3] += epsilon * global_amplitude * sphere_profile * sphere_factor
    inverse = metric.inv().applyfunc(trunc)
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for first in range(4):
            for second in range(4):
                connection[target][first][second] = trunc(
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
    potential = polar_amplitude * maxwell * wave
    field[2, 3] = -1 + epsilon * potential * sp.diff(polar_one_form, z)
    field[3, 2] = -field[2, 3]
    field[0, 3] = epsilon * sp.diff(potential, time) * polar_one_form
    field[3, 0] = -field[0, 3]
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
    derivative = sp.diff(harmonic, z)
    scalar_norm = sp.integrate(harmonic**2, (z, -1, 1))
    vector_norm = sp.integrate(sphere_factor * derivative**2, (z, -1, 1))

    def mixed_coefficient(row: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.diff(
                sp.diff(sp.diff(row, epsilon, 2) / 2, polar_amplitude),
                global_amplitude,
            ).subs(epsilon, 0)
            / wave
        )

    def linear_coefficient(row: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.diff(sp.diff(row, epsilon).subs(epsilon, 0), polar_amplitude)
            / wave
        )

    def scalar_projection(row: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.integrate(mixed_coefficient(row) * harmonic, (z, -1, 1))
            / scalar_norm
        )

    maxwell_projection = _canonical(
        sp.integrate(
            mixed_coefficient(maxwell_equations[3]) * sphere_factor * derivative,
            (z, -1, 1),
        )
        / vector_norm
    )
    linear_remainder = sp.Matrix(
        [
            -_canonical(
                sp.integrate(
                    linear_coefficient(metric_equations[(0, 0)]) * harmonic,
                    (z, -1, 1),
                )
                / scalar_norm
            ),
            2
            * _canonical(
                sp.integrate(
                    linear_coefficient(metric_equations[(0, 1)]) * harmonic,
                    (z, -1, 1),
                )
                / scalar_norm
            ),
            -_canonical(
                sp.integrate(
                    linear_coefficient(metric_equations[(1, 1)]) * harmonic,
                    (z, -1, 1),
                )
                / scalar_norm
            ),
            12
            * _canonical(
                sp.integrate(
                    linear_coefficient(maxwell_equations[3])
                    * sphere_factor
                    * derivative,
                    (z, -1, 1),
                )
                / vector_norm
            ),
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))
    if linear_remainder != sp.zeros(4, 1):
        raise AssertionError(f"polar Einstein-minus representative is off shell: {linear_remainder}")
    return sp.Matrix(
        [
            -scalar_projection(metric_equations[(0, 0)]),
            2 * scalar_projection(metric_equations[(0, 1)]),
            -scalar_projection(metric_equations[(1, 1)]),
            12 * maxwell_projection,
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))


def shell_pairing(value: sp.Matrix) -> sp.Expr:
    root = sp.sqrt(3)
    return sp.factor((sp.Matrix([12, 0, 12 - 24 * root, 6]).T * value)[0])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-case", choices=("a", "b", "d"), required=True)
    arguments = parser.parse_args()
    value = source(arguments.global_case)
    print([str(entry) for entry in value])
    print("shell_pairing", shell_pairing(value))


if __name__ == "__main__":
    main()

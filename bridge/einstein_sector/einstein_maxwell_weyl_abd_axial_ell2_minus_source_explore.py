"""Explore generalized-zero global sources crossed with axial Einstein-minus."""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


def source(global_case: str, degree: int = 2) -> sp.Matrix:
    if degree < 2:
        raise ValueError("the generic axial helper requires ell>=2")
    epsilon = sp.symbols("epsilon")
    global_amplitude, wave_amplitude = sp.symbols("u v")
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    eigenvalue = sp.Integer(degree * (degree + 1))
    branch_gap = sp.sqrt(2 * eigenvalue)
    harmonic = sp.legendre(degree, z)
    axial_one_form = sphere_factor * sp.diff(harmonic, z)
    frequency = sp.sqrt(eigenvalue - branch_gap)
    wave = sp.exp(-sp.I * frequency * time)
    h_time, h_space, q_time, q_space = [
        wave_amplitude * value * wave
        for value in (0, -2, 0, branch_gap)
    ]
    circle_profile = {
        "a": time**2,
        "b": time**3 / 3,
        "d": time,
    }[global_case]
    sphere_profile = {
        "a": sp.Integer(1),
        "b": time,
        "d": sp.Integer(0),
    }[global_case]
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
    trunc = lambda expression: _trunc(expression, epsilon, 2)
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = trunc(
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
        6 * metric_equations[(0, 3)] / axial_one_form,
        -6 * metric_equations[(1, 3)] / axial_one_form,
        maxwell_equations[0] / harmonic,
        maxwell_equations[1] / harmonic,
    ]
    values = []
    for row in rows:
        mixed = (
            sp.diff(
                sp.diff(sp.diff(row, epsilon, 2) / 2, global_amplitude),
                wave_amplitude,
            ).subs(epsilon, 0)
            / wave
        )
        values.append(sp.factor(sp.cancel(_canonical(mixed))))
    return sp.Matrix(values)


def shell_pairing(value: sp.Matrix, degree: int = 2) -> sp.Expr:
    """Pair against the k=0 self-adjoint Einstein-minus kernel vector."""
    eigenvalue = sp.Integer(degree * (degree + 1))
    return sp.factor((sp.Matrix([0, -2, 0, sp.sqrt(2 * eigenvalue)]).T * value)[0])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-case", choices=("a", "b", "d"), required=True)
    parser.add_argument("--degree", type=int, default=2)
    arguments = parser.parse_args()
    value = source(arguments.global_case, arguments.degree)
    print([str(entry) for entry in value])
    print("shell_pairing", shell_pairing(value, arguments.degree))


if __name__ == "__main__":
    main()

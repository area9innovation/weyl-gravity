"""Direct generic-lambda highest pivots for global b times Einstein-minus.

The calculation uses formal Legendre jets at the regular point z=0.  Scalar
outputs use the even jet Y(0)=1,Y'(0)=0; axial-vector outputs use the odd jet
Y(0)=0,Y'(0)=1.  The Legendre ODE fixes every higher derivative, so this is a
generic eigenvalue calculation rather than finite-ell interpolation.
"""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


def _legendre_jet(
    z: sp.Symbol,
    eigenvalue: sp.Expr,
    value: sp.Expr,
    derivative: sp.Expr,
    order: int = 8,
) -> sp.Expr:
    coefficients = [sp.S.Zero] * (order + 1)
    coefficients[0] = value
    coefficients[1] = derivative
    for degree in range(order - 1):
        coefficients[degree + 2] = sp.factor(
            (degree * (degree + 1) - eigenvalue)
            * coefficients[degree]
            / ((degree + 2) * (degree + 1))
        )
    return sp.Add(
        *(coefficient * z**degree for degree, coefficient in enumerate(coefficients))
    )


def _connection(
    metric: sp.Matrix,
    inverse: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    epsilon: sp.Symbol,
) -> list[list[list[sp.Expr]]]:
    trunc = lambda expression: _trunc(expression, epsilon, 2)
    result = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                result[target][left][right] = trunc(
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
    return result


def _data(
    epsilon: sp.Symbol,
    coordinates: tuple[sp.Symbol, ...],
    metric: sp.Matrix,
    inverse: sp.Matrix,
    field: sp.Matrix,
) -> dict[str, object]:
    return _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": _connection(metric, inverse, coordinates, epsilon),
            "field": field,
        },
        2,
    )


def axial_b_pivot() -> sp.Expr:
    epsilon = sp.symbols("epsilon")
    global_amplitude, wave_amplitude = sp.symbols("u v")
    eigenvalue = sp.symbols("lambda", positive=True)
    gap = sp.sqrt(2 * eigenvalue)
    frequency = sp.sqrt(eigenvalue - gap)
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    harmonic = _legendre_jet(z, eigenvalue, sp.S.Zero, sp.S.One)
    axial_one_form = sphere_factor * sp.diff(harmonic, z)
    wave = sp.exp(-sp.I * frequency * time)

    background_metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    perturbation = sp.zeros(4)
    # The b-mode t^2 pivot contains exactly one derivative of t^3/3.
    # Replace that profile by t and evaluate at t=0; terms with no derivative
    # retain a factor of t, while two or more derivatives vanish.
    perturbation[1, 1] = global_amplitude * time
    perturbation[1, 3] = perturbation[3, 1] = -2 * wave_amplitude * wave * axial_one_form
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
    field = sp.zeros(4)
    field[2, 3] = -1
    field[3, 2] = 1
    q_space = wave_amplitude * gap * wave
    field[0, 1] = epsilon * sp.diff(q_space, time) * harmonic
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * q_space * sp.diff(harmonic, z)
    field[2, 1] = -field[1, 2]
    metric_equations, _ = _equations(
        _data(epsilon, coordinates, metric, inverse, field), 2, ((1, 3),)
    )
    row = -6 * metric_equations[(1, 3)] / axial_one_form
    mixed = sp.diff(
        sp.diff(sp.diff(row, epsilon, 2) / 2, global_amplitude),
        wave_amplitude,
    ).subs(epsilon, 0) / wave
    pivot = sp.expand(mixed.subs({z: 0, time: 0}))
    return sp.factor(_canonical(pivot))


def polar_b_pivot() -> sp.Expr:
    epsilon = sp.symbols("epsilon")
    polar_amplitude, global_amplitude = sp.symbols("v u")
    eigenvalue = sp.symbols("lambda", positive=True)
    gap = sp.sqrt(2 * eigenvalue)
    frequency = sp.sqrt(eigenvalue - gap)
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    harmonic = _legendre_jet(z, eigenvalue, sp.S.One, sp.S.Zero)
    polar_one_form = sphere_factor * sp.diff(harmonic, z)
    wave = sp.exp(-sp.I * frequency * time)

    metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    metric[0, 0] += epsilon * polar_amplitude * 2 * eigenvalue * wave * harmonic
    metric[1, 1] += epsilon * (
        polar_amplitude * 2 * eigenvalue * (1 - gap) * wave * harmonic
        + global_amplitude
    )
    inverse = metric.inv().applyfunc(lambda expression: _trunc(expression, epsilon, 2))
    field = sp.zeros(4)
    potential = polar_amplitude * eigenvalue * wave
    field[2, 3] = -1 + epsilon * potential * sp.diff(polar_one_form, z)
    field[3, 2] = -field[2, 3]
    field[0, 3] = epsilon * sp.diff(potential, time) * polar_one_form
    field[3, 0] = -field[0, 3]
    metric_equations, _ = _equations(
        _data(epsilon, coordinates, metric, inverse, field), 2, ((0, 0),)
    )
    row = -metric_equations[(0, 0)]
    mixed = sp.diff(
        sp.diff(sp.diff(row, epsilon, 2) / 2, polar_amplitude),
        global_amplitude,
    ).subs(epsilon, 0) / wave
    # The polar b t^3 pivot is the no-derivative response to t^3/3.
    pivot = sp.expand(mixed.subs({z: 0, time: 0})) / 3
    return sp.factor(_canonical(pivot))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parity", choices=("axial", "polar"), required=True)
    arguments = parser.parse_args()
    value = axial_b_pivot() if arguments.parity == "axial" else polar_b_pivot()
    print(sp.factor(value))


if __name__ == "__main__":
    main()

"""Direct exceptional-ell1 times ell2-extra difference-frequency sources."""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


AXIAL_EXCEPTIONAL = (0, 1, 0, -3)
POLAR_EXCEPTIONAL = (0, 1, 0, 0)
AXIAL_EXTRA = {
    "e1": (-6, 0, 6, 0),
    "e2": (0, -sp.Rational(2, 3), 0, 6),
}
POLAR_EXTRA = {
    "e1": (0, 1, 0, 0),
    "e2": (-8, 0, -72, 48),
}


def _project_scalar(expression: sp.Expr, harmonic: sp.Expr, z: sp.Symbol) -> sp.Expr:
    norm = sp.integrate(harmonic**2, (z, -1, 1))
    return _canonical(sp.integrate(expression * harmonic, (z, -1, 1)) / norm)


def source(exceptional_parity: str, extra_parity: str, extra_case: str) -> sp.Matrix:
    epsilon = sp.symbols("epsilon")
    exceptional_amplitude, extra_amplitude = sp.symbols("u v")
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    exceptional_harmonic = z
    extra_harmonic = sp.legendre(2, z)
    exceptional_axial = sphere_factor
    extra_axial = sphere_factor * sp.diff(extra_harmonic, z)
    exceptional_polar = sphere_factor
    extra_polar = sphere_factor * sp.diff(extra_harmonic, z)
    omega = 2 / sp.sqrt(3)
    exceptional_wave = sp.exp(sp.I * omega * time)
    extra_wave = sp.exp(-2 * sp.I * omega * time)
    output_wave = sp.exp(-sp.I * omega * time)

    perturbation = sp.zeros(4)
    field = sp.zeros(4)
    field[2, 3] = -1
    field[3, 2] = 1

    if exceptional_parity == "axial":
        ht, hx, qt, qx = [exceptional_amplitude * value * exceptional_wave for value in AXIAL_EXCEPTIONAL]
        perturbation[0, 3] += ht * exceptional_axial
        perturbation[3, 0] += ht * exceptional_axial
        perturbation[1, 3] += hx * exceptional_axial
        perturbation[3, 1] += hx * exceptional_axial
        field[0, 1] += epsilon * sp.diff(qx, time) * exceptional_harmonic
        field[1, 0] = -field[0, 1]
        field[0, 2] += -epsilon * qt * sp.diff(exceptional_harmonic, z)
        field[2, 0] = -field[0, 2]
        field[1, 2] += -epsilon * qx * sp.diff(exceptional_harmonic, z)
        field[2, 1] = -field[1, 2]
    else:
        at, mixed, ct, maxwell = [exceptional_amplitude * value * exceptional_wave for value in POLAR_EXCEPTIONAL]
        perturbation[0, 0] += at * exceptional_harmonic
        perturbation[0, 1] += mixed * exceptional_harmonic
        perturbation[1, 0] += mixed * exceptional_harmonic
        perturbation[1, 1] += ct * exceptional_harmonic
        potential = maxwell
        field[2, 3] += epsilon * potential * sp.diff(exceptional_polar, z)
        field[3, 2] = -field[2, 3]
        field[0, 3] += epsilon * sp.diff(potential, time) * exceptional_polar
        field[3, 0] = -field[0, 3]

    if extra_parity == "axial":
        ht, hx, qt, qx = [extra_amplitude * value * extra_wave for value in AXIAL_EXTRA[extra_case]]
        perturbation[0, 3] += ht * extra_axial
        perturbation[3, 0] += ht * extra_axial
        perturbation[1, 3] += hx * extra_axial
        perturbation[3, 1] += hx * extra_axial
        field[0, 1] += epsilon * sp.diff(qx, time) * extra_harmonic
        field[1, 0] = -field[0, 1]
        field[0, 2] += -epsilon * qt * sp.diff(extra_harmonic, z)
        field[2, 0] = -field[0, 2]
        field[1, 2] += -epsilon * qx * sp.diff(extra_harmonic, z)
        field[2, 1] = -field[1, 2]
    else:
        at, mixed, ct, maxwell = [extra_amplitude * value * extra_wave for value in POLAR_EXTRA[extra_case]]
        perturbation[0, 0] += at * extra_harmonic
        perturbation[0, 1] += mixed * extra_harmonic
        perturbation[1, 0] += mixed * extra_harmonic
        perturbation[1, 1] += ct * extra_harmonic
        potential = maxwell
        field[2, 3] += epsilon * potential * sp.diff(extra_polar, z)
        field[3, 2] = -field[2, 3]
        field[0, 3] += epsilon * sp.diff(potential, time) * extra_polar
        field[3, 0] = -field[0, 3]

    background_metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    metric = background_metric + epsilon * perturbation
    background_inverse = sp.diag(-1, 1, sphere_factor, 1 / sphere_factor)
    inverse = (
        background_inverse
        - epsilon * background_inverse * perturbation * background_inverse
        + epsilon**2 * background_inverse * perturbation * background_inverse * perturbation * background_inverse
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
    output_parity = "polar" if exceptional_parity == extra_parity else "axial"
    metric_components = ((0, 0), (0, 1), (1, 1)) if output_parity == "polar" else ((0, 3), (1, 3))
    metric_equations, maxwell_equations = _equations(data, 2, metric_components)

    def coefficient(expression: sp.Expr) -> sp.Expr:
        value = (
            sp.diff(
                sp.diff(sp.diff(expression, epsilon, 2) / 2, exceptional_amplitude),
                extra_amplitude,
            )
            .subs(epsilon, 0)
            / output_wave
        )
        return sp.factor(sp.cancel(_canonical(value)))

    if output_parity == "polar":
        maxwell_value = coefficient(maxwell_equations[3])
        vector_norm = sp.integrate(sphere_factor, (z, -1, 1))
        maxwell_projection = _canonical(
            sp.integrate(maxwell_value * sphere_factor, (z, -1, 1)) / vector_norm
        )
        rows = [
            -_project_scalar(coefficient(metric_equations[(0, 0)]), exceptional_harmonic, z),
            2 * _project_scalar(coefficient(metric_equations[(0, 1)]), exceptional_harmonic, z),
            -_project_scalar(coefficient(metric_equations[(1, 1)]), exceptional_harmonic, z),
            4 * maxwell_projection,
        ]
    else:
        axial_norm = sp.integrate(exceptional_axial**2 / sphere_factor, (z, -1, 1))

        def axial_projection(expression: sp.Expr) -> sp.Expr:
            return _canonical(
                sp.integrate(coefficient(expression) * exceptional_axial / sphere_factor, (z, -1, 1))
                / axial_norm
            )

        rows = [
            2 * axial_projection(metric_equations[(0, 3)]),
            -2 * axial_projection(metric_equations[(1, 3)]),
            _project_scalar(coefficient(maxwell_equations[0]), exceptional_harmonic, z),
            _project_scalar(coefficient(maxwell_equations[1]), exceptional_harmonic, z),
        ]
    return sp.Matrix(rows).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exceptional-parity", choices=("axial", "polar"), required=True)
    parser.add_argument("--extra-parity", choices=("axial", "polar"), required=True)
    parser.add_argument("--extra-case", choices=("e1", "e2"), required=True)
    arguments = parser.parse_args()
    print([str(value) for value in source(arguments.exceptional_parity, arguments.extra_parity, arguments.extra_case)])


if __name__ == "__main__":
    main()

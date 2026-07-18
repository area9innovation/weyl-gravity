#!/usr/bin/env python3
"""Direct aligned twist times ell=2 extra quadratic action sources."""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)
from bridge.einstein_sector.einstein_maxwell_weyl_twist_ell2_extra_source_explore import (
    AXIAL_MODES,
    POLAR_MODES,
)


def aligned_source(
    extra_parity: str,
    extra_mode: str,
    twist_case: str,
    output_ell: int,
) -> tuple[sp.Matrix, sp.Matrix]:
    if output_ell not in (1, 3):
        raise ValueError("the aligned V1 tensor V2 product has only L=1,3")
    epsilon = sp.symbols("epsilon")
    twist_amplitude, wave_amplitude = sp.symbols("u v")
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    output_harmonic = sp.legendre(output_ell, z)
    output_axial_phi = sphere_factor * sp.diff(output_harmonic, z)
    twist_harmonic = z
    twist_axial_phi = sphere_factor
    extra_harmonic = sp.legendre(2, z)
    extra_axial_phi = sphere_factor * sp.diff(extra_harmonic, z)
    frequency = 4 / sp.sqrt(3)
    wave = sp.exp(-sp.I * frequency * time)
    twist_profile = {"position": sp.Integer(1), "velocity": time}[twist_case]
    tr = lambda expression: _trunc(expression, epsilon, 2)

    background_metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    perturbation = sp.zeros(4)
    perturbation[1, 3] = perturbation[3, 1] = (
        twist_amplitude * twist_profile * twist_axial_phi
    )
    if extra_parity == "axial":
        h_time, h_space, _, _ = AXIAL_MODES[extra_mode]
        perturbation[0, 3] += wave_amplitude * h_time * wave * extra_axial_phi
        perturbation[3, 0] = perturbation[0, 3]
        perturbation[1, 3] += wave_amplitude * h_space * wave * extra_axial_phi
        perturbation[3, 1] = perturbation[1, 3]
    else:
        a_time, mixed, a_space, _ = POLAR_MODES[extra_mode]
        perturbation[0, 0] += wave_amplitude * a_time * wave * extra_harmonic
        perturbation[0, 1] = perturbation[1, 0] = wave_amplitude * mixed * wave * extra_harmonic
        perturbation[1, 1] += wave_amplitude * a_space * wave * extra_harmonic

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
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for first in range(4):
            for second in range(4):
                connection[target][first][second] = tr(
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
    twist_potential_x = -twist_amplitude * twist_profile * twist_harmonic
    field[0, 1] += epsilon * sp.diff(twist_potential_x, time)
    field[1, 0] = -field[0, 1]
    field[1, 2] += -epsilon * sp.diff(twist_potential_x, z)
    field[2, 1] = -field[1, 2]

    if extra_parity == "axial":
        _, _, q_time, q_space = AXIAL_MODES[extra_mode]
        potential_time = wave_amplitude * q_time * wave * extra_harmonic
        potential_space = wave_amplitude * q_space * wave * extra_harmonic
        field[0, 1] += epsilon * sp.diff(potential_space, time)
        field[1, 0] = -field[0, 1]
        field[0, 2] += -epsilon * sp.diff(potential_time, z)
        field[2, 0] = -field[0, 2]
        field[1, 2] += -epsilon * sp.diff(potential_space, z)
        field[2, 1] = -field[1, 2]
    else:
        _, _, _, maxwell = POLAR_MODES[extra_mode]
        potential_phi = wave_amplitude * maxwell * wave * extra_axial_phi
        field[0, 3] += epsilon * sp.diff(potential_phi, time)
        field[3, 0] = -field[0, 3]
        field[2, 3] += epsilon * sp.diff(potential_phi, z)
        field[3, 2] = -field[2, 3]

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
    metric_pairs = ((0, 0), (0, 1), (1, 1), (0, 2), (0, 3), (1, 2), (1, 3))
    metric_equations, maxwell_equations = _equations(data, 2, metric_pairs)

    def maxwell_equation(right: int) -> sp.Expr:
        field_up = sp.zeros(4)
        for left in range(4):
            for raised_right in range(4):
                field_up[left, raised_right] = tr(
                    sum(
                        inverse[left, first] * inverse[raised_right, second] * field[first, second]
                        for first in range(4)
                        for second in range(4)
                    )
                )
        volume = tr(sp.sqrt(-metric.det()))
        return tr(
            sum(sp.diff(volume * field_up[left, right], coordinates[left]) for left in range(4))
            / volume
        )

    maxwell_equations[2] = maxwell_equation(2)

    def mixed(row: sp.Expr) -> sp.Expr:
        value = sp.diff(
            sp.diff(sp.diff(row, epsilon, 2) / 2, twist_amplitude),
            wave_amplitude,
        ).subs(epsilon, 0)
        return _canonical(sp.cancel(value / wave))

    scalar_norm = sp.Rational(2, 2 * output_ell + 1)
    axial_norm = sp.Rational(
        2 * output_ell * (output_ell + 1),
        2 * output_ell + 1,
    )
    if _canonical(sp.integrate(output_harmonic**2, (z, -1, 1)) - scalar_norm) != 0:
        raise AssertionError("aligned scalar harmonic norm changed")
    if _canonical(
        sp.integrate(output_axial_phi**2 / sphere_factor, (z, -1, 1)) - axial_norm
    ) != 0:
        raise AssertionError("aligned axial harmonic norm changed")

    def scalar_projection(row: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.integrate(mixed(row) * output_harmonic, (z, -1, 1)) / scalar_norm
        )

    def axial_projection(row_phi: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.integrate(mixed(row_phi) * output_axial_phi / sphere_factor, (z, -1, 1))
            / axial_norm
        )

    def contravariant_axial_projection(row_phi: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.integrate(mixed(row_phi) * output_axial_phi, (z, -1, 1)) / axial_norm
        )

    eigenvalue = sp.Integer(output_ell * (output_ell + 1))
    axial = sp.Matrix(
        [
            eigenvalue * axial_projection(metric_equations[(0, 3)]),
            -eigenvalue * axial_projection(metric_equations[(1, 3)]),
            scalar_projection(maxwell_equations[0]),
            scalar_projection(maxwell_equations[1]),
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))
    polar = sp.Matrix(
        [
            -scalar_projection(metric_equations[(0, 0)]),
            2 * scalar_projection(metric_equations[(0, 1)]),
            -scalar_projection(metric_equations[(1, 1)]),
            2 * eigenvalue * contravariant_axial_projection(maxwell_equations[3]),
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))
    return axial, polar


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extra-parity", choices=("axial", "polar"), required=True)
    parser.add_argument("--extra-mode", choices=("e1", "e2"), required=True)
    parser.add_argument("--twist-case", choices=("position", "velocity"), required=True)
    parser.add_argument("--output-ell", choices=(1, 3), required=True, type=int)
    arguments = parser.parse_args()
    axial, polar = aligned_source(
        arguments.extra_parity,
        arguments.extra_mode,
        arguments.twist_case,
        arguments.output_ell,
    )
    print("axial", [str(value) for value in axial])
    print("polar", [str(value) for value in polar])


if __name__ == "__main__":
    main()

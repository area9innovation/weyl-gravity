"""Exact fixed-ell probe of the tuned q-minus self-source.

This is an exploratory slow rail.  It generalizes the independently frozen
ell=2 four-dimensional replay without changing that producer.  No theorem or
certificate imports this module.
"""

from __future__ import annotations

import argparse
import time

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator as _polar_action_operator,
)


def _project_scalar(expression: sp.Expr, harmonic: sp.Expr, z: sp.Symbol) -> sp.Expr:
    norm = sp.integrate(harmonic**2, (z, -1, 1))
    return _canonical(sp.integrate(expression * harmonic, (z, -1, 1)) / norm)


def source_and_pairing(ell: int) -> tuple[sp.Matrix, sp.Matrix, sp.Expr]:
    if ell < 2:
        raise ValueError("the generic theorem starts at ell=2")

    epsilon = sp.symbols("epsilon")
    first_amplitude, second_amplitude = sp.symbols("u v")
    time_coordinate, space_coordinate, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time_coordinate, space_coordinate, z, azimuth)
    sphere_factor = 1 - z**2

    eigenvalue = sp.Integer(ell * (ell + 1))
    output_ell = 2 * ell
    output_eigenvalue = sp.Integer(output_ell * (output_ell + 1))
    root_two_lambda = sp.sqrt(2 * eigenvalue)
    momentum_squared = root_two_lambda - sp.Rational(ell, 2) - sp.Rational(1, 6)
    frequency_squared = eigenvalue - sp.Rational(ell, 2) - sp.Rational(1, 6)
    momentum = sp.sqrt(momentum_squared)
    frequency = sp.sqrt(frequency_squared)
    output_frequency = 2 * frequency

    input_harmonic = sp.legendre(ell, z)
    input_axial = sphere_factor * sp.diff(input_harmonic, z)
    output_harmonic = sp.legendre(output_ell, z)
    output_axial = sphere_factor * sp.diff(output_harmonic, z)

    def mode(amplitude: sp.Symbol, signed_momentum: sp.Expr) -> tuple[sp.Expr, ...]:
        wave = sp.exp(sp.I * (signed_momentum * space_coordinate - frequency * time_coordinate))
        return (
            amplitude * 2 * signed_momentum * wave,
            amplitude * (-2 * frequency) * wave,
            amplitude * (-root_two_lambda * signed_momentum) * wave,
            amplitude * (root_two_lambda * frequency) * wave,
        )

    first = mode(first_amplitude, momentum)
    second = mode(second_amplitude, -momentum)
    ht, hx, qt, qx = (first[index] + second[index] for index in range(4))

    perturbation = sp.zeros(4)
    perturbation[0, 3] = perturbation[3, 0] = ht * input_axial
    perturbation[1, 3] = perturbation[3, 1] = hx * input_axial
    background_metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
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
    field[0, 1] = epsilon * (sp.diff(qx, time_coordinate) - sp.diff(qt, space_coordinate)) * input_harmonic
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * qt * sp.diff(input_harmonic, z)
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * qx * sp.diff(input_harmonic, z)
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
    metric_equations, maxwell_equations = _equations(data, 2, ((0, 0), (0, 1), (1, 1)))
    output_wave = sp.exp(-sp.I * output_frequency * time_coordinate)

    def coefficient(expression: sp.Expr) -> sp.Expr:
        value = (
            sp.diff(sp.diff(sp.diff(expression, epsilon, 2) / 2, first_amplitude), second_amplitude)
            .subs(epsilon, 0)
            / output_wave
        )
        return sp.factor(sp.cancel(_canonical(value)))

    axial_norm = sp.integrate(output_axial**2 / sphere_factor, (z, -1, 1))
    maxwell_projection = _canonical(
        sp.integrate(coefficient(maxwell_equations[3]) * output_axial, (z, -1, 1)) / axial_norm
    )
    source = sp.Matrix(
        [
            -_project_scalar(coefficient(metric_equations[(0, 0)]), output_harmonic, z),
            2 * _project_scalar(coefficient(metric_equations[(0, 1)]), output_harmonic, z),
            -_project_scalar(coefficient(metric_equations[(1, 1)]), output_harmonic, z),
            2 * output_eigenvalue * maxwell_projection,
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))

    action, (target_lambda, target_momentum, target_frequency) = _polar_action_operator()
    block = action.subs(
        {
            target_lambda: output_eigenvalue,
            target_momentum: 0,
            target_frequency: output_frequency,
        }
    ).applyfunc(sp.factor)
    left_kernel = block.T.nullspace()
    if len(left_kernel) != 2:
        raise RuntimeError(f"polar p-shell cokernel changed at ell={ell}: {left_kernel}")
    dynamical = left_kernel[1]
    pairing = sp.factor(sp.cancel((dynamical.T * source)[0]))
    return source, dynamical, pairing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ell", type=int)
    arguments = parser.parse_args()
    started = time.monotonic()
    source, adjoint, pairing = source_and_pairing(arguments.ell)
    print(f"ell={arguments.ell}")
    print("source", [str(value) for value in source])
    print("adjoint", [str(value) for value in adjoint])
    print("pairing", pairing)
    print(f"elapsed_seconds={time.monotonic() - started:.2f}")


if __name__ == "__main__":
    main()

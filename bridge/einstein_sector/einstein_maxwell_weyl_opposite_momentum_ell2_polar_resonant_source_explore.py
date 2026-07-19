"""Direct polar-input analogue of the tuned ell=2 opposite-momentum fixture."""

from __future__ import annotations

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


def source_and_pairings() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    epsilon = sp.symbols("epsilon")
    first_amplitude, second_amplitude = sp.symbols("u v")
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    input_harmonic = sp.legendre(2, z)
    input_axial = sphere_factor * sp.diff(input_harmonic, z)
    output_harmonic = sp.legendre(4, z)
    output_axial = sphere_factor * sp.diff(output_harmonic, z)
    output_lambda = sp.Integer(20)

    k_squared = 2 * sp.sqrt(3) - sp.Rational(7, 6)
    momentum = sp.sqrt(k_squared)
    frequency = sp.sqrt(sp.Rational(29, 6))
    output_frequency = 2 * frequency
    a_time = -12 + sp.Rational(14, 3) * sp.sqrt(3)
    a_space = -12 - sp.Rational(58, 3) * sp.sqrt(3)

    def mode(amplitude: sp.Symbol, signed_momentum: sp.Expr) -> tuple[sp.Expr, ...]:
        wave = sp.exp(sp.I * (signed_momentum * space - frequency * time))
        return (
            amplitude * a_time * wave,
            amplitude * 4 * sp.sqrt(3) * signed_momentum * frequency * wave,
            amplitude * a_space * wave,
            amplitude * 6 * wave,
        )

    first = mode(first_amplitude, momentum)
    second = mode(second_amplitude, -momentum)
    profiles = [first[index] + second[index] for index in range(4)]
    at, mixed, ct, maxwell = profiles
    truncate = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    metric[0, 0] += epsilon * at * input_harmonic
    metric[0, 1] = metric[1, 0] = epsilon * mixed * input_harmonic
    metric[1, 1] += epsilon * ct * input_harmonic
    inverse = metric.inv().applyfunc(truncate)
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
    field[2, 3] = -1 + epsilon * maxwell * sp.diff(input_axial, z)
    field[3, 2] = -field[2, 3]
    field[0, 3] = epsilon * sp.diff(maxwell, time) * input_axial
    field[3, 0] = -field[0, 3]
    field[1, 3] = epsilon * sp.diff(maxwell, space) * input_axial
    field[3, 1] = -field[1, 3]

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
    output_wave = sp.exp(-sp.I * output_frequency * time)

    def coefficient(expression: sp.Expr) -> sp.Expr:
        value = (
            sp.diff(
                sp.diff(sp.diff(expression, epsilon, 2) / 2, first_amplitude),
                second_amplitude,
            )
            .subs(epsilon, 0)
            / output_wave
        )
        return sp.factor(sp.cancel(_canonical(value)))

    axial_norm = sp.integrate(output_axial**2 / sphere_factor, (z, -1, 1))
    maxwell_projection = _canonical(
        sp.integrate(coefficient(maxwell_equations[3]) * output_axial, (z, -1, 1))
        / axial_norm
    )
    source = sp.Matrix(
        [
            -_project_scalar(coefficient(metric_equations[(0, 0)]), output_harmonic, z),
            2 * _project_scalar(coefficient(metric_equations[(0, 1)]), output_harmonic, z),
            -_project_scalar(coefficient(metric_equations[(1, 1)]), output_harmonic, z),
            2 * output_lambda * maxwell_projection,
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))

    action, (target_lambda, target_momentum, target_frequency) = _polar_action_operator()
    block = action.subs(
        {
            target_lambda: output_lambda,
            target_momentum: 0,
            target_frequency: output_frequency,
        }
    ).applyfunc(sp.factor)
    left_kernel = block.T.nullspace()
    pairings = sp.Matrix(
        [sp.factor(sp.cancel((adjoint.T * source)[0])) for adjoint in left_kernel]
    )
    return source, sp.Matrix.hstack(*left_kernel), pairings


def main() -> None:
    source, adjoints, pairings = source_and_pairings()
    print("source", [str(value) for value in source])
    print("left_adjoint_columns", [[str(value) for value in adjoints[:, column]] for column in range(adjoints.cols)])
    print("pairings", [str(value) for value in pairings])


if __name__ == "__main__":
    main()

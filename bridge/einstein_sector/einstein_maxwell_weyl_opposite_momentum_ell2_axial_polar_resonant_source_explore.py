"""Direct axial-polar cross source on the tuned L=4 axial p shell."""

from __future__ import annotations

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows
from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


def _project_scalar(expression: sp.Expr, harmonic: sp.Expr, z: sp.Symbol) -> sp.Expr:
    norm = sp.integrate(harmonic**2, (z, -1, 1))
    return _canonical(sp.integrate(expression * harmonic, (z, -1, 1)) / norm)


def source_and_pairings() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    epsilon = sp.symbols("epsilon")
    axial_amplitude, polar_amplitude = sp.symbols("u v")
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
    axial_wave = sp.exp(sp.I * (momentum * space - frequency * time))
    polar_wave = sp.exp(sp.I * (-momentum * space - frequency * time))

    axial_ht = axial_amplitude * 2 * momentum * axial_wave
    axial_hx = axial_amplitude * (-2 * frequency) * axial_wave
    axial_qt = axial_amplitude * (-2 * sp.sqrt(3) * momentum) * axial_wave
    axial_qx = axial_amplitude * (2 * sp.sqrt(3) * frequency) * axial_wave
    polar_at = polar_amplitude * (-12 + sp.Rational(14, 3) * sp.sqrt(3)) * polar_wave
    polar_mixed = polar_amplitude * (-4 * sp.sqrt(3) * momentum * frequency) * polar_wave
    polar_ct = polar_amplitude * (-12 - sp.Rational(58, 3) * sp.sqrt(3)) * polar_wave
    polar_u = polar_amplitude * 6 * polar_wave
    truncate = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    metric[0, 0] += epsilon * polar_at * input_harmonic
    metric[0, 1] = metric[1, 0] = epsilon * polar_mixed * input_harmonic
    metric[1, 1] += epsilon * polar_ct * input_harmonic
    metric[0, 3] = metric[3, 0] = epsilon * axial_ht * input_axial
    metric[1, 3] = metric[3, 1] = epsilon * axial_hx * input_axial
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
    field[2, 3] = -1 + epsilon * polar_u * sp.diff(input_axial, z)
    field[3, 2] = -field[2, 3]
    field[0, 3] = epsilon * sp.diff(polar_u, time) * input_axial
    field[3, 0] = -field[0, 3]
    field[1, 3] = epsilon * sp.diff(polar_u, space) * input_axial
    field[3, 1] = -field[1, 3]
    field[0, 1] = epsilon * (
        sp.diff(axial_qx, time) - sp.diff(axial_qt, space)
    ) * input_harmonic
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * axial_qt * sp.diff(input_harmonic, z)
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * axial_qx * sp.diff(input_harmonic, z)
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
    output_wave = sp.exp(-sp.I * output_frequency * time)

    def coefficient(expression: sp.Expr) -> sp.Expr:
        value = (
            sp.diff(
                sp.diff(sp.diff(expression, epsilon, 2) / 2, axial_amplitude),
                polar_amplitude,
            )
            .subs(epsilon, 0)
            / output_wave
        )
        return sp.factor(sp.cancel(_canonical(value)))

    axial_norm = sp.integrate(output_axial**2 / sphere_factor, (z, -1, 1))

    def axial_projection(expression: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.integrate(coefficient(expression) * output_axial / sphere_factor, (z, -1, 1))
            / axial_norm
        )

    source = sp.Matrix(
        [
            output_lambda * axial_projection(metric_equations[(0, 3)]),
            -output_lambda * axial_projection(metric_equations[(1, 3)]),
            _project_scalar(coefficient(maxwell_equations[0]), output_harmonic, z),
            _project_scalar(coefficient(maxwell_equations[1]), output_harmonic, z),
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))

    rows, symbols = _generic_rows()
    target_lambda = symbols["lambda"]
    target_momentum = symbols["k"]
    target_frequency = symbols["omega"]
    coefficients = [symbols[name] for name in ("h_t", "h_x", "q_t", "q_x")]
    block = (
        sp.diag(target_lambda, -target_lambda, 1, 1)
        * sp.Matrix([rows[name] for name in ("metric_t", "metric_x", "maxwell_t", "maxwell_x")])
    ).jacobian(coefficients)
    block = block.subs(
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

"""Direct twist-position sources for the ell=2 Einstein q-primary shells."""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


ROOT3 = sp.sqrt(3)
BRANCHES = {
    "minus": {
        "frequency_squared": 6 - 2 * ROOT3,
        "axial": (0, -2, 0, 2 * ROOT3),
        "polar": (12, 0, 12 - 24 * ROOT3, 6),
    },
    "plus": {
        "frequency_squared": 6 + 2 * ROOT3,
        "axial": (0, -2, 0, -2 * ROOT3),
        "polar": (12, 0, 12 + 24 * ROOT3, 6),
    },
}


def _mixed_source(input_parity: str, branch: str) -> tuple[sp.Matrix, sp.Matrix]:
    epsilon = sp.symbols("epsilon")
    twist_amplitude, wave_amplitude = sp.symbols("u v")
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    sphere_root = sp.sqrt(sphere_factor)
    azimuthal_phase = sp.exp(sp.I * azimuth)
    output_harmonic = z * sphere_root
    # X_A=*dY_(2,1) for the same scalar harmonic used by the polar output.
    # The previous (-i/sqrt(1-z^2),-z*sqrt(1-z^2)) projector was *dY_(1,1)
    # and therefore could not be paired with a lambda=6 adjoint operator.
    output_axial_z = -sp.I * z / sphere_root
    output_axial_phi = (1 - 2 * z**2) * sphere_root
    twist_harmonic = sphere_root * azimuthal_phase
    twist_axial_z = -sp.I * azimuthal_phase / sphere_root
    twist_axial_phi = -z * sphere_root * azimuthal_phase
    wave_harmonic = sp.legendre(2, z)
    wave_axial_phi = sphere_factor * sp.diff(wave_harmonic, z)
    mode = BRANCHES[branch]
    # Keep the common shell frequency symbolic during the tensor calculation.
    # Substituting nested radicals before curvature simplification is both slower
    # and obscures the polynomial frequency dependence used by the certificate.
    frequency = sp.symbols("omega", positive=True, real=True)
    wave = sp.exp(-sp.I * frequency * time)
    tr = lambda expression: _trunc(expression, epsilon, 2)

    background_metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    perturbation = sp.zeros(4)
    perturbation[1, 2] = perturbation[2, 1] = twist_amplitude * twist_axial_z
    perturbation[1, 3] = perturbation[3, 1] = twist_amplitude * twist_axial_phi

    if input_parity == "axial":
        h_time, h_space, _, _ = mode["axial"]
        perturbation[0, 3] += wave_amplitude * h_time * wave * wave_axial_phi
        perturbation[3, 0] = perturbation[0, 3]
        perturbation[1, 3] += wave_amplitude * h_space * wave * wave_axial_phi
        perturbation[3, 1] = perturbation[1, 3]
    else:
        a_time, mixed, a_space, _ = mode["polar"]
        perturbation[0, 0] += wave_amplitude * a_time * wave * wave_harmonic
        perturbation[0, 1] = perturbation[1, 0] = wave_amplitude * mixed * wave * wave_harmonic
        perturbation[1, 1] += wave_amplitude * a_space * wave * wave_harmonic

    metric = background_metric + epsilon * perturbation
    background_inverse = sp.diag(-1, 1, sphere_factor, 1 / sphere_factor)
    inverse = (
        background_inverse
        - epsilon * background_inverse * perturbation * background_inverse
        + epsilon**2 * background_inverse * perturbation * background_inverse * perturbation * background_inverse
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
    twist_potential_x = -twist_amplitude * twist_harmonic
    field[1, 2] += -epsilon * sp.diff(twist_potential_x, z)
    field[2, 1] = -field[1, 2]
    field[1, 3] += -epsilon * sp.diff(twist_potential_x, azimuth)
    field[3, 1] = -field[1, 3]

    if input_parity == "axial":
        _, _, q_time, q_space = mode["axial"]
        potential_time = wave_amplitude * q_time * wave * wave_harmonic
        potential_space = wave_amplitude * q_space * wave * wave_harmonic
        field[0, 1] += epsilon * sp.diff(potential_space, time)
        field[1, 0] = -field[0, 1]
        field[0, 2] += -epsilon * sp.diff(potential_time, z)
        field[2, 0] = -field[0, 2]
        field[1, 2] += -epsilon * sp.diff(potential_space, z)
        field[2, 1] = -field[1, 2]
    else:
        _, _, _, maxwell = mode["polar"]
        potential_phi = wave_amplitude * maxwell * wave * wave_axial_phi
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
        return tr(sum(sp.diff(volume * field_up[left, right], coordinates[left]) for left in range(4)) / volume)

    maxwell_equations[2] = maxwell_equation(2)

    def mixed(row: sp.Expr) -> sp.Expr:
        value = sp.diff(sp.diff(sp.diff(row, epsilon, 2) / 2, twist_amplitude), wave_amplitude).subs(epsilon, 0)
        return _canonical(sp.cancel(value / (wave * azimuthal_phase)))

    scalar_norm = sp.integrate(output_harmonic**2, (z, -1, 1))
    axial_norm = sp.integrate(
        sphere_factor * (sp.I * z / sphere_root) * output_axial_z + output_axial_phi**2 / sphere_factor,
        (z, -1, 1),
    )
    if _canonical(scalar_norm - sp.Rational(4, 15)) != 0 or _canonical(axial_norm - sp.Rational(8, 5)) != 0:
        raise AssertionError("non-axisymmetric output harmonic normalization changed")

    def scalar_projection(row: sp.Expr) -> sp.Expr:
        return _canonical(sp.integrate(mixed(row) * output_harmonic, (z, -1, 1)) / scalar_norm)

    def axial_projection(row_z: sp.Expr, row_phi: sp.Expr) -> sp.Expr:
        integrand = sphere_factor * mixed(row_z) * (sp.I * z / sphere_root) + mixed(row_phi) * output_axial_phi / sphere_factor
        return _canonical(sp.integrate(integrand, (z, -1, 1)) / axial_norm)

    def contravariant_axial_projection(row_z: sp.Expr, row_phi: sp.Expr) -> sp.Expr:
        integrand = mixed(row_z) * (sp.I * z / sphere_root) + mixed(row_phi) * output_axial_phi
        return _canonical(sp.integrate(sp.powsimp(sp.cancel(integrand), force=True), (z, -1, 1)) / axial_norm)

    axial = sp.Matrix(
        [
            6 * axial_projection(metric_equations[(0, 2)], metric_equations[(0, 3)]),
            -6 * axial_projection(metric_equations[(1, 2)], metric_equations[(1, 3)]),
            scalar_projection(maxwell_equations[0]),
            scalar_projection(maxwell_equations[1]),
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))
    polar = sp.Matrix(
        [
            -scalar_projection(metric_equations[(0, 0)]),
            2 * scalar_projection(metric_equations[(0, 1)]),
            -scalar_projection(metric_equations[(1, 1)]),
            12 * contravariant_axial_projection(maxwell_equations[2], maxwell_equations[3]),
        ]
    ).applyfunc(lambda value: sp.factor(sp.cancel(_canonical(value))))
    return axial, polar


def source(input_parity: str, branch: str) -> tuple[sp.Matrix, sp.Matrix]:
    return _mixed_source(input_parity, branch)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-parity", choices=("axial", "polar"), required=True)
    parser.add_argument("--branch", choices=("minus", "plus"), required=True)
    arguments = parser.parse_args()
    axial, polar = source(arguments.input_parity, arguments.branch)
    print("axial", [str(value) for value in axial])
    print("polar", [str(value) for value in polar])


if __name__ == "__main__":
    main()

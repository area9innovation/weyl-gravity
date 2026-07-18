#!/usr/bin/env python3
"""Direct 4D bilinear source for canonical ell=2 extra-primary pairs."""

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
FREQUENCY = 4 / ROOT3
MODES: dict[str, tuple[str, tuple[sp.Expr, ...]]] = {
    "a1": ("axial", (-6, 0, 6, 0)),
    "a2": ("axial", (0, -sp.Rational(2, 3), 0, 6)),
    "p1": ("polar", (-8, 0, -72, 48)),
    "p2": ("polar", (0, 64 / ROOT3, 0, 0)),
}


def _maxwell_equation(data: dict[str, object], right: int, order: int) -> sp.Expr:
    epsilon = data["epsilon"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    field = data["field"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(field, sp.MatrixBase)
    tr = lambda expression: _trunc(expression, epsilon, order)
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
    volume = tr(sp.sqrt(-metric.det())).subs(sp.Abs(sp.sin(coordinates[2])), sp.sin(coordinates[2]))
    return tr(
        sum(sp.diff(volume * field_up[left, right], coordinates[left]) for left in range(4))
        / volume
    )


def _geometry(left_name: str, right_name: str, right_frequency_sign: int) -> dict[str, object]:
    left_parity, left = MODES[left_name]
    right_parity, right = MODES[right_name]
    epsilon, u, v = sp.symbols("epsilon u v")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    waves = (sp.exp(-sp.I * FREQUENCY * time), sp.exp(-sp.I * right_frequency_sign * FREQUENCY * time))
    tr = lambda expression: _trunc(expression, epsilon, 2)

    background_metric = sp.diag(-1, 1, 1, sine**2)
    perturbation = sp.zeros(4)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine

    for amplitude, parity, mode, wave in ((u, left_parity, left, waves[0]), (v, right_parity, right, waves[1])):
        if parity == "axial":
            h_time, h_space, q_time, q_space = mode
            perturbation[0, 3] += amplitude * h_time * wave * axial_one_form
            perturbation[3, 0] = perturbation[0, 3]
            perturbation[1, 3] += amplitude * h_space * wave * axial_one_form
            perturbation[3, 1] = perturbation[1, 3]
            potential_time = amplitude * q_time * wave * harmonic
            potential_space = amplitude * q_space * wave * harmonic
            field[0, 1] += epsilon * sp.diff(potential_space, time)
            field[1, 0] = -field[0, 1]
            field[0, 2] += -epsilon * sp.diff(potential_time, theta)
            field[2, 0] = -field[0, 2]
            field[1, 2] += -epsilon * sp.diff(potential_space, theta)
            field[2, 1] = -field[1, 2]
        else:
            a_time, mixed, a_space, maxwell = mode
            perturbation[0, 0] += amplitude * a_time * wave * harmonic
            perturbation[0, 1] += amplitude * mixed * wave * harmonic
            perturbation[1, 0] = perturbation[0, 1]
            perturbation[1, 1] += amplitude * a_space * wave * harmonic
            potential_phi = amplitude * maxwell * wave * axial_one_form
            field[0, 3] += epsilon * sp.diff(potential_phi, time)
            field[3, 0] = -field[0, 3]
            field[2, 3] += epsilon * sp.diff(potential_phi, theta)
            field[3, 2] = -field[2, 3]

    metric = background_metric + epsilon * perturbation
    background_inverse = sp.diag(-1, 1, 1, sine**-2)
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
    return {
        "epsilon": epsilon,
        "amplitudes": (u, v),
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
        "input_parities": (left_parity, right_parity),
        "output_frequency": sp.factor((1 + right_frequency_sign) * FREQUENCY),
    }


def pair_source(left_name: str, right_name: str, channel: str) -> dict[str, object]:
    sign = {"sum": 1, "zero": -1}[channel]
    geometry = _geometry(left_name, right_name, sign)
    data = _curvature(geometry, 2)
    left_parity, right_parity = geometry["input_parities"]
    pairs = (
        ((0, 0), (0, 1), (1, 1), (2, 2), (3, 3))
        if left_parity == right_parity
        else ((0, 3), (1, 3))
    )
    metric_equations, maxwell_equations = _equations(data, 2, pairs)
    epsilon = geometry["epsilon"]
    u, v = geometry["amplitudes"]
    time, _, theta, _ = geometry["coordinates"]
    sine = sp.sin(theta)

    def mixed(value: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.diff(sp.diff(sp.diff(value, epsilon, 2) / 2, u), v)
            .subs({epsilon: 0, time: 0})
        )

    output_frequency = geometry["output_frequency"]
    if left_parity == right_parity:
        sphere_trace = (metric_equations[(2, 2)] + metric_equations[(3, 3)] / sine**2) / 2
        raw = {
            "metric_00": mixed(metric_equations[(0, 0)]),
            "metric_01": mixed(metric_equations[(0, 1)]),
            "metric_11": mixed(metric_equations[(1, 1)]),
            "sphere_trace": mixed(sphere_trace),
            "maxwell_1": mixed(maxwell_equations[1]),
            "maxwell_3_density": mixed(sine * maxwell_equations[3]),
        }

        scalar_angles = (sp.pi / 3, sp.pi / 4, sp.pi / 6)
        scalar_matrix = sp.Matrix(
            [
                [sp.legendre(ell, sp.cos(angle)) for ell in (0, 2, 4)]
                for angle in scalar_angles
            ]
        )

        def scalar_coefficients(value: sp.Expr) -> dict[int, sp.Expr]:
            samples = sp.Matrix([_canonical(value.subs(theta, angle)) for angle in scalar_angles])
            coefficients = scalar_matrix.inv() * samples
            result = {ell: _canonical(coefficients[index]) for index, ell in enumerate((0, 2, 4))}
            audit_angle = sp.pi / 5
            audit = _canonical(
                value.subs(theta, audit_angle)
                - sum(result[ell] * sp.legendre(ell, sp.cos(audit_angle)) for ell in (0, 2, 4))
            )
            if sp.simplify(audit) != 0:
                raise AssertionError(f"same-parity scalar source contains an unexpected harmonic: {audit}")
            return result

        scalar_rows = {
            name: scalar_coefficients(raw[name])
            for name in ("metric_00", "metric_01", "metric_11", "sphere_trace", "maxwell_1")
        }

        axial_angles = (sp.pi / 3, sp.pi / 4)
        axial_matrix = sp.Matrix(
            [
                [sp.diff(sp.legendre(ell, sp.Symbol("z")), sp.Symbol("z")).subs(sp.Symbol("z"), sp.cos(angle)) for ell in (2, 4)]
                for angle in axial_angles
            ]
        )
        axial_samples = sp.Matrix(
            [_canonical(raw["maxwell_3_density"].subs(theta, angle) / sp.sin(angle)) for angle in axial_angles]
        )
        axial_coefficients = axial_matrix.inv() * axial_samples
        maxwell_coefficients = {ell: _canonical(axial_coefficients[index]) for index, ell in enumerate((2, 4))}
        audit_angle = sp.pi / 5
        audit = _canonical(
            raw["maxwell_3_density"].subs(theta, audit_angle) / sp.sin(audit_angle)
            - sum(
                maxwell_coefficients[ell]
                * sp.diff(sp.legendre(ell, sp.Symbol("z")), sp.Symbol("z")).subs(sp.Symbol("z"), sp.cos(audit_angle))
                for ell in (2, 4)
            )
        )
        if sp.simplify(audit) != 0:
            raise AssertionError(f"same-parity Maxwell source contains an unexpected harmonic: {audit}")

        homogeneous = [
            scalar_rows["metric_00"][0],
            scalar_rows["metric_11"][0],
            scalar_rows["sphere_trace"][0],
            scalar_rows["maxwell_1"][0],
        ]
        outputs: dict[str, list[sp.Expr]] = {}
        for ell in (2, 4):
            outputs[str(ell)] = [
                -scalar_rows["metric_00"][ell],
                2 * scalar_rows["metric_01"][ell],
                -scalar_rows["metric_11"][ell],
                2 * ell * (ell + 1) * maxwell_coefficients[ell],
            ]
        return {
            "input_parities": [left_parity, right_parity],
            "output_parity": "polar",
            "output_frequency": output_frequency,
            "homogeneous_rows_E00_E11_E22_Maxwell1": [sp.factor(value) for value in homogeneous],
            "action_rows_by_ell": {ell: [sp.factor(value) for value in values] for ell, values in outputs.items()},
        }

    raw_axial = {
        "metric_t": mixed(metric_equations[(0, 3)]),
        "metric_x": mixed(metric_equations[(1, 3)]),
        "maxwell_t": mixed(maxwell_equations[0]),
        "maxwell_x": mixed(maxwell_equations[1]),
    }

    scalar_ells = (0, 1, 2, 3, 4)
    scalar_angles = (sp.pi / 2, sp.pi / 3, 2 * sp.pi / 3, sp.pi / 4, 3 * sp.pi / 4)
    scalar_matrix = sp.Matrix(
        [[sp.legendre(ell, sp.cos(angle)) for ell in scalar_ells] for angle in scalar_angles]
    )
    scalar_coefficients = {}
    for name in ("maxwell_t", "maxwell_x"):
        samples = sp.Matrix([_canonical(raw_axial[name].subs(theta, angle)) for angle in scalar_angles])
        coefficients = scalar_matrix.inv() * samples
        scalar_coefficients[name] = {ell: _canonical(coefficients[index]) for index, ell in enumerate(scalar_ells)}
        audit_angle = sp.pi / 5
        audit = _canonical(
            raw_axial[name].subs(theta, audit_angle)
            - sum(scalar_coefficients[name][ell] * sp.legendre(ell, sp.cos(audit_angle)) for ell in scalar_ells)
        )
        if sp.simplify(audit) != 0:
            raise AssertionError(f"mixed-parity scalar source contains an unexpected harmonic: {audit}")

    axial_ells = (1, 2, 3, 4)
    axial_angles = (sp.pi / 3, 2 * sp.pi / 3, sp.pi / 4, 3 * sp.pi / 4)
    z = sp.Symbol("z")
    axial_matrix = sp.Matrix(
        [[sp.diff(sp.legendre(ell, z), z).subs(z, sp.cos(angle)) for ell in axial_ells] for angle in axial_angles]
    )
    axial_coefficients = {}
    for name in ("metric_t", "metric_x"):
        samples = sp.Matrix([_canonical(raw_axial[name].subs(theta, angle) / sp.sin(angle) ** 2) for angle in axial_angles])
        coefficients = axial_matrix.inv() * samples
        axial_coefficients[name] = {ell: _canonical(coefficients[index]) for index, ell in enumerate(axial_ells)}
        audit_angle = sp.pi / 5
        audit = _canonical(
            raw_axial[name].subs(theta, audit_angle) / sp.sin(audit_angle) ** 2
            - sum(
                axial_coefficients[name][ell] * sp.diff(sp.legendre(ell, z), z).subs(z, sp.cos(audit_angle))
                for ell in axial_ells
            )
        )
        if sp.simplify(audit) != 0:
            raise AssertionError(f"mixed-parity axial source contains an unexpected harmonic: {audit}")

    scalar_l0 = [scalar_coefficients["maxwell_t"][0], scalar_coefficients["maxwell_x"][0]]
    outputs = {}
    for ell in axial_ells:
        values = [
            ell * (ell + 1) * axial_coefficients["metric_t"][ell],
            -ell * (ell + 1) * axial_coefficients["metric_x"][ell],
            scalar_coefficients["maxwell_t"][ell],
            scalar_coefficients["maxwell_x"][ell],
        ]
        if any(_canonical(value) != 0 for value in values):
            outputs[str(ell)] = [sp.factor(value) for value in values]
    return {
        "input_parities": [left_parity, right_parity],
        "output_parity": "axial",
        "output_frequency": output_frequency,
        "maxwell_scalar_L0_rows_M0_M1": [sp.factor(value) for value in scalar_l0],
        "action_rows_by_ell": outputs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", choices=MODES, required=True)
    parser.add_argument("--right", choices=MODES, required=True)
    parser.add_argument("--channel", choices=("sum", "zero"), required=True)
    arguments = parser.parse_args()
    result = pair_source(arguments.left, arguments.right, arguments.channel)
    print(result)


if __name__ == "__main__":
    main()

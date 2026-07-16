"""Exhaustive exact second-variation check for the radiative symplectic forms.

This is the deliberately slower Tier-2 rail.  It expands the full
Einstein--Maxwell density to quadratic order for an arbitrary axisymmetric
spherical eigenfunction.  The fast certificate generator imports only the
resulting exact local Hessians and checks their harmonic consequences.
"""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _trunc,
)


class SymplecticActionCheckError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SymplecticActionCheckError(message)


def _geometry(metric: sp.Matrix, field: sp.Matrix, epsilon: sp.Symbol, coordinates: tuple[sp.Symbol, ...]) -> tuple[sp.Expr, sp.Expr]:
    inverse = metric.inv().applyfunc(lambda value: _trunc(value, epsilon, 2))
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = _trunc(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2,
                    epsilon,
                    2,
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
    field_squared = _trunc(
        sum(
            inverse[a, c] * inverse[b, d] * field[a, b] * field[c, d]
            for a in range(4)
            for b in range(4)
            for c in range(4)
            for d in range(4)
        ),
        epsilon,
        2,
    )
    sine = sp.sin(coordinates[2])
    volume = _trunc(sp.sqrt(-metric.det()), epsilon, 2).subs(sp.Abs(sine), sine)
    density = _trunc(
        volume * ((data["scalar"] - 1) / 2 - field_squared / 4),
        epsilon,
        2,
    )
    return sp.diff(density, epsilon, 2).subs(epsilon, 0) / 2, sine


def _effective_hessian(
    quadratic_density: sp.Expr,
    fields: tuple[sp.Expr, sp.Expr],
    time: sp.Symbol,
) -> sp.Matrix:
    velocities = tuple(sp.diff(field, time) for field in fields)
    accelerations = tuple(sp.diff(field, time, 2) for field in fields)
    raw = sp.hessian(quadratic_density, velocities)
    mixed = sp.Matrix(
        2,
        2,
        lambda i, j: sp.diff(quadratic_density, fields[i], accelerations[j]),
    )
    # Integrating q_i ddot(q_j) by parts changes the velocity Hessian by
    # -(mixed+mixed.T).  The discarded term is a spacetime divergence.
    return (raw - mixed - mixed.T).applyfunc(
        lambda value: sp.factor(sp.trigsimp(value))
    )


def exact_local_hessians() -> dict[str, sp.Matrix]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.Function("Y")(theta)
    first = sp.diff(harmonic, theta)
    axial_one_form = -sine * first

    axial_metric_coefficient = sp.Function("h_x")(time)
    axial_maxwell_coefficient = sp.Function("q_x")(time)
    axial_metric = sp.diag(-1, 1, 1, sine**2)
    axial_metric[1, 3] = axial_metric[3, 1] = (
        epsilon * axial_metric_coefficient * axial_one_form
    )
    axial_field = sp.zeros(4)
    axial_field[2, 3] = sine
    axial_field[3, 2] = -sine
    axial_field[0, 1] = epsilon * sp.diff(axial_maxwell_coefficient, time) * harmonic
    axial_field[1, 0] = -axial_field[0, 1]
    axial_field[1, 2] = -epsilon * axial_maxwell_coefficient * first
    axial_field[2, 1] = -axial_field[1, 2]
    axial_quadratic, _ = _geometry(
        axial_metric, axial_field, epsilon, coordinates
    )
    axial = _effective_hessian(
        axial_quadratic,
        (axial_metric_coefficient, axial_maxwell_coefficient),
        time,
    )

    polar_metric_master = sp.Function("K")(time)
    polar_maxwell_master = sp.Function("U")(time)
    reconstruction = polar_metric_master - 2 * polar_maxwell_master
    polar_metric = sp.diag(-1, 1, 1, sine**2)
    polar_metric[0, 0] += -epsilon * reconstruction * harmonic
    polar_metric[1, 1] += -epsilon * reconstruction * harmonic
    polar_metric[2, 2] += epsilon * polar_metric_master * harmonic
    polar_metric[3, 3] += epsilon * polar_metric_master * harmonic * sine**2
    polar_field = sp.zeros(4)
    polar_field[2, 3] = sine + epsilon * polar_maxwell_master * sp.diff(
        axial_one_form, theta
    )
    polar_field[3, 2] = -polar_field[2, 3]
    polar_field[0, 3] = (
        epsilon * sp.diff(polar_maxwell_master, time) * axial_one_form
    )
    polar_field[3, 0] = -polar_field[0, 3]
    polar_quadratic, _ = _geometry(
        polar_metric, polar_field, epsilon, coordinates
    )
    polar = _effective_hessian(
        polar_quadratic,
        (polar_metric_master, polar_maxwell_master),
        time,
    )
    return {"axial": axial, "polar": polar}


def verify() -> None:
    theta = sp.symbols("theta", real=True)
    sine = sp.sin(theta)
    harmonic = sp.Function("Y")(theta)
    first = sp.diff(harmonic, theta)
    expected = {
        "axial": sp.Matrix(
            [[sine * first**2 / 2, 0], [0, sine * harmonic**2]]
        ),
        "polar": sp.Matrix(
            [
                [sine * harmonic**2 / 2, -sine * harmonic**2],
                [-sine * harmonic**2, sine * first**2],
            ]
        ),
    }
    actual = exact_local_hessians()
    for parity in ("axial", "polar"):
        difference = (actual[parity] - expected[parity]).applyfunc(sp.simplify)
        _require(difference == sp.zeros(2), f"{parity} local Hessian changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if not args.verify:
        parser.error("--verify is required")
    verify()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Direct global-orbit quadratic source for aligned twist and electric data."""

from __future__ import annotations

import argparse

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _trunc,
)
from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _equations,
)


def direct_source() -> dict[str, dict[str, sp.Expr]]:
    epsilon = sp.symbols("epsilon")
    position, velocity, charge = sp.symbols("A B Q_e", real=True)
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    cosine = sp.cos(theta)
    amplitude = position + velocity * time
    tr = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[1, 3] = metric[3, 1] = epsilon * amplitude * sine**2
    inverse = metric.inv().applyfunc(tr)
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

    potential_x = charge * time - amplitude * cosine
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(potential_x, time)
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * sp.diff(potential_x, theta)
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
    pairs = tuple((first, second) for first in range(4) for second in range(first, 4))
    metric_equations, maxwell_equations = _equations(data, 2, pairs)
    raw = {
        f"E{first}{second}": _canonical(sp.diff(value, epsilon, 2).subs(epsilon, 0) / 2)
        for (first, second), value in metric_equations.items()
    }
    raw.update(
        {
            f"M{index}": _canonical(sp.diff(value, epsilon, 2).subs(epsilon, 0) / 2)
            for index, value in maxwell_equations.items()
        }
    )

    harmonic2 = sp.legendre(2, cosine)
    derivative2 = sp.diff(harmonic2, theta)
    tensor2 = (sp.diff(harmonic2, theta, 2) - sp.cot(theta) * derivative2) / 2
    sphere_trace = _canonical((raw["E22"] + raw["E33"] / sine**2) / 2)
    sphere_tracefree = _canonical((raw["E22"] - raw["E33"] / sine**2) / 2)

    def scalar_triple(value: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
        equator = _canonical(value.subs(theta, sp.pi / 2))
        plus_half = _canonical(value.subs(theta, sp.pi / 3))
        minus_half = _canonical(value.subs(theta, 2 * sp.pi / 3))
        ell1 = _canonical(plus_half - minus_half)
        ell2 = _canonical(sp.Rational(4, 3) * (plus_half + minus_half - 2 * equator))
        ell0 = _canonical(equator + ell2 / 2)
        audit = _canonical(
            value.subs(theta, sp.pi / 4)
            - ell0
            - ell1 * sp.cos(sp.pi / 4)
            - ell2 * harmonic2.subs(theta, sp.pi / 4)
        )
        if audit != 0:
            raise AssertionError(f"scalar row contains an unexpected harmonic: {audit}")
        return ell0, ell1, ell2

    scalar_rows = {
        "metric_00": raw["E00"],
        "metric_01": raw["E01"],
        "metric_11": raw["E11"],
        "sphere_trace": sphere_trace,
    }
    pairs_by_row = {name: scalar_triple(value) for name, value in scalar_rows.items()}
    homogeneous = {name: pair[0] for name, pair in pairs_by_row.items()}
    maxwell_0 = scalar_triple(raw["M0"])
    maxwell_1 = scalar_triple(raw["M1"])
    homogeneous.update({"maxwell_0": maxwell_0[0], "maxwell_1": maxwell_1[0]})

    def vector_pair(row_theta: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
        reduced = _canonical(row_theta / (-sine))
        ell1 = _canonical(reduced.subs(theta, sp.pi / 2))
        ell2 = _canonical(sp.Rational(2, 3) * (reduced.subs(theta, sp.pi / 3) - ell1))
        audit = _canonical(reduced.subs(theta, sp.pi / 4) - ell1 - 3 * ell2 * sp.cos(sp.pi / 4))
        if audit != 0:
            raise AssertionError(f"gradient row contains an unexpected harmonic: {audit}")
        return ell1, ell2

    def axial_pair(row_phi: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
        reduced = _canonical(row_phi / sine**2)
        ell1 = _canonical(reduced.subs(theta, sp.pi / 2))
        ell2 = _canonical(sp.Rational(2, 3) * (reduced.subs(theta, sp.pi / 3) - ell1))
        audit = _canonical(reduced.subs(theta, sp.pi / 4) - ell1 - 3 * ell2 * sp.cos(sp.pi / 4))
        if audit != 0:
            raise AssertionError(f"axial row contains an unexpected harmonic: {audit}")
        return ell1, ell2

    def axial_density_pair(value: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
        ell1 = _canonical(value.subs(theta, sp.pi / 2))
        ell2 = _canonical(sp.Rational(2, 3) * (value.subs(theta, sp.pi / 3) - ell1))
        audit = _canonical(value.subs(theta, sp.pi / 4) - ell1 - 3 * ell2 * sp.cos(sp.pi / 4))
        if audit != 0:
            raise AssertionError(f"Maxwell axial row contains an unexpected harmonic: {audit}")
        return ell1, ell2

    metric_0a = vector_pair(raw["E02"])
    metric_1a = vector_pair(raw["E12"])
    axial_metric_t = axial_pair(raw["E03"])
    axial_metric_x = axial_pair(raw["E13"])
    maxwell_axial = axial_density_pair(raw["M3"])
    polar_l2 = {name: pair[2] for name, pair in pairs_by_row.items()}
    polar_l2.update(
        {
            "metric_0a": metric_0a[1],
            "metric_1a": metric_1a[1],
            "sphere_tracefree": _canonical(sphere_tracefree / tensor2),
            "maxwell_axial_density": maxwell_axial[1],
        }
    )
    polar_l1 = {
        "metric_00": pairs_by_row["metric_00"][1],
        "metric_01": pairs_by_row["metric_01"][1],
        "metric_11": pairs_by_row["metric_11"][1],
        "metric_0a": metric_0a[0],
        "metric_1a": metric_1a[0],
        "sphere_trace": pairs_by_row["sphere_trace"][1],
        "sphere_tracefree": sp.Integer(0),
        "maxwell_axial_density": maxwell_axial[0],
    }
    axial_l1 = {
        "metric_t": axial_metric_t[0],
        "metric_x": axial_metric_x[0],
        "maxwell_t": maxwell_0[1],
        "maxwell_x": maxwell_1[1],
    }
    axial_l2_audit = [axial_metric_t[1], axial_metric_x[1], maxwell_0[2], maxwell_1[2]]
    if any(_canonical(value) != 0 for value in axial_l2_audit):
        raise AssertionError(f"unexpected axial L2 source: {axial_l2_audit}")
    for block in (homogeneous, polar_l1, axial_l1, polar_l2):
        for name, value in block.items():
            if value.has(theta):
                raise AssertionError(f"projection left theta in {name}: {value}")
    return {
        "homogeneous_L0": homogeneous,
        "polar_L1": polar_l1,
        "axial_L1": axial_l1,
        "polar_L2": polar_l2,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    for block, rows in direct_source().items():
        print(block, {name: str(sp.factor(value)) for name, value in rows.items()})


if __name__ == "__main__":
    main()

"""Slow exact Weyl--Maxwell Lee--Wald fixture for physical ell=1 modes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_radiative_lee_wald_fixture import (
    _axial_variation,
)
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    weyl_maxwell_current_time,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/weyl_maxwell_ell1_exceptional_lee_wald_fixture.json"


class WeylMaxwellEll1FixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylMaxwellEll1FixtureError(message)


def _add_variations(
    first: tuple[sp.Matrix, sp.Matrix],
    second: tuple[sp.Matrix, sp.Matrix],
) -> tuple[sp.Matrix, sp.Matrix]:
    return first[0] + second[0], first[1] + second[1]


def _polar_variation(
    physical: sp.Expr,
    gauge: sp.Expr,
    wave: sp.Expr,
    harmonic: sp.Expr,
    axial_one_form: sp.Expr,
    sine: sp.Expr,
    momentum: sp.Symbol,
    frequency: sp.Symbol,
) -> tuple[sp.Matrix, sp.Matrix]:
    metric = sp.zeros(4)
    potential = sp.zeros(4, 1)
    coefficients = {
        "A": -2 * physical + 2 * frequency**2 * gauge,
        "B": -2 * momentum * frequency * gauge,
        "C": 2 * physical + 2 * momentum**2 * gauge,
        "K": -2 * gauge,
        "U": physical - gauge,
    }
    metric[0, 0] = coefficients["A"] * wave * harmonic
    metric[0, 1] = metric[1, 0] = coefficients["B"] * wave * harmonic
    metric[1, 1] = coefficients["C"] * wave * harmonic
    metric[2, 2] = coefficients["K"] * wave * harmonic
    metric[3, 3] = coefficients["K"] * wave * harmonic * sine**2
    potential[3] = coefficients["U"] * wave * axial_one_form
    return metric, potential


def _axial_gauge_variation(
    gauge: sp.Expr,
    wave: sp.Expr,
    harmonic: sp.Expr,
    axial_one_form: sp.Expr,
    momentum: sp.Symbol,
    frequency: sp.Symbol,
    conjugate: bool,
) -> tuple[sp.Matrix, sp.Matrix]:
    metric = sp.zeros(4)
    potential = sp.zeros(4, 1)
    sign = -1 if conjugate else 1
    metric[0, 3] = metric[3, 0] = (
        -sign * sp.I * frequency * gauge * wave * axial_one_form
    )
    metric[1, 3] = metric[3, 1] = (
        sign * sp.I * momentum * gauge * wave * axial_one_form
    )
    potential[0] = sign * sp.I * frequency * gauge * wave * harmonic
    potential[1] = -sign * sp.I * momentum * gauge * wave * harmonic
    return metric, potential


def _fixed_sphere_integral(density: sp.Expr, theta: sp.Symbol) -> sp.Expr:
    real_trigonometric = sp.trigsimp(
        sp.expand_trig(sp.trigsimp(sp.expand_complex(density), method="fu")),
        method="fu",
    )
    result = sp.factor(
        2 * sp.pi * sp.integrate(real_trigonometric, (theta, 0, sp.pi))
    )
    _require(not result.has(theta), "theta survived the fixed ell=1 sphere integral")
    return result


def _shell_reduce(
    expression: sp.Expr,
    frequency: sp.Symbol,
    momentum: sp.Symbol,
) -> sp.Expr:
    numerator, denominator = sp.fraction(sp.cancel(sp.expand(expression)))
    _require(not denominator.has(frequency), "frequency-dependent denominator in shell reduction")
    remainder = sp.Poly(numerator, frequency).rem(
        sp.Poly(frequency**2 - momentum**2 - 4, frequency)
    )
    return sp.factor(remainder.as_expr() / denominator)


def _coefficient_matrix(
    current: sp.Expr,
    theta: sp.Symbol,
    frequency: sp.Symbol,
    momentum: sp.Symbol,
    amplitudes: tuple[sp.Symbol, sp.Symbol, sp.Symbol, sp.Symbol],
) -> tuple[sp.Matrix, sp.Matrix]:
    physical_first, gauge_first, physical_second, gauge_second = amplitudes
    zero = {symbol: 0 for symbol in amplitudes}
    rows = ((physical_first, gauge_first), (physical_second, gauge_second))
    off_shell = sp.zeros(2)
    on_shell = sp.zeros(2)
    for row, left in enumerate(rows[0]):
        for column, right in enumerate(rows[1]):
            density = sp.diff(sp.diff(current, left), right).subs(zero)
            integrated = _fixed_sphere_integral(density, theta)
            off_shell[row, column] = integrated
            on_shell[row, column] = _shell_reduce(
                integrated, frequency, momentum
            )
    return off_shell.applyfunc(sp.factor), on_shell.applyfunc(sp.factor)


def _matrix_rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(matrix[row, column]) for column in range(2)] for row in range(2)]


def _direct_fixture() -> dict[str, Any]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    momentum, frequency = sp.symbols("k omega", real=True)
    physical_first, gauge_first, physical_second, gauge_second = sp.symbols(
        "p1 g1 p2 g2", real=True
    )
    amplitudes = (
        physical_first,
        gauge_first,
        physical_second,
        gauge_second,
    )
    sine = sp.sin(theta)
    harmonic = sp.cos(theta)
    axial_one_form = -sine * sp.diff(harmonic, theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    inverse_wave = 1 / wave
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine

    axial_first = _add_variations(
        _axial_variation(
            physical_first,
            physical_first,
            wave,
            harmonic,
            axial_one_form,
            momentum,
            frequency,
        ),
        _axial_gauge_variation(
            gauge_first,
            wave,
            harmonic,
            axial_one_form,
            momentum,
            frequency,
            False,
        ),
    )
    axial_second = _add_variations(
        _axial_variation(
            physical_second,
            physical_second,
            inverse_wave,
            harmonic,
            axial_one_form,
            momentum,
            frequency,
        ),
        _axial_gauge_variation(
            gauge_second,
            inverse_wave,
            harmonic,
            axial_one_form,
            momentum,
            frequency,
            True,
        ),
    )
    polar_first = _polar_variation(
        physical_first,
        gauge_first,
        wave,
        harmonic,
        axial_one_form,
        sine,
        momentum,
        frequency,
    )
    polar_second = _polar_variation(
        physical_second,
        gauge_second,
        inverse_wave,
        harmonic,
        axial_one_form,
        sine,
        momentum,
        frequency,
    )

    axial_current = weyl_maxwell_current_time(
        metric, field, axial_first, axial_second, coordinates, sp.Integer(3)
    )
    polar_current = weyl_maxwell_current_time(
        metric, field, polar_first, polar_second, coordinates, sp.Integer(3)
    )
    axial_off_shell, axial_on_shell = _coefficient_matrix(
        axial_current, theta, frequency, momentum, amplitudes
    )
    polar_off_shell, polar_on_shell = _coefficient_matrix(
        polar_current, theta, frequency, momentum, amplitudes
    )

    expected_axial = sp.Matrix(
        [[-sp.Rational(256, 3) * sp.I * sp.pi * frequency, 0], [0, 0]]
    )
    expected_polar = sp.Matrix(
        [[-sp.Rational(64, 3) * sp.I * sp.pi * frequency, 0], [0, 0]]
    )
    _require(axial_on_shell == expected_axial, "axial ell=1 shell matrix changed")
    _require(polar_on_shell == expected_polar, "polar ell=1 shell matrix changed")

    return {
        "harmonic": "Y_10=cos(theta)",
        "harmonic_norm": "N_10=4*pi/3",
        "dispersion": "omega^2=k^2+4",
        "amplitude_order": ["physical", "residual_gauge"],
        "axial": {
            "physical_representative": "(H,Q)=(p,p) in the curl-potential convention",
            "gauge_representative": "delta h_A=partial_A s, delta q_A=-partial_A s",
            "off_shell_integrated_coordinate_current_matrix": _matrix_rows(axial_off_shell),
            "on_shell_integrated_coordinate_current_matrix": _matrix_rows(axial_on_shell),
            "gauge_row_and_column_zero_on_shell": True,
        },
        "polar": {
            "physical_representative": "K=0: (A,B,C,U)=(-2p,0,2p,p)",
            "gauge_representative": "(A,B,C,K,U)=(2*omega^2,-2*k*omega,2*k^2,-2,-1)*g",
            "off_shell_integrated_coordinate_current_matrix": _matrix_rows(polar_off_shell),
            "on_shell_integrated_coordinate_current_matrix": _matrix_rows(polar_on_shell),
            "gauge_row_and_column_zero_on_shell": True,
        },
        "shell_remainders": {
            "axial_physical_target_minus_expected": "0",
            "axial_physical_gauge": "0",
            "axial_gauge_physical": "0",
            "axial_gauge_gauge": "0",
            "polar_physical_target_minus_expected": "0",
            "polar_physical_gauge": "0",
            "polar_gauge_physical": "0",
            "polar_gauge_gauge": "0",
        },
    }


def build_fixture() -> dict[str, Any]:
    return {
        "schema": "weyl-maxwell-ell1-exceptional-lee-wald-fixture-v1",
        "result_id": "WEYL_MAXWELL_ELL1_EXCEPTIONAL_LEE_WALD_FIXTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "physical axial and polar ell=1 Einstein-Maxwell quotient modes on R_t x S1_L x S2, arbitrary symbolic periodic momentum k, plus their smooth residual gauge representatives, before final residual SO(4,2) quotient",
        "current_convention": "omega^t=delta1 theta^t(delta2)-delta2 theta^t(delta1); literal S_WM=int sqrt(-g)[(3/8)C^2-F^2/4]",
        "direct_current": _direct_fixture(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    fixture = build_fixture()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        _require(stored == fixture, f"stale ell=1 exceptional fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

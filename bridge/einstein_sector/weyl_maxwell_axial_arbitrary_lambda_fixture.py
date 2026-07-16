"""Slow exact arbitrary-harmonic Weyl--Maxwell axial Lee--Wald rail.

The direct coordinate current is computed with an unevaluated axisymmetric
spherical eigenfunction.  Its second derivative is reduced only with

    Y'' + cot(theta) Y' + lambda Y = 0,

and the remaining density is reduced modulo an explicitly displayed total
theta derivative.  No finite list of integer harmonics is interpolated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_radiative_lee_wald_fixture import (
    _axial_variation,
    _sphere_integral,
)
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    weyl_maxwell_current_time,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/weyl_maxwell_axial_arbitrary_lambda_fixture.json"
ELL2_FIXTURE = ROOT / "bridge/certificates/weyl_maxwell_axial_lee_wald_fixture.json"


class WeylMaxwellAxialArbitraryLambdaFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylMaxwellAxialArbitraryLambdaFixtureError(message)


def _direct_current() -> dict[str, Any]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    cosine = sp.cos(theta)
    momentum, frequency, eigenvalue, mass = sp.symbols(
        "k omega lambda mu", real=True
    )
    metric_first, metric_second, maxwell_first, maxwell_second = sp.symbols(
        "H1 H2 Q1 Q2", real=True
    )
    harmonic = sp.Function("Y")(theta)
    first_derivative = sp.diff(harmonic, theta)
    second_derivative = sp.diff(harmonic, theta, 2)
    axial_one_form = -sine * first_derivative
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    first = _axial_variation(
        metric_first,
        maxwell_first,
        wave,
        harmonic,
        axial_one_form,
        momentum,
        frequency,
    )
    second = _axial_variation(
        metric_second,
        maxwell_second,
        1 / wave,
        harmonic,
        axial_one_form,
        momentum,
        frequency,
    )
    current = weyl_maxwell_current_time(
        metric, field, first, second, coordinates, sp.Integer(3)
    )

    raw_density = (
        metric_first
        * metric_second
        * (
            -3 * mass * sine * first_derivative**2
            + sp.Rational(1, 2) * sine * first_derivative**2
            + 3 * sine * second_derivative**2
            + 3 * cosine * first_derivative * second_derivative
            + 3 * cosine**2 * first_derivative**2 / sine
        )
        - 2 * maxwell_first * maxwell_second * sine * harmonic**2
    )
    _require(
        sp.trigsimp(
            current
            - sp.I
            * frequency
            * (frequency**2 - momentum**2)
            * raw_density.subs(mass, frequency**2 - momentum**2)
        )
        == 0,
        "direct generic current did not reduce to the declared raw density",
    )

    harmonic_rule = {
        second_derivative: -sp.cot(theta) * first_derivative - eigenvalue * harmonic
    }
    ode_reduced = sp.trigsimp(sp.expand_trig(raw_density.xreplace(harmonic_rule)))
    canonical_density = sine * (
        eigenvalue
        * (3 * eigenvalue - 1 - 3 * mass)
        * metric_first
        * metric_second
        * harmonic**2
        - 2 * maxwell_first * maxwell_second * harmonic**2
    )
    boundary_primitive = -metric_first * metric_second * (
        (1 + 3 * mass) * sine * harmonic * first_derivative
        + sp.Rational(3, 2) * cosine * first_derivative**2
    )
    total_derivative_remainder = sp.trigsimp(
        sp.expand_trig(
            ode_reduced
            - canonical_density
            - sp.diff(boundary_primitive, theta)
        ).xreplace(harmonic_rule)
    )
    _require(
        sp.simplify(total_derivative_remainder) == 0,
        "harmonic ODE plus total-derivative reduction failed",
    )

    norm = sp.Symbol("N_lambda", positive=True)
    integrated = sp.I * frequency * mass * norm * (
        eigenvalue
        * (3 * eigenvalue - 1 - 3 * mass)
        * metric_first
        * metric_second
        - 2 * maxwell_first * maxwell_second
    )

    ell2_harmonic = sp.legendre(2, sp.cos(theta))
    ell2_current = _sphere_integral(
        current.subs(
            {
                harmonic: ell2_harmonic,
                sp.diff(harmonic, theta): sp.diff(ell2_harmonic, theta),
                sp.diff(harmonic, theta, 2): sp.diff(ell2_harmonic, theta, 2),
            }
        ),
        theta,
        azimuth,
    )
    old_fixture = json.loads(ELL2_FIXTURE.read_text(encoding="utf-8"))
    old_locals = {
        "k": momentum,
        "omega": frequency,
        "H": metric_first,
        "Q": maxwell_first,
        "I": sp.I,
        "pi": sp.pi,
    }
    old_ell2 = sp.sympify(
        old_fixture["axial_ell2"]["weyl_maxwell_integrated_coordinate_current"],
        locals=old_locals,
    )
    ell2_diagonal = ell2_current.subs(
        {metric_second: metric_first, maxwell_second: maxwell_first}
    )
    _require(
        sp.simplify(ell2_diagonal - old_ell2) == 0,
        "arbitrary-harmonic current does not reproduce the certified ell=2 fixture",
    )

    return {
        "harmonic_identity": "Y''+cot(theta)*Y'+lambda*Y=0",
        "derivation_rule": "arbitrary Y(theta), followed by the harmonic ODE and an explicit total derivative; no finite-ell interpolation",
        "direct_bilinear_coordinate_current": str(sp.factor(current)),
        "raw_density_after_mu_substitution": str(raw_density),
        "boundary_primitive": str(boundary_primitive),
        "ode_plus_total_derivative_remainder": str(sp.simplify(total_derivative_remainder)),
        "regular_pole_boundary_value": "0",
        "harmonic_norm": "N_lambda=integral_(S2) Y^2 dOmega>0",
        "integrated_bilinear_coordinate_current": str(sp.factor(integrated)),
        "coefficient_matrix_in_minus_i_omega_mu_N_convention": [
            ["lambda*(3*mu-3*lambda+1)", "0"],
            ["0", "2"],
        ],
        "ell2_normalization_remainder": str(sp.simplify(ell2_diagonal - old_ell2)),
    }


def build_fixture() -> dict[str, Any]:
    return {
        "schema": "weyl-maxwell-axial-arbitrary-lambda-fixture-v1",
        "result_id": "WEYL_MAXWELL_AXIAL_ARBITRARY_LAMBDA_FIXTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "arbitrary axisymmetric scalar harmonic eigenvalue lambda, symbolic Fourier momentum k and frequency omega, bilinear axial Einstein-Maxwell curl representatives",
        "current": _direct_current(),
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
        _require(stored == fixture, f"stale arbitrary-lambda fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

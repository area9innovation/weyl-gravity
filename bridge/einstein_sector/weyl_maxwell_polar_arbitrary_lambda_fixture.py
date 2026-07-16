"""Slow exact arbitrary-harmonic polar Weyl--Maxwell Lee--Wald rail."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_radiative_lee_wald_fixture import (
    _polar_variation,
    _sphere_integral,
)
from bridge.einstein_sector.quadratic_harmonic_density import (
    quadratic_normal_form,
)
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    weyl_maxwell_current_time,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/weyl_maxwell_polar_arbitrary_lambda_fixture.json"


class WeylMaxwellPolarArbitraryLambdaFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylMaxwellPolarArbitraryLambdaFixtureError(message)


def _replace_even_momentum(
    expression: sp.Expr,
    momentum: sp.Symbol,
    frequency: sp.Symbol,
    mass: sp.Symbol,
) -> sp.Expr:
    polynomial = sp.Poly(sp.expand(expression), momentum)
    result = sp.S.Zero
    for (degree,), coefficient in polynomial.terms():
        _require(degree % 2 == 0, "odd momentum power survived the polar current")
        result += coefficient * (frequency**2 - mass) ** (degree // 2)
    return sp.factor(sp.simplify(result))


def _direct_current() -> dict[str, Any]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    momentum, frequency, eigenvalue, mass = sp.symbols(
        "k omega lambda mu", real=True
    )
    metric_first, metric_second, maxwell_first, maxwell_second = sp.symbols(
        "K1 K2 U1 U2", real=True
    )
    harmonic = sp.Function("Y")(theta)
    axial_one_form = -sine * sp.diff(harmonic, theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    first = _polar_variation(
        metric_first,
        maxwell_first,
        wave,
        harmonic,
        axial_one_form,
        sine,
        momentum,
        frequency,
    )
    second = _polar_variation(
        metric_second,
        maxwell_second,
        1 / wave,
        harmonic,
        axial_one_form,
        sine,
        momentum,
        frequency,
    )
    current = weyl_maxwell_current_time(
        metric, field, first, second, coordinates, sp.Integer(3)
    )

    scaled = sp.cancel(
        current * (momentum**2 - frequency**2) / (sp.I * frequency)
    )
    scaled_mass = _replace_even_momentum(
        scaled, momentum, frequency, mass
    )
    density = sp.factor(sp.simplify(scaled_mass / mass))
    _require(
        sp.simplify(sp.diff(density, frequency)) == 0,
        "frequency survived the mu reduction",
    )
    normal = quadratic_normal_form(
        density, harmonic, theta, eigenvalue, primitive_degree=10
    )

    amplitude_symbols = (
        metric_first,
        metric_second,
        maxwell_first,
        maxwell_second,
    )
    coefficient_polynomial = sp.Poly(
        sp.expand(normal.canonical_coefficient), *amplitude_symbols
    )
    matrix = sp.Matrix(
        [
            [
                coefficient_polynomial.coeff_monomial(metric_first * metric_second),
                coefficient_polynomial.coeff_monomial(metric_first * maxwell_second),
            ],
            [
                coefficient_polynomial.coeff_monomial(maxwell_first * metric_second),
                coefficient_polynomial.coeff_monomial(maxwell_first * maxwell_second),
            ],
        ]
    ).applyfunc(sp.factor)
    _require(matrix[0, 1] == matrix[1, 0], "integrated polar matrix is not symmetric")
    reconstructed = (
        sp.Matrix([metric_first, maxwell_first]).T
        * matrix
        * sp.Matrix([metric_second, maxwell_second])
    )[0]
    _require(
        sp.simplify(reconstructed - normal.canonical_coefficient) == 0,
        "polar matrix does not reconstruct the canonical coefficient",
    )

    ell2_harmonic = sp.legendre(2, sp.cos(theta))
    ell2_substitutions = {
        harmonic: ell2_harmonic,
        sp.diff(harmonic, theta): sp.diff(ell2_harmonic, theta),
        sp.diff(harmonic, theta, 2): sp.diff(ell2_harmonic, theta, 2),
    }
    ell2_direct = _sphere_integral(current.xreplace(ell2_substitutions), theta, azimuth)
    ell2_normal = -sp.I * frequency * sp.Rational(4, 5) * sp.pi * reconstructed.subs(
        {eigenvalue: 6, mass: frequency**2 - momentum**2}
    )
    _require(
        sp.simplify(ell2_direct - ell2_normal) == 0,
        "ell=2 direct integral does not match the arbitrary-lambda normal form",
    )

    return {
        "harmonic_identity": "Y''+cot(theta)*Y'+lambda*Y=0",
        "derivation_rule": "arbitrary Y(theta), exact Legendre normal form with a solved pole-vanishing quadratic primitive; no finite-ell interpolation",
        "pairing_convention": "omega_WM^t=-i*omega*N_lambda*(K1,U1) G_WM,P(lambda,mu) (K2,U2)^T",
        "direct_bilinear_coordinate_current": str(sp.factor(current)),
        "mu_reduced_density": str(density),
        "normal_form_primitive_in_z": str(normal.primitive),
        "normal_form_remainder": str(normal.remainder),
        "harmonic_norm": "N_lambda=integral_(S2)Y^2 dOmega>0",
        "coefficient_matrix": [
            [str(matrix[row, column]) for column in range(2)]
            for row in range(2)
        ],
        "ell2_direct_integral": str(sp.factor(ell2_direct)),
        "ell2_normalization_remainder": str(sp.simplify(ell2_direct - ell2_normal)),
    }


def build_fixture() -> dict[str, Any]:
    return {
        "schema": "weyl-maxwell-polar-arbitrary-lambda-fixture-v1",
        "result_id": "WEYL_MAXWELL_POLAR_ARBITRARY_LAMBDA_FIXTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "arbitrary axisymmetric scalar harmonic eigenvalue lambda, symbolic nonzero mu=omega^2-k^2, bilinear polar Einstein-Maxwell master representatives",
        "mu_zero_scope": "the reconstructed representative is defined for mu!=0; the independently certified polar rank audit proves that the gauge-fixed ell>=2 mu=0 solution is only the zero field",
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
        _require(stored == fixture, f"stale arbitrary-lambda polar fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

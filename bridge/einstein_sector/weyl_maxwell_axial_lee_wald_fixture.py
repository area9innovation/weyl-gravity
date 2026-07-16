"""Slow exact Weyl--Maxwell axial Lee--Wald kill-test rail."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_radiative_lee_wald_fixture import (
    _axial_variation,
    _sphere_integral,
    _symplectic_current_time,
)
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    einstein_theta_time_variation,
    exterior_derivative,
    linearized_geometry,
    maxwell_theta_time_variation,
    weyl_maxwell_current_time,
    weyl_theta_time_variation,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/weyl_maxwell_axial_lee_wald_fixture.json"


class WeylMaxwellAxialFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylMaxwellAxialFixtureError(message)


def _background_bach_control(
    metric: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
) -> list[list[str]]:
    sine = sp.sin(coordinates[2])
    inverse = metric.inv()
    geometry = linearized_geometry(metric, sp.zeros(4), coordinates)
    ricci = sp.diag(0, 0, 1, sine**2)
    schouten = (ricci - sp.Rational(1, 3) * metric) / 2
    schouten_up = sp.simplify(inverse * schouten * inverse)
    bach = sp.zeros(4)
    for first in range(4):
        for third in range(4):
            value = sp.S.Zero
            for second in range(4):
                for fourth in range(4):
                    weyl_lower = (
                        metric[first, first]
                        * metric[second, second]
                        * metric[third, third]
                        * metric[fourth, fourth]
                        * geometry.weyl_up[first][second][third][fourth]
                    )
                    value += schouten_up[second, fourth] * weyl_lower
            bach[first, third] = sp.simplify(value)
    orthonormal = sp.diag(
        bach[0, 0],
        bach[1, 1],
        bach[2, 2],
        sp.simplify(bach[3, 3] / sine**2),
    )
    _require(
        orthonormal == sp.diag(sp.Rational(1, 6), -sp.Rational(1, 6), sp.Rational(1, 6), sp.Rational(1, 6)),
        "background Bach convention changed",
    )
    return [[str(orthonormal[row, column]) for column in range(4)] for row in range(4)]


def _axial_currents() -> dict[str, Any]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    momentum, frequency = sp.symbols("k omega", real=True)
    metric_master, maxwell_master = sp.symbols("H Q", real=True)
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    first = _axial_variation(
        metric_master,
        maxwell_master,
        wave,
        harmonic,
        axial_one_form,
        momentum,
        frequency,
    )
    second = _axial_variation(
        metric_master,
        maxwell_master,
        1 / wave,
        harmonic,
        axial_one_form,
        momentum,
        frequency,
    )
    first_metric, first_potential = first
    second_metric, second_potential = second
    first_geometry = linearized_geometry(metric, first_metric, coordinates)
    second_geometry = linearized_geometry(metric, second_metric, coordinates)
    maxwell_first_on_second = maxwell_theta_time_variation(
        metric,
        field,
        first_metric,
        exterior_derivative(first_potential, coordinates),
        second_potential,
        coordinates,
    )
    maxwell_second_on_first = maxwell_theta_time_variation(
        metric,
        field,
        second_metric,
        exterior_derivative(second_potential, coordinates),
        first_potential,
        coordinates,
    )
    maxwell_current = maxwell_first_on_second - maxwell_second_on_first
    einstein_current = sp.factor(
        einstein_theta_time_variation(
            first_geometry, second_metric, coordinates
        )
        - einstein_theta_time_variation(
            second_geometry, first_metric, coordinates
        )
        + maxwell_current
    )
    weyl_current = sp.factor(
        weyl_theta_time_variation(
            first_geometry, second_metric, coordinates, sp.Integer(3)
        )
        - weyl_theta_time_variation(
            second_geometry, first_metric, coordinates, sp.Integer(3)
        )
        + maxwell_current
    )
    independent_einstein = _symplectic_current_time(
        metric, field, first, second, coordinates
    )
    pointwise_remainder = sp.simplify(
        sp.refine(einstein_current - independent_einstein, sp.Q.positive(sine))
    )
    _require(pointwise_remainder == 0, "Einstein curvature-momentum control failed")

    norm = 4 * sp.pi / 5
    mass = frequency**2 - momentum**2
    expected_einstein = (
        -2
        * sp.I
        * frequency
        * norm
        / 2
        * mass
        * (6 * metric_master**2 + 2 * maxwell_master**2)
    )
    integrated_einstein = _sphere_integral(einstein_current, theta, azimuth)
    integrated_weyl = _sphere_integral(weyl_current, theta, azimuth)
    expected_weyl = (
        -8
        * sp.I
        * sp.pi
        * frequency
        * (momentum**2 - frequency**2)
        * (
            9 * metric_master**2 * momentum**2
            - 9 * metric_master**2 * frequency**2
            + 51 * metric_master**2
            - maxwell_master**2
        )
        / 5
    )
    _require(sp.simplify(integrated_einstein - expected_einstein) == 0, "Einstein integrated control failed")
    _require(sp.simplify(integrated_weyl - expected_weyl) == 0, "Weyl integrated current changed")
    _require(sp.diff(integrated_weyl, time) == 0 and sp.diff(integrated_weyl, space) == 0, "Weyl current is not conserved on the paired fixture")

    return {
        "harmonic": "Y_20=P_2(cos(theta))",
        "harmonic_norm": "4*pi/5",
        "representative": "h_(t,ax)=k*H*e^{i(kx-omega t)}X_a; h_(x,ax)=-omega*H*e^{i(kx-omega t)}X_a; a_t=k*Q*e^{i(kx-omega t)}Y; a_x=-omega*Q*e^{i(kx-omega t)}Y",
        "einstein_curvature_momentum_pointwise_remainder": str(pointwise_remainder),
        "einstein_integrated_coordinate_current": str(sp.factor(integrated_einstein)),
        "weyl_maxwell_integrated_coordinate_current": str(sp.factor(integrated_weyl)),
        "time_derivative": str(sp.diff(integrated_weyl, time)),
        "space_derivative": str(sp.diff(integrated_weyl, space)),
    }


def _flat_control() -> dict[str, str]:
    time, space, y_coordinate, z_coordinate = sp.symbols("t x y z", real=True)
    coordinates = (time, space, y_coordinate, z_coordinate)
    momentum, frequency, amplitude, alpha_b = sp.symbols(
        "k omega A alpha_B", real=True
    )
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    metric = sp.diag(-1, 1, 1, 1)
    field = sp.zeros(4)

    def transverse_traceless(profile: sp.Expr) -> tuple[sp.Matrix, sp.Matrix]:
        variation = sp.zeros(4)
        variation[2, 2] = amplitude * profile
        variation[3, 3] = -amplitude * profile
        return variation, sp.zeros(4, 1)

    current = sp.factor(
        weyl_maxwell_current_time(
            metric,
            field,
            transverse_traceless(wave),
            transverse_traceless(1 / wave),
            coordinates,
            alpha_b,
        )
    )
    expected = sp.I * amplitude**2 * alpha_b * frequency * (
        momentum**2 - frequency**2
    )
    _require(sp.simplify(current - expected) == 0, "flat TT current changed")
    return {
        "current": str(current),
        "einstein_shell": "omega^2=k^2",
        "restricted_value": "0",
    }


def _weyl_gauge_control() -> dict[str, str]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    momentum, frequency, metric_master, maxwell_master, sigma = sp.symbols(
        "k omega H Q sigma", real=True
    )
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    pure_weyl = (2 * sigma * metric, sp.zeros(4, 1))
    axial = _axial_variation(
        metric_master,
        maxwell_master,
        wave,
        harmonic,
        axial_one_form,
        momentum,
        frequency,
    )
    current = sp.factor(
        weyl_maxwell_current_time(
            metric, field, pure_weyl, axial, coordinates
        )
    )
    _require(current == 0, "pure Weyl direction is not a current kernel")
    return {"pointwise_current": "0", "integrated_current": "0"}


def build_fixture() -> dict[str, Any]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    metric = sp.diag(-1, 1, 1, sp.sin(theta) ** 2)
    return {
        "schema": "weyl-maxwell-axial-lee-wald-fixture-v1",
        "result_id": "WEYL_MAXWELL_AXIAL_LEE_WALD_FIXTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "background_bach_orthonormal": _background_bach_control(
            metric, (time, space, theta, azimuth)
        ),
        "flat_tt_control": _flat_control(),
        "axial_ell2": _axial_currents(),
        "pure_weyl_gauge_control": _weyl_gauge_control(),
        "current_formula": {
            "curvature_momentum": "P^abcd=(alpha_B/4)C^abcd",
            "potential": "Theta_C2^mu=2*sqrt(-g)[P^(mu a b nu)nabla_nu(delta g_ab)-nabla_nu(P^(mu a b nu))delta g_ab]",
            "critical_rule": "delta[nabla P] is retained although nabla Cbar=0",
            "maxwell": "Theta_M^mu=-sqrt(-g)F^(mu nu)delta A_nu with full metric/flux variation in omega",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    fixture = build_fixture()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(fixture, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        _require(stored == fixture, f"stale axial Lee-Wald fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

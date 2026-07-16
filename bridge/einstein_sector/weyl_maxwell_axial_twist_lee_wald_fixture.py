"""Direct Weyl--Maxwell current on the axial ell=1 twist block."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_exceptional_global_symplectic import (
    _twist_variation,
)
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    weyl_maxwell_current_time,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/weyl_maxwell_axial_twist_lee_wald_fixture.json"


class AxialTwistFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialTwistFixtureError(message)


def _integrate_sphere(density: sp.Expr, theta: sp.Symbol) -> sp.Expr:
    expanded = sp.trigsimp(
        sp.expand_trig(sp.trigsimp(sp.expand_complex(density), method="fu")),
        method="fu",
    )
    result = sp.factor(2 * sp.pi * sp.integrate(expanded, (theta, 0, sp.pi)))
    _require(not result.has(theta), "theta survived twist sphere integration")
    return result


def _direct_fixture() -> dict[str, Any]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    first_position, first_velocity, second_position, second_velocity = sp.symbols(
        "A1 B1 A2 B2", real=True
    )
    harmonic = sp.cos(theta)
    axial_one_form = -sine * sp.diff(harmonic, theta)
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    density = weyl_maxwell_current_time(
        metric,
        field,
        _twist_variation(
            first_position, first_velocity, time, harmonic, axial_one_form
        ),
        _twist_variation(
            second_position, second_velocity, time, harmonic, axial_one_form
        ),
        coordinates,
        sp.Integer(3),
    )
    integrated = _integrate_sphere(density, theta)
    expected = sp.Rational(16, 3) * sp.pi * (
        first_position * second_velocity - second_position * first_velocity
    )
    _require(sp.simplify(integrated - expected) == 0, "twist target current changed")
    matrix = sp.Matrix(
        2,
        2,
        lambda row, column: sp.diff(
            sp.diff(integrated, (first_position, first_velocity)[row]),
            (second_position, second_velocity)[column],
        ),
    )
    _require(matrix == -matrix.T, "twist current matrix is not antisymmetric")
    _require(matrix.rank() == 2, "twist target current lost rank")
    _require(sp.factor(matrix.det()) == sp.Rational(256, 9) * sp.pi**2, "twist determinant changed")
    _require(sp.diff(integrated, time) == 0, "twist target current is time dependent")
    return {
        "parameter_order": ["A", "B"],
        "representative": "h_(x,a)=(A+B*t)X_a, a_x=-(A+B*t)Y_1m",
        "harmonic": "direct fixture uses Y_10=cos(theta), N_10=4*pi/3",
        "integrated_coordinate_current_per_unit_x": str(integrated),
        "coordinate_current_matrix": [
            [str(matrix[row, column]) for column in range(2)] for row in range(2)
        ],
        "time_derivative": "0",
        "matrix_rank": 2,
        "matrix_determinant": "256*pi**2/9",
        "all_m_extension": "SO(3) equivariance gives the same coefficient times N_1m for all three real harmonics",
    }


def build_fixture() -> dict[str, Any]:
    return {
        "schema": "weyl-maxwell-axial-twist-lee-wald-fixture-v1",
        "result_id": "WEYL_MAXWELL_AXIAL_TWIST_LEE_WALD_FIXTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "generalized zero-frequency axial ell=1 twist block on R_t x S1_L x S2 at fixed periodicity, before final residual quotient",
        "current_convention": "omega^t=delta1 theta^t(delta2)-delta2 theta^t(delta1); Omega_Sigma=-L*int_S2 omega^t",
        "direct_current": _direct_fixture(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    fixture = build_fixture()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        _require(stored == fixture, f"stale axial twist fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

"""Direct Weyl--Maxwell current on the homogeneous generalized block."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_exceptional_global_symplectic import (
    _ell0_variation,
)
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    weyl_maxwell_current_time,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/weyl_maxwell_homogeneous_global_lee_wald_fixture.json"


class HomogeneousGlobalFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HomogeneousGlobalFixtureError(message)


def _integrate_sphere(density: sp.Expr, theta: sp.Symbol) -> sp.Expr:
    expanded = sp.trigsimp(
        sp.expand_trig(sp.trigsimp(sp.expand_complex(density), method="fu")),
        method="fu",
    )
    result = sp.factor(2 * sp.pi * sp.integrate(expanded, (theta, 0, sp.pi)))
    _require(not result.has(theta), "theta survived homogeneous sphere integration")
    return result


def _direct_fixture() -> dict[str, Any]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    first = sp.symbols("a1 b1 c1 d1 e1 w1", real=True)
    second = sp.symbols("a2 b2 c2 d2 e2 w2", real=True)
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    density = weyl_maxwell_current_time(
        metric,
        field,
        _ell0_variation(first, time, sine),
        _ell0_variation(second, time, sine),
        coordinates,
        sp.Integer(3),
    )
    integrated = _integrate_sphere(density, theta)
    expected = -2 * sp.pi * (
        2 * first[0] * second[1]
        - first[0] * second[3]
        - 2 * second[0] * first[1]
        + second[0] * first[3]
        + first[1] * second[2]
        - second[1] * first[2]
        - 2 * first[4] * second[5]
        + 2 * second[4] * first[5]
    )
    _require(sp.simplify(integrated - expected) == 0, "homogeneous target current changed")
    matrix = sp.Matrix(
        6,
        6,
        lambda row, column: sp.diff(
            sp.diff(integrated, first[row]), second[column]
        ),
    )
    _require(matrix == -matrix.T, "homogeneous current matrix is not antisymmetric")
    _require(matrix.rank() == 6, "homogeneous target current lost rank")
    _require(sp.factor(matrix.det()) == 256 * sp.pi**6, "homogeneous determinant changed")
    _require(sp.diff(integrated, time) == 0, "homogeneous target current is time dependent")
    return {
        "parameter_order": ["a", "b", "c", "d", "Q_e", "W_x"],
        "representative": [
            "K=a+b*t",
            "C=a*t^2+(b/3)*t^3+c+d*t",
            "A_x=W_x+Q_e*t",
        ],
        "integrated_coordinate_current_per_unit_x": str(integrated),
        "coordinate_current_matrix": [
            [str(matrix[row, column]) for column in range(6)] for row in range(6)
        ],
        "time_derivative": "0",
        "matrix_rank": 6,
        "matrix_determinant": "256*pi**6",
        "fixed_bundle_scope": "uniform magnetic variation is excluded; W_x is the flat S1 holonomy coordinate",
    }


def build_fixture() -> dict[str, Any]:
    return {
        "schema": "weyl-maxwell-homogeneous-global-lee-wald-fixture-v1",
        "result_id": "WEYL_MAXWELL_HOMOGENEOUS_GLOBAL_LEE_WALD_FIXTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "six-dimensional generalized homogeneous Einstein-Maxwell solution block on R_t x S1_L x S2 at fixed magnetic bundle, before final residual quotient",
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
        _require(stored == fixture, f"stale homogeneous fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

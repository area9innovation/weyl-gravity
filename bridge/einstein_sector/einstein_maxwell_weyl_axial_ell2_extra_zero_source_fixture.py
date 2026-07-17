"""Direct four-dimensional zero-frequency sources for both axial extra modes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _average,
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell2_extra_zero_source_fixture.schema.json"
HELPER_PATH = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py"
OUTPUTS = {
    "e1_self": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_e1_zero_source_fixture.json",
    "e1_e2": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_e1_e2_zero_source_fixture.json",
}


class ExtraZeroSourceFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtraZeroSourceFixtureError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _geometry(
    left: tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr],
    right: tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr],
) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    u, v = sp.symbols("u v")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    frequency = 4 / sp.sqrt(3)
    left_wave = sp.exp(-sp.I * frequency * time)
    right_wave = sp.exp(sp.I * frequency * time)
    ht = u * left[0] * left_wave + v * right[0] * right_wave
    hx = u * left[1] * left_wave + v * right[1] * right_wave
    qt = u * left[2] * left_wave + v * right[2] * right_wave
    qx = u * left[3] * left_wave + v * right[3] * right_wave
    tr = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 3] = metric[3, 0] = epsilon * ht * axial_one_form
    metric[1, 3] = metric[3, 1] = epsilon * hx * axial_one_form
    inverse = metric.inv().applyfunc(tr)
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
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
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(qx, time) * harmonic
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * qt * sp.diff(harmonic, theta)
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * qx * sp.diff(harmonic, theta)
    field[2, 1] = -field[1, 2]
    return {
        "epsilon": epsilon,
        "amplitudes": (u, v),
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }


def _source(case: str) -> list[sp.Expr]:
    root = sp.sqrt(3)
    e1 = (-6, 0, 6, 0)
    e2 = (0, -sp.Rational(2, 3), 0, 6)
    left, right = (e1, e1) if case == "e1_self" else (e1, e2)
    geometry = _geometry(left, right)
    data = _curvature(geometry, 2)
    metric_equations, maxwell_equations = _equations(
        data, 2, ((0, 0), (1, 1), (2, 2), (3, 3))
    )
    epsilon = geometry["epsilon"]
    u, v = geometry["amplitudes"]
    time, _, theta, _ = geometry["coordinates"]
    sphere_trace = (
        metric_equations[(2, 2)]
        + metric_equations[(3, 3)] / sp.sin(theta) ** 2
    ) / 2
    rows = [
        metric_equations[(0, 0)],
        metric_equations[(1, 1)],
        sphere_trace,
        maxwell_equations[1],
    ]
    source = []
    for row in rows:
        mixed = sp.diff(sp.diff(sp.diff(row, epsilon, 2) / 2, u), v).subs(
            {epsilon: 0, time: 0}
        )
        source.append(_canonical(sp.Rational(1, 4) * _average(mixed, theta)))
    if case == "e1_self":
        _require(source[0] == -sp.Rational(1728, 5), "e1 Taub normalization changed")
    else:
        _require(source[0] == 0, "orthogonal extra modes acquired H interference")
    return source


def build_fixture(case: str) -> dict[str, Any]:
    source = _source(case)
    return {
        "schema": "einstein-maxwell-weyl-axial-ell2-extra-zero-source-fixture-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": f"EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_{case.upper()}_ZERO_SOURCE_FIXTURE",
        "result_state": "DIRECT_FOUR_DIMENSIONAL_ZERO_FREQUENCY_SOURCE_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_ELL2_M0_K0_AXIAL_EXTRA_FIXTURE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(HELPER_PATH.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(HELPER_PATH),
        },
        "domain": "direct four-dimensional Weyl-Maxwell quadratic source on the axial ell=2,m=0,k=0 extra p-primary shell",
        "case": case,
        "frequency_squared": "16/3",
        "representatives_Ht_Hx_Qt_Qx": {
            "e1": ["-6", "0", "6", "0"],
            "e2": ["0", "-2/3", "0", "6"],
        },
        "real_channel_factor": "1/4",
        "homogeneous_source_rows_E00_E11_E22_Maxwell1": [str(value) for value in source],
        "claim_boundary": "This is a direct axisymmetric ell=2 zero-frequency source fixture. It does not by itself classify the Hermitian source rank, all m, the polar parity, general ell, or nonzero momentum.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(OUTPUTS), required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = build_fixture(args.case)
    if args.write:
        OUTPUTS[args.case].write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if args.verify:
        _require(json.loads(args.verify.read_text()) == payload, f"stale fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

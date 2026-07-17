"""Direct four-dimensional axial ell=3,k=0 zero-frequency source fixtures."""

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
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell3_zero_source_fixture.schema.json"
HELPER_PATH = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py"
CASES = ("plus", "minus", "extra_e1", "extra_e2", "extra_cross")
OUTPUTS = {case: ROOT / f"bridge/certificates/einstein_maxwell_weyl_axial_ell3_{case}_zero_source_fixture.json" for case in CASES}


class AxialEll3ZeroSourceFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialEll3ZeroSourceFixtureError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _modes() -> dict[str, tuple[tuple[sp.Expr, ...], sp.Expr]]:
    lam = sp.Integer(12)
    root = sp.sqrt(2 * lam)
    return {
        "plus": ((0, 1, 0, sp.sqrt(lam / 2)), sp.sqrt(lam + root)),
        "minus": ((0, 1, 0, -sp.sqrt(lam / 2)), sp.sqrt(lam - root)),
        "extra_e1": ((-lam, 0, lam, 0), sp.sqrt(lam - sp.Rational(2, 3))),
        "extra_e2": ((0, -sp.Rational(2, 3), 0, lam), sp.sqrt(lam - sp.Rational(2, 3))),
    }


def _geometry(left_name: str, right_name: str) -> dict[str, object]:
    modes = _modes()
    left, left_frequency = modes[left_name]
    right, right_frequency = modes[right_name]
    _require(sp.simplify(left_frequency**2 - right_frequency**2) == 0, "zero source requires a common shell")
    epsilon = sp.symbols("epsilon")
    u, v = sp.symbols("u v")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.legendre(3, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    left_wave = sp.exp(-sp.I * left_frequency * time)
    right_wave = sp.exp(sp.I * right_frequency * time)
    ht = u * left[0] * left_wave + v * right[0] * right_wave
    hx = u * left[1] * left_wave + v * right[1] * right_wave
    qt = u * left[2] * left_wave + v * right[2] * right_wave
    qx = u * left[3] * left_wave + v * right[3] * right_wave
    tr = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 3] = metric[3, 0] = epsilon * ht * axial_one_form
    metric[1, 3] = metric[3, 1] = epsilon * hx * axial_one_form
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
    left_name, right_name = ("extra_e1", "extra_e2") if case == "extra_cross" else (case, case)
    geometry = _geometry(left_name, right_name)
    data = _curvature(geometry, 2)
    metric_equations, maxwell_equations = _equations(data, 2, ((0, 0), (1, 1), (2, 2), (3, 3)))
    epsilon = geometry["epsilon"]
    u, v = geometry["amplitudes"]
    time, _, theta, _ = geometry["coordinates"]
    sphere_trace = (metric_equations[(2, 2)] + metric_equations[(3, 3)] / sp.sin(theta) ** 2) / 2
    rows = [metric_equations[(0, 0)], metric_equations[(1, 1)], sphere_trace, maxwell_equations[1]]
    source = []
    for row in rows:
        mixed = sp.diff(sp.diff(sp.diff(row, epsilon, 2) / 2, u), v).subs({epsilon: 0, time: 0})
        source.append(_canonical(sp.Rational(1, 4) * _average(mixed, theta)))
    return source


def build_fixture(case: str) -> dict[str, Any]:
    source = _source(case)
    return {
        "schema": "einstein-maxwell-weyl-axial-ell3-zero-source-fixture-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": f"EINSTEIN_MAXWELL_WEYL_AXIAL_ELL3_{case.upper()}_ZERO_SOURCE_FIXTURE",
        "result_state": "DIRECT_FOUR_DIMENSIONAL_ZERO_FREQUENCY_SOURCE_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_AXIAL_ELL3_M0_K0_FIXTURE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(HELPER_PATH.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(HELPER_PATH),
        },
        "domain": "direct four-dimensional homogeneous zero-frequency quadratic source for axial ell=3,m=0,k=0 Weyl-Maxwell modes",
        "case": case,
        "mode_table_Ht_Hx_Qt_Qx_and_frequency": {
            name: {"representative": [str(value) for value in mode], "frequency": str(frequency)}
            for name, (mode, frequency) in _modes().items()
        },
        "real_channel_factor": "1/4",
        "homogeneous_source_rows_E00_E11_E22_Maxwell1": [str(value) for value in source],
        "classification": {
            "zero_frequency_source_relation_assumed": False,
            "direct_tensor_replay_required_for_each_declared_case": True,
        },
        "claim_boundary": "This is a direct axial ell=3 axisymmetric source fixture. It does not by itself promote all m, polar parity, symbolic ell, or the complete second-order cone.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = build_fixture(args.case)
    if args.write:
        OUTPUTS[args.case].write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        _require(json.loads(args.verify.read_text()) == payload, f"stale fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()

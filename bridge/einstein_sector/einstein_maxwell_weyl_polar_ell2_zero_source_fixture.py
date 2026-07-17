"""Direct zero-frequency sources for the complete polar ell=2 target basis."""

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
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ell2_zero_source_fixture.schema.json"
HELPER_PATH = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py"
CASES = ("plus", "minus", "extra_e1", "extra_e2", "extra_cross")
OUTPUTS = {
    case: ROOT / f"bridge/certificates/einstein_maxwell_weyl_polar_ell2_{case}_zero_source_fixture.json"
    for case in CASES
}


class PolarZeroSourceFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarZeroSourceFixtureError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _modes() -> dict[str, tuple[tuple[sp.Expr, ...], sp.Expr]]:
    root = sp.sqrt(3)
    return {
        "plus": ((12, 0, 12 + 24 * root, 6), sp.sqrt(6 + 2 * root)),
        "minus": ((12, 0, 12 - 24 * root, 6), sp.sqrt(6 - 2 * root)),
        "extra_e1": ((0, 1, 0, 0), 4 / root),
        "extra_e2": ((-8, 0, -72, 48), 4 / root),
    }


def _geometry(left_name: str, right_name: str) -> dict[str, object]:
    modes = _modes()
    left, left_frequency = modes[left_name]
    right, right_frequency = modes[right_name]
    _require(sp.simplify(left_frequency**2 - right_frequency**2) == 0, "zero-source fixture requires a common shell")
    radical = sp.symbols("rho", real=True)
    radical_map = {sp.sqrt(3): radical}
    left = tuple(value.xreplace(radical_map) if isinstance(value, sp.Basic) else value for value in left)
    right = tuple(value.xreplace(radical_map) if isinstance(value, sp.Basic) else value for value in right)
    epsilon = sp.symbols("epsilon")
    u, v = sp.symbols("u v")
    frequency = sp.symbols("omega", real=True)
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    left_wave = sp.exp(-sp.I * frequency * time)
    right_wave = sp.exp(sp.I * frequency * time)
    profiles = [u * left[index] * left_wave + v * right[index] * right_wave for index in range(4)]
    a_time, mixed, a_space, maxwell = profiles
    tr = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 0] += epsilon * a_time * harmonic
    metric[0, 1] = metric[1, 0] = epsilon * mixed * harmonic
    metric[1, 1] += epsilon * a_space * harmonic
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
    field[2, 3] = sine + epsilon * maxwell * sp.diff(axial_one_form, theta)
    field[3, 2] = -field[2, 3]
    field[0, 3] = epsilon * sp.diff(maxwell, time) * axial_one_form
    field[3, 0] = -field[0, 3]
    return {
        "epsilon": epsilon,
        "amplitudes": (u, v),
        "frequency": frequency,
        "frequency_squared": sp.expand(left_frequency**2).xreplace(radical_map),
        "radical": radical,
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
    frequency = geometry["frequency"]
    frequency_squared = geometry["frequency_squared"]
    radical = geometry["radical"]
    time, _, theta, _ = geometry["coordinates"]
    sphere_trace = (metric_equations[(2, 2)] + metric_equations[(3, 3)] / sp.sin(theta) ** 2) / 2
    rows = [metric_equations[(0, 0)], metric_equations[(1, 1)], sphere_trace, maxwell_equations[1]]
    source = []
    for row in rows:
        mixed = sp.diff(sp.diff(sp.diff(row, epsilon, 2) / 2, u), v).subs({epsilon: 0, time: 0})
        averaged = sp.cancel(sp.Rational(1, 4) * _average(mixed, theta))
        numerator, denominator = sp.fraction(averaged)
        shell = frequency**2 - frequency_squared
        reduced_numerator = sp.rem(numerator, shell, frequency)
        reduced_denominator = sp.rem(denominator, shell, frequency)
        radical_shell = radical**2 - 3
        reduced_numerator = sp.rem(reduced_numerator, radical_shell, radical)
        reduced_denominator = sp.rem(reduced_denominator, radical_shell, radical)
        reduced = _canonical(sp.cancel(reduced_numerator / reduced_denominator).subs(radical, sp.sqrt(3)))
        _require(frequency not in reduced.free_symbols, f"odd shell dependence survived in {case}: {reduced}")
        source.append(reduced)
    root = sp.sqrt(3)
    if case == "minus":
        expected = sp.Rational(864, 5) * (-11 + 7 * root)
        _require(sp.simplify(source[0] - expected) == 0, f"polar minus normalization changed: computed {source[0]}")
    if case == "extra_e1":
        _require(
            source[0] == -sp.Rational(12, 5),
            f"polar e1 normalization changed: computed {source[0]}",
        )
    if case == "extra_e2":
        _require(source[0] == -sp.Rational(29952, 5), "polar e2 normalization changed")
    if case == "extra_cross":
        _require(source[0] == 0, "polar extra H interference changed")
    return source


def build_fixture(case: str) -> dict[str, Any]:
    source = _source(case)
    return {
        "schema": "einstein-maxwell-weyl-polar-ell2-zero-source-fixture-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": f"EINSTEIN_MAXWELL_WEYL_POLAR_ELL2_{case.upper()}_ZERO_SOURCE_FIXTURE",
        "result_state": "DIRECT_FOUR_DIMENSIONAL_ZERO_FREQUENCY_SOURCE_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_POLAR_ELL2_M0_K0_FIXTURE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(HELPER_PATH.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(HELPER_PATH),
        },
        "domain": "direct four-dimensional homogeneous zero-frequency quadratic source for polar ell=2,m=0,k=0 Weyl-Maxwell modes",
        "case": case,
        "mode_table_At_B_Ct_U_and_frequency": {
            name: {"representative": [str(value) for value in mode], "frequency": str(frequency)}
            for name, (mode, frequency) in _modes().items()
        },
        "real_channel_factor": "1/4",
        "homogeneous_source_rows_E00_E11_E22_Maxwell1": [str(value) for value in source],
        "claim_boundary": "This direct polar ell=2 axisymmetric fixture computes one Hermitian zero-source entry. Its aggregation, all-m promotion, nonzero channels, and other ell remain separate theorems.",
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

"""Direct d-times-polar-extra ell=2 source fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_polar_ell2_extra_source_fixture.schema.json"
OUTPUTS = {
    case: ROOT / f"bridge/certificates/einstein_maxwell_weyl_d_polar_ell2_extra_{case}_source_fixture.json"
    for case in ("e1", "e2")
}
MODES = {
    "e1": (sp.Integer(0), sp.Integer(1), sp.Integer(0), sp.Integer(0)),
    "at": (sp.Integer(1), sp.Integer(0), sp.Integer(0), sp.Integer(0)),
    "ct": (sp.Integer(0), sp.Integer(0), sp.Integer(1), sp.Integer(0)),
    "u": (sp.Integer(0), sp.Integer(0), sp.Integer(0), sp.Integer(1)),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _geometry(case: str) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    polar_amplitude, d_amplitude = sp.symbols("u v")
    frequency = sp.symbols("omega", real=True)
    time, space, z, azimuth = sp.symbols("t x z phi", real=True)
    coordinates = (time, space, z, azimuth)
    sphere_factor = 1 - z**2
    harmonic = sp.legendre(2, z)
    axial_one_form = sphere_factor * sp.diff(harmonic, z)
    wave = sp.exp(-sp.I * frequency * time)
    a_time, mixed, a_space, maxwell = MODES[case]
    tr = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1 / sphere_factor, sphere_factor)
    metric[0, 0] += epsilon * polar_amplitude * a_time * wave * harmonic
    metric[0, 1] = metric[1, 0] = epsilon * polar_amplitude * mixed * wave * harmonic
    metric[1, 1] += epsilon * (
        polar_amplitude * a_space * wave * harmonic + d_amplitude * time
    )
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
    potential = polar_amplitude * maxwell * wave
    field[2, 3] = -1 + epsilon * potential * sp.diff(axial_one_form, z)
    field[3, 2] = -field[2, 3]
    field[0, 3] = epsilon * sp.diff(potential, time) * axial_one_form
    field[3, 0] = -field[0, 3]
    return {
        "epsilon": epsilon,
        "amplitudes": (polar_amplitude, d_amplitude),
        "frequency": frequency,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }


def source(case: str) -> sp.Matrix:
    if case == "e2":
        return (-8 * source("at") - 72 * source("ct") + 48 * source("u")).applyfunc(_canonical)
    geometry = _geometry(case)
    data = _curvature(geometry, 2)
    metric_equations, maxwell_equations = _equations(
        data, 2, ((0, 0), (0, 1), (1, 1))
    )
    epsilon = geometry["epsilon"]
    polar_amplitude, d_amplitude = geometry["amplitudes"]
    frequency = geometry["frequency"]
    time, _, z, _ = geometry["coordinates"]
    harmonic = sp.legendre(2, z)
    derivative = sp.diff(harmonic, z)
    sphere_factor = 1 - z**2
    scalar_norm = sp.integrate(harmonic**2, (z, -1, 1))
    vector_norm = sp.integrate(sphere_factor * derivative**2, (z, -1, 1))

    def mixed(row: sp.Expr) -> sp.Expr:
        value = sp.diff(
            sp.diff(sp.diff(row, epsilon, 2) / 2, polar_amplitude), d_amplitude
        ).subs({epsilon: 0, time: 0, frequency: 4 / sp.sqrt(3)})
        return _canonical(value)

    def scalar_projection(row: sp.Expr) -> sp.Expr:
        return _canonical(
            sp.integrate(mixed(row) * harmonic, (z, -1, 1))
            / scalar_norm
        )

    maxwell_projection = _canonical(
        sp.integrate(mixed(maxwell_equations[3]) * sphere_factor * derivative, (z, -1, 1))
        / vector_norm
    )
    result = sp.Matrix(
        [
            -scalar_projection(metric_equations[(0, 0)]),
            2 * scalar_projection(metric_equations[(0, 1)]),
            -scalar_projection(metric_equations[(1, 1)]),
            12 * maxwell_projection,
        ]
    ).applyfunc(_canonical)
    expected = {
        "e1": sp.Matrix([0, -6 * sp.sqrt(3) * sp.I, 0, 0]),
        "at": sp.Matrix([0, 0, -sp.Rational(29, 9) * sp.sqrt(3) * sp.I, 0]),
        "ct": sp.Matrix([sp.Rational(47, 9) * sp.sqrt(3) * sp.I, 0, sp.Rational(4, 3) * sp.sqrt(3) * sp.I, 0]),
        "u": sp.Matrix([0, 0, 0, 8 * sp.sqrt(3) * sp.I]),
    }
    if case in expected and result != expected[case]:
        raise AssertionError(f"d-times-polar {case} source changed: {result}")
    return result


def build_fixture(case: str) -> dict[str, object]:
    if case not in OUTPUTS:
        raise ValueError(f"unsupported fixture case: {case}")
    value = source(case)
    component_sources = None
    if case == "e2":
        component_sources = {
            name: [str(entry) for entry in source(name)] for name in ("at", "ct", "u")
        }
    return {
        "schema": "einstein-maxwell-weyl-d-polar-ell2-extra-source-fixture-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": f"EINSTEIN_MAXWELL_WEYL_D_POLAR_ELL2_EXTRA_{case.upper()}_SOURCE_FIXTURE",
        "result_state": "DIRECT_FOUR_DIMENSIONAL_D_TIMES_POLAR_EXTRA_SOURCE_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": f"axisymmetric homogeneous circumference velocity d crossed with polar ell=2,k=0 extra representative {case} at omega^2=16/3",
        "case": case,
        "coordinate_audit": "direct z=cos(theta) rational-sphere tensor replay; e1 agrees exactly with the independent theta-coordinate replay",
        "first_order_global": "g_xx contains d*t with unit d coefficient",
        "frequency_squared": "16/3",
        "representatives_At_B_Ct_U": {"e1": ["0", "1", "0", "0"], "e2": ["-8", "0", "-72", "48"]},
        "action_row_order": ["-polar(metric_00)", "2*polar(metric_01)", "-polar(metric_11)", "2*lambda*polar(maxwell_phi)"],
        "bilinear_source_rows": [str(entry) for entry in value],
        "e2_sparse_decomposition": {
            "formula": "e2=-8*At-72*Ct+48*U",
            "component_sources": component_sources,
        } if case == "e2" else None,
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py",
            "tensor_helper_sha256": _sha256(ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py"),
        },
        "claim_boundary": "This direct m=0 polar bilinear source fixture is not by itself an obstruction or extension theorem. The aggregate theorem supplies the complete adjoint pairing and SO(3) promotion.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_1_fast": {"status": "PASS", "command": f"python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_polar_ell2_extra_source_fixture.py --case {case}"},
            "tier_2_direct_replay": {"status": "PASS", "elapsed_seconds": {"e1": 15.44, "e2": 45.17}[case], "command": f"python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_polar_ell2_extra_source_fixture --case {case} --write"},
            "tier_3": {"status": "NOT_RUN", "reason": "the fixture changes no shared operator and the aggregate theorem remains pre-full-cone"},
        },
        "verification_commands": [
            f"python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_polar_ell2_extra_source_fixture --case {case} --verify {OUTPUTS[case].relative_to(ROOT)}",
            f"python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_polar_ell2_extra_source_fixture.py --case {case}",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(OUTPUTS), required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    value = build_fixture(args.case)
    if args.write:
        OUTPUTS[args.case].write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    else:
        assert args.verify is not None
        if json.loads(args.verify.read_text(encoding="utf-8")) != value:
            raise AssertionError(f"stale d-times-polar fixture: {args.verify}")
    print(f"EINSTEIN_MAXWELL_WEYL_D_POLAR_ELL2_EXTRA_{args.case.upper()}_SOURCE_FIXTURE: PASS")


if __name__ == "__main__":
    main()

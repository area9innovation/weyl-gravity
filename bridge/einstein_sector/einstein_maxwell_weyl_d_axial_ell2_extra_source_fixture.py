"""Direct d-times-axial-extra sources on the ell=2 p shell."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import _canonical, _curvature, _equations, _trunc


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_axial_ell2_extra_source_fixture.schema.json"
HELPER_PATH = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py"
OUTPUTS = {
    "e1": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_e1_source_fixture.json",
    "e2": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_e2_source_fixture.json",
}


class DSourceFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DSourceFixtureError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _separate(expression: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.trigsimp(sp.expand_trig(expression), method="fu")))


def _direct_source(case: str) -> list[sp.Expr]:
    epsilon = sp.symbols("epsilon")
    global_amplitude, wave_amplitude = sp.symbols("u v")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.legendre(2, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)
    frequency = 4 / sp.sqrt(3)
    wave = sp.exp(-sp.I * frequency * time)
    representatives = {
        "e1": (-6, 0, 6, 0),
        "e2": (0, -sp.Rational(2, 3), 0, 6),
    }
    h_time, h_space, q_time, q_space = [wave_amplitude * value * wave for value in representatives[case]]
    background_metric = sp.diag(-1, 1, 1, sine**2)
    perturbation = sp.zeros(4)
    perturbation[1, 1] = global_amplitude * time
    perturbation[0, 3] = perturbation[3, 0] = h_time * axial_one_form
    perturbation[1, 3] = perturbation[3, 1] = h_space * axial_one_form
    metric = background_metric + epsilon * perturbation
    tr = lambda expression: _trunc(expression, epsilon, 2)
    background_inverse = sp.diag(-1, 1, 1, sine**-2)
    inverse = (
        background_inverse
        - epsilon * background_inverse * perturbation * background_inverse
        + epsilon**2 * background_inverse * perturbation * background_inverse * perturbation * background_inverse
    ).applyfunc(sp.expand)
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = tr(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2
                )
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * (sp.diff(q_space, time) * harmonic)
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * q_time * sp.diff(harmonic, theta)
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * q_space * sp.diff(harmonic, theta)
    field[2, 1] = -field[1, 2]
    data = _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        2,
    )
    metric_equations, maxwell_equations = _equations(data, 2, ((0, 3), (1, 3)))
    action_rows = [
        6 * metric_equations[(0, 3)] / axial_one_form,
        -6 * metric_equations[(1, 3)] / axial_one_form,
        maxwell_equations[0] / harmonic,
        maxwell_equations[1] / harmonic,
    ]
    source = []
    for row in action_rows:
        mixed = (
            sp.diff(sp.diff(sp.diff(row, epsilon, 2) / 2, global_amplitude), wave_amplitude)
            .subs(epsilon, 0)
            / wave
        )
        source.append(_separate(_canonical(mixed)))
    expected = {
        "e1": [-72 * sp.sqrt(3) * sp.I, 0, 0, 0],
        "e2": [0, -4 * sp.sqrt(3) * sp.I / 3, 0, -4 * sp.sqrt(3) * sp.I],
    }
    _require([sp.factor(source[index] - expected[case][index]) for index in range(4)] == [0] * 4, f"d-times-{case} source changed")
    return source


def build_fixture(case: str) -> dict[str, object]:
    source = _direct_source(case)
    elapsed = {"e1": 27.87, "e2": 85.89}[case]
    return {
        "schema": "einstein-maxwell-weyl-d-axial-ell2-extra-source-fixture-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": f"EINSTEIN_MAXWELL_WEYL_D_AXIAL_ELL2_EXTRA_{case.upper()}_SOURCE_FIXTURE",
        "result_state": "DIRECT_FOUR_DIMENSIONAL_D_TIMES_AXIAL_EXTRA_SOURCE_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": f"axisymmetric homogeneous d direction crossed with axial ell=2,k=0 extra representative {case} at omega^2=16/3",
        "case": case,
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(HELPER_PATH.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(HELPER_PATH),
            "method": "direct four-dimensional bivariate coefficient of the Weyl-Maxwell Euler operator",
        },
        "first_order_global": "C=d*t with unit d coefficient",
        "frequency_squared": "16/3",
        "representatives_Ht_Hx_Qt_Qx": {
            "e1": ["-6", "0", "6", "0"],
            "e2": ["0", "-2/3", "0", "6"],
        },
        "action_row_order": ["6*metric_t", "-6*metric_x", "maxwell_t", "maxwell_x"],
        "bilinear_source_rows": [str(sp.factor(value)) for value in source],
        "claim_boundary": "This is one direct m=0 axial bilinear source fixture. The aggregate theorem performs the adjoint pairing and SO(3) promotion; polar sources and the rest of the global block are separate.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1_fast": {"status": "PASS", "commands": [f"python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_axial_ell2_extra_source_fixture.py --case {case}"]},
            "tier_2_direct_four_dimensional_replay": {
                "status": "PASS",
                "elapsed_seconds": elapsed,
                "command": f"python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_axial_ell2_extra_source_fixture --case {case} --write",
                "criterion": "the direct bivariate four-dimensional Euler coefficient is the mathematical input; e2 is retained as an explicit expensive rail because its exact replay exceeds the fast-loop target",
            },
            "tier_3": {"status": "NOT_RUN", "reason": "the aggregate axial theorem does not freeze the polar or full global cone"},
        },
        "verification_commands": [
            f"python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_axial_ell2_extra_source_fixture --case {case} --write",
            f"python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_axial_ell2_extra_source_fixture.py --case {case}",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(OUTPUTS), required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_fixture(arguments.case)
    if arguments.write:
        OUTPUTS[arguments.case].write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, f"stale d-times-{arguments.case} source fixture")


if __name__ == "__main__":
    main()

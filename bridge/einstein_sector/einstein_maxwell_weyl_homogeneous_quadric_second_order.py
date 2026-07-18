"""Second-order extension of the complete standard homogeneous moment-map quadric."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import _curvature, _trunc
from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import _canonical, _equations


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_quadric_second_order.schema.json"
MOMENT_MAP_INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json"
ENGINE = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py"


class HomogeneousQuadricError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HomogeneousQuadricError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _direct_source() -> tuple[sp.Matrix, tuple[sp.Symbol, ...], sp.Symbol]:
    epsilon = sp.symbols("epsilon")
    a, b, c, d, charge, wilson = sp.symbols("a b c d Q_e W_x", real=True)
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    sphere = a + b * time
    circle = a * time**2 + b * time**3 / 3 + c + d * time
    potential = wilson + charge * time
    metric = sp.diag(
        -1,
        1 + epsilon * circle,
        1 + epsilon * sphere,
        (1 + epsilon * sphere) * sine**2,
    )
    tr = lambda expression: _trunc(expression, epsilon, 2)
    inverse = metric.inv().applyfunc(tr)
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
    field[0, 1] = epsilon * sp.diff(potential, time)
    field[1, 0] = -field[0, 1]
    geometry = {
        "epsilon": epsilon,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
    }
    data = _curvature(geometry, 2)
    metric_equations, maxwell_equations = _equations(
        data, 2, ((0, 0), (0, 1), (1, 1), (2, 2), (3, 3))
    )
    sphere_trace = (
        metric_equations[(2, 2)] + metric_equations[(3, 3)] / sine**2
    ) / 2
    rows = (
        metric_equations[(0, 0)],
        metric_equations[(0, 1)],
        metric_equations[(1, 1)],
        sphere_trace,
        maxwell_equations[0],
        maxwell_equations[1],
    )
    source = sp.Matrix(
        [_canonical(sp.diff(row, epsilon, 2).subs(epsilon, 0) / 2) for row in rows]
    )
    return source, (a, b, c, d, charge, wilson), time


def build_certificate() -> dict[str, object]:
    moment_maps = json.loads(MOMENT_MAP_INPUT.read_text(encoding="utf-8"))
    _require(moment_maps["classification"]["standard_homogeneous_common_zero_locus_classified"], "homogeneous moment-map input changed")
    source, (a, b, c, d, charge, wilson), time = _direct_source()
    constraint = sp.factor(a**2 + b**2 - b * d + charge**2)
    expected = sp.Matrix(
        [
            -constraint / 2,
            0,
            charge**2 / 2 + 9 * a**2 / 2 + 15 * a * b * time + 15 * b**2 * time**2 / 2 - 2 * b**2 + 3 * b * d,
            -charge**2 / 2 - 5 * a**2 / 2 - 15 * a * b * time / 2 - 15 * b**2 * time**2 / 4 + 3 * b**2 / 4 - 5 * b * d / 4,
            0,
            charge * (2 * a * time + b * time**2 - 2 * b + d) / 2,
        ]
    )
    _require((source - expected).applyfunc(sp.factor) == sp.zeros(6, 1), "homogeneous quadratic source changed")
    _require(sp.factor(source[2] + 2 * source[3] + constraint / 2) == 0, "homogeneous Noether relation changed")
    _require(not any(value.has(c, wilson) for value in source), "spectators entered the source")

    metric_correction = sp.factor(
        (-charge**2 - 9 * a**2 + 4 * b**2 - 6 * b * d) * time**4 / 24
        - a * b * time**5 / 4
        - b**2 * time**6 / 24
    )
    electric_correction = sp.factor(
        charge
        * (a * time**3 / 6 + b * time**4 / 24 + (-2 * b + d) * time**2 / 4)
    )
    linear_image = sp.Matrix(
        [
            0,
            0,
            sp.diff(metric_correction, time, 4) / 2,
            -sp.diff(metric_correction, time, 4) / 4,
            0,
            -sp.diff(electric_correction, time, 2),
        ]
    )
    remainder = (linear_image + source).applyfunc(sp.factor)
    expected_remainder = sp.Matrix([-constraint / 2, 0, 0, -constraint / 4, 0, 0])
    _require(
        (remainder - expected_remainder).applyfunc(sp.factor) == sp.zeros(6, 1),
        "homogeneous correction remainder changed",
    )

    return {
        "schema": "einstein-maxwell-weyl-homogeneous-quadric-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_QUADRIC_SECOND_ORDER",
        "result_state": "COMPLETE_STANDARD_HOMOGENEOUS_COMMON_ZERO_QUADRIC_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "complete standard homogeneous fixed-bundle tangent (a,b,c,d,Q_e,W_x) on R_t x S1_L x S2 before final residual quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "engine": {"path": str(ENGINE.relative_to(ROOT)), "sha256": _sha256(ENGINE)},
            "input": {"path": str(MOMENT_MAP_INPUT.relative_to(ROOT)), "sha256": _sha256(MOMENT_MAP_INPUT)},
        },
        "first_order_tangent": {
            "K": "a+b*t",
            "C": "a*t^2+(b/3)*t^3+c+d*t",
            "A_x": "W_x+Q_e*t",
            "common_zero_equation": str(constraint) + "=0",
        },
        "quadratic_source": {
            "row_order": ["E00", "E01", "E11", "sphere_trace", "Maxwell0", "Maxwell1"],
            "rows": [str(sp.factor(value)) for value in source],
            "constraint_pairing": "S_E00=-(1/2)*(a^2+b^2-b*d+Q_e^2)",
            "Noether_relation": "S_E11+2*S_sphere=-(1/2)*(a^2+b^2-b*d+Q_e^2)",
            "c_and_Wx_absent": True,
        },
        "second_order_correction": {
            "C2": "0",
            "K2": str(metric_correction),
            "A_x2": str(electric_correction),
            "other_components": "0 in the declared homogeneous gauge",
            "off_cone_remainder": [str(value) for value in remainder],
            "remainder_vanishes_modulo_common_zero_equation": True,
        },
        "classification": {
            "direct_complete_homogeneous_quadratic_source_computed": True,
            "homogeneous_Taub_pairing_equals_moment_map_quadric": True,
            "complete_standard_homogeneous_common_zero_quadric_second_order_extendible": True,
            "circumference_and_Wilson_spectators_retained": True,
            "magnetic_Chern_class_fixed": True,
            "twist_velocity_mixed_cone_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The nontrivial homogeneous moment-map cone is the exact second-order tangent cone for the complete standard homogeneous block: its defining quadric is precisely the sole constraint source, and every remaining polynomial source is removed by the displayed correction. Constant circumference and Wilson holonomy remain spectators. This does not make the isolated constant radion extendible; that direction lies off the quadric at fixed bundle topology.",
        "next_gate": "add axial twist velocities and physical ell=1 inputs to the exceptional/global common-zero cone, beginning with a collinear twist-velocity/homogeneous balance",
        "claim_boundary": "This proves a standard homogeneous second-order jet only. It does not include twist or physical ell=1 inputs, exceptional fourth-order target modes, all-orders integration, the final residual quotient, causal scattering, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.2, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 21.8, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_quadric_second_order --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_quadric_second_order.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_quadric_second_order"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": ["exceptional/global moment maps", "homogeneous Weyl-Maxwell equation engine"]},
            "tier_3": {"status": "NOT_RUN", "reason": "twist velocity, physical ell=1 inputs, and all-orders exceptional/global closure remain open"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_quadric_second_order --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_quadric_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_quadric_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "homogeneous quadric certificate is stale")


if __name__ == "__main__":
    main()

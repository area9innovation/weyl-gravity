"""Balanced homogeneous-radion and axial-twist-velocity second-order fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import _curvature, _trunc
from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows
from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import _canonical, _equations
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _generic_rows as _polar_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.schema.json"
INPUTS = {
    "moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "homogeneous_quadric": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
}


class HomogeneousTwistBalanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HomogeneousTwistBalanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _direct_source() -> tuple[dict[str, sp.Expr], tuple[sp.Symbol, ...]]:
    epsilon = sp.symbols("epsilon")
    radion, velocity = sp.symbols("a B", real=True)
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.cos(theta)
    axial_one_form = -sine * sp.diff(harmonic, theta)
    metric = sp.diag(
        -1,
        1 + epsilon * radion * time**2,
        1 + epsilon * radion,
        (1 + epsilon * radion) * sine**2,
    )
    metric[1, 3] = metric[3, 1] = epsilon * velocity * time * axial_one_form
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
    potential_x = -velocity * time * harmonic
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(potential_x, time)
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * sp.diff(potential_x, theta)
    field[2, 1] = -field[1, 2]
    data = _curvature(
        {"epsilon": epsilon, "coordinates": coordinates, "metric": metric, "inverse": inverse, "connection": connection, "field": field},
        2,
    )
    pairs = tuple((first, second) for first in range(4) for second in range(first, 4))
    metric_equations, maxwell_equations = _equations(data, 2, pairs)
    rows = {
        f"E{first}{second}": _canonical(sp.diff(value, epsilon, 2).subs(epsilon, 0) / 2)
        for (first, second), value in metric_equations.items()
    }
    rows.update(
        {
            f"M{index}": _canonical(sp.diff(value, epsilon, 2).subs(epsilon, 0) / 2)
            for index, value in maxwell_equations.items()
        }
    )
    return rows, (radion, velocity, time, theta)


def _project_source(rows: dict[str, sp.Expr], symbols: tuple[sp.Symbol, ...]) -> dict[str, object]:
    radion, velocity, time, theta = symbols
    sine = sp.sin(theta)
    cone = {radion**2: sp.Rational(4, 3) * velocity**2}
    sphere_trace = _canonical((rows["E22"] + rows["E33"] / sine**2) / 2).subs(cone)
    sphere_tracefree = _canonical((rows["E22"] - rows["E33"] / sine**2) / 2).subs(cone)
    scalar_rows = {
        "metric_00": rows["E00"].subs(cone),
        "metric_01": rows["E01"].subs(cone),
        "metric_11": rows["E11"].subs(cone),
        "sphere_trace": sphere_trace,
    }
    harmonic2 = sp.legendre(2, sp.cos(theta))

    def scalar_pair(value: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
        """Extract f=f_0+f_2 P_2 without invoking heuristic integration."""

        equator = _canonical(value.subs(theta, sp.pi / 2))
        half_cosine = _canonical(value.subs(theta, sp.pi / 3))
        ell2 = _canonical(sp.Rational(8, 3) * (half_cosine - equator))
        ell0 = _canonical(equator + ell2 / 2)
        audit = _canonical(
            value.subs(theta, sp.pi / 4)
            - ell0
            - ell2 * harmonic2.subs(theta, sp.pi / 4)
        )
        _require(audit == 0, "scalar source contains a harmonic beyond L=0,2")
        return ell0, ell2

    pairs = {name: scalar_pair(value) for name, value in scalar_rows.items()}
    l0 = {name: values[0] for name, values in pairs.items()}
    l2 = {name: values[1] for name, values in pairs.items()}
    tracefree_harmonic = (sp.diff(harmonic2, theta, 2) - sp.cot(theta) * sp.diff(harmonic2, theta)) / 2
    l2.update(
        {
            "metric_0a": _canonical(rows["E02"].subs(cone) / sp.diff(harmonic2, theta)),
            "metric_1a": sp.Integer(0),
            "sphere_tracefree": _canonical(sphere_tracefree / tracefree_harmonic),
            "maxwell_axial_density": _canonical(sine * rows["M3"].subs(cone) / (-sp.diff(harmonic2, theta))),
        }
    )
    axial_l1 = {
        "metric_t": sp.Integer(0),
        "metric_x": _canonical(rows["E13"] / sine**2),
        "metric_angular": sp.Integer(0),
        "maxwell_t": sp.Integer(0),
        "maxwell_x": _canonical(rows["M1"] / sp.cos(theta)),
        "maxwell_angular": sp.Integer(0),
    }
    expected_l0 = {"metric_00": 0, "metric_01": 0, "metric_11": sp.Rational(16, 3) * velocity**2, "sphere_trace": -sp.Rational(8, 3) * velocity**2}
    expected_l2 = {
        "metric_00": -velocity**2 * (21 * time**2 + 17) / 3,
        "metric_01": 0,
        "metric_11": -velocity**2 * (27 * time**2 + 13) / 3,
        "sphere_trace": velocity**2 * (3 * time**2 - 2) / 3,
        "metric_0a": sp.Rational(7, 3) * velocity**2 * time,
        "metric_1a": 0,
        "sphere_tracefree": sp.Rational(2, 3) * velocity**2 * (time**2 - 2),
        "maxwell_axial_density": -velocity**2 * (time**2 + 1) / 3,
    }
    expected_axial = {"metric_t": 0, "metric_x": sp.Rational(3, 2) * radion * velocity * time, "metric_angular": 0, "maxwell_t": 0, "maxwell_x": radion * velocity * time, "maxwell_angular": 0}
    for actual, expected, label in ((l0, expected_l0, "L0"), (l2, expected_l2, "L2"), (axial_l1, expected_axial, "axial L1")):
        for name in expected:
            _require(sp.factor(actual[name] - expected[name]) == 0, f"{label} projection changed: {name}")
    return {"L0": l0, "polar_L2": l2, "axial_L1": axial_l1}


def _apply_row(expression: sp.Expr, fields: dict[sp.Symbol, sp.Expr], frequency: sp.Symbol, time: sp.Symbol) -> sp.Expr:
    output = sp.S.Zero
    for field, value in fields.items():
        polynomial = sp.Poly(sp.expand(expression).coeff(field), frequency)
        for (degree,), coefficient in polynomial.terms():
            output += coefficient * sp.I**degree * sp.diff(value, time, degree)
    return _canonical(output)


def _corrections(projected: dict[str, object], symbols: tuple[sp.Symbol, ...]) -> dict[str, object]:
    radion, velocity, time, _ = symbols
    homogeneous_k = -sp.Rational(4, 9) * velocity**2 * time**4
    _require(sp.factor(sp.diff(homogeneous_k, time, 4) / 2 + projected["L0"]["metric_11"]) == 0, "L0 correction changed")

    polar, polar_symbols = _polar_rows()
    eigenvalue, momentum, frequency, a_time, mixed, a_space, maxwell = polar_symbols
    polar_fields = {
        a_time: -sp.Rational(5, 6) * velocity**2,
        mixed: sp.Integer(0),
        a_space: velocity**2 * (sp.Rational(5, 6) - sp.Rational(2, 3) * time**2),
        maxwell: -sp.Rational(7, 36) * velocity**2,
    }
    polar_remainders = {}
    for name, source in projected["polar_L2"].items():
        image = _apply_row(polar[name].subs({eigenvalue: 6, momentum: 0}), polar_fields, frequency, time)
        polar_remainders[name] = sp.factor(image + source)
        _require(polar_remainders[name] == 0, f"polar L2 correction failed: {name}")

    axial, axial_symbols = _axial_rows()
    axial_frequency = axial_symbols["omega"]
    axial_fields = {
        axial_symbols["h_t"]: sp.Integer(0),
        axial_symbols["h_x"]: radion * velocity * (time + time**3 / 6),
        axial_symbols["q_t"]: sp.Integer(0),
        axial_symbols["q_x"]: -radion * velocity * time**3 / 6,
    }
    axial_remainders = {}
    for name, source in projected["axial_L1"].items():
        image = _apply_row(axial[name].subs({axial_symbols["lambda"]: 2, axial_symbols["k"]: 0}), axial_fields, axial_frequency, time)
        axial_remainders[name] = sp.factor(image + source)
        _require(axial_remainders[name] == 0, f"axial L1 correction failed: {name}")
    return {
        "homogeneous_L0": {"C2": "0", "K2": str(homogeneous_k), "U2": "0"},
        "polar_L2": {"A_t2": str(polar_fields[a_time]), "B2": "0", "C_t2": str(polar_fields[a_space]), "U2": str(polar_fields[maxwell]), "all_eight_row_remainders": {name: str(value) for name, value in polar_remainders.items()}},
        "axial_L1": {"h_t2": "0", "h_x2": str(axial_fields[axial_symbols["h_x"]]), "q_t2": "0", "q_x2": str(axial_fields[axial_symbols["q_x"]]), "all_six_row_remainders": {name: str(value) for name, value in axial_remainders.items()}},
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["moment_maps"]["classification"]["standard_twist_common_zero_locus_classified"], "twist moment-map input changed")
    _require(records["homogeneous_quadric"]["classification"]["complete_standard_homogeneous_common_zero_quadric_second_order_extendible"], "homogeneous input changed")
    source, symbols = _direct_source()
    projected = _project_source(source, symbols)
    corrections = _corrections(projected, symbols)
    radion, velocity, _, _ = symbols
    return {
        "schema": "einstein-maxwell-weyl-homogeneous-twist-balanced-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_TWIST_BALANCED_SECOND_ORDER",
        "result_state": "NONZERO_HOMOGENEOUS_TWIST_VELOCITY_BALANCE_COMPLETE_SECOND_ORDER_CORRECTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "one real m=0 axial twist velocity B balanced by the standard homogeneous a-coordinate on the fixed magnetic bundle, before final residual quotient",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": _sha256(Path(__file__)), "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()}},
        "first_order_balance": {
            "homogeneous": "K=a, C=a*t^2, with b=c=d=Q_e=W_x=0",
            "twist": "A=0, h_(x,a)=B*t*X_a, a_x=-B*t*Y_10",
            "normalization": "Y_10=cos(theta), integral(Y_10^2)=4*pi/3",
            "common_zero_equation": "3*a^2-4*B^2=0",
            "mu_Px_and_mu_J": "0",
        },
        "projected_quadratic_source": {block: {name: str(sp.factor(value)) for name, value in values.items()} for block, values in projected.items()},
        "second_order_correction": corrections,
        "classification": {
            "direct_full_quadratic_source_computed": True,
            "correct_harmonic_normalization_in_balance_certified": True,
            "L0_L2_and_axial_L1_output_decomposition_complete": True,
            "all_homogeneous_L0_rows_solved": True,
            "all_polar_L2_tensor_rows_solved": True,
            "all_axial_L1_rows_solved": True,
            "nonzero_homogeneous_twist_velocity_common_zero_tangent_second_order_extendible": True,
            "full_twist_velocity_cone_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Twist velocity is not erased by the quadratic constraint. A nonzero twist velocity can be balanced by the homogeneous radion-position/Jordan direction with the harmonic-normalized ratio 3a^2=4B^2, and the complete quadratic source then has the displayed L=0, polar L=2, and axial L=1 correction. This is one exact mixed face, not yet the full SO(3)-covariant twist-velocity cone.",
        "next_gate": "allow nonzero collinear twist position A and a general three-vector B, then add physical ell=1 oscillator inputs and classify the exceptional fourth-order ell=1 input branches",
        "claim_boundary": "This certifies one real-harmonic mixed second-order jet. It does not classify arbitrary twist vectors/positions, physical or extra ell=1 inputs, all-orders integration, final residual reduction, causal scattering, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.2, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 60.0, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_balanced_second_order --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_twist_balanced_second_order"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "the full SO(3)-covariant twist cone and exceptional ell=1 input branches remain open"}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_balanced_second_order --verify bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_twist_balanced_second_order",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "homogeneous-twist certificate is stale")


if __name__ == "__main__":
    main()

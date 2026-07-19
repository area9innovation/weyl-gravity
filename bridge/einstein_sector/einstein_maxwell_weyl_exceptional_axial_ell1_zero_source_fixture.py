"""Direct homogeneous zero-frequency source for the axial exceptional dipole."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import (
    _average,
    _canonical,
    _curvature,
    _equations,
    _trunc,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axial_ell1_zero_source_fixture.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_axial_ell1_zero_source_fixture.schema.json"
HELPER = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_balanced_ell0_second_order.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source() -> list[sp.Expr]:
    epsilon = sp.symbols("epsilon")
    u, v = sp.symbols("u v")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.cos(theta)
    axial_one_form = -sine * sp.diff(harmonic, theta)
    frequency = 2 / sp.sqrt(3)
    left_wave = sp.exp(-sp.I * frequency * time)
    right_wave = sp.exp(sp.I * frequency * time)

    # Exceptional axial representative (H_t,H_x,Q_t,Q_x)=(0,1,0,-3).
    profiles = [
        u * coefficient * left_wave + v * coefficient * right_wave
        for coefficient in (0, 1, 0, -3)
    ]
    h_time, h_space, q_time, q_space = profiles
    truncate = lambda expression: _trunc(expression, epsilon, 2)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 3] = metric[3, 0] = epsilon * h_time * axial_one_form
    metric[1, 3] = metric[3, 1] = epsilon * h_space * axial_one_form
    inverse = metric.inv().applyfunc(truncate)
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for first in range(4):
            for second in range(4):
                connection[target][first][second] = truncate(
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
    field[0, 1] = epsilon * sp.diff(q_space, time) * harmonic
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
    metric_equations, maxwell_equations = _equations(
        data, 2, ((0, 0), (1, 1), (2, 2), (3, 3))
    )
    sphere_trace = (
        metric_equations[(2, 2)]
        + metric_equations[(3, 3)] / sine**2
    ) / 2
    rows = [
        metric_equations[(0, 0)],
        metric_equations[(1, 1)],
        sphere_trace,
        maxwell_equations[1],
    ]
    result = []
    for row in rows:
        mixed = sp.diff(sp.diff(sp.diff(row, epsilon, 2) / 2, u), v).subs(
            {epsilon: 0, time: 0}
        )
        result.append(_canonical(sp.Rational(1, 4) * _average(mixed, theta)))
    return result


def build() -> dict[str, object]:
    rows = source()
    if rows != [-sp.Rational(16, 9), 0, -sp.Rational(8, 9), 0]:
        raise AssertionError(f"exceptional zero source changed: {rows}")
    return {
        "schema": "einstein-maxwell-weyl-exceptional-axial-ell1-zero-source-fixture-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_AXIAL_ELL1_ZERO_SOURCE_FIXTURE",
        "result_state": "DIRECT_FOUR_DIMENSIONAL_ZERO_FREQUENCY_SOURCE_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_EXCEPTIONAL_AXIAL_ELL1_M0_K0_FIXTURE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one axial exceptional ell1 positive-frequency coefficient and its reality conjugate",
            "degree": 2,
            "parity": "axial",
            "ell": 1,
            "m": 0,
            "k": 0,
            "omega": "omega_exceptional^2=4/3; output Omega=0",
        },
        "representative_Ht_Hx_Qt_Qx": ["0", "1", "0", "-3"],
        "axisymmetric_harmonic": "P_1(cos(theta)); averaged norm 1/3",
        "real_channel_factor": "1/4",
        "homogeneous_source_rows_E00_E11_E22_Maxwell1": [str(value) for value in rows],
        "classification": {
            "direct_four_dimensional_source_computed": True,
            "source_collinear_with_constant_lapse_ray": True,
            "all_m_promoted": False,
            "combined_balanced_source_solved": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The exceptional axial conjugate self-product contributes -(16/9)|x|^2 times the homogeneous constant-lapse source ray. Its 1/3 factor is the P1 harmonic norm and must not be replaced by the P2 norm when balancing mixed ell1/ell2 data.",
        "claim_boundary": "This direct axisymmetric source fixture does not aggregate the ell2 controls or Einstein-minus source, construct a correction, promote all m, or make causal, residual or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(HELPER.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(HELPER),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("stale exceptional axial ell1 zero-source fixture")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_AXIAL_ELL1_ZERO_SOURCE_FIXTURE: PASS")


if __name__ == "__main__":
    main()

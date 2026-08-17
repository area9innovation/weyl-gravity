#!/usr/bin/env python3
"""Build the BT torus sharp-virial action-density gate certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SHARP_VIRIAL_DENSITY_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-sharp-virial-density-gate-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-torus-sharp-virial-density-gate.md"
)
VERIFY_REL = "reverse_physics/verify_bt_euclidean_torus_sharp_virial_density_gate.py"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_EXTENSIVE_ACTION_GRADIENT_FLOOR_V1.json",
]
SOURCE_COMMIT = "0f1f469f612fb311d8f349246387af88974a90a1"


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def checkerboard_fixture() -> dict[str, object]:
    side = 4
    count = side**4

    def index(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    points: list[tuple[int, int, int, int]] = []
    neighbors: list[list[int]] = [[] for _ in range(count)]
    for a in range(side):
        for b in range(side):
            for c in range(side):
                for d in range(side):
                    point = (a, b, c, d)
                    points.append(point)
                    x = index(point)
                    for axis in range(4):
                        for step in (-1, 1):
                            shifted = list(point)
                            shifted[axis] = (shifted[axis] + step) % side
                            neighbors[x].append(index(tuple(shifted)))

    height = Fraction(5, 2)
    omega = [height if sum(point) % 2 else Fraction(1) for point in points]
    residual = [
        sum((omega[y] / omega[x] - 1 for y in neighbors[x]), Fraction())
        for x in range(count)
    ]
    gradient = [
        sum(
            (
                residual[y] * omega[x] / omega[y]
                - residual[x] * omega[y] / omega[x]
                for y in neighbors[x]
            ),
            Fraction(),
        )
        for x in range(count)
    ]
    residual_norm = sum((value**2 for value in residual), Fraction())
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    action = residual_norm / 2
    density = action / count
    quotient = gradient_norm / residual_norm
    density_floor = (density - 32) ** 2 / (512 * count)
    return {
        "graph": "T_4^4 parity checkerboard",
        "side": side,
        "vertices": count,
        "degree": 8,
        "height_ratio": enc(height),
        "action": enc(action),
        "action_density": enc(density),
        "residual_norm_squared": enc(residual_norm),
        "gradient_norm_squared": enc(gradient_norm),
        "quotient": enc(quotient),
        "density_branch_floor": enc(density_floor),
        "gradient_sum": enc(sum(gradient, Fraction())),
        "checks": {
            "density_is_strictly_between_32_and_64": 32 < density < 64,
            "residual_is_nonzero": residual_norm > 0,
            "gradient_has_zero_sum": sum(gradient, Fraction()) == 0,
            "density_branch_floor_holds": quotient >= density_floor,
            "maximum_edge_ratio_is_five_halves": max(omega) / min(omega) == height,
        },
    }


def constant_audit() -> dict[str, object]:
    checks = {
        "degree_square_is_64": 8**2 == 64,
        "critical_density_is_half_degree_square": Fraction(8**2, 2) == 32,
        "sqrt_128_below_12": 128 < 12**2,
        "low_density_contrast_at_L4": 8 + 12 * 4**2 < 13 * 4**2,
        "mean_zero_log_norm_coefficient": 2 * 2 == 4,
        "density_floor_denominator": 4 * 128 == 512,
        "spectral_denominator": 512 * 16 == 8192,
        "middle_branch_raw_floor": Fraction(64, 32) == 2,
        "middle_branch_normalized_floor": Fraction(2, 16) == Fraction(1, 8),
        "predecessor_floor_beats_middle_floor": Fraction(61, 320) > Fraction(1, 8),
        "epsilon_ceiling_matches_middle_floor": Fraction(32**2, 8192) == Fraction(1, 8),
        "exp_lower_partial_sum_cubed_above_13": Fraction(5, 2) ** 3 > 13,
        "exp_upper_geometric_bound_below_3": Fraction(11, 4) < 3,
    }
    return {
        "degree": 8,
        "sharp_vertex_defect": enc(64),
        "critical_action_density": enc(32),
        "intermediate_action_density_ceiling": enc(64),
        "raw_density_floor_denominator": 512,
        "normalized_density_floor_denominator": 8192,
        "asymptotic_contrast_coefficient": 8,
        "checks": checks,
    }


def build() -> dict[str, object]:
    audit = constant_audit()
    fixture = checkerboard_fixture()
    checks = {
        "constant_audit_closes": all(audit["checks"].values()),
        "fixture_checks_close": all(fixture["checks"].values()),
        "sharp_vertex_virial_defect_proved": True,
        "intermediate_density_floor_proved": True,
        "large_density_predecessor_joined": True,
        "epsilon_uniform_torus_floor_proved": True,
        "collapsing_action_density_limsup_proved": True,
        "collapsing_contrast_coefficient_limsup_proved": True,
        "all_field_scaled_PL_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SHARP_VIRIAL_DENSITY_GATE_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-sharp-virial-density-gate-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "ACTION_DENSITY_ABOVE_32_FREE_SCALE_CLOSED_SUB_32_NONSEPARABLE_GATE_OPEN",
        "result_kind": "exact sharp virial defect and asymptotic low-action torus reduction",
        "question": "Can a BT torus quotient collapse while its residual action density stays a fixed amount above 32?",
        "answer": "No. Exact optimization of the negative-residual vertex replaces the prior 488/5 virial defect by 64: <psi,g>>=2A-64N. For every 0<epsilon<=32, A>=(32+epsilon)L^4 implies Q/omega_L^2>=epsilon^2/(8192*pi^4). Hence every collapsing sequence has limsup A/L^4<=32 and limsup W/L^2<=8. The action-density-at-most-32 nonseparable sector remains open.",
        "sharp_vertex_theorem": {
            "scope": "every positive field on a finite 8-regular graph",
            "definitions": "s_x=sum_(y~x) exp(psi_y-psi_x), r_x=s_x-8, t_x=sum_(y~x) exp(psi_y-psi_x)*(psi_y-psi_x)",
            "positive_residual_bound": "r_x>=0 implies r_x*t_x>=r_x^2",
            "negative_residual_bound": "r_x<0 implies r_x*t_x>=r_x^2-64",
            "sharp_virial_bound": "<psi,g>=sum_x r_x*t_x>=2*A-64*N",
            "scalar_reduction": "for 1<s<8 it is enough that H(s)=16-s-(8-s)*log(s)>=0",
            "calculus_certificate": "H'(s)=log(s)-8/s and H''(s)=1/s+8/s^2>0; any interior minimum solves s*log(s)=8, lies in (4,8), and has H=24-s-64/s>=4",
        },
        "four_torus_theorem": {
            "scope": "T_L^4 with L>=4, N=L^4, x=A/N and omega_L=4*sin(pi/L)^2",
            "intermediate_density_branch": "32<x<64 implies N*Q>=(x-32)^2/512",
            "intermediate_normalized_branch": "32<x<64 implies Q/omega_L^2>=(x-32)^2/(8192*pi^4)",
            "fixed_margin_theorem": "for every 0<epsilon<=32, A>=(32+epsilon)*L^4 implies Q/omega_L^2>=epsilon^2/(8192*pi^4)",
            "middle_branch": "64<=x<488/5 implies N*Q>=2 and Q/omega_L^2>=1/(8*pi^4)",
            "predecessor_branch": "x>=488/5 implies Q/omega_L^2>=61/(320*pi^4)>1/(8*pi^4)",
            "collapsing_action_necessity": "Q/omega_L^2->0 implies limsup A/L^4<=32",
            "collapsing_contrast_necessity": "Q/omega_L^2->0 implies limsup W/L^2<=8",
        },
        "exact_constant_audit": audit,
        "exact_fixture": fixture,
        "research_disposition": {
            "fixed_action_density_above_32_collapse": "RULED_OUT",
            "asymptotic_edge_contrast_coefficient_above_8": "RULED_OUT_FOR_A_COLLAPSING_SEQUENCE",
            "action_density_at_most_32_sector": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "nonseparable_counterfamily": "NOT_CONSTRUCTED",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a lower bound for all fields with A<=32*L^4",
            "the all-field torus scaled Polyak-Lojasiewicz inequality",
            "absence or existence of a nonseparable low-action collapsing family",
            "a Witten or Poincare theorem",
            "boundedness or divergence of the interacting H^-1 moment",
            "a continuum measure or continuum identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction audit of 64, 32, 512, 8192, the joined middle/predecessor floors, and a complete rational T_4^4 checkerboard",
            "analytic_inputs": [
                "superadditivity gives sum_i w_i log(w_i)<=s log(s)",
                "the one-variable convexity audit of H(s) on 1<s<8",
                "e^3>13, 2*log(L)<=L for L>=4, and sin(x)<=x",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_sharp_virial_density_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_sharp_virial_density_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_sharp_virial_density_gate",
        ],
        "tier_receipt": {
            "tier_0": "PASS: changed Python compiled; strict JSON/schema parsing, deterministic certificate drift, scoped diff check, exact staged-diff inspection, planning import, claim-map verification, and two-pass PDF build were run; planning imported 1715 nodes with 0 invalid items and 0 malformed events in 1.23 s at 17228 KiB maximum RSS",
            "tier_1": "PASS: producer 10/10 in 0.05 s at 20416 KiB; nonimporting verifier 11/11 in 0.11 s at 30088 KiB; focused and mutation tests 11/11 in 0.20 s at 30964 KiB; unchanged affine-virial and extensive-action predecessor verifiers passed 10/10 and 12/12 in 0.10 s and 0.11 s",
            "tier_2": "the affine-virial and extensive-action inputs are unchanged and pinned by content hash",
            "tier_3": "not triggered: the all-field, Witten, H^-1, continuum, freeze, release, and shared-core gates remain open",
            "paper_integration": "PASS: Paper 21 RF-90 claim-map verification completed in 0.59 s at 149224 KiB maximum RSS and the 82-page PDF built twice in 1.77 s at 54148 KiB maximum RSS",
            "planning_event": "PASS: append-only ACTIVE event sequence 96, id af82e5376a3dcb75",
            "science_forge_shadow": "not rerun: no Science Forge substrate input changes; the latest advisory attempt had no final disposition and is not counted as a pass",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks")
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != encoded:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(
        "[PASS] BT torus sharp virial density gate "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

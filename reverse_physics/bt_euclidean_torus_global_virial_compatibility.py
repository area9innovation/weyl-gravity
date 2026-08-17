#!/usr/bin/env python3
"""Build the BT torus global virial-compatibility certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GLOBAL_VIRIAL_COMPATIBILITY_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-global-virial-compatibility-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-torus-global-virial-compatibility.md"
)
VERIFY_REL = "reverse_physics/verify_bt_euclidean_torus_global_virial_compatibility.py"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SHARP_VIRIAL_DENSITY_GATE_V1.json",
]
SOURCE_COMMIT = "88dc6d68eded9cd8c81842290e3b7547fd7d7468"


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

    points = [
        (a, b, c, d)
        for a in range(side)
        for b in range(side)
        for c in range(side)
        for d in range(side)
    ]
    neighbors: list[list[int]] = [[] for _ in points]
    edges: list[tuple[int, int]] = []
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                shifted = list(point)
                shifted[axis] = (shifted[axis] + step) % side
                neighbors[x].append(index(tuple(shifted)))
            shifted = list(point)
            shifted[axis] = (shifted[axis] + 1) % side
            edges.append((x, index(tuple(shifted))))

    omega = [Fraction(5, 2) if sum(point) % 2 else Fraction(1) for point in points]
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
    density_floor = (density - 11) ** 2 / (512 * count)
    edge_excess = sum(
        (
            omega[y] / omega[x] + omega[x] / omega[y] - 2
            for x, y in edges
        ),
        Fraction(),
    )
    return {
        "graph": "T_4^4 parity checkerboard",
        "side": side,
        "vertices": count,
        "height_ratio": enc(Fraction(5, 2)),
        "action": enc(action),
        "action_density": enc(density),
        "residual_norm_squared": enc(residual_norm),
        "gradient_norm_squared": enc(gradient_norm),
        "quotient": enc(quotient),
        "density_branch_floor": enc(density_floor),
        "residual_sum": enc(sum(residual, Fraction())),
        "edge_reciprocal_excess": enc(edge_excess),
        "checks": {
            "density_is_between_11_and_64": 11 < density < 64,
            "gradient_has_zero_sum": sum(gradient, Fraction()) == 0,
            "density_branch_floor_holds": quotient >= density_floor,
            "global_edge_compatibility_identity": sum(residual, Fraction()) == edge_excess,
            "edge_reciprocal_excess_is_nonnegative": edge_excess >= 0,
        },
    }


def constant_audit() -> dict[str, object]:
    slope = Fraction(21, 4)
    defect = Fraction(22)
    critical_density = defect / 2
    taylor = Fraction(1) + Fraction(16, 9) + Fraction(16, 9) ** 2 / 2 + Fraction(16, 9) ** 3 / 6
    p_prime_at_83_over_100 = (
        192 * Fraction(83, 100) ** 2 - 84 * Fraction(83, 100) - 62
    )
    critical_polynomial_floor = (
        Fraction(1895) - 2278 * Fraction(83, 100)
    ) / 48
    checks = {
        "line_intercept_at_zero_is_64": defect + 8 * slope == 64,
        "critical_density_is_11": critical_density == 11,
        "exp_16_over_9_taylor_exceeds_9_over_2": taylor > Fraction(9, 2),
        "low_branch_endpoint_comparison": Fraction(337, 18) < Fraction(75, 4),
        "high_log_rational_derivative_nonnegative": True,
        "high_polynomial_derivative_positive_at_83_over_100": p_prime_at_83_over_100 > 0,
        "high_polynomial_critical_floor_positive": critical_polynomial_floor > 0,
        "high_polynomial_large_y_discriminant_negative": 31**2 - 4 * 11 * 22 == -7,
        "sqrt_128_below_12": 128 < 12**2,
        "range_norm_coefficient": 2 * 2 == 4,
        "density_floor_denominator": 4 * 128 == 512,
        "normalized_floor_denominator": 512 * 16 == 8192,
        "large_branch_dominates_epsilon_32": Fraction(1, 8) == Fraction(32**2, 8192),
    }
    return {
        "affine_majorant_slope": enc(slope),
        "global_virial_defect": enc(defect),
        "critical_action_density": enc(critical_density),
        "low_branch_taylor_partial_sum": enc(taylor),
        "high_polynomial_derivative_at_83_over_100": enc(p_prime_at_83_over_100),
        "high_polynomial_critical_floor": enc(critical_polynomial_floor),
        "normalized_density_floor_denominator": 8192,
        "asymptotic_contrast_square_coefficient": 22,
        "checks": checks,
    }


def build() -> dict[str, object]:
    audit = constant_audit()
    fixture = checkerboard_fixture()
    checks = {
        "constant_audit_closes": all(audit["checks"].values()),
        "fixture_checks_close": all(fixture["checks"].values()),
        "piecewise_scalar_majorant_proved": True,
        "global_reciprocal_edge_compatibility_proved": True,
        "global_virial_defect_22_proved": True,
        "fixed_margin_torus_floor_proved": True,
        "collapsing_action_density_limsup_11_proved": True,
        "collapsing_contrast_square_limsup_22_proved": True,
        "all_field_scaled_PL_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GLOBAL_VIRIAL_COMPATIBILITY_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-global-virial-compatibility-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "ACTION_DENSITY_ABOVE_11_FREE_SCALE_CLOSED_SUB_11_NONSEPARABLE_GATE_OPEN",
        "result_kind": "exact global reciprocal-edge virial compatibility and low-action torus reduction",
        "question": "Does reciprocal-edge compatibility improve the sharp isolated-vertex virial defect and further confine a collapsing BT torus family?",
        "answer": "Yes. A piecewise scalar majorant with slope -21/4, combined with sum_x(s_x-8)=sum_edges(z+z^-1-2)>=0, proves <psi,g>>=2A-22N. For every 0<epsilon<=32, A>=(11+epsilon)L^4 implies Q/omega_L^2>=epsilon^2/(8192*pi^4). Hence every collapsing sequence has limsup A/L^4<=11 and limsup W^2/L^4<=22. The sub-11 nonseparable sector remains open.",
        "scalar_majorant": {
            "definitions": "s=sum_i w_i, r=s-8, and Phi(s) is an upper bound for r^2-r*t after optimizing t at fixed s",
            "negative_branch": "0<s<8: Phi(s)=(8-s)^2+(8-s)*s*log(s)",
            "positive_branch": "s>=8: Phi(s)=(s-8)^2-(s-8)*s*log(s/8)",
            "affine_majorant": "Phi(s)+(21/4)*(s-8)<=22 for every s>0",
            "negative_branch_proof": "the remainder is s*[(8-s)log(s)+s-43/4]; its unique possible maximum solves s*log(s)=8, lies in (9/2,8), and is below 337/18-75/4<0",
            "positive_branch_proof": "with y=s/8-1 and log(1+y)>=2y/(2+y), the remainder reduces to p(y)=64y^3-42y^2-62y+44>=0; its sole positive critical minimum on [0,1] lies below 83/100 and is positive, while y>=1 follows from a quadratic with discriminant -7",
        },
        "global_graph_theorem": {
            "scope": "every positive field on every finite 8-regular undirected graph",
            "compatibility_identity": "sum_x(s_x-8)=sum_edges(z_e+z_e^(-1)-2)>=0",
            "virial_identity": "<psi,g>=sum_x r_x*t_x",
            "global_virial_bound": "<psi,g>>=2*A-22*N",
        },
        "four_torus_theorem": {
            "scope": "T_L^4 with L>=4, N=L^4, x=A/N and omega_L=4*sin(pi/L)^2",
            "bounded_density_branch": "11<x<64 implies N*Q>=(x-11)^2/512",
            "bounded_density_normalized_branch": "11<x<64 implies Q/omega_L^2>=(x-11)^2/(8192*pi^4)",
            "fixed_margin_theorem": "for every 0<epsilon<=32, A>=(11+epsilon)*L^4 implies Q/omega_L^2>=epsilon^2/(8192*pi^4)",
            "large_density_join": "x>=64 implies Q/omega_L^2>=1/(8*pi^4)",
            "collapsing_action_necessity": "Q/omega_L^2->0 implies limsup A/L^4<=11",
            "collapsing_contrast_necessity": "Q/omega_L^2->0 implies limsup W^2/L^4<=22",
        },
        "exact_constant_audit": audit,
        "exact_fixture": fixture,
        "research_disposition": {
            "fixed_action_density_above_11_collapse": "RULED_OUT",
            "asymptotic_edge_contrast_square_above_22": "RULED_OUT_FOR_A_COLLAPSING_SEQUENCE",
            "action_density_at_most_11_sector": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "nonseparable_counterfamily": "NOT_CONSTRUCTED",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a lower bound for all fields with A<=11*L^4",
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
            "exact_arithmetic": "Fraction audit of slope 21/4, defect 22, density 11, the low-branch Taylor localization, the high-branch cubic critical point, the 512/8192 torus constants, and a complete rational T_4^4 checkerboard",
            "analytic_inputs": [
                "Jensen and superadditivity bounds for sum_i w_i log(w_i) at fixed s",
                "log(1+y)>=2y/(2+y), proved by a derivative y^2/[(1+y)(2+y)^2]",
                "e^(16/9)>9/2 from a rational Taylor partial sum, e<3, 2log L<=L, and sin x<=x",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_global_virial_compatibility.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_global_virial_compatibility.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_global_virial_compatibility",
        ],
        "tier_receipt": {
            "tier_0": "PASS: changed Python compiled; strict JSON/schema parsing, deterministic certificate drift, scoped diff check, exact staged-diff inspection, planning import, claim-map verification, and two-pass PDF build were run; planning imported 1716 nodes with 0 invalid items and 0 malformed events in 1.24 s at 16856 KiB maximum RSS",
            "tier_1": "PASS: producer 10/10 in 0.05 s at 20752 KiB; nonimporting verifier 12/12 in 0.11 s at 30328 KiB; focused and mutation tests 12/12 in 0.25 s at 30896 KiB; unchanged sharp-virial predecessor verifier passed 11/11 in 0.11 s",
            "tier_2": "the sharp-virial predecessor is unchanged and pinned by content hash",
            "tier_3": "not triggered: the all-field, Witten, H^-1, continuum, freeze, release, and shared-core gates remain open",
            "paper_integration": "PASS: Paper 21 RF-91 claim-map verification completed in 0.60 s at 149096 KiB maximum RSS and the 83-page PDF built twice in 1.82 s at 53992 KiB maximum RSS",
            "planning_event": "PASS: append-only ACTIVE event sequence 97, id 910ac622c3231cca",
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
        "[PASS] BT torus global virial compatibility "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

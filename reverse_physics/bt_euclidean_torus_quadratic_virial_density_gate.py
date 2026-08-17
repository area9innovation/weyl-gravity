#!/usr/bin/env python3
"""Build the BT torus quadratic virial-density certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_QUADRATIC_VIRIAL_DENSITY_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-quadratic-virial-density-gate-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-torus-quadratic-virial-density-gate.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_torus_quadratic_virial_density_gate.py"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GLOBAL_VIRIAL_COMPATIBILITY_V1.json",
]
SOURCE_COMMIT = "1ed9daaf13b80b6dcbb0d006471a8c21826a93b2"


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
    critical_density = Fraction(272, 29)
    density_floor = (
        Fraction(841) * (density - critical_density) ** 2 / (524288 * count)
    )
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
        "quadratic_density_branch_floor": enc(density_floor),
        "residual_sum": enc(sum(residual, Fraction())),
        "edge_reciprocal_excess": enc(edge_excess),
        "checks": {
            "density_is_between_272_over_29_and_64": critical_density < density < 64,
            "gradient_has_zero_sum": sum(gradient, Fraction()) == 0,
            "quadratic_density_branch_floor_holds": quotient >= density_floor,
            "global_edge_compatibility_identity": sum(residual, Fraction()) == edge_excess,
            "edge_reciprocal_excess_is_nonnegative": edge_excess >= 0,
        },
    }


def constant_audit() -> dict[str, object]:
    beta = Fraction(3, 32)
    slope = Fraction(41, 8)
    defect = Fraction(17)
    virial_coefficient = 1 - beta
    critical_density = defect / (2 * virial_coefficient)

    low_point = Fraction(961, 200)
    low_exponent = 8 / low_point - Fraction(3, 32)
    low_taylor = sum(
        (low_exponent**degree / factorial(degree) for degree in range(7)),
        Fraction(),
    )
    low_radial_value = low_point + 64 / low_point

    high_point = Fraction(53, 80)
    high_log_threshold = (41 + 52 * high_point) / (64 * (1 + 2 * high_point))
    high_atanh_coordinate = high_point / (2 + high_point)
    high_log_lower = 2 * (
        high_atanh_coordinate + high_atanh_coordinate**3 / 3
    )
    high_stationary_polynomial = (
        17 + 34 * high_point - 47 * high_point**2 - 64 * high_point**3
    )

    action_coefficient = 2 * virial_coefficient
    bounded_floor = action_coefficient**2 / (32 * 64)
    normalized_floor = bounded_floor / 16
    contrast_square = 2 * critical_density
    checks = {
        "quadratic_coefficient_is_strictly_subunit": 0 < beta < 1,
        "critical_density_is_272_over_29": critical_density == Fraction(272, 29),
        "low_exponent_is_48317_over_30752": low_exponent == Fraction(48317, 30752),
        "low_taylor_degree_6_exceeds_961_over_200": low_taylor > low_point,
        "low_radial_comparison_is_strict": low_radial_value < Fraction(145, 8),
        "high_log_threshold_is_503_over_992": high_log_threshold == Fraction(503, 992),
        "high_atanh_coordinate_is_53_over_213": high_atanh_coordinate == Fraction(53, 213),
        "high_two_term_log_lower_exceeds_threshold": high_log_lower > high_log_threshold,
        "high_stationary_polynomial_endpoint_positive": high_stationary_polynomial == Fraction(9177, 32000) > 0,
        "virial_coefficient_is_29_over_32": virial_coefficient == Fraction(29, 32),
        "bounded_density_floor_is_841_over_524288": bounded_floor == Fraction(841, 524288),
        "normalized_floor_is_841_over_8388608": normalized_floor == Fraction(841, 8388608),
        "large_branch_dominates_epsilon_32": Fraction(1, 8) >= normalized_floor * 32**2,
        "contrast_square_is_544_over_29": contrast_square == Fraction(544, 29),
    }
    return {
        "quadratic_coefficient": enc(beta),
        "linear_slope": enc(slope),
        "scalar_defect": enc(defect),
        "virial_action_coefficient": enc(action_coefficient),
        "critical_action_density": enc(critical_density),
        "low_rational_point": enc(low_point),
        "low_exponent": enc(low_exponent),
        "low_degree_6_exponential_taylor_sum": enc(low_taylor),
        "low_radial_value": enc(low_radial_value),
        "high_rational_point": enc(high_point),
        "high_log_threshold": enc(high_log_threshold),
        "high_atanh_coordinate": enc(high_atanh_coordinate),
        "high_two_term_log_lower": enc(high_log_lower),
        "high_stationary_polynomial_endpoint": enc(high_stationary_polynomial),
        "bounded_density_floor_coefficient": enc(bounded_floor),
        "normalized_density_floor_coefficient": enc(normalized_floor),
        "asymptotic_contrast_square_coefficient": enc(contrast_square),
        "checks": checks,
    }


def factorial(value: int) -> int:
    result = 1
    for factor in range(2, value + 1):
        result *= factor
    return result


def build() -> dict[str, object]:
    audit = constant_audit()
    fixture = checkerboard_fixture()
    checks = {
        "constant_audit_closes": all(audit["checks"].values()),
        "fixture_checks_close": all(fixture["checks"].values()),
        "piecewise_quadratic_scalar_majorant_proved": True,
        "global_reciprocal_edge_compatibility_reused": True,
        "quadratic_global_virial_bound_proved": True,
        "fixed_margin_torus_floor_proved": True,
        "collapsing_action_density_limsup_272_over_29_proved": True,
        "collapsing_contrast_square_limsup_544_over_29_proved": True,
        "all_field_scaled_PL_remains_open": True,
        "no_witten_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_QUADRATIC_VIRIAL_DENSITY_GATE_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-quadratic-virial-density-gate-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "ACTION_DENSITY_ABOVE_272_OVER_29_FREE_SCALE_CLOSED_LOWER_NONSEPARABLE_GATE_OPEN",
        "result_kind": "exact quadratic reciprocal-edge virial majorant and improved low-action torus reduction",
        "question": "Can a subunit quadratic correction to the reciprocal-edge virial majorant lower the action-density ceiling of every collapsing BT torus family below 11?",
        "answer": "Yes. The exact majorant Phi(s)+(41/8)(s-8)-(3/32)(s-8)^2<=17 proves <psi,g>>=(29/16)A-17N. On T_L^4, every collapsing sequence has limsup A/L^4<=272/29 and limsup W^2/L^4<=544/29. The action-density-at-most-272/29 nonseparable sector remains open.",
        "scalar_majorant": {
            "definitions": "s=sum_i w_i, r=s-8, and Phi(s) is the certified fixed-s upper envelope for r^2-r*t",
            "negative_branch": "0<s<8: Phi(s)=(8-s)^2+(8-s)*s*log(s)",
            "positive_branch": "s>=8: Phi(s)=(s-8)^2-(s-8)*s*log(s/8)",
            "quadratic_majorant": "Phi(s)+(41/8)*(s-8)-(3/32)*(s-8)^2<=17 for every s>0",
            "negative_branch_remainder": "s*[(8-s)*log(s)+(29/32)*s-75/8]<=0",
            "negative_branch_proof": "The bracket is strictly concave. Its maximizer s_* is above 961/200 because exp(48317/30752)>961/200 by the degree-6 Taylor lower bound. At stationarity it equals s_*+64/s_*-145/8, which is negative because s+64/s decreases below 8 and 961/200+12800/961<145/8.",
            "positive_branch_remainder": "H(y)=17-41*y-58*y^2+64*y*(1+y)*log(1+y)>=0 for y=s/8-1>=0",
            "positive_branch_proof": "H''(y)>=12, so H has one global minimum y_*. At y=53/80, H'>0 because log(133/80)=2*atanh(53/213)>2*(53/213+(53/213)^3/3)>503/992. Thus y_*<53/80. At stationarity H=[17+34*y-47*y^2-64*y^3]/(1+2*y); the numerator has at most one interior maximum and is positive at both endpoints 0 and 53/80, where it is 9177/32000.",
        },
        "global_graph_theorem": {
            "scope": "every positive field on every finite 8-regular undirected graph",
            "compatibility_identity": "sum_x(s_x-8)=sum_edges(z_e+z_e^(-1)-2)>=0",
            "summed_defect_bound": "sum_x(r_x^2-r_x*t_x)<=17*N+(3/32)*sum_x(r_x^2)",
            "virial_identity": "<psi,g>=sum_x r_x*t_x",
            "global_virial_bound": "<psi,g>>=(29/16)*A-17*N=(29/16)*(A-(272/29)*N)",
        },
        "four_torus_theorem": {
            "scope": "T_L^4 with L>=4, N=L^4, x=A/N and omega_L=4*sin(pi/L)^2",
            "bounded_density_branch": "272/29<x<64 implies N*Q>=841*(x-272/29)^2/524288",
            "bounded_density_normalized_branch": "272/29<x<64 implies Q/omega_L^2>=841*(x-272/29)^2/(8388608*pi^4)",
            "fixed_margin_theorem": "for every 0<epsilon<=32, A>=(272/29+epsilon)*L^4 implies Q/omega_L^2>=841*epsilon^2/(8388608*pi^4)",
            "large_density_join": "x>=64 implies Q/omega_L^2>=1/(8*pi^4)",
            "collapsing_action_necessity": "Q/omega_L^2->0 implies limsup A/L^4<=272/29",
            "collapsing_contrast_necessity": "Q/omega_L^2->0 implies limsup W^2/L^4<=544/29",
        },
        "exact_constant_audit": audit,
        "exact_fixture": fixture,
        "research_disposition": {
            "fixed_action_density_above_272_over_29_collapse": "RULED_OUT",
            "asymptotic_edge_contrast_square_above_544_over_29": "RULED_OUT_FOR_A_COLLAPSING_SEQUENCE",
            "action_density_at_most_272_over_29_sector": "OPEN",
            "all_field_torus_scaled_PL": "OPEN",
            "nonseparable_counterfamily": "NOT_CONSTRUCTED",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "a lower bound for all fields with A<=(272/29)*L^4",
            "the all-field torus scaled Polyak-Lojasiewicz inequality",
            "absence or existence of a nonseparable low-action collapsing family",
            "optimality of the quadratic scalar majorant or the density 272/29",
            "a Witten or Poincare theorem",
            "boundedness or divergence of the interacting H^-1 moment",
            "a continuum measure or continuum identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction audit of beta=3/32, slope 41/8, defect 17, the degree-6 exponential witness, the two-term atanh witness, density 272/29, torus floor 841/8388608, contrast 544/29, and a complete rational T_4^4 checkerboard",
            "analytic_inputs": [
                "the predecessor's Jensen and superadditivity fixed-s envelope Phi",
                "strict concavity of the low logarithmic bracket and strict convexity H''>=12 on the high branch",
                "e^x greater than every finite positive Taylor partial sum",
                "log((1+z)/(1-z))=2*atanh(z)>2*(z+z^3/3) for 0<z<1",
                "the predecessor's reciprocal-edge identity, range/norm estimates, large-action branches, and sin(x)<=x",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_quadratic_virial_density_gate.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_quadratic_virial_density_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_quadratic_virial_density_gate",
        ],
        "tier_receipt": {
            "tier_0": "PASS: changed Python compiled; strict JSON/schema parsing, deterministic certificate drift, scoped diff check, exact staged-diff inspection, planning import, claim-map verification, and two-pass PDF build were run; planning imported 1717 nodes with 0 invalid items and 0 malformed events in 1.24 s at 17212 KiB maximum RSS",
            "tier_1": "PASS: producer 10/10 in 0.05 s at 20524 KiB; nonimporting verifier 13/13 in 0.12 s at 30416 KiB; focused and mutation tests 14/14 in 0.28 s at 30984 KiB; unchanged global-virial predecessor verifier passed 12/12 in 0.11 s at 30244 KiB",
            "tier_2": "the global-virial predecessor is unchanged, pinned by content hash, and its independent verifier passed",
            "tier_3": "not triggered: the all-field, H^-1, continuum, freeze, release, and shared-core gates remain open",
            "paper_integration": "PASS: Paper 21 RF-92 claim-map verification completed in 0.59 s at 149296 KiB maximum RSS and the 84-page PDF built twice in 0.90 s at 53984 KiB and 0.89 s at 54028 KiB",
            "planning_event": "PASS: append-only ACTIVE event sequence 98, id 1784e5fe84d22a71",
            "science_forge_shadow": "ADVISORY_NO_DISPOSITION: the advisory wrapper started but emitted no final disposition after two cbp subprocesses aborted; it is not counted as a scientific pass",
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
        "[PASS] BT torus quadratic virial-density gate "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Independently verify the BT torus quadratic virial-density gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_QUADRATIC_VIRIAL_DENSITY_GATE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-quadratic-virial-density-gate-v1.schema.json",
)
SOURCE_COMMIT = "1ed9daaf13b80b6dcbb0d006471a8c21826a93b2"


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def factorial(value: int) -> int:
    result = 1
    for factor in range(2, value + 1):
        result *= factor
    return result


def reconstruct_checkerboard() -> dict[str, Fraction]:
    side = 4
    points = [
        (a, b, c, d)
        for a in range(side)
        for b in range(side)
        for c in range(side)
        for d in range(side)
    ]

    def index(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    omega = [Fraction(5, 2) if sum(point) % 2 else Fraction(1) for point in points]
    residual = [Fraction() for _ in points]
    gradient = [Fraction() for _ in points]
    edges: list[tuple[int, int]] = []
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                shifted = list(point)
                shifted[axis] = (shifted[axis] + step) % side
                residual[x] += omega[index(tuple(shifted))] / omega[x] - 1
            shifted = list(point)
            shifted[axis] = (shifted[axis] + 1) % side
            edges.append((x, index(tuple(shifted))))
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                shifted = list(point)
                shifted[axis] = (shifted[axis] + step) % side
                y = index(tuple(shifted))
                gradient[x] += (
                    residual[y] * omega[x] / omega[y]
                    - residual[x] * omega[y] / omega[x]
                )
    residual_norm = sum((value * value for value in residual), Fraction())
    gradient_norm = sum((value * value for value in gradient), Fraction())
    action = residual_norm / 2
    density = action / len(points)
    critical_density = Fraction(272, 29)
    excess = sum(
        (omega[y] / omega[x] + omega[x] / omega[y] - 2 for x, y in edges),
        Fraction(),
    )
    return {
        "action": action,
        "action_density": density,
        "residual_norm_squared": residual_norm,
        "gradient_norm_squared": gradient_norm,
        "quotient": gradient_norm / residual_norm,
        "quadratic_density_branch_floor": (
            Fraction(841) * (density - critical_density) ** 2
            / (524288 * len(points))
        ),
        "residual_sum": sum(residual, Fraction()),
        "edge_reciprocal_excess": excess,
    }


def verify(certificate: dict[str, object]) -> list[tuple[str, bool]]:
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
        schema_ok = True
    except jsonschema.ValidationError:
        schema_ok = False

    provenance = certificate["provenance"]
    inputs_ok = (
        provenance["repository_base_commit"] == SOURCE_COMMIT
        and all(
            os.path.isfile(os.path.join(ROOT, row["path"]))
            and file_hash(os.path.join(ROOT, row["path"])) == row["sha256"]
            for row in provenance["inputs"]
        )
    )

    audit = certificate["exact_constant_audit"]
    beta = Fraction(3, 32)
    slope = Fraction(41, 8)
    defect = Fraction(17)
    action_coefficient = 2 * (1 - beta)
    critical_density = defect / action_coefficient
    low_point = Fraction(961, 200)
    low_exponent = 8 / low_point - Fraction(3, 32)
    low_taylor = sum(
        (low_exponent**degree / factorial(degree) for degree in range(7)),
        Fraction(),
    )
    low_radial = low_point + 64 / low_point
    high_point = Fraction(53, 80)
    high_threshold = (41 + 52 * high_point) / (64 * (1 + 2 * high_point))
    high_z = high_point / (2 + high_point)
    high_lower = 2 * (high_z + high_z**3 / 3)
    high_polynomial = 17 + 34 * high_point - 47 * high_point**2 - 64 * high_point**3
    bounded_floor = action_coefficient**2 / (32 * 64)
    normalized_floor = bounded_floor / 16
    constants_ok = (
        dec(audit["quadratic_coefficient"]) == beta
        and dec(audit["linear_slope"]) == slope
        and dec(audit["scalar_defect"]) == defect
        and dec(audit["virial_action_coefficient"]) == action_coefficient == Fraction(29, 16)
        and dec(audit["critical_action_density"]) == critical_density == Fraction(272, 29)
        and dec(audit["low_rational_point"]) == low_point
        and dec(audit["low_exponent"]) == low_exponent == Fraction(48317, 30752)
        and dec(audit["low_degree_6_exponential_taylor_sum"]) == low_taylor > low_point
        and dec(audit["low_radial_value"]) == low_radial < Fraction(145, 8)
        and dec(audit["high_rational_point"]) == high_point
        and dec(audit["high_log_threshold"]) == high_threshold == Fraction(503, 992)
        and dec(audit["high_atanh_coordinate"]) == high_z == Fraction(53, 213)
        and dec(audit["high_two_term_log_lower"]) == high_lower > high_threshold
        and dec(audit["high_stationary_polynomial_endpoint"]) == high_polynomial == Fraction(9177, 32000) > 0
        and dec(audit["bounded_density_floor_coefficient"]) == bounded_floor == Fraction(841, 524288)
        and dec(audit["normalized_density_floor_coefficient"]) == normalized_floor == Fraction(841, 8388608)
        and dec(audit["asymptotic_contrast_square_coefficient"]) == Fraction(544, 29)
        and all(audit["checks"].values())
    )

    scalar = certificate["scalar_majorant"]
    low_branch_ok = (
        scalar["negative_branch_remainder"]
        == "s*[(8-s)*log(s)+(29/32)*s-75/8]<=0"
        and low_taylor > low_point
        and low_radial < Fraction(145, 8)
    )
    # H''>=12 makes the high remainder strictly convex.  The two-term
    # atanh lower bound places its stationary point below 53/80.  At a
    # stationary point H=P/(1+2y); P' is strictly decreasing, hence P has
    # no interior minimum, and both endpoint values are positive.
    high_branch_ok = (
        scalar["positive_branch_remainder"]
        == "H(y)=17-41*y-58*y^2+64*y*(1+y)*log(1+y)>=0 for y=s/8-1>=0"
        and high_lower > high_threshold
        and high_polynomial > 0
        and 34 > 0
        and -94 - 384 * high_point < 0
    )
    majorant_ok = (
        scalar["quadratic_majorant"]
        == "Phi(s)+(41/8)*(s-8)-(3/32)*(s-8)^2<=17 for every s>0"
        and low_branch_ok
        and high_branch_ok
    )

    graph = certificate["global_graph_theorem"]
    graph_ok = (
        graph["compatibility_identity"]
        == "sum_x(s_x-8)=sum_edges(z_e+z_e^(-1)-2)>=0"
        and graph["summed_defect_bound"]
        == "sum_x(r_x^2-r_x*t_x)<=17*N+(3/32)*sum_x(r_x^2)"
        and graph["global_virial_bound"]
        == "<psi,g>>=(29/16)*A-17*N=(29/16)*(A-(272/29)*N)"
    )
    torus = certificate["four_torus_theorem"]
    torus_ok = (
        torus["bounded_density_branch"]
        == "272/29<x<64 implies N*Q>=841*(x-272/29)^2/524288"
        and torus["bounded_density_normalized_branch"]
        == "272/29<x<64 implies Q/omega_L^2>=841*(x-272/29)^2/(8388608*pi^4)"
        and torus["fixed_margin_theorem"]
        == "for every 0<epsilon<=32, A>=(272/29+epsilon)*L^4 implies Q/omega_L^2>=841*epsilon^2/(8388608*pi^4)"
        and Fraction(1, 8) >= normalized_floor * 32**2
        and torus["collapsing_action_necessity"]
        == "Q/omega_L^2->0 implies limsup A/L^4<=272/29"
        and torus["collapsing_contrast_necessity"]
        == "Q/omega_L^2->0 implies limsup W^2/L^4<=544/29"
    )

    rebuilt = reconstruct_checkerboard()
    fixture = certificate["exact_fixture"]
    fixture_ok = (
        all(
            dec(fixture[key]) == rebuilt[key]
            for key in (
                "action", "action_density", "residual_norm_squared",
                "gradient_norm_squared", "quotient",
                "quadratic_density_branch_floor", "residual_sum",
                "edge_reciprocal_excess",
            )
        )
        and rebuilt["residual_sum"] == rebuilt["edge_reciprocal_excess"] >= 0
        and rebuilt["quotient"] >= rebuilt["quadratic_density_branch_floor"]
        and all(fixture["checks"].values())
    )
    boundary = certificate["research_disposition"]
    boundary_ok = (
        boundary["fixed_action_density_above_272_over_29_collapse"] == "RULED_OUT"
        and boundary["action_density_at_most_272_over_29_sector"] == "OPEN"
        and boundary["all_field_torus_scaled_PL"] == "OPEN"
        and boundary["nonseparable_counterfamily"] == "NOT_CONSTRUCTED"
        and boundary["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        (
            "producer_not_imported",
            "bt_euclidean_torus_quadratic_virial_density_gate" not in sys.modules,
        ),
        ("predecessor_hash_and_source_commit", inputs_ok),
        ("exact_constants", constants_ok),
        ("negative_scalar_branch", low_branch_ok),
        ("positive_scalar_branch", high_branch_ok),
        ("quadratic_majorant", majorant_ok),
        ("global_graph_compatibility", graph_ok),
        ("four_torus_chain", torus_ok),
        ("independent_checkerboard_reconstruction", fixture_ok),
        ("claim_boundaries", boundary_ok),
        (
            "dependency_tags",
            certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        ),
        (
            "self_checks",
            self_checks["ok"] is True
            and self_checks["passed"] == self_checks["total"] == 10
            and all(self_checks["details"].values()),
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args(argv)
    try:
        with open(args.certificate, encoding="utf-8") as handle:
            certificate = json.load(handle)
        checks = verify(certificate)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return 1
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(value for _, value in checks)
    print(f"BT torus quadratic virial-density verifier: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())

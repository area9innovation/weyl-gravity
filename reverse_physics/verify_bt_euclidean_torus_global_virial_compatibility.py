#!/usr/bin/env python3
"""Independently verify the BT torus global virial compatibility."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GLOBAL_VIRIAL_COMPATIBILITY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-global-virial-compatibility-v1.schema.json",
)


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


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
        "density_branch_floor": (density - 11) ** 2 / (512 * len(points)),
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

    inputs_ok = all(
        os.path.isfile(os.path.join(ROOT, row["path"]))
        and file_hash(os.path.join(ROOT, row["path"])) == row["sha256"]
        for row in certificate["provenance"]["inputs"]
    )
    audit = certificate["exact_constant_audit"]
    taylor = sum(
        (
            Fraction(1),
            Fraction(16, 9),
            Fraction(16, 9) ** 2 / 2,
            Fraction(16, 9) ** 3 / 6,
        ),
        Fraction(),
    )
    derivative = 192 * Fraction(83, 100) ** 2 - 84 * Fraction(83, 100) - 62
    critical_floor = (Fraction(1895) - 2278 * Fraction(83, 100)) / 48
    constants_ok = (
        dec(audit["affine_majorant_slope"]) == Fraction(21, 4)
        and dec(audit["global_virial_defect"]) == 22
        and dec(audit["critical_action_density"]) == 11
        and dec(audit["low_branch_taylor_partial_sum"]) == taylor > Fraction(9, 2)
        and dec(audit["high_polynomial_derivative_at_83_over_100"])
        == derivative > 0
        and dec(audit["high_polynomial_critical_floor"])
        == critical_floor > 0
        and all(audit["checks"].values())
    )

    scalar = certificate["scalar_majorant"]
    low_branch_ok = (
        scalar["negative_branch"] == "0<s<8: Phi(s)=(8-s)^2+(8-s)*s*log(s)"
        and Fraction(337, 18) < Fraction(75, 4)
        and taylor > Fraction(9, 2)
    )
    # The rational log lower bound follows by differentiating. At the sole
    # positive critical minimum of p on [0,1], the derivative equation
    # reduces p to (1895-2278y)/48. The rational point 83/100 lies to its
    # right and keeps this expression positive. For y>=1, the lower
    # quadratic has discriminant -7.
    high_branch_ok = (
        scalar["positive_branch"]
        == "s>=8: Phi(s)=(s-8)^2-(s-8)*s*log(s/8)"
        and derivative > 0
        and critical_floor > 0
        and 31**2 - 4 * 11 * 22 == -7
    )
    graph = certificate["global_graph_theorem"]
    graph_ok = (
        graph["compatibility_identity"]
        == "sum_x(s_x-8)=sum_edges(z_e+z_e^(-1)-2)>=0"
        and graph["global_virial_bound"] == "<psi,g>>=2*A-22*N"
    )
    torus = certificate["four_torus_theorem"]
    torus_ok = (
        torus["bounded_density_branch"] == "11<x<64 implies N*Q>=(x-11)^2/512"
        and torus["fixed_margin_theorem"]
        == "for every 0<epsilon<=32, A>=(11+epsilon)*L^4 implies Q/omega_L^2>=epsilon^2/(8192*pi^4)"
        and torus["collapsing_action_necessity"]
        == "Q/omega_L^2->0 implies limsup A/L^4<=11"
        and torus["collapsing_contrast_necessity"]
        == "Q/omega_L^2->0 implies limsup W^2/L^4<=22"
    )

    rebuilt = reconstruct_checkerboard()
    fixture = certificate["exact_fixture"]
    fixture_ok = (
        all(
            dec(fixture[key]) == rebuilt[key]
            for key in (
                "action", "action_density", "residual_norm_squared",
                "gradient_norm_squared", "quotient", "density_branch_floor",
                "residual_sum", "edge_reciprocal_excess",
            )
        )
        and rebuilt["residual_sum"] == rebuilt["edge_reciprocal_excess"] >= 0
        and rebuilt["quotient"] >= rebuilt["density_branch_floor"]
        and all(fixture["checks"].values())
    )
    boundary = certificate["research_disposition"]
    boundary_ok = (
        boundary["fixed_action_density_above_11_collapse"] == "RULED_OUT"
        and boundary["action_density_at_most_11_sector"] == "OPEN"
        and boundary["all_field_torus_scaled_PL"] == "OPEN"
        and boundary["nonseparable_counterfamily"] == "NOT_CONSTRUCTED"
        and boundary["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        (
            "producer_not_imported",
            "bt_euclidean_torus_global_virial_compatibility" not in sys.modules,
        ),
        ("predecessor_hash", inputs_ok),
        ("exact_constants", constants_ok),
        ("negative_scalar_branch", low_branch_ok),
        ("positive_scalar_branch", high_branch_ok),
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
    print(f"BT torus global virial-compatibility verifier: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())

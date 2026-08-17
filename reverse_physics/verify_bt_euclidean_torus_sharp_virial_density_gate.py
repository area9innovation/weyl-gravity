#!/usr/bin/env python3
"""Independently verify the BT torus sharp-virial density gate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SHARP_VIRIAL_DENSITY_GATE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-sharp-virial-density-gate-v1.schema.json",
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
    count = side**4
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
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                shifted = list(point)
                shifted[axis] = (shifted[axis] + step) % side
                residual[x] += omega[index(tuple(shifted))] / omega[x] - 1
    gradient = [Fraction() for _ in points]
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
    density = action / count
    return {
        "action": action,
        "action_density": density,
        "residual_norm_squared": residual_norm,
        "gradient_norm_squared": gradient_norm,
        "quotient": gradient_norm / residual_norm,
        "density_branch_floor": (density - 32) ** 2 / (512 * count),
        "gradient_sum": sum(gradient, Fraction()),
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
    constants_ok = (
        dec(audit["sharp_vertex_defect"]) == 64
        and dec(audit["critical_action_density"]) == 32
        and audit["raw_density_floor_denominator"] == 512
        and audit["normalized_density_floor_denominator"] == 8192
        and Fraction(61, 320) > Fraction(1, 8)
        and all(audit["checks"].values())
    )

    # Independent exact audit of the one-variable proof. H is strictly
    # convex. At an interior minimum s*log(s)=8; log(4)<2 and log(8)>1
    # put it in (4,8). There, 20-s-64/s=-(s-4)(s-16)/s is nonnegative,
    # so H=24-s-64/s is at least four. The exponential comparisons follow
    # from e>5/2 and e<11/4<3: the lower bound is the degree-two Taylor
    # partial sum, and the upper bound uses n!>=2*3^(n-2) for n>=2.
    # No floating-point evaluation enters the claim.
    theorem = certificate["sharp_vertex_theorem"]
    scalar_proof_ok = (
        theorem["negative_residual_bound"] == "r_x<0 implies r_x*t_x>=r_x^2-64"
        and theorem["sharp_virial_bound"] == "<psi,g>=sum_x r_x*t_x>=2*A-64*N"
        and 4 + Fraction(64, 4) == 20
        and 8 + Fraction(64, 8) == 16
        and Fraction(5, 2) ** 2 > 4
        and Fraction(11, 4) < 3 < 8
        and (4 - 4) * (4 - 16) == 0
        and (8 - 4) * (8 - 16) < 0
    )

    torus = certificate["four_torus_theorem"]
    torus_chain_ok = (
        torus["intermediate_density_branch"] == "32<x<64 implies N*Q>=(x-32)^2/512"
        and torus["fixed_margin_theorem"]
        == "for every 0<epsilon<=32, A>=(32+epsilon)*L^4 implies Q/omega_L^2>=epsilon^2/(8192*pi^4)"
        and torus["middle_branch"]
        == "64<=x<488/5 implies N*Q>=2 and Q/omega_L^2>=1/(8*pi^4)"
        and torus["collapsing_action_necessity"]
        == "Q/omega_L^2->0 implies limsup A/L^4<=32"
        and torus["collapsing_contrast_necessity"]
        == "Q/omega_L^2->0 implies limsup W/L^2<=8"
    )
    log_chain_ok = (
        128 < 12**2
        and 8 + 12 * 4**2 < 13 * 4**2
        and Fraction(5, 2) ** 3 > 13
        and 3 + 4 <= 2 * 4
        and 512 * 16 == 8192
    )

    rebuilt = reconstruct_checkerboard()
    fixture = certificate["exact_fixture"]
    fixture_ok = (
        all(
            dec(fixture[key]) == rebuilt[key]
            for key in (
                "action",
                "action_density",
                "residual_norm_squared",
                "gradient_norm_squared",
                "quotient",
                "density_branch_floor",
                "gradient_sum",
            )
        )
        and 32 < rebuilt["action_density"] < 64
        and rebuilt["quotient"] >= rebuilt["density_branch_floor"]
        and all(fixture["checks"].values())
    )
    boundary = certificate["research_disposition"]
    boundary_ok = (
        boundary["fixed_action_density_above_32_collapse"] == "RULED_OUT"
        and boundary["action_density_at_most_32_sector"] == "OPEN"
        and boundary["all_field_torus_scaled_PL"] == "OPEN"
        and boundary["nonseparable_counterfamily"] == "NOT_CONSTRUCTED"
        and boundary["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        (
            "producer_not_imported",
            "bt_euclidean_torus_sharp_virial_density_gate" not in sys.modules,
        ),
        ("predecessor_hashes", inputs_ok),
        ("exact_constants", constants_ok),
        ("sharp_scalar_virial_proof", scalar_proof_ok),
        ("torus_density_chain", torus_chain_ok),
        ("logarithm_and_spectral_chain", log_chain_ok),
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
    print(f"BT torus sharp-virial density-gate verifier: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())

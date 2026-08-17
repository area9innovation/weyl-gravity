#!/usr/bin/env python3
"""Independently verify the BT torus curvature/cut concentration gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_CURVATURE_CUT_CONCENTRATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-curvature-cut-concentration-v1.schema.json",
)
SOURCE_COMMIT = "1d80094413f2365cff2b9c3c5b7c24292d6d40d4"


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def reconstruct_fixture() -> dict[str, Fraction | int | bool]:
    """Recompute the checkerboard without importing the producer."""

    side = 4
    points = list(product(range(side), repeat=4))

    def index(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    field = [Fraction(1) if sum(point) % 2 == 0 else Fraction(2) for point in points]
    neighbors: list[list[int]] = [[] for _ in points]
    edges: list[tuple[int, int]] = []
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % side
                neighbors[x].append(index(tuple(neighbor)))
            neighbor = list(point)
            neighbor[axis] = (neighbor[axis] + 1) % side
            edges.append((x, index(tuple(neighbor))))

    residual = [
        sum((field[y] / field[x] - 1 for y in neighbors[x]), Fraction())
        for x in range(len(points))
    ]
    curvature = [r / u**2 for r, u in zip(residual, field)]
    gradient = [
        sum(
            (
                residual[y] * field[x] / field[y]
                - residual[x] * field[y] / field[x]
                for y in neighbors[x]
            ),
            Fraction(),
        )
        for x in range(len(points))
    ]
    mean = sum(curvature, Fraction()) / len(points)
    centered = [value - mean for value in curvature]
    residual_norm = sum((value**2 for value in residual), Fraction())
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    centered_norm = sum((value**2 for value in centered), Fraction())
    energy = sum(
        (
            field[x] * field[y] * (curvature[x] - curvature[y]) ** 2
            for x, y in edges
        ),
        Fraction(),
    )
    pairing = sum((h * g for h, g in zip(curvature, gradient)), Fraction())
    low = [x for x, value in enumerate(field) if value <= 1]
    high = [x for x, value in enumerate(field) if value > 1]
    low_residual_norm = sum((residual[x] ** 2 for x in low), Fraction())
    cut_flux = sum((gradient[x] for x in high), Fraction())
    boundary_flux = Fraction()
    crossing_edges = 0
    for x, y in edges:
        if field[x] <= 1 < field[y]:
            low_x, high_y = x, y
        elif field[y] <= 1 < field[x]:
            low_x, high_y = y, x
        else:
            continue
        crossing_edges += 1
        boundary_flux += (
            residual[low_x] * field[high_y] / field[low_x]
            - residual[high_y] * field[low_x] / field[high_y]
        )
    omega = Fraction(2)
    return {
        "vertices": len(points),
        "low_vertices": len(low),
        "high_vertices": len(high),
        "crossing_edges": crossing_edges,
        "residual_norm_squared": residual_norm,
        "gradient_norm_squared": gradient_norm,
        "curvature_mean": mean,
        "centered_curvature_norm_squared": centered_norm,
        "weighted_curvature_energy": energy,
        "curvature_gradient_pairing": pairing,
        "omega_L": omega,
        "poincare_lower_side": omega * centered_norm,
        "spectral_flatness_squared_side": omega**2 * centered_norm,
        "low_residual_norm_squared": low_residual_norm,
        "low_residual_fraction": low_residual_norm / residual_norm,
        "cut_flux": cut_flux,
        "boundary_current_flux": boundary_flux,
        "exact_cut_quotient_floor": Fraction(len(points)) * cut_flux**2
        / (len(low) * len(high) * residual_norm),
        "universal_cut_coefficient_without_pi4": cut_flux**2
        / (4 * residual_norm),
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

    provenance = certificate["provenance"]
    provenance_ok = (
        provenance["repository_base_commit"] == SOURCE_COMMIT
        and all(
            os.path.isfile(os.path.join(ROOT, row["path"]))
            and file_hash(os.path.join(ROOT, row["path"])) == row["sha256"]
            for row in provenance["inputs"]
        )
    )
    spectral = certificate["spectral_flatness_theorem"]
    spectral_ok = (
        spectral["energy"]
        == "E=sum_edges c_xy*(h_x-h_y)^2=-<h,g>=-<h-h_bar,g>"
        and spectral["poincare_chain"]
        == "omega_L*||h-h_bar||_2^2<=sum_edges(h_x-h_y)^2<=E<=||h-h_bar||_2*||g||_2"
        and spectral["normalized_flatness"]
        == "||h-h_bar||_2/R<=sqrt(Q/omega_L^2)"
    )
    cut = certificate["height_cut_theorem"]
    cut_ok = (
        cut["boundary_formula"]
        == "Gamma_K=sum_(x outside S_K,y inside S_K,x~y)[r_x*u_y/u_x-r_y*u_x/u_y]"
        and cut["exact_indicator_floor"]
        == "Q>=N*Gamma_K^2/[s_K*(N-s_K)*R^2] for 0<s_K<N"
        and cut["normalized_floor"]
        == "Q/omega_L^2>=Gamma_K^2/(4*pi^4*R^2)"
    )
    combined = certificate["combined_concentration_theorem"]
    combined_ok = (
        combined["mean_bound"]
        == "|h_bar|*sqrt(m_K)/R<=sqrt(F_K)+sqrt(Q/omega_L^2)"
        and combined["macroscopic_low_set_bound"]
        == "if m_K>=theta*N then ||h||_2/R<=sqrt(F_K/theta)+(1+1/sqrt(theta))*sqrt(Q/omega_L^2)"
        and combined["imported_reciprocal_floor"]
        == "Q/omega_L^2>=A*F_K^2/(2*pi^4*K^2)"
    )

    rebuilt = reconstruct_fixture()
    fixture = certificate["exact_fixture"]
    rational_keys = (
        "residual_norm_squared",
        "gradient_norm_squared",
        "curvature_mean",
        "centered_curvature_norm_squared",
        "weighted_curvature_energy",
        "curvature_gradient_pairing",
        "omega_L",
        "poincare_lower_side",
        "spectral_flatness_squared_side",
        "low_residual_norm_squared",
        "low_residual_fraction",
        "cut_flux",
        "boundary_current_flux",
        "exact_cut_quotient_floor",
        "universal_cut_coefficient_without_pi4",
    )
    fixture_ok = (
        all(fixture[key] == rebuilt[key] for key in ("vertices", "low_vertices", "high_vertices", "crossing_edges"))
        and all(dec(fixture[key]) == rebuilt[key] for key in rational_keys)
        and rebuilt["gradient_sum"] == 0
        and rebuilt["weighted_curvature_energy"]
        == -rebuilt["curvature_gradient_pairing"]
        and rebuilt["gradient_norm_squared"]
        >= rebuilt["spectral_flatness_squared_side"]
        and rebuilt["cut_flux"] == rebuilt["boundary_current_flux"]
        and rebuilt["gradient_norm_squared"] / rebuilt["residual_norm_squared"]
        >= rebuilt["exact_cut_quotient_floor"]
        and rebuilt["low_residual_fraction"] == Fraction(4, 5)
        and all(fixture["checks"].values())
    )
    boundary = certificate["research_disposition"]
    boundary_ok = (
        boundary["positive_action_fixed_height_residual_retention"]
        == "RULED_OUT_FOR_COLLAPSE"
        and boundary["nonflat_unweighted_curvature"] == "RULED_OUT_FOR_COLLAPSE"
        and boundary["noncancelling_height_cut_current"]
        == "RULED_OUT_FOR_COLLAPSE"
        and boundary["all_field_torus_scaled_PL"] == "OPEN"
        and boundary["nonseparable_counterfamily"] == "NOT_CONSTRUCTED"
        and boundary["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        (
            "producer_not_imported",
            "bt_euclidean_torus_curvature_cut_concentration" not in sys.modules,
        ),
        ("predecessor_hash_and_source_commit", provenance_ok),
        ("spectral_flatness_chain", spectral_ok),
        ("height_cut_flux_chain", cut_ok),
        ("combined_concentration_chain", combined_ok),
        ("independent_checkerboard_reconstruction", fixture_ok),
        ("claim_boundaries", boundary_ok),
        (
            "dependency_tags",
            certificate["dependency_tags"]
            == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        ),
        (
            "self_checks",
            self_checks["ok"] is True
            and self_checks["passed"] == self_checks["total"] == 9
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
    print(
        "BT torus curvature/cut concentration verifier: "
        f"{passed}/{len(checks)} checks passed"
    )
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())

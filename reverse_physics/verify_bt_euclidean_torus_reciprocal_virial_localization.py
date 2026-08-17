#!/usr/bin/env python3
"""Independently verify the BT reciprocal-virial localization gate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_RECIPROCAL_VIRIAL_LOCALIZATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-reciprocal-virial-localization-v1.schema.json",
)
SOURCE_COMMIT = "d467431fa585c9bd60eaaf56eac3536206e6f2bf"


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def reconstruct_fixture() -> dict[str, Fraction]:
    side = 4
    points = list(product(range(side), repeat=4))

    def index(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    field = [Fraction(1) if sum(point) % 2 == 0 else Fraction(2) for point in points]
    residual = [Fraction() for _ in points]
    gradient = [Fraction() for _ in points]
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % side
                residual[x] += field[index(tuple(neighbor))] / field[x] - 1
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % side
                y = index(tuple(neighbor))
                gradient[x] += (
                    residual[y] * field[x] / field[y]
                    - residual[x] * field[y] / field[x]
                )
    inverse = [1 / value for value in field]
    inverse_mean = sum(inverse, Fraction()) / len(points)
    centered = [value - inverse_mean for value in inverse]
    residual_norm = sum((value**2 for value in residual), Fraction())
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    inverse_variance = sum((value**2 for value in centered), Fraction())
    moment = sum((r * r / u for r, u in zip(residual, field)), Fraction())
    pairing = sum((g * value for g, value in zip(gradient, centered)), Fraction())
    action = residual_norm / 2
    return {
        "vertices": Fraction(len(points)),
        "action": action,
        "residual_norm_squared": residual_norm,
        "gradient_norm_squared": gradient_norm,
        "inverse_mean": inverse_mean,
        "inverse_variance": inverse_variance,
        "reciprocal_residual_moment": moment,
        "reciprocal_fraction_eta": moment / residual_norm,
        "gradient_centered_inverse_pairing": pairing,
        "quotient": gradient_norm / residual_norm,
        "exact_cauchy_floor": moment**2 / (residual_norm * inverse_variance),
        "popoviciu_floor": 4 * moment**2 / (len(points) * residual_norm),
        "gradient_sum": sum(gradient, Fraction()),
        "centered_sum": sum(centered, Fraction()),
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
    graph = certificate["exact_graph_theorem"]
    graph_ok = (
        graph["inverse_direction_identity"] == "(Jv)_x=-r_x/u_x"
        and graph["pairing_identity"] == "<g,v-v_bar>=<g,v>=<r,Jv>=-B"
        and graph["exact_quotient_floor"]
        == "Q=||g||_2^2/R^2>=B^2/(R^2*||v-v_bar||_2^2)"
        and graph["popoviciu_floor"]
        == "||v-v_bar||_2^2<=N/4 and therefore Q>=4*B^2/(N*R^2)=8*eta^2*A/N"
    )
    torus = certificate["four_torus_theorem"]
    torus_ok = (
        torus["free_scale_comparison"] == "omega_L^2<=16*pi^4/N"
        and torus["normalized_floor"] == "Q/omega_L^2>=eta^2*A/(2*pi^4)"
        and torus["threshold_floor"]
        == "Q/omega_L^2>=A*F_K^2/(2*pi^4*K^2)"
        and torus["collapsing_necessity"]
        == "Q/omega_L^2->0 implies sqrt(A)*F_K/K->0 for every chosen threshold K>=1"
        and torus["fixed_threshold_corollary"]
        == "if liminf A>0 and K is fixed, collapse implies F_K->0"
        and torus["extensive_action_corollary"]
        == "if A>=a*L^4 with fixed a>0 and K is fixed, collapse implies F_K=o(L^-2)"
    )

    rebuilt = reconstruct_fixture()
    fixture = certificate["exact_fixture"]
    rational_keys = (
        "action",
        "residual_norm_squared",
        "gradient_norm_squared",
        "inverse_mean",
        "inverse_variance",
        "reciprocal_residual_moment",
        "reciprocal_fraction_eta",
        "gradient_centered_inverse_pairing",
        "quotient",
        "exact_cauchy_floor",
        "popoviciu_floor",
    )
    fixture_ok = (
        fixture["vertices"] == rebuilt["vertices"]
        and all(dec(fixture[key]) == rebuilt[key] for key in rational_keys)
        and rebuilt["gradient_sum"] == 0
        and rebuilt["centered_sum"] == 0
        and rebuilt["gradient_centered_inverse_pairing"]
        == -rebuilt["reciprocal_residual_moment"]
        and rebuilt["quotient"] == rebuilt["exact_cauchy_floor"]
        and rebuilt["quotient"] >= rebuilt["popoviciu_floor"]
        and rebuilt["reciprocal_fraction_eta"] == Fraction(9, 10)
        and rebuilt["action"] == 20 * rebuilt["vertices"]
        and all(fixture["checks"].values())
    )
    scout = certificate["numerical_scout_disposition"]
    scout_boundary_ok = (
        scout["status"] == "HYPOTHESIS_GENERATION_ONLY_NOT_CERTIFICATE_EVIDENCE"
        and scout["tool"]
        == "reverse_physics/bt_euclidean_torus_nonseparable_continuation_scout.py"
        and "no floating-point minimum is used" in scout["scientific_use"]
    )
    boundary = certificate["research_disposition"]
    boundary_ok = (
        boundary["fixed_height_residual_fraction_in_positive_action_collapsing_sequence"]
        == "RULED_OUT"
        and boundary["remaining_counterfamily_shape"]
        == "RESIDUAL_ENERGY_MUST_ESCAPE_TO_DIVERGING_FIELD_SUPERLEVELS_OR_TOTAL_ACTION_MUST_VANISH"
        and boundary["all_field_torus_scaled_PL"] == "OPEN"
        and boundary["nonseparable_counterfamily"] == "NOT_CONSTRUCTED"
        and boundary["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        (
            "producer_not_imported",
            "bt_euclidean_torus_reciprocal_virial_localization" not in sys.modules,
        ),
        ("predecessor_hash_and_source_commit", provenance_ok),
        ("inverse_field_graph_identity", graph_ok),
        ("four_torus_localization_chain", torus_ok),
        ("independent_checkerboard_reconstruction", fixture_ok),
        ("numeric_scout_kept_non_evidentiary", scout_boundary_ok),
        ("claim_boundaries", boundary_ok),
        (
            "dependency_tags",
            certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
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
    print(f"BT reciprocal-virial localization verifier: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())

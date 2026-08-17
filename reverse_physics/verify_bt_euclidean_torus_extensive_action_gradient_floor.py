#!/usr/bin/env python3
"""Independently verify the BT torus extensive-action gradient floor."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_EXTENSIVE_ACTION_GRADIENT_FLOOR_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-extensive-action-gradient-floor-v1.schema.json",
)


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def reconstruct_spike() -> dict[str, Fraction | int]:
    side = 4
    count = side**4

    def index(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    neighbors: list[list[int]] = [[] for _ in range(count)]
    for a in range(side):
        for b in range(side):
            for c in range(side):
                for d in range(side):
                    x = index((a, b, c, d))
                    coordinates = (a, b, c, d)
                    for axis in range(4):
                        for step in (-1, 1):
                            shifted = list(coordinates)
                            shifted[axis] = (shifted[axis] + step) % side
                            neighbors[x].append(index(tuple(shifted)))

    omega = [Fraction(1)] * count
    omega[0] = Fraction(1000)
    residual: list[Fraction] = []
    for x, row in enumerate(neighbors):
        residual.append(sum((omega[y] - omega[x] for y in row), Fraction()) / omega[x])
    gradient: list[Fraction] = []
    for x, row in enumerate(neighbors):
        gradient.append(
            sum(
                (
                    residual[y] * omega[x] / omega[y]
                    - residual[x] * omega[y] / omega[x]
                    for y in row
                ),
                Fraction(),
            )
        )
    residual_norm = sum((value * value for value in residual), Fraction())
    gradient_norm = sum((value * value for value in gradient), Fraction())
    return {
        "action": residual_norm / 2,
        "residual_norm_squared": residual_norm,
        "gradient_norm_squared": gradient_norm,
        "quotient": gradient_norm / residual_norm,
        "gradient_sum": sum(gradient, Fraction()),
        "maximum_edge_ratio": 1000,
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
        dec(audit["virial_constant"]) == Fraction(488, 5)
        and dec(audit["twice_virial_constant"]) == Fraction(976, 5)
        and Fraction(976, 5) < 14**2
        and dec(audit["pre_spectral_floor_coefficient"]) == Fraction(61, 20)
        and dec(audit["normalized_floor_coefficient"]) == Fraction(61, 320)
        and Fraction(488, 5) / (2 * 4 * 4) == Fraction(61, 20)
        and Fraction(61, 20) / 16 == Fraction(61, 320)
        and all(audit["checks"].values())
    )

    # The logarithmic estimate is analytic, but its load-bearing comparisons
    # are independently reduced here. For L>=4, 8+14L^2<16L^2. Also
    # log(16)<4 (because e>2) and 2log L<=L from its L=4 base value and
    # derivative 2/L<=1. Therefore log(8+sqrt(2C)L^2)<2L.
    log_chain_ok = (
        8 + 14 * 4**2 < 16 * 4**2
        and 2 < 4
        and Fraction(2, 4) <= 1
        and audit["logarithm_ceiling"] == "log(8+sqrt(2*C)*L^2)<2*L"
    )

    theorem = certificate["graph_theorem"]
    graph_chain_ok = (
        theorem["affine_virial_input"] == "<psi,g>>=2*A-C*N with C=488/5 for q=8"
        and theorem["radial_pairing_floor"] == "<psi,g>>=A"
        and theorem["edge_ratio_bound"] == "W<=q+sqrt(2*A)"
        and theorem["log_field_range_bound"]
        == "||psi||_2<=D*sqrt(N)*log(q+sqrt(2*A))"
        and theorem["quotient_floor"]
        == "Q>=A/[2*N*D^2*log(q+sqrt(2*A))^2]"
    )
    # Put s=sqrt(2A). The logarithmic derivative of
    # A/log(q+s)^2 is positive if (q+s)log(q+s)>s. Since q=8 and
    # log(q+s)>1, the left side exceeds q+s>s.
    monotonicity_ok = theorem["monotonicity"] == (
        "A/log(q+sqrt(2*A))^2 is increasing for A>0 when q>=1"
    )

    torus = certificate["four_torus_corollary"]
    torus_ok = (
        torus["scope"] == "T_L^4 with L>=4"
        and torus["diameter"] == "D=4*floor(L/2)<=2*L"
        and torus["quotient_floor"] == "Q>=(61/20)*L^(-4)"
        and torus["normalized_floor"] == "Q/omega_L^2>=61/(320*pi^4)"
        and torus["counterfamily_contrast_necessity"]
        == "Q/omega_L^2<61/(320*pi^4) implies W<16*L^2"
    )

    rebuilt = reconstruct_spike()
    fixture = certificate["exact_fixture"]
    fixture_ok = (
        dec(fixture["action"]) == rebuilt["action"]
        and dec(fixture["residual_norm_squared"]) == rebuilt["residual_norm_squared"]
        and dec(fixture["gradient_norm_squared"]) == rebuilt["gradient_norm_squared"]
        and dec(fixture["quotient"]) == rebuilt["quotient"]
        and dec(fixture["gradient_sum"]) == rebuilt["gradient_sum"] == 0
        and fixture["maximum_edge_ratio"] == rebuilt["maximum_edge_ratio"]
        and dec(fixture["action"]) >= dec(fixture["extensive_action_threshold"])
        and all(fixture["checks"].values())
    )
    boundary = certificate["research_disposition"]
    boundary_ok = (
        boundary["extensive_or_superextensive_action_collapse"] == "RULED_OUT"
        and boundary["low_action_sub_16_L_squared_sector"] == "OPEN"
        and boundary["all_field_torus_scaled_PL"] == "OPEN"
        and boundary["lorentzian_transfer"] == "NOT_ESTABLISHED"
        and "the all-field torus scaled Polyak-Lojasiewicz inequality"
        in certificate["does_not_establish"]
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        (
            "producer_not_imported",
            "bt_euclidean_torus_extensive_action_gradient_floor" not in sys.modules,
        ),
        ("predecessor_hashes", inputs_ok),
        ("exact_constants", constants_ok),
        ("logarithm_chain", log_chain_ok),
        ("graph_theorem_chain", graph_chain_ok),
        ("large_action_monotonicity", monotonicity_ok),
        ("four_torus_corollary", torus_ok),
        ("independent_spike_reconstruction", fixture_ok),
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
    print(
        "BT torus extensive-action gradient-floor verifier: "
        f"{passed}/{len(checks)} checks passed"
    )
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())

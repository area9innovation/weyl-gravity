#!/usr/bin/env python3
"""Non-importing verifier for the BT expected-Hessian axial symbol."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from fractions import Fraction
from itertools import product

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_EXPECTED_HESSIAN_AXIAL_SYMBOL_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-expected-hessian-axial-symbol-v1.schema.json",
)
OBSERVATION_REL = (
    "reverse_physics/data/bt_euclidean_hessian_symbol_observations_v1.json"
)
EXPECTED_INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RIEMANNIAN_ELECTRICAL_WITTEN_BRIDGE_V1.json",
    OBSERVATION_REL,
]


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_fixture() -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction]:
    length = 6
    dimensions = 2
    degree = 4
    points = list(product(range(length), repeat=dimensions))
    number = {point: index for index, point in enumerate(points)}
    profile = (Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2), Fraction(1), Fraction(1))
    omega = tuple(profile[point[0]] for point in points)

    def move(point, axis, step=1):
        result = list(point)
        result[axis] = (result[axis] + step) % length
        return tuple(result)

    neighbors = tuple(
        tuple(number[move(point, axis, step)]
              for axis in range(dimensions) for step in (-1, 1))
        for point in points
    )
    weights = tuple(
        tuple(omega[target] / omega[source] for target in row)
        for source, row in enumerate(neighbors)
    )
    residual = tuple(sum(row, Fraction()) - degree for row in weights)

    def column(selected):
        return tuple(
            -sum(weights[source], Fraction())
            if source == selected
            else sum((weight for weight, target in zip(weights[source], row)
                      if target == selected), Fraction())
            for source, row in enumerate(neighbors)
        )

    def hessian(left, right):
        left_column = column(left)
        right_column = column(right)
        value = sum((a * b for a, b in zip(left_column, right_column)), Fraction())
        for source, row in enumerate(neighbors):
            for weight, target in zip(weights[source], row):
                value += residual[source] * weight * (
                    int(left == target) - int(left == source)
                ) * (
                    int(right == target) - int(right == source)
                )
        return value

    b_values = []
    c_values = []
    d_values = []
    for left, point in enumerate(points):
        for axis in range(dimensions):
            b_values.append(hessian(left, number[move(point, axis)]))
            c_values.append(hessian(left, number[move(point, axis, 2)]))
        for first_sign in (-1, 1):
            for second_sign in (-1, 1):
                diagonal = move(move(point, 0, first_sign), 1, second_sign)
                d_values.append(hessian(left, number[diagonal]))

    average = lambda values: sum(values, Fraction()) / len(values)
    b = average(b_values)
    c = average(c_values)
    d = average(d_values)
    alpha = -(b + 4 * c + 2 * d)
    r2 = average([value * value for value in residual])
    return b, c, d, alpha, r2


def independent_observations() -> list[dict[str, float | int]]:
    with open(os.path.join(ROOT, OBSERVATION_REL), encoding="utf-8") as handle:
        observations = json.load(handle)
    rows = []
    for run in observations["runs"]:
        row: dict[str, float | int] = {
            "length": run["lattice"]["length"],
            "sample_count": run["recorded_samples"],
            "action_recompute_residual": run["final_action_recompute_residual"],
        }
        for name in ("b", "c", "d", "alpha", "action_density"):
            block_means = [
                block[f"sum_{name}"] / block["sample_count"]
                for block in run["blocks"]
            ]
            mean = math.fsum(block_means) / len(block_means)
            center = mean
            variance = math.fsum(
                (value - center) ** 2 for value in block_means
            ) / (len(block_means) - 1)
            row[f"mean_{name}"] = mean
            row[f"blocked_standard_error_{name}"] = math.sqrt(
                variance / len(block_means)
            )
        rows.append(row)
    return rows


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(cert)
    )
    inputs = cert.get("provenance", {}).get("inputs", [])
    checks["provenance_hashes_current"] = (
        [item.get("path") for item in inputs] == EXPECTED_INPUTS
        and all(item.get("sha256") == file_hash(item["path"]) for item in inputs)
    )

    b, c, d, alpha, r2 = independent_fixture()
    public_fixture = cert.get("exact_fixture", {})
    checks["independent_exact_hessian_fixture"] = (
        b == Fraction(-133, 12)
        and c == Fraction(59, 48)
        and d == Fraction(7, 3)
        and alpha == Fraction(3, 2)
        and r2 == Fraction(13, 12)
        and dec(public_fixture.get("b", {})) == b
        and dec(public_fixture.get("c", {})) == c
        and dec(public_fixture.get("d", {})) == d
        and dec(public_fixture.get("alpha", {})) == alpha
        and dec(public_fixture.get("residual_square_density", {})) == r2
    )

    bounds = cert.get("uniform_full_gibbs_bounds", {})
    q = Fraction(8)
    residual_bound = 2 * Fraction(1222, 25)
    s2 = 2 * q * q + 2 * residual_bound
    b_bound = 11 * q * q + 5 * residual_bound
    c_bound = s2 / 4
    d_bound = s2 / 2
    alpha_bound = b_bound + 4 * c_bound + 6 * d_bound
    symbol_bound = alpha_bound + 4 * c_bound
    checks["independent_uniform_constants"] = (
        residual_bound == Fraction(2444, 25)
        and s2 == Fraction(8088, 25)
        and b_bound == Fraction(5964, 5)
        and c_bound == Fraction(2022, 25)
        and d_bound == Fraction(4044, 25)
        and alpha_bound == Fraction(62172, 25)
        and symbol_bound == Fraction(14052, 5)
        and dec(bounds.get("residual_second_moment", {})) == residual_bound
        and dec(bounds.get("s_second_moment", {})) == s2
        and dec(bounds.get("absolute_b", {})) == b_bound
        and dec(bounds.get("upper_c", {})) == c_bound
        and dec(bounds.get("upper_d", {})) == d_bound
        and dec(bounds.get("absolute_alpha", {})) == alpha_bound
        and dec(bounds.get("C_H", {})) == symbol_bound
        and dec(bounds.get("psi_constant", {})) == Fraction(1, 17565)
        and dec(bounds.get("phi_constant", {})) == Fraction(5, 14052)
    )

    symbol = cert.get("exact_symbol_theorem", {})
    checks["symbol_and_ward_boundary"] = (
        symbol.get("four_dimensions") == "alpha_L=-(b_L+4*c_L+6*d_L)"
        and symbol.get("omega") == "2*(1-cos(p))"
        and "alpha_L*omega(p)+c_L*omega(p)^2"
        in symbol.get("axial_symbol_general_D", "")
        and "lambda^(-2)" in symbol.get("gibbs_ward", "")
        and "liminf alpha_L>=0" in symbol.get("positivity_consequence", "")
    )

    observed = independent_observations()
    public_rows = cert.get("finite_volume_diagnostic", {}).get("summaries", [])
    numeric_match = len(public_rows) == len(observed) == 2
    if numeric_match:
        for expected, public in zip(observed, public_rows):
            numeric_match &= expected["length"] == public.get("length")
            for name in ("b", "c", "d", "alpha", "action_density"):
                numeric_match &= abs(
                    expected[f"mean_{name}"] - public.get(f"mean_{name}", math.inf)
                ) < 1.0e-14
                numeric_match &= abs(
                    expected[f"blocked_standard_error_{name}"]
                    - public.get(f"blocked_standard_error_{name}", math.inf)
                ) < 1.0e-14
    checks["observation_reduction_and_hash"] = (
        numeric_match
        and cert.get("finite_volume_diagnostic", {}).get("observation_sha256")
        == file_hash(OBSERVATION_REL)
        and all(row["mean_alpha"] > 0.09 for row in observed)
        and abs(observed[0]["mean_alpha"] - observed[1]["mean_alpha"]) < 0.01
        and all(row["action_recompute_residual"] < 1.0e-8 for row in observed)
    )

    disposition = cert.get("method_disposition", {})
    checks["claim_boundary"] = (
        disposition.get("nonzero_infinite_volume_alpha") == "OBSERVED_NOT_PROVED"
        and disposition.get("conditioned_background_score_bound") == "OPEN_SEPARATE_OBJECT"
        and disposition.get("volume_uniform_witten_coercivity") == "OPEN"
        and disposition.get("actual_interacting_h_minus_one_second_moment") == "OPEN"
        and any("LORENTZIAN-CAUSAL" in item for item in cert.get("does_not_establish", []))
    )
    published = cert.get("checks", {})
    checks["producer_checks_consistent"] = (
        published.get("ok") is True
        and published.get("passed") == published.get("total") == 20
        and published.get("failures") == []
        and all(published.get("details", {}).values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    ok = all(checks.values())
    print(
        "BT expected-Hessian axial symbol independent verifier: "
        f"{'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})"
    )
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args()
    return 0 if verify(args.path) else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent verifier for BT tropical gradient escape."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TROPICAL_GRADIENT_ESCAPE_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-tropical-gradient-escape-v1.schema.json",
)


def decode(row: dict[str, int]) -> Fraction:
    return Fraction(row["numerator"], row["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def make_neighbors(shape: tuple[int, ...]) -> list[list[int]]:
    points = list(itertools.product(*(range(length) for length in shape)))
    index = {point: position for position, point in enumerate(points)}
    result: list[list[int]] = []
    for point in points:
        row: list[int] = []
        for axis, length in enumerate(shape):
            for step in (-1, 1):
                other = list(point)
                other[axis] = (other[axis] + step) % length
                row.append(index[tuple(other)])
        result.append(row)
    return result


def direct_norms(
    exponents: tuple[int, ...], neighbors: list[list[int]], base: int = 2
) -> tuple[Fraction, Fraction, Fraction]:
    omega = [Fraction(base**value) if value >= 0 else Fraction(1, base ** (-value)) for value in exponents]
    residual = [
        sum((omega[other] / omega[site] for other in row), Fraction(0))
        - len(row)
        for site, row in enumerate(neighbors)
    ]
    gradient = [Fraction(0) for _ in omega]
    for site, row in enumerate(neighbors):
        for other in row:
            current = residual[site] * omega[other] / omega[site]
            gradient[other] += current
            gradient[site] -= current
    return (
        sum((value * value for value in residual), Fraction(0)),
        sum((value * value for value in gradient), Fraction(0)),
        sum(gradient, Fraction(0)),
    )


def maximal_jump_data(
    exponents: tuple[int, ...], neighbors: list[list[int]]
) -> tuple[int, list[int], list[int], int]:
    jump = max(
        exponents[other] - exponents[site]
        for site, row in enumerate(neighbors)
        for other in row
    )
    counts = [
        sum(exponents[other] - exponents[site] == jump for other in row)
        for site, row in enumerate(neighbors)
    ]
    tails = [site for site, count in enumerate(counts) if count]
    source = min(tails, key=lambda site: (exponents[site], site))
    leading: list[int] = []
    for site, row in enumerate(neighbors):
        incoming_mass = sum(
            counts[other]
            for other in row
            if exponents[site] - exponents[other] == jump
        )
        leading.append(incoming_mass - counts[site] ** 2)
    return jump, counts, leading, source


def audit_profile(exponents: tuple[int, ...], neighbors: list[list[int]]) -> bool:
    if len(set(exponents)) == 1:
        return True
    jump, counts, leading, source = maximal_jump_data(exponents, neighbors)
    denominator = sum(value * value for value in counts)
    numerator = sum(value * value for value in leading)
    no_incoming = all(
        exponents[source] - exponents[other] != jump for other in neighbors[source]
    )
    return (
        jump > 0
        and counts[source] > 0
        and no_incoming
        and leading[source] == -(counts[source] ** 2)
        and numerator > 0
        and Fraction(numerator, denominator)
        >= Fraction(1, len(neighbors) * len(neighbors[0]) ** 2)
    )


def complete_small_class_audit() -> tuple[bool, int]:
    classes = [
        ((4,), range(-2, 3)),
        ((6,), range(-1, 2)),
        ((3, 3), (-1, 0)),
    ]
    checked = 0
    for shape, values in classes:
        neighbors = make_neighbors(shape)
        for tail in itertools.product(values, repeat=len(neighbors) - 1):
            exponents = (0,) + tuple(tail)
            if len(set(exponents)) == 1:
                continue
            checked += 1
            if not audit_profile(exponents, neighbors):
                return False, checked
    return True, checked


def fixture_neighbors(name: str) -> list[list[int]]:
    if name.startswith("C4"):
        return make_neighbors((4,))
    if name.startswith("C6"):
        return make_neighbors((6,))
    if name.startswith("T3x3"):
        return make_neighbors((3, 3))
    raise ValueError(name)


def verify(path: str = DEFAULT_CERT) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False
    checks: dict[str, bool] = {}
    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(cert))
    try:
        inputs = cert["provenance"]["inputs"]
        checks["input_hashes"] = len(inputs) == 2 and all(
            file_hash(row["path"]) == row["sha256"] for row in inputs
        )
        fixture_ok = True
        for row in cert["exact_fixtures"]:
            exponents = tuple(row["exponents"])
            neighbors = fixture_neighbors(row["name"])
            residual_norm, gradient_norm, gradient_sum = direct_norms(
                exponents, neighbors
            )
            jump, counts, leading, source = maximal_jump_data(exponents, neighbors)
            coefficient = Fraction(
                sum(value * value for value in leading),
                sum(value * value for value in counts),
            )
            tropical = row["tropical"]
            fixture_ok &= (
                residual_norm == decode(row["parameter_two_residual_norm_squared"])
                and gradient_norm == decode(row["parameter_two_gradient_norm_squared"])
                and gradient_sum == decode(row["parameter_two_gradient_sum"]) == 0
                and jump == tropical["max_edge_exponent_jump"]
                and counts == tropical["max_jump_outdegrees"]
                and leading == tropical["gradient_leading_coefficients"]
                and source == tropical["chosen_source_vertex"]
                and coefficient == decode(tropical["leading_quotient_coefficient"])
                and row["residual_max_laurent_degree"] == jump
                and row["gradient_max_laurent_degree"] == 2 * jump
            )
        checks["fixtures_directly_reconstructed"] = fixture_ok
        class_ok, class_count = complete_small_class_audit()
        checks["complete_621_class_audit"] = class_ok and class_count == 621
        theorem = cert["universal_tropical_theorem"]
        checks["universal_formula_boundary"] = (
            "(sum_x d_x^2)/(sum_x c_x^2)>0" in theorem["exact_limit"]
            and theorem["coefficient_floor"]
            == "(sum d_x^2)/(sum c_x^2)>=1/(N*q^2)"
            and theorem["consequence"]
            == "the residual-gradient quotient diverges on every nonconstant fixed power ray"
        )
        pl = cert["fixed_graph_PL_theorem"]
        checks["fixed_graph_PL_boundary"] = (
            pl["status"] == "PROVED_NONCONSTRUCTIVELY_FOR_EACH_FIXED_GRAPH"
            and "c_G>0" in pl["statement"]
            and "no lower bound" in pl["not_uniform"]
        )
        expected_disposition = {
            "fixed_graph_large_amplitude_gradient_collapse": "RULED_OUT",
            "fixed_graph_positive_PL_constant": "PROVED",
            "uniform_L_scaled_PL_constant": "OPEN",
            "PL_to_Witten_Lyapunov_bridge": "OPEN",
            "full_Witten_coercivity": "OPEN",
            "actual_interacting_h_minus_one": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "ordinary_OS_finite_volume": "OBSTRUCTED_BY_PREDECESSOR",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        }
        checks["research_boundary"] = cert["research_disposition"] == expected_disposition
        checks["dependency_boundary"] = cert["dependency_tags"] == [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ]
        checks["nonclaims"] = {
            "an L-uniform lower bound for c_L/omega_L^2",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "anything LORENTZIAN-CAUSAL",
        }.issubset(set(cert["does_not_establish"]))
        checks["certificate_checks"] = (
            cert["checks"]["ok"]
            and cert["checks"]["passed"] == cert["checks"]["total"]
            and not cert["checks"]["failures"]
            and all(cert["checks"]["details"].values())
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OSError):
        return False
    passed = all(checks.values())
    if passed:
        print(
            "[PASS] independent BT tropical gradient escape verifier "
            f"({sum(checks.values())}/{len(checks)}; 621 exponent classes)"
        )
    return passed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())

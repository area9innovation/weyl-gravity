#!/usr/bin/env python3
"""Independent verifier for the BT orthogonal-Hessian obstruction."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from collections import Counter
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ORTHOGONAL_HESSIAN_BLOCK_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-orthogonal-hessian-block-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def parity(coordinate: int) -> int:
    return 1 if coordinate % 2 == 0 else -1


def cosine_period_four(coordinate: int) -> int:
    return (1, 0, -1, 0)[coordinate % 4]


def sine_period_four(coordinate: int) -> int:
    return (0, 1, 0, -1)[coordinate % 4]


def center_exponent(site: tuple[int, ...]) -> int:
    return sum(parity(coordinate) for coordinate in site)


def direction(site: tuple[int, ...]) -> int:
    value = 1
    for coordinate in site:
        value *= cosine_period_four(coordinate)
    return value


def neighbor(site: tuple[int, ...], axis: int, step: int, length: int) -> tuple[int, ...]:
    result = list(site)
    result[axis] = (result[axis] + step) % length
    return tuple(result)


def enumerate_graph(length: int) -> dict:
    base = Fraction(4, 3)
    sites = list(itertools.product(range(length), repeat=4))
    action = Fraction(0)
    hessian = Fraction(0)
    norm = 0
    laplacian_form = 0
    residual_histogram: Counter[Fraction] = Counter()
    local_histogram: Counter[tuple[Fraction, Fraction, Fraction]] = Counter()
    values = {site: direction(site) for site in sites}
    centers = {site: center_exponent(site) for site in sites}

    for site in sites:
        residual = Fraction(-8)
        first = Fraction(0)
        second = Fraction(0)
        laplacian = 0
        for axis in range(4):
            for step in (-1, 1):
                adjacent = neighbor(site, axis, step, length)
                weight = base ** (centers[adjacent] - centers[site])
                difference = values[adjacent] - values[site]
                residual += weight
                first += weight * difference
                second += weight * difference * difference
                laplacian += values[site] - values[adjacent]
        action += residual * residual / 2
        hessian += first * first + residual * second
        norm += values[site] * values[site]
        laplacian_form += laplacian * laplacian
        residual_histogram[residual] += 1
        local_histogram[(residual, first, second)] += 1

    return {
        "action": action,
        "hessian": hessian,
        "norm": norm,
        "laplacian_form": laplacian_form,
        "residual_histogram": residual_histogram,
        "local_histogram": local_histogram,
        "mean_center": sum(centers.values()),
        "mean_direction": sum(values.values()),
        "sites": sites,
        "values": values,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    errors = []
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = list(Draft202012Validator(schema).iter_errors(certificate))

        checks["strict_schema"] = not errors
        ledger = certificate.get("checks", {})
        checks["closed_internal_check_ledger"] = (
            ledger.get("ok") is True
            and ledger.get("passed") == ledger.get("total") == 17
            and ledger.get("failures") == []
            and len(ledger.get("details", {})) == 17
            and all(ledger.get("details", {}).values())
        )

        cell = enumerate_graph(4)
        calculation = certificate.get("cell_calculation", {})
        checks["full_graph_action_rederived"] = (
            cell["action"] == Fraction(80458, 81)
            and decode(calculation["action"]) == cell["action"]
            and decode(calculation["action_density"])
            == cell["action"] / 256
        )
        checks["full_graph_hessian_rederived"] = (
            cell["hessian"] == Fraction(-13880, 81)
            and decode(calculation["directional_hessian"])
            == cell["hessian"]
            and decode(calculation["rayleigh_quotient"])
            == cell["hessian"] / cell["norm"]
            and cell["hessian"] < 0
        )
        checks["direction_spectral_data_rederived"] = (
            cell["norm"] == calculation.get("direction_norm_squared") == 16
            and cell["laplacian_form"]
            == calculation.get("free_bilaplacian_form")
            == 1024
            and calculation.get("direction_negative_laplacian_eigenvalue")
            == 8
        )
        expected_residual_histogram = Counter(
            {
                Fraction(-7, 2): 16,
                Fraction(-77, 72): 64,
                Fraction(49, 36): 96,
                Fraction(91, 24): 64,
                Fraction(56, 9): 16,
            }
        )
        checks["five_residual_classes_rederived"] = (
            cell["residual_histogram"] == expected_residual_histogram
            and [decode(row["residual"]) for row in calculation["residual_classes"]]
            == list(expected_residual_histogram.keys())
            and [row["vertex_count"] for row in calculation["residual_classes"]]
            == list(expected_residual_histogram.values())
        )
        expected_local_terms = {
            (Fraction(-7, 2), Fraction(-9, 2), Fraction(9, 2)): 8,
            (Fraction(-7, 2), Fraction(9, 2), Fraction(9, 2)): 8,
            (Fraction(-77, 72), Fraction(0), Fraction(32, 9)): 64,
            (Fraction(49, 36), Fraction(0), Fraction(0)): 96,
            (Fraction(91, 24), Fraction(0), Fraction(0)): 64,
            (Fraction(56, 9), Fraction(0), Fraction(0)): 16,
        }
        checks["local_second_variations_rederived"] = (
            cell["local_histogram"] == Counter(expected_local_terms)
        )

        checks["center_and_direction_means_rederived"] = (
            cell["mean_center"] == 0 and cell["mean_direction"] == 0
        )
        axial_inner_products = []
        for axis in range(4):
            axial_inner_products.append(
                sum(
                    cell["values"][site] * cosine_period_four(site[axis])
                    for site in cell["sites"]
                )
            )
            axial_inner_products.append(
                sum(
                    cell["values"][site] * sine_period_four(site[axis])
                    for site in cell["sites"]
                )
            )
        checks["full_lowest_axial_eigenspace_orthogonality_rederived"] = (
            axial_inner_products == [0] * 8
            and certificate.get("lowest_mode_orthogonality", {}).get("status")
            == "PROVED"
        )

        doubled = enumerate_graph(8)
        checks["period_four_replication_rederived"] = (
            doubled["action"] == 16 * cell["action"]
            and doubled["hessian"] == 16 * cell["hessian"]
            and doubled["norm"] == 16 * cell["norm"]
            and certificate.get("replication", {}).get("status")
            == "NEGATIVE_ON_AN_UNBOUNDED_VOLUME_SEQUENCE"
        )

        provenance = certificate.get("provenance", {})
        inputs = provenance.get("inputs", [])
        checks["input_hashes_match"] = len(inputs) == 3 and all(
            item.get("sha256") == file_hash(item.get("path", ""))
            for item in inputs
        )

        disposition = certificate.get("method_disposition", {})
        checks["claim_boundary_is_fail_closed"] = (
            disposition.get("global_orthogonal_hessian_block_positivity")
            == "OBSTRUCTED"
            and disposition.get("global_lowest_mode_schur_complement_definition")
            == "OBSTRUCTED"
            and disposition.get("pointwise_half_action_curvature_route")
            == "OBSTRUCTED_AS_FORMULATED"
            and disposition.get("direct_normalized_low_mode_marginal") == "OPEN"
            and disposition.get("actual_interacting_h_minus_one_second_moment_bound")
            == "OPEN"
            and disposition.get("interacting_tightness") == "NOT_ESTABLISHED"
            and disposition.get("continuum_limit") == "NOT_ESTABLISHED"
            and disposition.get("born_rule") == "NOT_ESTABLISHED"
            and disposition.get("krein_reconstruction") == "NOT_ASSESSED"
            and disposition.get("lorentzian_transfer") == "NOT_ESTABLISHED"
            and certificate.get("dependency_tags")
            == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]
        )
        nonclaims = certificate.get("does_not_establish", [])
        checks["required_nonclaims_are_explicit"] = all(
            any(token in statement for statement in nonclaims)
            for token in ("actual interacting H^-1", "continuum", "Born", "Krein", "LORENTZIAN-CAUSAL")
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return False

    passed = sum(checks.values())
    if not all(checks.values()):
        for error in errors[:3]:
            print(f"[FAIL] schema: {error.message}")
        for name, ok in checks.items():
            if not ok:
                print(f"[FAIL] {name}")
        return False
    print(
        "[PASS] independent BT orthogonal Hessian verifier "
        f"({passed}/{len(checks)})"
    )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())

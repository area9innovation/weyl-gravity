#!/usr/bin/env python3
"""Method-distinct verifier for the BT two-volume sampler preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_STEP_SCALING_PREFLIGHT_V1.json",
)
DATA_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "data",
    "bt_euclidean_lattice_step_scaling_observations_v1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-euclidean-step-scaling-preflight-v1.schema.json",
)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        while True:
            part = handle.read(32768)
            if not part:
                break
            digest.update(part)
    return digest.hexdigest()


def independent_summary(blocks: list[dict]) -> dict[str, tuple[float, float]]:
    """Recompute central values/errors from pooled totals and delete-one blocks."""
    def reduce(rows: list[dict]) -> dict[str, float]:
        number = sum(int(row["sample_count"]) for row in rows)
        modes = sum(int(row["axis_count"]) for row in rows)
        second = math.fsum(row["sum_mode2"] for row in rows) / modes
        fourth = math.fsum(row["sum_mode4"] for row in rows) / modes
        return {
            "action_density": math.fsum(
                row["sum_action_density"] for row in rows
            ) / number,
            "field_variance": math.fsum(
                row["sum_field_variance"] for row in rows
            ) / number,
            "mode_second_moment": second,
            "mode_fourth_moment": fourth,
            "connected_mode_proxy_u": 2.0 - fourth / second ** 2,
        }

    central = reduce(blocks)
    deleted = [reduce(blocks[:i] + blocks[i + 1:]) for i in range(len(blocks))]
    answer = {}
    for observable in central:
        center = math.fsum(row[observable] for row in deleted) / len(deleted)
        error = math.sqrt(
            (len(deleted) - 1) / len(deleted)
            * math.fsum((row[observable] - center) ** 2 for row in deleted)
        )
        answer[observable] = (central[observable], error)
    return answer


def close(left: float, right: float, tolerance: float = 2e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def direct_local_formula_residual() -> float:
    """Check the nonlinear one-site formula on a graph built independently."""
    length, dimensions, coupling = 3, 2, 0.4
    volume = length ** dimensions

    def coordinates(index: int) -> list[int]:
        output = [0] * dimensions
        for axis in range(dimensions - 1, -1, -1):
            output[axis], index = index % length, index // length
        return output

    def index(point: list[int]) -> int:
        output = 0
        for coordinate in point:
            output = output * length + coordinate
        return output

    graph = []
    for vertex in range(volume):
        point = coordinates(vertex)
        row = []
        for axis in range(dimensions):
            for sign in (-1, 1):
                neighbor = point.copy()
                neighbor[axis] = (neighbor[axis] + sign) % length
                row.append(index(neighbor))
        graph.append(row)
    field = [math.cos(0.29 * (i + 1)) / 9 for i in range(volume)]
    degree = 2 * dimensions

    def residuals(values: list[float]) -> list[float]:
        return [
            math.fsum(math.exp(coupling * (values[j] - values[i])) for j in row)
            - degree
            for i, row in enumerate(graph)
        ]

    old_residuals = residuals(field)
    old_action = math.fsum(value * value for value in old_residuals) / (
        2 * coupling ** 2
    )
    worst = 0.0
    for site, delta in ((1, 0.043), (7, -0.031)):
        multiplicities = Counter(graph[site])
        up = math.exp(coupling * delta)
        changed = {
            site: (old_residuals[site] + degree) / up - degree
        }
        for source, count in multiplicities.items():
            edge = math.exp(coupling * (field[site] - field[source]))
            changed[source] = old_residuals[source] + count * edge * (up - 1)
        predicted = math.fsum(
            changed[i] ** 2 - old_residuals[i] ** 2 for i in changed
        ) / (2 * coupling ** 2)
        proposal = field.copy()
        proposal[site] += delta
        direct_residuals = residuals(proposal)
        direct_action = math.fsum(value * value for value in direct_residuals) / (
            2 * coupling ** 2
        )
        worst = max(worst, abs(predicted - (direct_action - old_action)))
    return worst


def verify(path: str) -> bool:
    checks = {}
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(DATA_PATH, encoding="utf-8") as handle:
            observations = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["certificate_checks_closed"] = (
        certificate["checks"]["ok"]
        and certificate["checks"]["passed"] == certificate["checks"]["total"]
        and not certificate["checks"]["failures"]
    )
    recorded_hashes = {
        row["path"]: row["sha256"] for row in certificate["provenance"]["inputs"]
    }
    checks["all_provenance_hashes_current"] = all(
        recorded_hashes.get(relative) == file_hash(relative)
        for relative in recorded_hashes
    )
    checks["observation_hash_present"] = recorded_hashes.get(
        "reverse_physics/data/bt_euclidean_lattice_step_scaling_observations_v1.json"
    ) == file_hash(
        "reverse_physics/data/bt_euclidean_lattice_step_scaling_observations_v1.json"
    )
    checks["independent_local_formula"] = direct_local_formula_residual() < 1e-12
    checks["finite_volume_boundary"] = (
        certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]
        and certificate["lifecycle_state"] == "CLASSIFIED"
        and certificate["disposition"]["continuum_limit"] == "NOT_ESTABLISHED"
        and certificate["disposition"]["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )

    raw_by_key = {}
    for raw in observations["runs"]:
        key = (
            "free_metropolis" if raw["coupling"] == 0
            else f"lambda_0p4_L{raw['lattice']['length']}_"
                 f"{'metropolis' if raw['algorithm'].startswith('independent') else 'hmc'}"
        )
        raw_by_key[key] = raw
    cert_by_key = {row["key"]: row for row in certificate["runs"]}
    checks["five_unique_run_keys"] = set(raw_by_key) == set(cert_by_key) and len(
        raw_by_key
    ) == 5
    recomputed = {}
    summaries_match = True
    for key, raw in raw_by_key.items():
        recomputed[key] = independent_summary(raw["blocks"])
        for observable, (estimate, error) in recomputed[key].items():
            recorded = cert_by_key[key]["summary"][observable]
            summaries_match &= close(estimate, recorded["estimate"])
            summaries_match &= close(error, recorded["jackknife_standard_error"])
    checks["all_jackknife_summaries_recomputed"] = summaries_match

    free = recomputed["free_metropolis"]
    free_targets = {
        "action_density": 255 / 512,
        "mode_second_moment": 1 / 4,
        "connected_mode_proxy_u": 0.0,
    }
    checks["free_calibration_independent"] = all(
        abs((free[name][0] - target) / free[name][1]) < 4
        for name, target in free_targets.items()
    )

    names = (
        "action_density", "field_variance", "mode_second_moment",
        "connected_mode_proxy_u",
    )
    cross = {}
    for length in (4, 6):
        left = recomputed[f"lambda_0p4_L{length}_metropolis"]
        right = recomputed[f"lambda_0p4_L{length}_hmc"]
        cross[f"L{length}"] = {}
        for name in names:
            cross[f"L{length}"][name] = (
                left[name][0] - right[name][0]
            ) / math.hypot(left[name][1], right[name][1])
    checks["cross_sampler_z_scores_recomputed"] = all(
        close(value, certificate["cross_sampler_z_scores"][length][name])
        for length, row in cross.items() for name, value in row.items()
    )
    maximum = max(abs(value) for row in cross.values() for value in row.values())
    checks["coarse_not_precision_classification"] = 2 <= maximum < 4

    changes = {}
    for algorithm in ("metropolis", "hmc"):
        low = recomputed[f"lambda_0p4_L4_{algorithm}"]["connected_mode_proxy_u"]
        high = recomputed[f"lambda_0p4_L6_{algorithm}"]["connected_mode_proxy_u"]
        changes[algorithm] = (
            high[0] - low[0], math.hypot(high[1], low[1])
        )
    agreement = (changes["metropolis"][0] - changes["hmc"][0]) / math.hypot(
        changes["metropolis"][1], changes["hmc"][1]
    )
    checks["finite_size_change_recomputed"] = close(
        agreement, certificate["finite_size_change_cross_algorithm_z"]
    )
    checks["step_is_inconclusive"] = (
        abs(agreement) < 3
        and not all(abs(value / error) >= 3 for value, error in changes.values())
        and certificate["disposition"]["continuum_step_scaling"] == "NOT_ESTABLISHED"
    )
    checks["lorentzian_nonclaim_explicit"] = (
        "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"]
    )

    ok = all(checks.values())
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())

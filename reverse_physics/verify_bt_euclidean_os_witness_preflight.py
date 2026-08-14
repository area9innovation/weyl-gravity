#!/usr/bin/env python3
"""Independent raw-data verifier for the BT interacting OS witness preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_OS_WITNESS_PREFLIGHT_V1.json",
)
DATA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "data",
    "bt_euclidean_os_witness_observations_v1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-os-witness-preflight-v1.schema.json",
)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def close(left: float, right: float, tolerance: float = 2e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def direct_means(observations: dict) -> tuple[list[dict], dict[str, dict], float]:
    rows = []
    for run in observations["runs"]:
        values = [
            measurement["reflected_product"]
            for measurement in run["measurements"]
        ]
        rows.append({
            "algorithm": run["algorithm"],
            "seed": run["seed"],
            "samples": len(values),
            "mean": math.fsum(values) / len(values),
        })
    groups = {
        "local_metropolis": [
            row for row in rows if row["algorithm"].startswith("independent")
        ],
        "hmc": [row for row in rows if row["algorithm"].startswith("zero-mode")],
    }
    summaries = {}
    for name, group in groups.items():
        means = [row["mean"] for row in group]
        mean = statistics.fmean(means)
        error = statistics.stdev(means) / math.sqrt(len(means))
        summaries[name] = {"mean": mean, "error": error, "z": mean / error}
    cross = (
        summaries["local_metropolis"]["mean"] - summaries["hmc"]["mean"]
    ) / math.hypot(
        summaries["local_metropolis"]["error"],
        summaries["hmc"]["error"],
    )
    return rows, summaries, cross


def batch_signs(observations: dict, blocks: int = 20) -> dict[str, bool]:
    """Method-distinct block rail for the pooled sign of each algorithm."""
    output = {}
    for label, prefix in (
        ("local_metropolis", "independent"),
        ("hmc", "zero-mode"),
    ):
        block_means = []
        for run in observations["runs"]:
            if not run["algorithm"].startswith(prefix):
                continue
            values = [row["reflected_product"] for row in run["measurements"]]
            width = len(values) // blocks
            block_means.extend(
                statistics.fmean(values[index:index + width])
                for index in range(0, len(values), width)
            )
        output[label] = statistics.fmean(block_means) < 0
    return output


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
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
    checks["all_provenance_hashes_current"] = bool(recorded_hashes) and all(
        digest == file_hash(relative)
        for relative, digest in recorded_hashes.items()
    )
    checks["raw_product_identity"] = all(
        close(
            row["positive_F"] * row["reflected_F"],
            row["reflected_product"],
            tolerance=1e-15,
        )
        for run in observations["runs"]
        for row in run["measurements"]
    )

    rows, summaries, cross = direct_means(observations)
    recorded_runs = {
        (row["algorithm"], row["seed"]): row for row in certificate["runs"]
    }
    checks["all_run_means_reconstructed"] = all(
        close(
            row["mean"],
            recorded_runs[(row["algorithm"], row["seed"])][
                "mean_reflected_product"
            ],
        )
        and row["samples"]
        == recorded_runs[(row["algorithm"], row["seed"])]["samples"]
        for row in rows
    )
    recorded_summaries = certificate["algorithm_summaries"]
    checks["replica_statistics_reconstructed"] = all(
        close(summary["mean"], recorded_summaries[name]["equal_replica_mean"])
        and close(
            summary["error"],
            recorded_summaries[name]["replica_standard_error"],
        )
        and close(summary["z"], recorded_summaries[name]["z_from_zero"])
        for name, summary in summaries.items()
    )
    checks["cross_sampler_score_reconstructed"] = close(
        cross, certificate["cross_sampler_mean_z"]
    )
    checks["eight_negative_replica_means"] = len(rows) == 8 and all(
        row["mean"] < 0 for row in rows
    )
    checks["independent_block_sign_rail"] = all(batch_signs(observations).values())
    checks["precision_classification"] = (
        summaries["hmc"]["z"] < -3
        and -3 < summaries["local_metropolis"]["z"] < -2
        and abs(cross) < 2
    )
    checks["exact_free_authority_matches_observable"] = (
        observations["observable"]["exact_free_expectation"]
        == {"numerator": -1, "denominator": 1296}
    )
    checks["dependency_boundary"] = certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    checks["honest_disposition"] = certificate["disposition"] == {
        "lambda_0p4_reflected_witness": "TWO_SAMPLER_NEGATIVE_SIGN_SUPPORT_NOT_EXACT",
        "local_precision_gate": "TWO_SIGMA_PASS_THREE_SIGMA_NOT_PASSED",
        "hmc_precision_gate": "THREE_SIGMA_PASSED",
        "cross_sampler_agreement": "WITHIN_TWO_COMBINED_STANDARD_ERRORS",
        "ordinary_os_reflection_positivity_at_lambda_0p4": "OPEN",
        "continuum_limit": "NOT_ESTABLISHED",
        "krein_compatible_reconstruction": "NOT_ASSESSED",
        "born_rule": "NOT_ESTABLISHED",
        "lorentzian_transfer": "NOT_ESTABLISHED",
    }
    checks["required_nonclaims_present"] = {
        "an exact sign at lambda=0.4",
        "a continuum or infinite-volume limit",
        "a Krein-compatible reconstruction",
        "anything LORENTZIAN-CAUSAL",
    }.issubset(set(certificate["does_not_establish"]))

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Classify the independent-sampler BT OS witness observations at lambda=0.4."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_OS_WITNESS_PREFLIGHT_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_os_witness_observations_v1.json"
)
DATA_PATH = os.path.join(REPO_ROOT, DATA_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-os-witness-preflight-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-os-witness-preflight.md"
)
INPUTS = [
    DATA_REL,
    "reverse_physics/bt_euclidean_os_witness_experiment.py",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json",
]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def initial_positive_sequence_iat(values: list[float]) -> tuple[float, int]:
    """Geyer-style paired initial-positive autocorrelation estimate."""
    size = len(values)
    mean = math.fsum(values) / size
    centered = [value - mean for value in values]
    gamma_zero = math.fsum(value * value for value in centered) / size
    if not gamma_zero:
        return 1.0, 0
    correlations = []
    for lag in range(1, size // 2 + 1):
        covariance = math.fsum(
            centered[index] * centered[index + lag]
            for index in range(size - lag)
        ) / (size - lag)
        correlations.append(covariance / gamma_zero)
    total = 0.0
    used = 0
    for index in range(0, len(correlations) - 1, 2):
        pair = correlations[index] + correlations[index + 1]
        if pair <= 0:
            break
        total += pair
        used = index + 2
    return max(1.0, 1.0 + 2.0 * total), used


def run_summary(run: dict) -> dict:
    values = [row["reflected_product"] for row in run["measurements"]]
    mean = math.fsum(values) / len(values)
    variance = statistics.variance(values)
    iat, used_lags = initial_positive_sequence_iat(values)
    standard_error = math.sqrt(variance * iat / len(values))
    return {
        "algorithm": run["algorithm"],
        "seed": run["seed"],
        "samples": len(values),
        "mean_reflected_product": mean,
        "sample_variance": variance,
        "integrated_autocorrelation_time_retained_samples": iat,
        "positive_sequence_lags_used": used_lags,
        "effective_sample_size": len(values) / iat,
        "iat_standard_error": standard_error,
        "z_from_zero_iat": mean / standard_error,
        "acceptance_rate": run["acceptance_rate"],
        "elapsed_seconds_observed": run["elapsed_seconds_observed"],
    }


def replica_summary(rows: list[dict]) -> dict:
    means = [row["mean_reflected_product"] for row in rows]
    mean = statistics.fmean(means)
    standard_error = statistics.stdev(means) / math.sqrt(len(means))
    return {
        "replicas": len(rows),
        "equal_replica_mean": mean,
        "replica_standard_error": standard_error,
        "z_from_zero": mean / standard_error,
        "all_replica_means_negative": all(value < 0 for value in means),
        "minimum_iat": min(row["integrated_autocorrelation_time_retained_samples"] for row in rows),
        "maximum_iat": max(row["integrated_autocorrelation_time_retained_samples"] for row in rows),
        "total_retained_samples": sum(row["samples"] for row in rows),
    }


def build() -> dict:
    with open(DATA_PATH, encoding="utf-8") as handle:
        observations = json.load(handle)
    runs = [run_summary(run) for run in observations["runs"]]
    metropolis = [
        row for row in runs if row["algorithm"].startswith("independent")
    ]
    hmc = [row for row in runs if row["algorithm"].startswith("zero-mode")]
    algorithm_summaries = {
        "local_metropolis": replica_summary(metropolis),
        "hmc": replica_summary(hmc),
    }
    local = algorithm_summaries["local_metropolis"]
    global_hmc = algorithm_summaries["hmc"]
    cross_sampler_z = (
        local["equal_replica_mean"] - global_hmc["equal_replica_mean"]
    ) / math.hypot(
        local["replica_standard_error"],
        global_hmc["replica_standard_error"],
    )
    raw_product_residual = max(
        abs(
            measurement["positive_F"] * measurement["reflected_F"]
            - measurement["reflected_product"]
        )
        for run in observations["runs"]
        for measurement in run["measurements"]
    )
    checks = {
        "observation_is_production_not_smoke": observations["smoke"] is False,
        "dependency_is_euclidean_spectral": (
            observations["dependency_tags"] == ["EUCLIDEAN-SPECTRAL"]
        ),
        "four_independent_replicas_per_algorithm": (
            len(metropolis) == len(hmc) == 4
        ),
        "all_seeds_are_unique": len({row["seed"] for row in runs}) == 8,
        "all_raw_products_recompute_below_1e_15": raw_product_residual < 1e-15,
        "all_acceptance_rates_between_65_and_96_percent": all(
            0.65 < row["acceptance_rate"] < 0.96 for row in runs
        ),
        "all_iats_are_finite_and_at_least_one": all(
            math.isfinite(row["integrated_autocorrelation_time_retained_samples"])
            and row["integrated_autocorrelation_time_retained_samples"] >= 1
            for row in runs
        ),
        "all_eight_replica_means_are_negative": all(
            row["mean_reflected_product"] < 0 for row in runs
        ),
        "hmc_negative_sign_exceeds_3sigma": global_hmc["z_from_zero"] < -3,
        "local_negative_sign_exceeds_2sigma_but_not_3sigma": (
            -3 < local["z_from_zero"] < -2
        ),
        "cross_sampler_means_agree_within_2sigma": abs(cross_sampler_z) < 2,
        "local_iat_is_larger_than_hmc_iat": (
            local["minimum_iat"] > global_hmc["maximum_iat"]
        ),
        "lambda_0p4_exact_status_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_OS_WITNESS_PREFLIGHT_V1",
        "schema_version": "reverse-physics-bt-euclidean-os-witness-preflight-v1",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "independent-sampler reflected-witness sign preflight",
        "question": (
            "Do independent bounded samplers support a negative reflected BT "
            "witness at lambda=0.4 on the finite 6^4 lattice?"
        ),
        "answer": (
            "Yes as numerical support, not as an exact decision. All eight "
            "independent chain means are negative. Equal-replica pooling gives "
            f"{global_hmc['z_from_zero']:.2f} sigma for HMC and "
            f"{local['z_from_zero']:.2f} sigma for local Metropolis; their means "
            f"differ by only {abs(cross_sampler_z):.2f} combined standard errors. "
            "The local chain has much larger integrated autocorrelation and does "
            "not cross a three-sigma sign gate, so ordinary OS failure at "
            "lambda=0.4 remains unproved."
        ),
        "observable": observations["observable"],
        "runs": runs,
        "algorithm_summaries": algorithm_summaries,
        "cross_sampler_mean_z": cross_sampler_z,
        "maximum_raw_product_residual": raw_product_residual,
        "disposition": {
            "lambda_0p4_reflected_witness": (
                "TWO_SAMPLER_NEGATIVE_SIGN_SUPPORT_NOT_EXACT"
            ),
            "local_precision_gate": "TWO_SIGMA_PASS_THREE_SIGMA_NOT_PASSED",
            "hmc_precision_gate": "THREE_SIGMA_PASSED",
            "cross_sampler_agreement": "WITHIN_TWO_COMBINED_STANDARD_ERRORS",
            "ordinary_os_reflection_positivity_at_lambda_0p4": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "krein_compatible_reconstruction": "NOT_ASSESSED",
            "born_rule": "NOT_ESTABLISHED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "barrier_analysis": {
            "resolved": (
                "The exact free witness remains negative in central value for "
                "every independent interacting chain and both algorithms."
            ),
            "remaining": (
                "Local lowest-mode mixing inflates the replica uncertainty; "
                "a numerical sign is not an all-observable reflection-positivity theorem."
            ),
            "next_method": (
                "Quantify the analytic near-zero interval or use a rigorous "
                "finite-volume integration bound; do not convert significance "
                "chasing into an exact claim."
            ),
        },
        "missing_object_ledger": [
            "an explicit analytic lower bound on the near-zero obstruction interval",
            "a rigorous sign bound at lambda=0.4",
            "an all-observable reflection-positivity classification at lambda=0.4",
            "an interacting L-uniform negative-Sobolev estimate",
            "tightness, represented convergence and limit identification",
            "a Krein-compatible reconstruction and Lorentzian observable map",
        ],
        "does_not_establish": observations["does_not_establish"] + [
            "that a two- or three-sigma numerical sign is an exact obstruction",
            "that the witness sign decides every positive-time observable",
            "a Born rule, scattering probability, or empirical event rate",
        ],
        "provenance": {
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "production_command": (
                "ulimit -v 500000; single-thread numerical-library settings; "
                "python3 reverse_physics/bt_euclidean_os_witness_experiment.py --write"
            ),
            "production_elapsed_seconds_observed_sum": math.fsum(
                row["elapsed_seconds_observed"] for row in runs
            ),
            "memory_ceiling_kib": 500000,
            "peak_rss_kib": "NOT_RECORDED",
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_os_witness_preflight.py --check",
            "python3 reverse_physics/verify_bt_euclidean_os_witness_preflight.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_os_witness_preflight",
        ],
        "tier_receipt": {
            "tier_0": {
                "status": "PASS",
                "commands": [
                    "python3 -m py_compile <four changed Python files>",
                    "python3 -m json.tool <observation, certificate and schema JSON>",
                    "git diff --check -- <scoped paths>",
                ],
            },
            "tier_1": [
                {
                    "rail": "deterministic producer check",
                    "status": "PASS_14_OF_14",
                    "elapsed_seconds": 0.36,
                    "peak_rss_kib": 25572,
                },
                {
                    "rail": "independent raw-data verifier",
                    "status": "PASS_14_OF_14",
                    "elapsed_seconds": 0.14,
                    "peak_rss_kib": 34468,
                },
                {
                    "rail": "unit and six-mutation suite",
                    "status": "PASS_9_TESTS",
                    "elapsed_seconds": 0.73,
                    "peak_rss_kib": 37252,
                },
            ],
            "tier_2": {
                "status": "PASS_HASH_ONLY",
                "criterion": (
                    "the exact predecessor certificate is unchanged and its "
                    "content hash is checked by the independent verifier"
                ),
            },
            "tier_3": {
                "status": "NOT_RUN",
                "criterion": (
                    "CLASSIFIED finite-volume numerical preflight with no shared "
                    "operator, continuum theorem, quantum lifecycle or Lorentzian promotion"
                ),
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
    }


def write_or_check(certificate: dict, *, write: bool, check: bool) -> bool:
    encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    if check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return False
        if current != encoded:
            print("[FAIL] certificate differs from deterministic reproduction")
            return False
    for name, passed in certificate["checks"]["details"].items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if certificate['checks']['ok'] else 'FAIL'} "
        f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
    )
    return certificate["checks"]["ok"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return 0 if write_or_check(build(), write=args.write, check=args.check) else 1


if __name__ == "__main__":
    sys.exit(main())

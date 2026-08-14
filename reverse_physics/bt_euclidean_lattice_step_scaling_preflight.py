#!/usr/bin/env python3
"""Certify the BT independent-sampler and two-volume preflight observations."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_STEP_SCALING_PREFLIGHT_V1.json"
)
CERT_PATH = os.path.join(REPO_ROOT, CERT_REL)
DATA_REL = (
    "reverse_physics/data/"
    "bt_euclidean_lattice_step_scaling_observations_v1.json"
)
DATA_PATH = os.path.join(REPO_ROOT, DATA_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-step-scaling-preflight-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-lattice-step-scaling-preflight.md"
)
SOURCE_COMMIT = "bb903e5cd8713832b3871fe637405e0142139db2"
INPUTS = [
    DATA_REL,
    "reverse_physics/bt_euclidean_lattice_step_scaling_experiment.py",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json",
]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def aggregate(blocks: list[dict]) -> dict[str, float]:
    samples = sum(block["sample_count"] for block in blocks)
    axes = sum(block["axis_count"] for block in blocks)
    mode2 = sum(block["sum_mode2"] for block in blocks) / axes
    mode4 = sum(block["sum_mode4"] for block in blocks) / axes
    return {
        "action_density": (
            sum(block["sum_action_density"] for block in blocks) / samples
        ),
        "field_variance": (
            sum(block["sum_field_variance"] for block in blocks) / samples
        ),
        "mode_second_moment": mode2,
        "mode_fourth_moment": mode4,
        "connected_mode_proxy_u": 2.0 - mode4 / (mode2 * mode2),
    }


def jackknife_summary(blocks: list[dict]) -> dict[str, dict[str, float]]:
    central = aggregate(blocks)
    leave_one_out = [
        aggregate(blocks[:index] + blocks[index + 1:])
        for index in range(len(blocks))
    ]
    output = {}
    for key, value in central.items():
        jackknife_mean = sum(row[key] for row in leave_one_out) / len(blocks)
        variance = (len(blocks) - 1) / len(blocks) * sum(
            (row[key] - jackknife_mean) ** 2 for row in leave_one_out
        )
        output[key] = {
            "estimate": value,
            "jackknife_standard_error": math.sqrt(variance),
        }
    return output


def z_difference(left: dict[str, float], right: dict[str, float]) -> float:
    denominator = math.hypot(
        left["jackknife_standard_error"],
        right["jackknife_standard_error"],
    )
    return (
        (left["estimate"] - right["estimate"]) / denominator
        if denominator else math.inf
    )


def z_target(summary: dict[str, float], target: float) -> float:
    return (
        (summary["estimate"] - target) / summary["jackknife_standard_error"]
    )


def build() -> dict:
    with open(DATA_PATH, encoding="utf-8") as handle:
        observations = json.load(handle)
    runs = []
    indexed = {}
    for raw in observations["runs"]:
        summary = jackknife_summary(raw["blocks"])
        key = (
            "free_metropolis" if raw["coupling"] == 0.0
            else f"lambda_0p4_L{raw['lattice']['length']}_"
                 f"{'metropolis' if raw['algorithm'].startswith('independent') else 'hmc'}"
        )
        row = {
            "key": key,
            "algorithm": raw["algorithm"],
            "coupling": raw["coupling"],
            "lattice": raw["lattice"],
            "acceptance_rate": raw["acceptance_rate"],
            "recorded_samples": raw["recorded_samples"],
            "block_count": raw["block_count"],
            "elapsed_seconds_observed": raw["elapsed_seconds"],
            "final_action_recompute_residual": raw.get(
                "final_action_recompute_residual"
            ),
            "summary": summary,
        }
        runs.append(row)
        indexed[key] = row

    free = indexed["free_metropolis"]
    free_targets = {
        "action_density": float(Fraction(255, 512)),
        "mode_second_moment": 0.25,
        "connected_mode_proxy_u": 0.0,
    }
    free_z = {
        name: z_target(free["summary"][name], target)
        for name, target in free_targets.items()
    }

    comparison_names = [
        "action_density",
        "field_variance",
        "mode_second_moment",
        "connected_mode_proxy_u",
    ]
    cross_sampler = {}
    for length in (4, 6):
        metropolis = indexed[f"lambda_0p4_L{length}_metropolis"]
        hmc = indexed[f"lambda_0p4_L{length}_hmc"]
        cross_sampler[f"L{length}"] = {
            name: z_difference(
                metropolis["summary"][name], hmc["summary"][name]
            )
            for name in comparison_names
        }

    finite_size_changes = {}
    for algorithm in ("metropolis", "hmc"):
        low = indexed[f"lambda_0p4_L4_{algorithm}"]["summary"][
            "connected_mode_proxy_u"
        ]
        high = indexed[f"lambda_0p4_L6_{algorithm}"]["summary"][
            "connected_mode_proxy_u"
        ]
        difference = high["estimate"] - low["estimate"]
        error = math.hypot(
            high["jackknife_standard_error"],
            low["jackknife_standard_error"],
        )
        finite_size_changes[algorithm] = {
            "u_L6_minus_u_L4": difference,
            "standard_error": error,
            "z_from_zero": difference / error,
        }
    delta_agreement_z = (
        finite_size_changes["metropolis"]["u_L6_minus_u_L4"]
        - finite_size_changes["hmc"]["u_L6_minus_u_L4"]
    ) / math.hypot(
        finite_size_changes["metropolis"]["standard_error"],
        finite_size_changes["hmc"]["standard_error"],
    )

    all_cross_z = [
        abs(value)
        for comparison in cross_sampler.values()
        for value in comparison.values()
    ]
    checks = {
        "observation_artifact_is_production_not_smoke": not observations["smoke"],
        "observation_dependency_is_euclidean_spectral": (
            observations["dependency_tags"] == ["EUCLIDEAN-SPECTRAL"]
        ),
        "five_required_runs_are_present": set(indexed) == {
            "free_metropolis",
            "lambda_0p4_L4_metropolis",
            "lambda_0p4_L4_hmc",
            "lambda_0p4_L6_metropolis",
            "lambda_0p4_L6_hmc",
        },
        "local_delta_matches_direct_action_below_1e_12": (
            observations["local_delta_direct_check_max_residual"] < 1e-12
        ),
        "all_acceptance_rates_between_60_and_98_percent": all(
            0.60 < run["acceptance_rate"] < 0.98 for run in runs
        ),
        "local_final_actions_recompute_below_1e_8": all(
            run["final_action_recompute_residual"] is None
            or run["final_action_recompute_residual"] < 1e-8
            for run in runs
        ),
        "all_runs_have_twenty_nonempty_blocks": all(
            run["block_count"] == 20 and run["recorded_samples"] > 0
            for run in runs
        ),
        "free_action_density_within_4sigma": abs(free_z["action_density"]) < 4,
        "free_lowest_mode_second_moment_within_4sigma": (
            abs(free_z["mode_second_moment"]) < 4
        ),
        "free_connected_mode_proxy_within_4sigma_of_zero": (
            abs(free_z["connected_mode_proxy_u"]) < 4
        ),
        "interacting_cross_sampler_observables_within_4sigma": (
            max(all_cross_z) < 4
        ),
        "interacting_cross_sampler_not_claimed_precision_matched": (
            max(all_cross_z) >= 2
        ),
        "two_algorithm_finite_size_changes_agree_within_3sigma": (
            abs(delta_agreement_z) < 3
        ),
        "finite_size_change_not_resolved_by_both_algorithms_at_3sigma": not all(
            abs(row["z_from_zero"]) >= 3
            for row in finite_size_changes.values()
        ),
        "step_scaling_is_explicitly_preflight_not_continuum": True,
        "no_lorentzian_causal_claim": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_STEP_SCALING_PREFLIGHT_V1",
        "schema_version": "reverse-physics-bt-euclidean-step-scaling-preflight-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "finite-volume independent-sampler reproduction preflight",
        "question": (
            "Does an independently implemented local sampler reproduce the BT "
            "Euclidean lattice pilot at L=4 and L=6 well enough to infer a "
            "nonzero finite-size step of a lowest-mode interaction proxy?"
        ),
        "answer": (
            "The independent local action change is exact and its free-field "
            "calibration passes. At lambda=0.4, local Metropolis and HMC agree "
            "on the declared bulk and lowest-mode observables at the conservative "
            "four-sigma gate, but not at a two-sigma precision gate. Their L=4 "
            "to L=6 changes of u_L are statistically compatible, yet a nonzero "
            "change is not resolved by both algorithms. The independent-sampler "
            "preflight therefore passes only as a coarse reproduction; continuum "
            "step scaling remains inconclusive."
        ),
        "observable_scheme": observations["mode_scheme"],
        "free_calibration": {
            "exact_targets": free_targets,
            "z_scores": free_z,
        },
        "runs": runs,
        "cross_sampler_z_scores": cross_sampler,
        "maximum_absolute_cross_sampler_z": max(all_cross_z),
        "finite_size_changes": finite_size_changes,
        "finite_size_change_cross_algorithm_z": delta_agreement_z,
        "disposition": {
            "independent_local_action_delta": "EXACTLY_CROSS_CHECKED",
            "independent_free_calibration": "PASSED",
            "interacting_independent_reproduction": (
                "COARSE_4SIGMA_PASS_NOT_2SIGMA_PRECISION_MATCH"
            ),
            "two_volume_interaction_proxy": "OBSERVED_BUT_STEP_UNRESOLVED",
            "continuum_step_scaling": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "barrier_analysis": {
            "observed_barrier": (
                "The fourth-moment proxy is tail-sensitive and the local chain "
                "mixes the lowest mode slowly as L grows; current block errors "
                "are too large for a precision two-volume step."
            ),
            "what_was_broken": (
                "Sampler monoculture was broken: HMC and a local detailed-balance "
                "chain now provide independent numerical implementations."
            ),
            "what_remains": (
                "Precision, not existence, is now the barrier. Independent "
                "replicas and explicit integrated-autocorrelation estimates must "
                "agree at L=6 before adding L=8 or tuning a matched coupling."
            ),
        },
        "missing_object_ledger": [
            "raw per-measurement records for integrated-autocorrelation analysis",
            "multiple independent seeds per algorithm and volume",
            "a precision cross-sampler agreement gate at L=6",
            "a matched-renormalized-coupling finite-volume scheme",
            "an L=8 point after the L=6 precision gate passes",
            "a controlled continuum extrapolation",
            "Osterwalder--Schrader or alternative reconstruction",
            "a justified Lorentzian map and q8-q10 observable matching",
        ],
        "next_gate": (
            "Run at least four independent replicas of each algorithm at L=6, "
            "retain raw lowest-mode powers, estimate integrated autocorrelation "
            "times, and require action, variance, M2 and u_L agreement within "
            "two combined standard errors before spending on L=8."
        ),
        "does_not_establish": observations["does_not_establish"] + [
            "that four-sigma compatibility is a precision sampler equivalence",
            "that the observed two-volume difference is nonzero",
            "a beta function or asymptotically safe fixed point",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-14",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "observation_commands": [
                "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
                "NUMEXPR_NUM_THREADS=1; ulimit -v 500000; "
                "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 "
                "reverse_physics/bt_euclidean_lattice_step_scaling_experiment.py --write",
                "same bounded environment; bt_euclidean_lattice_step_scaling_experiment.py "
                "--refresh-metropolis --write",
                "same bounded environment; bt_euclidean_lattice_step_scaling_experiment.py "
                "--add-free-calibration --write",
            ],
            "peak_rss_kib": 18844,
        },
        "verification_commands": [
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 "
            "reverse_physics/bt_euclidean_lattice_step_scaling_preflight.py --check",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 "
            "reverse_physics/verify_bt_euclidean_lattice_step_scaling_preflight.py",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 "
            "-m unittest -v reverse_physics.tests.test_bt_euclidean_lattice_step_scaling_preflight",
        ],
        "tier_receipt": {
            "tier_0": "parse/schema/diff checks required",
            "tier_1": "producer, independent verifier, smoke and mutation tests required",
            "tier_2": "prior lattice certificate hash checked; no prior mathematical input changed",
            "tier_3": "not run: CLASSIFIED numerical preflight with no theorem or lifecycle promotion",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, value in checks.items() if not value],
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

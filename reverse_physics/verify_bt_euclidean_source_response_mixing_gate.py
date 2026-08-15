#!/usr/bin/env python3
"""Independent verifier for the BT source-response mixing gate."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from fractions import Fraction

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SOURCE_RESPONSE_MIXING_GATE_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-source-response-mixing-gate-v1.schema.json"
)
DATA_REL = "reverse_physics/data/bt_euclidean_source_response_observations_v1.json"


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def independent_fixture() -> dict:
    before = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    phase_factor = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    after = [before[index] * phase_factor[index] for index in range(4)]

    def rows(values: list[Fraction]) -> list[Fraction]:
        output = []
        for site, center in enumerate(values):
            incoming = values[(site - 1) % 4] + values[(site + 1) % 4]
            output.append(incoming / center - 2)
        return output

    residual_before = rows(before)
    residual_after = rows(after)
    action_before = sum((entry**2 for entry in residual_before), Fraction()) / 2
    action_after = sum((entry**2 for entry in residual_after), Fraction()) / 2
    return {
        "before": before,
        "phase_factor": phase_factor,
        "after": after,
        "residual_before": residual_before,
        "residual_after": residual_after,
        "action_before": action_before,
        "action_after": action_after,
        "full_delta": 4**3 * (action_after - action_before),
    }


def block_mean_and_error(run: dict, field: str) -> tuple[float, float]:
    block_means = []
    for block in run["blocks"]:
        block_means.append(
            block[f"sum_{field}"] / block["sample_count"]
        )
    mean = sum(block_means) / len(block_means)
    centered = sum((entry - mean) ** 2 for entry in block_means)
    error = math.sqrt(centered / (len(block_means) * (len(block_means) - 1)))
    return mean, error


def independent_observations() -> dict:
    with open(os.path.join(ROOT, DATA_REL), encoding="utf-8") as handle:
        data = json.load(handle)
    rows = []
    for run in data["runs"]:
        mode2, mode_error = block_mean_and_error(run, "mode2")
        action, action_error = block_mean_and_error(run, "action_density")
        omega = 2.0 * (1.0 - math.cos(2.0 * math.pi / run["lattice"]["length"]))
        rows.append(
            {
                "length": run["lattice"]["length"],
                "augmented": bool(run["whole_mode_proposals_per_sweep"]),
                "mode2": mode2,
                "mode_error": mode_error,
                "action": action,
                "action_error": action_error,
                "bilaplacian_ratio": omega**2 * mode2,
                "bilaplacian_error": omega**2 * mode_error,
            }
        )
    local, augmented = rows[1], rows[2]
    return {
        "rows": rows,
        "mode_z": abs(augmented["mode2"] - local["mode2"])
        / math.hypot(augmented["mode_error"], local["mode_error"]),
        "action_z": abs(augmented["action"] - local["action"])
        / math.hypot(augmented["action_error"], local["action_error"]),
    }


def verify(cert: dict) -> tuple[bool, list[tuple[str, bool]]]:
    with open(os.path.join(ROOT, SCHEMA_REL), encoding="utf-8") as handle:
        schema = json.load(handle)
    checks: list[tuple[str, bool]] = []
    try:
        jsonschema.Draft202012Validator(schema).validate(cert)
        strict_schema = True
    except jsonschema.ValidationError:
        strict_schema = False
    checks.append(("strict_schema", strict_schema))

    declared = cert.get("provenance", {})
    paths = declared.get("inputs", []) + declared.get("generated_inputs", [])
    checks.append(
        (
            "provenance_hash_current",
            bool(paths)
            and all(
                item.get("sha256") == sha256(item.get("path", ""))
                for item in paths
            ),
        )
    )

    exact = independent_fixture()
    stored = cert.get("exact_cycle_four_tensor_fixture", {})
    checks.append(
        (
            "independent_exact_fixture",
            [dec(value) for value in stored.get("axial_omega", [])]
            == exact["before"]
            and [dec(value) for value in stored.get("phase_multiplier", [])]
            == exact["phase_factor"]
            and [dec(value) for value in stored.get("proposed_omega", [])]
            == exact["after"]
            and [dec(value) for value in stored.get("residual", [])]
            == exact["residual_before"]
            and [dec(value) for value in stored.get("proposed_residual", [])]
            == exact["residual_after"]
            and dec(stored.get("full_4_to_the_4_delta_action", {"numerator": 0, "denominator": 1}))
            == exact["full_delta"]
            == Fraction(1372),
        )
    )

    source = cert.get("source_response_identity", {})
    kernel = cert.get("whole_mode_kernel", {})
    checks.append(
        (
            "source_and_kernel_boundary",
            source.get("status") == "PROVED_FINITE_VOLUME"
            and "Cov_J" in source.get("second_derivative", "")
            and kernel.get("status") == "PROVED_FINITE_VOLUME"
            and "symmetric" in kernel.get("detailed_balance", "")
            and kernel.get("action_evaluation")
            == "full independent residual and action recomputation",
        )
    )

    independent = independent_observations()
    preflight = cert.get("numerical_preflight", {})
    certificate_rows = preflight.get("rows", [])
    row_match = len(certificate_rows) == 3
    if row_match:
        for stored_row, rebuilt in zip(certificate_rows, independent["rows"]):
            row_match = row_match and stored_row.get("length") == rebuilt["length"]
            row_match = row_match and math.isclose(
                stored_row.get("mode2", math.nan), rebuilt["mode2"], rel_tol=0, abs_tol=1e-14
            )
            row_match = row_match and math.isclose(
                stored_row.get("action_density", math.nan), rebuilt["action"], rel_tol=0, abs_tol=1e-14
            )
            row_match = row_match and math.isclose(
                stored_row.get("bilaplacian_ratio", math.nan),
                rebuilt["bilaplacian_ratio"],
                rel_tol=0,
                abs_tol=1e-14,
            )
    checks.append(("independent_block_reduction", row_match))
    checks.append(
        (
            "mixing_disagreement_reproduced",
            independent["mode_z"] > 6.0
            and independent["action_z"] < 3.0
            and math.isclose(
                preflight.get("l8_mode2_difference_in_combined_block_standard_errors", math.nan),
                independent["mode_z"],
                rel_tol=0,
                abs_tol=1e-13,
            ),
        )
    )
    checks.append(
        (
            "bilaplacian_observation_not_promoted",
            all(
                abs(row["bilaplacian_ratio"] - 1.0)
                < 2.0 * row["bilaplacian_error"]
                for row in (independent["rows"][0], independent["rows"][2])
            )
            and cert.get("method_disposition", {}).get(
                "mode_augmented_l6_l8_bilaplacian_scaling"
            )
            == "OBSERVED_SUPPORTING_ONLY",
        )
    )

    disposition = cert.get("method_disposition", {})
    boundaries = cert.get("does_not_establish", [])
    checks.append(
        (
            "claim_boundary",
            disposition.get("actual_interacting_h_minus_one_second_moment")
            == "OPEN"
            and disposition.get("bilaplacian_scale_witten_or_center_coercivity")
            == "OPEN"
            and any("LORENTZIAN-CAUSAL" in item for item in boundaries)
            and any("equilibration" in item for item in boundaries),
        )
    )
    checks.append(
        (
            "producer_checks_consistent",
            cert.get("checks", {}).get("ok") is True
            and cert.get("checks", {}).get("passed") == 17
            and cert.get("checks", {}).get("total") == 17,
        )
    )
    return all(value for _, value in checks), checks


def main() -> int:
    with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
        cert = json.load(handle)
    ok, checks = verify(cert)
    for name, value in checks:
        print(f"[{'PASS' if value else 'FAIL'}] {name}")
    print(
        "BT source-response mixing-gate independent verifier: "
        f"{'PASS' if ok else 'FAIL'} ({sum(value for _, value in checks)}/{len(checks)})"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

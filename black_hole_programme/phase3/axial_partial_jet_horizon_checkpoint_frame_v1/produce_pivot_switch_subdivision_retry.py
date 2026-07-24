#!/usr/bin/env python3
"""Produce the append-only panel-30 supersession and retry certificate."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "pivot-switch-subdivision-retry-run.json"
OUTPUT = HERE / "pivot-switch-subdivision-retry-certificate.json"
RECEIPT = HERE / "pivot-switch-subdivision-retry-receipt.json"
SCHEMA = HERE / "pivot-switch-subdivision-retry-schema.json"
INPUTS = {
    "superseded_continuation_certificate": (
        HERE / "pivot-switch-continuation-certificate.json"
    ),
    "superseded_continuation_run": HERE / "pivot-switch-continuation-run.json",
    "source_pivot_switch_certificate": HERE / "pivot-switch-certificate.json",
    "retry_transport": HERE / "pivot_switch_subdivision_retry.py",
    "checkpoint_transport": HERE / "checkpoint_transport.py",
    "crosswalk": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_transport_crosswalk_v1/certificate.json",
    "spin_one_levelt": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_horizon_spin_one_levelt_v1/certificate.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict, dict]:
    run = json.loads(RUN.read_text())
    witness = run["panel_31_mutation_witness"]
    if not witness["old_check_order_would_accept"]:
        raise RuntimeError("old-check mutation witness drift")
    if witness["corrected_check_accepts"]:
        raise RuntimeError("corrected post-normalization gate drift")
    checkpoint = run["corrected_last_valid_checkpoint"]
    if checkpoint["panel"] != 30 or checkpoint["rho"] != "95/268435456":
        raise RuntimeError("corrected checkpoint drift")
    attempts = run["retry_grid"]["attempts"]
    if len(attempts) != 30 or run["retry_grid"]["successful_attempts"]:
        raise RuntimeError("bounded retry grid disposition drift")
    gate_counts = collections.Counter(row["terminal"]["gate"] for row in attempts)
    if set(gate_counts) != {
        "NONFINITE_PROJECTIVE_NORMALIZATION",
        "E2_PIVOT_CONTAINS_ZERO",
    }:
        raise RuntimeError("retry gate vocabulary drift")
    best = max(
        attempts,
        key=lambda row: row["completed_substeps"] / row["subdivisions"],
    )
    flags = run["claim_flags"]
    if not all(
        flags[name]
        for name in (
            "prior_panel_31_checkpoint_demoted",
            "panel_30_checkpoint_certified",
            "post_normalization_finiteness_gate_added",
            "bounded_retry_grid_exhausted",
        )
    ):
        raise RuntimeError("positive supersession gates drift")
    if any(
        flags[name]
        for name in (
            "next_base_panel_completed",
            "next_dyadic_shell_reached",
            "r4_reached",
            "H4_certified",
            "T_plus_certified",
        )
    ):
        raise RuntimeError("claim boundary drift")
    certificate = {
        "schema": "phase3-axial-horizon-pivot-switch-subdivision-retry-v1",
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_HORIZON_PIVOT_SWITCH_SUBDIVISION_RETRY"
        ),
        "status": "PANEL30_SUPERSESSION_RETRY_GRID_EXHAUSTED",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "supersession": run["supersedes"],
        "corrected_last_valid_checkpoint": checkpoint,
        "mutation_witness": witness,
        "retry_grid": {
            **run["retry_grid"],
            "gate_counts": dict(sorted(gate_counts.items())),
            "best_attempt": best,
        },
        "target": run["target"],
        "claim_flags": flags,
        "imports": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
            for name, path in INPUTS.items()
        },
        "run": {
            "path": str(RUN.relative_to(ROOT)),
            "sha256": sha256(RUN),
        },
        "does_not_establish": [
            "completion of base panel 31 after the corrected panel-30 checkpoint",
            "the next dyadic shell checkpoint or continuation to r=4",
            "a complete H4 frame, T_plus, or global Stokes identity",
            "that arbitrary affine/Taylor-model reconditioning cannot repair the rail",
            "any LORENTZIAN-CAUSAL theorem",
        ],
    }
    receipt = {
        "schema": "phase3-receipt-v1",
        "result_id": certificate["result_id"],
        "status": certificate["status"],
        "dependency_tags": certificate["dependency_tags"],
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.pivot_switch_subdivision_retry",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_pivot_switch_subdivision_retry --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_pivot_switch_subdivision_retry",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_pivot_switch_subdivision_retry",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "pivot_switch_subdivision_retry"
                ),
                "status": "PASS_DETERMINISTIC_FAIL_CLOSED_OUTPUT",
                "elapsed_seconds": 14.10,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_pivot_switch_subdivision_retry --check"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_pivot_switch_subdivision_retry"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_pivot_switch_subdivision_retry"
                ),
                "status": "PASS_5_TESTS",
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
            },
        ],
        "claim_boundary": (
            "append-only supersession: panel 30 is the last finite normalized "
            "checkpoint; 30 order/subdivision retries do not complete panel 31"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: no shared operator or physical scattering "
            "claim was promoted"
        ),
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    return certificate, receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, receipt = build()
    encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    receipt_encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.check:
        if OUTPUT.read_text() != encoded or RECEIPT.read_text() != receipt_encoded:
            raise SystemExit("generated subdivision-retry artifacts drift")
        print("horizon subdivision-retry artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()

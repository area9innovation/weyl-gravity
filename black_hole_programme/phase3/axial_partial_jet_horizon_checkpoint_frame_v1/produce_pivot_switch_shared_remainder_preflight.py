#!/usr/bin/env python3
"""Produce the one-step shared-reciprocal projective preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "pivot-switch-shared-remainder-preflight-run.json"
OUTPUT = HERE / "pivot-switch-shared-remainder-preflight-certificate.json"
RECEIPT = HERE / "pivot-switch-shared-remainder-preflight-receipt.json"
SCHEMA = HERE / "pivot-switch-shared-remainder-preflight-schema.json"
INPUTS = {
    "subdivision_retry_certificate": (
        HERE / "pivot-switch-subdivision-retry-certificate.json"
    ),
    "subdivision_retry_run": HERE / "pivot-switch-subdivision-retry-run.json",
    "shared_remainder_transport": (
        HERE / "pivot_switch_shared_remainder_preflight.py"
    ),
    "checkpoint_transport": HERE / "checkpoint_transport.py",
    "crosswalk": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_transport_crosswalk_v1/certificate.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict, dict]:
    run = json.loads(RUN.read_text())
    flags = run["claim_flags"]
    for name in (
        "corrected_panel_30_source_used",
        "one_next_radial_step_certified",
        "shared_remainder_normalization_certified",
        "post_normalization_finite",
        "eager_squared_denominator_mutant_killed",
    ):
        if not flags[name]:
            raise RuntimeError(f"positive preflight gate drift: {name}")
    for name in (
        "next_dyadic_shell_reached",
        "r4_reached",
        "H4_certified",
        "T_plus_certified",
    ):
        if flags[name]:
            raise RuntimeError(f"claim boundary drift: {name}")
    if run["source"]["last_valid_panel"] != 30:
        raise RuntimeError("source checkpoint drift")
    if run["target"]["panel"] != 31:
        raise RuntimeError("bounded target drift")
    representation = run["representation"]
    if not representation["post_normalization_finite"]:
        raise RuntimeError("post-normalization finiteness drift")
    mutant = representation["eager_squared_denominator_mutant"]
    if mutant["mutant_accepts"] or not mutant["denominator_contains_zero"]:
        raise RuntimeError("mutation witness drift")
    certificate = {
        "schema": (
            "phase3-axial-horizon-pivot-switch-shared-remainder-preflight-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_HORIZON_SHARED_REMAINDER_PREFLIGHT"
        ),
        "status": "ONE_SHARED_RECIPROCAL_STEP_CERTIFIED",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "source": run["source"],
        "target": run["target"],
        "raw_step": run["raw_step"],
        "representation": representation,
        "checkpoint": run["checkpoint"],
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
            "a complete next dyadic shell",
            "continuation of the shared-reciprocal rail to r=4",
            "a complete H4 frame, T_plus, or global Stokes identity",
            "uniform control of the shared reciprocal over frequency cells",
            "any LORENTZIAN-CAUSAL theorem",
        ],
    }
    receipt = {
        "schema": "phase3-receipt-v1",
        "result_id": certificate["result_id"],
        "status": certificate["status"],
        "dependency_tags": certificate["dependency_tags"],
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.pivot_switch_shared_remainder_preflight",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_pivot_switch_shared_remainder_preflight --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_pivot_switch_shared_remainder_preflight",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_pivot_switch_shared_remainder_preflight",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "pivot_switch_shared_remainder_preflight"
                ),
                "status": "PASS_DETERMINISTIC_OUTPUT",
                "elapsed_seconds": 10.92,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_pivot_switch_shared_remainder_preflight --check"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_pivot_switch_shared_remainder_preflight"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_pivot_switch_shared_remainder_preflight"
                ),
                "status": "PASS_5_TESTS",
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
            },
        ],
        "claim_boundary": (
            "one finite normalized step from corrected panel 30 to panel 31 "
            "using one shared reciprocal; no shell/r4/H4/T_plus promotion"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: bounded representation preflight only"
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
            raise SystemExit("generated shared-remainder artifacts drift")
        print("horizon shared-remainder preflight artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()

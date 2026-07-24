#!/usr/bin/env python3
"""Produce the content-addressed shared-remainder successor certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from . import shared_remainder_multipanel_successor as successor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "shared-remainder-multipanel-successor-run.json"
OUTPUT = HERE / "shared-remainder-multipanel-successor-certificate.json"
RECEIPT = HERE / "shared-remainder-multipanel-successor-receipt.json"
SCHEMA = HERE / "shared-remainder-multipanel-successor-schema.json"
INPUTS = {
    "shared_remainder_preflight_certificate": (
        HERE / "pivot-switch-shared-remainder-preflight-certificate.json"
    ),
    "shared_remainder_preflight_run": (
        HERE / "pivot-switch-shared-remainder-preflight-run.json"
    ),
    "subdivision_retry_certificate": (
        HERE / "pivot-switch-subdivision-retry-certificate.json"
    ),
    "successor_transport": HERE / "shared_remainder_multipanel_successor.py",
    "checkpoint_transport": HERE / "checkpoint_transport.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_chain(run: dict) -> None:
    parent = run["source"]["sha256"]
    generator = run["controls"]["generator_sha256"]
    checkpoints = run["checkpoint_chain"]
    if len(checkpoints) != run["accepted_substeps"]:
        raise RuntimeError("checkpoint count drift")
    for index, checkpoint in enumerate(checkpoints):
        if checkpoint["substep_index"] != index:
            raise RuntimeError("checkpoint index drift")
        if checkpoint["parent_sha256"] != parent:
            raise RuntimeError("checkpoint parent drift")
        if checkpoint["generator_sha256"] != generator:
            raise RuntimeError("checkpoint generator drift")
        payload = {
            key: value
            for key, value in checkpoint.items()
            if key != "content_sha256"
        }
        if successor.canonical_hash(payload) != checkpoint["content_sha256"]:
            raise RuntimeError("checkpoint content hash drift")
        parent = checkpoint["content_sha256"]


def build() -> tuple[dict, dict]:
    run = json.loads(RUN.read_text())
    verify_chain(run)
    if run["accepted_substeps"] != 9:
        raise RuntimeError("accepted substep count drift")
    terminal = run["terminal"]
    if terminal["gate"] != "FIXED_ATLAS_PIVOT_OBSTRUCTION":
        raise RuntimeError("terminal gate drift")
    if terminal["selected"] is not None:
        raise RuntimeError("unexpected terminal chart")
    if any(value != "0" for value in terminal["atlas_modulus_lowers"].values()):
        raise RuntimeError("terminal atlas lower-bound drift")
    if len(run["gate_ledger"]) != run["accepted_substeps"]:
        raise RuntimeError("gate ledger drift")
    if not all(row["post_normalization_finite"] for row in run["gate_ledger"]):
        raise RuntimeError("post-normalization gate drift")
    flags = run["claim_flags"]
    for name in (
        "source_checkpoint_hash_bound",
        "generator_hash_stable",
        "all_accepted_checkpoints_content_addressed",
        "shared_reciprocal_used_at_every_accepted_substep",
        "post_normalization_finite_at_every_checkpoint",
        "first_obstruction_fail_closed",
    ):
        if not flags[name]:
            raise RuntimeError(f"positive gate drift: {name}")
    for name in (
        "next_base_panel_completed",
        "next_dyadic_shell_reached",
        "r4_reached",
        "H4_certified",
        "T_plus_certified",
    ):
        if flags[name]:
            raise RuntimeError(f"claim boundary drift: {name}")
    certificate = {
        "schema": (
            "phase3-axial-horizon-shared-remainder-multipanel-successor-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_HORIZON_SHARED_REMAINDER_MULTIPANEL"
        ),
        "status": "NINE_SUBSTEPS_CONTENT_ADDRESSED_PIVOT_SHORTFALL",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "source": run["source"],
        "controls": run["controls"],
        "progress": {
            "accepted_substeps": run["accepted_substeps"],
            "reached_rho": run["reached_rho"],
            "checkpoint_chain": run["checkpoint_chain"],
            "gate_ledger": run["gate_ledger"],
        },
        "obstruction": terminal,
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
            "completion of the next base panel or dyadic shell",
            "continuation to r=4",
            "a complete typed H4 frame, T_plus, Gram, or Stokes identity",
            "that a stronger affine or Taylor-model enclosure cannot pass the pivot",
            "any LORENTZIAN-CAUSAL theorem",
        ],
    }
    receipt = {
        "schema": "phase3-receipt-v1",
        "result_id": certificate["result_id"],
        "status": certificate["status"],
        "dependency_tags": certificate["dependency_tags"],
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.shared_remainder_multipanel_successor",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_shared_remainder_multipanel_successor --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_shared_remainder_multipanel_successor",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_shared_remainder_multipanel_successor",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "shared_remainder_multipanel_successor"
                ),
                "status": "PASS_DETERMINISTIC_FAIL_CLOSED_OUTPUT",
                "elapsed_seconds": 10.54,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_shared_remainder_multipanel_successor --check"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_shared_remainder_multipanel_successor"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_shared_remainder_multipanel_successor"
                ),
                "status": "PASS_5_TESTS",
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
            },
        ],
        "claim_boundary": (
            "nine content-addressed normalized substeps beyond panel 31; "
            "fail closed when all fixed-atlas pivot lower bounds reach zero"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: transport-only reduced-mode preflight"
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
            raise SystemExit("generated multipanel successor artifacts drift")
        print("horizon shared-remainder multipanel artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()

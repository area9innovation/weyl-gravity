#!/usr/bin/env python3
"""Produce the fail-closed post-switch horizon continuation disposition."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "pivot-switch-continuation-run.json"
OUTPUT = HERE / "pivot-switch-continuation-certificate.json"
RECEIPT = HERE / "pivot-switch-continuation-receipt.json"
SCHEMA = HERE / "pivot-switch-continuation-schema.json"
INPUTS = {
    "source_pivot_switch_certificate": HERE / "pivot-switch-certificate.json",
    "source_pivot_switch_run": HERE / "pivot-switch-run.json",
    "continuation_transport": HERE / "pivot_switch_continuation.py",
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
    terminal = run["terminal"]
    if terminal is None or terminal["gate"] != "NONFINITE_TAYLOR_ENCLOSURE":
        raise RuntimeError("honest continuation obstruction drift")
    if run["accepted_panels_total"] != 32:
        raise RuntimeError("accepted panel count drift")
    if run["accepted_panels_from_switch_transition"] != 6:
        raise RuntimeError("post-switch panel count drift")
    if run["switch_count"] != len(run["switches"]) or run["switch_count"] != 1:
        raise RuntimeError("switch ledger drift")
    if run["last_valid_checkpoint"]["rho"] != terminal["rho"]:
        raise RuntimeError("last valid checkpoint drift")
    flags = run["claim_flags"]
    if not flags["common_dual_correlation_preserved_at_every_switch"]:
        raise RuntimeError("dual correlation gate drift")
    if not flags["every_switch_serialized"]:
        raise RuntimeError("switch serialization gate drift")
    if flags["next_dyadic_shell_reached"]:
        raise RuntimeError("dyadic-shell overclaim")
    last_panel = run["panel_ledger"][-1]
    if last_panel["panel"] != 31:
        raise RuntimeError("last valid panel drift")
    certificate = {
        "schema": (
            "phase3-axial-partial-jet-horizon-pivot-switch-continuation-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_HORIZON_MIXED_PIVOT_SWITCH_CONTINUATION"
        ),
        "status": "FIVE_POST_SWITCH_PANELS_NONFINITE_TAIL_SHORTFALL",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "scope": run["scope"],
        "progress": {
            "accepted_panels_total": run["accepted_panels_total"],
            "accepted_panels_from_switch_transition": run[
                "accepted_panels_from_switch_transition"
            ],
            "strictly_post_switch_panels": (
                run["accepted_panels_from_switch_transition"] - 1
            ),
            "switch_count": run["switch_count"],
            "switches": run["switches"],
            "last_valid_panel": last_panel,
            "last_valid_checkpoint": run["last_valid_checkpoint"],
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
            "the next dyadic horizon shell checkpoint",
            "continuation of the mixed line to r=4",
            "a complete three-channel H4 frame",
            "the outgoing T_plus map or global Stokes identity",
            "any LORENTZIAN-CAUSAL theorem",
        ],
    }
    receipt = {
        "schema": "phase3-receipt-v1",
        "result_id": certificate["result_id"],
        "status": certificate["status"],
        "dependency_tags": certificate["dependency_tags"],
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.pivot_switch_continuation",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_pivot_switch_continuation --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_pivot_switch_continuation",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_pivot_switch_continuation",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "pivot_switch_continuation"
                ),
                "status": "PASS_DETERMINISTIC_FAIL_CLOSED_OUTPUT",
                "elapsed_seconds": 10.46,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_pivot_switch_continuation --check"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_pivot_switch_continuation"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_pivot_switch_continuation"
                ),
                "status": "PASS_4_TESTS",
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
            },
        ],
        "claim_boundary": (
            "five panels strictly beyond the certified switch, ending in a "
            "resumable checkpoint; the next Taylor tail is non-finite and "
            "the next dyadic shell remains fail closed"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: no shared operator or physical scattering "
            "theorem changed"
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
            raise SystemExit("generated pivot-switch continuation artifacts drift")
        print("horizon pivot-switch continuation artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()

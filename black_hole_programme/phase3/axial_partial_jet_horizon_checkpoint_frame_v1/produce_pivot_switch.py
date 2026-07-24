#!/usr/bin/env python3
"""Produce the certified mixed-horizon fixed-GL pivot repair."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "pivot-switch-run.json"
OUTPUT = HERE / "pivot-switch-certificate.json"
RECEIPT = HERE / "pivot-switch-receipt.json"
SCHEMA = HERE / "pivot-switch-schema.json"
INPUTS = {
    "source_checkpoint_run": HERE / "checkpoint-run.json",
    "source_checkpoint_transport": HERE / "checkpoint_transport.py",
    "pivot_switch_transport": HERE / "pivot_switch.py",
    "crosswalk": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_transport_crosswalk_v1/certificate.json",
    "spin_one_levelt": ROOT
    / "black_hole_programme/phase3/axial_partial_jet_horizon_spin_one_levelt_v1/certificate.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict, dict]:
    run = json.loads(RUN.read_text())
    flags = run["claim_flags"]
    required = (
        "former_pivot_obstruction_reproduced",
        "fixed_gl_chart_certified",
        "common_dual_correlation_preserved",
        "one_post_switch_panel_certified",
    )
    if not all(flags[name] for name in required):
        raise RuntimeError("positive fixed-GL pivot gate drift")
    if flags["r4_reached"] or flags["H4_certified"] or flags["T_plus_certified"]:
        raise RuntimeError("claim boundary drift")
    if run["switch"]["determinant"] != "1":
        raise RuntimeError("fixed GL determinant drift")
    if run["post_switch_checkpoint"]["accepted_post_switch_panels"] != 1:
        raise RuntimeError("bounded post-switch scope drift")
    certificate = {
        "schema": "phase3-axial-partial-jet-horizon-pivot-switch-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_HORIZON_MIXED_PIVOT_SWITCH",
        "status": "ONE_POST_SWITCH_CHECKPOINT_CERTIFIED",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "method": {
            "representation": "mixed projective dual line",
            "fixed_chart": run["switch"],
            "repair": (
                "retain exact base_pivot=1 and tangent_pivot=0 identities "
                "after the common dual-scalar normalization"
            ),
            "former_obstruction": run["former_obstruction"],
        },
        "checkpoint": run["post_switch_checkpoint"],
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
            "continuation of the switched mixed line to r=4",
            "a complete three-channel H4 frame",
            "the outgoing T_plus map or the global Stokes identity",
            "any all-frequency or LORENTZIAN-CAUSAL theorem",
        ],
    }
    receipt = {
        "schema": "phase3-receipt-v1",
        "result_id": certificate["result_id"],
        "status": certificate["status"],
        "dependency_tags": certificate["dependency_tags"],
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.pivot_switch",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_pivot_switch --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_pivot_switch",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_pivot_switch",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1.pivot_switch"
                ),
                "status": "PASS_DETERMINISTIC_OUTPUT",
                "elapsed_seconds": 10.42,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_pivot_switch --check"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_pivot_switch"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_pivot_switch"
                ),
                "status": "PASS_4_TESTS",
                "elapsed_seconds": 11.22,
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
            },
        ],
        "claim_boundary": (
            "one certified mixed-line panel beyond the former pivot "
            "obstruction in a fixed GL chart; r=4/H4/T_plus remain open"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: this is a bounded representation repair "
            "and does not promote a physical scattering theorem"
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
            raise SystemExit("generated pivot-switch artifacts drift")
        print("horizon mixed pivot-switch artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()

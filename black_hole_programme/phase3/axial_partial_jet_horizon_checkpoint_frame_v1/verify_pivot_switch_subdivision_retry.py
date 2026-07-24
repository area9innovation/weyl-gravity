#!/usr/bin/env python3
"""Independent verifier for the panel-30 supersession and retry grid."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads(
        (HERE / "pivot-switch-subdivision-retry-certificate.json").read_text()
    )
    schema = json.loads(
        (HERE / "pivot-switch-subdivision-retry-schema.json").read_text()
    )
    Draft202012Validator(schema).validate(cert)
    require(
        cert["status"] == "PANEL30_SUPERSESSION_RETRY_GRID_EXHAUSTED",
        "status",
    )
    require(
        cert["supersession"]["result_id"]
        == "PURE_WEYL_PHASE3_AXIAL_HORIZON_MIXED_PIVOT_SWITCH_CONTINUATION",
        "superseded result",
    )
    checkpoint = cert["corrected_last_valid_checkpoint"]
    require(checkpoint["panel"] == 30, "checkpoint panel")
    require(checkpoint["rho"] == "95/268435456", "checkpoint rho")
    witness = cert["mutation_witness"]
    require(witness["raw_taylor_state_finite"], "raw state")
    require(witness["pivot_gate_passed"], "pivot gate")
    require(witness["old_check_order_would_accept"], "old mutation")
    require(not witness["normalized_state_finite"], "normalized state")
    require(not witness["corrected_check_accepts"], "corrected gate")
    grid = cert["retry_grid"]
    require(len(grid["attempts"]) == 30, "grid size")
    require(not grid["successful_attempts"], "unexpected success")
    require(
        set(grid["gate_counts"])
        == {"NONFINITE_PROJECTIVE_NORMALIZATION", "E2_PIVOT_CONTAINS_ZERO"},
        "gate vocabulary",
    )
    flags = cert["claim_flags"]
    require(flags["prior_panel_31_checkpoint_demoted"], "demotion")
    require(flags["panel_30_checkpoint_certified"], "checkpoint")
    require(flags["post_normalization_finiteness_gate_added"], "gate")
    require(not flags["next_base_panel_completed"], "panel overclaim")
    require(not flags["next_dyadic_shell_reached"], "shell overclaim")
    for item in cert["imports"].values():
        path = ROOT / item["path"]
        require(path.exists(), f"missing import {path}")
        require(sha256(path) == item["sha256"], f"hash drift {path}")
    run = ROOT / cert["run"]["path"]
    require(sha256(run) == cert["run"]["sha256"], "run hash")
    print("PASS independent horizon subdivision-retry verifier")


if __name__ == "__main__":
    main()

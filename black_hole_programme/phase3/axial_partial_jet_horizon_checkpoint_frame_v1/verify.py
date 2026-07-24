#!/usr/bin/env python3
"""Independent structural verification for the horizon checkpoint result."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    data = json.loads((HERE / "certificate.json").read_text())
    if data["status"] != "CANONICAL_KH_ZERO_CHECKPOINT_PIVOT_SHORTFALL":
        raise RuntimeError("status drift")
    frame = data["canonical_endpoint_frame"]
    if frame["K_H"] != [["0", "0"], ["0", "0"]]:
        raise RuntimeError("canonical K_H drift")
    if not frame["zero_residuals"]:
        raise RuntimeError("endpoint recurrence residual failed")
    flags = data["claim_flags"]
    for key in (
        "canonical_tau_analytic_horizon_frame_constructed",
        "K_H_computed",
        "K_H_exactly_zero_in_canonical_frame",
    ):
        if not flags[key]:
            raise RuntimeError(f"positive endpoint gate failed: {key}")
    for key in (
        "horizon_to_r4_column_certified",
        "complete_three_channel_frame_at_r4",
        "H4_pass_certified",
        "T_plus_recovered",
    ):
        if flags[key]:
            raise RuntimeError(f"fail-closed gate promoted: {key}")
    transport = data["checkpoint_transport"]
    if (
        transport["reached_r4"]
        or transport["accepted_panels"] != 27
        or transport["first_obstruction"]["gate"] != "PROJECTIVE_PIVOT"
        or transport["first_obstruction"]["mixed"]["gate"]
        != "PIVOT_CONTAINS_ZERO"
    ):
        raise RuntimeError("transport disposition drift")
    run = ROOT / transport["run_path"]
    if sha256(run) != transport["run_sha256"]:
        raise RuntimeError("run hash drift")
    for imported in data["imports"].values():
        path = ROOT / imported["path"]
        if sha256(path) != imported["sha256"]:
            raise RuntimeError(f"import drift: {path}")
    print("horizon canonical K_H/checkpoint verification: PASS")


if __name__ == "__main__":
    verify()

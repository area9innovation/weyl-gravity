#!/usr/bin/env python3
"""Independent verifier for the bounded post-switch continuation."""
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
        (HERE / "pivot-switch-continuation-certificate.json").read_text()
    )
    schema = json.loads(
        (HERE / "pivot-switch-continuation-schema.json").read_text()
    )
    Draft202012Validator(schema).validate(cert)
    require(
        cert["status"] == "FIVE_POST_SWITCH_PANELS_NONFINITE_TAIL_SHORTFALL",
        "status",
    )
    progress = cert["progress"]
    require(progress["accepted_panels_total"] == 32, "total panels")
    require(progress["strictly_post_switch_panels"] == 5, "post-switch panels")
    require(progress["switch_count"] == len(progress["switches"]) == 1, "switches")
    switch = progress["switches"][0]
    require(switch["selected"] == "e2-e3", "switch row")
    require(switch["pivot"]["exact_base_pivot"] == "1", "base identity")
    require(switch["pivot"]["exact_tangent_pivot"] == "0", "tangent identity")
    require(cert["obstruction"]["gate"] == "NONFINITE_TAYLOR_ENCLOSURE", "gate")
    require(
        progress["last_valid_checkpoint"]["rho"] == cert["obstruction"]["rho"],
        "checkpoint rho",
    )
    flags = cert["claim_flags"]
    require(flags["common_dual_correlation_preserved_at_every_switch"], "correlation")
    require(flags["every_switch_serialized"], "serialization")
    require(not flags["next_dyadic_shell_reached"], "dyadic overclaim")
    require(not flags["r4_reached"], "r4 overclaim")
    for item in cert["imports"].values():
        path = ROOT / item["path"]
        require(path.exists(), f"missing import {path}")
        require(sha256(path) == item["sha256"], f"hash drift {path}")
    run = ROOT / cert["run"]["path"]
    require(sha256(run) == cert["run"]["sha256"], "run hash")
    print("PASS independent horizon pivot-switch continuation verifier")


if __name__ == "__main__":
    main()

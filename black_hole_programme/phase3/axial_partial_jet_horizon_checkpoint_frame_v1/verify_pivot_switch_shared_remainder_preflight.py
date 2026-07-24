#!/usr/bin/env python3
"""Independent verifier for the shared-reciprocal one-step preflight."""
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
        (HERE / "pivot-switch-shared-remainder-preflight-certificate.json").read_text()
    )
    schema = json.loads(
        (HERE / "pivot-switch-shared-remainder-preflight-schema.json").read_text()
    )
    Draft202012Validator(schema).validate(cert)
    require(cert["status"] == "ONE_SHARED_RECIPROCAL_STEP_CERTIFIED", "status")
    require(cert["source"]["last_valid_panel"] == 30, "source panel")
    require(cert["target"]["panel"] == 31, "target panel")
    representation = cert["representation"]
    require(
        representation["kind"] == "shared-reciprocal dual projective chart",
        "representation",
    )
    require(representation["post_normalization_finite"], "post normalization")
    normalization = representation["normalization"]
    require(normalization["passed"], "normalization gate")
    require(normalization["exact_base_pivot"] == "1", "base pivot")
    require(normalization["exact_tangent_pivot"] == "0", "tangent pivot")
    mutant = representation["eager_squared_denominator_mutant"]
    require(mutant["denominator_contains_zero"], "mutant denominator")
    require(not mutant["normalized_tangent_finite"], "mutant tangent")
    require(not mutant["mutant_accepts"], "mutant acceptance")
    flags = cert["claim_flags"]
    require(flags["post_normalization_finite"], "finite flag")
    require(flags["eager_squared_denominator_mutant_killed"], "mutation flag")
    require(not flags["next_dyadic_shell_reached"], "shell overclaim")
    require(not flags["r4_reached"], "r4 overclaim")
    for item in cert["imports"].values():
        path = ROOT / item["path"]
        require(path.exists(), f"missing import {path}")
        require(sha256(path) == item["sha256"], f"hash drift {path}")
    run = ROOT / cert["run"]["path"]
    require(sha256(run) == cert["run"]["sha256"], "run hash")
    print("PASS independent horizon shared-remainder preflight verifier")


if __name__ == "__main__":
    main()

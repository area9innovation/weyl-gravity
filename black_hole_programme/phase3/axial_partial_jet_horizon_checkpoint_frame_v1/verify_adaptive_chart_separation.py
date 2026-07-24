#!/usr/bin/env python3
"""Independent verifier for the fixed-linear chart obstruction."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from . import adaptive_chart_separation as audit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads(
        (HERE / "adaptive-chart-separation-certificate.json").read_text()
    )
    schema = json.loads(
        (HERE / "adaptive-chart-separation-schema.json").read_text()
    )
    Draft202012Validator(schema).validate(cert)
    require(
        cert["status"] == "UNIVERSAL_CARTESIAN_FIXED_CHART_OBSTRUCTION",
        "status",
    )
    enclosure = cert["terminal_raw_enclosure"]
    require(enclosure["state_finite"], "state finiteness")
    require(all(enclosure["base_component_zero_membership"]), "zero membership")
    require(enclosure["zero_vector_in_cartesian_base_enclosure"], "zero vector")
    require(
        audit.canonical_hash(enclosure["payload"]) == enclosure["content_sha256"],
        "enclosure hash",
    )
    midpoint = cert["midpoint_adaptive_chart"]
    require(midpoint["determinant"] == "1", "midpoint GL determinant")
    require(midpoint["candidate"]["midpoint_modulus_nonzero"], "midpoint center")
    require(not midpoint["candidate"]["excludes_zero"], "midpoint full ball")
    require(not midpoint["certified"], "midpoint chart overclaim")
    require(
        not any(row["excludes_zero"] for row in cert["finite_candidate_atlas"].values()),
        "candidate atlas",
    )
    require(cert["universal_linear_separation"]["certified"], "universal theorem")
    mutation = cert["mutation_witness"]
    require(mutation["mutant_accepts"], "mutant premise")
    require(not mutation["correct_full_ball_gate_accepts"], "correct gate")
    require(mutation["mutation_killed"], "mutation kill")
    require(
        cert["terminal"]["gate"]
        == "UNIVERSAL_FIXED_LINEAR_CHART_SEPARATION_OBSTRUCTION",
        "terminal gate",
    )
    require(not cert["claim_flags"]["successor_substep_certified"], "successor")
    for item in cert["imports"].values():
        path = ROOT / item["path"]
        require(path.exists(), f"missing import {path}")
        require(sha256(path) == item["sha256"], f"hash drift {path}")
    run = ROOT / cert["run"]["path"]
    require(sha256(run) == cert["run"]["sha256"], "run hash")
    print("PASS independent adaptive-chart separation verifier")


if __name__ == "__main__":
    main()

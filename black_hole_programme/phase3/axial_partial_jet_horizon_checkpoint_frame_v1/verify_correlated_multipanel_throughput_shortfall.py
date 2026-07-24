#!/usr/bin/env python3
"""Independent verifier for the correlated multipanel throughput shortfall."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "correlated-multipanel-throughput-shortfall-certificate.json"
SCHEMA = HERE / "correlated-multipanel-throughput-shortfall-schema.json"
ABSENT_RUN = HERE / "correlated-affine-multipanel-successor-run.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    if certificate["status"] != "THROUGHPUT_SHORTFALL_NO_MULTIPANEL_CLAIM":
        raise SystemExit("status drift")
    if ABSENT_RUN.exists():
        raise SystemExit("multipanel run now exists and needs separate audit")
    for row in certificate["imports"].values():
        path = ROOT / row["path"]
        if sha256(path) != row["sha256"]:
            raise SystemExit(f"import hash drift: {path}")
    one_step = json.loads(
        (HERE / "correlated-affine-seed-successor-certificate.json").read_text()
    )
    resume = certificate["split_contract"]["resume_source"]
    if resume["content_sha256"] != one_step["successor_model"]["content_sha256"]:
        raise SystemExit("resume model hash drift")
    prototype = ast.parse(
        (HERE / "correlated_affine_multipanel_successor.py").read_text()
    )
    functions = {
        node.name
        for node in ast.walk(prototype)
        if isinstance(node, ast.FunctionDef)
    }
    if not {
        "generator_joint_coefficients",
        "cached_generator",
        "checkpoint",
    } <= functions:
        raise SystemExit("prototype code audit drift")
    attempt = certificate["observed_attempt"]
    if attempt["termination"] != "FAST_RAIL_TIMEOUT":
        raise SystemExit("termination drift")
    if attempt["run_artifact_written"]:
        raise SystemExit("absent output promoted")
    if certificate["terminal"]["multipanel_result_certified"]:
        raise SystemExit("multipanel result overclaim")
    print("correlated multipanel throughput shortfall verifier: PASS")


if __name__ == "__main__":
    main()

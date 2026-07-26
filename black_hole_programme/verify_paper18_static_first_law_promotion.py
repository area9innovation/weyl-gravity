#!/usr/bin/env python3
"""Fail-closed verifier for the append-only Paper 18 promotion record."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates" / "PAPER18_STATIC_FIRST_LAW_PROMOTION.json"
SCHEMA = HERE / "schema" / "paper18-static-first-law-promotion-v1.schema.json"
PRODUCER = HERE / "paper18_static_first_law_promotion.py"
STDLIB = ROOT / "paper" / "verify_18_static_weyl_thermodynamics_stdlib.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_producer():
    spec = importlib.util.spec_from_file_location("paper18_promotion", PRODUCER)
    require(spec is not None and spec.loader is not None, "cannot load producer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    require(CERTIFICATE.exists(), "promotion certificate missing")
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    require(payload["schema_sha256"] == sha256(SCHEMA), "schema hash mismatch")
    require(payload == load_producer().build(), "promotion certificate is stale or mutated")

    for name, row in payload["evidence"].items():
        path = ROOT / row["path"]
        require(path.exists(), f"missing evidence {name}")
        require(row["sha256"] == sha256(path), f"evidence hash mismatch: {name}")
        record = json.loads(path.read_text(encoding="utf-8"))
        require(record["result_token"] == row["result_token"], f"result token mismatch: {name}")

    flags = payload["claim_flags"]
    for name in (
        "laurent_classification_certified",
        "residual_basic_normalization_certified",
        "simultaneous_static_first_law_certified",
        "linear_spherical_gauge_audit_certified",
    ):
        require(flags[name], f"positive promotion flag is false: {name}")
    require(not flags["physical_process_first_law_certified"], "physical-process claim escaped boundary")
    require(not flags["radiative_flux_certified"], "radiative-flux claim escaped boundary")
    require(payload["declaration"]["historical_certificates_unchanged"], "append-only history declaration missing")
    require(not payload["declaration"]["expert_peer_reviewed"], "certificate falsely claims peer review")

    completed = subprocess.run(
        [sys.executable, str(STDLIB)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    require(completed.returncode == 0, f"stdlib verifier failed: {completed.stdout}{completed.stderr}")
    require("independent exact Paper 18 algebra checks" in completed.stdout, "stdlib pass token missing")
    print("PASS Paper 18 append-only promotion certificate and independent algebra rail")


if __name__ == "__main__":
    main()

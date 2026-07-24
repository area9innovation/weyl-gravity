#!/usr/bin/env python3
"""Independent verifier for the bounded projective transport shortfall."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    doc = json.loads(CERTIFICATE.read_text())
    if doc["status"] != (
        "CERTIFIED_PROJECTIVE_THROUGHPUT_AND_PIVOT_SHORTFALL"
    ):
        raise RuntimeError("status drift")
    for item in doc["imports"].values():
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise RuntimeError(f"import hash drift: {path}")

    midpoint = doc["midpoint_lohner_attempt"]
    for name in ("source", "compile_log", "run_log"):
        path = ROOT / midpoint[f"{name}_path"]
        if sha256(path) != midpoint[f"{name}_sha256"]:
            raise RuntimeError(f"{name} hash drift")
    if (ROOT / midpoint["compile_log_path"]).read_text():
        raise RuntimeError("compiler diagnostics are nonempty")
    if (ROOT / midpoint["run_log_path"]).read_text().strip() != (
        "TIMEOUT_240_SECONDS"
    ):
        raise RuntimeError("timeout marker drift")
    if not (
        midpoint["compile_exit"] == 0
        and midpoint["run_exit"] == 124
        and midpoint["status"] == "TIMEOUT"
        and not midpoint["completed_panel_diagnostics_available"]
    ):
        raise RuntimeError("midpoint timeout boundary drift")

    fixed = doc["fixed_full_pivot_attempt"]
    if not (
        fixed["status"] == "REFUSED"
        and fixed["gate"] == "pivot_solve"
        and fixed["shell"] == 0
        and fixed["panel"] == 5
        and fixed["total_panels"] == 5
        and fixed["refusal_code"] == 6
        and fixed["operator_tail"] < 3e-24
    ):
        raise RuntimeError("fixed-pivot refusal drift")
    if any(doc["claim_flags"].values()):
        raise RuntimeError("fail-closed claim flag promoted")
    print("PASS projective throughput and pivot shortfall")


if __name__ == "__main__":
    verify()

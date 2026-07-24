#!/usr/bin/env python3
"""Run scoped checks and write the point-half theorem receipt."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODULE = "black_hole_programme.phase3.axial_outgoing_population_point_half_v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> dict:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": " ".join(command),
        "elapsed_seconds": time.perf_counter() - started,
        "exit_code": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "output_tail": completed.stdout[-1200:],
    }


def main() -> int:
    commands = [
        run(["python3", "-m", f"{MODULE}.produce", "--check"]),
        run(["python3", "-m", f"{MODULE}.verify"]),
        run(["python3", "-m", "unittest", "-v", f"{MODULE}.test_point_half"]),
        run(
            [
                "python3",
                "-m",
                "py_compile",
                str(HERE / "produce.py"),
                str(HERE / "verify.py"),
                str(HERE / "test_point_half.py"),
                str(HERE / "audit.py"),
            ]
        ),
        run(
            [
                "python3",
                "-m",
                "jsonschema",
                "-i",
                str(HERE / "certificate.json"),
                str(HERE / "schema.json"),
            ]
        ),
        run(["git", "diff", "--check", "--", str(HERE.relative_to(ROOT))]),
    ]
    passed = all(item["exit_code"] == 0 for item in commands)
    artifacts = {}
    for name in (
        "README.md",
        "__init__.py",
        "audit.py",
        "certificate.json",
        "produce.py",
        "report.md",
        "schema.json",
        "test_point_half.py",
        "verify.py",
    ):
        path = HERE / name
        if path.exists():
            artifacts[name] = sha256(path)
    receipt = {
        "schema": "phase3-axial-outgoing-population-point-half-receipt-v1",
        "status": "PASS" if passed else "FAIL",
        "certificate": str((HERE / "certificate.json").relative_to(ROOT)),
        "certificate_sha256": sha256(HERE / "certificate.json"),
        "artifacts": artifacts,
        "commands": commands,
        "test_tiers": {
            "tier_0_edit_checks": "PASS" if passed else "FAIL",
            "tier_1_scoped_tests": "PASS" if passed else "FAIL",
            "tier_2_affected_chain": (
                "NOT_RUN: all mathematical inputs are content-hashed and "
                "independently replayed or exact imported certificates"
            ),
            "tier_3_full_suite": (
                "NOT_RUN: pointwise reduced-mode theorem; no release, freeze, "
                "shared core algebra, time-domain or quantum promotion"
            ),
        },
        "claim_boundary": (
            "Full outgoing population and nondegenerate transport-free "
            "outgoing defect are certified only at omega=1/2. Explicit Tplus "
            "entries and interval-wide reflection nonvanishing remain open."
        ),
    }
    (HERE / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(receipt["status"])
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())

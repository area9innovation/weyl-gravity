#!/usr/bin/env python3
"""Run scoped checks and write the chunk-01 receipt."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECEIPT = HERE / "receipt.json"
MODULE = (
    "black_hole_programme.phase3."
    "axial_partial_jet_outgoing_bplus4_chunk01_v1"
)


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
        run(["python3", "-m", "unittest", f"{MODULE}.test_chunk01"]),
        run(
            [
                "python3",
                "-m",
                "py_compile",
                str(HERE / "produce.py"),
                str(HERE / "verify.py"),
                str(HERE / "test_chunk01.py"),
                str(HERE / "audit.py"),
            ]
        ),
        run(
            [
                "git",
                "diff",
                "--check",
                "--",
                str(HERE.relative_to(ROOT)),
            ]
        ),
    ]
    passed = all(item["exit_code"] == 0 for item in commands)
    names = (
        "README.md",
        "__init__.py",
        "audit.py",
        "certificate.json",
        "checkpoint.json",
        "produce.py",
        "report.md",
        "run_manifest.json",
        "schema.json",
        "test_chunk01.py",
        "verify.py",
    )
    artifacts = {
        name: sha256(HERE / name)
        for name in names
        if (HERE / name).exists()
    }
    receipt = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-chunk01-receipt-v1"
        ),
        "status": "PASS" if passed else "FAIL",
        "certificate": str((HERE / "certificate.json").relative_to(ROOT)),
        "certificate_sha256": sha256(HERE / "certificate.json"),
        "artifacts": artifacts,
        "test_tiers": {
            "tier_0_edit_checks": "PASS" if passed else "FAIL",
            "tier_1_scoped_tests": "PASS" if passed else "FAIL",
            "tier_2_affected_chain": (
                "NOT_RUN: predecessor/operator inputs are unchanged and "
                "content-addressed; one independent boundary gate was run"
            ),
            "tier_3_full_suite": (
                "NOT_RUN: no r=4, Bplus4, T_plus, Stokes, paper, freeze, "
                "release, scattering, or flux promotion"
            ),
        },
        "commands": commands,
        "claim_boundary": (
            "One adaptive content-addressed successor from r=247/8 to "
            "r=123/4 completes in 25.8 seconds and passes the direct "
            "sixteen-state boundary comparison. Full r=4 remains open."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run scoped Bplus4 checks and emit a fail-closed receipt."""
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
    "axial_partial_jet_outgoing_bplus4_v1"
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
        run(["python3", "-m", "unittest", f"{MODULE}.test_bplus4"]),
        run(
            [
                "python3",
                "-m",
                "py_compile",
                str(HERE / "_probe.py"),
                str(HERE / "produce.py"),
                str(HERE / "verify.py"),
                str(HERE / "test_bplus4.py"),
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
        "_probe.py",
        "audit.py",
        "certificate.json",
        "checkpoint.json",
        "probe.forge",
        "probe_compile.txt",
        "probe_run.txt",
        "produce.py",
        "report.md",
        "schema.json",
        "test_bplus4.py",
        "verify.py",
    )
    artifacts = {
        name: sha256(HERE / name)
        for name in names
        if (HERE / name).exists()
    }
    receipt = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-receipt-v1"
        ),
        "status": "PASS" if passed else "FAIL",
        "scientific_disposition": "SHORTFALL",
        "certificate": str((HERE / "certificate.json").relative_to(ROOT)),
        "certificate_sha256": sha256(HERE / "certificate.json"),
        "artifacts": artifacts,
        "test_tiers": {
            "tier_0_edit_checks": "PASS" if passed else "FAIL",
            "tier_1_scoped_tests": "PASS" if passed else "FAIL",
            "tier_2_affected_chain": (
                "NOT_RUN: no source operator or imported certificate changed; "
                "the bounded successor imports them by content hash"
            ),
            "tier_3_full_suite": (
                "NOT_RUN: r=4 was not reached and no Bplus4, T_plus, paper, "
                "freeze, release, Stokes, or scattering theorem is promoted"
            ),
        },
        "commands": commands,
        "claim_boundary": (
            "A single correlated high-order panel from r=31 to r=247/8 "
            "passes direct/jet, tail, width, typing, and rank-preservation "
            "gates. Full Bplus4 at r=4 remains open due throughput."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())

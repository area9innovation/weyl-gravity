#!/usr/bin/env python3
"""Run scoped delivery checks and write the deterministic receipt."""
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
    "axial_partial_jet_outgoing_joint_frame_r31_v1"
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
        "output_tail": completed.stdout[-1000:],
    }


def main() -> int:
    commands = [
        run(["python3", "-m", f"{MODULE}.produce", "--check"]),
        run(["python3", "-m", f"{MODULE}.verify"]),
        run(["python3", "-m", "unittest", f"{MODULE}.test_joint_frame"]),
        run(
            [
                "python3",
                "-m",
                "py_compile",
                str(HERE / "produce.py"),
                str(HERE / "verify.py"),
                str(HERE / "test_joint_frame.py"),
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
    artifacts = {}
    for name in (
        "README.md",
        "__init__.py",
        "audit.py",
        "certificate.json",
        "produce.py",
        "report.md",
        "schema.json",
        "test_joint_frame.py",
        "verify.py",
    ):
        path = HERE / name
        artifacts[name] = sha256(path)
    receipt = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-joint-frame-r31-receipt-v1"
        ),
        "status": "PASS" if passed else "FAIL",
        "certificate": str((HERE / "certificate.json").relative_to(ROOT)),
        "certificate_sha256": sha256(HERE / "certificate.json"),
        "artifacts": artifacts,
        "test_tiers": {
            "tier_0_edit_checks": "PASS" if passed else "FAIL",
            "tier_1_scoped_tests": "PASS" if passed else "FAIL",
            "tier_2_affected_chain": (
                "NOT_RUN: imported content-addressed certificates and "
                "checkpoints were not changed"
            ),
            "tier_3_full_suite": (
                "NOT_RUN: no freeze, release, shared-core algebra change, "
                "or theorem promotion"
            ),
        },
        "commands": commands,
        "claim_boundary": (
            "A typed reduced E/R/S frame has complex rank three at r=31 "
            "on the first pilot child. Analytic K_plus, common amplitude "
            "normalization, T_plus, scattering, and flux remain open."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())

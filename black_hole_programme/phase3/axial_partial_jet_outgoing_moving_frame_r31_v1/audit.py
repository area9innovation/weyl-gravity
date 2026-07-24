#!/usr/bin/env python3
"""Run scoped checks and emit the moving-frame receipt."""
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
    "axial_partial_jet_outgoing_moving_frame_r31_v1"
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
        run(["python3", "-m", "unittest", f"{MODULE}.test_moving_frame"]),
        run(
            [
                "python3",
                "-m",
                "py_compile",
                str(HERE / "model_ops.py"),
                str(HERE / "produce.py"),
                str(HERE / "verify.py"),
                str(HERE / "test_moving_frame.py"),
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
    passed = all(command["exit_code"] == 0 for command in commands)
    artifact_names = (
        "README.md",
        "__init__.py",
        "audit.py",
        "certificate.json",
        "checkpoint.json",
        "model_ops.py",
        "produce.py",
        "report.md",
        "restart_manifest.json",
        "schema.json",
        "test_moving_frame.py",
        "verify.py",
    )
    artifacts = {
        name: sha256(HERE / name)
        for name in artifact_names
        if (HERE / name).exists()
    }
    receipt = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-moving-frame-r31-"
            "receipt-v1"
        ),
        "status": "PASS" if passed else "FAIL",
        "certificate": str((HERE / "certificate.json").relative_to(ROOT)),
        "certificate_sha256": sha256(HERE / "certificate.json"),
        "artifacts": artifacts,
        "test_tiers": {
            "tier_0_edit_checks": "PASS" if passed else "FAIL",
            "tier_1_scoped_tests": "PASS" if passed else "FAIL",
            "tier_2_affected_chain": (
                "NOT_RUN: source checkpoints and exact algebra certificates "
                "are imported by content hash and were not changed"
            ),
            "tier_3_full_suite": (
                "NOT_RUN: no freeze, release, shared-core algebra change, "
                "paper theorem edit, T_plus assembly, or Stokes promotion"
            ),
        },
        "commands": commands,
        "claim_boundary": (
            "At r=31 on the first pilot child, the R/E/S checkpoint is "
            "reissued in one typed analytic moving gauge with exact "
            "componentwise tangent correction, shared Taylor generator, "
            "rank three, restart serialization, and analytic first-jet "
            "K_plus=0. T_plus and Stokes are not established."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())

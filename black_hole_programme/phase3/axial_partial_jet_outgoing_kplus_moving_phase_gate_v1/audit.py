#!/usr/bin/env python3
"""Run scoped checks and write the moving-phase gate receipt."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODULE = (
    "black_hole_programme.phase3."
    "axial_partial_jet_outgoing_kplus_moving_phase_gate_v1"
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
        run(["python3", "-m", "unittest", f"{MODULE}.test_moving_phase_gate"]),
        run(
            [
                "python3",
                "-m",
                "py_compile",
                str(HERE / "algebra.py"),
                str(HERE / "produce.py"),
                str(HERE / "verify.py"),
                str(HERE / "test_moving_phase_gate.py"),
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
        "algebra.py",
        "audit.py",
        "certificate.json",
        "produce.py",
        "report.md",
        "schema.json",
        "test_moving_phase_gate.py",
        "verify.py",
    ):
        artifacts[name] = sha256(HERE / name)
    receipt = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-kplus-moving-phase-gate-"
            "receipt-v1"
        ),
        "status": "PASS" if passed else "FAIL",
        "certificate": str((HERE / "certificate.json").relative_to(ROOT)),
        "certificate_sha256": sha256(HERE / "certificate.json"),
        "artifacts": artifacts,
        "commands": commands,
        "test_tiers": {
            "tier_0_edit_checks": "PASS" if passed else "FAIL",
            "tier_1_scoped_tests": "PASS" if passed else "FAIL",
            "tier_2_affected_chain": (
                "NOT_RUN: no imported mathematical input changed"
            ),
            "tier_3_full_suite": (
                "NOT_RUN: fail-closed gate result; no theorem promotion, "
                "freeze, release, or shared-core change"
            ),
        },
        "claim_boundary": (
            "The outgoing intrinsic rate derivative is exactly -3/4 and "
            "forces a 93/4 relative normalizer derivative at r=31. Formal "
            "K_plus=0 is preserved; analytic K_plus, T_plus, Stokes, "
            "scattering, and flux remain unestablished."
        ),
    }
    (HERE / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(receipt["status"])
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())

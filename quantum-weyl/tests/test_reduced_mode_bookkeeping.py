#!/usr/bin/env python3
"""Regression test for the deterministic reduced-mode receipt."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "quantum-weyl" / "spectral" / "reduced_modes" / "bookkeeping.py"
VALIDATOR = ROOT / "quantum-weyl" / "schema" / "validate_result.py"
RESULT = ROOT / "quantum-weyl" / "certificates" / "REDUCED_MODE_SPECTRAL_BOOTSTRAP.json"


def main() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    expected = "REDUCED-MODE SPECTRAL BOOTSTRAP: ALL EXACT GUARDS PASS"
    if expected not in completed.stdout:
        raise AssertionError(f"missing success guard: {completed.stdout}")
    validation = subprocess.run(
        [sys.executable, str(VALIDATOR), str(RESULT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if validation.returncode != 0:
        raise AssertionError(validation.stdout + validation.stderr)
    print(expected)


if __name__ == "__main__":
    main()

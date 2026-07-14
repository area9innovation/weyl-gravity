#!/usr/bin/env python3
"""One-command energy-mode analytic-completion battery."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
JOBS = (
    ("verify_conformal_energy_mode_krein.py", "CONFORMAL ENERGY-MODE KREIN FOUNDATION: ALL PASS"),
    ("verify_conformal_completed_residual.py", "CONFORMAL COMPLETED RESIDUAL BRST: ALL PASS"),
)
GUARDS = (
    ("verify_conformal_energy_mode_krein.py", "--claim-pontryagin"),
    ("verify_conformal_energy_mode_krein.py", "--claim-positive-graviton-hilbert"),
    ("verify_conformal_energy_mode_krein.py", "--claim-bounded-generators"),
    ("verify_conformal_energy_mode_krein.py", "--claim-formal-adjoint-domains"),
    ("verify_conformal_energy_mode_krein.py", "--claim-group-representation"),
    ("verify_conformal_energy_mode_krein.py", "--claim-covariant-sobolev"),
    ("verify_conformal_completed_residual.py", "--claim-bounded-q"),
    ("verify_conformal_completed_residual.py", "--claim-global-ghost-krein"),
    ("verify_conformal_completed_residual.py", "--treat-d-as-physical-hamiltonian"),
    ("verify_conformal_completed_residual.py", "--claim-green-hyperbolic"),
    ("verify_conformal_completed_residual.py", "--claim-hadamard"),
    ("verify_conformal_completed_residual.py", "--claim-quantum-unitarity"),
)


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "symbolic" / script), *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    for script, marker in JOBS:
        result = _run(script, *(('--emit',) if args.emit else ()))
        if result.returncode or marker not in result.stdout:
            print(result.stdout)
            raise SystemExit(f"failed: {script}")
        print(marker)
    if args.guards:
        for script, flag in GUARDS:
            result = _run(script, flag)
            if result.returncode != 1 or "REFUSED:" not in result.stdout:
                print(result.stdout)
                raise SystemExit(
                    f"guard did not produce the expected refusal: {script} {flag} "
                    f"(exit={result.returncode})"
                )
        print(f"ANALYTIC COMPLETION OVERCLAIM GUARDS: {len(GUARDS)}/{len(GUARDS)} PASS")
    print("CONFORMAL ANALYTIC COMPLETION BATTERY: ALL PASS")


if __name__ == "__main__":
    main()

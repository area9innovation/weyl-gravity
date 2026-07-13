#!/usr/bin/env python3
"""Run the complete machine-verification suite supporting Paper VI.

The default run includes the slower G15 shifted-pole regression.  Use
``--quick`` for the theorem-critical exact checks only; G17 independently
recomputes the real-shell four-point certificate used by the obstruction
theorem.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

import sympy


HERE = Path(__file__).resolve().parent
CORE = [
    "verify_gravity_completion.py",
    "verify_gravity_cubic.py",
    "verify_gravity_factorization.py",
]
SLOW = ["verify_gravity_g15.py"]
FINAL = [
    "verify_gravity_obstruction.py",
    "verify_gravity_krein.py",
]


def run_script(name: str) -> None:
    print(f"\n{'=' * 72}\n{name}\n{'=' * 72}", flush=True)
    process = subprocess.Popen(
        [sys.executable, str(HERE / name)],
        cwd=HERE.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    output = []
    for line in process.stdout:
        print(line, end="", flush=True)
        output.append(line)
    return_code = process.wait()
    joined = "".join(output)
    if return_code != 0 or "ALL PASS" not in joined:
        raise SystemExit(
            f"{name} failed: exit={return_code}, ALL PASS marker="
            f"{'present' if 'ALL PASS' in joined else 'absent'}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quick",
        action="store_true",
        help="skip the slower G15 pole-regression script",
    )
    args = parser.parse_args()

    print(f"Python {sys.version.split()[0]}")
    print(f"SymPy {sympy.__version__}")
    scripts = CORE + ([] if args.quick else SLOW) + FINAL
    for script in scripts:
        run_script(script)
    print("\nPAPER VI GRAVITY SUITE: ALL PASS")


if __name__ == "__main__":
    main()

from __future__ import annotations

import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def test_producer_replay() -> None:
    run("python3", str(HERE / "produce.py"), "--check")


def test_independent_verifier() -> None:
    run("python3", str(HERE / "verify.py"))


def test_mutation_rail() -> None:
    run("python3", str(HERE / "verify.py"), "--self-test-mutation")

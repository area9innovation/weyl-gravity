#!/usr/bin/env python3
"""Emit or check the fail-closed Berger Hadamard construction gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .berger_hadamard_construction_gate import evaluate_gate


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates/BERGER_HADAMARD_CONSTRUCTION_GATE.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate_gate()
    paths = (
        "berger_hadamard_construction_gate.py",
        "berger_hadamard_construction_gate_certificate.py",
        "schema/berger-hadamard-construction-gate-v1.schema.json",
        "tests/test_berger_hadamard_construction_gate.py",
        "../reports/berger-hadamard-construction-gate.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    result["provenance"]["source_manifest"] = manifest
    result["provenance"]["source_manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale Berger Hadamard construction gate: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER HADAMARD GATE: CAUSAL COMMUTATOR READY, TWO-POINT KERNEL OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

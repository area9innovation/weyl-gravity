#!/usr/bin/env python3
"""Emit or check the Berger companion Hadamard existence audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .berger_companion_hadamard_existence_audit import evaluate, validate


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate()
    paths = (
        "berger_companion_hadamard_existence_audit.py",
        "berger_companion_hadamard_existence_audit_certificate.py",
        "verify_berger_companion_hadamard_existence_audit.py",
        "schema/berger-companion-hadamard-existence-audit-v1.schema.json",
        "tests/test_berger_companion_hadamard_existence_audit.py",
        "README.md",
        "../reports/berger-companion-hadamard-existence-audit.md",
    )
    manifest = {path: _sha256(HERE / path) for path in paths}
    result["provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    validate(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale Hadamard existence audit: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER COMPANION HADAMARD EXISTENCE AUDIT: PASS, STATE OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

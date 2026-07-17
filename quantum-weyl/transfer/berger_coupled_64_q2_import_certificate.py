#!/usr/bin/env python3
"""Emit or check the pinned coupled 64-row Berger q2 replay certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .berger_coupled_64_q2_import import build_payload
except ImportError:
    from berger_coupled_64_q2_import import build_payload


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/BERGER_COUPLED_64_Q2_IMPORT_REPLAY.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict:
    result = dict(build_payload())
    paths = (
        "berger_coupled_64_q2_import.py",
        "berger_coupled_64_q2_import_certificate.py",
        "verify_berger_coupled_64_q2_import.py",
        "schema/berger-coupled-64-q2-import-v1.schema.json",
        "tests/test_berger_coupled_64_q2_import.py",
        "../reports/berger-coupled-64-q2-import-replay.md",
        "README.md",
    )
    manifest = {path: _sha256(HERE / path) for path in paths}
    result["consumer_provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": _canonical_hash(manifest),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"stale coupled 64-row q2 replay: {OUTPUT}")
    print(
        "BERGER COUPLED 64-ROW Q2: STRUCTURAL/K REPLAY COMPLETE; "
        "Q1Q2, CYCLICITY, TRANSFER BLOCKED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

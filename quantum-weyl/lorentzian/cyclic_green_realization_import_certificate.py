#!/usr/bin/env python3
"""Emit/check the cyclic Berger Green-realization import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .cyclic_green_realization_import import build_import


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates/BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION_IMPORT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = build_import()
    paths = (
        "cyclic_green_realization_import.py",
        "cyclic_green_realization_import_certificate.py",
        "schema/berger-cyclic-green-realization-import-v1.schema.json",
        "tests/test_cyclic_green_realization_import.py",
        "../reports/berger-cyclic-green-realization-import.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    result["provenance"]["source_manifest"] = manifest
    result["provenance"]["source_manifest_sha256"] = _canonical_hash(manifest)
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
        raise SystemExit(f"stale cyclic Green realization import: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER CYCLIC ANALYTIC REALIZATION: IMPORTED; GREEN OPERATORS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

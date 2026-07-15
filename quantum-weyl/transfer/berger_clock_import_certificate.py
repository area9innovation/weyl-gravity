#!/usr/bin/env python3
"""Emit or check the nonlinear import of the Berger clock candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TRANSFER_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "BERGER_CLOCK_NONLINEAR_IMPORT.json"

try:
    from .berger_clock_import import build_import
except ImportError:
    from berger_clock_import import build_import


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "berger_clock_import.py",
        "berger_clock_import_certificate.py",
        "schema/berger-clock-nonlinear-import-v1.schema.json",
        "tests/test_berger_clock_import.py",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    certificate = build_import()
    source_manifest = _source_manifest()
    certificate["provenance"]["source_manifest"] = source_manifest
    certificate["provenance"]["source_manifest_sha256"] = _canonical_hash(source_manifest)
    certificate["provenance"]["schema"] = (
        "quantum-weyl/transfer/schema/berger-clock-nonlinear-import-v1.schema.json"
    )
    return certificate


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content):
        raise SystemExit(f"Berger nonlinear import certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER CLOCK: HEALTHY BACKGROUND AND REDUCED MOMENTUM IMPORTED, TOTAL D OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

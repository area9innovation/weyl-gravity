#!/usr/bin/env python3
"""Emit the pinned clock-reattached principal import certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .clock_reattached_principal_import import build_import


LORENTZIAN_ROOT = Path(__file__).resolve().parent
OUTPUT = LORENTZIAN_ROOT / "certificates" / "BERGER_CLOCK_REATTACHED_PRINCIPAL_INPUT_IMPORT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, Any]:
    payload = build_import()
    paths = (
        "clock_reattached_principal_import.py",
        "clock_reattached_principal_import_certificate.py",
        "schema/berger-clock-reattached-principal-import-v1.schema.json",
        "tests/test_clock_reattached_principal_import.py",
        "../reports/berger-clock-reattached-principal-import.md",
    )
    manifest = {path: _sha256(LORENTZIAN_ROOT / path) for path in paths}
    return {
        **payload,
        "consumer_provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content):
        raise SystemExit(f"stale clock-reattached principal import: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER CLOCK-REATTACHED PRINCIPAL WITNESS IMPORTED; CURVED ORDERS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

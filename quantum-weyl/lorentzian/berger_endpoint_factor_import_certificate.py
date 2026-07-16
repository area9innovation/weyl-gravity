#!/usr/bin/env python3
"""Emit the pinned Berger partial causal-endpoint import certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .berger_endpoint_factor_import import build_import
except ImportError:
    from berger_endpoint_factor_import import build_import


LORENTZIAN_ROOT = Path(__file__).resolve().parent
OUTPUT = LORENTZIAN_ROOT / "certificates" / "BERGER_ENDPOINT_FACTOR_INPUT_IMPORT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, Any]:
    payload = build_import()
    paths = (
        "berger_endpoint_factor_import.py",
        "berger_endpoint_factor_import_certificate.py",
        "schema/berger-endpoint-factor-import-v1.schema.json",
        "tests/test_berger_endpoint_factor_import.py",
        "README.md",
        "../reports/berger-endpoint-factor-import.md",
    )
    manifest = {path: _sha256(LORENTZIAN_ROOT / path) for path in paths}
    return {
        **payload,
        "consumer_provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
        },
    }


def _render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content):
        raise SystemExit(f"Berger endpoint-factor import certificate is stale: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER ENDPOINT FACTORS IMPORTED; METRIC GREEN REALIZATION OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit the Berger curved-witness adapter readiness certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .curved_witness_adapter import build_readiness_receipt


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates" / "BERGER_CURVED_CLOCK_REATTACHED_WITNESS_ADAPTER.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, object]:
    payload = build_readiness_receipt()
    paths = (
        "curved_witness_adapter.py",
        "curved_witness_adapter_certificate.py",
        "schema/berger-curved-witness-adapter-v1.schema.json",
        "schema/berger-curved-witness-export-v1.schema.json",
        "tests/test_curved_witness_adapter.py",
        "../reports/berger-curved-witness-adapter.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
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
        raise SystemExit(f"stale curved-witness adapter certificate: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER CURVED-WITNESS ADAPTER READY; AUTHORITATIVE W34 INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

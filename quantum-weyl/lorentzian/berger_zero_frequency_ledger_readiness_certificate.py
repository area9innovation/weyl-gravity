#!/usr/bin/env python3
"""Emit or check the retained zero-frequency ledger readiness theorem."""

from __future__ import annotations

import argparse
import hashlib
import json

from .berger_zero_frequency_ledger_readiness import HERE, build


OUTPUT = HERE / "certificates/BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS.json"


def _hash(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    result = build()
    paths = (
        "berger_zero_frequency_ledger_readiness.py",
        "berger_zero_frequency_ledger_readiness_certificate.py",
        "verify_berger_zero_frequency_ledger_readiness.py",
        "schema/berger-zero-frequency-ledger-readiness-v1.schema.json",
        "tests/test_berger_zero_frequency_ledger_readiness.py",
        "../reports/berger-zero-frequency-ledger-readiness.md",
    )
    manifest = {path: _hash(HERE / path) for path in paths}
    result["provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
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
        OUTPUT.write_text(content)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale zero-frequency readiness theorem: {OUTPUT}")
    print("BERGER ZERO FREQUENCY: CURRENT INPUT NONIDENTIFIABLE; FULL STATIONARY CARRIER REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

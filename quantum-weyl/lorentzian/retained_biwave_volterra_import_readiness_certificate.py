#!/usr/bin/env python3
"""Emit or check the retained Berger Volterra import-readiness certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .retained_biwave_volterra_import_readiness import evaluate_readiness


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_IMPORT_READINESS.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate_readiness()
    paths = (
        "retained_biwave_volterra_import_readiness.py",
        "retained_biwave_volterra_import_readiness_certificate.py",
        "schema/berger-retained-biwave-volterra-import-readiness-v1.schema.json",
        "tests/test_retained_biwave_volterra_import_readiness.py",
        "../reports/berger-retained-biwave-volterra-import-readiness.md",
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
        raise SystemExit(f"stale retained Volterra import readiness: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER RETAINED VOLTERRA: SOURCE PINNED; ANALYTIC CONTRACT REJECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

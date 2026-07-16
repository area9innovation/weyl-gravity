#!/usr/bin/env python3
"""Emit or check the pinned lower-by-two Berger metric import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .metric_lower_by_two_biwave_import import build_import, fast_receipt, replay_receipt


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, object]:
    result = build_import()
    paths = (
        "metric_lower_by_two_biwave_import.py",
        "metric_lower_by_two_biwave_import_certificate.py",
        "schema/berger-metric-lower-by-two-biwave-import-v1.schema.json",
        "tests/test_metric_lower_by_two_biwave_import.py",
        "../reports/berger-metric-lower-by-two-biwave-import.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    result["provenance"]["source_manifest"] = manifest
    result["provenance"]["source_manifest_sha256"] = _canonical_hash(manifest)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--replay-check", action="store_true")
    args = parser.parse_args()
    if args.fast_check:
        fast_receipt()
    if args.replay_check:
        replay_receipt()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale lower-by-two metric import: {OUTPUT}")
    if not any((args.emit, args.check, args.fast_check, args.replay_check)):
        print(content, end="")
    else:
        print("BERGER METRIC LOWER-BY-TWO BIWAVE: IMPORTED; CAUSAL RESOLVENT OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

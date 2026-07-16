#!/usr/bin/env python3
"""Emit or check the fail-closed Berger 54-row q2 arrival readiness receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .berger_54_row_q2_arrival import build_readiness_payload
except ImportError:
    from berger_54_row_q2_arrival import build_readiness_payload


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates" / "BERGER_54_ROW_Q2_ARRIVAL_READINESS.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, Any]:
    result = build_readiness_payload()
    paths = (
        "berger_54_row_q2_arrival.py",
        "berger_54_row_q2_arrival_certificate.py",
        "schema/berger-54-row-support-local-q2-portable-v1.schema.json",
        "schema/berger-54-row-q2-arrival-readiness-v1.schema.json",
        "tests/test_berger_54_row_q2_arrival.py",
        "../reports/berger-54-row-q2-arrival-readiness.md",
        "README.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
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
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"stale Berger q2 arrival readiness certificate: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER 54-ROW Q2 ARRIVAL ADAPTER: READY; CLASSICAL Q2 INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

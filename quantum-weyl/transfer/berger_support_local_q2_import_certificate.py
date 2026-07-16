#!/usr/bin/env python3
"""Emit or check the pinned complete Berger support-local q2 import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .berger_support_local_q2_import import build_import_payload
except ImportError:
    from berger_support_local_q2_import import build_import_payload


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates" / "BERGER_SUPPORT_LOCAL_Q2_IMPORT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, Any]:
    result = dict(build_import_payload())
    paths = (
        "berger_support_local_q2_import.py",
        "berger_support_local_q2_import_certificate.py",
        "berger_54_row_q2_arrival.py",
        "berger_54_row_local_d_import.py",
        "berger_gauge_fixed_nonminimal_import.py",
        "schema/berger-support-local-q2-import-v1.schema.json",
        "tests/test_berger_support_local_q2_import.py",
        "../reports/berger-support-local-q2-import.md",
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
        raise SystemExit(f"stale Berger support-local q2 import: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER SUPPORT-LOCAL Q2: IMPORTED; SCIENTIFIC REPLAY PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit or check the complete Berger 54-row local-D import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .berger_54_row_local_d_import import build_import
except ImportError:
    from berger_54_row_local_d_import import build_import


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates" / "BERGER_54_ROW_LOCAL_D_IMPORT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, object]:
    result = build_import()
    paths = (
        "berger_54_row_local_d_import.py",
        "berger_54_row_local_d_import_certificate.py",
        "schema/berger-54-row-local-d-import-v1.schema.json",
        "tests/test_berger_54_row_local_d_import.py",
        "../reports/berger-54-row-local-d-import.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    result["provenance"]["source_manifest"] = manifest
    result["provenance"]["source_manifest_sha256"] = _canonical_hash(manifest)
    result["provenance"]["schema"] = (
        "quantum-weyl/transfer/schema/berger-54-row-local-d-import-v1.schema.json"
    )
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
        raise SystemExit(f"stale import certificate: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER 54-ROW LOCAL D IMPORT: COMPLETE; SUPPORT-LOCAL Q2 BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

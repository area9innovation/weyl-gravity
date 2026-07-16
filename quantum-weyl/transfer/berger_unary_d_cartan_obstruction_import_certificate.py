#!/usr/bin/env python3
"""Emit the pinned Berger unary D-Cartan microlocal obstruction import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .berger_unary_d_cartan_obstruction_import import build_import


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates/BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION_IMPORT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, object]:
    result = build_import()
    paths = (
        "berger_unary_d_cartan_obstruction_import.py",
        "berger_unary_d_cartan_obstruction_import_certificate.py",
        "schema/berger-unary-d-cartan-obstruction-import-v1.schema.json",
        "tests/test_berger_unary_d_cartan_obstruction_import.py",
        "../reports/berger-unary-d-cartan-obstruction-import.md",
        "README.md",
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
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"stale unary D-Cartan obstruction import: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER BARE 26/54-ROW LOCAL UNARY D-CARTAN: EXACTLY OBSTRUCTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

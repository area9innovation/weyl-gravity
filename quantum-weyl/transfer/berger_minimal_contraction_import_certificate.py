#!/usr/bin/env python3
"""Emit or check the complete minimal Berger contraction import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .berger_minimal_contraction_import import build_import
except ImportError:
    from berger_minimal_contraction_import import build_import


TRANSFER_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_MINIMAL_34_CONTRACTION_IMPORT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source_manifest() -> dict[str, str]:
    paths = (
        "berger_retained_q1_import.py",
        "berger_minimal_contraction_import.py",
        "berger_minimal_contraction_import_certificate.py",
        "schema/berger-minimal-34-contraction-import-v1.schema.json",
        "tests/test_berger_minimal_contraction_import.py",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    certificate = build_import()
    manifest = _source_manifest()
    certificate["provenance"]["source_manifest"] = manifest
    certificate["provenance"]["source_manifest_sha256"] = _canonical_hash(manifest)
    certificate["provenance"]["schema"] = (
        "quantum-weyl/transfer/schema/"
        "berger-minimal-34-contraction-import-v1.schema.json"
    )
    return certificate


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and (
        not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content
    ):
        raise SystemExit(f"Berger minimal contraction import is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER MINIMAL CONTRACTION: 34 ROWS IMPORTED, NONLINEAR INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

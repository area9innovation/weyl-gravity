#!/usr/bin/env python3
"""Emit the pinned restricted support-local pp-wave transfer verdict."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .ppwave_branch_transfer_import import build_import
except ImportError:
    from ppwave_branch_transfer_import import build_import


TRANSFER_ROOT = Path(__file__).resolve().parent
OUTPUT = TRANSFER_ROOT / "certificates" / "PPWAVE_BRANCH_TRANSFERRED_ELL2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_certificate() -> dict[str, Any]:
    payload = build_import()
    paths = (
        "ppwave_branch_transfer_import.py",
        "ppwave_branch_transfer_import_certificate.py",
        "schema/ppwave-branch-transfer-import-v1.schema.json",
        "tests/test_ppwave_branch_transfer_import.py",
        "../reports/ppwave-branch-transfer.md",
    )
    manifest = {path: _sha256(TRANSFER_ROOT / path) for path in paths}
    payload["consumer_provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": _canonical_hash(manifest),
    }
    return payload


def _render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content):
        raise SystemExit(f"pp-wave transfer certificate is stale: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("PPWAVE BRANCH TRANSFER: RESTRICTED SUPPORT-LOCAL ELL2 EXACTLY ZERO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

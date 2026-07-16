#!/usr/bin/env python3
"""Emit or check the pinned axial Weyl--Maxwell quantum import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .einstein_maxwell_weyl_axial_import import build_import
except ImportError:
    from einstein_maxwell_weyl_axial_import import build_import


TRANSFER_ROOT = Path(__file__).resolve().parent
OUTPUT = TRANSFER_ROOT / "certificates" / "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_MODULE_IMPORT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, Any]:
    payload = build_import()
    paths = (
        "einstein_maxwell_weyl_axial_import.py",
        "einstein_maxwell_weyl_axial_import_certificate.py",
        "verify_einstein_maxwell_weyl_axial_import.py",
        "schema/einstein-maxwell-weyl-axial-import-v1.schema.json",
        "tests/test_einstein_maxwell_weyl_axial_import.py",
        "../reports/einstein-maxwell-weyl-axial-import.md",
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
        raise SystemExit(f"axial Weyl--Maxwell import certificate is stale: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("AXIAL WEYL--MAXWELL IMPORT: DIRECT LEE--WALD SIGNATURE (3,1); MIXED/CAUSAL/QUANTUM GATES OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit or check the pinned Berger reduced-mode ND2 import certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .berger_rational_fixture_q2_d_import import build_import
except ImportError:
    from berger_rational_fixture_q2_d_import import build_import


TRANSFER_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "BERGER_RATIONAL_FIXTURE_Q2_D_IMPORT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_certificate() -> dict[str, Any]:
    payload = build_import()
    paths = (
        "arity_two_cartan.py",
        "berger_rational_fixture_q2_d_import.py",
        "berger_rational_fixture_q2_d_import_certificate.py",
        "schema/berger-rational-fixture-q2-d-import-v1.schema.json",
        "tests/test_berger_rational_fixture_q2_d_import.py",
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
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content):
        raise SystemExit(f"Berger reduced-mode ND2 import is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("ND2_REDUCED_MODE_FIXTURE_IMPORT: PASS (PHYSICAL EXECUTION BLOCKED)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit or check the renormalized D-Ward insertion contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .ward_insertion_contract import build_contract_receipt


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates" / "RENORMALIZED_D_WARD_INSERTION_CONTRACT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, object]:
    payload = build_contract_receipt()
    paths = (
        "defect_complex.py",
        "ward_insertion_contract.py",
        "ward_insertion_contract_certificate.py",
        "schema/renormalized-D-ward-insertion-export-v1.schema.json",
        "schema/renormalized-D-ward-insertion-contract-v1.schema.json",
        "tests/test_defect_complex.py",
        "tests/test_ward_insertion_contract.py",
        "../reports/renormalized-D-ward-insertion-contract.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    return {
        **payload,
        "provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
            "export_schema": "quantum-weyl/cartan/schema/renormalized-D-ward-insertion-export-v1.schema.json",
            "certificate_schema": "quantum-weyl/cartan/schema/renormalized-D-ward-insertion-contract-v1.schema.json",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content):
        raise SystemExit(f"stale Ward insertion contract: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("RENORMALIZED D-WARD INSERTION CONTRACT: READY; PHYSICAL INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit or check the Berger 26-row Green/Hadamard endpoint contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .green_endpoint_contract import build_contract_receipt
except ImportError:
    from green_endpoint_contract import build_contract_receipt


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates" / "BERGER_26_ROW_GREEN_HADAMARD_ENDPOINT_CONTRACT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, object]:
    payload = build_contract_receipt()
    paths = (
        "__init__.py",
        "green_endpoint_contract.py",
        "green_endpoint_contract_certificate.py",
        "schema/berger-26-row-green-endpoint-export-v1.schema.json",
        "schema/berger-26-row-green-endpoint-contract-v1.schema.json",
        "tests/test_green_endpoint_contract.py",
        "../reports/berger-26-row-green-hadamard-endpoint-contract.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    return {
        **payload,
        "provenance": {
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
            "export_schema": "quantum-weyl/lorentzian/schema/berger-26-row-green-endpoint-export-v1.schema.json",
            "certificate_schema": "quantum-weyl/lorentzian/schema/berger-26-row-green-endpoint-contract-v1.schema.json",
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
        raise SystemExit(f"stale Green/Hadamard endpoint contract: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER 26-ROW GREEN CONTRACT: FACTORS AND CLOCK PRINCIPAL RECEIVED; CURVED OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

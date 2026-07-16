#!/usr/bin/env python3
"""Emit or check the repaired Berger causal-chain v2 import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .berger_causal_chain_v2_import import evaluate_import


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate_import()
    paths = (
        "berger_causal_chain_v2_import.py",
        "berger_causal_chain_v2_import_certificate.py",
        "schema/berger-causal-chain-v2-import-v1.schema.json",
        "tests/test_berger_causal_chain_v2_import.py",
        "../reports/berger-causal-chain-v2-import.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    result["provenance"]["source_manifest"] = manifest
    result["provenance"]["source_manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale Berger causal-chain v2 import: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER CAUSAL CHAIN V2: IMPORTED THROUGH D-CARTAN ARITY TWO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

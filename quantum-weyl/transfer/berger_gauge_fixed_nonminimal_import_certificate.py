#!/usr/bin/env python3
"""Emit or check the gauge-fixed Berger classical-unary import."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .berger_gauge_fixed_nonminimal_import import build_import
except ImportError:
    from berger_gauge_fixed_nonminimal_import import build_import


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates/BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = build_import()
    paths = (
        "berger_gauge_fixed_nonminimal_import.py",
        "berger_gauge_fixed_nonminimal_import_certificate.py",
        "schema/berger-gauge-fixed-nonminimal-import-v1.schema.json",
        "tests/test_berger_gauge_fixed_nonminimal_import.py",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    result["provenance"]["source_manifest"] = manifest
    result["provenance"]["source_manifest_sha256"] = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result["provenance"]["schema"] = "quantum-weyl/transfer/schema/berger-gauge-fixed-nonminimal-import-v1.schema.json"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale import certificate: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER GAUGE-FIXED NONMINIMAL IMPORT: UNARY COMPLETE, NONLINEAR BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

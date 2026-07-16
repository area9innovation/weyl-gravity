#!/usr/bin/env python3
"""Emit or check the retained Berger biwave companion preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .retained_biwave_companion_preflight import evaluate_preflight


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate_preflight()
    paths = (
        "retained_biwave_companion_preflight.py",
        "retained_biwave_companion_preflight_certificate.py",
        "schema/berger-retained-biwave-companion-preflight-v1.schema.json",
        "tests/test_retained_biwave_companion_preflight.py",
        "../reports/berger-retained-biwave-companion-preflight.md",
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
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale retained-biwave companion preflight: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER RETAINED BIWAVE COMPANION: EXACT; VOLTERRA RESOLVENT OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

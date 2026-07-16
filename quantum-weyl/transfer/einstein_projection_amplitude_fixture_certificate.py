#!/usr/bin/env python3
"""Emit or check the fail-closed Einstein-projection MHV fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .einstein_projection_amplitude_fixture import build_certificate_payload
except ImportError:
    from einstein_projection_amplitude_fixture import build_certificate_payload


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "certificates" / "EINSTEIN_PROJECTION_MHV_FIXTURE.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build_certificate() -> dict[str, Any]:
    result = build_certificate_payload()
    paths = (
        "einstein_projection_amplitude_fixture.py",
        "einstein_projection_amplitude_fixture_certificate.py",
        "schema/einstein-projection-amplitude-fixture-v1.schema.json",
        "tests/test_einstein_projection_amplitude_fixture.py",
        "../reports/einstein-projection-amplitude-fixture.md",
    )
    manifest = {path: _hash(ROOT / path) for path in paths}
    result["consumer_provenance"] = {
        "source_manifest": manifest,
        "source_manifest_sha256": _canonical_hash(manifest),
    }
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
        raise SystemExit(f"stale Einstein-projection fixture: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print(
            "EINSTEIN HELICITY PARITY PAIR: EXACT; "
            "SETTING/DEFECT/NORMALIZATION GATES READY; Q2 BLOCKED"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

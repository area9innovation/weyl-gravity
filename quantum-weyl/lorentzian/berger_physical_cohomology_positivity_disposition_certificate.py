#!/usr/bin/env python3
"""Emit/check the Berger physical-cohomology positivity disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .berger_physical_cohomology_positivity_disposition import evaluate
except ImportError:
    from berger_physical_cohomology_positivity_disposition import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE
    / "certificates/BERGER_PHYSICAL_COHOMOLOGY_POSITIVITY_DISPOSITION.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate().copy()
    paths = (
        "berger_physical_cohomology_positivity_disposition.py",
        "berger_physical_cohomology_positivity_disposition_certificate.py",
        "verify_berger_physical_cohomology_positivity_disposition.py",
        "schema/berger-physical-cohomology-positivity-disposition-v1.schema.json",
        "tests/test_berger_physical_cohomology_positivity_disposition.py",
        "../reports/berger-physical-cohomology-positivity-disposition.md",
    )
    manifest = {path: _sha256(HERE / path) for path in paths}
    result["provenance"] = {
        **result["provenance"],
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(
                manifest, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest(),
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
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale physical positivity certificate: {OUTPUT}")
    print("BERGER PHYSICAL POSITIVITY: UNDEFINED BEFORE Q26 WARD DESCENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit or check the renormalized D-Ward non-definition certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .renormalized_d_ward_insertion_nondefinition import evaluate
except ImportError:
    from renormalized_d_ward_insertion_nondefinition import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE
    / "certificates/RENORMALIZED_D_WARD_INSERTION_NONDEFINITION.json"
)
SOURCE_PATHS = (
    "renormalized_d_ward_insertion_nondefinition.py",
    "renormalized_d_ward_insertion_nondefinition_certificate.py",
    "verify_renormalized_d_ward_insertion_nondefinition.py",
    "schema/renormalized-d-ward-insertion-nondefinition-v1.schema.json",
    "tests/test_renormalized_d_ward_insertion_nondefinition.py",
    "../reports/renormalized-d-ward-insertion-nondefinition.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    value = evaluate()
    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    value["provenance"] = {
        "proof_type": (
            "EXACT_PINNED_BOUNDARY_NONDEFINITION_WITH_INDEPENDENT_REPLAY"
        ),
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(
                manifest, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest(),
    }
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale Ward non-definition certificate: {OUTPUT}")
    print("RENORMALIZED D-WARD INSERTION NONDEFINITION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

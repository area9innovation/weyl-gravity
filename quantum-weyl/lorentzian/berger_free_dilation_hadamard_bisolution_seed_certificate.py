#!/usr/bin/env python3
"""Emit or check the free-dilation Hadamard-bisolution seed certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .berger_free_dilation_hadamard_bisolution_seed import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE / "certificates/BERGER_FREE_DILATION_HADAMARD_BISOLUTION_SEED.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, object]:
    result = evaluate().copy()
    paths = (
        "berger_free_dilation_hadamard_bisolution_seed.py",
        "berger_free_dilation_hadamard_bisolution_seed_certificate.py",
        "verify_berger_free_dilation_hadamard_bisolution_seed.py",
        "schema/berger-free-dilation-hadamard-bisolution-seed-v1.schema.json",
        "tests/test_berger_free_dilation_hadamard_bisolution_seed.py",
        "../reports/berger-free-dilation-hadamard-bisolution-seed.md",
    )
    manifest = {path: _sha256(HERE / path) for path in paths}
    result["provenance"] = {
        **result["provenance"],
        "source_manifest": manifest,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
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
        raise SystemExit(f"stale free-dilation Hadamard seed: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print(
            "BERGER FREE DILATION HADAMARD BISOLUTION SEED: "
            "GLOBAL BISOLUTION PASS; POSITIVE STATE OPEN"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

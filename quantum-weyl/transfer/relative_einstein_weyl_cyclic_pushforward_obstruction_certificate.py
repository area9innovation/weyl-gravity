#!/usr/bin/env python3
"""Emit/check the relative Einstein--Weyl cyclic-pushforward obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .relative_einstein_weyl_cyclic_pushforward_obstruction import (
    evaluate,
    validate,
)


HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE
    / "certificates/RELATIVE_EINSTEIN_WEYL_CYCLIC_PUSHFORWARD_OBSTRUCTION.json"
)
SOURCES = (
    "relative_einstein_weyl_cyclic_pushforward_obstruction.py",
    "relative_einstein_weyl_cyclic_pushforward_obstruction_certificate.py",
    "verify_relative_einstein_weyl_cyclic_pushforward_obstruction.py",
    "schema/relative-einstein-weyl-cyclic-pushforward-obstruction-v1.schema.json",
    "tests/test_relative_einstein_weyl_cyclic_pushforward_obstruction.py",
    "../reports/relative-einstein-weyl-cyclic-pushforward-obstruction.md",
)


def build() -> dict:
    value = evaluate()
    value["provenance"] = {
        "proof_type": (
            "EXACT_ACTION_BV_LAYOUT_AUDIT_AND_GENERIC_COHOMOLOGY_"
            "CONGRUENCE_INERTIA_OBSTRUCTION"
        ),
        "source_manifest": {
            path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
            for path in SOURCES
        },
    }
    validate(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(text, encoding="utf-8")
    if args.check and OUTPUT.read_text(encoding="utf-8") != text:
        raise SystemExit("stale relative cyclic-pushforward obstruction")
    print("RELATIVE EINSTEIN-WEYL CYCLIC PUSHFORWARD OBSTRUCTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

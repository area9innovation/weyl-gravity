#!/usr/bin/env python3
"""Emit/check the homogeneous stationary normalization obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .berger_homogeneous_stationary_hadamard_normalization_obstruction import (
    evaluate,
)

HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE
    / "certificates/"
    "BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_NORMALIZATION_OBSTRUCTION.json"
)
SOURCES = (
    "berger_homogeneous_stationary_hadamard_normalization_obstruction.py",
    "berger_homogeneous_stationary_hadamard_normalization_obstruction_certificate.py",
    "verify_berger_homogeneous_stationary_hadamard_normalization_obstruction.py",
    "schema/berger-homogeneous-stationary-hadamard-normalization-obstruction-v1.schema.json",
    "tests/test_berger_homogeneous_stationary_hadamard_normalization_obstruction.py",
    "../reports/berger-homogeneous-stationary-hadamard-normalization-obstruction.md",
)


def build() -> dict:
    value = evaluate()
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    value["provenance"] = {
        "proof_type": "EXACT_CHARPOLY_IVT_AND_SIMPLE_EIGENLINE_OBSTRUCTION",
        "source_manifest": manifest,
    }
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(text)
    if args.check and OUTPUT.read_text() != text:
        raise SystemExit("stale homogeneous stationary obstruction")
    print("BERGER HOMOGENEOUS STATIONARY NORMALIZATION OBSTRUCTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

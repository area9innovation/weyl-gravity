#!/usr/bin/env python3
"""Emit/check the exact relative pairing-deformation classification."""

from __future__ import annotations

import argparse
import hashlib
import json

from .relative_einstein_weyl_pairing_deformation_classification import (
    HERE,
    build as classify,
    validate,
)


OUTPUT = (
    HERE
    / "certificates/"
    "RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION.json"
)
SOURCES = (
    "relative_einstein_weyl_pairing_deformation_classification.py",
    "relative_einstein_weyl_pairing_deformation_classification_certificate.py",
    "verify_relative_einstein_weyl_pairing_deformation_classification.py",
    "schema/relative-einstein-weyl-pairing-deformation-classification-v1.schema.json",
    "tests/test_relative_einstein_weyl_pairing_deformation_classification.py",
    "../reports/relative-einstein-weyl-pairing-deformation-classification.md",
)


def build() -> dict:
    value = classify()
    value["provenance"] = {
        "proof_type": (
            "EXACT_GENERIC_COHOMOLOGY_INERTIA_WALL_CLASSIFICATION_"
            "WITH_EXPLICIT_CONGRUENCES_AND_TYPED_AUXILIARIES"
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
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text
    ):
        raise SystemExit("stale relative pairing-deformation classification")
    print("RELATIVE EINSTEIN-WEYL PAIRING DEFORMATION CLASSIFICATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit/check the relative Einstein--Weyl QME non-definition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .relative_einstein_weyl_qme_defect_nondefinition import evaluate


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/RELATIVE_EINSTEIN_WEYL_QME_DEFECT_NONDEFINITION.json"
SOURCES = (
    "relative_einstein_weyl_qme_defect_nondefinition.py",
    "relative_einstein_weyl_qme_defect_nondefinition_certificate.py",
    "verify_relative_einstein_weyl_qme_defect_nondefinition.py",
    "schema/relative-einstein-weyl-qme-defect-nondefinition-v1.schema.json",
    "tests/test_relative_einstein_weyl_qme_defect_nondefinition.py",
    "../reports/relative-einstein-weyl-qme-defect-nondefinition.md",
)


def build() -> dict:
    value = evaluate()
    value["provenance"] = {
        "proof_type": (
            "EXACT_PINNED_TRIANGLE_IMPORT_AND_MISSING_CYCLIC_QME_ROW_AUDIT"
        ),
        "source_manifest": {
            path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
            for path in SOURCES
        },
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
        raise SystemExit("stale relative Einstein--Weyl QME non-definition")
    print("RELATIVE EINSTEIN-WEYL QME DEFECT NONDEFINITION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit/check the joint healthy matter/gauge projection obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json

from .matter_gauge_representation_projection_obstruction import (
    HERE,
    build as classify,
    validate,
)


OUTPUT = (
    HERE
    / "certificates/MATTER_GAUGE_REPRESENTATION_JOINT_HEALTHY_EMPTY_BY_PROJECTION.json"
)
SOURCES = (
    "matter_gauge_representation_projection_obstruction.py",
    "matter_gauge_representation_projection_obstruction_certificate.py",
    "verify_matter_gauge_representation_projection_obstruction.py",
    "schema/matter-gauge-representation-projection-obstruction-v1.schema.json",
    "tests/test_matter_gauge_representation_projection_obstruction.py",
    "../reports/matter-gauge-representation-projection-obstruction.md",
)


def build() -> dict:
    value = classify()
    value["provenance"] = {
        "proof_type": (
            "EXACT_FORGETFUL_MAP_COMPOSITION_WITH_POSITIVE_DUAL_SEPARATOR"
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
        raise SystemExit("stale matter/gauge projection obstruction")
    print("MATTER GAUGE REPRESENTATION PROJECTION OBSTRUCTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
